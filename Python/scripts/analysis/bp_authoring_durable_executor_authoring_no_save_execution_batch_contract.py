#!/usr/bin/env python
"""
Sections 186-192 durable executor authoring no-save execution batch contract.

This batched contract opens the offline no-save execution path after Section
185 durable authoring enablement. It admits executor open, command allow,
dispatch, execution evidence, completion/readback, and final no-save release
readiness as a single fast-path proof. It does not allow live durable writes,
asset modifications, package dirtying, save, delete, rename, or final durable
release readiness.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_enable_after_safety_boundary_unlock_contract as enable_after_unlock


DURABLE_EXECUTOR_AUTHORING_NO_SAVE_EXECUTION_BATCH_SCHEMA = (
    "section_186_192_durable_executor_authoring_no_save_execution_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_NO_SAVE_EXECUTION_BATCH_SUMMARY_SCHEMA = (
    "section_186_192_durable_executor_authoring_no_save_execution_batch_summary_v1"
)
SECTION_185_ENABLE_SUMMARY_SCHEMA = (
    enable_after_unlock
    .DURABLE_EXECUTOR_AUTHORING_ENABLE_AFTER_SAFETY_BOUNDARY_UNLOCK_SUMMARY_SCHEMA
)
UPSTREAM_BLOCKED_OUTPUT_COUNT_KEYS = enable_after_unlock.BLOCKED_OUTPUT_COUNT_KEYS
NO_SAVE_PATH_COUNT_KEYS = (
    "durable_authoring_command_admission_promoted_count",
    "durable_authoring_command_contract_started_count",
    "durable_authoring_command_contract_accepted_count",
    "durable_authoring_command_allowed_count",
    "durable_authoring_command_dispatched_count",
    "durable_authoring_command_executed_count",
    "durable_authoring_command_completed_count",
    "durable_executor_command_path_opened_count",
    "durable_executor_command_path_allowed_count",
    "durable_executor_open_promotion_barrier_promoted_count",
    "durable_executor_open_promotion_barrier_started_count",
    "durable_executor_open_promotion_barrier_accepted_count",
    "durable_executor_open_contract_started_count",
    "durable_executor_open_contract_accepted_count",
    "durable_executor_open_performed_count",
    "durable_executor_activated_count",
    "durable_executor_opened_count",
)
BLOCKED_OUTPUT_COUNT_KEYS = tuple(
    key
    for key in UPSTREAM_BLOCKED_OUTPUT_COUNT_KEYS
    if key not in NO_SAVE_PATH_COUNT_KEYS
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


def build_durable_executor_authoring_no_save_execution_batch_contract(
    requested: bool,
    section_185_enable_summary: Dict[str, Any],
) -> Dict[str, Any]:
    blocked_counts = _blocked_output_counts(section_185_enable_summary)
    section_185_summary_schema_matches = bool(
        section_185_enable_summary.get("schema") == SECTION_185_ENABLE_SUMMARY_SCHEMA
    )
    section_185_summary_passed = bool(
        section_185_enable_summary.get("status") == "passed"
    )
    section_185_authoring_enabled = bool(
        section_185_enable_summary.get("durable_authoring_enabled_count") == 1
    )
    section_185_final_release_not_ready = bool(
        section_185_enable_summary.get("final_durable_release_ready_count") == 0
    )
    section_185_executor_open_blocked = bool(
        section_185_enable_summary.get("durable_executor_open_allowed_count") == 0
    )
    section_185_command_allow_blocked = bool(
        section_185_enable_summary.get("durable_authoring_command_allowed_count")
        == 0
    )
    section_185_save_delete_rename_blocked = bool(
        section_185_enable_summary.get("save_delete_rename_allowed_count") == 0
    )
    section_185_live_durable_authoring_blocked = bool(
        section_185_enable_summary.get("live_durable_authoring_allowed_count") == 0
    )
    blocked_outputs_zero = all(count == 0 for count in blocked_counts.values())
    no_save_execution_batch_admissible = bool(
        requested
        and section_185_summary_schema_matches
        and section_185_summary_passed
        and section_185_authoring_enabled
        and section_185_final_release_not_ready
        and section_185_executor_open_blocked
        and section_185_command_allow_blocked
        and section_185_save_delete_rename_blocked
        and section_185_live_durable_authoring_blocked
        and blocked_outputs_zero
    )

    return {
        "id": "durable_executor_authoring_no_save_execution_batch",
        "schema": DURABLE_EXECUTOR_AUTHORING_NO_SAVE_EXECUTION_BATCH_SCHEMA,
        "requested": requested,
        "section_185_summary_schema_matches": section_185_summary_schema_matches,
        "section_185_summary_passed": section_185_summary_passed,
        "section_185_authoring_enabled": section_185_authoring_enabled,
        "section_185_final_release_not_ready": section_185_final_release_not_ready,
        "section_185_executor_open_blocked": section_185_executor_open_blocked,
        "section_185_command_allow_blocked": section_185_command_allow_blocked,
        "section_185_save_delete_rename_blocked": (
            section_185_save_delete_rename_blocked
        ),
        "section_185_live_durable_authoring_blocked": (
            section_185_live_durable_authoring_blocked
        ),
        "blocked_outputs_zero": blocked_outputs_zero,
        "no_save_execution_batch_admissible": no_save_execution_batch_admissible,
        "section_186_executor_opened": no_save_execution_batch_admissible,
        "section_187_open_readiness_consolidated": no_save_execution_batch_admissible,
        "section_188_authoring_command_allowed": no_save_execution_batch_admissible,
        "section_189_command_dispatch_gate_open": no_save_execution_batch_admissible,
        "section_190_command_execution_evidence_gate_open": (
            no_save_execution_batch_admissible
        ),
        "section_191_completion_readback_ready": no_save_execution_batch_admissible,
        "section_192_final_no_save_release_ready": (
            no_save_execution_batch_admissible
        ),
        "durable_executor_open_allowed": no_save_execution_batch_admissible,
        "durable_executor_opened": no_save_execution_batch_admissible,
        "durable_authoring_command_allowed": no_save_execution_batch_admissible,
        "durable_authoring_command_dispatched": no_save_execution_batch_admissible,
        "durable_authoring_command_executed": no_save_execution_batch_admissible,
        "durable_authoring_command_completed": no_save_execution_batch_admissible,
        "final_no_save_release_ready": no_save_execution_batch_admissible,
        "durable_authoring_enabled": no_save_execution_batch_admissible,
        "durable_authoring_allowed": False,
        "final_durable_release_ready": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "save_delete_rename_allowed": False,
        "save_asset_allowed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        "live_durable_authoring_allowed": False,
        "live_command_dispatched": False,
        "live_command_executed": False,
        **{
            key: 1 if no_save_execution_batch_admissible else 0
            for key in NO_SAVE_PATH_COUNT_KEYS
        },
        **blocked_counts,
    }


def summarize_durable_executor_authoring_no_save_execution_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "no_save_execution_batch_admissible")
            == len(requested)
            and _truthy_count(requested, "section_186_executor_opened")
            == len(requested)
            and _truthy_count(requested, "section_187_open_readiness_consolidated")
            == len(requested)
            and _truthy_count(requested, "section_188_authoring_command_allowed")
            == len(requested)
            and _truthy_count(requested, "section_189_command_dispatch_gate_open")
            == len(requested)
            and _truthy_count(
                requested, "section_190_command_execution_evidence_gate_open"
            )
            == len(requested)
            and _truthy_count(requested, "section_191_completion_readback_ready")
            == len(requested)
            and _truthy_count(requested, "section_192_final_no_save_release_ready")
            == len(requested)
            and _truthy_count(requested, "durable_authoring_allowed") == 0
            and _truthy_count(requested, "final_durable_release_ready") == 0
            and _truthy_count(requested, "asset_write_performed") == 0
            and _truthy_count(requested, "package_dirty_marked") == 0
            and _truthy_count(requested, "save_delete_rename_allowed") == 0
            and _truthy_count(requested, "save_asset_allowed") == 0
            and _truthy_count(requested, "delete_asset_allowed") == 0
            and _truthy_count(requested, "rename_asset_allowed") == 0
            and _truthy_count(requested, "live_durable_authoring_allowed") == 0
            and _truthy_count(requested, "live_command_dispatched") == 0
            and _truthy_count(requested, "live_command_executed") == 0
            and all(_sum_count(requested, key) == 0 for key in BLOCKED_OUTPUT_COUNT_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_NO_SAVE_EXECUTION_BATCH_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_no_save_execution_batch_count": (
            len(requested)
        ),
        "section_185_summary_schema_matches_count": _truthy_count(
            requested, "section_185_summary_schema_matches"
        ),
        "section_185_summary_passed_count": _truthy_count(
            requested, "section_185_summary_passed"
        ),
        "section_185_authoring_enabled_count": _truthy_count(
            requested, "section_185_authoring_enabled"
        ),
        "section_185_final_release_not_ready_count": _truthy_count(
            requested, "section_185_final_release_not_ready"
        ),
        "section_185_executor_open_blocked_count": _truthy_count(
            requested, "section_185_executor_open_blocked"
        ),
        "section_185_command_allow_blocked_count": _truthy_count(
            requested, "section_185_command_allow_blocked"
        ),
        "section_185_save_delete_rename_blocked_count": _truthy_count(
            requested, "section_185_save_delete_rename_blocked"
        ),
        "section_185_live_durable_authoring_blocked_count": _truthy_count(
            requested, "section_185_live_durable_authoring_blocked"
        ),
        "blocked_outputs_zero_count": _truthy_count(
            requested, "blocked_outputs_zero"
        ),
        "no_save_execution_batch_admissible_count": _truthy_count(
            requested, "no_save_execution_batch_admissible"
        ),
        "section_186_executor_opened_count": _truthy_count(
            requested, "section_186_executor_opened"
        ),
        "section_187_open_readiness_consolidated_count": _truthy_count(
            requested, "section_187_open_readiness_consolidated"
        ),
        "section_188_authoring_command_allowed_count": _truthy_count(
            requested, "section_188_authoring_command_allowed"
        ),
        "section_189_command_dispatch_gate_open_count": _truthy_count(
            requested, "section_189_command_dispatch_gate_open"
        ),
        "section_190_command_execution_evidence_gate_open_count": _truthy_count(
            requested, "section_190_command_execution_evidence_gate_open"
        ),
        "section_191_completion_readback_ready_count": _truthy_count(
            requested, "section_191_completion_readback_ready"
        ),
        "section_192_final_no_save_release_ready_count": _truthy_count(
            requested, "section_192_final_no_save_release_ready"
        ),
        "durable_executor_open_allowed_count": _truthy_count(
            requested, "durable_executor_open_allowed"
        ),
        "durable_executor_opened_count": _truthy_count(
            requested, "durable_executor_opened"
        ),
        "durable_authoring_command_allowed_count": _truthy_count(
            requested, "durable_authoring_command_allowed"
        ),
        "durable_authoring_command_dispatched_count": _truthy_count(
            requested, "durable_authoring_command_dispatched"
        ),
        "durable_authoring_command_executed_count": _truthy_count(
            requested, "durable_authoring_command_executed"
        ),
        "durable_authoring_command_completed_count": _truthy_count(
            requested, "durable_authoring_command_completed"
        ),
        "final_no_save_release_ready_count": _truthy_count(
            requested, "final_no_save_release_ready"
        ),
        "durable_authoring_enabled_count": _truthy_count(
            requested, "durable_authoring_enabled"
        ),
        "durable_authoring_allowed_count": _truthy_count(
            requested, "durable_authoring_allowed"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "asset_write_performed_count": _truthy_count(
            requested, "asset_write_performed"
        ),
        "package_dirty_marked_count": _truthy_count(
            requested, "package_dirty_marked"
        ),
        "save_delete_rename_allowed_count": _truthy_count(
            requested, "save_delete_rename_allowed"
        ),
        "save_asset_allowed_count": _truthy_count(
            requested, "save_asset_allowed"
        ),
        "delete_asset_allowed_count": _truthy_count(
            requested, "delete_asset_allowed"
        ),
        "rename_asset_allowed_count": _truthy_count(
            requested, "rename_asset_allowed"
        ),
        "live_durable_authoring_allowed_count": _truthy_count(
            requested, "live_durable_authoring_allowed"
        ),
        "live_command_dispatched_count": _truthy_count(
            requested, "live_command_dispatched"
        ),
        "live_command_executed_count": _truthy_count(
            requested, "live_command_executed"
        ),
    }
    summary.update({key: _sum_count(requested, key) for key in NO_SAVE_PATH_COUNT_KEYS})
    summary.update({key: _sum_count(requested, key) for key in BLOCKED_OUTPUT_COUNT_KEYS})
    return summary
