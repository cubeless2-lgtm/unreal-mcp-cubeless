#!/usr/bin/env python
"""
Section 129 durable executor authoring command-after-enable contract.

This contract validates a future authoring-command-only record after the
durable executor authoring enable-after-open record is valid. It does not
dispatch or execute live commands, modify assets, dirty packages, save,
delete/rename, cleanup, change code, or probe live bridges.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_COMMAND_AFTER_ENABLE_SCHEMA = (
    "section_129_durable_executor_authoring_command_after_enable_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_AFTER_ENABLE_RECORD_SCHEMA = (
    "section_129_durable_executor_authoring_command_after_enable_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_COMMAND_AFTER_ENABLE_SUMMARY_SCHEMA = (
    "section_129_durable_executor_authoring_command_after_enable_summary_v1"
)
EXPECTED_COMMAND_SCOPE = "durable_executor_authoring_command_after_enable_only"

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

OUTPUT_ACTION_KEYS = (
    "durable_authoring_command_contract_started",
    "durable_authoring_command_contract_accepted",
    "durable_authoring_command_allowed",
    "durable_authoring_command_dispatched",
    "durable_authoring_command_executed",
    "durable_authoring_enable_started",
    "durable_authoring_enable_accepted",
    "durable_authoring_enable_allowed",
    "durable_authoring_enabled",
    "durable_authoring_allowed",
    "durable_executor_open_performed",
    "durable_executor_opened",
    "code_change_performed",
    "executor_code_modified",
    "unreal_asset_modified",
    "live_bridge_probe_started",
    "asset_write_performed",
    "package_dirty_marked",
    "save_delete_rename_allowed",
    "cleanup_allowed",
    "live_command_dispatched",
    "live_command_executed",
)
UNSAFE_COMMAND_RECORD_ACTION_KEYS = (
    "durable_authoring_command_contract_started",
    "durable_authoring_command_contract_accepted",
    "durable_authoring_command_allowed",
    "durable_authoring_command_dispatched",
    "durable_authoring_command_executed",
    "durable_authoring_enable_started",
    "durable_authoring_enable_accepted",
    "durable_authoring_enable_allowed",
    "durable_authoring_enabled",
    "durable_authoring_allowed",
    "durable_executor_open_performed",
    "durable_executor_opened",
    "code_change_performed",
    "executor_code_modified",
    "unreal_asset_modified",
    "live_bridge_probe_started",
    "asset_write_performed",
    "package_dirty_marked",
    "save_asset_executed",
    "delete_asset_authorized",
    "rename_asset_authorized",
    "cleanup_authorized",
    "live_command_dispatched",
    "live_command_executed",
)
PREVIOUS_ZERO_COUNT_KEYS = (
    "durable_authoring_enable_started_count",
    "durable_authoring_enable_accepted_count",
    "durable_authoring_enable_allowed_count",
    "durable_authoring_enabled_count",
    "durable_authoring_allowed_count",
    "durable_authoring_command_contract_started_count",
    "durable_executor_open_contract_started_count",
    "durable_executor_open_contract_accepted_count",
    "durable_executor_open_performed_count",
    "durable_executor_activated_count",
    "durable_executor_opened_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
    "code_change_performed_count",
    "executor_code_modified_count",
    "unreal_asset_modified_count",
    "live_bridge_probe_started_count",
    "save_delete_rename_allowed_count",
    "cleanup_allowed_count",
    "live_command_dispatched_count",
    "live_command_executed_count",
)


def _attempted(value: Any) -> bool:
    return value is True or value == 1


def _sum_truthy(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(contract.get(key, 0) for contract in contracts)


def build_durable_executor_authoring_command_after_enable_contract(
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
        and authoring_enable_summary.get(
            "reported_forbidden_authoring_enable_count"
        )
        == 0
        and all(
            authoring_enable_summary.get(key) == 0
            for key in PREVIOUS_ZERO_COUNT_KEYS
        )
    )
    authoring_enable_inputs_satisfied = bool(
        authoring_enable_summary.get("authoring_enable_inputs_satisfied_count") == 1
    )
    authoring_enable_record_valid = bool(
        authoring_enable_summary.get("authoring_enable_record_valid_count") == 1
    )
    allowed_authoring_enable_observed = bool(
        authoring_enable_summary.get("allowed_authoring_enable_observed_count") == 1
    )
    no_forbidden_authoring_enable_claims = bool(
        authoring_enable_summary.get("no_forbidden_authoring_enable_claims_count") == 1
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
        and allowed_authoring_enable_observed
        and no_forbidden_authoring_enable_claims
        and target_package_allowlist_reconfirmed
        and overwrite_rename_decision_reconfirmed
        and rollback_readiness_reconfirmed
        and ownership_marker_reconfirmed
    )
    record_schema_matches = bool(
        command_record_present
        and command_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_COMMAND_AFTER_ENABLE_RECORD_SCHEMA
    )
    command_scope_matches = bool(
        command_record_present
        and command_record.get("command_scope") == EXPECTED_COMMAND_SCOPE
    )
    explicit_authoring_command_authorized = bool(
        command_record_present
        and command_record.get("explicit_durable_authoring_command_authorized") is True
    )
    command_status_passed = bool(
        command_record_present and command_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        command_record_present
        and command_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        command_record_present
        and command_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    planned_commands = list(command_record.get("commands") or [])
    planned_authoring_command_count = len(planned_commands) if command_record_present else 0
    forbidden_commands = [
        command
        for command in planned_commands
        if command in FORBIDDEN_DURABLE_AUTHORING_COMMANDS
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
        int(_attempted(command_record.get(key))) for key in UNSAFE_COMMAND_RECORD_ACTION_KEYS
    )
    authoring_command_contract_defined = bool(
        requested and authoring_enable_contract_ready
    )
    authoring_command_record_valid = bool(
        authoring_command_contract_defined
        and authoring_command_inputs_satisfied
        and record_schema_matches
        and command_scope_matches
        and explicit_authoring_command_authorized
        and command_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and planned_authoring_command_count > 0
        and allowed_authoring_command_count == planned_authoring_command_count
        and not forbidden_commands
        and not unknown_commands
        and unsafe_authoring_command_record_count == 0
    )
    missing: list[str] = []
    if requested:
        if not authoring_enable_inputs_satisfied:
            missing.append("section_128_authoring_enable_inputs_satisfied")
        if not authoring_enable_record_valid:
            missing.append("section_128_authoring_enable_record_valid")
        if not allowed_authoring_enable_observed:
            missing.append("section_128_allowed_authoring_enable_observed")
        if not no_forbidden_authoring_enable_claims:
            missing.append("section_128_no_forbidden_authoring_enable_claims")
        if not target_package_allowlist_reconfirmed:
            missing.append("section_128_target_package_allowlist_reconfirmed")
        if not overwrite_rename_decision_reconfirmed:
            missing.append("section_128_overwrite_rename_decision_reconfirmed")
        if not rollback_readiness_reconfirmed:
            missing.append("section_128_rollback_readiness_reconfirmed")
        if not ownership_marker_reconfirmed:
            missing.append("section_128_ownership_marker_reconfirmed")
        if not command_record_present:
            missing.append("durable_authoring_command_after_enable_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_after_enable_record_schema")
        if not command_scope_matches:
            missing.append("durable_executor_authoring_command_after_enable_only_scope")
        if not explicit_authoring_command_authorized:
            missing.append("explicit_durable_authoring_command_authorization")
        if not command_status_passed:
            missing.append("durable_authoring_command_after_enable_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if planned_authoring_command_count == 0:
            missing.append("durable_authoring_commands_present")
        missing.append("separate_durable_authoring_command_dispatch_contract")
    authoring_command_record_rejected = bool(
        command_record_present and not authoring_command_record_valid
    )
    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_command_after_enable",
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_AFTER_ENABLE_SCHEMA,
        "requested": requested,
        "authoring_command_contract_defined": authoring_command_contract_defined,
        "required_authoring_command_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_COMMAND_AFTER_ENABLE_RECORD_SCHEMA
            if requested
            else ""
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
        "allowed_authoring_enable_observed": allowed_authoring_enable_observed,
        "no_forbidden_authoring_enable_claims": (
            no_forbidden_authoring_enable_claims
        ),
        "target_package_allowlist_reconfirmed": (
            target_package_allowlist_reconfirmed
        ),
        "overwrite_rename_decision_reconfirmed": (
            overwrite_rename_decision_reconfirmed
        ),
        "rollback_readiness_reconfirmed": rollback_readiness_reconfirmed,
        "ownership_marker_reconfirmed": ownership_marker_reconfirmed,
        "authoring_command_inputs_satisfied": authoring_command_inputs_satisfied,
        "authoring_command_record_present": command_record_present,
        "record_schema_matches": record_schema_matches,
        "command_scope_matches": command_scope_matches,
        "explicit_authoring_command_authorized": (
            explicit_authoring_command_authorized
        ),
        "command_status_passed": command_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "planned_authoring_command_count": planned_authoring_command_count,
        "allowed_authoring_command_count": allowed_authoring_command_count,
        "forbidden_authoring_command_count": len(forbidden_commands),
        "unknown_authoring_command_count": len(unknown_commands),
        "authoring_command_record_valid": authoring_command_record_valid,
        "authoring_command_record_rejected": authoring_command_record_rejected,
        "unsafe_authoring_command_record_count": unsafe_authoring_command_record_count,
        "missing_authoring_command_prerequisites": missing,
        "missing_authoring_command_prerequisite_count": len(missing),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    return contract


def summarize_durable_executor_authoring_commands_after_enable(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(requested, "authoring_command_record_rejected")
    unsafe_count = _sum_count(requested, "unsafe_authoring_command_record_count")
    forbidden_command_count = _sum_count(requested, "forbidden_authoring_command_count")
    unknown_command_count = _sum_count(requested, "unknown_authoring_command_count")
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "authoring_command_contract_defined")
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_command_count == 0
            and unknown_command_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_COMMAND_AFTER_ENABLE_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_command_after_enable_count": len(
            requested
        ),
        "authoring_command_contract_defined_count": _sum_truthy(
            requested, "authoring_command_contract_defined"
        ),
        "authoring_enable_contract_ready_count": _sum_truthy(
            requested, "authoring_enable_contract_ready"
        ),
        "authoring_enable_inputs_satisfied_count": _sum_truthy(
            requested, "authoring_enable_inputs_satisfied"
        ),
        "authoring_enable_record_valid_count": _sum_truthy(
            requested, "authoring_enable_record_valid"
        ),
        "allowed_authoring_enable_observed_count": _sum_truthy(
            requested, "allowed_authoring_enable_observed"
        ),
        "no_forbidden_authoring_enable_claims_count": _sum_truthy(
            requested, "no_forbidden_authoring_enable_claims"
        ),
        "target_package_allowlist_reconfirmed_count": _sum_truthy(
            requested, "target_package_allowlist_reconfirmed"
        ),
        "overwrite_rename_decision_reconfirmed_count": _sum_truthy(
            requested, "overwrite_rename_decision_reconfirmed"
        ),
        "rollback_readiness_reconfirmed_count": _sum_truthy(
            requested, "rollback_readiness_reconfirmed"
        ),
        "ownership_marker_reconfirmed_count": _sum_truthy(
            requested, "ownership_marker_reconfirmed"
        ),
        "authoring_command_inputs_satisfied_count": _sum_truthy(
            requested, "authoring_command_inputs_satisfied"
        ),
        "authoring_command_record_present_count": _sum_truthy(
            requested, "authoring_command_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "command_scope_matches_count": _sum_truthy(
            requested, "command_scope_matches"
        ),
        "explicit_authoring_command_authorized_count": _sum_truthy(
            requested, "explicit_authoring_command_authorized"
        ),
        "command_status_passed_count": _sum_truthy(
            requested, "command_status_passed"
        ),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "planned_authoring_command_count": _sum_count(
            requested, "planned_authoring_command_count"
        ),
        "allowed_authoring_command_count": _sum_count(
            requested, "allowed_authoring_command_count"
        ),
        "forbidden_authoring_command_count": forbidden_command_count,
        "unknown_authoring_command_count": unknown_command_count,
        "authoring_command_record_valid_count": _sum_truthy(
            requested, "authoring_command_record_valid"
        ),
        "authoring_command_record_rejected_count": rejected_count,
        "unsafe_authoring_command_record_count": unsafe_count,
        "missing_authoring_command_prerequisite_count": _sum_count(
            requested, "missing_authoring_command_prerequisite_count"
        ),
    }
    summary.update({f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS})
    return summary
