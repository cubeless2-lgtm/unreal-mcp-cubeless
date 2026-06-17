#!/usr/bin/env python
"""
Sections 257-264 durable executor live Actor Blueprint authoring preflight.

This contract advances from Actor Blueprint expansion dry-run readiness into a
live-authoring checkpoint envelope. It proves the command envelope, read-only
target preflight, mutation sequence, compile/save ordering, rollback boundary,
and readback evidence plan are ready while actual Blueprint mutation, compile,
save, delete, rename, overwrite, and production writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract as actor_bp_expansion


DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_BATCH_SCHEMA = (
    "section_257_264_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_BATCH_SUMMARY_SCHEMA = (
    "section_257_264_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_summary_v1"
)
LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_RESULT_SCHEMA = (
    "section_257_264_live_actor_bp_authoring_preflight_result_v1"
)
SECTION_249_256_ACTOR_BP_EXPANSION_DRY_RUN_SUMMARY_SCHEMA = (
    actor_bp_expansion
    .DURABLE_EXECUTOR_AUTHORING_ACTOR_BP_EXPANSION_DRY_RUN_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = actor_bp_expansion.DEFAULT_TARGET_ASSET_PATH
DEFAULT_TARGET_DIRECTORY = actor_bp_expansion.DEFAULT_TARGET_DIRECTORY
DEFAULT_PARENT_CLASS = actor_bp_expansion.DEFAULT_PARENT_CLASS
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_actor_bp_expansion_dry_run_batch_count",
    "section_249_actor_blueprint_scope_confirmed_count",
    "section_250_variable_authoring_plan_accepted_count",
    "section_251_component_authoring_plan_accepted_count",
    "section_252_default_authoring_plan_accepted_count",
    "section_253_compile_save_dependency_declared_count",
    "section_254_temp_package_mutation_boundary_clean_count",
    "section_255_actor_authoring_readback_dry_run_ready_count",
    "section_256_actual_actor_authoring_requires_final_user_checkpoint_count",
    "actor_bp_expansion_dry_run_allowed_count",
    "actor_bp_expansion_dry_run_ready_count",
    "actual_actor_bp_authoring_requires_final_user_checkpoint_count",
    "final_durable_release_ready_count",
)
UPSTREAM_MUTATION_MUST_BE_CLOSED_COUNT_KEYS = (
    "variable_add_command_dispatched_count",
    "variable_add_command_executed_count",
    "component_add_command_dispatched_count",
    "component_add_command_executed_count",
    "default_write_command_dispatched_count",
    "default_write_command_executed_count",
    "actor_bp_authoring_command_dispatched_count",
    "actor_bp_authoring_command_executed_count",
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
    "production_path_write_allowed_count",
    "production_path_write_executed_count",
)
LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_PATH_COUNT_KEYS = (
    "section_257_live_actor_bp_command_envelope_scoped_count",
    "section_258_live_actor_bp_read_only_target_preflight_ready_count",
    "section_259_live_actor_bp_mutation_sequence_planned_count",
    "section_260_live_actor_bp_compile_save_ordering_verified_count",
    "section_261_live_actor_bp_rollback_boundary_revalidated_count",
    "section_262_live_actor_bp_readback_evidence_plan_ready_count",
    "section_263_live_actor_bp_final_checkpoint_required_count",
    "section_264_live_actor_bp_actual_authoring_closed_count",
    "live_actor_bp_authoring_preflight_allowed_count",
    "live_actor_bp_authoring_checkpoint_ready_count",
    "actual_live_actor_bp_authoring_requires_final_user_checkpoint_count",
)
BLOCKED_LIVE_ACTOR_BP_AUTHORING_OUTPUT_COUNT_KEYS = (
    "variable_add_command_dispatched_count",
    "variable_add_command_executed_count",
    "component_add_command_dispatched_count",
    "component_add_command_executed_count",
    "default_write_command_dispatched_count",
    "default_write_command_executed_count",
    "actor_bp_authoring_command_dispatched_count",
    "actor_bp_authoring_command_executed_count",
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


def build_live_actor_bp_authoring_preflight_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_directory: str = DEFAULT_TARGET_DIRECTORY,
    parent_class: str = DEFAULT_PARENT_CLASS,
    target_under_temp_root: bool = True,
    command_envelope_built: bool = True,
    command_envelope_scoped_to_target: bool = True,
    read_only_target_load_ready: bool = True,
    read_only_existing_member_scan_ready: bool = True,
    variable_mutation_step_planned: bool = True,
    component_mutation_step_planned: bool = True,
    default_value_mutation_step_planned: bool = True,
    compile_before_save_order_declared: bool = True,
    save_after_successful_compile_declared: bool = True,
    rollback_boundary_revalidated: bool = True,
    cleanup_delete_rename_still_closed: bool = True,
    readback_evidence_plan_ready: bool = True,
    final_user_checkpoint_required: bool = True,
    dirty_content_package_count: int = 0,
    dirty_map_package_count: int = 0,
    variable_add_command_dispatched: bool = False,
    variable_add_command_executed: bool = False,
    component_add_command_dispatched: bool = False,
    component_add_command_executed: bool = False,
    default_write_command_dispatched: bool = False,
    default_write_command_executed: bool = False,
    actor_bp_authoring_command_dispatched: bool = False,
    actor_bp_authoring_command_executed: bool = False,
    actor_bp_authoring_compile_dispatched: bool = False,
    actor_bp_authoring_compile_executed: bool = False,
    actor_bp_authoring_save_dispatched: bool = False,
    actor_bp_authoring_save_executed: bool = False,
    actor_bp_authoring_asset_write_performed: bool = False,
    actor_bp_authoring_package_dirty_marked: bool = False,
    cleanup_allowed: bool = False,
    cleanup_executed: bool = False,
    delete_asset_allowed: bool = False,
    rename_asset_allowed: bool = False,
    production_path_write_allowed: bool = False,
    production_path_write_executed: bool = False,
    error: str | None = None,
) -> Dict[str, Any]:
    return {
        "schema": LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_directory": target_directory,
        "parent_class": parent_class,
        "target_under_temp_root": target_under_temp_root,
        "command_envelope_built": command_envelope_built,
        "command_envelope_scoped_to_target": command_envelope_scoped_to_target,
        "read_only_target_load_ready": read_only_target_load_ready,
        "read_only_existing_member_scan_ready": (
            read_only_existing_member_scan_ready
        ),
        "variable_mutation_step_planned": variable_mutation_step_planned,
        "component_mutation_step_planned": component_mutation_step_planned,
        "default_value_mutation_step_planned": default_value_mutation_step_planned,
        "compile_before_save_order_declared": compile_before_save_order_declared,
        "save_after_successful_compile_declared": (
            save_after_successful_compile_declared
        ),
        "rollback_boundary_revalidated": rollback_boundary_revalidated,
        "cleanup_delete_rename_still_closed": cleanup_delete_rename_still_closed,
        "readback_evidence_plan_ready": readback_evidence_plan_ready,
        "final_user_checkpoint_required": final_user_checkpoint_required,
        "dirty_content_package_count": dirty_content_package_count,
        "dirty_map_package_count": dirty_map_package_count,
        "variable_add_command_dispatched": variable_add_command_dispatched,
        "variable_add_command_executed": variable_add_command_executed,
        "component_add_command_dispatched": component_add_command_dispatched,
        "component_add_command_executed": component_add_command_executed,
        "default_write_command_dispatched": default_write_command_dispatched,
        "default_write_command_executed": default_write_command_executed,
        "actor_bp_authoring_command_dispatched": (
            actor_bp_authoring_command_dispatched
        ),
        "actor_bp_authoring_command_executed": actor_bp_authoring_command_executed,
        "actor_bp_authoring_compile_dispatched": (
            actor_bp_authoring_compile_dispatched
        ),
        "actor_bp_authoring_compile_executed": actor_bp_authoring_compile_executed,
        "actor_bp_authoring_save_dispatched": actor_bp_authoring_save_dispatched,
        "actor_bp_authoring_save_executed": actor_bp_authoring_save_executed,
        "actor_bp_authoring_asset_write_performed": (
            actor_bp_authoring_asset_write_performed
        ),
        "actor_bp_authoring_package_dirty_marked": (
            actor_bp_authoring_package_dirty_marked
        ),
        "cleanup_allowed": cleanup_allowed,
        "cleanup_executed": cleanup_executed,
        "delete_asset_allowed": delete_asset_allowed,
        "rename_asset_allowed": rename_asset_allowed,
        "production_path_write_allowed": production_path_write_allowed,
        "production_path_write_executed": production_path_write_executed,
        "error": error,
    }


def build_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract(
    requested: bool,
    section_249_256_actor_bp_expansion_dry_run_summary: Dict[str, Any],
    live_actor_bp_authoring_preflight_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_249_256_summary_schema_matches = bool(
        section_249_256_actor_bp_expansion_dry_run_summary.get("schema")
        == SECTION_249_256_ACTOR_BP_EXPANSION_DRY_RUN_SUMMARY_SCHEMA
    )
    section_249_256_summary_passed = bool(
        section_249_256_actor_bp_expansion_dry_run_summary.get("status")
        == "passed"
    )
    upstream_actor_bp_expansion_dry_run_ready = all(
        _count_is_one(section_249_256_actor_bp_expansion_dry_run_summary, key)
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_actor_bp_mutation_outputs_closed = all(
        _count_is_zero(section_249_256_actor_bp_expansion_dry_run_summary, key)
        for key in UPSTREAM_MUTATION_MUST_BE_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        live_actor_bp_authoring_preflight_result.get("schema")
        == LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_RESULT_SCHEMA
    )
    live_actor_bp_command_envelope_scoped = bool(
        live_actor_bp_authoring_preflight_result.get("target_asset_path")
        == DEFAULT_TARGET_ASSET_PATH
        and live_actor_bp_authoring_preflight_result.get("target_directory")
        == DEFAULT_TARGET_DIRECTORY
        and live_actor_bp_authoring_preflight_result.get("parent_class")
        == DEFAULT_PARENT_CLASS
        and live_actor_bp_authoring_preflight_result.get("target_under_temp_root")
        and live_actor_bp_authoring_preflight_result.get("command_envelope_built")
        and live_actor_bp_authoring_preflight_result.get(
            "command_envelope_scoped_to_target"
        )
    )
    live_actor_bp_read_only_target_preflight_ready = bool(
        live_actor_bp_command_envelope_scoped
        and live_actor_bp_authoring_preflight_result.get(
            "read_only_target_load_ready"
        )
        and live_actor_bp_authoring_preflight_result.get(
            "read_only_existing_member_scan_ready"
        )
    )
    live_actor_bp_mutation_sequence_planned = bool(
        live_actor_bp_authoring_preflight_result.get(
            "variable_mutation_step_planned"
        )
        and live_actor_bp_authoring_preflight_result.get(
            "component_mutation_step_planned"
        )
        and live_actor_bp_authoring_preflight_result.get(
            "default_value_mutation_step_planned"
        )
    )
    live_actor_bp_compile_save_ordering_verified = bool(
        live_actor_bp_authoring_preflight_result.get(
            "compile_before_save_order_declared"
        )
        and live_actor_bp_authoring_preflight_result.get(
            "save_after_successful_compile_declared"
        )
    )
    live_actor_bp_rollback_boundary_revalidated = bool(
        live_actor_bp_authoring_preflight_result.get(
            "rollback_boundary_revalidated"
        )
        and live_actor_bp_authoring_preflight_result.get(
            "cleanup_delete_rename_still_closed"
        )
        and int(
            live_actor_bp_authoring_preflight_result.get(
                "dirty_content_package_count", -1
            )
        )
        == 0
        and int(
            live_actor_bp_authoring_preflight_result.get(
                "dirty_map_package_count", -1
            )
        )
        == 0
    )
    live_actor_bp_readback_evidence_plan_ready = bool(
        live_actor_bp_authoring_preflight_result.get(
            "readback_evidence_plan_ready"
        )
    )
    live_actor_bp_final_checkpoint_required = bool(
        live_actor_bp_authoring_preflight_result.get(
            "final_user_checkpoint_required"
        )
    )
    dry_run_blocks_actual_live_actor_authoring_outputs = bool(
        not live_actor_bp_authoring_preflight_result.get(
            "variable_add_command_dispatched"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "variable_add_command_executed"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "component_add_command_dispatched"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "component_add_command_executed"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "default_write_command_dispatched"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "default_write_command_executed"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "actor_bp_authoring_command_dispatched"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "actor_bp_authoring_command_executed"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "actor_bp_authoring_compile_dispatched"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "actor_bp_authoring_compile_executed"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "actor_bp_authoring_save_dispatched"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "actor_bp_authoring_save_executed"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "actor_bp_authoring_asset_write_performed"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "actor_bp_authoring_package_dirty_marked"
        )
        and not live_actor_bp_authoring_preflight_result.get("cleanup_allowed")
        and not live_actor_bp_authoring_preflight_result.get("cleanup_executed")
        and not live_actor_bp_authoring_preflight_result.get(
            "delete_asset_allowed"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "rename_asset_allowed"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "production_path_write_allowed"
        )
        and not live_actor_bp_authoring_preflight_result.get(
            "production_path_write_executed"
        )
    )
    result_has_no_error = bool(
        live_actor_bp_authoring_preflight_result.get("error") in (None, "")
    )
    live_actor_bp_authoring_checkpoint_ready = bool(
        requested
        and section_249_256_summary_schema_matches
        and section_249_256_summary_passed
        and upstream_actor_bp_expansion_dry_run_ready
        and upstream_actor_bp_mutation_outputs_closed
        and result_schema_matches
        and live_actor_bp_command_envelope_scoped
        and live_actor_bp_read_only_target_preflight_ready
        and live_actor_bp_mutation_sequence_planned
        and live_actor_bp_compile_save_ordering_verified
        and live_actor_bp_rollback_boundary_revalidated
        and live_actor_bp_readback_evidence_plan_ready
        and live_actor_bp_final_checkpoint_required
        and dry_run_blocks_actual_live_actor_authoring_outputs
        and result_has_no_error
    )
    actual_live_actor_bp_authoring_requires_final_user_checkpoint = (
        live_actor_bp_authoring_checkpoint_ready
    )

    return {
        "id": "durable_executor_authoring_live_actor_bp_authoring_preflight_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_249_256_summary_schema_matches": (
            section_249_256_summary_schema_matches
        ),
        "section_249_256_summary_passed": section_249_256_summary_passed,
        "section_249_256_actor_bp_expansion_dry_run_ready": (
            upstream_actor_bp_expansion_dry_run_ready
        ),
        "section_249_256_actor_bp_mutation_outputs_closed": (
            upstream_actor_bp_mutation_outputs_closed
        ),
        "result_schema_matches": result_schema_matches,
        "live_actor_bp_command_envelope_scoped": (
            live_actor_bp_command_envelope_scoped
        ),
        "live_actor_bp_read_only_target_preflight_ready": (
            live_actor_bp_read_only_target_preflight_ready
        ),
        "live_actor_bp_mutation_sequence_planned": (
            live_actor_bp_mutation_sequence_planned
        ),
        "live_actor_bp_compile_save_ordering_verified": (
            live_actor_bp_compile_save_ordering_verified
        ),
        "live_actor_bp_rollback_boundary_revalidated": (
            live_actor_bp_rollback_boundary_revalidated
        ),
        "live_actor_bp_readback_evidence_plan_ready": (
            live_actor_bp_readback_evidence_plan_ready
        ),
        "live_actor_bp_final_checkpoint_required": (
            live_actor_bp_final_checkpoint_required
        ),
        "dry_run_blocks_actual_live_actor_authoring_outputs": (
            dry_run_blocks_actual_live_actor_authoring_outputs
        ),
        "result_has_no_error": result_has_no_error,
        "live_actor_bp_authoring_checkpoint_ready": (
            live_actor_bp_authoring_checkpoint_ready
        ),
        "actual_live_actor_bp_authoring_requires_final_user_checkpoint": (
            actual_live_actor_bp_authoring_requires_final_user_checkpoint
        ),
        "section_257_live_actor_bp_command_envelope_scoped": (
            live_actor_bp_authoring_checkpoint_ready
        ),
        "section_258_live_actor_bp_read_only_target_preflight_ready": (
            live_actor_bp_authoring_checkpoint_ready
        ),
        "section_259_live_actor_bp_mutation_sequence_planned": (
            live_actor_bp_authoring_checkpoint_ready
        ),
        "section_260_live_actor_bp_compile_save_ordering_verified": (
            live_actor_bp_authoring_checkpoint_ready
        ),
        "section_261_live_actor_bp_rollback_boundary_revalidated": (
            live_actor_bp_authoring_checkpoint_ready
        ),
        "section_262_live_actor_bp_readback_evidence_plan_ready": (
            live_actor_bp_authoring_checkpoint_ready
        ),
        "section_263_live_actor_bp_final_checkpoint_required": (
            actual_live_actor_bp_authoring_requires_final_user_checkpoint
        ),
        "section_264_live_actor_bp_actual_authoring_closed": (
            live_actor_bp_authoring_checkpoint_ready
        ),
        "final_durable_release_ready": live_actor_bp_authoring_checkpoint_ready,
        "actor_bp_expansion_dry_run_ready": (
            live_actor_bp_authoring_checkpoint_ready
        ),
        "live_actor_bp_authoring_preflight_allowed": (
            live_actor_bp_authoring_checkpoint_ready
        ),
        "live_actor_bp_authoring_checkpoint_ready": (
            live_actor_bp_authoring_checkpoint_ready
        ),
        "variable_add_command_dispatched": False,
        "variable_add_command_executed": False,
        "component_add_command_dispatched": False,
        "component_add_command_executed": False,
        "default_write_command_dispatched": False,
        "default_write_command_executed": False,
        "actor_bp_authoring_command_dispatched": False,
        "actor_bp_authoring_command_executed": False,
        "actor_bp_authoring_compile_dispatched": False,
        "actor_bp_authoring_compile_executed": False,
        "actor_bp_authoring_save_dispatched": False,
        "actor_bp_authoring_save_executed": False,
        "actor_bp_authoring_asset_write_performed": False,
        "actor_bp_authoring_package_dirty_marked": False,
        "cleanup_allowed": False,
        "cleanup_executed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        "production_path_write_allowed": False,
        "production_path_write_executed": False,
        **{
            key: 1 if live_actor_bp_authoring_checkpoint_ready else 0
            for key in LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_PATH_COUNT_KEYS
        },
        **{key: 0 for key in BLOCKED_LIVE_ACTOR_BP_AUTHORING_OUTPUT_COUNT_KEYS},
    }


def summarize_durable_executor_authoring_live_actor_bp_authoring_preflight_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "live_actor_bp_authoring_checkpoint_ready"
            )
            == len(requested)
            and _truthy_count(
                requested,
                "actual_live_actor_bp_authoring_requires_final_user_checkpoint",
            )
            == len(requested)
            and _truthy_count(
                requested, "actor_bp_authoring_command_dispatched"
            )
            == 0
            and _truthy_count(requested, "actor_bp_authoring_command_executed")
            == 0
            and _truthy_count(
                requested, "actor_bp_authoring_asset_write_performed"
            )
            == 0
            and _truthy_count(
                requested, "actor_bp_authoring_package_dirty_marked"
            )
            == 0
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_LIVE_ACTOR_BP_AUTHORING_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_live_actor_bp_authoring_preflight_batch_count": (
            len(requested)
        ),
        "section_249_256_summary_schema_matches_count": _truthy_count(
            requested, "section_249_256_summary_schema_matches"
        ),
        "section_249_256_summary_passed_count": _truthy_count(
            requested, "section_249_256_summary_passed"
        ),
        "section_249_256_actor_bp_expansion_dry_run_ready_count": (
            _truthy_count(
                requested,
                "section_249_256_actor_bp_expansion_dry_run_ready",
            )
        ),
        "section_249_256_actor_bp_mutation_outputs_closed_count": (
            _truthy_count(
                requested,
                "section_249_256_actor_bp_mutation_outputs_closed",
            )
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "live_actor_bp_command_envelope_scoped_count": _truthy_count(
            requested, "live_actor_bp_command_envelope_scoped"
        ),
        "live_actor_bp_read_only_target_preflight_ready_count": _truthy_count(
            requested, "live_actor_bp_read_only_target_preflight_ready"
        ),
        "live_actor_bp_mutation_sequence_planned_count": _truthy_count(
            requested, "live_actor_bp_mutation_sequence_planned"
        ),
        "live_actor_bp_compile_save_ordering_verified_count": _truthy_count(
            requested, "live_actor_bp_compile_save_ordering_verified"
        ),
        "live_actor_bp_rollback_boundary_revalidated_count": _truthy_count(
            requested, "live_actor_bp_rollback_boundary_revalidated"
        ),
        "live_actor_bp_readback_evidence_plan_ready_count": _truthy_count(
            requested, "live_actor_bp_readback_evidence_plan_ready"
        ),
        "live_actor_bp_final_checkpoint_required_count": _truthy_count(
            requested, "live_actor_bp_final_checkpoint_required"
        ),
        "dry_run_blocks_actual_live_actor_authoring_outputs_count": (
            _truthy_count(
                requested,
                "dry_run_blocks_actual_live_actor_authoring_outputs",
            )
        ),
        "result_has_no_error_count": _truthy_count(
            requested, "result_has_no_error"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "actor_bp_expansion_dry_run_ready_count": _truthy_count(
            requested, "actor_bp_expansion_dry_run_ready"
        ),
        "live_actor_bp_authoring_preflight_allowed_count": _truthy_count(
            requested, "live_actor_bp_authoring_preflight_allowed"
        ),
        "live_actor_bp_authoring_checkpoint_ready_count": _truthy_count(
            requested, "live_actor_bp_authoring_checkpoint_ready"
        ),
        "actual_live_actor_bp_authoring_requires_final_user_checkpoint_count": (
            _truthy_count(
                requested,
                "actual_live_actor_bp_authoring_requires_final_user_checkpoint",
            )
        ),
        "variable_add_command_dispatched_count": _truthy_count(
            requested, "variable_add_command_dispatched"
        ),
        "variable_add_command_executed_count": _truthy_count(
            requested, "variable_add_command_executed"
        ),
        "component_add_command_dispatched_count": _truthy_count(
            requested, "component_add_command_dispatched"
        ),
        "component_add_command_executed_count": _truthy_count(
            requested, "component_add_command_executed"
        ),
        "default_write_command_dispatched_count": _truthy_count(
            requested, "default_write_command_dispatched"
        ),
        "default_write_command_executed_count": _truthy_count(
            requested, "default_write_command_executed"
        ),
        "actor_bp_authoring_command_dispatched_count": _truthy_count(
            requested, "actor_bp_authoring_command_dispatched"
        ),
        "actor_bp_authoring_command_executed_count": _truthy_count(
            requested, "actor_bp_authoring_command_executed"
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
        "cleanup_allowed_count": _truthy_count(requested, "cleanup_allowed"),
        "cleanup_executed_count": _truthy_count(requested, "cleanup_executed"),
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
            for key in LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_LIVE_ACTOR_BP_AUTHORING_OUTPUT_COUNT_KEYS
        }
    )
    return summary
