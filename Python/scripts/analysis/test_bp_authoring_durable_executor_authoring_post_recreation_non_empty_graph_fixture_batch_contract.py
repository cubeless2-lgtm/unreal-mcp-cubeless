#!/usr/bin/env python
"""Offline smoke tests for Sections 353-360 non-empty graph fixture."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract as graph_repair  # noqa: E402
import bp_authoring_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract as fixture  # noqa: E402
from test_bp_authoring_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract import build_current_section_337_344_summary  # noqa: E402


def build_current_section_345_352_summary() -> dict:
    section_337_344_summary = build_current_section_337_344_summary()
    result = graph_repair.build_graph_repair_execution_dry_run_result()
    contract = graph_repair.build_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract(
        True,
        section_337_344_summary,
        result,
    )
    return graph_repair.summarize_durable_executor_authoring_graph_repair_execution_dry_run_batches(
        [contract]
    )


def build_current_fixture_result(**overrides: object) -> dict:
    result = fixture.build_post_recreation_non_empty_graph_fixture_result()
    result.update(overrides)
    return result


def main() -> int:
    section_345_352_summary = build_current_section_345_352_summary()
    result = build_current_fixture_result()
    contract = fixture.build_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract(
        True,
        section_345_352_summary,
        result,
    )
    assert (
        contract["schema"]
        == fixture
        .DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_NON_EMPTY_GRAPH_FIXTURE_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_345_352_summary_schema_matches"] is True
    assert contract["section_345_352_summary_passed"] is True
    assert contract["section_345_352_graph_repair_execution_dry_run_ready"] is True
    assert contract["section_345_352_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["non_empty_graph_fixture_checkpoint_satisfied"] is True
    assert contract["fixture_target_scope_verified"] is True
    assert contract["fixture_actor_blueprint_create_or_update_executed"] is True
    assert contract["function_graph_inventory_non_empty_verified"] is True
    assert contract["fixture_compile_save_readback_verified"] is True
    assert contract["node_level_repair_still_blocked"] is True
    assert contract["non_fixture_outputs_closed"] is True
    assert contract["result_has_no_error"] is True
    assert contract["section_353_non_empty_graph_fixture_checkpoint_satisfied"] is True
    assert contract["section_354_fixture_target_scope_verified"] is True
    assert (
        contract[
            "section_355_fixture_actor_blueprint_create_or_update_executed"
        ]
        is True
    )
    assert (
        contract[
            "section_356_function_graph_inventory_non_empty_verified"
        ]
        is True
    )
    assert contract["section_357_fixture_compile_save_readback_verified"] is True
    assert contract["section_358_node_level_repair_still_blocked"] is True
    assert contract["section_359_non_fixture_outputs_closed"] is True
    assert contract["section_360_non_empty_graph_fixture_release_ready"] is True
    assert contract["post_recreation_non_empty_graph_fixture_ready"] is True
    assert (
        contract["post_recreation_node_level_repair_fixture_still_missing"]
        is True
    )
    assert contract["final_durable_release_ready"] is True

    summary = fixture.summarize_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_post_recreation_non_empty_graph_fixture_batch_count"
        ]
        == 1
    )
    expected_one_counts = (
        "section_345_352_summary_schema_matches_count",
        "section_345_352_summary_passed_count",
        "section_345_352_graph_repair_execution_dry_run_ready_count",
        "section_345_352_outputs_closed_count",
        "result_schema_matches_count",
        "non_empty_graph_fixture_checkpoint_satisfied_count",
        "fixture_target_scope_verified_count",
        "fixture_actor_blueprint_create_or_update_executed_count",
        "function_graph_inventory_non_empty_verified_count",
        "fixture_compile_save_readback_verified_count",
        "node_level_repair_still_blocked_count",
        "non_fixture_outputs_closed_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_353_non_empty_graph_fixture_checkpoint_satisfied_count",
        "section_354_fixture_target_scope_verified_count",
        "section_355_fixture_actor_blueprint_create_or_update_executed_count",
        "section_356_function_graph_inventory_non_empty_verified_count",
        "section_357_fixture_compile_save_readback_verified_count",
        "section_358_node_level_repair_still_blocked_count",
        "section_359_non_fixture_outputs_closed_count",
        "section_360_non_empty_graph_fixture_release_ready_count",
        "post_recreation_non_empty_graph_fixture_ready_count",
        "post_recreation_node_level_repair_fixture_still_missing_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in fixture.BLOCKED_NON_EMPTY_GRAPH_FIXTURE_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key

    missing_upstream = dict(section_345_352_summary)
    missing_upstream["graph_repair_execution_dry_run_ready_count"] = 0
    missing_upstream_contract = fixture.build_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = fixture.summarize_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_345_352_graph_repair_execution_dry_run_ready"
        ]
        is False
    )
    assert (
        missing_upstream_contract["post_recreation_non_empty_graph_fixture_ready"]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    production_path_contract = fixture.build_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract(
        True,
        section_345_352_summary,
        build_current_fixture_result(
            fixture_asset_path="/Game/Production/BP_BadGraphFixture",
            fixture_under_expected_root=False,
        ),
    )
    production_path_summary = fixture.summarize_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batches(
        [production_path_contract]
    )
    assert production_path_contract["fixture_target_scope_verified"] is False
    assert production_path_summary["status"] == "failed"

    missing_graph_contract = fixture.build_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract(
        True,
        section_345_352_summary,
        build_current_fixture_result(
            function_graph_exists_after=False,
            function_graph_count_after=0,
            function_graph_inventory_non_empty_after=False,
        ),
    )
    missing_graph_summary = fixture.summarize_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batches(
        [missing_graph_contract]
    )
    assert (
        missing_graph_contract["function_graph_inventory_non_empty_verified"]
        is False
    )
    assert missing_graph_summary["status"] == "failed"

    node_level_attempt_contract = fixture.build_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract(
        True,
        section_345_352_summary,
        build_current_fixture_result(
            function_graph_node_count_after=1,
            node_level_repair_fixture_ready=True,
            node_position_write_performed=True,
        ),
    )
    node_level_attempt_summary = fixture.summarize_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batches(
        [node_level_attempt_contract]
    )
    assert node_level_attempt_contract["node_level_repair_still_blocked"] is False
    assert node_level_attempt_summary["status"] == "failed"

    dirty_fixture_contract = fixture.build_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract(
        True,
        section_345_352_summary,
        build_current_fixture_result(target_dirty_after=True),
    )
    dirty_fixture_summary = fixture.summarize_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batches(
        [dirty_fixture_contract]
    )
    assert dirty_fixture_contract["fixture_compile_save_readback_verified"] is False
    assert dirty_fixture_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring post-recreation non-empty graph fixture batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
