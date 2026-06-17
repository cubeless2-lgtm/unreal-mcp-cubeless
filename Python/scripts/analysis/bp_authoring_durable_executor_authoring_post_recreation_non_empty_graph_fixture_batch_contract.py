#!/usr/bin/env python
"""
Sections 353-360 durable executor post-recreation non-empty graph fixture batch.

This contract follows the graph-repair dry-run gate. It admits one isolated
temporary Actor Blueprint fixture under /Game/_MCP_Temp with a named function
graph so diagnostics can exercise a non-empty graph inventory. The current
fixture graph has no nodes, so node-level repair remains blocked for a later
contract. Production writes, delete, rename, overwrite, cleanup, and actual
graph repair remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract as graph_repair


DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_NON_EMPTY_GRAPH_FIXTURE_BATCH_SCHEMA = (
    "section_353_360_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_NON_EMPTY_GRAPH_FIXTURE_BATCH_SUMMARY_SCHEMA = (
    "section_353_360_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_summary_v1"
)
POST_RECREATION_NON_EMPTY_GRAPH_FIXTURE_RESULT_SCHEMA = (
    "section_353_360_post_recreation_non_empty_graph_fixture_result_v1"
)
SECTION_345_352_GRAPH_REPAIR_EXECUTION_DRY_RUN_SUMMARY_SCHEMA = (
    graph_repair
    .DURABLE_EXECUTOR_AUTHORING_GRAPH_REPAIR_EXECUTION_DRY_RUN_BATCH_SUMMARY_SCHEMA
)
DEFAULT_FIXTURE_ASSET_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/BP_DurableGraphDiagnosticsFixture"
)
DEFAULT_FIXTURE_ROOT = "/Game/_MCP_Temp/DurableSaveGate"
DEFAULT_FIXTURE_BLUEPRINT_CLASS_NAME = "Blueprint"
DEFAULT_FIXTURE_GENERATED_CLASS_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/BP_DurableGraphDiagnosticsFixture.BP_DurableGraphDiagnosticsFixture_C"
)
DEFAULT_FIXTURE_CDO_CLASS_NAME = "BP_DurableGraphDiagnosticsFixture_C"
DEFAULT_FUNCTION_GRAPH_NAME = "MCPNonEmptyDiagnosticsFunction"
DEFAULT_CONTENT_FILE_SIZE = 26264
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_graph_repair_execution_dry_run_batch_count",
    "section_345_graph_repair_dry_run_checkpoint_satisfied_count",
    "section_346_graph_repair_dry_run_command_admitted_count",
    "section_347_graph_repair_dry_run_command_executed_count",
    "section_348_empty_graph_noop_repair_verified_count",
    "section_349_node_pin_mutation_outputs_blocked_count",
    "section_350_compile_save_outputs_blocked_count",
    "section_351_graph_repair_dry_run_no_write_boundary_verified_count",
    "section_352_graph_repair_execution_dry_run_release_ready_count",
    "graph_repair_execution_dry_run_ready_count",
    "graph_repair_actual_execution_still_blocked_count",
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    graph_repair.BLOCKED_GRAPH_REPAIR_EXECUTION_DRY_RUN_OUTPUT_COUNT_KEYS
)
POST_RECREATION_NON_EMPTY_GRAPH_FIXTURE_PATH_COUNT_KEYS = (
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
)
BLOCKED_NON_EMPTY_GRAPH_FIXTURE_OUTPUT_COUNT_KEYS = (
    "graph_repair_command_dispatched_count",
    "graph_repair_command_executed_count",
    "graph_layout_mutation_performed_count",
    "node_position_write_performed_count",
    "pin_connection_write_performed_count",
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
BLOCKED_NON_EMPTY_GRAPH_FIXTURE_RESULT_KEYS = (
    "graph_repair_command_dispatched",
    "graph_repair_command_executed",
    "graph_layout_mutation_performed",
    "node_position_write_performed",
    "pin_connection_write_performed",
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


def build_post_recreation_non_empty_graph_fixture_result(
    *,
    fixture_asset_path: str = DEFAULT_FIXTURE_ASSET_PATH,
    fixture_root: str = DEFAULT_FIXTURE_ROOT,
    fixture_under_expected_root: bool = True,
    asset_created: bool = True,
    asset_reused_on_final_readback: bool = True,
    fixture_create_or_update_executed: bool = True,
    asset_exists_after: bool = True,
    asset_data_valid_after: bool = True,
    blueprint_class_name: str = DEFAULT_FIXTURE_BLUEPRINT_CLASS_NAME,
    generated_class_path: str = DEFAULT_FIXTURE_GENERATED_CLASS_PATH,
    cdo_class_name: str = DEFAULT_FIXTURE_CDO_CLASS_NAME,
    cdo_is_actor: bool = True,
    content_file_exists_after: bool = True,
    content_file_size_after: int = DEFAULT_CONTENT_FILE_SIZE,
    function_graph_name_after: str = DEFAULT_FUNCTION_GRAPH_NAME,
    function_graph_exists_after: bool = True,
    function_graph_count_after: int = 1,
    function_graph_inventory_non_empty_after: bool = True,
    function_graph_node_count_after: int = 0,
    node_level_repair_fixture_ready: bool = False,
    compile_executed: bool = True,
    save_executed: bool = True,
    target_dirty_after: bool = False,
    dirty_maps_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
    graph_repair_command_dispatched: bool = False,
    graph_repair_command_executed: bool = False,
    graph_layout_mutation_performed: bool = False,
    node_position_write_performed: bool = False,
    pin_connection_write_performed: bool = False,
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
        "schema": POST_RECREATION_NON_EMPTY_GRAPH_FIXTURE_RESULT_SCHEMA,
        "fixture_asset_path": fixture_asset_path,
        "fixture_root": fixture_root,
        "fixture_under_expected_root": fixture_under_expected_root,
        "asset_created": asset_created,
        "asset_reused_on_final_readback": asset_reused_on_final_readback,
        "fixture_create_or_update_executed": fixture_create_or_update_executed,
        "asset_exists_after": asset_exists_after,
        "asset_data_valid_after": asset_data_valid_after,
        "blueprint_class_name": blueprint_class_name,
        "generated_class_path": generated_class_path,
        "cdo_class_name": cdo_class_name,
        "cdo_is_actor": cdo_is_actor,
        "content_file_exists_after": content_file_exists_after,
        "content_file_size_after": content_file_size_after,
        "function_graph_name_after": function_graph_name_after,
        "function_graph_exists_after": function_graph_exists_after,
        "function_graph_count_after": function_graph_count_after,
        "function_graph_inventory_non_empty_after": (
            function_graph_inventory_non_empty_after
        ),
        "function_graph_node_count_after": function_graph_node_count_after,
        "node_level_repair_fixture_ready": node_level_repair_fixture_ready,
        "compile_executed": compile_executed,
        "save_executed": save_executed,
        "target_dirty_after": target_dirty_after,
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_preserved": external_dirty_preserved,
        "graph_repair_command_dispatched": graph_repair_command_dispatched,
        "graph_repair_command_executed": graph_repair_command_executed,
        "graph_layout_mutation_performed": graph_layout_mutation_performed,
        "node_position_write_performed": node_position_write_performed,
        "pin_connection_write_performed": pin_connection_write_performed,
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


def build_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch_contract(
    requested: bool,
    section_345_352_graph_repair_execution_dry_run_summary: Dict[str, Any],
    post_recreation_non_empty_graph_fixture_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_345_352_summary_schema_matches = bool(
        section_345_352_graph_repair_execution_dry_run_summary.get("schema")
        == SECTION_345_352_GRAPH_REPAIR_EXECUTION_DRY_RUN_SUMMARY_SCHEMA
    )
    section_345_352_summary_passed = bool(
        section_345_352_graph_repair_execution_dry_run_summary.get("status")
        == "passed"
    )
    upstream_graph_repair_dry_run_ready = all(
        _count_is_one(
            section_345_352_graph_repair_execution_dry_run_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_345_352_graph_repair_execution_dry_run_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        post_recreation_non_empty_graph_fixture_result.get("schema")
        == POST_RECREATION_NON_EMPTY_GRAPH_FIXTURE_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_345_352_summary_schema_matches
        and section_345_352_summary_passed
        and upstream_graph_repair_dry_run_ready
        and upstream_outputs_closed
    )
    fixture_target_scope_verified = bool(
        post_recreation_non_empty_graph_fixture_result.get("fixture_asset_path")
        == DEFAULT_FIXTURE_ASSET_PATH
        and post_recreation_non_empty_graph_fixture_result.get("fixture_root")
        == DEFAULT_FIXTURE_ROOT
        and post_recreation_non_empty_graph_fixture_result.get(
            "fixture_under_expected_root"
        )
        and str(
            post_recreation_non_empty_graph_fixture_result.get(
                "fixture_asset_path", ""
            )
        ).startswith("/Game/_MCP_Temp/")
    )
    fixture_create_or_update_executed = bool(
        fixture_target_scope_verified
        and post_recreation_non_empty_graph_fixture_result.get(
            "fixture_create_or_update_executed"
        )
        and (
            post_recreation_non_empty_graph_fixture_result.get("asset_created")
            or post_recreation_non_empty_graph_fixture_result.get(
                "asset_reused_on_final_readback"
            )
        )
    )
    actor_blueprint_readback_verified = bool(
        post_recreation_non_empty_graph_fixture_result.get("asset_exists_after")
        and post_recreation_non_empty_graph_fixture_result.get(
            "asset_data_valid_after"
        )
        and post_recreation_non_empty_graph_fixture_result.get(
            "blueprint_class_name"
        )
        == DEFAULT_FIXTURE_BLUEPRINT_CLASS_NAME
        and post_recreation_non_empty_graph_fixture_result.get(
            "generated_class_path"
        )
        == DEFAULT_FIXTURE_GENERATED_CLASS_PATH
        and post_recreation_non_empty_graph_fixture_result.get("cdo_class_name")
        == DEFAULT_FIXTURE_CDO_CLASS_NAME
        and post_recreation_non_empty_graph_fixture_result.get("cdo_is_actor")
        and post_recreation_non_empty_graph_fixture_result.get(
            "content_file_exists_after"
        )
        and int(
            post_recreation_non_empty_graph_fixture_result.get(
                "content_file_size_after", 0
            )
            or 0
        )
        > 0
    )
    function_graph_inventory_non_empty_verified = bool(
        actor_blueprint_readback_verified
        and post_recreation_non_empty_graph_fixture_result.get(
            "function_graph_exists_after"
        )
        and post_recreation_non_empty_graph_fixture_result.get(
            "function_graph_name_after"
        )
        == DEFAULT_FUNCTION_GRAPH_NAME
        and int(
            post_recreation_non_empty_graph_fixture_result.get(
                "function_graph_count_after", 0
            )
            or 0
        )
        >= 1
        and post_recreation_non_empty_graph_fixture_result.get(
            "function_graph_inventory_non_empty_after"
        )
    )
    compile_save_readback_verified = bool(
        post_recreation_non_empty_graph_fixture_result.get("compile_executed")
        and post_recreation_non_empty_graph_fixture_result.get("save_executed")
        and not post_recreation_non_empty_graph_fixture_result.get(
            "target_dirty_after"
        )
        and not post_recreation_non_empty_graph_fixture_result.get(
            "dirty_maps_after"
        )
        and post_recreation_non_empty_graph_fixture_result.get(
            "external_dirty_preserved"
        )
    )
    node_level_repair_still_blocked = bool(
        int(
            post_recreation_non_empty_graph_fixture_result.get(
                "function_graph_node_count_after", -1
            )
            or 0
        )
        == 0
        and not post_recreation_non_empty_graph_fixture_result.get(
            "node_level_repair_fixture_ready"
        )
        and not post_recreation_non_empty_graph_fixture_result.get(
            "node_position_write_performed"
        )
        and not post_recreation_non_empty_graph_fixture_result.get(
            "pin_connection_write_performed"
        )
    )
    non_fixture_outputs_closed = bool(
        all(
            not post_recreation_non_empty_graph_fixture_result.get(key)
            for key in BLOCKED_NON_EMPTY_GRAPH_FIXTURE_RESULT_KEYS
        )
        and not post_recreation_non_empty_graph_fixture_result.get(
            "production_path_write_executed"
        )
    )
    result_has_no_error = bool(
        post_recreation_non_empty_graph_fixture_result.get("error") in (None, "")
    )
    fixture_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and fixture_target_scope_verified
        and fixture_create_or_update_executed
        and function_graph_inventory_non_empty_verified
        and compile_save_readback_verified
        and node_level_repair_still_blocked
        and non_fixture_outputs_closed
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_post_recreation_non_empty_graph_fixture_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_NON_EMPTY_GRAPH_FIXTURE_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_345_352_summary_schema_matches": (
            section_345_352_summary_schema_matches
        ),
        "section_345_352_summary_passed": section_345_352_summary_passed,
        "section_345_352_graph_repair_execution_dry_run_ready": (
            upstream_graph_repair_dry_run_ready
        ),
        "section_345_352_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "non_empty_graph_fixture_checkpoint_satisfied": checkpoint_satisfied,
        "fixture_target_scope_verified": fixture_target_scope_verified,
        "fixture_actor_blueprint_create_or_update_executed": (
            fixture_create_or_update_executed
        ),
        "function_graph_inventory_non_empty_verified": (
            function_graph_inventory_non_empty_verified
        ),
        "fixture_compile_save_readback_verified": compile_save_readback_verified,
        "node_level_repair_still_blocked": node_level_repair_still_blocked,
        "non_fixture_outputs_closed": non_fixture_outputs_closed,
        "result_has_no_error": result_has_no_error,
        "section_353_non_empty_graph_fixture_checkpoint_satisfied": (
            fixture_ready
        ),
        "section_354_fixture_target_scope_verified": fixture_ready,
        "section_355_fixture_actor_blueprint_create_or_update_executed": (
            fixture_ready
        ),
        "section_356_function_graph_inventory_non_empty_verified": fixture_ready,
        "section_357_fixture_compile_save_readback_verified": fixture_ready,
        "section_358_node_level_repair_still_blocked": fixture_ready,
        "section_359_non_fixture_outputs_closed": fixture_ready,
        "section_360_non_empty_graph_fixture_release_ready": fixture_ready,
        "post_recreation_non_empty_graph_fixture_ready": fixture_ready,
        "post_recreation_node_level_repair_fixture_still_missing": fixture_ready,
        "final_durable_release_ready": fixture_ready,
        **{
            key: 1 if fixture_ready else 0
            for key in POST_RECREATION_NON_EMPTY_GRAPH_FIXTURE_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_NON_EMPTY_GRAPH_FIXTURE_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_post_recreation_non_empty_graph_fixture_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "post_recreation_non_empty_graph_fixture_ready"
            )
            == len(requested)
            and _truthy_count(
                requested,
                "post_recreation_node_level_repair_fixture_still_missing",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_NON_EMPTY_GRAPH_FIXTURE_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_NON_EMPTY_GRAPH_FIXTURE_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_post_recreation_non_empty_graph_fixture_batch_count": (
            len(requested)
        ),
        "section_345_352_summary_schema_matches_count": _truthy_count(
            requested, "section_345_352_summary_schema_matches"
        ),
        "section_345_352_summary_passed_count": _truthy_count(
            requested, "section_345_352_summary_passed"
        ),
        "section_345_352_graph_repair_execution_dry_run_ready_count": (
            _truthy_count(
                requested,
                "section_345_352_graph_repair_execution_dry_run_ready",
            )
        ),
        "section_345_352_outputs_closed_count": _truthy_count(
            requested, "section_345_352_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "non_empty_graph_fixture_checkpoint_satisfied_count": _truthy_count(
            requested, "non_empty_graph_fixture_checkpoint_satisfied"
        ),
        "fixture_target_scope_verified_count": _truthy_count(
            requested, "fixture_target_scope_verified"
        ),
        "fixture_actor_blueprint_create_or_update_executed_count": _truthy_count(
            requested, "fixture_actor_blueprint_create_or_update_executed"
        ),
        "function_graph_inventory_non_empty_verified_count": _truthy_count(
            requested, "function_graph_inventory_non_empty_verified"
        ),
        "fixture_compile_save_readback_verified_count": _truthy_count(
            requested, "fixture_compile_save_readback_verified"
        ),
        "node_level_repair_still_blocked_count": _truthy_count(
            requested, "node_level_repair_still_blocked"
        ),
        "non_fixture_outputs_closed_count": _truthy_count(
            requested, "non_fixture_outputs_closed"
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
            for key in POST_RECREATION_NON_EMPTY_GRAPH_FIXTURE_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_NON_EMPTY_GRAPH_FIXTURE_OUTPUT_COUNT_KEYS
        }
    )
    return summary
