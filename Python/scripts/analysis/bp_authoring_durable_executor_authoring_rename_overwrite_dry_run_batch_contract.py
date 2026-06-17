#!/usr/bin/env python
"""
Sections 241-248 durable executor authoring rename/overwrite dry-run batch.

This contract opens only a dry-run gate for a target-scoped rename/overwrite
decision. It requires the cleanup/delete dry-run boundary, verifies that both
source and proposed destination stay under /Game/_MCP_Temp, and keeps actual
rename, overwrite, delete, cleanup, and production writes closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_cleanup_delete_dry_run_batch_contract as cleanup_delete_dry_run


DURABLE_EXECUTOR_AUTHORING_RENAME_OVERWRITE_DRY_RUN_BATCH_SCHEMA = (
    "section_241_248_durable_executor_authoring_rename_overwrite_dry_run_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_RENAME_OVERWRITE_DRY_RUN_BATCH_SUMMARY_SCHEMA = (
    "section_241_248_durable_executor_authoring_rename_overwrite_dry_run_batch_summary_v1"
)
RENAME_OVERWRITE_DRY_RUN_RESULT_SCHEMA = (
    "section_241_248_rename_overwrite_dry_run_result_v1"
)
SECTION_233_240_CLEANUP_DELETE_DRY_RUN_SUMMARY_SCHEMA = (
    cleanup_delete_dry_run
    .DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_DRY_RUN_BATCH_SUMMARY_SCHEMA
)
DEFAULT_SOURCE_ASSET_PATH = cleanup_delete_dry_run.DEFAULT_TARGET_ASSET_PATH
DEFAULT_SOURCE_DIRECTORY = cleanup_delete_dry_run.DEFAULT_TARGET_DIRECTORY
DEFAULT_RENAME_TARGET_ASSET_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/BP_DurableSaveGatePrep_Renamed"
)
DEFAULT_OVERWRITE_POLICY = "deny_existing_require_absent"
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_cleanup_delete_dry_run_batch_count",
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
    "final_durable_release_ready_count",
)
UPSTREAM_DESTRUCTIVE_MUST_BE_CLOSED_COUNT_KEYS = (
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
RENAME_OVERWRITE_DRY_RUN_PATH_COUNT_KEYS = (
    "section_241_rename_source_scope_confirmed_count",
    "section_242_rename_destination_scope_confirmed_count",
    "section_243_overwrite_policy_denies_existing_destination_count",
    "section_244_rename_overwrite_dry_run_plan_accepted_count",
    "section_245_rename_collision_boundary_clean_count",
    "section_246_rename_dirty_package_boundary_clean_count",
    "section_247_rename_result_readback_dry_run_ready_count",
    "section_248_actual_rename_overwrite_requires_final_user_checkpoint_count",
    "rename_overwrite_dry_run_ready_count",
    "actual_rename_overwrite_requires_final_user_checkpoint_count",
)
BLOCKED_RENAME_OVERWRITE_OUTPUT_COUNT_KEYS = (
    "cleanup_allowed_count",
    "cleanup_executed_count",
    "delete_asset_allowed_count",
    "rename_asset_allowed_count",
    "rename_command_dispatched_count",
    "rename_command_executed_count",
    "overwrite_allowed_count",
    "overwrite_executed_count",
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


def build_rename_overwrite_dry_run_result(
    *,
    source_asset_path: str = DEFAULT_SOURCE_ASSET_PATH,
    source_directory: str = DEFAULT_SOURCE_DIRECTORY,
    destination_asset_path: str = DEFAULT_RENAME_TARGET_ASSET_PATH,
    overwrite_policy: str = DEFAULT_OVERWRITE_POLICY,
    source_exists: bool = True,
    source_load_succeeded: bool = True,
    destination_exists: bool = False,
    source_under_temp_root: bool = True,
    destination_under_temp_root: bool = True,
    dry_run_plan_built: bool = True,
    dry_run_readback_plan_ready: bool = True,
    dirty_content_package_count: int = 0,
    dirty_map_package_count: int = 0,
    cleanup_allowed: bool = False,
    cleanup_executed: bool = False,
    delete_asset_called: bool = False,
    rename_asset_called: bool = False,
    rename_command_dispatched: bool = False,
    rename_command_executed: bool = False,
    overwrite_executed: bool = False,
    production_path_touched: bool = False,
    error: str | None = None,
) -> Dict[str, Any]:
    return {
        "schema": RENAME_OVERWRITE_DRY_RUN_RESULT_SCHEMA,
        "source_asset_path": source_asset_path,
        "source_directory": source_directory,
        "destination_asset_path": destination_asset_path,
        "overwrite_policy": overwrite_policy,
        "source_exists": source_exists,
        "source_load_succeeded": source_load_succeeded,
        "destination_exists": destination_exists,
        "source_under_temp_root": source_under_temp_root,
        "destination_under_temp_root": destination_under_temp_root,
        "dry_run_plan_built": dry_run_plan_built,
        "dry_run_readback_plan_ready": dry_run_readback_plan_ready,
        "dirty_content_package_count": dirty_content_package_count,
        "dirty_map_package_count": dirty_map_package_count,
        "cleanup_allowed": cleanup_allowed,
        "cleanup_executed": cleanup_executed,
        "delete_asset_called": delete_asset_called,
        "rename_asset_called": rename_asset_called,
        "rename_command_dispatched": rename_command_dispatched,
        "rename_command_executed": rename_command_executed,
        "overwrite_executed": overwrite_executed,
        "production_path_touched": production_path_touched,
        "error": error,
    }


def build_durable_executor_authoring_rename_overwrite_dry_run_batch_contract(
    requested: bool,
    section_233_240_cleanup_delete_dry_run_summary: Dict[str, Any],
    rename_overwrite_dry_run_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_233_240_summary_schema_matches = bool(
        section_233_240_cleanup_delete_dry_run_summary.get("schema")
        == SECTION_233_240_CLEANUP_DELETE_DRY_RUN_SUMMARY_SCHEMA
    )
    section_233_240_summary_passed = bool(
        section_233_240_cleanup_delete_dry_run_summary.get("status")
        == "passed"
    )
    upstream_cleanup_delete_dry_run_ready = all(
        _count_is_one(section_233_240_cleanup_delete_dry_run_summary, key)
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_destructive_outputs_closed = all(
        _count_is_zero(section_233_240_cleanup_delete_dry_run_summary, key)
        for key in UPSTREAM_DESTRUCTIVE_MUST_BE_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        rename_overwrite_dry_run_result.get("schema")
        == RENAME_OVERWRITE_DRY_RUN_RESULT_SCHEMA
    )
    rename_source_scope_confirmed = bool(
        rename_overwrite_dry_run_result.get("source_asset_path")
        == DEFAULT_SOURCE_ASSET_PATH
        and rename_overwrite_dry_run_result.get("source_directory")
        == DEFAULT_SOURCE_DIRECTORY
        and rename_overwrite_dry_run_result.get("source_under_temp_root")
        and rename_overwrite_dry_run_result.get("source_exists")
        and rename_overwrite_dry_run_result.get("source_load_succeeded")
    )
    rename_destination_scope_confirmed = bool(
        rename_overwrite_dry_run_result.get("destination_asset_path")
        == DEFAULT_RENAME_TARGET_ASSET_PATH
        and rename_overwrite_dry_run_result.get("destination_under_temp_root")
    )
    overwrite_policy_denies_existing_destination = bool(
        rename_overwrite_dry_run_result.get("overwrite_policy")
        == DEFAULT_OVERWRITE_POLICY
        and rename_overwrite_dry_run_result.get("destination_exists") is False
    )
    rename_overwrite_dry_run_plan_accepted = bool(
        rename_overwrite_dry_run_result.get("dry_run_plan_built")
    )
    rename_collision_boundary_clean = bool(
        overwrite_policy_denies_existing_destination
        and rename_destination_scope_confirmed
    )
    rename_dirty_package_boundary_clean = bool(
        int(
            rename_overwrite_dry_run_result.get(
                "dirty_content_package_count", -1
            )
        )
        == 0
        and int(rename_overwrite_dry_run_result.get("dirty_map_package_count", -1))
        == 0
    )
    rename_result_readback_dry_run_ready = bool(
        rename_overwrite_dry_run_plan_accepted
        and rename_overwrite_dry_run_result.get("dry_run_readback_plan_ready")
    )
    dry_run_blocks_actual_rename_outputs = bool(
        not rename_overwrite_dry_run_result.get("cleanup_allowed")
        and not rename_overwrite_dry_run_result.get("cleanup_executed")
        and not rename_overwrite_dry_run_result.get("delete_asset_called")
        and not rename_overwrite_dry_run_result.get("rename_asset_called")
        and not rename_overwrite_dry_run_result.get("rename_command_dispatched")
        and not rename_overwrite_dry_run_result.get("rename_command_executed")
        and not rename_overwrite_dry_run_result.get("overwrite_executed")
        and not rename_overwrite_dry_run_result.get("production_path_touched")
    )
    result_has_no_error = bool(
        rename_overwrite_dry_run_result.get("error") in (None, "")
    )
    rename_overwrite_dry_run_ready = bool(
        requested
        and section_233_240_summary_schema_matches
        and section_233_240_summary_passed
        and upstream_cleanup_delete_dry_run_ready
        and upstream_destructive_outputs_closed
        and result_schema_matches
        and rename_source_scope_confirmed
        and rename_destination_scope_confirmed
        and overwrite_policy_denies_existing_destination
        and rename_overwrite_dry_run_plan_accepted
        and rename_collision_boundary_clean
        and rename_dirty_package_boundary_clean
        and rename_result_readback_dry_run_ready
        and dry_run_blocks_actual_rename_outputs
        and result_has_no_error
    )
    actual_rename_overwrite_requires_final_user_checkpoint = (
        rename_overwrite_dry_run_ready
    )

    return {
        "id": "durable_executor_authoring_rename_overwrite_dry_run_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_RENAME_OVERWRITE_DRY_RUN_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_233_240_summary_schema_matches": (
            section_233_240_summary_schema_matches
        ),
        "section_233_240_summary_passed": section_233_240_summary_passed,
        "section_233_240_cleanup_delete_dry_run_ready": (
            upstream_cleanup_delete_dry_run_ready
        ),
        "section_233_240_destructive_outputs_closed": (
            upstream_destructive_outputs_closed
        ),
        "result_schema_matches": result_schema_matches,
        "rename_source_scope_confirmed": rename_source_scope_confirmed,
        "rename_destination_scope_confirmed": rename_destination_scope_confirmed,
        "overwrite_policy_denies_existing_destination": (
            overwrite_policy_denies_existing_destination
        ),
        "rename_overwrite_dry_run_plan_accepted": (
            rename_overwrite_dry_run_plan_accepted
        ),
        "rename_collision_boundary_clean": rename_collision_boundary_clean,
        "rename_dirty_package_boundary_clean": (
            rename_dirty_package_boundary_clean
        ),
        "rename_result_readback_dry_run_ready": (
            rename_result_readback_dry_run_ready
        ),
        "dry_run_blocks_actual_rename_outputs": (
            dry_run_blocks_actual_rename_outputs
        ),
        "result_has_no_error": result_has_no_error,
        "rename_overwrite_dry_run_ready": rename_overwrite_dry_run_ready,
        "actual_rename_overwrite_requires_final_user_checkpoint": (
            actual_rename_overwrite_requires_final_user_checkpoint
        ),
        "section_241_rename_source_scope_confirmed": (
            rename_overwrite_dry_run_ready
        ),
        "section_242_rename_destination_scope_confirmed": (
            rename_overwrite_dry_run_ready
        ),
        "section_243_overwrite_policy_denies_existing_destination": (
            rename_overwrite_dry_run_ready
        ),
        "section_244_rename_overwrite_dry_run_plan_accepted": (
            rename_overwrite_dry_run_ready
        ),
        "section_245_rename_collision_boundary_clean": (
            rename_overwrite_dry_run_ready
        ),
        "section_246_rename_dirty_package_boundary_clean": (
            rename_overwrite_dry_run_ready
        ),
        "section_247_rename_result_readback_dry_run_ready": (
            rename_overwrite_dry_run_ready
        ),
        "section_248_actual_rename_overwrite_requires_final_user_checkpoint": (
            actual_rename_overwrite_requires_final_user_checkpoint
        ),
        "final_durable_release_ready": rename_overwrite_dry_run_ready,
        "cleanup_delete_dry_run_ready": rename_overwrite_dry_run_ready,
        "rename_overwrite_dry_run_allowed": rename_overwrite_dry_run_ready,
        "rename_overwrite_dry_run_ready": rename_overwrite_dry_run_ready,
        "cleanup_allowed": False,
        "cleanup_executed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        "rename_command_dispatched": False,
        "rename_command_executed": False,
        "overwrite_allowed": False,
        "overwrite_executed": False,
        "production_path_write_allowed": False,
        "production_path_write_executed": False,
        **{
            key: 1 if rename_overwrite_dry_run_ready else 0
            for key in RENAME_OVERWRITE_DRY_RUN_PATH_COUNT_KEYS
        },
        **{key: 0 for key in BLOCKED_RENAME_OVERWRITE_OUTPUT_COUNT_KEYS},
    }


def summarize_durable_executor_authoring_rename_overwrite_dry_run_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "rename_overwrite_dry_run_ready")
            == len(requested)
            and _truthy_count(
                requested,
                "actual_rename_overwrite_requires_final_user_checkpoint",
            )
            == len(requested)
            and _truthy_count(requested, "rename_asset_allowed") == 0
            and _truthy_count(requested, "rename_command_dispatched") == 0
            and _truthy_count(requested, "rename_command_executed") == 0
            and _truthy_count(requested, "overwrite_allowed") == 0
            and _truthy_count(requested, "overwrite_executed") == 0
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_RENAME_OVERWRITE_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_RENAME_OVERWRITE_DRY_RUN_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_rename_overwrite_dry_run_batch_count": (
            len(requested)
        ),
        "section_233_240_summary_schema_matches_count": _truthy_count(
            requested, "section_233_240_summary_schema_matches"
        ),
        "section_233_240_summary_passed_count": _truthy_count(
            requested, "section_233_240_summary_passed"
        ),
        "section_233_240_cleanup_delete_dry_run_ready_count": _truthy_count(
            requested, "section_233_240_cleanup_delete_dry_run_ready"
        ),
        "section_233_240_destructive_outputs_closed_count": _truthy_count(
            requested, "section_233_240_destructive_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "rename_source_scope_confirmed_count": _truthy_count(
            requested, "rename_source_scope_confirmed"
        ),
        "rename_destination_scope_confirmed_count": _truthy_count(
            requested, "rename_destination_scope_confirmed"
        ),
        "overwrite_policy_denies_existing_destination_count": _truthy_count(
            requested, "overwrite_policy_denies_existing_destination"
        ),
        "rename_overwrite_dry_run_plan_accepted_count": _truthy_count(
            requested, "rename_overwrite_dry_run_plan_accepted"
        ),
        "rename_collision_boundary_clean_count": _truthy_count(
            requested, "rename_collision_boundary_clean"
        ),
        "rename_dirty_package_boundary_clean_count": _truthy_count(
            requested, "rename_dirty_package_boundary_clean"
        ),
        "rename_result_readback_dry_run_ready_count": _truthy_count(
            requested, "rename_result_readback_dry_run_ready"
        ),
        "dry_run_blocks_actual_rename_outputs_count": _truthy_count(
            requested, "dry_run_blocks_actual_rename_outputs"
        ),
        "result_has_no_error_count": _truthy_count(
            requested, "result_has_no_error"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "cleanup_delete_dry_run_ready_count": _truthy_count(
            requested, "cleanup_delete_dry_run_ready"
        ),
        "rename_overwrite_dry_run_allowed_count": _truthy_count(
            requested, "rename_overwrite_dry_run_allowed"
        ),
        "rename_overwrite_dry_run_ready_count": _truthy_count(
            requested, "rename_overwrite_dry_run_ready"
        ),
        "cleanup_allowed_count": _truthy_count(requested, "cleanup_allowed"),
        "cleanup_executed_count": _truthy_count(requested, "cleanup_executed"),
        "delete_asset_allowed_count": _truthy_count(
            requested, "delete_asset_allowed"
        ),
        "rename_asset_allowed_count": _truthy_count(
            requested, "rename_asset_allowed"
        ),
        "rename_command_dispatched_count": _truthy_count(
            requested, "rename_command_dispatched"
        ),
        "rename_command_executed_count": _truthy_count(
            requested, "rename_command_executed"
        ),
        "overwrite_allowed_count": _truthy_count(
            requested, "overwrite_allowed"
        ),
        "overwrite_executed_count": _truthy_count(
            requested, "overwrite_executed"
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
            for key in RENAME_OVERWRITE_DRY_RUN_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_RENAME_OVERWRITE_OUTPUT_COUNT_KEYS
        }
    )
    return summary
