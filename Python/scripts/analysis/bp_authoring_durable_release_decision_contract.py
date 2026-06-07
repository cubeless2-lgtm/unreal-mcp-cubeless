#!/usr/bin/env python
"""
Section 70 durable Blueprint authoring release decision contract.

The release decision keeps temporary Blueprint authoring ready while durable
Blueprint authoring remains disabled. Section 61-69 contracts are safety
evidence, not an enable flag.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_RELEASE_DECISION_SCHEMA = "section_70_durable_release_decision_contract_v1"
DURABLE_RELEASE_DECISION_SUMMARY_SCHEMA = "section_70_durable_release_decision_summary_v1"


def build_durable_release_decision_contract(
    requested: bool,
    mvp_decision_contract: Dict[str, Any],
    executor_summary: Dict[str, Any],
    safety_contract_statuses: Sequence[str],
) -> Dict[str, Any]:
    durable_gate = executor_summary.get("durable_gate_summary", {})
    safety_contracts_passed = bool(safety_contract_statuses and all(status == "passed" for status in safety_contract_statuses))
    temporary_ready = bool(mvp_decision_contract.get("temporary_blueprint_authoring_mvp_ready"))
    durable_closed = bool(
        mvp_decision_contract.get("durable_blueprint_authoring_mvp_ready") is False
        and durable_gate.get("durable_executor_enabled_count") == 0
        and durable_gate.get("durable_executor_executable_count") == 0
        and durable_gate.get("save_or_delete_commands_allowed_count") == 0
        and durable_gate.get("allowed_live_authoring_command_count") == 0
        and durable_gate.get("preflight_pass_count") == 0
    )
    return {
        "id": "durable_blueprint_authoring_release_decision",
        "schema": DURABLE_RELEASE_DECISION_SCHEMA,
        "requested": requested,
        "decision_status": "section_70_temporary_mvp_ready_durable_not_enabled"
        if requested and temporary_ready and durable_closed and safety_contracts_passed
        else "section_70_release_decision_blocked",
        "temporary_blueprint_authoring_mvp_ready": temporary_ready,
        "durable_blueprint_authoring_mvp_ready": False,
        "durable_authoring_enabled": False,
        "section_61_69_safety_contracts_passed": safety_contracts_passed,
        "section_61_69_safety_contract_count": len(safety_contract_statuses),
        "durable_executor_enabled_count": durable_gate.get("durable_executor_enabled_count", 0),
        "durable_executor_executable_count": durable_gate.get("durable_executor_executable_count", 0),
        "save_or_delete_commands_allowed_count": durable_gate.get("save_or_delete_commands_allowed_count", 0),
        "allowed_live_authoring_command_count": durable_gate.get("allowed_live_authoring_command_count", 0),
        "preflight_pass_count": durable_gate.get("preflight_pass_count", 0),
        "final_durable_release_ready": False,
        "main_push_requested": False,
        "required_before_durable_release": [
            "refresh live canary read-only evidence on a reachable UnrealMCP bridge",
            "prove marker write/readback and rollback cleanup boundaries",
            "make Section 68 durable save gate ready without exposing save/delete/rename in temporary smoke",
            "run a separate explicit live canary rehearsal before durable MVP enable",
        ],
    }


def summarize_durable_release_decisions(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(
                1
                for contract in requested
                if contract.get("decision_status") == "section_70_temporary_mvp_ready_durable_not_enabled"
            )
            == len(requested)
            and sum(1 for contract in requested if contract.get("temporary_blueprint_authoring_mvp_ready")) == len(requested)
            and sum(1 for contract in requested if contract.get("durable_blueprint_authoring_mvp_ready")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_enabled")) == 0
            and sum(1 for contract in requested if contract.get("final_durable_release_ready")) == 0
            else "failed"
        )
    return {
        "schema": DURABLE_RELEASE_DECISION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_release_decision_count": len(requested),
        "temporary_blueprint_authoring_mvp_ready_count": sum(
            1 for contract in requested if contract.get("temporary_blueprint_authoring_mvp_ready")
        ),
        "durable_blueprint_authoring_mvp_ready_count": sum(
            1 for contract in requested if contract.get("durable_blueprint_authoring_mvp_ready")
        ),
        "durable_authoring_enabled_count": sum(
            1 for contract in requested if contract.get("durable_authoring_enabled")
        ),
        "section_61_69_safety_contracts_passed_count": sum(
            1 for contract in requested if contract.get("section_61_69_safety_contracts_passed")
        ),
        "durable_executor_enabled_count": sum(
            contract.get("durable_executor_enabled_count", 0) for contract in requested
        ),
        "durable_executor_executable_count": sum(
            contract.get("durable_executor_executable_count", 0) for contract in requested
        ),
        "save_or_delete_commands_allowed_count": sum(
            contract.get("save_or_delete_commands_allowed_count", 0) for contract in requested
        ),
        "allowed_live_authoring_command_count": sum(
            contract.get("allowed_live_authoring_command_count", 0) for contract in requested
        ),
        "preflight_pass_count": sum(contract.get("preflight_pass_count", 0) for contract in requested),
        "final_durable_release_ready_count": sum(
            1 for contract in requested if contract.get("final_durable_release_ready")
        ),
    }
