#!/usr/bin/env python
"""Offline smoke tests for Sections 233-240 cleanup/delete dry-run batch."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_cleanup_delete_dry_run_batch_contract as cleanup_delete_dry_run  # noqa: E402
import bp_authoring_durable_executor_authoring_live_save_stability_batch_contract as live_save_stability  # noqa: E402
from test_bp_authoring_durable_executor_authoring_live_save_stability_batch_contract import build_current_section_217_224_summary  # noqa: E402


def build_current_section_225_232_summary() -> dict:
    section_217_224_summary = build_current_section_217_224_summary()
    stability_result = live_save_stability.build_live_save_stability_result(
        package_file_size_bytes=24133,
    )
    contract = (
        live_save_stability
        .build_durable_executor_authoring_live_save_stability_batch_contract(
            True,
            section_217_224_summary,
            stability_result,
        )
    )
    return (
        live_save_stability
        .summarize_durable_executor_authoring_live_save_stability_batches(
            [contract]
        )
    )


def build_current_cleanup_delete_result(**overrides: object) -> dict:
    result = cleanup_delete_dry_run.build_cleanup_delete_dry_run_result(
        package_file_size_bytes=24133,
    )
    result.update(overrides)
    return result


def main() -> int:
    section_225_232_summary = build_current_section_225_232_summary()
    cleanup_result = build_current_cleanup_delete_result()
    contract = (
        cleanup_delete_dry_run
        .build_durable_executor_authoring_cleanup_delete_dry_run_batch_contract(
            True,
            section_225_232_summary,
            cleanup_result,
        )
    )
    assert (
        contract["schema"]
        == cleanup_delete_dry_run
        .DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_DRY_RUN_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_225_232_summary_schema_matches"] is True
    assert contract["section_225_232_summary_passed"] is True
    assert contract["section_225_232_save_stability_ready"] is True
    assert contract["section_225_232_cleanup_delete_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["cleanup_target_scope_confirmed"] is True
    assert contract["saved_asset_pre_delete_readback_confirmed"] is True
    assert contract["cleanup_delete_dry_run_plan_accepted"] is True
    assert contract["delete_target_isolation_proved"] is True
    assert contract["dirty_package_no_delete_boundary_clean"] is True
    assert contract["delete_command_dispatch_dry_run_ready"] is True
    assert contract["delete_result_readback_dry_run_ready"] is True
    assert contract["dry_run_blocks_actual_delete_outputs"] is True
    assert contract["result_has_no_error"] is True
    assert contract["cleanup_delete_dry_run_ready"] is True
    assert contract["actual_delete_execution_requires_final_user_checkpoint"] is True
    assert contract["section_233_cleanup_target_scope_confirmed"] is True
    assert contract["section_234_saved_asset_pre_delete_readback_confirmed"] is True
    assert contract["section_235_cleanup_delete_dry_run_plan_accepted"] is True
    assert contract["section_236_delete_target_isolation_proved"] is True
    assert contract["section_237_dirty_package_no_delete_boundary_clean"] is True
    assert contract["section_238_delete_command_dispatch_dry_run_ready"] is True
    assert contract["section_239_delete_result_readback_dry_run_ready"] is True
    assert contract["section_240_actual_delete_requires_final_user_checkpoint"] is True
    assert contract["cleanup_delete_dry_run_allowed"] is True
    assert contract["cleanup_delete_dry_run_ready"] is True
    assert contract["cleanup_allowed"] is False
    assert contract["cleanup_executed"] is False
    assert contract["delete_command_dispatched"] is False
    assert contract["delete_command_executed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["production_path_write_allowed"] is False
    assert contract["production_path_write_executed"] is False

    summary = (
        cleanup_delete_dry_run
        .summarize_durable_executor_authoring_cleanup_delete_dry_run_batches(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_cleanup_delete_dry_run_batch_count"
        ]
        == 1
    )
    assert summary["section_225_232_save_stability_ready_count"] == 1
    assert summary["cleanup_target_scope_confirmed_count"] == 1
    assert summary["saved_asset_pre_delete_readback_confirmed_count"] == 1
    assert summary["cleanup_delete_dry_run_plan_accepted_count"] == 1
    assert summary["delete_target_isolation_proved_count"] == 1
    assert summary["dirty_package_no_delete_boundary_clean_count"] == 1
    assert summary["delete_command_dispatch_dry_run_ready_count"] == 1
    assert summary["delete_result_readback_dry_run_ready_count"] == 1
    assert summary["cleanup_delete_dry_run_ready_count"] == 1
    assert (
        summary[
            "actual_delete_execution_requires_final_user_checkpoint_count"
        ]
        == 1
    )
    assert summary["section_233_cleanup_target_scope_confirmed_count"] == 1
    assert (
        summary[
            "section_234_saved_asset_pre_delete_readback_confirmed_count"
        ]
        == 1
    )
    assert summary["section_235_cleanup_delete_dry_run_plan_accepted_count"] == 1
    assert summary["section_236_delete_target_isolation_proved_count"] == 1
    assert summary["section_237_dirty_package_no_delete_boundary_clean_count"] == 1
    assert summary["section_238_delete_command_dispatch_dry_run_ready_count"] == 1
    assert summary["section_239_delete_result_readback_dry_run_ready_count"] == 1
    assert (
        summary["section_240_actual_delete_requires_final_user_checkpoint_count"]
        == 1
    )
    assert summary["cleanup_delete_dry_run_allowed_count"] == 1
    assert summary["cleanup_allowed_count"] == 0
    assert summary["cleanup_executed_count"] == 0
    assert summary["delete_command_dispatched_count"] == 0
    assert summary["delete_command_executed_count"] == 0
    assert summary["delete_asset_allowed_count"] == 0
    assert summary["rename_asset_allowed_count"] == 0
    assert summary["production_path_write_allowed_count"] == 0
    assert summary["production_path_write_executed_count"] == 0

    missing_stability = dict(section_225_232_summary)
    missing_stability["live_save_stability_ready_count"] = 0
    missing_stability_contract = (
        cleanup_delete_dry_run
        .build_durable_executor_authoring_cleanup_delete_dry_run_batch_contract(
            True,
            missing_stability,
            cleanup_result,
        )
    )
    missing_stability_summary = (
        cleanup_delete_dry_run
        .summarize_durable_executor_authoring_cleanup_delete_dry_run_batches(
            [missing_stability_contract]
        )
    )
    assert missing_stability_contract["section_225_232_save_stability_ready"] is False
    assert missing_stability_contract["cleanup_delete_dry_run_ready"] is False
    assert missing_stability_contract["delete_asset_allowed"] is False
    assert missing_stability_summary["status"] == "failed"

    wrong_target_contract = (
        cleanup_delete_dry_run
        .build_durable_executor_authoring_cleanup_delete_dry_run_batch_contract(
            True,
            section_225_232_summary,
            build_current_cleanup_delete_result(
                target_asset_path="/Game/Cubeless/Unsafe/BP_Unsafe",
                target_under_temp_root=False,
            ),
        )
    )
    wrong_target_summary = (
        cleanup_delete_dry_run
        .summarize_durable_executor_authoring_cleanup_delete_dry_run_batches(
            [wrong_target_contract]
        )
    )
    assert wrong_target_contract["cleanup_target_scope_confirmed"] is False
    assert wrong_target_contract["cleanup_delete_dry_run_ready"] is False
    assert wrong_target_contract["production_path_write_allowed"] is False
    assert wrong_target_summary["status"] == "failed"

    dirty_contract = (
        cleanup_delete_dry_run
        .build_durable_executor_authoring_cleanup_delete_dry_run_batch_contract(
            True,
            section_225_232_summary,
            build_current_cleanup_delete_result(dirty_content_package_count=1),
        )
    )
    dirty_summary = (
        cleanup_delete_dry_run
        .summarize_durable_executor_authoring_cleanup_delete_dry_run_batches(
            [dirty_contract]
        )
    )
    assert dirty_contract["dirty_package_no_delete_boundary_clean"] is False
    assert dirty_contract["cleanup_delete_dry_run_ready"] is False
    assert dirty_contract["delete_asset_allowed"] is False
    assert dirty_summary["status"] == "failed"

    delete_attempt_contract = (
        cleanup_delete_dry_run
        .build_durable_executor_authoring_cleanup_delete_dry_run_batch_contract(
            True,
            section_225_232_summary,
            build_current_cleanup_delete_result(delete_asset_called=True),
        )
    )
    delete_attempt_summary = (
        cleanup_delete_dry_run
        .summarize_durable_executor_authoring_cleanup_delete_dry_run_batches(
            [delete_attempt_contract]
        )
    )
    assert delete_attempt_contract["dry_run_blocks_actual_delete_outputs"] is False
    assert delete_attempt_contract["cleanup_delete_dry_run_ready"] is False
    assert delete_attempt_contract["delete_asset_allowed"] is False
    assert delete_attempt_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring cleanup/delete dry-run batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
