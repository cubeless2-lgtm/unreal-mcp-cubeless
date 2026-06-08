#!/usr/bin/env python
"""Offline smoke tests for Section 182 safety boundary unlock decision contract."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_safety_boundary_unlock_decision_contract as unlock_decision  # noqa: E402
from test_bp_authoring_durable_executor_authoring_release_boundary_consolidation_contract import build_current_section_180_summary  # noqa: E402
import bp_authoring_durable_executor_authoring_release_boundary_consolidation_contract as consolidation  # noqa: E402


def build_current_section_181_summary() -> dict:
    section_180_summary = build_current_section_180_summary()
    contract = (
        consolidation.build_durable_executor_authoring_release_boundary_consolidation_contract(
            True,
            section_180_summary,
        )
    )
    return consolidation.summarize_durable_executor_authoring_release_boundary_consolidations(
        [contract]
    )


def main() -> int:
    section_181_summary = build_current_section_181_summary()
    contract = unlock_decision.build_durable_executor_authoring_safety_boundary_unlock_decision_contract(
        True,
        section_181_summary,
        None,
    )
    assert (
        contract["schema"]
        == unlock_decision.DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_DECISION_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_181_summary_schema_matches"] is True
    assert contract["section_181_summary_passed"] is True
    assert contract["section_181_release_boundary_consolidated"] is True
    assert contract["section_181_unlock_ready_absent"] is True
    assert contract["section_181_authoring_disabled"] is True
    assert contract["section_181_final_release_not_ready"] is True
    assert contract["blocked_outputs_zero"] is True
    assert contract["unlock_decision_record_present"] is False
    assert contract["unlock_decision_record_absent"] is True
    assert contract["explicit_unlock_approval_present"] is False
    assert contract["explicit_unlock_approval_absent"] is True
    assert contract["unlock_requires_explicit_user_approval"] is True
    assert contract["unlock_decision_checkpoint_only"] is True
    assert contract["unlock_decision_checkpoint_reached"] is True
    assert contract["unlock_record_admissible"] is False
    assert contract["durable_safety_boundary_unlock_ready"] is False
    assert contract["durable_safety_boundary_unlocked"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["final_durable_release_ready"] is False
    assert contract["save_delete_rename_allowed"] is False
    assert contract["live_durable_authoring_allowed"] is False
    assert contract["durable_authoring_command_allowed_count"] == 0
    assert contract["save_delete_rename_allowed_count"] == 0
    assert contract["live_command_dispatched_count"] == 0

    summary = unlock_decision.summarize_durable_executor_authoring_safety_boundary_unlock_decisions(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_safety_boundary_unlock_decision_count"
        ]
        == 1
    )
    assert summary["unlock_decision_checkpoint_only_count"] == 1
    assert summary["unlock_decision_checkpoint_reached_count"] == 1
    assert summary["unlock_decision_record_absent_count"] == 1
    assert summary["explicit_unlock_approval_absent_count"] == 1
    assert summary["unlock_requires_explicit_user_approval_count"] == 1
    assert summary["unlock_record_admissible_count"] == 0
    assert summary["durable_safety_boundary_unlock_ready_count"] == 0
    assert summary["durable_safety_boundary_unlocked_count"] == 0
    assert summary["durable_authoring_enabled_count"] == 0
    assert summary["final_durable_release_ready_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0
    assert summary["live_durable_authoring_allowed_count"] == 0

    approval_record = {
        "schema": unlock_decision.DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_DECISION_RECORD_SCHEMA,
        "explicit_durable_safety_boundary_unlock_approved": True,
    }
    approval_contract = unlock_decision.build_durable_executor_authoring_safety_boundary_unlock_decision_contract(
        True,
        section_181_summary,
        approval_record,
    )
    assert approval_contract["unlock_decision_record_present"] is True
    assert approval_contract["explicit_unlock_approval_present"] is True
    assert approval_contract["unlock_decision_checkpoint_only"] is False
    assert approval_contract["durable_safety_boundary_unlocked"] is False
    approval_summary = unlock_decision.summarize_durable_executor_authoring_safety_boundary_unlock_decisions(
        [approval_contract]
    )
    assert approval_summary["status"] == "failed"
    assert approval_summary["durable_safety_boundary_unlocked_count"] == 0

    print(
        "BP authoring durable executor authoring safety boundary unlock decision contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
