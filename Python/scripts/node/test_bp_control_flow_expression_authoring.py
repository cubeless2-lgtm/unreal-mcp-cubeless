#!/usr/bin/env python
"""
Smoke test for Blueprint control-flow and expression authoring MCP commands.

This creates a generic Blueprint, adds pure expression nodes to a function graph,
connects a comparison result into a Branch condition, and validates the Blueprint
compile result.
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
BLUEPRINT_NAME = f"MCP_BPExpressionAuthoringSmoke_{RUN_ID}"
FUNCTION_GRAPH_NAME = f"ExpressionFunctionSmoke_{RUN_ID}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestBPControlFlowExpressionAuthoring")


def send_command(command: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    command_obj = {"type": command, "params": params}
    command_json = json.dumps(command_obj)
    logger.info("Sending command: %s", command_json)

    with socket.create_connection((HOST, PORT), timeout=10.0) as sock:
        sock.sendall(command_json.encode("utf-8"))
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


def require_success(command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    response = send_command(command, params)
    if not response or response.get("status") != "success":
        raise RuntimeError(f"{command} failed: {response}")
    return response.get("result", response)


def require_error(command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    response = send_command(command, params)
    if not response or response.get("status") != "error":
        raise RuntimeError(f"{command} should have failed but returned: {response}")
    return response


def normalize_name(value: str) -> str:
    return value.lower().replace(" ", "").replace("_", "")


def find_pin(
    node: Dict[str, Any],
    direction: str,
    category: str = "",
    preferred_names: Iterable[str] = (),
) -> str:
    pins = node.get("pins", [])
    normalized_preferred = {normalize_name(name) for name in preferred_names}

    for pin in pins:
        pin_name = pin.get("name", "")
        if (
            pin.get("direction") == direction
            and (not category or pin.get("category", "").lower() == category.lower())
            and normalize_name(pin_name) in normalized_preferred
        ):
            return pin_name

    for pin in pins:
        if pin.get("direction") == direction and (not category or pin.get("category", "").lower() == category.lower()):
            return pin.get("name", "")

    raise RuntimeError(f"No {direction} {category or 'any'} pin found on node: {node}")


def find_exec_pin(node: Dict[str, Any], direction: str, preferred_names: Iterable[str] = ()) -> str:
    return find_pin(node, direction, "exec", preferred_names)


def set_pin_default(blueprint_name: str, graph_id: str, node: Dict[str, Any], pin_name: str, value: Any) -> Dict[str, Any]:
    return require_success(
        "set_blueprint_pin_default",
        {
            "blueprint_name": blueprint_name,
            "graph_id": graph_id,
            "node_id": node["node_id"],
            "pin_name": pin_name,
            "direction": "input",
            "value": value,
        },
    )


def create_temp_blueprint(blueprint_name: str) -> None:
    response = send_command(
        "create_blueprint",
        {
            "name": blueprint_name,
            "parent_class": "Actor",
            "package_path": TEMP_PACKAGE_PATH,
        },
    )
    if response and response.get("status") != "success":
        logger.warning("Create returned non-success; continuing in case the Blueprint already exists: %s", response)


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
        )
        if not response or response.get("status") != "success":
            logger.warning("Cleanup returned non-success: %s", response)
    except Exception as exc:
        logger.warning("Cleanup failed: %s", exc)


def validate_successful_authoring_path() -> Dict[str, Any]:
    create_temp_blueprint(BLUEPRINT_NAME)

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

    sequence = require_success(
        "add_blueprint_sequence_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "node_position": [0, 0],
        },
    )
    branch = require_success(
        "add_blueprint_branch_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "node_position": [280, 0],
        },
    )
    ret = require_success(
        "add_blueprint_return_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "node_position": [560, 0],
        },
    )
    compare = require_success(
        "add_blueprint_compare_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "operation": ">",
            "value_type": "int",
            "node_position": [80, 220],
        },
    )
    literal = require_success(
        "add_blueprint_literal_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "literal_type": "int",
            "value": 7,
            "node_position": [-160, 220],
        },
    )
    boolean = require_success(
        "add_blueprint_boolean_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "operation": "and",
            "node_position": [80, 420],
        },
    )
    select = require_success(
        "add_blueprint_select_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "value_type": "int",
            "node_position": [360, 260],
        },
    )
    is_valid = require_success(
        "add_blueprint_is_valid_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "value_type": "object",
            "node_position": [360, 460],
        },
    )

    set_pin_default(BLUEPRINT_NAME, graph_id, compare, find_pin(compare, "input", "int", ("B",)), 3)
    set_pin_default(BLUEPRINT_NAME, graph_id, boolean, find_pin(boolean, "input", "bool", ("A",)), True)
    set_pin_default(BLUEPRINT_NAME, graph_id, boolean, find_pin(boolean, "input", "bool", ("B",)), False)
    set_pin_default(BLUEPRINT_NAME, graph_id, select, find_pin(select, "input", "int", ("A",)), 10)
    set_pin_default(BLUEPRINT_NAME, graph_id, select, find_pin(select, "input", "int", ("B",)), 20)
    set_pin_default(BLUEPRINT_NAME, graph_id, select, find_pin(select, "input", "bool", ("bPickA", "bSelectA")), True)

    require_success(
        "connect_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "source_node_id": sequence["node_id"],
            "source_pin": find_exec_pin(sequence, "output", ("then_0", "then 0", "then")),
            "target_node_id": branch["node_id"],
            "target_pin": find_exec_pin(branch, "input", ("execute", "exec")),
        },
    )
    require_success(
        "connect_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "source_node_id": branch["node_id"],
            "source_pin": find_exec_pin(branch, "output", ("then", "true")),
            "target_node_id": ret["node_id"],
            "target_pin": find_exec_pin(ret, "input", ("execute", "exec")),
            "allow_pin_link_replacement": True,
        },
    )
    require_success(
        "connect_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "source_node_id": literal["node_id"],
            "source_pin": find_pin(literal, "output", "int", ("ReturnValue",)),
            "target_node_id": compare["node_id"],
            "target_pin": find_pin(compare, "input", "int", ("A",)),
        },
    )
    require_success(
        "connect_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "source_node_id": compare["node_id"],
            "source_pin": find_pin(compare, "output", "bool", ("ReturnValue",)),
            "target_node_id": branch["node_id"],
            "target_pin": find_pin(branch, "input", "bool", ("Condition",)),
        },
    )

    if not find_pin(select, "output", "int", ("ReturnValue",)):
        raise RuntimeError(f"Select node did not expose an int return pin: {select}")
    if not find_pin(is_valid, "output", "bool", ("ReturnValue",)):
        raise RuntimeError(f"IsValid node did not expose a bool return pin: {is_valid}")

    validation = require_success(
        "compile_and_validate_blueprint",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "save": False,
            "refresh_nodes": True,
        },
    )
    if not validation.get("validation_pass") or validation.get("compile_error_count", 1) != 0:
        raise RuntimeError(f"Blueprint validation failed: {validation}")

    return validation


def validate_error_paths() -> None:
    base_params = {
        "blueprint_name": BLUEPRINT_NAME,
        "graph_name": FUNCTION_GRAPH_NAME,
        "graph_type": "function",
    }
    require_error("add_blueprint_compare_node", {**base_params, "operation": "approximately", "value_type": "double"})
    require_error("add_blueprint_compare_node", {**base_params, "operation": "<", "value_type": "string"})
    require_error("add_blueprint_boolean_node", {**base_params, "operation": "maybe"})
    require_error("add_blueprint_select_node", {**base_params, "value_type": "byte"})
    require_error("add_blueprint_literal_node", {**base_params, "literal_type": "enum", "value": "Missing"})
    require_error("add_blueprint_is_valid_node", {**base_params, "value_type": "int"})


def main() -> None:
    cleanup_temp_assets([BLUEPRINT_NAME])
    try:
        validation = validate_successful_authoring_path()
        validate_error_paths()
        logger.info("Expression authoring validation passed: %s", validation)
    finally:
        cleanup_temp_assets([BLUEPRINT_NAME])


if __name__ == "__main__":
    main()
