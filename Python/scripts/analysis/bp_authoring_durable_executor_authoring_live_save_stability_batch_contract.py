#!/usr/bin/env python
"""
Sections 225-232 durable executor authoring live save stability batch.

This contract stabilizes the target-scoped live save path after the first
successful temp Blueprint save. It records the fixed UE 5.7 compile API,
partial-save recovery evidence, idempotent re-save/readback stability, and
dirty-package cleanup while keeping cleanup, delete, rename, and production
paths gated.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_live_actual_save_execution_batch_contract as live_actual_save_execution


DURABLE_EXECUTOR_AUTHORING_LIVE_SAVE_STABILITY_BATCH_SCHEMA = (
    "section_225_232_durable_executor_authoring_live_save_stability_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_LIVE_SAVE_STABILITY_BATCH_SUMMARY_SCHEMA = (
    "section_225_232_durable_executor_authoring_live_save_stability_batch_summary_v1"
)
LIVE_SAVE_STABILITY_RESULT_SCHEMA = (
    "section_225_232_live_save_stability_result_v1"
)
SECTION_217_224_LIVE_ACTUAL_SAVE_EXECUTION_SUMMARY_SCHEMA = (
    live_actual_save_execution
    .DURABLE_EXECUTOR_AUTHORING_LIVE_ACTUAL_SAVE_EXECUTION_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = live_actual_save_execution.DEFAULT_TARGET_ASSET_PATH
DEFAULT_TARGET_DIRECTORY = live_actual_save_execution.DEFAULT_TARGET_DIRECTORY
FIXED_COMPILE_API_NAME = "BlueprintEditorLibrary.compile_blueprint"
LEGACY_COMPILE_HELPER_NAME = "KismetEditorUtilities.compile_blueprint"
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_live_actual_save_execution_batch_count",
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
    "save_command_dispatched_count",
    "save_command_executed_count",
    "save_true_allowed_count",
    "save_asset_allowed_count",
    "compile_save_allowed_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
    "final_durable_release_ready_count",
)
UPSTREAM_DELETE_RENAME_MUST_BE_CLOSED_COUNT_KEYS = (
    "save_delete_rename_allowed_count",
    "delete_asset_allowed_count",
    "rename_asset_allowed_count",
)
LIVE_SAVE_STABILITY_PATH_COUNT_KEYS = (
    "section_225_live_compile_api_fixed_count",
    "section_226_live_legacy_compile_helper_mismatch_documented_count",
    "section_227_live_partial_save_recovery_verified_count",
    "section_228_live_idempotent_resave_verified_count",
    "section_229_live_save_readback_schema_strengthened_count",
    "section_230_live_dirty_package_stability_verified_count",
    "section_231_live_production_path_untouched_count",
    "section_232_live_delete_rename_cleanup_still_gated_count",
    "live_save_stability_ready_count",
)
DELETE_RENAME_CLEANUP_BLOCKED_OUTPUT_COUNT_KEYS = (
    "cleanup_allowed_count",
    "cleanup_executed_count",
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


def build_live_save_stability_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_directory: str = DEFAULT_TARGET_DIRECTORY,
    compile_api_name: str = FIXED_COMPILE_API_NAME,
    legacy_compile_helper_name: str = LEGACY_COMPILE_HELPER_NAME,
    legacy_compile_helper_unavailable: bool = True,
    compile_api_recovery_documented: bool = True,
    partial_save_failure_detected: bool = True,
    partial_save_recovery_completed: bool = True,
    idempotent_resave_attempted: bool = True,
    idempotent_resave_succeeded: bool = True,
    final_readback_confirmed: bool = True,
    package_file_exists: bool = True,
    package_file_size_bytes: int = 1,
    final_dirty_content_package_count: int = 0,
    final_dirty_map_package_count: int = 0,
    cleanup_allowed: bool = False,
    cleanup_executed: bool = False,
    delete_asset_called: bool = False,
    rename_asset_called: bool = False,
    production_path_touched: bool = False,
    error: str | None = None,
) -> Dict[str, Any]:
    return {
        "schema": LIVE_SAVE_STABILITY_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_directory": target_directory,
        "compile_api_name": compile_api_name,
        "legacy_compile_helper_name": legacy_compile_helper_name,
        "legacy_compile_helper_unavailable": legacy_compile_helper_unavailable,
        "compile_api_recovery_documented": compile_api_recovery_documented,
        "partial_save_failure_detected": partial_save_failure_detected,
        "partial_save_recovery_completed": partial_save_recovery_completed,
        "idempotent_resave_attempted": idempotent_resave_attempted,
        "idempotent_resave_succeeded": idempotent_resave_succeeded,
        "final_readback_confirmed": final_readback_confirmed,
        "package_file_exists": package_file_exists,
        "package_file_size_bytes": package_file_size_bytes,
        "final_dirty_content_package_count": final_dirty_content_package_count,
        "final_dirty_map_package_count": final_dirty_map_package_count,
        "cleanup_allowed": cleanup_allowed,
        "cleanup_executed": cleanup_executed,
        "delete_asset_called": delete_asset_called,
        "rename_asset_called": rename_asset_called,
        "production_path_touched": production_path_touched,
        "error": error,
    }


def build_durable_executor_authoring_live_save_stability_batch_contract(
    requested: bool,
    section_217_224_live_actual_save_execution_summary: Dict[str, Any],
    live_save_stability_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_217_224_summary_schema_matches = bool(
        section_217_224_live_actual_save_execution_summary.get("schema")
        == SECTION_217_224_LIVE_ACTUAL_SAVE_EXECUTION_SUMMARY_SCHEMA
    )
    section_217_224_summary_passed = bool(
        section_217_224_live_actual_save_execution_summary.get("status")
        == "passed"
    )
    upstream_actual_save_ready = all(
        _count_is_one(section_217_224_live_actual_save_execution_summary, key)
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_delete_rename_closed = all(
        _count_is_zero(
            section_217_224_live_actual_save_execution_summary, key
        )
        for key in UPSTREAM_DELETE_RENAME_MUST_BE_CLOSED_COUNT_KEYS
    )
    stability_result_schema_matches = bool(
        live_save_stability_result.get("schema")
        == LIVE_SAVE_STABILITY_RESULT_SCHEMA
    )
    target_path_matches = bool(
        live_save_stability_result.get("target_asset_path")
        == DEFAULT_TARGET_ASSET_PATH
    )
    target_directory_matches = bool(
        live_save_stability_result.get("target_directory")
        == DEFAULT_TARGET_DIRECTORY
    )
    compile_api_fixed = bool(
        live_save_stability_result.get("compile_api_name")
        == FIXED_COMPILE_API_NAME
    )
    legacy_compile_helper_mismatch_documented = bool(
        live_save_stability_result.get("legacy_compile_helper_name")
        == LEGACY_COMPILE_HELPER_NAME
        and live_save_stability_result.get("legacy_compile_helper_unavailable")
        and live_save_stability_result.get("compile_api_recovery_documented")
    )
    partial_save_recovery_verified = bool(
        live_save_stability_result.get("partial_save_failure_detected")
        and live_save_stability_result.get("partial_save_recovery_completed")
    )
    idempotent_resave_verified = bool(
        live_save_stability_result.get("idempotent_resave_attempted")
        and live_save_stability_result.get("idempotent_resave_succeeded")
    )
    save_readback_schema_strengthened = bool(
        live_save_stability_result.get("final_readback_confirmed")
        and live_save_stability_result.get("package_file_exists")
        and int(live_save_stability_result.get("package_file_size_bytes", 0) or 0)
        > 0
    )
    dirty_package_stability_verified = bool(
        int(
            live_save_stability_result.get(
                "final_dirty_content_package_count", -1
            )
        )
        == 0
        and int(
            live_save_stability_result.get("final_dirty_map_package_count", -1)
        )
        == 0
    )
    production_path_untouched = bool(
        not live_save_stability_result.get("production_path_touched")
    )
    delete_rename_cleanup_still_gated = bool(
        not live_save_stability_result.get("cleanup_allowed")
        and not live_save_stability_result.get("cleanup_executed")
        and not live_save_stability_result.get("delete_asset_called")
        and not live_save_stability_result.get("rename_asset_called")
    )
    stability_has_no_error = bool(
        live_save_stability_result.get("error") in (None, "")
    )
    live_save_stability_ready = bool(
        requested
        and section_217_224_summary_schema_matches
        and section_217_224_summary_passed
        and upstream_actual_save_ready
        and upstream_delete_rename_closed
        and stability_result_schema_matches
        and target_path_matches
        and target_directory_matches
        and compile_api_fixed
        and legacy_compile_helper_mismatch_documented
        and partial_save_recovery_verified
        and idempotent_resave_verified
        and save_readback_schema_strengthened
        and dirty_package_stability_verified
        and production_path_untouched
        and delete_rename_cleanup_still_gated
        and stability_has_no_error
    )

    return {
        "id": "durable_executor_authoring_live_save_stability_batch",
        "schema": DURABLE_EXECUTOR_AUTHORING_LIVE_SAVE_STABILITY_BATCH_SCHEMA,
        "requested": requested,
        "section_217_224_summary_schema_matches": (
            section_217_224_summary_schema_matches
        ),
        "section_217_224_summary_passed": section_217_224_summary_passed,
        "section_217_224_actual_save_ready": upstream_actual_save_ready,
        "section_217_224_delete_rename_closed": upstream_delete_rename_closed,
        "stability_result_schema_matches": stability_result_schema_matches,
        "target_path_matches": target_path_matches,
        "target_directory_matches": target_directory_matches,
        "compile_api_fixed": compile_api_fixed,
        "legacy_compile_helper_mismatch_documented": (
            legacy_compile_helper_mismatch_documented
        ),
        "partial_save_recovery_verified": partial_save_recovery_verified,
        "idempotent_resave_verified": idempotent_resave_verified,
        "save_readback_schema_strengthened": save_readback_schema_strengthened,
        "dirty_package_stability_verified": dirty_package_stability_verified,
        "production_path_untouched": production_path_untouched,
        "delete_rename_cleanup_still_gated": delete_rename_cleanup_still_gated,
        "stability_has_no_error": stability_has_no_error,
        "live_save_stability_ready": live_save_stability_ready,
        "section_225_live_compile_api_fixed": live_save_stability_ready,
        "section_226_live_legacy_compile_helper_mismatch_documented": (
            live_save_stability_ready
        ),
        "section_227_live_partial_save_recovery_verified": (
            live_save_stability_ready
        ),
        "section_228_live_idempotent_resave_verified": (
            live_save_stability_ready
        ),
        "section_229_live_save_readback_schema_strengthened": (
            live_save_stability_ready
        ),
        "section_230_live_dirty_package_stability_verified": (
            live_save_stability_ready
        ),
        "section_231_live_production_path_untouched": (
            live_save_stability_ready
        ),
        "section_232_live_delete_rename_cleanup_still_gated": (
            live_save_stability_ready
        ),
        "durable_authoring_enabled": live_save_stability_ready,
        "durable_executor_opened": live_save_stability_ready,
        "durable_authoring_allowed": live_save_stability_ready,
        "save_gate_open_allowed": live_save_stability_ready,
        "save_gate_opened": live_save_stability_ready,
        "save_command_admitted": live_save_stability_ready,
        "save_command_dispatched": live_save_stability_ready,
        "save_command_executed": live_save_stability_ready,
        "save_true_allowed": live_save_stability_ready,
        "save_asset_allowed": live_save_stability_ready,
        "compile_save_allowed": live_save_stability_ready,
        "asset_write_performed": live_save_stability_ready,
        "package_dirty_marked": live_save_stability_ready,
        "live_durable_authoring_allowed": live_save_stability_ready,
        "live_command_dispatched": live_save_stability_ready,
        "live_command_executed": live_save_stability_ready,
        "final_durable_release_ready": live_save_stability_ready,
        "cleanup_allowed": False,
        "cleanup_executed": False,
        "save_delete_rename_allowed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        "production_path_write_allowed": False,
        "production_path_write_executed": False,
        **{
            key: 1 if live_save_stability_ready else 0
            for key in LIVE_SAVE_STABILITY_PATH_COUNT_KEYS
        },
        **{key: 0 for key in DELETE_RENAME_CLEANUP_BLOCKED_OUTPUT_COUNT_KEYS},
    }


def summarize_durable_executor_authoring_live_save_stability_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "live_save_stability_ready")
            == len(requested)
            and _truthy_count(requested, "final_durable_release_ready")
            == len(requested)
            and _truthy_count(requested, "save_asset_allowed") == len(requested)
            and _truthy_count(requested, "compile_save_allowed")
            == len(requested)
            and _truthy_count(requested, "cleanup_allowed") == 0
            and _truthy_count(requested, "cleanup_executed") == 0
            and _truthy_count(requested, "save_delete_rename_allowed") == 0
            and _truthy_count(requested, "delete_asset_allowed") == 0
            and _truthy_count(requested, "rename_asset_allowed") == 0
            and _truthy_count(requested, "production_path_write_allowed") == 0
            and _truthy_count(requested, "production_path_write_executed") == 0
            and all(
                _sum_count(requested, key) == 0
                for key in DELETE_RENAME_CLEANUP_BLOCKED_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_LIVE_SAVE_STABILITY_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_live_save_stability_batch_count": (
            len(requested)
        ),
        "section_217_224_summary_schema_matches_count": _truthy_count(
            requested, "section_217_224_summary_schema_matches"
        ),
        "section_217_224_summary_passed_count": _truthy_count(
            requested, "section_217_224_summary_passed"
        ),
        "section_217_224_actual_save_ready_count": _truthy_count(
            requested, "section_217_224_actual_save_ready"
        ),
        "section_217_224_delete_rename_closed_count": _truthy_count(
            requested, "section_217_224_delete_rename_closed"
        ),
        "stability_result_schema_matches_count": _truthy_count(
            requested, "stability_result_schema_matches"
        ),
        "target_path_matches_count": _truthy_count(
            requested, "target_path_matches"
        ),
        "target_directory_matches_count": _truthy_count(
            requested, "target_directory_matches"
        ),
        "compile_api_fixed_count": _truthy_count(
            requested, "compile_api_fixed"
        ),
        "legacy_compile_helper_mismatch_documented_count": _truthy_count(
            requested, "legacy_compile_helper_mismatch_documented"
        ),
        "partial_save_recovery_verified_count": _truthy_count(
            requested, "partial_save_recovery_verified"
        ),
        "idempotent_resave_verified_count": _truthy_count(
            requested, "idempotent_resave_verified"
        ),
        "save_readback_schema_strengthened_count": _truthy_count(
            requested, "save_readback_schema_strengthened"
        ),
        "dirty_package_stability_verified_count": _truthy_count(
            requested, "dirty_package_stability_verified"
        ),
        "production_path_untouched_count": _truthy_count(
            requested, "production_path_untouched"
        ),
        "delete_rename_cleanup_still_gated_count": _truthy_count(
            requested, "delete_rename_cleanup_still_gated"
        ),
        "stability_has_no_error_count": _truthy_count(
            requested, "stability_has_no_error"
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
        "save_gate_opened_count": _truthy_count(requested, "save_gate_opened"),
        "save_command_admitted_count": _truthy_count(
            requested, "save_command_admitted"
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
        "cleanup_allowed_count": _truthy_count(requested, "cleanup_allowed"),
        "cleanup_executed_count": _truthy_count(requested, "cleanup_executed"),
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
            for key in LIVE_SAVE_STABILITY_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in DELETE_RENAME_CLEANUP_BLOCKED_OUTPUT_COUNT_KEYS
        }
    )
    return summary
