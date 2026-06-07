#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_live_preflight_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_live_preflight_contract as canary_live  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def main() -> int:
    manifest = job_contract.build_job_manifest(
        "durable_overwrite",
        "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints and overwrite if it exists with a Static Mesh Component.",
        temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    contract = manifest["durable_canary_live_preflight_contract"]
    assert contract["schema"] == canary_live.CANARY_LIVE_PREFLIGHT_CONTRACT_SCHEMA
    assert contract["requested"] is True
    assert contract["canary_asset_path"] == "/Game/_MCP_Temp/DurableCanary/BP_PlannerDurable_Canary"
    assert contract["canary_approval_gate_passed"] is True
    assert contract["read_only_live_preflight_allowed"] is True
    assert contract["read_only_live_command"] == canary_live.READ_ONLY_COMMAND
    assert contract["canary_execution_allowed_after_preflight"] is False
    assert contract["authoring_command_allowed"] is False
    assert contract["save_or_delete_allowed"] is False
    assert contract["cleanup_command_allowed"] is False
    assert contract["live_authoring_command_count"] == 0
    assert contract["live_save_or_delete_command_count"] == 0
    assert contract["live_cleanup_command_count"] == 0
    assert contract["result_schema"] == canary_live.CANARY_LIVE_PREFLIGHT_RESULT_SCHEMA
    assert "section_57_read_only_canary_preflight_only" in contract["blocked_by"]

    summary = canary_live.summarize_canary_live_preflight_contracts([contract])
    assert summary == {
        "schema": canary_live.CANARY_LIVE_PREFLIGHT_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_live_preflight_count": 1,
        "read_only_live_preflight_allowed_count": 1,
        "canary_execution_allowed_after_preflight_count": 0,
        "authoring_command_allowed_count": 0,
        "save_or_delete_allowed_count": 0,
        "cleanup_command_allowed_count": 0,
        "live_authoring_command_count": 0,
        "live_save_or_delete_command_count": 0,
        "live_cleanup_command_count": 0,
    }

    live_result = {
        "schema": canary_live.CANARY_LIVE_PREFLIGHT_RESULT_SCHEMA,
        "manifest_id": "durable_overwrite",
        "canary_asset_path": contract["canary_asset_path"],
        "status": "passed",
        "read_only": True,
        "authoring_attempted": False,
        "save_or_delete_attempted": False,
        "cleanup_attempted": False,
        "canary_execution_attempted": False,
        "asset_exists_check_performed": True,
        "asset_exists": False,
        "canary_execution_allowed_after_preflight": False,
    }
    live_summary = canary_live.summarize_canary_live_preflight_results([manifest], [live_result], live_requested=True)
    assert live_summary["status"] == "passed"
    assert live_summary["live_result_count"] == 1
    assert live_summary["passed_read_only_result_count"] == 1
    assert live_summary["authoring_attempted_count"] == 0
    assert live_summary["save_or_delete_attempted_count"] == 0
    assert live_summary["cleanup_attempted_count"] == 0
    assert live_summary["canary_execution_attempted_count"] == 0
    assert live_summary["canary_execution_allowed_after_preflight_count"] == 0

    default_manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    default_summary = job_contract.summarize_manifests(default_manifests)
    assert default_summary["durable_canary_live_preflight_request_count"] == 1
    assert default_summary["durable_canary_live_preflight_read_only_allowed_count"] == 1
    assert default_summary["durable_canary_live_preflight_execution_allowed_count"] == 0
    assert default_summary["durable_canary_live_preflight_authoring_command_allowed_count"] == 0
    assert default_summary["durable_canary_live_preflight_save_or_delete_allowed_count"] == 0
    assert default_summary["durable_canary_live_preflight_cleanup_command_allowed_count"] == 0
    assert default_summary["durable_canary_live_preflight_authoring_command_count"] == 0
    assert default_summary["durable_canary_live_preflight_save_or_delete_command_count"] == 0
    assert default_summary["durable_canary_live_preflight_cleanup_command_count"] == 0

    policy = manifest_executor.build_executor_policy(manifest, job_contract.DEFAULT_TEMP_PACKAGE_PATH)
    gate = policy["durable_executor_gate"]
    assert gate["canary_live_preflight_read_only_allowed"] is True
    assert gate["canary_live_preflight_execution_allowed"] is False
    assert gate["canary_live_preflight_authoring_allowed"] is False
    assert gate["canary_live_preflight_save_or_delete_allowed"] is False
    assert gate["canary_live_preflight_cleanup_allowed"] is False
    assert gate["canary_live_preflight_authoring_command_count"] == 0
    assert gate["canary_live_preflight_save_or_delete_command_count"] == 0
    assert gate["canary_live_preflight_cleanup_command_count"] == 0
    assert gate["save_or_delete_commands_allowed"] is False

    print("BP authoring durable canary live preflight contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
