#!/usr/bin/env python
"""
Section 184 durable executor authoring safety boundary unlock contract.

This contract promotes the Section 183 unlock-ready state into an unlocked
safety boundary. It still does not enable durable authoring, final release
readiness, save, delete, rename, cleanup, or live durable write commands.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_safety_boundary_unlock_record_contract as unlock_record


DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_SCHEMA = (
    "section_184_durable_executor_authoring_safety_boundary_unlock_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_SUMMARY_SCHEMA = (
    "section_184_durable_executor_authoring_safety_boundary_unlock_summary_v1"
)
SECTION_183_UNLOCK_RECORD_SUMMARY_SCHEMA = (
    unlock_record
    .DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_RECORD_SUMMARY_SCHEMA
)
BLOCKED_OUTPUT_COUNT_KEYS = unlock_record.BLOCKED_OUTPUT_COUNT_KEYS


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _blocked_output_counts(summary: Dict[str, Any]) -> Dict[str, int]:
    return {
        key: int(summary.get(key, 0) or 0)
        for key in BLOCKED_OUTPUT_COUNT_KEYS
    }


def build_durable_executor_authoring_safety_boundary_unlock_contract(
    requested: bool,
    section_183_unlock_record_summary: Dict[str, Any],
) -> Dict[str, Any]:
    blocked_counts = _blocked_output_counts(section_183_unlock_record_summary)
    section_183_summary_schema_matches = bool(
        section_183_unlock_record_summary.get("schema")
        == SECTION_183_UNLOCK_RECORD_SUMMARY_SCHEMA
    )
    section_183_summary_passed = bool(
        section_183_unlock_record_summary.get("status") == "passed"
    )
    section_183_unlock_record_admissible = bool(
        section_183_unlock_record_summary.get("unlock_record_admissible_count") == 1
    )
    section_183_unlock_ready = bool(
        section_183_unlock_record_summary.get(
            "durable_safety_boundary_unlock_ready_count"
        )
        == 1
    )
    section_183_unlocked_absent = bool(
        section_183_unlock_record_summary.get(
            "durable_safety_boundary_unlocked_count"
        )
        == 0
    )
    section_183_authoring_disabled = bool(
        section_183_unlock_record_summary.get("durable_authoring_enabled_count")
        == 0
    )
    section_183_final_release_not_ready = bool(
        section_183_unlock_record_summary.get("final_durable_release_ready_count")
        == 0
    )
    section_183_save_delete_rename_blocked = bool(
        section_183_unlock_record_summary.get("save_delete_rename_allowed_count")
        == 0
    )
    section_183_live_durable_authoring_blocked = bool(
        section_183_unlock_record_summary.get("live_durable_authoring_allowed_count")
        == 0
    )
    blocked_outputs_zero = all(count == 0 for count in blocked_counts.values())
    durable_safety_boundary_unlocked = bool(
        requested
        and section_183_summary_schema_matches
        and section_183_summary_passed
        and section_183_unlock_record_admissible
        and section_183_unlock_ready
        and section_183_unlocked_absent
        and section_183_authoring_disabled
        and section_183_final_release_not_ready
        and section_183_save_delete_rename_blocked
        and section_183_live_durable_authoring_blocked
        and blocked_outputs_zero
    )
    return {
        "id": "durable_executor_authoring_safety_boundary_unlock",
        "schema": DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_SCHEMA,
        "requested": requested,
        "section_183_summary_schema_matches": section_183_summary_schema_matches,
        "section_183_summary_passed": section_183_summary_passed,
        "section_183_unlock_record_admissible": (
            section_183_unlock_record_admissible
        ),
        "section_183_unlock_ready": section_183_unlock_ready,
        "section_183_unlocked_absent": section_183_unlocked_absent,
        "section_183_authoring_disabled": section_183_authoring_disabled,
        "section_183_final_release_not_ready": section_183_final_release_not_ready,
        "section_183_save_delete_rename_blocked": (
            section_183_save_delete_rename_blocked
        ),
        "section_183_live_durable_authoring_blocked": (
            section_183_live_durable_authoring_blocked
        ),
        "blocked_outputs_zero": blocked_outputs_zero,
        "durable_safety_boundary_unlocked": durable_safety_boundary_unlocked,
        "durable_authoring_enabled": False,
        "final_durable_release_ready": False,
        "durable_executor_open_allowed": False,
        "durable_authoring_command_allowed": False,
        "save_delete_rename_allowed": False,
        "live_durable_authoring_allowed": False,
        **blocked_counts,
    }


def summarize_durable_executor_authoring_safety_boundary_unlocks(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "durable_safety_boundary_unlocked")
            == len(requested)
            and _truthy_count(requested, "durable_authoring_enabled") == 0
            and _truthy_count(requested, "final_durable_release_ready") == 0
            and _truthy_count(requested, "durable_executor_open_allowed") == 0
            and _truthy_count(requested, "durable_authoring_command_allowed") == 0
            and _truthy_count(requested, "save_delete_rename_allowed") == 0
            and _truthy_count(requested, "live_durable_authoring_allowed") == 0
            and all(_sum_count(requested, key) == 0 for key in BLOCKED_OUTPUT_COUNT_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_safety_boundary_unlock_count": (
            len(requested)
        ),
        "section_183_summary_schema_matches_count": _truthy_count(
            requested, "section_183_summary_schema_matches"
        ),
        "section_183_summary_passed_count": _truthy_count(
            requested, "section_183_summary_passed"
        ),
        "section_183_unlock_record_admissible_count": _truthy_count(
            requested, "section_183_unlock_record_admissible"
        ),
        "section_183_unlock_ready_count": _truthy_count(
            requested, "section_183_unlock_ready"
        ),
        "section_183_unlocked_absent_count": _truthy_count(
            requested, "section_183_unlocked_absent"
        ),
        "section_183_authoring_disabled_count": _truthy_count(
            requested, "section_183_authoring_disabled"
        ),
        "section_183_final_release_not_ready_count": _truthy_count(
            requested, "section_183_final_release_not_ready"
        ),
        "section_183_save_delete_rename_blocked_count": _truthy_count(
            requested, "section_183_save_delete_rename_blocked"
        ),
        "section_183_live_durable_authoring_blocked_count": _truthy_count(
            requested, "section_183_live_durable_authoring_blocked"
        ),
        "blocked_outputs_zero_count": _truthy_count(
            requested, "blocked_outputs_zero"
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
        "durable_executor_open_allowed_count": _truthy_count(
            requested, "durable_executor_open_allowed"
        ),
        "durable_authoring_command_allowed_count": _truthy_count(
            requested, "durable_authoring_command_allowed"
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
