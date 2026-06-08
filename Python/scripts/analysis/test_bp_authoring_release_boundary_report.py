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
        assert report["verdict"]["release_boundary_version"] == "section_179_v121"
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
        assert report["verdict"]["section_87_canary_authoring_command_execution_status"] == "passed"
        assert report["verdict"]["section_88_canary_authoring_command_execution_evidence_status"] == "passed"
        assert report["verdict"]["section_89_canary_authoring_command_completion_decision_status"] == "passed"
        assert report["verdict"]["section_90_canary_authoring_command_completion_application_status"] == "passed"
        assert report["verdict"]["section_91_canary_authoring_command_completion_result_status"] == "passed"
        assert report["verdict"]["section_92_canary_authoring_command_result_readback_status"] == "passed"
        assert report["verdict"]["section_93_canary_authoring_final_no_save_release_status"] == "passed"
        assert report["verdict"]["section_94_canary_authoring_final_release_readiness_status"] == "passed"
        assert report["verdict"]["section_95_durable_executor_implementation_review_status"] == "passed"
        assert report["verdict"]["section_96_durable_executor_implementation_plan_status"] == "passed"
        assert report["verdict"]["section_97_durable_executor_change_design_status"] == "passed"
        assert report["verdict"]["section_98_durable_executor_code_change_approval_status"] == "passed"
        assert report["verdict"]["section_99_durable_executor_code_patch_plan_status"] == "passed"
        assert report["verdict"]["section_100_durable_executor_code_patch_review_status"] == "passed"
        assert report["verdict"]["section_101_durable_executor_code_patch_application_status"] == "passed"
        assert report["verdict"]["section_102_durable_executor_code_patch_execution_status"] == "passed"
        assert report["verdict"]["section_103_durable_executor_code_patch_result_status"] == "passed"
        assert report["verdict"]["section_104_durable_executor_code_patch_result_readback_status"] == "passed"
        assert report["verdict"]["section_105_durable_executor_code_patch_final_no_save_release_status"] == "passed"
        assert report["verdict"]["section_106_durable_executor_code_patch_final_release_readiness_status"] == "passed"
        assert report["verdict"]["section_107_durable_executor_code_patch_release_review_status"] == "passed"
        assert report["verdict"]["section_108_durable_executor_code_patch_release_decision_status"] == "passed"
        assert report["verdict"]["section_109_durable_executor_release_promotion_barrier_status"] == "passed"
        assert report["verdict"]["section_110_durable_executor_activation_readiness_status"] == "passed"
        assert report["verdict"]["section_111_durable_executor_open_status"] == "passed"
        assert report["verdict"]["section_112_durable_executor_authoring_enable_status"] == "passed"
        assert report["verdict"]["section_113_durable_executor_authoring_command_status"] == "passed"
        assert report["verdict"]["section_114_durable_executor_authoring_command_dispatch_status"] == "passed"
        assert report["verdict"]["section_115_durable_executor_authoring_command_execution_status"] == "passed"
        assert report["verdict"]["section_116_durable_executor_authoring_command_execution_evidence_status"] == "passed"
        assert report["verdict"]["section_117_durable_executor_authoring_command_completion_decision_status"] == "passed"
        assert report["verdict"]["section_118_durable_executor_authoring_command_completion_application_status"] == "passed"
        assert report["verdict"]["section_119_durable_executor_authoring_command_completion_result_status"] == "passed"
        assert report["verdict"]["section_120_durable_executor_authoring_command_result_readback_status"] == "passed"
        assert report["verdict"]["section_121_durable_executor_authoring_final_no_save_release_status"] == "passed"
        assert report["verdict"]["section_122_durable_executor_authoring_final_release_readiness_status"] == "passed"
        assert report["verdict"]["section_123_durable_executor_authoring_release_review_status"] == "passed"
        assert report["verdict"]["section_124_durable_executor_authoring_release_decision_status"] == "passed"
        assert report["verdict"]["section_125_durable_executor_authoring_release_promotion_barrier_status"] == "passed"
        assert report["verdict"]["section_126_durable_executor_authoring_activation_readiness_status"] == "passed"
        assert report["verdict"]["section_127_durable_executor_authoring_open_status"] == "passed"
        assert report["verdict"]["section_128_durable_executor_authoring_enable_after_open_status"] == "passed"
        assert report["verdict"]["section_129_durable_executor_authoring_command_after_enable_status"] == "passed"
        assert (
            report["verdict"][
                "section_130_durable_executor_authoring_command_dispatch_after_command_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_131_durable_executor_authoring_command_execution_after_dispatch_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_132_durable_executor_authoring_command_execution_evidence_after_execution_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_133_durable_executor_authoring_command_completion_decision_after_evidence_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_134_durable_executor_authoring_command_completion_application_after_decision_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_135_durable_executor_authoring_command_completion_result_after_application_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_136_durable_executor_authoring_command_result_readback_after_result_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_137_durable_executor_authoring_final_no_save_release_after_readback_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_138_durable_executor_authoring_final_release_readiness_after_no_save_release_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_139_durable_executor_authoring_release_review_after_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_140_durable_executor_authoring_release_decision_after_review_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_141_durable_executor_authoring_release_promotion_barrier_after_decision_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_142_durable_executor_authoring_activation_readiness_after_promotion_barrier_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_143_durable_executor_authoring_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_144_durable_executor_authoring_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_145_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_146_durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_147_durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_148_durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_149_durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_150_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_151_durable_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_152_durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_153_durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_154_durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_155_durable_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_156_durable_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_157_durable_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_158_durable_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_159_durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_160_durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_161_durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_162_durable_executor_authoring_command_request_dry_run_route_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_163_durable_executor_authoring_command_dispatch_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_164_durable_executor_authoring_command_dispatch_evidence_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_165_durable_executor_authoring_command_execution_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_166_durable_executor_authoring_command_execution_evidence_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_167_durable_executor_authoring_command_completion_decision_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_168_durable_executor_authoring_command_completion_application_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_169_durable_executor_authoring_command_completion_result_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_170_durable_executor_authoring_command_result_readback_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_171_durable_executor_authoring_final_no_save_release_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_172_durable_executor_authoring_final_release_readiness_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_173_durable_executor_authoring_release_review_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_174_durable_executor_authoring_release_decision_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_175_durable_executor_authoring_release_promotion_barrier_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_176_durable_executor_authoring_activation_readiness_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_177_durable_executor_authoring_open_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_178_durable_executor_authoring_open_promotion_barrier_dry_run_status"
            ]
            == "passed"
        )
        assert (
            report["verdict"][
                "section_179_durable_executor_authoring_command_path_dry_run_status"
            ]
            == "passed"
        )
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
        execution_row = find_row(report, "durable_canary_authoring_command_execution_contract")
        assert execution_row["status"] == "passed"
        assert execution_row["actual"]["durable_requested_canary_authoring_command_execution_count"] == 1
        assert execution_row["actual"]["execution_contract_defined_count"] == 1
        assert execution_row["actual"]["dispatch_contract_ready_count"] == 1
        assert execution_row["actual"]["dispatch_inputs_satisfied_count"] == 0
        assert execution_row["actual"]["dispatch_record_valid_count"] == 0
        assert execution_row["actual"]["planned_authoring_commands_present_count"] == 0
        assert execution_row["actual"]["allowed_authoring_commands_present_count"] == 0
        assert execution_row["actual"]["execution_inputs_satisfied_count"] == 0
        assert execution_row["actual"]["execution_record_present_count"] == 0
        assert execution_row["actual"]["record_schema_matches_count"] == 0
        assert execution_row["actual"]["execution_scope_matches_count"] == 0
        assert execution_row["actual"]["explicit_execution_authorized_count"] == 0
        assert execution_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert execution_row["actual"]["execution_record_valid_count"] == 0
        assert execution_row["actual"]["execution_record_rejected_count"] == 0
        assert execution_row["actual"]["unsafe_execution_record_count"] == 0
        assert execution_row["actual"]["missing_execution_prerequisite_count"] == 10
        assert execution_row["actual"]["durable_authoring_command_dispatch_allowed_count"] == 0
        assert execution_row["actual"]["durable_authoring_command_dispatched_count"] == 0
        assert execution_row["actual"]["durable_authoring_command_execution_allowed_count"] == 0
        assert execution_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert execution_row["actual"]["durable_authoring_enabled_count"] == 0
        assert execution_row["actual"]["durable_authoring_allowed_count"] == 0
        assert execution_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert execution_row["actual"]["cleanup_allowed_count"] == 0
        assert execution_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert execution_row["actual"]["live_command_plan_emitted_count"] == 0
        assert execution_row["actual"]["live_command_execution_allowed_count"] == 0
        assert execution_row["actual"]["live_command_executed_count"] == 0
        assert execution_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert execution_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        evidence_row = find_row(report, "durable_canary_authoring_command_execution_evidence_contract")
        assert evidence_row["status"] == "passed"
        assert evidence_row["actual"]["durable_requested_canary_authoring_command_execution_evidence_count"] == 1
        assert evidence_row["actual"]["evidence_contract_defined_count"] == 1
        assert evidence_row["actual"]["execution_contract_ready_count"] == 1
        assert evidence_row["actual"]["execution_inputs_satisfied_count"] == 0
        assert evidence_row["actual"]["execution_record_valid_count"] == 0
        assert evidence_row["actual"]["planned_authoring_commands_present_count"] == 0
        assert evidence_row["actual"]["allowed_authoring_commands_present_count"] == 0
        assert evidence_row["actual"]["evidence_inputs_satisfied_count"] == 0
        assert evidence_row["actual"]["evidence_record_present_count"] == 0
        assert evidence_row["actual"]["record_schema_matches_count"] == 0
        assert evidence_row["actual"]["evidence_scope_matches_count"] == 0
        assert evidence_row["actual"]["explicit_evidence_authorized_count"] == 0
        assert evidence_row["actual"]["evidence_status_passed_count"] == 0
        assert evidence_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert evidence_row["actual"]["allowed_evidence_command_observed_count"] == 0
        assert evidence_row["actual"]["no_forbidden_evidence_commands_count"] == 0
        assert evidence_row["actual"]["authoring_command_execution_evidence_admitted_count"] == 0
        assert evidence_row["actual"]["evidence_record_rejected_count"] == 0
        assert evidence_row["actual"]["unsafe_evidence_record_count"] == 0
        assert evidence_row["actual"]["missing_evidence_prerequisite_count"] == 13
        assert evidence_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert evidence_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        assert evidence_row["actual"]["durable_authoring_command_dispatch_allowed_count"] == 0
        assert evidence_row["actual"]["durable_authoring_command_dispatched_count"] == 0
        assert evidence_row["actual"]["durable_authoring_command_execution_allowed_count"] == 0
        assert evidence_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert evidence_row["actual"]["durable_promotion_allowed_count"] == 0
        assert evidence_row["actual"]["durable_authoring_enabled_count"] == 0
        assert evidence_row["actual"]["durable_authoring_allowed_count"] == 0
        assert evidence_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert evidence_row["actual"]["cleanup_allowed_count"] == 0
        assert evidence_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert evidence_row["actual"]["live_command_plan_emitted_count"] == 0
        assert evidence_row["actual"]["live_command_execution_allowed_count"] == 0
        assert evidence_row["actual"]["live_command_executed_count"] == 0
        assert evidence_row["actual"]["reported_authoring_create_command_count"] == 0
        assert evidence_row["actual"]["reported_authoring_compile_command_count"] == 0
        assert evidence_row["actual"]["reported_authoring_marker_write_command_count"] == 0
        assert evidence_row["actual"]["reported_authoring_marker_readback_command_count"] == 0
        assert evidence_row["actual"]["reported_authoring_read_only_exists_check_command_count"] == 0
        assert evidence_row["actual"]["reported_authoring_save_command_count"] == 0
        assert evidence_row["actual"]["reported_authoring_delete_rename_command_count"] == 0
        assert evidence_row["actual"]["reported_authoring_cleanup_command_count"] == 0
        assert evidence_row["actual"]["reported_authoring_duplicate_replace_command_count"] == 0
        assert evidence_row["actual"]["reported_authoring_live_dispatch_execution_command_count"] == 0
        completion_row = find_row(report, "durable_canary_authoring_command_completion_decision_contract")
        assert completion_row["status"] == "passed"
        assert completion_row["actual"]["durable_requested_canary_authoring_command_completion_decision_count"] == 1
        assert completion_row["actual"]["completion_decision_contract_defined_count"] == 1
        assert completion_row["actual"]["evidence_contract_ready_count"] == 1
        assert completion_row["actual"]["authoring_command_execution_evidence_admitted_count"] == 0
        assert completion_row["actual"]["allowed_evidence_command_observed_count"] == 0
        assert completion_row["actual"]["no_forbidden_evidence_commands_count"] == 0
        assert completion_row["actual"]["evidence_ready_for_completion_count"] == 0
        assert completion_row["actual"]["decision_record_present_count"] == 0
        assert completion_row["actual"]["record_schema_matches_count"] == 0
        assert completion_row["actual"]["completion_scope_matches_count"] == 0
        assert completion_row["actual"]["explicit_completion_authorized_count"] == 0
        assert completion_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert completion_row["actual"]["completion_decision_record_valid_count"] == 0
        assert completion_row["actual"]["completion_decision_record_rejected_count"] == 0
        assert completion_row["actual"]["unsafe_completion_decision_record_count"] == 0
        assert completion_row["actual"]["missing_completion_prerequisite_count"] == 9
        assert completion_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert completion_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        assert completion_row["actual"]["durable_authoring_command_completion_allowed_count"] == 0
        assert completion_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert completion_row["actual"]["durable_authoring_command_dispatch_allowed_count"] == 0
        assert completion_row["actual"]["durable_authoring_command_dispatched_count"] == 0
        assert completion_row["actual"]["durable_authoring_command_execution_allowed_count"] == 0
        assert completion_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert completion_row["actual"]["durable_promotion_allowed_count"] == 0
        assert completion_row["actual"]["durable_authoring_enabled_count"] == 0
        assert completion_row["actual"]["durable_authoring_allowed_count"] == 0
        assert completion_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert completion_row["actual"]["cleanup_allowed_count"] == 0
        assert completion_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert completion_row["actual"]["live_command_plan_emitted_count"] == 0
        assert completion_row["actual"]["live_command_execution_allowed_count"] == 0
        assert completion_row["actual"]["live_command_executed_count"] == 0
        application_row = find_row(report, "durable_canary_authoring_command_completion_application_contract")
        assert application_row["status"] == "passed"
        assert application_row["actual"]["durable_requested_canary_authoring_command_completion_application_count"] == 1
        assert application_row["actual"]["application_contract_defined_count"] == 1
        assert application_row["actual"]["completion_decision_contract_ready_count"] == 1
        assert application_row["actual"]["evidence_ready_for_completion_count"] == 0
        assert application_row["actual"]["completion_decision_record_valid_count"] == 0
        assert application_row["actual"]["application_inputs_satisfied_count"] == 0
        assert application_row["actual"]["application_record_present_count"] == 0
        assert application_row["actual"]["record_schema_matches_count"] == 0
        assert application_row["actual"]["application_scope_matches_count"] == 0
        assert application_row["actual"]["explicit_application_authorized_count"] == 0
        assert application_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert application_row["actual"]["application_record_valid_count"] == 0
        assert application_row["actual"]["application_record_rejected_count"] == 0
        assert application_row["actual"]["unsafe_application_record_count"] == 0
        assert application_row["actual"]["missing_application_prerequisite_count"] == 8
        assert application_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert application_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        assert application_row["actual"]["durable_authoring_command_completion_allowed_count"] == 0
        assert application_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert application_row["actual"]["durable_authoring_command_application_allowed_count"] == 0
        assert application_row["actual"]["durable_authoring_command_application_applied_count"] == 0
        assert application_row["actual"]["asset_write_allowed_count"] == 0
        assert application_row["actual"]["asset_write_performed_count"] == 0
        assert application_row["actual"]["package_dirty_marked_count"] == 0
        assert application_row["actual"]["durable_authoring_command_dispatch_allowed_count"] == 0
        assert application_row["actual"]["durable_authoring_command_dispatched_count"] == 0
        assert application_row["actual"]["durable_authoring_command_execution_allowed_count"] == 0
        assert application_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert application_row["actual"]["durable_promotion_allowed_count"] == 0
        assert application_row["actual"]["durable_authoring_enabled_count"] == 0
        assert application_row["actual"]["durable_authoring_allowed_count"] == 0
        assert application_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert application_row["actual"]["cleanup_allowed_count"] == 0
        assert application_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert application_row["actual"]["live_command_plan_emitted_count"] == 0
        assert application_row["actual"]["live_command_execution_allowed_count"] == 0
        assert application_row["actual"]["live_command_executed_count"] == 0
        result_row = find_row(report, "durable_canary_authoring_command_completion_result_contract")
        assert result_row["status"] == "passed"
        assert result_row["actual"]["durable_requested_canary_authoring_command_completion_result_count"] == 1
        assert result_row["actual"]["result_contract_defined_count"] == 1
        assert result_row["actual"]["application_contract_ready_count"] == 1
        assert result_row["actual"]["application_inputs_satisfied_count"] == 0
        assert result_row["actual"]["application_record_valid_count"] == 0
        assert result_row["actual"]["result_inputs_satisfied_count"] == 0
        assert result_row["actual"]["result_record_present_count"] == 0
        assert result_row["actual"]["record_schema_matches_count"] == 0
        assert result_row["actual"]["result_scope_matches_count"] == 0
        assert result_row["actual"]["explicit_result_authorized_count"] == 0
        assert result_row["actual"]["result_status_passed_count"] == 0
        assert result_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert result_row["actual"]["allowed_result_observed_count"] == 0
        assert result_row["actual"]["no_forbidden_results_count"] == 0
        assert result_row["actual"]["result_record_valid_count"] == 0
        assert result_row["actual"]["result_record_rejected_count"] == 0
        assert result_row["actual"]["unsafe_result_record_count"] == 0
        assert result_row["actual"]["missing_result_prerequisite_count"] == 11
        assert result_row["actual"]["reported_allowed_result_count"] == 0
        assert result_row["actual"]["reported_forbidden_result_count"] == 0
        assert result_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert result_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        assert result_row["actual"]["durable_authoring_command_completion_result_accepted_count"] == 0
        assert result_row["actual"]["durable_authoring_command_completion_allowed_count"] == 0
        assert result_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert result_row["actual"]["durable_authoring_command_application_allowed_count"] == 0
        assert result_row["actual"]["durable_authoring_command_application_applied_count"] == 0
        assert result_row["actual"]["asset_write_allowed_count"] == 0
        assert result_row["actual"]["asset_write_performed_count"] == 0
        assert result_row["actual"]["package_dirty_marked_count"] == 0
        assert result_row["actual"]["durable_authoring_enabled_count"] == 0
        assert result_row["actual"]["durable_authoring_allowed_count"] == 0
        assert result_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert result_row["actual"]["cleanup_allowed_count"] == 0
        assert result_row["actual"]["live_command_dispatch_allowed_count"] == 0
        assert result_row["actual"]["live_command_plan_emitted_count"] == 0
        assert result_row["actual"]["live_command_execution_allowed_count"] == 0
        assert result_row["actual"]["live_command_executed_count"] == 0
        assert result_row["actual"]["reported_completion_noop_result_count"] == 0
        assert result_row["actual"]["reported_application_validation_result_count"] == 0
        assert result_row["actual"]["reported_completion_completed_result_count"] == 0
        assert result_row["actual"]["reported_asset_write_result_count"] == 0
        assert result_row["actual"]["reported_package_dirty_result_count"] == 0
        assert result_row["actual"]["reported_save_result_count"] == 0
        assert result_row["actual"]["reported_delete_rename_result_count"] == 0
        assert result_row["actual"]["reported_cleanup_result_count"] == 0
        readback_row = find_row(report, "durable_canary_authoring_command_result_readback_contract")
        assert readback_row["status"] == "passed"
        assert readback_row["actual"]["durable_requested_canary_authoring_command_result_readback_count"] == 1
        assert readback_row["actual"]["readback_contract_defined_count"] == 1
        assert readback_row["actual"]["result_contract_ready_count"] == 1
        assert readback_row["actual"]["result_inputs_satisfied_count"] == 0
        assert readback_row["actual"]["result_record_valid_count"] == 0
        assert readback_row["actual"]["allowed_result_observed_count"] == 0
        assert readback_row["actual"]["no_forbidden_results_count"] == 0
        assert readback_row["actual"]["readback_inputs_satisfied_count"] == 0
        assert readback_row["actual"]["readback_record_present_count"] == 0
        assert readback_row["actual"]["record_schema_matches_count"] == 0
        assert readback_row["actual"]["readback_scope_matches_count"] == 0
        assert readback_row["actual"]["explicit_readback_authorized_count"] == 0
        assert readback_row["actual"]["readback_status_passed_count"] == 0
        assert readback_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert readback_row["actual"]["allowed_readback_observed_count"] == 0
        assert readback_row["actual"]["no_forbidden_readbacks_count"] == 0
        assert readback_row["actual"]["readback_record_valid_count"] == 0
        assert readback_row["actual"]["readback_record_rejected_count"] == 0
        assert readback_row["actual"]["unsafe_readback_record_count"] == 0
        assert readback_row["actual"]["missing_readback_prerequisite_count"] == 13
        assert readback_row["actual"]["reported_allowed_readback_count"] == 0
        assert readback_row["actual"]["reported_forbidden_readback_count"] == 0
        assert readback_row["actual"]["durable_authoring_command_result_readback_accepted_count"] == 0
        assert readback_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert readback_row["actual"]["asset_write_performed_count"] == 0
        assert readback_row["actual"]["package_dirty_marked_count"] == 0
        assert readback_row["actual"]["durable_authoring_enabled_count"] == 0
        assert readback_row["actual"]["durable_authoring_allowed_count"] == 0
        assert readback_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert readback_row["actual"]["cleanup_allowed_count"] == 0
        final_release_row = find_row(report, "durable_canary_authoring_final_no_save_release_contract")
        assert final_release_row["status"] == "passed"
        assert final_release_row["actual"]["durable_requested_canary_authoring_final_no_save_release_count"] == 1
        assert final_release_row["actual"]["final_no_save_release_contract_defined_count"] == 1
        assert final_release_row["actual"]["readback_contract_ready_count"] == 1
        assert final_release_row["actual"]["readback_inputs_satisfied_count"] == 0
        assert final_release_row["actual"]["readback_record_valid_count"] == 0
        assert final_release_row["actual"]["allowed_readback_observed_count"] == 0
        assert final_release_row["actual"]["no_forbidden_readbacks_count"] == 0
        assert final_release_row["actual"]["final_no_save_release_inputs_satisfied_count"] == 0
        assert final_release_row["actual"]["final_no_save_release_record_present_count"] == 0
        assert final_release_row["actual"]["record_schema_matches_count"] == 0
        assert final_release_row["actual"]["final_no_save_release_scope_matches_count"] == 0
        assert final_release_row["actual"]["explicit_final_no_save_release_authorized_count"] == 0
        assert final_release_row["actual"]["final_no_save_release_status_passed_count"] == 0
        assert final_release_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert final_release_row["actual"]["allowed_final_no_save_release_observed_count"] == 0
        assert final_release_row["actual"]["no_forbidden_final_no_save_releases_count"] == 0
        assert final_release_row["actual"]["final_no_save_release_record_valid_count"] == 0
        assert final_release_row["actual"]["final_no_save_release_record_rejected_count"] == 0
        assert final_release_row["actual"]["unsafe_final_no_save_release_record_count"] == 0
        assert final_release_row["actual"]["missing_final_no_save_release_prerequisite_count"] == 13
        assert final_release_row["actual"]["reported_allowed_final_no_save_release_count"] == 0
        assert final_release_row["actual"]["reported_forbidden_final_no_save_release_count"] == 0
        assert final_release_row["actual"]["durable_authoring_final_no_save_release_accepted_count"] == 0
        assert final_release_row["actual"]["durable_authoring_command_result_readback_accepted_count"] == 0
        assert final_release_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert final_release_row["actual"]["asset_write_performed_count"] == 0
        assert final_release_row["actual"]["package_dirty_marked_count"] == 0
        assert final_release_row["actual"]["durable_authoring_enabled_count"] == 0
        assert final_release_row["actual"]["durable_authoring_allowed_count"] == 0
        assert final_release_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert final_release_row["actual"]["cleanup_allowed_count"] == 0
        assert final_release_row["actual"]["live_command_dispatched_count"] == 0
        assert final_release_row["actual"]["live_command_executed_count"] == 0
        readiness_row = find_row(report, "durable_canary_authoring_final_release_readiness_contract")
        assert readiness_row["status"] == "passed"
        assert readiness_row["actual"]["durable_requested_canary_authoring_final_release_readiness_count"] == 1
        assert readiness_row["actual"]["final_release_readiness_contract_defined_count"] == 1
        assert readiness_row["actual"]["final_no_save_release_contract_ready_count"] == 1
        assert readiness_row["actual"]["final_no_save_release_inputs_satisfied_count"] == 0
        assert readiness_row["actual"]["final_no_save_release_record_valid_count"] == 0
        assert readiness_row["actual"]["allowed_final_no_save_release_observed_count"] == 0
        assert readiness_row["actual"]["no_forbidden_final_no_save_releases_count"] == 0
        assert readiness_row["actual"]["final_release_readiness_inputs_satisfied_count"] == 0
        assert readiness_row["actual"]["final_release_readiness_record_present_count"] == 0
        assert readiness_row["actual"]["record_schema_matches_count"] == 0
        assert readiness_row["actual"]["readiness_scope_matches_count"] == 0
        assert readiness_row["actual"]["explicit_readiness_authorized_count"] == 0
        assert readiness_row["actual"]["readiness_status_passed_count"] == 0
        assert readiness_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert readiness_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert readiness_row["actual"]["allowed_final_release_readiness_observed_count"] == 0
        assert readiness_row["actual"]["no_forbidden_final_release_readiness_claims_count"] == 0
        assert readiness_row["actual"]["final_release_readiness_record_valid_count"] == 0
        assert readiness_row["actual"]["final_release_readiness_record_rejected_count"] == 0
        assert readiness_row["actual"]["unsafe_final_release_readiness_record_count"] == 0
        assert readiness_row["actual"]["missing_final_release_readiness_prerequisite_count"] == 14
        assert readiness_row["actual"]["reported_allowed_final_release_readiness_count"] == 0
        assert readiness_row["actual"]["reported_forbidden_final_release_readiness_count"] == 0
        assert readiness_row["actual"]["durable_authoring_final_release_readiness_accepted_count"] == 0
        assert readiness_row["actual"]["durable_authoring_final_no_save_release_accepted_count"] == 0
        assert readiness_row["actual"]["durable_authoring_command_result_readback_accepted_count"] == 0
        assert readiness_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert readiness_row["actual"]["asset_write_performed_count"] == 0
        assert readiness_row["actual"]["package_dirty_marked_count"] == 0
        assert readiness_row["actual"]["durable_authoring_enabled_count"] == 0
        assert readiness_row["actual"]["durable_authoring_allowed_count"] == 0
        assert readiness_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert readiness_row["actual"]["cleanup_allowed_count"] == 0
        assert readiness_row["actual"]["live_command_dispatched_count"] == 0
        assert readiness_row["actual"]["live_command_executed_count"] == 0
        assert readiness_row["actual"]["durable_executor_implementation_review_started_count"] == 0
        implementation_review_row = find_row(report, "durable_executor_implementation_review_gate_contract")
        assert implementation_review_row["status"] == "passed"
        assert implementation_review_row["actual"]["durable_requested_executor_implementation_review_count"] == 1
        assert implementation_review_row["actual"]["implementation_review_contract_defined_count"] == 1
        assert implementation_review_row["actual"]["final_release_readiness_contract_ready_count"] == 1
        assert implementation_review_row["actual"]["final_release_readiness_inputs_satisfied_count"] == 0
        assert implementation_review_row["actual"]["final_release_readiness_record_valid_count"] == 0
        assert implementation_review_row["actual"]["allowed_final_release_readiness_observed_count"] == 0
        assert implementation_review_row["actual"]["no_forbidden_final_release_readiness_claims_count"] == 0
        assert implementation_review_row["actual"]["implementation_review_inputs_satisfied_count"] == 0
        assert implementation_review_row["actual"]["implementation_review_record_present_count"] == 0
        assert implementation_review_row["actual"]["record_schema_matches_count"] == 0
        assert implementation_review_row["actual"]["implementation_review_scope_matches_count"] == 0
        assert implementation_review_row["actual"]["explicit_implementation_review_authorized_count"] == 0
        assert implementation_review_row["actual"]["review_status_passed_count"] == 0
        assert implementation_review_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert implementation_review_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert implementation_review_row["actual"]["allowed_implementation_review_observed_count"] == 0
        assert implementation_review_row["actual"]["no_forbidden_implementation_review_claims_count"] == 0
        assert implementation_review_row["actual"]["implementation_review_record_valid_count"] == 0
        assert implementation_review_row["actual"]["implementation_review_record_rejected_count"] == 0
        assert implementation_review_row["actual"]["unsafe_implementation_review_record_count"] == 0
        assert implementation_review_row["actual"]["missing_implementation_review_prerequisite_count"] == 14
        assert implementation_review_row["actual"]["reported_allowed_implementation_review_count"] == 0
        assert implementation_review_row["actual"]["reported_forbidden_implementation_review_count"] == 0
        assert implementation_review_row["actual"]["durable_executor_implementation_review_started_count"] == 0
        assert implementation_review_row["actual"]["durable_executor_implementation_review_accepted_count"] == 0
        assert implementation_review_row["actual"]["durable_executor_implementation_plan_started_count"] == 0
        assert implementation_review_row["actual"]["code_change_performed_count"] == 0
        assert implementation_review_row["actual"]["executor_code_modified_count"] == 0
        assert implementation_review_row["actual"]["unreal_asset_modified_count"] == 0
        assert implementation_review_row["actual"]["live_bridge_probe_started_count"] == 0
        assert implementation_review_row["actual"]["durable_authoring_enabled_count"] == 0
        assert implementation_review_row["actual"]["durable_authoring_allowed_count"] == 0
        assert implementation_review_row["actual"]["asset_write_performed_count"] == 0
        assert implementation_review_row["actual"]["package_dirty_marked_count"] == 0
        assert implementation_review_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert implementation_review_row["actual"]["cleanup_allowed_count"] == 0
        assert implementation_review_row["actual"]["live_command_dispatched_count"] == 0
        assert implementation_review_row["actual"]["live_command_executed_count"] == 0
        implementation_plan_row = find_row(report, "durable_executor_implementation_plan_contract")
        assert implementation_plan_row["status"] == "passed"
        assert implementation_plan_row["actual"]["durable_requested_executor_implementation_plan_count"] == 1
        assert implementation_plan_row["actual"]["implementation_plan_contract_defined_count"] == 1
        assert implementation_plan_row["actual"]["implementation_review_contract_ready_count"] == 1
        assert implementation_plan_row["actual"]["implementation_review_inputs_satisfied_count"] == 0
        assert implementation_plan_row["actual"]["implementation_review_record_valid_count"] == 0
        assert implementation_plan_row["actual"]["allowed_implementation_review_observed_count"] == 0
        assert implementation_plan_row["actual"]["no_forbidden_implementation_review_claims_count"] == 0
        assert implementation_plan_row["actual"]["implementation_plan_inputs_satisfied_count"] == 0
        assert implementation_plan_row["actual"]["implementation_plan_record_present_count"] == 0
        assert implementation_plan_row["actual"]["record_schema_matches_count"] == 0
        assert implementation_plan_row["actual"]["implementation_plan_scope_matches_count"] == 0
        assert implementation_plan_row["actual"]["explicit_implementation_plan_authorized_count"] == 0
        assert implementation_plan_row["actual"]["plan_status_passed_count"] == 0
        assert implementation_plan_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert implementation_plan_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert implementation_plan_row["actual"]["allowed_implementation_plan_observed_count"] == 0
        assert implementation_plan_row["actual"]["no_forbidden_implementation_plan_claims_count"] == 0
        assert implementation_plan_row["actual"]["implementation_plan_record_valid_count"] == 0
        assert implementation_plan_row["actual"]["implementation_plan_record_rejected_count"] == 0
        assert implementation_plan_row["actual"]["unsafe_implementation_plan_record_count"] == 0
        assert implementation_plan_row["actual"]["missing_implementation_plan_prerequisite_count"] == 14
        assert implementation_plan_row["actual"]["reported_allowed_implementation_plan_count"] == 0
        assert implementation_plan_row["actual"]["reported_forbidden_implementation_plan_count"] == 0
        assert implementation_plan_row["actual"]["durable_executor_implementation_plan_started_count"] == 0
        assert implementation_plan_row["actual"]["durable_executor_implementation_plan_accepted_count"] == 0
        assert implementation_plan_row["actual"]["durable_executor_change_design_started_count"] == 0
        assert implementation_plan_row["actual"]["code_change_performed_count"] == 0
        assert implementation_plan_row["actual"]["executor_code_modified_count"] == 0
        assert implementation_plan_row["actual"]["unreal_asset_modified_count"] == 0
        assert implementation_plan_row["actual"]["live_bridge_probe_started_count"] == 0
        assert implementation_plan_row["actual"]["durable_authoring_enabled_count"] == 0
        assert implementation_plan_row["actual"]["durable_authoring_allowed_count"] == 0
        assert implementation_plan_row["actual"]["asset_write_performed_count"] == 0
        assert implementation_plan_row["actual"]["package_dirty_marked_count"] == 0
        assert implementation_plan_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert implementation_plan_row["actual"]["cleanup_allowed_count"] == 0
        assert implementation_plan_row["actual"]["live_command_dispatched_count"] == 0
        assert implementation_plan_row["actual"]["live_command_executed_count"] == 0
        change_design_row = find_row(report, "durable_executor_change_design_contract")
        assert change_design_row["status"] == "passed"
        assert change_design_row["actual"]["durable_requested_executor_change_design_count"] == 1
        assert change_design_row["actual"]["change_design_contract_defined_count"] == 1
        assert change_design_row["actual"]["implementation_plan_contract_ready_count"] == 1
        assert change_design_row["actual"]["implementation_plan_inputs_satisfied_count"] == 0
        assert change_design_row["actual"]["implementation_plan_record_valid_count"] == 0
        assert change_design_row["actual"]["allowed_implementation_plan_observed_count"] == 0
        assert change_design_row["actual"]["no_forbidden_implementation_plan_claims_count"] == 0
        assert change_design_row["actual"]["change_design_inputs_satisfied_count"] == 0
        assert change_design_row["actual"]["change_design_record_present_count"] == 0
        assert change_design_row["actual"]["record_schema_matches_count"] == 0
        assert change_design_row["actual"]["change_design_scope_matches_count"] == 0
        assert change_design_row["actual"]["explicit_change_design_authorized_count"] == 0
        assert change_design_row["actual"]["design_status_passed_count"] == 0
        assert change_design_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert change_design_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert change_design_row["actual"]["allowed_change_design_observed_count"] == 0
        assert change_design_row["actual"]["no_forbidden_change_design_claims_count"] == 0
        assert change_design_row["actual"]["change_design_record_valid_count"] == 0
        assert change_design_row["actual"]["change_design_record_rejected_count"] == 0
        assert change_design_row["actual"]["unsafe_change_design_record_count"] == 0
        assert change_design_row["actual"]["missing_change_design_prerequisite_count"] == 14
        assert change_design_row["actual"]["reported_allowed_change_design_count"] == 0
        assert change_design_row["actual"]["reported_forbidden_change_design_count"] == 0
        assert change_design_row["actual"]["durable_executor_change_design_started_count"] == 0
        assert change_design_row["actual"]["durable_executor_change_design_accepted_count"] == 0
        assert change_design_row["actual"]["durable_executor_code_change_approval_started_count"] == 0
        assert change_design_row["actual"]["code_change_performed_count"] == 0
        assert change_design_row["actual"]["executor_code_modified_count"] == 0
        assert change_design_row["actual"]["unreal_asset_modified_count"] == 0
        assert change_design_row["actual"]["live_bridge_probe_started_count"] == 0
        assert change_design_row["actual"]["durable_authoring_enabled_count"] == 0
        assert change_design_row["actual"]["durable_authoring_allowed_count"] == 0
        assert change_design_row["actual"]["asset_write_performed_count"] == 0
        assert change_design_row["actual"]["package_dirty_marked_count"] == 0
        assert change_design_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert change_design_row["actual"]["cleanup_allowed_count"] == 0
        assert change_design_row["actual"]["live_command_dispatched_count"] == 0
        assert change_design_row["actual"]["live_command_executed_count"] == 0
        approval_row = find_row(report, "durable_executor_code_change_approval_contract")
        assert approval_row["status"] == "passed"
        assert approval_row["actual"]["durable_requested_executor_code_change_approval_count"] == 1
        assert approval_row["actual"]["code_change_approval_contract_defined_count"] == 1
        assert approval_row["actual"]["change_design_contract_ready_count"] == 1
        assert approval_row["actual"]["change_design_inputs_satisfied_count"] == 0
        assert approval_row["actual"]["change_design_record_valid_count"] == 0
        assert approval_row["actual"]["allowed_change_design_observed_count"] == 0
        assert approval_row["actual"]["no_forbidden_change_design_claims_count"] == 0
        assert approval_row["actual"]["code_change_approval_inputs_satisfied_count"] == 0
        assert approval_row["actual"]["code_change_approval_record_present_count"] == 0
        assert approval_row["actual"]["record_schema_matches_count"] == 0
        assert approval_row["actual"]["code_change_approval_scope_matches_count"] == 0
        assert approval_row["actual"]["explicit_code_change_approval_authorized_count"] == 0
        assert approval_row["actual"]["approval_status_passed_count"] == 0
        assert approval_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert approval_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert approval_row["actual"]["allowed_code_change_approval_observed_count"] == 0
        assert approval_row["actual"]["no_forbidden_code_change_approval_claims_count"] == 0
        assert approval_row["actual"]["code_change_approval_record_valid_count"] == 0
        assert approval_row["actual"]["code_change_approval_record_rejected_count"] == 0
        assert approval_row["actual"]["unsafe_code_change_approval_record_count"] == 0
        assert approval_row["actual"]["missing_code_change_approval_prerequisite_count"] == 14
        assert approval_row["actual"]["reported_allowed_code_change_approval_count"] == 0
        assert approval_row["actual"]["reported_forbidden_code_change_approval_count"] == 0
        assert approval_row["actual"]["durable_executor_code_change_approval_started_count"] == 0
        assert approval_row["actual"]["durable_executor_code_change_approval_accepted_count"] == 0
        assert approval_row["actual"]["durable_executor_code_patch_plan_started_count"] == 0
        assert approval_row["actual"]["code_change_performed_count"] == 0
        assert approval_row["actual"]["executor_code_modified_count"] == 0
        assert approval_row["actual"]["unreal_asset_modified_count"] == 0
        assert approval_row["actual"]["live_bridge_probe_started_count"] == 0
        assert approval_row["actual"]["durable_authoring_enabled_count"] == 0
        assert approval_row["actual"]["durable_authoring_allowed_count"] == 0
        assert approval_row["actual"]["asset_write_performed_count"] == 0
        assert approval_row["actual"]["package_dirty_marked_count"] == 0
        assert approval_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert approval_row["actual"]["cleanup_allowed_count"] == 0
        assert approval_row["actual"]["live_command_dispatched_count"] == 0
        assert approval_row["actual"]["live_command_executed_count"] == 0
        patch_plan_row = find_row(report, "durable_executor_code_patch_plan_contract")
        assert patch_plan_row["status"] == "passed"
        assert patch_plan_row["actual"]["durable_requested_executor_code_patch_plan_count"] == 1
        assert patch_plan_row["actual"]["code_patch_plan_contract_defined_count"] == 1
        assert patch_plan_row["actual"]["code_change_approval_contract_ready_count"] == 1
        assert patch_plan_row["actual"]["code_change_approval_inputs_satisfied_count"] == 0
        assert patch_plan_row["actual"]["code_change_approval_record_valid_count"] == 0
        assert patch_plan_row["actual"]["allowed_code_change_approval_observed_count"] == 0
        assert patch_plan_row["actual"]["no_forbidden_code_change_approval_claims_count"] == 0
        assert patch_plan_row["actual"]["code_patch_plan_inputs_satisfied_count"] == 0
        assert patch_plan_row["actual"]["code_patch_plan_record_present_count"] == 0
        assert patch_plan_row["actual"]["record_schema_matches_count"] == 0
        assert patch_plan_row["actual"]["code_patch_plan_scope_matches_count"] == 0
        assert patch_plan_row["actual"]["explicit_code_patch_plan_authorized_count"] == 0
        assert patch_plan_row["actual"]["plan_status_passed_count"] == 0
        assert patch_plan_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert patch_plan_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert patch_plan_row["actual"]["allowed_code_patch_plan_observed_count"] == 0
        assert patch_plan_row["actual"]["no_forbidden_code_patch_plan_claims_count"] == 0
        assert patch_plan_row["actual"]["code_patch_plan_record_valid_count"] == 0
        assert patch_plan_row["actual"]["code_patch_plan_record_rejected_count"] == 0
        assert patch_plan_row["actual"]["unsafe_code_patch_plan_record_count"] == 0
        assert patch_plan_row["actual"]["missing_code_patch_plan_prerequisite_count"] == 14
        assert patch_plan_row["actual"]["reported_allowed_code_patch_plan_count"] == 0
        assert patch_plan_row["actual"]["reported_forbidden_code_patch_plan_count"] == 0
        assert patch_plan_row["actual"]["durable_executor_code_patch_plan_started_count"] == 0
        assert patch_plan_row["actual"]["durable_executor_code_patch_plan_accepted_count"] == 0
        assert patch_plan_row["actual"]["durable_executor_code_patch_review_started_count"] == 0
        assert patch_plan_row["actual"]["code_change_performed_count"] == 0
        assert patch_plan_row["actual"]["executor_code_modified_count"] == 0
        assert patch_plan_row["actual"]["unreal_asset_modified_count"] == 0
        assert patch_plan_row["actual"]["live_bridge_probe_started_count"] == 0
        assert patch_plan_row["actual"]["durable_authoring_enabled_count"] == 0
        assert patch_plan_row["actual"]["durable_authoring_allowed_count"] == 0
        assert patch_plan_row["actual"]["asset_write_performed_count"] == 0
        assert patch_plan_row["actual"]["package_dirty_marked_count"] == 0
        assert patch_plan_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert patch_plan_row["actual"]["cleanup_allowed_count"] == 0
        assert patch_plan_row["actual"]["live_command_dispatched_count"] == 0
        assert patch_plan_row["actual"]["live_command_executed_count"] == 0
        patch_review_row = find_row(report, "durable_executor_code_patch_review_contract")
        assert patch_review_row["status"] == "passed"
        assert patch_review_row["actual"]["durable_requested_executor_code_patch_review_count"] == 1
        assert patch_review_row["actual"]["code_patch_review_contract_defined_count"] == 1
        assert patch_review_row["actual"]["code_patch_plan_contract_ready_count"] == 1
        assert patch_review_row["actual"]["code_patch_plan_inputs_satisfied_count"] == 0
        assert patch_review_row["actual"]["code_patch_plan_record_valid_count"] == 0
        assert patch_review_row["actual"]["allowed_code_patch_plan_observed_count"] == 0
        assert patch_review_row["actual"]["no_forbidden_code_patch_plan_claims_count"] == 0
        assert patch_review_row["actual"]["code_patch_review_inputs_satisfied_count"] == 0
        assert patch_review_row["actual"]["code_patch_review_record_present_count"] == 0
        assert patch_review_row["actual"]["record_schema_matches_count"] == 0
        assert patch_review_row["actual"]["code_patch_review_scope_matches_count"] == 0
        assert patch_review_row["actual"]["explicit_code_patch_review_authorized_count"] == 0
        assert patch_review_row["actual"]["review_status_passed_count"] == 0
        assert patch_review_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert patch_review_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert patch_review_row["actual"]["allowed_code_patch_review_observed_count"] == 0
        assert patch_review_row["actual"]["no_forbidden_code_patch_review_claims_count"] == 0
        assert patch_review_row["actual"]["code_patch_review_record_valid_count"] == 0
        assert patch_review_row["actual"]["code_patch_review_record_rejected_count"] == 0
        assert patch_review_row["actual"]["unsafe_code_patch_review_record_count"] == 0
        assert patch_review_row["actual"]["missing_code_patch_review_prerequisite_count"] == 14
        assert patch_review_row["actual"]["reported_allowed_code_patch_review_count"] == 0
        assert patch_review_row["actual"]["reported_forbidden_code_patch_review_count"] == 0
        assert patch_review_row["actual"]["durable_executor_code_patch_review_started_count"] == 0
        assert patch_review_row["actual"]["durable_executor_code_patch_review_accepted_count"] == 0
        assert patch_review_row["actual"]["durable_executor_code_patch_application_started_count"] == 0
        assert patch_review_row["actual"]["code_change_performed_count"] == 0
        assert patch_review_row["actual"]["executor_code_modified_count"] == 0
        assert patch_review_row["actual"]["unreal_asset_modified_count"] == 0
        assert patch_review_row["actual"]["live_bridge_probe_started_count"] == 0
        assert patch_review_row["actual"]["durable_authoring_enabled_count"] == 0
        assert patch_review_row["actual"]["durable_authoring_allowed_count"] == 0
        assert patch_review_row["actual"]["asset_write_performed_count"] == 0
        assert patch_review_row["actual"]["package_dirty_marked_count"] == 0
        assert patch_review_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert patch_review_row["actual"]["cleanup_allowed_count"] == 0
        assert patch_review_row["actual"]["live_command_dispatched_count"] == 0
        assert patch_review_row["actual"]["live_command_executed_count"] == 0
        patch_application_row = find_row(report, "durable_executor_code_patch_application_contract")
        assert patch_application_row["status"] == "passed"
        assert patch_application_row["actual"]["durable_requested_executor_code_patch_application_count"] == 1
        assert patch_application_row["actual"]["code_patch_application_contract_defined_count"] == 1
        assert patch_application_row["actual"]["code_patch_review_contract_ready_count"] == 1
        assert patch_application_row["actual"]["code_patch_review_inputs_satisfied_count"] == 0
        assert patch_application_row["actual"]["code_patch_review_record_valid_count"] == 0
        assert patch_application_row["actual"]["allowed_code_patch_review_observed_count"] == 0
        assert patch_application_row["actual"]["no_forbidden_code_patch_review_claims_count"] == 0
        assert patch_application_row["actual"]["code_patch_application_inputs_satisfied_count"] == 0
        assert patch_application_row["actual"]["code_patch_application_record_present_count"] == 0
        assert patch_application_row["actual"]["record_schema_matches_count"] == 0
        assert patch_application_row["actual"]["code_patch_application_scope_matches_count"] == 0
        assert patch_application_row["actual"]["explicit_code_patch_application_authorized_count"] == 0
        assert patch_application_row["actual"]["application_status_passed_count"] == 0
        assert patch_application_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert patch_application_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert patch_application_row["actual"]["allowed_code_patch_application_observed_count"] == 0
        assert patch_application_row["actual"]["no_forbidden_code_patch_application_claims_count"] == 0
        assert patch_application_row["actual"]["code_patch_application_record_valid_count"] == 0
        assert patch_application_row["actual"]["code_patch_application_record_rejected_count"] == 0
        assert patch_application_row["actual"]["unsafe_code_patch_application_record_count"] == 0
        assert patch_application_row["actual"]["missing_code_patch_application_prerequisite_count"] == 14
        assert patch_application_row["actual"]["reported_allowed_code_patch_application_count"] == 0
        assert patch_application_row["actual"]["reported_forbidden_code_patch_application_count"] == 0
        assert patch_application_row["actual"]["durable_executor_code_patch_application_started_count"] == 0
        assert patch_application_row["actual"]["durable_executor_code_patch_application_accepted_count"] == 0
        assert patch_application_row["actual"]["durable_executor_code_patch_execution_started_count"] == 0
        assert patch_application_row["actual"]["code_change_performed_count"] == 0
        assert patch_application_row["actual"]["executor_code_modified_count"] == 0
        assert patch_application_row["actual"]["unreal_asset_modified_count"] == 0
        assert patch_application_row["actual"]["live_bridge_probe_started_count"] == 0
        assert patch_application_row["actual"]["durable_authoring_enabled_count"] == 0
        assert patch_application_row["actual"]["durable_authoring_allowed_count"] == 0
        assert patch_application_row["actual"]["asset_write_performed_count"] == 0
        assert patch_application_row["actual"]["package_dirty_marked_count"] == 0
        assert patch_application_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert patch_application_row["actual"]["cleanup_allowed_count"] == 0
        assert patch_application_row["actual"]["live_command_dispatched_count"] == 0
        assert patch_application_row["actual"]["live_command_executed_count"] == 0
        patch_execution_row = find_row(report, "durable_executor_code_patch_execution_contract")
        assert patch_execution_row["status"] == "passed"
        assert patch_execution_row["actual"]["durable_requested_executor_code_patch_execution_count"] == 1
        assert patch_execution_row["actual"]["code_patch_execution_contract_defined_count"] == 1
        assert patch_execution_row["actual"]["code_patch_application_contract_ready_count"] == 1
        assert patch_execution_row["actual"]["code_patch_application_inputs_satisfied_count"] == 0
        assert patch_execution_row["actual"]["code_patch_application_record_valid_count"] == 0
        assert patch_execution_row["actual"]["allowed_code_patch_application_observed_count"] == 0
        assert patch_execution_row["actual"]["no_forbidden_code_patch_application_claims_count"] == 0
        assert patch_execution_row["actual"]["code_patch_execution_inputs_satisfied_count"] == 0
        assert patch_execution_row["actual"]["code_patch_execution_record_present_count"] == 0
        assert patch_execution_row["actual"]["record_schema_matches_count"] == 0
        assert patch_execution_row["actual"]["code_patch_execution_scope_matches_count"] == 0
        assert patch_execution_row["actual"]["explicit_code_patch_execution_authorized_count"] == 0
        assert patch_execution_row["actual"]["execution_status_passed_count"] == 0
        assert patch_execution_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert patch_execution_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert patch_execution_row["actual"]["allowed_code_patch_execution_observed_count"] == 0
        assert patch_execution_row["actual"]["no_forbidden_code_patch_execution_claims_count"] == 0
        assert patch_execution_row["actual"]["code_patch_execution_record_valid_count"] == 0
        assert patch_execution_row["actual"]["code_patch_execution_record_rejected_count"] == 0
        assert patch_execution_row["actual"]["unsafe_code_patch_execution_record_count"] == 0
        assert patch_execution_row["actual"]["missing_code_patch_execution_prerequisite_count"] == 14
        assert patch_execution_row["actual"]["reported_allowed_code_patch_execution_count"] == 0
        assert patch_execution_row["actual"]["reported_forbidden_code_patch_execution_count"] == 0
        assert patch_execution_row["actual"]["durable_executor_code_patch_execution_started_count"] == 0
        assert patch_execution_row["actual"]["durable_executor_code_patch_execution_accepted_count"] == 0
        assert patch_execution_row["actual"]["durable_executor_code_patch_result_started_count"] == 0
        assert patch_execution_row["actual"]["code_change_performed_count"] == 0
        assert patch_execution_row["actual"]["executor_code_modified_count"] == 0
        assert patch_execution_row["actual"]["unreal_asset_modified_count"] == 0
        assert patch_execution_row["actual"]["live_bridge_probe_started_count"] == 0
        assert patch_execution_row["actual"]["durable_authoring_enabled_count"] == 0
        assert patch_execution_row["actual"]["durable_authoring_allowed_count"] == 0
        assert patch_execution_row["actual"]["asset_write_performed_count"] == 0
        assert patch_execution_row["actual"]["package_dirty_marked_count"] == 0
        assert patch_execution_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert patch_execution_row["actual"]["cleanup_allowed_count"] == 0
        assert patch_execution_row["actual"]["live_command_dispatched_count"] == 0
        assert patch_execution_row["actual"]["live_command_executed_count"] == 0
        patch_result_row = find_row(report, "durable_executor_code_patch_result_contract")
        assert patch_result_row["status"] == "passed"
        assert patch_result_row["actual"]["durable_requested_executor_code_patch_result_count"] == 1
        assert patch_result_row["actual"]["code_patch_result_contract_defined_count"] == 1
        assert patch_result_row["actual"]["code_patch_execution_contract_ready_count"] == 1
        assert patch_result_row["actual"]["code_patch_execution_inputs_satisfied_count"] == 0
        assert patch_result_row["actual"]["code_patch_execution_record_valid_count"] == 0
        assert patch_result_row["actual"]["allowed_code_patch_execution_observed_count"] == 0
        assert patch_result_row["actual"]["no_forbidden_code_patch_execution_claims_count"] == 0
        assert patch_result_row["actual"]["code_patch_result_inputs_satisfied_count"] == 0
        assert patch_result_row["actual"]["code_patch_result_record_present_count"] == 0
        assert patch_result_row["actual"]["record_schema_matches_count"] == 0
        assert patch_result_row["actual"]["code_patch_result_scope_matches_count"] == 0
        assert patch_result_row["actual"]["explicit_code_patch_result_authorized_count"] == 0
        assert patch_result_row["actual"]["result_status_passed_count"] == 0
        assert patch_result_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert patch_result_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert patch_result_row["actual"]["allowed_code_patch_result_observed_count"] == 0
        assert patch_result_row["actual"]["no_forbidden_code_patch_result_claims_count"] == 0
        assert patch_result_row["actual"]["code_patch_result_record_valid_count"] == 0
        assert patch_result_row["actual"]["code_patch_result_record_rejected_count"] == 0
        assert patch_result_row["actual"]["unsafe_code_patch_result_record_count"] == 0
        assert patch_result_row["actual"]["missing_code_patch_result_prerequisite_count"] == 14
        assert patch_result_row["actual"]["reported_allowed_code_patch_result_count"] == 0
        assert patch_result_row["actual"]["reported_forbidden_code_patch_result_count"] == 0
        assert patch_result_row["actual"]["durable_executor_code_patch_result_started_count"] == 0
        assert patch_result_row["actual"]["durable_executor_code_patch_result_accepted_count"] == 0
        assert patch_result_row["actual"]["durable_executor_code_patch_result_readback_started_count"] == 0
        assert patch_result_row["actual"]["code_change_performed_count"] == 0
        assert patch_result_row["actual"]["executor_code_modified_count"] == 0
        assert patch_result_row["actual"]["unreal_asset_modified_count"] == 0
        assert patch_result_row["actual"]["live_bridge_probe_started_count"] == 0
        assert patch_result_row["actual"]["durable_authoring_enabled_count"] == 0
        assert patch_result_row["actual"]["durable_authoring_allowed_count"] == 0
        assert patch_result_row["actual"]["asset_write_performed_count"] == 0
        assert patch_result_row["actual"]["package_dirty_marked_count"] == 0
        assert patch_result_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert patch_result_row["actual"]["cleanup_allowed_count"] == 0
        assert patch_result_row["actual"]["live_command_dispatched_count"] == 0
        assert patch_result_row["actual"]["live_command_executed_count"] == 0
        patch_readback_row = find_row(
            report, "durable_executor_code_patch_result_readback_contract"
        )
        assert patch_readback_row["status"] == "passed"
        assert patch_readback_row["actual"]["durable_requested_executor_code_patch_result_readback_count"] == 1
        assert patch_readback_row["actual"]["code_patch_result_readback_contract_defined_count"] == 1
        assert patch_readback_row["actual"]["code_patch_result_contract_ready_count"] == 1
        assert patch_readback_row["actual"]["code_patch_result_inputs_satisfied_count"] == 0
        assert patch_readback_row["actual"]["code_patch_result_record_valid_count"] == 0
        assert patch_readback_row["actual"]["allowed_code_patch_result_observed_count"] == 0
        assert patch_readback_row["actual"]["no_forbidden_code_patch_result_claims_count"] == 0
        assert patch_readback_row["actual"]["code_patch_result_readback_inputs_satisfied_count"] == 0
        assert patch_readback_row["actual"]["code_patch_result_readback_record_present_count"] == 0
        assert patch_readback_row["actual"]["record_schema_matches_count"] == 0
        assert patch_readback_row["actual"]["code_patch_result_readback_scope_matches_count"] == 0
        assert patch_readback_row["actual"]["explicit_code_patch_result_readback_authorized_count"] == 0
        assert patch_readback_row["actual"]["readback_status_passed_count"] == 0
        assert patch_readback_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert patch_readback_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert patch_readback_row["actual"]["allowed_code_patch_result_readback_observed_count"] == 0
        assert patch_readback_row["actual"]["no_forbidden_code_patch_result_readback_claims_count"] == 0
        assert patch_readback_row["actual"]["code_patch_result_readback_record_valid_count"] == 0
        assert patch_readback_row["actual"]["code_patch_result_readback_record_rejected_count"] == 0
        assert patch_readback_row["actual"]["unsafe_code_patch_result_readback_record_count"] == 0
        assert patch_readback_row["actual"]["missing_code_patch_result_readback_prerequisite_count"] == 14
        assert patch_readback_row["actual"]["reported_allowed_code_patch_result_readback_count"] == 0
        assert patch_readback_row["actual"]["reported_forbidden_code_patch_result_readback_count"] == 0
        assert patch_readback_row["actual"]["durable_executor_code_patch_result_readback_started_count"] == 0
        assert patch_readback_row["actual"]["durable_executor_code_patch_result_readback_accepted_count"] == 0
        assert patch_readback_row["actual"]["durable_executor_code_patch_final_no_save_release_started_count"] == 0
        assert patch_readback_row["actual"]["code_change_performed_count"] == 0
        assert patch_readback_row["actual"]["executor_code_modified_count"] == 0
        assert patch_readback_row["actual"]["unreal_asset_modified_count"] == 0
        assert patch_readback_row["actual"]["live_bridge_probe_started_count"] == 0
        assert patch_readback_row["actual"]["durable_authoring_enabled_count"] == 0
        assert patch_readback_row["actual"]["durable_authoring_allowed_count"] == 0
        assert patch_readback_row["actual"]["asset_write_performed_count"] == 0
        assert patch_readback_row["actual"]["package_dirty_marked_count"] == 0
        assert patch_readback_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert patch_readback_row["actual"]["cleanup_allowed_count"] == 0
        assert patch_readback_row["actual"]["live_command_dispatched_count"] == 0
        assert patch_readback_row["actual"]["live_command_executed_count"] == 0
        patch_final_release_row = find_row(
            report, "durable_executor_code_patch_final_no_save_release_contract"
        )
        assert patch_final_release_row["status"] == "passed"
        assert patch_final_release_row["actual"]["durable_requested_executor_code_patch_final_no_save_release_count"] == 1
        assert patch_final_release_row["actual"]["code_patch_final_no_save_release_contract_defined_count"] == 1
        assert patch_final_release_row["actual"]["code_patch_result_readback_contract_ready_count"] == 1
        assert patch_final_release_row["actual"]["code_patch_result_readback_inputs_satisfied_count"] == 0
        assert patch_final_release_row["actual"]["code_patch_result_readback_record_valid_count"] == 0
        assert patch_final_release_row["actual"]["allowed_code_patch_result_readback_observed_count"] == 0
        assert patch_final_release_row["actual"]["no_forbidden_code_patch_result_readback_claims_count"] == 0
        assert patch_final_release_row["actual"]["code_patch_final_no_save_release_inputs_satisfied_count"] == 0
        assert patch_final_release_row["actual"]["code_patch_final_no_save_release_record_present_count"] == 0
        assert patch_final_release_row["actual"]["record_schema_matches_count"] == 0
        assert patch_final_release_row["actual"]["code_patch_final_no_save_release_scope_matches_count"] == 0
        assert patch_final_release_row["actual"]["explicit_code_patch_final_no_save_release_authorized_count"] == 0
        assert patch_final_release_row["actual"]["final_no_save_release_status_passed_count"] == 0
        assert patch_final_release_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert patch_final_release_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert patch_final_release_row["actual"]["allowed_code_patch_final_no_save_release_observed_count"] == 0
        assert patch_final_release_row["actual"]["no_forbidden_code_patch_final_no_save_release_claims_count"] == 0
        assert patch_final_release_row["actual"]["code_patch_final_no_save_release_record_valid_count"] == 0
        assert patch_final_release_row["actual"]["code_patch_final_no_save_release_record_rejected_count"] == 0
        assert patch_final_release_row["actual"]["unsafe_code_patch_final_no_save_release_record_count"] == 0
        assert patch_final_release_row["actual"]["missing_code_patch_final_no_save_release_prerequisite_count"] == 14
        assert patch_final_release_row["actual"]["reported_allowed_code_patch_final_no_save_release_count"] == 0
        assert patch_final_release_row["actual"]["reported_forbidden_code_patch_final_no_save_release_count"] == 0
        assert patch_final_release_row["actual"]["durable_executor_code_patch_final_no_save_release_started_count"] == 0
        assert patch_final_release_row["actual"]["durable_executor_code_patch_final_no_save_release_accepted_count"] == 0
        assert patch_final_release_row["actual"]["durable_executor_code_patch_final_release_readiness_started_count"] == 0
        assert patch_final_release_row["actual"]["code_change_performed_count"] == 0
        assert patch_final_release_row["actual"]["executor_code_modified_count"] == 0
        assert patch_final_release_row["actual"]["unreal_asset_modified_count"] == 0
        assert patch_final_release_row["actual"]["live_bridge_probe_started_count"] == 0
        assert patch_final_release_row["actual"]["durable_authoring_enabled_count"] == 0
        assert patch_final_release_row["actual"]["durable_authoring_allowed_count"] == 0
        assert patch_final_release_row["actual"]["asset_write_performed_count"] == 0
        assert patch_final_release_row["actual"]["package_dirty_marked_count"] == 0
        assert patch_final_release_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert patch_final_release_row["actual"]["cleanup_allowed_count"] == 0
        assert patch_final_release_row["actual"]["live_command_dispatched_count"] == 0
        assert patch_final_release_row["actual"]["live_command_executed_count"] == 0
        patch_final_readiness_row = find_row(
            report, "durable_executor_code_patch_final_release_readiness_contract"
        )
        assert patch_final_readiness_row["status"] == "passed"
        assert patch_final_readiness_row["actual"]["durable_requested_executor_code_patch_final_release_readiness_count"] == 1
        assert patch_final_readiness_row["actual"]["code_patch_final_release_readiness_contract_defined_count"] == 1
        assert patch_final_readiness_row["actual"]["code_patch_final_no_save_release_contract_ready_count"] == 1
        assert patch_final_readiness_row["actual"]["code_patch_final_no_save_release_inputs_satisfied_count"] == 0
        assert patch_final_readiness_row["actual"]["code_patch_final_no_save_release_record_valid_count"] == 0
        assert patch_final_readiness_row["actual"]["allowed_code_patch_final_no_save_release_observed_count"] == 0
        assert patch_final_readiness_row["actual"]["no_forbidden_code_patch_final_no_save_release_claims_count"] == 0
        assert patch_final_readiness_row["actual"]["code_patch_final_release_readiness_inputs_satisfied_count"] == 0
        assert patch_final_readiness_row["actual"]["code_patch_final_release_readiness_record_present_count"] == 0
        assert patch_final_readiness_row["actual"]["record_schema_matches_count"] == 0
        assert patch_final_readiness_row["actual"]["code_patch_final_release_readiness_scope_matches_count"] == 0
        assert patch_final_readiness_row["actual"]["explicit_code_patch_final_release_readiness_authorized_count"] == 0
        assert patch_final_readiness_row["actual"]["readiness_status_passed_count"] == 0
        assert patch_final_readiness_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert patch_final_readiness_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert patch_final_readiness_row["actual"]["allowed_code_patch_final_release_readiness_observed_count"] == 0
        assert patch_final_readiness_row["actual"]["no_forbidden_code_patch_final_release_readiness_claims_count"] == 0
        assert patch_final_readiness_row["actual"]["code_patch_final_release_readiness_record_valid_count"] == 0
        assert patch_final_readiness_row["actual"]["code_patch_final_release_readiness_record_rejected_count"] == 0
        assert patch_final_readiness_row["actual"]["unsafe_code_patch_final_release_readiness_record_count"] == 0
        assert patch_final_readiness_row["actual"]["missing_code_patch_final_release_readiness_prerequisite_count"] == 14
        assert patch_final_readiness_row["actual"]["reported_allowed_code_patch_final_release_readiness_count"] == 0
        assert patch_final_readiness_row["actual"]["reported_forbidden_code_patch_final_release_readiness_count"] == 0
        assert patch_final_readiness_row["actual"]["durable_executor_code_patch_final_release_readiness_started_count"] == 0
        assert patch_final_readiness_row["actual"]["durable_executor_code_patch_final_release_ready_count"] == 0
        assert patch_final_readiness_row["actual"]["durable_executor_code_patch_release_review_started_count"] == 0
        assert patch_final_readiness_row["actual"]["code_change_performed_count"] == 0
        assert patch_final_readiness_row["actual"]["executor_code_modified_count"] == 0
        assert patch_final_readiness_row["actual"]["unreal_asset_modified_count"] == 0
        assert patch_final_readiness_row["actual"]["live_bridge_probe_started_count"] == 0
        assert patch_final_readiness_row["actual"]["durable_authoring_enabled_count"] == 0
        assert patch_final_readiness_row["actual"]["durable_authoring_allowed_count"] == 0
        assert patch_final_readiness_row["actual"]["asset_write_performed_count"] == 0
        assert patch_final_readiness_row["actual"]["package_dirty_marked_count"] == 0
        assert patch_final_readiness_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert patch_final_readiness_row["actual"]["cleanup_allowed_count"] == 0
        assert patch_final_readiness_row["actual"]["live_command_dispatched_count"] == 0
        assert patch_final_readiness_row["actual"]["live_command_executed_count"] == 0
        patch_release_review_row = find_row(
            report, "durable_executor_code_patch_release_review_contract"
        )
        assert patch_release_review_row["status"] == "passed"
        assert patch_release_review_row["actual"]["durable_requested_executor_code_patch_release_review_count"] == 1
        assert patch_release_review_row["actual"]["code_patch_release_review_contract_defined_count"] == 1
        assert patch_release_review_row["actual"]["code_patch_final_release_readiness_contract_ready_count"] == 1
        assert patch_release_review_row["actual"]["code_patch_final_release_readiness_inputs_satisfied_count"] == 0
        assert patch_release_review_row["actual"]["code_patch_final_release_readiness_record_valid_count"] == 0
        assert patch_release_review_row["actual"]["allowed_code_patch_final_release_readiness_observed_count"] == 0
        assert patch_release_review_row["actual"]["no_forbidden_code_patch_final_release_readiness_claims_count"] == 0
        assert patch_release_review_row["actual"]["code_patch_release_review_inputs_satisfied_count"] == 0
        assert patch_release_review_row["actual"]["code_patch_release_review_record_present_count"] == 0
        assert patch_release_review_row["actual"]["record_schema_matches_count"] == 0
        assert patch_release_review_row["actual"]["code_patch_release_review_scope_matches_count"] == 0
        assert patch_release_review_row["actual"]["explicit_code_patch_release_review_authorized_count"] == 0
        assert patch_release_review_row["actual"]["release_review_status_passed_count"] == 0
        assert patch_release_review_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert patch_release_review_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert patch_release_review_row["actual"]["allowed_code_patch_release_review_observed_count"] == 0
        assert patch_release_review_row["actual"]["no_forbidden_code_patch_release_review_claims_count"] == 0
        assert patch_release_review_row["actual"]["code_patch_release_review_record_valid_count"] == 0
        assert patch_release_review_row["actual"]["code_patch_release_review_record_rejected_count"] == 0
        assert patch_release_review_row["actual"]["unsafe_code_patch_release_review_record_count"] == 0
        assert patch_release_review_row["actual"]["missing_code_patch_release_review_prerequisite_count"] == 14
        assert patch_release_review_row["actual"]["reported_allowed_code_patch_release_review_count"] == 0
        assert patch_release_review_row["actual"]["reported_forbidden_code_patch_release_review_count"] == 0
        assert patch_release_review_row["actual"]["durable_executor_code_patch_release_review_started_count"] == 0
        assert patch_release_review_row["actual"]["durable_executor_code_patch_release_review_accepted_count"] == 0
        assert patch_release_review_row["actual"]["durable_executor_code_patch_release_decision_started_count"] == 0
        assert patch_release_review_row["actual"]["code_change_performed_count"] == 0
        assert patch_release_review_row["actual"]["executor_code_modified_count"] == 0
        assert patch_release_review_row["actual"]["unreal_asset_modified_count"] == 0
        assert patch_release_review_row["actual"]["live_bridge_probe_started_count"] == 0
        assert patch_release_review_row["actual"]["durable_authoring_enabled_count"] == 0
        assert patch_release_review_row["actual"]["durable_authoring_allowed_count"] == 0
        assert patch_release_review_row["actual"]["asset_write_performed_count"] == 0
        assert patch_release_review_row["actual"]["package_dirty_marked_count"] == 0
        assert patch_release_review_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert patch_release_review_row["actual"]["cleanup_allowed_count"] == 0
        assert patch_release_review_row["actual"]["live_command_dispatched_count"] == 0
        assert patch_release_review_row["actual"]["live_command_executed_count"] == 0
        patch_release_decision_row = find_row(
            report, "durable_executor_code_patch_release_decision_contract"
        )
        assert patch_release_decision_row["status"] == "passed"
        assert patch_release_decision_row["actual"]["durable_requested_executor_code_patch_release_decision_count"] == 1
        assert patch_release_decision_row["actual"]["code_patch_release_decision_contract_defined_count"] == 1
        assert patch_release_decision_row["actual"]["code_patch_release_review_contract_ready_count"] == 1
        assert patch_release_decision_row["actual"]["code_patch_release_review_inputs_satisfied_count"] == 0
        assert patch_release_decision_row["actual"]["code_patch_release_review_record_valid_count"] == 0
        assert patch_release_decision_row["actual"]["allowed_code_patch_release_review_observed_count"] == 0
        assert patch_release_decision_row["actual"]["no_forbidden_code_patch_release_review_claims_count"] == 0
        assert patch_release_decision_row["actual"]["code_patch_release_decision_inputs_satisfied_count"] == 0
        assert patch_release_decision_row["actual"]["code_patch_release_decision_record_present_count"] == 0
        assert patch_release_decision_row["actual"]["record_schema_matches_count"] == 0
        assert patch_release_decision_row["actual"]["code_patch_release_decision_scope_matches_count"] == 0
        assert patch_release_decision_row["actual"]["explicit_code_patch_release_decision_authorized_count"] == 0
        assert patch_release_decision_row["actual"]["release_decision_status_passed_count"] == 0
        assert patch_release_decision_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert patch_release_decision_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert patch_release_decision_row["actual"]["allowed_code_patch_release_decision_observed_count"] == 0
        assert patch_release_decision_row["actual"]["no_forbidden_code_patch_release_decision_claims_count"] == 0
        assert patch_release_decision_row["actual"]["code_patch_release_decision_record_valid_count"] == 0
        assert patch_release_decision_row["actual"]["code_patch_release_decision_record_rejected_count"] == 0
        assert patch_release_decision_row["actual"]["unsafe_code_patch_release_decision_record_count"] == 0
        assert patch_release_decision_row["actual"]["missing_code_patch_release_decision_prerequisite_count"] == 14
        assert patch_release_decision_row["actual"]["reported_allowed_code_patch_release_decision_count"] == 0
        assert patch_release_decision_row["actual"]["reported_forbidden_code_patch_release_decision_count"] == 0
        assert patch_release_decision_row["actual"]["durable_executor_code_patch_release_decision_started_count"] == 0
        assert patch_release_decision_row["actual"]["durable_executor_code_patch_release_decision_accepted_count"] == 0
        assert patch_release_decision_row["actual"]["durable_executor_release_promotion_barrier_started_count"] == 0
        assert patch_release_decision_row["actual"]["code_change_performed_count"] == 0
        assert patch_release_decision_row["actual"]["executor_code_modified_count"] == 0
        assert patch_release_decision_row["actual"]["unreal_asset_modified_count"] == 0
        assert patch_release_decision_row["actual"]["live_bridge_probe_started_count"] == 0
        assert patch_release_decision_row["actual"]["durable_authoring_enabled_count"] == 0
        assert patch_release_decision_row["actual"]["durable_authoring_allowed_count"] == 0
        assert patch_release_decision_row["actual"]["asset_write_performed_count"] == 0
        assert patch_release_decision_row["actual"]["package_dirty_marked_count"] == 0
        assert patch_release_decision_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert patch_release_decision_row["actual"]["cleanup_allowed_count"] == 0
        assert patch_release_decision_row["actual"]["live_command_dispatched_count"] == 0
        assert patch_release_decision_row["actual"]["live_command_executed_count"] == 0
        promotion_barrier_row = find_row(
            report, "durable_executor_release_promotion_barrier_contract"
        )
        assert promotion_barrier_row["status"] == "passed"
        assert promotion_barrier_row["actual"]["durable_requested_executor_release_promotion_barrier_count"] == 1
        assert promotion_barrier_row["actual"]["release_promotion_barrier_contract_defined_count"] == 1
        assert promotion_barrier_row["actual"]["code_patch_release_decision_contract_ready_count"] == 1
        assert promotion_barrier_row["actual"]["code_patch_release_decision_inputs_satisfied_count"] == 0
        assert promotion_barrier_row["actual"]["code_patch_release_decision_record_valid_count"] == 0
        assert promotion_barrier_row["actual"]["allowed_code_patch_release_decision_observed_count"] == 0
        assert promotion_barrier_row["actual"]["no_forbidden_code_patch_release_decision_claims_count"] == 0
        assert promotion_barrier_row["actual"]["release_promotion_barrier_inputs_satisfied_count"] == 0
        assert promotion_barrier_row["actual"]["release_promotion_barrier_record_present_count"] == 0
        assert promotion_barrier_row["actual"]["record_schema_matches_count"] == 0
        assert promotion_barrier_row["actual"]["release_promotion_barrier_scope_matches_count"] == 0
        assert promotion_barrier_row["actual"]["explicit_release_promotion_barrier_authorized_count"] == 0
        assert promotion_barrier_row["actual"]["promotion_barrier_status_passed_count"] == 0
        assert promotion_barrier_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert promotion_barrier_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert promotion_barrier_row["actual"]["allowed_release_promotion_barrier_observed_count"] == 0
        assert promotion_barrier_row["actual"]["no_forbidden_release_promotion_barrier_claims_count"] == 0
        assert promotion_barrier_row["actual"]["release_promotion_barrier_record_valid_count"] == 0
        assert promotion_barrier_row["actual"]["release_promotion_barrier_record_rejected_count"] == 0
        assert promotion_barrier_row["actual"]["unsafe_release_promotion_barrier_record_count"] == 0
        assert promotion_barrier_row["actual"]["missing_release_promotion_barrier_prerequisite_count"] == 14
        assert promotion_barrier_row["actual"]["reported_allowed_release_promotion_barrier_count"] == 0
        assert promotion_barrier_row["actual"]["reported_forbidden_release_promotion_barrier_count"] == 0
        assert promotion_barrier_row["actual"]["durable_executor_release_promotion_barrier_started_count"] == 0
        assert promotion_barrier_row["actual"]["durable_executor_release_promotion_barrier_accepted_count"] == 0
        assert promotion_barrier_row["actual"]["durable_executor_activation_readiness_started_count"] == 0
        assert promotion_barrier_row["actual"]["durable_executor_activated_count"] == 0
        assert promotion_barrier_row["actual"]["durable_executor_opened_count"] == 0
        assert promotion_barrier_row["actual"]["code_change_performed_count"] == 0
        assert promotion_barrier_row["actual"]["executor_code_modified_count"] == 0
        assert promotion_barrier_row["actual"]["unreal_asset_modified_count"] == 0
        assert promotion_barrier_row["actual"]["live_bridge_probe_started_count"] == 0
        assert promotion_barrier_row["actual"]["durable_authoring_enabled_count"] == 0
        assert promotion_barrier_row["actual"]["durable_authoring_allowed_count"] == 0
        assert promotion_barrier_row["actual"]["asset_write_performed_count"] == 0
        assert promotion_barrier_row["actual"]["package_dirty_marked_count"] == 0
        assert promotion_barrier_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert promotion_barrier_row["actual"]["cleanup_allowed_count"] == 0
        assert promotion_barrier_row["actual"]["live_command_dispatched_count"] == 0
        assert promotion_barrier_row["actual"]["live_command_executed_count"] == 0
        activation_readiness_row = find_row(
            report, "durable_executor_activation_readiness_contract"
        )
        assert activation_readiness_row["status"] == "passed"
        assert activation_readiness_row["actual"]["durable_requested_executor_activation_readiness_count"] == 1
        assert activation_readiness_row["actual"]["activation_readiness_contract_defined_count"] == 1
        assert activation_readiness_row["actual"]["release_promotion_barrier_contract_ready_count"] == 1
        assert activation_readiness_row["actual"]["release_promotion_barrier_inputs_satisfied_count"] == 0
        assert activation_readiness_row["actual"]["release_promotion_barrier_record_valid_count"] == 0
        assert activation_readiness_row["actual"]["allowed_release_promotion_barrier_observed_count"] == 0
        assert activation_readiness_row["actual"]["no_forbidden_release_promotion_barrier_claims_count"] == 0
        assert activation_readiness_row["actual"]["activation_readiness_inputs_satisfied_count"] == 0
        assert activation_readiness_row["actual"]["activation_readiness_record_present_count"] == 0
        assert activation_readiness_row["actual"]["record_schema_matches_count"] == 0
        assert activation_readiness_row["actual"]["activation_readiness_scope_matches_count"] == 0
        assert activation_readiness_row["actual"]["explicit_activation_readiness_authorized_count"] == 0
        assert activation_readiness_row["actual"]["activation_readiness_status_passed_count"] == 0
        assert activation_readiness_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert activation_readiness_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert activation_readiness_row["actual"]["allowed_activation_readiness_observed_count"] == 0
        assert activation_readiness_row["actual"]["no_forbidden_activation_readiness_claims_count"] == 0
        assert activation_readiness_row["actual"]["activation_readiness_record_valid_count"] == 0
        assert activation_readiness_row["actual"]["activation_readiness_record_rejected_count"] == 0
        assert activation_readiness_row["actual"]["unsafe_activation_readiness_record_count"] == 0
        assert activation_readiness_row["actual"]["missing_activation_readiness_prerequisite_count"] == 14
        assert activation_readiness_row["actual"]["reported_allowed_activation_readiness_count"] == 0
        assert activation_readiness_row["actual"]["reported_forbidden_activation_readiness_count"] == 0
        assert activation_readiness_row["actual"]["durable_executor_activation_readiness_started_count"] == 0
        assert activation_readiness_row["actual"]["durable_executor_activation_readiness_accepted_count"] == 0
        assert activation_readiness_row["actual"]["durable_executor_open_contract_started_count"] == 0
        assert activation_readiness_row["actual"]["durable_executor_activated_count"] == 0
        assert activation_readiness_row["actual"]["durable_executor_opened_count"] == 0
        assert activation_readiness_row["actual"]["code_change_performed_count"] == 0
        assert activation_readiness_row["actual"]["executor_code_modified_count"] == 0
        assert activation_readiness_row["actual"]["unreal_asset_modified_count"] == 0
        assert activation_readiness_row["actual"]["live_bridge_probe_started_count"] == 0
        assert activation_readiness_row["actual"]["durable_authoring_enabled_count"] == 0
        assert activation_readiness_row["actual"]["durable_authoring_allowed_count"] == 0
        assert activation_readiness_row["actual"]["asset_write_performed_count"] == 0
        assert activation_readiness_row["actual"]["package_dirty_marked_count"] == 0
        assert activation_readiness_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert activation_readiness_row["actual"]["cleanup_allowed_count"] == 0
        assert activation_readiness_row["actual"]["live_command_dispatched_count"] == 0
        assert activation_readiness_row["actual"]["live_command_executed_count"] == 0
        executor_open_row = find_row(report, "durable_executor_open_contract")
        assert executor_open_row["status"] == "passed"
        assert executor_open_row["actual"]["durable_requested_executor_open_count"] == 1
        assert executor_open_row["actual"]["open_contract_defined_count"] == 1
        assert executor_open_row["actual"]["activation_readiness_contract_ready_count"] == 1
        assert executor_open_row["actual"]["activation_readiness_inputs_satisfied_count"] == 0
        assert executor_open_row["actual"]["activation_readiness_record_valid_count"] == 0
        assert executor_open_row["actual"]["allowed_activation_readiness_observed_count"] == 0
        assert executor_open_row["actual"]["no_forbidden_activation_readiness_claims_count"] == 0
        assert executor_open_row["actual"]["open_inputs_satisfied_count"] == 0
        assert executor_open_row["actual"]["open_record_present_count"] == 0
        assert executor_open_row["actual"]["record_schema_matches_count"] == 0
        assert executor_open_row["actual"]["open_scope_matches_count"] == 0
        assert executor_open_row["actual"]["explicit_open_authorized_count"] == 0
        assert executor_open_row["actual"]["open_status_passed_count"] == 0
        assert executor_open_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_open_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_open_row["actual"]["allowed_open_observed_count"] == 0
        assert executor_open_row["actual"]["no_forbidden_open_claims_count"] == 0
        assert executor_open_row["actual"]["open_record_valid_count"] == 0
        assert executor_open_row["actual"]["open_record_rejected_count"] == 0
        assert executor_open_row["actual"]["unsafe_open_record_count"] == 0
        assert executor_open_row["actual"]["missing_open_prerequisite_count"] == 14
        assert executor_open_row["actual"]["reported_allowed_open_count"] == 0
        assert executor_open_row["actual"]["reported_forbidden_open_count"] == 0
        assert executor_open_row["actual"]["durable_executor_open_contract_started_count"] == 0
        assert executor_open_row["actual"]["durable_executor_open_contract_accepted_count"] == 0
        assert executor_open_row["actual"]["durable_executor_open_performed_count"] == 0
        assert executor_open_row["actual"]["durable_executor_activated_count"] == 0
        assert executor_open_row["actual"]["durable_executor_opened_count"] == 0
        assert executor_open_row["actual"]["durable_authoring_enable_started_count"] == 0
        assert executor_open_row["actual"]["code_change_performed_count"] == 0
        assert executor_open_row["actual"]["executor_code_modified_count"] == 0
        assert executor_open_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_open_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_open_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_open_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_open_row["actual"]["asset_write_performed_count"] == 0
        assert executor_open_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_open_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_open_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_open_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_open_row["actual"]["live_command_executed_count"] == 0
        executor_authoring_enable_row = find_row(
            report, "durable_executor_authoring_enable_contract"
        )
        assert executor_authoring_enable_row["status"] == "passed"
        assert executor_authoring_enable_row["actual"]["durable_requested_executor_authoring_enable_count"] == 1
        assert executor_authoring_enable_row["actual"]["authoring_enable_contract_defined_count"] == 1
        assert executor_authoring_enable_row["actual"]["executor_open_contract_ready_count"] == 1
        assert executor_authoring_enable_row["actual"]["open_inputs_satisfied_count"] == 0
        assert executor_authoring_enable_row["actual"]["open_record_valid_count"] == 0
        assert executor_authoring_enable_row["actual"]["allowed_open_observed_count"] == 0
        assert executor_authoring_enable_row["actual"]["no_forbidden_open_claims_count"] == 0
        assert executor_authoring_enable_row["actual"]["authoring_enable_inputs_satisfied_count"] == 0
        assert executor_authoring_enable_row["actual"]["authoring_enable_record_present_count"] == 0
        assert executor_authoring_enable_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_enable_row["actual"]["enable_scope_matches_count"] == 0
        assert executor_authoring_enable_row["actual"]["explicit_authoring_enable_authorized_count"] == 0
        assert executor_authoring_enable_row["actual"]["authoring_enable_status_passed_count"] == 0
        assert executor_authoring_enable_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_enable_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_enable_row["actual"]["target_package_allowlist_reconfirmed_count"] == 0
        assert executor_authoring_enable_row["actual"]["overwrite_rename_decision_reconfirmed_count"] == 0
        assert executor_authoring_enable_row["actual"]["rollback_readiness_reconfirmed_count"] == 0
        assert executor_authoring_enable_row["actual"]["ownership_marker_reconfirmed_count"] == 0
        assert executor_authoring_enable_row["actual"]["allowed_authoring_enable_observed_count"] == 0
        assert executor_authoring_enable_row["actual"]["no_forbidden_authoring_enable_claims_count"] == 0
        assert executor_authoring_enable_row["actual"]["authoring_enable_record_valid_count"] == 0
        assert executor_authoring_enable_row["actual"]["authoring_enable_record_rejected_count"] == 0
        assert executor_authoring_enable_row["actual"]["unsafe_authoring_enable_record_count"] == 0
        assert executor_authoring_enable_row["actual"]["missing_authoring_enable_prerequisite_count"] == 18
        assert executor_authoring_enable_row["actual"]["reported_allowed_authoring_enable_count"] == 0
        assert executor_authoring_enable_row["actual"]["reported_forbidden_authoring_enable_count"] == 0
        assert executor_authoring_enable_row["actual"]["durable_authoring_enable_started_count"] == 0
        assert executor_authoring_enable_row["actual"]["durable_authoring_enable_accepted_count"] == 0
        assert executor_authoring_enable_row["actual"]["durable_authoring_enable_allowed_count"] == 0
        assert executor_authoring_enable_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_enable_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_enable_row["actual"]["durable_authoring_command_contract_started_count"] == 0
        assert executor_authoring_enable_row["actual"]["durable_executor_open_performed_count"] == 0
        assert executor_authoring_enable_row["actual"]["durable_executor_opened_count"] == 0
        assert executor_authoring_enable_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_enable_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_enable_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_enable_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_enable_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_enable_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_enable_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_enable_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_enable_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_enable_row["actual"]["live_command_executed_count"] == 0
        executor_authoring_command_row = find_row(
            report, "durable_executor_authoring_command_contract"
        )
        assert executor_authoring_command_row["status"] == "passed"
        assert executor_authoring_command_row["actual"]["durable_requested_executor_authoring_command_count"] == 1
        assert executor_authoring_command_row["actual"]["authoring_command_contract_defined_count"] == 1
        assert executor_authoring_command_row["actual"]["authoring_enable_contract_ready_count"] == 1
        assert executor_authoring_command_row["actual"]["authoring_enable_inputs_satisfied_count"] == 0
        assert executor_authoring_command_row["actual"]["authoring_enable_record_valid_count"] == 0
        assert executor_authoring_command_row["actual"]["allowed_authoring_enable_observed_count"] == 0
        assert executor_authoring_command_row["actual"]["no_forbidden_authoring_enable_claims_count"] == 0
        assert executor_authoring_command_row["actual"]["target_package_allowlist_reconfirmed_count"] == 0
        assert executor_authoring_command_row["actual"]["overwrite_rename_decision_reconfirmed_count"] == 0
        assert executor_authoring_command_row["actual"]["rollback_readiness_reconfirmed_count"] == 0
        assert executor_authoring_command_row["actual"]["ownership_marker_reconfirmed_count"] == 0
        assert executor_authoring_command_row["actual"]["authoring_command_inputs_satisfied_count"] == 0
        assert executor_authoring_command_row["actual"]["authoring_command_record_present_count"] == 0
        assert executor_authoring_command_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_command_row["actual"]["command_scope_matches_count"] == 0
        assert executor_authoring_command_row["actual"]["explicit_authoring_command_authorized_count"] == 0
        assert executor_authoring_command_row["actual"]["command_status_passed_count"] == 0
        assert executor_authoring_command_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_command_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_command_row["actual"]["planned_authoring_command_count"] == 0
        assert executor_authoring_command_row["actual"]["allowed_authoring_command_count"] == 0
        assert executor_authoring_command_row["actual"]["forbidden_authoring_command_count"] == 0
        assert executor_authoring_command_row["actual"]["unknown_authoring_command_count"] == 0
        assert executor_authoring_command_row["actual"]["authoring_command_record_valid_count"] == 0
        assert executor_authoring_command_row["actual"]["authoring_command_record_rejected_count"] == 0
        assert executor_authoring_command_row["actual"]["unsafe_authoring_command_record_count"] == 0
        assert executor_authoring_command_row["actual"]["missing_authoring_command_prerequisite_count"] == 17
        assert executor_authoring_command_row["actual"]["durable_authoring_command_contract_started_count"] == 0
        assert executor_authoring_command_row["actual"]["durable_authoring_command_contract_accepted_count"] == 0
        assert executor_authoring_command_row["actual"]["durable_authoring_command_allowed_count"] == 0
        assert executor_authoring_command_row["actual"]["durable_authoring_command_dispatched_count"] == 0
        assert executor_authoring_command_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert executor_authoring_command_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_command_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_command_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_command_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_command_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_command_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_command_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_command_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_command_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_command_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_command_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_command_row["actual"]["live_command_executed_count"] == 0
        executor_authoring_dispatch_row = find_row(
            report, "durable_executor_authoring_command_dispatch_contract"
        )
        assert executor_authoring_dispatch_row["status"] == "passed"
        assert executor_authoring_dispatch_row["actual"]["durable_requested_executor_authoring_command_dispatch_count"] == 1
        assert executor_authoring_dispatch_row["actual"]["dispatch_contract_defined_count"] == 1
        assert executor_authoring_dispatch_row["actual"]["authoring_command_contract_ready_count"] == 1
        assert executor_authoring_dispatch_row["actual"]["authoring_command_inputs_satisfied_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["authoring_command_record_valid_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["planned_authoring_commands_present_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["allowed_authoring_commands_present_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["dispatch_inputs_satisfied_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["dispatch_record_present_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["dispatch_scope_matches_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["explicit_dispatch_authorized_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["dispatch_status_passed_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["allowed_dispatch_observed_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["no_forbidden_dispatch_claims_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["dispatch_record_valid_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["dispatch_record_rejected_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["unsafe_dispatch_record_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["missing_dispatch_prerequisite_count"] == 14
        assert executor_authoring_dispatch_row["actual"]["reported_allowed_dispatch_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["reported_forbidden_dispatch_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["durable_authoring_command_dispatch_started_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["durable_authoring_command_dispatch_accepted_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["durable_authoring_command_dispatch_allowed_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["durable_authoring_command_dispatched_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["durable_authoring_command_execution_contract_started_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_dispatch_row["actual"]["live_command_executed_count"] == 0
        executor_authoring_execution_row = find_row(
            report, "durable_executor_authoring_command_execution_contract"
        )
        assert executor_authoring_execution_row["status"] == "passed"
        assert executor_authoring_execution_row["actual"]["durable_requested_executor_authoring_command_execution_count"] == 1
        assert executor_authoring_execution_row["actual"]["execution_contract_defined_count"] == 1
        assert executor_authoring_execution_row["actual"]["dispatch_contract_ready_count"] == 1
        assert executor_authoring_execution_row["actual"]["dispatch_inputs_satisfied_count"] == 0
        assert executor_authoring_execution_row["actual"]["dispatch_record_valid_count"] == 0
        assert executor_authoring_execution_row["actual"]["planned_authoring_commands_present_count"] == 0
        assert executor_authoring_execution_row["actual"]["allowed_authoring_commands_present_count"] == 0
        assert executor_authoring_execution_row["actual"]["allowed_dispatch_observed_count"] == 0
        assert executor_authoring_execution_row["actual"]["no_forbidden_dispatch_claims_count"] == 0
        assert executor_authoring_execution_row["actual"]["execution_inputs_satisfied_count"] == 0
        assert executor_authoring_execution_row["actual"]["execution_record_present_count"] == 0
        assert executor_authoring_execution_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_execution_row["actual"]["execution_scope_matches_count"] == 0
        assert executor_authoring_execution_row["actual"]["explicit_execution_authorized_count"] == 0
        assert executor_authoring_execution_row["actual"]["execution_status_passed_count"] == 0
        assert executor_authoring_execution_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_execution_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_execution_row["actual"]["allowed_execution_observed_count"] == 0
        assert executor_authoring_execution_row["actual"]["no_forbidden_execution_claims_count"] == 0
        assert executor_authoring_execution_row["actual"]["execution_record_valid_count"] == 0
        assert executor_authoring_execution_row["actual"]["execution_record_rejected_count"] == 0
        assert executor_authoring_execution_row["actual"]["unsafe_execution_record_count"] == 0
        assert executor_authoring_execution_row["actual"]["missing_execution_prerequisite_count"] == 16
        assert executor_authoring_execution_row["actual"]["reported_allowed_execution_count"] == 0
        assert executor_authoring_execution_row["actual"]["reported_forbidden_execution_count"] == 0
        assert executor_authoring_execution_row["actual"]["durable_authoring_command_execution_started_count"] == 0
        assert executor_authoring_execution_row["actual"]["durable_authoring_command_execution_accepted_count"] == 0
        assert executor_authoring_execution_row["actual"]["durable_authoring_command_execution_allowed_count"] == 0
        assert executor_authoring_execution_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert executor_authoring_execution_row["actual"]["durable_authoring_command_execution_evidence_contract_started_count"] == 0
        assert executor_authoring_execution_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_execution_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_execution_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_execution_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_execution_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_execution_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_execution_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_execution_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_execution_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_execution_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_execution_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_execution_row["actual"]["live_command_executed_count"] == 0
        executor_authoring_execution_evidence_row = find_row(
            report, "durable_executor_authoring_command_execution_evidence_contract"
        )
        assert executor_authoring_execution_evidence_row["status"] == "passed"
        assert (
            executor_authoring_execution_evidence_row["actual"][
                "durable_requested_executor_authoring_command_execution_evidence_count"
            ]
            == 1
        )
        assert executor_authoring_execution_evidence_row["actual"]["evidence_contract_defined_count"] == 1
        assert executor_authoring_execution_evidence_row["actual"]["execution_contract_ready_count"] == 1
        assert executor_authoring_execution_evidence_row["actual"]["execution_inputs_satisfied_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["execution_record_valid_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["planned_authoring_commands_present_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["allowed_authoring_commands_present_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["allowed_execution_observed_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["no_forbidden_execution_claims_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["evidence_inputs_satisfied_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["evidence_record_present_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["evidence_scope_matches_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["explicit_evidence_authorized_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["evidence_status_passed_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["allowed_evidence_command_observed_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["no_forbidden_evidence_commands_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["authoring_command_execution_evidence_admitted_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["evidence_record_rejected_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["unsafe_evidence_record_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["missing_evidence_prerequisite_count"] == 16
        assert executor_authoring_execution_evidence_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        assert (
            executor_authoring_execution_evidence_row["actual"][
                "durable_authoring_command_completion_decision_started_count"
            ]
            == 0
        )
        assert executor_authoring_execution_evidence_row["actual"]["durable_authoring_command_execution_allowed_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["live_command_executed_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["reported_authoring_create_command_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["reported_authoring_compile_command_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["reported_authoring_marker_write_command_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["reported_authoring_marker_readback_command_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["reported_authoring_read_only_exists_check_command_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["reported_authoring_save_command_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["reported_authoring_delete_rename_command_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["reported_authoring_cleanup_command_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["reported_authoring_duplicate_replace_command_count"] == 0
        assert executor_authoring_execution_evidence_row["actual"]["reported_authoring_live_dispatch_execution_command_count"] == 0
        executor_authoring_completion_decision_row = find_row(
            report, "durable_executor_authoring_command_completion_decision_contract"
        )
        assert executor_authoring_completion_decision_row["status"] == "passed"
        assert (
            executor_authoring_completion_decision_row["actual"][
                "durable_requested_executor_authoring_command_completion_decision_count"
            ]
            == 1
        )
        assert executor_authoring_completion_decision_row["actual"]["completion_decision_contract_defined_count"] == 1
        assert executor_authoring_completion_decision_row["actual"]["evidence_contract_ready_count"] == 1
        assert executor_authoring_completion_decision_row["actual"]["authoring_command_execution_evidence_admitted_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["allowed_evidence_command_observed_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["no_forbidden_evidence_commands_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["evidence_ready_for_completion_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["decision_record_present_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["completion_scope_matches_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["explicit_completion_decision_authorized_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["completion_decision_status_passed_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["completion_decision_record_valid_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["completion_decision_record_rejected_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["unsafe_completion_decision_record_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["missing_completion_prerequisite_count"] == 11
        assert executor_authoring_completion_decision_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["durable_authoring_command_completion_allowed_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert (
            executor_authoring_completion_decision_row["actual"][
                "durable_authoring_command_completion_application_started_count"
            ]
            == 0
        )
        assert executor_authoring_completion_decision_row["actual"]["durable_authoring_command_dispatch_allowed_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["durable_authoring_command_dispatched_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["durable_authoring_command_execution_allowed_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_completion_decision_row["actual"]["live_command_executed_count"] == 0
        executor_authoring_completion_application_row = find_row(
            report, "durable_executor_authoring_command_completion_application_contract"
        )
        assert executor_authoring_completion_application_row["status"] == "passed"
        assert (
            executor_authoring_completion_application_row["actual"][
                "durable_requested_executor_authoring_command_completion_application_count"
            ]
            == 1
        )
        assert executor_authoring_completion_application_row["actual"]["application_contract_defined_count"] == 1
        assert executor_authoring_completion_application_row["actual"]["completion_decision_contract_ready_count"] == 1
        assert executor_authoring_completion_application_row["actual"]["evidence_ready_for_completion_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["completion_decision_record_valid_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["application_inputs_satisfied_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["application_record_present_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["application_scope_matches_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["explicit_application_authorized_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["application_status_passed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["application_record_valid_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["application_record_rejected_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["unsafe_application_record_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["missing_application_prerequisite_count"] == 10
        assert executor_authoring_completion_application_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["durable_authoring_command_completion_allowed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["durable_authoring_command_application_allowed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["durable_authoring_command_application_applied_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["asset_write_allowed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["durable_authoring_command_dispatch_allowed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["durable_authoring_command_dispatched_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["durable_authoring_command_execution_allowed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_completion_application_row["actual"]["live_command_executed_count"] == 0
        executor_authoring_completion_result_row = find_row(
            report, "durable_executor_authoring_command_completion_result_contract"
        )
        assert executor_authoring_completion_result_row["status"] == "passed"
        assert (
            executor_authoring_completion_result_row["actual"][
                "durable_requested_executor_authoring_command_completion_result_count"
            ]
            == 1
        )
        assert executor_authoring_completion_result_row["actual"]["result_contract_defined_count"] == 1
        assert executor_authoring_completion_result_row["actual"]["application_contract_ready_count"] == 1
        assert executor_authoring_completion_result_row["actual"]["application_inputs_satisfied_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["application_record_valid_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["result_inputs_satisfied_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["result_record_present_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["result_scope_matches_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["explicit_result_authorized_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["result_status_passed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["allowed_result_observed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["no_forbidden_results_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["result_record_valid_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["result_record_rejected_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["unsafe_result_record_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["missing_result_prerequisite_count"] == 12
        assert executor_authoring_completion_result_row["actual"]["reported_allowed_result_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_forbidden_result_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_allowed_evidence_command_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_forbidden_evidence_command_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["durable_authoring_command_completion_result_accepted_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["durable_authoring_command_completion_allowed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["durable_authoring_command_application_allowed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["durable_authoring_command_application_applied_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["asset_write_allowed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["durable_authoring_command_dispatch_allowed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["durable_authoring_command_dispatched_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["durable_authoring_command_execution_allowed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["live_command_executed_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_completion_noop_result_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_application_validation_result_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_completion_completed_result_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_asset_write_result_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_package_dirty_result_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_save_result_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_delete_rename_result_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_cleanup_result_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_code_change_result_count"] == 0
        assert executor_authoring_completion_result_row["actual"]["reported_live_command_result_count"] == 0
        executor_authoring_result_readback_row = find_row(
            report, "durable_executor_authoring_command_result_readback_contract"
        )
        assert executor_authoring_result_readback_row["status"] == "passed"
        assert (
            executor_authoring_result_readback_row["actual"][
                "durable_requested_executor_authoring_command_result_readback_count"
            ]
            == 1
        )
        assert executor_authoring_result_readback_row["actual"]["readback_contract_defined_count"] == 1
        assert executor_authoring_result_readback_row["actual"]["result_contract_ready_count"] == 1
        assert executor_authoring_result_readback_row["actual"]["result_inputs_satisfied_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["result_record_valid_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["allowed_result_observed_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["no_forbidden_results_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["readback_inputs_satisfied_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["readback_record_present_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["readback_scope_matches_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["explicit_readback_authorized_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["readback_status_passed_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["allowed_readback_observed_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["no_forbidden_readbacks_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["readback_record_valid_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["readback_record_rejected_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["unsafe_readback_record_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["missing_readback_prerequisite_count"] == 14
        assert executor_authoring_result_readback_row["actual"]["reported_allowed_readback_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["reported_forbidden_readback_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["durable_authoring_command_result_readback_accepted_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["durable_authoring_command_completion_result_accepted_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["live_command_executed_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["reported_no_completion_readback_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["reported_no_write_readback_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["reported_no_save_readback_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["reported_completed_readback_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["reported_asset_write_readback_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["reported_package_dirty_readback_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["reported_save_readback_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["reported_delete_rename_readback_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["reported_cleanup_readback_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["reported_code_change_readback_count"] == 0
        assert executor_authoring_result_readback_row["actual"]["reported_live_command_readback_count"] == 0
        executor_authoring_final_no_save_release_row = find_row(
            report, "durable_executor_authoring_final_no_save_release_contract"
        )
        assert executor_authoring_final_no_save_release_row["status"] == "passed"
        assert (
            executor_authoring_final_no_save_release_row["actual"][
                "durable_requested_executor_authoring_final_no_save_release_count"
            ]
            == 1
        )
        assert executor_authoring_final_no_save_release_row["actual"]["final_no_save_release_contract_defined_count"] == 1
        assert executor_authoring_final_no_save_release_row["actual"]["readback_contract_ready_count"] == 1
        assert executor_authoring_final_no_save_release_row["actual"]["readback_inputs_satisfied_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["readback_record_valid_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["allowed_readback_observed_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["no_forbidden_readbacks_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["final_no_save_release_inputs_satisfied_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["final_no_save_release_record_present_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["final_no_save_release_scope_matches_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["explicit_final_no_save_release_authorized_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["final_no_save_release_status_passed_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["allowed_final_no_save_release_observed_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["no_forbidden_final_no_save_releases_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["final_no_save_release_record_valid_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["final_no_save_release_record_rejected_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["unsafe_final_no_save_release_record_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["missing_final_no_save_release_prerequisite_count"] == 14
        assert executor_authoring_final_no_save_release_row["actual"]["reported_allowed_final_no_save_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_forbidden_final_no_save_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["durable_authoring_final_no_save_release_accepted_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["durable_authoring_final_release_readiness_started_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["durable_authoring_command_result_readback_accepted_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["durable_authoring_command_completion_result_accepted_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["live_command_executed_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_no_completion_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_no_write_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_no_save_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_readback_revalidated_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_no_code_change_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_no_live_command_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_completion_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_asset_write_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_package_dirty_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_save_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_delete_rename_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_cleanup_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_durable_authoring_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_code_change_release_count"] == 0
        assert executor_authoring_final_no_save_release_row["actual"]["reported_live_command_release_count"] == 0
        executor_authoring_final_release_readiness_row = find_row(
            report, "durable_executor_authoring_final_release_readiness_contract"
        )
        assert executor_authoring_final_release_readiness_row["status"] == "passed"
        assert (
            executor_authoring_final_release_readiness_row["actual"][
                "durable_requested_executor_authoring_final_release_readiness_count"
            ]
            == 1
        )
        assert executor_authoring_final_release_readiness_row["actual"]["final_release_readiness_contract_defined_count"] == 1
        assert executor_authoring_final_release_readiness_row["actual"]["final_no_save_release_contract_ready_count"] == 1
        assert executor_authoring_final_release_readiness_row["actual"]["final_no_save_release_inputs_satisfied_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["final_no_save_release_record_valid_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["allowed_final_no_save_release_observed_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["no_forbidden_final_no_save_releases_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["final_release_readiness_inputs_satisfied_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["final_release_readiness_record_present_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["readiness_scope_matches_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["explicit_readiness_authorized_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["readiness_status_passed_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["allowed_final_release_readiness_observed_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["no_forbidden_final_release_readiness_claims_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["final_release_readiness_record_valid_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["final_release_readiness_record_rejected_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["unsafe_final_release_readiness_record_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["missing_final_release_readiness_prerequisite_count"] == 14
        assert executor_authoring_final_release_readiness_row["actual"]["reported_allowed_final_release_readiness_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_forbidden_final_release_readiness_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["durable_authoring_final_release_readiness_started_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["durable_authoring_final_release_ready_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["durable_authoring_release_review_started_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["durable_authoring_final_no_save_release_accepted_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["durable_authoring_command_result_readback_accepted_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["durable_authoring_command_completion_result_accepted_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["live_command_executed_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_final_release_readiness_gate_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_final_no_save_release_revalidated_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_durable_authoring_still_disabled_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_no_completion_readiness_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_no_write_readiness_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_no_save_readiness_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_no_code_change_readiness_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_no_live_command_readiness_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_final_no_save_release_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_command_result_readback_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_completion_result_acceptance_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_completion_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_asset_write_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_package_dirty_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_save_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_delete_rename_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_cleanup_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_durable_authoring_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_code_change_count"] == 0
        assert executor_authoring_final_release_readiness_row["actual"]["reported_live_command_count"] == 0
        executor_authoring_release_review_row = find_row(
            report, "durable_executor_authoring_release_review_contract"
        )
        assert executor_authoring_release_review_row["status"] == "passed"
        assert (
            executor_authoring_release_review_row["actual"][
                "durable_requested_executor_authoring_release_review_count"
            ]
            == 1
        )
        assert executor_authoring_release_review_row["actual"]["release_review_contract_defined_count"] == 1
        assert executor_authoring_release_review_row["actual"]["final_release_readiness_contract_ready_count"] == 1
        assert executor_authoring_release_review_row["actual"]["final_release_readiness_inputs_satisfied_count"] == 0
        assert executor_authoring_release_review_row["actual"]["final_release_readiness_record_valid_count"] == 0
        assert executor_authoring_release_review_row["actual"]["allowed_final_release_readiness_observed_count"] == 0
        assert executor_authoring_release_review_row["actual"]["no_forbidden_final_release_readiness_claims_count"] == 0
        assert executor_authoring_release_review_row["actual"]["release_review_inputs_satisfied_count"] == 0
        assert executor_authoring_release_review_row["actual"]["release_review_record_present_count"] == 0
        assert executor_authoring_release_review_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_release_review_row["actual"]["release_review_scope_matches_count"] == 0
        assert executor_authoring_release_review_row["actual"]["explicit_release_review_authorized_count"] == 0
        assert executor_authoring_release_review_row["actual"]["release_review_status_passed_count"] == 0
        assert executor_authoring_release_review_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_release_review_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_release_review_row["actual"]["allowed_release_review_observed_count"] == 0
        assert executor_authoring_release_review_row["actual"]["no_forbidden_release_review_claims_count"] == 0
        assert executor_authoring_release_review_row["actual"]["release_review_record_valid_count"] == 0
        assert executor_authoring_release_review_row["actual"]["release_review_record_rejected_count"] == 0
        assert executor_authoring_release_review_row["actual"]["unsafe_release_review_record_count"] == 0
        assert executor_authoring_release_review_row["actual"]["missing_release_review_prerequisite_count"] == 14
        assert executor_authoring_release_review_row["actual"]["reported_allowed_release_review_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_forbidden_release_review_count"] == 0
        assert executor_authoring_release_review_row["actual"]["durable_authoring_release_review_started_count"] == 0
        assert executor_authoring_release_review_row["actual"]["durable_authoring_release_review_accepted_count"] == 0
        assert executor_authoring_release_review_row["actual"]["durable_authoring_release_decision_started_count"] == 0
        assert executor_authoring_release_review_row["actual"]["durable_authoring_final_release_readiness_started_count"] == 0
        assert executor_authoring_release_review_row["actual"]["durable_authoring_final_release_ready_count"] == 0
        assert executor_authoring_release_review_row["actual"]["durable_authoring_final_no_save_release_accepted_count"] == 0
        assert executor_authoring_release_review_row["actual"]["durable_authoring_command_result_readback_accepted_count"] == 0
        assert executor_authoring_release_review_row["actual"]["durable_authoring_command_completion_result_accepted_count"] == 0
        assert executor_authoring_release_review_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert executor_authoring_release_review_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_release_review_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_release_review_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_release_review_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_release_review_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_release_review_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_release_review_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_release_review_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_release_review_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_release_review_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_release_review_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_release_review_row["actual"]["live_command_executed_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_release_review_gate_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_final_release_readiness_revalidated_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_durable_authoring_still_disabled_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_no_completion_release_review_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_no_write_release_review_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_no_save_release_review_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_no_code_change_release_review_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_no_live_command_release_review_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_final_release_readiness_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_final_no_save_release_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_command_result_readback_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_completion_result_acceptance_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_completion_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_asset_write_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_package_dirty_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_save_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_delete_rename_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_cleanup_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_durable_authoring_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_code_change_count"] == 0
        assert executor_authoring_release_review_row["actual"]["reported_live_command_count"] == 0
        executor_authoring_release_decision_row = find_row(
            report, "durable_executor_authoring_release_decision_contract"
        )
        assert executor_authoring_release_decision_row["status"] == "passed"
        assert (
            executor_authoring_release_decision_row["actual"][
                "durable_requested_executor_authoring_release_decision_count"
            ]
            == 1
        )
        assert executor_authoring_release_decision_row["actual"]["release_decision_contract_defined_count"] == 1
        assert executor_authoring_release_decision_row["actual"]["release_review_contract_ready_count"] == 1
        assert executor_authoring_release_decision_row["actual"]["release_review_inputs_satisfied_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["release_review_record_valid_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["allowed_release_review_observed_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["no_forbidden_release_review_claims_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["release_decision_inputs_satisfied_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["release_decision_record_present_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["release_decision_scope_matches_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["explicit_release_decision_authorized_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["release_decision_status_passed_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["allowed_release_decision_observed_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["no_forbidden_release_decision_claims_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["release_decision_record_valid_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["release_decision_record_rejected_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["unsafe_release_decision_record_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["missing_release_decision_prerequisite_count"] == 14
        assert executor_authoring_release_decision_row["actual"]["reported_allowed_release_decision_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_forbidden_release_decision_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_release_decision_started_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_release_decision_accepted_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_release_promotion_barrier_started_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_release_review_started_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_release_review_accepted_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_final_release_readiness_started_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_final_release_ready_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_final_no_save_release_accepted_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_command_result_readback_accepted_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_command_completion_result_accepted_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["live_command_executed_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_release_decision_gate_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_release_review_revalidated_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_durable_authoring_still_disabled_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_no_completion_release_decision_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_no_write_release_decision_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_no_save_release_decision_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_no_code_change_release_decision_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_no_live_command_release_decision_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_release_review_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_final_release_readiness_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_final_no_save_release_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_command_result_readback_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_completion_result_acceptance_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_completion_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_asset_write_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_package_dirty_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_save_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_delete_rename_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_cleanup_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_durable_authoring_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_code_change_count"] == 0
        assert executor_authoring_release_decision_row["actual"]["reported_live_command_count"] == 0
        executor_authoring_release_promotion_barrier_row = find_row(
            report, "durable_executor_authoring_release_promotion_barrier_contract"
        )
        assert executor_authoring_release_promotion_barrier_row["status"] == "passed"
        assert (
            executor_authoring_release_promotion_barrier_row["actual"][
                "durable_requested_executor_authoring_release_promotion_barrier_count"
            ]
            == 1
        )
        assert executor_authoring_release_promotion_barrier_row["actual"]["release_promotion_barrier_contract_defined_count"] == 1
        assert executor_authoring_release_promotion_barrier_row["actual"]["release_decision_contract_ready_count"] == 1
        assert executor_authoring_release_promotion_barrier_row["actual"]["release_decision_inputs_satisfied_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["release_decision_record_valid_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["allowed_release_decision_observed_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["no_forbidden_release_decision_claims_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["release_promotion_barrier_inputs_satisfied_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["release_promotion_barrier_record_present_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["release_promotion_barrier_scope_matches_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["explicit_release_promotion_barrier_authorized_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["promotion_barrier_status_passed_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["allowed_release_promotion_barrier_observed_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["no_forbidden_release_promotion_barrier_claims_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["release_promotion_barrier_record_valid_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["release_promotion_barrier_record_rejected_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["unsafe_release_promotion_barrier_record_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["missing_release_promotion_barrier_prerequisite_count"] == 14
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_allowed_release_promotion_barrier_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_forbidden_release_promotion_barrier_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_release_promotion_barrier_started_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_release_promotion_barrier_accepted_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_executor_activation_readiness_started_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_executor_activated_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_executor_opened_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_release_decision_started_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_release_decision_accepted_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_release_review_started_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_release_review_accepted_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_final_release_readiness_started_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_final_release_ready_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_final_no_save_release_accepted_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_command_result_readback_accepted_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_command_completion_result_accepted_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["live_command_executed_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_promotion_barrier_gate_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_release_decision_revalidated_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_durable_authoring_still_disabled_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_no_completion_promotion_barrier_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_no_write_promotion_barrier_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_no_save_promotion_barrier_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_no_code_change_promotion_barrier_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_no_live_command_promotion_barrier_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_release_decision_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_release_review_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_final_release_readiness_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_final_no_save_release_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_command_result_readback_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_completion_result_acceptance_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_completion_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_executor_activation_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_executor_open_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_asset_write_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_package_dirty_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_save_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_delete_rename_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_cleanup_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_durable_authoring_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_code_change_count"] == 0
        assert executor_authoring_release_promotion_barrier_row["actual"]["reported_live_command_count"] == 0
        executor_authoring_activation_readiness_row = find_row(
            report, "durable_executor_authoring_activation_readiness_contract"
        )
        assert executor_authoring_activation_readiness_row["status"] == "passed"
        assert (
            executor_authoring_activation_readiness_row["actual"][
                "durable_requested_executor_authoring_activation_readiness_count"
            ]
            == 1
        )
        assert executor_authoring_activation_readiness_row["actual"]["activation_readiness_contract_defined_count"] == 1
        assert executor_authoring_activation_readiness_row["actual"]["release_promotion_barrier_contract_ready_count"] == 1
        assert executor_authoring_activation_readiness_row["actual"]["release_promotion_barrier_inputs_satisfied_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["release_promotion_barrier_record_valid_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["allowed_release_promotion_barrier_observed_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["no_forbidden_release_promotion_barrier_claims_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["activation_readiness_inputs_satisfied_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["activation_readiness_record_present_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["activation_readiness_scope_matches_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["explicit_activation_readiness_authorized_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["activation_readiness_status_passed_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["allowed_activation_readiness_observed_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["no_forbidden_activation_readiness_claims_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["activation_readiness_record_valid_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["activation_readiness_record_rejected_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["unsafe_activation_readiness_record_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["missing_activation_readiness_prerequisite_count"] == 14
        assert executor_authoring_activation_readiness_row["actual"]["reported_allowed_activation_readiness_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_forbidden_activation_readiness_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_release_promotion_barrier_started_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_release_promotion_barrier_accepted_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_executor_activation_readiness_started_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_executor_activation_readiness_accepted_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_executor_open_contract_started_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_executor_activated_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_executor_opened_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_release_decision_started_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_release_decision_accepted_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_release_review_started_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_release_review_accepted_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_final_release_readiness_started_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_final_release_ready_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_final_no_save_release_accepted_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_command_result_readback_accepted_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_command_completion_result_accepted_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["live_command_executed_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_activation_readiness_gate_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_promotion_barrier_revalidated_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_release_decision_revalidated_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_durable_authoring_still_disabled_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_no_completion_activation_readiness_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_no_write_activation_readiness_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_no_save_activation_readiness_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_no_code_change_activation_readiness_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_no_live_command_activation_readiness_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_release_promotion_barrier_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_release_decision_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_release_review_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_final_release_readiness_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_final_no_save_release_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_command_result_readback_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_completion_result_acceptance_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_completion_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_executor_activation_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_executor_open_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_asset_write_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_package_dirty_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_save_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_delete_rename_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_cleanup_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_durable_authoring_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_code_change_count"] == 0
        assert executor_authoring_activation_readiness_row["actual"]["reported_live_command_count"] == 0
        executor_authoring_open_row = find_row(
            report, "durable_executor_authoring_open_contract"
        )
        assert executor_authoring_open_row["status"] == "passed"
        assert (
            executor_authoring_open_row["actual"][
                "durable_requested_executor_authoring_open_count"
            ]
            == 1
        )
        assert executor_authoring_open_row["actual"]["open_contract_defined_count"] == 1
        assert executor_authoring_open_row["actual"]["activation_readiness_contract_ready_count"] == 1
        assert executor_authoring_open_row["actual"]["activation_readiness_inputs_satisfied_count"] == 0
        assert executor_authoring_open_row["actual"]["activation_readiness_record_valid_count"] == 0
        assert executor_authoring_open_row["actual"]["allowed_activation_readiness_observed_count"] == 0
        assert executor_authoring_open_row["actual"]["no_forbidden_activation_readiness_claims_count"] == 0
        assert executor_authoring_open_row["actual"]["open_inputs_satisfied_count"] == 0
        assert executor_authoring_open_row["actual"]["open_record_present_count"] == 0
        assert executor_authoring_open_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_open_row["actual"]["open_scope_matches_count"] == 0
        assert executor_authoring_open_row["actual"]["explicit_open_authorized_count"] == 0
        assert executor_authoring_open_row["actual"]["open_status_passed_count"] == 0
        assert executor_authoring_open_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_open_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_open_row["actual"]["allowed_open_observed_count"] == 0
        assert executor_authoring_open_row["actual"]["no_forbidden_open_claims_count"] == 0
        assert executor_authoring_open_row["actual"]["open_record_valid_count"] == 0
        assert executor_authoring_open_row["actual"]["open_record_rejected_count"] == 0
        assert executor_authoring_open_row["actual"]["unsafe_open_record_count"] == 0
        assert executor_authoring_open_row["actual"]["missing_open_prerequisite_count"] == 14
        assert executor_authoring_open_row["actual"]["reported_allowed_open_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_forbidden_open_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_executor_open_contract_started_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_executor_open_contract_accepted_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_executor_open_performed_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_executor_activated_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_executor_opened_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_enable_started_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_executor_activation_readiness_started_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_executor_activation_readiness_accepted_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_release_promotion_barrier_started_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_release_promotion_barrier_accepted_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_release_decision_started_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_release_decision_accepted_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_release_review_started_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_release_review_accepted_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_final_release_readiness_started_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_final_release_ready_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_final_no_save_release_accepted_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_command_result_readback_accepted_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_command_completion_result_accepted_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert executor_authoring_open_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_open_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_open_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_open_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_open_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_open_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_open_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_open_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_open_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_open_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_open_row["actual"]["live_command_executed_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_executor_open_gate_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_activation_readiness_revalidated_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_promotion_barrier_revalidated_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_durable_authoring_still_disabled_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_no_completion_open_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_no_write_open_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_no_save_open_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_no_code_change_open_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_no_live_command_open_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_activation_readiness_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_release_promotion_barrier_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_release_decision_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_release_review_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_final_release_readiness_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_final_no_save_release_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_command_result_readback_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_completion_result_acceptance_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_completion_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_executor_activation_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_executor_open_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_durable_authoring_enable_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_asset_write_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_package_dirty_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_save_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_delete_rename_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_cleanup_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_durable_authoring_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_code_change_count"] == 0
        assert executor_authoring_open_row["actual"]["reported_live_command_count"] == 0
        executor_authoring_enable_after_open_row = find_row(
            report, "durable_executor_authoring_enable_after_open_contract"
        )
        assert executor_authoring_enable_after_open_row["status"] == "passed"
        assert (
            executor_authoring_enable_after_open_row["actual"][
                "durable_requested_executor_authoring_enable_after_open_count"
            ]
            == 1
        )
        assert executor_authoring_enable_after_open_row["actual"]["authoring_enable_contract_defined_count"] == 1
        assert executor_authoring_enable_after_open_row["actual"]["executor_open_contract_ready_count"] == 1
        assert executor_authoring_enable_after_open_row["actual"]["open_inputs_satisfied_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["open_record_valid_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["allowed_open_observed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["no_forbidden_open_claims_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["authoring_enable_inputs_satisfied_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["authoring_enable_record_present_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["enable_scope_matches_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["explicit_authoring_enable_authorized_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["authoring_enable_status_passed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["target_package_allowlist_reconfirmed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["overwrite_rename_decision_reconfirmed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["rollback_readiness_reconfirmed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["ownership_marker_reconfirmed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["allowed_authoring_enable_observed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["no_forbidden_authoring_enable_claims_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["authoring_enable_record_valid_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["authoring_enable_record_rejected_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["unsafe_authoring_enable_record_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["missing_authoring_enable_prerequisite_count"] == 18
        assert executor_authoring_enable_after_open_row["actual"]["reported_allowed_authoring_enable_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_forbidden_authoring_enable_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_enable_started_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_enable_accepted_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_enable_allowed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_command_contract_started_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_executor_open_contract_started_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_executor_open_contract_accepted_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_executor_open_performed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_executor_activated_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_executor_opened_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_executor_activation_readiness_started_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_executor_activation_readiness_accepted_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_release_promotion_barrier_started_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_release_promotion_barrier_accepted_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_release_decision_started_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_release_decision_accepted_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_release_review_started_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_release_review_accepted_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_final_release_readiness_started_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_final_release_ready_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_final_no_save_release_accepted_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_command_result_readback_accepted_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_command_completion_result_accepted_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["durable_authoring_command_completed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["live_command_executed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_authoring_enable_gate_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_executor_open_revalidated_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_target_allowlist_reconfirmed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_overwrite_rename_decision_reconfirmed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_rollback_readiness_reconfirmed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_ownership_marker_reconfirmed_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_durable_authoring_still_disabled_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_no_code_change_authoring_enable_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_no_asset_change_authoring_enable_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_no_live_probe_authoring_enable_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_activation_readiness_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_release_promotion_barrier_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_release_decision_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_release_review_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_final_release_readiness_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_final_no_save_release_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_command_result_readback_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_completion_result_acceptance_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_completion_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_executor_activation_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_executor_open_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_authoring_enable_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_authoring_command_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_asset_write_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_package_dirty_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_save_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_delete_rename_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_cleanup_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_durable_authoring_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_code_change_count"] == 0
        assert executor_authoring_enable_after_open_row["actual"]["reported_live_command_count"] == 0
        executor_authoring_command_after_enable_row = find_row(
            report, "durable_executor_authoring_command_after_enable_contract"
        )
        assert executor_authoring_command_after_enable_row["status"] == "passed"
        assert (
            executor_authoring_command_after_enable_row["actual"][
                "durable_requested_executor_authoring_command_after_enable_count"
            ]
            == 1
        )
        assert executor_authoring_command_after_enable_row["actual"]["authoring_command_contract_defined_count"] == 1
        assert executor_authoring_command_after_enable_row["actual"]["authoring_enable_contract_ready_count"] == 1
        assert executor_authoring_command_after_enable_row["actual"]["authoring_enable_inputs_satisfied_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["authoring_enable_record_valid_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["allowed_authoring_enable_observed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["no_forbidden_authoring_enable_claims_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["target_package_allowlist_reconfirmed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["overwrite_rename_decision_reconfirmed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["rollback_readiness_reconfirmed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["ownership_marker_reconfirmed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["authoring_command_inputs_satisfied_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["authoring_command_record_present_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["record_schema_matches_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["command_scope_matches_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["explicit_authoring_command_authorized_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["command_status_passed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["no_save_delete_rename_acknowledged_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["explicit_durable_mvp_request_reconfirmed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["planned_authoring_command_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["allowed_authoring_command_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["forbidden_authoring_command_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["unknown_authoring_command_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["authoring_command_record_valid_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["authoring_command_record_rejected_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["unsafe_authoring_command_record_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["missing_authoring_command_prerequisite_count"] == 17
        assert executor_authoring_command_after_enable_row["actual"]["durable_authoring_command_contract_started_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["durable_authoring_command_contract_accepted_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["durable_authoring_command_allowed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["durable_authoring_command_dispatched_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["durable_authoring_command_executed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["durable_authoring_enable_started_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["durable_authoring_enable_accepted_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["durable_authoring_enable_allowed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["durable_authoring_enabled_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["durable_authoring_allowed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["durable_executor_open_performed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["durable_executor_opened_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["code_change_performed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["executor_code_modified_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["unreal_asset_modified_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["live_bridge_probe_started_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["asset_write_performed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["package_dirty_marked_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["save_delete_rename_allowed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["cleanup_allowed_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["live_command_dispatched_count"] == 0
        assert executor_authoring_command_after_enable_row["actual"]["live_command_executed_count"] == 0
        executor_authoring_command_dispatch_after_command_row = find_row(
            report,
            "durable_executor_authoring_command_dispatch_after_command_contract",
        )
        assert executor_authoring_command_dispatch_after_command_row["status"] == "passed"
        expected_dispatch_after_command_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_dispatch_after_command_count": 1,
            "dispatch_contract_defined_count": 1,
            "authoring_command_contract_ready_count": 1,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "planned_authoring_commands_present_count": 0,
            "allowed_authoring_commands_present_count": 0,
            "dispatch_inputs_satisfied_count": 0,
            "dispatch_record_present_count": 0,
            "record_schema_matches_count": 0,
            "dispatch_scope_matches_count": 0,
            "explicit_dispatch_authorized_count": 0,
            "dispatch_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_dispatch_observed_count": 0,
            "no_forbidden_dispatch_claims_count": 0,
            "dispatch_record_valid_count": 0,
            "dispatch_record_rejected_count": 0,
            "unsafe_dispatch_record_count": 0,
            "missing_dispatch_prerequisite_count": 14,
            "reported_allowed_dispatch_count": 0,
            "reported_forbidden_dispatch_count": 0,
            "durable_authoring_command_dispatch_started_count": 0,
            "durable_authoring_command_dispatch_accepted_count": 0,
            "durable_authoring_command_dispatch_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_execution_contract_started_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_command_contract_started_count": 0,
            "durable_authoring_command_contract_accepted_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "save_delete_rename_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
            "reported_dispatch_gate_count": 0,
            "reported_authoring_command_revalidated_count": 0,
            "reported_no_live_dispatch_performed_count": 0,
            "reported_no_execution_authorized_count": 0,
            "reported_no_asset_write_dispatch_count": 0,
            "reported_no_save_delete_rename_dispatch_count": 0,
            "reported_authoring_command_dispatch_count": 0,
            "reported_authoring_command_execution_count": 0,
            "reported_live_dispatch_count": 0,
            "reported_live_execution_count": 0,
            "reported_code_change_count": 0,
            "reported_executor_code_modified_count": 0,
            "reported_unreal_asset_change_count": 0,
            "reported_live_probe_count": 0,
            "reported_durable_authoring_count": 0,
            "reported_asset_write_count": 0,
            "reported_package_dirty_count": 0,
            "reported_save_count": 0,
            "reported_delete_rename_count": 0,
            "reported_cleanup_count": 0,
        }
        assert (
            executor_authoring_command_dispatch_after_command_row["actual"]
            == expected_dispatch_after_command_actual
        )
        executor_authoring_command_execution_after_dispatch_row = find_row(
            report,
            "durable_executor_authoring_command_execution_after_dispatch_contract",
        )
        assert executor_authoring_command_execution_after_dispatch_row["status"] == "passed"
        expected_execution_after_dispatch_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_execution_after_dispatch_count": 1,
            "execution_contract_defined_count": 1,
            "dispatch_contract_ready_count": 1,
            "dispatch_inputs_satisfied_count": 0,
            "dispatch_record_valid_count": 0,
            "planned_authoring_commands_present_count": 0,
            "allowed_authoring_commands_present_count": 0,
            "allowed_dispatch_observed_count": 0,
            "no_forbidden_dispatch_claims_count": 0,
            "execution_inputs_satisfied_count": 0,
            "execution_record_present_count": 0,
            "record_schema_matches_count": 0,
            "execution_scope_matches_count": 0,
            "explicit_execution_authorized_count": 0,
            "execution_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_execution_observed_count": 0,
            "no_forbidden_execution_claims_count": 0,
            "execution_record_valid_count": 0,
            "execution_record_rejected_count": 0,
            "unsafe_execution_record_count": 0,
            "missing_execution_prerequisite_count": 16,
            "reported_allowed_execution_count": 0,
            "reported_forbidden_execution_count": 0,
            "durable_authoring_command_execution_started_count": 0,
            "durable_authoring_command_execution_accepted_count": 0,
            "durable_authoring_command_execution_allowed_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_command_execution_evidence_contract_started_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "save_delete_rename_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
            "reported_execution_gate_count": 0,
            "reported_dispatch_revalidated_count": 0,
            "reported_no_live_execution_performed_count": 0,
            "reported_no_execution_evidence_admitted_count": 0,
            "reported_no_asset_write_execution_count": 0,
            "reported_no_save_delete_rename_execution_count": 0,
            "reported_authoring_command_execution_count": 0,
            "reported_execution_evidence_count": 0,
            "reported_live_execution_count": 0,
            "reported_live_dispatch_count": 0,
            "reported_code_change_count": 0,
            "reported_executor_code_modified_count": 0,
            "reported_unreal_asset_change_count": 0,
            "reported_live_probe_count": 0,
            "reported_durable_authoring_count": 0,
            "reported_asset_write_count": 0,
            "reported_package_dirty_count": 0,
            "reported_save_count": 0,
            "reported_delete_rename_count": 0,
            "reported_cleanup_count": 0,
        }
        assert (
            executor_authoring_command_execution_after_dispatch_row["actual"]
            == expected_execution_after_dispatch_actual
        )
        executor_authoring_execution_evidence_after_execution_row = find_row(
            report,
            "durable_executor_authoring_command_execution_evidence_after_execution_contract",
        )
        assert (
            executor_authoring_execution_evidence_after_execution_row["status"]
            == "passed"
        )
        expected_evidence_after_execution_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_execution_evidence_after_execution_count": 1,
            "evidence_contract_defined_count": 1,
            "execution_contract_ready_count": 1,
            "execution_inputs_satisfied_count": 0,
            "execution_record_valid_count": 0,
            "planned_authoring_commands_present_count": 0,
            "allowed_authoring_commands_present_count": 0,
            "allowed_execution_observed_count": 0,
            "no_forbidden_execution_claims_count": 0,
            "evidence_inputs_satisfied_count": 0,
            "evidence_record_present_count": 0,
            "record_schema_matches_count": 0,
            "evidence_scope_matches_count": 0,
            "explicit_evidence_authorized_count": 0,
            "evidence_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_evidence_command_observed_count": 0,
            "no_forbidden_evidence_commands_count": 0,
            "authoring_command_execution_evidence_admitted_count": 0,
            "evidence_record_rejected_count": 0,
            "unsafe_evidence_record_count": 0,
            "missing_evidence_prerequisite_count": 16,
            "reported_allowed_evidence_command_count": 0,
            "reported_forbidden_evidence_command_count": 0,
            "durable_authoring_command_completion_decision_started_count": 0,
            "durable_authoring_command_execution_allowed_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "save_delete_rename_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
            "reported_authoring_create_command_count": 0,
            "reported_authoring_compile_command_count": 0,
            "reported_authoring_marker_write_command_count": 0,
            "reported_authoring_marker_readback_command_count": 0,
            "reported_authoring_read_only_exists_check_command_count": 0,
            "reported_authoring_save_command_count": 0,
            "reported_authoring_delete_rename_command_count": 0,
            "reported_authoring_cleanup_command_count": 0,
            "reported_authoring_duplicate_replace_command_count": 0,
            "reported_authoring_live_dispatch_execution_command_count": 0,
            "reported_package_dirty_count": 0,
        }
        assert (
            executor_authoring_execution_evidence_after_execution_row["actual"]
            == expected_evidence_after_execution_actual
        )
        executor_authoring_completion_decision_after_evidence_row = find_row(
            report,
            "durable_executor_authoring_command_completion_decision_after_evidence_contract",
        )
        assert (
            executor_authoring_completion_decision_after_evidence_row["status"]
            == "passed"
        )
        expected_completion_decision_after_evidence_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_completion_decision_after_evidence_count": 1,
            "completion_decision_contract_defined_count": 1,
            "evidence_contract_ready_count": 1,
            "authoring_command_execution_evidence_admitted_count": 0,
            "allowed_evidence_command_observed_count": 0,
            "no_forbidden_evidence_commands_count": 0,
            "evidence_ready_for_completion_count": 0,
            "decision_record_present_count": 0,
            "record_schema_matches_count": 0,
            "completion_scope_matches_count": 0,
            "explicit_completion_decision_authorized_count": 0,
            "completion_decision_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "completion_decision_record_valid_count": 0,
            "completion_decision_record_rejected_count": 0,
            "unsafe_completion_decision_record_count": 0,
            "missing_completion_prerequisite_count": 11,
            "reported_allowed_evidence_command_count": 0,
            "reported_forbidden_evidence_command_count": 0,
            "durable_authoring_command_completion_allowed_count": 0,
            "durable_authoring_command_completed_count": 0,
            "durable_authoring_command_completion_application_started_count": 0,
            "durable_authoring_command_dispatch_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_execution_allowed_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "save_delete_rename_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            executor_authoring_completion_decision_after_evidence_row["actual"]
            == expected_completion_decision_after_evidence_actual
        )
        executor_authoring_completion_application_after_decision_row = find_row(
            report,
            "durable_executor_authoring_command_completion_application_after_decision_contract",
        )
        assert (
            executor_authoring_completion_application_after_decision_row["status"]
            == "passed"
        )
        expected_completion_application_after_decision_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_completion_application_after_decision_count": 1,
            "application_contract_defined_count": 1,
            "completion_decision_contract_ready_count": 1,
            "evidence_ready_for_completion_count": 0,
            "completion_decision_record_valid_count": 0,
            "application_inputs_satisfied_count": 0,
            "application_record_present_count": 0,
            "record_schema_matches_count": 0,
            "application_scope_matches_count": 0,
            "explicit_application_authorized_count": 0,
            "application_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "application_record_valid_count": 0,
            "application_record_rejected_count": 0,
            "unsafe_application_record_count": 0,
            "missing_application_prerequisite_count": 10,
            "reported_allowed_evidence_command_count": 0,
            "reported_forbidden_evidence_command_count": 0,
            "durable_authoring_command_completion_allowed_count": 0,
            "durable_authoring_command_completed_count": 0,
            "durable_authoring_command_application_allowed_count": 0,
            "durable_authoring_command_application_applied_count": 0,
            "asset_write_allowed_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "durable_authoring_command_dispatch_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_execution_allowed_count": 0,
            "durable_authoring_command_executed_count": 0,
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
        }
        assert (
            executor_authoring_completion_application_after_decision_row["actual"]
            == expected_completion_application_after_decision_actual
        )
        executor_authoring_completion_result_after_application_row = find_row(
            report,
            "durable_executor_authoring_command_completion_result_after_application_contract",
        )
        assert (
            executor_authoring_completion_result_after_application_row["status"]
            == "passed"
        )
        expected_completion_result_after_application_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_completion_result_after_application_count": 1,
            "result_contract_defined_count": 1,
            "application_contract_ready_count": 1,
            "application_inputs_satisfied_count": 0,
            "application_record_valid_count": 0,
            "result_inputs_satisfied_count": 0,
            "result_record_present_count": 0,
            "record_schema_matches_count": 0,
            "result_scope_matches_count": 0,
            "explicit_result_authorized_count": 0,
            "result_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_result_observed_count": 0,
            "no_forbidden_results_count": 0,
            "result_record_valid_count": 0,
            "result_record_rejected_count": 0,
            "unsafe_result_record_count": 0,
            "missing_result_prerequisite_count": 12,
            "reported_allowed_result_count": 0,
            "reported_forbidden_result_count": 0,
            "reported_allowed_evidence_command_count": 0,
            "reported_forbidden_evidence_command_count": 0,
            "durable_authoring_command_completion_result_accepted_count": 0,
            "durable_authoring_command_completion_allowed_count": 0,
            "durable_authoring_command_completed_count": 0,
            "durable_authoring_command_application_allowed_count": 0,
            "durable_authoring_command_application_applied_count": 0,
            "asset_write_allowed_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "durable_authoring_command_dispatch_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_execution_allowed_count": 0,
            "durable_authoring_command_executed_count": 0,
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
            "reported_completion_noop_result_count": 0,
            "reported_application_validation_result_count": 0,
            "reported_completion_completed_result_count": 0,
            "reported_asset_write_result_count": 0,
            "reported_package_dirty_result_count": 0,
            "reported_save_result_count": 0,
            "reported_delete_rename_result_count": 0,
            "reported_cleanup_result_count": 0,
            "reported_code_change_result_count": 0,
            "reported_live_command_result_count": 0,
        }
        assert (
            executor_authoring_completion_result_after_application_row["actual"]
            == expected_completion_result_after_application_actual
        )
        executor_authoring_result_readback_after_result_row = find_row(
            report,
            "durable_executor_authoring_command_result_readback_after_result_contract",
        )
        assert executor_authoring_result_readback_after_result_row["status"] == "passed"
        expected_result_readback_after_result_actual = {
            "summary_status": "passed",
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
        assert (
            executor_authoring_result_readback_after_result_row["actual"]
            == expected_result_readback_after_result_actual
        )
        executor_authoring_final_no_save_release_after_readback_row = find_row(
            report,
            "durable_executor_authoring_final_no_save_release_after_readback_contract",
        )
        assert (
            executor_authoring_final_no_save_release_after_readback_row["status"]
            == "passed"
        )
        expected_final_no_save_release_after_readback_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_final_no_save_release_after_readback_count": 1,
            "final_no_save_release_contract_defined_count": 1,
            "readback_contract_ready_count": 1,
            "readback_inputs_satisfied_count": 0,
            "readback_record_valid_count": 0,
            "allowed_readback_observed_count": 0,
            "no_forbidden_readbacks_count": 0,
            "final_no_save_release_inputs_satisfied_count": 0,
            "final_no_save_release_record_present_count": 0,
            "record_schema_matches_count": 0,
            "final_no_save_release_scope_matches_count": 0,
            "explicit_final_no_save_release_authorized_count": 0,
            "final_no_save_release_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_final_no_save_release_observed_count": 0,
            "no_forbidden_final_no_save_releases_count": 0,
            "final_no_save_release_record_valid_count": 0,
            "final_no_save_release_record_rejected_count": 0,
            "unsafe_final_no_save_release_record_count": 0,
            "missing_final_no_save_release_prerequisite_count": 14,
            "reported_allowed_final_no_save_release_count": 0,
            "reported_forbidden_final_no_save_release_count": 0,
            "durable_authoring_final_no_save_release_accepted_count": 0,
            "durable_authoring_final_release_readiness_started_count": 0,
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
            "reported_no_completion_release_count": 0,
            "reported_no_write_release_count": 0,
            "reported_no_save_release_count": 0,
            "reported_readback_revalidated_count": 0,
            "reported_no_code_change_release_count": 0,
            "reported_no_live_command_release_count": 0,
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
        assert (
            executor_authoring_final_no_save_release_after_readback_row["actual"]
            == expected_final_no_save_release_after_readback_actual
        )
        executor_authoring_final_release_readiness_after_no_save_release_row = find_row(
            report,
            "durable_executor_authoring_final_release_readiness_after_no_save_release_contract",
        )
        assert (
            executor_authoring_final_release_readiness_after_no_save_release_row["status"]
            == "passed"
        )
        expected_final_release_readiness_after_no_save_release_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_final_release_readiness_after_no_save_release_count": 1,
            "final_release_readiness_contract_defined_count": 1,
            "final_no_save_release_contract_ready_count": 1,
            "final_no_save_release_inputs_satisfied_count": 0,
            "final_no_save_release_record_valid_count": 0,
            "allowed_final_no_save_release_observed_count": 0,
            "no_forbidden_final_no_save_releases_count": 0,
            "final_release_readiness_inputs_satisfied_count": 0,
            "final_release_readiness_record_present_count": 0,
            "record_schema_matches_count": 0,
            "readiness_scope_matches_count": 0,
            "explicit_readiness_authorized_count": 0,
            "readiness_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_final_release_readiness_observed_count": 0,
            "no_forbidden_final_release_readiness_claims_count": 0,
            "final_release_readiness_record_valid_count": 0,
            "final_release_readiness_record_rejected_count": 0,
            "unsafe_final_release_readiness_record_count": 0,
            "missing_final_release_readiness_prerequisite_count": 14,
            "reported_allowed_final_release_readiness_count": 0,
            "reported_forbidden_final_release_readiness_count": 0,
            "durable_authoring_final_release_readiness_started_count": 0,
            "durable_authoring_final_release_ready_count": 0,
            "durable_authoring_release_review_started_count": 0,
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
            "reported_final_release_readiness_gate_count": 0,
            "reported_final_no_save_release_revalidated_count": 0,
            "reported_durable_authoring_still_disabled_count": 0,
            "reported_no_completion_readiness_count": 0,
            "reported_no_write_readiness_count": 0,
            "reported_no_save_readiness_count": 0,
            "reported_no_code_change_readiness_count": 0,
            "reported_no_live_command_readiness_count": 0,
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
        assert (
            executor_authoring_final_release_readiness_after_no_save_release_row[
                "actual"
            ]
            == expected_final_release_readiness_after_no_save_release_actual
        )
        executor_authoring_release_review_after_readiness_row = find_row(
            report,
            "durable_executor_authoring_release_review_after_readiness_contract",
        )
        assert executor_authoring_release_review_after_readiness_row["status"] == "passed"
        expected_release_review_after_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_release_review_after_readiness_count": 1,
            "release_review_contract_defined_count": 1,
            "final_release_readiness_contract_ready_count": 1,
            "final_release_readiness_inputs_satisfied_count": 0,
            "final_release_readiness_record_valid_count": 0,
            "allowed_final_release_readiness_observed_count": 0,
            "no_forbidden_final_release_readiness_claims_count": 0,
            "release_review_inputs_satisfied_count": 0,
            "release_review_record_present_count": 0,
            "record_schema_matches_count": 0,
            "release_review_scope_matches_count": 0,
            "explicit_release_review_authorized_count": 0,
            "release_review_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_release_review_observed_count": 0,
            "no_forbidden_release_review_claims_count": 0,
            "release_review_record_valid_count": 0,
            "release_review_record_rejected_count": 0,
            "unsafe_release_review_record_count": 0,
            "missing_release_review_prerequisite_count": 14,
            "reported_allowed_release_review_count": 0,
            "reported_forbidden_release_review_count": 0,
            "durable_authoring_release_review_started_count": 0,
            "durable_authoring_release_review_accepted_count": 0,
            "durable_authoring_release_decision_started_count": 0,
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
            "reported_release_review_gate_count": 0,
            "reported_final_release_readiness_revalidated_count": 0,
            "reported_durable_authoring_still_disabled_count": 0,
            "reported_no_completion_release_review_count": 0,
            "reported_no_write_release_review_count": 0,
            "reported_no_save_release_review_count": 0,
            "reported_no_code_change_release_review_count": 0,
            "reported_no_live_command_release_review_count": 0,
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
        assert (
            executor_authoring_release_review_after_readiness_row["actual"]
            == expected_release_review_after_readiness_actual
        )
        executor_authoring_release_decision_after_review_row = find_row(
            report,
            "durable_executor_authoring_release_decision_after_review_contract",
        )
        assert executor_authoring_release_decision_after_review_row["status"] == "passed"
        expected_release_decision_after_review_actual = {
            "summary_status": "passed",
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
        assert (
            executor_authoring_release_decision_after_review_row["actual"]
            == expected_release_decision_after_review_actual
        )
        executor_authoring_release_promotion_barrier_after_decision_row = find_row(
            report,
            "durable_executor_authoring_release_promotion_barrier_after_decision_contract",
        )
        assert (
            executor_authoring_release_promotion_barrier_after_decision_row["status"]
            == "passed"
        )
        expected_release_promotion_barrier_after_decision_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_release_promotion_barrier_after_decision_count": 1,
            "release_promotion_barrier_contract_defined_count": 1,
            "release_decision_contract_ready_count": 1,
            "release_decision_inputs_satisfied_count": 0,
            "release_decision_record_valid_count": 0,
            "allowed_release_decision_observed_count": 0,
            "no_forbidden_release_decision_claims_count": 0,
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
            "durable_authoring_release_promotion_barrier_started_count": 0,
            "durable_authoring_release_promotion_barrier_accepted_count": 0,
            "durable_executor_activation_readiness_started_count": 0,
            "durable_executor_activated_count": 0,
            "durable_executor_opened_count": 0,
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
            "reported_promotion_barrier_gate_count": 0,
            "reported_release_decision_revalidated_count": 0,
            "reported_durable_authoring_still_disabled_count": 0,
            "reported_no_completion_promotion_barrier_count": 0,
            "reported_no_write_promotion_barrier_count": 0,
            "reported_no_save_promotion_barrier_count": 0,
            "reported_no_code_change_promotion_barrier_count": 0,
            "reported_no_live_command_promotion_barrier_count": 0,
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
        assert (
            executor_authoring_release_promotion_barrier_after_decision_row["actual"]
            == expected_release_promotion_barrier_after_decision_actual
        )
        executor_authoring_activation_readiness_after_promotion_barrier_row = find_row(
            report,
            "durable_executor_authoring_activation_readiness_after_promotion_barrier_contract",
        )
        assert (
            executor_authoring_activation_readiness_after_promotion_barrier_row["status"]
            == "passed"
        )
        expected_activation_readiness_after_promotion_barrier_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_activation_readiness_after_promotion_barrier_count": 1,
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
            "durable_authoring_release_promotion_barrier_started_count": 0,
            "durable_authoring_release_promotion_barrier_accepted_count": 0,
            "durable_executor_activation_readiness_started_count": 0,
            "durable_executor_activation_readiness_accepted_count": 0,
            "durable_executor_open_contract_started_count": 0,
            "durable_executor_activated_count": 0,
            "durable_executor_opened_count": 0,
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
            "reported_activation_readiness_gate_count": 0,
            "reported_promotion_barrier_revalidated_count": 0,
            "reported_release_decision_revalidated_count": 0,
            "reported_durable_authoring_still_disabled_count": 0,
            "reported_no_completion_activation_readiness_count": 0,
            "reported_no_write_activation_readiness_count": 0,
            "reported_no_save_activation_readiness_count": 0,
            "reported_no_code_change_activation_readiness_count": 0,
            "reported_no_live_command_activation_readiness_count": 0,
            "reported_release_promotion_barrier_count": 0,
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
        assert (
            executor_authoring_activation_readiness_after_promotion_barrier_row[
                "actual"
            ]
            == expected_activation_readiness_after_promotion_barrier_actual
        )
        executor_authoring_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_open_after_activation_readiness_contract",
        )
        assert executor_authoring_open_after_activation_readiness_row["status"] == "passed"
        expected_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_open_after_activation_readiness_count": 1,
            "open_contract_defined_count": 1,
            "activation_readiness_contract_ready_count": 1,
            "activation_readiness_inputs_satisfied_count": 0,
            "activation_readiness_record_valid_count": 0,
            "allowed_activation_readiness_observed_count": 0,
            "no_forbidden_activation_readiness_claims_count": 0,
            "open_inputs_satisfied_count": 0,
            "open_record_present_count": 0,
            "record_schema_matches_count": 0,
            "open_scope_matches_count": 0,
            "explicit_open_authorized_count": 0,
            "open_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_open_observed_count": 0,
            "no_forbidden_open_claims_count": 0,
            "open_record_valid_count": 0,
            "open_record_rejected_count": 0,
            "unsafe_open_record_count": 0,
            "missing_open_prerequisite_count": 14,
            "reported_allowed_open_count": 0,
            "reported_forbidden_open_count": 0,
            "durable_executor_open_contract_started_count": 0,
            "durable_executor_open_contract_accepted_count": 0,
            "durable_executor_open_performed_count": 0,
            "durable_executor_activated_count": 0,
            "durable_executor_opened_count": 0,
            "durable_authoring_enable_started_count": 0,
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
            "reported_executor_open_gate_count": 0,
            "reported_activation_readiness_revalidated_count": 0,
            "reported_promotion_barrier_revalidated_count": 0,
            "reported_durable_authoring_still_disabled_count": 0,
            "reported_no_completion_open_count": 0,
            "reported_no_write_open_count": 0,
            "reported_no_save_open_count": 0,
            "reported_no_code_change_open_count": 0,
            "reported_no_live_command_open_count": 0,
            "reported_activation_readiness_count": 0,
            "reported_release_promotion_barrier_count": 0,
            "reported_release_decision_count": 0,
            "reported_release_review_count": 0,
            "reported_final_release_readiness_count": 0,
            "reported_final_no_save_release_count": 0,
            "reported_command_result_readback_count": 0,
            "reported_completion_result_acceptance_count": 0,
            "reported_completion_count": 0,
            "reported_executor_activation_count": 0,
            "reported_executor_open_count": 0,
            "reported_durable_authoring_enable_count": 0,
            "reported_asset_write_count": 0,
            "reported_package_dirty_count": 0,
            "reported_save_count": 0,
            "reported_delete_rename_count": 0,
            "reported_cleanup_count": 0,
            "reported_durable_authoring_count": 0,
            "reported_code_change_count": 0,
            "reported_live_command_count": 0,
        }
        assert (
            executor_authoring_open_after_activation_readiness_row["actual"]
            == expected_open_after_activation_readiness_actual
        )
        executor_authoring_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_enable_after_open_after_activation_readiness_row["status"]
            == "passed"
        )
        expected_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_enable_after_open_after_activation_readiness_count": 1,
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
            "reported_authoring_enable_gate_count": 0,
            "reported_executor_open_revalidated_count": 0,
            "reported_target_allowlist_reconfirmed_count": 0,
            "reported_overwrite_rename_decision_reconfirmed_count": 0,
            "reported_rollback_readiness_reconfirmed_count": 0,
            "reported_ownership_marker_reconfirmed_count": 0,
            "reported_durable_authoring_still_disabled_count": 0,
            "reported_no_code_change_authoring_enable_count": 0,
            "reported_no_asset_change_authoring_enable_count": 0,
            "reported_no_live_probe_authoring_enable_count": 0,
            "reported_activation_readiness_count": 0,
            "reported_release_promotion_barrier_count": 0,
            "reported_release_decision_count": 0,
            "reported_release_review_count": 0,
            "reported_final_release_readiness_count": 0,
            "reported_final_no_save_release_count": 0,
            "reported_command_result_readback_count": 0,
            "reported_completion_result_acceptance_count": 0,
            "reported_completion_count": 0,
            "reported_executor_activation_count": 0,
            "reported_executor_open_count": 0,
            "reported_authoring_enable_count": 0,
            "reported_authoring_command_count": 0,
            "reported_asset_write_count": 0,
            "reported_package_dirty_count": 0,
            "reported_save_count": 0,
            "reported_delete_rename_count": 0,
            "reported_cleanup_count": 0,
            "reported_durable_authoring_count": 0,
            "reported_code_change_count": 0,
            "reported_live_command_count": 0,
        }
        assert (
            executor_authoring_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_after_enable_after_open_after_activation_readiness_count": 1,
            "authoring_command_contract_defined_count": 1,
            "authoring_enable_contract_ready_count": 1,
            "authoring_enable_inputs_satisfied_count": 0,
            "authoring_enable_record_valid_count": 0,
            "allowed_authoring_enable_observed_count": 0,
            "no_forbidden_authoring_enable_claims_count": 0,
            "target_package_allowlist_reconfirmed_count": 0,
            "overwrite_rename_decision_reconfirmed_count": 0,
            "rollback_readiness_reconfirmed_count": 0,
            "ownership_marker_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_present_count": 0,
            "record_schema_matches_count": 0,
            "command_scope_matches_count": 0,
            "explicit_authoring_command_authorized_count": 0,
            "command_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "planned_authoring_command_count": 0,
            "allowed_authoring_command_count": 0,
            "forbidden_authoring_command_count": 0,
            "unknown_authoring_command_count": 0,
            "authoring_command_record_valid_count": 0,
            "authoring_command_record_rejected_count": 0,
            "unsafe_authoring_command_record_count": 0,
            "missing_authoring_command_prerequisite_count": 17,
            "durable_authoring_command_contract_started_count": 0,
            "durable_authoring_command_contract_accepted_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_enable_started_count": 0,
            "durable_authoring_enable_accepted_count": 0,
            "durable_authoring_enable_allowed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "durable_executor_open_performed_count": 0,
            "durable_executor_opened_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "save_delete_rename_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            executor_authoring_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
            "dispatch_contract_defined_count": 1,
            "authoring_command_contract_ready_count": 1,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "planned_authoring_commands_present_count": 0,
            "allowed_authoring_commands_present_count": 0,
            "dispatch_inputs_satisfied_count": 0,
            "dispatch_record_present_count": 0,
            "record_schema_matches_count": 0,
            "dispatch_scope_matches_count": 0,
            "explicit_dispatch_authorized_count": 0,
            "dispatch_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_dispatch_observed_count": 0,
            "no_forbidden_dispatch_claims_count": 0,
            "dispatch_record_valid_count": 0,
            "dispatch_record_rejected_count": 0,
            "unsafe_dispatch_record_count": 0,
            "missing_dispatch_prerequisite_count": 14,
            "reported_allowed_dispatch_count": 0,
            "reported_forbidden_dispatch_count": 0,
            "durable_authoring_command_dispatch_started_count": 0,
            "durable_authoring_command_dispatch_accepted_count": 0,
            "durable_authoring_command_dispatch_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_execution_contract_started_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_command_contract_started_count": 0,
            "durable_authoring_command_contract_accepted_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "save_delete_rename_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
            "reported_dispatch_gate_count": 0,
            "reported_authoring_command_revalidated_count": 0,
            "reported_no_live_dispatch_performed_count": 0,
            "reported_no_execution_authorized_count": 0,
            "reported_no_asset_write_dispatch_count": 0,
            "reported_no_save_delete_rename_dispatch_count": 0,
            "reported_authoring_command_dispatch_count": 0,
            "reported_authoring_command_execution_count": 0,
            "reported_live_dispatch_count": 0,
            "reported_live_execution_count": 0,
            "reported_code_change_count": 0,
            "reported_executor_code_modified_count": 0,
            "reported_unreal_asset_change_count": 0,
            "reported_live_probe_count": 0,
            "reported_durable_authoring_count": 0,
            "reported_asset_write_count": 0,
            "reported_package_dirty_count": 0,
            "reported_save_count": 0,
            "reported_delete_rename_count": 0,
            "reported_cleanup_count": 0,
        }
        assert (
            executor_authoring_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_command_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
            "execution_contract_defined_count": 1,
            "dispatch_contract_ready_count": 1,
            "dispatch_inputs_satisfied_count": 0,
            "dispatch_record_valid_count": 0,
            "planned_authoring_commands_present_count": 0,
            "allowed_authoring_commands_present_count": 0,
            "allowed_dispatch_observed_count": 0,
            "no_forbidden_dispatch_claims_count": 0,
            "execution_inputs_satisfied_count": 0,
            "execution_record_present_count": 0,
            "record_schema_matches_count": 0,
            "execution_scope_matches_count": 0,
            "explicit_execution_authorized_count": 0,
            "execution_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_execution_observed_count": 0,
            "no_forbidden_execution_claims_count": 0,
            "execution_record_valid_count": 0,
            "execution_record_rejected_count": 0,
            "unsafe_execution_record_count": 0,
            "missing_execution_prerequisite_count": 16,
            "reported_allowed_execution_count": 0,
            "reported_forbidden_execution_count": 0,
            "durable_authoring_command_execution_started_count": 0,
            "durable_authoring_command_execution_accepted_count": 0,
            "durable_authoring_command_execution_allowed_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_command_execution_evidence_contract_started_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "save_delete_rename_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
            "reported_execution_gate_count": 0,
            "reported_dispatch_revalidated_count": 0,
            "reported_no_live_execution_performed_count": 0,
            "reported_no_execution_evidence_admitted_count": 0,
            "reported_no_asset_write_execution_count": 0,
            "reported_no_save_delete_rename_execution_count": 0,
            "reported_authoring_command_execution_count": 0,
            "reported_execution_evidence_count": 0,
            "reported_live_execution_count": 0,
            "reported_live_dispatch_count": 0,
            "reported_code_change_count": 0,
            "reported_executor_code_modified_count": 0,
            "reported_unreal_asset_change_count": 0,
            "reported_live_probe_count": 0,
            "reported_durable_authoring_count": 0,
            "reported_asset_write_count": 0,
            "reported_package_dirty_count": 0,
            "reported_save_count": 0,
            "reported_delete_rename_count": 0,
            "reported_cleanup_count": 0,
        }
        assert (
            executor_authoring_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_command_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
            "evidence_contract_defined_count": 1,
            "execution_contract_ready_count": 1,
            "execution_inputs_satisfied_count": 0,
            "execution_record_valid_count": 0,
            "planned_authoring_commands_present_count": 0,
            "allowed_authoring_commands_present_count": 0,
            "allowed_execution_observed_count": 0,
            "no_forbidden_execution_claims_count": 0,
            "evidence_inputs_satisfied_count": 0,
            "evidence_record_present_count": 0,
            "record_schema_matches_count": 0,
            "evidence_scope_matches_count": 0,
            "explicit_evidence_authorized_count": 0,
            "evidence_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_evidence_command_observed_count": 0,
            "no_forbidden_evidence_commands_count": 0,
            "authoring_command_execution_evidence_admitted_count": 0,
            "evidence_record_rejected_count": 0,
            "unsafe_evidence_record_count": 0,
            "missing_evidence_prerequisite_count": 16,
            "reported_allowed_evidence_command_count": 0,
            "reported_forbidden_evidence_command_count": 0,
            "durable_authoring_command_completion_decision_started_count": 0,
            "durable_authoring_command_execution_allowed_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "save_delete_rename_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
            "reported_authoring_create_command_count": 0,
            "reported_authoring_compile_command_count": 0,
            "reported_authoring_marker_write_command_count": 0,
            "reported_authoring_marker_readback_command_count": 0,
            "reported_authoring_read_only_exists_check_command_count": 0,
            "reported_authoring_save_command_count": 0,
            "reported_authoring_delete_rename_command_count": 0,
            "reported_authoring_cleanup_command_count": 0,
            "reported_authoring_duplicate_replace_command_count": 0,
            "reported_authoring_live_dispatch_execution_command_count": 0,
            "reported_package_dirty_count": 0,
        }
        assert (
            executor_authoring_execution_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
            "completion_decision_contract_defined_count": 1,
            "evidence_contract_ready_count": 1,
            "authoring_command_execution_evidence_admitted_count": 0,
            "allowed_evidence_command_observed_count": 0,
            "no_forbidden_evidence_commands_count": 0,
            "evidence_ready_for_completion_count": 0,
            "decision_record_present_count": 0,
            "record_schema_matches_count": 0,
            "completion_scope_matches_count": 0,
            "explicit_completion_decision_authorized_count": 0,
            "completion_decision_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "completion_decision_record_valid_count": 0,
            "completion_decision_record_rejected_count": 0,
            "unsafe_completion_decision_record_count": 0,
            "missing_completion_prerequisite_count": 11,
            "reported_allowed_evidence_command_count": 0,
            "reported_forbidden_evidence_command_count": 0,
            "durable_authoring_command_completion_allowed_count": 0,
            "durable_authoring_command_completed_count": 0,
            "durable_authoring_command_completion_application_started_count": 0,
            "durable_authoring_command_dispatch_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_execution_allowed_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "save_delete_rename_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            executor_authoring_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
            "application_contract_defined_count": 1,
            "completion_decision_contract_ready_count": 1,
            "evidence_ready_for_completion_count": 0,
            "completion_decision_record_valid_count": 0,
            "application_inputs_satisfied_count": 0,
            "application_record_present_count": 0,
            "record_schema_matches_count": 0,
            "application_scope_matches_count": 0,
            "explicit_application_authorized_count": 0,
            "application_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "application_record_valid_count": 0,
            "application_record_rejected_count": 0,
            "unsafe_application_record_count": 0,
            "missing_application_prerequisite_count": 10,
            "reported_allowed_evidence_command_count": 0,
            "reported_forbidden_evidence_command_count": 0,
            "durable_authoring_command_completion_allowed_count": 0,
            "durable_authoring_command_completed_count": 0,
            "durable_authoring_command_application_allowed_count": 0,
            "durable_authoring_command_application_applied_count": 0,
            "asset_write_allowed_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "durable_authoring_command_dispatch_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_execution_allowed_count": 0,
            "durable_authoring_command_executed_count": 0,
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
        }
        assert (
            executor_authoring_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
            "result_contract_defined_count": 1,
            "application_contract_ready_count": 1,
            "application_inputs_satisfied_count": 0,
            "application_record_valid_count": 0,
            "result_inputs_satisfied_count": 0,
            "result_record_present_count": 0,
            "record_schema_matches_count": 0,
            "result_scope_matches_count": 0,
            "explicit_result_authorized_count": 0,
            "result_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_result_observed_count": 0,
            "no_forbidden_results_count": 0,
            "result_record_valid_count": 0,
            "result_record_rejected_count": 0,
            "unsafe_result_record_count": 0,
            "missing_result_prerequisite_count": 12,
            "reported_allowed_result_count": 0,
            "reported_forbidden_result_count": 0,
            "reported_allowed_evidence_command_count": 0,
            "reported_forbidden_evidence_command_count": 0,
            "durable_authoring_command_completion_result_accepted_count": 0,
            "durable_authoring_command_completion_allowed_count": 0,
            "durable_authoring_command_completed_count": 0,
            "durable_authoring_command_application_allowed_count": 0,
            "durable_authoring_command_application_applied_count": 0,
            "asset_write_allowed_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "durable_authoring_command_dispatch_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_execution_allowed_count": 0,
            "durable_authoring_command_executed_count": 0,
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
            "reported_completion_noop_result_count": 0,
            "reported_application_validation_result_count": 0,
            "reported_completion_completed_result_count": 0,
            "reported_asset_write_result_count": 0,
            "reported_package_dirty_result_count": 0,
            "reported_save_result_count": 0,
            "reported_delete_rename_result_count": 0,
            "reported_cleanup_result_count": 0,
            "reported_code_change_result_count": 0,
            "reported_live_command_result_count": 0,
        }
        assert (
            executor_authoring_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_completion_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
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
        assert (
            executor_authoring_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
            "final_no_save_release_contract_defined_count": 1,
            "readback_contract_ready_count": 1,
            "readback_inputs_satisfied_count": 0,
            "readback_record_valid_count": 0,
            "allowed_readback_observed_count": 0,
            "no_forbidden_readbacks_count": 0,
            "final_no_save_release_inputs_satisfied_count": 0,
            "final_no_save_release_record_present_count": 0,
            "record_schema_matches_count": 0,
            "final_no_save_release_scope_matches_count": 0,
            "explicit_final_no_save_release_authorized_count": 0,
            "final_no_save_release_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_final_no_save_release_observed_count": 0,
            "no_forbidden_final_no_save_releases_count": 0,
            "final_no_save_release_record_valid_count": 0,
            "final_no_save_release_record_rejected_count": 0,
            "unsafe_final_no_save_release_record_count": 0,
            "missing_final_no_save_release_prerequisite_count": 14,
            "reported_allowed_final_no_save_release_count": 0,
            "reported_forbidden_final_no_save_release_count": 0,
            "durable_authoring_final_no_save_release_accepted_count": 0,
            "durable_authoring_final_release_readiness_started_count": 0,
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
            "reported_no_completion_release_count": 0,
            "reported_no_write_release_count": 0,
            "reported_no_save_release_count": 0,
            "reported_readback_revalidated_count": 0,
            "reported_no_code_change_release_count": 0,
            "reported_no_live_command_release_count": 0,
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
        assert (
            executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
            "final_release_readiness_contract_defined_count": 1,
            "final_no_save_release_contract_ready_count": 1,
            "final_no_save_release_inputs_satisfied_count": 0,
            "final_no_save_release_record_valid_count": 0,
            "allowed_final_no_save_release_observed_count": 0,
            "no_forbidden_final_no_save_releases_count": 0,
            "final_release_readiness_inputs_satisfied_count": 0,
            "final_release_readiness_record_present_count": 0,
            "record_schema_matches_count": 0,
            "readiness_scope_matches_count": 0,
            "explicit_readiness_authorized_count": 0,
            "readiness_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_final_release_readiness_observed_count": 0,
            "no_forbidden_final_release_readiness_claims_count": 0,
            "final_release_readiness_record_valid_count": 0,
            "final_release_readiness_record_rejected_count": 0,
            "unsafe_final_release_readiness_record_count": 0,
            "missing_final_release_readiness_prerequisite_count": 14,
            "reported_allowed_final_release_readiness_count": 0,
            "reported_forbidden_final_release_readiness_count": 0,
            "durable_authoring_final_release_readiness_started_count": 0,
            "durable_authoring_final_release_ready_count": 0,
            "durable_authoring_release_review_started_count": 0,
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
            "reported_final_release_readiness_gate_count": 0,
            "reported_final_no_save_release_revalidated_count": 0,
            "reported_durable_authoring_still_disabled_count": 0,
            "reported_no_completion_readiness_count": 0,
            "reported_no_write_readiness_count": 0,
            "reported_no_save_readiness_count": 0,
            "reported_no_code_change_readiness_count": 0,
            "reported_no_live_command_readiness_count": 0,
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
        assert (
            executor_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
            "release_review_contract_defined_count": 1,
            "final_release_readiness_contract_ready_count": 1,
            "final_release_readiness_inputs_satisfied_count": 0,
            "final_release_readiness_record_valid_count": 0,
            "allowed_final_release_readiness_observed_count": 0,
            "no_forbidden_final_release_readiness_claims_count": 0,
            "release_review_inputs_satisfied_count": 0,
            "release_review_record_present_count": 0,
            "record_schema_matches_count": 0,
            "release_review_scope_matches_count": 0,
            "explicit_release_review_authorized_count": 0,
            "release_review_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_release_review_observed_count": 0,
            "no_forbidden_release_review_claims_count": 0,
            "release_review_record_valid_count": 0,
            "release_review_record_rejected_count": 0,
            "unsafe_release_review_record_count": 0,
            "missing_release_review_prerequisite_count": 14,
            "reported_allowed_release_review_count": 0,
            "reported_forbidden_release_review_count": 0,
            "durable_authoring_release_review_started_count": 0,
            "durable_authoring_release_review_accepted_count": 0,
            "durable_authoring_release_decision_started_count": 0,
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
            "reported_release_review_gate_count": 0,
            "reported_final_release_readiness_revalidated_count": 0,
            "reported_durable_authoring_still_disabled_count": 0,
            "reported_no_completion_release_review_count": 0,
            "reported_no_write_release_review_count": 0,
            "reported_no_save_release_review_count": 0,
            "reported_no_code_change_release_review_count": 0,
            "reported_no_live_command_release_review_count": 0,
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
        assert (
            executor_authoring_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_release_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
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
        assert (
            executor_authoring_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_release_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
            "release_promotion_barrier_contract_defined_count": 1,
            "release_decision_contract_ready_count": 1,
            "release_decision_inputs_satisfied_count": 0,
            "release_decision_record_valid_count": 0,
            "allowed_release_decision_observed_count": 0,
            "no_forbidden_release_decision_claims_count": 0,
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
            "durable_authoring_release_promotion_barrier_started_count": 0,
            "durable_authoring_release_promotion_barrier_accepted_count": 0,
            "durable_executor_activation_readiness_started_count": 0,
            "durable_executor_activated_count": 0,
            "durable_executor_opened_count": 0,
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
            "reported_promotion_barrier_gate_count": 0,
            "reported_release_decision_revalidated_count": 0,
            "reported_durable_authoring_still_disabled_count": 0,
            "reported_no_completion_promotion_barrier_count": 0,
            "reported_no_write_promotion_barrier_count": 0,
            "reported_no_save_promotion_barrier_count": 0,
            "reported_no_code_change_promotion_barrier_count": 0,
            "reported_no_live_command_promotion_barrier_count": 0,
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
        assert (
            executor_authoring_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_release_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
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
            "durable_authoring_release_promotion_barrier_started_count": 0,
            "durable_authoring_release_promotion_barrier_accepted_count": 0,
            "durable_executor_activation_readiness_started_count": 0,
            "durable_executor_activation_readiness_accepted_count": 0,
            "durable_executor_open_contract_started_count": 0,
            "durable_executor_activated_count": 0,
            "durable_executor_opened_count": 0,
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
            "reported_activation_readiness_gate_count": 0,
            "reported_promotion_barrier_revalidated_count": 0,
            "reported_release_decision_revalidated_count": 0,
            "reported_durable_authoring_still_disabled_count": 0,
            "reported_no_completion_activation_readiness_count": 0,
            "reported_no_write_activation_readiness_count": 0,
            "reported_no_save_activation_readiness_count": 0,
            "reported_no_code_change_activation_readiness_count": 0,
            "reported_no_live_command_activation_readiness_count": 0,
            "reported_release_promotion_barrier_count": 0,
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
        assert (
            executor_authoring_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
            "open_contract_defined_count": 1,
            "activation_readiness_contract_ready_count": 1,
            "activation_readiness_inputs_satisfied_count": 0,
            "activation_readiness_record_valid_count": 0,
            "allowed_activation_readiness_observed_count": 0,
            "no_forbidden_activation_readiness_claims_count": 0,
            "open_inputs_satisfied_count": 0,
            "open_record_present_count": 0,
            "record_schema_matches_count": 0,
            "open_scope_matches_count": 0,
            "explicit_open_authorized_count": 0,
            "open_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "allowed_open_observed_count": 0,
            "no_forbidden_open_claims_count": 0,
            "open_record_valid_count": 0,
            "open_record_rejected_count": 0,
            "unsafe_open_record_count": 0,
            "missing_open_prerequisite_count": 14,
            "reported_allowed_open_count": 0,
            "reported_forbidden_open_count": 0,
            "durable_executor_open_contract_started_count": 0,
            "durable_executor_open_contract_accepted_count": 0,
            "durable_executor_open_performed_count": 0,
            "durable_executor_activated_count": 0,
            "durable_executor_opened_count": 0,
            "durable_authoring_enable_started_count": 0,
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
            "reported_executor_open_gate_count": 0,
            "reported_activation_readiness_revalidated_count": 0,
            "reported_promotion_barrier_revalidated_count": 0,
            "reported_durable_authoring_still_disabled_count": 0,
            "reported_no_completion_open_count": 0,
            "reported_no_write_open_count": 0,
            "reported_no_save_open_count": 0,
            "reported_no_code_change_open_count": 0,
            "reported_no_live_command_open_count": 0,
            "reported_activation_readiness_count": 0,
            "reported_release_promotion_barrier_count": 0,
            "reported_release_decision_count": 0,
            "reported_release_review_count": 0,
            "reported_final_release_readiness_count": 0,
            "reported_final_no_save_release_count": 0,
            "reported_command_result_readback_count": 0,
            "reported_completion_result_acceptance_count": 0,
            "reported_completion_count": 0,
            "reported_executor_activation_count": 0,
            "reported_executor_open_count": 0,
            "reported_durable_authoring_enable_count": 0,
            "reported_asset_write_count": 0,
            "reported_package_dirty_count": 0,
            "reported_save_count": 0,
            "reported_delete_rename_count": 0,
            "reported_cleanup_count": 0,
            "reported_durable_authoring_count": 0,
            "reported_code_change_count": 0,
            "reported_live_command_count": 0,
        }
        assert (
            executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
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
            "reported_authoring_enable_gate_count": 0,
            "reported_executor_open_revalidated_count": 0,
            "reported_target_allowlist_reconfirmed_count": 0,
            "reported_overwrite_rename_decision_reconfirmed_count": 0,
            "reported_rollback_readiness_reconfirmed_count": 0,
            "reported_ownership_marker_reconfirmed_count": 0,
            "reported_durable_authoring_still_disabled_count": 0,
            "reported_no_code_change_authoring_enable_count": 0,
            "reported_no_asset_change_authoring_enable_count": 0,
            "reported_no_live_probe_authoring_enable_count": 0,
            "reported_activation_readiness_count": 0,
            "reported_release_promotion_barrier_count": 0,
            "reported_release_decision_count": 0,
            "reported_release_review_count": 0,
            "reported_final_release_readiness_count": 0,
            "reported_final_no_save_release_count": 0,
            "reported_command_result_readback_count": 0,
            "reported_completion_result_acceptance_count": 0,
            "reported_completion_count": 0,
            "reported_executor_activation_count": 0,
            "reported_executor_open_count": 0,
            "reported_authoring_enable_count": 0,
            "reported_authoring_command_count": 0,
            "reported_asset_write_count": 0,
            "reported_package_dirty_count": 0,
            "reported_save_count": 0,
            "reported_delete_rename_count": 0,
            "reported_cleanup_count": 0,
            "reported_durable_authoring_count": 0,
            "reported_code_change_count": 0,
            "reported_live_command_count": 0,
        }
        assert (
            executor_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row = find_row(
            report,
            "durable_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract",
        )
        assert (
            executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "status"
            ]
            == "passed"
        )
        expected_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": 1,
            "authoring_command_contract_defined_count": 1,
            "authoring_enable_contract_ready_count": 1,
            "open_inputs_satisfied_count": 0,
            "open_record_valid_count": 0,
            "allowed_open_observed_count": 0,
            "no_forbidden_open_claims_count": 0,
            "open_activation_promotion_readiness_chain_satisfied_count": 0,
            "authoring_enable_inputs_satisfied_count": 0,
            "authoring_enable_record_valid_count": 0,
            "allowed_authoring_enable_observed_count": 0,
            "no_forbidden_authoring_enable_claims_count": 0,
            "authoring_enable_chain_satisfied_count": 0,
            "target_package_allowlist_reconfirmed_count": 0,
            "overwrite_rename_decision_reconfirmed_count": 0,
            "rollback_readiness_reconfirmed_count": 0,
            "ownership_marker_reconfirmed_count": 0,
            "durable_release_readiness_chain_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_present_count": 0,
            "record_schema_matches_count": 0,
            "command_scope_matches_count": 0,
            "explicit_authoring_command_authorized_count": 0,
            "command_status_passed_count": 0,
            "no_save_delete_rename_acknowledged_count": 0,
            "explicit_durable_mvp_request_reconfirmed_count": 0,
            "planned_authoring_command_count": 0,
            "allowed_authoring_command_count": 0,
            "forbidden_authoring_command_count": 0,
            "unknown_authoring_command_count": 0,
            "authoring_command_record_valid_count": 0,
            "authoring_command_record_rejected_count": 0,
            "unsafe_authoring_command_record_count": 0,
            "missing_authoring_command_prerequisite_count": 21,
            "durable_authoring_command_contract_started_count": 0,
            "durable_authoring_command_contract_accepted_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_executor_command_path_opened_count": 0,
            "durable_executor_command_path_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_enable_started_count": 0,
            "durable_authoring_enable_accepted_count": 0,
            "durable_authoring_enable_allowed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
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
        assert (
            executor_authoring_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_row[
                "actual"
            ]
            == expected_command_after_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_actual
        )
        command_request_dry_run_route_row = find_row(
            report,
            "durable_executor_authoring_command_request_dry_run_route_contract",
        )
        assert command_request_dry_run_route_row["status"] == "passed"
        expected_command_request_dry_run_route_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_request_dry_run_route_count": 1,
            "route_contract_defined_count": 1,
            "section_161_command_contract_ready_count": 1,
            "open_activation_promotion_readiness_chain_satisfied_count": 0,
            "authoring_enable_chain_satisfied_count": 0,
            "durable_release_readiness_chain_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "readiness_chain_satisfied_count": 0,
            "dry_run_route_record_present_count": 0,
            "record_schema_matches_count": 0,
            "route_scope_matches_count": 0,
            "dry_run_only_count": 0,
            "route_status_passed_count": 0,
            "operator_reconfirmed_no_write_execution_count": 0,
            "operator_reconfirmed_no_save_delete_rename_count": 0,
            "requested_command_allowed_count": 0,
            "requested_command_forbidden_count": 0,
            "requested_command_unknown_count": 0,
            "dry_run_operation_allowed_count": 0,
            "target_asset_declared_count": 0,
            "readiness_proof_matches_count": 0,
            "release_boundary_proof_safe_count": 0,
            "dry_run_route_record_valid_count": 0,
            "dry_run_route_record_rejected_count": 0,
            "dry_run_route_admissible_count": 0,
            "unsafe_request_record_count": 0,
            "missing_dry_run_route_prerequisite_count": 17,
            "dry_run_route_request_started_count": 0,
            "dry_run_route_request_accepted_count": 0,
            "durable_command_request_promoted_count": 0,
            "durable_executor_command_path_opened_count": 0,
            "durable_executor_command_path_allowed_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "final_durable_release_ready_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "save_delete_rename_allowed_count": 0,
            "save_asset_allowed_count": 0,
            "delete_asset_allowed_count": 0,
            "rename_asset_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            command_request_dry_run_route_row["actual"]
            == expected_command_request_dry_run_route_actual
        )
        command_dispatch_dry_run_row = find_row(
            report,
            "durable_executor_authoring_command_dispatch_dry_run_contract",
        )
        assert command_dispatch_dry_run_row["status"] == "passed"
        expected_command_dispatch_dry_run_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_dispatch_dry_run_count": 1,
            "dispatch_contract_defined_count": 1,
            "section_162_route_contract_ready_count": 1,
            "open_activation_promotion_readiness_chain_satisfied_count": 0,
            "authoring_enable_chain_satisfied_count": 0,
            "durable_release_readiness_chain_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "dry_run_route_record_valid_count": 0,
            "dry_run_route_admissible_count": 0,
            "route_chain_satisfied_count": 0,
            "dispatch_dry_run_record_present_count": 0,
            "record_schema_matches_count": 0,
            "dispatch_scope_matches_count": 0,
            "dry_run_only_count": 0,
            "dispatch_status_passed_count": 0,
            "operator_reconfirmed_no_live_dispatch_count": 0,
            "operator_reconfirmed_no_write_execution_count": 0,
            "operator_reconfirmed_no_save_delete_rename_count": 0,
            "requested_command_allowed_count": 0,
            "requested_command_forbidden_count": 0,
            "requested_command_unknown_count": 0,
            "dispatch_operation_allowed_count": 0,
            "dispatch_envelope_target_declared_count": 0,
            "route_admission_proof_matches_count": 0,
            "release_boundary_proof_safe_count": 0,
            "dispatch_dry_run_record_valid_count": 0,
            "dispatch_dry_run_record_rejected_count": 0,
            "dispatch_dry_run_admissible_count": 0,
            "unsafe_dispatch_record_count": 0,
            "missing_dispatch_dry_run_prerequisite_count": 20,
            "dispatch_dry_run_started_count": 0,
            "dispatch_dry_run_accepted_count": 0,
            "durable_dispatch_envelope_promoted_count": 0,
            "durable_command_request_promoted_count": 0,
            "durable_executor_command_path_opened_count": 0,
            "durable_executor_command_path_allowed_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "final_durable_release_ready_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "save_delete_rename_allowed_count": 0,
            "save_asset_allowed_count": 0,
            "delete_asset_allowed_count": 0,
            "rename_asset_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            command_dispatch_dry_run_row["actual"]
            == expected_command_dispatch_dry_run_actual
        )
        command_dispatch_evidence_dry_run_row = find_row(
            report,
            "durable_executor_authoring_command_dispatch_evidence_dry_run_contract",
        )
        assert command_dispatch_evidence_dry_run_row["status"] == "passed"
        expected_command_dispatch_evidence_dry_run_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_dispatch_evidence_dry_run_count": 1,
            "dispatch_evidence_contract_defined_count": 1,
            "section_163_dispatch_contract_ready_count": 1,
            "open_activation_promotion_readiness_chain_satisfied_count": 0,
            "authoring_enable_chain_satisfied_count": 0,
            "durable_release_readiness_chain_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "dry_run_route_record_valid_count": 0,
            "dry_run_route_admissible_count": 0,
            "dispatch_dry_run_record_valid_count": 0,
            "dispatch_dry_run_admissible_count": 0,
            "dispatch_chain_satisfied_count": 0,
            "dispatch_evidence_dry_run_record_present_count": 0,
            "record_schema_matches_count": 0,
            "evidence_scope_matches_count": 0,
            "dry_run_only_count": 0,
            "evidence_status_passed_count": 0,
            "operator_reconfirmed_no_live_dispatch_count": 0,
            "operator_reconfirmed_no_live_execution_count": 0,
            "operator_reconfirmed_no_write_execution_count": 0,
            "operator_reconfirmed_no_save_delete_rename_count": 0,
            "requested_command_allowed_count": 0,
            "requested_command_forbidden_count": 0,
            "requested_command_unknown_count": 0,
            "evidence_operation_allowed_count": 0,
            "dispatch_evidence_target_declared_count": 0,
            "dispatch_admission_proof_matches_count": 0,
            "release_boundary_proof_safe_count": 0,
            "dispatch_evidence_dry_run_record_valid_count": 0,
            "dispatch_evidence_dry_run_record_rejected_count": 0,
            "dispatch_evidence_dry_run_admissible_count": 0,
            "unsafe_evidence_record_count": 0,
            "missing_dispatch_evidence_dry_run_prerequisite_count": 23,
            "dispatch_evidence_dry_run_started_count": 0,
            "dispatch_evidence_dry_run_accepted_count": 0,
            "durable_evidence_promoted_count": 0,
            "durable_dispatch_envelope_promoted_count": 0,
            "durable_command_request_promoted_count": 0,
            "durable_executor_command_path_opened_count": 0,
            "durable_executor_command_path_allowed_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "final_durable_release_ready_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "save_delete_rename_allowed_count": 0,
            "save_asset_allowed_count": 0,
            "delete_asset_allowed_count": 0,
            "rename_asset_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            command_dispatch_evidence_dry_run_row["actual"]
            == expected_command_dispatch_evidence_dry_run_actual
        )
        command_execution_dry_run_row = find_row(
            report,
            "durable_executor_authoring_command_execution_dry_run_contract",
        )
        assert command_execution_dry_run_row["status"] == "passed"
        expected_command_execution_dry_run_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_execution_dry_run_count": 1,
            "execution_contract_defined_count": 1,
            "section_164_dispatch_evidence_contract_ready_count": 1,
            "open_activation_promotion_readiness_chain_satisfied_count": 0,
            "authoring_enable_chain_satisfied_count": 0,
            "durable_release_readiness_chain_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "dry_run_route_record_valid_count": 0,
            "dry_run_route_admissible_count": 0,
            "dispatch_dry_run_record_valid_count": 0,
            "dispatch_dry_run_admissible_count": 0,
            "dispatch_evidence_dry_run_record_valid_count": 0,
            "dispatch_evidence_dry_run_admissible_count": 0,
            "evidence_chain_satisfied_count": 0,
            "execution_dry_run_record_present_count": 0,
            "record_schema_matches_count": 0,
            "execution_scope_matches_count": 0,
            "dry_run_only_count": 0,
            "execution_status_passed_count": 0,
            "operator_reconfirmed_no_live_dispatch_count": 0,
            "operator_reconfirmed_no_live_execution_count": 0,
            "operator_reconfirmed_no_write_execution_count": 0,
            "operator_reconfirmed_no_save_delete_rename_count": 0,
            "requested_command_allowed_count": 0,
            "requested_command_forbidden_count": 0,
            "requested_command_unknown_count": 0,
            "execution_operation_allowed_count": 0,
            "execution_target_declared_count": 0,
            "dispatch_evidence_admission_proof_matches_count": 0,
            "release_boundary_proof_safe_count": 0,
            "execution_dry_run_record_valid_count": 0,
            "execution_dry_run_record_rejected_count": 0,
            "execution_dry_run_admissible_count": 0,
            "unsafe_execution_record_count": 0,
            "missing_execution_dry_run_prerequisite_count": 25,
            "execution_dry_run_started_count": 0,
            "execution_dry_run_accepted_count": 0,
            "durable_execution_envelope_promoted_count": 0,
            "durable_evidence_promoted_count": 0,
            "durable_dispatch_envelope_promoted_count": 0,
            "durable_command_request_promoted_count": 0,
            "durable_executor_command_path_opened_count": 0,
            "durable_executor_command_path_allowed_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "final_durable_release_ready_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "save_delete_rename_allowed_count": 0,
            "save_asset_allowed_count": 0,
            "delete_asset_allowed_count": 0,
            "rename_asset_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            command_execution_dry_run_row["actual"]
            == expected_command_execution_dry_run_actual
        )
        command_execution_evidence_dry_run_row = find_row(
            report,
            "durable_executor_authoring_command_execution_evidence_dry_run_contract",
        )
        assert command_execution_evidence_dry_run_row["status"] == "passed"
        expected_command_execution_evidence_dry_run_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_execution_evidence_dry_run_count": 1,
            "execution_evidence_contract_defined_count": 1,
            "section_165_execution_contract_ready_count": 1,
            "open_activation_promotion_readiness_chain_satisfied_count": 0,
            "authoring_enable_chain_satisfied_count": 0,
            "durable_release_readiness_chain_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "dry_run_route_record_valid_count": 0,
            "dry_run_route_admissible_count": 0,
            "dispatch_dry_run_record_valid_count": 0,
            "dispatch_dry_run_admissible_count": 0,
            "dispatch_evidence_dry_run_record_valid_count": 0,
            "dispatch_evidence_dry_run_admissible_count": 0,
            "execution_dry_run_record_valid_count": 0,
            "execution_dry_run_admissible_count": 0,
            "execution_chain_satisfied_count": 0,
            "execution_evidence_dry_run_record_present_count": 0,
            "record_schema_matches_count": 0,
            "execution_evidence_scope_matches_count": 0,
            "dry_run_only_count": 0,
            "execution_evidence_status_passed_count": 0,
            "operator_reconfirmed_no_live_dispatch_count": 0,
            "operator_reconfirmed_no_live_execution_count": 0,
            "operator_reconfirmed_no_write_execution_count": 0,
            "operator_reconfirmed_no_save_delete_rename_count": 0,
            "requested_command_allowed_count": 0,
            "requested_command_forbidden_count": 0,
            "requested_command_unknown_count": 0,
            "execution_evidence_operation_allowed_count": 0,
            "execution_evidence_target_declared_count": 0,
            "execution_admission_proof_matches_count": 0,
            "release_boundary_proof_safe_count": 0,
            "execution_evidence_dry_run_record_valid_count": 0,
            "execution_evidence_dry_run_record_rejected_count": 0,
            "execution_evidence_dry_run_admissible_count": 0,
            "unsafe_execution_evidence_record_count": 0,
            "missing_execution_evidence_dry_run_prerequisite_count": 27,
            "execution_evidence_dry_run_started_count": 0,
            "execution_evidence_dry_run_accepted_count": 0,
            "durable_execution_evidence_promoted_count": 0,
            "durable_execution_envelope_promoted_count": 0,
            "durable_evidence_promoted_count": 0,
            "durable_dispatch_envelope_promoted_count": 0,
            "durable_command_request_promoted_count": 0,
            "durable_executor_command_path_opened_count": 0,
            "durable_executor_command_path_allowed_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "final_durable_release_ready_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "save_delete_rename_allowed_count": 0,
            "save_asset_allowed_count": 0,
            "delete_asset_allowed_count": 0,
            "rename_asset_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            command_execution_evidence_dry_run_row["actual"]
            == expected_command_execution_evidence_dry_run_actual
        )
        command_completion_decision_dry_run_row = find_row(
            report,
            "durable_executor_authoring_command_completion_decision_dry_run_contract",
        )
        assert command_completion_decision_dry_run_row["status"] == "passed"
        expected_command_completion_decision_dry_run_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_completion_decision_dry_run_count": 1,
            "completion_decision_contract_defined_count": 1,
            "section_166_execution_evidence_contract_ready_count": 1,
            "open_activation_promotion_readiness_chain_satisfied_count": 0,
            "authoring_enable_chain_satisfied_count": 0,
            "durable_release_readiness_chain_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "dry_run_route_record_valid_count": 0,
            "dry_run_route_admissible_count": 0,
            "dispatch_dry_run_record_valid_count": 0,
            "dispatch_dry_run_admissible_count": 0,
            "dispatch_evidence_dry_run_record_valid_count": 0,
            "dispatch_evidence_dry_run_admissible_count": 0,
            "execution_dry_run_record_valid_count": 0,
            "execution_dry_run_admissible_count": 0,
            "execution_evidence_dry_run_record_valid_count": 0,
            "execution_evidence_dry_run_admissible_count": 0,
            "execution_evidence_chain_satisfied_count": 0,
            "completion_decision_dry_run_record_present_count": 0,
            "record_schema_matches_count": 0,
            "completion_decision_scope_matches_count": 0,
            "dry_run_only_count": 0,
            "completion_decision_status_passed_count": 0,
            "operator_reconfirmed_no_live_dispatch_count": 0,
            "operator_reconfirmed_no_live_execution_count": 0,
            "operator_reconfirmed_no_write_execution_count": 0,
            "operator_reconfirmed_no_save_delete_rename_count": 0,
            "requested_command_allowed_count": 0,
            "requested_command_forbidden_count": 0,
            "requested_command_unknown_count": 0,
            "completion_decision_operation_allowed_count": 0,
            "completion_decision_target_declared_count": 0,
            "execution_evidence_admission_proof_matches_count": 0,
            "release_boundary_proof_safe_count": 0,
            "completion_decision_dry_run_record_valid_count": 0,
            "completion_decision_dry_run_record_rejected_count": 0,
            "completion_decision_dry_run_admissible_count": 0,
            "unsafe_completion_decision_record_count": 0,
            "missing_completion_decision_dry_run_prerequisite_count": 29,
            "completion_decision_dry_run_started_count": 0,
            "completion_decision_dry_run_accepted_count": 0,
            "durable_completion_decision_promoted_count": 0,
            "durable_execution_evidence_promoted_count": 0,
            "durable_execution_envelope_promoted_count": 0,
            "durable_evidence_promoted_count": 0,
            "durable_dispatch_envelope_promoted_count": 0,
            "durable_command_request_promoted_count": 0,
            "durable_executor_command_path_opened_count": 0,
            "durable_executor_command_path_allowed_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_command_completed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "final_durable_release_ready_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "save_delete_rename_allowed_count": 0,
            "save_asset_allowed_count": 0,
            "delete_asset_allowed_count": 0,
            "rename_asset_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            command_completion_decision_dry_run_row["actual"]
            == expected_command_completion_decision_dry_run_actual
        )
        command_completion_application_dry_run_row = find_row(
            report,
            "durable_executor_authoring_command_completion_application_dry_run_contract",
        )
        assert command_completion_application_dry_run_row["status"] == "passed"
        expected_command_completion_application_dry_run_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_completion_application_dry_run_count": 1,
            "completion_application_contract_defined_count": 1,
            "section_167_completion_decision_contract_ready_count": 1,
            "open_activation_promotion_readiness_chain_satisfied_count": 0,
            "authoring_enable_chain_satisfied_count": 0,
            "durable_release_readiness_chain_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "dry_run_route_record_valid_count": 0,
            "dry_run_route_admissible_count": 0,
            "dispatch_dry_run_record_valid_count": 0,
            "dispatch_dry_run_admissible_count": 0,
            "dispatch_evidence_dry_run_record_valid_count": 0,
            "dispatch_evidence_dry_run_admissible_count": 0,
            "execution_dry_run_record_valid_count": 0,
            "execution_dry_run_admissible_count": 0,
            "execution_evidence_dry_run_record_valid_count": 0,
            "execution_evidence_dry_run_admissible_count": 0,
            "completion_decision_dry_run_record_valid_count": 0,
            "completion_decision_dry_run_admissible_count": 0,
            "completion_decision_chain_satisfied_count": 0,
            "completion_application_dry_run_record_present_count": 0,
            "record_schema_matches_count": 0,
            "completion_application_scope_matches_count": 0,
            "dry_run_only_count": 0,
            "completion_application_status_passed_count": 0,
            "operator_reconfirmed_no_live_dispatch_count": 0,
            "operator_reconfirmed_no_live_execution_count": 0,
            "operator_reconfirmed_no_write_execution_count": 0,
            "operator_reconfirmed_no_save_delete_rename_count": 0,
            "requested_command_allowed_count": 0,
            "requested_command_forbidden_count": 0,
            "requested_command_unknown_count": 0,
            "completion_application_operation_allowed_count": 0,
            "completion_application_target_declared_count": 0,
            "completion_decision_admission_proof_matches_count": 0,
            "release_boundary_proof_safe_count": 0,
            "completion_application_dry_run_record_valid_count": 0,
            "completion_application_dry_run_record_rejected_count": 0,
            "completion_application_dry_run_admissible_count": 0,
            "unsafe_completion_application_record_count": 0,
            "missing_completion_application_dry_run_prerequisite_count": 31,
            "completion_application_dry_run_started_count": 0,
            "completion_application_dry_run_accepted_count": 0,
            "durable_completion_application_promoted_count": 0,
            "durable_completion_application_applied_count": 0,
            "durable_completion_decision_promoted_count": 0,
            "durable_execution_evidence_promoted_count": 0,
            "durable_execution_envelope_promoted_count": 0,
            "durable_evidence_promoted_count": 0,
            "durable_dispatch_envelope_promoted_count": 0,
            "durable_command_request_promoted_count": 0,
            "durable_executor_command_path_opened_count": 0,
            "durable_executor_command_path_allowed_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_command_completed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "final_durable_release_ready_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "save_delete_rename_allowed_count": 0,
            "save_asset_allowed_count": 0,
            "delete_asset_allowed_count": 0,
            "rename_asset_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            command_completion_application_dry_run_row["actual"]
            == expected_command_completion_application_dry_run_actual
        )
        command_completion_result_dry_run_row = find_row(
            report,
            "durable_executor_authoring_command_completion_result_dry_run_contract",
        )
        assert command_completion_result_dry_run_row["status"] == "passed"
        expected_command_completion_result_dry_run_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_completion_result_dry_run_count": 1,
            "completion_result_contract_defined_count": 1,
            "section_168_completion_application_contract_ready_count": 1,
            "open_activation_promotion_readiness_chain_satisfied_count": 0,
            "authoring_enable_chain_satisfied_count": 0,
            "durable_release_readiness_chain_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "dry_run_route_record_valid_count": 0,
            "dry_run_route_admissible_count": 0,
            "dispatch_dry_run_record_valid_count": 0,
            "dispatch_dry_run_admissible_count": 0,
            "dispatch_evidence_dry_run_record_valid_count": 0,
            "dispatch_evidence_dry_run_admissible_count": 0,
            "execution_dry_run_record_valid_count": 0,
            "execution_dry_run_admissible_count": 0,
            "execution_evidence_dry_run_record_valid_count": 0,
            "execution_evidence_dry_run_admissible_count": 0,
            "completion_decision_dry_run_record_valid_count": 0,
            "completion_decision_dry_run_admissible_count": 0,
            "completion_application_dry_run_record_valid_count": 0,
            "completion_application_dry_run_admissible_count": 0,
            "completion_application_chain_satisfied_count": 0,
            "completion_result_dry_run_record_present_count": 0,
            "record_schema_matches_count": 0,
            "completion_result_scope_matches_count": 0,
            "dry_run_only_count": 0,
            "completion_result_status_passed_count": 0,
            "operator_reconfirmed_no_live_dispatch_count": 0,
            "operator_reconfirmed_no_live_execution_count": 0,
            "operator_reconfirmed_no_write_execution_count": 0,
            "operator_reconfirmed_no_save_delete_rename_count": 0,
            "requested_command_allowed_count": 0,
            "requested_command_forbidden_count": 0,
            "requested_command_unknown_count": 0,
            "completion_result_operation_allowed_count": 0,
            "completion_result_target_declared_count": 0,
            "completion_application_admission_proof_matches_count": 0,
            "release_boundary_proof_safe_count": 0,
            "completion_result_dry_run_record_valid_count": 0,
            "completion_result_dry_run_record_rejected_count": 0,
            "completion_result_dry_run_admissible_count": 0,
            "unsafe_completion_result_record_count": 0,
            "missing_completion_result_dry_run_prerequisite_count": 33,
            "completion_result_dry_run_started_count": 0,
            "completion_result_dry_run_accepted_count": 0,
            "durable_completion_result_promoted_count": 0,
            "durable_completion_result_recorded_count": 0,
            "durable_completion_application_promoted_count": 0,
            "durable_completion_application_applied_count": 0,
            "durable_completion_decision_promoted_count": 0,
            "durable_execution_evidence_promoted_count": 0,
            "durable_execution_envelope_promoted_count": 0,
            "durable_evidence_promoted_count": 0,
            "durable_dispatch_envelope_promoted_count": 0,
            "durable_command_request_promoted_count": 0,
            "durable_executor_command_path_opened_count": 0,
            "durable_executor_command_path_allowed_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_command_completed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "final_durable_release_ready_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "save_delete_rename_allowed_count": 0,
            "save_asset_allowed_count": 0,
            "delete_asset_allowed_count": 0,
            "rename_asset_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            command_completion_result_dry_run_row["actual"]
            == expected_command_completion_result_dry_run_actual
        )
        command_result_readback_dry_run_row = find_row(
            report,
            "durable_executor_authoring_command_result_readback_dry_run_contract",
        )
        assert command_result_readback_dry_run_row["status"] == "passed"
        expected_command_result_readback_dry_run_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_command_result_readback_dry_run_count": 1,
            "result_readback_contract_defined_count": 1,
            "section_169_completion_result_contract_ready_count": 1,
            "open_activation_promotion_readiness_chain_satisfied_count": 0,
            "authoring_enable_chain_satisfied_count": 0,
            "durable_release_readiness_chain_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "dry_run_route_record_valid_count": 0,
            "dry_run_route_admissible_count": 0,
            "dispatch_dry_run_record_valid_count": 0,
            "dispatch_dry_run_admissible_count": 0,
            "dispatch_evidence_dry_run_record_valid_count": 0,
            "dispatch_evidence_dry_run_admissible_count": 0,
            "execution_dry_run_record_valid_count": 0,
            "execution_dry_run_admissible_count": 0,
            "execution_evidence_dry_run_record_valid_count": 0,
            "execution_evidence_dry_run_admissible_count": 0,
            "completion_decision_dry_run_record_valid_count": 0,
            "completion_decision_dry_run_admissible_count": 0,
            "completion_application_dry_run_record_valid_count": 0,
            "completion_application_dry_run_admissible_count": 0,
            "completion_result_dry_run_record_valid_count": 0,
            "completion_result_dry_run_admissible_count": 0,
            "completion_result_chain_satisfied_count": 0,
            "result_readback_dry_run_record_present_count": 0,
            "record_schema_matches_count": 0,
            "result_readback_scope_matches_count": 0,
            "dry_run_only_count": 0,
            "result_readback_status_passed_count": 0,
            "operator_reconfirmed_no_live_dispatch_count": 0,
            "operator_reconfirmed_no_live_execution_count": 0,
            "operator_reconfirmed_no_write_execution_count": 0,
            "operator_reconfirmed_no_save_delete_rename_count": 0,
            "requested_command_allowed_count": 0,
            "requested_command_forbidden_count": 0,
            "requested_command_unknown_count": 0,
            "result_readback_operation_allowed_count": 0,
            "result_readback_target_declared_count": 0,
            "completion_result_admission_proof_matches_count": 0,
            "release_boundary_proof_safe_count": 0,
            "result_readback_dry_run_record_valid_count": 0,
            "result_readback_dry_run_record_rejected_count": 0,
            "result_readback_dry_run_admissible_count": 0,
            "unsafe_result_readback_record_count": 0,
            "missing_result_readback_dry_run_prerequisite_count": 35,
            "result_readback_dry_run_started_count": 0,
            "result_readback_dry_run_accepted_count": 0,
            "durable_result_readback_promoted_count": 0,
            "durable_result_readback_accepted_count": 0,
            "durable_completion_result_promoted_count": 0,
            "durable_completion_result_recorded_count": 0,
            "durable_completion_application_promoted_count": 0,
            "durable_completion_application_applied_count": 0,
            "durable_completion_decision_promoted_count": 0,
            "durable_execution_evidence_promoted_count": 0,
            "durable_execution_envelope_promoted_count": 0,
            "durable_evidence_promoted_count": 0,
            "durable_dispatch_envelope_promoted_count": 0,
            "durable_command_request_promoted_count": 0,
            "durable_executor_command_path_opened_count": 0,
            "durable_executor_command_path_allowed_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_command_completed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "final_durable_release_ready_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "save_delete_rename_allowed_count": 0,
            "save_asset_allowed_count": 0,
            "delete_asset_allowed_count": 0,
            "rename_asset_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            command_result_readback_dry_run_row["actual"]
            == expected_command_result_readback_dry_run_actual
        )
        final_no_save_release_dry_run_row = find_row(
            report,
            "durable_executor_authoring_final_no_save_release_dry_run_contract",
        )
        assert final_no_save_release_dry_run_row["status"] == "passed"
        expected_final_no_save_release_dry_run_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_final_no_save_release_dry_run_count": 1,
            "final_no_save_release_contract_defined_count": 1,
            "section_170_result_readback_contract_ready_count": 1,
            "open_activation_promotion_readiness_chain_satisfied_count": 0,
            "authoring_enable_chain_satisfied_count": 0,
            "durable_release_readiness_chain_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "dry_run_route_record_valid_count": 0,
            "dry_run_route_admissible_count": 0,
            "dispatch_dry_run_record_valid_count": 0,
            "dispatch_dry_run_admissible_count": 0,
            "dispatch_evidence_dry_run_record_valid_count": 0,
            "dispatch_evidence_dry_run_admissible_count": 0,
            "execution_dry_run_record_valid_count": 0,
            "execution_dry_run_admissible_count": 0,
            "execution_evidence_dry_run_record_valid_count": 0,
            "execution_evidence_dry_run_admissible_count": 0,
            "completion_decision_dry_run_record_valid_count": 0,
            "completion_decision_dry_run_admissible_count": 0,
            "completion_application_dry_run_record_valid_count": 0,
            "completion_application_dry_run_admissible_count": 0,
            "completion_result_dry_run_record_valid_count": 0,
            "completion_result_dry_run_admissible_count": 0,
            "result_readback_dry_run_record_valid_count": 0,
            "result_readback_dry_run_admissible_count": 0,
            "result_readback_chain_satisfied_count": 0,
            "final_no_save_release_dry_run_record_present_count": 0,
            "record_schema_matches_count": 0,
            "final_no_save_release_scope_matches_count": 0,
            "dry_run_only_count": 0,
            "final_no_save_release_status_passed_count": 0,
            "operator_reconfirmed_no_live_dispatch_count": 0,
            "operator_reconfirmed_no_live_execution_count": 0,
            "operator_reconfirmed_no_write_execution_count": 0,
            "operator_reconfirmed_no_save_delete_rename_count": 0,
            "requested_command_allowed_count": 0,
            "requested_command_forbidden_count": 0,
            "requested_command_unknown_count": 0,
            "final_no_save_release_operation_allowed_count": 0,
            "final_no_save_release_target_declared_count": 0,
            "result_readback_admission_proof_matches_count": 0,
            "release_boundary_proof_safe_count": 0,
            "final_no_save_release_dry_run_record_valid_count": 0,
            "final_no_save_release_dry_run_record_rejected_count": 0,
            "final_no_save_release_dry_run_admissible_count": 0,
            "unsafe_final_no_save_release_record_count": 0,
            "missing_final_no_save_release_dry_run_prerequisite_count": 37,
            "final_no_save_release_dry_run_started_count": 0,
            "final_no_save_release_dry_run_accepted_count": 0,
            "durable_final_no_save_release_promoted_count": 0,
            "durable_final_no_save_release_accepted_count": 0,
            "durable_final_release_readiness_started_count": 0,
            "durable_final_release_ready_count": 0,
            "durable_result_readback_promoted_count": 0,
            "durable_result_readback_accepted_count": 0,
            "durable_completion_result_promoted_count": 0,
            "durable_completion_result_recorded_count": 0,
            "durable_completion_application_promoted_count": 0,
            "durable_completion_application_applied_count": 0,
            "durable_completion_decision_promoted_count": 0,
            "durable_execution_evidence_promoted_count": 0,
            "durable_execution_envelope_promoted_count": 0,
            "durable_evidence_promoted_count": 0,
            "durable_dispatch_envelope_promoted_count": 0,
            "durable_command_request_promoted_count": 0,
            "durable_executor_command_path_opened_count": 0,
            "durable_executor_command_path_allowed_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_command_completed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "final_durable_release_ready_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "save_delete_rename_allowed_count": 0,
            "save_asset_allowed_count": 0,
            "delete_asset_allowed_count": 0,
            "rename_asset_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            final_no_save_release_dry_run_row["actual"]
            == expected_final_no_save_release_dry_run_actual
        )
        final_release_readiness_dry_run_row = find_row(
            report,
            "durable_executor_authoring_final_release_readiness_dry_run_contract",
        )
        assert final_release_readiness_dry_run_row["status"] == "passed"
        expected_final_release_readiness_dry_run_actual = {
            "summary_status": "passed",
            "durable_requested_executor_authoring_final_release_readiness_dry_run_count": 1,
            "final_release_readiness_contract_defined_count": 1,
            "section_171_final_no_save_contract_ready_count": 1,
            "open_activation_promotion_readiness_chain_satisfied_count": 0,
            "authoring_enable_chain_satisfied_count": 0,
            "durable_release_readiness_chain_reconfirmed_count": 0,
            "authoring_command_inputs_satisfied_count": 0,
            "authoring_command_record_valid_count": 0,
            "dry_run_route_record_valid_count": 0,
            "dry_run_route_admissible_count": 0,
            "dispatch_dry_run_record_valid_count": 0,
            "dispatch_dry_run_admissible_count": 0,
            "dispatch_evidence_dry_run_record_valid_count": 0,
            "dispatch_evidence_dry_run_admissible_count": 0,
            "execution_dry_run_record_valid_count": 0,
            "execution_dry_run_admissible_count": 0,
            "execution_evidence_dry_run_record_valid_count": 0,
            "execution_evidence_dry_run_admissible_count": 0,
            "completion_decision_dry_run_record_valid_count": 0,
            "completion_decision_dry_run_admissible_count": 0,
            "completion_application_dry_run_record_valid_count": 0,
            "completion_application_dry_run_admissible_count": 0,
            "completion_result_dry_run_record_valid_count": 0,
            "completion_result_dry_run_admissible_count": 0,
            "result_readback_dry_run_record_valid_count": 0,
            "result_readback_dry_run_admissible_count": 0,
            "final_no_save_release_dry_run_record_valid_count": 0,
            "final_no_save_release_dry_run_admissible_count": 0,
            "final_no_save_release_chain_satisfied_count": 0,
            "final_release_readiness_dry_run_record_present_count": 0,
            "record_schema_matches_count": 0,
            "final_release_readiness_scope_matches_count": 0,
            "dry_run_only_count": 0,
            "final_release_readiness_status_passed_count": 0,
            "operator_reconfirmed_no_live_dispatch_count": 0,
            "operator_reconfirmed_no_live_execution_count": 0,
            "operator_reconfirmed_no_write_execution_count": 0,
            "operator_reconfirmed_no_save_delete_rename_count": 0,
            "requested_command_allowed_count": 0,
            "requested_command_forbidden_count": 0,
            "requested_command_unknown_count": 0,
            "final_release_readiness_operation_allowed_count": 0,
            "final_release_readiness_target_declared_count": 0,
            "final_no_save_admission_proof_matches_count": 0,
            "release_boundary_proof_safe_count": 0,
            "final_release_readiness_dry_run_record_valid_count": 0,
            "final_release_readiness_dry_run_record_rejected_count": 0,
            "final_release_readiness_dry_run_admissible_count": 0,
            "unsafe_final_release_readiness_record_count": 0,
            "missing_final_release_readiness_dry_run_prerequisite_count": 39,
            "final_release_readiness_dry_run_started_count": 0,
            "final_release_readiness_dry_run_accepted_count": 0,
            "durable_final_release_readiness_promoted_count": 0,
            "durable_final_release_readiness_started_count": 0,
            "durable_final_release_ready_count": 0,
            "durable_release_review_started_count": 0,
            "durable_final_no_save_release_promoted_count": 0,
            "durable_final_no_save_release_accepted_count": 0,
            "durable_result_readback_promoted_count": 0,
            "durable_result_readback_accepted_count": 0,
            "durable_completion_result_promoted_count": 0,
            "durable_completion_result_recorded_count": 0,
            "durable_completion_application_promoted_count": 0,
            "durable_completion_application_applied_count": 0,
            "durable_completion_decision_promoted_count": 0,
            "durable_execution_evidence_promoted_count": 0,
            "durable_execution_envelope_promoted_count": 0,
            "durable_evidence_promoted_count": 0,
            "durable_dispatch_envelope_promoted_count": 0,
            "durable_command_request_promoted_count": 0,
            "durable_executor_command_path_opened_count": 0,
            "durable_executor_command_path_allowed_count": 0,
            "durable_authoring_command_allowed_count": 0,
            "durable_authoring_command_dispatched_count": 0,
            "durable_authoring_command_executed_count": 0,
            "durable_authoring_command_completed_count": 0,
            "durable_authoring_enabled_count": 0,
            "durable_authoring_allowed_count": 0,
            "final_durable_release_ready_count": 0,
            "asset_write_performed_count": 0,
            "package_dirty_marked_count": 0,
            "code_change_performed_count": 0,
            "executor_code_modified_count": 0,
            "unreal_asset_modified_count": 0,
            "live_bridge_probe_started_count": 0,
            "save_delete_rename_allowed_count": 0,
            "save_asset_allowed_count": 0,
            "delete_asset_allowed_count": 0,
            "rename_asset_allowed_count": 0,
            "cleanup_allowed_count": 0,
            "live_command_dispatched_count": 0,
            "live_command_executed_count": 0,
        }
        assert (
            final_release_readiness_dry_run_row["actual"]
            == expected_final_release_readiness_dry_run_actual
        )
        release_review_dry_run_row = find_row(
            report,
            "durable_executor_authoring_release_review_dry_run_contract",
        )
        assert release_review_dry_run_row["status"] == "passed"
        assert (
            release_review_dry_run_row["actual"][
                "durable_requested_executor_authoring_release_review_dry_run_count"
            ]
            == 1
        )
        assert release_review_dry_run_row["actual"]["release_review_contract_defined_count"] == 1
        assert (
            release_review_dry_run_row["actual"][
                "section_172_final_release_readiness_contract_ready_count"
            ]
            == 1
        )
        assert release_review_dry_run_row["actual"]["final_release_readiness_chain_satisfied_count"] == 0
        assert release_review_dry_run_row["actual"]["release_review_dry_run_record_present_count"] == 0
        assert release_review_dry_run_row["actual"]["release_review_dry_run_record_valid_count"] == 0
        assert release_review_dry_run_row["actual"]["release_review_dry_run_admissible_count"] == 0
        assert release_review_dry_run_row["actual"]["missing_release_review_dry_run_prerequisite_count"] == 41
        assert release_review_dry_run_row["actual"]["durable_release_review_started_count"] == 0
        assert release_review_dry_run_row["actual"]["durable_release_decision_started_count"] == 0
        assert release_review_dry_run_row["actual"]["durable_executor_command_path_opened_count"] == 0
        assert release_review_dry_run_row["actual"]["durable_authoring_command_allowed_count"] == 0
        assert release_review_dry_run_row["actual"]["save_delete_rename_allowed_count"] == 0
        release_decision_dry_run_row = find_row(
            report,
            "durable_executor_authoring_release_decision_dry_run_contract",
        )
        assert release_decision_dry_run_row["status"] == "passed"
        assert (
            release_decision_dry_run_row["actual"][
                "durable_requested_executor_authoring_release_decision_dry_run_count"
            ]
            == 1
        )
        assert release_decision_dry_run_row["actual"]["release_decision_contract_defined_count"] == 1
        assert (
            release_decision_dry_run_row["actual"][
                "section_173_release_review_contract_ready_count"
            ]
            == 1
        )
        assert release_decision_dry_run_row["actual"]["release_review_chain_satisfied_count"] == 0
        assert release_decision_dry_run_row["actual"]["release_decision_dry_run_record_present_count"] == 0
        assert release_decision_dry_run_row["actual"]["release_decision_dry_run_record_valid_count"] == 0
        assert release_decision_dry_run_row["actual"]["release_decision_dry_run_admissible_count"] == 0
        assert release_decision_dry_run_row["actual"]["missing_release_decision_dry_run_prerequisite_count"] == 43
        assert release_decision_dry_run_row["actual"]["durable_release_decision_started_count"] == 0
        assert release_decision_dry_run_row["actual"]["durable_release_promotion_barrier_started_count"] == 0
        assert release_decision_dry_run_row["actual"]["durable_executor_command_path_opened_count"] == 0
        assert release_decision_dry_run_row["actual"]["durable_authoring_command_allowed_count"] == 0
        assert release_decision_dry_run_row["actual"]["save_delete_rename_allowed_count"] == 0
        promotion_barrier_dry_run_row = find_row(
            report,
            "durable_executor_authoring_release_promotion_barrier_dry_run_contract",
        )
        assert promotion_barrier_dry_run_row["status"] == "passed"
        assert (
            promotion_barrier_dry_run_row["actual"][
                "durable_requested_executor_authoring_release_promotion_barrier_dry_run_count"
            ]
            == 1
        )
        assert (
            promotion_barrier_dry_run_row["actual"][
                "release_promotion_barrier_contract_defined_count"
            ]
            == 1
        )
        assert (
            promotion_barrier_dry_run_row["actual"][
                "section_174_release_decision_contract_ready_count"
            ]
            == 1
        )
        assert promotion_barrier_dry_run_row["actual"]["release_decision_chain_satisfied_count"] == 0
        assert (
            promotion_barrier_dry_run_row["actual"][
                "release_promotion_barrier_dry_run_record_present_count"
            ]
            == 0
        )
        assert (
            promotion_barrier_dry_run_row["actual"][
                "release_promotion_barrier_dry_run_record_valid_count"
            ]
            == 0
        )
        assert (
            promotion_barrier_dry_run_row["actual"][
                "release_promotion_barrier_dry_run_admissible_count"
            ]
            == 0
        )
        assert (
            promotion_barrier_dry_run_row["actual"][
                "missing_release_promotion_barrier_dry_run_prerequisite_count"
            ]
            == 45
        )
        assert promotion_barrier_dry_run_row["actual"]["durable_release_promotion_barrier_started_count"] == 0
        assert promotion_barrier_dry_run_row["actual"]["durable_executor_activation_readiness_started_count"] == 0
        assert promotion_barrier_dry_run_row["actual"]["durable_executor_command_path_opened_count"] == 0
        assert promotion_barrier_dry_run_row["actual"]["durable_authoring_command_allowed_count"] == 0
        assert promotion_barrier_dry_run_row["actual"]["save_delete_rename_allowed_count"] == 0
        activation_readiness_dry_run_row = find_row(
            report,
            "durable_executor_authoring_activation_readiness_dry_run_contract",
        )
        assert activation_readiness_dry_run_row["status"] == "passed"
        assert (
            activation_readiness_dry_run_row["actual"][
                "durable_requested_executor_authoring_activation_readiness_dry_run_count"
            ]
            == 1
        )
        assert (
            activation_readiness_dry_run_row["actual"][
                "activation_readiness_contract_defined_count"
            ]
            == 1
        )
        assert (
            activation_readiness_dry_run_row["actual"][
                "section_175_release_promotion_barrier_contract_ready_count"
            ]
            == 1
        )
        assert (
            activation_readiness_dry_run_row["actual"][
                "release_promotion_barrier_chain_satisfied_count"
            ]
            == 0
        )
        assert (
            activation_readiness_dry_run_row["actual"][
                "activation_readiness_dry_run_record_present_count"
            ]
            == 0
        )
        assert (
            activation_readiness_dry_run_row["actual"][
                "activation_readiness_dry_run_record_valid_count"
            ]
            == 0
        )
        assert (
            activation_readiness_dry_run_row["actual"][
                "activation_readiness_dry_run_admissible_count"
            ]
            == 0
        )
        assert (
            activation_readiness_dry_run_row["actual"][
                "missing_activation_readiness_dry_run_prerequisite_count"
            ]
            == 47
        )
        assert (
            activation_readiness_dry_run_row["actual"][
                "durable_executor_activation_readiness_started_count"
            ]
            == 0
        )
        assert (
            activation_readiness_dry_run_row["actual"][
                "durable_executor_open_contract_started_count"
            ]
            == 0
        )
        assert activation_readiness_dry_run_row["actual"]["durable_executor_command_path_opened_count"] == 0
        assert activation_readiness_dry_run_row["actual"]["durable_authoring_command_allowed_count"] == 0
        assert activation_readiness_dry_run_row["actual"]["save_delete_rename_allowed_count"] == 0
        open_dry_run_row = find_row(
            report,
            "durable_executor_authoring_open_dry_run_contract",
        )
        assert open_dry_run_row["status"] == "passed"
        assert (
            open_dry_run_row["actual"][
                "durable_requested_executor_authoring_open_dry_run_count"
            ]
            == 1
        )
        assert open_dry_run_row["actual"]["open_contract_defined_count"] == 1
        assert (
            open_dry_run_row["actual"][
                "section_176_activation_readiness_contract_ready_count"
            ]
            == 1
        )
        assert open_dry_run_row["actual"]["activation_readiness_chain_satisfied_count"] == 0
        assert open_dry_run_row["actual"]["open_dry_run_record_present_count"] == 0
        assert open_dry_run_row["actual"]["open_dry_run_record_valid_count"] == 0
        assert open_dry_run_row["actual"]["open_dry_run_admissible_count"] == 0
        assert (
            open_dry_run_row["actual"][
                "missing_open_dry_run_prerequisite_count"
            ]
            == 49
        )
        assert open_dry_run_row["actual"]["durable_executor_open_contract_started_count"] == 0
        assert open_dry_run_row["actual"]["durable_executor_opened_count"] == 0
        assert open_dry_run_row["actual"]["durable_executor_command_path_opened_count"] == 0
        assert open_dry_run_row["actual"]["durable_authoring_command_allowed_count"] == 0
        assert open_dry_run_row["actual"]["save_delete_rename_allowed_count"] == 0
        open_promotion_barrier_dry_run_row = find_row(
            report,
            "durable_executor_authoring_open_promotion_barrier_dry_run_contract",
        )
        assert open_promotion_barrier_dry_run_row["status"] == "passed"
        assert (
            open_promotion_barrier_dry_run_row["actual"][
                "durable_requested_executor_authoring_open_promotion_barrier_dry_run_count"
            ]
            == 1
        )
        assert (
            open_promotion_barrier_dry_run_row["actual"][
                "open_promotion_barrier_contract_defined_count"
            ]
            == 1
        )
        assert (
            open_promotion_barrier_dry_run_row["actual"][
                "section_177_open_contract_ready_count"
            ]
            == 1
        )
        assert open_promotion_barrier_dry_run_row["actual"]["open_dry_run_chain_satisfied_count"] == 0
        assert (
            open_promotion_barrier_dry_run_row["actual"][
                "open_promotion_barrier_dry_run_record_present_count"
            ]
            == 0
        )
        assert (
            open_promotion_barrier_dry_run_row["actual"][
                "open_promotion_barrier_dry_run_record_valid_count"
            ]
            == 0
        )
        assert (
            open_promotion_barrier_dry_run_row["actual"][
                "open_promotion_barrier_dry_run_admissible_count"
            ]
            == 0
        )
        assert (
            open_promotion_barrier_dry_run_row["actual"][
                "missing_open_promotion_barrier_dry_run_prerequisite_count"
            ]
            == 51
        )
        assert (
            open_promotion_barrier_dry_run_row["actual"][
                "durable_executor_open_promotion_barrier_started_count"
            ]
            == 0
        )
        assert (
            open_promotion_barrier_dry_run_row["actual"][
                "durable_executor_open_contract_started_count"
            ]
            == 0
        )
        assert open_promotion_barrier_dry_run_row["actual"]["durable_executor_opened_count"] == 0
        assert open_promotion_barrier_dry_run_row["actual"]["durable_executor_command_path_opened_count"] == 0
        assert open_promotion_barrier_dry_run_row["actual"]["durable_authoring_command_allowed_count"] == 0
        assert open_promotion_barrier_dry_run_row["actual"]["save_delete_rename_allowed_count"] == 0
        command_path_dry_run_row = find_row(
            report,
            "durable_executor_authoring_command_path_dry_run_contract",
        )
        assert command_path_dry_run_row["status"] == "passed"
        assert (
            command_path_dry_run_row["actual"][
                "durable_requested_executor_authoring_command_path_dry_run_count"
            ]
            == 1
        )
        assert (
            command_path_dry_run_row["actual"][
                "command_path_contract_defined_count"
            ]
            == 1
        )
        assert (
            command_path_dry_run_row["actual"][
                "section_178_open_promotion_barrier_contract_ready_count"
            ]
            == 1
        )
        assert command_path_dry_run_row["actual"]["open_promotion_barrier_chain_satisfied_count"] == 0
        assert (
            command_path_dry_run_row["actual"][
                "command_path_dry_run_record_present_count"
            ]
            == 0
        )
        assert (
            command_path_dry_run_row["actual"][
                "command_path_dry_run_record_valid_count"
            ]
            == 0
        )
        assert (
            command_path_dry_run_row["actual"][
                "command_path_dry_run_admissible_count"
            ]
            == 0
        )
        assert (
            command_path_dry_run_row["actual"][
                "missing_command_path_dry_run_prerequisite_count"
            ]
            == 53
        )
        assert command_path_dry_run_row["actual"]["durable_executor_command_path_opened_count"] == 0
        assert command_path_dry_run_row["actual"]["durable_executor_command_path_allowed_count"] == 0
        assert command_path_dry_run_row["actual"]["durable_authoring_command_contract_started_count"] == 0
        assert command_path_dry_run_row["actual"]["durable_authoring_command_allowed_count"] == 0
        assert command_path_dry_run_row["actual"]["save_delete_rename_allowed_count"] == 0
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
