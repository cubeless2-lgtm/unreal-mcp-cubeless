#!/usr/bin/env python
"""
Section 125 durable executor authoring release promotion barrier contract.

This contract validates a future authoring-release-promotion-barrier-only record
after the durable authoring release decision record is valid. It does not start
activation readiness, activate or open the executor, enable durable authoring,
complete authoring commands, write assets, dirty packages, save, delete/rename,
cleanup, change code, probe live bridges, or dispatch live commands.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_RELEASE_PROMOTION_BARRIER_SCHEMA = (
    "section_125_durable_executor_authoring_release_promotion_barrier_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_RELEASE_PROMOTION_BARRIER_RECORD_SCHEMA = (
    "section_125_durable_executor_authoring_release_promotion_barrier_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_RELEASE_PROMOTION_BARRIER_SUMMARY_SCHEMA = (
    "section_125_durable_executor_authoring_release_promotion_barrier_summary_v1"
)
EXPECTED_RELEASE_PROMOTION_BARRIER_SCOPE = (
    "durable_executor_authoring_release_promotion_barrier_only"
)


OUTPUT_ACTION_KEYS = (
    "durable_authoring_release_promotion_barrier_started",
    "durable_authoring_release_promotion_barrier_accepted",
    "durable_executor_activation_readiness_started",
    "durable_executor_activated",
    "durable_executor_opened",
    "durable_authoring_release_decision_started",
    "durable_authoring_release_decision_accepted",
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
UNSAFE_BARRIER_RECORD_ACTION_KEYS = (
    "durable_authoring_release_promotion_barrier_started",
    "durable_authoring_release_promotion_barrier_accepted",
    "durable_executor_activation_readiness_started",
    "durable_executor_activated",
    "durable_executor_opened",
    "durable_authoring_release_decision_started",
    "durable_authoring_release_decision_accepted",
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
    "durable_authoring_release_decision_started_count",
    "durable_authoring_release_decision_accepted_count",
    "durable_authoring_release_promotion_barrier_started_count",
    "durable_authoring_release_review_started_count",
    "durable_authoring_release_review_accepted_count",
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
ALLOWED_PROMOTION_BARRIER_COUNT_KEYS = (
    "reported_promotion_barrier_gate_count",
    "reported_release_decision_revalidated_count",
    "reported_durable_authoring_still_disabled_count",
    "reported_no_completion_promotion_barrier_count",
    "reported_no_write_promotion_barrier_count",
    "reported_no_save_promotion_barrier_count",
    "reported_no_code_change_promotion_barrier_count",
    "reported_no_live_command_promotion_barrier_count",
)
FORBIDDEN_PROMOTION_BARRIER_COUNT_KEYS = (
    "reported_release_decision_count",
    "reported_release_review_count",
    "reported_final_release_readiness_count",
    "reported_final_no_save_release_count",
    "reported_command_result_readback_count",
    "reported_completion_result_acceptance_count",
    "reported_completion_count",
    "reported_executor_activation_count",
    "reported_executor_open_count",
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


def build_durable_executor_authoring_release_promotion_barrier_contract(
    requested: bool,
    release_decision_summary: Dict[str, Any],
    barrier_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    barrier_record = barrier_record or {}
    barrier_record_present = bool(barrier_record)
    release_decision_contract_ready = bool(
        requested
        and release_decision_summary.get("status") == "passed"
        and release_decision_summary.get("release_decision_contract_defined_count") == 1
        and release_decision_summary.get("release_decision_record_rejected_count") == 0
        and release_decision_summary.get("unsafe_release_decision_record_count") == 0
        and release_decision_summary.get("reported_forbidden_release_decision_count") == 0
        and all(release_decision_summary.get(key) == 0 for key in PREVIOUS_ZERO_COUNT_KEYS)
    )
    release_decision_inputs_satisfied = bool(
        release_decision_summary.get("release_decision_inputs_satisfied_count") == 1
    )
    release_decision_record_valid = bool(
        release_decision_summary.get("release_decision_record_valid_count") == 1
    )
    allowed_release_decision_observed = bool(
        release_decision_summary.get("allowed_release_decision_observed_count") == 1
    )
    no_forbidden_release_decision_claims = bool(
        release_decision_summary.get("no_forbidden_release_decision_claims_count") == 1
    )
    release_promotion_barrier_inputs_satisfied = bool(
        release_decision_inputs_satisfied
        and release_decision_record_valid
        and allowed_release_decision_observed
        and no_forbidden_release_decision_claims
    )
    record_schema_matches = bool(
        barrier_record_present
        and barrier_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_RELEASE_PROMOTION_BARRIER_RECORD_SCHEMA
    )
    release_promotion_barrier_scope_matches = bool(
        barrier_record_present
        and barrier_record.get("release_promotion_barrier_scope")
        == EXPECTED_RELEASE_PROMOTION_BARRIER_SCOPE
    )
    explicit_release_promotion_barrier_authorized = bool(
        barrier_record_present
        and barrier_record.get(
            "explicit_durable_authoring_release_promotion_barrier_authorized"
        )
        is True
    )
    promotion_barrier_status_passed = bool(
        barrier_record_present and barrier_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        barrier_record_present
        and barrier_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        barrier_record_present
        and barrier_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    allowed_counts = {
        key: _count(barrier_record.get(key))
        for key in ALLOWED_PROMOTION_BARRIER_COUNT_KEYS
    }
    forbidden_counts = {
        key: _count(barrier_record.get(key))
        for key in FORBIDDEN_PROMOTION_BARRIER_COUNT_KEYS
    }
    reported_allowed_release_promotion_barrier_count = sum(allowed_counts.values())
    reported_forbidden_release_promotion_barrier_count = sum(forbidden_counts.values())
    allowed_release_promotion_barrier_observed = bool(
        barrier_record_present and reported_allowed_release_promotion_barrier_count > 0
    )
    no_forbidden_release_promotion_barrier_claims = bool(
        barrier_record_present
        and reported_forbidden_release_promotion_barrier_count == 0
    )
    unsafe_release_promotion_barrier_record_count = (
        sum(
            int(_attempted(barrier_record.get(key)))
            for key in UNSAFE_BARRIER_RECORD_ACTION_KEYS
        )
        + reported_forbidden_release_promotion_barrier_count
    )
    release_promotion_barrier_contract_defined = bool(
        requested and release_decision_contract_ready
    )
    release_promotion_barrier_record_valid = bool(
        release_promotion_barrier_contract_defined
        and release_promotion_barrier_inputs_satisfied
        and record_schema_matches
        and release_promotion_barrier_scope_matches
        and explicit_release_promotion_barrier_authorized
        and promotion_barrier_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_release_promotion_barrier_observed
        and no_forbidden_release_promotion_barrier_claims
        and unsafe_release_promotion_barrier_record_count == 0
    )
    missing: list[str] = []
    if requested:
        if not release_decision_inputs_satisfied:
            missing.append("section_124_release_decision_inputs_satisfied")
        if not release_decision_record_valid:
            missing.append("section_124_release_decision_record_valid")
        if not allowed_release_decision_observed:
            missing.append("section_124_allowed_release_decision_observed")
        if not no_forbidden_release_decision_claims:
            missing.append("section_124_no_forbidden_release_decision_claims")
        if not barrier_record_present:
            missing.append("durable_authoring_release_promotion_barrier_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_release_promotion_barrier_record_schema")
        if not release_promotion_barrier_scope_matches:
            missing.append(
                "durable_executor_authoring_release_promotion_barrier_only_scope"
            )
        if not explicit_release_promotion_barrier_authorized:
            missing.append(
                "explicit_durable_authoring_release_promotion_barrier_authorization"
            )
        if not promotion_barrier_status_passed:
            missing.append("durable_authoring_release_promotion_barrier_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_release_promotion_barrier_observed:
            missing.append(
                "allowed_durable_authoring_release_promotion_barrier_observed"
            )
        if not no_forbidden_release_promotion_barrier_claims:
            missing.append(
                "no_forbidden_durable_authoring_release_promotion_barrier_claims"
            )
        missing.append("separate_durable_executor_activation_readiness_contract")
    release_promotion_barrier_record_rejected = bool(
        barrier_record_present and not release_promotion_barrier_record_valid
    )
    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_release_promotion_barrier",
        "schema": DURABLE_EXECUTOR_AUTHORING_RELEASE_PROMOTION_BARRIER_SCHEMA,
        "requested": requested,
        "release_promotion_barrier_contract_defined": (
            release_promotion_barrier_contract_defined
        ),
        "required_release_promotion_barrier_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_RELEASE_PROMOTION_BARRIER_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_release_promotion_barrier_scope": (
            EXPECTED_RELEASE_PROMOTION_BARRIER_SCOPE if requested else ""
        ),
        "release_decision_contract_ready": release_decision_contract_ready,
        "release_decision_inputs_satisfied": release_decision_inputs_satisfied,
        "release_decision_record_valid": release_decision_record_valid,
        "allowed_release_decision_observed": allowed_release_decision_observed,
        "no_forbidden_release_decision_claims": no_forbidden_release_decision_claims,
        "release_promotion_barrier_inputs_satisfied": (
            release_promotion_barrier_inputs_satisfied
        ),
        "release_promotion_barrier_record_present": barrier_record_present,
        "record_schema_matches": record_schema_matches,
        "release_promotion_barrier_scope_matches": (
            release_promotion_barrier_scope_matches
        ),
        "explicit_release_promotion_barrier_authorized": (
            explicit_release_promotion_barrier_authorized
        ),
        "promotion_barrier_status_passed": promotion_barrier_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "reported_allowed_release_promotion_barrier_count": (
            reported_allowed_release_promotion_barrier_count
        ),
        "reported_forbidden_release_promotion_barrier_count": (
            reported_forbidden_release_promotion_barrier_count
        ),
        "allowed_release_promotion_barrier_observed": (
            allowed_release_promotion_barrier_observed
        ),
        "no_forbidden_release_promotion_barrier_claims": (
            no_forbidden_release_promotion_barrier_claims
        ),
        "release_promotion_barrier_record_valid": (
            release_promotion_barrier_record_valid
        ),
        "release_promotion_barrier_record_rejected": (
            release_promotion_barrier_record_rejected
        ),
        "unsafe_release_promotion_barrier_record_count": (
            unsafe_release_promotion_barrier_record_count
        ),
        "missing_release_promotion_barrier_prerequisites": missing,
        "missing_release_promotion_barrier_prerequisite_count": len(missing),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract.update(allowed_counts)
    contract.update(forbidden_counts)
    return contract


def summarize_durable_executor_authoring_release_promotion_barriers(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(requested, "release_promotion_barrier_record_rejected")
    unsafe_count = _sum_count(
        requested, "unsafe_release_promotion_barrier_record_count"
    )
    forbidden_barrier_count = _sum_count(
        requested, "reported_forbidden_release_promotion_barrier_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "release_promotion_barrier_contract_defined")
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_barrier_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_RELEASE_PROMOTION_BARRIER_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_release_promotion_barrier_count": len(
            requested
        ),
        "release_promotion_barrier_contract_defined_count": _sum_truthy(
            requested, "release_promotion_barrier_contract_defined"
        ),
        "release_decision_contract_ready_count": _sum_truthy(
            requested, "release_decision_contract_ready"
        ),
        "release_decision_inputs_satisfied_count": _sum_truthy(
            requested, "release_decision_inputs_satisfied"
        ),
        "release_decision_record_valid_count": _sum_truthy(
            requested, "release_decision_record_valid"
        ),
        "allowed_release_decision_observed_count": _sum_truthy(
            requested, "allowed_release_decision_observed"
        ),
        "no_forbidden_release_decision_claims_count": _sum_truthy(
            requested, "no_forbidden_release_decision_claims"
        ),
        "release_promotion_barrier_inputs_satisfied_count": _sum_truthy(
            requested, "release_promotion_barrier_inputs_satisfied"
        ),
        "release_promotion_barrier_record_present_count": _sum_truthy(
            requested, "release_promotion_barrier_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "release_promotion_barrier_scope_matches_count": _sum_truthy(
            requested, "release_promotion_barrier_scope_matches"
        ),
        "explicit_release_promotion_barrier_authorized_count": _sum_truthy(
            requested, "explicit_release_promotion_barrier_authorized"
        ),
        "promotion_barrier_status_passed_count": _sum_truthy(
            requested, "promotion_barrier_status_passed"
        ),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "allowed_release_promotion_barrier_observed_count": _sum_truthy(
            requested, "allowed_release_promotion_barrier_observed"
        ),
        "no_forbidden_release_promotion_barrier_claims_count": _sum_truthy(
            requested, "no_forbidden_release_promotion_barrier_claims"
        ),
        "release_promotion_barrier_record_valid_count": _sum_truthy(
            requested, "release_promotion_barrier_record_valid"
        ),
        "release_promotion_barrier_record_rejected_count": rejected_count,
        "unsafe_release_promotion_barrier_record_count": unsafe_count,
        "missing_release_promotion_barrier_prerequisite_count": _sum_count(
            requested, "missing_release_promotion_barrier_prerequisite_count"
        ),
        "reported_allowed_release_promotion_barrier_count": _sum_count(
            requested, "reported_allowed_release_promotion_barrier_count"
        ),
        "reported_forbidden_release_promotion_barrier_count": forbidden_barrier_count,
    }
    summary.update({f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS})
    summary.update(
        {key: _sum_count(requested, key) for key in ALLOWED_PROMOTION_BARRIER_COUNT_KEYS}
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in FORBIDDEN_PROMOTION_BARRIER_COUNT_KEYS
        }
    )
    return summary
