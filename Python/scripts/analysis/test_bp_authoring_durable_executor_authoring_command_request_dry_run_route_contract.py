#!/usr/bin/env python
"""Offline smoke tests for Section 162 command request dry-run route contract."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_command_request_dry_run_route_contract as route  # noqa: E402
import bp_authoring_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_contract as section_161  # noqa: E402


def build_section_161_summary(**overrides: object) -> dict:
    summary = {
        "schema": section_161.DURABLE_EXECUTOR_AUTHORING_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_AFTER_PROMOTION_BARRIER_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
        "authoring_command_contract_defined_count": 1,
        "authoring_enable_contract_ready_count": 1,
        "open_activation_promotion_readiness_chain_satisfied_count": 0,
        "authoring_enable_chain_satisfied_count": 0,
        "durable_release_readiness_chain_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_valid_count": 0,
        "authoring_command_record_rejected_count": 0,
        "unsafe_authoring_command_record_count": 0,
        "forbidden_authoring_command_count": 0,
        "unknown_authoring_command_count": 0,
        "durable_authoring_command_contract_started_count": 0,
        "durable_authoring_command_contract_accepted_count": 0,
        "durable_authoring_command_allowed_count": 0,
        "durable_executor_command_path_opened_count": 0,
        "durable_executor_command_path_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
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
    summary.update(overrides)
    return summary


def build_request_record(**overrides: object) -> dict:
    record = {
        "schema": route.DURABLE_EXECUTOR_AUTHORING_COMMAND_REQUEST_DRY_RUN_ROUTE_RECORD_SCHEMA,
        "route_scope": route.EXPECTED_DRY_RUN_ROUTE_SCOPE,
        "status": "passed",
        "dry_run_only": True,
        "requested_command": "create_blueprint_asset",
        "dry_run_operation": "route_dry_run_only",
        "target_asset": "/Game/MCPTestFixtures/BP_PlannerDurable",
        "operator_reconfirmed_no_write_execution": True,
        "operator_reconfirmed_no_save_delete_rename": True,
        "readiness_proof": {
            "open_activation_promotion_readiness_chain_satisfied": True,
            "authoring_enable_chain_satisfied": True,
            "durable_release_readiness_chain_reconfirmed": True,
            "authoring_command_inputs_satisfied": True,
            "authoring_command_record_valid": True,
        },
        "release_boundary_proof": {
            "durable_authoring_enabled": False,
            "final_durable_release_ready": False,
            "save_delete_rename_allowed": False,
            "live_durable_authoring_allowed": False,
        },
        "durable_command_request_promoted": False,
        "durable_executor_command_path_opened": False,
        "durable_executor_command_path_allowed": False,
        "durable_authoring_command_allowed": False,
        "durable_authoring_command_dispatched": False,
        "durable_authoring_command_executed": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "final_durable_release_ready": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "code_change_performed": False,
        "executor_code_modified": False,
        "unreal_asset_modified": False,
        "live_bridge_probe_started": False,
        "save_delete_rename_allowed": False,
        "save_asset_allowed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatched": False,
        "live_command_executed": False,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_section_161_summary()
    contract = route.build_durable_executor_authoring_command_request_dry_run_route_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == route.DURABLE_EXECUTOR_AUTHORING_COMMAND_REQUEST_DRY_RUN_ROUTE_SCHEMA
    assert contract["requested"] is True
    assert contract["route_contract_defined"] is True
    assert contract["section_161_command_contract_ready"] is True
    assert contract["readiness_chain_satisfied"] is False
    assert contract["dry_run_route_record_present"] is False
    assert contract["dry_run_route_record_valid"] is False
    assert contract["dry_run_route_record_rejected"] is False
    assert contract["dry_run_route_admissible"] is False
    assert contract["missing_dry_run_route_prerequisite_count"] == 17
    assert "open_activation_promotion_readiness_chain_satisfied" in contract[
        "missing_dry_run_route_prerequisites"
    ]
    assert "command_request_dry_run_route_record_present" in contract[
        "missing_dry_run_route_prerequisites"
    ]
    assert contract["durable_command_request_promoted"] is False
    assert contract["durable_executor_command_path_opened"] is False
    assert contract["durable_executor_command_path_allowed"] is False
    assert contract["durable_authoring_command_dispatched"] is False
    assert contract["durable_authoring_command_executed"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["final_durable_release_ready"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = route.summarize_durable_executor_authoring_command_request_dry_run_routes(
        [contract]
    )
    assert summary["status"] == "passed"
    assert summary["durable_requested_executor_authoring_command_request_dry_run_route_count"] == 1
    assert summary["route_contract_defined_count"] == 1
    assert summary["section_161_command_contract_ready_count"] == 1
    assert summary["readiness_chain_satisfied_count"] == 0
    assert summary["dry_run_route_record_present_count"] == 0
    assert summary["dry_run_route_record_valid_count"] == 0
    assert summary["dry_run_route_record_rejected_count"] == 0
    assert summary["dry_run_route_admissible_count"] == 0
    assert summary["durable_command_request_promoted_count"] == 0
    assert summary["durable_executor_command_path_opened_count"] == 0
    assert summary["durable_authoring_command_executed_count"] == 0
    assert summary["durable_authoring_enabled_count"] == 0
    assert summary["final_durable_release_ready_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    blocked_with_record = route.build_durable_executor_authoring_command_request_dry_run_route_contract(
        True,
        current_summary,
        build_request_record(),
    )
    assert blocked_with_record["readiness_chain_satisfied"] is False
    assert blocked_with_record["dry_run_route_record_valid"] is False
    assert blocked_with_record["dry_run_route_record_rejected"] is True
    assert blocked_with_record["dry_run_route_admissible"] is False
    assert blocked_with_record["missing_dry_run_route_prerequisite_count"] == 5
    assert blocked_with_record["durable_executor_command_path_opened"] is False
    assert blocked_with_record["durable_authoring_command_executed"] is False
    assert blocked_with_record["save_delete_rename_allowed"] is False

    future_summary = build_section_161_summary(
        open_activation_promotion_readiness_chain_satisfied_count=1,
        authoring_enable_chain_satisfied_count=1,
        durable_release_readiness_chain_reconfirmed_count=1,
        authoring_command_inputs_satisfied_count=1,
        authoring_command_record_valid_count=1,
    )
    future_contract = route.build_durable_executor_authoring_command_request_dry_run_route_contract(
        True,
        future_summary,
        build_request_record(),
    )
    assert future_contract["readiness_chain_satisfied"] is True
    assert future_contract["dry_run_route_record_valid"] is True
    assert future_contract["dry_run_route_record_rejected"] is False
    assert future_contract["dry_run_route_admissible"] is True
    assert future_contract["missing_dry_run_route_prerequisite_count"] == 0
    assert future_contract["durable_command_request_promoted"] is False
    assert future_contract["durable_executor_command_path_opened"] is False
    assert future_contract["durable_executor_command_path_allowed"] is False
    assert future_contract["durable_authoring_command_allowed"] is False
    assert future_contract["durable_authoring_command_dispatched"] is False
    assert future_contract["durable_authoring_command_executed"] is False
    assert future_contract["durable_authoring_enabled"] is False
    assert future_contract["final_durable_release_ready"] is False
    assert future_contract["asset_write_performed"] is False
    assert future_contract["package_dirty_marked"] is False
    assert future_contract["save_delete_rename_allowed"] is False
    future_summary_result = route.summarize_durable_executor_authoring_command_request_dry_run_routes(
        [future_contract]
    )
    assert future_summary_result["status"] == "passed"
    assert future_summary_result["dry_run_route_admissible_count"] == 1
    assert future_summary_result["durable_command_request_promoted_count"] == 0
    assert future_summary_result["durable_executor_command_path_opened_count"] == 0
    assert future_summary_result["durable_authoring_command_executed_count"] == 0
    assert future_summary_result["save_delete_rename_allowed_count"] == 0

    forbidden_contract = route.build_durable_executor_authoring_command_request_dry_run_route_contract(
        True,
        future_summary,
        build_request_record(requested_command="save_asset"),
    )
    assert forbidden_contract["requested_command_forbidden"] is True
    assert forbidden_contract["dry_run_route_record_rejected"] is True
    assert forbidden_contract["dry_run_route_admissible"] is False
    forbidden_summary = route.summarize_durable_executor_authoring_command_request_dry_run_routes(
        [forbidden_contract]
    )
    assert forbidden_summary["status"] == "failed"
    assert forbidden_summary["requested_command_forbidden_count"] == 1
    assert forbidden_summary["durable_authoring_command_executed_count"] == 0
    assert forbidden_summary["save_delete_rename_allowed_count"] == 0

    unsafe_contract = route.build_durable_executor_authoring_command_request_dry_run_route_contract(
        True,
        future_summary,
        build_request_record(durable_executor_command_path_opened=True),
    )
    assert unsafe_contract["unsafe_request_record_count"] == 1
    assert unsafe_contract["dry_run_route_record_rejected"] is True
    assert unsafe_contract["dry_run_route_admissible"] is False
    assert unsafe_contract["durable_executor_command_path_opened"] is False
    assert unsafe_contract["durable_authoring_command_executed"] is False
    assert unsafe_contract["save_delete_rename_allowed"] is False

    print("BP authoring durable executor authoring command request dry-run route contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
