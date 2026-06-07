#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_job_contract.py."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_job_contract as contract  # noqa: E402
import bp_authoring_planner as planner  # noqa: E402


def find_manifest(report: dict, manifest_id: str) -> dict:
    for manifest in report["manifests"]:
        if manifest["id"] == manifest_id:
            return manifest
    raise AssertionError(f"missing manifest {manifest_id}")


def assert_no_authoring_steps(manifest: dict) -> None:
    assert manifest["executable"] is False
    assert manifest["component_list"] == []
    assert manifest["component_default_steps"] == []
    assert manifest["component_default_contracts"] == []
    assert manifest["component_hierarchy_contracts"] == []
    assert manifest["component_property_contracts"] == []
    assert manifest["variables_defaults"] == []
    assert manifest["event_graph_steps"] == []
    assert manifest["function_graph_steps"] == []
    assert manifest["function_call_contracts"] == []
    assert manifest["graph_layout_contracts"] == []
    assert manifest["graph_layout_spacing_contracts"] == []
    assert manifest["generated_function_invocation_steps"] == []
    assert manifest["dispatcher_lifecycle_steps"] == []
    assert manifest["structural_validation_plan"] == []
    assert contract.manifest_has_authoring_commands(manifest) is False


def command_ids(steps: list[dict]) -> set[str]:
    return {step["id"] for step in steps}


