#!/usr/bin/env python
"""Offline smoke tests for Section 168 command completion application dry-run contract."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_command_completion_application_dry_run_contract as application  # noqa: E402
import bp_authoring_durable_executor_authoring_command_completion_decision_dry_run_contract as decision  # noqa: E402


def build_section_167_summary(**overrides: object) -> dict:
    summary = {
        "schema": decision.DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_DECISION_DRY_RUN_SUMMARY_SCHEMA,
        "status": "passed",
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
        "completion_decision_dry_run_record_valid_count": 0,
        "completion_decision_dry_run_record_rejected_count": 0,
        "completion_decision_dry_run_admissible_count": 0,
        "unsafe_completion_decision_record_count": 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
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
    summary.update(overrides)
    return summary


def build_completion_application_record(**overrides: object) -> dict:
    record = {
        "schema": application.DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_DRY_RUN_RECORD_SCHEMA,
        "completion_application_scope": application.EXPECTED_COMPLETION_APPLICATION_SCOPE,
        "status": "passed",
        "dry_run_only": True,
        "requested_command": "create_blueprint_asset",
        "completion_application_operation": "completion_application_dry_run_only",
        "target_asset": "/Game/MCPTestFixtures/BP_PlannerDurable",
        "operator_reconfirmed_no_live_dispatch": True,
        "operator_reconfirmed_no_live_execution": True,
        "operator_reconfirmed_no_write_execution": True,
        "operator_reconfirmed_no_save_delete_rename": True,
        "completion_decision_admission_proof": {
            "open_activation_promotion_readiness_chain_satisfied": True,
            "authoring_enable_chain_satisfied": True,
            "durable_release_readiness_chain_reconfirmed": True,
            "authoring_command_inputs_satisfied": True,
            "authoring_command_record_valid": True,
            "dry_run_route_record_valid": True,
            "dry_run_route_admissible": True,
            "dispatch_dry_run_record_valid": True,
            "dispatch_dry_run_admissible": True,
            "dispatch_evidence_dry_run_record_valid": True,
            "dispatch_evidence_dry_run_admissible": True,
            "execution_dry_run_record_valid": True,
            "execution_dry_run_admissible": True,
            "execution_evidence_dry_run_record_valid": True,
            "execution_evidence_dry_run_admissible": True,
            "completion_decision_dry_run_record_valid": True,
            "completion_decision_dry_run_admissible": True,
        },
        "release_boundary_proof": {
            "durable_authoring_enabled": False,
            "final_durable_release_ready": False,
            "save_delete_rename_allowed": False,
            "live_durable_authoring_allowed": False,
        },
        "durable_completion_application_promoted": False,
        "durable_completion_application_applied": False,
        "durable_completion_decision_promoted": False,
        "durable_execution_evidence_promoted": False,
        "durable_execution_envelope_promoted": False,
        "durable_evidence_promoted": False,
        "durable_dispatch_envelope_promoted": False,
        "durable_command_request_promoted": False,
        "durable_executor_command_path_opened": False,
        "durable_executor_command_path_allowed": False,
        "durable_authoring_command_allowed": False,
        "durable_authoring_command_dispatched": False,
        "durable_authoring_command_executed": False,
        "durable_authoring_command_completed": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "final_durable_release_ready": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "code_change_performed": False,
        "executor_code_modified": False,
        "unreal_asset_modified": False,
        "live_bridge_probe_started": False,
        "save_delete_rename_allowed": False,
        "save_asset_allowed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatched": False,
        "live_command_executed": False,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_section_167_summary()
    contract = application.build_durable_executor_authoring_command_completion_application_dry_run_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == application.DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_DRY_RUN_SCHEMA
    assert contract["requested"] is True
    assert contract["completion_application_contract_defined"] is True
    assert contract["section_167_completion_decision_contract_ready"] is True
    assert contract["completion_decision_chain_satisfied"] is False
    assert contract["completion_application_dry_run_record_present"] is False
    assert contract["completion_application_dry_run_record_valid"] is False
    assert contract["completion_application_dry_run_record_rejected"] is False
    assert contract["completion_application_dry_run_admissible"] is False
    assert contract["missing_completion_application_dry_run_prerequisite_count"] == 31
    assert "section_167_completion_decision_dry_run_admissible" in contract[
        "missing_completion_application_dry_run_prerequisites"
    ]
    assert "command_completion_application_dry_run_record_present" in contract[
        "missing_completion_application_dry_run_prerequisites"
    ]
    assert contract["durable_completion_application_promoted"] is False
    assert contract["durable_completion_application_applied"] is False
    assert contract["durable_completion_decision_promoted"] is False
    assert contract["durable_executor_command_path_opened"] is False
    assert contract["durable_authoring_command_dispatched"] is False
    assert contract["durable_authoring_command_executed"] is False
    assert contract["durable_authoring_command_completed"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["final_durable_release_ready"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = application.summarize_durable_executor_authoring_command_completion_application_dry_runs(
        [contract]
    )
    assert summary["status"] == "passed"
    assert summary["durable_requested_executor_authoring_command_completion_application_dry_run_count"] == 1
    assert summary["completion_application_contract_defined_count"] == 1
    assert summary["section_167_completion_decision_contract_ready_count"] == 1
    assert summary["completion_decision_chain_satisfied_count"] == 0
    assert summary["completion_application_dry_run_record_present_count"] == 0
    assert summary["completion_application_dry_run_record_valid_count"] == 0
    assert summary["completion_application_dry_run_record_rejected_count"] == 0
    assert summary["completion_application_dry_run_admissible_count"] == 0
    assert summary["durable_completion_application_promoted_count"] == 0
    assert summary["durable_completion_application_applied_count"] == 0
    assert summary["durable_completion_decision_promoted_count"] == 0
    assert summary["durable_executor_command_path_opened_count"] == 0
    assert summary["durable_authoring_command_dispatched_count"] == 0
    assert summary["durable_authoring_command_executed_count"] == 0
    assert summary["durable_authoring_command_completed_count"] == 0
    assert summary["durable_authoring_enabled_count"] == 0
    assert summary["final_durable_release_ready_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    blocked_with_record = application.build_durable_executor_authoring_command_completion_application_dry_run_contract(
        True,
        current_summary,
        build_completion_application_record(),
    )
    assert blocked_with_record["completion_decision_chain_satisfied"] is False
    assert blocked_with_record["completion_application_dry_run_record_valid"] is False
    assert blocked_with_record["completion_application_dry_run_record_rejected"] is True
    assert blocked_with_record["completion_application_dry_run_admissible"] is False
    assert blocked_with_record["missing_completion_application_dry_run_prerequisite_count"] == 17
    assert blocked_with_record["durable_completion_application_promoted"] is False
    assert blocked_with_record["durable_completion_application_applied"] is False
    assert blocked_with_record["durable_executor_command_path_opened"] is False
    assert blocked_with_record["durable_authoring_command_dispatched"] is False
    assert blocked_with_record["durable_authoring_command_executed"] is False
    assert blocked_with_record["durable_authoring_command_completed"] is False
    assert blocked_with_record["save_delete_rename_allowed"] is False

    future_summary = build_section_167_summary(
        open_activation_promotion_readiness_chain_satisfied_count=1,
        authoring_enable_chain_satisfied_count=1,
        durable_release_readiness_chain_reconfirmed_count=1,
        authoring_command_inputs_satisfied_count=1,
        authoring_command_record_valid_count=1,
        dry_run_route_record_valid_count=1,
        dry_run_route_admissible_count=1,
        dispatch_dry_run_record_valid_count=1,
        dispatch_dry_run_admissible_count=1,
        dispatch_evidence_dry_run_record_valid_count=1,
        dispatch_evidence_dry_run_admissible_count=1,
        execution_dry_run_record_valid_count=1,
        execution_dry_run_admissible_count=1,
        execution_evidence_dry_run_record_valid_count=1,
        execution_evidence_dry_run_admissible_count=1,
        completion_decision_dry_run_record_valid_count=1,
        completion_decision_dry_run_admissible_count=1,
    )
    future_contract = application.build_durable_executor_authoring_command_completion_application_dry_run_contract(
        True,
        future_summary,
        build_completion_application_record(),
    )
    assert future_contract["completion_decision_chain_satisfied"] is True
    assert future_contract["completion_application_dry_run_record_valid"] is True
    assert future_contract["completion_application_dry_run_record_rejected"] is False
    assert future_contract["completion_application_dry_run_admissible"] is True
    assert future_contract["missing_completion_application_dry_run_prerequisite_count"] == 0
    assert future_contract["durable_completion_application_promoted"] is False
    assert future_contract["durable_completion_application_applied"] is False
    assert future_contract["durable_completion_decision_promoted"] is False
    assert future_contract["durable_execution_evidence_promoted"] is False
    assert future_contract["durable_executor_command_path_opened"] is False
    assert future_contract["durable_executor_command_path_allowed"] is False
    assert future_contract["durable_authoring_command_allowed"] is False
    assert future_contract["durable_authoring_command_dispatched"] is False
    assert future_contract["durable_authoring_command_executed"] is False
    assert future_contract["durable_authoring_command_completed"] is False
    assert future_contract["durable_authoring_enabled"] is False
    assert future_contract["final_durable_release_ready"] is False
    assert future_contract["asset_write_performed"] is False
    assert future_contract["package_dirty_marked"] is False
    assert future_contract["save_delete_rename_allowed"] is False
    future_summary_result = application.summarize_durable_executor_authoring_command_completion_application_dry_runs(
        [future_contract]
    )
    assert future_summary_result["status"] == "passed"
    assert future_summary_result["completion_application_dry_run_admissible_count"] == 1
    assert future_summary_result["durable_completion_application_promoted_count"] == 0
    assert future_summary_result["durable_completion_application_applied_count"] == 0
    assert future_summary_result["durable_completion_decision_promoted_count"] == 0
    assert future_summary_result["durable_executor_command_path_opened_count"] == 0
    assert future_summary_result["durable_authoring_command_dispatched_count"] == 0
    assert future_summary_result["durable_authoring_command_executed_count"] == 0
    assert future_summary_result["durable_authoring_command_completed_count"] == 0
    assert future_summary_result["save_delete_rename_allowed_count"] == 0

    forbidden_contract = application.build_durable_executor_authoring_command_completion_application_dry_run_contract(
        True,
        future_summary,
        build_completion_application_record(requested_command="save_asset"),
    )
    assert forbidden_contract["requested_command_forbidden"] is True
    assert forbidden_contract["completion_application_dry_run_record_rejected"] is True
    assert forbidden_contract["completion_application_dry_run_admissible"] is False
    forbidden_summary = application.summarize_durable_executor_authoring_command_completion_application_dry_runs(
        [forbidden_contract]
    )
    assert forbidden_summary["status"] == "failed"
    assert forbidden_summary["requested_command_forbidden_count"] == 1
    assert forbidden_summary["durable_authoring_command_dispatched_count"] == 0
    assert forbidden_summary["durable_authoring_command_executed_count"] == 0
    assert forbidden_summary["durable_authoring_command_completed_count"] == 0
    assert forbidden_summary["save_delete_rename_allowed_count"] == 0

    unsafe_contract = application.build_durable_executor_authoring_command_completion_application_dry_run_contract(
        True,
        future_summary,
        build_completion_application_record(durable_completion_application_applied=True),
    )
    assert unsafe_contract["unsafe_completion_application_record_count"] == 1
    assert unsafe_contract["completion_application_dry_run_record_rejected"] is True
    assert unsafe_contract["completion_application_dry_run_admissible"] is False
    assert unsafe_contract["durable_completion_application_applied"] is False
    assert unsafe_contract["durable_authoring_command_completed"] is False
    assert unsafe_contract["save_delete_rename_allowed"] is False

    print("BP authoring durable executor authoring command completion application dry-run contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
