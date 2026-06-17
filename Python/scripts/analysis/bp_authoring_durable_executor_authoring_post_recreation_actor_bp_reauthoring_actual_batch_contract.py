#!/usr/bin/env python
"""
Sections 313-320 durable executor post-recreation Actor BP reauthoring.

This contract follows the Section 305-312 temp Actor Blueprint recreation. It
admits one target-scoped variable, component, and Actor default/tag authoring
pass under /Game/_MCP_Temp, then proves compile/save/readback while graph
repair, delete, rename, overwrite, cleanup, and production writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_post_delete_recreation_actual_execution_batch_contract as recreation_actual


DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_ACTOR_BP_REAUTHORING_ACTUAL_BATCH_SCHEMA = (
    "section_313_320_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_ACTOR_BP_REAUTHORING_ACTUAL_BATCH_SUMMARY_SCHEMA = (
    "section_313_320_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_summary_v1"
)
POST_RECREATION_ACTOR_BP_REAUTHORING_ACTUAL_RESULT_SCHEMA = (
    "section_313_320_post_recreation_actor_bp_reauthoring_actual_result_v1"
)
SECTION_305_312_POST_DELETE_RECREATION_ACTUAL_EXECUTION_SUMMARY_SCHEMA = (
    recreation_actual
    .DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_ACTUAL_EXECUTION_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = recreation_actual.DEFAULT_TARGET_ASSET_PATH
DEFAULT_TARGET_ROOT = recreation_actual.DEFAULT_TARGET_ROOT
DEFAULT_TARGET_CONTENT_FILE = recreation_actual.DEFAULT_TARGET_CONTENT_FILE
DEFAULT_GENERATED_CLASS_PATH = recreation_actual.DEFAULT_GENERATED_CLASS_PATH
DEFAULT_BLUEPRINT_CLASS_NAME = recreation_actual.DEFAULT_BLUEPRINT_CLASS_NAME
DEFAULT_CDO_CLASS_NAME = recreation_actual.DEFAULT_CDO_CLASS_NAME
DEFAULT_CONTENT_FILE_SIZE_BEFORE = recreation_actual.DEFAULT_CONTENT_FILE_SIZE
DEFAULT_CONTENT_FILE_SIZE_AFTER = 26627
DEFAULT_VARIABLE_NAME = "MCPAuthoringScalar"
DEFAULT_VARIABLE_VALUE = 1.0
DEFAULT_COMPONENT_NAME = "MCPAuthoringProbeComponent"
DEFAULT_COMPONENT_CLASS = "SceneComponent"
DEFAULT_TAG_NAME = "MCP_DurableAuthoring_LiveProbe"
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_post_delete_recreation_actual_execution_batch_count",
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
    "final_durable_release_ready_count",
)
UPSTREAM_AUTHORING_OUTPUTS_CLOSED_COUNT_KEYS = (
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
POST_RECREATION_ACTOR_BP_REAUTHORING_PATH_COUNT_KEYS = (
    "section_313_reauthoring_checkpoint_satisfied_count",
    "section_314_recreated_actor_bp_target_ready_count",
    "section_315_variable_reauthoring_executed_count",
    "section_316_component_reauthoring_executed_count",
    "section_317_default_tag_reauthoring_executed_count",
    "section_318_reauthoring_compile_save_executed_count",
    "section_319_reauthoring_readback_verified_count",
    "section_320_reauthoring_dirty_baseline_preserved_count",
    "post_recreation_actor_bp_reauthoring_ready_count",
    "post_recreation_actor_bp_reauthoring_saved_count",
    "post_recreation_actor_bp_reauthoring_readback_verified_count",
)
BLOCKED_POST_RECREATION_REAUTHORING_OUTPUT_COUNT_KEYS = (
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


def build_post_recreation_actor_bp_reauthoring_actual_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_root: str = DEFAULT_TARGET_ROOT,
    target_under_expected_root: bool = True,
    asset_exists_before: bool = True,
    asset_data_valid_before: bool = True,
    content_file_exists_before: bool = True,
    content_file_size_before: int = DEFAULT_CONTENT_FILE_SIZE_BEFORE,
    loaded_before: bool = True,
    blueprint_class_name: str = DEFAULT_BLUEPRINT_CLASS_NAME,
    generated_class_path: str = DEFAULT_GENERATED_CLASS_PATH,
    cdo_class_name: str = DEFAULT_CDO_CLASS_NAME,
    cdo_is_actor: bool = True,
    target_dirty_before: bool = False,
    dirty_maps_before: Sequence[str] = (),
    external_dirty_before: Sequence[str] = (),
    preflight_passed: bool = True,
    variable_name: str = DEFAULT_VARIABLE_NAME,
    variable_value: float = DEFAULT_VARIABLE_VALUE,
    variable_exists_before: bool = False,
    variable_added: bool = True,
    variable_exists_after: bool = True,
    scalar_default_after: float = DEFAULT_VARIABLE_VALUE,
    component_name: str = DEFAULT_COMPONENT_NAME,
    component_class: str = DEFAULT_COMPONENT_CLASS,
    component_exists_before: bool = False,
    component_added: bool = True,
    component_exists_after: bool = True,
    component_class_after: str = DEFAULT_COMPONENT_CLASS,
    tag_name: str = DEFAULT_TAG_NAME,
    tag_exists_before: bool = False,
    default_written: bool = True,
    tag_exists_after: bool = True,
    compile_dispatched: bool = True,
    compile_executed: bool = True,
    save_asset_allowed: bool = True,
    save_dispatched: bool = True,
    save_executed: bool = True,
    asset_exists_after: bool = True,
    asset_data_valid_after: bool = True,
    content_file_exists_after: bool = True,
    content_file_size_after: int = DEFAULT_CONTENT_FILE_SIZE_AFTER,
    readback_verified: bool = True,
    target_dirty_after: bool = False,
    dirty_maps_after: Sequence[str] = (),
    external_dirty_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
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
        "schema": POST_RECREATION_ACTOR_BP_REAUTHORING_ACTUAL_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_root": target_root,
        "target_under_expected_root": target_under_expected_root,
        "asset_exists_before": asset_exists_before,
        "asset_data_valid_before": asset_data_valid_before,
        "content_file_exists_before": content_file_exists_before,
        "content_file_size_before": content_file_size_before,
        "loaded_before": loaded_before,
        "blueprint_class_name": blueprint_class_name,
        "generated_class_path": generated_class_path,
        "cdo_class_name": cdo_class_name,
        "cdo_is_actor": cdo_is_actor,
        "target_dirty_before": target_dirty_before,
        "dirty_maps_before": list(dirty_maps_before),
        "external_dirty_before": list(external_dirty_before),
        "preflight_passed": preflight_passed,
        "variable_name": variable_name,
        "variable_value": variable_value,
        "variable_exists_before": variable_exists_before,
        "variable_added": variable_added,
        "variable_exists_after": variable_exists_after,
        "scalar_default_after": scalar_default_after,
        "component_name": component_name,
        "component_class": component_class,
        "component_exists_before": component_exists_before,
        "component_added": component_added,
        "component_exists_after": component_exists_after,
        "component_class_after": component_class_after,
        "tag_name": tag_name,
        "tag_exists_before": tag_exists_before,
        "default_written": default_written,
        "tag_exists_after": tag_exists_after,
        "compile_dispatched": compile_dispatched,
        "compile_executed": compile_executed,
        "save_asset_allowed": save_asset_allowed,
        "save_dispatched": save_dispatched,
        "save_executed": save_executed,
        "asset_exists_after": asset_exists_after,
        "asset_data_valid_after": asset_data_valid_after,
        "content_file_exists_after": content_file_exists_after,
        "content_file_size_after": content_file_size_after,
        "readback_verified": readback_verified,
        "target_dirty_after": target_dirty_after,
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_after": list(external_dirty_after),
        "external_dirty_preserved": external_dirty_preserved,
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


def build_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract(
    requested: bool,
    section_305_312_post_delete_recreation_actual_execution_summary: Dict[str, Any],
    post_recreation_actor_bp_reauthoring_actual_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_305_312_summary_schema_matches = bool(
        section_305_312_post_delete_recreation_actual_execution_summary.get(
            "schema"
        )
        == SECTION_305_312_POST_DELETE_RECREATION_ACTUAL_EXECUTION_SUMMARY_SCHEMA
    )
    section_305_312_summary_passed = bool(
        section_305_312_post_delete_recreation_actual_execution_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_recreation_ready = all(
        _count_is_one(
            section_305_312_post_delete_recreation_actual_execution_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_authoring_outputs_closed = all(
        _count_is_zero(
            section_305_312_post_delete_recreation_actual_execution_summary,
            key,
        )
        for key in UPSTREAM_AUTHORING_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        post_recreation_actor_bp_reauthoring_actual_result.get("schema")
        == POST_RECREATION_ACTOR_BP_REAUTHORING_ACTUAL_RESULT_SCHEMA
    )
    reauthoring_checkpoint_satisfied = bool(
        requested
        and section_305_312_summary_schema_matches
        and section_305_312_summary_passed
        and upstream_recreation_ready
        and upstream_authoring_outputs_closed
    )
    recreated_actor_bp_target_ready = bool(
        post_recreation_actor_bp_reauthoring_actual_result.get(
            "target_asset_path"
        )
        == DEFAULT_TARGET_ASSET_PATH
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "target_root"
        )
        == DEFAULT_TARGET_ROOT
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "target_under_expected_root"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "asset_exists_before"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "asset_data_valid_before"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "content_file_exists_before"
        )
        and int(
            post_recreation_actor_bp_reauthoring_actual_result.get(
                "content_file_size_before", 0
            )
            or 0
        )
        > 0
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "loaded_before"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "blueprint_class_name"
        )
        == DEFAULT_BLUEPRINT_CLASS_NAME
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "generated_class_path"
        )
        == DEFAULT_GENERATED_CLASS_PATH
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "cdo_class_name"
        )
        == DEFAULT_CDO_CLASS_NAME
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "cdo_is_actor"
        )
        and not post_recreation_actor_bp_reauthoring_actual_result.get(
            "target_dirty_before"
        )
        and not post_recreation_actor_bp_reauthoring_actual_result.get(
            "dirty_maps_before"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "preflight_passed"
        )
    )
    variable_reauthoring_executed = bool(
        post_recreation_actor_bp_reauthoring_actual_result.get("variable_name")
        == DEFAULT_VARIABLE_NAME
        and float(
            post_recreation_actor_bp_reauthoring_actual_result.get(
                "variable_value", -1
            )
        )
        == DEFAULT_VARIABLE_VALUE
        and not post_recreation_actor_bp_reauthoring_actual_result.get(
            "variable_exists_before"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "variable_added"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "variable_exists_after"
        )
        and float(
            post_recreation_actor_bp_reauthoring_actual_result.get(
                "scalar_default_after", -1
            )
        )
        == DEFAULT_VARIABLE_VALUE
    )
    component_reauthoring_executed = bool(
        post_recreation_actor_bp_reauthoring_actual_result.get(
            "component_name"
        )
        == DEFAULT_COMPONENT_NAME
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "component_class"
        )
        == DEFAULT_COMPONENT_CLASS
        and not post_recreation_actor_bp_reauthoring_actual_result.get(
            "component_exists_before"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "component_added"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "component_exists_after"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "component_class_after"
        )
        == DEFAULT_COMPONENT_CLASS
    )
    default_tag_reauthoring_executed = bool(
        post_recreation_actor_bp_reauthoring_actual_result.get("tag_name")
        == DEFAULT_TAG_NAME
        and not post_recreation_actor_bp_reauthoring_actual_result.get(
            "tag_exists_before"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "default_written"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "tag_exists_after"
        )
    )
    compile_save_executed = bool(
        post_recreation_actor_bp_reauthoring_actual_result.get(
            "compile_dispatched"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "compile_executed"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "save_asset_allowed"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "save_dispatched"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "save_executed"
        )
    )
    reauthoring_readback_verified = bool(
        post_recreation_actor_bp_reauthoring_actual_result.get(
            "asset_exists_after"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "asset_data_valid_after"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "content_file_exists_after"
        )
        and int(
            post_recreation_actor_bp_reauthoring_actual_result.get(
                "content_file_size_after", 0
            )
            or 0
        )
        > int(
            post_recreation_actor_bp_reauthoring_actual_result.get(
                "content_file_size_before", 0
            )
            or 0
        )
        and variable_reauthoring_executed
        and component_reauthoring_executed
        and default_tag_reauthoring_executed
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "readback_verified"
        )
        and not post_recreation_actor_bp_reauthoring_actual_result.get(
            "target_dirty_after"
        )
    )
    dirty_baseline_preserved = bool(
        post_recreation_actor_bp_reauthoring_actual_result.get(
            "external_dirty_preserved"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "external_dirty_before"
        )
        == post_recreation_actor_bp_reauthoring_actual_result.get(
            "external_dirty_after"
        )
        and post_recreation_actor_bp_reauthoring_actual_result.get(
            "dirty_maps_before"
        )
        == post_recreation_actor_bp_reauthoring_actual_result.get(
            "dirty_maps_after"
        )
    )
    destructive_outputs_closed = all(
        not post_recreation_actor_bp_reauthoring_actual_result.get(key)
        for key in (
            "diagnostics_command_dispatched",
            "diagnostics_command_executed",
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
    )
    result_has_no_error = bool(
        post_recreation_actor_bp_reauthoring_actual_result.get("error")
        in (None, "")
    )
    reauthoring_passed = bool(
        reauthoring_checkpoint_satisfied
        and result_schema_matches
        and recreated_actor_bp_target_ready
        and variable_reauthoring_executed
        and component_reauthoring_executed
        and default_tag_reauthoring_executed
        and compile_save_executed
        and reauthoring_readback_verified
        and dirty_baseline_preserved
        and destructive_outputs_closed
        and result_has_no_error
    )

    return {
        "id": "durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_ACTOR_BP_REAUTHORING_ACTUAL_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_305_312_summary_schema_matches": (
            section_305_312_summary_schema_matches
        ),
        "section_305_312_summary_passed": section_305_312_summary_passed,
        "section_305_312_post_delete_recreation_actual_ready": (
            upstream_recreation_ready
        ),
        "section_305_312_authoring_outputs_closed": (
            upstream_authoring_outputs_closed
        ),
        "result_schema_matches": result_schema_matches,
        "reauthoring_checkpoint_satisfied": reauthoring_checkpoint_satisfied,
        "recreated_actor_bp_target_ready": recreated_actor_bp_target_ready,
        "variable_reauthoring_executed": variable_reauthoring_executed,
        "component_reauthoring_executed": component_reauthoring_executed,
        "default_tag_reauthoring_executed": (
            default_tag_reauthoring_executed
        ),
        "compile_save_executed": compile_save_executed,
        "reauthoring_readback_verified": reauthoring_readback_verified,
        "dirty_baseline_preserved": dirty_baseline_preserved,
        "destructive_outputs_closed": destructive_outputs_closed,
        "result_has_no_error": result_has_no_error,
        "section_313_reauthoring_checkpoint_satisfied": reauthoring_passed,
        "section_314_recreated_actor_bp_target_ready": reauthoring_passed,
        "section_315_variable_reauthoring_executed": reauthoring_passed,
        "section_316_component_reauthoring_executed": reauthoring_passed,
        "section_317_default_tag_reauthoring_executed": reauthoring_passed,
        "section_318_reauthoring_compile_save_executed": reauthoring_passed,
        "section_319_reauthoring_readback_verified": reauthoring_passed,
        "section_320_reauthoring_dirty_baseline_preserved": reauthoring_passed,
        "post_recreation_actor_bp_reauthoring_ready": reauthoring_passed,
        "post_recreation_actor_bp_reauthoring_saved": reauthoring_passed,
        "post_recreation_actor_bp_reauthoring_readback_verified": (
            reauthoring_passed
        ),
        "final_durable_release_ready": reauthoring_passed,
        "variable_add_command_dispatched": reauthoring_passed,
        "variable_add_command_executed": reauthoring_passed,
        "component_add_command_dispatched": reauthoring_passed,
        "component_add_command_executed": reauthoring_passed,
        "default_write_command_dispatched": reauthoring_passed,
        "default_write_command_executed": reauthoring_passed,
        "actor_bp_authoring_command_dispatched": reauthoring_passed,
        "actor_bp_authoring_command_executed": reauthoring_passed,
        "actor_bp_authoring_compile_dispatched": reauthoring_passed,
        "actor_bp_authoring_compile_executed": reauthoring_passed,
        "actor_bp_authoring_save_dispatched": reauthoring_passed,
        "actor_bp_authoring_save_executed": reauthoring_passed,
        "actor_bp_authoring_asset_write_performed": reauthoring_passed,
        "actor_bp_authoring_package_dirty_marked": reauthoring_passed,
        "actor_bp_authoring_target_dirty_after": False,
        "actor_bp_authoring_external_dirty_preserved": reauthoring_passed,
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
            key: 1 if reauthoring_passed else 0
            for key in POST_RECREATION_ACTOR_BP_REAUTHORING_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_POST_RECREATION_REAUTHORING_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "post_recreation_actor_bp_reauthoring_ready"
            )
            == len(requested)
            and _truthy_count(
                requested, "post_recreation_actor_bp_reauthoring_saved"
            )
            == len(requested)
            and _truthy_count(
                requested,
                "post_recreation_actor_bp_reauthoring_readback_verified",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_POST_RECREATION_REAUTHORING_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_ACTOR_BP_REAUTHORING_ACTUAL_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_count": (
            len(requested)
        ),
        "section_305_312_summary_schema_matches_count": _truthy_count(
            requested, "section_305_312_summary_schema_matches"
        ),
        "section_305_312_summary_passed_count": _truthy_count(
            requested, "section_305_312_summary_passed"
        ),
        "section_305_312_post_delete_recreation_actual_ready_count": (
            _truthy_count(
                requested,
                "section_305_312_post_delete_recreation_actual_ready",
            )
        ),
        "section_305_312_authoring_outputs_closed_count": _truthy_count(
            requested, "section_305_312_authoring_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "reauthoring_checkpoint_satisfied_count": _truthy_count(
            requested, "reauthoring_checkpoint_satisfied"
        ),
        "recreated_actor_bp_target_ready_count": _truthy_count(
            requested, "recreated_actor_bp_target_ready"
        ),
        "variable_reauthoring_executed_count": _truthy_count(
            requested, "variable_reauthoring_executed"
        ),
        "component_reauthoring_executed_count": _truthy_count(
            requested, "component_reauthoring_executed"
        ),
        "default_tag_reauthoring_executed_count": _truthy_count(
            requested, "default_tag_reauthoring_executed"
        ),
        "compile_save_executed_count": _truthy_count(
            requested, "compile_save_executed"
        ),
        "reauthoring_readback_verified_count": _truthy_count(
            requested, "reauthoring_readback_verified"
        ),
        "dirty_baseline_preserved_count": _truthy_count(
            requested, "dirty_baseline_preserved"
        ),
        "destructive_outputs_closed_count": _truthy_count(
            requested, "destructive_outputs_closed"
        ),
        "result_has_no_error_count": _truthy_count(
            requested, "result_has_no_error"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "variable_add_command_dispatched_count": _truthy_count(
            requested, "variable_add_command_dispatched"
        ),
        "variable_add_command_executed_count": _truthy_count(
            requested, "variable_add_command_executed"
        ),
        "component_add_command_dispatched_count": _truthy_count(
            requested, "component_add_command_dispatched"
        ),
        "component_add_command_executed_count": _truthy_count(
            requested, "component_add_command_executed"
        ),
        "default_write_command_dispatched_count": _truthy_count(
            requested, "default_write_command_dispatched"
        ),
        "default_write_command_executed_count": _truthy_count(
            requested, "default_write_command_executed"
        ),
        "actor_bp_authoring_command_dispatched_count": _truthy_count(
            requested, "actor_bp_authoring_command_dispatched"
        ),
        "actor_bp_authoring_command_executed_count": _truthy_count(
            requested, "actor_bp_authoring_command_executed"
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
        "actor_bp_authoring_target_dirty_after_count": _truthy_count(
            requested, "actor_bp_authoring_target_dirty_after"
        ),
        "actor_bp_authoring_external_dirty_preserved_count": _truthy_count(
            requested, "actor_bp_authoring_external_dirty_preserved"
        ),
    }
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in POST_RECREATION_ACTOR_BP_REAUTHORING_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_POST_RECREATION_REAUTHORING_OUTPUT_COUNT_KEYS
        }
    )
    return summary
