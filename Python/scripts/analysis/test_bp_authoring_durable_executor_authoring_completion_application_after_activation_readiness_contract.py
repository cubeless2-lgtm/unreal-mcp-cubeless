#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_authoring_completion_application_after_activation_readiness_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_completion_application_after_activation_readiness_contract as application  # noqa: E402
import bp_authoring_durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract as decision  # noqa: E402


def build_current_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary() -> dict:
    return {
        "schema": decision.DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SUMMARY_SCHEMA,
        "status": "passed",
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


def build_application_record(**overrides: object) -> dict:
    record = {
        "schema": application.DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_RECORD_SCHEMA,
        "application_scope": application.EXPECTED_APPLICATION_SCOPE,
        "explicit_durable_authoring_command_completion_application_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
        "durable_authoring_command_completion_allowed": False,
        "durable_authoring_command_completed": False,
        "durable_authoring_command_application_allowed": False,
        "durable_authoring_command_application_applied": False,
        "asset_write_allowed": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "durable_authoring_command_dispatch_allowed": False,
        "durable_authoring_command_dispatched": False,
        "durable_authoring_command_execution_allowed": False,
        "durable_authoring_command_executed": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "code_change_performed": False,
        "executor_code_modified": False,
        "unreal_asset_modified": False,
        "live_bridge_probe_started": False,
        "save_asset_authorized": False,
        "save_asset_executed": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
        "live_command_dispatch_authorized": False,
        "live_command_dispatch_performed": False,
        "live_command_dispatched": False,
        "live_command_execution_authorized": False,
        "live_command_execution_performed": False,
        "live_command_executed": False,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary()
    contract = application.build_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        True,
        current_summary,
    )
    assert (
        contract["schema"]
        == application.DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["application_contract_defined"] is True
    assert contract["completion_decision_contract_ready"] is True
    assert contract["evidence_ready_for_completion"] is False
    assert contract["completion_decision_record_valid"] is False
    assert contract["application_inputs_satisfied"] is False
    assert contract["application_record_present"] is False
    assert contract["application_record_valid"] is False
    assert contract["application_record_rejected"] is False
    assert contract["unsafe_application_record_count"] == 0
    assert contract["missing_application_prerequisite_count"] == 10
    assert "section_149_evidence_ready_for_completion" in contract[
        "missing_application_prerequisites"
    ]
    assert "section_149_completion_decision_record_valid" in contract[
        "missing_application_prerequisites"
    ]
    assert "durable_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_record_present" in contract[
        "missing_application_prerequisites"
    ]
    assert (
        "durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_only_scope"
        in contract["missing_application_prerequisites"]
    )
    assert "explicit_durable_mvp_request_reconfirmed" in contract[
        "missing_application_prerequisites"
    ]
    assert "separate_durable_authoring_command_completion_result_after_application_contract" in contract[
        "missing_application_prerequisites"
    ]
    assert contract["durable_authoring_command_completion_allowed"] is False
    assert contract["durable_authoring_command_completed"] is False
    assert contract["durable_authoring_command_application_applied"] is False
    assert contract["asset_write_allowed"] is False
    assert contract["asset_write_performed"] is False
    assert contract["package_dirty_marked"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = application.summarize_durable_executor_authoring_command_completion_applications_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count"
        ]
        == 1
    )
    assert summary["application_contract_defined_count"] == 1
    assert summary["completion_decision_contract_ready_count"] == 1
    assert summary["evidence_ready_for_completion_count"] == 0
    assert summary["completion_decision_record_valid_count"] == 0
    assert summary["application_inputs_satisfied_count"] == 0
    assert summary["application_record_valid_count"] == 0
    assert summary["application_record_rejected_count"] == 0
    assert summary["unsafe_application_record_count"] == 0
    assert summary["missing_application_prerequisite_count"] == 10
    assert summary["durable_authoring_command_completion_allowed_count"] == 0
    assert summary["durable_authoring_command_completed_count"] == 0
    assert summary["durable_authoring_command_application_applied_count"] == 0
    assert summary["asset_write_allowed_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["package_dirty_marked_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    future_summary = {
        **current_summary,
        "evidence_ready_for_completion_count": 1,
        "completion_decision_record_valid_count": 1,
        "reported_allowed_evidence_command_count": 5,
    }
    future_contract = application.build_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        True,
        future_summary,
        build_application_record(),
    )
    assert future_contract["application_record_valid"] is True
    assert future_contract["missing_application_prerequisite_count"] == 1
    assert future_contract["missing_application_prerequisites"] == [
        "separate_durable_authoring_command_completion_result_after_application_contract"
    ]
    assert future_contract["reported_allowed_evidence_command_count"] == 5
    assert future_contract["durable_authoring_command_completion_allowed"] is False
    assert future_contract["durable_authoring_command_completed"] is False
    assert future_contract["asset_write_allowed"] is False
    assert future_contract["asset_write_performed"] is False
    assert future_contract["package_dirty_marked"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    unsafe_contract = application.build_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
        True,
        future_summary,
        build_application_record(asset_write_performed=True),
    )
    assert unsafe_contract["application_record_valid"] is False
    assert unsafe_contract["application_record_rejected"] is True
    assert unsafe_contract["unsafe_application_record_count"] == 1
    unsafe_summary = application.summarize_durable_executor_authoring_command_completion_applications_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
        [unsafe_contract]
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["application_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_application_record_count"] == 1
    assert unsafe_summary["asset_write_performed_count"] == 0
    assert unsafe_summary["package_dirty_marked_count"] == 0
    assert unsafe_summary["save_delete_rename_allowed_count"] == 0

    print(
        "BP authoring durable executor authoring command completion application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


