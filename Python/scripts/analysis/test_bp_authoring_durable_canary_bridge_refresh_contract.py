#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_bridge_refresh_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_bridge_refresh_contract as bridge_refresh  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def main() -> int:
    manifest = job_contract.build_job_manifest(
        "durable_overwrite",
        "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints and overwrite if it exists with a Static Mesh Component.",
        temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    contract = manifest["durable_canary_bridge_refresh_contract"]
    assert contract["schema"] == bridge_refresh.CANARY_BRIDGE_REFRESH_SCHEMA
    assert contract["requested"] is True
    assert contract["canary_asset_path"] == "/Game/_MCP_Temp/DurableCanary/BP_PlannerDurable_Canary"
    assert contract["read_only_preflight_allowed"] is True
    assert contract["bridge_refresh_required"] is True
    assert contract["bridge_reachable"] is False
    assert contract["read_only_result_refreshed"] is False
    assert contract["bridge_refresh_satisfied"] is False
    assert contract["canary_execution_allowed_after_refresh"] is False
    assert contract["durable_executor_may_open_after_refresh"] is False
    assert contract["save_or_delete_allowed"] is False
    assert contract["cleanup_command_allowed"] is False
    assert contract["live_authoring_command_count"] == 0
    assert contract["live_save_or_delete_command_count"] == 0
    assert contract["live_cleanup_command_count"] == 0
    assert "unrealmcp_bridge_refresh_not_reachable" in contract["blocked_by"]
    assert "canary_read_only_preflight_result_not_refreshed" in contract["blocked_by"]

    refreshed = bridge_refresh.build_bridge_refresh_contract(
        requested=True,
        canary_live_preflight_contract=manifest["durable_canary_live_preflight_contract"],
        bridge_status={
            "mcp_server": bridge_refresh.EXPECTED_MCP_SERVER,
            "host": bridge_refresh.EXPECTED_BRIDGE_HOST,
            "port": bridge_refresh.EXPECTED_BRIDGE_PORT,
            "reachable": True,
        },
        refreshed_live_result={
            "status": "passed",
            "read_only": True,
            "asset_exists_check_performed": True,
            "authoring_attempted": False,
            "save_or_delete_attempted": False,
            "cleanup_attempted": False,
            "canary_execution_attempted": False,
        },
    )
    assert refreshed["bridge_reachable"] is True
    assert refreshed["read_only_result_refreshed"] is True
    assert refreshed["bridge_refresh_satisfied"] is True
    assert refreshed["canary_execution_allowed_after_refresh"] is False
    assert refreshed["durable_executor_may_open_after_refresh"] is False

    summary = bridge_refresh.summarize_bridge_refresh_contracts([contract])
    assert summary == {
        "schema": bridge_refresh.CANARY_BRIDGE_REFRESH_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_bridge_refresh_count": 1,
        "read_only_preflight_allowed_count": 1,
        "bridge_refresh_required_count": 1,
        "bridge_reachable_count": 0,
        "read_only_result_refreshed_count": 0,
        "bridge_refresh_satisfied_count": 0,
        "canary_execution_allowed_after_refresh_count": 0,
        "durable_executor_may_open_after_refresh_count": 0,
        "authoring_command_allowed_count": 0,
        "save_or_delete_allowed_count": 0,
        "cleanup_command_allowed_count": 0,
        "live_authoring_command_count": 0,
        "live_save_or_delete_command_count": 0,
        "live_cleanup_command_count": 0,
    }

    default_manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    default_summary = job_contract.summarize_manifests(default_manifests)
    assert default_summary["durable_canary_bridge_refresh_request_count"] == 1
    assert default_summary["durable_canary_bridge_refresh_required_count"] == 1
    assert default_summary["durable_canary_bridge_refresh_reachable_count"] == 0
    assert default_summary["durable_canary_bridge_refresh_read_only_result_refreshed_count"] == 0
    assert default_summary["durable_canary_bridge_refresh_satisfied_count"] == 0
    assert default_summary["durable_canary_bridge_refresh_execution_allowed_count"] == 0
    assert default_summary["durable_canary_bridge_refresh_executor_may_open_count"] == 0
    assert default_summary["durable_canary_bridge_refresh_save_or_delete_allowed_count"] == 0
    assert default_summary["durable_canary_bridge_refresh_cleanup_command_allowed_count"] == 0

    policy = manifest_executor.build_executor_policy(manifest, job_contract.DEFAULT_TEMP_PACKAGE_PATH)
    gate = policy["durable_executor_gate"]
    assert gate["canary_bridge_refresh_required"] is True
    assert gate["canary_bridge_refresh_reachable"] is False
    assert gate["canary_bridge_refresh_read_only_result_refreshed"] is False
    assert gate["canary_bridge_refresh_satisfied"] is False
    assert gate["canary_bridge_refresh_execution_allowed"] is False
    assert gate["canary_bridge_refresh_executor_may_open"] is False
    assert gate["canary_bridge_refresh_save_or_delete_allowed"] is False
    assert gate["canary_bridge_refresh_cleanup_allowed"] is False
    assert gate["canary_bridge_refresh_authoring_command_count"] == 0
    assert gate["canary_bridge_refresh_save_or_delete_command_count"] == 0
    assert gate["canary_bridge_refresh_cleanup_command_count"] == 0

    print("BP authoring durable canary bridge refresh contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
