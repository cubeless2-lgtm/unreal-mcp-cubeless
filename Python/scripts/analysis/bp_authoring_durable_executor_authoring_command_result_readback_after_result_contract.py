#!/usr/bin/env python
"""
Section 136 durable executor authoring command result readback-after-result contract.

This contract validates future readback records after a completion
result-after-application record is valid. It admits only no-completion,
no-write, and no-save readback evidence; it does not accept completed, write,
dirty-package, save, delete/rename, cleanup, code, or live command readbacks.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_COMMAND_RESULT_READBACK_AFTER_RESULT_SCHEMA = (
    "section_136_durable_executor_authoring_command_result_readback_after_result_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_RESULT_READBACK_AFTER_RESULT_RECORD_SCHEMA = (
    "section_136_durable_executor_authoring_command_result_readback_after_result_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_RESULT_READBACK_AFTER_RESULT_SUMMARY_SCHEMA = (
    "section_136_durable_executor_authoring_command_result_readback_after_result_summary_v1"
)
EXPECTED_READBACK_SCOPE = (
    "durable_executor_authoring_command_result_readback_after_result_only"
)


OUTPUT_ACTION_KEYS = (
    "durable_authoring_command_result_readback_accepted",
    "durable_authoring_command_completion_result_accepted",
    "durable_authoring_command_completed",
    "asset_write_performed",
    "package_dirty_marked",
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
UNSAFE_READBACK_RECORD_ACTION_KEYS = (
    "durable_authoring_command_result_readback_accepted",
    "durable_authoring_command_completion_result_accepted",
    "durable_authoring_command_completed",
    "asset_write_performed",
    "package_dirty_marked",
    "durable_authoring_enabled",
    "durable_authoring_allowed",
    "code_change_performed",
    "executor_code_modified",
    "unreal_asset_modified",
    "live_bridge_probe_started",
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
    "durable_authoring_command_completion_result_accepted_count",
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
ALLOWED_READBACK_COUNT_KEYS = (
    "reported_no_completion_readback_count",
    "reported_no_write_readback_count",
    "reported_no_save_readback_count",
)
FORBIDDEN_READBACK_COUNT_KEYS = (
    "reported_completed_readback_count",
    "reported_asset_write_readback_count",
    "reported_package_dirty_readback_count",
    "reported_save_readback_count",
    "reported_delete_rename_readback_count",
    "reported_cleanup_readback_count",
    "reported_code_change_readback_count",
    "reported_live_command_readback_count",
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


def build_durable_executor_authoring_command_result_readback_after_result_contract(
    requested: bool,
    completion_result_after_application_summary: Dict[str, Any],
    readback_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    readback_record = readback_record or {}
    readback_record_present = bool(readback_record)
    result_contract_ready = bool(
        requested
        and completion_result_after_application_summary.get("status") == "passed"
        and completion_result_after_application_summary.get("result_contract_defined_count")
        == 1
        and completion_result_after_application_summary.get("result_record_rejected_count")
        == 0
        and completion_result_after_application_summary.get("unsafe_result_record_count")
        == 0
        and completion_result_after_application_summary.get("reported_forbidden_result_count")
        == 0
        and completion_result_after_application_summary.get(
            "reported_forbidden_evidence_command_count"
        )
        == 0
        and all(
            completion_result_after_application_summary.get(key) == 0
            for key in PREVIOUS_ZERO_COUNT_KEYS
        )
    )
    result_inputs_satisfied = bool(
        completion_result_after_application_summary.get("result_inputs_satisfied_count")
        == 1
    )
    result_record_valid = bool(
        completion_result_after_application_summary.get("result_record_valid_count")
        == 1
    )
    allowed_result_observed = bool(
        completion_result_after_application_summary.get("allowed_result_observed_count")
        == 1
    )
    no_forbidden_results = bool(
        completion_result_after_application_summary.get("no_forbidden_results_count")
        == 1
    )
    readback_inputs_satisfied = bool(
        result_inputs_satisfied
        and result_record_valid
        and allowed_result_observed
        and no_forbidden_results
    )
    record_schema_matches = bool(
        readback_record_present
        and readback_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_COMMAND_RESULT_READBACK_AFTER_RESULT_RECORD_SCHEMA
    )
    readback_scope_matches = bool(
        readback_record_present
        and readback_record.get("readback_scope") == EXPECTED_READBACK_SCOPE
    )
    explicit_readback_authorized = bool(
        readback_record_present
        and readback_record.get(
            "explicit_durable_authoring_command_result_readback_authorized"
        )
        is True
    )
    readback_status_passed = bool(
        readback_record_present and readback_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        readback_record_present
        and readback_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        readback_record_present
        and readback_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    allowed_counts = {
        key: _count(readback_record.get(key)) for key in ALLOWED_READBACK_COUNT_KEYS
    }
    forbidden_counts = {
        key: _count(readback_record.get(key)) for key in FORBIDDEN_READBACK_COUNT_KEYS
    }
    reported_allowed_readback_count = sum(allowed_counts.values())
    reported_forbidden_readback_count = sum(forbidden_counts.values())
    allowed_readback_observed = bool(
        readback_record_present and reported_allowed_readback_count > 0
    )
    no_forbidden_readbacks = bool(
        readback_record_present and reported_forbidden_readback_count == 0
    )
    unsafe_readback_record_count = (
        sum(
            int(_attempted(readback_record.get(key)))
            for key in UNSAFE_READBACK_RECORD_ACTION_KEYS
        )
        + reported_forbidden_readback_count
    )
    readback_contract_defined = bool(requested and result_contract_ready)
    readback_record_valid = bool(
        readback_contract_defined
        and readback_inputs_satisfied
        and record_schema_matches
        and readback_scope_matches
        and explicit_readback_authorized
        and readback_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_readback_observed
        and no_forbidden_readbacks
        and unsafe_readback_record_count == 0
    )
    missing: list[str] = []
    if requested:
        if not result_inputs_satisfied:
            missing.append("section_135_result_inputs_satisfied")
        if not result_record_valid:
            missing.append("section_135_result_record_valid")
        if not allowed_result_observed:
            missing.append("section_135_allowed_result_observed")
        if not no_forbidden_results:
            missing.append("section_135_no_forbidden_results")
        if not readback_record_present:
            missing.append("durable_authoring_command_result_readback_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_result_readback_record_schema")
        if not readback_scope_matches:
            missing.append(
                "durable_executor_authoring_command_result_readback_after_result_only_scope"
            )
        if not explicit_readback_authorized:
            missing.append(
                "explicit_durable_authoring_command_result_readback_authorization"
            )
        if not readback_status_passed:
            missing.append("durable_authoring_command_result_readback_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_readback_observed:
            missing.append("allowed_durable_authoring_command_result_readback_observed")
        if not no_forbidden_readbacks:
            missing.append("no_forbidden_durable_authoring_command_result_readbacks")
        missing.append("separate_durable_authoring_final_no_save_release_contract")
    readback_record_rejected = bool(
        readback_record_present and not readback_record_valid
    )
    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_command_result_readback_after_result",
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_RESULT_READBACK_AFTER_RESULT_SCHEMA,
        "requested": requested,
        "readback_contract_defined": readback_contract_defined,
        "required_readback_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_COMMAND_RESULT_READBACK_AFTER_RESULT_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_readback_scope": EXPECTED_READBACK_SCOPE if requested else "",
        "result_contract_ready": result_contract_ready,
        "result_inputs_satisfied": result_inputs_satisfied,
        "result_record_valid": result_record_valid,
        "allowed_result_observed": allowed_result_observed,
        "no_forbidden_results": no_forbidden_results,
        "readback_inputs_satisfied": readback_inputs_satisfied,
        "readback_record_present": readback_record_present,
        "record_schema_matches": record_schema_matches,
        "readback_scope_matches": readback_scope_matches,
        "explicit_readback_authorized": explicit_readback_authorized,
        "readback_status_passed": readback_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "reported_allowed_readback_count": reported_allowed_readback_count,
        "reported_forbidden_readback_count": reported_forbidden_readback_count,
        "allowed_readback_observed": allowed_readback_observed,
        "no_forbidden_readbacks": no_forbidden_readbacks,
        "readback_record_valid": readback_record_valid,
        "readback_record_rejected": readback_record_rejected,
        "unsafe_readback_record_count": unsafe_readback_record_count,
        "missing_readback_prerequisites": missing,
        "missing_readback_prerequisite_count": len(missing),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract.update(allowed_counts)
    contract.update(forbidden_counts)
    return contract


def summarize_durable_executor_authoring_command_result_readbacks_after_result(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(requested, "readback_record_rejected")
    unsafe_count = _sum_count(requested, "unsafe_readback_record_count")
    forbidden_readback_count = _sum_count(
        requested, "reported_forbidden_readback_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "readback_contract_defined") == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_readback_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_RESULT_READBACK_AFTER_RESULT_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_command_result_readback_after_result_count": len(
            requested
        ),
        "readback_contract_defined_count": _sum_truthy(
            requested, "readback_contract_defined"
        ),
        "result_contract_ready_count": _sum_truthy(
            requested, "result_contract_ready"
        ),
        "result_inputs_satisfied_count": _sum_truthy(
            requested, "result_inputs_satisfied"
        ),
        "result_record_valid_count": _sum_truthy(requested, "result_record_valid"),
        "allowed_result_observed_count": _sum_truthy(
            requested, "allowed_result_observed"
        ),
        "no_forbidden_results_count": _sum_truthy(
            requested, "no_forbidden_results"
        ),
        "readback_inputs_satisfied_count": _sum_truthy(
            requested, "readback_inputs_satisfied"
        ),
        "readback_record_present_count": _sum_truthy(
            requested, "readback_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "readback_scope_matches_count": _sum_truthy(
            requested, "readback_scope_matches"
        ),
        "explicit_readback_authorized_count": _sum_truthy(
            requested, "explicit_readback_authorized"
        ),
        "readback_status_passed_count": _sum_truthy(
            requested, "readback_status_passed"
        ),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "allowed_readback_observed_count": _sum_truthy(
            requested, "allowed_readback_observed"
        ),
        "no_forbidden_readbacks_count": _sum_truthy(
            requested, "no_forbidden_readbacks"
        ),
        "readback_record_valid_count": _sum_truthy(
            requested, "readback_record_valid"
        ),
        "readback_record_rejected_count": rejected_count,
        "unsafe_readback_record_count": unsafe_count,
        "missing_readback_prerequisite_count": _sum_count(
            requested, "missing_readback_prerequisite_count"
        ),
        "reported_allowed_readback_count": _sum_count(
            requested, "reported_allowed_readback_count"
        ),
        "reported_forbidden_readback_count": forbidden_readback_count,
    }
    summary.update(
        {f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS}
    )
    summary.update(
        {key: _sum_count(requested, key) for key in ALLOWED_READBACK_COUNT_KEYS}
    )
    summary.update(
        {key: _sum_count(requested, key) for key in FORBIDDEN_READBACK_COUNT_KEYS}
    )
    return summary
