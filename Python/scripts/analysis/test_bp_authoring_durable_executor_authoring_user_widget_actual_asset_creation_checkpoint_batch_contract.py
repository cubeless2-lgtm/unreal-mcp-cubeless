#!/usr/bin/env python
"""Offline smoke tests for Sections 409-416 UserWidget actual asset checkpoint."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract as actual  # noqa: E402
import bp_authoring_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract as dry_run  # noqa: E402
from test_bp_authoring_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract import build_current_section_393_400_summary  # noqa: E402


def build_current_section_401_408_summary() -> dict:
    section_393_400_summary = build_current_section_393_400_summary()
    result = dry_run.build_user_widget_widget_tree_authoring_dry_run_admission_result()
    contract = dry_run.build_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract(
        True,
        section_393_400_summary,
        result,
    )
    return dry_run.summarize_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batches(
        [contract]
    )


def build_current_actual_result(**overrides: object) -> dict:
    result = actual.build_user_widget_actual_asset_creation_checkpoint_result()
    result.update(overrides)
    return result


def main() -> int:
    section_401_408_summary = build_current_section_401_408_summary()
    result = build_current_actual_result()
    contract = actual.build_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract(
        True,
        section_401_408_summary,
        result,
    )
    assert (
        contract["schema"]
        == actual
        .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_ACTUAL_ASSET_CREATION_CHECKPOINT_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_401_408_summary_schema_matches"] is True
    assert contract["section_401_408_summary_passed"] is True
    assert contract["section_401_408_user_widget_dry_run_ready"] is True
    assert contract["section_401_408_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["user_widget_actual_creation_checkpoint_satisfied"] is True
    assert contract["user_widget_actual_target_scope_verified"] is True
    assert contract["widget_blueprint_create_or_reuse_executed"] is True
    assert contract["widget_blueprint_compile_save_verified"] is True
    assert contract["widget_blueprint_readback_package_confirmed"] is True
    assert contract["widget_tree_mutation_still_blocked"] is True
    assert (
        contract["user_widget_delete_rename_cleanup_production_blocked"]
        is True
    )
    assert contract["user_widget_actual_creation_no_dirty_leftover"] is True
    assert contract["result_has_no_error"] is True
    assert contract["section_409_user_widget_actual_creation_checkpoint_satisfied"] is True
    assert contract["section_410_user_widget_actual_target_scope_verified"] is True
    assert contract["section_411_widget_blueprint_create_or_reuse_executed"] is True
    assert contract["section_412_widget_blueprint_compile_save_verified"] is True
    assert contract["section_413_widget_blueprint_readback_package_confirmed"] is True
    assert contract["section_414_widget_tree_mutation_still_blocked"] is True
    assert (
        contract["section_415_user_widget_delete_rename_cleanup_production_blocked"]
        is True
    )
    assert (
        contract[
            "section_416_user_widget_actual_asset_creation_checkpoint_release_ready"
        ]
        is True
    )
    assert contract["user_widget_actual_asset_creation_checkpoint_ready"] is True
    assert contract["user_widget_widget_tree_mutation_still_blocked"] is True
    assert contract["final_durable_release_ready"] is True

    summary = actual.summarize_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    expected_one_counts = (
        "durable_requested_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_count",
        "section_401_408_summary_schema_matches_count",
        "section_401_408_summary_passed_count",
        "section_401_408_user_widget_dry_run_ready_count",
        "section_401_408_outputs_closed_count",
        "result_schema_matches_count",
        "user_widget_actual_creation_checkpoint_satisfied_count",
        "user_widget_actual_target_scope_verified_count",
        "widget_blueprint_create_or_reuse_executed_count",
        "widget_blueprint_compile_save_verified_count",
        "widget_blueprint_readback_package_confirmed_count",
        "widget_tree_mutation_still_blocked_count",
        "user_widget_delete_rename_cleanup_production_blocked_count",
        "user_widget_actual_creation_no_dirty_leftover_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_409_user_widget_actual_creation_checkpoint_satisfied_count",
        "section_410_user_widget_actual_target_scope_verified_count",
        "section_411_widget_blueprint_create_or_reuse_executed_count",
        "section_412_widget_blueprint_compile_save_verified_count",
        "section_413_widget_blueprint_readback_package_confirmed_count",
        "section_414_widget_tree_mutation_still_blocked_count",
        "section_415_user_widget_delete_rename_cleanup_production_blocked_count",
        "section_416_user_widget_actual_asset_creation_checkpoint_release_ready_count",
        "user_widget_actual_asset_creation_checkpoint_ready_count",
        "user_widget_widget_tree_mutation_still_blocked_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in actual.BLOCKED_USER_WIDGET_ACTUAL_ASSET_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key

    missing_upstream = dict(section_401_408_summary)
    missing_upstream[
        "user_widget_widget_tree_authoring_dry_run_admission_ready_count"
    ] = 0
    missing_upstream_contract = actual.build_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = actual.summarize_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batches(
        [missing_upstream_contract]
    )
    assert missing_upstream_contract["section_401_408_user_widget_dry_run_ready"] is False
    assert (
        missing_upstream_contract[
            "user_widget_actual_asset_creation_checkpoint_ready"
        ]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    wrong_target_contract = actual.build_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract(
        True,
        section_401_408_summary,
        build_current_actual_result(
            target_asset_path="/Game/Production/WBP_DurableWidgetTreeActual",
        ),
    )
    wrong_target_summary = actual.summarize_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batches(
        [wrong_target_contract]
    )
    assert wrong_target_contract["user_widget_actual_target_scope_verified"] is False
    assert wrong_target_summary["status"] == "failed"

    missing_asset_contract = actual.build_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract(
        True,
        section_401_408_summary,
        build_current_actual_result(
            asset_created=False,
            asset_preexisted=False,
            asset_loaded=False,
        ),
    )
    missing_asset_summary = actual.summarize_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batches(
        [missing_asset_contract]
    )
    assert missing_asset_contract["widget_blueprint_create_or_reuse_executed"] is False
    assert missing_asset_summary["status"] == "failed"

    failed_compile_contract = actual.build_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract(
        True,
        section_401_408_summary,
        build_current_actual_result(compile_succeeded=False),
    )
    failed_compile_summary = actual.summarize_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batches(
        [failed_compile_contract]
    )
    assert failed_compile_contract["widget_blueprint_compile_save_verified"] is False
    assert failed_compile_summary["status"] == "failed"

    missing_package_contract = actual.build_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract(
        True,
        section_401_408_summary,
        build_current_actual_result(
            package_file_exists=False,
            package_file_size_bytes=0,
            readback_asset_loaded=False,
        ),
    )
    missing_package_summary = actual.summarize_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batches(
        [missing_package_contract]
    )
    assert missing_package_contract["widget_blueprint_readback_package_confirmed"] is False
    assert missing_package_summary["status"] == "failed"

    widget_mutation_contract = actual.build_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract(
        True,
        section_401_408_summary,
        build_current_actual_result(widget_tree_mutation_attempted=True),
    )
    widget_mutation_summary = actual.summarize_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batches(
        [widget_mutation_contract]
    )
    assert widget_mutation_contract["widget_tree_mutation_still_blocked"] is False
    assert widget_mutation_summary["status"] == "failed"

    dirty_contract = actual.build_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract(
        True,
        section_401_408_summary,
        build_current_actual_result(
            dirty_content_after=[
                "/Game/_MCP_Temp/DurableSaveGate/UserWidgetActual/WBP_DurableWidgetTreeActual"
            ],
            target_dirty_after=True,
        ),
    )
    dirty_summary = actual.summarize_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batches(
        [dirty_contract]
    )
    assert dirty_contract["user_widget_actual_creation_no_dirty_leftover"] is False
    assert dirty_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring UserWidget actual asset creation checkpoint batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
