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
import bp_authoring_durable_executor_authoring_command_completion_application_contract as durable_executor_authoring_command_completion_application
import bp_authoring_durable_executor_authoring_command_completion_decision_contract as durable_executor_authoring_command_completion_decision
import bp_authoring_durable_executor_authoring_command_completion_result_contract as durable_executor_authoring_command_completion_result
import bp_authoring_durable_executor_authoring_command_contract as durable_executor_authoring_command
import bp_authoring_durable_executor_authoring_command_dispatch_contract as durable_executor_authoring_command_dispatch
import bp_authoring_durable_executor_authoring_command_execution_contract as durable_executor_authoring_command_execution
import bp_authoring_durable_executor_authoring_command_execution_evidence_contract as durable_executor_authoring_command_execution_evidence
import bp_authoring_durable_executor_authoring_final_release_readiness_contract as durable_executor_authoring_final_release_readiness
import bp_authoring_durable_executor_authoring_final_no_save_release_contract as durable_executor_authoring_final_no_save_release
import bp_authoring_durable_executor_authoring_command_result_readback_contract as durable_executor_authoring_command_result_readback
import bp_authoring_durable_executor_authoring_command_after_enable_contract as durable_executor_authoring_command_after_enable
import bp_authoring_durable_executor_authoring_command_dispatch_after_command_contract as durable_executor_authoring_command_dispatch_after_command
import bp_authoring_durable_executor_authoring_command_execution_after_dispatch_contract as durable_executor_authoring_command_execution_after_dispatch
import bp_authoring_durable_executor_authoring_command_execution_evidence_after_execution_contract as durable_executor_authoring_command_execution_evidence_after_execution
import bp_authoring_durable_executor_authoring_command_completion_decision_after_evidence_contract as durable_executor_authoring_command_completion_decision_after_evidence
import bp_authoring_durable_executor_authoring_command_completion_application_after_decision_contract as durable_executor_authoring_command_completion_application_after_decision
import bp_authoring_durable_executor_authoring_command_completion_result_after_application_contract as durable_executor_authoring_command_completion_result_after_application
import bp_authoring_durable_executor_authoring_command_result_readback_after_result_contract as durable_executor_authoring_command_result_readback_after_result
import bp_authoring_durable_executor_authoring_final_no_save_release_after_readback_contract as durable_executor_authoring_final_no_save_release_after_readback
import bp_authoring_durable_executor_authoring_final_release_readiness_after_no_save_release_contract as durable_executor_authoring_final_release_readiness_after_no_save_release
import bp_authoring_durable_executor_authoring_release_review_after_readiness_contract as durable_executor_authoring_release_review_after_readiness
import bp_authoring_durable_executor_authoring_release_decision_after_review_contract as durable_executor_authoring_release_decision_after_review
import bp_authoring_durable_executor_authoring_release_promotion_barrier_after_decision_contract as durable_executor_authoring_release_promotion_barrier_after_decision
import bp_authoring_durable_executor_authoring_activation_readiness_after_promotion_barrier_contract as durable_executor_authoring_activation_readiness_after_promotion_barrier
import bp_authoring_durable_executor_authoring_open_after_activation_readiness_contract as durable_executor_authoring_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_enable_after_open_after_activation_readiness_contract as durable_executor_authoring_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_contract as durable_executor_authoring_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract as durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract as durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract as durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract as durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_completion_application_after_activation_readiness_contract as durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_completion_result_after_activation_readiness_contract as durable_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_result_readback_after_activation_readiness_contract as durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_final_no_save_after_activation_readiness_contract as durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_final_readiness_after_activation_readiness_contract as durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_release_review_after_activation_readiness_contract as durable_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_release_decision_after_activation_readiness_contract as durable_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_promotion_barrier_after_activation_readiness_contract as durable_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_activation_readiness_after_promotion_barrier_after_activation_readiness_contract as durable_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_contract as durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_contract as durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_contract as durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness
import bp_authoring_durable_executor_authoring_command_request_dry_run_route_contract as durable_executor_authoring_command_request_dry_run_route
import bp_authoring_durable_executor_authoring_command_dispatch_dry_run_contract as durable_executor_authoring_command_dispatch_dry_run
import bp_authoring_durable_executor_authoring_command_dispatch_evidence_dry_run_contract as durable_executor_authoring_command_dispatch_evidence_dry_run
import bp_authoring_durable_executor_authoring_command_execution_dry_run_contract as durable_executor_authoring_command_execution_dry_run
import bp_authoring_durable_executor_authoring_command_execution_evidence_dry_run_contract as durable_executor_authoring_command_execution_evidence_dry_run
import bp_authoring_durable_executor_authoring_command_completion_decision_dry_run_contract as durable_executor_authoring_command_completion_decision_dry_run
import bp_authoring_durable_executor_authoring_command_completion_application_dry_run_contract as durable_executor_authoring_command_completion_application_dry_run
import bp_authoring_durable_executor_authoring_command_completion_result_dry_run_contract as durable_executor_authoring_command_completion_result_dry_run
import bp_authoring_durable_executor_authoring_command_result_readback_dry_run_contract as durable_executor_authoring_command_result_readback_dry_run
import bp_authoring_durable_executor_authoring_final_no_save_release_dry_run_contract as durable_executor_authoring_final_no_save_release_dry_run
import bp_authoring_durable_executor_authoring_final_release_readiness_dry_run_contract as durable_executor_authoring_final_release_readiness_dry_run
import bp_authoring_durable_executor_authoring_release_review_dry_run_contract as durable_executor_authoring_release_review_dry_run
import bp_authoring_durable_executor_authoring_release_decision_dry_run_contract as durable_executor_authoring_release_decision_dry_run
import bp_authoring_durable_executor_authoring_release_promotion_barrier_dry_run_contract as durable_executor_authoring_release_promotion_barrier_dry_run
import bp_authoring_durable_executor_authoring_activation_readiness_dry_run_contract as durable_executor_authoring_activation_readiness_dry_run
import bp_authoring_durable_executor_authoring_open_dry_run_contract as durable_executor_authoring_open_dry_run
import bp_authoring_durable_executor_authoring_open_promotion_barrier_dry_run_contract as durable_executor_authoring_open_promotion_barrier_dry_run
import bp_authoring_durable_executor_authoring_command_path_dry_run_contract as durable_executor_authoring_command_path_dry_run
import bp_authoring_durable_executor_authoring_command_admission_dry_run_contract as durable_executor_authoring_command_admission_dry_run
import bp_authoring_durable_executor_authoring_release_boundary_consolidation_contract as durable_executor_authoring_release_boundary_consolidation
import bp_authoring_durable_executor_authoring_safety_boundary_unlock_decision_contract as durable_executor_authoring_safety_boundary_unlock_decision
import bp_authoring_durable_executor_authoring_safety_boundary_unlock_record_contract as durable_executor_authoring_safety_boundary_unlock_record
import bp_authoring_durable_executor_authoring_safety_boundary_unlock_contract as durable_executor_authoring_safety_boundary_unlock
import bp_authoring_durable_executor_authoring_enable_after_safety_boundary_unlock_contract as durable_executor_authoring_enable_after_safety_boundary_unlock
import bp_authoring_durable_executor_authoring_no_save_execution_batch_contract as durable_executor_authoring_no_save_execution_batch
import bp_authoring_durable_executor_authoring_save_gate_preflight_batch_contract as durable_executor_authoring_save_gate_preflight_batch
import bp_authoring_durable_executor_authoring_save_gate_open_admission_batch_contract as durable_executor_authoring_save_gate_open_admission_batch
import bp_authoring_durable_executor_authoring_live_pre_save_checkpoint_batch_contract as durable_executor_authoring_live_pre_save_checkpoint_batch
import bp_authoring_durable_executor_authoring_live_actual_save_execution_batch_contract as durable_executor_authoring_live_actual_save_execution_batch
import bp_authoring_durable_executor_authoring_live_save_stability_batch_contract as durable_executor_authoring_live_save_stability_batch
import bp_authoring_durable_executor_authoring_cleanup_delete_dry_run_batch_contract as durable_executor_authoring_cleanup_delete_dry_run_batch
import bp_authoring_durable_executor_authoring_rename_overwrite_dry_run_batch_contract as durable_executor_authoring_rename_overwrite_dry_run_batch
import bp_authoring_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract as durable_executor_authoring_actor_bp_expansion_dry_run_batch
import bp_authoring_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract as durable_executor_authoring_live_actor_bp_authoring_preflight_batch
import bp_authoring_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract as durable_executor_authoring_live_actor_bp_actual_authoring_batch
import bp_authoring_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract as durable_executor_authoring_live_actor_bp_component_default_readback_batch
import bp_authoring_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract as durable_executor_authoring_function_diagnostics_graph_layout_batch
import bp_authoring_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract as durable_executor_authoring_cleanup_delete_actual_execution_batch
import bp_authoring_durable_executor_authoring_post_delete_recreation_reset_batch_contract as durable_executor_authoring_post_delete_recreation_reset_batch
import bp_authoring_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract as durable_executor_authoring_post_delete_recreation_actual_execution_batch
import bp_authoring_durable_executor_authoring_enable_contract as durable_executor_authoring_enable
import bp_authoring_durable_executor_authoring_enable_after_open_contract as durable_executor_authoring_enable_after_open
import bp_authoring_durable_executor_authoring_activation_readiness_contract as durable_executor_authoring_activation_readiness
import bp_authoring_durable_executor_authoring_open_contract as durable_executor_authoring_open
import bp_authoring_durable_executor_authoring_release_decision_contract as durable_executor_authoring_release_decision
import bp_authoring_durable_executor_authoring_release_promotion_barrier_contract as durable_executor_authoring_release_promotion_barrier
import bp_authoring_durable_executor_authoring_release_review_contract as durable_executor_authoring_release_review
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


REPORT_SCHEMA = "section_305_312_bp_authoring_release_boundary_v143"
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


