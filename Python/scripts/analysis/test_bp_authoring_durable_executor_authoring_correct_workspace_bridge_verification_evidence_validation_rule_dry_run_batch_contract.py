#!/usr/bin/env python
"""Offline smoke tests for Sections 529-536 bridge evidence validation rule dry-run."""

from __future__ import annotations

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batch_contract as payload_dry_run
import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batch_contract as validation_dry_run


def build_upstream_summary() -> dict:
    summary = {
        "schema": (
            payload_dry_run
            .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in validation_dry_run.UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in validation_dry_run.UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_summary(
    result: dict | None = None,
    upstream_summary: dict | None = None,
) -> dict:
    contract = validation_dry_run.build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batch_contract(
        requested=True,
        section_521_528_verification_evidence_payload_dry_run_summary=(
            upstream_summary or build_upstream_summary()
        ),
        correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result=(
            result
            or validation_dry_run.build_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result()
        ),
    )
    return validation_dry_run.summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batches(
        [contract]
    )


def assert_all_path_counts(summary: dict, value: int) -> None:
    for key in validation_dry_run.CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_PATH_COUNT_KEYS:
        assert summary[key] == value, key


def assert_all_blocked_counts_zero(summary: dict) -> None:
    for key in validation_dry_run.BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key


def main() -> int:
    result = validation_dry_run.build_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result()
    contract = validation_dry_run.build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batch_contract(
        requested=True,
        section_521_528_verification_evidence_payload_dry_run_summary=build_upstream_summary(),
        correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result=result,
    )
    assert (
        contract[
            "correct_workspace_bridge_verification_evidence_validation_rule_dry_run_ready"
        ]
        is True
    )
    assert contract["verification_evidence_validation_not_executed"] is True
    assert contract["schema_validation_rules_recorded"] is True
    assert contract["identity_validation_rules_recorded"] is True
    assert contract["read_only_probe_validation_rules_recorded"] is True
    assert contract["dirty_state_validation_rules_recorded"] is True
    assert (
        contract["timestamp_and_placeholder_rejection_rules_recorded"] is True
    )
    assert contract["validation_execution_and_admission_still_blocked"] is True
    assert contract["validation_rule_dry_run_no_write_boundary_verified"] is True

    summary = validation_dry_run.summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batch_count"
        ]
        == 1
    )
    for key in (
        "section_521_528_summary_schema_matches_count",
        "section_521_528_summary_passed_count",
        "section_521_528_verification_evidence_payload_dry_run_ready_count",
        "section_521_528_outputs_closed_count",
        "result_schema_matches_count",
        "verification_evidence_validation_rule_dry_run_checkpoint_satisfied_count",
        "schema_validation_rules_recorded_count",
        "identity_validation_rules_recorded_count",
        "read_only_probe_validation_rules_recorded_count",
        "dirty_state_validation_rules_recorded_count",
        "timestamp_and_placeholder_rejection_rules_recorded_count",
        "validation_execution_and_admission_still_blocked_count",
        "validation_rule_dry_run_no_write_boundary_verified_count",
        "validation_rule_dry_run_compile_save_write_outputs_blocked_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
    ):
        assert summary[key] == 1, key
    assert_all_path_counts(summary, 1)
    assert_all_blocked_counts_zero(summary)

    missing_upstream = build_upstream_summary()
    missing_upstream["section_528_payload_dry_run_release_ready_count"] = 0
    assert build_summary(upstream_summary=missing_upstream)["status"] == "failed"

    missing_required_field = validation_dry_run.build_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result(
        required_evidence_fields=(
            "project_file_path",
            "editor_executable_path",
            "bridge_host",
        ),
    )
    assert build_summary(result=missing_required_field)["status"] == "failed"

    wrong_identity = validation_dry_run.build_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result(
        project_file_path=payload_dry_run.DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH,
    )
    assert build_summary(result=wrong_identity)["status"] == "failed"

    missing_probe_rule = validation_dry_run.build_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result(
        read_only_probe_validation_rules_recorded=False,
    )
    assert build_summary(result=missing_probe_rule)["status"] == "failed"

    missing_placeholder_rejection = validation_dry_run.build_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result(
        placeholder_rejection_rules_recorded=False,
    )
    assert build_summary(result=missing_placeholder_rejection)["status"] == "failed"

    validation_open = validation_dry_run.build_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result(
        evidence_schema_validation_allowed=True,
    )
    assert build_summary(result=validation_open)["status"] == "failed"

    validation_executed = validation_dry_run.build_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result(
        evidence_schema_validation_executed=True,
    )
    executed_summary = build_summary(result=validation_executed)
    assert executed_summary["status"] == "failed"
    assert executed_summary["evidence_schema_validation_executed_count"] == 1

    evidence_admitted = validation_dry_run.build_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result(
        verification_evidence_admitted=True,
    )
    admitted_summary = build_summary(result=evidence_admitted)
    assert admitted_summary["status"] == "failed"
    assert admitted_summary["verification_evidence_admitted_count"] == 1

    dirty_write = validation_dry_run.build_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result(
        dirty_content_after=(
            "/Game/_MCP_Temp/DurableSaveGate/UserWidgetActual/"
            "WBP_DurableWidgetTreeActual"
        ),
    )
    assert build_summary(result=dirty_write)["status"] == "failed"

    print(
        "BP authoring durable executor authoring correct-workspace bridge verification evidence validation rule dry-run batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
