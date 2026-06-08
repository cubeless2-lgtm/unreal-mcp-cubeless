#!/usr/bin/env python
"""Offline smoke tests for Sections 193-200 save-gate preflight batch."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_enable_after_safety_boundary_unlock_contract as enable_after_unlock  # noqa: E402
import bp_authoring_durable_executor_authoring_no_save_execution_batch_contract as no_save_batch  # noqa: E402
import bp_authoring_durable_executor_authoring_save_gate_preflight_batch_contract as save_gate_preflight  # noqa: E402
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


def build_current_section_186_192_summary() -> dict:
    section_185_summary = build_current_section_185_summary()
    contract = (
        no_save_batch
        .build_durable_executor_authoring_no_save_execution_batch_contract(
            True,
            section_185_summary,
        )
    )
    return (
        no_save_batch
        .summarize_durable_executor_authoring_no_save_execution_batches(
            [contract]
        )
    )


def main() -> int:
    section_186_192_summary = build_current_section_186_192_summary()
    contract = (
        save_gate_preflight
        .build_durable_executor_authoring_save_gate_preflight_batch_contract(
            True,
            section_186_192_summary,
        )
    )
    assert (
        contract["schema"]
        == save_gate_preflight
        .DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_PREFLIGHT_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_186_192_summary_schema_matches"] is True
    assert contract["section_186_192_summary_passed"] is True
    assert contract["section_186_192_no_save_ready"] is True
    assert contract["section_186_192_write_outputs_blocked"] is True
    assert contract["save_target_declared"] is True
    assert contract["save_target_package_allowlisted"] is True
    assert contract["save_target_read_only_exists_check_ready"] is True
    assert contract["ownership_marker_revalidated"] is True
    assert contract["rollback_policy_revalidated"] is True
    assert contract["overwrite_rename_decision_ready"] is True
    assert contract["read_only_save_preflight_ready"] is True
    assert contract["save_command_admission_preflight_ready"] is True
    assert contract["save_gate_open_review_ready"] is True
    assert contract["save_gate_preflight_ready"] is True
    assert contract["section_193_save_target_declared"] is True
    assert contract["section_194_ownership_marker_revalidated"] is True
    assert contract["section_195_rollback_policy_revalidated"] is True
    assert contract["section_196_overwrite_rename_decision_ready"] is True
    assert contract["section_197_read_only_save_preflight_ready"] is True
    assert contract["section_198_save_command_admission_preflight_ready"] is True
    assert contract["section_199_save_gate_open_review_ready"] is True
    assert contract["section_200_final_save_gate_preflight_ready"] is True
    assert contract["durable_authoring_enabled"] is True
    assert contract["durable_executor_opened"] is True
    assert contract["durable_authoring_command_no_save_execution_ready"] is True
    assert contract["final_no_save_release_ready"] is True
    assert contract["durable_authoring_allowed"] is False
    assert contract["final_durable_release_ready"] is False
    assert contract["asset_write_performed"] is False
    assert contract["package_dirty_marked"] is False
    assert contract["save_gate_open_allowed"] is False
    assert contract["save_command_admitted"] is False
    assert contract["save_command_dispatched"] is False
    assert contract["save_command_executed"] is False
    assert contract["save_true_allowed"] is False
    assert contract["save_asset_allowed"] is False
    assert contract["compile_save_allowed"] is False
    assert contract["save_delete_rename_allowed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["live_durable_authoring_allowed"] is False
    assert contract["live_command_dispatched"] is False
    assert contract["live_command_executed"] is False

    summary = (
        save_gate_preflight
        .summarize_durable_executor_authoring_save_gate_preflight_batches(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_save_gate_preflight_batch_count"
        ]
        == 1
    )
    assert summary["section_193_save_target_declared_count"] == 1
    assert summary["section_194_ownership_marker_revalidated_count"] == 1
    assert summary["section_195_rollback_policy_revalidated_count"] == 1
    assert summary["section_196_overwrite_rename_decision_ready_count"] == 1
    assert summary["section_197_read_only_save_preflight_ready_count"] == 1
    assert (
        summary["section_198_save_command_admission_preflight_ready_count"]
        == 1
    )
    assert summary["section_199_save_gate_open_review_ready_count"] == 1
    assert summary["section_200_final_save_gate_preflight_ready_count"] == 1
    assert summary["save_gate_preflight_ready_count"] == 1
    assert summary["save_command_admission_preflight_ready_count"] == 1
    assert summary["durable_authoring_enabled_count"] == 1
    assert summary["durable_executor_opened_count"] == 1
    assert summary["final_no_save_release_ready_count"] == 1
    assert summary["durable_authoring_allowed_count"] == 0
    assert summary["final_durable_release_ready_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["package_dirty_marked_count"] == 0
    assert summary["save_gate_open_allowed_count"] == 0
    assert summary["save_command_admitted_count"] == 0
    assert summary["save_command_dispatched_count"] == 0
    assert summary["save_command_executed_count"] == 0
    assert summary["save_true_allowed_count"] == 0
    assert summary["save_asset_allowed_count"] == 0
    assert summary["compile_save_allowed_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0
    assert summary["delete_asset_allowed_count"] == 0
    assert summary["rename_asset_allowed_count"] == 0
    assert summary["live_durable_authoring_allowed_count"] == 0
    assert summary["live_command_dispatched_count"] == 0
    assert summary["live_command_executed_count"] == 0

    missing_no_save_summary = dict(section_186_192_summary)
    missing_no_save_summary["final_no_save_release_ready_count"] = 0
    missing_no_save_contract = (
        save_gate_preflight
        .build_durable_executor_authoring_save_gate_preflight_batch_contract(
            True,
            missing_no_save_summary,
        )
    )
    missing_no_save_result = (
        save_gate_preflight
        .summarize_durable_executor_authoring_save_gate_preflight_batches(
            [missing_no_save_contract]
        )
    )
    assert missing_no_save_contract["section_186_192_no_save_ready"] is False
    assert missing_no_save_contract["save_gate_preflight_ready"] is False
    assert missing_no_save_contract["save_asset_allowed"] is False
    assert missing_no_save_result["status"] == "failed"

    unallowlisted_contract = (
        save_gate_preflight
        .build_durable_executor_authoring_save_gate_preflight_batch_contract(
            True,
            section_186_192_summary,
            target_asset_path="/Game/Unsafe/BP_DurableSaveGatePrep",
        )
    )
    unallowlisted_result = (
        save_gate_preflight
        .summarize_durable_executor_authoring_save_gate_preflight_batches(
            [unallowlisted_contract]
        )
    )
    assert unallowlisted_contract["save_target_declared"] is True
    assert unallowlisted_contract["save_target_package_allowlisted"] is False
    assert unallowlisted_contract["save_gate_preflight_ready"] is False
    assert unallowlisted_contract["save_command_admitted"] is False
    assert unallowlisted_result["status"] == "failed"

    save_allowed_summary = dict(section_186_192_summary)
    save_allowed_summary["save_asset_allowed_count"] = 1
    save_allowed_contract = (
        save_gate_preflight
        .build_durable_executor_authoring_save_gate_preflight_batch_contract(
            True,
            save_allowed_summary,
        )
    )
    save_allowed_result = (
        save_gate_preflight
        .summarize_durable_executor_authoring_save_gate_preflight_batches(
            [save_allowed_contract]
        )
    )
    assert save_allowed_contract["section_186_192_write_outputs_blocked"] is False
    assert save_allowed_contract["save_gate_preflight_ready"] is False
    assert save_allowed_contract["save_asset_allowed"] is False
    assert save_allowed_result["status"] == "failed"

    print(
        "BP authoring durable executor authoring save-gate preflight batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
