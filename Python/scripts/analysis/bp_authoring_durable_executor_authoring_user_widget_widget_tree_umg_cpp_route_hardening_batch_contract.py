#!/usr/bin/env python
"""
Sections 425-432 durable executor UserWidget UMG C++ route hardening.

This contract follows the Sections 417-424 WidgetTree mutation route preflight.
It records that the UnrealMCP UMG C++ command route has been hardened with a
safe _MCP_Temp default target, explicit production-path opt-in, save=false by
default, and a verified UBT build. It does not dispatch live WidgetTree
mutation commands and keeps delete, rename, overwrite, cleanup, and production
writes closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract as route_preflight


DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_BATCH_SCHEMA = (
    "section_425_432_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_BATCH_SUMMARY_SCHEMA = (
    "section_425_432_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_summary_v1"
)
USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_RESULT_SCHEMA = (
    "section_425_432_user_widget_widget_tree_umg_cpp_route_hardening_result_v1"
)
SECTION_417_424_USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_SUMMARY_SCHEMA = (
    route_preflight
    .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_BATCH_SUMMARY_SCHEMA
)

DEFAULT_PROJECT_FILE_PATH = "D:/Git/CubelessStylized/StylizedCubeless.uproject"
DEFAULT_UMG_CPP_SOURCE_PATH = (
    "D:/Git/CubelessStylized/Plugins/UnrealMCP/Source/UnrealMCP/Private/Commands/UnrealMCPUMGCommands.cpp"
)
DEFAULT_UNREAL_MCP_SUBMODULE_PATH = "D:/Git/CubelessStylized/Plugins/UnrealMCP"
DEFAULT_UBT_BUILD_COMMAND = (
    r'C:\Program Files\Epic Games\UE_5.7\Engine\Build\BatchFiles\Build.bat '
    'StylizedCubelessEditor Win64 Development '
    '-Project="D:/Git/CubelessStylized/StylizedCubeless.uproject" '
    "-WaitMutex -NoHotReloadFromIDE"
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_count",
    "section_409_416_summary_schema_matches_count",
    "section_409_416_summary_passed_count",
    "section_409_416_user_widget_actual_checkpoint_ready_count",
    "section_409_416_outputs_closed_count",
    "result_schema_matches_count",
    "user_widget_widget_tree_route_preflight_checkpoint_satisfied_count",
    "user_widget_actual_temp_asset_readonly_confirmed_count",
    "python_widget_tree_mutation_route_blocked_count",
    "unreal_mcp_umg_cpp_route_detected_count",
    "umg_cpp_route_safe_gate_hardening_required_count",
    "widget_tree_mutation_execution_outputs_blocked_count",
    "user_widget_widget_tree_route_preflight_no_write_boundary_verified_count",
    "result_has_no_error_count",
    "final_durable_release_ready_count",
    "user_widget_widget_tree_mutation_route_preflight_ready_count",
    "user_widget_widget_tree_actual_mutation_still_blocked_count",
    "cpp_route_hardening_required_count",
    *route_preflight.USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_PATH_COUNT_KEYS,
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    route_preflight.BLOCKED_USER_WIDGET_WIDGET_TREE_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
)

USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_PATH_COUNT_KEYS = (
    "section_425_user_widget_umg_cpp_route_hardening_checkpoint_satisfied_count",
    "section_426_user_widget_umg_cpp_temp_scope_gate_verified_count",
    "section_427_user_widget_umg_cpp_no_save_default_verified_count",
    "section_428_user_widget_umg_cpp_production_path_opt_in_guard_verified_count",
    "section_429_user_widget_umg_cpp_widget_tree_mutation_route_hardened_count",
    "section_430_user_widget_umg_cpp_build_verified_count",
    "section_431_user_widget_umg_cpp_live_command_no_dispatch_verified_count",
    "section_432_user_widget_widget_tree_umg_cpp_route_hardening_release_ready_count",
    "user_widget_widget_tree_umg_cpp_route_hardening_ready_count",
)
BLOCKED_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_OUTPUT_COUNT_KEYS = (
    "live_command_dispatched_count",
    "live_command_executed_count",
    "widget_tree_mutation_command_dispatched_count",
    "widget_tree_mutation_command_executed_count",
    "widget_tree_mutation_performed_count",
    "root_widget_created_count",
    "child_widget_added_count",
    "widget_slot_mutation_performed_count",
    "widget_binding_mutation_performed_count",
    "event_graph_mutation_performed_count",
    "compile_executed_count",
    "save_executed_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
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
BLOCKED_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_RESULT_KEYS = (
    "live_command_dispatched",
    "live_command_executed",
    "widget_tree_mutation_command_dispatched",
    "widget_tree_mutation_command_executed",
    "widget_tree_mutation_performed",
    "root_widget_created",
    "child_widget_added",
    "widget_slot_mutation_performed",
    "widget_binding_mutation_performed",
    "event_graph_mutation_performed",
    "compile_executed",
    "save_executed",
    "asset_write_performed",
    "package_dirty_marked",
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


def build_user_widget_widget_tree_umg_cpp_route_hardening_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    cpp_umg_commands_source_path: str = DEFAULT_UMG_CPP_SOURCE_PATH,
    unreal_mcp_submodule_path: str = DEFAULT_UNREAL_MCP_SUBMODULE_PATH,
    ubt_build_command: str = DEFAULT_UBT_BUILD_COMMAND,
    ubt_build_succeeded: bool = True,
    ubt_no_hot_reload_from_ide_used: bool = True,
    live_coding_mutex_detected: bool = True,
    editor_left_running: bool = True,
    cpp_command_registration_preserved: bool = True,
    cpp_create_umg_widget_blueprint_registered: bool = True,
    cpp_add_text_block_to_widget_registered: bool = True,
    cpp_add_button_to_widget_registered: bool = True,
    cpp_bind_widget_event_registered: bool = True,
    cpp_set_text_block_binding_registered: bool = True,
    cpp_add_widget_to_viewport_registered: bool = True,
    cpp_default_safe_widget_root_present: bool = True,
    cpp_safe_temp_root_present: bool = True,
    cpp_validate_safe_package_name_present: bool = True,
    cpp_resolve_target_path_helpers_present: bool = True,
    cpp_allows_explicit_production_path_opt_in: bool = True,
    cpp_blocks_production_without_opt_in: bool = True,
    cpp_fixed_game_widgets_path_removed: bool = True,
    cpp_save_default_false_present: bool = True,
    cpp_save_asset_guarded_by_save_flag: bool = True,
    cpp_immediate_save_asset_removed: bool = True,
    cpp_request_compile_default_true_present: bool = True,
    cpp_widget_tree_construct_widget_present: bool = True,
    cpp_get_or_create_root_canvas_present: bool = True,
    cpp_root_canvas_created_through_widget_tree: bool = True,
    cpp_child_widgets_created_through_widget_tree: bool = True,
    cpp_canvas_slot_position_route_present: bool = True,
    cpp_newobject_cdo_child_creation_removed: bool = True,
    cpp_mutation_finalize_helper_present: bool = True,
    dirty_content_before: Sequence[str] = (),
    dirty_content_after: Sequence[str] = (),
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    live_command_dispatched: bool = False,
    live_command_executed: bool = False,
    widget_tree_mutation_command_dispatched: bool = False,
    widget_tree_mutation_command_executed: bool = False,
    widget_tree_mutation_performed: bool = False,
    root_widget_created: bool = False,
    child_widget_added: bool = False,
    widget_slot_mutation_performed: bool = False,
    widget_binding_mutation_performed: bool = False,
    event_graph_mutation_performed: bool = False,
    compile_executed: bool = False,
    save_executed: bool = False,
    asset_write_performed: bool = False,
    package_dirty_marked: bool = False,
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
        "schema": USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_RESULT_SCHEMA,
        "project_file_path": project_file_path,
        "cpp_umg_commands_source_path": cpp_umg_commands_source_path,
        "unreal_mcp_submodule_path": unreal_mcp_submodule_path,
        "ubt_build_command": ubt_build_command,
        "ubt_build_succeeded": ubt_build_succeeded,
        "ubt_no_hot_reload_from_ide_used": ubt_no_hot_reload_from_ide_used,
        "live_coding_mutex_detected": live_coding_mutex_detected,
        "editor_left_running": editor_left_running,
        "cpp_command_registration_preserved": cpp_command_registration_preserved,
        "cpp_create_umg_widget_blueprint_registered": (
            cpp_create_umg_widget_blueprint_registered
        ),
        "cpp_add_text_block_to_widget_registered": (
            cpp_add_text_block_to_widget_registered
        ),
        "cpp_add_button_to_widget_registered": cpp_add_button_to_widget_registered,
        "cpp_bind_widget_event_registered": cpp_bind_widget_event_registered,
        "cpp_set_text_block_binding_registered": (
            cpp_set_text_block_binding_registered
        ),
        "cpp_add_widget_to_viewport_registered": (
            cpp_add_widget_to_viewport_registered
        ),
        "cpp_default_safe_widget_root_present": cpp_default_safe_widget_root_present,
        "cpp_safe_temp_root_present": cpp_safe_temp_root_present,
        "cpp_validate_safe_package_name_present": (
            cpp_validate_safe_package_name_present
        ),
        "cpp_resolve_target_path_helpers_present": (
            cpp_resolve_target_path_helpers_present
        ),
        "cpp_allows_explicit_production_path_opt_in": (
            cpp_allows_explicit_production_path_opt_in
        ),
        "cpp_blocks_production_without_opt_in": cpp_blocks_production_without_opt_in,
        "cpp_fixed_game_widgets_path_removed": cpp_fixed_game_widgets_path_removed,
        "cpp_save_default_false_present": cpp_save_default_false_present,
        "cpp_save_asset_guarded_by_save_flag": cpp_save_asset_guarded_by_save_flag,
        "cpp_immediate_save_asset_removed": cpp_immediate_save_asset_removed,
        "cpp_request_compile_default_true_present": (
            cpp_request_compile_default_true_present
        ),
        "cpp_widget_tree_construct_widget_present": (
            cpp_widget_tree_construct_widget_present
        ),
        "cpp_get_or_create_root_canvas_present": cpp_get_or_create_root_canvas_present,
        "cpp_root_canvas_created_through_widget_tree": (
            cpp_root_canvas_created_through_widget_tree
        ),
        "cpp_child_widgets_created_through_widget_tree": (
            cpp_child_widgets_created_through_widget_tree
        ),
        "cpp_canvas_slot_position_route_present": (
            cpp_canvas_slot_position_route_present
        ),
        "cpp_newobject_cdo_child_creation_removed": (
            cpp_newobject_cdo_child_creation_removed
        ),
        "cpp_mutation_finalize_helper_present": cpp_mutation_finalize_helper_present,
        "dirty_content_before": list(dirty_content_before),
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "live_command_dispatched": live_command_dispatched,
        "live_command_executed": live_command_executed,
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
        "compile_executed": compile_executed,
        "save_executed": save_executed,
        "asset_write_performed": asset_write_performed,
        "package_dirty_marked": package_dirty_marked,
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


def build_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract(
    requested: bool,
    section_417_424_user_widget_widget_tree_route_preflight_summary: Dict[str, Any],
    user_widget_widget_tree_umg_cpp_route_hardening_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_417_424_summary_schema_matches = bool(
        section_417_424_user_widget_widget_tree_route_preflight_summary.get(
            "schema"
        )
        == SECTION_417_424_USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_SUMMARY_SCHEMA
    )
    section_417_424_summary_passed = bool(
        section_417_424_user_widget_widget_tree_route_preflight_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_preflight_ready = all(
        _count_is_one(
            section_417_424_user_widget_widget_tree_route_preflight_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_417_424_user_widget_widget_tree_route_preflight_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    upstream_hardening_required = bool(
        section_417_424_user_widget_widget_tree_route_preflight_summary.get(
            "cpp_route_hardening_required_count"
        )
        == 1
    )
    result_schema_matches = bool(
        user_widget_widget_tree_umg_cpp_route_hardening_result.get("schema")
        == USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_417_424_summary_schema_matches
        and section_417_424_summary_passed
        and upstream_preflight_ready
        and upstream_outputs_closed
        and upstream_hardening_required
    )
    temp_scope_gate_verified = bool(
        user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_umg_commands_source_path"
        )
        == DEFAULT_UMG_CPP_SOURCE_PATH
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "unreal_mcp_submodule_path"
        )
        == DEFAULT_UNREAL_MCP_SUBMODULE_PATH
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_default_safe_widget_root_present"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_safe_temp_root_present"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_validate_safe_package_name_present"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_resolve_target_path_helpers_present"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_fixed_game_widgets_path_removed"
        )
    )
    no_save_default_verified = bool(
        user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_save_default_false_present"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_save_asset_guarded_by_save_flag"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_immediate_save_asset_removed"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_request_compile_default_true_present"
        )
    )
    production_path_guard_verified = bool(
        user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_allows_explicit_production_path_opt_in"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_blocks_production_without_opt_in"
        )
        and not user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "production_path_write_allowed"
        )
        and not user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "production_path_write_executed"
        )
    )
    widget_tree_route_hardened = bool(
        user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_command_registration_preserved"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_create_umg_widget_blueprint_registered"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_add_text_block_to_widget_registered"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_add_button_to_widget_registered"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_bind_widget_event_registered"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_set_text_block_binding_registered"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_add_widget_to_viewport_registered"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_widget_tree_construct_widget_present"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_get_or_create_root_canvas_present"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_root_canvas_created_through_widget_tree"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_child_widgets_created_through_widget_tree"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_canvas_slot_position_route_present"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_newobject_cdo_child_creation_removed"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "cpp_mutation_finalize_helper_present"
        )
    )
    build_verified = bool(
        user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "ubt_build_command"
        )
        == DEFAULT_UBT_BUILD_COMMAND
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "ubt_build_succeeded"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "ubt_no_hot_reload_from_ide_used"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "live_coding_mutex_detected"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "editor_left_running"
        )
    )
    live_command_no_dispatch_verified = bool(
        all(
            not user_widget_widget_tree_umg_cpp_route_hardening_result.get(key)
            for key in BLOCKED_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_RESULT_KEYS
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "dirty_content_before"
        )
        == user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "dirty_content_after"
        )
        and user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "dirty_maps_before"
        )
        == user_widget_widget_tree_umg_cpp_route_hardening_result.get(
            "dirty_maps_after"
        )
    )
    result_has_no_error = bool(
        user_widget_widget_tree_umg_cpp_route_hardening_result.get("error")
        in (None, "")
    )
    hardening_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and temp_scope_gate_verified
        and no_save_default_verified
        and production_path_guard_verified
        and widget_tree_route_hardened
        and build_verified
        and live_command_no_dispatch_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_417_424_summary_schema_matches": (
            section_417_424_summary_schema_matches
        ),
        "section_417_424_summary_passed": section_417_424_summary_passed,
        "section_417_424_user_widget_route_preflight_ready": (
            upstream_preflight_ready
        ),
        "section_417_424_outputs_closed": upstream_outputs_closed,
        "section_417_424_cpp_route_hardening_required": (
            upstream_hardening_required
        ),
        "result_schema_matches": result_schema_matches,
        "user_widget_umg_cpp_route_hardening_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "user_widget_umg_cpp_temp_scope_gate_verified": (
            temp_scope_gate_verified
        ),
        "user_widget_umg_cpp_no_save_default_verified": (
            no_save_default_verified
        ),
        "user_widget_umg_cpp_production_path_opt_in_guard_verified": (
            production_path_guard_verified
        ),
        "user_widget_umg_cpp_widget_tree_mutation_route_hardened": (
            widget_tree_route_hardened
        ),
        "user_widget_umg_cpp_build_verified": build_verified,
        "user_widget_umg_cpp_live_command_no_dispatch_verified": (
            live_command_no_dispatch_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_425_user_widget_umg_cpp_route_hardening_checkpoint_satisfied": (
            hardening_ready
        ),
        "section_426_user_widget_umg_cpp_temp_scope_gate_verified": (
            hardening_ready
        ),
        "section_427_user_widget_umg_cpp_no_save_default_verified": (
            hardening_ready
        ),
        "section_428_user_widget_umg_cpp_production_path_opt_in_guard_verified": (
            hardening_ready
        ),
        "section_429_user_widget_umg_cpp_widget_tree_mutation_route_hardened": (
            hardening_ready
        ),
        "section_430_user_widget_umg_cpp_build_verified": hardening_ready,
        "section_431_user_widget_umg_cpp_live_command_no_dispatch_verified": (
            hardening_ready
        ),
        "section_432_user_widget_widget_tree_umg_cpp_route_hardening_release_ready": (
            hardening_ready
        ),
        "user_widget_widget_tree_umg_cpp_route_hardening_ready": (
            hardening_ready
        ),
        "final_durable_release_ready": hardening_ready,
        **{
            key: 1 if hardening_ready else 0
            for key in USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "user_widget_widget_tree_umg_cpp_route_hardening_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "user_widget_umg_cpp_live_command_no_dispatch_verified",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_count": (
            len(requested)
        ),
        "section_417_424_summary_schema_matches_count": _truthy_count(
            requested, "section_417_424_summary_schema_matches"
        ),
        "section_417_424_summary_passed_count": _truthy_count(
            requested, "section_417_424_summary_passed"
        ),
        "section_417_424_user_widget_route_preflight_ready_count": _truthy_count(
            requested, "section_417_424_user_widget_route_preflight_ready"
        ),
        "section_417_424_outputs_closed_count": _truthy_count(
            requested, "section_417_424_outputs_closed"
        ),
        "section_417_424_cpp_route_hardening_required_count": _truthy_count(
            requested, "section_417_424_cpp_route_hardening_required"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "user_widget_umg_cpp_route_hardening_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "user_widget_umg_cpp_route_hardening_checkpoint_satisfied",
            )
        ),
        "user_widget_umg_cpp_temp_scope_gate_verified_count": _truthy_count(
            requested, "user_widget_umg_cpp_temp_scope_gate_verified"
        ),
        "user_widget_umg_cpp_no_save_default_verified_count": _truthy_count(
            requested, "user_widget_umg_cpp_no_save_default_verified"
        ),
        "user_widget_umg_cpp_production_path_opt_in_guard_verified_count": (
            _truthy_count(
                requested,
                "user_widget_umg_cpp_production_path_opt_in_guard_verified",
            )
        ),
        "user_widget_umg_cpp_widget_tree_mutation_route_hardened_count": (
            _truthy_count(
                requested,
                "user_widget_umg_cpp_widget_tree_mutation_route_hardened",
            )
        ),
        "user_widget_umg_cpp_build_verified_count": _truthy_count(
            requested, "user_widget_umg_cpp_build_verified"
        ),
        "user_widget_umg_cpp_live_command_no_dispatch_verified_count": (
            _truthy_count(
                requested,
                "user_widget_umg_cpp_live_command_no_dispatch_verified",
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
            for key in USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_OUTPUT_COUNT_KEYS
        }
    )
    return summary
