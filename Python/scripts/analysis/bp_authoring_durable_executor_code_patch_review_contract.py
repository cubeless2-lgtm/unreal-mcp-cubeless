#!/usr/bin/env python
"""
Section 100 durable executor code patch review contract.

This contract validates a future code-patch-review-only record after the code
patch plan record is valid. It does not start or apply code patches, modify
assets, probe live bridges, enable durable authoring, save, delete/rename, or
cleanup.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_CODE_PATCH_REVIEW_SCHEMA = (
    "section_100_durable_executor_code_patch_review_contract_v1"
)
DURABLE_EXECUTOR_CODE_PATCH_REVIEW_RECORD_SCHEMA = (
    "section_100_durable_executor_code_patch_review_record_v1"
)
DURABLE_EXECUTOR_CODE_PATCH_REVIEW_SUMMARY_SCHEMA = (
    "section_100_durable_executor_code_patch_review_summary_v1"
)
EXPECTED_CODE_PATCH_REVIEW_SCOPE = "durable_executor_code_patch_review_only"


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


def build_durable_executor_code_patch_review_contract(
    requested: bool,
    code_patch_plan_summary: Dict[str, Any],
    review_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    review_record = review_record or {}
    review_record_present = bool(review_record)
    code_patch_plan_contract_ready = bool(
        requested
        and code_patch_plan_summary.get("status") == "passed"
        and code_patch_plan_summary.get("code_patch_plan_contract_defined_count") == 1
        and code_patch_plan_summary.get("code_patch_plan_record_rejected_count") == 0
        and code_patch_plan_summary.get("unsafe_code_patch_plan_record_count") == 0
        and code_patch_plan_summary.get("reported_forbidden_code_patch_plan_count") == 0
        and code_patch_plan_summary.get("durable_executor_code_patch_plan_started_count") == 0
        and code_patch_plan_summary.get("durable_executor_code_patch_plan_accepted_count") == 0
        and code_patch_plan_summary.get("durable_executor_code_patch_review_started_count") == 0
        and code_patch_plan_summary.get("code_change_performed_count") == 0
        and code_patch_plan_summary.get("executor_code_modified_count") == 0
        and code_patch_plan_summary.get("unreal_asset_modified_count") == 0
        and code_patch_plan_summary.get("live_bridge_probe_started_count") == 0
        and code_patch_plan_summary.get("durable_authoring_enabled_count") == 0
        and code_patch_plan_summary.get("durable_authoring_allowed_count") == 0
        and code_patch_plan_summary.get("asset_write_performed_count") == 0
        and code_patch_plan_summary.get("package_dirty_marked_count") == 0
        and code_patch_plan_summary.get("save_delete_rename_allowed_count") == 0
        and code_patch_plan_summary.get("cleanup_allowed_count") == 0
        and code_patch_plan_summary.get("live_command_dispatched_count") == 0
        and code_patch_plan_summary.get("live_command_executed_count") == 0
    )
    code_patch_plan_inputs_satisfied = bool(
        code_patch_plan_summary.get("code_patch_plan_inputs_satisfied_count") == 1
    )
    code_patch_plan_record_valid = bool(
        code_patch_plan_summary.get("code_patch_plan_record_valid_count") == 1
    )
    allowed_code_patch_plan_observed = bool(
        code_patch_plan_summary.get("allowed_code_patch_plan_observed_count") == 1
    )
    no_forbidden_code_patch_plan_claims = bool(
        code_patch_plan_summary.get("no_forbidden_code_patch_plan_claims_count") == 1
    )
    code_patch_review_inputs_satisfied = bool(
        code_patch_plan_inputs_satisfied
        and code_patch_plan_record_valid
        and allowed_code_patch_plan_observed
        and no_forbidden_code_patch_plan_claims
    )
    record_schema_matches = bool(
        review_record_present
        and review_record.get("schema") == DURABLE_EXECUTOR_CODE_PATCH_REVIEW_RECORD_SCHEMA
    )
    code_patch_review_scope_matches = bool(
        review_record_present
        and review_record.get("code_patch_review_scope") == EXPECTED_CODE_PATCH_REVIEW_SCOPE
    )
    explicit_code_patch_review_authorized = bool(
        review_record_present
        and review_record.get("explicit_durable_executor_code_patch_review_authorized")
        is True
    )
    review_status_passed = bool(
        review_record_present and review_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        review_record_present
        and review_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        review_record_present
        and review_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    reported_patch_plan_review_count = _count(
        review_record.get("reported_patch_plan_review_count")
    )
    reported_patch_risk_review_count = _count(
        review_record.get("reported_patch_risk_review_count")
    )
    reported_no_code_change_review_count = _count(
        review_record.get("reported_no_code_change_review_count")
    )
    reported_no_asset_change_review_count = _count(
        review_record.get("reported_no_asset_change_review_count")
    )
    reported_no_live_probe_review_count = _count(
        review_record.get("reported_no_live_probe_review_count")
    )
    reported_code_patch_application_started_count = _count(
        review_record.get("reported_code_patch_application_started_count")
    )
    reported_code_change_count = _count(review_record.get("reported_code_change_count"))
    reported_executor_code_modified_count = _count(
        review_record.get("reported_executor_code_modified_count")
    )
    reported_unreal_asset_change_count = _count(
        review_record.get("reported_unreal_asset_change_count")
    )
    reported_live_probe_count = _count(review_record.get("reported_live_probe_count"))
    reported_durable_authoring_count = _count(
        review_record.get("reported_durable_authoring_count")
    )
    reported_asset_write_count = _count(review_record.get("reported_asset_write_count"))
    reported_save_count = _count(review_record.get("reported_save_count"))
    reported_delete_rename_count = _count(review_record.get("reported_delete_rename_count"))
    reported_cleanup_count = _count(review_record.get("reported_cleanup_count"))
    reported_allowed_code_patch_review_count = (
        reported_patch_plan_review_count
        + reported_patch_risk_review_count
        + reported_no_code_change_review_count
        + reported_no_asset_change_review_count
        + reported_no_live_probe_review_count
    )
    reported_forbidden_code_patch_review_count = (
        reported_code_patch_application_started_count
        + reported_code_change_count
        + reported_executor_code_modified_count
        + reported_unreal_asset_change_count
        + reported_live_probe_count
        + reported_durable_authoring_count
        + reported_asset_write_count
        + reported_save_count
        + reported_delete_rename_count
        + reported_cleanup_count
    )
    allowed_code_patch_review_observed = bool(
        review_record_present and reported_allowed_code_patch_review_count > 0
    )
    no_forbidden_code_patch_review_claims = bool(
        review_record_present and reported_forbidden_code_patch_review_count == 0
    )
    unsafe_code_patch_review_record_count = (
        sum(
            int(_attempted(review_record.get(key)))
            for key in (
                "durable_executor_code_patch_review_started",
                "durable_executor_code_patch_review_accepted",
                "durable_executor_code_patch_application_started",
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
        + reported_forbidden_code_patch_review_count
    )
    code_patch_review_contract_defined = bool(
        requested and code_patch_plan_contract_ready
    )
    code_patch_review_record_valid = bool(
        code_patch_review_contract_defined
        and code_patch_review_inputs_satisfied
        and record_schema_matches
        and code_patch_review_scope_matches
        and explicit_code_patch_review_authorized
        and review_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_code_patch_review_observed
        and no_forbidden_code_patch_review_claims
        and unsafe_code_patch_review_record_count == 0
    )
    missing = []
    if requested:
        if not code_patch_plan_inputs_satisfied:
            missing.append("section_99_code_patch_plan_inputs_satisfied")
        if not code_patch_plan_record_valid:
            missing.append("section_99_code_patch_plan_record_valid")
        if not allowed_code_patch_plan_observed:
            missing.append("section_99_allowed_code_patch_plan_observed")
        if not no_forbidden_code_patch_plan_claims:
            missing.append("section_99_no_forbidden_code_patch_plan_claims")
        if not review_record_present:
            missing.append("durable_executor_code_patch_review_record_present")
        if not record_schema_matches:
            missing.append("durable_executor_code_patch_review_record_schema")
        if not code_patch_review_scope_matches:
            missing.append("durable_executor_code_patch_review_only_scope")
        if not explicit_code_patch_review_authorized:
            missing.append("explicit_durable_executor_code_patch_review_authorization")
        if not review_status_passed:
            missing.append("durable_executor_code_patch_review_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_code_patch_review_observed:
            missing.append("allowed_durable_executor_code_patch_review_observed")
        if not no_forbidden_code_patch_review_claims:
            missing.append("no_forbidden_durable_executor_code_patch_review_claims")
        missing.append("separate_durable_executor_code_patch_application_contract")
    code_patch_review_record_rejected = bool(
        review_record_present and not code_patch_review_record_valid
    )
    return {
        "id": "durable_executor_code_patch_review",
        "schema": DURABLE_EXECUTOR_CODE_PATCH_REVIEW_SCHEMA,
        "requested": requested,
        "code_patch_review_contract_defined": code_patch_review_contract_defined,
        "required_code_patch_review_record_schema": (
            DURABLE_EXECUTOR_CODE_PATCH_REVIEW_RECORD_SCHEMA if requested else ""
        ),
        "expected_code_patch_review_scope": (
            EXPECTED_CODE_PATCH_REVIEW_SCOPE if requested else ""
        ),
        "code_patch_plan_contract_ready": code_patch_plan_contract_ready,
        "code_patch_plan_inputs_satisfied": code_patch_plan_inputs_satisfied,
        "code_patch_plan_record_valid": code_patch_plan_record_valid,
        "allowed_code_patch_plan_observed": allowed_code_patch_plan_observed,
        "no_forbidden_code_patch_plan_claims": no_forbidden_code_patch_plan_claims,
        "code_patch_review_inputs_satisfied": code_patch_review_inputs_satisfied,
        "code_patch_review_record_present": review_record_present,
        "record_schema_matches": record_schema_matches,
        "code_patch_review_scope_matches": code_patch_review_scope_matches,
        "explicit_code_patch_review_authorized": explicit_code_patch_review_authorized,
        "review_status_passed": review_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": explicit_durable_mvp_request_reconfirmed,
        "reported_allowed_code_patch_review_count": (
            reported_allowed_code_patch_review_count
        ),
        "reported_forbidden_code_patch_review_count": (
            reported_forbidden_code_patch_review_count
        ),
        "allowed_code_patch_review_observed": allowed_code_patch_review_observed,
        "no_forbidden_code_patch_review_claims": no_forbidden_code_patch_review_claims,
        "code_patch_review_record_valid": code_patch_review_record_valid,
        "code_patch_review_record_rejected": code_patch_review_record_rejected,
        "unsafe_code_patch_review_record_count": unsafe_code_patch_review_record_count,
        "missing_code_patch_review_prerequisites": missing,
        "missing_code_patch_review_prerequisite_count": len(missing),
        "durable_executor_code_patch_review_started": False,
        "durable_executor_code_patch_review_accepted": False,
        "durable_executor_code_patch_application_started": False,
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
        "reported_patch_plan_review_count": reported_patch_plan_review_count,
        "reported_patch_risk_review_count": reported_patch_risk_review_count,
        "reported_no_code_change_review_count": reported_no_code_change_review_count,
        "reported_no_asset_change_review_count": (
            reported_no_asset_change_review_count
        ),
        "reported_no_live_probe_review_count": reported_no_live_probe_review_count,
        "reported_code_patch_application_started_count": (
            reported_code_patch_application_started_count
        ),
        "reported_code_change_count": reported_code_change_count,
        "reported_executor_code_modified_count": reported_executor_code_modified_count,
        "reported_unreal_asset_change_count": reported_unreal_asset_change_count,
        "reported_live_probe_count": reported_live_probe_count,
        "reported_durable_authoring_count": reported_durable_authoring_count,
        "reported_asset_write_count": reported_asset_write_count,
        "reported_save_count": reported_save_count,
        "reported_delete_rename_count": reported_delete_rename_count,
        "reported_cleanup_count": reported_cleanup_count,
    }


def summarize_durable_executor_code_patch_reviews(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1 for contract in requested if contract.get("code_patch_review_record_rejected")
    )
    unsafe_count = sum(
        contract.get("unsafe_code_patch_review_record_count", 0)
        for contract in requested
    )
    forbidden_review_count = sum(
        contract.get("reported_forbidden_code_patch_review_count", 0)
        for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("code_patch_review_contract_defined"))
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_review_count == 0
            and sum(1 for contract in requested if contract.get("durable_executor_code_patch_review_started")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_code_patch_review_accepted")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_code_patch_application_started")) == 0
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
        "schema": DURABLE_EXECUTOR_CODE_PATCH_REVIEW_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_code_patch_review_count": len(requested),
        "code_patch_review_contract_defined_count": sum(
            1 for contract in requested if contract.get("code_patch_review_contract_defined")
        ),
        "code_patch_plan_contract_ready_count": sum(
            1 for contract in requested if contract.get("code_patch_plan_contract_ready")
        ),
        "code_patch_plan_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("code_patch_plan_inputs_satisfied")
        ),
        "code_patch_plan_record_valid_count": sum(
            1 for contract in requested if contract.get("code_patch_plan_record_valid")
        ),
        "allowed_code_patch_plan_observed_count": sum(
            1 for contract in requested if contract.get("allowed_code_patch_plan_observed")
        ),
        "no_forbidden_code_patch_plan_claims_count": sum(
            1
            for contract in requested
            if contract.get("no_forbidden_code_patch_plan_claims")
        ),
        "code_patch_review_inputs_satisfied_count": sum(
            1
            for contract in requested
            if contract.get("code_patch_review_inputs_satisfied")
        ),
        "code_patch_review_record_present_count": sum(
            1 for contract in requested if contract.get("code_patch_review_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "code_patch_review_scope_matches_count": sum(
            1 for contract in requested if contract.get("code_patch_review_scope_matches")
        ),
        "explicit_code_patch_review_authorized_count": sum(
            1
            for contract in requested
            if contract.get("explicit_code_patch_review_authorized")
        ),
        "review_status_passed_count": sum(
            1 for contract in requested if contract.get("review_status_passed")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "explicit_durable_mvp_request_reconfirmed_count": sum(
            1
            for contract in requested
            if contract.get("explicit_durable_mvp_request_reconfirmed")
        ),
        "allowed_code_patch_review_observed_count": sum(
            1
            for contract in requested
            if contract.get("allowed_code_patch_review_observed")
        ),
        "no_forbidden_code_patch_review_claims_count": sum(
            1
            for contract in requested
            if contract.get("no_forbidden_code_patch_review_claims")
        ),
        "code_patch_review_record_valid_count": sum(
            1 for contract in requested if contract.get("code_patch_review_record_valid")
        ),
        "code_patch_review_record_rejected_count": rejected_count,
        "unsafe_code_patch_review_record_count": unsafe_count,
        "missing_code_patch_review_prerequisite_count": sum(
            contract.get("missing_code_patch_review_prerequisite_count", 0)
            for contract in requested
        ),
        "reported_allowed_code_patch_review_count": sum(
            contract.get("reported_allowed_code_patch_review_count", 0)
            for contract in requested
        ),
        "reported_forbidden_code_patch_review_count": forbidden_review_count,
        "durable_executor_code_patch_review_started_count": sum(
            1
            for contract in requested
            if contract.get("durable_executor_code_patch_review_started")
        ),
        "durable_executor_code_patch_review_accepted_count": sum(
            1
            for contract in requested
            if contract.get("durable_executor_code_patch_review_accepted")
        ),
        "durable_executor_code_patch_application_started_count": sum(
            1
            for contract in requested
            if contract.get("durable_executor_code_patch_application_started")
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
        "reported_patch_plan_review_count": sum(
            contract.get("reported_patch_plan_review_count", 0)
            for contract in requested
        ),
        "reported_patch_risk_review_count": sum(
            contract.get("reported_patch_risk_review_count", 0)
            for contract in requested
        ),
        "reported_no_code_change_review_count": sum(
            contract.get("reported_no_code_change_review_count", 0)
            for contract in requested
        ),
        "reported_no_asset_change_review_count": sum(
            contract.get("reported_no_asset_change_review_count", 0)
            for contract in requested
        ),
        "reported_no_live_probe_review_count": sum(
            contract.get("reported_no_live_probe_review_count", 0)
            for contract in requested
        ),
        "reported_code_patch_application_started_count": sum(
            contract.get("reported_code_patch_application_started_count", 0)
            for contract in requested
        ),
        "reported_code_change_count": sum(
            contract.get("reported_code_change_count", 0) for contract in requested
        ),
        "reported_executor_code_modified_count": sum(
            contract.get("reported_executor_code_modified_count", 0)
            for contract in requested
        ),
        "reported_unreal_asset_change_count": sum(
            contract.get("reported_unreal_asset_change_count", 0)
            for contract in requested
        ),
        "reported_live_probe_count": sum(
            contract.get("reported_live_probe_count", 0) for contract in requested
        ),
        "reported_durable_authoring_count": sum(
            contract.get("reported_durable_authoring_count", 0)
            for contract in requested
        ),
        "reported_asset_write_count": sum(
            contract.get("reported_asset_write_count", 0) for contract in requested
        ),
        "reported_save_count": sum(
            contract.get("reported_save_count", 0) for contract in requested
        ),
        "reported_delete_rename_count": sum(
            contract.get("reported_delete_rename_count", 0)
            for contract in requested
        ),
        "reported_cleanup_count": sum(
            contract.get("reported_cleanup_count", 0) for contract in requested
        ),
    }
