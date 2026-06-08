#!/usr/bin/env python
"""Offline smoke tests for Sections 209-216 live pre-save checkpoint batch."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_live_pre_save_checkpoint_batch_contract as live_pre_save_checkpoint  # noqa: E402
import bp_authoring_durable_executor_authoring_save_gate_open_admission_batch_contract as save_gate_open_admission  # noqa: E402
from test_bp_authoring_durable_executor_authoring_save_gate_open_admission_batch_contract import build_current_section_193_200_summary  # noqa: E402


def build_current_section_201_208_summary() -> dict:
    section_193_200_summary = build_current_section_193_200_summary()
    contract = (
        save_gate_open_admission
        .build_durable_executor_authoring_save_gate_open_admission_batch_contract(
            True,
            section_193_200_summary,
        )
    )
    return (
        save_gate_open_admission
        .summarize_durable_executor_authoring_save_gate_open_admission_batches(
            [contract]
        )
    )


def build_current_live_result(**overrides: object) -> dict:
    result = (
        live_pre_save_checkpoint
        .build_live_pre_save_read_only_result(
            bridge_reachable=True,
            ieta_slate_status_succeeded=True,
        )
    )
    result.update(overrides)
    return result


def main() -> int:
    section_201_208_summary = build_current_section_201_208_summary()
    live_result = build_current_live_result()
    contract = (
        live_pre_save_checkpoint
        .build_durable_executor_authoring_live_pre_save_checkpoint_batch_contract(
            True,
            section_201_208_summary,
            live_result,
        )
    )
    assert (
        contract["schema"]
        == live_pre_save_checkpoint
        .DURABLE_EXECUTOR_AUTHORING_LIVE_PRE_SAVE_CHECKPOINT_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_201_208_summary_schema_matches"] is True
    assert contract["section_201_208_summary_passed"] is True
    assert contract["section_201_208_pre_save_ready"] is True
    assert contract["section_201_208_write_and_live_outputs_blocked"] is True
    assert contract["live_result_schema_matches"] is True
    assert contract["live_result_read_only"] is True
    assert contract["live_bridge_reachable"] is True
    assert contract["ieta_slate_status_succeeded"] is True
    assert contract["target_path_matches"] is True
    assert contract["read_only_target_check_performed"] is True
    assert contract["target_absent_for_new_temp_asset"] is True
    assert contract["target_directory_absent_or_empty"] is True
    assert contract["dirty_content_packages_zero"] is True
    assert contract["dirty_map_packages_zero"] is True
    assert contract["live_result_write_outputs_blocked"] is True
    assert contract["save_dispatch_final_checkpoint_ready"] is True
    assert contract["actual_save_execution_requires_final_user_checkpoint"] is True
    assert contract["section_209_live_bridge_recovered"] is True
    assert contract["section_210_live_pre_save_read_only_target_checked"] is True
    assert contract["section_211_live_target_absence_confirmed"] is True
    assert contract["section_212_live_dirty_package_boundary_clean"] is True
    assert (
        contract["section_213_live_overwrite_boundary_safe_for_new_temp_asset"]
        is True
    )
    assert contract["section_214_live_save_dispatch_final_checkpoint_ready"] is True
    assert contract["section_215_live_save_execution_readback_plan_ready"] is True
    assert contract["section_216_actual_save_requires_final_user_checkpoint"] is True
    assert contract["save_gate_open_allowed"] is True
    assert contract["save_command_admitted"] is True
    assert contract["final_pre_save_execution_ready"] is True
    assert contract["durable_authoring_allowed"] is False
    assert contract["final_durable_release_ready"] is False
    assert contract["asset_write_performed"] is False
    assert contract["package_dirty_marked"] is False
    assert contract["save_command_dispatched"] is False
    assert contract["save_command_executed"] is False
    assert contract["save_true_allowed"] is False
    assert contract["save_asset_allowed"] is False
    assert contract["compile_save_allowed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["live_command_dispatched"] is False
    assert contract["live_command_executed"] is False

    summary = (
        live_pre_save_checkpoint
        .summarize_durable_executor_authoring_live_pre_save_checkpoint_batches(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_live_pre_save_checkpoint_batch_count"
        ]
        == 1
    )
    assert summary["section_209_live_bridge_recovered_count"] == 1
    assert summary["section_210_live_pre_save_read_only_target_checked_count"] == 1
    assert summary["section_211_live_target_absence_confirmed_count"] == 1
    assert summary["section_212_live_dirty_package_boundary_clean_count"] == 1
    assert (
        summary[
            "section_213_live_overwrite_boundary_safe_for_new_temp_asset_count"
        ]
        == 1
    )
    assert summary["section_214_live_save_dispatch_final_checkpoint_ready_count"] == 1
    assert summary["section_215_live_save_execution_readback_plan_ready_count"] == 1
    assert (
        summary["section_216_actual_save_requires_final_user_checkpoint_count"]
        == 1
    )
    assert summary["live_bridge_reachable_count"] == 1
    assert summary["ieta_slate_status_succeeded_count"] == 1
    assert summary["read_only_target_check_performed_count"] == 1
    assert summary["target_absent_for_new_temp_asset_count"] == 1
    assert summary["target_directory_absent_or_empty_count"] == 1
    assert summary["dirty_content_packages_zero_count"] == 1
    assert summary["dirty_map_packages_zero_count"] == 1
    assert summary["save_dispatch_final_checkpoint_ready_count"] == 1
    assert summary["actual_save_execution_requires_final_user_checkpoint_count"] == 1
    assert summary["save_gate_open_allowed_count"] == 1
    assert summary["save_command_admitted_count"] == 1
    assert summary["final_pre_save_execution_ready_count"] == 1
    assert summary["durable_authoring_allowed_count"] == 0
    assert summary["final_durable_release_ready_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["package_dirty_marked_count"] == 0
    assert summary["save_command_dispatched_count"] == 0
    assert summary["save_command_executed_count"] == 0
    assert summary["save_true_allowed_count"] == 0
    assert summary["save_asset_allowed_count"] == 0
    assert summary["compile_save_allowed_count"] == 0
    assert summary["delete_asset_allowed_count"] == 0
    assert summary["rename_asset_allowed_count"] == 0
    assert summary["live_command_dispatched_count"] == 0
    assert summary["live_command_executed_count"] == 0

    bridge_down_contract = (
        live_pre_save_checkpoint
        .build_durable_executor_authoring_live_pre_save_checkpoint_batch_contract(
            True,
            section_201_208_summary,
            build_current_live_result(bridge_reachable=False),
        )
    )
    bridge_down_result = (
        live_pre_save_checkpoint
        .summarize_durable_executor_authoring_live_pre_save_checkpoint_batches(
            [bridge_down_contract]
        )
    )
    assert bridge_down_contract["live_bridge_reachable"] is False
    assert bridge_down_contract["save_dispatch_final_checkpoint_ready"] is False
    assert bridge_down_contract["save_command_dispatched"] is False
    assert bridge_down_result["status"] == "failed"

    existing_target_contract = (
        live_pre_save_checkpoint
        .build_durable_executor_authoring_live_pre_save_checkpoint_batch_contract(
            True,
            section_201_208_summary,
            build_current_live_result(asset_exists=True),
        )
    )
    existing_target_result = (
        live_pre_save_checkpoint
        .summarize_durable_executor_authoring_live_pre_save_checkpoint_batches(
            [existing_target_contract]
        )
    )
    assert existing_target_contract["target_absent_for_new_temp_asset"] is False
    assert existing_target_contract["save_dispatch_final_checkpoint_ready"] is False
    assert existing_target_contract["save_asset_allowed"] is False
    assert existing_target_result["status"] == "failed"

    dirty_contract = (
        live_pre_save_checkpoint
        .build_durable_executor_authoring_live_pre_save_checkpoint_batch_contract(
            True,
            section_201_208_summary,
            build_current_live_result(dirty_content_package_count=1),
        )
    )
    dirty_result = (
        live_pre_save_checkpoint
        .summarize_durable_executor_authoring_live_pre_save_checkpoint_batches(
            [dirty_contract]
        )
    )
    assert dirty_contract["dirty_content_packages_zero"] is False
    assert dirty_contract["save_dispatch_final_checkpoint_ready"] is False
    assert dirty_contract["asset_write_performed"] is False
    assert dirty_result["status"] == "failed"

    print(
        "BP authoring durable executor authoring live pre-save checkpoint batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
