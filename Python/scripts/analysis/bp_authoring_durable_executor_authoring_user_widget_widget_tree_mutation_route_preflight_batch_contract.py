#!/usr/bin/env python
"""
Sections 417-424 durable executor UserWidget WidgetTree mutation route preflight.

This contract follows the actual temp Widget Blueprint creation checkpoint. It
records a read-only Unreal preflight against the temp Widget Blueprint plus a
static UnrealMCP UMG command-route review. Python cannot access the protected
WidgetTree route, while the existing C++ route can mutate WidgetTree but still
lacks _MCP_Temp target-path and no-save hardening. Actual WidgetTree mutation,
compile/save, delete, rename, overwrite, cleanup, and production writes remain
closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract as actual_checkpoint


DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_BATCH_SCHEMA = (
    "section_417_424_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_BATCH_SUMMARY_SCHEMA = (
    "section_417_424_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_summary_v1"
)
USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_RESULT_SCHEMA = (
    "section_417_424_user_widget_widget_tree_mutation_route_preflight_result_v1"
)
SECTION_409_416_USER_WIDGET_ACTUAL_ASSET_CHECKPOINT_SUMMARY_SCHEMA = (
    actual_checkpoint
    .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_ACTUAL_ASSET_CREATION_CHECKPOINT_BATCH_SUMMARY_SCHEMA
)

DEFAULT_PROJECT_FILE_PATH = "D:/Git/CubelessStylized/StylizedCubeless.uproject"
DEFAULT_TARGET_ASSET_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/UserWidgetActual/WBP_DurableWidgetTreeActual"
)
DEFAULT_TARGET_NAME = "WBP_DurableWidgetTreeActual"
DEFAULT_TARGET_PACKAGE_FILE = (
    "D:/Git/CubelessStylized/Content/_MCP_Temp/DurableSaveGate/UserWidgetActual/WBP_DurableWidgetTreeActual.uasset"
)
DEFAULT_TARGET_GENERATED_CLASS_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/UserWidgetActual/WBP_DurableWidgetTreeActual.WBP_DurableWidgetTreeActual_C"
)
DEFAULT_PACKAGE_FILE_SIZE_BYTES = 21229
DEFAULT_ASSET_CLASS = "WidgetBlueprint"
DEFAULT_UMG_CPP_SOURCE_PATH = (
    "D:/Git/CubelessStylized/Plugins/UnrealMCP/Source/UnrealMCP/Private/Commands/UnrealMCPUMGCommands.cpp"
)
DEFAULT_BRIDGE_CPP_SOURCE_PATH = (
    "D:/Git/CubelessStylized/Plugins/UnrealMCP/Source/UnrealMCP/Private/UnrealMCPBridge.cpp"
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_count",
    "section_401_408_summary_schema_matches_count",
    "section_401_408_summary_passed_count",
    "section_401_408_user_widget_dry_run_ready_count",
    "section_401_408_outputs_closed_count",
    "result_schema_matches_count",
    "user_widget_actual_creation_checkpoint_satisfied_count",
    "user_widget_actual_target_scope_verified_count",
    "widget_blueprint_create_or_reuse_executed_count",
    "widget_blueprint_compile_save_verified_count",
    "widget_blueprint_readback_package_confirmed_count",
    "widget_tree_mutation_still_blocked_count",
    "user_widget_delete_rename_cleanup_production_blocked_count",
    "user_widget_actual_creation_no_dirty_leftover_count",
    "result_has_no_error_count",
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
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    actual_checkpoint
    .BLOCKED_USER_WIDGET_ACTUAL_ASSET_OUTPUT_COUNT_KEYS
)

USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_PATH_COUNT_KEYS = (
    "section_417_user_widget_widget_tree_route_preflight_checkpoint_satisfied_count",
    "section_418_user_widget_actual_temp_asset_readonly_confirmed_count",
    "section_419_python_widget_tree_mutation_route_blocked_count",
    "section_420_unreal_mcp_umg_cpp_route_detected_count",
    "section_421_umg_cpp_route_safe_gate_hardening_required_count",
    "section_422_widget_tree_mutation_execution_outputs_blocked_count",
    "section_423_user_widget_widget_tree_route_preflight_no_write_boundary_verified_count",
    "section_424_user_widget_widget_tree_mutation_route_preflight_release_ready_count",
    "user_widget_widget_tree_mutation_route_preflight_ready_count",
    "user_widget_widget_tree_actual_mutation_still_blocked_count",
    "cpp_route_hardening_required_count",
)
BLOCKED_USER_WIDGET_WIDGET_TREE_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS = (
    "compile_executed_count",
    "save_executed_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
    "widget_tree_mutation_command_dispatched_count",
    "widget_tree_mutation_command_executed_count",
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
BLOCKED_USER_WIDGET_WIDGET_TREE_ROUTE_PREFLIGHT_RESULT_KEYS = (
    "compile_executed",
    "save_executed",
    "asset_write_performed",
    "package_dirty_marked",
    "widget_tree_mutation_command_dispatched",
    "widget_tree_mutation_command_executed",
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


def build_user_widget_widget_tree_mutation_route_preflight_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_name: str = DEFAULT_TARGET_NAME,
    target_package_file: str = DEFAULT_TARGET_PACKAGE_FILE,
    target_package_file_size_bytes: int = DEFAULT_PACKAGE_FILE_SIZE_BYTES,
    target_asset_exists: bool = True,
    target_package_file_exists: bool = True,
    asset_loaded: bool = True,
    asset_class: str = DEFAULT_ASSET_CLASS,
    generated_class_present: bool = True,
    generated_class_path: str = DEFAULT_TARGET_GENERATED_CLASS_PATH,
    python_widget_tree_class_available: bool = False,
    python_widget_tree_property_accessible: bool = False,
    python_construct_widget_route_ready: bool = False,
    widget_tree_protected_access_error_count: int = 3,
    canvas_panel_class_available: bool = True,
    canvas_panel_add_child_to_canvas_available: bool = True,
    button_class_available: bool = True,
    text_block_class_available: bool = True,
    cpp_umg_commands_source_path: str = DEFAULT_UMG_CPP_SOURCE_PATH,
    cpp_bridge_source_path: str = DEFAULT_BRIDGE_CPP_SOURCE_PATH,
    unreal_mcp_umg_cpp_route_detected: bool = True,
    cpp_create_umg_widget_blueprint_registered: bool = True,
    cpp_add_text_block_to_widget_registered: bool = True,
    cpp_add_button_to_widget_registered: bool = True,
    cpp_bind_widget_event_registered: bool = True,
    cpp_uses_widget_tree_construct_widget: bool = True,
    cpp_uses_root_widget: bool = True,
    cpp_uses_add_child_to_canvas: bool = True,
    cpp_uses_compile_blueprint: bool = True,
    cpp_immediate_save_asset_present: bool = True,
    cpp_fixed_game_widgets_path_present: bool = True,
    cpp_safe_target_path_parameter_present: bool = False,
    cpp_no_save_mode_present: bool = False,
    cpp_temp_scope_gate_present: bool = False,
    cpp_delete_rename_cleanup_commands_present: bool = False,
    dirty_content_before: Sequence[str] = (),
    dirty_content_after: Sequence[str] = (),
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    target_dirty_after: bool = False,
    compile_executed: bool = False,
    save_executed: bool = False,
    asset_write_performed: bool = False,
    package_dirty_marked: bool = False,
    widget_tree_mutation_command_dispatched: bool = False,
    widget_tree_mutation_command_executed: bool = False,
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
        "schema": USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_RESULT_SCHEMA,
        "project_file_path": project_file_path,
        "target_asset_path": target_asset_path,
        "target_name": target_name,
        "target_package_file": target_package_file,
        "target_package_file_size_bytes": target_package_file_size_bytes,
        "target_asset_exists": target_asset_exists,
        "target_package_file_exists": target_package_file_exists,
        "asset_loaded": asset_loaded,
        "asset_class": asset_class,
        "generated_class_present": generated_class_present,
        "generated_class_path": generated_class_path,
        "python_widget_tree_class_available": python_widget_tree_class_available,
        "python_widget_tree_property_accessible": (
            python_widget_tree_property_accessible
        ),
        "python_construct_widget_route_ready": python_construct_widget_route_ready,
        "widget_tree_protected_access_error_count": (
            widget_tree_protected_access_error_count
        ),
        "canvas_panel_class_available": canvas_panel_class_available,
        "canvas_panel_add_child_to_canvas_available": (
            canvas_panel_add_child_to_canvas_available
        ),
        "button_class_available": button_class_available,
        "text_block_class_available": text_block_class_available,
        "cpp_umg_commands_source_path": cpp_umg_commands_source_path,
        "cpp_bridge_source_path": cpp_bridge_source_path,
        "unreal_mcp_umg_cpp_route_detected": unreal_mcp_umg_cpp_route_detected,
        "cpp_create_umg_widget_blueprint_registered": (
            cpp_create_umg_widget_blueprint_registered
        ),
        "cpp_add_text_block_to_widget_registered": (
            cpp_add_text_block_to_widget_registered
        ),
        "cpp_add_button_to_widget_registered": cpp_add_button_to_widget_registered,
        "cpp_bind_widget_event_registered": cpp_bind_widget_event_registered,
        "cpp_uses_widget_tree_construct_widget": (
            cpp_uses_widget_tree_construct_widget
        ),
        "cpp_uses_root_widget": cpp_uses_root_widget,
        "cpp_uses_add_child_to_canvas": cpp_uses_add_child_to_canvas,
        "cpp_uses_compile_blueprint": cpp_uses_compile_blueprint,
        "cpp_immediate_save_asset_present": cpp_immediate_save_asset_present,
        "cpp_fixed_game_widgets_path_present": cpp_fixed_game_widgets_path_present,
        "cpp_safe_target_path_parameter_present": (
            cpp_safe_target_path_parameter_present
        ),
        "cpp_no_save_mode_present": cpp_no_save_mode_present,
        "cpp_temp_scope_gate_present": cpp_temp_scope_gate_present,
        "cpp_delete_rename_cleanup_commands_present": (
            cpp_delete_rename_cleanup_commands_present
        ),
        "dirty_content_before": list(dirty_content_before),
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "target_dirty_after": target_dirty_after,
        "compile_executed": compile_executed,
        "save_executed": save_executed,
        "asset_write_performed": asset_write_performed,
        "package_dirty_marked": package_dirty_marked,
        "widget_tree_mutation_command_dispatched": (
            widget_tree_mutation_command_dispatched
        ),
        "widget_tree_mutation_command_executed": (
            widget_tree_mutation_command_executed
        ),
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


def build_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract(
    requested: bool,
    section_409_416_user_widget_actual_asset_checkpoint_summary: Dict[str, Any],
    user_widget_widget_tree_mutation_route_preflight_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_409_416_summary_schema_matches = bool(
        section_409_416_user_widget_actual_asset_checkpoint_summary.get("schema")
        == SECTION_409_416_USER_WIDGET_ACTUAL_ASSET_CHECKPOINT_SUMMARY_SCHEMA
    )
    section_409_416_summary_passed = bool(
        section_409_416_user_widget_actual_asset_checkpoint_summary.get("status")
        == "passed"
    )
    upstream_checkpoint_ready = all(
        _count_is_one(
            section_409_416_user_widget_actual_asset_checkpoint_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_409_416_user_widget_actual_asset_checkpoint_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        user_widget_widget_tree_mutation_route_preflight_result.get("schema")
        == USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_409_416_summary_schema_matches
        and section_409_416_summary_passed
        and upstream_checkpoint_ready
        and upstream_outputs_closed
    )
    actual_temp_asset_readonly_confirmed = bool(
        user_widget_widget_tree_mutation_route_preflight_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "target_asset_path"
        )
        == DEFAULT_TARGET_ASSET_PATH
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "target_name"
        )
        == DEFAULT_TARGET_NAME
        and str(
            user_widget_widget_tree_mutation_route_preflight_result.get(
                "target_package_file", ""
            )
        ).replace("\\", "/")
        == DEFAULT_TARGET_PACKAGE_FILE
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "target_asset_exists"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "target_package_file_exists"
        )
        and int(
            user_widget_widget_tree_mutation_route_preflight_result.get(
                "target_package_file_size_bytes", 0
            )
            or 0
        )
        > 0
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "asset_loaded"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "asset_class"
        )
        == DEFAULT_ASSET_CLASS
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "generated_class_present"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "generated_class_path"
        )
        == DEFAULT_TARGET_GENERATED_CLASS_PATH
    )
    python_route_blocked = bool(
        not user_widget_widget_tree_mutation_route_preflight_result.get(
            "python_widget_tree_class_available"
        )
        and not user_widget_widget_tree_mutation_route_preflight_result.get(
            "python_widget_tree_property_accessible"
        )
        and not user_widget_widget_tree_mutation_route_preflight_result.get(
            "python_construct_widget_route_ready"
        )
        and int(
            user_widget_widget_tree_mutation_route_preflight_result.get(
                "widget_tree_protected_access_error_count", 0
            )
            or 0
        )
        >= 1
    )
    cpp_route_detected = bool(
        user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_umg_commands_source_path"
        )
        == DEFAULT_UMG_CPP_SOURCE_PATH
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_bridge_source_path"
        )
        == DEFAULT_BRIDGE_CPP_SOURCE_PATH
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "unreal_mcp_umg_cpp_route_detected"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_create_umg_widget_blueprint_registered"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_add_text_block_to_widget_registered"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_add_button_to_widget_registered"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_bind_widget_event_registered"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_uses_widget_tree_construct_widget"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_uses_root_widget"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_uses_add_child_to_canvas"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_uses_compile_blueprint"
        )
    )
    cpp_route_hardening_required = bool(
        cpp_route_detected
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_fixed_game_widgets_path_present"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_immediate_save_asset_present"
        )
        and not user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_safe_target_path_parameter_present"
        )
        and not user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_no_save_mode_present"
        )
        and not user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_temp_scope_gate_present"
        )
        and not user_widget_widget_tree_mutation_route_preflight_result.get(
            "cpp_delete_rename_cleanup_commands_present"
        )
    )
    execution_outputs_blocked = bool(
        all(
            not user_widget_widget_tree_mutation_route_preflight_result.get(key)
            for key in BLOCKED_USER_WIDGET_WIDGET_TREE_ROUTE_PREFLIGHT_RESULT_KEYS
        )
    )
    no_write_boundary_verified = bool(
        execution_outputs_blocked
        and not user_widget_widget_tree_mutation_route_preflight_result.get(
            "target_dirty_after"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "dirty_content_before"
        )
        == user_widget_widget_tree_mutation_route_preflight_result.get(
            "dirty_content_after"
        )
        and user_widget_widget_tree_mutation_route_preflight_result.get(
            "dirty_maps_before"
        )
        == user_widget_widget_tree_mutation_route_preflight_result.get(
            "dirty_maps_after"
        )
        and not user_widget_widget_tree_mutation_route_preflight_result.get(
            "dirty_content_after"
        )
        and not user_widget_widget_tree_mutation_route_preflight_result.get(
            "dirty_maps_after"
        )
    )
    result_has_no_error = bool(
        user_widget_widget_tree_mutation_route_preflight_result.get("error")
        in (None, "")
    )
    preflight_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and actual_temp_asset_readonly_confirmed
        and python_route_blocked
        and cpp_route_detected
        and cpp_route_hardening_required
        and execution_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_409_416_summary_schema_matches": (
            section_409_416_summary_schema_matches
        ),
        "section_409_416_summary_passed": section_409_416_summary_passed,
        "section_409_416_user_widget_actual_checkpoint_ready": (
            upstream_checkpoint_ready
        ),
        "section_409_416_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "user_widget_widget_tree_route_preflight_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "user_widget_actual_temp_asset_readonly_confirmed": (
            actual_temp_asset_readonly_confirmed
        ),
        "python_widget_tree_mutation_route_blocked": python_route_blocked,
        "unreal_mcp_umg_cpp_route_detected": cpp_route_detected,
        "umg_cpp_route_safe_gate_hardening_required": (
            cpp_route_hardening_required
        ),
        "widget_tree_mutation_execution_outputs_blocked": (
            execution_outputs_blocked
        ),
        "user_widget_widget_tree_route_preflight_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_417_user_widget_widget_tree_route_preflight_checkpoint_satisfied": (
            preflight_ready
        ),
        "section_418_user_widget_actual_temp_asset_readonly_confirmed": (
            preflight_ready
        ),
        "section_419_python_widget_tree_mutation_route_blocked": (
            preflight_ready
        ),
        "section_420_unreal_mcp_umg_cpp_route_detected": preflight_ready,
        "section_421_umg_cpp_route_safe_gate_hardening_required": (
            preflight_ready
        ),
        "section_422_widget_tree_mutation_execution_outputs_blocked": (
            preflight_ready
        ),
        "section_423_user_widget_widget_tree_route_preflight_no_write_boundary_verified": (
            preflight_ready
        ),
        "section_424_user_widget_widget_tree_mutation_route_preflight_release_ready": (
            preflight_ready
        ),
        "user_widget_widget_tree_mutation_route_preflight_ready": (
            preflight_ready
        ),
        "user_widget_widget_tree_actual_mutation_still_blocked": (
            preflight_ready
        ),
        "cpp_route_hardening_required": preflight_ready,
        "final_durable_release_ready": preflight_ready,
        **{
            key: 1 if preflight_ready else 0
            for key in USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_USER_WIDGET_WIDGET_TREE_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "user_widget_widget_tree_mutation_route_preflight_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "user_widget_widget_tree_actual_mutation_still_blocked",
            )
            == len(requested)
            and _truthy_count(requested, "cpp_route_hardening_required") == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_USER_WIDGET_WIDGET_TREE_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_count": (
            len(requested)
        ),
        "section_409_416_summary_schema_matches_count": _truthy_count(
            requested, "section_409_416_summary_schema_matches"
        ),
        "section_409_416_summary_passed_count": _truthy_count(
            requested, "section_409_416_summary_passed"
        ),
        "section_409_416_user_widget_actual_checkpoint_ready_count": (
            _truthy_count(
                requested,
                "section_409_416_user_widget_actual_checkpoint_ready",
            )
        ),
        "section_409_416_outputs_closed_count": _truthy_count(
            requested, "section_409_416_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "user_widget_widget_tree_route_preflight_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "user_widget_widget_tree_route_preflight_checkpoint_satisfied",
            )
        ),
        "user_widget_actual_temp_asset_readonly_confirmed_count": _truthy_count(
            requested, "user_widget_actual_temp_asset_readonly_confirmed"
        ),
        "python_widget_tree_mutation_route_blocked_count": _truthy_count(
            requested, "python_widget_tree_mutation_route_blocked"
        ),
        "unreal_mcp_umg_cpp_route_detected_count": _truthy_count(
            requested, "unreal_mcp_umg_cpp_route_detected"
        ),
        "umg_cpp_route_safe_gate_hardening_required_count": _truthy_count(
            requested, "umg_cpp_route_safe_gate_hardening_required"
        ),
        "widget_tree_mutation_execution_outputs_blocked_count": _truthy_count(
            requested, "widget_tree_mutation_execution_outputs_blocked"
        ),
        "user_widget_widget_tree_route_preflight_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "user_widget_widget_tree_route_preflight_no_write_boundary_verified",
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
            for key in USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_USER_WIDGET_WIDGET_TREE_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
        }
    )
    return summary
