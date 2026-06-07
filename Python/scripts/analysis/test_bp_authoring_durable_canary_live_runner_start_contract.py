#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_live_runner_start_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_live_runner_envelope_contract as runner_envelope  # noqa: E402
import bp_authoring_durable_canary_live_runner_start_contract as runner_start  # noqa: E402


def build_current_runner_envelope_summary() -> dict:
    return {
        "schema": runner_envelope.CANARY_LIVE_RUNNER_ENVELOPE_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_live_runner_envelope_count": 1,
        "live_runner_envelope_defined_count": 1,
        "execution_release_contract_ready_count": 1,
        "execution_release_valid_count": 0,
        "live_runner_release_allowed_count": 0,
        "runner_plan_present_count": 0,
        "runner_plan_schema_matches_count": 0,
        "planned_command_count": 0,
        "forbidden_runner_command_count": 0,
        "unknown_runner_command_count": 0,
        "runner_plan_valid_count": 0,
        "runner_plan_rejected_count": 0,
        "missing_runner_prerequisite_count": 6,
        "live_runner_may_start_count": 0,
        "live_runner_started_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_runner_count": 0,
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


def build_start_record(**overrides: object) -> dict:
    record = {
        "schema": runner_start.CANARY_LIVE_RUNNER_START_RECORD_SCHEMA,
        "start_scope": runner_start.EXPECTED_START_SCOPE,
        "explicit_operator_live_runner_start_authorized": True,
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
    current_summary = build_current_runner_envelope_summary()
    contract = runner_start.build_canary_live_runner_start_contract(True, current_summary)
    assert contract["schema"] == runner_start.CANARY_LIVE_RUNNER_START_SCHEMA
    assert contract["requested"] is True
    assert contract["start_contract_defined"] is True
    assert contract["runner_envelope_ready"] is True
    assert contract["runner_plan_valid"] is False
    assert contract["runner_start_allowed_by_envelope"] is False
    assert contract["start_record_present"] is False
    assert contract["record_schema_matches"] is False
    assert contract["start_scope_matches"] is False
    assert contract["explicit_operator_start_authorized"] is False
    assert contract["no_save_delete_rename_acknowledged"] is False
    assert contract["start_record_valid"] is False
    assert contract["start_record_rejected"] is False
    assert contract["unsafe_start_record_count"] == 0
    assert contract["missing_start_prerequisite_count"] == 8
    assert "section_76_runner_plan_valid" in contract["missing_start_prerequisites"]
    assert "section_76_live_runner_may_start" in contract["missing_start_prerequisites"]
    assert "operator_live_runner_start_record_present" in contract["missing_start_prerequisites"]
    assert "operator_live_runner_start_record_schema" in contract["missing_start_prerequisites"]
    assert "durable_canary_live_runner_only_start_scope" in contract["missing_start_prerequisites"]
    assert "explicit_operator_live_runner_start_authorization" in contract["missing_start_prerequisites"]
    assert "operator_reconfirmed_no_save_delete_rename" in contract["missing_start_prerequisites"]
    assert "separate_live_command_dispatch_release" in contract["missing_start_prerequisites"]
    assert contract["live_runner_start_allowed"] is False
    assert contract["live_runner_started"] is False
    assert contract["live_command_dispatch_allowed"] is False
    assert contract["live_command_plan_emitted"] is False
    assert contract["durable_executor_may_open_after_runner_start"] is False

    summary = runner_start.summarize_canary_live_runner_starts([contract])
    assert summary == {
        "schema": runner_start.CANARY_LIVE_RUNNER_START_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_live_runner_start_count": 1,
        "start_contract_defined_count": 1,
        "runner_envelope_ready_count": 1,
        "runner_plan_valid_count": 0,
        "runner_start_allowed_by_envelope_count": 0,
        "start_record_present_count": 0,
        "record_schema_matches_count": 0,
        "start_scope_matches_count": 0,
        "explicit_operator_start_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "start_record_valid_count": 0,
        "start_record_rejected_count": 0,
        "unsafe_start_record_count": 0,
        "missing_start_prerequisite_count": 8,
        "live_runner_start_allowed_count": 0,
        "live_runner_started_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_runner_start_count": 0,
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
        "runner_plan_valid_count": 1,
        "live_runner_may_start_count": 1,
    }
    future_contract = runner_start.build_canary_live_runner_start_contract(
        True,
        future_summary,
        build_start_record(),
    )
    assert future_contract["start_record_valid"] is True
    assert future_contract["missing_start_prerequisite_count"] == 1
    assert future_contract["missing_start_prerequisites"] == ["separate_live_command_dispatch_release"]
    assert future_contract["live_runner_start_allowed"] is False
    assert future_contract["live_command_dispatch_allowed"] is False
    assert future_contract["durable_executor_may_open_after_runner_start"] is False

    unsafe_contract = runner_start.build_canary_live_runner_start_contract(
        True,
        future_summary,
        build_start_record(delete_asset_authorized=True),
    )
    assert unsafe_contract["start_record_valid"] is False
    assert unsafe_contract["start_record_rejected"] is True
    assert unsafe_contract["unsafe_start_record_count"] == 1
    unsafe_summary = runner_start.summarize_canary_live_runner_starts([unsafe_contract])
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["start_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_start_record_count"] == 1
    assert unsafe_summary["durable_executor_may_open_after_runner_start_count"] == 0

    print("BP authoring durable canary live runner start contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
