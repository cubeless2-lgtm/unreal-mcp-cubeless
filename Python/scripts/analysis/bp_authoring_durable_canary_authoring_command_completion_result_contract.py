#!/usr/bin/env python
"""
Section 91 durable canary authoring command completion result contract.

This contract validates the shape of future completion result records after an
application record is valid. It does not accept completed/write/save results.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_RESULT_SCHEMA = (
    "section_91_durable_canary_authoring_command_completion_result_contract_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_RESULT_RECORD_SCHEMA = (
    "section_91_durable_canary_authoring_command_completion_result_record_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_RESULT_SUMMARY_SCHEMA = (
    "section_91_durable_canary_authoring_command_completion_result_summary_v1"
)
EXPECTED_RESULT_SCOPE = "durable_canary_authoring_command_completion_result_only"


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


def build_canary_durable_authoring_command_completion_result_contract(
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
        and application_summary.get("durable_authoring_command_completion_allowed_count") == 0
        and application_summary.get("durable_authoring_command_completed_count") == 0
        and application_summary.get("durable_authoring_command_application_allowed_count") == 0
        and application_summary.get("durable_authoring_command_application_applied_count") == 0
        and application_summary.get("asset_write_allowed_count") == 0
        and application_summary.get("asset_write_performed_count") == 0
        and application_summary.get("package_dirty_marked_count") == 0
        and application_summary.get("durable_authoring_allowed_count") == 0
        and application_summary.get("save_delete_rename_allowed_count") == 0
        and application_summary.get("cleanup_allowed_count") == 0
        and application_summary.get("live_command_dispatch_allowed_count") == 0
        and application_summary.get("live_command_execution_allowed_count") == 0
        and application_summary.get("live_command_executed_count") == 0
    )
    application_inputs_satisfied = bool(
        application_summary.get("application_inputs_satisfied_count") == 1
    )
    application_record_valid = bool(application_summary.get("application_record_valid_count") == 1)
    result_inputs_satisfied = bool(application_inputs_satisfied and application_record_valid)
    record_schema_matches = bool(
        result_record_present
        and result_record.get("schema")
        == CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_RESULT_RECORD_SCHEMA
    )
    result_scope_matches = bool(
        result_record_present and result_record.get("result_scope") == EXPECTED_RESULT_SCOPE
    )
    explicit_result_authorized = bool(
        result_record_present
        and result_record.get("explicit_durable_authoring_command_completion_result_authorized")
        is True
    )
    result_status_passed = bool(result_record_present and result_record.get("status") == "passed")
    no_save_delete_rename_acknowledged = bool(
        result_record_present
        and result_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    reported_completion_noop_result_count = _count(
        result_record.get("reported_completion_noop_result_count")
    )
    reported_application_validation_result_count = _count(
        result_record.get("reported_application_validation_result_count")
    )
    reported_completion_completed_result_count = _count(
        result_record.get("reported_completion_completed_result_count")
    )
    reported_asset_write_result_count = _count(result_record.get("reported_asset_write_result_count"))
    reported_package_dirty_result_count = _count(
        result_record.get("reported_package_dirty_result_count")
    )
    reported_save_result_count = _count(result_record.get("reported_save_result_count"))
    reported_delete_rename_result_count = _count(
        result_record.get("reported_delete_rename_result_count")
    )
    reported_cleanup_result_count = _count(result_record.get("reported_cleanup_result_count"))
    reported_allowed_result_count = (
        reported_completion_noop_result_count + reported_application_validation_result_count
    )
    reported_forbidden_result_count = (
        reported_completion_completed_result_count
        + reported_asset_write_result_count
        + reported_package_dirty_result_count
        + reported_save_result_count
        + reported_delete_rename_result_count
        + reported_cleanup_result_count
    )
    allowed_result_observed = bool(result_record_present and reported_allowed_result_count > 0)
    no_forbidden_results = bool(result_record_present and reported_forbidden_result_count == 0)
    unsafe_result_record_count = (
        sum(
            int(_attempted(result_record.get(key)))
            for key in (
                "durable_authoring_command_completion_allowed",
                "durable_authoring_command_completed",
                "durable_authoring_command_completion_result_accepted",
                "durable_authoring_command_application_allowed",
                "durable_authoring_command_application_applied",
                "asset_write_allowed",
                "asset_write_performed",
                "package_dirty_marked",
                "save_asset_authorized",
                "save_asset_executed",
                "delete_asset_authorized",
                "rename_asset_authorized",
                "cleanup_authorized",
                "durable_authoring_enabled",
                "durable_authoring_allowed",
                "live_command_dispatch_performed",
                "live_command_execution_performed",
                "live_command_executed",
            )
        )
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
        and allowed_result_observed
        and no_forbidden_results
        and unsafe_result_record_count == 0
    )
    missing = []
    if requested:
        if not application_inputs_satisfied:
            missing.append("section_90_application_inputs_satisfied")
        if not application_record_valid:
            missing.append("section_90_application_record_valid")
        if not result_record_present:
            missing.append("durable_authoring_command_completion_result_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_completion_result_record_schema")
        if not result_scope_matches:
            missing.append("durable_canary_authoring_command_completion_result_only_scope")
        if not explicit_result_authorized:
            missing.append("explicit_durable_authoring_command_completion_result_authorization")
        if not result_status_passed:
            missing.append("durable_authoring_command_completion_result_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not allowed_result_observed:
            missing.append("allowed_durable_authoring_command_completion_result_observed")
        if not no_forbidden_results:
            missing.append("no_forbidden_durable_authoring_command_completion_results")
        missing.append("separate_durable_authoring_command_result_readback_contract")
    result_record_rejected = bool(result_record_present and not result_record_valid)
    return {
        "id": "durable_canary_authoring_command_completion_result",
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_RESULT_SCHEMA,
        "requested": requested,
        "result_contract_defined": result_contract_defined,
        "required_result_record_schema": (
            CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_RESULT_RECORD_SCHEMA
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
        "reported_allowed_result_count": reported_allowed_result_count,
        "reported_forbidden_result_count": reported_forbidden_result_count,
        "allowed_result_observed": allowed_result_observed,
        "no_forbidden_results": no_forbidden_results,
        "result_record_valid": result_record_valid,
        "result_record_rejected": result_record_rejected,
        "unsafe_result_record_count": unsafe_result_record_count,
        "missing_result_prerequisites": missing,
        "missing_result_prerequisite_count": len(missing),
        "durable_authoring_command_completion_result_accepted": False,
        "durable_authoring_command_completion_allowed": False,
        "durable_authoring_command_completed": False,
        "durable_authoring_command_application_allowed": False,
        "durable_authoring_command_application_applied": False,
        "asset_write_allowed": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_command_execution_allowed": False,
        "live_command_executed": False,
        "reported_completion_noop_result_count": reported_completion_noop_result_count,
        "reported_application_validation_result_count": (
            reported_application_validation_result_count
        ),
        "reported_completion_completed_result_count": (
            reported_completion_completed_result_count
        ),
        "reported_asset_write_result_count": reported_asset_write_result_count,
        "reported_package_dirty_result_count": reported_package_dirty_result_count,
        "reported_save_result_count": reported_save_result_count,
        "reported_delete_rename_result_count": reported_delete_rename_result_count,
        "reported_cleanup_result_count": reported_cleanup_result_count,
        "reported_allowed_evidence_command_count": application_summary.get(
            "reported_allowed_evidence_command_count",
            0,
        ),
        "reported_forbidden_evidence_command_count": application_summary.get(
            "reported_forbidden_evidence_command_count",
            0,
        ),
        "blocked_by": []
        if not requested
        else [
            "section_91_result_contract_does_not_accept_completed_write_or_save_results",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record only scoped completion result evidence after Section 90 application is valid",
            "reject result records that report completion, write, dirty package, save, delete, rename, or cleanup",
            "keep completion result readback behind a separate contract after result validation",
        ],
    }


def summarize_canary_durable_authoring_command_completion_results(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("result_record_rejected"))
    unsafe_count = sum(contract.get("unsafe_result_record_count", 0) for contract in requested)
    forbidden_result_count = sum(
        contract.get("reported_forbidden_result_count", 0) for contract in requested
    )
    forbidden_evidence_count = sum(
        contract.get("reported_forbidden_evidence_command_count", 0)
        for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("result_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_result_count == 0
            and forbidden_evidence_count == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_completion_result_accepted")
            )
            == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_completion_allowed")
            )
            == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_command_completed")) == 0
            and sum(1 for contract in requested if contract.get("asset_write_allowed")) == 0
            and sum(1 for contract in requested if contract.get("asset_write_performed")) == 0
            and sum(1 for contract in requested if contract.get("package_dirty_marked")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_delete_rename_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_dispatch_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_plan_emitted")) == 0
            and sum(1 for contract in requested if contract.get("live_command_execution_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_executed")) == 0
            else "failed"
        )
    return {
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_RESULT_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_authoring_command_completion_result_count": len(requested),
        "result_contract_defined_count": sum(
            1 for contract in requested if contract.get("result_contract_defined")
        ),
        "application_contract_ready_count": sum(
            1 for contract in requested if contract.get("application_contract_ready")
        ),
        "application_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("application_inputs_satisfied")
        ),
        "application_record_valid_count": sum(
            1 for contract in requested if contract.get("application_record_valid")
        ),
        "result_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("result_inputs_satisfied")
        ),
        "result_record_present_count": sum(
            1 for contract in requested if contract.get("result_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "result_scope_matches_count": sum(
            1 for contract in requested if contract.get("result_scope_matches")
        ),
        "explicit_result_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_result_authorized")
        ),
        "result_status_passed_count": sum(
            1 for contract in requested if contract.get("result_status_passed")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "allowed_result_observed_count": sum(
            1 for contract in requested if contract.get("allowed_result_observed")
        ),
        "no_forbidden_results_count": sum(
            1 for contract in requested if contract.get("no_forbidden_results")
        ),
        "result_record_valid_count": sum(
            1 for contract in requested if contract.get("result_record_valid")
        ),
        "result_record_rejected_count": rejected_count,
        "unsafe_result_record_count": unsafe_count,
        "missing_result_prerequisite_count": sum(
            contract.get("missing_result_prerequisite_count", 0)
            for contract in requested
        ),
        "reported_allowed_result_count": sum(
            contract.get("reported_allowed_result_count", 0) for contract in requested
        ),
        "reported_forbidden_result_count": forbidden_result_count,
        "reported_allowed_evidence_command_count": sum(
            contract.get("reported_allowed_evidence_command_count", 0)
            for contract in requested
        ),
        "reported_forbidden_evidence_command_count": forbidden_evidence_count,
        "durable_authoring_command_completion_result_accepted_count": sum(
            1
            for contract in requested
            if contract.get("durable_authoring_command_completion_result_accepted")
        ),
        "durable_authoring_command_completion_allowed_count": sum(
            1
            for contract in requested
            if contract.get("durable_authoring_command_completion_allowed")
        ),
        "durable_authoring_command_completed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_command_completed")
        ),
        "durable_authoring_command_application_allowed_count": sum(
            1
            for contract in requested
            if contract.get("durable_authoring_command_application_allowed")
        ),
        "durable_authoring_command_application_applied_count": sum(
            1
            for contract in requested
            if contract.get("durable_authoring_command_application_applied")
        ),
        "asset_write_allowed_count": sum(
            1 for contract in requested if contract.get("asset_write_allowed")
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
        "live_command_dispatch_allowed_count": sum(
            1 for contract in requested if contract.get("live_command_dispatch_allowed")
        ),
        "live_command_plan_emitted_count": sum(
            1 for contract in requested if contract.get("live_command_plan_emitted")
        ),
        "live_command_execution_allowed_count": sum(
            1 for contract in requested if contract.get("live_command_execution_allowed")
        ),
        "live_command_executed_count": sum(
            1 for contract in requested if contract.get("live_command_executed")
        ),
        "reported_completion_noop_result_count": sum(
            contract.get("reported_completion_noop_result_count", 0)
            for contract in requested
        ),
        "reported_application_validation_result_count": sum(
            contract.get("reported_application_validation_result_count", 0)
            for contract in requested
        ),
        "reported_completion_completed_result_count": sum(
            contract.get("reported_completion_completed_result_count", 0)
            for contract in requested
        ),
        "reported_asset_write_result_count": sum(
            contract.get("reported_asset_write_result_count", 0) for contract in requested
        ),
        "reported_package_dirty_result_count": sum(
            contract.get("reported_package_dirty_result_count", 0)
            for contract in requested
        ),
        "reported_save_result_count": sum(
            contract.get("reported_save_result_count", 0) for contract in requested
        ),
        "reported_delete_rename_result_count": sum(
            contract.get("reported_delete_rename_result_count", 0)
            for contract in requested
        ),
        "reported_cleanup_result_count": sum(
            contract.get("reported_cleanup_result_count", 0) for contract in requested
        ),
    }
