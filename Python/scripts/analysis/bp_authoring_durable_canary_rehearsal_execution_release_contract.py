#!/usr/bin/env python
"""
Section 75 durable canary rehearsal execution release contract.

This contract defines the record required before a future live canary rehearsal
execution may be considered. It does not execute the rehearsal and does not
open durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_REHEARSAL_EXECUTION_RELEASE_SCHEMA = (
    "section_75_durable_canary_rehearsal_execution_release_contract_v1"
)
CANARY_REHEARSAL_EXECUTION_RELEASE_RECORD_SCHEMA = (
    "section_75_durable_canary_rehearsal_execution_release_record_v1"
)
CANARY_REHEARSAL_EXECUTION_RELEASE_SUMMARY_SCHEMA = (
    "section_75_durable_canary_rehearsal_execution_release_summary_v1"
)
EXPECTED_RELEASE_SCOPE = "durable_canary_rehearsal_only"


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_rehearsal_execution_release_contract(
    requested: bool,
    promotion_barrier_summary: Dict[str, Any],
    release_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    release_record = release_record or {}
    release_record_present = bool(release_record)
    promotion_barrier_defined = bool(
        requested
        and promotion_barrier_summary.get("status") == "passed"
        and promotion_barrier_summary.get("promotion_barrier_defined_count") == 1
    )
    promotion_inputs_satisfied = bool(
        promotion_barrier_summary.get("promotion_inputs_satisfied_count") == 1
    )
    record_schema_matches = bool(
        release_record_present
        and release_record.get("schema") == CANARY_REHEARSAL_EXECUTION_RELEASE_RECORD_SCHEMA
    )
    release_scope_matches = bool(
        release_record_present and release_record.get("release_scope") == EXPECTED_RELEASE_SCOPE
    )
    explicit_execution_authorized = bool(
        release_record_present
        and release_record.get("explicit_durable_canary_rehearsal_execution_authorized") is True
    )
    no_save_delete_rename_acknowledged = bool(
        release_record_present
        and release_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    unsafe_release_record_count = sum(
        int(_authorized(release_record.get(key)))
        for key in (
            "durable_authoring_authorized",
            "save_asset_authorized",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
        )
    )
    execution_release_contract_defined = bool(requested and promotion_barrier_defined)
    release_record_valid = bool(
        execution_release_contract_defined
        and promotion_inputs_satisfied
        and record_schema_matches
        and release_scope_matches
        and explicit_execution_authorized
        and no_save_delete_rename_acknowledged
        and unsafe_release_record_count == 0
    )
    missing = []
    if requested:
        if not promotion_inputs_satisfied:
            missing.append("section_74_promotion_inputs_satisfied")
        if not release_record_present:
            missing.append("durable_rehearsal_execution_release_record_present")
        if not record_schema_matches:
            missing.append("durable_rehearsal_execution_release_record_schema")
        if not release_scope_matches:
            missing.append("durable_canary_rehearsal_only_release_scope")
        if not explicit_execution_authorized:
            missing.append("explicit_durable_canary_rehearsal_execution_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        missing.append("separate_live_rehearsal_runner_release")
    release_record_rejected = bool(release_record_present and not release_record_valid)
    return {
        "id": "durable_canary_rehearsal_execution_release",
        "schema": CANARY_REHEARSAL_EXECUTION_RELEASE_SCHEMA,
        "requested": requested,
        "execution_release_contract_defined": execution_release_contract_defined,
        "required_release_record_schema": CANARY_REHEARSAL_EXECUTION_RELEASE_RECORD_SCHEMA if requested else "",
        "expected_release_scope": EXPECTED_RELEASE_SCOPE if requested else "",
        "promotion_barrier_defined": promotion_barrier_defined,
        "promotion_inputs_satisfied": promotion_inputs_satisfied,
        "release_record_present": release_record_present,
        "record_schema_matches": record_schema_matches,
        "release_scope_matches": release_scope_matches,
        "explicit_execution_authorized": explicit_execution_authorized,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "release_record_valid": release_record_valid,
        "release_record_rejected": release_record_rejected,
        "unsafe_release_record_count": unsafe_release_record_count,
        "missing_release_prerequisites": missing,
        "missing_release_prerequisite_count": len(missing),
        "live_canary_rehearsal_release_allowed": False,
        "live_canary_rehearsal_execution_allowed": False,
        "live_canary_rehearsal_performed": False,
        "canary_creation_allowed": False,
        "canary_save_allowed": False,
        "canary_cleanup_allowed": False,
        "durable_executor_may_open_after_execution_release": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_creation_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
        "blocked_by": []
        if not requested
        else [
            "section_75_execution_release_does_not_run_live_rehearsal",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped durable canary rehearsal execution release before any future live rehearsal",
            "reject release records that authorize save, delete, rename, cleanup, or general durable authoring",
            "keep a separate live runner release gate before issuing live canary rehearsal commands",
        ],
    }


def summarize_canary_rehearsal_execution_releases(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("release_record_rejected"))
    unsafe_count = sum(contract.get("unsafe_release_record_count", 0) for contract in requested)
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("execution_release_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and sum(1 for contract in requested if contract.get("live_canary_rehearsal_release_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_canary_rehearsal_execution_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_canary_rehearsal_performed")) == 0
            and sum(1 for contract in requested if contract.get("canary_creation_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_save_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_cleanup_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_after_execution_release"))
            == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_delete_rename_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            and sum(contract.get("live_creation_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_save_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_delete_rename_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_cleanup_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": CANARY_REHEARSAL_EXECUTION_RELEASE_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_rehearsal_execution_release_count": len(requested),
        "execution_release_contract_defined_count": sum(
            1 for contract in requested if contract.get("execution_release_contract_defined")
        ),
        "promotion_barrier_defined_count": sum(
            1 for contract in requested if contract.get("promotion_barrier_defined")
        ),
        "promotion_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("promotion_inputs_satisfied")
        ),
        "release_record_present_count": sum(1 for contract in requested if contract.get("release_record_present")),
        "record_schema_matches_count": sum(1 for contract in requested if contract.get("record_schema_matches")),
        "release_scope_matches_count": sum(1 for contract in requested if contract.get("release_scope_matches")),
        "explicit_execution_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_execution_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "release_record_valid_count": sum(1 for contract in requested if contract.get("release_record_valid")),
        "release_record_rejected_count": rejected_count,
        "unsafe_release_record_count": unsafe_count,
        "missing_release_prerequisite_count": sum(
            contract.get("missing_release_prerequisite_count", 0) for contract in requested
        ),
        "live_canary_rehearsal_release_allowed_count": sum(
            1 for contract in requested if contract.get("live_canary_rehearsal_release_allowed")
        ),
        "live_canary_rehearsal_execution_allowed_count": sum(
            1 for contract in requested if contract.get("live_canary_rehearsal_execution_allowed")
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
            1 for contract in requested if contract.get("durable_executor_may_open_after_execution_release")
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
        "live_save_command_count": sum(contract.get("live_save_command_count", 0) for contract in requested),
        "live_delete_rename_command_count": sum(
            contract.get("live_delete_rename_command_count", 0) for contract in requested
        ),
        "live_cleanup_command_count": sum(
            contract.get("live_cleanup_command_count", 0) for contract in requested
        ),
    }
