#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_release_promotion_decision_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_live_command_execution_evidence_admission_contract as evidence_admission  # noqa: E402
import bp_authoring_durable_canary_release_promotion_decision_contract as promotion_decision  # noqa: E402


def build_current_evidence_admission_summary() -> dict:
    return {
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


def build_promotion_decision_record(**overrides: object) -> dict:
    record = {
        "schema": promotion_decision.CANARY_DURABLE_RELEASE_PROMOTION_DECISION_RECORD_SCHEMA,
        "promotion_scope": promotion_decision.EXPECTED_PROMOTION_SCOPE,
        "explicit_durable_release_promotion_authorized": True,
        "operator_reconfirmed_no_save_delete_rename": True,
        "durable_authoring_authorized": False,
        "durable_executor_activation_authorized": False,
        "durable_executor_open_authorized": False,
        "save_asset_authorized": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_evidence_admission_summary()
    contract = promotion_decision.build_canary_durable_release_promotion_decision_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == promotion_decision.CANARY_DURABLE_RELEASE_PROMOTION_DECISION_SCHEMA
    assert contract["requested"] is True
    assert contract["promotion_decision_contract_defined"] is True
    assert contract["evidence_admission_contract_ready"] is True
    assert contract["execution_evidence_admitted"] is False
    assert contract["allowed_evidence_command_observed"] is False
    assert contract["no_forbidden_evidence_commands"] is False
    assert contract["evidence_ready_for_promotion"] is False
    assert contract["decision_record_present"] is False
    assert contract["record_schema_matches"] is False
    assert contract["promotion_scope_matches"] is False
    assert contract["explicit_promotion_authorized"] is False
    assert contract["no_save_delete_rename_acknowledged"] is False
    assert contract["promotion_decision_record_valid"] is False
    assert contract["promotion_decision_record_rejected"] is False
    assert contract["unsafe_promotion_decision_record_count"] == 0
    assert contract["missing_promotion_prerequisite_count"] == 9
    assert "section_80_execution_evidence_admitted" in contract["missing_promotion_prerequisites"]
    assert "section_80_allowed_evidence_command_observed" in contract["missing_promotion_prerequisites"]
    assert "section_80_no_forbidden_evidence_commands" in contract["missing_promotion_prerequisites"]
    assert "durable_release_promotion_decision_record_present" in contract["missing_promotion_prerequisites"]
    assert "durable_release_promotion_decision_record_schema" in contract["missing_promotion_prerequisites"]
    assert "durable_canary_release_promotion_only_scope" in contract["missing_promotion_prerequisites"]
    assert "explicit_durable_release_promotion_authorization" in contract["missing_promotion_prerequisites"]
    assert "operator_reconfirmed_no_save_delete_rename" in contract["missing_promotion_prerequisites"]
    assert "separate_durable_executor_activation_contract" in contract["missing_promotion_prerequisites"]
    assert contract["durable_release_promotion_allowed"] is False
    assert contract["durable_release_promoted"] is False
    assert contract["durable_executor_may_open_after_promotion_decision"] is False

    summary = promotion_decision.summarize_canary_durable_release_promotion_decisions([contract])
    assert summary == {
        "schema": promotion_decision.CANARY_DURABLE_RELEASE_PROMOTION_DECISION_SUMMARY_SCHEMA,
        "status": "passed",
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

    future_summary = {
        **current_summary,
        "execution_evidence_admitted_count": 1,
        "allowed_evidence_command_observed_count": 1,
        "no_forbidden_evidence_commands_count": 1,
        "reported_allowed_evidence_command_count": 4,
    }
    future_contract = promotion_decision.build_canary_durable_release_promotion_decision_contract(
        True,
        future_summary,
        build_promotion_decision_record(),
    )
    assert future_contract["promotion_decision_record_valid"] is True
    assert future_contract["missing_promotion_prerequisite_count"] == 1
    assert future_contract["missing_promotion_prerequisites"] == [
        "separate_durable_executor_activation_contract"
    ]
    assert future_contract["durable_release_promotion_allowed"] is False
    assert future_contract["durable_release_promoted"] is False
    assert future_contract["durable_executor_may_open_after_promotion_decision"] is False
    assert future_contract["reported_allowed_evidence_command_count"] == 4

    unsafe_contract = promotion_decision.build_canary_durable_release_promotion_decision_contract(
        True,
        future_summary,
        build_promotion_decision_record(durable_executor_activation_authorized=True),
    )
    assert unsafe_contract["promotion_decision_record_valid"] is False
    assert unsafe_contract["promotion_decision_record_rejected"] is True
    assert unsafe_contract["unsafe_promotion_decision_record_count"] == 1
    unsafe_summary = promotion_decision.summarize_canary_durable_release_promotion_decisions(
        [unsafe_contract]
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["promotion_decision_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_promotion_decision_record_count"] == 1
    assert unsafe_summary["durable_executor_may_open_after_promotion_decision_count"] == 0

    print("BP authoring durable canary release promotion decision contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
