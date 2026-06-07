#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_code_change_approval_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_change_design_contract as design  # noqa: E402
import bp_authoring_durable_executor_code_change_approval_contract as approval  # noqa: E402


def build_current_change_design_summary() -> dict:
    return {
        "schema": design.DURABLE_EXECUTOR_CHANGE_DESIGN_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_executor_change_design_count": 1,
        "change_design_contract_defined_count": 1,
        "implementation_plan_contract_ready_count": 1,
        "implementation_plan_inputs_satisfied_count": 0,
        "implementation_plan_record_valid_count": 0,
        "allowed_implementation_plan_observed_count": 0,
        "no_forbidden_implementation_plan_claims_count": 0,
        "change_design_inputs_satisfied_count": 0,
        "change_design_record_present_count": 0,
        "record_schema_matches_count": 0,
        "change_design_scope_matches_count": 0,
        "explicit_change_design_authorized_count": 0,
        "design_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_change_design_observed_count": 0,
        "no_forbidden_change_design_claims_count": 0,
        "change_design_record_valid_count": 0,
        "change_design_record_rejected_count": 0,
        "unsafe_change_design_record_count": 0,
        "missing_change_design_prerequisite_count": 14,
        "reported_allowed_change_design_count": 0,
        "reported_forbidden_change_design_count": 0,
        "durable_executor_change_design_started_count": 0,
        "durable_executor_change_design_accepted_count": 0,
        "durable_executor_code_change_approval_started_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }


def build_approval_record(**overrides: object) -> dict:
    record = {
        "schema": approval.DURABLE_EXECUTOR_CODE_CHANGE_APPROVAL_RECORD_SCHEMA,
        "code_change_approval_scope": approval.EXPECTED_CODE_CHANGE_APPROVAL_SCOPE,
        "explicit_durable_executor_code_change_approval_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
        "durable_executor_code_change_approval_started": False,
        "durable_executor_code_change_approval_accepted": False,
        "durable_executor_code_patch_plan_started": False,
        "code_change_performed": False,
        "executor_code_modified": False,
        "unreal_asset_modified": False,
        "live_bridge_probe_started": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "save_asset_executed": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
        "live_command_dispatched": False,
        "live_command_executed": False,
        "reported_code_change_approval_review_count": 1,
        "reported_no_code_change_approval_count": 1,
        "reported_no_asset_change_approval_count": 1,
        "reported_no_live_probe_approval_count": 1,
        "reported_patch_plan_started_count": 0,
        "reported_code_change_count": 0,
        "reported_unreal_asset_change_count": 0,
        "reported_live_probe_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_asset_write_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_change_design_summary()
    contract = approval.build_durable_executor_code_change_approval_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == approval.DURABLE_EXECUTOR_CODE_CHANGE_APPROVAL_SCHEMA
    assert contract["requested"] is True
    assert contract["code_change_approval_contract_defined"] is True
    assert contract["change_design_contract_ready"] is True
    assert contract["change_design_inputs_satisfied"] is False
    assert contract["change_design_record_valid"] is False
    assert contract["allowed_change_design_observed"] is False
    assert contract["no_forbidden_change_design_claims"] is False
    assert contract["code_change_approval_inputs_satisfied"] is False
    assert contract["code_change_approval_record_present"] is False
    assert contract["code_change_approval_record_valid"] is False
    assert contract["code_change_approval_record_rejected"] is False
    assert contract["unsafe_code_change_approval_record_count"] == 0
    assert contract["missing_code_change_approval_prerequisite_count"] == 14
    assert "section_97_change_design_inputs_satisfied" in contract[
        "missing_code_change_approval_prerequisites"
    ]
    assert "section_97_change_design_record_valid" in contract[
        "missing_code_change_approval_prerequisites"
    ]
    assert "section_97_allowed_change_design_observed" in contract[
        "missing_code_change_approval_prerequisites"
    ]
    assert "section_97_no_forbidden_change_design_claims" in contract[
        "missing_code_change_approval_prerequisites"
    ]
    assert "durable_executor_code_change_approval_record_present" in contract[
        "missing_code_change_approval_prerequisites"
    ]
    assert "explicit_durable_mvp_request_reconfirmed" in contract[
        "missing_code_change_approval_prerequisites"
    ]
    assert "separate_durable_executor_code_patch_plan_contract" in contract[
        "missing_code_change_approval_prerequisites"
    ]
    assert contract["durable_executor_code_change_approval_started"] is False
    assert contract["durable_executor_code_patch_plan_started"] is False
    assert contract["code_change_performed"] is False
    assert contract["unreal_asset_modified"] is False
    assert contract["live_bridge_probe_started"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = approval.summarize_durable_executor_code_change_approvals([contract])
    assert summary["status"] == "passed"
    assert summary["durable_requested_executor_code_change_approval_count"] == 1
    assert summary["code_change_approval_contract_defined_count"] == 1
    assert summary["change_design_contract_ready_count"] == 1
    assert summary["code_change_approval_record_valid_count"] == 0
    assert summary["code_change_approval_record_rejected_count"] == 0
    assert summary["unsafe_code_change_approval_record_count"] == 0
    assert summary["missing_code_change_approval_prerequisite_count"] == 14
    assert summary["durable_executor_code_change_approval_started_count"] == 0
    assert summary["durable_executor_code_patch_plan_started_count"] == 0
    assert summary["code_change_performed_count"] == 0
    assert summary["unreal_asset_modified_count"] == 0
    assert summary["live_bridge_probe_started_count"] == 0
    assert summary["durable_authoring_enabled_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    future_summary = {
        **current_summary,
        "change_design_inputs_satisfied_count": 1,
        "change_design_record_valid_count": 1,
        "allowed_change_design_observed_count": 1,
        "no_forbidden_change_design_claims_count": 1,
    }
    future_contract = approval.build_durable_executor_code_change_approval_contract(
        True,
        future_summary,
        build_approval_record(),
    )
    assert future_contract["code_change_approval_record_valid"] is True
    assert future_contract["missing_code_change_approval_prerequisite_count"] == 1
    assert future_contract["missing_code_change_approval_prerequisites"] == [
        "separate_durable_executor_code_patch_plan_contract"
    ]
    assert future_contract["reported_allowed_code_change_approval_count"] == 4
    assert future_contract["reported_forbidden_code_change_approval_count"] == 0
    assert future_contract["durable_executor_code_change_approval_started"] is False
    assert future_contract["durable_executor_code_patch_plan_started"] is False
    assert future_contract["code_change_performed"] is False
    assert future_contract["unreal_asset_modified"] is False
    assert future_contract["durable_authoring_enabled"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    unsafe_contract = approval.build_durable_executor_code_change_approval_contract(
        True,
        future_summary,
        build_approval_record(code_change_performed=True),
    )
    assert unsafe_contract["code_change_approval_record_valid"] is False
    assert unsafe_contract["code_change_approval_record_rejected"] is True
    assert unsafe_contract["unsafe_code_change_approval_record_count"] == 1
    unsafe_summary = approval.summarize_durable_executor_code_change_approvals(
        [unsafe_contract]
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["code_change_approval_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_code_change_approval_record_count"] == 1
    assert unsafe_summary["code_change_performed_count"] == 0

    print("BP authoring durable executor code-change approval contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
