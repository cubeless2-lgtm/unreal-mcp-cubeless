#!/usr/bin/env python
"""
Section 40 Blueprint authoring manifest executor.

This module owns the execution contract for safe temporary Blueprint authoring
manifests. Unreal-specific command calls are still supplied by the live smoke
adapter, but policy checks, command-plan flattening, section orchestration, and
failure result shape live here.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import bp_authoring_durable_canary_live_preflight_contract as durable_canary_live_preflight
import bp_authoring_job_contract as job_contract
import bp_authoring_planner as planner


EXECUTOR_VERSION = "section_40_manifest_executor_v1"
EXECUTOR_POLICY_SCHEMA = "section_40_manifest_executor_policy_v1"
EXECUTOR_RESULT_SCHEMA = "section_40_manifest_executor_result_v1"
FAILURE_DIAGNOSTIC_SCHEMA = "section_41_failure_diagnostics_v2"
CAPABILITY_MATRIX_SCHEMA = "section_42_45_executor_capability_matrix_v1"
DURABLE_GATE_SCHEMA = "section_46_48_durable_executor_gate_v1"
DURABLE_LIVE_PREFLIGHT_SCHEMA = "section_48_durable_preflight_live_gate_v1"

EXECUTION_SECTIONS: Tuple[str, ...] = (
    "component_list",
    "component_default_steps",
    "variables_defaults",
    "event_graph_steps",
    "function_graph_steps",
    "generated_function_invocation_steps",
    "dispatcher_lifecycle_steps",
    "validation_plan",
)

STRUCTURAL_SECTION = "structural_validation_plan"

FORBIDDEN_LIVE_COMMANDS: Tuple[str, ...] = (
    "save_asset",
    "delete_asset",
    "rename_asset",
    "compile_and_save_blueprint",
)

CAPABILITY_KEYS: Tuple[str, ...] = (
    "typed_defaults",
    "graph_layout_dataflow",
    "function_graph_executor",
    "dispatcher_lifecycle_executor",
)


class ManifestExecutorFailure(Exception):
    """Raised when an executable manifest fails policy or step execution."""

    def __init__(
        self,
        diagnostic: Dict[str, Any],
        policy: Optional[Dict[str, Any]] = None,
        partial_result: Optional[Dict[str, Any]] = None,
    ):
        self.diagnostic = diagnostic
        self.policy = policy or {}
        self.partial_result = partial_result or {}
        super().__init__(diagnostic.get("error", diagnostic.get("reason", "Manifest executor failed")))


@dataclass
class ManifestExecutorCallbacks:
    execute_step: Callable[[str, Dict[str, Any], Dict[str, Dict[str, Any]], List[Dict[str, Any]]], Optional[Dict[str, Any]]]
    execute_structural_step: Callable[[Dict[str, Any], Dict[str, Dict[str, Any]]], Dict[str, Any]]
    build_failure_diagnostic: Callable[[str, Dict[str, Any], Dict[str, Dict[str, Any]], Exception, str], Dict[str, Any]]


def is_temp_package_path(path: str) -> bool:
    normalized = path.rstrip("/")
    return normalized == "/Game/_MCP_Temp" or normalized.startswith("/Game/_MCP_Temp/")


def classify_failure(phase: str, error_type: str, error: str, command: str = "") -> str:
    error_text = f"{error_type} {error}".lower()
    if phase == "executor_policy":
        return "policy_block"
    if phase == "cleanup":
        return "cleanup_failure"
    if "winerror 10054" in error_text or "connectionreseterror" in error_text:
        return "bridge_connection_reset"
    if "winerror 10061" in error_text or "connectionrefusederror" in error_text:
        return "bridge_connection_refused"
    if "quit_editor" in error_text or "editor shut down" in error_text or "engine exit requested" in error_text:
        return "editor_shutdown"
    if "compile validation failed" in error_text or command == "compile_and_validate_blueprint":
        return "compile_validation_failure"
    if phase == "structural_validation":
        return "structural_validation_failure"
    return "manifest_step_failure"


def replay_safety_for_category(category: str) -> Dict[str, Any]:
    if category == "policy_block":
        action = "do_not_replay_until_policy_reinforced"
        safe_to_replay_authoring = False
    elif category == "cleanup_failure":
        action = "retry_cleanup_only_before_authoring_replay"
        safe_to_replay_authoring = False
    elif category in {"bridge_connection_reset", "bridge_connection_refused", "editor_shutdown"}:
        action = "repair_or_restart_bridge_then_rerun_temp_smoke"
        safe_to_replay_authoring = True
    elif category == "compile_validation_failure":
        action = "inspect_compile_diagnostics_before_replay"
        safe_to_replay_authoring = False
    elif category == "structural_validation_failure":
        action = "inspect_manifest_contract_and_generated_graph_before_replay"
        safe_to_replay_authoring = False
    else:
        action = "inspect_manifest_step_before_replay"
        safe_to_replay_authoring = False
    return {
        "temp_scope_only": True,
        "durable_side_effects_allowed": False,
        "safe_to_replay_authoring": safe_to_replay_authoring,
        "recommended_action": action,
    }


def enrich_failure_diagnostic(diagnostic: Dict[str, Any], phase: str) -> Dict[str, Any]:
    enriched = dict(diagnostic)
    if "diagnostic_schema" in enriched:
        enriched["legacy_diagnostic_schema"] = enriched["diagnostic_schema"]
    command = str(enriched.get("command", ""))
    category = classify_failure(
        phase=phase,
        error_type=str(enriched.get("error_type", "")),
        error=str(enriched.get("error", enriched.get("reason", ""))),
        command=command,
    )
    enriched["diagnostic_schema"] = FAILURE_DIAGNOSTIC_SCHEMA
    enriched["executor_version"] = EXECUTOR_VERSION
    enriched["failure_category"] = category
    enriched["replay_safety"] = replay_safety_for_category(category)
    return enriched


def implied_command_for_step(step: Dict[str, Any]) -> str:
    operation = step.get("operation", "command")
    if operation == "command":
        return step.get("command", "")
    if operation == "set_pin_default":
        return "set_blueprint_pin_default"
    if operation == "connect":
        return "connect_blueprint_nodes"
    return ""


def step_requests_save(step: Dict[str, Any]) -> bool:
    command = implied_command_for_step(step)
    params = step.get("params", {})
    return bool(
        command == "compile_and_save_blueprint"
        or command == "save_asset"
        or step.get("save")
        or params.get("save")
        or params.get("save_asset")
    )


def flatten_execution_plan(manifest: Dict[str, Any]) -> List[Dict[str, Any]]:
    plan: List[Dict[str, Any]] = []
    for section in EXECUTION_SECTIONS:
        for index, step in enumerate(manifest.get(section, [])):
            command = implied_command_for_step(step)
            plan.append(
                {
                    "section": section,
                    "index": index,
                    "step_id": step.get("id", ""),
                    "operation": step.get("operation", "command"),
                    "command": command,
                    "authoring_command": command in job_contract.AUTHORING_COMMANDS,
                    "validation_command": command in job_contract.VALIDATION_COMMANDS,
                    "save_requested": step_requests_save(step),
                }
            )
    for index, step in enumerate(manifest.get(STRUCTURAL_SECTION, [])):
        plan.append(
            {
                "section": STRUCTURAL_SECTION,
                "index": index,
                "step_id": step.get("id", ""),
                "operation": step.get("operation", ""),
                "command": "",
                "authoring_command": False,
                "validation_command": True,
                "save_requested": False,
            }
        )
    return plan


def structural_operations(manifest: Dict[str, Any]) -> List[str]:
    return [step.get("operation", "") for step in manifest.get(STRUCTURAL_SECTION, [])]


def manifest_operations(manifest: Dict[str, Any]) -> List[str]:
    operations: List[str] = []
    for section in EXECUTION_SECTIONS:
        operations.extend(step.get("operation", "command") for step in manifest.get(section, []))
    operations.extend(structural_operations(manifest))
    return operations


def executable_steps(manifest: Dict[str, Any], section: str) -> List[Dict[str, Any]]:
    return [
        step
        for step in manifest.get(section, [])
        if step.get("operation", "command") not in {"contract_note", "review_only"}
    ]


def command_names(command_plan: Sequence[Dict[str, Any]]) -> List[str]:
    return [item.get("command", "") for item in command_plan if item.get("command")]


def build_capability_coverage(manifest: Dict[str, Any], command_plan: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    operations = manifest_operations(manifest)
    commands = command_names(command_plan)
    has_compile = "compile_and_validate_blueprint" in commands

    typed_requested = bool(
        manifest.get("component_default_steps")
        or manifest.get("variables_defaults")
        or manifest.get("component_property_contracts")
    )
    typed_missing: List[str] = []
    if manifest.get("component_default_steps") and "assert_component_default" not in operations:
        typed_missing.append("assert_component_default")
    if manifest.get("variables_defaults") and "assert_variable_default" not in operations:
        typed_missing.append("assert_variable_default")
    if manifest.get("component_property_contracts") and "assert_component_property" not in operations:
        typed_missing.append("assert_component_property")

    layout_requested = bool(
        manifest.get("graph_layout_contracts")
        or manifest.get("graph_layout_spacing_contracts")
        or any(operation == "assert_pin_link" for operation in operations)
    )
    layout_missing: List[str] = []
    if manifest.get("graph_layout_contracts") and "assert_node_layout" not in operations:
        layout_missing.append("assert_node_layout")
    if manifest.get("graph_layout_spacing_contracts") and "assert_layout_spacing" not in operations:
        layout_missing.append("assert_layout_spacing")
    if any(step.get("operation") == "connect" for section in EXECUTION_SECTIONS for step in manifest.get(section, [])):
        if "assert_pin_link" not in operations:
            layout_missing.append("assert_pin_link")

    function_requested = bool(
        executable_steps(manifest, "function_graph_steps")
        or executable_steps(manifest, "generated_function_invocation_steps")
    )
    function_missing: List[str] = []
    if function_requested:
        if "resolve_blueprint_graph" not in commands:
            function_missing.append("resolve_blueprint_graph")
        if "assert_graph_resolved" not in operations:
            function_missing.append("assert_graph_resolved")
        if "assert_node_exists" not in operations:
            function_missing.append("assert_node_exists")
        if not has_compile:
            function_missing.append("compile_and_validate_blueprint")

    dispatcher_requested = bool(manifest.get("dispatcher_lifecycle_steps"))
    dispatcher_required_commands = {
        "add_blueprint_event_dispatcher",
        "add_blueprint_event_dispatcher_call_node",
        "add_blueprint_custom_event_node",
        "add_blueprint_event_dispatcher_bind_node",
        "add_blueprint_event_dispatcher_assign_node",
        "add_blueprint_event_dispatcher_unbind_node",
        "add_blueprint_event_dispatcher_clear_node",
    }
    dispatcher_missing: List[str] = []
    if dispatcher_requested:
        missing_commands = sorted(dispatcher_required_commands.difference(commands))
        dispatcher_missing.extend(missing_commands)
        if "assert_pin" not in operations:
            dispatcher_missing.append("assert_pin")
        if "assert_pin_link" not in operations:
            dispatcher_missing.append("assert_pin_link")
        if not has_compile:
            dispatcher_missing.append("compile_and_validate_blueprint")

    def entry(requested: bool, missing: Sequence[str], evidence: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "requested": requested,
            "ready": bool(requested and not missing),
            "status": "ready" if requested and not missing else ("not_requested" if not requested else "missing_evidence"),
            "missing_evidence": list(missing),
            "evidence": evidence,
        }

    return {
        "schema": CAPABILITY_MATRIX_SCHEMA,
        "manifest_id": manifest.get("id", ""),
        "typed_defaults": entry(
            typed_requested,
            typed_missing,
            {
                "component_default_steps": len(manifest.get("component_default_steps", [])),
                "variables_defaults": len(manifest.get("variables_defaults", [])),
                "component_property_contracts": len(manifest.get("component_property_contracts", [])),
            },
        ),
        "graph_layout_dataflow": entry(
            layout_requested,
            sorted(set(layout_missing)),
            {
                "graph_layout_contracts": len(manifest.get("graph_layout_contracts", [])),
                "graph_layout_spacing_contracts": len(manifest.get("graph_layout_spacing_contracts", [])),
                "pin_link_assertions": sum(1 for operation in operations if operation == "assert_pin_link"),
            },
        ),
        "function_graph_executor": entry(
            function_requested,
            sorted(set(function_missing)),
            {
                "function_graph_steps": len(manifest.get("function_graph_steps", [])),
                "generated_function_invocation_steps": len(manifest.get("generated_function_invocation_steps", [])),
            },
        ),
        "dispatcher_lifecycle_executor": entry(
            dispatcher_requested,
            sorted(set(dispatcher_missing)),
            {
                "dispatcher_lifecycle_steps": len(manifest.get("dispatcher_lifecycle_steps", [])),
            },
        ),
    }


def unknown_commands(command_plan: Sequence[Dict[str, Any]]) -> List[str]:
    allowed = set(job_contract.AUTHORING_COMMANDS) | set(job_contract.VALIDATION_COMMANDS)
    allowed.update({"set_blueprint_pin_default", "connect_blueprint_nodes", ""})
    return sorted(
        {
            item.get("command", "")
            for item in command_plan
            if item.get("command", "") not in allowed
        }
    )


def manifest_requests_durable_authoring(manifest: Dict[str, Any]) -> bool:
    return bool(
        manifest.get("durable_preflight_contract", {}).get("requested")
        or manifest.get("durable_executor_skeleton_contract", {}).get("requested")
        or manifest.get("cleanup_rollback_boundary", {}).get("durable_authoring_requested")
    )


def build_durable_executor_gate(manifest: Dict[str, Any], command_plan: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    preflight = manifest.get("durable_preflight_contract", {})
    save_gate = manifest.get("durable_save_gate_contract", preflight.get("durable_save_gate_contract", {}))
    rollback = manifest.get("durable_rollback_policy_contract", preflight.get("durable_rollback_policy_contract", {}))
    ownership = manifest.get("durable_ownership_marker_contract", preflight.get("durable_ownership_marker_contract", {}))
    enable_contract = manifest.get("durable_enable_contract", preflight.get("durable_enable_contract", {}))
    dry_run_plan = manifest.get("durable_dry_run_plan_contract", preflight.get("durable_dry_run_plan_contract", {}))
    save_simulation = manifest.get(
        "durable_save_validation_simulation_contract",
        preflight.get("durable_save_validation_simulation_contract", {}),
    )
    canary_prep = manifest.get("durable_canary_prep_contract", preflight.get("durable_canary_prep_contract", {}))
    canary_approval = manifest.get(
        "durable_canary_approval_gate_contract",
        preflight.get("durable_canary_approval_gate_contract", {}),
    )
    canary_live_preflight = manifest.get(
        "durable_canary_live_preflight_contract",
        preflight.get("durable_canary_live_preflight_contract", {}),
    )
    canary_bridge_refresh = manifest.get(
        "durable_canary_bridge_refresh_contract",
        preflight.get("durable_canary_bridge_refresh_contract", {}),
    )
    canary_recovery = manifest.get(
        "durable_canary_recovery_matrix_contract",
        preflight.get("durable_canary_recovery_matrix_contract", {}),
    )
    readiness = manifest.get(
        "durable_executor_readiness_contract",
        preflight.get("durable_executor_readiness_contract", {}),
    )
    skeleton = manifest.get(
        "durable_executor_skeleton_contract",
        preflight.get("durable_executor_skeleton_contract", {}),
    )
    requested = manifest_requests_durable_authoring(manifest)
    read_only_preflight_allowed = bool(
        preflight.get("requested") and preflight.get("live_read_only_check_allowed") and preflight.get("target_asset_path")
    )
    contract_save_allowed = bool(save_gate.get("save_allowed"))
    executor_enabled = bool(skeleton.get("executor_enabled"))
    executor_can_execute = bool(skeleton.get("can_execute"))
    skeleton_command_plan = skeleton.get("command_plan", [])
    save_or_delete_commands_allowed = bool(
        skeleton.get("save_commands_allowed")
        or skeleton.get("delete_commands_allowed")
        or skeleton.get("rename_commands_allowed")
        or enable_contract.get("save_true_allowed")
        or enable_contract.get("save_asset_allowed")
        or enable_contract.get("delete_asset_allowed")
        or enable_contract.get("rename_asset_allowed")
        or ownership.get("delete_without_marker_allowed")
        or ownership.get("delete_preexisting_asset_allowed")
        or ownership.get("overwrite_preexisting_asset_allowed")
        or ownership.get("rename_preexisting_asset_allowed")
        or dry_run_plan.get("save_allowed")
        or dry_run_plan.get("delete_allowed")
        or dry_run_plan.get("rename_allowed")
        or dry_run_plan.get("live_command_count", 0) > 0
        or save_simulation.get("save_true_allowed")
        or save_simulation.get("save_asset_allowed")
        or save_simulation.get("compile_save_command_allowed")
        or save_simulation.get("live_command_count", 0) > 0
        or canary_prep.get("canary_live_execution_allowed")
        or canary_prep.get("general_blueprints_package_allowed")
        or canary_prep.get("save_true_allowed")
        or canary_prep.get("save_asset_allowed")
        or canary_prep.get("delete_asset_allowed")
        or canary_approval.get("canary_executor_may_open")
        or canary_approval.get("canary_live_execution_allowed")
        or canary_approval.get("general_blueprints_package_allowed")
        or canary_approval.get("save_true_allowed")
        or canary_approval.get("save_asset_allowed")
        or canary_approval.get("delete_asset_allowed")
        or canary_approval.get("live_command_count", 0) > 0
        or canary_live_preflight.get("canary_execution_allowed_after_preflight")
        or canary_live_preflight.get("authoring_command_allowed")
        or canary_live_preflight.get("save_or_delete_allowed")
        or canary_live_preflight.get("cleanup_command_allowed")
        or canary_live_preflight.get("live_authoring_command_count", 0) > 0
        or canary_live_preflight.get("live_save_or_delete_command_count", 0) > 0
        or canary_live_preflight.get("live_cleanup_command_count", 0) > 0
        or canary_bridge_refresh.get("canary_execution_allowed_after_refresh")
        or canary_bridge_refresh.get("durable_executor_may_open_after_refresh")
        or canary_bridge_refresh.get("authoring_command_allowed")
        or canary_bridge_refresh.get("save_or_delete_allowed")
        or canary_bridge_refresh.get("cleanup_command_allowed")
        or canary_bridge_refresh.get("live_authoring_command_count", 0) > 0
        or canary_bridge_refresh.get("live_save_or_delete_command_count", 0) > 0
        or canary_bridge_refresh.get("live_cleanup_command_count", 0) > 0
        or canary_recovery.get("cleanup_command_allowed")
        or canary_recovery.get("delete_command_allowed")
        or canary_recovery.get("save_command_allowed")
        or canary_recovery.get("authoring_command_allowed")
        or canary_recovery.get("live_cleanup_command_count", 0) > 0
        or canary_recovery.get("live_delete_command_count", 0) > 0
        or canary_recovery.get("live_save_command_count", 0) > 0
        or canary_recovery.get("live_authoring_command_count", 0) > 0
        or any(item.get("save_requested") for item in command_plan)
        or any(item.get("command") in FORBIDDEN_LIVE_COMMANDS for item in command_plan)
    )
    blocked_by = set(skeleton.get("disabled_by", []))
    blocked_by.update(enable_contract.get("failed_required_gate_ids", []))
    blocked_by.update(save_gate.get("blocked_by", []))
    blocked_by.update(readiness.get("failing_checks", []))
    if requested:
        if not enable_contract.get("enable_contract_satisfied"):
            blocked_by.add("durable_enable_contract_not_satisfied")
        if not executor_enabled:
            blocked_by.add("durable_executor_disabled")
        if not executor_can_execute:
            blocked_by.add("durable_executor_not_executable")
        if not contract_save_allowed:
            blocked_by.add("durable_save_not_allowed")
        if not rollback.get("rollback_policy_ready"):
            blocked_by.add("durable_rollback_policy_not_ready")
        if not read_only_preflight_allowed:
            blocked_by.add("durable_read_only_preflight_not_allowed")
    required_before_execution = set(manifest.get("required_reinforcement", []))
    required_before_execution.update(preflight.get("required_reinforcement", []))
    required_before_execution.update(ownership.get("required_reinforcement", []))
    required_before_execution.update(dry_run_plan.get("required_reinforcement", []))
    required_before_execution.update(save_simulation.get("required_reinforcement", []))
    required_before_execution.update(canary_prep.get("required_reinforcement", []))
    required_before_execution.update(canary_approval.get("required_reinforcement", []))
    required_before_execution.update(canary_live_preflight.get("required_reinforcement", []))
    required_before_execution.update(canary_bridge_refresh.get("required_reinforcement", []))
    required_before_execution.update(canary_recovery.get("required_reinforcement", []))
    required_before_execution.update(save_gate.get("required_reinforcement", []))
    required_before_execution.update(rollback.get("required_reinforcement", []))
    required_before_execution.update(enable_contract.get("required_reinforcement", []))
    required_before_execution.update(readiness.get("required_reinforcement", []))
    required_before_execution.update(skeleton.get("required_reinforcement", []))
    if not requested:
        status = "not_requested"
    elif read_only_preflight_allowed:
        status = "blocked_save_authoring_read_only_preflight_allowed"
    else:
        status = "blocked_save_authoring"
    return {
        "schema": DURABLE_GATE_SCHEMA,
        "manifest_id": manifest.get("id", ""),
        "requested": requested,
        "status": status,
        "target_asset_path": preflight.get("target_asset_path", ""),
        "read_only_live_preflight_requested": bool(preflight.get("requested")),
        "read_only_live_preflight_allowed": read_only_preflight_allowed,
        "read_only_live_command": preflight.get("asset_exists_check_command", "unreal.EditorAssetLibrary.does_asset_exist"),
        "live_scope": "read_only_asset_exists_check_only" if read_only_preflight_allowed else "none",
        "durable_authoring_allowed": False,
        "durable_enable_contract_schema": enable_contract.get("schema", ""),
        "durable_enable_contract_satisfied": bool(enable_contract.get("enable_contract_satisfied")),
        "durable_enable_executor_may_open": bool(enable_contract.get("durable_executor_may_open")),
        "durable_enable_failed_required_gate_ids": list(enable_contract.get("failed_required_gate_ids", [])),
        "ownership_marker_policy_ready": bool(ownership.get("ownership_marker_policy_ready")),
        "delete_without_ownership_marker_allowed": bool(ownership.get("delete_without_marker_allowed")),
        "delete_preexisting_asset_allowed": bool(ownership.get("delete_preexisting_asset_allowed")),
        "dry_run_plan_created": bool(dry_run_plan.get("dry_run_plan_created")),
        "dry_run_plan_valid": bool(dry_run_plan.get("dry_run_plan_valid")),
        "dry_run_plan_live_command_count": int(dry_run_plan.get("live_command_count", 0)),
        "dry_run_plan_executor_may_execute": bool(dry_run_plan.get("durable_executor_may_execute")),
        "save_simulation_evaluated": bool(save_simulation.get("simulation_evaluated")),
        "save_simulation_conditions_satisfied": bool(save_simulation.get("future_save_conditions_satisfied")),
        "save_simulation_save_true_allowed": bool(save_simulation.get("save_true_allowed")),
        "save_simulation_save_asset_allowed": bool(save_simulation.get("save_asset_allowed")),
        "save_simulation_live_command_count": int(save_simulation.get("live_command_count", 0)),
        "canary_prep_ready": bool(canary_prep.get("canary_prep_ready")),
        "canary_live_execution_allowed": bool(canary_prep.get("canary_live_execution_allowed")),
        "canary_general_blueprints_package_allowed": bool(canary_prep.get("general_blueprints_package_allowed")),
        "canary_save_true_allowed": bool(canary_prep.get("save_true_allowed")),
        "canary_save_asset_allowed": bool(canary_prep.get("save_asset_allowed")),
        "canary_delete_asset_allowed": bool(canary_prep.get("delete_asset_allowed")),
        "canary_approval_record_present": bool(canary_approval.get("approval_record_present")),
        "canary_approval_gate_passed": bool(canary_approval.get("canary_approval_gate_passed")),
        "canary_approval_scoped_to_canary_package": bool(
            canary_approval.get("approval_scoped_to_canary_package")
        ),
        "canary_approval_executor_may_open": bool(canary_approval.get("canary_executor_may_open")),
        "canary_approval_live_execution_allowed": bool(canary_approval.get("canary_live_execution_allowed")),
        "canary_approval_general_blueprints_package_allowed": bool(
            canary_approval.get("general_blueprints_package_allowed")
        ),
        "canary_approval_save_true_allowed": bool(canary_approval.get("save_true_allowed")),
        "canary_approval_save_asset_allowed": bool(canary_approval.get("save_asset_allowed")),
        "canary_approval_delete_asset_allowed": bool(canary_approval.get("delete_asset_allowed")),
        "canary_approval_live_command_count": int(canary_approval.get("live_command_count", 0)),
        "canary_live_preflight_read_only_allowed": bool(
            canary_live_preflight.get("read_only_live_preflight_allowed")
        ),
        "canary_live_preflight_execution_allowed": bool(
            canary_live_preflight.get("canary_execution_allowed_after_preflight")
        ),
        "canary_live_preflight_authoring_allowed": bool(canary_live_preflight.get("authoring_command_allowed")),
        "canary_live_preflight_save_or_delete_allowed": bool(canary_live_preflight.get("save_or_delete_allowed")),
        "canary_live_preflight_cleanup_allowed": bool(canary_live_preflight.get("cleanup_command_allowed")),
        "canary_live_preflight_authoring_command_count": int(
            canary_live_preflight.get("live_authoring_command_count", 0)
        ),
        "canary_live_preflight_save_or_delete_command_count": int(
            canary_live_preflight.get("live_save_or_delete_command_count", 0)
        ),
        "canary_live_preflight_cleanup_command_count": int(
            canary_live_preflight.get("live_cleanup_command_count", 0)
        ),
        "canary_bridge_refresh_required": bool(canary_bridge_refresh.get("bridge_refresh_required")),
        "canary_bridge_refresh_reachable": bool(canary_bridge_refresh.get("bridge_reachable")),
        "canary_bridge_refresh_read_only_result_refreshed": bool(
            canary_bridge_refresh.get("read_only_result_refreshed")
        ),
        "canary_bridge_refresh_satisfied": bool(canary_bridge_refresh.get("bridge_refresh_satisfied")),
        "canary_bridge_refresh_execution_allowed": bool(
            canary_bridge_refresh.get("canary_execution_allowed_after_refresh")
        ),
        "canary_bridge_refresh_executor_may_open": bool(
            canary_bridge_refresh.get("durable_executor_may_open_after_refresh")
        ),
        "canary_bridge_refresh_save_or_delete_allowed": bool(canary_bridge_refresh.get("save_or_delete_allowed")),
        "canary_bridge_refresh_cleanup_allowed": bool(canary_bridge_refresh.get("cleanup_command_allowed")),
        "canary_bridge_refresh_authoring_command_count": int(
            canary_bridge_refresh.get("live_authoring_command_count", 0)
        ),
        "canary_bridge_refresh_save_or_delete_command_count": int(
            canary_bridge_refresh.get("live_save_or_delete_command_count", 0)
        ),
        "canary_bridge_refresh_cleanup_command_count": int(
            canary_bridge_refresh.get("live_cleanup_command_count", 0)
        ),
        "canary_recovery_matrix_ready": bool(canary_recovery.get("recovery_matrix_ready")),
        "canary_recovery_scenario_count": int(canary_recovery.get("scenario_count", 0)),
        "canary_recovery_cleanup_allowed": bool(canary_recovery.get("cleanup_command_allowed")),
        "canary_recovery_delete_allowed": bool(canary_recovery.get("delete_command_allowed")),
        "canary_recovery_save_allowed": bool(canary_recovery.get("save_command_allowed")),
        "canary_recovery_authoring_allowed": bool(canary_recovery.get("authoring_command_allowed")),
        "canary_recovery_live_cleanup_command_count": int(canary_recovery.get("live_cleanup_command_count", 0)),
        "canary_recovery_live_delete_command_count": int(canary_recovery.get("live_delete_command_count", 0)),
        "canary_recovery_live_save_command_count": int(canary_recovery.get("live_save_command_count", 0)),
        "canary_recovery_live_authoring_command_count": int(canary_recovery.get("live_authoring_command_count", 0)),
        "durable_executor_enabled": executor_enabled,
        "durable_executor_can_execute": executor_can_execute,
        "durable_executor_command_count": len(skeleton_command_plan),
        "allowed_live_authoring_command_count": 0,
        "save_gate_requested": bool(save_gate.get("requested")),
        "contract_save_allowed": contract_save_allowed,
        "save_allowed": False,
        "save_commands_allowed": False,
        "delete_commands_allowed": False,
        "rename_commands_allowed": False,
        "save_or_delete_commands_allowed": save_or_delete_commands_allowed,
        "rollback_policy_ready": bool(rollback.get("rollback_policy_ready")),
        "preflight_pass": bool(preflight.get("preflight_pass")),
        "forbidden_commands": sorted(
            set(skeleton.get("forbidden_commands", ()))
            | set(FORBIDDEN_LIVE_COMMANDS)
            | {"save_asset", "delete_asset", "rename_asset", "duplicate_asset", "replace_existing_asset"}
        ),
        "blocked_by": sorted(blocked_by),
        "required_before_durable_execution": sorted(required_before_execution),
    }


def build_executor_policy(manifest: Dict[str, Any], temp_package_path: str) -> Dict[str, Any]:
    command_plan = flatten_execution_plan(manifest)
    capability_coverage = build_capability_coverage(manifest, command_plan)
    durable_gate = build_durable_executor_gate(manifest, command_plan)
    blocked_reasons: List[Dict[str, Any]] = []

    def block(key: str, reason: str, required: Iterable[str]) -> None:
        blocked_reasons.append(
            {
                "key": key,
                "reason": reason,
                "required_before_execution": list(required),
            }
        )

    if manifest.get("status") != planner.STATUS_SAFE:
        block("manifest_not_safe", "Only planner safe manifests may execute.", ("planner status safe_to_author",))
    if not manifest.get("executable"):
        block("manifest_not_executable", "Manifest is a dry-run record, not an executable job.", ("executable=true",))
    if manifest.get("parent_class") != "Actor":
        block("parent_class_not_allowlisted", "Section 40 executor supports only Actor parent Blueprints.", ("parent_class=Actor",))
    if not is_temp_package_path(temp_package_path):
        block("temp_package_path_not_allowlisted", "Temporary executor output must stay under /Game/_MCP_Temp.", ("/Game/_MCP_Temp output root",))
    if manifest_requests_durable_authoring(manifest):
        block(
            "durable_authoring_not_enabled",
            "Section 46-48 executor gate permits only read-only durable preflight and cannot execute durable authoring.",
            ("durable executor enable gate", "durable save gate", "rollback ownership boundary"),
        )
    if (
        durable_gate["durable_executor_enabled"]
        or durable_gate["durable_executor_can_execute"]
        or durable_gate["durable_enable_executor_may_open"]
        or durable_gate["dry_run_plan_executor_may_execute"]
        or durable_gate["dry_run_plan_live_command_count"] > 0
        or durable_gate["save_simulation_save_true_allowed"]
        or durable_gate["save_simulation_save_asset_allowed"]
        or durable_gate["save_simulation_live_command_count"] > 0
        or durable_gate["canary_live_execution_allowed"]
        or durable_gate["canary_general_blueprints_package_allowed"]
        or durable_gate["canary_save_true_allowed"]
        or durable_gate["canary_save_asset_allowed"]
        or durable_gate["canary_delete_asset_allowed"]
        or durable_gate["canary_approval_executor_may_open"]
        or durable_gate["canary_approval_live_execution_allowed"]
        or durable_gate["canary_approval_general_blueprints_package_allowed"]
        or durable_gate["canary_approval_save_true_allowed"]
        or durable_gate["canary_approval_save_asset_allowed"]
        or durable_gate["canary_approval_delete_asset_allowed"]
        or durable_gate["canary_approval_live_command_count"] > 0
        or durable_gate["canary_live_preflight_execution_allowed"]
        or durable_gate["canary_live_preflight_authoring_allowed"]
        or durable_gate["canary_live_preflight_save_or_delete_allowed"]
        or durable_gate["canary_live_preflight_cleanup_allowed"]
        or durable_gate["canary_live_preflight_authoring_command_count"] > 0
        or durable_gate["canary_live_preflight_save_or_delete_command_count"] > 0
        or durable_gate["canary_live_preflight_cleanup_command_count"] > 0
        or durable_gate["canary_bridge_refresh_execution_allowed"]
        or durable_gate["canary_bridge_refresh_executor_may_open"]
        or durable_gate["canary_bridge_refresh_save_or_delete_allowed"]
        or durable_gate["canary_bridge_refresh_cleanup_allowed"]
        or durable_gate["canary_bridge_refresh_authoring_command_count"] > 0
        or durable_gate["canary_bridge_refresh_save_or_delete_command_count"] > 0
        or durable_gate["canary_bridge_refresh_cleanup_command_count"] > 0
        or durable_gate["canary_recovery_cleanup_allowed"]
        or durable_gate["canary_recovery_delete_allowed"]
        or durable_gate["canary_recovery_save_allowed"]
        or durable_gate["canary_recovery_authoring_allowed"]
        or durable_gate["canary_recovery_live_cleanup_command_count"] > 0
        or durable_gate["canary_recovery_live_delete_command_count"] > 0
        or durable_gate["canary_recovery_live_save_command_count"] > 0
        or durable_gate["canary_recovery_live_authoring_command_count"] > 0
        or durable_gate["contract_save_allowed"]
        or durable_gate["save_or_delete_commands_allowed"]
        or durable_gate["allowed_live_authoring_command_count"]
    ):
        block(
            "durable_gate_opened",
            "Durable gate unexpectedly exposes save, delete, rename, or authoring execution.",
            ("close durable executor gate before temporary smoke execution",),
        )

    forbidden_commands = sorted(
        {
            item.get("command", "")
            for item in command_plan
            if item.get("command", "") in FORBIDDEN_LIVE_COMMANDS
        }
    )
    if forbidden_commands:
        block(
            "forbidden_live_command",
            f"Manifest contains forbidden live command(s): {', '.join(forbidden_commands)}",
            ("remove save/delete/rename commands",),
        )

    save_steps = [item for item in command_plan if item.get("save_requested")]
    if save_steps:
        block(
            "save_requested",
            "Section 40 temporary executor must compile with save=false.",
            ("save=false on every live compile",),
        )

    unknown = unknown_commands(command_plan)
    if unknown:
        block(
            "unknown_live_command",
            f"Manifest contains command(s) outside the executor allowlist: {', '.join(unknown)}",
            ("add an explicit executor handler and smoke coverage",),
        )

    return {
        "schema": EXECUTOR_POLICY_SCHEMA,
        "executor_version": EXECUTOR_VERSION,
        "manifest_id": manifest.get("id", ""),
        "manifest_version": manifest.get("manifest_version", ""),
        "requested": True,
        "executor_mode": "temporary_manifest_executor",
        "can_execute": not blocked_reasons,
        "temp_package_path": temp_package_path,
        "temp_scope_only": True,
        "durable_authoring_allowed": False,
        "save_allowed": False,
        "delete_allowed_scope": "/Game/_MCP_Temp",
        "command_plan_count": len(command_plan),
        "authoring_command_count": sum(1 for item in command_plan if item.get("authoring_command")),
        "validation_command_count": sum(1 for item in command_plan if item.get("validation_command")),
        "save_step_count": len(save_steps),
        "unknown_command_count": len(unknown),
        "forbidden_command_count": len(forbidden_commands),
        "blocked_reasons": blocked_reasons,
        "command_plan": command_plan,
        "capability_coverage": capability_coverage,
        "durable_executor_gate": durable_gate,
    }


def build_policy_failure_diagnostic(manifest: Dict[str, Any], policy: Dict[str, Any]) -> Dict[str, Any]:
    return enrich_failure_diagnostic(
        {
        "diagnostic_schema": "section_40_manifest_executor_policy_failure_v1",
        "executor_version": EXECUTOR_VERSION,
        "manifest_id": manifest.get("id", ""),
        "manifest_version": manifest.get("manifest_version", ""),
        "phase": "executor_policy",
        "reason": "manifest_executor_policy_blocked",
        "blocked_reasons": policy.get("blocked_reasons", []),
        "error": "Manifest executor policy blocked live execution",
        },
        phase="executor_policy",
    )


def build_cleanup_failure_diagnostic(
    manifest: Dict[str, Any],
    blueprint_name: str,
    asset_path: str,
    cleanup_result: Dict[str, Any],
) -> Dict[str, Any]:
    return enrich_failure_diagnostic(
        {
            "diagnostic_schema": "section_41_cleanup_failure_v1",
            "manifest_id": manifest.get("id", ""),
            "manifest_version": manifest.get("manifest_version", ""),
            "blueprint_name": blueprint_name,
            "asset_path": asset_path,
            "phase": "cleanup",
            "section": "cleanup",
            "step_id": "cleanup_generated_asset",
            "operation": "delete_temp_asset",
            "command": "execute_python",
            "error_type": "CleanupFailure",
            "error": str(cleanup_result.get("error") or cleanup_result),
            "cleanup_result": cleanup_result,
        },
        phase="cleanup",
    )


def execute_manifest(
    manifest: Dict[str, Any],
    blueprint_name: str,
    temp_package_path: str,
    callbacks: ManifestExecutorCallbacks,
) -> Dict[str, Any]:
    policy = build_executor_policy(manifest, temp_package_path)
    if not policy["can_execute"]:
        diagnostic = build_policy_failure_diagnostic(manifest, policy)
        partial = {
            "schema": EXECUTOR_RESULT_SCHEMA,
            "executor_version": EXECUTOR_VERSION,
            "manifest_id": manifest.get("id", ""),
            "blueprint_name": blueprint_name,
            "status": "blocked",
            "executor_policy": policy,
            "section_results": [],
            "structural_results": [],
        }
        raise ManifestExecutorFailure(diagnostic, policy, partial)

    node_results: Dict[str, Dict[str, Any]] = {}
    section_results: List[Dict[str, Any]] = []
    structural_results: List[Dict[str, Any]] = []
    current_section = ""
    current_step: Dict[str, Any] = {}

    try:
        for section in EXECUTION_SECTIONS:
            for step in manifest.get(section, []):
                current_section = section
                current_step = step
                callbacks.execute_step(section, step, node_results, section_results)

        for step in manifest.get(STRUCTURAL_SECTION, []):
            current_section = STRUCTURAL_SECTION
            current_step = step
            structural_results.append(callbacks.execute_structural_step(step, node_results))
    except ManifestExecutorFailure:
        raise
    except Exception as exc:
        phase = "structural_validation" if current_section == STRUCTURAL_SECTION else "manifest_step"
        diagnostic = enrich_failure_diagnostic(
            callbacks.build_failure_diagnostic(current_section, current_step, node_results, exc, phase),
            phase=phase,
        )
        failed_result = {
            "id": current_step.get("id"),
            "operation": current_step.get("operation", "command"),
            "command": current_step.get("command", ""),
            "status": "failed",
            "failure_diagnostics": diagnostic,
        }
        if current_section == STRUCTURAL_SECTION:
            structural_results.append(failed_result)
        else:
            section_results.append(failed_result)
        partial = {
            "schema": EXECUTOR_RESULT_SCHEMA,
            "executor_version": EXECUTOR_VERSION,
            "manifest_id": manifest.get("id", ""),
            "blueprint_name": blueprint_name,
            "status": "failed",
            "executor_policy": policy,
            "section_results": section_results,
            "structural_results": structural_results,
            "failure_diagnostics": diagnostic,
        }
        raise ManifestExecutorFailure(diagnostic, policy, partial) from exc

    validation = node_results.get("compile_validate", {})
    event_nodes = node_results.get("event_nodes", {})
    function_nodes = node_results.get("function_nodes", {})
    graphs = node_results.get("graphs", {})
    return {
        "schema": EXECUTOR_RESULT_SCHEMA,
        "executor_version": EXECUTOR_VERSION,
        "manifest_id": manifest.get("id", ""),
        "blueprint_name": blueprint_name,
        "status": "passed",
        "executor_policy": policy,
        "section_results": section_results,
        "structural_results": structural_results,
        "validation": validation,
        "node_count": len(event_nodes.get("nodes", [])),
        "function_node_count": len(function_nodes.get("nodes", [])),
        "graph_count": len(graphs.get("graphs", [])),
        "structural_assertion_count": len(structural_results),
        "layout_assertion_count": sum(1 for result in structural_results if result.get("operation") == "assert_node_layout"),
        "layout_spacing_assertion_count": sum(1 for result in structural_results if result.get("operation") == "assert_layout_spacing"),
        "failed_structural_assertion_count": 0,
        "dataflow_verified": any(
            result.get("operation") == "assert_pin_link" and result.get("link_kind") == "data"
            for result in structural_results
        ),
        "replay_safety": {
            "temp_scope_only": True,
            "durable_side_effects_allowed": False,
            "safe_to_replay_authoring": True,
            "recommended_action": "rerun_temp_smoke_after_cleanup_verification",
        },
    }


def summarize_executor_policies(manifests: Sequence[Dict[str, Any]], temp_package_path: str) -> Dict[str, Any]:
    policies = [build_executor_policy(manifest, temp_package_path) for manifest in manifests]
    capability_summary: Dict[str, Dict[str, int]] = {}
    for capability in CAPABILITY_KEYS:
        coverage_items = [policy["capability_coverage"][capability] for policy in policies]
        capability_summary[capability] = {
            "requested_manifest_count": sum(1 for item in coverage_items if item["requested"]),
            "ready_manifest_count": sum(1 for item in coverage_items if item["ready"]),
            "missing_evidence_manifest_count": sum(1 for item in coverage_items if item["status"] == "missing_evidence"),
        }
    durable_gates = [policy["durable_executor_gate"] for policy in policies]
    durable_requested_count = sum(1 for gate in durable_gates if gate["requested"])
    durable_gate_summary = {
        "schema": DURABLE_GATE_SCHEMA,
        "durable_requested_manifest_count": durable_requested_count,
        "read_only_live_preflight_allowed_count": sum(1 for gate in durable_gates if gate["read_only_live_preflight_allowed"]),
        "durable_enable_contract_satisfied_count": sum(
            1 for gate in durable_gates if gate["durable_enable_contract_satisfied"]
        ),
        "durable_enable_executor_may_open_count": sum(1 for gate in durable_gates if gate["durable_enable_executor_may_open"]),
        "durable_enable_failed_required_gate_count": sum(
            len(gate["durable_enable_failed_required_gate_ids"]) for gate in durable_gates
        ),
        "ownership_marker_policy_ready_count": sum(1 for gate in durable_gates if gate["ownership_marker_policy_ready"]),
        "delete_without_ownership_marker_allowed_count": sum(
            1 for gate in durable_gates if gate["delete_without_ownership_marker_allowed"]
        ),
        "delete_preexisting_asset_allowed_count": sum(1 for gate in durable_gates if gate["delete_preexisting_asset_allowed"]),
        "dry_run_plan_created_count": sum(1 for gate in durable_gates if gate["dry_run_plan_created"]),
        "dry_run_plan_valid_count": sum(1 for gate in durable_gates if gate["dry_run_plan_valid"]),
        "dry_run_plan_executor_may_execute_count": sum(
            1 for gate in durable_gates if gate["dry_run_plan_executor_may_execute"]
        ),
        "dry_run_plan_live_command_count": sum(gate["dry_run_plan_live_command_count"] for gate in durable_gates),
        "save_simulation_evaluated_count": sum(1 for gate in durable_gates if gate["save_simulation_evaluated"]),
        "save_simulation_conditions_satisfied_count": sum(
            1 for gate in durable_gates if gate["save_simulation_conditions_satisfied"]
        ),
        "save_simulation_save_true_allowed_count": sum(
            1 for gate in durable_gates if gate["save_simulation_save_true_allowed"]
        ),
        "save_simulation_save_asset_allowed_count": sum(
            1 for gate in durable_gates if gate["save_simulation_save_asset_allowed"]
        ),
        "save_simulation_live_command_count": sum(gate["save_simulation_live_command_count"] for gate in durable_gates),
        "canary_prep_ready_count": sum(1 for gate in durable_gates if gate["canary_prep_ready"]),
        "canary_live_execution_allowed_count": sum(1 for gate in durable_gates if gate["canary_live_execution_allowed"]),
        "canary_general_blueprints_package_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_general_blueprints_package_allowed"]
        ),
        "canary_save_true_allowed_count": sum(1 for gate in durable_gates if gate["canary_save_true_allowed"]),
        "canary_save_asset_allowed_count": sum(1 for gate in durable_gates if gate["canary_save_asset_allowed"]),
        "canary_delete_asset_allowed_count": sum(1 for gate in durable_gates if gate["canary_delete_asset_allowed"]),
        "canary_approval_record_present_count": sum(
            1 for gate in durable_gates if gate["canary_approval_record_present"]
        ),
        "canary_approval_gate_passed_count": sum(1 for gate in durable_gates if gate["canary_approval_gate_passed"]),
        "canary_approval_scoped_to_canary_package_count": sum(
            1 for gate in durable_gates if gate["canary_approval_scoped_to_canary_package"]
        ),
        "canary_approval_executor_may_open_count": sum(
            1 for gate in durable_gates if gate["canary_approval_executor_may_open"]
        ),
        "canary_approval_live_execution_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_approval_live_execution_allowed"]
        ),
        "canary_approval_general_blueprints_package_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_approval_general_blueprints_package_allowed"]
        ),
        "canary_approval_save_true_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_approval_save_true_allowed"]
        ),
        "canary_approval_save_asset_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_approval_save_asset_allowed"]
        ),
        "canary_approval_delete_asset_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_approval_delete_asset_allowed"]
        ),
        "canary_approval_live_command_count": sum(
            gate["canary_approval_live_command_count"] for gate in durable_gates
        ),
        "canary_live_preflight_read_only_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_live_preflight_read_only_allowed"]
        ),
        "canary_live_preflight_execution_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_live_preflight_execution_allowed"]
        ),
        "canary_live_preflight_authoring_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_live_preflight_authoring_allowed"]
        ),
        "canary_live_preflight_save_or_delete_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_live_preflight_save_or_delete_allowed"]
        ),
        "canary_live_preflight_cleanup_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_live_preflight_cleanup_allowed"]
        ),
        "canary_live_preflight_authoring_command_count": sum(
            gate["canary_live_preflight_authoring_command_count"] for gate in durable_gates
        ),
        "canary_live_preflight_save_or_delete_command_count": sum(
            gate["canary_live_preflight_save_or_delete_command_count"] for gate in durable_gates
        ),
        "canary_live_preflight_cleanup_command_count": sum(
            gate["canary_live_preflight_cleanup_command_count"] for gate in durable_gates
        ),
        "canary_bridge_refresh_required_count": sum(
            1 for gate in durable_gates if gate["canary_bridge_refresh_required"]
        ),
        "canary_bridge_refresh_reachable_count": sum(
            1 for gate in durable_gates if gate["canary_bridge_refresh_reachable"]
        ),
        "canary_bridge_refresh_read_only_result_refreshed_count": sum(
            1 for gate in durable_gates if gate["canary_bridge_refresh_read_only_result_refreshed"]
        ),
        "canary_bridge_refresh_satisfied_count": sum(
            1 for gate in durable_gates if gate["canary_bridge_refresh_satisfied"]
        ),
        "canary_bridge_refresh_execution_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_bridge_refresh_execution_allowed"]
        ),
        "canary_bridge_refresh_executor_may_open_count": sum(
            1 for gate in durable_gates if gate["canary_bridge_refresh_executor_may_open"]
        ),
        "canary_bridge_refresh_save_or_delete_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_bridge_refresh_save_or_delete_allowed"]
        ),
        "canary_bridge_refresh_cleanup_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_bridge_refresh_cleanup_allowed"]
        ),
        "canary_bridge_refresh_authoring_command_count": sum(
            gate["canary_bridge_refresh_authoring_command_count"] for gate in durable_gates
        ),
        "canary_bridge_refresh_save_or_delete_command_count": sum(
            gate["canary_bridge_refresh_save_or_delete_command_count"] for gate in durable_gates
        ),
        "canary_bridge_refresh_cleanup_command_count": sum(
            gate["canary_bridge_refresh_cleanup_command_count"] for gate in durable_gates
        ),
        "canary_recovery_matrix_ready_count": sum(1 for gate in durable_gates if gate["canary_recovery_matrix_ready"]),
        "canary_recovery_scenario_count": sum(gate["canary_recovery_scenario_count"] for gate in durable_gates),
        "canary_recovery_cleanup_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_recovery_cleanup_allowed"]
        ),
        "canary_recovery_delete_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_recovery_delete_allowed"]
        ),
        "canary_recovery_save_allowed_count": sum(1 for gate in durable_gates if gate["canary_recovery_save_allowed"]),
        "canary_recovery_authoring_allowed_count": sum(
            1 for gate in durable_gates if gate["canary_recovery_authoring_allowed"]
        ),
        "canary_recovery_live_cleanup_command_count": sum(
            gate["canary_recovery_live_cleanup_command_count"] for gate in durable_gates
        ),
        "canary_recovery_live_delete_command_count": sum(
            gate["canary_recovery_live_delete_command_count"] for gate in durable_gates
        ),
        "canary_recovery_live_save_command_count": sum(
            gate["canary_recovery_live_save_command_count"] for gate in durable_gates
        ),
        "canary_recovery_live_authoring_command_count": sum(
            gate["canary_recovery_live_authoring_command_count"] for gate in durable_gates
        ),
        "durable_executor_enabled_count": sum(1 for gate in durable_gates if gate["durable_executor_enabled"]),
        "durable_executor_executable_count": sum(1 for gate in durable_gates if gate["durable_executor_can_execute"]),
        "durable_executor_command_count": sum(gate["durable_executor_command_count"] for gate in durable_gates),
        "allowed_live_authoring_command_count": sum(gate["allowed_live_authoring_command_count"] for gate in durable_gates),
        "contract_save_allowed_count": sum(1 for gate in durable_gates if gate["contract_save_allowed"]),
        "save_or_delete_commands_allowed_count": sum(1 for gate in durable_gates if gate["save_or_delete_commands_allowed"]),
        "preflight_pass_count": sum(1 for gate in durable_gates if gate["preflight_pass"]),
        "status": "passed"
        if (
            durable_requested_count == sum(1 for gate in durable_gates if gate["read_only_live_preflight_allowed"])
            and sum(1 for gate in durable_gates if gate["durable_enable_contract_satisfied"]) == 0
            and sum(1 for gate in durable_gates if gate["durable_enable_executor_may_open"]) == 0
            and sum(1 for gate in durable_gates if gate["delete_without_ownership_marker_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["delete_preexisting_asset_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["dry_run_plan_executor_may_execute"]) == 0
            and sum(gate["dry_run_plan_live_command_count"] for gate in durable_gates) == 0
            and sum(1 for gate in durable_gates if gate["save_simulation_save_true_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["save_simulation_save_asset_allowed"]) == 0
            and sum(gate["save_simulation_live_command_count"] for gate in durable_gates) == 0
            and sum(1 for gate in durable_gates if gate["canary_live_execution_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_general_blueprints_package_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_save_true_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_save_asset_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_delete_asset_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_approval_executor_may_open"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_approval_live_execution_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_approval_general_blueprints_package_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_approval_save_true_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_approval_save_asset_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_approval_delete_asset_allowed"]) == 0
            and sum(gate["canary_approval_live_command_count"] for gate in durable_gates) == 0
            and sum(1 for gate in durable_gates if gate["canary_live_preflight_execution_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_live_preflight_authoring_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_live_preflight_save_or_delete_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_live_preflight_cleanup_allowed"]) == 0
            and sum(gate["canary_live_preflight_authoring_command_count"] for gate in durable_gates) == 0
            and sum(gate["canary_live_preflight_save_or_delete_command_count"] for gate in durable_gates) == 0
            and sum(gate["canary_live_preflight_cleanup_command_count"] for gate in durable_gates) == 0
            and sum(1 for gate in durable_gates if gate["canary_bridge_refresh_execution_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_bridge_refresh_executor_may_open"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_bridge_refresh_save_or_delete_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_bridge_refresh_cleanup_allowed"]) == 0
            and sum(gate["canary_bridge_refresh_authoring_command_count"] for gate in durable_gates) == 0
            and sum(gate["canary_bridge_refresh_save_or_delete_command_count"] for gate in durable_gates) == 0
            and sum(gate["canary_bridge_refresh_cleanup_command_count"] for gate in durable_gates) == 0
            and sum(1 for gate in durable_gates if gate["canary_recovery_cleanup_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_recovery_delete_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_recovery_save_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["canary_recovery_authoring_allowed"]) == 0
            and sum(gate["canary_recovery_live_cleanup_command_count"] for gate in durable_gates) == 0
            and sum(gate["canary_recovery_live_delete_command_count"] for gate in durable_gates) == 0
            and sum(gate["canary_recovery_live_save_command_count"] for gate in durable_gates) == 0
            and sum(gate["canary_recovery_live_authoring_command_count"] for gate in durable_gates) == 0
            and sum(1 for gate in durable_gates if gate["durable_executor_enabled"]) == 0
            and sum(1 for gate in durable_gates if gate["durable_executor_can_execute"]) == 0
            and sum(gate["allowed_live_authoring_command_count"] for gate in durable_gates) == 0
            and sum(1 for gate in durable_gates if gate["contract_save_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["save_or_delete_commands_allowed"]) == 0
            and sum(1 for gate in durable_gates if gate["preflight_pass"]) == 0
        )
        else "failed",
    }
    return {
        "executor_version": EXECUTOR_VERSION,
        "policy_schema": EXECUTOR_POLICY_SCHEMA,
        "capability_matrix_schema": CAPABILITY_MATRIX_SCHEMA,
        "durable_gate_schema": DURABLE_GATE_SCHEMA,
        "manifest_count": len(policies),
        "executable_by_executor_count": sum(1 for policy in policies if policy["can_execute"]),
        "blocked_by_executor_count": sum(1 for policy in policies if not policy["can_execute"]),
        "temporary_scope_only": True,
        "durable_authoring_allowed": False,
        "save_allowed": False,
        "command_plan_count": sum(policy["command_plan_count"] for policy in policies),
        "authoring_command_count": sum(policy["authoring_command_count"] for policy in policies),
        "validation_command_count": sum(policy["validation_command_count"] for policy in policies),
        "save_step_count": sum(policy["save_step_count"] for policy in policies),
        "unknown_command_count": sum(policy["unknown_command_count"] for policy in policies),
        "forbidden_command_count": sum(policy["forbidden_command_count"] for policy in policies),
        "capability_summary": capability_summary,
        "durable_gate_summary": durable_gate_summary,
        "policies": policies,
    }


def summarize_durable_live_preflight(
    manifests: Sequence[Dict[str, Any]],
    live_preflight_results: Sequence[Dict[str, Any]],
    live_requested: bool,
) -> Dict[str, Any]:
    requested_manifests = [
        manifest
        for manifest in manifests
        if manifest.get("durable_preflight_contract", {}).get("requested")
    ]
    allowed_manifest_ids = {
        manifest.get("id", "")
        for manifest in requested_manifests
        if manifest.get("durable_preflight_contract", {}).get("live_read_only_check_allowed")
    }
    result_manifest_ids = {result.get("manifest_id", "") for result in live_preflight_results}
    authoring_attempted_count = sum(1 for result in live_preflight_results if result.get("authoring_attempted"))
    save_or_delete_attempted_count = sum(1 for result in live_preflight_results if result.get("save_or_delete_attempted"))
    passed_read_only_result_count = sum(
        1
        for result in live_preflight_results
        if result.get("status") == "passed"
        and result.get("read_only") is True
        and result.get("asset_exists_check_performed") is True
        and not result.get("authoring_attempted")
        and not result.get("save_or_delete_attempted")
    )
    if not live_requested:
        status = "not_requested"
    elif not requested_manifests:
        status = "not_requested"
    elif (
        result_manifest_ids == allowed_manifest_ids
        and passed_read_only_result_count == len(allowed_manifest_ids)
        and authoring_attempted_count == 0
        and save_or_delete_attempted_count == 0
    ):
        status = "passed"
    else:
        status = "failed"
    return {
        "schema": DURABLE_LIVE_PREFLIGHT_SCHEMA,
        "status": status,
        "live_requested": live_requested,
        "durable_preflight_requested_manifest_count": len(requested_manifests),
        "read_only_live_preflight_allowed_count": len(allowed_manifest_ids),
        "live_result_count": len(live_preflight_results),
        "passed_read_only_result_count": passed_read_only_result_count,
        "authoring_attempted_count": authoring_attempted_count,
        "save_or_delete_attempted_count": save_or_delete_attempted_count,
        "preflight_pass_count": sum(1 for result in live_preflight_results if result.get("preflight_pass")),
        "durable_authoring_allowed": False,
        "save_or_delete_allowed": False,
        "missing_live_result_manifest_ids": sorted(allowed_manifest_ids - result_manifest_ids) if live_requested else [],
        "unexpected_live_result_manifest_ids": sorted(result_manifest_ids - allowed_manifest_ids),
        "read_only_only": True,
    }


def summarize_durable_canary_live_preflight(
    manifests: Sequence[Dict[str, Any]],
    live_preflight_results: Sequence[Dict[str, Any]],
    live_requested: bool,
) -> Dict[str, Any]:
    return durable_canary_live_preflight.summarize_canary_live_preflight_results(
        manifests,
        live_preflight_results,
        live_requested,
    )
