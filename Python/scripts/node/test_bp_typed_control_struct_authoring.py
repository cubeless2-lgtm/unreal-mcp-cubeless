#!/usr/bin/env python
"""
Smoke test for Blueprint typed control and native struct helper authoring.

This creates a generic Blueprint function graph, authors native Make/Break
Vector/Rotator/Transform helper nodes plus contiguous Switch on Int nodes, and
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
BLUEPRINT_NAME = f"MCP_BPTypedControlStructSmoke_{RUN_ID}"
FUNCTION_GRAPH_NAME = f"TypedControlStructSmoke_{RUN_ID}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestBPTypedControlStructAuthoring")


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


def find_optional_pin(
    node: Dict[str, Any],
    direction: str,
    category: str = "",
    preferred_names: Iterable[str] = (),
) -> Optional[str]:
    try:
        return find_pin(node, direction, category, preferred_names)
    except RuntimeError:
        return None


def has_pin_named(node: Dict[str, Any], direction: str, category: str, pin_name: str) -> bool:
    wanted_name = normalize_name(pin_name)
    return any(
        normalize_name(pin.get("name", "")) == wanted_name
        for pin in pins_matching(node, direction, category)
    )


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


def set_real_inputs(blueprint_name: str, graph_id: str, node: Dict[str, Any], values: List[float]) -> None:
    real_pins = pins_matching(node, "input", "real")
    if len(real_pins) < len(values):
        raise RuntimeError(f"Expected at least {len(values)} real input pins on node: {node}")

    for pin, value in zip(real_pins, values):
        set_pin_default(blueprint_name, graph_id, node, pin.get("name", ""), value)


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
            "output_count": 2,
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
    literal = require_success(
        "add_blueprint_literal_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "literal_type": "int",
            "value": 1,
            "node_position": [80, 200],
        },
    )
    switch = require_success(
        "add_blueprint_switch_int_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "case_values": [0, 1, 2],
            "has_default_pin": True,
            "node_position": [280, 0],
        },
    )
    switch_without_default = require_success(
        "add_blueprint_switch_int_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "start_index": 5,
            "case_count": 2,
            "has_default_pin": False,
            "node_position": [280, 320],
        },
    )

    if has_pin_named(switch_without_default, "output", "exec", "Default"):
        raise RuntimeError(f"Switch without default unexpectedly exposed a Default pin: {switch_without_default}")
    for case_name in ("0", "1", "2"):
        find_exec_pin(switch, "output", (case_name,))
    for case_name in ("5", "6"):
        find_exec_pin(switch_without_default, "output", (case_name,))

    make_vector = require_success(
        "add_blueprint_make_struct_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "struct_type": "vector",
            "node_position": [80, 520],
        },
    )
    break_vector = require_success(
        "add_blueprint_break_struct_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "struct_type": "vector",
            "node_position": [360, 520],
        },
    )
    make_rotator = require_success(
        "add_blueprint_make_struct_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "struct_type": "rotator",
            "node_position": [80, 740],
        },
    )
    break_rotator = require_success(
        "add_blueprint_break_struct_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "struct_type": "rotator",
            "node_position": [360, 740],
        },
    )
    make_transform = require_success(
        "add_blueprint_make_struct_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "struct_type": "transform",
            "node_position": [640, 600],
        },
    )
    break_transform = require_success(
        "add_blueprint_break_struct_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "struct_type": "transform",
            "node_position": [920, 600],
        },
    )

    set_real_inputs(BLUEPRINT_NAME, graph_id, make_vector, [1.0, 2.0, 3.0])
    set_real_inputs(BLUEPRINT_NAME, graph_id, make_rotator, [10.0, 20.0, 30.0])
    require_error(
        "set_blueprint_pin_default",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "node_id": make_vector["node_id"],
            "pin_name": pins_matching(make_vector, "input", "real")[0].get("name", ""),
            "direction": "input",
            "value": "not_a_number",
        },
    )

    connect(
        BLUEPRINT_NAME,
        graph_id,
        sequence,
        find_exec_pin(sequence, "output", ("then_0", "then 0", "then")),
        switch,
        find_exec_pin(switch, "input", ("execute", "exec")),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        sequence,
        find_exec_pin(sequence, "output", ("then_1", "then 1")),
        switch_without_default,
        find_exec_pin(switch_without_default, "input", ("execute", "exec")),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        literal,
        find_pin(literal, "output", "int", ("ReturnValue",)),
        switch,
        find_pin(switch, "input", "int", ("Selection",)),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        literal,
        find_pin(literal, "output", "int", ("ReturnValue",)),
        switch_without_default,
        find_pin(switch_without_default, "input", "int", ("Selection",)),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        switch,
        find_exec_pin(switch, "output", ("1",)),
        ret,
        find_exec_pin(ret, "input", ("execute", "exec")),
        allow_replacement=True,
    )

    connect(
        BLUEPRINT_NAME,
        graph_id,
        make_vector,
        find_pin(make_vector, "output", "struct", ("ReturnValue",)),
        break_vector,
        find_pin(break_vector, "input", "struct", ("InVec", "Vector")),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        make_rotator,
        find_pin(make_rotator, "output", "struct", ("ReturnValue",)),
        break_rotator,
        find_pin(break_rotator, "input", "struct", ("InRot", "Rotation")),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        make_vector,
        find_pin(make_vector, "output", "struct", ("ReturnValue",)),
        make_transform,
        find_pin(make_transform, "input", "struct", ("Location", "Translation")),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        make_rotator,
        find_pin(make_rotator, "output", "struct", ("ReturnValue",)),
        make_transform,
        find_pin(make_transform, "input", "struct", ("Rotation",)),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        make_transform,
        find_pin(make_transform, "output", "struct", ("ReturnValue",)),
        break_transform,
        find_pin(break_transform, "input", "struct", ("InTransform", "Transform")),
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
    require_error("add_blueprint_make_struct_node", {**base_params, "struct_type": "linear_color"})
    require_error("add_blueprint_break_struct_node", {**base_params, "struct_type": "unsupported"})
    require_error("add_blueprint_switch_int_node", {**base_params, "case_values": [0, 2]})
    require_error("add_blueprint_switch_int_node", {**base_params, "case_values": [1, 1]})
    require_error("add_blueprint_switch_int_node", {**base_params, "case_count": 0})
    require_error("add_blueprint_switch_int_node", {**base_params, "case_count": 129})


def main() -> None:
    cleanup_temp_assets([BLUEPRINT_NAME])
    try:
        validation = validate_successful_authoring_path()
        validate_error_paths()
        logger.info("Typed control and struct authoring validation passed: %s", validation)
    finally:
        cleanup_temp_assets([BLUEPRINT_NAME])


if __name__ == "__main__":
    main()
