#!/usr/bin/env python
"""
Smoke test for Blueprint collection literal authoring MCP commands.

This creates typed Make Array nodes, connects an int array literal to typed
array read operations, and validates the Blueprint compile result.
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
BLUEPRINT_NAME = f"MCP_BPCollectionLiteralSmoke_{RUN_ID}"
FUNCTION_GRAPH_NAME = f"CollectionLiteralSmoke_{RUN_ID}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestBPCollectionLiteralAuthoring")


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


def normalize_name(value: str) -> str:
    return value.lower().replace(" ", "").replace("_", "").replace("[", "").replace("]", "")


def create_temp_blueprint() -> None:
    response = send_command(
        "create_blueprint",
        {
            "name": BLUEPRINT_NAME,
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
            timeout=60.0,
        )
        if not response or response.get("status") != "success":
            logger.warning("Cleanup returned non-success: %s", response)
    except Exception as exc:
        logger.warning("Cleanup failed: %s", exc)


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


def input_value_pins(node: Dict[str, Any]) -> List[Dict[str, Any]]:
    return [
        pin
        for pin in node.get("pins", [])
        if pin.get("direction") == "input" and pin.get("category", "").lower() != "exec"
    ]


def has_node_title(nodes: Dict[str, Any], title_fragment: str) -> bool:
    wanted = normalize_name(title_fragment)
    return any(wanted in normalize_name(node.get("title", "")) for node in nodes.get("nodes", []))


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


def assert_make_array_node(node: Dict[str, Any], expected_category: str, expected_count: int) -> None:
    if node.get("class") != "K2Node_MakeArray":
        raise RuntimeError(f"Unexpected node class for Make Array: {node}")
    if node.get("input_count") != expected_count:
        raise RuntimeError(f"Unexpected Make Array input count: {node}")

    output_pin_name = find_pin(node, "output", "", ("Array",), require_array=True)
    output_pin = next(pin for pin in node.get("pins", []) if pin.get("name") == output_pin_name)
    if output_pin.get("pin_type", {}).get("category") != expected_category:
        raise RuntimeError(f"Unexpected Make Array output type: {node}")

    for pin in input_value_pins(node):
        if pin.get("is_array"):
            raise RuntimeError(f"Make Array element input was incorrectly typed as array: {pin}")
        if pin.get("pin_type", {}).get("category") != expected_category:
            raise RuntimeError(f"Unexpected Make Array input pin type: {pin}")


def validate_successful_authoring_path() -> Dict[str, Any]:
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

    make_int_array = require_success(
        "add_blueprint_make_array_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "element_type": "int",
            "values": [1, 2, 3],
            "node_position": [60, 180],
        },
    )
    assert_make_array_node(make_int_array, "int", 3)
    if make_int_array.get("values_applied", {}).get("[0]") != "1":
        raise RuntimeError(f"Make Array int default was not applied: {make_int_array}")

    make_empty_string_array = require_success(
        "add_blueprint_make_array_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "element_type": "string",
            "input_count": 0,
            "node_position": [60, 440],
        },
    )
    assert_make_array_node(make_empty_string_array, "string", 0)

    make_bool_array = require_success(
        "add_blueprint_make_array_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "element_type": "bool",
            "values": [True, False],
            "node_position": [60, 620],
        },
    )
    assert_make_array_node(make_bool_array, "bool", 2)
    if make_bool_array.get("values_applied", {}).get("[0]") != "true":
        raise RuntimeError(f"Make Array bool default was not applied: {make_bool_array}")

    make_vector_array = require_success(
        "add_blueprint_make_array_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "element_type": "vector",
            "values": [{"x": 1, "y": 2, "z": 3}],
            "node_position": [60, 800],
        },
    )
    assert_make_array_node(make_vector_array, "struct", 1)
    if "X=1" not in make_vector_array.get("values_applied", {}).get("[0]", ""):
        raise RuntimeError(f"Make Array vector default was not applied: {make_vector_array}")

    length_node = require_success(
        "add_blueprint_array_function_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "operation": "length",
            "element_type": "int",
            "node_position": [420, 180],
        },
    )
    get_node = require_success(
        "add_blueprint_array_function_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "operation": "get",
            "element_type": "int",
            "param_defaults": {"Index": 1},
            "node_position": [420, 360],
        },
    )

    array_output_pin = find_pin(make_int_array, "output", "", ("Array",), require_array=True)
    connect(
        graph_id,
        make_int_array,
        array_output_pin,
        length_node,
        find_pin(length_node, "input", "", ("TargetArray",), require_array=True),
    )
    connect(
        graph_id,
        make_int_array,
        array_output_pin,
        get_node,
        find_pin(get_node, "input", "", ("TargetArray",), require_array=True),
    )

    validation = require_success(
        "compile_and_validate_blueprint",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "save": False,
            "refresh_nodes": True,
        },
        timeout=120.0,
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
    require_error("add_blueprint_make_array_node", {**base_params, "element_type": "bool", "values": ["true"]})
    require_error("add_blueprint_make_array_node", {**base_params, "element_type": "int", "values": "1,2,3"})
    require_error("add_blueprint_make_array_node", {**base_params, "element_type": "int", "input_count": 129})
    require_error(
        "add_blueprint_make_array_node",
        {**base_params, "element_type": "int", "input_count": 1, "values": [1, 2]},
    )
    require_error("add_blueprint_make_array_node", {**base_params, "element_type": "int", "is_array": True})

    nodes_after_failures = require_success(
        "list_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_name": FUNCTION_GRAPH_NAME,
            "graph_type": "function",
            "include_pins": True,
        },
    )
    make_array_count = sum(1 for node in nodes_after_failures.get("nodes", []) if node.get("class") == "K2Node_MakeArray")
    if make_array_count != 4:
        raise RuntimeError(f"Failed Make Array commands left unexpected nodes behind: {nodes_after_failures}")
    if has_node_title(nodes_after_failures, "Make Set"):
        raise RuntimeError(f"Unexpected collection node left behind: {nodes_after_failures}")


def main() -> None:
    cleanup_temp_assets([BLUEPRINT_NAME])
    try:
        validation = validate_successful_authoring_path()
        validate_error_paths()
        logger.info("Collection literal authoring validation passed: %s", validation)
    finally:
        cleanup_temp_assets([BLUEPRINT_NAME])


if __name__ == "__main__":
    main()
