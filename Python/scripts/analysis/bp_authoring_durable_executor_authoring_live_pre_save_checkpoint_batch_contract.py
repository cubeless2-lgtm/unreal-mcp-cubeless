#!/usr/bin/env python
"""
Sections 209-216 durable executor authoring live pre-save checkpoint batch.

This contract records the final live read-only checkpoint before an actual
durable save dispatch. It requires a reachable UnrealMCP bridge, a successful
Ieta status call, read-only target/dirty-package evidence, and Section 208
pre-save execution readiness. It does not dispatch, execute, save, delete,
rename, dirty packages, or mark final durable release readiness.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_save_gate_open_admission_batch_contract as save_gate_open_admission
import bp_authoring_durable_executor_authoring_save_gate_preflight_batch_contract as save_gate_preflight


DURABLE_EXECUTOR_AUTHORING_LIVE_PRE_SAVE_CHECKPOINT_BATCH_SCHEMA = (
    "section_209_216_durable_executor_authoring_live_pre_save_checkpoint_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_LIVE_PRE_SAVE_CHECKPOINT_BATCH_SUMMARY_SCHEMA = (
    "section_209_216_durable_executor_authoring_live_pre_save_checkpoint_batch_summary_v1"
)
LIVE_PRE_SAVE_READ_ONLY_RESULT_SCHEMA = (
    "section_209_216_live_pre_save_read_only_result_v1"
)
SECTION_201_208_SAVE_GATE_OPEN_ADMISSION_SUMMARY_SCHEMA = (
    save_gate_open_admission
    .DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_OPEN_ADMISSION_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = save_gate_preflight.DEFAULT_SAVE_TARGET_ASSET_PATH
UPSTREAM_READY_COUNT_KEYS = (
    "section_201_explicit_save_gate_open_approved_count",
    "section_202_save_gate_opened_count",
    "section_203_save_command_admission_contract_accepted_count",
    "section_204_save_command_admitted_count",
    "section_205_save_command_dispatch_dry_run_ready_count",
    "section_206_save_command_execution_dry_run_ready_count",
    "section_207_save_command_result_readback_dry_run_ready_count",
    "section_208_final_pre_save_execution_ready_count",
    "explicit_save_gate_open_approved_count",
    "save_gate_open_allowed_count",
    "save_gate_opened_count",
    "save_command_admitted_count",
    "save_command_dry_run_allowed_count",
    "save_command_dispatch_dry_run_ready_count",
    "save_command_execution_dry_run_ready_count",
    "save_command_result_readback_dry_run_ready_count",
    "final_pre_save_execution_ready_count",
)
UPSTREAM_MUST_BE_CLOSED_COUNT_KEYS = (
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
LIVE_PRE_SAVE_CHECKPOINT_PATH_COUNT_KEYS = (
    "live_bridge_reachable_count",
    "ieta_slate_status_succeeded_count",
    "read_only_target_check_performed_count",
    "target_absent_for_new_temp_asset_count",
    "target_directory_absent_or_empty_count",
    "dirty_content_packages_zero_count",
    "dirty_map_packages_zero_count",
    "save_dispatch_final_checkpoint_ready_count",
    "actual_save_execution_requires_final_user_checkpoint_count",
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


def build_live_pre_save_read_only_result(
    *,
    bridge_reachable: bool,
    ieta_slate_status_succeeded: bool,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    asset_exists: bool = False,
    target_directory_exists: bool = False,
    dirty_content_package_count: int = 0,
    dirty_map_package_count: int = 0,
    read_only: bool = True,
) -> Dict[str, Any]:
    return {
        "schema": LIVE_PRE_SAVE_READ_ONLY_RESULT_SCHEMA,
        "read_only": read_only,
        "bridge_reachable": bridge_reachable,
        "ieta_slate_status_succeeded": ieta_slate_status_succeeded,
        "target_asset_path": target_asset_path,
        "asset_exists": asset_exists,
        "target_directory_exists": target_directory_exists,
        "dirty_content_package_count": dirty_content_package_count,
        "dirty_map_package_count": dirty_map_package_count,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "save_command_dispatched": False,
        "save_command_executed": False,
        "save_true_allowed": False,
        "save_asset_allowed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        "live_command_dispatched": False,
        "live_command_executed": False,
    }


def build_durable_executor_authoring_live_pre_save_checkpoint_batch_contract(
    requested: bool,
    section_201_208_save_gate_open_admission_summary: Dict[str, Any],
    live_pre_save_read_only_result: Dict[str, Any],
) -> Dict[str, Any]:
    blocked_counts = _closed_output_counts(
        section_201_208_save_gate_open_admission_summary
    )
    section_201_208_summary_schema_matches = bool(
        section_201_208_save_gate_open_admission_summary.get("schema")
        == SECTION_201_208_SAVE_GATE_OPEN_ADMISSION_SUMMARY_SCHEMA
    )
    section_201_208_summary_passed = bool(
        section_201_208_save_gate_open_admission_summary.get("status")
        == "passed"
    )
    upstream_pre_save_ready = all(
        _count_is_one(section_201_208_save_gate_open_admission_summary, key)
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_write_and_live_outputs_blocked = all(
        _count_is_zero(section_201_208_save_gate_open_admission_summary, key)
        for key in UPSTREAM_MUST_BE_CLOSED_COUNT_KEYS
    ) and all(count == 0 for count in blocked_counts.values())
    live_result_schema_matches = bool(
        live_pre_save_read_only_result.get("schema")
        == LIVE_PRE_SAVE_READ_ONLY_RESULT_SCHEMA
    )
    live_result_read_only = bool(live_pre_save_read_only_result.get("read_only"))
    live_bridge_reachable = bool(
        live_pre_save_read_only_result.get("bridge_reachable")
    )
    ieta_slate_status_succeeded = bool(
        live_pre_save_read_only_result.get("ieta_slate_status_succeeded")
    )
    target_path_matches = bool(
        live_pre_save_read_only_result.get("target_asset_path")
        == DEFAULT_TARGET_ASSET_PATH
    )
    read_only_target_check_performed = bool(
        live_result_schema_matches
        and live_result_read_only
        and target_path_matches
    )
    target_absent_for_new_temp_asset = bool(
        read_only_target_check_performed
        and live_pre_save_read_only_result.get("asset_exists") is False
    )
    target_directory_absent_or_empty = bool(
        read_only_target_check_performed
        and live_pre_save_read_only_result.get("target_directory_exists")
        is False
    )
    dirty_content_packages_zero = bool(
        int(live_pre_save_read_only_result.get("dirty_content_package_count", -1))
        == 0
    )
    dirty_map_packages_zero = bool(
        int(live_pre_save_read_only_result.get("dirty_map_package_count", -1))
        == 0
    )
    live_result_write_outputs_blocked = all(
        not live_pre_save_read_only_result.get(key)
        for key in WRITE_AND_LIVE_BLOCKED_OUTPUT_COUNT_KEYS
        if key in live_pre_save_read_only_result
    )
    save_dispatch_final_checkpoint_ready = bool(
        requested
        and section_201_208_summary_schema_matches
        and section_201_208_summary_passed
        and upstream_pre_save_ready
        and upstream_write_and_live_outputs_blocked
        and live_result_schema_matches
        and live_result_read_only
        and live_bridge_reachable
        and ieta_slate_status_succeeded
        and read_only_target_check_performed
        and target_absent_for_new_temp_asset
        and target_directory_absent_or_empty
        and dirty_content_packages_zero
        and dirty_map_packages_zero
        and live_result_write_outputs_blocked
    )
    actual_save_execution_requires_final_user_checkpoint = (
        save_dispatch_final_checkpoint_ready
    )

    return {
        "id": "durable_executor_authoring_live_pre_save_checkpoint_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_LIVE_PRE_SAVE_CHECKPOINT_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_201_208_summary_schema_matches": (
            section_201_208_summary_schema_matches
        ),
        "section_201_208_summary_passed": section_201_208_summary_passed,
        "section_201_208_pre_save_ready": upstream_pre_save_ready,
        "section_201_208_write_and_live_outputs_blocked": (
            upstream_write_and_live_outputs_blocked
        ),
        "live_result_schema_matches": live_result_schema_matches,
        "live_result_read_only": live_result_read_only,
        "live_bridge_reachable": live_bridge_reachable,
        "ieta_slate_status_succeeded": ieta_slate_status_succeeded,
        "target_path_matches": target_path_matches,
        "read_only_target_check_performed": read_only_target_check_performed,
        "target_absent_for_new_temp_asset": target_absent_for_new_temp_asset,
        "target_directory_absent_or_empty": target_directory_absent_or_empty,
        "dirty_content_packages_zero": dirty_content_packages_zero,
        "dirty_map_packages_zero": dirty_map_packages_zero,
        "live_result_write_outputs_blocked": live_result_write_outputs_blocked,
        "save_dispatch_final_checkpoint_ready": (
            save_dispatch_final_checkpoint_ready
        ),
        "actual_save_execution_requires_final_user_checkpoint": (
            actual_save_execution_requires_final_user_checkpoint
        ),
        "section_209_live_bridge_recovered": live_bridge_reachable,
        "section_210_live_pre_save_read_only_target_checked": (
            read_only_target_check_performed
        ),
        "section_211_live_target_absence_confirmed": (
            target_absent_for_new_temp_asset
        ),
        "section_212_live_dirty_package_boundary_clean": bool(
            dirty_content_packages_zero and dirty_map_packages_zero
        ),
        "section_213_live_overwrite_boundary_safe_for_new_temp_asset": bool(
            target_absent_for_new_temp_asset and target_directory_absent_or_empty
        ),
        "section_214_live_save_dispatch_final_checkpoint_ready": (
            save_dispatch_final_checkpoint_ready
        ),
        "section_215_live_save_execution_readback_plan_ready": (
            save_dispatch_final_checkpoint_ready
        ),
        "section_216_actual_save_requires_final_user_checkpoint": (
            actual_save_execution_requires_final_user_checkpoint
        ),
        "durable_authoring_enabled": save_dispatch_final_checkpoint_ready,
        "durable_executor_opened": save_dispatch_final_checkpoint_ready,
        "save_gate_open_allowed": save_dispatch_final_checkpoint_ready,
        "save_command_admitted": save_dispatch_final_checkpoint_ready,
        "final_pre_save_execution_ready": save_dispatch_final_checkpoint_ready,
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
            key: 1 if save_dispatch_final_checkpoint_ready else 0
            for key in LIVE_PRE_SAVE_CHECKPOINT_PATH_COUNT_KEYS
        },
        **blocked_counts,
    }


def summarize_durable_executor_authoring_live_pre_save_checkpoint_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "save_dispatch_final_checkpoint_ready")
            == len(requested)
            and _truthy_count(
                requested, "section_216_actual_save_requires_final_user_checkpoint"
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
            DURABLE_EXECUTOR_AUTHORING_LIVE_PRE_SAVE_CHECKPOINT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_live_pre_save_checkpoint_batch_count": (
            len(requested)
        ),
        "section_201_208_summary_schema_matches_count": _truthy_count(
            requested, "section_201_208_summary_schema_matches"
        ),
        "section_201_208_summary_passed_count": _truthy_count(
            requested, "section_201_208_summary_passed"
        ),
        "section_201_208_pre_save_ready_count": _truthy_count(
            requested, "section_201_208_pre_save_ready"
        ),
        "section_201_208_write_and_live_outputs_blocked_count": (
            _truthy_count(
                requested,
                "section_201_208_write_and_live_outputs_blocked",
            )
        ),
        "live_result_schema_matches_count": _truthy_count(
            requested, "live_result_schema_matches"
        ),
        "live_result_read_only_count": _truthy_count(
            requested, "live_result_read_only"
        ),
        "live_bridge_reachable_count": _truthy_count(
            requested, "live_bridge_reachable"
        ),
        "ieta_slate_status_succeeded_count": _truthy_count(
            requested, "ieta_slate_status_succeeded"
        ),
        "target_path_matches_count": _truthy_count(
            requested, "target_path_matches"
        ),
        "read_only_target_check_performed_count": _truthy_count(
            requested, "read_only_target_check_performed"
        ),
        "target_absent_for_new_temp_asset_count": _truthy_count(
            requested, "target_absent_for_new_temp_asset"
        ),
        "target_directory_absent_or_empty_count": _truthy_count(
            requested, "target_directory_absent_or_empty"
        ),
        "dirty_content_packages_zero_count": _truthy_count(
            requested, "dirty_content_packages_zero"
        ),
        "dirty_map_packages_zero_count": _truthy_count(
            requested, "dirty_map_packages_zero"
        ),
        "live_result_write_outputs_blocked_count": _truthy_count(
            requested, "live_result_write_outputs_blocked"
        ),
        "section_209_live_bridge_recovered_count": _truthy_count(
            requested, "section_209_live_bridge_recovered"
        ),
        "section_210_live_pre_save_read_only_target_checked_count": (
            _truthy_count(
                requested,
                "section_210_live_pre_save_read_only_target_checked",
            )
        ),
        "section_211_live_target_absence_confirmed_count": _truthy_count(
            requested, "section_211_live_target_absence_confirmed"
        ),
        "section_212_live_dirty_package_boundary_clean_count": _truthy_count(
            requested, "section_212_live_dirty_package_boundary_clean"
        ),
        "section_213_live_overwrite_boundary_safe_for_new_temp_asset_count": (
            _truthy_count(
                requested,
                "section_213_live_overwrite_boundary_safe_for_new_temp_asset",
            )
        ),
        "section_214_live_save_dispatch_final_checkpoint_ready_count": (
            _truthy_count(
                requested,
                "section_214_live_save_dispatch_final_checkpoint_ready",
            )
        ),
        "section_215_live_save_execution_readback_plan_ready_count": (
            _truthy_count(
                requested,
                "section_215_live_save_execution_readback_plan_ready",
            )
        ),
        "section_216_actual_save_requires_final_user_checkpoint_count": (
            _truthy_count(
                requested,
                "section_216_actual_save_requires_final_user_checkpoint",
            )
        ),
        "durable_authoring_enabled_count": _truthy_count(
            requested, "durable_authoring_enabled"
        ),
        "durable_executor_opened_count": _truthy_count(
            requested, "durable_executor_opened"
        ),
        "save_gate_open_allowed_count": _truthy_count(
            requested, "save_gate_open_allowed"
        ),
        "save_command_admitted_count": _truthy_count(
            requested, "save_command_admitted"
        ),
        "final_pre_save_execution_ready_count": _truthy_count(
            requested, "final_pre_save_execution_ready"
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
            for key in LIVE_PRE_SAVE_CHECKPOINT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in WRITE_AND_LIVE_BLOCKED_OUTPUT_COUNT_KEYS
        }
    )
    return summary
