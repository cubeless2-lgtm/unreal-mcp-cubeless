#!/usr/bin/env python
"""
Section 79 durable canary live command execution release contract.

This contract defines the operator release record required before a future live
command execution may be considered. It does not emit command plans, execute
live commands, save assets, or open durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_LIVE_COMMAND_EXECUTION_RELEASE_SCHEMA = (
    "section_79_durable_canary_live_command_execution_release_contract_v1"
)
CANARY_LIVE_COMMAND_EXECUTION_RELEASE_RECORD_SCHEMA = (
    "section_79_durable_canary_live_command_execution_release_record_v1"
)
CANARY_LIVE_COMMAND_EXECUTION_RELEASE_SUMMARY_SCHEMA = (
    "section_79_durable_canary_live_command_execution_release_summary_v1"
)
EXPECTED_EXECUTION_SCOPE = "durable_canary_live_command_execution_only"


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_live_command_execution_release_contract(
    requested: bool,
    dispatch_release_summary: Dict[str, Any],
    execution_release_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    execution_release_record = execution_release_record or {}
    execution_record_present = bool(execution_release_record)
    dispatch_release_contract_ready = bool(
        requested
        and dispatch_release_summary.get("status") == "passed"
        and dispatch_release_summary.get("dispatch_release_contract_defined_count") == 1
        and dispatch_release_summary.get("dispatch_release_record_rejected_count") == 0
        and dispatch_release_summary.get("unsafe_dispatch_release_record_count") == 0
        and dispatch_release_summary.get("durable_executor_may_open_after_dispatch_release_count") == 0
        and dispatch_release_summary.get("save_delete_rename_allowed_count") == 0
    )
    dispatch_inputs_satisfied = bool(dispatch_release_summary.get("dispatch_inputs_satisfied_count") == 1)
    dispatch_release_record_valid = bool(
        dispatch_release_summary.get("dispatch_release_record_valid_count") == 1
    )
    execution_inputs_satisfied = bool(dispatch_inputs_satisfied and dispatch_release_record_valid)
    record_schema_matches = bool(
        execution_record_present
        and execution_release_record.get("schema") == CANARY_LIVE_COMMAND_EXECUTION_RELEASE_RECORD_SCHEMA
    )
    execution_scope_matches = bool(
        execution_record_present
        and execution_release_record.get("execution_scope") == EXPECTED_EXECUTION_SCOPE
    )
    explicit_execution_authorized = bool(
        execution_record_present
        and execution_release_record.get("explicit_live_command_execution_authorized") is True
    )
    no_save_delete_rename_acknowledged = bool(
        execution_record_present
        and execution_release_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    unsafe_execution_release_record_count = sum(
        int(_authorized(execution_release_record.get(key)))
        for key in (
            "durable_authoring_authorized",
            "save_asset_authorized",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
        )
    )
    execution_release_contract_defined = bool(requested and dispatch_release_contract_ready)
    execution_release_record_valid = bool(
        execution_release_contract_defined
        and execution_inputs_satisfied
        and record_schema_matches
        and execution_scope_matches
        and explicit_execution_authorized
        and no_save_delete_rename_acknowledged
        and unsafe_execution_release_record_count == 0
    )
    missing = []
    if requested:
        if not dispatch_inputs_satisfied:
            missing.append("section_78_dispatch_inputs_satisfied")
        if not dispatch_release_record_valid:
            missing.append("section_78_dispatch_release_record_valid")
        if not execution_record_present:
            missing.append("live_command_execution_release_record_present")
        if not record_schema_matches:
            missing.append("live_command_execution_release_record_schema")
        if not execution_scope_matches:
            missing.append("durable_canary_live_command_execution_only_scope")
        if not explicit_execution_authorized:
            missing.append("explicit_live_command_execution_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        missing.append("separate_live_command_execution_evidence_admission")
    execution_release_record_rejected = bool(
        execution_record_present and not execution_release_record_valid
    )
    return {
        "id": "durable_canary_live_command_execution_release",
        "schema": CANARY_LIVE_COMMAND_EXECUTION_RELEASE_SCHEMA,
        "requested": requested,
        "execution_release_contract_defined": execution_release_contract_defined,
        "required_execution_release_record_schema": (
            CANARY_LIVE_COMMAND_EXECUTION_RELEASE_RECORD_SCHEMA if requested else ""
        ),
        "expected_execution_scope": EXPECTED_EXECUTION_SCOPE if requested else "",
        "dispatch_release_contract_ready": dispatch_release_contract_ready,
        "dispatch_inputs_satisfied": dispatch_inputs_satisfied,
        "dispatch_release_record_valid": dispatch_release_record_valid,
        "execution_inputs_satisfied": execution_inputs_satisfied,
        "execution_record_present": execution_record_present,
        "record_schema_matches": record_schema_matches,
        "execution_scope_matches": execution_scope_matches,
        "explicit_execution_authorized": explicit_execution_authorized,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "execution_release_record_valid": execution_release_record_valid,
        "execution_release_record_rejected": execution_release_record_rejected,
        "unsafe_execution_release_record_count": unsafe_execution_release_record_count,
        "missing_execution_prerequisites": missing,
        "missing_execution_prerequisite_count": len(missing),
        "live_command_execution_release_allowed": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_command_execution_allowed": False,
        "live_command_executed": False,
        "live_canary_rehearsal_performed": False,
        "canary_creation_allowed": False,
        "canary_save_allowed": False,
        "canary_cleanup_allowed": False,
        "durable_executor_may_open_after_execution_release": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_creation_command_count": 0,
        "live_compile_command_count": 0,
        "live_marker_write_command_count": 0,
        "live_marker_readback_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
        "blocked_by": []
        if not requested
        else [
            "section_79_execution_release_does_not_execute_live_commands",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped live command execution release only after Section 78 dispatch release is valid",
            "reject execution records that authorize save, delete, rename, cleanup, or general durable authoring",
            "keep live execution evidence behind a separate admission contract before durable promotion",
        ],
    }


def summarize_canary_live_command_execution_releases(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("execution_release_record_rejected"))
    unsafe_count = sum(
        contract.get("unsafe_execution_release_record_count", 0) for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("execution_release_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and sum(1 for contract in requested if contract.get("live_command_execution_release_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_dispatch_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_plan_emitted")) == 0
            and sum(1 for contract in requested if contract.get("live_command_execution_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_executed")) == 0
            and sum(1 for contract in requested if contract.get("live_canary_rehearsal_performed")) == 0
            and sum(1 for contract in requested if contract.get("canary_creation_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_save_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_cleanup_allowed")) == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_executor_may_open_after_execution_release")
            )
            == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_delete_rename_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            and sum(contract.get("live_creation_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_compile_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_marker_write_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_marker_readback_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_save_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_delete_rename_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_cleanup_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": CANARY_LIVE_COMMAND_EXECUTION_RELEASE_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_live_command_execution_release_count": len(requested),
        "execution_release_contract_defined_count": sum(
            1 for contract in requested if contract.get("execution_release_contract_defined")
        ),
        "dispatch_release_contract_ready_count": sum(
            1 for contract in requested if contract.get("dispatch_release_contract_ready")
        ),
        "dispatch_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("dispatch_inputs_satisfied")
        ),
        "dispatch_release_record_valid_count": sum(
            1 for contract in requested if contract.get("dispatch_release_record_valid")
        ),
        "execution_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("execution_inputs_satisfied")
        ),
        "execution_record_present_count": sum(
            1 for contract in requested if contract.get("execution_record_present")
        ),
        "record_schema_matches_count": sum(1 for contract in requested if contract.get("record_schema_matches")),
        "execution_scope_matches_count": sum(
            1 for contract in requested if contract.get("execution_scope_matches")
        ),
        "explicit_execution_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_execution_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "execution_release_record_valid_count": sum(
            1 for contract in requested if contract.get("execution_release_record_valid")
        ),
        "execution_release_record_rejected_count": rejected_count,
        "unsafe_execution_release_record_count": unsafe_count,
        "missing_execution_prerequisite_count": sum(
            contract.get("missing_execution_prerequisite_count", 0) for contract in requested
        ),
        "live_command_execution_release_allowed_count": sum(
            1 for contract in requested if contract.get("live_command_execution_release_allowed")
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
        "live_canary_rehearsal_performed_count": sum(
            1 for contract in requested if contract.get("live_canary_rehearsal_performed")
        ),
        "canary_creation_allowed_count": sum(
            1 for contract in requested if contract.get("canary_creation_allowed")
        ),
        "canary_save_allowed_count": sum(1 for contract in requested if contract.get("canary_save_allowed")),
        "canary_cleanup_allowed_count": sum(
            1 for contract in requested if contract.get("canary_cleanup_allowed")
        ),
        "durable_executor_may_open_after_execution_release_count": sum(
            1
            for contract in requested
            if contract.get("durable_executor_may_open_after_execution_release")
        ),
        "durable_authoring_allowed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_allowed")
        ),
        "save_delete_rename_allowed_count": sum(
            1 for contract in requested if contract.get("save_delete_rename_allowed")
        ),
        "cleanup_allowed_count": sum(1 for contract in requested if contract.get("cleanup_allowed")),
        "live_creation_command_count": sum(
            contract.get("live_creation_command_count", 0) for contract in requested
        ),
        "live_compile_command_count": sum(
            contract.get("live_compile_command_count", 0) for contract in requested
        ),
        "live_marker_write_command_count": sum(
            contract.get("live_marker_write_command_count", 0) for contract in requested
        ),
        "live_marker_readback_command_count": sum(
            contract.get("live_marker_readback_command_count", 0) for contract in requested
        ),
        "live_save_command_count": sum(contract.get("live_save_command_count", 0) for contract in requested),
        "live_delete_rename_command_count": sum(
            contract.get("live_delete_rename_command_count", 0) for contract in requested
        ),
        "live_cleanup_command_count": sum(contract.get("live_cleanup_command_count", 0) for contract in requested),
    }
