#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_live_command_execution_evidence_admission_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_live_command_execution_evidence_admission_contract as evidence_admission  # noqa: E402
import bp_authoring_durable_canary_live_command_execution_release_contract as execution_release  # noqa: E402


def build_current_execution_release_summary() -> dict:
    return {
        "schema": execution_release.CANARY_LIVE_COMMAND_EXECUTION_RELEASE_SUMMARY_SCHEMA,
        "status": "passed",
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


def build_evidence_record(**overrides: object) -> dict:
    record = {
        "schema": evidence_admission.CANARY_LIVE_COMMAND_EXECUTION_EVIDENCE_RECORD_SCHEMA,
        "evidence_scope": evidence_admission.EXPECTED_EVIDENCE_SCOPE,
        "explicit_live_command_execution_evidence_admission_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "authoring_attempted": False,
        "durable_authoring_attempted": False,
        "durable_authoring_authorized": False,
        "save_asset_attempted": False,
        "save_asset_authorized": False,
        "delete_asset_attempted": False,
        "delete_asset_authorized": False,
        "rename_asset_attempted": False,
        "rename_asset_authorized": False,
        "cleanup_attempted": False,
        "cleanup_authorized": False,
        "reported_live_creation_command_count": 1,
        "reported_live_compile_command_count": 1,
        "reported_live_marker_write_command_count": 1,
        "reported_live_marker_readback_command_count": 1,
        "reported_live_save_command_count": 0,
        "reported_live_delete_rename_command_count": 0,
        "reported_live_cleanup_command_count": 0,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_execution_release_summary()
    contract = evidence_admission.build_canary_live_command_execution_evidence_admission_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == evidence_admission.CANARY_LIVE_COMMAND_EXECUTION_EVIDENCE_ADMISSION_SCHEMA
    assert contract["requested"] is True
    assert contract["evidence_admission_contract_defined"] is True
    assert contract["execution_release_contract_ready"] is True
    assert contract["execution_inputs_satisfied"] is False
    assert contract["execution_release_record_valid"] is False
    assert contract["section_79_live_command_executed"] is False
    assert contract["evidence_inputs_satisfied"] is False
    assert contract["evidence_record_present"] is False
    assert contract["record_schema_matches"] is False
    assert contract["evidence_scope_matches"] is False
    assert contract["explicit_evidence_admission_authorized"] is False
    assert contract["evidence_status_passed"] is False
    assert contract["no_save_delete_rename_acknowledged"] is False
    assert contract["reported_allowed_evidence_command_count"] == 0
    assert contract["reported_forbidden_evidence_command_count"] == 0
    assert contract["allowed_evidence_command_observed"] is False
    assert contract["no_forbidden_evidence_commands"] is False
    assert contract["execution_evidence_admitted"] is False
    assert contract["evidence_record_rejected"] is False
    assert contract["unsafe_evidence_record_count"] == 0
    assert contract["missing_evidence_prerequisite_count"] == 12
    assert "section_79_execution_inputs_satisfied" in contract["missing_evidence_prerequisites"]
    assert "section_79_execution_release_record_valid" in contract["missing_evidence_prerequisites"]
    assert "section_79_live_command_executed" in contract["missing_evidence_prerequisites"]
    assert "live_command_execution_evidence_record_present" in contract["missing_evidence_prerequisites"]
    assert "live_command_execution_evidence_record_schema" in contract["missing_evidence_prerequisites"]
    assert "durable_canary_live_command_execution_evidence_only_scope" in contract["missing_evidence_prerequisites"]
    assert (
        "explicit_live_command_execution_evidence_admission_authorization"
        in contract["missing_evidence_prerequisites"]
    )
    assert "live_command_execution_evidence_status_passed" in contract["missing_evidence_prerequisites"]
    assert "operator_reconfirmed_no_save_delete_rename" in contract["missing_evidence_prerequisites"]
    assert "allowed_live_command_execution_evidence_observed" in contract["missing_evidence_prerequisites"]
    assert "no_forbidden_live_command_execution_evidence" in contract["missing_evidence_prerequisites"]
    assert "separate_durable_release_promotion_decision" in contract["missing_evidence_prerequisites"]
    assert contract["durable_promotion_allowed"] is False
    assert contract["durable_executor_may_open_after_evidence_admission"] is False
    assert contract["live_command_executed"] is False

    summary = evidence_admission.summarize_canary_live_command_execution_evidence_admissions([contract])
    assert summary == {
        "schema": evidence_admission.CANARY_LIVE_COMMAND_EXECUTION_EVIDENCE_ADMISSION_SUMMARY_SCHEMA,
        "status": "passed",
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

    future_summary = {
        **current_summary,
        "execution_inputs_satisfied_count": 1,
        "execution_release_record_valid_count": 1,
        "live_command_executed_count": 1,
    }
    admitted_contract = evidence_admission.build_canary_live_command_execution_evidence_admission_contract(
        True,
        future_summary,
        build_evidence_record(),
    )
    assert admitted_contract["execution_evidence_admitted"] is True
    assert admitted_contract["missing_evidence_prerequisite_count"] == 1
    assert admitted_contract["missing_evidence_prerequisites"] == [
        "separate_durable_release_promotion_decision"
    ]
    assert admitted_contract["reported_allowed_evidence_command_count"] == 4
    assert admitted_contract["reported_forbidden_evidence_command_count"] == 0
    assert admitted_contract["durable_promotion_allowed"] is False
    assert admitted_contract["durable_executor_may_open_after_evidence_admission"] is False
    assert admitted_contract["live_command_executed"] is False

    unsafe_contract = evidence_admission.build_canary_live_command_execution_evidence_admission_contract(
        True,
        future_summary,
        build_evidence_record(reported_live_save_command_count=1),
    )
    assert unsafe_contract["execution_evidence_admitted"] is False
    assert unsafe_contract["evidence_record_rejected"] is True
    assert unsafe_contract["unsafe_evidence_record_count"] == 1
    assert unsafe_contract["reported_forbidden_evidence_command_count"] == 1
    unsafe_summary = evidence_admission.summarize_canary_live_command_execution_evidence_admissions(
        [unsafe_contract]
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["evidence_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_evidence_record_count"] == 1
    assert unsafe_summary["reported_forbidden_evidence_command_count"] == 1
    assert unsafe_summary["durable_executor_may_open_after_evidence_admission_count"] == 0

    print("BP authoring durable canary live command execution evidence admission contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
