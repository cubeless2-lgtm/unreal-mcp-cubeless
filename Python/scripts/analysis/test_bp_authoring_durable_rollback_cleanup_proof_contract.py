#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_rollback_cleanup_proof_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_ownership_marker_proof_contract as marker_proof  # noqa: E402
import bp_authoring_durable_rollback_cleanup_proof_contract as cleanup_proof  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402


def main() -> int:
    manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    contract_summary = job_contract.summarize_manifests(manifests)
    marker = marker_proof.build_ownership_marker_proof_contract(True, contract_summary)
    contract = cleanup_proof.build_rollback_cleanup_proof_contract(True, contract_summary, marker)
    assert contract["schema"] == cleanup_proof.ROLLBACK_CLEANUP_PROOF_SCHEMA
    assert contract["requested"] is True
    assert contract["recovery_matrix_ready"] is True
    assert contract["cleanup_proof_required"] is True
    assert contract["ownership_marker_write_readback_satisfied"] is False
    assert contract["cleanup_proof_satisfied"] is False
    assert contract["cleanup_allowed"] is False
    assert contract["delete_allowed"] is False
    assert contract["delete_preexisting_asset_allowed"] is False
    assert contract["delete_without_marker_allowed"] is False
    assert contract["durable_executor_may_open_after_cleanup_proof"] is False
    assert contract["live_cleanup_command_count"] == 0
    assert contract["live_delete_command_count"] == 0
    assert "section_67_cleanup_proof_not_satisfied" in contract["blocked_by"]

    summary = cleanup_proof.summarize_rollback_cleanup_proof_contracts([contract])
    assert summary == {
        "schema": cleanup_proof.ROLLBACK_CLEANUP_PROOF_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_rollback_cleanup_proof_count": 1,
        "recovery_matrix_ready_count": 1,
        "cleanup_proof_required_count": 1,
        "ownership_marker_write_readback_satisfied_count": 0,
        "cleanup_proof_satisfied_count": 0,
        "cleanup_allowed_count": 0,
        "delete_allowed_count": 0,
        "delete_preexisting_asset_allowed_count": 0,
        "delete_without_marker_allowed_count": 0,
        "durable_executor_may_open_after_cleanup_proof_count": 0,
        "live_cleanup_command_count": 0,
        "live_delete_command_count": 0,
    }

    print("BP authoring durable rollback cleanup proof contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
