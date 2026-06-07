#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_rehearsal_readiness_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_rehearsal_readiness_contract as rehearsal_readiness  # noqa: E402
import bp_authoring_durable_live_evidence_refresh_contract as live_evidence  # noqa: E402
import bp_authoring_durable_ownership_marker_proof_contract as marker_proof  # noqa: E402
import bp_authoring_durable_rollback_cleanup_proof_contract as cleanup_proof  # noqa: E402
import bp_authoring_durable_save_gate_final_review_contract as save_review  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def main() -> int:
    manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    contract_summary = job_contract.summarize_manifests(manifests)
    executor_summary = manifest_executor.summarize_executor_policies(
        manifests,
        job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    live_contract = live_evidence.build_live_evidence_refresh_contract(
        True,
        {"verdict": {"status": "passed"}, "live_gate": {"status": "passed"}},
    )
    live_summary = live_evidence.summarize_live_evidence_refresh_contracts([live_contract])
    marker = marker_proof.build_ownership_marker_proof_contract(True, contract_summary)
    marker_summary = marker_proof.summarize_ownership_marker_proof_contracts([marker])
    cleanup = cleanup_proof.build_rollback_cleanup_proof_contract(True, contract_summary, marker)
    cleanup_summary = cleanup_proof.summarize_rollback_cleanup_proof_contracts([cleanup])
    save = save_review.build_save_gate_final_review_contract(True, contract_summary, executor_summary)
    save_summary = save_review.summarize_save_gate_final_review_contracts([save])
    contract = rehearsal_readiness.build_canary_rehearsal_readiness_contract(
        True,
        contract_summary["durable_canary_bridge_refresh_summary"],
        live_summary,
        marker_summary,
        cleanup_summary,
        save_summary,
    )
    assert contract["schema"] == rehearsal_readiness.CANARY_REHEARSAL_READINESS_SCHEMA
    assert contract["requested"] is True
    assert contract["rehearsal_readiness_review_complete"] is True
    assert contract["missing_rehearsal_prerequisite_count"] == 5
    assert "bridge_refresh_satisfied" in contract["missing_rehearsal_prerequisites"]
    assert "live_evidence_refresh_satisfied" in contract["missing_rehearsal_prerequisites"]
    assert "ownership_marker_write_readback" in contract["missing_rehearsal_prerequisites"]
    assert "rollback_cleanup_proof" in contract["missing_rehearsal_prerequisites"]
    assert "durable_save_enable_ready" in contract["missing_rehearsal_prerequisites"]
    assert contract["live_canary_rehearsal_ready"] is False
    assert contract["live_canary_rehearsal_attempted"] is False
    assert contract["canary_creation_attempted"] is False
    assert contract["canary_save_attempted"] is False
    assert contract["canary_cleanup_attempted"] is False
    assert contract["durable_executor_may_open_for_rehearsal"] is False
    assert contract["live_creation_command_count"] == 0
    assert contract["live_save_command_count"] == 0
    assert contract["live_cleanup_command_count"] == 0

    summary = rehearsal_readiness.summarize_canary_rehearsal_readiness_contracts([contract])
    assert summary == {
        "schema": rehearsal_readiness.CANARY_REHEARSAL_READINESS_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_rehearsal_readiness_count": 1,
        "rehearsal_readiness_review_complete_count": 1,
        "missing_rehearsal_prerequisite_count": 5,
        "live_canary_rehearsal_ready_count": 0,
        "live_canary_rehearsal_attempted_count": 0,
        "canary_creation_attempted_count": 0,
        "canary_save_attempted_count": 0,
        "canary_cleanup_attempted_count": 0,
        "durable_executor_may_open_for_rehearsal_count": 0,
        "live_creation_command_count": 0,
        "live_save_command_count": 0,
        "live_cleanup_command_count": 0,
    }

    print("BP authoring durable canary rehearsal readiness contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
