#!/usr/bin/env python
"""Smoke tests for bp_authoring_planner.py."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_planner as planner  # noqa: E402


def fixture_quality_gate() -> dict:
    return {
        "verdict": {
            "status": "existing_bp_authoring_quality_gate_passed",
        }
    }


def fixture_combined_report() -> dict:
    return {
        "verdict": {
            "current_authoring_ceiling": "temporary_smoke_only_bp_shells_allowlisted_actor_parent_component_hierarchy_property_graph_glue_validation_durable_read_only_asset_exists_preflight_overwrite_rename_decision_save_gate_rollback_draft_executor_readiness_checklist_and_disabled_executor_skeleton",
            "not_ready_for": [
                "replication/RPC/ReplicationGraph lowering",
                "Gameplay Ability System internals and ability-task flow",
            ],
        }
    }


def fixture_delegate_report() -> dict:
    return {
        "verdict": {
            "safe_now": [
                "declare and call Blueprint Event Dispatchers with signature graphs",
                "assign, unbind, and clear Blueprint Event Dispatcher lifecycle nodes",
            ],
            "unsafe_without_reinforcement": [
                "generic delegate lifecycle authoring for non-Event-Dispatcher targets",
                "async action proxy nodes with callback exec outputs",
            ],
        },
        "source_scan": {
            "lifecycle_classifier": {
                "site_count": 263,
            },
            "async_proxy_inventory": {
                "summary": {
                    "class_count": 13,
                    "classes_requiring_callback_exec_model": 13,
                }
            },
        },
    }


def find_plan(report: dict, plan_id: str) -> dict:
    for plan in report["plans"]:
        if plan["id"] == plan_id:
            return plan
    raise AssertionError(f"missing plan {plan_id}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mcp_bp_authoring_planner_fixture_") as temp_dir:
        output_dir = Path(temp_dir) / "out"
        report = planner.build_report(
            planner.DEFAULT_SAMPLE_REQUESTS,
            output_dir,
            fixture_quality_gate(),
            fixture_combined_report(),
            fixture_delegate_report(),
        )
        json_path, md_path = planner.write_report(report, output_dir)

        assert json_path.exists()
        assert md_path.exists()
        assert report["policy"]["lyra_specific_content_dependency"] is False
        assert report["policy_basis"]["async_proxy_classes"] == 13

        simple_actor = find_plan(report, "simple_actor_bp")
        assert simple_actor["status"] == planner.STATUS_SAFE
        assert any(step["key"] == "blueprint_shell" for step in simple_actor["safe_steps"])
        assert "create_blueprint" in simple_actor["needed_mcp_tools"]

        event_dispatcher = find_plan(report, "event_dispatcher_lifecycle")
        assert event_dispatcher["status"] == planner.STATUS_SAFE
        assert any(step["key"] == "event_dispatcher_lifecycle" for step in event_dispatcher["safe_steps"])
        assert not event_dispatcher["blocked_items"]

        async_proxy = find_plan(report, "async_proxy_request")
        assert async_proxy["status"] == planner.STATUS_BLOCKED
        assert any(item["key"] == "async_proxy_callback_exec" for item in async_proxy["blocked_items"])

        gas_replication = find_plan(report, "gas_replication_request")
        assert gas_replication["status"] == planner.STATUS_BLOCKED
        assert any(item["key"] == "gas_ability_task" for item in gas_replication["blocked_items"])
        assert any(item["key"] == "replication_rpc" for item in gas_replication["blocked_items"])

        commonui = find_plan(report, "commonui_request")
        assert commonui["status"] == planner.STATUS_BLOCKED
        assert any(item["key"] == "commonui_structure" for item in commonui["blocked_items"])

        unknown = planner.plan_request("unknown", "Make it feel better and more code-quality")
        assert unknown["status"] == planner.STATUS_REVIEW
        assert any(item["key"] == "insufficient_specificity" for item in unknown["requires_review"])

        dispatcher_delegate = planner.plan_request("dispatcher", "Use a Blueprint Event Dispatcher delegate and bind/unbind it")
        assert dispatcher_delegate["status"] == planner.STATUS_SAFE
        assert not dispatcher_delegate["blocked_items"]

        function_graph = planner.plan_request("function_graph", "Create a function graph with input parameter and return node")
        assert function_graph["status"] == planner.STATUS_SAFE
        assert any(step["key"] == "function_graph_glue" for step in function_graph["safe_steps"])
        assert "resolve_blueprint_graph" in function_graph["needed_mcp_tools"]
        assert "add_blueprint_function_parameter" in function_graph["needed_mcp_tools"]

        function_body = planner.plan_request(
            "function_body",
            "Create a function graph with a local variable, math node, dataflow, and return node",
        )
        assert function_body["status"] == planner.STATUS_SAFE
        assert any(step["key"] == "function_graph_glue" for step in function_body["safe_steps"])
        assert "add_blueprint_local_variable" in function_body["needed_mcp_tools"]
        assert "add_blueprint_math_node" in function_body["needed_mcp_tools"]
        assert "add_blueprint_variable_get_node" in function_body["needed_mcp_tools"]

        component_hierarchy = planner.plan_request(
            "component_hierarchy",
            "Create an Actor Blueprint shell with a Scene Component root and a child Static Mesh Component attached to that root.",
        )
        assert component_hierarchy["status"] == planner.STATUS_SAFE
        assert any(step["key"] == "blueprint_shell" for step in component_hierarchy["safe_steps"])
        assert any(step["key"] == "component_setup" for step in component_hierarchy["safe_steps"])
        assert "add_component_to_blueprint" in component_hierarchy["needed_mcp_tools"]
        assert "list_blueprint_components" in component_hierarchy["needed_mcp_tools"]

        component_property = planner.plan_request(
            "component_property",
            "Create an Actor Blueprint shell with a Static Mesh Component visibility false.",
        )
        assert component_property["status"] == planner.STATUS_SAFE
        assert any(step["key"] == "blueprint_shell" for step in component_property["safe_steps"])
        assert any(step["key"] == "component_setup" for step in component_property["safe_steps"])
        assert "add_component_to_blueprint" in component_property["needed_mcp_tools"]
        assert "get_component_property" in component_property["needed_mcp_tools"]

        local_set = planner.plan_request(
            "local_set",
            "Create a function graph with an input parameter, math node, local variable set node, and return node",
        )
        assert local_set["status"] == planner.STATUS_SAFE
        assert any(step["key"] == "function_graph_glue" for step in local_set["safe_steps"])
        assert "add_blueprint_variable_set_node" in local_set["needed_mcp_tools"]

        compare_branch = planner.plan_request(
            "compare_branch",
            "Create a function graph with an input parameter, compare node, branch, then and else local variable set nodes, and return node",
        )
        assert compare_branch["status"] == planner.STATUS_SAFE
        assert any(step["key"] == "function_graph_glue" for step in compare_branch["safe_steps"])
        assert "add_blueprint_compare_node" in compare_branch["needed_mcp_tools"]
        assert "add_blueprint_branch_node" in compare_branch["needed_mcp_tools"]
        assert "add_blueprint_variable_set_node" in compare_branch["needed_mcp_tools"]

        typed_defaults = planner.plan_request(
            "typed_defaults",
            "Create an Actor Blueprint shell with a Scene Component, bool variable default, string variable default, and vector variable default.",
        )
        assert typed_defaults["status"] == planner.STATUS_SAFE
        assert any(step["key"] == "blueprint_shell" for step in typed_defaults["safe_steps"])
        assert any(step["key"] == "component_setup" for step in typed_defaults["safe_steps"])
        assert any(step["key"] == "variables_defaults" for step in typed_defaults["safe_steps"])
        assert "add_blueprint_variable" in typed_defaults["needed_mcp_tools"]
        assert "add_component_to_blueprint" in typed_defaults["needed_mcp_tools"]
        assert "list_blueprint_components" in typed_defaults["needed_mcp_tools"]

        sequence_flow = planner.plan_request(
            "sequence_flow",
            "Create an Actor Blueprint shell with BeginPlay, a Sequence node, and two PrintString calls.",
        )
        assert sequence_flow["status"] == planner.STATUS_SAFE
        assert any(step["key"] == "function_graph_glue" for step in sequence_flow["safe_steps"])
        assert "add_blueprint_sequence_node" in sequence_flow["needed_mcp_tools"]
        assert "add_blueprint_call_function_node" in sequence_flow["needed_mcp_tools"]

        generated_invocation = planner.plan_request(
            "generated_invocation",
            "Create a function graph and call the generated function from BeginPlay with an input default",
        )
        assert generated_invocation["status"] == planner.STATUS_SAFE
        assert any(step["key"] == "function_graph_glue" for step in generated_invocation["safe_steps"])
        assert "add_blueprint_call_function_node" in generated_invocation["needed_mcp_tools"]
        assert "add_blueprint_variable_set_node" in generated_invocation["needed_mcp_tools"]
        assert "add_blueprint_self_reference" in generated_invocation["needed_mcp_tools"]

        native_delegate = planner.plan_request("native_delegate", "Bind a native delegate with AddUObject and RemoveAll cleanup")
        assert native_delegate["status"] == planner.STATUS_BLOCKED
        assert any(item["key"] == "native_delegate_lifecycle" for item in native_delegate["blocked_items"])

        assert not (output_dir.parent / "bp_authoring_quality_planner_report.json").exists()

    print("BP authoring planner smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
