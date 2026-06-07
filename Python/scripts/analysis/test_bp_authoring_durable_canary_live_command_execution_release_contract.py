#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_live_command_execution_release_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_live_command_dispatch_release_contract as dispatch_release  # noqa: E402
import bp_authoring_durable_canary_live_command_execution_release_contract as execution_release  # noqa: E402


def build_current_dispatch_release_summary() -> dict:
    return {
        "schema": dispatch_release.CANARY_LIVE_COMMAND_DISPATCH_RELEASE_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_live_command_dispatch_release_count": 1,
        "dispatch_release_contract_defined_count": 1,
        "start_contract_ready_count": 1,
        "runner_plan_valid_count": 0,
        "start_record_valid_count": 0,
        "live_runner_started_count": 0,
        "dispatch_inputs_satisfied_count": 0,
        "dispatch_record_present_count": 0,
        "record_schema_matches_count": 0,
        "dispatch_scope_matches_count": 0,
        "explicit_dispatch_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "dispatch_release_record_valid_count": 0,
        "dispatch_release_record_rejected_count": 0,
        "unsafe_dispatch_release_record_count": 0,
        "missing_dispatch_prerequisite_count": 9,
        "live_command_dispatch_release_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_dispatch_release_count": 0,
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


def build_execution_record(**overrides: object) -> dict:
    record = {
        "schema": execution_release.CANARY_LIVE_COMMAND_EXECUTION_RELEASE_RECORD_SCHEMA,
        "execution_scope": execution_release.EXPECTED_EXECUTION_SCOPE,
        "explicit_live_command_execution_authorized": True,
        "operator_reconfirmed_no_save_delete_rename": True,
        "durable_authoring_authorized": False,
        "save_asset_authorized": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_dispatch_release_summary()
    contract = execution_release.build_canary_live_command_execution_release_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == execution_release.CANARY_LIVE_COMMAND_EXECUTION_RELEASE_SCHEMA
    assert contract["requested"] is True
    assert contract["execution_release_contract_defined"] is True
    assert contract["dispatch_release_contract_ready"] is True
    assert contract["dispatch_inputs_satisfied"] is False
    assert contract["dispatch_release_record_valid"] is False
    assert contract["execution_inputs_satisfied"] is False
    assert contract["execution_record_present"] is False
    assert contract["record_schema_matches"] is False
    assert contract["execution_scope_matches"] is False
    assert contract["explicit_execution_authorized"] is False
    assert contract["no_save_delete_rename_acknowledged"] is False
    assert contract["execution_release_record_valid"] is False
    assert contract["execution_release_record_rejected"] is False
    assert contract["unsafe_execution_release_record_count"] == 0
    assert contract["missing_execution_prerequisite_count"] == 8
    assert "section_78_dispatch_inputs_satisfied" in contract["missing_execution_prerequisites"]
    assert "section_78_dispatch_release_record_valid" in contract["missing_execution_prerequisites"]
    assert "live_command_execution_release_record_present" in contract["missing_execution_prerequisites"]
    assert "live_command_execution_release_record_schema" in contract["missing_execution_prerequisites"]
    assert "durable_canary_live_command_execution_only_scope" in contract["missing_execution_prerequisites"]
    assert "explicit_live_command_execution_authorization" in contract["missing_execution_prerequisites"]
    assert "operator_reconfirmed_no_save_delete_rename" in contract["missing_execution_prerequisites"]
    assert "separate_live_command_execution_evidence_admission" in contract["missing_execution_prerequisites"]
    assert contract["live_command_execution_release_allowed"] is False
    assert contract["live_command_dispatch_allowed"] is False
    assert contract["live_command_plan_emitted"] is False
    assert contract["live_command_execution_allowed"] is False
    assert contract["live_command_executed"] is False
    assert contract["durable_executor_may_open_after_execution_release"] is False

    summary = execution_release.summarize_canary_live_command_execution_releases([contract])
    assert summary == {
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

    future_summary = {
        **current_summary,
        "dispatch_inputs_satisfied_count": 1,
        "dispatch_release_record_valid_count": 1,
    }
    future_contract = execution_release.build_canary_live_command_execution_release_contract(
        True,
        future_summary,
        build_execution_record(),
    )
    assert future_contract["execution_release_record_valid"] is True
    assert future_contract["missing_execution_prerequisite_count"] == 1
    assert future_contract["missing_execution_prerequisites"] == [
        "separate_live_command_execution_evidence_admission"
    ]
    assert future_contract["live_command_execution_release_allowed"] is False
    assert future_contract["live_command_execution_allowed"] is False
    assert future_contract["live_command_executed"] is False
    assert future_contract["durable_executor_may_open_after_execution_release"] is False

    unsafe_contract = execution_release.build_canary_live_command_execution_release_contract(
        True,
        future_summary,
        build_execution_record(save_asset_authorized=True),
    )
    assert unsafe_contract["execution_release_record_valid"] is False
    assert unsafe_contract["execution_release_record_rejected"] is True
    assert unsafe_contract["unsafe_execution_release_record_count"] == 1
    unsafe_summary = execution_release.summarize_canary_live_command_execution_releases([unsafe_contract])
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["execution_release_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_execution_release_record_count"] == 1
    assert unsafe_summary["durable_executor_may_open_after_execution_release_count"] == 0

    print("BP authoring durable canary live command execution release contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
