#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_authoring_final_no_save_release_after_readback_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_command_result_readback_after_result_contract as readback  # noqa: E402
import bp_authoring_durable_executor_authoring_final_no_save_release_after_readback_contract as final_release  # noqa: E402


def build_current_readback_after_result_summary() -> dict:
    return {
        "schema": readback.DURABLE_EXECUTOR_AUTHORING_COMMAND_RESULT_READBACK_AFTER_RESULT_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_executor_authoring_command_result_readback_after_result_count": 1,
        "readback_contract_defined_count": 1,
        "result_contract_ready_count": 1,
        "result_inputs_satisfied_count": 0,
        "result_record_valid_count": 0,
        "allowed_result_observed_count": 0,
        "no_forbidden_results_count": 0,
        "readback_inputs_satisfied_count": 0,
        "readback_record_present_count": 0,
        "record_schema_matches_count": 0,
        "readback_scope_matches_count": 0,
        "explicit_readback_authorized_count": 0,
        "readback_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_readback_observed_count": 0,
        "no_forbidden_readbacks_count": 0,
        "readback_record_valid_count": 0,
        "readback_record_rejected_count": 0,
        "unsafe_readback_record_count": 0,
        "missing_readback_prerequisite_count": 14,
        "reported_allowed_readback_count": 0,
        "reported_forbidden_readback_count": 0,
        "durable_authoring_command_result_readback_accepted_count": 0,
        "durable_authoring_command_completion_result_accepted_count": 0,
        "durable_authoring_command_completed_count": 0,
        "asset_write_performed_count": 0,
        "package_dirty_marked_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
        "reported_no_completion_readback_count": 0,
        "reported_no_write_readback_count": 0,
        "reported_no_save_readback_count": 0,
        "reported_completed_readback_count": 0,
        "reported_asset_write_readback_count": 0,
        "reported_package_dirty_readback_count": 0,
        "reported_save_readback_count": 0,
        "reported_delete_rename_readback_count": 0,
        "reported_cleanup_readback_count": 0,
        "reported_code_change_readback_count": 0,
        "reported_live_command_readback_count": 0,
    }


