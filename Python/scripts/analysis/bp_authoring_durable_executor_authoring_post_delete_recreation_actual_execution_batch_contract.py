#!/usr/bin/env python
"""
Sections 305-312 durable executor post-delete recreation actual execution.

This contract follows the Section 297-304 post-delete reset. It admits one
target-scoped Actor Blueprint recreation under /Game/_MCP_Temp, then proves the
asset was compiled, saved, and read back while variable/component/default
authoring, graph repair, delete, rename, overwrite, cleanup, and production
writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_post_delete_recreation_reset_batch_contract as post_delete_reset


DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_ACTUAL_EXECUTION_BATCH_SCHEMA = (
    "section_305_312_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_ACTUAL_EXECUTION_BATCH_SUMMARY_SCHEMA = (
    "section_305_312_durable_executor_authoring_post_delete_recreation_actual_execution_batch_summary_v1"
)
POST_DELETE_RECREATION_ACTUAL_EXECUTION_RESULT_SCHEMA = (
    "section_305_312_post_delete_recreation_actual_execution_result_v1"
)
SECTION_297_304_POST_DELETE_RECREATION_RESET_SUMMARY_SCHEMA = (
    post_delete_reset
    .DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_RESET_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = post_delete_reset.DEFAULT_TARGET_ASSET_PATH
DEFAULT_TARGET_ROOT = post_delete_reset.DEFAULT_TARGET_ROOT
DEFAULT_TARGET_FOLDER = "/Game/_MCP_Temp/DurableSaveGate"
DEFAULT_TARGET_CONTENT_FILE = post_delete_reset.DEFAULT_TARGET_CONTENT_FILE
DEFAULT_GENERATED_CLASS_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/"
    "BP_DurableSaveGatePrep.BP_DurableSaveGatePrep_C"
)
DEFAULT_BLUEPRINT_CLASS_NAME = "Blueprint"
DEFAULT_CDO_CLASS_NAME = "BP_DurableSaveGatePrep_C"
DEFAULT_CONTENT_FILE_SIZE = 24169
DEFAULT_EXTERNAL_DIRTY_PACKAGE = (
    post_delete_reset.DEFAULT_EXTERNAL_DIRTY_PACKAGE
)
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_post_delete_recreation_reset_batch_count",
    "section_297_post_delete_checkpoint_satisfied_count",
    "section_298_deleted_target_absence_confirmed_count",
    "section_299_recreation_plan_scoped_count",
    "section_300_recreation_requires_explicit_checkpoint_count",
    "section_301_readback_routes_reset_count",
    "section_302_diagnostics_routes_reset_count",
    "section_303_post_delete_no_write_boundary_verified_count",
    "section_304_post_delete_reset_release_ready_count",
    "post_delete_recreation_reset_ready_count",
    "post_delete_target_absence_confirmed_count",
    "post_delete_recreation_requires_checkpoint_count",
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    "recreate_asset_allowed_count",
    "recreate_command_dispatched_count",
    "recreate_command_executed_count",
    "readback_command_dispatched_count",
    "readback_command_executed_count",
    "diagnostics_command_dispatched_count",
    "diagnostics_command_executed_count",
    "graph_repair_command_dispatched_count",
    "graph_repair_command_executed_count",
    "graph_layout_mutation_performed_count",
    "node_position_write_performed_count",
    "pin_connection_write_performed_count",
    "actor_bp_authoring_compile_dispatched_count",
    "actor_bp_authoring_compile_executed_count",
    "actor_bp_authoring_save_dispatched_count",
    "actor_bp_authoring_save_executed_count",
    "actor_bp_authoring_asset_write_performed_count",
    "actor_bp_authoring_package_dirty_marked_count",
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
POST_DELETE_RECREATION_ACTUAL_EXECUTION_PATH_COUNT_KEYS = (
    "section_305_recreation_checkpoint_satisfied_count",
    "section_306_recreation_target_absence_preflight_count",
    "section_307_recreate_actor_bp_executed_count",
    "section_308_recreated_actor_bp_compiled_count",
    "section_309_recreated_actor_bp_saved_count",
    "section_310_recreated_actor_bp_readback_verified_count",
    "section_311_recreation_dirty_baseline_preserved_count",
    "section_312_recreation_actual_release_ready_count",
    "post_delete_recreation_actual_execution_ready_count",
    "post_delete_recreated_actor_bp_saved_count",
    "post_delete_recreated_actor_bp_readback_verified_count",
)
BLOCKED_POST_DELETE_RECREATION_ACTUAL_OUTPUT_COUNT_KEYS = (
    "variable_add_command_dispatched_count",
    "variable_add_command_executed_count",
    "component_add_command_dispatched_count",
    "component_add_command_executed_count",
    "default_write_command_dispatched_count",
    "default_write_command_executed_count",
    "diagnostics_command_dispatched_count",
    "diagnostics_command_executed_count",
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


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _count_is_one(summary: Dict[str, Any], key: str) -> bool:
    return bool(summary.get(key) == 1)


def _count_is_zero(summary: Dict[str, Any], key: str) -> bool:
    return bool(int(summary.get(key, 0) or 0) == 0)


def build_post_delete_recreation_actual_execution_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_root: str = DEFAULT_TARGET_ROOT,
    target_folder: str = DEFAULT_TARGET_FOLDER,
    target_content_file: str = DEFAULT_TARGET_CONTENT_FILE,
    target_under_expected_root: bool = True,
    asset_exists_before: bool = False,
    asset_data_valid_before: bool = False,
    content_file_exists_before: bool = False,
    target_dirty_before: bool = False,
    dirty_maps_before: Sequence[str] = (),
    external_dirty_before: Sequence[str] = (DEFAULT_EXTERNAL_DIRTY_PACKAGE,),
    preflight_passed: bool = True,
    recreate_asset_allowed: bool = True,
    recreate_command_dispatched: bool = True,
    recreate_command_executed: bool = True,
    asset_write_performed: bool = True,
    compile_dispatched: bool = True,
    compile_executed: bool = True,
    save_asset_allowed: bool = True,
    save_dispatched: bool = True,
    save_executed: bool = True,
    asset_exists_after: bool = True,
    asset_data_valid_after: bool = True,
    content_file_exists_after: bool = True,
    content_file_size: int = DEFAULT_CONTENT_FILE_SIZE,
    loaded_after: bool = True,
    blueprint_class_name: str = DEFAULT_BLUEPRINT_CLASS_NAME,
    generated_class_path: str = DEFAULT_GENERATED_CLASS_PATH,
    cdo_class_name: str = DEFAULT_CDO_CLASS_NAME,
    cdo_is_actor: bool = True,
    readback_verified: bool = True,
    target_dirty_after: bool = False,
    dirty_maps_after: Sequence[str] = (),
    external_dirty_after: Sequence[str] = (DEFAULT_EXTERNAL_DIRTY_PACKAGE,),
    external_dirty_preserved: bool = True,
    variable_add_command_dispatched: bool = False,
    variable_add_command_executed: bool = False,
    component_add_command_dispatched: bool = False,
    component_add_command_executed: bool = False,
    default_write_command_dispatched: bool = False,
    default_write_command_executed: bool = False,
    diagnostics_command_dispatched: bool = False,
    diagnostics_command_executed: bool = False,
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
        "schema": POST_DELETE_RECREATION_ACTUAL_EXECUTION_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_root": target_root,
        "target_folder": target_folder,
        "target_content_file": target_content_file,
        "target_under_expected_root": target_under_expected_root,
        "asset_exists_before": asset_exists_before,
        "asset_data_valid_before": asset_data_valid_before,
        "content_file_exists_before": content_file_exists_before,
        "target_dirty_before": target_dirty_before,
        "dirty_maps_before": list(dirty_maps_before),
        "external_dirty_before": list(external_dirty_before),
        "preflight_passed": preflight_passed,
        "recreate_asset_allowed": recreate_asset_allowed,
        "recreate_command_dispatched": recreate_command_dispatched,
        "recreate_command_executed": recreate_command_executed,
        "asset_write_performed": asset_write_performed,
        "compile_dispatched": compile_dispatched,
        "compile_executed": compile_executed,
        "save_asset_allowed": save_asset_allowed,
        "save_dispatched": save_dispatched,
        "save_executed": save_executed,
        "asset_exists_after": asset_exists_after,
        "asset_data_valid_after": asset_data_valid_after,
        "content_file_exists_after": content_file_exists_after,
        "content_file_size": content_file_size,
        "loaded_after": loaded_after,
        "blueprint_class_name": blueprint_class_name,
        "generated_class_path": generated_class_path,
        "cdo_class_name": cdo_class_name,
        "cdo_is_actor": cdo_is_actor,
        "readback_verified": readback_verified,
        "target_dirty_after": target_dirty_after,
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_after": list(external_dirty_after),
        "external_dirty_preserved": external_dirty_preserved,
        "variable_add_command_dispatched": variable_add_command_dispatched,
        "variable_add_command_executed": variable_add_command_executed,
        "component_add_command_dispatched": component_add_command_dispatched,
        "component_add_command_executed": component_add_command_executed,
        "default_write_command_dispatched": default_write_command_dispatched,
        "default_write_command_executed": default_write_command_executed,
        "diagnostics_command_dispatched": diagnostics_command_dispatched,
        "diagnostics_command_executed": diagnostics_command_executed,
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


def build_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract(
    requested: bool,
    section_297_304_post_delete_recreation_reset_summary: Dict[str, Any],
    post_delete_recreation_actual_execution_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_297_304_summary_schema_matches = bool(
        section_297_304_post_delete_recreation_reset_summary.get("schema")
        == SECTION_297_304_POST_DELETE_RECREATION_RESET_SUMMARY_SCHEMA
    )
    section_297_304_summary_passed = bool(
        section_297_304_post_delete_recreation_reset_summary.get("status")
        == "passed"
    )
    upstream_post_delete_reset_ready = all(
        _count_is_one(
            section_297_304_post_delete_recreation_reset_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_297_304_post_delete_recreation_reset_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        post_delete_recreation_actual_execution_result.get("schema")
        == POST_DELETE_RECREATION_ACTUAL_EXECUTION_RESULT_SCHEMA
    )
    recreation_checkpoint_satisfied = bool(
        requested
        and section_297_304_summary_schema_matches
        and section_297_304_summary_passed
        and upstream_post_delete_reset_ready
        and upstream_outputs_closed
    )
    recreation_target_absence_preflight = bool(
        post_delete_recreation_actual_execution_result.get("target_asset_path")
        == DEFAULT_TARGET_ASSET_PATH
        and post_delete_recreation_actual_execution_result.get("target_root")
        == DEFAULT_TARGET_ROOT
        and post_delete_recreation_actual_execution_result.get(
            "target_folder"
        )
        == DEFAULT_TARGET_FOLDER
        and post_delete_recreation_actual_execution_result.get(
            "target_under_expected_root"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "asset_exists_before"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "asset_data_valid_before"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "content_file_exists_before"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "target_dirty_before"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "dirty_maps_before"
        )
        and post_delete_recreation_actual_execution_result.get(
            "preflight_passed"
        )
    )
    recreate_actor_bp_executed = bool(
        post_delete_recreation_actual_execution_result.get(
            "recreate_asset_allowed"
        )
        and post_delete_recreation_actual_execution_result.get(
            "recreate_command_dispatched"
        )
        and post_delete_recreation_actual_execution_result.get(
            "recreate_command_executed"
        )
        and post_delete_recreation_actual_execution_result.get(
            "asset_write_performed"
        )
    )
    recreated_actor_bp_compiled = bool(
        post_delete_recreation_actual_execution_result.get(
            "compile_dispatched"
        )
        and post_delete_recreation_actual_execution_result.get(
            "compile_executed"
        )
    )
    recreated_actor_bp_saved = bool(
        post_delete_recreation_actual_execution_result.get(
            "save_asset_allowed"
        )
        and post_delete_recreation_actual_execution_result.get(
            "save_dispatched"
        )
        and post_delete_recreation_actual_execution_result.get(
            "save_executed"
        )
    )
    recreated_actor_bp_readback_verified = bool(
        post_delete_recreation_actual_execution_result.get(
            "asset_exists_after"
        )
        and post_delete_recreation_actual_execution_result.get(
            "asset_data_valid_after"
        )
        and post_delete_recreation_actual_execution_result.get(
            "content_file_exists_after"
        )
        and int(
            post_delete_recreation_actual_execution_result.get(
                "content_file_size", 0
            )
            or 0
        )
        > 0
        and post_delete_recreation_actual_execution_result.get("loaded_after")
        and post_delete_recreation_actual_execution_result.get(
            "blueprint_class_name"
        )
        == DEFAULT_BLUEPRINT_CLASS_NAME
        and post_delete_recreation_actual_execution_result.get(
            "generated_class_path"
        )
        == DEFAULT_GENERATED_CLASS_PATH
        and post_delete_recreation_actual_execution_result.get(
            "cdo_class_name"
        )
        == DEFAULT_CDO_CLASS_NAME
        and post_delete_recreation_actual_execution_result.get(
            "cdo_is_actor"
        )
        and post_delete_recreation_actual_execution_result.get(
            "readback_verified"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "target_dirty_after"
        )
    )
    recreation_dirty_baseline_preserved = bool(
        post_delete_recreation_actual_execution_result.get(
            "external_dirty_preserved"
        )
        and post_delete_recreation_actual_execution_result.get(
            "external_dirty_before"
        )
        == post_delete_recreation_actual_execution_result.get(
            "external_dirty_after"
        )
        and post_delete_recreation_actual_execution_result.get(
            "dirty_maps_before"
        )
        == post_delete_recreation_actual_execution_result.get(
            "dirty_maps_after"
        )
    )
    authoring_expansion_outputs_closed = bool(
        not post_delete_recreation_actual_execution_result.get(
            "variable_add_command_dispatched"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "variable_add_command_executed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "component_add_command_dispatched"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "component_add_command_executed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "default_write_command_dispatched"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "default_write_command_executed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "diagnostics_command_dispatched"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "diagnostics_command_executed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "graph_repair_command_dispatched"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "graph_repair_command_executed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "graph_layout_mutation_performed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "node_position_write_performed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "pin_connection_write_performed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "cleanup_allowed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "cleanup_executed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "delete_asset_allowed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "delete_asset_executed_output"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "rename_asset_allowed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "rename_command_dispatched"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "rename_command_executed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "overwrite_allowed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "overwrite_executed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "production_path_write_allowed"
        )
        and not post_delete_recreation_actual_execution_result.get(
            "production_path_write_executed"
        )
    )
    result_has_no_error = bool(
        post_delete_recreation_actual_execution_result.get("error") in (None, "")
    )
    recreation_actual_passed = bool(
        recreation_checkpoint_satisfied
        and result_schema_matches
        and recreation_target_absence_preflight
        and recreate_actor_bp_executed
        and recreated_actor_bp_compiled
        and recreated_actor_bp_saved
        and recreated_actor_bp_readback_verified
        and recreation_dirty_baseline_preserved
        and authoring_expansion_outputs_closed
        and result_has_no_error
    )

    return {
        "id": "durable_executor_authoring_post_delete_recreation_actual_execution_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_ACTUAL_EXECUTION_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_297_304_summary_schema_matches": (
            section_297_304_summary_schema_matches
        ),
        "section_297_304_summary_passed": section_297_304_summary_passed,
        "section_297_304_post_delete_reset_ready": (
            upstream_post_delete_reset_ready
        ),
        "section_297_304_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "recreation_checkpoint_satisfied": recreation_checkpoint_satisfied,
        "recreation_target_absence_preflight": (
            recreation_target_absence_preflight
        ),
        "recreate_actor_bp_executed": recreate_actor_bp_executed,
        "recreated_actor_bp_compiled": recreated_actor_bp_compiled,
        "recreated_actor_bp_saved": recreated_actor_bp_saved,
        "recreated_actor_bp_readback_verified": (
            recreated_actor_bp_readback_verified
        ),
        "recreation_dirty_baseline_preserved": (
            recreation_dirty_baseline_preserved
        ),
        "authoring_expansion_outputs_closed": (
            authoring_expansion_outputs_closed
        ),
        "result_has_no_error": result_has_no_error,
        "section_305_recreation_checkpoint_satisfied": (
            recreation_actual_passed
        ),
        "section_306_recreation_target_absence_preflight": (
            recreation_actual_passed
        ),
        "section_307_recreate_actor_bp_executed": recreation_actual_passed,
        "section_308_recreated_actor_bp_compiled": recreation_actual_passed,
        "section_309_recreated_actor_bp_saved": recreation_actual_passed,
        "section_310_recreated_actor_bp_readback_verified": (
            recreation_actual_passed
        ),
        "section_311_recreation_dirty_baseline_preserved": (
            recreation_actual_passed
        ),
        "section_312_recreation_actual_release_ready": (
            recreation_actual_passed
        ),
        "post_delete_recreation_actual_execution_ready": (
            recreation_actual_passed
        ),
        "post_delete_recreated_actor_bp_saved": recreation_actual_passed,
        "post_delete_recreated_actor_bp_readback_verified": (
            recreation_actual_passed
        ),
        "final_durable_release_ready": recreation_actual_passed,
        "recreate_asset_allowed": recreation_actual_passed,
        "recreate_command_dispatched": recreation_actual_passed,
        "recreate_command_executed": recreation_actual_passed,
        "actor_bp_authoring_compile_dispatched": recreation_actual_passed,
        "actor_bp_authoring_compile_executed": recreation_actual_passed,
        "actor_bp_authoring_save_dispatched": recreation_actual_passed,
        "actor_bp_authoring_save_executed": recreation_actual_passed,
        "actor_bp_authoring_asset_write_performed": recreation_actual_passed,
        "actor_bp_authoring_package_dirty_marked": False,
        "variable_add_command_dispatched": False,
        "variable_add_command_executed": False,
        "component_add_command_dispatched": False,
        "component_add_command_executed": False,
        "default_write_command_dispatched": False,
        "default_write_command_executed": False,
        "diagnostics_command_dispatched": False,
        "diagnostics_command_executed": False,
        "graph_repair_command_dispatched": False,
        "graph_repair_command_executed": False,
        "graph_layout_mutation_performed": False,
        "node_position_write_performed": False,
        "pin_connection_write_performed": False,
        "cleanup_allowed": False,
        "cleanup_executed": False,
        "delete_asset_allowed": False,
        "delete_asset_executed_output": False,
        "rename_asset_allowed": False,
        "rename_command_dispatched": False,
        "rename_command_executed": False,
        "overwrite_allowed": False,
        "overwrite_executed": False,
        "production_path_write_allowed": False,
        "production_path_write_executed": False,
        **{
            key: 1 if recreation_actual_passed else 0
            for key in POST_DELETE_RECREATION_ACTUAL_EXECUTION_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_POST_DELETE_RECREATION_ACTUAL_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_post_delete_recreation_actual_execution_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "post_delete_recreation_actual_execution_ready"
            )
            == len(requested)
            and _truthy_count(
                requested, "post_delete_recreated_actor_bp_saved"
            )
            == len(requested)
            and _truthy_count(
                requested,
                "post_delete_recreated_actor_bp_readback_verified",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_POST_DELETE_RECREATION_ACTUAL_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_ACTUAL_EXECUTION_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_post_delete_recreation_actual_execution_batch_count": (
            len(requested)
        ),
        "section_297_304_summary_schema_matches_count": _truthy_count(
            requested, "section_297_304_summary_schema_matches"
        ),
        "section_297_304_summary_passed_count": _truthy_count(
            requested, "section_297_304_summary_passed"
        ),
        "section_297_304_post_delete_reset_ready_count": _truthy_count(
            requested, "section_297_304_post_delete_reset_ready"
        ),
        "section_297_304_outputs_closed_count": _truthy_count(
            requested, "section_297_304_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "recreation_checkpoint_satisfied_count": _truthy_count(
            requested, "recreation_checkpoint_satisfied"
        ),
        "recreation_target_absence_preflight_count": _truthy_count(
            requested, "recreation_target_absence_preflight"
        ),
        "recreate_actor_bp_executed_count": _truthy_count(
            requested, "recreate_actor_bp_executed"
        ),
        "recreated_actor_bp_compiled_count": _truthy_count(
            requested, "recreated_actor_bp_compiled"
        ),
        "recreated_actor_bp_saved_count": _truthy_count(
            requested, "recreated_actor_bp_saved"
        ),
        "recreated_actor_bp_readback_verified_count": _truthy_count(
            requested, "recreated_actor_bp_readback_verified"
        ),
        "recreation_dirty_baseline_preserved_count": _truthy_count(
            requested, "recreation_dirty_baseline_preserved"
        ),
        "authoring_expansion_outputs_closed_count": _truthy_count(
            requested, "authoring_expansion_outputs_closed"
        ),
        "result_has_no_error_count": _truthy_count(
            requested, "result_has_no_error"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "recreate_asset_allowed_count": _truthy_count(
            requested, "recreate_asset_allowed"
        ),
        "recreate_command_dispatched_count": _truthy_count(
            requested, "recreate_command_dispatched"
        ),
        "recreate_command_executed_count": _truthy_count(
            requested, "recreate_command_executed"
        ),
        "actor_bp_authoring_compile_dispatched_count": _truthy_count(
            requested, "actor_bp_authoring_compile_dispatched"
        ),
        "actor_bp_authoring_compile_executed_count": _truthy_count(
            requested, "actor_bp_authoring_compile_executed"
        ),
        "actor_bp_authoring_save_dispatched_count": _truthy_count(
            requested, "actor_bp_authoring_save_dispatched"
        ),
        "actor_bp_authoring_save_executed_count": _truthy_count(
            requested, "actor_bp_authoring_save_executed"
        ),
        "actor_bp_authoring_asset_write_performed_count": _truthy_count(
            requested, "actor_bp_authoring_asset_write_performed"
        ),
        "actor_bp_authoring_package_dirty_marked_count": _truthy_count(
            requested, "actor_bp_authoring_package_dirty_marked"
        ),
    }
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in POST_DELETE_RECREATION_ACTUAL_EXECUTION_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_POST_DELETE_RECREATION_ACTUAL_OUTPUT_COUNT_KEYS
        }
    )
    return summary