def build_durable_executor_authoring_command_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    authoring_enable_row = build_durable_executor_authoring_enable_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    authoring_enable_summary = dict(authoring_enable_row["actual"])
    authoring_enable_summary["status"] = authoring_enable_summary.pop(
        "summary_status"
    )
    contract = durable_executor_authoring_command.build_durable_executor_authoring_command_contract(
        requested=True,
        authoring_enable_summary=authoring_enable_summary,
    )
    summary = durable_executor_authoring_command.summarize_durable_executor_authoring_commands(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_count": 1,
        "authoring_command_contract_defined_count": 1,
        "authoring_enable_contract_ready_count": 1,
        "authoring_enable_inputs_satisfied_count": 0,
        "authoring_enable_record_valid_count": 0,
        "allowed_authoring_enable_observed_count": 0,
        "no_forbidden_authoring_enable_claims_count": 0,
        "target_package_allowlist_reconfirmed_count": 0,
        "overwrite_rename_decision_reconfirmed_count": 0,
        "rollback_readiness_reconfirmed_count": 0,
        "ownership_marker_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_present_count": 0,
        "record_schema_matches_count": 0,
        "command_scope_matches_count": 0,
        "explicit_authoring_command_authorized_count": 0,
        "command_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "planned_authoring_command_count": 0,
        "allowed_authoring_command_count": 0,
        "forbidden_authoring_command_count": 0,
        "unknown_authoring_command_count": 0,
        "authoring_command_record_valid_count": 0,
        "authoring_command_record_rejected_count": 0,
        "unsafe_authoring_command_record_count": 0,
        "missing_authoring_command_prerequisite_count": 17,
        "durable_authoring_command_contract_started_count": 0,
        "durable_authoring_command_contract_accepted_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "durable_executor_authoring_command_contract",
        "Section 113 durable executor authoring command contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command contract is defined, but no command record is present.",
            "Allowed command names are scoped and save/delete/rename/live dispatch/execution commands are forbidden.",
            "Command dispatch, command execution, asset writes, save, delete/rename, and cleanup remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_dispatch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    authoring_command_row = build_durable_executor_authoring_command_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    authoring_command_summary = dict(authoring_command_row["actual"])
    authoring_command_summary["status"] = authoring_command_summary.pop(
        "summary_status"
    )
    contract = durable_executor_authoring_command_dispatch.build_durable_executor_authoring_command_dispatch_contract(
        requested=True,
        authoring_command_summary=authoring_command_summary,
    )
    summary = durable_executor_authoring_command_dispatch.summarize_durable_executor_authoring_command_dispatches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_dispatch_count": 1,
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
        "dispatch_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_dispatch_observed_count": 0,
        "no_forbidden_dispatch_claims_count": 0,
        "dispatch_record_valid_count": 0,
        "dispatch_record_rejected_count": 0,
        "unsafe_dispatch_record_count": 0,
        "missing_dispatch_prerequisite_count": 14,
        "reported_allowed_dispatch_count": 0,
        "reported_forbidden_dispatch_count": 0,
        "durable_authoring_command_dispatch_started_count": 0,
        "durable_authoring_command_dispatch_accepted_count": 0,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_contract_started_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "durable_executor_authoring_command_dispatch_contract",
        "Section 114 durable executor authoring command dispatch contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command dispatch contract is defined, but no dispatch record is present.",
            "Dispatch, execution, asset writes, save, delete/rename, cleanup, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_execution_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    dispatch_row = build_durable_executor_authoring_command_dispatch_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    dispatch_summary = dict(dispatch_row["actual"])
    dispatch_summary["status"] = dispatch_summary.pop("summary_status")
    contract = durable_executor_authoring_command_execution.build_durable_executor_authoring_command_execution_contract(
        requested=True,
        dispatch_summary=dispatch_summary,
    )
    summary = durable_executor_authoring_command_execution.summarize_durable_executor_authoring_command_executions(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_execution_count": 1,
        "execution_contract_defined_count": 1,
        "dispatch_contract_ready_count": 1,
        "dispatch_inputs_satisfied_count": 0,
        "dispatch_record_valid_count": 0,
        "planned_authoring_commands_present_count": 0,
        "allowed_authoring_commands_present_count": 0,
        "allowed_dispatch_observed_count": 0,
        "no_forbidden_dispatch_claims_count": 0,
        "execution_inputs_satisfied_count": 0,
        "execution_record_present_count": 0,
        "record_schema_matches_count": 0,
        "execution_scope_matches_count": 0,
        "explicit_execution_authorized_count": 0,
        "execution_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_execution_observed_count": 0,
        "no_forbidden_execution_claims_count": 0,
        "execution_record_valid_count": 0,
        "execution_record_rejected_count": 0,
        "unsafe_execution_record_count": 0,
        "missing_execution_prerequisite_count": 16,
        "reported_allowed_execution_count": 0,
        "reported_forbidden_execution_count": 0,
        "durable_authoring_command_execution_started_count": 0,
        "durable_authoring_command_execution_accepted_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_command_execution_evidence_contract_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "durable_executor_authoring_command_execution_contract",
        "Section 115 durable executor authoring command execution contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command execution contract is defined, but no execution record is present.",
            "Execution, evidence admission, asset writes, save, delete/rename, and cleanup remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_execution_evidence_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    execution_row = build_durable_executor_authoring_command_execution_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    execution_summary = dict(execution_row["actual"])
    execution_summary["status"] = execution_summary.pop("summary_status")
    contract = durable_executor_authoring_command_execution_evidence.build_durable_executor_authoring_command_execution_evidence_contract(
        requested=True,
        execution_summary=execution_summary,
    )
    summary = durable_executor_authoring_command_execution_evidence.summarize_durable_executor_authoring_command_execution_evidence(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_execution_evidence_count": 1,
        "evidence_contract_defined_count": 1,
        "execution_contract_ready_count": 1,
        "execution_inputs_satisfied_count": 0,
        "execution_record_valid_count": 0,
        "planned_authoring_commands_present_count": 0,
        "allowed_authoring_commands_present_count": 0,
        "allowed_execution_observed_count": 0,
        "no_forbidden_execution_claims_count": 0,
        "evidence_inputs_satisfied_count": 0,
        "evidence_record_present_count": 0,
        "record_schema_matches_count": 0,
        "evidence_scope_matches_count": 0,
        "explicit_evidence_authorized_count": 0,
        "evidence_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_evidence_command_observed_count": 0,
        "no_forbidden_evidence_commands_count": 0,
        "authoring_command_execution_evidence_admitted_count": 0,
        "evidence_record_rejected_count": 0,
        "unsafe_evidence_record_count": 0,
        "missing_evidence_prerequisite_count": 16,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
        "durable_authoring_command_completion_decision_started_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_execution_evidence_contract",
        "Section 116 durable executor authoring command execution evidence contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command execution evidence contract is defined, but no execution record or evidence record is present.",
            "Evidence admission, completion decision, asset writes, save, delete/rename, cleanup, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_completion_decision_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    evidence_row = build_durable_executor_authoring_command_execution_evidence_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    evidence_summary = dict(evidence_row["actual"])
    evidence_summary["status"] = evidence_summary.pop("summary_status")
    contract = durable_executor_authoring_command_completion_decision.build_durable_executor_authoring_command_completion_decision_contract(
        requested=True,
        evidence_summary=evidence_summary,
    )
    summary = durable_executor_authoring_command_completion_decision.summarize_durable_executor_authoring_command_completion_decisions(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_completion_decision_count": 1,
        "completion_decision_contract_defined_count": 1,
        "evidence_contract_ready_count": 1,
        "authoring_command_execution_evidence_admitted_count": 0,
        "allowed_evidence_command_observed_count": 0,
        "no_forbidden_evidence_commands_count": 0,
        "evidence_ready_for_completion_count": 0,
        "decision_record_present_count": 0,
        "record_schema_matches_count": 0,
        "completion_scope_matches_count": 0,
        "explicit_completion_decision_authorized_count": 0,
        "completion_decision_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "completion_decision_record_valid_count": 0,
        "completion_decision_record_rejected_count": 0,
        "unsafe_completion_decision_record_count": 0,
        "missing_completion_prerequisite_count": 11,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
        "durable_authoring_command_completion_allowed_count": 0,
        "durable_authoring_command_completed_count": 0,
        "durable_authoring_command_completion_application_started_count": 0,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "durable_executor_authoring_command_completion_decision_contract",
        "Section 117 durable executor authoring command completion decision contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command completion decision contract is defined, but no execution evidence record or completion decision record is present.",
            "Completion, completion application, asset writes, save, delete/rename, cleanup, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_completion_application_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    decision_row = build_durable_executor_authoring_command_completion_decision_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    decision_summary = dict(decision_row["actual"])
    decision_summary["status"] = decision_summary.pop("summary_status")
    contract = durable_executor_authoring_command_completion_application.build_durable_executor_authoring_command_completion_application_contract(
        requested=True,
        completion_decision_summary=decision_summary,
    )
    summary = durable_executor_authoring_command_completion_application.summarize_durable_executor_authoring_command_completion_applications(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_completion_application_count": 1,
        "application_contract_defined_count": 1,
        "completion_decision_contract_ready_count": 1,
        "evidence_ready_for_completion_count": 0,
        "completion_decision_record_valid_count": 0,
        "application_inputs_satisfied_count": 0,
        "application_record_present_count": 0,
        "record_schema_matches_count": 0,
        "application_scope_matches_count": 0,
        "explicit_application_authorized_count": 0,
        "application_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "application_record_valid_count": 0,
        "application_record_rejected_count": 0,
        "unsafe_application_record_count": 0,
        "missing_application_prerequisite_count": 10,
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
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
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
        "durable_executor_authoring_command_completion_application_contract",
        "Section 118 durable executor authoring command completion application contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command completion application contract is defined, but no completion decision record or application record is present.",
            "Completion application, asset writes, dirty marking, save, delete/rename, cleanup, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_completion_result_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    application_row = build_durable_executor_authoring_command_completion_application_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    application_summary = dict(application_row["actual"])
    application_summary["status"] = application_summary.pop("summary_status")
    contract = durable_executor_authoring_command_completion_result.build_durable_executor_authoring_command_completion_result_contract(
        requested=True,
        application_summary=application_summary,
    )
    summary = durable_executor_authoring_command_completion_result.summarize_durable_executor_authoring_command_completion_results(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_completion_result_count": 1,
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
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_result_observed_count": 0,
        "no_forbidden_results_count": 0,
        "result_record_valid_count": 0,
        "result_record_rejected_count": 0,
        "unsafe_result_record_count": 0,
        "missing_result_prerequisite_count": 12,
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
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_completion_noop_result_count": 0,
        "reported_application_validation_result_count": 0,
        "reported_completion_completed_result_count": 0,
        "reported_asset_write_result_count": 0,
        "reported_package_dirty_result_count": 0,
        "reported_save_result_count": 0,
        "reported_delete_rename_result_count": 0,
        "reported_cleanup_result_count": 0,
        "reported_code_change_result_count": 0,
        "reported_live_command_result_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_completion_result_contract",
        "Section 119 durable executor authoring command completion result contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command completion result contract is defined, but no application record or result record is present.",
            "Result acceptance, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_result_readback_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    result_row = build_durable_executor_authoring_command_completion_result_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    result_summary = dict(result_row["actual"])
    result_summary["status"] = result_summary.pop("summary_status")
    contract = durable_executor_authoring_command_result_readback.build_durable_executor_authoring_command_result_readback_contract(
        requested=True,
        result_summary=result_summary,
    )
    summary = durable_executor_authoring_command_result_readback.summarize_durable_executor_authoring_command_result_readbacks(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_result_readback_count": 1,
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
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_readback_observed_count": 0,
        "no_forbidden_readbacks_count": 0,
        "readback_record_valid_count": 0,
        "readback_record_rejected_count": 0,
        "unsafe_readback_record_count": 0,
        "missing_readback_prerequisite_count": 14,
        "reported_allowed_readback_count": 0,
        "reported_forbidden_readback_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_no_completion_readback_count": 0,
        "reported_no_write_readback_count": 0,
        "reported_no_save_readback_count": 0,
        "reported_completed_readback_count": 0,
        "reported_asset_write_readback_count": 0,
        "reported_package_dirty_readback_count": 0,
        "reported_save_readback_count": 0,
        "reported_delete_rename_readback_count": 0,
        "reported_cleanup_readback_count": 0,
        "reported_code_change_readback_count": 0,
        "reported_live_command_readback_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_result_readback_contract",
        "Section 120 durable executor authoring command result readback contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command result readback contract is defined, but no result record or readback record is present.",
            "Readback acceptance, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_final_no_save_release_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readback_row = build_durable_executor_authoring_command_result_readback_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    readback_summary = dict(readback_row["actual"])
    readback_summary["status"] = readback_summary.pop("summary_status")
    contract = durable_executor_authoring_final_no_save_release.build_durable_executor_authoring_final_no_save_release_contract(
        requested=True,
        readback_summary=readback_summary,
    )
    summary = durable_executor_authoring_final_no_save_release.summarize_durable_executor_authoring_final_no_save_releases(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_final_no_save_release_count": 1,
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
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_final_no_save_release_observed_count": 0,
        "no_forbidden_final_no_save_releases_count": 0,
        "final_no_save_release_record_valid_count": 0,
        "final_no_save_release_record_rejected_count": 0,
        "unsafe_final_no_save_release_record_count": 0,
        "missing_final_no_save_release_prerequisite_count": 14,
        "reported_allowed_final_no_save_release_count": 0,
        "reported_forbidden_final_no_save_release_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_no_completion_release_count": 0,
        "reported_no_write_release_count": 0,
        "reported_no_save_release_count": 0,
        "reported_readback_revalidated_count": 0,
        "reported_no_code_change_release_count": 0,
        "reported_no_live_command_release_count": 0,
        "reported_completion_release_count": 0,
        "reported_asset_write_release_count": 0,
        "reported_package_dirty_release_count": 0,
        "reported_save_release_count": 0,
        "reported_delete_rename_release_count": 0,
        "reported_cleanup_release_count": 0,
        "reported_durable_authoring_release_count": 0,
        "reported_code_change_release_count": 0,
        "reported_live_command_release_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_final_no_save_release_contract",
        "Section 121 durable executor authoring final no-save release contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring final no-save release contract is defined, but no readback record or final no-save release record is present.",
            "Final release readiness, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_final_release_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    final_no_save_release_row = build_durable_executor_authoring_final_no_save_release_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    final_no_save_release_summary = dict(final_no_save_release_row["actual"])
    final_no_save_release_summary["status"] = final_no_save_release_summary.pop(
        "summary_status"
    )
    contract = durable_executor_authoring_final_release_readiness.build_durable_executor_authoring_final_release_readiness_contract(
        requested=True,
        final_no_save_release_summary=final_no_save_release_summary,
    )
    summary = durable_executor_authoring_final_release_readiness.summarize_durable_executor_authoring_final_release_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_final_release_readiness_count": 1,
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
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_final_release_readiness_gate_count": 0,
        "reported_final_no_save_release_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_readiness_count": 0,
        "reported_no_write_readiness_count": 0,
        "reported_no_save_readiness_count": 0,
        "reported_no_code_change_readiness_count": 0,
        "reported_no_live_command_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_final_release_readiness_contract",
        "Section 122 durable executor authoring final release readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring final release readiness contract is defined, but no final no-save release record or readiness record is present.",
            "Release review, final readiness, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_release_review_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readiness_row = build_durable_executor_authoring_final_release_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    readiness_summary = dict(readiness_row["actual"])
    readiness_summary["status"] = readiness_summary.pop("summary_status")
    contract = durable_executor_authoring_release_review.build_durable_executor_authoring_release_review_contract(
        requested=True,
        final_release_readiness_summary=readiness_summary,
    )
    summary = durable_executor_authoring_release_review.summarize_durable_executor_authoring_release_reviews(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_release_review_count": 1,
        "release_review_contract_defined_count": 1,
        "final_release_readiness_contract_ready_count": 1,
        "final_release_readiness_inputs_satisfied_count": 0,
        "final_release_readiness_record_valid_count": 0,
        "allowed_final_release_readiness_observed_count": 0,
        "no_forbidden_final_release_readiness_claims_count": 0,
        "release_review_inputs_satisfied_count": 0,
        "release_review_record_present_count": 0,
        "record_schema_matches_count": 0,
        "release_review_scope_matches_count": 0,
        "explicit_release_review_authorized_count": 0,
        "release_review_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_release_review_observed_count": 0,
        "no_forbidden_release_review_claims_count": 0,
        "release_review_record_valid_count": 0,
        "release_review_record_rejected_count": 0,
        "unsafe_release_review_record_count": 0,
        "missing_release_review_prerequisite_count": 14,
        "reported_allowed_release_review_count": 0,
        "reported_forbidden_release_review_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_release_review_gate_count": 0,
        "reported_final_release_readiness_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_release_review_count": 0,
        "reported_no_write_release_review_count": 0,
        "reported_no_save_release_review_count": 0,
        "reported_no_code_change_release_review_count": 0,
        "reported_no_live_command_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_review_contract",
        "Section 123 durable executor authoring release review contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring release review contract is defined, but no final release readiness record or release review record is present.",
            "Release decision, review acceptance, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_release_decision_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    review_row = build_durable_executor_authoring_release_review_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    review_summary = dict(review_row["actual"])
    review_summary["status"] = review_summary.pop("summary_status")
    contract = durable_executor_authoring_release_decision.build_durable_executor_authoring_release_decision_contract(
        requested=True,
        release_review_summary=review_summary,
    )
    summary = durable_executor_authoring_release_decision.summarize_durable_executor_authoring_release_decisions(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_release_decision_count": 1,
        "release_decision_contract_defined_count": 1,
        "release_review_contract_ready_count": 1,
        "release_review_inputs_satisfied_count": 0,
        "release_review_record_valid_count": 0,
        "allowed_release_review_observed_count": 0,
        "no_forbidden_release_review_claims_count": 0,
        "release_decision_inputs_satisfied_count": 0,
        "release_decision_record_present_count": 0,
        "record_schema_matches_count": 0,
        "release_decision_scope_matches_count": 0,
        "explicit_release_decision_authorized_count": 0,
        "release_decision_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_release_decision_observed_count": 0,
        "no_forbidden_release_decision_claims_count": 0,
        "release_decision_record_valid_count": 0,
        "release_decision_record_rejected_count": 0,
        "unsafe_release_decision_record_count": 0,
        "missing_release_decision_prerequisite_count": 14,
        "reported_allowed_release_decision_count": 0,
        "reported_forbidden_release_decision_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_release_decision_gate_count": 0,
        "reported_release_review_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_release_decision_count": 0,
        "reported_no_write_release_decision_count": 0,
        "reported_no_save_release_decision_count": 0,
        "reported_no_code_change_release_decision_count": 0,
        "reported_no_live_command_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_decision_contract",
        "Section 124 durable executor authoring release decision contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring release decision contract is defined, but no release review record or decision record is present.",
            "Promotion barrier, release decision acceptance, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_release_promotion_barrier_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    decision_row = build_durable_executor_authoring_release_decision_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    decision_summary = dict(decision_row["actual"])
    decision_summary["status"] = decision_summary.pop("summary_status")
    contract = durable_executor_authoring_release_promotion_barrier.build_durable_executor_authoring_release_promotion_barrier_contract(
        requested=True,
        release_decision_summary=decision_summary,
    )
    summary = durable_executor_authoring_release_promotion_barrier.summarize_durable_executor_authoring_release_promotion_barriers(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_release_promotion_barrier_count": 1,
        "release_promotion_barrier_contract_defined_count": 1,
        "release_decision_contract_ready_count": 1,
        "release_decision_inputs_satisfied_count": 0,
        "release_decision_record_valid_count": 0,
        "allowed_release_decision_observed_count": 0,
        "no_forbidden_release_decision_claims_count": 0,
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
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_promotion_barrier_gate_count": 0,
        "reported_release_decision_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_promotion_barrier_count": 0,
        "reported_no_write_promotion_barrier_count": 0,
        "reported_no_save_promotion_barrier_count": 0,
        "reported_no_code_change_promotion_barrier_count": 0,
        "reported_no_live_command_promotion_barrier_count": 0,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_promotion_barrier_contract",
        "Section 125 durable executor authoring release promotion barrier contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring release promotion barrier contract is defined, but no release decision record or promotion barrier record is present.",
            "Activation readiness, executor activation/open, durable authoring enablement, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    barrier_row = build_durable_executor_authoring_release_promotion_barrier_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    barrier_summary = dict(barrier_row["actual"])
    barrier_summary["status"] = barrier_summary.pop("summary_status")
    contract = durable_executor_authoring_activation_readiness.build_durable_executor_authoring_activation_readiness_contract(
        requested=True,
        release_promotion_barrier_summary=barrier_summary,
    )
    summary = durable_executor_authoring_activation_readiness.summarize_durable_executor_authoring_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_activation_readiness_count": 1,
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
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_executor_open_contract_started_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_activation_readiness_gate_count": 0,
        "reported_promotion_barrier_revalidated_count": 0,
        "reported_release_decision_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_activation_readiness_count": 0,
        "reported_no_write_activation_readiness_count": 0,
        "reported_no_save_activation_readiness_count": 0,
        "reported_no_code_change_activation_readiness_count": 0,
        "reported_no_live_command_activation_readiness_count": 0,
        "reported_release_promotion_barrier_count": 0,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_activation_readiness_contract",
        "Section 126 durable executor authoring activation readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring activation readiness contract is defined, but no release promotion barrier record or activation readiness record is present.",
            "Executor activation/open, durable authoring enablement, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_open_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readiness_row = build_durable_executor_authoring_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    readiness_summary = dict(readiness_row["actual"])
    readiness_summary["status"] = readiness_summary.pop("summary_status")
    contract = durable_executor_authoring_open.build_durable_executor_authoring_open_contract(
        requested=True,
        activation_readiness_summary=readiness_summary,
    )
    summary = durable_executor_authoring_open.summarize_durable_executor_authoring_opens(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_open_count": 1,
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
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_executor_open_gate_count": 0,
        "reported_activation_readiness_revalidated_count": 0,
        "reported_promotion_barrier_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_open_count": 0,
        "reported_no_write_open_count": 0,
        "reported_no_save_open_count": 0,
        "reported_no_code_change_open_count": 0,
        "reported_no_live_command_open_count": 0,
        "reported_activation_readiness_count": 0,
        "reported_release_promotion_barrier_count": 0,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_durable_authoring_enable_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_open_contract",
        "Section 127 durable executor authoring open contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring open contract is defined, but no activation readiness record or open record is present.",
            "Executor open/activation, durable authoring enablement, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_enable_after_open_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    open_row = build_durable_executor_authoring_open_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    open_summary = dict(open_row["actual"])
    open_summary["status"] = open_summary.pop("summary_status")
    contract = durable_executor_authoring_enable_after_open.build_durable_executor_authoring_enable_after_open_contract(
        requested=True,
        open_summary=open_summary,
    )
    summary = durable_executor_authoring_enable_after_open.summarize_durable_executor_authoring_enable_after_open(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_enable_after_open_count": 1,
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
        "durable_executor_open_contract_started_count": 0,
        "durable_executor_open_contract_accepted_count": 0,
        "durable_executor_open_performed_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_authoring_enable_gate_count": 0,
        "reported_executor_open_revalidated_count": 0,
        "reported_target_allowlist_reconfirmed_count": 0,
        "reported_overwrite_rename_decision_reconfirmed_count": 0,
        "reported_rollback_readiness_reconfirmed_count": 0,
        "reported_ownership_marker_reconfirmed_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_code_change_authoring_enable_count": 0,
        "reported_no_asset_change_authoring_enable_count": 0,
        "reported_no_live_probe_authoring_enable_count": 0,
        "reported_activation_readiness_count": 0,
        "reported_release_promotion_barrier_count": 0,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_authoring_enable_count": 0,
        "reported_authoring_command_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_enable_after_open_contract",
        "Section 128 durable executor authoring enable-after-open contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring enable-after-open contract is defined, but no authoring open record or enable record is present.",
            "Durable authoring enablement, authoring command start, executor open, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_after_enable_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    enable_row = build_durable_executor_authoring_enable_after_open_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    enable_summary = dict(enable_row["actual"])
    enable_summary["status"] = enable_summary.pop("summary_status")
    contract = durable_executor_authoring_command_after_enable.build_durable_executor_authoring_command_after_enable_contract(
        requested=True,
        authoring_enable_summary=enable_summary,
    )
    summary = durable_executor_authoring_command_after_enable.summarize_durable_executor_authoring_commands_after_enable(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_after_enable_count": 1,
        "authoring_command_contract_defined_count": 1,
        "authoring_enable_contract_ready_count": 1,
        "authoring_enable_inputs_satisfied_count": 0,
        "authoring_enable_record_valid_count": 0,
        "allowed_authoring_enable_observed_count": 0,
        "no_forbidden_authoring_enable_claims_count": 0,
        "target_package_allowlist_reconfirmed_count": 0,
        "overwrite_rename_decision_reconfirmed_count": 0,
        "rollback_readiness_reconfirmed_count": 0,
        "ownership_marker_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_present_count": 0,
        "record_schema_matches_count": 0,
        "command_scope_matches_count": 0,
        "explicit_authoring_command_authorized_count": 0,
        "command_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "planned_authoring_command_count": 0,
        "allowed_authoring_command_count": 0,
        "forbidden_authoring_command_count": 0,
        "unknown_authoring_command_count": 0,
        "authoring_command_record_valid_count": 0,
        "authoring_command_record_rejected_count": 0,
        "unsafe_authoring_command_record_count": 0,
        "missing_authoring_command_prerequisite_count": 17,
        "durable_authoring_command_contract_started_count": 0,
        "durable_authoring_command_contract_accepted_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enable_started_count": 0,
        "durable_authoring_enable_accepted_count": 0,
        "durable_authoring_enable_allowed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "durable_executor_authoring_command_after_enable_contract",
        "Section 129 durable executor authoring command-after-enable contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command-after-enable contract is defined, but no enable-after-open record or command record is present.",
            "Authoring command allow/dispatch/execution, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_dispatch_after_command_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    command_row = build_durable_executor_authoring_command_after_enable_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    command_summary = dict(command_row["actual"])
    command_summary["status"] = command_summary.pop("summary_status")
    contract = durable_executor_authoring_command_dispatch_after_command.build_durable_executor_authoring_command_dispatch_after_command_contract(
        requested=True,
        authoring_command_summary=command_summary,
    )
    summary = durable_executor_authoring_command_dispatch_after_command.summarize_durable_executor_authoring_command_dispatches_after_command(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_dispatch_after_command_count": 1,
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
        "dispatch_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_dispatch_observed_count": 0,
        "no_forbidden_dispatch_claims_count": 0,
        "dispatch_record_valid_count": 0,
        "dispatch_record_rejected_count": 0,
        "unsafe_dispatch_record_count": 0,
        "missing_dispatch_prerequisite_count": 14,
        "reported_allowed_dispatch_count": 0,
        "reported_forbidden_dispatch_count": 0,
        "durable_authoring_command_dispatch_started_count": 0,
        "durable_authoring_command_dispatch_accepted_count": 0,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_contract_started_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_command_contract_started_count": 0,
        "durable_authoring_command_contract_accepted_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "reported_dispatch_gate_count": 0,
        "reported_authoring_command_revalidated_count": 0,
        "reported_no_live_dispatch_performed_count": 0,
        "reported_no_execution_authorized_count": 0,
        "reported_no_asset_write_dispatch_count": 0,
        "reported_no_save_delete_rename_dispatch_count": 0,
        "reported_authoring_command_dispatch_count": 0,
        "reported_authoring_command_execution_count": 0,
        "reported_live_dispatch_count": 0,
        "reported_live_execution_count": 0,
        "reported_code_change_count": 0,
        "reported_executor_code_modified_count": 0,
        "reported_unreal_asset_change_count": 0,
        "reported_live_probe_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_dispatch_after_command_contract",
        "Section 130 durable executor authoring command dispatch-after-command contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command dispatch-after-command contract is defined, but no command-after-enable record or dispatch record is present.",
            "Command dispatch/execution, live dispatch/execution, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_execution_after_dispatch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    dispatch_row = build_durable_executor_authoring_command_dispatch_after_command_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    dispatch_summary = dict(dispatch_row["actual"])
    dispatch_summary["status"] = dispatch_summary.pop("summary_status")
    contract = durable_executor_authoring_command_execution_after_dispatch.build_durable_executor_authoring_command_execution_after_dispatch_contract(
        requested=True,
        command_dispatch_after_command_summary=dispatch_summary,
    )
    summary = durable_executor_authoring_command_execution_after_dispatch.summarize_durable_executor_authoring_command_executions_after_dispatch(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_execution_after_dispatch_count": 1,
        "execution_contract_defined_count": 1,
        "dispatch_contract_ready_count": 1,
        "dispatch_inputs_satisfied_count": 0,
        "dispatch_record_valid_count": 0,
        "planned_authoring_commands_present_count": 0,
        "allowed_authoring_commands_present_count": 0,
        "allowed_dispatch_observed_count": 0,
        "no_forbidden_dispatch_claims_count": 0,
        "execution_inputs_satisfied_count": 0,
        "execution_record_present_count": 0,
        "record_schema_matches_count": 0,
        "execution_scope_matches_count": 0,
        "explicit_execution_authorized_count": 0,
        "execution_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_execution_observed_count": 0,
        "no_forbidden_execution_claims_count": 0,
        "execution_record_valid_count": 0,
        "execution_record_rejected_count": 0,
        "unsafe_execution_record_count": 0,
        "missing_execution_prerequisite_count": 16,
        "reported_allowed_execution_count": 0,
        "reported_forbidden_execution_count": 0,
        "durable_authoring_command_execution_started_count": 0,
        "durable_authoring_command_execution_accepted_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_command_execution_evidence_contract_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "reported_execution_gate_count": 0,
        "reported_dispatch_revalidated_count": 0,
        "reported_no_live_execution_performed_count": 0,
        "reported_no_execution_evidence_admitted_count": 0,
        "reported_no_asset_write_execution_count": 0,
        "reported_no_save_delete_rename_execution_count": 0,
        "reported_authoring_command_execution_count": 0,
        "reported_execution_evidence_count": 0,
        "reported_live_execution_count": 0,
        "reported_live_dispatch_count": 0,
        "reported_code_change_count": 0,
        "reported_executor_code_modified_count": 0,
        "reported_unreal_asset_change_count": 0,
        "reported_live_probe_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_execution_after_dispatch_contract",
        "Section 131 durable executor authoring command execution-after-dispatch contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command execution-after-dispatch contract is defined, but no dispatch-after-command record or execution record is present.",
            "Command execution, execution evidence admission, live dispatch/execution, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live probes remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_execution_evidence_after_execution_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    execution_row = build_durable_executor_authoring_command_execution_after_dispatch_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    execution_summary = dict(execution_row["actual"])
    execution_summary["status"] = execution_summary.pop("summary_status")
    contract = durable_executor_authoring_command_execution_evidence_after_execution.build_durable_executor_authoring_command_execution_evidence_after_execution_contract(
        requested=True,
        command_execution_after_dispatch_summary=execution_summary,
    )
    summary = durable_executor_authoring_command_execution_evidence_after_execution.summarize_durable_executor_authoring_command_execution_evidence_after_execution(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_execution_evidence_after_execution_count": 1,
        "evidence_contract_defined_count": 1,
        "execution_contract_ready_count": 1,
        "execution_inputs_satisfied_count": 0,
        "execution_record_valid_count": 0,
        "planned_authoring_commands_present_count": 0,
        "allowed_authoring_commands_present_count": 0,
        "allowed_execution_observed_count": 0,
        "no_forbidden_execution_claims_count": 0,
        "evidence_inputs_satisfied_count": 0,
        "evidence_record_present_count": 0,
        "record_schema_matches_count": 0,
        "evidence_scope_matches_count": 0,
        "explicit_evidence_authorized_count": 0,
        "evidence_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_evidence_command_observed_count": 0,
        "no_forbidden_evidence_commands_count": 0,
        "authoring_command_execution_evidence_admitted_count": 0,
        "evidence_record_rejected_count": 0,
        "unsafe_evidence_record_count": 0,
        "missing_evidence_prerequisite_count": 16,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
        "durable_authoring_command_completion_decision_started_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "reported_package_dirty_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_execution_evidence_after_execution_contract",
        "Section 132 durable executor authoring command execution evidence-after-execution contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command execution evidence-after-execution contract is defined, but no execution-after-dispatch record or evidence record is present.",
            "Evidence admission, completion decision, live dispatch/execution, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live probes remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_completion_decision_after_evidence_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    evidence_row = build_durable_executor_authoring_command_execution_evidence_after_execution_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    evidence_summary = dict(evidence_row["actual"])
    evidence_summary["status"] = evidence_summary.pop("summary_status")
    contract = durable_executor_authoring_command_completion_decision_after_evidence.build_durable_executor_authoring_command_completion_decision_after_evidence_contract(
        requested=True,
        evidence_after_execution_summary=evidence_summary,
    )
    summary = durable_executor_authoring_command_completion_decision_after_evidence.summarize_durable_executor_authoring_command_completion_decisions_after_evidence(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_completion_decision_after_evidence_count": 1,
        "completion_decision_contract_defined_count": 1,
        "evidence_contract_ready_count": 1,
        "authoring_command_execution_evidence_admitted_count": 0,
        "allowed_evidence_command_observed_count": 0,
        "no_forbidden_evidence_commands_count": 0,
        "evidence_ready_for_completion_count": 0,
        "decision_record_present_count": 0,
        "record_schema_matches_count": 0,
        "completion_scope_matches_count": 0,
        "explicit_completion_decision_authorized_count": 0,
        "completion_decision_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "completion_decision_record_valid_count": 0,
        "completion_decision_record_rejected_count": 0,
        "unsafe_completion_decision_record_count": 0,
        "missing_completion_prerequisite_count": 11,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
        "durable_authoring_command_completion_allowed_count": 0,
        "durable_authoring_command_completed_count": 0,
        "durable_authoring_command_completion_application_started_count": 0,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "durable_executor_authoring_command_completion_decision_after_evidence_contract",
        "Section 133 durable executor authoring command completion decision-after-evidence contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command completion decision-after-evidence contract is defined, but no evidence-after-execution record or completion decision record is present.",
            "Completion allowance, completion execution, completion application, live dispatch/execution, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live probes remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_completion_application_after_decision_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    decision_row = build_durable_executor_authoring_command_completion_decision_after_evidence_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    decision_summary = dict(decision_row["actual"])
    decision_summary["status"] = decision_summary.pop("summary_status")
    contract = durable_executor_authoring_command_completion_application_after_decision.build_durable_executor_authoring_command_completion_application_after_decision_contract(
        requested=True,
        completion_decision_after_evidence_summary=decision_summary,
    )
    summary = durable_executor_authoring_command_completion_application_after_decision.summarize_durable_executor_authoring_command_completion_applications_after_decision(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_completion_application_after_decision_count": 1,
        "application_contract_defined_count": 1,
        "completion_decision_contract_ready_count": 1,
        "evidence_ready_for_completion_count": 0,
        "completion_decision_record_valid_count": 0,
        "application_inputs_satisfied_count": 0,
        "application_record_present_count": 0,
        "record_schema_matches_count": 0,
        "application_scope_matches_count": 0,
        "explicit_application_authorized_count": 0,
        "application_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "application_record_valid_count": 0,
        "application_record_rejected_count": 0,
        "unsafe_application_record_count": 0,
        "missing_application_prerequisite_count": 10,
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
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
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
        "durable_executor_authoring_command_completion_application_after_decision_contract",
        "Section 134 durable executor authoring command completion application-after-decision contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command completion application-after-decision contract is defined, but no completion decision-after-evidence record or application record is present.",
            "Completion application, asset write allowance, package dirty marking, live dispatch/execution, save, delete/rename, cleanup, code changes, and live probes remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_completion_result_after_application_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    application_row = build_durable_executor_authoring_command_completion_application_after_decision_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    application_summary = dict(application_row["actual"])
    application_summary["status"] = application_summary.pop("summary_status")
    contract = durable_executor_authoring_command_completion_result_after_application.build_durable_executor_authoring_command_completion_result_after_application_contract(
        requested=True,
        application_after_decision_summary=application_summary,
    )
    summary = durable_executor_authoring_command_completion_result_after_application.summarize_durable_executor_authoring_command_completion_results_after_application(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_completion_result_after_application_count": 1,
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
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_result_observed_count": 0,
        "no_forbidden_results_count": 0,
        "result_record_valid_count": 0,
        "result_record_rejected_count": 0,
        "unsafe_result_record_count": 0,
        "missing_result_prerequisite_count": 12,
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
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_completion_noop_result_count": 0,
        "reported_application_validation_result_count": 0,
        "reported_completion_completed_result_count": 0,
        "reported_asset_write_result_count": 0,
        "reported_package_dirty_result_count": 0,
        "reported_save_result_count": 0,
        "reported_delete_rename_result_count": 0,
        "reported_cleanup_result_count": 0,
        "reported_code_change_result_count": 0,
        "reported_live_command_result_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_completion_result_after_application_contract",
        "Section 135 durable executor authoring command completion result-after-application contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command completion result-after-application contract is defined, but no application-after-decision record or result record is present.",
            "Result acceptance, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command results remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_result_readback_after_result_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    result_row = build_durable_executor_authoring_command_completion_result_after_application_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    result_summary = dict(result_row["actual"])
    result_summary["status"] = result_summary.pop("summary_status")
    contract = durable_executor_authoring_command_result_readback_after_result.build_durable_executor_authoring_command_result_readback_after_result_contract(
        requested=True,
        completion_result_after_application_summary=result_summary,
    )
    summary = durable_executor_authoring_command_result_readback_after_result.summarize_durable_executor_authoring_command_result_readbacks_after_result(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_result_readback_after_result_count": 1,
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
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_readback_observed_count": 0,
        "no_forbidden_readbacks_count": 0,
        "readback_record_valid_count": 0,
        "readback_record_rejected_count": 0,
        "unsafe_readback_record_count": 0,
        "missing_readback_prerequisite_count": 14,
        "reported_allowed_readback_count": 0,
        "reported_forbidden_readback_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_no_completion_readback_count": 0,
        "reported_no_write_readback_count": 0,
        "reported_no_save_readback_count": 0,
        "reported_completed_readback_count": 0,
        "reported_asset_write_readback_count": 0,
        "reported_package_dirty_readback_count": 0,
        "reported_save_readback_count": 0,
        "reported_delete_rename_readback_count": 0,
        "reported_cleanup_readback_count": 0,
        "reported_code_change_readback_count": 0,
        "reported_live_command_readback_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_result_readback_after_result_contract",
        "Section 136 durable executor authoring command result readback-after-result contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command result readback-after-result contract is defined, but no result-after-application record or readback record is present.",
            "Readback acceptance, final no-save release, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command readbacks remain blocked.",
        ),
    )


def build_durable_executor_authoring_final_no_save_release_after_readback_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readback_row = build_durable_executor_authoring_command_result_readback_after_result_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    readback_summary = dict(readback_row["actual"])
    readback_summary["status"] = readback_summary.pop("summary_status")
    contract = durable_executor_authoring_final_no_save_release_after_readback.build_durable_executor_authoring_final_no_save_release_after_readback_contract(
        requested=True,
        result_readback_after_result_summary=readback_summary,
    )
    summary = durable_executor_authoring_final_no_save_release_after_readback.summarize_durable_executor_authoring_final_no_save_releases_after_readback(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_final_no_save_release_after_readback_count": 1,
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
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_final_no_save_release_observed_count": 0,
        "no_forbidden_final_no_save_releases_count": 0,
        "final_no_save_release_record_valid_count": 0,
        "final_no_save_release_record_rejected_count": 0,
        "unsafe_final_no_save_release_record_count": 0,
        "missing_final_no_save_release_prerequisite_count": 14,
        "reported_allowed_final_no_save_release_count": 0,
        "reported_forbidden_final_no_save_release_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_no_completion_release_count": 0,
        "reported_no_write_release_count": 0,
        "reported_no_save_release_count": 0,
        "reported_readback_revalidated_count": 0,
        "reported_no_code_change_release_count": 0,
        "reported_no_live_command_release_count": 0,
        "reported_completion_release_count": 0,
        "reported_asset_write_release_count": 0,
        "reported_package_dirty_release_count": 0,
        "reported_save_release_count": 0,
        "reported_delete_rename_release_count": 0,
        "reported_cleanup_release_count": 0,
        "reported_durable_authoring_release_count": 0,
        "reported_code_change_release_count": 0,
        "reported_live_command_release_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_final_no_save_release_after_readback_contract",
        "Section 137 durable executor authoring final no-save release-after-readback contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring final no-save release-after-readback contract is defined, but no readback-after-result record or final no-save release record is present.",
            "Final release readiness, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_final_release_readiness_after_no_save_release_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    final_no_save_release_row = (
        build_durable_executor_authoring_final_no_save_release_after_readback_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    final_no_save_release_summary = dict(final_no_save_release_row["actual"])
    final_no_save_release_summary["status"] = final_no_save_release_summary.pop(
        "summary_status"
    )
    contract = durable_executor_authoring_final_release_readiness_after_no_save_release.build_durable_executor_authoring_final_release_readiness_after_no_save_release_contract(
        requested=True,
        final_no_save_release_after_readback_summary=final_no_save_release_summary,
    )
    summary = durable_executor_authoring_final_release_readiness_after_no_save_release.summarize_durable_executor_authoring_final_release_readiness_after_no_save_release(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_final_release_readiness_after_no_save_release_count": 1,
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
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_final_release_readiness_gate_count": 0,
        "reported_final_no_save_release_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_readiness_count": 0,
        "reported_no_write_readiness_count": 0,
        "reported_no_save_readiness_count": 0,
        "reported_no_code_change_readiness_count": 0,
        "reported_no_live_command_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_final_release_readiness_after_no_save_release_contract",
        "Section 138 durable executor authoring final release readiness-after-no-save-release contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring final release readiness-after-no-save-release contract is defined, but no final no-save release-after-readback record or readiness record is present.",
            "Release review, final readiness, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_release_review_after_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readiness_row = (
        build_durable_executor_authoring_final_release_readiness_after_no_save_release_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    readiness_summary = dict(readiness_row["actual"])
    readiness_summary["status"] = readiness_summary.pop("summary_status")
    contract = durable_executor_authoring_release_review_after_readiness.build_durable_executor_authoring_release_review_after_readiness_contract(
        requested=True,
        final_release_readiness_after_no_save_release_summary=readiness_summary,
    )
    summary = durable_executor_authoring_release_review_after_readiness.summarize_durable_executor_authoring_release_reviews_after_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_release_review_after_readiness_count": 1,
        "release_review_contract_defined_count": 1,
        "final_release_readiness_contract_ready_count": 1,
        "final_release_readiness_inputs_satisfied_count": 0,
        "final_release_readiness_record_valid_count": 0,
        "allowed_final_release_readiness_observed_count": 0,
        "no_forbidden_final_release_readiness_claims_count": 0,
        "release_review_inputs_satisfied_count": 0,
        "release_review_record_present_count": 0,
        "record_schema_matches_count": 0,
        "release_review_scope_matches_count": 0,
        "explicit_release_review_authorized_count": 0,
        "release_review_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_release_review_observed_count": 0,
        "no_forbidden_release_review_claims_count": 0,
        "release_review_record_valid_count": 0,
        "release_review_record_rejected_count": 0,
        "unsafe_release_review_record_count": 0,
        "missing_release_review_prerequisite_count": 14,
        "reported_allowed_release_review_count": 0,
        "reported_forbidden_release_review_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_release_review_gate_count": 0,
        "reported_final_release_readiness_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_release_review_count": 0,
        "reported_no_write_release_review_count": 0,
        "reported_no_save_release_review_count": 0,
        "reported_no_code_change_release_review_count": 0,
        "reported_no_live_command_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_review_after_readiness_contract",
        "Section 139 durable executor authoring release review-after-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring release review-after-readiness contract is defined, but no final release readiness-after-no-save-release record or release review record is present.",
            "Release decision, review acceptance, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_release_decision_after_review_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    review_row = build_durable_executor_authoring_release_review_after_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    review_summary = dict(review_row["actual"])
    review_summary["status"] = review_summary.pop("summary_status")
    contract = durable_executor_authoring_release_decision_after_review.build_durable_executor_authoring_release_decision_after_review_contract(
        requested=True,
        release_review_after_readiness_summary=review_summary,
    )
    summary = durable_executor_authoring_release_decision_after_review.summarize_durable_executor_authoring_release_decisions_after_review(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_release_decision_after_review_count": 1,
        "release_decision_contract_defined_count": 1,
        "release_review_contract_ready_count": 1,
        "release_review_inputs_satisfied_count": 0,
        "release_review_record_valid_count": 0,
        "allowed_release_review_observed_count": 0,
        "no_forbidden_release_review_claims_count": 0,
        "release_decision_inputs_satisfied_count": 0,
        "release_decision_record_present_count": 0,
        "record_schema_matches_count": 0,
        "release_decision_scope_matches_count": 0,
        "explicit_release_decision_authorized_count": 0,
        "release_decision_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_release_decision_observed_count": 0,
        "no_forbidden_release_decision_claims_count": 0,
        "release_decision_record_valid_count": 0,
        "release_decision_record_rejected_count": 0,
        "unsafe_release_decision_record_count": 0,
        "missing_release_decision_prerequisite_count": 14,
        "reported_allowed_release_decision_count": 0,
        "reported_forbidden_release_decision_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_release_decision_gate_count": 0,
        "reported_release_review_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_release_decision_count": 0,
        "reported_no_write_release_decision_count": 0,
        "reported_no_save_release_decision_count": 0,
        "reported_no_code_change_release_decision_count": 0,
        "reported_no_live_command_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_decision_after_review_contract",
        "Section 140 durable executor authoring release decision-after-review contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring release decision-after-review contract is defined, but no release review-after-readiness record or decision record is present.",
            "Promotion barrier, release decision acceptance, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_release_promotion_barrier_after_decision_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    decision_row = build_durable_executor_authoring_release_decision_after_review_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    decision_summary = dict(decision_row["actual"])
    decision_summary["status"] = decision_summary.pop("summary_status")
    contract = durable_executor_authoring_release_promotion_barrier_after_decision.build_durable_executor_authoring_release_promotion_barrier_after_decision_contract(
        requested=True,
        release_decision_after_review_summary=decision_summary,
    )
    summary = durable_executor_authoring_release_promotion_barrier_after_decision.summarize_durable_executor_authoring_release_promotion_barriers_after_decision(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_release_promotion_barrier_after_decision_count": 1,
        "release_promotion_barrier_contract_defined_count": 1,
        "release_decision_contract_ready_count": 1,
        "release_decision_inputs_satisfied_count": 0,
        "release_decision_record_valid_count": 0,
        "allowed_release_decision_observed_count": 0,
        "no_forbidden_release_decision_claims_count": 0,
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
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_promotion_barrier_gate_count": 0,
        "reported_release_decision_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_promotion_barrier_count": 0,
        "reported_no_write_promotion_barrier_count": 0,
        "reported_no_save_promotion_barrier_count": 0,
        "reported_no_code_change_promotion_barrier_count": 0,
        "reported_no_live_command_promotion_barrier_count": 0,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_promotion_barrier_after_decision_contract",
        "Section 141 durable executor authoring release promotion barrier-after-decision contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring release promotion barrier-after-decision contract is defined, but no release decision-after-review record or promotion barrier record is present.",
            "Activation readiness, executor activation/open, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_activation_readiness_after_promotion_barrier_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    barrier_row = (
        build_durable_executor_authoring_release_promotion_barrier_after_decision_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    barrier_summary = dict(barrier_row["actual"])
    barrier_summary["status"] = barrier_summary.pop("summary_status")
    contract = durable_executor_authoring_activation_readiness_after_promotion_barrier.build_durable_executor_authoring_activation_readiness_after_promotion_barrier_contract(
        requested=True,
        release_promotion_barrier_after_decision_summary=barrier_summary,
    )
    summary = durable_executor_authoring_activation_readiness_after_promotion_barrier.summarize_durable_executor_authoring_activation_readiness_after_promotion_barrier(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_activation_readiness_after_promotion_barrier_count": 1,
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
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_executor_open_contract_started_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_activation_readiness_gate_count": 0,
        "reported_promotion_barrier_revalidated_count": 0,
        "reported_release_decision_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_activation_readiness_count": 0,
        "reported_no_write_activation_readiness_count": 0,
        "reported_no_save_activation_readiness_count": 0,
        "reported_no_code_change_activation_readiness_count": 0,
        "reported_no_live_command_activation_readiness_count": 0,
        "reported_release_promotion_barrier_count": 0,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_activation_readiness_after_promotion_barrier_contract",
        "Section 142 durable executor authoring activation readiness-after-promotion-barrier contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring activation readiness-after-promotion-barrier contract is defined, but no promotion barrier-after-decision record or activation readiness record is present.",
            "Executor activation/open, durable authoring enablement, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readiness_row = (
        build_durable_executor_authoring_activation_readiness_after_promotion_barrier_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    readiness_summary = dict(readiness_row["actual"])
    readiness_summary["status"] = readiness_summary.pop("summary_status")
    contract = durable_executor_authoring_open_after_activation_readiness.build_durable_executor_authoring_open_after_activation_readiness_contract(
        requested=True,
        activation_readiness_after_promotion_barrier_summary=readiness_summary,
    )
    summary = durable_executor_authoring_open_after_activation_readiness.summarize_durable_executor_authoring_opens_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_open_after_activation_readiness_count": 1,
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
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_executor_open_gate_count": 0,
        "reported_activation_readiness_revalidated_count": 0,
        "reported_promotion_barrier_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_open_count": 0,
        "reported_no_write_open_count": 0,
        "reported_no_save_open_count": 0,
        "reported_no_code_change_open_count": 0,
        "reported_no_live_command_open_count": 0,
        "reported_activation_readiness_count": 0,
        "reported_release_promotion_barrier_count": 0,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_durable_authoring_enable_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_open_after_activation_readiness_contract",
        "Section 143 durable executor authoring open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring open-after-activation-readiness contract is defined, but no activation readiness-after-promotion-barrier record or open record is present.",
            "Executor open/activation, durable authoring enablement, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    open_row = build_durable_executor_authoring_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    open_summary = dict(open_row["actual"])
    open_summary["status"] = open_summary.pop("summary_status")
    contract = durable_executor_authoring_enable_after_open_after_activation_readiness.build_durable_executor_authoring_enable_after_open_after_activation_readiness_contract(
        requested=True,
        open_after_activation_readiness_summary=open_summary,
    )
    summary = durable_executor_authoring_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_enable_after_open_after_activation_readiness_count": 1,
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
        "durable_executor_open_contract_started_count": 0,
        "durable_executor_open_contract_accepted_count": 0,
        "durable_executor_open_performed_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_authoring_enable_gate_count": 0,
        "reported_executor_open_revalidated_count": 0,
        "reported_target_allowlist_reconfirmed_count": 0,
        "reported_overwrite_rename_decision_reconfirmed_count": 0,
        "reported_rollback_readiness_reconfirmed_count": 0,
        "reported_ownership_marker_reconfirmed_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_code_change_authoring_enable_count": 0,
        "reported_no_asset_change_authoring_enable_count": 0,
        "reported_no_live_probe_authoring_enable_count": 0,
        "reported_activation_readiness_count": 0,
        "reported_release_promotion_barrier_count": 0,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_authoring_enable_count": 0,
        "reported_authoring_command_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_enable_after_open_after_activation_readiness_contract",
        "Section 144 durable executor authoring enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring enable-after-open-after-activation-readiness contract is defined, but no open-after-activation-readiness record or enable record is present.",
            "Durable authoring enablement, authoring command start, executor open, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    enable_row = (
        build_durable_executor_authoring_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    enable_summary = dict(enable_row["actual"])
    enable_summary["status"] = enable_summary.pop("summary_status")
    contract = durable_executor_authoring_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        authoring_enable_after_open_after_activation_readiness_summary=enable_summary,
    )
    summary = durable_executor_authoring_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_commands_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_after_enable_after_open_after_activation_readiness_count": 1,
        "authoring_command_contract_defined_count": 1,
        "authoring_enable_contract_ready_count": 1,
        "authoring_enable_inputs_satisfied_count": 0,
        "authoring_enable_record_valid_count": 0,
        "allowed_authoring_enable_observed_count": 0,
        "no_forbidden_authoring_enable_claims_count": 0,
        "target_package_allowlist_reconfirmed_count": 0,
        "overwrite_rename_decision_reconfirmed_count": 0,
        "rollback_readiness_reconfirmed_count": 0,
        "ownership_marker_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_present_count": 0,
        "record_schema_matches_count": 0,
        "command_scope_matches_count": 0,
        "explicit_authoring_command_authorized_count": 0,
        "command_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "planned_authoring_command_count": 0,
        "allowed_authoring_command_count": 0,
        "forbidden_authoring_command_count": 0,
        "unknown_authoring_command_count": 0,
        "authoring_command_record_valid_count": 0,
        "authoring_command_record_rejected_count": 0,
        "unsafe_authoring_command_record_count": 0,
        "missing_authoring_command_prerequisite_count": 17,
        "durable_authoring_command_contract_started_count": 0,
        "durable_authoring_command_contract_accepted_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enable_started_count": 0,
        "durable_authoring_enable_accepted_count": 0,
        "durable_authoring_enable_allowed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 145 durable executor authoring command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command-after-enable-after-open-after-activation-readiness contract is defined, but no enable-after-open-after-activation-readiness record or command record is present.",
            "Authoring command allow/dispatch/execution, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    command_row = (
        build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    command_summary = dict(command_row["actual"])
    command_summary["status"] = command_summary.pop("summary_status")
    contract = durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        authoring_command_after_enable_after_open_after_activation_readiness_summary=command_summary,
    )
    summary = durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_command_dispatches_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
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
        "dispatch_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_dispatch_observed_count": 0,
        "no_forbidden_dispatch_claims_count": 0,
        "dispatch_record_valid_count": 0,
        "dispatch_record_rejected_count": 0,
        "unsafe_dispatch_record_count": 0,
        "missing_dispatch_prerequisite_count": 14,
        "reported_allowed_dispatch_count": 0,
        "reported_forbidden_dispatch_count": 0,
        "durable_authoring_command_dispatch_started_count": 0,
        "durable_authoring_command_dispatch_accepted_count": 0,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_contract_started_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_command_contract_started_count": 0,
        "durable_authoring_command_contract_accepted_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "reported_dispatch_gate_count": 0,
        "reported_authoring_command_revalidated_count": 0,
        "reported_no_live_dispatch_performed_count": 0,
        "reported_no_execution_authorized_count": 0,
        "reported_no_asset_write_dispatch_count": 0,
        "reported_no_save_delete_rename_dispatch_count": 0,
        "reported_authoring_command_dispatch_count": 0,
        "reported_authoring_command_execution_count": 0,
        "reported_live_dispatch_count": 0,
        "reported_live_execution_count": 0,
        "reported_code_change_count": 0,
        "reported_executor_code_modified_count": 0,
        "reported_unreal_asset_change_count": 0,
        "reported_live_probe_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 146 durable executor authoring command dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no command-after-enable-after-open-after-activation-readiness record or dispatch record is present.",
            "Command dispatch/execution, live dispatch/execution, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    dispatch_row = build_durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    dispatch_summary = dict(dispatch_row["actual"])
    dispatch_summary["status"] = dispatch_summary.pop("summary_status")
    contract = durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        command_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary=dispatch_summary,
    )
    summary = durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_command_executions_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
        "execution_contract_defined_count": 1,
        "dispatch_contract_ready_count": 1,
        "dispatch_inputs_satisfied_count": 0,
        "dispatch_record_valid_count": 0,
        "planned_authoring_commands_present_count": 0,
        "allowed_authoring_commands_present_count": 0,
        "allowed_dispatch_observed_count": 0,
        "no_forbidden_dispatch_claims_count": 0,
        "execution_inputs_satisfied_count": 0,
        "execution_record_present_count": 0,
        "record_schema_matches_count": 0,
        "execution_scope_matches_count": 0,
        "explicit_execution_authorized_count": 0,
        "execution_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_execution_observed_count": 0,
        "no_forbidden_execution_claims_count": 0,
        "execution_record_valid_count": 0,
        "execution_record_rejected_count": 0,
        "unsafe_execution_record_count": 0,
        "missing_execution_prerequisite_count": 16,
        "reported_allowed_execution_count": 0,
        "reported_forbidden_execution_count": 0,
        "durable_authoring_command_execution_started_count": 0,
        "durable_authoring_command_execution_accepted_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_command_execution_evidence_contract_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "reported_execution_gate_count": 0,
        "reported_dispatch_revalidated_count": 0,
        "reported_no_live_execution_performed_count": 0,
        "reported_no_execution_evidence_admitted_count": 0,
        "reported_no_asset_write_execution_count": 0,
        "reported_no_save_delete_rename_execution_count": 0,
        "reported_authoring_command_execution_count": 0,
        "reported_execution_evidence_count": 0,
        "reported_live_execution_count": 0,
        "reported_live_dispatch_count": 0,
        "reported_code_change_count": 0,
        "reported_executor_code_modified_count": 0,
        "reported_unreal_asset_change_count": 0,
        "reported_live_probe_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 147 durable executor authoring command execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no dispatch-after-command-after-enable-after-open-after-activation-readiness record or execution record is present.",
            "Command execution, execution evidence admission, live dispatch/execution, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live probes remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    execution_row = build_durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    execution_summary = dict(execution_row["actual"])
    execution_summary["status"] = execution_summary.pop("summary_status")
    contract = durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary=execution_summary,
    )
    summary = durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
        "evidence_contract_defined_count": 1,
        "execution_contract_ready_count": 1,
        "execution_inputs_satisfied_count": 0,
        "execution_record_valid_count": 0,
        "planned_authoring_commands_present_count": 0,
        "allowed_authoring_commands_present_count": 0,
        "allowed_execution_observed_count": 0,
        "no_forbidden_execution_claims_count": 0,
        "evidence_inputs_satisfied_count": 0,
        "evidence_record_present_count": 0,
        "record_schema_matches_count": 0,
        "evidence_scope_matches_count": 0,
        "explicit_evidence_authorized_count": 0,
        "evidence_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_evidence_command_observed_count": 0,
        "no_forbidden_evidence_commands_count": 0,
        "authoring_command_execution_evidence_admitted_count": 0,
        "evidence_record_rejected_count": 0,
        "unsafe_evidence_record_count": 0,
        "missing_evidence_prerequisite_count": 16,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
        "durable_authoring_command_completion_decision_started_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "reported_package_dirty_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 148 durable executor authoring command execution evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command execution evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness record or evidence record is present.",
            "Evidence admission, completion decision, live dispatch/execution, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live probes remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    evidence_row = build_durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    evidence_summary = dict(evidence_row["actual"])
    evidence_summary["status"] = evidence_summary.pop("summary_status")
    contract = durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary=evidence_summary,
    )
    summary = durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_command_completion_decisions_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
        "completion_decision_contract_defined_count": 1,
        "evidence_contract_ready_count": 1,
        "authoring_command_execution_evidence_admitted_count": 0,
        "allowed_evidence_command_observed_count": 0,
        "no_forbidden_evidence_commands_count": 0,
        "evidence_ready_for_completion_count": 0,
        "decision_record_present_count": 0,
        "record_schema_matches_count": 0,
        "completion_scope_matches_count": 0,
        "explicit_completion_decision_authorized_count": 0,
        "completion_decision_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "completion_decision_record_valid_count": 0,
        "completion_decision_record_rejected_count": 0,
        "unsafe_completion_decision_record_count": 0,
        "missing_completion_prerequisite_count": 11,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
        "durable_authoring_command_completion_allowed_count": 0,
        "durable_authoring_command_completed_count": 0,
        "durable_authoring_command_completion_application_started_count": 0,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
        "durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 149 durable executor authoring command completion decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command completion decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness record or completion decision record is present.",
            "Completion allowance, completion execution, completion application, live dispatch/execution, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live probes remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    decision_row = build_durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    decision_summary = dict(decision_row["actual"])
    decision_summary["status"] = decision_summary.pop("summary_status")
    contract = durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary=decision_summary,
    )
    summary = durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_command_completion_applications_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
        "application_contract_defined_count": 1,
        "completion_decision_contract_ready_count": 1,
        "evidence_ready_for_completion_count": 0,
        "completion_decision_record_valid_count": 0,
        "application_inputs_satisfied_count": 0,
        "application_record_present_count": 0,
        "record_schema_matches_count": 0,
        "application_scope_matches_count": 0,
        "explicit_application_authorized_count": 0,
        "application_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "application_record_valid_count": 0,
        "application_record_rejected_count": 0,
        "unsafe_application_record_count": 0,
        "missing_application_prerequisite_count": 10,
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
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
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
        "durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 150 durable executor authoring command completion application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command completion application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no completion decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness record or application record is present.",
            "Completion application, asset write allowance, package dirty marking, live dispatch/execution, save, delete/rename, cleanup, code changes, and live probes remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    application_row = build_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    application_summary = dict(application_row["actual"])
    application_summary["status"] = application_summary.pop("summary_status")
    contract = durable_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary=application_summary,
    )
    summary = durable_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_command_completion_results_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
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
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_result_observed_count": 0,
        "no_forbidden_results_count": 0,
        "result_record_valid_count": 0,
        "result_record_rejected_count": 0,
        "unsafe_result_record_count": 0,
        "missing_result_prerequisite_count": 12,
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
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_completion_noop_result_count": 0,
        "reported_application_validation_result_count": 0,
        "reported_completion_completed_result_count": 0,
        "reported_asset_write_result_count": 0,
        "reported_package_dirty_result_count": 0,
        "reported_save_result_count": 0,
        "reported_delete_rename_result_count": 0,
        "reported_cleanup_result_count": 0,
        "reported_code_change_result_count": 0,
        "reported_live_command_result_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 151 durable executor authoring command completion result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command completion result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness record or result record is present.",
            "Result acceptance, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command results remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    result_row = build_durable_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    result_summary = dict(result_row["actual"])
    result_summary["status"] = result_summary.pop("summary_status")
    contract = durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary=result_summary,
    )
    summary = durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_command_result_readbacks_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
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
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_readback_observed_count": 0,
        "no_forbidden_readbacks_count": 0,
        "readback_record_valid_count": 0,
        "readback_record_rejected_count": 0,
        "unsafe_readback_record_count": 0,
        "missing_readback_prerequisite_count": 14,
        "reported_allowed_readback_count": 0,
        "reported_forbidden_readback_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_no_completion_readback_count": 0,
        "reported_no_write_readback_count": 0,
        "reported_no_save_readback_count": 0,
        "reported_completed_readback_count": 0,
        "reported_asset_write_readback_count": 0,
        "reported_package_dirty_readback_count": 0,
        "reported_save_readback_count": 0,
        "reported_delete_rename_readback_count": 0,
        "reported_cleanup_readback_count": 0,
        "reported_code_change_readback_count": 0,
        "reported_live_command_readback_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 152 durable executor authoring command result readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command result readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no completion result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness record or readback record is present.",
            "Readback acceptance, final no-save release, completion, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command readbacks remain blocked.",
        ),
    )


def build_durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readback_row = build_durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    readback_summary = dict(readback_row["actual"])
    readback_summary["status"] = readback_summary.pop("summary_status")
    contract = durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary=readback_summary,
    )
    summary = durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_final_no_save_releases_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
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
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_final_no_save_release_observed_count": 0,
        "no_forbidden_final_no_save_releases_count": 0,
        "final_no_save_release_record_valid_count": 0,
        "final_no_save_release_record_rejected_count": 0,
        "unsafe_final_no_save_release_record_count": 0,
        "missing_final_no_save_release_prerequisite_count": 14,
        "reported_allowed_final_no_save_release_count": 0,
        "reported_forbidden_final_no_save_release_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_no_completion_release_count": 0,
        "reported_no_write_release_count": 0,
        "reported_no_save_release_count": 0,
        "reported_readback_revalidated_count": 0,
        "reported_no_code_change_release_count": 0,
        "reported_no_live_command_release_count": 0,
        "reported_completion_release_count": 0,
        "reported_asset_write_release_count": 0,
        "reported_package_dirty_release_count": 0,
        "reported_save_release_count": 0,
        "reported_delete_rename_release_count": 0,
        "reported_cleanup_release_count": 0,
        "reported_durable_authoring_release_count": 0,
        "reported_code_change_release_count": 0,
        "reported_live_command_release_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 153 durable executor authoring final no-save release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring final no-save release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no result readback record or final no-save release record is present.",
            "Final release readiness, completion acceptance, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    final_no_save_release_row = (
        build_durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    final_no_save_release_summary = dict(final_no_save_release_row["actual"])
    final_no_save_release_summary["status"] = final_no_save_release_summary.pop(
        "summary_status"
    )
    contract = durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary=final_no_save_release_summary,
    )
    summary = durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
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
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_final_release_readiness_gate_count": 0,
        "reported_final_no_save_release_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_readiness_count": 0,
        "reported_no_write_readiness_count": 0,
        "reported_no_save_readiness_count": 0,
        "reported_no_code_change_readiness_count": 0,
        "reported_no_live_command_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 154 durable executor authoring final release readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring final release readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no final no-save release record or readiness record is present.",
            "Release review, final readiness, completion acceptance, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readiness_row = build_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    readiness_summary = dict(readiness_row["actual"])
    readiness_summary["status"] = readiness_summary.pop("summary_status")
    contract = durable_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary=readiness_summary,
    )
    summary = durable_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_release_reviews_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
        "release_review_contract_defined_count": 1,
        "final_release_readiness_contract_ready_count": 1,
        "final_release_readiness_inputs_satisfied_count": 0,
        "final_release_readiness_record_valid_count": 0,
        "allowed_final_release_readiness_observed_count": 0,
        "no_forbidden_final_release_readiness_claims_count": 0,
        "release_review_inputs_satisfied_count": 0,
        "release_review_record_present_count": 0,
        "record_schema_matches_count": 0,
        "release_review_scope_matches_count": 0,
        "explicit_release_review_authorized_count": 0,
        "release_review_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_release_review_observed_count": 0,
        "no_forbidden_release_review_claims_count": 0,
        "release_review_record_valid_count": 0,
        "release_review_record_rejected_count": 0,
        "unsafe_release_review_record_count": 0,
        "missing_release_review_prerequisite_count": 14,
        "reported_allowed_release_review_count": 0,
        "reported_forbidden_release_review_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_release_review_gate_count": 0,
        "reported_final_release_readiness_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_release_review_count": 0,
        "reported_no_write_release_review_count": 0,
        "reported_no_save_release_review_count": 0,
        "reported_no_code_change_release_review_count": 0,
        "reported_no_live_command_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 155 durable executor authoring release review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring release review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no final release readiness record or release review record is present.",
            "Release review acceptance, release decision, final readiness, completion acceptance, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    review_row = build_durable_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    review_summary = dict(review_row["actual"])
    review_summary["status"] = review_summary.pop("summary_status")
    contract = durable_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary=review_summary,
    )
    summary = durable_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_release_decisions_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
        "release_decision_contract_defined_count": 1,
        "release_review_contract_ready_count": 1,
        "release_review_inputs_satisfied_count": 0,
        "release_review_record_valid_count": 0,
        "allowed_release_review_observed_count": 0,
        "no_forbidden_release_review_claims_count": 0,
        "release_decision_inputs_satisfied_count": 0,
        "release_decision_record_present_count": 0,
        "record_schema_matches_count": 0,
        "release_decision_scope_matches_count": 0,
        "explicit_release_decision_authorized_count": 0,
        "release_decision_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_release_decision_observed_count": 0,
        "no_forbidden_release_decision_claims_count": 0,
        "release_decision_record_valid_count": 0,
        "release_decision_record_rejected_count": 0,
        "unsafe_release_decision_record_count": 0,
        "missing_release_decision_prerequisite_count": 14,
        "reported_allowed_release_decision_count": 0,
        "reported_forbidden_release_decision_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_release_decision_gate_count": 0,
        "reported_release_review_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_release_decision_count": 0,
        "reported_no_write_release_decision_count": 0,
        "reported_no_save_release_decision_count": 0,
        "reported_no_code_change_release_decision_count": 0,
        "reported_no_live_command_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 156 durable executor authoring release decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring release decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no release review record or release decision record is present.",
            "Release decision acceptance, promotion barrier, release review, final readiness, completion acceptance, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    decision_row = build_durable_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    decision_summary = dict(decision_row["actual"])
    decision_summary["status"] = decision_summary.pop("summary_status")
    contract = durable_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        requested=True,
        release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary=decision_summary,
    )
    summary = durable_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_release_promotion_barriers_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
        "release_promotion_barrier_contract_defined_count": 1,
        "release_decision_contract_ready_count": 1,
        "release_decision_inputs_satisfied_count": 0,
        "release_decision_record_valid_count": 0,
        "allowed_release_decision_observed_count": 0,
        "no_forbidden_release_decision_claims_count": 0,
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
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_promotion_barrier_gate_count": 0,
        "reported_release_decision_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_promotion_barrier_count": 0,
        "reported_no_write_promotion_barrier_count": 0,
        "reported_no_save_promotion_barrier_count": 0,
        "reported_no_code_change_promotion_barrier_count": 0,
        "reported_no_live_command_promotion_barrier_count": 0,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 157 durable executor authoring release promotion barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring release promotion barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no release decision record or promotion barrier record is present.",
            "Activation readiness, executor activation/open, durable authoring enablement, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    promotion_barrier_row = build_durable_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    promotion_barrier_summary = dict(promotion_barrier_row["actual"])
    promotion_barrier_summary["status"] = promotion_barrier_summary.pop("summary_status")
    contract = durable_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_activation_readiness_after_promotion_barrier_after_activation_readiness_contract(
        requested=True,
        release_promotion_barrier_after_decision_summary=promotion_barrier_summary,
    )
    summary = durable_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_activation_readiness_after_promotion_barrier_after_activation_readiness(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
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
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_executor_open_contract_started_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_activation_readiness_gate_count": 0,
        "reported_promotion_barrier_revalidated_count": 0,
        "reported_release_decision_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_activation_readiness_count": 0,
        "reported_no_write_activation_readiness_count": 0,
        "reported_no_save_activation_readiness_count": 0,
        "reported_no_code_change_activation_readiness_count": 0,
        "reported_no_live_command_activation_readiness_count": 0,
        "reported_release_promotion_barrier_count": 0,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 158 durable executor authoring activation readiness-after-promotion-barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring activation readiness-after-promotion-barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no promotion barrier record or activation readiness record is present.",
            "Activation readiness start/acceptance, executor activation/open, durable authoring enablement, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readiness_row = build_durable_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    readiness_summary = dict(readiness_row["actual"])
    readiness_summary["status"] = readiness_summary.pop("summary_status")
    contract = durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_contract(
        requested=True,
        activation_readiness_after_promotion_barrier_summary=readiness_summary,
    )
    summary = durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_opens_after_activation_readiness_after_promotion_barrier(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
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
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_executor_open_gate_count": 0,
        "reported_activation_readiness_revalidated_count": 0,
        "reported_promotion_barrier_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_open_count": 0,
        "reported_no_write_open_count": 0,
        "reported_no_save_open_count": 0,
        "reported_no_code_change_open_count": 0,
        "reported_no_live_command_open_count": 0,
        "reported_activation_readiness_count": 0,
        "reported_release_promotion_barrier_count": 0,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_durable_authoring_enable_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 159 durable executor authoring open-after-activation-readiness-after-promotion-barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring open-after-activation-readiness-after-promotion-barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no activation readiness record or open record is present.",
            "Executor open/activation, durable authoring enablement, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    open_row = build_durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    open_summary = dict(open_row["actual"])
    open_summary["status"] = open_summary.pop("summary_status")
    contract = durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_contract(
        requested=True,
        open_after_activation_readiness_summary=open_summary,
    )
    summary = durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
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
        "durable_executor_open_contract_started_count": 0,
        "durable_executor_open_contract_accepted_count": 0,
        "durable_executor_open_performed_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_authoring_enable_gate_count": 0,
        "reported_executor_open_revalidated_count": 0,
        "reported_target_allowlist_reconfirmed_count": 0,
        "reported_overwrite_rename_decision_reconfirmed_count": 0,
        "reported_rollback_readiness_reconfirmed_count": 0,
        "reported_ownership_marker_reconfirmed_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_code_change_authoring_enable_count": 0,
        "reported_no_asset_change_authoring_enable_count": 0,
        "reported_no_live_probe_authoring_enable_count": 0,
        "reported_activation_readiness_count": 0,
        "reported_release_promotion_barrier_count": 0,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_authoring_enable_count": 0,
        "reported_authoring_command_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 160 durable executor authoring enable-after-open-after-activation-readiness-after-promotion-barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring enable-after-open-after-activation-readiness-after-promotion-barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no open record or authoring enable record is present.",
            "Durable authoring enablement, command start, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    enable_row = build_durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    enable_summary = dict(enable_row["actual"])
    enable_summary["status"] = enable_summary.pop("summary_status")
    contract = durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_contract(
        requested=True,
        authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_summary=enable_summary,
    )
    summary = durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness.summarize_durable_executor_authoring_commands_after_enable_after_open_after_activation_readiness_after_promotion_barrier(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
        "authoring_command_contract_defined_count": 1,
        "authoring_enable_contract_ready_count": 1,
        "open_inputs_satisfied_count": 0,
        "open_record_valid_count": 0,
        "allowed_open_observed_count": 0,
        "no_forbidden_open_claims_count": 0,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_inputs_satisfied_count": 0,
        "authoring_enable_record_valid_count": 0,
        "allowed_authoring_enable_observed_count": 0,
        "no_forbidden_authoring_enable_claims_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "target_package_allowlist_reconfirmed_count": 0,
        "overwrite_rename_decision_reconfirmed_count": 0,
        "rollback_readiness_reconfirmed_count": 0,
        "ownership_marker_reconfirmed_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_present_count": 0,
        "record_schema_matches_count": 0,
        "command_scope_matches_count": 0,
        "explicit_authoring_command_authorized_count": 0,
        "command_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "planned_authoring_command_count": 0,
        "allowed_authoring_command_count": 0,
        "forbidden_authoring_command_count": 0,
        "unknown_authoring_command_count": 0,
        "authoring_command_record_valid_count": 0,
        "authoring_command_record_rejected_count": 0,
        "unsafe_authoring_command_record_count": 0,
        "missing_authoring_command_prerequisite_count": 21,
        "durable_authoring_command_contract_started_count": 0,
        "durable_authoring_command_contract_accepted_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enable_started_count": 0,
        "durable_authoring_enable_accepted_count": 0,
        "durable_authoring_enable_allowed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "durable_executor_open_contract_started_count": 0,
        "durable_executor_open_contract_accepted_count": 0,
        "durable_executor_open_performed_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
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
        "durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        "Section 161 durable executor authoring command-after-enable-after-open-after-activation-readiness-after-promotion-barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command-after-enable-after-open-after-activation-readiness-after-promotion-barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract is defined, but no open record, authoring enable record, or command record is present.",
            "Durable command path opening, command allowance, dispatch/execution, asset writes, dirty marking, save, delete/rename, cleanup, code changes, and live command execution remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_request_dry_run_route_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    command_row = build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    command_summary = dict(command_row["actual"])
    command_summary["status"] = command_summary.pop("summary_status")
    contract = durable_executor_authoring_command_request_dry_run_route.build_durable_executor_authoring_command_request_dry_run_route_contract(
        requested=True,
        section_161_authoring_command_summary=command_summary,
    )
    summary = durable_executor_authoring_command_request_dry_run_route.summarize_durable_executor_authoring_command_request_dry_run_routes(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_request_dry_run_route_count": 1,
        "route_contract_defined_count": 1,
        "section_161_command_contract_ready_count": 1,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "readiness_chain_satisfied_count": 0,
        "dry_run_route_record_present_count": 0,
        "record_schema_matches_count": 0,
        "route_scope_matches_count": 0,
        "dry_run_only_count": 0,
        "route_status_passed_count": 0,
        "operator_reconfirmed_no_write_execution_count": 0,
        "operator_reconfirmed_no_save_delete_rename_count": 0,
        "requested_command_allowed_count": 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
        "dry_run_operation_allowed_count": 0,
        "target_asset_declared_count": 0,
        "readiness_proof_matches_count": 0,
        "release_boundary_proof_safe_count": 0,
        "dry_run_route_record_valid_count": 0,
        "dry_run_route_record_rejected_count": 0,
        "dry_run_route_admissible_count": 0,
        "unsafe_request_record_count": 0,
        "missing_dry_run_route_prerequisite_count": 17,
        "dry_run_route_request_started_count": 0,
        "dry_run_route_request_accepted_count": 0,
        "durable_command_request_promoted_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_request_dry_run_route_contract",
        "Section 162 durable executor authoring command request dry-run route contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command request dry-run route contract is defined, but no command request route record is present and the readiness chain remains incomplete.",
            "A future valid request can become dry-run admissible only; durable command promotion, command path opening, dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_dispatch_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    route_row = build_durable_executor_authoring_command_request_dry_run_route_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    route_summary = dict(route_row["actual"])
    route_summary["status"] = route_summary.pop("summary_status")
    contract = durable_executor_authoring_command_dispatch_dry_run.build_durable_executor_authoring_command_dispatch_dry_run_contract(
        requested=True,
        section_162_command_request_route_summary=route_summary,
    )
    summary = durable_executor_authoring_command_dispatch_dry_run.summarize_durable_executor_authoring_command_dispatch_dry_runs(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_dispatch_dry_run_count": 1,
        "dispatch_contract_defined_count": 1,
        "section_162_route_contract_ready_count": 1,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "dry_run_route_record_valid_count": 0,
        "dry_run_route_admissible_count": 0,
        "route_chain_satisfied_count": 0,
        "dispatch_dry_run_record_present_count": 0,
        "record_schema_matches_count": 0,
        "dispatch_scope_matches_count": 0,
        "dry_run_only_count": 0,
        "dispatch_status_passed_count": 0,
        "operator_reconfirmed_no_live_dispatch_count": 0,
        "operator_reconfirmed_no_write_execution_count": 0,
        "operator_reconfirmed_no_save_delete_rename_count": 0,
        "requested_command_allowed_count": 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
        "dispatch_operation_allowed_count": 0,
        "dispatch_envelope_target_declared_count": 0,
        "route_admission_proof_matches_count": 0,
        "release_boundary_proof_safe_count": 0,
        "dispatch_dry_run_record_valid_count": 0,
        "dispatch_dry_run_record_rejected_count": 0,
        "dispatch_dry_run_admissible_count": 0,
        "unsafe_dispatch_record_count": 0,
        "missing_dispatch_dry_run_prerequisite_count": 20,
        "dispatch_dry_run_started_count": 0,
        "dispatch_dry_run_accepted_count": 0,
        "durable_dispatch_envelope_promoted_count": 0,
        "durable_command_request_promoted_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_dispatch_dry_run_contract",
        "Section 163 durable executor authoring command dispatch dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command dispatch dry-run contract is defined, but no dispatch record is present and the Section 162 dry-run route is not admissible.",
            "A future valid dispatch record can become dry-run admissible only; durable dispatch envelope promotion, live dispatch/execution, command path opening, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_dispatch_evidence_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    dispatch_row = build_durable_executor_authoring_command_dispatch_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    dispatch_summary = dict(dispatch_row["actual"])
    dispatch_summary["status"] = dispatch_summary.pop("summary_status")
    contract = durable_executor_authoring_command_dispatch_evidence_dry_run.build_durable_executor_authoring_command_dispatch_evidence_dry_run_contract(
        requested=True,
        section_163_command_dispatch_dry_run_summary=dispatch_summary,
    )
    summary = durable_executor_authoring_command_dispatch_evidence_dry_run.summarize_durable_executor_authoring_command_dispatch_evidence_dry_runs(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_dispatch_evidence_dry_run_count": 1,
        "dispatch_evidence_contract_defined_count": 1,
        "section_163_dispatch_contract_ready_count": 1,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "dry_run_route_record_valid_count": 0,
        "dry_run_route_admissible_count": 0,
        "dispatch_dry_run_record_valid_count": 0,
        "dispatch_dry_run_admissible_count": 0,
        "dispatch_chain_satisfied_count": 0,
        "dispatch_evidence_dry_run_record_present_count": 0,
        "record_schema_matches_count": 0,
        "evidence_scope_matches_count": 0,
        "dry_run_only_count": 0,
        "evidence_status_passed_count": 0,
        "operator_reconfirmed_no_live_dispatch_count": 0,
        "operator_reconfirmed_no_live_execution_count": 0,
        "operator_reconfirmed_no_write_execution_count": 0,
        "operator_reconfirmed_no_save_delete_rename_count": 0,
        "requested_command_allowed_count": 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
        "evidence_operation_allowed_count": 0,
        "dispatch_evidence_target_declared_count": 0,
        "dispatch_admission_proof_matches_count": 0,
        "release_boundary_proof_safe_count": 0,
        "dispatch_evidence_dry_run_record_valid_count": 0,
        "dispatch_evidence_dry_run_record_rejected_count": 0,
        "dispatch_evidence_dry_run_admissible_count": 0,
        "unsafe_evidence_record_count": 0,
        "missing_dispatch_evidence_dry_run_prerequisite_count": 23,
        "dispatch_evidence_dry_run_started_count": 0,
        "dispatch_evidence_dry_run_accepted_count": 0,
        "durable_evidence_promoted_count": 0,
        "durable_dispatch_envelope_promoted_count": 0,
        "durable_command_request_promoted_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_dispatch_evidence_dry_run_contract",
        "Section 164 durable executor authoring command dispatch evidence dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command dispatch evidence dry-run contract is defined, but no dispatch evidence record is present and the Section 163 dispatch dry-run is not admissible.",
            "A future valid dispatch evidence record can become dry-run admissible only; durable evidence promotion, live dispatch/execution, command path opening, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_execution_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    evidence_row = build_durable_executor_authoring_command_dispatch_evidence_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    evidence_summary = dict(evidence_row["actual"])
    evidence_summary["status"] = evidence_summary.pop("summary_status")
    contract = durable_executor_authoring_command_execution_dry_run.build_durable_executor_authoring_command_execution_dry_run_contract(
        requested=True,
        section_164_command_dispatch_evidence_dry_run_summary=evidence_summary,
    )
    summary = durable_executor_authoring_command_execution_dry_run.summarize_durable_executor_authoring_command_execution_dry_runs(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_execution_dry_run_count": 1,
        "execution_contract_defined_count": 1,
        "section_164_dispatch_evidence_contract_ready_count": 1,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "dry_run_route_record_valid_count": 0,
        "dry_run_route_admissible_count": 0,
        "dispatch_dry_run_record_valid_count": 0,
        "dispatch_dry_run_admissible_count": 0,
        "dispatch_evidence_dry_run_record_valid_count": 0,
        "dispatch_evidence_dry_run_admissible_count": 0,
        "evidence_chain_satisfied_count": 0,
        "execution_dry_run_record_present_count": 0,
        "record_schema_matches_count": 0,
        "execution_scope_matches_count": 0,
        "dry_run_only_count": 0,
        "execution_status_passed_count": 0,
        "operator_reconfirmed_no_live_dispatch_count": 0,
        "operator_reconfirmed_no_live_execution_count": 0,
        "operator_reconfirmed_no_write_execution_count": 0,
        "operator_reconfirmed_no_save_delete_rename_count": 0,
        "requested_command_allowed_count": 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
        "execution_operation_allowed_count": 0,
        "execution_target_declared_count": 0,
        "dispatch_evidence_admission_proof_matches_count": 0,
        "release_boundary_proof_safe_count": 0,
        "execution_dry_run_record_valid_count": 0,
        "execution_dry_run_record_rejected_count": 0,
        "execution_dry_run_admissible_count": 0,
        "unsafe_execution_record_count": 0,
        "missing_execution_dry_run_prerequisite_count": 25,
        "execution_dry_run_started_count": 0,
        "execution_dry_run_accepted_count": 0,
        "durable_execution_envelope_promoted_count": 0,
        "durable_evidence_promoted_count": 0,
        "durable_dispatch_envelope_promoted_count": 0,
        "durable_command_request_promoted_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_execution_dry_run_contract",
        "Section 165 durable executor authoring command execution dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command execution dry-run contract is defined, but no execution record is present and the Section 164 dispatch evidence dry-run is not admissible.",
            "A future valid execution record can become dry-run admissible only; durable execution envelope promotion, live dispatch/execution, command path opening, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_execution_evidence_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    execution_row = build_durable_executor_authoring_command_execution_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    execution_summary = dict(execution_row["actual"])
    execution_summary["status"] = execution_summary.pop("summary_status")
    contract = durable_executor_authoring_command_execution_evidence_dry_run.build_durable_executor_authoring_command_execution_evidence_dry_run_contract(
        requested=True,
        section_165_command_execution_dry_run_summary=execution_summary,
    )
    summary = durable_executor_authoring_command_execution_evidence_dry_run.summarize_durable_executor_authoring_command_execution_evidence_dry_runs(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_execution_evidence_dry_run_count": 1,
        "execution_evidence_contract_defined_count": 1,
        "section_165_execution_contract_ready_count": 1,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "dry_run_route_record_valid_count": 0,
        "dry_run_route_admissible_count": 0,
        "dispatch_dry_run_record_valid_count": 0,
        "dispatch_dry_run_admissible_count": 0,
        "dispatch_evidence_dry_run_record_valid_count": 0,
        "dispatch_evidence_dry_run_admissible_count": 0,
        "execution_dry_run_record_valid_count": 0,
        "execution_dry_run_admissible_count": 0,
        "execution_chain_satisfied_count": 0,
        "execution_evidence_dry_run_record_present_count": 0,
        "record_schema_matches_count": 0,
        "execution_evidence_scope_matches_count": 0,
        "dry_run_only_count": 0,
        "execution_evidence_status_passed_count": 0,
        "operator_reconfirmed_no_live_dispatch_count": 0,
        "operator_reconfirmed_no_live_execution_count": 0,
        "operator_reconfirmed_no_write_execution_count": 0,
        "operator_reconfirmed_no_save_delete_rename_count": 0,
        "requested_command_allowed_count": 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
        "execution_evidence_operation_allowed_count": 0,
        "execution_evidence_target_declared_count": 0,
        "execution_admission_proof_matches_count": 0,
        "release_boundary_proof_safe_count": 0,
        "execution_evidence_dry_run_record_valid_count": 0,
        "execution_evidence_dry_run_record_rejected_count": 0,
        "execution_evidence_dry_run_admissible_count": 0,
        "unsafe_execution_evidence_record_count": 0,
        "missing_execution_evidence_dry_run_prerequisite_count": 27,
        "execution_evidence_dry_run_started_count": 0,
        "execution_evidence_dry_run_accepted_count": 0,
        "durable_execution_evidence_promoted_count": 0,
        "durable_execution_envelope_promoted_count": 0,
        "durable_evidence_promoted_count": 0,
        "durable_dispatch_envelope_promoted_count": 0,
        "durable_command_request_promoted_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_execution_evidence_dry_run_contract",
        "Section 166 durable executor authoring command execution evidence dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command execution evidence dry-run contract is defined, but no execution evidence record is present and the Section 165 execution dry-run is not admissible.",
            "A future valid execution evidence record can become dry-run admissible only; durable execution evidence promotion, live dispatch/execution, command path opening, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_completion_decision_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    evidence_row = build_durable_executor_authoring_command_execution_evidence_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    evidence_summary = dict(evidence_row["actual"])
    evidence_summary["status"] = evidence_summary.pop("summary_status")
    contract = durable_executor_authoring_command_completion_decision_dry_run.build_durable_executor_authoring_command_completion_decision_dry_run_contract(
        requested=True,
        section_166_command_execution_evidence_dry_run_summary=evidence_summary,
    )
    summary = durable_executor_authoring_command_completion_decision_dry_run.summarize_durable_executor_authoring_command_completion_decision_dry_runs(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_completion_decision_dry_run_count": 1,
        "completion_decision_contract_defined_count": 1,
        "section_166_execution_evidence_contract_ready_count": 1,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "dry_run_route_record_valid_count": 0,
        "dry_run_route_admissible_count": 0,
        "dispatch_dry_run_record_valid_count": 0,
        "dispatch_dry_run_admissible_count": 0,
        "dispatch_evidence_dry_run_record_valid_count": 0,
        "dispatch_evidence_dry_run_admissible_count": 0,
        "execution_dry_run_record_valid_count": 0,
        "execution_dry_run_admissible_count": 0,
        "execution_evidence_dry_run_record_valid_count": 0,
        "execution_evidence_dry_run_admissible_count": 0,
        "execution_evidence_chain_satisfied_count": 0,
        "completion_decision_dry_run_record_present_count": 0,
        "record_schema_matches_count": 0,
        "completion_decision_scope_matches_count": 0,
        "dry_run_only_count": 0,
        "completion_decision_status_passed_count": 0,
        "operator_reconfirmed_no_live_dispatch_count": 0,
        "operator_reconfirmed_no_live_execution_count": 0,
        "operator_reconfirmed_no_write_execution_count": 0,
        "operator_reconfirmed_no_save_delete_rename_count": 0,
        "requested_command_allowed_count": 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
        "completion_decision_operation_allowed_count": 0,
        "completion_decision_target_declared_count": 0,
        "execution_evidence_admission_proof_matches_count": 0,
        "release_boundary_proof_safe_count": 0,
        "completion_decision_dry_run_record_valid_count": 0,
        "completion_decision_dry_run_record_rejected_count": 0,
        "completion_decision_dry_run_admissible_count": 0,
        "unsafe_completion_decision_record_count": 0,
        "missing_completion_decision_dry_run_prerequisite_count": 29,
        "completion_decision_dry_run_started_count": 0,
        "completion_decision_dry_run_accepted_count": 0,
        "durable_completion_decision_promoted_count": 0,
        "durable_execution_evidence_promoted_count": 0,
        "durable_execution_envelope_promoted_count": 0,
        "durable_evidence_promoted_count": 0,
        "durable_dispatch_envelope_promoted_count": 0,
        "durable_command_request_promoted_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_command_completed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_completion_decision_dry_run_contract",
        "Section 167 durable executor authoring command completion decision dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command completion decision dry-run contract is defined, but no completion decision record is present and the Section 166 execution evidence dry-run is not admissible.",
            "A future valid completion decision record can become dry-run admissible only; durable completion decision promotion, command completion, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_completion_application_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    decision_row = build_durable_executor_authoring_command_completion_decision_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    decision_summary = dict(decision_row["actual"])
    decision_summary["status"] = decision_summary.pop("summary_status")
    contract = durable_executor_authoring_command_completion_application_dry_run.build_durable_executor_authoring_command_completion_application_dry_run_contract(
        requested=True,
        section_167_command_completion_decision_dry_run_summary=decision_summary,
    )
    summary = durable_executor_authoring_command_completion_application_dry_run.summarize_durable_executor_authoring_command_completion_application_dry_runs(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_completion_application_dry_run_count": 1,
        "completion_application_contract_defined_count": 1,
        "section_167_completion_decision_contract_ready_count": 1,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "dry_run_route_record_valid_count": 0,
        "dry_run_route_admissible_count": 0,
        "dispatch_dry_run_record_valid_count": 0,
        "dispatch_dry_run_admissible_count": 0,
        "dispatch_evidence_dry_run_record_valid_count": 0,
        "dispatch_evidence_dry_run_admissible_count": 0,
        "execution_dry_run_record_valid_count": 0,
        "execution_dry_run_admissible_count": 0,
        "execution_evidence_dry_run_record_valid_count": 0,
        "execution_evidence_dry_run_admissible_count": 0,
        "completion_decision_dry_run_record_valid_count": 0,
        "completion_decision_dry_run_admissible_count": 0,
        "completion_decision_chain_satisfied_count": 0,
        "completion_application_dry_run_record_present_count": 0,
        "record_schema_matches_count": 0,
        "completion_application_scope_matches_count": 0,
        "dry_run_only_count": 0,
        "completion_application_status_passed_count": 0,
        "operator_reconfirmed_no_live_dispatch_count": 0,
        "operator_reconfirmed_no_live_execution_count": 0,
        "operator_reconfirmed_no_write_execution_count": 0,
        "operator_reconfirmed_no_save_delete_rename_count": 0,
        "requested_command_allowed_count": 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
        "completion_application_operation_allowed_count": 0,
        "completion_application_target_declared_count": 0,
        "completion_decision_admission_proof_matches_count": 0,
        "release_boundary_proof_safe_count": 0,
        "completion_application_dry_run_record_valid_count": 0,
        "completion_application_dry_run_record_rejected_count": 0,
        "completion_application_dry_run_admissible_count": 0,
        "unsafe_completion_application_record_count": 0,
        "missing_completion_application_dry_run_prerequisite_count": 31,
        "completion_application_dry_run_started_count": 0,
        "completion_application_dry_run_accepted_count": 0,
        "durable_completion_application_promoted_count": 0,
        "durable_completion_application_applied_count": 0,
        "durable_completion_decision_promoted_count": 0,
        "durable_execution_evidence_promoted_count": 0,
        "durable_execution_envelope_promoted_count": 0,
        "durable_evidence_promoted_count": 0,
        "durable_dispatch_envelope_promoted_count": 0,
        "durable_command_request_promoted_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_command_completed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_completion_application_dry_run_contract",
        "Section 168 durable executor authoring command completion application dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command completion application dry-run contract is defined, but no completion application record is present and the Section 167 completion decision dry-run is not admissible.",
            "A future valid completion application record can become dry-run admissible only; durable completion application promotion/application, command completion, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_completion_result_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    application_row = build_durable_executor_authoring_command_completion_application_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    application_summary = dict(application_row["actual"])
    application_summary["status"] = application_summary.pop("summary_status")
    contract = durable_executor_authoring_command_completion_result_dry_run.build_durable_executor_authoring_command_completion_result_dry_run_contract(
        requested=True,
        section_168_command_completion_application_dry_run_summary=application_summary,
    )
    summary = durable_executor_authoring_command_completion_result_dry_run.summarize_durable_executor_authoring_command_completion_result_dry_runs(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_completion_result_dry_run_count": 1,
        "completion_result_contract_defined_count": 1,
        "section_168_completion_application_contract_ready_count": 1,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "dry_run_route_record_valid_count": 0,
        "dry_run_route_admissible_count": 0,
        "dispatch_dry_run_record_valid_count": 0,
        "dispatch_dry_run_admissible_count": 0,
        "dispatch_evidence_dry_run_record_valid_count": 0,
        "dispatch_evidence_dry_run_admissible_count": 0,
        "execution_dry_run_record_valid_count": 0,
        "execution_dry_run_admissible_count": 0,
        "execution_evidence_dry_run_record_valid_count": 0,
        "execution_evidence_dry_run_admissible_count": 0,
        "completion_decision_dry_run_record_valid_count": 0,
        "completion_decision_dry_run_admissible_count": 0,
        "completion_application_dry_run_record_valid_count": 0,
        "completion_application_dry_run_admissible_count": 0,
        "completion_application_chain_satisfied_count": 0,
        "completion_result_dry_run_record_present_count": 0,
        "record_schema_matches_count": 0,
        "completion_result_scope_matches_count": 0,
        "dry_run_only_count": 0,
        "completion_result_status_passed_count": 0,
        "operator_reconfirmed_no_live_dispatch_count": 0,
        "operator_reconfirmed_no_live_execution_count": 0,
        "operator_reconfirmed_no_write_execution_count": 0,
        "operator_reconfirmed_no_save_delete_rename_count": 0,
        "requested_command_allowed_count": 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
        "completion_result_operation_allowed_count": 0,
        "completion_result_target_declared_count": 0,
        "completion_application_admission_proof_matches_count": 0,
        "release_boundary_proof_safe_count": 0,
        "completion_result_dry_run_record_valid_count": 0,
        "completion_result_dry_run_record_rejected_count": 0,
        "completion_result_dry_run_admissible_count": 0,
        "unsafe_completion_result_record_count": 0,
        "missing_completion_result_dry_run_prerequisite_count": 33,
        "completion_result_dry_run_started_count": 0,
        "completion_result_dry_run_accepted_count": 0,
        "durable_completion_result_promoted_count": 0,
        "durable_completion_result_recorded_count": 0,
        "durable_completion_application_promoted_count": 0,
        "durable_completion_application_applied_count": 0,
        "durable_completion_decision_promoted_count": 0,
        "durable_execution_evidence_promoted_count": 0,
        "durable_execution_envelope_promoted_count": 0,
        "durable_evidence_promoted_count": 0,
        "durable_dispatch_envelope_promoted_count": 0,
        "durable_command_request_promoted_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_command_completed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_completion_result_dry_run_contract",
        "Section 169 durable executor authoring command completion result dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command completion result dry-run contract is defined, but no completion result record is present and the Section 168 completion application dry-run is not admissible.",
            "A future valid completion result record can become dry-run admissible only; durable completion result promotion/recording, command completion, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_result_readback_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    result_row = build_durable_executor_authoring_command_completion_result_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    result_summary = dict(result_row["actual"])
    result_summary["status"] = result_summary.pop("summary_status")
    contract = durable_executor_authoring_command_result_readback_dry_run.build_durable_executor_authoring_command_result_readback_dry_run_contract(
        requested=True,
        section_169_command_completion_result_dry_run_summary=result_summary,
    )
    summary = durable_executor_authoring_command_result_readback_dry_run.summarize_durable_executor_authoring_command_result_readback_dry_runs(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_command_result_readback_dry_run_count": 1,
        "result_readback_contract_defined_count": 1,
        "section_169_completion_result_contract_ready_count": 1,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "dry_run_route_record_valid_count": 0,
        "dry_run_route_admissible_count": 0,
        "dispatch_dry_run_record_valid_count": 0,
        "dispatch_dry_run_admissible_count": 0,
        "dispatch_evidence_dry_run_record_valid_count": 0,
        "dispatch_evidence_dry_run_admissible_count": 0,
        "execution_dry_run_record_valid_count": 0,
        "execution_dry_run_admissible_count": 0,
        "execution_evidence_dry_run_record_valid_count": 0,
        "execution_evidence_dry_run_admissible_count": 0,
        "completion_decision_dry_run_record_valid_count": 0,
        "completion_decision_dry_run_admissible_count": 0,
        "completion_application_dry_run_record_valid_count": 0,
        "completion_application_dry_run_admissible_count": 0,
        "completion_result_dry_run_record_valid_count": 0,
        "completion_result_dry_run_admissible_count": 0,
        "completion_result_chain_satisfied_count": 0,
        "result_readback_dry_run_record_present_count": 0,
        "record_schema_matches_count": 0,
        "result_readback_scope_matches_count": 0,
        "dry_run_only_count": 0,
        "result_readback_status_passed_count": 0,
        "operator_reconfirmed_no_live_dispatch_count": 0,
        "operator_reconfirmed_no_live_execution_count": 0,
        "operator_reconfirmed_no_write_execution_count": 0,
        "operator_reconfirmed_no_save_delete_rename_count": 0,
        "requested_command_allowed_count": 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
        "result_readback_operation_allowed_count": 0,
        "result_readback_target_declared_count": 0,
        "completion_result_admission_proof_matches_count": 0,
        "release_boundary_proof_safe_count": 0,
        "result_readback_dry_run_record_valid_count": 0,
        "result_readback_dry_run_record_rejected_count": 0,
        "result_readback_dry_run_admissible_count": 0,
        "unsafe_result_readback_record_count": 0,
        "missing_result_readback_dry_run_prerequisite_count": 35,
        "result_readback_dry_run_started_count": 0,
        "result_readback_dry_run_accepted_count": 0,
        "durable_result_readback_promoted_count": 0,
        "durable_result_readback_accepted_count": 0,
        "durable_completion_result_promoted_count": 0,
        "durable_completion_result_recorded_count": 0,
        "durable_completion_application_promoted_count": 0,
        "durable_completion_application_applied_count": 0,
        "durable_completion_decision_promoted_count": 0,
        "durable_execution_evidence_promoted_count": 0,
        "durable_execution_envelope_promoted_count": 0,
        "durable_evidence_promoted_count": 0,
        "durable_dispatch_envelope_promoted_count": 0,
        "durable_command_request_promoted_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_command_completed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_result_readback_dry_run_contract",
        "Section 170 durable executor authoring command result readback dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command result readback dry-run contract is defined, but no readback record is present and the Section 169 completion result dry-run is not admissible.",
            "A future valid result readback record can become dry-run admissible only; durable readback promotion/acceptance, command completion, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_final_no_save_release_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    result_readback_row = build_durable_executor_authoring_command_result_readback_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    result_readback_summary = dict(result_readback_row["actual"])
    result_readback_summary["status"] = result_readback_summary.pop("summary_status")
    contract = durable_executor_authoring_final_no_save_release_dry_run.build_durable_executor_authoring_final_no_save_release_dry_run_contract(
        requested=True,
        section_170_command_result_readback_dry_run_summary=result_readback_summary,
    )
    summary = durable_executor_authoring_final_no_save_release_dry_run.summarize_durable_executor_authoring_final_no_save_release_dry_runs(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_final_no_save_release_dry_run_count": 1,
        "final_no_save_release_contract_defined_count": 1,
        "section_170_result_readback_contract_ready_count": 1,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "dry_run_route_record_valid_count": 0,
        "dry_run_route_admissible_count": 0,
        "dispatch_dry_run_record_valid_count": 0,
        "dispatch_dry_run_admissible_count": 0,
        "dispatch_evidence_dry_run_record_valid_count": 0,
        "dispatch_evidence_dry_run_admissible_count": 0,
        "execution_dry_run_record_valid_count": 0,
        "execution_dry_run_admissible_count": 0,
        "execution_evidence_dry_run_record_valid_count": 0,
        "execution_evidence_dry_run_admissible_count": 0,
        "completion_decision_dry_run_record_valid_count": 0,
        "completion_decision_dry_run_admissible_count": 0,
        "completion_application_dry_run_record_valid_count": 0,
        "completion_application_dry_run_admissible_count": 0,
        "completion_result_dry_run_record_valid_count": 0,
        "completion_result_dry_run_admissible_count": 0,
        "result_readback_dry_run_record_valid_count": 0,
        "result_readback_dry_run_admissible_count": 0,
        "result_readback_chain_satisfied_count": 0,
        "final_no_save_release_dry_run_record_present_count": 0,
        "record_schema_matches_count": 0,
        "final_no_save_release_scope_matches_count": 0,
        "dry_run_only_count": 0,
        "final_no_save_release_status_passed_count": 0,
        "operator_reconfirmed_no_live_dispatch_count": 0,
        "operator_reconfirmed_no_live_execution_count": 0,
        "operator_reconfirmed_no_write_execution_count": 0,
        "operator_reconfirmed_no_save_delete_rename_count": 0,
        "requested_command_allowed_count": 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
        "final_no_save_release_operation_allowed_count": 0,
        "final_no_save_release_target_declared_count": 0,
        "result_readback_admission_proof_matches_count": 0,
        "release_boundary_proof_safe_count": 0,
        "final_no_save_release_dry_run_record_valid_count": 0,
        "final_no_save_release_dry_run_record_rejected_count": 0,
        "final_no_save_release_dry_run_admissible_count": 0,
        "unsafe_final_no_save_release_record_count": 0,
        "missing_final_no_save_release_dry_run_prerequisite_count": 37,
        "final_no_save_release_dry_run_started_count": 0,
        "final_no_save_release_dry_run_accepted_count": 0,
        "durable_final_no_save_release_promoted_count": 0,
        "durable_final_no_save_release_accepted_count": 0,
        "durable_final_release_readiness_started_count": 0,
        "durable_final_release_ready_count": 0,
        "durable_result_readback_promoted_count": 0,
        "durable_result_readback_accepted_count": 0,
        "durable_completion_result_promoted_count": 0,
        "durable_completion_result_recorded_count": 0,
        "durable_completion_application_promoted_count": 0,
        "durable_completion_application_applied_count": 0,
        "durable_completion_decision_promoted_count": 0,
        "durable_execution_evidence_promoted_count": 0,
        "durable_execution_envelope_promoted_count": 0,
        "durable_evidence_promoted_count": 0,
        "durable_dispatch_envelope_promoted_count": 0,
        "durable_command_request_promoted_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_command_completed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_final_no_save_release_dry_run_contract",
        "Section 171 durable executor authoring final no-save release dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring final no-save release dry-run contract is defined, but no final no-save release record is present and the Section 170 result readback dry-run is not admissible.",
            "A future valid final no-save release record can become dry-run admissible only; durable final release promotion/readiness, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_final_release_readiness_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    final_no_save_row = build_durable_executor_authoring_final_no_save_release_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    final_no_save_summary = dict(final_no_save_row["actual"])
    final_no_save_summary["status"] = final_no_save_summary.pop("summary_status")
    contract = durable_executor_authoring_final_release_readiness_dry_run.build_durable_executor_authoring_final_release_readiness_dry_run_contract(
        requested=True,
        section_171_final_no_save_release_dry_run_summary=final_no_save_summary,
    )
    summary = durable_executor_authoring_final_release_readiness_dry_run.summarize_durable_executor_authoring_final_release_readiness_dry_runs(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_final_release_readiness_dry_run_count": 1,
        "final_release_readiness_contract_defined_count": 1,
        "section_171_final_no_save_contract_ready_count": 1,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "dry_run_route_record_valid_count": 0,
        "dry_run_route_admissible_count": 0,
        "dispatch_dry_run_record_valid_count": 0,
        "dispatch_dry_run_admissible_count": 0,
        "dispatch_evidence_dry_run_record_valid_count": 0,
        "dispatch_evidence_dry_run_admissible_count": 0,
        "execution_dry_run_record_valid_count": 0,
        "execution_dry_run_admissible_count": 0,
        "execution_evidence_dry_run_record_valid_count": 0,
        "execution_evidence_dry_run_admissible_count": 0,
        "completion_decision_dry_run_record_valid_count": 0,
        "completion_decision_dry_run_admissible_count": 0,
        "completion_application_dry_run_record_valid_count": 0,
        "completion_application_dry_run_admissible_count": 0,
        "completion_result_dry_run_record_valid_count": 0,
        "completion_result_dry_run_admissible_count": 0,
        "result_readback_dry_run_record_valid_count": 0,
        "result_readback_dry_run_admissible_count": 0,
        "final_no_save_release_dry_run_record_valid_count": 0,
        "final_no_save_release_dry_run_admissible_count": 0,
        "final_no_save_release_chain_satisfied_count": 0,
        "final_release_readiness_dry_run_record_present_count": 0,
        "record_schema_matches_count": 0,
        "final_release_readiness_scope_matches_count": 0,
        "dry_run_only_count": 0,
        "final_release_readiness_status_passed_count": 0,
        "operator_reconfirmed_no_live_dispatch_count": 0,
        "operator_reconfirmed_no_live_execution_count": 0,
        "operator_reconfirmed_no_write_execution_count": 0,
        "operator_reconfirmed_no_save_delete_rename_count": 0,
        "requested_command_allowed_count": 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
        "final_release_readiness_operation_allowed_count": 0,
        "final_release_readiness_target_declared_count": 0,
        "final_no_save_admission_proof_matches_count": 0,
        "release_boundary_proof_safe_count": 0,
        "final_release_readiness_dry_run_record_valid_count": 0,
        "final_release_readiness_dry_run_record_rejected_count": 0,
        "final_release_readiness_dry_run_admissible_count": 0,
        "unsafe_final_release_readiness_record_count": 0,
        "missing_final_release_readiness_dry_run_prerequisite_count": 39,
        "final_release_readiness_dry_run_started_count": 0,
        "final_release_readiness_dry_run_accepted_count": 0,
        "durable_final_release_readiness_promoted_count": 0,
        "durable_final_release_readiness_started_count": 0,
        "durable_final_release_ready_count": 0,
        "durable_release_review_started_count": 0,
        "durable_final_no_save_release_promoted_count": 0,
        "durable_final_no_save_release_accepted_count": 0,
        "durable_result_readback_promoted_count": 0,
        "durable_result_readback_accepted_count": 0,
        "durable_completion_result_promoted_count": 0,
        "durable_completion_result_recorded_count": 0,
        "durable_completion_application_promoted_count": 0,
        "durable_completion_application_applied_count": 0,
        "durable_completion_decision_promoted_count": 0,
        "durable_execution_evidence_promoted_count": 0,
        "durable_execution_envelope_promoted_count": 0,
        "durable_evidence_promoted_count": 0,
        "durable_dispatch_envelope_promoted_count": 0,
        "durable_command_request_promoted_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_command_completed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_final_release_readiness_dry_run_contract",
        "Section 172 durable executor authoring final release readiness dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring final release readiness dry-run contract is defined, but no final release readiness record is present and the Section 171 final no-save release dry-run is not admissible.",
            "A future valid final release readiness record can become dry-run admissible only; durable final release readiness promotion, final durable release readiness, release review, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def _summary_from_row_actual(row_data: Dict[str, Any]) -> Dict[str, Any]:
    summary = dict(row_data["actual"])
    summary["status"] = summary.pop("summary_status")
    return summary


def _release_stage_dry_run_expected(module: Any) -> Dict[str, Any]:
    expected = {
        "summary_status": "passed",
        module.REQUEST_COUNT_KEY: 1,
        module.CONTRACT_DEFINED_COUNT_KEY: 1,
        module.PREVIOUS_READY_COUNT_KEY: 1,
    }
    expected.update(
        {
            f"{output_key}_count": 0
            for output_key, _summary_key, _missing_key in module.CHAIN_INPUTS
        }
    )
    expected[module.CHAIN_SATISFIED_COUNT_KEY] = 0
    expected.update({key: 0 for key in module.RECORD_SUMMARY_ZERO_COUNT_KEYS})
    expected[module.MISSING_PREREQUISITE_COUNT_KEY] = (
        module.CURRENT_MISSING_PREREQUISITE_COUNT
    )
    expected.update({f"{key}_count": 0 for key in module.OUTPUT_ACTION_KEYS})
    return expected


def build_durable_executor_authoring_release_review_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    final_readiness_row = build_durable_executor_authoring_final_release_readiness_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    final_readiness_summary = _summary_from_row_actual(final_readiness_row)
    contract = durable_executor_authoring_release_review_dry_run.build_durable_executor_authoring_release_review_dry_run_contract(
        requested=True,
        section_172_final_release_readiness_dry_run_summary=final_readiness_summary,
    )
    summary = durable_executor_authoring_release_review_dry_run.summarize_durable_executor_authoring_release_review_dry_runs(
        [contract]
    )
    expected = _release_stage_dry_run_expected(
        durable_executor_authoring_release_review_dry_run
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_review_dry_run_contract",
        "Section 173 durable executor authoring release review dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring release review dry-run contract is defined, but no release review record is present and the Section 172 final release readiness dry-run is not admissible.",
            "A future valid release review record can become dry-run admissible only; durable review promotion, release decision start, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_release_decision_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    review_row = build_durable_executor_authoring_release_review_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    review_summary = _summary_from_row_actual(review_row)
    contract = durable_executor_authoring_release_decision_dry_run.build_durable_executor_authoring_release_decision_dry_run_contract(
        requested=True,
        section_173_release_review_dry_run_summary=review_summary,
    )
    summary = durable_executor_authoring_release_decision_dry_run.summarize_durable_executor_authoring_release_decision_dry_runs(
        [contract]
    )
    expected = _release_stage_dry_run_expected(
        durable_executor_authoring_release_decision_dry_run
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_decision_dry_run_contract",
        "Section 174 durable executor authoring release decision dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring release decision dry-run contract is defined, but no release decision record is present and the Section 173 release review dry-run is not admissible.",
            "A future valid release decision record can become dry-run admissible only; durable decision promotion, promotion barrier start, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_release_promotion_barrier_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    decision_row = build_durable_executor_authoring_release_decision_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    decision_summary = _summary_from_row_actual(decision_row)
    contract = durable_executor_authoring_release_promotion_barrier_dry_run.build_durable_executor_authoring_release_promotion_barrier_dry_run_contract(
        requested=True,
        section_174_release_decision_dry_run_summary=decision_summary,
    )
    summary = durable_executor_authoring_release_promotion_barrier_dry_run.summarize_durable_executor_authoring_release_promotion_barrier_dry_runs(
        [contract]
    )
    expected = _release_stage_dry_run_expected(
        durable_executor_authoring_release_promotion_barrier_dry_run
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_promotion_barrier_dry_run_contract",
        "Section 175 durable executor authoring release promotion barrier dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring release promotion barrier dry-run contract is defined, but no promotion barrier record is present and the Section 174 release decision dry-run is not admissible.",
            "A future valid promotion barrier record can become dry-run admissible only; durable promotion barrier promotion, activation/open/enable, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_activation_readiness_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    promotion_barrier_row = build_durable_executor_authoring_release_promotion_barrier_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    promotion_barrier_summary = _summary_from_row_actual(promotion_barrier_row)
    contract = durable_executor_authoring_activation_readiness_dry_run.build_durable_executor_authoring_activation_readiness_dry_run_contract(
        requested=True,
        section_175_release_promotion_barrier_dry_run_summary=promotion_barrier_summary,
    )
    summary = durable_executor_authoring_activation_readiness_dry_run.summarize_durable_executor_authoring_activation_readiness_dry_runs(
        [contract]
    )
    expected = _release_stage_dry_run_expected(
        durable_executor_authoring_activation_readiness_dry_run
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_activation_readiness_dry_run_contract",
        "Section 176 durable executor authoring activation readiness dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring activation readiness dry-run contract is defined, but no activation readiness record is present and the Section 175 release promotion barrier dry-run is not admissible.",
            "A future valid activation readiness record can become dry-run admissible only; durable activation readiness promotion, executor open/start, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_open_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    activation_readiness_row = build_durable_executor_authoring_activation_readiness_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    activation_readiness_summary = _summary_from_row_actual(activation_readiness_row)
    contract = durable_executor_authoring_open_dry_run.build_durable_executor_authoring_open_dry_run_contract(
        requested=True,
        section_176_activation_readiness_dry_run_summary=activation_readiness_summary,
    )
    summary = durable_executor_authoring_open_dry_run.summarize_durable_executor_authoring_open_dry_runs(
        [contract]
    )
    expected = _release_stage_dry_run_expected(
        durable_executor_authoring_open_dry_run
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_open_dry_run_contract",
        "Section 177 durable executor authoring open dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring open dry-run contract is defined, but no open record is present and the Section 176 activation readiness dry-run is not admissible.",
            "A future valid open record can become dry-run admissible only; executor open/activation, durable authoring enable, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_open_promotion_barrier_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    open_row = build_durable_executor_authoring_open_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    open_summary = _summary_from_row_actual(open_row)
    contract = durable_executor_authoring_open_promotion_barrier_dry_run.build_durable_executor_authoring_open_promotion_barrier_dry_run_contract(
        requested=True,
        section_177_open_dry_run_summary=open_summary,
    )
    summary = durable_executor_authoring_open_promotion_barrier_dry_run.summarize_durable_executor_authoring_open_promotion_barrier_dry_runs(
        [contract]
    )
    expected = _release_stage_dry_run_expected(
        durable_executor_authoring_open_promotion_barrier_dry_run
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_open_promotion_barrier_dry_run_contract",
        "Section 178 durable executor authoring open promotion barrier dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring open promotion barrier dry-run contract is defined, but no open promotion barrier record is present and the Section 177 open dry-run is not admissible.",
            "A future valid open promotion barrier record can become dry-run admissible only; executor promotion/open/activation, durable authoring enable, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_path_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    open_promotion_barrier_row = build_durable_executor_authoring_open_promotion_barrier_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    open_promotion_barrier_summary = _summary_from_row_actual(
        open_promotion_barrier_row
    )
    contract = durable_executor_authoring_command_path_dry_run.build_durable_executor_authoring_command_path_dry_run_contract(
        requested=True,
        section_178_open_promotion_barrier_dry_run_summary=open_promotion_barrier_summary,
    )
    summary = durable_executor_authoring_command_path_dry_run.summarize_durable_executor_authoring_command_path_dry_runs(
        [contract]
    )
    expected = _release_stage_dry_run_expected(
        durable_executor_authoring_command_path_dry_run
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_path_dry_run_contract",
        "Section 179 durable executor authoring command path dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command path dry-run contract is defined, but no command path record is present and the Section 178 open promotion barrier dry-run is not admissible.",
            "A future valid command path record can become dry-run admissible only; executor command path open/allow, authoring command admission, live dispatch/execution, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_command_admission_dry_run_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    command_path_row = build_durable_executor_authoring_command_path_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    command_path_summary = _summary_from_row_actual(command_path_row)
    contract = durable_executor_authoring_command_admission_dry_run.build_durable_executor_authoring_command_admission_dry_run_contract(
        requested=True,
        section_179_command_path_dry_run_summary=command_path_summary,
    )
    summary = durable_executor_authoring_command_admission_dry_run.summarize_durable_executor_authoring_command_admission_dry_runs(
        [contract]
    )
    expected = _release_stage_dry_run_expected(
        durable_executor_authoring_command_admission_dry_run
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_command_admission_dry_run_contract",
        "Section 180 durable executor authoring command admission dry-run contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable executor authoring command admission dry-run contract is defined, but no command admission record is present and the Section 179 command path dry-run is not admissible.",
            "A future valid command admission record can become dry-run admissible only; authoring command allow/dispatch/execute, save, delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_release_boundary_consolidation_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    command_admission_row = build_durable_executor_authoring_command_admission_dry_run_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    command_admission_summary = _summary_from_row_actual(command_admission_row)
    command_admission_summary["schema"] = (
        durable_executor_authoring_command_admission_dry_run
        .DURABLE_EXECUTOR_AUTHORING_COMMAND_ADMISSION_DRY_RUN_SUMMARY_SCHEMA
    )
    contract = durable_executor_authoring_release_boundary_consolidation.build_durable_executor_authoring_release_boundary_consolidation_contract(
        requested=True,
        section_180_command_admission_dry_run_summary=command_admission_summary,
    )
    summary = durable_executor_authoring_release_boundary_consolidation.summarize_durable_executor_authoring_release_boundary_consolidations(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_release_boundary_consolidation_count": 1,
        "release_boundary_consolidated_count": 1,
        "section_180_summary_schema_matches_count": 1,
        "section_180_summary_passed_count": 1,
        "section_180_command_admission_contract_defined_count": 1,
        "section_179_command_path_contract_ready_count": 1,
        "section_180_command_path_chain_unsatisfied_count": 1,
        "command_admission_record_absent_count": 1,
        "command_admission_record_not_valid_count": 1,
        "command_admission_not_admissible_count": 1,
        "command_admission_missing_prerequisites_match_count": 1,
        "no_forbidden_or_unknown_requested_commands_count": 1,
        "no_rejected_or_unsafe_records_count": 1,
        "blocked_outputs_zero_count": 1,
        "durable_authoring_enabled_count": 0,
        "final_durable_release_ready_count": 0,
        "durable_safety_boundary_unlock_ready_count": 0,
    }
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_release_boundary_consolidation
                .BLOCKED_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_release_boundary_consolidation",
        "Section 181 durable executor authoring release boundary consolidation",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The Section 177-180 dry-run boundary is consolidated while command admission remains non-admissible and the command path chain remains unsatisfied.",
            "Durable authoring, final durable release readiness, command path open/allow, authoring command allow/dispatch/execute, save/delete/rename, cleanup, and live durable authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_safety_boundary_unlock_decision_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    consolidation_row = build_durable_executor_authoring_release_boundary_consolidation_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    consolidation_summary = _summary_from_row_actual(consolidation_row)
    consolidation_summary["schema"] = (
        durable_executor_authoring_release_boundary_consolidation
        .DURABLE_EXECUTOR_AUTHORING_RELEASE_BOUNDARY_CONSOLIDATION_SUMMARY_SCHEMA
    )
    contract = durable_executor_authoring_safety_boundary_unlock_decision.build_durable_executor_authoring_safety_boundary_unlock_decision_contract(
        requested=True,
        section_181_release_boundary_consolidation_summary=consolidation_summary,
    )
    summary = durable_executor_authoring_safety_boundary_unlock_decision.summarize_durable_executor_authoring_safety_boundary_unlock_decisions(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_safety_boundary_unlock_decision_count": 1,
        "unlock_decision_checkpoint_only_count": 1,
        "unlock_decision_checkpoint_reached_count": 1,
        "section_181_summary_schema_matches_count": 1,
        "section_181_summary_passed_count": 1,
        "section_181_release_boundary_consolidated_count": 1,
        "section_181_unlock_ready_absent_count": 1,
        "section_181_authoring_disabled_count": 1,
        "section_181_final_release_not_ready_count": 1,
        "blocked_outputs_zero_count": 1,
        "unlock_decision_record_present_count": 0,
        "unlock_decision_record_absent_count": 1,
        "unlock_decision_record_schema_matches_count": 0,
        "explicit_unlock_approval_present_count": 0,
        "explicit_unlock_approval_absent_count": 1,
        "unlock_requires_explicit_user_approval_count": 1,
        "unlock_record_admissible_count": 0,
        "durable_safety_boundary_unlock_ready_count": 0,
        "durable_safety_boundary_unlocked_count": 0,
        "durable_authoring_enabled_count": 0,
        "final_durable_release_ready_count": 0,
        "save_delete_rename_allowed_count": 0,
        "live_durable_authoring_allowed_count": 0,
    }
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_safety_boundary_unlock_decision
                .BLOCKED_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_safety_boundary_unlock_decision",
        "Section 182 durable executor authoring safety boundary unlock decision checkpoint",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The durable safety boundary unlock decision checkpoint is reached after Section 181 consolidation, but no explicit unlock decision record is present.",
            "This checkpoint does not unlock durable authoring, final durable release readiness, command path open/allow, authoring command allow/dispatch/execute, save/delete/rename, cleanup, or live durable authoring.",
        ),
    )


def build_durable_executor_authoring_safety_boundary_unlock_record_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    unlock_decision_row = build_durable_executor_authoring_safety_boundary_unlock_decision_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    unlock_decision_summary = _summary_from_row_actual(unlock_decision_row)
    unlock_decision_summary["schema"] = (
        durable_executor_authoring_safety_boundary_unlock_decision
        .DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_DECISION_SUMMARY_SCHEMA
    )
    live_preflight_summary: Dict[str, Any] = {}
    if planner_report is not None:
        live_preflight_summary = (
            planner_report
            .get("live_gate", {})
            .get("durable_live_preflight_gate", {})
        )
    approval_record = (
        durable_executor_authoring_safety_boundary_unlock_record
        .build_explicit_unlock_approval_record(
            "user_explicit_approval_section_183_2026_06_08"
        )
    )
    contract = durable_executor_authoring_safety_boundary_unlock_record.build_durable_executor_authoring_safety_boundary_unlock_record_contract(
        requested=True,
        section_182_unlock_decision_summary=unlock_decision_summary,
        live_preflight_summary=live_preflight_summary,
        approval_record=approval_record,
    )
    summary = durable_executor_authoring_safety_boundary_unlock_record.summarize_durable_executor_authoring_safety_boundary_unlock_records(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_safety_boundary_unlock_record_count": 1,
        "section_182_summary_schema_matches_count": 1,
        "section_182_summary_passed_count": 1,
        "section_182_checkpoint_reached_count": 1,
        "section_182_unlock_record_absent_count": 1,
        "section_182_unlock_record_not_admissible_count": 1,
        "section_182_authoring_disabled_count": 1,
        "section_182_final_release_not_ready_count": 1,
        "section_182_unlocked_absent_count": 1,
        "blocked_outputs_zero_count": 1,
        "approval_record_present_count": 1,
        "approval_record_schema_matches_count": 1,
        "approval_scope_matches_count": 1,
        "approval_operation_matches_count": 1,
        "explicit_unlock_approval_present_count": 1,
        "approval_requires_read_only_live_preflight_count": 1,
        "approval_blocks_save_delete_rename_count": 1,
        "approval_blocks_live_writes_count": 1,
        "live_preflight_schema_matches_count": 1,
        "live_preflight_passed_count": 1,
        "live_preflight_requested_count": 1,
        "live_preflight_result_present_count": 1,
        "live_preflight_read_only_result_passed_count": 1,
        "live_preflight_read_only_only_count": 1,
        "live_preflight_no_authoring_attempted_count": 1,
        "live_preflight_no_save_delete_attempted_count": 1,
        "live_preflight_does_not_pass_write_gate_count": 1,
        "unlock_record_admissible_count": 1,
        "durable_safety_boundary_unlock_ready_count": 1,
        "durable_safety_boundary_unlocked_count": 0,
        "durable_authoring_enabled_count": 0,
        "final_durable_release_ready_count": 0,
        "save_delete_rename_allowed_count": 0,
        "live_durable_authoring_allowed_count": 0,
    }
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_safety_boundary_unlock_record
                .BLOCKED_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_safety_boundary_unlock_record",
        "Section 183 durable executor authoring safety boundary unlock record",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The explicit unlock approval record is admitted only with Section 182 checkpoint evidence and passed read-only live preflight evidence.",
            "This records unlock readiness but does not unlock durable authoring, final durable release readiness, save/delete/rename, cleanup, or live durable authoring writes.",
        ),
    )


def build_durable_executor_authoring_safety_boundary_unlock_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    unlock_record_row = build_durable_executor_authoring_safety_boundary_unlock_record_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    unlock_record_summary = _summary_from_row_actual(unlock_record_row)
    unlock_record_summary["schema"] = (
        durable_executor_authoring_safety_boundary_unlock_record
        .DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_RECORD_SUMMARY_SCHEMA
    )
    contract = durable_executor_authoring_safety_boundary_unlock.build_durable_executor_authoring_safety_boundary_unlock_contract(
        requested=True,
        section_183_unlock_record_summary=unlock_record_summary,
    )
    summary = durable_executor_authoring_safety_boundary_unlock.summarize_durable_executor_authoring_safety_boundary_unlocks(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_safety_boundary_unlock_count": 1,
        "section_183_summary_schema_matches_count": 1,
        "section_183_summary_passed_count": 1,
        "section_183_unlock_record_admissible_count": 1,
        "section_183_unlock_ready_count": 1,
        "section_183_unlocked_absent_count": 1,
        "section_183_authoring_disabled_count": 1,
        "section_183_final_release_not_ready_count": 1,
        "section_183_save_delete_rename_blocked_count": 1,
        "section_183_live_durable_authoring_blocked_count": 1,
        "blocked_outputs_zero_count": 1,
        "durable_safety_boundary_unlocked_count": 1,
        "durable_authoring_enabled_count": 0,
        "final_durable_release_ready_count": 0,
        "durable_executor_open_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "live_durable_authoring_allowed_count": 0,
    }
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_safety_boundary_unlock
                .BLOCKED_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_safety_boundary_unlock",
        "Section 184 durable executor authoring safety boundary unlock",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "The safety boundary is unlocked only after Section 183 unlock-record readiness.",
            "Durable authoring, final durable release readiness, executor open, authoring commands, save/delete/rename, cleanup, and live durable write authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_enable_after_safety_boundary_unlock_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    unlock_row = build_durable_executor_authoring_safety_boundary_unlock_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    unlock_summary = _summary_from_row_actual(unlock_row)
    unlock_summary["schema"] = (
        durable_executor_authoring_safety_boundary_unlock
        .DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_SUMMARY_SCHEMA
    )
    contract = durable_executor_authoring_enable_after_safety_boundary_unlock.build_durable_executor_authoring_enable_after_safety_boundary_unlock_contract(
        requested=True,
        section_184_safety_boundary_unlock_summary=unlock_summary,
    )
    summary = durable_executor_authoring_enable_after_safety_boundary_unlock.summarize_durable_executor_authoring_enable_after_safety_boundary_unlocks(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_enable_after_safety_boundary_unlock_count": 1,
        "section_184_summary_schema_matches_count": 1,
        "section_184_summary_passed_count": 1,
        "section_184_safety_boundary_unlocked_count": 1,
        "section_184_authoring_disabled_count": 1,
        "section_184_final_release_not_ready_count": 1,
        "section_184_executor_open_blocked_count": 1,
        "section_184_authoring_command_blocked_count": 1,
        "section_184_save_delete_rename_blocked_count": 1,
        "section_184_live_durable_authoring_blocked_count": 1,
        "blocked_outputs_zero_count": 1,
        "durable_authoring_enable_admissible_count": 1,
        "durable_authoring_enabled_count": 1,
        "final_durable_release_ready_count": 0,
        "durable_executor_open_allowed_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "live_durable_authoring_allowed_count": 0,
    }
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_enable_after_safety_boundary_unlock
                .BLOCKED_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_enable_after_safety_boundary_unlock",
        "Section 185 durable executor authoring enable after safety boundary unlock",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Durable authoring is enabled only after Section 184 safety boundary unlock evidence.",
            "Executor open, authoring command allow, final release readiness, save/delete/rename, cleanup, and live durable write authoring remain blocked.",
        ),
    )


def build_durable_executor_authoring_no_save_execution_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    enable_row = build_durable_executor_authoring_enable_after_safety_boundary_unlock_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    enable_summary = _summary_from_row_actual(enable_row)
    enable_summary["schema"] = (
        durable_executor_authoring_enable_after_safety_boundary_unlock
        .DURABLE_EXECUTOR_AUTHORING_ENABLE_AFTER_SAFETY_BOUNDARY_UNLOCK_SUMMARY_SCHEMA
    )
    contract = durable_executor_authoring_no_save_execution_batch.build_durable_executor_authoring_no_save_execution_batch_contract(
        requested=True,
        section_185_enable_summary=enable_summary,
    )
    summary = durable_executor_authoring_no_save_execution_batch.summarize_durable_executor_authoring_no_save_execution_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_no_save_execution_batch_count": 1,
        "section_185_summary_schema_matches_count": 1,
        "section_185_summary_passed_count": 1,
        "section_185_authoring_enabled_count": 1,
        "section_185_final_release_not_ready_count": 1,
        "section_185_executor_open_blocked_count": 1,
        "section_185_command_allow_blocked_count": 1,
        "section_185_save_delete_rename_blocked_count": 1,
        "section_185_live_durable_authoring_blocked_count": 1,
        "blocked_outputs_zero_count": 1,
        "no_save_execution_batch_admissible_count": 1,
        "section_186_executor_opened_count": 1,
        "section_187_open_readiness_consolidated_count": 1,
        "section_188_authoring_command_allowed_count": 1,
        "section_189_command_dispatch_gate_open_count": 1,
        "section_190_command_execution_evidence_gate_open_count": 1,
        "section_191_completion_readback_ready_count": 1,
        "section_192_final_no_save_release_ready_count": 1,
        "durable_executor_open_allowed_count": 1,
        "durable_executor_opened_count": 1,
        "durable_authoring_command_allowed_count": 1,
        "durable_authoring_command_dispatched_count": 1,
        "durable_authoring_command_executed_count": 1,
        "durable_authoring_command_completed_count": 1,
        "final_no_save_release_ready_count": 1,
        "durable_authoring_enabled_count": 1,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "live_durable_authoring_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_no_save_execution_batch
                .BLOCKED_OUTPUT_COUNT_KEYS
            )
        }
    )
    for key in durable_executor_authoring_no_save_execution_batch.NO_SAVE_PATH_COUNT_KEYS:
        expected[key] = 1
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_no_save_execution_batch",
        "Sections 186-192 durable executor authoring no-save execution batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 186-192 are bundled: executor open, open readiness, command allow, dispatch, execution/evidence, completion/readback, and final no-save readiness.",
            "The batch does not allow asset writes, dirty packages, save/delete/rename, cleanup, live durable writes, live command dispatch/execution, or final durable release readiness.",
        ),
    )


def build_durable_executor_authoring_save_gate_preflight_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    no_save_row = build_durable_executor_authoring_no_save_execution_batch_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    no_save_summary = _summary_from_row_actual(no_save_row)
    no_save_summary["schema"] = (
        durable_executor_authoring_no_save_execution_batch
        .DURABLE_EXECUTOR_AUTHORING_NO_SAVE_EXECUTION_BATCH_SUMMARY_SCHEMA
    )
    contract = durable_executor_authoring_save_gate_preflight_batch.build_durable_executor_authoring_save_gate_preflight_batch_contract(
        requested=True,
        section_186_192_no_save_summary=no_save_summary,
    )
    summary = durable_executor_authoring_save_gate_preflight_batch.summarize_durable_executor_authoring_save_gate_preflight_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_save_gate_preflight_batch_count": 1,
        "section_186_192_summary_schema_matches_count": 1,
        "section_186_192_summary_passed_count": 1,
        "section_186_192_no_save_ready_count": 1,
        "section_186_192_write_outputs_blocked_count": 1,
        "section_193_save_target_declared_count": 1,
        "section_194_ownership_marker_revalidated_count": 1,
        "section_195_rollback_policy_revalidated_count": 1,
        "section_196_overwrite_rename_decision_ready_count": 1,
        "section_197_read_only_save_preflight_ready_count": 1,
        "section_198_save_command_admission_preflight_ready_count": 1,
        "section_199_save_gate_open_review_ready_count": 1,
        "section_200_final_save_gate_preflight_ready_count": 1,
        "durable_authoring_enabled_count": 1,
        "durable_executor_opened_count": 1,
        "durable_authoring_command_no_save_execution_ready_count": 1,
        "final_no_save_release_ready_count": 1,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_gate_open_allowed_count": 0,
        "save_command_admitted_count": 0,
        "save_command_dispatched_count": 0,
        "save_command_executed_count": 0,
        "save_true_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "compile_save_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "live_durable_authoring_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    for key in (
        durable_executor_authoring_save_gate_preflight_batch
        .SAVE_GATE_PREFLIGHT_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_save_gate_preflight_batch
                .UPSTREAM_BLOCKED_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_save_gate_preflight_batch",
        "Sections 193-200 durable executor authoring save-gate preflight batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 193-200 are bundled: save target declaration, ownership-marker revalidation, rollback revalidation, overwrite/rename decision, read-only save preflight, command-admission preflight, save-gate open review, and final save-gate preflight readiness.",
            "The batch does not admit, dispatch, execute, or save a command and does not allow save=true, save_asset, compile/save, delete, rename, package dirtying, live durable writes, or final durable release readiness.",
        ),
    )


def build_durable_executor_authoring_save_gate_open_admission_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    preflight_row = build_durable_executor_authoring_save_gate_preflight_batch_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    preflight_summary = _summary_from_row_actual(preflight_row)
    preflight_summary["schema"] = (
        durable_executor_authoring_save_gate_preflight_batch
        .DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_PREFLIGHT_BATCH_SUMMARY_SCHEMA
    )
    contract = durable_executor_authoring_save_gate_open_admission_batch.build_durable_executor_authoring_save_gate_open_admission_batch_contract(
        requested=True,
        section_193_200_save_gate_preflight_summary=preflight_summary,
    )
    summary = durable_executor_authoring_save_gate_open_admission_batch.summarize_durable_executor_authoring_save_gate_open_admission_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_save_gate_open_admission_batch_count": 1,
        "section_193_200_summary_schema_matches_count": 1,
        "section_193_200_summary_passed_count": 1,
        "section_193_200_save_gate_preflight_ready_count": 1,
        "section_193_200_save_gate_still_closed_count": 1,
        "section_193_200_write_and_live_outputs_blocked_count": 1,
        "section_201_explicit_save_gate_open_approved_count": 1,
        "section_202_save_gate_opened_count": 1,
        "section_203_save_command_admission_contract_accepted_count": 1,
        "section_204_save_command_admitted_count": 1,
        "section_205_save_command_dispatch_dry_run_ready_count": 1,
        "section_206_save_command_execution_dry_run_ready_count": 1,
        "section_207_save_command_result_readback_dry_run_ready_count": 1,
        "section_208_final_pre_save_execution_ready_count": 1,
        "durable_authoring_enabled_count": 1,
        "durable_executor_opened_count": 1,
        "durable_authoring_command_no_save_execution_ready_count": 1,
        "final_no_save_release_ready_count": 1,
        "durable_authoring_save_gate_preflight_ready_count": 1,
        "save_command_admission_preflight_ready_count": 1,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_command_dispatched_count": 0,
        "save_command_executed_count": 0,
        "save_true_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "compile_save_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "live_durable_authoring_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    for key in (
        durable_executor_authoring_save_gate_open_admission_batch
        .SAVE_GATE_OPEN_ADMISSION_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_save_gate_open_admission_batch
                .WRITE_AND_LIVE_BLOCKED_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_save_gate_open_admission_batch",
        "Sections 201-208 durable executor authoring save-gate open/admission batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 201-208 are bundled: explicit save-gate open approval, save gate open, save-command admission, dry-run dispatch readiness, dry-run execution readiness, dry-run result readback readiness, and final pre-save execution readiness.",
            "The batch does not dispatch or execute a live save command and does not allow save=true, save_asset, compile/save, delete, rename, package dirtying, live durable writes, or final durable release readiness.",
        ),
    )


def build_durable_executor_authoring_live_pre_save_checkpoint_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    open_admission_row = (
        build_durable_executor_authoring_save_gate_open_admission_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    open_admission_summary = _summary_from_row_actual(open_admission_row)
    open_admission_summary["schema"] = (
        durable_executor_authoring_save_gate_open_admission_batch
        .DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_OPEN_ADMISSION_BATCH_SUMMARY_SCHEMA
    )
    live_result = durable_executor_authoring_live_pre_save_checkpoint_batch.build_live_pre_save_read_only_result(
        bridge_reachable=True,
        ieta_slate_status_succeeded=True,
    )
    contract = durable_executor_authoring_live_pre_save_checkpoint_batch.build_durable_executor_authoring_live_pre_save_checkpoint_batch_contract(
        requested=True,
        section_201_208_save_gate_open_admission_summary=open_admission_summary,
        live_pre_save_read_only_result=live_result,
    )
    summary = durable_executor_authoring_live_pre_save_checkpoint_batch.summarize_durable_executor_authoring_live_pre_save_checkpoint_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_live_pre_save_checkpoint_batch_count": 1,
        "section_201_208_summary_schema_matches_count": 1,
        "section_201_208_summary_passed_count": 1,
        "section_201_208_pre_save_ready_count": 1,
        "section_201_208_write_and_live_outputs_blocked_count": 1,
        "live_result_schema_matches_count": 1,
        "live_result_read_only_count": 1,
        "live_bridge_reachable_count": 1,
        "ieta_slate_status_succeeded_count": 1,
        "target_path_matches_count": 1,
        "read_only_target_check_performed_count": 1,
        "target_absent_for_new_temp_asset_count": 1,
        "target_directory_absent_or_empty_count": 1,
        "dirty_content_packages_zero_count": 1,
        "dirty_map_packages_zero_count": 1,
        "live_result_write_outputs_blocked_count": 1,
        "section_209_live_bridge_recovered_count": 1,
        "section_210_live_pre_save_read_only_target_checked_count": 1,
        "section_211_live_target_absence_confirmed_count": 1,
        "section_212_live_dirty_package_boundary_clean_count": 1,
        "section_213_live_overwrite_boundary_safe_for_new_temp_asset_count": 1,
        "section_214_live_save_dispatch_final_checkpoint_ready_count": 1,
        "section_215_live_save_execution_readback_plan_ready_count": 1,
        "section_216_actual_save_requires_final_user_checkpoint_count": 1,
        "durable_authoring_enabled_count": 1,
        "durable_executor_opened_count": 1,
        "save_gate_open_allowed_count": 1,
        "save_command_admitted_count": 1,
        "final_pre_save_execution_ready_count": 1,
        "durable_authoring_allowed_count": 0,
        "final_durable_release_ready_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_command_dispatched_count": 0,
        "save_command_executed_count": 0,
        "save_true_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "compile_save_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "live_durable_authoring_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }
    for key in (
        durable_executor_authoring_live_pre_save_checkpoint_batch
        .LIVE_PRE_SAVE_CHECKPOINT_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_live_pre_save_checkpoint_batch
                .WRITE_AND_LIVE_BLOCKED_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_live_pre_save_checkpoint_batch",
        "Sections 209-216 durable executor authoring live pre-save checkpoint batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 209-216 are bundled: bridge recovery, read-only target check, target absence, dirty-package boundary, overwrite boundary for a new temp asset, final save dispatch checkpoint, save execution/readback plan, and final user checkpoint requirement.",
            "The batch does not dispatch or execute a save command and does not allow save=true, save_asset, compile/save, delete, rename, package dirtying, live durable writes, or final durable release readiness.",
        ),
    )


def build_durable_executor_authoring_live_actual_save_execution_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    live_pre_save_row = (
        build_durable_executor_authoring_live_pre_save_checkpoint_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    live_pre_save_summary = _summary_from_row_actual(live_pre_save_row)
    live_pre_save_summary["schema"] = (
        durable_executor_authoring_live_pre_save_checkpoint_batch
        .DURABLE_EXECUTOR_AUTHORING_LIVE_PRE_SAVE_CHECKPOINT_BATCH_SUMMARY_SCHEMA
    )
    execution_result = durable_executor_authoring_live_actual_save_execution_batch.build_live_actual_save_execution_result(
        package_file_size_bytes=24133,
    )
    readback_result = durable_executor_authoring_live_actual_save_execution_batch.build_live_actual_save_readback_result(
        package_file_size_bytes=24133,
    )
    contract = durable_executor_authoring_live_actual_save_execution_batch.build_durable_executor_authoring_live_actual_save_execution_batch_contract(
        requested=True,
        section_209_216_live_pre_save_checkpoint_summary=live_pre_save_summary,
        live_actual_save_execution_result=execution_result,
        live_actual_save_readback_result=readback_result,
    )
    summary = durable_executor_authoring_live_actual_save_execution_batch.summarize_durable_executor_authoring_live_actual_save_execution_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_live_actual_save_execution_batch_count": 1,
        "section_209_216_summary_schema_matches_count": 1,
        "section_209_216_summary_passed_count": 1,
        "section_209_216_live_pre_save_checkpoint_ready_count": 1,
        "section_209_216_write_outputs_closed_count": 1,
        "execution_result_schema_matches_count": 1,
        "execution_target_path_matches_count": 1,
        "execution_target_directory_matches_count": 1,
        "execution_asset_loaded_count": 1,
        "execution_asset_class_is_blueprint_count": 1,
        "execution_blueprint_compile_succeeded_count": 1,
        "execution_save_asset_succeeded_count": 1,
        "execution_live_command_succeeded_count": 1,
        "execution_write_performed_count": 1,
        "execution_post_asset_exists_count": 1,
        "execution_package_file_exists_count": 1,
        "execution_dirty_packages_cleared_count": 1,
        "execution_delete_rename_blocked_count": 1,
        "execution_has_no_error_count": 1,
        "readback_result_schema_matches_count": 1,
        "readback_result_read_only_count": 1,
        "readback_target_path_matches_count": 1,
        "readback_target_directory_matches_count": 1,
        "readback_asset_confirmed_count": 1,
        "readback_package_file_confirmed_count": 1,
        "readback_dirty_packages_zero_count": 1,
        "readback_write_outputs_blocked_count": 1,
        "durable_authoring_enabled_count": 1,
        "durable_executor_opened_count": 1,
        "durable_authoring_allowed_count": 1,
        "save_gate_open_allowed_count": 1,
        "save_gate_opened_count": 1,
        "save_command_admitted_count": 1,
        "final_pre_save_execution_ready_count": 1,
        "live_pre_save_checkpoint_ready_count": 1,
        "actual_save_execution_requires_final_user_checkpoint_count": 0,
        "save_command_dispatched_count": 1,
        "save_command_executed_count": 1,
        "save_true_allowed_count": 1,
        "save_asset_allowed_count": 1,
        "compile_save_allowed_count": 1,
        "asset_write_performed_count": 1,
        "package_dirty_marked_count": 1,
        "live_durable_authoring_allowed_count": 1,
        "live_command_dispatched_count": 1,
        "live_command_executed_count": 1,
        "final_durable_release_ready_count": 1,
        "save_delete_rename_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
    }
    for key in (
        durable_executor_authoring_live_actual_save_execution_batch
        .LIVE_ACTUAL_SAVE_EXECUTION_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_live_actual_save_execution_batch
                .DELETE_RENAME_BLOCKED_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_live_actual_save_execution_batch",
        "Sections 217-224 durable executor authoring live actual save execution batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 217-224 are bundled: explicit final checkpoint approval consumed, live save command dispatch/execution, temp Blueprint write, compile/save, save result confirmation, readback, dirty-package cleanup, and final durable release readiness.",
            "The batch is target-scoped to /Game/_MCP_Temp/DurableSaveGate/BP_DurableSaveGatePrep and keeps delete/rename closed.",
        ),
    )


def build_durable_executor_authoring_live_save_stability_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    actual_save_row = (
        build_durable_executor_authoring_live_actual_save_execution_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    actual_save_summary = _summary_from_row_actual(actual_save_row)
    actual_save_summary["schema"] = (
        durable_executor_authoring_live_actual_save_execution_batch
        .DURABLE_EXECUTOR_AUTHORING_LIVE_ACTUAL_SAVE_EXECUTION_BATCH_SUMMARY_SCHEMA
    )
    stability_result = durable_executor_authoring_live_save_stability_batch.build_live_save_stability_result(
        package_file_size_bytes=24133,
    )
    contract = durable_executor_authoring_live_save_stability_batch.build_durable_executor_authoring_live_save_stability_batch_contract(
        requested=True,
        section_217_224_live_actual_save_execution_summary=actual_save_summary,
        live_save_stability_result=stability_result,
    )
    summary = durable_executor_authoring_live_save_stability_batch.summarize_durable_executor_authoring_live_save_stability_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_live_save_stability_batch_count": 1,
        "section_217_224_summary_schema_matches_count": 1,
        "section_217_224_summary_passed_count": 1,
        "section_217_224_actual_save_ready_count": 1,
        "section_217_224_delete_rename_closed_count": 1,
        "stability_result_schema_matches_count": 1,
        "target_path_matches_count": 1,
        "target_directory_matches_count": 1,
        "compile_api_fixed_count": 1,
        "legacy_compile_helper_mismatch_documented_count": 1,
        "partial_save_recovery_verified_count": 1,
        "idempotent_resave_verified_count": 1,
        "save_readback_schema_strengthened_count": 1,
        "dirty_package_stability_verified_count": 1,
        "production_path_untouched_count": 1,
        "delete_rename_cleanup_still_gated_count": 1,
        "stability_has_no_error_count": 1,
        "durable_authoring_enabled_count": 1,
        "durable_executor_opened_count": 1,
        "durable_authoring_allowed_count": 1,
        "save_gate_open_allowed_count": 1,
        "save_gate_opened_count": 1,
        "save_command_admitted_count": 1,
        "save_command_dispatched_count": 1,
        "save_command_executed_count": 1,
        "save_true_allowed_count": 1,
        "save_asset_allowed_count": 1,
        "compile_save_allowed_count": 1,
        "asset_write_performed_count": 1,
        "package_dirty_marked_count": 1,
        "live_durable_authoring_allowed_count": 1,
        "live_command_dispatched_count": 1,
        "live_command_executed_count": 1,
        "final_durable_release_ready_count": 1,
        "cleanup_allowed_count": 0,
        "cleanup_executed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "production_path_write_allowed_count": 0,
        "production_path_write_executed_count": 0,
    }
    for key in (
        durable_executor_authoring_live_save_stability_batch
        .LIVE_SAVE_STABILITY_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_live_save_stability_batch
                .DELETE_RENAME_CLEANUP_BLOCKED_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_live_save_stability_batch",
        "Sections 225-232 durable executor authoring live save stability batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 225-232 stabilize the target-scoped save path: UE 5.7 compile API is fixed, the legacy compile helper mismatch is documented, partial-save recovery and idempotent re-save/readback are verified, and dirty-package stability is proven.",
            "The batch keeps cleanup, delete, rename, and production path writes closed.",
        ),
    )


def build_durable_executor_authoring_cleanup_delete_dry_run_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    stability_row = (
        build_durable_executor_authoring_live_save_stability_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    stability_summary = _summary_from_row_actual(stability_row)
    stability_summary["schema"] = (
        durable_executor_authoring_live_save_stability_batch
        .DURABLE_EXECUTOR_AUTHORING_LIVE_SAVE_STABILITY_BATCH_SUMMARY_SCHEMA
    )
    cleanup_result = durable_executor_authoring_cleanup_delete_dry_run_batch.build_cleanup_delete_dry_run_result(
        package_file_size_bytes=24133,
    )
    contract = durable_executor_authoring_cleanup_delete_dry_run_batch.build_durable_executor_authoring_cleanup_delete_dry_run_batch_contract(
        requested=True,
        section_225_232_live_save_stability_summary=stability_summary,
        cleanup_delete_dry_run_result=cleanup_result,
    )
    summary = durable_executor_authoring_cleanup_delete_dry_run_batch.summarize_durable_executor_authoring_cleanup_delete_dry_run_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_cleanup_delete_dry_run_batch_count": 1,
        "section_225_232_summary_schema_matches_count": 1,
        "section_225_232_summary_passed_count": 1,
        "section_225_232_save_stability_ready_count": 1,
        "section_225_232_cleanup_delete_closed_count": 1,
        "result_schema_matches_count": 1,
        "cleanup_target_scope_confirmed_count": 1,
        "saved_asset_pre_delete_readback_confirmed_count": 1,
        "cleanup_delete_dry_run_plan_accepted_count": 1,
        "delete_target_isolation_proved_count": 1,
        "dirty_package_no_delete_boundary_clean_count": 1,
        "delete_command_dispatch_dry_run_ready_count": 1,
        "delete_result_readback_dry_run_ready_count": 1,
        "dry_run_blocks_actual_delete_outputs_count": 1,
        "result_has_no_error_count": 1,
        "final_durable_release_ready_count": 1,
        "live_save_stability_ready_count": 1,
        "cleanup_delete_dry_run_allowed_count": 1,
        "cleanup_delete_dry_run_ready_count": 1,
        "cleanup_allowed_count": 0,
        "cleanup_executed_count": 0,
        "delete_command_dispatched_count": 0,
        "delete_command_executed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "production_path_write_allowed_count": 0,
        "production_path_write_executed_count": 0,
    }
    for key in (
        durable_executor_authoring_cleanup_delete_dry_run_batch
        .CLEANUP_DELETE_DRY_RUN_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_cleanup_delete_dry_run_batch
                .BLOCKED_DELETE_RENAME_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_cleanup_delete_dry_run_batch",
        "Sections 233-240 durable executor authoring cleanup/delete dry-run batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 233-240 prove target-scoped cleanup/delete dry-run readiness after saved temp Blueprint stability.",
            "The batch does not dispatch or execute cleanup/delete, keeps delete_asset/rename_asset closed, and requires a final user checkpoint before actual deletion.",
        ),
    )


def build_durable_executor_authoring_rename_overwrite_dry_run_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    cleanup_row = (
        build_durable_executor_authoring_cleanup_delete_dry_run_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    cleanup_summary = _summary_from_row_actual(cleanup_row)
    cleanup_summary["schema"] = (
        durable_executor_authoring_cleanup_delete_dry_run_batch
        .DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_DRY_RUN_BATCH_SUMMARY_SCHEMA
    )
    rename_result = durable_executor_authoring_rename_overwrite_dry_run_batch.build_rename_overwrite_dry_run_result()
    contract = durable_executor_authoring_rename_overwrite_dry_run_batch.build_durable_executor_authoring_rename_overwrite_dry_run_batch_contract(
        requested=True,
        section_233_240_cleanup_delete_dry_run_summary=cleanup_summary,
        rename_overwrite_dry_run_result=rename_result,
    )
    summary = durable_executor_authoring_rename_overwrite_dry_run_batch.summarize_durable_executor_authoring_rename_overwrite_dry_run_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_rename_overwrite_dry_run_batch_count": 1,
        "section_233_240_summary_schema_matches_count": 1,
        "section_233_240_summary_passed_count": 1,
        "section_233_240_cleanup_delete_dry_run_ready_count": 1,
        "section_233_240_destructive_outputs_closed_count": 1,
        "result_schema_matches_count": 1,
        "rename_source_scope_confirmed_count": 1,
        "rename_destination_scope_confirmed_count": 1,
        "overwrite_policy_denies_existing_destination_count": 1,
        "rename_overwrite_dry_run_plan_accepted_count": 1,
        "rename_collision_boundary_clean_count": 1,
        "rename_dirty_package_boundary_clean_count": 1,
        "rename_result_readback_dry_run_ready_count": 1,
        "dry_run_blocks_actual_rename_outputs_count": 1,
        "result_has_no_error_count": 1,
        "final_durable_release_ready_count": 1,
        "cleanup_delete_dry_run_ready_count": 1,
        "rename_overwrite_dry_run_allowed_count": 1,
        "rename_overwrite_dry_run_ready_count": 1,
        "cleanup_allowed_count": 0,
        "cleanup_executed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "rename_command_dispatched_count": 0,
        "rename_command_executed_count": 0,
        "overwrite_allowed_count": 0,
        "overwrite_executed_count": 0,
        "production_path_write_allowed_count": 0,
        "production_path_write_executed_count": 0,
    }
    for key in (
        durable_executor_authoring_rename_overwrite_dry_run_batch
        .RENAME_OVERWRITE_DRY_RUN_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_rename_overwrite_dry_run_batch
                .BLOCKED_RENAME_OVERWRITE_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_rename_overwrite_dry_run_batch",
        "Sections 241-248 durable executor authoring rename/overwrite dry-run batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 241-248 prove target-scoped rename/overwrite dry-run readiness with a deny-existing destination policy.",
            "The batch does not dispatch or execute rename/overwrite/delete and keeps production path writes closed.",
        ),
    )


def build_durable_executor_authoring_actor_bp_expansion_dry_run_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    rename_row = (
        build_durable_executor_authoring_rename_overwrite_dry_run_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    rename_summary = _summary_from_row_actual(rename_row)
    rename_summary["schema"] = (
        durable_executor_authoring_rename_overwrite_dry_run_batch
        .DURABLE_EXECUTOR_AUTHORING_RENAME_OVERWRITE_DRY_RUN_BATCH_SUMMARY_SCHEMA
    )
    actor_result = durable_executor_authoring_actor_bp_expansion_dry_run_batch.build_actor_bp_expansion_dry_run_result()
    contract = durable_executor_authoring_actor_bp_expansion_dry_run_batch.build_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract(
        requested=True,
        section_241_248_rename_overwrite_dry_run_summary=rename_summary,
        actor_bp_expansion_dry_run_result=actor_result,
    )
    summary = durable_executor_authoring_actor_bp_expansion_dry_run_batch.summarize_durable_executor_authoring_actor_bp_expansion_dry_run_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_actor_bp_expansion_dry_run_batch_count": 1,
        "section_241_248_summary_schema_matches_count": 1,
        "section_241_248_summary_passed_count": 1,
        "section_241_248_rename_overwrite_dry_run_ready_count": 1,
        "section_241_248_destructive_outputs_closed_count": 1,
        "result_schema_matches_count": 1,
        "actor_blueprint_scope_confirmed_count": 1,
        "variable_authoring_plan_accepted_count": 1,
        "component_authoring_plan_accepted_count": 1,
        "default_authoring_plan_accepted_count": 1,
        "compile_save_dependency_declared_count": 1,
        "temp_package_mutation_boundary_clean_count": 1,
        "actor_authoring_readback_dry_run_ready_count": 1,
        "dry_run_blocks_actual_actor_authoring_outputs_count": 1,
        "result_has_no_error_count": 1,
        "final_durable_release_ready_count": 1,
        "rename_overwrite_dry_run_ready_count": 1,
        "actor_bp_expansion_dry_run_allowed_count": 1,
        "actor_bp_expansion_dry_run_ready_count": 1,
        "actual_actor_bp_authoring_requires_final_user_checkpoint_count": 1,
    }
    for key in (
        durable_executor_authoring_actor_bp_expansion_dry_run_batch
        .ACTOR_BP_EXPANSION_DRY_RUN_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_actor_bp_expansion_dry_run_batch
                .BLOCKED_ACTOR_BP_AUTHORING_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_actor_bp_expansion_dry_run_batch",
        "Sections 249-256 durable executor actor Blueprint expansion dry-run batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 249-256 prove Actor Blueprint variable/component/default authoring dry-run readiness under /Game/_MCP_Temp.",
            "The batch does not dispatch or execute Blueprint mutation, compile, save, delete, rename, overwrite, or production writes.",
        ),
    )


def build_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    actor_row = (
        build_durable_executor_authoring_actor_bp_expansion_dry_run_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    actor_summary = _summary_from_row_actual(actor_row)
    actor_summary["schema"] = (
        durable_executor_authoring_actor_bp_expansion_dry_run_batch
        .DURABLE_EXECUTOR_AUTHORING_ACTOR_BP_EXPANSION_DRY_RUN_BATCH_SUMMARY_SCHEMA
    )
    preflight_result = durable_executor_authoring_live_actor_bp_authoring_preflight_batch.build_live_actor_bp_authoring_preflight_result()
    contract = durable_executor_authoring_live_actor_bp_authoring_preflight_batch.build_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract(
        requested=True,
        section_249_256_actor_bp_expansion_dry_run_summary=actor_summary,
        live_actor_bp_authoring_preflight_result=preflight_result,
    )
    summary = durable_executor_authoring_live_actor_bp_authoring_preflight_batch.summarize_durable_executor_authoring_live_actor_bp_authoring_preflight_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_live_actor_bp_authoring_preflight_batch_count": 1,
        "section_249_256_summary_schema_matches_count": 1,
        "section_249_256_summary_passed_count": 1,
        "section_249_256_actor_bp_expansion_dry_run_ready_count": 1,
        "section_249_256_actor_bp_mutation_outputs_closed_count": 1,
        "result_schema_matches_count": 1,
        "live_actor_bp_command_envelope_scoped_count": 1,
        "live_actor_bp_read_only_target_preflight_ready_count": 1,
        "live_actor_bp_mutation_sequence_planned_count": 1,
        "live_actor_bp_compile_save_ordering_verified_count": 1,
        "live_actor_bp_rollback_boundary_revalidated_count": 1,
        "live_actor_bp_readback_evidence_plan_ready_count": 1,
        "live_actor_bp_final_checkpoint_required_count": 1,
        "dry_run_blocks_actual_live_actor_authoring_outputs_count": 1,
        "result_has_no_error_count": 1,
        "final_durable_release_ready_count": 1,
        "actor_bp_expansion_dry_run_ready_count": 1,
        "live_actor_bp_authoring_preflight_allowed_count": 1,
        "live_actor_bp_authoring_checkpoint_ready_count": 1,
        "actual_live_actor_bp_authoring_requires_final_user_checkpoint_count": 1,
    }
    for key in (
        durable_executor_authoring_live_actor_bp_authoring_preflight_batch
        .LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_live_actor_bp_authoring_preflight_batch
                .BLOCKED_LIVE_ACTOR_BP_AUTHORING_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_live_actor_bp_authoring_preflight_batch",
        "Sections 257-264 durable executor live Actor Blueprint authoring preflight batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 257-264 prove the live Actor Blueprint authoring command envelope, read-only target preflight, compile/save order, rollback boundary, and readback evidence plan.",
            "The batch keeps actual variable/component/default mutation, compile, save, delete, rename, overwrite, and production writes closed until a final user checkpoint.",
        ),
    )


def build_durable_executor_authoring_live_actor_bp_actual_authoring_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    preflight_row = (
        build_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        )
    )
    preflight_summary = _summary_from_row_actual(preflight_row)
    preflight_summary["schema"] = (
        durable_executor_authoring_live_actor_bp_authoring_preflight_batch
        .DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_BATCH_SUMMARY_SCHEMA
    )
    actual_result = durable_executor_authoring_live_actor_bp_actual_authoring_batch.build_live_actor_bp_actual_authoring_result()
    contract = durable_executor_authoring_live_actor_bp_actual_authoring_batch.build_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract(
        requested=True,
        section_257_264_live_actor_bp_preflight_summary=preflight_summary,
        live_actor_bp_actual_authoring_result=actual_result,
    )
    summary = durable_executor_authoring_live_actor_bp_actual_authoring_batch.summarize_durable_executor_authoring_live_actor_bp_actual_authoring_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_live_actor_bp_actual_authoring_batch_count": 1,
        "section_257_264_summary_schema_matches_count": 1,
        "section_257_264_summary_passed_count": 1,
        "section_257_264_live_actor_bp_preflight_ready_count": 1,
        "section_257_264_mutation_outputs_closed_count": 1,
        "result_schema_matches_count": 1,
        "actual_execution_checkpoint_satisfied_count": 1,
        "target_scope_reconfirmed_count": 1,
        "variable_authoring_executed_count": 1,
        "component_authoring_executed_count": 1,
        "default_authoring_executed_count": 1,
        "compile_save_executed_count": 1,
        "readback_verified_count": 1,
        "dirty_baseline_preserved_count": 1,
        "destructive_outputs_closed_count": 1,
        "result_has_no_error_count": 1,
        "final_durable_release_ready_count": 1,
        "actual_live_actor_bp_authoring_requires_final_user_checkpoint_count": 0,
        "actual_live_actor_bp_authoring_final_checkpoint_satisfied_count": 1,
        "variable_add_command_dispatched_count": 1,
        "variable_add_command_executed_count": 1,
        "component_add_command_dispatched_count": 1,
        "component_add_command_executed_count": 1,
        "default_write_command_dispatched_count": 1,
        "default_write_command_executed_count": 1,
        "actor_bp_authoring_command_dispatched_count": 1,
        "actor_bp_authoring_command_executed_count": 1,
        "actor_bp_authoring_compile_dispatched_count": 1,
        "actor_bp_authoring_compile_executed_count": 1,
        "actor_bp_authoring_save_dispatched_count": 1,
        "actor_bp_authoring_save_executed_count": 1,
        "actor_bp_authoring_asset_write_performed_count": 1,
        "actor_bp_authoring_package_dirty_marked_count": 1,
        "actor_bp_authoring_target_dirty_after_count": 0,
        "actor_bp_authoring_external_dirty_preserved_count": 1,
        "cleanup_allowed_count": 0,
        "cleanup_executed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "rename_command_dispatched_count": 0,
        "rename_command_executed_count": 0,
        "overwrite_allowed_count": 0,
        "overwrite_executed_count": 0,
        "production_path_write_allowed_count": 0,
        "production_path_write_executed_count": 0,
    }
    for key in (
        durable_executor_authoring_live_actor_bp_actual_authoring_batch
        .LIVE_ACTOR_BP_ACTUAL_AUTHORING_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_live_actor_bp_actual_authoring_batch
                .BLOCKED_LIVE_ACTOR_BP_DESTRUCTIVE_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_live_actor_bp_actual_authoring_batch",
        "Sections 265-272 durable executor live Actor Blueprint actual authoring batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 265-272 prove actual target-scoped Actor Blueprint variable, component, and default/tag authoring under /Game/_MCP_Temp.",
            "The batch records that pre-existing external dirty state was preserved and delete/rename/overwrite/production writes remained closed.",
        ),
    )


def build_durable_executor_authoring_live_actor_bp_component_default_readback_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    actual_row = build_durable_executor_authoring_live_actor_bp_actual_authoring_batch_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    actual_summary = _summary_from_row_actual(actual_row)
    actual_summary["schema"] = (
        durable_executor_authoring_live_actor_bp_actual_authoring_batch
        .DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_ACTUAL_AUTHORING_BATCH_SUMMARY_SCHEMA
    )
    readback_result = durable_executor_authoring_live_actor_bp_component_default_readback_batch.build_live_actor_bp_component_default_readback_result()
    contract = durable_executor_authoring_live_actor_bp_component_default_readback_batch.build_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract(
        requested=True,
        section_265_272_live_actor_bp_actual_authoring_summary=actual_summary,
        live_actor_bp_component_default_readback_result=readback_result,
    )
    summary = durable_executor_authoring_live_actor_bp_component_default_readback_batch.summarize_durable_executor_authoring_live_actor_bp_component_default_readback_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_live_actor_bp_component_default_readback_batch_count": 1,
        "section_265_272_summary_schema_matches_count": 1,
        "section_265_272_summary_passed_count": 1,
        "section_265_272_live_actor_bp_actual_authoring_ready_count": 1,
        "section_265_272_destructive_outputs_closed_count": 1,
        "result_schema_matches_count": 1,
        "actual_authoring_summary_ready_count": 1,
        "class_type_readback_verified_count": 1,
        "variable_default_type_readback_verified_count": 1,
        "component_template_type_readback_verified_count": 1,
        "cdo_default_tag_readback_verified_count": 1,
        "broader_blueprint_class_authoring_guard_verified_count": 1,
        "readback_no_write_verified_count": 1,
        "result_has_no_error_count": 1,
        "final_durable_release_ready_count": 1,
    }
    for key in (
        durable_executor_authoring_live_actor_bp_component_default_readback_batch
        .LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_live_actor_bp_component_default_readback_batch
                .BLOCKED_LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_live_actor_bp_component_default_readback_batch",
        "Sections 273-280 durable executor live Actor Blueprint component/default readback batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 273-280 prove readback-only Actor Blueprint class, variable default/type, component template/type, and CDO tag evidence after actual _MCP_Temp authoring.",
            "The batch keeps new mutation, compile, save, delete, rename, overwrite, production writes, and unsupported broader Blueprint class authoring closed.",
        ),
    )


def build_durable_executor_authoring_function_diagnostics_graph_layout_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    readback_row = build_durable_executor_authoring_live_actor_bp_component_default_readback_batch_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    readback_summary = _summary_from_row_actual(readback_row)
    readback_summary["schema"] = (
        durable_executor_authoring_live_actor_bp_component_default_readback_batch
        .DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_BATCH_SUMMARY_SCHEMA
    )
    diagnostics_result = durable_executor_authoring_function_diagnostics_graph_layout_batch.build_function_diagnostics_graph_layout_result()
    contract = durable_executor_authoring_function_diagnostics_graph_layout_batch.build_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract(
        requested=True,
        section_273_280_component_default_readback_summary=readback_summary,
        function_diagnostics_graph_layout_result=diagnostics_result,
    )
    summary = durable_executor_authoring_function_diagnostics_graph_layout_batch.summarize_durable_executor_authoring_function_diagnostics_graph_layout_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_function_diagnostics_graph_layout_batch_count": 1,
        "section_273_280_summary_schema_matches_count": 1,
        "section_273_280_summary_passed_count": 1,
        "section_273_280_component_default_readback_ready_count": 1,
        "section_273_280_outputs_closed_count": 1,
        "result_schema_matches_count": 1,
        "actor_bp_readback_summary_ready_count": 1,
        "target_scope_reconfirmed_count": 1,
        "function_call_diagnostics_ready_count": 1,
        "pin_contract_diagnostics_ready_count": 1,
        "graph_layout_diagnostics_ready_count": 1,
        "repair_suggestions_generated_count": 1,
        "auto_graph_repair_execution_blocked_count": 1,
        "diagnostics_no_write_boundary_verified_count": 1,
        "result_has_no_error_count": 1,
        "graph_layout_repair_suggestions_ready_count": 1,
        "function_diagnostics_graph_layout_no_write_verified_count": 1,
        "final_durable_release_ready_count": 1,
    }
    for key in (
        durable_executor_authoring_function_diagnostics_graph_layout_batch
        .FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_function_diagnostics_graph_layout_batch
                .BLOCKED_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_function_diagnostics_graph_layout_batch",
        "Sections 281-288 durable executor function diagnostics and graph layout suggestion batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 281-288 prove diagnostic-only function call, pin contract, graph layout, spacing, and manual repair suggestion readiness.",
            "The batch keeps automatic graph repair, node movement, pin rewiring, compile, save, delete, rename, overwrite, and production writes closed.",
        ),
    )


def build_durable_executor_authoring_cleanup_delete_actual_execution_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    diagnostics_row = build_durable_executor_authoring_function_diagnostics_graph_layout_batch_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    diagnostics_summary = _summary_from_row_actual(diagnostics_row)
    diagnostics_summary["schema"] = (
        durable_executor_authoring_function_diagnostics_graph_layout_batch
        .DURABLE_EXECUTOR_AUTHORING_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_BATCH_SUMMARY_SCHEMA
    )
    delete_result = durable_executor_authoring_cleanup_delete_actual_execution_batch.build_cleanup_delete_actual_execution_result()
    contract = durable_executor_authoring_cleanup_delete_actual_execution_batch.build_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract(
        requested=True,
        section_281_288_function_diagnostics_graph_layout_summary=diagnostics_summary,
        cleanup_delete_actual_execution_result=delete_result,
    )
    summary = durable_executor_authoring_cleanup_delete_actual_execution_batch.summarize_durable_executor_authoring_cleanup_delete_actual_execution_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_cleanup_delete_actual_execution_batch_count": 1,
        "section_281_288_summary_schema_matches_count": 1,
        "section_281_288_summary_passed_count": 1,
        "section_281_288_function_diagnostics_graph_layout_ready_count": 1,
        "section_281_288_outputs_closed_count": 1,
        "result_schema_matches_count": 1,
        "actual_checkpoint_satisfied_count": 1,
        "delete_target_scope_isolated_count": 1,
        "delete_preflight_verified_count": 1,
        "delete_asset_executed_count": 1,
        "delete_readback_verified_count": 1,
        "external_dirty_baseline_preserved_count": 1,
        "non_delete_destructive_outputs_closed_count": 1,
        "result_has_no_error_count": 1,
        "final_durable_release_ready_count": 1,
        "delete_asset_allowed_count": 1,
        "delete_asset_executed_output_count": 1,
    }
    for key in (
        durable_executor_authoring_cleanup_delete_actual_execution_batch
        .CLEANUP_DELETE_ACTUAL_EXECUTION_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_cleanup_delete_actual_execution_batch
                .BLOCKED_CLEANUP_DELETE_ACTUAL_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_cleanup_delete_actual_execution_batch",
        "Sections 289-296 durable executor cleanup/delete actual execution batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 289-296 prove a single isolated /Game/_MCP_Temp target delete after readback and diagnostics gates.",
            "The batch records delete readback and external dirty preservation while broad cleanup, rename, overwrite, compile/save, and production writes remain closed.",
        ),
    )


