#!/usr/bin/env python
"""Offline smoke tests for Section 184 safety boundary unlock contract."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_safety_boundary_unlock_contract as unlock  # noqa: E402
import bp_authoring_durable_executor_authoring_safety_boundary_unlock_record_contract as unlock_record  # noqa: E402
from test_bp_authoring_durable_executor_authoring_safety_boundary_unlock_record_contract import build_current_section_182_summary  # noqa: E402
from test_bp_authoring_durable_executor_authoring_safety_boundary_unlock_record_contract import build_passed_read_only_live_preflight_summary  # noqa: E402


def build_current_section_183_summary() -> dict:
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
    return (
        unlock_record
        .summarize_durable_executor_authoring_safety_boundary_unlock_records(
            [contract]
        )
    )


def main() -> int:
    section_183_summary = build_current_section_183_summary()
    contract = unlock.build_durable_executor_authoring_safety_boundary_unlock_contract(
        True,
        section_183_summary,
    )
    assert (
        contract["schema"]
        == unlock.DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_183_summary_schema_matches"] is True
    assert contract["section_183_summary_passed"] is True
    assert contract["section_183_unlock_record_admissible"] is True
    assert contract["section_183_unlock_ready"] is True
    assert contract["section_183_unlocked_absent"] is True
    assert contract["section_183_authoring_disabled"] is True
    assert contract["section_183_final_release_not_ready"] is True
    assert contract["section_183_save_delete_rename_blocked"] is True
    assert contract["section_183_live_durable_authoring_blocked"] is True
    assert contract["blocked_outputs_zero"] is True
    assert contract["durable_safety_boundary_unlocked"] is True
    assert contract["durable_authoring_enabled"] is False
    assert contract["final_durable_release_ready"] is False
    assert contract["durable_executor_open_allowed"] is False
    assert contract["durable_authoring_command_allowed"] is False
    assert contract["save_delete_rename_allowed"] is False
    assert contract["live_durable_authoring_allowed"] is False
    assert contract["durable_authoring_command_allowed_count"] == 0
    assert contract["save_delete_rename_allowed_count"] == 0
    assert contract["live_command_dispatched_count"] == 0

    summary = unlock.summarize_durable_executor_authoring_safety_boundary_unlocks(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_safety_boundary_unlock_count"
        ]
        == 1
    )
    assert summary["section_183_unlock_record_admissible_count"] == 1
    assert summary["section_183_unlock_ready_count"] == 1
    assert summary["durable_safety_boundary_unlocked_count"] == 1
    assert summary["durable_authoring_enabled_count"] == 0
    assert summary["final_durable_release_ready_count"] == 0
    assert summary["durable_executor_open_allowed_count"] == 0
    assert summary["durable_authoring_command_allowed_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0
    assert summary["live_durable_authoring_allowed_count"] == 0

    not_ready_summary = dict(section_183_summary)
    not_ready_summary["durable_safety_boundary_unlock_ready_count"] = 0
    not_ready_contract = (
        unlock.build_durable_executor_authoring_safety_boundary_unlock_contract(
            True,
            not_ready_summary,
        )
    )
    not_ready_result = (
        unlock.summarize_durable_executor_authoring_safety_boundary_unlocks(
            [not_ready_contract]
        )
    )
    assert not_ready_contract["section_183_unlock_ready"] is False
    assert not_ready_contract["durable_safety_boundary_unlocked"] is False
    assert not_ready_result["status"] == "failed"

    save_allowed_summary = dict(section_183_summary)
    save_allowed_summary["save_delete_rename_allowed_count"] = 1
    save_allowed_contract = (
        unlock.build_durable_executor_authoring_safety_boundary_unlock_contract(
            True,
            save_allowed_summary,
        )
    )
    save_allowed_result = (
        unlock.summarize_durable_executor_authoring_safety_boundary_unlocks(
            [save_allowed_contract]
        )
    )
    assert save_allowed_contract["section_183_save_delete_rename_blocked"] is False
    assert save_allowed_contract["durable_safety_boundary_unlocked"] is False
    assert save_allowed_result["status"] == "failed"

    print(
        "BP authoring durable executor authoring safety boundary unlock contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
