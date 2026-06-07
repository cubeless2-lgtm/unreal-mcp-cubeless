#!/usr/bin/env python
"""
Section 77 durable canary live runner start contract.

This contract defines the operator start record required before a future live
runner may dispatch commands. It does not start the runner or issue commands.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_LIVE_RUNNER_START_SCHEMA = "section_77_durable_canary_live_runner_start_contract_v1"
CANARY_LIVE_RUNNER_START_RECORD_SCHEMA = "section_77_durable_canary_live_runner_start_record_v1"
CANARY_LIVE_RUNNER_START_SUMMARY_SCHEMA = "section_77_durable_canary_live_runner_start_summary_v1"
EXPECTED_START_SCOPE = "durable_canary_live_runner_only"


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_live_runner_start_contract(
    requested: bool,
    runner_envelope_summary: Dict[str, Any],
    start_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    start_record = start_record or {}
    start_record_present = bool(start_record)
    runner_envelope_ready = bool(
        requested
        and runner_envelope_summary.get("status") == "passed"
        and runner_envelope_summary.get("live_runner_envelope_defined_count") == 1
        and runner_envelope_summary.get("runner_plan_rejected_count") == 0
        and runner_envelope_summary.get("forbidden_runner_command_count") == 0
        and runner_envelope_summary.get("unknown_runner_command_count") == 0
        and runner_envelope_summary.get("durable_executor_may_open_after_runner_count") == 0
    )
    runner_plan_valid = bool(runner_envelope_summary.get("runner_plan_valid_count") == 1)
    runner_start_allowed_by_envelope = bool(runner_envelope_summary.get("live_runner_may_start_count") == 1)
    record_schema_matches = bool(
        start_record_present and start_record.get("schema") == CANARY_LIVE_RUNNER_START_RECORD_SCHEMA
    )
    start_scope_matches = bool(start_record_present and start_record.get("start_scope") == EXPECTED_START_SCOPE)
    explicit_operator_start_authorized = bool(
        start_record_present and start_record.get("explicit_operator_live_runner_start_authorized") is True
    )
    no_save_delete_rename_acknowledged = bool(
        start_record_present and start_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    unsafe_start_record_count = sum(
        int(_authorized(start_record.get(key)))
        for key in (
            "durable_authoring_authorized",
            "save_asset_authorized",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
        )
    )
    start_contract_defined = bool(requested and runner_envelope_ready)
    start_record_valid = bool(
        start_contract_defined
        and runner_plan_valid
        and runner_start_allowed_by_envelope
        and record_schema_matches
        and start_scope_matches
        and explicit_operator_start_authorized
        and no_save_delete_rename_acknowledged
        and unsafe_start_record_count == 0
    )
    missing = []
    if requested:
        if not runner_plan_valid:
            missing.append("section_76_runner_plan_valid")
        if not runner_start_allowed_by_envelope:
            missing.append("section_76_live_runner_may_start")
        if not start_record_present:
            missing.append("operator_live_runner_start_record_present")
        if not record_schema_matches:
            missing.append("operator_live_runner_start_record_schema")
        if not start_scope_matches:
            missing.append("durable_canary_live_runner_only_start_scope")
        if not explicit_operator_start_authorized:
            missing.append("explicit_operator_live_runner_start_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        missing.append("separate_live_command_dispatch_release")
    start_record_rejected = bool(start_record_present and not start_record_valid)
    return {
        "id": "durable_canary_live_runner_start",
        "schema": CANARY_LIVE_RUNNER_START_SCHEMA,
        "requested": requested,
        "start_contract_defined": start_contract_defined,
        "required_start_record_schema": CANARY_LIVE_RUNNER_START_RECORD_SCHEMA if requested else "",
        "expected_start_scope": EXPECTED_START_SCOPE if requested else "",
        "runner_envelope_ready": runner_envelope_ready,
        "runner_plan_valid": runner_plan_valid,
        "runner_start_allowed_by_envelope": runner_start_allowed_by_envelope,
        "start_record_present": start_record_present,
        "record_schema_matches": record_schema_matches,
        "start_scope_matches": start_scope_matches,
        "explicit_operator_start_authorized": explicit_operator_start_authorized,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "start_record_valid": start_record_valid,
        "start_record_rejected": start_record_rejected,
        "unsafe_start_record_count": unsafe_start_record_count,
        "missing_start_prerequisites": missing,
        "missing_start_prerequisite_count": len(missing),
        "live_runner_start_allowed": False,
        "live_runner_started": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_canary_rehearsal_performed": False,
        "canary_creation_allowed": False,
        "canary_save_allowed": False,
        "canary_cleanup_allowed": False,
        "durable_executor_may_open_after_runner_start": False,
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
            "section_77_start_contract_does_not_dispatch_live_commands",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped operator live runner start only after Section 76 allows runner start",
            "reject start records that authorize save, delete, rename, cleanup, or general durable authoring",
            "keep command dispatch behind a separate release after start validation",
        ],
    }


def summarize_canary_live_runner_starts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("start_record_rejected"))
    unsafe_count = sum(contract.get("unsafe_start_record_count", 0) for contract in requested)
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("start_contract_defined")) == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and sum(1 for contract in requested if contract.get("live_runner_start_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_runner_started")) == 0
            and sum(1 for contract in requested if contract.get("live_command_dispatch_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_plan_emitted")) == 0
            and sum(1 for contract in requested if contract.get("live_canary_rehearsal_performed")) == 0
            and sum(1 for contract in requested if contract.get("canary_creation_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_save_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_cleanup_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_after_runner_start")) == 0
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
        "schema": CANARY_LIVE_RUNNER_START_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_live_runner_start_count": len(requested),
        "start_contract_defined_count": sum(1 for contract in requested if contract.get("start_contract_defined")),
        "runner_envelope_ready_count": sum(1 for contract in requested if contract.get("runner_envelope_ready")),
        "runner_plan_valid_count": sum(1 for contract in requested if contract.get("runner_plan_valid")),
        "runner_start_allowed_by_envelope_count": sum(
            1 for contract in requested if contract.get("runner_start_allowed_by_envelope")
        ),
        "start_record_present_count": sum(1 for contract in requested if contract.get("start_record_present")),
        "record_schema_matches_count": sum(1 for contract in requested if contract.get("record_schema_matches")),
        "start_scope_matches_count": sum(1 for contract in requested if contract.get("start_scope_matches")),
        "explicit_operator_start_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_operator_start_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "start_record_valid_count": sum(1 for contract in requested if contract.get("start_record_valid")),
        "start_record_rejected_count": rejected_count,
        "unsafe_start_record_count": unsafe_count,
        "missing_start_prerequisite_count": sum(
            contract.get("missing_start_prerequisite_count", 0) for contract in requested
        ),
        "live_runner_start_allowed_count": sum(
            1 for contract in requested if contract.get("live_runner_start_allowed")
        ),
        "live_runner_started_count": sum(1 for contract in requested if contract.get("live_runner_started")),
        "live_command_dispatch_allowed_count": sum(
            1 for contract in requested if contract.get("live_command_dispatch_allowed")
        ),
        "live_command_plan_emitted_count": sum(
            1 for contract in requested if contract.get("live_command_plan_emitted")
        ),
        "live_canary_rehearsal_performed_count": sum(
            1 for contract in requested if contract.get("live_canary_rehearsal_performed")
        ),
        "canary_creation_allowed_count": sum(
            1 for contract in requested if contract.get("canary_creation_allowed")
        ),
        "canary_save_allowed_count": sum(1 for contract in requested if contract.get("canary_save_allowed")),
        "canary_cleanup_allowed_count": sum(1 for contract in requested if contract.get("canary_cleanup_allowed")),
        "durable_executor_may_open_after_runner_start_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_after_runner_start")
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
