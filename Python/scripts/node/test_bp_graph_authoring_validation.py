#!/usr/bin/env python
"""
Smoke test for Blueprint graph authoring MCP commands.

This creates a generic Blueprint, creates a function graph, adds basic K2 nodes,
and validates the Blueprint compile result.
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
BLUEPRINT_NAME = f"MCP_BPGraphAuthoringSmoke_{RUN_ID}"
DIAGNOSTIC_BLUEPRINT_NAME = f"MCP_BPCompileDiagnosticSmoke_{RUN_ID}"
FUNCTION_GRAPH_NAME = f"ConvertedFunctionSmoke_{RUN_ID}"
INVALID_PACKAGE_BLUEPRINT_NAME = f"MCP_BPInvalidPackageSmoke_{RUN_ID}"

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("TestBPGraphAuthoringValidation")


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


def find_exec_pin(node: Dict[str, Any], direction: str, preferred_names=()) -> str:
    pins = node.get("pins", [])
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

    raise RuntimeError(f"No {direction} exec pin found on node: {node}")


def find_pin(node: Dict[str, Any], direction: str, category: str, preferred_names=()) -> str:
    pins = node.get("pins", [])
    normalized_preferred = {name.lower().replace(" ", "").replace("_", "") for name in preferred_names}
    for pin in pins:
        pin_name = pin.get("name", "")
        normalized_name = pin_name.lower().replace(" ", "").replace("_", "")
        if (
            pin.get("direction") == direction
            and pin.get("category", "").lower() == category.lower()
            and normalized_name in normalized_preferred
        ):
            return pin_name

    for pin in pins:
        if pin.get("direction") == direction and pin.get("category", "").lower() == category.lower():
            return pin.get("name", "")

    raise RuntimeError(f"No {direction} {category} pin found on node: {node}")


def require_error(command: str, params: Dict[str, Any]) -> Dict[str, Any]:
    response = send_command(command, params)
    if not response or response.get("status") != "error":
        raise RuntimeError(f"{command} should have failed but returned: {response}")
    return response


def create_temp_blueprint(blueprint_name: str) -> None:
    create_response = send_command(
        "create_blueprint",
        {
            "name": blueprint_name,
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
        )
        if not response or response.get("status") != "success":
            logger.warning("Cleanup returned non-success: %s", response)
    except Exception as exc:
        logger.warning("Cleanup failed: %s", exc)


def require_compile_failure_diagnostics(validation: Dict[str, Any]) -> None:
    if validation.get("validation_pass"):
        raise RuntimeError(f"Diagnostic validation should have failed but passed: {validation}")
    if validation.get("compile_error_count", 0) < 1:
        raise RuntimeError(f"Diagnostic validation returned no compile errors: {validation}")

    diagnostics = validation.get("diagnostics", [])
    if not diagnostics:
        raise RuntimeError(f"Diagnostic validation returned no structured diagnostics: {validation}")

    for diagnostic in diagnostics:
        if diagnostic.get("severity") == "error" and diagnostic.get("message"):
            return

    raise RuntimeError(f"Diagnostic validation returned no error diagnostic with a message: {validation}")


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
    graph = graph_result["graph"]
    graph_id = graph["graph_id"]

    branch = require_success(
        "add_blueprint_branch_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "node_position": [240, 0],
        },
    )
    sequence = require_success(
        "add_blueprint_sequence_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "node_position": [40, 0],
            "output_count": 2,
        },
    )
    ret = require_success(
        "add_blueprint_return_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "node_position": [520, 0],
        },
    )
    require_success(
        "add_blueprint_dynamic_cast_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "target_class": "Actor",
            "node_position": [240, 220],
        },
    )

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
    if validation.get("diagnostic_count", 0) != 0:
        raise RuntimeError(f"Successful validation unexpectedly returned diagnostics: {validation}")

    missing_graph = require_success(
        "resolve_blueprint_graph",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": "00000000000000000000000000000000",
            "graph_type": "function",
        },
    )
    if missing_graph.get("resolved"):
        raise RuntimeError(f"Invalid graph id unexpectedly resolved: {missing_graph}")

    require_error(
        "add_blueprint_return_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
        },
    )
    require_error(
        "add_blueprint_dynamic_cast_node",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "target_class": "__MissingClassForNegativeSmoke",
        },
    )
    require_error(
        "connect_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_NAME,
            "graph_id": graph_id,
            "source_node_id": sequence["node_id"],
            "source_pin": find_exec_pin(sequence, "output", ("then_1", "then 1")),
            "target_node_id": branch["node_id"],
            "target_pin": find_pin(branch, "input", "bool", ("condition",)),
        },
    )

    return validation


def validate_compile_diagnostics_path() -> Dict[str, Any]:
    create_temp_blueprint(DIAGNOSTIC_BLUEPRINT_NAME)

    event = require_success(
        "add_blueprint_event_node",
        {
            "blueprint_name": DIAGNOSTIC_BLUEPRINT_NAME,
            "event_name": "ReceiveBeginPlay",
            "node_position": [0, 120],
        },
    )
    cast = require_success(
        "add_blueprint_dynamic_cast_node",
        {
            "blueprint_name": DIAGNOSTIC_BLUEPRINT_NAME,
            "target_class": "Actor",
            "node_position": [120, 120],
        }
    )
    require_success(
        "connect_blueprint_nodes",
        {
            "blueprint_name": DIAGNOSTIC_BLUEPRINT_NAME,
            "source_node_id": event["node_id"],
            "source_pin": "then",
            "target_node_id": cast["node_id"],
            "target_pin": "execute",
        }
    )

    validation = require_success(
        "compile_and_validate_blueprint",
        {
            "blueprint_name": DIAGNOSTIC_BLUEPRINT_NAME,
            "save": False,
            "refresh_nodes": True,
        },
    )
    require_compile_failure_diagnostics(validation)
    return validation


def validate_create_blueprint_package_path_guards() -> None:
    require_error(
        "create_blueprint",
        {
            "name": INVALID_PACKAGE_BLUEPRINT_NAME,
            "parent_class": "Actor",
            "package_path": "/Engine/_MCP_Temp",
        },
    )
    require_error(
        "create_blueprint",
        {
            "name": INVALID_PACKAGE_BLUEPRINT_NAME,
            "parent_class": "Actor",
            "package_path": "Game/_MCP_Temp",
        },
    )
    require_error(
        "create_blueprint",
        {
            "name": INVALID_PACKAGE_BLUEPRINT_NAME,
            "parent_class": "Actor",
            "package_path": "/Gameplay",
        },
    )
    require_error(
        "create_blueprint",
        {
            "name": INVALID_PACKAGE_BLUEPRINT_NAME,
            "parent_class": "Actor",
            "package_path": "",
        },
    )
    require_error(
        "create_blueprint",
        {
            "name": INVALID_PACKAGE_BLUEPRINT_NAME,
            "parent_class": "Actor",
            "package_path": "/Game/_MCP_Temp.SomeObject",
        },
    )
    require_error(
        "create_blueprint",
        {
            "name": INVALID_PACKAGE_BLUEPRINT_NAME,
            "parent_class": "Actor",
            "package_path": 42,
        },
    )


def main() -> None:
    try:
        validate_create_blueprint_package_path_guards()
        success_validation = validate_successful_authoring_path()
        diagnostic_validation = validate_compile_diagnostics_path()

        logger.info("Blueprint graph authoring validation passed: %s", success_validation)
        logger.info("Blueprint compile diagnostic validation passed: %s", diagnostic_validation)
    finally:
        cleanup_temp_assets([BLUEPRINT_NAME, DIAGNOSTIC_BLUEPRINT_NAME])


if __name__ == "__main__":
    main()
