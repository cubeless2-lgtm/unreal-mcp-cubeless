#!/usr/bin/env python
"""Offline smoke tests for Sections 361-368 node-level route preflight."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract as node_route  # noqa: E402
import bp_authoring_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract as non_empty_fixture  # noqa: E402
from test_bp_authoring_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract import build_current_section_345_352_summary  # noqa: E402


def build_current_section_353_360_summary() -> dict:
    section_345_352_summary = build_current_section_345_352_summary()
    result = non_empty_fixture.build_post_recreation_non_empty_graph_fixture_result()
    contract = non_empty_fixture.build_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract(
        True,
        section_345_352_summary,
        result,
    )
    return non_empty_fixture.summarize_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batches(
        [contract]
    )


def build_current_node_route_result(**overrides: object) -> dict:
    result = node_route.build_node_level_graph_fixture_route_preflight_result()
    result.update(overrides)
    return result


def main() -> int:
    section_353_360_summary = build_current_section_353_360_summary()
    result = build_current_node_route_result()
    contract = node_route.build_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract(
        True,
        section_353_360_summary,
        result,
    )
    assert (
        contract["schema"]
        == node_route
        .DURABLE_EXECUTOR_AUTHORING_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_353_360_summary_schema_matches"] is True
    assert contract["section_353_360_summary_passed"] is True
    assert contract["section_353_360_non_empty_graph_fixture_ready"] is True
    assert contract["section_353_360_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["node_level_route_preflight_checkpoint_satisfied"] is True
    assert contract["fixture_target_scope_verified"] is True
    assert contract["headless_fixture_readback_verified"] is True
    assert contract["python_node_object_construction_probe_recorded"] is True
    assert contract["python_node_mutation_api_absent_verified"] is True
    assert contract["live_mcp_correct_project_route_blocked"] is True
    assert contract["actual_node_authoring_outputs_blocked"] is True
    assert contract["node_level_preflight_no_write_boundary_verified"] is True
    assert contract["result_has_no_error"] is True
    assert (
        contract["section_361_node_level_route_preflight_checkpoint_satisfied"]
        is True
    )
    assert contract["section_362_headless_fixture_readback_verified"] is True
    assert (
        contract["section_363_python_node_object_construction_probe_recorded"]
        is True
    )
    assert (
        contract["section_364_python_node_mutation_api_absent_verified"]
        is True
    )
    assert contract["section_365_live_mcp_correct_project_route_blocked"] is True
    assert contract["section_366_actual_node_authoring_outputs_blocked"] is True
    assert (
        contract["section_367_node_level_preflight_no_write_boundary_verified"]
        is True
    )
    assert (
        contract[
            "section_368_node_level_graph_fixture_route_preflight_release_ready"
        ]
        is True
    )
    assert contract["node_level_graph_fixture_route_preflight_ready"] is True
    assert contract["node_level_actual_fixture_still_blocked"] is True
    assert contract["final_durable_release_ready"] is True

    summary = node_route.summarize_durable_executor_authoring_node_level_graph_fixture_route_preflight_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    expected_one_counts = (
        "durable_requested_executor_authoring_node_level_graph_fixture_route_preflight_batch_count",
        "section_353_360_summary_schema_matches_count",
        "section_353_360_summary_passed_count",
        "section_353_360_non_empty_graph_fixture_ready_count",
        "section_353_360_outputs_closed_count",
        "result_schema_matches_count",
        "node_level_route_preflight_checkpoint_satisfied_count",
        "fixture_target_scope_verified_count",
        "headless_fixture_readback_verified_count",
        "python_node_object_construction_probe_recorded_count",
        "python_node_mutation_api_absent_verified_count",
        "live_mcp_correct_project_route_blocked_count",
        "actual_node_authoring_outputs_blocked_count",
        "node_level_preflight_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_361_node_level_route_preflight_checkpoint_satisfied_count",
        "section_362_headless_fixture_readback_verified_count",
        "section_363_python_node_object_construction_probe_recorded_count",
        "section_364_python_node_mutation_api_absent_verified_count",
        "section_365_live_mcp_correct_project_route_blocked_count",
        "section_366_actual_node_authoring_outputs_blocked_count",
        "section_367_node_level_preflight_no_write_boundary_verified_count",
        "section_368_node_level_graph_fixture_route_preflight_release_ready_count",
        "node_level_graph_fixture_route_preflight_ready_count",
        "node_level_actual_fixture_still_blocked_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in (
        node_route
        .BLOCKED_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key

    missing_upstream = dict(section_353_360_summary)
    missing_upstream["post_recreation_non_empty_graph_fixture_ready_count"] = 0
    missing_upstream_contract = node_route.build_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = node_route.summarize_durable_executor_authoring_node_level_graph_fixture_route_preflight_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_353_360_non_empty_graph_fixture_ready"
        ]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    python_api_open_contract = node_route.build_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract(
        True,
        section_353_360_summary,
        build_current_node_route_result(
            python_node_position_api_available=True,
            python_allocate_default_pins_api_available=True,
        ),
    )
    python_api_open_summary = node_route.summarize_durable_executor_authoring_node_level_graph_fixture_route_preflight_batches(
        [python_api_open_contract]
    )
    assert (
        python_api_open_contract["python_node_mutation_api_absent_verified"]
        is False
    )
    assert python_api_open_summary["status"] == "failed"

    live_route_open_contract = node_route.build_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract(
        True,
        section_353_360_summary,
        build_current_node_route_result(
            live_mcp_fixture_found=True,
            live_mcp_route_correct_project_verified=True,
            live_mcp_node_authoring_route_blocked=False,
            live_mcp_error="",
        ),
    )
    live_route_open_summary = node_route.summarize_durable_executor_authoring_node_level_graph_fixture_route_preflight_batches(
        [live_route_open_contract]
    )
    assert (
        live_route_open_contract["live_mcp_correct_project_route_blocked"]
        is False
    )
    assert live_route_open_summary["status"] == "failed"

    node_write_contract = node_route.build_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract(
        True,
        section_353_360_summary,
        build_current_node_route_result(
            node_authoring_command_dispatched=True,
            add_blueprint_call_function_node_executed=True,
            graph_node_added=True,
        ),
    )
    node_write_summary = node_route.summarize_durable_executor_authoring_node_level_graph_fixture_route_preflight_batches(
        [node_write_contract]
    )
    assert node_write_contract["actual_node_authoring_outputs_blocked"] is False
    assert node_write_summary["status"] == "failed"

    dirty_contract = node_route.build_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract(
        True,
        section_353_360_summary,
        build_current_node_route_result(target_dirty_after=True),
    )
    dirty_summary = node_route.summarize_durable_executor_authoring_node_level_graph_fixture_route_preflight_batches(
        [dirty_contract]
    )
    assert (
        dirty_contract["node_level_preflight_no_write_boundary_verified"]
        is False
    )
    assert dirty_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring node-level graph fixture route preflight batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
