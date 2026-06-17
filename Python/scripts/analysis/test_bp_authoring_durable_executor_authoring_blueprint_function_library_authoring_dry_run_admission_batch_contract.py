#!/usr/bin/env python
"""Offline smoke tests for Sections 473-480 BFL dry-run admission."""

from __future__ import annotations

import bp_authoring_durable_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batch_contract as dry_run
import bp_authoring_durable_executor_authoring_blueprint_function_library_readonly_preflight_batch_contract as readonly_preflight


def build_upstream_summary() -> dict:
    summary = {
        "schema": (
            readonly_preflight
            .DURABLE_EXECUTOR_AUTHORING_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in dry_run.UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in dry_run.UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_summary(result: dict | None = None, upstream: dict | None = None) -> dict:
    contract = dry_run.build_durable_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batch_contract(
        requested=True,
        section_465_472_blueprint_function_library_readonly_preflight_summary=(
            upstream or build_upstream_summary()
        ),
        blueprint_function_library_authoring_dry_run_admission_result=(
            result
            or dry_run.build_blueprint_function_library_authoring_dry_run_admission_result()
        ),
    )
    return dry_run.summarize_durable_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batches(
        [contract]
    )


def assert_all_path_counts(summary: dict, value: int) -> None:
    for key in (
        dry_run
        .BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_PATH_COUNT_KEYS
    ):
        assert summary[key] == value, key


def assert_all_blocked_counts_zero(summary: dict) -> None:
    for key in (
        dry_run
        .BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key


def main() -> int:
    result = dry_run.build_blueprint_function_library_authoring_dry_run_admission_result()
    contract = dry_run.build_durable_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batch_contract(
        requested=True,
        section_465_472_blueprint_function_library_readonly_preflight_summary=build_upstream_summary(),
        blueprint_function_library_authoring_dry_run_admission_result=result,
    )
    assert (
        contract["blueprint_function_library_authoring_dry_run_admission_ready"]
        is True
    )
    assert contract["blueprint_function_library_actual_authoring_still_blocked"] is True
    assert contract["blueprint_function_library_dry_run_scope_verified"] is True
    assert (
        contract["blueprint_function_library_function_signature_plan_classified"]
        is True
    )
    assert contract["blueprint_function_library_graph_node_plan_classified"] is True
    assert contract["blueprint_function_library_graph_mutation_command_blocked"] is True
    assert (
        contract["blueprint_function_library_compile_save_write_outputs_blocked"]
        is True
    )
    assert (
        contract[
            "blueprint_function_library_authoring_dry_run_no_write_boundary_verified"
        ]
        is True
    )

    summary = dry_run.summarize_durable_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batch_count"
        ]
        == 1
    )
    assert summary["section_465_472_summary_schema_matches_count"] == 1
    assert summary["section_465_472_summary_passed_count"] == 1
    assert (
        summary[
            "section_465_472_blueprint_function_library_readonly_preflight_ready_count"
        ]
        == 1
    )
    assert summary["section_465_472_outputs_closed_count"] == 1
    assert summary["result_schema_matches_count"] == 1
    assert (
        summary[
            "blueprint_function_library_authoring_dry_run_checkpoint_satisfied_count"
        ]
        == 1
    )
    assert summary["blueprint_function_library_dry_run_scope_verified_count"] == 1
    assert (
        summary[
            "blueprint_function_library_function_signature_plan_classified_count"
        ]
        == 1
    )
    assert summary["blueprint_function_library_graph_node_plan_classified_count"] == 1
    assert (
        summary["blueprint_function_library_graph_mutation_command_blocked_count"]
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
            "blueprint_function_library_authoring_dry_run_no_write_boundary_verified_count"
        ]
        == 1
    )
    assert summary["result_has_no_error_count"] == 1
    assert summary["final_durable_release_ready_count"] == 1
    assert_all_path_counts(summary, 1)
    assert_all_blocked_counts_zero(summary)

    missing_upstream = build_upstream_summary()
    missing_upstream[
        "section_472_blueprint_function_library_readonly_preflight_release_ready_count"
    ] = 0
    assert build_summary(upstream=missing_upstream)["status"] == "failed"

    wrong_scope = dry_run.build_blueprint_function_library_authoring_dry_run_admission_result(
        target_asset_path="/Game/Production/BFL_Unexpected"
    )
    wrong_scope_summary = build_summary(result=wrong_scope)
    assert wrong_scope_summary["status"] == "failed"
    assert_all_path_counts(wrong_scope_summary, 0)

    mutation_open = dry_run.build_blueprint_function_library_authoring_dry_run_admission_result(
        function_library_graph_mutation_command_dispatched=True,
    )
    mutation_open_summary = build_summary(result=mutation_open)
    assert mutation_open_summary["status"] == "failed"
    assert (
        mutation_open_summary[
            "function_library_graph_mutation_command_dispatched_count"
        ]
        == 1
    )

    dirty_write = dry_run.build_blueprint_function_library_authoring_dry_run_admission_result(
        dirty_content_after_dry_run=(
            "/Game/_MCP_Temp/DurableSaveGate/FunctionLibraryDryRun/"
            "BFL_DurableFunctionLibraryDryRun"
        ),
    )
    assert build_summary(result=dirty_write)["status"] == "failed"

    print(
        "BP authoring durable executor authoring Blueprint Function Library authoring dry-run admission batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
