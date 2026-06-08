#!/usr/bin/env python
"""
Section 176 durable executor authoring activation readiness dry-run contract.

This contract defines an offline activation-readiness dry-run gate after the
Section 175 release promotion barrier dry-run. It can admit only an activation
readiness dry-run record. It does not promote readiness, start/open the executor,
enable durable authoring, dispatch live commands, execute live commands, modify
assets, dirty packages, save, delete/rename, cleanup, change code, or probe live
bridges.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

from bp_authoring_durable_executor_authoring_release_stage_dry_run_common import (
    ALLOWED_REQUESTED_COMMANDS,
    FORBIDDEN_REQUESTED_COMMANDS,
    build_release_stage_dry_run_contract,
    summarize_release_stage_dry_runs,
)


DURABLE_EXECUTOR_AUTHORING_ACTIVATION_READINESS_DRY_RUN_SCHEMA = (
    "section_176_durable_executor_authoring_activation_readiness_dry_run_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_ACTIVATION_READINESS_DRY_RUN_RECORD_SCHEMA = (
    "section_176_durable_executor_authoring_activation_readiness_dry_run_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_ACTIVATION_READINESS_DRY_RUN_SUMMARY_SCHEMA = (
    "section_176_durable_executor_authoring_activation_readiness_dry_run_summary_v1"
)
EXPECTED_ACTIVATION_READINESS_SCOPE = (
    "durable_executor_authoring_activation_readiness_dry_run_only"
)
ALLOWED_ACTIVATION_READINESS_DRY_RUN_OPERATIONS = (
    "validate_activation_readiness_envelope",
    "evaluate_activation_readiness_gate",
    "activation_readiness_dry_run_only",
)

OUTPUT_ACTION_KEYS = (
    "activation_readiness_dry_run_started",
    "activation_readiness_dry_run_accepted",
    "activation_readiness_dry_run_admissible",
    "durable_activation_readiness_promoted",
    "durable_executor_activation_readiness_started",
    "durable_executor_activation_readiness_accepted",
    "durable_executor_open_contract_started",
    "durable_executor_activated",
    "durable_executor_opened",
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
    "durable_executor_command_path_opened",
    "durable_executor_command_path_allowed",
    "durable_authoring_command_allowed",
    "durable_authoring_command_dispatched",
    "durable_authoring_command_executed",
    "durable_authoring_command_completed",
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
UNSAFE_ACTIVATION_READINESS_RECORD_ACTION_KEYS = tuple(
    key for key in OUTPUT_ACTION_KEYS if key != "activation_readiness_dry_run_admissible"
)
SECTION_175_ZERO_COUNT_KEYS = (
    "release_promotion_barrier_dry_run_started_count",
    "release_promotion_barrier_dry_run_accepted_count",
    "durable_release_promotion_barrier_promoted_count",
    "durable_release_promotion_barrier_started_count",
    "durable_release_promotion_barrier_accepted_count",
    "durable_executor_activation_readiness_started_count",
    "durable_executor_activated_count",
    "durable_executor_opened_count",
    "durable_release_decision_promoted_count",
    "durable_release_decision_started_count",
    "durable_release_decision_accepted_count",
    "durable_release_review_promoted_count",
    "durable_release_review_started_count",
    "durable_release_review_accepted_count",
    "durable_final_release_readiness_promoted_count",
    "durable_final_release_readiness_started_count",
    "durable_final_release_ready_count",
    "durable_final_no_save_release_promoted_count",
    "durable_final_no_save_release_accepted_count",
    "durable_result_readback_promoted_count",
    "durable_result_readback_accepted_count",
    "durable_completion_result_promoted_count",
    "durable_completion_result_recorded_count",
    "durable_completion_application_promoted_count",
    "durable_completion_application_applied_count",
    "durable_completion_decision_promoted_count",
    "durable_execution_evidence_promoted_count",
    "durable_execution_envelope_promoted_count",
    "durable_evidence_promoted_count",
    "durable_dispatch_envelope_promoted_count",
    "durable_command_request_promoted_count",
    "durable_executor_command_path_opened_count",
    "durable_executor_command_path_allowed_count",
    "durable_authoring_command_allowed_count",
    "durable_authoring_command_dispatched_count",
    "durable_authoring_command_executed_count",
    "durable_authoring_command_completed_count",
    "durable_authoring_enabled_count",
    "durable_authoring_allowed_count",
    "final_durable_release_ready_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
    "code_change_performed_count",
    "executor_code_modified_count",
    "unreal_asset_modified_count",
    "live_bridge_probe_started_count",
    "save_delete_rename_allowed_count",
    "save_asset_allowed_count",
    "delete_asset_allowed_count",
    "rename_asset_allowed_count",
    "cleanup_allowed_count",
    "live_command_dispatched_count",
    "live_command_executed_count",
)
CHAIN_INPUTS = (
    ("open_activation_promotion_readiness_chain_satisfied", "open_activation_promotion_readiness_chain_satisfied_count", "section_175_open_activation_promotion_readiness_chain_satisfied"),
    ("authoring_enable_chain_satisfied", "authoring_enable_chain_satisfied_count", "section_175_authoring_enable_chain_satisfied"),
    ("durable_release_readiness_chain_reconfirmed", "durable_release_readiness_chain_reconfirmed_count", "section_175_durable_release_readiness_chain_reconfirmed"),
    ("authoring_command_inputs_satisfied", "authoring_command_inputs_satisfied_count", "section_175_authoring_command_inputs_satisfied"),
    ("authoring_command_record_valid", "authoring_command_record_valid_count", "section_175_authoring_command_record_valid"),
    ("dry_run_route_record_valid", "dry_run_route_record_valid_count", "section_175_dry_run_route_record_valid"),
    ("dry_run_route_admissible", "dry_run_route_admissible_count", "section_175_dry_run_route_admissible"),
    ("dispatch_dry_run_record_valid", "dispatch_dry_run_record_valid_count", "section_175_dispatch_dry_run_record_valid"),
    ("dispatch_dry_run_admissible", "dispatch_dry_run_admissible_count", "section_175_dispatch_dry_run_admissible"),
    ("dispatch_evidence_dry_run_record_valid", "dispatch_evidence_dry_run_record_valid_count", "section_175_dispatch_evidence_dry_run_record_valid"),
    ("dispatch_evidence_dry_run_admissible", "dispatch_evidence_dry_run_admissible_count", "section_175_dispatch_evidence_dry_run_admissible"),
    ("execution_dry_run_record_valid", "execution_dry_run_record_valid_count", "section_175_execution_dry_run_record_valid"),
    ("execution_dry_run_admissible", "execution_dry_run_admissible_count", "section_175_execution_dry_run_admissible"),
    ("execution_evidence_dry_run_record_valid", "execution_evidence_dry_run_record_valid_count", "section_175_execution_evidence_dry_run_record_valid"),
    ("execution_evidence_dry_run_admissible", "execution_evidence_dry_run_admissible_count", "section_175_execution_evidence_dry_run_admissible"),
    ("completion_decision_dry_run_record_valid", "completion_decision_dry_run_record_valid_count", "section_175_completion_decision_dry_run_record_valid"),
    ("completion_decision_dry_run_admissible", "completion_decision_dry_run_admissible_count", "section_175_completion_decision_dry_run_admissible"),
    ("completion_application_dry_run_record_valid", "completion_application_dry_run_record_valid_count", "section_175_completion_application_dry_run_record_valid"),
    ("completion_application_dry_run_admissible", "completion_application_dry_run_admissible_count", "section_175_completion_application_dry_run_admissible"),
    ("completion_result_dry_run_record_valid", "completion_result_dry_run_record_valid_count", "section_175_completion_result_dry_run_record_valid"),
    ("completion_result_dry_run_admissible", "completion_result_dry_run_admissible_count", "section_175_completion_result_dry_run_admissible"),
    ("result_readback_dry_run_record_valid", "result_readback_dry_run_record_valid_count", "section_175_result_readback_dry_run_record_valid"),
    ("result_readback_dry_run_admissible", "result_readback_dry_run_admissible_count", "section_175_result_readback_dry_run_admissible"),
    ("final_no_save_release_dry_run_record_valid", "final_no_save_release_dry_run_record_valid_count", "section_175_final_no_save_release_dry_run_record_valid"),
    ("final_no_save_release_dry_run_admissible", "final_no_save_release_dry_run_admissible_count", "section_175_final_no_save_release_dry_run_admissible"),
    ("final_release_readiness_dry_run_record_valid", "final_release_readiness_dry_run_record_valid_count", "section_175_final_release_readiness_dry_run_record_valid"),
    ("final_release_readiness_dry_run_admissible", "final_release_readiness_dry_run_admissible_count", "section_175_final_release_readiness_dry_run_admissible"),
    ("release_review_dry_run_record_valid", "release_review_dry_run_record_valid_count", "section_175_release_review_dry_run_record_valid"),
    ("release_review_dry_run_admissible", "release_review_dry_run_admissible_count", "section_175_release_review_dry_run_admissible"),
    ("release_decision_dry_run_record_valid", "release_decision_dry_run_record_valid_count", "section_175_release_decision_dry_run_record_valid"),
    ("release_decision_dry_run_admissible", "release_decision_dry_run_admissible_count", "section_175_release_decision_dry_run_admissible"),
    ("release_promotion_barrier_dry_run_record_valid", "release_promotion_barrier_dry_run_record_valid_count", "section_175_release_promotion_barrier_dry_run_record_valid"),
    ("release_promotion_barrier_dry_run_admissible", "release_promotion_barrier_dry_run_admissible_count", "section_175_release_promotion_barrier_dry_run_admissible"),
)

REQUEST_COUNT_KEY = "durable_requested_executor_authoring_activation_readiness_dry_run_count"
CONTRACT_DEFINED_COUNT_KEY = "activation_readiness_contract_defined_count"
PREVIOUS_READY_COUNT_KEY = "section_175_release_promotion_barrier_contract_ready_count"
CHAIN_SATISFIED_COUNT_KEY = "release_promotion_barrier_chain_satisfied_count"
RECORD_SUMMARY_ZERO_COUNT_KEYS = (
    "activation_readiness_dry_run_record_present_count",
    "record_schema_matches_count",
    "activation_readiness_scope_matches_count",
    "dry_run_only_count",
    "activation_readiness_status_passed_count",
    "operator_reconfirmed_no_live_dispatch_count",
    "operator_reconfirmed_no_live_execution_count",
    "operator_reconfirmed_no_write_execution_count",
    "operator_reconfirmed_no_save_delete_rename_count",
    "requested_command_allowed_count",
    "requested_command_forbidden_count",
    "requested_command_unknown_count",
    "activation_readiness_operation_allowed_count",
    "activation_readiness_target_declared_count",
    "release_promotion_barrier_admission_proof_matches_count",
    "release_boundary_proof_safe_count",
    "activation_readiness_dry_run_record_valid_count",
    "activation_readiness_dry_run_record_rejected_count",
    "activation_readiness_dry_run_admissible_count",
    "unsafe_activation_readiness_record_count",
)
MISSING_PREREQUISITE_COUNT_KEY = "missing_activation_readiness_dry_run_prerequisite_count"
CURRENT_MISSING_PREREQUISITE_COUNT = 47
BLOCKED_WITH_RECORD_MISSING_PREREQUISITE_COUNT = 33

STAGE_SPEC = {
    "id": "durable_executor_authoring_activation_readiness_dry_run",
    "schema": DURABLE_EXECUTOR_AUTHORING_ACTIVATION_READINESS_DRY_RUN_SCHEMA,
    "record_schema": DURABLE_EXECUTOR_AUTHORING_ACTIVATION_READINESS_DRY_RUN_RECORD_SCHEMA,
    "summary_schema": DURABLE_EXECUTOR_AUTHORING_ACTIVATION_READINESS_DRY_RUN_SUMMARY_SCHEMA,
    "expected_scope": EXPECTED_ACTIVATION_READINESS_SCOPE,
    "allowed_operations": ALLOWED_ACTIVATION_READINESS_DRY_RUN_OPERATIONS,
    "output_action_keys": OUTPUT_ACTION_KEYS,
    "unsafe_action_keys": UNSAFE_ACTIVATION_READINESS_RECORD_ACTION_KEYS,
    "previous_zero_count_keys": SECTION_175_ZERO_COUNT_KEYS,
    "chain_inputs": CHAIN_INPUTS,
    "previous_defined_count_key": "release_promotion_barrier_contract_defined_count",
    "previous_rejected_count_key": "release_promotion_barrier_dry_run_record_rejected_count",
    "previous_unsafe_count_key": "unsafe_release_promotion_barrier_record_count",
    "previous_ready_missing_key": "section_175_release_promotion_barrier_dry_run_contract_ready",
    "contract_defined_key": "activation_readiness_contract_defined",
    "required_record_schema_field": "required_activation_readiness_record_schema",
    "expected_scope_field": "expected_activation_readiness_scope",
    "allowed_operations_field": "allowed_activation_readiness_dry_run_operations",
    "previous_ready_key": "section_175_release_promotion_barrier_contract_ready",
    "chain_satisfied_key": "release_promotion_barrier_chain_satisfied",
    "record_present_key": "activation_readiness_dry_run_record_present",
    "scope_record_field": "activation_readiness_scope",
    "scope_matches_key": "activation_readiness_scope_matches",
    "status_passed_key": "activation_readiness_status_passed",
    "operation_record_field": "activation_readiness_operation",
    "operation_allowed_key": "activation_readiness_operation_allowed",
    "target_declared_key": "activation_readiness_target_declared",
    "admission_proof_group": "release_promotion_barrier_admission_proof",
    "admission_proof_matches_key": "release_promotion_barrier_admission_proof_matches",
    "record_valid_key": "activation_readiness_dry_run_record_valid",
    "record_rejected_key": "activation_readiness_dry_run_record_rejected",
    "admissible_key": "activation_readiness_dry_run_admissible",
    "unsafe_count_key": "unsafe_activation_readiness_record_count",
    "missing_prerequisites_key": "missing_activation_readiness_dry_run_prerequisites",
    "missing_count_key": MISSING_PREREQUISITE_COUNT_KEY,
    "record_present_missing_key": "activation_readiness_dry_run_record_present",
    "record_schema_missing_key": "activation_readiness_dry_run_record_schema",
    "scope_missing_key": "activation_readiness_dry_run_only_scope",
    "dry_run_only_missing_key": "activation_readiness_dry_run_only",
    "status_missing_key": "activation_readiness_dry_run_status_passed",
    "operation_missing_key": "allowed_activation_readiness_dry_run_operation",
    "target_missing_key": "activation_readiness_target_declared",
    "admission_proof_missing_key": "release_promotion_barrier_admission_proof_matches",
    "request_count_key": REQUEST_COUNT_KEY,
    "contract_defined_count_key": CONTRACT_DEFINED_COUNT_KEY,
    "previous_ready_count_key": PREVIOUS_READY_COUNT_KEY,
    "chain_satisfied_count_key": CHAIN_SATISFIED_COUNT_KEY,
    "record_present_count_key": "activation_readiness_dry_run_record_present_count",
    "scope_matches_count_key": "activation_readiness_scope_matches_count",
    "status_passed_count_key": "activation_readiness_status_passed_count",
    "operation_allowed_count_key": "activation_readiness_operation_allowed_count",
    "target_declared_count_key": "activation_readiness_target_declared_count",
    "admission_proof_matches_count_key": "release_promotion_barrier_admission_proof_matches_count",
    "record_valid_count_key": "activation_readiness_dry_run_record_valid_count",
    "record_rejected_count_key": "activation_readiness_dry_run_record_rejected_count",
    "admissible_count_key": "activation_readiness_dry_run_admissible_count",
}


def build_durable_executor_authoring_activation_readiness_dry_run_contract(
    requested: bool,
    section_175_release_promotion_barrier_dry_run_summary: Dict[str, Any],
    activation_readiness_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return build_release_stage_dry_run_contract(
        STAGE_SPEC,
        requested,
        section_175_release_promotion_barrier_dry_run_summary,
        activation_readiness_record,
    )


def summarize_durable_executor_authoring_activation_readiness_dry_runs(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    return summarize_release_stage_dry_runs(STAGE_SPEC, contracts)
