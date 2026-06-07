#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_save_simulator.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_save_simulator as save_sim  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def main() -> int:
    manifest = job_contract.build_job_manifest(
        "durable_overwrite",
        "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints and overwrite if it exists with a Static Mesh Component.",
        temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    simulation = manifest["durable_save_validation_simulation_contract"]
    assert simulation["schema"] == save_sim.SAVE_SIMULATION_SCHEMA
    assert simulation["requested"] is True
    assert simulation["simulation_evaluated"] is True
    assert simulation["simulation_status"] == "blocked"
    assert simulation["future_save_conditions_satisfied"] is False
    assert simulation["save_true_allowed"] is False
    assert simulation["save_asset_allowed"] is False
    assert simulation["compile_save_command_allowed"] is False
    assert simulation["live_command_count"] == 0
    assert "read_only_asset_exists_result_available" in simulation["failed_check_ids"]
    assert "rollback_policy_ready" in simulation["failed_check_ids"]
    assert "enable_contract_satisfied" in simulation["failed_check_ids"]
    assert "compile_save_validation_enabled" in simulation["failed_check_ids"]
    assert "explicit_durable_executor_enable_flag" in simulation["failed_check_ids"]

    checks = {check["id"]: check for check in simulation["checks"]}
    assert checks["target_package_allowlisted"]["passed"] is True
    assert checks["ownership_marker_policy_ready"]["passed"] is True
    assert checks["dry_run_plan_valid"]["passed"] is True
    assert checks["rollback_policy_ready"]["passed"] is False

    summary = save_sim.summarize_save_simulations([simulation])
    assert summary == {
        "schema": save_sim.SAVE_SIMULATION_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_simulation_count": 1,
        "simulation_evaluated_count": 1,
        "future_save_conditions_satisfied_count": 0,
        "save_true_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "compile_save_command_allowed_count": 0,
        "live_command_count": 0,
        "forbidden_command_allowed_count": 0,
    }

    default_manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    default_summary = job_contract.summarize_manifests(default_manifests)
    assert default_summary["durable_save_simulation_request_count"] == 1
    assert default_summary["durable_save_simulation_evaluated_count"] == 1
    assert default_summary["durable_save_simulation_conditions_satisfied_count"] == 0
    assert default_summary["durable_save_simulation_save_true_allowed_count"] == 0
    assert default_summary["durable_save_simulation_save_asset_allowed_count"] == 0
    assert default_summary["durable_save_simulation_live_command_count"] == 0

    policy = manifest_executor.build_executor_policy(manifest, job_contract.DEFAULT_TEMP_PACKAGE_PATH)
    gate = policy["durable_executor_gate"]
    assert gate["save_simulation_evaluated"] is True
    assert gate["save_simulation_conditions_satisfied"] is False
    assert gate["save_simulation_save_true_allowed"] is False
    assert gate["save_simulation_save_asset_allowed"] is False
    assert gate["save_simulation_live_command_count"] == 0
    assert gate["save_or_delete_commands_allowed"] is False

    print("BP authoring durable save simulator smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
