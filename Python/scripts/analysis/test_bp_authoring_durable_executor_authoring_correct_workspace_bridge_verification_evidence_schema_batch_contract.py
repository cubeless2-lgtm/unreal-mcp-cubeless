#!/usr/bin/env python
"""Offline smoke tests for Sections 513-520 bridge verification evidence schema."""

from __future__ import annotations

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batch_contract as admission
import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_schema_batch_contract as evidence_schema


def build_upstream_summary() -> dict:
    summary = {
        "schema": (
            admission
            .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_POST_TAKEOVER_VERIFICATION_ADMISSION_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in evidence_schema.UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in evidence_schema.UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_summary(
    result: dict | None = None,
    upstream_summary: dict | None = None,
) -> dict:
    contract = evidence_schema.build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_schema_batch_contract(
        requested=True,
        section_505_512_post_takeover_verification_admission_summary=(
            upstream_summary or build_upstream_summary()
        ),
        correct_workspace_bridge_verification_evidence_schema_result=(
            result
            or evidence_schema.build_correct_workspace_bridge_verification_evidence_schema_result()
        ),
    )
    return evidence_schema.summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_schema_batches(
        [contract]
    )


def assert_all_path_counts(summary: dict, value: int) -> None:
    for key in evidence_schema.CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_SCHEMA_PATH_COUNT_KEYS:
        assert summary[key] == value, key


def assert_all_blocked_counts_zero(summary: dict) -> None:
    for key in evidence_schema.BLOCKED_VERIFICATION_EVIDENCE_SCHEMA_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key


def main() -> int:
    result = evidence_schema.build_correct_workspace_bridge_verification_evidence_schema_result()
    contract = evidence_schema.build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_schema_batch_contract(
        requested=True,
        section_505_512_post_takeover_verification_admission_summary=build_upstream_summary(),
        correct_workspace_bridge_verification_evidence_schema_result=result,
    )
    assert (
        contract["correct_workspace_bridge_verification_evidence_schema_ready"]
        is True
    )
    assert contract["verification_evidence_admission_still_blocked"] is True
    assert contract["required_evidence_fields_recorded"] is True
    assert contract["project_identity_evidence_requirements_recorded"] is True
    assert contract["bridge_identity_evidence_requirements_recorded"] is True
    assert contract["read_only_probe_evidence_requirements_recorded"] is True
    assert contract["evidence_ingest_and_admission_blocked"] is True
    assert contract["verification_evidence_schema_no_write_boundary_verified"] is True

    summary = evidence_schema.summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_schema_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_schema_batch_count"
        ]
        == 1
    )
    for key in (
        "section_505_512_summary_schema_matches_count",
        "section_505_512_summary_passed_count",
        "section_505_512_post_takeover_verification_admission_ready_count",
        "section_505_512_outputs_closed_count",
        "result_schema_matches_count",
        "verification_evidence_schema_checkpoint_satisfied_count",
        "required_evidence_fields_recorded_count",
        "project_identity_evidence_requirements_recorded_count",
        "bridge_identity_evidence_requirements_recorded_count",
        "read_only_probe_evidence_requirements_recorded_count",
        "evidence_ingest_and_admission_blocked_count",
        "verification_evidence_schema_no_write_boundary_verified_count",
        "verification_evidence_schema_compile_save_write_outputs_blocked_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
    ):
        assert summary[key] == 1, key
    assert_all_path_counts(summary, 1)
    assert_all_blocked_counts_zero(summary)

    missing_upstream = build_upstream_summary()
    missing_upstream[
        "section_512_post_takeover_verification_admission_release_ready_count"
    ] = 0
    assert build_summary(upstream_summary=missing_upstream)["status"] == "failed"

    missing_field = evidence_schema.build_correct_workspace_bridge_verification_evidence_schema_result(
        required_evidence_fields=(
            "project_file_path",
            "editor_executable_path",
            "bridge_host",
        ),
    )
    assert build_summary(result=missing_field)["status"] == "failed"

    ingest_open = evidence_schema.build_correct_workspace_bridge_verification_evidence_schema_result(
        evidence_ingest_allowed=True,
    )
    assert build_summary(result=ingest_open)["status"] == "failed"

    payload_received = evidence_schema.build_correct_workspace_bridge_verification_evidence_schema_result(
        evidence_payload_received=True,
    )
    payload_summary = build_summary(result=payload_received)
    assert payload_summary["status"] == "failed"
    assert payload_summary["evidence_payload_received_count"] == 1

    evidence_admitted = evidence_schema.build_correct_workspace_bridge_verification_evidence_schema_result(
        verification_evidence_admitted=True,
    )
    admitted_summary = build_summary(result=evidence_admitted)
    assert admitted_summary["status"] == "failed"
    assert admitted_summary["verification_evidence_admitted_count"] == 1

    dirty_write = evidence_schema.build_correct_workspace_bridge_verification_evidence_schema_result(
        dirty_content_after=(
            "/Game/_MCP_Temp/DurableSaveGate/UserWidgetActual/"
            "WBP_DurableWidgetTreeActual"
        ),
    )
    assert build_summary(result=dirty_write)["status"] == "failed"

    print(
        "BP authoring durable executor authoring correct-workspace bridge verification evidence schema batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
