#!/usr/bin/env python
"""Offline smoke tests for Sections 305-312 post-delete recreation actual execution."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract as recreation_actual  # noqa: E402
import bp_authoring_durable_executor_authoring_post_delete_recreation_reset_batch_contract as post_delete_reset  # noqa: E402
from test_bp_authoring_durable_executor_authoring_post_delete_recreation_reset_batch_contract import build_current_section_289_296_summary  # noqa: E402


def build_current_section_297_304_summary() -> dict:
    section_289_296_summary = build_current_section_289_296_summary()
    reset_result = post_delete_reset.build_post_delete_recreation_reset_result()
    contract = post_delete_reset.build_durable_executor_authoring_post_delete_recreation_reset_batch_contract(
        True,
        section_289_296_summary,
        reset_result,
    )
    return post_delete_reset.summarize_durable_executor_authoring_post_delete_recreation_reset_batches(
        [contract]
    )


def build_current_recreation_result(**overrides: object) -> dict:
    result = recreation_actual.build_post_delete_recreation_actual_execution_result()
    result.update(overrides)
    return result


def main() -> int:
    section_297_304_summary = build_current_section_297_304_summary()
    result = build_current_recreation_result()
    contract = recreation_actual.build_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract(
        True,
        section_297_304_summary,
        result,
    )
    assert (
        contract["schema"]
        == recreation_actual
        .DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_ACTUAL_EXECUTION_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_297_304_summary_schema_matches"] is True
    assert contract["section_297_304_summary_passed"] is True
    assert contract["section_297_304_post_delete_reset_ready"] is True
    assert contract["section_297_304_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["recreation_checkpoint_satisfied"] is True
    assert contract["recreation_target_absence_preflight"] is True
    assert contract["recreate_actor_bp_executed"] is True
    assert contract["recreated_actor_bp_compiled"] is True
    assert contract["recreated_actor_bp_saved"] is True
    assert contract["recreated_actor_bp_readback_verified"] is True
    assert contract["recreation_dirty_baseline_preserved"] is True
    assert contract["authoring_expansion_outputs_closed"] is True
    assert contract["result_has_no_error"] is True
    assert contract["section_305_recreation_checkpoint_satisfied"] is True
    assert contract["section_306_recreation_target_absence_preflight"] is True
    assert contract["section_307_recreate_actor_bp_executed"] is True
    assert contract["section_308_recreated_actor_bp_compiled"] is True
    assert contract["section_309_recreated_actor_bp_saved"] is True
    assert contract["section_310_recreated_actor_bp_readback_verified"] is True
    assert contract["section_311_recreation_dirty_baseline_preserved"] is True
    assert contract["section_312_recreation_actual_release_ready"] is True
    assert contract["post_delete_recreation_actual_execution_ready"] is True
    assert contract["post_delete_recreated_actor_bp_saved"] is True
    assert contract["post_delete_recreated_actor_bp_readback_verified"] is True
    assert contract["recreate_asset_allowed"] is True
    assert contract["recreate_command_dispatched"] is True
    assert contract["actor_bp_authoring_compile_executed"] is True
    assert contract["actor_bp_authoring_save_executed"] is True
    assert contract["actor_bp_authoring_asset_write_performed"] is True
    assert contract["actor_bp_authoring_package_dirty_marked"] is False
    assert contract["variable_add_command_executed"] is False
    assert contract["component_add_command_executed"] is False
    assert contract["default_write_command_executed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["production_path_write_allowed"] is False

    summary = recreation_actual.summarize_durable_executor_authoring_post_delete_recreation_actual_execution_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_post_delete_recreation_actual_execution_batch_count"
        ]
        == 1
    )
    expected_one_counts = (
        "section_297_304_summary_schema_matches_count",
        "section_297_304_summary_passed_count",
        "section_297_304_post_delete_reset_ready_count",
        "section_297_304_outputs_closed_count",
        "result_schema_matches_count",
        "recreation_checkpoint_satisfied_count",
        "recreation_target_absence_preflight_count",
        "recreate_actor_bp_executed_count",
        "recreated_actor_bp_compiled_count",
        "recreated_actor_bp_saved_count",
        "recreated_actor_bp_readback_verified_count",
        "recreation_dirty_baseline_preserved_count",
        "authoring_expansion_outputs_closed_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "recreate_asset_allowed_count",
        "recreate_command_dispatched_count",
        "recreate_command_executed_count",
        "actor_bp_authoring_compile_dispatched_count",
        "actor_bp_authoring_compile_executed_count",
        "actor_bp_authoring_save_dispatched_count",
        "actor_bp_authoring_save_executed_count",
        "actor_bp_authoring_asset_write_performed_count",
        "section_305_recreation_checkpoint_satisfied_count",
        "section_306_recreation_target_absence_preflight_count",
        "section_307_recreate_actor_bp_executed_count",
        "section_308_recreated_actor_bp_compiled_count",
        "section_309_recreated_actor_bp_saved_count",
        "section_310_recreated_actor_bp_readback_verified_count",
        "section_311_recreation_dirty_baseline_preserved_count",
        "section_312_recreation_actual_release_ready_count",
        "post_delete_recreation_actual_execution_ready_count",
        "post_delete_recreated_actor_bp_saved_count",
        "post_delete_recreated_actor_bp_readback_verified_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    expected_zero_counts = (
        "actor_bp_authoring_package_dirty_marked_count",
        *recreation_actual.BLOCKED_POST_DELETE_RECREATION_ACTUAL_OUTPUT_COUNT_KEYS,
    )
    for key in expected_zero_counts:
        assert summary[key] == 0, key

    missing_reset = dict(section_297_304_summary)
    missing_reset["post_delete_recreation_requires_checkpoint_count"] = 0
    missing_reset_contract = recreation_actual.build_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract(
        True,
        missing_reset,
        result,
    )
    missing_reset_summary = recreation_actual.summarize_durable_executor_authoring_post_delete_recreation_actual_execution_batches(
        [missing_reset_contract]
    )
    assert missing_reset_contract["section_297_304_post_delete_reset_ready"] is False
    assert missing_reset_contract["post_delete_recreation_actual_execution_ready"] is False
    assert missing_reset_summary["status"] == "failed"

    preflight_failed_contract = recreation_actual.build_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract(
        True,
        section_297_304_summary,
        build_current_recreation_result(
            asset_exists_before=True,
            content_file_exists_before=True,
            preflight_passed=False,
        ),
    )
    preflight_failed_summary = recreation_actual.summarize_durable_executor_authoring_post_delete_recreation_actual_execution_batches(
        [preflight_failed_contract]
    )
    assert preflight_failed_contract["recreation_target_absence_preflight"] is False
    assert preflight_failed_contract["post_delete_recreation_actual_execution_ready"] is False
    assert preflight_failed_summary["status"] == "failed"

    recreate_failed_contract = recreation_actual.build_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract(
        True,
        section_297_304_summary,
        build_current_recreation_result(
            recreate_command_executed=False,
            asset_write_performed=False,
        ),
    )
    recreate_failed_summary = recreation_actual.summarize_durable_executor_authoring_post_delete_recreation_actual_execution_batches(
        [recreate_failed_contract]
    )
    assert recreate_failed_contract["recreate_actor_bp_executed"] is False
    assert recreate_failed_contract["post_delete_recreation_actual_execution_ready"] is False
    assert recreate_failed_summary["status"] == "failed"

    readback_failed_contract = recreation_actual.build_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract(
        True,
        section_297_304_summary,
        build_current_recreation_result(
            asset_exists_after=False,
            cdo_is_actor=False,
            readback_verified=False,
        ),
    )
    readback_failed_summary = recreation_actual.summarize_durable_executor_authoring_post_delete_recreation_actual_execution_batches(
        [readback_failed_contract]
    )
    assert readback_failed_contract["recreated_actor_bp_readback_verified"] is False
    assert readback_failed_contract["post_delete_recreated_actor_bp_readback_verified"] is False
    assert readback_failed_summary["status"] == "failed"

    variable_attempt_contract = recreation_actual.build_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract(
        True,
        section_297_304_summary,
        build_current_recreation_result(
            variable_add_command_dispatched=True,
            variable_add_command_executed=True,
        ),
    )
    variable_attempt_summary = recreation_actual.summarize_durable_executor_authoring_post_delete_recreation_actual_execution_batches(
        [variable_attempt_contract]
    )
    assert variable_attempt_contract["authoring_expansion_outputs_closed"] is False
    assert variable_attempt_contract["post_delete_recreation_actual_execution_ready"] is False
    assert variable_attempt_summary["status"] == "failed"

    production_attempt_contract = recreation_actual.build_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract(
        True,
        section_297_304_summary,
        build_current_recreation_result(
            target_asset_path="/Game/Cubeless/Unsafe/BP_DurableSaveGatePrep",
            target_under_expected_root=False,
            production_path_write_allowed=True,
            production_path_write_executed=True,
        ),
    )
    production_attempt_summary = recreation_actual.summarize_durable_executor_authoring_post_delete_recreation_actual_execution_batches(
        [production_attempt_contract]
    )
    assert production_attempt_contract["recreation_target_absence_preflight"] is False
    assert production_attempt_contract["authoring_expansion_outputs_closed"] is False
    assert production_attempt_contract["post_delete_recreation_actual_execution_ready"] is False
    assert production_attempt_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring post-delete recreation actual execution batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
