#!/usr/bin/env python
"""Offline smoke tests for Sections 489-496 bridge takeover handoff."""

from __future__ import annotations

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_takeover_handoff_batch_contract as handoff
import bp_authoring_durable_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batch_contract as bridge_blocker


def build_upstream_summary() -> dict:
    summary = {
        "schema": (
            bridge_blocker
            .DURABLE_EXECUTOR_AUTHORING_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in handoff.UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in handoff.UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_summary(
    result: dict | None = None,
    upstream_summary: dict | None = None,
) -> dict:
    contract = handoff.build_durable_executor_authoring_correct_workspace_bridge_takeover_handoff_batch_contract(
        requested=True,
        section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_summary=(
            upstream_summary or build_upstream_summary()
        ),
        correct_workspace_bridge_takeover_handoff_result=(
            result
            or handoff.build_correct_workspace_bridge_takeover_handoff_result()
        ),
    )
    return handoff.summarize_durable_executor_authoring_correct_workspace_bridge_takeover_handoff_batches(
        [contract]
    )


def assert_all_path_counts(summary: dict, value: int) -> None:
    for key in handoff.CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_PATH_COUNT_KEYS:
        assert summary[key] == value, key


def assert_all_blocked_counts_zero(summary: dict) -> None:
    for key in handoff.BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key


def main() -> int:
    result = handoff.build_correct_workspace_bridge_takeover_handoff_result()
    contract = handoff.build_durable_executor_authoring_correct_workspace_bridge_takeover_handoff_batch_contract(
        requested=True,
        section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_summary=build_upstream_summary(),
        correct_workspace_bridge_takeover_handoff_result=result,
    )
    assert contract["correct_workspace_bridge_takeover_handoff_ready"] is True
    assert contract["correct_workspace_bridge_takeover_still_blocked"] is True
    assert contract["wrong_workspace_bridge_owner_context_recorded"] is True
    assert contract["correct_workspace_bridge_launch_plan_recorded"] is True
    assert contract["automatic_bridge_takeover_blocked"] is True
    assert contract["post_takeover_bridge_verification_chain_required"] is True
    assert contract["live_durable_dispatch_after_takeover_blocked"] is True
    assert (
        contract[
            "correct_workspace_bridge_takeover_handoff_no_write_boundary_verified"
        ]
        is True
    )

    summary = handoff.summarize_durable_executor_authoring_correct_workspace_bridge_takeover_handoff_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_correct_workspace_bridge_takeover_handoff_batch_count"
        ]
        == 1
    )
    for key in (
        "section_481_488_summary_schema_matches_count",
        "section_481_488_summary_passed_count",
        "section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_ready_count",
        "section_481_488_outputs_closed_count",
        "result_schema_matches_count",
        "correct_workspace_bridge_takeover_handoff_checkpoint_satisfied_count",
        "wrong_workspace_bridge_owner_context_recorded_count",
        "correct_workspace_bridge_launch_plan_recorded_count",
        "automatic_bridge_takeover_blocked_count",
        "post_takeover_bridge_verification_chain_required_count",
        "live_durable_dispatch_after_takeover_blocked_count",
        "correct_workspace_bridge_takeover_handoff_no_write_boundary_verified_count",
        "bridge_takeover_compile_save_write_outputs_blocked_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
    ):
        assert summary[key] == 1, key
    assert_all_path_counts(summary, 1)
    assert_all_blocked_counts_zero(summary)

    missing_upstream = build_upstream_summary()
    missing_upstream[
        "section_488_non_actor_actual_temp_checkpoint_bridge_blocker_release_ready_count"
    ] = 0
    assert build_summary(upstream_summary=missing_upstream)["status"] == "failed"

    explicit_takeover = handoff.build_correct_workspace_bridge_takeover_handoff_result(
        explicit_takeover_approval_recorded=True,
    )
    assert build_summary(result=explicit_takeover)["status"] == "failed"

    process_stop = handoff.build_correct_workspace_bridge_takeover_handoff_result(
        process_termination_command_dispatched=True,
    )
    process_stop_summary = build_summary(result=process_stop)
    assert process_stop_summary["status"] == "failed"
    assert process_stop_summary["process_termination_command_dispatched_count"] == 1

    bridge_verified = handoff.build_correct_workspace_bridge_takeover_handoff_result(
        correct_workspace_bridge_verified=True,
    )
    bridge_verified_summary = build_summary(result=bridge_verified)
    assert bridge_verified_summary["status"] == "failed"
    assert bridge_verified_summary["correct_workspace_bridge_verified_count"] == 1

    dirty_write = handoff.build_correct_workspace_bridge_takeover_handoff_result(
        dirty_content_after=(
            "/Game/_MCP_Temp/DurableSaveGate/UserWidgetActual/"
            "WBP_DurableWidgetTreeActual"
        ),
    )
    assert build_summary(result=dirty_write)["status"] == "failed"

    print(
        "BP authoring durable executor authoring correct-workspace bridge takeover handoff batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
