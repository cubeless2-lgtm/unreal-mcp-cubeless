#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_authoring_final_readiness_after_activation_readiness_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_final_no_save_after_activation_readiness_contract as final_release  # noqa: E402
import bp_authoring_durable_executor_authoring_final_readiness_after_activation_readiness_contract as readiness  # noqa: E402


def build_current_final_no_save_release_after_readback_summary() -> dict:
    return {
        "schema": final_release.DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_AFTER_READBACK_AFTER_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SUMMARY_SCHEMA,
        "status": "passed",
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


def build_readiness_record(**overrides: object) -> dict:
    record = {
        "schema": readiness.DURABLE_EXECUTOR_AUTHORING_FINAL_RELEASE_READINESS_AFTER_NO_SAVE_RELEASE_AFTER_READBACK_AFTER_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_RECORD_SCHEMA,
        "readiness_scope": readiness.EXPECTED_FINAL_RELEASE_READINESS_SCOPE,
        "explicit_durable_authoring_final_release_readiness_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
        "durable_authoring_final_release_readiness_started": False,
        "durable_authoring_final_release_ready": False,
        "durable_authoring_release_review_started": False,
        "durable_authoring_final_no_save_release_accepted": False,
        "durable_authoring_command_result_readback_accepted": False,
        "durable_authoring_command_completion_result_accepted": False,
        "durable_authoring_command_completed": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "code_change_performed": False,
        "executor_code_modified": False,
        "unreal_asset_modified": False,
        "live_bridge_probe_started": False,
        "save_asset_executed": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
        "live_command_dispatch_performed": False,
        "live_command_dispatched": False,
        "live_command_execution_performed": False,
        "live_command_executed": False,
        "reported_final_release_readiness_gate_count": 1,
        "reported_final_no_save_release_revalidated_count": 1,
        "reported_durable_authoring_still_disabled_count": 1,
        "reported_no_completion_readiness_count": 1,
        "reported_no_write_readiness_count": 1,
        "reported_no_save_readiness_count": 1,
        "reported_no_code_change_readiness_count": 1,
        "reported_no_live_command_readiness_count": 1,
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
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_final_no_save_release_after_readback_summary()
    contract = readiness.build_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        True,
        current_summary,
    )
    assert (
        contract["schema"]
        == readiness.DURABLE_EXECUTOR_AUTHORING_FINAL_RELEASE_READINESS_AFTER_NO_SAVE_RELEASE_AFTER_READBACK_AFTER_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["final_release_readiness_contract_defined"] is True
    assert contract["final_no_save_release_contract_ready"] is True
    assert contract["final_no_save_release_inputs_satisfied"] is False
    assert contract["final_no_save_release_record_valid"] is False
    assert contract["allowed_final_no_save_release_observed"] is False
    assert contract["no_forbidden_final_no_save_releases"] is False
    assert contract["final_release_readiness_inputs_satisfied"] is False
    assert contract["final_release_readiness_record_present"] is False
    assert contract["final_release_readiness_record_valid"] is False
    assert contract["final_release_readiness_record_rejected"] is False
    assert contract["unsafe_final_release_readiness_record_count"] == 0
    assert contract["missing_final_release_readiness_prerequisite_count"] == 14
    assert "section_153_final_no_save_release_inputs_satisfied" in contract[
        "missing_final_release_readiness_prerequisites"
    ]
    assert "section_153_final_no_save_release_record_valid" in contract[
        "missing_final_release_readiness_prerequisites"
    ]
    assert "section_153_allowed_final_no_save_release_observed" in contract[
        "missing_final_release_readiness_prerequisites"
    ]
    assert "section_153_no_forbidden_final_no_save_releases" in contract[
        "missing_final_release_readiness_prerequisites"
    ]
    assert "durable_authoring_final_release_readiness_record_present" in contract[
        "missing_final_release_readiness_prerequisites"
    ]
    assert "explicit_durable_mvp_request_reconfirmed" in contract[
        "missing_final_release_readiness_prerequisites"
    ]
    assert "separate_durable_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract" in contract[
        "missing_final_release_readiness_prerequisites"
    ]
    assert contract["durable_authoring_final_release_readiness_started"] is False
    assert contract["durable_authoring_final_release_ready"] is False
    assert contract["durable_authoring_release_review_started"] is False
    assert contract["durable_authoring_final_no_save_release_accepted"] is False
    assert contract["durable_authoring_command_result_readback_accepted"] is False
    assert contract["durable_authoring_command_completed"] is False
    assert contract["asset_write_performed"] is False
    assert contract["code_change_performed"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = readiness.summarize_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count"
        ]
        == 1
    )
    assert summary["final_release_readiness_contract_defined_count"] == 1
    assert summary["final_no_save_release_contract_ready_count"] == 1
    assert summary["final_release_readiness_record_valid_count"] == 0
    assert summary["final_release_readiness_record_rejected_count"] == 0
    assert summary["unsafe_final_release_readiness_record_count"] == 0
    assert summary["missing_final_release_readiness_prerequisite_count"] == 14
    assert summary["durable_authoring_final_release_readiness_started_count"] == 0
    assert summary["durable_authoring_final_release_ready_count"] == 0
    assert summary["durable_authoring_release_review_started_count"] == 0
    assert summary["durable_authoring_final_no_save_release_accepted_count"] == 0
    assert summary["durable_authoring_command_result_readback_accepted_count"] == 0
    assert summary["durable_authoring_command_completed_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["code_change_performed_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    future_summary = {
        **current_summary,
        "final_no_save_release_inputs_satisfied_count": 1,
        "final_no_save_release_record_valid_count": 1,
        "allowed_final_no_save_release_observed_count": 1,
        "no_forbidden_final_no_save_releases_count": 1,
    }
    future_contract = readiness.build_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        True,
        future_summary,
        build_readiness_record(),
    )
    assert future_contract["final_release_readiness_record_valid"] is True
    assert future_contract["missing_final_release_readiness_prerequisite_count"] == 1
    assert future_contract["missing_final_release_readiness_prerequisites"] == [
        "separate_durable_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
    ]
    assert future_contract["reported_allowed_final_release_readiness_count"] == 8
    assert future_contract["reported_forbidden_final_release_readiness_count"] == 0
    assert future_contract["durable_authoring_final_release_readiness_started"] is False
    assert future_contract["durable_authoring_final_release_ready"] is False
    assert future_contract["durable_authoring_release_review_started"] is False
    assert future_contract["durable_authoring_final_no_save_release_accepted"] is False
    assert future_contract["asset_write_performed"] is False
    assert future_contract["code_change_performed"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    unsafe_contract = readiness.build_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        True,
        future_summary,
        build_readiness_record(reported_save_count=1),
    )
    assert unsafe_contract["final_release_readiness_record_valid"] is False
    assert unsafe_contract["final_release_readiness_record_rejected"] is True
    assert unsafe_contract["unsafe_final_release_readiness_record_count"] == 1
    assert unsafe_contract["reported_forbidden_final_release_readiness_count"] == 1
    unsafe_summary = readiness.summarize_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [unsafe_contract]
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["final_release_readiness_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_final_release_readiness_record_count"] == 1
    assert unsafe_summary["durable_authoring_final_release_ready_count"] == 0
    assert unsafe_summary["save_delete_rename_allowed_count"] == 0

    code_change_contract = readiness.build_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        True,
        future_summary,
        build_readiness_record(code_change_performed=True),
    )
    assert code_change_contract["final_release_readiness_record_valid"] is False
    assert code_change_contract["final_release_readiness_record_rejected"] is True
    assert code_change_contract["unsafe_final_release_readiness_record_count"] == 1
    code_change_summary = readiness.summarize_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [code_change_contract]
    )
    assert code_change_summary["status"] == "failed"
    assert code_change_summary["code_change_performed_count"] == 0

    print(
        "BP authoring durable executor authoring final release readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
