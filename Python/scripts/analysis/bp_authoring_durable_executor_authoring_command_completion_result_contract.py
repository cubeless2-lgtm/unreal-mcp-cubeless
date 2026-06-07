#!/usr/bin/env python
"""
Section 119 durable executor authoring command completion result contract.

This contract validates future completion result records after an application
record is valid. It admits only no-op and validation result evidence; it does
not accept completed, write, dirty-package, save, delete/rename, cleanup, code,
or live command results.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_RESULT_SCHEMA = (
    "section_119_durable_executor_authoring_command_completion_result_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_RESULT_RECORD_SCHEMA = (
    "section_119_durable_executor_authoring_command_completion_result_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_RESULT_SUMMARY_SCHEMA = (
    "section_119_durable_executor_authoring_command_completion_result_summary_v1"
)
EXPECTED_RESULT_SCOPE = "durable_executor_authoring_command_completion_result_only"


OUTPUT_ACTION_KEYS = (
    "durable_authoring_command_completion_result_accepted",
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
UNSAFE_RESULT_RECORD_ACTION_KEYS = (
    "durable_authoring_command_completion_result_accepted",
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
    "live_command_dispatch_performed",
    "live_command_dispatched",
    "live_command_execution_performed",
    "live_command_executed",
)
PREVIOUS_ZERO_COUNT_KEYS = (
    "durable_authoring_command_completion_allowed_count",
    "durable_authoring_command_completed_count",
    "durable_authoring_command_application_allowed_count",
    "durable_authoring_command_application_applied_count",
    "asset_write_allowed_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
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
    "save_delete_rename_allowed_count",
    "cleanup_allowed_count",
    "live_command_dispatched_count",
    "live_command_executed_count",
)
ALLOWED_RESULT_COUNT_KEYS = (
    "reported_completion_noop_result_count",
    "reported_application_validation_result_count",
)
FORBIDDEN_RESULT_COUNT_KEYS = (
    "reported_completion_completed_result_count",
    "reported_asset_write_result_count",
    "reported_package_dirty_result_count",
    "reported_save_result_count",
    "reported_delete_rename_result_count",
    "reported_cleanup_result_count",
    "reported_code_change_result_count",
    "reported_live_command_result_count",
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


def build_durable_executor_authoring_command_completion_result_contract(
    requested: bool,
    application_summary: Dict[str, Any],
    result_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    result_record = result_record or {}
    result_record_present = bool(result_record)
    application_contract_ready = bool(
        requested
        and application_summary.get("status") == "passed"
        and application_summary.get("application_contract_defined_count") == 1
        and application_summary.get("application_record_rejected_count") == 0
        and application_summary.get("unsafe_application_record_count") == 0
        and application_summary.get("reported_forbidden_evidence_command_count") == 0
        and all(application_summary.get(key) == 0 for key in PREVIOUS_ZERO_COUNT_KEYS)
    )
    application_inputs_satisfied = bool(
        application_summary.get("application_inputs_satisfied_count") == 1
    )
    application_record_valid = bool(
        application_summary.get("application_record_valid_count") == 1
    )
    result_inputs_satisfied = bool(
        application_inputs_satisfied and application_record_valid
    )
    record_schema_matches = bool(
        result_record_present
        and result_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_RESULT_RECORD_SCHEMA
    )
    result_scope_matches = bool(
        result_record_present
        and result_record.get("result_scope") == EXPECTED_RESULT_SCOPE
    )
    explicit_result_authorized = bool(
        result_record_present
        and result_record.get(
            "explicit_durable_authoring_command_completion_result_authorized"
        )
        is True
    )
    result_status_passed = bool(
        result_record_present and result_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        result_record_present
        and result_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        result_record_present
        and result_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    allowed_counts = {
        key: _count(result_record.get(key)) for key in ALLOWED_RESULT_COUNT_KEYS
    }
    forbidden_counts = {
        key: _count(result_record.get(key)) for key in FORBIDDEN_RESULT_COUNT_KEYS
    }
    reported_allowed_result_count = sum(allowed_counts.values())
    reported_forbidden_result_count = sum(forbidden_counts.values())
    allowed_result_observed = bool(
        result_record_present and reported_allowed_result_count > 0
    )
    no_forbidden_results = bool(
        result_record_present and reported_forbidden_result_count == 0
    )
    unsafe_result_record_count = (
        sum(int(_attempted(result_record.get(key))) for key in UNSAFE_RESULT_RECORD_ACTION_KEYS)
        + reported_forbidden_result_count
    )
    result_contract_defined = bool(requested and application_contract_ready)
    result_record_valid = bool(
        result_contract_defined
        and result_inputs_satisfied
        and record_schema_matches
        and result_scope_matches
        and explicit_result_authorized
        and result_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_result_observed
        and no_forbidden_results
        and unsafe_result_record_count == 0
    )
    missing: list[str] = []
    if requested:
        if not application_inputs_satisfied:
            missing.append("section_118_application_inputs_satisfied")
        if not application_record_valid:
            missing.append("section_118_application_record_valid")
        if not result_record_present:
            missing.append("durable_authoring_command_completion_result_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_completion_result_record_schema")
        if not result_scope_matches:
            missing.append("durable_executor_authoring_command_completion_result_only_scope")
        if not explicit_result_authorized:
            missing.append(
                "explicit_durable_authoring_command_completion_result_authorization"
            )
        if not result_status_passed:
            missing.append("durable_authoring_command_completion_result_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_result_observed:
            missing.append("allowed_durable_authoring_command_completion_result_observed")
        if not no_forbidden_results:
            missing.append("no_forbidden_durable_authoring_command_completion_results")
        missing.append("separate_durable_authoring_command_result_readback_contract")
    result_record_rejected = bool(result_record_present and not result_record_valid)
    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_command_completion_result",
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_RESULT_SCHEMA,
        "requested": requested,
        "result_contract_defined": result_contract_defined,
        "required_result_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_RESULT_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_result_scope": EXPECTED_RESULT_SCOPE if requested else "",
        "application_contract_ready": application_contract_ready,
        "application_inputs_satisfied": application_inputs_satisfied,
        "application_record_valid": application_record_valid,
        "result_inputs_satisfied": result_inputs_satisfied,
        "result_record_present": result_record_present,
        "record_schema_matches": record_schema_matches,
        "result_scope_matches": result_scope_matches,
        "explicit_result_authorized": explicit_result_authorized,
        "result_status_passed": result_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "reported_allowed_result_count": reported_allowed_result_count,
        "reported_forbidden_result_count": reported_forbidden_result_count,
        "allowed_result_observed": allowed_result_observed,
        "no_forbidden_results": no_forbidden_results,
        "result_record_valid": result_record_valid,
        "result_record_rejected": result_record_rejected,
        "unsafe_result_record_count": unsafe_result_record_count,
        "missing_result_prerequisites": missing,
        "missing_result_prerequisite_count": len(missing),
        "reported_allowed_evidence_command_count": application_summary.get(
            "reported_allowed_evidence_command_count",
            0,
        ),
        "reported_forbidden_evidence_command_count": application_summary.get(
            "reported_forbidden_evidence_command_count",
            0,
        ),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract.update(allowed_counts)
    contract.update(forbidden_counts)
    return contract


def summarize_durable_executor_authoring_command_completion_results(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(requested, "result_record_rejected")
    unsafe_count = _sum_count(requested, "unsafe_result_record_count")
    forbidden_result_count = _sum_count(requested, "reported_forbidden_result_count")
    forbidden_evidence_count = _sum_count(
        requested, "reported_forbidden_evidence_command_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "result_contract_defined") == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_result_count == 0
            and forbidden_evidence_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_COMPLETION_RESULT_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_command_completion_result_count": len(
            requested
        ),
        "result_contract_defined_count": _sum_truthy(
            requested, "result_contract_defined"
        ),
        "application_contract_ready_count": _sum_truthy(
            requested, "application_contract_ready"
        ),
        "application_inputs_satisfied_count": _sum_truthy(
            requested, "application_inputs_satisfied"
        ),
        "application_record_valid_count": _sum_truthy(
            requested, "application_record_valid"
        ),
        "result_inputs_satisfied_count": _sum_truthy(
            requested, "result_inputs_satisfied"
        ),
        "result_record_present_count": _sum_truthy(
            requested, "result_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "result_scope_matches_count": _sum_truthy(requested, "result_scope_matches"),
        "explicit_result_authorized_count": _sum_truthy(
            requested, "explicit_result_authorized"
        ),
        "result_status_passed_count": _sum_truthy(
            requested, "result_status_passed"
        ),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "allowed_result_observed_count": _sum_truthy(
            requested, "allowed_result_observed"
        ),
        "no_forbidden_results_count": _sum_truthy(
            requested, "no_forbidden_results"
        ),
        "result_record_valid_count": _sum_truthy(requested, "result_record_valid"),
        "result_record_rejected_count": rejected_count,
        "unsafe_result_record_count": unsafe_count,
        "missing_result_prerequisite_count": _sum_count(
            requested, "missing_result_prerequisite_count"
        ),
        "reported_allowed_result_count": _sum_count(
            requested, "reported_allowed_result_count"
        ),
        "reported_forbidden_result_count": forbidden_result_count,
        "reported_allowed_evidence_command_count": _sum_count(
            requested, "reported_allowed_evidence_command_count"
        ),
        "reported_forbidden_evidence_command_count": forbidden_evidence_count,
    }
    summary.update({f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS})
    summary.update({key: _sum_count(requested, key) for key in ALLOWED_RESULT_COUNT_KEYS})
    summary.update({key: _sum_count(requested, key) for key in FORBIDDEN_RESULT_COUNT_KEYS})
    return summary
