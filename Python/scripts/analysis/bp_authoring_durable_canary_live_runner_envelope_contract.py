#!/usr/bin/env python
"""
Section 76 durable canary live runner envelope contract.

This contract defines the command envelope required before a future live canary
runner may start. It does not start the runner and does not issue live commands.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_LIVE_RUNNER_ENVELOPE_SCHEMA = "section_76_durable_canary_live_runner_envelope_contract_v1"
CANARY_LIVE_RUNNER_PLAN_SCHEMA = "section_76_durable_canary_live_runner_plan_v1"
CANARY_LIVE_RUNNER_ENVELOPE_SUMMARY_SCHEMA = "section_76_durable_canary_live_runner_envelope_summary_v1"

ALLOWED_REHEARSAL_COMMANDS = (
    "create_canary_blueprint",
    "compile_canary_blueprint",
    "write_executor_ownership_marker",
    "readback_executor_ownership_marker",
    "read_only_asset_exists_check",
)
FORBIDDEN_REHEARSAL_COMMANDS = (
    "save_asset",
    "save_true",
    "delete_asset",
    "rename_asset",
    "cleanup_asset",
    "general_durable_authoring",
)


def build_canary_live_runner_envelope_contract(
    requested: bool,
    execution_release_summary: Dict[str, Any],
    runner_plan: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    runner_plan = runner_plan or {}
    execution_release_contract_ready = bool(
        requested
        and execution_release_summary.get("status") == "passed"
        and execution_release_summary.get("execution_release_contract_defined_count") == 1
        and execution_release_summary.get("unsafe_release_record_count") == 0
        and execution_release_summary.get("durable_executor_may_open_after_execution_release_count") == 0
    )
    execution_release_valid = bool(execution_release_summary.get("release_record_valid_count") == 1)
    live_runner_release_allowed = bool(
        execution_release_summary.get("live_canary_rehearsal_release_allowed_count") == 1
    )
    runner_plan_present = bool(runner_plan)
    runner_plan_schema_matches = bool(
        runner_plan_present and runner_plan.get("schema") == CANARY_LIVE_RUNNER_PLAN_SCHEMA
    )
    planned_commands = list(runner_plan.get("commands") or [])
    planned_command_count = len(planned_commands) if runner_plan_present else 0
    forbidden_commands = [command for command in planned_commands if command in FORBIDDEN_REHEARSAL_COMMANDS]
    unknown_commands = [
        command
        for command in planned_commands
        if command not in ALLOWED_REHEARSAL_COMMANDS and command not in FORBIDDEN_REHEARSAL_COMMANDS
    ]
    live_runner_envelope_defined = bool(requested and execution_release_contract_ready)
    runner_plan_valid = bool(
        live_runner_envelope_defined
        and execution_release_valid
        and live_runner_release_allowed
        and runner_plan_schema_matches
        and planned_command_count > 0
        and not forbidden_commands
        and not unknown_commands
    )
    missing = []
    if requested:
        if not execution_release_valid:
            missing.append("section_75_execution_release_record_valid")
        if not live_runner_release_allowed:
            missing.append("section_75_live_canary_rehearsal_release_allowed")
        if not runner_plan_present:
            missing.append("live_runner_plan_present")
        if not runner_plan_schema_matches:
            missing.append("live_runner_plan_schema")
        if planned_command_count == 0:
            missing.append("live_runner_commands_present")
        missing.append("separate_operator_live_runner_start")
    runner_plan_rejected = bool(runner_plan_present and not runner_plan_valid)
    return {
        "id": "durable_canary_live_runner_envelope",
        "schema": CANARY_LIVE_RUNNER_ENVELOPE_SCHEMA,
        "requested": requested,
        "live_runner_envelope_defined": live_runner_envelope_defined,
        "required_runner_plan_schema": CANARY_LIVE_RUNNER_PLAN_SCHEMA if requested else "",
        "execution_release_contract_ready": execution_release_contract_ready,
        "execution_release_valid": execution_release_valid,
        "live_runner_release_allowed": live_runner_release_allowed,
        "runner_plan_present": runner_plan_present,
        "runner_plan_schema_matches": runner_plan_schema_matches,
        "planned_command_count": planned_command_count,
        "forbidden_runner_command_count": len(forbidden_commands),
        "unknown_runner_command_count": len(unknown_commands),
        "runner_plan_valid": runner_plan_valid,
        "runner_plan_rejected": runner_plan_rejected,
        "missing_runner_prerequisites": missing,
        "missing_runner_prerequisite_count": len(missing),
        "live_runner_may_start": False,
        "live_runner_started": False,
        "live_command_plan_emitted": False,
        "live_canary_rehearsal_performed": False,
        "canary_creation_allowed": False,
        "canary_save_allowed": False,
        "canary_cleanup_allowed": False,
        "durable_executor_may_open_after_runner": False,
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
            "section_76_live_runner_envelope_does_not_start_runner",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "supply a Section 76 runner plan only after Section 75 live runner release is allowed",
            "reject any runner plan containing save, delete, rename, cleanup, or general durable authoring",
            "keep live runner start as a separate operator action after envelope validation",
        ],
    }


def summarize_canary_live_runner_envelopes(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("runner_plan_rejected"))
    forbidden_count = sum(contract.get("forbidden_runner_command_count", 0) for contract in requested)
    unknown_count = sum(contract.get("unknown_runner_command_count", 0) for contract in requested)
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("live_runner_envelope_defined")) == len(requested)
            and rejected_count == 0
            and forbidden_count == 0
            and unknown_count == 0
            and sum(1 for contract in requested if contract.get("live_runner_may_start")) == 0
            and sum(1 for contract in requested if contract.get("live_runner_started")) == 0
            and sum(1 for contract in requested if contract.get("live_command_plan_emitted")) == 0
            and sum(1 for contract in requested if contract.get("live_canary_rehearsal_performed")) == 0
            and sum(1 for contract in requested if contract.get("canary_creation_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_save_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_cleanup_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_after_runner")) == 0
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
        "schema": CANARY_LIVE_RUNNER_ENVELOPE_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_live_runner_envelope_count": len(requested),
        "live_runner_envelope_defined_count": sum(
            1 for contract in requested if contract.get("live_runner_envelope_defined")
        ),
        "execution_release_contract_ready_count": sum(
            1 for contract in requested if contract.get("execution_release_contract_ready")
        ),
        "execution_release_valid_count": sum(
            1 for contract in requested if contract.get("execution_release_valid")
        ),
        "live_runner_release_allowed_count": sum(
            1 for contract in requested if contract.get("live_runner_release_allowed")
        ),
        "runner_plan_present_count": sum(1 for contract in requested if contract.get("runner_plan_present")),
        "runner_plan_schema_matches_count": sum(
            1 for contract in requested if contract.get("runner_plan_schema_matches")
        ),
        "planned_command_count": sum(contract.get("planned_command_count", 0) for contract in requested),
        "forbidden_runner_command_count": forbidden_count,
        "unknown_runner_command_count": unknown_count,
        "runner_plan_valid_count": sum(1 for contract in requested if contract.get("runner_plan_valid")),
        "runner_plan_rejected_count": rejected_count,
        "missing_runner_prerequisite_count": sum(
            contract.get("missing_runner_prerequisite_count", 0) for contract in requested
        ),
        "live_runner_may_start_count": sum(1 for contract in requested if contract.get("live_runner_may_start")),
        "live_runner_started_count": sum(1 for contract in requested if contract.get("live_runner_started")),
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
        "durable_executor_may_open_after_runner_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_after_runner")
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
        "live_cleanup_command_count": sum(
            contract.get("live_cleanup_command_count", 0) for contract in requested
        ),
    }
