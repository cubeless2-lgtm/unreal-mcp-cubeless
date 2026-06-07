#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_manifest_executor.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_job_contract as contract  # noqa: E402
import bp_authoring_manifest_executor as executor  # noqa: E402


def find_manifest(manifests: list[dict], manifest_id: str) -> dict:
    for manifest in manifests:
        if manifest["id"] == manifest_id:
            return manifest
    raise AssertionError(f"missing manifest {manifest_id}")


def main() -> int:
    manifests = [
        contract.build_job_manifest(request_id, request, temp_package_path=contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in contract.DEFAULT_SAMPLE_REQUESTS
    ]

    summary = executor.summarize_executor_policies(manifests, contract.DEFAULT_TEMP_PACKAGE_PATH)
    assert summary["executor_version"] == executor.EXECUTOR_VERSION
    assert summary["manifest_count"] == 19
    assert summary["executable_by_executor_count"] == 12
    assert summary["blocked_by_executor_count"] == 7
    assert summary["temporary_scope_only"] is True
    assert summary["durable_authoring_allowed"] is False
    assert summary["save_allowed"] is False
    assert summary["save_step_count"] == 0
    assert summary["unknown_command_count"] == 0
    assert summary["forbidden_command_count"] == 0
    assert summary["capability_matrix_schema"] == executor.CAPABILITY_MATRIX_SCHEMA
    assert summary["durable_gate_schema"] == executor.DURABLE_GATE_SCHEMA
    assert summary["durable_gate_summary"] == {
        "schema": executor.DURABLE_GATE_SCHEMA,
        "durable_requested_manifest_count": 1,
        "read_only_live_preflight_allowed_count": 1,
        "durable_enable_contract_satisfied_count": 0,
        "durable_enable_executor_may_open_count": 0,
        "durable_enable_failed_required_gate_count": 2,
        "ownership_marker_policy_ready_count": 1,
        "delete_without_ownership_marker_allowed_count": 0,
        "delete_preexisting_asset_allowed_count": 0,
        "dry_run_plan_created_count": 1,
        "dry_run_plan_valid_count": 1,
        "dry_run_plan_executor_may_execute_count": 0,
        "dry_run_plan_live_command_count": 0,
        "save_simulation_evaluated_count": 1,
        "save_simulation_conditions_satisfied_count": 0,
        "save_simulation_save_true_allowed_count": 0,
        "save_simulation_save_asset_allowed_count": 0,
        "save_simulation_live_command_count": 0,
        "canary_prep_ready_count": 1,
        "canary_live_execution_allowed_count": 0,
        "canary_general_blueprints_package_allowed_count": 0,
        "canary_save_true_allowed_count": 0,
        "canary_save_asset_allowed_count": 0,
        "canary_delete_asset_allowed_count": 0,
        "canary_approval_record_present_count": 1,
        "canary_approval_gate_passed_count": 1,
        "canary_approval_scoped_to_canary_package_count": 1,
        "canary_approval_executor_may_open_count": 0,
        "canary_approval_live_execution_allowed_count": 0,
        "canary_approval_general_blueprints_package_allowed_count": 0,
        "canary_approval_save_true_allowed_count": 0,
        "canary_approval_save_asset_allowed_count": 0,
        "canary_approval_delete_asset_allowed_count": 0,
        "canary_approval_live_command_count": 0,
        "canary_live_preflight_read_only_allowed_count": 1,
        "canary_live_preflight_execution_allowed_count": 0,
        "canary_live_preflight_authoring_allowed_count": 0,
        "canary_live_preflight_save_or_delete_allowed_count": 0,
        "canary_live_preflight_cleanup_allowed_count": 0,
        "canary_live_preflight_authoring_command_count": 0,
        "canary_live_preflight_save_or_delete_command_count": 0,
        "canary_live_preflight_cleanup_command_count": 0,
        "canary_bridge_refresh_required_count": 1,
        "canary_bridge_refresh_reachable_count": 0,
        "canary_bridge_refresh_read_only_result_refreshed_count": 0,
        "canary_bridge_refresh_satisfied_count": 0,
        "canary_bridge_refresh_execution_allowed_count": 0,
        "canary_bridge_refresh_executor_may_open_count": 0,
        "canary_bridge_refresh_save_or_delete_allowed_count": 0,
        "canary_bridge_refresh_cleanup_allowed_count": 0,
        "canary_bridge_refresh_authoring_command_count": 0,
        "canary_bridge_refresh_save_or_delete_command_count": 0,
        "canary_bridge_refresh_cleanup_command_count": 0,
        "canary_recovery_matrix_ready_count": 1,
        "canary_recovery_scenario_count": 6,
        "canary_recovery_cleanup_allowed_count": 0,
        "canary_recovery_delete_allowed_count": 0,
        "canary_recovery_save_allowed_count": 0,
        "canary_recovery_authoring_allowed_count": 0,
        "canary_recovery_live_cleanup_command_count": 0,
        "canary_recovery_live_delete_command_count": 0,
        "canary_recovery_live_save_command_count": 0,
        "canary_recovery_live_authoring_command_count": 0,
        "durable_executor_enabled_count": 0,
        "durable_executor_executable_count": 0,
        "durable_executor_command_count": 0,
        "allowed_live_authoring_command_count": 0,
        "contract_save_allowed_count": 0,
        "save_or_delete_commands_allowed_count": 0,
        "preflight_pass_count": 0,
        "status": "passed",
    }
    assert summary["capability_summary"]["typed_defaults"] == {
        "requested_manifest_count": 5,
        "ready_manifest_count": 5,
        "missing_evidence_manifest_count": 0,
    }
    assert summary["capability_summary"]["graph_layout_dataflow"] == {
        "requested_manifest_count": 11,
        "ready_manifest_count": 11,
        "missing_evidence_manifest_count": 0,
    }
    assert summary["capability_summary"]["function_graph_executor"] == {
        "requested_manifest_count": 5,
        "ready_manifest_count": 5,
        "missing_evidence_manifest_count": 0,
    }
    assert summary["capability_summary"]["dispatcher_lifecycle_executor"] == {
        "requested_manifest_count": 1,
        "ready_manifest_count": 1,
        "missing_evidence_manifest_count": 0,
    }

    safe_actor = find_manifest(manifests, "safe_actor_shell")
    safe_policy = executor.build_executor_policy(safe_actor, contract.DEFAULT_TEMP_PACKAGE_PATH)
    assert safe_policy["can_execute"] is True
    assert safe_policy["authoring_command_count"] > 0
    assert safe_policy["validation_command_count"] > 0
    assert any(item["command"] == "compile_and_validate_blueprint" for item in safe_policy["command_plan"])
    assert safe_policy["capability_coverage"]["typed_defaults"]["status"] == "ready"

    durable = find_manifest(manifests, "review_durable_authoring_save_requested")
    durable_policy = executor.build_executor_policy(durable, contract.DEFAULT_TEMP_PACKAGE_PATH)
    assert durable_policy["can_execute"] is False
    assert any(item["key"] == "manifest_not_executable" for item in durable_policy["blocked_reasons"])
    assert any(item["key"] == "durable_authoring_not_enabled" for item in durable_policy["blocked_reasons"])
    durable_gate = durable_policy["durable_executor_gate"]
    assert durable_gate["schema"] == executor.DURABLE_GATE_SCHEMA
    assert durable_gate["status"] == "blocked_save_authoring_read_only_preflight_allowed"
    assert durable_gate["read_only_live_preflight_allowed"] is True
    assert durable_gate["durable_authoring_allowed"] is False
    assert durable_gate["durable_enable_contract_schema"] == "section_51_durable_authoring_enable_contract_v1"
    assert durable_gate["durable_enable_contract_satisfied"] is False
    assert durable_gate["durable_enable_executor_may_open"] is False
    assert durable_gate["durable_enable_failed_required_gate_ids"] == [
        "overwrite_rename_decision",
        "rollback_readiness",
    ]
    assert durable_gate["ownership_marker_policy_ready"] is True
    assert durable_gate["delete_without_ownership_marker_allowed"] is False
    assert durable_gate["delete_preexisting_asset_allowed"] is False
    assert durable_gate["dry_run_plan_created"] is True
    assert durable_gate["dry_run_plan_valid"] is True
    assert durable_gate["dry_run_plan_executor_may_execute"] is False
    assert durable_gate["dry_run_plan_live_command_count"] == 0
    assert durable_gate["save_simulation_evaluated"] is True
    assert durable_gate["save_simulation_conditions_satisfied"] is False
    assert durable_gate["save_simulation_save_true_allowed"] is False
    assert durable_gate["save_simulation_save_asset_allowed"] is False
    assert durable_gate["save_simulation_live_command_count"] == 0
    assert durable_gate["canary_prep_ready"] is True
    assert durable_gate["canary_live_execution_allowed"] is False
    assert durable_gate["canary_general_blueprints_package_allowed"] is False
    assert durable_gate["canary_save_true_allowed"] is False
    assert durable_gate["canary_save_asset_allowed"] is False
    assert durable_gate["canary_delete_asset_allowed"] is False
    assert durable_gate["canary_approval_record_present"] is True
    assert durable_gate["canary_approval_gate_passed"] is True
    assert durable_gate["canary_approval_scoped_to_canary_package"] is True
    assert durable_gate["canary_approval_executor_may_open"] is False
    assert durable_gate["canary_approval_live_execution_allowed"] is False
    assert durable_gate["canary_approval_general_blueprints_package_allowed"] is False
    assert durable_gate["canary_approval_save_true_allowed"] is False
    assert durable_gate["canary_approval_save_asset_allowed"] is False
    assert durable_gate["canary_approval_delete_asset_allowed"] is False
    assert durable_gate["canary_approval_live_command_count"] == 0
    assert durable_gate["canary_live_preflight_read_only_allowed"] is True
    assert durable_gate["canary_live_preflight_execution_allowed"] is False
    assert durable_gate["canary_live_preflight_authoring_allowed"] is False
    assert durable_gate["canary_live_preflight_save_or_delete_allowed"] is False
    assert durable_gate["canary_live_preflight_cleanup_allowed"] is False
    assert durable_gate["canary_live_preflight_authoring_command_count"] == 0
    assert durable_gate["canary_live_preflight_save_or_delete_command_count"] == 0
    assert durable_gate["canary_live_preflight_cleanup_command_count"] == 0
    assert durable_gate["canary_bridge_refresh_required"] is True
    assert durable_gate["canary_bridge_refresh_reachable"] is False
    assert durable_gate["canary_bridge_refresh_read_only_result_refreshed"] is False
    assert durable_gate["canary_bridge_refresh_satisfied"] is False
    assert durable_gate["canary_bridge_refresh_execution_allowed"] is False
    assert durable_gate["canary_bridge_refresh_executor_may_open"] is False
    assert durable_gate["canary_bridge_refresh_save_or_delete_allowed"] is False
    assert durable_gate["canary_bridge_refresh_cleanup_allowed"] is False
    assert durable_gate["canary_bridge_refresh_authoring_command_count"] == 0
    assert durable_gate["canary_bridge_refresh_save_or_delete_command_count"] == 0
    assert durable_gate["canary_bridge_refresh_cleanup_command_count"] == 0
    assert durable_gate["canary_recovery_matrix_ready"] is True
    assert durable_gate["canary_recovery_scenario_count"] == 6
    assert durable_gate["canary_recovery_cleanup_allowed"] is False
    assert durable_gate["canary_recovery_delete_allowed"] is False
    assert durable_gate["canary_recovery_save_allowed"] is False
    assert durable_gate["canary_recovery_authoring_allowed"] is False
    assert durable_gate["canary_recovery_live_cleanup_command_count"] == 0
    assert durable_gate["canary_recovery_live_delete_command_count"] == 0
    assert durable_gate["canary_recovery_live_save_command_count"] == 0
    assert durable_gate["canary_recovery_live_authoring_command_count"] == 0
    assert durable_gate["durable_executor_enabled"] is False
    assert durable_gate["durable_executor_can_execute"] is False
    assert durable_gate["save_allowed"] is False
    assert durable_gate["save_or_delete_commands_allowed"] is False
    assert durable_gate["allowed_live_authoring_command_count"] == 0
    assert durable_gate["target_asset_path"] == "/Game/Blueprints/BP_PlannerDurable"
    assert "save_asset" in durable_gate["forbidden_commands"]
    assert "durable_enable_contract_not_satisfied" in durable_gate["blocked_by"]
    assert "explicit_durable_executor_enable_flag" in durable_gate["blocked_by"]

    live_preflight_summary = executor.summarize_durable_live_preflight(
        manifests,
        [
            {
                "schema": executor.DURABLE_LIVE_PREFLIGHT_SCHEMA,
                "manifest_id": "review_durable_authoring_save_requested",
                "status": "passed",
                "read_only": True,
                "authoring_attempted": False,
                "save_or_delete_attempted": False,
                "asset_exists_check_performed": True,
                "asset_exists": False,
                "preflight_pass": False,
            }
        ],
        live_requested=True,
    )
    assert live_preflight_summary == {
        "schema": executor.DURABLE_LIVE_PREFLIGHT_SCHEMA,
        "status": "passed",
        "live_requested": True,
        "durable_preflight_requested_manifest_count": 1,
        "read_only_live_preflight_allowed_count": 1,
        "live_result_count": 1,
        "passed_read_only_result_count": 1,
        "authoring_attempted_count": 0,
        "save_or_delete_attempted_count": 0,
        "preflight_pass_count": 0,
        "durable_authoring_allowed": False,
        "save_or_delete_allowed": False,
        "missing_live_result_manifest_ids": [],
        "unexpected_live_result_manifest_ids": [],
        "read_only_only": True,
    }
    offline_preflight_summary = executor.summarize_durable_live_preflight(manifests, [], live_requested=False)
    assert offline_preflight_summary["status"] == "not_requested"
    assert offline_preflight_summary["durable_preflight_requested_manifest_count"] == 1

    bad_scope_policy = executor.build_executor_policy(safe_actor, "/Game/Blueprints")
    assert bad_scope_policy["can_execute"] is False
    assert any(item["key"] == "temp_package_path_not_allowlisted" for item in bad_scope_policy["blocked_reasons"])
    policy_diagnostic = executor.build_policy_failure_diagnostic(safe_actor, bad_scope_policy)
    assert policy_diagnostic["diagnostic_schema"] == executor.FAILURE_DIAGNOSTIC_SCHEMA
    assert policy_diagnostic["failure_category"] == "policy_block"
    assert policy_diagnostic["replay_safety"]["safe_to_replay_authoring"] is False

    cleanup_diagnostic = executor.build_cleanup_failure_diagnostic(
        safe_actor,
        "MCP_Test",
        "/Game/_MCP_Temp/PlannerDrivenSmoke/MCP_Test",
        {"deleted": False},
    )
    assert cleanup_diagnostic["diagnostic_schema"] == executor.FAILURE_DIAGNOSTIC_SCHEMA
    assert cleanup_diagnostic["failure_category"] == "cleanup_failure"
    assert cleanup_diagnostic["replay_safety"]["recommended_action"] == "retry_cleanup_only_before_authoring_replay"

    bridge_diagnostic = executor.enrich_failure_diagnostic(
        {
            "diagnostic_schema": "legacy",
            "phase": "manifest_step",
            "command": "list_blueprint_components",
            "error_type": "ConnectionResetError",
            "error": "[WinError 10054] connection reset",
        },
        phase="manifest_step",
    )
    assert bridge_diagnostic["failure_category"] == "bridge_connection_reset"
    assert bridge_diagnostic["replay_safety"]["safe_to_replay_authoring"] is True

    calls: list[tuple[str, str]] = []
    minimal_manifest = {
        "id": "minimal_safe",
        "manifest_version": contract.MANIFEST_VERSION,
        "status": "safe_to_author",
        "executable": True,
        "parent_class": "Actor",
        "temp_package_path": contract.DEFAULT_TEMP_PACKAGE_PATH,
        "component_list": [{"id": "component", "operation": "contract_note"}],
        "component_default_steps": [],
        "variables_defaults": [],
        "event_graph_steps": [],
        "function_graph_steps": [],
        "generated_function_invocation_steps": [],
        "dispatcher_lifecycle_steps": [],
        "validation_plan": [{"id": "compile", "operation": "command", "command": "compile_and_validate_blueprint"}],
        "structural_validation_plan": [{"id": "node_exists", "operation": "assert_node_exists"}],
    }

    def execute_step(section: str, step: dict, node_results: dict, section_results: list[dict]) -> dict | None:
        calls.append((section, step["id"]))
        if step.get("command") == "compile_and_validate_blueprint":
            node_results["compile_validate"] = {"validation_pass": True, "compile_error_count": 0}
        section_results.append({"id": step["id"], "operation": step.get("operation", "command"), "status": "success"})
        return None

    def execute_structural_step(step: dict, node_results: dict) -> dict:
        calls.append(("structural_validation_plan", step["id"]))
        return {"id": step["id"], "operation": step["operation"], "status": "success"}

    def build_failure(section: str, step: dict, node_results: dict, exc: Exception, phase: str) -> dict:
        return {"section": section, "step_id": step.get("id", ""), "phase": phase, "error": str(exc)}

    result = executor.execute_manifest(
        minimal_manifest,
        "MCP_Test",
        contract.DEFAULT_TEMP_PACKAGE_PATH,
        executor.ManifestExecutorCallbacks(
            execute_step=execute_step,
            execute_structural_step=execute_structural_step,
            build_failure_diagnostic=build_failure,
        ),
    )
    assert result["schema"] == executor.EXECUTOR_RESULT_SCHEMA
    assert result["executor_version"] == executor.EXECUTOR_VERSION
    assert result["status"] == "passed"
    assert result["validation"]["compile_error_count"] == 0
    assert result["replay_safety"]["durable_side_effects_allowed"] is False
    assert calls == [
        ("component_list", "component"),
        ("validation_plan", "compile"),
        ("structural_validation_plan", "node_exists"),
    ]

    print("BP authoring manifest executor smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
