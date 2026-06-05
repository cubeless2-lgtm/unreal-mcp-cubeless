#!/usr/bin/env python
"""
Smoke test for Blueprint enum and advanced control-flow authoring MCP commands.

This creates a generic Blueprint function graph, authors enum declarations,
enum literal nodes, and a Switch on Enum node, then validates the Blueprint
compile result.
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
BLUEPRINT_NAME = f"MCP_BPEnumAdvancedControlSmoke_{RUN_ID}"
FUNCTION_GRAPH_NAME = f"EnumAdvancedControlSmoke_{RUN_ID}"
ENUM_TYPE = "/Script/Engine.ECollisionEnabled"
OTHER_ENUM_TYPE = "/Script/Engine.ETickingGroup"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestBPEnumAdvancedControlAuthoring")


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
) -> str:
    pins = pins_matching(node, direction, category)
    normalized_preferred = {normalize_name(name) for name in preferred_names}

    for pin in pins:
        pin_name = pin.get("name", "")
        if normalize_name(pin_name) in normalized_preferred:
            return pin_name

    if pins:
        return pins[0].get("name", "")

    raise RuntimeError(f"No {direction} {category or 'any'} pin found on node: {node}")


def find_exec_pin(node: Dict[str, Any], direction: str, preferred_names: Iterable[str] = ()) -> str:
    return find_pin(node, direction, "exec", preferred_names)


def output_exec_pin_names(node: Dict[str, Any]) -> List[str]:
    return [pin.get("name", "") for pin in pins_matching(node, "output", "exec")]


def assert_no_pin_named(nodes: Dict[str, Any], pin_name: str) -> None:
    for node in nodes.get("nodes", []):
        for pin in node.get("pins", []):
            if pin.get("name") == pin_name:
                raise RuntimeError(f"Unexpected pin left behind after failed command: {pin_name} in {nodes}")


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


def connect(
    blueprint_name: str,
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
            "blueprint_name": blueprint_name,
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

    variable = require_success(
        "add_blueprint_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "variable_name": "EnumMode",
            "variable_type": "enum",
            "type_object": ENUM_TYPE,
            "default_value": "NoCollision",
        },
    )
    if variable.get("pin_type", {}).get("category") != "byte":
        raise RuntimeError(f"Enum variable did not use a byte enum pin: {variable}")

    parameter = require_success(
        "add_blueprint_function_parameter",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "parameter_name": "InputMode",
            "parameter_type": "enum",
            "enum_type": ENUM_TYPE,
            "default_value": "PhysicsOnly",
        },
    )
    if parameter.get("pin_type", {}).get("category") != "byte":
        raise RuntimeError(f"Enum parameter did not use a byte enum pin: {parameter}")

    local = require_success(
        "add_blueprint_local_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "variable_name": "LocalMode",
            "variable_type": "enum",
            "type_object": ENUM_TYPE,
            "default_value": 1,
        },
    )
    if local.get("default_value") != "QueryOnly":
        raise RuntimeError(f"Numeric enum default was not normalized to the enum entry name: {local}")

    sequence = require_success(
        "add_blueprint_sequence_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "node_position": [0, 0],
        },
    )
    ret = require_success(
        "add_blueprint_return_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "node_position": [760, 0],
        },
    )
    enum_literal = require_success(
        "add_blueprint_enum_literal_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "enum_type": ENUM_TYPE,
            "value": "QueryOnly",
            "node_position": [80, 220],
        },
    )
    default_enum_literal = require_success(
        "add_blueprint_enum_literal_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "type_object": ENUM_TYPE,
            "node_position": [80, 440],
        },
    )
    if not default_enum_literal.get("default_value"):
        raise RuntimeError(f"Enum literal without a value did not get a visible default: {default_enum_literal}")

    switch_enum = require_success(
        "add_blueprint_switch_enum_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "enum_type": ENUM_TYPE,
            "has_default_pin": True,
            "node_position": [360, 0],
        },
    )
    if switch_enum.get("case_count", 0) < 2:
        raise RuntimeError(f"Switch enum did not expose expected case pins: {switch_enum}")
    expected_case_names = {entry.get("name", "") for entry in switch_enum.get("enum_entries", [])}
    actual_case_names = {name for name in output_exec_pin_names(switch_enum) if normalize_name(name) != "default"}
    if switch_enum.get("case_count") != len(expected_case_names) or actual_case_names != expected_case_names:
        raise RuntimeError(
            f"Switch enum case metadata does not match actual pins. "
            f"expected={sorted(expected_case_names)} actual={sorted(actual_case_names)} node={switch_enum}"
        )

    enum_input_pin = find_pin(enum_literal, "input", "byte", ("Enum",))
    normalized_default = set_pin_default(BLUEPRINT_NAME, graph_id, enum_literal, enum_input_pin, 1)
    if normalized_default.get("pin", {}).get("default_value") != "QueryOnly":
        raise RuntimeError(f"set_blueprint_pin_default did not normalize numeric enum value: {normalized_default}")

    connect(
        BLUEPRINT_NAME,
        graph_id,
        sequence,
        find_exec_pin(sequence, "output", ("then_0", "then 0", "then")),
        switch_enum,
        find_exec_pin(switch_enum, "input", ("execute", "exec")),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        enum_literal,
        find_pin(enum_literal, "output", "byte", ("ReturnValue",)),
        switch_enum,
        find_pin(switch_enum, "input", "byte", ("Selection",)),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        switch_enum,
        find_exec_pin(switch_enum, "output", ("QueryOnly",)),
        ret,
        find_exec_pin(ret, "input", ("execute", "exec")),
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
    require_error("add_blueprint_enum_literal_node", {**base_params, "enum_type": "/Script/Engine.EMissingEnum", "value": "Any"})
    require_error("add_blueprint_enum_literal_node", {**base_params, "enum_type": ENUM_TYPE, "value": "MissingValue"})
    require_error("add_blueprint_switch_enum_node", {**base_params, "enum_type": "/Script/Engine.EMissingEnum"})
    require_error(
        "add_blueprint_local_variable",
        {
            **base_params,
            "variable_name": "BadEnumDefault",
            "variable_type": "enum",
            "type_object": ENUM_TYPE,
            "default_value": "MissingValue",
        },
    )
    require_error(
        "add_blueprint_function_parameter",
        {
            **base_params,
            "parameter_name": "BadEnumParamDefault",
            "parameter_type": "enum",
            "enum_type": ENUM_TYPE,
            "default_value": "MissingValue",
        },
    )
    require_error(
        "add_blueprint_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "variable_name": "BadEnumArrayDefault",
            "variable_type": "enum",
            "type_object": ENUM_TYPE,
            "is_array": True,
            "default_value": 1,
        },
    )
    nodes_after_bad_parameter = require_success(
        "list_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_name": FUNCTION_GRAPH_NAME,
            "graph_type": "function",
            "include_pins": True,
        },
    )
    assert_no_pin_named(nodes_after_bad_parameter, "BadEnumParamDefault")

    graph_result = require_success(
        "resolve_blueprint_graph",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_name": FUNCTION_GRAPH_NAME,
            "graph_type": "function",
        },
    )
    graph_id = graph_result["graph"]["graph_id"]
    wrong_literal = require_success(
        "add_blueprint_enum_literal_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "enum_type": OTHER_ENUM_TYPE,
            "value": "TG_PrePhysics",
            "node_position": [80, 680],
        },
    )
    switch_enum = require_success(
        "add_blueprint_switch_enum_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "enum_type": ENUM_TYPE,
            "node_position": [360, 680],
        },
    )
    require_error(
        "connect_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "source_node_id": wrong_literal["node_id"],
            "source_pin": find_pin(wrong_literal, "output", "byte", ("ReturnValue",)),
            "target_node_id": switch_enum["node_id"],
            "target_pin": find_pin(switch_enum, "input", "byte", ("Selection",)),
        },
    )


def main() -> None:
    cleanup_temp_assets([BLUEPRINT_NAME])
    try:
        validation = validate_successful_authoring_path()
        validate_error_paths()
        logger.info("Enum advanced control authoring validation passed: %s", validation)
    finally:
        cleanup_temp_assets([BLUEPRINT_NAME])


if __name__ == "__main__":
    main()
