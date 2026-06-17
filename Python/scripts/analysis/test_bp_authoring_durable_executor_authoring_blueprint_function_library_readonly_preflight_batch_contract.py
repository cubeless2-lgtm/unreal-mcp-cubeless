#!/usr/bin/env python
"""Offline smoke tests for Sections 465-472 Blueprint Function Library preflight."""

from __future__ import annotations

import bp_authoring_durable_executor_authoring_blueprint_function_library_readonly_preflight_batch_contract as bfl_preflight
import bp_authoring_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract as admission


def build_upstream_summary() -> dict:
    summary = {
        "schema": (
            admission
            .DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in bfl_preflight.UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in bfl_preflight.UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_summary(result: dict | None = None, upstream: dict | None = None) -> dict:
    contract = bfl_preflight.build_durable_executor_authoring_blueprint_function_library_readonly_preflight_batch_contract(
        requested=True,
        section_385_392_non_actor_admission_dry_run_summary=(
            upstream or build_upstream_summary()
        ),
        blueprint_function_library_readonly_preflight_result=(
            result
            or bfl_preflight.build_blueprint_function_library_readonly_preflight_result()
        ),
    )
    return bfl_preflight.summarize_durable_executor_authoring_blueprint_function_library_readonly_preflight_batches(
        [contract]
    )


def assert_all_path_counts(summary: dict, value: int) -> None:
    for key in bfl_preflight.BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_PATH_COUNT_KEYS:
        assert summary[key] == value, key


def assert_all_blocked_counts_zero(summary: dict) -> None:
    for key in (
        bfl_preflight
        .BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key


def main() -> int:
    result = bfl_preflight.build_blueprint_function_library_readonly_preflight_result()
    contract = bfl_preflight.build_durable_executor_authoring_blueprint_function_library_readonly_preflight_batch_contract(
        requested=True,
        section_385_392_non_actor_admission_dry_run_summary=build_upstream_summary(),
        blueprint_function_library_readonly_preflight_result=result,
    )
    assert contract["blueprint_function_library_readonly_preflight_ready"] is True
    assert contract["blueprint_function_library_actual_authoring_still_blocked"] is True
    assert (
        contract[
            "blueprint_function_library_factory_parent_prerequisites_verified"
        ]
        is True
    )
    assert contract["blueprint_function_library_graph_prerequisites_verified"] is True
    assert contract["blueprint_function_library_creation_graph_outputs_blocked"] is True
    assert (
        contract["blueprint_function_library_compile_save_write_outputs_blocked"]
        is True
    )
    assert (
        contract[
            "blueprint_function_library_readonly_no_write_boundary_verified"
        ]
        is True
    )

    summary = bfl_preflight.summarize_durable_executor_authoring_blueprint_function_library_readonly_preflight_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_blueprint_function_library_readonly_preflight_batch_count"
        ]
        == 1
    )
    assert summary["section_385_392_summary_schema_matches_count"] == 1
    assert summary["section_385_392_summary_passed_count"] == 1
    assert summary["section_385_392_non_actor_admission_dry_run_ready_count"] == 1
    assert summary["section_385_392_outputs_closed_count"] == 1
    assert summary["result_schema_matches_count"] == 1
    assert (
        summary["blueprint_function_library_readonly_checkpoint_satisfied_count"]
        == 1
    )
    assert (
        summary[
            "correct_project_blueprint_function_library_readonly_probe_recorded_count"
        ]
        == 1
    )
    assert (
        summary[
            "blueprint_function_library_factory_parent_prerequisites_verified_count"
        ]
        == 1
    )
    assert (
        summary["blueprint_function_library_graph_prerequisites_verified_count"]
        == 1
    )
    assert (
        summary["blueprint_function_library_creation_graph_outputs_blocked_count"]
        == 1
    )
    assert (
        summary[
            "blueprint_function_library_compile_save_write_outputs_blocked_count"
        ]
        == 1
    )
    assert (
        summary[
            "blueprint_function_library_readonly_no_write_boundary_verified_count"
        ]
        == 1
    )
    assert summary["result_has_no_error_count"] == 1
    assert summary["final_durable_release_ready_count"] == 1
    assert_all_path_counts(summary, 1)
    assert_all_blocked_counts_zero(summary)

    missing_upstream = build_upstream_summary()
    missing_upstream[
        "section_390_function_library_interface_admission_blocked_pending_graph_contract_count"
    ] = 0
    assert build_summary(upstream=missing_upstream)["status"] == "failed"

    missing_graph_probe = bfl_preflight.build_blueprint_function_library_readonly_preflight_result(
        class_probes={"K2Node_FunctionEntry": {"loaded": False}},
    )
    missing_graph_summary = build_summary(result=missing_graph_probe)
    assert missing_graph_summary["status"] == "failed"
    assert_all_path_counts(missing_graph_summary, 0)

    graph_mutation_open = bfl_preflight.build_blueprint_function_library_readonly_preflight_result(
        function_library_graph_mutation_command_dispatched=True,
    )
    graph_mutation_summary = build_summary(result=graph_mutation_open)
    assert graph_mutation_summary["status"] == "failed"
    assert (
        graph_mutation_summary[
            "function_library_graph_mutation_command_dispatched_count"
        ]
        == 1
    )

    dirty_write = bfl_preflight.build_blueprint_function_library_readonly_preflight_result(
        dirty_content_after=(
            "/Game/_MCP_Temp/DurableSaveGate/FunctionLibraryReadOnly/"
            "BFL_DurableFunctionLibraryReadonly"
        ),
    )
    assert build_summary(result=dirty_write)["status"] == "failed"

    print(
        "BP authoring durable executor authoring Blueprint Function Library read-only preflight batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
