#!/usr/bin/env python
"""
Sections 529-536 durable executor bridge verification validation rule dry-run.

This contract follows the verification evidence payload dry-run gate. It records
the validation rule set that a future correct-workspace bridge proof must pass
while keeping validation execution, payload ingest, verification admission,
durable authoring dispatch, compile, save, delete, rename, overwrite, cleanup,
and production writes closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batch_contract as payload_dry_run


DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_BATCH_SCHEMA = (
    "section_529_536_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_BATCH_SUMMARY_SCHEMA = (
    "section_529_536_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batch_summary_v1"
)
CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_RESULT_SCHEMA = (
    "section_529_536_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result_v1"
)
SECTION_521_528_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_SUMMARY_SCHEMA = (
    payload_dry_run
    .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_BATCH_SUMMARY_SCHEMA
)

DEFAULT_PROJECT_FILE_PATH = payload_dry_run.DEFAULT_PROJECT_FILE_PATH
DEFAULT_BRIDGE_HOST = payload_dry_run.DEFAULT_BRIDGE_HOST
DEFAULT_BRIDGE_PORT = payload_dry_run.DEFAULT_BRIDGE_PORT
DEFAULT_EDITOR_EXECUTABLE_PATH = payload_dry_run.DEFAULT_EDITOR_EXECUTABLE_PATH
DEFAULT_MCP_SERVER_COMMAND = payload_dry_run.DEFAULT_MCP_SERVER_COMMAND
DEFAULT_REQUIRED_EVIDENCE_FIELDS = payload_dry_run.DEFAULT_REQUIRED_EVIDENCE_FIELDS
DEFAULT_REJECTION_FIXTURE_NAMES = payload_dry_run.DEFAULT_REJECTION_FIXTURE_NAMES
DEFAULT_VALIDATION_RULE_NAMES = (
    "required_field_presence",
    "project_file_path_matches_managed_workspace",
    "editor_executable_path_matches_expected_engine",
    "bridge_endpoint_matches_unreal_mcp_primary_port",
    "mcp_server_command_matches_expected_uv_command",
    "read_only_probe_result_is_actual_success",
    "dirty_content_before_is_empty",
    "dirty_content_after_is_empty",
    "timestamp_utc_is_fresh_and_parseable",
    "placeholder_payload_values_are_rejected",
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batch_count",
    "section_513_520_summary_schema_matches_count",
    "section_513_520_summary_passed_count",
    "section_513_520_verification_evidence_schema_ready_count",
    "section_513_520_outputs_closed_count",
    "result_schema_matches_count",
    "verification_evidence_payload_dry_run_checkpoint_satisfied_count",
    "payload_template_fields_mapped_count",
    "payload_identity_expectations_bound_count",
    "payload_dirty_state_placeholders_recorded_count",
    "rejection_fixture_matrix_recorded_count",
    "payload_ingest_and_admission_still_blocked_count",
    "payload_dry_run_no_write_boundary_verified_count",
    "payload_dry_run_compile_save_write_outputs_blocked_count",
    "result_has_no_error_count",
    "final_durable_release_ready_count",
    *payload_dry_run.CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_PATH_COUNT_KEYS,
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    payload_dry_run
    .BLOCKED_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_OUTPUT_COUNT_KEYS
)

CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_PATH_COUNT_KEYS = (
    "section_529_verification_evidence_validation_rule_dry_run_checkpoint_satisfied_count",
    "section_530_schema_validation_rules_recorded_count",
    "section_531_identity_validation_rules_recorded_count",
    "section_532_read_only_probe_validation_rules_recorded_count",
    "section_533_dirty_state_validation_rules_recorded_count",
    "section_534_timestamp_and_placeholder_rejection_rules_recorded_count",
    "section_535_validation_execution_and_admission_still_blocked_count",
    "section_536_validation_rule_dry_run_release_ready_count",
    "correct_workspace_bridge_verification_evidence_validation_rule_dry_run_ready_count",
    "verification_evidence_validation_not_executed_count",
)
BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_OUTPUT_COUNT_KEYS = (
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
BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_RESULT_KEYS = tuple(
    key.removesuffix("_count")
    for key in BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_OUTPUT_COUNT_KEYS
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
            BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_OUTPUT_COUNT_KEYS,
            BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_RESULT_KEYS,
        )
    }


def build_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result(
    *,
    validation_rule_names: Sequence[str] = DEFAULT_VALIDATION_RULE_NAMES,
    rejection_fixture_names: Sequence[str] = DEFAULT_REJECTION_FIXTURE_NAMES,
    required_evidence_fields: Sequence[str] = DEFAULT_REQUIRED_EVIDENCE_FIELDS,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    editor_executable_path: str = DEFAULT_EDITOR_EXECUTABLE_PATH,
    bridge_host: str = DEFAULT_BRIDGE_HOST,
    bridge_port_number: int = DEFAULT_BRIDGE_PORT,
    mcp_server_command: str = DEFAULT_MCP_SERVER_COMMAND,
    schema_validation_rules_recorded: bool = True,
    identity_validation_rules_recorded: bool = True,
    read_only_probe_validation_rules_recorded: bool = True,
    dirty_state_validation_rules_recorded: bool = True,
    timestamp_validation_rules_recorded: bool = True,
    placeholder_rejection_rules_recorded: bool = True,
    validation_rule_set_is_dry_run_only: bool = True,
    payload_ingest_allowed: bool = False,
    evidence_schema_validation_allowed: bool = False,
    verification_result_admission_allowed: bool = False,
    dirty_content_before: Sequence[str] = (),
    dirty_content_after: Sequence[str] = (),
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
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
            CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_RESULT_SCHEMA
        ),
        "validation_rule_names": list(validation_rule_names),
        "rejection_fixture_names": list(rejection_fixture_names),
        "required_evidence_fields": list(required_evidence_fields),
        "project_file_path": project_file_path,
        "editor_executable_path": editor_executable_path,
        "bridge_host": bridge_host,
        "bridge_port": bridge_port_number,
        "mcp_server_command": mcp_server_command,
        "schema_validation_rules_recorded": schema_validation_rules_recorded,
        "identity_validation_rules_recorded": identity_validation_rules_recorded,
        "read_only_probe_validation_rules_recorded": (
            read_only_probe_validation_rules_recorded
        ),
        "dirty_state_validation_rules_recorded": (
            dirty_state_validation_rules_recorded
        ),
        "timestamp_validation_rules_recorded": timestamp_validation_rules_recorded,
        "placeholder_rejection_rules_recorded": (
            placeholder_rejection_rules_recorded
        ),
        "validation_rule_set_is_dry_run_only": validation_rule_set_is_dry_run_only,
        "payload_ingest_allowed": payload_ingest_allowed,
        "evidence_schema_validation_allowed": evidence_schema_validation_allowed,
        "verification_result_admission_allowed": verification_result_admission_allowed,
        "dirty_content_before": list(dirty_content_before),
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_preserved": external_dirty_preserved,
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


def build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batch_contract(
    requested: bool,
    section_521_528_verification_evidence_payload_dry_run_summary: Dict[str, Any],
    correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result: Dict[str, Any],
) -> Dict[str, Any]:
    upstream_schema_matches = bool(
        section_521_528_verification_evidence_payload_dry_run_summary.get(
            "schema"
        )
        == SECTION_521_528_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_SUMMARY_SCHEMA
    )
    upstream_summary_passed = bool(
        section_521_528_verification_evidence_payload_dry_run_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_payload_dry_run_ready = all(
        _count_is_one(
            section_521_528_verification_evidence_payload_dry_run_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_521_528_verification_evidence_payload_dry_run_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "schema"
        )
        == CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and upstream_schema_matches
        and upstream_summary_passed
        and upstream_payload_dry_run_ready
        and upstream_outputs_closed
    )
    validation_rule_names = set(
        correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "validation_rule_names", ()
        )
    )
    schema_validation_rules_recorded = bool(
        correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "schema_validation_rules_recorded"
        )
        and tuple(
            correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
                "required_evidence_fields", ()
            )
        )
        == DEFAULT_REQUIRED_EVIDENCE_FIELDS
        and "required_field_presence" in validation_rule_names
    )
    identity_validation_rules_recorded = bool(
        correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "identity_validation_rules_recorded"
        )
        and correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "editor_executable_path"
        )
        == DEFAULT_EDITOR_EXECUTABLE_PATH
        and correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "bridge_host"
        )
        == DEFAULT_BRIDGE_HOST
        and correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "bridge_port"
        )
        == DEFAULT_BRIDGE_PORT
        and correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "mcp_server_command"
        )
        == DEFAULT_MCP_SERVER_COMMAND
        and {
            "project_file_path_matches_managed_workspace",
            "editor_executable_path_matches_expected_engine",
            "bridge_endpoint_matches_unreal_mcp_primary_port",
            "mcp_server_command_matches_expected_uv_command",
        }.issubset(validation_rule_names)
    )
    read_only_probe_validation_rules_recorded = bool(
        correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "read_only_probe_validation_rules_recorded"
        )
        and "read_only_probe_result_is_actual_success" in validation_rule_names
    )
    dirty_state_validation_rules_recorded = bool(
        correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "dirty_state_validation_rules_recorded"
        )
        and {
            "dirty_content_before_is_empty",
            "dirty_content_after_is_empty",
        }.issubset(validation_rule_names)
    )
    timestamp_and_placeholder_rejection_rules_recorded = bool(
        correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "timestamp_validation_rules_recorded"
        )
        and correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "placeholder_rejection_rules_recorded"
        )
        and "timestamp_utc_is_fresh_and_parseable" in validation_rule_names
        and "placeholder_payload_values_are_rejected" in validation_rule_names
        and set(
            correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
                "rejection_fixture_names", ()
            )
        )
        >= set(DEFAULT_REJECTION_FIXTURE_NAMES)
    )
    validation_execution_and_admission_still_blocked = bool(
        correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "validation_rule_set_is_dry_run_only"
        )
        and not correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "payload_ingest_allowed"
        )
        and not correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "evidence_schema_validation_allowed"
        )
        and not correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "verification_result_admission_allowed"
        )
        and all(
            not correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
                key
            )
            for key in (
                "evidence_payload_received",
                "evidence_payload_ingested",
                "evidence_schema_validation_executed",
                "evidence_schema_validation_passed",
                "verification_evidence_admitted",
                "correct_workspace_bridge_verified",
                "read_only_probe_result_accepted",
                "post_verification_authoring_allowed",
            )
        )
    )
    live_authoring_blocked = all(
        not correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
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
        not correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
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
        not correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            key
        )
        for key in BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        all_outputs_blocked
        and live_authoring_blocked
        and compile_save_write_outputs_blocked
        and correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "dirty_content_before"
        )
        == correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "dirty_content_after"
        )
        and correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "dirty_maps_before"
        )
        == correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "dirty_maps_after"
        )
        and not correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "dirty_content_after"
        )
        and not correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "dirty_maps_after"
        )
        and correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result.get(
            "error"
        )
        in (None, "")
    )
    validation_rule_dry_run_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and schema_validation_rules_recorded
        and identity_validation_rules_recorded
        and read_only_probe_validation_rules_recorded
        and dirty_state_validation_rules_recorded
        and timestamp_and_placeholder_rejection_rules_recorded
        and validation_execution_and_admission_still_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_521_528_summary_schema_matches": upstream_schema_matches,
        "section_521_528_summary_passed": upstream_summary_passed,
        "section_521_528_verification_evidence_payload_dry_run_ready": (
            upstream_payload_dry_run_ready
        ),
        "section_521_528_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "verification_evidence_validation_rule_dry_run_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "schema_validation_rules_recorded": schema_validation_rules_recorded,
        "identity_validation_rules_recorded": identity_validation_rules_recorded,
        "read_only_probe_validation_rules_recorded": (
            read_only_probe_validation_rules_recorded
        ),
        "dirty_state_validation_rules_recorded": dirty_state_validation_rules_recorded,
        "timestamp_and_placeholder_rejection_rules_recorded": (
            timestamp_and_placeholder_rejection_rules_recorded
        ),
        "validation_execution_and_admission_still_blocked": (
            validation_execution_and_admission_still_blocked
        ),
        "validation_rule_dry_run_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "validation_rule_dry_run_compile_save_write_outputs_blocked": (
            compile_save_write_outputs_blocked
        ),
        "result_has_no_error": result_has_no_error,
        "section_529_verification_evidence_validation_rule_dry_run_checkpoint_satisfied": (
            validation_rule_dry_run_ready
        ),
        "section_530_schema_validation_rules_recorded": (
            validation_rule_dry_run_ready
        ),
        "section_531_identity_validation_rules_recorded": (
            validation_rule_dry_run_ready
        ),
        "section_532_read_only_probe_validation_rules_recorded": (
            validation_rule_dry_run_ready
        ),
        "section_533_dirty_state_validation_rules_recorded": (
            validation_rule_dry_run_ready
        ),
        "section_534_timestamp_and_placeholder_rejection_rules_recorded": (
            validation_rule_dry_run_ready
        ),
        "section_535_validation_execution_and_admission_still_blocked": (
            validation_rule_dry_run_ready
        ),
        "section_536_validation_rule_dry_run_release_ready": (
            validation_rule_dry_run_ready
        ),
        "correct_workspace_bridge_verification_evidence_validation_rule_dry_run_ready": (
            validation_rule_dry_run_ready
        ),
        "verification_evidence_validation_not_executed": (
            validation_rule_dry_run_ready
        ),
        "final_durable_release_ready": validation_rule_dry_run_ready,
        **{
            key: 1 if validation_rule_dry_run_ready else 0
            for key in (
                CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_PATH_COUNT_KEYS
            )
        },
        **_blocked_output_counts(
            correct_workspace_bridge_verification_evidence_validation_rule_dry_run_result
        ),
    }


def summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "correct_workspace_bridge_verification_evidence_validation_rule_dry_run_ready",
            )
            == len(requested)
            and _truthy_count(
                requested, "verification_evidence_validation_not_executed"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_validation_rule_dry_run_batch_count": (
            len(requested)
        ),
        "section_521_528_summary_schema_matches_count": _truthy_count(
            requested, "section_521_528_summary_schema_matches"
        ),
        "section_521_528_summary_passed_count": _truthy_count(
            requested, "section_521_528_summary_passed"
        ),
        "section_521_528_verification_evidence_payload_dry_run_ready_count": (
            _truthy_count(
                requested,
                "section_521_528_verification_evidence_payload_dry_run_ready",
            )
        ),
        "section_521_528_outputs_closed_count": _truthy_count(
            requested, "section_521_528_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "verification_evidence_validation_rule_dry_run_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "verification_evidence_validation_rule_dry_run_checkpoint_satisfied",
            )
        ),
        "schema_validation_rules_recorded_count": _truthy_count(
            requested, "schema_validation_rules_recorded"
        ),
        "identity_validation_rules_recorded_count": _truthy_count(
            requested, "identity_validation_rules_recorded"
        ),
        "read_only_probe_validation_rules_recorded_count": _truthy_count(
            requested, "read_only_probe_validation_rules_recorded"
        ),
        "dirty_state_validation_rules_recorded_count": _truthy_count(
            requested, "dirty_state_validation_rules_recorded"
        ),
        "timestamp_and_placeholder_rejection_rules_recorded_count": _truthy_count(
            requested, "timestamp_and_placeholder_rejection_rules_recorded"
        ),
        "validation_execution_and_admission_still_blocked_count": _truthy_count(
            requested, "validation_execution_and_admission_still_blocked"
        ),
        "validation_rule_dry_run_no_write_boundary_verified_count": _truthy_count(
            requested, "validation_rule_dry_run_no_write_boundary_verified"
        ),
        "validation_rule_dry_run_compile_save_write_outputs_blocked_count": (
            _truthy_count(
                requested,
                "validation_rule_dry_run_compile_save_write_outputs_blocked",
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
                CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_PATH_COUNT_KEYS
            )
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in (
                BLOCKED_VERIFICATION_EVIDENCE_VALIDATION_RULE_DRY_RUN_OUTPUT_COUNT_KEYS
            )
        }
    )
    return summary
