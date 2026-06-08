#!/usr/bin/env python
"""Offline smoke tests for Sections 217-224 live actual save execution batch."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_live_actual_save_execution_batch_contract as live_actual_save_execution  # noqa: E402
import bp_authoring_durable_executor_authoring_live_pre_save_checkpoint_batch_contract as live_pre_save_checkpoint  # noqa: E402
from test_bp_authoring_durable_executor_authoring_live_pre_save_checkpoint_batch_contract import build_current_section_201_208_summary  # noqa: E402


def build_current_section_209_216_summary() -> dict:
    section_201_208_summary = build_current_section_201_208_summary()
    live_result = live_pre_save_checkpoint.build_live_pre_save_read_only_result(
        bridge_reachable=True,
        ieta_slate_status_succeeded=True,
    )
    contract = (
        live_pre_save_checkpoint
        .build_durable_executor_authoring_live_pre_save_checkpoint_batch_contract(
            True,
            section_201_208_summary,
            live_result,
        )
    )
    return (
        live_pre_save_checkpoint
        .summarize_durable_executor_authoring_live_pre_save_checkpoint_batches(
            [contract]
        )
    )


def build_current_execution_result(**overrides: object) -> dict:
    result = live_actual_save_execution.build_live_actual_save_execution_result()
    result.update(overrides)
    return result


def build_current_readback_result(**overrides: object) -> dict:
    result = live_actual_save_execution.build_live_actual_save_readback_result()
    result.update(overrides)
    return result


def main() -> int:
    section_209_216_summary = build_current_section_209_216_summary()
    execution_result = build_current_execution_result()
    readback_result = build_current_readback_result()
    contract = (
        live_actual_save_execution
        .build_durable_executor_authoring_live_actual_save_execution_batch_contract(
            True,
            section_209_216_summary,
            execution_result,
            readback_result,
        )
    )
    assert (
        contract["schema"]
        == live_actual_save_execution
        .DURABLE_EXECUTOR_AUTHORING_LIVE_ACTUAL_SAVE_EXECUTION_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_209_216_summary_schema_matches"] is True
    assert contract["section_209_216_summary_passed"] is True
    assert contract["section_209_216_live_pre_save_checkpoint_ready"] is True
    assert contract["section_209_216_write_outputs_closed"] is True
    assert contract["execution_result_schema_matches"] is True
    assert contract["execution_target_path_matches"] is True
    assert contract["execution_target_directory_matches"] is True
    assert contract["execution_asset_loaded"] is True
    assert contract["execution_asset_class_is_blueprint"] is True
    assert contract["execution_blueprint_compile_succeeded"] is True
    assert contract["execution_save_asset_succeeded"] is True
    assert contract["execution_live_command_succeeded"] is True
    assert contract["execution_write_performed"] is True
    assert contract["execution_post_asset_exists"] is True
    assert contract["execution_package_file_exists"] is True
    assert contract["execution_dirty_packages_cleared"] is True
    assert contract["execution_delete_rename_blocked"] is True
    assert contract["execution_has_no_error"] is True
    assert contract["readback_result_schema_matches"] is True
    assert contract["readback_result_read_only"] is True
    assert contract["readback_target_path_matches"] is True
    assert contract["readback_target_directory_matches"] is True
    assert contract["readback_asset_confirmed"] is True
    assert contract["readback_package_file_confirmed"] is True
    assert contract["readback_dirty_packages_zero"] is True
    assert contract["readback_write_outputs_blocked"] is True
    assert contract["live_actual_save_execution_ready"] is True
    assert contract["actual_save_final_checkpoint_satisfied"] is True
    assert contract["section_217_actual_save_approval_consumed"] is True
    assert contract["section_218_live_save_command_dispatched"] is True
    assert contract["section_219_live_temp_blueprint_write_performed"] is True
    assert contract["section_220_live_blueprint_compile_save_succeeded"] is True
    assert contract["section_221_live_save_asset_result_confirmed"] is True
    assert contract["section_222_live_saved_asset_readback_confirmed"] is True
    assert contract["section_223_live_dirty_packages_cleared_after_save"] is True
    assert contract["section_224_final_durable_release_ready"] is True
    assert contract["durable_authoring_enabled"] is True
    assert contract["durable_executor_opened"] is True
    assert contract["durable_authoring_allowed"] is True
    assert contract["save_gate_open_allowed"] is True
    assert contract["save_gate_opened"] is True
    assert contract["save_command_admitted"] is True
    assert contract["final_pre_save_execution_ready"] is True
    assert contract["live_pre_save_checkpoint_ready"] is True
    assert contract["actual_save_execution_requires_final_user_checkpoint"] is False
    assert contract["save_command_dispatched"] is True
    assert contract["save_command_executed"] is True
    assert contract["save_true_allowed"] is True
    assert contract["save_asset_allowed"] is True
    assert contract["compile_save_allowed"] is True
    assert contract["asset_write_performed"] is True
    assert contract["package_dirty_marked"] is True
    assert contract["live_durable_authoring_allowed"] is True
    assert contract["live_command_dispatched"] is True
    assert contract["live_command_executed"] is True
    assert contract["final_durable_release_ready"] is True
    assert contract["save_delete_rename_allowed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False

    summary = (
        live_actual_save_execution
        .summarize_durable_executor_authoring_live_actual_save_execution_batches(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_live_actual_save_execution_batch_count"
        ]
        == 1
    )
    assert summary["section_209_216_live_pre_save_checkpoint_ready_count"] == 1
    assert summary["execution_save_asset_succeeded_count"] == 1
    assert summary["execution_dirty_packages_cleared_count"] == 1
    assert summary["readback_asset_confirmed_count"] == 1
    assert summary["readback_package_file_confirmed_count"] == 1
    assert summary["readback_dirty_packages_zero_count"] == 1
    assert summary["live_actual_save_execution_ready_count"] == 1
    assert summary["actual_save_final_checkpoint_satisfied_count"] == 1
    assert summary["section_217_actual_save_approval_consumed_count"] == 1
    assert summary["section_218_live_save_command_dispatched_count"] == 1
    assert summary["section_219_live_temp_blueprint_write_performed_count"] == 1
    assert summary["section_220_live_blueprint_compile_save_succeeded_count"] == 1
    assert summary["section_221_live_save_asset_result_confirmed_count"] == 1
    assert summary["section_222_live_saved_asset_readback_confirmed_count"] == 1
    assert summary["section_223_live_dirty_packages_cleared_after_save_count"] == 1
    assert summary["section_224_final_durable_release_ready_count"] == 1
    assert summary["save_command_dispatched_count"] == 1
    assert summary["save_command_executed_count"] == 1
    assert summary["save_true_allowed_count"] == 1
    assert summary["save_asset_allowed_count"] == 1
    assert summary["compile_save_allowed_count"] == 1
    assert summary["asset_write_performed_count"] == 1
    assert summary["package_dirty_marked_count"] == 1
    assert summary["final_durable_release_ready_count"] == 1
    assert summary["save_delete_rename_allowed_count"] == 0
    assert summary["delete_asset_allowed_count"] == 0
    assert summary["rename_asset_allowed_count"] == 0

    missing_checkpoint = dict(section_209_216_summary)
    missing_checkpoint["section_216_actual_save_requires_final_user_checkpoint_count"] = 0
    missing_checkpoint_contract = (
        live_actual_save_execution
        .build_durable_executor_authoring_live_actual_save_execution_batch_contract(
            True,
            missing_checkpoint,
            execution_result,
            readback_result,
        )
    )
    missing_checkpoint_summary = (
        live_actual_save_execution
        .summarize_durable_executor_authoring_live_actual_save_execution_batches(
            [missing_checkpoint_contract]
        )
    )
    assert missing_checkpoint_contract["section_209_216_live_pre_save_checkpoint_ready"] is False
    assert missing_checkpoint_contract["live_actual_save_execution_ready"] is False
    assert missing_checkpoint_contract["final_durable_release_ready"] is False
    assert missing_checkpoint_contract["save_asset_allowed"] is False
    assert missing_checkpoint_summary["status"] == "failed"

    failed_save_contract = (
        live_actual_save_execution
        .build_durable_executor_authoring_live_actual_save_execution_batch_contract(
            True,
            section_209_216_summary,
            build_current_execution_result(save_asset_result=False),
            readback_result,
        )
    )
    failed_save_summary = (
        live_actual_save_execution
        .summarize_durable_executor_authoring_live_actual_save_execution_batches(
            [failed_save_contract]
        )
    )
    assert failed_save_contract["execution_save_asset_succeeded"] is False
    assert failed_save_contract["live_actual_save_execution_ready"] is False
    assert failed_save_contract["final_durable_release_ready"] is False
    assert failed_save_contract["delete_asset_allowed"] is False
    assert failed_save_summary["status"] == "failed"

    dirty_readback_contract = (
        live_actual_save_execution
        .build_durable_executor_authoring_live_actual_save_execution_batch_contract(
            True,
            section_209_216_summary,
            execution_result,
            build_current_readback_result(dirty_content_package_count=1),
        )
    )
    dirty_readback_summary = (
        live_actual_save_execution
        .summarize_durable_executor_authoring_live_actual_save_execution_batches(
            [dirty_readback_contract]
        )
    )
    assert dirty_readback_contract["readback_dirty_packages_zero"] is False
    assert dirty_readback_contract["live_actual_save_execution_ready"] is False
    assert dirty_readback_contract["final_durable_release_ready"] is False
    assert dirty_readback_contract["rename_asset_allowed"] is False
    assert dirty_readback_summary["status"] == "failed"

    delete_attempt_contract = (
        live_actual_save_execution
        .build_durable_executor_authoring_live_actual_save_execution_batch_contract(
            True,
            section_209_216_summary,
            build_current_execution_result(delete_asset_called=True),
            readback_result,
        )
    )
    delete_attempt_summary = (
        live_actual_save_execution
        .summarize_durable_executor_authoring_live_actual_save_execution_batches(
            [delete_attempt_contract]
        )
    )
    assert delete_attempt_contract["execution_delete_rename_blocked"] is False
    assert delete_attempt_contract["live_actual_save_execution_ready"] is False
    assert delete_attempt_contract["delete_asset_allowed"] is False
    assert delete_attempt_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring live actual save execution batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
