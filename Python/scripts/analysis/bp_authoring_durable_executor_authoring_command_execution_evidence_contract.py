#!/usr/bin/env python
"""
Section 116 durable executor authoring command execution evidence contract.

This contract validates a future durable-executor-authoring-command-execution-
evidence-only record after the durable executor authoring command execution
record is valid. It does not execute live commands, modify assets, save,
delete/rename, cleanup, or start command completion.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_SCHEMA = (
    "section_116_durable_executor_authoring_command_execution_evidence_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_RECORD_SCHEMA = (
    "section_116_durable_executor_authoring_command_execution_evidence_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_SUMMARY_SCHEMA = (
    "section_116_durable_executor_authoring_command_execution_evidence_summary_v1"
)
EXPECTED_EVIDENCE_SCOPE = (
    "durable_executor_authoring_command_execution_evidence_only"
)


OUTPUT_ACTION_KEYS = (
    "durable_authoring_command_completion_decision_started",
    "durable_authoring_command_execution_allowed",
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
UNSAFE_EVIDENCE_RECORD_ACTION_KEYS = (
    "durable_authoring_command_completion_decision_started",
    "durable_authoring_command_completion_decision_accepted",
    "durable_authoring_command_execution_allowed",
    "durable_authoring_command_executed",
    "durable_authoring_enabled",
    "durable_authoring_allowed",
    "code_change_performed",
    "executor_code_modified",
    "unreal_asset_modified",
    "live_bridge_probe_started",
    "asset_write_performed",
    "package_dirty_marked",
    "save_asset_attempted",
    "save_asset_authorized",
    "save_asset_executed",
    "delete_asset_attempted",
    "delete_asset_authorized",
    "rename_asset_attempted",
    "rename_asset_authorized",
    "cleanup_attempted",
    "cleanup_authorized",
    "live_command_dispatch_performed",
    "live_command_dispatched",
    "live_command_execution_performed",
    "live_command_executed",
)
PREVIOUS_ZERO_COUNT_KEYS = (
    "durable_authoring_command_execution_started_count",
    "durable_authoring_command_execution_accepted_count",
    "durable_authoring_command_execution_allowed_count",
    "durable_authoring_command_executed_count",
    "durable_authoring_command_execution_evidence_contract_started_count",
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
ALLOWED_EVIDENCE_COUNT_KEYS = (
    "reported_authoring_create_command_count",
    "reported_authoring_compile_command_count",
    "reported_authoring_marker_write_command_count",
    "reported_authoring_marker_readback_command_count",
    "reported_authoring_read_only_exists_check_command_count",
)
FORBIDDEN_EVIDENCE_COUNT_KEYS = (
    "reported_authoring_save_command_count",
    "reported_authoring_delete_rename_command_count",
    "reported_authoring_cleanup_command_count",
    "reported_authoring_duplicate_replace_command_count",
    "reported_authoring_live_dispatch_execution_command_count",
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


def build_durable_executor_authoring_command_execution_evidence_contract(
    requested: bool,
    execution_summary: Dict[str, Any],
    evidence_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    evidence_record = evidence_record or {}
    evidence_record_present = bool(evidence_record)
    execution_contract_ready = bool(
        requested
        and execution_summary.get("status") == "passed"
        and execution_summary.get("execution_contract_defined_count") == 1
        and execution_summary.get("execution_record_rejected_count") == 0
        and execution_summary.get("unsafe_execution_record_count") == 0
        and execution_summary.get("reported_forbidden_execution_count") == 0
        and all(execution_summary.get(key) == 0 for key in PREVIOUS_ZERO_COUNT_KEYS)
    )
    execution_inputs_satisfied = bool(
        execution_summary.get("execution_inputs_satisfied_count") == 1
    )
    execution_record_valid = bool(
        execution_summary.get("execution_record_valid_count") == 1
    )
    planned_authoring_commands_present = bool(
        execution_summary.get("planned_authoring_commands_present_count") == 1
    )
    allowed_authoring_commands_present = bool(
        execution_summary.get("allowed_authoring_commands_present_count") == 1
    )
    allowed_execution_observed = bool(
        execution_summary.get("allowed_execution_observed_count") == 1
    )
    no_forbidden_execution_claims = bool(
        execution_summary.get("no_forbidden_execution_claims_count") == 1
    )
    evidence_inputs_satisfied = bool(
        execution_inputs_satisfied
        and execution_record_valid
        and planned_authoring_commands_present
        and allowed_authoring_commands_present
        and allowed_execution_observed
        and no_forbidden_execution_claims
    )
    record_schema_matches = bool(
        evidence_record_present
        and evidence_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_RECORD_SCHEMA
    )
    evidence_scope_matches = bool(
        evidence_record_present
        and evidence_record.get("evidence_scope") == EXPECTED_EVIDENCE_SCOPE
    )
    explicit_evidence_authorized = bool(
        evidence_record_present
        and evidence_record.get(
            "explicit_durable_authoring_command_execution_evidence_authorized"
        )
        is True
    )
    evidence_status_passed = bool(
        evidence_record_present and evidence_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        evidence_record_present
        and evidence_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        evidence_record_present
        and evidence_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    allowed_counts = {
        key: _count(evidence_record.get(key)) for key in ALLOWED_EVIDENCE_COUNT_KEYS
    }
    forbidden_counts = {
        key: _count(evidence_record.get(key))
        for key in FORBIDDEN_EVIDENCE_COUNT_KEYS
    }
    reported_allowed_evidence_command_count = sum(allowed_counts.values())
    reported_forbidden_evidence_command_count = sum(forbidden_counts.values())
    allowed_evidence_command_observed = bool(
        evidence_record_present and reported_allowed_evidence_command_count > 0
    )
    no_forbidden_evidence_commands = bool(
        evidence_record_present and reported_forbidden_evidence_command_count == 0
    )
    unsafe_evidence_record_count = (
        sum(
            int(_attempted(evidence_record.get(key)))
            for key in UNSAFE_EVIDENCE_RECORD_ACTION_KEYS
        )
        + reported_forbidden_evidence_command_count
    )
    evidence_contract_defined = bool(requested and execution_contract_ready)
    authoring_command_execution_evidence_admitted = bool(
        evidence_contract_defined
        and evidence_inputs_satisfied
        and record_schema_matches
        and evidence_scope_matches
        and explicit_evidence_authorized
        and evidence_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_evidence_command_observed
        and no_forbidden_evidence_commands
        and unsafe_evidence_record_count == 0
    )
    missing: list[str] = []
    if requested:
        if not execution_inputs_satisfied:
            missing.append("section_115_execution_inputs_satisfied")
        if not execution_record_valid:
            missing.append("section_115_execution_record_valid")
        if not planned_authoring_commands_present:
            missing.append("section_115_planned_authoring_commands_present")
        if not allowed_authoring_commands_present:
            missing.append("section_115_allowed_authoring_commands_present")
        if not allowed_execution_observed:
            missing.append("section_115_allowed_execution_observed")
        if not no_forbidden_execution_claims:
            missing.append("section_115_no_forbidden_execution_claims")
        if not evidence_record_present:
            missing.append("durable_authoring_command_execution_evidence_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_execution_evidence_record_schema")
        if not evidence_scope_matches:
            missing.append(
                "durable_executor_authoring_command_execution_evidence_only_scope"
            )
        if not explicit_evidence_authorized:
            missing.append(
                "explicit_durable_authoring_command_execution_evidence_authorization"
            )
        if not evidence_status_passed:
            missing.append("durable_authoring_command_execution_evidence_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_evidence_command_observed:
            missing.append(
                "allowed_durable_authoring_command_execution_evidence_observed"
            )
        if not no_forbidden_evidence_commands:
            missing.append("no_forbidden_durable_authoring_command_execution_evidence")
        missing.append("separate_durable_authoring_command_completion_decision_contract")
    evidence_record_rejected = bool(
        evidence_record_present and not authoring_command_execution_evidence_admitted
    )
    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_command_execution_evidence",
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_SCHEMA,
        "requested": requested,
        "evidence_contract_defined": evidence_contract_defined,
        "required_evidence_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_evidence_scope": EXPECTED_EVIDENCE_SCOPE if requested else "",
        "execution_contract_ready": execution_contract_ready,
        "execution_inputs_satisfied": execution_inputs_satisfied,
        "execution_record_valid": execution_record_valid,
        "planned_authoring_commands_present": planned_authoring_commands_present,
        "allowed_authoring_commands_present": allowed_authoring_commands_present,
        "allowed_execution_observed": allowed_execution_observed,
        "no_forbidden_execution_claims": no_forbidden_execution_claims,
        "evidence_inputs_satisfied": evidence_inputs_satisfied,
        "evidence_record_present": evidence_record_present,
        "record_schema_matches": record_schema_matches,
        "evidence_scope_matches": evidence_scope_matches,
        "explicit_evidence_authorized": explicit_evidence_authorized,
        "evidence_status_passed": evidence_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "reported_allowed_evidence_command_count": (
            reported_allowed_evidence_command_count
        ),
        "reported_forbidden_evidence_command_count": (
            reported_forbidden_evidence_command_count
        ),
        "allowed_evidence_command_observed": allowed_evidence_command_observed,
        "no_forbidden_evidence_commands": no_forbidden_evidence_commands,
        "authoring_command_execution_evidence_admitted": (
            authoring_command_execution_evidence_admitted
        ),
        "evidence_record_rejected": evidence_record_rejected,
        "unsafe_evidence_record_count": unsafe_evidence_record_count,
        "missing_evidence_prerequisites": missing,
        "missing_evidence_prerequisite_count": len(missing),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract.update(allowed_counts)
    contract.update(forbidden_counts)
    return contract


def summarize_durable_executor_authoring_command_execution_evidence(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1 for contract in requested if contract.get("evidence_record_rejected")
    )
    unsafe_count = _sum_count(requested, "unsafe_evidence_record_count")
    forbidden_evidence_count = _sum_count(
        requested, "reported_forbidden_evidence_command_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "evidence_contract_defined") == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_evidence_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_EXECUTION_EVIDENCE_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_command_execution_evidence_count": len(
            requested
        ),
        "evidence_contract_defined_count": _sum_truthy(
            requested, "evidence_contract_defined"
        ),
        "execution_contract_ready_count": _sum_truthy(
            requested, "execution_contract_ready"
        ),
        "execution_inputs_satisfied_count": _sum_truthy(
            requested, "execution_inputs_satisfied"
        ),
        "execution_record_valid_count": _sum_truthy(
            requested, "execution_record_valid"
        ),
        "planned_authoring_commands_present_count": _sum_truthy(
            requested, "planned_authoring_commands_present"
        ),
        "allowed_authoring_commands_present_count": _sum_truthy(
            requested, "allowed_authoring_commands_present"
        ),
        "allowed_execution_observed_count": _sum_truthy(
            requested, "allowed_execution_observed"
        ),
        "no_forbidden_execution_claims_count": _sum_truthy(
            requested, "no_forbidden_execution_claims"
        ),
        "evidence_inputs_satisfied_count": _sum_truthy(
            requested, "evidence_inputs_satisfied"
        ),
        "evidence_record_present_count": _sum_truthy(
            requested, "evidence_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "evidence_scope_matches_count": _sum_truthy(
            requested, "evidence_scope_matches"
        ),
        "explicit_evidence_authorized_count": _sum_truthy(
            requested, "explicit_evidence_authorized"
        ),
        "evidence_status_passed_count": _sum_truthy(
            requested, "evidence_status_passed"
        ),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "allowed_evidence_command_observed_count": _sum_truthy(
            requested, "allowed_evidence_command_observed"
        ),
        "no_forbidden_evidence_commands_count": _sum_truthy(
            requested, "no_forbidden_evidence_commands"
        ),
        "authoring_command_execution_evidence_admitted_count": _sum_truthy(
            requested, "authoring_command_execution_evidence_admitted"
        ),
        "evidence_record_rejected_count": rejected_count,
        "unsafe_evidence_record_count": unsafe_count,
        "missing_evidence_prerequisite_count": _sum_count(
            requested, "missing_evidence_prerequisite_count"
        ),
        "reported_allowed_evidence_command_count": _sum_count(
            requested, "reported_allowed_evidence_command_count"
        ),
        "reported_forbidden_evidence_command_count": forbidden_evidence_count,
    }
    summary.update({f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS})
    summary.update(
        {key: _sum_count(requested, key) for key in ALLOWED_EVIDENCE_COUNT_KEYS}
    )
    summary.update(
        {key: _sum_count(requested, key) for key in FORBIDDEN_EVIDENCE_COUNT_KEYS}
    )
    return summary
