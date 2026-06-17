#!/usr/bin/env python
"""Offline smoke tests for Sections 241-248 rename/overwrite dry-run batch."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_cleanup_delete_dry_run_batch_contract as cleanup_delete_dry_run  # noqa: E402
import bp_authoring_durable_executor_authoring_rename_overwrite_dry_run_batch_contract as rename_overwrite_dry_run  # noqa: E402
from test_bp_authoring_durable_executor_authoring_cleanup_delete_dry_run_batch_contract import build_current_section_225_232_summary  # noqa: E402


def build_current_section_233_240_summary() -> dict:
    section_225_232_summary = build_current_section_225_232_summary()
    cleanup_result = cleanup_delete_dry_run.build_cleanup_delete_dry_run_result(
        package_file_size_bytes=24133,
    )
    contract = (
        cleanup_delete_dry_run
        .build_durable_executor_authoring_cleanup_delete_dry_run_batch_contract(
            True,
            section_225_232_summary,
            cleanup_result,
        )
    )
    return (
        cleanup_delete_dry_run
        .summarize_durable_executor_authoring_cleanup_delete_dry_run_batches(
            [contract]
        )
    )


def build_current_rename_result(**overrides: object) -> dict:
    result = rename_overwrite_dry_run.build_rename_overwrite_dry_run_result()
    result.update(overrides)
    return result


def main() -> int:
    section_233_240_summary = build_current_section_233_240_summary()
    rename_result = build_current_rename_result()
    contract = (
        rename_overwrite_dry_run
        .build_durable_executor_authoring_rename_overwrite_dry_run_batch_contract(
            True,
            section_233_240_summary,
            rename_result,
        )
    )
    assert (
        contract["schema"]
        == rename_overwrite_dry_run
        .DURABLE_EXECUTOR_AUTHORING_RENAME_OVERWRITE_DRY_RUN_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_233_240_summary_schema_matches"] is True
    assert contract["section_233_240_summary_passed"] is True
    assert contract["section_233_240_cleanup_delete_dry_run_ready"] is True
    assert contract["section_233_240_destructive_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["rename_source_scope_confirmed"] is True
    assert contract["rename_destination_scope_confirmed"] is True
    assert contract["overwrite_policy_denies_existing_destination"] is True
    assert contract["rename_overwrite_dry_run_plan_accepted"] is True
    assert contract["rename_collision_boundary_clean"] is True
    assert contract["rename_dirty_package_boundary_clean"] is True
    assert contract["rename_result_readback_dry_run_ready"] is True
    assert contract["dry_run_blocks_actual_rename_outputs"] is True
    assert contract["result_has_no_error"] is True
    assert contract["rename_overwrite_dry_run_ready"] is True
    assert contract["actual_rename_overwrite_requires_final_user_checkpoint"] is True
    assert contract["section_241_rename_source_scope_confirmed"] is True
    assert contract["section_242_rename_destination_scope_confirmed"] is True
    assert contract["section_243_overwrite_policy_denies_existing_destination"] is True
    assert contract["section_244_rename_overwrite_dry_run_plan_accepted"] is True
    assert contract["section_245_rename_collision_boundary_clean"] is True
    assert contract["section_246_rename_dirty_package_boundary_clean"] is True
    assert contract["section_247_rename_result_readback_dry_run_ready"] is True
    assert (
        contract["section_248_actual_rename_overwrite_requires_final_user_checkpoint"]
        is True
    )
    assert contract["rename_overwrite_dry_run_allowed"] is True
    assert contract["rename_overwrite_dry_run_ready"] is True
    assert contract["cleanup_allowed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["rename_command_dispatched"] is False
    assert contract["rename_command_executed"] is False
    assert contract["overwrite_allowed"] is False
    assert contract["overwrite_executed"] is False
    assert contract["production_path_write_allowed"] is False

    summary = (
        rename_overwrite_dry_run
        .summarize_durable_executor_authoring_rename_overwrite_dry_run_batches(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_rename_overwrite_dry_run_batch_count"
        ]
        == 1
    )
    assert summary["section_233_240_cleanup_delete_dry_run_ready_count"] == 1
    assert summary["rename_source_scope_confirmed_count"] == 1
    assert summary["rename_destination_scope_confirmed_count"] == 1
    assert summary["overwrite_policy_denies_existing_destination_count"] == 1
    assert summary["rename_overwrite_dry_run_plan_accepted_count"] == 1
    assert summary["rename_collision_boundary_clean_count"] == 1
    assert summary["rename_dirty_package_boundary_clean_count"] == 1
    assert summary["rename_result_readback_dry_run_ready_count"] == 1
    assert summary["rename_overwrite_dry_run_ready_count"] == 1
    assert (
        summary[
            "actual_rename_overwrite_requires_final_user_checkpoint_count"
        ]
        == 1
    )
    assert summary["section_241_rename_source_scope_confirmed_count"] == 1
    assert summary["section_242_rename_destination_scope_confirmed_count"] == 1
    assert (
        summary[
            "section_243_overwrite_policy_denies_existing_destination_count"
        ]
        == 1
    )
    assert summary["section_244_rename_overwrite_dry_run_plan_accepted_count"] == 1
    assert summary["section_245_rename_collision_boundary_clean_count"] == 1
    assert summary["section_246_rename_dirty_package_boundary_clean_count"] == 1
    assert summary["section_247_rename_result_readback_dry_run_ready_count"] == 1
    assert (
        summary[
            "section_248_actual_rename_overwrite_requires_final_user_checkpoint_count"
        ]
        == 1
    )
    assert summary["rename_overwrite_dry_run_allowed_count"] == 1
    assert summary["rename_asset_allowed_count"] == 0
    assert summary["rename_command_dispatched_count"] == 0
    assert summary["rename_command_executed_count"] == 0
    assert summary["overwrite_allowed_count"] == 0
    assert summary["overwrite_executed_count"] == 0
    assert summary["production_path_write_allowed_count"] == 0

    missing_cleanup = dict(section_233_240_summary)
    missing_cleanup["cleanup_delete_dry_run_ready_count"] = 0
    missing_cleanup_contract = (
        rename_overwrite_dry_run
        .build_durable_executor_authoring_rename_overwrite_dry_run_batch_contract(
            True,
            missing_cleanup,
            rename_result,
        )
    )
    missing_cleanup_summary = (
        rename_overwrite_dry_run
        .summarize_durable_executor_authoring_rename_overwrite_dry_run_batches(
            [missing_cleanup_contract]
        )
    )
    assert missing_cleanup_contract["section_233_240_cleanup_delete_dry_run_ready"] is False
    assert missing_cleanup_contract["rename_overwrite_dry_run_ready"] is False
    assert missing_cleanup_contract["rename_asset_allowed"] is False
    assert missing_cleanup_summary["status"] == "failed"

    destination_exists_contract = (
        rename_overwrite_dry_run
        .build_durable_executor_authoring_rename_overwrite_dry_run_batch_contract(
            True,
            section_233_240_summary,
            build_current_rename_result(destination_exists=True),
        )
    )
    destination_exists_summary = (
        rename_overwrite_dry_run
        .summarize_durable_executor_authoring_rename_overwrite_dry_run_batches(
            [destination_exists_contract]
        )
    )
    assert destination_exists_contract["overwrite_policy_denies_existing_destination"] is False
    assert destination_exists_contract["rename_overwrite_dry_run_ready"] is False
    assert destination_exists_contract["overwrite_allowed"] is False
    assert destination_exists_summary["status"] == "failed"

    production_destination_contract = (
        rename_overwrite_dry_run
        .build_durable_executor_authoring_rename_overwrite_dry_run_batch_contract(
            True,
            section_233_240_summary,
            build_current_rename_result(
                destination_asset_path="/Game/Cubeless/Unsafe/BP_Renamed",
                destination_under_temp_root=False,
            ),
        )
    )
    production_destination_summary = (
        rename_overwrite_dry_run
        .summarize_durable_executor_authoring_rename_overwrite_dry_run_batches(
            [production_destination_contract]
        )
    )
    assert production_destination_contract["rename_destination_scope_confirmed"] is False
    assert production_destination_contract["rename_overwrite_dry_run_ready"] is False
    assert production_destination_contract["production_path_write_allowed"] is False
    assert production_destination_summary["status"] == "failed"

    rename_attempt_contract = (
        rename_overwrite_dry_run
        .build_durable_executor_authoring_rename_overwrite_dry_run_batch_contract(
            True,
            section_233_240_summary,
            build_current_rename_result(rename_asset_called=True),
        )
    )
    rename_attempt_summary = (
        rename_overwrite_dry_run
        .summarize_durable_executor_authoring_rename_overwrite_dry_run_batches(
            [rename_attempt_contract]
        )
    )
    assert rename_attempt_contract["dry_run_blocks_actual_rename_outputs"] is False
    assert rename_attempt_contract["rename_overwrite_dry_run_ready"] is False
    assert rename_attempt_contract["rename_asset_allowed"] is False
    assert rename_attempt_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring rename/overwrite dry-run batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
