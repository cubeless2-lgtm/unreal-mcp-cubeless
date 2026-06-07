#!/usr/bin/env python
"""
Section 150 durable executor authoring command completion application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract.

This contract defines the scoped application record required after a future
completion-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness
record is valid. It does not apply completion, write assets, dirty packages,
save, delete/rename, cleanup, change code, probe live bridges, or open durable
authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SCHEMA = (
    "section_150_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_RECORD_SCHEMA = (
    "section_150_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SUMMARY_SCHEMA = (
    "section_150_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary_v1"
)
EXPECTED_APPLICATION_SCOPE = (
    "durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_only"
)


OUTPUT_ACTION_KEYS = (
    "durable_authoring_command_completion_allowed",
    "durable_authoring_command_completed",
    "durable_authoring_command_application_allowed",
    "durable_authoring_command_application_applied",
    "asset_write_allowed",
    "asset_write_performed",
    "package_dirty_marked",
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
    "save_delete_rename_allowed",
    "cleanup_allowed",
    "live_command_dispatched",
    "live_command_executed",
)
UNSAFE_APPLICATION_RECORD_ACTION_KEYS = (
    "durable_authoring_command_completion_allowed",
    "durable_authoring_command_completed",
    "durable_authoring_command_application_allowed",
    "durable_authoring_command_application_applied",
    "asset_write_allowed",
    "asset_write_performed",
    "package_dirty_marked",
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
    "durable_authoring_command_completion_allowed_count",
    "durable_authoring_command_completed_count",
    "durable_authoring_command_completion_application_started_count",
    "durable_authoring_command_dispatch_allowed_count",
    "durable_authoring_command_dispatched_count",
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


def build_durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
    requested: bool,
    completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary: Dict[str, Any],
    application_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    application_record = application_record or {}
    application_record_present = bool(application_record)
    completion_decision_contract_ready = bool(
        requested
        and completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get("status") == "passed"
        and completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get(
            "completion_decision_contract_defined_count"
        )
        == 1
        and completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get(
            "completion_decision_record_rejected_count"
        )
        == 0
        and completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get(
            "unsafe_completion_decision_record_count"
        )
        == 0
        and completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get(
            "reported_forbidden_evidence_command_count"
        )
        == 0
        and all(
            completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get(key) == 0
            for key in PREVIOUS_ZERO_COUNT_KEYS
        )
    )
    evidence_ready_for_completion = bool(
        completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get(
            "evidence_ready_for_completion_count"
        )
        == 1
    )
    completion_decision_record_valid = bool(
        completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get(
            "completion_decision_record_valid_count"
        )
        == 1
    )
    application_inputs_satisfied = bool(
        evidence_ready_for_completion and completion_decision_record_valid
    )
    record_schema_matches = bool(
        application_record_present
        and application_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_RECORD_SCHEMA
    )
    application_scope_matches = bool(
        application_record_present
        and application_record.get("application_scope") == EXPECTED_APPLICATION_SCOPE
    )
    explicit_application_authorized = bool(
        application_record_present
        and application_record.get(
            "explicit_durable_authoring_command_completion_application_authorized"
        )
        is True
    )
    application_status_passed = bool(
        application_record_present and application_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        application_record_present
        and application_record.get("operator_reconfirmed_no_save_delete_rename")
        is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        application_record_present
        and application_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    reported_allowed_evidence_command_count = (
        completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get(
            "reported_allowed_evidence_command_count",
            0,
        )
    )
    reported_forbidden_evidence_command_count = (
        completion_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get(
            "reported_forbidden_evidence_command_count",
            0,
        )
    )
    unsafe_application_record_count = sum(
        int(_attempted(application_record.get(key)))
        for key in UNSAFE_APPLICATION_RECORD_ACTION_KEYS
    )
    application_contract_defined = bool(
        requested and completion_decision_contract_ready
    )
    application_record_valid = bool(
        application_contract_defined
        and application_inputs_satisfied
        and record_schema_matches
        and application_scope_matches
        and explicit_application_authorized
        and application_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and unsafe_application_record_count == 0
    )
    missing: list[str] = []
    if requested:
        if not evidence_ready_for_completion:
            missing.append("section_149_evidence_ready_for_completion")
        if not completion_decision_record_valid:
            missing.append("section_149_completion_decision_record_valid")
        if not application_record_present:
            missing.append("durable_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_record_schema")
        if not application_scope_matches:
            missing.append(
                "durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_only_scope"
            )
        if not explicit_application_authorized:
            missing.append(
                "explicit_durable_authoring_command_completion_application_authorization"
            )
        if not application_status_passed:
            missing.append("durable_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        missing.append("separate_durable_authoring_command_completion_result_after_application_contract")
    application_record_rejected = bool(
        application_record_present and not application_record_valid
    )
    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness",
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SCHEMA,
        "requested": requested,
        "application_contract_defined": application_contract_defined,
        "required_application_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_application_scope": EXPECTED_APPLICATION_SCOPE if requested else "",
        "completion_decision_contract_ready": completion_decision_contract_ready,
        "evidence_ready_for_completion": evidence_ready_for_completion,
        "completion_decision_record_valid": completion_decision_record_valid,
        "application_inputs_satisfied": application_inputs_satisfied,
        "application_record_present": application_record_present,
        "record_schema_matches": record_schema_matches,
        "application_scope_matches": application_scope_matches,
        "explicit_application_authorized": explicit_application_authorized,
        "application_status_passed": application_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "application_record_valid": application_record_valid,
        "application_record_rejected": application_record_rejected,
        "unsafe_application_record_count": unsafe_application_record_count,
        "missing_application_prerequisites": missing,
        "missing_application_prerequisite_count": len(missing),
        "reported_allowed_evidence_command_count": (
            reported_allowed_evidence_command_count
        ),
        "reported_forbidden_evidence_command_count": (
            reported_forbidden_evidence_command_count
        ),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    return contract


def summarize_durable_executor_authoring_command_completion_applications_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(requested, "application_record_rejected")
    unsafe_count = _sum_count(requested, "unsafe_application_record_count")
    forbidden_evidence_count = _sum_count(
        requested, "reported_forbidden_evidence_command_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "application_contract_defined") == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_evidence_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_command_completion_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": len(
            requested
        ),
        "application_contract_defined_count": _sum_truthy(
            requested, "application_contract_defined"
        ),
        "completion_decision_contract_ready_count": _sum_truthy(
            requested, "completion_decision_contract_ready"
        ),
        "evidence_ready_for_completion_count": _sum_truthy(
            requested, "evidence_ready_for_completion"
        ),
        "completion_decision_record_valid_count": _sum_truthy(
            requested, "completion_decision_record_valid"
        ),
        "application_inputs_satisfied_count": _sum_truthy(
            requested, "application_inputs_satisfied"
        ),
        "application_record_present_count": _sum_truthy(
            requested, "application_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "application_scope_matches_count": _sum_truthy(
            requested, "application_scope_matches"
        ),
        "explicit_application_authorized_count": _sum_truthy(
            requested, "explicit_application_authorized"
        ),
        "application_status_passed_count": _sum_truthy(
            requested, "application_status_passed"
        ),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "application_record_valid_count": _sum_truthy(
            requested, "application_record_valid"
        ),
        "application_record_rejected_count": rejected_count,
        "unsafe_application_record_count": unsafe_count,
        "missing_application_prerequisite_count": _sum_count(
            requested, "missing_application_prerequisite_count"
        ),
        "reported_allowed_evidence_command_count": _sum_count(
            requested, "reported_allowed_evidence_command_count"
        ),
        "reported_forbidden_evidence_command_count": forbidden_evidence_count,
    }
    summary.update(
        {f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS}
    )
    return summary

