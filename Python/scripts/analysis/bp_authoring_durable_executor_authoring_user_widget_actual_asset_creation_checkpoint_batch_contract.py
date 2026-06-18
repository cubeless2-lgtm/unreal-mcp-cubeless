#!/usr/bin/env python
"""
Sections 409-416 durable executor UserWidget actual temp asset creation checkpoint.

This contract follows the UserWidget widget-tree authoring dry-run admission.
It records the approved correct-project headless Unreal execution that creates
or reuses a disposable Widget Blueprint under _MCP_Temp, compiles it, saves it,
and verifies package/readback state. WidgetTree mutation, root/child widget
authoring, slot/binding mutation, delete, rename, overwrite, cleanup, and
production writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract as dry_run
import project_paths


DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_ACTUAL_ASSET_CREATION_CHECKPOINT_BATCH_SCHEMA = (
    "section_409_416_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_ACTUAL_ASSET_CREATION_CHECKPOINT_BATCH_SUMMARY_SCHEMA = (
    "section_409_416_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_summary_v1"
)
USER_WIDGET_ACTUAL_ASSET_CREATION_CHECKPOINT_RESULT_SCHEMA = (
    "section_409_416_user_widget_actual_asset_creation_checkpoint_result_v1"
)
SECTION_401_408_USER_WIDGET_DRY_RUN_ADMISSION_SUMMARY_SCHEMA = (
    dry_run
    .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_AUTHORING_DRY_RUN_ADMISSION_BATCH_SUMMARY_SCHEMA
)
DEFAULT_PROJECT_FILE_PATH = project_paths.default_cubeless_uproject()
DEFAULT_TARGET_DIRECTORY = "/Game/_MCP_Temp/DurableSaveGate/UserWidgetActual"
DEFAULT_TARGET_ASSET_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/UserWidgetActual/WBP_DurableWidgetTreeActual"
)
DEFAULT_TARGET_NAME = "WBP_DurableWidgetTreeActual"
DEFAULT_TARGET_PACKAGE_FILE = project_paths.cubeless_content_path(
    "_MCP_Temp",
    "DurableSaveGate",
    "UserWidgetActual",
    "WBP_DurableWidgetTreeActual.uasset",
)
DEFAULT_ASSET_CLASS = "WidgetBlueprint"
DEFAULT_PACKAGE_FILE_SIZE_BYTES = 21229

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_count",
    "section_401_user_widget_authoring_dry_run_checkpoint_satisfied_count",
    "section_402_widget_blueprint_dry_run_scope_verified_count",
    "section_403_root_widget_plan_classified_count",
    "section_404_child_widget_slot_plan_classified_count",
    "section_405_widget_binding_event_graph_plan_blocked_count",
    "section_406_widget_authoring_creation_mutation_outputs_blocked_count",
    "section_407_user_widget_authoring_dry_run_no_write_boundary_verified_count",
    "section_408_user_widget_authoring_dry_run_admission_release_ready_count",
    "user_widget_widget_tree_authoring_dry_run_admission_ready_count",
    "user_widget_widget_tree_actual_authoring_still_blocked_count",
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    dry_run
    .BLOCKED_USER_WIDGET_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
)

USER_WIDGET_ACTUAL_ASSET_CREATION_CHECKPOINT_PATH_COUNT_KEYS = (
    "section_409_user_widget_actual_creation_checkpoint_satisfied_count",
    "section_410_user_widget_actual_target_scope_verified_count",
    "section_411_widget_blueprint_create_or_reuse_executed_count",
    "section_412_widget_blueprint_compile_save_verified_count",
    "section_413_widget_blueprint_readback_package_confirmed_count",
    "section_414_widget_tree_mutation_still_blocked_count",
    "section_415_user_widget_delete_rename_cleanup_production_blocked_count",
    "section_416_user_widget_actual_asset_creation_checkpoint_release_ready_count",
    "user_widget_actual_asset_creation_checkpoint_ready_count",
    "user_widget_widget_tree_mutation_still_blocked_count",
)
BLOCKED_USER_WIDGET_ACTUAL_ASSET_OUTPUT_COUNT_KEYS = (
    "widget_tree_mutation_attempted_count",
    "widget_tree_mutation_performed_count",
    "root_widget_created_count",
    "child_widget_added_count",
    "widget_slot_mutation_performed_count",
    "widget_binding_mutation_performed_count",
    "event_graph_mutation_performed_count",
    "delete_asset_allowed_count",
    "delete_asset_executed_output_count",
    "rename_asset_allowed_count",
    "rename_command_dispatched_count",
    "rename_command_executed_count",
    "overwrite_allowed_count",
    "overwrite_executed_count",
    "cleanup_allowed_count",
    "cleanup_executed_count",
    "production_path_write_allowed_count",
    "production_path_write_executed_count",
)
BLOCKED_USER_WIDGET_ACTUAL_ASSET_RESULT_KEYS = (
    "widget_tree_mutation_attempted",
    "widget_tree_mutation_performed",
    "root_widget_created",
    "child_widget_added",
    "widget_slot_mutation_performed",
    "widget_binding_mutation_performed",
    "event_graph_mutation_performed",
    "delete_asset_allowed",
    "delete_asset_executed_output",
    "rename_asset_allowed",
    "rename_command_dispatched",
    "rename_command_executed",
    "overwrite_allowed",
    "overwrite_executed",
    "cleanup_allowed",
    "cleanup_executed",
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


def build_user_widget_actual_asset_creation_checkpoint_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_directory: str = DEFAULT_TARGET_DIRECTORY,
    target_name: str = DEFAULT_TARGET_NAME,
    target_package_file: str = DEFAULT_TARGET_PACKAGE_FILE,
    directory_created_or_existing: bool = True,
    asset_preexisted: bool = True,
    asset_created: bool = False,
    asset_loaded: bool = True,
    asset_class: str = DEFAULT_ASSET_CLASS,
    generated_class_present: bool = True,
    compile_executed: bool = True,
    compile_succeeded: bool = True,
    save_executed: bool = True,
    save_succeeded: bool = True,
    package_file_exists: bool = True,
    package_file_size_bytes: int = DEFAULT_PACKAGE_FILE_SIZE_BYTES,
    readback_asset_loaded: bool = True,
    readback_asset_class: str = DEFAULT_ASSET_CLASS,
    readback_generated_class_present: bool = True,
    target_dirty_after: bool = False,
    dirty_content_before: Sequence[str] = (),
    dirty_content_after: Sequence[str] = (),
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    widget_tree_mutation_attempted: bool = False,
    widget_tree_mutation_performed: bool = False,
    root_widget_created: bool = False,
    child_widget_added: bool = False,
    widget_slot_mutation_performed: bool = False,
    widget_binding_mutation_performed: bool = False,
    event_graph_mutation_performed: bool = False,
    delete_asset_allowed: bool = False,
    delete_asset_executed_output: bool = False,
    rename_asset_allowed: bool = False,
    rename_command_dispatched: bool = False,
    rename_command_executed: bool = False,
    overwrite_allowed: bool = False,
    overwrite_executed: bool = False,
    cleanup_allowed: bool = False,
    cleanup_executed: bool = False,
    production_path_write_allowed: bool = False,
    production_path_write_executed: bool = False,
    error: str | None = None,
) -> Dict[str, Any]:
    return {
        "schema": USER_WIDGET_ACTUAL_ASSET_CREATION_CHECKPOINT_RESULT_SCHEMA,
        "project_file_path": project_file_path,
        "target_asset_path": target_asset_path,
        "target_directory": target_directory,
        "target_name": target_name,
        "target_package_file": target_package_file,
        "directory_created_or_existing": directory_created_or_existing,
        "asset_preexisted": asset_preexisted,
        "asset_created": asset_created,
        "asset_loaded": asset_loaded,
        "asset_class": asset_class,
        "generated_class_present": generated_class_present,
        "compile_executed": compile_executed,
        "compile_succeeded": compile_succeeded,
        "save_executed": save_executed,
        "save_succeeded": save_succeeded,
        "package_file_exists": package_file_exists,
        "package_file_size_bytes": package_file_size_bytes,
        "readback_asset_loaded": readback_asset_loaded,
        "readback_asset_class": readback_asset_class,
        "readback_generated_class_present": readback_generated_class_present,
        "target_dirty_after": target_dirty_after,
        "dirty_content_before": list(dirty_content_before),
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "widget_tree_mutation_attempted": widget_tree_mutation_attempted,
        "widget_tree_mutation_performed": widget_tree_mutation_performed,
        "root_widget_created": root_widget_created,
        "child_widget_added": child_widget_added,
        "widget_slot_mutation_performed": widget_slot_mutation_performed,
        "widget_binding_mutation_performed": widget_binding_mutation_performed,
        "event_graph_mutation_performed": event_graph_mutation_performed,
        "delete_asset_allowed": delete_asset_allowed,
        "delete_asset_executed_output": delete_asset_executed_output,
        "rename_asset_allowed": rename_asset_allowed,
        "rename_command_dispatched": rename_command_dispatched,
        "rename_command_executed": rename_command_executed,
        "overwrite_allowed": overwrite_allowed,
        "overwrite_executed": overwrite_executed,
        "cleanup_allowed": cleanup_allowed,
        "cleanup_executed": cleanup_executed,
        "production_path_write_allowed": production_path_write_allowed,
        "production_path_write_executed": production_path_write_executed,
        "error": error,
    }


def build_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract(
    requested: bool,
    section_401_408_user_widget_dry_run_admission_summary: Dict[str, Any],
    user_widget_actual_asset_creation_checkpoint_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_401_408_summary_schema_matches = bool(
        section_401_408_user_widget_dry_run_admission_summary.get("schema")
        == SECTION_401_408_USER_WIDGET_DRY_RUN_ADMISSION_SUMMARY_SCHEMA
    )
    section_401_408_summary_passed = bool(
        section_401_408_user_widget_dry_run_admission_summary.get("status")
        == "passed"
    )
    upstream_dry_run_ready = all(
        _count_is_one(
            section_401_408_user_widget_dry_run_admission_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_401_408_user_widget_dry_run_admission_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        user_widget_actual_asset_creation_checkpoint_result.get("schema")
        == USER_WIDGET_ACTUAL_ASSET_CREATION_CHECKPOINT_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_401_408_summary_schema_matches
        and section_401_408_summary_passed
        and upstream_dry_run_ready
        and upstream_outputs_closed
    )
    target_scope_verified = bool(
        user_widget_actual_asset_creation_checkpoint_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "target_asset_path"
        )
        == DEFAULT_TARGET_ASSET_PATH
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "target_directory"
        )
        == DEFAULT_TARGET_DIRECTORY
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "target_name"
        )
        == DEFAULT_TARGET_NAME
        and str(
            user_widget_actual_asset_creation_checkpoint_result.get(
                "target_package_file", ""
            )
        ).replace("\\", "/")
        == DEFAULT_TARGET_PACKAGE_FILE
    )
    create_or_reuse_executed = bool(
        user_widget_actual_asset_creation_checkpoint_result.get(
            "directory_created_or_existing"
        )
        and (
            user_widget_actual_asset_creation_checkpoint_result.get(
                "asset_created"
            )
            or user_widget_actual_asset_creation_checkpoint_result.get(
                "asset_preexisted"
            )
        )
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "asset_loaded"
        )
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "asset_class"
        )
        == DEFAULT_ASSET_CLASS
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "generated_class_present"
        )
    )
    compile_save_verified = bool(
        user_widget_actual_asset_creation_checkpoint_result.get(
            "compile_executed"
        )
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "compile_succeeded"
        )
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "save_executed"
        )
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "save_succeeded"
        )
    )
    readback_package_confirmed = bool(
        user_widget_actual_asset_creation_checkpoint_result.get(
            "package_file_exists"
        )
        and int(
            user_widget_actual_asset_creation_checkpoint_result.get(
                "package_file_size_bytes", 0
            )
            or 0
        )
        > 0
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "readback_asset_loaded"
        )
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "readback_asset_class"
        )
        == DEFAULT_ASSET_CLASS
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "readback_generated_class_present"
        )
    )
    widget_tree_mutation_still_blocked = all(
        not user_widget_actual_asset_creation_checkpoint_result.get(key)
        for key in (
            "widget_tree_mutation_attempted",
            "widget_tree_mutation_performed",
            "root_widget_created",
            "child_widget_added",
            "widget_slot_mutation_performed",
            "widget_binding_mutation_performed",
            "event_graph_mutation_performed",
        )
    )
    delete_rename_cleanup_production_blocked = all(
        not user_widget_actual_asset_creation_checkpoint_result.get(key)
        for key in (
            "delete_asset_allowed",
            "delete_asset_executed_output",
            "rename_asset_allowed",
            "rename_command_dispatched",
            "rename_command_executed",
            "overwrite_allowed",
            "overwrite_executed",
            "cleanup_allowed",
            "cleanup_executed",
            "production_path_write_allowed",
            "production_path_write_executed",
        )
    )
    no_dirty_leftover = bool(
        not user_widget_actual_asset_creation_checkpoint_result.get(
            "target_dirty_after"
        )
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "dirty_content_before"
        )
        == user_widget_actual_asset_creation_checkpoint_result.get(
            "dirty_content_after"
        )
        and user_widget_actual_asset_creation_checkpoint_result.get(
            "dirty_maps_before"
        )
        == user_widget_actual_asset_creation_checkpoint_result.get(
            "dirty_maps_after"
        )
        and not user_widget_actual_asset_creation_checkpoint_result.get(
            "dirty_content_after"
        )
        and not user_widget_actual_asset_creation_checkpoint_result.get(
            "dirty_maps_after"
        )
    )
    result_has_no_error = bool(
        user_widget_actual_asset_creation_checkpoint_result.get("error")
        in (None, "")
    )
    release_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and target_scope_verified
        and create_or_reuse_executed
        and compile_save_verified
        and readback_package_confirmed
        and widget_tree_mutation_still_blocked
        and delete_rename_cleanup_production_blocked
        and no_dirty_leftover
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_ACTUAL_ASSET_CREATION_CHECKPOINT_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_401_408_summary_schema_matches": (
            section_401_408_summary_schema_matches
        ),
        "section_401_408_summary_passed": section_401_408_summary_passed,
        "section_401_408_user_widget_dry_run_ready": upstream_dry_run_ready,
        "section_401_408_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "user_widget_actual_creation_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "user_widget_actual_target_scope_verified": target_scope_verified,
        "widget_blueprint_create_or_reuse_executed": create_or_reuse_executed,
        "widget_blueprint_compile_save_verified": compile_save_verified,
        "widget_blueprint_readback_package_confirmed": (
            readback_package_confirmed
        ),
        "widget_tree_mutation_still_blocked": widget_tree_mutation_still_blocked,
        "user_widget_delete_rename_cleanup_production_blocked": (
            delete_rename_cleanup_production_blocked
        ),
        "user_widget_actual_creation_no_dirty_leftover": no_dirty_leftover,
        "result_has_no_error": result_has_no_error,
        "section_409_user_widget_actual_creation_checkpoint_satisfied": (
            release_ready
        ),
        "section_410_user_widget_actual_target_scope_verified": release_ready,
        "section_411_widget_blueprint_create_or_reuse_executed": release_ready,
        "section_412_widget_blueprint_compile_save_verified": release_ready,
        "section_413_widget_blueprint_readback_package_confirmed": release_ready,
        "section_414_widget_tree_mutation_still_blocked": release_ready,
        "section_415_user_widget_delete_rename_cleanup_production_blocked": (
            release_ready
        ),
        "section_416_user_widget_actual_asset_creation_checkpoint_release_ready": (
            release_ready
        ),
        "user_widget_actual_asset_creation_checkpoint_ready": release_ready,
        "user_widget_widget_tree_mutation_still_blocked": release_ready,
        "final_durable_release_ready": release_ready,
        **{
            key: 1 if release_ready else 0
            for key in USER_WIDGET_ACTUAL_ASSET_CREATION_CHECKPOINT_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_USER_WIDGET_ACTUAL_ASSET_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "user_widget_actual_asset_creation_checkpoint_ready",
            )
            == len(requested)
            and _truthy_count(
                requested, "user_widget_widget_tree_mutation_still_blocked"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_USER_WIDGET_ACTUAL_ASSET_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_ACTUAL_ASSET_CREATION_CHECKPOINT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_count": (
            len(requested)
        ),
        "section_401_408_summary_schema_matches_count": _truthy_count(
            requested, "section_401_408_summary_schema_matches"
        ),
        "section_401_408_summary_passed_count": _truthy_count(
            requested, "section_401_408_summary_passed"
        ),
        "section_401_408_user_widget_dry_run_ready_count": _truthy_count(
            requested, "section_401_408_user_widget_dry_run_ready"
        ),
        "section_401_408_outputs_closed_count": _truthy_count(
            requested, "section_401_408_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "user_widget_actual_creation_checkpoint_satisfied_count": (
            _truthy_count(
                requested, "user_widget_actual_creation_checkpoint_satisfied"
            )
        ),
        "user_widget_actual_target_scope_verified_count": _truthy_count(
            requested, "user_widget_actual_target_scope_verified"
        ),
        "widget_blueprint_create_or_reuse_executed_count": _truthy_count(
            requested, "widget_blueprint_create_or_reuse_executed"
        ),
        "widget_blueprint_compile_save_verified_count": _truthy_count(
            requested, "widget_blueprint_compile_save_verified"
        ),
        "widget_blueprint_readback_package_confirmed_count": _truthy_count(
            requested, "widget_blueprint_readback_package_confirmed"
        ),
        "widget_tree_mutation_still_blocked_count": _truthy_count(
            requested, "widget_tree_mutation_still_blocked"
        ),
        "user_widget_delete_rename_cleanup_production_blocked_count": (
            _truthy_count(
                requested,
                "user_widget_delete_rename_cleanup_production_blocked",
            )
        ),
        "user_widget_actual_creation_no_dirty_leftover_count": _truthy_count(
            requested, "user_widget_actual_creation_no_dirty_leftover"
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
            for key in USER_WIDGET_ACTUAL_ASSET_CREATION_CHECKPOINT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_USER_WIDGET_ACTUAL_ASSET_OUTPUT_COUNT_KEYS
        }
    )
    return summary
