#!/usr/bin/env python
"""
Section 115 durable executor authoring command execution contract.

This contract validates a future durable-executor-authoring-command-execution-only
record after the durable executor authoring command dispatch record is valid. It
does not execute live commands, admit evidence, modify assets, save, delete/rename,
or cleanup.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_SCHEMA = (
    "section_115_durable_executor_authoring_command_execution_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_RECORD_SCHEMA = (
    "section_115_durable_executor_authoring_command_execution_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_SUMMARY_SCHEMA = (
    "section_115_durable_executor_authoring_command_execution_summary_v1"
)
EXPECTED_EXECUTION_SCOPE = "durable_executor_authoring_command_execution_only"


OUTPUT_ACTION_KEYS = (
    "durable_authoring_command_execution_started",
    "durable_authoring_command_execution_accepted",
    "durable_authoring_command_execution_allowed",
    "durable_authoring_command_executed",
    "durable_authoring_command_execution_evidence_contract_started",
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
    "durable_authoring_command_execution_started",
    "durable_authoring_command_execution_accepted",
    "durable_authoring_command_execution_allowed",
    "durable_authoring_command_executed",
    "durable_authoring_command_execution_evidence_contract_started",
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
    "live_command_execution_performed",
    "live_command_executed",
)
PREVIOUS_ZERO_COUNT_KEYS = (
    "durable_authoring_command_dispatch_started_count",
    "durable_authoring_command_dispatch_accepted_count",
    "durable_authoring_command_dispatch_allowed_count",
    "durable_authoring_command_dispatched_count",
    "durable_authoring_command_execution_contract_started_count",
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
ALLOWED_EXECUTION_COUNT_KEYS = (
    "reported_execution_gate_count",
    "reported_dispatch_revalidated_count",
    "reported_no_live_execution_performed_count",
    "reported_no_execution_evidence_admitted_count",
    "reported_no_asset_write_execution_count",
    "reported_no_save_delete_rename_execution_count",
)
FORBIDDEN_EXECUTION_COUNT_KEYS = (
    "reported_authoring_command_execution_count",
    "reported_execution_evidence_count",
    "reported_live_execution_count",
    "reported_live_dispatch_count",
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


def build_durable_executor_authoring_command_execution_contract(
    requested: bool,
    dispatch_summary: Dict[str, Any],
    execution_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    execution_record = execution_record or {}
    execution_record_present = bool(execution_record)
    dispatch_contract_ready = bool(
        requested
        and dispatch_summary.get("status") == "passed"
        and dispatch_summary.get("dispatch_contract_defined_count") == 1
        and dispatch_summary.get("dispatch_record_rejected_count") == 0
        and dispatch_summary.get("unsafe_dispatch_record_count") == 0
        and dispatch_summary.get("reported_forbidden_dispatch_count") == 0
        and all(dispatch_summary.get(key) == 0 for key in PREVIOUS_ZERO_COUNT_KEYS)
    )
    dispatch_inputs_satisfied = bool(
        dispatch_summary.get("dispatch_inputs_satisfied_count") == 1
    )
    dispatch_record_valid = bool(
        dispatch_summary.get("dispatch_record_valid_count") == 1
    )
    planned_authoring_commands_present = bool(
        dispatch_summary.get("planned_authoring_commands_present_count") == 1
    )
    allowed_authoring_commands_present = bool(
        dispatch_summary.get("allowed_authoring_commands_present_count") == 1
    )
    allowed_dispatch_observed = bool(
        dispatch_summary.get("allowed_dispatch_observed_count") == 1
    )
    no_forbidden_dispatch_claims = bool(
        dispatch_summary.get("no_forbidden_dispatch_claims_count") == 1
    )
    execution_inputs_satisfied = bool(
        dispatch_inputs_satisfied
        and dispatch_record_valid
        and planned_authoring_commands_present
        and allowed_authoring_commands_present
        and allowed_dispatch_observed
        and no_forbidden_dispatch_claims
    )
    record_schema_matches = bool(
        execution_record_present
        and execution_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_RECORD_SCHEMA
    )
    execution_scope_matches = bool(
        execution_record_present
        and execution_record.get("execution_scope") == EXPECTED_EXECUTION_SCOPE
    )
    explicit_execution_authorized = bool(
        execution_record_present
        and execution_record.get(
            "explicit_durable_authoring_command_execution_authorized"
        )
        is True
    )
    execution_status_passed = bool(
        execution_record_present and execution_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        execution_record_present
        and execution_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        execution_record_present
        and execution_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    allowed_counts = {
        key: _count(execution_record.get(key)) for key in ALLOWED_EXECUTION_COUNT_KEYS
    }
    forbidden_counts = {
        key: _count(execution_record.get(key))
        for key in FORBIDDEN_EXECUTION_COUNT_KEYS
    }
    reported_allowed_execution_count = sum(allowed_counts.values())
    reported_forbidden_execution_count = sum(forbidden_counts.values())
    allowed_execution_observed = bool(
        execution_record_present and reported_allowed_execution_count > 0
    )
    no_forbidden_execution_claims = bool(
        execution_record_present and reported_forbidden_execution_count == 0
    )
    unsafe_execution_record_count = (
        sum(int(_attempted(execution_record.get(key))) for key in UNSAFE_RECORD_ACTION_KEYS)
        + reported_forbidden_execution_count
    )
    execution_contract_defined = bool(requested and dispatch_contract_ready)
    execution_record_valid = bool(
        execution_contract_defined
        and execution_inputs_satisfied
        and record_schema_matches
        and execution_scope_matches
        and explicit_execution_authorized
        and execution_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_execution_observed
        and no_forbidden_execution_claims
        and unsafe_execution_record_count == 0
    )
    missing = []
    if requested:
        if not dispatch_inputs_satisfied:
            missing.append("section_114_dispatch_inputs_satisfied")
        if not dispatch_record_valid:
            missing.append("section_114_dispatch_record_valid")
        if not planned_authoring_commands_present:
            missing.append("section_114_planned_authoring_commands_present")
        if not allowed_authoring_commands_present:
            missing.append("section_114_allowed_authoring_commands_present")
        if not allowed_dispatch_observed:
            missing.append("section_114_allowed_dispatch_observed")
        if not no_forbidden_dispatch_claims:
            missing.append("section_114_no_forbidden_dispatch_claims")
        if not execution_record_present:
            missing.append("durable_authoring_command_execution_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_execution_record_schema")
        if not execution_scope_matches:
            missing.append("durable_executor_authoring_command_execution_only_scope")
        if not explicit_execution_authorized:
            missing.append("explicit_durable_authoring_command_execution_authorization")
        if not execution_status_passed:
            missing.append("durable_authoring_command_execution_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_execution_observed:
            missing.append("allowed_durable_authoring_command_execution_observed")
        if not no_forbidden_execution_claims:
            missing.append("no_forbidden_durable_authoring_command_execution_claims")
        missing.append("separate_durable_authoring_command_execution_evidence_contract")
    execution_record_rejected = bool(
        execution_record_present and not execution_record_valid
    )
    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_command_execution",
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_SCHEMA,
        "requested": requested,
        "execution_contract_defined": execution_contract_defined,
        "required_execution_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_execution_scope": EXPECTED_EXECUTION_SCOPE if requested else "",
        "dispatch_contract_ready": dispatch_contract_ready,
        "dispatch_inputs_satisfied": dispatch_inputs_satisfied,
        "dispatch_record_valid": dispatch_record_valid,
        "planned_authoring_commands_present": planned_authoring_commands_present,
        "allowed_authoring_commands_present": allowed_authoring_commands_present,
        "allowed_dispatch_observed": allowed_dispatch_observed,
        "no_forbidden_dispatch_claims": no_forbidden_dispatch_claims,
        "execution_inputs_satisfied": execution_inputs_satisfied,
        "execution_record_present": execution_record_present,
        "record_schema_matches": record_schema_matches,
        "execution_scope_matches": execution_scope_matches,
        "explicit_execution_authorized": explicit_execution_authorized,
        "execution_status_passed": execution_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "reported_allowed_execution_count": reported_allowed_execution_count,
        "reported_forbidden_execution_count": reported_forbidden_execution_count,
        "allowed_execution_observed": allowed_execution_observed,
        "no_forbidden_execution_claims": no_forbidden_execution_claims,
        "execution_record_valid": execution_record_valid,
        "execution_record_rejected": execution_record_rejected,
        "unsafe_execution_record_count": unsafe_execution_record_count,
        "missing_execution_prerequisites": missing,
        "missing_execution_prerequisite_count": len(missing),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract.update(allowed_counts)
    contract.update(forbidden_counts)
    return contract


def summarize_durable_executor_authoring_command_executions(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1 for contract in requested if contract.get("execution_record_rejected")
    )
    unsafe_count = _sum_count(requested, "unsafe_execution_record_count")
    forbidden_execution_count = _sum_count(
        requested, "reported_forbidden_execution_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "execution_contract_defined") == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_execution_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_command_execution_count": len(requested),
        "execution_contract_defined_count": _sum_truthy(
            requested, "execution_contract_defined"
        ),
        "dispatch_contract_ready_count": _sum_truthy(
            requested, "dispatch_contract_ready"
        ),
        "dispatch_inputs_satisfied_count": _sum_truthy(
            requested, "dispatch_inputs_satisfied"
        ),
        "dispatch_record_valid_count": _sum_truthy(requested, "dispatch_record_valid"),
        "planned_authoring_commands_present_count": _sum_truthy(
            requested, "planned_authoring_commands_present"
        ),
        "allowed_authoring_commands_present_count": _sum_truthy(
            requested, "allowed_authoring_commands_present"
        ),
        "allowed_dispatch_observed_count": _sum_truthy(
            requested, "allowed_dispatch_observed"
        ),
        "no_forbidden_dispatch_claims_count": _sum_truthy(
            requested, "no_forbidden_dispatch_claims"
        ),
        "execution_inputs_satisfied_count": _sum_truthy(
            requested, "execution_inputs_satisfied"
        ),
        "execution_record_present_count": _sum_truthy(
            requested, "execution_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "execution_scope_matches_count": _sum_truthy(
            requested, "execution_scope_matches"
        ),
        "explicit_execution_authorized_count": _sum_truthy(
            requested, "explicit_execution_authorized"
        ),
        "execution_status_passed_count": _sum_truthy(
            requested, "execution_status_passed"
        ),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "allowed_execution_observed_count": _sum_truthy(
            requested, "allowed_execution_observed"
        ),
        "no_forbidden_execution_claims_count": _sum_truthy(
            requested, "no_forbidden_execution_claims"
        ),
        "execution_record_valid_count": _sum_truthy(requested, "execution_record_valid"),
        "execution_record_rejected_count": rejected_count,
        "unsafe_execution_record_count": unsafe_count,
        "missing_execution_prerequisite_count": _sum_count(
            requested, "missing_execution_prerequisite_count"
        ),
        "reported_allowed_execution_count": _sum_count(
            requested, "reported_allowed_execution_count"
        ),
        "reported_forbidden_execution_count": forbidden_execution_count,
    }
    summary.update({f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS})
    summary.update(
        {key: _sum_count(requested, key) for key in ALLOWED_EXECUTION_COUNT_KEYS}
    )
    summary.update(
        {key: _sum_count(requested, key) for key in FORBIDDEN_EXECUTION_COUNT_KEYS}
    )
    return summary
