#!/usr/bin/env python
"""
Section 56 durable canary approval gate contract.

The approval gate proves that a canary target has an explicit, scoped approval
record before any later live canary section may consider execution. This section
does not approve live durable authoring, saving, or cleanup.
"""

from __future__ import annotations

from typing import Any, Dict, Optional, Sequence


CANARY_APPROVAL_RECORD_SCHEMA = "section_56_durable_canary_approval_record_v1"
CANARY_APPROVAL_GATE_SCHEMA = "section_56_durable_canary_approval_gate_v1"
CANARY_APPROVAL_SUMMARY_SCHEMA = "section_56_durable_canary_approval_summary_v1"

APPROVED_OPERATION = "canary_preflight_only"
APPROVAL_SCOPE_ID = "durable_canary_prep"


def build_scoped_canary_approval_record(canary_prep_contract: Dict[str, Any]) -> Dict[str, Any]:
    if not canary_prep_contract.get("requested"):
        return {}
    return {
        "schema": CANARY_APPROVAL_RECORD_SCHEMA,
        "approval_id": "section_56_scoped_canary_preflight_approval",
        "approval_source": "offline_release_boundary_contract",
        "approval_scope_id": APPROVAL_SCOPE_ID,
        "approved_operation": APPROVED_OPERATION,
        "source_target_asset_path": canary_prep_contract.get("source_target_asset_path", ""),
        "canary_package_path": canary_prep_contract.get("canary_package_path", ""),
        "canary_asset_path": canary_prep_contract.get("canary_asset_path", ""),
        "approval_does_not_authorize_live_execution": True,
        "approval_does_not_authorize_save_or_delete": True,
    }


def build_canary_approval_gate_contract(
    requested: bool,
    canary_prep_contract: Dict[str, Any],
    approval_record: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    approval_record = approval_record or {}
    approval_present = bool(approval_record)
    schema_ok = approval_record.get("schema") == CANARY_APPROVAL_RECORD_SCHEMA
    scope_ok = approval_record.get("approval_scope_id") == APPROVAL_SCOPE_ID
    operation_ok = approval_record.get("approved_operation") == APPROVED_OPERATION
    package_ok = approval_record.get("canary_package_path") == canary_prep_contract.get("canary_package_path")
    asset_ok = approval_record.get("canary_asset_path") == canary_prep_contract.get("canary_asset_path")
    source_target_ok = approval_record.get("source_target_asset_path") == canary_prep_contract.get(
        "source_target_asset_path"
    )
    scoped_to_canary_package = bool(
        requested
        and canary_prep_contract.get("canary_package_allowlisted")
        and package_ok
        and not canary_prep_contract.get("general_blueprints_package_allowed")
    )
    approval_gate_passed = bool(
        requested
        and canary_prep_contract.get("canary_prep_ready")
        and approval_present
        and schema_ok
        and scope_ok
        and operation_ok
        and package_ok
        and asset_ok
        and source_target_ok
        and scoped_to_canary_package
        and approval_record.get("approval_does_not_authorize_live_execution") is True
        and approval_record.get("approval_does_not_authorize_save_or_delete") is True
    )

    blocked_by: list[str] = []
    if requested:
        if not canary_prep_contract.get("canary_prep_ready"):
            blocked_by.append("canary_prep_not_ready")
        if not approval_present:
            blocked_by.append("canary_approval_record_missing")
        if approval_present and not schema_ok:
            blocked_by.append("canary_approval_schema_mismatch")
        if approval_present and not scope_ok:
            blocked_by.append("canary_approval_scope_mismatch")
        if approval_present and not operation_ok:
            blocked_by.append("canary_approval_operation_mismatch")
        if approval_present and not package_ok:
            blocked_by.append("canary_approval_package_mismatch")
        if approval_present and not asset_ok:
            blocked_by.append("canary_approval_asset_mismatch")
        if approval_present and not source_target_ok:
            blocked_by.append("canary_approval_source_target_mismatch")
        if not scoped_to_canary_package:
            blocked_by.append("canary_approval_not_scoped_to_canary_package")
        blocked_by.append("section_56_approval_gate_does_not_enable_live_canary")

    return {
        "id": "durable_canary_approval_gate",
        "schema": CANARY_APPROVAL_GATE_SCHEMA,
        "requested": requested,
        "canary_prep_schema": canary_prep_contract.get("schema", ""),
        "canary_prep_ready": bool(canary_prep_contract.get("canary_prep_ready")),
        "approval_record_required": requested,
        "approval_record_present": approval_present,
        "approval_record_schema_ok": schema_ok if approval_present else False,
        "approval_scope_matches": scope_ok if approval_present else False,
        "approval_operation_matches": operation_ok if approval_present else False,
        "approval_package_matches": package_ok if approval_present else False,
        "approval_asset_matches": asset_ok if approval_present else False,
        "approval_source_target_matches": source_target_ok if approval_present else False,
        "approval_scoped_to_canary_package": scoped_to_canary_package,
        "canary_approval_gate_passed": approval_gate_passed,
        "canary_executor_may_open": False,
        "canary_live_execution_allowed": False,
        "general_blueprints_package_allowed": False,
        "save_true_allowed": False,
        "save_asset_allowed": False,
        "delete_asset_allowed": False,
        "live_command_count": 0,
        "approval_record": approval_record,
        "blocked_by": sorted(set(blocked_by)),
        "required_reinforcement": []
        if not requested
        else [
            "keep Section 56 as an explicit approval gate only",
            "add Section 57 live canary preflight contract before any canary command may run",
            "prove canary cleanup remains limited to ownership-marked canary assets",
        ],
    }


def summarize_canary_approval_gate_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("canary_approval_gate_passed")) == len(requested)
            and sum(1 for contract in requested if contract.get("canary_executor_may_open")) == 0
            and sum(1 for contract in requested if contract.get("canary_live_execution_allowed")) == 0
            and sum(1 for contract in requested if contract.get("general_blueprints_package_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_true_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_asset_allowed")) == 0
            and sum(1 for contract in requested if contract.get("delete_asset_allowed")) == 0
            and sum(contract.get("live_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": CANARY_APPROVAL_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_approval_count": len(requested),
        "approval_record_present_count": sum(1 for contract in requested if contract.get("approval_record_present")),
        "canary_approval_gate_passed_count": sum(
            1 for contract in requested if contract.get("canary_approval_gate_passed")
        ),
        "approval_scoped_to_canary_package_count": sum(
            1 for contract in requested if contract.get("approval_scoped_to_canary_package")
        ),
        "canary_executor_may_open_count": sum(1 for contract in requested if contract.get("canary_executor_may_open")),
        "canary_live_execution_allowed_count": sum(
            1 for contract in requested if contract.get("canary_live_execution_allowed")
        ),
        "general_blueprints_package_allowed_count": sum(
            1 for contract in requested if contract.get("general_blueprints_package_allowed")
        ),
        "save_true_allowed_count": sum(1 for contract in requested if contract.get("save_true_allowed")),
        "save_asset_allowed_count": sum(1 for contract in requested if contract.get("save_asset_allowed")),
        "delete_asset_allowed_count": sum(1 for contract in requested if contract.get("delete_asset_allowed")),
        "live_command_count": sum(contract.get("live_command_count", 0) for contract in requested),
    }
