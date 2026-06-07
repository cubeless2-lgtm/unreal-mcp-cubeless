#!/usr/bin/env python
"""
Section 90 durable canary authoring command completion application contract.

This contract defines the scoped application record required after a future
completion decision is valid. It does not apply completion, write packages, save
assets, or open durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_APPLICATION_SCHEMA = (
    "section_90_durable_canary_authoring_command_completion_application_contract_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_APPLICATION_RECORD_SCHEMA = (
    "section_90_durable_canary_authoring_command_completion_application_record_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_APPLICATION_SUMMARY_SCHEMA = (
    "section_90_durable_canary_authoring_command_completion_application_summary_v1"
)
EXPECTED_APPLICATION_SCOPE = "durable_canary_authoring_command_completion_application_only"


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_durable_authoring_command_completion_application_contract(
    requested: bool,
    completion_decision_summary: Dict[str, Any],
    application_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    application_record = application_record or {}
    application_record_present = bool(application_record)
    completion_decision_contract_ready = bool(
        requested
        and completion_decision_summary.get("status") == "passed"
        and completion_decision_summary.get("completion_decision_contract_defined_count") == 1
        and completion_decision_summary.get("completion_decision_record_rejected_count") == 0
        and completion_decision_summary.get("unsafe_completion_decision_record_count") == 0
        and completion_decision_summary.get("reported_forbidden_evidence_command_count") == 0
        and completion_decision_summary.get("durable_authoring_command_completion_allowed_count") == 0
        and completion_decision_summary.get("durable_authoring_command_completed_count") == 0
        and completion_decision_summary.get("durable_authoring_command_dispatch_allowed_count") == 0
        and completion_decision_summary.get("durable_authoring_command_dispatched_count") == 0
        and completion_decision_summary.get("durable_authoring_command_execution_allowed_count") == 0
        and completion_decision_summary.get("durable_authoring_command_executed_count") == 0
        and completion_decision_summary.get("durable_promotion_allowed_count") == 0
        and completion_decision_summary.get("durable_authoring_enabled_count") == 0
        and completion_decision_summary.get("durable_authoring_allowed_count") == 0
        and completion_decision_summary.get("save_delete_rename_allowed_count") == 0
        and completion_decision_summary.get("cleanup_allowed_count") == 0
        and completion_decision_summary.get("live_command_dispatch_allowed_count") == 0
        and completion_decision_summary.get("live_command_execution_allowed_count") == 0
        and completion_decision_summary.get("live_command_executed_count") == 0
    )
    evidence_ready_for_completion = bool(
        completion_decision_summary.get("evidence_ready_for_completion_count") == 1
    )
    completion_decision_record_valid = bool(
        completion_decision_summary.get("completion_decision_record_valid_count") == 1
    )
    application_inputs_satisfied = bool(
        evidence_ready_for_completion and completion_decision_record_valid
    )
    record_schema_matches = bool(
        application_record_present
        and application_record.get("schema")
        == CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_APPLICATION_RECORD_SCHEMA
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
    no_save_delete_rename_acknowledged = bool(
        application_record_present
        and application_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    unsafe_application_record_count = sum(
        int(_authorized(application_record.get(key)))
        for key in (
            "durable_authoring_command_completion_allowed",
            "durable_authoring_command_completed",
            "durable_authoring_command_application_allowed",
            "durable_authoring_command_application_applied",
            "asset_write_performed",
            "package_dirty_marked",
            "durable_authoring_command_dispatch_allowed",
            "durable_authoring_command_dispatched",
            "durable_authoring_command_execution_allowed",
            "durable_authoring_command_executed",
            "durable_release_promotion_allowed",
            "durable_release_promoted",
            "durable_authoring_enabled",
            "durable_authoring_allowed",
            "save_asset_authorized",
            "save_asset_executed",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
            "live_command_dispatch_authorized",
            "live_command_dispatch_performed",
            "live_command_execution_authorized",
            "live_command_execution_performed",
            "live_command_executed",
        )
    )
    application_contract_defined = bool(requested and completion_decision_contract_ready)
    application_record_valid = bool(
        application_contract_defined
        and application_inputs_satisfied
        and record_schema_matches
        and application_scope_matches
        and explicit_application_authorized
        and no_save_delete_rename_acknowledged
        and unsafe_application_record_count == 0
    )
    missing = []
    if requested:
        if not evidence_ready_for_completion:
            missing.append("section_89_evidence_ready_for_completion")
        if not completion_decision_record_valid:
            missing.append("section_89_completion_decision_record_valid")
        if not application_record_present:
            missing.append("durable_authoring_command_completion_application_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_completion_application_record_schema")
        if not application_scope_matches:
            missing.append("durable_canary_authoring_command_completion_application_only_scope")
        if not explicit_application_authorized:
            missing.append("explicit_durable_authoring_command_completion_application_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        missing.append("separate_durable_authoring_command_completion_result_contract")
    application_record_rejected = bool(application_record_present and not application_record_valid)
    return {
        "id": "durable_canary_authoring_command_completion_application",
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_APPLICATION_SCHEMA,
        "requested": requested,
        "application_contract_defined": application_contract_defined,
        "required_application_record_schema": (
            CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_APPLICATION_RECORD_SCHEMA
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
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "application_record_valid": application_record_valid,
        "application_record_rejected": application_record_rejected,
        "unsafe_application_record_count": unsafe_application_record_count,
        "missing_application_prerequisites": missing,
        "missing_application_prerequisite_count": len(missing),
        "durable_authoring_command_completion_allowed": False,
        "durable_authoring_command_completed": False,
        "durable_authoring_command_application_allowed": False,
        "durable_authoring_command_application_applied": False,
        "asset_write_allowed": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "durable_authoring_command_dispatch_allowed": False,
        "durable_authoring_command_dispatched": False,
        "durable_authoring_command_execution_allowed": False,
        "durable_authoring_command_executed": False,
        "durable_promotion_allowed": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_command_execution_allowed": False,
        "live_command_executed": False,
        "reported_allowed_evidence_command_count": completion_decision_summary.get(
            "reported_allowed_evidence_command_count",
            0,
        ),
        "reported_forbidden_evidence_command_count": completion_decision_summary.get(
            "reported_forbidden_evidence_command_count",
            0,
        ),
        "blocked_by": []
        if not requested
        else [
            "section_90_application_contract_does_not_apply_write_or_save",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped durable authoring command completion application only after Section 89 decision is valid",
            "reject application records that claim completion, write, save, delete, rename, cleanup, durable authoring, or live command actions",
            "keep durable authoring command completion result behind a separate contract after application validation",
        ],
    }


def summarize_canary_durable_authoring_command_completion_applications(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("application_record_rejected"))
    unsafe_count = sum(contract.get("unsafe_application_record_count", 0) for contract in requested)
    forbidden_evidence_count = sum(
        contract.get("reported_forbidden_evidence_command_count", 0)
        for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("application_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_evidence_count == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_completion_allowed")
            )
            == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_command_completed")) == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_application_allowed")
            )
            == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_application_applied")
            )
            == 0
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
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_APPLICATION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_authoring_command_completion_application_count": len(requested),
        "application_contract_defined_count": sum(
            1 for contract in requested if contract.get("application_contract_defined")
        ),
        "completion_decision_contract_ready_count": sum(
            1 for contract in requested if contract.get("completion_decision_contract_ready")
        ),
        "evidence_ready_for_completion_count": sum(
            1 for contract in requested if contract.get("evidence_ready_for_completion")
        ),
        "completion_decision_record_valid_count": sum(
            1 for contract in requested if contract.get("completion_decision_record_valid")
        ),
        "application_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("application_inputs_satisfied")
        ),
        "application_record_present_count": sum(
            1 for contract in requested if contract.get("application_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "application_scope_matches_count": sum(
            1 for contract in requested if contract.get("application_scope_matches")
        ),
        "explicit_application_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_application_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "application_record_valid_count": sum(
            1 for contract in requested if contract.get("application_record_valid")
        ),
        "application_record_rejected_count": rejected_count,
        "unsafe_application_record_count": unsafe_count,
        "missing_application_prerequisite_count": sum(
            contract.get("missing_application_prerequisite_count", 0)
            for contract in requested
        ),
        "reported_allowed_evidence_command_count": sum(
            contract.get("reported_allowed_evidence_command_count", 0)
            for contract in requested
        ),
        "reported_forbidden_evidence_command_count": forbidden_evidence_count,
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
        "durable_authoring_command_dispatch_allowed_count": sum(
            1
            for contract in requested
            if contract.get("durable_authoring_command_dispatch_allowed")
        ),
        "durable_authoring_command_dispatched_count": sum(
            1 for contract in requested if contract.get("durable_authoring_command_dispatched")
        ),
        "durable_authoring_command_execution_allowed_count": sum(
            1
            for contract in requested
            if contract.get("durable_authoring_command_execution_allowed")
        ),
        "durable_authoring_command_executed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_command_executed")
        ),
        "durable_promotion_allowed_count": sum(
            1 for contract in requested if contract.get("durable_promotion_allowed")
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
    }
