#!/usr/bin/env python
"""Offline smoke tests for Sections 481-488 non-Actor bridge blocker."""

from __future__ import annotations

import bp_authoring_durable_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batch_contract as bfl_dry_run
import bp_authoring_durable_executor_authoring_data_asset_default_authoring_dry_run_admission_batch_contract as data_asset_dry_run
import bp_authoring_durable_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batch_contract as bridge_blocker
import bp_authoring_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_contract as bridge_port


def build_bridge_summary() -> dict:
    summary = {
        "schema": (
            bridge_port
            .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in bridge_blocker.BRIDGE_UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in bridge_blocker.BRIDGE_UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_data_asset_summary() -> dict:
    summary = {
        "schema": (
            data_asset_dry_run
            .DURABLE_EXECUTOR_AUTHORING_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_ADMISSION_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in bridge_blocker.DATA_ASSET_UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in bridge_blocker.DATA_ASSET_UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_bfl_summary() -> dict:
    summary = {
        "schema": (
            bfl_dry_run
            .DURABLE_EXECUTOR_AUTHORING_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in bridge_blocker.BFL_UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in bridge_blocker.BFL_UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_summary(
    result: dict | None = None,
    bridge_summary: dict | None = None,
    data_asset_summary: dict | None = None,
    bfl_summary: dict | None = None,
) -> dict:
    contract = bridge_blocker.build_durable_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batch_contract(
        requested=True,
        section_441_448_bridge_port_ownership_preflight_summary=(
            bridge_summary or build_bridge_summary()
        ),
        section_457_464_data_asset_dry_run_admission_summary=(
            data_asset_summary or build_data_asset_summary()
        ),
        section_473_480_bfl_dry_run_admission_summary=(
            bfl_summary or build_bfl_summary()
        ),
        non_actor_actual_temp_checkpoint_bridge_blocker_result=(
            result
            or bridge_blocker.build_non_actor_actual_temp_checkpoint_bridge_blocker_result()
        ),
    )
    return bridge_blocker.summarize_durable_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batches(
        [contract]
    )


def assert_all_path_counts(summary: dict, value: int) -> None:
    for key in bridge_blocker.NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_PATH_COUNT_KEYS:
        assert summary[key] == value, key


def assert_all_blocked_counts_zero(summary: dict) -> None:
    for key in bridge_blocker.BLOCKED_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key


def main() -> int:
    result = bridge_blocker.build_non_actor_actual_temp_checkpoint_bridge_blocker_result()
    contract = bridge_blocker.build_durable_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batch_contract(
        requested=True,
        section_441_448_bridge_port_ownership_preflight_summary=build_bridge_summary(),
        section_457_464_data_asset_dry_run_admission_summary=build_data_asset_summary(),
        section_473_480_bfl_dry_run_admission_summary=build_bfl_summary(),
        non_actor_actual_temp_checkpoint_bridge_blocker_result=result,
    )
    assert contract["non_actor_actual_temp_checkpoint_bridge_blocker_ready"] is True
    assert contract["non_actor_actual_temp_checkpoint_still_blocked"] is True
    assert contract["data_asset_actual_temp_checkpoint_preconditions_recorded"] is True
    assert contract["bfl_actual_temp_checkpoint_preconditions_recorded"] is True
    assert contract["wrong_workspace_bridge_blocker_reconfirmed"] is True
    assert contract["live_non_actor_temp_creation_dispatch_blocked"] is True
    assert contract["non_actor_temp_compile_save_write_outputs_blocked"] is True
    assert (
        contract["non_actor_actual_temp_checkpoint_no_write_boundary_verified"]
        is True
    )

    summary = bridge_blocker.summarize_durable_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batch_count"
        ]
        == 1
    )
    for key in (
        "section_441_448_summary_schema_matches_count",
        "section_441_448_summary_passed_count",
        "section_441_448_bridge_blocker_ready_count",
        "section_441_448_outputs_closed_count",
        "section_457_464_summary_schema_matches_count",
        "section_457_464_summary_passed_count",
        "section_457_464_data_asset_dry_run_ready_count",
        "section_457_464_outputs_closed_count",
        "section_473_480_summary_schema_matches_count",
        "section_473_480_summary_passed_count",
        "section_473_480_bfl_dry_run_ready_count",
        "section_473_480_outputs_closed_count",
        "result_schema_matches_count",
        "non_actor_actual_temp_checkpoint_bridge_blocker_checkpoint_satisfied_count",
        "data_asset_actual_temp_checkpoint_preconditions_recorded_count",
        "bfl_actual_temp_checkpoint_preconditions_recorded_count",
        "wrong_workspace_bridge_blocker_reconfirmed_count",
        "live_non_actor_temp_creation_dispatch_blocked_count",
        "non_actor_temp_compile_save_write_outputs_blocked_count",
        "non_actor_actual_temp_checkpoint_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
    ):
        assert summary[key] == 1, key
    assert_all_path_counts(summary, 1)
    assert_all_blocked_counts_zero(summary)

    missing_bridge = build_bridge_summary()
    missing_bridge["correct_workspace_bridge_port_release_still_required_count"] = 0
    assert build_summary(bridge_summary=missing_bridge)["status"] == "failed"

    missing_data_asset = build_data_asset_summary()
    missing_data_asset[
        "section_464_data_asset_authoring_dry_run_admission_release_ready_count"
    ] = 0
    assert build_summary(data_asset_summary=missing_data_asset)["status"] == "failed"

    bridge_verified = bridge_blocker.build_non_actor_actual_temp_checkpoint_bridge_blocker_result(
        correct_workspace_bridge_verified=True,
    )
    bridge_verified_summary = build_summary(result=bridge_verified)
    assert bridge_verified_summary["status"] == "failed"
    assert bridge_verified_summary["correct_workspace_bridge_verified_count"] == 1

    dispatch_open = bridge_blocker.build_non_actor_actual_temp_checkpoint_bridge_blocker_result(
        data_asset_actual_temp_create_command_dispatched=True,
    )
    dispatch_open_summary = build_summary(result=dispatch_open)
    assert dispatch_open_summary["status"] == "failed"
    assert (
        dispatch_open_summary[
            "data_asset_actual_temp_create_command_dispatched_count"
        ]
        == 1
    )

    dirty_write = bridge_blocker.build_non_actor_actual_temp_checkpoint_bridge_blocker_result(
        dirty_content_after=(
            "/Game/_MCP_Temp/DurableSaveGate/DataAssetActual/"
            "DA_DurableDataAssetActual"
        ),
    )
    assert build_summary(result=dirty_write)["status"] == "failed"

    print(
        "BP authoring durable executor authoring non-Actor actual temp checkpoint bridge blocker batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
