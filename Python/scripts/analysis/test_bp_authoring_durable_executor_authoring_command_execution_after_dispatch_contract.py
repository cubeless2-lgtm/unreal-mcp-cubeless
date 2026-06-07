#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_authoring_command_execution_after_dispatch_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_command_dispatch_after_command_contract as dispatch  # noqa: E402
import bp_authoring_durable_executor_authoring_command_execution_after_dispatch_contract as execution  # noqa: E402


def build_current_dispatch_after_command_summary() -> dict:
    return {
        "schema": dispatch.DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_AFTER_COMMAND_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_executor_authoring_command_dispatch_after_command_count": 1,
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
        "dispatch_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_dispatch_observed_count": 0,
        "no_forbidden_dispatch_claims_count": 0,
        "dispatch_record_valid_count": 0,
        "dispatch_record_rejected_count": 0,
        "unsafe_dispatch_record_count": 0,
        "missing_dispatch_prerequisite_count": 14,
        "reported_allowed_dispatch_count": 0,
        "reported_forbidden_dispatch_count": 0,
        "durable_authoring_command_dispatch_started_count": 0,
        "durable_authoring_command_dispatch_accepted_count": 0,
        "durable_authoring_command_dispatch_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_execution_contract_started_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_command_contract_started_count": 0,
        "durable_authoring_command_contract_accepted_count": 0,
        "durable_authoring_command_allowed_count": 0,
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


def build_execution_record(**overrides: object) -> dict:
    record = {
        "schema": execution.DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_AFTER_DISPATCH_RECORD_SCHEMA,
        "execution_scope": execution.EXPECTED_EXECUTION_SCOPE,
        "explicit_durable_authoring_command_execution_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
        "durable_authoring_command_execution_started": False,
        "durable_authoring_command_execution_accepted": False,
        "durable_authoring_command_execution_allowed": False,
        "durable_authoring_command_executed": False,
        "durable_authoring_command_execution_evidence_contract_started": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "code_change_performed": False,
        "executor_code_modified": False,
        "unreal_asset_modified": False,
        "live_bridge_probe_started": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "save_asset_executed": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
        "live_command_dispatch_performed": False,
        "live_command_dispatched": False,
        "live_command_execution_performed": False,
        "live_command_executed": False,
        "reported_execution_gate_count": 1,
        "reported_dispatch_revalidated_count": 1,
        "reported_no_live_execution_performed_count": 1,
        "reported_no_execution_evidence_admitted_count": 1,
        "reported_no_asset_write_execution_count": 1,
        "reported_no_save_delete_rename_execution_count": 1,
        "reported_authoring_command_execution_count": 0,
        "reported_execution_evidence_count": 0,
        "reported_live_execution_count": 0,
        "reported_live_dispatch_count": 0,
        "reported_code_change_count": 0,
        "reported_executor_code_modified_count": 0,
        "reported_unreal_asset_change_count": 0,
        "reported_live_probe_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_dispatch_after_command_summary()
    contract = execution.build_durable_executor_authoring_command_execution_after_dispatch_contract(
        True,
        current_summary,
    )
    assert (
        contract["schema"]
        == execution.DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_AFTER_DISPATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["execution_contract_defined"] is True
    assert contract["dispatch_contract_ready"] is True
    assert contract["dispatch_inputs_satisfied"] is False
    assert contract["dispatch_record_valid"] is False
    assert contract["planned_authoring_commands_present"] is False
    assert contract["allowed_authoring_commands_present"] is False
    assert contract["allowed_dispatch_observed"] is False
    assert contract["no_forbidden_dispatch_claims"] is False
    assert contract["execution_inputs_satisfied"] is False
    assert contract["execution_record_present"] is False
    assert contract["execution_record_valid"] is False
    assert contract["execution_record_rejected"] is False
    assert contract["unsafe_execution_record_count"] == 0
    assert contract["missing_execution_prerequisite_count"] == 16
    assert "section_130_dispatch_inputs_satisfied" in contract[
        "missing_execution_prerequisites"
    ]
    assert "section_130_dispatch_record_valid" in contract[
        "missing_execution_prerequisites"
    ]
    assert "section_130_allowed_dispatch_observed" in contract[
        "missing_execution_prerequisites"
    ]
    assert "section_130_no_forbidden_dispatch_claims" in contract[
        "missing_execution_prerequisites"
    ]
    assert "durable_authoring_command_execution_after_dispatch_record_present" in contract[
        "missing_execution_prerequisites"
    ]
    assert "explicit_durable_mvp_request_reconfirmed" in contract[
        "missing_execution_prerequisites"
    ]
    assert "separate_durable_authoring_command_execution_evidence_contract" in contract[
        "missing_execution_prerequisites"
    ]
    assert contract["durable_authoring_command_execution_started"] is False
    assert contract["durable_authoring_command_execution_accepted"] is False
    assert contract["durable_authoring_command_execution_allowed"] is False
    assert contract["durable_authoring_command_executed"] is False
    assert contract["durable_authoring_command_execution_evidence_contract_started"] is False
    assert contract["asset_write_performed"] is False
    assert contract["package_dirty_marked"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = (
        execution.summarize_durable_executor_authoring_command_executions_after_dispatch(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_command_execution_after_dispatch_count"
        ]
        == 1
    )
    assert summary["execution_contract_defined_count"] == 1
    assert summary["dispatch_contract_ready_count"] == 1
    assert summary["execution_record_valid_count"] == 0
    assert summary["execution_record_rejected_count"] == 0
    assert summary["unsafe_execution_record_count"] == 0
    assert summary["missing_execution_prerequisite_count"] == 16
    assert summary["reported_allowed_execution_count"] == 0
    assert summary["reported_forbidden_execution_count"] == 0
    assert summary["durable_authoring_command_execution_started_count"] == 0
    assert summary["durable_authoring_command_execution_accepted_count"] == 0
    assert summary["durable_authoring_command_execution_allowed_count"] == 0
    assert summary["durable_authoring_command_executed_count"] == 0
    assert summary["durable_authoring_command_execution_evidence_contract_started_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["package_dirty_marked_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    future_summary = {
        **current_summary,
        "dispatch_inputs_satisfied_count": 1,
        "dispatch_record_valid_count": 1,
        "planned_authoring_commands_present_count": 1,
        "allowed_authoring_commands_present_count": 1,
        "allowed_dispatch_observed_count": 1,
        "no_forbidden_dispatch_claims_count": 1,
    }
    future_contract = (
        execution.build_durable_executor_authoring_command_execution_after_dispatch_contract(
            True,
            future_summary,
            build_execution_record(),
        )
    )
    assert future_contract["execution_record_valid"] is True
    assert future_contract["missing_execution_prerequisite_count"] == 1
    assert future_contract["missing_execution_prerequisites"] == [
        "separate_durable_authoring_command_execution_evidence_contract"
    ]
    assert future_contract["reported_allowed_execution_count"] == 6
    assert future_contract["reported_forbidden_execution_count"] == 0
    assert future_contract["durable_authoring_command_execution_allowed"] is False
    assert future_contract["durable_authoring_command_executed"] is False
    assert future_contract["durable_authoring_command_execution_evidence_contract_started"] is False
    assert future_contract["asset_write_performed"] is False
    assert future_contract["package_dirty_marked"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    unsafe_contract = (
        execution.build_durable_executor_authoring_command_execution_after_dispatch_contract(
            True,
            future_summary,
            build_execution_record(durable_authoring_command_executed=True),
        )
    )
    assert unsafe_contract["execution_record_valid"] is False
    assert unsafe_contract["execution_record_rejected"] is True
    assert unsafe_contract["unsafe_execution_record_count"] == 1
    unsafe_summary = (
        execution.summarize_durable_executor_authoring_command_executions_after_dispatch(
            [unsafe_contract]
        )
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["execution_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_execution_record_count"] == 1
    assert unsafe_summary["durable_authoring_command_executed_count"] == 0

    forbidden_contract = (
        execution.build_durable_executor_authoring_command_execution_after_dispatch_contract(
            True,
            future_summary,
            build_execution_record(reported_package_dirty_count=1),
        )
    )
    assert forbidden_contract["execution_record_valid"] is False
    assert forbidden_contract["execution_record_rejected"] is True
    assert forbidden_contract["reported_forbidden_execution_count"] == 1
    assert forbidden_contract["unsafe_execution_record_count"] == 1

    print(
        "BP authoring durable executor authoring command execution after dispatch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
