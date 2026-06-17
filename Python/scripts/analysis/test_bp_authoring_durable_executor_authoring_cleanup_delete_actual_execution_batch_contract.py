#!/usr/bin/env python
"""Offline smoke tests for Sections 289-296 cleanup/delete actual execution."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract as cleanup_delete  # noqa: E402
import bp_authoring_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract as diagnostics  # noqa: E402
from test_bp_authoring_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract import build_current_section_273_280_summary  # noqa: E402


def build_current_section_281_288_summary() -> dict:
    section_273_280_summary = build_current_section_273_280_summary()
    diagnostics_result = diagnostics.build_function_diagnostics_graph_layout_result()
    contract = diagnostics.build_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract(
        True,
        section_273_280_summary,
        diagnostics_result,
    )
    return diagnostics.summarize_durable_executor_authoring_function_diagnostics_graph_layout_batches(
        [contract]
    )


def build_current_delete_result(**overrides: object) -> dict:
    result = cleanup_delete.build_cleanup_delete_actual_execution_result()
    result.update(overrides)
    return result


def main() -> int:
    section_281_288_summary = build_current_section_281_288_summary()
    result = build_current_delete_result()
    contract = cleanup_delete.build_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract(
        True,
        section_281_288_summary,
        result,
    )
    assert (
        contract["schema"]
        == cleanup_delete
        .DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_ACTUAL_EXECUTION_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_281_288_summary_schema_matches"] is True
    assert contract["section_281_288_summary_passed"] is True
    assert (
        contract["section_281_288_function_diagnostics_graph_layout_ready"]
        is True
    )
    assert contract["section_281_288_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["actual_checkpoint_satisfied"] is True
    assert contract["delete_target_scope_isolated"] is True
    assert contract["delete_preflight_verified"] is True
    assert contract["delete_asset_executed"] is True
    assert contract["delete_readback_verified"] is True
    assert contract["external_dirty_baseline_preserved"] is True
    assert contract["non_delete_destructive_outputs_closed"] is True
    assert contract["result_has_no_error"] is True
    assert contract["section_289_cleanup_delete_actual_checkpoint_satisfied"] is True
    assert contract["section_290_delete_target_scope_isolated"] is True
    assert contract["section_291_delete_preflight_verified"] is True
    assert contract["section_292_delete_asset_executed"] is True
    assert contract["section_293_delete_readback_verified"] is True
    assert contract["section_294_external_dirty_baseline_preserved"] is True
    assert contract["section_295_non_delete_destructive_outputs_closed"] is True
    assert contract["section_296_cleanup_delete_actual_release_ready"] is True
    assert contract["cleanup_delete_actual_execution_ready"] is True
    assert contract["cleanup_delete_actual_target_deleted"] is True
    assert contract["cleanup_delete_actual_external_dirty_preserved"] is True
    assert contract["final_durable_release_ready"] is True
    assert contract["delete_asset_allowed"] is True
    assert contract["delete_asset_executed_output"] is True
    assert contract["cleanup_allowed"] is False
    assert contract["cleanup_executed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["overwrite_allowed"] is False
    assert contract["production_path_write_allowed"] is False

    summary = cleanup_delete.summarize_durable_executor_authoring_cleanup_delete_actual_execution_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_cleanup_delete_actual_execution_batch_count"
        ]
        == 1
    )
    expected_one_counts = (
        "section_281_288_summary_schema_matches_count",
        "section_281_288_summary_passed_count",
        "section_281_288_function_diagnostics_graph_layout_ready_count",
        "section_281_288_outputs_closed_count",
        "result_schema_matches_count",
        "actual_checkpoint_satisfied_count",
        "delete_target_scope_isolated_count",
        "delete_preflight_verified_count",
        "delete_asset_executed_count",
        "delete_readback_verified_count",
        "external_dirty_baseline_preserved_count",
        "non_delete_destructive_outputs_closed_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "delete_asset_allowed_count",
        "delete_asset_executed_output_count",
        "section_289_cleanup_delete_actual_checkpoint_satisfied_count",
        "section_290_delete_target_scope_isolated_count",
        "section_291_delete_preflight_verified_count",
        "section_292_delete_asset_executed_count",
        "section_293_delete_readback_verified_count",
        "section_294_external_dirty_baseline_preserved_count",
        "section_295_non_delete_destructive_outputs_closed_count",
        "section_296_cleanup_delete_actual_release_ready_count",
        "cleanup_delete_actual_execution_ready_count",
        "cleanup_delete_actual_target_deleted_count",
        "cleanup_delete_actual_external_dirty_preserved_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    expected_zero_counts = (
        "cleanup_allowed_count",
        "cleanup_executed_count",
        "rename_asset_allowed_count",
        "rename_command_dispatched_count",
        "rename_command_executed_count",
        "overwrite_allowed_count",
        "overwrite_executed_count",
        "actor_bp_authoring_compile_dispatched_count",
        "actor_bp_authoring_compile_executed_count",
        "actor_bp_authoring_save_dispatched_count",
        "actor_bp_authoring_save_executed_count",
        "actor_bp_authoring_asset_write_performed_count",
        "actor_bp_authoring_package_dirty_marked_count",
        "production_path_write_allowed_count",
        "production_path_write_executed_count",
    )
    for key in expected_zero_counts:
        assert summary[key] == 0, key

    missing_diagnostics = dict(section_281_288_summary)
    missing_diagnostics[
        "function_diagnostics_graph_layout_no_write_verified_count"
    ] = 0
    missing_diagnostics_contract = cleanup_delete.build_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract(
        True,
        missing_diagnostics,
        result,
    )
    missing_diagnostics_summary = cleanup_delete.summarize_durable_executor_authoring_cleanup_delete_actual_execution_batches(
        [missing_diagnostics_contract]
    )
    assert (
        missing_diagnostics_contract[
            "section_281_288_function_diagnostics_graph_layout_ready"
        ]
        is False
    )
    assert (
        missing_diagnostics_contract[
            "cleanup_delete_actual_execution_ready"
        ]
        is False
    )
    assert missing_diagnostics_summary["status"] == "failed"

    production_target_contract = cleanup_delete.build_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract(
        True,
        section_281_288_summary,
        build_current_delete_result(
            target_asset_path="/Game/Cubeless/Unsafe/BP_DurableSaveGatePrep",
            target_under_expected_root=False,
        ),
    )
    production_target_summary = cleanup_delete.summarize_durable_executor_authoring_cleanup_delete_actual_execution_batches(
        [production_target_contract]
    )
    assert production_target_contract["delete_target_scope_isolated"] is False
    assert production_target_contract["cleanup_delete_actual_execution_ready"] is False
    assert production_target_summary["status"] == "failed"

    dirty_changed_contract = cleanup_delete.build_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract(
        True,
        section_281_288_summary,
        build_current_delete_result(
            external_dirty_after=(
                cleanup_delete.DEFAULT_EXTERNAL_DIRTY_PACKAGE,
                "/Game/Cubeless/UnexpectedDirty",
            ),
            external_dirty_preserved=False,
        ),
    )
    dirty_changed_summary = cleanup_delete.summarize_durable_executor_authoring_cleanup_delete_actual_execution_batches(
        [dirty_changed_contract]
    )
    assert dirty_changed_contract["external_dirty_baseline_preserved"] is False
    assert dirty_changed_contract["cleanup_delete_actual_execution_ready"] is False
    assert dirty_changed_summary["status"] == "failed"

    readback_failed_contract = cleanup_delete.build_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract(
        True,
        section_281_288_summary,
        build_current_delete_result(
            asset_exists_after=True,
            content_file_exists_after=True,
            readback_delete_verified=False,
        ),
    )
    readback_failed_summary = cleanup_delete.summarize_durable_executor_authoring_cleanup_delete_actual_execution_batches(
        [readback_failed_contract]
    )
    assert readback_failed_contract["delete_readback_verified"] is False
    assert readback_failed_contract["cleanup_delete_actual_target_deleted"] is False
    assert readback_failed_summary["status"] == "failed"

    rename_attempt_contract = cleanup_delete.build_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract(
        True,
        section_281_288_summary,
        build_current_delete_result(
            rename_asset_allowed=True,
            rename_command_dispatched=True,
        ),
    )
    rename_attempt_summary = cleanup_delete.summarize_durable_executor_authoring_cleanup_delete_actual_execution_batches(
        [rename_attempt_contract]
    )
    assert (
        rename_attempt_contract["non_delete_destructive_outputs_closed"]
        is False
    )
    assert rename_attempt_contract["cleanup_delete_actual_execution_ready"] is False
    assert rename_attempt_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring cleanup/delete actual execution batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
