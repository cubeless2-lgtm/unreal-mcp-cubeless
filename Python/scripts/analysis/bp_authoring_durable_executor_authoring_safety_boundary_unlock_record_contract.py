#!/usr/bin/env python
"""
Section 183 durable executor authoring safety boundary unlock record contract.

This contract admits an explicit unlock approval record only when Section 182
reached the decision checkpoint and the live durable preflight evidence is
read-only. It may mark the safety boundary as ready for a later unlock section,
but it does not enable durable authoring, final release readiness, save,
delete, rename, or live write commands.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_safety_boundary_unlock_decision_contract as unlock_decision


DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_RECORD_SCHEMA = (
    "section_183_durable_executor_authoring_safety_boundary_unlock_record_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_APPROVAL_RECORD_SCHEMA = (
    "section_183_durable_executor_authoring_safety_boundary_unlock_approval_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_RECORD_SUMMARY_SCHEMA = (
    "section_183_durable_executor_authoring_safety_boundary_unlock_record_summary_v1"
)
SECTION_182_UNLOCK_DECISION_SUMMARY_SCHEMA = (
    unlock_decision
    .DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_DECISION_SUMMARY_SCHEMA
)
DURABLE_LIVE_PREFLIGHT_SCHEMA = "section_48_durable_preflight_live_gate_v1"
BLOCKED_OUTPUT_COUNT_KEYS = unlock_decision.BLOCKED_OUTPUT_COUNT_KEYS

APPROVAL_SCOPE_ID = "durable_executor_authoring_safety_boundary"
APPROVED_OPERATION = (
    "durable_safety_boundary_unlock_record_and_read_only_live_preflight"
)
READ_ONLY_COMMAND = "unreal.EditorAssetLibrary.does_asset_exist"


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _blocked_output_counts(summary: Dict[str, Any]) -> Dict[str, int]:
    return {
        key: int(summary.get(key, 0) or 0)
        for key in BLOCKED_OUTPUT_COUNT_KEYS
    }


def build_explicit_unlock_approval_record(
    approval_source: str = "user_explicit_approval_section_183",
) -> Dict[str, Any]:
    return {
        "schema": DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_APPROVAL_RECORD_SCHEMA,
        "approval_id": "section_183_explicit_safety_boundary_unlock_record_approval",
        "approval_source": approval_source,
        "approval_scope_id": APPROVAL_SCOPE_ID,
        "approved_operation": APPROVED_OPERATION,
        "approved_read_only_command": READ_ONLY_COMMAND,
        "explicit_durable_safety_boundary_unlock_approved": True,
        "approval_requires_read_only_live_preflight": True,
        "approval_does_not_authorize_save_delete_rename": True,
        "approval_does_not_authorize_live_durable_authoring_writes": True,
        "approval_does_not_authorize_blueprint_save": True,
        "approval_does_not_authorize_asset_deletion": True,
        "approval_does_not_authorize_asset_rename": True,
    }


def build_durable_executor_authoring_safety_boundary_unlock_record_contract(
    requested: bool,
    section_182_unlock_decision_summary: Dict[str, Any],
    live_preflight_summary: Dict[str, Any],
    approval_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    approval_record = approval_record or {}
    approval_present = bool(approval_record)
    blocked_counts = _blocked_output_counts(section_182_unlock_decision_summary)

    section_182_summary_schema_matches = bool(
        section_182_unlock_decision_summary.get("schema")
        == SECTION_182_UNLOCK_DECISION_SUMMARY_SCHEMA
    )
    section_182_summary_passed = bool(
        section_182_unlock_decision_summary.get("status") == "passed"
    )
    section_182_checkpoint_reached = bool(
        section_182_unlock_decision_summary.get(
            "unlock_decision_checkpoint_reached_count"
        )
        == 1
    )
    section_182_unlock_record_absent = bool(
        section_182_unlock_decision_summary.get(
            "unlock_decision_record_absent_count"
        )
        == 1
    )
    section_182_unlock_record_not_admissible = bool(
        section_182_unlock_decision_summary.get(
            "unlock_record_admissible_count"
        )
        == 0
    )
    section_182_authoring_disabled = bool(
        section_182_unlock_decision_summary.get(
            "durable_authoring_enabled_count"
        )
        == 0
    )
    section_182_final_release_not_ready = bool(
        section_182_unlock_decision_summary.get(
            "final_durable_release_ready_count"
        )
        == 0
    )
    section_182_unlocked_absent = bool(
        section_182_unlock_decision_summary.get(
            "durable_safety_boundary_unlocked_count"
        )
        == 0
    )
    blocked_outputs_zero = all(count == 0 for count in blocked_counts.values())

    approval_schema_matches = bool(
        approval_present
        and approval_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_APPROVAL_RECORD_SCHEMA
    )
    approval_scope_matches = bool(
        approval_present
        and approval_record.get("approval_scope_id") == APPROVAL_SCOPE_ID
    )
    approval_operation_matches = bool(
        approval_present
        and approval_record.get("approved_operation") == APPROVED_OPERATION
    )
    explicit_unlock_approval_present = bool(
        approval_present
        and approval_record.get(
            "explicit_durable_safety_boundary_unlock_approved"
        )
        is True
    )
    approval_requires_read_only_live_preflight = bool(
        approval_present
        and approval_record.get("approval_requires_read_only_live_preflight")
        is True
    )
    approval_blocks_save_delete_rename = bool(
        approval_present
        and approval_record.get("approval_does_not_authorize_save_delete_rename")
        is True
        and approval_record.get("approval_does_not_authorize_blueprint_save")
        is True
        and approval_record.get("approval_does_not_authorize_asset_deletion")
        is True
        and approval_record.get("approval_does_not_authorize_asset_rename")
        is True
    )
    approval_blocks_live_writes = bool(
        approval_present
        and approval_record.get(
            "approval_does_not_authorize_live_durable_authoring_writes"
        )
        is True
    )

    live_preflight_schema_matches = bool(
        live_preflight_summary.get("schema") == DURABLE_LIVE_PREFLIGHT_SCHEMA
    )
    live_preflight_passed = bool(live_preflight_summary.get("status") == "passed")
    live_preflight_requested = bool(
        live_preflight_summary.get("live_requested") is True
    )
    live_preflight_result_present = bool(
        int(live_preflight_summary.get("live_result_count", 0) or 0) == 1
    )
    live_preflight_read_only_result_passed = bool(
        int(live_preflight_summary.get("passed_read_only_result_count", 0) or 0)
        == 1
    )
    live_preflight_read_only_only = bool(
        live_preflight_summary.get("read_only_only") is True
    )
    live_preflight_no_authoring_attempted = bool(
        int(live_preflight_summary.get("authoring_attempted_count", 0) or 0) == 0
    )
    live_preflight_no_save_delete_attempted = bool(
        int(live_preflight_summary.get("save_or_delete_attempted_count", 0) or 0)
        == 0
    )
    live_preflight_does_not_pass_write_gate = bool(
        int(live_preflight_summary.get("preflight_pass_count", 0) or 0) == 0
        and live_preflight_summary.get("durable_authoring_allowed") is False
        and live_preflight_summary.get("save_or_delete_allowed") is False
    )

    unlock_record_admissible = bool(
        requested
        and section_182_summary_schema_matches
        and section_182_summary_passed
        and section_182_checkpoint_reached
        and section_182_unlock_record_absent
        and section_182_unlock_record_not_admissible
        and section_182_authoring_disabled
        and section_182_final_release_not_ready
        and section_182_unlocked_absent
        and blocked_outputs_zero
        and approval_present
        and approval_schema_matches
        and approval_scope_matches
        and approval_operation_matches
        and explicit_unlock_approval_present
        and approval_requires_read_only_live_preflight
        and approval_blocks_save_delete_rename
        and approval_blocks_live_writes
        and live_preflight_schema_matches
        and live_preflight_passed
        and live_preflight_requested
        and live_preflight_result_present
        and live_preflight_read_only_result_passed
        and live_preflight_read_only_only
        and live_preflight_no_authoring_attempted
        and live_preflight_no_save_delete_attempted
        and live_preflight_does_not_pass_write_gate
    )

    return {
        "id": "durable_executor_authoring_safety_boundary_unlock_record",
        "schema": DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_RECORD_SCHEMA,
        "requested": requested,
        "section_182_summary_schema_matches": section_182_summary_schema_matches,
        "section_182_summary_passed": section_182_summary_passed,
        "section_182_checkpoint_reached": section_182_checkpoint_reached,
        "section_182_unlock_record_absent": section_182_unlock_record_absent,
        "section_182_unlock_record_not_admissible": (
            section_182_unlock_record_not_admissible
        ),
        "section_182_authoring_disabled": section_182_authoring_disabled,
        "section_182_final_release_not_ready": section_182_final_release_not_ready,
        "section_182_unlocked_absent": section_182_unlocked_absent,
        "blocked_outputs_zero": blocked_outputs_zero,
        "approval_record_present": approval_present,
        "approval_record_schema_matches": approval_schema_matches,
        "approval_scope_matches": approval_scope_matches,
        "approval_operation_matches": approval_operation_matches,
        "explicit_unlock_approval_present": explicit_unlock_approval_present,
        "approval_requires_read_only_live_preflight": (
            approval_requires_read_only_live_preflight
        ),
        "approval_blocks_save_delete_rename": approval_blocks_save_delete_rename,
        "approval_blocks_live_writes": approval_blocks_live_writes,
        "live_preflight_schema_matches": live_preflight_schema_matches,
        "live_preflight_passed": live_preflight_passed,
        "live_preflight_requested": live_preflight_requested,
        "live_preflight_result_present": live_preflight_result_present,
        "live_preflight_read_only_result_passed": (
            live_preflight_read_only_result_passed
        ),
        "live_preflight_read_only_only": live_preflight_read_only_only,
        "live_preflight_no_authoring_attempted": (
            live_preflight_no_authoring_attempted
        ),
        "live_preflight_no_save_delete_attempted": (
            live_preflight_no_save_delete_attempted
        ),
        "live_preflight_does_not_pass_write_gate": (
            live_preflight_does_not_pass_write_gate
        ),
        "unlock_record_admissible": unlock_record_admissible,
        "durable_safety_boundary_unlock_ready": unlock_record_admissible,
        "durable_safety_boundary_unlocked": False,
        "durable_authoring_enabled": False,
        "final_durable_release_ready": False,
        "save_delete_rename_allowed": False,
        "live_durable_authoring_allowed": False,
        "approval_record": approval_record if requested else {},
        **blocked_counts,
    }


def summarize_durable_executor_authoring_safety_boundary_unlock_records(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "unlock_record_admissible") == len(requested)
            and _truthy_count(
                requested, "durable_safety_boundary_unlock_ready"
            )
            == len(requested)
            and _truthy_count(requested, "durable_safety_boundary_unlocked") == 0
            and _truthy_count(requested, "durable_authoring_enabled") == 0
            and _truthy_count(requested, "final_durable_release_ready") == 0
            and _truthy_count(requested, "save_delete_rename_allowed") == 0
            and _truthy_count(requested, "live_durable_authoring_allowed") == 0
            and all(_sum_count(requested, key) == 0 for key in BLOCKED_OUTPUT_COUNT_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_RECORD_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_safety_boundary_unlock_record_count": (
            len(requested)
        ),
        "section_182_summary_schema_matches_count": _truthy_count(
            requested, "section_182_summary_schema_matches"
        ),
        "section_182_summary_passed_count": _truthy_count(
            requested, "section_182_summary_passed"
        ),
        "section_182_checkpoint_reached_count": _truthy_count(
            requested, "section_182_checkpoint_reached"
        ),
        "section_182_unlock_record_absent_count": _truthy_count(
            requested, "section_182_unlock_record_absent"
        ),
        "section_182_unlock_record_not_admissible_count": _truthy_count(
            requested, "section_182_unlock_record_not_admissible"
        ),
        "section_182_authoring_disabled_count": _truthy_count(
            requested, "section_182_authoring_disabled"
        ),
        "section_182_final_release_not_ready_count": _truthy_count(
            requested, "section_182_final_release_not_ready"
        ),
        "section_182_unlocked_absent_count": _truthy_count(
            requested, "section_182_unlocked_absent"
        ),
        "blocked_outputs_zero_count": _truthy_count(
            requested, "blocked_outputs_zero"
        ),
        "approval_record_present_count": _truthy_count(
            requested, "approval_record_present"
        ),
        "approval_record_schema_matches_count": _truthy_count(
            requested, "approval_record_schema_matches"
        ),
        "approval_scope_matches_count": _truthy_count(
            requested, "approval_scope_matches"
        ),
        "approval_operation_matches_count": _truthy_count(
            requested, "approval_operation_matches"
        ),
        "explicit_unlock_approval_present_count": _truthy_count(
            requested, "explicit_unlock_approval_present"
        ),
        "approval_requires_read_only_live_preflight_count": _truthy_count(
            requested, "approval_requires_read_only_live_preflight"
        ),
        "approval_blocks_save_delete_rename_count": _truthy_count(
            requested, "approval_blocks_save_delete_rename"
        ),
        "approval_blocks_live_writes_count": _truthy_count(
            requested, "approval_blocks_live_writes"
        ),
        "live_preflight_schema_matches_count": _truthy_count(
            requested, "live_preflight_schema_matches"
        ),
        "live_preflight_passed_count": _truthy_count(
            requested, "live_preflight_passed"
        ),
        "live_preflight_requested_count": _truthy_count(
            requested, "live_preflight_requested"
        ),
        "live_preflight_result_present_count": _truthy_count(
            requested, "live_preflight_result_present"
        ),
        "live_preflight_read_only_result_passed_count": _truthy_count(
            requested, "live_preflight_read_only_result_passed"
        ),
        "live_preflight_read_only_only_count": _truthy_count(
            requested, "live_preflight_read_only_only"
        ),
        "live_preflight_no_authoring_attempted_count": _truthy_count(
            requested, "live_preflight_no_authoring_attempted"
        ),
        "live_preflight_no_save_delete_attempted_count": _truthy_count(
            requested, "live_preflight_no_save_delete_attempted"
        ),
        "live_preflight_does_not_pass_write_gate_count": _truthy_count(
            requested, "live_preflight_does_not_pass_write_gate"
        ),
        "unlock_record_admissible_count": _truthy_count(
            requested, "unlock_record_admissible"
        ),
        "durable_safety_boundary_unlock_ready_count": _truthy_count(
            requested, "durable_safety_boundary_unlock_ready"
        ),
        "durable_safety_boundary_unlocked_count": _truthy_count(
            requested, "durable_safety_boundary_unlocked"
        ),
        "durable_authoring_enabled_count": _truthy_count(
            requested, "durable_authoring_enabled"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "save_delete_rename_allowed_count": _truthy_count(
            requested, "save_delete_rename_allowed"
        ),
        "live_durable_authoring_allowed_count": _truthy_count(
            requested, "live_durable_authoring_allowed"
        ),
    }
    summary.update({key: _sum_count(requested, key) for key in BLOCKED_OUTPUT_COUNT_KEYS})
    return summary
