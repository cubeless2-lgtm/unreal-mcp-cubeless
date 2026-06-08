#!/usr/bin/env python
"""
Section 182 durable executor authoring safety boundary unlock decision contract.

This contract reaches the unlock decision checkpoint after Section 181 release
boundary consolidation. It records that explicit unlock approval is still
absent and does not unlock durable authoring, open command paths, allow
authoring commands, dispatch live commands, execute live commands, modify
assets, dirty packages, save, delete/rename, cleanup, change code, or probe
live bridges.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_release_boundary_consolidation_contract as consolidation


DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_DECISION_SCHEMA = (
    "section_182_durable_executor_authoring_safety_boundary_unlock_decision_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_DECISION_RECORD_SCHEMA = (
    "section_182_durable_executor_authoring_safety_boundary_unlock_decision_record_v1"
)
DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_DECISION_SUMMARY_SCHEMA = (
    "section_182_durable_executor_authoring_safety_boundary_unlock_decision_summary_v1"
)
SECTION_181_CONSOLIDATION_SUMMARY_SCHEMA = (
    consolidation
    .DURABLE_EXECUTOR_AUTHORING_RELEASE_BOUNDARY_CONSOLIDATION_SUMMARY_SCHEMA
)
BLOCKED_OUTPUT_COUNT_KEYS = consolidation.BLOCKED_OUTPUT_COUNT_KEYS


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _blocked_output_counts(summary: Dict[str, Any]) -> Dict[str, int]:
    return {
        key: int(summary.get(key, 0) or 0)
        for key in BLOCKED_OUTPUT_COUNT_KEYS
    }


def build_durable_executor_authoring_safety_boundary_unlock_decision_contract(
    requested: bool,
    section_181_release_boundary_consolidation_summary: Dict[str, Any],
    unlock_decision_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    unlock_decision_record = unlock_decision_record or {}
    unlock_decision_record_present = bool(unlock_decision_record)
    blocked_counts = _blocked_output_counts(
        section_181_release_boundary_consolidation_summary
    )
    section_181_summary_schema_matches = bool(
        section_181_release_boundary_consolidation_summary.get("schema")
        == SECTION_181_CONSOLIDATION_SUMMARY_SCHEMA
    )
    section_181_summary_passed = bool(
        section_181_release_boundary_consolidation_summary.get("status") == "passed"
    )
    section_181_consolidated = bool(
        section_181_release_boundary_consolidation_summary.get(
            "release_boundary_consolidated_count"
        )
        == 1
    )
    section_181_unlock_ready_absent = bool(
        section_181_release_boundary_consolidation_summary.get(
            "durable_safety_boundary_unlock_ready_count"
        )
        == 0
    )
    section_181_authoring_disabled = bool(
        section_181_release_boundary_consolidation_summary.get(
            "durable_authoring_enabled_count"
        )
        == 0
    )
    section_181_final_release_not_ready = bool(
        section_181_release_boundary_consolidation_summary.get(
            "final_durable_release_ready_count"
        )
        == 0
    )
    blocked_outputs_zero = all(count == 0 for count in blocked_counts.values())
    record_schema_matches = bool(
        unlock_decision_record_present
        and unlock_decision_record.get("schema")
        == DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_DECISION_RECORD_SCHEMA
    )
    explicit_unlock_approval_present = bool(
        unlock_decision_record_present
        and unlock_decision_record.get(
            "explicit_durable_safety_boundary_unlock_approved"
        )
        is True
    )
    unlock_decision_record_absent = not unlock_decision_record_present
    explicit_unlock_approval_absent = not explicit_unlock_approval_present
    unlock_requires_explicit_user_approval = True
    unlock_decision_checkpoint_only = bool(
        requested
        and section_181_summary_schema_matches
        and section_181_summary_passed
        and section_181_consolidated
        and section_181_unlock_ready_absent
        and section_181_authoring_disabled
        and section_181_final_release_not_ready
        and blocked_outputs_zero
        and unlock_decision_record_absent
        and explicit_unlock_approval_absent
    )
    return {
        "id": "durable_executor_authoring_safety_boundary_unlock_decision",
        "schema": DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_DECISION_SCHEMA,
        "requested": requested,
        "section_181_summary_schema_matches": section_181_summary_schema_matches,
        "section_181_summary_passed": section_181_summary_passed,
        "section_181_release_boundary_consolidated": section_181_consolidated,
        "section_181_unlock_ready_absent": section_181_unlock_ready_absent,
        "section_181_authoring_disabled": section_181_authoring_disabled,
        "section_181_final_release_not_ready": section_181_final_release_not_ready,
        "blocked_outputs_zero": blocked_outputs_zero,
        "unlock_decision_record_present": unlock_decision_record_present,
        "unlock_decision_record_absent": unlock_decision_record_absent,
        "unlock_decision_record_schema_matches": record_schema_matches,
        "explicit_unlock_approval_present": explicit_unlock_approval_present,
        "explicit_unlock_approval_absent": explicit_unlock_approval_absent,
        "unlock_requires_explicit_user_approval": (
            unlock_requires_explicit_user_approval
        ),
        "unlock_decision_checkpoint_only": unlock_decision_checkpoint_only,
        "unlock_decision_checkpoint_reached": unlock_decision_checkpoint_only,
        "unlock_record_admissible": False,
        "durable_safety_boundary_unlock_ready": False,
        "durable_safety_boundary_unlocked": False,
        "durable_authoring_enabled": False,
        "final_durable_release_ready": False,
        "save_delete_rename_allowed": False,
        "live_durable_authoring_allowed": False,
        **blocked_counts,
    }


def summarize_durable_executor_authoring_safety_boundary_unlock_decisions(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "unlock_decision_checkpoint_only")
            == len(requested)
            and _truthy_count(requested, "unlock_record_admissible") == 0
            and _truthy_count(requested, "durable_safety_boundary_unlock_ready") == 0
            and _truthy_count(requested, "durable_safety_boundary_unlocked") == 0
            and _truthy_count(requested, "durable_authoring_enabled") == 0
            and _truthy_count(requested, "final_durable_release_ready") == 0
            and _truthy_count(requested, "save_delete_rename_allowed") == 0
            and _truthy_count(requested, "live_durable_authoring_allowed") == 0
            and all(_sum_count(requested, key) == 0 for key in BLOCKED_OUTPUT_COUNT_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_DECISION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_safety_boundary_unlock_decision_count": (
            len(requested)
        ),
        "unlock_decision_checkpoint_only_count": _truthy_count(
            requested, "unlock_decision_checkpoint_only"
        ),
        "unlock_decision_checkpoint_reached_count": _truthy_count(
            requested, "unlock_decision_checkpoint_reached"
        ),
        "section_181_summary_schema_matches_count": _truthy_count(
            requested, "section_181_summary_schema_matches"
        ),
        "section_181_summary_passed_count": _truthy_count(
            requested, "section_181_summary_passed"
        ),
        "section_181_release_boundary_consolidated_count": _truthy_count(
            requested, "section_181_release_boundary_consolidated"
        ),
        "section_181_unlock_ready_absent_count": _truthy_count(
            requested, "section_181_unlock_ready_absent"
        ),
        "section_181_authoring_disabled_count": _truthy_count(
            requested, "section_181_authoring_disabled"
        ),
        "section_181_final_release_not_ready_count": _truthy_count(
            requested, "section_181_final_release_not_ready"
        ),
        "blocked_outputs_zero_count": _truthy_count(
            requested, "blocked_outputs_zero"
        ),
        "unlock_decision_record_present_count": _truthy_count(
            requested, "unlock_decision_record_present"
        ),
        "unlock_decision_record_absent_count": _truthy_count(
            requested, "unlock_decision_record_absent"
        ),
        "unlock_decision_record_schema_matches_count": _truthy_count(
            requested, "unlock_decision_record_schema_matches"
        ),
        "explicit_unlock_approval_present_count": _truthy_count(
            requested, "explicit_unlock_approval_present"
        ),
        "explicit_unlock_approval_absent_count": _truthy_count(
            requested, "explicit_unlock_approval_absent"
        ),
        "unlock_requires_explicit_user_approval_count": _truthy_count(
            requested, "unlock_requires_explicit_user_approval"
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
