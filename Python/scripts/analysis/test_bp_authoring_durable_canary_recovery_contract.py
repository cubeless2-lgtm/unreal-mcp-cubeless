#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_recovery_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_recovery_contract as recovery  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def main() -> int:
    manifest = job_contract.build_job_manifest(
        "durable_overwrite",
        "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints and overwrite if it exists with a Static Mesh Component.",
        temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    contract = manifest["durable_canary_recovery_matrix_contract"]
    assert contract["schema"] == recovery.CANARY_RECOVERY_SCHEMA
    assert contract["requested"] is True
    assert contract["canary_asset_path"] == "/Game/_MCP_Temp/DurableCanary/BP_PlannerDurable_Canary"
    assert contract["canary_live_preflight_allowed"] is True
    assert contract["recovery_matrix_defined"] is True
    assert contract["recovery_matrix_ready"] is True
    assert contract["scenario_count"] == 6
    assert contract["cleanup_requires_ownership_marker"] is True
    assert contract["cleanup_requires_preflight_asset_absent"] is True
    assert contract["cleanup_requires_created_asset_path_match"] is True
    assert contract["cleanup_command_allowed"] is False
    assert contract["delete_command_allowed"] is False
    assert contract["save_command_allowed"] is False
    assert contract["authoring_command_allowed"] is False
    assert contract["live_cleanup_command_count"] == 0
    assert contract["live_delete_command_count"] == 0
    assert contract["live_save_command_count"] == 0
    assert contract["live_authoring_command_count"] == 0
    assert "section_58_recovery_matrix_report_only" in contract["blocked_by"]
    assert {item["id"] for item in contract["scenarios"]} == {
        "preflight_asset_absent",
        "preflight_asset_present",
        "creation_fails_before_marker",
        "creation_fails_after_marker",
        "compile_or_save_blocked",
        "cleanup_marker_valid",
    }

    summary = recovery.summarize_canary_recovery_matrices([contract])
    assert summary == {
        "schema": recovery.CANARY_RECOVERY_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_recovery_count": 1,
        "recovery_matrix_ready_count": 1,
        "scenario_count": 6,
        "cleanup_command_allowed_count": 0,
        "delete_command_allowed_count": 0,
        "save_command_allowed_count": 0,
        "authoring_command_allowed_count": 0,
        "live_cleanup_command_count": 0,
        "live_delete_command_count": 0,
        "live_save_command_count": 0,
        "live_authoring_command_count": 0,
    }

    default_manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    default_summary = job_contract.summarize_manifests(default_manifests)
    assert default_summary["durable_canary_recovery_request_count"] == 1
    assert default_summary["durable_canary_recovery_matrix_ready_count"] == 1
    assert default_summary["durable_canary_recovery_scenario_count"] == 6
    assert default_summary["durable_canary_recovery_cleanup_command_allowed_count"] == 0
    assert default_summary["durable_canary_recovery_delete_command_allowed_count"] == 0
    assert default_summary["durable_canary_recovery_save_command_allowed_count"] == 0
    assert default_summary["durable_canary_recovery_authoring_command_allowed_count"] == 0
    assert default_summary["durable_canary_recovery_live_cleanup_command_count"] == 0
    assert default_summary["durable_canary_recovery_live_delete_command_count"] == 0
    assert default_summary["durable_canary_recovery_live_save_command_count"] == 0
    assert default_summary["durable_canary_recovery_live_authoring_command_count"] == 0

    gate = manifest_executor.build_executor_policy(manifest, job_contract.DEFAULT_TEMP_PACKAGE_PATH)[
        "durable_executor_gate"
    ]
    assert gate["canary_recovery_matrix_ready"] is True
    assert gate["canary_recovery_scenario_count"] == 6
    assert gate["canary_recovery_cleanup_allowed"] is False
    assert gate["canary_recovery_delete_allowed"] is False
    assert gate["canary_recovery_save_allowed"] is False
    assert gate["canary_recovery_authoring_allowed"] is False
    assert gate["canary_recovery_live_cleanup_command_count"] == 0
    assert gate["canary_recovery_live_delete_command_count"] == 0
    assert gate["canary_recovery_live_save_command_count"] == 0
    assert gate["canary_recovery_live_authoring_command_count"] == 0

    print("BP authoring durable canary recovery contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
