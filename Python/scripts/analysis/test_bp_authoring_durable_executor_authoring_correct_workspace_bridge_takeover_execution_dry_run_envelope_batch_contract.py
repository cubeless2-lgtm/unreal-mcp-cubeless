#!/usr/bin/env python
"""Offline smoke tests for Sections 497-504 bridge takeover dry-run envelope."""

from __future__ import annotations

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batch_contract as envelope
import bp_authoring_durable_executor_authoring_correct_workspace_bridge_takeover_handoff_batch_contract as handoff


def build_upstream_summary() -> dict:
    summary = {
        "schema": (
            handoff
            .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in envelope.UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in envelope.UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_summary(
    result: dict | None = None,
    upstream_summary: dict | None = None,
) -> dict:
    contract = envelope.build_durable_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batch_contract(
        requested=True,
        section_489_496_correct_workspace_bridge_takeover_handoff_summary=(
            upstream_summary or build_upstream_summary()
        ),
        correct_workspace_bridge_takeover_execution_dry_run_envelope_result=(
            result
            or envelope.build_correct_workspace_bridge_takeover_execution_dry_run_envelope_result()
        ),
    )
    return envelope.summarize_durable_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batches(
        [contract]
    )


def assert_all_path_counts(summary: dict, value: int) -> None:
    for key in envelope.CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_PATH_COUNT_KEYS:
        assert summary[key] == value, key


def assert_all_blocked_counts_zero(summary: dict) -> None:
    for key in envelope.BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key


def main() -> int:
    result = envelope.build_correct_workspace_bridge_takeover_execution_dry_run_envelope_result()
    contract = envelope.build_durable_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batch_contract(
        requested=True,
        section_489_496_correct_workspace_bridge_takeover_handoff_summary=build_upstream_summary(),
        correct_workspace_bridge_takeover_execution_dry_run_envelope_result=result,
    )
    assert (
        contract["correct_workspace_bridge_takeover_execution_dry_run_envelope_ready"]
        is True
    )
    assert contract["correct_workspace_bridge_takeover_execution_still_blocked"] is True
    assert contract["takeover_execution_scope_recorded"] is True
    assert contract["takeover_execution_authorization_still_required"] is True
    assert contract["wrong_workspace_release_command_blocked"] is True
    assert contract["correct_workspace_editor_launch_command_blocked"] is True
    assert contract["correct_workspace_bridge_verification_command_blocked"] is True
    assert contract["live_durable_dispatch_after_takeover_execution_blocked"] is True
    assert contract["takeover_execution_dry_run_no_write_boundary_verified"] is True

    summary = envelope.summarize_durable_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batch_count"
        ]
        == 1
    )
    for key in (
        "section_489_496_summary_schema_matches_count",
        "section_489_496_summary_passed_count",
        "section_489_496_correct_workspace_bridge_takeover_handoff_ready_count",
        "section_489_496_outputs_closed_count",
        "result_schema_matches_count",
        "correct_workspace_bridge_takeover_execution_dry_run_checkpoint_satisfied_count",
        "takeover_execution_scope_recorded_count",
        "takeover_execution_authorization_still_required_count",
        "wrong_workspace_release_command_blocked_count",
        "correct_workspace_editor_launch_command_blocked_count",
        "correct_workspace_bridge_verification_command_blocked_count",
        "live_durable_dispatch_after_takeover_execution_blocked_count",
        "takeover_execution_dry_run_no_write_boundary_verified_count",
        "takeover_execution_compile_save_write_outputs_blocked_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
    ):
        assert summary[key] == 1, key
    assert_all_path_counts(summary, 1)
    assert_all_blocked_counts_zero(summary)

    missing_upstream = build_upstream_summary()
    missing_upstream[
        "section_496_correct_workspace_bridge_takeover_handoff_release_ready_count"
    ] = 0
    assert build_summary(upstream_summary=missing_upstream)["status"] == "failed"

    authorization_open = envelope.build_correct_workspace_bridge_takeover_execution_dry_run_envelope_result(
        actual_takeover_execution_allowed=True,
    )
    assert build_summary(result=authorization_open)["status"] == "failed"

    process_stop = envelope.build_correct_workspace_bridge_takeover_execution_dry_run_envelope_result(
        process_termination_command_dispatched=True,
    )
    process_stop_summary = build_summary(result=process_stop)
    assert process_stop_summary["status"] == "failed"
    assert process_stop_summary["process_termination_command_dispatched_count"] == 1

    launch_dispatch = envelope.build_correct_workspace_bridge_takeover_execution_dry_run_envelope_result(
        correct_workspace_editor_launch_command_dispatched=True,
    )
    launch_dispatch_summary = build_summary(result=launch_dispatch)
    assert launch_dispatch_summary["status"] == "failed"
    assert (
        launch_dispatch_summary[
            "correct_workspace_editor_launch_command_dispatched_count"
        ]
        == 1
    )

    verify_dispatch = envelope.build_correct_workspace_bridge_takeover_execution_dry_run_envelope_result(
        read_only_probe_command_dispatched=True,
    )
    verify_dispatch_summary = build_summary(result=verify_dispatch)
    assert verify_dispatch_summary["status"] == "failed"
    assert verify_dispatch_summary["read_only_probe_command_dispatched_count"] == 1

    dirty_write = envelope.build_correct_workspace_bridge_takeover_execution_dry_run_envelope_result(
        dirty_content_after=(
            "/Game/_MCP_Temp/DurableSaveGate/DataAssetActual/"
            "DA_DurableDataAssetActual"
        ),
    )
    assert build_summary(result=dirty_write)["status"] == "failed"

    print(
        "BP authoring durable executor authoring correct-workspace bridge takeover execution dry-run envelope batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
