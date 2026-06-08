#!/usr/bin/env python
"""
Section 185 durable executor authoring enable after safety boundary unlock.

This contract enables durable authoring only after Section 184 unlocked the
safety boundary. It does not open the executor, allow authoring commands, allow
save/delete/rename, mark final release readiness, or allow live durable writes.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_safety_boundary_unlock_contract as unlock


DURABLE_EXECUTOR_AUTHORING_ENABLE_AFTER_SAFETY_BOUNDARY_UNLOCK_SCHEMA = (
    "section_185_durable_executor_authoring_enable_after_safety_boundary_unlock_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_ENABLE_AFTER_SAFETY_BOUNDARY_UNLOCK_SUMMARY_SCHEMA = (
    "section_185_durable_executor_authoring_enable_after_safety_boundary_unlock_summary_v1"
)
SECTION_184_UNLOCK_SUMMARY_SCHEMA = (
    unlock.DURABLE_EXECUTOR_AUTHORING_SAFETY_BOUNDARY_UNLOCK_SUMMARY_SCHEMA
)
UPSTREAM_BLOCKED_OUTPUT_COUNT_KEYS = unlock.BLOCKED_OUTPUT_COUNT_KEYS
BLOCKED_OUTPUT_COUNT_KEYS = tuple(
    key
    for key in UPSTREAM_BLOCKED_OUTPUT_COUNT_KEYS
    if key != "durable_authoring_enabled_count"
)


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _blocked_output_counts(summary: Dict[str, Any]) -> Dict[str, int]:
    return {
        key: int(summary.get(key, 0) or 0)
        for key in BLOCKED_OUTPUT_COUNT_KEYS
    }


def build_durable_executor_authoring_enable_after_safety_boundary_unlock_contract(
    requested: bool,
    section_184_safety_boundary_unlock_summary: Dict[str, Any],
) -> Dict[str, Any]:
    blocked_counts = _blocked_output_counts(section_184_safety_boundary_unlock_summary)
    section_184_summary_schema_matches = bool(
        section_184_safety_boundary_unlock_summary.get("schema")
        == SECTION_184_UNLOCK_SUMMARY_SCHEMA
    )
    section_184_summary_passed = bool(
        section_184_safety_boundary_unlock_summary.get("status") == "passed"
    )
    section_184_safety_boundary_unlocked = bool(
        section_184_safety_boundary_unlock_summary.get(
            "durable_safety_boundary_unlocked_count"
        )
        == 1
    )
    section_184_authoring_disabled = bool(
        section_184_safety_boundary_unlock_summary.get(
            "durable_authoring_enabled_count"
        )
        == 0
    )
    section_184_final_release_not_ready = bool(
        section_184_safety_boundary_unlock_summary.get(
            "final_durable_release_ready_count"
        )
        == 0
    )
    section_184_executor_open_blocked = bool(
        section_184_safety_boundary_unlock_summary.get(
            "durable_executor_open_allowed_count"
        )
        == 0
    )
    section_184_authoring_command_blocked = bool(
        section_184_safety_boundary_unlock_summary.get(
            "durable_authoring_command_allowed_count"
        )
        == 0
    )
    section_184_save_delete_rename_blocked = bool(
        section_184_safety_boundary_unlock_summary.get(
            "save_delete_rename_allowed_count"
        )
        == 0
    )
    section_184_live_durable_authoring_blocked = bool(
        section_184_safety_boundary_unlock_summary.get(
            "live_durable_authoring_allowed_count"
        )
        == 0
    )
    blocked_outputs_zero = all(count == 0 for count in blocked_counts.values())
    durable_authoring_enable_admissible = bool(
        requested
        and section_184_summary_schema_matches
        and section_184_summary_passed
        and section_184_safety_boundary_unlocked
        and section_184_authoring_disabled
        and section_184_final_release_not_ready
        and section_184_executor_open_blocked
        and section_184_authoring_command_blocked
        and section_184_save_delete_rename_blocked
        and section_184_live_durable_authoring_blocked
        and blocked_outputs_zero
    )
    return {
        "id": "durable_executor_authoring_enable_after_safety_boundary_unlock",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_ENABLE_AFTER_SAFETY_BOUNDARY_UNLOCK_SCHEMA
        ),
        "requested": requested,
        "section_184_summary_schema_matches": section_184_summary_schema_matches,
        "section_184_summary_passed": section_184_summary_passed,
        "section_184_safety_boundary_unlocked": section_184_safety_boundary_unlocked,
        "section_184_authoring_disabled": section_184_authoring_disabled,
        "section_184_final_release_not_ready": section_184_final_release_not_ready,
        "section_184_executor_open_blocked": section_184_executor_open_blocked,
        "section_184_authoring_command_blocked": (
            section_184_authoring_command_blocked
        ),
        "section_184_save_delete_rename_blocked": (
            section_184_save_delete_rename_blocked
        ),
        "section_184_live_durable_authoring_blocked": (
            section_184_live_durable_authoring_blocked
        ),
        "blocked_outputs_zero": blocked_outputs_zero,
        "durable_authoring_enable_admissible": durable_authoring_enable_admissible,
        "durable_authoring_enabled": durable_authoring_enable_admissible,
        "final_durable_release_ready": False,
        "durable_executor_open_allowed": False,
        "durable_authoring_command_allowed": False,
        "save_delete_rename_allowed": False,
        "live_durable_authoring_allowed": False,
        **blocked_counts,
    }


def summarize_durable_executor_authoring_enable_after_safety_boundary_unlocks(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "durable_authoring_enable_admissible")
            == len(requested)
            and _truthy_count(requested, "durable_authoring_enabled")
            == len(requested)
            and _truthy_count(requested, "final_durable_release_ready") == 0
            and _truthy_count(requested, "durable_executor_open_allowed") == 0
            and _truthy_count(requested, "durable_authoring_command_allowed") == 0
            and _truthy_count(requested, "save_delete_rename_allowed") == 0
            and _truthy_count(requested, "live_durable_authoring_allowed") == 0
            and all(_sum_count(requested, key) == 0 for key in BLOCKED_OUTPUT_COUNT_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_ENABLE_AFTER_SAFETY_BOUNDARY_UNLOCK_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_enable_after_safety_boundary_unlock_count": (
            len(requested)
        ),
        "section_184_summary_schema_matches_count": _truthy_count(
            requested, "section_184_summary_schema_matches"
        ),
        "section_184_summary_passed_count": _truthy_count(
            requested, "section_184_summary_passed"
        ),
        "section_184_safety_boundary_unlocked_count": _truthy_count(
            requested, "section_184_safety_boundary_unlocked"
        ),
        "section_184_authoring_disabled_count": _truthy_count(
            requested, "section_184_authoring_disabled"
        ),
        "section_184_final_release_not_ready_count": _truthy_count(
            requested, "section_184_final_release_not_ready"
        ),
        "section_184_executor_open_blocked_count": _truthy_count(
            requested, "section_184_executor_open_blocked"
        ),
        "section_184_authoring_command_blocked_count": _truthy_count(
            requested, "section_184_authoring_command_blocked"
        ),
        "section_184_save_delete_rename_blocked_count": _truthy_count(
            requested, "section_184_save_delete_rename_blocked"
        ),
        "section_184_live_durable_authoring_blocked_count": _truthy_count(
            requested, "section_184_live_durable_authoring_blocked"
        ),
        "blocked_outputs_zero_count": _truthy_count(
            requested, "blocked_outputs_zero"
        ),
        "durable_authoring_enable_admissible_count": _truthy_count(
            requested, "durable_authoring_enable_admissible"
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
