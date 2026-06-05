#!/usr/bin/env python
"""
Smoke test for Blueprint loop and collection authoring MCP commands.

This creates a generic Blueprint function graph, authors a standard ForLoop
macro plus typed int array function nodes, connects the array target pins, and
validates the Blueprint compile result.
"""

import json
import logging
import socket
import uuid
from typing import Any, Dict, Iterable, List, Optional


HOST = "127.0.0.1"
PORT = 55557
RUN_ID = uuid.uuid4().hex[:8]
TEMP_PACKAGE_PATH = "/Game/_MCP_Temp"
BLUEPRINT_NAME = f"MCP_BPLoopCollectionSmoke_{RUN_ID}"
FUNCTION_GRAPH_NAME = f"LoopCollectionSmoke_{RUN_ID}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestBPLoopCollectionAuthoring")


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
    return value.lower().replace(" ", "").replace("_", "").replace("[", "").replace("]", "")


def pins_matching(node: Dict[str, Any], direction: str, category: str = "") -> List[Dict[str, Any]]:
    return [
        pin
        for pin in node.get("pins", [])
        if pin.get("direction") == direction
        and (not category or pin.get("category", "").lower() == category.lower())
    ]


def find_pin(
    node: Dict[str, Any],
    direction: str,
    category: str = "",
    preferred_names: Iterable[str] = (),
    require_array: Optional[bool] = None,
) -> str:
    pins = pins_matching(node, direction, category)
    normalized_preferred = {normalize_name(name) for name in preferred_names}

    for pin in pins:
        if require_array is not None and bool(pin.get("is_array")) != require_array:
            continue
        if normalize_name(pin.get("name", "")) in normalized_preferred:
            return pin.get("name", "")

    for pin in pins:
        if require_array is None or bool(pin.get("is_array")) == require_array:
            return pin.get("name", "")

    raise RuntimeError(f"No {direction} {category or 'any'} pin found on node: {node}")


def find_exec_pin(node: Dict[str, Any], direction: str, preferred_names: Iterable[str] = ()) -> str:
    return find_pin(node, direction, "exec", preferred_names)


def has_node_title(nodes: Dict[str, Any], title_fragment: str) -> bool:
    wanted = normalize_name(title_fragment)
    return any(wanted in normalize_name(node.get("title", "")) for node in nodes.get("nodes", []))


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


