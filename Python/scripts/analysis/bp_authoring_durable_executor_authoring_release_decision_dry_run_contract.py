#!/usr/bin/env python
"""
Section 174 durable executor authoring release decision dry-run contract.

This contract defines an offline release-decision dry-run gate after the Section
173 release review dry-run. It can admit only a release decision dry-run record.
It does not promote decision, start promotion barrier, mark final readiness, open
command paths, dispatch live commands, execute live commands, modify assets,
dirty packages, save, delete/rename, cleanup, change code, or probe live bridges.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

from bp_authoring_durable_executor_authoring_release_stage_dry_run_common import (
    ALLOWED_REQUESTED_COMMANDS,
    FORBIDDEN_REQUESTED_COMMANDS,
    build_release_stage_dry_run_contract,
    summarize_release_stage_dry_runs,
)


DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_DRY_RUN_SCHEMA = (
    "section_174_durable_executor_authoring_release_decision_dry_run_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_DRY_RUN_RECORD_SCHEMA = (
    "section_174_durable_executor_authoring_release_decision_dry_run_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_DRY_RUN_SUMMARY_SCHEMA = (
    "section_174_durable_executor_authoring_release_decision_dry_run_summary_v1"
)
EXPECTED_RELEASE_DECISION_SCOPE = "durable_executor_authoring_release_decision_dry_run_only"
ALLOWED_RELEASE_DECISION_DRY_RUN_OPERATIONS = (
    "validate_release_decision_envelope",
    "evaluate_release_decision_gate",
    "release_decision_dry_run_only",
)

OUTPUT_ACTION_KEYS = (
    "release_decision_dry_run_started",
    "release_decision_dry_run_accepted",
    "release_decision_dry_run_admissible",
    "durable_release_decision_promoted",
    "durable_release_decision_started",
    "durable_release_decision_accepted",
    "durable_release_promotion_barrier_started",
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
UNSAFE_RELEASE_DECISION_RECORD_ACTION_KEYS = tuple(
    key for key in OUTPUT_ACTION_KEYS if key != "release_decision_dry_run_admissible"
)
SECTION_173_ZERO_COUNT_KEYS = (
    "release_review_dry_run_started_count",
    "release_review_dry_run_accepted_count",
    "durable_release_review_promoted_count",
    "durable_release_review_started_count",
    "durable_release_review_accepted_count",
    "durable_release_decision_started_count",
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
    ("open_activation_promotion_readiness_chain_satisfied", "open_activation_promotion_readiness_chain_satisfied_count", "section_173_open_activation_promotion_readiness_chain_satisfied"),
    ("authoring_enable_chain_satisfied", "authoring_enable_chain_satisfied_count", "section_173_authoring_enable_chain_satisfied"),
    ("durable_release_readiness_chain_reconfirmed", "durable_release_readiness_chain_reconfirmed_count", "section_173_durable_release_readiness_chain_reconfirmed"),
    ("authoring_command_inputs_satisfied", "authoring_command_inputs_satisfied_count", "section_173_authoring_command_inputs_satisfied"),
    ("authoring_command_record_valid", "authoring_command_record_valid_count", "section_173_authoring_command_record_valid"),
    ("dry_run_route_record_valid", "dry_run_route_record_valid_count", "section_173_dry_run_route_record_valid"),
    ("dry_run_route_admissible", "dry_run_route_admissible_count", "section_173_dry_run_route_admissible"),
    ("dispatch_dry_run_record_valid", "dispatch_dry_run_record_valid_count", "section_173_dispatch_dry_run_record_valid"),
    ("dispatch_dry_run_admissible", "dispatch_dry_run_admissible_count", "section_173_dispatch_dry_run_admissible"),
    ("dispatch_evidence_dry_run_record_valid", "dispatch_evidence_dry_run_record_valid_count", "section_173_dispatch_evidence_dry_run_record_valid"),
    ("dispatch_evidence_dry_run_admissible", "dispatch_evidence_dry_run_admissible_count", "section_173_dispatch_evidence_dry_run_admissible"),
    ("execution_dry_run_record_valid", "execution_dry_run_record_valid_count", "section_173_execution_dry_run_record_valid"),
    ("execution_dry_run_admissible", "execution_dry_run_admissible_count", "section_173_execution_dry_run_admissible"),
    ("execution_evidence_dry_run_record_valid", "execution_evidence_dry_run_record_valid_count", "section_173_execution_evidence_dry_run_record_valid"),
    ("execution_evidence_dry_run_admissible", "execution_evidence_dry_run_admissible_count", "section_173_execution_evidence_dry_run_admissible"),
    ("completion_decision_dry_run_record_valid", "completion_decision_dry_run_record_valid_count", "section_173_completion_decision_dry_run_record_valid"),
    ("completion_decision_dry_run_admissible", "completion_decision_dry_run_admissible_count", "section_173_completion_decision_dry_run_admissible"),
    ("completion_application_dry_run_record_valid", "completion_application_dry_run_record_valid_count", "section_173_completion_application_dry_run_record_valid"),
    ("completion_application_dry_run_admissible", "completion_application_dry_run_admissible_count", "section_173_completion_application_dry_run_admissible"),
    ("completion_result_dry_run_record_valid", "completion_result_dry_run_record_valid_count", "section_173_completion_result_dry_run_record_valid"),
    ("completion_result_dry_run_admissible", "completion_result_dry_run_admissible_count", "section_173_completion_result_dry_run_admissible"),
    ("result_readback_dry_run_record_valid", "result_readback_dry_run_record_valid_count", "section_173_result_readback_dry_run_record_valid"),
    ("result_readback_dry_run_admissible", "result_readback_dry_run_admissible_count", "section_173_result_readback_dry_run_admissible"),
    ("final_no_save_release_dry_run_record_valid", "final_no_save_release_dry_run_record_valid_count", "section_173_final_no_save_release_dry_run_record_valid"),
    ("final_no_save_release_dry_run_admissible", "final_no_save_release_dry_run_admissible_count", "section_173_final_no_save_release_dry_run_admissible"),
    ("final_release_readiness_dry_run_record_valid", "final_release_readiness_dry_run_record_valid_count", "section_173_final_release_readiness_dry_run_record_valid"),
    ("final_release_readiness_dry_run_admissible", "final_release_readiness_dry_run_admissible_count", "section_173_final_release_readiness_dry_run_admissible"),
    ("release_review_dry_run_record_valid", "release_review_dry_run_record_valid_count", "section_173_release_review_dry_run_record_valid"),
    ("release_review_dry_run_admissible", "release_review_dry_run_admissible_count", "section_173_release_review_dry_run_admissible"),
)

REQUEST_COUNT_KEY = "durable_requested_executor_authoring_release_decision_dry_run_count"
CONTRACT_DEFINED_COUNT_KEY = "release_decision_contract_defined_count"
PREVIOUS_READY_COUNT_KEY = "section_173_release_review_contract_ready_count"
CHAIN_SATISFIED_COUNT_KEY = "release_review_chain_satisfied_count"
RECORD_SUMMARY_ZERO_COUNT_KEYS = (
    "release_decision_dry_run_record_present_count",
    "record_schema_matches_count",
    "release_decision_scope_matches_count",
    "dry_run_only_count",
    "release_decision_status_passed_count",
    "operator_reconfirmed_no_live_dispatch_count",
    "operator_reconfirmed_no_live_execution_count",
    "operator_reconfirmed_no_write_execution_count",
    "operator_reconfirmed_no_save_delete_rename_count",
    "requested_command_allowed_count",
    "requested_command_forbidden_count",
    "requested_command_unknown_count",
    "release_decision_operation_allowed_count",
    "release_decision_target_declared_count",
    "release_review_admission_proof_matches_count",
    "release_boundary_proof_safe_count",
    "release_decision_dry_run_record_valid_count",
    "release_decision_dry_run_record_rejected_count",
    "release_decision_dry_run_admissible_count",
    "unsafe_release_decision_record_count",
)
MISSING_PREREQUISITE_COUNT_KEY = "missing_release_decision_dry_run_prerequisite_count"
CURRENT_MISSING_PREREQUISITE_COUNT = 43
BLOCKED_WITH_RECORD_MISSING_PREREQUISITE_COUNT = 29

STAGE_SPEC = {
    "id": "durable_executor_authoring_release_decision_dry_run",
    "schema": DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_DRY_RUN_SCHEMA,
    "record_schema": DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_DRY_RUN_RECORD_SCHEMA,
    "summary_schema": DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_DRY_RUN_SUMMARY_SCHEMA,
    "expected_scope": EXPECTED_RELEASE_DECISION_SCOPE,
    "allowed_operations": ALLOWED_RELEASE_DECISION_DRY_RUN_OPERATIONS,
    "output_action_keys": OUTPUT_ACTION_KEYS,
    "unsafe_action_keys": UNSAFE_RELEASE_DECISION_RECORD_ACTION_KEYS,
    "previous_zero_count_keys": SECTION_173_ZERO_COUNT_KEYS,
    "chain_inputs": CHAIN_INPUTS,
    "previous_defined_count_key": "release_review_contract_defined_count",
    "previous_rejected_count_key": "release_review_dry_run_record_rejected_count",
    "previous_unsafe_count_key": "unsafe_release_review_record_count",
    "previous_ready_missing_key": "section_173_release_review_dry_run_contract_ready",
    "contract_defined_key": "release_decision_contract_defined",
    "required_record_schema_field": "required_release_decision_record_schema",
    "expected_scope_field": "expected_release_decision_scope",
    "allowed_operations_field": "allowed_release_decision_dry_run_operations",
    "previous_ready_key": "section_173_release_review_contract_ready",
    "chain_satisfied_key": "release_review_chain_satisfied",
    "record_present_key": "release_decision_dry_run_record_present",
    "scope_record_field": "release_decision_scope",
    "scope_matches_key": "release_decision_scope_matches",
    "status_passed_key": "release_decision_status_passed",
    "operation_record_field": "release_decision_operation",
    "operation_allowed_key": "release_decision_operation_allowed",
    "target_declared_key": "release_decision_target_declared",
    "admission_proof_group": "release_review_admission_proof",
    "admission_proof_matches_key": "release_review_admission_proof_matches",
    "record_valid_key": "release_decision_dry_run_record_valid",
    "record_rejected_key": "release_decision_dry_run_record_rejected",
    "admissible_key": "release_decision_dry_run_admissible",
    "unsafe_count_key": "unsafe_release_decision_record_count",
    "missing_prerequisites_key": "missing_release_decision_dry_run_prerequisites",
    "missing_count_key": MISSING_PREREQUISITE_COUNT_KEY,
    "record_present_missing_key": "release_decision_dry_run_record_present",
    "record_schema_missing_key": "release_decision_dry_run_record_schema",
    "scope_missing_key": "release_decision_dry_run_only_scope",
    "dry_run_only_missing_key": "release_decision_dry_run_only",
    "status_missing_key": "release_decision_dry_run_status_passed",
    "operation_missing_key": "allowed_release_decision_dry_run_operation",
    "target_missing_key": "release_decision_target_declared",
    "admission_proof_missing_key": "release_review_admission_proof_matches",
    "request_count_key": REQUEST_COUNT_KEY,
    "contract_defined_count_key": CONTRACT_DEFINED_COUNT_KEY,
    "previous_ready_count_key": PREVIOUS_READY_COUNT_KEY,
    "chain_satisfied_count_key": CHAIN_SATISFIED_COUNT_KEY,
    "record_present_count_key": "release_decision_dry_run_record_present_count",
    "scope_matches_count_key": "release_decision_scope_matches_count",
    "status_passed_count_key": "release_decision_status_passed_count",
    "operation_allowed_count_key": "release_decision_operation_allowed_count",
    "target_declared_count_key": "release_decision_target_declared_count",
    "admission_proof_matches_count_key": "release_review_admission_proof_matches_count",
    "record_valid_count_key": "release_decision_dry_run_record_valid_count",
    "record_rejected_count_key": "release_decision_dry_run_record_rejected_count",
    "admissible_count_key": "release_decision_dry_run_admissible_count",
}


def build_durable_executor_authoring_release_decision_dry_run_contract(
    requested: bool,
    section_173_release_review_dry_run_summary: Dict[str, Any],
    release_decision_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    return build_release_stage_dry_run_contract(
        STAGE_SPEC,
        requested,
        section_173_release_review_dry_run_summary,
        release_decision_record,
    )


def summarize_durable_executor_authoring_release_decision_dry_runs(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    return summarize_release_stage_dry_runs(STAGE_SPEC, contracts)
