#!/usr/bin/env python
"""
Sections 377-384 durable executor broader non-Actor live read-only preflight.

This contract follows the correct-project live MCP route preflight. It records
a headless Unreal read-only probe for broader non-Actor Blueprint prerequisites:
WidgetBlueprint, DataAsset-style Blueprint, AnimBlueprint, Blueprint Function
Library, and Blueprint Interface factories/classes are visible in the correct
project. Actual non-Actor Blueprint creation, widget/default/animation graph
mutation, compile, save, delete, rename, overwrite, cleanup, and production
writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

import bp_authoring_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract as live_route


DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_BATCH_SCHEMA = (
    "section_377_384_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_BATCH_SUMMARY_SCHEMA = (
    "section_377_384_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_summary_v1"
)
BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_RESULT_SCHEMA = (
    "section_377_384_broader_non_actor_live_readonly_preflight_result_v1"
)
SECTION_369_376_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_SUMMARY_SCHEMA = (
    live_route
    .DURABLE_EXECUTOR_AUTHORING_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_BATCH_SUMMARY_SCHEMA
)
DEFAULT_PROJECT_FILE_PATH = live_route.DEFAULT_PROJECT_FILE_PATH
DEFAULT_FACTORY_CLASSES = (
    "WidgetBlueprintFactory",
    "BlueprintFactory",
    "AnimBlueprintFactory",
    "BlueprintFunctionLibraryFactory",
    "BlueprintInterfaceFactory",
)
DEFAULT_PARENT_CLASS_PROBES = {
    "UserWidget": {
        "path": "/Script/UMG.UserWidget",
        "class_name": "UserWidget",
        "loaded": True,
    },
    "PrimaryDataAsset": {
        "path": "/Script/Engine.PrimaryDataAsset",
        "class_name": "PrimaryDataAsset",
        "loaded": True,
    },
    "AnimInstance": {
        "path": "/Script/Engine.AnimInstance",
        "class_name": "AnimInstance",
        "loaded": True,
    },
    "BlueprintFunctionLibrary": {
        "path": "/Script/Engine.BlueprintFunctionLibrary",
        "class_name": "BlueprintFunctionLibrary",
        "loaded": True,
    },
}
DEFAULT_PREFLIGHT_MARKER = "CODEX_SECTION_377_BROADER_NON_ACTOR_READONLY_PREFLIGHT"

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_correct_project_live_mcp_route_preflight_batch_count",
    "section_369_correct_project_live_mcp_route_checkpoint_satisfied_count",
    "section_370_mcp_config_preflight_verified_count",
    "section_371_sibling_server_path_verified_count",
    "section_372_live_bridge_read_only_probe_recorded_count",
    "section_373_live_bridge_correct_project_not_verified_count",
    "section_374_live_mcp_activation_outputs_blocked_count",
    "section_375_correct_project_live_mcp_route_no_write_boundary_verified_count",
    "section_376_correct_project_live_mcp_route_preflight_release_ready_count",
    "correct_project_live_mcp_route_preflight_ready_count",
    "correct_project_live_mcp_activation_still_blocked_count",
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    live_route
    .BLOCKED_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
)

BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_PATH_COUNT_KEYS = (
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
)
BLOCKED_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS = (
    "user_widget_blueprint_create_command_dispatched_count",
    "user_widget_blueprint_create_command_executed_count",
    "data_asset_blueprint_create_command_dispatched_count",
    "data_asset_blueprint_create_command_executed_count",
    "anim_blueprint_create_command_dispatched_count",
    "anim_blueprint_create_command_executed_count",
    "non_actor_blueprint_creation_command_dispatched_count",
    "non_actor_blueprint_creation_command_executed_count",
    "widget_tree_mutation_performed_count",
    "data_asset_default_mutation_performed_count",
    "animation_graph_mutation_performed_count",
    "non_actor_blueprint_compile_dispatched_count",
    "non_actor_blueprint_compile_executed_count",
    "non_actor_blueprint_save_dispatched_count",
    "non_actor_blueprint_save_executed_count",
    "non_actor_blueprint_asset_write_performed_count",
    "non_actor_blueprint_package_dirty_marked_count",
    "compile_executed_count",
    "save_executed_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
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
BLOCKED_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_RESULT_KEYS = (
    "user_widget_blueprint_create_command_dispatched",
    "user_widget_blueprint_create_command_executed",
    "data_asset_blueprint_create_command_dispatched",
    "data_asset_blueprint_create_command_executed",
    "anim_blueprint_create_command_dispatched",
    "anim_blueprint_create_command_executed",
    "non_actor_blueprint_creation_command_dispatched",
    "non_actor_blueprint_creation_command_executed",
    "widget_tree_mutation_performed",
    "data_asset_default_mutation_performed",
    "animation_graph_mutation_performed",
    "non_actor_blueprint_compile_dispatched",
    "non_actor_blueprint_compile_executed",
    "non_actor_blueprint_save_dispatched",
    "non_actor_blueprint_save_executed",
    "non_actor_blueprint_asset_write_performed",
    "non_actor_blueprint_package_dirty_marked",
    "compile_executed",
    "save_executed",
    "asset_write_performed",
    "package_dirty_marked",
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


def _factory_map(
    overrides: Mapping[str, bool] | None = None,
) -> Dict[str, bool]:
    factory_classes = {name: True for name in DEFAULT_FACTORY_CLASSES}
    if overrides:
        factory_classes.update(overrides)
    return factory_classes


def _parent_probe_map(
    overrides: Mapping[str, Mapping[str, Any]] | None = None,
) -> Dict[str, Dict[str, Any]]:
    probes = {
        name: dict(probe)
        for name, probe in DEFAULT_PARENT_CLASS_PROBES.items()
    }
    if overrides:
        for name, probe in overrides.items():
            probes[name] = {**probes.get(name, {}), **dict(probe)}
    return probes


def build_broader_non_actor_live_readonly_preflight_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    preflight_marker: str = DEFAULT_PREFLIGHT_MARKER,
    correct_project_loaded: bool = True,
    read_only_preflight_attempted: bool = True,
    read_only_preflight_executed: bool = True,
    factory_classes: Mapping[str, bool] | None = None,
    parent_class_probes: Mapping[str, Mapping[str, Any]] | None = None,
    dirty_content_before: Sequence[str] = (),
    dirty_content_after: Sequence[str] = (),
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
    actual_non_actor_blueprint_authoring_allowed: bool = False,
    user_widget_blueprint_create_command_dispatched: bool = False,
    user_widget_blueprint_create_command_executed: bool = False,
    data_asset_blueprint_create_command_dispatched: bool = False,
    data_asset_blueprint_create_command_executed: bool = False,
    anim_blueprint_create_command_dispatched: bool = False,
    anim_blueprint_create_command_executed: bool = False,
    non_actor_blueprint_creation_command_dispatched: bool = False,
    non_actor_blueprint_creation_command_executed: bool = False,
    widget_tree_mutation_performed: bool = False,
    data_asset_default_mutation_performed: bool = False,
    animation_graph_mutation_performed: bool = False,
    non_actor_blueprint_compile_dispatched: bool = False,
    non_actor_blueprint_compile_executed: bool = False,
    non_actor_blueprint_save_dispatched: bool = False,
    non_actor_blueprint_save_executed: bool = False,
    non_actor_blueprint_asset_write_performed: bool = False,
    non_actor_blueprint_package_dirty_marked: bool = False,
    compile_executed: bool = False,
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
        "schema": BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_RESULT_SCHEMA,
        "project_file_path": project_file_path,
        "preflight_marker": preflight_marker,
        "correct_project_loaded": correct_project_loaded,
        "read_only_preflight_attempted": read_only_preflight_attempted,
        "read_only_preflight_executed": read_only_preflight_executed,
        "factory_classes": _factory_map(factory_classes),
        "parent_class_probes": _parent_probe_map(parent_class_probes),
        "dirty_content_before": list(dirty_content_before),
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_preserved": external_dirty_preserved,
        "actual_non_actor_blueprint_authoring_allowed": (
            actual_non_actor_blueprint_authoring_allowed
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
        "non_actor_blueprint_creation_command_dispatched": (
            non_actor_blueprint_creation_command_dispatched
        ),
        "non_actor_blueprint_creation_command_executed": (
            non_actor_blueprint_creation_command_executed
        ),
        "widget_tree_mutation_performed": widget_tree_mutation_performed,
        "data_asset_default_mutation_performed": (
            data_asset_default_mutation_performed
        ),
        "animation_graph_mutation_performed": animation_graph_mutation_performed,
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
        "compile_executed": compile_executed,
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


def _parent_probe_loaded(
    parent_class_probes: Mapping[str, Mapping[str, Any]],
    name: str,
) -> bool:
    expected = DEFAULT_PARENT_CLASS_PROBES[name]
    probe = parent_class_probes.get(name, {})
    return bool(
        probe.get("loaded")
        and probe.get("path") == expected["path"]
        and probe.get("class_name") == expected["class_name"]
    )


def build_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract(
    requested: bool,
    section_369_376_correct_project_live_mcp_route_preflight_summary: Dict[str, Any],
    broader_non_actor_live_readonly_preflight_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_369_376_summary_schema_matches = bool(
        section_369_376_correct_project_live_mcp_route_preflight_summary.get(
            "schema"
        )
        == SECTION_369_376_CORRECT_PROJECT_LIVE_MCP_ROUTE_PREFLIGHT_SUMMARY_SCHEMA
    )
    section_369_376_summary_passed = bool(
        section_369_376_correct_project_live_mcp_route_preflight_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_correct_project_live_route_preflight_ready = all(
        _count_is_one(
            section_369_376_correct_project_live_mcp_route_preflight_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_369_376_correct_project_live_mcp_route_preflight_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        broader_non_actor_live_readonly_preflight_result.get("schema")
        == BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_369_376_summary_schema_matches
        and section_369_376_summary_passed
        and upstream_correct_project_live_route_preflight_ready
        and upstream_outputs_closed
    )
    headless_readonly_probe_recorded = bool(
        broader_non_actor_live_readonly_preflight_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and broader_non_actor_live_readonly_preflight_result.get(
            "correct_project_loaded"
        )
        and broader_non_actor_live_readonly_preflight_result.get(
            "read_only_preflight_attempted"
        )
        and broader_non_actor_live_readonly_preflight_result.get(
            "read_only_preflight_executed"
        )
        and broader_non_actor_live_readonly_preflight_result.get(
            "preflight_marker"
        )
        == DEFAULT_PREFLIGHT_MARKER
    )
    factory_classes = dict(
        broader_non_actor_live_readonly_preflight_result.get(
            "factory_classes", {}
        )
        or {}
    )
    parent_class_probes = dict(
        broader_non_actor_live_readonly_preflight_result.get(
            "parent_class_probes", {}
        )
        or {}
    )
    non_actor_factory_prerequisites_verified = all(
        factory_classes.get(factory_name)
        for factory_name in DEFAULT_FACTORY_CLASSES
    )
    user_widget_readonly_prerequisites_verified = bool(
        factory_classes.get("WidgetBlueprintFactory")
        and _parent_probe_loaded(parent_class_probes, "UserWidget")
    )
    data_asset_readonly_prerequisites_verified = bool(
        factory_classes.get("BlueprintFactory")
        and _parent_probe_loaded(parent_class_probes, "PrimaryDataAsset")
    )
    anim_blueprint_readonly_prerequisites_verified = bool(
        factory_classes.get("AnimBlueprintFactory")
        and _parent_probe_loaded(parent_class_probes, "AnimInstance")
    )
    creation_mutation_outputs_blocked = bool(
        not broader_non_actor_live_readonly_preflight_result.get(
            "actual_non_actor_blueprint_authoring_allowed"
        )
        and all(
            not broader_non_actor_live_readonly_preflight_result.get(key)
            for key in BLOCKED_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_RESULT_KEYS
        )
    )
    no_write_boundary_verified = bool(
        creation_mutation_outputs_blocked
        and broader_non_actor_live_readonly_preflight_result.get(
            "dirty_content_before"
        )
        == broader_non_actor_live_readonly_preflight_result.get(
            "dirty_content_after"
        )
        and broader_non_actor_live_readonly_preflight_result.get(
            "dirty_maps_before"
        )
        == broader_non_actor_live_readonly_preflight_result.get(
            "dirty_maps_after"
        )
        and not broader_non_actor_live_readonly_preflight_result.get(
            "dirty_content_after"
        )
        and not broader_non_actor_live_readonly_preflight_result.get(
            "dirty_maps_after"
        )
        and broader_non_actor_live_readonly_preflight_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        broader_non_actor_live_readonly_preflight_result.get("error")
        in (None, "")
    )
    preflight_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and headless_readonly_probe_recorded
        and non_actor_factory_prerequisites_verified
        and user_widget_readonly_prerequisites_verified
        and data_asset_readonly_prerequisites_verified
        and anim_blueprint_readonly_prerequisites_verified
        and creation_mutation_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_369_376_summary_schema_matches": (
            section_369_376_summary_schema_matches
        ),
        "section_369_376_summary_passed": section_369_376_summary_passed,
        "section_369_376_correct_project_live_route_preflight_ready": (
            upstream_correct_project_live_route_preflight_ready
        ),
        "section_369_376_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "broader_non_actor_live_readonly_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "correct_project_headless_non_actor_readonly_probe_recorded": (
            headless_readonly_probe_recorded
        ),
        "non_actor_factory_prerequisites_verified": (
            non_actor_factory_prerequisites_verified
        ),
        "user_widget_readonly_prerequisites_verified": (
            user_widget_readonly_prerequisites_verified
        ),
        "data_asset_readonly_prerequisites_verified": (
            data_asset_readonly_prerequisites_verified
        ),
        "anim_blueprint_readonly_prerequisites_verified": (
            anim_blueprint_readonly_prerequisites_verified
        ),
        "non_actor_creation_mutation_outputs_blocked": (
            creation_mutation_outputs_blocked
        ),
        "broader_non_actor_live_readonly_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_377_broader_non_actor_live_readonly_checkpoint_satisfied": (
            preflight_ready
        ),
        "section_378_correct_project_headless_non_actor_readonly_probe_recorded": (
            preflight_ready
        ),
        "section_379_user_widget_readonly_prerequisites_verified": (
            preflight_ready
        ),
        "section_380_data_asset_readonly_prerequisites_verified": (
            preflight_ready
        ),
        "section_381_anim_blueprint_readonly_prerequisites_verified": (
            preflight_ready
        ),
        "section_382_non_actor_creation_mutation_outputs_blocked": (
            preflight_ready
        ),
        "section_383_broader_non_actor_live_readonly_no_write_boundary_verified": (
            preflight_ready
        ),
        "section_384_broader_non_actor_live_readonly_preflight_release_ready": (
            preflight_ready
        ),
        "broader_non_actor_live_readonly_preflight_ready": preflight_ready,
        "broader_non_actor_actual_authoring_still_blocked": preflight_ready,
        "final_durable_release_ready": preflight_ready,
        **{
            key: 1 if preflight_ready else 0
            for key in BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in (
                BLOCKED_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS
            )
        },
    }


def summarize_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "broader_non_actor_live_readonly_preflight_ready"
            )
            == len(requested)
            and _truthy_count(
                requested, "broader_non_actor_actual_authoring_still_blocked"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_broader_non_actor_live_readonly_preflight_batch_count": (
            len(requested)
        ),
        "section_369_376_summary_schema_matches_count": _truthy_count(
            requested, "section_369_376_summary_schema_matches"
        ),
        "section_369_376_summary_passed_count": _truthy_count(
            requested, "section_369_376_summary_passed"
        ),
        "section_369_376_correct_project_live_route_preflight_ready_count": (
            _truthy_count(
                requested,
                "section_369_376_correct_project_live_route_preflight_ready",
            )
        ),
        "section_369_376_outputs_closed_count": _truthy_count(
            requested, "section_369_376_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "broader_non_actor_live_readonly_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "broader_non_actor_live_readonly_checkpoint_satisfied",
            )
        ),
        "correct_project_headless_non_actor_readonly_probe_recorded_count": (
            _truthy_count(
                requested,
                "correct_project_headless_non_actor_readonly_probe_recorded",
            )
        ),
        "non_actor_factory_prerequisites_verified_count": _truthy_count(
            requested, "non_actor_factory_prerequisites_verified"
        ),
        "user_widget_readonly_prerequisites_verified_count": _truthy_count(
            requested, "user_widget_readonly_prerequisites_verified"
        ),
        "data_asset_readonly_prerequisites_verified_count": _truthy_count(
            requested, "data_asset_readonly_prerequisites_verified"
        ),
        "anim_blueprint_readonly_prerequisites_verified_count": _truthy_count(
            requested, "anim_blueprint_readonly_prerequisites_verified"
        ),
        "non_actor_creation_mutation_outputs_blocked_count": _truthy_count(
            requested, "non_actor_creation_mutation_outputs_blocked"
        ),
        "broader_non_actor_live_readonly_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "broader_non_actor_live_readonly_no_write_boundary_verified",
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
            for key in BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in (
                BLOCKED_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS
            )
        }
    )
    return summary
