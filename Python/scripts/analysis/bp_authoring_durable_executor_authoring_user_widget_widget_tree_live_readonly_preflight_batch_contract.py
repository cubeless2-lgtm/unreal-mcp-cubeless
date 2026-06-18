#!/usr/bin/env python
"""
Sections 393-400 durable executor UserWidget widget-tree live read-only preflight.

This contract follows the broader non-Actor live authoring admission dry-run.
It records a correct-project headless Unreal read-only probe for WidgetBlueprint,
WidgetBlueprintFactory, UserWidget, WidgetTree, and basic UMG widget classes.
Actual Widget Blueprint creation, root widget creation, child widget addition,
slot/binding mutation, compile, save, delete, rename, overwrite, cleanup, and
production writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

import bp_authoring_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract as admission
import project_paths


DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_LIVE_READONLY_PREFLIGHT_BATCH_SCHEMA = (
    "section_393_400_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_LIVE_READONLY_PREFLIGHT_BATCH_SUMMARY_SCHEMA = (
    "section_393_400_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_summary_v1"
)
USER_WIDGET_WIDGET_TREE_LIVE_READONLY_PREFLIGHT_RESULT_SCHEMA = (
    "section_393_400_user_widget_widget_tree_live_readonly_preflight_result_v1"
)
SECTION_385_392_NON_ACTOR_ADMISSION_DRY_RUN_SUMMARY_SCHEMA = (
    admission
    .DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_BATCH_SUMMARY_SCHEMA
)
DEFAULT_PROJECT_FILE_PATH = project_paths.default_cubeless_uproject()
DEFAULT_PREFLIGHT_MARKER = "CODEX_SECTION_393_USER_WIDGET_READONLY_PREFLIGHT"
DEFAULT_CLASS_PROBES = {
    "WidgetBlueprint": {
        "path": "/Script/UMGEditor.WidgetBlueprint",
        "class_name": "WidgetBlueprint",
        "loaded": True,
    },
    "WidgetBlueprintFactory": {
        "path": "/Script/UMGEditor.WidgetBlueprintFactory",
        "class_name": "WidgetBlueprintFactory",
        "loaded": True,
    },
    "UserWidget": {
        "path": "/Script/UMG.UserWidget",
        "class_name": "UserWidget",
        "loaded": True,
    },
    "WidgetTree": {
        "path": "/Script/UMG.WidgetTree",
        "class_name": "WidgetTree",
        "loaded": True,
    },
    "CanvasPanel": {
        "path": "/Script/UMG.CanvasPanel",
        "class_name": "CanvasPanel",
        "loaded": True,
    },
    "Button": {
        "path": "/Script/UMG.Button",
        "class_name": "Button",
        "loaded": True,
    },
    "TextBlock": {
        "path": "/Script/UMG.TextBlock",
        "class_name": "TextBlock",
        "loaded": True,
    },
}
WIDGET_BLUEPRINT_PREREQUISITE_CLASSES = (
    "WidgetBlueprint",
    "WidgetBlueprintFactory",
    "UserWidget",
    "WidgetTree",
)
ROOT_WIDGET_PREREQUISITE_CLASSES = (
    "CanvasPanel",
    "Button",
    "TextBlock",
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_count",
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
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    admission
    .BLOCKED_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_OUTPUT_COUNT_KEYS
)

USER_WIDGET_WIDGET_TREE_LIVE_READONLY_PREFLIGHT_PATH_COUNT_KEYS = (
    "section_393_user_widget_widget_tree_checkpoint_satisfied_count",
    "section_394_correct_project_user_widget_readonly_probe_recorded_count",
    "section_395_widget_blueprint_prerequisites_verified_count",
    "section_396_root_widget_control_prerequisites_verified_count",
    "section_397_widget_tree_creation_mutation_outputs_blocked_count",
    "section_398_widget_compile_save_write_outputs_blocked_count",
    "section_399_user_widget_widget_tree_no_write_boundary_verified_count",
    "section_400_user_widget_widget_tree_live_readonly_preflight_release_ready_count",
    "user_widget_widget_tree_live_readonly_preflight_ready_count",
    "user_widget_widget_tree_actual_authoring_still_blocked_count",
)
BLOCKED_USER_WIDGET_WIDGET_TREE_PREFLIGHT_OUTPUT_COUNT_KEYS = (
    "widget_blueprint_create_command_dispatched_count",
    "widget_blueprint_create_command_executed_count",
    "widget_tree_mutation_performed_count",
    "root_widget_created_count",
    "child_widget_added_count",
    "widget_slot_mutation_performed_count",
    "widget_binding_mutation_performed_count",
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
BLOCKED_USER_WIDGET_WIDGET_TREE_PREFLIGHT_RESULT_KEYS = (
    "widget_blueprint_create_command_dispatched",
    "widget_blueprint_create_command_executed",
    "widget_tree_mutation_performed",
    "root_widget_created",
    "child_widget_added",
    "widget_slot_mutation_performed",
    "widget_binding_mutation_performed",
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


def _class_probe_map(
    overrides: Mapping[str, Mapping[str, Any]] | None = None,
) -> Dict[str, Dict[str, Any]]:
    probes = {
        name: dict(probe)
        for name, probe in DEFAULT_CLASS_PROBES.items()
    }
    if overrides:
        for name, probe in overrides.items():
            probes[name] = {**probes.get(name, {}), **dict(probe)}
    return probes


def build_user_widget_widget_tree_live_readonly_preflight_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    preflight_marker: str = DEFAULT_PREFLIGHT_MARKER,
    read_only_preflight_attempted: bool = True,
    read_only_preflight_executed: bool = True,
    class_probes: Mapping[str, Mapping[str, Any]] | None = None,
    dirty_content_before: Sequence[str] = (),
    dirty_content_after: Sequence[str] = (),
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
    widget_blueprint_create_command_dispatched: bool = False,
    widget_blueprint_create_command_executed: bool = False,
    widget_tree_mutation_performed: bool = False,
    root_widget_created: bool = False,
    child_widget_added: bool = False,
    widget_slot_mutation_performed: bool = False,
    widget_binding_mutation_performed: bool = False,
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
        "schema": USER_WIDGET_WIDGET_TREE_LIVE_READONLY_PREFLIGHT_RESULT_SCHEMA,
        "project_file_path": project_file_path,
        "preflight_marker": preflight_marker,
        "read_only_preflight_attempted": read_only_preflight_attempted,
        "read_only_preflight_executed": read_only_preflight_executed,
        "class_probes": _class_probe_map(class_probes),
        "dirty_content_before": list(dirty_content_before),
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_preserved": external_dirty_preserved,
        "widget_blueprint_create_command_dispatched": (
            widget_blueprint_create_command_dispatched
        ),
        "widget_blueprint_create_command_executed": (
            widget_blueprint_create_command_executed
        ),
        "widget_tree_mutation_performed": widget_tree_mutation_performed,
        "root_widget_created": root_widget_created,
        "child_widget_added": child_widget_added,
        "widget_slot_mutation_performed": widget_slot_mutation_performed,
        "widget_binding_mutation_performed": widget_binding_mutation_performed,
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


def _class_probe_loaded(
    class_probes: Mapping[str, Mapping[str, Any]],
    name: str,
) -> bool:
    expected = DEFAULT_CLASS_PROBES[name]
    probe = class_probes.get(name, {})
    return bool(
        probe.get("loaded")
        and probe.get("path") == expected["path"]
        and probe.get("class_name") == expected["class_name"]
    )


def build_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract(
    requested: bool,
    section_385_392_non_actor_admission_dry_run_summary: Dict[str, Any],
    user_widget_widget_tree_live_readonly_preflight_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_385_392_summary_schema_matches = bool(
        section_385_392_non_actor_admission_dry_run_summary.get("schema")
        == SECTION_385_392_NON_ACTOR_ADMISSION_DRY_RUN_SUMMARY_SCHEMA
    )
    section_385_392_summary_passed = bool(
        section_385_392_non_actor_admission_dry_run_summary.get("status")
        == "passed"
    )
    upstream_admission_dry_run_ready = all(
        _count_is_one(
            section_385_392_non_actor_admission_dry_run_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_385_392_non_actor_admission_dry_run_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        user_widget_widget_tree_live_readonly_preflight_result.get("schema")
        == USER_WIDGET_WIDGET_TREE_LIVE_READONLY_PREFLIGHT_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_385_392_summary_schema_matches
        and section_385_392_summary_passed
        and upstream_admission_dry_run_ready
        and upstream_outputs_closed
    )
    readonly_probe_recorded = bool(
        user_widget_widget_tree_live_readonly_preflight_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and user_widget_widget_tree_live_readonly_preflight_result.get(
            "preflight_marker"
        )
        == DEFAULT_PREFLIGHT_MARKER
        and user_widget_widget_tree_live_readonly_preflight_result.get(
            "read_only_preflight_attempted"
        )
        and user_widget_widget_tree_live_readonly_preflight_result.get(
            "read_only_preflight_executed"
        )
    )
    class_probes = dict(
        user_widget_widget_tree_live_readonly_preflight_result.get(
            "class_probes", {}
        )
        or {}
    )
    widget_blueprint_prerequisites_verified = all(
        _class_probe_loaded(class_probes, name)
        for name in WIDGET_BLUEPRINT_PREREQUISITE_CLASSES
    )
    root_widget_control_prerequisites_verified = all(
        _class_probe_loaded(class_probes, name)
        for name in ROOT_WIDGET_PREREQUISITE_CLASSES
    )
    widget_tree_creation_mutation_outputs_blocked = all(
        not user_widget_widget_tree_live_readonly_preflight_result.get(key)
        for key in (
            "widget_blueprint_create_command_dispatched",
            "widget_blueprint_create_command_executed",
            "widget_tree_mutation_performed",
            "root_widget_created",
            "child_widget_added",
            "widget_slot_mutation_performed",
            "widget_binding_mutation_performed",
        )
    )
    compile_save_write_outputs_blocked = all(
        not user_widget_widget_tree_live_readonly_preflight_result.get(key)
        for key in (
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
    )
    all_outputs_blocked = all(
        not user_widget_widget_tree_live_readonly_preflight_result.get(key)
        for key in BLOCKED_USER_WIDGET_WIDGET_TREE_PREFLIGHT_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        all_outputs_blocked
        and user_widget_widget_tree_live_readonly_preflight_result.get(
            "dirty_content_before"
        )
        == user_widget_widget_tree_live_readonly_preflight_result.get(
            "dirty_content_after"
        )
        and user_widget_widget_tree_live_readonly_preflight_result.get(
            "dirty_maps_before"
        )
        == user_widget_widget_tree_live_readonly_preflight_result.get(
            "dirty_maps_after"
        )
        and not user_widget_widget_tree_live_readonly_preflight_result.get(
            "dirty_content_after"
        )
        and not user_widget_widget_tree_live_readonly_preflight_result.get(
            "dirty_maps_after"
        )
        and user_widget_widget_tree_live_readonly_preflight_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        user_widget_widget_tree_live_readonly_preflight_result.get("error")
        in (None, "")
    )
    preflight_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and readonly_probe_recorded
        and widget_blueprint_prerequisites_verified
        and root_widget_control_prerequisites_verified
        and widget_tree_creation_mutation_outputs_blocked
        and compile_save_write_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_LIVE_READONLY_PREFLIGHT_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_385_392_summary_schema_matches": (
            section_385_392_summary_schema_matches
        ),
        "section_385_392_summary_passed": section_385_392_summary_passed,
        "section_385_392_non_actor_admission_dry_run_ready": (
            upstream_admission_dry_run_ready
        ),
        "section_385_392_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "user_widget_widget_tree_checkpoint_satisfied": checkpoint_satisfied,
        "correct_project_user_widget_readonly_probe_recorded": (
            readonly_probe_recorded
        ),
        "widget_blueprint_prerequisites_verified": (
            widget_blueprint_prerequisites_verified
        ),
        "root_widget_control_prerequisites_verified": (
            root_widget_control_prerequisites_verified
        ),
        "widget_tree_creation_mutation_outputs_blocked": (
            widget_tree_creation_mutation_outputs_blocked
        ),
        "widget_compile_save_write_outputs_blocked": (
            compile_save_write_outputs_blocked
        ),
        "user_widget_widget_tree_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_393_user_widget_widget_tree_checkpoint_satisfied": (
            preflight_ready
        ),
        "section_394_correct_project_user_widget_readonly_probe_recorded": (
            preflight_ready
        ),
        "section_395_widget_blueprint_prerequisites_verified": preflight_ready,
        "section_396_root_widget_control_prerequisites_verified": (
            preflight_ready
        ),
        "section_397_widget_tree_creation_mutation_outputs_blocked": (
            preflight_ready
        ),
        "section_398_widget_compile_save_write_outputs_blocked": (
            preflight_ready
        ),
        "section_399_user_widget_widget_tree_no_write_boundary_verified": (
            preflight_ready
        ),
        "section_400_user_widget_widget_tree_live_readonly_preflight_release_ready": (
            preflight_ready
        ),
        "user_widget_widget_tree_live_readonly_preflight_ready": preflight_ready,
        "user_widget_widget_tree_actual_authoring_still_blocked": (
            preflight_ready
        ),
        "final_durable_release_ready": preflight_ready,
        **{
            key: 1 if preflight_ready else 0
            for key in USER_WIDGET_WIDGET_TREE_LIVE_READONLY_PREFLIGHT_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_USER_WIDGET_WIDGET_TREE_PREFLIGHT_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "user_widget_widget_tree_live_readonly_preflight_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "user_widget_widget_tree_actual_authoring_still_blocked",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_USER_WIDGET_WIDGET_TREE_PREFLIGHT_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_LIVE_READONLY_PREFLIGHT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_count": (
            len(requested)
        ),
        "section_385_392_summary_schema_matches_count": _truthy_count(
            requested, "section_385_392_summary_schema_matches"
        ),
        "section_385_392_summary_passed_count": _truthy_count(
            requested, "section_385_392_summary_passed"
        ),
        "section_385_392_non_actor_admission_dry_run_ready_count": (
            _truthy_count(
                requested, "section_385_392_non_actor_admission_dry_run_ready"
            )
        ),
        "section_385_392_outputs_closed_count": _truthy_count(
            requested, "section_385_392_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "user_widget_widget_tree_checkpoint_satisfied_count": _truthy_count(
            requested, "user_widget_widget_tree_checkpoint_satisfied"
        ),
        "correct_project_user_widget_readonly_probe_recorded_count": (
            _truthy_count(
                requested,
                "correct_project_user_widget_readonly_probe_recorded",
            )
        ),
        "widget_blueprint_prerequisites_verified_count": _truthy_count(
            requested, "widget_blueprint_prerequisites_verified"
        ),
        "root_widget_control_prerequisites_verified_count": _truthy_count(
            requested, "root_widget_control_prerequisites_verified"
        ),
        "widget_tree_creation_mutation_outputs_blocked_count": _truthy_count(
            requested, "widget_tree_creation_mutation_outputs_blocked"
        ),
        "widget_compile_save_write_outputs_blocked_count": _truthy_count(
            requested, "widget_compile_save_write_outputs_blocked"
        ),
        "user_widget_widget_tree_no_write_boundary_verified_count": (
            _truthy_count(
                requested, "user_widget_widget_tree_no_write_boundary_verified"
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
            for key in USER_WIDGET_WIDGET_TREE_LIVE_READONLY_PREFLIGHT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_USER_WIDGET_WIDGET_TREE_PREFLIGHT_OUTPUT_COUNT_KEYS
        }
    )
    return summary
