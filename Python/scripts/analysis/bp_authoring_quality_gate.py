#!/usr/bin/env python
"""
Blueprint authoring quality gate for existing UnrealMCP capabilities.

This script has two layers:
- offline capability manifest: confirmed MCP commands/functions only
- optional live gate: create and validate a temporary Blueprint through the
  UnrealMCP Editor bridge without changing C++ code
"""

from __future__ import annotations

import argparse
import json
import socket
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import external_project_readiness_analyzer as base


DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 55557
DEFAULT_TEMP_PACKAGE_PATH = "/Game/_MCP_Temp/BPAuthoringQualityGate"
JSON_LOG_PREFIX = "__MCP_BP_QUALITY_GATE_JSON__"


@dataclass(frozen=True)
class GateSpec:
    key: str
    label: str
    required_commands: Tuple[str, ...]
    optional_commands: Tuple[str, ...] = ()
    quality_rule: str = ""


QUALITY_GATES: Tuple[GateSpec, ...] = (
    GateSpec(
        key="asset_creation_temp_path",
        label="Blueprint asset creation under MCP temp path",
        required_commands=("create_blueprint",),
        quality_rule="Generated assets must be under /Game/_MCP_Temp and must be cleanable.",
    ),
    GateSpec(
        key="component_authoring",
        label="Component authoring",
        required_commands=("add_component_to_blueprint", "list_blueprint_components", "get_component_property"),
        optional_commands=("set_component_property", "set_static_mesh_properties"),
        quality_rule="Components must be inspectable and compile after creation.",
    ),
    GateSpec(
        key="variable_authoring",
        label="Member variable authoring",
        required_commands=("add_blueprint_variable",),
        optional_commands=("add_blueprint_variable_get_node", "add_blueprint_variable_set_node"),
        quality_rule="Variables must preserve type/default metadata and be usable by graph nodes.",
    ),
    GateSpec(
        key="event_dispatcher_declaration",
        label="Event Dispatcher declaration",
        required_commands=("add_blueprint_event_dispatcher",),
        quality_rule="Event Dispatchers must create a multicast delegate variable and delegate signature graph that compile cleanly.",
    ),
    GateSpec(
        key="event_dispatcher_call_node",
        label="Event Dispatcher call node",
        required_commands=("add_blueprint_event_dispatcher_call_node",),
        quality_rule="Event Dispatcher call nodes must preserve the dispatcher signature, connect into exec flow, and compile cleanly.",
    ),
    GateSpec(
        key="custom_event_authoring",
        label="Custom event node",
        required_commands=("add_blueprint_custom_event_node",),
        quality_rule="Custom events must support dispatcher-compatible signatures and expose delegate output pins.",
    ),
    GateSpec(
        key="event_dispatcher_bind_node",
        label="Event Dispatcher bind node",
        required_commands=("add_blueprint_event_dispatcher_bind_node",),
        quality_rule="Event Dispatcher bind nodes must accept compatible event delegates and compile cleanly.",
    ),
    GateSpec(
        key="event_dispatcher_unbind_node",
        label="Event Dispatcher unbind node",
        required_commands=("add_blueprint_event_dispatcher_unbind_node",),
        quality_rule="Event Dispatcher unbind nodes must accept compatible event delegates and compile cleanly.",
    ),
    GateSpec(
        key="event_dispatcher_clear_node",
        label="Event Dispatcher clear node",
        required_commands=("add_blueprint_event_dispatcher_clear_node",),
        quality_rule="Event Dispatcher clear nodes must remove all bound events without requiring a delegate pin.",
    ),
    GateSpec(
        key="event_dispatcher_assign_node",
        label="Event Dispatcher assign node",
        required_commands=("add_blueprint_event_dispatcher_assign_node",),
        quality_rule="Event Dispatcher assign nodes must create a signature-compatible event target and compile cleanly.",
    ),
    GateSpec(
        key="function_graph_authoring",
        label="Function graph authoring",
        required_commands=("resolve_blueprint_graph", "add_blueprint_function_parameter"),
        optional_commands=("add_blueprint_local_variable", "add_blueprint_return_node"),
        quality_rule="Function graphs must be resolvable by stable graph id and compile cleanly.",
    ),
    GateSpec(
        key="event_graph_topology",
        label="Event graph topology",
        required_commands=(
            "add_blueprint_event_node",
            "add_blueprint_sequence_node",
            "add_blueprint_branch_node",
            "connect_blueprint_nodes",
            "set_blueprint_pin_default",
        ),
        quality_rule="Exec/data pins must be connected intentionally and inspectable after creation.",
    ),
    GateSpec(
        key="graph_inspection",
        label="Graph inspection",
        required_commands=("list_blueprint_graphs", "list_blueprint_nodes", "resolve_blueprint"),
        quality_rule="Generated graph structure must be re-read after authoring.",
    ),
    GateSpec(
        key="compile_validation",
        label="Compile and validation",
        required_commands=("compile_and_validate_blueprint",),
        optional_commands=("compile_blueprint", "compile_and_save_blueprint"),
        quality_rule="Compile must pass with zero errors before save is treated as valid.",
    ),
    GateSpec(
        key="editor_python_cleanup",
        label="Editor Python cleanup and introspection",
        required_commands=("execute_python",),
        quality_rule="The gate must inspect project identity and clean temporary assets.",
    ),
)


