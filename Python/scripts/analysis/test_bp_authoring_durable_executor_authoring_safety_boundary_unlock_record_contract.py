#!/usr/bin/env python
"""Offline smoke tests for Section 183 safety boundary unlock record contract."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_safety_boundary_unlock_decision_contract as unlock_decision  # noqa: E402
import bp_authoring_durable_executor_authoring_safety_boundary_unlock_record_contract as unlock_record  # noqa: E402
from test_bp_authoring_durable_executor_authoring_safety_boundary_unlock_decision_contract import build_current_section_181_summary  # noqa: E402


def build_current_section_182_summary() -> dict:
    section_181_summary = build_current_section_181_summary()
    contract = (
        unlock_decision
        .build_durable_executor_authoring_safety_boundary_unlock_decision_contract(
            True,
            section_181_summary,
            None,
        )
    )
    return (
        unlock_decision
        .summarize_durable_executor_authoring_safety_boundary_unlock_decisions(
            [contract]
        )
    )


def build_passed_read_only_live_preflight_summary() -> dict:
    return {
        "schema": unlock_record.DURABLE_LIVE_PREFLIGHT_SCHEMA,
        "status": "passed",
        "live_requested": True,
        "durable_preflight_requested_manifest_count": 1,
        "read_only_live_preflight_allowed_count": 1,
        "live_result_count": 1,
        "passed_read_only_result_count": 1,
        "authoring_attempted_count": 0,
        "save_or_delete_attempted_count": 0,
        "preflight_pass_count": 0,
        "durable_authoring_allowed": False,
        "save_or_delete_allowed": False,
        "missing_live_result_manifest_ids": [],
        "unexpected_live_result_manifest_ids": [],
        "read_only_only": True,
    }


def main() -> int:
    section_182_summary = build_current_section_182_summary()
    live_preflight_summary = build_passed_read_only_live_preflight_summary()
    approval_record = unlock_record.build_explicit_unlock_approval_record()
    contract = (
        unlock_record
        .build_durable_executor_authoring_safety_boundary_unlock_record_contract(
            True,
            section_182_summary,
            live_preflight_summary,
            approval_record,
        )
    )
    assert (
        contract["schema"]
        == unlock_record.DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_RECORD_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_182_summary_schema_matches"] is True
    assert contract["section_182_summary_passed"] is True
    assert contract["section_182_checkpoint_reached"] is True
    assert contract["section_182_unlock_record_absent"] is True
    assert contract["section_182_unlock_record_not_admissible"] is True
    assert contract["section_182_authoring_disabled"] is True
    assert contract["section_182_final_release_not_ready"] is True
    assert contract["section_182_unlocked_absent"] is True
    assert contract["blocked_outputs_zero"] is True
    assert contract["approval_record_present"] is True
    assert contract["approval_record_schema_matches"] is True
    assert contract["approval_scope_matches"] is True
    assert contract["approval_operation_matches"] is True
    assert contract["explicit_unlock_approval_present"] is True
    assert contract["approval_requires_read_only_live_preflight"] is True
    assert contract["approval_blocks_save_delete_rename"] is True
    assert contract["approval_blocks_live_writes"] is True
    assert contract["live_preflight_schema_matches"] is True
    assert contract["live_preflight_passed"] is True
    assert contract["live_preflight_requested"] is True
    assert contract["live_preflight_result_present"] is True
    assert contract["live_preflight_read_only_result_passed"] is True
    assert contract["live_preflight_read_only_only"] is True
    assert contract["live_preflight_no_authoring_attempted"] is True
    assert contract["live_preflight_no_save_delete_attempted"] is True
    assert contract["live_preflight_does_not_pass_write_gate"] is True
    assert contract["unlock_record_admissible"] is True
    assert contract["durable_safety_boundary_unlock_ready"] is True
    assert contract["durable_safety_boundary_unlocked"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["final_durable_release_ready"] is False
    assert contract["save_delete_rename_allowed"] is False
    assert contract["live_durable_authoring_allowed"] is False
    assert contract["durable_authoring_command_allowed_count"] == 0
    assert contract["save_delete_rename_allowed_count"] == 0
    assert contract["live_command_dispatched_count"] == 0

    summary = (
        unlock_record
        .summarize_durable_executor_authoring_safety_boundary_unlock_records(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_safety_boundary_unlock_record_count"
        ]
        == 1
    )
    assert summary["unlock_record_admissible_count"] == 1
    assert summary["durable_safety_boundary_unlock_ready_count"] == 1
    assert summary["durable_safety_boundary_unlocked_count"] == 0
    assert summary["durable_authoring_enabled_count"] == 0
    assert summary["final_durable_release_ready_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0
    assert summary["live_durable_authoring_allowed_count"] == 0

    missing_approval_contract = (
        unlock_record
        .build_durable_executor_authoring_safety_boundary_unlock_record_contract(
            True,
            section_182_summary,
            live_preflight_summary,
            None,
        )
    )
    missing_approval_summary = (
        unlock_record
        .summarize_durable_executor_authoring_safety_boundary_unlock_records(
            [missing_approval_contract]
        )
    )
    assert missing_approval_contract["approval_record_present"] is False
    assert missing_approval_contract["unlock_record_admissible"] is False
    assert missing_approval_contract["durable_safety_boundary_unlock_ready"] is False
    assert missing_approval_summary["status"] == "failed"

    write_attempt_summary = dict(live_preflight_summary)
    write_attempt_summary["authoring_attempted_count"] = 1
    write_attempt_contract = (
        unlock_record
        .build_durable_executor_authoring_safety_boundary_unlock_record_contract(
            True,
            section_182_summary,
            write_attempt_summary,
            approval_record,
        )
    )
    write_attempt_summary_result = (
        unlock_record
        .summarize_durable_executor_authoring_safety_boundary_unlock_records(
            [write_attempt_contract]
        )
    )
    assert write_attempt_contract["live_preflight_no_authoring_attempted"] is False
    assert write_attempt_contract["unlock_record_admissible"] is False
    assert write_attempt_summary_result["status"] == "failed"

    print(
        "BP authoring durable executor authoring safety boundary unlock record contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
