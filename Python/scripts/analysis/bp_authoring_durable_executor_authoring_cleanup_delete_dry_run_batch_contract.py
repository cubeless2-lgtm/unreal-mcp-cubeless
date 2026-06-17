#!/usr/bin/env python
"""
Sections 233-240 durable executor authoring cleanup/delete dry-run batch.

This contract opens only the dry-run planning gate for cleaning up the saved
temporary Blueprint. It proves the target is isolated under /Game/_MCP_Temp and
that deletion can be planned, but actual cleanup/delete dispatch remains behind
a final checkpoint.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_live_save_stability_batch_contract as live_save_stability


DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_DRY_RUN_BATCH_SCHEMA = (
    "section_233_240_durable_executor_authoring_cleanup_delete_dry_run_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_DRY_RUN_BATCH_SUMMARY_SCHEMA = (
    "section_233_240_durable_executor_authoring_cleanup_delete_dry_run_batch_summary_v1"
)
CLEANUP_DELETE_DRY_RUN_RESULT_SCHEMA = (
    "section_233_240_cleanup_delete_dry_run_result_v1"
)
SECTION_225_232_LIVE_SAVE_STABILITY_SUMMARY_SCHEMA = (
    live_save_stability
    .DURABLE_EXECUTOR_AUTHORING_LIVE_SAVE_STABILITY_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = live_save_stability.DEFAULT_TARGET_ASSET_PATH
DEFAULT_TARGET_DIRECTORY = live_save_stability.DEFAULT_TARGET_DIRECTORY
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_live_save_stability_batch_count",
    "section_225_live_compile_api_fixed_count",
    "section_226_live_legacy_compile_helper_mismatch_documented_count",
    "section_227_live_partial_save_recovery_verified_count",
    "section_228_live_idempotent_resave_verified_count",
    "section_229_live_save_readback_schema_strengthened_count",
    "section_230_live_dirty_package_stability_verified_count",
    "section_231_live_production_path_untouched_count",
    "section_232_live_delete_rename_cleanup_still_gated_count",
    "live_save_stability_ready_count",
    "final_durable_release_ready_count",
)
UPSTREAM_CLEANUP_DELETE_MUST_BE_CLOSED_COUNT_KEYS = (
    "cleanup_allowed_count",
    "cleanup_executed_count",
    "save_delete_rename_allowed_count",
    "delete_asset_allowed_count",
    "rename_asset_allowed_count",
    "production_path_write_allowed_count",
    "production_path_write_executed_count",
)
CLEANUP_DELETE_DRY_RUN_PATH_COUNT_KEYS = (
    "section_233_cleanup_target_scope_confirmed_count",
    "section_234_saved_asset_pre_delete_readback_confirmed_count",
    "section_235_cleanup_delete_dry_run_plan_accepted_count",
    "section_236_delete_target_isolation_proved_count",
    "section_237_dirty_package_no_delete_boundary_clean_count",
    "section_238_delete_command_dispatch_dry_run_ready_count",
    "section_239_delete_result_readback_dry_run_ready_count",
    "section_240_actual_delete_requires_final_user_checkpoint_count",
    "cleanup_delete_dry_run_ready_count",
    "actual_delete_execution_requires_final_user_checkpoint_count",
)
BLOCKED_DELETE_RENAME_OUTPUT_COUNT_KEYS = (
    "cleanup_allowed_count",
    "cleanup_executed_count",
    "delete_command_dispatched_count",
    "delete_command_executed_count",
    "save_delete_rename_allowed_count",
    "delete_asset_allowed_count",
    "rename_asset_allowed_count",
    "production_path_write_allowed_count",
    "production_path_write_executed_count",
)


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _count_is_one(summary: Dict[str, Any], key: str) -> bool:
    return bool(summary.get(key) == 1)


def _count_is_zero(summary: Dict[str, Any], key: str) -> bool:
    return bool(int(summary.get(key, 0) or 0) == 0)


def build_cleanup_delete_dry_run_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_directory: str = DEFAULT_TARGET_DIRECTORY,
    target_exists: bool = True,
    target_load_succeeded: bool = True,
    package_file_exists: bool = True,
    package_file_size_bytes: int = 1,
    target_under_temp_root: bool = True,
    target_is_exact_saved_temp_blueprint: bool = True,
    dry_run_plan_built: bool = True,
    dry_run_dispatch_ready: bool = True,
    dry_run_readback_plan_ready: bool = True,
    dirty_content_package_count: int = 0,
    dirty_map_package_count: int = 0,
    cleanup_allowed: bool = False,
    cleanup_executed: bool = False,
    delete_command_dispatched: bool = False,
    delete_command_executed: bool = False,
    delete_asset_called: bool = False,
    rename_asset_called: bool = False,
    production_path_touched: bool = False,
    error: str | None = None,
) -> Dict[str, Any]:
    return {
        "schema": CLEANUP_DELETE_DRY_RUN_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_directory": target_directory,
        "target_exists": target_exists,
        "target_load_succeeded": target_load_succeeded,
        "package_file_exists": package_file_exists,
        "package_file_size_bytes": package_file_size_bytes,
        "target_under_temp_root": target_under_temp_root,
        "target_is_exact_saved_temp_blueprint": (
            target_is_exact_saved_temp_blueprint
        ),
        "dry_run_plan_built": dry_run_plan_built,
        "dry_run_dispatch_ready": dry_run_dispatch_ready,
        "dry_run_readback_plan_ready": dry_run_readback_plan_ready,
        "dirty_content_package_count": dirty_content_package_count,
        "dirty_map_package_count": dirty_map_package_count,
        "cleanup_allowed": cleanup_allowed,
        "cleanup_executed": cleanup_executed,
        "delete_command_dispatched": delete_command_dispatched,
        "delete_command_executed": delete_command_executed,
        "delete_asset_called": delete_asset_called,
        "rename_asset_called": rename_asset_called,
        "production_path_touched": production_path_touched,
        "error": error,
    }


def build_durable_executor_authoring_cleanup_delete_dry_run_batch_contract(
    requested: bool,
    section_225_232_live_save_stability_summary: Dict[str, Any],
    cleanup_delete_dry_run_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_225_232_summary_schema_matches = bool(
        section_225_232_live_save_stability_summary.get("schema")
        == SECTION_225_232_LIVE_SAVE_STABILITY_SUMMARY_SCHEMA
    )
    section_225_232_summary_passed = bool(
        section_225_232_live_save_stability_summary.get("status") == "passed"
    )
    upstream_save_stability_ready = all(
        _count_is_one(section_225_232_live_save_stability_summary, key)
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_cleanup_delete_closed = all(
        _count_is_zero(section_225_232_live_save_stability_summary, key)
        for key in UPSTREAM_CLEANUP_DELETE_MUST_BE_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        cleanup_delete_dry_run_result.get("schema")
        == CLEANUP_DELETE_DRY_RUN_RESULT_SCHEMA
    )
    target_path_matches = bool(
        cleanup_delete_dry_run_result.get("target_asset_path")
        == DEFAULT_TARGET_ASSET_PATH
    )
    target_directory_matches = bool(
        cleanup_delete_dry_run_result.get("target_directory")
        == DEFAULT_TARGET_DIRECTORY
    )
    cleanup_target_scope_confirmed = bool(
        target_path_matches
        and target_directory_matches
        and cleanup_delete_dry_run_result.get("target_under_temp_root")
        and cleanup_delete_dry_run_result.get(
            "target_is_exact_saved_temp_blueprint"
        )
    )
    saved_asset_pre_delete_readback_confirmed = bool(
        cleanup_delete_dry_run_result.get("target_exists")
        and cleanup_delete_dry_run_result.get("target_load_succeeded")
        and cleanup_delete_dry_run_result.get("package_file_exists")
        and int(
            cleanup_delete_dry_run_result.get("package_file_size_bytes", 0)
            or 0
        )
        > 0
    )
    cleanup_delete_dry_run_plan_accepted = bool(
        cleanup_delete_dry_run_result.get("dry_run_plan_built")
    )
    delete_target_isolation_proved = bool(
        cleanup_target_scope_confirmed
        and saved_asset_pre_delete_readback_confirmed
    )
    dirty_package_no_delete_boundary_clean = bool(
        int(
            cleanup_delete_dry_run_result.get(
                "dirty_content_package_count", -1
            )
        )
        == 0
        and int(cleanup_delete_dry_run_result.get("dirty_map_package_count", -1))
        == 0
    )
    delete_command_dispatch_dry_run_ready = bool(
        cleanup_delete_dry_run_plan_accepted
        and cleanup_delete_dry_run_result.get("dry_run_dispatch_ready")
    )
    delete_result_readback_dry_run_ready = bool(
        delete_command_dispatch_dry_run_ready
        and cleanup_delete_dry_run_result.get("dry_run_readback_plan_ready")
    )
    dry_run_blocks_actual_delete_outputs = bool(
        not cleanup_delete_dry_run_result.get("cleanup_allowed")
        and not cleanup_delete_dry_run_result.get("cleanup_executed")
        and not cleanup_delete_dry_run_result.get("delete_command_dispatched")
        and not cleanup_delete_dry_run_result.get("delete_command_executed")
        and not cleanup_delete_dry_run_result.get("delete_asset_called")
        and not cleanup_delete_dry_run_result.get("rename_asset_called")
        and not cleanup_delete_dry_run_result.get("production_path_touched")
    )
    result_has_no_error = bool(
        cleanup_delete_dry_run_result.get("error") in (None, "")
    )
    cleanup_delete_dry_run_ready = bool(
        requested
        and section_225_232_summary_schema_matches
        and section_225_232_summary_passed
        and upstream_save_stability_ready
        and upstream_cleanup_delete_closed
        and result_schema_matches
        and cleanup_target_scope_confirmed
        and saved_asset_pre_delete_readback_confirmed
        and cleanup_delete_dry_run_plan_accepted
        and delete_target_isolation_proved
        and dirty_package_no_delete_boundary_clean
        and delete_command_dispatch_dry_run_ready
        and delete_result_readback_dry_run_ready
        and dry_run_blocks_actual_delete_outputs
        and result_has_no_error
    )
    actual_delete_execution_requires_final_user_checkpoint = (
        cleanup_delete_dry_run_ready
    )

    return {
        "id": "durable_executor_authoring_cleanup_delete_dry_run_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_DRY_RUN_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_225_232_summary_schema_matches": (
            section_225_232_summary_schema_matches
        ),
        "section_225_232_summary_passed": section_225_232_summary_passed,
        "section_225_232_save_stability_ready": upstream_save_stability_ready,
        "section_225_232_cleanup_delete_closed": (
            upstream_cleanup_delete_closed
        ),
        "result_schema_matches": result_schema_matches,
        "cleanup_target_scope_confirmed": cleanup_target_scope_confirmed,
        "saved_asset_pre_delete_readback_confirmed": (
            saved_asset_pre_delete_readback_confirmed
        ),
        "cleanup_delete_dry_run_plan_accepted": (
            cleanup_delete_dry_run_plan_accepted
        ),
        "delete_target_isolation_proved": delete_target_isolation_proved,
        "dirty_package_no_delete_boundary_clean": (
            dirty_package_no_delete_boundary_clean
        ),
        "delete_command_dispatch_dry_run_ready": (
            delete_command_dispatch_dry_run_ready
        ),
        "delete_result_readback_dry_run_ready": (
            delete_result_readback_dry_run_ready
        ),
        "dry_run_blocks_actual_delete_outputs": (
            dry_run_blocks_actual_delete_outputs
        ),
        "result_has_no_error": result_has_no_error,
        "cleanup_delete_dry_run_ready": cleanup_delete_dry_run_ready,
        "actual_delete_execution_requires_final_user_checkpoint": (
            actual_delete_execution_requires_final_user_checkpoint
        ),
        "section_233_cleanup_target_scope_confirmed": (
            cleanup_delete_dry_run_ready
        ),
        "section_234_saved_asset_pre_delete_readback_confirmed": (
            cleanup_delete_dry_run_ready
        ),
        "section_235_cleanup_delete_dry_run_plan_accepted": (
            cleanup_delete_dry_run_ready
        ),
        "section_236_delete_target_isolation_proved": (
            cleanup_delete_dry_run_ready
        ),
        "section_237_dirty_package_no_delete_boundary_clean": (
            cleanup_delete_dry_run_ready
        ),
        "section_238_delete_command_dispatch_dry_run_ready": (
            cleanup_delete_dry_run_ready
        ),
        "section_239_delete_result_readback_dry_run_ready": (
            cleanup_delete_dry_run_ready
        ),
        "section_240_actual_delete_requires_final_user_checkpoint": (
            actual_delete_execution_requires_final_user_checkpoint
        ),
        "final_durable_release_ready": cleanup_delete_dry_run_ready,
        "live_save_stability_ready": cleanup_delete_dry_run_ready,
        "cleanup_delete_dry_run_allowed": cleanup_delete_dry_run_ready,
        "cleanup_delete_dry_run_ready": cleanup_delete_dry_run_ready,
        "cleanup_allowed": False,
        "cleanup_executed": False,
        "delete_command_dispatched": False,
        "delete_command_executed": False,
        "save_delete_rename_allowed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        "production_path_write_allowed": False,
        "production_path_write_executed": False,
        **{
            key: 1 if cleanup_delete_dry_run_ready else 0
            for key in CLEANUP_DELETE_DRY_RUN_PATH_COUNT_KEYS
        },
        **{key: 0 for key in BLOCKED_DELETE_RENAME_OUTPUT_COUNT_KEYS},
    }


def summarize_durable_executor_authoring_cleanup_delete_dry_run_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "cleanup_delete_dry_run_ready")
            == len(requested)
            and _truthy_count(
                requested,
                "actual_delete_execution_requires_final_user_checkpoint",
            )
            == len(requested)
            and _truthy_count(requested, "cleanup_allowed") == 0
            and _truthy_count(requested, "cleanup_executed") == 0
            and _truthy_count(requested, "delete_command_dispatched") == 0
            and _truthy_count(requested, "delete_command_executed") == 0
            and _truthy_count(requested, "save_delete_rename_allowed") == 0
            and _truthy_count(requested, "delete_asset_allowed") == 0
            and _truthy_count(requested, "rename_asset_allowed") == 0
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_DELETE_RENAME_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_DRY_RUN_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_cleanup_delete_dry_run_batch_count": (
            len(requested)
        ),
        "section_225_232_summary_schema_matches_count": _truthy_count(
            requested, "section_225_232_summary_schema_matches"
        ),
        "section_225_232_summary_passed_count": _truthy_count(
            requested, "section_225_232_summary_passed"
        ),
        "section_225_232_save_stability_ready_count": _truthy_count(
            requested, "section_225_232_save_stability_ready"
        ),
        "section_225_232_cleanup_delete_closed_count": _truthy_count(
            requested, "section_225_232_cleanup_delete_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "cleanup_target_scope_confirmed_count": _truthy_count(
            requested, "cleanup_target_scope_confirmed"
        ),
        "saved_asset_pre_delete_readback_confirmed_count": _truthy_count(
            requested, "saved_asset_pre_delete_readback_confirmed"
        ),
        "cleanup_delete_dry_run_plan_accepted_count": _truthy_count(
            requested, "cleanup_delete_dry_run_plan_accepted"
        ),
        "delete_target_isolation_proved_count": _truthy_count(
            requested, "delete_target_isolation_proved"
        ),
        "dirty_package_no_delete_boundary_clean_count": _truthy_count(
            requested, "dirty_package_no_delete_boundary_clean"
        ),
        "delete_command_dispatch_dry_run_ready_count": _truthy_count(
            requested, "delete_command_dispatch_dry_run_ready"
        ),
        "delete_result_readback_dry_run_ready_count": _truthy_count(
            requested, "delete_result_readback_dry_run_ready"
        ),
        "dry_run_blocks_actual_delete_outputs_count": _truthy_count(
            requested, "dry_run_blocks_actual_delete_outputs"
        ),
        "result_has_no_error_count": _truthy_count(
            requested, "result_has_no_error"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "live_save_stability_ready_count": _truthy_count(
            requested, "live_save_stability_ready"
        ),
        "cleanup_delete_dry_run_allowed_count": _truthy_count(
            requested, "cleanup_delete_dry_run_allowed"
        ),
        "cleanup_delete_dry_run_ready_count": _truthy_count(
            requested, "cleanup_delete_dry_run_ready"
        ),
        "cleanup_allowed_count": _truthy_count(requested, "cleanup_allowed"),
        "cleanup_executed_count": _truthy_count(requested, "cleanup_executed"),
        "delete_command_dispatched_count": _truthy_count(
            requested, "delete_command_dispatched"
        ),
        "delete_command_executed_count": _truthy_count(
            requested, "delete_command_executed"
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
        "production_path_write_allowed_count": _truthy_count(
            requested, "production_path_write_allowed"
        ),
        "production_path_write_executed_count": _truthy_count(
            requested, "production_path_write_executed"
        ),
    }
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in CLEANUP_DELETE_DRY_RUN_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_DELETE_RENAME_OUTPUT_COUNT_KEYS
        }
    )
    return summary
