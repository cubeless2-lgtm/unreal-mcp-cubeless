#!/usr/bin/env python
"""
Section 61 durable canary bridge refresh contract.

The contract separates a fresh UnrealMCP bridge/read-only canary preflight
refresh from durable authoring execution. Missing live bridge evidence keeps
the durable executor closed; it does not fail the offline safety boundary.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_BRIDGE_REFRESH_SCHEMA = "section_61_durable_canary_bridge_refresh_contract_v1"
CANARY_BRIDGE_REFRESH_SUMMARY_SCHEMA = "section_61_durable_canary_bridge_refresh_summary_v1"
EXPECTED_MCP_SERVER = "unrealMCP"
EXPECTED_BRIDGE_HOST = "127.0.0.1"
EXPECTED_BRIDGE_PORT = 55557


def build_bridge_refresh_contract(
    requested: bool,
    canary_live_preflight_contract: Dict[str, Any],
    bridge_status: Dict[str, Any] | None = None,
    refreshed_live_result: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    bridge_status = bridge_status or {}
    refreshed_live_result = refreshed_live_result or {}
    read_only_preflight_allowed = bool(
        requested and canary_live_preflight_contract.get("read_only_live_preflight_allowed")
    )
    bridge_reachable = bool(
        bridge_status.get("mcp_server") == EXPECTED_MCP_SERVER
        and bridge_status.get("host") == EXPECTED_BRIDGE_HOST
        and bridge_status.get("port") == EXPECTED_BRIDGE_PORT
        and bridge_status.get("reachable") is True
    )
    read_only_result_refreshed = bool(
        refreshed_live_result.get("status") == "passed"
        and refreshed_live_result.get("read_only") is True
        and refreshed_live_result.get("asset_exists_check_performed") is True
        and not refreshed_live_result.get("authoring_attempted")
        and not refreshed_live_result.get("save_or_delete_attempted")
        and not refreshed_live_result.get("cleanup_attempted")
        and not refreshed_live_result.get("canary_execution_attempted")
    )
    blocked_by: list[str] = []
    if requested:
        if not read_only_preflight_allowed:
            blocked_by.append("section_57_read_only_canary_preflight_not_allowed")
        if not bridge_reachable:
            blocked_by.append("unrealmcp_bridge_refresh_not_reachable")
        if not read_only_result_refreshed:
            blocked_by.append("canary_read_only_preflight_result_not_refreshed")
        blocked_by.append("section_61_bridge_refresh_blocks_durable_execution")

    return {
        "id": "durable_canary_bridge_refresh",
        "schema": CANARY_BRIDGE_REFRESH_SCHEMA,
        "requested": requested,
        "expected_mcp_server": EXPECTED_MCP_SERVER,
        "expected_bridge_host": EXPECTED_BRIDGE_HOST,
        "expected_bridge_port": EXPECTED_BRIDGE_PORT,
        "canary_asset_path": canary_live_preflight_contract.get("canary_asset_path", "") if requested else "",
        "read_only_preflight_allowed": read_only_preflight_allowed,
        "bridge_refresh_required": requested,
        "bridge_reachable": bridge_reachable,
        "read_only_result_refreshed": read_only_result_refreshed,
        "bridge_refresh_satisfied": bool(
            requested and read_only_preflight_allowed and bridge_reachable and read_only_result_refreshed
        ),
        "canary_execution_allowed_after_refresh": False,
        "durable_executor_may_open_after_refresh": False,
        "authoring_command_allowed": False,
        "save_or_delete_allowed": False,
        "cleanup_command_allowed": False,
        "live_authoring_command_count": 0,
        "live_save_or_delete_command_count": 0,
        "live_cleanup_command_count": 0,
        "blocked_by": sorted(set(blocked_by)),
        "required_reinforcement": []
        if not requested
        else [
            "refresh the UnrealMCP bridge status on 127.0.0.1:55557",
            "record a fresh read-only canary asset-exists result",
            "keep durable canary execution closed after bridge refresh",
        ],
    }


def summarize_bridge_refresh_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    unsafe_count = sum(
        1
        for contract in requested
        if contract.get("canary_execution_allowed_after_refresh")
        or contract.get("durable_executor_may_open_after_refresh")
        or contract.get("authoring_command_allowed")
        or contract.get("save_or_delete_allowed")
        or contract.get("cleanup_command_allowed")
        or contract.get("live_authoring_command_count", 0) > 0
        or contract.get("live_save_or_delete_command_count", 0) > 0
        or contract.get("live_cleanup_command_count", 0) > 0
    )
    status = "not_requested"
    if requested:
        status = "passed" if unsafe_count == 0 else "failed"
    return {
        "schema": CANARY_BRIDGE_REFRESH_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_bridge_refresh_count": len(requested),
        "read_only_preflight_allowed_count": sum(
            1 for contract in requested if contract.get("read_only_preflight_allowed")
        ),
        "bridge_refresh_required_count": sum(1 for contract in requested if contract.get("bridge_refresh_required")),
        "bridge_reachable_count": sum(1 for contract in requested if contract.get("bridge_reachable")),
        "read_only_result_refreshed_count": sum(
            1 for contract in requested if contract.get("read_only_result_refreshed")
        ),
        "bridge_refresh_satisfied_count": sum(
            1 for contract in requested if contract.get("bridge_refresh_satisfied")
        ),
        "canary_execution_allowed_after_refresh_count": sum(
            1 for contract in requested if contract.get("canary_execution_allowed_after_refresh")
        ),
        "durable_executor_may_open_after_refresh_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_after_refresh")
        ),
        "authoring_command_allowed_count": sum(1 for contract in requested if contract.get("authoring_command_allowed")),
        "save_or_delete_allowed_count": sum(1 for contract in requested if contract.get("save_or_delete_allowed")),
        "cleanup_command_allowed_count": sum(1 for contract in requested if contract.get("cleanup_command_allowed")),
        "live_authoring_command_count": sum(contract.get("live_authoring_command_count", 0) for contract in requested),
        "live_save_or_delete_command_count": sum(
            contract.get("live_save_or_delete_command_count", 0) for contract in requested
        ),
        "live_cleanup_command_count": sum(contract.get("live_cleanup_command_count", 0) for contract in requested),
    }