DEFERRED_AUTHORING_GAPS = (
    "generic delegate lifecycle authoring for non-Event-Dispatcher targets",
    "async proxy node callback exec pin authoring",
    "latent continuation topology validation",
    "CommonUI widget tree and activation policy authoring",
    "GAS AbilityTask and prediction-safe authoring",
)


class BridgeError(RuntimeError):
    pass


def collect_tool_names(capabilities: Dict[str, Any]) -> List[str]:
    tool_names = set(capabilities.get("plugin_commands", []))
    for funcs in capabilities.get("python_tools", {}).values():
        tool_names.update(funcs)
    return sorted(tool_names)


def build_capability_manifest(mcp_root: Path, plugin_root: Optional[Path]) -> Dict[str, Any]:
    capabilities = base.scan_mcp_capabilities(mcp_root, plugin_root)
    tool_names = set(collect_tool_names(capabilities))
    gate_results = []

    for gate in QUALITY_GATES:
        missing_required = [name for name in gate.required_commands if name not in tool_names]
        confirmed_optional = [name for name in gate.optional_commands if name in tool_names]
        missing_optional = [name for name in gate.optional_commands if name not in tool_names]
        gate_results.append(
            {
                "key": gate.key,
                "label": gate.label,
                "ready": not missing_required,
                "required_commands": list(gate.required_commands),
                "confirmed_required_commands": [name for name in gate.required_commands if name in tool_names],
                "missing_required_commands": missing_required,
                "confirmed_optional_commands": confirmed_optional,
                "missing_optional_commands": missing_optional,
                "quality_rule": gate.quality_rule,
            }
        )

    return {
        "raw_capabilities": capabilities,
        "confirmed_tool_names": sorted(tool_names),
        "gate_results": gate_results,
        "all_required_ready": all(item["ready"] for item in gate_results),
        "deferred_authoring_gaps": list(DEFERRED_AUTHORING_GAPS),
    }


def send_command(host: str, port: int, command: str, params: Dict[str, Any], timeout: float = 60.0) -> Dict[str, Any]:
    command_obj = {"type": command, "params": params}
    with socket.create_connection((host, port), timeout=10.0) as sock:
        sock.sendall(json.dumps(command_obj).encode("utf-8"))
        sock.settimeout(timeout)

        chunks = []
        while True:
            chunk = sock.recv(4096)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                return json.loads(b"".join(chunks).decode("utf-8"))
            except json.JSONDecodeError:
                continue

    raise BridgeError(f"No JSON response for command: {command}")


def require_success(
    host: str,
    port: int,
    command: str,
    params: Dict[str, Any],
    stage_results: List[Dict[str, Any]],
    timeout: float = 60.0,
) -> Dict[str, Any]:
    response = send_command(host, port, command, params, timeout=timeout)
    stage_results.append({"command": command, "status": response.get("status", "unknown")})
    if response.get("status") != "success":
        raise BridgeError(f"{command} failed: {response}")
    return response.get("result", response)


