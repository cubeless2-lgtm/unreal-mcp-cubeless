#!/usr/bin/env python
"""
Section 114 durable executor authoring command dispatch contract.

This contract validates a future durable-executor-authoring-command-dispatch-only
record after the durable executor authoring command record is valid. It does not
dispatch or execute live commands, modify assets, save, delete/rename, or cleanup.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_SCHEMA = (
    "section_114_durable_executor_authoring_command_dispatch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_RECORD_SCHEMA = (
    "section_114_durable_executor_authoring_command_dispatch_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_SUMMARY_SCHEMA = (
    "section_114_durable_executor_authoring_command_dispatch_summary_v1"
)
EXPECTED_DISPATCH_SCOPE = "durable_executor_authoring_command_dispatch_only"


OUTPUT_ACTION_KEYS = (
    "durable_authoring_command_dispatch_started",
    "durable_authoring_command_dispatch_accepted",
    "durable_authoring_command_dispatch_allowed",
    "durable_authoring_command_dispatched",
    "durable_authoring_command_execution_contract_started",
    "durable_authoring_command_executed",
    "durable_authoring_enabled",
    "durable_authoring_allowed",
    "code_change_performed",
    "executor_code_modified",
    "unreal_asset_modified",
    "live_bridge_probe_started",
    "asset_write_performed",
    "package_dirty_marked",
    "save_delete_rename_allowed",
    "cleanup_allowed",
    "live_command_dispatched",
    "live_command_executed",
)
UNSAFE_RECORD_ACTION_KEYS = (
    "durable_authoring_command_dispatch_started",
    "durable_authoring_command_dispatch_accepted",
    "durable_authoring_command_dispatch_allowed",
    "durable_authoring_command_dispatched",
    "durable_authoring_command_execution_contract_started",
    "durable_authoring_command_executed",
    "durable_authoring_enabled",
    "durable_authoring_allowed",
    "code_change_performed",
    "executor_code_modified",
    "unreal_asset_modified",
    "live_bridge_probe_started",
    "asset_write_performed",
    "package_dirty_marked",
    "save_asset_executed",
    "delete_asset_authorized",
    "rename_asset_authorized",
    "cleanup_authorized",
    "live_command_dispatch_performed",
    "live_command_dispatched",
    "live_command_execution_authorized",
    "live_command_executed",
)
PREVIOUS_ZERO_COUNT_KEYS = (
    "durable_authoring_command_contract_started_count",
    "durable_authoring_command_contract_accepted_count",
    "durable_authoring_command_allowed_count",
    "durable_authoring_command_dispatched_count",
    "durable_authoring_command_executed_count",
    "durable_authoring_enabled_count",
    "durable_authoring_allowed_count",
    "code_change_performed_count",
    "executor_code_modified_count",
    "unreal_asset_modified_count",
    "live_bridge_probe_started_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
    "save_delete_rename_allowed_count",
    "cleanup_allowed_count",
    "live_command_dispatched_count",
    "live_command_executed_count",
)
ALLOWED_DISPATCH_COUNT_KEYS = (
    "reported_dispatch_gate_count",
    "reported_authoring_command_revalidated_count",
    "reported_no_live_dispatch_performed_count",
    "reported_no_execution_authorized_count",
    "reported_no_asset_write_dispatch_count",
    "reported_no_save_delete_rename_dispatch_count",
)
FORBIDDEN_DISPATCH_COUNT_KEYS = (
    "reported_authoring_command_dispatch_count",
    "reported_authoring_command_execution_count",
    "reported_live_dispatch_count",
    "reported_live_execution_count",
    "reported_code_change_count",
    "reported_executor_code_modified_count",
    "reported_unreal_asset_change_count",
    "reported_live_probe_count",
    "reported_durable_authoring_count",
    "reported_asset_write_count",
    "reported_save_count",
    "reported_delete_rename_count",
    "reported_cleanup_count",
)


def _attempted(value: Any) -> bool:
    return value is True or value == 1


def _count(value: Any) -> int:
    if value is True:
        return 1
    if value in (False, None, ""):
        return 0
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def _sum_truthy(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(contract.get(key, 0) for contract in contracts)


def build_durable_executor_authoring_command_dispatch_contract(
    requested: bool,
    authoring_command_summary: Dict[str, Any],
    dispatch_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    dispatch_record = dispatch_record or {}
    dispatch_record_present = bool(dispatch_record)
    authoring_command_contract_ready = bool(
        requested
        and authoring_command_summary.get("status") == "passed"
        and authoring_command_summary.get("authoring_command_contract_defined_count") == 1
        and authoring_command_summary.get("authoring_command_record_rejected_count") == 0
        and authoring_command_summary.get("unsafe_authoring_command_record_count") == 0
        and authoring_command_summary.get("forbidden_authoring_command_count") == 0
        and authoring_command_summary.get("unknown_authoring_command_count") == 0
        and all(
            authoring_command_summary.get(key) == 0 for key in PREVIOUS_ZERO_COUNT_KEYS
        )
    )
    authoring_command_inputs_satisfied = bool(
        authoring_command_summary.get("authoring_command_inputs_satisfied_count") == 1
    )
    authoring_command_record_valid = bool(
        authoring_command_summary.get("authoring_command_record_valid_count") == 1
    )
    planned_authoring_commands_present = bool(
        authoring_command_summary.get("planned_authoring_command_count", 0) > 0
    )
    allowed_authoring_commands_present = bool(
        authoring_command_summary.get("allowed_authoring_command_count", 0) > 0
    )
    dispatch_inputs_satisfied = bool(
        authoring_command_inputs_satisfied
        and authoring_command_record_valid
        and planned_authoring_commands_present
        and allowed_authoring_commands_present
    )
    record_schema_matches = bool(
        dispatch_record_present
        and dispatch_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_RECORD_SCHEMA
    )
    dispatch_scope_matches = bool(
        dispatch_record_present
        and dispatch_record.get("dispatch_scope") == EXPECTED_DISPATCH_SCOPE
    )
    explicit_dispatch_authorized = bool(
        dispatch_record_present
        and dispatch_record.get(
            "explicit_durable_authoring_command_dispatch_authorized"
        )
        is True
    )
    dispatch_status_passed = bool(
        dispatch_record_present and dispatch_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        dispatch_record_present
        and dispatch_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        dispatch_record_present
        and dispatch_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    allowed_counts = {
        key: _count(dispatch_record.get(key)) for key in ALLOWED_DISPATCH_COUNT_KEYS
    }
    forbidden_counts = {
        key: _count(dispatch_record.get(key)) for key in FORBIDDEN_DISPATCH_COUNT_KEYS
    }
    reported_allowed_dispatch_count = sum(allowed_counts.values())
    reported_forbidden_dispatch_count = sum(forbidden_counts.values())
    allowed_dispatch_observed = bool(
        dispatch_record_present and reported_allowed_dispatch_count > 0
    )
    no_forbidden_dispatch_claims = bool(
        dispatch_record_present and reported_forbidden_dispatch_count == 0
    )
    unsafe_dispatch_record_count = (
        sum(int(_attempted(dispatch_record.get(key))) for key in UNSAFE_RECORD_ACTION_KEYS)
        + reported_forbidden_dispatch_count
    )
    dispatch_contract_defined = bool(requested and authoring_command_contract_ready)
    dispatch_record_valid = bool(
        dispatch_contract_defined
        and dispatch_inputs_satisfied
        and record_schema_matches
        and dispatch_scope_matches
        and explicit_dispatch_authorized
        and dispatch_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_dispatch_observed
        and no_forbidden_dispatch_claims
        and unsafe_dispatch_record_count == 0
    )
    missing = []
    if requested:
        if not authoring_command_inputs_satisfied:
            missing.append("section_113_authoring_command_inputs_satisfied")
        if not authoring_command_record_valid:
            missing.append("section_113_authoring_command_record_valid")
        if not planned_authoring_commands_present:
            missing.append("section_113_planned_authoring_commands_present")
        if not allowed_authoring_commands_present:
            missing.append("section_113_allowed_authoring_commands_present")
        if not dispatch_record_present:
            missing.append("durable_authoring_command_dispatch_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_dispatch_record_schema")
        if not dispatch_scope_matches:
            missing.append("durable_executor_authoring_command_dispatch_only_scope")
        if not explicit_dispatch_authorized:
            missing.append("explicit_durable_authoring_command_dispatch_authorization")
        if not dispatch_status_passed:
            missing.append("durable_authoring_command_dispatch_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_dispatch_observed:
            missing.append("allowed_durable_authoring_command_dispatch_observed")
        if not no_forbidden_dispatch_claims:
            missing.append("no_forbidden_durable_authoring_command_dispatch_claims")
        missing.append("separate_durable_authoring_command_execution_contract")
    dispatch_record_rejected = bool(dispatch_record_present and not dispatch_record_valid)
    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_command_dispatch",
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_SCHEMA,
        "requested": requested,
        "dispatch_contract_defined": dispatch_contract_defined,
        "required_dispatch_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_RECORD_SCHEMA if requested else ""
        ),
        "expected_dispatch_scope": EXPECTED_DISPATCH_SCOPE if requested else "",
        "authoring_command_contract_ready": authoring_command_contract_ready,
        "authoring_command_inputs_satisfied": authoring_command_inputs_satisfied,
        "authoring_command_record_valid": authoring_command_record_valid,
        "planned_authoring_commands_present": planned_authoring_commands_present,
        "allowed_authoring_commands_present": allowed_authoring_commands_present,
        "dispatch_inputs_satisfied": dispatch_inputs_satisfied,
        "dispatch_record_present": dispatch_record_present,
        "record_schema_matches": record_schema_matches,
        "dispatch_scope_matches": dispatch_scope_matches,
        "explicit_dispatch_authorized": explicit_dispatch_authorized,
        "dispatch_status_passed": dispatch_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "reported_allowed_dispatch_count": reported_allowed_dispatch_count,
        "reported_forbidden_dispatch_count": reported_forbidden_dispatch_count,
        "allowed_dispatch_observed": allowed_dispatch_observed,
        "no_forbidden_dispatch_claims": no_forbidden_dispatch_claims,
        "dispatch_record_valid": dispatch_record_valid,
        "dispatch_record_rejected": dispatch_record_rejected,
        "unsafe_dispatch_record_count": unsafe_dispatch_record_count,
        "missing_dispatch_prerequisites": missing,
        "missing_dispatch_prerequisite_count": len(missing),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract.update(allowed_counts)
    contract.update(forbidden_counts)
    return contract


def summarize_durable_executor_authoring_command_dispatches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1 for contract in requested if contract.get("dispatch_record_rejected")
    )
    unsafe_count = _sum_count(requested, "unsafe_dispatch_record_count")
    forbidden_dispatch_count = _sum_count(requested, "reported_forbidden_dispatch_count")
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "dispatch_contract_defined") == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_dispatch_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_DISPATCH_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_command_dispatch_count": len(requested),
        "dispatch_contract_defined_count": _sum_truthy(
            requested, "dispatch_contract_defined"
        ),
        "authoring_command_contract_ready_count": _sum_truthy(
            requested, "authoring_command_contract_ready"
        ),
        "authoring_command_inputs_satisfied_count": _sum_truthy(
            requested, "authoring_command_inputs_satisfied"
        ),
        "authoring_command_record_valid_count": _sum_truthy(
            requested, "authoring_command_record_valid"
        ),
        "planned_authoring_commands_present_count": _sum_truthy(
            requested, "planned_authoring_commands_present"
        ),
        "allowed_authoring_commands_present_count": _sum_truthy(
            requested, "allowed_authoring_commands_present"
        ),
        "dispatch_inputs_satisfied_count": _sum_truthy(
            requested, "dispatch_inputs_satisfied"
        ),
        "dispatch_record_present_count": _sum_truthy(
            requested, "dispatch_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "dispatch_scope_matches_count": _sum_truthy(
            requested, "dispatch_scope_matches"
        ),
        "explicit_dispatch_authorized_count": _sum_truthy(
            requested, "explicit_dispatch_authorized"
        ),
        "dispatch_status_passed_count": _sum_truthy(
            requested, "dispatch_status_passed"
        ),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "allowed_dispatch_observed_count": _sum_truthy(
            requested, "allowed_dispatch_observed"
        ),
        "no_forbidden_dispatch_claims_count": _sum_truthy(
            requested, "no_forbidden_dispatch_claims"
        ),
        "dispatch_record_valid_count": _sum_truthy(requested, "dispatch_record_valid"),
        "dispatch_record_rejected_count": rejected_count,
        "unsafe_dispatch_record_count": unsafe_count,
        "missing_dispatch_prerequisite_count": _sum_count(
            requested, "missing_dispatch_prerequisite_count"
        ),
        "reported_allowed_dispatch_count": _sum_count(
            requested, "reported_allowed_dispatch_count"
        ),
        "reported_forbidden_dispatch_count": forbidden_dispatch_count,
    }
    summary.update({f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS})
    summary.update(
        {key: _sum_count(requested, key) for key in ALLOWED_DISPATCH_COUNT_KEYS}
    )
    summary.update(
        {key: _sum_count(requested, key) for key in FORBIDDEN_DISPATCH_COUNT_KEYS}
    )
    return summary