def build_durable_executor_authoring_post_delete_recreation_reset_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    cleanup_delete_row = build_durable_executor_authoring_cleanup_delete_actual_execution_batch_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    cleanup_delete_summary = _summary_from_row_actual(cleanup_delete_row)
    cleanup_delete_summary["schema"] = (
        durable_executor_authoring_cleanup_delete_actual_execution_batch
        .DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_ACTUAL_EXECUTION_BATCH_SUMMARY_SCHEMA
    )
    reset_result = durable_executor_authoring_post_delete_recreation_reset_batch.build_post_delete_recreation_reset_result()
    contract = durable_executor_authoring_post_delete_recreation_reset_batch.build_durable_executor_authoring_post_delete_recreation_reset_batch_contract(
        requested=True,
        section_289_296_cleanup_delete_actual_execution_summary=cleanup_delete_summary,
        post_delete_recreation_reset_result=reset_result,
    )
    summary = durable_executor_authoring_post_delete_recreation_reset_batch.summarize_durable_executor_authoring_post_delete_recreation_reset_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_post_delete_recreation_reset_batch_count": 1,
        "section_289_296_summary_schema_matches_count": 1,
        "section_289_296_summary_passed_count": 1,
        "section_289_296_cleanup_delete_actual_ready_count": 1,
        "section_289_296_non_delete_outputs_closed_count": 1,
        "result_schema_matches_count": 1,
        "post_delete_checkpoint_satisfied_count": 1,
        "deleted_target_absence_confirmed_count": 1,
        "recreation_plan_scoped_count": 1,
        "recreation_requires_explicit_checkpoint_count": 1,
        "readback_routes_reset_count": 1,
        "diagnostics_routes_reset_count": 1,
        "post_delete_no_write_boundary_verified_count": 1,
        "result_has_no_error_count": 1,
        "final_durable_release_ready_count": 1,
    }
    for key in (
        durable_executor_authoring_post_delete_recreation_reset_batch
        .POST_DELETE_RECREATION_RESET_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_post_delete_recreation_reset_batch
                .BLOCKED_POST_DELETE_RECREATION_RESET_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_post_delete_recreation_reset_batch",
        "Sections 297-304 durable executor post-delete recreation/readback reset batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 297-304 prove the deleted /Game/_MCP_Temp target is absent and stale readback/diagnostics paths are reset.",
            "The batch scopes future temp Actor Blueprint recreation behind a separate explicit checkpoint while recreate, readback, diagnostics, graph repair, compile/save, delete, rename, overwrite, and production writes remain closed.",
        ),
    )


