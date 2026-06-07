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
        fixture_root = Path(temp_dir)
        project_root = fixture_root / "CubelessStylized"
        project_root.mkdir()
        sibling_python = fixture_root / "unreal-mcp-cubeless" / "Python"
        sibling_python.mkdir(parents=True)
        (sibling_python / "unreal_mcp_server.py").write_text("# fixture\n", encoding="utf-8")
        (project_root / ".mcp.json").write_text(
            """{
  "mcpServers": {
    "unrealMCP": {
      "command": "uv",
      "args": [
        "--directory",
        "../unreal-mcp-cubeless/Python",
        "run",
        "--python",
        "3.11",
        "unreal_mcp_server.py"
      ]
    }
  }
}
""",
            encoding="utf-8",
        )
        (project_root / "Content" / "_MCP_Temp" / "PlannerDrivenSmoke").mkdir(parents=True)
        report = release_boundary.build_report(repo_root=repo_root, project_root=project_root)
        assert report["schema"] == release_boundary.REPORT_SCHEMA
        assert report["verdict"]["status"] == "passed"
        assert report["verdict"]["release_boundary_version"] == "section_86_v28"
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
        assert report["verdict"]["section_70_durable_release_decision_status"] == "passed"
        assert report["verdict"]["section_71_bridge_recovery_readiness_status"] == "passed"
        assert report["verdict"]["section_72_canary_read_only_retry_envelope_status"] == "passed"
        assert report["verdict"]["section_73_canary_read_only_retry_result_admission_status"] == "passed"
        assert report["verdict"]["section_74_canary_rehearsal_promotion_barrier_status"] == "passed"
        assert report["verdict"]["section_75_canary_rehearsal_execution_release_status"] == "passed"
        assert report["verdict"]["section_76_canary_live_runner_envelope_status"] == "passed"
        assert report["verdict"]["section_77_canary_live_runner_start_status"] == "passed"
        assert report["verdict"]["section_78_canary_live_command_dispatch_release_status"] == "passed"
        assert report["verdict"]["section_79_canary_live_command_execution_release_status"] == "passed"
        assert report["verdict"]["section_80_canary_live_command_execution_evidence_admission_status"] == "passed"
        assert report["verdict"]["section_81_canary_release_promotion_decision_status"] == "passed"
        assert report["verdict"]["section_82_canary_executor_activation_status"] == "passed"
        assert report["verdict"]["section_83_canary_executor_open_status"] == "passed"
        assert report["verdict"]["section_84_canary_authoring_enable_status"] == "passed"
        assert report["verdict"]["section_85_canary_authoring_command_status"] == "passed"
        assert report["verdict"]["section_86_canary_authoring_command_dispatch_status"] == "passed"
        assert report["verdict"]["final_durable_release_ready"] is False
        assert report["verdict"]["main_push_requested"] is False
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
        release_decision_row = find_row(report, "section_70_durable_release_decision_contract")
        assert release_decision_row["status"] == "passed"
        assert release_decision_row["actual"]["durable_requested_release_decision_count"] == 1
        assert release_decision_row["actual"]["temporary_blueprint_authoring_mvp_ready_count"] == 1
        assert release_decision_row["actual"]["durable_blueprint_authoring_mvp_ready_count"] == 0
        assert release_decision_row["actual"]["durable_authoring_enabled_count"] == 0
        assert release_decision_row["actual"]["section_61_69_safety_contracts_passed_count"] == 1
        assert release_decision_row["actual"]["durable_executor_enabled_count"] == 0
        assert release_decision_row["actual"]["durable_executor_executable_count"] == 0
        assert release_decision_row["actual"]["save_or_delete_commands_allowed_count"] == 0
        assert release_decision_row["actual"]["allowed_live_authoring_command_count"] == 0
        assert release_decision_row["actual"]["preflight_pass_count"] == 0
        assert release_decision_row["actual"]["final_durable_release_ready_count"] == 0
        bridge_recovery_row = find_row(report, "durable_bridge_recovery_readiness_contract")
        assert bridge_recovery_row["status"] == "passed"
        assert bridge_recovery_row["actual"]["durable_requested_bridge_recovery_readiness_count"] == 1
        assert bridge_recovery_row["actual"]["local_recovery_inputs_ready_count"] == 1
        assert bridge_recovery_row["actual"]["missing_recovery_input_count"] == 0
        assert bridge_recovery_row["actual"]["bridge_socket_probe_performed_count"] == 0
        assert bridge_recovery_row["actual"]["bridge_reachable_count"] == 0
        assert bridge_recovery_row["actual"]["read_only_canary_retry_allowed_after_recovery_count"] == 0
        assert bridge_recovery_row["actual"]["durable_executor_may_open_after_recovery_count"] == 0
        assert bridge_recovery_row["actual"]["durable_authoring_allowed_count"] == 0
        assert bridge_recovery_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert bridge_recovery_row["actual"]["live_authoring_command_count"] == 0
        assert bridge_recovery_row["actual"]["live_save_or_delete_command_count"] == 0
        retry_envelope_row = find_row(report, "durable_canary_read_only_retry_envelope_contract")
        assert retry_envelope_row["status"] == "passed"
        assert retry_envelope_row["actual"]["durable_requested_canary_read_only_retry_envelope_count"] == 1
        assert retry_envelope_row["actual"]["read_only_retry_envelope_defined_count"] == 1
        assert retry_envelope_row["actual"]["read_only_command_count"] == 1
        assert retry_envelope_row["actual"]["missing_retry_prerequisite_count"] == 2
        assert retry_envelope_row["actual"]["read_only_retry_prerequisites_satisfied_count"] == 0
        assert retry_envelope_row["actual"]["live_read_only_retry_allowed_count"] == 0
        assert retry_envelope_row["actual"]["live_read_only_retry_performed_count"] == 0
        assert retry_envelope_row["actual"]["live_read_only_result_recorded_count"] == 0
        assert retry_envelope_row["actual"]["canary_execution_allowed_after_retry_count"] == 0
        assert retry_envelope_row["actual"]["durable_executor_may_open_after_retry_count"] == 0
        assert retry_envelope_row["actual"]["authoring_command_allowed_count"] == 0
        assert retry_envelope_row["actual"]["save_or_delete_allowed_count"] == 0
        assert retry_envelope_row["actual"]["cleanup_allowed_count"] == 0
        assert retry_envelope_row["actual"]["live_authoring_command_count"] == 0
        assert retry_envelope_row["actual"]["live_save_or_delete_command_count"] == 0
        assert retry_envelope_row["actual"]["live_cleanup_command_count"] == 0
        result_admission_row = find_row(report, "durable_canary_read_only_retry_result_admission_contract")
        assert result_admission_row["status"] == "passed"
        assert (
            result_admission_row["actual"]["durable_requested_canary_read_only_retry_result_admission_count"]
            == 1
        )
        assert result_admission_row["actual"]["retry_result_admission_contract_defined_count"] == 1
        assert result_admission_row["actual"]["live_read_only_retry_result_present_count"] == 0
        assert result_admission_row["actual"]["result_schema_matches_count"] == 0
        assert result_admission_row["actual"]["explicit_live_read_only_retry_authorized_count"] == 0
        assert result_admission_row["actual"]["read_only_command_matches_count"] == 0
        assert result_admission_row["actual"]["result_status_passed_count"] == 0
        assert result_admission_row["actual"]["read_only_result_count"] == 0
        assert result_admission_row["actual"]["asset_exists_check_performed_count"] == 0
        assert result_admission_row["actual"]["read_only_result_admitted_count"] == 0
        assert result_admission_row["actual"]["missing_admission_prerequisite_count"] == 2
        assert result_admission_row["actual"]["rejected_retry_result_count"] == 0
        assert result_admission_row["actual"]["unsafe_retry_result_count"] == 0
        assert result_admission_row["actual"]["canary_execution_allowed_after_retry_result_count"] == 0
        assert result_admission_row["actual"]["durable_executor_may_open_after_retry_result_count"] == 0
        assert result_admission_row["actual"]["authoring_command_allowed_count"] == 0
        assert result_admission_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert result_admission_row["actual"]["cleanup_allowed_count"] == 0
        assert result_admission_row["actual"]["live_authoring_command_count"] == 0
        assert result_admission_row["actual"]["live_save_delete_rename_command_count"] == 0
        assert result_admission_row["actual"]["live_cleanup_command_count"] == 0
        assert result_admission_row["actual"]["live_canary_execution_command_count"] == 0
        promotion_barrier_row = find_row(report, "durable_canary_rehearsal_promotion_barrier_contract")
        assert promotion_barrier_row["status"] == "passed"
        assert (
            promotion_barrier_row["actual"]["durable_requested_canary_rehearsal_promotion_barrier_count"]
            == 1
        )
        assert promotion_barrier_row["actual"]["promotion_barrier_defined_count"] == 1
        assert promotion_barrier_row["actual"]["read_only_result_admitted_count"] == 0
        assert promotion_barrier_row["actual"]["rehearsal_readiness_review_complete_count"] == 1
        assert promotion_barrier_row["actual"]["promotion_inputs_satisfied_count"] == 0
        assert promotion_barrier_row["actual"]["promotion_execution_release_present_count"] == 0
        assert promotion_barrier_row["actual"]["missing_promotion_prerequisite_count"] == 7
        assert promotion_barrier_row["actual"]["canary_rehearsal_promotion_allowed_count"] == 0
        assert promotion_barrier_row["actual"]["live_canary_rehearsal_allowed_count"] == 0
        assert promotion_barrier_row["actual"]["live_canary_rehearsal_performed_count"] == 0
        assert promotion_barrier_row["actual"]["canary_creation_allowed_count"] == 0
        assert promotion_barrier_row["actual"]["canary_save_allowed_count"] == 0
        assert promotion_barrier_row["actual"]["canary_cleanup_allowed_count"] == 0
        assert promotion_barrier_row["actual"]["durable_executor_may_open_after_promotion_count"] == 0
        assert promotion_barrier_row["actual"]["durable_authoring_allowed_count"] == 0
        assert promotion_barrier_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert promotion_barrier_row["actual"]["cleanup_allowed_count"] == 0
        assert promotion_barrier_row["actual"]["live_creation_command_count"] == 0
        assert promotion_barrier_row["actual"]["live_save_command_count"] == 0
        assert promotion_barrier_row["actual"]["live_delete_rename_command_count"] == 0
        assert promotion_barrier_row["actual"]["live_cleanup_command_count"] == 0
        execution_release_row = find_row(report, "durable_canary_rehearsal_execution_release_contract")
        assert execution_release_row["status"] == "passed"
        assert execution_release_row["actual"]["durable_requested_canary_rehearsal_execution_release_count"] == 1
        assert execution_release_row["actual"]["execution_release_contract_defined_count"] == 1
        assert execution_release_row["actual"]["promotion_barrier_defined_count"] == 1
        assert execution_release_row["actual"]["promotion_inputs_satisfied_count"] == 0
        assert execution_release_row["actual"]["release_record_present_count"] == 0
        assert execution_release_row["actual"]["record_schema_matches_count"] == 0
        assert execution_release_row["actual"]["release_scope_matches_count"] == 0
        assert execution_release_row["actual"]["explicit_execution_authorized_count"] == 0
        assert execution_release_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert execution_release_row["actual"]["release_record_valid_count"] == 0
        assert execution_release_row["actual"]["release_record_rejected_count"] == 0
        assert execution_release_row["actual"]["unsafe_release_record_count"] == 0
        assert execution_release_row["actual"]["missing_release_prerequisite_count"] == 7
        assert execution_release_row["actual"]["live_canary_rehearsal_release_allowed_count"] == 0
        assert execution_release_row["actual"]["live_canary_rehearsal_execution_allowed_count"] == 0
        assert execution_release_row["actual"]["live_canary_rehearsal_performed_count"] == 0
        assert execution_release_row["actual"]["canary_creation_allowed_count"] == 0
        assert execution_release_row["actual"]["canary_save_allowed_count"] == 0
        assert execution_release_row["actual"]["canary_cleanup_allowed_count"] == 0
        assert execution_release_row["actual"]["durable_executor_may_open_after_execution_release_count"] == 0
        assert execution_release_row["actual"]["durable_authoring_allowed_count"] == 0
        assert execution_release_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert execution_release_row["actual"]["cleanup_allowed_count"] == 0
        assert execution_release_row["actual"]["live_creation_command_count"] == 0
        assert execution_release_row["actual"]["live_save_command_count"] == 0
        assert execution_release_row["actual"]["live_delete_rename_command_count"] == 0
        assert execution_release_row["actual"]["live_cleanup_command_count"] == 0
        runner_envelope_row = find_row(report, "durable_canary_live_runner_envelope_contract")
        assert runner_envelope_row["status"] == "passed"
        assert runner_envelope_row["actual"]["durable_requested_canary_live_runner_envelope_count"] == 1
        assert runner_envelope_row["actual"]["live_runner_envelope_defined_count"] == 1
        assert runner_envelope_row["actual"]["execution_release_contract_ready_count"] == 1
        assert runner_envelope_row["actual"]["execution_release_valid_count"] == 0
        assert runner_envelope_row["actual"]["live_runner_release_allowed_count"] == 0
        assert runner_envelope_row["actual"]["runner_plan_present_count"] == 0
        assert runner_envelope_row["actual"]["runner_plan_schema_matches_count"] == 0
        assert runner_envelope_row["actual"]["planned_command_count"] == 0
        assert runner_envelope_row["actual"]["forbidden_runner_command_count"] == 0
        assert runner_envelope_row["actual"]["unknown_runner_command_count"] == 0
        assert runner_envelope_row["actual"]["runner_plan_valid_count"] == 0
        assert runner_envelope_row["actual"]["runner_plan_rejected_count"] == 0
        assert runner_envelope_row["actual"]["missing_runner_prerequisite_count"] == 6
        assert runner_envelope_row["actual"]["live_runner_may_start_count"] == 0
        assert runner_envelope_row["actual"]["live_runner_started_count"] == 0
        assert runner_envelope_row["actual"]["live_command_plan_emitted_count"] == 0
        assert runner_envelope_row["actual"]["live_canary_rehearsal_performed_count"] == 0
        assert runner_envelope_row["actual"]["canary_creation_allowed_count"] == 0
        assert runner_envelope_row["actual"]["canary_save_allowed_count"] == 0
        assert runner_envelope_row["actual"]["canary_cleanup_allowed_count"] == 0
        assert runner_envelope_row["actual"]["durable_executor_may_open_after_runner_count"] == 0
        assert runner_envelope_row["actual"]["durable_authoring_allowed_count"] == 0
        assert runner_envelope_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert runner_envelope_row["actual"]["cleanup_allowed_count"] == 0
        assert runner_envelope_row["actual"]["live_creation_command_count"] == 0
        assert runner_envelope_row["actual"]["live_compile_command_count"] == 0
        assert runner_envelope_row["actual"]["live_marker_write_command_count"] == 0
        assert runner_envelope_row["actual"]["live_marker_readback_command_count"] == 0
        assert runner_envelope_row["actual"]["live_save_command_count"] == 0
        assert runner_envelope_row["actual"]["live_delete_rename_command_count"] == 0
        assert runner_envelope_row["actual"]["live_cleanup_command_count"] == 0
        runner_start_row = find_row(report, "durable_canary_live_runner_start_contract")
        assert runner_start_row["status"] == "passed"
        assert runner_start_row["actual"]["durable_requested_canary_live_runner_start_count"] == 1
        assert runner_start_row["actual"]["start_contract_defined_count"] == 1
        assert runner_start_row["actual"]["runner_envelope_ready_count"] == 1
        assert runner_start_row["actual"]["runner_plan_valid_count"] == 0
        assert runner_start_row["actual"]["runner_start_allowed_by_envelope_count"] == 0
        assert runner_start_row["actual"]["start_record_present_count"] == 0
        assert runner_start_row["actual"]["record_schema_matches_count"] == 0
        assert runner_start_row["actual"]["start_scope_matches_count"] == 0
        assert runner_start_row["actual"]["explicit_operator_start_authorized_count"] == 0
        assert runner_start_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert runner_start_row["actual"]["start_record_valid_count"] == 0
        assert runner_start_row["actual"]["start_record_rejected_count"] == 0
        assert runner_start_row["actual"]["unsafe_start_record_count"] == 0
        assert runner_start_row["actual"]["missing_start_prerequisite_count"] == 8
        assert runner_start_row["actual"]["live_runner_start_allowed_count"] == 0
        assert runner_start_row["actual"]["live_runner_started_count"] == 0
        assert runner_start_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert runner_start_row["actual"]["live_command_plan_emitted_count"] == 0
        assert runner_start_row["actual"]["live_canary_rehearsal_performed_count"] == 0
        assert runner_start_row["actual"]["canary_creation_allowed_count"] == 0
        assert runner_start_row["actual"]["canary_save_allowed_count"] == 0
        assert runner_start_row["actual"]["canary_cleanup_allowed_count"] == 0
        assert runner_start_row["actual"]["durable_executor_may_open_after_runner_start_count"] == 0
        assert runner_start_row["actual"]["durable_authoring_allowed_count"] == 0
        assert runner_start_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert runner_start_row["actual"]["cleanup_allowed_count"] == 0
        assert runner_start_row["actual"]["live_creation_command_count"] == 0
        assert runner_start_row["actual"]["live_compile_command_count"] == 0
        assert runner_start_row["actual"]["live_marker_write_command_count"] == 0
        assert runner_start_row["actual"]["live_marker_readback_command_count"] == 0
        assert runner_start_row["actual"]["live_save_command_count"] == 0
        assert runner_start_row["actual"]["live_delete_rename_command_count"] == 0
        assert runner_start_row["actual"]["live_cleanup_command_count"] == 0
        dispatch_release_row = find_row(report, "durable_canary_live_command_dispatch_release_contract")
        assert dispatch_release_row["status"] == "passed"
        assert (
            dispatch_release_row["actual"]["durable_requested_canary_live_command_dispatch_release_count"]
            == 1
        )
        assert dispatch_release_row["actual"]["dispatch_release_contract_defined_count"] == 1
        assert dispatch_release_row["actual"]["start_contract_ready_count"] == 1
        assert dispatch_release_row["actual"]["runner_plan_valid_count"] == 0
        assert dispatch_release_row["actual"]["start_record_valid_count"] == 0
        assert dispatch_release_row["actual"]["live_runner_started_count"] == 0
        assert dispatch_release_row["actual"]["dispatch_inputs_satisfied_count"] == 0
        assert dispatch_release_row["actual"]["dispatch_record_present_count"] == 0
        assert dispatch_release_row["actual"]["record_schema_matches_count"] == 0
        assert dispatch_release_row["actual"]["dispatch_scope_matches_count"] == 0
        assert dispatch_release_row["actual"]["explicit_dispatch_authorized_count"] == 0
        assert dispatch_release_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert dispatch_release_row["actual"]["dispatch_release_record_valid_count"] == 0
        assert dispatch_release_row["actual"]["dispatch_release_record_rejected_count"] == 0
        assert dispatch_release_row["actual"]["unsafe_dispatch_release_record_count"] == 0
        assert dispatch_release_row["actual"]["missing_dispatch_prerequisite_count"] == 9
        assert dispatch_release_row["actual"]["live_command_dispatch_release_allowed_count"] == 0
        assert dispatch_release_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert dispatch_release_row["actual"]["live_command_plan_emitted_count"] == 0
        assert dispatch_release_row["actual"]["live_canary_rehearsal_performed_count"] == 0
        assert dispatch_release_row["actual"]["canary_creation_allowed_count"] == 0
        assert dispatch_release_row["actual"]["canary_save_allowed_count"] == 0
        assert dispatch_release_row["actual"]["canary_cleanup_allowed_count"] == 0
        assert dispatch_release_row["actual"]["durable_executor_may_open_after_dispatch_release_count"] == 0
        assert dispatch_release_row["actual"]["durable_authoring_allowed_count"] == 0
        assert dispatch_release_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert dispatch_release_row["actual"]["cleanup_allowed_count"] == 0
        assert dispatch_release_row["actual"]["live_creation_command_count"] == 0
        assert dispatch_release_row["actual"]["live_compile_command_count"] == 0
        assert dispatch_release_row["actual"]["live_marker_write_command_count"] == 0
        assert dispatch_release_row["actual"]["live_marker_readback_command_count"] == 0
        assert dispatch_release_row["actual"]["live_save_command_count"] == 0
        assert dispatch_release_row["actual"]["live_delete_rename_command_count"] == 0
        assert dispatch_release_row["actual"]["live_cleanup_command_count"] == 0
        execution_release_row = find_row(report, "durable_canary_live_command_execution_release_contract")
        assert execution_release_row["status"] == "passed"
        assert (
            execution_release_row["actual"]["durable_requested_canary_live_command_execution_release_count"]
            == 1
        )
        assert execution_release_row["actual"]["execution_release_contract_defined_count"] == 1
        assert execution_release_row["actual"]["dispatch_release_contract_ready_count"] == 1
        assert execution_release_row["actual"]["dispatch_inputs_satisfied_count"] == 0
        assert execution_release_row["actual"]["dispatch_release_record_valid_count"] == 0
        assert execution_release_row["actual"]["execution_inputs_satisfied_count"] == 0
        assert execution_release_row["actual"]["execution_record_present_count"] == 0
        assert execution_release_row["actual"]["record_schema_matches_count"] == 0
        assert execution_release_row["actual"]["execution_scope_matches_count"] == 0
        assert execution_release_row["actual"]["explicit_execution_authorized_count"] == 0
        assert execution_release_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert execution_release_row["actual"]["execution_release_record_valid_count"] == 0
        assert execution_release_row["actual"]["execution_release_record_rejected_count"] == 0
        assert execution_release_row["actual"]["unsafe_execution_release_record_count"] == 0
        assert execution_release_row["actual"]["missing_execution_prerequisite_count"] == 8
        assert execution_release_row["actual"]["live_command_execution_release_allowed_count"] == 0
        assert execution_release_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert execution_release_row["actual"]["live_command_plan_emitted_count"] == 0
        assert execution_release_row["actual"]["live_command_execution_allowed_count"] == 0
        assert execution_release_row["actual"]["live_command_executed_count"] == 0
        assert execution_release_row["actual"]["live_canary_rehearsal_performed_count"] == 0
        assert execution_release_row["actual"]["canary_creation_allowed_count"] == 0
        assert execution_release_row["actual"]["canary_save_allowed_count"] == 0
        assert execution_release_row["actual"]["canary_cleanup_allowed_count"] == 0
        assert execution_release_row["actual"]["durable_executor_may_open_after_execution_release_count"] == 0
        assert execution_release_row["actual"]["durable_authoring_allowed_count"] == 0
        assert execution_release_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert execution_release_row["actual"]["cleanup_allowed_count"] == 0
        assert execution_release_row["actual"]["live_creation_command_count"] == 0
        assert execution_release_row["actual"]["live_compile_command_count"] == 0
        assert execution_release_row["actual"]["live_marker_write_command_count"] == 0
        assert execution_release_row["actual"]["live_marker_readback_command_count"] == 0
        assert execution_release_row["actual"]["live_save_command_count"] == 0
        assert execution_release_row["actual"]["live_delete_rename_command_count"] == 0
        assert execution_release_row["actual"]["live_cleanup_command_count"] == 0
        evidence_admission_row = find_row(
            report,
            "durable_canary_live_command_execution_evidence_admission_contract",
        )
        assert evidence_admission_row["status"] == "passed"
        assert (
            evidence_admission_row["actual"][
                "durable_requested_canary_live_command_execution_evidence_admission_count"
            ]
            == 1
        )
        assert evidence_admission_row["actual"]["evidence_admission_contract_defined_count"] == 1
        assert evidence_admission_row["actual"]["execution_release_contract_ready_count"] == 1
        assert evidence_admission_row["actual"]["execution_inputs_satisfied_count"] == 0
        assert evidence_admission_row["actual"]["execution_release_record_valid_count"] == 0
        assert evidence_admission_row["actual"]["section_79_live_command_executed_count"] == 0
        assert evidence_admission_row["actual"]["evidence_inputs_satisfied_count"] == 0
        assert evidence_admission_row["actual"]["evidence_record_present_count"] == 0
        assert evidence_admission_row["actual"]["record_schema_matches_count"] == 0
        assert evidence_admission_row["actual"]["evidence_scope_matches_count"] == 0
        assert evidence_admission_row["actual"]["explicit_evidence_admission_authorized_count"] == 0
        assert evidence_admission_row["actual"]["evidence_status_passed_count"] == 0
        assert evidence_admission_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert evidence_admission_row["actual"]["allowed_evidence_command_observed_count"] == 0
        assert evidence_admission_row["actual"]["no_forbidden_evidence_commands_count"] == 0
        assert evidence_admission_row["actual"]["execution_evidence_admitted_count"] == 0
        assert evidence_admission_row["actual"]["evidence_record_rejected_count"] == 0
        assert evidence_admission_row["actual"]["unsafe_evidence_record_count"] == 0
        assert evidence_admission_row["actual"]["missing_evidence_prerequisite_count"] == 12
        assert evidence_admission_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert evidence_admission_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        assert evidence_admission_row["actual"]["durable_promotion_allowed_count"] == 0
        assert evidence_admission_row["actual"]["durable_executor_may_open_after_evidence_admission_count"] == 0
        assert evidence_admission_row["actual"]["durable_authoring_allowed_count"] == 0
        assert evidence_admission_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert evidence_admission_row["actual"]["cleanup_allowed_count"] == 0
        assert evidence_admission_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert evidence_admission_row["actual"]["live_command_plan_emitted_count"] == 0
        assert evidence_admission_row["actual"]["live_command_execution_allowed_count"] == 0
        assert evidence_admission_row["actual"]["live_command_executed_count"] == 0
        assert evidence_admission_row["actual"]["reported_live_creation_command_count"] == 0
        assert evidence_admission_row["actual"]["reported_live_compile_command_count"] == 0
        assert evidence_admission_row["actual"]["reported_live_marker_write_command_count"] == 0
        assert evidence_admission_row["actual"]["reported_live_marker_readback_command_count"] == 0
        assert evidence_admission_row["actual"]["reported_live_save_command_count"] == 0
        assert evidence_admission_row["actual"]["reported_live_delete_rename_command_count"] == 0
        assert evidence_admission_row["actual"]["reported_live_cleanup_command_count"] == 0
        promotion_decision_row = find_row(report, "durable_canary_release_promotion_decision_contract")
        assert promotion_decision_row["status"] == "passed"
        assert promotion_decision_row["actual"]["durable_requested_canary_release_promotion_decision_count"] == 1
        assert promotion_decision_row["actual"]["promotion_decision_contract_defined_count"] == 1
        assert promotion_decision_row["actual"]["evidence_admission_contract_ready_count"] == 1
        assert promotion_decision_row["actual"]["execution_evidence_admitted_count"] == 0
        assert promotion_decision_row["actual"]["allowed_evidence_command_observed_count"] == 0
        assert promotion_decision_row["actual"]["no_forbidden_evidence_commands_count"] == 0
        assert promotion_decision_row["actual"]["evidence_ready_for_promotion_count"] == 0
        assert promotion_decision_row["actual"]["decision_record_present_count"] == 0
        assert promotion_decision_row["actual"]["record_schema_matches_count"] == 0
        assert promotion_decision_row["actual"]["promotion_scope_matches_count"] == 0
        assert promotion_decision_row["actual"]["explicit_promotion_authorized_count"] == 0
        assert promotion_decision_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert promotion_decision_row["actual"]["promotion_decision_record_valid_count"] == 0
        assert promotion_decision_row["actual"]["promotion_decision_record_rejected_count"] == 0
        assert promotion_decision_row["actual"]["unsafe_promotion_decision_record_count"] == 0
        assert promotion_decision_row["actual"]["missing_promotion_prerequisite_count"] == 9
        assert promotion_decision_row["actual"]["durable_release_promotion_allowed_count"] == 0
        assert promotion_decision_row["actual"]["durable_release_promoted_count"] == 0
        assert promotion_decision_row["actual"]["durable_executor_may_open_after_promotion_decision_count"] == 0
        assert promotion_decision_row["actual"]["durable_authoring_allowed_count"] == 0
        assert promotion_decision_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert promotion_decision_row["actual"]["cleanup_allowed_count"] == 0
        assert promotion_decision_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert promotion_decision_row["actual"]["live_command_plan_emitted_count"] == 0
        assert promotion_decision_row["actual"]["live_command_execution_allowed_count"] == 0
        assert promotion_decision_row["actual"]["live_command_executed_count"] == 0
        assert promotion_decision_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert promotion_decision_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        executor_activation_row = find_row(report, "durable_canary_executor_activation_contract")
        assert executor_activation_row["status"] == "passed"
        assert executor_activation_row["actual"]["durable_requested_canary_executor_activation_count"] == 1
        assert executor_activation_row["actual"]["activation_contract_defined_count"] == 1
        assert executor_activation_row["actual"]["promotion_decision_contract_ready_count"] == 1
        assert executor_activation_row["actual"]["evidence_ready_for_promotion_count"] == 0
        assert executor_activation_row["actual"]["promotion_decision_record_valid_count"] == 0
        assert executor_activation_row["actual"]["activation_inputs_satisfied_count"] == 0
        assert executor_activation_row["actual"]["activation_record_present_count"] == 0
        assert executor_activation_row["actual"]["record_schema_matches_count"] == 0
        assert executor_activation_row["actual"]["activation_scope_matches_count"] == 0
        assert executor_activation_row["actual"]["explicit_activation_authorized_count"] == 0
        assert executor_activation_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_activation_row["actual"]["activation_record_valid_count"] == 0
        assert executor_activation_row["actual"]["activation_record_rejected_count"] == 0
        assert executor_activation_row["actual"]["unsafe_activation_record_count"] == 0
        assert executor_activation_row["actual"]["missing_activation_prerequisite_count"] == 8
        assert executor_activation_row["actual"]["durable_executor_activation_allowed_count"] == 0
        assert executor_activation_row["actual"]["durable_executor_activated_count"] == 0
        assert executor_activation_row["actual"]["durable_executor_may_open_after_activation_count"] == 0
        assert executor_activation_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_activation_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_activation_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_activation_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert executor_activation_row["actual"]["live_command_plan_emitted_count"] == 0
        assert executor_activation_row["actual"]["live_command_execution_allowed_count"] == 0
        assert executor_activation_row["actual"]["live_command_executed_count"] == 0
        assert executor_activation_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert executor_activation_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        executor_open_row = find_row(report, "durable_canary_executor_open_contract")
        assert executor_open_row["status"] == "passed"
        assert executor_open_row["actual"]["durable_requested_canary_executor_open_count"] == 1
        assert executor_open_row["actual"]["open_contract_defined_count"] == 1
        assert executor_open_row["actual"]["activation_contract_ready_count"] == 1
        assert executor_open_row["actual"]["activation_inputs_satisfied_count"] == 0
        assert executor_open_row["actual"]["activation_record_valid_count"] == 0
        assert executor_open_row["actual"]["open_inputs_satisfied_count"] == 0
        assert executor_open_row["actual"]["open_record_present_count"] == 0
        assert executor_open_row["actual"]["record_schema_matches_count"] == 0
        assert executor_open_row["actual"]["open_scope_matches_count"] == 0
        assert executor_open_row["actual"]["explicit_open_authorized_count"] == 0
        assert executor_open_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_open_row["actual"]["open_record_valid_count"] == 0
        assert executor_open_row["actual"]["open_record_rejected_count"] == 0
        assert executor_open_row["actual"]["unsafe_open_record_count"] == 0
        assert executor_open_row["actual"]["missing_open_prerequisite_count"] == 8
        assert executor_open_row["actual"]["durable_executor_open_allowed_count"] == 0
        assert executor_open_row["actual"]["durable_executor_opened_count"] == 0
        assert executor_open_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_open_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_open_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_open_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert executor_open_row["actual"]["live_command_plan_emitted_count"] == 0
        assert executor_open_row["actual"]["live_command_execution_allowed_count"] == 0
        assert executor_open_row["actual"]["live_command_executed_count"] == 0
        assert executor_open_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert executor_open_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        authoring_enable_row = find_row(report, "durable_canary_authoring_enable_contract")
        assert authoring_enable_row["status"] == "passed"
        assert authoring_enable_row["actual"]["durable_requested_canary_authoring_enable_count"] == 1
        assert authoring_enable_row["actual"]["authoring_enable_contract_defined_count"] == 1
        assert authoring_enable_row["actual"]["executor_open_contract_ready_count"] == 1
        assert authoring_enable_row["actual"]["open_inputs_satisfied_count"] == 0
        assert authoring_enable_row["actual"]["open_record_valid_count"] == 0
        assert authoring_enable_row["actual"]["authoring_enable_inputs_satisfied_count"] == 0
        assert authoring_enable_row["actual"]["authoring_enable_record_present_count"] == 0
        assert authoring_enable_row["actual"]["record_schema_matches_count"] == 0
        assert authoring_enable_row["actual"]["enable_scope_matches_count"] == 0
        assert authoring_enable_row["actual"]["explicit_authoring_enable_authorized_count"] == 0
        assert authoring_enable_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert authoring_enable_row["actual"]["target_package_allowlist_reconfirmed_count"] == 0
        assert authoring_enable_row["actual"]["overwrite_rename_decision_reconfirmed_count"] == 0
        assert authoring_enable_row["actual"]["rollback_readiness_reconfirmed_count"] == 0
        assert authoring_enable_row["actual"]["ownership_marker_reconfirmed_count"] == 0
        assert authoring_enable_row["actual"]["authoring_enable_record_valid_count"] == 0
        assert authoring_enable_row["actual"]["authoring_enable_record_rejected_count"] == 0
        assert authoring_enable_row["actual"]["unsafe_authoring_enable_record_count"] == 0
        assert authoring_enable_row["actual"]["missing_authoring_enable_prerequisite_count"] == 12
        assert authoring_enable_row["actual"]["durable_authoring_enable_allowed_count"] == 0
        assert authoring_enable_row["actual"]["durable_authoring_enabled_count"] == 0
        assert authoring_enable_row["actual"]["durable_authoring_allowed_count"] == 0
        assert authoring_enable_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert authoring_enable_row["actual"]["cleanup_allowed_count"] == 0
        assert authoring_enable_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert authoring_enable_row["actual"]["live_command_plan_emitted_count"] == 0
        assert authoring_enable_row["actual"]["live_command_execution_allowed_count"] == 0
        assert authoring_enable_row["actual"]["live_command_executed_count"] == 0
        assert authoring_enable_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert authoring_enable_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        authoring_command_row = find_row(report, "durable_canary_authoring_command_contract")
        assert authoring_command_row["status"] == "passed"
        assert authoring_command_row["actual"]["durable_requested_canary_authoring_command_count"] == 1
        assert authoring_command_row["actual"]["authoring_command_contract_defined_count"] == 1
        assert authoring_command_row["actual"]["authoring_enable_contract_ready_count"] == 1
        assert authoring_command_row["actual"]["authoring_enable_inputs_satisfied_count"] == 0
        assert authoring_command_row["actual"]["authoring_enable_record_valid_count"] == 0
        assert authoring_command_row["actual"]["target_package_allowlist_reconfirmed_count"] == 0
        assert authoring_command_row["actual"]["overwrite_rename_decision_reconfirmed_count"] == 0
        assert authoring_command_row["actual"]["rollback_readiness_reconfirmed_count"] == 0
        assert authoring_command_row["actual"]["ownership_marker_reconfirmed_count"] == 0
        assert authoring_command_row["actual"]["authoring_command_inputs_satisfied_count"] == 0
        assert authoring_command_row["actual"]["authoring_command_record_present_count"] == 0
        assert authoring_command_row["actual"]["record_schema_matches_count"] == 0
        assert authoring_command_row["actual"]["command_scope_matches_count"] == 0
        assert authoring_command_row["actual"]["explicit_authoring_command_authorized_count"] == 0
        assert authoring_command_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert authoring_command_row["actual"]["planned_authoring_command_count"] == 0
        assert authoring_command_row["actual"]["allowed_authoring_command_count"] == 0
        assert authoring_command_row["actual"]["forbidden_authoring_command_count"] == 0
        assert authoring_command_row["actual"]["unknown_authoring_command_count"] == 0
        assert authoring_command_row["actual"]["authoring_command_record_valid_count"] == 0
        assert authoring_command_row["actual"]["authoring_command_record_rejected_count"] == 0
        assert authoring_command_row["actual"]["unsafe_authoring_command_record_count"] == 0
        assert authoring_command_row["actual"]["missing_authoring_command_prerequisite_count"] == 13
        assert authoring_command_row["actual"]["durable_authoring_command_allowed_count"] == 0
        assert authoring_command_row["actual"]["durable_authoring_command_dispatched_count"] == 0
        assert authoring_command_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert authoring_command_row["actual"]["durable_authoring_enabled_count"] == 0
        assert authoring_command_row["actual"]["durable_authoring_allowed_count"] == 0
        assert authoring_command_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert authoring_command_row["actual"]["cleanup_allowed_count"] == 0
        assert authoring_command_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert authoring_command_row["actual"]["live_command_plan_emitted_count"] == 0
        assert authoring_command_row["actual"]["live_command_execution_allowed_count"] == 0
        assert authoring_command_row["actual"]["live_command_executed_count"] == 0
        assert authoring_command_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert authoring_command_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        dispatch_row = find_row(report, "durable_canary_authoring_command_dispatch_contract")
        assert dispatch_row["status"] == "passed"
        assert dispatch_row["actual"]["durable_requested_canary_authoring_command_dispatch_count"] == 1
        assert dispatch_row["actual"]["dispatch_contract_defined_count"] == 1
        assert dispatch_row["actual"]["authoring_command_contract_ready_count"] == 1
        assert dispatch_row["actual"]["authoring_command_inputs_satisfied_count"] == 0
        assert dispatch_row["actual"]["authoring_command_record_valid_count"] == 0
        assert dispatch_row["actual"]["planned_authoring_commands_present_count"] == 0
        assert dispatch_row["actual"]["allowed_authoring_commands_present_count"] == 0
        assert dispatch_row["actual"]["dispatch_inputs_satisfied_count"] == 0
        assert dispatch_row["actual"]["dispatch_record_present_count"] == 0
        assert dispatch_row["actual"]["record_schema_matches_count"] == 0
        assert dispatch_row["actual"]["dispatch_scope_matches_count"] == 0
        assert dispatch_row["actual"]["explicit_dispatch_authorized_count"] == 0
        assert dispatch_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert dispatch_row["actual"]["dispatch_record_valid_count"] == 0
        assert dispatch_row["actual"]["dispatch_record_rejected_count"] == 0
        assert dispatch_row["actual"]["unsafe_dispatch_record_count"] == 0
        assert dispatch_row["actual"]["missing_dispatch_prerequisite_count"] == 10
        assert dispatch_row["actual"]["durable_authoring_command_dispatch_allowed_count"] == 0
        assert dispatch_row["actual"]["durable_authoring_command_dispatched_count"] == 0
        assert dispatch_row["actual"]["durable_authoring_command_execution_allowed_count"] == 0
        assert dispatch_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert dispatch_row["actual"]["durable_authoring_enabled_count"] == 0
        assert dispatch_row["actual"]["durable_authoring_allowed_count"] == 0
        assert dispatch_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert dispatch_row["actual"]["cleanup_allowed_count"] == 0
        assert dispatch_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert dispatch_row["actual"]["live_command_plan_emitted_count"] == 0
        assert dispatch_row["actual"]["live_command_execution_allowed_count"] == 0
        assert dispatch_row["actual"]["live_command_executed_count"] == 0
        assert dispatch_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert dispatch_row["actual"]["reported_forbidden_evidence_command_count"] == 0
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
