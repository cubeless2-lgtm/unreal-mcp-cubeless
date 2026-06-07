#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_live_runner_envelope_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_live_runner_envelope_contract as runner_envelope  # noqa: E402
import bp_authoring_durable_canary_rehearsal_execution_release_contract as execution_release  # noqa: E402


def build_current_execution_release_summary() -> dict:
    return {
        "schema": execution_release.CANARY_REHEARSAL_EXECUTION_RELEASE_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_rehearsal_execution_release_count": 1,
        "execution_release_contract_defined_count": 1,
        "promotion_barrier_defined_count": 1,
        "promotion_inputs_satisfied_count": 0,
        "release_record_present_count": 0,
        "record_schema_matches_count": 0,
        "release_scope_matches_count": 0,
        "explicit_execution_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "release_record_valid_count": 0,
        "release_record_rejected_count": 0,
        "unsafe_release_record_count": 0,
        "missing_release_prerequisite_count": 7,
        "live_canary_rehearsal_release_allowed_count": 0,
        "live_canary_rehearsal_execution_allowed_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_execution_release_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_creation_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
    }


def build_runner_plan(*commands: str) -> dict:
    return {
        "schema": runner_envelope.CANARY_LIVE_RUNNER_PLAN_SCHEMA,
        "commands": list(commands),
    }


def main() -> int:
    current_summary = build_current_execution_release_summary()
    contract = runner_envelope.build_canary_live_runner_envelope_contract(True, current_summary)
    assert contract["schema"] == runner_envelope.CANARY_LIVE_RUNNER_ENVELOPE_SCHEMA
    assert contract["requested"] is True
    assert contract["live_runner_envelope_defined"] is True
    assert contract["execution_release_contract_ready"] is True
    assert contract["execution_release_valid"] is False
    assert contract["live_runner_release_allowed"] is False
    assert contract["runner_plan_present"] is False
    assert contract["runner_plan_schema_matches"] is False
    assert contract["planned_command_count"] == 0
    assert contract["forbidden_runner_command_count"] == 0
    assert contract["unknown_runner_command_count"] == 0
    assert contract["runner_plan_valid"] is False
    assert contract["runner_plan_rejected"] is False
    assert contract["missing_runner_prerequisite_count"] == 6
    assert "section_75_execution_release_record_valid" in contract["missing_runner_prerequisites"]
    assert "section_75_live_canary_rehearsal_release_allowed" in contract["missing_runner_prerequisites"]
    assert "live_runner_plan_present" in contract["missing_runner_prerequisites"]
    assert "live_runner_plan_schema" in contract["missing_runner_prerequisites"]
    assert "live_runner_commands_present" in contract["missing_runner_prerequisites"]
    assert "separate_operator_live_runner_start" in contract["missing_runner_prerequisites"]
    assert contract["live_runner_may_start"] is False
    assert contract["live_runner_started"] is False
    assert contract["live_command_plan_emitted"] is False
    assert contract["live_canary_rehearsal_performed"] is False
    assert contract["durable_executor_may_open_after_runner"] is False

    summary = runner_envelope.summarize_canary_live_runner_envelopes([contract])
    assert summary == {
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

    future_summary = {
        **current_summary,
        "release_record_valid_count": 1,
        "live_canary_rehearsal_release_allowed_count": 1,
    }
    future_contract = runner_envelope.build_canary_live_runner_envelope_contract(
        True,
        future_summary,
        build_runner_plan("create_canary_blueprint", "compile_canary_blueprint", "read_only_asset_exists_check"),
    )
    assert future_contract["runner_plan_valid"] is True
    assert future_contract["missing_runner_prerequisite_count"] == 1
    assert future_contract["missing_runner_prerequisites"] == ["separate_operator_live_runner_start"]
    assert future_contract["live_runner_may_start"] is False
    assert future_contract["live_command_plan_emitted"] is False
    assert future_contract["durable_executor_may_open_after_runner"] is False

    unsafe_contract = runner_envelope.build_canary_live_runner_envelope_contract(
        True,
        future_summary,
        build_runner_plan("create_canary_blueprint", "save_asset"),
    )
    assert unsafe_contract["runner_plan_valid"] is False
    assert unsafe_contract["runner_plan_rejected"] is True
    assert unsafe_contract["forbidden_runner_command_count"] == 1
    unsafe_summary = runner_envelope.summarize_canary_live_runner_envelopes([unsafe_contract])
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["runner_plan_rejected_count"] == 1
    assert unsafe_summary["forbidden_runner_command_count"] == 1
    assert unsafe_summary["durable_executor_may_open_after_runner_count"] == 0

    print("BP authoring durable canary live runner envelope contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