def build_durable_executor_authoring_post_delete_recreation_actual_execution_batch_row(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    project_root: Path,
    planner_report: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    reset_row = build_durable_executor_authoring_post_delete_recreation_reset_batch_row(
        contract_summary,
        executor_summary,
        project_root,
        planner_report,
    )
    reset_summary = _summary_from_row_actual(reset_row)
    reset_summary["schema"] = (
        durable_executor_authoring_post_delete_recreation_reset_batch
        .DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_RESET_BATCH_SUMMARY_SCHEMA
    )
    recreate_result = durable_executor_authoring_post_delete_recreation_actual_execution_batch.build_post_delete_recreation_actual_execution_result()
    contract = durable_executor_authoring_post_delete_recreation_actual_execution_batch.build_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract(
        requested=True,
        section_297_304_post_delete_recreation_reset_summary=reset_summary,
        post_delete_recreation_actual_execution_result=recreate_result,
    )
    summary = durable_executor_authoring_post_delete_recreation_actual_execution_batch.summarize_durable_executor_authoring_post_delete_recreation_actual_execution_batches(
        [contract]
    )
    expected = {
        "summary_status": "passed",
        "durable_requested_executor_authoring_post_delete_recreation_actual_execution_batch_count": 1,
        "section_297_304_summary_schema_matches_count": 1,
        "section_297_304_summary_passed_count": 1,
        "section_297_304_post_delete_reset_ready_count": 1,
        "section_297_304_outputs_closed_count": 1,
        "result_schema_matches_count": 1,
        "recreation_checkpoint_satisfied_count": 1,
        "recreation_target_absence_preflight_count": 1,
        "recreate_actor_bp_executed_count": 1,
        "recreated_actor_bp_compiled_count": 1,
        "recreated_actor_bp_saved_count": 1,
        "recreated_actor_bp_readback_verified_count": 1,
        "recreation_dirty_baseline_preserved_count": 1,
        "authoring_expansion_outputs_closed_count": 1,
        "result_has_no_error_count": 1,
        "final_durable_release_ready_count": 1,
        "recreate_asset_allowed_count": 1,
        "recreate_command_dispatched_count": 1,
        "recreate_command_executed_count": 1,
        "actor_bp_authoring_compile_dispatched_count": 1,
        "actor_bp_authoring_compile_executed_count": 1,
        "actor_bp_authoring_save_dispatched_count": 1,
        "actor_bp_authoring_save_executed_count": 1,
        "actor_bp_authoring_asset_write_performed_count": 1,
        "actor_bp_authoring_package_dirty_marked_count": 0,
    }
    for key in (
        durable_executor_authoring_post_delete_recreation_actual_execution_batch
        .POST_DELETE_RECREATION_ACTUAL_EXECUTION_PATH_COUNT_KEYS
    ):
        expected[key] = 1
    expected.update(
        {
            key: 0
            for key in (
                durable_executor_authoring_post_delete_recreation_actual_execution_batch
                .BLOCKED_POST_DELETE_RECREATION_ACTUAL_OUTPUT_COUNT_KEYS
            )
        }
    )
    actual = {
        key: summary.get(key) if key != "summary_status" else summary.get("status")
        for key in expected
    }
    return row(
        "durable_executor_authoring_post_delete_recreation_actual_execution_batch",
        "Sections 305-312 durable executor post-delete recreation actual execution batch",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Sections 305-312 prove a single blank Actor Blueprint was recreated, compiled, saved, and read back under /Game/_MCP_Temp after the post-delete reset gate.",
            "The batch keeps variable/component/default authoring, diagnostics, graph repair, delete, rename, overwrite, cleanup, package dirty state, and production writes closed.",
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
        "release_boundary_version": "section_305_312_v143",
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
        build_durable_executor_authoring_command_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_dispatch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_execution_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_execution_evidence_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_completion_decision_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_completion_application_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_completion_result_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_result_readback_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_final_no_save_release_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_final_release_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_review_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_decision_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_promotion_barrier_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_open_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_enable_after_open_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_after_enable_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_dispatch_after_command_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_execution_after_dispatch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_execution_evidence_after_execution_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_completion_decision_after_evidence_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_completion_application_after_decision_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_completion_result_after_application_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_result_readback_after_result_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_final_no_save_release_after_readback_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_final_release_readiness_after_no_save_release_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_review_after_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_decision_after_review_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_promotion_barrier_after_decision_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_activation_readiness_after_promotion_barrier_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_request_dry_run_route_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_dispatch_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_dispatch_evidence_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_execution_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_execution_evidence_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_completion_decision_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_completion_application_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_completion_result_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_result_readback_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_final_no_save_release_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_final_release_readiness_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_review_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_decision_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_promotion_barrier_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_activation_readiness_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_open_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_open_promotion_barrier_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_path_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_command_admission_dry_run_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_release_boundary_consolidation_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_safety_boundary_unlock_decision_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_safety_boundary_unlock_record_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_safety_boundary_unlock_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_enable_after_safety_boundary_unlock_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_no_save_execution_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_save_gate_preflight_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_save_gate_open_admission_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_live_pre_save_checkpoint_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_live_actual_save_execution_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_live_save_stability_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_cleanup_delete_dry_run_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_rename_overwrite_dry_run_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_actor_bp_expansion_dry_run_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_live_actor_bp_actual_authoring_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_live_actor_bp_component_default_readback_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_function_diagnostics_graph_layout_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_cleanup_delete_actual_execution_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_post_delete_recreation_reset_batch_row(
            contract_summary,
            executor_summary,
            project_root,
            planner_report,
        ),
        build_durable_executor_authoring_post_delete_recreation_actual_execution_batch_row(
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
            "release_boundary_version": "section_305_312_v143",
            "mvp_decision_status": decision_contract["decision_status"],
            "temporary_blueprint_authoring_mvp_ready": decision_contract[
                "temporary_blueprint_authoring_mvp_ready"
            ],
            "durable_blueprint_authoring_mvp_ready": decision_contract["durable_blueprint_authoring_mvp_ready"],
            "failed_blocking_count": len(failed_blocking),
            "failed_blocking_ids": [item["id"] for item in failed_blocking],
            "ready_for_main_push": not failed_blocking,
            "durable_authoring_enabled": not failed_blocking,
            "durable_authoring_release_status": (
                "section_312_post_delete_recreation_actual_execution_ready"
                if not failed_blocking
                else "failed"
            ),
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
            "section_113_durable_executor_authoring_command_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_114_durable_executor_authoring_command_dispatch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_115_durable_executor_authoring_command_execution_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_116_durable_executor_authoring_command_execution_evidence_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_117_durable_executor_authoring_command_completion_decision_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_118_durable_executor_authoring_command_completion_application_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_119_durable_executor_authoring_command_completion_result_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_120_durable_executor_authoring_command_result_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_121_durable_executor_authoring_final_no_save_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_122_durable_executor_authoring_final_release_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_123_durable_executor_authoring_release_review_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_124_durable_executor_authoring_release_decision_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_125_durable_executor_authoring_release_promotion_barrier_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_126_durable_executor_authoring_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_127_durable_executor_authoring_open_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_128_durable_executor_authoring_enable_after_open_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_129_durable_executor_authoring_command_after_enable_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_130_durable_executor_authoring_command_dispatch_after_command_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_131_durable_executor_authoring_command_execution_after_dispatch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_132_durable_executor_authoring_command_execution_evidence_after_execution_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_133_durable_executor_authoring_command_completion_decision_after_evidence_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_134_durable_executor_authoring_command_completion_application_after_decision_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_135_durable_executor_authoring_command_completion_result_after_application_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_136_durable_executor_authoring_command_result_readback_after_result_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_137_durable_executor_authoring_final_no_save_release_after_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_138_durable_executor_authoring_final_release_readiness_after_no_save_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_139_durable_executor_authoring_release_review_after_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_140_durable_executor_authoring_release_decision_after_review_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_141_durable_executor_authoring_release_promotion_barrier_after_decision_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_142_durable_executor_authoring_activation_readiness_after_promotion_barrier_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_143_durable_executor_authoring_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_144_durable_executor_authoring_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_145_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_146_durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_147_durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_148_durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_149_durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_150_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_151_durable_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_152_durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_153_durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_154_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_155_durable_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_156_durable_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_157_durable_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_158_durable_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_159_durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_160_durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_161_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_162_durable_executor_authoring_command_request_dry_run_route_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_163_durable_executor_authoring_command_dispatch_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_164_durable_executor_authoring_command_dispatch_evidence_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_165_durable_executor_authoring_command_execution_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_166_durable_executor_authoring_command_execution_evidence_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_167_durable_executor_authoring_command_completion_decision_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_168_durable_executor_authoring_command_completion_application_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_169_durable_executor_authoring_command_completion_result_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_170_durable_executor_authoring_command_result_readback_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_171_durable_executor_authoring_final_no_save_release_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_172_durable_executor_authoring_final_release_readiness_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_173_durable_executor_authoring_release_review_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_174_durable_executor_authoring_release_decision_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_175_durable_executor_authoring_release_promotion_barrier_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_176_durable_executor_authoring_activation_readiness_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_177_durable_executor_authoring_open_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_178_durable_executor_authoring_open_promotion_barrier_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_179_durable_executor_authoring_command_path_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_180_durable_executor_authoring_command_admission_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_181_durable_executor_authoring_release_boundary_consolidation_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_182_durable_executor_authoring_safety_boundary_unlock_decision_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_183_durable_executor_authoring_safety_boundary_unlock_record_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_184_durable_executor_authoring_safety_boundary_unlock_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_185_durable_executor_authoring_enable_after_safety_boundary_unlock_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_186_192_durable_executor_authoring_no_save_execution_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_186_durable_executor_open_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_187_durable_executor_open_readiness_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_188_durable_authoring_command_allow_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_189_durable_authoring_command_dispatch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_190_durable_authoring_command_execution_evidence_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_191_durable_authoring_command_completion_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_192_durable_authoring_final_no_save_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_193_200_durable_executor_authoring_save_gate_preflight_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_193_durable_authoring_save_target_declaration_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_194_durable_authoring_ownership_marker_revalidation_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_195_durable_authoring_rollback_revalidation_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_196_durable_authoring_overwrite_rename_decision_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_197_durable_authoring_read_only_save_preflight_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_198_durable_authoring_save_command_admission_preflight_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_199_durable_authoring_save_gate_open_review_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_200_durable_authoring_final_save_gate_preflight_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_201_208_durable_executor_authoring_save_gate_open_admission_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_201_durable_authoring_explicit_save_gate_open_approval_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_202_durable_authoring_save_gate_open_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_203_durable_authoring_save_command_admission_contract_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_204_durable_authoring_save_command_admission_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_205_durable_authoring_save_command_dispatch_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_206_durable_authoring_save_command_execution_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_207_durable_authoring_save_command_result_readback_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_208_durable_authoring_final_pre_save_execution_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_209_216_durable_executor_authoring_live_pre_save_checkpoint_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_209_durable_authoring_live_bridge_recovery_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_210_durable_authoring_live_pre_save_read_only_target_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_211_durable_authoring_live_target_absence_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_212_durable_authoring_live_dirty_package_boundary_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_213_durable_authoring_live_overwrite_boundary_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_214_durable_authoring_live_save_dispatch_final_checkpoint_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_215_durable_authoring_live_save_execution_readback_plan_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_216_durable_authoring_actual_save_final_checkpoint_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_217_224_durable_executor_authoring_live_actual_save_execution_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_217_durable_authoring_actual_save_approval_consumed_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_218_durable_authoring_live_save_command_dispatch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_219_durable_authoring_live_temp_blueprint_write_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_220_durable_authoring_live_blueprint_compile_save_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_221_durable_authoring_live_save_asset_result_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_222_durable_authoring_live_saved_asset_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_223_durable_authoring_live_dirty_packages_cleared_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_224_durable_authoring_final_durable_release_ready_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_225_232_durable_executor_authoring_live_save_stability_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_225_durable_authoring_live_compile_api_fixed_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_226_durable_authoring_live_legacy_compile_helper_mismatch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_227_durable_authoring_live_partial_save_recovery_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_228_durable_authoring_live_idempotent_resave_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_229_durable_authoring_live_save_readback_schema_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_230_durable_authoring_live_dirty_package_stability_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_231_durable_authoring_live_production_path_boundary_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_232_durable_authoring_cleanup_delete_rename_gate_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_233_240_durable_executor_authoring_cleanup_delete_dry_run_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_233_durable_authoring_cleanup_target_scope_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_234_durable_authoring_saved_asset_pre_delete_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_235_durable_authoring_cleanup_delete_dry_run_plan_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_236_durable_authoring_delete_target_isolation_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_237_durable_authoring_no_delete_dirty_package_boundary_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_238_durable_authoring_delete_dispatch_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_239_durable_authoring_delete_result_readback_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_240_durable_authoring_actual_delete_final_checkpoint_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_241_248_durable_executor_authoring_rename_overwrite_dry_run_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_241_durable_authoring_rename_source_scope_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_242_durable_authoring_rename_destination_scope_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_243_durable_authoring_overwrite_policy_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_244_durable_authoring_rename_overwrite_dry_run_plan_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_245_durable_authoring_rename_collision_boundary_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_246_durable_authoring_rename_dirty_package_boundary_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_247_durable_authoring_rename_result_readback_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_248_durable_authoring_actual_rename_overwrite_final_checkpoint_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_249_256_durable_executor_authoring_actor_bp_expansion_dry_run_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_249_durable_authoring_actor_blueprint_scope_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_250_durable_authoring_variable_plan_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_251_durable_authoring_component_plan_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_252_durable_authoring_default_plan_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_253_durable_authoring_compile_save_dependency_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_254_durable_authoring_temp_package_mutation_boundary_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_255_durable_authoring_actor_readback_dry_run_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_256_durable_authoring_actual_actor_authoring_final_checkpoint_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_257_264_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_257_durable_authoring_live_actor_bp_command_envelope_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_258_durable_authoring_live_actor_bp_read_only_target_preflight_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_259_durable_authoring_live_actor_bp_mutation_sequence_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_260_durable_authoring_live_actor_bp_compile_save_order_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_261_durable_authoring_live_actor_bp_rollback_boundary_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_262_durable_authoring_live_actor_bp_readback_evidence_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_263_durable_authoring_live_actor_bp_final_checkpoint_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_264_durable_authoring_live_actor_bp_actual_authoring_closed_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_265_272_durable_executor_authoring_live_actor_bp_actual_authoring_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_265_durable_authoring_live_actor_bp_actual_execution_checkpoint_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_266_durable_authoring_live_actor_bp_target_scope_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_267_durable_authoring_live_actor_bp_variable_authoring_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_268_durable_authoring_live_actor_bp_component_authoring_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_269_durable_authoring_live_actor_bp_default_authoring_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_270_durable_authoring_live_actor_bp_compile_save_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_271_durable_authoring_live_actor_bp_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_272_durable_authoring_live_actor_bp_dirty_baseline_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_273_280_durable_executor_authoring_live_actor_bp_component_default_readback_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_273_durable_authoring_live_actor_bp_actual_summary_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_274_durable_authoring_live_actor_bp_class_type_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_275_durable_authoring_live_actor_bp_variable_default_type_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_276_durable_authoring_live_actor_bp_component_template_type_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_277_durable_authoring_live_actor_bp_cdo_default_tag_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_278_broader_blueprint_class_authoring_guard_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_279_durable_authoring_live_actor_bp_readback_no_write_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_280_durable_authoring_live_actor_bp_component_default_readback_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_281_288_durable_executor_authoring_function_diagnostics_graph_layout_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_281_durable_authoring_actor_bp_readback_summary_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_282_durable_authoring_function_call_diagnostics_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_283_durable_authoring_pin_contract_diagnostics_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_284_durable_authoring_graph_layout_diagnostics_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_285_durable_authoring_repair_suggestions_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_286_durable_authoring_auto_graph_repair_execution_blocked_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_287_durable_authoring_diagnostics_no_write_boundary_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_288_durable_authoring_function_diagnostics_graph_layout_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_289_296_durable_executor_authoring_cleanup_delete_actual_execution_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_289_durable_authoring_cleanup_delete_actual_checkpoint_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_290_durable_authoring_delete_target_scope_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_291_durable_authoring_delete_preflight_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_292_durable_authoring_delete_asset_execution_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_293_durable_authoring_delete_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_294_durable_authoring_external_dirty_baseline_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_295_durable_authoring_non_delete_destructive_outputs_closed_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_296_durable_authoring_cleanup_delete_actual_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_297_304_durable_executor_authoring_post_delete_recreation_reset_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_297_durable_authoring_post_delete_checkpoint_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_298_durable_authoring_deleted_target_absence_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_299_durable_authoring_recreation_plan_scope_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_300_durable_authoring_recreation_checkpoint_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_301_durable_authoring_readback_routes_reset_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_302_durable_authoring_diagnostics_routes_reset_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_303_durable_authoring_post_delete_no_write_boundary_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_304_durable_authoring_post_delete_reset_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_305_312_durable_executor_authoring_post_delete_recreation_actual_execution_batch_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_305_durable_authoring_recreation_checkpoint_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_306_durable_authoring_recreation_target_absence_preflight_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_307_durable_authoring_recreate_actor_bp_execution_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_308_durable_authoring_recreated_actor_bp_compile_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_309_durable_authoring_recreated_actor_bp_save_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_310_durable_authoring_recreated_actor_bp_readback_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_311_durable_authoring_recreation_dirty_baseline_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "section_312_durable_authoring_recreation_actual_release_status": (
                "passed" if not failed_blocking else "failed"
            ),
            "durable_executor_opened": not failed_blocking,
            "durable_authoring_command_no_save_execution_ready": not failed_blocking,
            "final_no_save_release_ready": not failed_blocking,
            "durable_authoring_save_gate_preflight_ready": not failed_blocking,
            "save_command_admission_preflight_ready": not failed_blocking,
            "save_gate_open_allowed": not failed_blocking,
            "save_gate_opened": not failed_blocking,
            "save_command_admitted": not failed_blocking,
            "save_command_dry_run_ready": not failed_blocking,
            "final_pre_save_execution_ready": not failed_blocking,
            "live_pre_save_checkpoint_ready": not failed_blocking,
            "actual_save_execution_requires_final_user_checkpoint": False,
            "actual_save_final_checkpoint_satisfied": not failed_blocking,
            "live_actual_save_execution_ready": not failed_blocking,
            "live_save_stability_ready": not failed_blocking,
            "cleanup_delete_dry_run_allowed": not failed_blocking,
            "cleanup_delete_dry_run_ready": not failed_blocking,
            "actual_delete_execution_requires_final_user_checkpoint": (
                not failed_blocking
            ),
            "rename_overwrite_dry_run_allowed": not failed_blocking,
            "rename_overwrite_dry_run_ready": not failed_blocking,
            "actual_rename_overwrite_requires_final_user_checkpoint": (
                not failed_blocking
            ),
            "actor_bp_expansion_dry_run_allowed": not failed_blocking,
            "actor_bp_expansion_dry_run_ready": not failed_blocking,
            "actual_actor_bp_authoring_requires_final_user_checkpoint": (
                not failed_blocking
            ),
            "live_actor_bp_authoring_preflight_allowed": not failed_blocking,
            "live_actor_bp_authoring_checkpoint_ready": not failed_blocking,
            "actual_live_actor_bp_authoring_requires_final_user_checkpoint": (
                False
            ),
            "actual_live_actor_bp_authoring_final_checkpoint_satisfied": (
                not failed_blocking
            ),
            "live_actor_bp_actual_authoring_executed": not failed_blocking,
            "live_actor_bp_actual_authoring_saved": not failed_blocking,
            "live_actor_bp_actual_authoring_readback_verified": (
                not failed_blocking
            ),
            "actor_bp_authoring_external_dirty_preserved": (
                not failed_blocking
            ),
            "live_actor_bp_component_default_type_readback_ready": (
                not failed_blocking
            ),
            "broader_blueprint_class_authoring_guard_ready": (
                not failed_blocking
            ),
            "live_actor_bp_component_default_readback_no_write_verified": (
                not failed_blocking
            ),
            "unsupported_blueprint_class_authoring_blocked": (
                not failed_blocking
            ),
            "function_call_diagnostics_ready": not failed_blocking,
            "pin_contract_diagnostics_ready": not failed_blocking,
            "graph_layout_diagnostics_ready": not failed_blocking,
            "graph_layout_repair_suggestions_ready": not failed_blocking,
            "function_diagnostics_graph_layout_no_write_verified": (
                not failed_blocking
            ),
            "auto_graph_repair_execution_blocked": not failed_blocking,
            "cleanup_delete_actual_execution_ready": not failed_blocking,
            "cleanup_delete_actual_target_deleted": not failed_blocking,
            "cleanup_delete_actual_external_dirty_preserved": (
                not failed_blocking
            ),
            "post_delete_recreation_reset_ready": not failed_blocking,
            "post_delete_target_absence_confirmed": not failed_blocking,
            "post_delete_recreation_requires_final_user_checkpoint": (
                not failed_blocking
            ),
            "post_delete_readback_routes_reset": not failed_blocking,
            "post_delete_diagnostics_routes_reset": not failed_blocking,
            "post_delete_recreate_asset_allowed": not failed_blocking,
            "post_delete_recreate_command_dispatched": not failed_blocking,
            "post_delete_recreate_command_executed": not failed_blocking,
            "post_delete_recreation_actual_execution_ready": (
                not failed_blocking
            ),
            "post_delete_recreated_actor_bp_saved": not failed_blocking,
            "post_delete_recreated_actor_bp_readback_verified": (
                not failed_blocking
            ),
            "post_delete_recreation_variable_authoring_open": False,
            "post_delete_recreation_component_authoring_open": False,
            "post_delete_recreation_default_authoring_open": False,
            "graph_repair_command_dispatched": False,
            "graph_repair_command_executed": False,
            "graph_layout_mutation_performed": False,
            "node_position_write_performed": False,
            "pin_connection_write_performed": False,
            "fixed_compile_api": (
                durable_executor_authoring_live_save_stability_batch
                .FIXED_COMPILE_API_NAME
            ),
            "saved_temp_blueprint_asset_path": (
                durable_executor_authoring_live_actual_save_execution_batch
                .DEFAULT_TARGET_ASSET_PATH
            ),
            "save_command_dispatched": not failed_blocking,
            "save_command_executed": not failed_blocking,
            "save_asset_allowed": not failed_blocking,
            "save_true_allowed": not failed_blocking,
            "compile_save_allowed": not failed_blocking,
            "asset_write_performed": not failed_blocking,
            "package_dirty_marked": not failed_blocking,
            "live_durable_authoring_allowed": not failed_blocking,
            "live_command_dispatched": not failed_blocking,
            "live_command_executed": not failed_blocking,
            "cleanup_allowed": False,
            "cleanup_executed": False,
            "save_delete_rename_allowed": False,
            "delete_asset_allowed": not failed_blocking,
            "delete_asset_executed": not failed_blocking,
            "rename_asset_allowed": False,
            "rename_command_dispatched": False,
            "rename_command_executed": False,
            "overwrite_allowed": False,
            "overwrite_executed": False,
            "variable_add_command_dispatched": not failed_blocking,
            "variable_add_command_executed": not failed_blocking,
            "component_add_command_dispatched": not failed_blocking,
            "component_add_command_executed": not failed_blocking,
            "default_write_command_dispatched": not failed_blocking,
            "default_write_command_executed": not failed_blocking,
            "actor_bp_authoring_command_dispatched": not failed_blocking,
            "actor_bp_authoring_command_executed": not failed_blocking,
            "actor_bp_authoring_compile_dispatched": not failed_blocking,
            "actor_bp_authoring_compile_executed": not failed_blocking,
            "actor_bp_authoring_save_dispatched": not failed_blocking,
            "actor_bp_authoring_save_executed": not failed_blocking,
            "actor_bp_authoring_asset_write_performed": not failed_blocking,
            "actor_bp_authoring_package_dirty_marked": not failed_blocking,
            "actor_bp_authoring_target_dirty_after": False,
            "production_path_write_allowed": False,
            "production_path_write_executed": False,
            "durable_safety_boundary_unlock_ready": not failed_blocking,
            "durable_safety_boundary_unlocked": not failed_blocking,
            "final_durable_release_ready": not failed_blocking,
            "main_push_requested": False,
            "current_authoring_ceiling": (
                "planner_safe_temporary_manifest_execution_with_structural_validation_durable_read_only_preflight_section_51_enable_contract_section_52_ownership_marker_section_53_dry_run_plan_section_54_save_simulator_section_55_canary_prep_section_56_canary_approval_gate_section_57_canary_live_preflight_section_58_canary_recovery_matrix_section_59_release_boundary_v2_section_60_mvp_decision_section_61_bridge_refresh_contract_section_62_live_evidence_refresh_contract_section_63_executor_review_contract_section_64_canary_command_allowlist_contract_section_65_canary_creation_boundary_contract_section_66_ownership_marker_proof_contract_section_67_rollback_cleanup_proof_contract_section_68_save_gate_final_review_contract_section_69_canary_rehearsal_readiness_contract_section_70_durable_release_decision_contract_section_71_bridge_recovery_readiness_contract_section_72_canary_read_only_retry_envelope_contract_section_73_canary_read_only_retry_result_admission_contract_section_74_canary_rehearsal_promotion_barrier_contract_section_75_canary_rehearsal_execution_release_contract_section_76_canary_live_runner_envelope_contract_section_77_canary_live_runner_start_contract_section_78_canary_live_command_dispatch_release_contract_section_79_canary_live_command_execution_release_contract_section_80_canary_live_command_execution_evidence_admission_contract_section_81_canary_release_promotion_decision_contract_section_82_canary_executor_activation_contract_section_83_canary_executor_open_contract_section_84_canary_authoring_enable_contract_section_85_canary_authoring_command_contract_section_86_canary_authoring_command_dispatch_contract_section_87_canary_authoring_command_execution_contract_section_88_canary_authoring_command_execution_evidence_contract_section_89_canary_authoring_command_completion_decision_contract_section_90_canary_authoring_command_completion_application_contract_section_91_canary_authoring_command_completion_result_contract_section_92_canary_authoring_command_result_readback_contract_section_93_canary_authoring_final_no_save_release_contract_section_94_canary_authoring_final_release_readiness_contract_section_95_durable_executor_implementation_review_contract_section_96_durable_executor_implementation_plan_contract_section_97_durable_executor_change_design_contract_section_98_durable_executor_code_change_approval_contract_section_99_durable_executor_code_patch_plan_contract_section_100_durable_executor_code_patch_review_contract_section_101_durable_executor_code_patch_application_contract_section_102_durable_executor_code_patch_execution_contract_section_103_durable_executor_code_patch_result_contract_section_104_durable_executor_code_patch_result_readback_contract_section_105_durable_executor_code_patch_final_no_save_release_contract_section_106_durable_executor_code_patch_final_release_readiness_contract_section_107_durable_executor_code_patch_release_review_contract_section_108_durable_executor_code_patch_release_decision_contract_section_109_durable_executor_release_promotion_barrier_contract_section_110_durable_executor_activation_readiness_contract_section_111_durable_executor_open_contract_section_112_durable_executor_authoring_enable_contract_section_113_durable_executor_authoring_command_contract_section_114_durable_executor_authoring_command_dispatch_contract_section_115_durable_executor_authoring_command_execution_contract_section_116_durable_executor_authoring_command_execution_evidence_contract_section_117_durable_executor_authoring_command_completion_decision_contract_section_118_durable_executor_authoring_command_completion_application_contract_section_119_durable_executor_authoring_command_completion_result_contract_section_120_durable_executor_authoring_command_result_readback_contract_section_121_durable_executor_authoring_final_no_save_release_contract_section_122_durable_executor_authoring_final_release_readiness_contract_section_123_durable_executor_authoring_release_review_contract_section_124_durable_executor_authoring_release_decision_contract_section_125_durable_executor_authoring_release_promotion_barrier_contract_section_126_durable_executor_authoring_activation_readiness_contract_section_127_durable_executor_authoring_open_contract_section_128_durable_executor_authoring_enable_after_open_contract_and_section_129_durable_executor_authoring_command_after_enable_contract"
                "_and_section_130_durable_executor_authoring_command_dispatch_after_command_contract"
                "_and_section_131_durable_executor_authoring_command_execution_after_dispatch_contract"
                "_and_section_132_durable_executor_authoring_command_execution_evidence_after_execution_contract"
                "_and_section_133_durable_executor_authoring_command_completion_decision_after_evidence_contract"
                "_and_section_134_durable_executor_authoring_command_completion_application_after_decision_contract"
                "_and_section_135_durable_executor_authoring_command_completion_result_after_application_contract"
                "_and_section_136_durable_executor_authoring_command_result_readback_after_result_contract"
                "_and_section_137_durable_executor_authoring_final_no_save_release_after_readback_contract"
                "_and_section_138_durable_executor_authoring_final_release_readiness_after_no_save_release_contract"
                "_and_section_139_durable_executor_authoring_release_review_after_readiness_contract"
                "_and_section_140_durable_executor_authoring_release_decision_after_review_contract"
                "_and_section_141_durable_executor_authoring_release_promotion_barrier_after_decision_contract"
                "_and_section_142_durable_executor_authoring_activation_readiness_after_promotion_barrier_contract"
                "_and_section_143_durable_executor_authoring_open_after_activation_readiness_contract"
                "_and_section_144_durable_executor_authoring_enable_after_open_after_activation_readiness_contract"
                "_and_section_145_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_146_durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_147_durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_148_durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_149_durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_150_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_151_durable_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_152_durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_153_durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_154_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_155_durable_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_156_durable_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_157_durable_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_158_durable_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_159_durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_160_durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_161_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
                "_and_section_162_durable_executor_authoring_command_request_dry_run_route_contract"
                "_and_section_163_durable_executor_authoring_command_dispatch_dry_run_contract"
                "_and_section_164_durable_executor_authoring_command_dispatch_evidence_dry_run_contract"
                "_and_section_165_durable_executor_authoring_command_execution_dry_run_contract"
                "_and_section_166_durable_executor_authoring_command_execution_evidence_dry_run_contract"
                "_and_section_167_durable_executor_authoring_command_completion_decision_dry_run_contract"
                "_and_section_168_durable_executor_authoring_command_completion_application_dry_run_contract"
                "_and_section_169_durable_executor_authoring_command_completion_result_dry_run_contract"
                "_and_section_170_durable_executor_authoring_command_result_readback_dry_run_contract"
                "_and_section_171_durable_executor_authoring_final_no_save_release_dry_run_contract"
                "_and_section_172_durable_executor_authoring_final_release_readiness_dry_run_contract"
                "_and_section_173_durable_executor_authoring_release_review_dry_run_contract"
                "_and_section_174_durable_executor_authoring_release_decision_dry_run_contract"
                "_and_section_175_durable_executor_authoring_release_promotion_barrier_dry_run_contract"
                "_and_section_176_durable_executor_authoring_activation_readiness_dry_run_contract"
                "_and_section_177_durable_executor_authoring_open_dry_run_contract"
                "_and_section_178_durable_executor_authoring_open_promotion_barrier_dry_run_contract"
                "_and_section_179_durable_executor_authoring_command_path_dry_run_contract"
                "_and_section_180_durable_executor_authoring_command_admission_dry_run_contract"
                "_and_section_181_durable_executor_authoring_release_boundary_consolidation"
                "_and_section_182_durable_executor_authoring_safety_boundary_unlock_decision_checkpoint"
                "_and_section_183_durable_executor_authoring_safety_boundary_unlock_record_read_only_preflight"
                "_and_section_184_durable_executor_authoring_safety_boundary_unlocked_no_write"
                "_and_section_185_durable_executor_authoring_enabled_no_executor_open_no_write"
                "_and_section_186_192_durable_executor_authoring_no_save_execution_ready_save_gate_closed"
                "_and_section_193_200_durable_executor_authoring_save_gate_preflight_ready_actual_save_closed"
                "_and_section_201_208_durable_executor_authoring_save_gate_open_command_admitted_actual_save_closed"
                "_and_section_209_216_durable_executor_authoring_live_pre_save_checkpoint_ready_actual_save_closed"
                "_and_section_217_224_durable_executor_authoring_live_actual_save_execution_readback_ready"
                "_and_section_225_232_durable_executor_authoring_live_save_stability_ready_cleanup_delete_rename_closed"
                "_and_section_233_240_durable_executor_authoring_cleanup_delete_dry_run_ready_actual_delete_closed"
                "_and_section_241_248_durable_executor_authoring_rename_overwrite_dry_run_ready_actual_rename_closed"
                "_and_section_249_256_durable_executor_authoring_actor_bp_expansion_dry_run_ready_actual_actor_authoring_closed"
                "_and_section_257_264_durable_executor_authoring_live_actor_bp_authoring_checkpoint_ready_actual_authoring_closed"
                "_and_section_265_272_durable_executor_authoring_live_actor_bp_actual_authoring_readback_ready"
                "_and_section_273_280_durable_executor_authoring_live_actor_bp_component_default_readback_ready"
                "_and_section_281_288_durable_executor_authoring_function_diagnostics_graph_layout_repair_suggestions_ready"
                "_and_section_289_296_durable_executor_authoring_cleanup_delete_actual_execution_readback_ready"
                "_and_section_297_304_durable_executor_authoring_post_delete_recreation_readback_reset_ready"
                "_and_section_305_312_durable_executor_authoring_post_delete_recreation_actual_execution_ready"
            ),
            "cxx_changes_required": False,
        },
        "next_reinforcement_candidates": [
            "post-recreation Actor Blueprint variable/component/default reauthoring checkpoint",
            "broader non-Actor Blueprint authoring dry-run contracts",
            "graph repair execution dry-run with compile/save still closed",
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
