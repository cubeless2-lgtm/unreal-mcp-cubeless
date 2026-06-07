#!/usr/bin/env python
"""
Section 54 durable save validation simulator.

This simulator evaluates durable save prerequisites without running
compile(save=true), save_asset, delete_asset, rename_asset, or any live durable
authoring command.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


SAVE_SIMULATION_SCHEMA = "section_54_durable_save_validation_simulator_v1"
SAVE_SIMULATION_SUMMARY_SCHEMA = "section_54_durable_save_validation_simulator_summary_v1"


def _check(check_id: str, label: str, passed: bool, evidence: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": check_id,
        "label": label,
        "required": True,
        "passed": bool(passed),
        "evidence": evidence,
    }


def build_save_validation_simulation(
    requested: bool,
    preflight_contract: Dict[str, Any],
    enable_contract: Dict[str, Any],
    ownership_marker_contract: Dict[str, Any],
    dry_run_plan_contract: Dict[str, Any],
    save_gate_contract: Dict[str, Any],
    rollback_policy_contract: Dict[str, Any],
    readiness_contract: Dict[str, Any],
) -> Dict[str, Any]:
    target_asset_path = preflight_contract.get("target_asset_path", "")
    checks = []
    if requested:
        checks = [
            _check(
                "target_package_allowlisted",
                "Target package path is allowlisted",
                bool(preflight_contract.get("package_path_allowed")),
                {"target_package_path": preflight_contract.get("target_package_path", "")},
            ),
            _check(
                "read_only_asset_exists_result_available",
                "Read-only asset-exists result is available to the save gate",
                bool(save_gate_contract.get("prerequisites", {}).get("asset_exists_result_available_in_manifest")),
                {"asset_exists": preflight_contract.get("asset_exists")},
            ),
            _check(
                "overwrite_or_rename_decision_present",
                "Overwrite-or-rename decision is present and conflict-free",
                bool(
                    save_gate_contract.get("prerequisites", {}).get("overwrite_or_rename_decision_present")
                    and save_gate_contract.get("prerequisites", {}).get("overwrite_or_rename_decision_conflict_free")
                ),
                preflight_contract.get("overwrite_rename_decision_contract", {}),
            ),
            _check(
                "ownership_marker_policy_ready",
                "Executor-created ownership marker policy is ready",
                bool(ownership_marker_contract.get("ownership_marker_policy_ready")),
                {"marker_schema": ownership_marker_contract.get("schema", "")},
            ),
            _check(
                "rollback_policy_ready",
                "Rollback policy is ready",
                bool(rollback_policy_contract.get("rollback_policy_ready")),
                {"rollback_allowed": rollback_policy_contract.get("rollback_allowed")},
            ),
            _check(
                "dry_run_plan_valid",
                "Section 53 dry-run plan is valid and has no live commands",
                bool(
                    dry_run_plan_contract.get("dry_run_plan_valid")
                    and dry_run_plan_contract.get("live_command_count", 0) == 0
                    and not dry_run_plan_contract.get("durable_executor_may_execute")
                ),
                {"plan_step_count": dry_run_plan_contract.get("plan_step_count", 0)},
            ),
            _check(
                "enable_contract_satisfied",
                "Section 51 enable contract is satisfied",
                bool(enable_contract.get("enable_contract_satisfied")),
                {"failed_required_gate_ids": enable_contract.get("failed_required_gate_ids", [])},
            ),
            _check(
                "compile_save_validation_enabled",
                "Durable compile/save validation is enabled for simulation",
                bool(save_gate_contract.get("prerequisites", {}).get("durable_compile_save_validation_enabled")),
                {},
            ),
            _check(
                "explicit_durable_executor_enable_flag",
                "Explicit durable executor enable flag is set",
                bool(
                    any(
                        item.get("id") == "explicit_durable_executor_enable_flag" and item.get("passed")
                        for item in readiness_contract.get("checks", [])
                    )
                ),
                {},
            ),
        ]

    failed_checks = [check["id"] for check in checks if check["required"] and not check["passed"]]
    evaluated = bool(requested and target_asset_path)
    conditions_satisfied = bool(evaluated and not failed_checks)
    blocked_by = list(failed_checks)
    if requested:
        blocked_by.append("section_54_simulator_does_not_enable_save")
    return {
        "id": "durable_save_validation_simulator",
        "schema": SAVE_SIMULATION_SCHEMA,
        "requested": requested,
        "target_asset_path": target_asset_path,
        "simulation_evaluated": evaluated,
        "simulation_status": "blocked" if requested else "not_requested",
        "checks": checks,
        "failed_check_ids": failed_checks,
        "future_save_conditions_satisfied": conditions_satisfied,
        "save_true_allowed": False,
        "save_asset_allowed": False,
        "compile_save_command_allowed": False,
        "live_command_count": 0,
        "durable_authoring_allowed": False,
        "blocked_by": sorted(set(blocked_by)),
        "required_reinforcement": []
        if not requested
        else [
            "provide read-only asset-exists result to the durable save gate",
            "satisfy conflict, rollback, enable, compile-save validation, and explicit enable checks",
            "keep simulator no-command until a later durable canary release",
        ],
    }


def summarize_save_simulations(simulations: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [simulation for simulation in simulations if simulation.get("requested")]
    live_command_count = sum(simulation.get("live_command_count", 0) for simulation in requested)
    forbidden_allowed_count = sum(
        1
        for simulation in requested
        if simulation.get("save_true_allowed")
        or simulation.get("save_asset_allowed")
        or simulation.get("compile_save_command_allowed")
    )
    status = "not_requested"
    if requested:
        status = "passed" if live_command_count == 0 and forbidden_allowed_count == 0 else "failed"
    return {
        "schema": SAVE_SIMULATION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_simulation_count": len(requested),
        "simulation_evaluated_count": sum(1 for simulation in requested if simulation.get("simulation_evaluated")),
        "future_save_conditions_satisfied_count": sum(
            1 for simulation in requested if simulation.get("future_save_conditions_satisfied")
        ),
        "save_true_allowed_count": sum(1 for simulation in requested if simulation.get("save_true_allowed")),
        "save_asset_allowed_count": sum(1 for simulation in requested if simulation.get("save_asset_allowed")),
        "compile_save_command_allowed_count": sum(
            1 for simulation in requested if simulation.get("compile_save_command_allowed")
        ),
        "live_command_count": live_command_count,
        "forbidden_command_allowed_count": forbidden_allowed_count,
    }
