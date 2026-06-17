#!/usr/bin/env python
"""
Sections 297-304 durable executor post-delete recreation/readback reset.

This contract follows the isolated Section 289-296 temp Blueprint delete. It
proves the deleted target is absent, resets readback/diagnostics expectations,
and scopes a future temp Actor Blueprint recreation plan behind a separate
explicit checkpoint. It does not recreate, save, delete, rename, overwrite, or
mutate graph layout.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_cleanup_delete_actual_execution_batch_contract as cleanup_delete


DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_RESET_BATCH_SCHEMA = (
    "section_297_304_durable_executor_authoring_post_delete_recreation_reset_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_RESET_BATCH_SUMMARY_SCHEMA = (
    "section_297_304_durable_executor_authoring_post_delete_recreation_reset_batch_summary_v1"
)
POST_DELETE_RECREATION_RESET_RESULT_SCHEMA = (
    "section_297_304_post_delete_recreation_reset_result_v1"
)
SECTION_289_296_CLEANUP_DELETE_ACTUAL_EXECUTION_SUMMARY_SCHEMA = (
    cleanup_delete
    .DURABLE_EXECUTOR_AUTHORING_CLEANUP_DELETE_ACTUAL_EXECUTION_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = cleanup_delete.DEFAULT_TARGET_ASSET_PATH
DEFAULT_TARGET_ROOT = cleanup_delete.DEFAULT_TARGET_ROOT
DEFAULT_TARGET_CONTENT_FILE = cleanup_delete.DEFAULT_TARGET_CONTENT_FILE
DEFAULT_EXTERNAL_DIRTY_PACKAGE = cleanup_delete.DEFAULT_EXTERNAL_DIRTY_PACKAGE
DEFAULT_RECREATION_PLAN_ID = "recreate_temp_actor_bp_after_delete"
DEFAULT_RECREATION_PARENT_CLASS = "Actor"
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_cleanup_delete_actual_execution_batch_count",
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
    "delete_asset_allowed_count",
    "delete_asset_executed_output_count",
    "final_durable_release_ready_count",
)
UPSTREAM_NON_DELETE_OUTPUTS_CLOSED_COUNT_KEYS = (
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
POST_DELETE_RECREATION_RESET_PATH_COUNT_KEYS = (
    "section_297_post_delete_checkpoint_satisfied_count",
    "section_298_deleted_target_absence_confirmed_count",
    "section_299_recreation_plan_scoped_count",
    "section_300_recreation_requires_explicit_checkpoint_count",
    "section_301_readback_routes_reset_count",
    "section_302_diagnostics_routes_reset_count",
    "section_303_post_delete_no_write_boundary_verified_count",
    "section_304_post_delete_reset_release_ready_count",
    "post_delete_recreation_reset_ready_count",
    "post_delete_target_absence_confirmed_count",
    "post_delete_recreation_requires_checkpoint_count",
)
BLOCKED_POST_DELETE_RECREATION_RESET_OUTPUT_COUNT_KEYS = (
    "recreate_asset_allowed_count",
    "recreate_command_dispatched_count",
    "recreate_command_executed_count",
    "readback_command_dispatched_count",
    "readback_command_executed_count",
    "diagnostics_command_dispatched_count",
    "diagnostics_command_executed_count",
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
    "delete_asset_executed_output_count",
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


def build_post_delete_recreation_reset_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_root: str = DEFAULT_TARGET_ROOT,
    target_content_file: str = DEFAULT_TARGET_CONTENT_FILE,
    target_under_expected_root: bool = True,
    asset_exists_after_delete: bool = False,
    asset_data_valid_after_delete: bool = False,
    content_file_exists_after_delete: bool = False,
    deleted_target_absence_confirmed: bool = True,
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_before: Sequence[str] = (DEFAULT_EXTERNAL_DIRTY_PACKAGE,),
    external_dirty_after: Sequence[str] = (DEFAULT_EXTERNAL_DIRTY_PACKAGE,),
    external_dirty_preserved: bool = True,
    recreation_plan_id: str = DEFAULT_RECREATION_PLAN_ID,
    recreation_parent_class: str = DEFAULT_RECREATION_PARENT_CLASS,
    recreation_plan_prepared: bool = True,
    recreation_target_root_scoped: bool = True,
    recreation_requires_explicit_checkpoint: bool = True,
    readback_routes_reset: bool = True,
    diagnostics_routes_reset: bool = True,
    previous_readback_evidence_invalidated: bool = True,
    read_only_preflight: bool = True,
    recreate_asset_allowed: bool = False,
    recreate_command_dispatched: bool = False,
    recreate_command_executed: bool = False,
    readback_command_dispatched: bool = False,
    readback_command_executed: bool = False,
    diagnostics_command_dispatched: bool = False,
    diagnostics_command_executed: bool = False,
    graph_repair_command_dispatched: bool = False,
    graph_repair_command_executed: bool = False,
    graph_layout_mutation_performed: bool = False,
    node_position_write_performed: bool = False,
    pin_connection_write_performed: bool = False,
    compile_dispatched: bool = False,
    compile_executed: bool = False,
    save_dispatched: bool = False,
    save_executed: bool = False,
    asset_write_performed: bool = False,
    package_dirty_marked: bool = False,
    cleanup_allowed: bool = False,
    cleanup_executed: bool = False,
    delete_asset_allowed: bool = False,
    delete_asset_executed_output: bool = False,
    rename_asset_allowed: bool = False,
    rename_command_dispatched: bool = False,
    rename_command_executed: bool = False,
    overwrite_allowed: bool = False,
    overwrite_executed: bool = False,
    production_path_write_allowed: bool = False,
    production_path_write_executed: bool = False,
    error: str | None = None,
) -> Dict[str, Any]:
    return {
        "schema": POST_DELETE_RECREATION_RESET_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_root": target_root,
        "target_content_file": target_content_file,
        "target_under_expected_root": target_under_expected_root,
        "asset_exists_after_delete": asset_exists_after_delete,
        "asset_data_valid_after_delete": asset_data_valid_after_delete,
        "content_file_exists_after_delete": content_file_exists_after_delete,
        "deleted_target_absence_confirmed": deleted_target_absence_confirmed,
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_before": list(external_dirty_before),
        "external_dirty_after": list(external_dirty_after),
        "external_dirty_preserved": external_dirty_preserved,
        "recreation_plan_id": recreation_plan_id,
        "recreation_parent_class": recreation_parent_class,
        "recreation_plan_prepared": recreation_plan_prepared,
        "recreation_target_root_scoped": recreation_target_root_scoped,
        "recreation_requires_explicit_checkpoint": (
            recreation_requires_explicit_checkpoint
        ),
        "readback_routes_reset": readback_routes_reset,
        "diagnostics_routes_reset": diagnostics_routes_reset,
        "previous_readback_evidence_invalidated": (
            previous_readback_evidence_invalidated
        ),
        "read_only_preflight": read_only_preflight,
        "recreate_asset_allowed": recreate_asset_allowed,
        "recreate_command_dispatched": recreate_command_dispatched,
        "recreate_command_executed": recreate_command_executed,
        "readback_command_dispatched": readback_command_dispatched,
        "readback_command_executed": readback_command_executed,
        "diagnostics_command_dispatched": diagnostics_command_dispatched,
        "diagnostics_command_executed": diagnostics_command_executed,
        "graph_repair_command_dispatched": graph_repair_command_dispatched,
        "graph_repair_command_executed": graph_repair_command_executed,
        "graph_layout_mutation_performed": graph_layout_mutation_performed,
        "node_position_write_performed": node_position_write_performed,
        "pin_connection_write_performed": pin_connection_write_performed,
        "compile_dispatched": compile_dispatched,
        "compile_executed": compile_executed,
        "save_dispatched": save_dispatched,
        "save_executed": save_executed,
        "asset_write_performed": asset_write_performed,
        "package_dirty_marked": package_dirty_marked,
        "cleanup_allowed": cleanup_allowed,
        "cleanup_executed": cleanup_executed,
        "delete_asset_allowed": delete_asset_allowed,
        "delete_asset_executed_output": delete_asset_executed_output,
        "rename_asset_allowed": rename_asset_allowed,
        "rename_command_dispatched": rename_command_dispatched,
        "rename_command_executed": rename_command_executed,
        "overwrite_allowed": overwrite_allowed,
        "overwrite_executed": overwrite_executed,
        "production_path_write_allowed": production_path_write_allowed,
        "production_path_write_executed": production_path_write_executed,
        "error": error,
    }


def build_durable_executor_authoring_post_delete_recreation_reset_batch_contract(
    requested: bool,
    section_289_296_cleanup_delete_actual_execution_summary: Dict[str, Any],
    post_delete_recreation_reset_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_289_296_summary_schema_matches = bool(
        section_289_296_cleanup_delete_actual_execution_summary.get("schema")
        == SECTION_289_296_CLEANUP_DELETE_ACTUAL_EXECUTION_SUMMARY_SCHEMA
    )
    section_289_296_summary_passed = bool(
        section_289_296_cleanup_delete_actual_execution_summary.get("status")
        == "passed"
    )
    upstream_cleanup_delete_ready = all(
        _count_is_one(
            section_289_296_cleanup_delete_actual_execution_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_non_delete_outputs_closed = all(
        _count_is_zero(
            section_289_296_cleanup_delete_actual_execution_summary,
            key,
        )
        for key in UPSTREAM_NON_DELETE_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        post_delete_recreation_reset_result.get("schema")
        == POST_DELETE_RECREATION_RESET_RESULT_SCHEMA
    )
    post_delete_checkpoint_satisfied = bool(
        requested
        and section_289_296_summary_schema_matches
        and section_289_296_summary_passed
        and upstream_cleanup_delete_ready
        and upstream_non_delete_outputs_closed
    )
    deleted_target_absence_confirmed = bool(
        post_delete_recreation_reset_result.get("target_asset_path")
        == DEFAULT_TARGET_ASSET_PATH
        and post_delete_recreation_reset_result.get("target_root")
        == DEFAULT_TARGET_ROOT
        and str(
            post_delete_recreation_reset_result.get("target_asset_path", "")
        ).startswith(DEFAULT_TARGET_ROOT)
        and post_delete_recreation_reset_result.get(
            "target_under_expected_root"
        )
        and post_delete_recreation_reset_result.get(
            "deleted_target_absence_confirmed"
        )
        and not post_delete_recreation_reset_result.get(
            "asset_exists_after_delete"
        )
        and not post_delete_recreation_reset_result.get(
            "asset_data_valid_after_delete"
        )
        and not post_delete_recreation_reset_result.get(
            "content_file_exists_after_delete"
        )
    )
    recreation_plan_scoped = bool(
        post_delete_recreation_reset_result.get("recreation_plan_id")
        == DEFAULT_RECREATION_PLAN_ID
        and post_delete_recreation_reset_result.get(
            "recreation_parent_class"
        )
        == DEFAULT_RECREATION_PARENT_CLASS
        and post_delete_recreation_reset_result.get(
            "recreation_plan_prepared"
        )
        and post_delete_recreation_reset_result.get(
            "recreation_target_root_scoped"
        )
        and str(
            post_delete_recreation_reset_result.get("target_asset_path", "")
        ).startswith(DEFAULT_TARGET_ROOT)
    )
    recreation_requires_explicit_checkpoint = bool(
        post_delete_recreation_reset_result.get(
            "recreation_requires_explicit_checkpoint"
        )
        and not post_delete_recreation_reset_result.get(
            "recreate_asset_allowed"
        )
        and not post_delete_recreation_reset_result.get(
            "recreate_command_dispatched"
        )
        and not post_delete_recreation_reset_result.get(
            "recreate_command_executed"
        )
    )
    readback_routes_reset = bool(
        post_delete_recreation_reset_result.get("readback_routes_reset")
        and post_delete_recreation_reset_result.get(
            "previous_readback_evidence_invalidated"
        )
        and not post_delete_recreation_reset_result.get(
            "readback_command_dispatched"
        )
        and not post_delete_recreation_reset_result.get(
            "readback_command_executed"
        )
    )
    diagnostics_routes_reset = bool(
        post_delete_recreation_reset_result.get("diagnostics_routes_reset")
        and not post_delete_recreation_reset_result.get(
            "diagnostics_command_dispatched"
        )
        and not post_delete_recreation_reset_result.get(
            "diagnostics_command_executed"
        )
        and not post_delete_recreation_reset_result.get(
            "graph_repair_command_dispatched"
        )
        and not post_delete_recreation_reset_result.get(
            "graph_repair_command_executed"
        )
        and not post_delete_recreation_reset_result.get(
            "graph_layout_mutation_performed"
        )
        and not post_delete_recreation_reset_result.get(
            "node_position_write_performed"
        )
        and not post_delete_recreation_reset_result.get(
            "pin_connection_write_performed"
        )
    )
    post_delete_no_write_boundary_verified = bool(
        post_delete_recreation_reset_result.get("read_only_preflight")
        and post_delete_recreation_reset_result.get(
            "external_dirty_preserved"
        )
        and post_delete_recreation_reset_result.get("external_dirty_before")
        == post_delete_recreation_reset_result.get("external_dirty_after")
        and post_delete_recreation_reset_result.get("dirty_maps_before")
        == post_delete_recreation_reset_result.get("dirty_maps_after")
        and not post_delete_recreation_reset_result.get("compile_dispatched")
        and not post_delete_recreation_reset_result.get("compile_executed")
        and not post_delete_recreation_reset_result.get("save_dispatched")
        and not post_delete_recreation_reset_result.get("save_executed")
        and not post_delete_recreation_reset_result.get(
            "asset_write_performed"
        )
        and not post_delete_recreation_reset_result.get(
            "package_dirty_marked"
        )
        and not post_delete_recreation_reset_result.get("cleanup_allowed")
        and not post_delete_recreation_reset_result.get("cleanup_executed")
        and not post_delete_recreation_reset_result.get(
            "delete_asset_allowed"
        )
        and not post_delete_recreation_reset_result.get(
            "delete_asset_executed_output"
        )
        and not post_delete_recreation_reset_result.get(
            "rename_asset_allowed"
        )
        and not post_delete_recreation_reset_result.get(
            "rename_command_dispatched"
        )
        and not post_delete_recreation_reset_result.get(
            "rename_command_executed"
        )
        and not post_delete_recreation_reset_result.get("overwrite_allowed")
        and not post_delete_recreation_reset_result.get("overwrite_executed")
        and not post_delete_recreation_reset_result.get(
            "production_path_write_allowed"
        )
        and not post_delete_recreation_reset_result.get(
            "production_path_write_executed"
        )
    )
    result_has_no_error = bool(
        post_delete_recreation_reset_result.get("error") in (None, "")
    )
    post_delete_recreation_reset_passed = bool(
        post_delete_checkpoint_satisfied
        and result_schema_matches
        and deleted_target_absence_confirmed
        and recreation_plan_scoped
        and recreation_requires_explicit_checkpoint
        and readback_routes_reset
        and diagnostics_routes_reset
        and post_delete_no_write_boundary_verified
        and result_has_no_error
    )

    return {
        "id": "durable_executor_authoring_post_delete_recreation_reset_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_RESET_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_289_296_summary_schema_matches": (
            section_289_296_summary_schema_matches
        ),
        "section_289_296_summary_passed": section_289_296_summary_passed,
        "section_289_296_cleanup_delete_actual_ready": (
            upstream_cleanup_delete_ready
        ),
        "section_289_296_non_delete_outputs_closed": (
            upstream_non_delete_outputs_closed
        ),
        "result_schema_matches": result_schema_matches,
        "post_delete_checkpoint_satisfied": post_delete_checkpoint_satisfied,
        "deleted_target_absence_confirmed": (
            deleted_target_absence_confirmed
        ),
        "recreation_plan_scoped": recreation_plan_scoped,
        "recreation_requires_explicit_checkpoint": (
            recreation_requires_explicit_checkpoint
        ),
        "readback_routes_reset": readback_routes_reset,
        "diagnostics_routes_reset": diagnostics_routes_reset,
        "post_delete_no_write_boundary_verified": (
            post_delete_no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_297_post_delete_checkpoint_satisfied": (
            post_delete_recreation_reset_passed
        ),
        "section_298_deleted_target_absence_confirmed": (
            post_delete_recreation_reset_passed
        ),
        "section_299_recreation_plan_scoped": (
            post_delete_recreation_reset_passed
        ),
        "section_300_recreation_requires_explicit_checkpoint": (
            post_delete_recreation_reset_passed
        ),
        "section_301_readback_routes_reset": (
            post_delete_recreation_reset_passed
        ),
        "section_302_diagnostics_routes_reset": (
            post_delete_recreation_reset_passed
        ),
        "section_303_post_delete_no_write_boundary_verified": (
            post_delete_recreation_reset_passed
        ),
        "section_304_post_delete_reset_release_ready": (
            post_delete_recreation_reset_passed
        ),
        "post_delete_recreation_reset_ready": (
            post_delete_recreation_reset_passed
        ),
        "post_delete_target_absence_confirmed": (
            post_delete_recreation_reset_passed
        ),
        "post_delete_recreation_requires_checkpoint": (
            post_delete_recreation_reset_passed
        ),
        "final_durable_release_ready": post_delete_recreation_reset_passed,
        "recreate_asset_allowed": False,
        "recreate_command_dispatched": False,
        "recreate_command_executed": False,
        "readback_command_dispatched": False,
        "readback_command_executed": False,
        "diagnostics_command_dispatched": False,
        "diagnostics_command_executed": False,
        "graph_repair_command_dispatched": False,
        "graph_repair_command_executed": False,
        "graph_layout_mutation_performed": False,
        "node_position_write_performed": False,
        "pin_connection_write_performed": False,
        "actor_bp_authoring_compile_dispatched": False,
        "actor_bp_authoring_compile_executed": False,
        "actor_bp_authoring_save_dispatched": False,
        "actor_bp_authoring_save_executed": False,
        "actor_bp_authoring_asset_write_performed": False,
        "actor_bp_authoring_package_dirty_marked": False,
        "cleanup_allowed": False,
        "cleanup_executed": False,
        "delete_asset_allowed": False,
        "delete_asset_executed_output": False,
        "rename_asset_allowed": False,
        "rename_command_dispatched": False,
        "rename_command_executed": False,
        "overwrite_allowed": False,
        "overwrite_executed": False,
        "production_path_write_allowed": False,
        "production_path_write_executed": False,
        **{
            key: 1 if post_delete_recreation_reset_passed else 0
            for key in POST_DELETE_RECREATION_RESET_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_POST_DELETE_RECREATION_RESET_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_post_delete_recreation_reset_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "post_delete_recreation_reset_ready"
            )
            == len(requested)
            and _truthy_count(
                requested, "post_delete_target_absence_confirmed"
            )
            == len(requested)
            and _truthy_count(
                requested, "post_delete_recreation_requires_checkpoint"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_POST_DELETE_RECREATION_RESET_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_POST_DELETE_RECREATION_RESET_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_post_delete_recreation_reset_batch_count": (
            len(requested)
        ),
        "section_289_296_summary_schema_matches_count": _truthy_count(
            requested, "section_289_296_summary_schema_matches"
        ),
        "section_289_296_summary_passed_count": _truthy_count(
            requested, "section_289_296_summary_passed"
        ),
        "section_289_296_cleanup_delete_actual_ready_count": (
            _truthy_count(
                requested, "section_289_296_cleanup_delete_actual_ready"
            )
        ),
        "section_289_296_non_delete_outputs_closed_count": _truthy_count(
            requested, "section_289_296_non_delete_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "post_delete_checkpoint_satisfied_count": _truthy_count(
            requested, "post_delete_checkpoint_satisfied"
        ),
        "deleted_target_absence_confirmed_count": _truthy_count(
            requested, "deleted_target_absence_confirmed"
        ),
        "recreation_plan_scoped_count": _truthy_count(
            requested, "recreation_plan_scoped"
        ),
        "recreation_requires_explicit_checkpoint_count": _truthy_count(
            requested, "recreation_requires_explicit_checkpoint"
        ),
        "readback_routes_reset_count": _truthy_count(
            requested, "readback_routes_reset"
        ),
        "diagnostics_routes_reset_count": _truthy_count(
            requested, "diagnostics_routes_reset"
        ),
        "post_delete_no_write_boundary_verified_count": _truthy_count(
            requested, "post_delete_no_write_boundary_verified"
        ),
        "result_has_no_error_count": _truthy_count(
            requested, "result_has_no_error"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
    }
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in POST_DELETE_RECREATION_RESET_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_POST_DELETE_RECREATION_RESET_OUTPUT_COUNT_KEYS
        }
    )
    return summary
