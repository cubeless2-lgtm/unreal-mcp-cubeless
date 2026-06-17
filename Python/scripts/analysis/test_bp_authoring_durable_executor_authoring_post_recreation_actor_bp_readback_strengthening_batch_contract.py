#!/usr/bin/env python
"""Offline smoke tests for Sections 321-328 post-recreation Actor BP readback strengthening."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract as readback  # noqa: E402
import bp_authoring_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract as reauthoring  # noqa: E402
from test_bp_authoring_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract import build_current_section_305_312_summary  # noqa: E402


def build_current_section_313_320_summary() -> dict:
    section_305_312_summary = build_current_section_305_312_summary()
    result = reauthoring.build_post_recreation_actor_bp_reauthoring_actual_result()
    contract = reauthoring.build_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract(
        True,
        section_305_312_summary,
        result,
    )
    return reauthoring.summarize_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batches(
        [contract]
    )


def build_current_readback_result(**overrides: object) -> dict:
    result = readback.build_post_recreation_actor_bp_readback_strengthening_result()
    result.update(overrides)
    return result


def main() -> int:
    section_313_320_summary = build_current_section_313_320_summary()
    result = build_current_readback_result()
    contract = readback.build_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract(
        True,
        section_313_320_summary,
        result,
    )
    assert (
        contract["schema"]
        == readback
        .DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_ACTOR_BP_READBACK_STRENGTHENING_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_313_320_summary_schema_matches"] is True
    assert contract["section_313_320_summary_passed"] is True
    assert contract["section_313_320_post_recreation_reauthoring_ready"] is True
    assert contract["section_313_320_destructive_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["readback_strengthening_checkpoint_satisfied"] is True
    assert contract["recreated_actor_bp_readback_route_ready"] is True
    assert contract["variable_default_reread_verified"] is True
    assert contract["default_tag_reread_verified"] is True
    assert contract["raw_component_duplicate_handles_detected"] is True
    assert contract["unique_component_identity_verified"] is True
    assert contract["readback_no_write_dirty_boundary_verified"] is True
    assert contract["result_has_no_error"] is True
    assert contract["section_321_readback_strengthening_checkpoint_satisfied"] is True
    assert contract["section_322_recreated_actor_bp_readback_route_ready"] is True
    assert contract["section_323_variable_default_reread_verified"] is True
    assert contract["section_324_default_tag_reread_verified"] is True
    assert contract["section_325_raw_component_duplicate_handles_detected"] is True
    assert contract["section_326_unique_component_identity_verified"] is True
    assert contract["section_327_readback_no_write_dirty_boundary_verified"] is True
    assert contract["section_328_readback_strengthening_release_ready"] is True
    assert contract["post_recreation_actor_bp_readback_strengthened"] is True
    assert contract["post_recreation_actor_bp_unique_component_identity_verified"] is True
    assert contract["final_durable_release_ready"] is True

    summary = readback.summarize_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_count"
        ]
        == 1
    )
    expected_one_counts = (
        "section_313_320_summary_schema_matches_count",
        "section_313_320_summary_passed_count",
        "section_313_320_post_recreation_reauthoring_ready_count",
        "section_313_320_destructive_outputs_closed_count",
        "result_schema_matches_count",
        "readback_strengthening_checkpoint_satisfied_count",
        "recreated_actor_bp_readback_route_ready_count",
        "variable_default_reread_verified_count",
        "default_tag_reread_verified_count",
        "raw_component_duplicate_handles_detected_count",
        "unique_component_identity_verified_count",
        "readback_no_write_dirty_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_321_readback_strengthening_checkpoint_satisfied_count",
        "section_322_recreated_actor_bp_readback_route_ready_count",
        "section_323_variable_default_reread_verified_count",
        "section_324_default_tag_reread_verified_count",
        "section_325_raw_component_duplicate_handles_detected_count",
        "section_326_unique_component_identity_verified_count",
        "section_327_readback_no_write_dirty_boundary_verified_count",
        "section_328_readback_strengthening_release_ready_count",
        "post_recreation_actor_bp_readback_strengthened_count",
        "post_recreation_actor_bp_unique_component_identity_verified_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in readback.BLOCKED_READBACK_STRENGTHENING_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key

    missing_upstream = dict(section_313_320_summary)
    missing_upstream["post_recreation_actor_bp_reauthoring_readback_verified_count"] = 0
    missing_upstream_contract = readback.build_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = readback.summarize_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batches(
        [missing_upstream_contract]
    )
    assert missing_upstream_contract["section_313_320_post_recreation_reauthoring_ready"] is False
    assert missing_upstream_contract["post_recreation_actor_bp_readback_strengthened"] is False
    assert missing_upstream_summary["status"] == "failed"

    missing_variable_contract = readback.build_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract(
        True,
        section_313_320_summary,
        build_current_readback_result(
            variable_readback_verified=False,
            scalar_default_after=0.0,
        ),
    )
    missing_variable_summary = readback.summarize_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batches(
        [missing_variable_contract]
    )
    assert missing_variable_contract["variable_default_reread_verified"] is False
    assert missing_variable_contract["post_recreation_actor_bp_readback_strengthened"] is False
    assert missing_variable_summary["status"] == "failed"

    no_duplicate_contract = readback.build_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract(
        True,
        section_313_320_summary,
        build_current_readback_result(
            matching_component_handle_count=1,
            raw_duplicate_component_handles_detected=False,
        ),
    )
    no_duplicate_summary = readback.summarize_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batches(
        [no_duplicate_contract]
    )
    assert no_duplicate_contract["raw_component_duplicate_handles_detected"] is False
    assert no_duplicate_contract["post_recreation_actor_bp_readback_strengthened"] is False
    assert no_duplicate_summary["status"] == "failed"

    wrong_identity_contract = readback.build_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract(
        True,
        section_313_320_summary,
        build_current_readback_result(unique_component_name="OtherComponent"),
    )
    wrong_identity_summary = readback.summarize_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batches(
        [wrong_identity_contract]
    )
    assert wrong_identity_contract["unique_component_identity_verified"] is False
    assert wrong_identity_contract["post_recreation_actor_bp_readback_strengthened"] is False
    assert wrong_identity_summary["status"] == "failed"

    write_attempt_contract = readback.build_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract(
        True,
        section_313_320_summary,
        build_current_readback_result(
            actor_bp_authoring_save_executed=True,
            actor_bp_authoring_asset_write_performed=True,
            target_dirty_after_readback=True,
        ),
    )
    write_attempt_summary = readback.summarize_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batches(
        [write_attempt_contract]
    )
    assert write_attempt_contract["readback_no_write_dirty_boundary_verified"] is False
    assert write_attempt_contract["post_recreation_actor_bp_readback_strengthened"] is False
    assert write_attempt_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring post-recreation Actor BP readback strengthening batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
