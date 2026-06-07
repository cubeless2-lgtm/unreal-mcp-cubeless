#!/usr/bin/env python
"""
Section 81 durable canary release promotion decision contract.

This contract defines the operator decision record required before durable
release promotion may be considered. It does not activate the durable executor,
save assets, or open durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_DURABLE_RELEASE_PROMOTION_DECISION_SCHEMA = (
    "section_81_durable_canary_release_promotion_decision_contract_v1"
)
CANARY_DURABLE_RELEASE_PROMOTION_DECISION_RECORD_SCHEMA = (
    "section_81_durable_canary_release_promotion_decision_record_v1"
)
CANARY_DURABLE_RELEASE_PROMOTION_DECISION_SUMMARY_SCHEMA = (
    "section_81_durable_canary_release_promotion_decision_summary_v1"
)
EXPECTED_PROMOTION_SCOPE = "durable_canary_release_promotion_only"


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_durable_release_promotion_decision_contract(
    requested: bool,
    evidence_admission_summary: Dict[str, Any],
    promotion_decision_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    promotion_decision_record = promotion_decision_record or {}
    decision_record_present = bool(promotion_decision_record)
    evidence_admission_contract_ready = bool(
        requested
        and evidence_admission_summary.get("status") == "passed"
        and evidence_admission_summary.get("evidence_admission_contract_defined_count") == 1
        and evidence_admission_summary.get("evidence_record_rejected_count") == 0
        and evidence_admission_summary.get("unsafe_evidence_record_count") == 0
        and evidence_admission_summary.get("reported_forbidden_evidence_command_count") == 0
        and evidence_admission_summary.get("durable_executor_may_open_after_evidence_admission_count") == 0
        and evidence_admission_summary.get("save_delete_rename_allowed_count") == 0
    )
    execution_evidence_admitted = bool(
        evidence_admission_summary.get("execution_evidence_admitted_count") == 1
    )
    allowed_evidence_command_observed = bool(
        evidence_admission_summary.get("allowed_evidence_command_observed_count") == 1
    )
    no_forbidden_evidence_commands = bool(
        evidence_admission_summary.get("no_forbidden_evidence_commands_count") == 1
    )
    evidence_ready_for_promotion = bool(
        execution_evidence_admitted
        and allowed_evidence_command_observed
        and no_forbidden_evidence_commands
    )
    record_schema_matches = bool(
        decision_record_present
        and promotion_decision_record.get("schema")
        == CANARY_DURABLE_RELEASE_PROMOTION_DECISION_RECORD_SCHEMA
    )
    promotion_scope_matches = bool(
        decision_record_present
        and promotion_decision_record.get("promotion_scope") == EXPECTED_PROMOTION_SCOPE
    )
    explicit_promotion_authorized = bool(
        decision_record_present
        and promotion_decision_record.get("explicit_durable_release_promotion_authorized") is True
    )
    no_save_delete_rename_acknowledged = bool(
        decision_record_present
        and promotion_decision_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    unsafe_promotion_decision_record_count = sum(
        int(_authorized(promotion_decision_record.get(key)))
        for key in (
            "durable_authoring_authorized",
            "durable_executor_activation_authorized",
            "durable_executor_open_authorized",
            "save_asset_authorized",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
        )
    )
    promotion_decision_contract_defined = bool(requested and evidence_admission_contract_ready)
    promotion_decision_record_valid = bool(
        promotion_decision_contract_defined
        and evidence_ready_for_promotion
        and record_schema_matches
        and promotion_scope_matches
        and explicit_promotion_authorized
        and no_save_delete_rename_acknowledged
        and unsafe_promotion_decision_record_count == 0
    )
    missing = []
    if requested:
        if not execution_evidence_admitted:
            missing.append("section_80_execution_evidence_admitted")
        if not allowed_evidence_command_observed:
            missing.append("section_80_allowed_evidence_command_observed")
        if not no_forbidden_evidence_commands:
            missing.append("section_80_no_forbidden_evidence_commands")
        if not decision_record_present:
            missing.append("durable_release_promotion_decision_record_present")
        if not record_schema_matches:
            missing.append("durable_release_promotion_decision_record_schema")
        if not promotion_scope_matches:
            missing.append("durable_canary_release_promotion_only_scope")
        if not explicit_promotion_authorized:
            missing.append("explicit_durable_release_promotion_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        missing.append("separate_durable_executor_activation_contract")
    promotion_decision_record_rejected = bool(
        decision_record_present and not promotion_decision_record_valid
    )
    return {
        "id": "durable_canary_release_promotion_decision",
        "schema": CANARY_DURABLE_RELEASE_PROMOTION_DECISION_SCHEMA,
        "requested": requested,
        "promotion_decision_contract_defined": promotion_decision_contract_defined,
        "required_promotion_decision_record_schema": (
            CANARY_DURABLE_RELEASE_PROMOTION_DECISION_RECORD_SCHEMA if requested else ""
        ),
        "expected_promotion_scope": EXPECTED_PROMOTION_SCOPE if requested else "",
        "evidence_admission_contract_ready": evidence_admission_contract_ready,
        "execution_evidence_admitted": execution_evidence_admitted,
        "allowed_evidence_command_observed": allowed_evidence_command_observed,
        "no_forbidden_evidence_commands": no_forbidden_evidence_commands,
        "evidence_ready_for_promotion": evidence_ready_for_promotion,
        "decision_record_present": decision_record_present,
        "record_schema_matches": record_schema_matches,
        "promotion_scope_matches": promotion_scope_matches,
        "explicit_promotion_authorized": explicit_promotion_authorized,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "promotion_decision_record_valid": promotion_decision_record_valid,
        "promotion_decision_record_rejected": promotion_decision_record_rejected,
        "unsafe_promotion_decision_record_count": unsafe_promotion_decision_record_count,
        "missing_promotion_prerequisites": missing,
        "missing_promotion_prerequisite_count": len(missing),
        "durable_release_promotion_allowed": False,
        "durable_release_promoted": False,
        "durable_executor_may_open_after_promotion_decision": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_command_execution_allowed": False,
        "live_command_executed": False,
        "reported_allowed_evidence_command_count": evidence_admission_summary.get(
            "reported_allowed_evidence_command_count",
            0,
        ),
        "reported_forbidden_evidence_command_count": evidence_admission_summary.get(
            "reported_forbidden_evidence_command_count",
            0,
        ),
        "blocked_by": []
        if not requested
        else [
            "section_81_promotion_decision_does_not_activate_durable_executor",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped durable release promotion decision only after Section 80 admits evidence",
            "reject promotion decisions that authorize executor activation, save, delete, rename, cleanup, or durable authoring",
            "keep durable executor activation behind a separate contract after promotion decision validation",
        ],
    }


def summarize_canary_durable_release_promotion_decisions(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("promotion_decision_record_rejected"))
    unsafe_count = sum(
        contract.get("unsafe_promotion_decision_record_count", 0) for contract in requested
    )
    forbidden_evidence_count = sum(
        contract.get("reported_forbidden_evidence_command_count", 0) for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("promotion_decision_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_evidence_count == 0
            and sum(1 for contract in requested if contract.get("durable_release_promotion_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_release_promoted")) == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_executor_may_open_after_promotion_decision")
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
        "schema": CANARY_DURABLE_RELEASE_PROMOTION_DECISION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_release_promotion_decision_count": len(requested),
        "promotion_decision_contract_defined_count": sum(
            1 for contract in requested if contract.get("promotion_decision_contract_defined")
        ),
        "evidence_admission_contract_ready_count": sum(
            1 for contract in requested if contract.get("evidence_admission_contract_ready")
        ),
        "execution_evidence_admitted_count": sum(
            1 for contract in requested if contract.get("execution_evidence_admitted")
        ),
        "allowed_evidence_command_observed_count": sum(
            1 for contract in requested if contract.get("allowed_evidence_command_observed")
        ),
        "no_forbidden_evidence_commands_count": sum(
            1 for contract in requested if contract.get("no_forbidden_evidence_commands")
        ),
        "evidence_ready_for_promotion_count": sum(
            1 for contract in requested if contract.get("evidence_ready_for_promotion")
        ),
        "decision_record_present_count": sum(
            1 for contract in requested if contract.get("decision_record_present")
        ),
        "record_schema_matches_count": sum(1 for contract in requested if contract.get("record_schema_matches")),
        "promotion_scope_matches_count": sum(
            1 for contract in requested if contract.get("promotion_scope_matches")
        ),
        "explicit_promotion_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_promotion_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "promotion_decision_record_valid_count": sum(
            1 for contract in requested if contract.get("promotion_decision_record_valid")
        ),
        "promotion_decision_record_rejected_count": rejected_count,
        "unsafe_promotion_decision_record_count": unsafe_count,
        "missing_promotion_prerequisite_count": sum(
            contract.get("missing_promotion_prerequisite_count", 0) for contract in requested
        ),
        "durable_release_promotion_allowed_count": sum(
            1 for contract in requested if contract.get("durable_release_promotion_allowed")
        ),
        "durable_release_promoted_count": sum(
            1 for contract in requested if contract.get("durable_release_promoted")
        ),
        "durable_executor_may_open_after_promotion_decision_count": sum(
            1
            for contract in requested
            if contract.get("durable_executor_may_open_after_promotion_decision")
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
        "reported_allowed_evidence_command_count": sum(
            contract.get("reported_allowed_evidence_command_count", 0) for contract in requested
        ),
        "reported_forbidden_evidence_command_count": forbidden_evidence_count,
    }
