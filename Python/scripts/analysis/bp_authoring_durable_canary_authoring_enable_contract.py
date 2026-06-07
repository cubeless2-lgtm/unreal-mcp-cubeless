#!/usr/bin/env python
"""
Section 84 durable canary authoring enable contract.

This contract defines the operator authoring-enable record required after a
future durable executor open record is valid. It does not enable durable
authoring, save assets, or execute live commands.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_DURABLE_AUTHORING_ENABLE_SCHEMA = (
    "section_84_durable_canary_authoring_enable_contract_v1"
)
CANARY_DURABLE_AUTHORING_ENABLE_RECORD_SCHEMA = (
    "section_84_durable_canary_authoring_enable_record_v1"
)
CANARY_DURABLE_AUTHORING_ENABLE_SUMMARY_SCHEMA = (
    "section_84_durable_canary_authoring_enable_summary_v1"
)
EXPECTED_ENABLE_SCOPE = "durable_canary_authoring_enable_only"


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_durable_authoring_enable_contract(
    requested: bool,
    open_summary: Dict[str, Any],
    enable_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    enable_record = enable_record or {}
    enable_record_present = bool(enable_record)
    executor_open_contract_ready = bool(
        requested
        and open_summary.get("status") == "passed"
        and open_summary.get("open_contract_defined_count") == 1
        and open_summary.get("open_record_rejected_count") == 0
        and open_summary.get("unsafe_open_record_count") == 0
        and open_summary.get("reported_forbidden_evidence_command_count") == 0
        and open_summary.get("durable_executor_open_allowed_count") == 0
        and open_summary.get("durable_executor_opened_count") == 0
        and open_summary.get("durable_authoring_allowed_count") == 0
        and open_summary.get("save_delete_rename_allowed_count") == 0
    )
    open_inputs_satisfied = bool(open_summary.get("open_inputs_satisfied_count") == 1)
    open_record_valid = bool(open_summary.get("open_record_valid_count") == 1)
    authoring_enable_inputs_satisfied = bool(open_inputs_satisfied and open_record_valid)
    record_schema_matches = bool(
        enable_record_present
        and enable_record.get("schema") == CANARY_DURABLE_AUTHORING_ENABLE_RECORD_SCHEMA
    )
    enable_scope_matches = bool(
        enable_record_present
        and enable_record.get("enable_scope") == EXPECTED_ENABLE_SCOPE
    )
    explicit_authoring_enable_authorized = bool(
        enable_record_present
        and enable_record.get("explicit_durable_authoring_enable_authorized") is True
    )
    no_save_delete_rename_acknowledged = bool(
        enable_record_present
        and enable_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    target_package_allowlist_reconfirmed = bool(
        enable_record_present
        and enable_record.get("target_package_allowlist_reconfirmed") is True
    )
    overwrite_rename_decision_reconfirmed = bool(
        enable_record_present
        and enable_record.get("overwrite_rename_decision_reconfirmed") is True
    )
    rollback_readiness_reconfirmed = bool(
        enable_record_present
        and enable_record.get("rollback_readiness_reconfirmed") is True
    )
    ownership_marker_reconfirmed = bool(
        enable_record_present
        and enable_record.get("executor_created_ownership_marker_reconfirmed") is True
    )
    unsafe_authoring_enable_record_count = sum(
        int(_authorized(enable_record.get(key)))
        for key in (
            "durable_authoring_enabled",
            "durable_authoring_allowed",
            "durable_executor_activation_authorized",
            "durable_executor_open_authorized",
            "durable_executor_open_performed",
            "durable_executor_opened",
            "durable_authoring_command_authorized",
            "save_asset_authorized",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
            "live_command_dispatch_authorized",
            "live_command_execution_authorized",
        )
    )
    authoring_enable_contract_defined = bool(requested and executor_open_contract_ready)
    authoring_enable_record_valid = bool(
        authoring_enable_contract_defined
        and authoring_enable_inputs_satisfied
        and record_schema_matches
        and enable_scope_matches
        and explicit_authoring_enable_authorized
        and no_save_delete_rename_acknowledged
        and target_package_allowlist_reconfirmed
        and overwrite_rename_decision_reconfirmed
        and rollback_readiness_reconfirmed
        and ownership_marker_reconfirmed
        and unsafe_authoring_enable_record_count == 0
    )
    missing = []
    if requested:
        if not open_inputs_satisfied:
            missing.append("section_83_open_inputs_satisfied")
        if not open_record_valid:
            missing.append("section_83_open_record_valid")
        if not enable_record_present:
            missing.append("durable_authoring_enable_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_enable_record_schema")
        if not enable_scope_matches:
            missing.append("durable_canary_authoring_enable_only_scope")
        if not explicit_authoring_enable_authorized:
            missing.append("explicit_durable_authoring_enable_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not target_package_allowlist_reconfirmed:
            missing.append("section_51_target_package_allowlist_reconfirmed")
        if not overwrite_rename_decision_reconfirmed:
            missing.append("section_51_overwrite_rename_decision_reconfirmed")
        if not rollback_readiness_reconfirmed:
            missing.append("section_51_rollback_readiness_reconfirmed")
        if not ownership_marker_reconfirmed:
            missing.append("section_51_executor_created_ownership_marker_reconfirmed")
        missing.append("separate_durable_authoring_command_contract")
    authoring_enable_record_rejected = bool(
        enable_record_present and not authoring_enable_record_valid
    )
    return {
        "id": "durable_canary_authoring_enable",
        "schema": CANARY_DURABLE_AUTHORING_ENABLE_SCHEMA,
        "requested": requested,
        "authoring_enable_contract_defined": authoring_enable_contract_defined,
        "required_authoring_enable_record_schema": (
            CANARY_DURABLE_AUTHORING_ENABLE_RECORD_SCHEMA if requested else ""
        ),
        "expected_enable_scope": EXPECTED_ENABLE_SCOPE if requested else "",
        "executor_open_contract_ready": executor_open_contract_ready,
        "open_inputs_satisfied": open_inputs_satisfied,
        "open_record_valid": open_record_valid,
        "authoring_enable_inputs_satisfied": authoring_enable_inputs_satisfied,
        "authoring_enable_record_present": enable_record_present,
        "record_schema_matches": record_schema_matches,
        "enable_scope_matches": enable_scope_matches,
        "explicit_authoring_enable_authorized": explicit_authoring_enable_authorized,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "target_package_allowlist_reconfirmed": target_package_allowlist_reconfirmed,
        "overwrite_rename_decision_reconfirmed": overwrite_rename_decision_reconfirmed,
        "rollback_readiness_reconfirmed": rollback_readiness_reconfirmed,
        "ownership_marker_reconfirmed": ownership_marker_reconfirmed,
        "authoring_enable_record_valid": authoring_enable_record_valid,
        "authoring_enable_record_rejected": authoring_enable_record_rejected,
        "unsafe_authoring_enable_record_count": unsafe_authoring_enable_record_count,
        "missing_authoring_enable_prerequisites": missing,
        "missing_authoring_enable_prerequisite_count": len(missing),
        "durable_authoring_enable_allowed": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_command_execution_allowed": False,
        "live_command_executed": False,
        "reported_allowed_evidence_command_count": open_summary.get(
            "reported_allowed_evidence_command_count",
            0,
        ),
        "reported_forbidden_evidence_command_count": open_summary.get(
            "reported_forbidden_evidence_command_count",
            0,
        ),
        "blocked_by": []
        if not requested
        else [
            "section_84_authoring_enable_contract_does_not_enable_durable_authoring",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped durable authoring enable authorization only after Section 83 executor open is valid",
            "reconfirm the Section 51 target allowlist, overwrite/rename decision, rollback readiness, and ownership marker gates",
            "keep durable authoring commands behind a separate contract after authoring enable record validation",
        ],
    }


def summarize_canary_durable_authoring_enables(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1 for contract in requested if contract.get("authoring_enable_record_rejected")
    )
    unsafe_count = sum(
        contract.get("unsafe_authoring_enable_record_count", 0) for contract in requested
    )
    forbidden_evidence_count = sum(
        contract.get("reported_forbidden_evidence_command_count", 0) for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("authoring_enable_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_evidence_count == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_enable_allowed")) == 0
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
        "schema": CANARY_DURABLE_AUTHORING_ENABLE_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_authoring_enable_count": len(requested),
        "authoring_enable_contract_defined_count": sum(
            1 for contract in requested if contract.get("authoring_enable_contract_defined")
        ),
        "executor_open_contract_ready_count": sum(
            1 for contract in requested if contract.get("executor_open_contract_ready")
        ),
        "open_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("open_inputs_satisfied")
        ),
        "open_record_valid_count": sum(
            1 for contract in requested if contract.get("open_record_valid")
        ),
        "authoring_enable_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("authoring_enable_inputs_satisfied")
        ),
        "authoring_enable_record_present_count": sum(
            1 for contract in requested if contract.get("authoring_enable_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "enable_scope_matches_count": sum(
            1 for contract in requested if contract.get("enable_scope_matches")
        ),
        "explicit_authoring_enable_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_authoring_enable_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
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
        "authoring_enable_record_valid_count": sum(
            1 for contract in requested if contract.get("authoring_enable_record_valid")
        ),
        "authoring_enable_record_rejected_count": rejected_count,
        "unsafe_authoring_enable_record_count": unsafe_count,
        "missing_authoring_enable_prerequisite_count": sum(
            contract.get("missing_authoring_enable_prerequisite_count", 0) for contract in requested
        ),
        "durable_authoring_enable_allowed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_enable_allowed")
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
