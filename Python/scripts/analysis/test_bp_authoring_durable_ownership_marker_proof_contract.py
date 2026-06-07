#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_ownership_marker_proof_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_ownership_marker_proof_contract as marker_proof  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402


def main() -> int:
    manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    contract_summary = job_contract.summarize_manifests(manifests)
    contract = marker_proof.build_ownership_marker_proof_contract(True, contract_summary)
    assert contract["schema"] == marker_proof.OWNERSHIP_MARKER_PROOF_SCHEMA
    assert contract["requested"] is True
    assert contract["ownership_marker_policy_ready"] is True
    assert contract["write_readback_proof_required"] is True
    assert contract["marker_write_performed"] is False
    assert contract["marker_readback_verified"] is False
    assert contract["write_readback_proof_satisfied"] is False
    assert contract["cleanup_allowed_after_marker_proof"] is False
    assert contract["delete_allowed_after_marker_proof"] is False
    assert contract["durable_executor_may_open_after_marker_proof"] is False
    assert contract["live_write_command_count"] == 0
    assert contract["live_readback_command_count"] == 0
    assert contract["live_delete_command_count"] == 0
    assert "section_66_marker_write_readback_proof_not_performed" in contract["blocked_by"]

    summary = marker_proof.summarize_ownership_marker_proof_contracts([contract])
    assert summary == {
        "schema": marker_proof.OWNERSHIP_MARKER_PROOF_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_ownership_marker_proof_count": 1,
        "ownership_marker_policy_ready_count": 1,
        "write_readback_proof_required_count": 1,
        "marker_write_performed_count": 0,
        "marker_readback_verified_count": 0,
        "write_readback_proof_satisfied_count": 0,
        "cleanup_allowed_after_marker_proof_count": 0,
        "delete_allowed_after_marker_proof_count": 0,
        "durable_executor_may_open_after_marker_proof_count": 0,
        "live_write_command_count": 0,
        "live_readback_command_count": 0,
        "live_delete_command_count": 0,
    }

    print("BP authoring durable ownership marker proof contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
