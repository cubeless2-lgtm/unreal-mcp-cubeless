#!/usr/bin/env python
"""
Section 73 durable canary read-only retry result admission contract.

This contract validates the shape of a future read-only canary retry result.
It does not perform the retry and does not open durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_READ_ONLY_RETRY_RESULT_ADMISSION_SCHEMA = (
    "section_73_durable_canary_read_only_retry_result_admission_contract_v1"
)
CANARY_READ_ONLY_RETRY_RESULT_SCHEMA = "section_73_durable_canary_read_only_retry_result_v1"
CANARY_READ_ONLY_RETRY_RESULT_ADMISSION_SUMMARY_SCHEMA = (
    "section_73_durable_canary_read_only_retry_result_admission_summary_v1"
)
READ_ONLY_RESULT_COMMAND = "unreal.EditorAssetLibrary.does_asset_exist"


def _attempted(value: Any) -> bool:
    return value is True or value == 1


def build_canary_read_only_retry_result_admission_contract(
    requested: bool,
    retry_envelope_summary: Dict[str, Any],
    retry_result: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    retry_result = retry_result or {}
    result_present = bool(retry_result)
    envelope_defined = bool(
        requested
        and retry_envelope_summary.get("status") == "passed"
        and retry_envelope_summary.get("durable_requested_canary_read_only_retry_envelope_count") == 1
        and retry_envelope_summary.get("read_only_retry_envelope_defined_count") == 1
        and retry_envelope_summary.get("read_only_command_count") == 1
    )
    result_schema_matches = bool(
        result_present and retry_result.get("schema") == CANARY_READ_ONLY_RETRY_RESULT_SCHEMA
    )
    explicit_retry_authorized = bool(
        result_present and retry_result.get("explicit_live_read_only_retry_authorized") is True
    )
    read_only_command = retry_result.get("command") or retry_result.get("read_only_command") or ""
    read_only_command_matches = bool(result_present and read_only_command == READ_ONLY_RESULT_COMMAND)
    result_status_passed = bool(result_present and retry_result.get("status") == "passed")
    read_only_result = bool(result_present and retry_result.get("read_only") is True)
    asset_exists_check_performed = bool(
        result_present and retry_result.get("asset_exists_check_performed") is True
    )
    authoring_attempted_count = int(_attempted(retry_result.get("authoring_attempted")))
    save_delete_rename_attempted_count = sum(
        int(_attempted(retry_result.get(key)))
        for key in (
            "save_or_delete_attempted",
            "save_asset_attempted",
            "delete_asset_attempted",
            "rename_asset_attempted",
        )
    )
    cleanup_attempted_count = int(_attempted(retry_result.get("cleanup_attempted")))
    canary_execution_attempted_count = int(_attempted(retry_result.get("canary_execution_attempted")))
    durable_authoring_attempted_count = int(_attempted(retry_result.get("durable_authoring_attempted")))
    unsafe_retry_result_count = (
        authoring_attempted_count
        + save_delete_rename_attempted_count
        + cleanup_attempted_count
        + canary_execution_attempted_count
        + durable_authoring_attempted_count
    )
    read_only_result_admitted = bool(
        envelope_defined
        and result_schema_matches
        and explicit_retry_authorized
        and read_only_command_matches
        and result_status_passed
        and read_only_result
        and asset_exists_check_performed
        and unsafe_retry_result_count == 0
    )
    missing: list[str] = []
    if requested:
        if not envelope_defined:
            missing.append("section_72_retry_envelope_not_defined")
        if not result_present:
            missing.append("live_read_only_retry_result_missing")
        if not explicit_retry_authorized:
            missing.append("explicit_live_read_only_retry_authorization_missing")
    rejected_result = bool(result_present and not read_only_result_admitted)
    return {
        "id": "durable_canary_read_only_retry_result_admission",
        "schema": CANARY_READ_ONLY_RETRY_RESULT_ADMISSION_SCHEMA,
        "requested": requested,
        "retry_result_admission_contract_defined": envelope_defined,
        "required_result_schema": CANARY_READ_ONLY_RETRY_RESULT_SCHEMA if requested else "",
        "live_read_only_retry_result_present": result_present,
        "result_schema_matches": result_schema_matches,
        "explicit_live_read_only_retry_authorized": explicit_retry_authorized,
        "read_only_command": read_only_command if requested else "",
        "read_only_command_matches": read_only_command_matches,
        "result_status_passed": result_status_passed,
        "read_only_result": read_only_result,
        "asset_exists_check_performed": asset_exists_check_performed,
        "read_only_result_admitted": read_only_result_admitted,
        "missing_admission_prerequisites": missing,
        "missing_admission_prerequisite_count": len(missing),
        "retry_result_rejected": rejected_result,
        "unsafe_retry_result_count": unsafe_retry_result_count,
        "canary_execution_allowed_after_retry_result": False,
        "durable_executor_may_open_after_retry_result": False,
        "authoring_command_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_authoring_command_count": authoring_attempted_count + durable_authoring_attempted_count,
        "live_save_delete_rename_command_count": save_delete_rename_attempted_count,
        "live_cleanup_command_count": cleanup_attempted_count,
        "live_canary_execution_command_count": canary_execution_attempted_count,
        "blocked_by": []
        if not requested
        else [
            "section_73_result_admission_does_not_open_durable_execution",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a Section 73 read-only retry result only from a separately authorized live retry",
            "reject any retry result that contains authoring, save, delete, rename, cleanup, or canary execution",
            "keep durable executor closed after read-only retry result admission",
        ],
    }


def summarize_canary_read_only_retry_result_admissions(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("retry_result_rejected"))
    unsafe_count = sum(contract.get("unsafe_retry_result_count", 0) for contract in requested)
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(
                1 for contract in requested if contract.get("retry_result_admission_contract_defined")
            )
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and sum(
                1
                for contract in requested
                if contract.get("canary_execution_allowed_after_retry_result")
            )
            == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_executor_may_open_after_retry_result")
            )
            == 0
            and sum(1 for contract in requested if contract.get("authoring_command_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_delete_rename_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            and sum(contract.get("live_authoring_command_count", 0) for contract in requested) == 0
            and sum(
                contract.get("live_save_delete_rename_command_count", 0) for contract in requested
            )
            == 0
            and sum(contract.get("live_cleanup_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_canary_execution_command_count", 0) for contract in requested)
            == 0
            else "failed"
        )
    return {
        "schema": CANARY_READ_ONLY_RETRY_RESULT_ADMISSION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_read_only_retry_result_admission_count": len(requested),
        "retry_result_admission_contract_defined_count": sum(
            1 for contract in requested if contract.get("retry_result_admission_contract_defined")
        ),
        "live_read_only_retry_result_present_count": sum(
            1 for contract in requested if contract.get("live_read_only_retry_result_present")
        ),
        "result_schema_matches_count": sum(
            1 for contract in requested if contract.get("result_schema_matches")
        ),
        "explicit_live_read_only_retry_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_live_read_only_retry_authorized")
        ),
        "read_only_command_matches_count": sum(
            1 for contract in requested if contract.get("read_only_command_matches")
        ),
        "result_status_passed_count": sum(
            1 for contract in requested if contract.get("result_status_passed")
        ),
        "read_only_result_count": sum(1 for contract in requested if contract.get("read_only_result")),
        "asset_exists_check_performed_count": sum(
            1 for contract in requested if contract.get("asset_exists_check_performed")
        ),
        "read_only_result_admitted_count": sum(
            1 for contract in requested if contract.get("read_only_result_admitted")
        ),
        "missing_admission_prerequisite_count": sum(
            contract.get("missing_admission_prerequisite_count", 0) for contract in requested
        ),
        "rejected_retry_result_count": rejected_count,
        "unsafe_retry_result_count": unsafe_count,
        "canary_execution_allowed_after_retry_result_count": sum(
            1 for contract in requested if contract.get("canary_execution_allowed_after_retry_result")
        ),
        "durable_executor_may_open_after_retry_result_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_after_retry_result")
        ),
        "authoring_command_allowed_count": sum(
            1 for contract in requested if contract.get("authoring_command_allowed")
        ),
        "save_delete_rename_allowed_count": sum(
            1 for contract in requested if contract.get("save_delete_rename_allowed")
        ),
        "cleanup_allowed_count": sum(1 for contract in requested if contract.get("cleanup_allowed")),
        "live_authoring_command_count": sum(
            contract.get("live_authoring_command_count", 0) for contract in requested
        ),
        "live_save_delete_rename_command_count": sum(
            contract.get("live_save_delete_rename_command_count", 0) for contract in requested
        ),
        "live_cleanup_command_count": sum(
            contract.get("live_cleanup_command_count", 0) for contract in requested
        ),
        "live_canary_execution_command_count": sum(
            contract.get("live_canary_execution_command_count", 0) for contract in requested
        ),
    }
