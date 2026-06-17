#!/usr/bin/env python
"""
Sections 337-344 durable executor broader non-Actor Blueprint dry-run batch.

This contract follows the post-recreation diagnostics refresh and admits only
offline dry-run planning for broader Blueprint classes. UserWidget, DataAsset,
and AnimBlueprint candidates can be classified, but actual asset creation,
graph/default/widget/animation mutation, compile, save, delete, rename,
overwrite, cleanup, and production writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract as diagnostics_refresh


DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_BATCH_SCHEMA = (
    "section_337_344_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_BATCH_SUMMARY_SCHEMA = (
    "section_337_344_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_summary_v1"
)
BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_RESULT_SCHEMA = (
    "section_337_344_broader_non_actor_blueprint_dry_run_result_v1"
)
SECTION_329_336_POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_SUMMARY_SCHEMA = (
    diagnostics_refresh
    .DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_BATCH_SUMMARY_SCHEMA
)
DEFAULT_CANDIDATE_BLUEPRINT_CLASSES = (
    "UserWidget",
    "DataAsset",
    "AnimBlueprint",
)
DEFAULT_DRY_RUN_PLAN_ROOT = "/Game/_MCP_Temp/DurableSaveGate/DryRun"
DEFAULT_PLANNED_OUTPUT_ASSET_PATHS = (
    "/Game/_MCP_Temp/DurableSaveGate/DryRun/WBP_DurableSaveGatePrep_DryRun",
    "/Game/_MCP_Temp/DurableSaveGate/DryRun/DA_DurableSaveGatePrep_DryRun",
    "/Game/_MCP_Temp/DurableSaveGate/DryRun/ABP_DurableSaveGatePrep_DryRun",
)
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_post_recreation_function_diagnostics_refresh_batch_count",
    "section_329_post_recreation_diagnostics_refresh_checkpoint_satisfied_count",
    "section_330_current_actor_bp_graph_inventory_ready_count",
    "section_331_empty_graph_state_safely_classified_count",
    "section_332_function_diagnostics_refreshed_count",
    "section_333_pin_contract_diagnostics_refreshed_count",
    "section_334_graph_layout_diagnostics_refreshed_count",
    "section_335_diagnostics_refresh_no_write_boundary_verified_count",
    "section_336_post_recreation_function_diagnostics_refresh_release_ready_count",
    "post_recreation_function_diagnostics_refreshed_count",
    "post_recreation_empty_graph_state_verified_count",
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
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
BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_PATH_COUNT_KEYS = (
    "section_337_broader_blueprint_dry_run_checkpoint_satisfied_count",
    "section_338_user_widget_authoring_plan_classified_count",
    "section_339_data_asset_authoring_plan_classified_count",
    "section_340_anim_blueprint_authoring_plan_classified_count",
    "section_341_class_specific_prerequisites_recorded_count",
    "section_342_actual_non_actor_blueprint_creation_blocked_count",
    "section_343_broader_blueprint_dry_run_no_write_boundary_verified_count",
    "section_344_broader_non_actor_blueprint_dry_run_release_ready_count",
    "broader_non_actor_blueprint_dry_run_ready_count",
    "broader_blueprint_actual_authoring_still_blocked_count",
)
BLOCKED_BROADER_NON_ACTOR_BLUEPRINT_OUTPUT_COUNT_KEYS = (
    "user_widget_blueprint_create_command_dispatched_count",
    "user_widget_blueprint_create_command_executed_count",
    "data_asset_blueprint_create_command_dispatched_count",
    "data_asset_blueprint_create_command_executed_count",
    "anim_blueprint_create_command_dispatched_count",
    "anim_blueprint_create_command_executed_count",
    "non_actor_blueprint_compile_dispatched_count",
    "non_actor_blueprint_compile_executed_count",
    "non_actor_blueprint_save_dispatched_count",
    "non_actor_blueprint_save_executed_count",
    "non_actor_blueprint_asset_write_performed_count",
    "non_actor_blueprint_package_dirty_marked_count",
    "widget_tree_mutation_performed_count",
    "data_asset_default_mutation_performed_count",
    "animation_graph_mutation_performed_count",
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
BLOCKED_BROADER_NON_ACTOR_BLUEPRINT_RESULT_KEYS = (
    "user_widget_blueprint_create_command_dispatched",
    "user_widget_blueprint_create_command_executed",
    "data_asset_blueprint_create_command_dispatched",
    "data_asset_blueprint_create_command_executed",
    "anim_blueprint_create_command_dispatched",
    "anim_blueprint_create_command_executed",
    "non_actor_blueprint_compile_dispatched",
    "non_actor_blueprint_compile_executed",
    "non_actor_blueprint_save_dispatched",
    "non_actor_blueprint_save_executed",
    "non_actor_blueprint_asset_write_performed",
    "non_actor_blueprint_package_dirty_marked",
    "widget_tree_mutation_performed",
    "data_asset_default_mutation_performed",
    "animation_graph_mutation_performed",
    "cleanup_allowed",
    "cleanup_executed",
    "delete_asset_allowed",
    "delete_asset_executed_output",
    "rename_asset_allowed",
    "rename_command_dispatched",
    "rename_command_executed",
    "overwrite_allowed",
    "overwrite_executed",
    "production_path_write_allowed",
    "production_path_write_executed",
)


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _count_is_one(summary: Dict[str, Any], key: str) -> bool:
    return bool(summary.get(key) == 1)


def _count_is_zero(summary: Dict[str, Any], key: str) -> bool:
    return bool(int(summary.get(key, 0) or 0) == 0)


def build_broader_non_actor_blueprint_dry_run_result(
    *,
    dry_run_only: bool = True,
    plan_root: str = DEFAULT_DRY_RUN_PLAN_ROOT,
    candidate_blueprint_classes: Sequence[str] = (
        DEFAULT_CANDIDATE_BLUEPRINT_CLASSES
    ),
    planned_output_asset_paths: Sequence[str] = (
        DEFAULT_PLANNED_OUTPUT_ASSET_PATHS
    ),
    user_widget_plan_classified: bool = True,
    user_widget_parent_class: str = "UserWidget",
    user_widget_requires_widget_blueprint_factory: bool = True,
    data_asset_plan_classified: bool = True,
    data_asset_parent_class_required: bool = True,
    data_asset_default_mutation_requires_separate_contract: bool = True,
    anim_blueprint_plan_classified: bool = True,
    anim_blueprint_requires_skeleton: bool = True,
    anim_blueprint_missing_skeleton_blocks_execution: bool = True,
    class_specific_prerequisites_recorded: bool = True,
    actual_non_actor_blueprint_authoring_allowed: bool = False,
    output_assets_created: bool = False,
    dirty_maps_after_dry_run: Sequence[str] = (),
    dirty_content_after_dry_run: Sequence[str] = (),
    user_widget_blueprint_create_command_dispatched: bool = False,
    user_widget_blueprint_create_command_executed: bool = False,
    data_asset_blueprint_create_command_dispatched: bool = False,
    data_asset_blueprint_create_command_executed: bool = False,
    anim_blueprint_create_command_dispatched: bool = False,
    anim_blueprint_create_command_executed: bool = False,
    non_actor_blueprint_compile_dispatched: bool = False,
    non_actor_blueprint_compile_executed: bool = False,
    non_actor_blueprint_save_dispatched: bool = False,
    non_actor_blueprint_save_executed: bool = False,
    non_actor_blueprint_asset_write_performed: bool = False,
    non_actor_blueprint_package_dirty_marked: bool = False,
    widget_tree_mutation_performed: bool = False,
    data_asset_default_mutation_performed: bool = False,
    animation_graph_mutation_performed: bool = False,
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
        "schema": BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_RESULT_SCHEMA,
        "dry_run_only": dry_run_only,
        "plan_root": plan_root,
        "candidate_blueprint_classes": list(candidate_blueprint_classes),
        "planned_output_asset_paths": list(planned_output_asset_paths),
        "user_widget_plan_classified": user_widget_plan_classified,
        "user_widget_parent_class": user_widget_parent_class,
        "user_widget_requires_widget_blueprint_factory": (
            user_widget_requires_widget_blueprint_factory
        ),
        "data_asset_plan_classified": data_asset_plan_classified,
        "data_asset_parent_class_required": data_asset_parent_class_required,
        "data_asset_default_mutation_requires_separate_contract": (
            data_asset_default_mutation_requires_separate_contract
        ),
        "anim_blueprint_plan_classified": anim_blueprint_plan_classified,
        "anim_blueprint_requires_skeleton": anim_blueprint_requires_skeleton,
        "anim_blueprint_missing_skeleton_blocks_execution": (
            anim_blueprint_missing_skeleton_blocks_execution
        ),
        "class_specific_prerequisites_recorded": (
            class_specific_prerequisites_recorded
        ),
        "actual_non_actor_blueprint_authoring_allowed": (
            actual_non_actor_blueprint_authoring_allowed
        ),
        "output_assets_created": output_assets_created,
        "dirty_maps_after_dry_run": list(dirty_maps_after_dry_run),
        "dirty_content_after_dry_run": list(dirty_content_after_dry_run),
        "user_widget_blueprint_create_command_dispatched": (
            user_widget_blueprint_create_command_dispatched
        ),
        "user_widget_blueprint_create_command_executed": (
            user_widget_blueprint_create_command_executed
        ),
        "data_asset_blueprint_create_command_dispatched": (
            data_asset_blueprint_create_command_dispatched
        ),
        "data_asset_blueprint_create_command_executed": (
            data_asset_blueprint_create_command_executed
        ),
        "anim_blueprint_create_command_dispatched": (
            anim_blueprint_create_command_dispatched
        ),
        "anim_blueprint_create_command_executed": (
            anim_blueprint_create_command_executed
        ),
        "non_actor_blueprint_compile_dispatched": (
            non_actor_blueprint_compile_dispatched
        ),
        "non_actor_blueprint_compile_executed": (
            non_actor_blueprint_compile_executed
        ),
        "non_actor_blueprint_save_dispatched": non_actor_blueprint_save_dispatched,
        "non_actor_blueprint_save_executed": non_actor_blueprint_save_executed,
        "non_actor_blueprint_asset_write_performed": (
            non_actor_blueprint_asset_write_performed
        ),
        "non_actor_blueprint_package_dirty_marked": (
            non_actor_blueprint_package_dirty_marked
        ),
        "widget_tree_mutation_performed": widget_tree_mutation_performed,
        "data_asset_default_mutation_performed": (
            data_asset_default_mutation_performed
        ),
        "animation_graph_mutation_performed": animation_graph_mutation_performed,
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


def build_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract(
    requested: bool,
    section_329_336_post_recreation_function_diagnostics_refresh_summary: Dict[str, Any],
    broader_non_actor_blueprint_dry_run_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_329_336_summary_schema_matches = bool(
        section_329_336_post_recreation_function_diagnostics_refresh_summary.get(
            "schema"
        )
        == SECTION_329_336_POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_SUMMARY_SCHEMA
    )
    section_329_336_summary_passed = bool(
        section_329_336_post_recreation_function_diagnostics_refresh_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_diagnostics_refreshed = all(
        _count_is_one(
            section_329_336_post_recreation_function_diagnostics_refresh_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_329_336_post_recreation_function_diagnostics_refresh_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        broader_non_actor_blueprint_dry_run_result.get("schema")
        == BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_329_336_summary_schema_matches
        and section_329_336_summary_passed
        and upstream_diagnostics_refreshed
        and upstream_outputs_closed
    )
    planned_paths = tuple(
        broader_non_actor_blueprint_dry_run_result.get(
            "planned_output_asset_paths", ()
        )
        or ()
    )
    dry_run_scope_verified = bool(
        broader_non_actor_blueprint_dry_run_result.get("dry_run_only")
        and broader_non_actor_blueprint_dry_run_result.get("plan_root")
        == DEFAULT_DRY_RUN_PLAN_ROOT
        and tuple(
            broader_non_actor_blueprint_dry_run_result.get(
                "candidate_blueprint_classes", ()
            )
            or ()
        )
        == DEFAULT_CANDIDATE_BLUEPRINT_CLASSES
        and planned_paths == DEFAULT_PLANNED_OUTPUT_ASSET_PATHS
        and all(path.startswith("/Game/_MCP_Temp/") for path in planned_paths)
        and not broader_non_actor_blueprint_dry_run_result.get(
            "output_assets_created"
        )
    )
    user_widget_plan_classified = bool(
        broader_non_actor_blueprint_dry_run_result.get(
            "user_widget_plan_classified"
        )
        and broader_non_actor_blueprint_dry_run_result.get(
            "user_widget_parent_class"
        )
        == "UserWidget"
        and broader_non_actor_blueprint_dry_run_result.get(
            "user_widget_requires_widget_blueprint_factory"
        )
    )
    data_asset_plan_classified = bool(
        broader_non_actor_blueprint_dry_run_result.get(
            "data_asset_plan_classified"
        )
        and broader_non_actor_blueprint_dry_run_result.get(
            "data_asset_parent_class_required"
        )
        and broader_non_actor_blueprint_dry_run_result.get(
            "data_asset_default_mutation_requires_separate_contract"
        )
    )
    anim_blueprint_plan_classified = bool(
        broader_non_actor_blueprint_dry_run_result.get(
            "anim_blueprint_plan_classified"
        )
        and broader_non_actor_blueprint_dry_run_result.get(
            "anim_blueprint_requires_skeleton"
        )
        and broader_non_actor_blueprint_dry_run_result.get(
            "anim_blueprint_missing_skeleton_blocks_execution"
        )
    )
    class_specific_prerequisites_recorded = bool(
        broader_non_actor_blueprint_dry_run_result.get(
            "class_specific_prerequisites_recorded"
        )
        and user_widget_plan_classified
        and data_asset_plan_classified
        and anim_blueprint_plan_classified
    )
    actual_creation_blocked = bool(
        not broader_non_actor_blueprint_dry_run_result.get(
            "actual_non_actor_blueprint_authoring_allowed"
        )
        and all(
            not broader_non_actor_blueprint_dry_run_result.get(key)
            for key in BLOCKED_BROADER_NON_ACTOR_BLUEPRINT_RESULT_KEYS
        )
    )
    no_write_boundary_verified = bool(
        actual_creation_blocked
        and not broader_non_actor_blueprint_dry_run_result.get(
            "dirty_maps_after_dry_run"
        )
        and not broader_non_actor_blueprint_dry_run_result.get(
            "dirty_content_after_dry_run"
        )
    )
    result_has_no_error = bool(
        broader_non_actor_blueprint_dry_run_result.get("error") in (None, "")
    )
    dry_run_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and dry_run_scope_verified
        and user_widget_plan_classified
        and data_asset_plan_classified
        and anim_blueprint_plan_classified
        and class_specific_prerequisites_recorded
        and actual_creation_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_329_336_summary_schema_matches": (
            section_329_336_summary_schema_matches
        ),
        "section_329_336_summary_passed": section_329_336_summary_passed,
        "section_329_336_post_recreation_diagnostics_refreshed": (
            upstream_diagnostics_refreshed
        ),
        "section_329_336_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "broader_blueprint_dry_run_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "broader_blueprint_dry_run_scope_verified": dry_run_scope_verified,
        "user_widget_authoring_plan_classified": user_widget_plan_classified,
        "data_asset_authoring_plan_classified": data_asset_plan_classified,
        "anim_blueprint_authoring_plan_classified": (
            anim_blueprint_plan_classified
        ),
        "class_specific_prerequisites_recorded": (
            class_specific_prerequisites_recorded
        ),
        "actual_non_actor_blueprint_creation_blocked": (
            actual_creation_blocked
        ),
        "broader_blueprint_dry_run_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_337_broader_blueprint_dry_run_checkpoint_satisfied": (
            dry_run_ready
        ),
        "section_338_user_widget_authoring_plan_classified": dry_run_ready,
        "section_339_data_asset_authoring_plan_classified": dry_run_ready,
        "section_340_anim_blueprint_authoring_plan_classified": dry_run_ready,
        "section_341_class_specific_prerequisites_recorded": dry_run_ready,
        "section_342_actual_non_actor_blueprint_creation_blocked": (
            dry_run_ready
        ),
        "section_343_broader_blueprint_dry_run_no_write_boundary_verified": (
            dry_run_ready
        ),
        "section_344_broader_non_actor_blueprint_dry_run_release_ready": (
            dry_run_ready
        ),
        "broader_non_actor_blueprint_dry_run_ready": dry_run_ready,
        "broader_blueprint_actual_authoring_still_blocked": dry_run_ready,
        "final_durable_release_ready": dry_run_ready,
        **{
            key: 1 if dry_run_ready else 0
            for key in BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_BROADER_NON_ACTOR_BLUEPRINT_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "broader_non_actor_blueprint_dry_run_ready"
            )
            == len(requested)
            and _truthy_count(
                requested, "broader_blueprint_actual_authoring_still_blocked"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_BROADER_NON_ACTOR_BLUEPRINT_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_broader_non_actor_blueprint_dry_run_batch_count": (
            len(requested)
        ),
        "section_329_336_summary_schema_matches_count": _truthy_count(
            requested, "section_329_336_summary_schema_matches"
        ),
        "section_329_336_summary_passed_count": _truthy_count(
            requested, "section_329_336_summary_passed"
        ),
        "section_329_336_post_recreation_diagnostics_refreshed_count": (
            _truthy_count(
                requested,
                "section_329_336_post_recreation_diagnostics_refreshed",
            )
        ),
        "section_329_336_outputs_closed_count": _truthy_count(
            requested, "section_329_336_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "broader_blueprint_dry_run_checkpoint_satisfied_count": _truthy_count(
            requested, "broader_blueprint_dry_run_checkpoint_satisfied"
        ),
        "broader_blueprint_dry_run_scope_verified_count": _truthy_count(
            requested, "broader_blueprint_dry_run_scope_verified"
        ),
        "user_widget_authoring_plan_classified_count": _truthy_count(
            requested, "user_widget_authoring_plan_classified"
        ),
        "data_asset_authoring_plan_classified_count": _truthy_count(
            requested, "data_asset_authoring_plan_classified"
        ),
        "anim_blueprint_authoring_plan_classified_count": _truthy_count(
            requested, "anim_blueprint_authoring_plan_classified"
        ),
        "class_specific_prerequisites_recorded_count": _truthy_count(
            requested, "class_specific_prerequisites_recorded"
        ),
        "actual_non_actor_blueprint_creation_blocked_count": _truthy_count(
            requested, "actual_non_actor_blueprint_creation_blocked"
        ),
        "broader_blueprint_dry_run_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "broader_blueprint_dry_run_no_write_boundary_verified",
            )
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
            for key in BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_BROADER_NON_ACTOR_BLUEPRINT_OUTPUT_COUNT_KEYS
        }
    )
    return summary
