#!/usr/bin/env python
"""
Sections 497-504 durable executor bridge takeover execution dry-run envelope.

This contract follows the correct-workspace bridge takeover handoff. It records
the execution envelope for a future bridge takeover while proving the envelope
is dry-run only: no process stop, port release, editor launch, MCP start, bridge
verification, live authoring, compile, save, delete, rename, overwrite, cleanup,
or production write is allowed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_takeover_handoff_batch_contract as handoff


DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_BATCH_SCHEMA = (
    "section_497_504_durable_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_BATCH_SUMMARY_SCHEMA = (
    "section_497_504_durable_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batch_summary_v1"
)
CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_RESULT_SCHEMA = (
    "section_497_504_correct_workspace_bridge_takeover_execution_dry_run_envelope_result_v1"
)
SECTION_489_496_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_SUMMARY_SCHEMA = (
    handoff
    .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_BATCH_SUMMARY_SCHEMA
)

DEFAULT_PROJECT_FILE_PATH = handoff.DEFAULT_PROJECT_FILE_PATH
DEFAULT_BRIDGE_HOST = handoff.DEFAULT_BRIDGE_HOST
DEFAULT_BRIDGE_PORT = handoff.DEFAULT_BRIDGE_PORT
DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH = (
    handoff.DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH
)
DEFAULT_WRONG_WORKSPACE_OWNER_PROCESS_ID = (
    handoff.DEFAULT_WRONG_WORKSPACE_OWNER_PROCESS_ID
)
DEFAULT_EDITOR_EXECUTABLE_PATH = handoff.DEFAULT_EDITOR_EXECUTABLE_PATH
DEFAULT_MCP_SERVER_COMMAND = handoff.DEFAULT_MCP_SERVER_COMMAND
DEFAULT_EXECUTION_SCOPE = (
    "wrong_workspace_process_stop",
    "bridge_port_release",
    "correct_workspace_editor_launch",
    "mcp_server_start",
    "correct_workspace_bridge_read_only_verify",
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_correct_workspace_bridge_takeover_handoff_batch_count",
    "section_481_488_summary_schema_matches_count",
    "section_481_488_summary_passed_count",
    "section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_ready_count",
    "section_481_488_outputs_closed_count",
    "result_schema_matches_count",
    "correct_workspace_bridge_takeover_handoff_checkpoint_satisfied_count",
    "wrong_workspace_bridge_owner_context_recorded_count",
    "correct_workspace_bridge_launch_plan_recorded_count",
    "automatic_bridge_takeover_blocked_count",
    "post_takeover_bridge_verification_chain_required_count",
    "live_durable_dispatch_after_takeover_blocked_count",
    "correct_workspace_bridge_takeover_handoff_no_write_boundary_verified_count",
    "bridge_takeover_compile_save_write_outputs_blocked_count",
    "result_has_no_error_count",
    "final_durable_release_ready_count",
    *handoff.CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_PATH_COUNT_KEYS,
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    handoff.BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_OUTPUT_COUNT_KEYS
)

CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_PATH_COUNT_KEYS = (
    "section_497_correct_workspace_bridge_takeover_execution_dry_run_checkpoint_satisfied_count",
    "section_498_takeover_execution_scope_recorded_count",
    "section_499_takeover_execution_authorization_still_required_count",
    "section_500_wrong_workspace_release_command_blocked_count",
    "section_501_correct_workspace_editor_launch_command_blocked_count",
    "section_502_correct_workspace_bridge_verification_command_blocked_count",
    "section_503_takeover_execution_dry_run_no_write_boundary_verified_count",
    "section_504_takeover_execution_dry_run_release_ready_count",
    "correct_workspace_bridge_takeover_execution_dry_run_envelope_ready_count",
    "correct_workspace_bridge_takeover_execution_still_blocked_count",
)
BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_OUTPUT_COUNT_KEYS = (
    "process_termination_command_dispatched_count",
    "wrong_workspace_editor_stopped_count",
    "bridge_port_released_count",
    "correct_workspace_editor_launch_command_dispatched_count",
    "correct_workspace_editor_started_count",
    "mcp_server_start_command_dispatched_count",
    "mcp_server_started_count",
    "correct_workspace_bridge_start_command_dispatched_count",
    "correct_workspace_bridge_started_count",
    "correct_workspace_bridge_verify_command_dispatched_count",
    "correct_workspace_bridge_verified_count",
    "read_only_probe_command_dispatched_count",
    "read_only_probe_executed_count",
    "live_command_dispatched_count",
    "live_command_executed_count",
    "widget_tree_mutation_command_dispatched_count",
    "widget_tree_mutation_command_executed_count",
    "non_actor_actual_temp_checkpoint_command_dispatched_count",
    "non_actor_actual_temp_checkpoint_command_executed_count",
    "data_asset_actual_temp_create_command_dispatched_count",
    "data_asset_actual_temp_create_command_executed_count",
    "bfl_actual_temp_create_command_dispatched_count",
    "bfl_actual_temp_create_command_executed_count",
    "compile_executed_count",
    "save_executed_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
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
BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_RESULT_KEYS = tuple(
    key.removesuffix("_count")
    for key in BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_OUTPUT_COUNT_KEYS
)


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _count_is_one(summary: Dict[str, Any], key: str) -> bool:
    return bool(summary.get(key) == 1)


def _count_is_zero(summary: Dict[str, Any], key: str) -> bool:
    return bool(int(summary.get(key, 0) or 0) == 0)


def _blocked_output_counts(result: Dict[str, Any]) -> Dict[str, int]:
    return {
        count_key: 1 if result.get(result_key) else 0
        for count_key, result_key in zip(
            BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_OUTPUT_COUNT_KEYS,
            BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_RESULT_KEYS,
        )
    }


def build_correct_workspace_bridge_takeover_execution_dry_run_envelope_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    bridge_host: str = DEFAULT_BRIDGE_HOST,
    bridge_port_number: int = DEFAULT_BRIDGE_PORT,
    wrong_workspace_project_file_path: str = DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH,
    wrong_workspace_owner_process_id: int = DEFAULT_WRONG_WORKSPACE_OWNER_PROCESS_ID,
    expected_editor_executable_path: str = DEFAULT_EDITOR_EXECUTABLE_PATH,
    expected_mcp_server_command: str = DEFAULT_MCP_SERVER_COMMAND,
    takeover_execution_dry_run_requested: bool = True,
    takeover_execution_scope: Sequence[str] = DEFAULT_EXECUTION_SCOPE,
    operator_takeover_required: bool = True,
    explicit_takeover_approval_recorded: bool = False,
    actual_takeover_execution_allowed: bool = False,
    wrong_workspace_release_command_blocked: bool = True,
    correct_workspace_editor_launch_command_blocked: bool = True,
    correct_workspace_bridge_verification_command_blocked: bool = True,
    post_takeover_authoring_dispatch_blocked: bool = True,
    dirty_content_before: Sequence[str] = (),
    dirty_content_after: Sequence[str] = (),
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
    process_termination_command_dispatched: bool = False,
    wrong_workspace_editor_stopped: bool = False,
    bridge_port_released: bool = False,
    correct_workspace_editor_launch_command_dispatched: bool = False,
    correct_workspace_editor_started: bool = False,
    mcp_server_start_command_dispatched: bool = False,
    mcp_server_started: bool = False,
    correct_workspace_bridge_start_command_dispatched: bool = False,
    correct_workspace_bridge_started: bool = False,
    correct_workspace_bridge_verify_command_dispatched: bool = False,
    correct_workspace_bridge_verified: bool = False,
    read_only_probe_command_dispatched: bool = False,
    read_only_probe_executed: bool = False,
    live_command_dispatched: bool = False,
    live_command_executed: bool = False,
    widget_tree_mutation_command_dispatched: bool = False,
    widget_tree_mutation_command_executed: bool = False,
    non_actor_actual_temp_checkpoint_command_dispatched: bool = False,
    non_actor_actual_temp_checkpoint_command_executed: bool = False,
    data_asset_actual_temp_create_command_dispatched: bool = False,
    data_asset_actual_temp_create_command_executed: bool = False,
    bfl_actual_temp_create_command_dispatched: bool = False,
    bfl_actual_temp_create_command_executed: bool = False,
    compile_executed: bool = False,
    save_executed: bool = False,
    asset_write_performed: bool = False,
    package_dirty_marked: bool = False,
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
        "schema": (
            CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_RESULT_SCHEMA
        ),
        "project_file_path": project_file_path,
        "bridge_host": bridge_host,
        "bridge_port": bridge_port_number,
        "wrong_workspace_project_file_path": wrong_workspace_project_file_path,
        "wrong_workspace_owner_process_id": wrong_workspace_owner_process_id,
        "expected_editor_executable_path": expected_editor_executable_path,
        "expected_mcp_server_command": expected_mcp_server_command,
        "takeover_execution_dry_run_requested": takeover_execution_dry_run_requested,
        "takeover_execution_scope": list(takeover_execution_scope),
        "operator_takeover_required": operator_takeover_required,
        "explicit_takeover_approval_recorded": explicit_takeover_approval_recorded,
        "actual_takeover_execution_allowed": actual_takeover_execution_allowed,
        "wrong_workspace_release_command_blocked": (
            wrong_workspace_release_command_blocked
        ),
        "correct_workspace_editor_launch_command_blocked": (
            correct_workspace_editor_launch_command_blocked
        ),
        "correct_workspace_bridge_verification_command_blocked": (
            correct_workspace_bridge_verification_command_blocked
        ),
        "post_takeover_authoring_dispatch_blocked": (
            post_takeover_authoring_dispatch_blocked
        ),
        "dirty_content_before": list(dirty_content_before),
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_preserved": external_dirty_preserved,
        "process_termination_command_dispatched": process_termination_command_dispatched,
        "wrong_workspace_editor_stopped": wrong_workspace_editor_stopped,
        "bridge_port_released": bridge_port_released,
        "correct_workspace_editor_launch_command_dispatched": (
            correct_workspace_editor_launch_command_dispatched
        ),
        "correct_workspace_editor_started": correct_workspace_editor_started,
        "mcp_server_start_command_dispatched": mcp_server_start_command_dispatched,
        "mcp_server_started": mcp_server_started,
        "correct_workspace_bridge_start_command_dispatched": (
            correct_workspace_bridge_start_command_dispatched
        ),
        "correct_workspace_bridge_started": correct_workspace_bridge_started,
        "correct_workspace_bridge_verify_command_dispatched": (
            correct_workspace_bridge_verify_command_dispatched
        ),
        "correct_workspace_bridge_verified": correct_workspace_bridge_verified,
        "read_only_probe_command_dispatched": read_only_probe_command_dispatched,
        "read_only_probe_executed": read_only_probe_executed,
        "live_command_dispatched": live_command_dispatched,
        "live_command_executed": live_command_executed,
        "widget_tree_mutation_command_dispatched": (
            widget_tree_mutation_command_dispatched
        ),
        "widget_tree_mutation_command_executed": (
            widget_tree_mutation_command_executed
        ),
        "non_actor_actual_temp_checkpoint_command_dispatched": (
            non_actor_actual_temp_checkpoint_command_dispatched
        ),
        "non_actor_actual_temp_checkpoint_command_executed": (
            non_actor_actual_temp_checkpoint_command_executed
        ),
        "data_asset_actual_temp_create_command_dispatched": (
            data_asset_actual_temp_create_command_dispatched
        ),
        "data_asset_actual_temp_create_command_executed": (
            data_asset_actual_temp_create_command_executed
        ),
        "bfl_actual_temp_create_command_dispatched": (
            bfl_actual_temp_create_command_dispatched
        ),
        "bfl_actual_temp_create_command_executed": (
            bfl_actual_temp_create_command_executed
        ),
        "compile_executed": compile_executed,
        "save_executed": save_executed,
        "asset_write_performed": asset_write_performed,
        "package_dirty_marked": package_dirty_marked,
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


def build_durable_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batch_contract(
    requested: bool,
    section_489_496_correct_workspace_bridge_takeover_handoff_summary: Dict[str, Any],
    correct_workspace_bridge_takeover_execution_dry_run_envelope_result: Dict[str, Any],
) -> Dict[str, Any]:
    upstream_schema_matches = bool(
        section_489_496_correct_workspace_bridge_takeover_handoff_summary.get(
            "schema"
        )
        == SECTION_489_496_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_SUMMARY_SCHEMA
    )
    upstream_summary_passed = bool(
        section_489_496_correct_workspace_bridge_takeover_handoff_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_handoff_ready = all(
        _count_is_one(
            section_489_496_correct_workspace_bridge_takeover_handoff_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_489_496_correct_workspace_bridge_takeover_handoff_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "schema"
        )
        == CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and upstream_schema_matches
        and upstream_summary_passed
        and upstream_handoff_ready
        and upstream_outputs_closed
    )
    scope_recorded = bool(
        correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "bridge_host"
        )
        == DEFAULT_BRIDGE_HOST
        and correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "bridge_port"
        )
        == DEFAULT_BRIDGE_PORT
        and correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "wrong_workspace_project_file_path"
        )
        == DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH
        and correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "wrong_workspace_owner_process_id"
        )
        == DEFAULT_WRONG_WORKSPACE_OWNER_PROCESS_ID
        and correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "expected_editor_executable_path"
        )
        == DEFAULT_EDITOR_EXECUTABLE_PATH
        and correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "expected_mcp_server_command"
        )
        == DEFAULT_MCP_SERVER_COMMAND
        and correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "takeover_execution_dry_run_requested"
        )
        and tuple(
            correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
                "takeover_execution_scope", ()
            )
        )
        == DEFAULT_EXECUTION_SCOPE
    )
    authorization_still_required = bool(
        correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "operator_takeover_required"
        )
        and not correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "explicit_takeover_approval_recorded"
        )
        and not correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "actual_takeover_execution_allowed"
        )
    )
    release_command_blocked = bool(
        correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "wrong_workspace_release_command_blocked"
        )
        and all(
            not correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
                key
            )
            for key in (
                "process_termination_command_dispatched",
                "wrong_workspace_editor_stopped",
                "bridge_port_released",
            )
        )
    )
    editor_launch_command_blocked = bool(
        correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "correct_workspace_editor_launch_command_blocked"
        )
        and all(
            not correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
                key
            )
            for key in (
                "correct_workspace_editor_launch_command_dispatched",
                "correct_workspace_editor_started",
                "mcp_server_start_command_dispatched",
                "mcp_server_started",
                "correct_workspace_bridge_start_command_dispatched",
                "correct_workspace_bridge_started",
            )
        )
    )
    bridge_verification_command_blocked = bool(
        correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "correct_workspace_bridge_verification_command_blocked"
        )
        and all(
            not correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
                key
            )
            for key in (
                "correct_workspace_bridge_verify_command_dispatched",
                "correct_workspace_bridge_verified",
                "read_only_probe_command_dispatched",
                "read_only_probe_executed",
            )
        )
    )
    live_dispatch_blocked = bool(
        correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "post_takeover_authoring_dispatch_blocked"
        )
        and all(
            not correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
                key
            )
            for key in (
                "live_command_dispatched",
                "live_command_executed",
                "widget_tree_mutation_command_dispatched",
                "widget_tree_mutation_command_executed",
                "non_actor_actual_temp_checkpoint_command_dispatched",
                "non_actor_actual_temp_checkpoint_command_executed",
                "data_asset_actual_temp_create_command_dispatched",
                "data_asset_actual_temp_create_command_executed",
                "bfl_actual_temp_create_command_dispatched",
                "bfl_actual_temp_create_command_executed",
            )
        )
    )
    compile_save_write_outputs_blocked = all(
        not correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            key
        )
        for key in (
            "compile_executed",
            "save_executed",
            "asset_write_performed",
            "package_dirty_marked",
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
    all_outputs_blocked = all(
        not correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            key
        )
        for key in BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        all_outputs_blocked
        and correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "dirty_content_before"
        )
        == correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "dirty_content_after"
        )
        and correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "dirty_maps_before"
        )
        == correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "dirty_maps_after"
        )
        and not correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "dirty_content_after"
        )
        and not correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "dirty_maps_after"
        )
        and correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        correct_workspace_bridge_takeover_execution_dry_run_envelope_result.get(
            "error"
        )
        in (None, "")
    )
    envelope_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and scope_recorded
        and authorization_still_required
        and release_command_blocked
        and editor_launch_command_blocked
        and bridge_verification_command_blocked
        and live_dispatch_blocked
        and compile_save_write_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_489_496_summary_schema_matches": upstream_schema_matches,
        "section_489_496_summary_passed": upstream_summary_passed,
        "section_489_496_correct_workspace_bridge_takeover_handoff_ready": (
            upstream_handoff_ready
        ),
        "section_489_496_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "correct_workspace_bridge_takeover_execution_dry_run_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "takeover_execution_scope_recorded": scope_recorded,
        "takeover_execution_authorization_still_required": (
            authorization_still_required
        ),
        "wrong_workspace_release_command_blocked": release_command_blocked,
        "correct_workspace_editor_launch_command_blocked": (
            editor_launch_command_blocked
        ),
        "correct_workspace_bridge_verification_command_blocked": (
            bridge_verification_command_blocked
        ),
        "live_durable_dispatch_after_takeover_execution_blocked": (
            live_dispatch_blocked
        ),
        "takeover_execution_dry_run_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "takeover_execution_compile_save_write_outputs_blocked": (
            compile_save_write_outputs_blocked
        ),
        "result_has_no_error": result_has_no_error,
        "section_497_correct_workspace_bridge_takeover_execution_dry_run_checkpoint_satisfied": (
            envelope_ready
        ),
        "section_498_takeover_execution_scope_recorded": envelope_ready,
        "section_499_takeover_execution_authorization_still_required": (
            envelope_ready
        ),
        "section_500_wrong_workspace_release_command_blocked": envelope_ready,
        "section_501_correct_workspace_editor_launch_command_blocked": (
            envelope_ready
        ),
        "section_502_correct_workspace_bridge_verification_command_blocked": (
            envelope_ready
        ),
        "section_503_takeover_execution_dry_run_no_write_boundary_verified": (
            envelope_ready
        ),
        "section_504_takeover_execution_dry_run_release_ready": envelope_ready,
        "correct_workspace_bridge_takeover_execution_dry_run_envelope_ready": (
            envelope_ready
        ),
        "correct_workspace_bridge_takeover_execution_still_blocked": envelope_ready,
        "final_durable_release_ready": envelope_ready,
        **{
            key: 1 if envelope_ready else 0
            for key in (
                CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_PATH_COUNT_KEYS
            )
        },
        **_blocked_output_counts(
            correct_workspace_bridge_takeover_execution_dry_run_envelope_result
        ),
    }


def summarize_durable_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "correct_workspace_bridge_takeover_execution_dry_run_envelope_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "correct_workspace_bridge_takeover_execution_still_blocked",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batch_count": (
            len(requested)
        ),
        "section_489_496_summary_schema_matches_count": _truthy_count(
            requested, "section_489_496_summary_schema_matches"
        ),
        "section_489_496_summary_passed_count": _truthy_count(
            requested, "section_489_496_summary_passed"
        ),
        "section_489_496_correct_workspace_bridge_takeover_handoff_ready_count": (
            _truthy_count(
                requested,
                "section_489_496_correct_workspace_bridge_takeover_handoff_ready",
            )
        ),
        "section_489_496_outputs_closed_count": _truthy_count(
            requested, "section_489_496_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "correct_workspace_bridge_takeover_execution_dry_run_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "correct_workspace_bridge_takeover_execution_dry_run_checkpoint_satisfied",
            )
        ),
        "takeover_execution_scope_recorded_count": _truthy_count(
            requested, "takeover_execution_scope_recorded"
        ),
        "takeover_execution_authorization_still_required_count": _truthy_count(
            requested, "takeover_execution_authorization_still_required"
        ),
        "wrong_workspace_release_command_blocked_count": _truthy_count(
            requested, "wrong_workspace_release_command_blocked"
        ),
        "correct_workspace_editor_launch_command_blocked_count": _truthy_count(
            requested, "correct_workspace_editor_launch_command_blocked"
        ),
        "correct_workspace_bridge_verification_command_blocked_count": (
            _truthy_count(
                requested, "correct_workspace_bridge_verification_command_blocked"
            )
        ),
        "live_durable_dispatch_after_takeover_execution_blocked_count": (
            _truthy_count(
                requested,
                "live_durable_dispatch_after_takeover_execution_blocked",
            )
        ),
        "takeover_execution_dry_run_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "takeover_execution_dry_run_no_write_boundary_verified",
            )
        ),
        "takeover_execution_compile_save_write_outputs_blocked_count": (
            _truthy_count(
                requested,
                "takeover_execution_compile_save_write_outputs_blocked",
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
            for key in (
                CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_PATH_COUNT_KEYS
            )
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in (
                BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_OUTPUT_COUNT_KEYS
            )
        }
    )
    return summary
