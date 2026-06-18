#!/usr/bin/env python
"""
Sections 361-368 durable executor node-level graph fixture route preflight.

This contract follows the post-recreation non-empty graph fixture gate. It
records the next node-level authoring preflight without adding nodes. The
correct-project headless Python route can load the fixture and construct a
K2Node_CallFunction object, but does not expose the mutation APIs required to
make a valid graph node. The live MCP route is also blocked because the bridge
does not find the correct-project temp fixture. Actual node authoring, compile,
save, graph repair, delete, rename, overwrite, cleanup, and production writes
therefore remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract as non_empty_fixture
import project_paths


DURABLE_EXECUTOR_AUTHORING_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_BATCH_SCHEMA = (
    "section_361_368_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_BATCH_SUMMARY_SCHEMA = (
    "section_361_368_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_summary_v1"
)
NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_RESULT_SCHEMA = (
    "section_361_368_node_level_graph_fixture_route_preflight_result_v1"
)
SECTION_353_360_NON_EMPTY_GRAPH_FIXTURE_SUMMARY_SCHEMA = (
    non_empty_fixture
    .DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_NON_EMPTY_GRAPH_FIXTURE_BATCH_SUMMARY_SCHEMA
)
DEFAULT_FIXTURE_ASSET_PATH = non_empty_fixture.DEFAULT_FIXTURE_ASSET_PATH
DEFAULT_FIXTURE_ROOT = non_empty_fixture.DEFAULT_FIXTURE_ROOT
DEFAULT_FUNCTION_GRAPH_NAME = non_empty_fixture.DEFAULT_FUNCTION_GRAPH_NAME
DEFAULT_PROJECT_FILE_PATH = project_paths.default_cubeless_uproject()
DEFAULT_LIVE_MCP_ERROR = (
    "Blueprint not found: "
    "/Game/_MCP_Temp/DurableSaveGate/BP_DurableGraphDiagnosticsFixture"
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_post_recreation_non_empty_graph_fixture_batch_count",
    "section_353_non_empty_graph_fixture_checkpoint_satisfied_count",
    "section_354_fixture_target_scope_verified_count",
    "section_355_fixture_actor_blueprint_create_or_update_executed_count",
    "section_356_function_graph_inventory_non_empty_verified_count",
    "section_357_fixture_compile_save_readback_verified_count",
    "section_358_node_level_repair_still_blocked_count",
    "section_359_non_fixture_outputs_closed_count",
    "section_360_non_empty_graph_fixture_release_ready_count",
    "post_recreation_non_empty_graph_fixture_ready_count",
    "post_recreation_node_level_repair_fixture_still_missing_count",
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    non_empty_fixture.BLOCKED_NON_EMPTY_GRAPH_FIXTURE_OUTPUT_COUNT_KEYS
)

NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_PATH_COUNT_KEYS = (
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
)

BLOCKED_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS = (
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
BLOCKED_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_RESULT_KEYS = (
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


def build_node_level_graph_fixture_route_preflight_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    fixture_asset_path: str = DEFAULT_FIXTURE_ASSET_PATH,
    fixture_root: str = DEFAULT_FIXTURE_ROOT,
    fixture_under_expected_root: bool = True,
    headless_asset_loaded: bool = True,
    headless_graph_loaded: bool = True,
    function_graph_name_after: str = DEFAULT_FUNCTION_GRAPH_NAME,
    function_graph_count_after: int = 1,
    function_graph_node_count_before: int = 0,
    python_k2_call_function_class_exists: bool = True,
    python_new_object_k2_node_succeeded: bool = True,
    python_node_position_api_available: bool = False,
    python_pin_access_api_available: bool = False,
    python_allocate_default_pins_api_available: bool = False,
    python_set_from_function_api_available: bool = False,
    python_graph_add_node_api_available: bool = False,
    live_mcp_list_nodes_attempted: bool = True,
    live_mcp_fixture_found: bool = False,
    live_mcp_route_correct_project_verified: bool = False,
    live_mcp_node_authoring_route_blocked: bool = True,
    live_mcp_error: str = DEFAULT_LIVE_MCP_ERROR,
    target_dirty_after: bool = False,
    dirty_content_after: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
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
        "schema": NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_RESULT_SCHEMA,
        "project_file_path": project_file_path,
        "fixture_asset_path": fixture_asset_path,
        "fixture_root": fixture_root,
        "fixture_under_expected_root": fixture_under_expected_root,
        "headless_asset_loaded": headless_asset_loaded,
        "headless_graph_loaded": headless_graph_loaded,
        "function_graph_name_after": function_graph_name_after,
        "function_graph_count_after": function_graph_count_after,
        "function_graph_node_count_before": function_graph_node_count_before,
        "python_k2_call_function_class_exists": (
            python_k2_call_function_class_exists
        ),
        "python_new_object_k2_node_succeeded": (
            python_new_object_k2_node_succeeded
        ),
        "python_node_position_api_available": (
            python_node_position_api_available
        ),
        "python_pin_access_api_available": python_pin_access_api_available,
        "python_allocate_default_pins_api_available": (
            python_allocate_default_pins_api_available
        ),
        "python_set_from_function_api_available": (
            python_set_from_function_api_available
        ),
        "python_graph_add_node_api_available": python_graph_add_node_api_available,
        "live_mcp_list_nodes_attempted": live_mcp_list_nodes_attempted,
        "live_mcp_fixture_found": live_mcp_fixture_found,
        "live_mcp_route_correct_project_verified": (
            live_mcp_route_correct_project_verified
        ),
        "live_mcp_node_authoring_route_blocked": (
            live_mcp_node_authoring_route_blocked
        ),
        "live_mcp_error": live_mcp_error,
        "target_dirty_after": target_dirty_after,
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_preserved": external_dirty_preserved,
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


def build_durable_executor_authoring_node_level_graph_fixture_route_preflight_batch_contract(
    requested: bool,
    section_353_360_non_empty_graph_fixture_summary: Dict[str, Any],
    node_level_graph_fixture_route_preflight_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_353_360_summary_schema_matches = bool(
        section_353_360_non_empty_graph_fixture_summary.get("schema")
        == SECTION_353_360_NON_EMPTY_GRAPH_FIXTURE_SUMMARY_SCHEMA
    )
    section_353_360_summary_passed = bool(
        section_353_360_non_empty_graph_fixture_summary.get("status")
        == "passed"
    )
    upstream_non_empty_fixture_ready = all(
        _count_is_one(section_353_360_non_empty_graph_fixture_summary, key)
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(section_353_360_non_empty_graph_fixture_summary, key)
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        node_level_graph_fixture_route_preflight_result.get("schema")
        == NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_353_360_summary_schema_matches
        and section_353_360_summary_passed
        and upstream_non_empty_fixture_ready
        and upstream_outputs_closed
    )
    fixture_target_scope_verified = bool(
        node_level_graph_fixture_route_preflight_result.get(
            "fixture_asset_path"
        )
        == DEFAULT_FIXTURE_ASSET_PATH
        and node_level_graph_fixture_route_preflight_result.get(
            "fixture_root"
        )
        == DEFAULT_FIXTURE_ROOT
        and node_level_graph_fixture_route_preflight_result.get(
            "fixture_under_expected_root"
        )
        and str(
            node_level_graph_fixture_route_preflight_result.get(
                "fixture_asset_path", ""
            )
        ).startswith("/Game/_MCP_Temp/")
    )
    headless_fixture_readback_verified = bool(
        node_level_graph_fixture_route_preflight_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and fixture_target_scope_verified
        and node_level_graph_fixture_route_preflight_result.get(
            "headless_asset_loaded"
        )
        and node_level_graph_fixture_route_preflight_result.get(
            "headless_graph_loaded"
        )
        and node_level_graph_fixture_route_preflight_result.get(
            "function_graph_name_after"
        )
        == DEFAULT_FUNCTION_GRAPH_NAME
        and int(
            node_level_graph_fixture_route_preflight_result.get(
                "function_graph_count_after", 0
            )
            or 0
        )
        >= 1
        and int(
            node_level_graph_fixture_route_preflight_result.get(
                "function_graph_node_count_before", -1
            )
            or 0
        )
        == 0
    )
    python_node_object_construction_probe_recorded = bool(
        node_level_graph_fixture_route_preflight_result.get(
            "python_k2_call_function_class_exists"
        )
        and node_level_graph_fixture_route_preflight_result.get(
            "python_new_object_k2_node_succeeded"
        )
    )
    python_node_mutation_api_absent_verified = bool(
        python_node_object_construction_probe_recorded
        and not node_level_graph_fixture_route_preflight_result.get(
            "python_node_position_api_available"
        )
        and not node_level_graph_fixture_route_preflight_result.get(
            "python_pin_access_api_available"
        )
        and not node_level_graph_fixture_route_preflight_result.get(
            "python_allocate_default_pins_api_available"
        )
        and not node_level_graph_fixture_route_preflight_result.get(
            "python_set_from_function_api_available"
        )
        and not node_level_graph_fixture_route_preflight_result.get(
            "python_graph_add_node_api_available"
        )
    )
    live_mcp_correct_project_route_blocked = bool(
        node_level_graph_fixture_route_preflight_result.get(
            "live_mcp_list_nodes_attempted"
        )
        and not node_level_graph_fixture_route_preflight_result.get(
            "live_mcp_fixture_found"
        )
        and not node_level_graph_fixture_route_preflight_result.get(
            "live_mcp_route_correct_project_verified"
        )
        and node_level_graph_fixture_route_preflight_result.get(
            "live_mcp_node_authoring_route_blocked"
        )
        and "Blueprint not found"
        in str(
            node_level_graph_fixture_route_preflight_result.get(
                "live_mcp_error", ""
            )
        )
    )
    actual_node_authoring_outputs_blocked = all(
        not node_level_graph_fixture_route_preflight_result.get(key)
        for key in BLOCKED_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        actual_node_authoring_outputs_blocked
        and not node_level_graph_fixture_route_preflight_result.get(
            "target_dirty_after"
        )
        and not node_level_graph_fixture_route_preflight_result.get(
            "dirty_content_after"
        )
        and not node_level_graph_fixture_route_preflight_result.get(
            "dirty_maps_after"
        )
        and node_level_graph_fixture_route_preflight_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        node_level_graph_fixture_route_preflight_result.get("error")
        in (None, "")
    )
    route_preflight_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and headless_fixture_readback_verified
        and python_node_object_construction_probe_recorded
        and python_node_mutation_api_absent_verified
        and live_mcp_correct_project_route_blocked
        and actual_node_authoring_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_node_level_graph_fixture_route_preflight_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_353_360_summary_schema_matches": (
            section_353_360_summary_schema_matches
        ),
        "section_353_360_summary_passed": section_353_360_summary_passed,
        "section_353_360_non_empty_graph_fixture_ready": (
            upstream_non_empty_fixture_ready
        ),
        "section_353_360_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "node_level_route_preflight_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "fixture_target_scope_verified": fixture_target_scope_verified,
        "headless_fixture_readback_verified": (
            headless_fixture_readback_verified
        ),
        "python_node_object_construction_probe_recorded": (
            python_node_object_construction_probe_recorded
        ),
        "python_node_mutation_api_absent_verified": (
            python_node_mutation_api_absent_verified
        ),
        "live_mcp_correct_project_route_blocked": (
            live_mcp_correct_project_route_blocked
        ),
        "actual_node_authoring_outputs_blocked": (
            actual_node_authoring_outputs_blocked
        ),
        "node_level_preflight_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_361_node_level_route_preflight_checkpoint_satisfied": (
            route_preflight_ready
        ),
        "section_362_headless_fixture_readback_verified": route_preflight_ready,
        "section_363_python_node_object_construction_probe_recorded": (
            route_preflight_ready
        ),
        "section_364_python_node_mutation_api_absent_verified": (
            route_preflight_ready
        ),
        "section_365_live_mcp_correct_project_route_blocked": (
            route_preflight_ready
        ),
        "section_366_actual_node_authoring_outputs_blocked": (
            route_preflight_ready
        ),
        "section_367_node_level_preflight_no_write_boundary_verified": (
            route_preflight_ready
        ),
        "section_368_node_level_graph_fixture_route_preflight_release_ready": (
            route_preflight_ready
        ),
        "node_level_graph_fixture_route_preflight_ready": (
            route_preflight_ready
        ),
        "node_level_actual_fixture_still_blocked": route_preflight_ready,
        "final_durable_release_ready": route_preflight_ready,
        **{
            key: 1 if route_preflight_ready else 0
            for key in NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_node_level_graph_fixture_route_preflight_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "node_level_graph_fixture_route_preflight_ready"
            )
            == len(requested)
            and _truthy_count(
                requested, "node_level_actual_fixture_still_blocked"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_node_level_graph_fixture_route_preflight_batch_count": (
            len(requested)
        ),
        "section_353_360_summary_schema_matches_count": _truthy_count(
            requested, "section_353_360_summary_schema_matches"
        ),
        "section_353_360_summary_passed_count": _truthy_count(
            requested, "section_353_360_summary_passed"
        ),
        "section_353_360_non_empty_graph_fixture_ready_count": (
            _truthy_count(
                requested, "section_353_360_non_empty_graph_fixture_ready"
            )
        ),
        "section_353_360_outputs_closed_count": _truthy_count(
            requested, "section_353_360_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "node_level_route_preflight_checkpoint_satisfied_count": (
            _truthy_count(
                requested, "node_level_route_preflight_checkpoint_satisfied"
            )
        ),
        "fixture_target_scope_verified_count": _truthy_count(
            requested, "fixture_target_scope_verified"
        ),
        "headless_fixture_readback_verified_count": _truthy_count(
            requested, "headless_fixture_readback_verified"
        ),
        "python_node_object_construction_probe_recorded_count": (
            _truthy_count(
                requested, "python_node_object_construction_probe_recorded"
            )
        ),
        "python_node_mutation_api_absent_verified_count": _truthy_count(
            requested, "python_node_mutation_api_absent_verified"
        ),
        "live_mcp_correct_project_route_blocked_count": _truthy_count(
            requested, "live_mcp_correct_project_route_blocked"
        ),
        "actual_node_authoring_outputs_blocked_count": _truthy_count(
            requested, "actual_node_authoring_outputs_blocked"
        ),
        "node_level_preflight_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "node_level_preflight_no_write_boundary_verified",
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
            for key in NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_NODE_LEVEL_GRAPH_FIXTURE_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
        }
    )
    return summary
