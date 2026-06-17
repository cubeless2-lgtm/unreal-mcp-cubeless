#!/usr/bin/env python
"""Offline smoke tests for Sections 369-376 live MCP route preflight."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract as live_route  # noqa: E402
import bp_authoring_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract as node_route  # noqa: E402
from test_bp_authoring_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract import build_current_section_353_360_summary  # noqa: E402


def build_current_section_361_368_summary() -> dict:
    section_353_360_summary = build_current_section_353_360_summary()
    result = node_route.build_node_level_graph_fixture_route_preflight_result()
    contract = node_route.build_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract(
        True,
        section_353_360_summary,
        result,
    )
    return node_route.summarize_durable_executor_authoring_node_level_graph_fixture_route_preflight_batches(
        [contract]
    )


def build_current_live_route_result(**overrides: object) -> dict:
    result = live_route.build_correct_project_live_mcp_route_preflight_result()
    result.update(overrides)
    return result


def main() -> int:
    section_361_368_summary = build_current_section_361_368_summary()
    result = build_current_live_route_result()
    contract = live_route.build_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract(
        True,
        section_361_368_summary,
        result,
    )
    assert (
        contract["schema"]
        == live_route
        .DURABLE_EXECUTOR_AUTHORING_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_361_368_summary_schema_matches"] is True
    assert contract["section_361_368_summary_passed"] is True
    assert contract["section_361_368_node_level_route_preflight_ready"] is True
    assert contract["section_361_368_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["correct_project_live_mcp_route_checkpoint_satisfied"] is True
    assert contract["mcp_config_preflight_verified"] is True
    assert contract["sibling_server_path_verified"] is True
    assert contract["live_bridge_read_only_probe_recorded"] is True
    assert contract["live_bridge_correct_project_not_verified"] is True
    assert contract["live_mcp_activation_outputs_blocked"] is True
    assert (
        contract["correct_project_live_mcp_route_no_write_boundary_verified"]
        is True
    )
    assert contract["result_has_no_error"] is True
    assert (
        contract[
            "section_369_correct_project_live_mcp_route_checkpoint_satisfied"
        ]
        is True
    )
    assert contract["section_370_mcp_config_preflight_verified"] is True
    assert contract["section_371_sibling_server_path_verified"] is True
    assert contract["section_372_live_bridge_read_only_probe_recorded"] is True
    assert contract["section_373_live_bridge_correct_project_not_verified"] is True
    assert contract["section_374_live_mcp_activation_outputs_blocked"] is True
    assert (
        contract[
            "section_375_correct_project_live_mcp_route_no_write_boundary_verified"
        ]
        is True
    )
    assert (
        contract[
            "section_376_correct_project_live_mcp_route_preflight_release_ready"
        ]
        is True
    )
    assert contract["correct_project_live_mcp_route_preflight_ready"] is True
    assert contract["correct_project_live_mcp_activation_still_blocked"] is True
    assert contract["final_durable_release_ready"] is True

    summary = live_route.summarize_durable_executor_authoring_correct_project_live_mcp_route_preflight_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    expected_one_counts = (
        "durable_requested_executor_authoring_correct_project_live_mcp_route_preflight_batch_count",
        "section_361_368_summary_schema_matches_count",
        "section_361_368_summary_passed_count",
        "section_361_368_node_level_route_preflight_ready_count",
        "section_361_368_outputs_closed_count",
        "result_schema_matches_count",
        "correct_project_live_mcp_route_checkpoint_satisfied_count",
        "mcp_config_preflight_verified_count",
        "sibling_server_path_verified_count",
        "live_bridge_read_only_probe_recorded_count",
        "live_bridge_correct_project_not_verified_count",
        "live_mcp_activation_outputs_blocked_count",
        "correct_project_live_mcp_route_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_369_correct_project_live_mcp_route_checkpoint_satisfied_count",
        "section_370_mcp_config_preflight_verified_count",
        "section_371_sibling_server_path_verified_count",
        "section_372_live_bridge_read_only_probe_recorded_count",
        "section_373_live_bridge_correct_project_not_verified_count",
        "section_374_live_mcp_activation_outputs_blocked_count",
        "section_375_correct_project_live_mcp_route_no_write_boundary_verified_count",
        "section_376_correct_project_live_mcp_route_preflight_release_ready_count",
        "correct_project_live_mcp_route_preflight_ready_count",
        "correct_project_live_mcp_activation_still_blocked_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in (
        live_route
        .BLOCKED_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key

    missing_upstream = dict(section_361_368_summary)
    missing_upstream["node_level_graph_fixture_route_preflight_ready_count"] = 0
    missing_upstream_contract = live_route.build_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = live_route.summarize_durable_executor_authoring_correct_project_live_mcp_route_preflight_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_361_368_node_level_route_preflight_ready"
        ]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    bad_config_contract = live_route.build_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract(
        True,
        section_361_368_summary,
        build_current_live_route_result(mcp_command="python", mcp_command_matches=False),
    )
    bad_config_summary = live_route.summarize_durable_executor_authoring_correct_project_live_mcp_route_preflight_batches(
        [bad_config_contract]
    )
    assert bad_config_contract["mcp_config_preflight_verified"] is False
    assert bad_config_summary["status"] == "failed"

    bridge_verified_contract = live_route.build_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract(
        True,
        section_361_368_summary,
        build_current_live_route_result(
            live_bridge_fixture_found=True,
            live_bridge_correct_project_verified=True,
            live_bridge_correct_project_not_verified=False,
            live_mcp_activation_still_blocked=False,
            live_bridge_error="",
        ),
    )
    bridge_verified_summary = live_route.summarize_durable_executor_authoring_correct_project_live_mcp_route_preflight_batches(
        [bridge_verified_contract]
    )
    assert (
        bridge_verified_contract["live_bridge_correct_project_not_verified"]
        is False
    )
    assert bridge_verified_summary["status"] == "failed"

    activation_contract = live_route.build_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract(
        True,
        section_361_368_summary,
        build_current_live_route_result(
            live_mcp_activation_command_dispatched=True,
            node_authoring_command_dispatched=True,
        ),
    )
    activation_summary = live_route.summarize_durable_executor_authoring_correct_project_live_mcp_route_preflight_batches(
        [activation_contract]
    )
    assert activation_contract["live_mcp_activation_outputs_blocked"] is False
    assert activation_summary["status"] == "failed"

    dirty_contract = live_route.build_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract(
        True,
        section_361_368_summary,
        build_current_live_route_result(target_dirty_after=True),
    )
    dirty_summary = live_route.summarize_durable_executor_authoring_correct_project_live_mcp_route_preflight_batches(
        [dirty_contract]
    )
    assert (
        dirty_contract[
            "correct_project_live_mcp_route_no_write_boundary_verified"
        ]
        is False
    )
    assert dirty_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring correct-project live MCP route preflight batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
