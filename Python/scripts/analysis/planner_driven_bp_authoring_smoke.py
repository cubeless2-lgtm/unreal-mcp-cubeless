#!/usr/bin/env python
"""
Planner-driven live Blueprint authoring smoke.

This gate proves that Blueprint authoring is routed through
bp_authoring_planner first. Only `safe_to_author` requests may reach the live
UnrealMCP bridge; review and blocked requests are recorded as prevented and do
not send any asset-authoring commands.
"""

from __future__ import annotations

import argparse
import json
import math
import socket
import uuid
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import bp_authoring_job_contract as job_contract
import bp_authoring_manifest_executor as manifest_executor
import bp_authoring_planner as planner
import bp_authoring_quality_gate as quality_gate
import external_project_readiness_analyzer as base


DEFAULT_TEMP_PACKAGE_PATH = "/Game/_MCP_Temp/PlannerDrivenSmoke"
DEFAULT_HOST = quality_gate.DEFAULT_HOST
DEFAULT_PORT = quality_gate.DEFAULT_PORT

MANIFEST_EXECUTION_SECTIONS: Tuple[str, ...] = manifest_executor.EXECUTION_SECTIONS


REQUESTS: Tuple[Tuple[str, str], ...] = (
    (
        "safe_actor_shell",
        "Create an Actor Blueprint shell with a Static Mesh Component, exposed health variable, BeginPlay event, and branch.",
    ),
    (
        "safe_function_call_defaults",
        "Create an Actor Blueprint shell with a Static Mesh Component using the Engine cube mesh, float speed variable default 450, BeginPlay branch, and PrintString function call.",
    ),
    (
        "safe_component_hierarchy",
        "Create an Actor Blueprint shell with a Scene Component root named PlannerSmokeRoot and a child Static Mesh Component named PlannerSmokeMesh attached to PlannerSmokeRoot, plus BeginPlay branch.",
    ),
    (
        "safe_component_property_defaults",
        "Create an Actor Blueprint shell with a Static Mesh Component visibility false and BeginPlay branch.",
    ),
    (
        "review_component_property_unsupported",
        "Create an Actor Blueprint shell with a Static Mesh Component component property CastShadow false.",
    ),
    (
        "review_parent_class_unsupported",
        "Create a Character Blueprint shell with a Static Mesh Component and BeginPlay branch.",
    ),
    (
        "review_durable_authoring_save_requested",
        "Create and save a durable Actor Blueprint named BP_PlannerDurable in /Game/Blueprints with a Static Mesh Component and BeginPlay branch.",
    ),
    (
        "safe_function_graph_authoring",
        "Create an Actor Blueprint shell with a function graph named ComputePlannerValue, int input InputValue default 3, int output ResultValue default 7, and a return node.",
    ),
    (
        "safe_function_graph_body_math",
        "Create an Actor Blueprint shell with a function graph named ComputePlannerBody, double local variable LocalValue default 5, an add math node using LocalValue plus 2, double output ResultValue, connect the math result to the return node, and compile.",
    ),
    (
        "safe_function_graph_local_set",
        "Create an Actor Blueprint shell with a function graph named ComputePlannerLocalSet, double input InputValue default 3, double local variable AccumulatedValue default 0, add 2 to InputValue, set AccumulatedValue from the math result, then return AccumulatedValue as ResultValue.",
    ),
    (
        "safe_function_graph_compare_branch",
        "Create an Actor Blueprint shell with a function graph named ComputePlannerBranch, double input InputValue default 3, double output ResultValue default 0, double local variable BranchResult default 0, compare InputValue greater than 10, branch on the comparison, set BranchResult to 1 on then and -1 on else, then return BranchResult as ResultValue.",
    ),
    (
        "safe_typed_variables_defaults",
        "Create an Actor Blueprint shell with a Scene Component transform default, bool variable bPlannerEnabled default true, string variable PlannerLabel default Section22, and vector variable PlannerOffset default X=10 Y=20 Z=30.",
    ),
    (
        "safe_event_sequence_flow",
        "Create an Actor Blueprint shell with BeginPlay, a Sequence node with two outputs, and two PrintString calls for the first and second sequence outputs.",
    ),
    (
        "safe_generated_function_invocation",
        "Create an Actor Blueprint shell with BeginPlay, a function graph named ComputePlannerInvocation, double input AddendValue default 2, double local variable LocalValue default 5, an add math node returning ResultValue, then call the generated function from BeginPlay with AddendValue default 2 and store the ResultValue output in double variable LastInvocationResult default 0.",
    ),
    (
        "safe_event_dispatcher",
        "Create a Blueprint Event Dispatcher, call it, bind it to a compatible custom event, assign it, unbind it, and clear it.",
    ),
    (
        "review_umg_button",
        "Create a UMG button click event graph for a UserWidget.",
    ),
    (
        "blocked_async_proxy",
        "Convert a UBlueprintAsyncActionBase async action with callback exec pins, Activate(), Broadcast(), and cancellation cleanup.",
    ),
    (
        "blocked_gas_replication",
        "Build a Gameplay Ability with AbilityTask prediction and replicated Server RPC state changes.",
    ),
    (
        "blocked_commonui",
        "Create a CommonUI activatable widget tree with layer activation policy and back handling.",
    ),
)


def repo_root_from_script() -> Path:
    return base.repo_root_from_script()


def request_pairs_from_args(requests: Sequence[str]) -> List[Tuple[str, str]]:
    if not requests:
        return list(REQUESTS)
    return [(f"request_{index + 1}", request) for index, request in enumerate(requests)]


def build_plans(requests: Sequence[Tuple[str, str]]) -> List[Dict[str, Any]]:
    return [manifest["planner"] for manifest in build_manifests(requests, DEFAULT_TEMP_PACKAGE_PATH)]


def build_manifests(requests: Sequence[Tuple[str, str]], temp_package_path: str) -> List[Dict[str, Any]]:
    return job_contract.build_manifests(requests, temp_package_path=temp_package_path)


