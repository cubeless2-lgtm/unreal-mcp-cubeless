#!/usr/bin/env python
"""
Sections 505-512 durable executor post-takeover bridge verification admission.

This contract follows the bridge takeover execution dry-run envelope. It records
that post-takeover verification evidence cannot be admitted until actual
takeover execution completes and the correct workspace bridge is proven through
a read-only probe. Until then, verification admission, durable authoring
dispatch, compile, save, delete, rename, overwrite, cleanup, and production
writes stay closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batch_contract as takeover_envelope


DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_POST_TAKEOVER_VERIFICATION_ADMISSION_BATCH_SCHEMA = (
    "section_505_512_durable_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_POST_TAKEOVER_VERIFICATION_ADMISSION_BATCH_SUMMARY_SCHEMA = (
    "section_505_512_durable_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batch_summary_v1"
)
CORRECT_WORKSPACE_BRIDGE_POST_TAKEOVER_VERIFICATION_ADMISSION_RESULT_SCHEMA = (
    "section_505_512_correct_workspace_bridge_post_takeover_verification_admission_result_v1"
)
SECTION_497_504_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_SUMMARY_SCHEMA = (
    takeover_envelope
    .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_BATCH_SUMMARY_SCHEMA
)

DEFAULT_PROJECT_FILE_PATH = takeover_envelope.DEFAULT_PROJECT_FILE_PATH
DEFAULT_BRIDGE_HOST = takeover_envelope.DEFAULT_BRIDGE_HOST
DEFAULT_BRIDGE_PORT = takeover_envelope.DEFAULT_BRIDGE_PORT
DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH = (
    takeover_envelope.DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH
)
DEFAULT_EDITOR_EXECUTABLE_PATH = takeover_envelope.DEFAULT_EDITOR_EXECUTABLE_PATH
DEFAULT_MCP_SERVER_COMMAND = takeover_envelope.DEFAULT_MCP_SERVER_COMMAND

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_correct_workspace_bridge_takeover_execution_dry_run_envelope_batch_count",
    "section_489_496_summary_schema_matches_count",
    "section_489_496_summary_passed_count",
    "section_489_496_correct_workspace_bridge_takeover_handoff_ready_count",
    "section_489_496_outputs_closed_count",
    "result_schema_matches_count",
    "correct_workspace_bridge_takeover_execution_dry_run_checkpoint_satisfied_count",
    "takeover_execution_scope_recorded_count",
    "takeover_execution_authorization_still_required_count",
    "wrong_workspace_release_command_blocked_count",
    "correct_workspace_editor_launch_command_blocked_count",
    "correct_workspace_bridge_verification_command_blocked_count",
    "live_durable_dispatch_after_takeover_execution_blocked_count",
    "takeover_execution_dry_run_no_write_boundary_verified_count",
    "takeover_execution_compile_save_write_outputs_blocked_count",
    "result_has_no_error_count",
    "final_durable_release_ready_count",
    *takeover_envelope.CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_PATH_COUNT_KEYS,
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    takeover_envelope
    .BLOCKED_CORRECT_WORKSPACE_BRIDGE_TAKEOVER_EXECUTION_OUTPUT_COUNT_KEYS
)

CORRECT_WORKSPACE_BRIDGE_POST_TAKEOVER_VERIFICATION_ADMISSION_PATH_COUNT_KEYS = (
    "section_505_post_takeover_verification_admission_checkpoint_satisfied_count",
    "section_506_takeover_execution_completion_evidence_required_count",
    "section_507_correct_workspace_bridge_identity_evidence_required_count",
    "section_508_read_only_probe_evidence_required_count",
    "section_509_verification_result_admission_blocked_count",
    "section_510_live_authoring_after_verification_blocked_count",
    "section_511_post_takeover_verification_admission_no_write_boundary_verified_count",
    "section_512_post_takeover_verification_admission_release_ready_count",
    "correct_workspace_bridge_post_takeover_verification_admission_ready_count",
    "correct_workspace_bridge_verification_result_still_missing_count",
)
BLOCKED_POST_TAKEOVER_VERIFICATION_ADMISSION_OUTPUT_COUNT_KEYS = (
    "takeover_execution_completed_count",
    "correct_workspace_editor_process_detected_count",
    "correct_workspace_bridge_port_owned_count",
    "correct_workspace_bridge_started_count",
    "correct_workspace_bridge_verified_count",
    "read_only_probe_command_dispatched_count",
    "read_only_probe_executed_count",
    "read_only_probe_result_recorded_count",
    "read_only_probe_passed_count",
    "verification_result_admitted_count",
    "post_verification_authoring_allowed_count",
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
BLOCKED_POST_TAKEOVER_VERIFICATION_ADMISSION_RESULT_KEYS = tuple(
    key.removesuffix("_count")
    for key in BLOCKED_POST_TAKEOVER_VERIFICATION_ADMISSION_OUTPUT_COUNT_KEYS
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
            BLOCKED_POST_TAKEOVER_VERIFICATION_ADMISSION_OUTPUT_COUNT_KEYS,
            BLOCKED_POST_TAKEOVER_VERIFICATION_ADMISSION_RESULT_KEYS,
        )
    }


def build_correct_workspace_bridge_post_takeover_verification_admission_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    bridge_host: str = DEFAULT_BRIDGE_HOST,
    bridge_port_number: int = DEFAULT_BRIDGE_PORT,
    wrong_workspace_project_file_path: str = DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH,
    expected_editor_executable_path: str = DEFAULT_EDITOR_EXECUTABLE_PATH,
    expected_mcp_server_command: str = DEFAULT_MCP_SERVER_COMMAND,
    operator_takeover_required: bool = True,
    actual_takeover_execution_allowed: bool = False,
    verification_evidence_required: bool = True,
    takeover_execution_completed: bool = False,
    correct_workspace_editor_process_detected: bool = False,
    correct_workspace_bridge_port_owned: bool = False,
    correct_workspace_bridge_started: bool = False,
    correct_workspace_bridge_verified: bool = False,
    read_only_probe_command_dispatched: bool = False,
    read_only_probe_executed: bool = False,
    read_only_probe_result_recorded: bool = False,
    read_only_probe_passed: bool = False,
    verification_result_admitted: bool = False,
    post_verification_authoring_allowed: bool = False,
    dirty_content_before: Sequence[str] = (),
    dirty_content_after: Sequence[str] = (),
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
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
            CORRECT_WORKSPACE_BRIDGE_POST_TAKEOVER_VERIFICATION_ADMISSION_RESULT_SCHEMA
        ),
        "project_file_path": project_file_path,
        "bridge_host": bridge_host,
        "bridge_port": bridge_port_number,
        "wrong_workspace_project_file_path": wrong_workspace_project_file_path,
        "expected_editor_executable_path": expected_editor_executable_path,
        "expected_mcp_server_command": expected_mcp_server_command,
        "operator_takeover_required": operator_takeover_required,
        "actual_takeover_execution_allowed": actual_takeover_execution_allowed,
        "verification_evidence_required": verification_evidence_required,
        "takeover_execution_completed": takeover_execution_completed,
        "correct_workspace_editor_process_detected": (
            correct_workspace_editor_process_detected
        ),
        "correct_workspace_bridge_port_owned": correct_workspace_bridge_port_owned,
        "correct_workspace_bridge_started": correct_workspace_bridge_started,
        "correct_workspace_bridge_verified": correct_workspace_bridge_verified,
        "read_only_probe_command_dispatched": read_only_probe_command_dispatched,
        "read_only_probe_executed": read_only_probe_executed,
        "read_only_probe_result_recorded": read_only_probe_result_recorded,
        "read_only_probe_passed": read_only_probe_passed,
        "verification_result_admitted": verification_result_admitted,
        "post_verification_authoring_allowed": post_verification_authoring_allowed,
        "dirty_content_before": list(dirty_content_before),
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_preserved": external_dirty_preserved,
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


def build_durable_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batch_contract(
    requested: bool,
    section_497_504_takeover_execution_dry_run_envelope_summary: Dict[str, Any],
    correct_workspace_bridge_post_takeover_verification_admission_result: Dict[str, Any],
) -> Dict[str, Any]:
    upstream_schema_matches = bool(
        section_497_504_takeover_execution_dry_run_envelope_summary.get("schema")
        == SECTION_497_504_TAKEOVER_EXECUTION_DRY_RUN_ENVELOPE_SUMMARY_SCHEMA
    )
    upstream_summary_passed = bool(
        section_497_504_takeover_execution_dry_run_envelope_summary.get("status")
        == "passed"
    )
    upstream_envelope_ready = all(
        _count_is_one(
            section_497_504_takeover_execution_dry_run_envelope_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_497_504_takeover_execution_dry_run_envelope_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "schema"
        )
        == CORRECT_WORKSPACE_BRIDGE_POST_TAKEOVER_VERIFICATION_ADMISSION_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and upstream_schema_matches
        and upstream_summary_passed
        and upstream_envelope_ready
        and upstream_outputs_closed
    )
    takeover_completion_evidence_required = bool(
        correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "bridge_host"
        )
        == DEFAULT_BRIDGE_HOST
        and correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "bridge_port"
        )
        == DEFAULT_BRIDGE_PORT
        and correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "wrong_workspace_project_file_path"
        )
        == DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH
        and correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "expected_editor_executable_path"
        )
        == DEFAULT_EDITOR_EXECUTABLE_PATH
        and correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "expected_mcp_server_command"
        )
        == DEFAULT_MCP_SERVER_COMMAND
        and correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "operator_takeover_required"
        )
        and not correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "actual_takeover_execution_allowed"
        )
        and not correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "takeover_execution_completed"
        )
    )
    bridge_identity_evidence_required = all(
        not correct_workspace_bridge_post_takeover_verification_admission_result.get(
            key
        )
        for key in (
            "correct_workspace_editor_process_detected",
            "correct_workspace_bridge_port_owned",
            "correct_workspace_bridge_started",
            "correct_workspace_bridge_verified",
        )
    )
    read_only_probe_evidence_required = bool(
        correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "verification_evidence_required"
        )
        and all(
            not correct_workspace_bridge_post_takeover_verification_admission_result.get(
                key
            )
            for key in (
                "read_only_probe_command_dispatched",
                "read_only_probe_executed",
                "read_only_probe_result_recorded",
                "read_only_probe_passed",
            )
        )
    )
    verification_result_admission_blocked = bool(
        not correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "verification_result_admitted"
        )
        and not correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "post_verification_authoring_allowed"
        )
    )
    live_authoring_after_verification_blocked = all(
        not correct_workspace_bridge_post_takeover_verification_admission_result.get(
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
    compile_save_write_outputs_blocked = all(
        not correct_workspace_bridge_post_takeover_verification_admission_result.get(
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
        not correct_workspace_bridge_post_takeover_verification_admission_result.get(
            key
        )
        for key in BLOCKED_POST_TAKEOVER_VERIFICATION_ADMISSION_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        all_outputs_blocked
        and correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "dirty_content_before"
        )
        == correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "dirty_content_after"
        )
        and correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "dirty_maps_before"
        )
        == correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "dirty_maps_after"
        )
        and not correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "dirty_content_after"
        )
        and not correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "dirty_maps_after"
        )
        and correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        correct_workspace_bridge_post_takeover_verification_admission_result.get(
            "error"
        )
        in (None, "")
    )
    admission_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and takeover_completion_evidence_required
        and bridge_identity_evidence_required
        and read_only_probe_evidence_required
        and verification_result_admission_blocked
        and live_authoring_after_verification_blocked
        and compile_save_write_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_POST_TAKEOVER_VERIFICATION_ADMISSION_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_497_504_summary_schema_matches": upstream_schema_matches,
        "section_497_504_summary_passed": upstream_summary_passed,
        "section_497_504_takeover_execution_dry_run_envelope_ready": (
            upstream_envelope_ready
        ),
        "section_497_504_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "post_takeover_verification_admission_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "takeover_execution_completion_evidence_required": (
            takeover_completion_evidence_required
        ),
        "correct_workspace_bridge_identity_evidence_required": (
            bridge_identity_evidence_required
        ),
        "read_only_probe_evidence_required": read_only_probe_evidence_required,
        "verification_result_admission_blocked": (
            verification_result_admission_blocked
        ),
        "live_authoring_after_verification_blocked": (
            live_authoring_after_verification_blocked
        ),
        "post_takeover_verification_admission_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "post_takeover_verification_compile_save_write_outputs_blocked": (
            compile_save_write_outputs_blocked
        ),
        "result_has_no_error": result_has_no_error,
        "section_505_post_takeover_verification_admission_checkpoint_satisfied": (
            admission_ready
        ),
        "section_506_takeover_execution_completion_evidence_required": (
            admission_ready
        ),
        "section_507_correct_workspace_bridge_identity_evidence_required": (
            admission_ready
        ),
        "section_508_read_only_probe_evidence_required": admission_ready,
        "section_509_verification_result_admission_blocked": admission_ready,
        "section_510_live_authoring_after_verification_blocked": (
            admission_ready
        ),
        "section_511_post_takeover_verification_admission_no_write_boundary_verified": (
            admission_ready
        ),
        "section_512_post_takeover_verification_admission_release_ready": (
            admission_ready
        ),
        "correct_workspace_bridge_post_takeover_verification_admission_ready": (
            admission_ready
        ),
        "correct_workspace_bridge_verification_result_still_missing": (
            admission_ready
        ),
        "final_durable_release_ready": admission_ready,
        **{
            key: 1 if admission_ready else 0
            for key in (
                CORRECT_WORKSPACE_BRIDGE_POST_TAKEOVER_VERIFICATION_ADMISSION_PATH_COUNT_KEYS
            )
        },
        **_blocked_output_counts(
            correct_workspace_bridge_post_takeover_verification_admission_result
        ),
    }


def summarize_durable_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "correct_workspace_bridge_post_takeover_verification_admission_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "correct_workspace_bridge_verification_result_still_missing",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_POST_TAKEOVER_VERIFICATION_ADMISSION_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_POST_TAKEOVER_VERIFICATION_ADMISSION_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_correct_workspace_bridge_post_takeover_verification_admission_batch_count": (
            len(requested)
        ),
        "section_497_504_summary_schema_matches_count": _truthy_count(
            requested, "section_497_504_summary_schema_matches"
        ),
        "section_497_504_summary_passed_count": _truthy_count(
            requested, "section_497_504_summary_passed"
        ),
        "section_497_504_takeover_execution_dry_run_envelope_ready_count": (
            _truthy_count(
                requested,
                "section_497_504_takeover_execution_dry_run_envelope_ready",
            )
        ),
        "section_497_504_outputs_closed_count": _truthy_count(
            requested, "section_497_504_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "post_takeover_verification_admission_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "post_takeover_verification_admission_checkpoint_satisfied",
            )
        ),
        "takeover_execution_completion_evidence_required_count": _truthy_count(
            requested, "takeover_execution_completion_evidence_required"
        ),
        "correct_workspace_bridge_identity_evidence_required_count": (
            _truthy_count(
                requested, "correct_workspace_bridge_identity_evidence_required"
            )
        ),
        "read_only_probe_evidence_required_count": _truthy_count(
            requested, "read_only_probe_evidence_required"
        ),
        "verification_result_admission_blocked_count": _truthy_count(
            requested, "verification_result_admission_blocked"
        ),
        "live_authoring_after_verification_blocked_count": _truthy_count(
            requested, "live_authoring_after_verification_blocked"
        ),
        "post_takeover_verification_admission_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "post_takeover_verification_admission_no_write_boundary_verified",
            )
        ),
        "post_takeover_verification_compile_save_write_outputs_blocked_count": (
            _truthy_count(
                requested,
                "post_takeover_verification_compile_save_write_outputs_blocked",
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
                CORRECT_WORKSPACE_BRIDGE_POST_TAKEOVER_VERIFICATION_ADMISSION_PATH_COUNT_KEYS
            )
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in (
                BLOCKED_POST_TAKEOVER_VERIFICATION_ADMISSION_OUTPUT_COUNT_KEYS
            )
        }
    )
    return summary
