#!/usr/bin/env python
"""
Section 159 durable executor authoring open-after-activation-readiness-after-promotion-barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract.

This contract validates a future authoring-open-after-activation-readiness-after-promotion-barrier-after-decision-after-review-after-readiness-after-no-save-release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness-only
record after the durable authoring activation readiness-after-promotion-barrier
record is valid. It does not activate or open the executor, start authoring
enablement, enable durable authoring, complete
authoring commands, write assets, dirty packages, save, delete/rename, cleanup,
change code, probe live bridges, or dispatch live commands.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_OPEN_AFTER_ACTIVATION_READINESS_AFTER_PROMOTION_BARRIER_SCHEMA = (
    "section_159_durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_OPEN_AFTER_ACTIVATION_READINESS_AFTER_PROMOTION_BARRIER_RECORD_SCHEMA = (
    "section_159_durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_OPEN_AFTER_ACTIVATION_READINESS_AFTER_PROMOTION_BARRIER_SUMMARY_SCHEMA = (
    "section_159_durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary_v1"
)
EXPECTED_OPEN_SCOPE = "durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_only"


OUTPUT_ACTION_KEYS = (
    "durable_executor_open_contract_started",
    "durable_executor_open_contract_accepted",
    "durable_executor_open_performed",
    "durable_executor_activated",
    "durable_executor_opened",
    "durable_authoring_enable_started",
    "durable_executor_activation_readiness_started",
    "durable_executor_activation_readiness_accepted",
    "durable_authoring_release_promotion_barrier_started",
    "durable_authoring_release_promotion_barrier_accepted",
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
UNSAFE_OPEN_RECORD_ACTION_KEYS = (
    "durable_executor_open_contract_started",
    "durable_executor_open_contract_accepted",
    "durable_executor_open_performed",
    "durable_executor_activated",
    "durable_executor_opened",
    "durable_authoring_enable_started",
    "durable_executor_activation_readiness_started",
    "durable_executor_activation_readiness_accepted",
    "durable_authoring_release_promotion_barrier_started",
    "durable_authoring_release_promotion_barrier_accepted",
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
    "durable_authoring_release_promotion_barrier_started_count",
    "durable_authoring_release_promotion_barrier_accepted_count",
    "durable_executor_activation_readiness_started_count",
    "durable_executor_activation_readiness_accepted_count",
    "durable_executor_open_contract_started_count",
    "durable_executor_activated_count",
    "durable_executor_opened_count",
    "durable_authoring_release_decision_started_count",
    "durable_authoring_release_decision_accepted_count",
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
ALLOWED_OPEN_COUNT_KEYS = (
    "reported_executor_open_gate_count",
    "reported_activation_readiness_revalidated_count",
    "reported_promotion_barrier_revalidated_count",
    "reported_durable_authoring_still_disabled_count",
    "reported_no_completion_open_count",
    "reported_no_write_open_count",
    "reported_no_save_open_count",
    "reported_no_code_change_open_count",
    "reported_no_live_command_open_count",
)
FORBIDDEN_OPEN_COUNT_KEYS = (
    "reported_activation_readiness_count",
    "reported_release_promotion_barrier_count",
    "reported_release_decision_count",
    "reported_release_review_count",
    "reported_final_release_readiness_count",
    "reported_final_no_save_release_count",
    "reported_command_result_readback_count",
    "reported_completion_result_acceptance_count",
    "reported_completion_count",
    "reported_executor_activation_count",
    "reported_executor_open_count",
    "reported_durable_authoring_enable_count",
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


def build_durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_contract(
    requested: bool,
    activation_readiness_after_promotion_barrier_summary: Dict[str, Any],
    open_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    open_record = open_record or {}
    open_record_present = bool(open_record)
    activation_readiness_contract_ready = bool(
        requested
        and activation_readiness_after_promotion_barrier_summary.get("status") == "passed"
        and activation_readiness_after_promotion_barrier_summary.get(
            "activation_readiness_contract_defined_count"
        )
        == 1
        and activation_readiness_after_promotion_barrier_summary.get("activation_readiness_record_rejected_count")
        == 0
        and activation_readiness_after_promotion_barrier_summary.get("unsafe_activation_readiness_record_count")
        == 0
        and activation_readiness_after_promotion_barrier_summary.get(
            "reported_forbidden_activation_readiness_count"
        )
        == 0
        and all(
            activation_readiness_after_promotion_barrier_summary.get(key) == 0
            for key in PREVIOUS_ZERO_COUNT_KEYS
        )
    )
    activation_readiness_inputs_satisfied = bool(
        activation_readiness_after_promotion_barrier_summary.get("activation_readiness_inputs_satisfied_count")
        == 1
    )
    activation_readiness_record_valid = bool(
        activation_readiness_after_promotion_barrier_summary.get("activation_readiness_record_valid_count") == 1
    )
    allowed_activation_readiness_observed = bool(
        activation_readiness_after_promotion_barrier_summary.get("allowed_activation_readiness_observed_count")
        == 1
    )
    no_forbidden_activation_readiness_claims = bool(
        activation_readiness_after_promotion_barrier_summary.get("no_forbidden_activation_readiness_claims_count")
        == 1
    )
    open_inputs_satisfied = bool(
        activation_readiness_inputs_satisfied
        and activation_readiness_record_valid
        and allowed_activation_readiness_observed
        and no_forbidden_activation_readiness_claims
    )
    record_schema_matches = bool(
        open_record_present
        and open_record.get("schema") == DURABLE_EXECUTOR_AUTHORING_OPEN_AFTER_ACTIVATION_READINESS_AFTER_PROMOTION_BARRIER_RECORD_SCHEMA
    )
    open_scope_matches = bool(
        open_record_present and open_record.get("open_scope") == EXPECTED_OPEN_SCOPE
    )
    explicit_open_authorized = bool(
        open_record_present
        and open_record.get("explicit_durable_executor_authoring_open_authorized")
        is True
    )
    open_status_passed = bool(
        open_record_present and open_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        open_record_present
        and open_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        open_record_present
        and open_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    allowed_counts = {key: _count(open_record.get(key)) for key in ALLOWED_OPEN_COUNT_KEYS}
    forbidden_counts = {key: _count(open_record.get(key)) for key in FORBIDDEN_OPEN_COUNT_KEYS}
    reported_allowed_open_count = sum(allowed_counts.values())
    reported_forbidden_open_count = sum(forbidden_counts.values())
    allowed_open_observed = bool(open_record_present and reported_allowed_open_count > 0)
    no_forbidden_open_claims = bool(
        open_record_present and reported_forbidden_open_count == 0
    )
    unsafe_open_record_count = (
        sum(int(_attempted(open_record.get(key))) for key in UNSAFE_OPEN_RECORD_ACTION_KEYS)
        + reported_forbidden_open_count
    )
    open_contract_defined = bool(requested and activation_readiness_contract_ready)
    open_record_valid = bool(
        open_contract_defined
        and open_inputs_satisfied
        and record_schema_matches
        and open_scope_matches
        and explicit_open_authorized
        and open_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_open_observed
        and no_forbidden_open_claims
        and unsafe_open_record_count == 0
    )
    missing: list[str] = []
    if requested:
        if not activation_readiness_inputs_satisfied:
            missing.append("section_158_activation_readiness_inputs_satisfied")
        if not activation_readiness_record_valid:
            missing.append("section_158_activation_readiness_record_valid")
        if not allowed_activation_readiness_observed:
            missing.append("section_158_allowed_activation_readiness_observed")
        if not no_forbidden_activation_readiness_claims:
            missing.append("section_158_no_forbidden_activation_readiness_claims")
        if not open_record_present:
            missing.append("durable_executor_authoring_open_record_present")
        if not record_schema_matches:
            missing.append("durable_executor_authoring_open_record_schema")
        if not open_scope_matches:
            missing.append("durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_only_scope")
        if not explicit_open_authorized:
            missing.append("explicit_durable_executor_authoring_open_authorization")
        if not open_status_passed:
            missing.append("durable_executor_authoring_open_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_open_observed:
            missing.append("allowed_durable_executor_authoring_open_observed")
        if not no_forbidden_open_claims:
            missing.append("no_forbidden_durable_executor_authoring_open_claims")
        missing.append("separate_durable_authoring_enable_after_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract")
    open_record_rejected = bool(open_record_present and not open_record_valid)
    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness",
        "schema": DURABLE_EXECUTOR_AUTHORING_OPEN_AFTER_ACTIVATION_READINESS_AFTER_PROMOTION_BARRIER_SCHEMA,
        "requested": requested,
        "open_contract_defined": open_contract_defined,
        "required_open_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_OPEN_AFTER_ACTIVATION_READINESS_AFTER_PROMOTION_BARRIER_RECORD_SCHEMA if requested else ""
        ),
        "expected_open_scope": EXPECTED_OPEN_SCOPE if requested else "",
        "activation_readiness_contract_ready": (
            activation_readiness_contract_ready
        ),
        "activation_readiness_inputs_satisfied": (
            activation_readiness_inputs_satisfied
        ),
        "activation_readiness_record_valid": activation_readiness_record_valid,
        "allowed_activation_readiness_observed": (
            allowed_activation_readiness_observed
        ),
        "no_forbidden_activation_readiness_claims": (
            no_forbidden_activation_readiness_claims
        ),
        "open_inputs_satisfied": open_inputs_satisfied,
        "open_record_present": open_record_present,
        "record_schema_matches": record_schema_matches,
        "open_scope_matches": open_scope_matches,
        "explicit_open_authorized": explicit_open_authorized,
        "open_status_passed": open_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "reported_allowed_open_count": reported_allowed_open_count,
        "reported_forbidden_open_count": reported_forbidden_open_count,
        "allowed_open_observed": allowed_open_observed,
        "no_forbidden_open_claims": no_forbidden_open_claims,
        "open_record_valid": open_record_valid,
        "open_record_rejected": open_record_rejected,
        "unsafe_open_record_count": unsafe_open_record_count,
        "missing_open_prerequisites": missing,
        "missing_open_prerequisite_count": len(missing),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract.update(allowed_counts)
    contract.update(forbidden_counts)
    return contract


def summarize_durable_executor_authoring_opens_after_activation_readiness_after_promotion_barrier(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(requested, "open_record_rejected")
    unsafe_count = _sum_count(requested, "unsafe_open_record_count")
    forbidden_open_count = _sum_count(requested, "reported_forbidden_open_count")
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "open_contract_defined") == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_open_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_OPEN_AFTER_ACTIVATION_READINESS_AFTER_PROMOTION_BARRIER_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_open_after_activation_readiness_after_promotion_barrier_after_decision_after_review_after_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": len(requested),
        "open_contract_defined_count": _sum_truthy(
            requested, "open_contract_defined"
        ),
        "activation_readiness_contract_ready_count": _sum_truthy(
            requested, "activation_readiness_contract_ready"
        ),
        "activation_readiness_inputs_satisfied_count": _sum_truthy(
            requested, "activation_readiness_inputs_satisfied"
        ),
        "activation_readiness_record_valid_count": _sum_truthy(
            requested, "activation_readiness_record_valid"
        ),
        "allowed_activation_readiness_observed_count": _sum_truthy(
            requested, "allowed_activation_readiness_observed"
        ),
        "no_forbidden_activation_readiness_claims_count": _sum_truthy(
            requested, "no_forbidden_activation_readiness_claims"
        ),
        "open_inputs_satisfied_count": _sum_truthy(
            requested, "open_inputs_satisfied"
        ),
        "open_record_present_count": _sum_truthy(requested, "open_record_present"),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "open_scope_matches_count": _sum_truthy(requested, "open_scope_matches"),
        "explicit_open_authorized_count": _sum_truthy(
            requested, "explicit_open_authorized"
        ),
        "open_status_passed_count": _sum_truthy(requested, "open_status_passed"),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "allowed_open_observed_count": _sum_truthy(
            requested, "allowed_open_observed"
        ),
        "no_forbidden_open_claims_count": _sum_truthy(
            requested, "no_forbidden_open_claims"
        ),
        "open_record_valid_count": _sum_truthy(requested, "open_record_valid"),
        "open_record_rejected_count": rejected_count,
        "unsafe_open_record_count": unsafe_count,
        "missing_open_prerequisite_count": _sum_count(
            requested, "missing_open_prerequisite_count"
        ),
        "reported_allowed_open_count": _sum_count(
            requested, "reported_allowed_open_count"
        ),
        "reported_forbidden_open_count": forbidden_open_count,
    }
    summary.update({f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS})
    summary.update({key: _sum_count(requested, key) for key in ALLOWED_OPEN_COUNT_KEYS})
    summary.update({key: _sum_count(requested, key) for key in FORBIDDEN_OPEN_COUNT_KEYS})
    return summary
