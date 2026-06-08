#!/usr/bin/env python
"""
Sections 201-208 durable executor authoring save-gate open/admission batch.

This contract promotes Section 200 save-gate preflight readiness into an
offline save-gate-open and save-command-admission dry-run path. It does not
dispatch or execute a live save command, run save=true/save_asset, dirty a
package, delete, rename, or mark final durable release readiness.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_save_gate_preflight_batch_contract as save_gate_preflight


DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_OPEN_ADMISSION_BATCH_SCHEMA = (
    "section_201_208_durable_executor_authoring_save_gate_open_admission_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_OPEN_ADMISSION_BATCH_SUMMARY_SCHEMA = (
    "section_201_208_durable_executor_authoring_save_gate_open_admission_batch_summary_v1"
)
SECTION_193_200_SAVE_GATE_PREFLIGHT_SUMMARY_SCHEMA = (
    save_gate_preflight
    .DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_PREFLIGHT_BATCH_SUMMARY_SCHEMA
)
UPSTREAM_SAVE_GATE_PREFLIGHT_REQUIRED_COUNT_KEYS = (
    "section_186_192_summary_schema_matches_count",
    "section_186_192_summary_passed_count",
    "section_186_192_no_save_ready_count",
    "section_186_192_write_outputs_blocked_count",
    "section_193_save_target_declared_count",
    "section_194_ownership_marker_revalidated_count",
    "section_195_rollback_policy_revalidated_count",
    "section_196_overwrite_rename_decision_ready_count",
    "section_197_read_only_save_preflight_ready_count",
    "section_198_save_command_admission_preflight_ready_count",
    "section_199_save_gate_open_review_ready_count",
    "section_200_final_save_gate_preflight_ready_count",
    "save_target_declared_count",
    "save_target_package_allowlisted_count",
    "save_target_read_only_exists_check_ready_count",
    "ownership_marker_revalidated_count",
    "rollback_policy_revalidated_count",
    "overwrite_rename_decision_ready_count",
    "read_only_save_preflight_ready_count",
    "save_command_admission_preflight_ready_count",
    "save_gate_open_review_ready_count",
    "save_gate_preflight_ready_count",
    "durable_authoring_enabled_count",
    "durable_executor_opened_count",
    "durable_authoring_command_no_save_execution_ready_count",
    "final_no_save_release_ready_count",
)
UPSTREAM_MUST_BE_CLOSED_COUNT_KEYS = (
    "durable_authoring_allowed_count",
    "final_durable_release_ready_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
    "save_gate_open_allowed_count",
    "save_command_admitted_count",
    "save_command_dispatched_count",
    "save_command_executed_count",
    "save_true_allowed_count",
    "save_asset_allowed_count",
    "compile_save_allowed_count",
    "save_delete_rename_allowed_count",
    "delete_asset_allowed_count",
    "rename_asset_allowed_count",
    "live_durable_authoring_allowed_count",
    "live_command_dispatched_count",
    "live_command_executed_count",
)
SAVE_GATE_OPEN_ADMISSION_PATH_COUNT_KEYS = (
    "explicit_save_gate_open_approved_count",
    "save_gate_open_allowed_count",
    "save_gate_opened_count",
    "save_command_admission_contract_started_count",
    "save_command_admission_contract_accepted_count",
    "save_command_admitted_count",
    "save_command_dry_run_allowed_count",
    "save_command_dispatch_dry_run_ready_count",
    "save_command_execution_dry_run_ready_count",
    "save_command_result_readback_dry_run_ready_count",
    "final_pre_save_execution_ready_count",
)
WRITE_AND_LIVE_BLOCKED_OUTPUT_COUNT_KEYS = (
    "durable_authoring_allowed_count",
    "final_durable_release_ready_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
    "save_command_dispatched_count",
    "save_command_executed_count",
    "save_true_allowed_count",
    "save_asset_allowed_count",
    "compile_save_allowed_count",
    "save_delete_rename_allowed_count",
    "delete_asset_allowed_count",
    "rename_asset_allowed_count",
    "live_durable_authoring_allowed_count",
    "live_command_dispatched_count",
    "live_command_executed_count",
)


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _count_is_one(summary: Dict[str, Any], key: str) -> bool:
    return bool(summary.get(key) == 1)


def _count_is_zero(summary: Dict[str, Any], key: str) -> bool:
    return bool(int(summary.get(key, 0) or 0) == 0)


def _closed_output_counts(summary: Dict[str, Any]) -> Dict[str, int]:
    return {
        key: int(summary.get(key, 0) or 0)
        for key in WRITE_AND_LIVE_BLOCKED_OUTPUT_COUNT_KEYS
    }


def build_durable_executor_authoring_save_gate_open_admission_batch_contract(
    requested: bool,
    section_193_200_save_gate_preflight_summary: Dict[str, Any],
) -> Dict[str, Any]:
    blocked_counts = _closed_output_counts(
        section_193_200_save_gate_preflight_summary
    )
    section_193_200_summary_schema_matches = bool(
        section_193_200_save_gate_preflight_summary.get("schema")
        == SECTION_193_200_SAVE_GATE_PREFLIGHT_SUMMARY_SCHEMA
    )
    section_193_200_summary_passed = bool(
        section_193_200_save_gate_preflight_summary.get("status") == "passed"
    )
    upstream_save_gate_preflight_ready = all(
        _count_is_one(section_193_200_save_gate_preflight_summary, key)
        for key in UPSTREAM_SAVE_GATE_PREFLIGHT_REQUIRED_COUNT_KEYS
    )
    upstream_save_gate_still_closed = all(
        _count_is_zero(section_193_200_save_gate_preflight_summary, key)
        for key in UPSTREAM_MUST_BE_CLOSED_COUNT_KEYS
    )
    upstream_write_and_live_outputs_blocked = all(
        count == 0 for count in blocked_counts.values()
    )
    explicit_save_gate_open_approved = bool(
        requested
        and section_193_200_summary_schema_matches
        and section_193_200_summary_passed
        and upstream_save_gate_preflight_ready
        and upstream_save_gate_still_closed
        and upstream_write_and_live_outputs_blocked
    )
    save_gate_open_allowed = explicit_save_gate_open_approved
    save_gate_opened = save_gate_open_allowed
    save_command_admission_contract_started = save_gate_opened
    save_command_admission_contract_accepted = (
        save_command_admission_contract_started
    )
    save_command_admitted = save_command_admission_contract_accepted
    save_command_dry_run_allowed = save_command_admitted
    save_command_dispatch_dry_run_ready = save_command_dry_run_allowed
    save_command_execution_dry_run_ready = save_command_dispatch_dry_run_ready
    save_command_result_readback_dry_run_ready = (
        save_command_execution_dry_run_ready
    )
    final_pre_save_execution_ready = save_command_result_readback_dry_run_ready

    return {
        "id": "durable_executor_authoring_save_gate_open_admission_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_OPEN_ADMISSION_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_193_200_summary_schema_matches": (
            section_193_200_summary_schema_matches
        ),
        "section_193_200_summary_passed": section_193_200_summary_passed,
        "section_193_200_save_gate_preflight_ready": (
            upstream_save_gate_preflight_ready
        ),
        "section_193_200_save_gate_still_closed": (
            upstream_save_gate_still_closed
        ),
        "section_193_200_write_and_live_outputs_blocked": (
            upstream_write_and_live_outputs_blocked
        ),
        "explicit_save_gate_open_approved": explicit_save_gate_open_approved,
        "save_gate_open_allowed": save_gate_open_allowed,
        "save_gate_opened": save_gate_opened,
        "save_command_admission_contract_started": (
            save_command_admission_contract_started
        ),
        "save_command_admission_contract_accepted": (
            save_command_admission_contract_accepted
        ),
        "save_command_admitted": save_command_admitted,
        "save_command_dry_run_allowed": save_command_dry_run_allowed,
        "save_command_dispatch_dry_run_ready": (
            save_command_dispatch_dry_run_ready
        ),
        "save_command_execution_dry_run_ready": (
            save_command_execution_dry_run_ready
        ),
        "save_command_result_readback_dry_run_ready": (
            save_command_result_readback_dry_run_ready
        ),
        "final_pre_save_execution_ready": final_pre_save_execution_ready,
        "section_201_explicit_save_gate_open_approved": (
            explicit_save_gate_open_approved
        ),
        "section_202_save_gate_opened": save_gate_opened,
        "section_203_save_command_admission_contract_accepted": (
            save_command_admission_contract_accepted
        ),
        "section_204_save_command_admitted": save_command_admitted,
        "section_205_save_command_dispatch_dry_run_ready": (
            save_command_dispatch_dry_run_ready
        ),
        "section_206_save_command_execution_dry_run_ready": (
            save_command_execution_dry_run_ready
        ),
        "section_207_save_command_result_readback_dry_run_ready": (
            save_command_result_readback_dry_run_ready
        ),
        "section_208_final_pre_save_execution_ready": (
            final_pre_save_execution_ready
        ),
        "durable_authoring_enabled": final_pre_save_execution_ready,
        "durable_executor_opened": final_pre_save_execution_ready,
        "durable_authoring_command_no_save_execution_ready": (
            final_pre_save_execution_ready
        ),
        "final_no_save_release_ready": final_pre_save_execution_ready,
        "durable_authoring_save_gate_preflight_ready": (
            final_pre_save_execution_ready
        ),
        "save_command_admission_preflight_ready": (
            final_pre_save_execution_ready
        ),
        "durable_authoring_allowed": False,
        "final_durable_release_ready": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "save_command_dispatched": False,
        "save_command_executed": False,
        "save_true_allowed": False,
        "save_asset_allowed": False,
        "compile_save_allowed": False,
        "save_delete_rename_allowed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        "live_durable_authoring_allowed": False,
        "live_command_dispatched": False,
        "live_command_executed": False,
        **{
            key: 1 if final_pre_save_execution_ready else 0
            for key in SAVE_GATE_OPEN_ADMISSION_PATH_COUNT_KEYS
        },
        **blocked_counts,
    }


def summarize_durable_executor_authoring_save_gate_open_admission_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "final_pre_save_execution_ready")
            == len(requested)
            and _truthy_count(
                requested, "section_201_explicit_save_gate_open_approved"
            )
            == len(requested)
            and _truthy_count(requested, "section_202_save_gate_opened")
            == len(requested)
            and _truthy_count(
                requested,
                "section_203_save_command_admission_contract_accepted",
            )
            == len(requested)
            and _truthy_count(requested, "section_204_save_command_admitted")
            == len(requested)
            and _truthy_count(
                requested, "section_205_save_command_dispatch_dry_run_ready"
            )
            == len(requested)
            and _truthy_count(
                requested, "section_206_save_command_execution_dry_run_ready"
            )
            == len(requested)
            and _truthy_count(
                requested,
                "section_207_save_command_result_readback_dry_run_ready",
            )
            == len(requested)
            and _truthy_count(
                requested, "section_208_final_pre_save_execution_ready"
            )
            == len(requested)
            and _truthy_count(requested, "save_gate_open_allowed")
            == len(requested)
            and _truthy_count(requested, "save_command_admitted")
            == len(requested)
            and _truthy_count(requested, "durable_authoring_allowed") == 0
            and _truthy_count(requested, "final_durable_release_ready") == 0
            and _truthy_count(requested, "asset_write_performed") == 0
            and _truthy_count(requested, "package_dirty_marked") == 0
            and _truthy_count(requested, "save_command_dispatched") == 0
            and _truthy_count(requested, "save_command_executed") == 0
            and _truthy_count(requested, "save_true_allowed") == 0
            and _truthy_count(requested, "save_asset_allowed") == 0
            and _truthy_count(requested, "compile_save_allowed") == 0
            and _truthy_count(requested, "save_delete_rename_allowed") == 0
            and _truthy_count(requested, "delete_asset_allowed") == 0
            and _truthy_count(requested, "rename_asset_allowed") == 0
            and _truthy_count(requested, "live_durable_authoring_allowed") == 0
            and _truthy_count(requested, "live_command_dispatched") == 0
            and _truthy_count(requested, "live_command_executed") == 0
            and all(
                _sum_count(requested, key) == 0
                for key in WRITE_AND_LIVE_BLOCKED_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_OPEN_ADMISSION_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_save_gate_open_admission_batch_count": (
            len(requested)
        ),
        "section_193_200_summary_schema_matches_count": _truthy_count(
            requested, "section_193_200_summary_schema_matches"
        ),
        "section_193_200_summary_passed_count": _truthy_count(
            requested, "section_193_200_summary_passed"
        ),
        "section_193_200_save_gate_preflight_ready_count": _truthy_count(
            requested, "section_193_200_save_gate_preflight_ready"
        ),
        "section_193_200_save_gate_still_closed_count": _truthy_count(
            requested, "section_193_200_save_gate_still_closed"
        ),
        "section_193_200_write_and_live_outputs_blocked_count": (
            _truthy_count(
                requested,
                "section_193_200_write_and_live_outputs_blocked",
            )
        ),
        "section_201_explicit_save_gate_open_approved_count": _truthy_count(
            requested, "section_201_explicit_save_gate_open_approved"
        ),
        "section_202_save_gate_opened_count": _truthy_count(
            requested, "section_202_save_gate_opened"
        ),
        "section_203_save_command_admission_contract_accepted_count": (
            _truthy_count(
                requested,
                "section_203_save_command_admission_contract_accepted",
            )
        ),
        "section_204_save_command_admitted_count": _truthy_count(
            requested, "section_204_save_command_admitted"
        ),
        "section_205_save_command_dispatch_dry_run_ready_count": (
            _truthy_count(
                requested,
                "section_205_save_command_dispatch_dry_run_ready",
            )
        ),
        "section_206_save_command_execution_dry_run_ready_count": (
            _truthy_count(
                requested,
                "section_206_save_command_execution_dry_run_ready",
            )
        ),
        "section_207_save_command_result_readback_dry_run_ready_count": (
            _truthy_count(
                requested,
                "section_207_save_command_result_readback_dry_run_ready",
            )
        ),
        "section_208_final_pre_save_execution_ready_count": _truthy_count(
            requested, "section_208_final_pre_save_execution_ready"
        ),
        "durable_authoring_enabled_count": _truthy_count(
            requested, "durable_authoring_enabled"
        ),
        "durable_executor_opened_count": _truthy_count(
            requested, "durable_executor_opened"
        ),
        "durable_authoring_command_no_save_execution_ready_count": (
            _truthy_count(
                requested,
                "durable_authoring_command_no_save_execution_ready",
            )
        ),
        "final_no_save_release_ready_count": _truthy_count(
            requested, "final_no_save_release_ready"
        ),
        "durable_authoring_save_gate_preflight_ready_count": _truthy_count(
            requested, "durable_authoring_save_gate_preflight_ready"
        ),
        "save_command_admission_preflight_ready_count": _truthy_count(
            requested, "save_command_admission_preflight_ready"
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
        "save_command_dispatched_count": _truthy_count(
            requested, "save_command_dispatched"
        ),
        "save_command_executed_count": _truthy_count(
            requested, "save_command_executed"
        ),
        "save_true_allowed_count": _truthy_count(
            requested, "save_true_allowed"
        ),
        "save_asset_allowed_count": _truthy_count(
            requested, "save_asset_allowed"
        ),
        "compile_save_allowed_count": _truthy_count(
            requested, "compile_save_allowed"
        ),
        "save_delete_rename_allowed_count": _truthy_count(
            requested, "save_delete_rename_allowed"
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
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in SAVE_GATE_OPEN_ADMISSION_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in WRITE_AND_LIVE_BLOCKED_OUTPUT_COUNT_KEYS
        }
    )
    return summary
