#!/usr/bin/env python
"""
Section 58 durable canary recovery matrix contract.

The matrix defines rollback and cleanup evidence requirements for a future
durable canary. It is report-only and does not allow cleanup, delete, save, or
authoring commands.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_RECOVERY_SCHEMA = "section_58_durable_canary_recovery_matrix_v1"
CANARY_RECOVERY_SUMMARY_SCHEMA = "section_58_durable_canary_recovery_summary_v1"


def _scenario(scenario_id: str, trigger: str, required_evidence: Sequence[str]) -> Dict[str, Any]:
    return {
        "id": scenario_id,
        "trigger": trigger,
        "mode": "offline_report_only",
        "required_evidence": list(required_evidence),
        "cleanup_command_allowed": False,
        "delete_command_allowed": False,
        "save_command_allowed": False,
        "authoring_command_allowed": False,
    }


def build_canary_recovery_matrix_contract(
    requested: bool,
    canary_prep_contract: Dict[str, Any],
    canary_live_preflight_contract: Dict[str, Any],
) -> Dict[str, Any]:
    canary_asset_path = canary_prep_contract.get("canary_asset_path", "")
    live_preflight_allowed = bool(canary_live_preflight_contract.get("read_only_live_preflight_allowed"))
    scenarios = []
    if requested:
        scenarios = [
            _scenario(
                "preflight_asset_absent",
                "Read-only canary preflight reports the canary asset does not exist.",
                ("section_57_canary_live_preflight_result", "asset_exists_false"),
            ),
            _scenario(
                "preflight_asset_present",
                "Read-only canary preflight reports the canary asset already exists.",
                ("section_57_canary_live_preflight_result", "manual_review_before_reuse_or_cleanup"),
            ),
            _scenario(
                "creation_fails_before_marker",
                "A future canary creation attempt fails before an ownership marker is recorded.",
                ("no_cleanup_without_marker", "manual_review_required"),
            ),
            _scenario(
                "creation_fails_after_marker",
                "A future canary creation attempt fails after an ownership marker is recorded.",
                ("executor_created_ownership_marker", "created_asset_path_matches_canary_path"),
            ),
            _scenario(
                "compile_or_save_blocked",
                "A future canary compile/save path remains blocked by policy.",
                ("compile_result", "save_gate_denied", "no_save_command_executed"),
            ),
            _scenario(
                "cleanup_marker_valid",
                "A future cleanup request has a marker that matches the canary target and run id.",
                ("executor_created_ownership_marker", "preflight_asset_exists_false", "run_id_matches"),
            ),
        ]
    matrix_ready = bool(requested and canary_asset_path and live_preflight_allowed and len(scenarios) == 6)
    blocked_by: list[str] = []
    if requested:
        if not canary_asset_path:
            blocked_by.append("canary_asset_path_missing")
        if not live_preflight_allowed:
            blocked_by.append("canary_live_preflight_not_allowed")
        blocked_by.append("section_58_recovery_matrix_report_only")

    return {
        "id": "durable_canary_recovery_matrix",
        "schema": CANARY_RECOVERY_SCHEMA,
        "requested": requested,
        "canary_asset_path": canary_asset_path if requested else "",
        "canary_live_preflight_allowed": live_preflight_allowed if requested else False,
        "recovery_matrix_defined": bool(scenarios),
        "recovery_matrix_ready": matrix_ready,
        "scenario_count": len(scenarios),
        "scenarios": scenarios,
        "cleanup_requires_ownership_marker": requested,
        "cleanup_requires_preflight_asset_absent": requested,
        "cleanup_requires_created_asset_path_match": requested,
        "cleanup_command_allowed": False,
        "delete_command_allowed": False,
        "save_command_allowed": False,
        "authoring_command_allowed": False,
        "live_cleanup_command_count": 0,
        "live_delete_command_count": 0,
        "live_save_command_count": 0,
        "live_authoring_command_count": 0,
        "blocked_by": sorted(set(blocked_by)),
        "required_reinforcement": []
        if not requested
        else [
            "keep Section 58 recovery matrix report-only",
            "require a valid ownership marker before any future cleanup command",
            "prove cleanup/delete behavior in a separate section before enabling it",
        ],
    }


def summarize_canary_recovery_matrices(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("recovery_matrix_ready")) == len(requested)
            and sum(1 for contract in requested if contract.get("cleanup_command_allowed")) == 0
            and sum(1 for contract in requested if contract.get("delete_command_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_command_allowed")) == 0
            and sum(1 for contract in requested if contract.get("authoring_command_allowed")) == 0
            and sum(contract.get("live_cleanup_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_delete_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_save_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_authoring_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": CANARY_RECOVERY_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_recovery_count": len(requested),
        "recovery_matrix_ready_count": sum(1 for contract in requested if contract.get("recovery_matrix_ready")),
        "scenario_count": sum(contract.get("scenario_count", 0) for contract in requested),
        "cleanup_command_allowed_count": sum(1 for contract in requested if contract.get("cleanup_command_allowed")),
        "delete_command_allowed_count": sum(1 for contract in requested if contract.get("delete_command_allowed")),
        "save_command_allowed_count": sum(1 for contract in requested if contract.get("save_command_allowed")),
        "authoring_command_allowed_count": sum(1 for contract in requested if contract.get("authoring_command_allowed")),
        "live_cleanup_command_count": sum(contract.get("live_cleanup_command_count", 0) for contract in requested),
        "live_delete_command_count": sum(contract.get("live_delete_command_count", 0) for contract in requested),
        "live_save_command_count": sum(contract.get("live_save_command_count", 0) for contract in requested),
        "live_authoring_command_count": sum(contract.get("live_authoring_command_count", 0) for contract in requested),
    }
