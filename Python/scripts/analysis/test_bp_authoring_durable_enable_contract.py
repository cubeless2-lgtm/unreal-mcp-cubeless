#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_enable_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_enable_contract as enable_contract  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def gate_map(contract: dict) -> dict[str, dict]:
    return {gate["id"]: gate for gate in contract["gates"]}


def build_contract(
    *,
    package_allowed: bool = True,
    decision_present: bool = True,
    decision_conflict: bool = False,
    rollback_ready: bool = True,
    ownership_marker_ready: bool = True,
) -> dict:
    decision = "overwrite_existing" if decision_present else "missing"
    return enable_contract.build_enable_contract(
        requested=True,
        target_package_path="/Game/Blueprints",
        target_asset_path="/Game/Blueprints/BP_EnableContract",
        package_path_allowed=package_allowed,
        overwrite_rename_decision_contract={
            "decision": decision,
            "decision_present": decision_present,
            "decision_conflict": decision_conflict,
            "overwrite_requested": decision_present,
            "rename_if_exists_requested": False,
        },
        rollback_policy_contract={
            "rollback_policy_ready": rollback_ready,
            "rollback_allowed": rollback_ready,
            "protects_preexisting_assets": True,
            "delete_existing_asset_allowed": False,
            "overwrite_existing_asset_allowed": False,
            "requires_executor_created_asset_marker": True,
            "allowed_delete_scope": "only executor-created assets with ownership marker",
        },
        ownership_marker_policy_ready=ownership_marker_ready,
    )


def assert_never_opens(contract: dict) -> None:
    assert contract["durable_executor_may_open"] is False
    assert contract["durable_authoring_allowed"] is False
    assert contract["save_true_allowed"] is False
    assert contract["save_asset_allowed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert "save_asset" in contract["forbidden_commands"]
    assert "delete_asset" in contract["forbidden_commands"]
    assert "rename_asset" in contract["forbidden_commands"]


def main() -> int:
    complete = build_contract()
    assert complete["schema"] == enable_contract.ENABLE_CONTRACT_SCHEMA
    assert complete["enable_contract_satisfied"] is True
    assert complete["failed_required_gate_ids"] == []
    assert_never_opens(complete)

    missing_gate_cases = [
        (enable_contract.TARGET_PACKAGE_ALLOWLIST_GATE, build_contract(package_allowed=False)),
        (enable_contract.OVERWRITE_RENAME_DECISION_GATE, build_contract(decision_present=False)),
        (enable_contract.OVERWRITE_RENAME_DECISION_GATE, build_contract(decision_conflict=True)),
        (enable_contract.ROLLBACK_READINESS_GATE, build_contract(rollback_ready=False)),
        (enable_contract.EXECUTOR_CREATED_OWNERSHIP_MARKER_GATE, build_contract(ownership_marker_ready=False)),
    ]
    for expected_gate_id, contract in missing_gate_cases:
        assert contract["enable_contract_satisfied"] is False
        assert expected_gate_id in contract["failed_required_gate_ids"]
        assert gate_map(contract)[expected_gate_id]["status"] == "failed"
        assert_never_opens(contract)

    summary = enable_contract.summarize_enable_contracts([complete, *[contract for _, contract in missing_gate_cases]])
    assert summary["schema"] == enable_contract.ENABLE_CONTRACT_SUMMARY_SCHEMA
    assert summary["status"] == "passed"
    assert summary["durable_requested_manifest_count"] == 6
    assert summary["enable_contract_satisfied_count"] == 1
    assert summary["durable_executor_may_open_count"] == 0
    assert summary["durable_authoring_allowed_count"] == 0
    assert summary["forbidden_command_allowed_count"] == 0

    manifest = job_contract.build_job_manifest(
        "durable_overwrite",
        "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints and overwrite if it exists with a Static Mesh Component.",
        temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    integrated = manifest["durable_enable_contract"]
    integrated_gates = gate_map(integrated)
    assert integrated["enable_contract_satisfied"] is False
    assert integrated["durable_executor_may_open"] is False
    assert integrated_gates[enable_contract.TARGET_PACKAGE_ALLOWLIST_GATE]["passed"] is True
    assert integrated_gates[enable_contract.OVERWRITE_RENAME_DECISION_GATE]["passed"] is True
    assert integrated_gates[enable_contract.ROLLBACK_READINESS_GATE]["passed"] is False
    assert integrated_gates[enable_contract.EXECUTOR_CREATED_OWNERSHIP_MARKER_GATE]["passed"] is True
    assert "rollback_readiness" in manifest["durable_executor_skeleton_contract"]["disabled_by"]
    assert "executor_created_ownership_marker" not in manifest["durable_executor_skeleton_contract"]["disabled_by"]
    assert manifest["durable_executor_skeleton_contract"]["command_plan"] == []
    assert manifest["durable_executor_skeleton_contract"]["allowed_live_command_count"] == 0

    policy = manifest_executor.build_executor_policy(manifest, job_contract.DEFAULT_TEMP_PACKAGE_PATH)
    gate = policy["durable_executor_gate"]
    assert policy["can_execute"] is False
    assert gate["durable_enable_contract_satisfied"] is False
    assert gate["durable_enable_executor_may_open"] is False
    assert gate["durable_authoring_allowed"] is False
    assert gate["save_allowed"] is False
    assert gate["save_or_delete_commands_allowed"] is False
    assert "durable_enable_contract_not_satisfied" in gate["blocked_by"]

    print("BP authoring durable enable contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
