#!/usr/bin/env python
"""
Section 153 durable executor authoring final no-save release-after-readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness contract.

This contract validates a future final-no-save-release-only record after the
durable authoring command result readback-after-result-after-application-after-decision-after-evidence-after-execution-after-dispatch-after-command-after-enable-after-open-after-activation-readiness record is valid. It does
not accept durable authoring completion, asset writes, dirty packages, save,
delete/rename, cleanup, code changes, live probes, live commands, or durable
authoring enablement.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_AFTER_READBACK_AFTER_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SCHEMA = (
    "section_153_durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_AFTER_READBACK_AFTER_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_RECORD_SCHEMA = (
    "section_153_durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_AFTER_READBACK_AFTER_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SUMMARY_SCHEMA = (
    "section_153_durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary_v1"
)
EXPECTED_FINAL_NO_SAVE_RELEASE_SCOPE = (
    "durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_only"
)


OUTPUT_ACTION_KEYS = (
    "durable_authoring_final_no_save_release_accepted",
    "durable_authoring_final_release_readiness_started",
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
UNSAFE_FINAL_NO_SAVE_RELEASE_RECORD_ACTION_KEYS = (
    "durable_authoring_final_no_save_release_accepted",
    "durable_authoring_final_release_readiness_started",
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
ALLOWED_FINAL_NO_SAVE_RELEASE_COUNT_KEYS = (
    "reported_no_completion_release_count",
    "reported_no_write_release_count",
    "reported_no_save_release_count",
    "reported_readback_revalidated_count",
    "reported_no_code_change_release_count",
    "reported_no_live_command_release_count",
)
FORBIDDEN_FINAL_NO_SAVE_RELEASE_COUNT_KEYS = (
    "reported_completion_release_count",
    "reported_asset_write_release_count",
    "reported_package_dirty_release_count",
    "reported_save_release_count",
    "reported_delete_rename_release_count",
    "reported_cleanup_release_count",
    "reported_durable_authoring_release_count",
    "reported_code_change_release_count",
    "reported_live_command_release_count",
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


def build_durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract(
    requested: bool,
    result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary: Dict[str, Any],
    final_no_save_release_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    final_no_save_release_record = final_no_save_release_record or {}
    release_record_present = bool(final_no_save_release_record)
    readback_contract_ready = bool(
        requested
        and result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get("status") == "passed"
        and result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get("readback_contract_defined_count")
        == 1
        and result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get("readback_record_rejected_count")
        == 0
        and result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get("unsafe_readback_record_count")
        == 0
        and result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get("reported_forbidden_readback_count")
        == 0
        and all(
            result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get(key) == 0
            for key in PREVIOUS_ZERO_COUNT_KEYS
        )
    )
    readback_inputs_satisfied = bool(
        result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get("readback_inputs_satisfied_count")
        == 1
    )
    readback_record_valid = bool(
        result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get("readback_record_valid_count") == 1
    )
    allowed_readback_observed = bool(
        result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get("allowed_readback_observed_count")
        == 1
    )
    no_forbidden_readbacks = bool(
        result_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_summary.get("no_forbidden_readbacks_count") == 1
    )
    final_no_save_release_inputs_satisfied = bool(
        readback_inputs_satisfied
        and readback_record_valid
        and allowed_readback_observed
        and no_forbidden_readbacks
    )
    record_schema_matches = bool(
        release_record_present
        and final_no_save_release_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_AFTER_READBACK_AFTER_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_RECORD_SCHEMA
    )
    final_no_save_release_scope_matches = bool(
        release_record_present
        and final_no_save_release_record.get("final_no_save_release_scope")
        == EXPECTED_FINAL_NO_SAVE_RELEASE_SCOPE
    )
    explicit_final_no_save_release_authorized = bool(
        release_record_present
        and final_no_save_release_record.get(
            "explicit_durable_authoring_final_no_save_release_authorized"
        )
        is True
    )
    final_no_save_release_status_passed = bool(
        release_record_present
        and final_no_save_release_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        release_record_present
        and final_no_save_release_record.get("operator_reconfirmed_no_save_delete_rename")
        is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        release_record_present
        and final_no_save_release_record.get("explicit_durable_mvp_request_reconfirmed")
        is True
    )
    allowed_counts = {
        key: _count(final_no_save_release_record.get(key))
        for key in ALLOWED_FINAL_NO_SAVE_RELEASE_COUNT_KEYS
    }
    forbidden_counts = {
        key: _count(final_no_save_release_record.get(key))
        for key in FORBIDDEN_FINAL_NO_SAVE_RELEASE_COUNT_KEYS
    }
    reported_allowed_final_no_save_release_count = sum(allowed_counts.values())
    reported_forbidden_final_no_save_release_count = sum(forbidden_counts.values())
    allowed_final_no_save_release_observed = bool(
        release_record_present and reported_allowed_final_no_save_release_count > 0
    )
    no_forbidden_final_no_save_releases = bool(
        release_record_present and reported_forbidden_final_no_save_release_count == 0
    )
    unsafe_final_no_save_release_record_count = (
        sum(
            int(_attempted(final_no_save_release_record.get(key)))
            for key in UNSAFE_FINAL_NO_SAVE_RELEASE_RECORD_ACTION_KEYS
        )
        + reported_forbidden_final_no_save_release_count
    )
    final_no_save_release_contract_defined = bool(
        requested and readback_contract_ready
    )
    final_no_save_release_record_valid = bool(
        final_no_save_release_contract_defined
        and final_no_save_release_inputs_satisfied
        and record_schema_matches
        and final_no_save_release_scope_matches
        and explicit_final_no_save_release_authorized
        and final_no_save_release_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_final_no_save_release_observed
        and no_forbidden_final_no_save_releases
        and unsafe_final_no_save_release_record_count == 0
    )
    missing: list[str] = []
    if requested:
        if not readback_inputs_satisfied:
            missing.append("section_152_readback_inputs_satisfied")
        if not readback_record_valid:
            missing.append("section_152_readback_record_valid")
        if not allowed_readback_observed:
            missing.append("section_152_allowed_readback_observed")
        if not no_forbidden_readbacks:
            missing.append("section_152_no_forbidden_readbacks")
        if not release_record_present:
            missing.append("durable_authoring_final_no_save_release_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_final_no_save_release_record_schema")
        if not final_no_save_release_scope_matches:
            missing.append(
                "durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_only_scope"
            )
        if not explicit_final_no_save_release_authorized:
            missing.append(
                "explicit_durable_authoring_final_no_save_release_authorization"
            )
        if not final_no_save_release_status_passed:
            missing.append("durable_authoring_final_no_save_release_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_final_no_save_release_observed:
            missing.append("allowed_durable_authoring_final_no_save_release_observed")
        if not no_forbidden_final_no_save_releases:
            missing.append("no_forbidden_durable_authoring_final_no_save_releases")
        missing.append(
            "separate_durable_authoring_final_release_readiness_after_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_contract"
        )
    final_no_save_release_record_rejected = bool(
        release_record_present and not final_no_save_release_record_valid
    )
    contract: Dict[str, Any] = {
        "id": "durable_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness",
        "schema": DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_AFTER_READBACK_AFTER_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SCHEMA,
        "requested": requested,
        "final_no_save_release_contract_defined": (
            final_no_save_release_contract_defined
        ),
        "required_final_no_save_release_record_schema": (
            DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_AFTER_READBACK_AFTER_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_final_no_save_release_scope": (
            EXPECTED_FINAL_NO_SAVE_RELEASE_SCOPE if requested else ""
        ),
        "readback_contract_ready": readback_contract_ready,
        "readback_inputs_satisfied": readback_inputs_satisfied,
        "readback_record_valid": readback_record_valid,
        "allowed_readback_observed": allowed_readback_observed,
        "no_forbidden_readbacks": no_forbidden_readbacks,
        "final_no_save_release_inputs_satisfied": (
            final_no_save_release_inputs_satisfied
        ),
        "final_no_save_release_record_present": release_record_present,
        "record_schema_matches": record_schema_matches,
        "final_no_save_release_scope_matches": final_no_save_release_scope_matches,
        "explicit_final_no_save_release_authorized": (
            explicit_final_no_save_release_authorized
        ),
        "final_no_save_release_status_passed": final_no_save_release_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "reported_allowed_final_no_save_release_count": (
            reported_allowed_final_no_save_release_count
        ),
        "reported_forbidden_final_no_save_release_count": (
            reported_forbidden_final_no_save_release_count
        ),
        "allowed_final_no_save_release_observed": (
            allowed_final_no_save_release_observed
        ),
        "no_forbidden_final_no_save_releases": no_forbidden_final_no_save_releases,
        "final_no_save_release_record_valid": final_no_save_release_record_valid,
        "final_no_save_release_record_rejected": final_no_save_release_record_rejected,
        "unsafe_final_no_save_release_record_count": (
            unsafe_final_no_save_release_record_count
        ),
        "missing_final_no_save_release_prerequisites": missing,
        "missing_final_no_save_release_prerequisite_count": len(missing),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract.update(allowed_counts)
    contract.update(forbidden_counts)
    return contract


def summarize_durable_executor_authoring_final_no_save_releases_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(requested, "final_no_save_release_record_rejected")
    unsafe_count = _sum_count(
        requested, "unsafe_final_no_save_release_record_count"
    )
    forbidden_release_count = _sum_count(
        requested, "reported_forbidden_final_no_save_release_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, "final_no_save_release_contract_defined")
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_release_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_FINAL_NO_SAVE_RELEASE_AFTER_READBACK_AFTER_RESULT_AFTER_APPLICATION_AFTER_DECISION_AFTER_EVIDENCE_AFTER_EXECUTION_AFTER_DISPATCH_AFTER_COMMAND_AFTER_ENABLE_AFTER_OPEN_AFTER_ACTIVATION_READINESS_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_final_no_save_release_after_readback_after_result_after_application_after_decision_after_evidence_after_execution_after_dispatch_after_command_after_enable_after_open_after_activation_readiness_count": len(
            requested
        ),
        "final_no_save_release_contract_defined_count": _sum_truthy(
            requested, "final_no_save_release_contract_defined"
        ),
        "readback_contract_ready_count": _sum_truthy(
            requested, "readback_contract_ready"
        ),
        "readback_inputs_satisfied_count": _sum_truthy(
            requested, "readback_inputs_satisfied"
        ),
        "readback_record_valid_count": _sum_truthy(
            requested, "readback_record_valid"
        ),
        "allowed_readback_observed_count": _sum_truthy(
            requested, "allowed_readback_observed"
        ),
        "no_forbidden_readbacks_count": _sum_truthy(
            requested, "no_forbidden_readbacks"
        ),
        "final_no_save_release_inputs_satisfied_count": _sum_truthy(
            requested, "final_no_save_release_inputs_satisfied"
        ),
        "final_no_save_release_record_present_count": _sum_truthy(
            requested, "final_no_save_release_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "final_no_save_release_scope_matches_count": _sum_truthy(
            requested, "final_no_save_release_scope_matches"
        ),
        "explicit_final_no_save_release_authorized_count": _sum_truthy(
            requested, "explicit_final_no_save_release_authorized"
        ),
        "final_no_save_release_status_passed_count": _sum_truthy(
            requested, "final_no_save_release_status_passed"
        ),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "allowed_final_no_save_release_observed_count": _sum_truthy(
            requested, "allowed_final_no_save_release_observed"
        ),
        "no_forbidden_final_no_save_releases_count": _sum_truthy(
            requested, "no_forbidden_final_no_save_releases"
        ),
        "final_no_save_release_record_valid_count": _sum_truthy(
            requested, "final_no_save_release_record_valid"
        ),
        "final_no_save_release_record_rejected_count": rejected_count,
        "unsafe_final_no_save_release_record_count": unsafe_count,
        "missing_final_no_save_release_prerequisite_count": _sum_count(
            requested, "missing_final_no_save_release_prerequisite_count"
        ),
        "reported_allowed_final_no_save_release_count": _sum_count(
            requested, "reported_allowed_final_no_save_release_count"
        ),
        "reported_forbidden_final_no_save_release_count": forbidden_release_count,
    }
    summary.update(
        {f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS}
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in ALLOWED_FINAL_NO_SAVE_RELEASE_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in FORBIDDEN_FINAL_NO_SAVE_RELEASE_COUNT_KEYS
        }
    )
    return summary
