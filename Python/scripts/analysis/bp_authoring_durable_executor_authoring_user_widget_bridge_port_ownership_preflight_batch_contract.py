#!/usr/bin/env python
"""
Sections 441-448 durable executor UserWidget bridge port ownership preflight.

This contract follows the Sections 433-440 correct-workspace reload preflight.
It records that the primary UnrealMCP bridge port is owned by the wrong
workspace editor process, so the correct CubelessStylized bridge cannot be
treated as live and UserWidget WidgetTree mutation remains blocked.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_contract as reload_preflight
import project_paths


DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_BATCH_SCHEMA = (
    "section_441_448_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_BATCH_SUMMARY_SCHEMA = (
    "section_441_448_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_summary_v1"
)
USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_RESULT_SCHEMA = (
    "section_441_448_user_widget_bridge_port_ownership_preflight_result_v1"
)
SECTION_433_440_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_SUMMARY_SCHEMA = (
    reload_preflight
    .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_BATCH_SUMMARY_SCHEMA
)

DEFAULT_PROJECT_FILE_PATH = reload_preflight.DEFAULT_PROJECT_FILE_PATH
DEFAULT_PRIMARY_BRIDGE_HOST = "127.0.0.1"
DEFAULT_PRIMARY_BRIDGE_PORT = 55557
DEFAULT_PORT_OWNER_PROCESS_ID = reload_preflight.DEFAULT_RUNNING_EDITOR_PROCESS_ID
DEFAULT_PORT_OWNER_PROJECT_FILE_PATH = (
    reload_preflight.DEFAULT_RUNNING_EDITOR_PROJECT_FILE_PATH
)
DEFAULT_PORT_OWNER_COMMAND_LINE = project_paths.default_port_owner_command_line()

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_count",
    "section_425_432_summary_schema_matches_count",
    "section_425_432_summary_passed_count",
    "section_425_432_user_widget_umg_cpp_route_hardening_ready_count",
    "section_425_432_outputs_closed_count",
    "result_schema_matches_count",
    "user_widget_correct_workspace_reload_checkpoint_satisfied_count",
    "hardened_unreal_mcp_dll_on_disk_verified_count",
    "running_editor_workspace_mismatch_detected_count",
    "running_editor_unreal_mcp_module_mismatch_detected_count",
    "correct_workspace_live_bridge_blocked_count",
    "correct_workspace_editor_restart_required_recorded_count",
    "user_widget_live_mutation_command_no_dispatch_verified_count",
    "result_has_no_error_count",
    "final_durable_release_ready_count",
    "user_widget_correct_workspace_reload_preflight_ready_count",
    "correct_workspace_editor_reload_still_required_count",
    *reload_preflight.USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_PATH_COUNT_KEYS,
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    reload_preflight
    .BLOCKED_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_OUTPUT_COUNT_KEYS
)

USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_PATH_COUNT_KEYS = (
    "section_441_user_widget_bridge_port_ownership_checkpoint_satisfied_count",
    "section_442_primary_bridge_port_probe_recorded_count",
    "section_443_wrong_workspace_port_owner_detected_count",
    "section_444_correct_workspace_bridge_port_unavailable_count",
    "section_445_correct_workspace_bridge_start_blocked_count",
    "section_446_live_user_widget_mutation_bridge_blocked_count",
    "section_447_user_widget_bridge_port_no_dispatch_verified_count",
    "section_448_user_widget_bridge_port_ownership_preflight_release_ready_count",
    "user_widget_bridge_port_ownership_preflight_ready_count",
    "correct_workspace_bridge_port_release_still_required_count",
)
BLOCKED_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_OUTPUT_COUNT_KEYS = (
    "correct_workspace_bridge_started_count",
    "correct_workspace_bridge_verified_count",
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
BLOCKED_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_RESULT_KEYS = (
    "correct_workspace_bridge_started",
    "correct_workspace_bridge_verified",
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


def build_user_widget_bridge_port_ownership_preflight_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    primary_bridge_host: str = DEFAULT_PRIMARY_BRIDGE_HOST,
    primary_bridge_port: int = DEFAULT_PRIMARY_BRIDGE_PORT,
    port_probe_executed: bool = True,
    port_listen_detected: bool = True,
    port_established_detected: bool = True,
    port_owner_process_id: int = DEFAULT_PORT_OWNER_PROCESS_ID,
    port_owner_process_is_unreal_editor: bool = True,
    port_owner_project_file_path: str = DEFAULT_PORT_OWNER_PROJECT_FILE_PATH,
    port_owner_command_line: str = DEFAULT_PORT_OWNER_COMMAND_LINE,
    port_owner_matches_expected_project: bool = False,
    correct_workspace_bridge_port_available: bool = False,
    correct_workspace_bridge_start_blocked: bool = True,
    correct_workspace_bridge_started: bool = False,
    correct_workspace_bridge_verified: bool = False,
    live_user_widget_mutation_bridge_blocked: bool = True,
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
        "schema": USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_RESULT_SCHEMA,
        "project_file_path": project_file_path,
        "primary_bridge_host": primary_bridge_host,
        "primary_bridge_port": primary_bridge_port,
        "port_probe_executed": port_probe_executed,
        "port_listen_detected": port_listen_detected,
        "port_established_detected": port_established_detected,
        "port_owner_process_id": port_owner_process_id,
        "port_owner_process_is_unreal_editor": port_owner_process_is_unreal_editor,
        "port_owner_project_file_path": port_owner_project_file_path,
        "port_owner_command_line": port_owner_command_line,
        "port_owner_matches_expected_project": port_owner_matches_expected_project,
        "correct_workspace_bridge_port_available": (
            correct_workspace_bridge_port_available
        ),
        "correct_workspace_bridge_start_blocked": correct_workspace_bridge_start_blocked,
        "correct_workspace_bridge_started": correct_workspace_bridge_started,
        "correct_workspace_bridge_verified": correct_workspace_bridge_verified,
        "live_user_widget_mutation_bridge_blocked": (
            live_user_widget_mutation_bridge_blocked
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


def build_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_contract(
    requested: bool,
    section_433_440_user_widget_correct_workspace_reload_preflight_summary: Dict[str, Any],
    user_widget_bridge_port_ownership_preflight_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_433_440_summary_schema_matches = bool(
        section_433_440_user_widget_correct_workspace_reload_preflight_summary.get(
            "schema"
        )
        == SECTION_433_440_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_SUMMARY_SCHEMA
    )
    section_433_440_summary_passed = bool(
        section_433_440_user_widget_correct_workspace_reload_preflight_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_reload_preflight_ready = all(
        _count_is_one(
            section_433_440_user_widget_correct_workspace_reload_preflight_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_433_440_user_widget_correct_workspace_reload_preflight_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        user_widget_bridge_port_ownership_preflight_result.get("schema")
        == USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_433_440_summary_schema_matches
        and section_433_440_summary_passed
        and upstream_reload_preflight_ready
        and upstream_outputs_closed
    )
    primary_bridge_port_probe_recorded = bool(
        _normalize_path(
            user_widget_bridge_port_ownership_preflight_result.get(
                "project_file_path"
            )
        )
        == DEFAULT_PROJECT_FILE_PATH
        and user_widget_bridge_port_ownership_preflight_result.get(
            "primary_bridge_host"
        )
        == DEFAULT_PRIMARY_BRIDGE_HOST
        and user_widget_bridge_port_ownership_preflight_result.get(
            "primary_bridge_port"
        )
        == DEFAULT_PRIMARY_BRIDGE_PORT
        and user_widget_bridge_port_ownership_preflight_result.get(
            "port_probe_executed"
        )
        and user_widget_bridge_port_ownership_preflight_result.get(
            "port_listen_detected"
        )
        and user_widget_bridge_port_ownership_preflight_result.get(
            "port_established_detected"
        )
    )
    wrong_workspace_port_owner_detected = bool(
        primary_bridge_port_probe_recorded
        and user_widget_bridge_port_ownership_preflight_result.get(
            "port_owner_process_id"
        )
        == DEFAULT_PORT_OWNER_PROCESS_ID
        and user_widget_bridge_port_ownership_preflight_result.get(
            "port_owner_process_is_unreal_editor"
        )
        and _normalize_path(
            user_widget_bridge_port_ownership_preflight_result.get(
                "port_owner_project_file_path"
            )
        )
        == DEFAULT_PORT_OWNER_PROJECT_FILE_PATH
        and not user_widget_bridge_port_ownership_preflight_result.get(
            "port_owner_matches_expected_project"
        )
    )
    correct_workspace_bridge_port_unavailable = bool(
        wrong_workspace_port_owner_detected
        and not user_widget_bridge_port_ownership_preflight_result.get(
            "correct_workspace_bridge_port_available"
        )
    )
    correct_workspace_bridge_start_blocked = bool(
        correct_workspace_bridge_port_unavailable
        and user_widget_bridge_port_ownership_preflight_result.get(
            "correct_workspace_bridge_start_blocked"
        )
        and not user_widget_bridge_port_ownership_preflight_result.get(
            "correct_workspace_bridge_started"
        )
        and not user_widget_bridge_port_ownership_preflight_result.get(
            "correct_workspace_bridge_verified"
        )
    )
    live_user_widget_mutation_bridge_blocked = bool(
        correct_workspace_bridge_start_blocked
        and user_widget_bridge_port_ownership_preflight_result.get(
            "live_user_widget_mutation_bridge_blocked"
        )
    )
    bridge_port_no_dispatch_verified = bool(
        all(
            not user_widget_bridge_port_ownership_preflight_result.get(key)
            for key in BLOCKED_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_RESULT_KEYS
        )
    )
    result_has_no_error = bool(
        user_widget_bridge_port_ownership_preflight_result.get("error")
        in (None, "")
    )
    port_ownership_preflight_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and primary_bridge_port_probe_recorded
        and wrong_workspace_port_owner_detected
        and correct_workspace_bridge_port_unavailable
        and correct_workspace_bridge_start_blocked
        and live_user_widget_mutation_bridge_blocked
        and bridge_port_no_dispatch_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_433_440_summary_schema_matches": (
            section_433_440_summary_schema_matches
        ),
        "section_433_440_summary_passed": section_433_440_summary_passed,
        "section_433_440_user_widget_reload_preflight_ready": (
            upstream_reload_preflight_ready
        ),
        "section_433_440_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "user_widget_bridge_port_ownership_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "primary_bridge_port_probe_recorded": primary_bridge_port_probe_recorded,
        "wrong_workspace_port_owner_detected": wrong_workspace_port_owner_detected,
        "correct_workspace_bridge_port_unavailable": (
            correct_workspace_bridge_port_unavailable
        ),
        "correct_workspace_bridge_start_blocked": (
            correct_workspace_bridge_start_blocked
        ),
        "live_user_widget_mutation_bridge_blocked": (
            live_user_widget_mutation_bridge_blocked
        ),
        "user_widget_bridge_port_no_dispatch_verified": (
            bridge_port_no_dispatch_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_441_user_widget_bridge_port_ownership_checkpoint_satisfied": (
            port_ownership_preflight_ready
        ),
        "section_442_primary_bridge_port_probe_recorded": (
            port_ownership_preflight_ready
        ),
        "section_443_wrong_workspace_port_owner_detected": (
            port_ownership_preflight_ready
        ),
        "section_444_correct_workspace_bridge_port_unavailable": (
            port_ownership_preflight_ready
        ),
        "section_445_correct_workspace_bridge_start_blocked": (
            port_ownership_preflight_ready
        ),
        "section_446_live_user_widget_mutation_bridge_blocked": (
            port_ownership_preflight_ready
        ),
        "section_447_user_widget_bridge_port_no_dispatch_verified": (
            port_ownership_preflight_ready
        ),
        "section_448_user_widget_bridge_port_ownership_preflight_release_ready": (
            port_ownership_preflight_ready
        ),
        "user_widget_bridge_port_ownership_preflight_ready": (
            port_ownership_preflight_ready
        ),
        "correct_workspace_bridge_port_release_still_required": (
            port_ownership_preflight_ready
        ),
        "final_durable_release_ready": port_ownership_preflight_ready,
        **{
            key: 1 if port_ownership_preflight_ready else 0
            for key in USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "user_widget_bridge_port_ownership_preflight_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "correct_workspace_bridge_port_release_still_required",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_count": (
            len(requested)
        ),
        "section_433_440_summary_schema_matches_count": _truthy_count(
            requested, "section_433_440_summary_schema_matches"
        ),
        "section_433_440_summary_passed_count": _truthy_count(
            requested, "section_433_440_summary_passed"
        ),
        "section_433_440_user_widget_reload_preflight_ready_count": _truthy_count(
            requested, "section_433_440_user_widget_reload_preflight_ready"
        ),
        "section_433_440_outputs_closed_count": _truthy_count(
            requested, "section_433_440_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "user_widget_bridge_port_ownership_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "user_widget_bridge_port_ownership_checkpoint_satisfied",
            )
        ),
        "primary_bridge_port_probe_recorded_count": _truthy_count(
            requested, "primary_bridge_port_probe_recorded"
        ),
        "wrong_workspace_port_owner_detected_count": _truthy_count(
            requested, "wrong_workspace_port_owner_detected"
        ),
        "correct_workspace_bridge_port_unavailable_count": _truthy_count(
            requested, "correct_workspace_bridge_port_unavailable"
        ),
        "correct_workspace_bridge_start_blocked_count": _truthy_count(
            requested, "correct_workspace_bridge_start_blocked"
        ),
        "live_user_widget_mutation_bridge_blocked_count": _truthy_count(
            requested, "live_user_widget_mutation_bridge_blocked"
        ),
        "user_widget_bridge_port_no_dispatch_verified_count": _truthy_count(
            requested, "user_widget_bridge_port_no_dispatch_verified"
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
            for key in USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_OUTPUT_COUNT_KEYS
        }
    )
    return summary
