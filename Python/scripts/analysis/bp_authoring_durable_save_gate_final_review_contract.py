#!/usr/bin/env python
"""
Section 68 durable save gate final enable review contract.

The save gate is reviewed against all accumulated durable prerequisites. The
review may pass as a closed gate, but it does not enable save=true/save_asset.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


SAVE_GATE_FINAL_REVIEW_SCHEMA = "section_68_durable_save_gate_final_review_contract_v1"
SAVE_GATE_FINAL_REVIEW_SUMMARY_SCHEMA = "section_68_durable_save_gate_final_review_summary_v1"


def build_save_gate_final_review_contract(
    requested: bool,
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
) -> Dict[str, Any]:
    durable_gate = executor_summary.get("durable_gate_summary", {})
    review_complete = bool(
        requested
        and contract_summary.get("durable_save_simulation_evaluated_count") == 1
        and contract_summary.get("durable_enable_target_package_allowlist_passed_count") == 1
        and durable_gate.get("status") == "passed"
    )
    missing = []
    if requested:
        if contract_summary.get("durable_enable_overwrite_rename_decision_passed_count") != 1:
            missing.append("overwrite_or_rename_decision")
        if contract_summary.get("durable_enable_rollback_readiness_passed_count") != 1:
            missing.append("rollback_readiness")
        if contract_summary.get("durable_save_simulation_conditions_satisfied_count") != 1:
            missing.append("save_validation_conditions")
        if durable_gate.get("preflight_pass_count") != 1:
            missing.append("durable_live_preflight_pass")
    return {
        "id": "durable_save_gate_final_enable_review",
        "schema": SAVE_GATE_FINAL_REVIEW_SCHEMA,
        "requested": requested,
        "save_gate_final_review_complete": review_complete,
        "missing_enable_prerequisites": missing,
        "missing_enable_prerequisite_count": len(missing),
        "durable_save_enable_ready": False,
        "save_true_allowed": False,
        "save_asset_allowed": False,
        "compile_save_allowed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        "durable_executor_may_open_after_save_review": False,
        "live_save_command_count": 0,
        "live_delete_or_rename_command_count": 0,
        "blocked_by": []
        if not requested
        else [
            "section_68_save_gate_review_does_not_enable_save",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "satisfy overwrite/rename and rollback readiness before durable save",
            "promote a passed live read-only preflight result before durable save",
            "keep save=true and save_asset forbidden until a later explicit durable release",
        ],
    }


def summarize_save_gate_final_review_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("save_gate_final_review_complete")) == len(requested)
            and sum(1 for contract in requested if contract.get("durable_save_enable_ready")) == 0
            and sum(1 for contract in requested if contract.get("save_true_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_asset_allowed")) == 0
            and sum(1 for contract in requested if contract.get("compile_save_allowed")) == 0
            and sum(1 for contract in requested if contract.get("delete_asset_allowed")) == 0
            and sum(1 for contract in requested if contract.get("rename_asset_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_after_save_review")) == 0
            and sum(contract.get("live_save_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_delete_or_rename_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": SAVE_GATE_FINAL_REVIEW_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_save_gate_final_review_count": len(requested),
        "save_gate_final_review_complete_count": sum(
            1 for contract in requested if contract.get("save_gate_final_review_complete")
        ),
        "missing_enable_prerequisite_count": sum(
            contract.get("missing_enable_prerequisite_count", 0) for contract in requested
        ),
        "durable_save_enable_ready_count": sum(
            1 for contract in requested if contract.get("durable_save_enable_ready")
        ),
        "save_true_allowed_count": sum(1 for contract in requested if contract.get("save_true_allowed")),
        "save_asset_allowed_count": sum(1 for contract in requested if contract.get("save_asset_allowed")),
        "compile_save_allowed_count": sum(1 for contract in requested if contract.get("compile_save_allowed")),
        "delete_asset_allowed_count": sum(1 for contract in requested if contract.get("delete_asset_allowed")),
        "rename_asset_allowed_count": sum(1 for contract in requested if contract.get("rename_asset_allowed")),
        "durable_executor_may_open_after_save_review_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_after_save_review")
        ),
        "live_save_command_count": sum(contract.get("live_save_command_count", 0) for contract in requested),
        "live_delete_or_rename_command_count": sum(
            contract.get("live_delete_or_rename_command_count", 0) for contract in requested
        ),
    }
