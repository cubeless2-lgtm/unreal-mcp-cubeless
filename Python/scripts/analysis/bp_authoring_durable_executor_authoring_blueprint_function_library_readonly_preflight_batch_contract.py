#!/usr/bin/env python
"""
Sections 465-472 durable executor Blueprint Function Library read-only preflight.

This contract follows the broader non-Actor live authoring admission dry-run.
It records a correct-project read-only preflight for a Blueprint Function
Library authoring route. Actual BFL creation, function graph mutation, compile,
save, delete, rename, overwrite, cleanup, and production writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Mapping, Sequence

import bp_authoring_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract as admission


DURABLE_EXECUTOR_AUTHORING_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_BATCH_SCHEMA = (
    "section_465_472_durable_executor_authoring_blueprint_function_library_readonly_preflight_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_BATCH_SUMMARY_SCHEMA = (
    "section_465_472_durable_executor_authoring_blueprint_function_library_readonly_preflight_batch_summary_v1"
)
BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_RESULT_SCHEMA = (
    "section_465_472_blueprint_function_library_readonly_preflight_result_v1"
)
SECTION_385_392_NON_ACTOR_ADMISSION_DRY_RUN_SUMMARY_SCHEMA = (
    admission
    .DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_BATCH_SUMMARY_SCHEMA
)
DEFAULT_PROJECT_FILE_PATH = "D:/Git/CubelessStylized/StylizedCubeless.uproject"
DEFAULT_PREFLIGHT_MARKER = "CODEX_SECTION_465_BFL_READONLY_PREFLIGHT"
DEFAULT_DRY_RUN_ROOT = "/Game/_MCP_Temp/DurableSaveGate/FunctionLibraryReadOnly"
DEFAULT_TARGET_ASSET_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/FunctionLibraryReadOnly/"
    "BFL_DurableFunctionLibraryReadonly"
)
DEFAULT_PARENT_CLASS = "BlueprintFunctionLibrary"
DEFAULT_FACTORY_CLASS = "BlueprintFunctionLibraryFactory"
DEFAULT_CLASS_PROBES = {
    "Blueprint": {
        "path": "/Script/Engine.Blueprint",
        "class_name": "Blueprint",
        "loaded": True,
    },
    "BlueprintFunctionLibrary": {
        "path": "/Script/Engine.BlueprintFunctionLibrary",
        "class_name": "BlueprintFunctionLibrary",
        "loaded": True,
    },
    "BlueprintFunctionLibraryFactory": {
        "path": "/Script/UnrealEd.BlueprintFunctionLibraryFactory",
        "class_name": "BlueprintFunctionLibraryFactory",
        "loaded": True,
    },
    "EdGraph": {
        "path": "/Script/Engine.EdGraph",
        "class_name": "EdGraph",
        "loaded": True,
    },
    "K2Node_FunctionEntry": {
        "path": "/Script/BlueprintGraph.K2Node_FunctionEntry",
        "class_name": "K2Node_FunctionEntry",
        "loaded": True,
    },
}

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

BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_PATH_COUNT_KEYS = (
    "section_465_blueprint_function_library_readonly_checkpoint_satisfied_count",
    "section_466_correct_project_blueprint_function_library_readonly_probe_recorded_count",
    "section_467_blueprint_function_library_factory_parent_prerequisites_verified_count",
    "section_468_blueprint_function_library_graph_prerequisites_verified_count",
    "section_469_blueprint_function_library_creation_graph_outputs_blocked_count",
    "section_470_blueprint_function_library_compile_save_write_outputs_blocked_count",
    "section_471_blueprint_function_library_readonly_no_write_boundary_verified_count",
    "section_472_blueprint_function_library_readonly_preflight_release_ready_count",
    "blueprint_function_library_readonly_preflight_ready_count",
    "blueprint_function_library_actual_authoring_still_blocked_count",
)
BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS = (
    "function_library_blueprint_create_command_dispatched_count",
    "function_library_blueprint_create_command_executed_count",
    "function_library_graph_mutation_command_dispatched_count",
    "function_library_graph_mutation_command_executed_count",
    "function_library_function_added_count",
    "function_library_function_signature_changed_count",
    "function_library_node_added_count",
    "function_library_pin_connected_count",
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
BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_RESULT_KEYS = tuple(
    key.removesuffix("_count")
    for key in BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS
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


def build_blueprint_function_library_readonly_preflight_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    preflight_marker: str = DEFAULT_PREFLIGHT_MARKER,
    read_only_preflight_attempted: bool = True,
    read_only_preflight_executed: bool = True,
    dry_run_root: str = DEFAULT_DRY_RUN_ROOT,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    parent_class: str = DEFAULT_PARENT_CLASS,
    factory_class: str = DEFAULT_FACTORY_CLASS,
    class_probes: Mapping[str, Mapping[str, Any]] | None = None,
    function_graph_readback_plan_recorded: bool = True,
    function_graph_mutation_requires_contract: bool = True,
    function_graph_mutation_blocked_pending_contract: bool = True,
    actual_function_library_authoring_allowed: bool = False,
    dirty_content_before: Sequence[str] = (),
    dirty_content_after: Sequence[str] = (),
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
    function_library_blueprint_create_command_dispatched: bool = False,
    function_library_blueprint_create_command_executed: bool = False,
    function_library_graph_mutation_command_dispatched: bool = False,
    function_library_graph_mutation_command_executed: bool = False,
    function_library_function_added: bool = False,
    function_library_function_signature_changed: bool = False,
    function_library_node_added: bool = False,
    function_library_pin_connected: bool = False,
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
        "schema": BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_RESULT_SCHEMA,
        "project_file_path": project_file_path,
        "preflight_marker": preflight_marker,
        "read_only_preflight_attempted": read_only_preflight_attempted,
        "read_only_preflight_executed": read_only_preflight_executed,
        "dry_run_root": dry_run_root,
        "target_asset_path": target_asset_path,
        "parent_class": parent_class,
        "factory_class": factory_class,
        "class_probes": _class_probe_map(class_probes),
        "function_graph_readback_plan_recorded": (
            function_graph_readback_plan_recorded
        ),
        "function_graph_mutation_requires_contract": (
            function_graph_mutation_requires_contract
        ),
        "function_graph_mutation_blocked_pending_contract": (
            function_graph_mutation_blocked_pending_contract
        ),
        "actual_function_library_authoring_allowed": (
            actual_function_library_authoring_allowed
        ),
        "dirty_content_before": list(dirty_content_before),
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_preserved": external_dirty_preserved,
        "function_library_blueprint_create_command_dispatched": (
            function_library_blueprint_create_command_dispatched
        ),
        "function_library_blueprint_create_command_executed": (
            function_library_blueprint_create_command_executed
        ),
        "function_library_graph_mutation_command_dispatched": (
            function_library_graph_mutation_command_dispatched
        ),
        "function_library_graph_mutation_command_executed": (
            function_library_graph_mutation_command_executed
        ),
        "function_library_function_added": function_library_function_added,
        "function_library_function_signature_changed": (
            function_library_function_signature_changed
        ),
        "function_library_node_added": function_library_node_added,
        "function_library_pin_connected": function_library_pin_connected,
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


def _blocked_output_counts(result: Mapping[str, Any]) -> Dict[str, int]:
    return {
        count_key: 1 if result.get(result_key) else 0
        for count_key, result_key in zip(
            BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS,
            BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_RESULT_KEYS,
        )
    }


def build_durable_executor_authoring_blueprint_function_library_readonly_preflight_batch_contract(
    requested: bool,
    section_385_392_non_actor_admission_dry_run_summary: Dict[str, Any],
    blueprint_function_library_readonly_preflight_result: Dict[str, Any],
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
        blueprint_function_library_readonly_preflight_result.get("schema")
        == BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_385_392_summary_schema_matches
        and section_385_392_summary_passed
        and upstream_admission_dry_run_ready
        and upstream_outputs_closed
    )
    readonly_probe_recorded = bool(
        blueprint_function_library_readonly_preflight_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and blueprint_function_library_readonly_preflight_result.get(
            "preflight_marker"
        )
        == DEFAULT_PREFLIGHT_MARKER
        and blueprint_function_library_readonly_preflight_result.get(
            "read_only_preflight_attempted"
        )
        and blueprint_function_library_readonly_preflight_result.get(
            "read_only_preflight_executed"
        )
    )
    target_scope_verified = bool(
        blueprint_function_library_readonly_preflight_result.get("dry_run_root")
        == DEFAULT_DRY_RUN_ROOT
        and blueprint_function_library_readonly_preflight_result.get(
            "target_asset_path"
        )
        == DEFAULT_TARGET_ASSET_PATH
        and str(
            blueprint_function_library_readonly_preflight_result.get(
                "target_asset_path", ""
            )
        ).startswith("/Game/_MCP_Temp/")
        and blueprint_function_library_readonly_preflight_result.get(
            "parent_class"
        )
        == DEFAULT_PARENT_CLASS
        and blueprint_function_library_readonly_preflight_result.get(
            "factory_class"
        )
        == DEFAULT_FACTORY_CLASS
        and not blueprint_function_library_readonly_preflight_result.get(
            "actual_function_library_authoring_allowed"
        )
    )
    class_probes = dict(
        blueprint_function_library_readonly_preflight_result.get(
            "class_probes", {}
        )
        or {}
    )
    factory_parent_prerequisites_verified = bool(
        target_scope_verified
        and all(
            _class_probe_loaded(class_probes, name)
            for name in (
                "Blueprint",
                "BlueprintFunctionLibrary",
                "BlueprintFunctionLibraryFactory",
            )
        )
    )
    graph_prerequisites_verified = bool(
        blueprint_function_library_readonly_preflight_result.get(
            "function_graph_readback_plan_recorded"
        )
        and all(
            _class_probe_loaded(class_probes, name)
            for name in ("EdGraph", "K2Node_FunctionEntry")
        )
    )
    creation_graph_outputs_blocked = bool(
        blueprint_function_library_readonly_preflight_result.get(
            "function_graph_mutation_requires_contract"
        )
        and blueprint_function_library_readonly_preflight_result.get(
            "function_graph_mutation_blocked_pending_contract"
        )
        and not blueprint_function_library_readonly_preflight_result.get(
            "actual_function_library_authoring_allowed"
        )
        and all(
            not blueprint_function_library_readonly_preflight_result.get(key)
            for key in (
                "function_library_blueprint_create_command_dispatched",
                "function_library_blueprint_create_command_executed",
                "function_library_graph_mutation_command_dispatched",
                "function_library_graph_mutation_command_executed",
                "function_library_function_added",
                "function_library_function_signature_changed",
                "function_library_node_added",
                "function_library_pin_connected",
            )
        )
    )
    compile_save_write_outputs_blocked = all(
        not blueprint_function_library_readonly_preflight_result.get(key)
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
        not blueprint_function_library_readonly_preflight_result.get(key)
        for key in BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        all_outputs_blocked
        and blueprint_function_library_readonly_preflight_result.get(
            "dirty_content_before"
        )
        == blueprint_function_library_readonly_preflight_result.get(
            "dirty_content_after"
        )
        and blueprint_function_library_readonly_preflight_result.get(
            "dirty_maps_before"
        )
        == blueprint_function_library_readonly_preflight_result.get(
            "dirty_maps_after"
        )
        and not blueprint_function_library_readonly_preflight_result.get(
            "dirty_content_after"
        )
        and not blueprint_function_library_readonly_preflight_result.get(
            "dirty_maps_after"
        )
        and blueprint_function_library_readonly_preflight_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        blueprint_function_library_readonly_preflight_result.get("error")
        in (None, "")
    )
    preflight_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and readonly_probe_recorded
        and factory_parent_prerequisites_verified
        and graph_prerequisites_verified
        and creation_graph_outputs_blocked
        and compile_save_write_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_blueprint_function_library_readonly_preflight_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_BATCH_SCHEMA
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
        "blueprint_function_library_readonly_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "correct_project_blueprint_function_library_readonly_probe_recorded": (
            readonly_probe_recorded
        ),
        "blueprint_function_library_factory_parent_prerequisites_verified": (
            factory_parent_prerequisites_verified
        ),
        "blueprint_function_library_graph_prerequisites_verified": (
            graph_prerequisites_verified
        ),
        "blueprint_function_library_creation_graph_outputs_blocked": (
            creation_graph_outputs_blocked
        ),
        "blueprint_function_library_compile_save_write_outputs_blocked": (
            compile_save_write_outputs_blocked
        ),
        "blueprint_function_library_readonly_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_465_blueprint_function_library_readonly_checkpoint_satisfied": (
            preflight_ready
        ),
        "section_466_correct_project_blueprint_function_library_readonly_probe_recorded": (
            preflight_ready
        ),
        "section_467_blueprint_function_library_factory_parent_prerequisites_verified": (
            preflight_ready
        ),
        "section_468_blueprint_function_library_graph_prerequisites_verified": (
            preflight_ready
        ),
        "section_469_blueprint_function_library_creation_graph_outputs_blocked": (
            preflight_ready
        ),
        "section_470_blueprint_function_library_compile_save_write_outputs_blocked": (
            preflight_ready
        ),
        "section_471_blueprint_function_library_readonly_no_write_boundary_verified": (
            preflight_ready
        ),
        "section_472_blueprint_function_library_readonly_preflight_release_ready": (
            preflight_ready
        ),
        "blueprint_function_library_readonly_preflight_ready": preflight_ready,
        "blueprint_function_library_actual_authoring_still_blocked": (
            preflight_ready
        ),
        "final_durable_release_ready": preflight_ready,
        **{
            key: 1 if preflight_ready else 0
            for key in BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_PATH_COUNT_KEYS
        },
        **_blocked_output_counts(blueprint_function_library_readonly_preflight_result),
    }


def summarize_durable_executor_authoring_blueprint_function_library_readonly_preflight_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "blueprint_function_library_readonly_preflight_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "blueprint_function_library_actual_authoring_still_blocked",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_blueprint_function_library_readonly_preflight_batch_count": (
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
        "blueprint_function_library_readonly_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "blueprint_function_library_readonly_checkpoint_satisfied",
            )
        ),
        "correct_project_blueprint_function_library_readonly_probe_recorded_count": (
            _truthy_count(
                requested,
                "correct_project_blueprint_function_library_readonly_probe_recorded",
            )
        ),
        "blueprint_function_library_factory_parent_prerequisites_verified_count": (
            _truthy_count(
                requested,
                "blueprint_function_library_factory_parent_prerequisites_verified",
            )
        ),
        "blueprint_function_library_graph_prerequisites_verified_count": (
            _truthy_count(
                requested,
                "blueprint_function_library_graph_prerequisites_verified",
            )
        ),
        "blueprint_function_library_creation_graph_outputs_blocked_count": (
            _truthy_count(
                requested,
                "blueprint_function_library_creation_graph_outputs_blocked",
            )
        ),
        "blueprint_function_library_compile_save_write_outputs_blocked_count": (
            _truthy_count(
                requested,
                "blueprint_function_library_compile_save_write_outputs_blocked",
            )
        ),
        "blueprint_function_library_readonly_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "blueprint_function_library_readonly_no_write_boundary_verified",
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
            for key in BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in (
                BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS
            )
        }
    )
    return summary
