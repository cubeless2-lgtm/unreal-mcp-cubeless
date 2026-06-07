#!/usr/bin/env python
"""
Section 65 durable canary creation boundary contract.

The canary target may be prepared, but live canary creation remains closed.
This contract prevents a read-only canary preflight from turning into
create/save/delete behavior.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_CREATION_BOUNDARY_SCHEMA = "section_65_durable_canary_creation_boundary_contract_v1"
CANARY_CREATION_BOUNDARY_SUMMARY_SCHEMA = "section_65_durable_canary_creation_boundary_summary_v1"


def build_canary_creation_boundary_contract(
    requested: bool,
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
) -> Dict[str, Any]:
    durable_gate = executor_summary.get("durable_gate_summary", {})
    boundary_defined = bool(
        requested
        and contract_summary.get("durable_canary_prep_ready_count") == 1
        and contract_summary.get("durable_canary_approval_gate_passed_count") == 1
        and contract_summary.get("durable_canary_live_preflight_read_only_allowed_count") == 1
    )
    create_command_allowed = False
    save_command_allowed = False
    delete_command_allowed = False
    cleanup_command_allowed = False
    live_execution_allowed = bool(
        durable_gate.get("canary_live_execution_allowed_count")
        or durable_gate.get("canary_live_preflight_execution_allowed_count")
        or durable_gate.get("canary_bridge_refresh_execution_allowed_count")
    )
    return {
        "id": "durable_canary_creation_boundary",
        "schema": CANARY_CREATION_BOUNDARY_SCHEMA,
        "requested": requested,
        "canary_creation_boundary_defined": boundary_defined,
        "canary_prep_ready_count": contract_summary.get("durable_canary_prep_ready_count", 0),
        "canary_approval_gate_passed_count": contract_summary.get("durable_canary_approval_gate_passed_count", 0),
        "read_only_preflight_allowed_count": contract_summary.get(
            "durable_canary_live_preflight_read_only_allowed_count",
            0,
        ),
        "bridge_refresh_satisfied_count": durable_gate.get("canary_bridge_refresh_satisfied_count", 0),
        "create_blueprint_allowed": create_command_allowed,
        "save_command_allowed": save_command_allowed,
        "delete_command_allowed": delete_command_allowed,
        "cleanup_command_allowed": cleanup_command_allowed,
        "live_canary_creation_allowed": live_execution_allowed and create_command_allowed,
        "durable_executor_may_open_for_creation": False,
        "live_creation_command_count": 0,
        "live_save_or_delete_command_count": 0,
        "blocked_by": []
        if not requested
        else [
            "section_65_creation_boundary_does_not_allow_create_blueprint",
            "bridge_refresh_and_live_evidence_not_satisfied_for_creation",
        ],
        "required_reinforcement": []
        if not requested
        else [
            "prove fresh bridge and read-only canary evidence before any creation rehearsal",
            "define an explicit create command allowlist in a later release",
            "keep save/delete/cleanup disabled during canary creation boundary review",
        ],
    }


def summarize_canary_creation_boundary_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("canary_creation_boundary_defined")) == len(requested)
            and sum(1 for contract in requested if contract.get("create_blueprint_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_command_allowed")) == 0
            and sum(1 for contract in requested if contract.get("delete_command_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_command_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_canary_creation_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_for_creation")) == 0
            and sum(contract.get("live_creation_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_save_or_delete_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": CANARY_CREATION_BOUNDARY_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_creation_boundary_count": len(requested),
        "canary_creation_boundary_defined_count": sum(
            1 for contract in requested if contract.get("canary_creation_boundary_defined")
        ),
        "create_blueprint_allowed_count": sum(
            1 for contract in requested if contract.get("create_blueprint_allowed")
        ),
        "save_command_allowed_count": sum(1 for contract in requested if contract.get("save_command_allowed")),
        "delete_command_allowed_count": sum(1 for contract in requested if contract.get("delete_command_allowed")),
        "cleanup_command_allowed_count": sum(1 for contract in requested if contract.get("cleanup_command_allowed")),
        "live_canary_creation_allowed_count": sum(
            1 for contract in requested if contract.get("live_canary_creation_allowed")
        ),
        "durable_executor_may_open_for_creation_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_for_creation")
        ),
        "live_creation_command_count": sum(contract.get("live_creation_command_count", 0) for contract in requested),
        "live_save_or_delete_command_count": sum(
            contract.get("live_save_or_delete_command_count", 0) for contract in requested
        ),
    }
