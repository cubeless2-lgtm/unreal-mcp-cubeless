#!/usr/bin/env python
"""
Section 168 durable executor authoring command completion application dry-run contract.

This contract defines an offline completion application dry-run gate after the
Section 167 completion decision dry-run. It can admit only a completion
application dry-run record. It does not promote completion applications,
apply completion, promote completion decisions, open command paths, dispatch
live commands, execute live commands, modify assets, dirty packages, save,
delete/rename, cleanup, change code, or probe live bridges.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_DRY_RUN_SCHEMA = (
    "section_168_durable_executor_authoring_command_completion_application_dry_run_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_DRY_RUN_RECORD_SCHEMA = (
    "section_168_durable_executor_authoring_command_completion_application_dry_run_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_DRY_RUN_SUMMARY_SCHEMA = (
    "section_168_durable_executor_authoring_command_completion_application_dry_run_summary_v1"
)
EXPECTED_COMPLETION_APPLICATION_SCOPE = (
    "durable_executor_authoring_command_completion_application_dry_run_only"
)

ALLOWED_COMPLETION_APPLICATION_DRY_RUN_OPERATIONS = (
    "validate_completion_application_envelope",
    "evaluate_completion_application_readiness",
    "completion_application_dry_run_only",
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
    "completion_application_dry_run_started",
    "completion_application_dry_run_accepted",
    "completion_application_dry_run_admissible",
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
UNSAFE_COMPLETION_APPLICATION_RECORD_ACTION_KEYS = (
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
SECTION_167_ZERO_COUNT_KEYS = (
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
        "section_167_open_activation_promotion_readiness_chain_satisfied",
    ),
    (
        "authoring_enable_chain_satisfied",
        "authoring_enable_chain_satisfied_count",
        "section_167_authoring_enable_chain_satisfied",
    ),
    (
        "durable_release_readiness_chain_reconfirmed",
        "durable_release_readiness_chain_reconfirmed_count",
        "section_167_durable_release_readiness_chain_reconfirmed",
    ),
    (
        "authoring_command_inputs_satisfied",
        "authoring_command_inputs_satisfied_count",
        "section_167_authoring_command_inputs_satisfied",
    ),
    (
        "authoring_command_record_valid",
        "authoring_command_record_valid_count",
        "section_167_authoring_command_record_valid",
    ),
    (
        "dry_run_route_record_valid",
        "dry_run_route_record_valid_count",
        "section_167_dry_run_route_record_valid",
    ),
    (
        "dry_run_route_admissible",
        "dry_run_route_admissible_count",
        "section_167_dry_run_route_admissible",
    ),
    (
        "dispatch_dry_run_record_valid",
        "dispatch_dry_run_record_valid_count",
        "section_167_dispatch_dry_run_record_valid",
    ),
    (
        "dispatch_dry_run_admissible",
        "dispatch_dry_run_admissible_count",
        "section_167_dispatch_dry_run_admissible",
    ),
    (
        "dispatch_evidence_dry_run_record_valid",
        "dispatch_evidence_dry_run_record_valid_count",
        "section_167_dispatch_evidence_dry_run_record_valid",
    ),
    (
        "dispatch_evidence_dry_run_admissible",
        "dispatch_evidence_dry_run_admissible_count",
        "section_167_dispatch_evidence_dry_run_admissible",
    ),
    (
        "execution_dry_run_record_valid",
        "execution_dry_run_record_valid_count",
        "section_167_execution_dry_run_record_valid",
    ),
    (
        "execution_dry_run_admissible",
        "execution_dry_run_admissible_count",
        "section_167_execution_dry_run_admissible",
    ),
    (
        "execution_evidence_dry_run_record_valid",
        "execution_evidence_dry_run_record_valid_count",
        "section_167_execution_evidence_dry_run_record_valid",
    ),
    (
        "execution_evidence_dry_run_admissible",
        "execution_evidence_dry_run_admissible_count",
        "section_167_execution_evidence_dry_run_admissible",
    ),
    (
        "completion_decision_dry_run_record_valid",
        "completion_decision_dry_run_record_valid_count",
        "section_167_completion_decision_dry_run_record_valid",
    ),
    (
        "completion_decision_dry_run_admissible",
        "completion_decision_dry_run_admissible_count",
        "section_167_completion_decision_dry_run_admissible",
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


def _chain_flags(section_167_completion_decision_summary: Dict[str, Any]) -> Dict[str, bool]:
    return {
        output_key: section_167_completion_decision_summary.get(summary_key) == 1
        for output_key, summary_key, _missing_key in CHAIN_INPUTS
    }


def build_durable_executor_authoring_command_completion_application_dry_run_contract(
    requested: bool,
    section_167_command_completion_decision_dry_run_summary: Dict[str, Any],
    completion_application_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    completion_application_record = completion_application_record or {}
    completion_application_record_present = bool(completion_application_record)
    section_167_completion_decision_contract_ready = bool(
        requested
        and section_167_command_completion_decision_dry_run_summary.get("status")
        == "passed"
        and section_167_command_completion_decision_dry_run_summary.get(
            "completion_decision_contract_defined_count"
        )
        == 1
        and section_167_command_completion_decision_dry_run_summary.get(
            "completion_decision_dry_run_record_rejected_count"
        )
        == 0
        and section_167_command_completion_decision_dry_run_summary.get(
            "unsafe_completion_decision_record_count"
        )
        == 0
        and section_167_command_completion_decision_dry_run_summary.get(
            "requested_command_forbidden_count"
        )
        == 0
        and section_167_command_completion_decision_dry_run_summary.get(
            "requested_command_unknown_count"
        )
        == 0
        and all(
            section_167_command_completion_decision_dry_run_summary.get(key) == 0
            for key in SECTION_167_ZERO_COUNT_KEYS
        )
    )
    chain_flags = _chain_flags(
        section_167_command_completion_decision_dry_run_summary
    )
    completion_decision_chain_satisfied = all(chain_flags.values())
    completion_application_contract_defined = bool(
        requested and section_167_completion_decision_contract_ready
    )

    record_schema_matches = bool(
        completion_application_record_present
        and completion_application_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_DRY_RUN_RECORD_SCHEMA
    )
    completion_application_scope_matches = bool(
        completion_application_record_present
        and completion_application_record.get("completion_application_scope")
        == EXPECTED_COMPLETION_APPLICATION_SCOPE
    )
    dry_run_only = bool(
        completion_application_record_present
        and completion_application_record.get("dry_run_only") is True
    )
    completion_application_status_passed = bool(
        completion_application_record_present
        and completion_application_record.get("status") == "passed"
    )
    operator_reconfirmed_no_live_dispatch = bool(
        completion_application_record_present
        and completion_application_record.get("operator_reconfirmed_no_live_dispatch")
        is True
    )
    operator_reconfirmed_no_live_execution = bool(
        completion_application_record_present
        and completion_application_record.get("operator_reconfirmed_no_live_execution")
        is True
    )
    operator_reconfirmed_no_write_execution = bool(
        completion_application_record_present
        and completion_application_record.get("operator_reconfirmed_no_write_execution")
        is True
    )
    operator_reconfirmed_no_save_delete_rename = bool(
        completion_application_record_present
        and completion_application_record.get(
            "operator_reconfirmed_no_save_delete_rename"
        )
        is True
    )
    requested_command = completion_application_record.get("requested_command", "")
    completion_application_operation = completion_application_record.get(
        "completion_application_operation", ""
    )
    target_asset = completion_application_record.get("target_asset", "")
    requested_command_allowed = bool(requested_command in ALLOWED_REQUESTED_COMMANDS)
    requested_command_forbidden = bool(requested_command in FORBIDDEN_REQUESTED_COMMANDS)
    requested_command_unknown = bool(
        completion_application_record_present
        and requested_command not in ALLOWED_REQUESTED_COMMANDS
        and requested_command not in FORBIDDEN_REQUESTED_COMMANDS
    )
    completion_application_operation_allowed = bool(
        completion_application_operation
        in ALLOWED_COMPLETION_APPLICATION_DRY_RUN_OPERATIONS
    )
    completion_application_target_declared = bool(
        isinstance(target_asset, str) and target_asset.startswith("/Game/")
    )
    completion_decision_admission_proof_matches = all(
        _proof_flag(
            completion_application_record,
            "completion_decision_admission_proof",
            key,
        )
        for key, _summary_key, _missing_key in CHAIN_INPUTS
    )
    release_boundary_proof_safe = bool(
        completion_application_record_present
        and completion_application_record.get("release_boundary_proof", {}).get(
            "durable_authoring_enabled"
        )
        is False
        and completion_application_record.get("release_boundary_proof", {}).get(
            "final_durable_release_ready"
        )
        is False
        and completion_application_record.get("release_boundary_proof", {}).get(
            "save_delete_rename_allowed"
        )
        is False
        and completion_application_record.get("release_boundary_proof", {}).get(
            "live_durable_authoring_allowed"
        )
        is False
    )
    unsafe_completion_application_record_count = sum(
        int(_attempted(completion_application_record.get(key)))
        for key in UNSAFE_COMPLETION_APPLICATION_RECORD_ACTION_KEYS
    )
    completion_application_dry_run_record_valid = bool(
        completion_application_contract_defined
        and completion_decision_chain_satisfied
        and record_schema_matches
        and completion_application_scope_matches
        and dry_run_only
        and completion_application_status_passed
        and operator_reconfirmed_no_live_dispatch
        and operator_reconfirmed_no_live_execution
        and operator_reconfirmed_no_write_execution
        and operator_reconfirmed_no_save_delete_rename
        and requested_command_allowed
        and not requested_command_forbidden
        and not requested_command_unknown
        and completion_application_operation_allowed
        and completion_application_target_declared
        and completion_decision_admission_proof_matches
        and release_boundary_proof_safe
        and unsafe_completion_application_record_count == 0
    )
    completion_application_dry_run_record_rejected = bool(
        completion_application_record_present
        and not completion_application_dry_run_record_valid
    )
    completion_application_dry_run_admissible = bool(
        completion_application_dry_run_record_valid
    )

    missing: list[str] = []
    if requested:
        if not section_167_completion_decision_contract_ready:
            missing.append(
                "section_167_command_completion_decision_dry_run_contract_ready"
            )
        for output_key, _summary_key, missing_key in CHAIN_INPUTS:
            if not chain_flags[output_key]:
                missing.append(missing_key)
        if not completion_application_record_present:
            missing.append("command_completion_application_dry_run_record_present")
        if not record_schema_matches:
            missing.append("command_completion_application_dry_run_record_schema")
        if not completion_application_scope_matches:
            missing.append("command_completion_application_dry_run_only_scope")
        if not dry_run_only:
            missing.append("completion_application_dry_run_only")
        if not completion_application_status_passed:
            missing.append("command_completion_application_dry_run_status_passed")
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
        if not completion_application_operation_allowed:
            missing.append("allowed_completion_application_dry_run_operation")
        if not completion_application_target_declared:
            missing.append("completion_application_target_declared")
        if not completion_decision_admission_proof_matches:
            missing.append("completion_decision_admission_proof_matches")
        if not release_boundary_proof_safe:
            missing.append("release_boundary_proof_safe")

    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_command_completion_application_dry_run",
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_DRY_RUN_SCHEMA,
        "requested": requested,
        "completion_application_contract_defined": (
            completion_application_contract_defined
        ),
        "required_completion_application_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_DRY_RUN_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_completion_application_scope": (
            EXPECTED_COMPLETION_APPLICATION_SCOPE if requested else ""
        ),
        "allowed_completion_application_dry_run_operations": (
            list(ALLOWED_COMPLETION_APPLICATION_DRY_RUN_OPERATIONS)
            if requested
            else []
        ),
        "allowed_requested_commands": (
            list(ALLOWED_REQUESTED_COMMANDS) if requested else []
        ),
        "forbidden_requested_commands": (
            list(FORBIDDEN_REQUESTED_COMMANDS) if requested else []
        ),
        "section_167_completion_decision_contract_ready": (
            section_167_completion_decision_contract_ready
        ),
        "completion_decision_chain_satisfied": completion_decision_chain_satisfied,
        "completion_application_dry_run_record_present": (
            completion_application_record_present
        ),
        "record_schema_matches": record_schema_matches,
        "completion_application_scope_matches": completion_application_scope_matches,
        "dry_run_only": dry_run_only,
        "completion_application_status_passed": completion_application_status_passed,
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
        "completion_application_operation_allowed": (
            completion_application_operation_allowed
        ),
        "completion_application_target_declared": completion_application_target_declared,
        "completion_decision_admission_proof_matches": (
            completion_decision_admission_proof_matches
        ),
        "release_boundary_proof_safe": release_boundary_proof_safe,
        "completion_application_dry_run_record_valid": (
            completion_application_dry_run_record_valid
        ),
        "completion_application_dry_run_record_rejected": (
            completion_application_dry_run_record_rejected
        ),
        "completion_application_dry_run_admissible": (
            completion_application_dry_run_admissible
        ),
        "unsafe_completion_application_record_count": (
            unsafe_completion_application_record_count
        ),
        "missing_completion_application_dry_run_prerequisites": missing,
        "missing_completion_application_dry_run_prerequisite_count": len(missing),
    }
    contract.update(chain_flags)
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract["completion_application_dry_run_admissible"] = (
        completion_application_dry_run_admissible
    )
    return contract


def summarize_durable_executor_authoring_command_completion_application_dry_runs(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(
        requested, "completion_application_dry_run_record_rejected"
    )
    unsafe_count = _sum_count(
        requested, "unsafe_completion_application_record_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "completion_application_contract_defined")
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and _sum_truthy(requested, "requested_command_forbidden") == 0
            and _sum_truthy(requested, "requested_command_unknown") == 0
            and all(
                _sum_truthy(requested, key) == 0
                for key in OUTPUT_ACTION_KEYS
                if key != "completion_application_dry_run_admissible"
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_DRY_RUN_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_command_completion_application_dry_run_count": len(
            requested
        ),
        "completion_application_contract_defined_count": _sum_truthy(
            requested, "completion_application_contract_defined"
        ),
        "section_167_completion_decision_contract_ready_count": _sum_truthy(
            requested, "section_167_completion_decision_contract_ready"
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
            "completion_decision_chain_satisfied_count": _sum_truthy(
                requested, "completion_decision_chain_satisfied"
            ),
            "completion_application_dry_run_record_present_count": _sum_truthy(
                requested, "completion_application_dry_run_record_present"
            ),
            "record_schema_matches_count": _sum_truthy(
                requested, "record_schema_matches"
            ),
            "completion_application_scope_matches_count": _sum_truthy(
                requested, "completion_application_scope_matches"
            ),
            "dry_run_only_count": _sum_truthy(requested, "dry_run_only"),
            "completion_application_status_passed_count": _sum_truthy(
                requested, "completion_application_status_passed"
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
            "completion_application_operation_allowed_count": _sum_truthy(
                requested, "completion_application_operation_allowed"
            ),
            "completion_application_target_declared_count": _sum_truthy(
                requested, "completion_application_target_declared"
            ),
            "completion_decision_admission_proof_matches_count": _sum_truthy(
                requested, "completion_decision_admission_proof_matches"
            ),
            "release_boundary_proof_safe_count": _sum_truthy(
                requested, "release_boundary_proof_safe"
            ),
            "completion_application_dry_run_record_valid_count": _sum_truthy(
                requested, "completion_application_dry_run_record_valid"
            ),
            "completion_application_dry_run_record_rejected_count": rejected_count,
            "completion_application_dry_run_admissible_count": _sum_truthy(
                requested, "completion_application_dry_run_admissible"
            ),
            "unsafe_completion_application_record_count": unsafe_count,
            "missing_completion_application_dry_run_prerequisite_count": _sum_count(
                requested,
                "missing_completion_application_dry_run_prerequisite_count",
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