def find_exec_pin(node: Dict[str, Any], direction: str, preferred_names: Iterable[str] = ()) -> str:
    pins = node.get("pins", [])
    if not pins:
        if direction == "output":
            return next(iter(preferred_names), "then")
        if direction == "input":
            return next(iter(preferred_names), "execute")

    normalized_preferred = {name.lower().replace(" ", "").replace("_", "") for name in preferred_names}
    for pin in pins:
        pin_name = pin.get("name", "")
        normalized_name = pin_name.lower().replace(" ", "").replace("_", "")
        if (
            pin.get("direction") == direction
            and pin.get("category", "").lower() == "exec"
            and normalized_name in normalized_preferred
        ):
            return pin_name

    for pin in pins:
        if pin.get("direction") == direction and pin.get("category", "").lower() == "exec":
            return pin.get("name", "")

    raise BridgeError(f"No {direction} exec pin found on node: {node}")


def find_pin(node: Dict[str, Any], direction: str, preferred_names: Iterable[str] = ()) -> str:
    pins = node.get("pins", [])
    normalized_preferred = {name.lower().replace(" ", "").replace("_", "") for name in preferred_names}
    for pin in pins:
        pin_name = pin.get("name", "")
        normalized_name = pin_name.lower().replace(" ", "").replace("_", "")
        if pin.get("direction") == direction and normalized_name in normalized_preferred:
            return pin_name

    for pin in pins:
        if pin.get("direction") == direction:
            return pin.get("name", "")

    raise BridgeError(f"No {direction} pin found on node: {node}")


def extract_json_from_python_result(result: Dict[str, Any]) -> Dict[str, Any]:
    for log_entry in result.get("logs", []):
        output = log_entry.get("output", "")
        if JSON_LOG_PREFIX not in output:
            continue
        payload = output.split(JSON_LOG_PREFIX, 1)[1].strip()
        return json.loads(payload)
    command_result = result.get("command_result", "")
    if JSON_LOG_PREFIX in command_result:
        return json.loads(command_result.split(JSON_LOG_PREFIX, 1)[1].strip())
    return {}


def execute_python_json(
    host: str,
    port: int,
    code: str,
    stage_results: List[Dict[str, Any]],
    timeout: float = 60.0,
) -> Dict[str, Any]:
    result = require_success(
        host,
        port,
        "execute_python",
        {"code": code, "mode": "ExecuteFile", "defer_to_ticker": False},
        stage_results,
        timeout=timeout,
    )
    if not result.get("success"):
        raise BridgeError(f"execute_python reported failure: {result}")
    return extract_json_from_python_result(result)


