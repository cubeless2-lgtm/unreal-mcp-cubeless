#!/usr/bin/env python
"""
Section 80 durable canary live command execution evidence admission contract.

This contract validates the shape of future live command execution evidence.
It does not execute live commands, save assets, or open durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_LIVE_COMMAND_EXECUTION_EVIDENCE_ADMISSION_SCHEMA = (
    "section_80_durable_canary_live_command_execution_evidence_admission_contract_v1"
)
CANARY_LIVE_COMMAND_EXECUTION_EVIDENCE_RECORD_SCHEMA = (
    "section_80_durable_canary_live_command_execution_evidence_record_v1"
)
CANARY_LIVE_COMMAND_EXECUTION_EVIDENCE_ADMISSION_SUMMARY_SCHEMA = (
    "section_80_durable_canary_live_command_execution_evidence_admission_summary_v1"
)
EXPECTED_EVIDENCE_SCOPE = "durable_canary_live_command_execution_evidence_only"


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


def build_canary_live_command_execution_evidence_admission_contract(
    requested: bool,
    execution_release_summary: Dict[str, Any],
    evidence_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    evidence_record = evidence_record or {}
    evidence_record_present = bool(evidence_record)
    execution_release_contract_ready = bool(
        requested
        and execution_release_summary.get("status") == "passed"
        and execution_release_summary.get("execution_release_contract_defined_count") == 1
        and execution_release_summary.get("execution_release_record_rejected_count") == 0
        and execution_release_summary.get("unsafe_execution_release_record_count") == 0
        and execution_release_summary.get("durable_executor_may_open_after_execution_release_count") == 0
        and execution_release_summary.get("save_delete_rename_allowed_count") == 0
    )
    execution_inputs_satisfied = bool(
        execution_release_summary.get("execution_inputs_satisfied_count") == 1
    )
    execution_release_record_valid = bool(
        execution_release_summary.get("execution_release_record_valid_count") == 1
    )
    section_79_live_command_executed = bool(
        execution_release_summary.get("live_command_executed_count") == 1
    )
    evidence_inputs_satisfied = bool(
        execution_inputs_satisfied
        and execution_release_record_valid
        and section_79_live_command_executed
    )
    record_schema_matches = bool(
        evidence_record_present
        and evidence_record.get("schema") == CANARY_LIVE_COMMAND_EXECUTION_EVIDENCE_RECORD_SCHEMA
    )
    evidence_scope_matches = bool(
        evidence_record_present and evidence_record.get("evidence_scope") == EXPECTED_EVIDENCE_SCOPE
    )
    explicit_evidence_admission_authorized = bool(
        evidence_record_present
        and evidence_record.get("explicit_live_command_execution_evidence_admission_authorized") is True
    )
    evidence_status_passed = bool(evidence_record_present and evidence_record.get("status") == "passed")
    no_save_delete_rename_acknowledged = bool(
        evidence_record_present
        and evidence_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    reported_live_creation_command_count = _count(evidence_record.get("reported_live_creation_command_count"))
    reported_live_compile_command_count = _count(evidence_record.get("reported_live_compile_command_count"))
    reported_live_marker_write_command_count = _count(
        evidence_record.get("reported_live_marker_write_command_count")
    )
    reported_live_marker_readback_command_count = _count(
        evidence_record.get("reported_live_marker_readback_command_count")
    )
    reported_live_save_command_count = _count(evidence_record.get("reported_live_save_command_count"))
    reported_live_delete_rename_command_count = _count(
        evidence_record.get("reported_live_delete_rename_command_count")
    )
    reported_live_cleanup_command_count = _count(evidence_record.get("reported_live_cleanup_command_count"))
    reported_allowed_evidence_command_count = (
        reported_live_creation_command_count
        + reported_live_compile_command_count
        + reported_live_marker_write_command_count
        + reported_live_marker_readback_command_count
    )
    reported_forbidden_evidence_command_count = (
        reported_live_save_command_count
        + reported_live_delete_rename_command_count
        + reported_live_cleanup_command_count
    )
    allowed_evidence_command_observed = bool(
        evidence_record_present and reported_allowed_evidence_command_count > 0
    )
    no_forbidden_evidence_commands = bool(
        evidence_record_present and reported_forbidden_evidence_command_count == 0
    )
    unsafe_evidence_record_count = (
        sum(
            int(_attempted(evidence_record.get(key)))
            for key in (
                "authoring_attempted",
                "durable_authoring_attempted",
                "durable_authoring_authorized",
                "save_asset_attempted",
                "save_asset_authorized",
                "delete_asset_attempted",
                "delete_asset_authorized",
                "rename_asset_attempted",
                "rename_asset_authorized",
                "cleanup_attempted",
                "cleanup_authorized",
            )
        )
        + reported_forbidden_evidence_command_count
    )
    evidence_admission_contract_defined = bool(requested and execution_release_contract_ready)
    execution_evidence_admitted = bool(
        evidence_admission_contract_defined
        and evidence_inputs_satisfied
        and record_schema_matches
        and evidence_scope_matches
        and explicit_evidence_admission_authorized
        and evidence_status_passed
        and no_save_delete_rename_acknowledged
        and allowed_evidence_command_observed
        and no_forbidden_evidence_commands
        and unsafe_evidence_record_count == 0
    )
    missing: list[str] = []
    if requested:
        if not execution_inputs_satisfied:
            missing.append("section_79_execution_inputs_satisfied")
        if not execution_release_record_valid:
            missing.append("section_79_execution_release_record_valid")
        if not section_79_live_command_executed:
            missing.append("section_79_live_command_executed")
        if not evidence_record_present:
            missing.append("live_command_execution_evidence_record_present")
        if not record_schema_matches:
            missing.append("live_command_execution_evidence_record_schema")
        if not evidence_scope_matches:
            missing.append("durable_canary_live_command_execution_evidence_only_scope")
        if not explicit_evidence_admission_authorized:
            missing.append("explicit_live_command_execution_evidence_admission_authorization")
        if not evidence_status_passed:
            missing.append("live_command_execution_evidence_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not allowed_evidence_command_observed:
            missing.append("allowed_live_command_execution_evidence_observed")
        if not no_forbidden_evidence_commands:
            missing.append("no_forbidden_live_command_execution_evidence")
        missing.append("separate_durable_release_promotion_decision")
    evidence_record_rejected = bool(evidence_record_present and not execution_evidence_admitted)
    return {
        "id": "durable_canary_live_command_execution_evidence_admission",
        "schema": CANARY_LIVE_COMMAND_EXECUTION_EVIDENCE_ADMISSION_SCHEMA,
        "requested": requested,
        "evidence_admission_contract_defined": evidence_admission_contract_defined,
        "required_evidence_record_schema": (
            CANARY_LIVE_COMMAND_EXECUTION_EVIDENCE_RECORD_SCHEMA if requested else ""
        ),
        "expected_evidence_scope": EXPECTED_EVIDENCE_SCOPE if requested else "",
        "execution_release_contract_ready": execution_release_contract_ready,
        "execution_inputs_satisfied": execution_inputs_satisfied,
        "execution_release_record_valid": execution_release_record_valid,
        "section_79_live_command_executed": section_79_live_command_executed,
        "evidence_inputs_satisfied": evidence_inputs_satisfied,
        "evidence_record_present": evidence_record_present,
        "record_schema_matches": record_schema_matches,
        "evidence_scope_matches": evidence_scope_matches,
        "explicit_evidence_admission_authorized": explicit_evidence_admission_authorized,
        "evidence_status_passed": evidence_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "reported_allowed_evidence_command_count": reported_allowed_evidence_command_count,
        "reported_forbidden_evidence_command_count": reported_forbidden_evidence_command_count,
        "allowed_evidence_command_observed": allowed_evidence_command_observed,
        "no_forbidden_evidence_commands": no_forbidden_evidence_commands,
        "execution_evidence_admitted": execution_evidence_admitted,
        "evidence_record_rejected": evidence_record_rejected,
        "unsafe_evidence_record_count": unsafe_evidence_record_count,
        "missing_evidence_prerequisites": missing,
        "missing_evidence_prerequisite_count": len(missing),
        "durable_promotion_allowed": False,
        "durable_executor_may_open_after_evidence_admission": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_command_execution_allowed": False,
        "live_command_executed": False,
        "reported_live_creation_command_count": reported_live_creation_command_count,
        "reported_live_compile_command_count": reported_live_compile_command_count,
        "reported_live_marker_write_command_count": reported_live_marker_write_command_count,
        "reported_live_marker_readback_command_count": reported_live_marker_readback_command_count,
        "reported_live_save_command_count": reported_live_save_command_count,
        "reported_live_delete_rename_command_count": reported_live_delete_rename_command_count,
        "reported_live_cleanup_command_count": reported_live_cleanup_command_count,
        "blocked_by": []
        if not requested
        else [
            "section_80_evidence_admission_does_not_open_durable_execution",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "admit only scoped live command execution evidence after Section 79 release and execution evidence exist",
            "reject evidence that reports save, delete, rename, cleanup, or general durable authoring",
            "keep durable promotion behind a separate release decision after evidence admission",
        ],
    }


def summarize_canary_live_command_execution_evidence_admissions(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("evidence_record_rejected"))
    unsafe_count = sum(contract.get("unsafe_evidence_record_count", 0) for contract in requested)
    forbidden_evidence_count = sum(
        contract.get("reported_forbidden_evidence_command_count", 0) for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("evidence_admission_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_evidence_count == 0
            and sum(1 for contract in requested if contract.get("durable_promotion_allowed")) == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_executor_may_open_after_evidence_admission")
            )
            == 0
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
        "schema": CANARY_LIVE_COMMAND_EXECUTION_EVIDENCE_ADMISSION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_live_command_execution_evidence_admission_count": len(requested),
        "evidence_admission_contract_defined_count": sum(
            1 for contract in requested if contract.get("evidence_admission_contract_defined")
        ),
        "execution_release_contract_ready_count": sum(
            1 for contract in requested if contract.get("execution_release_contract_ready")
        ),
        "execution_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("execution_inputs_satisfied")
        ),
        "execution_release_record_valid_count": sum(
            1 for contract in requested if contract.get("execution_release_record_valid")
        ),
        "section_79_live_command_executed_count": sum(
            1 for contract in requested if contract.get("section_79_live_command_executed")
        ),
        "evidence_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("evidence_inputs_satisfied")
        ),
        "evidence_record_present_count": sum(
            1 for contract in requested if contract.get("evidence_record_present")
        ),
        "record_schema_matches_count": sum(1 for contract in requested if contract.get("record_schema_matches")),
        "evidence_scope_matches_count": sum(
            1 for contract in requested if contract.get("evidence_scope_matches")
        ),
        "explicit_evidence_admission_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_evidence_admission_authorized")
        ),
        "evidence_status_passed_count": sum(
            1 for contract in requested if contract.get("evidence_status_passed")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "allowed_evidence_command_observed_count": sum(
            1 for contract in requested if contract.get("allowed_evidence_command_observed")
        ),
        "no_forbidden_evidence_commands_count": sum(
            1 for contract in requested if contract.get("no_forbidden_evidence_commands")
        ),
        "execution_evidence_admitted_count": sum(
            1 for contract in requested if contract.get("execution_evidence_admitted")
        ),
        "evidence_record_rejected_count": rejected_count,
        "unsafe_evidence_record_count": unsafe_count,
        "missing_evidence_prerequisite_count": sum(
            contract.get("missing_evidence_prerequisite_count", 0) for contract in requested
        ),
        "reported_allowed_evidence_command_count": sum(
            contract.get("reported_allowed_evidence_command_count", 0) for contract in requested
        ),
        "reported_forbidden_evidence_command_count": forbidden_evidence_count,
        "durable_promotion_allowed_count": sum(
            1 for contract in requested if contract.get("durable_promotion_allowed")
        ),
        "durable_executor_may_open_after_evidence_admission_count": sum(
            1
            for contract in requested
            if contract.get("durable_executor_may_open_after_evidence_admission")
        ),
        "durable_authoring_allowed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_allowed")
        ),
        "save_delete_rename_allowed_count": sum(
            1 for contract in requested if contract.get("save_delete_rename_allowed")
        ),
        "cleanup_allowed_count": sum(1 for contract in requested if contract.get("cleanup_allowed")),
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
        "reported_live_creation_command_count": sum(
            contract.get("reported_live_creation_command_count", 0) for contract in requested
        ),
        "reported_live_compile_command_count": sum(
            contract.get("reported_live_compile_command_count", 0) for contract in requested
        ),
        "reported_live_marker_write_command_count": sum(
            contract.get("reported_live_marker_write_command_count", 0) for contract in requested
        ),
        "reported_live_marker_readback_command_count": sum(
            contract.get("reported_live_marker_readback_command_count", 0) for contract in requested
        ),
        "reported_live_save_command_count": sum(
            contract.get("reported_live_save_command_count", 0) for contract in requested
        ),
        "reported_live_delete_rename_command_count": sum(
            contract.get("reported_live_delete_rename_command_count", 0) for contract in requested
        ),
        "reported_live_cleanup_command_count": sum(
            contract.get("reported_live_cleanup_command_count", 0) for contract in requested
        ),
    }
