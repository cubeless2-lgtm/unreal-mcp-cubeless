#!/usr/bin/env python
"""
Section 82 durable canary executor activation contract.

This contract defines the operator activation record required before a future
durable executor open may be considered. It does not open the durable executor,
save assets, or enable durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_DURABLE_EXECUTOR_ACTIVATION_SCHEMA = (
    "section_82_durable_canary_executor_activation_contract_v1"
)
CANARY_DURABLE_EXECUTOR_ACTIVATION_RECORD_SCHEMA = (
    "section_82_durable_canary_executor_activation_record_v1"
)
CANARY_DURABLE_EXECUTOR_ACTIVATION_SUMMARY_SCHEMA = (
    "section_82_durable_canary_executor_activation_summary_v1"
)
EXPECTED_ACTIVATION_SCOPE = "durable_canary_executor_activation_only"


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_durable_executor_activation_contract(
    requested: bool,
    promotion_decision_summary: Dict[str, Any],
    activation_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    activation_record = activation_record or {}
    activation_record_present = bool(activation_record)
    promotion_decision_contract_ready = bool(
        requested
        and promotion_decision_summary.get("status") == "passed"
        and promotion_decision_summary.get("promotion_decision_contract_defined_count") == 1
        and promotion_decision_summary.get("promotion_decision_record_rejected_count") == 0
        and promotion_decision_summary.get("unsafe_promotion_decision_record_count") == 0
        and promotion_decision_summary.get("reported_forbidden_evidence_command_count") == 0
        and promotion_decision_summary.get("durable_executor_may_open_after_promotion_decision_count") == 0
        and promotion_decision_summary.get("save_delete_rename_allowed_count") == 0
    )
    evidence_ready_for_promotion = bool(
        promotion_decision_summary.get("evidence_ready_for_promotion_count") == 1
    )
    promotion_decision_record_valid = bool(
        promotion_decision_summary.get("promotion_decision_record_valid_count") == 1
    )
    activation_inputs_satisfied = bool(
        evidence_ready_for_promotion and promotion_decision_record_valid
    )
    record_schema_matches = bool(
        activation_record_present
        and activation_record.get("schema") == CANARY_DURABLE_EXECUTOR_ACTIVATION_RECORD_SCHEMA
    )
    activation_scope_matches = bool(
        activation_record_present
        and activation_record.get("activation_scope") == EXPECTED_ACTIVATION_SCOPE
    )
    explicit_activation_authorized = bool(
        activation_record_present
        and activation_record.get("explicit_durable_executor_activation_authorized") is True
    )
    no_save_delete_rename_acknowledged = bool(
        activation_record_present
        and activation_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    unsafe_activation_record_count = sum(
        int(_authorized(activation_record.get(key)))
        for key in (
            "durable_authoring_authorized",
            "durable_executor_open_authorized",
            "save_asset_authorized",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
        )
    )
    activation_contract_defined = bool(requested and promotion_decision_contract_ready)
    activation_record_valid = bool(
        activation_contract_defined
        and activation_inputs_satisfied
        and record_schema_matches
        and activation_scope_matches
        and explicit_activation_authorized
        and no_save_delete_rename_acknowledged
        and unsafe_activation_record_count == 0
    )
    missing = []
    if requested:
        if not evidence_ready_for_promotion:
            missing.append("section_81_evidence_ready_for_promotion")
        if not promotion_decision_record_valid:
            missing.append("section_81_promotion_decision_record_valid")
        if not activation_record_present:
            missing.append("durable_executor_activation_record_present")
        if not record_schema_matches:
            missing.append("durable_executor_activation_record_schema")
        if not activation_scope_matches:
            missing.append("durable_canary_executor_activation_only_scope")
        if not explicit_activation_authorized:
            missing.append("explicit_durable_executor_activation_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        missing.append("separate_durable_executor_open_contract")
    activation_record_rejected = bool(activation_record_present and not activation_record_valid)
    return {
        "id": "durable_canary_executor_activation",
        "schema": CANARY_DURABLE_EXECUTOR_ACTIVATION_SCHEMA,
        "requested": requested,
        "activation_contract_defined": activation_contract_defined,
        "required_activation_record_schema": (
            CANARY_DURABLE_EXECUTOR_ACTIVATION_RECORD_SCHEMA if requested else ""
        ),
        "expected_activation_scope": EXPECTED_ACTIVATION_SCOPE if requested else "",
        "promotion_decision_contract_ready": promotion_decision_contract_ready,
        "evidence_ready_for_promotion": evidence_ready_for_promotion,
        "promotion_decision_record_valid": promotion_decision_record_valid,
        "activation_inputs_satisfied": activation_inputs_satisfied,
        "activation_record_present": activation_record_present,
        "record_schema_matches": record_schema_matches,
        "activation_scope_matches": activation_scope_matches,
        "explicit_activation_authorized": explicit_activation_authorized,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "activation_record_valid": activation_record_valid,
        "activation_record_rejected": activation_record_rejected,
        "unsafe_activation_record_count": unsafe_activation_record_count,
        "missing_activation_prerequisites": missing,
        "missing_activation_prerequisite_count": len(missing),
        "durable_executor_activation_allowed": False,
        "durable_executor_activated": False,
        "durable_executor_may_open_after_activation": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_command_execution_allowed": False,
        "live_command_executed": False,
        "reported_allowed_evidence_command_count": promotion_decision_summary.get(
            "reported_allowed_evidence_command_count",
            0,
        ),
        "reported_forbidden_evidence_command_count": promotion_decision_summary.get(
            "reported_forbidden_evidence_command_count",
            0,
        ),
        "blocked_by": []
        if not requested
        else [
            "section_82_activation_contract_does_not_open_durable_executor",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped durable executor activation only after Section 81 promotion decision is valid",
            "reject activation records that authorize durable authoring, executor open, save, delete, rename, or cleanup",
            "keep durable executor open behind a separate contract after activation validation",
        ],
    }


def summarize_canary_durable_executor_activations(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("activation_record_rejected"))
    unsafe_count = sum(contract.get("unsafe_activation_record_count", 0) for contract in requested)
    forbidden_evidence_count = sum(
        contract.get("reported_forbidden_evidence_command_count", 0) for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("activation_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_evidence_count == 0
            and sum(1 for contract in requested if contract.get("durable_executor_activation_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_activated")) == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_executor_may_open_after_activation")
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
        "schema": CANARY_DURABLE_EXECUTOR_ACTIVATION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_executor_activation_count": len(requested),
        "activation_contract_defined_count": sum(
            1 for contract in requested if contract.get("activation_contract_defined")
        ),
        "promotion_decision_contract_ready_count": sum(
            1 for contract in requested if contract.get("promotion_decision_contract_ready")
        ),
        "evidence_ready_for_promotion_count": sum(
            1 for contract in requested if contract.get("evidence_ready_for_promotion")
        ),
        "promotion_decision_record_valid_count": sum(
            1 for contract in requested if contract.get("promotion_decision_record_valid")
        ),
        "activation_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("activation_inputs_satisfied")
        ),
        "activation_record_present_count": sum(
            1 for contract in requested if contract.get("activation_record_present")
        ),
        "record_schema_matches_count": sum(1 for contract in requested if contract.get("record_schema_matches")),
        "activation_scope_matches_count": sum(
            1 for contract in requested if contract.get("activation_scope_matches")
        ),
        "explicit_activation_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_activation_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "activation_record_valid_count": sum(
            1 for contract in requested if contract.get("activation_record_valid")
        ),
        "activation_record_rejected_count": rejected_count,
        "unsafe_activation_record_count": unsafe_count,
        "missing_activation_prerequisite_count": sum(
            contract.get("missing_activation_prerequisite_count", 0) for contract in requested
        ),
        "durable_executor_activation_allowed_count": sum(
            1 for contract in requested if contract.get("durable_executor_activation_allowed")
        ),
        "durable_executor_activated_count": sum(
            1 for contract in requested if contract.get("durable_executor_activated")
        ),
        "durable_executor_may_open_after_activation_count": sum(
            1
            for contract in requested
            if contract.get("durable_executor_may_open_after_activation")
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
