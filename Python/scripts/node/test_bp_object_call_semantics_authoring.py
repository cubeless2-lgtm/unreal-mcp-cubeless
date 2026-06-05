#!/usr/bin/env python
"""
Smoke test for Blueprint object reference and function call semantics commands.

This creates a generic Blueprint function graph, authors validated function call
nodes for self/object/static calls, connects explicit target pins where needed,
and validates the Blueprint compile result.
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
BLUEPRINT_NAME = f"MCP_BPObjectCallSemanticsSmoke_{RUN_ID}"
FUNCTION_GRAPH_NAME = f"ObjectCallSemanticsSmoke_{RUN_ID}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestBPObjectCallSemanticsAuthoring")


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


def find_object_input_pin(node: Dict[str, Any], preferred_names: Iterable[str] = ()) -> str:
    return find_pin(node, "input", "object", preferred_names)


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

    scene_var = require_success(
        "add_blueprint_local_variable",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "variable_name": "SceneTarget",
            "variable_type": "object",
            "type_object": "/Script/Engine.SceneComponent",
        },
    )
    if scene_var.get("pin_type", {}).get("subcategory_object") != "/Script/Engine.SceneComponent":
        raise RuntimeError(f"Scene component object variable was not typed correctly: {scene_var}")

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
            "node_position": [980, 0],
        },
    )
    scene_get = require_success(
        "add_blueprint_variable_get_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "variable_name": "SceneTarget",
            "node_position": [80, 320],
        },
    )
    hide_call = require_success(
        "add_blueprint_call_function_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "function_class": "/Script/Engine.Actor",
            "function_name": "SetActorHiddenInGame",
            "param_defaults": {"bNewHidden": True},
            "node_position": [220, 0],
        },
    )
    location_call = require_success(
        "add_blueprint_call_function_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "function_class": "/Script/Engine.SceneComponent",
            "function_name": "K2_SetRelativeLocation",
            "param_defaults": {
                "NewLocation": [10, 20, 30],
                "bSweep": False,
                "bTeleport": False,
            },
            "node_position": [540, 0],
        },
    )
    actor_of_class_call = require_success(
        "add_blueprint_call_function_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "function_class": "/Script/Engine.GameplayStatics",
            "function_name": "GetActorOfClass",
            "param_defaults": {"ActorClass": "/Script/Engine.Actor"},
            "node_position": [540, 360],
        },
    )
    get_location_call = require_success(
        "add_blueprint_call_function_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "function_class": "/Script/Engine.Actor",
            "function_name": "K2_GetActorLocation",
            "node_position": [220, 360],
        },
    )

    if not hide_call.get("param_defaults_applied", {}).get("bNewHidden"):
        raise RuntimeError(f"Boolean default was not reported as applied: {hide_call}")
    if actor_of_class_call.get("param_defaults_applied", {}).get("ActorClass") != "/Script/Engine.Actor":
        raise RuntimeError(f"Class default was not reported as applied: {actor_of_class_call}")
    if not get_location_call.get("is_pure"):
        raise RuntimeError(f"Expected K2_GetActorLocation to be pure: {get_location_call}")

    connect(
        BLUEPRINT_NAME,
        graph_id,
        sequence,
        find_exec_pin(sequence, "output", ("then_0", "then 0", "then")),
        hide_call,
        find_exec_pin(hide_call, "input", ("execute", "exec")),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        hide_call,
        find_exec_pin(hide_call, "output", ("then",)),
        location_call,
        find_exec_pin(location_call, "input", ("execute", "exec")),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        scene_get,
        find_pin(scene_get, "output", "object", ("SceneTarget",)),
        location_call,
        find_object_input_pin(location_call, ("self", "target")),
    )
    connect(
        BLUEPRINT_NAME,
        graph_id,
        location_call,
        find_exec_pin(location_call, "output", ("then",)),
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
    require_error(
        "add_blueprint_call_function_node",
        {**base_params, "function_class": "/Script/Engine.KismetSystemLibrary", "function_name": "Delay"},
    )
    require_error(
        "add_blueprint_call_function_node",
        {**base_params, "function_class": "/Script/Engine.KismetArrayLibrary", "function_name": "Array_Add"},
    )
    require_error(
        "add_blueprint_call_function_node",
        {**base_params, "function_class": "/Script/Engine.Actor", "function_name": "__MissingFunction"},
    )
    require_error(
        "add_blueprint_call_function_node",
        {
            **base_params,
            "function_class": "/Script/Engine.Actor",
            "function_name": "SetActorTickEnabled",
            "param_defaults": {"bEnabled": "not_a_bool"},
        },
    )
    nodes_after_bad_default = require_success(
        "list_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_name": FUNCTION_GRAPH_NAME,
            "graph_type": "function",
            "include_pins": True,
        },
    )
    if has_node_title(nodes_after_bad_default, "Set Actor Tick Enabled"):
        raise RuntimeError(f"Invalid default left a failed function call node behind: {nodes_after_bad_default}")


def main() -> None:
    cleanup_temp_assets([BLUEPRINT_NAME])
    try:
        validation = validate_successful_authoring_path()
        validate_error_paths()
        logger.info("Object call semantics authoring validation passed: %s", validation)
    finally:
        cleanup_temp_assets([BLUEPRINT_NAME])


if __name__ == "__main__":
    main()
