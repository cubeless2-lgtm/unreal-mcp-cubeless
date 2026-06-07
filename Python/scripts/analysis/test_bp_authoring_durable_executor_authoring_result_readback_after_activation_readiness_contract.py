#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_authoring_result_readback_after_activation_readiness_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_completion_result_after_activation_readiness_contract as result  # noqa: E402
import bp_authoring_durable_executor_authoring_result_readback_after_activation_readiness_contract as readback  # noqa: E402


def build_current_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary() -> dict:
    return {
        "schema": result.DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SUMMARY_SCHEMA,
        "status": "passed",
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


def build_readback_record(**overrides: object) -> dict:
    record = {
        "schema": readback.DURABLE_EXECUTOR_AUTHORING_COMMAND_RESULT_READBACK_AFTER_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_RECORD_SCHEMA,
        "readback_scope": readback.EXPECTED_READBACK_SCOPE,
        "explicit_durable_authoring_command_result_readback_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
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
        "reported_no_completion_readback_count": 1,
        "reported_no_write_readback_count": 1,
        "reported_no_save_readback_count": 1,
        "reported_completed_readback_count": 0,
        "reported_asset_write_readback_count": 0,
        "reported_package_dirty_readback_count": 0,
        "reported_save_readback_count": 0,
        "reported_delete_rename_readback_count": 0,
        "reported_cleanup_readback_count": 0,
        "reported_code_change_readback_count": 0,
        "reported_live_command_readback_count": 0,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary()
    contract = readback.build_durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == readback.DURABLE_EXECUTOR_AUTHORING_COMMAND_RESULT_READBACK_AFTER_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SCHEMA
    assert contract["requested"] is True
    assert contract["readback_contract_defined"] is True
    assert contract["result_contract_ready"] is True
    assert contract["result_inputs_satisfied"] is False
    assert contract["result_record_valid"] is False
    assert contract["allowed_result_observed"] is False
    assert contract["no_forbidden_results"] is False
    assert contract["readback_inputs_satisfied"] is False
    assert contract["readback_record_present"] is False
    assert contract["readback_record_valid"] is False
    assert contract["readback_record_rejected"] is False
    assert contract["unsafe_readback_record_count"] == 0
    assert contract["missing_readback_prerequisite_count"] == 14
    assert "section_151_result_inputs_satisfied" in contract[
        "missing_readback_prerequisites"
    ]
    assert "section_151_result_record_valid" in contract[
        "missing_readback_prerequisites"
    ]
    assert "section_151_allowed_result_observed" in contract[
        "missing_readback_prerequisites"
    ]
    assert "section_151_no_forbidden_results" in contract[
        "missing_readback_prerequisites"
    ]
    assert "separate_durable_authoring_final_no_save_release_after_readback_contract" in contract[
        "missing_readback_prerequisites"
    ]
    assert contract["durable_authoring_command_result_readback_accepted"] is False
    assert contract["durable_authoring_command_completed"] is False
    assert contract["asset_write_performed"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = readback.summarize_durable_executor_authoring_command_result_readbacks_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    assert summary["status"] == "passed"
    assert summary["durable_requested_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count"] == 1
    assert summary["readback_contract_defined_count"] == 1
    assert summary["result_contract_ready_count"] == 1
    assert summary["readback_record_valid_count"] == 0
    assert summary["readback_record_rejected_count"] == 0
    assert summary["unsafe_readback_record_count"] == 0
    assert summary["missing_readback_prerequisite_count"] == 14
    assert summary["durable_authoring_command_result_readback_accepted_count"] == 0
    assert summary["durable_authoring_command_completed_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    future_summary = {
        **current_summary,
        "result_inputs_satisfied_count": 1,
        "result_record_valid_count": 1,
        "allowed_result_observed_count": 1,
        "no_forbidden_results_count": 1,
    }
    future_contract = readback.build_durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        True,
        future_summary,
        build_readback_record(),
    )
    assert future_contract["readback_record_valid"] is True
    assert future_contract["missing_readback_prerequisite_count"] == 1
    assert future_contract["missing_readback_prerequisites"] == [
        "separate_durable_authoring_final_no_save_release_after_readback_contract"
    ]
    assert future_contract["reported_allowed_readback_count"] == 3
    assert future_contract["reported_forbidden_readback_count"] == 0
    assert future_contract["durable_authoring_command_result_readback_accepted"] is False
    assert future_contract["asset_write_performed"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    unsafe_contract = readback.build_durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        True,
        future_summary,
        build_readback_record(reported_completed_readback_count=1),
    )
    assert unsafe_contract["readback_record_valid"] is False
    assert unsafe_contract["readback_record_rejected"] is True
    assert unsafe_contract["unsafe_readback_record_count"] == 1
    assert unsafe_contract["reported_forbidden_readback_count"] == 1
    unsafe_summary = readback.summarize_durable_executor_authoring_command_result_readbacks_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [unsafe_contract]
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["readback_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_readback_record_count"] == 1
    assert unsafe_summary["durable_authoring_command_result_readback_accepted_count"] == 0
    assert unsafe_summary["save_delete_rename_allowed_count"] == 0

    print(
        "BP authoring durable executor authoring command result readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