def compile_steps(manifest: dict) -> list[dict]:
    steps: list[dict] = []
    for section in (
        "event_graph_steps",
        "function_graph_steps",
        "generated_function_invocation_steps",
        "dispatcher_lifecycle_steps",
        "validation_plan",
    ):
        steps.extend(step for step in manifest.get(section, []) if step.get("command") == "compile_and_validate_blueprint")
    return steps


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mcp_bp_authoring_job_contract_fixture_") as temp_dir:
        output_dir = Path(temp_dir) / "out"
        custom_temp_path = "/Game/_MCP_Temp/PlannerDrivenSmokeContract"
        report = contract.build_report(
            contract.DEFAULT_SAMPLE_REQUESTS,
            output_dir,
            temp_package_path=custom_temp_path,
        )
        json_path, md_path = contract.write_report(report, output_dir)

        assert json_path.exists()
        assert md_path.exists()
        assert report["manifest_version"] == contract.MANIFEST_VERSION
        assert report["temp_package_path"] == custom_temp_path
        assert report["summary"]["manifest_count"] == 19
        assert report["summary"]["executable_manifest_count"] == 12
        assert report["summary"]["non_executable_manifest_count"] == 7
        assert report["summary"]["non_safe_authoring_command_count"] == 0
        assert report["summary"]["structural_assertion_count"] == 201
        assert report["summary"]["authoring_step_count"] == 166
        assert report["summary"]["component_default_contract_count"] == 6
        assert report["summary"]["component_hierarchy_contract_count"] == 1
        assert report["summary"]["component_property_contract_count"] == 1
        assert report["summary"]["function_call_contract_count"] == 4
        assert report["summary"]["graph_layout_contract_count"] == 38
        assert report["summary"]["graph_layout_spacing_contract_count"] == 54
        assert report["summary"]["status_counts"][planner.STATUS_SAFE] == 15
        assert report["summary"]["status_counts"][planner.STATUS_REVIEW] == 1
        assert report["summary"]["status_counts"][planner.STATUS_BLOCKED] == 3
        assert report["summary"]["durable_authoring_request_count"] == 1
        assert report["summary"]["durable_authoring_eligible_count"] == 0
        assert report["summary"]["durable_preflight_request_count"] == 1
        assert report["summary"]["durable_preflight_pass_count"] == 0
        assert report["summary"]["durable_overwrite_rename_decision_required_count"] == 1
        assert report["summary"]["durable_overwrite_rename_decision_present_count"] == 0
        assert report["summary"]["durable_overwrite_rename_decision_conflict_count"] == 0
        assert report["summary"]["durable_save_gate_request_count"] == 1
        assert report["summary"]["durable_save_allowed_count"] == 0
        assert report["summary"]["durable_rollback_policy_ready_count"] == 0
        assert report["summary"]["durable_executor_readiness_request_count"] == 1
        assert report["summary"]["durable_executor_ready_count"] == 0
        assert report["summary"]["durable_executor_skeleton_request_count"] == 1
        assert report["summary"]["durable_executor_skeleton_enabled_count"] == 0
        assert report["summary"]["durable_executor_skeleton_executable_count"] == 0
        assert report["summary"]["durable_executor_skeleton_command_count"] == 0
        assert report["summary"]["durable_ownership_marker_request_count"] == 1
        assert report["summary"]["durable_ownership_marker_policy_ready_count"] == 1
        assert report["summary"]["durable_ownership_delete_without_marker_allowed_count"] == 0
        assert report["summary"]["durable_ownership_delete_preexisting_asset_allowed_count"] == 0
        assert report["summary"]["durable_dry_run_plan_request_count"] == 1
        assert report["summary"]["durable_dry_run_plan_created_count"] == 1
        assert report["summary"]["durable_dry_run_plan_valid_count"] == 1
        assert report["summary"]["durable_dry_run_executor_may_execute_count"] == 0
        assert report["summary"]["durable_dry_run_live_command_count"] == 0
        assert report["summary"]["durable_dry_run_forbidden_command_allowed_count"] == 0
        assert report["summary"]["durable_save_simulation_request_count"] == 1
        assert report["summary"]["durable_save_simulation_evaluated_count"] == 1
        assert report["summary"]["durable_save_simulation_conditions_satisfied_count"] == 0
        assert report["summary"]["durable_save_simulation_save_true_allowed_count"] == 0
        assert report["summary"]["durable_save_simulation_save_asset_allowed_count"] == 0
        assert report["summary"]["durable_save_simulation_compile_save_command_allowed_count"] == 0
        assert report["summary"]["durable_save_simulation_live_command_count"] == 0
        assert report["summary"]["durable_canary_prep_request_count"] == 1
        assert report["summary"]["durable_canary_prep_ready_count"] == 1
        assert report["summary"]["durable_canary_live_execution_allowed_count"] == 0
        assert report["summary"]["durable_canary_general_blueprints_package_allowed_count"] == 0
        assert report["summary"]["durable_canary_save_true_allowed_count"] == 0
        assert report["summary"]["durable_canary_save_asset_allowed_count"] == 0
        assert report["summary"]["durable_canary_delete_asset_allowed_count"] == 0
        assert report["summary"]["durable_canary_approval_request_count"] == 1
        assert report["summary"]["durable_canary_approval_record_present_count"] == 1
        assert report["summary"]["durable_canary_approval_gate_passed_count"] == 1
        assert report["summary"]["durable_canary_approval_scoped_to_canary_package_count"] == 1
        assert report["summary"]["durable_canary_executor_may_open_count"] == 0
        assert report["summary"]["durable_canary_approval_live_execution_allowed_count"] == 0
        assert report["summary"]["durable_canary_approval_general_blueprints_package_allowed_count"] == 0
        assert report["summary"]["durable_canary_approval_save_true_allowed_count"] == 0
        assert report["summary"]["durable_canary_approval_save_asset_allowed_count"] == 0
        assert report["summary"]["durable_canary_approval_delete_asset_allowed_count"] == 0
        assert report["summary"]["durable_canary_approval_live_command_count"] == 0
        assert report["summary"]["durable_canary_live_preflight_request_count"] == 1
        assert report["summary"]["durable_canary_live_preflight_read_only_allowed_count"] == 1
        assert report["summary"]["durable_canary_live_preflight_execution_allowed_count"] == 0
        assert report["summary"]["durable_canary_live_preflight_authoring_command_allowed_count"] == 0
        assert report["summary"]["durable_canary_live_preflight_save_or_delete_allowed_count"] == 0
        assert report["summary"]["durable_canary_live_preflight_cleanup_command_allowed_count"] == 0
        assert report["summary"]["durable_canary_live_preflight_authoring_command_count"] == 0
        assert report["summary"]["durable_canary_live_preflight_save_or_delete_command_count"] == 0
        assert report["summary"]["durable_canary_live_preflight_cleanup_command_count"] == 0
        assert report["summary"]["durable_canary_recovery_request_count"] == 1
        assert report["summary"]["durable_canary_recovery_matrix_ready_count"] == 1
        assert report["summary"]["durable_canary_recovery_scenario_count"] == 6
        assert report["summary"]["durable_canary_recovery_cleanup_command_allowed_count"] == 0
        assert report["summary"]["durable_canary_recovery_delete_command_allowed_count"] == 0
        assert report["summary"]["durable_canary_recovery_save_command_allowed_count"] == 0
        assert report["summary"]["durable_canary_recovery_authoring_command_allowed_count"] == 0
        assert report["summary"]["durable_canary_recovery_live_cleanup_command_count"] == 0
        assert report["summary"]["durable_canary_recovery_live_delete_command_count"] == 0
        assert report["summary"]["durable_canary_recovery_live_save_command_count"] == 0
        assert report["summary"]["durable_canary_recovery_live_authoring_command_count"] == 0
        assert report["summary"]["durable_enable_contract_request_count"] == 1
        assert report["summary"]["durable_enable_contract_satisfied_count"] == 0
        assert report["summary"]["durable_enable_executor_may_open_count"] == 0
        assert report["summary"]["durable_enable_authoring_allowed_count"] == 0
        assert report["summary"]["durable_enable_forbidden_command_allowed_count"] == 0
        assert report["summary"]["durable_enable_failed_required_gate_count"] == 2
        assert report["summary"]["durable_enable_target_package_allowlist_passed_count"] == 1
        assert report["summary"]["durable_enable_overwrite_rename_decision_passed_count"] == 0
        assert report["summary"]["durable_enable_rollback_readiness_passed_count"] == 0
        assert report["summary"]["durable_enable_ownership_marker_passed_count"] == 1
        for manifest in report["manifests"]:
            if manifest["executable"]:
                assert compile_steps(manifest)
                assert all(step["params"]["save"] is False for step in compile_steps(manifest))
                assert manifest["authoring_executor_contract"]["temporary_smoke"]["compile_save"] is False
                assert manifest["authoring_executor_contract"]["temporary_smoke"]["durable_asset_creation_allowed"] is False

        safe_actor = find_manifest(report, "safe_actor_shell")
        assert safe_actor["planner"]["status"] == planner.STATUS_SAFE
        assert safe_actor["executable"] is True
        assert safe_actor["blueprint_kind"] == "actor_blueprint"
        assert safe_actor["parent_class"] == "Actor"
        assert safe_actor["parent_class_contract"]["schema"] == "section_31_parent_class_allowlist_contract_v1"
        assert safe_actor["parent_class_contract"]["executable_allowed"] is True
        assert safe_actor["parent_class_contract"]["allowlist"][0]["parent_class"] == "Actor"
        assert safe_actor["durable_authoring_contract"]["schema"] == "section_39_durable_authoring_contract_v1"
        assert safe_actor["durable_authoring_contract"]["requested"] is False
        assert safe_actor["durable_authoring_contract"]["durable_authoring_eligible"] is False
        assert safe_actor["durable_preflight_contract"]["schema"] == "section_39_durable_preflight_contract_v1"
        assert safe_actor["durable_preflight_contract"]["requested"] is False
        assert safe_actor["durable_preflight_contract"]["target_asset_path"] == ""
        assert safe_actor["durable_preflight_contract"]["preflight_pass"] is False
        assert safe_actor["durable_preflight_contract"]["overwrite_rename_decision_contract"]["decision"] == "not_required"
        assert safe_actor["durable_save_gate_contract"]["schema"] == "section_37_durable_save_gate_contract_v1"
        assert safe_actor["durable_save_gate_contract"]["requested"] is False
        assert safe_actor["durable_save_gate_contract"]["save_allowed"] is False
        assert safe_actor["durable_rollback_policy_contract"]["schema"] == "section_37_durable_rollback_policy_contract_v1"
        assert safe_actor["durable_rollback_policy_contract"]["requested"] is False
        assert safe_actor["durable_ownership_marker_contract"]["schema"] == "section_52_durable_ownership_marker_contract_v1"
        assert safe_actor["durable_ownership_marker_contract"]["requested"] is False
        assert safe_actor["durable_ownership_marker_contract"]["ownership_marker_policy_ready"] is False
        assert safe_actor["durable_enable_contract"]["schema"] == "section_51_durable_authoring_enable_contract_v1"
        assert safe_actor["durable_enable_contract"]["requested"] is False
        assert safe_actor["durable_enable_contract"]["enable_contract_satisfied"] is False
        assert safe_actor["durable_enable_contract"]["durable_executor_may_open"] is False
        assert safe_actor["durable_enable_contract"]["failed_required_gate_ids"] == []
        assert safe_actor["durable_dry_run_plan_contract"]["schema"] == "section_53_durable_executor_dry_run_plan_v1"
        assert safe_actor["durable_dry_run_plan_contract"]["requested"] is False
        assert safe_actor["durable_dry_run_plan_contract"]["dry_run_plan_created"] is False
        assert safe_actor["durable_dry_run_plan_contract"]["durable_executor_may_execute"] is False
        assert safe_actor["durable_save_validation_simulation_contract"]["schema"] == "section_54_durable_save_validation_simulator_v1"
        assert safe_actor["durable_save_validation_simulation_contract"]["requested"] is False
        assert safe_actor["durable_save_validation_simulation_contract"]["save_true_allowed"] is False
        assert safe_actor["durable_canary_prep_contract"]["schema"] == "section_55_durable_canary_prep_contract_v1"
        assert safe_actor["durable_canary_prep_contract"]["requested"] is False
        assert safe_actor["durable_canary_prep_contract"]["canary_prep_ready"] is False
        assert safe_actor["durable_canary_prep_contract"]["canary_live_execution_allowed"] is False
        assert safe_actor["durable_canary_approval_gate_contract"]["schema"] == "section_56_durable_canary_approval_gate_v1"
        assert safe_actor["durable_canary_approval_gate_contract"]["requested"] is False
        assert safe_actor["durable_canary_approval_gate_contract"]["approval_record_present"] is False
        assert safe_actor["durable_canary_approval_gate_contract"]["canary_approval_gate_passed"] is False
        assert safe_actor["durable_canary_approval_gate_contract"]["canary_live_execution_allowed"] is False
        assert safe_actor["durable_canary_live_preflight_contract"]["schema"] == "section_57_durable_canary_live_preflight_contract_v1"
        assert safe_actor["durable_canary_live_preflight_contract"]["requested"] is False
        assert safe_actor["durable_canary_live_preflight_contract"]["read_only_live_preflight_allowed"] is False
        assert safe_actor["durable_canary_live_preflight_contract"]["canary_execution_allowed_after_preflight"] is False
        assert safe_actor["durable_canary_recovery_matrix_contract"]["schema"] == "section_58_durable_canary_recovery_matrix_v1"
        assert safe_actor["durable_canary_recovery_matrix_contract"]["requested"] is False
        assert safe_actor["durable_canary_recovery_matrix_contract"]["recovery_matrix_ready"] is False
        assert safe_actor["durable_canary_recovery_matrix_contract"]["cleanup_command_allowed"] is False
        assert safe_actor["durable_executor_readiness_contract"]["schema"] == "section_38_durable_executor_readiness_contract_v1"
        assert safe_actor["durable_executor_readiness_contract"]["requested"] is False
        assert safe_actor["durable_executor_readiness_contract"]["durable_executor_ready"] is False
        assert safe_actor["durable_executor_skeleton_contract"]["schema"] == "section_39_durable_executor_skeleton_contract_v1"
        assert safe_actor["durable_executor_skeleton_contract"]["requested"] is False
        assert safe_actor["durable_executor_skeleton_contract"]["skeleton_defined"] is False
        assert safe_actor["durable_executor_skeleton_contract"]["executor_mode"] == "not_requested"
        assert safe_actor["durable_executor_skeleton_contract"]["executor_enabled"] is False
        assert safe_actor["durable_executor_skeleton_contract"]["can_execute"] is False
        assert safe_actor["durable_executor_skeleton_contract"]["command_plan"] == []
        assert safe_actor["authoring_executor_contract"]["schema"] == "section_39_authoring_executor_contract_v1"
        assert safe_actor["temp_package_path"] == custom_temp_path
        assert safe_actor["component_list"][0]["component_type"] == "StaticMeshComponent"
        assert safe_actor["component_default_contracts"][0]["component_name"] == "PlannerSmokeMesh"
        assert safe_actor["component_default_contracts"][0]["expected_transform"]["location"] == [0, 0, 0]
        assert safe_actor["variables_defaults"][0]["variable_name"] == "Health"
        assert safe_actor["variables_defaults"][0]["default_value"] == 100
        assert {"receive_begin_play", "branch", "branch_condition_default", "begin_play_to_branch"} <= command_ids(
            safe_actor["event_graph_steps"]
        )
        assert any(step["id"] == "compile_validate" for step in safe_actor["validation_plan"])
        assert any(step["id"] == "component_primary_defaults_verified" for step in safe_actor["validation_plan"])
        assert {
            "receive_begin_play_node_exists",
            "branch_node_exists",
            "branch_condition_default_default_verified",
            "begin_play_to_branch_link_verified",
            "receive_begin_play_layout_verified",
            "branch_layout_verified",
        } <= command_ids(safe_actor["structural_validation_plan"])
        assert safe_actor["cleanup_rollback_boundary"]["allowed_package_root"] == custom_temp_path
        assert safe_actor["validation_diagnostics"]["report_failure_diagnostics"] is True
        assert safe_actor["failure_diagnostics_contract"]["diagnostic_schema"] == "section_21_failure_diagnostics_v1"
        assert safe_actor["failure_diagnostics_contract"]["report_on_manifest_step_failure"] is True
        assert "step_id" in safe_actor["failure_diagnostics_contract"]["required_fields"]
        assert "stage_tail" in safe_actor["failure_diagnostics_contract"]["required_fields"]

        function_defaults = find_manifest(report, "safe_function_call_defaults")
        assert function_defaults["planner"]["status"] == planner.STATUS_SAFE
        assert function_defaults["executable"] is True
        assert function_defaults["component_default_steps"][0]["command"] == "set_static_mesh_properties"
        assert function_defaults["component_default_steps"][0]["static_mesh"] == "/Engine/BasicShapes/Cube.Cube"
        assert function_defaults["component_default_contracts"][0]["expected_static_mesh"] == "/Engine/BasicShapes/Cube.Cube"
        assert function_defaults["variables_defaults"][0]["variable_name"] == "Speed"
        assert function_defaults["variables_defaults"][0]["variable_type"] == "float"
        assert function_defaults["variables_defaults"][0]["default_value"] == 450.0
        assert {"print_string_call", "branch_true_to_print_string"} <= command_ids(function_defaults["event_graph_steps"])
        assert len(function_defaults["function_call_contracts"]) == 1
        assert len(function_defaults["graph_layout_contracts"]) == 3
        assert len(function_defaults["graph_layout_spacing_contracts"]) == 3
        print_call_contract = function_defaults["function_call_contracts"][0]
        assert print_call_contract["schema"] == "section_23_function_call_contract_v1"
        assert print_call_contract["function_class"] == "/Script/Engine.KismetSystemLibrary"
        assert print_call_contract["function_name"] == "PrintString"
        assert print_call_contract["input_defaults"][0]["pin_name"] == "InString"
        assert print_call_contract["input_defaults"][0]["expected_value"] == "Planner Smoke"
        assert print_call_contract["required_incoming_exec_links"][0]["source_step"] == "branch_true_to_print_string"
        assert {"print_string_call_node_exists", "branch_true_to_print_string_link_verified"} <= command_ids(
            function_defaults["structural_validation_plan"]
        )
        assert "print_string_call_contract_verified" in command_ids(function_defaults["structural_validation_plan"])
        assert "print_string_call_layout_verified" in command_ids(function_defaults["structural_validation_plan"])
        assert "branch_to_print_string_call_spacing_verified" in command_ids(function_defaults["structural_validation_plan"])
        assert "print_string_call_instring_default_verified" in command_ids(function_defaults["structural_validation_plan"])
        print_call = next(step for step in function_defaults["event_graph_steps"] if step["id"] == "print_string_call")
        assert print_call["params"]["function_class"] == "/Script/Engine.KismetSystemLibrary"
        assert print_call["params"]["function_name"] == "PrintString"
        assert function_defaults["validation_diagnostics"]["required_compile_error_count"] == 0

        component_hierarchy = find_manifest(report, "safe_component_hierarchy")
        assert component_hierarchy["planner"]["status"] == planner.STATUS_SAFE
        assert component_hierarchy["executable"] is True
        assert len(component_hierarchy["component_list"]) == 2
        hierarchy_root = component_hierarchy["component_list"][0]
        hierarchy_child = component_hierarchy["component_list"][1]
        assert hierarchy_root["component_type"] == "SceneComponent"
        assert hierarchy_root["component_name"] == "PlannerSmokeRoot"
        assert hierarchy_child["component_type"] == "StaticMeshComponent"
        assert hierarchy_child["component_name"] == "PlannerSmokeMesh"
        assert hierarchy_child["parent_component_name"] == "PlannerSmokeRoot"
        assert hierarchy_child["transform"]["location"] == [100, 0, 0]
        assert len(component_hierarchy["component_default_contracts"]) == 2
        assert len(component_hierarchy["component_hierarchy_contracts"]) == 1
        hierarchy_contract = component_hierarchy["component_hierarchy_contracts"][0]
        assert hierarchy_contract["schema"] == "section_28_component_hierarchy_contract_v1"
        assert hierarchy_contract["expected_parent_component_name"] == "PlannerSmokeRoot"
        assert hierarchy_contract["parent_declared_in_manifest"] is True
        assert "component_child_mesh_hierarchy_verified" in command_ids(component_hierarchy["validation_plan"])
        assert component_hierarchy["authoring_step_count"] == 11

        component_property = find_manifest(report, "safe_component_property_defaults")
        assert component_property["planner"]["status"] == planner.STATUS_SAFE
        assert component_property["executable"] is True
        assert component_property["component_default_steps"][0]["command"] == "set_component_property"
        assert component_property["component_default_steps"][0]["property_name"] == "bVisible"
        assert component_property["component_default_steps"][0]["property_value"] is False
        assert len(component_property["component_property_contracts"]) == 1
        property_contract = component_property["component_property_contracts"][0]
        assert property_contract["schema"] == "section_29_component_property_contract_v1"
        assert property_contract["allowlist_id"] == "static_mesh_component_bvisible"
        assert property_contract["expected_value"] is False
        assert "component_visibility_default_property_verified" in command_ids(component_property["validation_plan"])
        assert component_property["authoring_step_count"] == 10

        unsupported_property = find_manifest(report, "review_component_property_unsupported")
        assert unsupported_property["planner"]["status"] == planner.STATUS_SAFE
        assert unsupported_property["executable"] is False
        assert_no_authoring_steps(unsupported_property)
        assert unsupported_property["component_property_allowlist"][0]["property_name"] == "bVisible"
        assert any(
            reason["key"] == "contract_unsupported_component_property"
            for reason in unsupported_property["blocked_review_reasons"]
        )
        assert "add the requested component property to the Section 30 allowlist" in unsupported_property["required_reinforcement"]

        unsupported_parent = find_manifest(report, "review_parent_class_unsupported")
        assert unsupported_parent["planner"]["status"] == planner.STATUS_SAFE
        assert unsupported_parent["executable"] is False
        assert unsupported_parent["blueprint_kind"] == "character_blueprint"
        assert unsupported_parent["parent_class"] == "Character"
        assert unsupported_parent["parent_class_contract"]["requested_parent_class"] == "Character"
        assert unsupported_parent["parent_class_contract"]["executable_allowed"] is False
        assert unsupported_parent["parent_class_contract"]["allowlist"][0]["parent_class"] == "Actor"
        assert_no_authoring_steps(unsupported_parent)
        assert any(reason["key"] == "contract_unsupported_parent_class" for reason in unsupported_parent["blocked_review_reasons"])
        assert "add the requested parent class to the Section 31 allowlist" in unsupported_parent["required_reinforcement"]

        durable_save = find_manifest(report, "review_durable_authoring_save_requested")
        assert durable_save["planner"]["status"] == planner.STATUS_SAFE
        assert durable_save["executable"] is False
        assert durable_save["blueprint_kind"] == "actor_blueprint"
        assert durable_save["parent_class"] == "Actor"
        assert_no_authoring_steps(durable_save)
        durable_contract = durable_save["durable_authoring_contract"]
        assert durable_contract["requested"] is True
        assert durable_contract["requested_blueprint_name"] == "BP_PlannerDurable"
        assert durable_contract["requested_package_path"] == "/Game/Blueprints"
        assert durable_contract["package_path_allowed"] is True
        assert durable_contract["durable_executor_enabled"] is False
        assert durable_contract["durable_authoring_eligible"] is False
        assert durable_contract["save_allowed"] is False
        assert "/Game/Blueprints" in durable_contract["package_path_allowlist"]
        preflight_contract = durable_save["durable_preflight_contract"]
        assert preflight_contract == durable_contract["durable_preflight_contract"]
        assert preflight_contract == durable_save["authoring_executor_contract"]["durable_preflight"]
        assert preflight_contract["schema"] == "section_39_durable_preflight_contract_v1"
        assert preflight_contract["requested"] is True
        assert preflight_contract["dry_run_only"] is True
        assert preflight_contract["target_package_path"] == "/Game/Blueprints"
        assert preflight_contract["target_blueprint_name"] == "BP_PlannerDurable"
        assert preflight_contract["target_asset_path"] == "/Game/Blueprints/BP_PlannerDurable"
        assert preflight_contract["package_path_allowed"] is True
        assert preflight_contract["asset_exists_check_required"] is True
        assert preflight_contract["asset_exists_check_performed"] is False
        assert preflight_contract["asset_exists_check_command"] == "unreal.EditorAssetLibrary.does_asset_exist"
        assert preflight_contract["asset_exists_check_scope"] == "read_only_live_preflight"
        assert preflight_contract["asset_exists_live_result_schema"] == "section_35_durable_preflight_live_result_v1"
        assert preflight_contract["asset_exists"] is None
        assert preflight_contract["overwrite_decision_required"] is True
        assert preflight_contract["overwrite_decision_present"] is False
        assert preflight_contract["rename_decision_present"] is False
        decision_contract = preflight_contract["overwrite_rename_decision_contract"]
        assert decision_contract["schema"] == "section_36_overwrite_rename_decision_contract_v1"
        assert decision_contract["decision_required"] is True
        assert decision_contract["decision_present"] is False
        assert decision_contract["decision"] == "missing"
        assert decision_contract["target_asset_path"] == "/Game/Blueprints/BP_PlannerDurable"
        assert decision_contract["overwrite_requested"] is False
        assert decision_contract["rename_if_exists_requested"] is False
        assert decision_contract["decision_conflict"] is False
        assert decision_contract["overwrite_allowed"] is False
        assert decision_contract["rename_if_exists_allowed"] is False
        assert decision_contract["executor_may_resolve_conflict"] is False
        assert "choose exactly one durable conflict policy" in decision_contract["required_reinforcement"][0]
        save_gate_contract = durable_save["durable_save_gate_contract"]
        rollback_policy_contract = durable_save["durable_rollback_policy_contract"]
        readiness_contract = durable_save["durable_executor_readiness_contract"]
        skeleton_contract = durable_save["durable_executor_skeleton_contract"]
        assert save_gate_contract == preflight_contract["durable_save_gate_contract"]
        assert durable_save["durable_ownership_marker_contract"] == preflight_contract["durable_ownership_marker_contract"]
        assert durable_save["durable_ownership_marker_contract"] == durable_save["authoring_executor_contract"]["durable_ownership_marker"]
        assert durable_save["durable_enable_contract"] == preflight_contract["durable_enable_contract"]
        assert durable_save["durable_enable_contract"] == durable_save["authoring_executor_contract"]["durable_enable_contract"]
        assert durable_save["durable_dry_run_plan_contract"] == preflight_contract["durable_dry_run_plan_contract"]
        assert durable_save["durable_dry_run_plan_contract"] == durable_save["authoring_executor_contract"]["durable_dry_run_plan"]
        assert (
            durable_save["durable_save_validation_simulation_contract"]
            == preflight_contract["durable_save_validation_simulation_contract"]
        )
        assert (
            durable_save["durable_save_validation_simulation_contract"]
            == durable_save["authoring_executor_contract"]["durable_save_validation_simulation"]
        )
        assert durable_save["durable_canary_prep_contract"] == preflight_contract["durable_canary_prep_contract"]
        assert durable_save["durable_canary_prep_contract"] == durable_save["authoring_executor_contract"]["durable_canary_prep"]
        assert durable_save["durable_canary_approval_gate_contract"] == preflight_contract[
            "durable_canary_approval_gate_contract"
        ]
        assert (
            durable_save["durable_canary_approval_gate_contract"]
            == durable_save["authoring_executor_contract"]["durable_canary_approval_gate"]
        )
        assert durable_save["durable_canary_live_preflight_contract"] == preflight_contract[
            "durable_canary_live_preflight_contract"
        ]
        assert (
            durable_save["durable_canary_live_preflight_contract"]
            == durable_save["authoring_executor_contract"]["durable_canary_live_preflight"]
        )
        assert durable_save["durable_canary_recovery_matrix_contract"] == preflight_contract[
            "durable_canary_recovery_matrix_contract"
        ]
        assert (
            durable_save["durable_canary_recovery_matrix_contract"]
            == durable_save["authoring_executor_contract"]["durable_canary_recovery_matrix"]
        )
        assert rollback_policy_contract == preflight_contract["durable_rollback_policy_contract"]
        assert readiness_contract == preflight_contract["durable_executor_readiness_contract"]
        assert skeleton_contract == preflight_contract["durable_executor_skeleton_contract"]
        assert save_gate_contract == durable_save["authoring_executor_contract"]["durable_save_gate"]
        assert rollback_policy_contract == durable_save["authoring_executor_contract"]["durable_rollback_policy"]
        assert readiness_contract == durable_save["authoring_executor_contract"]["durable_executor_readiness"]
        assert skeleton_contract == durable_save["authoring_executor_contract"]["durable_executor_skeleton"]
        assert save_gate_contract["schema"] == "section_37_durable_save_gate_contract_v1"
        assert save_gate_contract["requested"] is True
        assert save_gate_contract["save_requested"] is True
        assert save_gate_contract["save_allowed"] is False
        assert save_gate_contract["compile_save_allowed"] is False
        assert save_gate_contract["temporary_smoke_may_save"] is False
        assert save_gate_contract["preflight_pass"] is False
        assert save_gate_contract["prerequisites"]["target_package_path_allowed"] is True
        assert save_gate_contract["prerequisites"]["asset_exists_result_available_in_manifest"] is False
        assert save_gate_contract["prerequisites"]["overwrite_or_rename_decision_present"] is False
        assert "durable_executor_disabled" in save_gate_contract["blocked_by"]
        assert "asset_exists_result_missing" in save_gate_contract["blocked_by"]
        assert "overwrite_rename_decision_missing" in save_gate_contract["blocked_by"]
        assert "rollback_policy_not_ready" in save_gate_contract["blocked_by"]
        ownership_contract = durable_save["durable_ownership_marker_contract"]
        assert ownership_contract["schema"] == "section_52_durable_ownership_marker_contract_v1"
        assert ownership_contract["requested"] is True
        assert ownership_contract["ownership_marker_policy_ready"] is True
        assert ownership_contract["delete_without_marker_allowed"] is False
        assert ownership_contract["delete_preexisting_asset_allowed"] is False
        assert ownership_contract["overwrite_preexisting_asset_allowed"] is False
        assert ownership_contract["rename_preexisting_asset_allowed"] is False
        assert "preflight_asset_existed_before_authoring" in ownership_contract["required_marker_fields"]
        enable_contract = durable_save["durable_enable_contract"]
        assert enable_contract["schema"] == "section_51_durable_authoring_enable_contract_v1"
        assert enable_contract["requested"] is True
        assert enable_contract["enable_contract_satisfied"] is False
        assert enable_contract["durable_executor_may_open"] is False
        assert enable_contract["durable_authoring_allowed"] is False
        assert enable_contract["save_true_allowed"] is False
        assert enable_contract["save_asset_allowed"] is False
        assert enable_contract["delete_asset_allowed"] is False
        assert enable_contract["rename_asset_allowed"] is False
        assert "save_asset" in enable_contract["forbidden_commands"]
        assert "delete_asset" in enable_contract["forbidden_commands"]
        assert "rename_asset" in enable_contract["forbidden_commands"]
        assert enable_contract["failed_required_gate_ids"] == [
            "overwrite_rename_decision",
            "rollback_readiness",
        ]
        enable_gates = {gate["id"]: gate for gate in enable_contract["gates"]}
        assert enable_gates["target_package_allowlist"]["passed"] is True
        assert enable_gates["overwrite_rename_decision"]["passed"] is False
        assert enable_gates["rollback_readiness"]["passed"] is False
        assert enable_gates["executor_created_ownership_marker"]["passed"] is True
        dry_run_plan = durable_save["durable_dry_run_plan_contract"]
        assert dry_run_plan["schema"] == "section_53_durable_executor_dry_run_plan_v1"
        assert dry_run_plan["requested"] is True
        assert dry_run_plan["dry_run_plan_created"] is True
        assert dry_run_plan["dry_run_plan_valid"] is True
        assert dry_run_plan["execution_command_plan"] == []
        assert dry_run_plan["live_command_count"] == 0
        assert dry_run_plan["durable_executor_may_execute"] is False
        assert dry_run_plan["save_allowed"] is False
        assert dry_run_plan["delete_allowed"] is False
        assert dry_run_plan["rename_allowed"] is False
        assert "save_asset" in dry_run_plan["forbidden_commands"]
        save_simulation = durable_save["durable_save_validation_simulation_contract"]
        assert save_simulation["schema"] == "section_54_durable_save_validation_simulator_v1"
        assert save_simulation["requested"] is True
        assert save_simulation["simulation_evaluated"] is True
        assert save_simulation["future_save_conditions_satisfied"] is False
        assert save_simulation["save_true_allowed"] is False
        assert save_simulation["save_asset_allowed"] is False
        assert save_simulation["compile_save_command_allowed"] is False
        assert save_simulation["live_command_count"] == 0
        assert "section_54_simulator_does_not_enable_save" in save_simulation["blocked_by"]
        canary_prep = durable_save["durable_canary_prep_contract"]
        assert canary_prep["schema"] == "section_55_durable_canary_prep_contract_v1"
        assert canary_prep["requested"] is True
        assert canary_prep["source_target_asset_path"] == "/Game/Blueprints/BP_PlannerDurable"
        assert canary_prep["canary_package_path"] == "/Game/_MCP_Temp/DurableCanary"
        assert canary_prep["canary_asset_path"] == "/Game/_MCP_Temp/DurableCanary/BP_PlannerDurable_Canary"
        assert canary_prep["canary_package_allowlisted"] is True
        assert canary_prep["canary_prep_ready"] is True
        assert canary_prep["canary_live_execution_allowed"] is False
        assert canary_prep["general_blueprints_package_allowed"] is False
        assert canary_prep["save_true_allowed"] is False
        assert canary_prep["save_asset_allowed"] is False
        assert canary_prep["delete_asset_allowed"] is False
        assert canary_prep["cleanup_requires_ownership_marker"] is True
        assert "section_55_prep_only_no_live_canary" in canary_prep["blocked_by"]
        canary_approval = durable_save["durable_canary_approval_gate_contract"]
        assert canary_approval["schema"] == "section_56_durable_canary_approval_gate_v1"
        assert canary_approval["requested"] is True
        assert canary_approval["canary_prep_ready"] is True
        assert canary_approval["approval_record_present"] is True
        assert canary_approval["approval_scoped_to_canary_package"] is True
        assert canary_approval["canary_approval_gate_passed"] is True
        assert canary_approval["canary_executor_may_open"] is False
        assert canary_approval["canary_live_execution_allowed"] is False
        assert canary_approval["general_blueprints_package_allowed"] is False
        assert canary_approval["save_true_allowed"] is False
        assert canary_approval["save_asset_allowed"] is False
        assert canary_approval["delete_asset_allowed"] is False
        assert canary_approval["live_command_count"] == 0
        assert "section_56_approval_gate_does_not_enable_live_canary" in canary_approval["blocked_by"]
        canary_live_preflight = durable_save["durable_canary_live_preflight_contract"]
        assert canary_live_preflight["schema"] == "section_57_durable_canary_live_preflight_contract_v1"
        assert canary_live_preflight["requested"] is True
        assert canary_live_preflight["canary_asset_path"] == "/Game/_MCP_Temp/DurableCanary/BP_PlannerDurable_Canary"
        assert canary_live_preflight["read_only_live_preflight_allowed"] is True
        assert canary_live_preflight["read_only_live_command"] == "unreal.EditorAssetLibrary.does_asset_exist"
        assert canary_live_preflight["canary_execution_allowed_after_preflight"] is False
        assert canary_live_preflight["authoring_command_allowed"] is False
        assert canary_live_preflight["save_or_delete_allowed"] is False
        assert canary_live_preflight["cleanup_command_allowed"] is False
        assert canary_live_preflight["live_authoring_command_count"] == 0
        assert canary_live_preflight["live_save_or_delete_command_count"] == 0
        assert canary_live_preflight["live_cleanup_command_count"] == 0
        assert "section_57_read_only_canary_preflight_only" in canary_live_preflight["blocked_by"]
        canary_recovery = durable_save["durable_canary_recovery_matrix_contract"]
        assert canary_recovery["schema"] == "section_58_durable_canary_recovery_matrix_v1"
        assert canary_recovery["requested"] is True
        assert canary_recovery["recovery_matrix_ready"] is True
        assert canary_recovery["scenario_count"] == 6
        assert canary_recovery["cleanup_command_allowed"] is False
        assert canary_recovery["delete_command_allowed"] is False
        assert canary_recovery["save_command_allowed"] is False
        assert canary_recovery["authoring_command_allowed"] is False
        assert canary_recovery["live_cleanup_command_count"] == 0
        assert canary_recovery["live_delete_command_count"] == 0
        assert canary_recovery["live_save_command_count"] == 0
        assert canary_recovery["live_authoring_command_count"] == 0
        assert "section_58_recovery_matrix_report_only" in canary_recovery["blocked_by"]
        assert rollback_policy_contract["schema"] == "section_37_durable_rollback_policy_contract_v1"
        assert rollback_policy_contract["requested"] is True
        assert rollback_policy_contract["policy_mode"] == "draft_only"
        assert rollback_policy_contract["rollback_policy_ready"] is False
        assert rollback_policy_contract["rollback_allowed"] is False
        assert rollback_policy_contract["delete_created_asset_on_failure"] is False
        assert rollback_policy_contract["delete_existing_asset_allowed"] is False
        assert rollback_policy_contract["overwrite_existing_asset_allowed"] is False
        assert rollback_policy_contract["requires_executor_created_asset_marker"] is True
        assert rollback_policy_contract["protects_preexisting_assets"] is True
        assert readiness_contract["schema"] == "section_38_durable_executor_readiness_contract_v1"
        assert readiness_contract["requested"] is True
        assert readiness_contract["enablement_mode"] == "disabled"
        assert readiness_contract["durable_executor_ready"] is False
        assert readiness_contract["readiness_level"] == "not_ready"
        readiness_checks = {check["id"]: check for check in readiness_contract["checks"]}
        assert readiness_checks["target_package_path_allowlisted"]["passed"] is True
        assert readiness_checks["live_asset_exists_result_promoted"]["passed"] is False
        assert readiness_checks["conflict_resolution_decision_present"]["passed"] is False
        assert readiness_checks["conflict_resolution_decision_conflict_free"]["passed"] is True
        assert readiness_checks["save_gate_allows_save"]["passed"] is False
        assert readiness_checks["rollback_policy_ready"]["passed"] is False
        assert readiness_checks["durable_compile_save_validation_enabled"]["passed"] is False
        assert readiness_checks["executor_created_asset_marker_policy_ready"]["passed"] is False
        assert readiness_checks["explicit_durable_executor_enable_flag"]["passed"] is False
        assert "live_asset_exists_result_promoted" in readiness_contract["failing_checks"]
        assert "explicit_durable_executor_enable_flag" in readiness_contract["failing_checks"]
        assert skeleton_contract["schema"] == "section_39_durable_executor_skeleton_contract_v1"
        assert skeleton_contract["requested"] is True
        assert skeleton_contract["skeleton_defined"] is True
        assert skeleton_contract["executor_mode"] == "disabled_skeleton"
        assert skeleton_contract["executor_enabled"] is False
        assert skeleton_contract["can_execute"] is False
        assert skeleton_contract["command_plan"] == []
        assert skeleton_contract["authoring_commands_allowed"] is False
        assert skeleton_contract["save_commands_allowed"] is False
        assert skeleton_contract["delete_commands_allowed"] is False
        assert skeleton_contract["rename_commands_allowed"] is False
        assert skeleton_contract["allowed_live_command_count"] == 0
        assert "section_39_durable_preflight_contract_v1" in skeleton_contract["input_contracts"]
        assert "section_52_durable_ownership_marker_contract_v1" in skeleton_contract["input_contracts"]
        assert "section_51_durable_authoring_enable_contract_v1" in skeleton_contract["input_contracts"]
        assert "section_55_durable_canary_prep_contract_v1" in skeleton_contract["input_contracts"]
        assert "section_56_durable_canary_approval_gate_v1" in skeleton_contract["input_contracts"]
        assert "section_57_durable_canary_live_preflight_contract_v1" in skeleton_contract["input_contracts"]
        assert "section_58_durable_canary_recovery_matrix_v1" in skeleton_contract["input_contracts"]
        assert "section_37_durable_save_gate_contract_v1" in skeleton_contract["input_contracts"]
        assert "section_38_durable_executor_readiness_contract_v1" in skeleton_contract["input_contracts"]
        assert "durable_executor_skeleton_disabled" in skeleton_contract["disabled_by"]
        assert "overwrite_rename_decision" in skeleton_contract["disabled_by"]
        assert "rollback_readiness" in skeleton_contract["disabled_by"]
        assert "executor_created_ownership_marker" not in skeleton_contract["disabled_by"]
        assert "explicit_durable_executor_enable_flag" in skeleton_contract["disabled_by"]
        assert "create_blueprint" in skeleton_contract["forbidden_commands"]
        assert "save_asset" in skeleton_contract["forbidden_commands"]
        assert "delete_asset" in skeleton_contract["forbidden_commands"]
        assert preflight_contract["save_gate_required"] is True
        assert preflight_contract["save_gate_passed"] is False
        assert preflight_contract["preflight_pass"] is False
        assert preflight_contract["live_read_only_check_allowed"] is True
        assert durable_save["authoring_executor_contract"]["temporary_smoke"]["durable_asset_creation_allowed"] is False
        assert any(reason["key"] == "contract_durable_executor_not_enabled" for reason in durable_save["blocked_review_reasons"])
        assert "keep the Section 39 durable executor skeleton disabled until readiness passes" in durable_save["required_reinforcement"]

        overwrite_save = contract.build_job_manifest(
            "durable_overwrite",
            "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints and overwrite if it exists with a Static Mesh Component.",
            temp_package_path=custom_temp_path,
        )
        assert overwrite_save["planner"]["status"] == planner.STATUS_SAFE
        assert overwrite_save["executable"] is False
        assert_no_authoring_steps(overwrite_save)
        overwrite_decision = overwrite_save["durable_preflight_contract"]["overwrite_rename_decision_contract"]
        assert overwrite_decision["decision_required"] is True
        assert overwrite_decision["decision_present"] is True
        assert overwrite_decision["decision"] == "overwrite_existing"
        assert overwrite_decision["overwrite_requested"] is True
        assert overwrite_decision["rename_if_exists_requested"] is False
        assert overwrite_decision["decision_conflict"] is False
        assert overwrite_decision["overwrite_allowed"] is False
        assert overwrite_save["durable_preflight_contract"]["preflight_pass"] is False
        assert overwrite_save["durable_save_gate_contract"]["prerequisites"]["overwrite_or_rename_decision_present"] is True
        assert overwrite_save["durable_save_gate_contract"]["save_allowed"] is False
        assert "overwrite_rename_decision_overwrite_existing" not in overwrite_save["durable_save_gate_contract"]["blocked_by"]
        assert "rollback_policy_not_ready" in overwrite_save["durable_save_gate_contract"]["blocked_by"]
        overwrite_readiness = overwrite_save["durable_executor_readiness_contract"]
        assert overwrite_readiness["durable_executor_ready"] is False
        overwrite_readiness_checks = {check["id"]: check for check in overwrite_readiness["checks"]}
        assert overwrite_readiness_checks["conflict_resolution_decision_present"]["passed"] is True
        assert overwrite_readiness_checks["save_gate_allows_save"]["passed"] is False

        rename_save = contract.build_job_manifest(
            "durable_rename",
            "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints and create unique name if exists with a Static Mesh Component.",
            temp_package_path=custom_temp_path,
        )
        assert rename_save["planner"]["status"] == planner.STATUS_SAFE
        assert rename_save["executable"] is False
        assert_no_authoring_steps(rename_save)
        rename_decision = rename_save["durable_preflight_contract"]["overwrite_rename_decision_contract"]
        assert rename_decision["decision_present"] is True
        assert rename_decision["decision"] == "rename_if_exists"
        assert rename_decision["overwrite_requested"] is False
        assert rename_decision["rename_if_exists_requested"] is True
        assert rename_decision["rename_if_exists_allowed"] is False
        assert rename_save["durable_save_gate_contract"]["prerequisites"]["overwrite_or_rename_decision_present"] is True
        assert rename_save["durable_save_gate_contract"]["save_allowed"] is False

        conflict_save = contract.build_job_manifest(
            "durable_conflict",
            "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints, overwrite it if it exists, and create unique name if exists.",
            temp_package_path=custom_temp_path,
        )
        assert conflict_save["planner"]["status"] == planner.STATUS_SAFE
        assert conflict_save["executable"] is False
        assert_no_authoring_steps(conflict_save)
        conflict_decision = conflict_save["durable_preflight_contract"]["overwrite_rename_decision_contract"]
        assert conflict_decision["decision_present"] is False
        assert conflict_decision["decision"] == "conflicting_decisions"
        assert conflict_decision["overwrite_requested"] is True
        assert conflict_decision["rename_if_exists_requested"] is True
        assert conflict_decision["decision_conflict"] is True
        assert "remove the conflicting durable overwrite/rename policy" in conflict_decision["required_reinforcement"][0]
        assert conflict_save["durable_save_gate_contract"]["prerequisites"]["overwrite_or_rename_decision_conflict_free"] is False
        assert "overwrite_rename_decision_conflict" in conflict_save["durable_save_gate_contract"]["blocked_by"]

        function_graph = find_manifest(report, "safe_function_graph_authoring")
        assert function_graph["planner"]["status"] == planner.STATUS_SAFE
        assert function_graph["executable"] is True
        function_graph_step_ids = command_ids(function_graph["function_graph_steps"])
        assert {
            "resolve_function_graph",
            "function_input_value",
            "function_output_value",
            "function_return_node",
            "function_return_default",
        } <= function_graph_step_ids
        resolve_step = next(step for step in function_graph["function_graph_steps"] if step["id"] == "resolve_function_graph")
        assert resolve_step["params"]["graph_name"] == "ComputePlannerValue"
        assert resolve_step["params"]["create_if_missing"] is True
        return_default = next(step for step in function_graph["function_graph_steps"] if step["id"] == "function_return_default")
        assert return_default["graph_name"] == "ComputePlannerValue"
        assert {
            "resolve_function_graph_graph_resolved",
            "function_input_value_node_exists",
            "function_output_value_node_exists",
            "function_return_node_node_exists",
            "function_return_default_default_verified",
        } <= command_ids(function_graph["structural_validation_plan"])
        assert any(step["id"] == "list_function_nodes" for step in function_graph["validation_plan"])

        function_body = find_manifest(report, "safe_function_graph_body_math")
        assert function_body["planner"]["status"] == planner.STATUS_SAFE
        assert function_body["executable"] is True
        function_body_step_ids = command_ids(function_body["function_graph_steps"])
        assert {
            "resolve_function_graph",
            "function_output_value",
            "function_local_value",
            "local_value_get",
            "math_add_node",
            "math_add_rhs_default",
            "local_value_to_math_add",
            "function_return_node",
            "math_result_to_return",
        } <= function_body_step_ids
        assert function_body["variables_defaults"] == []
        body_graph = next(step for step in function_body["function_graph_steps"] if step["id"] == "resolve_function_graph")
        assert body_graph["params"]["graph_name"] == "ComputePlannerBody"
        local_value = next(step for step in function_body["function_graph_steps"] if step["id"] == "function_local_value")
        assert local_value["params"]["variable_type"] == "double"
        assert local_value["params"]["default_value"] == 5.0
        math_result = next(step for step in function_body["function_graph_steps"] if step["id"] == "math_result_to_return")
        assert math_result["graph_name"] == "ComputePlannerBody"
        function_body_structural_ids = command_ids(function_body["structural_validation_plan"])
        assert {
            "resolve_function_graph_graph_resolved",
            "function_output_value_node_exists",
            "local_value_get_node_exists",
            "math_add_node_node_exists",
            "math_add_rhs_default_default_verified",
            "local_value_to_math_add_link_verified",
            "function_return_node_node_exists",
            "math_result_to_return_link_verified",
            "local_value_get_layout_verified",
            "math_add_node_layout_verified",
            "function_return_node_layout_verified",
        } <= function_body_structural_ids
        assert "function_local_value_node_exists" not in function_body_structural_ids
        assert len(function_body["structural_validation_plan"]) == 14
        assert any(
            step["id"] == "list_function_nodes" and step["params"]["graph_name"] == "ComputePlannerBody"
            for step in function_body["validation_plan"]
        )

        local_set = find_manifest(report, "safe_function_graph_local_set")
        assert local_set["planner"]["status"] == planner.STATUS_SAFE
        assert local_set["executable"] is True
        assert local_set["function_graph_steps"][0]["params"]["graph_name"] == "ComputePlannerLocalSet"
        local_set_step_ids = command_ids(local_set["function_graph_steps"])
        assert {
            "function_input_value",
            "function_output_value",
            "function_local_accumulated_value",
            "pre_local_set_compile",
            "math_add_node",
            "math_add_rhs_default",
            "local_value_set",
            "input_value_to_math_add",
            "math_result_to_local_value_set",
            "function_entry_to_local_value_set",
            "local_value_set_to_return_exec",
            "local_value_set_output_to_return",
        } <= local_set_step_ids
        local_set_node = next(step for step in local_set["function_graph_steps"] if step["id"] == "local_value_set")
        assert local_set_node["params"]["variable_name"] == "AccumulatedValue"
        entry_to_set = next(step for step in local_set["function_graph_steps"] if step["id"] == "function_entry_to_local_value_set")
        assert entry_to_set["allow_pin_link_replacement"] is True
        local_set_structural_ids = command_ids(local_set["structural_validation_plan"])
        assert {
            "resolve_function_graph_graph_resolved",
            "function_input_value_node_exists",
            "function_output_value_node_exists",
            "math_add_node_node_exists",
            "math_add_rhs_default_default_verified",
            "local_value_set_node_exists",
            "input_value_to_math_add_link_verified",
            "math_result_to_local_value_set_link_verified",
            "function_entry_to_local_value_set_link_verified",
            "local_value_set_to_return_exec_link_verified",
            "local_value_set_output_to_return_link_verified",
            "math_add_node_layout_verified",
            "local_value_set_layout_verified",
        } <= local_set_structural_ids
        assert local_set["structural_assertion_count"] == 14

        compare_branch = find_manifest(report, "safe_function_graph_compare_branch")
        assert compare_branch["planner"]["status"] == planner.STATUS_SAFE
        assert compare_branch["executable"] is True
        assert compare_branch["function_graph_steps"][0]["params"]["graph_name"] == "ComputePlannerBranch"
        compare_branch_step_ids = command_ids(compare_branch["function_graph_steps"])
        assert {
            "function_input_value",
            "function_output_value",
            "function_local_branch_result",
            "pre_compare_branch_compile",
            "compare_greater_node",
            "compare_threshold_default",
            "branch_node",
            "branch_then_value_set",
            "branch_then_value_default",
            "branch_else_value_set",
            "branch_else_value_default",
            "branch_result_get",
            "input_value_to_compare",
            "compare_result_to_branch",
            "function_entry_to_branch",
            "branch_then_to_value_set",
            "branch_else_to_value_set",
            "branch_then_set_to_return_exec",
            "branch_else_set_to_return_exec",
            "branch_result_to_return",
        } <= compare_branch_step_ids
        compare_node = next(step for step in compare_branch["function_graph_steps"] if step["id"] == "compare_greater_node")
        assert compare_node["command"] == "add_blueprint_compare_node"
        assert compare_node["params"]["operation"] == "greater"
        assert compare_node["params"]["value_type"] == "double"
        entry_to_branch = next(step for step in compare_branch["function_graph_steps"] if step["id"] == "function_entry_to_branch")
        assert entry_to_branch["allow_pin_link_replacement"] is True
        branch_then = next(step for step in compare_branch["function_graph_steps"] if step["id"] == "branch_then_to_value_set")
        branch_else = next(step for step in compare_branch["function_graph_steps"] if step["id"] == "branch_else_to_value_set")
        assert branch_then["source_pin_preferred"] == ["then"]
        assert branch_else["source_pin_preferred"] == ["else"]
        compare_branch_structural_ids = command_ids(compare_branch["structural_validation_plan"])
        assert {
            "resolve_function_graph_graph_resolved",
            "function_input_value_node_exists",
            "function_output_value_node_exists",
            "compare_greater_node_node_exists",
            "compare_threshold_default_default_verified",
            "branch_node_node_exists",
            "branch_then_value_set_node_exists",
            "branch_then_value_default_default_verified",
            "branch_else_value_set_node_exists",
            "branch_else_value_default_default_verified",
            "branch_result_get_node_exists",
            "input_value_to_compare_link_verified",
            "compare_result_to_branch_link_verified",
            "function_entry_to_branch_link_verified",
            "branch_then_to_value_set_link_verified",
            "branch_else_to_value_set_link_verified",
            "branch_then_set_to_return_exec_link_verified",
            "branch_else_set_to_return_exec_link_verified",
            "branch_result_to_return_link_verified",
            "compare_greater_node_layout_verified",
            "branch_node_layout_verified",
            "branch_then_value_set_layout_verified",
            "branch_else_value_set_layout_verified",
            "branch_result_get_layout_verified",
        } <= compare_branch_structural_ids
        assert "function_local_branch_result_node_exists" not in compare_branch_structural_ids
        assert compare_branch["structural_assertion_count"] == 34

        typed_defaults = find_manifest(report, "safe_typed_variables_defaults")
        assert typed_defaults["planner"]["status"] == planner.STATUS_SAFE
        assert typed_defaults["executable"] is True
        assert typed_defaults["component_list"][0]["component_type"] == "SceneComponent"
        assert typed_defaults["component_list"][0]["component_name"] == "TypedDefaultsRoot"
        assert typed_defaults["component_list"][0]["transform"]["location"] == [10, 20, 30]
        assert typed_defaults["component_default_contracts"][0]["component_name"] == "TypedDefaultsRoot"
        assert typed_defaults["component_default_contracts"][0]["expected_transform"]["rotation"] == [0, 45, 0]
        typed_variable_defaults = {variable["variable_name"]: variable for variable in typed_defaults["variables_defaults"]}
        assert typed_variable_defaults["bPlannerEnabled"]["variable_type"] == "bool"
        assert typed_variable_defaults["bPlannerEnabled"]["default_value"] is True
        assert typed_variable_defaults["PlannerLabel"]["variable_type"] == "string"
        assert typed_variable_defaults["PlannerLabel"]["default_value"] == "Section22"
        assert typed_variable_defaults["PlannerOffset"]["variable_type"] == "vector"
        assert typed_variable_defaults["PlannerOffset"]["default_value"] == [10, 20, 30]
        typed_validation_ids = command_ids(typed_defaults["validation_plan"])
        assert {
            "variable_planner_enabled_default_verified",
            "variable_planner_label_default_verified",
            "variable_planner_offset_default_verified",
        } <= typed_validation_ids
        assert typed_defaults["structural_assertion_count"] == 0

        sequence_flow = find_manifest(report, "safe_event_sequence_flow")
        assert sequence_flow["planner"]["status"] == planner.STATUS_SAFE
        assert sequence_flow["executable"] is True
        sequence_step_ids = command_ids(sequence_flow["event_graph_steps"])
        assert {
            "receive_begin_play",
            "sequence_node",
            "begin_play_to_sequence",
            "sequence_first_print_string",
            "sequence_second_print_string",
            "sequence_then_0_to_first_print",
            "sequence_then_1_to_second_print",
        } <= sequence_step_ids
        sequence_node = next(step for step in sequence_flow["event_graph_steps"] if step["id"] == "sequence_node")
        assert sequence_node["command"] == "add_blueprint_sequence_node"
        assert sequence_node["params"]["output_count"] == 2
        assert len(sequence_flow["function_call_contracts"]) == 2
        assert len(sequence_flow["graph_layout_contracts"]) == 4
        assert len(sequence_flow["graph_layout_spacing_contracts"]) == 6
        sequence_structural_ids = command_ids(sequence_flow["structural_validation_plan"])
        assert {
            "sequence_node_node_exists",
            "sequence_node_output_count_verified",
            "sequence_first_print_string_instring_default_verified",
            "sequence_second_print_string_instring_default_verified",
            "sequence_then_0_to_first_print_link_verified",
            "sequence_then_1_to_second_print_link_verified",
            "sequence_first_print_string_contract_verified",
            "sequence_second_print_string_contract_verified",
            "sequence_node_layout_verified",
            "sequence_first_print_string_layout_verified",
            "sequence_second_print_string_layout_verified",
            "sequence_first_print_string_to_sequence_second_print_string_spacing_verified",
        } <= sequence_structural_ids
        assert sequence_flow["structural_assertion_count"] == 22

        generated_invocation = find_manifest(report, "safe_generated_function_invocation")
        assert generated_invocation["planner"]["status"] == planner.STATUS_SAFE
        assert generated_invocation["executable"] is True
        assert generated_invocation["function_graph_steps"][0]["params"]["graph_name"] == "ComputePlannerInvocation"
        assert any(
            variable["variable_name"] == "LastInvocationResult"
            and variable["variable_type"] == "double"
            and variable["default_value"] == 0.0
            for variable in generated_invocation["variables_defaults"]
        )
        generated_function_step_ids = command_ids(generated_invocation["function_graph_steps"])
        assert {
            "function_input_addend",
            "function_output_value",
            "function_local_value",
            "local_value_get",
            "math_add_node",
            "local_value_to_math_add",
            "input_addend_to_math_add",
            "function_return_node",
            "math_result_to_return",
        } <= generated_function_step_ids
        generated_invocation_step_ids = command_ids(generated_invocation["generated_function_invocation_steps"])
        assert {
            "pre_invocation_compile",
            "generated_function_call",
            "generated_function_result_output_exists",
            "event_graph_self_reference",
            "last_invocation_result_set",
            "generated_function_to_result_set_exec",
            "generated_result_to_last_invocation_result",
            "self_to_last_invocation_result_target",
            "branch_true_to_generated_function",
        } <= generated_invocation_step_ids
        generated_call = next(
            step for step in generated_invocation["generated_function_invocation_steps"] if step["id"] == "generated_function_call"
        )
        assert generated_call["params"]["function_class"] == "{temp_package_path}/{blueprint_name}.{blueprint_name}_C"
        assert generated_call["params"]["function_name"] == "ComputePlannerInvocation"
        assert generated_call["params"]["param_defaults"]["AddendValue"] == 2.0
        assert len(generated_invocation["function_call_contracts"]) == 1
        generated_call_contract = generated_invocation["function_call_contracts"][0]
        assert generated_call_contract["function_class"] == "{temp_package_path}/{blueprint_name}.{blueprint_name}_C"
        assert generated_call_contract["function_name"] == "ComputePlannerInvocation"
        assert generated_call_contract["input_defaults"][0]["pin_name"] == "AddendValue"
        assert generated_call_contract["required_output_pins"][0]["pin_names"] == ["ResultValue"]
        assert len(generated_invocation["graph_layout_contracts"]) == 8
        assert len(generated_invocation["graph_layout_spacing_contracts"]) == 13
        assert {link["source_step"] for link in generated_call_contract["required_outgoing_links"]} == {
            "generated_function_to_result_set_exec",
            "generated_result_to_last_invocation_result",
        }
        generated_structural_ids = command_ids(generated_invocation["structural_validation_plan"])
        assert {
            "generated_function_call_node_exists",
            "generated_function_call_addendvalue_default_verified",
            "generated_function_result_output_exists_postcondition",
            "generated_function_call_contract_verified",
            "event_graph_self_reference_node_exists",
            "last_invocation_result_set_node_exists",
            "generated_function_to_result_set_exec_link_verified",
            "generated_result_to_last_invocation_result_link_verified",
            "self_to_last_invocation_result_target_link_verified",
            "branch_true_to_generated_function_link_verified",
            "input_addend_to_math_add_link_verified",
            "generated_function_call_layout_verified",
            "event_graph_self_reference_layout_verified",
            "last_invocation_result_set_layout_verified",
            "generated_function_call_to_last_invocation_result_set_spacing_verified",
        } <= generated_structural_ids
        assert generated_invocation["structural_assertion_count"] == 44

        dispatcher = find_manifest(report, "safe_event_dispatcher")
        assert dispatcher["planner"]["status"] == planner.STATUS_SAFE
        assert dispatcher["executable"] is True
        dispatcher_step_ids = command_ids(dispatcher["dispatcher_lifecycle_steps"])
        assert {
            "dispatcher_declare",
            "dispatcher_call",
            "dispatcher_custom_event",
            "dispatcher_bind",
            "dispatcher_assign",
            "dispatcher_unbind",
            "dispatcher_clear",
            "custom_event_to_bind_delegate",
            "custom_event_to_unbind_delegate",
        } <= dispatcher_step_ids
        assert dispatcher["blocked_review_reasons"] == []
        assert any(step["id"] == "list_graphs" for step in dispatcher["validation_plan"])
        assert {
            "dispatcher_call_node_exists",
            "dispatcher_custom_event_node_exists",
            "dispatcher_call_layout_verified",
            "dispatcher_custom_event_layout_verified",
            "custom_event_delegate_output_exists_postcondition",
            "bind_delegate_input_exists_postcondition",
            "custom_event_to_bind_delegate_link_verified",
        } <= command_ids(dispatcher["structural_validation_plan"])

        review_umg = find_manifest(report, "review_umg_button")
        assert review_umg["planner"]["status"] == planner.STATUS_REVIEW
        assert review_umg["blueprint_kind"] == "widget_blueprint"
        assert review_umg["parent_class"] == "UserWidget"
        assert_no_authoring_steps(review_umg)
        assert review_umg["failure_diagnostics_contract"]["report_on_manifest_step_failure"] is False
        assert any(reason["key"] == "umg_widget_event" for reason in review_umg["blocked_review_reasons"])

        blocked_async = find_manifest(report, "blocked_async_proxy")
        assert blocked_async["planner"]["status"] == planner.STATUS_BLOCKED
        assert_no_authoring_steps(blocked_async)
        assert any(reason["key"] == "async_proxy_callback_exec" for reason in blocked_async["blocked_review_reasons"])
        assert "async proxy callback inventory" in blocked_async["required_reinforcement"]

        blocked_gas = find_manifest(report, "blocked_gas_replication")
        assert_no_authoring_steps(blocked_gas)
        assert any(reason["key"] == "gas_ability_task" for reason in blocked_gas["blocked_review_reasons"])
        assert any(reason["key"] == "replication_rpc" for reason in blocked_gas["blocked_review_reasons"])

        blocked_commonui = find_manifest(report, "blocked_commonui")
        assert blocked_commonui["blueprint_kind"] == "commonui_widget_blueprint"
        assert blocked_commonui["parent_class"] == "CommonActivatableWidget"
        assert_no_authoring_steps(blocked_commonui)

        unknown = contract.build_job_manifest("unknown", "Make BP magic happen", temp_package_path=custom_temp_path)
        assert unknown["status"] == planner.STATUS_REVIEW
        assert_no_authoring_steps(unknown)
        assert any(reason["key"] == "insufficient_specificity" for reason in unknown["blocked_review_reasons"])

        enhanced_input = contract.build_job_manifest(
            "enhanced_input",
            "Create Enhanced Input action glue for an Input Action asset.",
            temp_package_path=custom_temp_path,
        )
        assert enhanced_input["planner"]["status"] == planner.STATUS_SAFE
        assert enhanced_input["executable"] is False
        assert_no_authoring_steps(enhanced_input)
        assert any(reason["key"] == "contract_executor_missing_enhanced_input_glue" for reason in enhanced_input["blocked_review_reasons"])

        assert not (output_dir.parent / "bp_authoring_job_contract_report.json").exists()

    print("BP authoring job contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
