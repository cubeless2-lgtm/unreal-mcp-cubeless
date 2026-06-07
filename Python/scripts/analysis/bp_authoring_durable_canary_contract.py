#!/usr/bin/env python
"""
Section 55 durable canary preparation contract.

The canary prep defines a narrow target and cleanup boundary for a future
durable canary. It does not approve or execute live durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_PREP_SCHEMA = "section_55_durable_canary_prep_contract_v1"
CANARY_PREP_SUMMARY_SCHEMA = "section_55_durable_canary_prep_summary_v1"

DEFAULT_CANARY_PACKAGE_PATH = "/Game/_MCP_Temp/DurableCanary"
CANARY_PACKAGE_ALLOWLIST = (DEFAULT_CANARY_PACKAGE_PATH,)


def canary_package_is_allowlisted(package_path: str) -> bool:
    normalized = package_path.rstrip("/")
    return any(normalized == allowed or normalized.startswith(f"{allowed}/") for allowed in CANARY_PACKAGE_ALLOWLIST)


def build_canary_prep_contract(
    requested: bool,
    source_target_asset_path: str,
    requested_blueprint_name: str,
    ownership_marker_contract: Dict[str, Any],
    save_simulation_contract: Dict[str, Any],
    canary_package_path: str = DEFAULT_CANARY_PACKAGE_PATH,
) -> Dict[str, Any]:
    canary_blueprint_name = f"{requested_blueprint_name or 'BP_Durable'}_Canary"
    canary_asset_path = f"{canary_package_path.rstrip('/')}/{canary_blueprint_name}" if requested else ""
    target_allowlisted = canary_package_is_allowlisted(canary_package_path)
    prep_ready = bool(
        requested
        and canary_asset_path
        and target_allowlisted
        and ownership_marker_contract.get("ownership_marker_policy_ready")
        and save_simulation_contract.get("simulation_evaluated")
    )
    blocked_by: list[str] = []
    if requested:
        if not target_allowlisted:
            blocked_by.append("canary_package_not_allowlisted")
        if not ownership_marker_contract.get("ownership_marker_policy_ready"):
            blocked_by.append("ownership_marker_policy_not_ready")
        if not save_simulation_contract.get("simulation_evaluated"):
            blocked_by.append("save_simulation_not_evaluated")
        blocked_by.append("section_55_prep_only_no_live_canary")

    return {
        "id": "durable_canary_prep",
        "schema": CANARY_PREP_SCHEMA,
        "requested": requested,
        "source_target_asset_path": source_target_asset_path,
        "canary_package_path": canary_package_path if requested else "",
        "canary_blueprint_name": canary_blueprint_name if requested else "",
        "canary_asset_path": canary_asset_path,
        "canary_package_allowlist": list(CANARY_PACKAGE_ALLOWLIST),
        "canary_package_allowlisted": target_allowlisted if requested else False,
        "canary_prep_ready": prep_ready,
        "canary_live_execution_allowed": False,
        "general_blueprints_package_allowed": False,
        "preexisting_asset_overwrite_allowed": False,
        "save_true_allowed": False,
        "save_asset_allowed": False,
        "delete_asset_allowed": False,
        "cleanup_requires_ownership_marker": requested,
        "cleanup_allowed_package_path": canary_package_path if requested else "",
        "blocked_by": sorted(set(blocked_by)),
        "required_reinforcement": []
        if not requested
        else [
            "add Section 56 explicit canary approval before live canary execution",
            "keep canary target under the canary package allowlist",
            "prove cleanup only touches ownership-marked canary assets",
        ],
    }


def summarize_canary_prep_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("canary_live_execution_allowed")) == 0
            and sum(1 for contract in requested if contract.get("general_blueprints_package_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_true_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_asset_allowed")) == 0
            and sum(1 for contract in requested if contract.get("delete_asset_allowed")) == 0
            else "failed"
        )
    return {
        "schema": CANARY_PREP_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_prep_count": len(requested),
        "canary_prep_ready_count": sum(1 for contract in requested if contract.get("canary_prep_ready")),
        "canary_live_execution_allowed_count": sum(
            1 for contract in requested if contract.get("canary_live_execution_allowed")
        ),
        "general_blueprints_package_allowed_count": sum(
            1 for contract in requested if contract.get("general_blueprints_package_allowed")
        ),
        "save_true_allowed_count": sum(1 for contract in requested if contract.get("save_true_allowed")),
        "save_asset_allowed_count": sum(1 for contract in requested if contract.get("save_asset_allowed")),
        "delete_asset_allowed_count": sum(1 for contract in requested if contract.get("delete_asset_allowed")),
    }
