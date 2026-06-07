#!/usr/bin/env python
"""
Section 83 durable canary executor open contract.

This contract defines the operator open record required before a future durable
executor open step may be considered. It does not open the durable executor,
save assets, or enable durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_DURABLE_EXECUTOR_OPEN_SCHEMA = "section_83_durable_canary_executor_open_contract_v1"
CANARY_DURABLE_EXECUTOR_OPEN_RECORD_SCHEMA = "section_83_durable_canary_executor_open_record_v1"
CANARY_DURABLE_EXECUTOR_OPEN_SUMMARY_SCHEMA = "section_83_durable_canary_executor_open_summary_v1"
EXPECTED_OPEN_SCOPE = "durable_canary_executor_open_only"


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_durable_executor_open_contract(
    requested: bool,
    activation_summary: Dict[str, Any],
    open_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    open_record = open_record or {}
    open_record_present = bool(open_record)
    activation_contract_ready = bool(
        requested
        and activation_summary.get("status") == "passed"
        and activation_summary.get("activation_contract_defined_count") == 1
        and activation_summary.get("activation_record_rejected_count") == 0
        and activation_summary.get("unsafe_activation_record_count") == 0
        and activation_summary.get("reported_forbidden_evidence_command_count") == 0
        and activation_summary.get("durable_executor_activation_allowed_count") == 0
        and activation_summary.get("durable_executor_activated_count") == 0
        and activation_summary.get("durable_executor_may_open_after_activation_count") == 0
        and activation_summary.get("save_delete_rename_allowed_count") == 0
    )
    activation_inputs_satisfied = bool(
        activation_summary.get("activation_inputs_satisfied_count") == 1
    )
    activation_record_valid = bool(
        activation_summary.get("activation_record_valid_count") == 1
    )
    open_inputs_satisfied = bool(
        activation_inputs_satisfied and activation_record_valid
    )
    record_schema_matches = bool(
        open_record_present
        and open_record.get("schema") == CANARY_DURABLE_EXECUTOR_OPEN_RECORD_SCHEMA
    )
    open_scope_matches = bool(
        open_record_present
        and open_record.get("open_scope") == EXPECTED_OPEN_SCOPE
    )
    explicit_open_authorized = bool(
        open_record_present
        and open_record.get("explicit_durable_executor_open_authorized") is True
    )
    no_save_delete_rename_acknowledged = bool(
        open_record_present
        and open_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    unsafe_open_record_count = sum(
        int(_authorized(open_record.get(key)))
        for key in (
            "durable_authoring_authorized",
            "durable_executor_activation_authorized",
            "durable_executor_open_performed",
            "durable_executor_opened",
            "save_asset_authorized",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
            "live_command_dispatch_authorized",
            "live_command_execution_authorized",
        )
    )
    open_contract_defined = bool(requested and activation_contract_ready)
    open_record_valid = bool(
        open_contract_defined
        and open_inputs_satisfied
        and record_schema_matches
        and open_scope_matches
        and explicit_open_authorized
        and no_save_delete_rename_acknowledged
        and unsafe_open_record_count == 0
    )
    missing = []
    if requested:
        if not activation_inputs_satisfied:
            missing.append("section_82_activation_inputs_satisfied")
        if not activation_record_valid:
            missing.append("section_82_activation_record_valid")
        if not open_record_present:
            missing.append("durable_executor_open_record_present")
        if not record_schema_matches:
            missing.append("durable_executor_open_record_schema")
        if not open_scope_matches:
            missing.append("durable_canary_executor_open_only_scope")
        if not explicit_open_authorized:
            missing.append("explicit_durable_executor_open_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        missing.append("separate_durable_authoring_enable_contract")
    open_record_rejected = bool(open_record_present and not open_record_valid)
    return {
        "id": "durable_canary_executor_open",
        "schema": CANARY_DURABLE_EXECUTOR_OPEN_SCHEMA,
        "requested": requested,
        "open_contract_defined": open_contract_defined,
        "required_open_record_schema": (
            CANARY_DURABLE_EXECUTOR_OPEN_RECORD_SCHEMA if requested else ""
        ),
        "expected_open_scope": EXPECTED_OPEN_SCOPE if requested else "",
        "activation_contract_ready": activation_contract_ready,
        "activation_inputs_satisfied": activation_inputs_satisfied,
        "activation_record_valid": activation_record_valid,
        "open_inputs_satisfied": open_inputs_satisfied,
        "open_record_present": open_record_present,
        "record_schema_matches": record_schema_matches,
        "open_scope_matches": open_scope_matches,
        "explicit_open_authorized": explicit_open_authorized,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "open_record_valid": open_record_valid,
        "open_record_rejected": open_record_rejected,
        "unsafe_open_record_count": unsafe_open_record_count,
        "missing_open_prerequisites": missing,
        "missing_open_prerequisite_count": len(missing),
        "durable_executor_open_allowed": False,
        "durable_executor_opened": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_command_execution_allowed": False,
        "live_command_executed": False,
        "reported_allowed_evidence_command_count": activation_summary.get(
            "reported_allowed_evidence_command_count",
            0,
        ),
        "reported_forbidden_evidence_command_count": activation_summary.get(
            "reported_forbidden_evidence_command_count",
            0,
        ),
        "blocked_by": []
        if not requested
        else [
            "section_83_open_contract_does_not_open_durable_executor",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped durable executor open authorization only after Section 82 activation is valid",
            "reject open records that authorize durable authoring, executor activation, save, delete, rename, cleanup, or live command execution",
            "keep durable authoring enablement behind a separate contract after open record validation",
        ],
    }


def summarize_canary_durable_executor_opens(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("open_record_rejected"))
    unsafe_count = sum(contract.get("unsafe_open_record_count", 0) for contract in requested)
    forbidden_evidence_count = sum(
        contract.get("reported_forbidden_evidence_command_count", 0) for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("open_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_evidence_count == 0
            and sum(1 for contract in requested if contract.get("durable_executor_open_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_opened")) == 0
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
        "schema": CANARY_DURABLE_EXECUTOR_OPEN_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_executor_open_count": len(requested),
        "open_contract_defined_count": sum(
            1 for contract in requested if contract.get("open_contract_defined")
        ),
        "activation_contract_ready_count": sum(
            1 for contract in requested if contract.get("activation_contract_ready")
        ),
        "activation_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("activation_inputs_satisfied")
        ),
        "activation_record_valid_count": sum(
            1 for contract in requested if contract.get("activation_record_valid")
        ),
        "open_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("open_inputs_satisfied")
        ),
        "open_record_present_count": sum(
            1 for contract in requested if contract.get("open_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "open_scope_matches_count": sum(
            1 for contract in requested if contract.get("open_scope_matches")
        ),
        "explicit_open_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_open_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "open_record_valid_count": sum(
            1 for contract in requested if contract.get("open_record_valid")
        ),
        "open_record_rejected_count": rejected_count,
        "unsafe_open_record_count": unsafe_count,
        "missing_open_prerequisite_count": sum(
            contract.get("missing_open_prerequisite_count", 0) for contract in requested
        ),
        "durable_executor_open_allowed_count": sum(
            1 for contract in requested if contract.get("durable_executor_open_allowed")
        ),
        "durable_executor_opened_count": sum(
            1 for contract in requested if contract.get("durable_executor_opened")
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
        "reported_allowed_evidence_command_count": sum(
            contract.get("reported_allowed_evidence_command_count", 0) for contract in requested
        ),
        "reported_forbidden_evidence_command_count": forbidden_evidence_count,
    }
