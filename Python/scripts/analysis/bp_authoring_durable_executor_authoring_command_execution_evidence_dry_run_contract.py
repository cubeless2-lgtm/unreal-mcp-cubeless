#!/usr/bin/env python
"""
Section 166 durable executor authoring command execution evidence dry-run contract.

This contract defines an offline execution evidence dry-run gate after the
Section 165 execution dry-run. It can admit only an execution evidence dry-run
record. It does not promote execution evidence, promote execution envelopes,
open command paths, dispatch live commands, execute live commands, modify
assets, dirty packages, save, delete/rename, cleanup, change code, or probe
live bridges.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_DRY_RUN_SCHEMA = (
    "section_166_durable_executor_authoring_command_execution_evidence_dry_run_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_DRY_RUN_RECORD_SCHEMA = (
    "section_166_durable_executor_authoring_command_execution_evidence_dry_run_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_DRY_RUN_SUMMARY_SCHEMA = (
    "section_166_durable_executor_authoring_command_execution_evidence_dry_run_summary_v1"
)
EXPECTED_EXECUTION_EVIDENCE_SCOPE = (
    "durable_executor_authoring_command_execution_evidence_dry_run_only"
)

ALLOWED_EXECUTION_EVIDENCE_DRY_RUN_OPERATIONS = (
    "validate_execution_evidence_envelope",
    "evaluate_execution_evidence_readiness",
    "execution_evidence_dry_run_only",
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
    "execution_evidence_dry_run_started",
    "execution_evidence_dry_run_accepted",
    "execution_evidence_dry_run_admissible",
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
UNSAFE_EXECUTION_EVIDENCE_RECORD_ACTION_KEYS = (
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
SECTION_165_ZERO_COUNT_KEYS = (
    "durable_execution_envelope_promoted_count",
    "durable_evidence_promoted_count",
    "durable_dispatch_envelope_promoted_count",
    "durable_command_request_promoted_count",
    "durable_executor_command_path_opened_count",
    "durable_executor_command_path_allowed_count",
    "durable_authoring_command_allowed_count",
    "durable_authoring_command_dispatched_count",
    "durable_authoring_command_executed_count",
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
        "section_165_open_activation_promotion_readiness_chain_satisfied",
    ),
    (
        "authoring_enable_chain_satisfied",
        "authoring_enable_chain_satisfied_count",
        "section_165_authoring_enable_chain_satisfied",
    ),
    (
        "durable_release_readiness_chain_reconfirmed",
        "durable_release_readiness_chain_reconfirmed_count",
        "section_165_durable_release_readiness_chain_reconfirmed",
    ),
    (
        "authoring_command_inputs_satisfied",
        "authoring_command_inputs_satisfied_count",
        "section_165_authoring_command_inputs_satisfied",
    ),
    (
        "authoring_command_record_valid",
        "authoring_command_record_valid_count",
        "section_165_authoring_command_record_valid",
    ),
    (
        "dry_run_route_record_valid",
        "dry_run_route_record_valid_count",
        "section_165_dry_run_route_record_valid",
    ),
    (
        "dry_run_route_admissible",
        "dry_run_route_admissible_count",
        "section_165_dry_run_route_admissible",
    ),
    (
        "dispatch_dry_run_record_valid",
        "dispatch_dry_run_record_valid_count",
        "section_165_dispatch_dry_run_record_valid",
    ),
    (
        "dispatch_dry_run_admissible",
        "dispatch_dry_run_admissible_count",
        "section_165_dispatch_dry_run_admissible",
    ),
    (
        "dispatch_evidence_dry_run_record_valid",
        "dispatch_evidence_dry_run_record_valid_count",
        "section_165_dispatch_evidence_dry_run_record_valid",
    ),
    (
        "dispatch_evidence_dry_run_admissible",
        "dispatch_evidence_dry_run_admissible_count",
        "section_165_dispatch_evidence_dry_run_admissible",
    ),
    (
        "execution_dry_run_record_valid",
        "execution_dry_run_record_valid_count",
        "section_165_execution_dry_run_record_valid",
    ),
    (
        "execution_dry_run_admissible",
        "execution_dry_run_admissible_count",
        "section_165_execution_dry_run_admissible",
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


def _chain_flags(section_165_execution_summary: Dict[str, Any]) -> Dict[str, bool]:
    return {
        output_key: section_165_execution_summary.get(summary_key) == 1
        for output_key, summary_key, _missing_key in CHAIN_INPUTS
    }


def build_durable_executor_authoring_command_execution_evidence_dry_run_contract(
    requested: bool,
    section_165_command_execution_dry_run_summary: Dict[str, Any],
    execution_evidence_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    execution_evidence_record = execution_evidence_record or {}
    execution_evidence_record_present = bool(execution_evidence_record)
    section_165_execution_contract_ready = bool(
        requested
        and section_165_command_execution_dry_run_summary.get("status") == "passed"
        and section_165_command_execution_dry_run_summary.get(
            "execution_contract_defined_count"
        )
        == 1
        and section_165_command_execution_dry_run_summary.get(
            "execution_dry_run_record_rejected_count"
        )
        == 0
        and section_165_command_execution_dry_run_summary.get(
            "unsafe_execution_record_count"
        )
        == 0
        and section_165_command_execution_dry_run_summary.get(
            "requested_command_forbidden_count"
        )
        == 0
        and section_165_command_execution_dry_run_summary.get(
            "requested_command_unknown_count"
        )
        == 0
        and all(
            section_165_command_execution_dry_run_summary.get(key) == 0
            for key in SECTION_165_ZERO_COUNT_KEYS
        )
    )
    chain_flags = _chain_flags(section_165_command_execution_dry_run_summary)
    execution_chain_satisfied = all(chain_flags.values())
    execution_evidence_contract_defined = bool(
        requested and section_165_execution_contract_ready
    )

    record_schema_matches = bool(
        execution_evidence_record_present
        and execution_evidence_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_DRY_RUN_RECORD_SCHEMA
    )
    execution_evidence_scope_matches = bool(
        execution_evidence_record_present
        and execution_evidence_record.get("execution_evidence_scope")
        == EXPECTED_EXECUTION_EVIDENCE_SCOPE
    )
    dry_run_only = bool(
        execution_evidence_record_present
        and execution_evidence_record.get("dry_run_only") is True
    )
    execution_evidence_status_passed = bool(
        execution_evidence_record_present
        and execution_evidence_record.get("status") == "passed"
    )
    operator_reconfirmed_no_live_dispatch = bool(
        execution_evidence_record_present
        and execution_evidence_record.get("operator_reconfirmed_no_live_dispatch")
        is True
    )
    operator_reconfirmed_no_live_execution = bool(
        execution_evidence_record_present
        and execution_evidence_record.get("operator_reconfirmed_no_live_execution")
        is True
    )
    operator_reconfirmed_no_write_execution = bool(
        execution_evidence_record_present
        and execution_evidence_record.get("operator_reconfirmed_no_write_execution")
        is True
    )
    operator_reconfirmed_no_save_delete_rename = bool(
        execution_evidence_record_present
        and execution_evidence_record.get(
            "operator_reconfirmed_no_save_delete_rename"
        )
        is True
    )
    requested_command = execution_evidence_record.get("requested_command", "")
    execution_evidence_operation = execution_evidence_record.get(
        "execution_evidence_operation", ""
    )
    target_asset = execution_evidence_record.get("target_asset", "")
    requested_command_allowed = bool(requested_command in ALLOWED_REQUESTED_COMMANDS)
    requested_command_forbidden = bool(requested_command in FORBIDDEN_REQUESTED_COMMANDS)
    requested_command_unknown = bool(
        execution_evidence_record_present
        and requested_command not in ALLOWED_REQUESTED_COMMANDS
        and requested_command not in FORBIDDEN_REQUESTED_COMMANDS
    )
    execution_evidence_operation_allowed = bool(
        execution_evidence_operation
        in ALLOWED_EXECUTION_EVIDENCE_DRY_RUN_OPERATIONS
    )
    execution_evidence_target_declared = bool(
        isinstance(target_asset, str) and target_asset.startswith("/Game/")
    )
    execution_admission_proof_matches = all(
        _proof_flag(execution_evidence_record, "execution_admission_proof", key)
        for key, _summary_key, _missing_key in CHAIN_INPUTS
    )
    release_boundary_proof_safe = bool(
        execution_evidence_record_present
        and execution_evidence_record.get("release_boundary_proof", {}).get(
            "durable_authoring_enabled"
        )
        is False
        and execution_evidence_record.get("release_boundary_proof", {}).get(
            "final_durable_release_ready"
        )
        is False
        and execution_evidence_record.get("release_boundary_proof", {}).get(
            "save_delete_rename_allowed"
        )
        is False
        and execution_evidence_record.get("release_boundary_proof", {}).get(
            "live_durable_authoring_allowed"
        )
        is False
    )
    unsafe_execution_evidence_record_count = sum(
        int(_attempted(execution_evidence_record.get(key)))
        for key in UNSAFE_EXECUTION_EVIDENCE_RECORD_ACTION_KEYS
    )
    execution_evidence_dry_run_record_valid = bool(
        execution_evidence_contract_defined
        and execution_chain_satisfied
        and record_schema_matches
        and execution_evidence_scope_matches
        and dry_run_only
        and execution_evidence_status_passed
        and operator_reconfirmed_no_live_dispatch
        and operator_reconfirmed_no_live_execution
        and operator_reconfirmed_no_write_execution
        and operator_reconfirmed_no_save_delete_rename
        and requested_command_allowed
        and not requested_command_forbidden
        and not requested_command_unknown
        and execution_evidence_operation_allowed
        and execution_evidence_target_declared
        and execution_admission_proof_matches
        and release_boundary_proof_safe
        and unsafe_execution_evidence_record_count == 0
    )
    execution_evidence_dry_run_record_rejected = bool(
        execution_evidence_record_present
        and not execution_evidence_dry_run_record_valid
    )
    execution_evidence_dry_run_admissible = bool(
        execution_evidence_dry_run_record_valid
    )

    missing: list[str] = []
    if requested:
        if not section_165_execution_contract_ready:
            missing.append("section_165_command_execution_dry_run_contract_ready")
        for output_key, _summary_key, missing_key in CHAIN_INPUTS:
            if not chain_flags[output_key]:
                missing.append(missing_key)
        if not execution_evidence_record_present:
            missing.append("command_execution_evidence_dry_run_record_present")
        if not record_schema_matches:
            missing.append("command_execution_evidence_dry_run_record_schema")
        if not execution_evidence_scope_matches:
            missing.append("command_execution_evidence_dry_run_only_scope")
        if not dry_run_only:
            missing.append("execution_evidence_dry_run_only")
        if not execution_evidence_status_passed:
            missing.append("command_execution_evidence_dry_run_status_passed")
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
        if not execution_evidence_operation_allowed:
            missing.append("allowed_execution_evidence_dry_run_operation")
        if not execution_evidence_target_declared:
            missing.append("execution_evidence_target_declared")
        if not execution_admission_proof_matches:
            missing.append("execution_admission_proof_matches")
        if not release_boundary_proof_safe:
            missing.append("release_boundary_proof_safe")

    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_command_execution_evidence_dry_run",
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_DRY_RUN_SCHEMA,
        "requested": requested,
        "execution_evidence_contract_defined": (
            execution_evidence_contract_defined
        ),
        "required_execution_evidence_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_DRY_RUN_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_execution_evidence_scope": (
            EXPECTED_EXECUTION_EVIDENCE_SCOPE if requested else ""
        ),
        "allowed_execution_evidence_dry_run_operations": (
            list(ALLOWED_EXECUTION_EVIDENCE_DRY_RUN_OPERATIONS)
            if requested
            else []
        ),
        "allowed_requested_commands": (
            list(ALLOWED_REQUESTED_COMMANDS) if requested else []
        ),
        "forbidden_requested_commands": (
            list(FORBIDDEN_REQUESTED_COMMANDS) if requested else []
        ),
        "section_165_execution_contract_ready": section_165_execution_contract_ready,
        "execution_chain_satisfied": execution_chain_satisfied,
        "execution_evidence_dry_run_record_present": (
            execution_evidence_record_present
        ),
        "record_schema_matches": record_schema_matches,
        "execution_evidence_scope_matches": execution_evidence_scope_matches,
        "dry_run_only": dry_run_only,
        "execution_evidence_status_passed": execution_evidence_status_passed,
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
        "execution_evidence_operation_allowed": (
            execution_evidence_operation_allowed
        ),
        "execution_evidence_target_declared": (
            execution_evidence_target_declared
        ),
        "execution_admission_proof_matches": execution_admission_proof_matches,
        "release_boundary_proof_safe": release_boundary_proof_safe,
        "execution_evidence_dry_run_record_valid": (
            execution_evidence_dry_run_record_valid
        ),
        "execution_evidence_dry_run_record_rejected": (
            execution_evidence_dry_run_record_rejected
        ),
        "execution_evidence_dry_run_admissible": (
            execution_evidence_dry_run_admissible
        ),
        "unsafe_execution_evidence_record_count": (
            unsafe_execution_evidence_record_count
        ),
        "missing_execution_evidence_dry_run_prerequisites": missing,
        "missing_execution_evidence_dry_run_prerequisite_count": len(missing),
    }
    contract.update(chain_flags)
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract["execution_evidence_dry_run_admissible"] = (
        execution_evidence_dry_run_admissible
    )
    return contract


def summarize_durable_executor_authoring_command_execution_evidence_dry_runs(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(
        requested, "execution_evidence_dry_run_record_rejected"
    )
    unsafe_count = _sum_count(
        requested, "unsafe_execution_evidence_record_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "execution_evidence_contract_defined")
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and _sum_truthy(requested, "requested_command_forbidden") == 0
            and _sum_truthy(requested, "requested_command_unknown") == 0
            and all(
                _sum_truthy(requested, key) == 0
                for key in OUTPUT_ACTION_KEYS
                if key != "execution_evidence_dry_run_admissible"
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_DRY_RUN_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_command_execution_evidence_dry_run_count": len(
            requested
        ),
        "execution_evidence_contract_defined_count": _sum_truthy(
            requested, "execution_evidence_contract_defined"
        ),
        "section_165_execution_contract_ready_count": _sum_truthy(
            requested, "section_165_execution_contract_ready"
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
            "execution_chain_satisfied_count": _sum_truthy(
                requested, "execution_chain_satisfied"
            ),
            "execution_evidence_dry_run_record_present_count": _sum_truthy(
                requested, "execution_evidence_dry_run_record_present"
            ),
            "record_schema_matches_count": _sum_truthy(
                requested, "record_schema_matches"
            ),
            "execution_evidence_scope_matches_count": _sum_truthy(
                requested, "execution_evidence_scope_matches"
            ),
            "dry_run_only_count": _sum_truthy(requested, "dry_run_only"),
            "execution_evidence_status_passed_count": _sum_truthy(
                requested, "execution_evidence_status_passed"
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
            "execution_evidence_operation_allowed_count": _sum_truthy(
                requested, "execution_evidence_operation_allowed"
            ),
            "execution_evidence_target_declared_count": _sum_truthy(
                requested, "execution_evidence_target_declared"
            ),
            "execution_admission_proof_matches_count": _sum_truthy(
                requested, "execution_admission_proof_matches"
            ),
            "release_boundary_proof_safe_count": _sum_truthy(
                requested, "release_boundary_proof_safe"
            ),
            "execution_evidence_dry_run_record_valid_count": _sum_truthy(
                requested, "execution_evidence_dry_run_record_valid"
            ),
            "execution_evidence_dry_run_record_rejected_count": rejected_count,
            "execution_evidence_dry_run_admissible_count": _sum_truthy(
                requested, "execution_evidence_dry_run_admissible"
            ),
            "unsafe_execution_evidence_record_count": unsafe_count,
            "missing_execution_evidence_dry_run_prerequisite_count": _sum_count(
                requested,
                "missing_execution_evidence_dry_run_prerequisite_count",
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
