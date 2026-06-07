#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_rehearsal_promotion_barrier_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_bridge_recovery_readiness_contract as bridge_recovery  # noqa: E402
import bp_authoring_durable_canary_command_allowlist_contract as command_allowlist  # noqa: E402
import bp_authoring_durable_canary_read_only_retry_envelope_contract as retry_envelope  # noqa: E402
import bp_authoring_durable_canary_read_only_retry_result_admission_contract as result_admission  # noqa: E402
import bp_authoring_durable_canary_rehearsal_promotion_barrier_contract as promotion_barrier  # noqa: E402
import bp_authoring_durable_canary_rehearsal_readiness_contract as rehearsal_readiness  # noqa: E402
import bp_authoring_durable_live_evidence_refresh_contract as live_evidence  # noqa: E402
import bp_authoring_durable_ownership_marker_proof_contract as marker_proof  # noqa: E402
import bp_authoring_durable_rollback_cleanup_proof_contract as cleanup_proof  # noqa: E402
import bp_authoring_durable_save_gate_final_review_contract as save_review  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def build_current_summaries() -> tuple[dict, dict, dict, dict, dict]:
    manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    contract_summary = job_contract.summarize_manifests(manifests)
    executor_summary = manifest_executor.summarize_executor_policies(
        manifests,
        job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    recovery = bridge_recovery.build_bridge_recovery_readiness_contract(
        True,
        {
            "mcp_config_present": True,
            "server_defined": True,
            "command": bridge_recovery.EXPECTED_COMMAND,
            "args": [
                "--directory",
                bridge_recovery.EXPECTED_DIRECTORY_ARG,
                "run",
                "--python",
                bridge_recovery.EXPECTED_PYTHON_VERSION,
                bridge_recovery.EXPECTED_SERVER_SCRIPT,
            ],
            "directory_arg": bridge_recovery.EXPECTED_DIRECTORY_ARG,
            "python_version": bridge_recovery.EXPECTED_PYTHON_VERSION,
            "python_dir_exists": True,
            "server_script_exists": True,
            "uv_available": True,
        },
    )
    allowlist = command_allowlist.build_canary_command_allowlist_contract(True, executor_summary)
    envelope = retry_envelope.build_canary_read_only_retry_envelope_contract(
        True,
        bridge_recovery.summarize_bridge_recovery_readiness_contracts([recovery]),
        contract_summary["durable_canary_live_preflight_summary"],
        command_allowlist.summarize_canary_command_allowlist_contracts([allowlist]),
    )
    admission = result_admission.build_canary_read_only_retry_result_admission_contract(
        True,
        retry_envelope.summarize_canary_read_only_retry_envelopes([envelope]),
    )
    retry_admission_summary = result_admission.summarize_canary_read_only_retry_result_admissions([admission])
    live_contract = live_evidence.build_live_evidence_refresh_contract(
        True,
        {"verdict": {"status": "passed"}, "live_gate": {"status": "passed"}},
    )
    marker = marker_proof.build_ownership_marker_proof_contract(True, contract_summary)
    marker_summary = marker_proof.summarize_ownership_marker_proof_contracts([marker])
    cleanup = cleanup_proof.build_rollback_cleanup_proof_contract(True, contract_summary, marker)
    cleanup_summary = cleanup_proof.summarize_rollback_cleanup_proof_contracts([cleanup])
    save = save_review.build_save_gate_final_review_contract(True, contract_summary, executor_summary)
    save_summary = save_review.summarize_save_gate_final_review_contracts([save])
    rehearsal = rehearsal_readiness.build_canary_rehearsal_readiness_contract(
        True,
        contract_summary["durable_canary_bridge_refresh_summary"],
        live_evidence.summarize_live_evidence_refresh_contracts([live_contract]),
        marker_summary,
        cleanup_summary,
        save_summary,
    )
    rehearsal_summary = rehearsal_readiness.summarize_canary_rehearsal_readiness_contracts([rehearsal])
    return retry_admission_summary, rehearsal_summary, marker_summary, cleanup_summary, save_summary


def main() -> int:
    retry_admission_summary, rehearsal_summary, marker_summary, cleanup_summary, save_summary = build_current_summaries()
    contract = promotion_barrier.build_canary_rehearsal_promotion_barrier_contract(
        True,
        retry_admission_summary,
        rehearsal_summary,
        marker_summary,
        cleanup_summary,
        save_summary,
    )
    assert contract["schema"] == promotion_barrier.CANARY_REHEARSAL_PROMOTION_BARRIER_SCHEMA
    assert contract["requested"] is True
    assert contract["promotion_barrier_defined"] is True
    assert contract["read_only_result_admitted"] is False
    assert contract["rehearsal_readiness_review_complete"] is True
    assert contract["promotion_inputs_satisfied"] is False
    assert contract["promotion_execution_release_present"] is False
    assert contract["missing_promotion_prerequisite_count"] == 7
    assert "read_only_retry_result_admitted" in contract["missing_promotion_prerequisites"]
    assert "live_canary_rehearsal_ready" in contract["missing_promotion_prerequisites"]
    assert "ownership_marker_write_readback" in contract["missing_promotion_prerequisites"]
    assert "rollback_cleanup_proof" in contract["missing_promotion_prerequisites"]
    assert "durable_save_enable_ready" in contract["missing_promotion_prerequisites"]
    assert "explicit_live_canary_rehearsal_authorization" in contract["missing_promotion_prerequisites"]
    assert "separate_durable_rehearsal_execution_release" in contract["missing_promotion_prerequisites"]
    assert contract["canary_rehearsal_promotion_allowed"] is False
    assert contract["live_canary_rehearsal_allowed"] is False
    assert contract["live_canary_rehearsal_performed"] is False
    assert contract["canary_creation_allowed"] is False
    assert contract["canary_save_allowed"] is False
    assert contract["canary_cleanup_allowed"] is False
    assert contract["durable_executor_may_open_after_promotion"] is False
    assert contract["durable_authoring_allowed"] is False
    assert contract["save_delete_rename_allowed"] is False
    assert contract["cleanup_allowed"] is False

    summary = promotion_barrier.summarize_canary_rehearsal_promotion_barriers([contract])
    assert summary == {
        "schema": promotion_barrier.CANARY_REHEARSAL_PROMOTION_BARRIER_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_rehearsal_promotion_barrier_count": 1,
        "promotion_barrier_defined_count": 1,
        "read_only_result_admitted_count": 0,
        "rehearsal_readiness_review_complete_count": 1,
        "promotion_inputs_satisfied_count": 0,
        "promotion_execution_release_present_count": 0,
        "missing_promotion_prerequisite_count": 7,
        "canary_rehearsal_promotion_allowed_count": 0,
        "live_canary_rehearsal_allowed_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_promotion_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_creation_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
    }

    future_contract = promotion_barrier.build_canary_rehearsal_promotion_barrier_contract(
        True,
        {
            **retry_admission_summary,
            "read_only_result_admitted_count": 1,
        },
        {
            **rehearsal_summary,
            "live_canary_rehearsal_ready_count": 1,
        },
        {
            **marker_summary,
            "write_readback_proof_satisfied_count": 1,
        },
        {
            **cleanup_summary,
            "cleanup_proof_satisfied_count": 1,
        },
        {
            **save_summary,
            "durable_save_enable_ready_count": 1,
        },
        explicit_live_canary_rehearsal_authorization=True,
    )
    assert future_contract["promotion_inputs_satisfied"] is True
    assert future_contract["missing_promotion_prerequisite_count"] == 1
    assert future_contract["missing_promotion_prerequisites"] == ["separate_durable_rehearsal_execution_release"]
    assert future_contract["promotion_execution_release_present"] is False
    assert future_contract["canary_rehearsal_promotion_allowed"] is False
    assert future_contract["durable_executor_may_open_after_promotion"] is False

    print("BP authoring durable canary rehearsal promotion barrier contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
