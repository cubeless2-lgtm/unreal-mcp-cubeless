#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_open_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_activation_readiness_contract as readiness  # noqa: E402
import bp_authoring_durable_executor_open_contract as executor_open  # noqa: E402


def build_current_activation_readiness_summary() -> dict:
    return {
        "schema": readiness.DURABLE_EXECUTOR_ACTIVATION_READINESS_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_executor_activation_readiness_count": 1,
        "activation_readiness_contract_defined_count": 1,
        "release_promotion_barrier_contract_ready_count": 1,
        "release_promotion_barrier_inputs_satisfied_count": 0,
        "release_promotion_barrier_record_valid_count": 0,
        "allowed_release_promotion_barrier_observed_count": 0,
        "no_forbidden_release_promotion_barrier_claims_count": 0,
        "activation_readiness_inputs_satisfied_count": 0,
        "activation_readiness_record_present_count": 0,
        "record_schema_matches_count": 0,
        "activation_readiness_scope_matches_count": 0,
        "explicit_activation_readiness_authorized_count": 0,
        "activation_readiness_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_activation_readiness_observed_count": 0,
        "no_forbidden_activation_readiness_claims_count": 0,
        "activation_readiness_record_valid_count": 0,
        "activation_readiness_record_rejected_count": 0,
        "unsafe_activation_readiness_record_count": 0,
        "missing_activation_readiness_prerequisite_count": 14,
        "reported_allowed_activation_readiness_count": 0,
        "reported_forbidden_activation_readiness_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_executor_open_contract_started_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
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


def build_open_record(**overrides: object) -> dict:
    record = {
        "schema": executor_open.DURABLE_EXECUTOR_OPEN_RECORD_SCHEMA,
        "open_scope": executor_open.EXPECTED_OPEN_SCOPE,
        "explicit_durable_executor_open_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
        "durable_executor_open_contract_started": False,
        "durable_executor_open_contract_accepted": False,
        "durable_executor_open_performed": False,
        "durable_executor_activated": False,
        "durable_executor_opened": False,
        "durable_authoring_enable_started": False,
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
        "reported_executor_open_gate_count": 1,
        "reported_activation_readiness_revalidated_count": 1,
        "reported_target_allowlist_revalidated_count": 1,
        "reported_rollback_readiness_revalidated_count": 1,
        "reported_ownership_marker_revalidated_count": 1,
        "reported_durable_authoring_still_disabled_count": 1,
        "reported_no_code_change_open_count": 1,
        "reported_no_asset_change_open_count": 1,
        "reported_no_live_probe_open_count": 1,
        "reported_code_patch_applied_count": 0,
        "reported_code_patch_execution_count": 0,
        "reported_code_patch_result_admission_count": 0,
        "reported_code_patch_result_readback_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_release_review_count": 0,
        "reported_release_decision_count": 0,
        "reported_promotion_barrier_count": 0,
        "reported_activation_readiness_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_durable_authoring_enable_count": 0,
        "reported_code_change_count": 0,
        "reported_executor_code_modified_count": 0,
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
    current_summary = build_current_activation_readiness_summary()
    contract = executor_open.build_durable_executor_open_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == executor_open.DURABLE_EXECUTOR_OPEN_SCHEMA
    assert contract["requested"] is True
    assert contract["open_contract_defined"] is True
    assert contract["activation_readiness_contract_ready"] is True
    assert contract["activation_readiness_inputs_satisfied"] is False
    assert contract["activation_readiness_record_valid"] is False
    assert contract["allowed_activation_readiness_observed"] is False
    assert contract["no_forbidden_activation_readiness_claims"] is False
    assert contract["open_inputs_satisfied"] is False
    assert contract["open_record_present"] is False
    assert contract["open_record_valid"] is False
    assert contract["open_record_rejected"] is False
    assert contract["unsafe_open_record_count"] == 0
    assert contract["missing_open_prerequisite_count"] == 14
    assert "section_110_activation_readiness_inputs_satisfied" in contract[
        "missing_open_prerequisites"
    ]
    assert "section_110_activation_readiness_record_valid" in contract[
        "missing_open_prerequisites"
    ]
    assert "section_110_allowed_activation_readiness_observed" in contract[
        "missing_open_prerequisites"
    ]
    assert "section_110_no_forbidden_activation_readiness_claims" in contract[
        "missing_open_prerequisites"
    ]
    assert "durable_executor_open_record_present" in contract[
        "missing_open_prerequisites"
    ]
    assert "explicit_durable_mvp_request_reconfirmed" in contract[
        "missing_open_prerequisites"
    ]
    assert "separate_durable_authoring_enable_contract" in contract[
        "missing_open_prerequisites"
    ]
    assert contract["durable_executor_open_contract_started"] is False
    assert contract["durable_executor_open_contract_accepted"] is False
    assert contract["durable_executor_open_performed"] is False
    assert contract["durable_executor_activated"] is False
    assert contract["durable_executor_opened"] is False
    assert contract["durable_authoring_enable_started"] is False
    assert contract["code_change_performed"] is False
    assert contract["executor_code_modified"] is False
    assert contract["unreal_asset_modified"] is False
    assert contract["live_bridge_probe_started"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = executor_open.summarize_durable_executor_opens([contract])
    assert summary["status"] == "passed"
    assert summary["durable_requested_executor_open_count"] == 1
    assert summary["open_contract_defined_count"] == 1
    assert summary["activation_readiness_contract_ready_count"] == 1
    assert summary["open_record_valid_count"] == 0
    assert summary["open_record_rejected_count"] == 0
    assert summary["unsafe_open_record_count"] == 0
    assert summary["missing_open_prerequisite_count"] == 14
    assert summary["durable_executor_open_contract_started_count"] == 0
    assert summary["durable_executor_open_contract_accepted_count"] == 0
    assert summary["durable_executor_open_performed_count"] == 0
    assert summary["durable_executor_activated_count"] == 0
    assert summary["durable_executor_opened_count"] == 0
    assert summary["durable_authoring_enable_started_count"] == 0
    assert summary["code_change_performed_count"] == 0
    assert summary["executor_code_modified_count"] == 0
    assert summary["unreal_asset_modified_count"] == 0
    assert summary["live_bridge_probe_started_count"] == 0
    assert summary["durable_authoring_enabled_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    future_summary = {
        **current_summary,
        "activation_readiness_inputs_satisfied_count": 1,
        "activation_readiness_record_valid_count": 1,
        "allowed_activation_readiness_observed_count": 1,
        "no_forbidden_activation_readiness_claims_count": 1,
    }
    future_contract = executor_open.build_durable_executor_open_contract(
        True,
        future_summary,
        build_open_record(),
    )
    assert future_contract["open_record_valid"] is True
    assert future_contract["missing_open_prerequisite_count"] == 1
    assert future_contract["missing_open_prerequisites"] == [
        "separate_durable_authoring_enable_contract"
    ]
    assert future_contract["reported_allowed_open_count"] == 9
    assert future_contract["reported_forbidden_open_count"] == 0
    assert future_contract["durable_executor_open_contract_started"] is False
    assert future_contract["durable_executor_open_contract_accepted"] is False
    assert future_contract["durable_executor_open_performed"] is False
    assert future_contract["durable_executor_activated"] is False
    assert future_contract["durable_executor_opened"] is False
    assert future_contract["durable_authoring_enable_started"] is False
    assert future_contract["code_change_performed"] is False
    assert future_contract["executor_code_modified"] is False
    assert future_contract["unreal_asset_modified"] is False
    assert future_contract["durable_authoring_enabled"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    unsafe_contract = executor_open.build_durable_executor_open_contract(
        True,
        future_summary,
        build_open_record(durable_executor_opened=True),
    )
    assert unsafe_contract["open_record_valid"] is False
    assert unsafe_contract["open_record_rejected"] is True
    assert unsafe_contract["unsafe_open_record_count"] == 1
    unsafe_summary = executor_open.summarize_durable_executor_opens([unsafe_contract])
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["open_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_open_record_count"] == 1
    assert unsafe_summary["durable_executor_opened_count"] == 0
    assert unsafe_summary["durable_executor_open_contract_started_count"] == 0

    forbidden_contract = executor_open.build_durable_executor_open_contract(
        True,
        future_summary,
        build_open_record(reported_durable_authoring_enable_count=1),
    )
    assert forbidden_contract["open_record_valid"] is False
    assert forbidden_contract["open_record_rejected"] is True
    assert forbidden_contract["reported_forbidden_open_count"] == 1
    assert forbidden_contract["unsafe_open_record_count"] == 1

    print("BP authoring durable executor open contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
