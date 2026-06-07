#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_creation_boundary_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_creation_boundary_contract as creation_boundary  # noqa: E402
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
    contract = creation_boundary.build_canary_creation_boundary_contract(
        True,
        contract_summary,
        executor_summary,
    )
    assert contract["schema"] == creation_boundary.CANARY_CREATION_BOUNDARY_SCHEMA
    assert contract["requested"] is True
    assert contract["canary_creation_boundary_defined"] is True
    assert contract["canary_prep_ready_count"] == 1
    assert contract["canary_approval_gate_passed_count"] == 1
    assert contract["read_only_preflight_allowed_count"] == 1
    assert contract["bridge_refresh_satisfied_count"] == 0
    assert contract["create_blueprint_allowed"] is False
    assert contract["save_command_allowed"] is False
    assert contract["delete_command_allowed"] is False
    assert contract["cleanup_command_allowed"] is False
    assert contract["live_canary_creation_allowed"] is False
    assert contract["durable_executor_may_open_for_creation"] is False
    assert contract["live_creation_command_count"] == 0
    assert contract["live_save_or_delete_command_count"] == 0
    assert "section_65_creation_boundary_does_not_allow_create_blueprint" in contract["blocked_by"]

    summary = creation_boundary.summarize_canary_creation_boundary_contracts([contract])
    assert summary == {
        "schema": creation_boundary.CANARY_CREATION_BOUNDARY_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_creation_boundary_count": 1,
        "canary_creation_boundary_defined_count": 1,
        "create_blueprint_allowed_count": 0,
        "save_command_allowed_count": 0,
        "delete_command_allowed_count": 0,
        "cleanup_command_allowed_count": 0,
        "live_canary_creation_allowed_count": 0,
        "durable_executor_may_open_for_creation_count": 0,
        "live_creation_command_count": 0,
        "live_save_or_delete_command_count": 0,
    }

    print("BP authoring durable canary creation boundary contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
