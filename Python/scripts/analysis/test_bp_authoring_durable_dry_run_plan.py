#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_dry_run_plan.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_dry_run_plan as dry_run  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def main() -> int:
    manifest = job_contract.build_job_manifest(
        "durable_overwrite",
        "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints and overwrite if it exists with a Static Mesh Component.",
        temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    plan = manifest["durable_dry_run_plan_contract"]
    assert plan["schema"] == dry_run.DRY_RUN_PLAN_SCHEMA
    assert plan["requested"] is True
    assert plan["target_asset_path"] == "/Game/Blueprints/BP_PlannerDurable"
    assert plan["dry_run_plan_created"] is True
    assert plan["dry_run_plan_valid"] is True
    assert plan["plan_step_count"] == 6
    assert plan["execution_command_plan"] == []
    assert plan["live_command_count"] == 0
    assert plan["durable_executor_may_execute"] is False
    assert plan["durable_authoring_allowed"] is False
    assert plan["save_allowed"] is False
    assert plan["delete_allowed"] is False
    assert plan["rename_allowed"] is False
    assert "save_asset" in plan["forbidden_commands"]
    assert "delete_asset" in plan["forbidden_commands"]
    assert all(step["mode"] == "offline_report_only" for step in plan["plan_steps"])
    assert all(step["live_command_allowed"] is False for step in plan["plan_steps"])
    assert all(step["command"] == "" for step in plan["plan_steps"])

    summary = dry_run.summarize_dry_run_plans([plan])
    assert summary == {
        "schema": dry_run.DRY_RUN_PLAN_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_plan_count": 1,
        "dry_run_plan_created_count": 1,
        "dry_run_plan_valid_count": 1,
        "durable_executor_may_execute_count": 0,
        "live_command_count": 0,
        "forbidden_command_allowed_count": 0,
    }

    default_manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    default_summary = job_contract.summarize_manifests(default_manifests)
    assert default_summary["durable_dry_run_plan_request_count"] == 1
    assert default_summary["durable_dry_run_plan_created_count"] == 1
    assert default_summary["durable_dry_run_plan_valid_count"] == 1
    assert default_summary["durable_dry_run_executor_may_execute_count"] == 0
    assert default_summary["durable_dry_run_live_command_count"] == 0
    assert default_summary["durable_dry_run_forbidden_command_allowed_count"] == 0

    policy = manifest_executor.build_executor_policy(manifest, job_contract.DEFAULT_TEMP_PACKAGE_PATH)
    gate = policy["durable_executor_gate"]
    assert gate["dry_run_plan_created"] is True
    assert gate["dry_run_plan_valid"] is True
    assert gate["dry_run_plan_executor_may_execute"] is False
    assert gate["dry_run_plan_live_command_count"] == 0
    assert gate["save_or_delete_commands_allowed"] is False

    print("BP authoring durable dry-run plan smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
