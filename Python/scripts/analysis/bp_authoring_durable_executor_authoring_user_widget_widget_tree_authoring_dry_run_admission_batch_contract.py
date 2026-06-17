#!/usr/bin/env python
"""
Sections 401-408 durable executor UserWidget widget-tree authoring dry-run admission.

This contract follows the UserWidget widget-tree live read-only preflight. It
admits only an offline dry-run plan for a disposable Widget Blueprint under
_MCP_Temp. The plan records the parent class, root widget, child widgets, slot
layout, and binding/event-graph blockers. Actual Widget Blueprint creation,
widget tree mutation, graph/binding mutation, compile, save, delete, rename,
overwrite, cleanup, and production writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract as widget_preflight


DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_AUTHORING_DRY_RUN_ADMISSION_BATCH_SCHEMA = (
    "section_401_408_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_AUTHORING_DRY_RUN_ADMISSION_BATCH_SUMMARY_SCHEMA = (
    "section_401_408_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_summary_v1"
)
USER_WIDGET_WIDGET_TREE_AUTHORING_DRY_RUN_ADMISSION_RESULT_SCHEMA = (
    "section_401_408_user_widget_widget_tree_authoring_dry_run_admission_result_v1"
)
SECTION_393_400_USER_WIDGET_WIDGET_TREE_PREFLIGHT_SUMMARY_SCHEMA = (
    widget_preflight
    .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_LIVE_READONLY_PREFLIGHT_BATCH_SUMMARY_SCHEMA
)
DEFAULT_DRY_RUN_ROOT = "/Game/_MCP_Temp/DurableSaveGate/UserWidgetDryRun"
DEFAULT_TARGET_ASSET_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/UserWidgetDryRun/WBP_DurableWidgetTreeDryRun"
)
DEFAULT_PARENT_CLASS = "UserWidget"
DEFAULT_ROOT_WIDGET_CLASS = "CanvasPanel"
DEFAULT_CHILD_WIDGET_CLASSES = ("Button", "TextBlock")
DEFAULT_SLOT_LAYOUT_PLAN = (
    "CanvasPanelSlot/Button:anchors=top_left,position=(64,64),size=(240,64)",
    "CanvasPanelSlot/TextBlock:anchors=top_left,position=(80,80),auto_size=true",
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_count",
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
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    widget_preflight
    .BLOCKED_USER_WIDGET_WIDGET_TREE_PREFLIGHT_OUTPUT_COUNT_KEYS
)

USER_WIDGET_WIDGET_TREE_AUTHORING_DRY_RUN_ADMISSION_PATH_COUNT_KEYS = (
    "section_401_user_widget_authoring_dry_run_checkpoint_satisfied_count",
    "section_402_widget_blueprint_dry_run_scope_verified_count",
    "section_403_root_widget_plan_classified_count",
    "section_404_child_widget_slot_plan_classified_count",
    "section_405_widget_binding_event_graph_plan_blocked_count",
    "section_406_widget_authoring_creation_mutation_outputs_blocked_count",
    "section_407_user_widget_authoring_dry_run_no_write_boundary_verified_count",
    "section_408_user_widget_authoring_dry_run_admission_release_ready_count",
    "user_widget_widget_tree_authoring_dry_run_admission_ready_count",
    "user_widget_widget_tree_actual_authoring_still_blocked_count",
)
BLOCKED_USER_WIDGET_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS = (
    "widget_blueprint_authoring_admission_command_dispatched_count",
    "widget_blueprint_authoring_admission_command_executed_count",
    "widget_blueprint_create_command_dispatched_count",
    "widget_blueprint_create_command_executed_count",
    "widget_tree_mutation_command_dispatched_count",
    "widget_tree_mutation_command_executed_count",
    "root_widget_created_count",
    "child_widget_added_count",
    "widget_slot_mutation_performed_count",
    "widget_binding_mutation_performed_count",
    "event_graph_mutation_performed_count",
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
BLOCKED_USER_WIDGET_AUTHORING_DRY_RUN_RESULT_KEYS = (
    "widget_blueprint_authoring_admission_command_dispatched",
    "widget_blueprint_authoring_admission_command_executed",
    "widget_blueprint_create_command_dispatched",
    "widget_blueprint_create_command_executed",
    "widget_tree_mutation_command_dispatched",
    "widget_tree_mutation_command_executed",
    "root_widget_created",
    "child_widget_added",
    "widget_slot_mutation_performed",
    "widget_binding_mutation_performed",
    "event_graph_mutation_performed",
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


def build_user_widget_widget_tree_authoring_dry_run_admission_result(
    *,
    dry_run_only: bool = True,
    dry_run_root: str = DEFAULT_DRY_RUN_ROOT,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    parent_class: str = DEFAULT_PARENT_CLASS,
    root_widget_class: str = DEFAULT_ROOT_WIDGET_CLASS,
    child_widget_classes: Sequence[str] = DEFAULT_CHILD_WIDGET_CLASSES,
    slot_layout_plan: Sequence[str] = DEFAULT_SLOT_LAYOUT_PLAN,
    binding_plan_recorded: bool = True,
    event_graph_mutation_requires_separate_contract: bool = True,
    widget_binding_event_graph_plan_blocked: bool = True,
    actual_widget_blueprint_authoring_allowed: bool = False,
    dirty_content_after_dry_run: Sequence[str] = (),
    dirty_maps_after_dry_run: Sequence[str] = (),
    widget_blueprint_authoring_admission_command_dispatched: bool = False,
    widget_blueprint_authoring_admission_command_executed: bool = False,
    widget_blueprint_create_command_dispatched: bool = False,
    widget_blueprint_create_command_executed: bool = False,
    widget_tree_mutation_command_dispatched: bool = False,
    widget_tree_mutation_command_executed: bool = False,
    root_widget_created: bool = False,
    child_widget_added: bool = False,
    widget_slot_mutation_performed: bool = False,
    widget_binding_mutation_performed: bool = False,
    event_graph_mutation_performed: bool = False,
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
        "schema": USER_WIDGET_WIDGET_TREE_AUTHORING_DRY_RUN_ADMISSION_RESULT_SCHEMA,
        "dry_run_only": dry_run_only,
        "dry_run_root": dry_run_root,
        "target_asset_path": target_asset_path,
        "parent_class": parent_class,
        "root_widget_class": root_widget_class,
        "child_widget_classes": list(child_widget_classes),
        "slot_layout_plan": list(slot_layout_plan),
        "binding_plan_recorded": binding_plan_recorded,
        "event_graph_mutation_requires_separate_contract": (
            event_graph_mutation_requires_separate_contract
        ),
        "widget_binding_event_graph_plan_blocked": (
            widget_binding_event_graph_plan_blocked
        ),
        "actual_widget_blueprint_authoring_allowed": (
            actual_widget_blueprint_authoring_allowed
        ),
        "dirty_content_after_dry_run": list(dirty_content_after_dry_run),
        "dirty_maps_after_dry_run": list(dirty_maps_after_dry_run),
        "widget_blueprint_authoring_admission_command_dispatched": (
            widget_blueprint_authoring_admission_command_dispatched
        ),
        "widget_blueprint_authoring_admission_command_executed": (
            widget_blueprint_authoring_admission_command_executed
        ),
        "widget_blueprint_create_command_dispatched": (
            widget_blueprint_create_command_dispatched
        ),
        "widget_blueprint_create_command_executed": (
            widget_blueprint_create_command_executed
        ),
        "widget_tree_mutation_command_dispatched": (
            widget_tree_mutation_command_dispatched
        ),
        "widget_tree_mutation_command_executed": (
            widget_tree_mutation_command_executed
        ),
        "root_widget_created": root_widget_created,
        "child_widget_added": child_widget_added,
        "widget_slot_mutation_performed": widget_slot_mutation_performed,
        "widget_binding_mutation_performed": widget_binding_mutation_performed,
        "event_graph_mutation_performed": event_graph_mutation_performed,
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


def build_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract(
    requested: bool,
    section_393_400_user_widget_widget_tree_preflight_summary: Dict[str, Any],
    user_widget_widget_tree_authoring_dry_run_admission_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_393_400_summary_schema_matches = bool(
        section_393_400_user_widget_widget_tree_preflight_summary.get("schema")
        == SECTION_393_400_USER_WIDGET_WIDGET_TREE_PREFLIGHT_SUMMARY_SCHEMA
    )
    section_393_400_summary_passed = bool(
        section_393_400_user_widget_widget_tree_preflight_summary.get("status")
        == "passed"
    )
    upstream_preflight_ready = all(
        _count_is_one(
            section_393_400_user_widget_widget_tree_preflight_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_393_400_user_widget_widget_tree_preflight_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        user_widget_widget_tree_authoring_dry_run_admission_result.get("schema")
        == USER_WIDGET_WIDGET_TREE_AUTHORING_DRY_RUN_ADMISSION_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_393_400_summary_schema_matches
        and section_393_400_summary_passed
        and upstream_preflight_ready
        and upstream_outputs_closed
    )
    dry_run_scope_verified = bool(
        user_widget_widget_tree_authoring_dry_run_admission_result.get(
            "dry_run_only"
        )
        and user_widget_widget_tree_authoring_dry_run_admission_result.get(
            "dry_run_root"
        )
        == DEFAULT_DRY_RUN_ROOT
        and user_widget_widget_tree_authoring_dry_run_admission_result.get(
            "target_asset_path"
        )
        == DEFAULT_TARGET_ASSET_PATH
        and str(
            user_widget_widget_tree_authoring_dry_run_admission_result.get(
                "target_asset_path", ""
            )
        ).startswith("/Game/_MCP_Temp/")
        and user_widget_widget_tree_authoring_dry_run_admission_result.get(
            "parent_class"
        )
        == DEFAULT_PARENT_CLASS
        and not user_widget_widget_tree_authoring_dry_run_admission_result.get(
            "actual_widget_blueprint_authoring_allowed"
        )
    )
    root_widget_plan_classified = bool(
        user_widget_widget_tree_authoring_dry_run_admission_result.get(
            "root_widget_class"
        )
        == DEFAULT_ROOT_WIDGET_CLASS
    )
    child_widget_slot_plan_classified = bool(
        tuple(
            user_widget_widget_tree_authoring_dry_run_admission_result.get(
                "child_widget_classes", ()
            )
            or ()
        )
        == DEFAULT_CHILD_WIDGET_CLASSES
        and tuple(
            user_widget_widget_tree_authoring_dry_run_admission_result.get(
                "slot_layout_plan", ()
            )
            or ()
        )
        == DEFAULT_SLOT_LAYOUT_PLAN
    )
    binding_event_graph_plan_blocked = bool(
        user_widget_widget_tree_authoring_dry_run_admission_result.get(
            "binding_plan_recorded"
        )
        and user_widget_widget_tree_authoring_dry_run_admission_result.get(
            "event_graph_mutation_requires_separate_contract"
        )
        and user_widget_widget_tree_authoring_dry_run_admission_result.get(
            "widget_binding_event_graph_plan_blocked"
        )
    )
    creation_mutation_outputs_blocked = bool(
        not user_widget_widget_tree_authoring_dry_run_admission_result.get(
            "actual_widget_blueprint_authoring_allowed"
        )
        and all(
            not user_widget_widget_tree_authoring_dry_run_admission_result.get(
                key
            )
            for key in BLOCKED_USER_WIDGET_AUTHORING_DRY_RUN_RESULT_KEYS
        )
    )
    no_write_boundary_verified = bool(
        creation_mutation_outputs_blocked
        and not user_widget_widget_tree_authoring_dry_run_admission_result.get(
            "dirty_content_after_dry_run"
        )
        and not user_widget_widget_tree_authoring_dry_run_admission_result.get(
            "dirty_maps_after_dry_run"
        )
    )
    result_has_no_error = bool(
        user_widget_widget_tree_authoring_dry_run_admission_result.get("error")
        in (None, "")
    )
    dry_run_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and dry_run_scope_verified
        and root_widget_plan_classified
        and child_widget_slot_plan_classified
        and binding_event_graph_plan_blocked
        and creation_mutation_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_AUTHORING_DRY_RUN_ADMISSION_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_393_400_summary_schema_matches": (
            section_393_400_summary_schema_matches
        ),
        "section_393_400_summary_passed": section_393_400_summary_passed,
        "section_393_400_user_widget_preflight_ready": (
            upstream_preflight_ready
        ),
        "section_393_400_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "user_widget_authoring_dry_run_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "widget_blueprint_dry_run_scope_verified": dry_run_scope_verified,
        "root_widget_plan_classified": root_widget_plan_classified,
        "child_widget_slot_plan_classified": child_widget_slot_plan_classified,
        "widget_binding_event_graph_plan_blocked": (
            binding_event_graph_plan_blocked
        ),
        "widget_authoring_creation_mutation_outputs_blocked": (
            creation_mutation_outputs_blocked
        ),
        "user_widget_authoring_dry_run_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_401_user_widget_authoring_dry_run_checkpoint_satisfied": (
            dry_run_ready
        ),
        "section_402_widget_blueprint_dry_run_scope_verified": dry_run_ready,
        "section_403_root_widget_plan_classified": dry_run_ready,
        "section_404_child_widget_slot_plan_classified": dry_run_ready,
        "section_405_widget_binding_event_graph_plan_blocked": dry_run_ready,
        "section_406_widget_authoring_creation_mutation_outputs_blocked": (
            dry_run_ready
        ),
        "section_407_user_widget_authoring_dry_run_no_write_boundary_verified": (
            dry_run_ready
        ),
        "section_408_user_widget_authoring_dry_run_admission_release_ready": (
            dry_run_ready
        ),
        "user_widget_widget_tree_authoring_dry_run_admission_ready": (
            dry_run_ready
        ),
        "user_widget_widget_tree_actual_authoring_still_blocked": (
            dry_run_ready
        ),
        "final_durable_release_ready": dry_run_ready,
        **{
            key: 1 if dry_run_ready else 0
            for key in USER_WIDGET_WIDGET_TREE_AUTHORING_DRY_RUN_ADMISSION_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_USER_WIDGET_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "user_widget_widget_tree_authoring_dry_run_admission_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "user_widget_widget_tree_actual_authoring_still_blocked",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_USER_WIDGET_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_AUTHORING_DRY_RUN_ADMISSION_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_count": (
            len(requested)
        ),
        "section_393_400_summary_schema_matches_count": _truthy_count(
            requested, "section_393_400_summary_schema_matches"
        ),
        "section_393_400_summary_passed_count": _truthy_count(
            requested, "section_393_400_summary_passed"
        ),
        "section_393_400_user_widget_preflight_ready_count": _truthy_count(
            requested, "section_393_400_user_widget_preflight_ready"
        ),
        "section_393_400_outputs_closed_count": _truthy_count(
            requested, "section_393_400_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "user_widget_authoring_dry_run_checkpoint_satisfied_count": (
            _truthy_count(
                requested, "user_widget_authoring_dry_run_checkpoint_satisfied"
            )
        ),
        "widget_blueprint_dry_run_scope_verified_count": _truthy_count(
            requested, "widget_blueprint_dry_run_scope_verified"
        ),
        "root_widget_plan_classified_count": _truthy_count(
            requested, "root_widget_plan_classified"
        ),
        "child_widget_slot_plan_classified_count": _truthy_count(
            requested, "child_widget_slot_plan_classified"
        ),
        "widget_binding_event_graph_plan_blocked_count": _truthy_count(
            requested, "widget_binding_event_graph_plan_blocked"
        ),
        "widget_authoring_creation_mutation_outputs_blocked_count": (
            _truthy_count(
                requested,
                "widget_authoring_creation_mutation_outputs_blocked",
            )
        ),
        "user_widget_authoring_dry_run_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "user_widget_authoring_dry_run_no_write_boundary_verified",
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
            for key in USER_WIDGET_WIDGET_TREE_AUTHORING_DRY_RUN_ADMISSION_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_USER_WIDGET_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
        }
    )
    return summary
