#!/usr/bin/env python
"""
Section 117 durable executor authoring command completion decision contract.

This contract defines the scoped decision record required after future durable
executor authoring command execution evidence is admitted. It does not complete
commands, modify assets, save, delete/rename, cleanup, or start completion
application.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_DECISION_SCHEMA = (
    "section_117_durable_executor_authoring_command_completion_decision_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_DECISION_RECORD_SCHEMA = (
    "section_117_durable_executor_authoring_command_completion_decision_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_DECISION_SUMMARY_SCHEMA = (
    "section_117_durable_executor_authoring_command_completion_decision_summary_v1"
)
EXPECTED_COMPLETION_SCOPE = (
    "durable_executor_authoring_command_completion_decision_only"
)


OUTPUT_ACTION_KEYS = (
    "durable_authoring_command_completion_allowed",
    "durable_authoring_command_completed",
    "durable_authoring_command_completion_application_started",
    "durable_authoring_command_dispatch_allowed",
    "durable_authoring_command_dispatched",
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
UNSAFE_COMPLETION_DECISION_RECORD_ACTION_KEYS = (
    "durable_authoring_command_completion_allowed",
    "durable_authoring_command_completed",
    "durable_authoring_command_completion_application_started",
    "durable_authoring_command_dispatch_allowed",
    "durable_authoring_command_dispatched",
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
    "save_asset_authorized",
    "save_asset_executed",
    "delete_asset_authorized",
    "rename_asset_authorized",
    "cleanup_authorized",
    "live_command_dispatch_authorized",
    "live_command_dispatch_performed",
    "live_command_dispatched",
    "live_command_execution_authorized",
    "live_command_execution_performed",
    "live_command_executed",
)
PREVIOUS_ZERO_COUNT_KEYS = (
    "durable_authoring_command_completion_decision_started_count",
    "durable_authoring_command_execution_allowed_count",
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


def _attempted(value: Any) -> bool:
    return value is True or value == 1


def _sum_truthy(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(contract.get(key, 0) for contract in contracts)


def build_durable_executor_authoring_command_completion_decision_contract(
    requested: bool,
    evidence_summary: Dict[str, Any],
    completion_decision_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    completion_decision_record = completion_decision_record or {}
    decision_record_present = bool(completion_decision_record)
    evidence_contract_ready = bool(
        requested
        and evidence_summary.get("status") == "passed"
        and evidence_summary.get("evidence_contract_defined_count") == 1
        and evidence_summary.get("evidence_record_rejected_count") == 0
        and evidence_summary.get("unsafe_evidence_record_count") == 0
        and evidence_summary.get("reported_forbidden_evidence_command_count") == 0
        and all(evidence_summary.get(key) == 0 for key in PREVIOUS_ZERO_COUNT_KEYS)
    )
    authoring_command_execution_evidence_admitted = bool(
        evidence_summary.get("authoring_command_execution_evidence_admitted_count")
        == 1
    )
    allowed_evidence_command_observed = bool(
        evidence_summary.get("allowed_evidence_command_observed_count") == 1
    )
    no_forbidden_evidence_commands = bool(
        evidence_summary.get("no_forbidden_evidence_commands_count") == 1
    )
    evidence_ready_for_completion = bool(
        authoring_command_execution_evidence_admitted
        and allowed_evidence_command_observed
        and no_forbidden_evidence_commands
    )
    record_schema_matches = bool(
        decision_record_present
        and completion_decision_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_DECISION_RECORD_SCHEMA
    )
    completion_scope_matches = bool(
        decision_record_present
        and completion_decision_record.get("completion_scope")
        == EXPECTED_COMPLETION_SCOPE
    )
    explicit_completion_decision_authorized = bool(
        decision_record_present
        and completion_decision_record.get(
            "explicit_durable_authoring_command_completion_decision_authorized"
        )
        is True
    )
    completion_decision_status_passed = bool(
        decision_record_present
        and completion_decision_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        decision_record_present
        and completion_decision_record.get("operator_reconfirmed_no_save_delete_rename")
        is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        decision_record_present
        and completion_decision_record.get("explicit_durable_mvp_request_reconfirmed")
        is True
    )
    reported_allowed_evidence_command_count = evidence_summary.get(
        "reported_allowed_evidence_command_count",
        0,
    )
    reported_forbidden_evidence_command_count = evidence_summary.get(
        "reported_forbidden_evidence_command_count",
        0,
    )
    unsafe_completion_decision_record_count = sum(
        int(_attempted(completion_decision_record.get(key)))
        for key in UNSAFE_COMPLETION_DECISION_RECORD_ACTION_KEYS
    )
    completion_decision_contract_defined = bool(requested and evidence_contract_ready)
    completion_decision_record_valid = bool(
        completion_decision_contract_defined
        and evidence_ready_for_completion
        and record_schema_matches
        and completion_scope_matches
        and explicit_completion_decision_authorized
        and completion_decision_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and unsafe_completion_decision_record_count == 0
    )
    missing: list[str] = []
    if requested:
        if not authoring_command_execution_evidence_admitted:
            missing.append("section_116_authoring_command_execution_evidence_admitted")
        if not allowed_evidence_command_observed:
            missing.append("section_116_allowed_evidence_command_observed")
        if not no_forbidden_evidence_commands:
            missing.append("section_116_no_forbidden_evidence_commands")
        if not decision_record_present:
            missing.append("durable_authoring_command_completion_decision_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_completion_decision_record_schema")
        if not completion_scope_matches:
            missing.append(
                "durable_executor_authoring_command_completion_decision_only_scope"
            )
        if not explicit_completion_decision_authorized:
            missing.append(
                "explicit_durable_authoring_command_completion_decision_authorization"
            )
        if not completion_decision_status_passed:
            missing.append("durable_authoring_command_completion_decision_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        missing.append("separate_durable_authoring_command_completion_application_contract")
    completion_decision_record_rejected = bool(
        decision_record_present and not completion_decision_record_valid
    )
    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_command_completion_decision",
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_DECISION_SCHEMA,
        "requested": requested,
        "completion_decision_contract_defined": (
            completion_decision_contract_defined
        ),
        "required_completion_decision_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_DECISION_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_completion_scope": EXPECTED_COMPLETION_SCOPE if requested else "",
        "evidence_contract_ready": evidence_contract_ready,
        "authoring_command_execution_evidence_admitted": (
            authoring_command_execution_evidence_admitted
        ),
        "allowed_evidence_command_observed": allowed_evidence_command_observed,
        "no_forbidden_evidence_commands": no_forbidden_evidence_commands,
        "evidence_ready_for_completion": evidence_ready_for_completion,
        "decision_record_present": decision_record_present,
        "record_schema_matches": record_schema_matches,
        "completion_scope_matches": completion_scope_matches,
        "explicit_completion_decision_authorized": (
            explicit_completion_decision_authorized
        ),
        "completion_decision_status_passed": completion_decision_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "completion_decision_record_valid": completion_decision_record_valid,
        "completion_decision_record_rejected": completion_decision_record_rejected,
        "unsafe_completion_decision_record_count": (
            unsafe_completion_decision_record_count
        ),
        "missing_completion_prerequisites": missing,
        "missing_completion_prerequisite_count": len(missing),
        "reported_allowed_evidence_command_count": (
            reported_allowed_evidence_command_count
        ),
        "reported_forbidden_evidence_command_count": (
            reported_forbidden_evidence_command_count
        ),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    return contract


def summarize_durable_executor_authoring_command_completion_decisions(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1
        for contract in requested
        if contract.get("completion_decision_record_rejected")
    )
    unsafe_count = _sum_count(requested, "unsafe_completion_decision_record_count")
    forbidden_evidence_count = _sum_count(
        requested, "reported_forbidden_evidence_command_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "completion_decision_contract_defined")
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_evidence_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_DECISION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_command_completion_decision_count": len(
            requested
        ),
        "completion_decision_contract_defined_count": _sum_truthy(
            requested, "completion_decision_contract_defined"
        ),
        "evidence_contract_ready_count": _sum_truthy(
            requested, "evidence_contract_ready"
        ),
        "authoring_command_execution_evidence_admitted_count": _sum_truthy(
            requested, "authoring_command_execution_evidence_admitted"
        ),
        "allowed_evidence_command_observed_count": _sum_truthy(
            requested, "allowed_evidence_command_observed"
        ),
        "no_forbidden_evidence_commands_count": _sum_truthy(
            requested, "no_forbidden_evidence_commands"
        ),
        "evidence_ready_for_completion_count": _sum_truthy(
            requested, "evidence_ready_for_completion"
        ),
        "decision_record_present_count": _sum_truthy(
            requested, "decision_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "completion_scope_matches_count": _sum_truthy(
            requested, "completion_scope_matches"
        ),
        "explicit_completion_decision_authorized_count": _sum_truthy(
            requested, "explicit_completion_decision_authorized"
        ),
        "completion_decision_status_passed_count": _sum_truthy(
            requested, "completion_decision_status_passed"
        ),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "completion_decision_record_valid_count": _sum_truthy(
            requested, "completion_decision_record_valid"
        ),
        "completion_decision_record_rejected_count": rejected_count,
        "unsafe_completion_decision_record_count": unsafe_count,
        "missing_completion_prerequisite_count": _sum_count(
            requested, "missing_completion_prerequisite_count"
        ),
        "reported_allowed_evidence_command_count": _sum_count(
            requested, "reported_allowed_evidence_command_count"
        ),
        "reported_forbidden_evidence_command_count": forbidden_evidence_count,
    }
    summary.update({f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS})
    return summary