def connect(
    graph_id: str,
    source: Dict[str, Any],
    source_pin: str,
    target: Dict[str, Any],
    target_pin: str,
    allow_replacement: bool = False,
) -> Dict[str, Any]:
    return require_success(
        "connect_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "source_node_id": source["node_id"],
            "source_pin": source_pin,
            "target_node_id": target["node_id"],
            "target_pin": target_pin,
            "allow_pin_link_replacement": allow_replacement,
        },
    )


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

    array_var = require_success(
        "add_blueprint_local_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "variable_name": "LoopValues",
            "variable_type": "int",
            "is_array": True,
        },
    )
    if not array_var.get("pin_type", {}).get("is_array"):
        raise RuntimeError(f"Local array variable was not authored as an array: {array_var}")

    sequence = require_success(
        "add_blueprint_sequence_node",
        {"blueprint_name": BLUEPRINT_NAME, "graph_id": graph_id, "node_position": [0, 0]},
    )
    loop = require_success(
        "add_blueprint_loop_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "loop_type": "for_loop",
            "first_index": 0,
            "last_index": 2,
            "node_position": [260, 0],
        },
    )
    if loop.get("macro_name") != "ForLoop":
        raise RuntimeError(f"Unexpected loop macro: {loop}")
    if loop.get("pin_defaults_applied", {}).get("FirstIndex") != "0":
        raise RuntimeError(f"Loop FirstIndex default was not applied: {loop}")

    ret = require_success(
        "add_blueprint_return_node",
        {"blueprint_name": BLUEPRINT_NAME, "graph_id": graph_id, "node_position": [980, 0]},
    )
    array_get_var = require_success(
        "add_blueprint_variable_get_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "variable_name": "LoopValues",
            "node_position": [60, 280],
        },
    )
    target_array_pin = find_pin(array_get_var, "output", "", ("LoopValues",), require_array=True)

    length_node = require_success(
        "add_blueprint_array_function_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "operation": "length",
            "element_type": "int",
            "node_position": [340, 280],
        },
    )
    get_node = require_success(
        "add_blueprint_array_function_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "operation": "get",
            "element_type": "int",
            "param_defaults": {"Index": 0},
            "node_position": [340, 460],
        },
    )
    add_node = require_success(
        "add_blueprint_array_function_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "operation": "add",
            "element_type": "int",
            "param_defaults": {"NewItem": 4},
            "node_position": [560, 20],
        },
    )
    set_node = require_success(
        "add_blueprint_array_function_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "operation": "set",
            "element_type": "int",
            "param_defaults": {"Index": 0, "Item": 9, "bSizeToFit": True},
            "node_position": [760, 20],
        },
    )

    if length_node.get("element_pin_type", {}).get("category") != "int":
        raise RuntimeError(f"Length node element type was not reported as int: {length_node}")
    if add_node.get("param_defaults_applied", {}).get("NewItem") != "4":
        raise RuntimeError(f"Array add default was not applied: {add_node}")
    if set_node.get("param_defaults_applied", {}).get("bSizeToFit") != "true":
        raise RuntimeError(f"Array set bool default was not applied: {set_node}")

    connect(graph_id, sequence, find_exec_pin(sequence, "output", ("then_0", "then 0", "then")), loop, find_exec_pin(loop, "input", ("execute", "exec")))
    connect(graph_id, loop, find_exec_pin(loop, "output", ("LoopBody",)), add_node, find_exec_pin(add_node, "input", ("execute", "exec")))
    connect(graph_id, add_node, find_exec_pin(add_node, "output", ("then",)), set_node, find_exec_pin(set_node, "input", ("execute", "exec")))
    connect(graph_id, loop, find_exec_pin(loop, "output", ("Completed",)), ret, find_exec_pin(ret, "input", ("execute", "exec")))

    for array_function in (length_node, get_node, add_node, set_node):
        connect(
            graph_id,
            array_get_var,
            target_array_pin,
            array_function,
            find_pin(array_function, "input", "", ("TargetArray",), require_array=True),
            allow_replacement=True,
        )

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
    require_error("add_blueprint_loop_node", {**base_params, "loop_type": "while_loop"})
    require_error("add_blueprint_loop_node", {**base_params, "loop_type": "for_loop", "first_index": "not_an_int"})
    require_error("add_blueprint_array_function_node", {**base_params, "operation": "reverse", "element_type": "int"})
    require_error(
        "add_blueprint_array_function_node",
        {**base_params, "operation": "add", "element_type": "int", "param_defaults": {"TargetArray": []}},
    )
    require_error(
        "add_blueprint_call_function_node",
        {**base_params, "function_class": "/Script/Engine.KismetArrayLibrary", "function_name": "Array_Add"},
    )

    nodes_after_failures = require_success(
        "list_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_name": FUNCTION_GRAPH_NAME,
            "graph_type": "function",
            "include_pins": True,
        },
    )
    if has_node_title(nodes_after_failures, "While"):
        raise RuntimeError(f"Unsupported loop left a node behind: {nodes_after_failures}")


def main() -> None:
    cleanup_temp_assets([BLUEPRINT_NAME])
    try:
        validation = validate_successful_authoring_path()
        validate_error_paths()
        logger.info("Loop and collection authoring validation passed: %s", validation)
    finally:
        cleanup_temp_assets([BLUEPRINT_NAME])


if __name__ == "__main__":
    main()
