#!/usr/bin/env python
"""Offline smoke tests for planner_driven_bp_authoring_smoke.py."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_planner as planner  # noqa: E402
import planner_driven_bp_authoring_smoke as smoke  # noqa: E402


def find_prevented(report: dict, plan_id: str) -> dict:
    for item in report["planner_gate"]["prevented_requests"]:
        if item["id"] == plan_id:
            return item
    raise AssertionError(f"missing prevented request {plan_id}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mcp_planner_driven_smoke_fixture_") as temp_dir:
        output_dir = Path(temp_dir) / "out"
        report = smoke.build_report(smoke.REQUESTS, output_dir, None)
        json_path, md_path = smoke.write_report(report, output_dir)

        assert json_path.exists()
        assert md_path.exists()
        assert report["verdict"]["cxx_changes_required"] is False
        assert report["authoring_job_contract"]["executable_manifest_count"] == 12
        assert report["authoring_job_contract"]["non_executable_manifest_count"] == 7
        assert report["authoring_job_contract"]["non_safe_authoring_command_count"] == 0
        assert report["authoring_job_contract"]["structural_assertion_count"] == 201
        assert report["authoring_job_contract"]["authoring_step_count"] == 166
        assert report["authoring_job_contract"]["component_default_contract_count"] == 6
        assert report["authoring_job_contract"]["component_hierarchy_contract_count"] == 1
        assert report["authoring_job_contract"]["component_property_contract_count"] == 1
        assert report["authoring_job_contract"]["function_call_contract_count"] == 4
        assert report["authoring_job_contract"]["graph_layout_contract_count"] == 38
        assert report["authoring_job_contract"]["graph_layout_spacing_contract_count"] == 54
        assert report["authoring_job_contract"]["durable_authoring_request_count"] == 1
        assert report["authoring_job_contract"]["durable_authoring_eligible_count"] == 0
        assert report["authoring_job_contract"]["durable_preflight_request_count"] == 1
        assert report["authoring_job_contract"]["durable_preflight_pass_count"] == 0
        assert report["authoring_job_contract"]["durable_overwrite_rename_decision_required_count"] == 1
        assert report["authoring_job_contract"]["durable_overwrite_rename_decision_present_count"] == 0
        assert report["authoring_job_contract"]["durable_overwrite_rename_decision_conflict_count"] == 0
        assert report["authoring_job_contract"]["durable_save_gate_request_count"] == 1
        assert report["authoring_job_contract"]["durable_save_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_rollback_policy_ready_count"] == 0
        assert report["authoring_job_contract"]["durable_executor_readiness_request_count"] == 1
        assert report["authoring_job_contract"]["durable_executor_ready_count"] == 0
        assert report["authoring_job_contract"]["durable_executor_skeleton_request_count"] == 1
        assert report["authoring_job_contract"]["durable_executor_skeleton_enabled_count"] == 0
        assert report["authoring_job_contract"]["durable_executor_skeleton_executable_count"] == 0
        assert report["authoring_job_contract"]["durable_executor_skeleton_command_count"] == 0
        assert report["authoring_job_contract"]["durable_ownership_marker_request_count"] == 1
        assert report["authoring_job_contract"]["durable_ownership_marker_policy_ready_count"] == 1
        assert report["authoring_job_contract"]["durable_ownership_delete_without_marker_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_ownership_delete_preexisting_asset_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_dry_run_plan_request_count"] == 1
        assert report["authoring_job_contract"]["durable_dry_run_plan_created_count"] == 1
        assert report["authoring_job_contract"]["durable_dry_run_plan_valid_count"] == 1
        assert report["authoring_job_contract"]["durable_dry_run_executor_may_execute_count"] == 0
        assert report["authoring_job_contract"]["durable_dry_run_live_command_count"] == 0
        assert report["authoring_job_contract"]["durable_dry_run_forbidden_command_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_save_simulation_request_count"] == 1
        assert report["authoring_job_contract"]["durable_save_simulation_evaluated_count"] == 1
        assert report["authoring_job_contract"]["durable_save_simulation_conditions_satisfied_count"] == 0
        assert report["authoring_job_contract"]["durable_save_simulation_save_true_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_save_simulation_save_asset_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_save_simulation_compile_save_command_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_save_simulation_live_command_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_prep_request_count"] == 1
        assert report["authoring_job_contract"]["durable_canary_prep_ready_count"] == 1
        assert report["authoring_job_contract"]["durable_canary_live_execution_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_general_blueprints_package_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_save_true_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_save_asset_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_delete_asset_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_approval_request_count"] == 1
        assert report["authoring_job_contract"]["durable_canary_approval_record_present_count"] == 1
        assert report["authoring_job_contract"]["durable_canary_approval_gate_passed_count"] == 1
        assert report["authoring_job_contract"]["durable_canary_approval_scoped_to_canary_package_count"] == 1
        assert report["authoring_job_contract"]["durable_canary_executor_may_open_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_approval_live_execution_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_approval_general_blueprints_package_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_approval_save_true_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_approval_save_asset_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_approval_delete_asset_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_approval_live_command_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_live_preflight_request_count"] == 1
        assert report["authoring_job_contract"]["durable_canary_live_preflight_read_only_allowed_count"] == 1
        assert report["authoring_job_contract"]["durable_canary_live_preflight_execution_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_live_preflight_authoring_command_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_live_preflight_save_or_delete_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_live_preflight_cleanup_command_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_live_preflight_authoring_command_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_live_preflight_save_or_delete_command_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_live_preflight_cleanup_command_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_bridge_refresh_request_count"] == 1
        assert report["authoring_job_contract"]["durable_canary_bridge_refresh_required_count"] == 1
        assert report["authoring_job_contract"]["durable_canary_bridge_refresh_reachable_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_bridge_refresh_read_only_result_refreshed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_bridge_refresh_satisfied_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_bridge_refresh_execution_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_bridge_refresh_executor_may_open_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_bridge_refresh_save_or_delete_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_bridge_refresh_cleanup_command_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_bridge_refresh_live_authoring_command_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_bridge_refresh_live_save_or_delete_command_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_bridge_refresh_live_cleanup_command_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_recovery_request_count"] == 1
        assert report["authoring_job_contract"]["durable_canary_recovery_matrix_ready_count"] == 1
        assert report["authoring_job_contract"]["durable_canary_recovery_scenario_count"] == 6
        assert report["authoring_job_contract"]["durable_canary_recovery_cleanup_command_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_recovery_delete_command_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_recovery_save_command_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_recovery_authoring_command_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_recovery_live_cleanup_command_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_recovery_live_delete_command_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_recovery_live_save_command_count"] == 0
        assert report["authoring_job_contract"]["durable_canary_recovery_live_authoring_command_count"] == 0
        assert report["authoring_job_contract"]["durable_enable_contract_request_count"] == 1
        assert report["authoring_job_contract"]["durable_enable_contract_satisfied_count"] == 0
        assert report["authoring_job_contract"]["durable_enable_executor_may_open_count"] == 0
        assert report["authoring_job_contract"]["durable_enable_authoring_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_enable_forbidden_command_allowed_count"] == 0
        assert report["authoring_job_contract"]["durable_enable_failed_required_gate_count"] == 2
        assert report["authoring_job_contract"]["durable_enable_target_package_allowlist_passed_count"] == 1
        assert report["authoring_job_contract"]["durable_enable_overwrite_rename_decision_passed_count"] == 0
        assert report["authoring_job_contract"]["durable_enable_rollback_readiness_passed_count"] == 0
        assert report["authoring_job_contract"]["durable_enable_ownership_marker_passed_count"] == 1
        assert report["manifest_executor"]["executor_version"] == smoke.manifest_executor.EXECUTOR_VERSION
        assert report["manifest_executor"]["executable_by_executor_count"] == 12
        assert report["manifest_executor"]["blocked_by_executor_count"] == 7
        assert report["manifest_executor"]["temporary_scope_only"] is True
        assert report["manifest_executor"]["durable_authoring_allowed"] is False
        assert report["manifest_executor"]["save_allowed"] is False
        assert report["manifest_executor"]["save_step_count"] == 0
        assert report["manifest_executor"]["unknown_command_count"] == 0
        assert report["manifest_executor"]["forbidden_command_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["status"] == "passed"
        assert report["manifest_executor"]["durable_gate_summary"]["durable_requested_manifest_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["read_only_live_preflight_allowed_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["durable_enable_contract_satisfied_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["durable_enable_executor_may_open_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["durable_enable_failed_required_gate_count"] == 2
        assert report["manifest_executor"]["durable_gate_summary"]["ownership_marker_policy_ready_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["delete_without_ownership_marker_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["delete_preexisting_asset_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["dry_run_plan_created_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["dry_run_plan_valid_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["dry_run_plan_executor_may_execute_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["dry_run_plan_live_command_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["save_simulation_evaluated_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["save_simulation_conditions_satisfied_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["save_simulation_save_true_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["save_simulation_save_asset_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["save_simulation_live_command_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_prep_ready_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["canary_live_execution_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_general_blueprints_package_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_save_true_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_save_asset_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_delete_asset_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_approval_record_present_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["canary_approval_gate_passed_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["canary_approval_scoped_to_canary_package_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["canary_approval_executor_may_open_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_approval_live_execution_allowed_count"] == 0
        assert (
            report["manifest_executor"]["durable_gate_summary"][
                "canary_approval_general_blueprints_package_allowed_count"
            ]
            == 0
        )
        assert report["manifest_executor"]["durable_gate_summary"]["canary_approval_save_true_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_approval_save_asset_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_approval_delete_asset_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_approval_live_command_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_live_preflight_read_only_allowed_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["canary_live_preflight_execution_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_live_preflight_authoring_allowed_count"] == 0
        assert (
            report["manifest_executor"]["durable_gate_summary"][
                "canary_live_preflight_save_or_delete_allowed_count"
            ]
            == 0
        )
        assert report["manifest_executor"]["durable_gate_summary"]["canary_live_preflight_cleanup_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_live_preflight_authoring_command_count"] == 0
        assert (
            report["manifest_executor"]["durable_gate_summary"][
                "canary_live_preflight_save_or_delete_command_count"
            ]
            == 0
        )
        assert report["manifest_executor"]["durable_gate_summary"]["canary_live_preflight_cleanup_command_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_bridge_refresh_required_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["canary_bridge_refresh_reachable_count"] == 0
        assert (
            report["manifest_executor"]["durable_gate_summary"][
                "canary_bridge_refresh_read_only_result_refreshed_count"
            ]
            == 0
        )
        assert report["manifest_executor"]["durable_gate_summary"]["canary_bridge_refresh_satisfied_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_bridge_refresh_execution_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_bridge_refresh_executor_may_open_count"] == 0
        assert (
            report["manifest_executor"]["durable_gate_summary"][
                "canary_bridge_refresh_save_or_delete_allowed_count"
            ]
            == 0
        )
        assert report["manifest_executor"]["durable_gate_summary"]["canary_bridge_refresh_cleanup_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_bridge_refresh_authoring_command_count"] == 0
        assert (
            report["manifest_executor"]["durable_gate_summary"][
                "canary_bridge_refresh_save_or_delete_command_count"
            ]
            == 0
        )
        assert report["manifest_executor"]["durable_gate_summary"]["canary_bridge_refresh_cleanup_command_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_recovery_matrix_ready_count"] == 1
        assert report["manifest_executor"]["durable_gate_summary"]["canary_recovery_scenario_count"] == 6
        assert report["manifest_executor"]["durable_gate_summary"]["canary_recovery_cleanup_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_recovery_delete_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_recovery_save_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_recovery_authoring_allowed_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_recovery_live_cleanup_command_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_recovery_live_delete_command_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_recovery_live_save_command_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["canary_recovery_live_authoring_command_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["durable_executor_enabled_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["durable_executor_executable_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["allowed_live_authoring_command_count"] == 0
        assert report["manifest_executor"]["durable_gate_summary"]["save_or_delete_commands_allowed_count"] == 0
        assert report["manifest_executor"]["capability_summary"]["typed_defaults"]["ready_manifest_count"] == 5
        assert report["manifest_executor"]["capability_summary"]["graph_layout_dataflow"]["ready_manifest_count"] == 11
        assert report["manifest_executor"]["capability_summary"]["function_graph_executor"]["ready_manifest_count"] == 5
        assert report["manifest_executor"]["capability_summary"]["dispatcher_lifecycle_executor"]["ready_manifest_count"] == 1
        assert report["planner_gate"]["safe_request_count"] == 12
        assert report["planner_gate"]["requires_review_request_count"] == 1
        assert report["planner_gate"]["blocked_until_reinforced_request_count"] == 3
        assert report["planner_gate"]["prevented_request_count"] == 7
        assert report["planner_gate"]["status_counts"][planner.STATUS_SAFE] == 15
        assert report["planner_gate"]["status_counts"][planner.STATUS_REVIEW] == 1
        assert report["planner_gate"]["status_counts"][planner.STATUS_BLOCKED] == 3
        assert report["live_gate"]["status"] == "not_requested"
        assert report["live_gate"]["durable_live_preflight_gate"]["status"] == "not_requested"
        assert report["live_gate"]["durable_live_preflight_gate"]["durable_preflight_requested_manifest_count"] == 1
        assert report["live_gate"]["durable_canary_live_preflight_gate"]["status"] == "not_requested"
        assert (
            report["live_gate"]["durable_canary_live_preflight_gate"][
                "durable_canary_preflight_requested_manifest_count"
            ]
            == 1
        )

        safe_ids = {item["id"] for item in report["planner_gate"]["authoring_queue"]}
        assert safe_ids == {
            "safe_actor_shell",
            "safe_function_call_defaults",
            "safe_component_hierarchy",
            "safe_component_property_defaults",
            "safe_function_graph_authoring",
            "safe_function_graph_body_math",
            "safe_function_graph_local_set",
            "safe_function_graph_compare_branch",
            "safe_typed_variables_defaults",
            "safe_event_sequence_flow",
            "safe_generated_function_invocation",
            "safe_event_dispatcher",
        }

        review_umg = find_prevented(report, "review_umg_button")
        assert review_umg["status"] == planner.STATUS_REVIEW
        assert review_umg["authoring_attempted"] is False

        unsupported_property = find_prevented(report, "review_component_property_unsupported")
        assert unsupported_property["status"] == planner.STATUS_SAFE
        assert unsupported_property["authoring_attempted"] is False
        assert any(
            item["key"] == "contract_unsupported_component_property"
            for item in unsupported_property["blocked_review_reasons"]
        )

        unsupported_parent = find_prevented(report, "review_parent_class_unsupported")
        assert unsupported_parent["status"] == planner.STATUS_SAFE
        assert unsupported_parent["authoring_attempted"] is False
        assert any(
            item["key"] == "contract_unsupported_parent_class"
            for item in unsupported_parent["blocked_review_reasons"]
        )

        durable_save = find_prevented(report, "review_durable_authoring_save_requested")
        assert durable_save["status"] == planner.STATUS_SAFE
        assert durable_save["authoring_attempted"] is False
        assert durable_save["durable_preflight_contract"]["target_asset_path"] == "/Game/Blueprints/BP_PlannerDurable"
        assert durable_save["durable_preflight_contract"]["preflight_pass"] is False
        assert durable_save["durable_preflight_contract"]["overwrite_rename_decision_contract"]["decision"] == "missing"
        assert durable_save["durable_preflight_contract"]["durable_enable_contract"]["enable_contract_satisfied"] is False
        assert durable_save["durable_preflight_contract"]["durable_enable_contract"]["durable_executor_may_open"] is False
        assert durable_save["durable_preflight_contract"]["durable_enable_contract"]["failed_required_gate_ids"] == [
            "overwrite_rename_decision",
            "rollback_readiness",
        ]
        assert durable_save["durable_preflight_contract"]["durable_ownership_marker_contract"][
            "ownership_marker_policy_ready"
        ] is True
        assert durable_save["durable_preflight_contract"]["durable_dry_run_plan_contract"]["dry_run_plan_valid"] is True
        assert (
            durable_save["durable_preflight_contract"]["durable_dry_run_plan_contract"]["durable_executor_may_execute"]
            is False
        )
        assert durable_save["durable_preflight_contract"]["durable_save_validation_simulation_contract"][
            "simulation_evaluated"
        ] is True
        assert durable_save["durable_preflight_contract"]["durable_save_validation_simulation_contract"][
            "save_true_allowed"
        ] is False
        assert durable_save["durable_preflight_contract"]["durable_canary_prep_contract"]["canary_prep_ready"] is True
        assert (
            durable_save["durable_preflight_contract"]["durable_canary_prep_contract"]["canary_live_execution_allowed"]
            is False
        )
        assert (
            durable_save["durable_preflight_contract"]["durable_canary_prep_contract"][
                "general_blueprints_package_allowed"
            ]
            is False
        )
        assert (
            durable_save["durable_preflight_contract"]["durable_canary_approval_gate_contract"][
                "canary_approval_gate_passed"
            ]
            is True
        )
        assert (
            durable_save["durable_preflight_contract"]["durable_canary_approval_gate_contract"][
                "canary_executor_may_open"
            ]
            is False
        )
        assert (
            durable_save["durable_preflight_contract"]["durable_canary_approval_gate_contract"][
                "canary_live_execution_allowed"
            ]
            is False
        )
        assert (
            durable_save["durable_preflight_contract"]["durable_canary_live_preflight_contract"][
                "read_only_live_preflight_allowed"
            ]
            is True
        )
        assert (
            durable_save["durable_preflight_contract"]["durable_canary_live_preflight_contract"][
                "canary_execution_allowed_after_preflight"
            ]
            is False
        )
        assert (
            durable_save["durable_preflight_contract"]["durable_canary_bridge_refresh_contract"][
                "bridge_refresh_required"
            ]
            is True
        )
        assert (
            durable_save["durable_preflight_contract"]["durable_canary_bridge_refresh_contract"][
                "bridge_refresh_satisfied"
            ]
            is False
        )
        assert (
            durable_save["durable_preflight_contract"]["durable_canary_bridge_refresh_contract"][
                "durable_executor_may_open_after_refresh"
            ]
            is False
        )
        assert (
            durable_save["durable_preflight_contract"]["durable_canary_recovery_matrix_contract"][
                "recovery_matrix_ready"
            ]
            is True
        )
        assert (
            durable_save["durable_preflight_contract"]["durable_canary_recovery_matrix_contract"][
                "cleanup_command_allowed"
            ]
            is False
        )
        assert durable_save["durable_preflight_contract"]["durable_save_gate_contract"]["save_allowed"] is False
        assert "rollback_policy_not_ready" in durable_save["durable_preflight_contract"]["durable_save_gate_contract"]["blocked_by"]
        assert durable_save["durable_preflight_contract"]["durable_executor_readiness_contract"]["durable_executor_ready"] is False
        assert (
            "explicit_durable_executor_enable_flag"
            in durable_save["durable_preflight_contract"]["durable_executor_readiness_contract"]["failing_checks"]
        )
        assert durable_save["durable_executor_skeleton_contract"]["executor_enabled"] is False
        assert durable_save["durable_executor_skeleton_contract"]["can_execute"] is False
        assert durable_save["durable_executor_skeleton_contract"]["command_plan"] == []
        assert durable_save["durable_executor_skeleton_contract"]["allowed_live_command_count"] == 0
        assert "save_asset" in durable_save["durable_executor_skeleton_contract"]["forbidden_commands"]
        durable_executor_policy = next(
            policy
            for policy in report["manifest_executor"]["policies"]
            if policy["manifest_id"] == "review_durable_authoring_save_requested"
        )
        assert durable_executor_policy["durable_executor_gate"]["status"] == "blocked_save_authoring_read_only_preflight_allowed"
        assert durable_executor_policy["durable_executor_gate"]["read_only_live_preflight_allowed"] is True
        assert durable_executor_policy["durable_executor_gate"]["durable_enable_contract_satisfied"] is False
        assert durable_executor_policy["durable_executor_gate"]["durable_enable_executor_may_open"] is False
        assert durable_executor_policy["durable_executor_gate"]["dry_run_plan_valid"] is True
        assert durable_executor_policy["durable_executor_gate"]["dry_run_plan_executor_may_execute"] is False
        assert durable_executor_policy["durable_executor_gate"]["save_simulation_evaluated"] is True
        assert durable_executor_policy["durable_executor_gate"]["save_simulation_save_true_allowed"] is False
        assert durable_executor_policy["durable_executor_gate"]["canary_prep_ready"] is True
        assert durable_executor_policy["durable_executor_gate"]["canary_live_execution_allowed"] is False
        assert durable_executor_policy["durable_executor_gate"]["canary_general_blueprints_package_allowed"] is False
        assert durable_executor_policy["durable_executor_gate"]["canary_approval_gate_passed"] is True
        assert durable_executor_policy["durable_executor_gate"]["canary_approval_executor_may_open"] is False
        assert durable_executor_policy["durable_executor_gate"]["canary_approval_live_execution_allowed"] is False
        assert durable_executor_policy["durable_executor_gate"]["canary_live_preflight_read_only_allowed"] is True
        assert durable_executor_policy["durable_executor_gate"]["canary_live_preflight_execution_allowed"] is False
        assert durable_executor_policy["durable_executor_gate"]["canary_live_preflight_save_or_delete_allowed"] is False
        assert durable_executor_policy["durable_executor_gate"]["canary_bridge_refresh_required"] is True
        assert durable_executor_policy["durable_executor_gate"]["canary_bridge_refresh_satisfied"] is False
        assert durable_executor_policy["durable_executor_gate"]["canary_bridge_refresh_executor_may_open"] is False
        assert durable_executor_policy["durable_executor_gate"]["canary_bridge_refresh_save_or_delete_allowed"] is False
        assert durable_executor_policy["durable_executor_gate"]["canary_recovery_matrix_ready"] is True
        assert durable_executor_policy["durable_executor_gate"]["canary_recovery_cleanup_allowed"] is False
        assert durable_executor_policy["durable_executor_gate"]["canary_recovery_delete_allowed"] is False
        assert durable_executor_policy["durable_executor_gate"]["save_allowed"] is False
        assert durable_executor_policy["durable_executor_gate"]["save_or_delete_commands_allowed"] is False
        assert any(
            item["key"] == "contract_durable_executor_not_enabled"
            for item in durable_save["blocked_review_reasons"]
        )

        blocked_async = find_prevented(report, "blocked_async_proxy")
        assert blocked_async["status"] == planner.STATUS_BLOCKED
        assert blocked_async["authoring_attempted"] is False
        assert any(item["key"] == "async_proxy_callback_exec" for item in blocked_async["blocked_items"])

        blocked_gas = find_prevented(report, "blocked_gas_replication")
        assert any(item["key"] == "gas_ability_task" for item in blocked_gas["blocked_items"])
        assert any(item["key"] == "replication_rpc" for item in blocked_gas["blocked_items"])

        blocked_commonui = find_prevented(report, "blocked_commonui")
        assert any(item["key"] == "commonui_structure" for item in blocked_commonui["blocked_items"])

        assert not (output_dir.parent / "planner_driven_bp_authoring_smoke_report.json").exists()

        custom_temp_path = "/Game/_MCP_Temp/PlannerDrivenSmokeCustom"
        custom_report = smoke.build_report(smoke.REQUESTS, output_dir, None, temp_package_path=custom_temp_path)
        assert custom_report["temp_package_path"] == custom_temp_path

        executed_plan_ids: list[str] = []
        originals = {
            "bridge_available": smoke.bridge_available,
            "require_success": smoke.require_success,
            "execute_python_json": smoke.execute_python_json,
            "list_temp_assets": smoke.list_temp_assets,
            "run_safe_manifest": smoke.run_safe_manifest,
            "snapshot_logs": smoke.quality_gate.snapshot_logs,
            "collect_new_log_errors": smoke.quality_gate.collect_new_log_errors,
        }

        def fake_require_success(host, port, command, params, stage_results, timeout=60.0):
            stage_results.append({"command": command, "status": "success"})
            if command == "ping":
                return {"message": "pong"}
            raise AssertionError(f"offline live fake should not execute command {command}")

        def fake_execute_python_json(host, port, code, stage_results, timeout=60.0):
            stage_results.append({"command": "execute_python", "status": "success"})
            if "does_asset_exist(target_asset_path)" in code:
                return {
                    "target_asset_path": "/Game/Blueprints/BP_PlannerDurable",
                    "asset_exists": False,
                }
            if "does_asset_exist(canary_asset_path)" in code:
                return {
                    "canary_asset_path": "/Game/_MCP_Temp/DurableCanary/BP_PlannerDurable_Canary",
                    "asset_exists": False,
                }
            return {
                "project_file": "D:/Git/CubelessStylized/StylizedCubeless.uproject",
                "project_dir": "D:/Git/CubelessStylized/",
                "engine_version": "offline-test",
            }

        def fake_run_safe_manifest(host, port, manifest, temp_package_path, run_id, keep_assets):
            executed_plan_ids.append(manifest["id"])
            return {
                "plan_id": manifest["id"],
                "manifest_id": manifest["id"],
                "status": "passed",
                "executor_version": smoke.manifest_executor.EXECUTOR_VERSION,
                "asset_path": f"{temp_package_path}/MCP_PlannerSmoke_{manifest['id']}_{run_id}",
                "execution": {"validation": {"validation_pass": True, "compile_error_count": 0}},
                "cleanup": {"deleted": True},
            }

        try:
            smoke.bridge_available = lambda host, port: True
            smoke.require_success = fake_require_success
            smoke.execute_python_json = fake_execute_python_json
            smoke.list_temp_assets = lambda host, port, temp_package_path, stage_results: []
            smoke.run_safe_manifest = fake_run_safe_manifest
            smoke.quality_gate.snapshot_logs = lambda project_root: {}
            smoke.quality_gate.collect_new_log_errors = lambda project_root, before: []

            live_result = smoke.run_live_smoke(
                smoke.build_manifests(smoke.REQUESTS, smoke.DEFAULT_TEMP_PACKAGE_PATH),
                host="127.0.0.1",
                port=55557,
                project_root=None,
                expected_project_file="StylizedCubeless.uproject",
                temp_package_path=smoke.DEFAULT_TEMP_PACKAGE_PATH,
                keep_assets=False,
                require_live=True,
            )
        finally:
            smoke.bridge_available = originals["bridge_available"]
            smoke.require_success = originals["require_success"]
            smoke.execute_python_json = originals["execute_python_json"]
            smoke.list_temp_assets = originals["list_temp_assets"]
            smoke.run_safe_manifest = originals["run_safe_manifest"]
            smoke.quality_gate.snapshot_logs = originals["snapshot_logs"]
            smoke.quality_gate.collect_new_log_errors = originals["collect_new_log_errors"]

        assert live_result["status"] == "passed"
        assert live_result["non_safe_authoring_attempted"] is False
        assert live_result["durable_authoring_attempted"] is False
        assert live_result["durable_live_save_or_delete_attempted"] is False
        assert live_result["durable_canary_authoring_attempted"] is False
        assert live_result["durable_canary_save_or_delete_attempted"] is False
        assert live_result["durable_canary_cleanup_attempted"] is False
        assert live_result["durable_canary_execution_attempted"] is False
        assert live_result["durable_live_preflight_gate"]["status"] == "passed"
        assert live_result["durable_live_preflight_gate"]["passed_read_only_result_count"] == 1
        assert live_result["durable_live_preflight_gate"]["authoring_attempted_count"] == 0
        assert live_result["durable_live_preflight_gate"]["save_or_delete_attempted_count"] == 0
        assert live_result["durable_canary_live_preflight_gate"]["status"] == "passed"
        assert live_result["durable_canary_live_preflight_gate"]["passed_read_only_result_count"] == 1
        assert live_result["durable_canary_live_preflight_gate"]["authoring_attempted_count"] == 0
        assert live_result["durable_canary_live_preflight_gate"]["save_or_delete_attempted_count"] == 0
        assert live_result["durable_canary_live_preflight_gate"]["cleanup_attempted_count"] == 0
        assert live_result["durable_canary_live_preflight_gate"]["canary_execution_attempted_count"] == 0
        assert len(live_result["durable_preflight_live_results"]) == 1
        durable_live_result = live_result["durable_preflight_live_results"][0]
        assert durable_live_result["schema"] == "section_35_durable_preflight_live_result_v1"
        assert durable_live_result["manifest_id"] == "review_durable_authoring_save_requested"
        assert durable_live_result["target_asset_path"] == "/Game/Blueprints/BP_PlannerDurable"
        assert durable_live_result["status"] == "passed"
        assert durable_live_result["read_only"] is True
        assert durable_live_result["authoring_attempted"] is False
        assert durable_live_result["save_or_delete_attempted"] is False
        assert durable_live_result["asset_exists_check_performed"] is True
        assert durable_live_result["asset_exists"] is False
        assert durable_live_result["preflight_pass"] is False
        assert len(live_result["durable_canary_preflight_live_results"]) == 1
        canary_live_result = live_result["durable_canary_preflight_live_results"][0]
        assert canary_live_result["schema"] == "section_57_durable_canary_live_preflight_result_v1"
        assert canary_live_result["manifest_id"] == "review_durable_authoring_save_requested"
        assert canary_live_result["canary_asset_path"] == "/Game/_MCP_Temp/DurableCanary/BP_PlannerDurable_Canary"
        assert canary_live_result["status"] == "passed"
        assert canary_live_result["read_only"] is True
        assert canary_live_result["authoring_attempted"] is False
        assert canary_live_result["save_or_delete_attempted"] is False
        assert canary_live_result["cleanup_attempted"] is False
        assert canary_live_result["canary_execution_attempted"] is False
        assert canary_live_result["asset_exists_check_performed"] is True
        assert canary_live_result["asset_exists"] is False
        assert canary_live_result["canary_execution_allowed_after_preflight"] is False
        assert executed_plan_ids == [
            "safe_actor_shell",
            "safe_function_call_defaults",
            "safe_component_hierarchy",
            "safe_component_property_defaults",
            "safe_function_graph_authoring",
            "safe_function_graph_body_math",
            "safe_function_graph_local_set",
            "safe_function_graph_compare_branch",
            "safe_typed_variables_defaults",
            "safe_event_sequence_flow",
            "safe_generated_function_invocation",
            "safe_event_dispatcher",
        ]
        assert all(item["authoring_attempted"] is False for item in live_result["prevented_requests"])
        assert any(item["id"] == "review_component_property_unsupported" for item in live_result["prevented_requests"])
        assert any(item["id"] == "review_parent_class_unsupported" for item in live_result["prevented_requests"])
        live_durable_save = find_prevented({"planner_gate": live_result}, "review_durable_authoring_save_requested")
        assert live_durable_save["durable_preflight_contract"]["target_asset_path"] == "/Game/Blueprints/BP_PlannerDurable"
        assert live_durable_save["durable_preflight_contract"]["preflight_pass"] is False
        assert live_durable_save["durable_preflight_live_result"] == durable_live_result
        assert live_durable_save["durable_canary_preflight_live_result"] == canary_live_result
        live_report = smoke.build_report(smoke.REQUESTS, output_dir, live_result)
        report_durable_save = next(
            item
            for item in live_report["live_gate"]["prevented_requests"]
            if item["id"] == "review_durable_authoring_save_requested"
        )
        assert report_durable_save["durable_preflight_live_result"] == durable_live_result
        assert report_durable_save["durable_canary_preflight_live_result"] == canary_live_result
        assert live_report["live_gate"]["non_safe_authoring_attempted"] is False
        assert live_report["live_gate"]["durable_authoring_attempted"] is False
        assert live_report["live_gate"]["durable_live_save_or_delete_attempted"] is False
        assert live_report["live_gate"]["durable_canary_execution_attempted"] is False
        assert live_report["live_gate"]["durable_canary_cleanup_attempted"] is False
        assert live_report["live_gate"]["durable_live_preflight_gate"]["status"] == "passed"
        assert live_report["live_gate"]["durable_live_preflight_gate"]["read_only_only"] is True
        assert live_report["live_gate"]["durable_canary_live_preflight_gate"]["status"] == "passed"
        assert live_report["live_gate"]["durable_canary_live_preflight_gate"]["read_only_only"] is True
        assert live_report["verdict"]["executor_version"] == smoke.manifest_executor.EXECUTOR_VERSION
        assert live_report["verdict"]["executor_executable_manifests"] == 12

        failure_originals = {
            "require_success": smoke.require_success,
            "cleanup_generated_asset": smoke.cleanup_generated_asset,
        }
        failure_manifest = smoke.build_manifests([smoke.REQUESTS[0]], smoke.DEFAULT_TEMP_PACKAGE_PATH)[0]

        def fake_failure_require_success(host, port, command, params, stage_results, timeout=60.0):
            status = "failed" if command == "add_blueprint_variable" else "success"
            stage_results.append({"command": command, "status": status})
            if command == "add_blueprint_variable":
                raise smoke.quality_gate.BridgeError("synthetic variable authoring failure")
            return {"node_id": f"{command}_node", "pins": [], "validation_pass": True, "compile_error_count": 0}

        try:
            smoke.require_success = fake_failure_require_success
            smoke.cleanup_generated_asset = lambda host, port, asset_path, stage_results: {"asset_path": asset_path, "deleted": True}

            failed_execution = smoke.run_safe_manifest(
                host="127.0.0.1",
                port=55557,
                manifest=failure_manifest,
                temp_package_path=smoke.DEFAULT_TEMP_PACKAGE_PATH,
                run_id="failure",
                keep_assets=False,
            )
        finally:
            smoke.require_success = failure_originals["require_success"]
            smoke.cleanup_generated_asset = failure_originals["cleanup_generated_asset"]

        assert failed_execution["status"] == "failed"
        assert failed_execution["cleanup"]["deleted"] is True
        failure_diagnostics = failed_execution["failure_diagnostics"]
        assert failure_diagnostics["diagnostic_schema"] == smoke.manifest_executor.FAILURE_DIAGNOSTIC_SCHEMA
        assert failure_diagnostics["legacy_diagnostic_schema"] == "section_21_failure_diagnostics_v1"
        assert failure_diagnostics["executor_version"] == smoke.manifest_executor.EXECUTOR_VERSION
        assert failure_diagnostics["failure_category"] == "manifest_step_failure"
        assert failure_diagnostics["replay_safety"]["durable_side_effects_allowed"] is False
        assert failure_diagnostics["replay_safety"]["safe_to_replay_authoring"] is False
        assert failure_diagnostics["phase"] == "manifest_step"
        assert failure_diagnostics["section"] == "variables_defaults"
        assert failure_diagnostics["step_id"] == "variable_health"
        assert failure_diagnostics["command"] == "add_blueprint_variable"
        assert failure_diagnostics["error"] == "synthetic variable authoring failure"
        assert failure_diagnostics["stage_tail"][-1] == {"command": "add_blueprint_variable", "status": "failed"}
        assert failed_execution["diagnostics"]["failed_step_id"] == "variable_health"

    print("planner-driven BP authoring smoke offline test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
