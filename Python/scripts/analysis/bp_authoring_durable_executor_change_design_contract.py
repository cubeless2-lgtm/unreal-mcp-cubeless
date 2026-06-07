#!/usr/bin/env python
"""
Section 97 durable executor change design contract.

This contract validates a future change-design-only record after the
implementation plan record is valid. It does not approve code edits, asset
changes, live probes, durable authoring, saves, delete/rename, or cleanup.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_CHANGE_DESIGN_SCHEMA = "section_97_durable_executor_change_design_contract_v1"
DURABLE_EXECUTOR_CHANGE_DESIGN_RECORD_SCHEMA = (
    "section_97_durable_executor_change_design_record_v1"
)
DURABLE_EXECUTOR_CHANGE_DESIGN_SUMMARY_SCHEMA = (
    "section_97_durable_executor_change_design_summary_v1"
)
EXPECTED_CHANGE_DESIGN_SCOPE = "durable_executor_change_design_only"


def _attempted(value: Any) -> bool:
    return value is True or value == 1


def _count(value: Any) -> int:
    if value is True:
        return 1
    if value in (False, None, ""):
        return 0
    try:
        return max(0, int(value))
    except (TypeError, ValueError):
        return 0


def build_durable_executor_change_design_contract(
    requested: bool,
    implementation_plan_summary: Dict[str, Any],
    design_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    design_record = design_record or {}
    design_record_present = bool(design_record)
    implementation_plan_contract_ready = bool(
        requested
        and implementation_plan_summary.get("status") == "passed"
        and implementation_plan_summary.get("implementation_plan_contract_defined_count") == 1
        and implementation_plan_summary.get("implementation_plan_record_rejected_count") == 0
        and implementation_plan_summary.get("unsafe_implementation_plan_record_count") == 0
        and implementation_plan_summary.get("reported_forbidden_implementation_plan_count") == 0
        and implementation_plan_summary.get("durable_executor_implementation_plan_started_count") == 0
        and implementation_plan_summary.get("durable_executor_implementation_plan_accepted_count") == 0
        and implementation_plan_summary.get("durable_executor_change_design_started_count") == 0
        and implementation_plan_summary.get("code_change_performed_count") == 0
        and implementation_plan_summary.get("executor_code_modified_count") == 0
        and implementation_plan_summary.get("unreal_asset_modified_count") == 0
        and implementation_plan_summary.get("live_bridge_probe_started_count") == 0
        and implementation_plan_summary.get("durable_authoring_enabled_count") == 0
        and implementation_plan_summary.get("durable_authoring_allowed_count") == 0
        and implementation_plan_summary.get("asset_write_performed_count") == 0
        and implementation_plan_summary.get("package_dirty_marked_count") == 0
        and implementation_plan_summary.get("save_delete_rename_allowed_count") == 0
        and implementation_plan_summary.get("cleanup_allowed_count") == 0
        and implementation_plan_summary.get("live_command_dispatched_count") == 0
        and implementation_plan_summary.get("live_command_executed_count") == 0
    )
    implementation_plan_inputs_satisfied = bool(
        implementation_plan_summary.get("implementation_plan_inputs_satisfied_count") == 1
    )
    implementation_plan_record_valid = bool(
        implementation_plan_summary.get("implementation_plan_record_valid_count") == 1
    )
    allowed_implementation_plan_observed = bool(
        implementation_plan_summary.get("allowed_implementation_plan_observed_count") == 1
    )
    no_forbidden_implementation_plan_claims = bool(
        implementation_plan_summary.get("no_forbidden_implementation_plan_claims_count") == 1
    )
    change_design_inputs_satisfied = bool(
        implementation_plan_inputs_satisfied
        and implementation_plan_record_valid
        and allowed_implementation_plan_observed
        and no_forbidden_implementation_plan_claims
    )
    record_schema_matches = bool(
        design_record_present
        and design_record.get("schema") == DURABLE_EXECUTOR_CHANGE_DESIGN_RECORD_SCHEMA
    )
    change_design_scope_matches = bool(
        design_record_present
        and design_record.get("change_design_scope") == EXPECTED_CHANGE_DESIGN_SCOPE
    )
    explicit_change_design_authorized = bool(
        design_record_present
        and design_record.get("explicit_durable_executor_change_design_authorized") is True
    )
    design_status_passed = bool(design_record_present and design_record.get("status") == "passed")
    no_save_delete_rename_acknowledged = bool(
        design_record_present
        and design_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        design_record_present
        and design_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    reported_change_design_inventory_count = _count(
        design_record.get("reported_change_design_inventory_count")
    )
    reported_no_code_change_design_count = _count(
        design_record.get("reported_no_code_change_design_count")
    )
    reported_no_asset_change_design_count = _count(
        design_record.get("reported_no_asset_change_design_count")
    )
    reported_no_live_probe_design_count = _count(
        design_record.get("reported_no_live_probe_design_count")
    )
    reported_code_change_approval_count = _count(
        design_record.get("reported_code_change_approval_count")
    )
    reported_code_change_count = _count(design_record.get("reported_code_change_count"))
    reported_unreal_asset_change_count = _count(
        design_record.get("reported_unreal_asset_change_count")
    )
    reported_live_probe_count = _count(design_record.get("reported_live_probe_count"))
    reported_durable_authoring_count = _count(design_record.get("reported_durable_authoring_count"))
    reported_asset_write_count = _count(design_record.get("reported_asset_write_count"))
    reported_save_count = _count(design_record.get("reported_save_count"))
    reported_delete_rename_count = _count(design_record.get("reported_delete_rename_count"))
    reported_cleanup_count = _count(design_record.get("reported_cleanup_count"))
    reported_allowed_change_design_count = (
        reported_change_design_inventory_count
        + reported_no_code_change_design_count
        + reported_no_asset_change_design_count
        + reported_no_live_probe_design_count
    )
    reported_forbidden_change_design_count = (
        reported_code_change_approval_count
        + reported_code_change_count
        + reported_unreal_asset_change_count
        + reported_live_probe_count
        + reported_durable_authoring_count
        + reported_asset_write_count
        + reported_save_count
        + reported_delete_rename_count
        + reported_cleanup_count
    )
    allowed_change_design_observed = bool(
        design_record_present and reported_allowed_change_design_count > 0
    )
    no_forbidden_change_design_claims = bool(
        design_record_present and reported_forbidden_change_design_count == 0
    )
    unsafe_change_design_record_count = (
        sum(
            int(_attempted(design_record.get(key)))
            for key in (
                "durable_executor_change_design_started",
                "durable_executor_change_design_accepted",
                "durable_executor_code_change_approval_started",
                "code_change_performed",
                "executor_code_modified",
                "unreal_asset_modified",
                "live_bridge_probe_started",
                "durable_authoring_enabled",
                "durable_authoring_allowed",
                "asset_write_performed",
                "package_dirty_marked",
                "save_asset_executed",
                "delete_asset_authorized",
                "rename_asset_authorized",
                "cleanup_authorized",
                "live_command_dispatched",
                "live_command_executed",
            )
        )
        + reported_forbidden_change_design_count
    )
    change_design_contract_defined = bool(requested and implementation_plan_contract_ready)
    change_design_record_valid = bool(
        change_design_contract_defined
        and change_design_inputs_satisfied
        and record_schema_matches
        and change_design_scope_matches
        and explicit_change_design_authorized
        and design_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_change_design_observed
        and no_forbidden_change_design_claims
        and unsafe_change_design_record_count == 0
    )
    missing = []
    if requested:
        if not implementation_plan_inputs_satisfied:
            missing.append("section_96_implementation_plan_inputs_satisfied")
        if not implementation_plan_record_valid:
            missing.append("section_96_implementation_plan_record_valid")
        if not allowed_implementation_plan_observed:
            missing.append("section_96_allowed_implementation_plan_observed")
        if not no_forbidden_implementation_plan_claims:
            missing.append("section_96_no_forbidden_implementation_plan_claims")
        if not design_record_present:
            missing.append("durable_executor_change_design_record_present")
        if not record_schema_matches:
            missing.append("durable_executor_change_design_record_schema")
        if not change_design_scope_matches:
            missing.append("durable_executor_change_design_only_scope")
        if not explicit_change_design_authorized:
            missing.append("explicit_durable_executor_change_design_authorization")
        if not design_status_passed:
            missing.append("durable_executor_change_design_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_change_design_observed:
            missing.append("allowed_durable_executor_change_design_observed")
        if not no_forbidden_change_design_claims:
            missing.append("no_forbidden_durable_executor_change_design_claims")
        missing.append("separate_durable_executor_code_change_approval_contract")
    change_design_record_rejected = bool(design_record_present and not change_design_record_valid)
    return {
        "id": "durable_executor_change_design",
        "schema": DURABLE_EXECUTOR_CHANGE_DESIGN_SCHEMA,
        "requested": requested,
        "change_design_contract_defined": change_design_contract_defined,
        "required_change_design_record_schema": (
            DURABLE_EXECUTOR_CHANGE_DESIGN_RECORD_SCHEMA if requested else ""
        ),
        "expected_change_design_scope": EXPECTED_CHANGE_DESIGN_SCOPE if requested else "",
        "implementation_plan_contract_ready": implementation_plan_contract_ready,
        "implementation_plan_inputs_satisfied": implementation_plan_inputs_satisfied,
        "implementation_plan_record_valid": implementation_plan_record_valid,
        "allowed_implementation_plan_observed": allowed_implementation_plan_observed,
        "no_forbidden_implementation_plan_claims": no_forbidden_implementation_plan_claims,
        "change_design_inputs_satisfied": change_design_inputs_satisfied,
        "change_design_record_present": design_record_present,
        "record_schema_matches": record_schema_matches,
        "change_design_scope_matches": change_design_scope_matches,
        "explicit_change_design_authorized": explicit_change_design_authorized,
        "design_status_passed": design_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": explicit_durable_mvp_request_reconfirmed,
        "reported_allowed_change_design_count": reported_allowed_change_design_count,
        "reported_forbidden_change_design_count": reported_forbidden_change_design_count,
        "allowed_change_design_observed": allowed_change_design_observed,
        "no_forbidden_change_design_claims": no_forbidden_change_design_claims,
        "change_design_record_valid": change_design_record_valid,
        "change_design_record_rejected": change_design_record_rejected,
        "unsafe_change_design_record_count": unsafe_change_design_record_count,
        "missing_change_design_prerequisites": missing,
        "missing_change_design_prerequisite_count": len(missing),
        "durable_executor_change_design_started": False,
        "durable_executor_change_design_accepted": False,
        "durable_executor_code_change_approval_started": False,
        "code_change_performed": False,
        "executor_code_modified": False,
        "unreal_asset_modified": False,
        "live_bridge_probe_started": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatched": False,
        "live_command_executed": False,
        "reported_change_design_inventory_count": reported_change_design_inventory_count,
        "reported_no_code_change_design_count": reported_no_code_change_design_count,
        "reported_no_asset_change_design_count": reported_no_asset_change_design_count,
        "reported_no_live_probe_design_count": reported_no_live_probe_design_count,
        "reported_code_change_approval_count": reported_code_change_approval_count,
        "reported_code_change_count": reported_code_change_count,
        "reported_unreal_asset_change_count": reported_unreal_asset_change_count,
        "reported_live_probe_count": reported_live_probe_count,
        "reported_durable_authoring_count": reported_durable_authoring_count,
        "reported_asset_write_count": reported_asset_write_count,
        "reported_save_count": reported_save_count,
        "reported_delete_rename_count": reported_delete_rename_count,
        "reported_cleanup_count": reported_cleanup_count,
    }


def summarize_durable_executor_change_designs(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(1 for contract in requested if contract.get("change_design_record_rejected"))
    unsafe_count = sum(
        contract.get("unsafe_change_design_record_count", 0) for contract in requested
    )
    forbidden_design_count = sum(
        contract.get("reported_forbidden_change_design_count", 0)
        for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("change_design_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_design_count == 0
            and sum(1 for contract in requested if contract.get("durable_executor_change_design_started")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_change_design_accepted")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_code_change_approval_started")) == 0
            and sum(1 for contract in requested if contract.get("code_change_performed")) == 0
            and sum(1 for contract in requested if contract.get("executor_code_modified")) == 0
            and sum(1 for contract in requested if contract.get("unreal_asset_modified")) == 0
            and sum(1 for contract in requested if contract.get("live_bridge_probe_started")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_enabled")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_allowed")) == 0
            and sum(1 for contract in requested if contract.get("asset_write_performed")) == 0
            and sum(1 for contract in requested if contract.get("package_dirty_marked")) == 0
            and sum(1 for contract in requested if contract.get("save_delete_rename_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_dispatched")) == 0
            and sum(1 for contract in requested if contract.get("live_command_executed")) == 0
            else "failed"
        )
    return {
        "schema": DURABLE_EXECUTOR_CHANGE_DESIGN_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_change_design_count": len(requested),
        "change_design_contract_defined_count": sum(
            1 for contract in requested if contract.get("change_design_contract_defined")
        ),
        "implementation_plan_contract_ready_count": sum(
            1 for contract in requested if contract.get("implementation_plan_contract_ready")
        ),
        "implementation_plan_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("implementation_plan_inputs_satisfied")
        ),
        "implementation_plan_record_valid_count": sum(
            1 for contract in requested if contract.get("implementation_plan_record_valid")
        ),
        "allowed_implementation_plan_observed_count": sum(
            1 for contract in requested if contract.get("allowed_implementation_plan_observed")
        ),
        "no_forbidden_implementation_plan_claims_count": sum(
            1 for contract in requested if contract.get("no_forbidden_implementation_plan_claims")
        ),
        "change_design_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("change_design_inputs_satisfied")
        ),
        "change_design_record_present_count": sum(
            1 for contract in requested if contract.get("change_design_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "change_design_scope_matches_count": sum(
            1 for contract in requested if contract.get("change_design_scope_matches")
        ),
        "explicit_change_design_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_change_design_authorized")
        ),
        "design_status_passed_count": sum(
            1 for contract in requested if contract.get("design_status_passed")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "explicit_durable_mvp_request_reconfirmed_count": sum(
            1 for contract in requested if contract.get("explicit_durable_mvp_request_reconfirmed")
        ),
        "allowed_change_design_observed_count": sum(
            1 for contract in requested if contract.get("allowed_change_design_observed")
        ),
        "no_forbidden_change_design_claims_count": sum(
            1 for contract in requested if contract.get("no_forbidden_change_design_claims")
        ),
        "change_design_record_valid_count": sum(
            1 for contract in requested if contract.get("change_design_record_valid")
        ),
        "change_design_record_rejected_count": rejected_count,
        "unsafe_change_design_record_count": unsafe_count,
        "missing_change_design_prerequisite_count": sum(
            contract.get("missing_change_design_prerequisite_count", 0)
            for contract in requested
        ),
        "reported_allowed_change_design_count": sum(
            contract.get("reported_allowed_change_design_count", 0) for contract in requested
        ),
        "reported_forbidden_change_design_count": forbidden_design_count,
        "durable_executor_change_design_started_count": sum(
            1 for contract in requested if contract.get("durable_executor_change_design_started")
        ),
        "durable_executor_change_design_accepted_count": sum(
            1 for contract in requested if contract.get("durable_executor_change_design_accepted")
        ),
        "durable_executor_code_change_approval_started_count": sum(
            1
            for contract in requested
            if contract.get("durable_executor_code_change_approval_started")
        ),
        "code_change_performed_count": sum(
            1 for contract in requested if contract.get("code_change_performed")
        ),
        "executor_code_modified_count": sum(
            1 for contract in requested if contract.get("executor_code_modified")
        ),
        "unreal_asset_modified_count": sum(
            1 for contract in requested if contract.get("unreal_asset_modified")
        ),
        "live_bridge_probe_started_count": sum(
            1 for contract in requested if contract.get("live_bridge_probe_started")
        ),
        "durable_authoring_enabled_count": sum(
            1 for contract in requested if contract.get("durable_authoring_enabled")
        ),
        "durable_authoring_allowed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_allowed")
        ),
        "asset_write_performed_count": sum(
            1 for contract in requested if contract.get("asset_write_performed")
        ),
        "package_dirty_marked_count": sum(
            1 for contract in requested if contract.get("package_dirty_marked")
        ),
        "save_delete_rename_allowed_count": sum(
            1 for contract in requested if contract.get("save_delete_rename_allowed")
        ),
        "cleanup_allowed_count": sum(
            1 for contract in requested if contract.get("cleanup_allowed")
        ),
        "live_command_dispatched_count": sum(
            1 for contract in requested if contract.get("live_command_dispatched")
        ),
        "live_command_executed_count": sum(
            1 for contract in requested if contract.get("live_command_executed")
        ),
        "reported_change_design_inventory_count": sum(
            contract.get("reported_change_design_inventory_count", 0)
            for contract in requested
        ),
        "reported_no_code_change_design_count": sum(
            contract.get("reported_no_code_change_design_count", 0)
            for contract in requested
        ),
        "reported_no_asset_change_design_count": sum(
            contract.get("reported_no_asset_change_design_count", 0)
            for contract in requested
        ),
        "reported_no_live_probe_design_count": sum(
            contract.get("reported_no_live_probe_design_count", 0)
            for contract in requested
        ),
        "reported_code_change_approval_count": sum(
            contract.get("reported_code_change_approval_count", 0)
            for contract in requested
        ),
        "reported_code_change_count": sum(
            contract.get("reported_code_change_count", 0) for contract in requested
        ),
        "reported_unreal_asset_change_count": sum(
            contract.get("reported_unreal_asset_change_count", 0)
            for contract in requested
        ),
        "reported_live_probe_count": sum(
            contract.get("reported_live_probe_count", 0) for contract in requested
        ),
        "reported_durable_authoring_count": sum(
            contract.get("reported_durable_authoring_count", 0) for contract in requested
        ),
        "reported_asset_write_count": sum(
            contract.get("reported_asset_write_count", 0) for contract in requested
        ),
        "reported_save_count": sum(
            contract.get("reported_save_count", 0) for contract in requested
        ),
        "reported_delete_rename_count": sum(
            contract.get("reported_delete_rename_count", 0) for contract in requested
        ),
        "reported_cleanup_count": sum(
            contract.get("reported_cleanup_count", 0) for contract in requested
        ),
    }
