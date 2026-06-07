#!/usr/bin/env python
"""
Section 57 durable canary live preflight contract.

The contract allows only a read-only asset-exists preflight for the prepared
canary target. It does not allow canary execution, authoring, save, delete, or
cleanup commands.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_LIVE_PREFLIGHT_CONTRACT_SCHEMA = "section_57_durable_canary_live_preflight_contract_v1"
CANARY_LIVE_PREFLIGHT_RESULT_SCHEMA = "section_57_durable_canary_live_preflight_result_v1"
CANARY_LIVE_PREFLIGHT_SUMMARY_SCHEMA = "section_57_durable_canary_live_preflight_summary_v1"

READ_ONLY_COMMAND = "unreal.EditorAssetLibrary.does_asset_exist"


def build_canary_live_preflight_contract(
    requested: bool,
    canary_prep_contract: Dict[str, Any],
    canary_approval_gate_contract: Dict[str, Any],
) -> Dict[str, Any]:
    canary_asset_path = canary_prep_contract.get("canary_asset_path", "")
    read_only_allowed = bool(
        requested
        and canary_asset_path
        and canary_prep_contract.get("canary_prep_ready")
        and canary_approval_gate_contract.get("canary_approval_gate_passed")
        and not canary_approval_gate_contract.get("canary_executor_may_open")
        and not canary_approval_gate_contract.get("canary_live_execution_allowed")
    )
    blocked_by: list[str] = []
    if requested:
        if not canary_asset_path:
            blocked_by.append("canary_asset_path_missing")
        if not canary_prep_contract.get("canary_prep_ready"):
            blocked_by.append("canary_prep_not_ready")
        if not canary_approval_gate_contract.get("canary_approval_gate_passed"):
            blocked_by.append("canary_approval_gate_not_passed")
        blocked_by.append("section_57_read_only_canary_preflight_only")

    return {
        "id": "durable_canary_live_preflight",
        "schema": CANARY_LIVE_PREFLIGHT_CONTRACT_SCHEMA,
        "requested": requested,
        "canary_asset_path": canary_asset_path if requested else "",
        "canary_package_path": canary_prep_contract.get("canary_package_path", "") if requested else "",
        "canary_approval_gate_passed": bool(canary_approval_gate_contract.get("canary_approval_gate_passed")),
        "read_only_live_preflight_allowed": read_only_allowed,
        "read_only_live_command": READ_ONLY_COMMAND if read_only_allowed else "",
        "canary_execution_allowed_after_preflight": False,
        "authoring_command_allowed": False,
        "save_or_delete_allowed": False,
        "cleanup_command_allowed": False,
        "live_authoring_command_count": 0,
        "live_save_or_delete_command_count": 0,
        "live_cleanup_command_count": 0,
        "result_schema": CANARY_LIVE_PREFLIGHT_RESULT_SCHEMA,
        "preflight_result_required_before_canary_execution": requested,
        "blocked_by": sorted(set(blocked_by)),
        "required_reinforcement": []
        if not requested
        else [
            "keep Section 57 canary live preflight read-only",
            "record canary asset-exists result before any future canary execution",
            "prove Section 58 rollback recovery before enabling cleanup or delete",
        ],
    }


def build_not_requested_live_result(manifest_id: str, contract: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "schema": CANARY_LIVE_PREFLIGHT_RESULT_SCHEMA,
        "manifest_id": manifest_id,
        "canary_asset_path": contract.get("canary_asset_path", ""),
        "status": "not_requested",
        "read_only": True,
        "authoring_attempted": False,
        "save_or_delete_attempted": False,
        "cleanup_attempted": False,
        "canary_execution_attempted": False,
        "asset_exists_check_performed": False,
        "asset_exists": None,
        "canary_execution_allowed_after_preflight": False,
    }


def summarize_canary_live_preflight_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("read_only_live_preflight_allowed")) == len(requested)
            and sum(1 for contract in requested if contract.get("canary_execution_allowed_after_preflight")) == 0
            and sum(1 for contract in requested if contract.get("authoring_command_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_or_delete_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_command_allowed")) == 0
            and sum(contract.get("live_authoring_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_save_or_delete_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_cleanup_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": CANARY_LIVE_PREFLIGHT_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_live_preflight_count": len(requested),
        "read_only_live_preflight_allowed_count": sum(
            1 for contract in requested if contract.get("read_only_live_preflight_allowed")
        ),
        "canary_execution_allowed_after_preflight_count": sum(
            1 for contract in requested if contract.get("canary_execution_allowed_after_preflight")
        ),
        "authoring_command_allowed_count": sum(1 for contract in requested if contract.get("authoring_command_allowed")),
        "save_or_delete_allowed_count": sum(1 for contract in requested if contract.get("save_or_delete_allowed")),
        "cleanup_command_allowed_count": sum(1 for contract in requested if contract.get("cleanup_command_allowed")),
        "live_authoring_command_count": sum(contract.get("live_authoring_command_count", 0) for contract in requested),
        "live_save_or_delete_command_count": sum(
            contract.get("live_save_or_delete_command_count", 0) for contract in requested
        ),
        "live_cleanup_command_count": sum(contract.get("live_cleanup_command_count", 0) for contract in requested),
    }


def summarize_canary_live_preflight_results(
    manifests: Sequence[Dict[str, Any]],
    live_preflight_results: Sequence[Dict[str, Any]],
    live_requested: bool,
) -> Dict[str, Any]:
    requested_manifests = [
        manifest
        for manifest in manifests
        if manifest.get("durable_canary_live_preflight_contract", {}).get("requested")
    ]
    allowed_manifest_ids = {
        manifest.get("id", "")
        for manifest in requested_manifests
        if manifest.get("durable_canary_live_preflight_contract", {}).get("read_only_live_preflight_allowed")
    }
    result_manifest_ids = {result.get("manifest_id", "") for result in live_preflight_results}
    authoring_attempted_count = sum(1 for result in live_preflight_results if result.get("authoring_attempted"))
    save_or_delete_attempted_count = sum(
        1 for result in live_preflight_results if result.get("save_or_delete_attempted")
    )
    cleanup_attempted_count = sum(1 for result in live_preflight_results if result.get("cleanup_attempted"))
    canary_execution_attempted_count = sum(
        1 for result in live_preflight_results if result.get("canary_execution_attempted")
    )
    passed_read_only_result_count = sum(
        1
        for result in live_preflight_results
        if result.get("status") == "passed"
        and result.get("read_only") is True
        and result.get("asset_exists_check_performed") is True
        and not result.get("authoring_attempted")
        and not result.get("save_or_delete_attempted")
        and not result.get("cleanup_attempted")
        and not result.get("canary_execution_attempted")
        and not result.get("canary_execution_allowed_after_preflight")
    )
    missing = sorted(allowed_manifest_ids - result_manifest_ids)
    unexpected = sorted(result_manifest_ids - allowed_manifest_ids)
    status = "not_requested"
    if live_requested:
        status = (
            "passed"
            if len(live_preflight_results) == len(allowed_manifest_ids)
            and passed_read_only_result_count == len(allowed_manifest_ids)
            and authoring_attempted_count == 0
            and save_or_delete_attempted_count == 0
            and cleanup_attempted_count == 0
            and canary_execution_attempted_count == 0
            and not missing
            and not unexpected
            else "failed"
        )
    return {
        "schema": CANARY_LIVE_PREFLIGHT_SUMMARY_SCHEMA,
        "status": status,
        "live_requested": live_requested,
        "durable_canary_preflight_requested_manifest_count": len(requested_manifests),
        "read_only_live_preflight_allowed_count": len(allowed_manifest_ids),
        "live_result_count": len(live_preflight_results),
        "passed_read_only_result_count": passed_read_only_result_count,
        "authoring_attempted_count": authoring_attempted_count,
        "save_or_delete_attempted_count": save_or_delete_attempted_count,
        "cleanup_attempted_count": cleanup_attempted_count,
        "canary_execution_attempted_count": canary_execution_attempted_count,
        "canary_execution_allowed_after_preflight_count": sum(
            1 for result in live_preflight_results if result.get("canary_execution_allowed_after_preflight")
        ),
        "missing_live_result_manifest_ids": missing,
        "unexpected_live_result_manifest_ids": unexpected,
        "read_only_only": True,
    }