def build_final_no_save_release_record(**overrides: object) -> dict:
    record = {
        "schema": final_release.DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_AFTER_READBACK_RECORD_SCHEMA,
        "final_no_save_release_scope": final_release.EXPECTED_FINAL_NO_SAVE_RELEASE_SCOPE,
        "explicit_durable_authoring_final_no_save_release_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
        "durable_authoring_final_no_save_release_accepted": False,
        "durable_authoring_final_release_readiness_started": False,
        "durable_authoring_command_result_readback_accepted": False,
        "durable_authoring_command_completion_result_accepted": False,
        "durable_authoring_command_completed": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "code_change_performed": False,
        "executor_code_modified": False,
        "unreal_asset_modified": False,
        "live_bridge_probe_started": False,
        "save_asset_executed": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
        "live_command_dispatch_performed": False,
        "live_command_dispatched": False,
        "live_command_execution_performed": False,
        "live_command_executed": False,
        "reported_no_completion_release_count": 1,
        "reported_no_write_release_count": 1,
        "reported_no_save_release_count": 1,
        "reported_readback_revalidated_count": 1,
        "reported_no_code_change_release_count": 1,
        "reported_no_live_command_release_count": 1,
        "reported_completion_release_count": 0,
        "reported_asset_write_release_count": 0,
        "reported_package_dirty_release_count": 0,
        "reported_save_release_count": 0,
        "reported_delete_rename_release_count": 0,
        "reported_cleanup_release_count": 0,
        "reported_durable_authoring_release_count": 0,
        "reported_code_change_release_count": 0,
        "reported_live_command_release_count": 0,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_readback_after_result_summary()
    contract = final_release.build_durable_executor_authoring_final_no_save_release_after_readback_contract(
        True,
        current_summary,
    )
    assert (
        contract["schema"]
        == final_release.DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_AFTER_READBACK_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["final_no_save_release_contract_defined"] is True
    assert contract["readback_contract_ready"] is True
    assert contract["readback_inputs_satisfied"] is False
    assert contract["readback_record_valid"] is False
    assert contract["allowed_readback_observed"] is False
    assert contract["no_forbidden_readbacks"] is False
    assert contract["final_no_save_release_inputs_satisfied"] is False
    assert contract["final_no_save_release_record_present"] is False
    assert contract["final_no_save_release_record_valid"] is False
    assert contract["final_no_save_release_record_rejected"] is False
    assert contract["unsafe_final_no_save_release_record_count"] == 0
    assert contract["missing_final_no_save_release_prerequisite_count"] == 14
    assert "section_136_readback_inputs_satisfied" in contract[
        "missing_final_no_save_release_prerequisites"
    ]
    assert "section_136_readback_record_valid" in contract[
        "missing_final_no_save_release_prerequisites"
    ]
    assert "section_136_allowed_readback_observed" in contract[
        "missing_final_no_save_release_prerequisites"
    ]
    assert "section_136_no_forbidden_readbacks" in contract[
        "missing_final_no_save_release_prerequisites"
    ]
    assert "durable_authoring_final_no_save_release_record_present" in contract[
        "missing_final_no_save_release_prerequisites"
    ]
    assert "explicit_durable_mvp_request_reconfirmed" in contract[
        "missing_final_no_save_release_prerequisites"
    ]
    assert (
        "separate_durable_authoring_final_release_readiness_after_no_save_release_contract"
        in contract["missing_final_no_save_release_prerequisites"]
    )
    assert contract["durable_authoring_final_no_save_release_accepted"] is False
    assert contract["durable_authoring_final_release_readiness_started"] is False
    assert contract["durable_authoring_command_result_readback_accepted"] is False
    assert contract["durable_authoring_command_completed"] is False
    assert contract["asset_write_performed"] is False
    assert contract["code_change_performed"] is False
    assert contract["live_bridge_probe_started"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = (
        final_release.summarize_durable_executor_authoring_final_no_save_releases_after_readback(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_final_no_save_release_after_readback_count"
        ]
        == 1
    )
    assert summary["final_no_save_release_contract_defined_count"] == 1
    assert summary["readback_contract_ready_count"] == 1
    assert summary["final_no_save_release_record_valid_count"] == 0
    assert summary["final_no_save_release_record_rejected_count"] == 0
    assert summary["unsafe_final_no_save_release_record_count"] == 0
    assert summary["missing_final_no_save_release_prerequisite_count"] == 14
    assert summary["durable_authoring_final_no_save_release_accepted_count"] == 0
    assert summary["durable_authoring_final_release_readiness_started_count"] == 0
    assert summary["durable_authoring_command_result_readback_accepted_count"] == 0
    assert summary["durable_authoring_command_completed_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["code_change_performed_count"] == 0
    assert summary["live_bridge_probe_started_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    future_summary = {
        **current_summary,
        "readback_inputs_satisfied_count": 1,
        "readback_record_valid_count": 1,
        "allowed_readback_observed_count": 1,
        "no_forbidden_readbacks_count": 1,
    }
    future_contract = final_release.build_durable_executor_authoring_final_no_save_release_after_readback_contract(
        True,
        future_summary,
        build_final_no_save_release_record(),
    )
    assert future_contract["final_no_save_release_record_valid"] is True
    assert future_contract["missing_final_no_save_release_prerequisite_count"] == 1
    assert future_contract["missing_final_no_save_release_prerequisites"] == [
        "separate_durable_authoring_final_release_readiness_after_no_save_release_contract"
    ]
    assert future_contract["reported_allowed_final_no_save_release_count"] == 6
    assert future_contract["reported_forbidden_final_no_save_release_count"] == 0
    assert future_contract["durable_authoring_final_no_save_release_accepted"] is False
    assert future_contract["durable_authoring_final_release_readiness_started"] is False
    assert future_contract["durable_authoring_command_result_readback_accepted"] is False
    assert future_contract["asset_write_performed"] is False
    assert future_contract["code_change_performed"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    unsafe_contract = final_release.build_durable_executor_authoring_final_no_save_release_after_readback_contract(
        True,
        future_summary,
        build_final_no_save_release_record(reported_save_release_count=1),
    )
    assert unsafe_contract["final_no_save_release_record_valid"] is False
    assert unsafe_contract["final_no_save_release_record_rejected"] is True
    assert unsafe_contract["unsafe_final_no_save_release_record_count"] == 1
    assert unsafe_contract["reported_forbidden_final_no_save_release_count"] == 1
    unsafe_summary = (
        final_release.summarize_durable_executor_authoring_final_no_save_releases_after_readback(
            [unsafe_contract]
        )
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["final_no_save_release_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_final_no_save_release_record_count"] == 1
    assert unsafe_summary["durable_authoring_final_no_save_release_accepted_count"] == 0
    assert unsafe_summary["save_delete_rename_allowed_count"] == 0

    code_change_contract = final_release.build_durable_executor_authoring_final_no_save_release_after_readback_contract(
        True,
        future_summary,
        build_final_no_save_release_record(code_change_performed=True),
    )
    assert code_change_contract["final_no_save_release_record_valid"] is False
    assert code_change_contract["final_no_save_release_record_rejected"] is True
    assert code_change_contract["unsafe_final_no_save_release_record_count"] == 1
    code_change_summary = (
        final_release.summarize_durable_executor_authoring_final_no_save_releases_after_readback(
            [code_change_contract]
        )
    )
    assert code_change_summary["status"] == "failed"
    assert code_change_summary["code_change_performed_count"] == 0

    print(
        "BP authoring durable executor authoring final no-save release-after-readback contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
