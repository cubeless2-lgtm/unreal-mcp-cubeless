#!/usr/bin/env python
"""
Section 85 durable canary authoring command contract.

This contract defines the scoped durable authoring command record required after
a future authoring-enable record is valid. It does not dispatch or execute live
commands, save assets, or allow delete/rename/cleanup actions.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_DURABLE_AUTHORING_COMMAND_SCHEMA = (
    "section_85_durable_canary_authoring_command_contract_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_RECORD_SCHEMA = (
    "section_85_durable_canary_authoring_command_record_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_SUMMARY_SCHEMA = (
    "section_85_durable_canary_authoring_command_summary_v1"
)
EXPECTED_COMMAND_SCOPE = "durable_canary_authoring_command_only"

ALLOWED_DURABLE_AUTHORING_COMMANDS = (
    "create_blueprint_asset",
    "compile_and_validate_blueprint",
    "write_executor_ownership_marker",
    "readback_executor_ownership_marker",
    "read_only_asset_exists_check",
)
FORBIDDEN_DURABLE_AUTHORING_COMMANDS = (
    "compile_and_validate_blueprint(save=true)",
    "compile_and_save_blueprint",
    "save_true",
    "save_asset",
    "delete_asset",
    "rename_asset",
    "duplicate_asset",
    "replace_existing_asset",
    "cleanup_asset",
    "general_durable_authoring",
    "live_command_dispatch",
    "live_command_execution",
)


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_durable_authoring_command_contract(
    requested: bool,
    authoring_enable_summary: Dict[str, Any],
    command_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    command_record = command_record or {}
    command_record_present = bool(command_record)
    authoring_enable_contract_ready = bool(
        requested
        and authoring_enable_summary.get("status") == "passed"
        and authoring_enable_summary.get("authoring_enable_contract_defined_count") == 1
        and authoring_enable_summary.get("authoring_enable_record_rejected_count") == 0
        and authoring_enable_summary.get("unsafe_authoring_enable_record_count") == 0
        and authoring_enable_summary.get("reported_forbidden_evidence_command_count") == 0
        and authoring_enable_summary.get("durable_authoring_enable_allowed_count") == 0
        and authoring_enable_summary.get("durable_authoring_enabled_count") == 0
        and authoring_enable_summary.get("durable_authoring_allowed_count") == 0
        and authoring_enable_summary.get("save_delete_rename_allowed_count") == 0
    )
    authoring_enable_inputs_satisfied = bool(
        authoring_enable_summary.get("authoring_enable_inputs_satisfied_count") == 1
    )
    authoring_enable_record_valid = bool(
        authoring_enable_summary.get("authoring_enable_record_valid_count") == 1
    )
    target_package_allowlist_reconfirmed = bool(
        authoring_enable_summary.get("target_package_allowlist_reconfirmed_count") == 1
    )
    overwrite_rename_decision_reconfirmed = bool(
        authoring_enable_summary.get("overwrite_rename_decision_reconfirmed_count") == 1
    )
    rollback_readiness_reconfirmed = bool(
        authoring_enable_summary.get("rollback_readiness_reconfirmed_count") == 1
    )
    ownership_marker_reconfirmed = bool(
        authoring_enable_summary.get("ownership_marker_reconfirmed_count") == 1
    )
    authoring_command_inputs_satisfied = bool(
        authoring_enable_inputs_satisfied
        and authoring_enable_record_valid
        and target_package_allowlist_reconfirmed
        and overwrite_rename_decision_reconfirmed
        and rollback_readiness_reconfirmed
        and ownership_marker_reconfirmed
    )
    record_schema_matches = bool(
        command_record_present
        and command_record.get("schema") == CANARY_DURABLE_AUTHORING_COMMAND_RECORD_SCHEMA
    )
    command_scope_matches = bool(
        command_record_present
        and command_record.get("command_scope") == EXPECTED_COMMAND_SCOPE
    )
    explicit_authoring_command_authorized = bool(
        command_record_present
        and command_record.get("explicit_durable_authoring_command_authorized") is True
    )
    no_save_delete_rename_acknowledged = bool(
        command_record_present
        and command_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    planned_commands = list(command_record.get("commands") or [])
    planned_authoring_command_count = len(planned_commands) if command_record_present else 0
    forbidden_commands = [
        command for command in planned_commands if command in FORBIDDEN_DURABLE_AUTHORING_COMMANDS
    ]
    unknown_commands = [
        command
        for command in planned_commands
        if command not in ALLOWED_DURABLE_AUTHORING_COMMANDS
        and command not in FORBIDDEN_DURABLE_AUTHORING_COMMANDS
    ]
    allowed_authoring_command_count = sum(
        1 for command in planned_commands if command in ALLOWED_DURABLE_AUTHORING_COMMANDS
    )
    unsafe_authoring_command_record_count = sum(
        int(_authorized(command_record.get(key)))
        for key in (
            "durable_authoring_enabled",
            "durable_authoring_allowed",
            "durable_authoring_command_allowed",
            "durable_authoring_command_dispatched",
            "durable_authoring_command_executed",
            "save_asset_authorized",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
            "live_command_dispatch_authorized",
            "live_command_execution_authorized",
        )
    )
    authoring_command_contract_defined = bool(requested and authoring_enable_contract_ready)
    authoring_command_record_valid = bool(
        authoring_command_contract_defined
        and authoring_command_inputs_satisfied
        and record_schema_matches
        and command_scope_matches
        and explicit_authoring_command_authorized
        and no_save_delete_rename_acknowledged
        and planned_authoring_command_count > 0
        and not forbidden_commands
        and not unknown_commands
        and unsafe_authoring_command_record_count == 0
    )
    missing = []
    if requested:
        if not authoring_enable_inputs_satisfied:
            missing.append("section_84_authoring_enable_inputs_satisfied")
        if not authoring_enable_record_valid:
            missing.append("section_84_authoring_enable_record_valid")
        if not target_package_allowlist_reconfirmed:
            missing.append("section_84_target_package_allowlist_reconfirmed")
        if not overwrite_rename_decision_reconfirmed:
            missing.append("section_84_overwrite_rename_decision_reconfirmed")
        if not rollback_readiness_reconfirmed:
            missing.append("section_84_rollback_readiness_reconfirmed")
        if not ownership_marker_reconfirmed:
            missing.append("section_84_ownership_marker_reconfirmed")
        if not command_record_present:
            missing.append("durable_authoring_command_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_record_schema")
        if not command_scope_matches:
            missing.append("durable_canary_authoring_command_only_scope")
        if not explicit_authoring_command_authorized:
            missing.append("explicit_durable_authoring_command_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if planned_authoring_command_count == 0:
            missing.append("durable_authoring_commands_present")
        missing.append("separate_durable_authoring_command_dispatch_contract")
    authoring_command_record_rejected = bool(
        command_record_present and not authoring_command_record_valid
    )
    return {
        "id": "durable_canary_authoring_command",
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_SCHEMA,
        "requested": requested,
        "authoring_command_contract_defined": authoring_command_contract_defined,
        "required_authoring_command_record_schema": (
            CANARY_DURABLE_AUTHORING_COMMAND_RECORD_SCHEMA if requested else ""
        ),
        "expected_command_scope": EXPECTED_COMMAND_SCOPE if requested else "",
        "allowed_durable_authoring_commands": (
            list(ALLOWED_DURABLE_AUTHORING_COMMANDS) if requested else []
        ),
        "forbidden_durable_authoring_commands": (
            list(FORBIDDEN_DURABLE_AUTHORING_COMMANDS) if requested else []
        ),
        "authoring_enable_contract_ready": authoring_enable_contract_ready,
        "authoring_enable_inputs_satisfied": authoring_enable_inputs_satisfied,
        "authoring_enable_record_valid": authoring_enable_record_valid,
        "target_package_allowlist_reconfirmed": target_package_allowlist_reconfirmed,
        "overwrite_rename_decision_reconfirmed": overwrite_rename_decision_reconfirmed,
        "rollback_readiness_reconfirmed": rollback_readiness_reconfirmed,
        "ownership_marker_reconfirmed": ownership_marker_reconfirmed,
        "authoring_command_inputs_satisfied": authoring_command_inputs_satisfied,
        "authoring_command_record_present": command_record_present,
        "record_schema_matches": record_schema_matches,
        "command_scope_matches": command_scope_matches,
        "explicit_authoring_command_authorized": explicit_authoring_command_authorized,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "planned_authoring_command_count": planned_authoring_command_count,
        "allowed_authoring_command_count": allowed_authoring_command_count,
        "forbidden_authoring_command_count": len(forbidden_commands),
        "unknown_authoring_command_count": len(unknown_commands),
        "authoring_command_record_valid": authoring_command_record_valid,
        "authoring_command_record_rejected": authoring_command_record_rejected,
        "unsafe_authoring_command_record_count": unsafe_authoring_command_record_count,
        "missing_authoring_command_prerequisites": missing,
        "missing_authoring_command_prerequisite_count": len(missing),
        "durable_authoring_command_allowed": False,
        "durable_authoring_command_dispatched": False,
        "durable_authoring_command_executed": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_command_execution_allowed": False,
        "live_command_executed": False,
        "reported_allowed_evidence_command_count": authoring_enable_summary.get(
            "reported_allowed_evidence_command_count",
            0,
        ),
        "reported_forbidden_evidence_command_count": authoring_enable_summary.get(
            "reported_forbidden_evidence_command_count",
            0,
        ),
        "blocked_by": []
        if not requested
        else [
            "section_85_authoring_command_contract_does_not_dispatch_or_execute",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped durable authoring command only after Section 84 authoring enable is valid",
            "reject command records containing save, delete, rename, cleanup, live dispatch, or live execution commands",
            "keep durable command dispatch and execution behind separate contracts after command record validation",
        ],
    }


def summarize_canary_durable_authoring_commands(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1 for contract in requested if contract.get("authoring_command_record_rejected")
    )
    unsafe_count = sum(
        contract.get("unsafe_authoring_command_record_count", 0) for contract in requested
    )
    forbidden_command_count = sum(
        contract.get("forbidden_authoring_command_count", 0) for contract in requested
    )
    unknown_command_count = sum(
        contract.get("unknown_authoring_command_count", 0) for contract in requested
    )
    forbidden_evidence_count = sum(
        contract.get("reported_forbidden_evidence_command_count", 0) for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("authoring_command_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_command_count == 0
            and unknown_command_count == 0
            and forbidden_evidence_count == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_command_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_command_dispatched")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_command_executed")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_enabled")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_delete_rename_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_dispatch_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_plan_emitted")) == 0
            and sum(1 for contract in requested if contract.get("live_command_execution_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_executed")) == 0
            else "failed"
        )
    return {
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_authoring_command_count": len(requested),
        "authoring_command_contract_defined_count": sum(
            1 for contract in requested if contract.get("authoring_command_contract_defined")
        ),
        "authoring_enable_contract_ready_count": sum(
            1 for contract in requested if contract.get("authoring_enable_contract_ready")
        ),
        "authoring_enable_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("authoring_enable_inputs_satisfied")
        ),
        "authoring_enable_record_valid_count": sum(
            1 for contract in requested if contract.get("authoring_enable_record_valid")
        ),
        "target_package_allowlist_reconfirmed_count": sum(
            1 for contract in requested if contract.get("target_package_allowlist_reconfirmed")
        ),
        "overwrite_rename_decision_reconfirmed_count": sum(
            1 for contract in requested if contract.get("overwrite_rename_decision_reconfirmed")
        ),
        "rollback_readiness_reconfirmed_count": sum(
            1 for contract in requested if contract.get("rollback_readiness_reconfirmed")
        ),
        "ownership_marker_reconfirmed_count": sum(
            1 for contract in requested if contract.get("ownership_marker_reconfirmed")
        ),
        "authoring_command_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("authoring_command_inputs_satisfied")
        ),
        "authoring_command_record_present_count": sum(
            1 for contract in requested if contract.get("authoring_command_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "command_scope_matches_count": sum(
            1 for contract in requested if contract.get("command_scope_matches")
        ),
        "explicit_authoring_command_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_authoring_command_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "planned_authoring_command_count": sum(
            contract.get("planned_authoring_command_count", 0) for contract in requested
        ),
        "allowed_authoring_command_count": sum(
            contract.get("allowed_authoring_command_count", 0) for contract in requested
        ),
        "forbidden_authoring_command_count": forbidden_command_count,
        "unknown_authoring_command_count": unknown_command_count,
        "authoring_command_record_valid_count": sum(
            1 for contract in requested if contract.get("authoring_command_record_valid")
        ),
        "authoring_command_record_rejected_count": rejected_count,
        "unsafe_authoring_command_record_count": unsafe_count,
        "missing_authoring_command_prerequisite_count": sum(
            contract.get("missing_authoring_command_prerequisite_count", 0)
            for contract in requested
        ),
        "durable_authoring_command_allowed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_command_allowed")
        ),
        "durable_authoring_command_dispatched_count": sum(
            1 for contract in requested if contract.get("durable_authoring_command_dispatched")
        ),
        "durable_authoring_command_executed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_command_executed")
        ),
        "durable_authoring_enabled_count": sum(
            1 for contract in requested if contract.get("durable_authoring_enabled")
        ),
        "durable_authoring_allowed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_allowed")
        ),
        "save_delete_rename_allowed_count": sum(
            1 for contract in requested if contract.get("save_delete_rename_allowed")
        ),
        "cleanup_allowed_count": sum(
            1 for contract in requested if contract.get("cleanup_allowed")
        ),
        "live_command_dispatch_allowed_count": sum(
            1 for contract in requested if contract.get("live_command_dispatch_allowed")
        ),
        "live_command_plan_emitted_count": sum(
            1 for contract in requested if contract.get("live_command_plan_emitted")
        ),
        "live_command_execution_allowed_count": sum(
            1 for contract in requested if contract.get("live_command_execution_allowed")
        ),
        "live_command_executed_count": sum(
            1 for contract in requested if contract.get("live_command_executed")
        ),
        "reported_allowed_evidence_command_count": sum(
            contract.get("reported_allowed_evidence_command_count", 0) for contract in requested
        ),
        "reported_forbidden_evidence_command_count": forbidden_evidence_count,
    }
