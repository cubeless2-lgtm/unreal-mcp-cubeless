#!/usr/bin/env python
"""
Section 180 durable executor authoring command admission dry-run contract.

This contract defines an offline authoring-command-admission dry-run gate after
the Section 179 command path dry-run. It can admit only a command admission
dry-run record. It does not allow authoring commands, dispatch live commands,
execute live commands, modify assets, dirty packages, save, delete/rename,
cleanup, change code, or probe live bridges.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_command_path_dry_run_contract as command_path_dry_run
from bp_authoring_durable_executor_authoring_release_stage_dry_run_common import (
    build_release_stage_dry_run_contract,
    summarize_release_stage_dry_runs,
)


DURABLE_EXECUTOR_AUTHORING_COMMAND_ADMISSION_DRY_RUN_SCHEMA = (
    "section_180_durable_executor_authoring_command_admission_dry_run_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_ADMISSION_DRY_RUN_RECORD_SCHEMA = (
    "section_180_durable_executor_authoring_command_admission_dry_run_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_ADMISSION_DRY_RUN_SUMMARY_SCHEMA = (
    "section_180_durable_executor_authoring_command_admission_dry_run_summary_v1"
)
EXPECTED_COMMAND_ADMISSION_SCOPE = (
    "durable_executor_authoring_command_admission_dry_run_only"
)
ALLOWED_COMMAND_ADMISSION_DRY_RUN_OPERATIONS = (
    "validate_command_admission_envelope",
    "evaluate_command_admission_gate",
    "command_admission_dry_run_only",
)

OUTPUT_ACTION_KEYS = (
    "command_admission_dry_run_started",
    "command_admission_dry_run_accepted",
    "command_admission_dry_run_admissible",
    "durable_authoring_command_admission_promoted",
    "durable_authoring_command_contract_started",
    "durable_authoring_command_contract_accepted",
    "durable_authoring_command_allowed",
    "durable_authoring_command_dispatched",
    "durable_authoring_command_executed",
    "durable_authoring_command_completed",
    "durable_executor_command_path_opened",
    "durable_executor_command_path_allowed",
    "durable_executor_open_promotion_barrier_promoted",
    "durable_executor_open_promotion_barrier_started",
    "durable_executor_open_promotion_barrier_accepted",
    "durable_executor_open_contract_started",
    "durable_executor_open_contract_accepted",
    "durable_executor_open_performed",
    "durable_executor_activated",
    "durable_executor_opened",
    "durable_authoring_enable_started",
    "durable_activation_readiness_promoted",
    "durable_executor_activation_readiness_started",
    "durable_executor_activation_readiness_accepted",
    "durable_release_promotion_barrier_promoted",
    "durable_release_promotion_barrier_started",
    "durable_release_promotion_barrier_accepted",
    "durable_release_decision_promoted",
    "durable_release_decision_started",
    "durable_release_decision_accepted",
    "durable_release_review_promoted",
    "durable_release_review_started",
    "durable_release_review_accepted",
    "durable_final_release_readiness_promoted",
    "durable_final_release_readiness_started",
    "durable_final_release_ready",
    "durable_final_no_save_release_promoted",
    "durable_final_no_save_release_accepted",
    "durable_result_readback_promoted",
    "durable_result_readback_accepted",
    "durable_completion_result_promoted",
    "durable_completion_result_recorded",
    "durable_completion_application_promoted",
    "durable_completion_application_applied",
    "durable_completion_decision_promoted",
    "durable_execution_evidence_promoted",
    "durable_execution_envelope_promoted",
    "durable_evidence_promoted",
    "durable_dispatch_envelope_promoted",
    "durable_command_request_promoted",
    "durable_authoring_enabled",
    "durable_authoring_allowed",
    "final_durable_release_ready",
    "asset_write_performed",
    "package_dirty_marked",
    "code_change_performed",
    "executor_code_modified",
    "unreal_asset_modified",
    "live_bridge_probe_started",
    "save_delete_rename_allowed",
    "save_asset_allowed",
    "delete_asset_allowed",
    "rename_asset_allowed",
    "cleanup_allowed",
    "live_command_dispatched",
    "live_command_executed",
)
UNSAFE_COMMAND_ADMISSION_RECORD_ACTION_KEYS = tuple(
    key
    for key in OUTPUT_ACTION_KEYS
    if key != "command_admission_dry_run_admissible"
)
SECTION_179_ZERO_COUNT_KEYS = tuple(
    f"{key}_count"
    for key in command_path_dry_run.OUTPUT_ACTION_KEYS
    if key != "command_path_dry_run_admissible"
)
CHAIN_INPUTS = command_path_dry_run.CHAIN_INPUTS + (
    (
        "command_path_dry_run_record_valid",
        "command_path_dry_run_record_valid_count",
        "section_179_command_path_dry_run_record_valid",
    ),
    (
        "command_path_dry_run_admissible",
        "command_path_dry_run_admissible_count",
        "section_179_command_path_dry_run_admissible",
    ),
)

REQUEST_COUNT_KEY = "durable_requested_executor_authoring_command_admission_dry_run_count"
CONTRACT_DEFINED_COUNT_KEY = "command_admission_contract_defined_count"
PREVIOUS_READY_COUNT_KEY = "section_179_command_path_contract_ready_count"
CHAIN_SATISFIED_COUNT_KEY = "command_path_chain_satisfied_count"
RECORD_SUMMARY_ZERO_COUNT_KEYS = (
    "command_admission_dry_run_record_present_count",
    "record_schema_matches_count",
    "command_admission_scope_matches_count",
    "dry_run_only_count",
    "command_admission_status_passed_count",
    "operator_reconfirmed_no_live_dispatch_count",
    "operator_reconfirmed_no_live_execution_count",
    "operator_reconfirmed_no_write_execution_count",
    "operator_reconfirmed_no_save_delete_rename_count",
    "requested_command_allowed_count",
    "requested_command_forbidden_count",
    "requested_command_unknown_count",
    "command_admission_operation_allowed_count",
    "command_admission_target_declared_count",
    "command_path_admission_proof_matches_count",
    "release_boundary_proof_safe_count",
    "command_admission_dry_run_record_valid_count",
    "command_admission_dry_run_record_rejected_count",
    "command_admission_dry_run_admissible_count",
    "unsafe_command_admission_record_count",
)
MISSING_PREREQUISITE_COUNT_KEY = (
    "missing_command_admission_dry_run_prerequisite_count"
)
CURRENT_MISSING_PREREQUISITE_COUNT = len(CHAIN_INPUTS) + 14
BLOCKED_WITH_RECORD_MISSING_PREREQUISITE_COUNT = len(CHAIN_INPUTS)

STAGE_SPEC = {
    "id": "durable_executor_authoring_command_admission_dry_run",
    "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_ADMISSION_DRY_RUN_SCHEMA,
    "record_schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_ADMISSION_DRY_RUN_RECORD_SCHEMA,
    "summary_schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_ADMISSION_DRY_RUN_SUMMARY_SCHEMA,
    "expected_scope": EXPECTED_COMMAND_ADMISSION_SCOPE,
    "allowed_operations": ALLOWED_COMMAND_ADMISSION_DRY_RUN_OPERATIONS,
    "output_action_keys": OUTPUT_ACTION_KEYS,
    "unsafe_action_keys": UNSAFE_COMMAND_ADMISSION_RECORD_ACTION_KEYS,
    "previous_zero_count_keys": SECTION_179_ZERO_COUNT_KEYS,
    "chain_inputs": CHAIN_INPUTS,
    "previous_defined_count_key": "command_path_contract_defined_count",
    "previous_rejected_count_key": "command_path_dry_run_record_rejected_count",
    "previous_unsafe_count_key": "unsafe_command_path_record_count",
    "previous_ready_missing_key": "section_179_command_path_dry_run_contract_ready",
    "contract_defined_key": "command_admission_contract_defined",
    "required_record_schema_field": "required_command_admission_record_schema",
    "expected_scope_field": "expected_command_admission_scope",
    "allowed_operations_field": "allowed_command_admission_dry_run_operations",
    "previous_ready_key": "section_179_command_path_contract_ready",
    "chain_satisfied_key": "command_path_chain_satisfied",
    "record_present_key": "command_admission_dry_run_record_present",
    "scope_record_field": "command_admission_scope",
    "scope_matches_key": "command_admission_scope_matches",
    "status_passed_key": "command_admission_status_passed",
    "operation_record_field": "command_admission_operation",
    "operation_allowed_key": "command_admission_operation_allowed",
    "target_declared_key": "command_admission_target_declared",
    "admission_proof_group": "command_path_admission_proof",
    "admission_proof_matches_key": "command_path_admission_proof_matches",
    "record_valid_key": "command_admission_dry_run_record_valid",
    "record_rejected_key": "command_admission_dry_run_record_rejected",
    "admissible_key": "command_admission_dry_run_admissible",
    "unsafe_count_key": "unsafe_command_admission_record_count",
    "missing_prerequisites_key": "missing_command_admission_dry_run_prerequisites",
    "missing_count_key": MISSING_PREREQUISITE_COUNT_KEY,
    "record_present_missing_key": "command_admission_dry_run_record_present",
    "record_schema_missing_key": "command_admission_dry_run_record_schema",
    "scope_missing_key": "command_admission_dry_run_only_scope",
    "dry_run_only_missing_key": "command_admission_dry_run_only",
    "status_missing_key": "command_admission_dry_run_status_passed",
    "operation_missing_key": "allowed_command_admission_dry_run_operation",
    "target_missing_key": "command_admission_target_declared",
    "admission_proof_missing_key": "command_path_admission_proof_matches",
    "request_count_key": REQUEST_COUNT_KEY,
    "contract_defined_count_key": CONTRACT_DEFINED_COUNT_KEY,
    "previous_ready_count_key": PREVIOUS_READY_COUNT_KEY,
    "chain_satisfied_count_key": CHAIN_SATISFIED_COUNT_KEY,
    "record_present_count_key": "command_admission_dry_run_record_present_count",
    "scope_matches_count_key": "command_admission_scope_matches_count",
    "status_passed_count_key": "command_admission_status_passed_count",
    "operation_allowed_count_key": "command_admission_operation_allowed_count",
    "target_declared_count_key": "command_admission_target_declared_count",
    "admission_proof_matches_count_key": "command_path_admission_proof_matches_count",
    "record_valid_count_key": "command_admission_dry_run_record_valid_count",
    "record_rejected_count_key": "command_admission_dry_run_record_rejected_count",
    "admissible_count_key": "command_admission_dry_run_admissible_count",
}


def build_durable_executor_authoring_command_admission_dry_run_contract(
    requested: bool,
    section_179_command_path_dry_run_summary: Dict[str, Any],
    command_admission_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return build_release_stage_dry_run_contract(
        STAGE_SPEC,
        requested,
        section_179_command_path_dry_run_summary,
        command_admission_record,
    )


def summarize_durable_executor_authoring_command_admission_dry_runs(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    return summarize_release_stage_dry_runs(STAGE_SPEC, contracts)
