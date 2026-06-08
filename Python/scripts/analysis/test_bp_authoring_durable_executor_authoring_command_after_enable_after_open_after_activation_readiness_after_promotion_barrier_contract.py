#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_contract as command  # noqa: E402
import bp_authoring_durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_contract as enable  # noqa: E402


def build_current_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_summary() -> dict:
    return {
        "schema": enable.DURABLE_EXECUTOR_AUTHORING_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_AFTER_PROMOTION_BARRIER_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
        "authoring_enable_contract_defined_count": 1,
        "executor_open_contract_ready_count": 1,
        "open_inputs_satisfied_count": 0,
        "open_record_valid_count": 0,
        "allowed_open_observed_count": 0,
        "no_forbidden_open_claims_count": 0,
        "authoring_enable_inputs_satisfied_count": 0,
        "authoring_enable_record_present_count": 0,
        "record_schema_matches_count": 0,
        "enable_scope_matches_count": 0,
        "explicit_authoring_enable_authorized_count": 0,
        "authoring_enable_status_passed_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "explicit_durable_mvp_request_reconfirmed_count": 0,
        "target_package_allowlist_reconfirmed_count": 0,
        "overwrite_rename_decision_reconfirmed_count": 0,
        "rollback_readiness_reconfirmed_count": 0,
        "ownership_marker_reconfirmed_count": 0,
        "allowed_authoring_enable_observed_count": 0,
        "no_forbidden_authoring_enable_claims_count": 0,
        "authoring_enable_record_valid_count": 0,
        "authoring_enable_record_rejected_count": 0,
        "unsafe_authoring_enable_record_count": 0,
        "missing_authoring_enable_prerequisite_count": 18,
        "reported_allowed_authoring_enable_count": 0,
        "reported_forbidden_authoring_enable_count": 0,
        "durable_authoring_enable_started_count": 0,
        "durable_authoring_enable_accepted_count": 0,
        "durable_authoring_enable_allowed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "durable_authoring_command_contract_started_count": 0,
        "durable_executor_open_contract_started_count": 0,
        "durable_executor_open_contract_accepted_count": 0,
        "durable_executor_open_performed_count": 0,
        "durable_executor_activated_count": 0,
        "durable_executor_opened_count": 0,
        "durable_executor_activation_readiness_started_count": 0,
        "durable_executor_activation_readiness_accepted_count": 0,
        "durable_authoring_release_promotion_barrier_started_count": 0,
        "durable_authoring_release_promotion_barrier_accepted_count": 0,
        "durable_authoring_release_decision_started_count": 0,
        "durable_authoring_release_decision_accepted_count": 0,
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
        "code_change_performed_count": 0,
        "executor_code_modified_count": 0,
        "unreal_asset_modified_count": 0,
        "live_bridge_probe_started_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatched_count": 0,
        "live_command_executed_count": 0,
    }


