#!/usr/bin/env python
"""
Sections 289-296 durable executor cleanup/delete actual execution batch.

This contract admits a single isolated delete of the temporary Actor Blueprint
created under /Game/_MCP_Temp. It proves the delete target, preflight, execution,
readback, and external-dirty preservation evidence while keeping broad cleanup,
rename, overwrite, compile/save, and production writes closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract as diagnostics
import project_paths


DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_ACTUAL_EXECUTION_BATCH_SCHEMA = (
    "section_289_296_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_ACTUAL_EXECUTION_BATCH_SUMMARY_SCHEMA = (
    "section_289_296_durable_executor_authoring_cleanup_delete_actual_execution_batch_summary_v1"
)
CLEANUP_DELETE_ACTUAL_EXECUTION_RESULT_SCHEMA = (
    "section_289_296_cleanup_delete_actual_execution_result_v1"
)
SECTION_281_288_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_SUMMARY_SCHEMA = (
    diagnostics
    .DURABLE_EXECUTOR_AUTHORING_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = diagnostics.DEFAULT_TARGET_ASSET_PATH
DEFAULT_TARGET_ROOT = "/Game/_MCP_Temp/DurableSaveGate/"
DEFAULT_TARGET_CONTENT_FILE = project_paths.cubeless_content_path(
    "_MCP_Temp",
    "DurableSaveGate",
    "BP_DurableSaveGatePrep.uasset",
)
DEFAULT_EXTERNAL_DIRTY_PACKAGE = "/Game/Cubeless/VFX/Fire/NS_Codex_Fire_01"
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_function_diagnostics_graph_layout_batch_count",
    "section_281_actor_bp_readback_summary_ready_count",
    "section_282_function_call_diagnostics_ready_count",
    "section_283_pin_contract_diagnostics_ready_count",
    "section_284_graph_layout_diagnostics_ready_count",
    "section_285_repair_suggestions_generated_count",
    "section_286_auto_graph_repair_execution_blocked_count",
    "section_287_diagnostics_no_write_boundary_verified_count",
    "section_288_function_diagnostics_graph_layout_release_ready_count",
    "function_call_diagnostics_ready_count",
    "graph_layout_repair_suggestions_ready_count",
    "function_diagnostics_graph_layout_no_write_verified_count",
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    "graph_repair_command_dispatched_count",
    "graph_repair_command_executed_count",
    "graph_layout_mutation_performed_count",
    "node_position_write_performed_count",
    "pin_connection_write_performed_count",
    "actor_bp_authoring_compile_dispatched_count",
    "actor_bp_authoring_compile_executed_count",
    "actor_bp_authoring_save_dispatched_count",
    "actor_bp_authoring_save_executed_count",
    "actor_bp_authoring_asset_write_performed_count",
    "actor_bp_authoring_package_dirty_marked_count",
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
CLEANUP_DELETE_ACTUAL_EXECUTION_PATH_COUNT_KEYS = (
    "section_289_cleanup_delete_actual_checkpoint_satisfied_count",
    "section_290_delete_target_scope_isolated_count",
    "section_291_delete_preflight_verified_count",
    "section_292_delete_asset_executed_count",
    "section_293_delete_readback_verified_count",
    "section_294_external_dirty_baseline_preserved_count",
    "section_295_non_delete_destructive_outputs_closed_count",
    "section_296_cleanup_delete_actual_release_ready_count",
    "cleanup_delete_actual_execution_ready_count",
    "cleanup_delete_actual_target_deleted_count",
    "cleanup_delete_actual_external_dirty_preserved_count",
)
BLOCKED_CLEANUP_DELETE_ACTUAL_OUTPUT_COUNT_KEYS = (
    "cleanup_allowed_count",
    "cleanup_executed_count",
    "rename_asset_allowed_count",
    "rename_command_dispatched_count",
    "rename_command_executed_count",
    "overwrite_allowed_count",
    "overwrite_executed_count",
    "actor_bp_authoring_compile_dispatched_count",
    "actor_bp_authoring_compile_executed_count",
    "actor_bp_authoring_save_dispatched_count",
    "actor_bp_authoring_save_executed_count",
    "actor_bp_authoring_asset_write_performed_count",
    "actor_bp_authoring_package_dirty_marked_count",
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


def build_cleanup_delete_actual_execution_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_root: str = DEFAULT_TARGET_ROOT,
    target_content_file: str = DEFAULT_TARGET_CONTENT_FILE,
    target_under_expected_root: bool = True,
    asset_exists_before: bool = True,
    asset_exists_after: bool = False,
    content_file_exists_after: bool = False,
    target_dirty_before: bool = False,
    target_dirty_after: bool = False,
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_before: Sequence[str] = (DEFAULT_EXTERNAL_DIRTY_PACKAGE,),
    external_dirty_after: Sequence[str] = (DEFAULT_EXTERNAL_DIRTY_PACKAGE,),
    external_dirty_preserved: bool = True,
    referencers_before: Sequence[str] = (),
    external_referencers_before: Sequence[str] = (),
    safety_passed_before_delete: bool = True,
    delete_asset_allowed: bool = True,
    delete_asset_executed: bool = True,
    readback_delete_verified: bool = True,
    safety_passed_after_delete: bool = True,
    cleanup_allowed: bool = False,
    cleanup_executed: bool = False,
    rename_asset_allowed: bool = False,
    rename_command_dispatched: bool = False,
    rename_command_executed: bool = False,
    overwrite_allowed: bool = False,
    overwrite_executed: bool = False,
    compile_dispatched: bool = False,
    compile_executed: bool = False,
    save_dispatched: bool = False,
    save_executed: bool = False,
    asset_write_performed: bool = False,
    package_dirty_marked: bool = False,
    production_path_write_allowed: bool = False,
    production_path_write_executed: bool = False,
    error: str | None = None,
) -> Dict[str, Any]:
    return {
        "schema": CLEANUP_DELETE_ACTUAL_EXECUTION_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_root": target_root,
        "target_content_file": target_content_file,
        "target_under_expected_root": target_under_expected_root,
        "asset_exists_before": asset_exists_before,
        "asset_exists_after": asset_exists_after,
        "content_file_exists_after": content_file_exists_after,
        "target_dirty_before": target_dirty_before,
        "target_dirty_after": target_dirty_after,
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_before": list(external_dirty_before),
        "external_dirty_after": list(external_dirty_after),
        "external_dirty_preserved": external_dirty_preserved,
        "referencers_before": list(referencers_before),
        "external_referencers_before": list(external_referencers_before),
        "safety_passed_before_delete": safety_passed_before_delete,
        "delete_asset_allowed": delete_asset_allowed,
        "delete_asset_executed": delete_asset_executed,
        "readback_delete_verified": readback_delete_verified,
        "safety_passed_after_delete": safety_passed_after_delete,
        "cleanup_allowed": cleanup_allowed,
        "cleanup_executed": cleanup_executed,
        "rename_asset_allowed": rename_asset_allowed,
        "rename_command_dispatched": rename_command_dispatched,
        "rename_command_executed": rename_command_executed,
        "overwrite_allowed": overwrite_allowed,
        "overwrite_executed": overwrite_executed,
        "compile_dispatched": compile_dispatched,
        "compile_executed": compile_executed,
        "save_dispatched": save_dispatched,
        "save_executed": save_executed,
        "asset_write_performed": asset_write_performed,
        "package_dirty_marked": package_dirty_marked,
        "production_path_write_allowed": production_path_write_allowed,
        "production_path_write_executed": production_path_write_executed,
        "error": error,
    }


def build_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract(
    requested: bool,
    section_281_288_function_diagnostics_graph_layout_summary: Dict[str, Any],
    cleanup_delete_actual_execution_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_281_288_summary_schema_matches = bool(
        section_281_288_function_diagnostics_graph_layout_summary.get("schema")
        == SECTION_281_288_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_SUMMARY_SCHEMA
    )
    section_281_288_summary_passed = bool(
        section_281_288_function_diagnostics_graph_layout_summary.get("status")
        == "passed"
    )
    upstream_diagnostics_ready = all(
        _count_is_one(
            section_281_288_function_diagnostics_graph_layout_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_281_288_function_diagnostics_graph_layout_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        cleanup_delete_actual_execution_result.get("schema")
        == CLEANUP_DELETE_ACTUAL_EXECUTION_RESULT_SCHEMA
    )
    actual_checkpoint_satisfied = bool(
        requested
        and section_281_288_summary_schema_matches
        and section_281_288_summary_passed
        and upstream_diagnostics_ready
        and upstream_outputs_closed
    )
    delete_target_scope_isolated = bool(
        cleanup_delete_actual_execution_result.get("target_asset_path")
        == DEFAULT_TARGET_ASSET_PATH
        and cleanup_delete_actual_execution_result.get("target_root")
        == DEFAULT_TARGET_ROOT
        and str(
            cleanup_delete_actual_execution_result.get("target_asset_path", "")
        ).startswith(DEFAULT_TARGET_ROOT)
        and cleanup_delete_actual_execution_result.get(
            "target_under_expected_root"
        )
        and not cleanup_delete_actual_execution_result.get(
            "external_referencers_before"
        )
    )
    delete_preflight_verified = bool(
        cleanup_delete_actual_execution_result.get("asset_exists_before")
        and not cleanup_delete_actual_execution_result.get("target_dirty_before")
        and not cleanup_delete_actual_execution_result.get("dirty_maps_before")
        and cleanup_delete_actual_execution_result.get(
            "safety_passed_before_delete"
        )
    )
    delete_asset_executed = bool(
        cleanup_delete_actual_execution_result.get("delete_asset_allowed")
        and cleanup_delete_actual_execution_result.get("delete_asset_executed")
    )
    delete_readback_verified = bool(
        delete_asset_executed
        and not cleanup_delete_actual_execution_result.get("asset_exists_after")
        and not cleanup_delete_actual_execution_result.get(
            "content_file_exists_after"
        )
        and cleanup_delete_actual_execution_result.get(
            "readback_delete_verified"
        )
        and not cleanup_delete_actual_execution_result.get("target_dirty_after")
    )
    external_dirty_baseline_preserved = bool(
        cleanup_delete_actual_execution_result.get("external_dirty_preserved")
        and cleanup_delete_actual_execution_result.get("external_dirty_before")
        == cleanup_delete_actual_execution_result.get("external_dirty_after")
        and cleanup_delete_actual_execution_result.get("dirty_maps_before")
        == cleanup_delete_actual_execution_result.get("dirty_maps_after")
    )
    non_delete_destructive_outputs_closed = bool(
        not cleanup_delete_actual_execution_result.get("cleanup_allowed")
        and not cleanup_delete_actual_execution_result.get("cleanup_executed")
        and not cleanup_delete_actual_execution_result.get(
            "rename_asset_allowed"
        )
        and not cleanup_delete_actual_execution_result.get(
            "rename_command_dispatched"
        )
        and not cleanup_delete_actual_execution_result.get(
            "rename_command_executed"
        )
        and not cleanup_delete_actual_execution_result.get("overwrite_allowed")
        and not cleanup_delete_actual_execution_result.get("overwrite_executed")
        and not cleanup_delete_actual_execution_result.get(
            "compile_dispatched"
        )
        and not cleanup_delete_actual_execution_result.get("compile_executed")
        and not cleanup_delete_actual_execution_result.get("save_dispatched")
        and not cleanup_delete_actual_execution_result.get("save_executed")
        and not cleanup_delete_actual_execution_result.get(
            "asset_write_performed"
        )
        and not cleanup_delete_actual_execution_result.get(
            "package_dirty_marked"
        )
        and not cleanup_delete_actual_execution_result.get(
            "production_path_write_allowed"
        )
        and not cleanup_delete_actual_execution_result.get(
            "production_path_write_executed"
        )
    )
    result_has_no_error = bool(
        cleanup_delete_actual_execution_result.get("error") in (None, "")
    )
    cleanup_delete_actual_passed = bool(
        actual_checkpoint_satisfied
        and result_schema_matches
        and delete_target_scope_isolated
        and delete_preflight_verified
        and delete_asset_executed
        and delete_readback_verified
        and external_dirty_baseline_preserved
        and non_delete_destructive_outputs_closed
        and cleanup_delete_actual_execution_result.get(
            "safety_passed_after_delete"
        )
        and result_has_no_error
    )

    return {
        "id": "durable_executor_authoring_cleanup_delete_actual_execution_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_ACTUAL_EXECUTION_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_281_288_summary_schema_matches": (
            section_281_288_summary_schema_matches
        ),
        "section_281_288_summary_passed": section_281_288_summary_passed,
        "section_281_288_function_diagnostics_graph_layout_ready": (
            upstream_diagnostics_ready
        ),
        "section_281_288_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "actual_checkpoint_satisfied": actual_checkpoint_satisfied,
        "delete_target_scope_isolated": delete_target_scope_isolated,
        "delete_preflight_verified": delete_preflight_verified,
        "delete_asset_executed": delete_asset_executed,
        "delete_readback_verified": delete_readback_verified,
        "external_dirty_baseline_preserved": (
            external_dirty_baseline_preserved
        ),
        "non_delete_destructive_outputs_closed": (
            non_delete_destructive_outputs_closed
        ),
        "result_has_no_error": result_has_no_error,
        "section_289_cleanup_delete_actual_checkpoint_satisfied": (
            cleanup_delete_actual_passed
        ),
        "section_290_delete_target_scope_isolated": (
            cleanup_delete_actual_passed
        ),
        "section_291_delete_preflight_verified": cleanup_delete_actual_passed,
        "section_292_delete_asset_executed": cleanup_delete_actual_passed,
        "section_293_delete_readback_verified": cleanup_delete_actual_passed,
        "section_294_external_dirty_baseline_preserved": (
            cleanup_delete_actual_passed
        ),
        "section_295_non_delete_destructive_outputs_closed": (
            cleanup_delete_actual_passed
        ),
        "section_296_cleanup_delete_actual_release_ready": (
            cleanup_delete_actual_passed
        ),
        "cleanup_delete_actual_execution_ready": cleanup_delete_actual_passed,
        "cleanup_delete_actual_target_deleted": cleanup_delete_actual_passed,
        "cleanup_delete_actual_external_dirty_preserved": (
            cleanup_delete_actual_passed
        ),
        "final_durable_release_ready": cleanup_delete_actual_passed,
        "delete_asset_allowed": cleanup_delete_actual_passed,
        "delete_asset_executed_output": cleanup_delete_actual_passed,
        "cleanup_allowed": False,
        "cleanup_executed": False,
        "rename_asset_allowed": False,
        "rename_command_dispatched": False,
        "rename_command_executed": False,
        "overwrite_allowed": False,
        "overwrite_executed": False,
        "actor_bp_authoring_compile_dispatched": False,
        "actor_bp_authoring_compile_executed": False,
        "actor_bp_authoring_save_dispatched": False,
        "actor_bp_authoring_save_executed": False,
        "actor_bp_authoring_asset_write_performed": False,
        "actor_bp_authoring_package_dirty_marked": False,
        "production_path_write_allowed": False,
        "production_path_write_executed": False,
        **{
            key: 1 if cleanup_delete_actual_passed else 0
            for key in CLEANUP_DELETE_ACTUAL_EXECUTION_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_CLEANUP_DELETE_ACTUAL_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_cleanup_delete_actual_execution_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "cleanup_delete_actual_execution_ready"
            )
            == len(requested)
            and _truthy_count(
                requested, "cleanup_delete_actual_target_deleted"
            )
            == len(requested)
            and _truthy_count(
                requested,
                "cleanup_delete_actual_external_dirty_preserved",
            )
            == len(requested)
            and _truthy_count(requested, "delete_asset_allowed")
            == len(requested)
            and _truthy_count(requested, "delete_asset_executed_output")
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_CLEANUP_DELETE_ACTUAL_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_ACTUAL_EXECUTION_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_cleanup_delete_actual_execution_batch_count": (
            len(requested)
        ),
        "section_281_288_summary_schema_matches_count": _truthy_count(
            requested, "section_281_288_summary_schema_matches"
        ),
        "section_281_288_summary_passed_count": _truthy_count(
            requested, "section_281_288_summary_passed"
        ),
        "section_281_288_function_diagnostics_graph_layout_ready_count": (
            _truthy_count(
                requested,
                "section_281_288_function_diagnostics_graph_layout_ready",
            )
        ),
        "section_281_288_outputs_closed_count": _truthy_count(
            requested, "section_281_288_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "actual_checkpoint_satisfied_count": _truthy_count(
            requested, "actual_checkpoint_satisfied"
        ),
        "delete_target_scope_isolated_count": _truthy_count(
            requested, "delete_target_scope_isolated"
        ),
        "delete_preflight_verified_count": _truthy_count(
            requested, "delete_preflight_verified"
        ),
        "delete_asset_executed_count": _truthy_count(
            requested, "delete_asset_executed"
        ),
        "delete_readback_verified_count": _truthy_count(
            requested, "delete_readback_verified"
        ),
        "external_dirty_baseline_preserved_count": _truthy_count(
            requested, "external_dirty_baseline_preserved"
        ),
        "non_delete_destructive_outputs_closed_count": _truthy_count(
            requested, "non_delete_destructive_outputs_closed"
        ),
        "result_has_no_error_count": _truthy_count(
            requested, "result_has_no_error"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "delete_asset_allowed_count": _truthy_count(
            requested, "delete_asset_allowed"
        ),
        "delete_asset_executed_output_count": _truthy_count(
            requested, "delete_asset_executed_output"
        ),
        "cleanup_allowed_count": _truthy_count(requested, "cleanup_allowed"),
        "cleanup_executed_count": _truthy_count(requested, "cleanup_executed"),
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
        "actor_bp_authoring_compile_dispatched_count": _truthy_count(
            requested, "actor_bp_authoring_compile_dispatched"
        ),
        "actor_bp_authoring_compile_executed_count": _truthy_count(
            requested, "actor_bp_authoring_compile_executed"
        ),
        "actor_bp_authoring_save_dispatched_count": _truthy_count(
            requested, "actor_bp_authoring_save_dispatched"
        ),
        "actor_bp_authoring_save_executed_count": _truthy_count(
            requested, "actor_bp_authoring_save_executed"
        ),
        "actor_bp_authoring_asset_write_performed_count": _truthy_count(
            requested, "actor_bp_authoring_asset_write_performed"
        ),
        "actor_bp_authoring_package_dirty_marked_count": _truthy_count(
            requested, "actor_bp_authoring_package_dirty_marked"
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
            for key in CLEANUP_DELETE_ACTUAL_EXECUTION_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_CLEANUP_DELETE_ACTUAL_OUTPUT_COUNT_KEYS
        }
    )
    return summary
