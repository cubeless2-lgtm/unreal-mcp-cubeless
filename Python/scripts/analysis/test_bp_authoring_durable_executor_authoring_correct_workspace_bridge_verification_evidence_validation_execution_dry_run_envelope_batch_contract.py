#!/usr/bin/env python
"""Offline smoke tests for Sections 537-544 bridge validation execution envelope."""

from __future__ import annotations

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batch_contract as validation_envelope
import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batch_contract as validation_rules


def build_upstream_summary() -> dict:
    summary = {
        "schema": (
            validation_rules
            .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_BATCH_SUMMARY_SCHEMA
        ),
        "status": "passed",
    }
    for key in validation_envelope.UPSTREAM_READY_COUNT_KEYS:
        summary[key] = 1
    for key in validation_envelope.UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS:
        summary[key] = 0
    return summary


def build_summary(
    result: dict | None = None,
    upstream_summary: dict | None = None,
) -> dict:
    contract = validation_envelope.build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batch_contract(
        requested=True,
        section_529_536_verification_evidence_validation_rule_dry_run_summary=(
            upstream_summary or build_upstream_summary()
        ),
        correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result=(
            result
            or validation_envelope.build_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result()
        ),
    )
    return validation_envelope.summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batches(
        [contract]
    )


def assert_all_path_counts(summary: dict, value: int) -> None:
    for key in validation_envelope.CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_PATH_COUNT_KEYS:
        assert summary[key] == value, key


def assert_all_blocked_counts_zero(summary: dict) -> None:
    for key in validation_envelope.BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key


def main() -> int:
    result = validation_envelope.build_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result()
    contract = validation_envelope.build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batch_contract(
        requested=True,
        section_529_536_verification_evidence_validation_rule_dry_run_summary=build_upstream_summary(),
        correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result=result,
    )
    assert (
        contract[
            "correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_ready"
        ]
        is True
    )
    assert contract["verification_evidence_validation_execution_still_blocked"] is True
    assert contract["validation_execution_scope_recorded"] is True
    assert contract["real_evidence_payload_required"] is True
    assert contract["validation_rule_set_binding_required"] is True
    assert contract["validation_execution_authorization_still_required"] is True
    assert contract["validation_result_admission_still_blocked"] is True
    assert contract["validation_execution_dry_run_no_write_boundary_verified"] is True

    summary = validation_envelope.summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batch_count"
        ]
        == 1
    )
    for key in (
        "section_529_536_summary_schema_matches_count",
        "section_529_536_summary_passed_count",
        "section_529_536_verification_evidence_validation_rule_dry_run_ready_count",
        "section_529_536_outputs_closed_count",
        "result_schema_matches_count",
        "validation_execution_dry_run_envelope_checkpoint_satisfied_count",
        "validation_execution_scope_recorded_count",
        "real_evidence_payload_required_count",
        "validation_rule_set_binding_required_count",
        "validation_execution_authorization_still_required_count",
        "validation_result_admission_still_blocked_count",
        "validation_execution_dry_run_no_write_boundary_verified_count",
        "validation_execution_dry_run_compile_save_write_outputs_blocked_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
    ):
        assert summary[key] == 1, key
    assert_all_path_counts(summary, 1)
    assert_all_blocked_counts_zero(summary)

    missing_upstream = build_upstream_summary()
    missing_upstream["section_536_validation_rule_dry_run_release_ready_count"] = 0
    assert build_summary(upstream_summary=missing_upstream)["status"] == "failed"

    missing_scope_step = validation_envelope.build_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result(
        validation_execution_scope=(
            "payload_load",
            "required_field_presence_validate",
        ),
    )
    assert build_summary(result=missing_scope_step)["status"] == "failed"

    wrong_identity = validation_envelope.build_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result(
        bridge_port_number=8090,
    )
    assert build_summary(result=wrong_identity)["status"] == "failed"

    payload_received = validation_envelope.build_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result(
        evidence_payload_received=True,
    )
    payload_summary = build_summary(result=payload_received)
    assert payload_summary["status"] == "failed"
    assert payload_summary["evidence_payload_received_count"] == 1

    validation_allowed = validation_envelope.build_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result(
        validation_execution_allowed=True,
    )
    assert build_summary(result=validation_allowed)["status"] == "failed"

    validation_dispatched = validation_envelope.build_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result(
        validation_execution_command_dispatched=True,
    )
    dispatched_summary = build_summary(result=validation_dispatched)
    assert dispatched_summary["status"] == "failed"
    assert dispatched_summary["validation_execution_command_dispatched_count"] == 1

    validation_executed = validation_envelope.build_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result(
        validation_execution_command_executed=True,
    )
    executed_summary = build_summary(result=validation_executed)
    assert executed_summary["status"] == "failed"
    assert executed_summary["validation_execution_command_executed_count"] == 1

    evidence_admitted = validation_envelope.build_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result(
        verification_evidence_admitted=True,
    )
    admitted_summary = build_summary(result=evidence_admitted)
    assert admitted_summary["status"] == "failed"
    assert admitted_summary["verification_evidence_admitted_count"] == 1

    dirty_write = validation_envelope.build_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result(
        dirty_content_after=(
            "/Game/_MCP_Temp/DurableSaveGate/UserWidgetActual/"
            "WBP_DurableWidgetTreeActual"
        ),
    )
    assert build_summary(result=dirty_write)["status"] == "failed"

    print(
        "BP authoring durable executor authoring correct-workspace bridge verification evidence validation execution dry-run envelope batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
