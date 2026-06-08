#!/usr/bin/env python
"""
Section 163 durable executor authoring command dispatch dry-run contract.

This contract defines an offline dispatch dry-run gate after the Section 162
command request dry-run route. It can admit only a dry-run dispatch envelope.
It does not promote durable commands, open command paths, dispatch live
commands, execute commands, modify assets, dirty packages, save, delete/rename,
cleanup, change code, or probe live bridges.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_DRY_RUN_SCHEMA = (
    "section_163_durable_executor_authoring_command_dispatch_dry_run_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_DRY_RUN_RECORD_SCHEMA = (
    "section_163_durable_executor_authoring_command_dispatch_dry_run_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_DRY_RUN_SUMMARY_SCHEMA = (
    "section_163_durable_executor_authoring_command_dispatch_dry_run_summary_v1"
)
EXPECTED_DISPATCH_SCOPE = (
    "durable_executor_authoring_command_dispatch_dry_run_only"
)

ALLOWED_DISPATCH_DRY_RUN_OPERATIONS = (
    "validate_dispatch_envelope",
    "evaluate_dispatch_readiness",
    "dispatch_dry_run_only",
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
    "dispatch_dry_run_started",
    "dispatch_dry_run_accepted",
    "dispatch_dry_run_admissible",
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
UNSAFE_DISPATCH_RECORD_ACTION_KEYS = (
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
SECTION_162_ZERO_COUNT_KEYS = (
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


def _attempted(value: Any) -> bool:
    return value is True or value == 1


def _sum_truthy(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(contract.get(key, 0) for contract in contracts)


def _proof_flag(record: Dict[str, Any], group: str, key: str) -> bool:
    value = record.get(group, {})
    return isinstance(value, dict) and value.get(key) is True


def build_durable_executor_authoring_command_dispatch_dry_run_contract(
    requested: bool,
    section_162_command_request_route_summary: Dict[str, Any],
    dispatch_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    dispatch_record = dispatch_record or {}
    dispatch_record_present = bool(dispatch_record)
    section_162_route_contract_ready = bool(
        requested
        and section_162_command_request_route_summary.get("status") == "passed"
        and section_162_command_request_route_summary.get(
            "route_contract_defined_count"
        )
        == 1
        and section_162_command_request_route_summary.get(
            "dry_run_route_record_rejected_count"
        )
        == 0
        and section_162_command_request_route_summary.get(
            "unsafe_request_record_count"
        )
        == 0
        and section_162_command_request_route_summary.get(
            "requested_command_forbidden_count"
        )
        == 0
        and section_162_command_request_route_summary.get(
            "requested_command_unknown_count"
        )
        == 0
        and all(
            section_162_command_request_route_summary.get(key) == 0
            for key in SECTION_162_ZERO_COUNT_KEYS
        )
    )
    open_activation_promotion_readiness_chain_satisfied = bool(
        section_162_command_request_route_summary.get(
            "open_activation_promotion_readiness_chain_satisfied_count"
        )
        == 1
    )
    authoring_enable_chain_satisfied = bool(
        section_162_command_request_route_summary.get(
            "authoring_enable_chain_satisfied_count"
        )
        == 1
    )
    durable_release_readiness_chain_reconfirmed = bool(
        section_162_command_request_route_summary.get(
            "durable_release_readiness_chain_reconfirmed_count"
        )
        == 1
    )
    authoring_command_inputs_satisfied = bool(
        section_162_command_request_route_summary.get(
            "authoring_command_inputs_satisfied_count"
        )
        == 1
    )
    authoring_command_record_valid = bool(
        section_162_command_request_route_summary.get(
            "authoring_command_record_valid_count"
        )
        == 1
    )
    dry_run_route_record_valid = bool(
        section_162_command_request_route_summary.get(
            "dry_run_route_record_valid_count"
        )
        == 1
    )
    dry_run_route_admissible = bool(
        section_162_command_request_route_summary.get(
            "dry_run_route_admissible_count"
        )
        == 1
    )
    route_chain_satisfied = bool(
        open_activation_promotion_readiness_chain_satisfied
        and authoring_enable_chain_satisfied
        and durable_release_readiness_chain_reconfirmed
        and authoring_command_inputs_satisfied
        and authoring_command_record_valid
        and dry_run_route_record_valid
        and dry_run_route_admissible
    )
    dispatch_contract_defined = bool(requested and section_162_route_contract_ready)

    record_schema_matches = bool(
        dispatch_record_present
        and dispatch_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_DRY_RUN_RECORD_SCHEMA
    )
    dispatch_scope_matches = bool(
        dispatch_record_present
        and dispatch_record.get("dispatch_scope") == EXPECTED_DISPATCH_SCOPE
    )
    dry_run_only = bool(
        dispatch_record_present and dispatch_record.get("dry_run_only") is True
    )
    dispatch_status_passed = bool(
        dispatch_record_present and dispatch_record.get("status") == "passed"
    )
    operator_reconfirmed_no_live_dispatch = bool(
        dispatch_record_present
        and dispatch_record.get("operator_reconfirmed_no_live_dispatch") is True
    )
    operator_reconfirmed_no_write_execution = bool(
        dispatch_record_present
        and dispatch_record.get("operator_reconfirmed_no_write_execution") is True
    )
    operator_reconfirmed_no_save_delete_rename = bool(
        dispatch_record_present
        and dispatch_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    requested_command = dispatch_record.get("requested_command", "")
    dispatch_operation = dispatch_record.get("dispatch_operation", "")
    target_asset = dispatch_record.get("target_asset", "")
    requested_command_allowed = bool(requested_command in ALLOWED_REQUESTED_COMMANDS)
    requested_command_forbidden = bool(requested_command in FORBIDDEN_REQUESTED_COMMANDS)
    requested_command_unknown = bool(
        dispatch_record_present
        and requested_command not in ALLOWED_REQUESTED_COMMANDS
        and requested_command not in FORBIDDEN_REQUESTED_COMMANDS
    )
    dispatch_operation_allowed = bool(
        dispatch_operation in ALLOWED_DISPATCH_DRY_RUN_OPERATIONS
    )
    dispatch_envelope_target_declared = bool(
        isinstance(target_asset, str) and target_asset.startswith("/Game/")
    )
    route_admission_proof_matches = bool(
        _proof_flag(
            dispatch_record,
            "route_admission_proof",
            "open_activation_promotion_readiness_chain_satisfied",
        )
        and _proof_flag(
            dispatch_record,
            "route_admission_proof",
            "authoring_enable_chain_satisfied",
        )
        and _proof_flag(
            dispatch_record,
            "route_admission_proof",
            "durable_release_readiness_chain_reconfirmed",
        )
        and _proof_flag(
            dispatch_record,
            "route_admission_proof",
            "authoring_command_inputs_satisfied",
        )
        and _proof_flag(
            dispatch_record,
            "route_admission_proof",
            "authoring_command_record_valid",
        )
        and _proof_flag(
            dispatch_record,
            "route_admission_proof",
            "dry_run_route_record_valid",
        )
        and _proof_flag(
            dispatch_record,
            "route_admission_proof",
            "dry_run_route_admissible",
        )
    )
    release_boundary_proof_safe = bool(
        dispatch_record_present
        and dispatch_record.get("release_boundary_proof", {}).get(
            "durable_authoring_enabled"
        )
        is False
        and dispatch_record.get("release_boundary_proof", {}).get(
            "final_durable_release_ready"
        )
        is False
        and dispatch_record.get("release_boundary_proof", {}).get(
            "save_delete_rename_allowed"
        )
        is False
        and dispatch_record.get("release_boundary_proof", {}).get(
            "live_durable_authoring_allowed"
        )
        is False
    )
    unsafe_dispatch_record_count = sum(
        int(_attempted(dispatch_record.get(key)))
        for key in UNSAFE_DISPATCH_RECORD_ACTION_KEYS
    )
    dispatch_dry_run_record_valid = bool(
        dispatch_contract_defined
        and route_chain_satisfied
        and record_schema_matches
        and dispatch_scope_matches
        and dry_run_only
        and dispatch_status_passed
        and operator_reconfirmed_no_live_dispatch
        and operator_reconfirmed_no_write_execution
        and operator_reconfirmed_no_save_delete_rename
        and requested_command_allowed
        and not requested_command_forbidden
        and not requested_command_unknown
        and dispatch_operation_allowed
        and dispatch_envelope_target_declared
        and route_admission_proof_matches
        and release_boundary_proof_safe
        and unsafe_dispatch_record_count == 0
    )
    dispatch_dry_run_record_rejected = bool(
        dispatch_record_present and not dispatch_dry_run_record_valid
    )
    dispatch_dry_run_admissible = bool(dispatch_dry_run_record_valid)

    missing: list[str] = []
    if requested:
        if not section_162_route_contract_ready:
            missing.append("section_162_command_request_route_contract_ready")
        if not open_activation_promotion_readiness_chain_satisfied:
            missing.append("section_162_open_activation_promotion_readiness_chain_satisfied")
        if not authoring_enable_chain_satisfied:
            missing.append("section_162_authoring_enable_chain_satisfied")
        if not durable_release_readiness_chain_reconfirmed:
            missing.append("section_162_durable_release_readiness_chain_reconfirmed")
        if not authoring_command_inputs_satisfied:
            missing.append("section_162_authoring_command_inputs_satisfied")
        if not authoring_command_record_valid:
            missing.append("section_162_authoring_command_record_valid")
        if not dry_run_route_record_valid:
            missing.append("section_162_dry_run_route_record_valid")
        if not dry_run_route_admissible:
            missing.append("section_162_dry_run_route_admissible")
        if not dispatch_record_present:
            missing.append("command_dispatch_dry_run_record_present")
        if not record_schema_matches:
            missing.append("command_dispatch_dry_run_record_schema")
        if not dispatch_scope_matches:
            missing.append("command_dispatch_dry_run_only_scope")
        if not dry_run_only:
            missing.append("dispatch_dry_run_only")
        if not dispatch_status_passed:
            missing.append("command_dispatch_dry_run_status_passed")
        if not operator_reconfirmed_no_live_dispatch:
            missing.append("operator_reconfirmed_no_live_dispatch")
        if not operator_reconfirmed_no_write_execution:
            missing.append("operator_reconfirmed_no_write_execution")
        if not operator_reconfirmed_no_save_delete_rename:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not requested_command_allowed:
            missing.append("allowed_requested_command")
        if not dispatch_operation_allowed:
            missing.append("allowed_dispatch_dry_run_operation")
        if not dispatch_envelope_target_declared:
            missing.append("dispatch_envelope_target_declared")
        if not route_admission_proof_matches:
            missing.append("route_admission_proof_matches")
        if not release_boundary_proof_safe:
            missing.append("release_boundary_proof_safe")

    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_command_dispatch_dry_run",
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_DRY_RUN_SCHEMA,
        "requested": requested,
        "dispatch_contract_defined": dispatch_contract_defined,
        "required_dispatch_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_DRY_RUN_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_dispatch_scope": EXPECTED_DISPATCH_SCOPE if requested else "",
        "allowed_dispatch_dry_run_operations": (
            list(ALLOWED_DISPATCH_DRY_RUN_OPERATIONS) if requested else []
        ),
        "allowed_requested_commands": (
            list(ALLOWED_REQUESTED_COMMANDS) if requested else []
        ),
        "forbidden_requested_commands": (
            list(FORBIDDEN_REQUESTED_COMMANDS) if requested else []
        ),
        "section_162_route_contract_ready": section_162_route_contract_ready,
        "open_activation_promotion_readiness_chain_satisfied": (
            open_activation_promotion_readiness_chain_satisfied
        ),
        "authoring_enable_chain_satisfied": authoring_enable_chain_satisfied,
        "durable_release_readiness_chain_reconfirmed": (
            durable_release_readiness_chain_reconfirmed
        ),
        "authoring_command_inputs_satisfied": authoring_command_inputs_satisfied,
        "authoring_command_record_valid": authoring_command_record_valid,
        "dry_run_route_record_valid": dry_run_route_record_valid,
        "dry_run_route_admissible": dry_run_route_admissible,
        "route_chain_satisfied": route_chain_satisfied,
        "dispatch_dry_run_record_present": dispatch_record_present,
        "record_schema_matches": record_schema_matches,
        "dispatch_scope_matches": dispatch_scope_matches,
        "dry_run_only": dry_run_only,
        "dispatch_status_passed": dispatch_status_passed,
        "operator_reconfirmed_no_live_dispatch": (
            operator_reconfirmed_no_live_dispatch
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
        "dispatch_operation_allowed": dispatch_operation_allowed,
        "dispatch_envelope_target_declared": dispatch_envelope_target_declared,
        "route_admission_proof_matches": route_admission_proof_matches,
        "release_boundary_proof_safe": release_boundary_proof_safe,
        "dispatch_dry_run_record_valid": dispatch_dry_run_record_valid,
        "dispatch_dry_run_record_rejected": dispatch_dry_run_record_rejected,
        "dispatch_dry_run_admissible": dispatch_dry_run_admissible,
        "unsafe_dispatch_record_count": unsafe_dispatch_record_count,
        "missing_dispatch_dry_run_prerequisites": missing,
        "missing_dispatch_dry_run_prerequisite_count": len(missing),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract["dispatch_dry_run_admissible"] = dispatch_dry_run_admissible
    return contract


def summarize_durable_executor_authoring_command_dispatch_dry_runs(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(requested, "dispatch_dry_run_record_rejected")
    unsafe_count = _sum_count(requested, "unsafe_dispatch_record_count")
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "dispatch_contract_defined") == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and _sum_truthy(requested, "requested_command_forbidden") == 0
            and _sum_truthy(requested, "requested_command_unknown") == 0
            and all(
                _sum_truthy(requested, key) == 0
                for key in OUTPUT_ACTION_KEYS
                if key != "dispatch_dry_run_admissible"
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_DRY_RUN_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_command_dispatch_dry_run_count": len(
            requested
        ),
        "dispatch_contract_defined_count": _sum_truthy(
            requested, "dispatch_contract_defined"
        ),
        "section_162_route_contract_ready_count": _sum_truthy(
            requested, "section_162_route_contract_ready"
        ),
        "open_activation_promotion_readiness_chain_satisfied_count": _sum_truthy(
            requested, "open_activation_promotion_readiness_chain_satisfied"
        ),
        "authoring_enable_chain_satisfied_count": _sum_truthy(
            requested, "authoring_enable_chain_satisfied"
        ),
        "durable_release_readiness_chain_reconfirmed_count": _sum_truthy(
            requested, "durable_release_readiness_chain_reconfirmed"
        ),
        "authoring_command_inputs_satisfied_count": _sum_truthy(
            requested, "authoring_command_inputs_satisfied"
        ),
        "authoring_command_record_valid_count": _sum_truthy(
            requested, "authoring_command_record_valid"
        ),
        "dry_run_route_record_valid_count": _sum_truthy(
            requested, "dry_run_route_record_valid"
        ),
        "dry_run_route_admissible_count": _sum_truthy(
            requested, "dry_run_route_admissible"
        ),
        "route_chain_satisfied_count": _sum_truthy(
            requested, "route_chain_satisfied"
        ),
        "dispatch_dry_run_record_present_count": _sum_truthy(
            requested, "dispatch_dry_run_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(
            requested, "record_schema_matches"
        ),
        "dispatch_scope_matches_count": _sum_truthy(
            requested, "dispatch_scope_matches"
        ),
        "dry_run_only_count": _sum_truthy(requested, "dry_run_only"),
        "dispatch_status_passed_count": _sum_truthy(
            requested, "dispatch_status_passed"
        ),
        "operator_reconfirmed_no_live_dispatch_count": _sum_truthy(
            requested, "operator_reconfirmed_no_live_dispatch"
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
        "dispatch_operation_allowed_count": _sum_truthy(
            requested, "dispatch_operation_allowed"
        ),
        "dispatch_envelope_target_declared_count": _sum_truthy(
            requested, "dispatch_envelope_target_declared"
        ),
        "route_admission_proof_matches_count": _sum_truthy(
            requested, "route_admission_proof_matches"
        ),
        "release_boundary_proof_safe_count": _sum_truthy(
            requested, "release_boundary_proof_safe"
        ),
        "dispatch_dry_run_record_valid_count": _sum_truthy(
            requested, "dispatch_dry_run_record_valid"
        ),
        "dispatch_dry_run_record_rejected_count": rejected_count,
        "dispatch_dry_run_admissible_count": _sum_truthy(
            requested, "dispatch_dry_run_admissible"
        ),
        "unsafe_dispatch_record_count": unsafe_count,
        "missing_dispatch_dry_run_prerequisite_count": _sum_count(
            requested, "missing_dispatch_dry_run_prerequisite_count"
        ),
    }
    summary.update(
        {
            f"{key}_count": _sum_truthy(requested, key)
            for key in OUTPUT_ACTION_KEYS
        }
    )
    return summary
