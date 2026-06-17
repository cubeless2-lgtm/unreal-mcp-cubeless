#!/usr/bin/env python
"""
Sections 329-336 durable executor post-recreation function diagnostics refresh.

This contract follows the Section 321-328 readback-strengthened temp Actor
Blueprint. It admits only read-only diagnostics refresh for the current
post-recreation graph/function state. The observed target has no function
graphs or ubergraph pages, so the refresh must classify the empty graph state
without opening graph repair, node movement, pin rewiring, compile/save, delete,
rename, overwrite, cleanup, or production writes.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_contract as readback


DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_BATCH_SCHEMA = (
    "section_329_336_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_BATCH_SUMMARY_SCHEMA = (
    "section_329_336_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_summary_v1"
)
POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_RESULT_SCHEMA = (
    "section_329_336_post_recreation_function_diagnostics_refresh_result_v1"
)
SECTION_321_328_POST_RECREATION_ACTOR_BP_READBACK_STRENGTHENING_SUMMARY_SCHEMA = (
    readback
    .DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_ACTOR_BP_READBACK_STRENGTHENING_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = readback.DEFAULT_TARGET_ASSET_PATH
DEFAULT_TARGET_ROOT = readback.DEFAULT_TARGET_ROOT
DEFAULT_GENERATED_CLASS_PATH = readback.DEFAULT_GENERATED_CLASS_PATH
DEFAULT_BLUEPRINT_CLASS_NAME = readback.DEFAULT_BLUEPRINT_CLASS_NAME
DEFAULT_CDO_CLASS_NAME = readback.DEFAULT_CDO_CLASS_NAME
DEFAULT_FUNCTION_GRAPH_COUNT = 0
DEFAULT_UBERGRAPH_PAGE_COUNT = 0
DEFAULT_CONSTRUCTION_SCRIPT_PRESENT = False
DEFAULT_DIAGNOSTIC_REFRESH_CATEGORIES = (
    "post_recreation_function_inventory",
    "empty_graph_state_classification",
    "no_repair_required",
)
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_post_recreation_actor_bp_readback_strengthening_batch_count",
    "section_321_readback_strengthening_checkpoint_satisfied_count",
    "section_322_recreated_actor_bp_readback_route_ready_count",
    "section_323_variable_default_reread_verified_count",
    "section_324_default_tag_reread_verified_count",
    "section_325_raw_component_duplicate_handles_detected_count",
    "section_326_unique_component_identity_verified_count",
    "section_327_readback_no_write_dirty_boundary_verified_count",
    "section_328_readback_strengthening_release_ready_count",
    "post_recreation_actor_bp_readback_strengthened_count",
    "post_recreation_actor_bp_unique_component_identity_verified_count",
    "final_durable_release_ready_count",
)
UPSTREAM_DESTRUCTIVE_OUTPUTS_CLOSED_COUNT_KEYS = (
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
    "diagnostics_command_dispatched_count",
    "diagnostics_command_executed_count",
    "graph_repair_command_dispatched_count",
    "graph_repair_command_executed_count",
    "graph_layout_mutation_performed_count",
    "node_position_write_performed_count",
    "pin_connection_write_performed_count",
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
POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_PATH_COUNT_KEYS = (
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
)
BLOCKED_FUNCTION_DIAGNOSTICS_REFRESH_OUTPUT_COUNT_KEYS = (
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
BLOCKED_FUNCTION_DIAGNOSTICS_REFRESH_RESULT_KEYS = (
    "diagnostics_command_dispatched",
    "diagnostics_command_executed",
    "graph_repair_command_dispatched",
    "graph_repair_command_executed",
    "graph_layout_mutation_performed",
    "node_position_write_performed",
    "pin_connection_write_performed",
    "actor_bp_authoring_compile_dispatched",
    "actor_bp_authoring_compile_executed",
    "actor_bp_authoring_save_dispatched",
    "actor_bp_authoring_save_executed",
    "actor_bp_authoring_asset_write_performed",
    "actor_bp_authoring_package_dirty_marked",
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


def build_post_recreation_function_diagnostics_refresh_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_root: str = DEFAULT_TARGET_ROOT,
    target_under_expected_root: bool = True,
    asset_exists: bool = True,
    asset_data_valid: bool = True,
    blueprint_class_name: str = DEFAULT_BLUEPRINT_CLASS_NAME,
    generated_class_path: str = DEFAULT_GENERATED_CLASS_PATH,
    cdo_class_name: str = DEFAULT_CDO_CLASS_NAME,
    cdo_is_actor: bool = True,
    graph_inventory_read_only: bool = True,
    function_graph_count: int = DEFAULT_FUNCTION_GRAPH_COUNT,
    ubergraph_page_count: int = DEFAULT_UBERGRAPH_PAGE_COUNT,
    construction_script_present: bool = DEFAULT_CONSTRUCTION_SCRIPT_PRESENT,
    empty_graph_state_safely_classified: bool = True,
    function_diagnostics_refreshed: bool = True,
    pin_contract_diagnostics_refreshed: bool = True,
    graph_layout_diagnostics_refreshed: bool = True,
    diagnostic_refresh_categories: Sequence[str] = (
        DEFAULT_DIAGNOSTIC_REFRESH_CATEGORIES
    ),
    no_repair_required: bool = True,
    repair_suggestion_count: int = 0,
    repair_suggestions_are_manual_only: bool = True,
    target_dirty_after_readback: bool = False,
    dirty_maps_after_readback: Sequence[str] = (),
    dirty_content_after_readback: Sequence[str] = (),
    diagnostics_command_dispatched: bool = False,
    diagnostics_command_executed: bool = False,
    graph_repair_command_dispatched: bool = False,
    graph_repair_command_executed: bool = False,
    graph_layout_mutation_performed: bool = False,
    node_position_write_performed: bool = False,
    pin_connection_write_performed: bool = False,
    actor_bp_authoring_compile_dispatched: bool = False,
    actor_bp_authoring_compile_executed: bool = False,
    actor_bp_authoring_save_dispatched: bool = False,
    actor_bp_authoring_save_executed: bool = False,
    actor_bp_authoring_asset_write_performed: bool = False,
    actor_bp_authoring_package_dirty_marked: bool = False,
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
        "schema": POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_root": target_root,
        "target_under_expected_root": target_under_expected_root,
        "asset_exists": asset_exists,
        "asset_data_valid": asset_data_valid,
        "blueprint_class_name": blueprint_class_name,
        "generated_class_path": generated_class_path,
        "cdo_class_name": cdo_class_name,
        "cdo_is_actor": cdo_is_actor,
        "graph_inventory_read_only": graph_inventory_read_only,
        "function_graph_count": function_graph_count,
        "ubergraph_page_count": ubergraph_page_count,
        "construction_script_present": construction_script_present,
        "empty_graph_state_safely_classified": (
            empty_graph_state_safely_classified
        ),
        "function_diagnostics_refreshed": function_diagnostics_refreshed,
        "pin_contract_diagnostics_refreshed": pin_contract_diagnostics_refreshed,
        "graph_layout_diagnostics_refreshed": (
            graph_layout_diagnostics_refreshed
        ),
        "diagnostic_refresh_categories": list(diagnostic_refresh_categories),
        "no_repair_required": no_repair_required,
        "repair_suggestion_count": repair_suggestion_count,
        "repair_suggestions_are_manual_only": repair_suggestions_are_manual_only,
        "target_dirty_after_readback": target_dirty_after_readback,
        "dirty_maps_after_readback": list(dirty_maps_after_readback),
        "dirty_content_after_readback": list(dirty_content_after_readback),
        "diagnostics_command_dispatched": diagnostics_command_dispatched,
        "diagnostics_command_executed": diagnostics_command_executed,
        "graph_repair_command_dispatched": graph_repair_command_dispatched,
        "graph_repair_command_executed": graph_repair_command_executed,
        "graph_layout_mutation_performed": graph_layout_mutation_performed,
        "node_position_write_performed": node_position_write_performed,
        "pin_connection_write_performed": pin_connection_write_performed,
        "actor_bp_authoring_compile_dispatched": (
            actor_bp_authoring_compile_dispatched
        ),
        "actor_bp_authoring_compile_executed": (
            actor_bp_authoring_compile_executed
        ),
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


def build_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract(
    requested: bool,
    section_321_328_post_recreation_actor_bp_readback_strengthening_summary: Dict[str, Any],
    post_recreation_function_diagnostics_refresh_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_321_328_summary_schema_matches = bool(
        section_321_328_post_recreation_actor_bp_readback_strengthening_summary.get(
            "schema"
        )
        == SECTION_321_328_POST_RECREATION_ACTOR_BP_READBACK_STRENGTHENING_SUMMARY_SCHEMA
    )
    section_321_328_summary_passed = bool(
        section_321_328_post_recreation_actor_bp_readback_strengthening_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_readback_strengthened = all(
        _count_is_one(
            section_321_328_post_recreation_actor_bp_readback_strengthening_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_destructive_outputs_closed = all(
        _count_is_zero(
            section_321_328_post_recreation_actor_bp_readback_strengthening_summary,
            key,
        )
        for key in UPSTREAM_DESTRUCTIVE_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        post_recreation_function_diagnostics_refresh_result.get("schema")
        == POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_321_328_summary_schema_matches
        and section_321_328_summary_passed
        and upstream_readback_strengthened
        and upstream_destructive_outputs_closed
    )
    target_scope_verified = bool(
        post_recreation_function_diagnostics_refresh_result.get(
            "target_asset_path"
        )
        == DEFAULT_TARGET_ASSET_PATH
        and post_recreation_function_diagnostics_refresh_result.get(
            "target_root"
        )
        == DEFAULT_TARGET_ROOT
        and post_recreation_function_diagnostics_refresh_result.get(
            "target_under_expected_root"
        )
        and str(
            post_recreation_function_diagnostics_refresh_result.get(
                "target_asset_path", ""
            )
        ).startswith("/Game/_MCP_Temp/")
    )
    actor_bp_graph_inventory_ready = bool(
        target_scope_verified
        and post_recreation_function_diagnostics_refresh_result.get(
            "asset_exists"
        )
        and post_recreation_function_diagnostics_refresh_result.get(
            "asset_data_valid"
        )
        and post_recreation_function_diagnostics_refresh_result.get(
            "blueprint_class_name"
        )
        == DEFAULT_BLUEPRINT_CLASS_NAME
        and post_recreation_function_diagnostics_refresh_result.get(
            "generated_class_path"
        )
        == DEFAULT_GENERATED_CLASS_PATH
        and post_recreation_function_diagnostics_refresh_result.get(
            "cdo_class_name"
        )
        == DEFAULT_CDO_CLASS_NAME
        and post_recreation_function_diagnostics_refresh_result.get(
            "cdo_is_actor"
        )
        and post_recreation_function_diagnostics_refresh_result.get(
            "graph_inventory_read_only"
        )
    )
    empty_graph_state_safely_classified = bool(
        int(
            post_recreation_function_diagnostics_refresh_result.get(
                "function_graph_count", -1
            )
            or 0
        )
        == DEFAULT_FUNCTION_GRAPH_COUNT
        and int(
            post_recreation_function_diagnostics_refresh_result.get(
                "ubergraph_page_count", -1
            )
            or 0
        )
        == DEFAULT_UBERGRAPH_PAGE_COUNT
        and post_recreation_function_diagnostics_refresh_result.get(
            "construction_script_present"
        )
        == DEFAULT_CONSTRUCTION_SCRIPT_PRESENT
        and post_recreation_function_diagnostics_refresh_result.get(
            "empty_graph_state_safely_classified"
        )
    )
    categories = tuple(
        post_recreation_function_diagnostics_refresh_result.get(
            "diagnostic_refresh_categories", ()
        )
        or ()
    )
    function_diagnostics_refreshed = bool(
        post_recreation_function_diagnostics_refresh_result.get(
            "function_diagnostics_refreshed"
        )
        and "post_recreation_function_inventory" in categories
    )
    pin_contract_diagnostics_refreshed = bool(
        post_recreation_function_diagnostics_refresh_result.get(
            "pin_contract_diagnostics_refreshed"
        )
        and "empty_graph_state_classification" in categories
    )
    graph_layout_diagnostics_refreshed = bool(
        post_recreation_function_diagnostics_refresh_result.get(
            "graph_layout_diagnostics_refreshed"
        )
        and "no_repair_required" in categories
        and post_recreation_function_diagnostics_refresh_result.get(
            "no_repair_required"
        )
        and int(
            post_recreation_function_diagnostics_refresh_result.get(
                "repair_suggestion_count", -1
            )
            or 0
        )
        == 0
        and post_recreation_function_diagnostics_refresh_result.get(
            "repair_suggestions_are_manual_only"
        )
    )
    no_write_dirty_boundary_verified = bool(
        not post_recreation_function_diagnostics_refresh_result.get(
            "target_dirty_after_readback"
        )
        and not post_recreation_function_diagnostics_refresh_result.get(
            "dirty_maps_after_readback"
        )
        and not post_recreation_function_diagnostics_refresh_result.get(
            "dirty_content_after_readback"
        )
        and all(
            not post_recreation_function_diagnostics_refresh_result.get(key)
            for key in BLOCKED_FUNCTION_DIAGNOSTICS_REFRESH_RESULT_KEYS
        )
    )
    result_has_no_error = bool(
        post_recreation_function_diagnostics_refresh_result.get("error")
        in (None, "")
    )
    refreshed = bool(
        checkpoint_satisfied
        and result_schema_matches
        and actor_bp_graph_inventory_ready
        and empty_graph_state_safely_classified
        and function_diagnostics_refreshed
        and pin_contract_diagnostics_refreshed
        and graph_layout_diagnostics_refreshed
        and no_write_dirty_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_321_328_summary_schema_matches": (
            section_321_328_summary_schema_matches
        ),
        "section_321_328_summary_passed": section_321_328_summary_passed,
        "section_321_328_post_recreation_readback_strengthened": (
            upstream_readback_strengthened
        ),
        "section_321_328_destructive_outputs_closed": (
            upstream_destructive_outputs_closed
        ),
        "result_schema_matches": result_schema_matches,
        "diagnostics_refresh_checkpoint_satisfied": checkpoint_satisfied,
        "current_actor_bp_graph_inventory_ready": (
            actor_bp_graph_inventory_ready
        ),
        "empty_graph_state_safely_classified": (
            empty_graph_state_safely_classified
        ),
        "function_diagnostics_refreshed": function_diagnostics_refreshed,
        "pin_contract_diagnostics_refreshed": (
            pin_contract_diagnostics_refreshed
        ),
        "graph_layout_diagnostics_refreshed": (
            graph_layout_diagnostics_refreshed
        ),
        "diagnostics_refresh_no_write_boundary_verified": (
            no_write_dirty_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_329_post_recreation_diagnostics_refresh_checkpoint_satisfied": (
            refreshed
        ),
        "section_330_current_actor_bp_graph_inventory_ready": refreshed,
        "section_331_empty_graph_state_safely_classified": refreshed,
        "section_332_function_diagnostics_refreshed": refreshed,
        "section_333_pin_contract_diagnostics_refreshed": refreshed,
        "section_334_graph_layout_diagnostics_refreshed": refreshed,
        "section_335_diagnostics_refresh_no_write_boundary_verified": (
            refreshed
        ),
        "section_336_post_recreation_function_diagnostics_refresh_release_ready": (
            refreshed
        ),
        "post_recreation_function_diagnostics_refreshed": refreshed,
        "post_recreation_empty_graph_state_verified": refreshed,
        "final_durable_release_ready": refreshed,
        **{
            key: 1 if refreshed else 0
            for key in POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_FUNCTION_DIAGNOSTICS_REFRESH_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested, "post_recreation_function_diagnostics_refreshed"
            )
            == len(requested)
            and _truthy_count(
                requested, "post_recreation_empty_graph_state_verified"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_FUNCTION_DIAGNOSTICS_REFRESH_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_post_recreation_function_diagnostics_refresh_batch_count": (
            len(requested)
        ),
        "section_321_328_summary_schema_matches_count": _truthy_count(
            requested, "section_321_328_summary_schema_matches"
        ),
        "section_321_328_summary_passed_count": _truthy_count(
            requested, "section_321_328_summary_passed"
        ),
        "section_321_328_post_recreation_readback_strengthened_count": (
            _truthy_count(
                requested,
                "section_321_328_post_recreation_readback_strengthened",
            )
        ),
        "section_321_328_destructive_outputs_closed_count": _truthy_count(
            requested, "section_321_328_destructive_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "diagnostics_refresh_checkpoint_satisfied_count": _truthy_count(
            requested, "diagnostics_refresh_checkpoint_satisfied"
        ),
        "current_actor_bp_graph_inventory_ready_count": _truthy_count(
            requested, "current_actor_bp_graph_inventory_ready"
        ),
        "empty_graph_state_safely_classified_count": _truthy_count(
            requested, "empty_graph_state_safely_classified"
        ),
        "function_diagnostics_refreshed_count": _truthy_count(
            requested, "function_diagnostics_refreshed"
        ),
        "pin_contract_diagnostics_refreshed_count": _truthy_count(
            requested, "pin_contract_diagnostics_refreshed"
        ),
        "graph_layout_diagnostics_refreshed_count": _truthy_count(
            requested, "graph_layout_diagnostics_refreshed"
        ),
        "diagnostics_refresh_no_write_boundary_verified_count": _truthy_count(
            requested, "diagnostics_refresh_no_write_boundary_verified"
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
            for key in POST_RECREATION_FUNCTION_DIAGNOSTICS_REFRESH_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_FUNCTION_DIAGNOSTICS_REFRESH_OUTPUT_COUNT_KEYS
        }
    )
    return summary
