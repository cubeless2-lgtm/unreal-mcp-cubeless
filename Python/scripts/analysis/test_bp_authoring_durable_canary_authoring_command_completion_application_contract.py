#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_authoring_command_completion_application_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_authoring_command_completion_application_contract as application  # noqa: E402
import bp_authoring_durable_canary_authoring_command_completion_decision_contract as decision  # noqa: E402


def build_current_completion_decision_summary() -> dict:
    return {
        "schema": decision.CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_DECISION_SUMMARY_SCHEMA,
        "status": "passed",
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


def build_application_record(**overrides: object) -> dict:
    record = {
        "schema": application.CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_APPLICATION_RECORD_SCHEMA,
        "application_scope": application.EXPECTED_APPLICATION_SCOPE,
        "explicit_durable_authoring_command_completion_application_authorized": True,
        "operator_reconfirmed_no_save_delete_rename": True,
        "durable_authoring_command_completion_allowed": False,
        "durable_authoring_command_completed": False,
        "durable_authoring_command_application_allowed": False,
        "durable_authoring_command_application_applied": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "durable_authoring_command_dispatch_allowed": False,
        "durable_authoring_command_dispatched": False,
        "durable_authoring_command_execution_allowed": False,
        "durable_authoring_command_executed": False,
        "durable_release_promotion_allowed": False,
        "durable_release_promoted": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "save_asset_authorized": False,
        "save_asset_executed": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
        "live_command_dispatch_authorized": False,
        "live_command_dispatch_performed": False,
        "live_command_execution_authorized": False,
        "live_command_execution_performed": False,
        "live_command_executed": False,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_completion_decision_summary()
    contract = application.build_canary_durable_authoring_command_completion_application_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == application.CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_APPLICATION_SCHEMA
    assert contract["requested"] is True
    assert contract["application_contract_defined"] is True
    assert contract["completion_decision_contract_ready"] is True
    assert contract["evidence_ready_for_completion"] is False
    assert contract["completion_decision_record_valid"] is False
    assert contract["application_inputs_satisfied"] is False
    assert contract["application_record_present"] is False
    assert contract["record_schema_matches"] is False
    assert contract["application_scope_matches"] is False
    assert contract["explicit_application_authorized"] is False
    assert contract["no_save_delete_rename_acknowledged"] is False
    assert contract["application_record_valid"] is False
    assert contract["application_record_rejected"] is False
    assert contract["unsafe_application_record_count"] == 0
    assert contract["missing_application_prerequisite_count"] == 8
    assert "section_89_evidence_ready_for_completion" in contract["missing_application_prerequisites"]
    assert "section_89_completion_decision_record_valid" in contract["missing_application_prerequisites"]
    assert (
        "durable_authoring_command_completion_application_record_present"
        in contract["missing_application_prerequisites"]
    )
    assert (
        "durable_authoring_command_completion_application_record_schema"
        in contract["missing_application_prerequisites"]
    )
    assert (
        "durable_canary_authoring_command_completion_application_only_scope"
        in contract["missing_application_prerequisites"]
    )
    assert (
        "explicit_durable_authoring_command_completion_application_authorization"
        in contract["missing_application_prerequisites"]
    )
    assert "operator_reconfirmed_no_save_delete_rename" in contract["missing_application_prerequisites"]
    assert (
        "separate_durable_authoring_command_completion_result_contract"
        in contract["missing_application_prerequisites"]
    )
    assert contract["durable_authoring_command_completion_allowed"] is False
    assert contract["durable_authoring_command_completed"] is False
    assert contract["asset_write_allowed"] is False
    assert contract["asset_write_performed"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = application.summarize_canary_durable_authoring_command_completion_applications(
        [contract]
    )
    assert summary == {
        "schema": application.CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_APPLICATION_SUMMARY_SCHEMA,
        "status": "passed",
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

    future_summary = {
        **current_summary,
        "evidence_ready_for_completion_count": 1,
        "completion_decision_record_valid_count": 1,
        "reported_allowed_evidence_command_count": 5,
    }
    future_contract = application.build_canary_durable_authoring_command_completion_application_contract(
        True,
        future_summary,
        build_application_record(),
    )
    assert future_contract["application_record_valid"] is True
    assert future_contract["missing_application_prerequisite_count"] == 1
    assert future_contract["missing_application_prerequisites"] == [
        "separate_durable_authoring_command_completion_result_contract"
    ]
    assert future_contract["reported_allowed_evidence_command_count"] == 5
    assert future_contract["durable_authoring_command_completion_allowed"] is False
    assert future_contract["durable_authoring_command_completed"] is False
    assert future_contract["asset_write_allowed"] is False
    assert future_contract["asset_write_performed"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    unsafe_contract = application.build_canary_durable_authoring_command_completion_application_contract(
        True,
        future_summary,
        build_application_record(asset_write_performed=True),
    )
    assert unsafe_contract["application_record_valid"] is False
    assert unsafe_contract["application_record_rejected"] is True
    assert unsafe_contract["unsafe_application_record_count"] == 1
    unsafe_summary = application.summarize_canary_durable_authoring_command_completion_applications(
        [unsafe_contract]
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["application_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_application_record_count"] == 1
    assert unsafe_summary["asset_write_performed_count"] == 0
    assert unsafe_summary["save_delete_rename_allowed_count"] == 0

    print("BP authoring durable canary authoring command completion application contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
