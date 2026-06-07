#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_authoring_command_completion_decision_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_command_completion_decision_contract as completion_decision  # noqa: E402
import bp_authoring_durable_executor_authoring_command_execution_evidence_contract as evidence  # noqa: E402


def build_current_evidence_summary() -> dict:
    return {
        "schema": (
            evidence.DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_SUMMARY_SCHEMA
        ),
        "status": "passed",
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


def build_completion_decision_record(**overrides: object) -> dict:
    record = {
        "schema": (
            completion_decision.DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_DECISION_RECORD_SCHEMA
        ),
        "completion_scope": completion_decision.EXPECTED_COMPLETION_SCOPE,
        "explicit_durable_authoring_command_completion_decision_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
        "durable_authoring_command_completion_allowed": False,
        "durable_authoring_command_completed": False,
        "durable_authoring_command_completion_application_started": False,
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
        "asset_write_performed": False,
        "package_dirty_marked": False,
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
    current_summary = build_current_evidence_summary()
    contract = (
        completion_decision.build_durable_executor_authoring_command_completion_decision_contract(
            True,
            current_summary,
        )
    )
    assert contract["schema"] == completion_decision.DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_DECISION_SCHEMA
    assert contract["requested"] is True
    assert contract["completion_decision_contract_defined"] is True
    assert contract["evidence_contract_ready"] is True
    assert contract["authoring_command_execution_evidence_admitted"] is False
    assert contract["allowed_evidence_command_observed"] is False
    assert contract["no_forbidden_evidence_commands"] is False
    assert contract["evidence_ready_for_completion"] is False
    assert contract["decision_record_present"] is False
    assert contract["record_schema_matches"] is False
    assert contract["completion_scope_matches"] is False
    assert contract["explicit_completion_decision_authorized"] is False
    assert contract["completion_decision_status_passed"] is False
    assert contract["no_save_delete_rename_acknowledged"] is False
    assert contract["explicit_durable_mvp_request_reconfirmed"] is False
    assert contract["completion_decision_record_valid"] is False
    assert contract["completion_decision_record_rejected"] is False
    assert contract["unsafe_completion_decision_record_count"] == 0
    assert contract["missing_completion_prerequisite_count"] == 11
    assert "section_116_authoring_command_execution_evidence_admitted" in contract[
        "missing_completion_prerequisites"
    ]
    assert "section_116_allowed_evidence_command_observed" in contract[
        "missing_completion_prerequisites"
    ]
    assert "section_116_no_forbidden_evidence_commands" in contract[
        "missing_completion_prerequisites"
    ]
    assert "durable_authoring_command_completion_decision_record_present" in contract[
        "missing_completion_prerequisites"
    ]
    assert "durable_executor_authoring_command_completion_decision_only_scope" in contract[
        "missing_completion_prerequisites"
    ]
    assert "explicit_durable_authoring_command_completion_decision_authorization" in contract[
        "missing_completion_prerequisites"
    ]
    assert "durable_authoring_command_completion_decision_status_passed" in contract[
        "missing_completion_prerequisites"
    ]
    assert "explicit_durable_mvp_request_reconfirmed" in contract[
        "missing_completion_prerequisites"
    ]
    assert "separate_durable_authoring_command_completion_application_contract" in contract[
        "missing_completion_prerequisites"
    ]
    assert contract["durable_authoring_command_completion_allowed"] is False
    assert contract["durable_authoring_command_completed"] is False
    assert contract["durable_authoring_command_completion_application_started"] is False
    assert contract["asset_write_performed"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = (
        completion_decision.summarize_durable_executor_authoring_command_completion_decisions(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert summary["durable_requested_executor_authoring_command_completion_decision_count"] == 1
    assert summary["completion_decision_contract_defined_count"] == 1
    assert summary["evidence_contract_ready_count"] == 1
    assert summary["authoring_command_execution_evidence_admitted_count"] == 0
    assert summary["evidence_ready_for_completion_count"] == 0
    assert summary["completion_decision_record_valid_count"] == 0
    assert summary["completion_decision_record_rejected_count"] == 0
    assert summary["unsafe_completion_decision_record_count"] == 0
    assert summary["missing_completion_prerequisite_count"] == 11
    assert summary["reported_allowed_evidence_command_count"] == 0
    assert summary["reported_forbidden_evidence_command_count"] == 0
    assert summary["durable_authoring_command_completion_allowed_count"] == 0
    assert summary["durable_authoring_command_completed_count"] == 0
    assert summary["durable_authoring_command_completion_application_started_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    future_summary = {
        **current_summary,
        "authoring_command_execution_evidence_admitted_count": 1,
        "allowed_evidence_command_observed_count": 1,
        "no_forbidden_evidence_commands_count": 1,
        "reported_allowed_evidence_command_count": 5,
    }
    future_contract = (
        completion_decision.build_durable_executor_authoring_command_completion_decision_contract(
            True,
            future_summary,
            build_completion_decision_record(),
        )
    )
    assert future_contract["completion_decision_record_valid"] is True
    assert future_contract["missing_completion_prerequisite_count"] == 1
    assert future_contract["missing_completion_prerequisites"] == [
        "separate_durable_authoring_command_completion_application_contract"
    ]
    assert future_contract["reported_allowed_evidence_command_count"] == 5
    assert future_contract["durable_authoring_command_completion_allowed"] is False
    assert future_contract["durable_authoring_command_completed"] is False
    assert future_contract["durable_authoring_command_completion_application_started"] is False
    assert future_contract["asset_write_performed"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    unsafe_contract = (
        completion_decision.build_durable_executor_authoring_command_completion_decision_contract(
            True,
            future_summary,
            build_completion_decision_record(save_asset_authorized=True),
        )
    )
    assert unsafe_contract["completion_decision_record_valid"] is False
    assert unsafe_contract["completion_decision_record_rejected"] is True
    assert unsafe_contract["unsafe_completion_decision_record_count"] == 1
    unsafe_summary = (
        completion_decision.summarize_durable_executor_authoring_command_completion_decisions(
            [unsafe_contract]
        )
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["completion_decision_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_completion_decision_record_count"] == 1
    assert unsafe_summary["durable_authoring_command_completion_allowed_count"] == 0
    assert unsafe_summary["durable_authoring_command_completed_count"] == 0
    assert unsafe_summary["save_delete_rename_allowed_count"] == 0

    action_claim = (
        completion_decision.build_durable_executor_authoring_command_completion_decision_contract(
            True,
            future_summary,
            build_completion_decision_record(asset_write_performed=True),
        )
    )
    assert action_claim["completion_decision_record_valid"] is False
    assert action_claim["completion_decision_record_rejected"] is True
    assert action_claim["unsafe_completion_decision_record_count"] == 1

    print(
        "BP authoring durable executor authoring command completion decision contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
