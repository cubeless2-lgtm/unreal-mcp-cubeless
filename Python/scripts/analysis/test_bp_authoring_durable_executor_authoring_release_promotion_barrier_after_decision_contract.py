#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_authoring_release_promotion_barrier_after_decision_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_release_decision_after_review_contract as decision  # noqa: E402
import bp_authoring_durable_executor_authoring_release_promotion_barrier_after_decision_contract as barrier  # noqa: E402


def build_current_release_decision_after_review_summary() -> dict:
    return {
        "schema": decision.DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_AFTER_REVIEW_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_executor_authoring_release_decision_after_review_count": 1,
        "release_decision_contract_defined_count": 1,
        "release_review_contract_ready_count": 1,
        "release_review_inputs_satisfied_count": 0,
        "release_review_record_valid_count": 0,
        "allowed_release_review_observed_count": 0,
        "no_forbidden_release_review_claims_count": 0,
        "release_decision_inputs_satisfied_count": 0,
        "release_decision_record_present_count": 0,
        "record_schema_matches_count": 0,
        "release_decision_scope_matches_count": 0,
        "explicit_release_decision_authorized_count": 0,
        "release_decision_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "allowed_release_decision_observed_count": 0,
        "no_forbidden_release_decision_claims_count": 0,
        "release_decision_record_valid_count": 0,
        "release_decision_record_rejected_count": 0,
        "unsafe_release_decision_record_count": 0,
        "missing_release_decision_prerequisite_count": 14,
        "reported_allowed_release_decision_count": 0,
        "reported_forbidden_release_decision_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_review_started_count": 0,
        "durable_authoring_release_review_accepted_count": 0,
        "durable_authoring_final_release_readiness_started_count": 0,
        "durable_authoring_final_release_ready_count": 0,
        "durable_authoring_final_no_save_release_accepted_count": 0,
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
        "reported_release_decision_gate_count": 0,
        "reported_release_review_revalidated_count": 0,
        "reported_durable_authoring_still_disabled_count": 0,
        "reported_no_completion_release_decision_count": 0,
        "reported_no_write_release_decision_count": 0,
        "reported_no_save_release_decision_count": 0,
        "reported_no_code_change_release_decision_count": 0,
        "reported_no_live_command_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }


def build_release_promotion_barrier_record(**overrides: object) -> dict:
    record = {
        "schema": barrier.DURABLE_EXECUTOR_AUTHORING_RELEASE_PROMOTION_BARRIER_AFTER_DECISION_RECORD_SCHEMA,
        "release_promotion_barrier_scope": barrier.EXPECTED_RELEASE_PROMOTION_BARRIER_SCOPE,
        "explicit_durable_authoring_release_promotion_barrier_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
        "durable_authoring_release_promotion_barrier_started": False,
        "durable_authoring_release_promotion_barrier_accepted": False,
        "durable_executor_activation_readiness_started": False,
        "durable_executor_activated": False,
        "durable_executor_opened": False,
        "durable_authoring_release_decision_started": False,
        "durable_authoring_release_decision_accepted": False,
        "durable_authoring_release_review_started": False,
        "durable_authoring_release_review_accepted": False,
        "durable_authoring_final_release_readiness_started": False,
        "durable_authoring_final_release_ready": False,
        "durable_authoring_final_no_save_release_accepted": False,
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
        "reported_promotion_barrier_gate_count": 1,
        "reported_release_decision_revalidated_count": 1,
        "reported_durable_authoring_still_disabled_count": 1,
        "reported_no_completion_promotion_barrier_count": 1,
        "reported_no_write_promotion_barrier_count": 1,
        "reported_no_save_promotion_barrier_count": 1,
        "reported_no_code_change_promotion_barrier_count": 1,
        "reported_no_live_command_promotion_barrier_count": 1,
        "reported_release_decision_count": 0,
        "reported_release_review_count": 0,
        "reported_final_release_readiness_count": 0,
        "reported_final_no_save_release_count": 0,
        "reported_command_result_readback_count": 0,
        "reported_completion_result_acceptance_count": 0,
        "reported_completion_count": 0,
        "reported_executor_activation_count": 0,
        "reported_executor_open_count": 0,
        "reported_asset_write_count": 0,
        "reported_package_dirty_count": 0,
        "reported_save_count": 0,
        "reported_delete_rename_count": 0,
        "reported_cleanup_count": 0,
        "reported_durable_authoring_count": 0,
        "reported_code_change_count": 0,
        "reported_live_command_count": 0,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_release_decision_after_review_summary()
    contract = barrier.build_durable_executor_authoring_release_promotion_barrier_after_decision_contract(
        True,
        current_summary,
    )
    assert (
        contract["schema"]
        == barrier.DURABLE_EXECUTOR_AUTHORING_RELEASE_PROMOTION_BARRIER_AFTER_DECISION_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["release_promotion_barrier_contract_defined"] is True
    assert contract["release_decision_contract_ready"] is True
    assert contract["release_decision_inputs_satisfied"] is False
    assert contract["release_decision_record_valid"] is False
    assert contract["allowed_release_decision_observed"] is False
    assert contract["no_forbidden_release_decision_claims"] is False
    assert contract["release_promotion_barrier_inputs_satisfied"] is False
    assert contract["release_promotion_barrier_record_present"] is False
    assert contract["release_promotion_barrier_record_valid"] is False
    assert contract["release_promotion_barrier_record_rejected"] is False
    assert contract["unsafe_release_promotion_barrier_record_count"] == 0
    assert contract["missing_release_promotion_barrier_prerequisite_count"] == 14
    assert "section_140_release_decision_inputs_satisfied" in contract[
        "missing_release_promotion_barrier_prerequisites"
    ]
    assert "section_140_release_decision_record_valid" in contract[
        "missing_release_promotion_barrier_prerequisites"
    ]
    assert "section_140_allowed_release_decision_observed" in contract[
        "missing_release_promotion_barrier_prerequisites"
    ]
    assert "section_140_no_forbidden_release_decision_claims" in contract[
        "missing_release_promotion_barrier_prerequisites"
    ]
    assert "durable_authoring_release_promotion_barrier_record_present" in contract[
        "missing_release_promotion_barrier_prerequisites"
    ]
    assert "explicit_durable_mvp_request_reconfirmed" in contract[
        "missing_release_promotion_barrier_prerequisites"
    ]
    assert (
        "separate_durable_authoring_activation_readiness_after_promotion_barrier_contract"
        in contract["missing_release_promotion_barrier_prerequisites"]
    )
    assert contract["durable_authoring_release_promotion_barrier_started"] is False
    assert contract["durable_authoring_release_promotion_barrier_accepted"] is False
    assert contract["durable_executor_activation_readiness_started"] is False
    assert contract["durable_executor_activated"] is False
    assert contract["durable_executor_opened"] is False
    assert contract["asset_write_performed"] is False
    assert contract["code_change_performed"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = barrier.summarize_durable_executor_authoring_release_promotion_barriers_after_decision(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_release_promotion_barrier_after_decision_count"
        ]
        == 1
    )
    assert summary["release_promotion_barrier_contract_defined_count"] == 1
    assert summary["release_decision_contract_ready_count"] == 1
    assert summary["release_promotion_barrier_record_valid_count"] == 0
    assert summary["release_promotion_barrier_record_rejected_count"] == 0
    assert summary["unsafe_release_promotion_barrier_record_count"] == 0
    assert summary["missing_release_promotion_barrier_prerequisite_count"] == 14
    assert summary["durable_authoring_release_promotion_barrier_started_count"] == 0
    assert summary["durable_authoring_release_promotion_barrier_accepted_count"] == 0
    assert summary["durable_executor_activation_readiness_started_count"] == 0
    assert summary["durable_executor_activated_count"] == 0
    assert summary["durable_executor_opened_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["code_change_performed_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    future_summary = {
        **current_summary,
        "release_decision_inputs_satisfied_count": 1,
        "release_decision_record_valid_count": 1,
        "allowed_release_decision_observed_count": 1,
        "no_forbidden_release_decision_claims_count": 1,
    }
    future_contract = barrier.build_durable_executor_authoring_release_promotion_barrier_after_decision_contract(
        True,
        future_summary,
        build_release_promotion_barrier_record(),
    )
    assert future_contract["release_promotion_barrier_record_valid"] is True
    assert future_contract["missing_release_promotion_barrier_prerequisite_count"] == 1
    assert future_contract["missing_release_promotion_barrier_prerequisites"] == [
        "separate_durable_authoring_activation_readiness_after_promotion_barrier_contract"
    ]
    assert future_contract["reported_allowed_release_promotion_barrier_count"] == 8
    assert future_contract["reported_forbidden_release_promotion_barrier_count"] == 0
    assert future_contract["durable_authoring_release_promotion_barrier_started"] is False
    assert future_contract["durable_executor_activation_readiness_started"] is False
    assert future_contract["durable_executor_activated"] is False
    assert future_contract["durable_executor_opened"] is False
    assert future_contract["asset_write_performed"] is False
    assert future_contract["code_change_performed"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    unsafe_contract = barrier.build_durable_executor_authoring_release_promotion_barrier_after_decision_contract(
        True,
        future_summary,
        build_release_promotion_barrier_record(reported_save_count=1),
    )
    assert unsafe_contract["release_promotion_barrier_record_valid"] is False
    assert unsafe_contract["release_promotion_barrier_record_rejected"] is True
    assert unsafe_contract["unsafe_release_promotion_barrier_record_count"] == 1
    assert unsafe_contract["reported_forbidden_release_promotion_barrier_count"] == 1
    unsafe_summary = (
        barrier.summarize_durable_executor_authoring_release_promotion_barriers_after_decision(
            [unsafe_contract]
        )
    )
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["release_promotion_barrier_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_release_promotion_barrier_record_count"] == 1
    assert unsafe_summary["durable_authoring_release_promotion_barrier_started_count"] == 0
    assert unsafe_summary["durable_executor_activation_readiness_started_count"] == 0

    activation_contract = barrier.build_durable_executor_authoring_release_promotion_barrier_after_decision_contract(
        True,
        future_summary,
        build_release_promotion_barrier_record(
            durable_executor_activation_readiness_started=True
        ),
    )
    assert activation_contract["release_promotion_barrier_record_valid"] is False
    assert activation_contract["release_promotion_barrier_record_rejected"] is True
    assert activation_contract["unsafe_release_promotion_barrier_record_count"] == 1
    activation_summary = (
        barrier.summarize_durable_executor_authoring_release_promotion_barriers_after_decision(
            [activation_contract]
        )
    )
    assert activation_summary["status"] == "failed"
    assert activation_summary["durable_executor_activation_readiness_started_count"] == 0

    print(
        "BP authoring durable executor authoring release promotion barrier-after-decision contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
