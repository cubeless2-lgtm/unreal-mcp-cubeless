#!/usr/bin/env python
"""Offline smoke tests for Sections 297-304 post-delete reset."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract as cleanup_delete  # noqa: E402
import bp_authoring_durable_executor_authoring_post_delete_recreation_reset_batch_contract as post_delete_reset  # noqa: E402
from test_bp_authoring_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract import build_current_section_281_288_summary  # noqa: E402


def build_current_section_289_296_summary() -> dict:
    section_281_288_summary = build_current_section_281_288_summary()
    delete_result = cleanup_delete.build_cleanup_delete_actual_execution_result()
    contract = cleanup_delete.build_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract(
        True,
        section_281_288_summary,
        delete_result,
    )
    return cleanup_delete.summarize_durable_executor_authoring_cleanup_delete_actual_execution_batches(
        [contract]
    )


def build_current_reset_result(**overrides: object) -> dict:
    result = post_delete_reset.build_post_delete_recreation_reset_result()
    result.update(overrides)
    return result


def main() -> int:
    section_289_296_summary = build_current_section_289_296_summary()
    result = build_current_reset_result()
    contract = post_delete_reset.build_durable_executor_authoring_post_delete_recreation_reset_batch_contract(
        True,
        section_289_296_summary,
        result,
    )
    assert (
        contract["schema"]
        == post_delete_reset
        .DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_RESET_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_289_296_summary_schema_matches"] is True
    assert contract["section_289_296_summary_passed"] is True
    assert contract["section_289_296_cleanup_delete_actual_ready"] is True
    assert contract["section_289_296_non_delete_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["post_delete_checkpoint_satisfied"] is True
    assert contract["deleted_target_absence_confirmed"] is True
    assert contract["recreation_plan_scoped"] is True
    assert contract["recreation_requires_explicit_checkpoint"] is True
    assert contract["readback_routes_reset"] is True
    assert contract["diagnostics_routes_reset"] is True
    assert contract["post_delete_no_write_boundary_verified"] is True
    assert contract["result_has_no_error"] is True
    assert contract["section_297_post_delete_checkpoint_satisfied"] is True
    assert contract["section_298_deleted_target_absence_confirmed"] is True
    assert contract["section_299_recreation_plan_scoped"] is True
    assert contract["section_300_recreation_requires_explicit_checkpoint"] is True
    assert contract["section_301_readback_routes_reset"] is True
    assert contract["section_302_diagnostics_routes_reset"] is True
    assert contract["section_303_post_delete_no_write_boundary_verified"] is True
    assert contract["section_304_post_delete_reset_release_ready"] is True
    assert contract["post_delete_recreation_reset_ready"] is True
    assert contract["post_delete_target_absence_confirmed"] is True
    assert contract["post_delete_recreation_requires_checkpoint"] is True
    assert contract["final_durable_release_ready"] is True
    assert contract["recreate_asset_allowed"] is False
    assert contract["recreate_command_dispatched"] is False
    assert contract["readback_command_dispatched"] is False
    assert contract["diagnostics_command_dispatched"] is False
    assert contract["graph_repair_command_dispatched"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["delete_asset_executed_output"] is False

    summary = post_delete_reset.summarize_durable_executor_authoring_post_delete_recreation_reset_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_post_delete_recreation_reset_batch_count"
        ]
        == 1
    )
    expected_one_counts = (
        "section_289_296_summary_schema_matches_count",
        "section_289_296_summary_passed_count",
        "section_289_296_cleanup_delete_actual_ready_count",
        "section_289_296_non_delete_outputs_closed_count",
        "result_schema_matches_count",
        "post_delete_checkpoint_satisfied_count",
        "deleted_target_absence_confirmed_count",
        "recreation_plan_scoped_count",
        "recreation_requires_explicit_checkpoint_count",
        "readback_routes_reset_count",
        "diagnostics_routes_reset_count",
        "post_delete_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_297_post_delete_checkpoint_satisfied_count",
        "section_298_deleted_target_absence_confirmed_count",
        "section_299_recreation_plan_scoped_count",
        "section_300_recreation_requires_explicit_checkpoint_count",
        "section_301_readback_routes_reset_count",
        "section_302_diagnostics_routes_reset_count",
        "section_303_post_delete_no_write_boundary_verified_count",
        "section_304_post_delete_reset_release_ready_count",
        "post_delete_recreation_reset_ready_count",
        "post_delete_target_absence_confirmed_count",
        "post_delete_recreation_requires_checkpoint_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in (
        post_delete_reset
        .BLOCKED_POST_DELETE_RECREATION_RESET_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key

    missing_delete = dict(section_289_296_summary)
    missing_delete["cleanup_delete_actual_target_deleted_count"] = 0
    missing_delete_contract = post_delete_reset.build_durable_executor_authoring_post_delete_recreation_reset_batch_contract(
        True,
        missing_delete,
        result,
    )
    missing_delete_summary = post_delete_reset.summarize_durable_executor_authoring_post_delete_recreation_reset_batches(
        [missing_delete_contract]
    )
    assert (
        missing_delete_contract["section_289_296_cleanup_delete_actual_ready"]
        is False
    )
    assert missing_delete_contract["post_delete_recreation_reset_ready"] is False
    assert missing_delete_summary["status"] == "failed"

    target_reappeared_contract = post_delete_reset.build_durable_executor_authoring_post_delete_recreation_reset_batch_contract(
        True,
        section_289_296_summary,
        build_current_reset_result(
            asset_exists_after_delete=True,
            asset_data_valid_after_delete=True,
            content_file_exists_after_delete=True,
            deleted_target_absence_confirmed=False,
        ),
    )
    target_reappeared_summary = post_delete_reset.summarize_durable_executor_authoring_post_delete_recreation_reset_batches(
        [target_reappeared_contract]
    )
    assert target_reappeared_contract["deleted_target_absence_confirmed"] is False
    assert target_reappeared_contract["post_delete_recreation_reset_ready"] is False
    assert target_reappeared_summary["status"] == "failed"

    recreation_dispatched_contract = post_delete_reset.build_durable_executor_authoring_post_delete_recreation_reset_batch_contract(
        True,
        section_289_296_summary,
        build_current_reset_result(
            recreate_asset_allowed=True,
            recreate_command_dispatched=True,
        ),
    )
    recreation_dispatched_summary = post_delete_reset.summarize_durable_executor_authoring_post_delete_recreation_reset_batches(
        [recreation_dispatched_contract]
    )
    assert (
        recreation_dispatched_contract[
            "recreation_requires_explicit_checkpoint"
        ]
        is False
    )
    assert recreation_dispatched_contract["post_delete_recreation_reset_ready"] is False
    assert recreation_dispatched_summary["status"] == "failed"

    readback_dispatched_contract = post_delete_reset.build_durable_executor_authoring_post_delete_recreation_reset_batch_contract(
        True,
        section_289_296_summary,
        build_current_reset_result(readback_command_dispatched=True),
    )
    readback_dispatched_summary = post_delete_reset.summarize_durable_executor_authoring_post_delete_recreation_reset_batches(
        [readback_dispatched_contract]
    )
    assert readback_dispatched_contract["readback_routes_reset"] is False
    assert readback_dispatched_contract["post_delete_recreation_reset_ready"] is False
    assert readback_dispatched_summary["status"] == "failed"

    diagnostics_dispatched_contract = post_delete_reset.build_durable_executor_authoring_post_delete_recreation_reset_batch_contract(
        True,
        section_289_296_summary,
        build_current_reset_result(
            diagnostics_command_dispatched=True,
            graph_layout_mutation_performed=True,
        ),
    )
    diagnostics_dispatched_summary = post_delete_reset.summarize_durable_executor_authoring_post_delete_recreation_reset_batches(
        [diagnostics_dispatched_contract]
    )
    assert diagnostics_dispatched_contract["diagnostics_routes_reset"] is False
    assert diagnostics_dispatched_contract["post_delete_recreation_reset_ready"] is False
    assert diagnostics_dispatched_summary["status"] == "failed"

    production_target_contract = post_delete_reset.build_durable_executor_authoring_post_delete_recreation_reset_batch_contract(
        True,
        section_289_296_summary,
        build_current_reset_result(
            target_asset_path="/Game/Cubeless/Unsafe/BP_DurableSaveGatePrep",
            target_under_expected_root=False,
        ),
    )
    production_target_summary = post_delete_reset.summarize_durable_executor_authoring_post_delete_recreation_reset_batches(
        [production_target_contract]
    )
    assert production_target_contract["deleted_target_absence_confirmed"] is False
    assert production_target_contract["recreation_plan_scoped"] is False
    assert production_target_contract["post_delete_recreation_reset_ready"] is False
    assert production_target_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring post-delete recreation reset batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
