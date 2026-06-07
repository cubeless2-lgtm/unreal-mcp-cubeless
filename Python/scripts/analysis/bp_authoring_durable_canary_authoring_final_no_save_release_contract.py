#!/usr/bin/env python
"""
Section 93 durable canary authoring final no-save release contract.

This contract validates a future no-save release record after result readback
is valid. It still does not accept durable completion, asset writes, saves,
delete/rename, cleanup, or durable authoring enablement.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_DURABLE_AUTHORING_FINAL_NO_SAVE_RELEASE_SCHEMA = (
    "section_93_durable_canary_authoring_final_no_save_release_contract_v1"
)
CANARY_DURABLE_AUTHORING_FINAL_NO_SAVE_RELEASE_RECORD_SCHEMA = (
    "section_93_durable_canary_authoring_final_no_save_release_record_v1"
)
CANARY_DURABLE_AUTHORING_FINAL_NO_SAVE_RELEASE_SUMMARY_SCHEMA = (
    "section_93_durable_canary_authoring_final_no_save_release_summary_v1"
)
EXPECTED_FINAL_NO_SAVE_RELEASE_SCOPE = "durable_canary_authoring_final_no_save_release_only"


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


def build_canary_durable_authoring_final_no_save_release_contract(
    requested: bool,
    readback_summary: Dict[str, Any],
    final_no_save_release_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    final_no_save_release_record = final_no_save_release_record or {}
    release_record_present = bool(final_no_save_release_record)
    readback_contract_ready = bool(
        requested
        and readback_summary.get("status") == "passed"
        and readback_summary.get("readback_contract_defined_count") == 1
        and readback_summary.get("readback_record_rejected_count") == 0
        and readback_summary.get("unsafe_readback_record_count") == 0
        and readback_summary.get("reported_forbidden_readback_count") == 0
        and readback_summary.get("durable_authoring_command_result_readback_accepted_count") == 0
        and readback_summary.get("durable_authoring_command_completed_count") == 0
        and readback_summary.get("asset_write_performed_count") == 0
        and readback_summary.get("package_dirty_marked_count") == 0
        and readback_summary.get("durable_authoring_enabled_count") == 0
        and readback_summary.get("durable_authoring_allowed_count") == 0
        and readback_summary.get("save_delete_rename_allowed_count") == 0
        and readback_summary.get("cleanup_allowed_count") == 0
    )
    readback_inputs_satisfied = bool(readback_summary.get("readback_inputs_satisfied_count") == 1)
    readback_record_valid = bool(readback_summary.get("readback_record_valid_count") == 1)
    allowed_readback_observed = bool(readback_summary.get("allowed_readback_observed_count") == 1)
    no_forbidden_readbacks = bool(readback_summary.get("no_forbidden_readbacks_count") == 1)
    final_no_save_release_inputs_satisfied = bool(
        readback_inputs_satisfied
        and readback_record_valid
        and allowed_readback_observed
        and no_forbidden_readbacks
    )
    record_schema_matches = bool(
        release_record_present
        and final_no_save_release_record.get("schema")
        == CANARY_DURABLE_AUTHORING_FINAL_NO_SAVE_RELEASE_RECORD_SCHEMA
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
        release_record_present and final_no_save_release_record.get("status") == "passed"
    )
    no_save_delete_rename_acknowledged = bool(
        release_record_present
        and final_no_save_release_record.get("operator_reconfirmed_no_save_delete_rename")
        is True
    )
    reported_no_completion_release_count = _count(
        final_no_save_release_record.get("reported_no_completion_release_count")
    )
    reported_no_write_release_count = _count(
        final_no_save_release_record.get("reported_no_write_release_count")
    )
    reported_no_save_release_count = _count(
        final_no_save_release_record.get("reported_no_save_release_count")
    )
    reported_readback_revalidated_count = _count(
        final_no_save_release_record.get("reported_readback_revalidated_count")
    )
    reported_completion_release_count = _count(
        final_no_save_release_record.get("reported_completion_release_count")
    )
    reported_asset_write_release_count = _count(
        final_no_save_release_record.get("reported_asset_write_release_count")
    )
    reported_package_dirty_release_count = _count(
        final_no_save_release_record.get("reported_package_dirty_release_count")
    )
    reported_save_release_count = _count(
        final_no_save_release_record.get("reported_save_release_count")
    )
    reported_delete_rename_release_count = _count(
        final_no_save_release_record.get("reported_delete_rename_release_count")
    )
    reported_cleanup_release_count = _count(
        final_no_save_release_record.get("reported_cleanup_release_count")
    )
    reported_durable_authoring_release_count = _count(
        final_no_save_release_record.get("reported_durable_authoring_release_count")
    )
    reported_allowed_final_no_save_release_count = (
        reported_no_completion_release_count
        + reported_no_write_release_count
        + reported_no_save_release_count
        + reported_readback_revalidated_count
    )
    reported_forbidden_final_no_save_release_count = (
        reported_completion_release_count
        + reported_asset_write_release_count
        + reported_package_dirty_release_count
        + reported_save_release_count
        + reported_delete_rename_release_count
        + reported_cleanup_release_count
        + reported_durable_authoring_release_count
    )
    allowed_final_no_save_release_observed = bool(
        release_record_present and reported_allowed_final_no_save_release_count > 0
    )
    no_forbidden_final_no_save_releases = bool(
        release_record_present and reported_forbidden_final_no_save_release_count == 0
    )
    unsafe_final_no_save_release_record_count = (
        sum(
            int(_attempted(final_no_save_release_record.get(key)))
            for key in (
                "durable_authoring_final_no_save_release_accepted",
                "durable_authoring_command_result_readback_accepted",
                "durable_authoring_command_completed",
                "durable_authoring_command_completion_result_accepted",
                "asset_write_performed",
                "package_dirty_marked",
                "save_asset_executed",
                "delete_asset_authorized",
                "rename_asset_authorized",
                "cleanup_authorized",
                "durable_authoring_enabled",
                "durable_authoring_allowed",
                "live_command_dispatched",
                "live_command_executed",
            )
        )
        + reported_forbidden_final_no_save_release_count
    )
    final_no_save_release_contract_defined = bool(requested and readback_contract_ready)
    final_no_save_release_record_valid = bool(
        final_no_save_release_contract_defined
        and final_no_save_release_inputs_satisfied
        and record_schema_matches
        and final_no_save_release_scope_matches
        and explicit_final_no_save_release_authorized
        and final_no_save_release_status_passed
        and no_save_delete_rename_acknowledged
        and allowed_final_no_save_release_observed
        and no_forbidden_final_no_save_releases
        and unsafe_final_no_save_release_record_count == 0
    )
    missing = []
    if requested:
        if not readback_inputs_satisfied:
            missing.append("section_92_readback_inputs_satisfied")
        if not readback_record_valid:
            missing.append("section_92_readback_record_valid")
        if not allowed_readback_observed:
            missing.append("section_92_allowed_readback_observed")
        if not no_forbidden_readbacks:
            missing.append("section_92_no_forbidden_readbacks")
        if not release_record_present:
            missing.append("durable_authoring_final_no_save_release_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_final_no_save_release_record_schema")
        if not final_no_save_release_scope_matches:
            missing.append("durable_canary_authoring_final_no_save_release_only_scope")
        if not explicit_final_no_save_release_authorized:
            missing.append("explicit_durable_authoring_final_no_save_release_authorization")
        if not final_no_save_release_status_passed:
            missing.append("durable_authoring_final_no_save_release_status_passed")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not allowed_final_no_save_release_observed:
            missing.append("allowed_durable_authoring_final_no_save_release_observed")
        if not no_forbidden_final_no_save_releases:
            missing.append("no_forbidden_durable_authoring_final_no_save_releases")
        missing.append("separate_durable_authoring_final_release_readiness_contract")
    final_no_save_release_record_rejected = bool(
        release_record_present and not final_no_save_release_record_valid
    )
    return {
        "id": "durable_canary_authoring_final_no_save_release",
        "schema": CANARY_DURABLE_AUTHORING_FINAL_NO_SAVE_RELEASE_SCHEMA,
        "requested": requested,
        "final_no_save_release_contract_defined": final_no_save_release_contract_defined,
        "required_final_no_save_release_record_schema": (
            CANARY_DURABLE_AUTHORING_FINAL_NO_SAVE_RELEASE_RECORD_SCHEMA
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
        "final_no_save_release_inputs_satisfied": final_no_save_release_inputs_satisfied,
        "final_no_save_release_record_present": release_record_present,
        "record_schema_matches": record_schema_matches,
        "final_no_save_release_scope_matches": final_no_save_release_scope_matches,
        "explicit_final_no_save_release_authorized": explicit_final_no_save_release_authorized,
        "final_no_save_release_status_passed": final_no_save_release_status_passed,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "reported_allowed_final_no_save_release_count": reported_allowed_final_no_save_release_count,
        "reported_forbidden_final_no_save_release_count": (
            reported_forbidden_final_no_save_release_count
        ),
        "allowed_final_no_save_release_observed": allowed_final_no_save_release_observed,
        "no_forbidden_final_no_save_releases": no_forbidden_final_no_save_releases,
        "final_no_save_release_record_valid": final_no_save_release_record_valid,
        "final_no_save_release_record_rejected": final_no_save_release_record_rejected,
        "unsafe_final_no_save_release_record_count": unsafe_final_no_save_release_record_count,
        "missing_final_no_save_release_prerequisites": missing,
        "missing_final_no_save_release_prerequisite_count": len(missing),
        "durable_authoring_final_no_save_release_accepted": False,
        "durable_authoring_command_result_readback_accepted": False,
        "durable_authoring_command_completed": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatched": False,
        "live_command_executed": False,
        "reported_no_completion_release_count": reported_no_completion_release_count,
        "reported_no_write_release_count": reported_no_write_release_count,
        "reported_no_save_release_count": reported_no_save_release_count,
        "reported_readback_revalidated_count": reported_readback_revalidated_count,
        "reported_completion_release_count": reported_completion_release_count,
        "reported_asset_write_release_count": reported_asset_write_release_count,
        "reported_package_dirty_release_count": reported_package_dirty_release_count,
        "reported_save_release_count": reported_save_release_count,
        "reported_delete_rename_release_count": reported_delete_rename_release_count,
        "reported_cleanup_release_count": reported_cleanup_release_count,
        "reported_durable_authoring_release_count": reported_durable_authoring_release_count,
    }


def summarize_canary_durable_authoring_final_no_save_releases(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1 for contract in requested if contract.get("final_no_save_release_record_rejected")
    )
    unsafe_count = sum(
        contract.get("unsafe_final_no_save_release_record_count", 0)
        for contract in requested
    )
    forbidden_release_count = sum(
        contract.get("reported_forbidden_final_no_save_release_count", 0)
        for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(
                1
                for contract in requested
                if contract.get("final_no_save_release_contract_defined")
            )
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_release_count == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_final_no_save_release_accepted")
            )
            == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_result_readback_accepted")
            )
            == 0
            and sum(
                1 for contract in requested if contract.get("durable_authoring_command_completed")
            )
            == 0
            and sum(1 for contract in requested if contract.get("asset_write_performed")) == 0
            and sum(1 for contract in requested if contract.get("package_dirty_marked")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_enabled")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_delete_rename_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_dispatched")) == 0
            and sum(1 for contract in requested if contract.get("live_command_executed")) == 0
            else "failed"
        )
    return {
        "schema": CANARY_DURABLE_AUTHORING_FINAL_NO_SAVE_RELEASE_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_authoring_final_no_save_release_count": len(requested),
        "final_no_save_release_contract_defined_count": sum(
            1
            for contract in requested
            if contract.get("final_no_save_release_contract_defined")
        ),
        "readback_contract_ready_count": sum(
            1 for contract in requested if contract.get("readback_contract_ready")
        ),
        "readback_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("readback_inputs_satisfied")
        ),
        "readback_record_valid_count": sum(
            1 for contract in requested if contract.get("readback_record_valid")
        ),
        "allowed_readback_observed_count": sum(
            1 for contract in requested if contract.get("allowed_readback_observed")
        ),
        "no_forbidden_readbacks_count": sum(
            1 for contract in requested if contract.get("no_forbidden_readbacks")
        ),
        "final_no_save_release_inputs_satisfied_count": sum(
            1
            for contract in requested
            if contract.get("final_no_save_release_inputs_satisfied")
        ),
        "final_no_save_release_record_present_count": sum(
            1
            for contract in requested
            if contract.get("final_no_save_release_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "final_no_save_release_scope_matches_count": sum(
            1
            for contract in requested
            if contract.get("final_no_save_release_scope_matches")
        ),
        "explicit_final_no_save_release_authorized_count": sum(
            1
            for contract in requested
            if contract.get("explicit_final_no_save_release_authorized")
        ),
        "final_no_save_release_status_passed_count": sum(
            1
            for contract in requested
            if contract.get("final_no_save_release_status_passed")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "allowed_final_no_save_release_observed_count": sum(
            1
            for contract in requested
            if contract.get("allowed_final_no_save_release_observed")
        ),
        "no_forbidden_final_no_save_releases_count": sum(
            1
            for contract in requested
            if contract.get("no_forbidden_final_no_save_releases")
        ),
        "final_no_save_release_record_valid_count": sum(
            1
            for contract in requested
            if contract.get("final_no_save_release_record_valid")
        ),
        "final_no_save_release_record_rejected_count": rejected_count,
        "unsafe_final_no_save_release_record_count": unsafe_count,
        "missing_final_no_save_release_prerequisite_count": sum(
            contract.get("missing_final_no_save_release_prerequisite_count", 0)
            for contract in requested
        ),
        "reported_allowed_final_no_save_release_count": sum(
            contract.get("reported_allowed_final_no_save_release_count", 0)
            for contract in requested
        ),
        "reported_forbidden_final_no_save_release_count": forbidden_release_count,
        "durable_authoring_final_no_save_release_accepted_count": sum(
            1
            for contract in requested
            if contract.get("durable_authoring_final_no_save_release_accepted")
        ),
        "durable_authoring_command_result_readback_accepted_count": sum(
            1
            for contract in requested
            if contract.get("durable_authoring_command_result_readback_accepted")
        ),
        "durable_authoring_command_completed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_command_completed")
        ),
        "asset_write_performed_count": sum(
            1 for contract in requested if contract.get("asset_write_performed")
        ),
        "package_dirty_marked_count": sum(
            1 for contract in requested if contract.get("package_dirty_marked")
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
        "live_command_dispatched_count": sum(
            1 for contract in requested if contract.get("live_command_dispatched")
        ),
        "live_command_executed_count": sum(
            1 for contract in requested if contract.get("live_command_executed")
        ),
        "reported_no_completion_release_count": sum(
            contract.get("reported_no_completion_release_count", 0)
            for contract in requested
        ),
        "reported_no_write_release_count": sum(
            contract.get("reported_no_write_release_count", 0) for contract in requested
        ),
        "reported_no_save_release_count": sum(
            contract.get("reported_no_save_release_count", 0) for contract in requested
        ),
        "reported_readback_revalidated_count": sum(
            contract.get("reported_readback_revalidated_count", 0)
            for contract in requested
        ),
        "reported_completion_release_count": sum(
            contract.get("reported_completion_release_count", 0) for contract in requested
        ),
        "reported_asset_write_release_count": sum(
            contract.get("reported_asset_write_release_count", 0)
            for contract in requested
        ),
        "reported_package_dirty_release_count": sum(
            contract.get("reported_package_dirty_release_count", 0)
            for contract in requested
        ),
        "reported_save_release_count": sum(
            contract.get("reported_save_release_count", 0) for contract in requested
        ),
        "reported_delete_rename_release_count": sum(
            contract.get("reported_delete_rename_release_count", 0)
            for contract in requested
        ),
        "reported_cleanup_release_count": sum(
            contract.get("reported_cleanup_release_count", 0) for contract in requested
        ),
        "reported_durable_authoring_release_count": sum(
            contract.get("reported_durable_authoring_release_count", 0)
            for contract in requested
        ),
    }