def build_command_record(**overrides: object) -> dict:
    record = {
        "schema": command.DURABLE_EXECUTOR_AUTHORING_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_AFTER_PROMOTION_BARRIER_RECORD_SCHEMA,
        "command_scope": command.EXPECTED_COMMAND_SCOPE,
        "explicit_durable_authoring_command_authorized": True,
        "status": "passed",
        "operator_reconfirmed_no_save_delete_rename": True,
        "explicit_durable_mvp_request_reconfirmed": True,
        "commands": [
            "create_blueprint_asset",
            "compile_and_validate_blueprint",
            "write_executor_ownership_marker",
            "readback_executor_ownership_marker",
        ],
        "durable_authoring_command_contract_started": False,
        "durable_authoring_command_contract_accepted": False,
        "durable_authoring_command_allowed": False,
        "durable_executor_command_path_opened": False,
        "durable_executor_command_path_allowed": False,
        "durable_authoring_command_dispatched": False,
        "durable_authoring_command_executed": False,
        "durable_authoring_enable_started": False,
        "durable_authoring_enable_accepted": False,
        "durable_authoring_enable_allowed": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "durable_executor_open_contract_started": False,
        "durable_executor_open_contract_accepted": False,
        "durable_executor_open_performed": False,
        "durable_executor_activated": False,
        "durable_executor_opened": False,
        "durable_executor_activation_readiness_started": False,
        "durable_executor_activation_readiness_accepted": False,
        "durable_authoring_release_promotion_barrier_started": False,
        "durable_authoring_release_promotion_barrier_accepted": False,
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
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_summary()
    contract = command.build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_contract(
        True,
        current_summary,
    )
    assert (
        contract["schema"]
        == command.DURABLE_EXECUTOR_AUTHORING_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_AFTER_PROMOTION_BARRIER_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["authoring_command_contract_defined"] is True
    assert contract["authoring_enable_contract_ready"] is True
    assert contract["open_inputs_satisfied"] is False
    assert contract["open_record_valid"] is False
    assert contract["allowed_open_observed"] is False
    assert contract["no_forbidden_open_claims"] is False
    assert contract["open_activation_promotion_readiness_chain_satisfied"] is False
    assert contract["authoring_enable_inputs_satisfied"] is False
    assert contract["authoring_enable_record_valid"] is False
    assert contract["allowed_authoring_enable_observed"] is False
    assert contract["no_forbidden_authoring_enable_claims"] is False
    assert contract["authoring_enable_chain_satisfied"] is False
    assert contract["target_package_allowlist_reconfirmed"] is False
    assert contract["overwrite_rename_decision_reconfirmed"] is False
    assert contract["rollback_readiness_reconfirmed"] is False
    assert contract["ownership_marker_reconfirmed"] is False
    assert contract["durable_release_readiness_chain_reconfirmed"] is False
    assert contract["authoring_command_inputs_satisfied"] is False
    assert contract["authoring_command_record_present"] is False
    assert contract["authoring_command_record_valid"] is False
    assert contract["authoring_command_record_rejected"] is False
    assert contract["unsafe_authoring_command_record_count"] == 0
    assert contract["missing_authoring_command_prerequisite_count"] == 21
    assert "section_160_open_inputs_satisfied" in contract[
        "missing_authoring_command_prerequisites"
    ]
    assert "section_160_authoring_enable_inputs_satisfied" in contract[
        "missing_authoring_command_prerequisites"
    ]
    assert "section_160_target_package_allowlist_reconfirmed" in contract[
        "missing_authoring_command_prerequisites"
    ]
    assert "durable_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_record_present" in contract[
        "missing_authoring_command_prerequisites"
    ]
    assert "durable_authoring_commands_present" in contract[
        "missing_authoring_command_prerequisites"
    ]
    assert "separate_durable_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_contract" in contract[
        "missing_authoring_command_prerequisites"
    ]
    assert contract["durable_authoring_command_contract_started"] is False
    assert contract["durable_authoring_command_contract_accepted"] is False
    assert contract["durable_authoring_command_allowed"] is False
    assert contract["durable_executor_command_path_opened"] is False
    assert contract["durable_executor_command_path_allowed"] is False
    assert contract["durable_authoring_command_dispatched"] is False
    assert contract["durable_authoring_command_executed"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["durable_authoring_allowed"] is False
    assert contract["asset_write_performed"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = command.summarize_durable_executor_authoring_commands_after_enable_after_open_after_activation_readiness_after_promotion_barrier(
        [contract]
    )
    assert summary["status"] == "passed"
    assert summary["durable_requested_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count"] == 1
    assert summary["authoring_command_contract_defined_count"] == 1
    assert summary["authoring_enable_contract_ready_count"] == 1
    assert summary["authoring_command_record_valid_count"] == 0
    assert summary["authoring_command_record_rejected_count"] == 0
    assert summary["unsafe_authoring_command_record_count"] == 0
    assert summary["missing_authoring_command_prerequisite_count"] == 21
    assert summary["planned_authoring_command_count"] == 0
    assert summary["allowed_authoring_command_count"] == 0
    assert summary["forbidden_authoring_command_count"] == 0
    assert summary["unknown_authoring_command_count"] == 0
    assert summary["durable_authoring_command_contract_started_count"] == 0
    assert summary["durable_authoring_command_contract_accepted_count"] == 0
    assert summary["durable_authoring_command_allowed_count"] == 0
    assert summary["durable_executor_command_path_opened_count"] == 0
    assert summary["durable_executor_command_path_allowed_count"] == 0
    assert summary["durable_authoring_command_dispatched_count"] == 0
    assert summary["durable_authoring_command_executed_count"] == 0
    assert summary["durable_authoring_enabled_count"] == 0
    assert summary["durable_authoring_allowed_count"] == 0
    assert summary["asset_write_performed_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    blocked_with_record = command.build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_contract(
        True,
        current_summary,
        build_command_record(),
    )
    assert blocked_with_record["authoring_command_record_valid"] is False
    assert blocked_with_record["authoring_command_record_rejected"] is True
    assert blocked_with_record["planned_authoring_command_count"] == 4
    assert blocked_with_record["allowed_authoring_command_count"] == 4
    assert blocked_with_record["durable_executor_command_path_opened"] is False
    assert blocked_with_record["durable_authoring_command_allowed"] is False
    assert blocked_with_record["durable_authoring_enabled"] is False
    assert blocked_with_record["save_delete_rename_allowed"] is False

    future_summary = {
        **current_summary,
        "open_inputs_satisfied_count": 1,
        "open_record_valid_count": 1,
        "allowed_open_observed_count": 1,
        "no_forbidden_open_claims_count": 1,
        "authoring_enable_inputs_satisfied_count": 1,
        "authoring_enable_record_valid_count": 1,
        "allowed_authoring_enable_observed_count": 1,
        "no_forbidden_authoring_enable_claims_count": 1,
        "target_package_allowlist_reconfirmed_count": 1,
        "overwrite_rename_decision_reconfirmed_count": 1,
        "rollback_readiness_reconfirmed_count": 1,
        "ownership_marker_reconfirmed_count": 1,
    }
    future_contract = command.build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_contract(
        True,
        future_summary,
        build_command_record(),
    )
    assert future_contract["open_activation_promotion_readiness_chain_satisfied"] is True
    assert future_contract["authoring_enable_chain_satisfied"] is True
    assert future_contract["durable_release_readiness_chain_reconfirmed"] is True
    assert future_contract["authoring_command_inputs_satisfied"] is True
    assert future_contract["authoring_command_record_valid"] is True
    assert future_contract["planned_authoring_command_count"] == 4
    assert future_contract["allowed_authoring_command_count"] == 4
    assert future_contract["missing_authoring_command_prerequisite_count"] == 1
    assert future_contract["missing_authoring_command_prerequisites"] == [
        "separate_durable_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_contract"
    ]
    assert future_contract["durable_authoring_command_allowed"] is False
    assert future_contract["durable_executor_command_path_opened"] is False
    assert future_contract["durable_executor_command_path_allowed"] is False
    assert future_contract["durable_authoring_command_dispatched"] is False
    assert future_contract["durable_authoring_command_executed"] is False
    assert future_contract["durable_authoring_enabled"] is False
    assert future_contract["durable_authoring_allowed"] is False
    assert future_contract["asset_write_performed"] is False
    assert future_contract["save_delete_rename_allowed"] is False

    forbidden_contract = command.build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_contract(
        True,
        future_summary,
        build_command_record(commands=["create_blueprint_asset", "save_asset"]),
    )
    assert forbidden_contract["authoring_command_record_valid"] is False
    assert forbidden_contract["authoring_command_record_rejected"] is True
    assert forbidden_contract["forbidden_authoring_command_count"] == 1
    forbidden_summary = command.summarize_durable_executor_authoring_commands_after_enable_after_open_after_activation_readiness_after_promotion_barrier(
        [forbidden_contract]
    )
    assert forbidden_summary["status"] == "failed"
    assert forbidden_summary["authoring_command_record_rejected_count"] == 1
    assert forbidden_summary["forbidden_authoring_command_count"] == 1
    assert forbidden_summary["durable_authoring_command_executed_count"] == 0
    assert forbidden_summary["durable_authoring_allowed_count"] == 0

    unsafe_contract = command.build_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_contract(
        True,
        future_summary,
        build_command_record(durable_executor_command_path_opened=True),
    )
    assert unsafe_contract["authoring_command_record_valid"] is False
    assert unsafe_contract["authoring_command_record_rejected"] is True
    assert unsafe_contract["unsafe_authoring_command_record_count"] == 1

    print(
        "BP authoring durable executor authoring command-after-enable-after-open-after-activation-readiness-after-promotion-barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
