#!/usr/bin/env python
"""
Section 64 durable canary command allowlist contract.

Only the read-only canary asset-exists command is allowlisted. Authoring,
save, delete, rename, cleanup, and canary execution commands stay forbidden.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_COMMAND_ALLOWLIST_SCHEMA = "section_64_durable_canary_command_allowlist_contract_v1"
CANARY_COMMAND_ALLOWLIST_SUMMARY_SCHEMA = "section_64_durable_canary_command_allowlist_summary_v1"
READ_ONLY_ASSET_EXISTS_COMMAND = "unreal.EditorAssetLibrary.does_asset_exist"
FORBIDDEN_COMMANDS = (
    "create_blueprint",
    "compile_and_save_blueprint",
    "save_asset",
    "delete_asset",
    "rename_asset",
    "duplicate_asset",
    "replace_existing_asset",
)


def build_canary_command_allowlist_contract(
    requested: bool,
    executor_summary: Dict[str, Any],
) -> Dict[str, Any]:
    durable_gate = executor_summary.get("durable_gate_summary", {})
    gate_safe = bool(
        durable_gate.get("canary_live_preflight_read_only_allowed_count") == durable_gate.get(
            "durable_requested_manifest_count"
        )
        and durable_gate.get("canary_live_preflight_execution_allowed_count") == 0
        and durable_gate.get("canary_live_preflight_authoring_allowed_count") == 0
        and durable_gate.get("canary_live_preflight_save_or_delete_allowed_count") == 0
        and durable_gate.get("canary_recovery_cleanup_allowed_count") == 0
        and durable_gate.get("canary_recovery_delete_allowed_count") == 0
        and durable_gate.get("save_or_delete_commands_allowed_count") == 0
        and durable_gate.get("allowed_live_authoring_command_count") == 0
    )
    return {
        "id": "durable_canary_command_allowlist",
        "schema": CANARY_COMMAND_ALLOWLIST_SCHEMA,
        "requested": requested,
        "allowed_read_only_commands": [READ_ONLY_ASSET_EXISTS_COMMAND] if requested else [],
        "allowed_read_only_command_count": 1 if requested else 0,
        "forbidden_commands": list(FORBIDDEN_COMMANDS) if requested else [],
        "forbidden_command_count": len(FORBIDDEN_COMMANDS) if requested else 0,
        "executor_gate_matches_allowlist": bool(requested and gate_safe),
        "authoring_commands_allowed": False,
        "save_commands_allowed": False,
        "delete_commands_allowed": False,
        "rename_commands_allowed": False,
        "cleanup_commands_allowed": False,
        "canary_execution_allowed": False,
        "durable_executor_may_open_from_allowlist": False,
        "blocked_by": []
        if not requested
        else [
            "section_64_allowlist_is_read_only_preflight_only",
            "durable_canary_authoring_commands_not_allowlisted",
        ],
        "required_reinforcement": []
        if not requested
        else [
            "keep canary command allowlist limited to read-only asset existence checks",
            "add a separate explicit release before allowlisting create/save/delete/rename commands",
            "reject any manifest or executor policy that exposes save/delete/rename commands",
        ],
    }


def summarize_canary_command_allowlist_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("executor_gate_matches_allowlist")) == len(requested)
            and sum(1 for contract in requested if contract.get("authoring_commands_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_commands_allowed")) == 0
            and sum(1 for contract in requested if contract.get("delete_commands_allowed")) == 0
            and sum(1 for contract in requested if contract.get("rename_commands_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_commands_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_execution_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_from_allowlist")) == 0
            else "failed"
        )
    return {
        "schema": CANARY_COMMAND_ALLOWLIST_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_command_allowlist_count": len(requested),
        "allowed_read_only_command_count": sum(
            contract.get("allowed_read_only_command_count", 0) for contract in requested
        ),
        "forbidden_command_count": sum(contract.get("forbidden_command_count", 0) for contract in requested),
        "executor_gate_matches_allowlist_count": sum(
            1 for contract in requested if contract.get("executor_gate_matches_allowlist")
        ),
        "authoring_commands_allowed_count": sum(
            1 for contract in requested if contract.get("authoring_commands_allowed")
        ),
        "save_commands_allowed_count": sum(1 for contract in requested if contract.get("save_commands_allowed")),
        "delete_commands_allowed_count": sum(1 for contract in requested if contract.get("delete_commands_allowed")),
        "rename_commands_allowed_count": sum(1 for contract in requested if contract.get("rename_commands_allowed")),
        "cleanup_commands_allowed_count": sum(1 for contract in requested if contract.get("cleanup_commands_allowed")),
        "canary_execution_allowed_count": sum(1 for contract in requested if contract.get("canary_execution_allowed")),
        "durable_executor_may_open_from_allowlist_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_from_allowlist")
        ),
    }
