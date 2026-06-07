#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_code_patch_final_release_readiness_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_code_patch_final_no_save_release_contract as final_release  # noqa: E402
import bp_authoring_durable_executor_code_patch_final_release_readiness_contract as readiness  # noqa: E402


def build_current_code_patch_final_no_save_release_summary() -> dict:
    return {
        "schema": (
            final_release.DURABLE_EXECUTOR_CODE_PATCH_FINAL_NO_SAVE_RELEASE_SUMMARY_SCHEMA
        ),
        "status": "passed",
        "durable_requested_executor_code_patch_final_no_save_release_count": 1,
        "code_patch_final_no_save_release_contract_defined_count": 1,
        "code_patch_result_readback_contract_ready_count": 1,
        "code_patch_result_readback_inputs_satisfied_count": 0,
        "code_patch_result_readback_record_valid_count": 0,
        "allowed_code_patch_result_readback_observed_count": 0,
        "no_forbidden_code_patch_result_readback_claims_count": 0,
        "code_patch_final_no_save_release_inputs_satisfied_count": 0,
        "code_patch_final_no_save_release_record_present_count": 0,
        "record_schema_matches_count": 0,
        "code_patch_final_no_save_release_scope_matches_count": 0,
        "explicit_code_patch_final_no_save_release_authorized_count": 0,
        "final_no_save_release_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_code_patch_final_no_save_release_observed_count": 0,
        "no_forbidden_code_patch_final_no_save_release_claims_count": 0,
        "code_patch_final_no_save_release_record_valid_count": 0,
        "code_patch_final_no_save_release_record_rejected_count": 0,
        "unsafe_code_patch_final_no_save_release_record_count": 0,
        "missing_code_patch_final_no_save_release_prerequisite_count": 14,
        "reported_allowed_code_patch_final_no_save_release_count": 0,
        "reported_forbidden_code_patch_final_no_save_release_count": 0,
        "durable_executor_code_patch_final_no_save_release_started_count": 0,
        "durable_executor_code_patch_final_no_save_release_accepted_count": 0,
        "durable_executor_code_patch_final_release_readiness_started_count": 0,
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


def build_readiness_record(**overrides: object) -> dict:
    record = {
        "schema": (
            readiness.DURABLE_EXECUTOR_CODE_PATCH_FINAL_RELEASE_READINESS_RECORD_SCHEMA
        ),
        "code_patch_final_release_readiness_scope": (
            readiness.EXPECTED_CODE_PATCH_FINAL_RELEASE_READINESS_SCOPE
        ),
        "explicit_durable_executor_code_patch_final_release_readiness_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
        "durable_executor_code_patch_final_release_readiness_started": False,
        "durable_executor_code_patch_final_release_ready": False,
        "durable_executor_code_patch_release_review_started": False,
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
        "reported_final_release_readiness_gate_count": 1,
        "reported_final_no_save_release_revalidated_count": 1,
        "reported_durable_authoring_still_disabled_count": 1,
        "reported_no_code_change_readiness_count": 1,
        "reported_no_asset_change_readiness_count": 1,
        "reported_no_live_probe_readiness_count": 1,
        "reported_code_patch_applied_count": 0,
        "reported_code_patch_execution_count": 0,
        "reported_code_patch_result_admission_count": 0,
        "reported_code_patch_result_readback_count": 0,
        "reported_final_no_save_release_count": 0,
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
    current_summary = build_current_code_patch_final_no_save_release_summary()
    contract = readiness.build_durable_executor_code_patch_final_release_readiness_contract(
        True,
        current_summary,
    )
    assert (
        contract["schema"]
        == readiness.DURABLE_EXECUTOR_CODE_PATCH_FINAL_RELEASE_READINESS_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["code_patch_final_release_readiness_contract_defined"] is True
    assert contract["code_patch_final_no_save_release_contract_ready"] is True
    assert contract["code_patch_final_no_save_release_inputs_satisfied"] is False
    assert contract["code_patch_final_no_save_release_record_valid"] is False
    assert contract["allowed_code_patch_final_no_save_release_observed"] is False
    assert contract["no_forbidden_code_patch_final_no_save_release_claims"] is False
    assert contract["code_patch_final_release_readiness_inputs_satisfied"] is False
    assert contract["code_patch_final_release_readiness_record_present"] is False
    assert contract["code_patch_final_release_readiness_record_valid"] is False
    assert contract["code_patch_final_release_readiness_record_rejected"] is False
    assert contract["unsafe_code_patch_final_release_readiness_record_count"] == 0
    assert contract["missing_code_patch_final_release_readiness_prerequisite_count"] == 14
    assert "section_105_code_patch_final_no_save_release_inputs_satisfied" in contract[
        "missing_code_patch_final_release_readiness_prerequisites"
    ]
    assert "section_105_code_patch_final_no_save_release_record_valid" in contract[
        "missing_code_patch_final_release_readiness_prerequisites"
    ]
    assert "section_105_allowed_code_patch_final_no_save_release_observed" in contract[
        "missing_code_patch_final_release_readiness_prerequisites"
    ]
    assert "section_105_no_forbidden_code_patch_final_no_save_release_claims" in contract[
        "missing_code_patch_final_release_readiness_prerequisites"
    ]
    assert (
        "durable_executor_code_patch_final_release_readiness_record_present"
        in contract["missing_code_patch_final_release_readiness_prerequisites"]
    )
    assert "explicit_durable_mvp_request_reconfirmed" in contract[
        "missing_code_patch_final_release_readiness_prerequisites"
    ]
    assert "separate_durable_executor_code_patch_release_review_contract" in contract[
        "missing_code_patch_final_release_readiness_prerequisites"
    ]
    assert contract["durable_executor_code_patch_final_release_readiness_started"] is False
    assert contract["durable_executor_code_patch_final_release_ready"] is False
    assert contract["durable_executor_code_patch_release_review_started"] is False
    assert contract["code_change_performed"] is False
    assert contract["executor_code_modified"] is False
    assert contract["unreal_asset_modified"] is False
    assert contract["live_bridge_probe_started"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = readiness.summarize_durable_executor_code_patch_final_release_readiness(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary["durable_requested_executor_code_patch_final_release_readiness_count"]
        == 1
    )
    assert summary["code_patch_final_release_readiness_contract_defined_count"] == 1
    assert summary["code_patch_final_no_save_release_contract_ready_count"] == 1
    assert summary["code_patch_final_release_readiness_record_valid_count"] == 0
    assert summary["code_patch_final_release_readiness_record_rejected_count"] == 0
    assert summary["unsafe_code_patch_final_release_readiness_record_count"] == 0
    assert summary["missing_code_patch_final_release_readiness_prerequisite_count"] == 14
    assert summary["durable_executor_code_patch_final_release_readiness_started_count"] == 0
    assert summary["durable_executor_code_patch_final_release_ready_count"] == 0
    assert summary["durable_executor_code_patch_release_review_started_count"] == 0
    assert summary["code_change_performed_count"] == 0
    assert summary["executor_code_modified_count"] == 0
    assert summary["unreal_asset_modified_count"] == 0
    assert summary["live_bridge_probe_started_count"] == 0
    assert summary["durable_authoring_enabled_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    future_summary = {
        **current_summary,
        "code_patch_final_no_save_release_inputs_satisfied_count": 1,
        "code_patch_final_no_save_release_record_valid_count": 1,
        "allowed_code_patch_final_no_save_release_observed_count": 1,
        "no_forbidden_code_patch_final_no_save_release_claims_count": 1,
    }
    future_contract = (
        readiness.build_durable_executor_code_patch_final_release_readiness_contract(
            True,
            future_summary,
            build_readiness_record(),
        )
    )
    assert future_contract["code_patch_final_release_readiness_record_valid"] is True
    assert (
        future_contract["missing_code_patch_final_release_readiness_prerequisite_count"]
        == 1
    )
    assert future_contract[
        "missing_code_patch_final_release_readiness_prerequisites"
    ] == ["separate_durable_executor_code_patch_release_review_contract"]
    assert future_contract["reported_allowed_code_patch_final_release_readiness_count"] == 6
    assert future_contract["reported_forbidden_code_patch_final_release_readiness_count"] == 0
    assert future_contract["durable_executor_code_patch_final_release_readiness_started"] is False
    assert future_contract["durable_executor_code_patch_final_release_ready"] is False
    assert future_contract["durable_executor_code_patch_release_review_started"] is False
    assert future_contract["code_change_performed"] is False
    assert future_contract["executor_code_modified"] is False
    assert future_contract["unreal_asset_modified"] is False
    assert future_contract["durable_authoring_enabled"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    unsafe_contract = (
        readiness.build_durable_executor_code_patch_final_release_readiness_contract(
            True,
            future_summary,
            build_readiness_record(code_change_performed=True),
        )
    )
    assert unsafe_contract["code_patch_final_release_readiness_record_valid"] is False
    assert unsafe_contract["code_patch_final_release_readiness_record_rejected"] is True
    assert unsafe_contract["unsafe_code_patch_final_release_readiness_record_count"] == 1
    unsafe_summary = (
        readiness.summarize_durable_executor_code_patch_final_release_readiness(
            [unsafe_contract]
        )
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["code_patch_final_release_readiness_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_code_patch_final_release_readiness_record_count"] == 1
    assert unsafe_summary["code_change_performed_count"] == 0
    assert unsafe_summary["durable_executor_code_patch_final_release_ready_count"] == 0
    assert (
        unsafe_summary["durable_executor_code_patch_release_review_started_count"] == 0
    )

    forbidden_contract = (
        readiness.build_durable_executor_code_patch_final_release_readiness_contract(
            True,
            future_summary,
            build_readiness_record(reported_code_patch_applied_count=1),
        )
    )
    assert forbidden_contract["code_patch_final_release_readiness_record_valid"] is False
    assert forbidden_contract["code_patch_final_release_readiness_record_rejected"] is True
    assert forbidden_contract[
        "reported_forbidden_code_patch_final_release_readiness_count"
    ] == 1
    assert forbidden_contract["unsafe_code_patch_final_release_readiness_record_count"] == 1

    print(
        "BP authoring durable executor code patch final release readiness contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
