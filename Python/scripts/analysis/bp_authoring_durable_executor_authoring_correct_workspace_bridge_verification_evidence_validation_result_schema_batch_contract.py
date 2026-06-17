#!/usr/bin/env python
"""
Sections 545-552 durable executor bridge validation result schema dry-run.

This contract follows the validation execution dry-run envelope. It records the
schema required for a future validation result while keeping validation result
recording, verification admission, durable authoring dispatch, compile, save,
delete, rename, overwrite, cleanup, and production writes closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batch_contract as validation_envelope


DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_BATCH_SCHEMA = (
    "section_545_552_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_result_schema_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_BATCH_SUMMARY_SCHEMA = (
    "section_545_552_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_result_schema_batch_summary_v1"
)
CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_RESULT_SCHEMA = (
    "section_545_552_correct_workspace_bridge_verification_evidence_validation_result_schema_result_v1"
)
SECTION_537_544_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_SUMMARY_SCHEMA = (
    validation_envelope
    .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_BATCH_SUMMARY_SCHEMA
)

DEFAULT_PROJECT_FILE_PATH = validation_envelope.DEFAULT_PROJECT_FILE_PATH
DEFAULT_BRIDGE_HOST = validation_envelope.DEFAULT_BRIDGE_HOST
DEFAULT_BRIDGE_PORT = validation_envelope.DEFAULT_BRIDGE_PORT
DEFAULT_EDITOR_EXECUTABLE_PATH = validation_envelope.DEFAULT_EDITOR_EXECUTABLE_PATH
DEFAULT_MCP_SERVER_COMMAND = validation_envelope.DEFAULT_MCP_SERVER_COMMAND
DEFAULT_VALIDATION_RESULT_FIELDS = (
    "validation_result_id",
    "project_file_path",
    "editor_executable_path",
    "bridge_host",
    "bridge_port",
    "mcp_server_command",
    "validation_rule_names",
    "passed_rule_names",
    "failed_rule_names",
    "rejection_reasons",
    "validated_at_utc",
    "source_payload_timestamp_utc",
    "no_dirty_content_before",
    "no_dirty_content_after",
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batch_count",
    "section_529_536_summary_schema_matches_count",
    "section_529_536_summary_passed_count",
    "section_529_536_verification_evidence_validation_rule_dry_run_ready_count",
    "section_529_536_outputs_closed_count",
    "result_schema_matches_count",
    "validation_execution_dry_run_envelope_checkpoint_satisfied_count",
    "validation_execution_scope_recorded_count",
    "real_evidence_payload_required_count",
    "validation_rule_set_binding_required_count",
    "validation_execution_authorization_still_required_count",
    "validation_result_admission_still_blocked_count",
    "validation_execution_dry_run_no_write_boundary_verified_count",
    "validation_execution_dry_run_compile_save_write_outputs_blocked_count",
    "result_has_no_error_count",
    "final_durable_release_ready_count",
    *validation_envelope.CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_PATH_COUNT_KEYS,
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    validation_envelope
    .BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_OUTPUT_COUNT_KEYS
)

CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_PATH_COUNT_KEYS = (
    "section_545_validation_result_schema_checkpoint_satisfied_count",
    "section_546_validation_result_fields_recorded_count",
    "section_547_validation_pass_fail_semantics_recorded_count",
    "section_548_validation_rejection_reason_fields_recorded_count",
    "section_549_validation_result_requires_execution_evidence_count",
    "section_550_validation_result_admission_still_blocked_count",
    "section_551_validation_result_schema_no_write_boundary_verified_count",
    "section_552_validation_result_schema_release_ready_count",
    "correct_workspace_bridge_verification_evidence_validation_result_schema_ready_count",
    "verification_validation_result_still_missing_count",
)
BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_OUTPUT_COUNT_KEYS = (
    "validation_execution_command_dispatched_count",
    "validation_execution_command_executed_count",
    "validation_result_recorded_count",
    "validation_result_schema_validation_executed_count",
    "validation_result_schema_validation_passed_count",
    "validation_result_admitted_count",
    "evidence_payload_received_count",
    "evidence_payload_ingested_count",
    "evidence_schema_validation_executed_count",
    "evidence_schema_validation_passed_count",
    "verification_evidence_admitted_count",
    "correct_workspace_bridge_verified_count",
    "read_only_probe_result_accepted_count",
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
BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_RESULT_KEYS = tuple(
    key.removesuffix("_count")
    for key in BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_OUTPUT_COUNT_KEYS
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
            BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_OUTPUT_COUNT_KEYS,
            BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_RESULT_KEYS,
        )
    }


def build_correct_workspace_bridge_verification_evidence_validation_result_schema_result(
    *,
    validation_result_fields: Sequence[str] = DEFAULT_VALIDATION_RESULT_FIELDS,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    editor_executable_path: str = DEFAULT_EDITOR_EXECUTABLE_PATH,
    bridge_host: str = DEFAULT_BRIDGE_HOST,
    bridge_port_number: int = DEFAULT_BRIDGE_PORT,
    mcp_server_command: str = DEFAULT_MCP_SERVER_COMMAND,
    validation_result_fields_recorded: bool = True,
    validation_pass_fail_semantics_recorded: bool = True,
    validation_rejection_reason_fields_recorded: bool = True,
    validation_result_requires_execution_evidence: bool = True,
    validation_result_admission_allowed: bool = False,
    validation_result_recording_allowed: bool = False,
    dirty_content_before: Sequence[str] = (),
    dirty_content_after: Sequence[str] = (),
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
    validation_execution_command_dispatched: bool = False,
    validation_execution_command_executed: bool = False,
    validation_result_recorded: bool = False,
    validation_result_schema_validation_executed: bool = False,
    validation_result_schema_validation_passed: bool = False,
    validation_result_admitted: bool = False,
    evidence_payload_received: bool = False,
    evidence_payload_ingested: bool = False,
    evidence_schema_validation_executed: bool = False,
    evidence_schema_validation_passed: bool = False,
    verification_evidence_admitted: bool = False,
    correct_workspace_bridge_verified: bool = False,
    read_only_probe_result_accepted: bool = False,
    post_verification_authoring_allowed: bool = False,
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
        "schema": CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_RESULT_SCHEMA,
        "validation_result_fields": list(validation_result_fields),
        "project_file_path": project_file_path,
        "editor_executable_path": editor_executable_path,
        "bridge_host": bridge_host,
        "bridge_port": bridge_port_number,
        "mcp_server_command": mcp_server_command,
        "validation_result_fields_recorded": validation_result_fields_recorded,
        "validation_pass_fail_semantics_recorded": (
            validation_pass_fail_semantics_recorded
        ),
        "validation_rejection_reason_fields_recorded": (
            validation_rejection_reason_fields_recorded
        ),
        "validation_result_requires_execution_evidence": (
            validation_result_requires_execution_evidence
        ),
        "validation_result_admission_allowed": validation_result_admission_allowed,
        "validation_result_recording_allowed": validation_result_recording_allowed,
        "dirty_content_before": list(dirty_content_before),
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_preserved": external_dirty_preserved,
        "validation_execution_command_dispatched": (
            validation_execution_command_dispatched
        ),
        "validation_execution_command_executed": (
            validation_execution_command_executed
        ),
        "validation_result_recorded": validation_result_recorded,
        "validation_result_schema_validation_executed": (
            validation_result_schema_validation_executed
        ),
        "validation_result_schema_validation_passed": (
            validation_result_schema_validation_passed
        ),
        "validation_result_admitted": validation_result_admitted,
        "evidence_payload_received": evidence_payload_received,
        "evidence_payload_ingested": evidence_payload_ingested,
        "evidence_schema_validation_executed": evidence_schema_validation_executed,
        "evidence_schema_validation_passed": evidence_schema_validation_passed,
        "verification_evidence_admitted": verification_evidence_admitted,
        "correct_workspace_bridge_verified": correct_workspace_bridge_verified,
        "read_only_probe_result_accepted": read_only_probe_result_accepted,
        "post_verification_authoring_allowed": post_verification_authoring_allowed,
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


def build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_result_schema_batch_contract(
    requested: bool,
    section_537_544_validation_execution_dry_run_envelope_summary: Dict[str, Any],
    correct_workspace_bridge_verification_evidence_validation_result_schema_result: Dict[str, Any],
) -> Dict[str, Any]:
    upstream_schema_matches = bool(
        section_537_544_validation_execution_dry_run_envelope_summary.get("schema")
        == SECTION_537_544_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_SUMMARY_SCHEMA
    )
    upstream_summary_passed = bool(
        section_537_544_validation_execution_dry_run_envelope_summary.get("status")
        == "passed"
    )
    upstream_execution_envelope_ready = all(
        _count_is_one(
            section_537_544_validation_execution_dry_run_envelope_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_537_544_validation_execution_dry_run_envelope_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "schema"
        )
        == CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and upstream_schema_matches
        and upstream_summary_passed
        and upstream_execution_envelope_ready
        and upstream_outputs_closed
    )
    validation_result_fields_recorded = bool(
        correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "validation_result_fields_recorded"
        )
        and tuple(
            correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
                "validation_result_fields", ()
            )
        )
        == DEFAULT_VALIDATION_RESULT_FIELDS
        and correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "editor_executable_path"
        )
        == DEFAULT_EDITOR_EXECUTABLE_PATH
        and correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "bridge_host"
        )
        == DEFAULT_BRIDGE_HOST
        and correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "bridge_port"
        )
        == DEFAULT_BRIDGE_PORT
        and correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "mcp_server_command"
        )
        == DEFAULT_MCP_SERVER_COMMAND
    )
    validation_pass_fail_semantics_recorded = bool(
        correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "validation_pass_fail_semantics_recorded"
        )
        and "passed_rule_names"
        in correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "validation_result_fields", ()
        )
        and "failed_rule_names"
        in correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "validation_result_fields", ()
        )
    )
    validation_rejection_reason_fields_recorded = bool(
        correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "validation_rejection_reason_fields_recorded"
        )
        and "rejection_reasons"
        in correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "validation_result_fields", ()
        )
    )
    validation_result_requires_execution_evidence = bool(
        correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "validation_result_requires_execution_evidence"
        )
        and not correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "validation_execution_command_executed"
        )
        and not correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "validation_result_recorded"
        )
    )
    validation_result_admission_still_blocked = bool(
        not correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "validation_result_admission_allowed"
        )
        and not correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "validation_result_recording_allowed"
        )
        and all(
            not correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
                key
            )
            for key in (
                "validation_result_recorded",
                "validation_result_schema_validation_executed",
                "validation_result_schema_validation_passed",
                "validation_result_admitted",
                "verification_evidence_admitted",
                "correct_workspace_bridge_verified",
                "read_only_probe_result_accepted",
                "post_verification_authoring_allowed",
            )
        )
    )
    live_authoring_blocked = all(
        not correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
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
        not correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
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
        not correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            key
        )
        for key in BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        all_outputs_blocked
        and live_authoring_blocked
        and compile_save_write_outputs_blocked
        and correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "dirty_content_before"
        )
        == correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "dirty_content_after"
        )
        and correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "dirty_maps_before"
        )
        == correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "dirty_maps_after"
        )
        and not correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "dirty_content_after"
        )
        and not correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "dirty_maps_after"
        )
        and correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        correct_workspace_bridge_verification_evidence_validation_result_schema_result.get(
            "error"
        )
        in (None, "")
    )
    validation_result_schema_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and validation_result_fields_recorded
        and validation_pass_fail_semantics_recorded
        and validation_rejection_reason_fields_recorded
        and validation_result_requires_execution_evidence
        and validation_result_admission_still_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_result_schema_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_537_544_summary_schema_matches": upstream_schema_matches,
        "section_537_544_summary_passed": upstream_summary_passed,
        "section_537_544_validation_execution_dry_run_envelope_ready": (
            upstream_execution_envelope_ready
        ),
        "section_537_544_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "validation_result_schema_checkpoint_satisfied": checkpoint_satisfied,
        "validation_result_fields_recorded": validation_result_fields_recorded,
        "validation_pass_fail_semantics_recorded": (
            validation_pass_fail_semantics_recorded
        ),
        "validation_rejection_reason_fields_recorded": (
            validation_rejection_reason_fields_recorded
        ),
        "validation_result_requires_execution_evidence": (
            validation_result_requires_execution_evidence
        ),
        "validation_result_admission_still_blocked": (
            validation_result_admission_still_blocked
        ),
        "validation_result_schema_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "validation_result_schema_compile_save_write_outputs_blocked": (
            compile_save_write_outputs_blocked
        ),
        "result_has_no_error": result_has_no_error,
        "section_545_validation_result_schema_checkpoint_satisfied": (
            validation_result_schema_ready
        ),
        "section_546_validation_result_fields_recorded": (
            validation_result_schema_ready
        ),
        "section_547_validation_pass_fail_semantics_recorded": (
            validation_result_schema_ready
        ),
        "section_548_validation_rejection_reason_fields_recorded": (
            validation_result_schema_ready
        ),
        "section_549_validation_result_requires_execution_evidence": (
            validation_result_schema_ready
        ),
        "section_550_validation_result_admission_still_blocked": (
            validation_result_schema_ready
        ),
        "section_551_validation_result_schema_no_write_boundary_verified": (
            validation_result_schema_ready
        ),
        "section_552_validation_result_schema_release_ready": (
            validation_result_schema_ready
        ),
        "correct_workspace_bridge_verification_evidence_validation_result_schema_ready": (
            validation_result_schema_ready
        ),
        "verification_validation_result_still_missing": (
            validation_result_schema_ready
        ),
        "final_durable_release_ready": validation_result_schema_ready,
        **{
            key: 1 if validation_result_schema_ready else 0
            for key in (
                CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_PATH_COUNT_KEYS
            )
        },
        **_blocked_output_counts(
            correct_workspace_bridge_verification_evidence_validation_result_schema_result
        ),
    }


def summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_result_schema_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "correct_workspace_bridge_verification_evidence_validation_result_schema_ready",
            )
            == len(requested)
            and _truthy_count(
                requested, "verification_validation_result_still_missing"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_validation_result_schema_batch_count": (
            len(requested)
        ),
        "section_537_544_summary_schema_matches_count": _truthy_count(
            requested, "section_537_544_summary_schema_matches"
        ),
        "section_537_544_summary_passed_count": _truthy_count(
            requested, "section_537_544_summary_passed"
        ),
        "section_537_544_validation_execution_dry_run_envelope_ready_count": (
            _truthy_count(
                requested,
                "section_537_544_validation_execution_dry_run_envelope_ready",
            )
        ),
        "section_537_544_outputs_closed_count": _truthy_count(
            requested, "section_537_544_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "validation_result_schema_checkpoint_satisfied_count": _truthy_count(
            requested, "validation_result_schema_checkpoint_satisfied"
        ),
        "validation_result_fields_recorded_count": _truthy_count(
            requested, "validation_result_fields_recorded"
        ),
        "validation_pass_fail_semantics_recorded_count": _truthy_count(
            requested, "validation_pass_fail_semantics_recorded"
        ),
        "validation_rejection_reason_fields_recorded_count": _truthy_count(
            requested, "validation_rejection_reason_fields_recorded"
        ),
        "validation_result_requires_execution_evidence_count": _truthy_count(
            requested, "validation_result_requires_execution_evidence"
        ),
        "validation_result_admission_still_blocked_count": _truthy_count(
            requested, "validation_result_admission_still_blocked"
        ),
        "validation_result_schema_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "validation_result_schema_no_write_boundary_verified",
            )
        ),
        "validation_result_schema_compile_save_write_outputs_blocked_count": (
            _truthy_count(
                requested,
                "validation_result_schema_compile_save_write_outputs_blocked",
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
                CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_PATH_COUNT_KEYS
            )
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in (
                BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RESULT_SCHEMA_OUTPUT_COUNT_KEYS
            )
        }
    )
    return summary
