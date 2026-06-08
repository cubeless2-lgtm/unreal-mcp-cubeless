#!/usr/bin/env python
"""Offline smoke tests for Section 185 durable authoring enable contract."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_enable_after_safety_boundary_unlock_contract as enable_after_unlock  # noqa: E402
import bp_authoring_durable_executor_authoring_safety_boundary_unlock_contract as unlock  # noqa: E402
from test_bp_authoring_durable_executor_authoring_safety_boundary_unlock_contract import build_current_section_183_summary  # noqa: E402


def build_current_section_184_summary() -> dict:
    section_183_summary = build_current_section_183_summary()
    contract = unlock.build_durable_executor_authoring_safety_boundary_unlock_contract(
        True,
        section_183_summary,
    )
    return unlock.summarize_durable_executor_authoring_safety_boundary_unlocks(
        [contract]
    )


def main() -> int:
    section_184_summary = build_current_section_184_summary()
    contract = (
        enable_after_unlock
        .build_durable_executor_authoring_enable_after_safety_boundary_unlock_contract(
            True,
            section_184_summary,
        )
    )
    assert (
        contract["schema"]
        == enable_after_unlock.DURABLE_EXECUTOR_AUTHORING_ENABLE_AFTER_SAFETY_BOUNDARY_UNLOCK_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_184_summary_schema_matches"] is True
    assert contract["section_184_summary_passed"] is True
    assert contract["section_184_safety_boundary_unlocked"] is True
    assert contract["section_184_authoring_disabled"] is True
    assert contract["section_184_final_release_not_ready"] is True
    assert contract["section_184_executor_open_blocked"] is True
    assert contract["section_184_authoring_command_blocked"] is True
    assert contract["section_184_save_delete_rename_blocked"] is True
    assert contract["section_184_live_durable_authoring_blocked"] is True
    assert contract["blocked_outputs_zero"] is True
    assert contract["durable_authoring_enable_admissible"] is True
    assert contract["durable_authoring_enabled"] is True
    assert contract["final_durable_release_ready"] is False
    assert contract["durable_executor_open_allowed"] is False
    assert contract["durable_authoring_command_allowed"] is False
    assert contract["save_delete_rename_allowed"] is False
    assert contract["live_durable_authoring_allowed"] is False
    assert contract["durable_authoring_command_allowed_count"] == 0
    assert contract["save_delete_rename_allowed_count"] == 0
    assert contract["live_command_dispatched_count"] == 0

    summary = (
        enable_after_unlock
        .summarize_durable_executor_authoring_enable_after_safety_boundary_unlocks(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_enable_after_safety_boundary_unlock_count"
        ]
        == 1
    )
    assert summary["section_184_safety_boundary_unlocked_count"] == 1
    assert summary["durable_authoring_enable_admissible_count"] == 1
    assert summary["durable_authoring_enabled_count"] == 1
    assert summary["final_durable_release_ready_count"] == 0
    assert summary["durable_executor_open_allowed_count"] == 0
    assert summary["durable_authoring_command_allowed_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0
    assert summary["live_durable_authoring_allowed_count"] == 0

    locked_summary = dict(section_184_summary)
    locked_summary["durable_safety_boundary_unlocked_count"] = 0
    locked_contract = (
        enable_after_unlock
        .build_durable_executor_authoring_enable_after_safety_boundary_unlock_contract(
            True,
            locked_summary,
        )
    )
    locked_result = (
        enable_after_unlock
        .summarize_durable_executor_authoring_enable_after_safety_boundary_unlocks(
            [locked_contract]
        )
    )
    assert locked_contract["section_184_safety_boundary_unlocked"] is False
    assert locked_contract["durable_authoring_enabled"] is False
    assert locked_result["status"] == "failed"

    save_allowed_summary = dict(section_184_summary)
    save_allowed_summary["save_delete_rename_allowed_count"] = 1
    save_allowed_contract = (
        enable_after_unlock
        .build_durable_executor_authoring_enable_after_safety_boundary_unlock_contract(
            True,
            save_allowed_summary,
        )
    )
    save_allowed_result = (
        enable_after_unlock
        .summarize_durable_executor_authoring_enable_after_safety_boundary_unlocks(
            [save_allowed_contract]
        )
    )
    assert save_allowed_contract["section_184_save_delete_rename_blocked"] is False
    assert save_allowed_contract["durable_authoring_enabled"] is False
    assert save_allowed_result["status"] == "failed"

    print(
        "BP authoring durable executor authoring enable after safety boundary unlock contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
