#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_activation_readiness_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_activation_readiness_contract as readiness  # noqa: E402
import bp_authoring_durable_executor_release_promotion_barrier_contract as barrier  # noqa: E402


def build_current_release_promotion_barrier_summary() -> dict:
    return {
        "schema": barrier.DURABLE_EXECUTOR_RELEASE_PROMOTION_BARRIER_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_executor_release_promotion_barrier_count": 1,
        "release_promotion_barrier_contract_defined_count": 1,
        "code_patch_release_decision_contract_ready_count": 1,
        "code_patch_release_decision_inputs_satisfied_count": 0,
        "code_patch_release_decision_record_valid_count": 0,
        "allowed_code_patch_release_decision_observed_count": 0,
        "no_forbidden_code_patch_release_decision_claims_count": 0,
        "release_promotion_barrier_inputs_satisfied_count": 0,
        "release_promotion_barrier_record_present_count": 0,
        "record_schema_matches_count": 0,
        "release_promotion_barrier_scope_matches_count": 0,
        "explicit_release_promotion_barrier_authorized_count": 0,
        "promotion_barrier_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_release_promotion_barrier_observed_count": 0,
        "no_forbidden_release_promotion_barrier_claims_count": 0,
        "release_promotion_barrier_record_valid_count": 0,
        "release_promotion_barrier_record_rejected_count": 0,
        "unsafe_release_promotion_barrier_record_count": 0,
        "missing_release_promotion_barrier_prerequisite_count": 14,
        "reported_allowed_release_promotion_barrier_count": 0,
        "reported_forbidden_release_promotion_barrier_count": 0,
        "durable_executor_release_promotion_barrier_started_count": 0,
        "durable_executor_release_promotion_barrier_accepted_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
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


def build_activation_readiness_record(**overrides: object) -> dict:
    record = {
        "schema": readiness.DURABLE_EXECUTOR_ACTIVATION_READINESS_RECORD_SCHEMA,
        "activation_readiness_scope": readiness.EXPECTED_ACTIVATION_READINESS_SCOPE,
        "explicit_durable_executor_activation_readiness_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
        "durable_executor_activation_readiness_started": False,
        "durable_executor_activation_readiness_accepted": False,
        "durable_executor_open_contract_started": False,
        "durable_executor_activated": False,
        "durable_executor_opened": False,
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
        "reported_activation_readiness_gate_count": 1,
        "reported_promotion_barrier_revalidated_count": 1,
        "reported_target_allowlist_revalidated_count": 1,
        "reported_rollback_readiness_revalidated_count": 1,
        "reported_ownership_marker_revalidated_count": 1,
        "reported_durable_authoring_still_disabled_count": 1,
        "reported_no_code_change_activation_readiness_count": 1,
        "reported_no_asset_change_activation_readiness_count": 1,
        "reported_no_live_probe_activation_readiness_count": 1,
        "reported_code_patch_applied_count": 0,
        "reported_code_patch_execution_count": 0,
        "reported_code_patch_result_admission_count": 0,
        "reported_code_patch_result_readback_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_release_review_count": 0,
        "reported_release_decision_count": 0,
        "reported_promotion_barrier_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
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
    current_summary = build_current_release_promotion_barrier_summary()
    contract = readiness.build_durable_executor_activation_readiness_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == readiness.DURABLE_EXECUTOR_ACTIVATION_READINESS_SCHEMA
    assert contract["requested"] is True
    assert contract["activation_readiness_contract_defined"] is True
    assert contract["release_promotion_barrier_contract_ready"] is True
    assert contract["release_promotion_barrier_inputs_satisfied"] is False
    assert contract["release_promotion_barrier_record_valid"] is False
    assert contract["allowed_release_promotion_barrier_observed"] is False
    assert contract["no_forbidden_release_promotion_barrier_claims"] is False
    assert contract["activation_readiness_inputs_satisfied"] is False
    assert contract["activation_readiness_record_present"] is False
    assert contract["activation_readiness_record_valid"] is False
    assert contract["activation_readiness_record_rejected"] is False
    assert contract["unsafe_activation_readiness_record_count"] == 0
    assert contract["missing_activation_readiness_prerequisite_count"] == 14
    assert "section_109_release_promotion_barrier_inputs_satisfied" in contract[
        "missing_activation_readiness_prerequisites"
    ]
    assert "section_109_release_promotion_barrier_record_valid" in contract[
        "missing_activation_readiness_prerequisites"
    ]
    assert "section_109_allowed_release_promotion_barrier_observed" in contract[
        "missing_activation_readiness_prerequisites"
    ]
    assert "section_109_no_forbidden_release_promotion_barrier_claims" in contract[
        "missing_activation_readiness_prerequisites"
    ]
    assert "durable_executor_activation_readiness_record_present" in contract[
        "missing_activation_readiness_prerequisites"
    ]
    assert "explicit_durable_mvp_request_reconfirmed" in contract[
        "missing_activation_readiness_prerequisites"
    ]
    assert "separate_durable_executor_open_contract" in contract[
        "missing_activation_readiness_prerequisites"
    ]
    assert contract["durable_executor_activation_readiness_started"] is False
    assert contract["durable_executor_activation_readiness_accepted"] is False
    assert contract["durable_executor_open_contract_started"] is False
    assert contract["durable_executor_activated"] is False
    assert contract["durable_executor_opened"] is False
    assert contract["code_change_performed"] is False
    assert contract["executor_code_modified"] is False
    assert contract["unreal_asset_modified"] is False
    assert contract["live_bridge_probe_started"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = readiness.summarize_durable_executor_activation_readiness([contract])
    assert summary["status"] == "passed"
    assert summary["durable_requested_executor_activation_readiness_count"] == 1
    assert summary["activation_readiness_contract_defined_count"] == 1
    assert summary["release_promotion_barrier_contract_ready_count"] == 1
    assert summary["activation_readiness_record_valid_count"] == 0
    assert summary["activation_readiness_record_rejected_count"] == 0
    assert summary["unsafe_activation_readiness_record_count"] == 0
    assert summary["missing_activation_readiness_prerequisite_count"] == 14
    assert summary["durable_executor_activation_readiness_started_count"] == 0
    assert summary["durable_executor_activation_readiness_accepted_count"] == 0
    assert summary["durable_executor_open_contract_started_count"] == 0
    assert summary["durable_executor_activated_count"] == 0
    assert summary["durable_executor_opened_count"] == 0
    assert summary["code_change_performed_count"] == 0
    assert summary["executor_code_modified_count"] == 0
    assert summary["unreal_asset_modified_count"] == 0
    assert summary["live_bridge_probe_started_count"] == 0
    assert summary["durable_authoring_enabled_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    future_summary = {
        **current_summary,
        "release_promotion_barrier_inputs_satisfied_count": 1,
        "release_promotion_barrier_record_valid_count": 1,
        "allowed_release_promotion_barrier_observed_count": 1,
        "no_forbidden_release_promotion_barrier_claims_count": 1,
    }
    future_contract = readiness.build_durable_executor_activation_readiness_contract(
        True,
        future_summary,
        build_activation_readiness_record(),
    )
    assert future_contract["activation_readiness_record_valid"] is True
    assert future_contract["missing_activation_readiness_prerequisite_count"] == 1
    assert future_contract["missing_activation_readiness_prerequisites"] == [
        "separate_durable_executor_open_contract"
    ]
    assert future_contract["reported_allowed_activation_readiness_count"] == 9
    assert future_contract["reported_forbidden_activation_readiness_count"] == 0
    assert future_contract["durable_executor_activation_readiness_started"] is False
    assert future_contract["durable_executor_activation_readiness_accepted"] is False
    assert future_contract["durable_executor_open_contract_started"] is False
    assert future_contract["durable_executor_activated"] is False
    assert future_contract["durable_executor_opened"] is False
    assert future_contract["code_change_performed"] is False
    assert future_contract["executor_code_modified"] is False
    assert future_contract["unreal_asset_modified"] is False
    assert future_contract["durable_authoring_enabled"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    unsafe_contract = readiness.build_durable_executor_activation_readiness_contract(
        True,
        future_summary,
        build_activation_readiness_record(durable_executor_opened=True),
    )
    assert unsafe_contract["activation_readiness_record_valid"] is False
    assert unsafe_contract["activation_readiness_record_rejected"] is True
    assert unsafe_contract["unsafe_activation_readiness_record_count"] == 1
    unsafe_summary = readiness.summarize_durable_executor_activation_readiness(
        [unsafe_contract]
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["activation_readiness_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_activation_readiness_record_count"] == 1
    assert unsafe_summary["durable_executor_opened_count"] == 0
    assert unsafe_summary["durable_executor_activation_readiness_started_count"] == 0

    forbidden_contract = readiness.build_durable_executor_activation_readiness_contract(
        True,
        future_summary,
        build_activation_readiness_record(reported_executor_open_count=1),
    )
    assert forbidden_contract["activation_readiness_record_valid"] is False
    assert forbidden_contract["activation_readiness_record_rejected"] is True
    assert forbidden_contract["reported_forbidden_activation_readiness_count"] == 1
    assert forbidden_contract["unsafe_activation_readiness_record_count"] == 1

    print("BP authoring durable executor activation readiness contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
