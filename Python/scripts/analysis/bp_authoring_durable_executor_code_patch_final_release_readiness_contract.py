#!/usr/bin/env python
"""
Section 106 durable executor code patch final release readiness contract.

This contract validates a future code-patch-final-release-readiness-only record
after the code patch final no-save release record is valid. It does not apply
code patches, modify code or assets, probe live bridges, enable durable
authoring, save, delete/rename, or cleanup.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_CODE_PATCH_FINAL_RELEASE_READINESS_SCHEMA = (
    "section_106_durable_executor_code_patch_final_release_readiness_contract_v1"
)
DURABLE_EXECUTOR_CODE_PATCH_FINAL_RELEASE_READINESS_RECORD_SCHEMA = (
    "section_106_durable_executor_code_patch_final_release_readiness_record_v1"
)
DURABLE_EXECUTOR_CODE_PATCH_FINAL_RELEASE_READINESS_SUMMARY_SCHEMA = (
    "section_106_durable_executor_code_patch_final_release_readiness_summary_v1"
)
EXPECTED_CODE_PATCH_FINAL_RELEASE_READINESS_SCOPE = (
    "durable_executor_code_patch_final_release_readiness_only"
)


OUTPUT_ACTION_KEYS = (
    "durable_executor_code_patch_final_release_readiness_started",
    "durable_executor_code_patch_final_release_ready",
    "durable_executor_code_patch_release_review_started",
    "code_change_performed",
    "executor_code_modified",
    "unreal_asset_modified",
    "live_bridge_probe_started",
    "durable_authoring_enabled",
    "durable_authoring_allowed",
    "asset_write_performed",
    "package_dirty_marked",
    "save_delete_rename_allowed",
    "cleanup_allowed",
    "live_command_dispatched",
    "live_command_executed",
)
UNSAFE_RECORD_ACTION_KEYS = (
    "durable_executor_code_patch_final_release_readiness_started",
    "durable_executor_code_patch_final_release_ready",
    "durable_executor_code_patch_release_review_started",
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
ALLOWED_FINAL_RELEASE_READINESS_COUNT_KEYS = (
    "reported_final_release_readiness_gate_count",
    "reported_final_no_save_release_revalidated_count",
    "reported_durable_authoring_still_disabled_count",
    "reported_no_code_change_readiness_count",
    "reported_no_asset_change_readiness_count",
    "reported_no_live_probe_readiness_count",
)
FORBIDDEN_FINAL_RELEASE_READINESS_COUNT_KEYS = (
    "reported_code_patch_applied_count",
    "reported_code_patch_execution_count",
    "reported_code_patch_result_admission_count",
    "reported_code_patch_result_readback_count",
    "reported_final_no_save_release_count",
    "reported_code_change_count",
    "reported_executor_code_modified_count",
    "reported_unreal_asset_change_count",
    "reported_live_probe_count",
    "reported_durable_authoring_count",
    "reported_asset_write_count",
    "reported_save_count",
    "reported_delete_rename_count",
    "reported_cleanup_count",
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


def build_durable_executor_code_patch_final_release_readiness_contract(
    requested: bool,
    code_patch_final_no_save_release_summary: Dict[str, Any],
    readiness_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    readiness_record = readiness_record or {}
    readiness_record_present = bool(readiness_record)
    code_patch_final_no_save_release_contract_ready = bool(
        requested
        and code_patch_final_no_save_release_summary.get("status") == "passed"
        and code_patch_final_no_save_release_summary.get(
            "code_patch_final_no_save_release_contract_defined_count"
        )
        == 1
        and code_patch_final_no_save_release_summary.get(
            "code_patch_final_no_save_release_record_rejected_count"
        )
        == 0
        and code_patch_final_no_save_release_summary.get(
            "unsafe_code_patch_final_no_save_release_record_count"
        )
        == 0
        and code_patch_final_no_save_release_summary.get(
            "reported_forbidden_code_patch_final_no_save_release_count"
        )
        == 0
        and code_patch_final_no_save_release_summary.get(
            "durable_executor_code_patch_final_no_save_release_started_count"
        )
        == 0
        and code_patch_final_no_save_release_summary.get(
            "durable_executor_code_patch_final_no_save_release_accepted_count"
        )
        == 0
        and code_patch_final_no_save_release_summary.get(
            "durable_executor_code_patch_final_release_readiness_started_count"
        )
        == 0
        and code_patch_final_no_save_release_summary.get("code_change_performed_count")
        == 0
        and code_patch_final_no_save_release_summary.get("executor_code_modified_count")
        == 0
        and code_patch_final_no_save_release_summary.get("unreal_asset_modified_count")
        == 0
        and code_patch_final_no_save_release_summary.get("live_bridge_probe_started_count")
        == 0
        and code_patch_final_no_save_release_summary.get("durable_authoring_enabled_count")
        == 0
        and code_patch_final_no_save_release_summary.get("durable_authoring_allowed_count")
        == 0
        and code_patch_final_no_save_release_summary.get("asset_write_performed_count")
        == 0
        and code_patch_final_no_save_release_summary.get("package_dirty_marked_count")
        == 0
        and code_patch_final_no_save_release_summary.get("save_delete_rename_allowed_count")
        == 0
        and code_patch_final_no_save_release_summary.get("cleanup_allowed_count") == 0
        and code_patch_final_no_save_release_summary.get("live_command_dispatched_count")
        == 0
        and code_patch_final_no_save_release_summary.get("live_command_executed_count")
        == 0
    )
    code_patch_final_no_save_release_inputs_satisfied = bool(
        code_patch_final_no_save_release_summary.get(
            "code_patch_final_no_save_release_inputs_satisfied_count"
        )
        == 1
    )
    code_patch_final_no_save_release_record_valid = bool(
        code_patch_final_no_save_release_summary.get(
            "code_patch_final_no_save_release_record_valid_count"
        )
        == 1
    )
    allowed_code_patch_final_no_save_release_observed = bool(
        code_patch_final_no_save_release_summary.get(
            "allowed_code_patch_final_no_save_release_observed_count"
        )
        == 1
    )
    no_forbidden_code_patch_final_no_save_release_claims = bool(
        code_patch_final_no_save_release_summary.get(
            "no_forbidden_code_patch_final_no_save_release_claims_count"
        )
        == 1
    )
    code_patch_final_release_readiness_inputs_satisfied = bool(
        code_patch_final_no_save_release_inputs_satisfied
        and code_patch_final_no_save_release_record_valid
        and allowed_code_patch_final_no_save_release_observed
        and no_forbidden_code_patch_final_no_save_release_claims
    )
    record_schema_matches = bool(
        readiness_record_present
        and readiness_record.get("schema")
        == DURABLE_EXECUTOR_CODE_PATCH_FINAL_RELEASE_READINESS_RECORD_SCHEMA
    )
    code_patch_final_release_readiness_scope_matches = bool(
        readiness_record_present
        and readiness_record.get("code_patch_final_release_readiness_scope")
        == EXPECTED_CODE_PATCH_FINAL_RELEASE_READINESS_SCOPE
    )
    explicit_code_patch_final_release_readiness_authorized = bool(
        readiness_record_present
        and readiness_record.get(
            "explicit_durable_executor_code_patch_final_release_readiness_authorized"
        )
        is True
    )
    readiness_status_passed = bool(
        readiness_record_present and readiness_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        readiness_record_present
        and readiness_record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    explicit_durable_mvp_request_reconfirmed = bool(
        readiness_record_present
        and readiness_record.get("explicit_durable_mvp_request_reconfirmed") is True
    )
    allowed_counts = {
        key: _count(readiness_record.get(key))
        for key in ALLOWED_FINAL_RELEASE_READINESS_COUNT_KEYS
    }
    forbidden_counts = {
        key: _count(readiness_record.get(key))
        for key in FORBIDDEN_FINAL_RELEASE_READINESS_COUNT_KEYS
    }
    reported_allowed_code_patch_final_release_readiness_count = sum(
        allowed_counts.values()
    )
    reported_forbidden_code_patch_final_release_readiness_count = sum(
        forbidden_counts.values()
    )
    allowed_code_patch_final_release_readiness_observed = bool(
        readiness_record_present
        and reported_allowed_code_patch_final_release_readiness_count > 0
    )
    no_forbidden_code_patch_final_release_readiness_claims = bool(
        readiness_record_present
        and reported_forbidden_code_patch_final_release_readiness_count == 0
    )
    unsafe_code_patch_final_release_readiness_record_count = (
        sum(int(_attempted(readiness_record.get(key))) for key in UNSAFE_RECORD_ACTION_KEYS)
        + reported_forbidden_code_patch_final_release_readiness_count
    )
    code_patch_final_release_readiness_contract_defined = bool(
        requested and code_patch_final_no_save_release_contract_ready
    )
    code_patch_final_release_readiness_record_valid = bool(
        code_patch_final_release_readiness_contract_defined
        and code_patch_final_release_readiness_inputs_satisfied
        and record_schema_matches
        and code_patch_final_release_readiness_scope_matches
        and explicit_code_patch_final_release_readiness_authorized
        and readiness_status_passed
        and no_save_delete_rename_acknowledged
        and explicit_durable_mvp_request_reconfirmed
        and allowed_code_patch_final_release_readiness_observed
        and no_forbidden_code_patch_final_release_readiness_claims
        and unsafe_code_patch_final_release_readiness_record_count == 0
    )
    missing = []
    if requested:
        if not code_patch_final_no_save_release_inputs_satisfied:
            missing.append("section_105_code_patch_final_no_save_release_inputs_satisfied")
        if not code_patch_final_no_save_release_record_valid:
            missing.append("section_105_code_patch_final_no_save_release_record_valid")
        if not allowed_code_patch_final_no_save_release_observed:
            missing.append("section_105_allowed_code_patch_final_no_save_release_observed")
        if not no_forbidden_code_patch_final_no_save_release_claims:
            missing.append(
                "section_105_no_forbidden_code_patch_final_no_save_release_claims"
            )
        if not readiness_record_present:
            missing.append(
                "durable_executor_code_patch_final_release_readiness_record_present"
            )
        if not record_schema_matches:
            missing.append(
                "durable_executor_code_patch_final_release_readiness_record_schema"
            )
        if not code_patch_final_release_readiness_scope_matches:
            missing.append(
                "durable_executor_code_patch_final_release_readiness_only_scope"
            )
        if not explicit_code_patch_final_release_readiness_authorized:
            missing.append(
                "explicit_durable_executor_code_patch_final_release_readiness_authorization"
            )
        if not readiness_status_passed:
            missing.append(
                "durable_executor_code_patch_final_release_readiness_status_passed"
            )
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not explicit_durable_mvp_request_reconfirmed:
            missing.append("explicit_durable_mvp_request_reconfirmed")
        if not allowed_code_patch_final_release_readiness_observed:
            missing.append(
                "allowed_durable_executor_code_patch_final_release_readiness_observed"
            )
        if not no_forbidden_code_patch_final_release_readiness_claims:
            missing.append(
                "no_forbidden_durable_executor_code_patch_final_release_readiness_claims"
            )
        missing.append(
            "separate_durable_executor_code_patch_release_review_contract"
        )
    code_patch_final_release_readiness_record_rejected = bool(
        readiness_record_present
        and not code_patch_final_release_readiness_record_valid
    )
    contract: Dict[str, Any] = {
        "id": "durable_executor_code_patch_final_release_readiness",
        "schema": DURABLE_EXECUTOR_CODE_PATCH_FINAL_RELEASE_READINESS_SCHEMA,
        "requested": requested,
        "code_patch_final_release_readiness_contract_defined": (
            code_patch_final_release_readiness_contract_defined
        ),
        "required_code_patch_final_release_readiness_record_schema": (
            DURABLE_EXECUTOR_CODE_PATCH_FINAL_RELEASE_READINESS_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_code_patch_final_release_readiness_scope": (
            EXPECTED_CODE_PATCH_FINAL_RELEASE_READINESS_SCOPE if requested else ""
        ),
        "code_patch_final_no_save_release_contract_ready": (
            code_patch_final_no_save_release_contract_ready
        ),
        "code_patch_final_no_save_release_inputs_satisfied": (
            code_patch_final_no_save_release_inputs_satisfied
        ),
        "code_patch_final_no_save_release_record_valid": (
            code_patch_final_no_save_release_record_valid
        ),
        "allowed_code_patch_final_no_save_release_observed": (
            allowed_code_patch_final_no_save_release_observed
        ),
        "no_forbidden_code_patch_final_no_save_release_claims": (
            no_forbidden_code_patch_final_no_save_release_claims
        ),
        "code_patch_final_release_readiness_inputs_satisfied": (
            code_patch_final_release_readiness_inputs_satisfied
        ),
        "code_patch_final_release_readiness_record_present": (
            readiness_record_present
        ),
        "record_schema_matches": record_schema_matches,
        "code_patch_final_release_readiness_scope_matches": (
            code_patch_final_release_readiness_scope_matches
        ),
        "explicit_code_patch_final_release_readiness_authorized": (
            explicit_code_patch_final_release_readiness_authorized
        ),
        "readiness_status_passed": readiness_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "explicit_durable_mvp_request_reconfirmed": (
            explicit_durable_mvp_request_reconfirmed
        ),
        "reported_allowed_code_patch_final_release_readiness_count": (
            reported_allowed_code_patch_final_release_readiness_count
        ),
        "reported_forbidden_code_patch_final_release_readiness_count": (
            reported_forbidden_code_patch_final_release_readiness_count
        ),
        "allowed_code_patch_final_release_readiness_observed": (
            allowed_code_patch_final_release_readiness_observed
        ),
        "no_forbidden_code_patch_final_release_readiness_claims": (
            no_forbidden_code_patch_final_release_readiness_claims
        ),
        "code_patch_final_release_readiness_record_valid": (
            code_patch_final_release_readiness_record_valid
        ),
        "code_patch_final_release_readiness_record_rejected": (
            code_patch_final_release_readiness_record_rejected
        ),
        "unsafe_code_patch_final_release_readiness_record_count": (
            unsafe_code_patch_final_release_readiness_record_count
        ),
        "missing_code_patch_final_release_readiness_prerequisites": missing,
        "missing_code_patch_final_release_readiness_prerequisite_count": len(missing),
    }
    contract.update({key: False for key in OUTPUT_ACTION_KEYS})
    contract.update(allowed_counts)
    contract.update(forbidden_counts)
    return contract


def summarize_durable_executor_code_patch_final_release_readiness(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1
        for contract in requested
        if contract.get("code_patch_final_release_readiness_record_rejected")
    )
    unsafe_count = _sum_count(
        requested, "unsafe_code_patch_final_release_readiness_record_count"
    )
    forbidden_final_release_readiness_count = _sum_count(
        requested, "reported_forbidden_code_patch_final_release_readiness_count"
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(
                requested, "code_patch_final_release_readiness_contract_defined"
            )
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_final_release_readiness_count == 0
            and all(_sum_truthy(requested, key) == 0 for key in OUTPUT_ACTION_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_CODE_PATCH_FINAL_RELEASE_READINESS_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_code_patch_final_release_readiness_count": len(
            requested
        ),
        "code_patch_final_release_readiness_contract_defined_count": _sum_truthy(
            requested, "code_patch_final_release_readiness_contract_defined"
        ),
        "code_patch_final_no_save_release_contract_ready_count": _sum_truthy(
            requested, "code_patch_final_no_save_release_contract_ready"
        ),
        "code_patch_final_no_save_release_inputs_satisfied_count": _sum_truthy(
            requested, "code_patch_final_no_save_release_inputs_satisfied"
        ),
        "code_patch_final_no_save_release_record_valid_count": _sum_truthy(
            requested, "code_patch_final_no_save_release_record_valid"
        ),
        "allowed_code_patch_final_no_save_release_observed_count": _sum_truthy(
            requested, "allowed_code_patch_final_no_save_release_observed"
        ),
        "no_forbidden_code_patch_final_no_save_release_claims_count": _sum_truthy(
            requested, "no_forbidden_code_patch_final_no_save_release_claims"
        ),
        "code_patch_final_release_readiness_inputs_satisfied_count": _sum_truthy(
            requested, "code_patch_final_release_readiness_inputs_satisfied"
        ),
        "code_patch_final_release_readiness_record_present_count": _sum_truthy(
            requested, "code_patch_final_release_readiness_record_present"
        ),
        "record_schema_matches_count": _sum_truthy(requested, "record_schema_matches"),
        "code_patch_final_release_readiness_scope_matches_count": _sum_truthy(
            requested, "code_patch_final_release_readiness_scope_matches"
        ),
        "explicit_code_patch_final_release_readiness_authorized_count": _sum_truthy(
            requested, "explicit_code_patch_final_release_readiness_authorized"
        ),
        "readiness_status_passed_count": _sum_truthy(
            requested, "readiness_status_passed"
        ),
        "no_save_delete_rename_acknowledged_count": _sum_truthy(
            requested, "no_save_delete_rename_acknowledged"
        ),
        "explicit_durable_mvp_request_reconfirmed_count": _sum_truthy(
            requested, "explicit_durable_mvp_request_reconfirmed"
        ),
        "allowed_code_patch_final_release_readiness_observed_count": _sum_truthy(
            requested, "allowed_code_patch_final_release_readiness_observed"
        ),
        "no_forbidden_code_patch_final_release_readiness_claims_count": _sum_truthy(
            requested, "no_forbidden_code_patch_final_release_readiness_claims"
        ),
        "code_patch_final_release_readiness_record_valid_count": _sum_truthy(
            requested, "code_patch_final_release_readiness_record_valid"
        ),
        "code_patch_final_release_readiness_record_rejected_count": rejected_count,
        "unsafe_code_patch_final_release_readiness_record_count": unsafe_count,
        "missing_code_patch_final_release_readiness_prerequisite_count": _sum_count(
            requested, "missing_code_patch_final_release_readiness_prerequisite_count"
        ),
        "reported_allowed_code_patch_final_release_readiness_count": _sum_count(
            requested, "reported_allowed_code_patch_final_release_readiness_count"
        ),
        "reported_forbidden_code_patch_final_release_readiness_count": (
            forbidden_final_release_readiness_count
        ),
    }
    summary.update({f"{key}_count": _sum_truthy(requested, key) for key in OUTPUT_ACTION_KEYS})
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in ALLOWED_FINAL_RELEASE_READINESS_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in FORBIDDEN_FINAL_RELEASE_READINESS_COUNT_KEYS
        }
    )
    return summary
