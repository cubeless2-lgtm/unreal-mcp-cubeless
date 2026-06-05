#!/usr/bin/env python
"""
Smoke test for Blueprint data and function authoring MCP commands.

This creates a generic Blueprint, authors member variables, function
parameters, and local variables, then validates the Blueprint compile result.
"""

import json
import logging
import socket
import uuid
from typing import Any, Dict, Iterable, Optional


HOST = "127.0.0.1"
PORT = 55557
RUN_ID = uuid.uuid4().hex[:8]
TEMP_PACKAGE_PATH = "/Game/_MCP_Temp"
BLUEPRINT_NAME = f"MCP_BPDataFunctionSmoke_{RUN_ID}"
FUNCTION_GRAPH_NAME = f"DataFunctionSmoke_{RUN_ID}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestBPDataFunctionAuthoring")


def send_command(command: str, params: Dict[str, Any], timeout: float = 60.0) -> Optional[Dict[str, Any]]:
    command_obj = {"type": command, "params": params}
    command_json = json.dumps(command_obj)
    logger.info("Sending command: %s", command_json)

    with socket.create_connection((HOST, PORT), timeout=10.0) as sock:
        sock.sendall(command_json.encode("utf-8"))
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

    if not chunks:
        return None
    return json.loads(b"".join(chunks).decode("utf-8"))


def require_success(command: str, params: Dict[str, Any], timeout: float = 60.0) -> Dict[str, Any]:
    response = send_command(command, params, timeout=timeout)
    if not response or response.get("status") != "success":
        raise RuntimeError(f"{command} failed: {response}")
    return response.get("result", response)


def require_error(command: str, params: Dict[str, Any], timeout: float = 60.0) -> Dict[str, Any]:
    response = send_command(command, params, timeout=timeout)
    if not response or response.get("status") != "error":
        raise RuntimeError(f"{command} should have failed but returned: {response}")
    return response


def create_temp_blueprint() -> None:
    create_response = send_command(
        "create_blueprint",
        {
            "name": BLUEPRINT_NAME,
            "parent_class": "Actor",
            "package_path": TEMP_PACKAGE_PATH,
        },
    )
    if create_response and create_response.get("status") != "success":
        logger.warning("Create returned non-success; continuing in case the Blueprint already exists: %s", create_response)


def cleanup_temp_assets(asset_names: Iterable[str]) -> None:
    quoted_paths = ", ".join(repr(f"{TEMP_PACKAGE_PATH}/{asset_name}") for asset_name in asset_names)
    cleanup_code = f"""
for asset_path in [{quoted_paths}]:
    if unreal.EditorAssetLibrary.does_asset_exist(asset_path):
        unreal.EditorAssetLibrary.delete_asset(asset_path)
"""
    try:
        response = send_command(
            "execute_python",
            {
                "code": f"exec({cleanup_code!r})",
                "mode": "execute",
                "defer_to_ticker": False,
            },
            timeout=60.0,
        )
        if not response or response.get("status") != "success":
            logger.warning("Cleanup returned non-success: %s", response)
    except Exception as exc:
        logger.warning("Cleanup failed: %s", exc)


def require_pin(nodes: Dict[str, Any], node_class: str, pin_name: str, direction: str) -> None:
    for node in nodes.get("nodes", []):
        if node.get("class") != node_class:
            continue
        for pin in node.get("pins", []):
            if pin.get("name") == pin_name and pin.get("direction") == direction:
                return
    raise RuntimeError(f"Missing {direction} pin '{pin_name}' on {node_class}: {nodes}")