def cleanup_temp_asset(host: str, port: int, asset_path: str, stage_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    code = f"""
import json
import unreal
asset_path = {asset_path!r}
deleted = False
if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
    deleted = bool(unreal.EditorAssetLibrary.delete_asset(asset_path))
print({JSON_LOG_PREFIX!r} + json.dumps({{"asset_path": asset_path, "deleted": deleted}}))
"""
    return execute_python_json(host, port, code, stage_results)


def snapshot_logs(project_root: Optional[Path]) -> Dict[str, int]:
    if not project_root:
        return {}
    log_dir = project_root / "Saved" / "Logs"
    if not log_dir.exists():
        return {}
    return {str(path): path.stat().st_size for path in log_dir.glob("*.log") if path.is_file()}


def collect_new_log_errors(project_root: Optional[Path], before: Dict[str, int]) -> List[str]:
    if not project_root:
        return []
    log_dir = project_root / "Saved" / "Logs"
    if not log_dir.exists():
        return []

    errors: List[str] = []
    for path in log_dir.glob("*.log"):
        if not path.is_file():
            continue
        start = before.get(str(path), 0)
        try:
            with path.open("rb") as handle:
                handle.seek(start)
                text = handle.read().decode("utf-8", errors="ignore")
        except OSError:
            continue
        for line in text.splitlines():
            if "Error:" in line or "LogBlueprint: Error" in line:
                errors.append(line.strip())
    return errors[:40]


def run_live_quality_gate(
    host: str,
    port: int,
    project_root: Optional[Path],
    expected_project_file: str,
    temp_package_path: str,
    keep_assets: bool,
) -> Dict[str, Any]:
    run_id = uuid.uuid4().hex[:8]
    blueprint_name = f"MCP_BPQualityGate_{run_id}"
    function_graph_name = f"QualityFunction_{run_id}"
    asset_path = f"{temp_package_path}/{blueprint_name}"
    stage_results: List[Dict[str, Any]] = []
    log_snapshot = snapshot_logs(project_root)

    live_result: Dict[str, Any] = {
        "status": "failed",
        "host": host,
        "port": port,
        "blueprint_name": blueprint_name,
        "asset_path": asset_path,
        "temp_package_path": temp_package_path,
        "stages": stage_results,
        "cleanup": {},
        "inspection": {},
        "validation": {},
        "new_log_errors": [],
    }
    gate_completed = False

    try:
        ping = require_success(host, port, "ping", {}, stage_results, timeout=20.0)
        if ping.get("message") != "pong":
            raise BridgeError(f"Unexpected ping response: {ping}")

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
print({JSON_LOG_PREFIX!r} + json.dumps(data))
""",
            stage_results,
        )
        live_result["project_identity"] = project_identity
        if expected_project_file and not project_identity.get("project_file", "").replace("\\\\", "/").endswith(
            expected_project_file.replace("\\", "/")
        ):
            raise BridgeError(f"Unexpected project file: {project_identity}")

        cleanup_temp_asset(host, port, asset_path, stage_results)

        require_success(
            host,
            port,
            "create_blueprint",
            {"name": blueprint_name, "parent_class": "Actor", "package_path": temp_package_path},
            stage_results,
        )
        require_success(
            host,
            port,
            "add_component_to_blueprint",
            {
                "blueprint_name": blueprint_name,
                "component_type": "StaticMeshComponent",
                "component_name": "QualityMesh",
                "location": [0, 0, 0],
                "rotation": [0, 0, 0],
                "scale": [1, 1, 1],
            },
            stage_results,
        )
        component_listing = require_success(
            host,
            port,
            "list_blueprint_components",
            {"blueprint_name": blueprint_name, "component_name": "QualityMesh"},
            stage_results,
        )
        matching_components = [
            component
            for component in component_listing.get("components", [])
            if component.get("component_name") == "QualityMesh"
        ]
        if not matching_components:
            raise BridgeError(f"QualityMesh component was not listed after creation: {component_listing}")
        require_success(
            host,
            port,
            "add_blueprint_variable",
            {
                "blueprint_name": blueprint_name,
                "variable_name": "QualityScore",
                "variable_type": "int",
                "default_value": 7,
                "category": "MCP Quality Gate",
                "tooltip": "Generated by the BP authoring quality gate",
            },
            stage_results,
        )
        dispatcher = require_success(
            host,
            port,
            "add_blueprint_event_dispatcher",
            {
                "blueprint_name": blueprint_name,
                "dispatcher_name": "OnQualityGateTriggered",
                "inputs": [{"name": "Score", "type": "int"}],
                "category": "MCP Quality Gate",
                "tooltip": "Generated by the BP authoring quality gate",
            },
            stage_results,
        )
        if dispatcher.get("pin_type", {}).get("category") != "mcdelegate":
            raise BridgeError(f"Unexpected Event Dispatcher pin type: {dispatcher}")
        if not dispatcher.get("inputs"):
            raise BridgeError(f"Event Dispatcher signature input was not reported: {dispatcher}")

        graph_result = require_success(
            host,
            port,
            "resolve_blueprint_graph",
            {
                "blueprint_name": blueprint_name,
                "graph_name": function_graph_name,
                "graph_type": "function",
                "create_if_missing": True,
            },
            stage_results,
        )
        function_graph_id = graph_result["graph"]["graph_id"]
        require_success(
            host,
            port,
            "add_blueprint_function_parameter",
            {
                "blueprint_name": blueprint_name,
                "graph_id": function_graph_id,
                "parameter_name": "InputValue",
                "parameter_type": "int",
                "direction": "input",
                "default_value": 3,
            },
            stage_results,
        )
        require_success(
            host,
            port,
            "add_blueprint_function_parameter",
            {
                "blueprint_name": blueprint_name,
                "graph_id": function_graph_id,
                "parameter_name": "ResultValue",
                "parameter_type": "int",
                "direction": "output",
                "default_value": 0,
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
        sequence = require_success(
            host,
            port,
            "add_blueprint_sequence_node",
            {"blueprint_name": blueprint_name, "node_position": [220, 0], "output_count": 2},
            stage_results,
        )
        branch = require_success(
            host,
            port,
            "add_blueprint_branch_node",
            {"blueprint_name": blueprint_name, "node_position": [460, 0]},
            stage_results,
        )
        dispatcher_call = require_success(
            host,
            port,
            "add_blueprint_event_dispatcher_call_node",
            {
                "blueprint_name": blueprint_name,
                "dispatcher_name": "OnQualityGateTriggered",
                "node_position": [920, 160],
                "graph_type": "event",
            },
            stage_results,
        )
        if not any(pin.get("name") == "Score" and pin.get("direction") == "input" for pin in dispatcher_call.get("pins", [])):
            raise BridgeError(f"Event Dispatcher call node did not expose signature input pin: {dispatcher_call}")
        custom_event = require_success(
            host,
            port,
            "add_blueprint_custom_event_node",
            {
                "blueprint_name": blueprint_name,
                "custom_event_name": "HandleQualityGateTriggered",
                "signature_source_dispatcher_name": "OnQualityGateTriggered",
                "node_position": [920, 360],
                "graph_type": "event",
            },
            stage_results,
        )
        if not any(pin.get("name") == "Score" and pin.get("direction") == "output" for pin in custom_event.get("pins", [])):
            raise BridgeError(f"Custom event did not expose dispatcher signature output pin: {custom_event}")
        if not any(
            pin.get("name") == "OutputDelegate" and pin.get("direction") == "output"
            for pin in custom_event.get("pins", [])
        ):
            raise BridgeError(f"Custom event did not expose delegate output pin: {custom_event}")
        dispatcher_bind = require_success(
            host,
            port,
            "add_blueprint_event_dispatcher_bind_node",
            {
                "blueprint_name": blueprint_name,
                "dispatcher_name": "OnQualityGateTriggered",
                "node_position": [700, 0],
                "graph_type": "event",
            },
            stage_results,
        )
        if not any(pin.get("name") == "Delegate" and pin.get("direction") == "input" for pin in dispatcher_bind.get("pins", [])):
            raise BridgeError(f"Event Dispatcher bind node did not expose delegate input pin: {dispatcher_bind}")
        dispatcher_assign = require_success(
            host,
            port,
            "add_blueprint_event_dispatcher_assign_node",
            {
                "blueprint_name": blueprint_name,
                "dispatcher_name": "OnQualityGateTriggered",
                "node_position": [920, -160],
                "graph_type": "event",
            },
            stage_results,
        )
        assign_delegate_pins = [
            pin
            for pin in dispatcher_assign.get("pins", [])
            if pin.get("name") == "Delegate" and pin.get("direction") == "input"
        ]
        if not assign_delegate_pins:
            raise BridgeError(f"Event Dispatcher assign node did not expose delegate input pin: {dispatcher_assign}")
        if not assign_delegate_pins[0].get("linked_to"):
            raise BridgeError(f"Event Dispatcher assign node did not auto-create and wire a custom event: {dispatcher_assign}")
        dispatcher_unbind = require_success(
            host,
            port,
            "add_blueprint_event_dispatcher_unbind_node",
            {
                "blueprint_name": blueprint_name,
                "dispatcher_name": "OnQualityGateTriggered",
                "node_position": [1160, 160],
                "graph_type": "event",
            },
            stage_results,
        )
        if not any(pin.get("name") == "Delegate" and pin.get("direction") == "input" for pin in dispatcher_unbind.get("pins", [])):
            raise BridgeError(f"Event Dispatcher unbind node did not expose delegate input pin: {dispatcher_unbind}")
        dispatcher_clear = require_success(
            host,
            port,
            "add_blueprint_event_dispatcher_clear_node",
            {
                "blueprint_name": blueprint_name,
                "dispatcher_name": "OnQualityGateTriggered",
                "node_position": [1400, 160],
                "graph_type": "event",
            },
            stage_results,
        )
        if any(pin.get("name") == "Delegate" and pin.get("direction") == "input" for pin in dispatcher_clear.get("pins", [])):
            raise BridgeError(f"Event Dispatcher clear node should not expose a delegate input pin: {dispatcher_clear}")
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
            "set_blueprint_pin_default",
            {
                "blueprint_name": blueprint_name,
                "node_id": dispatcher_call["node_id"],
                "pin_name": "Score",
                "value": 42,
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
                "source_pin": find_exec_pin(event, "output", ("then",)),
                "target_node_id": sequence["node_id"],
                "target_pin": find_exec_pin(sequence, "input", ("execute", "exec")),
            },
            stage_results,
        )
        require_success(
            host,
            port,
            "connect_blueprint_nodes",
            {
                "blueprint_name": blueprint_name,
                "source_node_id": sequence["node_id"],
                "source_pin": find_exec_pin(sequence, "output", ("then_1", "then 1")),
                "target_node_id": dispatcher_bind["node_id"],
                "target_pin": find_exec_pin(dispatcher_bind, "input", ("execute", "exec")),
            },
            stage_results,
        )
        require_success(
            host,
            port,
            "connect_blueprint_nodes",
            {
                "blueprint_name": blueprint_name,
                "source_node_id": dispatcher_bind["node_id"],
                "source_pin": find_exec_pin(dispatcher_bind, "output", ("then",)),
                "target_node_id": dispatcher_assign["node_id"],
                "target_pin": find_exec_pin(dispatcher_assign, "input", ("execute", "exec")),
            },
            stage_results,
        )
        require_success(
            host,
            port,
            "connect_blueprint_nodes",
            {
                "blueprint_name": blueprint_name,
                "source_node_id": dispatcher_assign["node_id"],
                "source_pin": find_exec_pin(dispatcher_assign, "output", ("then",)),
                "target_node_id": dispatcher_call["node_id"],
                "target_pin": find_exec_pin(dispatcher_call, "input", ("execute", "exec")),
            },
            stage_results,
        )
        require_success(
            host,
            port,
            "connect_blueprint_nodes",
            {
                "blueprint_name": blueprint_name,
                "source_node_id": dispatcher_call["node_id"],
                "source_pin": find_exec_pin(dispatcher_call, "output", ("then",)),
                "target_node_id": dispatcher_unbind["node_id"],
                "target_pin": find_exec_pin(dispatcher_unbind, "input", ("execute", "exec")),
            },
            stage_results,
        )
        require_success(
            host,
            port,
            "connect_blueprint_nodes",
            {
                "blueprint_name": blueprint_name,
                "source_node_id": dispatcher_unbind["node_id"],
                "source_pin": find_exec_pin(dispatcher_unbind, "output", ("then",)),
                "target_node_id": dispatcher_clear["node_id"],
                "target_pin": find_exec_pin(dispatcher_clear, "input", ("execute", "exec")),
            },
            stage_results,
        )
        require_success(
            host,
            port,
            "connect_blueprint_nodes",
            {
                "blueprint_name": blueprint_name,
                "source_node_id": sequence["node_id"],
                "source_pin": find_exec_pin(sequence, "output", ("then_0", "then 0", "then")),
                "target_node_id": branch["node_id"],
                "target_pin": find_exec_pin(branch, "input", ("execute", "exec")),
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
                "source_pin": find_pin(custom_event, "output", ("OutputDelegate",)),
                "target_node_id": dispatcher_bind["node_id"],
                "target_pin": find_pin(dispatcher_bind, "input", ("Delegate",)),
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
                "source_pin": find_pin(custom_event, "output", ("OutputDelegate",)),
                "target_node_id": dispatcher_unbind["node_id"],
                "target_pin": find_pin(dispatcher_unbind, "input", ("Delegate",)),
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
        delegate_graphs = [
            graph
            for graph in graphs.get("graphs", [])
            if graph.get("graph_type") == "delegate" and graph.get("graph_name") == "OnQualityGateTriggered"
        ]
        if not delegate_graphs:
            raise BridgeError(f"Event Dispatcher delegate signature graph was not found: {graphs}")
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
            {"blueprint_name": blueprint_name, "save": True, "refresh_nodes": True},
            stage_results,
            timeout=120.0,
        )
        live_result["validation"] = validation

        if not validation.get("validation_pass") or validation.get("compile_error_count", 1) != 0:
            raise BridgeError(f"Compile validation failed: {validation}")

        inspection = execute_python_json(
            host,
            port,
            f"""
import json
import unreal
asset_path = {asset_path!r}
asset = unreal.EditorAssetLibrary.load_asset(asset_path)
data = {{
    "asset_exists": unreal.EditorAssetLibrary.does_asset_exist(asset_path),
    "asset_class": asset.get_class().get_name() if asset else "",
    "package_path": asset_path,
}}
print({JSON_LOG_PREFIX!r} + json.dumps(data))
""",
            stage_results,
        )
        live_result["inspection"] = {
            "graphs": graphs.get("graphs", []),
            "node_count": len(nodes.get("nodes", [])),
            "event_dispatcher": {
                "dispatcher_name": dispatcher.get("dispatcher_name", ""),
                "signature_graph": dispatcher.get("signature_graph", {}),
                "inputs": dispatcher.get("inputs", []),
            },
            "event_dispatcher_call": {
                "node_id": dispatcher_call.get("node_id", ""),
                "dispatcher_name": dispatcher_call.get("dispatcher_name", ""),
                "signature_function": dispatcher_call.get("signature_function", ""),
            },
            "custom_event": {
                "node_id": custom_event.get("node_id", ""),
                "custom_event_name": custom_event.get("custom_event_name", ""),
                "signature_source_dispatcher_name": custom_event.get("signature_source_dispatcher_name", ""),
                "signature_function": custom_event.get("signature_function", ""),
            },
            "event_dispatcher_bind": {
                "node_id": dispatcher_bind.get("node_id", ""),
                "dispatcher_name": dispatcher_bind.get("dispatcher_name", ""),
                "signature_function": dispatcher_bind.get("signature_function", ""),
            },
            "event_dispatcher_assign": {
                "node_id": dispatcher_assign.get("node_id", ""),
                "dispatcher_name": dispatcher_assign.get("dispatcher_name", ""),
                "signature_function": dispatcher_assign.get("signature_function", ""),
            },
            "event_dispatcher_unbind": {
                "node_id": dispatcher_unbind.get("node_id", ""),
                "dispatcher_name": dispatcher_unbind.get("dispatcher_name", ""),
                "signature_function": dispatcher_unbind.get("signature_function", ""),
            },
            "event_dispatcher_clear": {
                "node_id": dispatcher_clear.get("node_id", ""),
                "dispatcher_name": dispatcher_clear.get("dispatcher_name", ""),
                "signature_function": dispatcher_clear.get("signature_function", ""),
            },
            "asset": inspection,
        }
        if not inspection.get("asset_exists"):
            raise BridgeError(f"Generated asset was not found after save: {inspection}")

        new_errors = collect_new_log_errors(project_root, log_snapshot)
        live_result["new_log_errors"] = new_errors
        if new_errors:
            raise BridgeError(f"New editor log errors appeared: {new_errors[:3]}")

        live_result["status"] = "passed"
        gate_completed = True
    except Exception as exc:
        live_result["status"] = "failed"
        live_result["error"] = str(exc)
        live_result["new_log_errors"] = collect_new_log_errors(project_root, log_snapshot)
    finally:
        if not keep_assets:
            try:
                live_result["cleanup"] = cleanup_temp_asset(host, port, asset_path, stage_results)
            except Exception as cleanup_exc:
                live_result["cleanup"] = {"error": str(cleanup_exc)}
            if gate_completed and not live_result["cleanup"].get("deleted"):
                live_result["status"] = "failed"
                live_result["error"] = f"Temporary Blueprint cleanup failed: {live_result['cleanup']}"

    return live_result


def build_report(
    mcp_root: Path,
    plugin_root: Optional[Path],
    output_dir: Path,
    live_result: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    manifest = build_capability_manifest(mcp_root, plugin_root)
    live_status = "not_requested" if live_result is None else live_result.get("status", "unknown")
    if live_result and live_result.get("status") == "passed":
        verdict = "existing_bp_authoring_quality_gate_passed"
    elif live_result and live_result.get("status") == "failed":
        verdict = "existing_bp_authoring_quality_gate_failed"
    elif manifest["all_required_ready"]:
        verdict = "capability_manifest_ready_live_gate_not_run"
    else:
        verdict = "capability_manifest_missing_required_commands"

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_kind": "bp_authoring_quality_gate",
        "output_dir": str(output_dir),
        "mcp_root": str(mcp_root),
        "plugin_root": str(plugin_root) if plugin_root else "",
        "capability_manifest": manifest,
        "live_gate": live_result or {"status": live_status},
        "verdict": {
            "status": verdict,
            "cxx_changes_required_for_this_gate": False,
            "lyra_project_used": False,
            "temp_package_root": DEFAULT_TEMP_PACKAGE_PATH,
        },
    }


def format_list(items: Sequence[str]) -> str:
    if not items:
        return "- none\n"
    return "\n".join(f"- `{item}`" for item in items) + "\n"


def render_markdown(report: Dict[str, Any]) -> str:
    manifest = report["capability_manifest"]
    live = report["live_gate"]
    lines = [
        "# BP Authoring Quality Gate",
        "",
        f"- Generated UTC: `{report['generated_at']}`",
        f"- Verdict: `{report['verdict']['status']}`",
        f"- C++ changes required for this gate: `{report['verdict']['cxx_changes_required_for_this_gate']}`",
        f"- Temp package root: `{report['verdict']['temp_package_root']}`",
        "",
        "## Capability Gate Results",
        "",
        "| Gate | Ready | Missing Required | Confirmed Optional |",
        "| --- | --- | --- | --- |",
    ]
    for item in manifest["gate_results"]:
        missing = ", ".join(f"`{name}`" for name in item["missing_required_commands"]) or "none"
        optional = ", ".join(f"`{name}`" for name in item["confirmed_optional_commands"]) or "none"
        lines.append(f"| {item['label']} | `{item['ready']}` | {missing} | {optional} |")

    lines.extend(["", "## Deferred Authoring Gaps", "", format_list(manifest["deferred_authoring_gaps"])])
    lines.extend(["## Live Gate", "", f"- Status: `{live.get('status')}`"])
    if live.get("error"):
        lines.append(f"- Error: {live['error']}")
    if live.get("blueprint_name"):
        lines.append(f"- Blueprint: `{live['blueprint_name']}`")
    if live.get("asset_path"):
        lines.append(f"- Asset path: `{live['asset_path']}`")
    validation = live.get("validation") or {}
    if validation:
        lines.append(f"- Compile validation pass: `{validation.get('validation_pass')}`")
        lines.append(f"- Compile errors: `{validation.get('compile_error_count')}`")
    if live.get("inspection"):
        lines.append(f"- Inspected node count: `{live['inspection'].get('node_count', 0)}`")
    if live.get("new_log_errors"):
        lines.extend(["", "### New Log Errors", ""])
        lines.extend(f"- `{line}`" for line in live["new_log_errors"][:20])

    lines.extend(
        [
            "",
            "## Decision",
            "",
            "Use this gate before adding new UnrealMCP C++ Blueprint primitives. A new C++ primitive should add or update a live quality gate assertion, not just expose a command.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report(report: Dict[str, Any], output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "bp_authoring_quality_gate_report.json"
    md_path = output_dir / "bp_authoring_quality_gate_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_arg_parser() -> argparse.ArgumentParser:
    repo_root = base.repo_root_from_script()
    output_dir = repo_root / "Docs" / "Analysis" / "BPAuthoringQualityGate"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mcp-root", default=str(repo_root))
    parser.add_argument("--plugin-root", default=str(repo_root.parent / "CubelessStylized" / "Plugins" / "UnrealMCP"))
    parser.add_argument("--output-dir", default=str(output_dir))
    parser.add_argument("--run-live", action="store_true", help="Run the live Unreal Editor bridge quality gate.")
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
    mcp_root = Path(args.mcp_root).resolve()
    plugin_root = Path(args.plugin_root).resolve() if args.plugin_root else None
    output_dir = Path(args.output_dir).resolve()

    live_result = None
    if args.run_live:
        project_root = Path(args.project_root).resolve() if args.project_root else None
        live_result = run_live_quality_gate(
            host=args.host,
            port=args.port,
            project_root=project_root,
            expected_project_file=args.expected_project_file,
            temp_package_path=args.temp_package_path,
            keep_assets=args.keep_assets,
        )

    report = build_report(mcp_root, plugin_root, output_dir, live_result)
    if not args.no_write:
        json_path, md_path = write_report(report, output_dir)
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")

    print(f"Verdict: {report['verdict']['status']}")
    print(f"Required capability gates ready: {report['capability_manifest']['all_required_ready']}")
    print(f"Live gate status: {report['live_gate']['status']}")
    return 1 if report["live_gate"].get("status") == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
