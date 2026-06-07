#!/usr/bin/env python
"""
Section 71 durable bridge recovery readiness contract.

This contract verifies the local UnrealMCP recovery inputs before any live
durable check is retried. It does not probe the socket or open durable
authoring.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any, Dict, Sequence


BRIDGE_RECOVERY_READINESS_SCHEMA = "section_71_durable_bridge_recovery_readiness_contract_v1"
BRIDGE_RECOVERY_READINESS_SUMMARY_SCHEMA = "section_71_durable_bridge_recovery_readiness_summary_v1"
EXPECTED_SERVER_NAME = "unrealMCP"
EXPECTED_COMMAND = "uv"
EXPECTED_DIRECTORY_ARG = "../unreal-mcp-cubeless/Python"
EXPECTED_PYTHON_VERSION = "3.11"
EXPECTED_SERVER_SCRIPT = "unreal_mcp_server.py"
EXPECTED_BRIDGE_HOST = "127.0.0.1"
EXPECTED_BRIDGE_PORT = 55557


def read_mcp_config(project_root: Path) -> Dict[str, Any]:
    config_path = project_root / ".mcp.json"
    if not config_path.exists():
        return {}
    return json.loads(config_path.read_text(encoding="utf-8"))


def _arg_after(args: Sequence[str], key: str) -> str:
    if key not in args:
        return ""
    index = list(args).index(key)
    if index + 1 >= len(args):
        return ""
    return str(args[index + 1])


def collect_bridge_recovery_inputs(
    project_root: Path,
    mcp_config: Dict[str, Any] | None = None,
    uv_available: bool | None = None,
) -> Dict[str, Any]:
    mcp_config = mcp_config if mcp_config is not None else read_mcp_config(project_root)
    server = mcp_config.get("mcpServers", {}).get(EXPECTED_SERVER_NAME, {})
    args = [str(item) for item in server.get("args", [])]
    command = str(server.get("command", ""))
    directory_arg = _arg_after(args, "--directory")
    python_version = _arg_after(args, "--python")
    python_dir = (project_root / directory_arg).resolve() if directory_arg else Path()
    script_path = (python_dir / EXPECTED_SERVER_SCRIPT).resolve() if directory_arg else Path()
    return {
        "mcp_config_present": bool(mcp_config),
        "server_defined": bool(server),
        "command": command,
        "args": args,
        "directory_arg": directory_arg,
        "python_version": python_version,
        "python_dir": str(python_dir) if directory_arg else "",
        "python_dir_exists": python_dir.exists() if directory_arg else False,
        "server_script": str(script_path) if directory_arg else "",
        "server_script_exists": script_path.exists() if directory_arg else False,
        "uv_available": shutil.which(command) is not None if uv_available is None and command else bool(uv_available),
        "bridge_host": EXPECTED_BRIDGE_HOST,
        "bridge_port": EXPECTED_BRIDGE_PORT,
    }


def build_bridge_recovery_readiness_contract(
    requested: bool,
    recovery_inputs: Dict[str, Any],
) -> Dict[str, Any]:
    args = list(recovery_inputs.get("args", []))
    local_inputs_ready = bool(
        requested
        and recovery_inputs.get("mcp_config_present")
        and recovery_inputs.get("server_defined")
        and recovery_inputs.get("command") == EXPECTED_COMMAND
        and recovery_inputs.get("directory_arg") == EXPECTED_DIRECTORY_ARG
        and recovery_inputs.get("python_version") == EXPECTED_PYTHON_VERSION
        and EXPECTED_SERVER_SCRIPT in args
        and recovery_inputs.get("python_dir_exists")
        and recovery_inputs.get("server_script_exists")
        and recovery_inputs.get("uv_available")
    )
    missing = []
    if requested:
        if not recovery_inputs.get("mcp_config_present"):
            missing.append("mcp_config")
        if not recovery_inputs.get("server_defined"):
            missing.append("unrealMCP_server")
        if recovery_inputs.get("command") != EXPECTED_COMMAND:
            missing.append("uv_command")
        if recovery_inputs.get("directory_arg") != EXPECTED_DIRECTORY_ARG:
            missing.append("sibling_python_directory_arg")
        if recovery_inputs.get("python_version") != EXPECTED_PYTHON_VERSION:
            missing.append("python_3_11_arg")
        if EXPECTED_SERVER_SCRIPT not in args:
            missing.append("unreal_mcp_server_script_arg")
        if not recovery_inputs.get("python_dir_exists"):
            missing.append("sibling_python_directory")
        if not recovery_inputs.get("server_script_exists"):
            missing.append("unreal_mcp_server_script")
        if not recovery_inputs.get("uv_available"):
            missing.append("uv_available")

    return {
        "id": "durable_bridge_recovery_readiness",
        "schema": BRIDGE_RECOVERY_READINESS_SCHEMA,
        "requested": requested,
        "expected_server_name": EXPECTED_SERVER_NAME,
        "expected_command": EXPECTED_COMMAND,
        "expected_directory_arg": EXPECTED_DIRECTORY_ARG,
        "expected_python_version": EXPECTED_PYTHON_VERSION,
        "expected_server_script": EXPECTED_SERVER_SCRIPT,
        "expected_bridge_host": EXPECTED_BRIDGE_HOST,
        "expected_bridge_port": EXPECTED_BRIDGE_PORT,
        "local_recovery_inputs_ready": local_inputs_ready,
        "missing_recovery_inputs": missing,
        "missing_recovery_input_count": len(missing),
        "bridge_socket_probe_performed": False,
        "bridge_reachable": False,
        "read_only_canary_retry_allowed_after_recovery": False,
        "durable_executor_may_open_after_recovery": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "live_authoring_command_count": 0,
        "live_save_or_delete_command_count": 0,
        "blocked_by": []
        if not requested
        else [
            "section_71_recovery_readiness_does_not_probe_or_open_bridge",
            "read_only_canary_retry_requires_separate_live_preflight_run",
        ],
        "required_reinforcement": []
        if not requested
        else [
            "repair or start Unreal Editor bridge separately before live read-only retry",
            "retry only Section 57 read-only canary preflight after recovery",
            "keep durable save/delete/rename disabled during recovery readiness review",
        ],
    }


def summarize_bridge_recovery_readiness_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("local_recovery_inputs_ready")) == len(requested)
            and sum(1 for contract in requested if contract.get("bridge_socket_probe_performed")) == 0
            and sum(1 for contract in requested if contract.get("bridge_reachable")) == 0
            and sum(1 for contract in requested if contract.get("read_only_canary_retry_allowed_after_recovery")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_after_recovery")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_delete_rename_allowed")) == 0
            and sum(contract.get("live_authoring_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_save_or_delete_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": BRIDGE_RECOVERY_READINESS_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_bridge_recovery_readiness_count": len(requested),
        "local_recovery_inputs_ready_count": sum(
            1 for contract in requested if contract.get("local_recovery_inputs_ready")
        ),
        "missing_recovery_input_count": sum(
            contract.get("missing_recovery_input_count", 0) for contract in requested
        ),
        "bridge_socket_probe_performed_count": sum(
            1 for contract in requested if contract.get("bridge_socket_probe_performed")
        ),
        "bridge_reachable_count": sum(1 for contract in requested if contract.get("bridge_reachable")),
        "read_only_canary_retry_allowed_after_recovery_count": sum(
            1 for contract in requested if contract.get("read_only_canary_retry_allowed_after_recovery")
        ),
        "durable_executor_may_open_after_recovery_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_after_recovery")
        ),
        "durable_authoring_allowed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_allowed")
        ),
        "save_delete_rename_allowed_count": sum(
            1 for contract in requested if contract.get("save_delete_rename_allowed")
        ),
        "live_authoring_command_count": sum(contract.get("live_authoring_command_count", 0) for contract in requested),
        "live_save_or_delete_command_count": sum(
            contract.get("live_save_or_delete_command_count", 0) for contract in requested
        ),
    }
