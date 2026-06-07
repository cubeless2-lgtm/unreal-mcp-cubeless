#!/usr/bin/env python
"""
Section 140 durable executor authoring release decision-after-review contract.

This contract validates a future release-decision-only record after the durable
authoring release review-after-readiness record is valid. It does not accept
release decision execution, promotion barrier start, durable authoring
readiness, completion, asset writes, dirty packages, save, delete/rename,
cleanup, code changes, live probes, live commands, or durable authoring
enablement.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_AFTER_REVIEW_SCHEMA = (
    "section_140_durable_executor_authoring_release_decision_after_review_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_AFTER_REVIEW_RECORD_SCHEMA = (
    "section_140_durable_executor_authoring_release_decision_after_review_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_AFTER_REVIEW_SUMMARY_SCHEMA = (
    "section_140_durable_executor_authoring_release_decision_after_review_summary_v1"
)
EXPECTED_RELEASE_DECISION_SCOPE = (
    "durable_executor_authoring_release_decision_after_review_only"
)


OUTPUT_ACTION_KEYS = (
    "durable_authoring_release_decision_started",
    "durable_authoring_release_decision_accepted",
    "durable_authoring_release_promotion_barrier_started",
    "durable_authoring_release_review_started",
    "durable_authoring_release_review_accepted",
    "durable_authoring_final_release_readiness_started",
    "durable_authoring_final_release_ready",
    "durable_authoring_final_no_save_release_accepted",
    "durable_authoring_command_result_readback_accepted",
    "durable_authoring_command_completion_result_accepted",
    "durable_authoring_command_completed",
    "asset_write_performed",
    "package_dirty_marked",
    "durable_authoring_enabled",
    "durable_authoring_allowed",
    "code_change_performed",
    "executor_code_modified",
    "unreal_asset_modified",
    "live_bridge_probe_started",
    "save_delete_rename_allowed",
    "cleanup_allowed",
    "live_command_dispatched",
    "live_command_executed",
)
UNSAFE_RELEASE_DECISION_RECORD_ACTION_KEYS = (
    "durable_authoring_release_decision_started",
    "durable_authoring_release_decision_accepted",
    "durable_authoring_release_promotion_barrier_started",
    "durable_authoring_release_review_started",
    "durable_authoring_release_review_accepted",
    "durable_authoring_final_release_readiness_started",
    "durable_authoring_final_release_ready",
    "durable_authoring_final_no_save_release_accepted",
    "durable_authoring_command_result_readback_accepted",
    "durable_authoring_command_completion_result_accepted",
    "durable_authoring_command_completed",
    "asset_write_performed",
    "package_dirty_marked",
    "durable_authoring_enabled",
    "durable_authoring_allowed",
    "code_change_performed",
    "executor_code_modified",
    "unreal_asset_modified",
    "live_bridge_probe_started",
    "save_asset_executed",
    "delete_asset_authorized",
    "rename_asset_authorized",
    "cleanup_authorized",
    "live_command_dispatch_performed",
    "live_command_dispatched",
    "live_command_execution_performed",
    "live_command_executed",
)
PREVIOUS_ZERO_COUNT_KEYS = (
    "durable_authoring_release_review_started_count",
    "durable_authoring_release_review_accepted_count",
    "durable_authoring_release_decision_started_count",
    "durable_authoring_final_release_readiness_started_count",
    "durable_authoring_final_release_ready_count",
    "durable_authoring_final_no_save_release_accepted_count",
    "durable_authoring_command_result_readback_accepted_count",
    "durable_authoring_command_completion_result_accepted_count",
    "durable_authoring_command_completed_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
    "durable_authoring_enabled_count",
    "durable_authoring_allowed_count",
    "code_change_performed_count",
    "executor_code_modified_count",
    "unreal_asset_modified_count",
    "live_bridge_probe_started_count",
    "save_delete_rename_allowed_count",
    "cleanup_allowed_count",
    "live_command_dispatched_count",
    "live_command_executed_count",
)
ALLOWED_RELEASE_DECISION_COUNT_KEYS = (
    "reported_release_decision_gate_count",
    "reported_release_review_revalidated_count",
    "reported_durable_authoring_still_disabled_count",
    "reported_no_completion_release_decision_count",
    "reported_no_write_release_decision_count",
    "reported_no_save_release_decision_count",
    "reported_no_code_change_release_decision_count",
    "reported_no_live_command_release_decision_count",
)
FORBIDDEN_RELEASE_DECISION_COUNT_KEYS = (
    "reported_release_review_count",
    "reported_final_release_readiness_count",
    "reported_final_no_save_release_count",
    "reported_command_result_readback_count",
    "reported_completion_result_acceptance_count",
    "reported_completion_count",
    "reported_asset_write_count",
    "reported_package_dirty_count",
    "reported_save_count",
    "reported_delete_rename_count",
    "reported_cleanup_count",
    "reported_durable_authoring_count",
    "reported_code_change_count",
    "reported_live_command_count",
)


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


def _sum_truthy(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(contract.get(key, 0) for contract in contracts)


def build_durable_executor_authoring_release_decision_after_review_contract(
    requested: bool,
    release_review_after_readiness_summary: Dict[str, Any],
    decision_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    decision_record = decision_record or {}
    decision_record_present = bool(decision_record)
    release_review_contract_ready = bool(
        requested
        and release_review_after_readiness_summary.get("status") == "passed"
        and release_review_after_readiness_summary.get(
            "release_review_contract_defined_count"
        )
        == 1
        and release_review_after_readiness_summary.get(
            "release_review_record_rejected_count"
        )
        == 0
        and release_review_after_readiness_summary.get(
            "unsafe_release_review_record_count"
        )
        == 0
        and release_review_after_readiness_summary.get(
            "reported_forbidden_release_review_count"
        )
        == 0
        and all(
            release_review_after_readiness_summary.get(key) == 0
            for key in PREVIOUS_ZERO_COUNT_KEYS
        )
    )
    release_review_inputs_satisfied = bool(
        release_review_after_readiness_summary.get(
            "release_review_inputs_satisfied_count"
        )
        == 1
    )
    release_review_record_valid = bool(
        release_review_after_readiness_summary.get("release_review_record_valid_count")
        == 1
    )
    allowed_release_review_observed = bool(
        release_review_after_readiness_summary.get(
            "allowed_release_review_observed_count"
        )
        == 1
    )
    no_forbidden_release_review_claims = bool(
        release_review_after_readiness_summary.get(
            "no_forbidden_release_review_claims_count"
        )
        == 1
    )
    release_decision_inputs_satisfied = bool(
        release_review_inputs_satisfied
        and release_review_record_valid
        and allowed_release_review_observed
        and no_forbidden_release_review_claims
    )
    record_schema_matches = bool(
        decision_record_present
        and decision_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_AFTER_REVIEW_RECORD_SCHEMA
    )
    release_decision_scope_matches = bool(
        decision_record_present
        and decision_record.get("release_decision_scope")
        == EXPECTED_RELEASE_DECISION_SCOPE
    )
    explicit_release_decision_authorized = bool(
        decision_record_present
        and decision_record.get(
            "explicit_durable_authoring_release_decision_authorized"
        )
        is True
    )
    release_decision_status_passed = bool(
        decision_record_present and decision_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        decision_record_present
        and decision_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        decision_record_present
        and decision_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    allowed_counts = {
        key: _count(decision_record.get(key))
        for key in ALLOWED_RELEASE_DECISION_COUNT_KEYS
    }
    forbidden_counts = {
        key: _count(decision_record.get(key))
        for key in FORBIDDEN_RELEASE_DECISION_COUNT_KEYS
    }
    reported_allowed_release_decision_count = sum(allowed_counts.values())
    reported_forbidden_release_decision_count = sum(forbidden_counts.values())
    allowed_release_decision_observed = bool(
        decision_record_present and reported_allowed_release_decision_count > 0
    )
    no_forbidden_release_decision_claims = bool(
        decision_record_present and reported_forbidden_release_decision_count == 0
    )
    unsafe_release_decision_record_count = (
        sum(
            int(_attempted(decision_record.get(key)))
            for key in UNSAFE_RELEASE_DECISION_RECORD_ACTION_KEYS
        )
        + reported_forbidden_release_decision_count
    )
    release_decision_contract_defined = bool(
        requested and release_review_contract_ready
    )
    release_decision_record_valid = bool(
        release_decision_contract_defined
        and release_decision_inputs_satisfied
        and record_schema_matches
        and release_decision_scope_matches
        and explicit_release_decision_authorized
        and release_decision_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_release_decision_observed
        and no_forbidden_release_decision_claims
        and unsafe_release_decision_record_count == 0
    )
    missing: list[str] = []
    if requested:
        if not release_review_inputs_satisfied:
            missing.append("section_139_release_review_inputs_satisfied")
        if not release_review_record_valid:
            missing.append("section_139_release_review_record_valid")
        if not allowed_release_review_observed:
            missing.append("section_139_allowed_release_review_observed")
        if not no_forbidden_release_review_claims:
            missing.append("section_139_no_forbidden_release_review_claims")
        if not decision_record_present:
            missing.append("durable_authoring_release_decision_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_release_decision_record_schema")
        if not release_decision_scope_matches:
            missing.append(
                "durable_executor_authoring_release_decision_after_review_only_scope"
            )
        if not explicit_release_decision_authorized:
            missing.append(
                "explicit_durable_authoring_release_decision_authorization"
            )
        if not release_decision_status_passed:
            missing.append("durable_authoring_release_decision_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_release_decision_observed:
            missing.append("allowed_durable_authoring_release_decision_observed")
        if not no_forbidden_release_decision_claims:
            missing.append("no_forbidden_durable_authoring_release_decision_claims")
        missing.append(
            "separate_durable_authoring_release_promotion_barrier_after_decision_contract"
        )
    release_decision_record_rejected = bool(
        decision_record_present and not release_decision_record_valid
    )
    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_release_decision_after_review",
        "schema": DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_AFTER_REVIEW_SCHEMA,
        "requested": requested,
        "release_decision_contract_defined": release_decision_contract_defined,
        "required_release_decision_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_AFTER_REVIEW_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_release_decision_scope": (
            EXPECTED_RELEASE_DECISION_SCOPE if requested else ""
        ),
        "release_review_contract_ready": release_review_contract_ready,
        "release_review_inputs_satisfied": release_review_inputs_satisfied,
        "release_review_record_valid": release_review_record_valid,
        "allowed_release_review_observed": allowed_release_review_observed,
        "no_forbidden_release_review_claims": no_forbidden_release_review_claims,
        "release_decision_inputs_satisfied": release_decision_inputs_satisfied,
        "release_decision_record_present": decision_record_present,
        "record_schema_matches": record_schema_matches,
        "release_decision_scope_matches": release_decision_scope_matches,
        "explicit_release_decision_authorized": explicit_release_decision_authorized,
        "release_decision_status_passed": release_decision_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "reported_allowed_release_decision_count": (
            reported_allowed_release_decision_count
        ),
        "reported_forbidden_release_decision_count": (
            reported_forbidden_release_decision_count
        ),
        "allowed_release_decision_observed": allowed_release_decision_observed,
        "no_forbidden_release_decision_claims": no_forbidden_release_decision_claims,
        "release_decision_record_valid": release_decision_record_valid,
        "release_decision_record_rejected": release_decision_record_rejected,
        "unsafe_release_decision_record_count": unsafe_release_decision_record_count,
        "missing_release_decision_prerequisites": missing,
        "missing_release_decision_prerequisite_count": len(missing),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract.update(allowed_counts)
    contract.update(forbidden_counts)
    return contract


def summarize_durable_executor_authoring_release_decisions_after_review(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(requested, "release_decision_record_rejected")
    unsafe_count = _sum_count(requested, "unsafe_release_decision_record_count")
    forbidden_decision_count = _sum_count(
        requested, "reported_forbidden_release_decision_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "release_decision_contract_defined")
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_decision_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_RELEASE_DECISION_AFTER_REVIEW_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_release_decision_after_review_count": len(
            requested
        ),
        "release_decision_contract_defined_count": _sum_truthy(
            requested, "release_decision_contract_defined"
        ),
        "release_review_contract_ready_count": _sum_truthy(
            requested, "release_review_contract_ready"
        ),
        "release_review_inputs_satisfied_count": _sum_truthy(
            requested, "release_review_inputs_satisfied"
        ),
        "release_review_record_valid_count": _sum_truthy(
            requested, "release_review_record_valid"
        ),
        "allowed_release_review_observed_count": _sum_truthy(
            requested, "allowed_release_review_observed"
        ),
        "no_forbidden_release_review_claims_count": _sum_truthy(
            requested, "no_forbidden_release_review_claims"
        ),
        "release_decision_inputs_satisfied_count": _sum_truthy(
            requested, "release_decision_inputs_satisfied"
        ),
        "release_decision_record_present_count": _sum_truthy(
            requested, "release_decision_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "release_decision_scope_matches_count": _sum_truthy(
            requested, "release_decision_scope_matches"
        ),
        "explicit_release_decision_authorized_count": _sum_truthy(
            requested, "explicit_release_decision_authorized"
        ),
        "release_decision_status_passed_count": _sum_truthy(
            requested, "release_decision_status_passed"
        ),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "allowed_release_decision_observed_count": _sum_truthy(
            requested, "allowed_release_decision_observed"
        ),
        "no_forbidden_release_decision_claims_count": _sum_truthy(
            requested, "no_forbidden_release_decision_claims"
        ),
        "release_decision_record_valid_count": _sum_truthy(
            requested, "release_decision_record_valid"
        ),
        "release_decision_record_rejected_count": rejected_count,
        "unsafe_release_decision_record_count": unsafe_count,
        "missing_release_decision_prerequisite_count": _sum_count(
            requested, "missing_release_decision_prerequisite_count"
        ),
        "reported_allowed_release_decision_count": _sum_count(
            requested, "reported_allowed_release_decision_count"
        ),
        "reported_forbidden_release_decision_count": forbidden_decision_count,
    }
    summary.update(
        {f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS}
    )
    summary.update(
        {key: _sum_count(requested, key) for key in ALLOWED_RELEASE_DECISION_COUNT_KEYS}
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in FORBIDDEN_RELEASE_DECISION_COUNT_KEYS
        }
    )
    return summary
