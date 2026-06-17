#!/usr/bin/env python
"""Offline smoke tests for Sections 521-528 bridge verification evidence payload dry-run."""

from __future__ import annotations

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batch_contract as payload_dry_run
import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_schema_batch_contract as evidence_schema


def build_upstream_summary() -> dict:
    summary = {
        "schema": (
            evidence_schema
            .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_SCHEMA_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in payload_dry_run.UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in payload_dry_run.UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_summary(
    result: dict | None = None,
    upstream_summary: dict | None = None,
) -> dict:
    contract = payload_dry_run.build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batch_contract(
        requested=True,
        section_513_520_verification_evidence_schema_summary=(
            upstream_summary or build_upstream_summary()
        ),
        correct_workspace_bridge_verification_evidence_payload_dry_run_result=(
            result
            or payload_dry_run.build_correct_workspace_bridge_verification_evidence_payload_dry_run_result()
        ),
    )
    return payload_dry_run.summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batches(
        [contract]
    )


def assert_all_path_counts(summary: dict, value: int) -> None:
    for key in payload_dry_run.CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_PATH_COUNT_KEYS:
        assert summary[key] == value, key


def assert_all_blocked_counts_zero(summary: dict) -> None:
    for key in payload_dry_run.BLOCKED_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key


def main() -> int:
    result = payload_dry_run.build_correct_workspace_bridge_verification_evidence_payload_dry_run_result()
    contract = payload_dry_run.build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batch_contract(
        requested=True,
        section_513_520_verification_evidence_schema_summary=build_upstream_summary(),
        correct_workspace_bridge_verification_evidence_payload_dry_run_result=result,
    )
    assert (
        contract[
            "correct_workspace_bridge_verification_evidence_payload_dry_run_ready"
        ]
        is True
    )
    assert contract["verification_evidence_payload_not_ingested"] is True
    assert contract["payload_template_fields_mapped"] is True
    assert contract["payload_identity_expectations_bound"] is True
    assert contract["payload_dirty_state_placeholders_recorded"] is True
    assert contract["rejection_fixture_matrix_recorded"] is True
    assert contract["payload_ingest_and_admission_still_blocked"] is True
    assert contract["payload_dry_run_no_write_boundary_verified"] is True

    summary = payload_dry_run.summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batch_count"
        ]
        == 1
    )
    for key in (
        "section_513_520_summary_schema_matches_count",
        "section_513_520_summary_passed_count",
        "section_513_520_verification_evidence_schema_ready_count",
        "section_513_520_outputs_closed_count",
        "result_schema_matches_count",
        "verification_evidence_payload_dry_run_checkpoint_satisfied_count",
        "payload_template_fields_mapped_count",
        "payload_identity_expectations_bound_count",
        "payload_dirty_state_placeholders_recorded_count",
        "rejection_fixture_matrix_recorded_count",
        "payload_ingest_and_admission_still_blocked_count",
        "payload_dry_run_no_write_boundary_verified_count",
        "payload_dry_run_compile_save_write_outputs_blocked_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
    ):
        assert summary[key] == 1, key
    assert_all_path_counts(summary, 1)
    assert_all_blocked_counts_zero(summary)

    missing_upstream = build_upstream_summary()
    missing_upstream[
        "section_520_verification_evidence_schema_release_ready_count"
    ] = 0
    assert build_summary(upstream_summary=missing_upstream)["status"] == "failed"

    missing_template_field = payload_dry_run.default_payload_template()
    missing_template_field.pop("timestamp_utc")
    assert (
        build_summary(
            result=payload_dry_run.build_correct_workspace_bridge_verification_evidence_payload_dry_run_result(
                payload_template=missing_template_field,
            )
        )["status"]
        == "failed"
    )

    actual_like_payload = payload_dry_run.build_correct_workspace_bridge_verification_evidence_payload_dry_run_result(
        payload_template_is_placeholder_only=False,
    )
    assert build_summary(result=actual_like_payload)["status"] == "failed"

    missing_rejection_fixture = payload_dry_run.build_correct_workspace_bridge_verification_evidence_payload_dry_run_result(
        rejection_fixture_names=(
            "missing_project_file_path",
            "wrong_project_file_path",
        ),
    )
    assert build_summary(result=missing_rejection_fixture)["status"] == "failed"

    ingest_open = payload_dry_run.build_correct_workspace_bridge_verification_evidence_payload_dry_run_result(
        payload_ingest_allowed=True,
    )
    assert build_summary(result=ingest_open)["status"] == "failed"

    payload_received = payload_dry_run.build_correct_workspace_bridge_verification_evidence_payload_dry_run_result(
        evidence_payload_received=True,
    )
    payload_summary = build_summary(result=payload_received)
    assert payload_summary["status"] == "failed"
    assert payload_summary["evidence_payload_received_count"] == 1

    evidence_ingested = payload_dry_run.build_correct_workspace_bridge_verification_evidence_payload_dry_run_result(
        evidence_payload_ingested=True,
    )
    ingested_summary = build_summary(result=evidence_ingested)
    assert ingested_summary["status"] == "failed"
    assert ingested_summary["evidence_payload_ingested_count"] == 1

    dirty_write = payload_dry_run.build_correct_workspace_bridge_verification_evidence_payload_dry_run_result(
        dirty_content_after=(
            "/Game/_MCP_Temp/DurableSaveGate/UserWidgetActual/"
            "WBP_DurableWidgetTreeActual"
        ),
    )
    assert build_summary(result=dirty_write)["status"] == "failed"

    print(
        "BP authoring durable executor authoring correct-workspace bridge verification evidence payload dry-run batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
