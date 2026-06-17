#!/usr/bin/env python
"""
Sections 537-544 durable executor bridge verification validation execution dry-run.

This contract follows the validation rule dry-run gate. It records the future
validation execution envelope for correct-workspace bridge proof while keeping
validation command dispatch, validation execution, evidence admission, durable
authoring dispatch, compile, save, delete, rename, overwrite, cleanup, and
production writes closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batch_contract as validation_rules


DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_BATCH_SCHEMA = (
    "section_537_544_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_BATCH_SUMMARY_SCHEMA = (
    "section_537_544_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batch_summary_v1"
)
CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_RESULT_SCHEMA = (
    "section_537_544_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result_v1"
)
SECTION_529_536_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_SUMMARY_SCHEMA = (
    validation_rules
    .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_BATCH_SUMMARY_SCHEMA
)

DEFAULT_PROJECT_FILE_PATH = validation_rules.DEFAULT_PROJECT_FILE_PATH
DEFAULT_BRIDGE_HOST = validation_rules.DEFAULT_BRIDGE_HOST
DEFAULT_BRIDGE_PORT = validation_rules.DEFAULT_BRIDGE_PORT
DEFAULT_EDITOR_EXECUTABLE_PATH = validation_rules.DEFAULT_EDITOR_EXECUTABLE_PATH
DEFAULT_MCP_SERVER_COMMAND = validation_rules.DEFAULT_MCP_SERVER_COMMAND
DEFAULT_VALIDATION_EXECUTION_SCOPE = (
    "payload_load",
    "required_field_presence_validate",
    "project_identity_validate",
    "editor_executable_validate",
    "bridge_endpoint_validate",
    "mcp_server_command_validate",
    "read_only_probe_result_validate",
    "dirty_state_validate",
    "timestamp_freshness_validate",
    "placeholder_rejection_validate",
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batch_count",
    "section_521_528_summary_schema_matches_count",
    "section_521_528_summary_passed_count",
    "section_521_528_verification_evidence_payload_dry_run_ready_count",
    "section_521_528_outputs_closed_count",
    "result_schema_matches_count",
    "verification_evidence_validation_rule_dry_run_checkpoint_satisfied_count",
    "schema_validation_rules_recorded_count",
    "identity_validation_rules_recorded_count",
    "read_only_probe_validation_rules_recorded_count",
    "dirty_state_validation_rules_recorded_count",
    "timestamp_and_placeholder_rejection_rules_recorded_count",
    "validation_execution_and_admission_still_blocked_count",
    "validation_rule_dry_run_no_write_boundary_verified_count",
    "validation_rule_dry_run_compile_save_write_outputs_blocked_count",
    "result_has_no_error_count",
    "final_durable_release_ready_count",
    *validation_rules.CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_PATH_COUNT_KEYS,
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    validation_rules
    .BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_OUTPUT_COUNT_KEYS
)

CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_PATH_COUNT_KEYS = (
    "section_537_validation_execution_dry_run_envelope_checkpoint_satisfied_count",
    "section_538_validation_execution_scope_recorded_count",
    "section_539_real_evidence_payload_required_count",
    "section_540_validation_rule_set_binding_required_count",
    "section_541_validation_execution_authorization_still_required_count",
    "section_542_validation_result_admission_still_blocked_count",
    "section_543_validation_execution_dry_run_no_write_boundary_verified_count",
    "section_544_validation_execution_dry_run_release_ready_count",
    "correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_ready_count",
    "verification_evidence_validation_execution_still_blocked_count",
)
BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_OUTPUT_COUNT_KEYS = (
    "validation_execution_command_dispatched_count",
    "validation_execution_command_executed_count",
    "validation_result_recorded_count",
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
BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_RESULT_KEYS = tuple(
    key.removesuffix("_count")
    for key in (
        BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_OUTPUT_COUNT_KEYS
    )
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
            BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_OUTPUT_COUNT_KEYS,
            BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_RESULT_KEYS,
        )
    }


def build_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    editor_executable_path: str = DEFAULT_EDITOR_EXECUTABLE_PATH,
    bridge_host: str = DEFAULT_BRIDGE_HOST,
    bridge_port_number: int = DEFAULT_BRIDGE_PORT,
    mcp_server_command: str = DEFAULT_MCP_SERVER_COMMAND,
    validation_execution_scope: Sequence[str] = DEFAULT_VALIDATION_EXECUTION_SCOPE,
    validation_execution_scope_recorded: bool = True,
    real_evidence_payload_required: bool = True,
    validation_rule_set_binding_required: bool = True,
    validation_execution_authorization_required: bool = True,
    validation_execution_allowed: bool = False,
    verification_result_admission_allowed: bool = False,
    dirty_content_before: Sequence[str] = (),
    dirty_content_after: Sequence[str] = (),
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
    validation_execution_command_dispatched: bool = False,
    validation_execution_command_executed: bool = False,
    validation_result_recorded: bool = False,
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
        "schema": (
            CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_RESULT_SCHEMA
        ),
        "project_file_path": project_file_path,
        "editor_executable_path": editor_executable_path,
        "bridge_host": bridge_host,
        "bridge_port": bridge_port_number,
        "mcp_server_command": mcp_server_command,
        "validation_execution_scope": list(validation_execution_scope),
        "validation_execution_scope_recorded": validation_execution_scope_recorded,
        "real_evidence_payload_required": real_evidence_payload_required,
        "validation_rule_set_binding_required": validation_rule_set_binding_required,
        "validation_execution_authorization_required": (
            validation_execution_authorization_required
        ),
        "validation_execution_allowed": validation_execution_allowed,
        "verification_result_admission_allowed": verification_result_admission_allowed,
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


def build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batch_contract(
    requested: bool,
    section_529_536_verification_evidence_validation_rule_dry_run_summary: Dict[str, Any],
    correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result: Dict[str, Any],
) -> Dict[str, Any]:
    upstream_schema_matches = bool(
        section_529_536_verification_evidence_validation_rule_dry_run_summary.get(
            "schema"
        )
        == SECTION_529_536_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_SUMMARY_SCHEMA
    )
    upstream_summary_passed = bool(
        section_529_536_verification_evidence_validation_rule_dry_run_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_validation_rules_ready = all(
        _count_is_one(
            section_529_536_verification_evidence_validation_rule_dry_run_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_529_536_verification_evidence_validation_rule_dry_run_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "schema"
        )
        == CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and upstream_schema_matches
        and upstream_summary_passed
        and upstream_validation_rules_ready
        and upstream_outputs_closed
    )
    scope = tuple(
        correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "validation_execution_scope", ()
        )
    )
    validation_execution_scope_recorded = bool(
        correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "validation_execution_scope_recorded"
        )
        and scope == DEFAULT_VALIDATION_EXECUTION_SCOPE
        and correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "editor_executable_path"
        )
        == DEFAULT_EDITOR_EXECUTABLE_PATH
        and correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "bridge_host"
        )
        == DEFAULT_BRIDGE_HOST
        and correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "bridge_port"
        )
        == DEFAULT_BRIDGE_PORT
        and correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "mcp_server_command"
        )
        == DEFAULT_MCP_SERVER_COMMAND
    )
    real_evidence_payload_required = bool(
        correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "real_evidence_payload_required"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "evidence_payload_received"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "evidence_payload_ingested"
        )
    )
    validation_rule_set_binding_required = bool(
        correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "validation_rule_set_binding_required"
        )
    )
    validation_execution_authorization_still_required = bool(
        correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "validation_execution_authorization_required"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "validation_execution_allowed"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "validation_execution_command_dispatched"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "validation_execution_command_executed"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "validation_result_recorded"
        )
    )
    validation_result_admission_still_blocked = bool(
        not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "verification_result_admission_allowed"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "evidence_schema_validation_executed"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "evidence_schema_validation_passed"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "verification_evidence_admitted"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "correct_workspace_bridge_verified"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "read_only_probe_result_accepted"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "post_verification_authoring_allowed"
        )
    )
    live_authoring_blocked = all(
        not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
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
        not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
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
        not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            key
        )
        for key in (
            BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_RESULT_KEYS
        )
    )
    no_write_boundary_verified = bool(
        all_outputs_blocked
        and live_authoring_blocked
        and compile_save_write_outputs_blocked
        and correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "dirty_content_before"
        )
        == correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "dirty_content_after"
        )
        and correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "dirty_maps_before"
        )
        == correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "dirty_maps_after"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "dirty_content_after"
        )
        and not correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "dirty_maps_after"
        )
        and correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result.get(
            "error"
        )
        in (None, "")
    )
    validation_execution_envelope_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and validation_execution_scope_recorded
        and real_evidence_payload_required
        and validation_rule_set_binding_required
        and validation_execution_authorization_still_required
        and validation_result_admission_still_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_529_536_summary_schema_matches": upstream_schema_matches,
        "section_529_536_summary_passed": upstream_summary_passed,
        "section_529_536_verification_evidence_validation_rule_dry_run_ready": (
            upstream_validation_rules_ready
        ),
        "section_529_536_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "validation_execution_dry_run_envelope_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "validation_execution_scope_recorded": validation_execution_scope_recorded,
        "real_evidence_payload_required": real_evidence_payload_required,
        "validation_rule_set_binding_required": validation_rule_set_binding_required,
        "validation_execution_authorization_still_required": (
            validation_execution_authorization_still_required
        ),
        "validation_result_admission_still_blocked": (
            validation_result_admission_still_blocked
        ),
        "validation_execution_dry_run_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "validation_execution_dry_run_compile_save_write_outputs_blocked": (
            compile_save_write_outputs_blocked
        ),
        "result_has_no_error": result_has_no_error,
        "section_537_validation_execution_dry_run_envelope_checkpoint_satisfied": (
            validation_execution_envelope_ready
        ),
        "section_538_validation_execution_scope_recorded": (
            validation_execution_envelope_ready
        ),
        "section_539_real_evidence_payload_required": (
            validation_execution_envelope_ready
        ),
        "section_540_validation_rule_set_binding_required": (
            validation_execution_envelope_ready
        ),
        "section_541_validation_execution_authorization_still_required": (
            validation_execution_envelope_ready
        ),
        "section_542_validation_result_admission_still_blocked": (
            validation_execution_envelope_ready
        ),
        "section_543_validation_execution_dry_run_no_write_boundary_verified": (
            validation_execution_envelope_ready
        ),
        "section_544_validation_execution_dry_run_release_ready": (
            validation_execution_envelope_ready
        ),
        "correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_ready": (
            validation_execution_envelope_ready
        ),
        "verification_evidence_validation_execution_still_blocked": (
            validation_execution_envelope_ready
        ),
        "final_durable_release_ready": validation_execution_envelope_ready,
        **{
            key: 1 if validation_execution_envelope_ready else 0
            for key in (
                CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_PATH_COUNT_KEYS
            )
        },
        **_blocked_output_counts(
            correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_result
        ),
    }


def summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "verification_evidence_validation_execution_still_blocked",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_validation_execution_dry_run_envelope_batch_count": (
            len(requested)
        ),
        "section_529_536_summary_schema_matches_count": _truthy_count(
            requested, "section_529_536_summary_schema_matches"
        ),
        "section_529_536_summary_passed_count": _truthy_count(
            requested, "section_529_536_summary_passed"
        ),
        "section_529_536_verification_evidence_validation_rule_dry_run_ready_count": (
            _truthy_count(
                requested,
                "section_529_536_verification_evidence_validation_rule_dry_run_ready",
            )
        ),
        "section_529_536_outputs_closed_count": _truthy_count(
            requested, "section_529_536_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "validation_execution_dry_run_envelope_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "validation_execution_dry_run_envelope_checkpoint_satisfied",
            )
        ),
        "validation_execution_scope_recorded_count": _truthy_count(
            requested, "validation_execution_scope_recorded"
        ),
        "real_evidence_payload_required_count": _truthy_count(
            requested, "real_evidence_payload_required"
        ),
        "validation_rule_set_binding_required_count": _truthy_count(
            requested, "validation_rule_set_binding_required"
        ),
        "validation_execution_authorization_still_required_count": _truthy_count(
            requested, "validation_execution_authorization_still_required"
        ),
        "validation_result_admission_still_blocked_count": _truthy_count(
            requested, "validation_result_admission_still_blocked"
        ),
        "validation_execution_dry_run_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "validation_execution_dry_run_no_write_boundary_verified",
            )
        ),
        "validation_execution_dry_run_compile_save_write_outputs_blocked_count": (
            _truthy_count(
                requested,
                "validation_execution_dry_run_compile_save_write_outputs_blocked",
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
                CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_PATH_COUNT_KEYS
            )
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in (
                BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_EXECUTION_DRY_RUN_ENVELOPE_OUTPUT_COUNT_KEYS
            )
        }
    )
    return summary
