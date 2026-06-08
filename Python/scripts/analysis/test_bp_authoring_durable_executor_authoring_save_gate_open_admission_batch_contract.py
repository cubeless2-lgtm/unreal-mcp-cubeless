#!/usr/bin/env python
"""Offline smoke tests for Sections 201-208 save-gate open/admission batch."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_save_gate_open_admission_batch_contract as save_gate_open_admission  # noqa: E402
import bp_authoring_durable_executor_authoring_save_gate_preflight_batch_contract as save_gate_preflight  # noqa: E402
from test_bp_authoring_durable_executor_authoring_save_gate_preflight_batch_contract import build_current_section_186_192_summary  # noqa: E402


def build_current_section_193_200_summary() -> dict:
    section_186_192_summary = build_current_section_186_192_summary()
    contract = (
        save_gate_preflight
        .build_durable_executor_authoring_save_gate_preflight_batch_contract(
            True,
            section_186_192_summary,
        )
    )
    return (
        save_gate_preflight
        .summarize_durable_executor_authoring_save_gate_preflight_batches(
            [contract]
        )
    )


def main() -> int:
    section_193_200_summary = build_current_section_193_200_summary()
    contract = (
        save_gate_open_admission
        .build_durable_executor_authoring_save_gate_open_admission_batch_contract(
            True,
            section_193_200_summary,
        )
    )
    assert (
        contract["schema"]
        == save_gate_open_admission
        .DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_OPEN_ADMISSION_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_193_200_summary_schema_matches"] is True
    assert contract["section_193_200_summary_passed"] is True
    assert contract["section_193_200_save_gate_preflight_ready"] is True
    assert contract["section_193_200_save_gate_still_closed"] is True
    assert contract["section_193_200_write_and_live_outputs_blocked"] is True
    assert contract["explicit_save_gate_open_approved"] is True
    assert contract["save_gate_open_allowed"] is True
    assert contract["save_gate_opened"] is True
    assert contract["save_command_admission_contract_started"] is True
    assert contract["save_command_admission_contract_accepted"] is True
    assert contract["save_command_admitted"] is True
    assert contract["save_command_dry_run_allowed"] is True
    assert contract["save_command_dispatch_dry_run_ready"] is True
    assert contract["save_command_execution_dry_run_ready"] is True
    assert contract["save_command_result_readback_dry_run_ready"] is True
    assert contract["final_pre_save_execution_ready"] is True
    assert contract["section_201_explicit_save_gate_open_approved"] is True
    assert contract["section_202_save_gate_opened"] is True
    assert contract["section_203_save_command_admission_contract_accepted"] is True
    assert contract["section_204_save_command_admitted"] is True
    assert contract["section_205_save_command_dispatch_dry_run_ready"] is True
    assert contract["section_206_save_command_execution_dry_run_ready"] is True
    assert contract["section_207_save_command_result_readback_dry_run_ready"] is True
    assert contract["section_208_final_pre_save_execution_ready"] is True
    assert contract["durable_authoring_enabled"] is True
    assert contract["durable_executor_opened"] is True
    assert contract["durable_authoring_command_no_save_execution_ready"] is True
    assert contract["final_no_save_release_ready"] is True
    assert contract["durable_authoring_save_gate_preflight_ready"] is True
    assert contract["save_command_admission_preflight_ready"] is True
    assert contract["durable_authoring_allowed"] is False
    assert contract["final_durable_release_ready"] is False
    assert contract["asset_write_performed"] is False
    assert contract["package_dirty_marked"] is False
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
        save_gate_open_admission
        .summarize_durable_executor_authoring_save_gate_open_admission_batches(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_save_gate_open_admission_batch_count"
        ]
        == 1
    )
    assert summary["section_201_explicit_save_gate_open_approved_count"] == 1
    assert summary["section_202_save_gate_opened_count"] == 1
    assert (
        summary["section_203_save_command_admission_contract_accepted_count"]
        == 1
    )
    assert summary["section_204_save_command_admitted_count"] == 1
    assert summary["section_205_save_command_dispatch_dry_run_ready_count"] == 1
    assert summary["section_206_save_command_execution_dry_run_ready_count"] == 1
    assert (
        summary["section_207_save_command_result_readback_dry_run_ready_count"]
        == 1
    )
    assert summary["section_208_final_pre_save_execution_ready_count"] == 1
    assert summary["explicit_save_gate_open_approved_count"] == 1
    assert summary["save_gate_open_allowed_count"] == 1
    assert summary["save_gate_opened_count"] == 1
    assert summary["save_command_admission_contract_started_count"] == 1
    assert summary["save_command_admission_contract_accepted_count"] == 1
    assert summary["save_command_admitted_count"] == 1
    assert summary["save_command_dry_run_allowed_count"] == 1
    assert summary["save_command_dispatch_dry_run_ready_count"] == 1
    assert summary["save_command_execution_dry_run_ready_count"] == 1
    assert summary["save_command_result_readback_dry_run_ready_count"] == 1
    assert summary["final_pre_save_execution_ready_count"] == 1
    assert summary["durable_authoring_enabled_count"] == 1
    assert summary["durable_executor_opened_count"] == 1
    assert summary["durable_authoring_save_gate_preflight_ready_count"] == 1
    assert summary["save_command_admission_preflight_ready_count"] == 1
    assert summary["durable_authoring_allowed_count"] == 0
    assert summary["final_durable_release_ready_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["package_dirty_marked_count"] == 0
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

    missing_preflight_summary = dict(section_193_200_summary)
    missing_preflight_summary["save_gate_preflight_ready_count"] = 0
    missing_preflight_contract = (
        save_gate_open_admission
        .build_durable_executor_authoring_save_gate_open_admission_batch_contract(
            True,
            missing_preflight_summary,
        )
    )
    missing_preflight_result = (
        save_gate_open_admission
        .summarize_durable_executor_authoring_save_gate_open_admission_batches(
            [missing_preflight_contract]
        )
    )
    assert missing_preflight_contract["section_193_200_save_gate_preflight_ready"] is False
    assert missing_preflight_contract["save_gate_open_allowed"] is False
    assert missing_preflight_contract["save_command_admitted"] is False
    assert missing_preflight_contract["save_asset_allowed"] is False
    assert missing_preflight_result["status"] == "failed"

    already_open_summary = dict(section_193_200_summary)
    already_open_summary["save_gate_open_allowed_count"] = 1
    already_open_contract = (
        save_gate_open_admission
        .build_durable_executor_authoring_save_gate_open_admission_batch_contract(
            True,
            already_open_summary,
        )
    )
    already_open_result = (
        save_gate_open_admission
        .summarize_durable_executor_authoring_save_gate_open_admission_batches(
            [already_open_contract]
        )
    )
    assert already_open_contract["section_193_200_save_gate_still_closed"] is False
    assert already_open_contract["save_gate_open_allowed"] is False
    assert already_open_contract["save_command_admitted"] is False
    assert already_open_result["status"] == "failed"

    save_allowed_summary = dict(section_193_200_summary)
    save_allowed_summary["save_asset_allowed_count"] = 1
    save_allowed_contract = (
        save_gate_open_admission
        .build_durable_executor_authoring_save_gate_open_admission_batch_contract(
            True,
            save_allowed_summary,
        )
    )
    save_allowed_result = (
        save_gate_open_admission
        .summarize_durable_executor_authoring_save_gate_open_admission_batches(
            [save_allowed_contract]
        )
    )
    assert save_allowed_contract["section_193_200_save_gate_still_closed"] is False
    assert save_allowed_contract["section_193_200_write_and_live_outputs_blocked"] is False
    assert save_allowed_contract["save_gate_open_allowed"] is False
    assert save_allowed_contract["save_command_admitted"] is False
    assert save_allowed_contract["save_asset_allowed"] is False
    assert save_allowed_result["status"] == "failed"

    print(
        "BP authoring durable executor authoring save-gate open/admission batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
