#!/usr/bin/env python
"""
Section 162 durable executor authoring command request dry-run route contract.

This contract defines the next gate after the Section 161 durable executor
authoring command contract. It permits only an offline command request and
dry-run route decision. It does not open durable command execution, dispatch
live commands, modify assets, dirty packages, save, delete/rename, cleanup,
change code, or probe live bridges.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_COMMAND_REQUEST_DRY_RUN_ROUTE_SCHEMA = (
    "section_162_durable_executor_authoring_command_request_dry_run_route_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_REQUEST_DRY_RUN_ROUTE_RECORD_SCHEMA = (
    "section_162_durable_executor_authoring_command_request_dry_run_route_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_REQUEST_DRY_RUN_ROUTE_SUMMARY_SCHEMA = (
    "section_162_durable_executor_authoring_command_request_dry_run_route_summary_v1"
)
EXPECTED_DRY_RUN_ROUTE_SCOPE = (
    "durable_executor_authoring_command_request_dry_run_route_only"
)

ALLOWED_DRY_RUN_OPERATIONS = (
    "validate_command_request_contract",
    "evaluate_durable_authoring_readiness_chain",
    "route_dry_run_only",
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
    "dry_run_route_request_started",
    "dry_run_route_request_accepted",
    "dry_run_route_admissible",
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
UNSAFE_REQUEST_RECORD_ACTION_KEYS = (
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
SECTION_161_ZERO_COUNT_KEYS = (
    "durable_authoring_command_contract_started_count",
    "durable_authoring_command_contract_accepted_count",
    "durable_authoring_command_allowed_count",
    "durable_executor_command_path_opened_count",
    "durable_executor_command_path_allowed_count",
    "durable_authoring_command_dispatched_count",
    "durable_authoring_command_executed_count",
    "durable_authoring_enabled_count",
    "durable_authoring_allowed_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
    "code_change_performed_count",
    "executor_code_modified_count",
    "unreal_asset_modified_count",
    "live_bridge_probe_started_count",
    "save_delete_rename_allowed_count",
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


def build_durable_executor_authoring_command_request_dry_run_route_contract(
    requested: bool,
    section_161_authoring_command_summary: Dict[str, Any],
    request_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    request_record = request_record or {}
    request_record_present = bool(request_record)
    section_161_command_contract_ready = bool(
        requested
        and section_161_authoring_command_summary.get("status") == "passed"
        and section_161_authoring_command_summary.get(
            "authoring_command_contract_defined_count"
        )
        == 1
        and section_161_authoring_command_summary.get(
            "authoring_command_record_rejected_count"
        )
        == 0
        and section_161_authoring_command_summary.get(
            "unsafe_authoring_command_record_count"
        )
        == 0
        and section_161_authoring_command_summary.get(
            "forbidden_authoring_command_count"
        )
        == 0
        and section_161_authoring_command_summary.get(
            "unknown_authoring_command_count"
        )
        == 0
        and all(
            section_161_authoring_command_summary.get(key) == 0
            for key in SECTION_161_ZERO_COUNT_KEYS
        )
    )
    open_activation_promotion_readiness_chain_satisfied = bool(
        section_161_authoring_command_summary.get(
            "open_activation_promotion_readiness_chain_satisfied_count"
        )
        == 1
    )
    authoring_enable_chain_satisfied = bool(
        section_161_authoring_command_summary.get(
            "authoring_enable_chain_satisfied_count"
        )
        == 1
    )
    durable_release_readiness_chain_reconfirmed = bool(
        section_161_authoring_command_summary.get(
            "durable_release_readiness_chain_reconfirmed_count"
        )
        == 1
    )
    authoring_command_inputs_satisfied = bool(
        section_161_authoring_command_summary.get(
            "authoring_command_inputs_satisfied_count"
        )
        == 1
    )
    authoring_command_record_valid = bool(
        section_161_authoring_command_summary.get(
            "authoring_command_record_valid_count"
        )
        == 1
    )
    readiness_chain_satisfied = bool(
        open_activation_promotion_readiness_chain_satisfied
        and authoring_enable_chain_satisfied
        and durable_release_readiness_chain_reconfirmed
        and authoring_command_inputs_satisfied
        and authoring_command_record_valid
    )
    route_contract_defined = bool(requested and section_161_command_contract_ready)

    record_schema_matches = bool(
        request_record_present
        and request_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_COMMAND_REQUEST_DRY_RUN_ROUTE_RECORD_SCHEMA
    )
    route_scope_matches = bool(
        request_record_present
        and request_record.get("route_scope") == EXPECTED_DRY_RUN_ROUTE_SCOPE
    )
    dry_run_only = bool(
        request_record_present and request_record.get("dry_run_only") is True
    )
    route_status_passed = bool(
        request_record_present and request_record.get("status") == "passed"
    )
    operator_reconfirmed_no_write_execution = bool(
        request_record_present
        and request_record.get("operator_reconfirmed_no_write_execution") is True
    )
    operator_reconfirmed_no_save_delete_rename = bool(
        request_record_present
        and request_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    requested_command = request_record.get("requested_command", "")
    dry_run_operation = request_record.get("dry_run_operation", "")
    target_asset = request_record.get("target_asset", "")
    requested_command_allowed = bool(requested_command in ALLOWED_REQUESTED_COMMANDS)
    requested_command_forbidden = bool(requested_command in FORBIDDEN_REQUESTED_COMMANDS)
    requested_command_unknown = bool(
        request_record_present
        and requested_command not in ALLOWED_REQUESTED_COMMANDS
        and requested_command not in FORBIDDEN_REQUESTED_COMMANDS
    )
    dry_run_operation_allowed = bool(dry_run_operation in ALLOWED_DRY_RUN_OPERATIONS)
    target_asset_declared = bool(
        isinstance(target_asset, str) and target_asset.startswith("/Game/")
    )
    readiness_proof_matches = bool(
        _proof_flag(
            request_record,
            "readiness_proof",
            "open_activation_promotion_readiness_chain_satisfied",
        )
        and _proof_flag(
            request_record, "readiness_proof", "authoring_enable_chain_satisfied"
        )
        and _proof_flag(
            request_record,
            "readiness_proof",
            "durable_release_readiness_chain_reconfirmed",
        )
        and _proof_flag(
            request_record, "readiness_proof", "authoring_command_inputs_satisfied"
        )
        and _proof_flag(
            request_record, "readiness_proof", "authoring_command_record_valid"
        )
    )
    release_boundary_proof_safe = bool(
        request_record_present
        and request_record.get("release_boundary_proof", {}).get(
            "durable_authoring_enabled"
        )
        is False
        and request_record.get("release_boundary_proof", {}).get(
            "final_durable_release_ready"
        )
        is False
        and request_record.get("release_boundary_proof", {}).get(
            "save_delete_rename_allowed"
        )
        is False
        and request_record.get("release_boundary_proof", {}).get(
            "live_durable_authoring_allowed"
        )
        is False
    )
    unsafe_request_record_count = sum(
        int(_attempted(request_record.get(key)))
        for key in UNSAFE_REQUEST_RECORD_ACTION_KEYS
    )
    dry_run_route_record_valid = bool(
        route_contract_defined
        and readiness_chain_satisfied
        and record_schema_matches
        and route_scope_matches
        and dry_run_only
        and route_status_passed
        and operator_reconfirmed_no_write_execution
        and operator_reconfirmed_no_save_delete_rename
        and requested_command_allowed
        and not requested_command_forbidden
        and not requested_command_unknown
        and dry_run_operation_allowed
        and target_asset_declared
        and readiness_proof_matches
        and release_boundary_proof_safe
        and unsafe_request_record_count == 0
    )
    dry_run_route_record_rejected = bool(
        request_record_present and not dry_run_route_record_valid
    )
    dry_run_route_admissible = bool(dry_run_route_record_valid)

    missing: list[str] = []
    if requested:
        if not section_161_command_contract_ready:
            missing.append("section_161_authoring_command_contract_ready")
        if not open_activation_promotion_readiness_chain_satisfied:
            missing.append("open_activation_promotion_readiness_chain_satisfied")
        if not authoring_enable_chain_satisfied:
            missing.append("authoring_enable_chain_satisfied")
        if not durable_release_readiness_chain_reconfirmed:
            missing.append("durable_release_readiness_chain_reconfirmed")
        if not authoring_command_inputs_satisfied:
            missing.append("authoring_command_inputs_satisfied")
        if not authoring_command_record_valid:
            missing.append("authoring_command_record_valid")
        if not request_record_present:
            missing.append("command_request_dry_run_route_record_present")
        if not record_schema_matches:
            missing.append("command_request_dry_run_route_record_schema")
        if not route_scope_matches:
            missing.append("command_request_dry_run_route_only_scope")
        if not dry_run_only:
            missing.append("dry_run_only")
        if not route_status_passed:
            missing.append("command_request_dry_run_route_status_passed")
        if not operator_reconfirmed_no_write_execution:
            missing.append("operator_reconfirmed_no_write_execution")
        if not operator_reconfirmed_no_save_delete_rename:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not requested_command_allowed:
            missing.append("allowed_requested_command")
        if not dry_run_operation_allowed:
            missing.append("allowed_dry_run_operation")
        if not target_asset_declared:
            missing.append("target_asset_declared")
        if not readiness_proof_matches:
            missing.append("readiness_proof_matches")
        if not release_boundary_proof_safe:
            missing.append("release_boundary_proof_safe")

    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_command_request_dry_run_route",
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_REQUEST_DRY_RUN_ROUTE_SCHEMA,
        "requested": requested,
        "route_contract_defined": route_contract_defined,
        "required_route_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_COMMAND_REQUEST_DRY_RUN_ROUTE_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_route_scope": EXPECTED_DRY_RUN_ROUTE_SCOPE if requested else "",
        "allowed_dry_run_operations": (
            list(ALLOWED_DRY_RUN_OPERATIONS) if requested else []
        ),
        "allowed_requested_commands": (
            list(ALLOWED_REQUESTED_COMMANDS) if requested else []
        ),
        "forbidden_requested_commands": (
            list(FORBIDDEN_REQUESTED_COMMANDS) if requested else []
        ),
        "section_161_command_contract_ready": section_161_command_contract_ready,
        "open_activation_promotion_readiness_chain_satisfied": (
            open_activation_promotion_readiness_chain_satisfied
        ),
        "authoring_enable_chain_satisfied": authoring_enable_chain_satisfied,
        "durable_release_readiness_chain_reconfirmed": (
            durable_release_readiness_chain_reconfirmed
        ),
        "authoring_command_inputs_satisfied": authoring_command_inputs_satisfied,
        "authoring_command_record_valid": authoring_command_record_valid,
        "readiness_chain_satisfied": readiness_chain_satisfied,
        "dry_run_route_record_present": request_record_present,
        "record_schema_matches": record_schema_matches,
        "route_scope_matches": route_scope_matches,
        "dry_run_only": dry_run_only,
        "route_status_passed": route_status_passed,
        "operator_reconfirmed_no_write_execution": (
            operator_reconfirmed_no_write_execution
        ),
        "operator_reconfirmed_no_save_delete_rename": (
            operator_reconfirmed_no_save_delete_rename
        ),
        "requested_command_allowed": requested_command_allowed,
        "requested_command_forbidden": requested_command_forbidden,
        "requested_command_unknown": requested_command_unknown,
        "dry_run_operation_allowed": dry_run_operation_allowed,
        "target_asset_declared": target_asset_declared,
        "readiness_proof_matches": readiness_proof_matches,
        "release_boundary_proof_safe": release_boundary_proof_safe,
        "dry_run_route_record_valid": dry_run_route_record_valid,
        "dry_run_route_record_rejected": dry_run_route_record_rejected,
        "dry_run_route_admissible": dry_run_route_admissible,
        "unsafe_request_record_count": unsafe_request_record_count,
        "missing_dry_run_route_prerequisites": missing,
        "missing_dry_run_route_prerequisite_count": len(missing),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract["dry_run_route_admissible"] = dry_run_route_admissible
    return contract


def summarize_durable_executor_authoring_command_request_dry_run_routes(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(requested, "dry_run_route_record_rejected")
    unsafe_count = _sum_count(requested, "unsafe_request_record_count")
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "route_contract_defined") == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and _sum_truthy(requested, "requested_command_forbidden") == 0
            and _sum_truthy(requested, "requested_command_unknown") == 0
            and all(
                _sum_truthy(requested, key) == 0
                for key in OUTPUT_ACTION_KEYS
                if key != "dry_run_route_admissible"
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_REQUEST_DRY_RUN_ROUTE_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_command_request_dry_run_route_count": len(
            requested
        ),
        "route_contract_defined_count": _sum_truthy(
            requested, "route_contract_defined"
        ),
        "section_161_command_contract_ready_count": _sum_truthy(
            requested, "section_161_command_contract_ready"
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
        "readiness_chain_satisfied_count": _sum_truthy(
            requested, "readiness_chain_satisfied"
        ),
        "dry_run_route_record_present_count": _sum_truthy(
            requested, "dry_run_route_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(
            requested, "record_schema_matches"
        ),
        "route_scope_matches_count": _sum_truthy(requested, "route_scope_matches"),
        "dry_run_only_count": _sum_truthy(requested, "dry_run_only"),
        "route_status_passed_count": _sum_truthy(requested, "route_status_passed"),
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
        "dry_run_operation_allowed_count": _sum_truthy(
            requested, "dry_run_operation_allowed"
        ),
        "target_asset_declared_count": _sum_truthy(
            requested, "target_asset_declared"
        ),
        "readiness_proof_matches_count": _sum_truthy(
            requested, "readiness_proof_matches"
        ),
        "release_boundary_proof_safe_count": _sum_truthy(
            requested, "release_boundary_proof_safe"
        ),
        "dry_run_route_record_valid_count": _sum_truthy(
            requested, "dry_run_route_record_valid"
        ),
        "dry_run_route_record_rejected_count": rejected_count,
        "dry_run_route_admissible_count": _sum_truthy(
            requested, "dry_run_route_admissible"
        ),
        "unsafe_request_record_count": unsafe_count,
        "missing_dry_run_route_prerequisite_count": _sum_count(
            requested, "missing_dry_run_route_prerequisite_count"
        ),
    }
    summary.update(
        {
            f"{key}_count": _sum_truthy(requested, key)
            for key in OUTPUT_ACTION_KEYS
        }
    )
    return summary
