#!/usr/bin/env python
"""Offline smoke tests for Sections 186-192 no-save execution batch contract."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_enable_after_safety_boundary_unlock_contract as enable_after_unlock  # noqa: E402
import bp_authoring_durable_executor_authoring_no_save_execution_batch_contract as no_save_batch  # noqa: E402
from test_bp_authoring_durable_executor_authoring_enable_after_safety_boundary_unlock_contract import build_current_section_184_summary  # noqa: E402


def build_current_section_185_summary() -> dict:
    section_184_summary = build_current_section_184_summary()
    contract = (
        enable_after_unlock
        .build_durable_executor_authoring_enable_after_safety_boundary_unlock_contract(
            True,
            section_184_summary,
        )
    )
    return (
        enable_after_unlock
        .summarize_durable_executor_authoring_enable_after_safety_boundary_unlocks(
            [contract]
        )
    )


def main() -> int:
    section_185_summary = build_current_section_185_summary()
    contract = (
        no_save_batch
        .build_durable_executor_authoring_no_save_execution_batch_contract(
            True,
            section_185_summary,
        )
    )
    assert (
        contract["schema"]
        == no_save_batch.DURABLE_EXECUTOR_AUTHORING_NO_SAVE_EXECUTION_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_185_summary_schema_matches"] is True
    assert contract["section_185_summary_passed"] is True
    assert contract["section_185_authoring_enabled"] is True
    assert contract["section_185_final_release_not_ready"] is True
    assert contract["section_185_executor_open_blocked"] is True
    assert contract["section_185_command_allow_blocked"] is True
    assert contract["section_185_save_delete_rename_blocked"] is True
    assert contract["section_185_live_durable_authoring_blocked"] is True
    assert contract["blocked_outputs_zero"] is True
    assert contract["no_save_execution_batch_admissible"] is True
    assert contract["section_186_executor_opened"] is True
    assert contract["section_187_open_readiness_consolidated"] is True
    assert contract["section_188_authoring_command_allowed"] is True
    assert contract["section_189_command_dispatch_gate_open"] is True
    assert contract["section_190_command_execution_evidence_gate_open"] is True
    assert contract["section_191_completion_readback_ready"] is True
    assert contract["section_192_final_no_save_release_ready"] is True
    assert contract["durable_executor_open_allowed"] is True
    assert contract["durable_executor_opened"] is True
    assert contract["durable_authoring_command_allowed"] is True
    assert contract["durable_authoring_command_dispatched"] is True
    assert contract["durable_authoring_command_executed"] is True
    assert contract["durable_authoring_command_completed"] is True
    assert contract["final_no_save_release_ready"] is True
    assert contract["durable_authoring_enabled"] is True
    assert contract["durable_authoring_allowed"] is False
    assert contract["final_durable_release_ready"] is False
    assert contract["asset_write_performed"] is False
    assert contract["package_dirty_marked"] is False
    assert contract["save_delete_rename_allowed"] is False
    assert contract["save_asset_allowed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["live_durable_authoring_allowed"] is False
    assert contract["live_command_dispatched"] is False
    assert contract["live_command_executed"] is False

    summary = (
        no_save_batch
        .summarize_durable_executor_authoring_no_save_execution_batches(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_no_save_execution_batch_count"
        ]
        == 1
    )
    assert summary["section_186_executor_opened_count"] == 1
    assert summary["section_187_open_readiness_consolidated_count"] == 1
    assert summary["section_188_authoring_command_allowed_count"] == 1
    assert summary["section_189_command_dispatch_gate_open_count"] == 1
    assert summary["section_190_command_execution_evidence_gate_open_count"] == 1
    assert summary["section_191_completion_readback_ready_count"] == 1
    assert summary["section_192_final_no_save_release_ready_count"] == 1
    assert summary["durable_executor_opened_count"] == 1
    assert summary["durable_authoring_command_allowed_count"] == 1
    assert summary["durable_authoring_command_dispatched_count"] == 1
    assert summary["durable_authoring_command_executed_count"] == 1
    assert summary["durable_authoring_command_completed_count"] == 1
    assert summary["final_no_save_release_ready_count"] == 1
    assert summary["durable_authoring_enabled_count"] == 1
    assert summary["durable_authoring_allowed_count"] == 0
    assert summary["final_durable_release_ready_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["package_dirty_marked_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0
    assert summary["save_asset_allowed_count"] == 0
    assert summary["delete_asset_allowed_count"] == 0
    assert summary["rename_asset_allowed_count"] == 0
    assert summary["live_durable_authoring_allowed_count"] == 0
    assert summary["live_command_dispatched_count"] == 0
    assert summary["live_command_executed_count"] == 0

    disabled_summary = dict(section_185_summary)
    disabled_summary["durable_authoring_enabled_count"] = 0
    disabled_contract = (
        no_save_batch
        .build_durable_executor_authoring_no_save_execution_batch_contract(
            True,
            disabled_summary,
        )
    )
    disabled_result = (
        no_save_batch
        .summarize_durable_executor_authoring_no_save_execution_batches(
            [disabled_contract]
        )
    )
    assert disabled_contract["section_185_authoring_enabled"] is False
    assert disabled_contract["no_save_execution_batch_admissible"] is False
    assert disabled_result["status"] == "failed"

    save_allowed_summary = dict(section_185_summary)
    save_allowed_summary["save_delete_rename_allowed_count"] = 1
    save_allowed_contract = (
        no_save_batch
        .build_durable_executor_authoring_no_save_execution_batch_contract(
            True,
            save_allowed_summary,
        )
    )
    save_allowed_result = (
        no_save_batch
        .summarize_durable_executor_authoring_no_save_execution_batches(
            [save_allowed_contract]
        )
    )
    assert save_allowed_contract["section_185_save_delete_rename_blocked"] is False
    assert save_allowed_contract["no_save_execution_batch_admissible"] is False
    assert save_allowed_result["status"] == "failed"

    print(
        "BP authoring durable executor authoring no-save execution batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
