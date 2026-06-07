#!/usr/bin/env python
"""
Section 86 durable canary authoring command dispatch contract.

This contract defines the scoped dispatch record required after a future
authoring command record is valid. It does not dispatch or execute live
commands, save assets, or allow delete/rename/cleanup actions.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_DURABLE_AUTHORING_COMMAND_DISPATCH_SCHEMA = (
    "section_86_durable_canary_authoring_command_dispatch_contract_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_DISPATCH_RECORD_SCHEMA = (
    "section_86_durable_canary_authoring_command_dispatch_record_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_DISPATCH_SUMMARY_SCHEMA = (
    "section_86_durable_canary_authoring_command_dispatch_summary_v1"
)
EXPECTED_DISPATCH_SCOPE = "durable_canary_authoring_command_dispatch_only"


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_durable_authoring_command_dispatch_contract(
    requested: bool,
    authoring_command_summary: Dict[str, Any],
    dispatch_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    dispatch_record = dispatch_record or {}
    dispatch_record_present = bool(dispatch_record)
    authoring_command_contract_ready = bool(
        requested
        and authoring_command_summary.get("status") == "passed"
        and authoring_command_summary.get("authoring_command_contract_defined_count") == 1
        and authoring_command_summary.get("authoring_command_record_rejected_count") == 0
        and authoring_command_summary.get("unsafe_authoring_command_record_count") == 0
        and authoring_command_summary.get("forbidden_authoring_command_count") == 0
        and authoring_command_summary.get("unknown_authoring_command_count") == 0
        and authoring_command_summary.get("reported_forbidden_evidence_command_count") == 0
        and authoring_command_summary.get("durable_authoring_command_allowed_count") == 0
        and authoring_command_summary.get("durable_authoring_command_dispatched_count") == 0
        and authoring_command_summary.get("durable_authoring_command_executed_count") == 0
        and authoring_command_summary.get("durable_authoring_allowed_count") == 0
        and authoring_command_summary.get("save_delete_rename_allowed_count") == 0
    )
    authoring_command_inputs_satisfied = bool(
        authoring_command_summary.get("authoring_command_inputs_satisfied_count") == 1
    )
    authoring_command_record_valid = bool(
        authoring_command_summary.get("authoring_command_record_valid_count") == 1
    )
    planned_authoring_commands_present = bool(
        authoring_command_summary.get("planned_authoring_command_count", 0) > 0
    )
    allowed_authoring_commands_present = bool(
        authoring_command_summary.get("allowed_authoring_command_count", 0) > 0
    )
    dispatch_inputs_satisfied = bool(
        authoring_command_inputs_satisfied
        and authoring_command_record_valid
        and planned_authoring_commands_present
        and allowed_authoring_commands_present
    )
    record_schema_matches = bool(
        dispatch_record_present
        and dispatch_record.get("schema") == CANARY_DURABLE_AUTHORING_COMMAND_DISPATCH_RECORD_SCHEMA
    )
    dispatch_scope_matches = bool(
        dispatch_record_present
        and dispatch_record.get("dispatch_scope") == EXPECTED_DISPATCH_SCOPE
    )
    explicit_dispatch_authorized = bool(
        dispatch_record_present
        and dispatch_record.get("explicit_durable_authoring_command_dispatch_authorized") is True
    )
    no_save_delete_rename_acknowledged = bool(
        dispatch_record_present
        and dispatch_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    unsafe_dispatch_record_count = sum(
        int(_authorized(dispatch_record.get(key)))
        for key in (
            "durable_authoring_enabled",
            "durable_authoring_allowed",
            "durable_authoring_command_allowed",
            "durable_authoring_command_dispatched",
            "durable_authoring_command_executed",
            "save_asset_authorized",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
            "live_command_dispatch_performed",
            "live_command_execution_authorized",
            "live_command_executed",
        )
    )
    dispatch_contract_defined = bool(requested and authoring_command_contract_ready)
    dispatch_record_valid = bool(
        dispatch_contract_defined
        and dispatch_inputs_satisfied
        and record_schema_matches
        and dispatch_scope_matches
        and explicit_dispatch_authorized
        and no_save_delete_rename_acknowledged
        and unsafe_dispatch_record_count == 0
    )
    missing = []
    if requested:
        if not authoring_command_inputs_satisfied:
            missing.append("section_85_authoring_command_inputs_satisfied")
        if not authoring_command_record_valid:
            missing.append("section_85_authoring_command_record_valid")
        if not planned_authoring_commands_present:
            missing.append("section_85_planned_authoring_commands_present")
        if not allowed_authoring_commands_present:
            missing.append("section_85_allowed_authoring_commands_present")
        if not dispatch_record_present:
            missing.append("durable_authoring_command_dispatch_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_dispatch_record_schema")
        if not dispatch_scope_matches:
            missing.append("durable_canary_authoring_command_dispatch_only_scope")
        if not explicit_dispatch_authorized:
            missing.append("explicit_durable_authoring_command_dispatch_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        missing.append("separate_durable_authoring_command_execution_contract")
    dispatch_record_rejected = bool(dispatch_record_present and not dispatch_record_valid)
    return {
        "id": "durable_canary_authoring_command_dispatch",
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_DISPATCH_SCHEMA,
        "requested": requested,
        "dispatch_contract_defined": dispatch_contract_defined,
        "required_dispatch_record_schema": (
            CANARY_DURABLE_AUTHORING_COMMAND_DISPATCH_RECORD_SCHEMA if requested else ""
        ),
        "expected_dispatch_scope": EXPECTED_DISPATCH_SCOPE if requested else "",
        "authoring_command_contract_ready": authoring_command_contract_ready,
        "authoring_command_inputs_satisfied": authoring_command_inputs_satisfied,
        "authoring_command_record_valid": authoring_command_record_valid,
        "planned_authoring_commands_present": planned_authoring_commands_present,
        "allowed_authoring_commands_present": allowed_authoring_commands_present,
        "dispatch_inputs_satisfied": dispatch_inputs_satisfied,
        "dispatch_record_present": dispatch_record_present,
        "record_schema_matches": record_schema_matches,
        "dispatch_scope_matches": dispatch_scope_matches,
        "explicit_dispatch_authorized": explicit_dispatch_authorized,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "dispatch_record_valid": dispatch_record_valid,
        "dispatch_record_rejected": dispatch_record_rejected,
        "unsafe_dispatch_record_count": unsafe_dispatch_record_count,
        "missing_dispatch_prerequisites": missing,
        "missing_dispatch_prerequisite_count": len(missing),
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
        "reported_allowed_evidence_command_count": authoring_command_summary.get(
            "reported_allowed_evidence_command_count",
            0,
        ),
        "reported_forbidden_evidence_command_count": authoring_command_summary.get(
            "reported_forbidden_evidence_command_count",
            0,
        ),
        "blocked_by": []
        if not requested
        else [
            "section_86_dispatch_contract_does_not_dispatch_or_execute",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped durable authoring command dispatch only after Section 85 command record is valid",
            "reject dispatch records that claim dispatch, execution, save, delete, rename, cleanup, or durable authoring",
            "keep durable command execution behind a separate contract after dispatch record validation",
        ],
    }


def summarize_canary_durable_authoring_command_dispatches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1 for contract in requested if contract.get("dispatch_record_rejected")
    )
    unsafe_count = sum(
        contract.get("unsafe_dispatch_record_count", 0) for contract in requested
    )
    forbidden_evidence_count = sum(
        contract.get("reported_forbidden_evidence_command_count", 0) for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("dispatch_contract_defined"))
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
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_DISPATCH_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_authoring_command_dispatch_count": len(requested),
        "dispatch_contract_defined_count": sum(
            1 for contract in requested if contract.get("dispatch_contract_defined")
        ),
        "authoring_command_contract_ready_count": sum(
            1 for contract in requested if contract.get("authoring_command_contract_ready")
        ),
        "authoring_command_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("authoring_command_inputs_satisfied")
        ),
        "authoring_command_record_valid_count": sum(
            1 for contract in requested if contract.get("authoring_command_record_valid")
        ),
        "planned_authoring_commands_present_count": sum(
            1 for contract in requested if contract.get("planned_authoring_commands_present")
        ),
        "allowed_authoring_commands_present_count": sum(
            1 for contract in requested if contract.get("allowed_authoring_commands_present")
        ),
        "dispatch_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("dispatch_inputs_satisfied")
        ),
        "dispatch_record_present_count": sum(
            1 for contract in requested if contract.get("dispatch_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "dispatch_scope_matches_count": sum(
            1 for contract in requested if contract.get("dispatch_scope_matches")
        ),
        "explicit_dispatch_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_dispatch_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "dispatch_record_valid_count": sum(
            1 for contract in requested if contract.get("dispatch_record_valid")
        ),
        "dispatch_record_rejected_count": rejected_count,
        "unsafe_dispatch_record_count": unsafe_count,
        "missing_dispatch_prerequisite_count": sum(
            contract.get("missing_dispatch_prerequisite_count", 0) for contract in requested
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
