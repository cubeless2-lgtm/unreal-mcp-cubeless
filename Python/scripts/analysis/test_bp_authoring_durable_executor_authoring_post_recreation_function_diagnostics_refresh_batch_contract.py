#!/usr/bin/env python
"""Offline smoke tests for Sections 329-336 post-recreation diagnostics refresh."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract as readback  # noqa: E402
import bp_authoring_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract as diagnostics  # noqa: E402
from test_bp_authoring_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract import build_current_section_313_320_summary  # noqa: E402


def build_current_section_321_328_summary() -> dict:
    section_313_320_summary = build_current_section_313_320_summary()
    result = readback.build_post_recreation_actor_bp_readback_strengthening_result()
    contract = readback.build_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract(
        True,
        section_313_320_summary,
        result,
    )
    return readback.summarize_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batches(
        [contract]
    )


def build_current_diagnostics_result(**overrides: object) -> dict:
    result = diagnostics.build_post_recreation_function_diagnostics_refresh_result()
    result.update(overrides)
    return result


def main() -> int:
    section_321_328_summary = build_current_section_321_328_summary()
    result = build_current_diagnostics_result()
    contract = diagnostics.build_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract(
        True,
        section_321_328_summary,
        result,
    )
    assert (
        contract["schema"]
        == diagnostics
        .DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_321_328_summary_schema_matches"] is True
    assert contract["section_321_328_summary_passed"] is True
    assert contract["section_321_328_post_recreation_readback_strengthened"] is True
    assert contract["section_321_328_destructive_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["diagnostics_refresh_checkpoint_satisfied"] is True
    assert contract["current_actor_bp_graph_inventory_ready"] is True
    assert contract["empty_graph_state_safely_classified"] is True
    assert contract["function_diagnostics_refreshed"] is True
    assert contract["pin_contract_diagnostics_refreshed"] is True
    assert contract["graph_layout_diagnostics_refreshed"] is True
    assert contract["diagnostics_refresh_no_write_boundary_verified"] is True
    assert contract["result_has_no_error"] is True
    assert (
        contract[
            "section_329_post_recreation_diagnostics_refresh_checkpoint_satisfied"
        ]
        is True
    )
    assert contract["section_330_current_actor_bp_graph_inventory_ready"] is True
    assert contract["section_331_empty_graph_state_safely_classified"] is True
    assert contract["section_332_function_diagnostics_refreshed"] is True
    assert contract["section_333_pin_contract_diagnostics_refreshed"] is True
    assert contract["section_334_graph_layout_diagnostics_refreshed"] is True
    assert (
        contract[
            "section_335_diagnostics_refresh_no_write_boundary_verified"
        ]
        is True
    )
    assert (
        contract[
            "section_336_post_recreation_function_diagnostics_refresh_release_ready"
        ]
        is True
    )
    assert contract["post_recreation_function_diagnostics_refreshed"] is True
    assert contract["post_recreation_empty_graph_state_verified"] is True
    assert contract["final_durable_release_ready"] is True

    summary = diagnostics.summarize_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_post_recreation_function_diagnostics_refresh_batch_count"
        ]
        == 1
    )
    expected_one_counts = (
        "section_321_328_summary_schema_matches_count",
        "section_321_328_summary_passed_count",
        "section_321_328_post_recreation_readback_strengthened_count",
        "section_321_328_destructive_outputs_closed_count",
        "result_schema_matches_count",
        "diagnostics_refresh_checkpoint_satisfied_count",
        "current_actor_bp_graph_inventory_ready_count",
        "empty_graph_state_safely_classified_count",
        "function_diagnostics_refreshed_count",
        "pin_contract_diagnostics_refreshed_count",
        "graph_layout_diagnostics_refreshed_count",
        "diagnostics_refresh_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_329_post_recreation_diagnostics_refresh_checkpoint_satisfied_count",
        "section_330_current_actor_bp_graph_inventory_ready_count",
        "section_331_empty_graph_state_safely_classified_count",
        "section_332_function_diagnostics_refreshed_count",
        "section_333_pin_contract_diagnostics_refreshed_count",
        "section_334_graph_layout_diagnostics_refreshed_count",
        "section_335_diagnostics_refresh_no_write_boundary_verified_count",
        "section_336_post_recreation_function_diagnostics_refresh_release_ready_count",
        "post_recreation_function_diagnostics_refreshed_count",
        "post_recreation_empty_graph_state_verified_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in diagnostics.BLOCKED_FUNCTION_DIAGNOSTICS_REFRESH_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key

    missing_upstream = dict(section_321_328_summary)
    missing_upstream["post_recreation_actor_bp_readback_strengthened_count"] = 0
    missing_upstream_contract = diagnostics.build_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = diagnostics.summarize_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_321_328_post_recreation_readback_strengthened"
        ]
        is False
    )
    assert (
        missing_upstream_contract[
            "post_recreation_function_diagnostics_refreshed"
        ]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    dirty_read_contract = diagnostics.build_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract(
        True,
        section_321_328_summary,
        build_current_diagnostics_result(
            dirty_content_after_readback=[
                diagnostics.DEFAULT_TARGET_ASSET_PATH,
            ],
            target_dirty_after_readback=True,
        ),
    )
    dirty_read_summary = diagnostics.summarize_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batches(
        [dirty_read_contract]
    )
    assert (
        dirty_read_contract[
            "diagnostics_refresh_no_write_boundary_verified"
        ]
        is False
    )
    assert dirty_read_summary["status"] == "failed"

    non_empty_unclassified_contract = diagnostics.build_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract(
        True,
        section_321_328_summary,
        build_current_diagnostics_result(
            function_graph_count=1,
            empty_graph_state_safely_classified=False,
        ),
    )
    non_empty_unclassified_summary = diagnostics.summarize_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batches(
        [non_empty_unclassified_contract]
    )
    assert (
        non_empty_unclassified_contract["empty_graph_state_safely_classified"]
        is False
    )
    assert non_empty_unclassified_summary["status"] == "failed"

    missing_function_refresh_contract = diagnostics.build_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract(
        True,
        section_321_328_summary,
        build_current_diagnostics_result(
            function_diagnostics_refreshed=False,
            diagnostic_refresh_categories=("empty_graph_state_classification",),
        ),
    )
    missing_function_refresh_summary = diagnostics.summarize_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batches(
        [missing_function_refresh_contract]
    )
    assert (
        missing_function_refresh_contract["function_diagnostics_refreshed"]
        is False
    )
    assert missing_function_refresh_summary["status"] == "failed"

    repair_attempt_contract = diagnostics.build_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract(
        True,
        section_321_328_summary,
        build_current_diagnostics_result(
            graph_repair_command_dispatched=True,
            graph_layout_mutation_performed=True,
            node_position_write_performed=True,
        ),
    )
    repair_attempt_summary = diagnostics.summarize_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batches(
        [repair_attempt_contract]
    )
    assert (
        repair_attempt_contract[
            "diagnostics_refresh_no_write_boundary_verified"
        ]
        is False
    )
    assert repair_attempt_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring post-recreation function diagnostics refresh batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
