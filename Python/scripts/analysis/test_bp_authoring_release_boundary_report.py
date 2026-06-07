#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_release_boundary_report.py."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_release_boundary_report as release_boundary  # noqa: E402


def find_row(report: dict, row_id: str) -> dict:
    for item in report["regression_matrix"]:
        if item["id"] == row_id:
            return item
    raise AssertionError(f"missing row {row_id}")


def main() -> int:
    repo_root = SCRIPT_DIR.parents[2]
    with tempfile.TemporaryDirectory(prefix="mcp_release_boundary_fixture_") as temp_dir:
        project_root = Path(temp_dir)
        (project_root / "Content" / "_MCP_Temp" / "PlannerDrivenSmoke").mkdir(parents=True)
        report = release_boundary.build_report(repo_root=repo_root, project_root=project_root)
        assert report["schema"] == release_boundary.REPORT_SCHEMA
        assert report["verdict"]["status"] == "passed"
        assert report["verdict"]["release_boundary_version"] == "section_69_v11"
        assert report["verdict"]["section_51_58_contract_status"] == "passed"
        assert report["verdict"]["section_61_bridge_refresh_status"] == "passed"
        assert report["verdict"]["section_62_live_evidence_refresh_status"] == "passed"
        assert report["verdict"]["section_63_executor_review_status"] == "passed"
        assert report["verdict"]["section_64_canary_command_allowlist_status"] == "passed"
        assert report["verdict"]["section_65_canary_creation_boundary_status"] == "passed"
        assert report["verdict"]["section_66_ownership_marker_proof_status"] == "passed"
        assert report["verdict"]["section_67_rollback_cleanup_proof_status"] == "passed"
        assert report["verdict"]["section_68_save_gate_final_review_status"] == "passed"
        assert report["verdict"]["section_69_canary_rehearsal_readiness_status"] == "passed"
        assert report["verdict"]["mvp_decision_status"] == "temporary_mvp_ready_durable_not_enabled"
        assert report["verdict"]["temporary_blueprint_authoring_mvp_ready"] is True
        assert report["verdict"]["durable_blueprint_authoring_mvp_ready"] is False
        assert report["verdict"]["ready_for_main_push"] is True
        assert report["verdict"]["durable_authoring_enabled"] is False
        assert find_row(report, "job_contract_default_request_set")["status"] == "passed"
        assert find_row(report, "manifest_executor_policy")["status"] == "passed"
        assert find_row(report, "executor_capability_matrix")["status"] == "passed"
        assert find_row(report, "durable_executor_gate_matrix")["status"] == "passed"
        enable_row = find_row(report, "durable_authoring_enable_contract")
        assert enable_row["status"] == "passed"
        assert enable_row["actual"]["enable_contract_satisfied_count"] == 0
        assert enable_row["actual"]["durable_executor_may_open_count"] == 0
        assert enable_row["actual"]["executor_gate_may_open_count"] == 0
        assert enable_row["actual"]["ownership_marker_passed_count"] == 1
        ownership_row = find_row(report, "durable_ownership_marker_contract")
        assert ownership_row["status"] == "passed"
        assert ownership_row["actual"]["durable_ownership_marker_policy_ready_count"] == 1
        assert ownership_row["actual"]["durable_ownership_delete_without_marker_allowed_count"] == 0
        assert ownership_row["actual"]["durable_ownership_delete_preexisting_asset_allowed_count"] == 0
        dry_run_row = find_row(report, "durable_executor_dry_run_plan")
        assert dry_run_row["status"] == "passed"
        assert dry_run_row["actual"]["dry_run_plan_created_count"] == 1
        assert dry_run_row["actual"]["dry_run_plan_valid_count"] == 1
        assert dry_run_row["actual"]["durable_executor_may_execute_count"] == 0
        assert dry_run_row["actual"]["live_command_count"] == 0
        save_sim_row = find_row(report, "durable_save_validation_simulator")
        assert save_sim_row["status"] == "passed"
        assert save_sim_row["actual"]["simulation_evaluated_count"] == 1
        assert save_sim_row["actual"]["future_save_conditions_satisfied_count"] == 0
        assert save_sim_row["actual"]["save_true_allowed_count"] == 0
        assert save_sim_row["actual"]["save_asset_allowed_count"] == 0
        assert save_sim_row["actual"]["live_command_count"] == 0
        canary_row = find_row(report, "durable_canary_prep_contract")
        assert canary_row["status"] == "passed"
        assert canary_row["actual"]["durable_requested_canary_prep_count"] == 1
        assert canary_row["actual"]["canary_prep_ready_count"] == 1
        assert canary_row["actual"]["canary_live_execution_allowed_count"] == 0
        assert canary_row["actual"]["general_blueprints_package_allowed_count"] == 0
        assert canary_row["actual"]["save_true_allowed_count"] == 0
        assert canary_row["actual"]["save_asset_allowed_count"] == 0
        assert canary_row["actual"]["delete_asset_allowed_count"] == 0
        canary_approval_row = find_row(report, "durable_canary_approval_gate_contract")
        assert canary_approval_row["status"] == "passed"
        assert canary_approval_row["actual"]["durable_requested_canary_approval_count"] == 1
        assert canary_approval_row["actual"]["approval_record_present_count"] == 1
        assert canary_approval_row["actual"]["canary_approval_gate_passed_count"] == 1
        assert canary_approval_row["actual"]["canary_executor_may_open_count"] == 0
        assert canary_approval_row["actual"]["canary_live_execution_allowed_count"] == 0
        assert canary_approval_row["actual"]["live_command_count"] == 0
        canary_live_preflight_row = find_row(report, "durable_canary_live_preflight_contract")
        assert canary_live_preflight_row["status"] == "passed"
        assert canary_live_preflight_row["actual"]["durable_requested_canary_live_preflight_count"] == 1
        assert canary_live_preflight_row["actual"]["read_only_live_preflight_allowed_count"] == 1
        assert canary_live_preflight_row["actual"]["canary_execution_allowed_after_preflight_count"] == 0
        assert canary_live_preflight_row["actual"]["live_save_or_delete_command_count"] == 0
        assert canary_live_preflight_row["actual"]["live_cleanup_command_count"] == 0
        canary_bridge_refresh_row = find_row(report, "durable_canary_bridge_refresh_contract")
        assert canary_bridge_refresh_row["status"] == "passed"
        assert canary_bridge_refresh_row["actual"]["durable_requested_bridge_refresh_count"] == 1
        assert canary_bridge_refresh_row["actual"]["read_only_preflight_allowed_count"] == 1
        assert canary_bridge_refresh_row["actual"]["bridge_refresh_required_count"] == 1
        assert canary_bridge_refresh_row["actual"]["bridge_reachable_count"] == 0
        assert canary_bridge_refresh_row["actual"]["read_only_result_refreshed_count"] == 0
        assert canary_bridge_refresh_row["actual"]["bridge_refresh_satisfied_count"] == 0
        assert canary_bridge_refresh_row["actual"]["canary_execution_allowed_after_refresh_count"] == 0
        assert canary_bridge_refresh_row["actual"]["durable_executor_may_open_after_refresh_count"] == 0
        assert canary_bridge_refresh_row["actual"]["live_save_or_delete_command_count"] == 0
        assert canary_bridge_refresh_row["actual"]["executor_gate_required_count"] == 1
        assert canary_bridge_refresh_row["actual"]["executor_gate_satisfied_count"] == 0
        assert canary_bridge_refresh_row["actual"]["executor_gate_execution_allowed_count"] == 0
        assert canary_bridge_refresh_row["actual"]["executor_gate_executor_may_open_count"] == 0
        live_evidence_refresh_row = find_row(report, "durable_live_evidence_refresh_contract")
        assert live_evidence_refresh_row["status"] == "passed"
        assert live_evidence_refresh_row["actual"]["durable_requested_live_evidence_refresh_count"] == 1
        assert live_evidence_refresh_row["actual"]["planner_live_report_present_count"] == 1
        assert live_evidence_refresh_row["actual"]["canary_live_evidence_present_count"] == 0
        assert live_evidence_refresh_row["actual"]["live_evidence_refresh_required_count"] == 1
        assert live_evidence_refresh_row["actual"]["read_only_result_refreshed_count"] == 0
        assert live_evidence_refresh_row["actual"]["live_evidence_refresh_satisfied_count"] == 0
        assert live_evidence_refresh_row["actual"]["unsafe_live_attempt_count"] == 0
        assert (
            live_evidence_refresh_row["actual"]["durable_executor_may_open_after_report_refresh_count"]
            == 0
        )
        assert live_evidence_refresh_row["actual"]["save_or_delete_allowed_count"] == 0
        executor_review_row = find_row(report, "durable_executor_implementation_review_contract")
        assert executor_review_row["status"] == "passed"
        assert executor_review_row["actual"]["durable_requested_executor_review_count"] == 1
        assert executor_review_row["actual"]["review_check_count"] == 6
        assert executor_review_row["actual"]["disabled_executor_boundary_review_passed_count"] == 1
        assert executor_review_row["actual"]["durable_live_implementation_approved_count"] == 0
        assert executor_review_row["actual"]["durable_executor_may_open_after_review_count"] == 0
        assert executor_review_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_review_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_review_row["actual"]["canary_execution_allowed_count"] == 0
        assert executor_review_row["actual"]["failing_check_count"] == 0
        command_allowlist_row = find_row(report, "durable_canary_command_allowlist_contract")
        assert command_allowlist_row["status"] == "passed"
        assert command_allowlist_row["actual"]["durable_requested_canary_command_allowlist_count"] == 1
        assert command_allowlist_row["actual"]["allowed_read_only_command_count"] == 1
        assert command_allowlist_row["actual"]["forbidden_command_count"] == 7
        assert command_allowlist_row["actual"]["executor_gate_matches_allowlist_count"] == 1
        assert command_allowlist_row["actual"]["authoring_commands_allowed_count"] == 0
        assert command_allowlist_row["actual"]["save_commands_allowed_count"] == 0
        assert command_allowlist_row["actual"]["delete_commands_allowed_count"] == 0
        assert command_allowlist_row["actual"]["rename_commands_allowed_count"] == 0
        assert command_allowlist_row["actual"]["cleanup_commands_allowed_count"] == 0
        assert command_allowlist_row["actual"]["canary_execution_allowed_count"] == 0
        assert command_allowlist_row["actual"]["durable_executor_may_open_from_allowlist_count"] == 0
        creation_boundary_row = find_row(report, "durable_canary_creation_boundary_contract")
        assert creation_boundary_row["status"] == "passed"
        assert creation_boundary_row["actual"]["durable_requested_canary_creation_boundary_count"] == 1
        assert creation_boundary_row["actual"]["canary_creation_boundary_defined_count"] == 1
        assert creation_boundary_row["actual"]["create_blueprint_allowed_count"] == 0
        assert creation_boundary_row["actual"]["save_command_allowed_count"] == 0
        assert creation_boundary_row["actual"]["delete_command_allowed_count"] == 0
        assert creation_boundary_row["actual"]["cleanup_command_allowed_count"] == 0
        assert creation_boundary_row["actual"]["live_canary_creation_allowed_count"] == 0
        assert creation_boundary_row["actual"]["durable_executor_may_open_for_creation_count"] == 0
        assert creation_boundary_row["actual"]["live_creation_command_count"] == 0
        assert creation_boundary_row["actual"]["live_save_or_delete_command_count"] == 0
        marker_proof_row = find_row(report, "durable_ownership_marker_write_readback_proof_contract")
        assert marker_proof_row["status"] == "passed"
        assert marker_proof_row["actual"]["durable_requested_ownership_marker_proof_count"] == 1
        assert marker_proof_row["actual"]["ownership_marker_policy_ready_count"] == 1
        assert marker_proof_row["actual"]["write_readback_proof_required_count"] == 1
        assert marker_proof_row["actual"]["marker_write_performed_count"] == 0
        assert marker_proof_row["actual"]["marker_readback_verified_count"] == 0
        assert marker_proof_row["actual"]["write_readback_proof_satisfied_count"] == 0
        assert marker_proof_row["actual"]["cleanup_allowed_after_marker_proof_count"] == 0
        assert marker_proof_row["actual"]["delete_allowed_after_marker_proof_count"] == 0
        assert marker_proof_row["actual"]["durable_executor_may_open_after_marker_proof_count"] == 0
        assert marker_proof_row["actual"]["live_write_command_count"] == 0
        assert marker_proof_row["actual"]["live_readback_command_count"] == 0
        assert marker_proof_row["actual"]["live_delete_command_count"] == 0
        cleanup_proof_row = find_row(report, "durable_rollback_cleanup_proof_contract")
        assert cleanup_proof_row["status"] == "passed"
        assert cleanup_proof_row["actual"]["durable_requested_rollback_cleanup_proof_count"] == 1
        assert cleanup_proof_row["actual"]["recovery_matrix_ready_count"] == 1
        assert cleanup_proof_row["actual"]["cleanup_proof_required_count"] == 1
        assert cleanup_proof_row["actual"]["ownership_marker_write_readback_satisfied_count"] == 0
        assert cleanup_proof_row["actual"]["cleanup_proof_satisfied_count"] == 0
        assert cleanup_proof_row["actual"]["cleanup_allowed_count"] == 0
        assert cleanup_proof_row["actual"]["delete_allowed_count"] == 0
        assert cleanup_proof_row["actual"]["delete_preexisting_asset_allowed_count"] == 0
        assert cleanup_proof_row["actual"]["delete_without_marker_allowed_count"] == 0
        assert cleanup_proof_row["actual"]["durable_executor_may_open_after_cleanup_proof_count"] == 0
        assert cleanup_proof_row["actual"]["live_cleanup_command_count"] == 0
        assert cleanup_proof_row["actual"]["live_delete_command_count"] == 0
        save_review_row = find_row(report, "durable_save_gate_final_enable_review_contract")
        assert save_review_row["status"] == "passed"
        assert save_review_row["actual"]["durable_requested_save_gate_final_review_count"] == 1
        assert save_review_row["actual"]["save_gate_final_review_complete_count"] == 1
        assert save_review_row["actual"]["missing_enable_prerequisite_count"] == 4
        assert save_review_row["actual"]["durable_save_enable_ready_count"] == 0
        assert save_review_row["actual"]["save_true_allowed_count"] == 0
        assert save_review_row["actual"]["save_asset_allowed_count"] == 0
        assert save_review_row["actual"]["compile_save_allowed_count"] == 0
        assert save_review_row["actual"]["delete_asset_allowed_count"] == 0
        assert save_review_row["actual"]["rename_asset_allowed_count"] == 0
        assert save_review_row["actual"]["durable_executor_may_open_after_save_review_count"] == 0
        assert save_review_row["actual"]["live_save_command_count"] == 0
        assert save_review_row["actual"]["live_delete_or_rename_command_count"] == 0
        rehearsal_row = find_row(report, "durable_canary_rehearsal_readiness_contract")
        assert rehearsal_row["status"] == "passed"
        assert rehearsal_row["actual"]["durable_requested_canary_rehearsal_readiness_count"] == 1
        assert rehearsal_row["actual"]["rehearsal_readiness_review_complete_count"] == 1
        assert rehearsal_row["actual"]["missing_rehearsal_prerequisite_count"] == 5
        assert rehearsal_row["actual"]["live_canary_rehearsal_ready_count"] == 0
        assert rehearsal_row["actual"]["live_canary_rehearsal_attempted_count"] == 0
        assert rehearsal_row["actual"]["canary_creation_attempted_count"] == 0
        assert rehearsal_row["actual"]["canary_save_attempted_count"] == 0
        assert rehearsal_row["actual"]["canary_cleanup_attempted_count"] == 0
        assert rehearsal_row["actual"]["durable_executor_may_open_for_rehearsal_count"] == 0
        assert rehearsal_row["actual"]["live_creation_command_count"] == 0
        assert rehearsal_row["actual"]["live_save_command_count"] == 0
        assert rehearsal_row["actual"]["live_cleanup_command_count"] == 0
        canary_recovery_row = find_row(report, "durable_canary_recovery_matrix")
        assert canary_recovery_row["status"] == "passed"
        assert canary_recovery_row["actual"]["durable_requested_canary_recovery_count"] == 1
        assert canary_recovery_row["actual"]["recovery_matrix_ready_count"] == 1
        assert canary_recovery_row["actual"]["scenario_count"] == 6
        assert canary_recovery_row["actual"]["cleanup_command_allowed_count"] == 0
        assert canary_recovery_row["actual"]["delete_command_allowed_count"] == 0
        assert canary_recovery_row["actual"]["live_cleanup_command_count"] == 0
        consolidation_row = find_row(report, "section_51_58_release_boundary_v2_consolidation")
        assert consolidation_row["status"] == "passed"
        assert consolidation_row["actual"]["durable_authoring_enabled"] is False
        assert consolidation_row["actual"]["section_51_58_blocking_contracts_ready"] is True
        assert consolidation_row["actual"]["durable_canary_recovery_cleanup_allowed_count"] == 0
        mvp_row = find_row(report, "section_60_mvp_decision_contract")
        assert mvp_row["status"] == "passed"
        assert mvp_row["actual"]["temporary_blueprint_authoring_mvp_ready"] is True
        assert mvp_row["actual"]["durable_blueprint_authoring_mvp_ready"] is False
        assert mvp_row["actual"]["durable_authoring_enabled"] is False
        assert find_row(report, "planner_driven_live_smoke_report")["status"] == "passed"
        canary_live_report_row = find_row(report, "durable_canary_read_only_live_preflight")
        assert canary_live_report_row["blocking"] is False
        if canary_live_report_row["status"] == "passed":
            assert canary_live_report_row["actual"]["passed_read_only_result_count"] == 1
        else:
            assert canary_live_report_row["actual"]["passed_read_only_result_count"] in (None, 0)
        assert find_row(report, "durable_read_only_live_preflight")["status"] == "passed"
        assert find_row(report, "project_filesystem_side_effect_boundary")["status"] == "passed"
        output_dir = Path(temp_dir) / "out"
        json_path, md_path = release_boundary.write_report(report, output_dir)
        assert json_path.exists()
        assert md_path.exists()
    print("BP authoring release boundary smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
