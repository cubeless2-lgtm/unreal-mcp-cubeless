#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_approval_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_approval_contract as approval  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def main() -> int:
    manifest = job_contract.build_job_manifest(
        "durable_overwrite",
        "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints and overwrite if it exists with a Static Mesh Component.",
        temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    canary_prep = manifest["durable_canary_prep_contract"]
    contract = manifest["durable_canary_approval_gate_contract"]
    assert contract["schema"] == approval.CANARY_APPROVAL_GATE_SCHEMA
    assert contract["requested"] is True
    assert contract["canary_prep_ready"] is True
    assert contract["approval_record_required"] is True
    assert contract["approval_record_present"] is True
    assert contract["approval_record_schema_ok"] is True
    assert contract["approval_scope_matches"] is True
    assert contract["approval_operation_matches"] is True
    assert contract["approval_scoped_to_canary_package"] is True
    assert contract["canary_approval_gate_passed"] is True
    assert contract["canary_executor_may_open"] is False
    assert contract["canary_live_execution_allowed"] is False
    assert contract["general_blueprints_package_allowed"] is False
    assert contract["save_true_allowed"] is False
    assert contract["save_asset_allowed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["live_command_count"] == 0
    assert "section_56_approval_gate_does_not_enable_live_canary" in contract["blocked_by"]
    record = contract["approval_record"]
    assert record["schema"] == approval.CANARY_APPROVAL_RECORD_SCHEMA
    assert record["approved_operation"] == approval.APPROVED_OPERATION
    assert record["approval_scope_id"] == approval.APPROVAL_SCOPE_ID
    assert record["canary_package_path"] == "/Game/_MCP_Temp/DurableCanary"
    assert record["canary_asset_path"] == "/Game/_MCP_Temp/DurableCanary/BP_PlannerDurable_Canary"
    assert record["approval_does_not_authorize_live_execution"] is True
    assert record["approval_does_not_authorize_save_or_delete"] is True

    missing_approval = approval.build_canary_approval_gate_contract(
        requested=True,
        canary_prep_contract=canary_prep,
        approval_record=None,
    )
    assert missing_approval["canary_approval_gate_passed"] is False
    assert missing_approval["canary_live_execution_allowed"] is False
    assert "canary_approval_record_missing" in missing_approval["blocked_by"]

    bad_scope_record = approval.build_scoped_canary_approval_record(canary_prep)
    bad_scope_record["canary_asset_path"] = "/Game/Blueprints/BP_PlannerDurable"
    bad_scope = approval.build_canary_approval_gate_contract(
        requested=True,
        canary_prep_contract=canary_prep,
        approval_record=bad_scope_record,
    )
    assert bad_scope["canary_approval_gate_passed"] is False
    assert bad_scope["canary_live_execution_allowed"] is False
    assert "canary_approval_asset_mismatch" in bad_scope["blocked_by"]

    summary = approval.summarize_canary_approval_gate_contracts([contract])
    assert summary == {
        "schema": approval.CANARY_APPROVAL_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_approval_count": 1,
        "approval_record_present_count": 1,
        "canary_approval_gate_passed_count": 1,
        "approval_scoped_to_canary_package_count": 1,
        "canary_executor_may_open_count": 0,
        "canary_live_execution_allowed_count": 0,
        "general_blueprints_package_allowed_count": 0,
        "save_true_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "live_command_count": 0,
    }

    default_manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    default_summary = job_contract.summarize_manifests(default_manifests)
    assert default_summary["durable_canary_approval_request_count"] == 1
    assert default_summary["durable_canary_approval_record_present_count"] == 1
    assert default_summary["durable_canary_approval_gate_passed_count"] == 1
    assert default_summary["durable_canary_approval_scoped_to_canary_package_count"] == 1
    assert default_summary["durable_canary_executor_may_open_count"] == 0
    assert default_summary["durable_canary_approval_live_execution_allowed_count"] == 0
    assert default_summary["durable_canary_approval_general_blueprints_package_allowed_count"] == 0
    assert default_summary["durable_canary_approval_save_true_allowed_count"] == 0
    assert default_summary["durable_canary_approval_save_asset_allowed_count"] == 0
    assert default_summary["durable_canary_approval_delete_asset_allowed_count"] == 0
    assert default_summary["durable_canary_approval_live_command_count"] == 0

    policy = manifest_executor.build_executor_policy(manifest, job_contract.DEFAULT_TEMP_PACKAGE_PATH)
    gate = policy["durable_executor_gate"]
    assert gate["canary_approval_record_present"] is True
    assert gate["canary_approval_gate_passed"] is True
    assert gate["canary_approval_scoped_to_canary_package"] is True
    assert gate["canary_approval_executor_may_open"] is False
    assert gate["canary_approval_live_execution_allowed"] is False
    assert gate["canary_approval_general_blueprints_package_allowed"] is False
    assert gate["canary_approval_save_true_allowed"] is False
    assert gate["canary_approval_save_asset_allowed"] is False
    assert gate["canary_approval_delete_asset_allowed"] is False
    assert gate["canary_approval_live_command_count"] == 0
    assert gate["save_or_delete_commands_allowed"] is False

    print("BP authoring durable canary approval contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
