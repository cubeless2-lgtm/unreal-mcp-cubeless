#!/usr/bin/env python
"""Offline smoke tests for Sections 345-352 graph repair execution dry-run."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract as broader  # noqa: E402
import bp_authoring_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract as graph_repair  # noqa: E402
from test_bp_authoring_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract import build_current_section_329_336_summary  # noqa: E402


def build_current_section_337_344_summary() -> dict:
    section_329_336_summary = build_current_section_329_336_summary()
    result = broader.build_broader_non_actor_blueprint_dry_run_result()
    contract = broader.build_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract(
        True,
        section_329_336_summary,
        result,
    )
    return broader.summarize_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batches(
        [contract]
    )


def build_current_dry_run_result(**overrides: object) -> dict:
    result = graph_repair.build_graph_repair_execution_dry_run_result()
    result.update(overrides)
    return result


def main() -> int:
    section_337_344_summary = build_current_section_337_344_summary()
    result = build_current_dry_run_result()
    contract = graph_repair.build_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract(
        True,
        section_337_344_summary,
        result,
    )
    assert (
        contract["schema"]
        == graph_repair
        .DURABLE_EXECUTOR_AUTHORING_GRAPH_REPAIR_EXECUTION_DRY_RUN_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_337_344_summary_schema_matches"] is True
    assert contract["section_337_344_summary_passed"] is True
    assert contract["section_337_344_broader_non_actor_blueprint_dry_run_ready"] is True
    assert contract["section_337_344_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["graph_repair_dry_run_checkpoint_satisfied"] is True
    assert contract["graph_repair_dry_run_command_admitted"] is True
    assert contract["graph_repair_dry_run_command_executed"] is True
    assert contract["empty_graph_noop_repair_verified"] is True
    assert contract["node_pin_mutation_outputs_blocked"] is True
    assert contract["compile_save_outputs_blocked"] is True
    assert contract["graph_repair_dry_run_no_write_boundary_verified"] is True
    assert contract["result_has_no_error"] is True
    assert contract["section_345_graph_repair_dry_run_checkpoint_satisfied"] is True
    assert contract["section_346_graph_repair_dry_run_command_admitted"] is True
    assert contract["section_347_graph_repair_dry_run_command_executed"] is True
    assert contract["section_348_empty_graph_noop_repair_verified"] is True
    assert contract["section_349_node_pin_mutation_outputs_blocked"] is True
    assert contract["section_350_compile_save_outputs_blocked"] is True
    assert (
        contract[
            "section_351_graph_repair_dry_run_no_write_boundary_verified"
        ]
        is True
    )
    assert (
        contract[
            "section_352_graph_repair_execution_dry_run_release_ready"
        ]
        is True
    )
    assert contract["graph_repair_execution_dry_run_ready"] is True
    assert contract["graph_repair_actual_execution_still_blocked"] is True
    assert contract["final_durable_release_ready"] is True

    summary = graph_repair.summarize_durable_executor_authoring_graph_repair_execution_dry_run_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_graph_repair_execution_dry_run_batch_count"
        ]
        == 1
    )
    expected_one_counts = (
        "section_337_344_summary_schema_matches_count",
        "section_337_344_summary_passed_count",
        "section_337_344_broader_non_actor_blueprint_dry_run_ready_count",
        "section_337_344_outputs_closed_count",
        "result_schema_matches_count",
        "graph_repair_dry_run_checkpoint_satisfied_count",
        "graph_repair_dry_run_command_admitted_count",
        "graph_repair_dry_run_command_executed_count",
        "empty_graph_noop_repair_verified_count",
        "node_pin_mutation_outputs_blocked_count",
        "compile_save_outputs_blocked_count",
        "graph_repair_dry_run_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_345_graph_repair_dry_run_checkpoint_satisfied_count",
        "section_346_graph_repair_dry_run_command_admitted_count",
        "section_347_graph_repair_dry_run_command_executed_count",
        "section_348_empty_graph_noop_repair_verified_count",
        "section_349_node_pin_mutation_outputs_blocked_count",
        "section_350_compile_save_outputs_blocked_count",
        "section_351_graph_repair_dry_run_no_write_boundary_verified_count",
        "section_352_graph_repair_execution_dry_run_release_ready_count",
        "graph_repair_execution_dry_run_ready_count",
        "graph_repair_actual_execution_still_blocked_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in graph_repair.BLOCKED_GRAPH_REPAIR_EXECUTION_DRY_RUN_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key

    missing_upstream = dict(section_337_344_summary)
    missing_upstream["broader_non_actor_blueprint_dry_run_ready_count"] = 0
    missing_upstream_contract = graph_repair.build_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = graph_repair.summarize_durable_executor_authoring_graph_repair_execution_dry_run_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_337_344_broader_non_actor_blueprint_dry_run_ready"
        ]
        is False
    )
    assert missing_upstream_contract["graph_repair_execution_dry_run_ready"] is False
    assert missing_upstream_summary["status"] == "failed"

    wrong_target_contract = graph_repair.build_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract(
        True,
        section_337_344_summary,
        build_current_dry_run_result(target_asset_path="/Game/Production/BP_Bad"),
    )
    wrong_target_summary = graph_repair.summarize_durable_executor_authoring_graph_repair_execution_dry_run_batches(
        [wrong_target_contract]
    )
    assert wrong_target_contract["graph_repair_dry_run_command_admitted"] is False
    assert wrong_target_summary["status"] == "failed"

    non_noop_contract = graph_repair.build_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract(
        True,
        section_337_344_summary,
        build_current_dry_run_result(
            dry_run_noop_due_empty_graph=False,
            node_position_repair_plan_count=1,
        ),
    )
    non_noop_summary = graph_repair.summarize_durable_executor_authoring_graph_repair_execution_dry_run_batches(
        [non_noop_contract]
    )
    assert non_noop_contract["empty_graph_noop_repair_verified"] is False
    assert non_noop_summary["status"] == "failed"

    mutation_attempt_contract = graph_repair.build_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract(
        True,
        section_337_344_summary,
        build_current_dry_run_result(
            graph_repair_command_dispatched=True,
            node_position_write_performed=True,
            target_dirty_after_dry_run=True,
        ),
    )
    mutation_attempt_summary = graph_repair.summarize_durable_executor_authoring_graph_repair_execution_dry_run_batches(
        [mutation_attempt_contract]
    )
    assert mutation_attempt_contract["node_pin_mutation_outputs_blocked"] is False
    assert (
        mutation_attempt_contract[
            "graph_repair_dry_run_no_write_boundary_verified"
        ]
        is False
    )
    assert mutation_attempt_summary["status"] == "failed"

    compile_save_attempt_contract = graph_repair.build_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract(
        True,
        section_337_344_summary,
        build_current_dry_run_result(
            compile_required=True,
            actor_bp_authoring_compile_dispatched=True,
            save_required=True,
            actor_bp_authoring_save_dispatched=True,
        ),
    )
    compile_save_attempt_summary = graph_repair.summarize_durable_executor_authoring_graph_repair_execution_dry_run_batches(
        [compile_save_attempt_contract]
    )
    assert compile_save_attempt_contract["compile_save_outputs_blocked"] is False
    assert compile_save_attempt_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring graph repair execution dry-run batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
