#!/usr/bin/env python
"""
Sections 321-328 durable executor post-recreation Actor BP readback strengthening.

This contract follows the Section 313-320 temp Actor Blueprint reauthoring
checkpoint. It admits only readback normalization: duplicate raw component
handles are accepted only when they collapse to one expected component identity,
and no write, compile, save, delete, rename, overwrite, cleanup, graph repair,
or production path is opened.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_contract as reauthoring


DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_ACTOR_BP_READBACK_STRENGTHENING_BATCH_SCHEMA = (
    "section_321_328_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_ACTOR_BP_READBACK_STRENGTHENING_BATCH_SUMMARY_SCHEMA = (
    "section_321_328_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_summary_v1"
)
POST_RECREATION_ACTOR_BP_READBACK_STRENGTHENING_RESULT_SCHEMA = (
    "section_321_328_post_recreation_actor_bp_readback_strengthening_result_v1"
)
SECTION_313_320_POST_RECREATION_ACTOR_BP_REAUTHORING_ACTUAL_SUMMARY_SCHEMA = (
    reauthoring
    .DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_ACTOR_BP_REAUTHORING_ACTUAL_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = reauthoring.DEFAULT_TARGET_ASSET_PATH
DEFAULT_TARGET_ROOT = reauthoring.DEFAULT_TARGET_ROOT
DEFAULT_GENERATED_CLASS_PATH = reauthoring.DEFAULT_GENERATED_CLASS_PATH
DEFAULT_BLUEPRINT_CLASS_NAME = reauthoring.DEFAULT_BLUEPRINT_CLASS_NAME
DEFAULT_CDO_CLASS_NAME = reauthoring.DEFAULT_CDO_CLASS_NAME
DEFAULT_CONTENT_FILE_SIZE = reauthoring.DEFAULT_CONTENT_FILE_SIZE_AFTER
DEFAULT_VARIABLE_NAME = reauthoring.DEFAULT_VARIABLE_NAME
DEFAULT_VARIABLE_VALUE = reauthoring.DEFAULT_VARIABLE_VALUE
DEFAULT_COMPONENT_NAME = reauthoring.DEFAULT_COMPONENT_NAME
DEFAULT_COMPONENT_CLASS = reauthoring.DEFAULT_COMPONENT_CLASS
DEFAULT_TAG_NAME = reauthoring.DEFAULT_TAG_NAME
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_post_recreation_actor_bp_reauthoring_actual_batch_count",
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
    "final_durable_release_ready_count",
)
UPSTREAM_DESTRUCTIVE_OUTPUTS_CLOSED_COUNT_KEYS = (
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
POST_RECREATION_READBACK_STRENGTHENING_PATH_COUNT_KEYS = (
    "section_321_readback_strengthening_checkpoint_satisfied_count",
    "section_322_recreated_actor_bp_readback_route_ready_count",
    "section_323_variable_default_reread_verified_count",
    "section_324_default_tag_reread_verified_count",
    "section_325_raw_component_duplicate_handles_detected_count",
    "section_326_unique_component_identity_verified_count",
    "section_327_readback_no_write_dirty_boundary_verified_count",
    "section_328_readback_strengthening_release_ready_count",
    "post_recreation_actor_bp_readback_strengthened_count",
    "post_recreation_actor_bp_unique_component_identity_verified_count",
)
BLOCKED_READBACK_STRENGTHENING_OUTPUT_COUNT_KEYS = (
    "variable_add_command_dispatched_count",
    "variable_add_command_executed_count",
    "component_add_command_dispatched_count",
    "component_add_command_executed_count",
    "default_write_command_dispatched_count",
    "default_write_command_executed_count",
    "actor_bp_authoring_command_dispatched_count",
    "actor_bp_authoring_command_executed_count",
    "actor_bp_authoring_compile_dispatched_count",
    "actor_bp_authoring_compile_executed_count",
    "actor_bp_authoring_save_dispatched_count",
    "actor_bp_authoring_save_executed_count",
    "actor_bp_authoring_asset_write_performed_count",
    "actor_bp_authoring_package_dirty_marked_count",
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


def build_post_recreation_actor_bp_readback_strengthening_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_root: str = DEFAULT_TARGET_ROOT,
    target_under_expected_root: bool = True,
    asset_exists: bool = True,
    asset_data_valid: bool = True,
    content_file_exists: bool = True,
    content_file_size: int = DEFAULT_CONTENT_FILE_SIZE,
    blueprint_class_name: str = DEFAULT_BLUEPRINT_CLASS_NAME,
    generated_class_path: str = DEFAULT_GENERATED_CLASS_PATH,
    cdo_class_name: str = DEFAULT_CDO_CLASS_NAME,
    cdo_is_actor: bool = True,
    scalar_default_after: float = DEFAULT_VARIABLE_VALUE,
    variable_readback_verified: bool = True,
    tag_exists_after: bool = True,
    matching_component_handle_count: int = 2,
    unique_component_identity_count: int = 1,
    unique_component_name: str = DEFAULT_COMPONENT_NAME,
    unique_component_class: str = DEFAULT_COMPONENT_CLASS,
    raw_duplicate_component_handles_detected: bool = True,
    component_readback_verified: bool = True,
    readback_strengthened: bool = True,
    target_dirty_after_readback: bool = False,
    dirty_maps_after_readback: Sequence[str] = (),
    external_dirty_after_readback: Sequence[str] = (),
    variable_add_command_dispatched: bool = False,
    variable_add_command_executed: bool = False,
    component_add_command_dispatched: bool = False,
    component_add_command_executed: bool = False,
    default_write_command_dispatched: bool = False,
    default_write_command_executed: bool = False,
    actor_bp_authoring_command_dispatched: bool = False,
    actor_bp_authoring_command_executed: bool = False,
    actor_bp_authoring_compile_dispatched: bool = False,
    actor_bp_authoring_compile_executed: bool = False,
    actor_bp_authoring_save_dispatched: bool = False,
    actor_bp_authoring_save_executed: bool = False,
    actor_bp_authoring_asset_write_performed: bool = False,
    actor_bp_authoring_package_dirty_marked: bool = False,
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
        "schema": POST_RECREATION_ACTOR_BP_READBACK_STRENGTHENING_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_root": target_root,
        "target_under_expected_root": target_under_expected_root,
        "asset_exists": asset_exists,
        "asset_data_valid": asset_data_valid,
        "content_file_exists": content_file_exists,
        "content_file_size": content_file_size,
        "blueprint_class_name": blueprint_class_name,
        "generated_class_path": generated_class_path,
        "cdo_class_name": cdo_class_name,
        "cdo_is_actor": cdo_is_actor,
        "scalar_default_after": scalar_default_after,
        "variable_readback_verified": variable_readback_verified,
        "tag_exists_after": tag_exists_after,
        "matching_component_handle_count": matching_component_handle_count,
        "unique_component_identity_count": unique_component_identity_count,
        "unique_component_name": unique_component_name,
        "unique_component_class": unique_component_class,
        "raw_duplicate_component_handles_detected": (
            raw_duplicate_component_handles_detected
        ),
        "component_readback_verified": component_readback_verified,
        "readback_strengthened": readback_strengthened,
        "target_dirty_after_readback": target_dirty_after_readback,
        "dirty_maps_after_readback": list(dirty_maps_after_readback),
        "external_dirty_after_readback": list(external_dirty_after_readback),
        "variable_add_command_dispatched": variable_add_command_dispatched,
        "variable_add_command_executed": variable_add_command_executed,
        "component_add_command_dispatched": component_add_command_dispatched,
        "component_add_command_executed": component_add_command_executed,
        "default_write_command_dispatched": default_write_command_dispatched,
        "default_write_command_executed": default_write_command_executed,
        "actor_bp_authoring_command_dispatched": actor_bp_authoring_command_dispatched,
        "actor_bp_authoring_command_executed": actor_bp_authoring_command_executed,
        "actor_bp_authoring_compile_dispatched": actor_bp_authoring_compile_dispatched,
        "actor_bp_authoring_compile_executed": actor_bp_authoring_compile_executed,
        "actor_bp_authoring_save_dispatched": actor_bp_authoring_save_dispatched,
        "actor_bp_authoring_save_executed": actor_bp_authoring_save_executed,
        "actor_bp_authoring_asset_write_performed": actor_bp_authoring_asset_write_performed,
        "actor_bp_authoring_package_dirty_marked": actor_bp_authoring_package_dirty_marked,
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


def build_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract(
    requested: bool,
    section_313_320_post_recreation_actor_bp_reauthoring_actual_summary: Dict[str, Any],
    post_recreation_actor_bp_readback_strengthening_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_313_320_summary_schema_matches = bool(
        section_313_320_post_recreation_actor_bp_reauthoring_actual_summary.get(
            "schema"
        )
        == SECTION_313_320_POST_RECREATION_ACTOR_BP_REAUTHORING_ACTUAL_SUMMARY_SCHEMA
    )
    section_313_320_summary_passed = bool(
        section_313_320_post_recreation_actor_bp_reauthoring_actual_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_reauthoring_ready = all(
        _count_is_one(
            section_313_320_post_recreation_actor_bp_reauthoring_actual_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_destructive_outputs_closed = all(
        _count_is_zero(
            section_313_320_post_recreation_actor_bp_reauthoring_actual_summary,
            key,
        )
        for key in UPSTREAM_DESTRUCTIVE_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        post_recreation_actor_bp_readback_strengthening_result.get("schema")
        == POST_RECREATION_ACTOR_BP_READBACK_STRENGTHENING_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_313_320_summary_schema_matches
        and section_313_320_summary_passed
        and upstream_reauthoring_ready
        and upstream_destructive_outputs_closed
    )
    target_readback_ready = bool(
        post_recreation_actor_bp_readback_strengthening_result.get(
            "target_asset_path"
        )
        == DEFAULT_TARGET_ASSET_PATH
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "target_root"
        )
        == DEFAULT_TARGET_ROOT
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "target_under_expected_root"
        )
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "asset_exists"
        )
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "asset_data_valid"
        )
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "content_file_exists"
        )
        and int(
            post_recreation_actor_bp_readback_strengthening_result.get(
                "content_file_size", 0
            )
            or 0
        )
        > 0
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "blueprint_class_name"
        )
        == DEFAULT_BLUEPRINT_CLASS_NAME
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "generated_class_path"
        )
        == DEFAULT_GENERATED_CLASS_PATH
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "cdo_class_name"
        )
        == DEFAULT_CDO_CLASS_NAME
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "cdo_is_actor"
        )
    )
    variable_default_reread_verified = bool(
        post_recreation_actor_bp_readback_strengthening_result.get(
            "variable_readback_verified"
        )
        and float(
            post_recreation_actor_bp_readback_strengthening_result.get(
                "scalar_default_after", -1
            )
        )
        == DEFAULT_VARIABLE_VALUE
    )
    default_tag_reread_verified = bool(
        post_recreation_actor_bp_readback_strengthening_result.get(
            "tag_exists_after"
        )
    )
    raw_duplicate_handles_detected = bool(
        int(
            post_recreation_actor_bp_readback_strengthening_result.get(
                "matching_component_handle_count", 0
            )
            or 0
        )
        > int(
            post_recreation_actor_bp_readback_strengthening_result.get(
                "unique_component_identity_count", 0
            )
            or 0
        )
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "raw_duplicate_component_handles_detected"
        )
    )
    unique_component_identity_verified = bool(
        post_recreation_actor_bp_readback_strengthening_result.get(
            "unique_component_identity_count"
        )
        == 1
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "unique_component_name"
        )
        == DEFAULT_COMPONENT_NAME
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "unique_component_class"
        )
        == DEFAULT_COMPONENT_CLASS
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "component_readback_verified"
        )
    )
    no_write_dirty_boundary_verified = bool(
        not post_recreation_actor_bp_readback_strengthening_result.get(
            "target_dirty_after_readback"
        )
        and not post_recreation_actor_bp_readback_strengthening_result.get(
            "dirty_maps_after_readback"
        )
        and all(
            not post_recreation_actor_bp_readback_strengthening_result.get(key)
            for key in BLOCKED_READBACK_STRENGTHENING_OUTPUT_COUNT_KEYS
        )
    )
    result_has_no_error = bool(
        post_recreation_actor_bp_readback_strengthening_result.get("error")
        in (None, "")
    )
    strengthened = bool(
        checkpoint_satisfied
        and result_schema_matches
        and target_readback_ready
        and variable_default_reread_verified
        and default_tag_reread_verified
        and raw_duplicate_handles_detected
        and unique_component_identity_verified
        and no_write_dirty_boundary_verified
        and post_recreation_actor_bp_readback_strengthening_result.get(
            "readback_strengthened"
        )
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_ACTOR_BP_READBACK_STRENGTHENING_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_313_320_summary_schema_matches": (
            section_313_320_summary_schema_matches
        ),
        "section_313_320_summary_passed": section_313_320_summary_passed,
        "section_313_320_post_recreation_reauthoring_ready": (
            upstream_reauthoring_ready
        ),
        "section_313_320_destructive_outputs_closed": (
            upstream_destructive_outputs_closed
        ),
        "result_schema_matches": result_schema_matches,
        "readback_strengthening_checkpoint_satisfied": checkpoint_satisfied,
        "recreated_actor_bp_readback_route_ready": target_readback_ready,
        "variable_default_reread_verified": variable_default_reread_verified,
        "default_tag_reread_verified": default_tag_reread_verified,
        "raw_component_duplicate_handles_detected": raw_duplicate_handles_detected,
        "unique_component_identity_verified": unique_component_identity_verified,
        "readback_no_write_dirty_boundary_verified": (
            no_write_dirty_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_321_readback_strengthening_checkpoint_satisfied": strengthened,
        "section_322_recreated_actor_bp_readback_route_ready": strengthened,
        "section_323_variable_default_reread_verified": strengthened,
        "section_324_default_tag_reread_verified": strengthened,
        "section_325_raw_component_duplicate_handles_detected": strengthened,
        "section_326_unique_component_identity_verified": strengthened,
        "section_327_readback_no_write_dirty_boundary_verified": strengthened,
        "section_328_readback_strengthening_release_ready": strengthened,
        "post_recreation_actor_bp_readback_strengthened": strengthened,
        "post_recreation_actor_bp_unique_component_identity_verified": (
            strengthened
        ),
        "final_durable_release_ready": strengthened,
        **{
            key: 1 if strengthened else 0
            for key in POST_RECREATION_READBACK_STRENGTHENING_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_READBACK_STRENGTHENING_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "post_recreation_actor_bp_readback_strengthened"
            )
            == len(requested)
            and _truthy_count(
                requested,
                "post_recreation_actor_bp_unique_component_identity_verified",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_READBACK_STRENGTHENING_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_ACTOR_BP_READBACK_STRENGTHENING_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_count": (
            len(requested)
        ),
        "section_313_320_summary_schema_matches_count": _truthy_count(
            requested, "section_313_320_summary_schema_matches"
        ),
        "section_313_320_summary_passed_count": _truthy_count(
            requested, "section_313_320_summary_passed"
        ),
        "section_313_320_post_recreation_reauthoring_ready_count": (
            _truthy_count(
                requested,
                "section_313_320_post_recreation_reauthoring_ready",
            )
        ),
        "section_313_320_destructive_outputs_closed_count": _truthy_count(
            requested, "section_313_320_destructive_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "readback_strengthening_checkpoint_satisfied_count": _truthy_count(
            requested, "readback_strengthening_checkpoint_satisfied"
        ),
        "recreated_actor_bp_readback_route_ready_count": _truthy_count(
            requested, "recreated_actor_bp_readback_route_ready"
        ),
        "variable_default_reread_verified_count": _truthy_count(
            requested, "variable_default_reread_verified"
        ),
        "default_tag_reread_verified_count": _truthy_count(
            requested, "default_tag_reread_verified"
        ),
        "raw_component_duplicate_handles_detected_count": _truthy_count(
            requested, "raw_component_duplicate_handles_detected"
        ),
        "unique_component_identity_verified_count": _truthy_count(
            requested, "unique_component_identity_verified"
        ),
        "readback_no_write_dirty_boundary_verified_count": _truthy_count(
            requested, "readback_no_write_dirty_boundary_verified"
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
            for key in POST_RECREATION_READBACK_STRENGTHENING_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_READBACK_STRENGTHENING_OUTPUT_COUNT_KEYS
        }
    )
    return summary
