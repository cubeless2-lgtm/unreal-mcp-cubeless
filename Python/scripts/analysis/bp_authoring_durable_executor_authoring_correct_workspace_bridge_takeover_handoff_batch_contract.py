#!/usr/bin/env python
"""
Sections 489-496 durable executor correct-workspace bridge takeover handoff.

This contract follows the non-Actor actual temp checkpoint bridge blocker. It
records the exact handoff requirements for releasing the wrong-workspace bridge
owner and launching/verifying the managed CubelessStylized bridge, while keeping
all process takeover, editor launch, MCP start, live authoring, compile, save,
delete, rename, overwrite, cleanup, and production writes closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batch_contract as bridge_blocker
import bp_authoring_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_contract as bridge_port


DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_BATCH_SCHEMA = (
    "section_489_496_durable_executor_authoring_correct_workspace_bridge_takeover_handoff_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_BATCH_SUMMARY_SCHEMA = (
    "section_489_496_durable_executor_authoring_correct_workspace_bridge_takeover_handoff_batch_summary_v1"
)
CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_RESULT_SCHEMA = (
    "section_489_496_correct_workspace_bridge_takeover_handoff_result_v1"
)
SECTION_481_488_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_SUMMARY_SCHEMA = (
    bridge_blocker
    .DURABLE_EXECUTOR_AUTHORING_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_BATCH_SUMMARY_SCHEMA
)

DEFAULT_PROJECT_FILE_PATH = bridge_blocker.DEFAULT_PROJECT_FILE_PATH
DEFAULT_BRIDGE_HOST = bridge_blocker.DEFAULT_BRIDGE_HOST
DEFAULT_BRIDGE_PORT = bridge_blocker.DEFAULT_BRIDGE_PORT
DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH = (
    bridge_blocker.DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH
)
DEFAULT_WRONG_WORKSPACE_OWNER_PROCESS_ID = bridge_port.DEFAULT_PORT_OWNER_PROCESS_ID
DEFAULT_WRONG_WORKSPACE_OWNER_COMMAND_LINE = bridge_port.DEFAULT_PORT_OWNER_COMMAND_LINE
DEFAULT_EDITOR_EXECUTABLE_PATH = (
    "C:/Program Files/Epic Games/UE_5.7/Engine/Binaries/Win64/UnrealEditor.exe"
)
DEFAULT_MCP_SERVER_COMMAND = (
    "uv --directory ../unreal-mcp-cubeless/Python run --python 3.11 "
    "unreal_mcp_server.py"
)
DEFAULT_HANDOFF_STEPS = (
    "Record the current wrong-workspace Unreal Editor owner of 127.0.0.1:55557.",
    "Release 127.0.0.1:55557 only through an explicit bridge takeover action.",
    "Launch D:/Git/CubelessStylized/StylizedCubeless.uproject with the hardened UnrealMCP DLL loaded.",
    "Verify the correct workspace bridge by read-only probe before any authoring command dispatch.",
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batch_count",
    "section_441_448_summary_schema_matches_count",
    "section_441_448_summary_passed_count",
    "section_441_448_bridge_blocker_ready_count",
    "section_441_448_outputs_closed_count",
    "section_457_464_summary_schema_matches_count",
    "section_457_464_summary_passed_count",
    "section_457_464_data_asset_dry_run_ready_count",
    "section_457_464_outputs_closed_count",
    "section_473_480_summary_schema_matches_count",
    "section_473_480_summary_passed_count",
    "section_473_480_bfl_dry_run_ready_count",
    "section_473_480_outputs_closed_count",
    "result_schema_matches_count",
    "non_actor_actual_temp_checkpoint_bridge_blocker_checkpoint_satisfied_count",
    "data_asset_actual_temp_checkpoint_preconditions_recorded_count",
    "bfl_actual_temp_checkpoint_preconditions_recorded_count",
    "wrong_workspace_bridge_blocker_reconfirmed_count",
    "live_non_actor_temp_creation_dispatch_blocked_count",
    "non_actor_temp_compile_save_write_outputs_blocked_count",
    "non_actor_actual_temp_checkpoint_no_write_boundary_verified_count",
    "result_has_no_error_count",
    "final_durable_release_ready_count",
    *bridge_blocker.NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_PATH_COUNT_KEYS,
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    bridge_blocker.BLOCKED_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_OUTPUT_COUNT_KEYS
)

CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_PATH_COUNT_KEYS = (
    "section_489_correct_workspace_bridge_takeover_handoff_checkpoint_satisfied_count",
    "section_490_wrong_workspace_bridge_owner_context_recorded_count",
    "section_491_correct_workspace_bridge_launch_plan_recorded_count",
    "section_492_automatic_bridge_takeover_blocked_count",
    "section_493_post_takeover_bridge_verification_chain_required_count",
    "section_494_live_durable_dispatch_after_takeover_blocked_count",
    "section_495_correct_workspace_bridge_takeover_handoff_no_write_boundary_verified_count",
    "section_496_correct_workspace_bridge_takeover_handoff_release_ready_count",
    "correct_workspace_bridge_takeover_handoff_ready_count",
    "correct_workspace_bridge_takeover_still_blocked_count",
)
BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_OUTPUT_COUNT_KEYS = (
    "process_termination_command_dispatched_count",
    "wrong_workspace_editor_stopped_count",
    "bridge_port_released_count",
    "correct_workspace_editor_launch_command_dispatched_count",
    "correct_workspace_editor_started_count",
    "mcp_server_start_command_dispatched_count",
    "mcp_server_started_count",
    "correct_workspace_bridge_started_count",
    "correct_workspace_bridge_verified_count",
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
BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_RESULT_KEYS = tuple(
    key.removesuffix("_count")
    for key in BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_OUTPUT_COUNT_KEYS
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
            BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_OUTPUT_COUNT_KEYS,
            BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_RESULT_KEYS,
        )
    }


def build_correct_workspace_bridge_takeover_handoff_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    bridge_host: str = DEFAULT_BRIDGE_HOST,
    bridge_port_number: int = DEFAULT_BRIDGE_PORT,
    wrong_workspace_project_file_path: str = DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH,
    wrong_workspace_owner_process_id: int = DEFAULT_WRONG_WORKSPACE_OWNER_PROCESS_ID,
    wrong_workspace_owner_command_line: str = DEFAULT_WRONG_WORKSPACE_OWNER_COMMAND_LINE,
    expected_editor_executable_path: str = DEFAULT_EDITOR_EXECUTABLE_PATH,
    expected_mcp_server_command: str = DEFAULT_MCP_SERVER_COMMAND,
    handoff_steps: Sequence[str] = DEFAULT_HANDOFF_STEPS,
    operator_takeover_required: bool = True,
    explicit_takeover_approval_recorded: bool = False,
    correct_workspace_bridge_verification_required: bool = True,
    post_takeover_read_only_probe_required: bool = True,
    asset_authoring_after_takeover_blocked: bool = True,
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
    correct_workspace_bridge_started: bool = False,
    correct_workspace_bridge_verified: bool = False,
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
        "schema": CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_RESULT_SCHEMA,
        "project_file_path": project_file_path,
        "bridge_host": bridge_host,
        "bridge_port": bridge_port_number,
        "wrong_workspace_project_file_path": wrong_workspace_project_file_path,
        "wrong_workspace_owner_process_id": wrong_workspace_owner_process_id,
        "wrong_workspace_owner_command_line": wrong_workspace_owner_command_line,
        "expected_editor_executable_path": expected_editor_executable_path,
        "expected_mcp_server_command": expected_mcp_server_command,
        "handoff_steps": list(handoff_steps),
        "operator_takeover_required": operator_takeover_required,
        "explicit_takeover_approval_recorded": explicit_takeover_approval_recorded,
        "correct_workspace_bridge_verification_required": (
            correct_workspace_bridge_verification_required
        ),
        "post_takeover_read_only_probe_required": post_takeover_read_only_probe_required,
        "asset_authoring_after_takeover_blocked": (
            asset_authoring_after_takeover_blocked
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
        "correct_workspace_bridge_started": correct_workspace_bridge_started,
        "correct_workspace_bridge_verified": correct_workspace_bridge_verified,
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


def build_durable_executor_authoring_correct_workspace_bridge_takeover_handoff_batch_contract(
    requested: bool,
    section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_summary: Dict[str, Any],
    correct_workspace_bridge_takeover_handoff_result: Dict[str, Any],
) -> Dict[str, Any]:
    upstream_schema_matches = bool(
        section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_summary.get(
            "schema"
        )
        == SECTION_481_488_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_SUMMARY_SCHEMA
    )
    upstream_summary_passed = bool(
        section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_blocker_ready = all(
        _count_is_one(
            section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        correct_workspace_bridge_takeover_handoff_result.get("schema")
        == CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and upstream_schema_matches
        and upstream_summary_passed
        and upstream_blocker_ready
        and upstream_outputs_closed
    )
    wrong_workspace_context_recorded = bool(
        correct_workspace_bridge_takeover_handoff_result.get("project_file_path")
        == DEFAULT_PROJECT_FILE_PATH
        and correct_workspace_bridge_takeover_handoff_result.get("bridge_host")
        == DEFAULT_BRIDGE_HOST
        and correct_workspace_bridge_takeover_handoff_result.get("bridge_port")
        == DEFAULT_BRIDGE_PORT
        and correct_workspace_bridge_takeover_handoff_result.get(
            "wrong_workspace_project_file_path"
        )
        == DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH
        and correct_workspace_bridge_takeover_handoff_result.get(
            "wrong_workspace_owner_process_id"
        )
        == DEFAULT_WRONG_WORKSPACE_OWNER_PROCESS_ID
        and DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH
        in str(
            correct_workspace_bridge_takeover_handoff_result.get(
                "wrong_workspace_owner_command_line", ""
            )
        )
    )
    launch_plan_recorded = bool(
        correct_workspace_bridge_takeover_handoff_result.get(
            "expected_editor_executable_path"
        )
        == DEFAULT_EDITOR_EXECUTABLE_PATH
        and correct_workspace_bridge_takeover_handoff_result.get(
            "expected_mcp_server_command"
        )
        == DEFAULT_MCP_SERVER_COMMAND
        and tuple(
            correct_workspace_bridge_takeover_handoff_result.get(
                "handoff_steps", ()
            )
        )
        == DEFAULT_HANDOFF_STEPS
    )
    automatic_takeover_blocked = bool(
        correct_workspace_bridge_takeover_handoff_result.get(
            "operator_takeover_required"
        )
        and not correct_workspace_bridge_takeover_handoff_result.get(
            "explicit_takeover_approval_recorded"
        )
        and all(
            not correct_workspace_bridge_takeover_handoff_result.get(key)
            for key in (
                "process_termination_command_dispatched",
                "wrong_workspace_editor_stopped",
                "bridge_port_released",
                "correct_workspace_editor_launch_command_dispatched",
                "correct_workspace_editor_started",
                "mcp_server_start_command_dispatched",
                "mcp_server_started",
                "correct_workspace_bridge_started",
            )
        )
    )
    verification_chain_required = bool(
        correct_workspace_bridge_takeover_handoff_result.get(
            "correct_workspace_bridge_verification_required"
        )
        and correct_workspace_bridge_takeover_handoff_result.get(
            "post_takeover_read_only_probe_required"
        )
        and correct_workspace_bridge_takeover_handoff_result.get(
            "asset_authoring_after_takeover_blocked"
        )
        and not correct_workspace_bridge_takeover_handoff_result.get(
            "correct_workspace_bridge_verified"
        )
    )
    live_dispatch_blocked = all(
        not correct_workspace_bridge_takeover_handoff_result.get(key)
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
    compile_save_write_outputs_blocked = all(
        not correct_workspace_bridge_takeover_handoff_result.get(key)
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
        not correct_workspace_bridge_takeover_handoff_result.get(key)
        for key in BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        all_outputs_blocked
        and correct_workspace_bridge_takeover_handoff_result.get(
            "dirty_content_before"
        )
        == correct_workspace_bridge_takeover_handoff_result.get(
            "dirty_content_after"
        )
        and correct_workspace_bridge_takeover_handoff_result.get("dirty_maps_before")
        == correct_workspace_bridge_takeover_handoff_result.get("dirty_maps_after")
        and not correct_workspace_bridge_takeover_handoff_result.get(
            "dirty_content_after"
        )
        and not correct_workspace_bridge_takeover_handoff_result.get(
            "dirty_maps_after"
        )
        and correct_workspace_bridge_takeover_handoff_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        correct_workspace_bridge_takeover_handoff_result.get("error") in (None, "")
    )
    handoff_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and wrong_workspace_context_recorded
        and launch_plan_recorded
        and automatic_takeover_blocked
        and verification_chain_required
        and live_dispatch_blocked
        and compile_save_write_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_correct_workspace_bridge_takeover_handoff_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_481_488_summary_schema_matches": upstream_schema_matches,
        "section_481_488_summary_passed": upstream_summary_passed,
        "section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_ready": (
            upstream_blocker_ready
        ),
        "section_481_488_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "correct_workspace_bridge_takeover_handoff_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "wrong_workspace_bridge_owner_context_recorded": (
            wrong_workspace_context_recorded
        ),
        "correct_workspace_bridge_launch_plan_recorded": launch_plan_recorded,
        "automatic_bridge_takeover_blocked": automatic_takeover_blocked,
        "post_takeover_bridge_verification_chain_required": (
            verification_chain_required
        ),
        "live_durable_dispatch_after_takeover_blocked": live_dispatch_blocked,
        "correct_workspace_bridge_takeover_handoff_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "bridge_takeover_compile_save_write_outputs_blocked": (
            compile_save_write_outputs_blocked
        ),
        "result_has_no_error": result_has_no_error,
        "section_489_correct_workspace_bridge_takeover_handoff_checkpoint_satisfied": (
            handoff_ready
        ),
        "section_490_wrong_workspace_bridge_owner_context_recorded": handoff_ready,
        "section_491_correct_workspace_bridge_launch_plan_recorded": (
            handoff_ready
        ),
        "section_492_automatic_bridge_takeover_blocked": handoff_ready,
        "section_493_post_takeover_bridge_verification_chain_required": (
            handoff_ready
        ),
        "section_494_live_durable_dispatch_after_takeover_blocked": handoff_ready,
        "section_495_correct_workspace_bridge_takeover_handoff_no_write_boundary_verified": (
            handoff_ready
        ),
        "section_496_correct_workspace_bridge_takeover_handoff_release_ready": (
            handoff_ready
        ),
        "correct_workspace_bridge_takeover_handoff_ready": handoff_ready,
        "correct_workspace_bridge_takeover_still_blocked": handoff_ready,
        "final_durable_release_ready": handoff_ready,
        **{
            key: 1 if handoff_ready else 0
            for key in CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_PATH_COUNT_KEYS
        },
        **_blocked_output_counts(correct_workspace_bridge_takeover_handoff_result),
    }


def summarize_durable_executor_authoring_correct_workspace_bridge_takeover_handoff_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "correct_workspace_bridge_takeover_handoff_ready"
            )
            == len(requested)
            and _truthy_count(
                requested, "correct_workspace_bridge_takeover_still_blocked"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_correct_workspace_bridge_takeover_handoff_batch_count": (
            len(requested)
        ),
        "section_481_488_summary_schema_matches_count": _truthy_count(
            requested, "section_481_488_summary_schema_matches"
        ),
        "section_481_488_summary_passed_count": _truthy_count(
            requested, "section_481_488_summary_passed"
        ),
        "section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_ready_count": (
            _truthy_count(
                requested,
                "section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_ready",
            )
        ),
        "section_481_488_outputs_closed_count": _truthy_count(
            requested, "section_481_488_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "correct_workspace_bridge_takeover_handoff_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "correct_workspace_bridge_takeover_handoff_checkpoint_satisfied",
            )
        ),
        "wrong_workspace_bridge_owner_context_recorded_count": _truthy_count(
            requested, "wrong_workspace_bridge_owner_context_recorded"
        ),
        "correct_workspace_bridge_launch_plan_recorded_count": _truthy_count(
            requested, "correct_workspace_bridge_launch_plan_recorded"
        ),
        "automatic_bridge_takeover_blocked_count": _truthy_count(
            requested, "automatic_bridge_takeover_blocked"
        ),
        "post_takeover_bridge_verification_chain_required_count": _truthy_count(
            requested, "post_takeover_bridge_verification_chain_required"
        ),
        "live_durable_dispatch_after_takeover_blocked_count": _truthy_count(
            requested, "live_durable_dispatch_after_takeover_blocked"
        ),
        "correct_workspace_bridge_takeover_handoff_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "correct_workspace_bridge_takeover_handoff_no_write_boundary_verified",
            )
        ),
        "bridge_takeover_compile_save_write_outputs_blocked_count": _truthy_count(
            requested, "bridge_takeover_compile_save_write_outputs_blocked"
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
            for key in CORRECT_WORKSPACE_BRIDGE_TAKEOVER_HANDOFF_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_OUTPUT_COUNT_KEYS
        }
    )
    return summary
