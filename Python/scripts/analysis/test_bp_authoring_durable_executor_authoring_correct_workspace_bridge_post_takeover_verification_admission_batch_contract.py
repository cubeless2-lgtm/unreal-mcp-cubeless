#!/usr/bin/env python
"""Offline smoke tests for Sections 505-512 bridge verification admission."""

from __future__ import annotations

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batch_contract as admission
import bp_authoring_durable_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batch_contract as envelope


def build_upstream_summary() -> dict:
    summary = {
        "schema": (
            envelope
            .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in admission.UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in admission.UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_summary(
    result: dict | None = None,
    upstream_summary: dict | None = None,
) -> dict:
    contract = admission.build_durable_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batch_contract(
        requested=True,
        section_497_504_takeover_execution_dry_run_envelope_summary=(
            upstream_summary or build_upstream_summary()
        ),
        correct_workspace_bridge_post_takeover_verification_admission_result=(
            result
            or admission.build_correct_workspace_bridge_post_takeover_verification_admission_result()
        ),
    )
    return admission.summarize_durable_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batches(
        [contract]
    )


def assert_all_path_counts(summary: dict, value: int) -> None:
    for key in admission.CORRECT_WORKSPACE_BRIDGE_POST_TAKEOVER_VERIFICATION_ADMISSION_PATH_COUNT_KEYS:
        assert summary[key] == value, key


def assert_all_blocked_counts_zero(summary: dict) -> None:
    for key in admission.BLOCKED_POST_TAKEOVER_VERIFICATION_ADMISSION_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key


def main() -> int:
    result = admission.build_correct_workspace_bridge_post_takeover_verification_admission_result()
    contract = admission.build_durable_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batch_contract(
        requested=True,
        section_497_504_takeover_execution_dry_run_envelope_summary=build_upstream_summary(),
        correct_workspace_bridge_post_takeover_verification_admission_result=result,
    )
    assert (
        contract[
            "correct_workspace_bridge_post_takeover_verification_admission_ready"
        ]
        is True
    )
    assert contract["correct_workspace_bridge_verification_result_still_missing"] is True
    assert contract["takeover_execution_completion_evidence_required"] is True
    assert contract["correct_workspace_bridge_identity_evidence_required"] is True
    assert contract["read_only_probe_evidence_required"] is True
    assert contract["verification_result_admission_blocked"] is True
    assert contract["live_authoring_after_verification_blocked"] is True
    assert (
        contract[
            "post_takeover_verification_admission_no_write_boundary_verified"
        ]
        is True
    )

    summary = admission.summarize_durable_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batch_count"
        ]
        == 1
    )
    for key in (
        "section_497_504_summary_schema_matches_count",
        "section_497_504_summary_passed_count",
        "section_497_504_takeover_execution_dry_run_envelope_ready_count",
        "section_497_504_outputs_closed_count",
        "result_schema_matches_count",
        "post_takeover_verification_admission_checkpoint_satisfied_count",
        "takeover_execution_completion_evidence_required_count",
        "correct_workspace_bridge_identity_evidence_required_count",
        "read_only_probe_evidence_required_count",
        "verification_result_admission_blocked_count",
        "live_authoring_after_verification_blocked_count",
        "post_takeover_verification_admission_no_write_boundary_verified_count",
        "post_takeover_verification_compile_save_write_outputs_blocked_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
    ):
        assert summary[key] == 1, key
    assert_all_path_counts(summary, 1)
    assert_all_blocked_counts_zero(summary)

    missing_upstream = build_upstream_summary()
    missing_upstream[
        "section_504_takeover_execution_dry_run_release_ready_count"
    ] = 0
    assert build_summary(upstream_summary=missing_upstream)["status"] == "failed"

    takeover_done = admission.build_correct_workspace_bridge_post_takeover_verification_admission_result(
        takeover_execution_completed=True,
    )
    takeover_done_summary = build_summary(result=takeover_done)
    assert takeover_done_summary["status"] == "failed"
    assert takeover_done_summary["takeover_execution_completed_count"] == 1

    bridge_verified = admission.build_correct_workspace_bridge_post_takeover_verification_admission_result(
        correct_workspace_bridge_verified=True,
    )
    bridge_verified_summary = build_summary(result=bridge_verified)
    assert bridge_verified_summary["status"] == "failed"
    assert bridge_verified_summary["correct_workspace_bridge_verified_count"] == 1

    probe_passed = admission.build_correct_workspace_bridge_post_takeover_verification_admission_result(
        read_only_probe_passed=True,
    )
    probe_passed_summary = build_summary(result=probe_passed)
    assert probe_passed_summary["status"] == "failed"
    assert probe_passed_summary["read_only_probe_passed_count"] == 1

    admitted = admission.build_correct_workspace_bridge_post_takeover_verification_admission_result(
        verification_result_admitted=True,
    )
    admitted_summary = build_summary(result=admitted)
    assert admitted_summary["status"] == "failed"
    assert admitted_summary["verification_result_admitted_count"] == 1

    dirty_write = admission.build_correct_workspace_bridge_post_takeover_verification_admission_result(
        dirty_content_after=(
            "/Game/_MCP_Temp/DurableSaveGate/FunctionLibraryActual/"
            "BFL_DurableFunctionLibraryActual"
        ),
    )
    assert build_summary(result=dirty_write)["status"] == "failed"

    print(
        "BP authoring durable executor authoring correct-workspace bridge post-takeover verification admission batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
