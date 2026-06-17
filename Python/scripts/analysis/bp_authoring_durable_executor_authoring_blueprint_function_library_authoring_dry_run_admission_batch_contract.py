#!/usr/bin/env python
"""
Sections 473-480 durable executor Blueprint Function Library dry-run admission.

This contract follows the Blueprint Function Library read-only preflight. It
admits only an offline dry-run plan for a disposable BFL under _MCP_Temp.
Actual BFL creation, function graph mutation, compile, save, delete, rename,
overwrite, cleanup, and production writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_blueprint_function_library_readonly_preflight_batch_contract as readonly_preflight


DURABLE_EXECUTOR_AUTHORING_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_BATCH_SCHEMA = (
    "section_473_480_durable_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_BATCH_SUMMARY_SCHEMA = (
    "section_473_480_durable_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batch_summary_v1"
)
BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_RESULT_SCHEMA = (
    "section_473_480_blueprint_function_library_authoring_dry_run_admission_result_v1"
)
SECTION_465_472_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_SUMMARY_SCHEMA = (
    readonly_preflight
    .DURABLE_EXECUTOR_AUTHORING_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_BATCH_SUMMARY_SCHEMA
)
DEFAULT_DRY_RUN_ROOT = "/Game/_MCP_Temp/DurableSaveGate/FunctionLibraryDryRun"
DEFAULT_TARGET_ASSET_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/FunctionLibraryDryRun/"
    "BFL_DurableFunctionLibraryDryRun"
)
DEFAULT_PARENT_CLASS = "BlueprintFunctionLibrary"
DEFAULT_FUNCTION_SIGNATURE_PLAN = (
    "FunctionName=CodexDryRunFunction",
    "ReturnType=bool",
    "Inputs=WorldContextObject:Object",
    "Pure=false",
)
DEFAULT_GRAPH_NODE_PLAN = (
    "EntryNode=K2Node_FunctionEntry",
    "ReturnNode=K2Node_FunctionResult",
    "LiteralBool=true",
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_blueprint_function_library_readonly_preflight_batch_count",
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
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    readonly_preflight
    .BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS
)

BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_PATH_COUNT_KEYS = (
    "section_473_blueprint_function_library_authoring_dry_run_checkpoint_satisfied_count",
    "section_474_blueprint_function_library_dry_run_scope_verified_count",
    "section_475_blueprint_function_library_function_signature_plan_classified_count",
    "section_476_blueprint_function_library_graph_node_plan_classified_count",
    "section_477_blueprint_function_library_graph_mutation_command_blocked_count",
    "section_478_blueprint_function_library_compile_save_write_outputs_blocked_count",
    "section_479_blueprint_function_library_authoring_dry_run_no_write_boundary_verified_count",
    "section_480_blueprint_function_library_authoring_dry_run_admission_release_ready_count",
    "blueprint_function_library_authoring_dry_run_admission_ready_count",
    "blueprint_function_library_actual_authoring_still_blocked_count",
)
BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS = (
    "function_library_authoring_admission_command_dispatched_count",
    "function_library_authoring_admission_command_executed_count",
    "function_library_blueprint_create_command_dispatched_count",
    "function_library_blueprint_create_command_executed_count",
    "function_library_graph_mutation_command_dispatched_count",
    "function_library_graph_mutation_command_executed_count",
    "function_library_function_added_count",
    "function_library_function_signature_changed_count",
    "function_library_node_added_count",
    "function_library_pin_connected_count",
    "function_library_readback_command_dispatched_count",
    "function_library_readback_command_executed_count",
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
BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_RESULT_KEYS = tuple(
    key.removesuffix("_count")
    for key in BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
)


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _count_is_one(summary: Dict[str, Any], key: str) -> bool:
    return bool(summary.get(key) == 1)


def _count_is_zero(summary: Dict[str, Any], key: str) -> bool:
    return bool(int(summary.get(key, 0) or 0) == 0)


def build_blueprint_function_library_authoring_dry_run_admission_result(
    *,
    dry_run_only: bool = True,
    dry_run_root: str = DEFAULT_DRY_RUN_ROOT,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    parent_class: str = DEFAULT_PARENT_CLASS,
    function_signature_plan: Sequence[str] = DEFAULT_FUNCTION_SIGNATURE_PLAN,
    graph_node_plan: Sequence[str] = DEFAULT_GRAPH_NODE_PLAN,
    graph_mutation_requires_live_contract: bool = True,
    graph_mutation_command_blocked: bool = True,
    actual_function_library_authoring_allowed: bool = False,
    dirty_content_after_dry_run: Sequence[str] = (),
    dirty_maps_after_dry_run: Sequence[str] = (),
    function_library_authoring_admission_command_dispatched: bool = False,
    function_library_authoring_admission_command_executed: bool = False,
    function_library_blueprint_create_command_dispatched: bool = False,
    function_library_blueprint_create_command_executed: bool = False,
    function_library_graph_mutation_command_dispatched: bool = False,
    function_library_graph_mutation_command_executed: bool = False,
    function_library_function_added: bool = False,
    function_library_function_signature_changed: bool = False,
    function_library_node_added: bool = False,
    function_library_pin_connected: bool = False,
    function_library_readback_command_dispatched: bool = False,
    function_library_readback_command_executed: bool = False,
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
        "schema": BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_RESULT_SCHEMA,
        "dry_run_only": dry_run_only,
        "dry_run_root": dry_run_root,
        "target_asset_path": target_asset_path,
        "parent_class": parent_class,
        "function_signature_plan": list(function_signature_plan),
        "graph_node_plan": list(graph_node_plan),
        "graph_mutation_requires_live_contract": graph_mutation_requires_live_contract,
        "graph_mutation_command_blocked": graph_mutation_command_blocked,
        "actual_function_library_authoring_allowed": (
            actual_function_library_authoring_allowed
        ),
        "dirty_content_after_dry_run": list(dirty_content_after_dry_run),
        "dirty_maps_after_dry_run": list(dirty_maps_after_dry_run),
        "function_library_authoring_admission_command_dispatched": (
            function_library_authoring_admission_command_dispatched
        ),
        "function_library_authoring_admission_command_executed": (
            function_library_authoring_admission_command_executed
        ),
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
        "function_library_readback_command_dispatched": (
            function_library_readback_command_dispatched
        ),
        "function_library_readback_command_executed": (
            function_library_readback_command_executed
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


def _blocked_output_counts(result: Dict[str, Any]) -> Dict[str, int]:
    return {
        count_key: 1 if result.get(result_key) else 0
        for count_key, result_key in zip(
            BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS,
            BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_RESULT_KEYS,
        )
    }


def build_durable_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batch_contract(
    requested: bool,
    section_465_472_blueprint_function_library_readonly_preflight_summary: Dict[str, Any],
    blueprint_function_library_authoring_dry_run_admission_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_465_472_summary_schema_matches = bool(
        section_465_472_blueprint_function_library_readonly_preflight_summary.get(
            "schema"
        )
        == SECTION_465_472_BLUEPRINT_FUNCTION_LIBRARY_READONLY_PREFLIGHT_SUMMARY_SCHEMA
    )
    section_465_472_summary_passed = bool(
        section_465_472_blueprint_function_library_readonly_preflight_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_readonly_preflight_ready = all(
        _count_is_one(
            section_465_472_blueprint_function_library_readonly_preflight_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_465_472_blueprint_function_library_readonly_preflight_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        blueprint_function_library_authoring_dry_run_admission_result.get("schema")
        == BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_465_472_summary_schema_matches
        and section_465_472_summary_passed
        and upstream_readonly_preflight_ready
        and upstream_outputs_closed
    )
    dry_run_scope_verified = bool(
        blueprint_function_library_authoring_dry_run_admission_result.get(
            "dry_run_only"
        )
        and blueprint_function_library_authoring_dry_run_admission_result.get(
            "dry_run_root"
        )
        == DEFAULT_DRY_RUN_ROOT
        and blueprint_function_library_authoring_dry_run_admission_result.get(
            "target_asset_path"
        )
        == DEFAULT_TARGET_ASSET_PATH
        and str(
            blueprint_function_library_authoring_dry_run_admission_result.get(
                "target_asset_path", ""
            )
        ).startswith("/Game/_MCP_Temp/")
        and blueprint_function_library_authoring_dry_run_admission_result.get(
            "parent_class"
        )
        == DEFAULT_PARENT_CLASS
        and not blueprint_function_library_authoring_dry_run_admission_result.get(
            "actual_function_library_authoring_allowed"
        )
    )
    function_signature_plan_classified = bool(
        tuple(
            blueprint_function_library_authoring_dry_run_admission_result.get(
                "function_signature_plan", ()
            )
            or ()
        )
        == DEFAULT_FUNCTION_SIGNATURE_PLAN
    )
    graph_node_plan_classified = bool(
        tuple(
            blueprint_function_library_authoring_dry_run_admission_result.get(
                "graph_node_plan", ()
            )
            or ()
        )
        == DEFAULT_GRAPH_NODE_PLAN
    )
    graph_mutation_command_blocked = bool(
        blueprint_function_library_authoring_dry_run_admission_result.get(
            "graph_mutation_requires_live_contract"
        )
        and blueprint_function_library_authoring_dry_run_admission_result.get(
            "graph_mutation_command_blocked"
        )
        and not blueprint_function_library_authoring_dry_run_admission_result.get(
            "actual_function_library_authoring_allowed"
        )
        and all(
            not blueprint_function_library_authoring_dry_run_admission_result.get(key)
            for key in (
                "function_library_authoring_admission_command_dispatched",
                "function_library_authoring_admission_command_executed",
                "function_library_blueprint_create_command_dispatched",
                "function_library_blueprint_create_command_executed",
                "function_library_graph_mutation_command_dispatched",
                "function_library_graph_mutation_command_executed",
                "function_library_function_added",
                "function_library_function_signature_changed",
                "function_library_node_added",
                "function_library_pin_connected",
                "function_library_readback_command_dispatched",
                "function_library_readback_command_executed",
            )
        )
    )
    compile_save_write_outputs_blocked = all(
        not blueprint_function_library_authoring_dry_run_admission_result.get(key)
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
        not blueprint_function_library_authoring_dry_run_admission_result.get(key)
        for key in BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        all_outputs_blocked
        and not blueprint_function_library_authoring_dry_run_admission_result.get(
            "dirty_content_after_dry_run"
        )
        and not blueprint_function_library_authoring_dry_run_admission_result.get(
            "dirty_maps_after_dry_run"
        )
    )
    result_has_no_error = bool(
        blueprint_function_library_authoring_dry_run_admission_result.get("error")
        in (None, "")
    )
    dry_run_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and dry_run_scope_verified
        and function_signature_plan_classified
        and graph_node_plan_classified
        and graph_mutation_command_blocked
        and compile_save_write_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_465_472_summary_schema_matches": (
            section_465_472_summary_schema_matches
        ),
        "section_465_472_summary_passed": section_465_472_summary_passed,
        "section_465_472_blueprint_function_library_readonly_preflight_ready": (
            upstream_readonly_preflight_ready
        ),
        "section_465_472_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "blueprint_function_library_authoring_dry_run_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "blueprint_function_library_dry_run_scope_verified": dry_run_scope_verified,
        "blueprint_function_library_function_signature_plan_classified": (
            function_signature_plan_classified
        ),
        "blueprint_function_library_graph_node_plan_classified": (
            graph_node_plan_classified
        ),
        "blueprint_function_library_graph_mutation_command_blocked": (
            graph_mutation_command_blocked
        ),
        "blueprint_function_library_compile_save_write_outputs_blocked": (
            compile_save_write_outputs_blocked
        ),
        "blueprint_function_library_authoring_dry_run_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_473_blueprint_function_library_authoring_dry_run_checkpoint_satisfied": (
            dry_run_ready
        ),
        "section_474_blueprint_function_library_dry_run_scope_verified": (
            dry_run_ready
        ),
        "section_475_blueprint_function_library_function_signature_plan_classified": (
            dry_run_ready
        ),
        "section_476_blueprint_function_library_graph_node_plan_classified": (
            dry_run_ready
        ),
        "section_477_blueprint_function_library_graph_mutation_command_blocked": (
            dry_run_ready
        ),
        "section_478_blueprint_function_library_compile_save_write_outputs_blocked": (
            dry_run_ready
        ),
        "section_479_blueprint_function_library_authoring_dry_run_no_write_boundary_verified": (
            dry_run_ready
        ),
        "section_480_blueprint_function_library_authoring_dry_run_admission_release_ready": (
            dry_run_ready
        ),
        "blueprint_function_library_authoring_dry_run_admission_ready": (
            dry_run_ready
        ),
        "blueprint_function_library_actual_authoring_still_blocked": (
            dry_run_ready
        ),
        "final_durable_release_ready": dry_run_ready,
        **{
            key: 1 if dry_run_ready else 0
            for key in (
                BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_PATH_COUNT_KEYS
            )
        },
        **_blocked_output_counts(
            blueprint_function_library_authoring_dry_run_admission_result
        ),
    }


def summarize_durable_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "blueprint_function_library_authoring_dry_run_admission_ready",
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
                    BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batch_count": (
            len(requested)
        ),
        "section_465_472_summary_schema_matches_count": _truthy_count(
            requested, "section_465_472_summary_schema_matches"
        ),
        "section_465_472_summary_passed_count": _truthy_count(
            requested, "section_465_472_summary_passed"
        ),
        "section_465_472_blueprint_function_library_readonly_preflight_ready_count": (
            _truthy_count(
                requested,
                "section_465_472_blueprint_function_library_readonly_preflight_ready",
            )
        ),
        "section_465_472_outputs_closed_count": _truthy_count(
            requested, "section_465_472_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "blueprint_function_library_authoring_dry_run_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "blueprint_function_library_authoring_dry_run_checkpoint_satisfied",
            )
        ),
        "blueprint_function_library_dry_run_scope_verified_count": _truthy_count(
            requested, "blueprint_function_library_dry_run_scope_verified"
        ),
        "blueprint_function_library_function_signature_plan_classified_count": (
            _truthy_count(
                requested,
                "blueprint_function_library_function_signature_plan_classified",
            )
        ),
        "blueprint_function_library_graph_node_plan_classified_count": (
            _truthy_count(
                requested,
                "blueprint_function_library_graph_node_plan_classified",
            )
        ),
        "blueprint_function_library_graph_mutation_command_blocked_count": (
            _truthy_count(
                requested,
                "blueprint_function_library_graph_mutation_command_blocked",
            )
        ),
        "blueprint_function_library_compile_save_write_outputs_blocked_count": (
            _truthy_count(
                requested,
                "blueprint_function_library_compile_save_write_outputs_blocked",
            )
        ),
        "blueprint_function_library_authoring_dry_run_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "blueprint_function_library_authoring_dry_run_no_write_boundary_verified",
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
            for key in (
                BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_PATH_COUNT_KEYS
            )
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in (
                BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
            )
        }
    )
    return summary
