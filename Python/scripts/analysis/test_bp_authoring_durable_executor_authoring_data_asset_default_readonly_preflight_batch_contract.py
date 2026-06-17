#!/usr/bin/env python
"""Offline smoke tests for Sections 449-456 DataAsset read-only preflight."""

from __future__ import annotations

import bp_authoring_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract as admission
import bp_authoring_durable_executor_authoring_data_asset_default_readonly_preflight_batch_contract as data_asset_preflight


def build_upstream_summary() -> dict:
    summary = {
        "schema": (
            admission
            .DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in data_asset_preflight.UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in data_asset_preflight.UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_summary(result: dict | None = None, upstream: dict | None = None) -> dict:
    contract = data_asset_preflight.build_durable_executor_authoring_data_asset_default_readonly_preflight_batch_contract(
        requested=True,
        section_385_392_non_actor_admission_dry_run_summary=(
            upstream or build_upstream_summary()
        ),
        data_asset_default_readonly_preflight_result=(
            result
            or data_asset_preflight.build_data_asset_default_readonly_preflight_result()
        ),
    )
    return data_asset_preflight.summarize_durable_executor_authoring_data_asset_default_readonly_preflight_batches(
        [contract]
    )


def assert_all_path_counts(summary: dict, value: int) -> None:
    for key in data_asset_preflight.DATA_ASSET_DEFAULT_READONLY_PREFLIGHT_PATH_COUNT_KEYS:
        assert summary[key] == value, key


def assert_all_blocked_counts_zero(summary: dict) -> None:
    for key in (
        data_asset_preflight
        .BLOCKED_DATA_ASSET_DEFAULT_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key


def main() -> int:
    result = data_asset_preflight.build_data_asset_default_readonly_preflight_result()
    contract = data_asset_preflight.build_durable_executor_authoring_data_asset_default_readonly_preflight_batch_contract(
        requested=True,
        section_385_392_non_actor_admission_dry_run_summary=build_upstream_summary(),
        data_asset_default_readonly_preflight_result=result,
    )
    assert contract["data_asset_default_readonly_preflight_ready"] is True
    assert contract["data_asset_default_actual_authoring_still_blocked"] is True
    assert contract["data_asset_blueprint_factory_prerequisites_verified"] is True
    assert (
        contract["primary_data_asset_default_readback_prerequisites_verified"]
        is True
    )
    assert contract["data_asset_default_mutation_outputs_blocked"] is True
    assert contract["data_asset_compile_save_write_outputs_blocked"] is True
    assert (
        contract["data_asset_default_readonly_no_write_boundary_verified"]
        is True
    )

    summary = data_asset_preflight.summarize_durable_executor_authoring_data_asset_default_readonly_preflight_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_data_asset_default_readonly_preflight_batch_count"
        ]
        == 1
    )
    assert summary["section_385_392_summary_schema_matches_count"] == 1
    assert summary["section_385_392_summary_passed_count"] == 1
    assert summary["section_385_392_non_actor_admission_dry_run_ready_count"] == 1
    assert summary["section_385_392_outputs_closed_count"] == 1
    assert summary["result_schema_matches_count"] == 1
    assert summary["data_asset_default_readonly_checkpoint_satisfied_count"] == 1
    assert summary["correct_project_data_asset_readonly_probe_recorded_count"] == 1
    assert summary["data_asset_blueprint_factory_prerequisites_verified_count"] == 1
    assert (
        summary[
            "primary_data_asset_default_readback_prerequisites_verified_count"
        ]
        == 1
    )
    assert summary["data_asset_default_mutation_outputs_blocked_count"] == 1
    assert summary["data_asset_compile_save_write_outputs_blocked_count"] == 1
    assert (
        summary[
            "data_asset_default_readonly_no_write_boundary_verified_count"
        ]
        == 1
    )
    assert summary["result_has_no_error_count"] == 1
    assert summary["final_durable_release_ready_count"] == 1
    assert_all_path_counts(summary, 1)
    assert_all_blocked_counts_zero(summary)

    missing_upstream = build_upstream_summary()
    missing_upstream["section_388_data_asset_admission_blocked_pending_default_contract_count"] = 0
    assert build_summary(upstream=missing_upstream)["status"] == "failed"

    missing_parent = data_asset_preflight.build_data_asset_default_readonly_preflight_result(
        class_probes={"PrimaryDataAsset": {"loaded": False}},
    )
    missing_parent_summary = build_summary(result=missing_parent)
    assert missing_parent_summary["status"] == "failed"
    assert_all_path_counts(missing_parent_summary, 0)

    mutation_open = data_asset_preflight.build_data_asset_default_readonly_preflight_result(
        data_asset_default_mutation_command_dispatched=True,
    )
    mutation_open_summary = build_summary(result=mutation_open)
    assert mutation_open_summary["status"] == "failed"
    assert (
        mutation_open_summary[
            "data_asset_default_mutation_command_dispatched_count"
        ]
        == 1
    )

    dirty_write = data_asset_preflight.build_data_asset_default_readonly_preflight_result(
        dirty_content_after=(
            "/Game/_MCP_Temp/DurableSaveGate/DataAssetDefaultReadOnly/"
            "DA_DurableDataAssetReadonly"
        ),
    )
    assert build_summary(result=dirty_write)["status"] == "failed"

    print(
        "BP authoring durable executor authoring DataAsset default read-only preflight batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
