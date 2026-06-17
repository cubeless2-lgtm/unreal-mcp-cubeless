#!/usr/bin/env python
"""Offline smoke tests for Sections 337-344 broader non-Actor Blueprint dry-run."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract as broader  # noqa: E402
import bp_authoring_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract as diagnostics  # noqa: E402
from test_bp_authoring_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract import build_current_section_321_328_summary  # noqa: E402


def build_current_section_329_336_summary() -> dict:
    section_321_328_summary = build_current_section_321_328_summary()
    result = diagnostics.build_post_recreation_function_diagnostics_refresh_result()
    contract = diagnostics.build_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract(
        True,
        section_321_328_summary,
        result,
    )
    return diagnostics.summarize_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batches(
        [contract]
    )


def build_current_dry_run_result(**overrides: object) -> dict:
    result = broader.build_broader_non_actor_blueprint_dry_run_result()
    result.update(overrides)
    return result


def main() -> int:
    section_329_336_summary = build_current_section_329_336_summary()
    result = build_current_dry_run_result()
    contract = broader.build_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract(
        True,
        section_329_336_summary,
        result,
    )
    assert (
        contract["schema"]
        == broader
        .DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_329_336_summary_schema_matches"] is True
    assert contract["section_329_336_summary_passed"] is True
    assert contract["section_329_336_post_recreation_diagnostics_refreshed"] is True
    assert contract["section_329_336_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["broader_blueprint_dry_run_checkpoint_satisfied"] is True
    assert contract["broader_blueprint_dry_run_scope_verified"] is True
    assert contract["user_widget_authoring_plan_classified"] is True
    assert contract["data_asset_authoring_plan_classified"] is True
    assert contract["anim_blueprint_authoring_plan_classified"] is True
    assert contract["class_specific_prerequisites_recorded"] is True
    assert contract["actual_non_actor_blueprint_creation_blocked"] is True
    assert contract["broader_blueprint_dry_run_no_write_boundary_verified"] is True
    assert contract["result_has_no_error"] is True
    assert contract["section_337_broader_blueprint_dry_run_checkpoint_satisfied"] is True
    assert contract["section_338_user_widget_authoring_plan_classified"] is True
    assert contract["section_339_data_asset_authoring_plan_classified"] is True
    assert contract["section_340_anim_blueprint_authoring_plan_classified"] is True
    assert contract["section_341_class_specific_prerequisites_recorded"] is True
    assert contract["section_342_actual_non_actor_blueprint_creation_blocked"] is True
    assert (
        contract[
            "section_343_broader_blueprint_dry_run_no_write_boundary_verified"
        ]
        is True
    )
    assert (
        contract[
            "section_344_broader_non_actor_blueprint_dry_run_release_ready"
        ]
        is True
    )
    assert contract["broader_non_actor_blueprint_dry_run_ready"] is True
    assert contract["broader_blueprint_actual_authoring_still_blocked"] is True
    assert contract["final_durable_release_ready"] is True

    summary = broader.summarize_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_broader_non_actor_blueprint_dry_run_batch_count"
        ]
        == 1
    )
    expected_one_counts = (
        "section_329_336_summary_schema_matches_count",
        "section_329_336_summary_passed_count",
        "section_329_336_post_recreation_diagnostics_refreshed_count",
        "section_329_336_outputs_closed_count",
        "result_schema_matches_count",
        "broader_blueprint_dry_run_checkpoint_satisfied_count",
        "broader_blueprint_dry_run_scope_verified_count",
        "user_widget_authoring_plan_classified_count",
        "data_asset_authoring_plan_classified_count",
        "anim_blueprint_authoring_plan_classified_count",
        "class_specific_prerequisites_recorded_count",
        "actual_non_actor_blueprint_creation_blocked_count",
        "broader_blueprint_dry_run_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_337_broader_blueprint_dry_run_checkpoint_satisfied_count",
        "section_338_user_widget_authoring_plan_classified_count",
        "section_339_data_asset_authoring_plan_classified_count",
        "section_340_anim_blueprint_authoring_plan_classified_count",
        "section_341_class_specific_prerequisites_recorded_count",
        "section_342_actual_non_actor_blueprint_creation_blocked_count",
        "section_343_broader_blueprint_dry_run_no_write_boundary_verified_count",
        "section_344_broader_non_actor_blueprint_dry_run_release_ready_count",
        "broader_non_actor_blueprint_dry_run_ready_count",
        "broader_blueprint_actual_authoring_still_blocked_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in broader.BLOCKED_BROADER_NON_ACTOR_BLUEPRINT_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key

    missing_upstream = dict(section_329_336_summary)
    missing_upstream["post_recreation_function_diagnostics_refreshed_count"] = 0
    missing_upstream_contract = broader.build_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = broader.summarize_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_329_336_post_recreation_diagnostics_refreshed"
        ]
        is False
    )
    assert missing_upstream_contract["broader_non_actor_blueprint_dry_run_ready"] is False
    assert missing_upstream_summary["status"] == "failed"

    production_path_contract = broader.build_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract(
        True,
        section_329_336_summary,
        build_current_dry_run_result(
            planned_output_asset_paths=(
                "/Game/Production/WBP_DurableSaveGatePrep_DryRun",
                broader.DEFAULT_PLANNED_OUTPUT_ASSET_PATHS[1],
                broader.DEFAULT_PLANNED_OUTPUT_ASSET_PATHS[2],
            ),
        ),
    )
    production_path_summary = broader.summarize_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batches(
        [production_path_contract]
    )
    assert production_path_contract["broader_blueprint_dry_run_scope_verified"] is False
    assert production_path_summary["status"] == "failed"

    missing_widget_contract = broader.build_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract(
        True,
        section_329_336_summary,
        build_current_dry_run_result(
            user_widget_plan_classified=False,
            user_widget_parent_class="Actor",
        ),
    )
    missing_widget_summary = broader.summarize_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batches(
        [missing_widget_contract]
    )
    assert missing_widget_contract["user_widget_authoring_plan_classified"] is False
    assert missing_widget_summary["status"] == "failed"

    anim_without_skeleton_block_contract = broader.build_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract(
        True,
        section_329_336_summary,
        build_current_dry_run_result(
            anim_blueprint_missing_skeleton_blocks_execution=False,
        ),
    )
    anim_without_skeleton_block_summary = broader.summarize_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batches(
        [anim_without_skeleton_block_contract]
    )
    assert (
        anim_without_skeleton_block_contract[
            "anim_blueprint_authoring_plan_classified"
        ]
        is False
    )
    assert anim_without_skeleton_block_summary["status"] == "failed"

    actual_create_contract = broader.build_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract(
        True,
        section_329_336_summary,
        build_current_dry_run_result(
            actual_non_actor_blueprint_authoring_allowed=True,
            user_widget_blueprint_create_command_dispatched=True,
            non_actor_blueprint_asset_write_performed=True,
            dirty_content_after_dry_run=[
                broader.DEFAULT_PLANNED_OUTPUT_ASSET_PATHS[0],
            ],
        ),
    )
    actual_create_summary = broader.summarize_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batches(
        [actual_create_contract]
    )
    assert actual_create_contract["actual_non_actor_blueprint_creation_blocked"] is False
    assert (
        actual_create_contract[
            "broader_blueprint_dry_run_no_write_boundary_verified"
        ]
        is False
    )
    assert actual_create_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring broader non-Actor Blueprint dry-run batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
