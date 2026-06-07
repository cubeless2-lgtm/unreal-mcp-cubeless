#!/usr/bin/env python
"""
Section 92 durable canary authoring command result readback contract.

This contract validates future readback records after a completion result record
is valid. It does not accept completed/write/save state as durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_DURABLE_AUTHORING_COMMAND_RESULT_READBACK_SCHEMA = (
    "section_92_durable_canary_authoring_command_result_readback_contract_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_RESULT_READBACK_RECORD_SCHEMA = (
    "section_92_durable_canary_authoring_command_result_readback_record_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_RESULT_READBACK_SUMMARY_SCHEMA = (
    "section_92_durable_canary_authoring_command_result_readback_summary_v1"
)
EXPECTED_READBACK_SCOPE = "durable_canary_authoring_command_result_readback_only"


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


def build_canary_durable_authoring_command_result_readback_contract(
    requested: bool,
    result_summary: Dict[str, Any],
    readback_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    readback_record = readback_record or {}
    readback_record_present = bool(readback_record)
    result_contract_ready = bool(
        requested
        and result_summary.get("status") == "passed"
        and result_summary.get("result_contract_defined_count") == 1
        and result_summary.get("result_record_rejected_count") == 0
        and result_summary.get("unsafe_result_record_count") == 0
        and result_summary.get("reported_forbidden_result_count") == 0
        and result_summary.get("reported_forbidden_evidence_command_count") == 0
        and result_summary.get("durable_authoring_command_completion_result_accepted_count") == 0
        and result_summary.get("durable_authoring_command_completed_count") == 0
        and result_summary.get("asset_write_performed_count") == 0
        and result_summary.get("package_dirty_marked_count") == 0
        and result_summary.get("save_delete_rename_allowed_count") == 0
        and result_summary.get("cleanup_allowed_count") == 0
    )
    result_inputs_satisfied = bool(result_summary.get("result_inputs_satisfied_count") == 1)
    result_record_valid = bool(result_summary.get("result_record_valid_count") == 1)
    allowed_result_observed = bool(result_summary.get("allowed_result_observed_count") == 1)
    no_forbidden_results = bool(result_summary.get("no_forbidden_results_count") == 1)
    readback_inputs_satisfied = bool(
        result_inputs_satisfied
        and result_record_valid
        and allowed_result_observed
        and no_forbidden_results
    )
    record_schema_matches = bool(
        readback_record_present
        and readback_record.get("schema")
        == CANARY_DURABLE_AUTHORING_COMMAND_RESULT_READBACK_RECORD_SCHEMA
    )
    readback_scope_matches = bool(
        readback_record_present
        and readback_record.get("readback_scope") == EXPECTED_READBACK_SCOPE
    )
    explicit_readback_authorized = bool(
        readback_record_present
        and readback_record.get("explicit_durable_authoring_command_result_readback_authorized")
        is True
    )
    readback_status_passed = bool(readback_record_present and readback_record.get("status") == "passed")
    no_save_delete_rename_acknowledged = bool(
        readback_record_present
        and readback_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    reported_no_completion_readback_count = _count(
        readback_record.get("reported_no_completion_readback_count")
    )
    reported_no_write_readback_count = _count(
        readback_record.get("reported_no_write_readback_count")
    )
    reported_no_save_readback_count = _count(
        readback_record.get("reported_no_save_readback_count")
    )
    reported_completed_readback_count = _count(
        readback_record.get("reported_completed_readback_count")
    )
    reported_asset_write_readback_count = _count(
        readback_record.get("reported_asset_write_readback_count")
    )
    reported_package_dirty_readback_count = _count(
        readback_record.get("reported_package_dirty_readback_count")
    )
    reported_save_readback_count = _count(readback_record.get("reported_save_readback_count"))
    reported_delete_rename_readback_count = _count(
        readback_record.get("reported_delete_rename_readback_count")
    )
    reported_cleanup_readback_count = _count(
        readback_record.get("reported_cleanup_readback_count")
    )
    reported_allowed_readback_count = (
        reported_no_completion_readback_count
        + reported_no_write_readback_count
        + reported_no_save_readback_count
    )
    reported_forbidden_readback_count = (
        reported_completed_readback_count
        + reported_asset_write_readback_count
        + reported_package_dirty_readback_count
        + reported_save_readback_count
        + reported_delete_rename_readback_count
        + reported_cleanup_readback_count
    )
    allowed_readback_observed = bool(
        readback_record_present and reported_allowed_readback_count > 0
    )
    no_forbidden_readbacks = bool(
        readback_record_present and reported_forbidden_readback_count == 0
    )
    unsafe_readback_record_count = (
        sum(
            int(_attempted(readback_record.get(key)))
            for key in (
                "durable_authoring_command_completed",
                "durable_authoring_command_completion_result_accepted",
                "asset_write_performed",
                "package_dirty_marked",
                "save_asset_executed",
                "delete_asset_authorized",
                "rename_asset_authorized",
                "cleanup_authorized",
                "durable_authoring_enabled",
                "durable_authoring_allowed",
            )
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
        and allowed_readback_observed
        and no_forbidden_readbacks
        and unsafe_readback_record_count == 0
    )
    missing = []
    if requested:
        if not result_inputs_satisfied:
            missing.append("section_91_result_inputs_satisfied")
        if not result_record_valid:
            missing.append("section_91_result_record_valid")
        if not allowed_result_observed:
            missing.append("section_91_allowed_result_observed")
        if not no_forbidden_results:
            missing.append("section_91_no_forbidden_results")
        if not readback_record_present:
            missing.append("durable_authoring_command_result_readback_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_result_readback_record_schema")
        if not readback_scope_matches:
            missing.append("durable_canary_authoring_command_result_readback_only_scope")
        if not explicit_readback_authorized:
            missing.append("explicit_durable_authoring_command_result_readback_authorization")
        if not readback_status_passed:
            missing.append("durable_authoring_command_result_readback_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not allowed_readback_observed:
            missing.append("allowed_durable_authoring_command_result_readback_observed")
        if not no_forbidden_readbacks:
            missing.append("no_forbidden_durable_authoring_command_result_readbacks")
        missing.append("separate_durable_authoring_final_no_save_release_contract")
    readback_record_rejected = bool(readback_record_present and not readback_record_valid)
    return {
        "id": "durable_canary_authoring_command_result_readback",
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_RESULT_READBACK_SCHEMA,
        "requested": requested,
        "readback_contract_defined": readback_contract_defined,
        "required_readback_record_schema": (
            CANARY_DURABLE_AUTHORING_COMMAND_RESULT_READBACK_RECORD_SCHEMA
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
        "reported_allowed_readback_count": reported_allowed_readback_count,
        "reported_forbidden_readback_count": reported_forbidden_readback_count,
        "allowed_readback_observed": allowed_readback_observed,
        "no_forbidden_readbacks": no_forbidden_readbacks,
        "readback_record_valid": readback_record_valid,
        "readback_record_rejected": readback_record_rejected,
        "unsafe_readback_record_count": unsafe_readback_record_count,
        "missing_readback_prerequisites": missing,
        "missing_readback_prerequisite_count": len(missing),
        "durable_authoring_command_result_readback_accepted": False,
        "durable_authoring_command_completed": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "reported_no_completion_readback_count": reported_no_completion_readback_count,
        "reported_no_write_readback_count": reported_no_write_readback_count,
        "reported_no_save_readback_count": reported_no_save_readback_count,
        "reported_completed_readback_count": reported_completed_readback_count,
        "reported_asset_write_readback_count": reported_asset_write_readback_count,
        "reported_package_dirty_readback_count": reported_package_dirty_readback_count,
        "reported_save_readback_count": reported_save_readback_count,
        "reported_delete_rename_readback_count": reported_delete_rename_readback_count,
        "reported_cleanup_readback_count": reported_cleanup_readback_count,
    }


def summarize_canary_durable_authoring_command_result_readbacks(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("readback_record_rejected"))
    unsafe_count = sum(contract.get("unsafe_readback_record_count", 0) for contract in requested)
    forbidden_readback_count = sum(
        contract.get("reported_forbidden_readback_count", 0) for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("readback_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_readback_count == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_result_readback_accepted")
            )
            == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_command_completed")) == 0
            and sum(1 for contract in requested if contract.get("asset_write_performed")) == 0
            and sum(1 for contract in requested if contract.get("package_dirty_marked")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_delete_rename_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            else "failed"
        )
    return {
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_RESULT_READBACK_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_authoring_command_result_readback_count": len(requested),
        "readback_contract_defined_count": sum(
            1 for contract in requested if contract.get("readback_contract_defined")
        ),
        "result_contract_ready_count": sum(
            1 for contract in requested if contract.get("result_contract_ready")
        ),
        "result_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("result_inputs_satisfied")
        ),
        "result_record_valid_count": sum(
            1 for contract in requested if contract.get("result_record_valid")
        ),
        "allowed_result_observed_count": sum(
            1 for contract in requested if contract.get("allowed_result_observed")
        ),
        "no_forbidden_results_count": sum(
            1 for contract in requested if contract.get("no_forbidden_results")
        ),
        "readback_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("readback_inputs_satisfied")
        ),
        "readback_record_present_count": sum(
            1 for contract in requested if contract.get("readback_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "readback_scope_matches_count": sum(
            1 for contract in requested if contract.get("readback_scope_matches")
        ),
        "explicit_readback_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_readback_authorized")
        ),
        "readback_status_passed_count": sum(
            1 for contract in requested if contract.get("readback_status_passed")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "allowed_readback_observed_count": sum(
            1 for contract in requested if contract.get("allowed_readback_observed")
        ),
        "no_forbidden_readbacks_count": sum(
            1 for contract in requested if contract.get("no_forbidden_readbacks")
        ),
        "readback_record_valid_count": sum(
            1 for contract in requested if contract.get("readback_record_valid")
        ),
        "readback_record_rejected_count": rejected_count,
        "unsafe_readback_record_count": unsafe_count,
        "missing_readback_prerequisite_count": sum(
            contract.get("missing_readback_prerequisite_count", 0)
            for contract in requested
        ),
        "reported_allowed_readback_count": sum(
            contract.get("reported_allowed_readback_count", 0) for contract in requested
        ),
        "reported_forbidden_readback_count": forbidden_readback_count,
        "durable_authoring_command_result_readback_accepted_count": sum(
            1
            for contract in requested
            if contract.get("durable_authoring_command_result_readback_accepted")
        ),
        "durable_authoring_command_completed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_command_completed")
        ),
        "asset_write_performed_count": sum(
            1 for contract in requested if contract.get("asset_write_performed")
        ),
        "package_dirty_marked_count": sum(
            1 for contract in requested if contract.get("package_dirty_marked")
        ),
        "durable_authoring_enabled_count": sum(
            1 for contract in requested if contract.get("durable_authoring_enabled")
        ),
        "durable_authoring_allowed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_allowed")
        ),
        "save_delete_rename_allowed_count": sum(
            1 for contract in requested if contract.get("save_delete_rename_allowed")
        ),
        "cleanup_allowed_count": sum(
            1 for contract in requested if contract.get("cleanup_allowed")
        ),
        "reported_no_completion_readback_count": sum(
            contract.get("reported_no_completion_readback_count", 0)
            for contract in requested
        ),
        "reported_no_write_readback_count": sum(
            contract.get("reported_no_write_readback_count", 0) for contract in requested
        ),
        "reported_no_save_readback_count": sum(
            contract.get("reported_no_save_readback_count", 0) for contract in requested
        ),
        "reported_completed_readback_count": sum(
            contract.get("reported_completed_readback_count", 0) for contract in requested
        ),
        "reported_asset_write_readback_count": sum(
            contract.get("reported_asset_write_readback_count", 0)
            for contract in requested
        ),
        "reported_package_dirty_readback_count": sum(
            contract.get("reported_package_dirty_readback_count", 0)
            for contract in requested
        ),
        "reported_save_readback_count": sum(
            contract.get("reported_save_readback_count", 0) for contract in requested
        ),
        "reported_delete_rename_readback_count": sum(
            contract.get("reported_delete_rename_readback_count", 0)
            for contract in requested
        ),
        "reported_cleanup_readback_count": sum(
            contract.get("reported_cleanup_readback_count", 0) for contract in requested
        ),
    }
