#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_ownership_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_ownership_contract as ownership  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402


TARGET = "/Game/Blueprints/BP_PlannerDurable"


def main() -> int:
    contract = ownership.build_ownership_marker_contract(True, TARGET)
    assert contract["schema"] == ownership.OWNERSHIP_MARKER_SCHEMA
    assert contract["ownership_marker_policy_ready"] is True
    assert contract["delete_without_marker_allowed"] is False
    assert contract["delete_preexisting_asset_allowed"] is False
    assert contract["overwrite_preexisting_asset_allowed"] is False
    assert contract["rename_preexisting_asset_allowed"] is False
    assert "target_asset_path" in contract["required_marker_fields"]
    assert "preflight_asset_existed_before_authoring" in contract["required_marker_fields"]

    missing_marker = ownership.evaluate_rollback_delete_authorization(
        contract,
        TARGET,
        None,
        preflight_asset_existed_before_authoring=False,
    )
    assert missing_marker["authorized"] is False
    assert missing_marker["delete_allowed_now"] is False
    assert "ownership_marker_missing_required_fields" in missing_marker["blocked_by"]

    valid_marker = ownership.build_valid_marker_record(TARGET)
    valid_authorization = ownership.evaluate_rollback_delete_authorization(
        contract,
        TARGET,
        valid_marker,
        preflight_asset_existed_before_authoring=False,
    )
    assert valid_authorization["authorized"] is True
    assert valid_authorization["delete_allowed_now"] is False
    assert valid_authorization["durable_side_effects_allowed"] is False

    target_mismatch = dict(valid_marker)
    target_mismatch["target_asset_path"] = "/Game/Blueprints/BP_Other"
    mismatch_authorization = ownership.evaluate_rollback_delete_authorization(
        contract,
        TARGET,
        target_mismatch,
        preflight_asset_existed_before_authoring=False,
    )
    assert mismatch_authorization["authorized"] is False
    assert "marker_target_asset_path_mismatch" in mismatch_authorization["blocked_by"]

    preexisting_asset = ownership.evaluate_rollback_delete_authorization(
        contract,
        TARGET,
        valid_marker,
        preflight_asset_existed_before_authoring=True,
    )
    assert preexisting_asset["authorized"] is False
    assert "preexisting_asset_delete_forbidden" in preexisting_asset["blocked_by"]

    manifest = job_contract.build_job_manifest(
        "durable_overwrite",
        "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints and overwrite if it exists with a Static Mesh Component.",
        temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    manifest_contract = manifest["durable_ownership_marker_contract"]
    assert manifest_contract["ownership_marker_policy_ready"] is True
    assert manifest_contract["delete_without_marker_allowed"] is False
    assert manifest_contract["delete_preexisting_asset_allowed"] is False
    assert manifest["durable_rollback_policy_contract"]["ownership_marker_policy_ready"] is True
    assert manifest["durable_rollback_policy_contract"]["rollback_policy_ready"] is False
    assert manifest["durable_enable_contract"]["failed_required_gate_ids"] == ["rollback_readiness"]
    assert manifest["durable_enable_contract"]["durable_executor_may_open"] is False

    print("BP authoring durable ownership contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
