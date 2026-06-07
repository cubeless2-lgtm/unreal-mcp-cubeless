#!/usr/bin/env python
"""
Section 87 durable canary authoring command execution contract.

This contract defines the scoped execution record required after a future
dispatch record is valid. It does not execute live commands, save assets, or
allow delete/rename/cleanup actions.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_DURABLE_AUTHORING_COMMAND_EXECUTION_SCHEMA = (
    "section_87_durable_canary_authoring_command_execution_contract_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_EXECUTION_RECORD_SCHEMA = (
    "section_87_durable_canary_authoring_command_execution_record_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_EXECUTION_SUMMARY_SCHEMA = (
    "section_87_durable_canary_authoring_command_execution_summary_v1"
)
EXPECTED_EXECUTION_SCOPE = "durable_canary_authoring_command_execution_only"


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_durable_authoring_command_execution_contract(
    requested: bool,
    dispatch_summary: Dict[str, Any],
    execution_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    execution_record = execution_record or {}
    execution_record_present = bool(execution_record)
    dispatch_contract_ready = bool(
        requested
        and dispatch_summary.get("status") == "passed"
        and dispatch_summary.get("dispatch_contract_defined_count") == 1
        and dispatch_summary.get("dispatch_record_rejected_count") == 0
        and dispatch_summary.get("unsafe_dispatch_record_count") == 0
        and dispatch_summary.get("reported_forbidden_evidence_command_count") == 0
        and dispatch_summary.get("durable_authoring_command_dispatch_allowed_count") == 0
        and dispatch_summary.get("durable_authoring_command_dispatched_count") == 0
        and dispatch_summary.get("durable_authoring_command_execution_allowed_count") == 0
        and dispatch_summary.get("durable_authoring_command_executed_count") == 0
        and dispatch_summary.get("durable_authoring_allowed_count") == 0
        and dispatch_summary.get("save_delete_rename_allowed_count") == 0
    )
    dispatch_inputs_satisfied = bool(dispatch_summary.get("dispatch_inputs_satisfied_count") == 1)
    dispatch_record_valid = bool(dispatch_summary.get("dispatch_record_valid_count") == 1)
    planned_authoring_commands_present = bool(
        dispatch_summary.get("planned_authoring_commands_present_count") == 1
    )
    allowed_authoring_commands_present = bool(
        dispatch_summary.get("allowed_authoring_commands_present_count") == 1
    )
    execution_inputs_satisfied = bool(
        dispatch_inputs_satisfied
        and dispatch_record_valid
        and planned_authoring_commands_present
        and allowed_authoring_commands_present
    )
    record_schema_matches = bool(
        execution_record_present
        and execution_record.get("schema") == CANARY_DURABLE_AUTHORING_COMMAND_EXECUTION_RECORD_SCHEMA
    )
    execution_scope_matches = bool(
        execution_record_present
        and execution_record.get("execution_scope") == EXPECTED_EXECUTION_SCOPE
    )
    explicit_execution_authorized = bool(
        execution_record_present
        and execution_record.get("explicit_durable_authoring_command_execution_authorized") is True
    )
    no_save_delete_rename_acknowledged = bool(
        execution_record_present
        and execution_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    unsafe_execution_record_count = sum(
        int(_authorized(execution_record.get(key)))
        for key in (
            "durable_authoring_enabled",
            "durable_authoring_allowed",
            "durable_authoring_command_dispatch_allowed",
            "durable_authoring_command_dispatched",
            "durable_authoring_command_execution_allowed",
            "durable_authoring_command_executed",
            "save_asset_authorized",
            "save_asset_executed",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
            "live_command_dispatch_performed",
            "live_command_execution_performed",
            "live_command_executed",
        )
    )
    execution_contract_defined = bool(requested and dispatch_contract_ready)
    execution_record_valid = bool(
        execution_contract_defined
        and execution_inputs_satisfied
        and record_schema_matches
        and execution_scope_matches
        and explicit_execution_authorized
        and no_save_delete_rename_acknowledged
        and unsafe_execution_record_count == 0
    )
    missing = []
    if requested:
        if not dispatch_inputs_satisfied:
            missing.append("section_86_dispatch_inputs_satisfied")
        if not dispatch_record_valid:
            missing.append("section_86_dispatch_record_valid")
        if not planned_authoring_commands_present:
            missing.append("section_86_planned_authoring_commands_present")
        if not allowed_authoring_commands_present:
            missing.append("section_86_allowed_authoring_commands_present")
        if not execution_record_present:
            missing.append("durable_authoring_command_execution_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_execution_record_schema")
        if not execution_scope_matches:
            missing.append("durable_canary_authoring_command_execution_only_scope")
        if not explicit_execution_authorized:
            missing.append("explicit_durable_authoring_command_execution_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        missing.append("separate_durable_authoring_command_execution_evidence_contract")
    execution_record_rejected = bool(execution_record_present and not execution_record_valid)
    return {
        "id": "durable_canary_authoring_command_execution",
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_EXECUTION_SCHEMA,
        "requested": requested,
        "execution_contract_defined": execution_contract_defined,
        "required_execution_record_schema": (
            CANARY_DURABLE_AUTHORING_COMMAND_EXECUTION_RECORD_SCHEMA if requested else ""
        ),
        "expected_execution_scope": EXPECTED_EXECUTION_SCOPE if requested else "",
        "dispatch_contract_ready": dispatch_contract_ready,
        "dispatch_inputs_satisfied": dispatch_inputs_satisfied,
        "dispatch_record_valid": dispatch_record_valid,
        "planned_authoring_commands_present": planned_authoring_commands_present,
        "allowed_authoring_commands_present": allowed_authoring_commands_present,
        "execution_inputs_satisfied": execution_inputs_satisfied,
        "execution_record_present": execution_record_present,
        "record_schema_matches": record_schema_matches,
        "execution_scope_matches": execution_scope_matches,
        "explicit_execution_authorized": explicit_execution_authorized,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "execution_record_valid": execution_record_valid,
        "execution_record_rejected": execution_record_rejected,
        "unsafe_execution_record_count": unsafe_execution_record_count,
        "missing_execution_prerequisites": missing,
        "missing_execution_prerequisite_count": len(missing),
        "durable_authoring_command_dispatch_allowed": False,
        "durable_authoring_command_dispatched": False,
        "durable_authoring_command_execution_allowed": False,
        "durable_authoring_command_executed": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_command_execution_allowed": False,
        "live_command_executed": False,
        "reported_allowed_evidence_command_count": dispatch_summary.get(
            "reported_allowed_evidence_command_count",
            0,
        ),
        "reported_forbidden_evidence_command_count": dispatch_summary.get(
            "reported_forbidden_evidence_command_count",
            0,
        ),
        "blocked_by": []
        if not requested
        else [
            "section_87_execution_contract_does_not_execute",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped durable authoring command execution only after Section 86 dispatch is valid",
            "reject execution records that claim execution, save, delete, rename, cleanup, or durable authoring",
            "keep execution evidence admission behind a separate contract after execution record validation",
        ],
    }


def summarize_canary_durable_authoring_command_executions(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1 for contract in requested if contract.get("execution_record_rejected")
    )
    unsafe_count = sum(
        contract.get("unsafe_execution_record_count", 0) for contract in requested
    )
    forbidden_evidence_count = sum(
        contract.get("reported_forbidden_evidence_command_count", 0) for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("execution_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_evidence_count == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_dispatch_allowed")
            )
            == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_command_dispatched")) == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_execution_allowed")
            )
            == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_command_executed")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_enabled")) == 0
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
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_EXECUTION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_authoring_command_execution_count": len(requested),
        "execution_contract_defined_count": sum(
            1 for contract in requested if contract.get("execution_contract_defined")
        ),
        "dispatch_contract_ready_count": sum(
            1 for contract in requested if contract.get("dispatch_contract_ready")
        ),
        "dispatch_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("dispatch_inputs_satisfied")
        ),
        "dispatch_record_valid_count": sum(
            1 for contract in requested if contract.get("dispatch_record_valid")
        ),
        "planned_authoring_commands_present_count": sum(
            1 for contract in requested if contract.get("planned_authoring_commands_present")
        ),
        "allowed_authoring_commands_present_count": sum(
            1 for contract in requested if contract.get("allowed_authoring_commands_present")
        ),
        "execution_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("execution_inputs_satisfied")
        ),
        "execution_record_present_count": sum(
            1 for contract in requested if contract.get("execution_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "execution_scope_matches_count": sum(
            1 for contract in requested if contract.get("execution_scope_matches")
        ),
        "explicit_execution_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_execution_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "execution_record_valid_count": sum(
            1 for contract in requested if contract.get("execution_record_valid")
        ),
        "execution_record_rejected_count": rejected_count,
        "unsafe_execution_record_count": unsafe_count,
        "missing_execution_prerequisite_count": sum(
            contract.get("missing_execution_prerequisite_count", 0) for contract in requested
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
        "reported_allowed_evidence_command_count": sum(
            contract.get("reported_allowed_evidence_command_count", 0) for contract in requested
        ),
        "reported_forbidden_evidence_command_count": forbidden_evidence_count,
    }
