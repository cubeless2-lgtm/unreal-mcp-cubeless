#!/usr/bin/env python
"""Offline smoke tests for Sections 545-552 bridge validation result schema."""

from __future__ import annotations

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batch_contract as validation_envelope
import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_result_schema_batch_contract as result_schema


def build_upstream_summary() -> dict:
    summary = {
        "schema": (
            validation_envelope
            .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in result_schema.UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in result_schema.UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_summary(
    result: dict | None = None,
    upstream_summary: dict | None = None,
) -> dict:
    contract = result_schema.build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_result_schema_batch_contract(
        requested=True,
        section_537_544_validation_execution_dry_run_envelope_summary=(
            upstream_summary or build_upstream_summary()
        ),
        correct_workspace_bridge_verification_evidence_validation_result_schema_result=(
            result
            or result_schema.build_correct_workspace_bridge_verification_evidence_validation_result_schema_result()
        ),
    )
    return result_schema.summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_result_schema_batches(
        [contract]
    )


def assert_all_path_counts(summary: dict, value: int) -> None:
    for key in result_schema.CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_PATH_COUNT_KEYS:
        assert summary[key] == value, key


def assert_all_blocked_counts_zero(summary: dict) -> None:
    for key in result_schema.BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key


def main() -> int:
    result = result_schema.build_correct_workspace_bridge_verification_evidence_validation_result_schema_result()
    contract = result_schema.build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_result_schema_batch_contract(
        requested=True,
        section_537_544_validation_execution_dry_run_envelope_summary=build_upstream_summary(),
        correct_workspace_bridge_verification_evidence_validation_result_schema_result=result,
    )
    assert (
        contract[
            "correct_workspace_bridge_verification_evidence_validation_result_schema_ready"
        ]
        is True
    )
    assert contract["verification_validation_result_still_missing"] is True
    assert contract["validation_result_fields_recorded"] is True
    assert contract["validation_pass_fail_semantics_recorded"] is True
    assert contract["validation_rejection_reason_fields_recorded"] is True
    assert contract["validation_result_requires_execution_evidence"] is True
    assert contract["validation_result_admission_still_blocked"] is True
    assert contract["validation_result_schema_no_write_boundary_verified"] is True

    summary = result_schema.summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_result_schema_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_validation_result_schema_batch_count"
        ]
        == 1
    )
    for key in (
        "section_537_544_summary_schema_matches_count",
        "section_537_544_summary_passed_count",
        "section_537_544_validation_execution_dry_run_envelope_ready_count",
        "section_537_544_outputs_closed_count",
        "result_schema_matches_count",
        "validation_result_schema_checkpoint_satisfied_count",
        "validation_result_fields_recorded_count",
        "validation_pass_fail_semantics_recorded_count",
        "validation_rejection_reason_fields_recorded_count",
        "validation_result_requires_execution_evidence_count",
        "validation_result_admission_still_blocked_count",
        "validation_result_schema_no_write_boundary_verified_count",
        "validation_result_schema_compile_save_write_outputs_blocked_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
    ):
        assert summary[key] == 1, key
    assert_all_path_counts(summary, 1)
    assert_all_blocked_counts_zero(summary)

    missing_upstream = build_upstream_summary()
    missing_upstream[
        "section_544_validation_execution_dry_run_release_ready_count"
    ] = 0
    assert build_summary(upstream_summary=missing_upstream)["status"] == "failed"

    missing_field = result_schema.build_correct_workspace_bridge_verification_evidence_validation_result_schema_result(
        validation_result_fields=(
            "validation_result_id",
            "project_file_path",
            "bridge_host",
        ),
    )
    assert build_summary(result=missing_field)["status"] == "failed"

    wrong_identity = result_schema.build_correct_workspace_bridge_verification_evidence_validation_result_schema_result(
        bridge_port_number=8090,
    )
    assert build_summary(result=wrong_identity)["status"] == "failed"

    no_pass_fail = result_schema.build_correct_workspace_bridge_verification_evidence_validation_result_schema_result(
        validation_pass_fail_semantics_recorded=False,
    )
    assert build_summary(result=no_pass_fail)["status"] == "failed"

    recording_open = result_schema.build_correct_workspace_bridge_verification_evidence_validation_result_schema_result(
        validation_result_recording_allowed=True,
    )
    assert build_summary(result=recording_open)["status"] == "failed"

    validation_executed = result_schema.build_correct_workspace_bridge_verification_evidence_validation_result_schema_result(
        validation_execution_command_executed=True,
    )
    executed_summary = build_summary(result=validation_executed)
    assert executed_summary["status"] == "failed"
    assert executed_summary["validation_execution_command_executed_count"] == 1

    validation_recorded = result_schema.build_correct_workspace_bridge_verification_evidence_validation_result_schema_result(
        validation_result_recorded=True,
    )
    recorded_summary = build_summary(result=validation_recorded)
    assert recorded_summary["status"] == "failed"
    assert recorded_summary["validation_result_recorded_count"] == 1

    validation_admitted = result_schema.build_correct_workspace_bridge_verification_evidence_validation_result_schema_result(
        validation_result_admitted=True,
    )
    admitted_summary = build_summary(result=validation_admitted)
    assert admitted_summary["status"] == "failed"
    assert admitted_summary["validation_result_admitted_count"] == 1

    dirty_write = result_schema.build_correct_workspace_bridge_verification_evidence_validation_result_schema_result(
        dirty_content_after=(
            "/Game/_MCP_Temp/DurableSaveGate/UserWidgetActual/"
            "WBP_DurableWidgetTreeActual"
        ),
    )
    assert build_summary(result=dirty_write)["status"] == "failed"

    print(
        "BP authoring durable executor authoring correct-workspace bridge verification evidence validation result schema batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
