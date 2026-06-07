#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_authoring_command_execution_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_authoring_command_dispatch_contract as dispatch  # noqa: E402
import bp_authoring_durable_canary_authoring_command_execution_contract as execution  # noqa: E402


def build_current_dispatch_summary() -> dict:
    return {
        "schema": dispatch.CANARY_DURABLE_AUTHORING_COMMAND_DISPATCH_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_authoring_command_dispatch_count": 1,
        "dispatch_contract_defined_count": 1,
        "authoring_command_contract_ready_count": 1,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "planned_authoring_commands_present_count": 0,
        "allowed_authoring_commands_present_count": 0,
        "dispatch_inputs_satisfied_count": 0,
        "dispatch_record_present_count": 0,
        "record_schema_matches_count": 0,
        "dispatch_scope_matches_count": 0,
        "explicit_dispatch_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "dispatch_record_valid_count": 0,
        "dispatch_record_rejected_count": 0,
        "unsafe_dispatch_record_count": 0,
        "missing_dispatch_prerequisite_count": 10,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
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


def build_execution_record(**overrides: object) -> dict:
    record = {
        "schema": execution.CANARY_DURABLE_AUTHORING_COMMAND_EXECUTION_RECORD_SCHEMA,
        "execution_scope": execution.EXPECTED_EXECUTION_SCOPE,
        "explicit_durable_authoring_command_execution_authorized": True,
        "operator_reconfirmed_no_save_delete_rename": True,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "durable_authoring_command_dispatch_allowed": False,
        "durable_authoring_command_dispatched": False,
        "durable_authoring_command_execution_allowed": False,
        "durable_authoring_command_executed": False,
        "save_asset_authorized": False,
        "save_asset_executed": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
        "live_command_dispatch_performed": False,
        "live_command_execution_performed": False,
        "live_command_executed": False,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_dispatch_summary()
    contract = execution.build_canary_durable_authoring_command_execution_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == execution.CANARY_DURABLE_AUTHORING_COMMAND_EXECUTION_SCHEMA
    assert contract["requested"] is True
    assert contract["execution_contract_defined"] is True
    assert contract["dispatch_contract_ready"] is True
    assert contract["dispatch_inputs_satisfied"] is False
    assert contract["dispatch_record_valid"] is False
    assert contract["planned_authoring_commands_present"] is False
    assert contract["allowed_authoring_commands_present"] is False
    assert contract["execution_inputs_satisfied"] is False
    assert contract["execution_record_present"] is False
    assert contract["record_schema_matches"] is False
    assert contract["execution_scope_matches"] is False
    assert contract["explicit_execution_authorized"] is False
    assert contract["no_save_delete_rename_acknowledged"] is False
    assert contract["execution_record_valid"] is False
    assert contract["execution_record_rejected"] is False
    assert contract["unsafe_execution_record_count"] == 0
    assert contract["missing_execution_prerequisite_count"] == 10
    assert "section_86_dispatch_inputs_satisfied" in contract["missing_execution_prerequisites"]
    assert "section_86_dispatch_record_valid" in contract["missing_execution_prerequisites"]
    assert "section_86_planned_authoring_commands_present" in contract["missing_execution_prerequisites"]
    assert "section_86_allowed_authoring_commands_present" in contract["missing_execution_prerequisites"]
    assert "durable_authoring_command_execution_record_present" in contract["missing_execution_prerequisites"]
    assert "durable_authoring_command_execution_record_schema" in contract["missing_execution_prerequisites"]
    assert "durable_canary_authoring_command_execution_only_scope" in contract["missing_execution_prerequisites"]
    assert "explicit_durable_authoring_command_execution_authorization" in contract["missing_execution_prerequisites"]
    assert "operator_reconfirmed_no_save_delete_rename" in contract["missing_execution_prerequisites"]
    assert (
        "separate_durable_authoring_command_execution_evidence_contract"
        in contract["missing_execution_prerequisites"]
    )
    assert contract["durable_authoring_command_dispatch_allowed"] is False
    assert contract["durable_authoring_command_dispatched"] is False
    assert contract["durable_authoring_command_execution_allowed"] is False
    assert contract["durable_authoring_command_executed"] is False

    summary = execution.summarize_canary_durable_authoring_command_executions([contract])
    assert summary == {
        "schema": execution.CANARY_DURABLE_AUTHORING_COMMAND_EXECUTION_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_authoring_command_execution_count": 1,
        "execution_contract_defined_count": 1,
        "dispatch_contract_ready_count": 1,
        "dispatch_inputs_satisfied_count": 0,
        "dispatch_record_valid_count": 0,
        "planned_authoring_commands_present_count": 0,
        "allowed_authoring_commands_present_count": 0,
        "execution_inputs_satisfied_count": 0,
        "execution_record_present_count": 0,
        "record_schema_matches_count": 0,
        "execution_scope_matches_count": 0,
        "explicit_execution_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "execution_record_valid_count": 0,
        "execution_record_rejected_count": 0,
        "unsafe_execution_record_count": 0,
        "missing_execution_prerequisite_count": 10,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_allowed_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
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
        "dispatch_inputs_satisfied_count": 1,
        "dispatch_record_present_count": 1,
        "record_schema_matches_count": 1,
        "dispatch_scope_matches_count": 1,
        "explicit_dispatch_authorized_count": 1,
        "no_save_delete_rename_acknowledged_count": 1,
        "dispatch_record_valid_count": 1,
        "planned_authoring_commands_present_count": 1,
        "allowed_authoring_commands_present_count": 1,
        "reported_allowed_evidence_command_count": 4,
    }
    future_contract = execution.build_canary_durable_authoring_command_execution_contract(
        True,
        future_summary,
        build_execution_record(),
    )
    assert future_contract["execution_record_valid"] is True
    assert future_contract["missing_execution_prerequisite_count"] == 1
    assert future_contract["missing_execution_prerequisites"] == [
        "separate_durable_authoring_command_execution_evidence_contract"
    ]
    assert future_contract["durable_authoring_command_dispatch_allowed"] is False
    assert future_contract["durable_authoring_command_dispatched"] is False
    assert future_contract["durable_authoring_command_execution_allowed"] is False
    assert future_contract["durable_authoring_command_executed"] is False
    assert future_contract["durable_authoring_allowed"] is False
    assert future_contract["reported_allowed_evidence_command_count"] == 4

    unsafe_contract = execution.build_canary_durable_authoring_command_execution_contract(
        True,
        future_summary,
        build_execution_record(durable_authoring_command_executed=True),
    )
    assert unsafe_contract["execution_record_valid"] is False
    assert unsafe_contract["execution_record_rejected"] is True
    assert unsafe_contract["unsafe_execution_record_count"] == 1
    unsafe_summary = execution.summarize_canary_durable_authoring_command_executions(
        [unsafe_contract]
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["execution_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_execution_record_count"] == 1
    assert unsafe_summary["durable_authoring_command_executed_count"] == 0
    assert unsafe_summary["durable_authoring_allowed_count"] == 0

    print("BP authoring durable canary authoring command execution contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
