#!/usr/bin/env python
"""
Section 51 durable Blueprint authoring enable contract.

This contract does not enable durable Blueprint saving. It isolates the gates
that must be satisfied before a future durable executor may even be considered.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Sequence


ENABLE_CONTRACT_SCHEMA = "section_51_durable_authoring_enable_contract_v1"
ENABLE_CONTRACT_SUMMARY_SCHEMA = "section_51_durable_authoring_enable_contract_summary_v1"

TARGET_PACKAGE_ALLOWLIST_GATE = "target_package_allowlist"
OVERWRITE_RENAME_DECISION_GATE = "overwrite_rename_decision"
ROLLBACK_READINESS_GATE = "rollback_readiness"
EXECUTOR_CREATED_OWNERSHIP_MARKER_GATE = "executor_created_ownership_marker"

REQUIRED_GATE_IDS: Sequence[str] = (
    TARGET_PACKAGE_ALLOWLIST_GATE,
    OVERWRITE_RENAME_DECISION_GATE,
    ROLLBACK_READINESS_GATE,
    EXECUTOR_CREATED_OWNERSHIP_MARKER_GATE,
)

FORBIDDEN_DURABLE_COMMANDS: Sequence[str] = (
    "compile_and_validate_blueprint(save=true)",
    "save_asset",
    "delete_asset",
    "rename_asset",
)


def _gate(
    gate_id: str,
    label: str,
    requested: bool,
    passed: bool,
    evidence: Dict[str, Any],
    required_reinforcement: Iterable[str],
) -> Dict[str, Any]:
    return {
        "id": gate_id,
        "label": label,
        "required": True,
        "requested": requested,
        "passed": bool(requested and passed),
        "status": "passed" if requested and passed else ("failed" if requested else "not_requested"),
        "evidence": evidence,
        "required_reinforcement": [] if requested and passed else list(required_reinforcement),
    }


def build_enable_contract(
    requested: bool,
    target_package_path: str,
    target_asset_path: str,
    package_path_allowed: bool,
    overwrite_rename_decision_contract: Dict[str, Any],
    rollback_policy_contract: Dict[str, Any],
    ownership_marker_policy_ready: bool = False,
) -> Dict[str, Any]:
    decision_present = bool(overwrite_rename_decision_contract.get("decision_present"))
    decision_conflict = bool(overwrite_rename_decision_contract.get("decision_conflict"))
    decision = str(overwrite_rename_decision_contract.get("decision", "missing"))
    rollback_ready = bool(rollback_policy_contract.get("rollback_policy_ready"))
    protects_preexisting_assets = bool(rollback_policy_contract.get("protects_preexisting_assets"))

    gates = [
        _gate(
            TARGET_PACKAGE_ALLOWLIST_GATE,
            "Target package path is allowlisted for future durable authoring",
            requested,
            bool(target_package_path and package_path_allowed),
            {
                "target_package_path": target_package_path,
                "target_asset_path": target_asset_path,
                "package_path_allowed": package_path_allowed,
            },
            [
                "choose a durable target package under the Section 51 allowlist",
                "prove the package root is reserved for durable MCP-created Blueprints",
            ],
        ),
        _gate(
            OVERWRITE_RENAME_DECISION_GATE,
            "Exactly one overwrite-or-rename decision is present and conflict-free",
            requested,
            decision_present and not decision_conflict,
            {
                "decision": decision,
                "decision_present": decision_present,
                "decision_conflict": decision_conflict,
                "overwrite_requested": bool(overwrite_rename_decision_contract.get("overwrite_requested")),
                "rename_if_exists_requested": bool(overwrite_rename_decision_contract.get("rename_if_exists_requested")),
            },
            [
                "choose exactly one durable conflict policy: overwrite_existing or rename_if_exists",
                "reject requests that ask for both overwrite and rename-if-exists",
            ],
        ),
        _gate(
            ROLLBACK_READINESS_GATE,
            "Rollback policy is ready and protects preexisting assets",
            requested,
            rollback_ready and protects_preexisting_assets,
            {
                "rollback_policy_ready": rollback_ready,
                "rollback_allowed": bool(rollback_policy_contract.get("rollback_allowed")),
                "protects_preexisting_assets": protects_preexisting_assets,
                "delete_existing_asset_allowed": bool(rollback_policy_contract.get("delete_existing_asset_allowed")),
                "overwrite_existing_asset_allowed": bool(rollback_policy_contract.get("overwrite_existing_asset_allowed")),
            },
            [
                "define rollback behavior for create, compile, save, and cancellation failures",
                "prove rollback never deletes or overwrites preexisting assets without policy",
            ],
        ),
        _gate(
            EXECUTOR_CREATED_OWNERSHIP_MARKER_GATE,
            "Executor-created asset ownership marker policy is ready",
            requested,
            ownership_marker_policy_ready,
            {
                "ownership_marker_policy_ready": ownership_marker_policy_ready,
                "requires_executor_created_asset_marker": bool(
                    rollback_policy_contract.get("requires_executor_created_asset_marker")
                ),
                "allowed_delete_scope": rollback_policy_contract.get("allowed_delete_scope", ""),
            },
            [
                "record an executor-created asset ownership marker before any durable save",
                "allow delete/rollback only for assets with the executor-created ownership marker",
            ],
        ),
    ]

    failed_gate_ids = [gate["id"] for gate in gates if gate["requested"] and not gate["passed"]]
    enable_contract_satisfied = bool(requested and not failed_gate_ids)
    section_51_blocker = "section_51_does_not_enable_live_durable_authoring"
    blocked_by = list(failed_gate_ids)
    if requested:
        blocked_by.append(section_51_blocker)

    return {
        "id": "durable_authoring_enable_contract",
        "schema": ENABLE_CONTRACT_SCHEMA,
        "requested": requested,
        "contract_scope": "offline_enable_conditions_only",
        "target_asset_path": target_asset_path,
        "required_gate_ids": list(REQUIRED_GATE_IDS),
        "gates": gates,
        "failed_required_gate_ids": failed_gate_ids,
        "enable_contract_satisfied": enable_contract_satisfied,
        "durable_executor_may_open": False,
        "durable_authoring_allowed": False,
        "save_true_allowed": False,
        "save_asset_allowed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        "forbidden_commands": list(FORBIDDEN_DURABLE_COMMANDS),
        "blocked_by": blocked_by,
        "required_reinforcement": []
        if not requested
        else [
            "satisfy every Section 51 durable authoring enable gate",
            "keep save=true, save_asset, delete_asset, and rename_asset forbidden until a later explicit durable release",
            "prove the future durable executor with offline tests before any live durable authoring",
        ],
    }


def summarize_enable_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested_contracts = [contract for contract in contracts if contract.get("requested")]

    def gate_passed_count(gate_id: str) -> int:
        count = 0
        for contract in requested_contracts:
            for gate in contract.get("gates", []):
                if gate.get("id") == gate_id and gate.get("passed"):
                    count += 1
        return count

    durable_executor_may_open_count = sum(1 for contract in requested_contracts if contract.get("durable_executor_may_open"))
    durable_authoring_allowed_count = sum(1 for contract in requested_contracts if contract.get("durable_authoring_allowed"))
    forbidden_command_allowed_count = sum(
        1
        for contract in requested_contracts
        if contract.get("save_true_allowed")
        or contract.get("save_asset_allowed")
        or contract.get("delete_asset_allowed")
        or contract.get("rename_asset_allowed")
    )
    status = "not_requested"
    if requested_contracts:
        status = (
            "passed"
            if durable_executor_may_open_count == 0
            and durable_authoring_allowed_count == 0
            and forbidden_command_allowed_count == 0
            else "failed"
        )

    return {
        "schema": ENABLE_CONTRACT_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_manifest_count": len(requested_contracts),
        "enable_contract_satisfied_count": sum(
            1 for contract in requested_contracts if contract.get("enable_contract_satisfied")
        ),
        "durable_executor_may_open_count": durable_executor_may_open_count,
        "durable_authoring_allowed_count": durable_authoring_allowed_count,
        "forbidden_command_allowed_count": forbidden_command_allowed_count,
        "failed_required_gate_count": sum(
            len(contract.get("failed_required_gate_ids", [])) for contract in requested_contracts
        ),
        "target_package_allowlist_passed_count": gate_passed_count(TARGET_PACKAGE_ALLOWLIST_GATE),
        "overwrite_rename_decision_passed_count": gate_passed_count(OVERWRITE_RENAME_DECISION_GATE),
        "rollback_readiness_passed_count": gate_passed_count(ROLLBACK_READINESS_GATE),
        "ownership_marker_passed_count": gate_passed_count(EXECUTOR_CREATED_OWNERSHIP_MARKER_GATE),
    }
