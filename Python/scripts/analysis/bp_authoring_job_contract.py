#!/usr/bin/env python
"""
Section 39 Blueprint authoring job contract.

This layer converts a user-facing Blueprint authoring request into a structured
manifest before any live UnrealMCP asset-authoring command can run. The planner
verdict is preserved, but only safe requests receive executable authoring steps.
Review and blocked requests remain dry-run manifests with reasons and required
reinforcement.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import bp_authoring_planner as planner
import external_project_readiness_analyzer as base


MANIFEST_VERSION = "section_39_bp_authoring_job_contract_v28"
DEFAULT_TEMP_PACKAGE_PATH = "/Game/_MCP_Temp/PlannerDrivenSmoke"

AUTHORING_COMMANDS = {
    "add_component_to_blueprint",
    "set_static_mesh_properties",
    "set_component_property",
    "add_blueprint_variable",
    "add_blueprint_event_node",
    "add_blueprint_branch_node",
    "add_blueprint_call_function_node",
    "resolve_blueprint_graph",
    "add_blueprint_function_parameter",
    "add_blueprint_local_variable",
    "add_blueprint_variable_get_node",
    "add_blueprint_variable_set_node",
    "add_blueprint_self_reference",
    "add_blueprint_math_node",
    "add_blueprint_compare_node",
    "add_blueprint_return_node",
    "set_blueprint_pin_default",
    "connect_blueprint_nodes",
    "add_blueprint_event_dispatcher",
    "add_blueprint_event_dispatcher_call_node",
    "add_blueprint_custom_event_node",
    "add_blueprint_event_dispatcher_bind_node",
    "add_blueprint_event_dispatcher_assign_node",
    "add_blueprint_event_dispatcher_unbind_node",
    "add_blueprint_event_dispatcher_clear_node",
}

VALIDATION_COMMANDS = {
    "list_blueprint_graphs",
    "list_blueprint_nodes",
    "list_blueprint_components",
    "get_component_property",
    "compile_and_validate_blueprint",
}

SUPPORTED_EXECUTABLE_SAFE_RULE_KEYS = {
    "blueprint_shell",
    "component_setup",
    "variables_defaults",
    "function_graph_glue",
    "event_dispatcher_lifecycle",
}

PARENT_CLASS_ALLOWLIST: Tuple[Dict[str, Any], ...] = (
    {
        "id": "actor_blueprint_actor_parent",
        "blueprint_kind": "actor_blueprint",
        "parent_class": "Actor",
        "reason": "Section 31 live authoring has validated only Actor Blueprint shells as executable parent-class output.",
    },
)

COMPONENT_PROPERTY_ALLOWLIST: Tuple[Dict[str, Any], ...] = (
    {
        "id": "static_mesh_component_bvisible",
        "component_type": "StaticMeshComponent",
        "property_name": "bVisible",
        "value_type": "bool",
        "supported_values": [True, False],
        "request_patterns": (
            r"\bbvisible\s+(true|false)\b",
            r"\bvisible\s+(true|false)\b",
            r"\bvisibility\s+(true|false)\b",
        ),
    },
)

DURABLE_PACKAGE_PATH_ALLOWLIST: Tuple[str, ...] = (
    "/Game/Blueprints",
    "/Game/MCPGenerated",
)

DEFAULT_SAMPLE_REQUESTS: Tuple[Tuple[str, str], ...] = (
    (
        "safe_actor_shell",
        "Create an Actor Blueprint shell with a Static Mesh Component, exposed health variable, BeginPlay event, and branch.",
    ),
    (
        "safe_function_call_defaults",
        "Create an Actor Blueprint shell with a Static Mesh Component using the Engine cube mesh, float speed variable default 450, BeginPlay branch, and PrintString function call.",
    ),
    (
        "safe_component_hierarchy",
        "Create an Actor Blueprint shell with a Scene Component root named PlannerSmokeRoot and a child Static Mesh Component named PlannerSmokeMesh attached to PlannerSmokeRoot, plus BeginPlay branch.",
    ),
    (
        "safe_component_property_defaults",
        "Create an Actor Blueprint shell with a Static Mesh Component visibility false and BeginPlay branch.",
    ),
    (
        "review_component_property_unsupported",
        "Create an Actor Blueprint shell with a Static Mesh Component component property CastShadow false.",
    ),
    (
        "review_parent_class_unsupported",
        "Create a Character Blueprint shell with a Static Mesh Component and BeginPlay branch.",
    ),
    (
        "review_durable_authoring_save_requested",
        "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints with a Static Mesh Component and BeginPlay branch.",
    ),
    (
        "safe_function_graph_authoring",
        "Create an Actor Blueprint shell with a function graph named ComputePlannerValue, int input InputValue default 3, int output ResultValue default 7, and a return node.",
    ),
    (
        "safe_function_graph_body_math",
        "Create an Actor Blueprint shell with a function graph named ComputePlannerBody, double local variable LocalValue default 5, an add math node using LocalValue plus 2, double output ResultValue, connect the math result to the return node, and compile.",
    ),
    (
        "safe_function_graph_local_set",
        "Create an Actor Blueprint shell with a function graph named ComputePlannerLocalSet, double input InputValue default 3, double local variable AccumulatedValue default 0, add 2 to InputValue, set AccumulatedValue from the math result, then return AccumulatedValue as ResultValue.",
    ),
    (
        "safe_function_graph_compare_branch",
        "Create an Actor Blueprint shell with a function graph named ComputePlannerBranch, double input InputValue default 3, double output ResultValue default 0, double local variable BranchResult default 0, compare InputValue greater than 10, branch on the comparison, set BranchResult to 1 on then and -1 on else, then return BranchResult as ResultValue.",
    ),
    (
        "safe_typed_variables_defaults",
        "Create an Actor Blueprint shell with a Scene Component transform default, bool variable bPlannerEnabled default true, string variable PlannerLabel default Section22, and vector variable PlannerOffset default X=10 Y=20 Z=30.",
    ),
    (
        "safe_event_sequence_flow",
        "Create an Actor Blueprint shell with BeginPlay, a Sequence node with two outputs, and two PrintString calls for the first and second sequence outputs.",
    ),
    (
        "safe_generated_function_invocation",
        "Create an Actor Blueprint shell with BeginPlay, a function graph named ComputePlannerInvocation, double input AddendValue default 2, double local variable LocalValue default 5, an add math node returning ResultValue, then call the generated function from BeginPlay with AddendValue default 2 and store the ResultValue output in double variable LastInvocationResult default 0.",
    ),
    (
        "safe_event_dispatcher",
        "Create a Blueprint Event Dispatcher, call it, bind it to a compatible custom event, assign it, unbind it, and clear it.",
    ),
    (
        "review_umg_button",
        "Create a UMG button click event graph for a UserWidget.",
    ),
    (
        "blocked_async_proxy",
        "Convert a UBlueprintAsyncActionBase async action with callback exec pins, Activate(), Broadcast(), and cancellation cleanup.",
    ),
    (
        "blocked_gas_replication",
        "Build a Gameplay Ability with AbilityTask prediction and replicated Server RPC state changes.",
    ),
    (
        "blocked_commonui",
        "Create a CommonUI activatable widget tree with layer activation policy and back handling.",
    ),
)


def repo_root_from_script() -> Path:
    return base.repo_root_from_script()


def slugify_identifier(value: str) -> str:
    slug = re.sub(r"[^A-Za-z0-9_]+", "_", value.strip())
    slug = re.sub(r"_+", "_", slug).strip("_")
    return slug or "request"


def request_has_typed_variables_defaults(request_text: str) -> bool:
    return bool(
        re.search(
            r"\b(bplannerenabled|plannerlabel|planneroffset|typed variable|bool variable|string variable|vector variable)\b",
            request_text,
            re.IGNORECASE,
        )
    )


def request_has_component_hierarchy(request_text: str) -> bool:
    return bool(
        re.search(
            r"\b(child static mesh component|attached to|attach(ed)? under|component hierarchy|scene component root)\b",
            request_text,
            re.IGNORECASE,
        )
    )


def parent_class_allowlist_entries() -> List[Dict[str, Any]]:
    return [
        {
            "id": entry["id"],
            "blueprint_kind": entry["blueprint_kind"],
            "parent_class": entry["parent_class"],
            "reason": entry["reason"],
        }
        for entry in PARENT_CLASS_ALLOWLIST
    ]


def parent_class_is_allowlisted(blueprint_kind: str, parent_class: str) -> bool:
    return any(
        entry["blueprint_kind"] == blueprint_kind and entry["parent_class"].lower() == parent_class.lower()
        for entry in PARENT_CLASS_ALLOWLIST
    )


def build_parent_class_contract(blueprint_kind: str, parent_class: str) -> Dict[str, Any]:
    executable_allowed = parent_class_is_allowlisted(blueprint_kind, parent_class)
    return {
        "id": "parent_class_allowlist_boundary",
        "schema": "section_31_parent_class_allowlist_contract_v1",
        "blueprint_kind": blueprint_kind,
        "requested_parent_class": parent_class,
        "executable_allowed": executable_allowed,
        "allowlist": parent_class_allowlist_entries(),
        "required_reinforcement": []
        if executable_allowed
        else [
            "add the requested parent class to the Section 31 allowlist",
            "prove parent-specific component, graph, compile, and cleanup behavior",
            "rerun job contract and planner-driven live smoke",
        ],
    }


def durable_package_path_allowlist_entries() -> List[str]:
    return list(DURABLE_PACKAGE_PATH_ALLOWLIST)


def request_mentions_durable_authoring(request_text: str) -> bool:
    return bool(
        re.search(
            r"\b(save|saved|durable|permanent|persist(ent)?|real asset|under\s+/game|in\s+/game|to\s+/game)\b",
            request_text,
            re.IGNORECASE,
        )
    )


def requested_durable_package_path(request_text: str) -> str:
    match = re.search(r"\b(?:in|under|to|at)\s+(/Game/[A-Za-z0-9_/\-]+)", request_text, re.IGNORECASE)
    return match.group(1).rstrip(".,;:") if match else ""


def requested_durable_blueprint_name(request_id: str, request_text: str) -> str:
    match = re.search(r"\b(?:named|called)\s+([A-Za-z_][A-Za-z0-9_]*)\b", request_text, re.IGNORECASE)
    if match:
        return match.group(1)
    return f"BP_{slugify_identifier(request_id)}"


def durable_package_path_is_allowlisted(package_path: str) -> bool:
    normalized = package_path.rstrip("/")
    return any(normalized == allowed or normalized.startswith(f"{allowed}/") for allowed in DURABLE_PACKAGE_PATH_ALLOWLIST)


def build_durable_target_asset_path(package_path: str, blueprint_name: str) -> str:
    if not package_path or not blueprint_name:
        return ""
    return f"{package_path.rstrip('/')}/{blueprint_name}"


def request_mentions_overwrite_decision(request_text: str) -> bool:
    return bool(re.search(r"\b(overwrite|replace|update existing|resave)\b", request_text, re.IGNORECASE))


def request_mentions_rename_decision(request_text: str) -> bool:
    return bool(
        re.search(
            r"\b(create unique|unique name|auto[-\s]?rename|rename if exists|new name if exists)\b",
            request_text,
            re.IGNORECASE,
        )
    )


def build_overwrite_rename_decision_contract(
    requested: bool,
    request_text: str,
    target_asset_path: str,
) -> Dict[str, Any]:
    overwrite_present = request_mentions_overwrite_decision(request_text) if requested else False
    rename_present = request_mentions_rename_decision(request_text) if requested else False
    decision_required = requested and bool(target_asset_path)
    decision_conflict = overwrite_present and rename_present
    if not decision_required:
        decision = "not_required"
    elif decision_conflict:
        decision = "conflicting_decisions"
    elif overwrite_present:
        decision = "overwrite_existing"
    elif rename_present:
        decision = "rename_if_exists"
    else:
        decision = "missing"
    decision_present = decision in {"overwrite_existing", "rename_if_exists"}
    return {
        "id": "durable_overwrite_rename_decision",
        "schema": "section_36_overwrite_rename_decision_contract_v1",
        "decision_required": decision_required,
        "decision_present": decision_present,
        "decision": decision,
        "target_asset_path": target_asset_path,
        "overwrite_requested": overwrite_present,
        "rename_if_exists_requested": rename_present,
        "decision_conflict": decision_conflict,
        "overwrite_allowed": False,
        "rename_if_exists_allowed": False,
        "executor_may_resolve_conflict": False,
        "required_reinforcement": []
        if not decision_required
        else (
            ["choose exactly one durable conflict policy: overwrite_existing or rename_if_exists"]
            if decision == "missing"
            else (
                ["remove the conflicting durable overwrite/rename policy before authoring"]
                if decision_conflict
                else ["add durable executor save and rollback policy before applying this decision"]
            )
        ),
    }


def build_durable_rollback_policy_contract(requested: bool, target_asset_path: str) -> Dict[str, Any]:
    return {
        "id": "durable_rollback_policy",
        "schema": "section_37_durable_rollback_policy_contract_v1",
        "requested": requested,
        "target_asset_path": target_asset_path,
        "policy_mode": "draft_only",
        "rollback_policy_ready": False,
        "rollback_allowed": False,
        "delete_created_asset_on_failure": False,
        "delete_created_asset_on_cancel": False,
        "delete_existing_asset_allowed": False,
        "overwrite_existing_asset_allowed": False,
        "keep_failed_draft_allowed": False,
        "requires_executor_created_asset_marker": requested,
        "protects_preexisting_assets": True,
        "allowed_delete_scope": "none until durable executor records created asset ownership",
        "required_reinforcement": []
        if not requested
        else [
            "define durable executor ownership markers for newly created assets",
            "define rollback behavior for create failure, compile failure, save failure, and cancellation",
            "prove preexisting assets cannot be deleted or overwritten without explicit policy",
        ],
    }


def build_durable_save_gate_contract(
    requested: bool,
    package_path_allowed: bool,
    asset_exists_check_required: bool,
    decision_contract: Dict[str, Any],
    rollback_policy_contract: Dict[str, Any],
) -> Dict[str, Any]:
    prerequisites = {
        "durable_executor_enabled": False,
        "target_package_path_allowed": package_path_allowed,
        "asset_exists_check_required": asset_exists_check_required,
        "asset_exists_result_available_in_manifest": False,
        "overwrite_or_rename_decision_present": decision_contract["decision_present"],
        "overwrite_or_rename_decision_conflict_free": not decision_contract["decision_conflict"],
        "rollback_policy_ready": rollback_policy_contract["rollback_policy_ready"],
        "durable_compile_save_validation_enabled": False,
    }
    blocked_by = []
    if requested:
        if not prerequisites["durable_executor_enabled"]:
            blocked_by.append("durable_executor_disabled")
        if not prerequisites["target_package_path_allowed"]:
            blocked_by.append("target_package_path_not_allowlisted")
        if prerequisites["asset_exists_check_required"] and not prerequisites["asset_exists_result_available_in_manifest"]:
            blocked_by.append("asset_exists_result_missing")
        if not prerequisites["overwrite_or_rename_decision_present"]:
            blocked_by.append(f"overwrite_rename_decision_{decision_contract['decision']}")
        if not prerequisites["overwrite_or_rename_decision_conflict_free"]:
            blocked_by.append("overwrite_rename_decision_conflict")
        if not prerequisites["rollback_policy_ready"]:
            blocked_by.append("rollback_policy_not_ready")
        if not prerequisites["durable_compile_save_validation_enabled"]:
            blocked_by.append("durable_compile_save_validation_not_enabled")
    save_allowed = requested and not blocked_by
    return {
        "id": "durable_save_gate",
        "schema": "section_37_durable_save_gate_contract_v1",
        "requested": requested,
        "save_requested": requested,
        "save_allowed": save_allowed,
        "compile_save_allowed": False,
        "temporary_smoke_may_save": False,
        "preflight_pass": False,
        "prerequisites": prerequisites,
        "blocked_by": blocked_by,
        "required_reinforcement": []
        if not requested
        else [
            "enable a durable executor separate from temporary smoke",
            "promote live read-only asset-exists result into the durable save gate",
            "require a conflict-free overwrite/rename decision",
            "make rollback policy ready before allowing save=true validation",
        ],
    }


def build_readiness_check(check_id: str, label: str, passed: bool, required: bool = True) -> Dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "required": required,
        "passed": passed,
    }


def build_durable_executor_readiness_contract(
    requested: bool,
    package_path_allowed: bool,
    decision_contract: Dict[str, Any],
    save_gate_contract: Dict[str, Any],
    rollback_policy_contract: Dict[str, Any],
) -> Dict[str, Any]:
    checks = [
        build_readiness_check("target_package_path_allowlisted", "Target package path is allowlisted", package_path_allowed),
        build_readiness_check(
            "live_asset_exists_result_promoted",
            "Live read-only asset-exists result is promoted into the durable save gate",
            False,
        ),
        build_readiness_check(
            "conflict_resolution_decision_present",
            "Overwrite or rename-if-exists decision is present",
            decision_contract["decision_present"],
        ),
        build_readiness_check(
            "conflict_resolution_decision_conflict_free",
            "Overwrite or rename-if-exists decision is conflict-free",
            not decision_contract["decision_conflict"],
        ),
        build_readiness_check("save_gate_allows_save", "Durable save gate allows save", save_gate_contract["save_allowed"]),
        build_readiness_check(
            "rollback_policy_ready",
            "Rollback policy is ready and protects preexisting assets",
            rollback_policy_contract["rollback_policy_ready"],
        ),
        build_readiness_check(
            "durable_compile_save_validation_enabled",
            "Durable compile and save validation is enabled",
            save_gate_contract["prerequisites"]["durable_compile_save_validation_enabled"],
        ),
        build_readiness_check(
            "executor_created_asset_marker_policy_ready",
            "Durable executor created-asset ownership marker policy is ready",
            False,
        ),
        build_readiness_check("explicit_durable_executor_enable_flag", "Explicit durable executor enable flag is set", False),
    ]
    failing_checks = [check["id"] for check in checks if check["required"] and not check["passed"]]
    ready = requested and not failing_checks
    return {
        "id": "durable_executor_readiness",
        "schema": "section_38_durable_executor_readiness_contract_v1",
        "requested": requested,
        "enablement_mode": "disabled",
        "durable_executor_ready": ready,
        "readiness_level": "ready" if ready else "not_ready",
        "checks": checks,
        "failing_checks": failing_checks,
        "required_reinforcement": []
        if not requested
        else [
            "satisfy all Section 38 durable executor readiness checks",
            "require an explicit durable executor enable flag before save execution",
            "rerun offline tests and planner-driven live smoke before enabling durable save",
        ],
    }


def build_durable_executor_skeleton_contract(
    requested: bool,
    preflight_schema: str,
    save_gate_contract: Dict[str, Any],
    rollback_policy_contract: Dict[str, Any],
    readiness_contract: Dict[str, Any],
) -> Dict[str, Any]:
    readiness_failures = list(readiness_contract.get("failing_checks", []))
    disabled_by = []
    if requested:
        disabled_by = ["durable_executor_skeleton_disabled"]
        disabled_by.extend(readiness_failures)
    return {
        "id": "durable_executor_skeleton",
        "schema": "section_39_durable_executor_skeleton_contract_v1",
        "requested": requested,
        "skeleton_defined": requested,
        "executor_mode": "disabled_skeleton" if requested else "not_requested",
        "executor_enabled": False,
        "can_execute": False,
        "command_plan": [],
        "authoring_commands_allowed": False,
        "save_commands_allowed": False,
        "delete_commands_allowed": False,
        "rename_commands_allowed": False,
        "allowed_live_command_count": 0,
        "input_contracts": [
            preflight_schema,
            save_gate_contract["schema"],
            rollback_policy_contract["schema"],
            readiness_contract["schema"],
        ],
        "required_manifest_inputs": [
            "durable_preflight_contract",
            "durable_save_gate_contract",
            "durable_rollback_policy_contract",
            "durable_executor_readiness_contract",
        ],
        "planned_output_fields": [
            "created_asset_path",
            "asset_exists_before_authoring",
            "conflict_resolution_decision",
            "compile_validation_result",
            "save_result",
            "rollback_result",
            "failure_diagnostics",
        ],
        "forbidden_commands": [
            "create_blueprint",
            "compile_and_validate_blueprint(save=true)",
            "save_asset",
            "delete_asset",
            "rename_asset",
            "duplicate_asset",
            "replace_existing_asset",
        ],
        "disabled_by": disabled_by,
        "required_reinforcement": []
        if not requested
        else [
            "keep the skeleton disabled until Section 38 readiness passes",
            "add an explicit durable executor enable flag before command_plan may contain commands",
            "prove the enabled executor with offline tests before any live durable save",
        ],
    }


def build_durable_preflight_contract(
    requested: bool,
    request_text: str,
    package_path: str,
    blueprint_name: str,
    package_path_allowed: bool,
) -> Dict[str, Any]:
    target_asset_path = build_durable_target_asset_path(package_path, blueprint_name)
    overwrite_decision_present = request_mentions_overwrite_decision(request_text) if requested else False
    rename_decision_present = request_mentions_rename_decision(request_text) if requested else False
    overwrite_rename_decision_contract = build_overwrite_rename_decision_contract(requested, request_text, target_asset_path)
    rollback_policy_contract = build_durable_rollback_policy_contract(requested, target_asset_path)
    asset_exists_check_required = requested and bool(target_asset_path)
    overwrite_decision_required = requested and bool(target_asset_path)
    save_gate_contract = build_durable_save_gate_contract(
        requested,
        package_path_allowed,
        asset_exists_check_required,
        overwrite_rename_decision_contract,
        rollback_policy_contract,
    )
    readiness_contract = build_durable_executor_readiness_contract(
        requested,
        package_path_allowed,
        overwrite_rename_decision_contract,
        save_gate_contract,
        rollback_policy_contract,
    )
    executor_skeleton_contract = build_durable_executor_skeleton_contract(
        requested,
        "section_39_durable_preflight_contract_v1",
        save_gate_contract,
        rollback_policy_contract,
        readiness_contract,
    )
    save_gate_passed = False
    preflight_pass = (
        requested
        and package_path_allowed
        and asset_exists_check_required
        and overwrite_rename_decision_contract["decision_present"]
        and save_gate_passed
    )
    return {
        "id": "durable_preflight_dry_run_boundary",
        "schema": "section_39_durable_preflight_contract_v1",
        "requested": requested,
        "dry_run_only": True,
        "target_package_path": package_path,
        "target_blueprint_name": blueprint_name,
        "target_asset_path": target_asset_path,
        "package_path_allowed": package_path_allowed,
        "asset_exists_check_required": asset_exists_check_required,
        "asset_exists_check_performed": False,
        "asset_exists_check_command": "unreal.EditorAssetLibrary.does_asset_exist",
        "asset_exists_check_scope": "read_only_live_preflight",
        "asset_exists_live_result_schema": "section_35_durable_preflight_live_result_v1",
        "asset_exists": None,
        "overwrite_decision_required": overwrite_decision_required,
        "overwrite_decision_present": overwrite_decision_present,
        "rename_decision_present": rename_decision_present,
        "overwrite_rename_decision_contract": overwrite_rename_decision_contract,
        "durable_save_gate_contract": save_gate_contract,
        "durable_rollback_policy_contract": rollback_policy_contract,
        "durable_executor_readiness_contract": readiness_contract,
        "durable_executor_skeleton_contract": executor_skeleton_contract,
        "save_gate_required": requested,
        "save_gate_passed": save_gate_passed,
        "preflight_pass": preflight_pass,
        "live_read_only_check_allowed": requested and bool(target_asset_path),
        "required_reinforcement": []
        if not requested
        else [
            "perform a read-only target asset existence check before durable authoring",
            "require an explicit overwrite or rename-if-exists decision",
            "require a durable save gate separate from temporary smoke",
            "record the preflight result before any durable authoring command runs",
        ],
    }


def build_durable_authoring_contract(
    request_id: str,
    request_text: str,
    blueprint_kind: str,
    parent_class: str,
) -> Dict[str, Any]:
    requested = request_mentions_durable_authoring(request_text)
    package_path = requested_durable_package_path(request_text)
    blueprint_name = requested_durable_blueprint_name(request_id, request_text) if requested else ""
    package_path_allowed = durable_package_path_is_allowlisted(package_path) if package_path else False
    preflight_contract = build_durable_preflight_contract(
        requested,
        request_text,
        package_path,
        blueprint_name,
        package_path_allowed,
    )
    return {
        "id": "durable_authoring_boundary",
        "schema": "section_39_durable_authoring_contract_v1",
        "requested": requested,
        "blueprint_kind": blueprint_kind,
        "parent_class": parent_class,
        "requested_blueprint_name": blueprint_name,
        "requested_package_path": package_path,
        "package_path_allowlist": durable_package_path_allowlist_entries(),
        "package_path_allowed": package_path_allowed,
        "durable_executor_enabled": False,
        "durable_authoring_eligible": False,
        "save_allowed": False,
        "temporary_smoke_may_save": False,
        "durable_preflight_contract": preflight_contract,
        "overwrite_policy": "requires_explicit_review",
        "preflight_required": [
            "asset_exists_check",
            "target_package_path_allowlist_check",
            "overwrite_or_rename_decision",
            "save_gate_review",
        ],
        "rollback_boundary": {
            "delete_on_failure": "requires_explicit_policy",
            "keep_draft_on_failure": "requires_explicit_policy",
            "allowed_delete_scope": "only assets created by the durable executor after preflight",
        },
        "required_reinforcement": []
        if not requested
        else [
            "implement a durable executor separate from temporary smoke",
            "keep the Section 39 durable executor skeleton disabled until readiness passes",
            "satisfy the Section 38 durable executor readiness checklist",
            "promote the Section 37 save gate and rollback contracts into a durable executor gate",
            "add durable overwrite/rename policy application and rollback boundary",
            "add save=true validation for durable-only manifests",
            "rerun offline tests and live smoke without creating durable assets",
        ],
    }


def build_authoring_executor_contract(
    executable: bool,
    temp_package_path: str,
    durable_authoring_contract: Dict[str, Any],
) -> Dict[str, Any]:
    return {
        "schema": "section_39_authoring_executor_contract_v1",
        "live_executor": "temporary_smoke",
        "temporary_smoke": {
            "executable": executable,
            "package_path": temp_package_path,
            "compile_save": False,
            "cleanup_required": True,
            "durable_asset_creation_allowed": False,
        },
        "durable_authoring": durable_authoring_contract,
        "durable_preflight": durable_authoring_contract["durable_preflight_contract"],
        "durable_save_gate": durable_authoring_contract["durable_preflight_contract"]["durable_save_gate_contract"],
        "durable_rollback_policy": durable_authoring_contract["durable_preflight_contract"]["durable_rollback_policy_contract"],
        "durable_executor_readiness": durable_authoring_contract["durable_preflight_contract"][
            "durable_executor_readiness_contract"
        ],
        "durable_executor_skeleton": durable_authoring_contract["durable_preflight_contract"][
            "durable_executor_skeleton_contract"
        ],
    }


def component_property_allowlist_entries() -> List[Dict[str, Any]]:
    return [
        {
            "id": entry["id"],
            "component_type": entry["component_type"],
            "property_name": entry["property_name"],
            "value_type": entry["value_type"],
            "supported_values": list(entry["supported_values"]),
        }
        for entry in COMPONENT_PROPERTY_ALLOWLIST
    ]


def request_mentions_component_property_default(request_text: str) -> bool:
    return bool(
        re.search(
            r"\b(component property|component default|bvisible|visible|visibility|castshadow|cast shadow|mobility|collision)\b",
            request_text,
            re.IGNORECASE,
        )
    )


def parse_bool_text(value: str) -> bool:
    return value.lower() == "true"


def allowed_component_property_request(request_text: str, component_type: str) -> Optional[Dict[str, Any]]:
    for entry in COMPONENT_PROPERTY_ALLOWLIST:
        if entry["component_type"] != component_type:
            continue
        for pattern in entry["request_patterns"]:
            match = re.search(pattern, request_text, re.IGNORECASE)
            if not match:
                continue
            value = parse_bool_text(match.group(1))
            if value not in entry["supported_values"]:
                return None
            return {
                "allowlist_id": entry["id"],
                "component_type": entry["component_type"],
                "property_name": entry["property_name"],
                "property_value": value,
                "value_type": entry["value_type"],
            }
    return None


def infer_blueprint_kind(request_text: str, plan: Dict[str, Any]) -> str:
    text = request_text.lower()
    if "commonui" in text or "activatable widget" in text:
        return "commonui_widget_blueprint"
    if "umg" in text or "userwidget" in text or "widget blueprint" in text:
        return "widget_blueprint"
    if "gameplay ability" in text or "abilitytask" in text or "ability task" in text:
        return "gameplay_ability_blueprint"
    if "animation blueprint" in text or "anim blueprint" in text or "animbp" in text:
        return "animation_blueprint"
    if "component blueprint" in text or "actorcomponent" in text:
        return "component_blueprint"
    if any(step["key"] == "event_dispatcher_lifecycle" for step in plan.get("safe_steps", [])):
        return "actor_blueprint"
    if "pawn" in text:
        return "pawn_blueprint"
    if "character" in text:
        return "character_blueprint"
    return "actor_blueprint" if plan.get("status") == planner.STATUS_SAFE else "unknown_blueprint"


def infer_parent_class(request_text: str, blueprint_kind: str, target_class: str = "") -> str:
    if target_class:
        return target_class
    text = request_text.lower()
    if blueprint_kind == "widget_blueprint":
        return "UserWidget"
    if blueprint_kind == "commonui_widget_blueprint":
        return "CommonActivatableWidget"
    if blueprint_kind == "gameplay_ability_blueprint":
        return "GameplayAbility"
    if blueprint_kind == "animation_blueprint":
        return "AnimInstance"
    if blueprint_kind == "component_blueprint":
        return "ActorComponent"
    if "character" in text:
        return "Character"
    if "pawn" in text:
        return "Pawn"
    return "Actor" if blueprint_kind == "actor_blueprint" else ""


def build_component_list(plan: Dict[str, Any], request_text: str) -> List[Dict[str, Any]]:
    safe_keys = {step["key"] for step in plan.get("safe_steps", [])}
    text = request_text.lower()
    if "component_setup" not in safe_keys and "static mesh component" not in text and "scene component" not in text:
        return []
    if "static mesh component" not in text and "scene component" not in text:
        return []

    if request_has_component_hierarchy(request_text):
        return [
            {
                "id": "component_root",
                "label": "Hierarchy root scene component",
                "command": "add_component_to_blueprint",
                "component_type": "SceneComponent",
                "component_name": "PlannerSmokeRoot",
                "transform": {
                    "location": [0, 0, 0],
                    "rotation": [0, 0, 0],
                    "scale": [1, 1, 1],
                },
            },
            {
                "id": "component_child_mesh",
                "label": "Hierarchy child static mesh component",
                "command": "add_component_to_blueprint",
                "component_type": "StaticMeshComponent",
                "component_name": "PlannerSmokeMesh",
                "parent_component_name": "PlannerSmokeRoot",
                "transform": {
                    "location": [100, 0, 0],
                    "rotation": [0, 0, 0],
                    "scale": [1, 1, 1],
                },
            },
        ]

    component_type = "SceneComponent" if "scene component" in text and "static mesh component" not in text else "StaticMeshComponent"
    component_name = "TypedDefaultsRoot" if request_has_typed_variables_defaults(request_text) else (
        "PlannerSmokeRoot" if component_type == "SceneComponent" else "PlannerSmokeMesh"
    )
    transform = (
        {
            "location": [10, 20, 30],
            "rotation": [0, 45, 0],
            "scale": [1, 2, 1],
        }
        if request_has_typed_variables_defaults(request_text)
        else {
            "location": [0, 0, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1],
        }
    )
    return [
        {
            "id": "component_primary",
            "label": "Primary safe component",
            "command": "add_component_to_blueprint",
            "component_type": component_type,
            "component_name": component_name,
            "transform": transform,
        }
    ]


def build_component_default_steps(component_list: Sequence[Dict[str, Any]], request_text: str) -> List[Dict[str, Any]]:
    text = request_text.lower()
    if not component_list:
        return []

    primary_component = component_list[0]
    steps: List[Dict[str, Any]] = []
    if primary_component["component_type"] == "StaticMeshComponent" and ("cube mesh" in text or "engine cube" in text):
        steps.append(
            {
                "id": "component_static_mesh_default",
                "label": "Static mesh default",
                "command": "set_static_mesh_properties",
                "component_name": primary_component["component_name"],
                "static_mesh": "/Engine/BasicShapes/Cube.Cube",
            }
        )
    allowed_property = allowed_component_property_request(text, primary_component["component_type"])
    if allowed_property:
        steps.append(
            {
                "id": "component_visibility_default",
                "label": "Component visibility default",
                "command": "set_component_property",
                "component_name": primary_component["component_name"],
                "allowlist_id": allowed_property["allowlist_id"],
                "property_name": allowed_property["property_name"],
                "property_value": allowed_property["property_value"],
            }
        )
    return steps


def build_component_default_contracts(
    component_list: Sequence[Dict[str, Any]],
    component_default_steps: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    contracts: List[Dict[str, Any]] = []
    static_mesh_defaults = {
        step["component_name"]: step.get("static_mesh", "")
        for step in component_default_steps
        if step.get("command") == "set_static_mesh_properties"
    }
    for component in component_list:
        contracts.append(
            {
                "id": f"{component['id']}_defaults_contract",
                "schema": "section_26_component_default_contract_v1",
                "operation": "component_default_contract",
                "source_step": component["id"],
                "component_name": component["component_name"],
                "component_type": component["component_type"],
                "expected_transform": component.get("transform", {}),
                "expected_static_mesh": static_mesh_defaults.get(component["component_name"], ""),
                "validation": [
                    "assert component is listed from Blueprint SCS",
                    "assert component class matches manifest component type",
                    "assert relative transform matches manifest defaults",
                    "assert static mesh default when authored",
                ],
            }
        )
    return contracts


def build_component_hierarchy_contracts(component_list: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    contracts: List[Dict[str, Any]] = []
    component_names = {component.get("component_name", "") for component in component_list}
    for component in component_list:
        parent_component_name = component.get("parent_component_name", "")
        if not parent_component_name:
            continue
        contracts.append(
            {
                "id": f"{component['id']}_hierarchy_contract",
                "schema": "section_28_component_hierarchy_contract_v1",
                "operation": "component_hierarchy_contract",
                "source_step": component["id"],
                "component_name": component["component_name"],
                "expected_parent_component_name": parent_component_name,
                "parent_declared_in_manifest": parent_component_name in component_names,
                "validation": [
                    "assert child component is listed from Blueprint SCS",
                    "assert parent_component_name matches manifest attachment",
                    "assert parent component was declared in the same manifest",
                ],
            }
        )
    return contracts


def build_component_property_contracts(component_default_steps: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    contracts: List[Dict[str, Any]] = []
    for step in component_default_steps:
        if step.get("command") != "set_component_property":
            continue
        contracts.append(
            {
                "id": f"{step['id']}_contract",
                "schema": "section_29_component_property_contract_v1",
                "operation": "component_property_contract",
                "source_step": step["id"],
                "component_name": step["component_name"],
                "allowlist_id": step.get("allowlist_id", ""),
                "property_name": step["property_name"],
                "expected_value": step.get("property_value"),
                "validation": [
                    "assert component property can be re-read after authoring",
                    "assert re-read property value matches manifest value",
                ],
            }
        )
    return contracts


def parse_numeric_default(request_text: str, variable_name: str, fallback: float) -> float:
    pattern = rf"\b{re.escape(variable_name.lower())}\b\s+(?:variable\s+)?(?:default|value)?\s*(?:=|to|of)?\s*(-?\d+(?:\.\d+)?)"
    match = re.search(pattern, request_text.lower())
    if not match:
        match = re.search(r"\bdefault\s+(-?\d+(?:\.\d+)?)", request_text.lower())
    if not match:
        return fallback
    return float(match.group(1))


def build_variables_defaults(plan: Dict[str, Any], request_text: str) -> List[Dict[str, Any]]:
    safe_keys = {step["key"] for step in plan.get("safe_steps", [])}
    text = request_text.lower()
    if "variables_defaults" not in safe_keys and "health variable" not in text:
        return []

    variables: List[Dict[str, Any]] = []
    if request_has_typed_variables_defaults(request_text):
        variables.extend(
            [
                {
                    "id": "variable_planner_enabled",
                    "label": "Explicit bool default",
                    "command": "add_blueprint_variable",
                    "variable_name": "bPlannerEnabled",
                    "variable_type": "bool",
                    "default_value": True,
                    "is_exposed": True,
                    "category": "Planner Smoke",
                    "tooltip": "Section 22 bool default",
                },
                {
                    "id": "variable_planner_label",
                    "label": "Explicit string default",
                    "command": "add_blueprint_variable",
                    "variable_name": "PlannerLabel",
                    "variable_type": "string",
                    "default_value": "Section22",
                    "is_exposed": True,
                    "category": "Planner Smoke",
                    "tooltip": "Section 22 string default",
                },
                {
                    "id": "variable_planner_offset",
                    "label": "Explicit vector default",
                    "command": "add_blueprint_variable",
                    "variable_name": "PlannerOffset",
                    "variable_type": "vector",
                    "default_value": [10, 20, 30],
                    "is_exposed": True,
                    "category": "Planner Smoke",
                    "tooltip": "Section 22 vector default",
                },
            ]
        )
    if "health" in text:
        variables.append(
            {
                "id": "variable_health",
                "label": "Explicit health default",
                "command": "add_blueprint_variable",
                "variable_name": "Health",
                "variable_type": "int",
                "default_value": int(parse_numeric_default(request_text, "health", 100)),
                "category": "Planner Smoke",
            }
        )
    if "speed" in text:
        variables.append(
            {
                "id": "variable_speed",
                "label": "Explicit speed default",
                "command": "add_blueprint_variable",
                "variable_name": "Speed",
                "variable_type": "float",
                "default_value": parse_numeric_default(request_text, "speed", 450.0),
                "category": "Planner Smoke",
            }
        )
    if request_has_generated_function_invocation(request_text):
        variables.append(
            {
                "id": "variable_last_invocation_result",
                "label": "Generated function result sink",
                "command": "add_blueprint_variable",
                "variable_name": "LastInvocationResult",
                "variable_type": "double",
                "default_value": 0.0,
                "category": "Planner Smoke",
            }
        )
    return variables


def request_needs_concrete_function_call(request_text: str) -> bool:
    return bool(re.search(r"\b(function call|call function|printstring|print string)\b", request_text, re.IGNORECASE))


def request_has_supported_function_call(request_text: str) -> bool:
    return bool(re.search(r"\b(printstring|print string)\b", request_text, re.IGNORECASE))


def request_has_function_graph_authoring(request_text: str) -> bool:
    return bool(re.search(r"\bfunction graph\b|\breturn node\b|\boutput\s+\w+\s+default\b", request_text, re.IGNORECASE))


def request_has_function_graph_body_authoring(request_text: str) -> bool:
    return bool(re.search(r"\b(local variable|math node|dataflow)\b", request_text, re.IGNORECASE))


def request_has_function_graph_local_set(request_text: str) -> bool:
    return bool(re.search(r"\b(local variable set|set\s+\w+|set\s+accumulatedvalue|return\s+accumulatedvalue)\b", request_text, re.IGNORECASE))


def request_has_function_graph_compare_branch(request_text: str) -> bool:
    return bool(
        re.search(
            r"\b(compare|greater than|less than|branch on|then and|else)\b",
            request_text,
            re.IGNORECASE,
        )
        and re.search(r"\bfunction graph\b", request_text, re.IGNORECASE)
        and re.search(r"\bbranch\b", request_text, re.IGNORECASE)
    )


def request_has_generated_function_invocation(request_text: str) -> bool:
    return bool(re.search(r"\b(generated function|call the generated function|call generated function|from beginplay)\b", request_text, re.IGNORECASE))


def request_has_event_sequence_flow(request_text: str) -> bool:
    return bool(re.search(r"\b(sequence node|sequence outputs|first sequence|second sequence)\b", request_text, re.IGNORECASE))


def function_graph_name_for_request(request_text: str) -> str:
    match = re.search(r"\bfunction graph named\s+([A-Za-z_][A-Za-z0-9_]*)", request_text, re.IGNORECASE)
    if match:
        return match.group(1)
    if request_has_generated_function_invocation(request_text):
        return "ComputePlannerInvocation"
    if request_has_function_graph_compare_branch(request_text):
        return "ComputePlannerBranch"
    if request_has_function_graph_local_set(request_text):
        return "ComputePlannerLocalSet"
    return "ComputePlannerBody" if request_has_function_graph_body_authoring(request_text) else "ComputePlannerValue"


def build_event_graph_steps(plan: Dict[str, Any], request_text: str) -> List[Dict[str, Any]]:
    safe_keys = {step["key"] for step in plan.get("safe_steps", [])}
    text = request_text.lower()
    has_sequence_flow = request_has_event_sequence_flow(request_text)
    if "function_graph_glue" not in safe_keys and "beginplay" not in text and "branch" not in text and not has_sequence_flow:
        return []
    if request_has_function_graph_authoring(request_text) and "beginplay" not in text:
        return []

    steps: List[Dict[str, Any]] = []
    if "beginplay" in text or "branch" in text or has_sequence_flow:
        steps.append(
            {
                "id": "receive_begin_play",
                "operation": "command",
                "command": "add_blueprint_event_node",
                "params": {
                    "event_name": "ReceiveBeginPlay",
                    "node_position": [0, 0],
                },
                "store_as": "receive_begin_play",
            }
        )
        if has_sequence_flow:
            steps.extend(
                [
                    {
                        "id": "sequence_node",
                        "operation": "command",
                        "command": "add_blueprint_sequence_node",
                        "params": {
                            "output_count": 2,
                            "node_position": [260, 0],
                            "graph_type": "event",
                        },
                        "store_as": "sequence_node",
                    },
                    {
                        "id": "begin_play_to_sequence",
                        "operation": "connect",
                        "source_node_ref": "receive_begin_play",
                        "source_pin_kind": "exec",
                        "source_pin_preferred": ["then"],
                        "target_node_ref": "sequence_node",
                        "target_pin_kind": "exec",
                        "target_pin_preferred": ["execute", "exec"],
                    },
                    {
                        "id": "sequence_first_print_string",
                        "operation": "command",
                        "command": "add_blueprint_call_function_node",
                        "params": {
                            "function_class": "/Script/Engine.KismetSystemLibrary",
                            "function_name": "PrintString",
                            "param_defaults": {
                                "InString": "Planner Sequence First",
                            },
                            "node_position": [560, -120],
                            "graph_type": "event",
                        },
                        "store_as": "sequence_first_print_string",
                    },
                    {
                        "id": "sequence_second_print_string",
                        "operation": "command",
                        "command": "add_blueprint_call_function_node",
                        "params": {
                            "function_class": "/Script/Engine.KismetSystemLibrary",
                            "function_name": "PrintString",
                            "param_defaults": {
                                "InString": "Planner Sequence Second",
                            },
                            "node_position": [560, 160],
                            "graph_type": "event",
                        },
                        "store_as": "sequence_second_print_string",
                    },
                    {
                        "id": "sequence_then_0_to_first_print",
                        "operation": "connect",
                        "source_node_ref": "sequence_node",
                        "source_pin_kind": "exec",
                        "source_pin_preferred": ["then_0", "then 0", "then0"],
                        "target_node_ref": "sequence_first_print_string",
                        "target_pin_kind": "exec",
                        "target_pin_preferred": ["execute", "exec"],
                    },
                    {
                        "id": "sequence_then_1_to_second_print",
                        "operation": "connect",
                        "source_node_ref": "sequence_node",
                        "source_pin_kind": "exec",
                        "source_pin_preferred": ["then_1", "then 1", "then1"],
                        "target_node_ref": "sequence_second_print_string",
                        "target_pin_kind": "exec",
                        "target_pin_preferred": ["execute", "exec"],
                    },
                ]
            )
            return steps
        steps.extend(
            [
                {
                    "id": "branch",
                    "operation": "command",
                    "command": "add_blueprint_branch_node",
                    "params": {
                        "node_position": [260, 0],
                    },
                    "store_as": "branch",
                },
                {
                    "id": "branch_condition_default",
                    "operation": "set_pin_default",
                    "node_ref": "branch",
                    "pin_name": "Condition",
                    "value": True,
                    "direction": "input",
                },
                {
                    "id": "begin_play_to_branch",
                    "operation": "connect",
                    "source_node_ref": "receive_begin_play",
                    "source_pin_kind": "exec",
                    "source_pin_preferred": ["then"],
                    "target_node_ref": "branch",
                    "target_pin_kind": "exec",
                    "target_pin_preferred": ["execute", "exec"],
                },
            ]
        )
    if request_has_supported_function_call(request_text):
        steps.append(
            {
                "id": "print_string_call",
                "operation": "command",
                "command": "add_blueprint_call_function_node",
                "params": {
                    "function_class": "/Script/Engine.KismetSystemLibrary",
                    "function_name": "PrintString",
                    "param_defaults": {
                        "InString": "Planner Smoke",
                    },
                    "node_position": [520, 0],
                    "graph_type": "event",
                },
                "store_as": "print_string_call",
            }
        )
        if any(step["id"] == "branch" for step in steps):
            steps.append(
                {
                    "id": "branch_true_to_print_string",
                    "operation": "connect",
                    "source_node_ref": "branch",
                    "source_pin_kind": "exec",
                    "source_pin_preferred": ["true"],
                    "target_node_ref": "print_string_call",
                    "target_pin_kind": "exec",
                    "target_pin_preferred": ["execute", "exec"],
                }
            )
    return steps


def contract_specificity_gaps(
    plan: Dict[str, Any],
    parent_class_contract: Dict[str, Any],
    durable_authoring_contract: Dict[str, Any],
    component_list: Sequence[Dict[str, Any]],
    variables_defaults: Sequence[Dict[str, Any]],
    event_graph_steps: Sequence[Dict[str, Any]],
    dispatcher_lifecycle_steps: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if plan["status"] != planner.STATUS_SAFE:
        return []

    safe_keys = {step["key"] for step in plan.get("safe_steps", [])}
    gaps: List[Dict[str, Any]] = []
    if not parent_class_contract["executable_allowed"]:
        gaps.append(
            {
                "status": planner.STATUS_REVIEW,
                "key": "contract_unsupported_parent_class",
                "label": "Parent class outside Section 31 allowlist",
                "reason": (
                    f"Parent class `{parent_class_contract['requested_parent_class']}` for "
                    f"`{parent_class_contract['blueprint_kind']}` is not in the Section 31 executable allowlist."
                ),
                "required_before_authoring": parent_class_contract["required_reinforcement"],
            }
        )
    if durable_authoring_contract["requested"]:
        gaps.append(
            {
                "status": planner.STATUS_REVIEW,
                "key": "contract_durable_executor_not_enabled",
                "label": "Durable authoring executor contract missing",
                "reason": (
                    "The request asks for a saved or durable Blueprint asset, but Section 39 only permits "
                    "dry-run durable preflight, read-only live asset-exists checking, overwrite/rename decision "
                    "classification, save-gate/rollback policy drafting, executor-readiness checking, a disabled durable "
                    "executor skeleton, and temporary-smoke execution with save=false until durable save execution is explicitly enabled."
                ),
                "required_before_authoring": durable_authoring_contract["required_reinforcement"],
            }
        )
    unsupported_keys = sorted(safe_keys - SUPPORTED_EXECUTABLE_SAFE_RULE_KEYS)
    for key in unsupported_keys:
        gaps.append(
            {
                "status": planner.STATUS_REVIEW,
                "key": f"contract_executor_missing_{key}",
                "label": "Section 15 executor template missing",
                "reason": f"The planner marked `{key}` safe, but Section 15 has no executable manifest template for that rule yet.",
                "required_before_authoring": [f"add Section 15 manifest executor support for {key}", "rerun job contract smoke"],
            }
        )

    if "component_setup" in safe_keys and not component_list:
        gaps.append(
            {
                "status": planner.STATUS_REVIEW,
                "key": "contract_missing_component_specificity",
                "label": "Component type missing",
                "reason": "Component setup needs an explicit component type before live authoring.",
                "required_before_authoring": ["specify component type", "rerun job contract smoke"],
            }
        )
    component_property_requested = request_mentions_component_property_default(plan["request"])
    component_property_step_count = sum(
        1
        for step in build_component_default_steps(component_list, plan["request"])
        if step.get("command") == "set_component_property"
    )
    if component_property_requested and component_property_step_count == 0:
        gaps.append(
            {
                "status": planner.STATUS_REVIEW,
                "key": "contract_unsupported_component_property",
                "label": "Component property outside Section 30 allowlist",
                "reason": "Component property authoring is executable only for allowlisted properties with post-authoring introspection.",
                "required_before_authoring": [
                    "add the requested component property to the Section 30 allowlist",
                    "add get_component_property validation for the property type",
                    "rerun job contract and planner-driven live smoke",
                ],
            }
        )
    if (
        "variables_defaults" in safe_keys
        and not variables_defaults
        and not request_has_function_graph_body_authoring(plan["request"])
        and not component_property_requested
    ):
        gaps.append(
            {
                "status": planner.STATUS_REVIEW,
                "key": "contract_missing_variable_specificity",
                "label": "Variable metadata missing",
                "reason": "Variable authoring needs explicit variable name, type, and default before live authoring.",
                "required_before_authoring": ["specify variable name/type/default", "rerun job contract smoke"],
            }
        )
    has_function_graph_request = request_has_function_graph_authoring(plan["request"])
    if "function_graph_glue" in safe_keys and not event_graph_steps and not dispatcher_lifecycle_steps and not has_function_graph_request:
        gaps.append(
            {
                "status": planner.STATUS_REVIEW,
                "key": "contract_missing_graph_specificity",
                "label": "Graph topology missing",
                "reason": "Graph glue needs explicit event/function nodes, pins, and connections before live authoring.",
                "required_before_authoring": ["specify graph nodes and connections", "rerun job contract smoke"],
            }
        )
    if (
        request_needs_concrete_function_call(plan["request"])
        and not request_has_generated_function_invocation(plan["request"])
        and not any(step.get("command") == "add_blueprint_call_function_node" for step in event_graph_steps)
    ):
        gaps.append(
            {
                "status": planner.STATUS_REVIEW,
                "key": "contract_missing_function_call_specificity",
                "label": "Concrete safe function call missing",
                "reason": "Function-call authoring needs a specific supported UFunction and pin defaults before live authoring.",
                "required_before_authoring": ["specify supported UFunction and pin defaults", "rerun job contract smoke"],
            }
        )
    return gaps


def build_function_graph_steps(plan: Dict[str, Any], event_graph_steps: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not any(step["key"] == "function_graph_glue" for step in plan.get("safe_steps", [])):
        return []
    if request_has_function_graph_authoring(plan["request"]):
        graph_name = function_graph_name_for_request(plan["request"])
        if request_has_generated_function_invocation(plan["request"]):
            return [
                {
                    "id": "resolve_function_graph",
                    "operation": "command",
                    "command": "resolve_blueprint_graph",
                    "params": {
                        "graph_name": graph_name,
                        "graph_type": "function",
                        "create_if_missing": True,
                    },
                    "store_as": "function_graph",
                },
                {
                    "id": "function_input_addend",
                    "operation": "command",
                    "command": "add_blueprint_function_parameter",
                    "params": {
                        "parameter_name": "AddendValue",
                        "parameter_type": "double",
                        "direction": "input",
                        "default_value": 2.0,
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_input_addend",
                },
                {
                    "id": "function_output_value",
                    "operation": "command",
                    "command": "add_blueprint_function_parameter",
                    "params": {
                        "parameter_name": "ResultValue",
                        "parameter_type": "double",
                        "direction": "output",
                        "default_value": 0.0,
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_output_value",
                },
                {
                    "id": "function_local_value",
                    "operation": "command",
                    "command": "add_blueprint_local_variable",
                    "params": {
                        "variable_name": "LocalValue",
                        "variable_type": "double",
                        "default_value": 5.0,
                        "category": "Planner Smoke",
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_local_value",
                },
                {
                    "id": "local_value_get",
                    "operation": "command",
                    "command": "add_blueprint_variable_get_node",
                    "params": {
                        "variable_name": "LocalValue",
                        "node_position": [0, 80],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "local_value_get",
                },
                {
                    "id": "math_add_node",
                    "operation": "command",
                    "command": "add_blueprint_math_node",
                    "params": {
                        "operation": "add",
                        "node_position": [260, 80],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "math_add_node",
                },
                {
                    "id": "local_value_to_math_add",
                    "operation": "connect",
                    "source_node_ref": "local_value_get",
                    "source_pin_kind": "data",
                    "source_pin_preferred": ["LocalValue"],
                    "target_node_ref": "math_add_node",
                    "target_pin_kind": "data",
                    "target_pin_preferred": ["A"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "input_addend_to_math_add",
                    "operation": "connect",
                    "source_node_ref": "function_input_addend",
                    "source_pin_kind": "data",
                    "source_pin_preferred": ["AddendValue"],
                    "target_node_ref": "math_add_node",
                    "target_pin_kind": "data",
                    "target_pin_preferred": ["B"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "function_return_node",
                    "operation": "command",
                    "command": "add_blueprint_return_node",
                    "params": {
                        "node_position": [560, 0],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_return_node",
                },
                {
                    "id": "math_result_to_return",
                    "operation": "connect",
                    "source_node_ref": "math_add_node",
                    "source_pin_kind": "data",
                    "source_pin_preferred": ["ReturnValue", "Result"],
                    "target_node_ref": "function_return_node",
                    "target_pin_kind": "data",
                    "target_pin_preferred": ["ResultValue"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
            ]
        if request_has_function_graph_compare_branch(plan["request"]):
            return [
                {
                    "id": "resolve_function_graph",
                    "operation": "command",
                    "command": "resolve_blueprint_graph",
                    "params": {
                        "graph_name": graph_name,
                        "graph_type": "function",
                        "create_if_missing": True,
                    },
                    "store_as": "function_graph",
                },
                {
                    "id": "function_input_value",
                    "operation": "command",
                    "command": "add_blueprint_function_parameter",
                    "params": {
                        "parameter_name": "InputValue",
                        "parameter_type": "double",
                        "direction": "input",
                        "default_value": 3.0,
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_input_value",
                },
                {
                    "id": "function_output_value",
                    "operation": "command",
                    "command": "add_blueprint_function_parameter",
                    "params": {
                        "parameter_name": "ResultValue",
                        "parameter_type": "double",
                        "direction": "output",
                        "default_value": 0.0,
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_return_node",
                },
                {
                    "id": "function_local_branch_result",
                    "operation": "command",
                    "command": "add_blueprint_local_variable",
                    "params": {
                        "variable_name": "BranchResult",
                        "variable_type": "double",
                        "default_value": 0.0,
                        "category": "Planner Smoke",
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_local_branch_result",
                },
                {
                    "id": "pre_compare_branch_compile",
                    "operation": "command",
                    "command": "compile_and_validate_blueprint",
                    "params": {
                        "save": False,
                        "refresh_nodes": True,
                    },
                    "store_as": "pre_compare_branch_compile",
                    "must_pass_compile": True,
                },
                {
                    "id": "compare_greater_node",
                    "operation": "command",
                    "command": "add_blueprint_compare_node",
                    "params": {
                        "operation": "greater",
                        "value_type": "double",
                        "node_position": [260, 80],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "compare_greater_node",
                },
                {
                    "id": "compare_threshold_default",
                    "operation": "set_pin_default",
                    "node_ref": "compare_greater_node",
                    "pin_name": "B",
                    "value": 10.0,
                    "direction": "input",
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "branch_node",
                    "operation": "command",
                    "command": "add_blueprint_branch_node",
                    "params": {
                        "node_position": [520, 20],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "branch_node",
                },
                {
                    "id": "branch_then_value_set",
                    "operation": "command",
                    "command": "add_blueprint_variable_set_node",
                    "params": {
                        "variable_name": "BranchResult",
                        "node_position": [780, -80],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "branch_then_value_set",
                },
                {
                    "id": "branch_then_value_default",
                    "operation": "set_pin_default",
                    "node_ref": "branch_then_value_set",
                    "pin_name": "BranchResult",
                    "value": 1.0,
                    "direction": "input",
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "branch_else_value_set",
                    "operation": "command",
                    "command": "add_blueprint_variable_set_node",
                    "params": {
                        "variable_name": "BranchResult",
                        "node_position": [780, 180],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "branch_else_value_set",
                },
                {
                    "id": "branch_else_value_default",
                    "operation": "set_pin_default",
                    "node_ref": "branch_else_value_set",
                    "pin_name": "BranchResult",
                    "value": -1.0,
                    "direction": "input",
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "branch_result_get",
                    "operation": "command",
                    "command": "add_blueprint_variable_get_node",
                    "params": {
                        "variable_name": "BranchResult",
                        "node_position": [1040, 80],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "branch_result_get",
                },
                {
                    "id": "input_value_to_compare",
                    "operation": "connect",
                    "source_node_ref": "function_input_value",
                    "source_pin_kind": "data",
                    "source_pin_preferred": ["InputValue"],
                    "target_node_ref": "compare_greater_node",
                    "target_pin_kind": "data",
                    "target_pin_preferred": ["A"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "compare_result_to_branch",
                    "operation": "connect",
                    "source_node_ref": "compare_greater_node",
                    "source_pin_kind": "data",
                    "source_pin_preferred": ["ReturnValue"],
                    "target_node_ref": "branch_node",
                    "target_pin_kind": "data",
                    "target_pin_preferred": ["Condition"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "function_entry_to_branch",
                    "operation": "connect",
                    "source_node_ref": "function_input_value",
                    "source_pin_kind": "exec",
                    "source_pin_preferred": ["then"],
                    "target_node_ref": "branch_node",
                    "target_pin_kind": "exec",
                    "target_pin_preferred": ["execute", "exec"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                    "allow_pin_link_replacement": True,
                },
                {
                    "id": "branch_then_to_value_set",
                    "operation": "connect",
                    "source_node_ref": "branch_node",
                    "source_pin_kind": "exec",
                    "source_pin_preferred": ["then"],
                    "target_node_ref": "branch_then_value_set",
                    "target_pin_kind": "exec",
                    "target_pin_preferred": ["execute", "exec"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "branch_else_to_value_set",
                    "operation": "connect",
                    "source_node_ref": "branch_node",
                    "source_pin_kind": "exec",
                    "source_pin_preferred": ["else"],
                    "target_node_ref": "branch_else_value_set",
                    "target_pin_kind": "exec",
                    "target_pin_preferred": ["execute", "exec"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "branch_then_set_to_return_exec",
                    "operation": "connect",
                    "source_node_ref": "branch_then_value_set",
                    "source_pin_kind": "exec",
                    "source_pin_preferred": ["then"],
                    "target_node_ref": "function_return_node",
                    "target_pin_kind": "exec",
                    "target_pin_preferred": ["execute", "exec"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "branch_else_set_to_return_exec",
                    "operation": "connect",
                    "source_node_ref": "branch_else_value_set",
                    "source_pin_kind": "exec",
                    "source_pin_preferred": ["then"],
                    "target_node_ref": "function_return_node",
                    "target_pin_kind": "exec",
                    "target_pin_preferred": ["execute", "exec"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "branch_result_to_return",
                    "operation": "connect",
                    "source_node_ref": "branch_result_get",
                    "source_pin_kind": "data",
                    "source_pin_preferred": ["BranchResult"],
                    "target_node_ref": "function_return_node",
                    "target_pin_kind": "data",
                    "target_pin_preferred": ["ResultValue"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
            ]
        if request_has_function_graph_local_set(plan["request"]):
            return [
                {
                    "id": "resolve_function_graph",
                    "operation": "command",
                    "command": "resolve_blueprint_graph",
                    "params": {
                        "graph_name": graph_name,
                        "graph_type": "function",
                        "create_if_missing": True,
                    },
                    "store_as": "function_graph",
                },
                {
                    "id": "function_input_value",
                    "operation": "command",
                    "command": "add_blueprint_function_parameter",
                    "params": {
                        "parameter_name": "InputValue",
                        "parameter_type": "double",
                        "direction": "input",
                        "default_value": 3.0,
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_input_value",
                },
                {
                    "id": "function_output_value",
                    "operation": "command",
                    "command": "add_blueprint_function_parameter",
                    "params": {
                        "parameter_name": "ResultValue",
                        "parameter_type": "double",
                        "direction": "output",
                        "default_value": 0.0,
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_return_node",
                },
                {
                    "id": "function_local_accumulated_value",
                    "operation": "command",
                    "command": "add_blueprint_local_variable",
                    "params": {
                        "variable_name": "AccumulatedValue",
                        "variable_type": "double",
                        "default_value": 0.0,
                        "category": "Planner Smoke",
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_local_accumulated_value",
                },
                {
                    "id": "pre_local_set_compile",
                    "operation": "command",
                    "command": "compile_and_validate_blueprint",
                    "params": {
                        "save": False,
                        "refresh_nodes": True,
                    },
                    "store_as": "pre_local_set_compile",
                    "must_pass_compile": True,
                },
                {
                    "id": "math_add_node",
                    "operation": "command",
                    "command": "add_blueprint_math_node",
                    "params": {
                        "operation": "add",
                        "node_position": [260, 80],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "math_add_node",
                },
                {
                    "id": "math_add_rhs_default",
                    "operation": "set_pin_default",
                    "node_ref": "math_add_node",
                    "pin_name": "B",
                    "value": 2.0,
                    "direction": "input",
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "local_value_set",
                    "operation": "command",
                    "command": "add_blueprint_variable_set_node",
                    "params": {
                        "variable_name": "AccumulatedValue",
                        "node_position": [560, 20],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "local_value_set",
                },
                {
                    "id": "input_value_to_math_add",
                    "operation": "connect",
                    "source_node_ref": "function_input_value",
                    "source_pin_kind": "data",
                    "source_pin_preferred": ["InputValue"],
                    "target_node_ref": "math_add_node",
                    "target_pin_kind": "data",
                    "target_pin_preferred": ["A"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "math_result_to_local_value_set",
                    "operation": "connect",
                    "source_node_ref": "math_add_node",
                    "source_pin_kind": "data",
                    "source_pin_preferred": ["ReturnValue", "Result"],
                    "target_node_ref": "local_value_set",
                    "target_pin_kind": "data",
                    "target_pin_preferred": ["AccumulatedValue"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "function_entry_to_local_value_set",
                    "operation": "connect",
                    "source_node_ref": "function_input_value",
                    "source_pin_kind": "exec",
                    "source_pin_preferred": ["then"],
                    "target_node_ref": "local_value_set",
                    "target_pin_kind": "exec",
                    "target_pin_preferred": ["execute", "exec"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                    "allow_pin_link_replacement": True,
                },
                {
                    "id": "local_value_set_to_return_exec",
                    "operation": "connect",
                    "source_node_ref": "local_value_set",
                    "source_pin_kind": "exec",
                    "source_pin_preferred": ["then"],
                    "target_node_ref": "function_return_node",
                    "target_pin_kind": "exec",
                    "target_pin_preferred": ["execute", "exec"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                    "allow_pin_link_replacement": True,
                },
                {
                    "id": "local_value_set_output_to_return",
                    "operation": "connect",
                    "source_node_ref": "local_value_set",
                    "source_pin_kind": "data",
                    "source_pin_preferred": ["Output_Get"],
                    "target_node_ref": "function_return_node",
                    "target_pin_kind": "data",
                    "target_pin_preferred": ["ResultValue"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
            ]
        if request_has_function_graph_body_authoring(plan["request"]):
            return [
                {
                    "id": "resolve_function_graph",
                    "operation": "command",
                    "command": "resolve_blueprint_graph",
                    "params": {
                        "graph_name": graph_name,
                        "graph_type": "function",
                        "create_if_missing": True,
                    },
                    "store_as": "function_graph",
                },
                {
                    "id": "function_output_value",
                    "operation": "command",
                    "command": "add_blueprint_function_parameter",
                    "params": {
                        "parameter_name": "ResultValue",
                        "parameter_type": "double",
                        "direction": "output",
                        "default_value": 0.0,
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_output_value",
                },
                {
                    "id": "function_local_value",
                    "operation": "command",
                    "command": "add_blueprint_local_variable",
                    "params": {
                        "variable_name": "LocalValue",
                        "variable_type": "double",
                        "default_value": 5.0,
                        "category": "Planner Smoke",
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_local_value",
                },
                {
                    "id": "local_value_get",
                    "operation": "command",
                    "command": "add_blueprint_variable_get_node",
                    "params": {
                        "variable_name": "LocalValue",
                        "node_position": [0, 80],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "local_value_get",
                },
                {
                    "id": "math_add_node",
                    "operation": "command",
                    "command": "add_blueprint_math_node",
                    "params": {
                        "operation": "add",
                        "node_position": [260, 80],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "math_add_node",
                },
                {
                    "id": "math_add_rhs_default",
                    "operation": "set_pin_default",
                    "node_ref": "math_add_node",
                    "pin_name": "B",
                    "value": 2.0,
                    "direction": "input",
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "local_value_to_math_add",
                    "operation": "connect",
                    "source_node_ref": "local_value_get",
                    "source_pin_kind": "data",
                    "source_pin_preferred": ["LocalValue"],
                    "target_node_ref": "math_add_node",
                    "target_pin_kind": "data",
                    "target_pin_preferred": ["A"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                {
                    "id": "function_return_node",
                    "operation": "command",
                    "command": "add_blueprint_return_node",
                    "params": {
                        "node_position": [560, 0],
                        "graph_name": graph_name,
                        "graph_type": "function",
                    },
                    "store_as": "function_return_node",
                },
                {
                    "id": "math_result_to_return",
                    "operation": "connect",
                    "source_node_ref": "math_add_node",
                    "source_pin_kind": "data",
                    "source_pin_preferred": ["ReturnValue", "Result"],
                    "target_node_ref": "function_return_node",
                    "target_pin_kind": "data",
                    "target_pin_preferred": ["ResultValue"],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
            ]
        return [
            {
                "id": "resolve_function_graph",
                "operation": "command",
                "command": "resolve_blueprint_graph",
                "params": {
                    "graph_name": graph_name,
                    "graph_type": "function",
                    "create_if_missing": True,
                },
                "store_as": "function_graph",
            },
            {
                "id": "function_input_value",
                "operation": "command",
                "command": "add_blueprint_function_parameter",
                "params": {
                    "parameter_name": "InputValue",
                    "parameter_type": "int",
                    "direction": "input",
                    "default_value": 3,
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                "store_as": "function_input_value",
            },
            {
                "id": "function_output_value",
                "operation": "command",
                "command": "add_blueprint_function_parameter",
                "params": {
                    "parameter_name": "ResultValue",
                    "parameter_type": "int",
                    "direction": "output",
                    "default_value": 7,
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                "store_as": "function_output_value",
            },
            {
                "id": "function_return_node",
                "operation": "command",
                "command": "add_blueprint_return_node",
                "params": {
                    "node_position": [360, 0],
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                "store_as": "function_return_node",
            },
            {
                "id": "function_return_default",
                "operation": "set_pin_default",
                "node_ref": "function_return_node",
                "pin_name": "ResultValue",
                "value": 7,
                "direction": "input",
                "graph_name": graph_name,
                "graph_type": "function",
            },
        ]
    if any(step.get("id") == "print_string_call" for step in event_graph_steps):
        return [
            {
                "id": "function_call_authored_in_event_graph",
                "operation": "contract_note",
                "note": "The concrete PrintString function call is authored in the event graph; no dedicated function graph is created for this smoke manifest.",
            }
        ]
    return [
        {
            "id": "function_graph_scope",
            "operation": "contract_note",
            "note": "No concrete reflected function name was provided, so this manifest does not emit a function-call node.",
        }
    ]


def build_dispatcher_lifecycle_steps(plan: Dict[str, Any]) -> List[Dict[str, Any]]:
    if not any(step["key"] == "event_dispatcher_lifecycle" for step in plan.get("safe_steps", [])):
        return []
    return [
        {
            "id": "dispatcher_declare",
            "operation": "command",
            "command": "add_blueprint_event_dispatcher",
            "params": {
                "dispatcher_name": "OnPlannerSmoke",
                "inputs": [{"name": "Value", "type": "int"}],
                "category": "Planner Smoke",
            },
            "store_as": "dispatcher_declare",
        },
        {
            "id": "dispatcher_call",
            "operation": "command",
            "command": "add_blueprint_event_dispatcher_call_node",
            "params": {
                "dispatcher_name": "OnPlannerSmoke",
                "node_position": [640, 0],
                "graph_type": "event",
            },
            "store_as": "dispatcher_call",
        },
        {
            "id": "dispatcher_custom_event",
            "operation": "command",
            "command": "add_blueprint_custom_event_node",
            "params": {
                "custom_event_name": "HandlePlannerSmoke",
                "signature_source_dispatcher_name": "OnPlannerSmoke",
                "node_position": [640, 280],
                "graph_type": "event",
            },
            "store_as": "dispatcher_custom_event",
        },
        {
            "id": "dispatcher_bind",
            "operation": "command",
            "command": "add_blueprint_event_dispatcher_bind_node",
            "params": {
                "dispatcher_name": "OnPlannerSmoke",
                "node_position": [360, 0],
                "graph_type": "event",
            },
            "store_as": "dispatcher_bind",
        },
        {
            "id": "dispatcher_assign",
            "operation": "command",
            "command": "add_blueprint_event_dispatcher_assign_node",
            "params": {
                "dispatcher_name": "OnPlannerSmoke",
                "node_position": [360, 220],
                "graph_type": "event",
            },
            "store_as": "dispatcher_assign",
        },
        {
            "id": "dispatcher_unbind",
            "operation": "command",
            "command": "add_blueprint_event_dispatcher_unbind_node",
            "params": {
                "dispatcher_name": "OnPlannerSmoke",
                "node_position": [900, 0],
                "graph_type": "event",
            },
            "store_as": "dispatcher_unbind",
        },
        {
            "id": "dispatcher_clear",
            "operation": "command",
            "command": "add_blueprint_event_dispatcher_clear_node",
            "params": {
                "dispatcher_name": "OnPlannerSmoke",
                "node_position": [1160, 0],
                "graph_type": "event",
            },
            "store_as": "dispatcher_clear",
        },
        {
            "id": "custom_event_delegate_output_exists",
            "operation": "assert_pin",
            "node_ref": "dispatcher_custom_event",
            "direction": "output",
            "pin_names": ["OutputDelegate"],
            "must_exist": True,
        },
        {
            "id": "bind_delegate_input_exists",
            "operation": "assert_pin",
            "node_ref": "dispatcher_bind",
            "direction": "input",
            "pin_names": ["Delegate"],
            "must_exist": True,
        },
        {
            "id": "clear_delegate_input_absent",
            "operation": "assert_pin",
            "node_ref": "dispatcher_clear",
            "direction": "input",
            "pin_names": ["Delegate"],
            "must_exist": False,
        },
        {
            "id": "custom_event_to_bind_delegate",
            "operation": "connect",
            "source_node_ref": "dispatcher_custom_event",
            "source_pin_kind": "data",
            "source_pin_preferred": ["OutputDelegate"],
            "target_node_ref": "dispatcher_bind",
            "target_pin_kind": "data",
            "target_pin_preferred": ["Delegate"],
        },
        {
            "id": "custom_event_to_unbind_delegate",
            "operation": "connect",
            "source_node_ref": "dispatcher_custom_event",
            "source_pin_kind": "data",
            "source_pin_preferred": ["OutputDelegate"],
            "target_node_ref": "dispatcher_unbind",
            "target_pin_kind": "data",
            "target_pin_preferred": ["Delegate"],
        },
    ]


def build_generated_function_invocation_steps(plan: Dict[str, Any], event_graph_steps: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if not request_has_generated_function_invocation(plan["request"]):
        return []
    graph_name = function_graph_name_for_request(plan["request"])
    steps: List[Dict[str, Any]] = [
        {
            "id": "pre_invocation_compile",
            "operation": "command",
            "command": "compile_and_validate_blueprint",
            "params": {
                "save": False,
                "refresh_nodes": True,
            },
            "store_as": "pre_invocation_compile",
            "must_pass_compile": True,
        },
        {
            "id": "generated_function_call",
            "operation": "command",
            "command": "add_blueprint_call_function_node",
            "params": {
                "function_class": "{temp_package_path}/{blueprint_name}.{blueprint_name}_C",
                "function_name": graph_name,
                "param_defaults": {
                    "AddendValue": 2.0,
                },
                "node_position": [560, 120],
                "graph_type": "event",
            },
            "store_as": "generated_function_call",
        },
        {
            "id": "generated_function_result_output_exists",
            "operation": "assert_pin",
            "node_ref": "generated_function_call",
            "direction": "output",
            "pin_names": ["ResultValue"],
            "must_exist": True,
        },
        {
            "id": "event_graph_self_reference",
            "operation": "command",
            "command": "add_blueprint_self_reference",
            "params": {
                "node_position": [700, 260],
                "graph_type": "event",
            },
            "store_as": "event_graph_self_reference",
        },
        {
            "id": "last_invocation_result_set",
            "operation": "command",
            "command": "add_blueprint_variable_set_node",
            "params": {
                "variable_name": "LastInvocationResult",
                "node_position": [860, 120],
                "graph_type": "event",
            },
            "store_as": "last_invocation_result_set",
        },
        {
            "id": "generated_function_to_result_set_exec",
            "operation": "connect",
            "source_node_ref": "generated_function_call",
            "source_pin_kind": "exec",
            "source_pin_preferred": ["then"],
            "target_node_ref": "last_invocation_result_set",
            "target_pin_kind": "exec",
            "target_pin_preferred": ["execute", "exec"],
            "graph_type": "event",
        },
        {
            "id": "generated_result_to_last_invocation_result",
            "operation": "connect",
            "source_node_ref": "generated_function_call",
            "source_pin_kind": "data",
            "source_pin_preferred": ["ResultValue"],
            "target_node_ref": "last_invocation_result_set",
            "target_pin_kind": "data",
            "target_pin_preferred": ["LastInvocationResult"],
            "graph_type": "event",
        },
        {
            "id": "self_to_last_invocation_result_target",
            "operation": "connect",
            "source_node_ref": "event_graph_self_reference",
            "source_pin_kind": "data",
            "source_pin_preferred": ["self"],
            "target_node_ref": "last_invocation_result_set",
            "target_pin_kind": "data",
            "target_pin_preferred": ["self", "target"],
            "graph_type": "event",
        },
    ]
    if any(step.get("id") == "branch" for step in event_graph_steps):
        steps.append(
            {
                "id": "branch_true_to_generated_function",
                "operation": "connect",
                "source_node_ref": "branch",
                "source_pin_kind": "exec",
                "source_pin_preferred": ["true"],
                "target_node_ref": "generated_function_call",
                "target_pin_kind": "exec",
                "target_pin_preferred": ["execute", "exec"],
                "graph_type": "event",
            }
        )
    elif any(step.get("id") == "receive_begin_play" for step in event_graph_steps):
        steps.append(
            {
                "id": "begin_play_to_generated_function",
                "operation": "connect",
                "source_node_ref": "receive_begin_play",
                "source_pin_kind": "exec",
                "source_pin_preferred": ["then"],
                "target_node_ref": "generated_function_call",
                "target_pin_kind": "exec",
                "target_pin_preferred": ["execute", "exec"],
                "graph_type": "event",
            }
        )
    return steps


def build_function_call_contracts(
    executable: bool,
    event_graph_steps: Sequence[Dict[str, Any]],
    generated_function_invocation_steps: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if not executable:
        return []

    call_sections = (
        ("event_graph_steps", event_graph_steps),
        ("generated_function_invocation_steps", generated_function_invocation_steps),
    )
    contracts: List[Dict[str, Any]] = []
    for source_section, steps in call_sections:
        call_steps = [
            step
            for step in steps
            if step.get("operation") == "command"
            and step.get("command") == "add_blueprint_call_function_node"
            and step.get("store_as")
        ]
        for call_step in call_steps:
            node_ref = call_step["store_as"]
            params = call_step.get("params", {})
            incoming_exec_links = [
                {
                    "source_node_ref": step["source_node_ref"],
                    "source_pin_kind": step.get("source_pin_kind", "exec"),
                    "source_pin_preferred": step.get("source_pin_preferred", ()),
                    "target_pin_kind": step.get("target_pin_kind", "exec"),
                    "target_pin_preferred": step.get("target_pin_preferred", ()),
                    "source_step": step.get("id", ""),
                }
                for step in steps
                if step.get("operation") == "connect"
                and step.get("target_node_ref") == node_ref
                and step.get("source_pin_kind", "exec") == "exec"
            ]
            outgoing_links = [
                {
                    "target_node_ref": step["target_node_ref"],
                    "source_pin_kind": step.get("source_pin_kind", "exec"),
                    "source_pin_preferred": step.get("source_pin_preferred", ()),
                    "target_pin_kind": step.get("target_pin_kind", "exec"),
                    "target_pin_preferred": step.get("target_pin_preferred", ()),
                    "source_step": step.get("id", ""),
                }
                for step in steps
                if step.get("operation") == "connect" and step.get("source_node_ref") == node_ref
            ]
            required_output_pins = [
                {
                    "pin_names": step.get("pin_names", []),
                    "source_step": step.get("id", ""),
                }
                for step in steps
                if step.get("operation") == "assert_pin"
                and step.get("node_ref") == node_ref
                and step.get("direction") == "output"
                and step.get("must_exist", True)
            ]
            contracts.append(
                {
                    "id": f"{call_step['id']}_contract",
                    "schema": "section_23_function_call_contract_v1",
                    "operation": "function_call_contract",
                    "source_section": source_section,
                    "source_step": call_step["id"],
                    "node_ref": node_ref,
                    "function_class": params.get("function_class", ""),
                    "function_name": params.get("function_name", ""),
                    "graph_name": params.get("graph_name", ""),
                    "graph_type": params.get("graph_type", ""),
                    "input_defaults": [
                        {
                            "pin_name": pin_name,
                            "expected_value": pin_value,
                            "direction": "input",
                        }
                        for pin_name, pin_value in params.get("param_defaults", {}).items()
                    ],
                    "required_output_pins": required_output_pins,
                    "required_incoming_exec_links": incoming_exec_links,
                    "required_outgoing_links": outgoing_links,
                    "validation": [
                        "assert call node exists",
                        "assert function identity is visible on the authored node",
                        "assert declared input pin defaults",
                        "assert declared output pins",
                        "assert declared incoming and outgoing links",
                    ],
                }
            )
    return contracts


def build_graph_layout_contracts(
    executable: bool,
    event_graph_steps: Sequence[Dict[str, Any]],
    function_graph_steps: Sequence[Dict[str, Any]],
    generated_function_invocation_steps: Sequence[Dict[str, Any]],
    dispatcher_lifecycle_steps: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if not executable:
        return []

    contracts: List[Dict[str, Any]] = []
    for source_section, steps in (
        ("event_graph_steps", event_graph_steps),
        ("function_graph_steps", function_graph_steps),
        ("generated_function_invocation_steps", generated_function_invocation_steps),
        ("dispatcher_lifecycle_steps", dispatcher_lifecycle_steps),
    ):
        for step in steps:
            if step.get("operation") != "command" or not step.get("store_as"):
                continue
            params = step.get("params", {})
            node_position = params.get("node_position")
            if node_position is None:
                continue
            graph_type = params.get("graph_type", "")
            if not graph_type:
                graph_type = "function" if source_section == "function_graph_steps" else "event"
            contracts.append(
                {
                    "id": f"{step['id']}_layout",
                    "schema": "section_24_graph_layout_contract_v1",
                    "operation": "graph_layout_contract",
                    "source_section": source_section,
                    "source_step": step["id"],
                    "node_ref": step["store_as"],
                    "expected_position": node_position,
                    "position_tolerance": 16.0,
                    "graph_name": params.get("graph_name", ""),
                    "graph_type": graph_type,
                    "diagnostics": [
                        "assert authored node x/y matches manifest node_position",
                        "report actual node position",
                        "report graph selector used for the authored node",
                    ],
                }
            )
    return contracts


def build_graph_layout_spacing_contracts(graph_layout_contracts: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped_contracts: Dict[Tuple[str, str], List[Dict[str, Any]]] = {}
    for contract in graph_layout_contracts:
        graph_key = (contract.get("graph_type", ""), contract.get("graph_name", ""))
        grouped_contracts.setdefault(graph_key, []).append(contract)

    spacing_contracts: List[Dict[str, Any]] = []
    for (graph_type, graph_name), contracts in grouped_contracts.items():
        for source_contract, target_contract in combinations(contracts, 2):
            source_ref = source_contract.get("node_ref", "")
            target_ref = target_contract.get("node_ref", "")
            if not source_ref or not target_ref or source_ref == target_ref:
                continue
            spacing_contracts.append(
                {
                    "id": f"{source_contract['source_step']}_to_{target_contract['source_step']}_spacing",
                    "schema": "section_27_graph_layout_spacing_contract_v1",
                    "operation": "graph_layout_spacing_contract",
                    "source_section": source_contract.get("source_section", ""),
                    "target_section": target_contract.get("source_section", ""),
                    "source_step": source_contract["source_step"],
                    "target_step": target_contract["source_step"],
                    "source_node_ref": source_ref,
                    "target_node_ref": target_ref,
                    "source_expected_position": source_contract.get("expected_position", []),
                    "target_expected_position": target_contract.get("expected_position", []),
                    "minimum_distance": 96.0,
                    "graph_name": graph_name,
                    "graph_type": graph_type,
                    "diagnostics": [
                        "assert two authored nodes in the same graph are not placed at near-identical coordinates",
                        "report actual node positions and distance",
                        "report manifest expected node positions for both nodes",
                    ],
                }
            )
    return spacing_contracts


def build_variable_default_validation_steps(variables_defaults: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    steps: List[Dict[str, Any]] = []
    for variable in variables_defaults:
        if variable.get("command") != "add_blueprint_variable" or "default_value" not in variable:
            continue
        steps.append(
            {
                "id": f"{variable['id']}_default_verified",
                "operation": "assert_variable_default",
                "variable_name": variable["variable_name"],
                "variable_type": variable["variable_type"],
                "expected_value": variable.get("default_value"),
                "tolerance": 0.0001,
            }
        )
    return steps


def build_component_default_validation_steps(component_default_contracts: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": f"{contract['source_step']}_defaults_verified",
            "operation": "assert_component_default",
            "component_name": contract["component_name"],
            "component_type": contract["component_type"],
            "expected_transform": contract.get("expected_transform", {}),
            "expected_static_mesh": contract.get("expected_static_mesh", ""),
            "tolerance": 0.0001,
        }
        for contract in component_default_contracts
    ]


def build_component_hierarchy_validation_steps(component_hierarchy_contracts: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": f"{contract['source_step']}_hierarchy_verified",
            "operation": "assert_component_hierarchy",
            "component_name": contract["component_name"],
            "expected_parent_component_name": contract["expected_parent_component_name"],
        }
        for contract in component_hierarchy_contracts
    ]


def build_component_property_validation_steps(component_property_contracts: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [
        {
            "id": f"{contract['source_step']}_property_verified",
            "operation": "assert_component_property",
            "component_name": contract["component_name"],
            "property_name": contract["property_name"],
            "expected_value": contract.get("expected_value"),
            "tolerance": 0.0001,
        }
        for contract in component_property_contracts
    ]


def build_validation_plan(
    plan: Dict[str, Any],
    executable: bool,
    variables_defaults: Sequence[Dict[str, Any]] = (),
    component_default_contracts: Sequence[Dict[str, Any]] = (),
    component_hierarchy_contracts: Sequence[Dict[str, Any]] = (),
    component_property_contracts: Sequence[Dict[str, Any]] = (),
) -> List[Dict[str, Any]]:
    if not executable:
        return [
            {
                "id": "dry_run_no_authoring",
                "operation": "review_only",
                "reason": "Manifest is not executable; do not create or modify Blueprint assets.",
                "planner_validation": plan.get("validation_plan", []),
            }
        ]

    validation_steps: List[Dict[str, Any]] = []
    if request_has_function_graph_authoring(plan["request"]):
        graph_name = function_graph_name_for_request(plan["request"])
        validation_steps.append(
            {
                "id": "list_function_nodes",
                "operation": "command",
                "command": "list_blueprint_nodes",
                "params": {
                    "include_pins": True,
                    "graph_name": graph_name,
                    "graph_type": "function",
                },
                "store_as": "function_nodes",
            }
        )
    if any(step["key"] == "event_dispatcher_lifecycle" for step in plan.get("safe_steps", [])):
        validation_steps.append(
            {
                "id": "list_graphs",
                "operation": "command",
                "command": "list_blueprint_graphs",
                "params": {"graph_type": "any"},
                "store_as": "graphs",
            }
        )
    validation_steps.extend(
        [
            {
                "id": "list_event_nodes",
                "operation": "command",
                "command": "list_blueprint_nodes",
                "params": {
                    "include_pins": True,
                    "graph_type": "event",
                },
                "store_as": "event_nodes",
            },
            {
                "id": "compile_validate",
                "operation": "command",
                "command": "compile_and_validate_blueprint",
                "params": {
                    "save": False,
                    "refresh_nodes": True,
                },
                "store_as": "compile_validate",
                "must_pass_compile": True,
            },
        ]
    )
    validation_steps.extend(build_component_default_validation_steps(component_default_contracts))
    validation_steps.extend(build_component_hierarchy_validation_steps(component_hierarchy_contracts))
    validation_steps.extend(build_component_property_validation_steps(component_property_contracts))
    validation_steps.extend(build_variable_default_validation_steps(variables_defaults))
    return validation_steps


def build_structural_validation_plan(
    executable: bool,
    event_graph_steps: Sequence[Dict[str, Any]],
    function_graph_steps: Sequence[Dict[str, Any]],
    generated_function_invocation_steps: Sequence[Dict[str, Any]],
    function_call_contracts: Sequence[Dict[str, Any]],
    graph_layout_contracts: Sequence[Dict[str, Any]],
    graph_layout_spacing_contracts: Sequence[Dict[str, Any]],
    dispatcher_lifecycle_steps: Sequence[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    if not executable:
        return []

    node_authoring_commands = {
        "add_blueprint_event_node",
        "add_blueprint_branch_node",
        "add_blueprint_sequence_node",
        "add_blueprint_call_function_node",
        "add_blueprint_function_parameter",
        "add_blueprint_variable_get_node",
        "add_blueprint_variable_set_node",
        "add_blueprint_self_reference",
        "add_blueprint_math_node",
        "add_blueprint_compare_node",
        "add_blueprint_return_node",
        "add_blueprint_event_dispatcher_call_node",
        "add_blueprint_custom_event_node",
        "add_blueprint_event_dispatcher_bind_node",
        "add_blueprint_event_dispatcher_assign_node",
        "add_blueprint_event_dispatcher_unbind_node",
        "add_blueprint_event_dispatcher_clear_node",
    }
    structural_steps: List[Dict[str, Any]] = []
    for source_section, steps in (
        ("event_graph_steps", event_graph_steps),
        ("function_graph_steps", function_graph_steps),
        ("generated_function_invocation_steps", generated_function_invocation_steps),
        ("dispatcher_lifecycle_steps", dispatcher_lifecycle_steps),
    ):
        for step in steps:
            step_id = step.get("id", "")
            operation = step.get("operation", "command")
            command = step.get("command", "")
            store_as = step.get("store_as")
            graph_name = step.get("graph_name", step.get("params", {}).get("graph_name", ""))
            graph_type = step.get("graph_type", step.get("params", {}).get("graph_type", ""))

            if operation == "command" and command == "resolve_blueprint_graph" and store_as:
                structural_steps.append(
                    {
                        "id": f"{step_id}_graph_resolved",
                        "operation": "assert_graph_resolved",
                        "source_step": step_id,
                        "source_section": source_section,
                        "graph_ref": store_as,
                        "graph_name": graph_name,
                        "graph_type": graph_type,
                    }
                )
            elif operation == "command" and store_as and command in node_authoring_commands:
                structural_steps.append(
                    {
                        "id": f"{step_id}_node_exists",
                        "operation": "assert_node_exists",
                        "source_step": step_id,
                        "source_section": source_section,
                        "node_ref": store_as,
                        "graph_name": graph_name,
                        "graph_type": graph_type,
                    }
                )
                for param_name, param_value in step.get("params", {}).get("param_defaults", {}).items():
                    structural_steps.append(
                        {
                            "id": f"{step_id}_{slugify_identifier(param_name).lower()}_default_verified",
                            "operation": "assert_pin_default",
                            "source_step": step_id,
                            "source_section": source_section,
                            "node_ref": store_as,
                            "pin_name": param_name,
                            "value": param_value,
                            "direction": "input",
                            "graph_name": graph_name,
                            "graph_type": graph_type,
                        }
                    )
                if command == "add_blueprint_sequence_node":
                    structural_steps.append(
                        {
                            "id": f"{step_id}_output_count_verified",
                            "operation": "assert_exec_pin_count",
                            "source_step": step_id,
                            "source_section": source_section,
                            "node_ref": store_as,
                            "direction": "output",
                            "minimum_count": int(step.get("params", {}).get("output_count", 2)),
                            "graph_name": graph_name,
                            "graph_type": graph_type,
                        }
                    )
            elif operation == "set_pin_default":
                structural_steps.append(
                    {
                        "id": f"{step_id}_default_verified",
                        "operation": "assert_pin_default",
                        "source_step": step_id,
                        "source_section": source_section,
                        "node_ref": step["node_ref"],
                        "pin_name": step["pin_name"],
                        "value": step.get("value"),
                        "direction": step.get("direction", "input"),
                        "graph_name": graph_name,
                        "graph_type": graph_type,
                    }
                )
            elif operation == "connect":
                structural_steps.append(
                    {
                        "id": f"{step_id}_link_verified",
                        "operation": "assert_pin_link",
                        "source_step": step_id,
                        "source_section": source_section,
                        "source_node_ref": step["source_node_ref"],
                        "source_pin_kind": step.get("source_pin_kind", "exec"),
                        "source_pin_preferred": step.get("source_pin_preferred", ()),
                        "target_node_ref": step["target_node_ref"],
                        "target_pin_kind": step.get("target_pin_kind", "exec"),
                        "target_pin_preferred": step.get("target_pin_preferred", ()),
                        "graph_name": graph_name,
                        "graph_type": graph_type,
                    }
                )
            elif operation == "assert_pin":
                structural_steps.append(
                    {
                        "id": f"{step_id}_postcondition",
                        "operation": "assert_pin",
                        "source_step": step_id,
                        "source_section": source_section,
                        "node_ref": step["node_ref"],
                        "direction": step.get("direction"),
                        "pin_names": step.get("pin_names", []),
                        "must_exist": step.get("must_exist", True),
                        "graph_name": graph_name,
                        "graph_type": graph_type,
                    }
                )
    for contract in function_call_contracts:
        structural_steps.append(
            {
                "id": f"{contract['id']}_verified",
                "operation": "assert_function_call_contract",
                "source_step": contract["source_step"],
                "source_section": contract["source_section"],
                "node_ref": contract["node_ref"],
                "function_class": contract.get("function_class", ""),
                "function_name": contract.get("function_name", ""),
                "graph_name": contract.get("graph_name", ""),
                "graph_type": contract.get("graph_type", ""),
                "input_defaults": contract.get("input_defaults", []),
                "required_output_pins": contract.get("required_output_pins", []),
                "required_incoming_exec_links": contract.get("required_incoming_exec_links", []),
                "required_outgoing_links": contract.get("required_outgoing_links", []),
            }
        )
    for contract in graph_layout_contracts:
        structural_steps.append(
            {
                "id": f"{contract['id']}_verified",
                "operation": "assert_node_layout",
                "source_step": contract["source_step"],
                "source_section": contract["source_section"],
                "node_ref": contract["node_ref"],
                "expected_position": contract["expected_position"],
                "position_tolerance": contract.get("position_tolerance", 1.0),
                "graph_name": contract.get("graph_name", ""),
                "graph_type": contract.get("graph_type", ""),
            }
        )
    for contract in graph_layout_spacing_contracts:
        structural_steps.append(
            {
                "id": f"{contract['id']}_verified",
                "operation": "assert_layout_spacing",
                "source_step": contract["source_step"],
                "target_step": contract["target_step"],
                "source_section": contract["source_section"],
                "target_section": contract["target_section"],
                "source_node_ref": contract["source_node_ref"],
                "target_node_ref": contract["target_node_ref"],
                "source_expected_position": contract.get("source_expected_position", []),
                "target_expected_position": contract.get("target_expected_position", []),
                "minimum_distance": contract.get("minimum_distance", 96.0),
                "graph_name": contract.get("graph_name", ""),
                "graph_type": contract.get("graph_type", ""),
            }
        )
    return structural_steps


def collect_blocked_review_reasons(plan: Dict[str, Any], contract_reasons: Sequence[Dict[str, Any]] = ()) -> List[Dict[str, Any]]:
    reasons: List[Dict[str, Any]] = []
    for item in plan.get("requires_review", []):
        reasons.append(
            {
                "status": planner.STATUS_REVIEW,
                "key": item["key"],
                "label": item["label"],
                "reason": item["reason"],
                "required_before_authoring": item.get("validation", []),
            }
        )
    for item in plan.get("blocked_items", []):
        reasons.append(
            {
                "status": planner.STATUS_BLOCKED,
                "key": item["key"],
                "label": item["label"],
                "reason": item["reason"],
                "required_before_authoring": item.get("required_before_authoring", []),
            }
        )
    reasons.extend(contract_reasons)
    return reasons


def collect_required_reinforcement(plan: Dict[str, Any], contract_reasons: Sequence[Dict[str, Any]] = ()) -> List[str]:
    return planner.unique(
        item
        for reason in collect_blocked_review_reasons(plan, contract_reasons)
        for item in reason.get("required_before_authoring", [])
    )


def count_executable_steps(manifest: Dict[str, Any]) -> int:
    sections = (
        "component_list",
        "component_default_steps",
        "variables_defaults",
        "event_graph_steps",
        "function_graph_steps",
        "generated_function_invocation_steps",
        "dispatcher_lifecycle_steps",
        "validation_plan",
    )
    return sum(1 for section in sections for step in manifest.get(section, []) if step.get("operation") != "contract_note")


def manifest_has_authoring_commands(manifest: Dict[str, Any]) -> bool:
    sections = (
        "component_list",
        "component_default_steps",
        "variables_defaults",
        "event_graph_steps",
        "function_graph_steps",
        "generated_function_invocation_steps",
        "dispatcher_lifecycle_steps",
    )
    for section in sections:
        for step in manifest.get(section, []):
            if step.get("command") in AUTHORING_COMMANDS:
                return True
    return False


def build_job_manifest(
    request_id: str,
    request_text: str,
    temp_package_path: str = DEFAULT_TEMP_PACKAGE_PATH,
    target_class: str = "",
) -> Dict[str, Any]:
    plan = planner.plan_request(request_id, request_text, target_class=target_class)
    blueprint_kind = infer_blueprint_kind(plan["request"], plan)
    parent_class = infer_parent_class(plan["request"], blueprint_kind, target_class=target_class)
    parent_class_contract = build_parent_class_contract(blueprint_kind, parent_class)
    durable_authoring_contract = build_durable_authoring_contract(request_id, plan["request"], blueprint_kind, parent_class)
    sanitized_id = slugify_identifier(request_id)

    planner_safe = plan["status"] == planner.STATUS_SAFE
    component_list = build_component_list(plan, plan["request"]) if planner_safe else []
    component_default_steps = build_component_default_steps(component_list, plan["request"]) if planner_safe else []
    component_default_contracts = build_component_default_contracts(component_list, component_default_steps) if planner_safe else []
    component_hierarchy_contracts = build_component_hierarchy_contracts(component_list) if planner_safe else []
    component_property_contracts = build_component_property_contracts(component_default_steps) if planner_safe else []
    variables_defaults = build_variables_defaults(plan, plan["request"]) if planner_safe else []
    event_graph_steps = build_event_graph_steps(plan, plan["request"]) if planner_safe else []
    dispatcher_lifecycle_steps = build_dispatcher_lifecycle_steps(plan) if planner_safe else []
    contract_reasons = contract_specificity_gaps(
        plan,
        parent_class_contract,
        durable_authoring_contract,
        component_list,
        variables_defaults,
        event_graph_steps,
        dispatcher_lifecycle_steps,
    )
    executable = planner_safe and not contract_reasons
    function_graph_steps = build_function_graph_steps(plan, event_graph_steps) if executable else []
    generated_function_invocation_steps = build_generated_function_invocation_steps(plan, event_graph_steps) if executable else []
    function_call_contracts = build_function_call_contracts(executable, event_graph_steps, generated_function_invocation_steps)
    graph_layout_contracts = build_graph_layout_contracts(
        executable,
        event_graph_steps,
        function_graph_steps,
        generated_function_invocation_steps,
        dispatcher_lifecycle_steps,
    )
    graph_layout_spacing_contracts = build_graph_layout_spacing_contracts(graph_layout_contracts)
    if not executable:
        component_list = []
        component_default_steps = []
        component_default_contracts = []
        component_hierarchy_contracts = []
        component_property_contracts = []
        variables_defaults = []
        event_graph_steps = []
        function_call_contracts = []
        graph_layout_contracts = []
        graph_layout_spacing_contracts = []
        generated_function_invocation_steps = []
        dispatcher_lifecycle_steps = []
    validation_plan = build_validation_plan(
        plan,
        executable,
        variables_defaults,
        component_default_contracts,
        component_hierarchy_contracts,
        component_property_contracts,
    )
    structural_validation_plan = build_structural_validation_plan(
        executable,
        event_graph_steps,
        function_graph_steps,
        generated_function_invocation_steps,
        function_call_contracts,
        graph_layout_contracts,
        graph_layout_spacing_contracts,
        dispatcher_lifecycle_steps,
    )

    manifest = {
        "manifest_version": MANIFEST_VERSION,
        "analysis_kind": "bp_authoring_job_contract",
        "id": request_id,
        "request_original": plan["request"],
        "planner": plan,
        "status": plan["status"],
        "executable": executable,
        "blueprint_kind": blueprint_kind,
        "parent_class": parent_class,
        "parent_class_contract": parent_class_contract,
        "durable_authoring_contract": durable_authoring_contract,
        "durable_preflight_contract": durable_authoring_contract["durable_preflight_contract"],
        "durable_save_gate_contract": durable_authoring_contract["durable_preflight_contract"]["durable_save_gate_contract"],
        "durable_rollback_policy_contract": durable_authoring_contract["durable_preflight_contract"][
            "durable_rollback_policy_contract"
        ],
        "durable_executor_readiness_contract": durable_authoring_contract["durable_preflight_contract"][
            "durable_executor_readiness_contract"
        ],
        "durable_executor_skeleton_contract": durable_authoring_contract["durable_preflight_contract"][
            "durable_executor_skeleton_contract"
        ],
        "authoring_executor_contract": build_authoring_executor_contract(executable, temp_package_path, durable_authoring_contract),
        "blueprint_name_template": f"MCP_PlannerSmoke_{sanitized_id}_{{run_id}}",
        "temp_package_path": temp_package_path,
        "component_list": component_list,
        "component_default_steps": component_default_steps,
        "component_default_contracts": component_default_contracts,
        "component_hierarchy_contracts": component_hierarchy_contracts,
        "component_property_contracts": component_property_contracts,
        "component_property_allowlist": component_property_allowlist_entries(),
        "variables_defaults": variables_defaults,
        "event_graph_steps": event_graph_steps,
        "function_graph_steps": function_graph_steps,
        "function_call_contracts": function_call_contracts,
        "graph_layout_contracts": graph_layout_contracts,
        "graph_layout_spacing_contracts": graph_layout_spacing_contracts,
        "generated_function_invocation_steps": generated_function_invocation_steps,
        "dispatcher_lifecycle_steps": dispatcher_lifecycle_steps,
        "validation_plan": validation_plan,
        "structural_validation_plan": structural_validation_plan,
        "validation_diagnostics": {
            "required_compile_error_count": 0,
            "required_validation_pass": True,
            "required_asset_cleanup": True,
            "report_node_count": True,
            "report_graph_count": True,
            "report_section_step_results": True,
            "report_structural_assertion_results": True,
            "report_failure_diagnostics": True,
        },
        "failure_diagnostics_contract": {
            "diagnostic_schema": "section_21_failure_diagnostics_v1",
            "report_on_manifest_step_failure": executable,
            "report_on_structural_validation_failure": executable,
            "stage_tail_count": 5,
            "required_fields": [
                "manifest_id",
                "manifest_version",
                "blueprint_name",
                "phase",
                "section",
                "step_id",
                "operation",
                "command",
                "graph_name",
                "graph_type",
                "node_refs",
                "available_node_refs",
                "stage_tail",
                "error",
            ],
        },
        "cleanup_rollback_boundary": {
            "asset_path_template": f"{temp_package_path}/MCP_PlannerSmoke_{sanitized_id}_{{run_id}}",
            "delete_generated_asset_on_success": True,
            "delete_generated_asset_on_failure": True,
            "keep_assets_flag_may_override_cleanup": True,
            "allowed_package_root": temp_package_path,
            "rollback_scope": "Only the generated temporary Blueprint asset may be deleted by this smoke.",
        },
        "blocked_review_reasons": collect_blocked_review_reasons(plan, contract_reasons),
        "required_reinforcement": collect_required_reinforcement(plan, contract_reasons),
        "contract_rules": {
            "non_safe_authoring_steps_allowed": False,
            "safe_manifest_requires_compile_validation": True,
            "live_authoring_package_root": temp_package_path,
        },
    }
    manifest["authoring_step_count"] = count_executable_steps(manifest)
    manifest["structural_assertion_count"] = len(structural_validation_plan)
    if not executable and manifest_has_authoring_commands(manifest):
        raise ValueError(f"Non-executable manifest contains authoring commands: {request_id}")
    return manifest


def build_manifests(
    requests: Sequence[Tuple[str, str]],
    temp_package_path: str = DEFAULT_TEMP_PACKAGE_PATH,
    target_class: str = "",
) -> List[Dict[str, Any]]:
    return [build_job_manifest(request_id, request_text, temp_package_path, target_class) for request_id, request_text in requests]


def summarize_manifests(manifests: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    status_counts = Counter(manifest["status"] for manifest in manifests)
    executable_manifests = [manifest for manifest in manifests if manifest["executable"]]
    non_executable_manifests = [manifest for manifest in manifests if not manifest["executable"]]
    return {
        "manifest_count": len(manifests),
        "executable_manifest_count": len(executable_manifests),
        "non_executable_manifest_count": len(non_executable_manifests),
        "status_counts": dict(status_counts),
        "authoring_step_count": sum(manifest.get("authoring_step_count", 0) for manifest in executable_manifests),
        "structural_assertion_count": sum(manifest.get("structural_assertion_count", 0) for manifest in executable_manifests),
        "component_default_contract_count": sum(len(manifest.get("component_default_contracts", [])) for manifest in executable_manifests),
        "component_hierarchy_contract_count": sum(
            len(manifest.get("component_hierarchy_contracts", [])) for manifest in executable_manifests
        ),
        "component_property_contract_count": sum(
            len(manifest.get("component_property_contracts", [])) for manifest in executable_manifests
        ),
        "function_call_contract_count": sum(len(manifest.get("function_call_contracts", [])) for manifest in executable_manifests),
        "graph_layout_contract_count": sum(len(manifest.get("graph_layout_contracts", [])) for manifest in executable_manifests),
        "graph_layout_spacing_contract_count": sum(
            len(manifest.get("graph_layout_spacing_contracts", [])) for manifest in executable_manifests
        ),
        "durable_authoring_request_count": sum(
            1 for manifest in manifests if manifest.get("durable_authoring_contract", {}).get("requested")
        ),
        "durable_authoring_eligible_count": sum(
            1 for manifest in manifests if manifest.get("durable_authoring_contract", {}).get("durable_authoring_eligible")
        ),
        "durable_preflight_request_count": sum(
            1 for manifest in manifests if manifest.get("durable_preflight_contract", {}).get("requested")
        ),
        "durable_preflight_pass_count": sum(
            1 for manifest in manifests if manifest.get("durable_preflight_contract", {}).get("preflight_pass")
        ),
        "durable_overwrite_rename_decision_required_count": sum(
            1
            for manifest in manifests
            if manifest.get("durable_preflight_contract", {})
            .get("overwrite_rename_decision_contract", {})
            .get("decision_required")
        ),
        "durable_overwrite_rename_decision_present_count": sum(
            1
            for manifest in manifests
            if manifest.get("durable_preflight_contract", {})
            .get("overwrite_rename_decision_contract", {})
            .get("decision_present")
        ),
        "durable_overwrite_rename_decision_conflict_count": sum(
            1
            for manifest in manifests
            if manifest.get("durable_preflight_contract", {})
            .get("overwrite_rename_decision_contract", {})
            .get("decision_conflict")
        ),
        "durable_save_gate_request_count": sum(
            1 for manifest in manifests if manifest.get("durable_save_gate_contract", {}).get("requested")
        ),
        "durable_save_allowed_count": sum(
            1 for manifest in manifests if manifest.get("durable_save_gate_contract", {}).get("save_allowed")
        ),
        "durable_rollback_policy_ready_count": sum(
            1 for manifest in manifests if manifest.get("durable_rollback_policy_contract", {}).get("rollback_policy_ready")
        ),
        "durable_executor_readiness_request_count": sum(
            1 for manifest in manifests if manifest.get("durable_executor_readiness_contract", {}).get("requested")
        ),
        "durable_executor_ready_count": sum(
            1 for manifest in manifests if manifest.get("durable_executor_readiness_contract", {}).get("durable_executor_ready")
        ),
        "durable_executor_skeleton_request_count": sum(
            1 for manifest in manifests if manifest.get("durable_executor_skeleton_contract", {}).get("requested")
        ),
        "durable_executor_skeleton_enabled_count": sum(
            1 for manifest in manifests if manifest.get("durable_executor_skeleton_contract", {}).get("executor_enabled")
        ),
        "durable_executor_skeleton_executable_count": sum(
            1 for manifest in manifests if manifest.get("durable_executor_skeleton_contract", {}).get("can_execute")
        ),
        "durable_executor_skeleton_command_count": sum(
            manifest.get("durable_executor_skeleton_contract", {}).get("allowed_live_command_count", 0)
            for manifest in manifests
        ),
        "non_safe_authoring_command_count": sum(1 for manifest in non_executable_manifests if manifest_has_authoring_commands(manifest)),
        "executable_manifest_ids": [manifest["id"] for manifest in executable_manifests],
        "non_executable_manifest_ids": [manifest["id"] for manifest in non_executable_manifests],
    }


def build_report(
    requests: Sequence[Tuple[str, str]],
    output_dir: Path,
    temp_package_path: str = DEFAULT_TEMP_PACKAGE_PATH,
    target_class: str = "",
) -> Dict[str, Any]:
    manifests = build_manifests(requests, temp_package_path=temp_package_path, target_class=target_class)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_kind": "bp_authoring_job_contract",
        "manifest_version": MANIFEST_VERSION,
        "output_dir": str(output_dir),
        "temp_package_path": temp_package_path,
        "summary": summarize_manifests(manifests),
        "manifests": manifests,
        "policy": {
            "planner_status_preserved": True,
            "non_safe_requests_are_dry_run_only": True,
            "unknown_requests_default_to_review": True,
            "cxx_changes_required": False,
        },
    }


def format_count_map(data: Dict[str, Any]) -> str:
    if not data:
        return "- none\n"
    return "\n".join(f"- `{key}`: {value}" for key, value in data.items()) + "\n"


def format_steps(steps: Sequence[Dict[str, Any]]) -> List[str]:
    if not steps:
        return ["- none"]
    lines = []
    for step in steps:
        command = step.get("command", step.get("operation", ""))
        lines.append(f"- `{step.get('id', '')}` `{command}`")
    return lines


def render_markdown(report: Dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# BP Authoring Job Contract",
        "",
        f"- Generated UTC: `{report['generated_at']}`",
        f"- Manifest version: `{report['manifest_version']}`",
        f"- Temp package path: `{report['temp_package_path']}`",
        f"- Manifests: `{summary['manifest_count']}`",
        f"- Executable manifests: `{summary['executable_manifest_count']}`",
        f"- Non-executable manifests: `{summary['non_executable_manifest_count']}`",
        f"- Non-safe authoring command count: `{summary['non_safe_authoring_command_count']}`",
        f"- Structural assertions: `{summary['structural_assertion_count']}`",
        f"- Component default contracts: `{summary['component_default_contract_count']}`",
        f"- Component hierarchy contracts: `{summary['component_hierarchy_contract_count']}`",
        f"- Component property contracts: `{summary['component_property_contract_count']}`",
        f"- Function call contracts: `{summary['function_call_contract_count']}`",
        f"- Graph layout contracts: `{summary['graph_layout_contract_count']}`",
        f"- Graph layout spacing contracts: `{summary['graph_layout_spacing_contract_count']}`",
        f"- Durable authoring requests: `{summary['durable_authoring_request_count']}`",
        f"- Durable authoring eligible: `{summary['durable_authoring_eligible_count']}`",
        f"- Durable preflight requests: `{summary['durable_preflight_request_count']}`",
        f"- Durable preflight pass: `{summary['durable_preflight_pass_count']}`",
        f"- Durable overwrite/rename decision required: `{summary['durable_overwrite_rename_decision_required_count']}`",
        f"- Durable overwrite/rename decision present: `{summary['durable_overwrite_rename_decision_present_count']}`",
        f"- Durable overwrite/rename decision conflicts: `{summary['durable_overwrite_rename_decision_conflict_count']}`",
        f"- Durable save gate requests: `{summary['durable_save_gate_request_count']}`",
        f"- Durable save allowed: `{summary['durable_save_allowed_count']}`",
        f"- Durable rollback policy ready: `{summary['durable_rollback_policy_ready_count']}`",
        f"- Durable executor readiness requests: `{summary['durable_executor_readiness_request_count']}`",
        f"- Durable executor ready: `{summary['durable_executor_ready_count']}`",
        f"- Durable executor skeleton requests: `{summary['durable_executor_skeleton_request_count']}`",
        f"- Durable executor skeleton enabled: `{summary['durable_executor_skeleton_enabled_count']}`",
        f"- Durable executor skeleton executable: `{summary['durable_executor_skeleton_executable_count']}`",
        f"- Durable executor skeleton command count: `{summary['durable_executor_skeleton_command_count']}`",
        "",
        "## Status Counts",
        "",
        format_count_map(summary["status_counts"]),
        "## Manifests",
        "",
    ]
    for manifest in report["manifests"]:
        lines.extend(
            [
                f"### {manifest['id']}",
                "",
                f"- Request: {manifest['request_original']}",
                f"- Planner status: `{manifest['planner']['status']}`",
                f"- Executable: `{manifest['executable']}`",
                f"- Blueprint kind: `{manifest['blueprint_kind']}`",
                f"- Parent class: `{manifest['parent_class']}`",
                f"- Parent class executable allowed: `{manifest['parent_class_contract']['executable_allowed']}`",
                f"- Durable requested: `{manifest['durable_authoring_contract']['requested']}`",
                f"- Durable eligible: `{manifest['durable_authoring_contract']['durable_authoring_eligible']}`",
                f"- Durable package path: `{manifest['durable_authoring_contract']['requested_package_path'] or 'none'}`",
                f"- Durable save allowed: `{manifest['durable_authoring_contract']['save_allowed']}`",
                f"- Durable preflight target: `{manifest['durable_preflight_contract']['target_asset_path'] or 'none'}`",
                f"- Durable preflight pass: `{manifest['durable_preflight_contract']['preflight_pass']}`",
                f"- Durable overwrite/rename decision: `{manifest['durable_preflight_contract']['overwrite_rename_decision_contract']['decision']}`",
                f"- Durable save gate allowed: `{manifest['durable_save_gate_contract']['save_allowed']}`",
                f"- Durable rollback ready: `{manifest['durable_rollback_policy_contract']['rollback_policy_ready']}`",
                f"- Durable executor ready: `{manifest['durable_executor_readiness_contract']['durable_executor_ready']}`",
                f"- Durable executor skeleton enabled: `{manifest['durable_executor_skeleton_contract']['executor_enabled']}`",
                f"- Durable executor skeleton executable: `{manifest['durable_executor_skeleton_contract']['can_execute']}`",
                "",
                "Component list:",
                *format_steps(manifest["component_list"]),
                "",
                "Component defaults:",
                *format_steps(manifest["component_default_steps"]),
                "",
                "Component default contracts:",
                *format_steps(manifest["component_default_contracts"]),
                "",
                "Component hierarchy contracts:",
                *format_steps(manifest["component_hierarchy_contracts"]),
                "",
                "Component property contracts:",
                *format_steps(manifest["component_property_contracts"]),
                "",
                "Variables/defaults:",
                *format_steps(manifest["variables_defaults"]),
                "",
                "Event graph steps:",
                *format_steps(manifest["event_graph_steps"]),
                "",
                "Function graph steps:",
                *format_steps(manifest["function_graph_steps"]),
                "",
                "Function call contracts:",
                *format_steps(manifest["function_call_contracts"]),
                "",
                "Graph layout contracts:",
                *format_steps(manifest["graph_layout_contracts"]),
                "",
                "Graph layout spacing contracts:",
                *format_steps(manifest["graph_layout_spacing_contracts"]),
                "",
                "Generated function invocation steps:",
                *format_steps(manifest["generated_function_invocation_steps"]),
                "",
                "Dispatcher lifecycle steps:",
                *format_steps(manifest["dispatcher_lifecycle_steps"]),
                "",
                "Validation plan:",
                *format_steps(manifest["validation_plan"]),
                "",
                "Structural validation plan:",
                *format_steps(manifest["structural_validation_plan"]),
                "",
            ]
        )
        if manifest["blocked_review_reasons"]:
            lines.append("Blocked/review reasons:")
            for reason in manifest["blocked_review_reasons"]:
                lines.append(f"- `{reason['status']}` `{reason['key']}`: {reason['reason']}")
            lines.append("")

    lines.extend(
        [
            "## Decision",
            "",
            "A user request must become one of these manifests before live UnrealMCP Blueprint authoring. Only executable safe manifests may create assets; review and blocked manifests are dry-run records.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report(report: Dict[str, Any], output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "bp_authoring_job_contract_report.json"
    md_path = output_dir / "bp_authoring_job_contract_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def request_pairs_from_args(requests: Sequence[str]) -> List[Tuple[str, str]]:
    if not requests:
        return list(DEFAULT_SAMPLE_REQUESTS)
    return [(f"request_{index + 1}", request) for index, request in enumerate(requests)]


def build_arg_parser() -> argparse.ArgumentParser:
    repo_root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", action="append", default=[], help="Blueprint authoring request to convert. Repeatable.")
    parser.add_argument("--target-class", default="", help="Optional parent class hint for the generated Blueprint.")
    parser.add_argument("--temp-package-path", default=DEFAULT_TEMP_PACKAGE_PATH)
    parser.add_argument("--output-dir", default=str(repo_root / "Docs" / "Analysis" / "BPAuthoringJobContract"))
    parser.add_argument("--no-write", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    output_dir = Path(args.output_dir).resolve()
    report = build_report(
        request_pairs_from_args(args.request),
        output_dir,
        temp_package_path=args.temp_package_path,
        target_class=args.target_class,
    )
    if not args.no_write:
        json_path, md_path = write_report(report, output_dir)
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    print(f"Manifest count: {report['summary']['manifest_count']}")
    print(f"Executable manifests: {report['summary']['executable_manifest_count']}")
    print(f"Status counts: {report['summary']['status_counts']}")
    return 1 if report["summary"]["non_safe_authoring_command_count"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
