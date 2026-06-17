#!/usr/bin/env python
"""
Sections 521-528 durable executor bridge verification evidence payload dry-run.

This contract follows the verification evidence schema gate. It records the
placeholder payload template and negative fixture matrix for a future
correct-workspace bridge proof while keeping payload ingest, schema validation
execution, verification admission, durable authoring dispatch, compile, save,
delete, rename, overwrite, cleanup, and production writes closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_correct_workspace_bridge_verification_evidence_schema_batch_contract as evidence_schema


DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_BATCH_SCHEMA = (
    "section_521_528_durable_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_BATCH_SUMMARY_SCHEMA = (
    "section_521_528_durable_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batch_summary_v1"
)
CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_RESULT_SCHEMA = (
    "section_521_528_correct_workspace_bridge_verification_evidence_payload_dry_run_result_v1"
)
SECTION_513_520_VERIFICATION_EVIDENCE_SCHEMA_SUMMARY_SCHEMA = (
    evidence_schema
    .DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_SCHEMA_BATCH_SUMMARY_SCHEMA
)

DEFAULT_PROJECT_FILE_PATH = evidence_schema.DEFAULT_PROJECT_FILE_PATH
DEFAULT_BRIDGE_HOST = evidence_schema.DEFAULT_BRIDGE_HOST
DEFAULT_BRIDGE_PORT = evidence_schema.DEFAULT_BRIDGE_PORT
DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH = (
    evidence_schema.DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH
)
DEFAULT_EDITOR_EXECUTABLE_PATH = evidence_schema.DEFAULT_EDITOR_EXECUTABLE_PATH
DEFAULT_MCP_SERVER_COMMAND = evidence_schema.DEFAULT_MCP_SERVER_COMMAND
DEFAULT_REQUIRED_EVIDENCE_FIELDS = evidence_schema.DEFAULT_REQUIRED_EVIDENCE_FIELDS
PLACEHOLDER_READ_ONLY_PROBE_RESULT = "__requires_actual_read_only_probe_result__"
PLACEHOLDER_NO_DIRTY_CONTENT_BEFORE = "__requires_actual_no_dirty_content_before__"
PLACEHOLDER_NO_DIRTY_CONTENT_AFTER = "__requires_actual_no_dirty_content_after__"
PLACEHOLDER_TIMESTAMP_UTC = "__requires_actual_utc_timestamp__"
DEFAULT_REJECTION_FIXTURE_NAMES = (
    "missing_project_file_path",
    "wrong_project_file_path",
    "wrong_bridge_port",
    "missing_read_only_probe_result",
    "dirty_state_after",
    "stale_timestamp_utc",
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_schema_batch_count",
    "section_505_512_summary_schema_matches_count",
    "section_505_512_summary_passed_count",
    "section_505_512_post_takeover_verification_admission_ready_count",
    "section_505_512_outputs_closed_count",
    "result_schema_matches_count",
    "verification_evidence_schema_checkpoint_satisfied_count",
    "required_evidence_fields_recorded_count",
    "project_identity_evidence_requirements_recorded_count",
    "bridge_identity_evidence_requirements_recorded_count",
    "read_only_probe_evidence_requirements_recorded_count",
    "evidence_ingest_and_admission_blocked_count",
    "verification_evidence_schema_no_write_boundary_verified_count",
    "verification_evidence_schema_compile_save_write_outputs_blocked_count",
    "result_has_no_error_count",
    "final_durable_release_ready_count",
    *evidence_schema.CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_SCHEMA_PATH_COUNT_KEYS,
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    evidence_schema.BLOCKED_VERIFICATION_EVIDENCE_SCHEMA_OUTPUT_COUNT_KEYS
)

CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_PATH_COUNT_KEYS = (
    "section_521_verification_evidence_payload_dry_run_checkpoint_satisfied_count",
    "section_522_payload_template_fields_mapped_count",
    "section_523_payload_identity_expectations_bound_count",
    "section_524_payload_dirty_state_placeholders_recorded_count",
    "section_525_rejection_fixture_matrix_recorded_count",
    "section_526_payload_ingest_and_admission_still_blocked_count",
    "section_527_payload_dry_run_no_write_boundary_verified_count",
    "section_528_payload_dry_run_release_ready_count",
    "correct_workspace_bridge_verification_evidence_payload_dry_run_ready_count",
    "verification_evidence_payload_not_ingested_count",
)
BLOCKED_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_OUTPUT_COUNT_KEYS = (
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
BLOCKED_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_RESULT_KEYS = tuple(
    key.removesuffix("_count")
    for key in BLOCKED_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_OUTPUT_COUNT_KEYS
)


def default_payload_template() -> Dict[str, Any]:
    return {
        "project_file_path": DEFAULT_PROJECT_FILE_PATH,
        "editor_executable_path": DEFAULT_EDITOR_EXECUTABLE_PATH,
        "bridge_host": DEFAULT_BRIDGE_HOST,
        "bridge_port": DEFAULT_BRIDGE_PORT,
        "mcp_server_command": DEFAULT_MCP_SERVER_COMMAND,
        "read_only_probe_result": PLACEHOLDER_READ_ONLY_PROBE_RESULT,
        "no_dirty_content_before": PLACEHOLDER_NO_DIRTY_CONTENT_BEFORE,
        "no_dirty_content_after": PLACEHOLDER_NO_DIRTY_CONTENT_AFTER,
        "timestamp_utc": PLACEHOLDER_TIMESTAMP_UTC,
    }


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
            BLOCKED_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_OUTPUT_COUNT_KEYS,
            BLOCKED_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_RESULT_KEYS,
        )
    }


def build_correct_workspace_bridge_verification_evidence_payload_dry_run_result(
    *,
    payload_template: Dict[str, Any] | None = None,
    rejection_fixture_names: Sequence[str] = DEFAULT_REJECTION_FIXTURE_NAMES,
    payload_template_created: bool = True,
    payload_template_is_placeholder_only: bool = True,
    payload_required_fields_mapped: bool = True,
    payload_identity_expectations_bound: bool = True,
    payload_dirty_state_placeholders_recorded: bool = True,
    rejection_fixture_matrix_recorded: bool = True,
    wrong_workspace_fixture_recorded: bool = True,
    stale_timestamp_fixture_recorded: bool = True,
    dirty_state_fixture_recorded: bool = True,
    missing_probe_fixture_recorded: bool = True,
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
        "schema": CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_RESULT_SCHEMA,
        "payload_template": payload_template or default_payload_template(),
        "required_evidence_fields": list(DEFAULT_REQUIRED_EVIDENCE_FIELDS),
        "rejection_fixture_names": list(rejection_fixture_names),
        "payload_template_created": payload_template_created,
        "payload_template_is_placeholder_only": payload_template_is_placeholder_only,
        "payload_required_fields_mapped": payload_required_fields_mapped,
        "payload_identity_expectations_bound": payload_identity_expectations_bound,
        "payload_dirty_state_placeholders_recorded": (
            payload_dirty_state_placeholders_recorded
        ),
        "rejection_fixture_matrix_recorded": rejection_fixture_matrix_recorded,
        "wrong_workspace_fixture_recorded": wrong_workspace_fixture_recorded,
        "stale_timestamp_fixture_recorded": stale_timestamp_fixture_recorded,
        "dirty_state_fixture_recorded": dirty_state_fixture_recorded,
        "missing_probe_fixture_recorded": missing_probe_fixture_recorded,
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


def build_durable_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batch_contract(
    requested: bool,
    section_513_520_verification_evidence_schema_summary: Dict[str, Any],
    correct_workspace_bridge_verification_evidence_payload_dry_run_result: Dict[str, Any],
) -> Dict[str, Any]:
    upstream_schema_matches = bool(
        section_513_520_verification_evidence_schema_summary.get("schema")
        == SECTION_513_520_VERIFICATION_EVIDENCE_SCHEMA_SUMMARY_SCHEMA
    )
    upstream_summary_passed = bool(
        section_513_520_verification_evidence_schema_summary.get("status")
        == "passed"
    )
    upstream_schema_ready = all(
        _count_is_one(section_513_520_verification_evidence_schema_summary, key)
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(section_513_520_verification_evidence_schema_summary, key)
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "schema"
        )
        == CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and upstream_schema_matches
        and upstream_summary_passed
        and upstream_schema_ready
        and upstream_outputs_closed
    )
    payload_template = (
        correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "payload_template", {}
        )
    )
    payload_template_fields_mapped = bool(
        correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "payload_template_created"
        )
        and correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "payload_template_is_placeholder_only"
        )
        and correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "payload_required_fields_mapped"
        )
        and tuple(payload_template.keys()) == DEFAULT_REQUIRED_EVIDENCE_FIELDS
        and tuple(
            correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
                "required_evidence_fields", ()
            )
        )
        == DEFAULT_REQUIRED_EVIDENCE_FIELDS
    )
    payload_identity_expectations_bound = bool(
        correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "payload_identity_expectations_bound"
        )
        and payload_template.get("project_file_path") == DEFAULT_PROJECT_FILE_PATH
        and payload_template.get("editor_executable_path")
        == DEFAULT_EDITOR_EXECUTABLE_PATH
        and payload_template.get("bridge_host") == DEFAULT_BRIDGE_HOST
        and payload_template.get("bridge_port") == DEFAULT_BRIDGE_PORT
        and payload_template.get("mcp_server_command") == DEFAULT_MCP_SERVER_COMMAND
    )
    payload_dirty_state_placeholders_recorded = bool(
        correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "payload_dirty_state_placeholders_recorded"
        )
        and payload_template.get("read_only_probe_result")
        == PLACEHOLDER_READ_ONLY_PROBE_RESULT
        and payload_template.get("no_dirty_content_before")
        == PLACEHOLDER_NO_DIRTY_CONTENT_BEFORE
        and payload_template.get("no_dirty_content_after")
        == PLACEHOLDER_NO_DIRTY_CONTENT_AFTER
        and payload_template.get("timestamp_utc") == PLACEHOLDER_TIMESTAMP_UTC
    )
    rejection_fixture_matrix_recorded = bool(
        correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "rejection_fixture_matrix_recorded"
        )
        and set(
            correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
                "rejection_fixture_names", ()
            )
        )
        >= set(DEFAULT_REJECTION_FIXTURE_NAMES)
        and correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "wrong_workspace_fixture_recorded"
        )
        and correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "stale_timestamp_fixture_recorded"
        )
        and correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "dirty_state_fixture_recorded"
        )
        and correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "missing_probe_fixture_recorded"
        )
    )
    payload_ingest_and_admission_still_blocked = bool(
        not correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "payload_ingest_allowed"
        )
        and not correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "evidence_schema_validation_allowed"
        )
        and not correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "verification_result_admission_allowed"
        )
        and all(
            not correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
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
        not correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
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
        not correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
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
        not correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            key
        )
        for key in BLOCKED_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        all_outputs_blocked
        and live_authoring_blocked
        and compile_save_write_outputs_blocked
        and correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "dirty_content_before"
        )
        == correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "dirty_content_after"
        )
        and correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "dirty_maps_before"
        )
        == correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "dirty_maps_after"
        )
        and not correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "dirty_content_after"
        )
        and not correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "dirty_maps_after"
        )
        and correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        correct_workspace_bridge_verification_evidence_payload_dry_run_result.get(
            "error"
        )
        in (None, "")
    )
    payload_dry_run_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and payload_template_fields_mapped
        and payload_identity_expectations_bound
        and payload_dirty_state_placeholders_recorded
        and rejection_fixture_matrix_recorded
        and payload_ingest_and_admission_still_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_513_520_summary_schema_matches": upstream_schema_matches,
        "section_513_520_summary_passed": upstream_summary_passed,
        "section_513_520_verification_evidence_schema_ready": (
            upstream_schema_ready
        ),
        "section_513_520_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "verification_evidence_payload_dry_run_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "payload_template_fields_mapped": payload_template_fields_mapped,
        "payload_identity_expectations_bound": payload_identity_expectations_bound,
        "payload_dirty_state_placeholders_recorded": (
            payload_dirty_state_placeholders_recorded
        ),
        "rejection_fixture_matrix_recorded": rejection_fixture_matrix_recorded,
        "payload_ingest_and_admission_still_blocked": (
            payload_ingest_and_admission_still_blocked
        ),
        "payload_dry_run_no_write_boundary_verified": no_write_boundary_verified,
        "payload_dry_run_compile_save_write_outputs_blocked": (
            compile_save_write_outputs_blocked
        ),
        "result_has_no_error": result_has_no_error,
        "section_521_verification_evidence_payload_dry_run_checkpoint_satisfied": (
            payload_dry_run_ready
        ),
        "section_522_payload_template_fields_mapped": payload_dry_run_ready,
        "section_523_payload_identity_expectations_bound": (
            payload_dry_run_ready
        ),
        "section_524_payload_dirty_state_placeholders_recorded": (
            payload_dry_run_ready
        ),
        "section_525_rejection_fixture_matrix_recorded": payload_dry_run_ready,
        "section_526_payload_ingest_and_admission_still_blocked": (
            payload_dry_run_ready
        ),
        "section_527_payload_dry_run_no_write_boundary_verified": (
            payload_dry_run_ready
        ),
        "section_528_payload_dry_run_release_ready": payload_dry_run_ready,
        "correct_workspace_bridge_verification_evidence_payload_dry_run_ready": (
            payload_dry_run_ready
        ),
        "verification_evidence_payload_not_ingested": payload_dry_run_ready,
        "final_durable_release_ready": payload_dry_run_ready,
        **{
            key: 1 if payload_dry_run_ready else 0
            for key in (
                CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_PATH_COUNT_KEYS
            )
        },
        **_blocked_output_counts(
            correct_workspace_bridge_verification_evidence_payload_dry_run_result
        ),
    }


def summarize_durable_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "correct_workspace_bridge_verification_evidence_payload_dry_run_ready",
            )
            == len(requested)
            and _truthy_count(
                requested, "verification_evidence_payload_not_ingested"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_correct_workspace_bridge_verification_evidence_payload_dry_run_batch_count": (
            len(requested)
        ),
        "section_513_520_summary_schema_matches_count": _truthy_count(
            requested, "section_513_520_summary_schema_matches"
        ),
        "section_513_520_summary_passed_count": _truthy_count(
            requested, "section_513_520_summary_passed"
        ),
        "section_513_520_verification_evidence_schema_ready_count": (
            _truthy_count(
                requested,
                "section_513_520_verification_evidence_schema_ready",
            )
        ),
        "section_513_520_outputs_closed_count": _truthy_count(
            requested, "section_513_520_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "verification_evidence_payload_dry_run_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "verification_evidence_payload_dry_run_checkpoint_satisfied",
            )
        ),
        "payload_template_fields_mapped_count": _truthy_count(
            requested, "payload_template_fields_mapped"
        ),
        "payload_identity_expectations_bound_count": _truthy_count(
            requested, "payload_identity_expectations_bound"
        ),
        "payload_dirty_state_placeholders_recorded_count": _truthy_count(
            requested, "payload_dirty_state_placeholders_recorded"
        ),
        "rejection_fixture_matrix_recorded_count": _truthy_count(
            requested, "rejection_fixture_matrix_recorded"
        ),
        "payload_ingest_and_admission_still_blocked_count": _truthy_count(
            requested, "payload_ingest_and_admission_still_blocked"
        ),
        "payload_dry_run_no_write_boundary_verified_count": _truthy_count(
            requested, "payload_dry_run_no_write_boundary_verified"
        ),
        "payload_dry_run_compile_save_write_outputs_blocked_count": (
            _truthy_count(
                requested,
                "payload_dry_run_compile_save_write_outputs_blocked",
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
                CORRECT_WORKSPACE_BRIDGE_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_PATH_COUNT_KEYS
            )
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in (
                BLOCKED_VERIFICATION_EVIDENCE_PAYLOAD_DRY_RUN_OUTPUT_COUNT_KEYS
            )
        }
    )
    return summary
