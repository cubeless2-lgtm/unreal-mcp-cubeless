#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_authoring_command_execution_evidence_after_execution_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_command_execution_after_dispatch_contract as execution  # noqa: E402
import bp_authoring_durable_executor_authoring_command_execution_evidence_after_execution_contract as evidence  # noqa: E402


def build_current_execution_after_dispatch_summary() -> dict:
    return {
        "schema": execution.DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_AFTER_DISPATCH_SUMMARY_SCHEMA,
        "status": "passed",
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
    }


def build_evidence_record(**overrides: object) -> dict:
    record = {
        "schema": evidence.DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_AFTER_EXECUTION_RECORD_SCHEMA,
        "evidence_scope": evidence.EXPECTED_EVIDENCE_SCOPE,
        "explicit_durable_authoring_command_execution_evidence_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
        "durable_authoring_command_completion_decision_started": False,
        "durable_authoring_command_completion_decision_accepted": False,
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
        "save_asset_attempted": False,
        "save_asset_authorized": False,
        "save_asset_executed": False,
        "delete_asset_attempted": False,
        "delete_asset_authorized": False,
        "rename_asset_attempted": False,
        "rename_asset_authorized": False,
        "cleanup_attempted": False,
        "cleanup_authorized": False,
        "live_command_dispatch_performed": False,
        "live_command_dispatched": False,
        "live_command_execution_performed": False,
        "live_command_executed": False,
        "reported_authoring_create_command_count": 1,
        "reported_authoring_compile_command_count": 1,
        "reported_authoring_marker_write_command_count": 1,
        "reported_authoring_marker_readback_command_count": 1,
        "reported_authoring_read_only_exists_check_command_count": 1,
        "reported_authoring_save_command_count": 0,
        "reported_authoring_delete_rename_command_count": 0,
        "reported_authoring_cleanup_command_count": 0,
        "reported_authoring_duplicate_replace_command_count": 0,
        "reported_authoring_live_dispatch_execution_command_count": 0,
        "reported_package_dirty_count": 0,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_execution_after_dispatch_summary()
    contract = (
        evidence.build_durable_executor_authoring_command_execution_evidence_after_execution_contract(
            True,
            current_summary,
        )
    )
    assert (
        contract["schema"]
        == evidence.DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_AFTER_EXECUTION_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["evidence_contract_defined"] is True
    assert contract["execution_contract_ready"] is True
    assert contract["execution_inputs_satisfied"] is False
    assert contract["execution_record_valid"] is False
    assert contract["planned_authoring_commands_present"] is False
    assert contract["allowed_authoring_commands_present"] is False
    assert contract["allowed_execution_observed"] is False
    assert contract["no_forbidden_execution_claims"] is False
    assert contract["evidence_inputs_satisfied"] is False
    assert contract["evidence_record_present"] is False
    assert contract["authoring_command_execution_evidence_admitted"] is False
    assert contract["evidence_record_rejected"] is False
    assert contract["unsafe_evidence_record_count"] == 0
    assert contract["missing_evidence_prerequisite_count"] == 16
    assert "section_131_execution_inputs_satisfied" in contract[
        "missing_evidence_prerequisites"
    ]
    assert "section_131_execution_record_valid" in contract[
        "missing_evidence_prerequisites"
    ]
    assert "section_131_allowed_execution_observed" in contract[
        "missing_evidence_prerequisites"
    ]
    assert "section_131_no_forbidden_execution_claims" in contract[
        "missing_evidence_prerequisites"
    ]
    assert (
        "durable_authoring_command_execution_evidence_after_execution_record_present"
        in contract["missing_evidence_prerequisites"]
    )
    assert "explicit_durable_mvp_request_reconfirmed" in contract[
        "missing_evidence_prerequisites"
    ]
    assert "separate_durable_authoring_command_completion_decision_contract" in contract[
        "missing_evidence_prerequisites"
    ]
    assert contract["durable_authoring_command_completion_decision_started"] is False
    assert contract["durable_authoring_command_execution_allowed"] is False
    assert contract["durable_authoring_command_executed"] is False
    assert contract["asset_write_performed"] is False
    assert contract["package_dirty_marked"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = evidence.summarize_durable_executor_authoring_command_execution_evidence_after_execution(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_command_execution_evidence_after_execution_count"
        ]
        == 1
    )
    assert summary["evidence_contract_defined_count"] == 1
    assert summary["execution_contract_ready_count"] == 1
    assert summary["execution_record_valid_count"] == 0
    assert summary["authoring_command_execution_evidence_admitted_count"] == 0
    assert summary["evidence_record_rejected_count"] == 0
    assert summary["unsafe_evidence_record_count"] == 0
    assert summary["missing_evidence_prerequisite_count"] == 16
    assert summary["reported_allowed_evidence_command_count"] == 0
    assert summary["reported_forbidden_evidence_command_count"] == 0
    assert summary["durable_authoring_command_completion_decision_started_count"] == 0
    assert summary["durable_authoring_command_execution_allowed_count"] == 0
    assert summary["durable_authoring_command_executed_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["package_dirty_marked_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    future_summary = {
        **current_summary,
        "execution_inputs_satisfied_count": 1,
        "execution_record_valid_count": 1,
        "planned_authoring_commands_present_count": 1,
        "allowed_authoring_commands_present_count": 1,
        "allowed_execution_observed_count": 1,
        "no_forbidden_execution_claims_count": 1,
        "reported_allowed_execution_count": 6,
    }
    admitted_contract = (
        evidence.build_durable_executor_authoring_command_execution_evidence_after_execution_contract(
            True,
            future_summary,
            build_evidence_record(),
        )
    )
    assert admitted_contract["authoring_command_execution_evidence_admitted"] is True
    assert admitted_contract["missing_evidence_prerequisite_count"] == 1
    assert admitted_contract["missing_evidence_prerequisites"] == [
        "separate_durable_authoring_command_completion_decision_contract"
    ]
    assert admitted_contract["reported_allowed_evidence_command_count"] == 5
    assert admitted_contract["reported_forbidden_evidence_command_count"] == 0
    assert admitted_contract["durable_authoring_command_completion_decision_started"] is False
    assert admitted_contract["durable_authoring_command_execution_allowed"] is False
    assert admitted_contract["durable_authoring_command_executed"] is False
    assert admitted_contract["asset_write_performed"] is False
    assert admitted_contract["package_dirty_marked"] is False
    assert admitted_contract["save_delete_rename_allowed"] is False

    forbidden_contract = (
        evidence.build_durable_executor_authoring_command_execution_evidence_after_execution_contract(
            True,
            future_summary,
            build_evidence_record(reported_authoring_save_command_count=1),
        )
    )
    assert forbidden_contract["authoring_command_execution_evidence_admitted"] is False
    assert forbidden_contract["evidence_record_rejected"] is True
    assert forbidden_contract["unsafe_evidence_record_count"] == 1
    assert forbidden_contract["reported_forbidden_evidence_command_count"] == 1
    forbidden_summary = evidence.summarize_durable_executor_authoring_command_execution_evidence_after_execution(
        [forbidden_contract]
    )
    assert forbidden_summary["status"] == "failed"
    assert forbidden_summary["evidence_record_rejected_count"] == 1
    assert forbidden_summary["unsafe_evidence_record_count"] == 1
    assert forbidden_summary["reported_forbidden_evidence_command_count"] == 1
    assert forbidden_summary["durable_authoring_command_completion_decision_started_count"] == 0
    assert forbidden_summary["durable_authoring_command_execution_allowed_count"] == 0
    assert forbidden_summary["durable_authoring_command_executed_count"] == 0

    action_claim = (
        evidence.build_durable_executor_authoring_command_execution_evidence_after_execution_contract(
            True,
            future_summary,
            build_evidence_record(package_dirty_marked=True),
        )
    )
    assert action_claim["authoring_command_execution_evidence_admitted"] is False
    assert action_claim["evidence_record_rejected"] is True
    assert action_claim["unsafe_evidence_record_count"] == 1

    print(
        "BP authoring durable executor authoring command execution evidence after execution contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
