#!/usr/bin/env python
"""
Section 49-50 Blueprint authoring regression matrix and release boundary report.

The report does not run live Unreal authoring. It reads the current analysis
reports and rebuilds the offline manifest/executor matrix so the release
boundary is explicit before publishing BP authoring changes.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import bp_authoring_job_contract as job_contract
import bp_authoring_durable_bridge_recovery_readiness_contract as bridge_recovery_readiness
import bp_authoring_durable_canary_authoring_command_contract as authoring_command
import bp_authoring_durable_canary_authoring_command_completion_application_contract as authoring_completion_application
import bp_authoring_durable_canary_authoring_command_completion_decision_contract as authoring_completion_decision
import bp_authoring_durable_canary_authoring_command_completion_result_contract as authoring_completion_result
import bp_authoring_durable_canary_authoring_command_dispatch_contract as authoring_command_dispatch
import bp_authoring_durable_canary_authoring_command_execution_contract as authoring_command_execution
import bp_authoring_durable_canary_authoring_command_execution_evidence_contract as authoring_command_execution_evidence
import bp_authoring_durable_canary_authoring_final_no_save_release_contract as authoring_final_no_save_release
import bp_authoring_durable_canary_authoring_final_release_readiness_contract as authoring_final_release_readiness
import bp_authoring_durable_canary_authoring_command_result_readback_contract as authoring_result_readback
import bp_authoring_durable_executor_change_design_contract as change_design
import bp_authoring_durable_executor_code_change_approval_contract as code_change_approval
import bp_authoring_durable_executor_code_patch_application_contract as code_patch_application
import bp_authoring_durable_executor_code_patch_execution_contract as code_patch_execution
import bp_authoring_durable_executor_code_patch_final_no_save_release_contract as code_patch_final_no_save_release
import bp_authoring_durable_executor_code_patch_final_release_readiness_contract as code_patch_final_release_readiness
import bp_authoring_durable_executor_code_patch_release_decision_contract as code_patch_release_decision
import bp_authoring_durable_executor_code_patch_release_review_contract as code_patch_release_review
import bp_authoring_durable_executor_code_patch_result_contract as code_patch_result
import bp_authoring_durable_executor_code_patch_result_readback_contract as code_patch_result_readback
import bp_authoring_durable_executor_code_patch_plan_contract as code_patch_plan
import bp_authoring_durable_executor_code_patch_review_contract as code_patch_review
import bp_authoring_durable_executor_activation_readiness_contract as activation_readiness
import bp_authoring_durable_executor_authoring_enable_contract as durable_executor_authoring_enable
import bp_authoring_durable_executor_open_contract as durable_executor_open
import bp_authoring_durable_executor_release_promotion_barrier_contract as release_promotion_barrier
import bp_authoring_durable_executor_implementation_plan_contract as implementation_plan
import bp_authoring_durable_executor_implementation_review_contract as implementation_review
import bp_authoring_durable_canary_command_allowlist_contract as canary_command_allowlist
import bp_authoring_durable_canary_authoring_enable_contract as authoring_enable
import bp_authoring_durable_canary_creation_boundary_contract as canary_creation_boundary
import bp_authoring_durable_canary_executor_activation_contract as executor_activation
import bp_authoring_durable_canary_executor_open_contract as executor_open
import bp_authoring_durable_canary_live_command_dispatch_release_contract as live_command_dispatch_release
import bp_authoring_durable_canary_live_command_execution_evidence_admission_contract as execution_evidence_admission
import bp_authoring_durable_canary_live_command_execution_release_contract as live_command_execution_release
import bp_authoring_durable_canary_live_runner_envelope_contract as live_runner_envelope
import bp_authoring_durable_canary_live_runner_start_contract as live_runner_start
import bp_authoring_durable_canary_release_promotion_decision_contract as promotion_decision
import bp_authoring_durable_canary_read_only_retry_envelope_contract as canary_read_only_retry
import bp_authoring_durable_canary_read_only_retry_result_admission_contract as retry_result_admission
import bp_authoring_durable_canary_rehearsal_execution_release_contract as rehearsal_execution_release
import bp_authoring_durable_canary_rehearsal_promotion_barrier_contract as rehearsal_promotion_barrier
import bp_authoring_durable_canary_rehearsal_readiness_contract as canary_rehearsal_readiness
import bp_authoring_durable_executor_review_contract as executor_review
import bp_authoring_durable_live_evidence_refresh_contract as live_evidence_refresh
import bp_authoring_durable_mvp_decision_contract as mvp_decision
import bp_authoring_durable_ownership_marker_proof_contract as ownership_marker_proof
import bp_authoring_durable_release_decision_contract as durable_release_decision
import bp_authoring_durable_rollback_cleanup_proof_contract as rollback_cleanup_proof
import bp_authoring_durable_save_gate_final_review_contract as save_gate_final_review
import bp_authoring_manifest_executor as manifest_executor


REPORT_SCHEMA = "section_112_bp_authoring_release_boundary_v54"
ANALYSIS_KIND = "bp_authoring_release_boundary"


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def row(
    row_id: str,
    label: str,
    passed: bool,
    expected: Dict[str, Any],
    actual: Dict[str, Any],
    blocking: bool = True,
    notes: Iterable[str] = (),
) -> Dict[str, Any]:
    return {
        "id": row_id,
        "label": label,
        "status": "passed" if passed else "failed",
        "blocking": blocking,
        "expected": expected,
        "actual": actual,
        "notes": list(notes),
    }


def missing_row(row_id: str, label: str, path: Path) -> Dict[str, Any]:
    return row(
        row_id,
        label,
        passed=False,
        expected={"report_exists": True},
        actual={"report_exists": False, "path": str(path)},
        notes=("regenerate the required analysis report before release review",),
    )


def default_manifests() -> List[Dict[str, Any]]:
    return [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]


def build_contract_matrix_row(contract_summary: Dict[str, Any]) -> Dict[str, Any]:
    expected = {
        "manifest_count": 19,
        "executable_manifest_count": 12,
        "non_executable_manifest_count": 7,
        "non_safe_authoring_command_count": 0,
        "durable_authoring_request_count": 1,
        "durable_authoring_eligible_count": 0,
    }
    actual = {key: contract_summary.get(key) for key in expected}
    return row(
        "job_contract_default_request_set",
        "Section 12-39 job contract default request set",
        passed=actual == expected,
        expected=expected,
        actual=actual,
    )


def build_executor_matrix_row(executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    expected = {
        "executable_by_executor_count": 12,
        "blocked_by_executor_count": 7,
        "save_step_count": 0,
        "unknown_command_count": 0,
        "forbidden_command_count": 0,
        "durable_authoring_allowed": False,
        "save_allowed": False,
    }
    actual = {key: executor_summary.get(key) for key in expected}
    return row(
        "manifest_executor_policy",
        "Section 40-41 temporary manifest executor policy",
        passed=actual == expected,
        expected=expected,
        actual=actual,
    )


def build_capability_matrix_row(executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    expected_ready = {
        "typed_defaults": 5,
        "graph_layout_dataflow": 11,
        "function_graph_executor": 5,
        "dispatcher_lifecycle_executor": 1,
    }
    capability_summary = executor_summary.get("capability_summary", {})
    actual = {
        key: {
            "requested": capability_summary.get(key, {}).get("requested_manifest_count"),
            "ready": capability_summary.get(key, {}).get("ready_manifest_count"),
            "missing": capability_summary.get(key, {}).get("missing_evidence_manifest_count"),
        }
        for key in expected_ready
    }
    passed = all(
        actual[key]["requested"] == expected_ready[key]
        and actual[key]["ready"] == expected_ready[key]
        and actual[key]["missing"] == 0
        for key in expected_ready
    )
    return row(
        "executor_capability_matrix",
        "Section 42-45 executor capability matrix",
        passed=passed,
        expected={key: {"requested": value, "ready": value, "missing": 0} for key, value in expected_ready.items()},
        actual=actual,
    )


def build_durable_gate_matrix_row(executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    expected = {
        "status": "passed",
        "durable_requested_manifest_count": 1,
        "read_only_live_preflight_allowed_count": 1,
        "durable_executor_enabled_count": 0,
        "durable_executor_executable_count": 0,
        "allowed_live_authoring_command_count": 0,
        "contract_save_allowed_count": 0,
        "save_or_delete_commands_allowed_count": 0,
        "canary_bridge_refresh_execution_allowed_count": 0,
        "canary_bridge_refresh_executor_may_open_count": 0,
        "canary_bridge_refresh_save_or_delete_allowed_count": 0,
        "preflight_pass_count": 0,
    }
    durable_summary = executor_summary.get("durable_gate_summary", {})
    actual = {key: durable_summary.get(key) for key in expected}
    return row(
        "durable_executor_gate_matrix",
        "Section 46-48/61 durable executor gate matrix",
        passed=actual == expected,
        expected=expected,
        actual=actual,
    )


def build_durable_enable_contract_row(contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    enable_summary = contract_summary.get("durable_enable_contract_summary", {})
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "summary_status": "passed",
        "durable_requested_manifest_count": 1,
        "enable_contract_satisfied_count": 0,
        "durable_executor_may_open_count": 0,
        "durable_authoring_allowed_count": 0,
        "forbidden_command_allowed_count": 0,
        "target_package_allowlist_passed_count": 1,
        "overwrite_rename_decision_passed_count": 0,
        "rollback_readiness_passed_count": 0,
        "ownership_marker_passed_count": 1,
        "executor_gate_may_open_count": 0,
    }
    actual = {
        "summary_status": enable_summary.get("status"),
        "durable_requested_manifest_count": enable_summary.get("durable_requested_manifest_count"),
        "enable_contract_satisfied_count": enable_summary.get("enable_contract_satisfied_count"),
        "durable_executor_may_open_count": enable_summary.get("durable_executor_may_open_count"),
        "durable_authoring_allowed_count": enable_summary.get("durable_authoring_allowed_count"),
        "forbidden_command_allowed_count": enable_summary.get("forbidden_command_allowed_count"),
        "target_package_allowlist_passed_count": enable_summary.get("target_package_allowlist_passed_count"),
        "overwrite_rename_decision_passed_count": enable_summary.get("overwrite_rename_decision_passed_count"),
        "rollback_readiness_passed_count": enable_summary.get("rollback_readiness_passed_count"),
        "ownership_marker_passed_count": enable_summary.get("ownership_marker_passed_count"),
        "executor_gate_may_open_count": durable_gate_summary.get("durable_enable_executor_may_open_count"),
    }
    return row(
        "durable_authoring_enable_contract",
        "Section 51 durable authoring enable contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Section 51 separates target allowlist, overwrite/rename, rollback readiness, and ownership marker gates.",
            "It does not enable durable save/delete/rename/live authoring.",
        ),
    )


def build_durable_ownership_marker_row(contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "durable_ownership_marker_request_count": 1,
        "durable_ownership_marker_policy_ready_count": 1,
        "durable_ownership_delete_without_marker_allowed_count": 0,
        "durable_ownership_delete_preexisting_asset_allowed_count": 0,
        "executor_gate_ownership_marker_policy_ready_count": 1,
        "executor_gate_delete_without_marker_allowed_count": 0,
        "executor_gate_delete_preexisting_asset_allowed_count": 0,
    }
    actual = {
        "durable_ownership_marker_request_count": contract_summary.get("durable_ownership_marker_request_count"),
        "durable_ownership_marker_policy_ready_count": contract_summary.get(
            "durable_ownership_marker_policy_ready_count"
        ),
        "durable_ownership_delete_without_marker_allowed_count": contract_summary.get(
            "durable_ownership_delete_without_marker_allowed_count"
        ),
        "durable_ownership_delete_preexisting_asset_allowed_count": contract_summary.get(
            "durable_ownership_delete_preexisting_asset_allowed_count"
        ),
        "executor_gate_ownership_marker_policy_ready_count": durable_gate_summary.get("ownership_marker_policy_ready_count"),
        "executor_gate_delete_without_marker_allowed_count": durable_gate_summary.get(
            "delete_without_ownership_marker_allowed_count"
        ),
        "executor_gate_delete_preexisting_asset_allowed_count": durable_gate_summary.get(
            "delete_preexisting_asset_allowed_count"
        ),
    }
    return row(
        "durable_ownership_marker_contract",
        "Section 52 durable rollback ownership marker contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Rollback/delete is authorized only for executor-created assets with a matching ownership marker.",
            "Section 52 still does not execute delete or durable save commands.",
        ),
    )


def build_durable_dry_run_plan_row(contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    dry_run_summary = contract_summary.get("durable_dry_run_plan_summary", {})
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "summary_status": "passed",
        "durable_requested_plan_count": 1,
        "dry_run_plan_created_count": 1,
        "dry_run_plan_valid_count": 1,
        "durable_executor_may_execute_count": 0,
        "live_command_count": 0,
        "forbidden_command_allowed_count": 0,
        "executor_gate_dry_run_plan_created_count": 1,
        "executor_gate_dry_run_plan_valid_count": 1,
        "executor_gate_dry_run_may_execute_count": 0,
        "executor_gate_dry_run_live_command_count": 0,
    }
    actual = {
        "summary_status": dry_run_summary.get("status"),
        "durable_requested_plan_count": dry_run_summary.get("durable_requested_plan_count"),
        "dry_run_plan_created_count": dry_run_summary.get("dry_run_plan_created_count"),
        "dry_run_plan_valid_count": dry_run_summary.get("dry_run_plan_valid_count"),
        "durable_executor_may_execute_count": dry_run_summary.get("durable_executor_may_execute_count"),
        "live_command_count": dry_run_summary.get("live_command_count"),
        "forbidden_command_allowed_count": dry_run_summary.get("forbidden_command_allowed_count"),
        "executor_gate_dry_run_plan_created_count": durable_gate_summary.get("dry_run_plan_created_count"),
        "executor_gate_dry_run_plan_valid_count": durable_gate_summary.get("dry_run_plan_valid_count"),
        "executor_gate_dry_run_may_execute_count": durable_gate_summary.get("dry_run_plan_executor_may_execute_count"),
        "executor_gate_dry_run_live_command_count": durable_gate_summary.get("dry_run_plan_live_command_count"),
    }
    return row(
        "durable_executor_dry_run_plan",
        "Section 53 durable executor dry-run plan",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Dry-run plan records durable execution intent without live commands.",
            "Execution command plan must remain empty until a later durable release.",
        ),
    )


def build_durable_save_simulator_row(contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    save_summary = contract_summary.get("durable_save_simulation_summary", {})
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "summary_status": "passed",
        "durable_requested_simulation_count": 1,
        "simulation_evaluated_count": 1,
        "future_save_conditions_satisfied_count": 0,
        "save_true_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "compile_save_command_allowed_count": 0,
        "live_command_count": 0,
        "executor_gate_simulation_evaluated_count": 1,
        "executor_gate_conditions_satisfied_count": 0,
        "executor_gate_save_true_allowed_count": 0,
        "executor_gate_save_asset_allowed_count": 0,
        "executor_gate_live_command_count": 0,
    }
    actual = {
        "summary_status": save_summary.get("status"),
        "durable_requested_simulation_count": save_summary.get("durable_requested_simulation_count"),
        "simulation_evaluated_count": save_summary.get("simulation_evaluated_count"),
        "future_save_conditions_satisfied_count": save_summary.get("future_save_conditions_satisfied_count"),
        "save_true_allowed_count": save_summary.get("save_true_allowed_count"),
        "save_asset_allowed_count": save_summary.get("save_asset_allowed_count"),
        "compile_save_command_allowed_count": save_summary.get("compile_save_command_allowed_count"),
        "live_command_count": save_summary.get("live_command_count"),
        "executor_gate_simulation_evaluated_count": durable_gate_summary.get("save_simulation_evaluated_count"),
        "executor_gate_conditions_satisfied_count": durable_gate_summary.get(
            "save_simulation_conditions_satisfied_count"
        ),
        "executor_gate_save_true_allowed_count": durable_gate_summary.get("save_simulation_save_true_allowed_count"),
        "executor_gate_save_asset_allowed_count": durable_gate_summary.get("save_simulation_save_asset_allowed_count"),
        "executor_gate_live_command_count": durable_gate_summary.get("save_simulation_live_command_count"),
    }
    return row(
        "durable_save_validation_simulator",
        "Section 54 durable save validation simulator",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Simulator evaluates save prerequisites without save=true or save_asset.",
            "Failed conditions must keep durable save closed.",
        ),
    )


def build_durable_canary_prep_row(contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    canary_summary = contract_summary.get("durable_canary_prep_summary", {})
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_prep_count": 1,
        "canary_prep_ready_count": 1,
        "canary_live_execution_allowed_count": 0,
        "general_blueprints_package_allowed_count": 0,
        "save_true_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "executor_gate_canary_prep_ready_count": 1,
        "executor_gate_canary_live_allowed_count": 0,
        "executor_gate_general_blueprints_allowed_count": 0,
    }
    actual = {
        "summary_status": canary_summary.get("status"),
        "durable_requested_canary_prep_count": canary_summary.get("durable_requested_canary_prep_count"),
        "canary_prep_ready_count": canary_summary.get("canary_prep_ready_count"),
        "canary_live_execution_allowed_count": canary_summary.get("canary_live_execution_allowed_count"),
        "general_blueprints_package_allowed_count": canary_summary.get("general_blueprints_package_allowed_count"),
        "save_true_allowed_count": canary_summary.get("save_true_allowed_count"),
        "save_asset_allowed_count": canary_summary.get("save_asset_allowed_count"),
        "delete_asset_allowed_count": canary_summary.get("delete_asset_allowed_count"),
        "executor_gate_canary_prep_ready_count": durable_gate_summary.get("canary_prep_ready_count"),
        "executor_gate_canary_live_allowed_count": durable_gate_summary.get("canary_live_execution_allowed_count"),
        "executor_gate_general_blueprints_allowed_count": durable_gate_summary.get(
            "canary_general_blueprints_package_allowed_count"
        ),
    }
    return row(
        "durable_canary_prep_contract",
        "Section 55 durable canary prep contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Canary prep reserves a narrow target under /Game/_MCP_Temp/DurableCanary.",
            "Prep does not approve live durable canary execution.",
        ),
    )


def build_durable_canary_approval_row(
    contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]
) -> Dict[str, Any]:
    approval_summary = contract_summary.get("durable_canary_approval_summary", {})
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_approval_count": 1,
        "approval_record_present_count": 1,
        "canary_approval_gate_passed_count": 1,
        "approval_scoped_to_canary_package_count": 1,
        "canary_executor_may_open_count": 0,
        "canary_live_execution_allowed_count": 0,
        "general_blueprints_package_allowed_count": 0,
        "save_true_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "live_command_count": 0,
        "executor_gate_canary_approval_gate_passed_count": 1,
        "executor_gate_canary_executor_may_open_count": 0,
        "executor_gate_canary_live_allowed_count": 0,
    }
    actual = {
        "summary_status": approval_summary.get("status"),
        "durable_requested_canary_approval_count": approval_summary.get(
            "durable_requested_canary_approval_count"
        ),
        "approval_record_present_count": approval_summary.get("approval_record_present_count"),
        "canary_approval_gate_passed_count": approval_summary.get("canary_approval_gate_passed_count"),
        "approval_scoped_to_canary_package_count": approval_summary.get(
            "approval_scoped_to_canary_package_count"
        ),
        "canary_executor_may_open_count": approval_summary.get("canary_executor_may_open_count"),
        "canary_live_execution_allowed_count": approval_summary.get("canary_live_execution_allowed_count"),
        "general_blueprints_package_allowed_count": approval_summary.get(
            "general_blueprints_package_allowed_count"
        ),
        "save_true_allowed_count": approval_summary.get("save_true_allowed_count"),
        "save_asset_allowed_count": approval_summary.get("save_asset_allowed_count"),
        "delete_asset_allowed_count": approval_summary.get("delete_asset_allowed_count"),
        "live_command_count": approval_summary.get("live_command_count"),
        "executor_gate_canary_approval_gate_passed_count": durable_gate_summary.get(
            "canary_approval_gate_passed_count"
        ),
        "executor_gate_canary_executor_may_open_count": durable_gate_summary.get(
            "canary_approval_executor_may_open_count"
        ),
        "executor_gate_canary_live_allowed_count": durable_gate_summary.get(
            "canary_approval_live_execution_allowed_count"
        ),
    }
    return row(
        "durable_canary_approval_gate_contract",
        "Section 56 durable canary approval gate",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Canary approval must be explicit and scoped to /Game/_MCP_Temp/DurableCanary.",
            "Approval gate still does not open live durable canary execution.",
        ),
    )


def build_durable_canary_live_preflight_row(
    contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]
) -> Dict[str, Any]:
    live_summary = contract_summary.get("durable_canary_live_preflight_summary", {})
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_live_preflight_count": 1,
        "read_only_live_preflight_allowed_count": 1,
        "canary_execution_allowed_after_preflight_count": 0,
        "authoring_command_allowed_count": 0,
        "save_or_delete_allowed_count": 0,
        "cleanup_command_allowed_count": 0,
        "live_authoring_command_count": 0,
        "live_save_or_delete_command_count": 0,
        "live_cleanup_command_count": 0,
        "executor_gate_read_only_allowed_count": 1,
        "executor_gate_execution_allowed_count": 0,
        "executor_gate_save_or_delete_allowed_count": 0,
    }
    actual = {
        "summary_status": live_summary.get("status"),
        "durable_requested_canary_live_preflight_count": live_summary.get(
            "durable_requested_canary_live_preflight_count"
        ),
        "read_only_live_preflight_allowed_count": live_summary.get("read_only_live_preflight_allowed_count"),
        "canary_execution_allowed_after_preflight_count": live_summary.get(
            "canary_execution_allowed_after_preflight_count"
        ),
        "authoring_command_allowed_count": live_summary.get("authoring_command_allowed_count"),
        "save_or_delete_allowed_count": live_summary.get("save_or_delete_allowed_count"),
        "cleanup_command_allowed_count": live_summary.get("cleanup_command_allowed_count"),
        "live_authoring_command_count": live_summary.get("live_authoring_command_count"),
        "live_save_or_delete_command_count": live_summary.get("live_save_or_delete_command_count"),
        "live_cleanup_command_count": live_summary.get("live_cleanup_command_count"),
        "executor_gate_read_only_allowed_count": durable_gate_summary.get(
            "canary_live_preflight_read_only_allowed_count"
        ),
        "executor_gate_execution_allowed_count": durable_gate_summary.get(
            "canary_live_preflight_execution_allowed_count"
        ),
        "executor_gate_save_or_delete_allowed_count": durable_gate_summary.get(
            "canary_live_preflight_save_or_delete_allowed_count"
        ),
    }
    return row(
        "durable_canary_live_preflight_contract",
        "Section 57 durable canary live preflight",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Canary live preflight may only run a read-only asset-exists check.",
            "The contract still denies canary execution, save, delete, and cleanup commands.",
        ),
    )


def build_durable_canary_recovery_row(
    contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]
) -> Dict[str, Any]:
    recovery_summary = contract_summary.get("durable_canary_recovery_summary", {})
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_recovery_count": 1,
        "recovery_matrix_ready_count": 1,
        "scenario_count": 6,
        "cleanup_command_allowed_count": 0,
        "delete_command_allowed_count": 0,
        "save_command_allowed_count": 0,
        "authoring_command_allowed_count": 0,
        "live_cleanup_command_count": 0,
        "live_delete_command_count": 0,
        "live_save_command_count": 0,
        "live_authoring_command_count": 0,
        "executor_gate_recovery_matrix_ready_count": 1,
        "executor_gate_cleanup_allowed_count": 0,
        "executor_gate_delete_allowed_count": 0,
    }
    actual = {
        "summary_status": recovery_summary.get("status"),
        "durable_requested_canary_recovery_count": recovery_summary.get(
            "durable_requested_canary_recovery_count"
        ),
        "recovery_matrix_ready_count": recovery_summary.get("recovery_matrix_ready_count"),
        "scenario_count": recovery_summary.get("scenario_count"),
        "cleanup_command_allowed_count": recovery_summary.get("cleanup_command_allowed_count"),
        "delete_command_allowed_count": recovery_summary.get("delete_command_allowed_count"),
        "save_command_allowed_count": recovery_summary.get("save_command_allowed_count"),
        "authoring_command_allowed_count": recovery_summary.get("authoring_command_allowed_count"),
        "live_cleanup_command_count": recovery_summary.get("live_cleanup_command_count"),
        "live_delete_command_count": recovery_summary.get("live_delete_command_count"),
        "live_save_command_count": recovery_summary.get("live_save_command_count"),
        "live_authoring_command_count": recovery_summary.get("live_authoring_command_count"),
        "executor_gate_recovery_matrix_ready_count": durable_gate_summary.get("canary_recovery_matrix_ready_count"),
        "executor_gate_cleanup_allowed_count": durable_gate_summary.get("canary_recovery_cleanup_allowed_count"),
        "executor_gate_delete_allowed_count": durable_gate_summary.get("canary_recovery_delete_allowed_count"),
    }
    return row(
        "durable_canary_recovery_matrix",
        "Section 58 durable canary recovery matrix",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Recovery scenarios are report-only.",
            "Cleanup/delete remain disabled until a later explicit release.",
        ),
    )


def build_durable_canary_bridge_refresh_row(
    contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]
) -> Dict[str, Any]:
    bridge_summary = contract_summary.get("durable_canary_bridge_refresh_summary", {})
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "summary_status": "passed",
        "durable_requested_bridge_refresh_count": 1,
        "read_only_preflight_allowed_count": 1,
        "bridge_refresh_required_count": 1,
        "bridge_reachable_count": 0,
        "read_only_result_refreshed_count": 0,
        "bridge_refresh_satisfied_count": 0,
        "canary_execution_allowed_after_refresh_count": 0,
        "durable_executor_may_open_after_refresh_count": 0,
        "save_or_delete_allowed_count": 0,
        "cleanup_command_allowed_count": 0,
        "live_authoring_command_count": 0,
        "live_save_or_delete_command_count": 0,
        "live_cleanup_command_count": 0,
        "executor_gate_required_count": 1,
        "executor_gate_satisfied_count": 0,
        "executor_gate_execution_allowed_count": 0,
        "executor_gate_executor_may_open_count": 0,
    }
    actual = {
        "summary_status": bridge_summary.get("status"),
        "durable_requested_bridge_refresh_count": bridge_summary.get(
            "durable_requested_bridge_refresh_count"
        ),
        "read_only_preflight_allowed_count": bridge_summary.get("read_only_preflight_allowed_count"),
        "bridge_refresh_required_count": bridge_summary.get("bridge_refresh_required_count"),
        "bridge_reachable_count": bridge_summary.get("bridge_reachable_count"),
        "read_only_result_refreshed_count": bridge_summary.get("read_only_result_refreshed_count"),
        "bridge_refresh_satisfied_count": bridge_summary.get("bridge_refresh_satisfied_count"),
        "canary_execution_allowed_after_refresh_count": bridge_summary.get(
            "canary_execution_allowed_after_refresh_count"
        ),
        "durable_executor_may_open_after_refresh_count": bridge_summary.get(
            "durable_executor_may_open_after_refresh_count"
        ),
        "save_or_delete_allowed_count": bridge_summary.get("save_or_delete_allowed_count"),
        "cleanup_command_allowed_count": bridge_summary.get("cleanup_command_allowed_count"),
        "live_authoring_command_count": bridge_summary.get("live_authoring_command_count"),
        "live_save_or_delete_command_count": bridge_summary.get("live_save_or_delete_command_count"),
        "live_cleanup_command_count": bridge_summary.get("live_cleanup_command_count"),
        "executor_gate_required_count": durable_gate_summary.get("canary_bridge_refresh_required_count"),
        "executor_gate_satisfied_count": durable_gate_summary.get("canary_bridge_refresh_satisfied_count"),
        "executor_gate_execution_allowed_count": durable_gate_summary.get(
            "canary_bridge_refresh_execution_allowed_count"
        ),
        "executor_gate_executor_may_open_count": durable_gate_summary.get(
            "canary_bridge_refresh_executor_may_open_count"
        ),
    }
    return row(
        "durable_canary_bridge_refresh_contract",
        "Section 61 durable canary bridge refresh contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Bridge refresh and fresh read-only canary evidence are required before any future canary execution.",
            "Missing bridge evidence keeps execution closed rather than enabling durable authoring.",
        ),
    )


def build_live_evidence_refresh_row(planner_report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    contract = live_evidence_refresh.build_live_evidence_refresh_contract(
        requested=True,
        planner_report=planner_report,
    )
    summary = live_evidence_refresh.summarize_live_evidence_refresh_contracts([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_live_evidence_refresh_count": 1,
        "planner_live_report_present_count": 1,
        "canary_live_evidence_present_count": 0,
        "live_evidence_refresh_required_count": 1,
        "read_only_result_refreshed_count": 0,
        "live_evidence_refresh_satisfied_count": 0,
        "unsafe_live_attempt_count": 0,
        "durable_executor_may_open_after_report_refresh_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_or_delete_allowed_count": 0,
        "cleanup_allowed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_live_evidence_refresh_count": summary.get(
            "durable_requested_live_evidence_refresh_count"
        ),
        "planner_live_report_present_count": summary.get("planner_live_report_present_count"),
        "canary_live_evidence_present_count": summary.get("canary_live_evidence_present_count"),
        "live_evidence_refresh_required_count": summary.get("live_evidence_refresh_required_count"),
        "read_only_result_refreshed_count": summary.get("read_only_result_refreshed_count"),
        "live_evidence_refresh_satisfied_count": summary.get("live_evidence_refresh_satisfied_count"),
        "unsafe_live_attempt_count": summary.get("unsafe_live_attempt_count"),
        "durable_executor_may_open_after_report_refresh_count": summary.get(
            "durable_executor_may_open_after_report_refresh_count"
        ),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_or_delete_allowed_count": summary.get("save_or_delete_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
    }
    return row(
        "durable_live_evidence_refresh_contract",
        "Section 62 durable live evidence refresh contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Stored live evidence must include a fresh Section 57 canary read-only preflight before future canary execution.",
            "The current release boundary treats missing canary evidence as refresh-pending and executor-closed.",
        ),
    )


def build_executor_review_row(executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    contract = executor_review.build_executor_review_contract(
        requested=True,
        executor_summary=executor_summary,
    )
    summary = executor_review.summarize_executor_review_contracts([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_review_count": 1,
        "review_check_count": len(executor_review.REVIEW_CHECK_IDS),
        "disabled_executor_boundary_review_passed_count": 1,
        "durable_live_implementation_approved_count": 0,
        "durable_executor_may_open_after_review_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "canary_execution_allowed_count": 0,
        "failing_check_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_executor_review_count": summary.get("durable_requested_executor_review_count"),
        "review_check_count": summary.get("review_check_count"),
        "disabled_executor_boundary_review_passed_count": summary.get(
            "disabled_executor_boundary_review_passed_count"
        ),
        "durable_live_implementation_approved_count": summary.get("durable_live_implementation_approved_count"),
        "durable_executor_may_open_after_review_count": summary.get(
            "durable_executor_may_open_after_review_count"
        ),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "canary_execution_allowed_count": summary.get("canary_execution_allowed_count"),
        "failing_check_count": summary.get("failing_check_count"),
    }
    return row(
        "durable_executor_implementation_review_contract",
        "Section 63 durable executor implementation review contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The disabled durable executor boundary has been reviewed as closed.",
            "This review does not approve live durable implementation, save, delete, rename, or canary execution.",
        ),
    )


def build_canary_command_allowlist_row(executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    contract = canary_command_allowlist.build_canary_command_allowlist_contract(
        requested=True,
        executor_summary=executor_summary,
    )
    summary = canary_command_allowlist.summarize_canary_command_allowlist_contracts([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_command_allowlist_count": 1,
        "allowed_read_only_command_count": 1,
        "forbidden_command_count": len(canary_command_allowlist.FORBIDDEN_COMMANDS),
        "executor_gate_matches_allowlist_count": 1,
        "authoring_commands_allowed_count": 0,
        "save_commands_allowed_count": 0,
        "delete_commands_allowed_count": 0,
        "rename_commands_allowed_count": 0,
        "cleanup_commands_allowed_count": 0,
        "canary_execution_allowed_count": 0,
        "durable_executor_may_open_from_allowlist_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_command_allowlist_count": summary.get(
            "durable_requested_canary_command_allowlist_count"
        ),
        "allowed_read_only_command_count": summary.get("allowed_read_only_command_count"),
        "forbidden_command_count": summary.get("forbidden_command_count"),
        "executor_gate_matches_allowlist_count": summary.get("executor_gate_matches_allowlist_count"),
        "authoring_commands_allowed_count": summary.get("authoring_commands_allowed_count"),
        "save_commands_allowed_count": summary.get("save_commands_allowed_count"),
        "delete_commands_allowed_count": summary.get("delete_commands_allowed_count"),
        "rename_commands_allowed_count": summary.get("rename_commands_allowed_count"),
        "cleanup_commands_allowed_count": summary.get("cleanup_commands_allowed_count"),
        "canary_execution_allowed_count": summary.get("canary_execution_allowed_count"),
        "durable_executor_may_open_from_allowlist_count": summary.get(
            "durable_executor_may_open_from_allowlist_count"
        ),
    }
    return row(
        "durable_canary_command_allowlist_contract",
        "Section 64 durable canary command allowlist contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The canary allowlist contains only the read-only asset-exists command.",
            "Save, delete, rename, cleanup, authoring, and canary execution remain forbidden.",
        ),
    )


def build_canary_creation_boundary_row(
    contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]
) -> Dict[str, Any]:
    contract = canary_creation_boundary.build_canary_creation_boundary_contract(
        requested=True,
        contract_summary=contract_summary,
        executor_summary=executor_summary,
    )
    summary = canary_creation_boundary.summarize_canary_creation_boundary_contracts([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_creation_boundary_count": 1,
        "canary_creation_boundary_defined_count": 1,
        "create_blueprint_allowed_count": 0,
        "save_command_allowed_count": 0,
        "delete_command_allowed_count": 0,
        "cleanup_command_allowed_count": 0,
        "live_canary_creation_allowed_count": 0,
        "durable_executor_may_open_for_creation_count": 0,
        "live_creation_command_count": 0,
        "live_save_or_delete_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_creation_boundary_count": summary.get(
            "durable_requested_canary_creation_boundary_count"
        ),
        "canary_creation_boundary_defined_count": summary.get("canary_creation_boundary_defined_count"),
        "create_blueprint_allowed_count": summary.get("create_blueprint_allowed_count"),
        "save_command_allowed_count": summary.get("save_command_allowed_count"),
        "delete_command_allowed_count": summary.get("delete_command_allowed_count"),
        "cleanup_command_allowed_count": summary.get("cleanup_command_allowed_count"),
        "live_canary_creation_allowed_count": summary.get("live_canary_creation_allowed_count"),
        "durable_executor_may_open_for_creation_count": summary.get(
            "durable_executor_may_open_for_creation_count"
        ),
        "live_creation_command_count": summary.get("live_creation_command_count"),
        "live_save_or_delete_command_count": summary.get("live_save_or_delete_command_count"),
    }
    return row(
        "durable_canary_creation_boundary_contract",
        "Section 65 durable canary creation boundary contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Canary prep and approval are present, but create_blueprint remains outside the live allowlist.",
            "No canary creation, save, delete, cleanup, or executor opening is permitted.",
        ),
    )


def build_ownership_marker_proof_row(contract_summary: Dict[str, Any]) -> Dict[str, Any]:
    contract = ownership_marker_proof.build_ownership_marker_proof_contract(
        requested=True,
        contract_summary=contract_summary,
    )
    summary = ownership_marker_proof.summarize_ownership_marker_proof_contracts([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_ownership_marker_proof_count": 1,
        "ownership_marker_policy_ready_count": 1,
        "write_readback_proof_required_count": 1,
        "marker_write_performed_count": 0,
        "marker_readback_verified_count": 0,
        "write_readback_proof_satisfied_count": 0,
        "cleanup_allowed_after_marker_proof_count": 0,
        "delete_allowed_after_marker_proof_count": 0,
        "durable_executor_may_open_after_marker_proof_count": 0,
        "live_write_command_count": 0,
        "live_readback_command_count": 0,
        "live_delete_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_ownership_marker_proof_count": summary.get(
            "durable_requested_ownership_marker_proof_count"
        ),
        "ownership_marker_policy_ready_count": summary.get("ownership_marker_policy_ready_count"),
        "write_readback_proof_required_count": summary.get("write_readback_proof_required_count"),
        "marker_write_performed_count": summary.get("marker_write_performed_count"),
        "marker_readback_verified_count": summary.get("marker_readback_verified_count"),
        "write_readback_proof_satisfied_count": summary.get("write_readback_proof_satisfied_count"),
        "cleanup_allowed_after_marker_proof_count": summary.get("cleanup_allowed_after_marker_proof_count"),
        "delete_allowed_after_marker_proof_count": summary.get("delete_allowed_after_marker_proof_count"),
        "durable_executor_may_open_after_marker_proof_count": summary.get(
            "durable_executor_may_open_after_marker_proof_count"
        ),
        "live_write_command_count": summary.get("live_write_command_count"),
        "live_readback_command_count": summary.get("live_readback_command_count"),
        "live_delete_command_count": summary.get("live_delete_command_count"),
    }
    return row(
        "durable_ownership_marker_write_readback_proof_contract",
        "Section 66 durable ownership marker write/readback proof contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Ownership marker policy is ready, but write/readback proof has not been performed.",
            "Cleanup and delete remain disabled until a verified executor-created marker exists.",
        ),
    )


def build_rollback_cleanup_proof_row(contract_summary: Dict[str, Any]) -> Dict[str, Any]:
    marker_contract = ownership_marker_proof.build_ownership_marker_proof_contract(
        requested=True,
        contract_summary=contract_summary,
    )
    contract = rollback_cleanup_proof.build_rollback_cleanup_proof_contract(
        requested=True,
        contract_summary=contract_summary,
        marker_proof_contract=marker_contract,
    )
    summary = rollback_cleanup_proof.summarize_rollback_cleanup_proof_contracts([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_rollback_cleanup_proof_count": 1,
        "recovery_matrix_ready_count": 1,
        "cleanup_proof_required_count": 1,
        "ownership_marker_write_readback_satisfied_count": 0,
        "cleanup_proof_satisfied_count": 0,
        "cleanup_allowed_count": 0,
        "delete_allowed_count": 0,
        "delete_preexisting_asset_allowed_count": 0,
        "delete_without_marker_allowed_count": 0,
        "durable_executor_may_open_after_cleanup_proof_count": 0,
        "live_cleanup_command_count": 0,
        "live_delete_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_rollback_cleanup_proof_count": summary.get(
            "durable_requested_rollback_cleanup_proof_count"
        ),
        "recovery_matrix_ready_count": summary.get("recovery_matrix_ready_count"),
        "cleanup_proof_required_count": summary.get("cleanup_proof_required_count"),
        "ownership_marker_write_readback_satisfied_count": summary.get(
            "ownership_marker_write_readback_satisfied_count"
        ),
        "cleanup_proof_satisfied_count": summary.get("cleanup_proof_satisfied_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "delete_allowed_count": summary.get("delete_allowed_count"),
        "delete_preexisting_asset_allowed_count": summary.get("delete_preexisting_asset_allowed_count"),
        "delete_without_marker_allowed_count": summary.get("delete_without_marker_allowed_count"),
        "durable_executor_may_open_after_cleanup_proof_count": summary.get(
            "durable_executor_may_open_after_cleanup_proof_count"
        ),
        "live_cleanup_command_count": summary.get("live_cleanup_command_count"),
        "live_delete_command_count": summary.get("live_delete_command_count"),
    }
    return row(
        "durable_rollback_cleanup_proof_contract",
        "Section 67 durable rollback cleanup proof contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Recovery matrix is ready, but cleanup proof is blocked until ownership marker write/readback passes.",
            "Delete and cleanup commands remain disabled, including preexisting asset delete.",
        ),
    )


def build_save_gate_final_review_row(
    contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]
) -> Dict[str, Any]:
    contract = save_gate_final_review.build_save_gate_final_review_contract(
        requested=True,
        contract_summary=contract_summary,
        executor_summary=executor_summary,
    )
    summary = save_gate_final_review.summarize_save_gate_final_review_contracts([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_save_gate_final_review_count": 1,
        "save_gate_final_review_complete_count": 1,
        "missing_enable_prerequisite_count": 4,
        "durable_save_enable_ready_count": 0,
        "save_true_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "compile_save_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "durable_executor_may_open_after_save_review_count": 0,
        "live_save_command_count": 0,
        "live_delete_or_rename_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_save_gate_final_review_count": summary.get(
            "durable_requested_save_gate_final_review_count"
        ),
        "save_gate_final_review_complete_count": summary.get("save_gate_final_review_complete_count"),
        "missing_enable_prerequisite_count": summary.get("missing_enable_prerequisite_count"),
        "durable_save_enable_ready_count": summary.get("durable_save_enable_ready_count"),
        "save_true_allowed_count": summary.get("save_true_allowed_count"),
        "save_asset_allowed_count": summary.get("save_asset_allowed_count"),
        "compile_save_allowed_count": summary.get("compile_save_allowed_count"),
        "delete_asset_allowed_count": summary.get("delete_asset_allowed_count"),
        "rename_asset_allowed_count": summary.get("rename_asset_allowed_count"),
        "durable_executor_may_open_after_save_review_count": summary.get(
            "durable_executor_may_open_after_save_review_count"
        ),
        "live_save_command_count": summary.get("live_save_command_count"),
        "live_delete_or_rename_command_count": summary.get("live_delete_or_rename_command_count"),
    }
    return row(
        "durable_save_gate_final_enable_review_contract",
        "Section 68 durable save gate final enable review contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The save gate has been reviewed against current prerequisites.",
            "Missing overwrite/rollback/live preflight/save validation keeps save=true and save_asset disabled.",
        ),
    )


def build_canary_rehearsal_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    live_contract = live_evidence_refresh.build_live_evidence_refresh_contract(
        requested=True,
        planner_report=planner_report,
    )
    marker_contract = ownership_marker_proof.build_ownership_marker_proof_contract(
        requested=True,
        contract_summary=contract_summary,
    )
    cleanup_contract = rollback_cleanup_proof.build_rollback_cleanup_proof_contract(
        requested=True,
        contract_summary=contract_summary,
        marker_proof_contract=marker_contract,
    )
    save_contract = save_gate_final_review.build_save_gate_final_review_contract(
        requested=True,
        contract_summary=contract_summary,
        executor_summary=executor_summary,
    )
    contract = canary_rehearsal_readiness.build_canary_rehearsal_readiness_contract(
        requested=True,
        bridge_refresh_summary=contract_summary.get("durable_canary_bridge_refresh_summary", {}),
        live_evidence_summary=live_evidence_refresh.summarize_live_evidence_refresh_contracts([live_contract]),
        marker_proof_summary=ownership_marker_proof.summarize_ownership_marker_proof_contracts([marker_contract]),
        cleanup_proof_summary=rollback_cleanup_proof.summarize_rollback_cleanup_proof_contracts([cleanup_contract]),
        save_review_summary=save_gate_final_review.summarize_save_gate_final_review_contracts([save_contract]),
    )
    summary = canary_rehearsal_readiness.summarize_canary_rehearsal_readiness_contracts([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_rehearsal_readiness_count": 1,
        "rehearsal_readiness_review_complete_count": 1,
        "missing_rehearsal_prerequisite_count": 5,
        "live_canary_rehearsal_ready_count": 0,
        "live_canary_rehearsal_attempted_count": 0,
        "canary_creation_attempted_count": 0,
        "canary_save_attempted_count": 0,
        "canary_cleanup_attempted_count": 0,
        "durable_executor_may_open_for_rehearsal_count": 0,
        "live_creation_command_count": 0,
        "live_save_command_count": 0,
        "live_cleanup_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_rehearsal_readiness_count": summary.get(
            "durable_requested_canary_rehearsal_readiness_count"
        ),
        "rehearsal_readiness_review_complete_count": summary.get(
            "rehearsal_readiness_review_complete_count"
        ),
        "missing_rehearsal_prerequisite_count": summary.get("missing_rehearsal_prerequisite_count"),
        "live_canary_rehearsal_ready_count": summary.get("live_canary_rehearsal_ready_count"),
        "live_canary_rehearsal_attempted_count": summary.get("live_canary_rehearsal_attempted_count"),
        "canary_creation_attempted_count": summary.get("canary_creation_attempted_count"),
        "canary_save_attempted_count": summary.get("canary_save_attempted_count"),
        "canary_cleanup_attempted_count": summary.get("canary_cleanup_attempted_count"),
        "durable_executor_may_open_for_rehearsal_count": summary.get(
            "durable_executor_may_open_for_rehearsal_count"
        ),
        "live_creation_command_count": summary.get("live_creation_command_count"),
        "live_save_command_count": summary.get("live_save_command_count"),
        "live_cleanup_command_count": summary.get("live_cleanup_command_count"),
    }
    return row(
        "durable_canary_rehearsal_readiness_contract",
        "Section 69 durable live canary rehearsal readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Live canary rehearsal readiness has been reviewed and remains false.",
            "No creation, save, cleanup, or durable executor command is attempted.",
        ),
    )


def build_durable_release_decision_row(
    decision_contract: Dict[str, Any],
    executor_summary: Dict[str, Any],
    safety_contract_statuses: Sequence[str],
) -> Dict[str, Any]:
    contract = durable_release_decision.build_durable_release_decision_contract(
        requested=True,
        mvp_decision_contract=decision_contract,
        executor_summary=executor_summary,
        safety_contract_statuses=safety_contract_statuses,
    )
    summary = durable_release_decision.summarize_durable_release_decisions([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_release_decision_count": 1,
        "temporary_blueprint_authoring_mvp_ready_count": 1,
        "durable_blueprint_authoring_mvp_ready_count": 0,
        "durable_authoring_enabled_count": 0,
        "section_61_69_safety_contracts_passed_count": 1,
        "durable_executor_enabled_count": 0,
        "durable_executor_executable_count": 0,
        "save_or_delete_commands_allowed_count": 0,
        "allowed_live_authoring_command_count": 0,
        "preflight_pass_count": 0,
        "final_durable_release_ready_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_release_decision_count": summary.get("durable_requested_release_decision_count"),
        "temporary_blueprint_authoring_mvp_ready_count": summary.get(
            "temporary_blueprint_authoring_mvp_ready_count"
        ),
        "durable_blueprint_authoring_mvp_ready_count": summary.get(
            "durable_blueprint_authoring_mvp_ready_count"
        ),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "section_61_69_safety_contracts_passed_count": summary.get(
            "section_61_69_safety_contracts_passed_count"
        ),
        "durable_executor_enabled_count": summary.get("durable_executor_enabled_count"),
        "durable_executor_executable_count": summary.get("durable_executor_executable_count"),
        "save_or_delete_commands_allowed_count": summary.get("save_or_delete_commands_allowed_count"),
        "allowed_live_authoring_command_count": summary.get("allowed_live_authoring_command_count"),
        "preflight_pass_count": summary.get("preflight_pass_count"),
        "final_durable_release_ready_count": summary.get("final_durable_release_ready_count"),
    }
    return row(
        "section_70_durable_release_decision_contract",
        "Section 70 durable Blueprint authoring release decision",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Section 61-69 safety contracts are report-safe, but they do not enable durable authoring.",
            "Temporary Blueprint authoring remains the ready MVP; durable Blueprint authoring stays disabled.",
        ),
    )


def build_bridge_recovery_readiness_row(project_root: Path) -> Dict[str, Any]:
    recovery_inputs = bridge_recovery_readiness.collect_bridge_recovery_inputs(project_root)
    contract = bridge_recovery_readiness.build_bridge_recovery_readiness_contract(
        requested=True,
        recovery_inputs=recovery_inputs,
    )
    summary = bridge_recovery_readiness.summarize_bridge_recovery_readiness_contracts([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_bridge_recovery_readiness_count": 1,
        "local_recovery_inputs_ready_count": 1,
        "missing_recovery_input_count": 0,
        "bridge_socket_probe_performed_count": 0,
        "bridge_reachable_count": 0,
        "read_only_canary_retry_allowed_after_recovery_count": 0,
        "durable_executor_may_open_after_recovery_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "live_authoring_command_count": 0,
        "live_save_or_delete_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_bridge_recovery_readiness_count": summary.get(
            "durable_requested_bridge_recovery_readiness_count"
        ),
        "local_recovery_inputs_ready_count": summary.get("local_recovery_inputs_ready_count"),
        "missing_recovery_input_count": summary.get("missing_recovery_input_count"),
        "bridge_socket_probe_performed_count": summary.get("bridge_socket_probe_performed_count"),
        "bridge_reachable_count": summary.get("bridge_reachable_count"),
        "read_only_canary_retry_allowed_after_recovery_count": summary.get(
            "read_only_canary_retry_allowed_after_recovery_count"
        ),
        "durable_executor_may_open_after_recovery_count": summary.get(
            "durable_executor_may_open_after_recovery_count"
        ),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "live_authoring_command_count": summary.get("live_authoring_command_count"),
        "live_save_or_delete_command_count": summary.get("live_save_or_delete_command_count"),
    }
    return row(
        "durable_bridge_recovery_readiness_contract",
        "Section 71 durable bridge recovery readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Local UnrealMCP recovery inputs are present, but this row does not probe or open the bridge.",
            "A later live read-only retry must remain separate from durable save/delete/rename enablement.",
        ),
    )


def build_canary_read_only_retry_envelope_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
) -> Dict[str, Any]:
    recovery_contract = bridge_recovery_readiness.build_bridge_recovery_readiness_contract(
        requested=True,
        recovery_inputs=bridge_recovery_readiness.collect_bridge_recovery_inputs(project_root),
    )
    allowlist_contract = canary_command_allowlist.build_canary_command_allowlist_contract(
        requested=True,
        executor_summary=executor_summary,
    )
    contract = canary_read_only_retry.build_canary_read_only_retry_envelope_contract(
        requested=True,
        bridge_recovery_summary=bridge_recovery_readiness.summarize_bridge_recovery_readiness_contracts(
            [recovery_contract]
        ),
        canary_live_preflight_summary=contract_summary.get("durable_canary_live_preflight_summary", {}),
        command_allowlist_summary=canary_command_allowlist.summarize_canary_command_allowlist_contracts(
            [allowlist_contract]
        ),
    )
    summary = canary_read_only_retry.summarize_canary_read_only_retry_envelopes([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_read_only_retry_envelope_count": 1,
        "read_only_retry_envelope_defined_count": 1,
        "read_only_command_count": 1,
        "missing_retry_prerequisite_count": 2,
        "read_only_retry_prerequisites_satisfied_count": 0,
        "live_read_only_retry_allowed_count": 0,
        "live_read_only_retry_performed_count": 0,
        "live_read_only_result_recorded_count": 0,
        "canary_execution_allowed_after_retry_count": 0,
        "durable_executor_may_open_after_retry_count": 0,
        "authoring_command_allowed_count": 0,
        "save_or_delete_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_authoring_command_count": 0,
        "live_save_or_delete_command_count": 0,
        "live_cleanup_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_read_only_retry_envelope_count": summary.get(
            "durable_requested_canary_read_only_retry_envelope_count"
        ),
        "read_only_retry_envelope_defined_count": summary.get("read_only_retry_envelope_defined_count"),
        "read_only_command_count": summary.get("read_only_command_count"),
        "missing_retry_prerequisite_count": summary.get("missing_retry_prerequisite_count"),
        "read_only_retry_prerequisites_satisfied_count": summary.get(
            "read_only_retry_prerequisites_satisfied_count"
        ),
        "live_read_only_retry_allowed_count": summary.get("live_read_only_retry_allowed_count"),
        "live_read_only_retry_performed_count": summary.get("live_read_only_retry_performed_count"),
        "live_read_only_result_recorded_count": summary.get("live_read_only_result_recorded_count"),
        "canary_execution_allowed_after_retry_count": summary.get("canary_execution_allowed_after_retry_count"),
        "durable_executor_may_open_after_retry_count": summary.get("durable_executor_may_open_after_retry_count"),
        "authoring_command_allowed_count": summary.get("authoring_command_allowed_count"),
        "save_or_delete_allowed_count": summary.get("save_or_delete_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_authoring_command_count": summary.get("live_authoring_command_count"),
        "live_save_or_delete_command_count": summary.get("live_save_or_delete_command_count"),
        "live_cleanup_command_count": summary.get("live_cleanup_command_count"),
    }
    return row(
        "durable_canary_read_only_retry_envelope_contract",
        "Section 72 durable canary read-only retry envelope contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The retry envelope is defined, but live retry is not allowed or performed by offline release review.",
            "Bridge reachability and explicit live retry invocation remain separate prerequisites.",
        ),
    )


def build_canary_read_only_retry_result_admission_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
) -> Dict[str, Any]:
    recovery_contract = bridge_recovery_readiness.build_bridge_recovery_readiness_contract(
        requested=True,
        recovery_inputs=bridge_recovery_readiness.collect_bridge_recovery_inputs(project_root),
    )
    allowlist_contract = canary_command_allowlist.build_canary_command_allowlist_contract(
        requested=True,
        executor_summary=executor_summary,
    )
    retry_envelope_contract = canary_read_only_retry.build_canary_read_only_retry_envelope_contract(
        requested=True,
        bridge_recovery_summary=bridge_recovery_readiness.summarize_bridge_recovery_readiness_contracts(
            [recovery_contract]
        ),
        canary_live_preflight_summary=contract_summary.get("durable_canary_live_preflight_summary", {}),
        command_allowlist_summary=canary_command_allowlist.summarize_canary_command_allowlist_contracts(
            [allowlist_contract]
        ),
    )
    contract = retry_result_admission.build_canary_read_only_retry_result_admission_contract(
        requested=True,
        retry_envelope_summary=canary_read_only_retry.summarize_canary_read_only_retry_envelopes(
            [retry_envelope_contract]
        ),
    )
    summary = retry_result_admission.summarize_canary_read_only_retry_result_admissions([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_read_only_retry_result_admission_count": 1,
        "retry_result_admission_contract_defined_count": 1,
        "live_read_only_retry_result_present_count": 0,
        "result_schema_matches_count": 0,
        "explicit_live_read_only_retry_authorized_count": 0,
        "read_only_command_matches_count": 0,
        "result_status_passed_count": 0,
        "read_only_result_count": 0,
        "asset_exists_check_performed_count": 0,
        "read_only_result_admitted_count": 0,
        "missing_admission_prerequisite_count": 2,
        "rejected_retry_result_count": 0,
        "unsafe_retry_result_count": 0,
        "canary_execution_allowed_after_retry_result_count": 0,
        "durable_executor_may_open_after_retry_result_count": 0,
        "authoring_command_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_authoring_command_count": 0,
        "live_save_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
        "live_canary_execution_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_read_only_retry_result_admission_count": summary.get(
            "durable_requested_canary_read_only_retry_result_admission_count"
        ),
        "retry_result_admission_contract_defined_count": summary.get(
            "retry_result_admission_contract_defined_count"
        ),
        "live_read_only_retry_result_present_count": summary.get(
            "live_read_only_retry_result_present_count"
        ),
        "result_schema_matches_count": summary.get("result_schema_matches_count"),
        "explicit_live_read_only_retry_authorized_count": summary.get(
            "explicit_live_read_only_retry_authorized_count"
        ),
        "read_only_command_matches_count": summary.get("read_only_command_matches_count"),
        "result_status_passed_count": summary.get("result_status_passed_count"),
        "read_only_result_count": summary.get("read_only_result_count"),
        "asset_exists_check_performed_count": summary.get("asset_exists_check_performed_count"),
        "read_only_result_admitted_count": summary.get("read_only_result_admitted_count"),
        "missing_admission_prerequisite_count": summary.get("missing_admission_prerequisite_count"),
        "rejected_retry_result_count": summary.get("rejected_retry_result_count"),
        "unsafe_retry_result_count": summary.get("unsafe_retry_result_count"),
        "canary_execution_allowed_after_retry_result_count": summary.get(
            "canary_execution_allowed_after_retry_result_count"
        ),
        "durable_executor_may_open_after_retry_result_count": summary.get(
            "durable_executor_may_open_after_retry_result_count"
        ),
        "authoring_command_allowed_count": summary.get("authoring_command_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_authoring_command_count": summary.get("live_authoring_command_count"),
        "live_save_delete_rename_command_count": summary.get("live_save_delete_rename_command_count"),
        "live_cleanup_command_count": summary.get("live_cleanup_command_count"),
        "live_canary_execution_command_count": summary.get("live_canary_execution_command_count"),
    }
    return row(
        "durable_canary_read_only_retry_result_admission_contract",
        "Section 73 durable canary read-only retry result admission contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "No live retry result is admitted by the offline release boundary.",
            "A future result must be explicitly authorized, schema-matched, read-only, and free of authoring commands.",
        ),
    )


def build_canary_rehearsal_promotion_barrier_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    recovery_contract = bridge_recovery_readiness.build_bridge_recovery_readiness_contract(
        requested=True,
        recovery_inputs=bridge_recovery_readiness.collect_bridge_recovery_inputs(project_root),
    )
    allowlist_contract = canary_command_allowlist.build_canary_command_allowlist_contract(
        requested=True,
        executor_summary=executor_summary,
    )
    retry_envelope_contract = canary_read_only_retry.build_canary_read_only_retry_envelope_contract(
        requested=True,
        bridge_recovery_summary=bridge_recovery_readiness.summarize_bridge_recovery_readiness_contracts(
            [recovery_contract]
        ),
        canary_live_preflight_summary=contract_summary.get("durable_canary_live_preflight_summary", {}),
        command_allowlist_summary=canary_command_allowlist.summarize_canary_command_allowlist_contracts(
            [allowlist_contract]
        ),
    )
    retry_admission_contract = retry_result_admission.build_canary_read_only_retry_result_admission_contract(
        requested=True,
        retry_envelope_summary=canary_read_only_retry.summarize_canary_read_only_retry_envelopes(
            [retry_envelope_contract]
        ),
    )
    live_contract = live_evidence_refresh.build_live_evidence_refresh_contract(
        requested=True,
        planner_report=planner_report,
    )
    marker_contract = ownership_marker_proof.build_ownership_marker_proof_contract(
        requested=True,
        contract_summary=contract_summary,
    )
    cleanup_contract = rollback_cleanup_proof.build_rollback_cleanup_proof_contract(
        requested=True,
        contract_summary=contract_summary,
        marker_proof_contract=marker_contract,
    )
    save_contract = save_gate_final_review.build_save_gate_final_review_contract(
        requested=True,
        contract_summary=contract_summary,
        executor_summary=executor_summary,
    )
    rehearsal_contract = canary_rehearsal_readiness.build_canary_rehearsal_readiness_contract(
        requested=True,
        bridge_refresh_summary=contract_summary.get("durable_canary_bridge_refresh_summary", {}),
        live_evidence_summary=live_evidence_refresh.summarize_live_evidence_refresh_contracts([live_contract]),
        marker_proof_summary=ownership_marker_proof.summarize_ownership_marker_proof_contracts([marker_contract]),
        cleanup_proof_summary=rollback_cleanup_proof.summarize_rollback_cleanup_proof_contracts([cleanup_contract]),
        save_review_summary=save_gate_final_review.summarize_save_gate_final_review_contracts([save_contract]),
    )
    contract = rehearsal_promotion_barrier.build_canary_rehearsal_promotion_barrier_contract(
        requested=True,
        retry_result_admission_summary=retry_result_admission.summarize_canary_read_only_retry_result_admissions(
            [retry_admission_contract]
        ),
        rehearsal_readiness_summary=canary_rehearsal_readiness.summarize_canary_rehearsal_readiness_contracts(
            [rehearsal_contract]
        ),
        marker_proof_summary=ownership_marker_proof.summarize_ownership_marker_proof_contracts([marker_contract]),
        cleanup_proof_summary=rollback_cleanup_proof.summarize_rollback_cleanup_proof_contracts([cleanup_contract]),
        save_review_summary=save_gate_final_review.summarize_save_gate_final_review_contracts([save_contract]),
    )
    summary = rehearsal_promotion_barrier.summarize_canary_rehearsal_promotion_barriers([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_rehearsal_promotion_barrier_count": 1,
        "promotion_barrier_defined_count": 1,
        "read_only_result_admitted_count": 0,
        "rehearsal_readiness_review_complete_count": 1,
        "promotion_inputs_satisfied_count": 0,
        "promotion_execution_release_present_count": 0,
        "missing_promotion_prerequisite_count": 7,
        "canary_rehearsal_promotion_allowed_count": 0,
        "live_canary_rehearsal_allowed_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_promotion_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_creation_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_rehearsal_promotion_barrier_count": summary.get(
            "durable_requested_canary_rehearsal_promotion_barrier_count"
        ),
        "promotion_barrier_defined_count": summary.get("promotion_barrier_defined_count"),
        "read_only_result_admitted_count": summary.get("read_only_result_admitted_count"),
        "rehearsal_readiness_review_complete_count": summary.get("rehearsal_readiness_review_complete_count"),
        "promotion_inputs_satisfied_count": summary.get("promotion_inputs_satisfied_count"),
        "promotion_execution_release_present_count": summary.get("promotion_execution_release_present_count"),
        "missing_promotion_prerequisite_count": summary.get("missing_promotion_prerequisite_count"),
        "canary_rehearsal_promotion_allowed_count": summary.get("canary_rehearsal_promotion_allowed_count"),
        "live_canary_rehearsal_allowed_count": summary.get("live_canary_rehearsal_allowed_count"),
        "live_canary_rehearsal_performed_count": summary.get("live_canary_rehearsal_performed_count"),
        "canary_creation_allowed_count": summary.get("canary_creation_allowed_count"),
        "canary_save_allowed_count": summary.get("canary_save_allowed_count"),
        "canary_cleanup_allowed_count": summary.get("canary_cleanup_allowed_count"),
        "durable_executor_may_open_after_promotion_count": summary.get(
            "durable_executor_may_open_after_promotion_count"
        ),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_creation_command_count": summary.get("live_creation_command_count"),
        "live_save_command_count": summary.get("live_save_command_count"),
        "live_delete_rename_command_count": summary.get("live_delete_rename_command_count"),
        "live_cleanup_command_count": summary.get("live_cleanup_command_count"),
    }
    return row(
        "durable_canary_rehearsal_promotion_barrier_contract",
        "Section 74 durable canary rehearsal promotion barrier contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "An admitted read-only retry result cannot promote itself to live canary rehearsal.",
            "A separate durable rehearsal execution release is still required before any live authoring command.",
        ),
    )


def build_canary_rehearsal_execution_release_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    recovery_contract = bridge_recovery_readiness.build_bridge_recovery_readiness_contract(
        requested=True,
        recovery_inputs=bridge_recovery_readiness.collect_bridge_recovery_inputs(project_root),
    )
    allowlist_contract = canary_command_allowlist.build_canary_command_allowlist_contract(
        requested=True,
        executor_summary=executor_summary,
    )
    retry_envelope_contract = canary_read_only_retry.build_canary_read_only_retry_envelope_contract(
        requested=True,
        bridge_recovery_summary=bridge_recovery_readiness.summarize_bridge_recovery_readiness_contracts(
            [recovery_contract]
        ),
        canary_live_preflight_summary=contract_summary.get("durable_canary_live_preflight_summary", {}),
        command_allowlist_summary=canary_command_allowlist.summarize_canary_command_allowlist_contracts(
            [allowlist_contract]
        ),
    )
    retry_admission_contract = retry_result_admission.build_canary_read_only_retry_result_admission_contract(
        requested=True,
        retry_envelope_summary=canary_read_only_retry.summarize_canary_read_only_retry_envelopes(
            [retry_envelope_contract]
        ),
    )
    live_contract = live_evidence_refresh.build_live_evidence_refresh_contract(
        requested=True,
        planner_report=planner_report,
    )
    marker_contract = ownership_marker_proof.build_ownership_marker_proof_contract(
        requested=True,
        contract_summary=contract_summary,
    )
    cleanup_contract = rollback_cleanup_proof.build_rollback_cleanup_proof_contract(
        requested=True,
        contract_summary=contract_summary,
        marker_proof_contract=marker_contract,
    )
    save_contract = save_gate_final_review.build_save_gate_final_review_contract(
        requested=True,
        contract_summary=contract_summary,
        executor_summary=executor_summary,
    )
    rehearsal_contract = canary_rehearsal_readiness.build_canary_rehearsal_readiness_contract(
        requested=True,
        bridge_refresh_summary=contract_summary.get("durable_canary_bridge_refresh_summary", {}),
        live_evidence_summary=live_evidence_refresh.summarize_live_evidence_refresh_contracts([live_contract]),
        marker_proof_summary=ownership_marker_proof.summarize_ownership_marker_proof_contracts([marker_contract]),
        cleanup_proof_summary=rollback_cleanup_proof.summarize_rollback_cleanup_proof_contracts([cleanup_contract]),
        save_review_summary=save_gate_final_review.summarize_save_gate_final_review_contracts([save_contract]),
    )
    promotion_contract = rehearsal_promotion_barrier.build_canary_rehearsal_promotion_barrier_contract(
        requested=True,
        retry_result_admission_summary=retry_result_admission.summarize_canary_read_only_retry_result_admissions(
            [retry_admission_contract]
        ),
        rehearsal_readiness_summary=canary_rehearsal_readiness.summarize_canary_rehearsal_readiness_contracts(
            [rehearsal_contract]
        ),
        marker_proof_summary=ownership_marker_proof.summarize_ownership_marker_proof_contracts([marker_contract]),
        cleanup_proof_summary=rollback_cleanup_proof.summarize_rollback_cleanup_proof_contracts([cleanup_contract]),
        save_review_summary=save_gate_final_review.summarize_save_gate_final_review_contracts([save_contract]),
    )
    contract = rehearsal_execution_release.build_canary_rehearsal_execution_release_contract(
        requested=True,
        promotion_barrier_summary=rehearsal_promotion_barrier.summarize_canary_rehearsal_promotion_barriers(
            [promotion_contract]
        ),
    )
    summary = rehearsal_execution_release.summarize_canary_rehearsal_execution_releases([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_rehearsal_execution_release_count": 1,
        "execution_release_contract_defined_count": 1,
        "promotion_barrier_defined_count": 1,
        "promotion_inputs_satisfied_count": 0,
        "release_record_present_count": 0,
        "record_schema_matches_count": 0,
        "release_scope_matches_count": 0,
        "explicit_execution_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "release_record_valid_count": 0,
        "release_record_rejected_count": 0,
        "unsafe_release_record_count": 0,
        "missing_release_prerequisite_count": 7,
        "live_canary_rehearsal_release_allowed_count": 0,
        "live_canary_rehearsal_execution_allowed_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_execution_release_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_creation_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_rehearsal_execution_release_count": summary.get(
            "durable_requested_canary_rehearsal_execution_release_count"
        ),
        "execution_release_contract_defined_count": summary.get("execution_release_contract_defined_count"),
        "promotion_barrier_defined_count": summary.get("promotion_barrier_defined_count"),
        "promotion_inputs_satisfied_count": summary.get("promotion_inputs_satisfied_count"),
        "release_record_present_count": summary.get("release_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "release_scope_matches_count": summary.get("release_scope_matches_count"),
        "explicit_execution_authorized_count": summary.get("explicit_execution_authorized_count"),
        "no_save_delete_rename_acknowledged_count": summary.get("no_save_delete_rename_acknowledged_count"),
        "release_record_valid_count": summary.get("release_record_valid_count"),
        "release_record_rejected_count": summary.get("release_record_rejected_count"),
        "unsafe_release_record_count": summary.get("unsafe_release_record_count"),
        "missing_release_prerequisite_count": summary.get("missing_release_prerequisite_count"),
        "live_canary_rehearsal_release_allowed_count": summary.get(
            "live_canary_rehearsal_release_allowed_count"
        ),
        "live_canary_rehearsal_execution_allowed_count": summary.get(
            "live_canary_rehearsal_execution_allowed_count"
        ),
        "live_canary_rehearsal_performed_count": summary.get("live_canary_rehearsal_performed_count"),
        "canary_creation_allowed_count": summary.get("canary_creation_allowed_count"),
        "canary_save_allowed_count": summary.get("canary_save_allowed_count"),
        "canary_cleanup_allowed_count": summary.get("canary_cleanup_allowed_count"),
        "durable_executor_may_open_after_execution_release_count": summary.get(
            "durable_executor_may_open_after_execution_release_count"
        ),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_creation_command_count": summary.get("live_creation_command_count"),
        "live_save_command_count": summary.get("live_save_command_count"),
        "live_delete_rename_command_count": summary.get("live_delete_rename_command_count"),
        "live_cleanup_command_count": summary.get("live_cleanup_command_count"),
    }
    return row(
        "durable_canary_rehearsal_execution_release_contract",
        "Section 75 durable canary rehearsal execution release contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The execution release contract is defined, but no release record is present.",
            "Even a scoped release record would still need a separate live runner release before commands run.",
        ),
    )


def build_canary_live_runner_envelope_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    recovery_contract = bridge_recovery_readiness.build_bridge_recovery_readiness_contract(
        requested=True,
        recovery_inputs=bridge_recovery_readiness.collect_bridge_recovery_inputs(project_root),
    )
    allowlist_contract = canary_command_allowlist.build_canary_command_allowlist_contract(
        requested=True,
        executor_summary=executor_summary,
    )
    retry_envelope_contract = canary_read_only_retry.build_canary_read_only_retry_envelope_contract(
        requested=True,
        bridge_recovery_summary=bridge_recovery_readiness.summarize_bridge_recovery_readiness_contracts(
            [recovery_contract]
        ),
        canary_live_preflight_summary=contract_summary.get("durable_canary_live_preflight_summary", {}),
        command_allowlist_summary=canary_command_allowlist.summarize_canary_command_allowlist_contracts(
            [allowlist_contract]
        ),
    )
    retry_admission_contract = retry_result_admission.build_canary_read_only_retry_result_admission_contract(
        requested=True,
        retry_envelope_summary=canary_read_only_retry.summarize_canary_read_only_retry_envelopes(
            [retry_envelope_contract]
        ),
    )
    live_contract = live_evidence_refresh.build_live_evidence_refresh_contract(
        requested=True,
        planner_report=planner_report,
    )
    marker_contract = ownership_marker_proof.build_ownership_marker_proof_contract(
        requested=True,
        contract_summary=contract_summary,
    )
    cleanup_contract = rollback_cleanup_proof.build_rollback_cleanup_proof_contract(
        requested=True,
        contract_summary=contract_summary,
        marker_proof_contract=marker_contract,
    )
    save_contract = save_gate_final_review.build_save_gate_final_review_contract(
        requested=True,
        contract_summary=contract_summary,
        executor_summary=executor_summary,
    )
    rehearsal_contract = canary_rehearsal_readiness.build_canary_rehearsal_readiness_contract(
        requested=True,
        bridge_refresh_summary=contract_summary.get("durable_canary_bridge_refresh_summary", {}),
        live_evidence_summary=live_evidence_refresh.summarize_live_evidence_refresh_contracts([live_contract]),
        marker_proof_summary=ownership_marker_proof.summarize_ownership_marker_proof_contracts([marker_contract]),
        cleanup_proof_summary=rollback_cleanup_proof.summarize_rollback_cleanup_proof_contracts([cleanup_contract]),
        save_review_summary=save_gate_final_review.summarize_save_gate_final_review_contracts([save_contract]),
    )
    promotion_contract = rehearsal_promotion_barrier.build_canary_rehearsal_promotion_barrier_contract(
        requested=True,
        retry_result_admission_summary=retry_result_admission.summarize_canary_read_only_retry_result_admissions(
            [retry_admission_contract]
        ),
        rehearsal_readiness_summary=canary_rehearsal_readiness.summarize_canary_rehearsal_readiness_contracts(
            [rehearsal_contract]
        ),
        marker_proof_summary=ownership_marker_proof.summarize_ownership_marker_proof_contracts([marker_contract]),
        cleanup_proof_summary=rollback_cleanup_proof.summarize_rollback_cleanup_proof_contracts([cleanup_contract]),
        save_review_summary=save_gate_final_review.summarize_save_gate_final_review_contracts([save_contract]),
    )
    execution_release_contract = rehearsal_execution_release.build_canary_rehearsal_execution_release_contract(
        requested=True,
        promotion_barrier_summary=rehearsal_promotion_barrier.summarize_canary_rehearsal_promotion_barriers(
            [promotion_contract]
        ),
    )
    contract = live_runner_envelope.build_canary_live_runner_envelope_contract(
        requested=True,
        execution_release_summary=rehearsal_execution_release.summarize_canary_rehearsal_execution_releases(
            [execution_release_contract]
        ),
    )
    summary = live_runner_envelope.summarize_canary_live_runner_envelopes([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_live_runner_envelope_count": 1,
        "live_runner_envelope_defined_count": 1,
        "execution_release_contract_ready_count": 1,
        "execution_release_valid_count": 0,
        "live_runner_release_allowed_count": 0,
        "runner_plan_present_count": 0,
        "runner_plan_schema_matches_count": 0,
        "planned_command_count": 0,
        "forbidden_runner_command_count": 0,
        "unknown_runner_command_count": 0,
        "runner_plan_valid_count": 0,
        "runner_plan_rejected_count": 0,
        "missing_runner_prerequisite_count": 6,
        "live_runner_may_start_count": 0,
        "live_runner_started_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_runner_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_creation_command_count": 0,
        "live_compile_command_count": 0,
        "live_marker_write_command_count": 0,
        "live_marker_readback_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_live_runner_envelope_count": summary.get(
            "durable_requested_canary_live_runner_envelope_count"
        ),
        "live_runner_envelope_defined_count": summary.get("live_runner_envelope_defined_count"),
        "execution_release_contract_ready_count": summary.get("execution_release_contract_ready_count"),
        "execution_release_valid_count": summary.get("execution_release_valid_count"),
        "live_runner_release_allowed_count": summary.get("live_runner_release_allowed_count"),
        "runner_plan_present_count": summary.get("runner_plan_present_count"),
        "runner_plan_schema_matches_count": summary.get("runner_plan_schema_matches_count"),
        "planned_command_count": summary.get("planned_command_count"),
        "forbidden_runner_command_count": summary.get("forbidden_runner_command_count"),
        "unknown_runner_command_count": summary.get("unknown_runner_command_count"),
        "runner_plan_valid_count": summary.get("runner_plan_valid_count"),
        "runner_plan_rejected_count": summary.get("runner_plan_rejected_count"),
        "missing_runner_prerequisite_count": summary.get("missing_runner_prerequisite_count"),
        "live_runner_may_start_count": summary.get("live_runner_may_start_count"),
        "live_runner_started_count": summary.get("live_runner_started_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_canary_rehearsal_performed_count": summary.get("live_canary_rehearsal_performed_count"),
        "canary_creation_allowed_count": summary.get("canary_creation_allowed_count"),
        "canary_save_allowed_count": summary.get("canary_save_allowed_count"),
        "canary_cleanup_allowed_count": summary.get("canary_cleanup_allowed_count"),
        "durable_executor_may_open_after_runner_count": summary.get("durable_executor_may_open_after_runner_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_creation_command_count": summary.get("live_creation_command_count"),
        "live_compile_command_count": summary.get("live_compile_command_count"),
        "live_marker_write_command_count": summary.get("live_marker_write_command_count"),
        "live_marker_readback_command_count": summary.get("live_marker_readback_command_count"),
        "live_save_command_count": summary.get("live_save_command_count"),
        "live_delete_rename_command_count": summary.get("live_delete_rename_command_count"),
        "live_cleanup_command_count": summary.get("live_cleanup_command_count"),
    }
    return row(
        "durable_canary_live_runner_envelope_contract",
        "Section 76 durable canary live runner envelope contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The live runner envelope is defined, but no runner plan or start action is present.",
            "Forbidden save/delete/rename/cleanup commands stay outside the live runner envelope.",
        ),
    )


def build_canary_live_runner_start_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    envelope_row = build_canary_live_runner_envelope_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    runner_envelope_summary = dict(envelope_row["actual"])
    runner_envelope_summary["status"] = runner_envelope_summary.pop("summary_status")
    contract = live_runner_start.build_canary_live_runner_start_contract(
        requested=True,
        runner_envelope_summary=runner_envelope_summary,
    )
    summary = live_runner_start.summarize_canary_live_runner_starts([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_live_runner_start_count": 1,
        "start_contract_defined_count": 1,
        "runner_envelope_ready_count": 1,
        "runner_plan_valid_count": 0,
        "runner_start_allowed_by_envelope_count": 0,
        "start_record_present_count": 0,
        "record_schema_matches_count": 0,
        "start_scope_matches_count": 0,
        "explicit_operator_start_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "start_record_valid_count": 0,
        "start_record_rejected_count": 0,
        "unsafe_start_record_count": 0,
        "missing_start_prerequisite_count": 8,
        "live_runner_start_allowed_count": 0,
        "live_runner_started_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_runner_start_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_creation_command_count": 0,
        "live_compile_command_count": 0,
        "live_marker_write_command_count": 0,
        "live_marker_readback_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_live_runner_start_count": summary.get(
            "durable_requested_canary_live_runner_start_count"
        ),
        "start_contract_defined_count": summary.get("start_contract_defined_count"),
        "runner_envelope_ready_count": summary.get("runner_envelope_ready_count"),
        "runner_plan_valid_count": summary.get("runner_plan_valid_count"),
        "runner_start_allowed_by_envelope_count": summary.get("runner_start_allowed_by_envelope_count"),
        "start_record_present_count": summary.get("start_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "start_scope_matches_count": summary.get("start_scope_matches_count"),
        "explicit_operator_start_authorized_count": summary.get("explicit_operator_start_authorized_count"),
        "no_save_delete_rename_acknowledged_count": summary.get("no_save_delete_rename_acknowledged_count"),
        "start_record_valid_count": summary.get("start_record_valid_count"),
        "start_record_rejected_count": summary.get("start_record_rejected_count"),
        "unsafe_start_record_count": summary.get("unsafe_start_record_count"),
        "missing_start_prerequisite_count": summary.get("missing_start_prerequisite_count"),
        "live_runner_start_allowed_count": summary.get("live_runner_start_allowed_count"),
        "live_runner_started_count": summary.get("live_runner_started_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_canary_rehearsal_performed_count": summary.get("live_canary_rehearsal_performed_count"),
        "canary_creation_allowed_count": summary.get("canary_creation_allowed_count"),
        "canary_save_allowed_count": summary.get("canary_save_allowed_count"),
        "canary_cleanup_allowed_count": summary.get("canary_cleanup_allowed_count"),
        "durable_executor_may_open_after_runner_start_count": summary.get(
            "durable_executor_may_open_after_runner_start_count"
        ),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_creation_command_count": summary.get("live_creation_command_count"),
        "live_compile_command_count": summary.get("live_compile_command_count"),
        "live_marker_write_command_count": summary.get("live_marker_write_command_count"),
        "live_marker_readback_command_count": summary.get("live_marker_readback_command_count"),
        "live_save_command_count": summary.get("live_save_command_count"),
        "live_delete_rename_command_count": summary.get("live_delete_rename_command_count"),
        "live_cleanup_command_count": summary.get("live_cleanup_command_count"),
    }
    return row(
        "durable_canary_live_runner_start_contract",
        "Section 77 durable canary live runner start contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The runner start contract is defined, but no operator start record is present.",
            "Command dispatch remains behind a separate release; no live commands are emitted.",
        ),
    )


def build_canary_live_command_dispatch_release_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    runner_start_row = build_canary_live_runner_start_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    runner_start_summary = dict(runner_start_row["actual"])
    runner_start_summary["status"] = runner_start_summary.pop("summary_status")
    contract = live_command_dispatch_release.build_canary_live_command_dispatch_release_contract(
        requested=True,
        runner_start_summary=runner_start_summary,
    )
    summary = live_command_dispatch_release.summarize_canary_live_command_dispatch_releases([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_live_command_dispatch_release_count": 1,
        "dispatch_release_contract_defined_count": 1,
        "start_contract_ready_count": 1,
        "runner_plan_valid_count": 0,
        "start_record_valid_count": 0,
        "live_runner_started_count": 0,
        "dispatch_inputs_satisfied_count": 0,
        "dispatch_record_present_count": 0,
        "record_schema_matches_count": 0,
        "dispatch_scope_matches_count": 0,
        "explicit_dispatch_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "dispatch_release_record_valid_count": 0,
        "dispatch_release_record_rejected_count": 0,
        "unsafe_dispatch_release_record_count": 0,
        "missing_dispatch_prerequisite_count": 9,
        "live_command_dispatch_release_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_dispatch_release_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_creation_command_count": 0,
        "live_compile_command_count": 0,
        "live_marker_write_command_count": 0,
        "live_marker_readback_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_live_command_dispatch_release_count": summary.get(
            "durable_requested_canary_live_command_dispatch_release_count"
        ),
        "dispatch_release_contract_defined_count": summary.get(
            "dispatch_release_contract_defined_count"
        ),
        "start_contract_ready_count": summary.get("start_contract_ready_count"),
        "runner_plan_valid_count": summary.get("runner_plan_valid_count"),
        "start_record_valid_count": summary.get("start_record_valid_count"),
        "live_runner_started_count": summary.get("live_runner_started_count"),
        "dispatch_inputs_satisfied_count": summary.get("dispatch_inputs_satisfied_count"),
        "dispatch_record_present_count": summary.get("dispatch_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "dispatch_scope_matches_count": summary.get("dispatch_scope_matches_count"),
        "explicit_dispatch_authorized_count": summary.get("explicit_dispatch_authorized_count"),
        "no_save_delete_rename_acknowledged_count": summary.get("no_save_delete_rename_acknowledged_count"),
        "dispatch_release_record_valid_count": summary.get("dispatch_release_record_valid_count"),
        "dispatch_release_record_rejected_count": summary.get("dispatch_release_record_rejected_count"),
        "unsafe_dispatch_release_record_count": summary.get("unsafe_dispatch_release_record_count"),
        "missing_dispatch_prerequisite_count": summary.get("missing_dispatch_prerequisite_count"),
        "live_command_dispatch_release_allowed_count": summary.get(
            "live_command_dispatch_release_allowed_count"
        ),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_canary_rehearsal_performed_count": summary.get("live_canary_rehearsal_performed_count"),
        "canary_creation_allowed_count": summary.get("canary_creation_allowed_count"),
        "canary_save_allowed_count": summary.get("canary_save_allowed_count"),
        "canary_cleanup_allowed_count": summary.get("canary_cleanup_allowed_count"),
        "durable_executor_may_open_after_dispatch_release_count": summary.get(
            "durable_executor_may_open_after_dispatch_release_count"
        ),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_creation_command_count": summary.get("live_creation_command_count"),
        "live_compile_command_count": summary.get("live_compile_command_count"),
        "live_marker_write_command_count": summary.get("live_marker_write_command_count"),
        "live_marker_readback_command_count": summary.get("live_marker_readback_command_count"),
        "live_save_command_count": summary.get("live_save_command_count"),
        "live_delete_rename_command_count": summary.get("live_delete_rename_command_count"),
        "live_cleanup_command_count": summary.get("live_cleanup_command_count"),
    }
    return row(
        "durable_canary_live_command_dispatch_release_contract",
        "Section 78 durable canary live command dispatch release contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The command dispatch release contract is defined, but no dispatch release record is present.",
            "Command plan emission and live canary rehearsal remain behind a separate execution release.",
        ),
    )


def build_canary_live_command_execution_release_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    dispatch_release_row = build_canary_live_command_dispatch_release_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    dispatch_release_summary = dict(dispatch_release_row["actual"])
    dispatch_release_summary["status"] = dispatch_release_summary.pop("summary_status")
    contract = live_command_execution_release.build_canary_live_command_execution_release_contract(
        requested=True,
        dispatch_release_summary=dispatch_release_summary,
    )
    summary = live_command_execution_release.summarize_canary_live_command_execution_releases([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_live_command_execution_release_count": 1,
        "execution_release_contract_defined_count": 1,
        "dispatch_release_contract_ready_count": 1,
        "dispatch_inputs_satisfied_count": 0,
        "dispatch_release_record_valid_count": 0,
        "execution_inputs_satisfied_count": 0,
        "execution_record_present_count": 0,
        "record_schema_matches_count": 0,
        "execution_scope_matches_count": 0,
        "explicit_execution_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "execution_release_record_valid_count": 0,
        "execution_release_record_rejected_count": 0,
        "unsafe_execution_release_record_count": 0,
        "missing_execution_prerequisite_count": 8,
        "live_command_execution_release_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_execution_release_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_creation_command_count": 0,
        "live_compile_command_count": 0,
        "live_marker_write_command_count": 0,
        "live_marker_readback_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_live_command_execution_release_count": summary.get(
            "durable_requested_canary_live_command_execution_release_count"
        ),
        "execution_release_contract_defined_count": summary.get(
            "execution_release_contract_defined_count"
        ),
        "dispatch_release_contract_ready_count": summary.get("dispatch_release_contract_ready_count"),
        "dispatch_inputs_satisfied_count": summary.get("dispatch_inputs_satisfied_count"),
        "dispatch_release_record_valid_count": summary.get("dispatch_release_record_valid_count"),
        "execution_inputs_satisfied_count": summary.get("execution_inputs_satisfied_count"),
        "execution_record_present_count": summary.get("execution_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "execution_scope_matches_count": summary.get("execution_scope_matches_count"),
        "explicit_execution_authorized_count": summary.get("explicit_execution_authorized_count"),
        "no_save_delete_rename_acknowledged_count": summary.get("no_save_delete_rename_acknowledged_count"),
        "execution_release_record_valid_count": summary.get("execution_release_record_valid_count"),
        "execution_release_record_rejected_count": summary.get("execution_release_record_rejected_count"),
        "unsafe_execution_release_record_count": summary.get("unsafe_execution_release_record_count"),
        "missing_execution_prerequisite_count": summary.get("missing_execution_prerequisite_count"),
        "live_command_execution_release_allowed_count": summary.get(
            "live_command_execution_release_allowed_count"
        ),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
        "live_canary_rehearsal_performed_count": summary.get("live_canary_rehearsal_performed_count"),
        "canary_creation_allowed_count": summary.get("canary_creation_allowed_count"),
        "canary_save_allowed_count": summary.get("canary_save_allowed_count"),
        "canary_cleanup_allowed_count": summary.get("canary_cleanup_allowed_count"),
        "durable_executor_may_open_after_execution_release_count": summary.get(
            "durable_executor_may_open_after_execution_release_count"
        ),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_creation_command_count": summary.get("live_creation_command_count"),
        "live_compile_command_count": summary.get("live_compile_command_count"),
        "live_marker_write_command_count": summary.get("live_marker_write_command_count"),
        "live_marker_readback_command_count": summary.get("live_marker_readback_command_count"),
        "live_save_command_count": summary.get("live_save_command_count"),
        "live_delete_rename_command_count": summary.get("live_delete_rename_command_count"),
        "live_cleanup_command_count": summary.get("live_cleanup_command_count"),
    }
    return row(
        "durable_canary_live_command_execution_release_contract",
        "Section 79 durable canary live command execution release contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The command execution release contract is defined, but no execution release record is present.",
            "No command plan is emitted and no live command is executed by this contract.",
        ),
    )


def build_canary_live_command_execution_evidence_admission_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    execution_release_row = build_canary_live_command_execution_release_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    execution_release_summary = dict(execution_release_row["actual"])
    execution_release_summary["status"] = execution_release_summary.pop("summary_status")
    contract = execution_evidence_admission.build_canary_live_command_execution_evidence_admission_contract(
        requested=True,
        execution_release_summary=execution_release_summary,
    )
    summary = execution_evidence_admission.summarize_canary_live_command_execution_evidence_admissions(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_live_command_execution_evidence_admission_count": 1,
        "evidence_admission_contract_defined_count": 1,
        "execution_release_contract_ready_count": 1,
        "execution_inputs_satisfied_count": 0,
        "execution_release_record_valid_count": 0,
        "section_79_live_command_executed_count": 0,
        "evidence_inputs_satisfied_count": 0,
        "evidence_record_present_count": 0,
        "record_schema_matches_count": 0,
        "evidence_scope_matches_count": 0,
        "explicit_evidence_admission_authorized_count": 0,
        "evidence_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "allowed_evidence_command_observed_count": 0,
        "no_forbidden_evidence_commands_count": 0,
        "execution_evidence_admitted_count": 0,
        "evidence_record_rejected_count": 0,
        "unsafe_evidence_record_count": 0,
        "missing_evidence_prerequisite_count": 12,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
        "durable_promotion_allowed_count": 0,
        "durable_executor_may_open_after_evidence_admission_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "reported_live_creation_command_count": 0,
        "reported_live_compile_command_count": 0,
        "reported_live_marker_write_command_count": 0,
        "reported_live_marker_readback_command_count": 0,
        "reported_live_save_command_count": 0,
        "reported_live_delete_rename_command_count": 0,
        "reported_live_cleanup_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_live_command_execution_evidence_admission_count": summary.get(
            "durable_requested_canary_live_command_execution_evidence_admission_count"
        ),
        "evidence_admission_contract_defined_count": summary.get(
            "evidence_admission_contract_defined_count"
        ),
        "execution_release_contract_ready_count": summary.get("execution_release_contract_ready_count"),
        "execution_inputs_satisfied_count": summary.get("execution_inputs_satisfied_count"),
        "execution_release_record_valid_count": summary.get("execution_release_record_valid_count"),
        "section_79_live_command_executed_count": summary.get("section_79_live_command_executed_count"),
        "evidence_inputs_satisfied_count": summary.get("evidence_inputs_satisfied_count"),
        "evidence_record_present_count": summary.get("evidence_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "evidence_scope_matches_count": summary.get("evidence_scope_matches_count"),
        "explicit_evidence_admission_authorized_count": summary.get(
            "explicit_evidence_admission_authorized_count"
        ),
        "evidence_status_passed_count": summary.get("evidence_status_passed_count"),
        "no_save_delete_rename_acknowledged_count": summary.get("no_save_delete_rename_acknowledged_count"),
        "allowed_evidence_command_observed_count": summary.get("allowed_evidence_command_observed_count"),
        "no_forbidden_evidence_commands_count": summary.get("no_forbidden_evidence_commands_count"),
        "execution_evidence_admitted_count": summary.get("execution_evidence_admitted_count"),
        "evidence_record_rejected_count": summary.get("evidence_record_rejected_count"),
        "unsafe_evidence_record_count": summary.get("unsafe_evidence_record_count"),
        "missing_evidence_prerequisite_count": summary.get("missing_evidence_prerequisite_count"),
        "reported_allowed_evidence_command_count": summary.get("reported_allowed_evidence_command_count"),
        "reported_forbidden_evidence_command_count": summary.get("reported_forbidden_evidence_command_count"),
        "durable_promotion_allowed_count": summary.get("durable_promotion_allowed_count"),
        "durable_executor_may_open_after_evidence_admission_count": summary.get(
            "durable_executor_may_open_after_evidence_admission_count"
        ),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
        "reported_live_creation_command_count": summary.get("reported_live_creation_command_count"),
        "reported_live_compile_command_count": summary.get("reported_live_compile_command_count"),
        "reported_live_marker_write_command_count": summary.get("reported_live_marker_write_command_count"),
        "reported_live_marker_readback_command_count": summary.get(
            "reported_live_marker_readback_command_count"
        ),
        "reported_live_save_command_count": summary.get("reported_live_save_command_count"),
        "reported_live_delete_rename_command_count": summary.get(
            "reported_live_delete_rename_command_count"
        ),
        "reported_live_cleanup_command_count": summary.get("reported_live_cleanup_command_count"),
    }
    return row(
        "durable_canary_live_command_execution_evidence_admission_contract",
        "Section 80 durable canary live command execution evidence admission contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The execution evidence admission contract is defined, but no evidence record is present.",
            "Admitted evidence still cannot promote durable authoring without a separate release decision.",
        ),
    )


def build_canary_release_promotion_decision_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    evidence_admission_row = build_canary_live_command_execution_evidence_admission_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    evidence_admission_summary = dict(evidence_admission_row["actual"])
    evidence_admission_summary["status"] = evidence_admission_summary.pop("summary_status")
    contract = promotion_decision.build_canary_durable_release_promotion_decision_contract(
        requested=True,
        evidence_admission_summary=evidence_admission_summary,
    )
    summary = promotion_decision.summarize_canary_durable_release_promotion_decisions([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_release_promotion_decision_count": 1,
        "promotion_decision_contract_defined_count": 1,
        "evidence_admission_contract_ready_count": 1,
        "execution_evidence_admitted_count": 0,
        "allowed_evidence_command_observed_count": 0,
        "no_forbidden_evidence_commands_count": 0,
        "evidence_ready_for_promotion_count": 0,
        "decision_record_present_count": 0,
        "record_schema_matches_count": 0,
        "promotion_scope_matches_count": 0,
        "explicit_promotion_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "promotion_decision_record_valid_count": 0,
        "promotion_decision_record_rejected_count": 0,
        "unsafe_promotion_decision_record_count": 0,
        "missing_promotion_prerequisite_count": 9,
        "durable_release_promotion_allowed_count": 0,
        "durable_release_promoted_count": 0,
        "durable_executor_may_open_after_promotion_decision_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_release_promotion_decision_count": summary.get(
            "durable_requested_canary_release_promotion_decision_count"
        ),
        "promotion_decision_contract_defined_count": summary.get("promotion_decision_contract_defined_count"),
        "evidence_admission_contract_ready_count": summary.get("evidence_admission_contract_ready_count"),
        "execution_evidence_admitted_count": summary.get("execution_evidence_admitted_count"),
        "allowed_evidence_command_observed_count": summary.get("allowed_evidence_command_observed_count"),
        "no_forbidden_evidence_commands_count": summary.get("no_forbidden_evidence_commands_count"),
        "evidence_ready_for_promotion_count": summary.get("evidence_ready_for_promotion_count"),
        "decision_record_present_count": summary.get("decision_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "promotion_scope_matches_count": summary.get("promotion_scope_matches_count"),
        "explicit_promotion_authorized_count": summary.get("explicit_promotion_authorized_count"),
        "no_save_delete_rename_acknowledged_count": summary.get("no_save_delete_rename_acknowledged_count"),
        "promotion_decision_record_valid_count": summary.get("promotion_decision_record_valid_count"),
        "promotion_decision_record_rejected_count": summary.get("promotion_decision_record_rejected_count"),
        "unsafe_promotion_decision_record_count": summary.get("unsafe_promotion_decision_record_count"),
        "missing_promotion_prerequisite_count": summary.get("missing_promotion_prerequisite_count"),
        "durable_release_promotion_allowed_count": summary.get("durable_release_promotion_allowed_count"),
        "durable_release_promoted_count": summary.get("durable_release_promoted_count"),
        "durable_executor_may_open_after_promotion_decision_count": summary.get(
            "durable_executor_may_open_after_promotion_decision_count"
        ),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
        "reported_allowed_evidence_command_count": summary.get("reported_allowed_evidence_command_count"),
        "reported_forbidden_evidence_command_count": summary.get("reported_forbidden_evidence_command_count"),
    }
    return row(
        "durable_canary_release_promotion_decision_contract",
        "Section 81 durable canary release promotion decision contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The release promotion decision contract is defined, but no promotion decision record is present.",
            "Durable executor activation remains behind a separate contract.",
        ),
    )


def build_canary_executor_activation_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    promotion_decision_row = build_canary_release_promotion_decision_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    promotion_decision_summary = dict(promotion_decision_row["actual"])
    promotion_decision_summary["status"] = promotion_decision_summary.pop("summary_status")
    contract = executor_activation.build_canary_durable_executor_activation_contract(
        requested=True,
        promotion_decision_summary=promotion_decision_summary,
    )
    summary = executor_activation.summarize_canary_durable_executor_activations([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_executor_activation_count": 1,
        "activation_contract_defined_count": 1,
        "promotion_decision_contract_ready_count": 1,
        "evidence_ready_for_promotion_count": 0,
        "promotion_decision_record_valid_count": 0,
        "activation_inputs_satisfied_count": 0,
        "activation_record_present_count": 0,
        "record_schema_matches_count": 0,
        "activation_scope_matches_count": 0,
        "explicit_activation_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "activation_record_valid_count": 0,
        "activation_record_rejected_count": 0,
        "unsafe_activation_record_count": 0,
        "missing_activation_prerequisite_count": 8,
        "durable_executor_activation_allowed_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_may_open_after_activation_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_executor_activation_count": summary.get(
            "durable_requested_canary_executor_activation_count"
        ),
        "activation_contract_defined_count": summary.get("activation_contract_defined_count"),
        "promotion_decision_contract_ready_count": summary.get("promotion_decision_contract_ready_count"),
        "evidence_ready_for_promotion_count": summary.get("evidence_ready_for_promotion_count"),
        "promotion_decision_record_valid_count": summary.get("promotion_decision_record_valid_count"),
        "activation_inputs_satisfied_count": summary.get("activation_inputs_satisfied_count"),
        "activation_record_present_count": summary.get("activation_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "activation_scope_matches_count": summary.get("activation_scope_matches_count"),
        "explicit_activation_authorized_count": summary.get("explicit_activation_authorized_count"),
        "no_save_delete_rename_acknowledged_count": summary.get("no_save_delete_rename_acknowledged_count"),
        "activation_record_valid_count": summary.get("activation_record_valid_count"),
        "activation_record_rejected_count": summary.get("activation_record_rejected_count"),
        "unsafe_activation_record_count": summary.get("unsafe_activation_record_count"),
        "missing_activation_prerequisite_count": summary.get("missing_activation_prerequisite_count"),
        "durable_executor_activation_allowed_count": summary.get("durable_executor_activation_allowed_count"),
        "durable_executor_activated_count": summary.get("durable_executor_activated_count"),
        "durable_executor_may_open_after_activation_count": summary.get(
            "durable_executor_may_open_after_activation_count"
        ),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
        "reported_allowed_evidence_command_count": summary.get("reported_allowed_evidence_command_count"),
        "reported_forbidden_evidence_command_count": summary.get("reported_forbidden_evidence_command_count"),
    }
    return row(
        "durable_canary_executor_activation_contract",
        "Section 82 durable canary executor activation contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The executor activation contract is defined, but no activation record is present.",
            "Durable executor open remains behind a separate contract.",
        ),
    )


def build_canary_executor_open_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    activation_row = build_canary_executor_activation_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    activation_summary = dict(activation_row["actual"])
    activation_summary["status"] = activation_summary.pop("summary_status")
    contract = executor_open.build_canary_durable_executor_open_contract(
        requested=True,
        activation_summary=activation_summary,
    )
    summary = executor_open.summarize_canary_durable_executor_opens([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_executor_open_count": 1,
        "open_contract_defined_count": 1,
        "activation_contract_ready_count": 1,
        "activation_inputs_satisfied_count": 0,
        "activation_record_valid_count": 0,
        "open_inputs_satisfied_count": 0,
        "open_record_present_count": 0,
        "record_schema_matches_count": 0,
        "open_scope_matches_count": 0,
        "explicit_open_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "open_record_valid_count": 0,
        "open_record_rejected_count": 0,
        "unsafe_open_record_count": 0,
        "missing_open_prerequisite_count": 8,
        "durable_executor_open_allowed_count": 0,
        "durable_executor_opened_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_executor_open_count": summary.get(
            "durable_requested_canary_executor_open_count"
        ),
        "open_contract_defined_count": summary.get("open_contract_defined_count"),
        "activation_contract_ready_count": summary.get("activation_contract_ready_count"),
        "activation_inputs_satisfied_count": summary.get("activation_inputs_satisfied_count"),
        "activation_record_valid_count": summary.get("activation_record_valid_count"),
        "open_inputs_satisfied_count": summary.get("open_inputs_satisfied_count"),
        "open_record_present_count": summary.get("open_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "open_scope_matches_count": summary.get("open_scope_matches_count"),
        "explicit_open_authorized_count": summary.get("explicit_open_authorized_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "open_record_valid_count": summary.get("open_record_valid_count"),
        "open_record_rejected_count": summary.get("open_record_rejected_count"),
        "unsafe_open_record_count": summary.get("unsafe_open_record_count"),
        "missing_open_prerequisite_count": summary.get("missing_open_prerequisite_count"),
        "durable_executor_open_allowed_count": summary.get("durable_executor_open_allowed_count"),
        "durable_executor_opened_count": summary.get("durable_executor_opened_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
        "reported_allowed_evidence_command_count": summary.get("reported_allowed_evidence_command_count"),
        "reported_forbidden_evidence_command_count": summary.get("reported_forbidden_evidence_command_count"),
    }
    return row(
        "durable_canary_executor_open_contract",
        "Section 83 durable canary executor open contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The executor open contract is defined, but no open record is present.",
            "Durable authoring enablement remains behind a separate contract.",
        ),
    )


def build_canary_authoring_enable_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    open_row = build_canary_executor_open_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    open_summary = dict(open_row["actual"])
    open_summary["status"] = open_summary.pop("summary_status")
    contract = authoring_enable.build_canary_durable_authoring_enable_contract(
        requested=True,
        open_summary=open_summary,
    )
    summary = authoring_enable.summarize_canary_durable_authoring_enables([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_authoring_enable_count": 1,
        "authoring_enable_contract_defined_count": 1,
        "executor_open_contract_ready_count": 1,
        "open_inputs_satisfied_count": 0,
        "open_record_valid_count": 0,
        "authoring_enable_inputs_satisfied_count": 0,
        "authoring_enable_record_present_count": 0,
        "record_schema_matches_count": 0,
        "enable_scope_matches_count": 0,
        "explicit_authoring_enable_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "target_package_allowlist_reconfirmed_count": 0,
        "overwrite_rename_decision_reconfirmed_count": 0,
        "rollback_readiness_reconfirmed_count": 0,
        "ownership_marker_reconfirmed_count": 0,
        "authoring_enable_record_valid_count": 0,
        "authoring_enable_record_rejected_count": 0,
        "unsafe_authoring_enable_record_count": 0,
        "missing_authoring_enable_prerequisite_count": 12,
        "durable_authoring_enable_allowed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_authoring_enable_count": summary.get(
            "durable_requested_canary_authoring_enable_count"
        ),
        "authoring_enable_contract_defined_count": summary.get(
            "authoring_enable_contract_defined_count"
        ),
        "executor_open_contract_ready_count": summary.get("executor_open_contract_ready_count"),
        "open_inputs_satisfied_count": summary.get("open_inputs_satisfied_count"),
        "open_record_valid_count": summary.get("open_record_valid_count"),
        "authoring_enable_inputs_satisfied_count": summary.get(
            "authoring_enable_inputs_satisfied_count"
        ),
        "authoring_enable_record_present_count": summary.get("authoring_enable_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "enable_scope_matches_count": summary.get("enable_scope_matches_count"),
        "explicit_authoring_enable_authorized_count": summary.get(
            "explicit_authoring_enable_authorized_count"
        ),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "target_package_allowlist_reconfirmed_count": summary.get(
            "target_package_allowlist_reconfirmed_count"
        ),
        "overwrite_rename_decision_reconfirmed_count": summary.get(
            "overwrite_rename_decision_reconfirmed_count"
        ),
        "rollback_readiness_reconfirmed_count": summary.get("rollback_readiness_reconfirmed_count"),
        "ownership_marker_reconfirmed_count": summary.get("ownership_marker_reconfirmed_count"),
        "authoring_enable_record_valid_count": summary.get("authoring_enable_record_valid_count"),
        "authoring_enable_record_rejected_count": summary.get("authoring_enable_record_rejected_count"),
        "unsafe_authoring_enable_record_count": summary.get("unsafe_authoring_enable_record_count"),
        "missing_authoring_enable_prerequisite_count": summary.get(
            "missing_authoring_enable_prerequisite_count"
        ),
        "durable_authoring_enable_allowed_count": summary.get("durable_authoring_enable_allowed_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
        "reported_allowed_evidence_command_count": summary.get("reported_allowed_evidence_command_count"),
        "reported_forbidden_evidence_command_count": summary.get("reported_forbidden_evidence_command_count"),
    }
    return row(
        "durable_canary_authoring_enable_contract",
        "Section 84 durable canary authoring enable contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The authoring enable contract is defined, but no enable record is present.",
            "Durable authoring commands remain behind a separate contract.",
        ),
    )


def build_canary_authoring_command_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    enable_row = build_canary_authoring_enable_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    enable_summary = dict(enable_row["actual"])
    enable_summary["status"] = enable_summary.pop("summary_status")
    contract = authoring_command.build_canary_durable_authoring_command_contract(
        requested=True,
        authoring_enable_summary=enable_summary,
    )
    summary = authoring_command.summarize_canary_durable_authoring_commands([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_authoring_command_count": 1,
        "authoring_command_contract_defined_count": 1,
        "authoring_enable_contract_ready_count": 1,
        "authoring_enable_inputs_satisfied_count": 0,
        "authoring_enable_record_valid_count": 0,
        "target_package_allowlist_reconfirmed_count": 0,
        "overwrite_rename_decision_reconfirmed_count": 0,
        "rollback_readiness_reconfirmed_count": 0,
        "ownership_marker_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_present_count": 0,
        "record_schema_matches_count": 0,
        "command_scope_matches_count": 0,
        "explicit_authoring_command_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "planned_authoring_command_count": 0,
        "allowed_authoring_command_count": 0,
        "forbidden_authoring_command_count": 0,
        "unknown_authoring_command_count": 0,
        "authoring_command_record_valid_count": 0,
        "authoring_command_record_rejected_count": 0,
        "unsafe_authoring_command_record_count": 0,
        "missing_authoring_command_prerequisite_count": 13,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_authoring_command_count": summary.get(
            "durable_requested_canary_authoring_command_count"
        ),
        "authoring_command_contract_defined_count": summary.get(
            "authoring_command_contract_defined_count"
        ),
        "authoring_enable_contract_ready_count": summary.get("authoring_enable_contract_ready_count"),
        "authoring_enable_inputs_satisfied_count": summary.get(
            "authoring_enable_inputs_satisfied_count"
        ),
        "authoring_enable_record_valid_count": summary.get("authoring_enable_record_valid_count"),
        "target_package_allowlist_reconfirmed_count": summary.get(
            "target_package_allowlist_reconfirmed_count"
        ),
        "overwrite_rename_decision_reconfirmed_count": summary.get(
            "overwrite_rename_decision_reconfirmed_count"
        ),
        "rollback_readiness_reconfirmed_count": summary.get("rollback_readiness_reconfirmed_count"),
        "ownership_marker_reconfirmed_count": summary.get("ownership_marker_reconfirmed_count"),
        "authoring_command_inputs_satisfied_count": summary.get(
            "authoring_command_inputs_satisfied_count"
        ),
        "authoring_command_record_present_count": summary.get("authoring_command_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "command_scope_matches_count": summary.get("command_scope_matches_count"),
        "explicit_authoring_command_authorized_count": summary.get(
            "explicit_authoring_command_authorized_count"
        ),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "planned_authoring_command_count": summary.get("planned_authoring_command_count"),
        "allowed_authoring_command_count": summary.get("allowed_authoring_command_count"),
        "forbidden_authoring_command_count": summary.get("forbidden_authoring_command_count"),
        "unknown_authoring_command_count": summary.get("unknown_authoring_command_count"),
        "authoring_command_record_valid_count": summary.get("authoring_command_record_valid_count"),
        "authoring_command_record_rejected_count": summary.get("authoring_command_record_rejected_count"),
        "unsafe_authoring_command_record_count": summary.get("unsafe_authoring_command_record_count"),
        "missing_authoring_command_prerequisite_count": summary.get(
            "missing_authoring_command_prerequisite_count"
        ),
        "durable_authoring_command_allowed_count": summary.get("durable_authoring_command_allowed_count"),
        "durable_authoring_command_dispatched_count": summary.get(
            "durable_authoring_command_dispatched_count"
        ),
        "durable_authoring_command_executed_count": summary.get(
            "durable_authoring_command_executed_count"
        ),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
        "reported_allowed_evidence_command_count": summary.get("reported_allowed_evidence_command_count"),
        "reported_forbidden_evidence_command_count": summary.get("reported_forbidden_evidence_command_count"),
    }
    return row(
        "durable_canary_authoring_command_contract",
        "Section 85 durable canary authoring command contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The authoring command contract is defined, but no command record is present.",
            "Durable command dispatch and execution remain behind separate contracts.",
        ),
    )


def build_canary_authoring_command_dispatch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    command_row = build_canary_authoring_command_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    command_summary = dict(command_row["actual"])
    command_summary["status"] = command_summary.pop("summary_status")
    contract = authoring_command_dispatch.build_canary_durable_authoring_command_dispatch_contract(
        requested=True,
        authoring_command_summary=command_summary,
    )
    summary = authoring_command_dispatch.summarize_canary_durable_authoring_command_dispatches([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_authoring_command_dispatch_count": 1,
        "dispatch_contract_defined_count": 1,
        "authoring_command_contract_ready_count": 1,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "planned_authoring_commands_present_count": 0,
        "allowed_authoring_commands_present_count": 0,
        "dispatch_inputs_satisfied_count": 0,
        "dispatch_record_present_count": 0,
        "record_schema_matches_count": 0,
        "dispatch_scope_matches_count": 0,
        "explicit_dispatch_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "dispatch_record_valid_count": 0,
        "dispatch_record_rejected_count": 0,
        "unsafe_dispatch_record_count": 0,
        "missing_dispatch_prerequisite_count": 10,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_authoring_command_dispatch_count": summary.get(
            "durable_requested_canary_authoring_command_dispatch_count"
        ),
        "dispatch_contract_defined_count": summary.get("dispatch_contract_defined_count"),
        "authoring_command_contract_ready_count": summary.get("authoring_command_contract_ready_count"),
        "authoring_command_inputs_satisfied_count": summary.get(
            "authoring_command_inputs_satisfied_count"
        ),
        "authoring_command_record_valid_count": summary.get("authoring_command_record_valid_count"),
        "planned_authoring_commands_present_count": summary.get(
            "planned_authoring_commands_present_count"
        ),
        "allowed_authoring_commands_present_count": summary.get(
            "allowed_authoring_commands_present_count"
        ),
        "dispatch_inputs_satisfied_count": summary.get("dispatch_inputs_satisfied_count"),
        "dispatch_record_present_count": summary.get("dispatch_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "dispatch_scope_matches_count": summary.get("dispatch_scope_matches_count"),
        "explicit_dispatch_authorized_count": summary.get("explicit_dispatch_authorized_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "dispatch_record_valid_count": summary.get("dispatch_record_valid_count"),
        "dispatch_record_rejected_count": summary.get("dispatch_record_rejected_count"),
        "unsafe_dispatch_record_count": summary.get("unsafe_dispatch_record_count"),
        "missing_dispatch_prerequisite_count": summary.get("missing_dispatch_prerequisite_count"),
        "durable_authoring_command_dispatch_allowed_count": summary.get(
            "durable_authoring_command_dispatch_allowed_count"
        ),
        "durable_authoring_command_dispatched_count": summary.get(
            "durable_authoring_command_dispatched_count"
        ),
        "durable_authoring_command_execution_allowed_count": summary.get(
            "durable_authoring_command_execution_allowed_count"
        ),
        "durable_authoring_command_executed_count": summary.get(
            "durable_authoring_command_executed_count"
        ),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
        "reported_allowed_evidence_command_count": summary.get("reported_allowed_evidence_command_count"),
        "reported_forbidden_evidence_command_count": summary.get("reported_forbidden_evidence_command_count"),
    }
    return row(
        "durable_canary_authoring_command_dispatch_contract",
        "Section 86 durable canary authoring command dispatch contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The authoring command dispatch contract is defined, but no dispatch record is present.",
            "Durable command execution remains behind a separate contract.",
        ),
    )


def build_canary_authoring_command_execution_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    dispatch_row = build_canary_authoring_command_dispatch_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    dispatch_summary = dict(dispatch_row["actual"])
    dispatch_summary["status"] = dispatch_summary.pop("summary_status")
    contract = authoring_command_execution.build_canary_durable_authoring_command_execution_contract(
        requested=True,
        dispatch_summary=dispatch_summary,
    )
    summary = authoring_command_execution.summarize_canary_durable_authoring_command_executions([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_authoring_command_execution_count": 1,
        "execution_contract_defined_count": 1,
        "dispatch_contract_ready_count": 1,
        "dispatch_inputs_satisfied_count": 0,
        "dispatch_record_valid_count": 0,
        "planned_authoring_commands_present_count": 0,
        "allowed_authoring_commands_present_count": 0,
        "execution_inputs_satisfied_count": 0,
        "execution_record_present_count": 0,
        "record_schema_matches_count": 0,
        "execution_scope_matches_count": 0,
        "explicit_execution_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "execution_record_valid_count": 0,
        "execution_record_rejected_count": 0,
        "unsafe_execution_record_count": 0,
        "missing_execution_prerequisite_count": 10,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_authoring_command_execution_count": summary.get(
            "durable_requested_canary_authoring_command_execution_count"
        ),
        "execution_contract_defined_count": summary.get("execution_contract_defined_count"),
        "dispatch_contract_ready_count": summary.get("dispatch_contract_ready_count"),
        "dispatch_inputs_satisfied_count": summary.get("dispatch_inputs_satisfied_count"),
        "dispatch_record_valid_count": summary.get("dispatch_record_valid_count"),
        "planned_authoring_commands_present_count": summary.get(
            "planned_authoring_commands_present_count"
        ),
        "allowed_authoring_commands_present_count": summary.get(
            "allowed_authoring_commands_present_count"
        ),
        "execution_inputs_satisfied_count": summary.get("execution_inputs_satisfied_count"),
        "execution_record_present_count": summary.get("execution_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "execution_scope_matches_count": summary.get("execution_scope_matches_count"),
        "explicit_execution_authorized_count": summary.get("explicit_execution_authorized_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "execution_record_valid_count": summary.get("execution_record_valid_count"),
        "execution_record_rejected_count": summary.get("execution_record_rejected_count"),
        "unsafe_execution_record_count": summary.get("unsafe_execution_record_count"),
        "missing_execution_prerequisite_count": summary.get("missing_execution_prerequisite_count"),
        "durable_authoring_command_dispatch_allowed_count": summary.get(
            "durable_authoring_command_dispatch_allowed_count"
        ),
        "durable_authoring_command_dispatched_count": summary.get(
            "durable_authoring_command_dispatched_count"
        ),
        "durable_authoring_command_execution_allowed_count": summary.get(
            "durable_authoring_command_execution_allowed_count"
        ),
        "durable_authoring_command_executed_count": summary.get(
            "durable_authoring_command_executed_count"
        ),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
        "reported_allowed_evidence_command_count": summary.get("reported_allowed_evidence_command_count"),
        "reported_forbidden_evidence_command_count": summary.get("reported_forbidden_evidence_command_count"),
    }
    return row(
        "durable_canary_authoring_command_execution_contract",
        "Section 87 durable canary authoring command execution contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The authoring command execution contract is defined, but no execution record is present.",
            "Durable execution evidence admission remains behind a separate contract.",
        ),
    )


def build_canary_authoring_command_execution_evidence_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    execution_row = build_canary_authoring_command_execution_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    execution_summary = dict(execution_row["actual"])
    execution_summary["status"] = execution_summary.pop("summary_status")
    contract = (
        authoring_command_execution_evidence.build_canary_durable_authoring_command_execution_evidence_contract(
            requested=True,
            execution_summary=execution_summary,
        )
    )
    summary = (
        authoring_command_execution_evidence.summarize_canary_durable_authoring_command_execution_evidence(
            [contract]
        )
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_authoring_command_execution_evidence_count": 1,
        "evidence_contract_defined_count": 1,
        "execution_contract_ready_count": 1,
        "execution_inputs_satisfied_count": 0,
        "execution_record_valid_count": 0,
        "planned_authoring_commands_present_count": 0,
        "allowed_authoring_commands_present_count": 0,
        "evidence_inputs_satisfied_count": 0,
        "evidence_record_present_count": 0,
        "record_schema_matches_count": 0,
        "evidence_scope_matches_count": 0,
        "explicit_evidence_authorized_count": 0,
        "evidence_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "allowed_evidence_command_observed_count": 0,
        "no_forbidden_evidence_commands_count": 0,
        "authoring_command_execution_evidence_admitted_count": 0,
        "evidence_record_rejected_count": 0,
        "unsafe_evidence_record_count": 0,
        "missing_evidence_prerequisite_count": 13,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_promotion_allowed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "reported_authoring_create_command_count": 0,
        "reported_authoring_compile_command_count": 0,
        "reported_authoring_marker_write_command_count": 0,
        "reported_authoring_marker_readback_command_count": 0,
        "reported_authoring_read_only_exists_check_command_count": 0,
        "reported_authoring_save_command_count": 0,
        "reported_authoring_delete_rename_command_count": 0,
        "reported_authoring_cleanup_command_count": 0,
        "reported_authoring_duplicate_replace_command_count": 0,
        "reported_authoring_live_dispatch_execution_command_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_authoring_command_execution_evidence_count": summary.get(
            "durable_requested_canary_authoring_command_execution_evidence_count"
        ),
        "evidence_contract_defined_count": summary.get("evidence_contract_defined_count"),
        "execution_contract_ready_count": summary.get("execution_contract_ready_count"),
        "execution_inputs_satisfied_count": summary.get("execution_inputs_satisfied_count"),
        "execution_record_valid_count": summary.get("execution_record_valid_count"),
        "planned_authoring_commands_present_count": summary.get(
            "planned_authoring_commands_present_count"
        ),
        "allowed_authoring_commands_present_count": summary.get(
            "allowed_authoring_commands_present_count"
        ),
        "evidence_inputs_satisfied_count": summary.get("evidence_inputs_satisfied_count"),
        "evidence_record_present_count": summary.get("evidence_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "evidence_scope_matches_count": summary.get("evidence_scope_matches_count"),
        "explicit_evidence_authorized_count": summary.get("explicit_evidence_authorized_count"),
        "evidence_status_passed_count": summary.get("evidence_status_passed_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "allowed_evidence_command_observed_count": summary.get(
            "allowed_evidence_command_observed_count"
        ),
        "no_forbidden_evidence_commands_count": summary.get(
            "no_forbidden_evidence_commands_count"
        ),
        "authoring_command_execution_evidence_admitted_count": summary.get(
            "authoring_command_execution_evidence_admitted_count"
        ),
        "evidence_record_rejected_count": summary.get("evidence_record_rejected_count"),
        "unsafe_evidence_record_count": summary.get("unsafe_evidence_record_count"),
        "missing_evidence_prerequisite_count": summary.get("missing_evidence_prerequisite_count"),
        "reported_allowed_evidence_command_count": summary.get("reported_allowed_evidence_command_count"),
        "reported_forbidden_evidence_command_count": summary.get("reported_forbidden_evidence_command_count"),
        "durable_authoring_command_dispatch_allowed_count": summary.get(
            "durable_authoring_command_dispatch_allowed_count"
        ),
        "durable_authoring_command_dispatched_count": summary.get(
            "durable_authoring_command_dispatched_count"
        ),
        "durable_authoring_command_execution_allowed_count": summary.get(
            "durable_authoring_command_execution_allowed_count"
        ),
        "durable_authoring_command_executed_count": summary.get(
            "durable_authoring_command_executed_count"
        ),
        "durable_promotion_allowed_count": summary.get("durable_promotion_allowed_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
        "reported_authoring_create_command_count": summary.get(
            "reported_authoring_create_command_count"
        ),
        "reported_authoring_compile_command_count": summary.get(
            "reported_authoring_compile_command_count"
        ),
        "reported_authoring_marker_write_command_count": summary.get(
            "reported_authoring_marker_write_command_count"
        ),
        "reported_authoring_marker_readback_command_count": summary.get(
            "reported_authoring_marker_readback_command_count"
        ),
        "reported_authoring_read_only_exists_check_command_count": summary.get(
            "reported_authoring_read_only_exists_check_command_count"
        ),
        "reported_authoring_save_command_count": summary.get(
            "reported_authoring_save_command_count"
        ),
        "reported_authoring_delete_rename_command_count": summary.get(
            "reported_authoring_delete_rename_command_count"
        ),
        "reported_authoring_cleanup_command_count": summary.get(
            "reported_authoring_cleanup_command_count"
        ),
        "reported_authoring_duplicate_replace_command_count": summary.get(
            "reported_authoring_duplicate_replace_command_count"
        ),
        "reported_authoring_live_dispatch_execution_command_count": summary.get(
            "reported_authoring_live_dispatch_execution_command_count"
        ),
    }
    return row(
        "durable_canary_authoring_command_execution_evidence_contract",
        "Section 88 durable canary authoring command execution evidence contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The authoring command execution evidence contract is defined, but no evidence record is present.",
            "Admitted execution evidence still cannot complete durable authoring without a separate decision.",
        ),
    )


def build_canary_authoring_command_completion_decision_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    evidence_row = build_canary_authoring_command_execution_evidence_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    evidence_summary = dict(evidence_row["actual"])
    evidence_summary["status"] = evidence_summary.pop("summary_status")
    contract = authoring_completion_decision.build_canary_durable_authoring_command_completion_decision_contract(
        requested=True,
        evidence_summary=evidence_summary,
    )
    summary = authoring_completion_decision.summarize_canary_durable_authoring_command_completion_decisions(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_authoring_command_completion_decision_count": 1,
        "completion_decision_contract_defined_count": 1,
        "evidence_contract_ready_count": 1,
        "authoring_command_execution_evidence_admitted_count": 0,
        "allowed_evidence_command_observed_count": 0,
        "no_forbidden_evidence_commands_count": 0,
        "evidence_ready_for_completion_count": 0,
        "decision_record_present_count": 0,
        "record_schema_matches_count": 0,
        "completion_scope_matches_count": 0,
        "explicit_completion_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "completion_decision_record_valid_count": 0,
        "completion_decision_record_rejected_count": 0,
        "unsafe_completion_decision_record_count": 0,
        "missing_completion_prerequisite_count": 9,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
        "durable_authoring_command_completion_allowed_count": 0,
        "durable_authoring_command_completed_count": 0,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_promotion_allowed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_authoring_command_completion_decision_count": summary.get(
            "durable_requested_canary_authoring_command_completion_decision_count"
        ),
        "completion_decision_contract_defined_count": summary.get(
            "completion_decision_contract_defined_count"
        ),
        "evidence_contract_ready_count": summary.get("evidence_contract_ready_count"),
        "authoring_command_execution_evidence_admitted_count": summary.get(
            "authoring_command_execution_evidence_admitted_count"
        ),
        "allowed_evidence_command_observed_count": summary.get(
            "allowed_evidence_command_observed_count"
        ),
        "no_forbidden_evidence_commands_count": summary.get("no_forbidden_evidence_commands_count"),
        "evidence_ready_for_completion_count": summary.get("evidence_ready_for_completion_count"),
        "decision_record_present_count": summary.get("decision_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "completion_scope_matches_count": summary.get("completion_scope_matches_count"),
        "explicit_completion_authorized_count": summary.get("explicit_completion_authorized_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "completion_decision_record_valid_count": summary.get(
            "completion_decision_record_valid_count"
        ),
        "completion_decision_record_rejected_count": summary.get(
            "completion_decision_record_rejected_count"
        ),
        "unsafe_completion_decision_record_count": summary.get(
            "unsafe_completion_decision_record_count"
        ),
        "missing_completion_prerequisite_count": summary.get(
            "missing_completion_prerequisite_count"
        ),
        "reported_allowed_evidence_command_count": summary.get("reported_allowed_evidence_command_count"),
        "reported_forbidden_evidence_command_count": summary.get("reported_forbidden_evidence_command_count"),
        "durable_authoring_command_completion_allowed_count": summary.get(
            "durable_authoring_command_completion_allowed_count"
        ),
        "durable_authoring_command_completed_count": summary.get(
            "durable_authoring_command_completed_count"
        ),
        "durable_authoring_command_dispatch_allowed_count": summary.get(
            "durable_authoring_command_dispatch_allowed_count"
        ),
        "durable_authoring_command_dispatched_count": summary.get(
            "durable_authoring_command_dispatched_count"
        ),
        "durable_authoring_command_execution_allowed_count": summary.get(
            "durable_authoring_command_execution_allowed_count"
        ),
        "durable_authoring_command_executed_count": summary.get(
            "durable_authoring_command_executed_count"
        ),
        "durable_promotion_allowed_count": summary.get("durable_promotion_allowed_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
    }
    return row(
        "durable_canary_authoring_command_completion_decision_contract",
        "Section 89 durable canary authoring command completion decision contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The authoring command completion decision contract is defined, but no decision record is present.",
            "A valid decision still cannot complete, save, delete, rename, or clean up without a separate application contract.",
        ),
    )


def build_canary_authoring_command_completion_application_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    decision_row = build_canary_authoring_command_completion_decision_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    decision_summary = dict(decision_row["actual"])
    decision_summary["status"] = decision_summary.pop("summary_status")
    contract = authoring_completion_application.build_canary_durable_authoring_command_completion_application_contract(
        requested=True,
        completion_decision_summary=decision_summary,
    )
    summary = authoring_completion_application.summarize_canary_durable_authoring_command_completion_applications(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_authoring_command_completion_application_count": 1,
        "application_contract_defined_count": 1,
        "completion_decision_contract_ready_count": 1,
        "evidence_ready_for_completion_count": 0,
        "completion_decision_record_valid_count": 0,
        "application_inputs_satisfied_count": 0,
        "application_record_present_count": 0,
        "record_schema_matches_count": 0,
        "application_scope_matches_count": 0,
        "explicit_application_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "application_record_valid_count": 0,
        "application_record_rejected_count": 0,
        "unsafe_application_record_count": 0,
        "missing_application_prerequisite_count": 8,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
        "durable_authoring_command_completion_allowed_count": 0,
        "durable_authoring_command_completed_count": 0,
        "durable_authoring_command_application_allowed_count": 0,
        "durable_authoring_command_application_applied_count": 0,
        "asset_write_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_promotion_allowed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_authoring_command_completion_application_count": summary.get(
            "durable_requested_canary_authoring_command_completion_application_count"
        ),
        "application_contract_defined_count": summary.get("application_contract_defined_count"),
        "completion_decision_contract_ready_count": summary.get(
            "completion_decision_contract_ready_count"
        ),
        "evidence_ready_for_completion_count": summary.get("evidence_ready_for_completion_count"),
        "completion_decision_record_valid_count": summary.get(
            "completion_decision_record_valid_count"
        ),
        "application_inputs_satisfied_count": summary.get("application_inputs_satisfied_count"),
        "application_record_present_count": summary.get("application_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "application_scope_matches_count": summary.get("application_scope_matches_count"),
        "explicit_application_authorized_count": summary.get("explicit_application_authorized_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "application_record_valid_count": summary.get("application_record_valid_count"),
        "application_record_rejected_count": summary.get("application_record_rejected_count"),
        "unsafe_application_record_count": summary.get("unsafe_application_record_count"),
        "missing_application_prerequisite_count": summary.get(
            "missing_application_prerequisite_count"
        ),
        "reported_allowed_evidence_command_count": summary.get("reported_allowed_evidence_command_count"),
        "reported_forbidden_evidence_command_count": summary.get("reported_forbidden_evidence_command_count"),
        "durable_authoring_command_completion_allowed_count": summary.get(
            "durable_authoring_command_completion_allowed_count"
        ),
        "durable_authoring_command_completed_count": summary.get(
            "durable_authoring_command_completed_count"
        ),
        "durable_authoring_command_application_allowed_count": summary.get(
            "durable_authoring_command_application_allowed_count"
        ),
        "durable_authoring_command_application_applied_count": summary.get(
            "durable_authoring_command_application_applied_count"
        ),
        "asset_write_allowed_count": summary.get("asset_write_allowed_count"),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "durable_authoring_command_dispatch_allowed_count": summary.get(
            "durable_authoring_command_dispatch_allowed_count"
        ),
        "durable_authoring_command_dispatched_count": summary.get(
            "durable_authoring_command_dispatched_count"
        ),
        "durable_authoring_command_execution_allowed_count": summary.get(
            "durable_authoring_command_execution_allowed_count"
        ),
        "durable_authoring_command_executed_count": summary.get(
            "durable_authoring_command_executed_count"
        ),
        "durable_promotion_allowed_count": summary.get("durable_promotion_allowed_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
    }
    return row(
        "durable_canary_authoring_command_completion_application_contract",
        "Section 90 durable canary authoring command completion application contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The authoring command completion application contract is defined, but no application record is present.",
            "A valid application still cannot complete, write, save, delete, rename, or clean up without a separate result contract.",
        ),
    )


def build_canary_authoring_command_completion_result_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    application_row = build_canary_authoring_command_completion_application_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    application_summary = dict(application_row["actual"])
    application_summary["status"] = application_summary.pop("summary_status")
    contract = authoring_completion_result.build_canary_durable_authoring_command_completion_result_contract(
        requested=True,
        application_summary=application_summary,
    )
    summary = authoring_completion_result.summarize_canary_durable_authoring_command_completion_results(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_authoring_command_completion_result_count": 1,
        "result_contract_defined_count": 1,
        "application_contract_ready_count": 1,
        "application_inputs_satisfied_count": 0,
        "application_record_valid_count": 0,
        "result_inputs_satisfied_count": 0,
        "result_record_present_count": 0,
        "record_schema_matches_count": 0,
        "result_scope_matches_count": 0,
        "explicit_result_authorized_count": 0,
        "result_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "allowed_result_observed_count": 0,
        "no_forbidden_results_count": 0,
        "result_record_valid_count": 0,
        "result_record_rejected_count": 0,
        "unsafe_result_record_count": 0,
        "missing_result_prerequisite_count": 11,
        "reported_allowed_result_count": 0,
        "reported_forbidden_result_count": 0,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completion_allowed_count": 0,
        "durable_authoring_command_completed_count": 0,
        "durable_authoring_command_application_allowed_count": 0,
        "durable_authoring_command_application_applied_count": 0,
        "asset_write_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "reported_completion_noop_result_count": 0,
        "reported_application_validation_result_count": 0,
        "reported_completion_completed_result_count": 0,
        "reported_asset_write_result_count": 0,
        "reported_package_dirty_result_count": 0,
        "reported_save_result_count": 0,
        "reported_delete_rename_result_count": 0,
        "reported_cleanup_result_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_authoring_command_completion_result_count": summary.get(
            "durable_requested_canary_authoring_command_completion_result_count"
        ),
        "result_contract_defined_count": summary.get("result_contract_defined_count"),
        "application_contract_ready_count": summary.get("application_contract_ready_count"),
        "application_inputs_satisfied_count": summary.get("application_inputs_satisfied_count"),
        "application_record_valid_count": summary.get("application_record_valid_count"),
        "result_inputs_satisfied_count": summary.get("result_inputs_satisfied_count"),
        "result_record_present_count": summary.get("result_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "result_scope_matches_count": summary.get("result_scope_matches_count"),
        "explicit_result_authorized_count": summary.get("explicit_result_authorized_count"),
        "result_status_passed_count": summary.get("result_status_passed_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "allowed_result_observed_count": summary.get("allowed_result_observed_count"),
        "no_forbidden_results_count": summary.get("no_forbidden_results_count"),
        "result_record_valid_count": summary.get("result_record_valid_count"),
        "result_record_rejected_count": summary.get("result_record_rejected_count"),
        "unsafe_result_record_count": summary.get("unsafe_result_record_count"),
        "missing_result_prerequisite_count": summary.get("missing_result_prerequisite_count"),
        "reported_allowed_result_count": summary.get("reported_allowed_result_count"),
        "reported_forbidden_result_count": summary.get("reported_forbidden_result_count"),
        "reported_allowed_evidence_command_count": summary.get("reported_allowed_evidence_command_count"),
        "reported_forbidden_evidence_command_count": summary.get("reported_forbidden_evidence_command_count"),
        "durable_authoring_command_completion_result_accepted_count": summary.get(
            "durable_authoring_command_completion_result_accepted_count"
        ),
        "durable_authoring_command_completion_allowed_count": summary.get(
            "durable_authoring_command_completion_allowed_count"
        ),
        "durable_authoring_command_completed_count": summary.get(
            "durable_authoring_command_completed_count"
        ),
        "durable_authoring_command_application_allowed_count": summary.get(
            "durable_authoring_command_application_allowed_count"
        ),
        "durable_authoring_command_application_applied_count": summary.get(
            "durable_authoring_command_application_applied_count"
        ),
        "asset_write_allowed_count": summary.get("asset_write_allowed_count"),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatch_allowed_count": summary.get("live_command_dispatch_allowed_count"),
        "live_command_plan_emitted_count": summary.get("live_command_plan_emitted_count"),
        "live_command_execution_allowed_count": summary.get("live_command_execution_allowed_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
        "reported_completion_noop_result_count": summary.get("reported_completion_noop_result_count"),
        "reported_application_validation_result_count": summary.get(
            "reported_application_validation_result_count"
        ),
        "reported_completion_completed_result_count": summary.get(
            "reported_completion_completed_result_count"
        ),
        "reported_asset_write_result_count": summary.get("reported_asset_write_result_count"),
        "reported_package_dirty_result_count": summary.get("reported_package_dirty_result_count"),
        "reported_save_result_count": summary.get("reported_save_result_count"),
        "reported_delete_rename_result_count": summary.get("reported_delete_rename_result_count"),
        "reported_cleanup_result_count": summary.get("reported_cleanup_result_count"),
    }
    return row(
        "durable_canary_authoring_command_completion_result_contract",
        "Section 91 durable canary authoring command completion result contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The authoring command completion result contract is defined, but no result record is present.",
            "Completed/write/save results cannot be accepted without a separate readback contract.",
        ),
    )


def build_canary_authoring_command_result_readback_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    result_row = build_canary_authoring_command_completion_result_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    result_summary = dict(result_row["actual"])
    result_summary["status"] = result_summary.pop("summary_status")
    contract = authoring_result_readback.build_canary_durable_authoring_command_result_readback_contract(
        requested=True,
        result_summary=result_summary,
    )
    summary = authoring_result_readback.summarize_canary_durable_authoring_command_result_readbacks(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_authoring_command_result_readback_count": 1,
        "readback_contract_defined_count": 1,
        "result_contract_ready_count": 1,
        "result_inputs_satisfied_count": 0,
        "result_record_valid_count": 0,
        "allowed_result_observed_count": 0,
        "no_forbidden_results_count": 0,
        "readback_inputs_satisfied_count": 0,
        "readback_record_present_count": 0,
        "record_schema_matches_count": 0,
        "readback_scope_matches_count": 0,
        "explicit_readback_authorized_count": 0,
        "readback_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "allowed_readback_observed_count": 0,
        "no_forbidden_readbacks_count": 0,
        "readback_record_valid_count": 0,
        "readback_record_rejected_count": 0,
        "unsafe_readback_record_count": 0,
        "missing_readback_prerequisite_count": 13,
        "reported_allowed_readback_count": 0,
        "reported_forbidden_readback_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_authoring_command_result_readback_count": summary.get(
            "durable_requested_canary_authoring_command_result_readback_count"
        ),
        "readback_contract_defined_count": summary.get("readback_contract_defined_count"),
        "result_contract_ready_count": summary.get("result_contract_ready_count"),
        "result_inputs_satisfied_count": summary.get("result_inputs_satisfied_count"),
        "result_record_valid_count": summary.get("result_record_valid_count"),
        "allowed_result_observed_count": summary.get("allowed_result_observed_count"),
        "no_forbidden_results_count": summary.get("no_forbidden_results_count"),
        "readback_inputs_satisfied_count": summary.get("readback_inputs_satisfied_count"),
        "readback_record_present_count": summary.get("readback_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "readback_scope_matches_count": summary.get("readback_scope_matches_count"),
        "explicit_readback_authorized_count": summary.get("explicit_readback_authorized_count"),
        "readback_status_passed_count": summary.get("readback_status_passed_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "allowed_readback_observed_count": summary.get("allowed_readback_observed_count"),
        "no_forbidden_readbacks_count": summary.get("no_forbidden_readbacks_count"),
        "readback_record_valid_count": summary.get("readback_record_valid_count"),
        "readback_record_rejected_count": summary.get("readback_record_rejected_count"),
        "unsafe_readback_record_count": summary.get("unsafe_readback_record_count"),
        "missing_readback_prerequisite_count": summary.get("missing_readback_prerequisite_count"),
        "reported_allowed_readback_count": summary.get("reported_allowed_readback_count"),
        "reported_forbidden_readback_count": summary.get("reported_forbidden_readback_count"),
        "durable_authoring_command_result_readback_accepted_count": summary.get(
            "durable_authoring_command_result_readback_accepted_count"
        ),
        "durable_authoring_command_completed_count": summary.get(
            "durable_authoring_command_completed_count"
        ),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
    }
    return row(
        "durable_canary_authoring_command_result_readback_contract",
        "Section 92 durable canary authoring command result readback contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The authoring command result readback contract is defined, but no readback record is present.",
            "Completed/write/save readbacks cannot be accepted without a final no-save release contract.",
        ),
    )


def build_canary_authoring_final_no_save_release_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readback_row = build_canary_authoring_command_result_readback_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    readback_summary = dict(readback_row["actual"])
    readback_summary["status"] = readback_summary.pop("summary_status")
    contract = (
        authoring_final_no_save_release.build_canary_durable_authoring_final_no_save_release_contract(
            requested=True,
            readback_summary=readback_summary,
        )
    )
    summary = authoring_final_no_save_release.summarize_canary_durable_authoring_final_no_save_releases(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_authoring_final_no_save_release_count": 1,
        "final_no_save_release_contract_defined_count": 1,
        "readback_contract_ready_count": 1,
        "readback_inputs_satisfied_count": 0,
        "readback_record_valid_count": 0,
        "allowed_readback_observed_count": 0,
        "no_forbidden_readbacks_count": 0,
        "final_no_save_release_inputs_satisfied_count": 0,
        "final_no_save_release_record_present_count": 0,
        "record_schema_matches_count": 0,
        "final_no_save_release_scope_matches_count": 0,
        "explicit_final_no_save_release_authorized_count": 0,
        "final_no_save_release_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "allowed_final_no_save_release_observed_count": 0,
        "no_forbidden_final_no_save_releases_count": 0,
        "final_no_save_release_record_valid_count": 0,
        "final_no_save_release_record_rejected_count": 0,
        "unsafe_final_no_save_release_record_count": 0,
        "missing_final_no_save_release_prerequisite_count": 13,
        "reported_allowed_final_no_save_release_count": 0,
        "reported_forbidden_final_no_save_release_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_authoring_final_no_save_release_count": summary.get(
            "durable_requested_canary_authoring_final_no_save_release_count"
        ),
        "final_no_save_release_contract_defined_count": summary.get(
            "final_no_save_release_contract_defined_count"
        ),
        "readback_contract_ready_count": summary.get("readback_contract_ready_count"),
        "readback_inputs_satisfied_count": summary.get("readback_inputs_satisfied_count"),
        "readback_record_valid_count": summary.get("readback_record_valid_count"),
        "allowed_readback_observed_count": summary.get("allowed_readback_observed_count"),
        "no_forbidden_readbacks_count": summary.get("no_forbidden_readbacks_count"),
        "final_no_save_release_inputs_satisfied_count": summary.get(
            "final_no_save_release_inputs_satisfied_count"
        ),
        "final_no_save_release_record_present_count": summary.get(
            "final_no_save_release_record_present_count"
        ),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "final_no_save_release_scope_matches_count": summary.get(
            "final_no_save_release_scope_matches_count"
        ),
        "explicit_final_no_save_release_authorized_count": summary.get(
            "explicit_final_no_save_release_authorized_count"
        ),
        "final_no_save_release_status_passed_count": summary.get(
            "final_no_save_release_status_passed_count"
        ),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "allowed_final_no_save_release_observed_count": summary.get(
            "allowed_final_no_save_release_observed_count"
        ),
        "no_forbidden_final_no_save_releases_count": summary.get(
            "no_forbidden_final_no_save_releases_count"
        ),
        "final_no_save_release_record_valid_count": summary.get(
            "final_no_save_release_record_valid_count"
        ),
        "final_no_save_release_record_rejected_count": summary.get(
            "final_no_save_release_record_rejected_count"
        ),
        "unsafe_final_no_save_release_record_count": summary.get(
            "unsafe_final_no_save_release_record_count"
        ),
        "missing_final_no_save_release_prerequisite_count": summary.get(
            "missing_final_no_save_release_prerequisite_count"
        ),
        "reported_allowed_final_no_save_release_count": summary.get(
            "reported_allowed_final_no_save_release_count"
        ),
        "reported_forbidden_final_no_save_release_count": summary.get(
            "reported_forbidden_final_no_save_release_count"
        ),
        "durable_authoring_final_no_save_release_accepted_count": summary.get(
            "durable_authoring_final_no_save_release_accepted_count"
        ),
        "durable_authoring_command_result_readback_accepted_count": summary.get(
            "durable_authoring_command_result_readback_accepted_count"
        ),
        "durable_authoring_command_completed_count": summary.get(
            "durable_authoring_command_completed_count"
        ),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatched_count": summary.get("live_command_dispatched_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
    }
    return row(
        "durable_canary_authoring_final_no_save_release_contract",
        "Section 93 durable canary authoring final no-save release contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The final no-save release contract is defined, but no final release record is present.",
            "Durable completion, writes, saves, delete/rename, and cleanup remain rejected.",
        ),
    )


def build_canary_authoring_final_release_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    final_release_row = build_canary_authoring_final_no_save_release_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    final_no_save_release_summary = dict(final_release_row["actual"])
    final_no_save_release_summary["status"] = final_no_save_release_summary.pop("summary_status")
    contract = (
        authoring_final_release_readiness.build_canary_durable_authoring_final_release_readiness_contract(
            requested=True,
            final_no_save_release_summary=final_no_save_release_summary,
        )
    )
    summary = authoring_final_release_readiness.summarize_canary_durable_authoring_final_release_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_canary_authoring_final_release_readiness_count": 1,
        "final_release_readiness_contract_defined_count": 1,
        "final_no_save_release_contract_ready_count": 1,
        "final_no_save_release_inputs_satisfied_count": 0,
        "final_no_save_release_record_valid_count": 0,
        "allowed_final_no_save_release_observed_count": 0,
        "no_forbidden_final_no_save_releases_count": 0,
        "final_release_readiness_inputs_satisfied_count": 0,
        "final_release_readiness_record_present_count": 0,
        "record_schema_matches_count": 0,
        "readiness_scope_matches_count": 0,
        "explicit_readiness_authorized_count": 0,
        "readiness_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_final_release_readiness_observed_count": 0,
        "no_forbidden_final_release_readiness_claims_count": 0,
        "final_release_readiness_record_valid_count": 0,
        "final_release_readiness_record_rejected_count": 0,
        "unsafe_final_release_readiness_record_count": 0,
        "missing_final_release_readiness_prerequisite_count": 14,
        "reported_allowed_final_release_readiness_count": 0,
        "reported_forbidden_final_release_readiness_count": 0,
        "durable_authoring_final_release_readiness_accepted_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "durable_executor_implementation_review_started_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_canary_authoring_final_release_readiness_count": summary.get(
            "durable_requested_canary_authoring_final_release_readiness_count"
        ),
        "final_release_readiness_contract_defined_count": summary.get(
            "final_release_readiness_contract_defined_count"
        ),
        "final_no_save_release_contract_ready_count": summary.get(
            "final_no_save_release_contract_ready_count"
        ),
        "final_no_save_release_inputs_satisfied_count": summary.get(
            "final_no_save_release_inputs_satisfied_count"
        ),
        "final_no_save_release_record_valid_count": summary.get(
            "final_no_save_release_record_valid_count"
        ),
        "allowed_final_no_save_release_observed_count": summary.get(
            "allowed_final_no_save_release_observed_count"
        ),
        "no_forbidden_final_no_save_releases_count": summary.get(
            "no_forbidden_final_no_save_releases_count"
        ),
        "final_release_readiness_inputs_satisfied_count": summary.get(
            "final_release_readiness_inputs_satisfied_count"
        ),
        "final_release_readiness_record_present_count": summary.get(
            "final_release_readiness_record_present_count"
        ),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "readiness_scope_matches_count": summary.get("readiness_scope_matches_count"),
        "explicit_readiness_authorized_count": summary.get(
            "explicit_readiness_authorized_count"
        ),
        "readiness_status_passed_count": summary.get("readiness_status_passed_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": summary.get(
            "explicit_durable_mvp_request_reconfirmed_count"
        ),
        "allowed_final_release_readiness_observed_count": summary.get(
            "allowed_final_release_readiness_observed_count"
        ),
        "no_forbidden_final_release_readiness_claims_count": summary.get(
            "no_forbidden_final_release_readiness_claims_count"
        ),
        "final_release_readiness_record_valid_count": summary.get(
            "final_release_readiness_record_valid_count"
        ),
        "final_release_readiness_record_rejected_count": summary.get(
            "final_release_readiness_record_rejected_count"
        ),
        "unsafe_final_release_readiness_record_count": summary.get(
            "unsafe_final_release_readiness_record_count"
        ),
        "missing_final_release_readiness_prerequisite_count": summary.get(
            "missing_final_release_readiness_prerequisite_count"
        ),
        "reported_allowed_final_release_readiness_count": summary.get(
            "reported_allowed_final_release_readiness_count"
        ),
        "reported_forbidden_final_release_readiness_count": summary.get(
            "reported_forbidden_final_release_readiness_count"
        ),
        "durable_authoring_final_release_readiness_accepted_count": summary.get(
            "durable_authoring_final_release_readiness_accepted_count"
        ),
        "durable_authoring_final_no_save_release_accepted_count": summary.get(
            "durable_authoring_final_no_save_release_accepted_count"
        ),
        "durable_authoring_command_result_readback_accepted_count": summary.get(
            "durable_authoring_command_result_readback_accepted_count"
        ),
        "durable_authoring_command_completed_count": summary.get(
            "durable_authoring_command_completed_count"
        ),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatched_count": summary.get("live_command_dispatched_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
        "durable_executor_implementation_review_started_count": summary.get(
            "durable_executor_implementation_review_started_count"
        ),
    }
    return row(
        "durable_canary_authoring_final_release_readiness_contract",
        "Section 94 durable canary authoring final release readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The final release readiness contract is defined, but no readiness record is present.",
            "Implementation review requires a separate explicit durable MVP review contract.",
        ),
    )


def build_durable_executor_implementation_review_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readiness_row = build_canary_authoring_final_release_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    readiness_summary = dict(readiness_row["actual"])
    readiness_summary["status"] = readiness_summary.pop("summary_status")
    contract = implementation_review.build_durable_executor_implementation_review_contract(
        requested=True,
        final_release_readiness_summary=readiness_summary,
    )
    summary = implementation_review.summarize_durable_executor_implementation_reviews(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_implementation_review_count": 1,
        "implementation_review_contract_defined_count": 1,
        "final_release_readiness_contract_ready_count": 1,
        "final_release_readiness_inputs_satisfied_count": 0,
        "final_release_readiness_record_valid_count": 0,
        "allowed_final_release_readiness_observed_count": 0,
        "no_forbidden_final_release_readiness_claims_count": 0,
        "implementation_review_inputs_satisfied_count": 0,
        "implementation_review_record_present_count": 0,
        "record_schema_matches_count": 0,
        "implementation_review_scope_matches_count": 0,
        "explicit_implementation_review_authorized_count": 0,
        "review_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_implementation_review_observed_count": 0,
        "no_forbidden_implementation_review_claims_count": 0,
        "implementation_review_record_valid_count": 0,
        "implementation_review_record_rejected_count": 0,
        "unsafe_implementation_review_record_count": 0,
        "missing_implementation_review_prerequisite_count": 14,
        "reported_allowed_implementation_review_count": 0,
        "reported_forbidden_implementation_review_count": 0,
        "durable_executor_implementation_review_started_count": 0,
        "durable_executor_implementation_review_accepted_count": 0,
        "durable_executor_implementation_plan_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_executor_implementation_review_count": summary.get(
            "durable_requested_executor_implementation_review_count"
        ),
        "implementation_review_contract_defined_count": summary.get(
            "implementation_review_contract_defined_count"
        ),
        "final_release_readiness_contract_ready_count": summary.get(
            "final_release_readiness_contract_ready_count"
        ),
        "final_release_readiness_inputs_satisfied_count": summary.get(
            "final_release_readiness_inputs_satisfied_count"
        ),
        "final_release_readiness_record_valid_count": summary.get(
            "final_release_readiness_record_valid_count"
        ),
        "allowed_final_release_readiness_observed_count": summary.get(
            "allowed_final_release_readiness_observed_count"
        ),
        "no_forbidden_final_release_readiness_claims_count": summary.get(
            "no_forbidden_final_release_readiness_claims_count"
        ),
        "implementation_review_inputs_satisfied_count": summary.get(
            "implementation_review_inputs_satisfied_count"
        ),
        "implementation_review_record_present_count": summary.get(
            "implementation_review_record_present_count"
        ),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "implementation_review_scope_matches_count": summary.get(
            "implementation_review_scope_matches_count"
        ),
        "explicit_implementation_review_authorized_count": summary.get(
            "explicit_implementation_review_authorized_count"
        ),
        "review_status_passed_count": summary.get("review_status_passed_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": summary.get(
            "explicit_durable_mvp_request_reconfirmed_count"
        ),
        "allowed_implementation_review_observed_count": summary.get(
            "allowed_implementation_review_observed_count"
        ),
        "no_forbidden_implementation_review_claims_count": summary.get(
            "no_forbidden_implementation_review_claims_count"
        ),
        "implementation_review_record_valid_count": summary.get(
            "implementation_review_record_valid_count"
        ),
        "implementation_review_record_rejected_count": summary.get(
            "implementation_review_record_rejected_count"
        ),
        "unsafe_implementation_review_record_count": summary.get(
            "unsafe_implementation_review_record_count"
        ),
        "missing_implementation_review_prerequisite_count": summary.get(
            "missing_implementation_review_prerequisite_count"
        ),
        "reported_allowed_implementation_review_count": summary.get(
            "reported_allowed_implementation_review_count"
        ),
        "reported_forbidden_implementation_review_count": summary.get(
            "reported_forbidden_implementation_review_count"
        ),
        "durable_executor_implementation_review_started_count": summary.get(
            "durable_executor_implementation_review_started_count"
        ),
        "durable_executor_implementation_review_accepted_count": summary.get(
            "durable_executor_implementation_review_accepted_count"
        ),
        "durable_executor_implementation_plan_started_count": summary.get(
            "durable_executor_implementation_plan_started_count"
        ),
        "code_change_performed_count": summary.get("code_change_performed_count"),
        "executor_code_modified_count": summary.get("executor_code_modified_count"),
        "unreal_asset_modified_count": summary.get("unreal_asset_modified_count"),
        "live_bridge_probe_started_count": summary.get("live_bridge_probe_started_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatched_count": summary.get("live_command_dispatched_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
    }
    return row(
        "durable_executor_implementation_review_gate_contract",
        "Section 95 durable executor implementation review contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The implementation review contract is defined, but no review record is present.",
            "Implementation planning, code changes, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_implementation_plan_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    review_row = build_durable_executor_implementation_review_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    review_summary = dict(review_row["actual"])
    review_summary["status"] = review_summary.pop("summary_status")
    contract = implementation_plan.build_durable_executor_implementation_plan_contract(
        requested=True,
        implementation_review_summary=review_summary,
    )
    summary = implementation_plan.summarize_durable_executor_implementation_plans(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_implementation_plan_count": 1,
        "implementation_plan_contract_defined_count": 1,
        "implementation_review_contract_ready_count": 1,
        "implementation_review_inputs_satisfied_count": 0,
        "implementation_review_record_valid_count": 0,
        "allowed_implementation_review_observed_count": 0,
        "no_forbidden_implementation_review_claims_count": 0,
        "implementation_plan_inputs_satisfied_count": 0,
        "implementation_plan_record_present_count": 0,
        "record_schema_matches_count": 0,
        "implementation_plan_scope_matches_count": 0,
        "explicit_implementation_plan_authorized_count": 0,
        "plan_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_implementation_plan_observed_count": 0,
        "no_forbidden_implementation_plan_claims_count": 0,
        "implementation_plan_record_valid_count": 0,
        "implementation_plan_record_rejected_count": 0,
        "unsafe_implementation_plan_record_count": 0,
        "missing_implementation_plan_prerequisite_count": 14,
        "reported_allowed_implementation_plan_count": 0,
        "reported_forbidden_implementation_plan_count": 0,
        "durable_executor_implementation_plan_started_count": 0,
        "durable_executor_implementation_plan_accepted_count": 0,
        "durable_executor_change_design_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_executor_implementation_plan_count": summary.get(
            "durable_requested_executor_implementation_plan_count"
        ),
        "implementation_plan_contract_defined_count": summary.get(
            "implementation_plan_contract_defined_count"
        ),
        "implementation_review_contract_ready_count": summary.get(
            "implementation_review_contract_ready_count"
        ),
        "implementation_review_inputs_satisfied_count": summary.get(
            "implementation_review_inputs_satisfied_count"
        ),
        "implementation_review_record_valid_count": summary.get(
            "implementation_review_record_valid_count"
        ),
        "allowed_implementation_review_observed_count": summary.get(
            "allowed_implementation_review_observed_count"
        ),
        "no_forbidden_implementation_review_claims_count": summary.get(
            "no_forbidden_implementation_review_claims_count"
        ),
        "implementation_plan_inputs_satisfied_count": summary.get(
            "implementation_plan_inputs_satisfied_count"
        ),
        "implementation_plan_record_present_count": summary.get(
            "implementation_plan_record_present_count"
        ),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "implementation_plan_scope_matches_count": summary.get(
            "implementation_plan_scope_matches_count"
        ),
        "explicit_implementation_plan_authorized_count": summary.get(
            "explicit_implementation_plan_authorized_count"
        ),
        "plan_status_passed_count": summary.get("plan_status_passed_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": summary.get(
            "explicit_durable_mvp_request_reconfirmed_count"
        ),
        "allowed_implementation_plan_observed_count": summary.get(
            "allowed_implementation_plan_observed_count"
        ),
        "no_forbidden_implementation_plan_claims_count": summary.get(
            "no_forbidden_implementation_plan_claims_count"
        ),
        "implementation_plan_record_valid_count": summary.get(
            "implementation_plan_record_valid_count"
        ),
        "implementation_plan_record_rejected_count": summary.get(
            "implementation_plan_record_rejected_count"
        ),
        "unsafe_implementation_plan_record_count": summary.get(
            "unsafe_implementation_plan_record_count"
        ),
        "missing_implementation_plan_prerequisite_count": summary.get(
            "missing_implementation_plan_prerequisite_count"
        ),
        "reported_allowed_implementation_plan_count": summary.get(
            "reported_allowed_implementation_plan_count"
        ),
        "reported_forbidden_implementation_plan_count": summary.get(
            "reported_forbidden_implementation_plan_count"
        ),
        "durable_executor_implementation_plan_started_count": summary.get(
            "durable_executor_implementation_plan_started_count"
        ),
        "durable_executor_implementation_plan_accepted_count": summary.get(
            "durable_executor_implementation_plan_accepted_count"
        ),
        "durable_executor_change_design_started_count": summary.get(
            "durable_executor_change_design_started_count"
        ),
        "code_change_performed_count": summary.get("code_change_performed_count"),
        "executor_code_modified_count": summary.get("executor_code_modified_count"),
        "unreal_asset_modified_count": summary.get("unreal_asset_modified_count"),
        "live_bridge_probe_started_count": summary.get("live_bridge_probe_started_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatched_count": summary.get("live_command_dispatched_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
    }
    return row(
        "durable_executor_implementation_plan_contract",
        "Section 96 durable executor implementation plan contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The implementation plan contract is defined, but no plan record is present.",
            "Change design, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_change_design_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    plan_row = build_durable_executor_implementation_plan_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    plan_summary = dict(plan_row["actual"])
    plan_summary["status"] = plan_summary.pop("summary_status")
    contract = change_design.build_durable_executor_change_design_contract(
        requested=True,
        implementation_plan_summary=plan_summary,
    )
    summary = change_design.summarize_durable_executor_change_designs([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_change_design_count": 1,
        "change_design_contract_defined_count": 1,
        "implementation_plan_contract_ready_count": 1,
        "implementation_plan_inputs_satisfied_count": 0,
        "implementation_plan_record_valid_count": 0,
        "allowed_implementation_plan_observed_count": 0,
        "no_forbidden_implementation_plan_claims_count": 0,
        "change_design_inputs_satisfied_count": 0,
        "change_design_record_present_count": 0,
        "record_schema_matches_count": 0,
        "change_design_scope_matches_count": 0,
        "explicit_change_design_authorized_count": 0,
        "design_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_change_design_observed_count": 0,
        "no_forbidden_change_design_claims_count": 0,
        "change_design_record_valid_count": 0,
        "change_design_record_rejected_count": 0,
        "unsafe_change_design_record_count": 0,
        "missing_change_design_prerequisite_count": 14,
        "reported_allowed_change_design_count": 0,
        "reported_forbidden_change_design_count": 0,
        "durable_executor_change_design_started_count": 0,
        "durable_executor_change_design_accepted_count": 0,
        "durable_executor_code_change_approval_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_executor_change_design_count": summary.get(
            "durable_requested_executor_change_design_count"
        ),
        "change_design_contract_defined_count": summary.get(
            "change_design_contract_defined_count"
        ),
        "implementation_plan_contract_ready_count": summary.get(
            "implementation_plan_contract_ready_count"
        ),
        "implementation_plan_inputs_satisfied_count": summary.get(
            "implementation_plan_inputs_satisfied_count"
        ),
        "implementation_plan_record_valid_count": summary.get(
            "implementation_plan_record_valid_count"
        ),
        "allowed_implementation_plan_observed_count": summary.get(
            "allowed_implementation_plan_observed_count"
        ),
        "no_forbidden_implementation_plan_claims_count": summary.get(
            "no_forbidden_implementation_plan_claims_count"
        ),
        "change_design_inputs_satisfied_count": summary.get("change_design_inputs_satisfied_count"),
        "change_design_record_present_count": summary.get("change_design_record_present_count"),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "change_design_scope_matches_count": summary.get("change_design_scope_matches_count"),
        "explicit_change_design_authorized_count": summary.get(
            "explicit_change_design_authorized_count"
        ),
        "design_status_passed_count": summary.get("design_status_passed_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": summary.get(
            "explicit_durable_mvp_request_reconfirmed_count"
        ),
        "allowed_change_design_observed_count": summary.get(
            "allowed_change_design_observed_count"
        ),
        "no_forbidden_change_design_claims_count": summary.get(
            "no_forbidden_change_design_claims_count"
        ),
        "change_design_record_valid_count": summary.get("change_design_record_valid_count"),
        "change_design_record_rejected_count": summary.get(
            "change_design_record_rejected_count"
        ),
        "unsafe_change_design_record_count": summary.get("unsafe_change_design_record_count"),
        "missing_change_design_prerequisite_count": summary.get(
            "missing_change_design_prerequisite_count"
        ),
        "reported_allowed_change_design_count": summary.get(
            "reported_allowed_change_design_count"
        ),
        "reported_forbidden_change_design_count": summary.get(
            "reported_forbidden_change_design_count"
        ),
        "durable_executor_change_design_started_count": summary.get(
            "durable_executor_change_design_started_count"
        ),
        "durable_executor_change_design_accepted_count": summary.get(
            "durable_executor_change_design_accepted_count"
        ),
        "durable_executor_code_change_approval_started_count": summary.get(
            "durable_executor_code_change_approval_started_count"
        ),
        "code_change_performed_count": summary.get("code_change_performed_count"),
        "executor_code_modified_count": summary.get("executor_code_modified_count"),
        "unreal_asset_modified_count": summary.get("unreal_asset_modified_count"),
        "live_bridge_probe_started_count": summary.get("live_bridge_probe_started_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatched_count": summary.get("live_command_dispatched_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
    }
    return row(
        "durable_executor_change_design_contract",
        "Section 97 durable executor change design contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The change design contract is defined, but no design record is present.",
            "Code-change approval, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_code_change_approval_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    design_row = build_durable_executor_change_design_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    design_summary = dict(design_row["actual"])
    design_summary["status"] = design_summary.pop("summary_status")
    contract = code_change_approval.build_durable_executor_code_change_approval_contract(
        requested=True,
        change_design_summary=design_summary,
    )
    summary = code_change_approval.summarize_durable_executor_code_change_approvals(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_code_change_approval_count": 1,
        "code_change_approval_contract_defined_count": 1,
        "change_design_contract_ready_count": 1,
        "change_design_inputs_satisfied_count": 0,
        "change_design_record_valid_count": 0,
        "allowed_change_design_observed_count": 0,
        "no_forbidden_change_design_claims_count": 0,
        "code_change_approval_inputs_satisfied_count": 0,
        "code_change_approval_record_present_count": 0,
        "record_schema_matches_count": 0,
        "code_change_approval_scope_matches_count": 0,
        "explicit_code_change_approval_authorized_count": 0,
        "approval_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_code_change_approval_observed_count": 0,
        "no_forbidden_code_change_approval_claims_count": 0,
        "code_change_approval_record_valid_count": 0,
        "code_change_approval_record_rejected_count": 0,
        "unsafe_code_change_approval_record_count": 0,
        "missing_code_change_approval_prerequisite_count": 14,
        "reported_allowed_code_change_approval_count": 0,
        "reported_forbidden_code_change_approval_count": 0,
        "durable_executor_code_change_approval_started_count": 0,
        "durable_executor_code_change_approval_accepted_count": 0,
        "durable_executor_code_patch_plan_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_executor_code_change_approval_count": summary.get(
            "durable_requested_executor_code_change_approval_count"
        ),
        "code_change_approval_contract_defined_count": summary.get(
            "code_change_approval_contract_defined_count"
        ),
        "change_design_contract_ready_count": summary.get("change_design_contract_ready_count"),
        "change_design_inputs_satisfied_count": summary.get(
            "change_design_inputs_satisfied_count"
        ),
        "change_design_record_valid_count": summary.get("change_design_record_valid_count"),
        "allowed_change_design_observed_count": summary.get(
            "allowed_change_design_observed_count"
        ),
        "no_forbidden_change_design_claims_count": summary.get(
            "no_forbidden_change_design_claims_count"
        ),
        "code_change_approval_inputs_satisfied_count": summary.get(
            "code_change_approval_inputs_satisfied_count"
        ),
        "code_change_approval_record_present_count": summary.get(
            "code_change_approval_record_present_count"
        ),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "code_change_approval_scope_matches_count": summary.get(
            "code_change_approval_scope_matches_count"
        ),
        "explicit_code_change_approval_authorized_count": summary.get(
            "explicit_code_change_approval_authorized_count"
        ),
        "approval_status_passed_count": summary.get("approval_status_passed_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": summary.get(
            "explicit_durable_mvp_request_reconfirmed_count"
        ),
        "allowed_code_change_approval_observed_count": summary.get(
            "allowed_code_change_approval_observed_count"
        ),
        "no_forbidden_code_change_approval_claims_count": summary.get(
            "no_forbidden_code_change_approval_claims_count"
        ),
        "code_change_approval_record_valid_count": summary.get(
            "code_change_approval_record_valid_count"
        ),
        "code_change_approval_record_rejected_count": summary.get(
            "code_change_approval_record_rejected_count"
        ),
        "unsafe_code_change_approval_record_count": summary.get(
            "unsafe_code_change_approval_record_count"
        ),
        "missing_code_change_approval_prerequisite_count": summary.get(
            "missing_code_change_approval_prerequisite_count"
        ),
        "reported_allowed_code_change_approval_count": summary.get(
            "reported_allowed_code_change_approval_count"
        ),
        "reported_forbidden_code_change_approval_count": summary.get(
            "reported_forbidden_code_change_approval_count"
        ),
        "durable_executor_code_change_approval_started_count": summary.get(
            "durable_executor_code_change_approval_started_count"
        ),
        "durable_executor_code_change_approval_accepted_count": summary.get(
            "durable_executor_code_change_approval_accepted_count"
        ),
        "durable_executor_code_patch_plan_started_count": summary.get(
            "durable_executor_code_patch_plan_started_count"
        ),
        "code_change_performed_count": summary.get("code_change_performed_count"),
        "executor_code_modified_count": summary.get("executor_code_modified_count"),
        "unreal_asset_modified_count": summary.get("unreal_asset_modified_count"),
        "live_bridge_probe_started_count": summary.get("live_bridge_probe_started_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatched_count": summary.get("live_command_dispatched_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
    }
    return row(
        "durable_executor_code_change_approval_contract",
        "Section 98 durable executor code-change approval contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The code-change approval contract is defined, but no approval record is present.",
            "Patch planning, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_code_patch_plan_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    approval_row = build_durable_executor_code_change_approval_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    approval_summary = dict(approval_row["actual"])
    approval_summary["status"] = approval_summary.pop("summary_status")
    contract = code_patch_plan.build_durable_executor_code_patch_plan_contract(
        requested=True,
        code_change_approval_summary=approval_summary,
    )
    summary = code_patch_plan.summarize_durable_executor_code_patch_plans([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_code_patch_plan_count": 1,
        "code_patch_plan_contract_defined_count": 1,
        "code_change_approval_contract_ready_count": 1,
        "code_change_approval_inputs_satisfied_count": 0,
        "code_change_approval_record_valid_count": 0,
        "allowed_code_change_approval_observed_count": 0,
        "no_forbidden_code_change_approval_claims_count": 0,
        "code_patch_plan_inputs_satisfied_count": 0,
        "code_patch_plan_record_present_count": 0,
        "record_schema_matches_count": 0,
        "code_patch_plan_scope_matches_count": 0,
        "explicit_code_patch_plan_authorized_count": 0,
        "plan_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_code_patch_plan_observed_count": 0,
        "no_forbidden_code_patch_plan_claims_count": 0,
        "code_patch_plan_record_valid_count": 0,
        "code_patch_plan_record_rejected_count": 0,
        "unsafe_code_patch_plan_record_count": 0,
        "missing_code_patch_plan_prerequisite_count": 14,
        "reported_allowed_code_patch_plan_count": 0,
        "reported_forbidden_code_patch_plan_count": 0,
        "durable_executor_code_patch_plan_started_count": 0,
        "durable_executor_code_patch_plan_accepted_count": 0,
        "durable_executor_code_patch_review_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_executor_code_patch_plan_count": summary.get(
            "durable_requested_executor_code_patch_plan_count"
        ),
        "code_patch_plan_contract_defined_count": summary.get(
            "code_patch_plan_contract_defined_count"
        ),
        "code_change_approval_contract_ready_count": summary.get(
            "code_change_approval_contract_ready_count"
        ),
        "code_change_approval_inputs_satisfied_count": summary.get(
            "code_change_approval_inputs_satisfied_count"
        ),
        "code_change_approval_record_valid_count": summary.get(
            "code_change_approval_record_valid_count"
        ),
        "allowed_code_change_approval_observed_count": summary.get(
            "allowed_code_change_approval_observed_count"
        ),
        "no_forbidden_code_change_approval_claims_count": summary.get(
            "no_forbidden_code_change_approval_claims_count"
        ),
        "code_patch_plan_inputs_satisfied_count": summary.get(
            "code_patch_plan_inputs_satisfied_count"
        ),
        "code_patch_plan_record_present_count": summary.get(
            "code_patch_plan_record_present_count"
        ),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "code_patch_plan_scope_matches_count": summary.get(
            "code_patch_plan_scope_matches_count"
        ),
        "explicit_code_patch_plan_authorized_count": summary.get(
            "explicit_code_patch_plan_authorized_count"
        ),
        "plan_status_passed_count": summary.get("plan_status_passed_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": summary.get(
            "explicit_durable_mvp_request_reconfirmed_count"
        ),
        "allowed_code_patch_plan_observed_count": summary.get(
            "allowed_code_patch_plan_observed_count"
        ),
        "no_forbidden_code_patch_plan_claims_count": summary.get(
            "no_forbidden_code_patch_plan_claims_count"
        ),
        "code_patch_plan_record_valid_count": summary.get(
            "code_patch_plan_record_valid_count"
        ),
        "code_patch_plan_record_rejected_count": summary.get(
            "code_patch_plan_record_rejected_count"
        ),
        "unsafe_code_patch_plan_record_count": summary.get(
            "unsafe_code_patch_plan_record_count"
        ),
        "missing_code_patch_plan_prerequisite_count": summary.get(
            "missing_code_patch_plan_prerequisite_count"
        ),
        "reported_allowed_code_patch_plan_count": summary.get(
            "reported_allowed_code_patch_plan_count"
        ),
        "reported_forbidden_code_patch_plan_count": summary.get(
            "reported_forbidden_code_patch_plan_count"
        ),
        "durable_executor_code_patch_plan_started_count": summary.get(
            "durable_executor_code_patch_plan_started_count"
        ),
        "durable_executor_code_patch_plan_accepted_count": summary.get(
            "durable_executor_code_patch_plan_accepted_count"
        ),
        "durable_executor_code_patch_review_started_count": summary.get(
            "durable_executor_code_patch_review_started_count"
        ),
        "code_change_performed_count": summary.get("code_change_performed_count"),
        "executor_code_modified_count": summary.get("executor_code_modified_count"),
        "unreal_asset_modified_count": summary.get("unreal_asset_modified_count"),
        "live_bridge_probe_started_count": summary.get("live_bridge_probe_started_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatched_count": summary.get("live_command_dispatched_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
    }
    return row(
        "durable_executor_code_patch_plan_contract",
        "Section 99 durable executor code patch plan contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The code patch plan contract is defined, but no patch plan record is present.",
            "Code patch review, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_code_patch_review_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    patch_plan_row = build_durable_executor_code_patch_plan_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    patch_plan_summary = dict(patch_plan_row["actual"])
    patch_plan_summary["status"] = patch_plan_summary.pop("summary_status")
    contract = code_patch_review.build_durable_executor_code_patch_review_contract(
        requested=True,
        code_patch_plan_summary=patch_plan_summary,
    )
    summary = code_patch_review.summarize_durable_executor_code_patch_reviews(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_code_patch_review_count": 1,
        "code_patch_review_contract_defined_count": 1,
        "code_patch_plan_contract_ready_count": 1,
        "code_patch_plan_inputs_satisfied_count": 0,
        "code_patch_plan_record_valid_count": 0,
        "allowed_code_patch_plan_observed_count": 0,
        "no_forbidden_code_patch_plan_claims_count": 0,
        "code_patch_review_inputs_satisfied_count": 0,
        "code_patch_review_record_present_count": 0,
        "record_schema_matches_count": 0,
        "code_patch_review_scope_matches_count": 0,
        "explicit_code_patch_review_authorized_count": 0,
        "review_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_code_patch_review_observed_count": 0,
        "no_forbidden_code_patch_review_claims_count": 0,
        "code_patch_review_record_valid_count": 0,
        "code_patch_review_record_rejected_count": 0,
        "unsafe_code_patch_review_record_count": 0,
        "missing_code_patch_review_prerequisite_count": 14,
        "reported_allowed_code_patch_review_count": 0,
        "reported_forbidden_code_patch_review_count": 0,
        "durable_executor_code_patch_review_started_count": 0,
        "durable_executor_code_patch_review_accepted_count": 0,
        "durable_executor_code_patch_application_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_executor_code_patch_review_count": summary.get(
            "durable_requested_executor_code_patch_review_count"
        ),
        "code_patch_review_contract_defined_count": summary.get(
            "code_patch_review_contract_defined_count"
        ),
        "code_patch_plan_contract_ready_count": summary.get(
            "code_patch_plan_contract_ready_count"
        ),
        "code_patch_plan_inputs_satisfied_count": summary.get(
            "code_patch_plan_inputs_satisfied_count"
        ),
        "code_patch_plan_record_valid_count": summary.get(
            "code_patch_plan_record_valid_count"
        ),
        "allowed_code_patch_plan_observed_count": summary.get(
            "allowed_code_patch_plan_observed_count"
        ),
        "no_forbidden_code_patch_plan_claims_count": summary.get(
            "no_forbidden_code_patch_plan_claims_count"
        ),
        "code_patch_review_inputs_satisfied_count": summary.get(
            "code_patch_review_inputs_satisfied_count"
        ),
        "code_patch_review_record_present_count": summary.get(
            "code_patch_review_record_present_count"
        ),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "code_patch_review_scope_matches_count": summary.get(
            "code_patch_review_scope_matches_count"
        ),
        "explicit_code_patch_review_authorized_count": summary.get(
            "explicit_code_patch_review_authorized_count"
        ),
        "review_status_passed_count": summary.get("review_status_passed_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": summary.get(
            "explicit_durable_mvp_request_reconfirmed_count"
        ),
        "allowed_code_patch_review_observed_count": summary.get(
            "allowed_code_patch_review_observed_count"
        ),
        "no_forbidden_code_patch_review_claims_count": summary.get(
            "no_forbidden_code_patch_review_claims_count"
        ),
        "code_patch_review_record_valid_count": summary.get(
            "code_patch_review_record_valid_count"
        ),
        "code_patch_review_record_rejected_count": summary.get(
            "code_patch_review_record_rejected_count"
        ),
        "unsafe_code_patch_review_record_count": summary.get(
            "unsafe_code_patch_review_record_count"
        ),
        "missing_code_patch_review_prerequisite_count": summary.get(
            "missing_code_patch_review_prerequisite_count"
        ),
        "reported_allowed_code_patch_review_count": summary.get(
            "reported_allowed_code_patch_review_count"
        ),
        "reported_forbidden_code_patch_review_count": summary.get(
            "reported_forbidden_code_patch_review_count"
        ),
        "durable_executor_code_patch_review_started_count": summary.get(
            "durable_executor_code_patch_review_started_count"
        ),
        "durable_executor_code_patch_review_accepted_count": summary.get(
            "durable_executor_code_patch_review_accepted_count"
        ),
        "durable_executor_code_patch_application_started_count": summary.get(
            "durable_executor_code_patch_application_started_count"
        ),
        "code_change_performed_count": summary.get("code_change_performed_count"),
        "executor_code_modified_count": summary.get("executor_code_modified_count"),
        "unreal_asset_modified_count": summary.get("unreal_asset_modified_count"),
        "live_bridge_probe_started_count": summary.get("live_bridge_probe_started_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatched_count": summary.get("live_command_dispatched_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
    }
    return row(
        "durable_executor_code_patch_review_contract",
        "Section 100 durable executor code patch review contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The code patch review contract is defined, but no review record is present.",
            "Code patch application, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_code_patch_application_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    review_row = build_durable_executor_code_patch_review_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    review_summary = dict(review_row["actual"])
    review_summary["status"] = review_summary.pop("summary_status")
    contract = (
        code_patch_application.build_durable_executor_code_patch_application_contract(
            requested=True,
            code_patch_review_summary=review_summary,
        )
    )
    summary = code_patch_application.summarize_durable_executor_code_patch_applications(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_code_patch_application_count": 1,
        "code_patch_application_contract_defined_count": 1,
        "code_patch_review_contract_ready_count": 1,
        "code_patch_review_inputs_satisfied_count": 0,
        "code_patch_review_record_valid_count": 0,
        "allowed_code_patch_review_observed_count": 0,
        "no_forbidden_code_patch_review_claims_count": 0,
        "code_patch_application_inputs_satisfied_count": 0,
        "code_patch_application_record_present_count": 0,
        "record_schema_matches_count": 0,
        "code_patch_application_scope_matches_count": 0,
        "explicit_code_patch_application_authorized_count": 0,
        "application_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_code_patch_application_observed_count": 0,
        "no_forbidden_code_patch_application_claims_count": 0,
        "code_patch_application_record_valid_count": 0,
        "code_patch_application_record_rejected_count": 0,
        "unsafe_code_patch_application_record_count": 0,
        "missing_code_patch_application_prerequisite_count": 14,
        "reported_allowed_code_patch_application_count": 0,
        "reported_forbidden_code_patch_application_count": 0,
        "durable_executor_code_patch_application_started_count": 0,
        "durable_executor_code_patch_application_accepted_count": 0,
        "durable_executor_code_patch_execution_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_executor_code_patch_application_count": summary.get(
            "durable_requested_executor_code_patch_application_count"
        ),
        "code_patch_application_contract_defined_count": summary.get(
            "code_patch_application_contract_defined_count"
        ),
        "code_patch_review_contract_ready_count": summary.get(
            "code_patch_review_contract_ready_count"
        ),
        "code_patch_review_inputs_satisfied_count": summary.get(
            "code_patch_review_inputs_satisfied_count"
        ),
        "code_patch_review_record_valid_count": summary.get(
            "code_patch_review_record_valid_count"
        ),
        "allowed_code_patch_review_observed_count": summary.get(
            "allowed_code_patch_review_observed_count"
        ),
        "no_forbidden_code_patch_review_claims_count": summary.get(
            "no_forbidden_code_patch_review_claims_count"
        ),
        "code_patch_application_inputs_satisfied_count": summary.get(
            "code_patch_application_inputs_satisfied_count"
        ),
        "code_patch_application_record_present_count": summary.get(
            "code_patch_application_record_present_count"
        ),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "code_patch_application_scope_matches_count": summary.get(
            "code_patch_application_scope_matches_count"
        ),
        "explicit_code_patch_application_authorized_count": summary.get(
            "explicit_code_patch_application_authorized_count"
        ),
        "application_status_passed_count": summary.get(
            "application_status_passed_count"
        ),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": summary.get(
            "explicit_durable_mvp_request_reconfirmed_count"
        ),
        "allowed_code_patch_application_observed_count": summary.get(
            "allowed_code_patch_application_observed_count"
        ),
        "no_forbidden_code_patch_application_claims_count": summary.get(
            "no_forbidden_code_patch_application_claims_count"
        ),
        "code_patch_application_record_valid_count": summary.get(
            "code_patch_application_record_valid_count"
        ),
        "code_patch_application_record_rejected_count": summary.get(
            "code_patch_application_record_rejected_count"
        ),
        "unsafe_code_patch_application_record_count": summary.get(
            "unsafe_code_patch_application_record_count"
        ),
        "missing_code_patch_application_prerequisite_count": summary.get(
            "missing_code_patch_application_prerequisite_count"
        ),
        "reported_allowed_code_patch_application_count": summary.get(
            "reported_allowed_code_patch_application_count"
        ),
        "reported_forbidden_code_patch_application_count": summary.get(
            "reported_forbidden_code_patch_application_count"
        ),
        "durable_executor_code_patch_application_started_count": summary.get(
            "durable_executor_code_patch_application_started_count"
        ),
        "durable_executor_code_patch_application_accepted_count": summary.get(
            "durable_executor_code_patch_application_accepted_count"
        ),
        "durable_executor_code_patch_execution_started_count": summary.get(
            "durable_executor_code_patch_execution_started_count"
        ),
        "code_change_performed_count": summary.get("code_change_performed_count"),
        "executor_code_modified_count": summary.get("executor_code_modified_count"),
        "unreal_asset_modified_count": summary.get("unreal_asset_modified_count"),
        "live_bridge_probe_started_count": summary.get("live_bridge_probe_started_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatched_count": summary.get("live_command_dispatched_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
    }
    return row(
        "durable_executor_code_patch_application_contract",
        "Section 101 durable executor code patch application contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The code patch application contract is defined, but no application record is present.",
            "Code patch execution, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_code_patch_execution_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    application_row = build_durable_executor_code_patch_application_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    application_summary = dict(application_row["actual"])
    application_summary["status"] = application_summary.pop("summary_status")
    contract = code_patch_execution.build_durable_executor_code_patch_execution_contract(
        requested=True,
        code_patch_application_summary=application_summary,
    )
    summary = code_patch_execution.summarize_durable_executor_code_patch_executions(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_code_patch_execution_count": 1,
        "code_patch_execution_contract_defined_count": 1,
        "code_patch_application_contract_ready_count": 1,
        "code_patch_application_inputs_satisfied_count": 0,
        "code_patch_application_record_valid_count": 0,
        "allowed_code_patch_application_observed_count": 0,
        "no_forbidden_code_patch_application_claims_count": 0,
        "code_patch_execution_inputs_satisfied_count": 0,
        "code_patch_execution_record_present_count": 0,
        "record_schema_matches_count": 0,
        "code_patch_execution_scope_matches_count": 0,
        "explicit_code_patch_execution_authorized_count": 0,
        "execution_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_code_patch_execution_observed_count": 0,
        "no_forbidden_code_patch_execution_claims_count": 0,
        "code_patch_execution_record_valid_count": 0,
        "code_patch_execution_record_rejected_count": 0,
        "unsafe_code_patch_execution_record_count": 0,
        "missing_code_patch_execution_prerequisite_count": 14,
        "reported_allowed_code_patch_execution_count": 0,
        "reported_forbidden_code_patch_execution_count": 0,
        "durable_executor_code_patch_execution_started_count": 0,
        "durable_executor_code_patch_execution_accepted_count": 0,
        "durable_executor_code_patch_result_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        "summary_status": summary.get("status"),
        "durable_requested_executor_code_patch_execution_count": summary.get(
            "durable_requested_executor_code_patch_execution_count"
        ),
        "code_patch_execution_contract_defined_count": summary.get(
            "code_patch_execution_contract_defined_count"
        ),
        "code_patch_application_contract_ready_count": summary.get(
            "code_patch_application_contract_ready_count"
        ),
        "code_patch_application_inputs_satisfied_count": summary.get(
            "code_patch_application_inputs_satisfied_count"
        ),
        "code_patch_application_record_valid_count": summary.get(
            "code_patch_application_record_valid_count"
        ),
        "allowed_code_patch_application_observed_count": summary.get(
            "allowed_code_patch_application_observed_count"
        ),
        "no_forbidden_code_patch_application_claims_count": summary.get(
            "no_forbidden_code_patch_application_claims_count"
        ),
        "code_patch_execution_inputs_satisfied_count": summary.get(
            "code_patch_execution_inputs_satisfied_count"
        ),
        "code_patch_execution_record_present_count": summary.get(
            "code_patch_execution_record_present_count"
        ),
        "record_schema_matches_count": summary.get("record_schema_matches_count"),
        "code_patch_execution_scope_matches_count": summary.get(
            "code_patch_execution_scope_matches_count"
        ),
        "explicit_code_patch_execution_authorized_count": summary.get(
            "explicit_code_patch_execution_authorized_count"
        ),
        "execution_status_passed_count": summary.get("execution_status_passed_count"),
        "no_save_delete_rename_acknowledged_count": summary.get(
            "no_save_delete_rename_acknowledged_count"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": summary.get(
            "explicit_durable_mvp_request_reconfirmed_count"
        ),
        "allowed_code_patch_execution_observed_count": summary.get(
            "allowed_code_patch_execution_observed_count"
        ),
        "no_forbidden_code_patch_execution_claims_count": summary.get(
            "no_forbidden_code_patch_execution_claims_count"
        ),
        "code_patch_execution_record_valid_count": summary.get(
            "code_patch_execution_record_valid_count"
        ),
        "code_patch_execution_record_rejected_count": summary.get(
            "code_patch_execution_record_rejected_count"
        ),
        "unsafe_code_patch_execution_record_count": summary.get(
            "unsafe_code_patch_execution_record_count"
        ),
        "missing_code_patch_execution_prerequisite_count": summary.get(
            "missing_code_patch_execution_prerequisite_count"
        ),
        "reported_allowed_code_patch_execution_count": summary.get(
            "reported_allowed_code_patch_execution_count"
        ),
        "reported_forbidden_code_patch_execution_count": summary.get(
            "reported_forbidden_code_patch_execution_count"
        ),
        "durable_executor_code_patch_execution_started_count": summary.get(
            "durable_executor_code_patch_execution_started_count"
        ),
        "durable_executor_code_patch_execution_accepted_count": summary.get(
            "durable_executor_code_patch_execution_accepted_count"
        ),
        "durable_executor_code_patch_result_started_count": summary.get(
            "durable_executor_code_patch_result_started_count"
        ),
        "code_change_performed_count": summary.get("code_change_performed_count"),
        "executor_code_modified_count": summary.get("executor_code_modified_count"),
        "unreal_asset_modified_count": summary.get("unreal_asset_modified_count"),
        "live_bridge_probe_started_count": summary.get("live_bridge_probe_started_count"),
        "durable_authoring_enabled_count": summary.get("durable_authoring_enabled_count"),
        "durable_authoring_allowed_count": summary.get("durable_authoring_allowed_count"),
        "asset_write_performed_count": summary.get("asset_write_performed_count"),
        "package_dirty_marked_count": summary.get("package_dirty_marked_count"),
        "save_delete_rename_allowed_count": summary.get("save_delete_rename_allowed_count"),
        "cleanup_allowed_count": summary.get("cleanup_allowed_count"),
        "live_command_dispatched_count": summary.get("live_command_dispatched_count"),
        "live_command_executed_count": summary.get("live_command_executed_count"),
    }
    return row(
        "durable_executor_code_patch_execution_contract",
        "Section 102 durable executor code patch execution contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The code patch execution contract is defined, but no execution record is present.",
            "Code patch result admission, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_code_patch_result_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    execution_row = build_durable_executor_code_patch_execution_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    execution_summary = dict(execution_row["actual"])
    execution_summary["status"] = execution_summary.pop("summary_status")
    contract = code_patch_result.build_durable_executor_code_patch_result_contract(
        requested=True,
        code_patch_execution_summary=execution_summary,
    )
    summary = code_patch_result.summarize_durable_executor_code_patch_results(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_code_patch_result_count": 1,
        "code_patch_result_contract_defined_count": 1,
        "code_patch_execution_contract_ready_count": 1,
        "code_patch_execution_inputs_satisfied_count": 0,
        "code_patch_execution_record_valid_count": 0,
        "allowed_code_patch_execution_observed_count": 0,
        "no_forbidden_code_patch_execution_claims_count": 0,
        "code_patch_result_inputs_satisfied_count": 0,
        "code_patch_result_record_present_count": 0,
        "record_schema_matches_count": 0,
        "code_patch_result_scope_matches_count": 0,
        "explicit_code_patch_result_authorized_count": 0,
        "result_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_code_patch_result_observed_count": 0,
        "no_forbidden_code_patch_result_claims_count": 0,
        "code_patch_result_record_valid_count": 0,
        "code_patch_result_record_rejected_count": 0,
        "unsafe_code_patch_result_record_count": 0,
        "missing_code_patch_result_prerequisite_count": 14,
        "reported_allowed_code_patch_result_count": 0,
        "reported_forbidden_code_patch_result_count": 0,
        "durable_executor_code_patch_result_started_count": 0,
        "durable_executor_code_patch_result_accepted_count": 0,
        "durable_executor_code_patch_result_readback_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_code_patch_result_contract",
        "Section 103 durable executor code patch result contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The code patch result contract is defined, but no result record is present.",
            "Code patch result readback, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_code_patch_result_readback_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    result_row = build_durable_executor_code_patch_result_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    result_summary = dict(result_row["actual"])
    result_summary["status"] = result_summary.pop("summary_status")
    contract = code_patch_result_readback.build_durable_executor_code_patch_result_readback_contract(
        requested=True,
        code_patch_result_summary=result_summary,
    )
    summary = code_patch_result_readback.summarize_durable_executor_code_patch_result_readbacks(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_code_patch_result_readback_count": 1,
        "code_patch_result_readback_contract_defined_count": 1,
        "code_patch_result_contract_ready_count": 1,
        "code_patch_result_inputs_satisfied_count": 0,
        "code_patch_result_record_valid_count": 0,
        "allowed_code_patch_result_observed_count": 0,
        "no_forbidden_code_patch_result_claims_count": 0,
        "code_patch_result_readback_inputs_satisfied_count": 0,
        "code_patch_result_readback_record_present_count": 0,
        "record_schema_matches_count": 0,
        "code_patch_result_readback_scope_matches_count": 0,
        "explicit_code_patch_result_readback_authorized_count": 0,
        "readback_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_code_patch_result_readback_observed_count": 0,
        "no_forbidden_code_patch_result_readback_claims_count": 0,
        "code_patch_result_readback_record_valid_count": 0,
        "code_patch_result_readback_record_rejected_count": 0,
        "unsafe_code_patch_result_readback_record_count": 0,
        "missing_code_patch_result_readback_prerequisite_count": 14,
        "reported_allowed_code_patch_result_readback_count": 0,
        "reported_forbidden_code_patch_result_readback_count": 0,
        "durable_executor_code_patch_result_readback_started_count": 0,
        "durable_executor_code_patch_result_readback_accepted_count": 0,
        "durable_executor_code_patch_final_no_save_release_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_code_patch_result_readback_contract",
        "Section 104 durable executor code patch result readback contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The code patch result readback contract is defined, but no readback record is present.",
            "Final no-save release, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_code_patch_final_no_save_release_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readback_row = build_durable_executor_code_patch_result_readback_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    readback_summary = dict(readback_row["actual"])
    readback_summary["status"] = readback_summary.pop("summary_status")
    contract = code_patch_final_no_save_release.build_durable_executor_code_patch_final_no_save_release_contract(
        requested=True,
        code_patch_result_readback_summary=readback_summary,
    )
    summary = code_patch_final_no_save_release.summarize_durable_executor_code_patch_final_no_save_releases(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_code_patch_final_no_save_release_count": 1,
        "code_patch_final_no_save_release_contract_defined_count": 1,
        "code_patch_result_readback_contract_ready_count": 1,
        "code_patch_result_readback_inputs_satisfied_count": 0,
        "code_patch_result_readback_record_valid_count": 0,
        "allowed_code_patch_result_readback_observed_count": 0,
        "no_forbidden_code_patch_result_readback_claims_count": 0,
        "code_patch_final_no_save_release_inputs_satisfied_count": 0,
        "code_patch_final_no_save_release_record_present_count": 0,
        "record_schema_matches_count": 0,
        "code_patch_final_no_save_release_scope_matches_count": 0,
        "explicit_code_patch_final_no_save_release_authorized_count": 0,
        "final_no_save_release_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_code_patch_final_no_save_release_observed_count": 0,
        "no_forbidden_code_patch_final_no_save_release_claims_count": 0,
        "code_patch_final_no_save_release_record_valid_count": 0,
        "code_patch_final_no_save_release_record_rejected_count": 0,
        "unsafe_code_patch_final_no_save_release_record_count": 0,
        "missing_code_patch_final_no_save_release_prerequisite_count": 14,
        "reported_allowed_code_patch_final_no_save_release_count": 0,
        "reported_forbidden_code_patch_final_no_save_release_count": 0,
        "durable_executor_code_patch_final_no_save_release_started_count": 0,
        "durable_executor_code_patch_final_no_save_release_accepted_count": 0,
        "durable_executor_code_patch_final_release_readiness_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_code_patch_final_no_save_release_contract",
        "Section 105 durable executor code patch final no-save release contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The code patch final no-save release contract is defined, but no final release record is present.",
            "Final release readiness, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_code_patch_final_release_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    final_no_save_release_row = build_durable_executor_code_patch_final_no_save_release_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    final_no_save_release_summary = dict(final_no_save_release_row["actual"])
    final_no_save_release_summary["status"] = final_no_save_release_summary.pop(
        "summary_status"
    )
    contract = code_patch_final_release_readiness.build_durable_executor_code_patch_final_release_readiness_contract(
        requested=True,
        code_patch_final_no_save_release_summary=final_no_save_release_summary,
    )
    summary = code_patch_final_release_readiness.summarize_durable_executor_code_patch_final_release_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_code_patch_final_release_readiness_count": 1,
        "code_patch_final_release_readiness_contract_defined_count": 1,
        "code_patch_final_no_save_release_contract_ready_count": 1,
        "code_patch_final_no_save_release_inputs_satisfied_count": 0,
        "code_patch_final_no_save_release_record_valid_count": 0,
        "allowed_code_patch_final_no_save_release_observed_count": 0,
        "no_forbidden_code_patch_final_no_save_release_claims_count": 0,
        "code_patch_final_release_readiness_inputs_satisfied_count": 0,
        "code_patch_final_release_readiness_record_present_count": 0,
        "record_schema_matches_count": 0,
        "code_patch_final_release_readiness_scope_matches_count": 0,
        "explicit_code_patch_final_release_readiness_authorized_count": 0,
        "readiness_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_code_patch_final_release_readiness_observed_count": 0,
        "no_forbidden_code_patch_final_release_readiness_claims_count": 0,
        "code_patch_final_release_readiness_record_valid_count": 0,
        "code_patch_final_release_readiness_record_rejected_count": 0,
        "unsafe_code_patch_final_release_readiness_record_count": 0,
        "missing_code_patch_final_release_readiness_prerequisite_count": 14,
        "reported_allowed_code_patch_final_release_readiness_count": 0,
        "reported_forbidden_code_patch_final_release_readiness_count": 0,
        "durable_executor_code_patch_final_release_readiness_started_count": 0,
        "durable_executor_code_patch_final_release_ready_count": 0,
        "durable_executor_code_patch_release_review_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_code_patch_final_release_readiness_contract",
        "Section 106 durable executor code patch final release readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The code patch final release readiness contract is defined, but no readiness record is present.",
            "Release review, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_code_patch_release_review_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readiness_row = build_durable_executor_code_patch_final_release_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    readiness_summary = dict(readiness_row["actual"])
    readiness_summary["status"] = readiness_summary.pop("summary_status")
    contract = code_patch_release_review.build_durable_executor_code_patch_release_review_contract(
        requested=True,
        code_patch_final_release_readiness_summary=readiness_summary,
    )
    summary = code_patch_release_review.summarize_durable_executor_code_patch_release_reviews(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_code_patch_release_review_count": 1,
        "code_patch_release_review_contract_defined_count": 1,
        "code_patch_final_release_readiness_contract_ready_count": 1,
        "code_patch_final_release_readiness_inputs_satisfied_count": 0,
        "code_patch_final_release_readiness_record_valid_count": 0,
        "allowed_code_patch_final_release_readiness_observed_count": 0,
        "no_forbidden_code_patch_final_release_readiness_claims_count": 0,
        "code_patch_release_review_inputs_satisfied_count": 0,
        "code_patch_release_review_record_present_count": 0,
        "record_schema_matches_count": 0,
        "code_patch_release_review_scope_matches_count": 0,
        "explicit_code_patch_release_review_authorized_count": 0,
        "release_review_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_code_patch_release_review_observed_count": 0,
        "no_forbidden_code_patch_release_review_claims_count": 0,
        "code_patch_release_review_record_valid_count": 0,
        "code_patch_release_review_record_rejected_count": 0,
        "unsafe_code_patch_release_review_record_count": 0,
        "missing_code_patch_release_review_prerequisite_count": 14,
        "reported_allowed_code_patch_release_review_count": 0,
        "reported_forbidden_code_patch_release_review_count": 0,
        "durable_executor_code_patch_release_review_started_count": 0,
        "durable_executor_code_patch_release_review_accepted_count": 0,
        "durable_executor_code_patch_release_decision_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_code_patch_release_review_contract",
        "Section 107 durable executor code patch release review contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The code patch release review contract is defined, but no release review record is present.",
            "Release decision, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_code_patch_release_decision_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    release_review_row = build_durable_executor_code_patch_release_review_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    release_review_summary = dict(release_review_row["actual"])
    release_review_summary["status"] = release_review_summary.pop("summary_status")
    contract = code_patch_release_decision.build_durable_executor_code_patch_release_decision_contract(
        requested=True,
        code_patch_release_review_summary=release_review_summary,
    )
    summary = code_patch_release_decision.summarize_durable_executor_code_patch_release_decisions(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_code_patch_release_decision_count": 1,
        "code_patch_release_decision_contract_defined_count": 1,
        "code_patch_release_review_contract_ready_count": 1,
        "code_patch_release_review_inputs_satisfied_count": 0,
        "code_patch_release_review_record_valid_count": 0,
        "allowed_code_patch_release_review_observed_count": 0,
        "no_forbidden_code_patch_release_review_claims_count": 0,
        "code_patch_release_decision_inputs_satisfied_count": 0,
        "code_patch_release_decision_record_present_count": 0,
        "record_schema_matches_count": 0,
        "code_patch_release_decision_scope_matches_count": 0,
        "explicit_code_patch_release_decision_authorized_count": 0,
        "release_decision_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_code_patch_release_decision_observed_count": 0,
        "no_forbidden_code_patch_release_decision_claims_count": 0,
        "code_patch_release_decision_record_valid_count": 0,
        "code_patch_release_decision_record_rejected_count": 0,
        "unsafe_code_patch_release_decision_record_count": 0,
        "missing_code_patch_release_decision_prerequisite_count": 14,
        "reported_allowed_code_patch_release_decision_count": 0,
        "reported_forbidden_code_patch_release_decision_count": 0,
        "durable_executor_code_patch_release_decision_started_count": 0,
        "durable_executor_code_patch_release_decision_accepted_count": 0,
        "durable_executor_release_promotion_barrier_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_code_patch_release_decision_contract",
        "Section 108 durable executor code patch release decision contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The code patch release decision contract is defined, but no release decision record is present.",
            "Promotion barrier, code edits, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_release_promotion_barrier_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    release_decision_row = build_durable_executor_code_patch_release_decision_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    release_decision_summary = dict(release_decision_row["actual"])
    release_decision_summary["status"] = release_decision_summary.pop(
        "summary_status"
    )
    contract = release_promotion_barrier.build_durable_executor_release_promotion_barrier_contract(
        requested=True,
        code_patch_release_decision_summary=release_decision_summary,
    )
    summary = release_promotion_barrier.summarize_durable_executor_release_promotion_barriers(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_release_promotion_barrier_count": 1,
        "release_promotion_barrier_contract_defined_count": 1,
        "code_patch_release_decision_contract_ready_count": 1,
        "code_patch_release_decision_inputs_satisfied_count": 0,
        "code_patch_release_decision_record_valid_count": 0,
        "allowed_code_patch_release_decision_observed_count": 0,
        "no_forbidden_code_patch_release_decision_claims_count": 0,
        "release_promotion_barrier_inputs_satisfied_count": 0,
        "release_promotion_barrier_record_present_count": 0,
        "record_schema_matches_count": 0,
        "release_promotion_barrier_scope_matches_count": 0,
        "explicit_release_promotion_barrier_authorized_count": 0,
        "promotion_barrier_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_release_promotion_barrier_observed_count": 0,
        "no_forbidden_release_promotion_barrier_claims_count": 0,
        "release_promotion_barrier_record_valid_count": 0,
        "release_promotion_barrier_record_rejected_count": 0,
        "unsafe_release_promotion_barrier_record_count": 0,
        "missing_release_promotion_barrier_prerequisite_count": 14,
        "reported_allowed_release_promotion_barrier_count": 0,
        "reported_forbidden_release_promotion_barrier_count": 0,
        "durable_executor_release_promotion_barrier_started_count": 0,
        "durable_executor_release_promotion_barrier_accepted_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_release_promotion_barrier_contract",
        "Section 109 durable executor release promotion barrier contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor release promotion barrier is defined, but no barrier record is present.",
            "Activation readiness, executor open, live probes, asset changes, and durable authoring remain blocked.",
        ),
    )


def build_durable_executor_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    promotion_barrier_row = build_durable_executor_release_promotion_barrier_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    promotion_barrier_summary = dict(promotion_barrier_row["actual"])
    promotion_barrier_summary["status"] = promotion_barrier_summary.pop(
        "summary_status"
    )
    contract = activation_readiness.build_durable_executor_activation_readiness_contract(
        requested=True,
        release_promotion_barrier_summary=promotion_barrier_summary,
    )
    summary = activation_readiness.summarize_durable_executor_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_activation_readiness_count": 1,
        "activation_readiness_contract_defined_count": 1,
        "release_promotion_barrier_contract_ready_count": 1,
        "release_promotion_barrier_inputs_satisfied_count": 0,
        "release_promotion_barrier_record_valid_count": 0,
        "allowed_release_promotion_barrier_observed_count": 0,
        "no_forbidden_release_promotion_barrier_claims_count": 0,
        "activation_readiness_inputs_satisfied_count": 0,
        "activation_readiness_record_present_count": 0,
        "record_schema_matches_count": 0,
        "activation_readiness_scope_matches_count": 0,
        "explicit_activation_readiness_authorized_count": 0,
        "activation_readiness_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_activation_readiness_observed_count": 0,
        "no_forbidden_activation_readiness_claims_count": 0,
        "activation_readiness_record_valid_count": 0,
        "activation_readiness_record_rejected_count": 0,
        "unsafe_activation_readiness_record_count": 0,
        "missing_activation_readiness_prerequisite_count": 14,
        "reported_allowed_activation_readiness_count": 0,
        "reported_forbidden_activation_readiness_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_executor_open_contract_started_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_activation_readiness_contract",
        "Section 110 durable executor activation readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor activation readiness contract is defined, but no readiness record is present.",
            "Executor open, live probes, asset changes, durable authoring, save, delete/rename, and cleanup remain blocked.",
        ),
    )


def build_durable_executor_open_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    activation_readiness_row = build_durable_executor_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    activation_readiness_summary = dict(activation_readiness_row["actual"])
    activation_readiness_summary["status"] = activation_readiness_summary.pop(
        "summary_status"
    )
    contract = durable_executor_open.build_durable_executor_open_contract(
        requested=True,
        activation_readiness_summary=activation_readiness_summary,
    )
    summary = durable_executor_open.summarize_durable_executor_opens([contract])
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_open_count": 1,
        "open_contract_defined_count": 1,
        "activation_readiness_contract_ready_count": 1,
        "activation_readiness_inputs_satisfied_count": 0,
        "activation_readiness_record_valid_count": 0,
        "allowed_activation_readiness_observed_count": 0,
        "no_forbidden_activation_readiness_claims_count": 0,
        "open_inputs_satisfied_count": 0,
        "open_record_present_count": 0,
        "record_schema_matches_count": 0,
        "open_scope_matches_count": 0,
        "explicit_open_authorized_count": 0,
        "open_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_open_observed_count": 0,
        "no_forbidden_open_claims_count": 0,
        "open_record_valid_count": 0,
        "open_record_rejected_count": 0,
        "unsafe_open_record_count": 0,
        "missing_open_prerequisite_count": 14,
        "reported_allowed_open_count": 0,
        "reported_forbidden_open_count": 0,
        "durable_executor_open_contract_started_count": 0,
        "durable_executor_open_contract_accepted_count": 0,
        "durable_executor_open_performed_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "durable_authoring_enable_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_open_contract",
        "Section 111 durable executor open contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor open contract is defined, but no open record is present.",
            "Executor open, durable authoring enablement, live probes, asset changes, save, delete/rename, and cleanup remain blocked.",
        ),
    )


def build_durable_executor_authoring_enable_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    executor_open_row = build_durable_executor_open_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    open_summary = dict(executor_open_row["actual"])
    open_summary["status"] = open_summary.pop("summary_status")
    contract = durable_executor_authoring_enable.build_durable_executor_authoring_enable_contract(
        requested=True,
        open_summary=open_summary,
    )
    summary = durable_executor_authoring_enable.summarize_durable_executor_authoring_enables(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_enable_count": 1,
        "authoring_enable_contract_defined_count": 1,
        "executor_open_contract_ready_count": 1,
        "open_inputs_satisfied_count": 0,
        "open_record_valid_count": 0,
        "allowed_open_observed_count": 0,
        "no_forbidden_open_claims_count": 0,
        "authoring_enable_inputs_satisfied_count": 0,
        "authoring_enable_record_present_count": 0,
        "record_schema_matches_count": 0,
        "enable_scope_matches_count": 0,
        "explicit_authoring_enable_authorized_count": 0,
        "authoring_enable_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "target_package_allowlist_reconfirmed_count": 0,
        "overwrite_rename_decision_reconfirmed_count": 0,
        "rollback_readiness_reconfirmed_count": 0,
        "ownership_marker_reconfirmed_count": 0,
        "allowed_authoring_enable_observed_count": 0,
        "no_forbidden_authoring_enable_claims_count": 0,
        "authoring_enable_record_valid_count": 0,
        "authoring_enable_record_rejected_count": 0,
        "unsafe_authoring_enable_record_count": 0,
        "missing_authoring_enable_prerequisite_count": 18,
        "reported_allowed_authoring_enable_count": 0,
        "reported_forbidden_authoring_enable_count": 0,
        "durable_authoring_enable_started_count": 0,
        "durable_authoring_enable_accepted_count": 0,
        "durable_authoring_enable_allowed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "durable_authoring_command_contract_started_count": 0,
        "durable_executor_open_performed_count": 0,
        "durable_executor_opened_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_enable_contract",
        "Section 112 durable executor authoring enable contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring enable contract is defined, but no enable record is present.",
            "Target allowlist, overwrite/rename, rollback readiness, and ownership marker gates are explicit prerequisites before commands.",
            "Durable authoring, live probes, asset changes, save, delete/rename, and cleanup remain blocked.",
        ),
    )


def build_section_51_58_consolidation_row(
    contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]
) -> Dict[str, Any]:
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "durable_authoring_enabled": False,
        "durable_enable_satisfied_count": 0,
        "durable_executor_may_open_count": 0,
        "durable_save_allowed_count": 0,
        "durable_canary_executor_may_open_count": 0,
        "durable_canary_live_execution_allowed_count": 0,
        "durable_canary_recovery_cleanup_allowed_count": 0,
        "durable_gate_status": "passed",
        "section_51_58_blocking_contracts_ready": True,
    }
    actual = {
        "durable_authoring_enabled": False,
        "durable_enable_satisfied_count": contract_summary.get("durable_enable_contract_satisfied_count"),
        "durable_executor_may_open_count": contract_summary.get("durable_enable_executor_may_open_count"),
        "durable_save_allowed_count": contract_summary.get("durable_save_allowed_count"),
        "durable_canary_executor_may_open_count": contract_summary.get("durable_canary_executor_may_open_count"),
        "durable_canary_live_execution_allowed_count": contract_summary.get(
            "durable_canary_approval_live_execution_allowed_count"
        ),
        "durable_canary_recovery_cleanup_allowed_count": contract_summary.get(
            "durable_canary_recovery_cleanup_command_allowed_count"
        ),
        "durable_gate_status": durable_gate_summary.get("status"),
        "section_51_58_blocking_contracts_ready": all(
            contract_summary.get(key, {}).get("status") == "passed"
            for key in (
                "durable_enable_contract_summary",
                "durable_dry_run_plan_summary",
                "durable_save_simulation_summary",
                "durable_canary_prep_summary",
                "durable_canary_approval_summary",
                "durable_canary_live_preflight_summary",
                "durable_canary_recovery_summary",
            )
        ),
    }
    return row(
        "section_51_58_release_boundary_v2_consolidation",
        "Section 59 release boundary v2 consolidation",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Section 51-58 contracts are present and blocking-safe.",
            "Durable authoring remains disabled; only read-only preflight evidence is allowed.",
        ),
    )


def build_mvp_decision_row(decision_contract: Dict[str, Any]) -> Dict[str, Any]:
    expected = {
        "schema": mvp_decision.MVP_DECISION_SCHEMA,
        "decision_status": "temporary_mvp_ready_durable_not_enabled",
        "temporary_blueprint_authoring_mvp_ready": True,
        "durable_blueprint_authoring_mvp_ready": False,
        "durable_authoring_enabled": False,
        "durable_save_allowed": False,
        "durable_cleanup_allowed": False,
        "durable_canary_live_execution_allowed": False,
    }
    actual = {key: decision_contract.get(key) for key in expected}
    return row(
        "section_60_mvp_decision_contract",
        "Section 60 MVP decision contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Temporary planner-safe Blueprint authoring is the MVP-ready scope.",
            "Durable Blueprint authoring remains contracts-only and disabled.",
        ),
    )


def build_planner_live_rows(planner_report_path: Path, planner_report: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if planner_report is None:
        return [missing_row("planner_driven_live_smoke_report", "Planner-driven live smoke report", planner_report_path)]
    verdict = planner_report.get("verdict", {})
    live_gate = planner_report.get("live_gate", {})
    preflight_gate = live_gate.get("durable_live_preflight_gate", {})
    canary_preflight_gate = live_gate.get("durable_canary_live_preflight_gate", {})
    smoke_expected = {
        "verdict_status": "passed",
        "safe_requests_queued": 12,
        "non_safe_requests_prevented": 7,
        "executor_executable_manifests": 12,
    }
    smoke_actual = {
        "verdict_status": verdict.get("status"),
        "safe_requests_queued": verdict.get("safe_requests_queued"),
        "non_safe_requests_prevented": verdict.get("non_safe_requests_prevented"),
        "executor_executable_manifests": verdict.get("executor_executable_manifests"),
    }
    cleanup_expected = {
        "generated_leftovers": 0,
        "new_log_errors": 0,
        "durable_authoring_attempted": False,
        "durable_live_save_or_delete_attempted": False,
        "durable_canary_execution_attempted": False,
        "durable_canary_cleanup_attempted": False,
    }
    cleanup_actual = {
        "generated_leftovers": len(live_gate.get("generated_leftovers", [])),
        "new_log_errors": len(live_gate.get("new_log_errors", [])),
        "durable_authoring_attempted": live_gate.get("durable_authoring_attempted"),
        "durable_live_save_or_delete_attempted": live_gate.get("durable_live_save_or_delete_attempted"),
        "durable_canary_execution_attempted": bool(live_gate.get("durable_canary_execution_attempted")),
        "durable_canary_cleanup_attempted": bool(live_gate.get("durable_canary_cleanup_attempted")),
    }
    preflight_expected = {
        "status": "passed",
        "live_result_count": 1,
        "passed_read_only_result_count": 1,
        "authoring_attempted_count": 0,
        "save_or_delete_attempted_count": 0,
        "preflight_pass_count": 0,
    }
    preflight_actual = {key: preflight_gate.get(key) for key in preflight_expected}
    canary_preflight_expected = {
        "status": "passed",
        "live_result_count": 1,
        "passed_read_only_result_count": 1,
        "authoring_attempted_count": 0,
        "save_or_delete_attempted_count": 0,
        "cleanup_attempted_count": 0,
        "canary_execution_attempted_count": 0,
        "canary_execution_allowed_after_preflight_count": 0,
        "read_only_only": True,
    }
    canary_preflight_actual = {key: canary_preflight_gate.get(key) for key in canary_preflight_expected}
    return [
        row(
            "planner_driven_live_smoke_report",
            "Planner-driven live smoke report",
            passed=smoke_actual == smoke_expected,
            expected=smoke_expected,
            actual=smoke_actual,
        ),
        row(
            "planner_live_cleanup_and_log_boundary",
            "Planner live cleanup and log boundary",
            passed=cleanup_actual == cleanup_expected,
            expected=cleanup_expected,
            actual=cleanup_actual,
        ),
        row(
            "durable_read_only_live_preflight",
            "Durable read-only live preflight boundary",
            passed=preflight_actual == preflight_expected,
            expected=preflight_expected,
            actual=preflight_actual,
        ),
        row(
            "durable_canary_read_only_live_preflight",
            "Durable canary read-only live preflight boundary",
            passed=canary_preflight_actual == canary_preflight_expected,
            expected=canary_preflight_expected,
            actual=canary_preflight_actual,
            blocking=False,
            notes=(
                "Section 57 contract is blocking in offline release rows.",
                "This live row becomes passed after the next reachable UnrealMCP read-only canary preflight run.",
            ),
        ),
    ]


def build_quality_gate_row(quality_report_path: Path, quality_report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if quality_report is None:
        return missing_row("bp_authoring_quality_gate_live_report", "BP authoring quality gate live report", quality_report_path)
    expected = {
        "verdict_status": "existing_bp_authoring_quality_gate_passed",
        "live_status": "passed",
        "cxx_changes_required_for_this_gate": False,
    }
    actual = {
        "verdict_status": quality_report.get("verdict", {}).get("status"),
        "live_status": quality_report.get("live_gate", {}).get("status"),
        "cxx_changes_required_for_this_gate": quality_report.get("verdict", {}).get(
            "cxx_changes_required_for_this_gate"
        ),
    }
    return row(
        "bp_authoring_quality_gate_live_report",
        "BP authoring quality gate live report",
        passed=actual == expected,
        expected=expected,
        actual=actual,
    )


def build_lyra_boundary_row(lyra_report_path: Path, lyra_report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if lyra_report is None:
        return missing_row("lyra_readiness_boundary", "Lyra readiness boundary report", lyra_report_path)
    verdict = lyra_report.get("verdict", {})
    ceiling = verdict.get("current_authoring_ceiling", "")
    not_ready_for = verdict.get("not_ready_for", [])
    actual = {
        "minimum_stable_scope": verdict.get("minimum_stable_scope"),
        "ceiling_mentions_temporary_smoke": "temporary_smoke_only" in ceiling,
        "editor_open_required_now": verdict.get("editor_open_required_now"),
        "not_ready_for_count": len(not_ready_for),
    }
    expected = {
        "minimum_stable_scope": "readiness_classification_and_candidate_selection",
        "ceiling_mentions_temporary_smoke": True,
        "editor_open_required_now": False,
        "not_ready_for_count_at_least": 1,
    }
    passed = (
        actual["minimum_stable_scope"] == expected["minimum_stable_scope"]
        and actual["ceiling_mentions_temporary_smoke"] is True
        and actual["editor_open_required_now"] is False
        and actual["not_ready_for_count"] >= expected["not_ready_for_count_at_least"]
    )
    return row(
        "lyra_readiness_boundary",
        "Lyra readiness and authoring ceiling boundary",
        passed=passed,
        expected=expected,
        actual=actual,
    )


def collect_project_filesystem_boundary(project_root: Path) -> Dict[str, Any]:
    temp_root = project_root / "Content" / "_MCP_Temp" / "PlannerDrivenSmoke"
    generated_leftovers = []
    if temp_root.exists():
        generated_leftovers = [str(path) for path in temp_root.rglob("*") if "MCP_PlannerSmoke_" in path.name]
    durable_asset = project_root / "Content" / "MCPTestFixtures" / "BP_PlannerDurable.uasset"
    actual = {
        "project_root_exists": project_root.exists(),
        "generated_planner_smoke_leftovers": len(generated_leftovers),
        "durable_test_asset_exists": durable_asset.exists(),
    }
    expected = {
        "project_root_exists": True,
        "generated_planner_smoke_leftovers": 0,
        "durable_test_asset_exists": False,
    }
    return row(
        "project_filesystem_side_effect_boundary",
        "Project filesystem side-effect boundary",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=generated_leftovers[:5],
    )


def build_report(repo_root: Optional[Path] = None, project_root: Optional[Path] = None) -> Dict[str, Any]:
    repo_root = repo_root or repo_root_from_script()
    project_root = project_root or repo_root.parent / "CubelessStylized"
    reports_root = repo_root / "Docs" / "Analysis"
    planner_report_path = reports_root / "PlannerDrivenSmoke" / "planner_driven_bp_authoring_smoke_report.json"
    quality_report_path = reports_root / "BPAuthoringQualityGate" / "bp_authoring_quality_gate_report.json"
    lyra_report_path = reports_root / "Lyra" / "lyra_combined_readiness_report.json"

    manifests = default_manifests()
    contract_summary = job_contract.summarize_manifests(manifests)
    executor_summary = manifest_executor.summarize_executor_policies(manifests, job_contract.DEFAULT_TEMP_PACKAGE_PATH)
    planner_report = read_json(planner_report_path)
    quality_report = read_json(quality_report_path)
    lyra_report = read_json(lyra_report_path)
    preliminary_verdict = {
        "status": "passed",
        "release_boundary_version": "section_112_v54",
        "durable_authoring_enabled": False,
    }
    decision_contract = mvp_decision.build_mvp_decision_contract(
        contract_summary,
        executor_summary,
        preliminary_verdict,
    )
    safety_rows = [
        build_durable_canary_bridge_refresh_row(contract_summary, executor_summary),
        build_live_evidence_refresh_row(planner_report),
        build_executor_review_row(executor_summary),
        build_canary_command_allowlist_row(executor_summary),
        build_canary_creation_boundary_row(contract_summary, executor_summary),
        build_ownership_marker_proof_row(contract_summary),
        build_rollback_cleanup_proof_row(contract_summary),
        build_save_gate_final_review_row(contract_summary, executor_summary),
        build_canary_rehearsal_readiness_row(contract_summary, executor_summary, planner_report),
    ]
    safety_contract_statuses = [item["status"] for item in safety_rows]

    matrix = [
        build_contract_matrix_row(contract_summary),
        build_executor_matrix_row(executor_summary),
        build_capability_matrix_row(executor_summary),
        build_durable_gate_matrix_row(executor_summary),
        build_durable_enable_contract_row(contract_summary, executor_summary),
        build_durable_ownership_marker_row(contract_summary, executor_summary),
        build_durable_dry_run_plan_row(contract_summary, executor_summary),
        build_durable_save_simulator_row(contract_summary, executor_summary),
        build_durable_canary_prep_row(contract_summary, executor_summary),
        build_durable_canary_approval_row(contract_summary, executor_summary),
        build_durable_canary_live_preflight_row(contract_summary, executor_summary),
        *safety_rows,
        build_durable_canary_recovery_row(contract_summary, executor_summary),
        build_section_51_58_consolidation_row(contract_summary, executor_summary),
        build_mvp_decision_row(decision_contract),
        build_durable_release_decision_row(decision_contract, executor_summary, safety_contract_statuses),
        build_bridge_recovery_readiness_row(project_root),
        build_canary_read_only_retry_envelope_row(contract_summary, executor_summary, project_root),
        build_canary_read_only_retry_result_admission_row(contract_summary, executor_summary, project_root),
        build_canary_rehearsal_promotion_barrier_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_rehearsal_execution_release_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_live_runner_envelope_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_live_runner_start_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_live_command_dispatch_release_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_live_command_execution_release_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_live_command_execution_evidence_admission_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_release_promotion_decision_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_executor_activation_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_executor_open_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_authoring_enable_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_authoring_command_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_authoring_command_dispatch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_authoring_command_execution_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_authoring_command_execution_evidence_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_authoring_command_completion_decision_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_authoring_command_completion_application_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_authoring_command_completion_result_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_authoring_command_result_readback_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_authoring_final_no_save_release_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_canary_authoring_final_release_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_implementation_review_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_implementation_plan_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_change_design_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_code_change_approval_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_code_patch_plan_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_code_patch_review_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_code_patch_application_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_code_patch_execution_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_code_patch_result_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_code_patch_result_readback_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_code_patch_final_no_save_release_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_code_patch_final_release_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_code_patch_release_review_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_code_patch_release_decision_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_release_promotion_barrier_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_open_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_enable_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        *build_planner_live_rows(planner_report_path, planner_report),
        build_quality_gate_row(quality_report_path, quality_report),
        build_lyra_boundary_row(lyra_report_path, lyra_report),
        collect_project_filesystem_boundary(project_root),
    ]
    failed_blocking = [item for item in matrix if item["blocking"] and item["status"] != "passed"]
    return {
        "schema": REPORT_SCHEMA,
        "analysis_kind": ANALYSIS_KIND,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "project_root": str(project_root),
        "report_inputs": {
            "planner_driven_smoke": str(planner_report_path),
            "bp_authoring_quality_gate": str(quality_report_path),
            "lyra_combined_readiness": str(lyra_report_path),
        },
        "regression_matrix": matrix,
        "verdict": {
            "status": "passed" if not failed_blocking else "failed",
            "release_boundary_version": "section_112_v54",
            "mvp_decision_status": decision_contract["decision_status"],
            "temporary_blueprint_authoring_mvp_ready": decision_contract[
                "temporary_blueprint_authoring_mvp_ready"
            ],
            "durable_blueprint_authoring_mvp_ready": decision_contract["durable_blueprint_authoring_mvp_ready"],
            "failed_blocking_count": len(failed_blocking),
            "failed_blocking_ids": [item["id"] for item in failed_blocking],
            "ready_for_main_push": not failed_blocking,
            "durable_authoring_enabled": False,
            "durable_authoring_release_status": "section_70_not_enabled_contracts_only",
            "section_51_58_contract_status": "passed" if not failed_blocking else "failed",
            "section_61_bridge_refresh_status": "passed" if not failed_blocking else "failed",
            "section_62_live_evidence_refresh_status": "passed" if not failed_blocking else "failed",
            "section_63_executor_review_status": "passed" if not failed_blocking else "failed",
            "section_64_canary_command_allowlist_status": "passed" if not failed_blocking else "failed",
            "section_65_canary_creation_boundary_status": "passed" if not failed_blocking else "failed",
            "section_66_ownership_marker_proof_status": "passed" if not failed_blocking else "failed",
            "section_67_rollback_cleanup_proof_status": "passed" if not failed_blocking else "failed",
            "section_68_save_gate_final_review_status": "passed" if not failed_blocking else "failed",
            "section_69_canary_rehearsal_readiness_status": "passed" if not failed_blocking else "failed",
            "section_70_durable_release_decision_status": "passed" if not failed_blocking else "failed",
            "section_71_bridge_recovery_readiness_status": "passed" if not failed_blocking else "failed",
            "section_72_canary_read_only_retry_envelope_status": "passed" if not failed_blocking else "failed",
            "section_73_canary_read_only_retry_result_admission_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_74_canary_rehearsal_promotion_barrier_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_75_canary_rehearsal_execution_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_76_canary_live_runner_envelope_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_77_canary_live_runner_start_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_78_canary_live_command_dispatch_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_79_canary_live_command_execution_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_80_canary_live_command_execution_evidence_admission_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_81_canary_release_promotion_decision_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_82_canary_executor_activation_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_83_canary_executor_open_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_84_canary_authoring_enable_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_85_canary_authoring_command_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_86_canary_authoring_command_dispatch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_87_canary_authoring_command_execution_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_88_canary_authoring_command_execution_evidence_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_89_canary_authoring_command_completion_decision_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_90_canary_authoring_command_completion_application_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_91_canary_authoring_command_completion_result_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_92_canary_authoring_command_result_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_93_canary_authoring_final_no_save_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_94_canary_authoring_final_release_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_95_durable_executor_implementation_review_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_96_durable_executor_implementation_plan_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_97_durable_executor_change_design_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_98_durable_executor_code_change_approval_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_99_durable_executor_code_patch_plan_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_100_durable_executor_code_patch_review_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_101_durable_executor_code_patch_application_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_102_durable_executor_code_patch_execution_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_103_durable_executor_code_patch_result_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_104_durable_executor_code_patch_result_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_105_durable_executor_code_patch_final_no_save_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_106_durable_executor_code_patch_final_release_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_107_durable_executor_code_patch_release_review_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_108_durable_executor_code_patch_release_decision_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_109_durable_executor_release_promotion_barrier_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_110_durable_executor_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_111_durable_executor_open_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_112_durable_executor_authoring_enable_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "final_durable_release_ready": False,
            "main_push_requested": False,
            "current_authoring_ceiling": (
                "planner_safe_temporary_manifest_execution_with_structural_validation_durable_read_only_preflight_section_51_enable_contract_section_52_ownership_marker_section_53_dry_run_plan_section_54_save_simulator_section_55_canary_prep_section_56_canary_approval_gate_section_57_canary_live_preflight_section_58_canary_recovery_matrix_section_59_release_boundary_v2_section_60_mvp_decision_section_61_bridge_refresh_contract_section_62_live_evidence_refresh_contract_section_63_executor_review_contract_section_64_canary_command_allowlist_contract_section_65_canary_creation_boundary_contract_section_66_ownership_marker_proof_contract_section_67_rollback_cleanup_proof_contract_section_68_save_gate_final_review_contract_section_69_canary_rehearsal_readiness_contract_section_70_durable_release_decision_contract_section_71_bridge_recovery_readiness_contract_section_72_canary_read_only_retry_envelope_contract_section_73_canary_read_only_retry_result_admission_contract_section_74_canary_rehearsal_promotion_barrier_contract_section_75_canary_rehearsal_execution_release_contract_section_76_canary_live_runner_envelope_contract_section_77_canary_live_runner_start_contract_section_78_canary_live_command_dispatch_release_contract_section_79_canary_live_command_execution_release_contract_section_80_canary_live_command_execution_evidence_admission_contract_section_81_canary_release_promotion_decision_contract_section_82_canary_executor_activation_contract_section_83_canary_executor_open_contract_section_84_canary_authoring_enable_contract_section_85_canary_authoring_command_contract_section_86_canary_authoring_command_dispatch_contract_section_87_canary_authoring_command_execution_contract_section_88_canary_authoring_command_execution_evidence_contract_section_89_canary_authoring_command_completion_decision_contract_section_90_canary_authoring_command_completion_application_contract_section_91_canary_authoring_command_completion_result_contract_section_92_canary_authoring_command_result_readback_contract_section_93_canary_authoring_final_no_save_release_contract_section_94_canary_authoring_final_release_readiness_contract_section_95_durable_executor_implementation_review_contract_section_96_durable_executor_implementation_plan_contract_section_97_durable_executor_change_design_contract_section_98_durable_executor_code_change_approval_contract_section_99_durable_executor_code_patch_plan_contract_section_100_durable_executor_code_patch_review_contract_section_101_durable_executor_code_patch_application_contract_section_102_durable_executor_code_patch_execution_contract_section_103_durable_executor_code_patch_result_contract_section_104_durable_executor_code_patch_result_readback_contract_section_105_durable_executor_code_patch_final_no_save_release_contract_section_106_durable_executor_code_patch_final_release_readiness_contract_section_107_durable_executor_code_patch_release_review_contract_section_108_durable_executor_code_patch_release_decision_contract_section_109_durable_executor_release_promotion_barrier_contract_section_110_durable_executor_activation_readiness_contract_section_111_durable_executor_open_contract_and_section_112_durable_executor_authoring_enable_contract"
            ),
            "cxx_changes_required": False,
        },
        "next_reinforcement_candidates": [
            "durable authoring command contract only after durable authoring enable record",
            "component default/type readback expansion for broader Blueprint classes",
            "function call diagnostics and graph layout repair suggestions",
        ],
    }


def render_markdown(report: Dict[str, Any]) -> str:
    verdict = report["verdict"]
    lines = [
        "# BP Authoring Release Boundary",
        "",
        f"- Generated UTC: `{report['generated_at']}`",
        f"- Schema: `{report['schema']}`",
        f"- Status: `{verdict['status']}`",
        f"- Ready for main push: `{verdict['ready_for_main_push']}`",
        f"- Durable authoring enabled: `{verdict['durable_authoring_enabled']}`",
        f"- Durable release status: `{verdict['durable_authoring_release_status']}`",
        f"- Current authoring ceiling: `{verdict['current_authoring_ceiling']}`",
        "",
        "## Regression Matrix",
        "",
    ]
    for item in report["regression_matrix"]:
        lines.append(
            f"- `{item['status']}` `{item['id']}` blocking=`{item['blocking']}` - {item['label']}"
        )
        if item["status"] != "passed":
            lines.append(f"  - expected: `{json.dumps(item['expected'], sort_keys=True)}`")
            lines.append(f"  - actual: `{json.dumps(item['actual'], sort_keys=True)}`")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "This boundary permits temporary planner-safe manifest execution only. Section 70 records the durable release decision: durable Blueprint creation, saving, delete, rename, cleanup, and live canary rehearsal remain disabled until a later explicit durable release.",
            "",
            "## Next Reinforcement Candidates",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["next_reinforcement_candidates"])
    return "\n".join(lines) + "\n"


def write_report(report: Dict[str, Any], output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "bp_authoring_release_boundary_report.json"
    md_path = output_dir / "bp_authoring_release_boundary_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_arg_parser() -> argparse.ArgumentParser:
    repo_root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(repo_root / "Docs" / "Analysis" / "BPAuthoringReleaseBoundary"))
    parser.add_argument("--project-root", default=str(repo_root.parent / "CubelessStylized"))
    parser.add_argument("--no-write", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    report = build_report(project_root=Path(args.project_root).resolve())
    if not args.no_write:
        json_path, md_path = write_report(report, Path(args.output_dir).resolve())
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    print(f"Release boundary status: {report['verdict']['status']}")
    print(f"Failed blocking rows: {report['verdict']['failed_blocking_count']}")
    return 0 if report["verdict"]["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
