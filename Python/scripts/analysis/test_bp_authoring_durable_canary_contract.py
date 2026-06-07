#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_contract as canary  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def main() -> int:
    manifest = job_contract.build_job_manifest(
        "durable_overwrite",
        "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints and overwrite if it exists with a Static Mesh Component.",
        temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    contract = manifest["durable_canary_prep_contract"]
    assert contract["schema"] == canary.CANARY_PREP_SCHEMA
    assert contract["requested"] is True
    assert contract["source_target_asset_path"] == "/Game/Blueprints/BP_PlannerDurable"
    assert contract["canary_package_path"] == canary.DEFAULT_CANARY_PACKAGE_PATH
    assert contract["canary_asset_path"] == "/Game/_MCP_Temp/DurableCanary/BP_PlannerDurable_Canary"
    assert contract["canary_package_allowlisted"] is True
    assert contract["canary_prep_ready"] is True
    assert contract["canary_live_execution_allowed"] is False
    assert contract["general_blueprints_package_allowed"] is False
    assert contract["save_true_allowed"] is False
    assert contract["save_asset_allowed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["cleanup_requires_ownership_marker"] is True
    assert "section_55_prep_only_no_live_canary" in contract["blocked_by"]

    summary = canary.summarize_canary_prep_contracts([contract])
    assert summary == {
        "schema": canary.CANARY_PREP_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_prep_count": 1,
        "canary_prep_ready_count": 1,
        "canary_live_execution_allowed_count": 0,
        "general_blueprints_package_allowed_count": 0,
        "save_true_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
    }

    default_manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    default_summary = job_contract.summarize_manifests(default_manifests)
    assert default_summary["durable_canary_prep_request_count"] == 1
    assert default_summary["durable_canary_prep_ready_count"] == 1
    assert default_summary["durable_canary_live_execution_allowed_count"] == 0
    assert default_summary["durable_canary_general_blueprints_package_allowed_count"] == 0
    assert default_summary["durable_canary_save_true_allowed_count"] == 0
    assert default_summary["durable_canary_save_asset_allowed_count"] == 0
    assert default_summary["durable_canary_delete_asset_allowed_count"] == 0

    policy = manifest_executor.build_executor_policy(manifest, job_contract.DEFAULT_TEMP_PACKAGE_PATH)
    gate = policy["durable_executor_gate"]
    assert gate["canary_prep_ready"] is True
    assert gate["canary_live_execution_allowed"] is False
    assert gate["canary_general_blueprints_package_allowed"] is False
    assert gate["canary_save_true_allowed"] is False
    assert gate["canary_save_asset_allowed"] is False
    assert gate["canary_delete_asset_allowed"] is False
    assert gate["save_or_delete_commands_allowed"] is False

    print("BP authoring durable canary contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
