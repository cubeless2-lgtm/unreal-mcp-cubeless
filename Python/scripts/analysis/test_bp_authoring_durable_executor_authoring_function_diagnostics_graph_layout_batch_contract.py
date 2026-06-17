#!/usr/bin/env python
"""Offline smoke tests for Sections 281-288 diagnostics/layout suggestions."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract as diagnostics  # noqa: E402
import bp_authoring_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract as readback  # noqa: E402
from test_bp_authoring_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract import build_current_section_265_272_summary  # noqa: E402


def build_current_section_273_280_summary() -> dict:
    section_265_272_summary = build_current_section_265_272_summary()
    readback_result = (
        readback.build_live_actor_bp_component_default_readback_result()
    )
    contract = readback.build_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract(
        True,
        section_265_272_summary,
        readback_result,
    )
    return readback.summarize_durable_executor_authoring_live_actor_bp_component_default_readback_batches(
        [contract]
    )


def build_current_diagnostics_result(**overrides: object) -> dict:
    result = diagnostics.build_function_diagnostics_graph_layout_result()
    result.update(overrides)
    return result


def main() -> int:
    section_273_280_summary = build_current_section_273_280_summary()
    result = build_current_diagnostics_result()
    contract = diagnostics.build_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract(
        True,
        section_273_280_summary,
        result,
    )
    assert (
        contract["schema"]
        == diagnostics
        .DURABLE_EXECUTOR_AUTHORING_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_273_280_summary_schema_matches"] is True
    assert contract["section_273_280_summary_passed"] is True
    assert contract["section_273_280_component_default_readback_ready"] is True
    assert contract["section_273_280_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["actor_bp_readback_summary_ready"] is True
    assert contract["target_scope_reconfirmed"] is True
    assert contract["function_call_diagnostics_ready"] is True
    assert contract["pin_contract_diagnostics_ready"] is True
    assert contract["graph_layout_diagnostics_ready"] is True
    assert contract["repair_suggestions_generated"] is True
    assert contract["auto_graph_repair_execution_blocked"] is True
    assert contract["diagnostics_no_write_boundary_verified"] is True
    assert contract["result_has_no_error"] is True
    assert contract["section_281_actor_bp_readback_summary_ready"] is True
    assert contract["section_282_function_call_diagnostics_ready"] is True
    assert contract["section_283_pin_contract_diagnostics_ready"] is True
    assert contract["section_284_graph_layout_diagnostics_ready"] is True
    assert contract["section_285_repair_suggestions_generated"] is True
    assert contract["section_286_auto_graph_repair_execution_blocked"] is True
    assert contract["section_287_diagnostics_no_write_boundary_verified"] is True
    assert (
        contract[
            "section_288_function_diagnostics_graph_layout_release_ready"
        ]
        is True
    )
    assert contract["graph_layout_repair_suggestions_ready"] is True
    assert (
        contract["function_diagnostics_graph_layout_no_write_verified"]
        is True
    )
    assert contract["final_durable_release_ready"] is True
    assert contract["graph_repair_command_dispatched"] is False
    assert contract["graph_repair_command_executed"] is False
    assert contract["graph_layout_mutation_performed"] is False
    assert contract["node_position_write_performed"] is False
    assert contract["pin_connection_write_performed"] is False
    assert contract["actor_bp_authoring_compile_dispatched"] is False
    assert contract["actor_bp_authoring_save_dispatched"] is False
    assert contract["actor_bp_authoring_asset_write_performed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["production_path_write_allowed"] is False

    summary = diagnostics.summarize_durable_executor_authoring_function_diagnostics_graph_layout_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_function_diagnostics_graph_layout_batch_count"
        ]
        == 1
    )
    expected_one_counts = (
        "section_273_280_summary_schema_matches_count",
        "section_273_280_summary_passed_count",
        "section_273_280_component_default_readback_ready_count",
        "section_273_280_outputs_closed_count",
        "result_schema_matches_count",
        "actor_bp_readback_summary_ready_count",
        "target_scope_reconfirmed_count",
        "function_call_diagnostics_ready_count",
        "pin_contract_diagnostics_ready_count",
        "graph_layout_diagnostics_ready_count",
        "repair_suggestions_generated_count",
        "auto_graph_repair_execution_blocked_count",
        "diagnostics_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "graph_layout_repair_suggestions_ready_count",
        "function_diagnostics_graph_layout_no_write_verified_count",
        "final_durable_release_ready_count",
        "section_281_actor_bp_readback_summary_ready_count",
        "section_282_function_call_diagnostics_ready_count",
        "section_283_pin_contract_diagnostics_ready_count",
        "section_284_graph_layout_diagnostics_ready_count",
        "section_285_repair_suggestions_generated_count",
        "section_286_auto_graph_repair_execution_blocked_count",
        "section_287_diagnostics_no_write_boundary_verified_count",
        "section_288_function_diagnostics_graph_layout_release_ready_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    expected_zero_counts = (
        "graph_repair_command_dispatched_count",
        "graph_repair_command_executed_count",
        "graph_layout_mutation_performed_count",
        "node_position_write_performed_count",
        "pin_connection_write_performed_count",
        "actor_bp_authoring_compile_dispatched_count",
        "actor_bp_authoring_compile_executed_count",
        "actor_bp_authoring_save_dispatched_count",
        "actor_bp_authoring_save_executed_count",
        "actor_bp_authoring_asset_write_performed_count",
        "actor_bp_authoring_package_dirty_marked_count",
        "cleanup_allowed_count",
        "cleanup_executed_count",
        "delete_asset_allowed_count",
        "rename_asset_allowed_count",
        "rename_command_dispatched_count",
        "rename_command_executed_count",
        "overwrite_allowed_count",
        "overwrite_executed_count",
        "production_path_write_allowed_count",
        "production_path_write_executed_count",
    )
    for key in expected_zero_counts:
        assert summary[key] == 0, key

    missing_readback_summary = dict(section_273_280_summary)
    missing_readback_summary[
        "live_actor_bp_component_default_readback_no_write_verified_count"
    ] = 0
    missing_readback_contract = diagnostics.build_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract(
        True,
        missing_readback_summary,
        result,
    )
    missing_readback_result = diagnostics.summarize_durable_executor_authoring_function_diagnostics_graph_layout_batches(
        [missing_readback_contract]
    )
    assert (
        missing_readback_contract[
            "section_273_280_component_default_readback_ready"
        ]
        is False
    )
    assert missing_readback_contract["function_call_diagnostics_ready"] is True
    assert (
        missing_readback_contract[
            "section_288_function_diagnostics_graph_layout_release_ready"
        ]
        is False
    )
    assert missing_readback_result["status"] == "failed"

    bad_function_schema_contract = diagnostics.build_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract(
        True,
        section_273_280_summary,
        build_current_diagnostics_result(function_call_contract_schema="legacy"),
    )
    bad_function_schema_summary = diagnostics.summarize_durable_executor_authoring_function_diagnostics_graph_layout_batches(
        [bad_function_schema_contract]
    )
    assert (
        bad_function_schema_contract["function_call_diagnostics_ready"]
        is False
    )
    assert bad_function_schema_summary["status"] == "failed"

    missing_suggestion_contract = diagnostics.build_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract(
        True,
        section_273_280_summary,
        build_current_diagnostics_result(repair_suggestion_count=2),
    )
    missing_suggestion_summary = diagnostics.summarize_durable_executor_authoring_function_diagnostics_graph_layout_batches(
        [missing_suggestion_contract]
    )
    assert (
        missing_suggestion_contract["repair_suggestions_generated"] is False
    )
    assert missing_suggestion_summary["status"] == "failed"

    auto_repair_contract = diagnostics.build_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract(
        True,
        section_273_280_summary,
        build_current_diagnostics_result(
            auto_graph_repair_execution_allowed=True,
            graph_repair_command_dispatched=True,
            graph_layout_mutation_performed=True,
            node_position_write_performed=True,
        ),
    )
    auto_repair_summary = diagnostics.summarize_durable_executor_authoring_function_diagnostics_graph_layout_batches(
        [auto_repair_contract]
    )
    assert (
        auto_repair_contract["auto_graph_repair_execution_blocked"] is False
    )
    assert (
        auto_repair_contract[
            "function_diagnostics_graph_layout_no_write_verified"
        ]
        is False
    )
    assert auto_repair_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring function diagnostics graph layout batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
