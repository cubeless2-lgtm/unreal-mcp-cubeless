#!/usr/bin/env python
"""
Section 171 durable executor authoring final no-save release dry-run contract.

This contract defines an offline final no-save release dry-run gate after the
Section 170 result readback dry-run. It can admit only a final no-save release
dry-run record. It does not promote final release, accept no-save release,
mark final readiness, open command paths, dispatch live commands, execute live
commands, modify assets, dirty packages, save, delete/rename, cleanup, change
code, or probe live bridges.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_DRY_RUN_SCHEMA = (
    "section_171_durable_executor_authoring_final_no_save_release_dry_run_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_DRY_RUN_RECORD_SCHEMA = (
    "section_171_durable_executor_authoring_final_no_save_release_dry_run_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_DRY_RUN_SUMMARY_SCHEMA = (
    "section_171_durable_executor_authoring_final_no_save_release_dry_run_summary_v1"
)
EXPECTED_FINAL_NO_SAVE_RELEASE_SCOPE = (
    "durable_executor_authoring_final_no_save_release_dry_run_only"
)

ALLOWED_FINAL_NO_SAVE_RELEASE_DRY_RUN_OPERATIONS = (
    "validate_final_no_save_release_envelope",
    "evaluate_final_no_save_release_readiness",
    "final_no_save_release_dry_run_only",
)
ALLOWED_REQUESTED_COMMANDS = (
    "create_blueprint_asset",
    "compile_and_validate_blueprint",
    "write_executor_ownership_marker",
    "readback_executor_ownership_marker",
    "read_only_asset_exists_check",
)
FORBIDDEN_REQUESTED_COMMANDS = (
    "compile_and_validate_blueprint(save=true)",
    "compile_and_save_blueprint",
    "save=true",
    "save_true",
    "save_asset",
    "delete_asset",
    "rename_asset",
    "duplicate_asset",
    "replace_existing_asset",
    "cleanup_asset",
    "general_durable_authoring",
    "live_command_dispatch",
    "live_command_execution",
)

OUTPUT_ACTION_KEYS = (
    "final_no_save_release_dry_run_started",
    "final_no_save_release_dry_run_accepted",
    "final_no_save_release_dry_run_admissible",
    "durable_final_no_save_release_promoted",
    "durable_final_no_save_release_accepted",
    "durable_final_release_readiness_started",
    "durable_final_release_ready",
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
UNSAFE_FINAL_NO_SAVE_RELEASE_RECORD_ACTION_KEYS = (
    "durable_final_no_save_release_promoted",
    "durable_final_no_save_release_accepted",
    "durable_final_release_readiness_started",
    "durable_final_release_ready",
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
SECTION_170_ZERO_COUNT_KEYS = (
    "result_readback_dry_run_started_count",
    "result_readback_dry_run_accepted_count",
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
    (
        "open_activation_promotion_readiness_chain_satisfied",
        "open_activation_promotion_readiness_chain_satisfied_count",
        "section_170_open_activation_promotion_readiness_chain_satisfied",
    ),
    (
        "authoring_enable_chain_satisfied",
        "authoring_enable_chain_satisfied_count",
        "section_170_authoring_enable_chain_satisfied",
    ),
    (
        "durable_release_readiness_chain_reconfirmed",
        "durable_release_readiness_chain_reconfirmed_count",
        "section_170_durable_release_readiness_chain_reconfirmed",
    ),
    (
        "authoring_command_inputs_satisfied",
        "authoring_command_inputs_satisfied_count",
        "section_170_authoring_command_inputs_satisfied",
    ),
    (
        "authoring_command_record_valid",
        "authoring_command_record_valid_count",
        "section_170_authoring_command_record_valid",
    ),
    (
        "dry_run_route_record_valid",
        "dry_run_route_record_valid_count",
        "section_170_dry_run_route_record_valid",
    ),
    (
        "dry_run_route_admissible",
        "dry_run_route_admissible_count",
        "section_170_dry_run_route_admissible",
    ),
    (
        "dispatch_dry_run_record_valid",
        "dispatch_dry_run_record_valid_count",
        "section_170_dispatch_dry_run_record_valid",
    ),
    (
        "dispatch_dry_run_admissible",
        "dispatch_dry_run_admissible_count",
        "section_170_dispatch_dry_run_admissible",
    ),
    (
        "dispatch_evidence_dry_run_record_valid",
        "dispatch_evidence_dry_run_record_valid_count",
        "section_170_dispatch_evidence_dry_run_record_valid",
    ),
    (
        "dispatch_evidence_dry_run_admissible",
        "dispatch_evidence_dry_run_admissible_count",
        "section_170_dispatch_evidence_dry_run_admissible",
    ),
    (
        "execution_dry_run_record_valid",
        "execution_dry_run_record_valid_count",
        "section_170_execution_dry_run_record_valid",
    ),
    (
        "execution_dry_run_admissible",
        "execution_dry_run_admissible_count",
        "section_170_execution_dry_run_admissible",
    ),
    (
        "execution_evidence_dry_run_record_valid",
        "execution_evidence_dry_run_record_valid_count",
        "section_170_execution_evidence_dry_run_record_valid",
    ),
    (
        "execution_evidence_dry_run_admissible",
        "execution_evidence_dry_run_admissible_count",
        "section_170_execution_evidence_dry_run_admissible",
    ),
    (
        "completion_decision_dry_run_record_valid",
        "completion_decision_dry_run_record_valid_count",
        "section_170_completion_decision_dry_run_record_valid",
    ),
    (
        "completion_decision_dry_run_admissible",
        "completion_decision_dry_run_admissible_count",
        "section_170_completion_decision_dry_run_admissible",
    ),
    (
        "completion_application_dry_run_record_valid",
        "completion_application_dry_run_record_valid_count",
        "section_170_completion_application_dry_run_record_valid",
    ),
    (
        "completion_application_dry_run_admissible",
        "completion_application_dry_run_admissible_count",
        "section_170_completion_application_dry_run_admissible",
    ),
    (
        "completion_result_dry_run_record_valid",
        "completion_result_dry_run_record_valid_count",
        "section_170_completion_result_dry_run_record_valid",
    ),
    (
        "completion_result_dry_run_admissible",
        "completion_result_dry_run_admissible_count",
        "section_170_completion_result_dry_run_admissible",
    ),
    (
        "result_readback_dry_run_record_valid",
        "result_readback_dry_run_record_valid_count",
        "section_170_result_readback_dry_run_record_valid",
    ),
    (
        "result_readback_dry_run_admissible",
        "result_readback_dry_run_admissible_count",
        "section_170_result_readback_dry_run_admissible",
    ),
)


def _attempted(value: Any) -> bool:
    return value is True or value == 1


def _sum_truthy(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(contract.get(key, 0) for contract in contracts)


def _proof_flag(record: Dict[str, Any], group: str, key: str) -> bool:
    value = record.get(group, {})
    return isinstance(value, dict) and value.get(key) is True


def _chain_flags(section_170_result_readback_summary: Dict[str, Any]) -> Dict[str, bool]:
    return {
        output_key: section_170_result_readback_summary.get(summary_key) == 1
        for output_key, summary_key, _missing_key in CHAIN_INPUTS
    }


def build_durable_executor_authoring_final_no_save_release_dry_run_contract(
    requested: bool,
    section_170_command_result_readback_dry_run_summary: Dict[str, Any],
    final_no_save_release_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    final_no_save_release_record = final_no_save_release_record or {}
    release_record_present = bool(final_no_save_release_record)
    section_170_result_readback_contract_ready = bool(
        requested
        and section_170_command_result_readback_dry_run_summary.get("status")
        == "passed"
        and section_170_command_result_readback_dry_run_summary.get(
            "result_readback_contract_defined_count"
        )
        == 1
        and section_170_command_result_readback_dry_run_summary.get(
            "result_readback_dry_run_record_rejected_count"
        )
        == 0
        and section_170_command_result_readback_dry_run_summary.get(
            "unsafe_result_readback_record_count"
        )
        == 0
        and section_170_command_result_readback_dry_run_summary.get(
            "requested_command_forbidden_count"
        )
        == 0
        and section_170_command_result_readback_dry_run_summary.get(
            "requested_command_unknown_count"
        )
        == 0
        and all(
            section_170_command_result_readback_dry_run_summary.get(key) == 0
            for key in SECTION_170_ZERO_COUNT_KEYS
        )
    )
    chain_flags = _chain_flags(section_170_command_result_readback_dry_run_summary)
    result_readback_chain_satisfied = all(chain_flags.values())
    final_no_save_release_contract_defined = bool(
        requested and section_170_result_readback_contract_ready
    )

    record_schema_matches = bool(
        release_record_present
        and final_no_save_release_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_DRY_RUN_RECORD_SCHEMA
    )
    final_no_save_release_scope_matches = bool(
        release_record_present
        and final_no_save_release_record.get("final_no_save_release_scope")
        == EXPECTED_FINAL_NO_SAVE_RELEASE_SCOPE
    )
    dry_run_only = bool(
        release_record_present
        and final_no_save_release_record.get("dry_run_only") is True
    )
    final_no_save_release_status_passed = bool(
        release_record_present
        and final_no_save_release_record.get("status") == "passed"
    )
    operator_reconfirmed_no_live_dispatch = bool(
        release_record_present
        and final_no_save_release_record.get("operator_reconfirmed_no_live_dispatch")
        is True
    )
    operator_reconfirmed_no_live_execution = bool(
        release_record_present
        and final_no_save_release_record.get("operator_reconfirmed_no_live_execution")
        is True
    )
    operator_reconfirmed_no_write_execution = bool(
        release_record_present
        and final_no_save_release_record.get("operator_reconfirmed_no_write_execution")
        is True
    )
    operator_reconfirmed_no_save_delete_rename = bool(
        release_record_present
        and final_no_save_release_record.get(
            "operator_reconfirmed_no_save_delete_rename"
        )
        is True
    )
    requested_command = final_no_save_release_record.get("requested_command", "")
    final_no_save_release_operation = final_no_save_release_record.get(
        "final_no_save_release_operation", ""
    )
    target_asset = final_no_save_release_record.get("target_asset", "")
    requested_command_allowed = bool(requested_command in ALLOWED_REQUESTED_COMMANDS)
    requested_command_forbidden = bool(requested_command in FORBIDDEN_REQUESTED_COMMANDS)
    requested_command_unknown = bool(
        release_record_present
        and requested_command not in ALLOWED_REQUESTED_COMMANDS
        and requested_command not in FORBIDDEN_REQUESTED_COMMANDS
    )
    final_no_save_release_operation_allowed = bool(
        final_no_save_release_operation
        in ALLOWED_FINAL_NO_SAVE_RELEASE_DRY_RUN_OPERATIONS
    )
    final_no_save_release_target_declared = bool(
        isinstance(target_asset, str) and target_asset.startswith("/Game/")
    )
    result_readback_admission_proof_matches = all(
        _proof_flag(
            final_no_save_release_record,
            "result_readback_admission_proof",
            key,
        )
        for key, _summary_key, _missing_key in CHAIN_INPUTS
    )
    release_boundary_proof_safe = bool(
        release_record_present
        and final_no_save_release_record.get("release_boundary_proof", {}).get(
            "durable_authoring_enabled"
        )
        is False
        and final_no_save_release_record.get("release_boundary_proof", {}).get(
            "final_durable_release_ready"
        )
        is False
        and final_no_save_release_record.get("release_boundary_proof", {}).get(
            "save_delete_rename_allowed"
        )
        is False
        and final_no_save_release_record.get("release_boundary_proof", {}).get(
            "live_durable_authoring_allowed"
        )
        is False
    )
    unsafe_final_no_save_release_record_count = sum(
        int(_attempted(final_no_save_release_record.get(key)))
        for key in UNSAFE_FINAL_NO_SAVE_RELEASE_RECORD_ACTION_KEYS
    )
    final_no_save_release_dry_run_record_valid = bool(
        final_no_save_release_contract_defined
        and result_readback_chain_satisfied
        and record_schema_matches
        and final_no_save_release_scope_matches
        and dry_run_only
        and final_no_save_release_status_passed
        and operator_reconfirmed_no_live_dispatch
        and operator_reconfirmed_no_live_execution
        and operator_reconfirmed_no_write_execution
        and operator_reconfirmed_no_save_delete_rename
        and requested_command_allowed
        and not requested_command_forbidden
        and not requested_command_unknown
        and final_no_save_release_operation_allowed
        and final_no_save_release_target_declared
        and result_readback_admission_proof_matches
        and release_boundary_proof_safe
        and unsafe_final_no_save_release_record_count == 0
    )
    final_no_save_release_dry_run_record_rejected = bool(
        release_record_present and not final_no_save_release_dry_run_record_valid
    )
    final_no_save_release_dry_run_admissible = bool(
        final_no_save_release_dry_run_record_valid
    )

    missing: list[str] = []
    if requested:
        if not section_170_result_readback_contract_ready:
            missing.append("section_170_command_result_readback_dry_run_contract_ready")
        for output_key, _summary_key, missing_key in CHAIN_INPUTS:
            if not chain_flags[output_key]:
                missing.append(missing_key)
        if not release_record_present:
            missing.append("final_no_save_release_dry_run_record_present")
        if not record_schema_matches:
            missing.append("final_no_save_release_dry_run_record_schema")
        if not final_no_save_release_scope_matches:
            missing.append("final_no_save_release_dry_run_only_scope")
        if not dry_run_only:
            missing.append("final_no_save_release_dry_run_only")
        if not final_no_save_release_status_passed:
            missing.append("final_no_save_release_dry_run_status_passed")
        if not operator_reconfirmed_no_live_dispatch:
            missing.append("operator_reconfirmed_no_live_dispatch")
        if not operator_reconfirmed_no_live_execution:
            missing.append("operator_reconfirmed_no_live_execution")
        if not operator_reconfirmed_no_write_execution:
            missing.append("operator_reconfirmed_no_write_execution")
        if not operator_reconfirmed_no_save_delete_rename:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not requested_command_allowed:
            missing.append("allowed_requested_command")
        if not final_no_save_release_operation_allowed:
            missing.append("allowed_final_no_save_release_dry_run_operation")
        if not final_no_save_release_target_declared:
            missing.append("final_no_save_release_target_declared")
        if not result_readback_admission_proof_matches:
            missing.append("result_readback_admission_proof_matches")
        if not release_boundary_proof_safe:
            missing.append("release_boundary_proof_safe")

    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_final_no_save_release_dry_run",
        "schema": DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_DRY_RUN_SCHEMA,
        "requested": requested,
        "final_no_save_release_contract_defined": (
            final_no_save_release_contract_defined
        ),
        "required_final_no_save_release_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_DRY_RUN_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_final_no_save_release_scope": (
            EXPECTED_FINAL_NO_SAVE_RELEASE_SCOPE if requested else ""
        ),
        "allowed_final_no_save_release_dry_run_operations": (
            list(ALLOWED_FINAL_NO_SAVE_RELEASE_DRY_RUN_OPERATIONS)
            if requested
            else []
        ),
        "allowed_requested_commands": (
            list(ALLOWED_REQUESTED_COMMANDS) if requested else []
        ),
        "forbidden_requested_commands": (
            list(FORBIDDEN_REQUESTED_COMMANDS) if requested else []
        ),
        "section_170_result_readback_contract_ready": (
            section_170_result_readback_contract_ready
        ),
        "result_readback_chain_satisfied": result_readback_chain_satisfied,
        "final_no_save_release_dry_run_record_present": release_record_present,
        "record_schema_matches": record_schema_matches,
        "final_no_save_release_scope_matches": final_no_save_release_scope_matches,
        "dry_run_only": dry_run_only,
        "final_no_save_release_status_passed": (
            final_no_save_release_status_passed
        ),
        "operator_reconfirmed_no_live_dispatch": (
            operator_reconfirmed_no_live_dispatch
        ),
        "operator_reconfirmed_no_live_execution": (
            operator_reconfirmed_no_live_execution
        ),
        "operator_reconfirmed_no_write_execution": (
            operator_reconfirmed_no_write_execution
        ),
        "operator_reconfirmed_no_save_delete_rename": (
            operator_reconfirmed_no_save_delete_rename
        ),
        "requested_command_allowed": requested_command_allowed,
        "requested_command_forbidden": requested_command_forbidden,
        "requested_command_unknown": requested_command_unknown,
        "final_no_save_release_operation_allowed": (
            final_no_save_release_operation_allowed
        ),
        "final_no_save_release_target_declared": (
            final_no_save_release_target_declared
        ),
        "result_readback_admission_proof_matches": (
            result_readback_admission_proof_matches
        ),
        "release_boundary_proof_safe": release_boundary_proof_safe,
        "final_no_save_release_dry_run_record_valid": (
            final_no_save_release_dry_run_record_valid
        ),
        "final_no_save_release_dry_run_record_rejected": (
            final_no_save_release_dry_run_record_rejected
        ),
        "final_no_save_release_dry_run_admissible": (
            final_no_save_release_dry_run_admissible
        ),
        "unsafe_final_no_save_release_record_count": (
            unsafe_final_no_save_release_record_count
        ),
        "missing_final_no_save_release_dry_run_prerequisites": missing,
        "missing_final_no_save_release_dry_run_prerequisite_count": len(missing),
    }
    contract.update(chain_flags)
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract["final_no_save_release_dry_run_admissible"] = (
        final_no_save_release_dry_run_admissible
    )
    return contract


def summarize_durable_executor_authoring_final_no_save_release_dry_runs(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(
        requested, "final_no_save_release_dry_run_record_rejected"
    )
    unsafe_count = _sum_count(
        requested, "unsafe_final_no_save_release_record_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "final_no_save_release_contract_defined")
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and _sum_truthy(requested, "requested_command_forbidden") == 0
            and _sum_truthy(requested, "requested_command_unknown") == 0
            and all(
                _sum_truthy(requested, key) == 0
                for key in OUTPUT_ACTION_KEYS
                if key != "final_no_save_release_dry_run_admissible"
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_DRY_RUN_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_final_no_save_release_dry_run_count": len(
            requested
        ),
        "final_no_save_release_contract_defined_count": _sum_truthy(
            requested, "final_no_save_release_contract_defined"
        ),
        "section_170_result_readback_contract_ready_count": _sum_truthy(
            requested, "section_170_result_readback_contract_ready"
        ),
    }
    summary.update(
        {
            f"{output_key}_count": _sum_truthy(requested, output_key)
            for output_key, _summary_key, _missing_key in CHAIN_INPUTS
        }
    )
    summary.update(
        {
            "result_readback_chain_satisfied_count": _sum_truthy(
                requested, "result_readback_chain_satisfied"
            ),
            "final_no_save_release_dry_run_record_present_count": _sum_truthy(
                requested, "final_no_save_release_dry_run_record_present"
            ),
            "record_schema_matches_count": _sum_truthy(
                requested, "record_schema_matches"
            ),
            "final_no_save_release_scope_matches_count": _sum_truthy(
                requested, "final_no_save_release_scope_matches"
            ),
            "dry_run_only_count": _sum_truthy(requested, "dry_run_only"),
            "final_no_save_release_status_passed_count": _sum_truthy(
                requested, "final_no_save_release_status_passed"
            ),
            "operator_reconfirmed_no_live_dispatch_count": _sum_truthy(
                requested, "operator_reconfirmed_no_live_dispatch"
            ),
            "operator_reconfirmed_no_live_execution_count": _sum_truthy(
                requested, "operator_reconfirmed_no_live_execution"
            ),
            "operator_reconfirmed_no_write_execution_count": _sum_truthy(
                requested, "operator_reconfirmed_no_write_execution"
            ),
            "operator_reconfirmed_no_save_delete_rename_count": _sum_truthy(
                requested, "operator_reconfirmed_no_save_delete_rename"
            ),
            "requested_command_allowed_count": _sum_truthy(
                requested, "requested_command_allowed"
            ),
            "requested_command_forbidden_count": _sum_truthy(
                requested, "requested_command_forbidden"
            ),
            "requested_command_unknown_count": _sum_truthy(
                requested, "requested_command_unknown"
            ),
            "final_no_save_release_operation_allowed_count": _sum_truthy(
                requested, "final_no_save_release_operation_allowed"
            ),
            "final_no_save_release_target_declared_count": _sum_truthy(
                requested, "final_no_save_release_target_declared"
            ),
            "result_readback_admission_proof_matches_count": _sum_truthy(
                requested, "result_readback_admission_proof_matches"
            ),
            "release_boundary_proof_safe_count": _sum_truthy(
                requested, "release_boundary_proof_safe"
            ),
            "final_no_save_release_dry_run_record_valid_count": _sum_truthy(
                requested, "final_no_save_release_dry_run_record_valid"
            ),
            "final_no_save_release_dry_run_record_rejected_count": rejected_count,
            "final_no_save_release_dry_run_admissible_count": _sum_truthy(
                requested, "final_no_save_release_dry_run_admissible"
            ),
            "unsafe_final_no_save_release_record_count": unsafe_count,
            "missing_final_no_save_release_dry_run_prerequisite_count": _sum_count(
                requested,
                "missing_final_no_save_release_dry_run_prerequisite_count",
            ),
        }
    )
    summary.update(
        {
            f"{key}_count": _sum_truthy(requested, key)
            for key in OUTPUT_ACTION_KEYS
        }
    )
    return summary
