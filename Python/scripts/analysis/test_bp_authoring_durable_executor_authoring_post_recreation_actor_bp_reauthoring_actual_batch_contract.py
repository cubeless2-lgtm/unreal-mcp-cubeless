#!/usr/bin/env python
"""Offline smoke tests for Sections 313-320 post-recreation Actor BP reauthoring."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract as recreation_actual  # noqa: E402
import bp_authoring_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract as reauthoring  # noqa: E402
from test_bp_authoring_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract import build_current_section_297_304_summary  # noqa: E402


def build_current_section_305_312_summary() -> dict:
    section_297_304_summary = build_current_section_297_304_summary()
    result = recreation_actual.build_post_delete_recreation_actual_execution_result()
    contract = recreation_actual.build_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract(
        True,
        section_297_304_summary,
        result,
    )
    return recreation_actual.summarize_durable_executor_authoring_post_delete_recreation_actual_execution_batches(
        [contract]
    )


def build_current_reauthoring_result(**overrides: object) -> dict:
    result = reauthoring.build_post_recreation_actor_bp_reauthoring_actual_result()
    result.update(overrides)
    return result


def main() -> int:
    section_305_312_summary = build_current_section_305_312_summary()
    result = build_current_reauthoring_result()
    contract = reauthoring.build_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract(
        True,
        section_305_312_summary,
        result,
    )
    assert (
        contract["schema"]
        == reauthoring
        .DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_ACTOR_BP_REAUTHORING_ACTUAL_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_305_312_summary_schema_matches"] is True
    assert contract["section_305_312_summary_passed"] is True
    assert contract["section_305_312_post_delete_recreation_actual_ready"] is True
    assert contract["section_305_312_authoring_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["reauthoring_checkpoint_satisfied"] is True
    assert contract["recreated_actor_bp_target_ready"] is True
    assert contract["variable_reauthoring_executed"] is True
    assert contract["component_reauthoring_executed"] is True
    assert contract["default_tag_reauthoring_executed"] is True
    assert contract["compile_save_executed"] is True
    assert contract["reauthoring_readback_verified"] is True
    assert contract["dirty_baseline_preserved"] is True
    assert contract["destructive_outputs_closed"] is True
    assert contract["result_has_no_error"] is True
    assert contract["section_313_reauthoring_checkpoint_satisfied"] is True
    assert contract["section_314_recreated_actor_bp_target_ready"] is True
    assert contract["section_315_variable_reauthoring_executed"] is True
    assert contract["section_316_component_reauthoring_executed"] is True
    assert contract["section_317_default_tag_reauthoring_executed"] is True
    assert contract["section_318_reauthoring_compile_save_executed"] is True
    assert contract["section_319_reauthoring_readback_verified"] is True
    assert contract["section_320_reauthoring_dirty_baseline_preserved"] is True
    assert contract["post_recreation_actor_bp_reauthoring_ready"] is True
    assert contract["post_recreation_actor_bp_reauthoring_saved"] is True
    assert contract["post_recreation_actor_bp_reauthoring_readback_verified"] is True
    assert contract["variable_add_command_executed"] is True
    assert contract["component_add_command_executed"] is True
    assert contract["default_write_command_executed"] is True
    assert contract["actor_bp_authoring_save_executed"] is True
    assert contract["actor_bp_authoring_asset_write_performed"] is True
    assert contract["actor_bp_authoring_package_dirty_marked"] is True
    assert contract["actor_bp_authoring_target_dirty_after"] is False
    assert contract["actor_bp_authoring_external_dirty_preserved"] is True
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["production_path_write_allowed"] is False

    summary = reauthoring.summarize_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_count"
        ]
        == 1
    )
    expected_one_counts = (
        "section_305_312_summary_schema_matches_count",
        "section_305_312_summary_passed_count",
        "section_305_312_post_delete_recreation_actual_ready_count",
        "section_305_312_authoring_outputs_closed_count",
        "result_schema_matches_count",
        "reauthoring_checkpoint_satisfied_count",
        "recreated_actor_bp_target_ready_count",
        "variable_reauthoring_executed_count",
        "component_reauthoring_executed_count",
        "default_tag_reauthoring_executed_count",
        "compile_save_executed_count",
        "reauthoring_readback_verified_count",
        "dirty_baseline_preserved_count",
        "destructive_outputs_closed_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "variable_add_command_dispatched_count",
        "variable_add_command_executed_count",
        "component_add_command_dispatched_count",
        "component_add_command_executed_count",
        "default_write_command_dispatched_count",
        "default_write_command_executed_count",
        "actor_bp_authoring_command_dispatched_count",
        "actor_bp_authoring_command_executed_count",
        "actor_bp_authoring_compile_dispatched_count",
        "actor_bp_authoring_compile_executed_count",
        "actor_bp_authoring_save_dispatched_count",
        "actor_bp_authoring_save_executed_count",
        "actor_bp_authoring_asset_write_performed_count",
        "actor_bp_authoring_package_dirty_marked_count",
        "actor_bp_authoring_external_dirty_preserved_count",
        "section_313_reauthoring_checkpoint_satisfied_count",
        "section_314_recreated_actor_bp_target_ready_count",
        "section_315_variable_reauthoring_executed_count",
        "section_316_component_reauthoring_executed_count",
        "section_317_default_tag_reauthoring_executed_count",
        "section_318_reauthoring_compile_save_executed_count",
        "section_319_reauthoring_readback_verified_count",
        "section_320_reauthoring_dirty_baseline_preserved_count",
        "post_recreation_actor_bp_reauthoring_ready_count",
        "post_recreation_actor_bp_reauthoring_saved_count",
        "post_recreation_actor_bp_reauthoring_readback_verified_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    expected_zero_counts = (
        "actor_bp_authoring_target_dirty_after_count",
        *reauthoring.BLOCKED_POST_RECREATION_REAUTHORING_OUTPUT_COUNT_KEYS,
    )
    for key in expected_zero_counts:
        assert summary[key] == 0, key

    missing_recreation = dict(section_305_312_summary)
    missing_recreation["post_delete_recreated_actor_bp_readback_verified_count"] = 0
    missing_recreation_contract = reauthoring.build_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract(
        True,
        missing_recreation,
        result,
    )
    missing_recreation_summary = reauthoring.summarize_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batches(
        [missing_recreation_contract]
    )
    assert (
        missing_recreation_contract[
            "section_305_312_post_delete_recreation_actual_ready"
        ]
        is False
    )
    assert missing_recreation_contract["post_recreation_actor_bp_reauthoring_ready"] is False
    assert missing_recreation_summary["status"] == "failed"

    production_target_contract = reauthoring.build_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract(
        True,
        section_305_312_summary,
        build_current_reauthoring_result(
            target_asset_path="/Game/Cubeless/Unsafe/BP_DurableSaveGatePrep",
            target_under_expected_root=False,
        ),
    )
    production_target_summary = reauthoring.summarize_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batches(
        [production_target_contract]
    )
    assert production_target_contract["recreated_actor_bp_target_ready"] is False
    assert production_target_contract["post_recreation_actor_bp_reauthoring_ready"] is False
    assert production_target_summary["status"] == "failed"

    missing_variable_contract = reauthoring.build_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract(
        True,
        section_305_312_summary,
        build_current_reauthoring_result(
            variable_exists_after=False,
            scalar_default_after=0.0,
        ),
    )
    missing_variable_summary = reauthoring.summarize_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batches(
        [missing_variable_contract]
    )
    assert missing_variable_contract["variable_reauthoring_executed"] is False
    assert missing_variable_contract["reauthoring_readback_verified"] is False
    assert missing_variable_summary["status"] == "failed"

    missing_component_contract = reauthoring.build_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract(
        True,
        section_305_312_summary,
        build_current_reauthoring_result(component_exists_after=False),
    )
    missing_component_summary = reauthoring.summarize_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batches(
        [missing_component_contract]
    )
    assert missing_component_contract["component_reauthoring_executed"] is False
    assert missing_component_contract["post_recreation_actor_bp_reauthoring_ready"] is False
    assert missing_component_summary["status"] == "failed"

    dirty_changed_contract = reauthoring.build_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract(
        True,
        section_305_312_summary,
        build_current_reauthoring_result(
            external_dirty_after=("/Game/Cubeless/Unexpected",),
            external_dirty_preserved=False,
        ),
    )
    dirty_changed_summary = reauthoring.summarize_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batches(
        [dirty_changed_contract]
    )
    assert dirty_changed_contract["dirty_baseline_preserved"] is False
    assert dirty_changed_contract["post_recreation_actor_bp_reauthoring_ready"] is False
    assert dirty_changed_summary["status"] == "failed"

    destructive_contract = reauthoring.build_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract(
        True,
        section_305_312_summary,
        build_current_reauthoring_result(
            production_path_write_allowed=True,
            production_path_write_executed=True,
        ),
    )
    destructive_summary = reauthoring.summarize_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batches(
        [destructive_contract]
    )
    assert destructive_contract["destructive_outputs_closed"] is False
    assert destructive_contract["post_recreation_actor_bp_reauthoring_ready"] is False
    assert destructive_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring post-recreation Actor BP reauthoring actual batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
