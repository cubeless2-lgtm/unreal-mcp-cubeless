#!/usr/bin/env python
"""
Sections 249-256 durable executor actor Blueprint expansion dry-run batch.

This contract opens only a dry-run gate for Actor Blueprint variable,
component, and default-value authoring. It requires the Section 241-248
rename/overwrite dry-run boundary, keeps the target under /Game/_MCP_Temp, and
keeps actual Blueprint mutation, compile, save, delete, rename, overwrite, and
production writes closed until a final user checkpoint.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_rename_overwrite_dry_run_batch_contract as rename_overwrite_dry_run


DURABLE_EXECUTOR_AUTHORING_ACTOR_BP_EXPANSION_DRY_RUN_BATCH_SCHEMA = (
    "section_249_256_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_ACTOR_BP_EXPANSION_DRY_RUN_BATCH_SUMMARY_SCHEMA = (
    "section_249_256_durable_executor_authoring_actor_bp_expansion_dry_run_batch_summary_v1"
)
ACTOR_BP_EXPANSION_DRY_RUN_RESULT_SCHEMA = (
    "section_249_256_actor_bp_expansion_dry_run_result_v1"
)
SECTION_241_248_RENAME_OVERWRITE_DRY_RUN_SUMMARY_SCHEMA = (
    rename_overwrite_dry_run
    .DURABLE_EXECUTOR_AUTHORING_RENAME_OVERWRITE_DRY_RUN_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = rename_overwrite_dry_run.DEFAULT_SOURCE_ASSET_PATH
DEFAULT_TARGET_DIRECTORY = rename_overwrite_dry_run.DEFAULT_SOURCE_DIRECTORY
DEFAULT_PARENT_CLASS = "/Script/Engine.Actor"
DEFAULT_VARIABLE_SPEC = {
    "name": "MCPAuthoringScalar",
    "type": "float",
    "default": 1.0,
    "editable": True,
    "category": "MCPAuthoring",
}
DEFAULT_COMPONENT_SPEC = {
    "name": "MCPPreviewSceneRoot",
    "component_class": "SceneComponent",
    "attach_to": "DefaultSceneRoot",
    "creation_method": "SimpleConstructionScript",
}
DEFAULT_DEFAULT_VALUE_SPEC = {
    "target": "ClassDefaultObject",
    "property_name": "Tags",
    "value": ["MCP_DurableAuthoring_DryRun"],
}
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_rename_overwrite_dry_run_batch_count",
    "section_241_rename_source_scope_confirmed_count",
    "section_242_rename_destination_scope_confirmed_count",
    "section_243_overwrite_policy_denies_existing_destination_count",
    "section_244_rename_overwrite_dry_run_plan_accepted_count",
    "section_245_rename_collision_boundary_clean_count",
    "section_246_rename_dirty_package_boundary_clean_count",
    "section_247_rename_result_readback_dry_run_ready_count",
    "section_248_actual_rename_overwrite_requires_final_user_checkpoint_count",
    "rename_overwrite_dry_run_allowed_count",
    "rename_overwrite_dry_run_ready_count",
    "actual_rename_overwrite_requires_final_user_checkpoint_count",
    "final_durable_release_ready_count",
)
UPSTREAM_DESTRUCTIVE_MUST_BE_CLOSED_COUNT_KEYS = (
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
ACTOR_BP_EXPANSION_DRY_RUN_PATH_COUNT_KEYS = (
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
)
BLOCKED_ACTOR_BP_AUTHORING_OUTPUT_COUNT_KEYS = (
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


def build_actor_bp_expansion_dry_run_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_directory: str = DEFAULT_TARGET_DIRECTORY,
    parent_class: str = DEFAULT_PARENT_CLASS,
    target_under_temp_root: bool = True,
    blueprint_load_succeeded: bool = True,
    blueprint_class_is_actor: bool = True,
    variable_plan_built: bool = True,
    variable_spec_valid: bool = True,
    component_plan_built: bool = True,
    component_spec_valid: bool = True,
    default_value_plan_built: bool = True,
    default_value_spec_valid: bool = True,
    compile_after_mutation_required: bool = True,
    save_after_compile_required: bool = True,
    readback_plan_ready: bool = True,
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
        "schema": ACTOR_BP_EXPANSION_DRY_RUN_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_directory": target_directory,
        "parent_class": parent_class,
        "target_under_temp_root": target_under_temp_root,
        "blueprint_load_succeeded": blueprint_load_succeeded,
        "blueprint_class_is_actor": blueprint_class_is_actor,
        "variable_spec": dict(DEFAULT_VARIABLE_SPEC),
        "component_spec": dict(DEFAULT_COMPONENT_SPEC),
        "default_value_spec": dict(DEFAULT_DEFAULT_VALUE_SPEC),
        "variable_plan_built": variable_plan_built,
        "variable_spec_valid": variable_spec_valid,
        "component_plan_built": component_plan_built,
        "component_spec_valid": component_spec_valid,
        "default_value_plan_built": default_value_plan_built,
        "default_value_spec_valid": default_value_spec_valid,
        "compile_after_mutation_required": compile_after_mutation_required,
        "save_after_compile_required": save_after_compile_required,
        "readback_plan_ready": readback_plan_ready,
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


def build_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract(
    requested: bool,
    section_241_248_rename_overwrite_dry_run_summary: Dict[str, Any],
    actor_bp_expansion_dry_run_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_241_248_summary_schema_matches = bool(
        section_241_248_rename_overwrite_dry_run_summary.get("schema")
        == SECTION_241_248_RENAME_OVERWRITE_DRY_RUN_SUMMARY_SCHEMA
    )
    section_241_248_summary_passed = bool(
        section_241_248_rename_overwrite_dry_run_summary.get("status")
        == "passed"
    )
    upstream_rename_overwrite_dry_run_ready = all(
        _count_is_one(section_241_248_rename_overwrite_dry_run_summary, key)
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_destructive_outputs_closed = all(
        _count_is_zero(section_241_248_rename_overwrite_dry_run_summary, key)
        for key in UPSTREAM_DESTRUCTIVE_MUST_BE_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        actor_bp_expansion_dry_run_result.get("schema")
        == ACTOR_BP_EXPANSION_DRY_RUN_RESULT_SCHEMA
    )
    actor_blueprint_scope_confirmed = bool(
        actor_bp_expansion_dry_run_result.get("target_asset_path")
        == DEFAULT_TARGET_ASSET_PATH
        and actor_bp_expansion_dry_run_result.get("target_directory")
        == DEFAULT_TARGET_DIRECTORY
        and actor_bp_expansion_dry_run_result.get("parent_class")
        == DEFAULT_PARENT_CLASS
        and actor_bp_expansion_dry_run_result.get("target_under_temp_root")
        and actor_bp_expansion_dry_run_result.get("blueprint_load_succeeded")
        and actor_bp_expansion_dry_run_result.get("blueprint_class_is_actor")
    )
    variable_authoring_plan_accepted = bool(
        actor_bp_expansion_dry_run_result.get("variable_plan_built")
        and actor_bp_expansion_dry_run_result.get("variable_spec_valid")
    )
    component_authoring_plan_accepted = bool(
        actor_bp_expansion_dry_run_result.get("component_plan_built")
        and actor_bp_expansion_dry_run_result.get("component_spec_valid")
    )
    default_authoring_plan_accepted = bool(
        actor_bp_expansion_dry_run_result.get("default_value_plan_built")
        and actor_bp_expansion_dry_run_result.get("default_value_spec_valid")
    )
    compile_save_dependency_declared = bool(
        actor_bp_expansion_dry_run_result.get("compile_after_mutation_required")
        and actor_bp_expansion_dry_run_result.get("save_after_compile_required")
    )
    temp_package_mutation_boundary_clean = bool(
        actor_blueprint_scope_confirmed
        and int(
            actor_bp_expansion_dry_run_result.get(
                "dirty_content_package_count", -1
            )
        )
        == 0
        and int(
            actor_bp_expansion_dry_run_result.get("dirty_map_package_count", -1)
        )
        == 0
    )
    actor_authoring_readback_dry_run_ready = bool(
        actor_bp_expansion_dry_run_result.get("readback_plan_ready")
        and variable_authoring_plan_accepted
        and component_authoring_plan_accepted
        and default_authoring_plan_accepted
    )
    dry_run_blocks_actual_actor_authoring_outputs = bool(
        not actor_bp_expansion_dry_run_result.get(
            "variable_add_command_dispatched"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "variable_add_command_executed"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "component_add_command_dispatched"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "component_add_command_executed"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "default_write_command_dispatched"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "default_write_command_executed"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "actor_bp_authoring_command_dispatched"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "actor_bp_authoring_command_executed"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "actor_bp_authoring_compile_dispatched"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "actor_bp_authoring_compile_executed"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "actor_bp_authoring_save_dispatched"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "actor_bp_authoring_save_executed"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "actor_bp_authoring_asset_write_performed"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "actor_bp_authoring_package_dirty_marked"
        )
        and not actor_bp_expansion_dry_run_result.get("cleanup_allowed")
        and not actor_bp_expansion_dry_run_result.get("cleanup_executed")
        and not actor_bp_expansion_dry_run_result.get("delete_asset_allowed")
        and not actor_bp_expansion_dry_run_result.get("rename_asset_allowed")
        and not actor_bp_expansion_dry_run_result.get(
            "production_path_write_allowed"
        )
        and not actor_bp_expansion_dry_run_result.get(
            "production_path_write_executed"
        )
    )
    result_has_no_error = bool(
        actor_bp_expansion_dry_run_result.get("error") in (None, "")
    )
    actor_bp_expansion_dry_run_ready = bool(
        requested
        and section_241_248_summary_schema_matches
        and section_241_248_summary_passed
        and upstream_rename_overwrite_dry_run_ready
        and upstream_destructive_outputs_closed
        and result_schema_matches
        and actor_blueprint_scope_confirmed
        and variable_authoring_plan_accepted
        and component_authoring_plan_accepted
        and default_authoring_plan_accepted
        and compile_save_dependency_declared
        and temp_package_mutation_boundary_clean
        and actor_authoring_readback_dry_run_ready
        and dry_run_blocks_actual_actor_authoring_outputs
        and result_has_no_error
    )
    actual_actor_bp_authoring_requires_final_user_checkpoint = (
        actor_bp_expansion_dry_run_ready
    )

    return {
        "id": "durable_executor_authoring_actor_bp_expansion_dry_run_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_ACTOR_BP_EXPANSION_DRY_RUN_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_241_248_summary_schema_matches": (
            section_241_248_summary_schema_matches
        ),
        "section_241_248_summary_passed": section_241_248_summary_passed,
        "section_241_248_rename_overwrite_dry_run_ready": (
            upstream_rename_overwrite_dry_run_ready
        ),
        "section_241_248_destructive_outputs_closed": (
            upstream_destructive_outputs_closed
        ),
        "result_schema_matches": result_schema_matches,
        "actor_blueprint_scope_confirmed": actor_blueprint_scope_confirmed,
        "variable_authoring_plan_accepted": variable_authoring_plan_accepted,
        "component_authoring_plan_accepted": component_authoring_plan_accepted,
        "default_authoring_plan_accepted": default_authoring_plan_accepted,
        "compile_save_dependency_declared": compile_save_dependency_declared,
        "temp_package_mutation_boundary_clean": (
            temp_package_mutation_boundary_clean
        ),
        "actor_authoring_readback_dry_run_ready": (
            actor_authoring_readback_dry_run_ready
        ),
        "dry_run_blocks_actual_actor_authoring_outputs": (
            dry_run_blocks_actual_actor_authoring_outputs
        ),
        "result_has_no_error": result_has_no_error,
        "actor_bp_expansion_dry_run_ready": actor_bp_expansion_dry_run_ready,
        "actual_actor_bp_authoring_requires_final_user_checkpoint": (
            actual_actor_bp_authoring_requires_final_user_checkpoint
        ),
        "section_249_actor_blueprint_scope_confirmed": (
            actor_bp_expansion_dry_run_ready
        ),
        "section_250_variable_authoring_plan_accepted": (
            actor_bp_expansion_dry_run_ready
        ),
        "section_251_component_authoring_plan_accepted": (
            actor_bp_expansion_dry_run_ready
        ),
        "section_252_default_authoring_plan_accepted": (
            actor_bp_expansion_dry_run_ready
        ),
        "section_253_compile_save_dependency_declared": (
            actor_bp_expansion_dry_run_ready
        ),
        "section_254_temp_package_mutation_boundary_clean": (
            actor_bp_expansion_dry_run_ready
        ),
        "section_255_actor_authoring_readback_dry_run_ready": (
            actor_bp_expansion_dry_run_ready
        ),
        "section_256_actual_actor_authoring_requires_final_user_checkpoint": (
            actual_actor_bp_authoring_requires_final_user_checkpoint
        ),
        "final_durable_release_ready": actor_bp_expansion_dry_run_ready,
        "rename_overwrite_dry_run_ready": actor_bp_expansion_dry_run_ready,
        "actor_bp_expansion_dry_run_allowed": actor_bp_expansion_dry_run_ready,
        "actor_bp_expansion_dry_run_ready": actor_bp_expansion_dry_run_ready,
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
            key: 1 if actor_bp_expansion_dry_run_ready else 0
            for key in ACTOR_BP_EXPANSION_DRY_RUN_PATH_COUNT_KEYS
        },
        **{key: 0 for key in BLOCKED_ACTOR_BP_AUTHORING_OUTPUT_COUNT_KEYS},
    }


def summarize_durable_executor_authoring_actor_bp_expansion_dry_run_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "actor_bp_expansion_dry_run_ready")
            == len(requested)
            and _truthy_count(
                requested,
                "actual_actor_bp_authoring_requires_final_user_checkpoint",
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
                for key in BLOCKED_ACTOR_BP_AUTHORING_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_ACTOR_BP_EXPANSION_DRY_RUN_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_actor_bp_expansion_dry_run_batch_count": (
            len(requested)
        ),
        "section_241_248_summary_schema_matches_count": _truthy_count(
            requested, "section_241_248_summary_schema_matches"
        ),
        "section_241_248_summary_passed_count": _truthy_count(
            requested, "section_241_248_summary_passed"
        ),
        "section_241_248_rename_overwrite_dry_run_ready_count": _truthy_count(
            requested, "section_241_248_rename_overwrite_dry_run_ready"
        ),
        "section_241_248_destructive_outputs_closed_count": _truthy_count(
            requested, "section_241_248_destructive_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "actor_blueprint_scope_confirmed_count": _truthy_count(
            requested, "actor_blueprint_scope_confirmed"
        ),
        "variable_authoring_plan_accepted_count": _truthy_count(
            requested, "variable_authoring_plan_accepted"
        ),
        "component_authoring_plan_accepted_count": _truthy_count(
            requested, "component_authoring_plan_accepted"
        ),
        "default_authoring_plan_accepted_count": _truthy_count(
            requested, "default_authoring_plan_accepted"
        ),
        "compile_save_dependency_declared_count": _truthy_count(
            requested, "compile_save_dependency_declared"
        ),
        "temp_package_mutation_boundary_clean_count": _truthy_count(
            requested, "temp_package_mutation_boundary_clean"
        ),
        "actor_authoring_readback_dry_run_ready_count": _truthy_count(
            requested, "actor_authoring_readback_dry_run_ready"
        ),
        "dry_run_blocks_actual_actor_authoring_outputs_count": _truthy_count(
            requested, "dry_run_blocks_actual_actor_authoring_outputs"
        ),
        "result_has_no_error_count": _truthy_count(
            requested, "result_has_no_error"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "rename_overwrite_dry_run_ready_count": _truthy_count(
            requested, "rename_overwrite_dry_run_ready"
        ),
        "actor_bp_expansion_dry_run_allowed_count": _truthy_count(
            requested, "actor_bp_expansion_dry_run_allowed"
        ),
        "actor_bp_expansion_dry_run_ready_count": _truthy_count(
            requested, "actor_bp_expansion_dry_run_ready"
        ),
        "actual_actor_bp_authoring_requires_final_user_checkpoint_count": (
            _truthy_count(
                requested,
                "actual_actor_bp_authoring_requires_final_user_checkpoint",
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
            for key in ACTOR_BP_EXPANSION_DRY_RUN_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_ACTOR_BP_AUTHORING_OUTPUT_COUNT_KEYS
        }
    )
    return summary
