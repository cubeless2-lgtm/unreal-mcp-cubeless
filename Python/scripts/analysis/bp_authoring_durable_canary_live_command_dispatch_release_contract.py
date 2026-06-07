#!/usr/bin/env python
"""
Section 78 durable canary live command dispatch release contract.

This contract defines the operator release record required before a future live
runner command dispatch may be considered. It does not emit command plans,
dispatch live commands, or open durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_LIVE_COMMAND_DISPATCH_RELEASE_SCHEMA = (
    "section_78_durable_canary_live_command_dispatch_release_contract_v1"
)
CANARY_LIVE_COMMAND_DISPATCH_RELEASE_RECORD_SCHEMA = (
    "section_78_durable_canary_live_command_dispatch_release_record_v1"
)
CANARY_LIVE_COMMAND_DISPATCH_RELEASE_SUMMARY_SCHEMA = (
    "section_78_durable_canary_live_command_dispatch_release_summary_v1"
)
EXPECTED_DISPATCH_SCOPE = "durable_canary_live_command_dispatch_only"


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_live_command_dispatch_release_contract(
    requested: bool,
    runner_start_summary: Dict[str, Any],
    dispatch_release_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    dispatch_release_record = dispatch_release_record or {}
    dispatch_record_present = bool(dispatch_release_record)
    start_contract_ready = bool(
        requested
        and runner_start_summary.get("status") == "passed"
        and runner_start_summary.get("start_contract_defined_count") == 1
        and runner_start_summary.get("start_record_rejected_count") == 0
        and runner_start_summary.get("unsafe_start_record_count") == 0
        and runner_start_summary.get("durable_executor_may_open_after_runner_start_count") == 0
        and runner_start_summary.get("save_delete_rename_allowed_count") == 0
    )
    runner_plan_valid = bool(runner_start_summary.get("runner_plan_valid_count") == 1)
    start_record_valid = bool(runner_start_summary.get("start_record_valid_count") == 1)
    live_runner_started = bool(runner_start_summary.get("live_runner_started_count") == 1)
    dispatch_inputs_satisfied = bool(runner_plan_valid and start_record_valid and live_runner_started)
    record_schema_matches = bool(
        dispatch_record_present
        and dispatch_release_record.get("schema") == CANARY_LIVE_COMMAND_DISPATCH_RELEASE_RECORD_SCHEMA
    )
    dispatch_scope_matches = bool(
        dispatch_record_present
        and dispatch_release_record.get("dispatch_scope") == EXPECTED_DISPATCH_SCOPE
    )
    explicit_dispatch_authorized = bool(
        dispatch_record_present
        and dispatch_release_record.get("explicit_live_command_dispatch_authorized") is True
    )
    no_save_delete_rename_acknowledged = bool(
        dispatch_record_present
        and dispatch_release_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    unsafe_dispatch_release_record_count = sum(
        int(_authorized(dispatch_release_record.get(key)))
        for key in (
            "durable_authoring_authorized",
            "save_asset_authorized",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
        )
    )
    dispatch_release_contract_defined = bool(requested and start_contract_ready)
    dispatch_release_record_valid = bool(
        dispatch_release_contract_defined
        and dispatch_inputs_satisfied
        and record_schema_matches
        and dispatch_scope_matches
        and explicit_dispatch_authorized
        and no_save_delete_rename_acknowledged
        and unsafe_dispatch_release_record_count == 0
    )
    missing = []
    if requested:
        if not runner_plan_valid:
            missing.append("section_77_runner_plan_valid")
        if not start_record_valid:
            missing.append("section_77_start_record_valid")
        if not live_runner_started:
            missing.append("section_77_live_runner_started")
        if not dispatch_record_present:
            missing.append("live_command_dispatch_release_record_present")
        if not record_schema_matches:
            missing.append("live_command_dispatch_release_record_schema")
        if not dispatch_scope_matches:
            missing.append("durable_canary_live_command_dispatch_only_scope")
        if not explicit_dispatch_authorized:
            missing.append("explicit_live_command_dispatch_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        missing.append("separate_live_command_execution_release")
    dispatch_release_record_rejected = bool(dispatch_record_present and not dispatch_release_record_valid)
    return {
        "id": "durable_canary_live_command_dispatch_release",
        "schema": CANARY_LIVE_COMMAND_DISPATCH_RELEASE_SCHEMA,
        "requested": requested,
        "dispatch_release_contract_defined": dispatch_release_contract_defined,
        "required_dispatch_release_record_schema": (
            CANARY_LIVE_COMMAND_DISPATCH_RELEASE_RECORD_SCHEMA if requested else ""
        ),
        "expected_dispatch_scope": EXPECTED_DISPATCH_SCOPE if requested else "",
        "start_contract_ready": start_contract_ready,
        "runner_plan_valid": runner_plan_valid,
        "start_record_valid": start_record_valid,
        "live_runner_started": live_runner_started,
        "dispatch_inputs_satisfied": dispatch_inputs_satisfied,
        "dispatch_record_present": dispatch_record_present,
        "record_schema_matches": record_schema_matches,
        "dispatch_scope_matches": dispatch_scope_matches,
        "explicit_dispatch_authorized": explicit_dispatch_authorized,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "dispatch_release_record_valid": dispatch_release_record_valid,
        "dispatch_release_record_rejected": dispatch_release_record_rejected,
        "unsafe_dispatch_release_record_count": unsafe_dispatch_release_record_count,
        "missing_dispatch_prerequisites": missing,
        "missing_dispatch_prerequisite_count": len(missing),
        "live_command_dispatch_release_allowed": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_canary_rehearsal_performed": False,
        "canary_creation_allowed": False,
        "canary_save_allowed": False,
        "canary_cleanup_allowed": False,
        "durable_executor_may_open_after_dispatch_release": False,
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
            "section_78_dispatch_release_does_not_emit_live_commands",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped live command dispatch release only after Section 77 start evidence is valid",
            "reject dispatch records that authorize save, delete, rename, cleanup, or general durable authoring",
            "keep live command execution behind a separate release before issuing commands",
        ],
    }


def summarize_canary_live_command_dispatch_releases(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("dispatch_release_record_rejected"))
    unsafe_count = sum(
        contract.get("unsafe_dispatch_release_record_count", 0) for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("dispatch_release_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and sum(1 for contract in requested if contract.get("live_command_dispatch_release_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_dispatch_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_plan_emitted")) == 0
            and sum(1 for contract in requested if contract.get("live_canary_rehearsal_performed")) == 0
            and sum(1 for contract in requested if contract.get("canary_creation_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_save_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_cleanup_allowed")) == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_executor_may_open_after_dispatch_release")
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
        "schema": CANARY_LIVE_COMMAND_DISPATCH_RELEASE_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_live_command_dispatch_release_count": len(requested),
        "dispatch_release_contract_defined_count": sum(
            1 for contract in requested if contract.get("dispatch_release_contract_defined")
        ),
        "start_contract_ready_count": sum(
            1 for contract in requested if contract.get("start_contract_ready")
        ),
        "runner_plan_valid_count": sum(1 for contract in requested if contract.get("runner_plan_valid")),
        "start_record_valid_count": sum(1 for contract in requested if contract.get("start_record_valid")),
        "live_runner_started_count": sum(1 for contract in requested if contract.get("live_runner_started")),
        "dispatch_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("dispatch_inputs_satisfied")
        ),
        "dispatch_record_present_count": sum(
            1 for contract in requested if contract.get("dispatch_record_present")
        ),
        "record_schema_matches_count": sum(1 for contract in requested if contract.get("record_schema_matches")),
        "dispatch_scope_matches_count": sum(
            1 for contract in requested if contract.get("dispatch_scope_matches")
        ),
        "explicit_dispatch_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_dispatch_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "dispatch_release_record_valid_count": sum(
            1 for contract in requested if contract.get("dispatch_release_record_valid")
        ),
        "dispatch_release_record_rejected_count": rejected_count,
        "unsafe_dispatch_release_record_count": unsafe_count,
        "missing_dispatch_prerequisite_count": sum(
            contract.get("missing_dispatch_prerequisite_count", 0) for contract in requested
        ),
        "live_command_dispatch_release_allowed_count": sum(
            1 for contract in requested if contract.get("live_command_dispatch_release_allowed")
        ),
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
        "canary_cleanup_allowed_count": sum(
            1 for contract in requested if contract.get("canary_cleanup_allowed")
        ),
        "durable_executor_may_open_after_dispatch_release_count": sum(
            1
            for contract in requested
            if contract.get("durable_executor_may_open_after_dispatch_release")
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
