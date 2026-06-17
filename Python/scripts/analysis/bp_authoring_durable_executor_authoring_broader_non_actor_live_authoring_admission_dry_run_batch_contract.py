#!/usr/bin/env python
"""
Sections 385-392 durable executor broader non-Actor live authoring admission dry-run.

This contract follows the broader non-Actor live read-only preflight. It admits
only an offline admission dry-run for live non-Actor Blueprint authoring. The
dry-run records the class-specific blockers for UserWidget, DataAsset-style
Blueprint, AnimBlueprint, Blueprint Function Library, and Blueprint Interface
routes. Actual asset creation, widget/default/animation/function/interface graph
mutation, compile, save, delete, rename, overwrite, cleanup, and production
writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract as readonly_preflight


DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_BATCH_SCHEMA = (
    "section_385_392_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_BATCH_SUMMARY_SCHEMA = (
    "section_385_392_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_summary_v1"
)
BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_RESULT_SCHEMA = (
    "section_385_392_broader_non_actor_live_authoring_admission_dry_run_result_v1"
)
SECTION_377_384_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_SUMMARY_SCHEMA = (
    readonly_preflight
    .DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_BATCH_SUMMARY_SCHEMA
)
DEFAULT_ADMISSION_ROUTE = "broader_non_actor_live_authoring"
DEFAULT_DRY_RUN_ROOT = "/Game/_MCP_Temp/DurableSaveGate/NonActorAdmissionDryRun"
DEFAULT_CANDIDATE_CLASSES = (
    "UserWidget",
    "PrimaryDataAsset",
    "AnimBlueprint",
    "BlueprintFunctionLibrary",
    "BlueprintInterface",
)
DEFAULT_PLANNED_OUTPUT_ASSET_PATHS = (
    "/Game/_MCP_Temp/DurableSaveGate/NonActorAdmissionDryRun/WBP_DurableNonActorAdmission",
    "/Game/_MCP_Temp/DurableSaveGate/NonActorAdmissionDryRun/DA_DurableNonActorAdmission",
    "/Game/_MCP_Temp/DurableSaveGate/NonActorAdmissionDryRun/ABP_DurableNonActorAdmission",
    "/Game/_MCP_Temp/DurableSaveGate/NonActorAdmissionDryRun/BFL_DurableNonActorAdmission",
    "/Game/_MCP_Temp/DurableSaveGate/NonActorAdmissionDryRun/BPI_DurableNonActorAdmission",
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_broader_non_actor_live_readonly_preflight_batch_count",
    "section_377_broader_non_actor_live_readonly_checkpoint_satisfied_count",
    "section_378_correct_project_headless_non_actor_readonly_probe_recorded_count",
    "section_379_user_widget_readonly_prerequisites_verified_count",
    "section_380_data_asset_readonly_prerequisites_verified_count",
    "section_381_anim_blueprint_readonly_prerequisites_verified_count",
    "section_382_non_actor_creation_mutation_outputs_blocked_count",
    "section_383_broader_non_actor_live_readonly_no_write_boundary_verified_count",
    "section_384_broader_non_actor_live_readonly_preflight_release_ready_count",
    "broader_non_actor_live_readonly_preflight_ready_count",
    "broader_non_actor_actual_authoring_still_blocked_count",
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    readonly_preflight
    .BLOCKED_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS
)

BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_PATH_COUNT_KEYS = (
    "section_385_broader_non_actor_live_authoring_admission_checkpoint_satisfied_count",
    "section_386_non_actor_live_authoring_admission_request_scope_classified_count",
    "section_387_user_widget_admission_blocked_pending_widget_tree_contract_count",
    "section_388_data_asset_admission_blocked_pending_default_contract_count",
    "section_389_anim_blueprint_admission_blocked_pending_skeleton_contract_count",
    "section_390_function_library_interface_admission_blocked_pending_graph_contract_count",
    "section_391_live_non_actor_creation_outputs_blocked_no_write_verified_count",
    "section_392_broader_non_actor_live_authoring_admission_dry_run_release_ready_count",
    "broader_non_actor_live_authoring_admission_dry_run_ready_count",
    "broader_non_actor_live_authoring_still_blocked_count",
)
BLOCKED_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_OUTPUT_COUNT_KEYS = (
    "live_non_actor_authoring_admission_command_dispatched_count",
    "live_non_actor_authoring_admission_command_executed_count",
    "user_widget_live_authoring_admitted_count",
    "user_widget_live_authoring_executed_count",
    "data_asset_live_authoring_admitted_count",
    "data_asset_live_authoring_executed_count",
    "anim_blueprint_live_authoring_admitted_count",
    "anim_blueprint_live_authoring_executed_count",
    "function_library_live_authoring_admitted_count",
    "function_library_live_authoring_executed_count",
    "blueprint_interface_live_authoring_admitted_count",
    "blueprint_interface_live_authoring_executed_count",
    "user_widget_blueprint_create_command_dispatched_count",
    "user_widget_blueprint_create_command_executed_count",
    "data_asset_blueprint_create_command_dispatched_count",
    "data_asset_blueprint_create_command_executed_count",
    "anim_blueprint_create_command_dispatched_count",
    "anim_blueprint_create_command_executed_count",
    "function_library_blueprint_create_command_dispatched_count",
    "function_library_blueprint_create_command_executed_count",
    "blueprint_interface_create_command_dispatched_count",
    "blueprint_interface_create_command_executed_count",
    "widget_tree_mutation_performed_count",
    "data_asset_default_mutation_performed_count",
    "animation_graph_mutation_performed_count",
    "function_library_graph_mutation_performed_count",
    "blueprint_interface_function_mutation_performed_count",
    "non_actor_blueprint_compile_dispatched_count",
    "non_actor_blueprint_compile_executed_count",
    "non_actor_blueprint_save_dispatched_count",
    "non_actor_blueprint_save_executed_count",
    "non_actor_blueprint_asset_write_performed_count",
    "non_actor_blueprint_package_dirty_marked_count",
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
BLOCKED_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_RESULT_KEYS = (
    "live_non_actor_authoring_admission_command_dispatched",
    "live_non_actor_authoring_admission_command_executed",
    "user_widget_live_authoring_admitted",
    "user_widget_live_authoring_executed",
    "data_asset_live_authoring_admitted",
    "data_asset_live_authoring_executed",
    "anim_blueprint_live_authoring_admitted",
    "anim_blueprint_live_authoring_executed",
    "function_library_live_authoring_admitted",
    "function_library_live_authoring_executed",
    "blueprint_interface_live_authoring_admitted",
    "blueprint_interface_live_authoring_executed",
    "user_widget_blueprint_create_command_dispatched",
    "user_widget_blueprint_create_command_executed",
    "data_asset_blueprint_create_command_dispatched",
    "data_asset_blueprint_create_command_executed",
    "anim_blueprint_create_command_dispatched",
    "anim_blueprint_create_command_executed",
    "function_library_blueprint_create_command_dispatched",
    "function_library_blueprint_create_command_executed",
    "blueprint_interface_create_command_dispatched",
    "blueprint_interface_create_command_executed",
    "widget_tree_mutation_performed",
    "data_asset_default_mutation_performed",
    "animation_graph_mutation_performed",
    "function_library_graph_mutation_performed",
    "blueprint_interface_function_mutation_performed",
    "non_actor_blueprint_compile_dispatched",
    "non_actor_blueprint_compile_executed",
    "non_actor_blueprint_save_dispatched",
    "non_actor_blueprint_save_executed",
    "non_actor_blueprint_asset_write_performed",
    "non_actor_blueprint_package_dirty_marked",
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


def build_broader_non_actor_live_authoring_admission_dry_run_result(
    *,
    dry_run_only: bool = True,
    admission_route: str = DEFAULT_ADMISSION_ROUTE,
    dry_run_root: str = DEFAULT_DRY_RUN_ROOT,
    candidate_classes: Sequence[str] = DEFAULT_CANDIDATE_CLASSES,
    planned_output_asset_paths: Sequence[str] = DEFAULT_PLANNED_OUTPUT_ASSET_PATHS,
    correct_project_readonly_preflight_required: bool = True,
    correct_project_readonly_preflight_satisfied: bool = True,
    actual_live_non_actor_authoring_allowed: bool = False,
    user_widget_requires_widget_tree_contract: bool = True,
    user_widget_admission_blocked_pending_widget_tree_contract: bool = True,
    data_asset_requires_default_mutation_contract: bool = True,
    data_asset_admission_blocked_pending_default_contract: bool = True,
    anim_blueprint_requires_skeleton_contract: bool = True,
    anim_blueprint_missing_skeleton_blocks_admission: bool = True,
    function_library_requires_graph_authoring_contract: bool = True,
    blueprint_interface_requires_interface_function_contract: bool = True,
    function_library_interface_admission_blocked_pending_graph_contract: bool = True,
    dirty_content_after_dry_run: Sequence[str] = (),
    dirty_maps_after_dry_run: Sequence[str] = (),
    live_non_actor_authoring_admission_command_dispatched: bool = False,
    live_non_actor_authoring_admission_command_executed: bool = False,
    user_widget_live_authoring_admitted: bool = False,
    user_widget_live_authoring_executed: bool = False,
    data_asset_live_authoring_admitted: bool = False,
    data_asset_live_authoring_executed: bool = False,
    anim_blueprint_live_authoring_admitted: bool = False,
    anim_blueprint_live_authoring_executed: bool = False,
    function_library_live_authoring_admitted: bool = False,
    function_library_live_authoring_executed: bool = False,
    blueprint_interface_live_authoring_admitted: bool = False,
    blueprint_interface_live_authoring_executed: bool = False,
    user_widget_blueprint_create_command_dispatched: bool = False,
    user_widget_blueprint_create_command_executed: bool = False,
    data_asset_blueprint_create_command_dispatched: bool = False,
    data_asset_blueprint_create_command_executed: bool = False,
    anim_blueprint_create_command_dispatched: bool = False,
    anim_blueprint_create_command_executed: bool = False,
    function_library_blueprint_create_command_dispatched: bool = False,
    function_library_blueprint_create_command_executed: bool = False,
    blueprint_interface_create_command_dispatched: bool = False,
    blueprint_interface_create_command_executed: bool = False,
    widget_tree_mutation_performed: bool = False,
    data_asset_default_mutation_performed: bool = False,
    animation_graph_mutation_performed: bool = False,
    function_library_graph_mutation_performed: bool = False,
    blueprint_interface_function_mutation_performed: bool = False,
    non_actor_blueprint_compile_dispatched: bool = False,
    non_actor_blueprint_compile_executed: bool = False,
    non_actor_blueprint_save_dispatched: bool = False,
    non_actor_blueprint_save_executed: bool = False,
    non_actor_blueprint_asset_write_performed: bool = False,
    non_actor_blueprint_package_dirty_marked: bool = False,
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
        "schema": BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_RESULT_SCHEMA,
        "dry_run_only": dry_run_only,
        "admission_route": admission_route,
        "dry_run_root": dry_run_root,
        "candidate_classes": list(candidate_classes),
        "planned_output_asset_paths": list(planned_output_asset_paths),
        "correct_project_readonly_preflight_required": (
            correct_project_readonly_preflight_required
        ),
        "correct_project_readonly_preflight_satisfied": (
            correct_project_readonly_preflight_satisfied
        ),
        "actual_live_non_actor_authoring_allowed": (
            actual_live_non_actor_authoring_allowed
        ),
        "user_widget_requires_widget_tree_contract": (
            user_widget_requires_widget_tree_contract
        ),
        "user_widget_admission_blocked_pending_widget_tree_contract": (
            user_widget_admission_blocked_pending_widget_tree_contract
        ),
        "data_asset_requires_default_mutation_contract": (
            data_asset_requires_default_mutation_contract
        ),
        "data_asset_admission_blocked_pending_default_contract": (
            data_asset_admission_blocked_pending_default_contract
        ),
        "anim_blueprint_requires_skeleton_contract": (
            anim_blueprint_requires_skeleton_contract
        ),
        "anim_blueprint_missing_skeleton_blocks_admission": (
            anim_blueprint_missing_skeleton_blocks_admission
        ),
        "function_library_requires_graph_authoring_contract": (
            function_library_requires_graph_authoring_contract
        ),
        "blueprint_interface_requires_interface_function_contract": (
            blueprint_interface_requires_interface_function_contract
        ),
        "function_library_interface_admission_blocked_pending_graph_contract": (
            function_library_interface_admission_blocked_pending_graph_contract
        ),
        "dirty_content_after_dry_run": list(dirty_content_after_dry_run),
        "dirty_maps_after_dry_run": list(dirty_maps_after_dry_run),
        "live_non_actor_authoring_admission_command_dispatched": (
            live_non_actor_authoring_admission_command_dispatched
        ),
        "live_non_actor_authoring_admission_command_executed": (
            live_non_actor_authoring_admission_command_executed
        ),
        "user_widget_live_authoring_admitted": user_widget_live_authoring_admitted,
        "user_widget_live_authoring_executed": user_widget_live_authoring_executed,
        "data_asset_live_authoring_admitted": data_asset_live_authoring_admitted,
        "data_asset_live_authoring_executed": data_asset_live_authoring_executed,
        "anim_blueprint_live_authoring_admitted": (
            anim_blueprint_live_authoring_admitted
        ),
        "anim_blueprint_live_authoring_executed": (
            anim_blueprint_live_authoring_executed
        ),
        "function_library_live_authoring_admitted": (
            function_library_live_authoring_admitted
        ),
        "function_library_live_authoring_executed": (
            function_library_live_authoring_executed
        ),
        "blueprint_interface_live_authoring_admitted": (
            blueprint_interface_live_authoring_admitted
        ),
        "blueprint_interface_live_authoring_executed": (
            blueprint_interface_live_authoring_executed
        ),
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
        "function_library_blueprint_create_command_dispatched": (
            function_library_blueprint_create_command_dispatched
        ),
        "function_library_blueprint_create_command_executed": (
            function_library_blueprint_create_command_executed
        ),
        "blueprint_interface_create_command_dispatched": (
            blueprint_interface_create_command_dispatched
        ),
        "blueprint_interface_create_command_executed": (
            blueprint_interface_create_command_executed
        ),
        "widget_tree_mutation_performed": widget_tree_mutation_performed,
        "data_asset_default_mutation_performed": (
            data_asset_default_mutation_performed
        ),
        "animation_graph_mutation_performed": animation_graph_mutation_performed,
        "function_library_graph_mutation_performed": (
            function_library_graph_mutation_performed
        ),
        "blueprint_interface_function_mutation_performed": (
            blueprint_interface_function_mutation_performed
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


def build_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract(
    requested: bool,
    section_377_384_broader_non_actor_live_readonly_preflight_summary: Dict[str, Any],
    broader_non_actor_live_authoring_admission_dry_run_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_377_384_summary_schema_matches = bool(
        section_377_384_broader_non_actor_live_readonly_preflight_summary.get(
            "schema"
        )
        == SECTION_377_384_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_SUMMARY_SCHEMA
    )
    section_377_384_summary_passed = bool(
        section_377_384_broader_non_actor_live_readonly_preflight_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_readonly_preflight_ready = all(
        _count_is_one(
            section_377_384_broader_non_actor_live_readonly_preflight_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_377_384_broader_non_actor_live_readonly_preflight_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        broader_non_actor_live_authoring_admission_dry_run_result.get("schema")
        == BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_377_384_summary_schema_matches
        and section_377_384_summary_passed
        and upstream_readonly_preflight_ready
        and upstream_outputs_closed
    )
    planned_paths = tuple(
        broader_non_actor_live_authoring_admission_dry_run_result.get(
            "planned_output_asset_paths", ()
        )
        or ()
    )
    admission_scope_classified = bool(
        broader_non_actor_live_authoring_admission_dry_run_result.get(
            "dry_run_only"
        )
        and broader_non_actor_live_authoring_admission_dry_run_result.get(
            "admission_route"
        )
        == DEFAULT_ADMISSION_ROUTE
        and broader_non_actor_live_authoring_admission_dry_run_result.get(
            "dry_run_root"
        )
        == DEFAULT_DRY_RUN_ROOT
        and tuple(
            broader_non_actor_live_authoring_admission_dry_run_result.get(
                "candidate_classes", ()
            )
            or ()
        )
        == DEFAULT_CANDIDATE_CLASSES
        and planned_paths == DEFAULT_PLANNED_OUTPUT_ASSET_PATHS
        and all(path.startswith("/Game/_MCP_Temp/") for path in planned_paths)
        and broader_non_actor_live_authoring_admission_dry_run_result.get(
            "correct_project_readonly_preflight_required"
        )
        and broader_non_actor_live_authoring_admission_dry_run_result.get(
            "correct_project_readonly_preflight_satisfied"
        )
    )
    user_widget_blocked = bool(
        broader_non_actor_live_authoring_admission_dry_run_result.get(
            "user_widget_requires_widget_tree_contract"
        )
        and broader_non_actor_live_authoring_admission_dry_run_result.get(
            "user_widget_admission_blocked_pending_widget_tree_contract"
        )
        and not broader_non_actor_live_authoring_admission_dry_run_result.get(
            "user_widget_live_authoring_admitted"
        )
    )
    data_asset_blocked = bool(
        broader_non_actor_live_authoring_admission_dry_run_result.get(
            "data_asset_requires_default_mutation_contract"
        )
        and broader_non_actor_live_authoring_admission_dry_run_result.get(
            "data_asset_admission_blocked_pending_default_contract"
        )
        and not broader_non_actor_live_authoring_admission_dry_run_result.get(
            "data_asset_live_authoring_admitted"
        )
    )
    anim_blueprint_blocked = bool(
        broader_non_actor_live_authoring_admission_dry_run_result.get(
            "anim_blueprint_requires_skeleton_contract"
        )
        and broader_non_actor_live_authoring_admission_dry_run_result.get(
            "anim_blueprint_missing_skeleton_blocks_admission"
        )
        and not broader_non_actor_live_authoring_admission_dry_run_result.get(
            "anim_blueprint_live_authoring_admitted"
        )
    )
    function_library_interface_blocked = bool(
        broader_non_actor_live_authoring_admission_dry_run_result.get(
            "function_library_requires_graph_authoring_contract"
        )
        and broader_non_actor_live_authoring_admission_dry_run_result.get(
            "blueprint_interface_requires_interface_function_contract"
        )
        and broader_non_actor_live_authoring_admission_dry_run_result.get(
            "function_library_interface_admission_blocked_pending_graph_contract"
        )
        and not broader_non_actor_live_authoring_admission_dry_run_result.get(
            "function_library_live_authoring_admitted"
        )
        and not broader_non_actor_live_authoring_admission_dry_run_result.get(
            "blueprint_interface_live_authoring_admitted"
        )
    )
    live_creation_outputs_blocked = bool(
        not broader_non_actor_live_authoring_admission_dry_run_result.get(
            "actual_live_non_actor_authoring_allowed"
        )
        and all(
            not broader_non_actor_live_authoring_admission_dry_run_result.get(
                key
            )
            for key in BLOCKED_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_RESULT_KEYS
        )
    )
    no_write_boundary_verified = bool(
        live_creation_outputs_blocked
        and not broader_non_actor_live_authoring_admission_dry_run_result.get(
            "dirty_content_after_dry_run"
        )
        and not broader_non_actor_live_authoring_admission_dry_run_result.get(
            "dirty_maps_after_dry_run"
        )
    )
    result_has_no_error = bool(
        broader_non_actor_live_authoring_admission_dry_run_result.get("error")
        in (None, "")
    )
    dry_run_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and admission_scope_classified
        and user_widget_blocked
        and data_asset_blocked
        and anim_blueprint_blocked
        and function_library_interface_blocked
        and live_creation_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_377_384_summary_schema_matches": (
            section_377_384_summary_schema_matches
        ),
        "section_377_384_summary_passed": section_377_384_summary_passed,
        "section_377_384_broader_non_actor_live_readonly_preflight_ready": (
            upstream_readonly_preflight_ready
        ),
        "section_377_384_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "live_authoring_admission_dry_run_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "admission_request_scope_classified": admission_scope_classified,
        "user_widget_admission_blocked_pending_widget_tree_contract": (
            user_widget_blocked
        ),
        "data_asset_admission_blocked_pending_default_contract": (
            data_asset_blocked
        ),
        "anim_blueprint_admission_blocked_pending_skeleton_contract": (
            anim_blueprint_blocked
        ),
        "function_library_interface_admission_blocked_pending_graph_contract": (
            function_library_interface_blocked
        ),
        "live_non_actor_creation_outputs_blocked": live_creation_outputs_blocked,
        "live_non_actor_authoring_admission_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_385_broader_non_actor_live_authoring_admission_checkpoint_satisfied": (
            dry_run_ready
        ),
        "section_386_non_actor_live_authoring_admission_request_scope_classified": (
            dry_run_ready
        ),
        "section_387_user_widget_admission_blocked_pending_widget_tree_contract": (
            dry_run_ready
        ),
        "section_388_data_asset_admission_blocked_pending_default_contract": (
            dry_run_ready
        ),
        "section_389_anim_blueprint_admission_blocked_pending_skeleton_contract": (
            dry_run_ready
        ),
        "section_390_function_library_interface_admission_blocked_pending_graph_contract": (
            dry_run_ready
        ),
        "section_391_live_non_actor_creation_outputs_blocked_no_write_verified": (
            dry_run_ready
        ),
        "section_392_broader_non_actor_live_authoring_admission_dry_run_release_ready": (
            dry_run_ready
        ),
        "broader_non_actor_live_authoring_admission_dry_run_ready": dry_run_ready,
        "broader_non_actor_live_authoring_still_blocked": dry_run_ready,
        "final_durable_release_ready": dry_run_ready,
        **{
            key: 1 if dry_run_ready else 0
            for key in BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in (
                BLOCKED_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_OUTPUT_COUNT_KEYS
            )
        },
    }


def summarize_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "broader_non_actor_live_authoring_admission_dry_run_ready",
            )
            == len(requested)
            and _truthy_count(
                requested, "broader_non_actor_live_authoring_still_blocked"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_count": (
            len(requested)
        ),
        "section_377_384_summary_schema_matches_count": _truthy_count(
            requested, "section_377_384_summary_schema_matches"
        ),
        "section_377_384_summary_passed_count": _truthy_count(
            requested, "section_377_384_summary_passed"
        ),
        "section_377_384_broader_non_actor_live_readonly_preflight_ready_count": (
            _truthy_count(
                requested,
                "section_377_384_broader_non_actor_live_readonly_preflight_ready",
            )
        ),
        "section_377_384_outputs_closed_count": _truthy_count(
            requested, "section_377_384_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "live_authoring_admission_dry_run_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "live_authoring_admission_dry_run_checkpoint_satisfied",
            )
        ),
        "admission_request_scope_classified_count": _truthy_count(
            requested, "admission_request_scope_classified"
        ),
        "user_widget_admission_blocked_pending_widget_tree_contract_count": (
            _truthy_count(
                requested,
                "user_widget_admission_blocked_pending_widget_tree_contract",
            )
        ),
        "data_asset_admission_blocked_pending_default_contract_count": (
            _truthy_count(
                requested,
                "data_asset_admission_blocked_pending_default_contract",
            )
        ),
        "anim_blueprint_admission_blocked_pending_skeleton_contract_count": (
            _truthy_count(
                requested,
                "anim_blueprint_admission_blocked_pending_skeleton_contract",
            )
        ),
        "function_library_interface_admission_blocked_pending_graph_contract_count": (
            _truthy_count(
                requested,
                "function_library_interface_admission_blocked_pending_graph_contract",
            )
        ),
        "live_non_actor_creation_outputs_blocked_count": _truthy_count(
            requested, "live_non_actor_creation_outputs_blocked"
        ),
        "live_non_actor_authoring_admission_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "live_non_actor_authoring_admission_no_write_boundary_verified",
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
            for key in BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in (
                BLOCKED_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_OUTPUT_COUNT_KEYS
            )
        }
    )
    return summary
