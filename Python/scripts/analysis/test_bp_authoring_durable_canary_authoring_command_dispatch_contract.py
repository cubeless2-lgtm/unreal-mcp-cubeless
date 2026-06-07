#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_authoring_command_dispatch_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_authoring_command_contract as authoring_command  # noqa: E402
import bp_authoring_durable_canary_authoring_command_dispatch_contract as dispatch  # noqa: E402


def build_current_authoring_command_summary() -> dict:
    return {
        "schema": authoring_command.CANARY_DURABLE_AUTHORING_COMMAND_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_authoring_command_count": 1,
        "authoring_command_contract_defined_count": 1,
        "authoring_enable_contract_ready_count": 1,
        "authoring_enable_inputs_satisfied_count": 0,
        "authoring_enable_record_valid_count": 0,
        "target_package_allowlist_reconfirmed_count": 0,
        "overwrite_rename_decision_reconfirmed_count": 0,
        "rollback_readiness_reconfirmed_count": 0,
        "ownership_marker_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_present_count": 0,
        "record_schema_matches_count": 0,
        "command_scope_matches_count": 0,
        "explicit_authoring_command_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "planned_authoring_command_count": 0,
        "allowed_authoring_command_count": 0,
        "forbidden_authoring_command_count": 0,
        "unknown_authoring_command_count": 0,
        "authoring_command_record_valid_count": 0,
        "authoring_command_record_rejected_count": 0,
        "unsafe_authoring_command_record_count": 0,
        "missing_authoring_command_prerequisite_count": 13,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
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


def build_dispatch_record(**overrides: object) -> dict:
    record = {
        "schema": dispatch.CANARY_DURABLE_AUTHORING_COMMAND_DISPATCH_RECORD_SCHEMA,
        "dispatch_scope": dispatch.EXPECTED_DISPATCH_SCOPE,
        "explicit_durable_authoring_command_dispatch_authorized": True,
        "operator_reconfirmed_no_save_delete_rename": True,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "durable_authoring_command_allowed": False,
        "durable_authoring_command_dispatched": False,
        "durable_authoring_command_executed": False,
        "save_asset_authorized": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
        "live_command_dispatch_performed": False,
        "live_command_execution_authorized": False,
        "live_command_executed": False,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_authoring_command_summary()
    contract = dispatch.build_canary_durable_authoring_command_dispatch_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == dispatch.CANARY_DURABLE_AUTHORING_COMMAND_DISPATCH_SCHEMA
    assert contract["requested"] is True
    assert contract["dispatch_contract_defined"] is True
    assert contract["authoring_command_contract_ready"] is True
    assert contract["authoring_command_inputs_satisfied"] is False
    assert contract["authoring_command_record_valid"] is False
    assert contract["planned_authoring_commands_present"] is False
    assert contract["allowed_authoring_commands_present"] is False
    assert contract["dispatch_inputs_satisfied"] is False
    assert contract["dispatch_record_present"] is False
    assert contract["record_schema_matches"] is False
    assert contract["dispatch_scope_matches"] is False
    assert contract["explicit_dispatch_authorized"] is False
    assert contract["no_save_delete_rename_acknowledged"] is False
    assert contract["dispatch_record_valid"] is False
    assert contract["dispatch_record_rejected"] is False
    assert contract["unsafe_dispatch_record_count"] == 0
    assert contract["missing_dispatch_prerequisite_count"] == 10
    assert "section_85_authoring_command_inputs_satisfied" in contract["missing_dispatch_prerequisites"]
    assert "section_85_authoring_command_record_valid" in contract["missing_dispatch_prerequisites"]
    assert "section_85_planned_authoring_commands_present" in contract["missing_dispatch_prerequisites"]
    assert "section_85_allowed_authoring_commands_present" in contract["missing_dispatch_prerequisites"]
    assert "durable_authoring_command_dispatch_record_present" in contract["missing_dispatch_prerequisites"]
    assert "durable_authoring_command_dispatch_record_schema" in contract["missing_dispatch_prerequisites"]
    assert "durable_canary_authoring_command_dispatch_only_scope" in contract["missing_dispatch_prerequisites"]
    assert "explicit_durable_authoring_command_dispatch_authorization" in contract["missing_dispatch_prerequisites"]
    assert "operator_reconfirmed_no_save_delete_rename" in contract["missing_dispatch_prerequisites"]
    assert "separate_durable_authoring_command_execution_contract" in contract["missing_dispatch_prerequisites"]
    assert contract["durable_authoring_command_dispatch_allowed"] is False
    assert contract["durable_authoring_command_dispatched"] is False
    assert contract["durable_authoring_command_execution_allowed"] is False
    assert contract["durable_authoring_command_executed"] is False

    summary = dispatch.summarize_canary_durable_authoring_command_dispatches([contract])
    assert summary == {
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

    future_summary = {
        **current_summary,
        "authoring_command_inputs_satisfied_count": 1,
        "authoring_command_record_present_count": 1,
        "record_schema_matches_count": 1,
        "command_scope_matches_count": 1,
        "explicit_authoring_command_authorized_count": 1,
        "no_save_delete_rename_acknowledged_count": 1,
        "planned_authoring_command_count": 4,
        "allowed_authoring_command_count": 4,
        "authoring_command_record_valid_count": 1,
        "reported_allowed_evidence_command_count": 4,
    }
    future_contract = dispatch.build_canary_durable_authoring_command_dispatch_contract(
        True,
        future_summary,
        build_dispatch_record(),
    )
    assert future_contract["dispatch_record_valid"] is True
    assert future_contract["missing_dispatch_prerequisite_count"] == 1
    assert future_contract["missing_dispatch_prerequisites"] == [
        "separate_durable_authoring_command_execution_contract"
    ]
    assert future_contract["durable_authoring_command_dispatch_allowed"] is False
    assert future_contract["durable_authoring_command_dispatched"] is False
    assert future_contract["durable_authoring_command_execution_allowed"] is False
    assert future_contract["durable_authoring_command_executed"] is False
    assert future_contract["durable_authoring_allowed"] is False
    assert future_contract["reported_allowed_evidence_command_count"] == 4

    unsafe_contract = dispatch.build_canary_durable_authoring_command_dispatch_contract(
        True,
        future_summary,
        build_dispatch_record(durable_authoring_command_dispatched=True),
    )
    assert unsafe_contract["dispatch_record_valid"] is False
    assert unsafe_contract["dispatch_record_rejected"] is True
    assert unsafe_contract["unsafe_dispatch_record_count"] == 1
    unsafe_summary = dispatch.summarize_canary_durable_authoring_command_dispatches(
        [unsafe_contract]
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["dispatch_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_dispatch_record_count"] == 1
    assert unsafe_summary["durable_authoring_command_dispatched_count"] == 0
    assert unsafe_summary["durable_authoring_command_executed_count"] == 0

    print("BP authoring durable canary authoring command dispatch contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
