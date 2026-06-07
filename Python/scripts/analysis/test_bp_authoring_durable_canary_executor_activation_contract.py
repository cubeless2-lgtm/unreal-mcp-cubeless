#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_executor_activation_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_executor_activation_contract as executor_activation  # noqa: E402
import bp_authoring_durable_canary_release_promotion_decision_contract as promotion_decision  # noqa: E402


def build_current_promotion_decision_summary() -> dict:
    return {
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


def build_activation_record(**overrides: object) -> dict:
    record = {
        "schema": executor_activation.CANARY_DURABLE_EXECUTOR_ACTIVATION_RECORD_SCHEMA,
        "activation_scope": executor_activation.EXPECTED_ACTIVATION_SCOPE,
        "explicit_durable_executor_activation_authorized": True,
        "operator_reconfirmed_no_save_delete_rename": True,
        "durable_authoring_authorized": False,
        "durable_executor_open_authorized": False,
        "save_asset_authorized": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_promotion_decision_summary()
    contract = executor_activation.build_canary_durable_executor_activation_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == executor_activation.CANARY_DURABLE_EXECUTOR_ACTIVATION_SCHEMA
    assert contract["requested"] is True
    assert contract["activation_contract_defined"] is True
    assert contract["promotion_decision_contract_ready"] is True
    assert contract["evidence_ready_for_promotion"] is False
    assert contract["promotion_decision_record_valid"] is False
    assert contract["activation_inputs_satisfied"] is False
    assert contract["activation_record_present"] is False
    assert contract["record_schema_matches"] is False
    assert contract["activation_scope_matches"] is False
    assert contract["explicit_activation_authorized"] is False
    assert contract["no_save_delete_rename_acknowledged"] is False
    assert contract["activation_record_valid"] is False
    assert contract["activation_record_rejected"] is False
    assert contract["unsafe_activation_record_count"] == 0
    assert contract["missing_activation_prerequisite_count"] == 8
    assert "section_81_evidence_ready_for_promotion" in contract["missing_activation_prerequisites"]
    assert "section_81_promotion_decision_record_valid" in contract["missing_activation_prerequisites"]
    assert "durable_executor_activation_record_present" in contract["missing_activation_prerequisites"]
    assert "durable_executor_activation_record_schema" in contract["missing_activation_prerequisites"]
    assert "durable_canary_executor_activation_only_scope" in contract["missing_activation_prerequisites"]
    assert "explicit_durable_executor_activation_authorization" in contract["missing_activation_prerequisites"]
    assert "operator_reconfirmed_no_save_delete_rename" in contract["missing_activation_prerequisites"]
    assert "separate_durable_executor_open_contract" in contract["missing_activation_prerequisites"]
    assert contract["durable_executor_activation_allowed"] is False
    assert contract["durable_executor_activated"] is False
    assert contract["durable_executor_may_open_after_activation"] is False

    summary = executor_activation.summarize_canary_durable_executor_activations([contract])
    assert summary == {
        "schema": executor_activation.CANARY_DURABLE_EXECUTOR_ACTIVATION_SUMMARY_SCHEMA,
        "status": "passed",
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

    future_summary = {
        **current_summary,
        "evidence_ready_for_promotion_count": 1,
        "promotion_decision_record_valid_count": 1,
        "reported_allowed_evidence_command_count": 4,
    }
    future_contract = executor_activation.build_canary_durable_executor_activation_contract(
        True,
        future_summary,
        build_activation_record(),
    )
    assert future_contract["activation_record_valid"] is True
    assert future_contract["missing_activation_prerequisite_count"] == 1
    assert future_contract["missing_activation_prerequisites"] == [
        "separate_durable_executor_open_contract"
    ]
    assert future_contract["durable_executor_activation_allowed"] is False
    assert future_contract["durable_executor_activated"] is False
    assert future_contract["durable_executor_may_open_after_activation"] is False
    assert future_contract["reported_allowed_evidence_command_count"] == 4

    unsafe_contract = executor_activation.build_canary_durable_executor_activation_contract(
        True,
        future_summary,
        build_activation_record(durable_executor_open_authorized=True),
    )
    assert unsafe_contract["activation_record_valid"] is False
    assert unsafe_contract["activation_record_rejected"] is True
    assert unsafe_contract["unsafe_activation_record_count"] == 1
    unsafe_summary = executor_activation.summarize_canary_durable_executor_activations([unsafe_contract])
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["activation_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_activation_record_count"] == 1
    assert unsafe_summary["durable_executor_may_open_after_activation_count"] == 0

    print("BP authoring durable canary executor activation contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