def validate_successful_data_authoring_path() -> Dict[str, Any]:
    create_temp_blueprint()

    graph_result = require_success(
        "resolve_blueprint_graph",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_name": FUNCTION_GRAPH_NAME,
            "graph_type": "function",
            "create_if_missing": True,
        },
    )
    graph_id = graph_result["graph"]["graph_id"]

    count_var = require_success(
        "add_blueprint_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "variable_name": "StoredCount",
            "variable_type": "int",
            "default_value": 7,
            "category": "MCP Smoke",
            "tooltip": "Count authored by MCP smoke",
            "metadata": {"ClampMin": 0},
        },
    )
    if count_var.get("default_value") != "7":
        raise RuntimeError(f"Unexpected int variable default: {count_var}")

    vector_var = require_success(
        "add_blueprint_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "variable_name": "StoredVector",
            "variable_type": "vector",
            "default_value": [1, 2, 3],
        },
    )
    if "X=1" not in vector_var.get("default_value", ""):
        raise RuntimeError(f"Unexpected vector variable default: {vector_var}")

    float_var = require_success(
        "add_blueprint_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "variable_name": "StoredFloat",
            "variable_type": "float",
            "default_value": 1.25,
        },
    )
    if float_var.get("pin_type", {}).get("category") != "real" or float_var.get("pin_type", {}).get("subcategory") != "float":
        raise RuntimeError(f"Float variable did not use UE real/float pin type: {float_var}")

    double_var = require_success(
        "add_blueprint_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "variable_name": "StoredDouble",
            "variable_type": "double",
            "default_value": 2.5,
        },
    )
    if double_var.get("pin_type", {}).get("category") != "real" or double_var.get("pin_type", {}).get("subcategory") != "double":
        raise RuntimeError(f"Double variable did not use UE real/double pin type: {double_var}")

    array_var = require_success(
        "add_blueprint_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "variable_name": "StoredCounts",
            "variable_type": "int",
            "is_array": True,
        },
    )
    if not array_var.get("pin_type", {}).get("is_array"):
        raise RuntimeError(f"Array variable was not authored as an array: {array_var}")

    input_param = require_success(
        "add_blueprint_function_parameter",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "parameter_name": "InputCount",
            "parameter_type": "int",
            "direction": "input",
            "default_value": 5,
        },
    )
    if input_param.get("default_value") != "5":
        raise RuntimeError(f"Unexpected function input default: {input_param}")

    require_success(
        "add_blueprint_function_parameter",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "parameter_name": "InputVector",
            "parameter_type": "vector",
            "direction": "input",
            "default_value": {"x": 1, "y": 2, "z": 3},
        },
    )
    require_success(
        "add_blueprint_function_parameter",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "parameter_name": "ResultCount",
            "parameter_type": "int",
            "direction": "output",
            "default_value": 0,
        },
    )

    local_var = require_success(
        "add_blueprint_local_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "variable_name": "AccumulatedCount",
            "variable_type": "int",
            "default_value": 0,
            "category": "MCP Smoke",
            "tooltip": "Local count authored by MCP smoke",
        },
    )
    if local_var.get("default_value") != "0":
        raise RuntimeError(f"Unexpected local variable default: {local_var}")

    transform_local = require_success(
        "add_blueprint_local_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "variable_name": "LocalTransform",
            "variable_type": "transform",
            "default_value": {"translation": {"x": 4, "y": 5, "z": 6}},
        },
    )
    if "Scale3D=(X=1" not in transform_local.get("default_value", ""):
        raise RuntimeError(f"Transform default fallback was not applied: {transform_local}")

    local_get = require_success(
        "add_blueprint_variable_get_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "variable_name": "AccumulatedCount",
            "node_position": [120, 180],
        },
    )
    local_set = require_success(
        "add_blueprint_variable_set_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "variable_name": "AccumulatedCount",
            "node_position": [120, 0],
        },
    )
    require_error(
        "set_blueprint_pin_default",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "node_id": local_set["node_id"],
            "pin_name": "AccumulatedCount",
            "direction": "input",
            "value": "not_an_int",
        },
    )
    require_success(
        "set_blueprint_pin_default",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "node_id": local_set["node_id"],
            "pin_name": "AccumulatedCount",
            "direction": "input",
            "value": 11,
        },
    )

    require_success(
        "add_blueprint_return_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "node_position": [320, 0],
        },
    )

    nodes = require_success(
        "list_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "include_pins": True,
        },
    )
    require_pin(nodes, "K2Node_FunctionEntry", "InputCount", "output")
    require_pin(nodes, "K2Node_FunctionEntry", "InputVector", "output")
    require_pin(nodes, "K2Node_FunctionResult", "ResultCount", "input")
    require_pin({"nodes": [local_get]}, "K2Node_VariableGet", "AccumulatedCount", "output")
    require_pin({"nodes": [local_set]}, "K2Node_VariableSet", "AccumulatedCount", "input")
    require_pin({"nodes": [local_set]}, "K2Node_VariableSet", "Output_Get", "output")

    validation = require_success(
        "compile_and_validate_blueprint",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "save": False,
            "refresh_nodes": True,
        },
        timeout=90.0,
    )
    if not validation.get("validation_pass") or validation.get("compile_error_count", 1) != 0:
        raise RuntimeError(f"Blueprint validation failed: {validation}")

    require_error(
        "add_blueprint_function_parameter",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "parameter_name": "InputCount",
            "parameter_type": "int",
            "direction": "input",
        },
    )
    require_error(
        "add_blueprint_function_parameter",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "parameter_name": "BadDirection",
            "parameter_type": "int",
            "direction": "sideways",
        },
    )
    require_error(
        "add_blueprint_local_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "variable_name": "AccumulatedCount",
            "variable_type": "int",
        },
    )
    require_error(
        "add_blueprint_local_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "variable_name": "EventGraphLocal",
            "variable_type": "int",
        },
    )
    require_error(
        "add_blueprint_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "variable_name": "UnsupportedMember",
            "variable_type": "unsupported_descriptor",
        },
    )

    return validation


def main() -> None:
    try:
        validation = validate_successful_data_authoring_path()
        logger.info("Blueprint data/function authoring validation passed: %s", validation)
    finally:
        cleanup_temp_assets([BLUEPRINT_NAME])


if __name__ == "__main__":
    main()
