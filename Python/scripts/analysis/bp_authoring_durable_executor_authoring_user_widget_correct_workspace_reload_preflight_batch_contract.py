#!/usr/bin/env python
"""
Sections 433-440 durable executor UserWidget correct-workspace reload preflight.

This contract follows the Sections 425-432 UMG C++ route hardening. It records
that the hardened UnrealMCP DLL exists in the managed CubelessStylized workspace,
but the currently running Unreal Editor is still attached to a different
workspace. Live WidgetTree mutation remains blocked until a correct-workspace
editor session loads the hardened plugin DLL.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract as route_hardening
import project_paths


DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_BATCH_SCHEMA = (
    "section_433_440_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_BATCH_SUMMARY_SCHEMA = (
    "section_433_440_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_summary_v1"
)
USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_RESULT_SCHEMA = (
    "section_433_440_user_widget_correct_workspace_reload_preflight_result_v1"
)
SECTION_425_432_USER_WIDGET_UMG_CPP_ROUTE_HARDENING_SUMMARY_SCHEMA = (
    route_hardening
    .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_BATCH_SUMMARY_SCHEMA
)

DEFAULT_PROJECT_FILE_PATH = project_paths.default_cubeless_uproject()
DEFAULT_EXPECTED_UNREAL_MCP_DLL_PATH = project_paths.cubeless_unreal_mcp_dll_path()
DEFAULT_EXPECTED_UNREAL_MCP_SUBMODULE_COMMIT = (
    "df47193754f421e38f31d9627f0a5257824a2a3c"
)
DEFAULT_RUNNING_EDITOR_PROJECT_FILE_PATH = project_paths.default_wrong_workspace_uproject()
DEFAULT_RUNNING_EDITOR_UNREAL_MCP_DLL_PATH = project_paths.wrong_workspace_unreal_mcp_dll_path()
DEFAULT_RUNNING_EDITOR_PROCESS_ID = 55408
DEFAULT_RUNNING_EDITOR_PROCESS_START_TIME = "2026-06-17T10:46:30+09:00"

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_count",
    "section_417_424_summary_schema_matches_count",
    "section_417_424_summary_passed_count",
    "section_417_424_user_widget_route_preflight_ready_count",
    "section_417_424_outputs_closed_count",
    "section_417_424_cpp_route_hardening_required_count",
    "result_schema_matches_count",
    "user_widget_umg_cpp_route_hardening_checkpoint_satisfied_count",
    "user_widget_umg_cpp_temp_scope_gate_verified_count",
    "user_widget_umg_cpp_no_save_default_verified_count",
    "user_widget_umg_cpp_production_path_opt_in_guard_verified_count",
    "user_widget_umg_cpp_widget_tree_mutation_route_hardened_count",
    "user_widget_umg_cpp_build_verified_count",
    "user_widget_umg_cpp_live_command_no_dispatch_verified_count",
    "result_has_no_error_count",
    "final_durable_release_ready_count",
    "user_widget_widget_tree_umg_cpp_route_hardening_ready_count",
    *route_hardening.USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_PATH_COUNT_KEYS,
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    route_hardening
    .BLOCKED_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_OUTPUT_COUNT_KEYS
)

USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_PATH_COUNT_KEYS = (
    "section_433_user_widget_correct_workspace_reload_checkpoint_satisfied_count",
    "section_434_hardened_unreal_mcp_dll_on_disk_verified_count",
    "section_435_running_editor_workspace_mismatch_detected_count",
    "section_436_running_editor_unreal_mcp_module_mismatch_detected_count",
    "section_437_correct_workspace_live_bridge_blocked_count",
    "section_438_correct_workspace_editor_restart_required_recorded_count",
    "section_439_user_widget_live_mutation_command_no_dispatch_verified_count",
    "section_440_user_widget_correct_workspace_reload_preflight_release_ready_count",
    "user_widget_correct_workspace_reload_preflight_ready_count",
    "correct_workspace_editor_reload_still_required_count",
)
BLOCKED_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_OUTPUT_COUNT_KEYS = (
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
BLOCKED_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_RESULT_KEYS = (
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


def _normalize_path(value: Any) -> str:
    return str(value or "").replace("\\", "/")


def build_user_widget_correct_workspace_reload_preflight_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    expected_unreal_mcp_dll_path: str = DEFAULT_EXPECTED_UNREAL_MCP_DLL_PATH,
    expected_unreal_mcp_submodule_commit: str = DEFAULT_EXPECTED_UNREAL_MCP_SUBMODULE_COMMIT,
    hardened_unreal_mcp_dll_exists: bool = True,
    hardened_unreal_mcp_dll_size_bytes: int = 3048960,
    running_editor_detected: bool = True,
    running_editor_process_id: int = DEFAULT_RUNNING_EDITOR_PROCESS_ID,
    running_editor_process_start_time: str = DEFAULT_RUNNING_EDITOR_PROCESS_START_TIME,
    running_editor_project_file_path: str = DEFAULT_RUNNING_EDITOR_PROJECT_FILE_PATH,
    running_editor_unreal_mcp_dll_path: str = DEFAULT_RUNNING_EDITOR_UNREAL_MCP_DLL_PATH,
    running_editor_loaded_unreal_mcp_module: bool = True,
    running_editor_matches_expected_project: bool = False,
    running_editor_loaded_expected_unreal_mcp_dll: bool = False,
    correct_workspace_editor_session_loaded: bool = False,
    correct_workspace_live_bridge_verified: bool = False,
    correct_workspace_editor_restart_required: bool = True,
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
        "schema": USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_RESULT_SCHEMA,
        "project_file_path": project_file_path,
        "expected_unreal_mcp_dll_path": expected_unreal_mcp_dll_path,
        "expected_unreal_mcp_submodule_commit": expected_unreal_mcp_submodule_commit,
        "hardened_unreal_mcp_dll_exists": hardened_unreal_mcp_dll_exists,
        "hardened_unreal_mcp_dll_size_bytes": hardened_unreal_mcp_dll_size_bytes,
        "running_editor_detected": running_editor_detected,
        "running_editor_process_id": running_editor_process_id,
        "running_editor_process_start_time": running_editor_process_start_time,
        "running_editor_project_file_path": running_editor_project_file_path,
        "running_editor_unreal_mcp_dll_path": running_editor_unreal_mcp_dll_path,
        "running_editor_loaded_unreal_mcp_module": (
            running_editor_loaded_unreal_mcp_module
        ),
        "running_editor_matches_expected_project": (
            running_editor_matches_expected_project
        ),
        "running_editor_loaded_expected_unreal_mcp_dll": (
            running_editor_loaded_expected_unreal_mcp_dll
        ),
        "correct_workspace_editor_session_loaded": (
            correct_workspace_editor_session_loaded
        ),
        "correct_workspace_live_bridge_verified": correct_workspace_live_bridge_verified,
        "correct_workspace_editor_restart_required": (
            correct_workspace_editor_restart_required
        ),
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


def build_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_contract(
    requested: bool,
    section_425_432_user_widget_umg_cpp_route_hardening_summary: Dict[str, Any],
    user_widget_correct_workspace_reload_preflight_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_425_432_summary_schema_matches = bool(
        section_425_432_user_widget_umg_cpp_route_hardening_summary.get("schema")
        == SECTION_425_432_USER_WIDGET_UMG_CPP_ROUTE_HARDENING_SUMMARY_SCHEMA
    )
    section_425_432_summary_passed = bool(
        section_425_432_user_widget_umg_cpp_route_hardening_summary.get("status")
        == "passed"
    )
    upstream_hardening_ready = all(
        _count_is_one(
            section_425_432_user_widget_umg_cpp_route_hardening_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_425_432_user_widget_umg_cpp_route_hardening_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        user_widget_correct_workspace_reload_preflight_result.get("schema")
        == USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_425_432_summary_schema_matches
        and section_425_432_summary_passed
        and upstream_hardening_ready
        and upstream_outputs_closed
    )
    hardened_dll_on_disk_verified = bool(
        _normalize_path(
            user_widget_correct_workspace_reload_preflight_result.get(
                "project_file_path"
            )
        )
        == DEFAULT_PROJECT_FILE_PATH
        and _normalize_path(
            user_widget_correct_workspace_reload_preflight_result.get(
                "expected_unreal_mcp_dll_path"
            )
        )
        == DEFAULT_EXPECTED_UNREAL_MCP_DLL_PATH
        and user_widget_correct_workspace_reload_preflight_result.get(
            "expected_unreal_mcp_submodule_commit"
        )
        == DEFAULT_EXPECTED_UNREAL_MCP_SUBMODULE_COMMIT
        and user_widget_correct_workspace_reload_preflight_result.get(
            "hardened_unreal_mcp_dll_exists"
        )
        and int(
            user_widget_correct_workspace_reload_preflight_result.get(
                "hardened_unreal_mcp_dll_size_bytes", 0
            )
            or 0
        )
        > 0
    )
    running_editor_workspace_mismatch_detected = bool(
        user_widget_correct_workspace_reload_preflight_result.get(
            "running_editor_detected"
        )
        and _normalize_path(
            user_widget_correct_workspace_reload_preflight_result.get(
                "running_editor_project_file_path"
            )
        )
        == DEFAULT_RUNNING_EDITOR_PROJECT_FILE_PATH
        and not user_widget_correct_workspace_reload_preflight_result.get(
            "running_editor_matches_expected_project"
        )
        and _normalize_path(
            user_widget_correct_workspace_reload_preflight_result.get(
                "running_editor_project_file_path"
            )
        )
        != DEFAULT_PROJECT_FILE_PATH
    )
    running_editor_unreal_mcp_module_mismatch_detected = bool(
        user_widget_correct_workspace_reload_preflight_result.get(
            "running_editor_loaded_unreal_mcp_module"
        )
        and _normalize_path(
            user_widget_correct_workspace_reload_preflight_result.get(
                "running_editor_unreal_mcp_dll_path"
            )
        )
        == DEFAULT_RUNNING_EDITOR_UNREAL_MCP_DLL_PATH
        and not user_widget_correct_workspace_reload_preflight_result.get(
            "running_editor_loaded_expected_unreal_mcp_dll"
        )
        and _normalize_path(
            user_widget_correct_workspace_reload_preflight_result.get(
                "running_editor_unreal_mcp_dll_path"
            )
        )
        != DEFAULT_EXPECTED_UNREAL_MCP_DLL_PATH
    )
    correct_workspace_live_bridge_blocked = bool(
        running_editor_workspace_mismatch_detected
        and running_editor_unreal_mcp_module_mismatch_detected
        and not user_widget_correct_workspace_reload_preflight_result.get(
            "correct_workspace_editor_session_loaded"
        )
        and not user_widget_correct_workspace_reload_preflight_result.get(
            "correct_workspace_live_bridge_verified"
        )
    )
    editor_restart_required_recorded = bool(
        correct_workspace_live_bridge_blocked
        and user_widget_correct_workspace_reload_preflight_result.get(
            "correct_workspace_editor_restart_required"
        )
    )
    live_mutation_command_no_dispatch_verified = bool(
        all(
            not user_widget_correct_workspace_reload_preflight_result.get(key)
            for key in BLOCKED_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_RESULT_KEYS
        )
    )
    result_has_no_error = bool(
        user_widget_correct_workspace_reload_preflight_result.get("error")
        in (None, "")
    )
    reload_preflight_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and hardened_dll_on_disk_verified
        and running_editor_workspace_mismatch_detected
        and running_editor_unreal_mcp_module_mismatch_detected
        and correct_workspace_live_bridge_blocked
        and editor_restart_required_recorded
        and live_mutation_command_no_dispatch_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_425_432_summary_schema_matches": (
            section_425_432_summary_schema_matches
        ),
        "section_425_432_summary_passed": section_425_432_summary_passed,
        "section_425_432_user_widget_umg_cpp_route_hardening_ready": (
            upstream_hardening_ready
        ),
        "section_425_432_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "user_widget_correct_workspace_reload_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "hardened_unreal_mcp_dll_on_disk_verified": hardened_dll_on_disk_verified,
        "running_editor_workspace_mismatch_detected": (
            running_editor_workspace_mismatch_detected
        ),
        "running_editor_unreal_mcp_module_mismatch_detected": (
            running_editor_unreal_mcp_module_mismatch_detected
        ),
        "correct_workspace_live_bridge_blocked": correct_workspace_live_bridge_blocked,
        "correct_workspace_editor_restart_required_recorded": (
            editor_restart_required_recorded
        ),
        "user_widget_live_mutation_command_no_dispatch_verified": (
            live_mutation_command_no_dispatch_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_433_user_widget_correct_workspace_reload_checkpoint_satisfied": (
            reload_preflight_ready
        ),
        "section_434_hardened_unreal_mcp_dll_on_disk_verified": (
            reload_preflight_ready
        ),
        "section_435_running_editor_workspace_mismatch_detected": (
            reload_preflight_ready
        ),
        "section_436_running_editor_unreal_mcp_module_mismatch_detected": (
            reload_preflight_ready
        ),
        "section_437_correct_workspace_live_bridge_blocked": reload_preflight_ready,
        "section_438_correct_workspace_editor_restart_required_recorded": (
            reload_preflight_ready
        ),
        "section_439_user_widget_live_mutation_command_no_dispatch_verified": (
            reload_preflight_ready
        ),
        "section_440_user_widget_correct_workspace_reload_preflight_release_ready": (
            reload_preflight_ready
        ),
        "user_widget_correct_workspace_reload_preflight_ready": (
            reload_preflight_ready
        ),
        "correct_workspace_editor_reload_still_required": reload_preflight_ready,
        "final_durable_release_ready": reload_preflight_ready,
        **{
            key: 1 if reload_preflight_ready else 0
            for key in USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "user_widget_correct_workspace_reload_preflight_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "correct_workspace_editor_reload_still_required",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_count": (
            len(requested)
        ),
        "section_425_432_summary_schema_matches_count": _truthy_count(
            requested, "section_425_432_summary_schema_matches"
        ),
        "section_425_432_summary_passed_count": _truthy_count(
            requested, "section_425_432_summary_passed"
        ),
        "section_425_432_user_widget_umg_cpp_route_hardening_ready_count": (
            _truthy_count(
                requested,
                "section_425_432_user_widget_umg_cpp_route_hardening_ready",
            )
        ),
        "section_425_432_outputs_closed_count": _truthy_count(
            requested, "section_425_432_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "user_widget_correct_workspace_reload_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "user_widget_correct_workspace_reload_checkpoint_satisfied",
            )
        ),
        "hardened_unreal_mcp_dll_on_disk_verified_count": _truthy_count(
            requested, "hardened_unreal_mcp_dll_on_disk_verified"
        ),
        "running_editor_workspace_mismatch_detected_count": _truthy_count(
            requested, "running_editor_workspace_mismatch_detected"
        ),
        "running_editor_unreal_mcp_module_mismatch_detected_count": (
            _truthy_count(
                requested,
                "running_editor_unreal_mcp_module_mismatch_detected",
            )
        ),
        "correct_workspace_live_bridge_blocked_count": _truthy_count(
            requested, "correct_workspace_live_bridge_blocked"
        ),
        "correct_workspace_editor_restart_required_recorded_count": _truthy_count(
            requested, "correct_workspace_editor_restart_required_recorded"
        ),
        "user_widget_live_mutation_command_no_dispatch_verified_count": (
            _truthy_count(
                requested,
                "user_widget_live_mutation_command_no_dispatch_verified",
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
            for key in USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_OUTPUT_COUNT_KEYS
        }
    )
    return summary
