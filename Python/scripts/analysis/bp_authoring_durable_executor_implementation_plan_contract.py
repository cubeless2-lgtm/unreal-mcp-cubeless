#!/usr/bin/env python
"""
Section 96 durable executor implementation plan contract.

This contract validates a future implementation-plan-only record after the
implementation review record is valid. It does not start implementation,
change code or assets, probe live bridges, enable durable authoring, save,
delete/rename, or cleanup.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_IMPLEMENTATION_PLAN_SCHEMA = (
    "section_96_durable_executor_implementation_plan_contract_v1"
)
DURABLE_EXECUTOR_IMPLEMENTATION_PLAN_RECORD_SCHEMA = (
    "section_96_durable_executor_implementation_plan_record_v1"
)
DURABLE_EXECUTOR_IMPLEMENTATION_PLAN_SUMMARY_SCHEMA = (
    "section_96_durable_executor_implementation_plan_summary_v1"
)
EXPECTED_IMPLEMENTATION_PLAN_SCOPE = "durable_executor_implementation_plan_only"


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


def build_durable_executor_implementation_plan_contract(
    requested: bool,
    implementation_review_summary: Dict[str, Any],
    plan_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    plan_record = plan_record or {}
    plan_record_present = bool(plan_record)
    implementation_review_contract_ready = bool(
        requested
        and implementation_review_summary.get("status") == "passed"
        and implementation_review_summary.get("implementation_review_contract_defined_count") == 1
        and implementation_review_summary.get("implementation_review_record_rejected_count") == 0
        and implementation_review_summary.get("unsafe_implementation_review_record_count") == 0
        and implementation_review_summary.get("reported_forbidden_implementation_review_count") == 0
        and implementation_review_summary.get("durable_executor_implementation_review_started_count") == 0
        and implementation_review_summary.get("durable_executor_implementation_review_accepted_count") == 0
        and implementation_review_summary.get("durable_executor_implementation_plan_started_count") == 0
        and implementation_review_summary.get("code_change_performed_count") == 0
        and implementation_review_summary.get("executor_code_modified_count") == 0
        and implementation_review_summary.get("unreal_asset_modified_count") == 0
        and implementation_review_summary.get("live_bridge_probe_started_count") == 0
        and implementation_review_summary.get("durable_authoring_enabled_count") == 0
        and implementation_review_summary.get("durable_authoring_allowed_count") == 0
        and implementation_review_summary.get("asset_write_performed_count") == 0
        and implementation_review_summary.get("package_dirty_marked_count") == 0
        and implementation_review_summary.get("save_delete_rename_allowed_count") == 0
        and implementation_review_summary.get("cleanup_allowed_count") == 0
        and implementation_review_summary.get("live_command_dispatched_count") == 0
        and implementation_review_summary.get("live_command_executed_count") == 0
    )
    implementation_review_inputs_satisfied = bool(
        implementation_review_summary.get("implementation_review_inputs_satisfied_count") == 1
    )
    implementation_review_record_valid = bool(
        implementation_review_summary.get("implementation_review_record_valid_count") == 1
    )
    allowed_implementation_review_observed = bool(
        implementation_review_summary.get("allowed_implementation_review_observed_count") == 1
    )
    no_forbidden_implementation_review_claims = bool(
        implementation_review_summary.get("no_forbidden_implementation_review_claims_count") == 1
    )
    implementation_plan_inputs_satisfied = bool(
        implementation_review_inputs_satisfied
        and implementation_review_record_valid
        and allowed_implementation_review_observed
        and no_forbidden_implementation_review_claims
    )
    record_schema_matches = bool(
        plan_record_present
        and plan_record.get("schema") == DURABLE_EXECUTOR_IMPLEMENTATION_PLAN_RECORD_SCHEMA
    )
    implementation_plan_scope_matches = bool(
        plan_record_present
        and plan_record.get("implementation_plan_scope") == EXPECTED_IMPLEMENTATION_PLAN_SCOPE
    )
    explicit_implementation_plan_authorized = bool(
        plan_record_present
        and plan_record.get("explicit_durable_executor_implementation_plan_authorized") is True
    )
    plan_status_passed = bool(plan_record_present and plan_record.get("status") == "passed")
    no_save_delete_rename_acknowledged = bool(
        plan_record_present
        and plan_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        plan_record_present
        and plan_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    reported_contract_inventory_plan_count = _count(
        plan_record.get("reported_contract_inventory_plan_count")
    )
    reported_no_code_change_plan_count = _count(
        plan_record.get("reported_no_code_change_plan_count")
    )
    reported_no_asset_change_plan_count = _count(
        plan_record.get("reported_no_asset_change_plan_count")
    )
    reported_no_live_probe_plan_count = _count(
        plan_record.get("reported_no_live_probe_plan_count")
    )
    reported_implementation_started_count = _count(
        plan_record.get("reported_implementation_started_count")
    )
    reported_code_change_count = _count(plan_record.get("reported_code_change_count"))
    reported_unreal_asset_change_count = _count(
        plan_record.get("reported_unreal_asset_change_count")
    )
    reported_live_probe_count = _count(plan_record.get("reported_live_probe_count"))
    reported_durable_authoring_count = _count(plan_record.get("reported_durable_authoring_count"))
    reported_asset_write_count = _count(plan_record.get("reported_asset_write_count"))
    reported_save_count = _count(plan_record.get("reported_save_count"))
    reported_delete_rename_count = _count(plan_record.get("reported_delete_rename_count"))
    reported_cleanup_count = _count(plan_record.get("reported_cleanup_count"))
    reported_allowed_implementation_plan_count = (
        reported_contract_inventory_plan_count
        + reported_no_code_change_plan_count
        + reported_no_asset_change_plan_count
        + reported_no_live_probe_plan_count
    )
    reported_forbidden_implementation_plan_count = (
        reported_implementation_started_count
        + reported_code_change_count
        + reported_unreal_asset_change_count
        + reported_live_probe_count
        + reported_durable_authoring_count
        + reported_asset_write_count
        + reported_save_count
        + reported_delete_rename_count
        + reported_cleanup_count
    )
    allowed_implementation_plan_observed = bool(
        plan_record_present and reported_allowed_implementation_plan_count > 0
    )
    no_forbidden_implementation_plan_claims = bool(
        plan_record_present and reported_forbidden_implementation_plan_count == 0
    )
    unsafe_implementation_plan_record_count = (
        sum(
            int(_attempted(plan_record.get(key)))
            for key in (
                "durable_executor_implementation_plan_started",
                "durable_executor_implementation_plan_accepted",
                "durable_executor_change_design_started",
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
        + reported_forbidden_implementation_plan_count
    )
    implementation_plan_contract_defined = bool(
        requested and implementation_review_contract_ready
    )
    implementation_plan_record_valid = bool(
        implementation_plan_contract_defined
        and implementation_plan_inputs_satisfied
        and record_schema_matches
        and implementation_plan_scope_matches
        and explicit_implementation_plan_authorized
        and plan_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_implementation_plan_observed
        and no_forbidden_implementation_plan_claims
        and unsafe_implementation_plan_record_count == 0
    )
    missing = []
    if requested:
        if not implementation_review_inputs_satisfied:
            missing.append("section_95_implementation_review_inputs_satisfied")
        if not implementation_review_record_valid:
            missing.append("section_95_implementation_review_record_valid")
        if not allowed_implementation_review_observed:
            missing.append("section_95_allowed_implementation_review_observed")
        if not no_forbidden_implementation_review_claims:
            missing.append("section_95_no_forbidden_implementation_review_claims")
        if not plan_record_present:
            missing.append("durable_executor_implementation_plan_record_present")
        if not record_schema_matches:
            missing.append("durable_executor_implementation_plan_record_schema")
        if not implementation_plan_scope_matches:
            missing.append("durable_executor_implementation_plan_only_scope")
        if not explicit_implementation_plan_authorized:
            missing.append("explicit_durable_executor_implementation_plan_authorization")
        if not plan_status_passed:
            missing.append("durable_executor_implementation_plan_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_implementation_plan_observed:
            missing.append("allowed_durable_executor_implementation_plan_observed")
        if not no_forbidden_implementation_plan_claims:
            missing.append("no_forbidden_durable_executor_implementation_plan_claims")
        missing.append("separate_durable_executor_change_design_contract")
    implementation_plan_record_rejected = bool(
        plan_record_present and not implementation_plan_record_valid
    )
    return {
        "id": "durable_executor_implementation_plan",
        "schema": DURABLE_EXECUTOR_IMPLEMENTATION_PLAN_SCHEMA,
        "requested": requested,
        "implementation_plan_contract_defined": implementation_plan_contract_defined,
        "required_implementation_plan_record_schema": (
            DURABLE_EXECUTOR_IMPLEMENTATION_PLAN_RECORD_SCHEMA if requested else ""
        ),
        "expected_implementation_plan_scope": (
            EXPECTED_IMPLEMENTATION_PLAN_SCOPE if requested else ""
        ),
        "implementation_review_contract_ready": implementation_review_contract_ready,
        "implementation_review_inputs_satisfied": implementation_review_inputs_satisfied,
        "implementation_review_record_valid": implementation_review_record_valid,
        "allowed_implementation_review_observed": allowed_implementation_review_observed,
        "no_forbidden_implementation_review_claims": no_forbidden_implementation_review_claims,
        "implementation_plan_inputs_satisfied": implementation_plan_inputs_satisfied,
        "implementation_plan_record_present": plan_record_present,
        "record_schema_matches": record_schema_matches,
        "implementation_plan_scope_matches": implementation_plan_scope_matches,
        "explicit_implementation_plan_authorized": explicit_implementation_plan_authorized,
        "plan_status_passed": plan_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": explicit_durable_mvp_request_reconfirmed,
        "reported_allowed_implementation_plan_count": reported_allowed_implementation_plan_count,
        "reported_forbidden_implementation_plan_count": reported_forbidden_implementation_plan_count,
        "allowed_implementation_plan_observed": allowed_implementation_plan_observed,
        "no_forbidden_implementation_plan_claims": no_forbidden_implementation_plan_claims,
        "implementation_plan_record_valid": implementation_plan_record_valid,
        "implementation_plan_record_rejected": implementation_plan_record_rejected,
        "unsafe_implementation_plan_record_count": unsafe_implementation_plan_record_count,
        "missing_implementation_plan_prerequisites": missing,
        "missing_implementation_plan_prerequisite_count": len(missing),
        "durable_executor_implementation_plan_started": False,
        "durable_executor_implementation_plan_accepted": False,
        "durable_executor_change_design_started": False,
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
        "reported_contract_inventory_plan_count": reported_contract_inventory_plan_count,
        "reported_no_code_change_plan_count": reported_no_code_change_plan_count,
        "reported_no_asset_change_plan_count": reported_no_asset_change_plan_count,
        "reported_no_live_probe_plan_count": reported_no_live_probe_plan_count,
        "reported_implementation_started_count": reported_implementation_started_count,
        "reported_code_change_count": reported_code_change_count,
        "reported_unreal_asset_change_count": reported_unreal_asset_change_count,
        "reported_live_probe_count": reported_live_probe_count,
        "reported_durable_authoring_count": reported_durable_authoring_count,
        "reported_asset_write_count": reported_asset_write_count,
        "reported_save_count": reported_save_count,
        "reported_delete_rename_count": reported_delete_rename_count,
        "reported_cleanup_count": reported_cleanup_count,
    }


def summarize_durable_executor_implementation_plans(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1 for contract in requested if contract.get("implementation_plan_record_rejected")
    )
    unsafe_count = sum(
        contract.get("unsafe_implementation_plan_record_count", 0)
        for contract in requested
    )
    forbidden_plan_count = sum(
        contract.get("reported_forbidden_implementation_plan_count", 0)
        for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(
                1
                for contract in requested
                if contract.get("implementation_plan_contract_defined")
            )
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_plan_count == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_executor_implementation_plan_started")
            )
            == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_executor_implementation_plan_accepted")
            )
            == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_executor_change_design_started")
            )
            == 0
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
        "schema": DURABLE_EXECUTOR_IMPLEMENTATION_PLAN_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_implementation_plan_count": len(requested),
        "implementation_plan_contract_defined_count": sum(
            1 for contract in requested if contract.get("implementation_plan_contract_defined")
        ),
        "implementation_review_contract_ready_count": sum(
            1 for contract in requested if contract.get("implementation_review_contract_ready")
        ),
        "implementation_review_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("implementation_review_inputs_satisfied")
        ),
        "implementation_review_record_valid_count": sum(
            1 for contract in requested if contract.get("implementation_review_record_valid")
        ),
        "allowed_implementation_review_observed_count": sum(
            1 for contract in requested if contract.get("allowed_implementation_review_observed")
        ),
        "no_forbidden_implementation_review_claims_count": sum(
            1
            for contract in requested
            if contract.get("no_forbidden_implementation_review_claims")
        ),
        "implementation_plan_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("implementation_plan_inputs_satisfied")
        ),
        "implementation_plan_record_present_count": sum(
            1 for contract in requested if contract.get("implementation_plan_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "implementation_plan_scope_matches_count": sum(
            1 for contract in requested if contract.get("implementation_plan_scope_matches")
        ),
        "explicit_implementation_plan_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_implementation_plan_authorized")
        ),
        "plan_status_passed_count": sum(
            1 for contract in requested if contract.get("plan_status_passed")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "explicit_durable_mvp_request_reconfirmed_count": sum(
            1 for contract in requested if contract.get("explicit_durable_mvp_request_reconfirmed")
        ),
        "allowed_implementation_plan_observed_count": sum(
            1 for contract in requested if contract.get("allowed_implementation_plan_observed")
        ),
        "no_forbidden_implementation_plan_claims_count": sum(
            1 for contract in requested if contract.get("no_forbidden_implementation_plan_claims")
        ),
        "implementation_plan_record_valid_count": sum(
            1 for contract in requested if contract.get("implementation_plan_record_valid")
        ),
        "implementation_plan_record_rejected_count": rejected_count,
        "unsafe_implementation_plan_record_count": unsafe_count,
        "missing_implementation_plan_prerequisite_count": sum(
            contract.get("missing_implementation_plan_prerequisite_count", 0)
            for contract in requested
        ),
        "reported_allowed_implementation_plan_count": sum(
            contract.get("reported_allowed_implementation_plan_count", 0)
            for contract in requested
        ),
        "reported_forbidden_implementation_plan_count": forbidden_plan_count,
        "durable_executor_implementation_plan_started_count": sum(
            1
            for contract in requested
            if contract.get("durable_executor_implementation_plan_started")
        ),
        "durable_executor_implementation_plan_accepted_count": sum(
            1
            for contract in requested
            if contract.get("durable_executor_implementation_plan_accepted")
        ),
        "durable_executor_change_design_started_count": sum(
            1 for contract in requested if contract.get("durable_executor_change_design_started")
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
        "reported_contract_inventory_plan_count": sum(
            contract.get("reported_contract_inventory_plan_count", 0)
            for contract in requested
        ),
        "reported_no_code_change_plan_count": sum(
            contract.get("reported_no_code_change_plan_count", 0)
            for contract in requested
        ),
        "reported_no_asset_change_plan_count": sum(
            contract.get("reported_no_asset_change_plan_count", 0)
            for contract in requested
        ),
        "reported_no_live_probe_plan_count": sum(
            contract.get("reported_no_live_probe_plan_count", 0)
            for contract in requested
        ),
        "reported_implementation_started_count": sum(
            contract.get("reported_implementation_started_count", 0)
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
