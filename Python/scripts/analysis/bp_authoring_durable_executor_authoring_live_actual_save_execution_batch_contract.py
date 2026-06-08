#!/usr/bin/env python
"""
Sections 217-224 durable executor authoring live actual save execution batch.

This contract records the approved live save path for the temporary durable
Blueprint target. It requires the Section 209-216 live pre-save checkpoint,
an executed compile/save result, and a read-only readback proving the saved
Blueprint exists on disk with dirty packages cleared. Delete and rename remain
closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_live_pre_save_checkpoint_batch_contract as live_pre_save_checkpoint
import bp_authoring_durable_executor_authoring_save_gate_preflight_batch_contract as save_gate_preflight


DURABLE_EXECUTOR_AUTHORING_LIVE_ACTUAL_SAVE_EXECUTION_BATCH_SCHEMA = (
    "section_217_224_durable_executor_authoring_live_actual_save_execution_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_LIVE_ACTUAL_SAVE_EXECUTION_BATCH_SUMMARY_SCHEMA = (
    "section_217_224_durable_executor_authoring_live_actual_save_execution_batch_summary_v1"
)
LIVE_ACTUAL_SAVE_EXECUTION_RESULT_SCHEMA = (
    "section_217_live_compile_save_result_v1"
)
LIVE_ACTUAL_SAVE_READBACK_RESULT_SCHEMA = (
    "section_217_224_live_actual_save_final_readback_result_v1"
)
SECTION_209_216_LIVE_PRE_SAVE_CHECKPOINT_SUMMARY_SCHEMA = (
    live_pre_save_checkpoint
    .DURABLE_EXECUTOR_AUTHORING_LIVE_PRE_SAVE_CHECKPOINT_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = save_gate_preflight.DEFAULT_SAVE_TARGET_ASSET_PATH
DEFAULT_TARGET_DIRECTORY = "/Game/_MCP_Temp/DurableSaveGate"
DEFAULT_ASSET_CLASS = "Blueprint"
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_live_pre_save_checkpoint_batch_count",
    "section_209_live_bridge_recovered_count",
    "section_210_live_pre_save_read_only_target_checked_count",
    "section_211_live_target_absence_confirmed_count",
    "section_212_live_dirty_package_boundary_clean_count",
    "section_213_live_overwrite_boundary_safe_for_new_temp_asset_count",
    "section_214_live_save_dispatch_final_checkpoint_ready_count",
    "section_215_live_save_execution_readback_plan_ready_count",
    "section_216_actual_save_requires_final_user_checkpoint_count",
    "save_dispatch_final_checkpoint_ready_count",
    "actual_save_execution_requires_final_user_checkpoint_count",
    "durable_authoring_enabled_count",
    "durable_executor_opened_count",
    "save_gate_open_allowed_count",
    "save_command_admitted_count",
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
LIVE_ACTUAL_SAVE_EXECUTION_PATH_COUNT_KEYS = (
    "section_217_actual_save_approval_consumed_count",
    "section_218_live_save_command_dispatched_count",
    "section_219_live_temp_blueprint_write_performed_count",
    "section_220_live_blueprint_compile_save_succeeded_count",
    "section_221_live_save_asset_result_confirmed_count",
    "section_222_live_saved_asset_readback_confirmed_count",
    "section_223_live_dirty_packages_cleared_after_save_count",
    "section_224_final_durable_release_ready_count",
    "live_actual_save_execution_ready_count",
    "actual_save_final_checkpoint_satisfied_count",
)
DELETE_RENAME_BLOCKED_OUTPUT_COUNT_KEYS = (
    "save_delete_rename_allowed_count",
    "delete_asset_allowed_count",
    "rename_asset_allowed_count",
)


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _count_is_one(summary: Dict[str, Any], key: str) -> bool:
    return bool(summary.get(key) == 1)


def _count_is_zero(summary: Dict[str, Any], key: str) -> bool:
    return bool(int(summary.get(key, 0) or 0) == 0)


def _target_matches(result: Dict[str, Any]) -> bool:
    return bool(result.get("target_asset_path") == DEFAULT_TARGET_ASSET_PATH)


def _target_directory_matches(result: Dict[str, Any]) -> bool:
    return bool(result.get("target_directory") == DEFAULT_TARGET_DIRECTORY)


def build_live_actual_save_execution_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_directory: str = DEFAULT_TARGET_DIRECTORY,
    asset_loaded: bool = True,
    asset_class: str = DEFAULT_ASSET_CLASS,
    blueprint_compile_attempted: bool = True,
    blueprint_compile_succeeded: bool = True,
    save_asset_called: bool = True,
    save_asset_result: bool = True,
    save_true_used: bool = True,
    live_command_dispatched: bool = True,
    live_command_executed: bool = True,
    asset_write_performed: bool = True,
    package_dirty_marked: bool = True,
    post_asset_exists: bool = True,
    package_file_exists: bool = True,
    package_file_size_bytes: int = 1,
    post_dirty_content_package_count: int = 0,
    post_dirty_map_package_count: int = 0,
    delete_asset_called: bool = False,
    rename_asset_called: bool = False,
    error: str | None = None,
) -> Dict[str, Any]:
    return {
        "schema": LIVE_ACTUAL_SAVE_EXECUTION_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_directory": target_directory,
        "asset_loaded": asset_loaded,
        "asset_class": asset_class,
        "blueprint_compile_attempted": blueprint_compile_attempted,
        "blueprint_compile_succeeded": blueprint_compile_succeeded,
        "save_asset_called": save_asset_called,
        "save_asset_result": save_asset_result,
        "save_true_used": save_true_used,
        "live_command_dispatched": live_command_dispatched,
        "live_command_executed": live_command_executed,
        "asset_write_performed": asset_write_performed,
        "package_dirty_marked": package_dirty_marked,
        "post_asset_exists": post_asset_exists,
        "package_file_exists": package_file_exists,
        "package_file_size_bytes": package_file_size_bytes,
        "post_dirty_content_package_count": post_dirty_content_package_count,
        "post_dirty_map_package_count": post_dirty_map_package_count,
        "delete_asset_called": delete_asset_called,
        "rename_asset_called": rename_asset_called,
        "error": error,
    }


def build_live_actual_save_readback_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_directory: str = DEFAULT_TARGET_DIRECTORY,
    read_only: bool = True,
    asset_exists: bool = True,
    asset_load_succeeded: bool = True,
    asset_class: str = DEFAULT_ASSET_CLASS,
    target_directory_exists: bool = True,
    package_file_exists: bool = True,
    package_file_size_bytes: int = 1,
    dirty_content_package_count: int = 0,
    dirty_map_package_count: int = 0,
    save_asset_called: bool = False,
    delete_asset_called: bool = False,
    rename_asset_called: bool = False,
    write_performed: bool = False,
) -> Dict[str, Any]:
    return {
        "schema": LIVE_ACTUAL_SAVE_READBACK_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_directory": target_directory,
        "read_only": read_only,
        "asset_exists": asset_exists,
        "asset_load_succeeded": asset_load_succeeded,
        "asset_class": asset_class,
        "target_directory_exists": target_directory_exists,
        "package_file_exists": package_file_exists,
        "package_file_size_bytes": package_file_size_bytes,
        "dirty_content_package_count": dirty_content_package_count,
        "dirty_map_package_count": dirty_map_package_count,
        "save_asset_called": save_asset_called,
        "delete_asset_called": delete_asset_called,
        "rename_asset_called": rename_asset_called,
        "write_performed": write_performed,
    }


def build_durable_executor_authoring_live_actual_save_execution_batch_contract(
    requested: bool,
    section_209_216_live_pre_save_checkpoint_summary: Dict[str, Any],
    live_actual_save_execution_result: Dict[str, Any],
    live_actual_save_readback_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_209_216_summary_schema_matches = bool(
        section_209_216_live_pre_save_checkpoint_summary.get("schema")
        == SECTION_209_216_LIVE_PRE_SAVE_CHECKPOINT_SUMMARY_SCHEMA
    )
    section_209_216_summary_passed = bool(
        section_209_216_live_pre_save_checkpoint_summary.get("status")
        == "passed"
    )
    upstream_checkpoint_ready = all(
        _count_is_one(section_209_216_live_pre_save_checkpoint_summary, key)
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_write_outputs_closed = all(
        _count_is_zero(section_209_216_live_pre_save_checkpoint_summary, key)
        for key in UPSTREAM_MUST_BE_CLOSED_COUNT_KEYS
    )

    execution_result_schema_matches = bool(
        live_actual_save_execution_result.get("schema")
        == LIVE_ACTUAL_SAVE_EXECUTION_RESULT_SCHEMA
    )
    execution_target_path_matches = _target_matches(
        live_actual_save_execution_result
    )
    execution_target_directory_matches = _target_directory_matches(
        live_actual_save_execution_result
    )
    execution_asset_loaded = bool(
        live_actual_save_execution_result.get("asset_loaded")
    )
    execution_asset_class_is_blueprint = bool(
        live_actual_save_execution_result.get("asset_class")
        == DEFAULT_ASSET_CLASS
    )
    execution_blueprint_compile_succeeded = bool(
        live_actual_save_execution_result.get("blueprint_compile_attempted")
        and live_actual_save_execution_result.get("blueprint_compile_succeeded")
    )
    execution_save_asset_succeeded = bool(
        live_actual_save_execution_result.get("save_asset_called")
        and live_actual_save_execution_result.get("save_asset_result")
        and live_actual_save_execution_result.get("save_true_used")
    )
    execution_live_command_succeeded = bool(
        live_actual_save_execution_result.get("live_command_dispatched")
        and live_actual_save_execution_result.get("live_command_executed")
    )
    execution_write_performed = bool(
        live_actual_save_execution_result.get("asset_write_performed")
        and live_actual_save_execution_result.get("package_dirty_marked")
    )
    execution_post_asset_exists = bool(
        live_actual_save_execution_result.get("post_asset_exists")
    )
    execution_package_file_exists = bool(
        live_actual_save_execution_result.get("package_file_exists")
        and int(
            live_actual_save_execution_result.get(
                "package_file_size_bytes", 0
            )
            or 0
        )
        > 0
    )
    execution_dirty_packages_cleared = bool(
        int(
            live_actual_save_execution_result.get(
                "post_dirty_content_package_count", -1
            )
        )
        == 0
        and int(
            live_actual_save_execution_result.get(
                "post_dirty_map_package_count", -1
            )
        )
        == 0
    )
    execution_delete_rename_blocked = bool(
        not live_actual_save_execution_result.get("delete_asset_called")
        and not live_actual_save_execution_result.get("rename_asset_called")
    )
    execution_has_no_error = bool(
        live_actual_save_execution_result.get("error") in (None, "")
    )

    readback_result_schema_matches = bool(
        live_actual_save_readback_result.get("schema")
        == LIVE_ACTUAL_SAVE_READBACK_RESULT_SCHEMA
    )
    readback_result_read_only = bool(
        live_actual_save_readback_result.get("read_only")
    )
    readback_target_path_matches = _target_matches(
        live_actual_save_readback_result
    )
    readback_target_directory_matches = _target_directory_matches(
        live_actual_save_readback_result
    )
    readback_asset_confirmed = bool(
        live_actual_save_readback_result.get("asset_exists")
        and live_actual_save_readback_result.get("asset_load_succeeded")
        and live_actual_save_readback_result.get("asset_class")
        == DEFAULT_ASSET_CLASS
        and live_actual_save_readback_result.get("target_directory_exists")
    )
    readback_package_file_confirmed = bool(
        live_actual_save_readback_result.get("package_file_exists")
        and int(
            live_actual_save_readback_result.get(
                "package_file_size_bytes", 0
            )
            or 0
        )
        > 0
    )
    readback_dirty_packages_zero = bool(
        int(
            live_actual_save_readback_result.get(
                "dirty_content_package_count", -1
            )
        )
        == 0
        and int(
            live_actual_save_readback_result.get("dirty_map_package_count", -1)
        )
        == 0
    )
    readback_write_outputs_blocked = bool(
        not live_actual_save_readback_result.get("save_asset_called")
        and not live_actual_save_readback_result.get("delete_asset_called")
        and not live_actual_save_readback_result.get("rename_asset_called")
        and not live_actual_save_readback_result.get("write_performed")
    )
    live_actual_save_execution_ready = bool(
        requested
        and section_209_216_summary_schema_matches
        and section_209_216_summary_passed
        and upstream_checkpoint_ready
        and upstream_write_outputs_closed
        and execution_result_schema_matches
        and execution_target_path_matches
        and execution_target_directory_matches
        and execution_asset_loaded
        and execution_asset_class_is_blueprint
        and execution_blueprint_compile_succeeded
        and execution_save_asset_succeeded
        and execution_live_command_succeeded
        and execution_write_performed
        and execution_post_asset_exists
        and execution_package_file_exists
        and execution_dirty_packages_cleared
        and execution_delete_rename_blocked
        and execution_has_no_error
        and readback_result_schema_matches
        and readback_result_read_only
        and readback_target_path_matches
        and readback_target_directory_matches
        and readback_asset_confirmed
        and readback_package_file_confirmed
        and readback_dirty_packages_zero
        and readback_write_outputs_blocked
    )
    actual_save_final_checkpoint_satisfied = live_actual_save_execution_ready
    final_durable_release_ready = live_actual_save_execution_ready

    return {
        "id": "durable_executor_authoring_live_actual_save_execution_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_LIVE_ACTUAL_SAVE_EXECUTION_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_209_216_summary_schema_matches": (
            section_209_216_summary_schema_matches
        ),
        "section_209_216_summary_passed": section_209_216_summary_passed,
        "section_209_216_live_pre_save_checkpoint_ready": (
            upstream_checkpoint_ready
        ),
        "section_209_216_write_outputs_closed": upstream_write_outputs_closed,
        "execution_result_schema_matches": execution_result_schema_matches,
        "execution_target_path_matches": execution_target_path_matches,
        "execution_target_directory_matches": (
            execution_target_directory_matches
        ),
        "execution_asset_loaded": execution_asset_loaded,
        "execution_asset_class_is_blueprint": execution_asset_class_is_blueprint,
        "execution_blueprint_compile_succeeded": (
            execution_blueprint_compile_succeeded
        ),
        "execution_save_asset_succeeded": execution_save_asset_succeeded,
        "execution_live_command_succeeded": execution_live_command_succeeded,
        "execution_write_performed": execution_write_performed,
        "execution_post_asset_exists": execution_post_asset_exists,
        "execution_package_file_exists": execution_package_file_exists,
        "execution_dirty_packages_cleared": execution_dirty_packages_cleared,
        "execution_delete_rename_blocked": execution_delete_rename_blocked,
        "execution_has_no_error": execution_has_no_error,
        "readback_result_schema_matches": readback_result_schema_matches,
        "readback_result_read_only": readback_result_read_only,
        "readback_target_path_matches": readback_target_path_matches,
        "readback_target_directory_matches": readback_target_directory_matches,
        "readback_asset_confirmed": readback_asset_confirmed,
        "readback_package_file_confirmed": readback_package_file_confirmed,
        "readback_dirty_packages_zero": readback_dirty_packages_zero,
        "readback_write_outputs_blocked": readback_write_outputs_blocked,
        "live_actual_save_execution_ready": live_actual_save_execution_ready,
        "actual_save_final_checkpoint_satisfied": (
            actual_save_final_checkpoint_satisfied
        ),
        "section_217_actual_save_approval_consumed": (
            live_actual_save_execution_ready
        ),
        "section_218_live_save_command_dispatched": (
            live_actual_save_execution_ready
        ),
        "section_219_live_temp_blueprint_write_performed": (
            live_actual_save_execution_ready
        ),
        "section_220_live_blueprint_compile_save_succeeded": (
            live_actual_save_execution_ready
        ),
        "section_221_live_save_asset_result_confirmed": (
            live_actual_save_execution_ready
        ),
        "section_222_live_saved_asset_readback_confirmed": (
            live_actual_save_execution_ready
        ),
        "section_223_live_dirty_packages_cleared_after_save": (
            live_actual_save_execution_ready
        ),
        "section_224_final_durable_release_ready": (
            final_durable_release_ready
        ),
        "durable_authoring_enabled": live_actual_save_execution_ready,
        "durable_executor_opened": live_actual_save_execution_ready,
        "durable_authoring_allowed": live_actual_save_execution_ready,
        "save_gate_open_allowed": live_actual_save_execution_ready,
        "save_gate_opened": live_actual_save_execution_ready,
        "save_command_admitted": live_actual_save_execution_ready,
        "final_pre_save_execution_ready": live_actual_save_execution_ready,
        "live_pre_save_checkpoint_ready": live_actual_save_execution_ready,
        "actual_save_execution_requires_final_user_checkpoint": False,
        "save_command_dispatched": live_actual_save_execution_ready,
        "save_command_executed": live_actual_save_execution_ready,
        "save_true_allowed": live_actual_save_execution_ready,
        "save_asset_allowed": live_actual_save_execution_ready,
        "compile_save_allowed": live_actual_save_execution_ready,
        "asset_write_performed": live_actual_save_execution_ready,
        "package_dirty_marked": live_actual_save_execution_ready,
        "live_durable_authoring_allowed": live_actual_save_execution_ready,
        "live_command_dispatched": live_actual_save_execution_ready,
        "live_command_executed": live_actual_save_execution_ready,
        "final_durable_release_ready": final_durable_release_ready,
        "save_delete_rename_allowed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        **{
            key: 1 if live_actual_save_execution_ready else 0
            for key in LIVE_ACTUAL_SAVE_EXECUTION_PATH_COUNT_KEYS
        },
        **{key: 0 for key in DELETE_RENAME_BLOCKED_OUTPUT_COUNT_KEYS},
    }


def summarize_durable_executor_authoring_live_actual_save_execution_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "live_actual_save_execution_ready")
            == len(requested)
            and _truthy_count(
                requested, "actual_save_final_checkpoint_satisfied"
            )
            == len(requested)
            and _truthy_count(requested, "final_durable_release_ready")
            == len(requested)
            and _truthy_count(requested, "save_command_dispatched")
            == len(requested)
            and _truthy_count(requested, "save_command_executed")
            == len(requested)
            and _truthy_count(requested, "save_asset_allowed")
            == len(requested)
            and _truthy_count(requested, "save_true_allowed")
            == len(requested)
            and _truthy_count(requested, "compile_save_allowed")
            == len(requested)
            and _truthy_count(requested, "asset_write_performed")
            == len(requested)
            and _truthy_count(requested, "package_dirty_marked")
            == len(requested)
            and _truthy_count(requested, "live_command_dispatched")
            == len(requested)
            and _truthy_count(requested, "live_command_executed")
            == len(requested)
            and _truthy_count(requested, "save_delete_rename_allowed") == 0
            and _truthy_count(requested, "delete_asset_allowed") == 0
            and _truthy_count(requested, "rename_asset_allowed") == 0
            and all(
                _sum_count(requested, key) == 0
                for key in DELETE_RENAME_BLOCKED_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_LIVE_ACTUAL_SAVE_EXECUTION_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_live_actual_save_execution_batch_count": (
            len(requested)
        ),
        "section_209_216_summary_schema_matches_count": _truthy_count(
            requested, "section_209_216_summary_schema_matches"
        ),
        "section_209_216_summary_passed_count": _truthy_count(
            requested, "section_209_216_summary_passed"
        ),
        "section_209_216_live_pre_save_checkpoint_ready_count": _truthy_count(
            requested,
            "section_209_216_live_pre_save_checkpoint_ready",
        ),
        "section_209_216_write_outputs_closed_count": _truthy_count(
            requested, "section_209_216_write_outputs_closed"
        ),
        "execution_result_schema_matches_count": _truthy_count(
            requested, "execution_result_schema_matches"
        ),
        "execution_target_path_matches_count": _truthy_count(
            requested, "execution_target_path_matches"
        ),
        "execution_target_directory_matches_count": _truthy_count(
            requested, "execution_target_directory_matches"
        ),
        "execution_asset_loaded_count": _truthy_count(
            requested, "execution_asset_loaded"
        ),
        "execution_asset_class_is_blueprint_count": _truthy_count(
            requested, "execution_asset_class_is_blueprint"
        ),
        "execution_blueprint_compile_succeeded_count": _truthy_count(
            requested, "execution_blueprint_compile_succeeded"
        ),
        "execution_save_asset_succeeded_count": _truthy_count(
            requested, "execution_save_asset_succeeded"
        ),
        "execution_live_command_succeeded_count": _truthy_count(
            requested, "execution_live_command_succeeded"
        ),
        "execution_write_performed_count": _truthy_count(
            requested, "execution_write_performed"
        ),
        "execution_post_asset_exists_count": _truthy_count(
            requested, "execution_post_asset_exists"
        ),
        "execution_package_file_exists_count": _truthy_count(
            requested, "execution_package_file_exists"
        ),
        "execution_dirty_packages_cleared_count": _truthy_count(
            requested, "execution_dirty_packages_cleared"
        ),
        "execution_delete_rename_blocked_count": _truthy_count(
            requested, "execution_delete_rename_blocked"
        ),
        "execution_has_no_error_count": _truthy_count(
            requested, "execution_has_no_error"
        ),
        "readback_result_schema_matches_count": _truthy_count(
            requested, "readback_result_schema_matches"
        ),
        "readback_result_read_only_count": _truthy_count(
            requested, "readback_result_read_only"
        ),
        "readback_target_path_matches_count": _truthy_count(
            requested, "readback_target_path_matches"
        ),
        "readback_target_directory_matches_count": _truthy_count(
            requested, "readback_target_directory_matches"
        ),
        "readback_asset_confirmed_count": _truthy_count(
            requested, "readback_asset_confirmed"
        ),
        "readback_package_file_confirmed_count": _truthy_count(
            requested, "readback_package_file_confirmed"
        ),
        "readback_dirty_packages_zero_count": _truthy_count(
            requested, "readback_dirty_packages_zero"
        ),
        "readback_write_outputs_blocked_count": _truthy_count(
            requested, "readback_write_outputs_blocked"
        ),
        "durable_authoring_enabled_count": _truthy_count(
            requested, "durable_authoring_enabled"
        ),
        "durable_executor_opened_count": _truthy_count(
            requested, "durable_executor_opened"
        ),
        "durable_authoring_allowed_count": _truthy_count(
            requested, "durable_authoring_allowed"
        ),
        "save_gate_open_allowed_count": _truthy_count(
            requested, "save_gate_open_allowed"
        ),
        "save_gate_opened_count": _truthy_count(
            requested, "save_gate_opened"
        ),
        "save_command_admitted_count": _truthy_count(
            requested, "save_command_admitted"
        ),
        "final_pre_save_execution_ready_count": _truthy_count(
            requested, "final_pre_save_execution_ready"
        ),
        "live_pre_save_checkpoint_ready_count": _truthy_count(
            requested, "live_pre_save_checkpoint_ready"
        ),
        "actual_save_execution_requires_final_user_checkpoint_count": (
            _truthy_count(
                requested,
                "actual_save_execution_requires_final_user_checkpoint",
            )
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
        "asset_write_performed_count": _truthy_count(
            requested, "asset_write_performed"
        ),
        "package_dirty_marked_count": _truthy_count(
            requested, "package_dirty_marked"
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
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
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
    }
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in LIVE_ACTUAL_SAVE_EXECUTION_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in DELETE_RENAME_BLOCKED_OUTPUT_COUNT_KEYS
        }
    )
    return summary