def summarize_planner_gate(manifests: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    status_counts = Counter(manifest["status"] for manifest in manifests)
    safe_manifests = [manifest for manifest in manifests if manifest["status"] == planner.STATUS_SAFE and manifest["executable"]]
    review_manifests = [manifest for manifest in manifests if manifest["status"] == planner.STATUS_REVIEW]
    blocked_manifests = [manifest for manifest in manifests if manifest["status"] == planner.STATUS_BLOCKED]
    prevented_manifests = [manifest for manifest in manifests if manifest["status"] != planner.STATUS_SAFE or not manifest["executable"]]
    return {
        "safe_request_count": len(safe_manifests),
        "requires_review_request_count": len(review_manifests),
        "blocked_until_reinforced_request_count": len(blocked_manifests),
        "prevented_request_count": len(prevented_manifests),
        "status_counts": {
            planner.STATUS_SAFE: status_counts.get(planner.STATUS_SAFE, 0),
            planner.STATUS_REVIEW: status_counts.get(planner.STATUS_REVIEW, 0),
            planner.STATUS_BLOCKED: status_counts.get(planner.STATUS_BLOCKED, 0),
        },
        "authoring_queue": [
            {
                "id": manifest["id"],
                "status": manifest["status"],
                "request": manifest["request_original"],
                "blueprint_kind": manifest["blueprint_kind"],
                "parent_class": manifest["parent_class"],
                "manifest_version": manifest["manifest_version"],
            }
            for manifest in safe_manifests
        ],
        "prevented_requests": [
            {
                "id": manifest["id"],
                "status": manifest["status"],
                "request": manifest["request_original"],
                "authoring_attempted": False,
                "blocked_items": manifest["planner"].get("blocked_items", []),
                "requires_review": manifest["planner"].get("requires_review", []),
                "blocked_review_reasons": manifest.get("blocked_review_reasons", []),
                "durable_preflight_contract": manifest.get("durable_preflight_contract", {}),
                "durable_executor_skeleton_contract": manifest.get("durable_executor_skeleton_contract", {}),
            }
            for manifest in prevented_manifests
        ],
        "false_safe_guard": "Only executable safe_to_author job manifests are placed in the live authoring queue.",
    }


def bridge_available(host: str, port: int) -> bool:
    try:
        with socket.create_connection((host, port), timeout=2.0):
            return True
    except OSError:
        return False


def execute_python_json(host: str, port: int, code: str, stage_results: List[Dict[str, Any]], timeout: float = 60.0) -> Dict[str, Any]:
    return quality_gate.execute_python_json(host, port, code, stage_results, timeout=timeout)


def list_temp_assets(host: str, port: int, temp_package_path: str, stage_results: List[Dict[str, Any]]) -> List[str]:
    code = f"""
import json
import unreal
temp_package_path = {temp_package_path!r}
assets = []
if unreal.EditorAssetLibrary.does_directory_exist(temp_package_path):
    assets = [str(asset) for asset in unreal.EditorAssetLibrary.list_assets(temp_package_path, recursive=True, include_folder=False)]
print({quality_gate.JSON_LOG_PREFIX!r} + json.dumps({{"assets": assets}}))
"""
    return execute_python_json(host, port, code, stage_results).get("assets", [])


def run_durable_preflight_read_only_check(
    host: str,
    port: int,
    manifest: Dict[str, Any],
    stage_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    contract = manifest.get("durable_preflight_contract", {})
    target_asset_path = contract.get("target_asset_path", "")
    result: Dict[str, Any] = {
        "schema": "section_35_durable_preflight_live_result_v1",
        "manifest_id": manifest["id"],
        "target_asset_path": target_asset_path,
        "status": "not_requested",
        "read_only": True,
        "authoring_attempted": False,
        "save_or_delete_attempted": False,
        "asset_exists_check_performed": False,
        "asset_exists": None,
        "preflight_pass": False,
    }
    if not contract.get("requested"):
        result["status"] = "skipped"
        result["reason"] = "durable preflight was not requested"
        return result
    if not contract.get("live_read_only_check_allowed") or not target_asset_path:
        result["status"] = "failed"
        result["reason"] = "durable preflight target is missing or not allowed for live read-only check"
        return result

    code = f"""
import json
import unreal
target_asset_path = {target_asset_path!r}
data = {{
    "target_asset_path": target_asset_path,
    "asset_exists": bool(unreal.EditorAssetLibrary.does_asset_exist(target_asset_path)),
}}
print({quality_gate.JSON_LOG_PREFIX!r} + json.dumps(data))
"""
    live_data = execute_python_json(host, port, code, stage_results)
    result.update(
        {
            "status": "passed",
            "asset_exists_check_performed": True,
            "asset_exists": bool(live_data.get("asset_exists", False)),
            "target_asset_path": live_data.get("target_asset_path", target_asset_path),
            "preflight_pass": False,
        }
    )
    return result


def inspect_asset(host: str, port: int, asset_path: str, stage_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    code = f"""
import json
import unreal
asset_path = {asset_path!r}
asset = unreal.EditorAssetLibrary.load_asset(asset_path)
data = {{
    "asset_path": asset_path,
    "asset_exists": unreal.EditorAssetLibrary.does_asset_exist(asset_path),
    "asset_class": asset.get_class().get_name() if asset else "",
}}
print({quality_gate.JSON_LOG_PREFIX!r} + json.dumps(data))
"""
    return execute_python_json(host, port, code, stage_results)


def cleanup_generated_asset(host: str, port: int, asset_path: str, stage_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    return quality_gate.cleanup_temp_asset(host, port, asset_path, stage_results)


def blueprint_name_for_manifest(manifest: Dict[str, Any], run_id: str) -> str:
    return manifest["blueprint_name_template"].format(run_id=run_id)


def require_success(
    host: str,
    port: int,
    command: str,
    params: Dict[str, Any],
    stage_results: List[Dict[str, Any]],
    timeout: float = 60.0,
) -> Dict[str, Any]:
    return quality_gate.require_success(host, port, command, params, stage_results, timeout=timeout)


def expand_manifest_param_value(value: Any, blueprint_name: str, temp_package_path: str) -> Any:
    if isinstance(value, str):
        return value.format(blueprint_name=blueprint_name, temp_package_path=temp_package_path)
    if isinstance(value, list):
        return [expand_manifest_param_value(item, blueprint_name, temp_package_path) for item in value]
    if isinstance(value, dict):
        return {key: expand_manifest_param_value(item, blueprint_name, temp_package_path) for key, item in value.items()}
    return value


def params_for_manifest_command(blueprint_name: str, step: Dict[str, Any], temp_package_path: str) -> Dict[str, Any]:
    command = step.get("command", "")
    if command == "add_component_to_blueprint":
        transform = step.get("transform", {})
        params = {
            "component_type": step["component_type"],
            "component_name": step["component_name"],
            "location": transform.get("location", [0, 0, 0]),
            "rotation": transform.get("rotation", [0, 0, 0]),
            "scale": transform.get("scale", [1, 1, 1]),
        }
        if step.get("parent_component_name"):
            params["parent_component_name"] = step["parent_component_name"]
    elif command == "add_blueprint_variable":
        params = {
            "variable_name": step["variable_name"],
            "variable_type": step["variable_type"],
            "default_value": step.get("default_value"),
            "category": step.get("category", "Planner Smoke"),
        }
        for optional_key in ("is_exposed", "tooltip", "friendly_name", "type_object", "is_array", "metadata"):
            if optional_key in step:
                params[optional_key] = step[optional_key]
    elif command == "set_static_mesh_properties":
        params = {
            "component_name": step["component_name"],
            "static_mesh": step["static_mesh"],
        }
    elif command == "set_component_property":
        params = {
            "component_name": step["component_name"],
            "property_name": step["property_name"],
            "property_value": step.get("property_value"),
        }
    else:
        params = dict(step.get("params", {}))
    params = expand_manifest_param_value(params, blueprint_name, temp_package_path)
    params["blueprint_name"] = blueprint_name
    return params


class ManifestStepFailure(quality_gate.BridgeError):
    def __init__(self, diagnostic: Dict[str, Any]):
        self.diagnostic = diagnostic
        super().__init__(diagnostic.get("error", "Manifest step failed"))


def summarize_stage_tail(stage_results: Sequence[Dict[str, Any]], limit: int = 5) -> List[Dict[str, Any]]:
    return [
        {
            "command": stage.get("command", ""),
            "status": stage.get("status", ""),
        }
        for stage in stage_results[-limit:]
    ]


def referenced_node_refs(step: Dict[str, Any]) -> Dict[str, str]:
    refs: Dict[str, str] = {}
    for key in ("node_ref", "source_node_ref", "target_node_ref", "graph_ref"):
        value = step.get(key)
        if value:
            refs[key] = str(value)
    return refs


def summarize_node_cache(node_results: Dict[str, Dict[str, Any]], refs: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
    summary: Dict[str, Dict[str, Any]] = {}
    for ref_name in refs.values():
        node = node_results.get(ref_name)
        if not isinstance(node, dict):
            continue
        summary[ref_name] = {
            "node_id": node.get("node_id", ""),
            "node_class": node.get("class", ""),
            "node_title": node.get("title", ""),
            "graph_name": node.get("graph", {}).get("graph_name", ""),
            "graph_type": node.get("graph", {}).get("graph_type", ""),
            "x": node.get("x"),
            "y": node.get("y"),
            "pin_count": len(node.get("pins", [])),
        }
    return summary


def build_failure_diagnostic(
    manifest: Dict[str, Any],
    blueprint_name: str,
    section: str,
    step: Dict[str, Any],
    node_results: Dict[str, Dict[str, Any]],
    stage_results: Sequence[Dict[str, Any]],
    exc: Exception,
    phase: str,
) -> Dict[str, Any]:
    node_refs = referenced_node_refs(step)
    return {
        "diagnostic_schema": "section_21_failure_diagnostics_v1",
        "manifest_id": manifest.get("id", ""),
        "manifest_version": manifest.get("manifest_version", ""),
        "blueprint_name": blueprint_name,
        "temp_package_path": manifest.get("temp_package_path", ""),
        "phase": phase,
        "section": section,
        "step_id": step.get("id", ""),
        "source_step": step.get("source_step", ""),
        "operation": step.get("operation", "command"),
        "command": step.get("command", ""),
        "graph_name": step.get("graph_name", step.get("params", {}).get("graph_name", "")),
        "graph_type": step.get("graph_type", step.get("params", {}).get("graph_type", "")),
        "node_refs": node_refs,
        "available_node_refs": sorted(node_results.keys()),
        "node_cache": summarize_node_cache(node_results, node_refs),
        "stage_tail": summarize_stage_tail(stage_results, manifest.get("failure_diagnostics_contract", {}).get("stage_tail_count", 5)),
        "error_type": type(exc).__name__,
        "error": str(exc),
    }


def get_manifest_node(node_results: Dict[str, Dict[str, Any]], step: Dict[str, Any], key: str) -> Dict[str, Any]:
    node_ref = step[key]
    if node_ref not in node_results:
        raise quality_gate.BridgeError(f"Manifest step references missing node result '{node_ref}': {step}")
    return node_results[node_ref]


def manifest_pin_name(node: Dict[str, Any], direction: str, pin_kind: str, preferred: Iterable[str]) -> str:
    if pin_kind == "exec":
        return quality_gate.find_exec_pin(node, direction, preferred)
    return quality_gate.find_pin(node, direction, preferred)


def assert_manifest_pin(node: Dict[str, Any], step: Dict[str, Any]) -> None:
    expected_names = set(step.get("pin_names", []))
    matching_pins = [
        pin
        for pin in node.get("pins", [])
        if pin.get("direction") == step.get("direction") and pin.get("name") in expected_names
    ]
    must_exist = bool(step.get("must_exist", True))
    if must_exist and not matching_pins:
        raise quality_gate.BridgeError(f"Manifest pin assertion failed; expected pin missing: {step} node={node}")
    if not must_exist and matching_pins:
        raise quality_gate.BridgeError(f"Manifest pin assertion failed; unexpected pin present: {step} node={node}")


def normalize_pin_lookup(value: str) -> str:
    return value.lower().replace(" ", "").replace("_", "")


def find_node_by_id(nodes_result: Dict[str, Any], node_id: str) -> Optional[Dict[str, Any]]:
    for node in nodes_result.get("nodes", []):
        if node.get("node_id") == node_id:
            return node
    return None


def hydrate_node_result_if_needed(
    host: str,
    port: int,
    blueprint_name: str,
    step: Dict[str, Any],
    result: Dict[str, Any],
    stage_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    node_id = result.get("node_id", "")
    if not node_id or result.get("pins"):
        return result

    step_params = step.get("params", {})
    list_params: Dict[str, Any] = {
        "blueprint_name": blueprint_name,
        "include_pins": True,
    }
    for selector_key in ("graph_name", "graph_id", "graph_type"):
        selector_value = step_params.get(selector_key)
        if selector_value:
            list_params[selector_key] = selector_value

    nodes = require_success(host, port, "list_blueprint_nodes", list_params, stage_results, timeout=120.0)
    refreshed = find_node_by_id(nodes, node_id)
    if not refreshed:
        return result
    merged = dict(result)
    merged.update(refreshed)
    return merged


def refreshed_manifest_node(node_results: Dict[str, Dict[str, Any]], step: Dict[str, Any], key: str) -> Dict[str, Any]:
    original_node = get_manifest_node(node_results, step, key)
    node_id = original_node.get("node_id", "")
    if not node_id:
        raise quality_gate.BridgeError(f"Manifest structural assertion references a non-node result: {step} result={original_node}")

    graph_type = step.get("graph_type", "")
    preferred_sources: List[str] = []
    if graph_type == "function":
        preferred_sources = ["function_nodes", "event_nodes"]
    elif graph_type == "event":
        preferred_sources = ["event_nodes", "function_nodes"]
    else:
        preferred_sources = ["function_nodes", "event_nodes"]

    for result_key in preferred_sources:
        refreshed = find_node_by_id(node_results.get(result_key, {}), node_id)
        if refreshed:
            return refreshed
    return original_node


def find_manifest_pin(node: Dict[str, Any], direction: str, pin_names: Iterable[str]) -> Dict[str, Any]:
    normalized_names = {normalize_pin_lookup(name) for name in pin_names}
    for pin in node.get("pins", []):
        if pin.get("direction") == direction and normalize_pin_lookup(pin.get("name", "")) in normalized_names:
            return pin
    raise quality_gate.BridgeError(f"Expected {direction} pin not found. names={list(pin_names)} node={node}")


def pin_default_matches(actual_value: Any, expected_value: Any) -> bool:
    actual = "" if actual_value is None else str(actual_value)
    if isinstance(expected_value, bool):
        return actual.lower() == ("true" if expected_value else "false")
    if isinstance(expected_value, (int, float)):
        try:
            return abs(float(actual) - float(expected_value)) < 0.0001
        except ValueError:
            return False
    return actual == str(expected_value)


def numeric_sequence_matches(actual: Any, expected: Any, tolerance: float) -> bool:
    if not isinstance(actual, list) or not isinstance(expected, list) or len(actual) != len(expected):
        return False
    try:
        return all(abs(float(actual_value) - float(expected_value)) <= tolerance for actual_value, expected_value in zip(actual, expected))
    except (TypeError, ValueError):
        return False


def component_class_matches(actual_class: str, expected_type: str) -> bool:
    normalized_actual = actual_class.lower()
    normalized_expected = expected_type.lower()
    if normalized_actual == normalized_expected:
        return True
    return normalized_actual.endswith(normalized_expected)


def assert_blueprint_component_default(
    host: str,
    port: int,
    blueprint_name: str,
    step: Dict[str, Any],
    stage_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    result = require_success(
        host,
        port,
        "list_blueprint_components",
        {"blueprint_name": blueprint_name, "component_name": step["component_name"]},
        stage_results,
        timeout=120.0,
    )
    components = [
        component
        for component in result.get("components", [])
        if component.get("component_name") == step["component_name"]
    ]
    if not components:
        raise quality_gate.BridgeError(f"Component default assertion could not find component: step={step} result={result}")
    component = components[0]
    if not component_class_matches(component.get("component_class", ""), step.get("component_type", "")):
        raise quality_gate.BridgeError(f"Component class mismatch: step={step} component={component}")

    tolerance = float(step.get("tolerance", 0.0001))
    expected_transform = step.get("expected_transform", {})
    actual_transform = component.get("relative_transform", {})
    transform_checks = {}
    for key in ("location", "rotation", "scale"):
        expected_value = expected_transform.get(key)
        if expected_value is None:
            continue
        actual_value = actual_transform.get(key)
        if not numeric_sequence_matches(actual_value, expected_value, tolerance):
            raise quality_gate.BridgeError(
                f"Component transform mismatch for {key}: expected={expected_value} actual={actual_value} step={step} component={component}"
            )
        transform_checks[key] = actual_value

    expected_static_mesh = step.get("expected_static_mesh", "")
    if expected_static_mesh:
        actual_static_mesh = component.get("static_mesh", "")
        if actual_static_mesh != expected_static_mesh:
            raise quality_gate.BridgeError(
                f"Component static mesh mismatch: expected={expected_static_mesh} actual={actual_static_mesh} step={step} component={component}"
            )

    return {
        "component_name": component.get("component_name", ""),
        "component_class": component.get("component_class", ""),
        "relative_transform": actual_transform,
        "transform_checks": transform_checks,
        "static_mesh": component.get("static_mesh", ""),
    }


def assert_blueprint_component_hierarchy(
    host: str,
    port: int,
    blueprint_name: str,
    step: Dict[str, Any],
    stage_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    result = require_success(
        host,
        port,
        "list_blueprint_components",
        {"blueprint_name": blueprint_name, "component_name": step["component_name"]},
        stage_results,
        timeout=120.0,
    )
    components = [
        component
        for component in result.get("components", [])
        if component.get("component_name") == step["component_name"]
    ]
    if not components:
        raise quality_gate.BridgeError(f"Component hierarchy assertion could not find component: step={step} result={result}")
    component = components[0]
    expected_parent = step.get("expected_parent_component_name", "")
    actual_parent = component.get("parent_component_name", "")
    if actual_parent != expected_parent:
        raise quality_gate.BridgeError(
            f"Component hierarchy mismatch: expected_parent={expected_parent} actual_parent={actual_parent} step={step} component={component}"
        )
    return {
        "component_name": component.get("component_name", ""),
        "parent_component_name": actual_parent,
    }


def values_match(actual_value: Any, expected_value: Any, tolerance: float) -> bool:
    if isinstance(expected_value, bool):
        return isinstance(actual_value, bool) and actual_value == expected_value
    if isinstance(expected_value, (int, float)) and not isinstance(expected_value, bool):
        return isinstance(actual_value, (int, float)) and abs(float(actual_value) - float(expected_value)) <= tolerance
    if isinstance(expected_value, list):
        return numeric_sequence_matches(actual_value, expected_value, tolerance)
    return actual_value == expected_value


def assert_blueprint_component_property(
    host: str,
    port: int,
    blueprint_name: str,
    step: Dict[str, Any],
    stage_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    result = require_success(
        host,
        port,
        "get_component_property",
        {
            "blueprint_name": blueprint_name,
            "component_name": step["component_name"],
            "property_name": step["property_name"],
        },
        stage_results,
        timeout=120.0,
    )
    expected_value = step.get("expected_value")
    actual_value = result.get("property_value")
    tolerance = float(step.get("tolerance", 0.0001))
    if not values_match(actual_value, expected_value, tolerance):
        raise quality_gate.BridgeError(
            f"Component property mismatch: expected={expected_value} actual={actual_value} step={step} result={result}"
        )
    return {
        "component_name": result.get("component_name", ""),
        "property_name": result.get("property_name", ""),
        "property_type": result.get("property_type", ""),
        "property_value": actual_value,
    }


def assert_blueprint_variable_default(
    host: str,
    port: int,
    blueprint_name: str,
    temp_package_path: str,
    step: Dict[str, Any],
    stage_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    asset_path = f"{temp_package_path}/{blueprint_name}"
    expected_json = json.dumps(step.get("expected_value"), ensure_ascii=False)
    variable_name = step["variable_name"]
    tolerance = float(step.get("tolerance", 0.0001))
    code = f"""
import json
import math
import unreal

asset_path = {asset_path!r}
variable_name = {variable_name!r}
expected = json.loads({expected_json!r})
tolerance = {tolerance!r}
asset = unreal.EditorAssetLibrary.load_asset(asset_path)

def normalize_value(value):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float, str)):
        return value
    if hasattr(value, "x") and hasattr(value, "y") and hasattr(value, "z"):
        return [float(value.x), float(value.y), float(value.z)]
    return str(value)

def values_match(actual, expected_value):
    if isinstance(expected_value, bool):
        return isinstance(actual, bool) and actual == expected_value
    if isinstance(expected_value, (int, float)) and not isinstance(expected_value, bool):
        return isinstance(actual, (int, float)) and abs(float(actual) - float(expected_value)) <= tolerance
    if isinstance(expected_value, list):
        if not isinstance(actual, list) or len(actual) != len(expected_value):
            return False
        return all(abs(float(a) - float(e)) <= tolerance for a, e in zip(actual, expected_value))
    return str(actual) == str(expected_value)

data = {{
    "asset_path": asset_path,
    "variable_name": variable_name,
    "expected_value": expected,
    "actual_value": None,
    "matches": False,
    "asset_exists": bool(asset),
}}
if asset:
    generated_class = asset.generated_class()
    cdo = unreal.get_default_object(generated_class)
    actual = normalize_value(cdo.get_editor_property(variable_name))
    data["actual_value"] = actual
    data["matches"] = values_match(actual, expected)
print({quality_gate.JSON_LOG_PREFIX!r} + json.dumps(data))
"""
    result = execute_python_json(host, port, code, stage_results, timeout=120.0)
    if not result.get("matches"):
        raise quality_gate.BridgeError(f"Variable default mismatch: {result}")
    return result


def assert_structural_graph_resolved(node_results: Dict[str, Dict[str, Any]], step: Dict[str, Any]) -> Dict[str, Any]:
    graph_result = get_manifest_node(node_results, step, "graph_ref")
    graph = graph_result.get("graph", {})
    if graph_result.get("resolved") is False:
        raise quality_gate.BridgeError(f"Graph was not resolved: {step} result={graph_result}")
    expected_name = step.get("graph_name", "")
    actual_name = graph.get("graph_name", graph.get("name", ""))
    if expected_name and actual_name != expected_name:
        raise quality_gate.BridgeError(f"Graph name mismatch: expected={expected_name} result={graph_result}")
    expected_type = step.get("graph_type", "")
    if expected_type and graph.get("graph_type") != expected_type:
        raise quality_gate.BridgeError(f"Graph type mismatch: expected={expected_type} result={graph_result}")
    return {"graph_name": actual_name, "graph_type": graph.get("graph_type", "")}


def assert_structural_node_exists(node_results: Dict[str, Dict[str, Any]], step: Dict[str, Any]) -> Dict[str, Any]:
    node = refreshed_manifest_node(node_results, step, "node_ref")
    return {"node_id": node.get("node_id", ""), "node_class": node.get("class", ""), "node_title": node.get("title", "")}


def assert_structural_pin_default(node_results: Dict[str, Dict[str, Any]], step: Dict[str, Any]) -> Dict[str, Any]:
    node = refreshed_manifest_node(node_results, step, "node_ref")
    pin = find_manifest_pin(node, step.get("direction", "input"), [step["pin_name"]])
    if not pin_default_matches(pin.get("default_value"), step.get("value")):
        raise quality_gate.BridgeError(
            f"Pin default mismatch: expected={step.get('value')} actual={pin.get('default_value')} step={step} node={node}"
        )
    return {"node_id": node.get("node_id", ""), "pin_name": pin.get("name", ""), "default_value": pin.get("default_value", "")}


def assert_structural_pin_link(node_results: Dict[str, Dict[str, Any]], step: Dict[str, Any]) -> Dict[str, Any]:
    source_node = refreshed_manifest_node(node_results, step, "source_node_ref")
    target_node = refreshed_manifest_node(node_results, step, "target_node_ref")
    source_pin_name = manifest_pin_name(
        source_node,
        "output",
        step.get("source_pin_kind", "exec"),
        step.get("source_pin_preferred", ()),
    )
    target_pin_name = manifest_pin_name(
        target_node,
        "input",
        step.get("target_pin_kind", "exec"),
        step.get("target_pin_preferred", ()),
    )
    source_pin = find_manifest_pin(source_node, "output", [source_pin_name])
    linked_to = source_pin.get("linked_to", [])
    if not any(link.get("node_id") == target_node.get("node_id") and link.get("pin_name") == target_pin_name for link in linked_to):
        raise quality_gate.BridgeError(
            f"Expected pin link missing: {source_node.get('node_id')}:{source_pin_name} -> "
            f"{target_node.get('node_id')}:{target_pin_name} step={step} linked_to={linked_to}"
        )
    return {
        "source_node_id": source_node.get("node_id", ""),
        "source_pin": source_pin_name,
        "target_node_id": target_node.get("node_id", ""),
        "target_pin": target_pin_name,
        "link_kind": step.get("source_pin_kind", "exec"),
    }


def normalize_function_identity(value: str) -> str:
    return "".join(character.lower() for character in value if character.isalnum())


def assert_function_call_contract(node_results: Dict[str, Dict[str, Any]], step: Dict[str, Any]) -> Dict[str, Any]:
    node = refreshed_manifest_node(node_results, step, "node_ref")
    if node.get("class") != "K2Node_CallFunction":
        raise quality_gate.BridgeError(f"Function call contract expected K2Node_CallFunction: step={step} node={node}")

    expected_function_name = step.get("function_name", "")
    node_identity_text = " ".join(
        str(node.get(key, ""))
        for key in ("title", "function_name", "member_name", "target_function", "target")
    )
    if expected_function_name and normalize_function_identity(expected_function_name) not in normalize_function_identity(node_identity_text):
        raise quality_gate.BridgeError(
            f"Function call identity mismatch: expected={expected_function_name} node_identity={node_identity_text} step={step}"
        )

    input_defaults_verified = []
    for input_default in step.get("input_defaults", []):
        pin = find_manifest_pin(node, input_default.get("direction", "input"), [input_default["pin_name"]])
        if not pin_default_matches(pin.get("default_value"), input_default.get("expected_value")):
            raise quality_gate.BridgeError(
                f"Function call input default mismatch: expected={input_default} actual={pin.get('default_value')} node={node}"
            )
        input_defaults_verified.append(input_default["pin_name"])

    output_pins_verified = []
    for output_pin in step.get("required_output_pins", []):
        pin_names = output_pin.get("pin_names", [])
        pin = find_manifest_pin(node, "output", pin_names)
        output_pins_verified.append(pin.get("name", ""))

    incoming_links_verified = 0
    for link in step.get("required_incoming_exec_links", []):
        assert_structural_pin_link(
            node_results,
            {
                "source_node_ref": link["source_node_ref"],
                "source_pin_kind": link.get("source_pin_kind", "exec"),
                "source_pin_preferred": link.get("source_pin_preferred", ()),
                "target_node_ref": step["node_ref"],
                "target_pin_kind": link.get("target_pin_kind", "exec"),
                "target_pin_preferred": link.get("target_pin_preferred", ()),
            },
        )
        incoming_links_verified += 1

    outgoing_links_verified = 0
    for link in step.get("required_outgoing_links", []):
        assert_structural_pin_link(
            node_results,
            {
                "source_node_ref": step["node_ref"],
                "source_pin_kind": link.get("source_pin_kind", "exec"),
                "source_pin_preferred": link.get("source_pin_preferred", ()),
                "target_node_ref": link["target_node_ref"],
                "target_pin_kind": link.get("target_pin_kind", "exec"),
                "target_pin_preferred": link.get("target_pin_preferred", ()),
            },
        )
        outgoing_links_verified += 1

    return {
        "node_id": node.get("node_id", ""),
        "node_class": node.get("class", ""),
        "node_title": node.get("title", ""),
        "function_name": expected_function_name,
        "function_class": step.get("function_class", ""),
        "input_defaults_verified": input_defaults_verified,
        "output_pins_verified": output_pins_verified,
        "incoming_links_verified": incoming_links_verified,
        "outgoing_links_verified": outgoing_links_verified,
    }


def assert_node_layout(node_results: Dict[str, Dict[str, Any]], step: Dict[str, Any]) -> Dict[str, Any]:
    node = refreshed_manifest_node(node_results, step, "node_ref")
    if "x" not in node or "y" not in node:
        raise quality_gate.BridgeError(f"Node layout assertion requires x/y fields: step={step} node={node}")
    expected = step.get("expected_position", [])
    if not isinstance(expected, list) or len(expected) < 2:
        raise quality_gate.BridgeError(f"Node layout assertion requires expected [x, y]: step={step}")
    tolerance = float(step.get("position_tolerance", 1.0))
    actual = [float(node["x"]), float(node["y"])]
    delta = [actual[0] - float(expected[0]), actual[1] - float(expected[1])]
    if abs(delta[0]) > tolerance or abs(delta[1]) > tolerance:
        raise quality_gate.BridgeError(
            f"Node layout mismatch: expected={expected} actual={actual} tolerance={tolerance} step={step} node={node}"
        )
    return {
        "node_id": node.get("node_id", ""),
        "node_class": node.get("class", ""),
        "node_title": node.get("title", ""),
        "expected_position": expected[:2],
        "actual_position": actual,
        "delta": delta,
        "position_tolerance": tolerance,
    }


def assert_layout_spacing(node_results: Dict[str, Dict[str, Any]], step: Dict[str, Any]) -> Dict[str, Any]:
    source_node = refreshed_manifest_node(node_results, step, "source_node_ref")
    target_node = refreshed_manifest_node(node_results, step, "target_node_ref")
    for label, node in (("source", source_node), ("target", target_node)):
        if "x" not in node or "y" not in node:
            raise quality_gate.BridgeError(f"Layout spacing assertion requires {label} x/y fields: step={step} node={node}")

    source_position = [float(source_node["x"]), float(source_node["y"])]
    target_position = [float(target_node["x"]), float(target_node["y"])]
    delta = [target_position[0] - source_position[0], target_position[1] - source_position[1]]
    actual_distance = math.hypot(delta[0], delta[1])
    minimum_distance = float(step.get("minimum_distance", 1.0))
    if actual_distance < minimum_distance:
        raise quality_gate.BridgeError(
            "Layout spacing mismatch: "
            f"minimum_distance={minimum_distance} actual_distance={actual_distance} "
            f"source={source_position} target={target_position} step={step}"
        )
    return {
        "source_node_id": source_node.get("node_id", ""),
        "target_node_id": target_node.get("node_id", ""),
        "source_node_class": source_node.get("class", ""),
        "target_node_class": target_node.get("class", ""),
        "source_node_title": source_node.get("title", ""),
        "target_node_title": target_node.get("title", ""),
        "source_expected_position": step.get("source_expected_position", [])[:2],
        "target_expected_position": step.get("target_expected_position", [])[:2],
        "source_actual_position": source_position,
        "target_actual_position": target_position,
        "delta": delta,
        "actual_distance": actual_distance,
        "minimum_distance": minimum_distance,
    }


def assert_exec_pin_count(node_results: Dict[str, Dict[str, Any]], step: Dict[str, Any]) -> Dict[str, Any]:
    node = refreshed_manifest_node(node_results, step, "node_ref")
    direction = step.get("direction", "output")
    pins = [
        pin
        for pin in node.get("pins", [])
        if pin.get("direction") == direction and pin.get("category", "").lower() == "exec"
    ]
    minimum_count = int(step.get("minimum_count", 1))
    if len(pins) < minimum_count:
        raise quality_gate.BridgeError(f"Exec pin count mismatch: minimum={minimum_count} actual={len(pins)} step={step} node={node}")
    return {
        "node_id": node.get("node_id", ""),
        "node_class": node.get("class", ""),
        "node_title": node.get("title", ""),
        "direction": direction,
        "minimum_count": minimum_count,
        "actual_count": len(pins),
        "pin_names": [pin.get("name", "") for pin in pins],
    }


def execute_structural_validation_step(node_results: Dict[str, Dict[str, Any]], step: Dict[str, Any]) -> Dict[str, Any]:
    operation = step.get("operation", "")
    if operation == "assert_graph_resolved":
        details = assert_structural_graph_resolved(node_results, step)
    elif operation == "assert_node_exists":
        details = assert_structural_node_exists(node_results, step)
    elif operation == "assert_pin_default":
        details = assert_structural_pin_default(node_results, step)
    elif operation == "assert_pin_link":
        details = assert_structural_pin_link(node_results, step)
    elif operation == "assert_pin":
        node = refreshed_manifest_node(node_results, step, "node_ref")
        assert_manifest_pin(node, step)
        details = {"node_id": node.get("node_id", ""), "pin_names": step.get("pin_names", [])}
    elif operation == "assert_function_call_contract":
        details = assert_function_call_contract(node_results, step)
    elif operation == "assert_node_layout":
        details = assert_node_layout(node_results, step)
    elif operation == "assert_layout_spacing":
        details = assert_layout_spacing(node_results, step)
    elif operation == "assert_exec_pin_count":
        details = assert_exec_pin_count(node_results, step)
    else:
        raise quality_gate.BridgeError(f"Unsupported structural validation operation '{operation}' in step: {step}")
    return {
        "id": step.get("id"),
        "operation": operation,
        "source_step": step.get("source_step", ""),
        "status": "success",
        **details,
    }


def execute_structural_validation_plan(
    manifest: Dict[str, Any],
    node_results: Dict[str, Dict[str, Any]],
) -> List[Dict[str, Any]]:
    results = []
    for step in manifest.get("structural_validation_plan", []):
        results.append(execute_structural_validation_step(node_results, step))
    return results


def execute_manifest_step(
    host: str,
    port: int,
    blueprint_name: str,
    temp_package_path: str,
    step: Dict[str, Any],
    stage_results: List[Dict[str, Any]],
    node_results: Dict[str, Dict[str, Any]],
    section_results: List[Dict[str, Any]],
) -> Optional[Dict[str, Any]]:
    operation = step.get("operation", "command")
    if operation in {"contract_note", "review_only"}:
        section_results.append({"id": step.get("id"), "operation": operation, "status": "skipped"})
        return None

    if operation == "command":
        command = step["command"]
        result = require_success(host, port, command, params_for_manifest_command(blueprint_name, step, temp_package_path), stage_results, timeout=120.0)
        result = hydrate_node_result_if_needed(host, port, blueprint_name, step, result, stage_results)
        store_key = step.get("store_as") or step.get("id")
        if store_key:
            node_results[store_key] = result
        if step.get("must_pass_compile") and (not result.get("validation_pass") or result.get("compile_error_count", 1) != 0):
            raise quality_gate.BridgeError(f"Compile validation failed: {result}")
        section_results.append({"id": step.get("id"), "operation": operation, "command": command, "status": "success"})
        return result

    if operation == "set_pin_default":
        node = get_manifest_node(node_results, step, "node_ref")
        result = require_success(
            host,
            port,
            "set_blueprint_pin_default",
            {
                "blueprint_name": blueprint_name,
                "node_id": node["node_id"],
                "pin_name": step["pin_name"],
                "value": step.get("value"),
                "direction": step.get("direction", "input"),
                "graph_name": step.get("graph_name", ""),
                "graph_id": step.get("graph_id", ""),
                "graph_type": step.get("graph_type", ""),
            },
            stage_results,
        )
        section_results.append({"id": step.get("id"), "operation": operation, "status": "success"})
        return result

    if operation == "connect":
        source_node = get_manifest_node(node_results, step, "source_node_ref")
        target_node = get_manifest_node(node_results, step, "target_node_ref")
        connect_params = {
            "blueprint_name": blueprint_name,
            "source_node_id": source_node["node_id"],
            "source_pin": manifest_pin_name(
                source_node,
                "output",
                step.get("source_pin_kind", "exec"),
                step.get("source_pin_preferred", ()),
            ),
            "target_node_id": target_node["node_id"],
            "target_pin": manifest_pin_name(
                target_node,
                "input",
                step.get("target_pin_kind", "exec"),
                step.get("target_pin_preferred", ()),
            ),
            "graph_name": step.get("graph_name", ""),
            "graph_id": step.get("graph_id", ""),
            "graph_type": step.get("graph_type", ""),
        }
        if "allow_pin_link_replacement" in step:
            connect_params["allow_pin_link_replacement"] = step["allow_pin_link_replacement"]
        result = require_success(
            host,
            port,
            "connect_blueprint_nodes",
            connect_params,
            stage_results,
        )
        section_results.append({"id": step.get("id"), "operation": operation, "status": "success"})
        return result

    if operation == "assert_pin":
        node = get_manifest_node(node_results, step, "node_ref")
        assert_manifest_pin(node, step)
        section_results.append({"id": step.get("id"), "operation": operation, "status": "success"})
        return None

    if operation == "assert_variable_default":
        result = assert_blueprint_variable_default(host, port, blueprint_name, temp_package_path, step, stage_results)
        section_results.append(
            {
                "id": step.get("id"),
                "operation": operation,
                "variable_name": step.get("variable_name", ""),
                "status": "success",
                "actual_value": result.get("actual_value"),
            }
        )
        return result

    if operation == "assert_component_default":
        result = assert_blueprint_component_default(host, port, blueprint_name, step, stage_results)
        section_results.append(
            {
                "id": step.get("id"),
                "operation": operation,
                "component_name": step.get("component_name", ""),
                "status": "success",
                "component_class": result.get("component_class", ""),
                "relative_transform": result.get("relative_transform", {}),
                "static_mesh": result.get("static_mesh", ""),
            }
        )
        return result

    if operation == "assert_component_hierarchy":
        result = assert_blueprint_component_hierarchy(host, port, blueprint_name, step, stage_results)
        section_results.append(
            {
                "id": step.get("id"),
                "operation": operation,
                "component_name": step.get("component_name", ""),
                "status": "success",
                "parent_component_name": result.get("parent_component_name", ""),
            }
        )
        return result

    if operation == "assert_component_property":
        result = assert_blueprint_component_property(host, port, blueprint_name, step, stage_results)
        section_results.append(
            {
                "id": step.get("id"),
                "operation": operation,
                "component_name": step.get("component_name", ""),
                "property_name": step.get("property_name", ""),
                "status": "success",
                "property_type": result.get("property_type", ""),
                "property_value": result.get("property_value"),
            }
        )
        return result

    raise quality_gate.BridgeError(f"Unsupported manifest operation '{operation}' in step: {step}")


def execute_manifest_sections(
    host: str,
    port: int,
    blueprint_name: str,
    manifest: Dict[str, Any],
    stage_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    def run_step(
        section: str,
        step: Dict[str, Any],
        node_results: Dict[str, Dict[str, Any]],
        section_results: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        return execute_manifest_step(
            host,
            port,
            blueprint_name,
            manifest["temp_package_path"],
            step,
            stage_results,
            node_results,
            section_results,
        )

    def run_structural_step(step: Dict[str, Any], node_results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        return execute_structural_validation_step(node_results, step)

    def build_diagnostic(
        section: str,
        step: Dict[str, Any],
        node_results: Dict[str, Dict[str, Any]],
        exc: Exception,
        phase: str,
    ) -> Dict[str, Any]:
        return build_failure_diagnostic(
            manifest,
            blueprint_name,
            section,
            step,
            node_results,
            stage_results,
            exc,
            phase=phase,
        )

    return manifest_executor.execute_manifest(
        manifest,
        blueprint_name,
        manifest["temp_package_path"],
        manifest_executor.ManifestExecutorCallbacks(
            execute_step=run_step,
            execute_structural_step=run_structural_step,
            build_failure_diagnostic=build_diagnostic,
        ),
    )


def add_common_blueprint_shell(
    host: str,
    port: int,
    blueprint_name: str,
    temp_package_path: str,
    stage_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    return require_success(
        host,
        port,
        "create_blueprint",
        {"name": blueprint_name, "parent_class": "Actor", "package_path": temp_package_path},
        stage_results,
    )


def author_safe_actor_shell(
    host: str,
    port: int,
    plan: Dict[str, Any],
    blueprint_name: str,
    temp_package_path: str,
    stage_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    add_common_blueprint_shell(host, port, blueprint_name, temp_package_path, stage_results)
    require_success(
        host,
        port,
        "add_component_to_blueprint",
        {
            "blueprint_name": blueprint_name,
            "component_type": "StaticMeshComponent",
            "component_name": "PlannerSmokeMesh",
            "location": [0, 0, 0],
            "rotation": [0, 0, 0],
            "scale": [1, 1, 1],
        },
        stage_results,
    )
    require_success(
        host,
        port,
        "add_blueprint_variable",
        {
            "blueprint_name": blueprint_name,
            "variable_name": "Health",
            "variable_type": "int",
            "default_value": 100,
            "category": "Planner Smoke",
        },
        stage_results,
    )
    event = require_success(
        host,
        port,
        "add_blueprint_event_node",
        {"blueprint_name": blueprint_name, "event_name": "ReceiveBeginPlay", "node_position": [0, 0]},
        stage_results,
    )
    branch = require_success(
        host,
        port,
        "add_blueprint_branch_node",
        {"blueprint_name": blueprint_name, "node_position": [260, 0]},
        stage_results,
    )
    require_success(
        host,
        port,
        "set_blueprint_pin_default",
        {
            "blueprint_name": blueprint_name,
            "node_id": branch["node_id"],
            "pin_name": "Condition",
            "value": True,
            "direction": "input",
        },
        stage_results,
    )
    require_success(
        host,
        port,
        "connect_blueprint_nodes",
        {
            "blueprint_name": blueprint_name,
            "source_node_id": event["node_id"],
            "source_pin": quality_gate.find_exec_pin(event, "output", ("then",)),
            "target_node_id": branch["node_id"],
            "target_pin": quality_gate.find_exec_pin(branch, "input", ("execute", "exec")),
        },
        stage_results,
    )
    nodes = require_success(
        host,
        port,
        "list_blueprint_nodes",
        {"blueprint_name": blueprint_name, "include_pins": True, "graph_type": "event"},
        stage_results,
    )
    validation = require_success(
        host,
        port,
        "compile_and_validate_blueprint",
        {"blueprint_name": blueprint_name, "save": False, "refresh_nodes": True},
        stage_results,
        timeout=120.0,
    )
    return {
        "plan_id": plan["id"],
        "blueprint_name": blueprint_name,
        "node_count": len(nodes.get("nodes", [])),
        "validation": validation,
    }


def author_safe_event_dispatcher(
    host: str,
    port: int,
    plan: Dict[str, Any],
    blueprint_name: str,
    temp_package_path: str,
    stage_results: List[Dict[str, Any]],
) -> Dict[str, Any]:
    add_common_blueprint_shell(host, port, blueprint_name, temp_package_path, stage_results)
    dispatcher = require_success(
        host,
        port,
        "add_blueprint_event_dispatcher",
        {
            "blueprint_name": blueprint_name,
            "dispatcher_name": "OnPlannerSmoke",
            "inputs": [{"name": "Value", "type": "int"}],
            "category": "Planner Smoke",
        },
        stage_results,
    )
    call_node = require_success(
        host,
        port,
        "add_blueprint_event_dispatcher_call_node",
        {
            "blueprint_name": blueprint_name,
            "dispatcher_name": "OnPlannerSmoke",
            "node_position": [640, 0],
            "graph_type": "event",
        },
        stage_results,
    )
    custom_event = require_success(
        host,
        port,
        "add_blueprint_custom_event_node",
        {
            "blueprint_name": blueprint_name,
            "custom_event_name": "HandlePlannerSmoke",
            "signature_source_dispatcher_name": "OnPlannerSmoke",
            "node_position": [640, 280],
            "graph_type": "event",
        },
        stage_results,
    )
    bind_node = require_success(
        host,
        port,
        "add_blueprint_event_dispatcher_bind_node",
        {
            "blueprint_name": blueprint_name,
            "dispatcher_name": "OnPlannerSmoke",
            "node_position": [360, 0],
            "graph_type": "event",
        },
        stage_results,
    )
    assign_node = require_success(
        host,
        port,
        "add_blueprint_event_dispatcher_assign_node",
        {
            "blueprint_name": blueprint_name,
            "dispatcher_name": "OnPlannerSmoke",
            "node_position": [360, 220],
            "graph_type": "event",
        },
        stage_results,
    )
    unbind_node = require_success(
        host,
        port,
        "add_blueprint_event_dispatcher_unbind_node",
        {
            "blueprint_name": blueprint_name,
            "dispatcher_name": "OnPlannerSmoke",
            "node_position": [900, 0],
            "graph_type": "event",
        },
        stage_results,
    )
    clear_node = require_success(
        host,
        port,
        "add_blueprint_event_dispatcher_clear_node",
        {
            "blueprint_name": blueprint_name,
            "dispatcher_name": "OnPlannerSmoke",
            "node_position": [1160, 0],
            "graph_type": "event",
        },
        stage_results,
    )
    if not any(pin.get("name") == "OutputDelegate" and pin.get("direction") == "output" for pin in custom_event.get("pins", [])):
        raise quality_gate.BridgeError(f"Custom event did not expose OutputDelegate: {custom_event}")
    if not any(pin.get("name") == "Delegate" and pin.get("direction") == "input" for pin in bind_node.get("pins", [])):
        raise quality_gate.BridgeError(f"Bind node did not expose Delegate input: {bind_node}")
    if any(pin.get("name") == "Delegate" and pin.get("direction") == "input" for pin in clear_node.get("pins", [])):
        raise quality_gate.BridgeError(f"Clear node unexpectedly exposed Delegate input: {clear_node}")
    require_success(
        host,
        port,
        "connect_blueprint_nodes",
        {
            "blueprint_name": blueprint_name,
            "source_node_id": custom_event["node_id"],
            "source_pin": quality_gate.find_pin(custom_event, "output", ("OutputDelegate",)),
            "target_node_id": bind_node["node_id"],
            "target_pin": quality_gate.find_pin(bind_node, "input", ("Delegate",)),
        },
        stage_results,
    )
    require_success(
        host,
        port,
        "connect_blueprint_nodes",
        {
            "blueprint_name": blueprint_name,
            "source_node_id": custom_event["node_id"],
            "source_pin": quality_gate.find_pin(custom_event, "output", ("OutputDelegate",)),
            "target_node_id": unbind_node["node_id"],
            "target_pin": quality_gate.find_pin(unbind_node, "input", ("Delegate",)),
        },
        stage_results,
    )
    graphs = require_success(
        host,
        port,
        "list_blueprint_graphs",
        {"blueprint_name": blueprint_name, "graph_type": "any"},
        stage_results,
    )
    nodes = require_success(
        host,
        port,
        "list_blueprint_nodes",
        {"blueprint_name": blueprint_name, "include_pins": True, "graph_type": "event"},
        stage_results,
    )
    validation = require_success(
        host,
        port,
        "compile_and_validate_blueprint",
        {"blueprint_name": blueprint_name, "save": False, "refresh_nodes": True},
        stage_results,
        timeout=120.0,
    )
    return {
        "plan_id": plan["id"],
        "blueprint_name": blueprint_name,
        "dispatcher_name": dispatcher.get("dispatcher_name", "OnPlannerSmoke"),
        "signature_graph_count": len([graph for graph in graphs.get("graphs", []) if graph.get("graph_type") == "delegate"]),
        "node_count": len(nodes.get("nodes", [])),
        "call_node": call_node.get("node_id", ""),
        "assign_node": assign_node.get("node_id", ""),
        "clear_node": clear_node.get("node_id", ""),
        "validation": validation,
    }


def run_safe_manifest(
    host: str,
    port: int,
    manifest: Dict[str, Any],
    temp_package_path: str,
    run_id: str,
    keep_assets: bool,
) -> Dict[str, Any]:
    if manifest["status"] != planner.STATUS_SAFE or not manifest["executable"]:
        raise quality_gate.BridgeError(f"Non-executable manifest reached live authoring: {manifest['id']}")
    blueprint_name = blueprint_name_for_manifest(manifest, run_id)
    asset_path = f"{temp_package_path}/{blueprint_name}"
    stage_results: List[Dict[str, Any]] = []
    result: Dict[str, Any] = {
        "plan_id": manifest["id"],
        "manifest_id": manifest["id"],
        "manifest_version": manifest["manifest_version"],
        "executor_version": manifest_executor.EXECUTOR_VERSION,
        "status": "failed",
        "blueprint_name": blueprint_name,
        "asset_path": asset_path,
        "stages": stage_results,
        "cleanup": {},
        "inspection": {},
    }
    try:
        executor_policy = manifest_executor.build_executor_policy(manifest, temp_package_path)
        result["executor_policy"] = executor_policy
        if not executor_policy["can_execute"]:
            raise manifest_executor.ManifestExecutorFailure(
                manifest_executor.build_policy_failure_diagnostic(manifest, executor_policy),
                executor_policy,
            )
        cleanup_generated_asset(host, port, asset_path, stage_results)
        require_success(
            host,
            port,
            "create_blueprint",
            {"name": blueprint_name, "parent_class": manifest["parent_class"], "package_path": temp_package_path},
            stage_results,
        )
        result["execution"] = execute_manifest_sections(host, port, blueprint_name, manifest, stage_results)
        validation = result["execution"].get("validation", {})
        if not validation.get("validation_pass") or validation.get("compile_error_count", 1) != 0:
            raise quality_gate.BridgeError(f"Compile validation failed: {validation}")
        result["diagnostics"] = {
            "manifest_step_count": result["execution"].get("section_results") and len(result["execution"]["section_results"]) or 0,
            "stage_count": len(stage_results),
            "node_count": result["execution"].get("node_count", 0),
            "function_node_count": result["execution"].get("function_node_count", 0),
            "graph_count": result["execution"].get("graph_count", 0),
            "structural_assertion_count": result["execution"].get("structural_assertion_count", 0),
            "layout_assertion_count": result["execution"].get("layout_assertion_count", 0),
            "layout_spacing_assertion_count": result["execution"].get("layout_spacing_assertion_count", 0),
            "failed_structural_assertion_count": result["execution"].get("failed_structural_assertion_count", 0),
            "dataflow_verified": result["execution"].get("dataflow_verified", False),
            "validation_pass": validation.get("validation_pass"),
            "compile_error_count": validation.get("compile_error_count"),
        }
        result["inspection"] = inspect_asset(host, port, asset_path, stage_results)
        if not result["inspection"].get("asset_exists"):
            raise quality_gate.BridgeError(f"Generated asset missing after authoring: {result['inspection']}")
        result["status"] = "passed"
    except (ManifestStepFailure, manifest_executor.ManifestExecutorFailure) as exc:
        result["status"] = "failed"
        result["error"] = str(exc)
        result["failure_diagnostics"] = exc.diagnostic
        if getattr(exc, "policy", None):
            result["executor_policy"] = exc.policy
        if getattr(exc, "partial_result", None):
            result["executor_partial_result"] = exc.partial_result
        result["diagnostics"] = {
            "stage_count": len(stage_results),
            "failed_step_id": exc.diagnostic.get("step_id", ""),
            "failed_section": exc.diagnostic.get("section", ""),
            "failed_phase": exc.diagnostic.get("phase", ""),
        }
    except Exception as exc:
        result["status"] = "failed"
        result["error"] = str(exc)
    finally:
        if not keep_assets:
            try:
                result["cleanup"] = cleanup_generated_asset(host, port, asset_path, stage_results)
            except Exception as cleanup_exc:
                result["cleanup"] = {"error": str(cleanup_exc)}
                result["cleanup_failure_diagnostics"] = manifest_executor.build_cleanup_failure_diagnostic(
                    manifest,
                    blueprint_name,
                    asset_path,
                    result["cleanup"],
                )
            if result["status"] == "passed" and not result["cleanup"].get("deleted"):
                result["status"] = "failed"
                result["error"] = f"Temporary Blueprint cleanup failed: {result['cleanup']}"
                result["cleanup_failure_diagnostics"] = manifest_executor.build_cleanup_failure_diagnostic(
                    manifest,
                    blueprint_name,
                    asset_path,
                    result["cleanup"],
                )
    return result


def run_safe_plan(
    host: str,
    port: int,
    plan: Dict[str, Any],
    temp_package_path: str,
    run_id: str,
    keep_assets: bool,
) -> Dict[str, Any]:
    manifest = job_contract.build_job_manifest(plan["id"], plan["request"], temp_package_path=temp_package_path)
    return run_safe_manifest(host, port, manifest, temp_package_path, run_id, keep_assets)


def run_live_smoke(
    manifests: Sequence[Dict[str, Any]],
    host: str,
    port: int,
    project_root: Optional[Path],
    expected_project_file: str,
    temp_package_path: str,
    keep_assets: bool,
    require_live: bool,
) -> Dict[str, Any]:
    live_result: Dict[str, Any] = {
        "status": "not_requested",
        "host": host,
        "port": port,
        "temp_package_path": temp_package_path,
        "safe_executions": [],
        "durable_preflight_live_results": [],
        "non_safe_authoring_attempted": False,
        "durable_authoring_attempted": False,
        "durable_live_save_or_delete_attempted": False,
        "prevented_requests": [
            {
                "id": manifest["id"],
                "status": manifest["status"],
                "request": manifest["request_original"],
                "authoring_attempted": False,
                "blocked_items": manifest["planner"].get("blocked_items", []),
                "requires_review": manifest["planner"].get("requires_review", []),
                "blocked_review_reasons": manifest.get("blocked_review_reasons", []),
                "durable_preflight_contract": manifest.get("durable_preflight_contract", {}),
                "durable_executor_skeleton_contract": manifest.get("durable_executor_skeleton_contract", {}),
            }
            for manifest in manifests
            if manifest["status"] != planner.STATUS_SAFE or not manifest["executable"]
        ],
        "new_log_errors": [],
    }
    if not bridge_available(host, port):
        live_result["status"] = "failed" if require_live else "skipped"
        live_result["reason"] = f"UnrealMCP bridge not reachable at {host}:{port}"
        live_result["durable_live_preflight_gate"] = manifest_executor.summarize_durable_live_preflight(
            manifests,
            live_result.get("durable_preflight_live_results", []),
            live_requested=True,
        )
        return live_result

    stage_results: List[Dict[str, Any]] = []
    live_result["stages"] = stage_results
    log_snapshot = quality_gate.snapshot_logs(project_root)
    try:
        ping = require_success(host, port, "ping", {}, stage_results, timeout=20.0)
        if ping.get("message") != "pong":
            raise quality_gate.BridgeError(f"Unexpected ping response: {ping}")
        project_identity = execute_python_json(
            host,
            port,
            f"""
import json
import unreal
data = {{
    "project_file": unreal.Paths.get_project_file_path(),
    "project_dir": unreal.Paths.project_dir(),
    "engine_version": unreal.SystemLibrary.get_engine_version(),
}}
print({quality_gate.JSON_LOG_PREFIX!r} + json.dumps(data))
""",
            stage_results,
        )
        live_result["project_identity"] = project_identity
        if expected_project_file and not project_identity.get("project_file", "").replace("\\\\", "/").endswith(
            expected_project_file.replace("\\", "/")
        ):
            raise quality_gate.BridgeError(f"Unexpected project file: {project_identity}")

        before_assets = list_temp_assets(host, port, temp_package_path, stage_results)
        live_result["assets_before"] = before_assets
        run_id = uuid.uuid4().hex[:8]
        prevented_by_id = {item["id"]: item for item in live_result["prevented_requests"]}
        for manifest in manifests:
            if manifest["status"] == planner.STATUS_SAFE and manifest["executable"]:
                continue
            if not manifest.get("durable_preflight_contract", {}).get("requested"):
                continue
            preflight_result = run_durable_preflight_read_only_check(host, port, manifest, stage_results)
            live_result["durable_preflight_live_results"].append(preflight_result)
            prevented_by_id[manifest["id"]]["durable_preflight_live_result"] = preflight_result
            live_result["durable_authoring_attempted"] = bool(
                live_result["durable_authoring_attempted"] or preflight_result.get("authoring_attempted")
            )
            live_result["durable_live_save_or_delete_attempted"] = bool(
                live_result["durable_live_save_or_delete_attempted"] or preflight_result.get("save_or_delete_attempted")
            )
            if preflight_result["status"] != "passed":
                raise quality_gate.BridgeError(f"Durable preflight read-only check failed: {preflight_result}")

        for manifest in manifests:
            if manifest["status"] != planner.STATUS_SAFE or not manifest["executable"]:
                continue
            execution = run_safe_manifest(host, port, manifest, temp_package_path, run_id, keep_assets)
            live_result["safe_executions"].append(execution)
            if execution.get("status") != "passed":
                raise quality_gate.BridgeError(f"Safe manifest live execution failed: {execution}")

        after_assets = list_temp_assets(host, port, temp_package_path, stage_results)
        generated_leftovers = [asset for asset in after_assets if "/MCP_PlannerSmoke_" in asset]
        live_result["assets_after"] = after_assets
        live_result["generated_leftovers"] = generated_leftovers
        if not keep_assets and generated_leftovers:
            raise quality_gate.BridgeError(f"Generated PlannerDrivenSmoke assets were not cleaned: {generated_leftovers}")

        new_errors = quality_gate.collect_new_log_errors(project_root, log_snapshot)
        live_result["new_log_errors"] = new_errors
        if new_errors:
            raise quality_gate.BridgeError(f"New editor log errors appeared: {new_errors[:3]}")
        live_result["status"] = "passed"
    except Exception as exc:
        live_result["status"] = "failed"
        live_result["error"] = str(exc)
        live_result["new_log_errors"] = quality_gate.collect_new_log_errors(project_root, log_snapshot)
    live_result["durable_live_preflight_gate"] = manifest_executor.summarize_durable_live_preflight(
        manifests,
        live_result.get("durable_preflight_live_results", []),
        live_requested=True,
    )
    return live_result


def build_report(
    requests: Sequence[Tuple[str, str]],
    output_dir: Path,
    live_result: Optional[Dict[str, Any]],
    temp_package_path: str = DEFAULT_TEMP_PACKAGE_PATH,
) -> Dict[str, Any]:
    manifests = build_manifests(requests, temp_package_path)
    gate_summary = summarize_planner_gate(manifests)
    executor_summary = manifest_executor.summarize_executor_policies(manifests, temp_package_path)
    live = dict(live_result) if live_result is not None else {"status": "not_requested"}
    if live_result is not None:
        live_prevented_by_id = {item["id"]: item for item in live_result.get("prevented_requests", [])}
        merged_prevented_requests = []
        for item in gate_summary["prevented_requests"]:
            merged_item = dict(item)
            live_item = live_prevented_by_id.get(item["id"], {})
            if "durable_preflight_live_result" in live_item:
                merged_item["durable_preflight_live_result"] = live_item["durable_preflight_live_result"]
            merged_prevented_requests.append(merged_item)
        live["prevented_requests"] = merged_prevented_requests
        live["non_safe_authoring_attempted"] = any(item.get("authoring_attempted") for item in merged_prevented_requests)
        live["durable_authoring_attempted"] = bool(
            live.get("durable_authoring_attempted")
            or any(item.get("authoring_attempted") for item in live.get("durable_preflight_live_results", []))
        )
        live["durable_live_save_or_delete_attempted"] = bool(
            live.get("durable_live_save_or_delete_attempted")
            or any(item.get("save_or_delete_attempted") for item in live.get("durable_preflight_live_results", []))
        )
    live["durable_live_preflight_gate"] = manifest_executor.summarize_durable_live_preflight(
        manifests,
        live.get("durable_preflight_live_results", []),
        live_requested=live_result is not None,
    )
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_kind": "planner_driven_bp_authoring_smoke",
        "output_dir": str(output_dir),
        "temp_package_path": temp_package_path,
        "authoring_job_contract": job_contract.summarize_manifests(manifests),
        "manifest_executor": executor_summary,
        "planner_gate": gate_summary,
        "plans": [manifest["planner"] for manifest in manifests],
        "authoring_manifests": manifests,
        "live_gate": live,
        "verdict": {
            "status": live.get("status", "not_requested"),
            "safe_requests_queued": gate_summary["safe_request_count"],
            "non_safe_requests_prevented": gate_summary["prevented_request_count"],
            "executor_version": executor_summary["executor_version"],
            "executor_executable_manifests": executor_summary["executable_by_executor_count"],
            "cxx_changes_required": False,
            "authoring_policy": "planner_gate_to_job_manifest_before_unrealmcp_asset_authoring",
        },
    }


def format_count_map(data: Dict[str, Any]) -> str:
    if not data:
        return "- none\n"
    return "\n".join(f"- `{key}`: {value}" for key, value in data.items()) + "\n"


def render_markdown(report: Dict[str, Any]) -> str:
    gate_summary = report["planner_gate"]
    live = report["live_gate"]
    lines = [
        "# Planner Driven BP Authoring Smoke",
        "",
        f"- Generated UTC: `{report['generated_at']}`",
        f"- Temp package path: `{report['temp_package_path']}`",
        f"- Live status: `{live.get('status')}`",
        f"- Manifest version: `{report['authoring_manifests'][0]['manifest_version'] if report['authoring_manifests'] else 'none'}`",
        f"- Executor version: `{report['manifest_executor']['executor_version']}`",
        f"- Safe requests queued: `{gate_summary['safe_request_count']}`",
        f"- Non-safe requests prevented: `{gate_summary['prevented_request_count']}`",
        f"- Executor executable manifests: `{report['manifest_executor']['executable_by_executor_count']}`",
        f"- Durable executor gate: `{report['manifest_executor']['durable_gate_summary']['status']}`",
        "",
        "## Planner Gate",
        "",
        "### Authoring Queue",
        "",
    ]
    if gate_summary["authoring_queue"]:
        lines.extend(
            f"- `{item['id']}` `{item['status']}` `{item['blueprint_kind']}` parent=`{item['parent_class']}`: {item['request']}"
            for item in gate_summary["authoring_queue"]
        )
    else:
        lines.append("- none")
    lines.extend(["", "### Prevented Requests", ""])
    if gate_summary["prevented_requests"]:
        for item in gate_summary["prevented_requests"]:
            lines.append(f"- `{item['id']}` `{item['status']}` authoring_attempted=`{item['authoring_attempted']}`: {item['request']}")
    else:
        lines.append("- none")
    lines.extend(["", "## Live Gate", "", f"- Status: `{live.get('status')}`"])
    if live.get("status") != "not_requested":
        lines.append(f"- Non-safe authoring attempted: `{live.get('non_safe_authoring_attempted')}`")
        lines.append(f"- Durable authoring attempted: `{live.get('durable_authoring_attempted')}`")
        lines.append(f"- Durable save/delete attempted: `{live.get('durable_live_save_or_delete_attempted')}`")
    live_preflight_gate = live.get("durable_live_preflight_gate", {})
    if live_preflight_gate:
        lines.append(f"- Durable live preflight gate: `{live_preflight_gate.get('status')}`")
        lines.append(
            f"- Durable live read-only results: `{live_preflight_gate.get('passed_read_only_result_count')}`/"
            f"`{live_preflight_gate.get('read_only_live_preflight_allowed_count')}`"
        )
    if live.get("reason"):
        lines.append(f"- Reason: {live['reason']}")
    if live.get("error"):
        lines.append(f"- Error: {live['error']}")
    durable_preflight_results = live.get("durable_preflight_live_results", [])
    if durable_preflight_results:
        lines.extend(["", "### Durable Preflight Live Results", ""])
        for item in durable_preflight_results:
            lines.append(
                f"- `{item['manifest_id']}` status=`{item['status']}` target=`{item['target_asset_path']}` "
                f"asset_exists=`{item['asset_exists']}` read_only=`{item['read_only']}` "
                f"authoring_attempted=`{item['authoring_attempted']}` "
                f"save_or_delete_attempted=`{item['save_or_delete_attempted']}`"
            )
    if live.get("safe_executions"):
        lines.extend(["", "### Safe Executions", ""])
        for execution in live["safe_executions"]:
            validation = execution.get("execution", {}).get("validation", {})
            diagnostics = execution.get("diagnostics", {})
            failure = execution.get("failure_diagnostics", {})
            lines.append(
                f"- `{execution.get('plan_id')}` `{execution.get('status')}` asset=`{execution.get('asset_path')}` "
                f"compile_errors=`{validation.get('compile_error_count')}` nodes=`{diagnostics.get('node_count')}` "
                f"function_nodes=`{diagnostics.get('function_node_count')}` steps=`{diagnostics.get('manifest_step_count')}` "
                f"structural_assertions=`{diagnostics.get('structural_assertion_count')}` "
                f"layout_assertions=`{diagnostics.get('layout_assertion_count')}` "
                f"layout_spacing_assertions=`{diagnostics.get('layout_spacing_assertion_count')}` "
                f"dataflow_verified=`{diagnostics.get('dataflow_verified')}` "
                f"cleanup_deleted=`{execution.get('cleanup', {}).get('deleted')}`"
            )
            if failure:
                lines.append(
                    f"  - failure phase=`{failure.get('phase')}` section=`{failure.get('section')}` "
                    f"step=`{failure.get('step_id')}` command=`{failure.get('command')}` error=`{failure.get('error')}`"
                )
    if live.get("generated_leftovers") is not None:
        lines.extend(["", "### Generated Leftovers", "", format_count_map({asset: "leftover" for asset in live.get("generated_leftovers", [])})])
    if live.get("new_log_errors"):
        lines.extend(["", "### New Log Errors", ""])
        lines.extend(f"- `{line}`" for line in live["new_log_errors"][:20])
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "Run this smoke before letting automated BP requests call live UnrealMCP authoring. A non-safe planner status or non-executable job manifest must remain a dry-run record and must not create assets.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report(report: Dict[str, Any], output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "planner_driven_bp_authoring_smoke_report.json"
    md_path = output_dir / "planner_driven_bp_authoring_smoke_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_arg_parser() -> argparse.ArgumentParser:
    repo_root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", action="append", default=[], help="Planner request to route. Repeatable.")
    parser.add_argument("--output-dir", default=str(repo_root / "Docs" / "Analysis" / "PlannerDrivenSmoke"))
    parser.add_argument("--run-live", action="store_true", help="Run safe requests against the live UnrealMCP bridge.")
    parser.add_argument("--require-live", action="store_true", help="Fail if --run-live is requested and the bridge is unavailable.")
    parser.add_argument("--host", default=DEFAULT_HOST)
    parser.add_argument("--port", type=int, default=DEFAULT_PORT)
    parser.add_argument("--project-root", default=str(repo_root.parent / "CubelessStylized"))
    parser.add_argument("--expected-project-file", default="StylizedCubeless.uproject")
    parser.add_argument("--temp-package-path", default=DEFAULT_TEMP_PACKAGE_PATH)
    parser.add_argument("--keep-assets", action="store_true")
    parser.add_argument("--no-write", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    requests = request_pairs_from_args(args.request)
    live_result = None
    if args.run_live:
        manifests = build_manifests(requests, args.temp_package_path)
        live_result = run_live_smoke(
            manifests,
            host=args.host,
            port=args.port,
            project_root=Path(args.project_root).resolve() if args.project_root else None,
            expected_project_file=args.expected_project_file,
            temp_package_path=args.temp_package_path,
            keep_assets=args.keep_assets,
            require_live=args.require_live,
        )

    output_dir = Path(args.output_dir).resolve()
    report = build_report(requests, output_dir, live_result, temp_package_path=args.temp_package_path)
    if not args.no_write:
        json_path, md_path = write_report(report, output_dir)
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    print(f"Planner safe requests queued: {report['planner_gate']['safe_request_count']}")
    print(f"Planner non-safe requests prevented: {report['planner_gate']['prevented_request_count']}")
    print(f"Live status: {report['live_gate'].get('status')}")
    return 1 if report["live_gate"].get("status") == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
