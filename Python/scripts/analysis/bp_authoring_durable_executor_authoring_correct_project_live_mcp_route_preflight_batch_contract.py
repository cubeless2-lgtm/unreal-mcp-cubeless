#!/usr/bin/env python
"""
Sections 369-376 durable executor correct-project live MCP route preflight.

This contract follows the node-level graph fixture route preflight. It records
the configuration and read-only bridge evidence needed before any live MCP
node-authoring route can be used. The local .mcp.json and sibling server path
are valid, but the current live bridge read-only probe does not find the
correct-project temp fixture. Activation, node authoring, compile, save, graph
repair, delete, rename, overwrite, cleanup, and production writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract as node_route


DURABLE_EXECUTOR_AUTHORING_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_BATCH_SCHEMA = (
    "section_369_376_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_BATCH_SUMMARY_SCHEMA = (
    "section_369_376_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_summary_v1"
)
CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_RESULT_SCHEMA = (
    "section_369_376_correct_project_live_mcp_route_preflight_result_v1"
)
SECTION_361_368_NODE_LEVEL_ROUTE_PREFLIGHT_SUMMARY_SCHEMA = (
    node_route
    .DURABLE_EXECUTOR_AUTHORING_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_BATCH_SUMMARY_SCHEMA
)
DEFAULT_PROJECT_FILE_PATH = node_route.DEFAULT_PROJECT_FILE_PATH
DEFAULT_FIXTURE_ASSET_PATH = node_route.DEFAULT_FIXTURE_ASSET_PATH
DEFAULT_MCP_SERVER_NAME = "unrealMCP"
DEFAULT_MCP_COMMAND = "uv"
DEFAULT_MCP_DIRECTORY_ARG = "../unreal-mcp-cubeless/Python"
DEFAULT_MCP_SERVER_SCRIPT = "unreal_mcp_server.py"
DEFAULT_EXPECTED_BRIDGE_HOST = "127.0.0.1"
DEFAULT_EXPECTED_BRIDGE_PORT = 55557
DEFAULT_PROBE_COMMAND = "list_blueprint_nodes"
DEFAULT_LIVE_MCP_ERROR = node_route.DEFAULT_LIVE_MCP_ERROR

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_node_level_graph_fixture_route_preflight_batch_count",
    "section_361_node_level_route_preflight_checkpoint_satisfied_count",
    "section_362_headless_fixture_readback_verified_count",
    "section_363_python_node_object_construction_probe_recorded_count",
    "section_364_python_node_mutation_api_absent_verified_count",
    "section_365_live_mcp_correct_project_route_blocked_count",
    "section_366_actual_node_authoring_outputs_blocked_count",
    "section_367_node_level_preflight_no_write_boundary_verified_count",
    "section_368_node_level_graph_fixture_route_preflight_release_ready_count",
    "node_level_graph_fixture_route_preflight_ready_count",
    "node_level_actual_fixture_still_blocked_count",
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    node_route
    .BLOCKED_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
)

CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_PATH_COUNT_KEYS = (
    "section_369_correct_project_live_mcp_route_checkpoint_satisfied_count",
    "section_370_mcp_config_preflight_verified_count",
    "section_371_sibling_server_path_verified_count",
    "section_372_live_bridge_read_only_probe_recorded_count",
    "section_373_live_bridge_correct_project_not_verified_count",
    "section_374_live_mcp_activation_outputs_blocked_count",
    "section_375_correct_project_live_mcp_route_no_write_boundary_verified_count",
    "section_376_correct_project_live_mcp_route_preflight_release_ready_count",
    "correct_project_live_mcp_route_preflight_ready_count",
    "correct_project_live_mcp_activation_still_blocked_count",
)

BLOCKED_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS = (
    "live_mcp_activation_command_dispatched_count",
    "live_mcp_activation_command_executed_count",
    "node_authoring_command_dispatched_count",
    "node_authoring_command_executed_count",
    "add_blueprint_call_function_node_dispatched_count",
    "add_blueprint_call_function_node_executed_count",
    "graph_node_added_count",
    "graph_layout_mutation_performed_count",
    "node_position_write_performed_count",
    "pin_connection_write_performed_count",
    "compile_executed_count",
    "save_executed_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
    "graph_repair_command_dispatched_count",
    "graph_repair_command_executed_count",
    "cleanup_allowed_count",
    "cleanup_executed_count",
    "delete_asset_allowed_count",
    "delete_asset_executed_output_count",
    "rename_asset_allowed_count",
    "rename_command_dispatched_count",
    "rename_command_executed_count",
    "overwrite_allowed_count",
    "overwrite_executed_count",
    "production_path_write_allowed_count",
    "production_path_write_executed_count",
)
BLOCKED_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_RESULT_KEYS = (
    "live_mcp_activation_command_dispatched",
    "live_mcp_activation_command_executed",
    "node_authoring_command_dispatched",
    "node_authoring_command_executed",
    "add_blueprint_call_function_node_dispatched",
    "add_blueprint_call_function_node_executed",
    "graph_node_added",
    "graph_layout_mutation_performed",
    "node_position_write_performed",
    "pin_connection_write_performed",
    "compile_executed",
    "save_executed",
    "asset_write_performed",
    "package_dirty_marked",
    "graph_repair_command_dispatched",
    "graph_repair_command_executed",
    "cleanup_allowed",
    "cleanup_executed",
    "delete_asset_allowed",
    "delete_asset_executed_output",
    "rename_asset_allowed",
    "rename_command_dispatched",
    "rename_command_executed",
    "overwrite_allowed",
    "overwrite_executed",
    "production_path_write_allowed",
    "production_path_write_executed",
)


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _count_is_one(summary: Dict[str, Any], key: str) -> bool:
    return bool(summary.get(key) == 1)


def _count_is_zero(summary: Dict[str, Any], key: str) -> bool:
    return bool(int(summary.get(key, 0) or 0) == 0)


def build_correct_project_live_mcp_route_preflight_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    mcp_server_name: str = DEFAULT_MCP_SERVER_NAME,
    mcp_command: str = DEFAULT_MCP_COMMAND,
    mcp_directory_arg: str = DEFAULT_MCP_DIRECTORY_ARG,
    mcp_server_script: str = DEFAULT_MCP_SERVER_SCRIPT,
    mcp_server_defined: bool = True,
    mcp_command_matches: bool = True,
    mcp_args_match_expected: bool = True,
    mcp_directory_resolves: bool = True,
    mcp_server_script_exists: bool = True,
    expected_bridge_host: str = DEFAULT_EXPECTED_BRIDGE_HOST,
    expected_bridge_port: int = DEFAULT_EXPECTED_BRIDGE_PORT,
    read_only_probe_attempted: bool = True,
    read_only_probe_command: str = DEFAULT_PROBE_COMMAND,
    read_only_probe_target_asset_path: str = DEFAULT_FIXTURE_ASSET_PATH,
    read_only_probe_include_pins: bool = True,
    live_bridge_responded: bool = True,
    live_bridge_fixture_found: bool = False,
    live_bridge_correct_project_verified: bool = False,
    live_bridge_correct_project_not_verified: bool = True,
    live_bridge_error: str = DEFAULT_LIVE_MCP_ERROR,
    live_mcp_activation_still_blocked: bool = True,
    target_dirty_after: bool = False,
    dirty_content_after: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
    live_mcp_activation_command_dispatched: bool = False,
    live_mcp_activation_command_executed: bool = False,
    node_authoring_command_dispatched: bool = False,
    node_authoring_command_executed: bool = False,
    add_blueprint_call_function_node_dispatched: bool = False,
    add_blueprint_call_function_node_executed: bool = False,
    graph_node_added: bool = False,
    graph_layout_mutation_performed: bool = False,
    node_position_write_performed: bool = False,
    pin_connection_write_performed: bool = False,
    compile_executed: bool = False,
    save_executed: bool = False,
    asset_write_performed: bool = False,
    package_dirty_marked: bool = False,
    graph_repair_command_dispatched: bool = False,
    graph_repair_command_executed: bool = False,
    cleanup_allowed: bool = False,
    cleanup_executed: bool = False,
    delete_asset_allowed: bool = False,
    delete_asset_executed_output: bool = False,
    rename_asset_allowed: bool = False,
    rename_command_dispatched: bool = False,
    rename_command_executed: bool = False,
    overwrite_allowed: bool = False,
    overwrite_executed: bool = False,
    production_path_write_allowed: bool = False,
    production_path_write_executed: bool = False,
    error: str | None = None,
) -> Dict[str, Any]:
    return {
        "schema": CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_RESULT_SCHEMA,
        "project_file_path": project_file_path,
        "mcp_server_name": mcp_server_name,
        "mcp_command": mcp_command,
        "mcp_directory_arg": mcp_directory_arg,
        "mcp_server_script": mcp_server_script,
        "mcp_server_defined": mcp_server_defined,
        "mcp_command_matches": mcp_command_matches,
        "mcp_args_match_expected": mcp_args_match_expected,
        "mcp_directory_resolves": mcp_directory_resolves,
        "mcp_server_script_exists": mcp_server_script_exists,
        "expected_bridge_host": expected_bridge_host,
        "expected_bridge_port": expected_bridge_port,
        "read_only_probe_attempted": read_only_probe_attempted,
        "read_only_probe_command": read_only_probe_command,
        "read_only_probe_target_asset_path": read_only_probe_target_asset_path,
        "read_only_probe_include_pins": read_only_probe_include_pins,
        "live_bridge_responded": live_bridge_responded,
        "live_bridge_fixture_found": live_bridge_fixture_found,
        "live_bridge_correct_project_verified": (
            live_bridge_correct_project_verified
        ),
        "live_bridge_correct_project_not_verified": (
            live_bridge_correct_project_not_verified
        ),
        "live_bridge_error": live_bridge_error,
        "live_mcp_activation_still_blocked": live_mcp_activation_still_blocked,
        "target_dirty_after": target_dirty_after,
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_preserved": external_dirty_preserved,
        "live_mcp_activation_command_dispatched": (
            live_mcp_activation_command_dispatched
        ),
        "live_mcp_activation_command_executed": (
            live_mcp_activation_command_executed
        ),
        "node_authoring_command_dispatched": node_authoring_command_dispatched,
        "node_authoring_command_executed": node_authoring_command_executed,
        "add_blueprint_call_function_node_dispatched": (
            add_blueprint_call_function_node_dispatched
        ),
        "add_blueprint_call_function_node_executed": (
            add_blueprint_call_function_node_executed
        ),
        "graph_node_added": graph_node_added,
        "graph_layout_mutation_performed": graph_layout_mutation_performed,
        "node_position_write_performed": node_position_write_performed,
        "pin_connection_write_performed": pin_connection_write_performed,
        "compile_executed": compile_executed,
        "save_executed": save_executed,
        "asset_write_performed": asset_write_performed,
        "package_dirty_marked": package_dirty_marked,
        "graph_repair_command_dispatched": graph_repair_command_dispatched,
        "graph_repair_command_executed": graph_repair_command_executed,
        "cleanup_allowed": cleanup_allowed,
        "cleanup_executed": cleanup_executed,
        "delete_asset_allowed": delete_asset_allowed,
        "delete_asset_executed_output": delete_asset_executed_output,
        "rename_asset_allowed": rename_asset_allowed,
        "rename_command_dispatched": rename_command_dispatched,
        "rename_command_executed": rename_command_executed,
        "overwrite_allowed": overwrite_allowed,
        "overwrite_executed": overwrite_executed,
        "production_path_write_allowed": production_path_write_allowed,
        "production_path_write_executed": production_path_write_executed,
        "error": error,
    }


def build_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract(
    requested: bool,
    section_361_368_node_level_route_preflight_summary: Dict[str, Any],
    correct_project_live_mcp_route_preflight_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_361_368_summary_schema_matches = bool(
        section_361_368_node_level_route_preflight_summary.get("schema")
        == SECTION_361_368_NODE_LEVEL_ROUTE_PREFLIGHT_SUMMARY_SCHEMA
    )
    section_361_368_summary_passed = bool(
        section_361_368_node_level_route_preflight_summary.get("status")
        == "passed"
    )
    upstream_node_route_preflight_ready = all(
        _count_is_one(section_361_368_node_level_route_preflight_summary, key)
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(section_361_368_node_level_route_preflight_summary, key)
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        correct_project_live_mcp_route_preflight_result.get("schema")
        == CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_361_368_summary_schema_matches
        and section_361_368_summary_passed
        and upstream_node_route_preflight_ready
        and upstream_outputs_closed
    )
    mcp_config_preflight_verified = bool(
        correct_project_live_mcp_route_preflight_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and correct_project_live_mcp_route_preflight_result.get(
            "mcp_server_name"
        )
        == DEFAULT_MCP_SERVER_NAME
        and correct_project_live_mcp_route_preflight_result.get(
            "mcp_server_defined"
        )
        and correct_project_live_mcp_route_preflight_result.get(
            "mcp_command"
        )
        == DEFAULT_MCP_COMMAND
        and correct_project_live_mcp_route_preflight_result.get(
            "mcp_command_matches"
        )
        and correct_project_live_mcp_route_preflight_result.get(
            "mcp_args_match_expected"
        )
        and correct_project_live_mcp_route_preflight_result.get(
            "expected_bridge_host"
        )
        == DEFAULT_EXPECTED_BRIDGE_HOST
        and int(
            correct_project_live_mcp_route_preflight_result.get(
                "expected_bridge_port", 0
            )
            or 0
        )
        == DEFAULT_EXPECTED_BRIDGE_PORT
    )
    sibling_server_path_verified = bool(
        correct_project_live_mcp_route_preflight_result.get(
            "mcp_directory_arg"
        )
        == DEFAULT_MCP_DIRECTORY_ARG
        and correct_project_live_mcp_route_preflight_result.get(
            "mcp_directory_resolves"
        )
        and correct_project_live_mcp_route_preflight_result.get(
            "mcp_server_script"
        )
        == DEFAULT_MCP_SERVER_SCRIPT
        and correct_project_live_mcp_route_preflight_result.get(
            "mcp_server_script_exists"
        )
    )
    read_only_probe_recorded = bool(
        correct_project_live_mcp_route_preflight_result.get(
            "read_only_probe_attempted"
        )
        and correct_project_live_mcp_route_preflight_result.get(
            "read_only_probe_command"
        )
        == DEFAULT_PROBE_COMMAND
        and correct_project_live_mcp_route_preflight_result.get(
            "read_only_probe_target_asset_path"
        )
        == DEFAULT_FIXTURE_ASSET_PATH
        and correct_project_live_mcp_route_preflight_result.get(
            "read_only_probe_include_pins"
        )
        and correct_project_live_mcp_route_preflight_result.get(
            "live_bridge_responded"
        )
    )
    live_bridge_correct_project_not_verified = bool(
        read_only_probe_recorded
        and not correct_project_live_mcp_route_preflight_result.get(
            "live_bridge_fixture_found"
        )
        and not correct_project_live_mcp_route_preflight_result.get(
            "live_bridge_correct_project_verified"
        )
        and correct_project_live_mcp_route_preflight_result.get(
            "live_bridge_correct_project_not_verified"
        )
        and correct_project_live_mcp_route_preflight_result.get(
            "live_mcp_activation_still_blocked"
        )
        and "Blueprint not found"
        in str(
            correct_project_live_mcp_route_preflight_result.get(
                "live_bridge_error", ""
            )
        )
    )
    activation_outputs_blocked = all(
        not correct_project_live_mcp_route_preflight_result.get(key)
        for key in BLOCKED_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        activation_outputs_blocked
        and not correct_project_live_mcp_route_preflight_result.get(
            "target_dirty_after"
        )
        and not correct_project_live_mcp_route_preflight_result.get(
            "dirty_content_after"
        )
        and not correct_project_live_mcp_route_preflight_result.get(
            "dirty_maps_after"
        )
        and correct_project_live_mcp_route_preflight_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        correct_project_live_mcp_route_preflight_result.get("error")
        in (None, "")
    )
    route_preflight_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and mcp_config_preflight_verified
        and sibling_server_path_verified
        and read_only_probe_recorded
        and live_bridge_correct_project_not_verified
        and activation_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_correct_project_live_mcp_route_preflight_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_361_368_summary_schema_matches": (
            section_361_368_summary_schema_matches
        ),
        "section_361_368_summary_passed": section_361_368_summary_passed,
        "section_361_368_node_level_route_preflight_ready": (
            upstream_node_route_preflight_ready
        ),
        "section_361_368_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "correct_project_live_mcp_route_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "mcp_config_preflight_verified": mcp_config_preflight_verified,
        "sibling_server_path_verified": sibling_server_path_verified,
        "live_bridge_read_only_probe_recorded": read_only_probe_recorded,
        "live_bridge_correct_project_not_verified": (
            live_bridge_correct_project_not_verified
        ),
        "live_mcp_activation_outputs_blocked": activation_outputs_blocked,
        "correct_project_live_mcp_route_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_369_correct_project_live_mcp_route_checkpoint_satisfied": (
            route_preflight_ready
        ),
        "section_370_mcp_config_preflight_verified": route_preflight_ready,
        "section_371_sibling_server_path_verified": route_preflight_ready,
        "section_372_live_bridge_read_only_probe_recorded": (
            route_preflight_ready
        ),
        "section_373_live_bridge_correct_project_not_verified": (
            route_preflight_ready
        ),
        "section_374_live_mcp_activation_outputs_blocked": (
            route_preflight_ready
        ),
        "section_375_correct_project_live_mcp_route_no_write_boundary_verified": (
            route_preflight_ready
        ),
        "section_376_correct_project_live_mcp_route_preflight_release_ready": (
            route_preflight_ready
        ),
        "correct_project_live_mcp_route_preflight_ready": route_preflight_ready,
        "correct_project_live_mcp_activation_still_blocked": (
            route_preflight_ready
        ),
        "final_durable_release_ready": route_preflight_ready,
        **{
            key: 1 if route_preflight_ready else 0
            for key in CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_correct_project_live_mcp_route_preflight_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "correct_project_live_mcp_route_preflight_ready"
            )
            == len(requested)
            and _truthy_count(
                requested, "correct_project_live_mcp_activation_still_blocked"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_correct_project_live_mcp_route_preflight_batch_count": (
            len(requested)
        ),
        "section_361_368_summary_schema_matches_count": _truthy_count(
            requested, "section_361_368_summary_schema_matches"
        ),
        "section_361_368_summary_passed_count": _truthy_count(
            requested, "section_361_368_summary_passed"
        ),
        "section_361_368_node_level_route_preflight_ready_count": (
            _truthy_count(
                requested, "section_361_368_node_level_route_preflight_ready"
            )
        ),
        "section_361_368_outputs_closed_count": _truthy_count(
            requested, "section_361_368_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "correct_project_live_mcp_route_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "correct_project_live_mcp_route_checkpoint_satisfied",
            )
        ),
        "mcp_config_preflight_verified_count": _truthy_count(
            requested, "mcp_config_preflight_verified"
        ),
        "sibling_server_path_verified_count": _truthy_count(
            requested, "sibling_server_path_verified"
        ),
        "live_bridge_read_only_probe_recorded_count": _truthy_count(
            requested, "live_bridge_read_only_probe_recorded"
        ),
        "live_bridge_correct_project_not_verified_count": _truthy_count(
            requested, "live_bridge_correct_project_not_verified"
        ),
        "live_mcp_activation_outputs_blocked_count": _truthy_count(
            requested, "live_mcp_activation_outputs_blocked"
        ),
        "correct_project_live_mcp_route_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "correct_project_live_mcp_route_no_write_boundary_verified",
            )
        ),
        "result_has_no_error_count": _truthy_count(
            requested, "result_has_no_error"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
    }
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
        }
    )
    return summary
