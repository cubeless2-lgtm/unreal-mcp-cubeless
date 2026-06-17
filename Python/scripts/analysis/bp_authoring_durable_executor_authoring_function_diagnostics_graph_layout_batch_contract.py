#!/usr/bin/env python
"""
Sections 281-288 durable executor function diagnostics and graph layout batch.

This contract adds a diagnostic-only gate after the saved temporary Actor
Blueprint readback. It proves function-call, pin-contract, and graph-layout
diagnostics can produce repair suggestions while automatic graph repair,
mutation, compile, save, delete, rename, overwrite, and production writes remain
closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract as readback


DURABLE_EXECUTOR_AUTHORING_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_BATCH_SCHEMA = (
    "section_281_288_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_BATCH_SUMMARY_SCHEMA = (
    "section_281_288_durable_executor_authoring_function_diagnostics_graph_layout_batch_summary_v1"
)
FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_RESULT_SCHEMA = (
    "section_281_288_function_diagnostics_graph_layout_result_v1"
)
SECTION_273_280_COMPONENT_DEFAULT_READBACK_SUMMARY_SCHEMA = (
    readback
    .DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = readback.DEFAULT_TARGET_ASSET_PATH
DEFAULT_FUNCTION_CALL_CONTRACT_SCHEMA = "section_23_function_call_contract_v1"
DEFAULT_GRAPH_LAYOUT_CONTRACT_SCHEMA = "section_24_graph_layout_contract_v1"
DEFAULT_GRAPH_LAYOUT_SPACING_CONTRACT_SCHEMA = (
    "section_27_graph_layout_spacing_contract_v1"
)
DEFAULT_FAILURE_DIAGNOSTIC_SCHEMA = "section_41_failure_diagnostics_v2"
DEFAULT_DIAGNOSTIC_CATEGORIES = (
    "function_target_resolution",
    "pin_contract_mismatch",
    "graph_layout_spacing_violation",
)
DEFAULT_REPAIR_SUGGESTION_KINDS = (
    "reselect_reflected_function_target",
    "repair_missing_exec_or_data_pin_contract",
    "move_overlapping_nodes_without_mutation",
)
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_live_actor_bp_component_default_readback_batch_count",
    "section_273_live_actor_bp_actual_authoring_summary_ready_count",
    "section_274_live_actor_bp_class_type_readback_verified_count",
    "section_275_live_actor_bp_variable_default_type_readback_verified_count",
    "section_276_live_actor_bp_component_template_type_readback_verified_count",
    "section_277_live_actor_bp_cdo_default_tag_readback_verified_count",
    "section_278_broader_blueprint_class_authoring_guard_verified_count",
    "section_279_live_actor_bp_readback_no_write_verified_count",
    "section_280_live_actor_bp_component_default_readback_release_ready_count",
    "live_actor_bp_component_default_type_readback_ready_count",
    "broader_blueprint_class_authoring_guard_ready_count",
    "live_actor_bp_component_default_readback_no_write_verified_count",
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
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
    "actor_bp_authoring_target_dirty_after_count",
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
FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_PATH_COUNT_KEYS = (
    "section_281_actor_bp_readback_summary_ready_count",
    "section_282_function_call_diagnostics_ready_count",
    "section_283_pin_contract_diagnostics_ready_count",
    "section_284_graph_layout_diagnostics_ready_count",
    "section_285_repair_suggestions_generated_count",
    "section_286_auto_graph_repair_execution_blocked_count",
    "section_287_diagnostics_no_write_boundary_verified_count",
    "section_288_function_diagnostics_graph_layout_release_ready_count",
    "function_call_diagnostics_ready_count",
    "graph_layout_repair_suggestions_ready_count",
    "function_diagnostics_graph_layout_no_write_verified_count",
)
BLOCKED_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_OUTPUT_COUNT_KEYS = (
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
    "rename_asset_allowed_count",
    "rename_command_dispatched_count",
    "rename_command_executed_count",
    "overwrite_allowed_count",
    "overwrite_executed_count",
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


def build_function_diagnostics_graph_layout_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    diagnostic_only: bool = True,
    function_call_contract_schema: str = DEFAULT_FUNCTION_CALL_CONTRACT_SCHEMA,
    function_call_contracts_checked: int = 2,
    function_target_resolution_checked: bool = True,
    reflected_function_target_diagnostic_ready: bool = True,
    pin_contracts_checked: int = 3,
    exec_pin_diagnostic_ready: bool = True,
    data_pin_diagnostic_ready: bool = True,
    graph_layout_contract_schema: str = DEFAULT_GRAPH_LAYOUT_CONTRACT_SCHEMA,
    graph_layout_spacing_contract_schema: str = (
        DEFAULT_GRAPH_LAYOUT_SPACING_CONTRACT_SCHEMA
    ),
    node_layout_contracts_checked: int = 3,
    layout_spacing_contracts_checked: int = 3,
    overlap_or_spacing_diagnostic_ready: bool = True,
    failure_diagnostic_schema: str = DEFAULT_FAILURE_DIAGNOSTIC_SCHEMA,
    diagnostic_categories: Sequence[str] = DEFAULT_DIAGNOSTIC_CATEGORIES,
    repair_suggestion_kinds: Sequence[str] = DEFAULT_REPAIR_SUGGESTION_KINDS,
    repair_suggestion_count: int = 3,
    repair_suggestions_are_manual_only: bool = True,
    auto_graph_repair_execution_allowed: bool = False,
    graph_repair_command_dispatched: bool = False,
    graph_repair_command_executed: bool = False,
    graph_layout_mutation_performed: bool = False,
    node_position_write_performed: bool = False,
    pin_connection_write_performed: bool = False,
    compile_dispatched: bool = False,
    compile_executed: bool = False,
    save_dispatched: bool = False,
    save_executed: bool = False,
    asset_write_performed: bool = False,
    package_dirty_marked: bool = False,
    cleanup_allowed: bool = False,
    cleanup_executed: bool = False,
    delete_asset_allowed: bool = False,
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
        "schema": FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "diagnostic_only": diagnostic_only,
        "function_call_contract_schema": function_call_contract_schema,
        "function_call_contracts_checked": function_call_contracts_checked,
        "function_target_resolution_checked": (
            function_target_resolution_checked
        ),
        "reflected_function_target_diagnostic_ready": (
            reflected_function_target_diagnostic_ready
        ),
        "pin_contracts_checked": pin_contracts_checked,
        "exec_pin_diagnostic_ready": exec_pin_diagnostic_ready,
        "data_pin_diagnostic_ready": data_pin_diagnostic_ready,
        "graph_layout_contract_schema": graph_layout_contract_schema,
        "graph_layout_spacing_contract_schema": (
            graph_layout_spacing_contract_schema
        ),
        "node_layout_contracts_checked": node_layout_contracts_checked,
        "layout_spacing_contracts_checked": layout_spacing_contracts_checked,
        "overlap_or_spacing_diagnostic_ready": (
            overlap_or_spacing_diagnostic_ready
        ),
        "failure_diagnostic_schema": failure_diagnostic_schema,
        "diagnostic_categories": list(diagnostic_categories),
        "repair_suggestion_kinds": list(repair_suggestion_kinds),
        "repair_suggestion_count": repair_suggestion_count,
        "repair_suggestions_are_manual_only": repair_suggestions_are_manual_only,
        "auto_graph_repair_execution_allowed": (
            auto_graph_repair_execution_allowed
        ),
        "graph_repair_command_dispatched": graph_repair_command_dispatched,
        "graph_repair_command_executed": graph_repair_command_executed,
        "graph_layout_mutation_performed": graph_layout_mutation_performed,
        "node_position_write_performed": node_position_write_performed,
        "pin_connection_write_performed": pin_connection_write_performed,
        "compile_dispatched": compile_dispatched,
        "compile_executed": compile_executed,
        "save_dispatched": save_dispatched,
        "save_executed": save_executed,
        "asset_write_performed": asset_write_performed,
        "package_dirty_marked": package_dirty_marked,
        "cleanup_allowed": cleanup_allowed,
        "cleanup_executed": cleanup_executed,
        "delete_asset_allowed": delete_asset_allowed,
        "rename_asset_allowed": rename_asset_allowed,
        "rename_command_dispatched": rename_command_dispatched,
        "rename_command_executed": rename_command_executed,
        "overwrite_allowed": overwrite_allowed,
        "overwrite_executed": overwrite_executed,
        "production_path_write_allowed": production_path_write_allowed,
        "production_path_write_executed": production_path_write_executed,
        "error": error,
    }


def build_durable_executor_authoring_function_diagnostics_graph_layout_batch_contract(
    requested: bool,
    section_273_280_component_default_readback_summary: Dict[str, Any],
    function_diagnostics_graph_layout_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_273_280_summary_schema_matches = bool(
        section_273_280_component_default_readback_summary.get("schema")
        == SECTION_273_280_COMPONENT_DEFAULT_READBACK_SUMMARY_SCHEMA
    )
    section_273_280_summary_passed = bool(
        section_273_280_component_default_readback_summary.get("status")
        == "passed"
    )
    upstream_readback_ready = all(
        _count_is_one(section_273_280_component_default_readback_summary, key)
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(section_273_280_component_default_readback_summary, key)
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        function_diagnostics_graph_layout_result.get("schema")
        == FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_RESULT_SCHEMA
    )
    actor_bp_readback_summary_ready = bool(
        requested
        and section_273_280_summary_schema_matches
        and section_273_280_summary_passed
        and upstream_readback_ready
        and upstream_outputs_closed
    )
    target_scope_reconfirmed = bool(
        function_diagnostics_graph_layout_result.get("target_asset_path")
        == DEFAULT_TARGET_ASSET_PATH
        and str(
            function_diagnostics_graph_layout_result.get("target_asset_path", "")
        ).startswith("/Game/_MCP_Temp/")
    )
    categories = tuple(
        function_diagnostics_graph_layout_result.get(
            "diagnostic_categories", ()
        )
        or ()
    )
    repair_kinds = tuple(
        function_diagnostics_graph_layout_result.get(
            "repair_suggestion_kinds", ()
        )
        or ()
    )
    function_call_diagnostics_ready = bool(
        target_scope_reconfirmed
        and function_diagnostics_graph_layout_result.get("diagnostic_only")
        and function_diagnostics_graph_layout_result.get(
            "function_call_contract_schema"
        )
        == DEFAULT_FUNCTION_CALL_CONTRACT_SCHEMA
        and int(
            function_diagnostics_graph_layout_result.get(
                "function_call_contracts_checked", 0
            )
            or 0
        )
        >= 2
        and function_diagnostics_graph_layout_result.get(
            "function_target_resolution_checked"
        )
        and function_diagnostics_graph_layout_result.get(
            "reflected_function_target_diagnostic_ready"
        )
        and "function_target_resolution" in categories
    )
    pin_contract_diagnostics_ready = bool(
        int(
            function_diagnostics_graph_layout_result.get(
                "pin_contracts_checked", 0
            )
            or 0
        )
        >= 3
        and function_diagnostics_graph_layout_result.get(
            "exec_pin_diagnostic_ready"
        )
        and function_diagnostics_graph_layout_result.get(
            "data_pin_diagnostic_ready"
        )
        and "pin_contract_mismatch" in categories
    )
    graph_layout_diagnostics_ready = bool(
        function_diagnostics_graph_layout_result.get(
            "graph_layout_contract_schema"
        )
        == DEFAULT_GRAPH_LAYOUT_CONTRACT_SCHEMA
        and function_diagnostics_graph_layout_result.get(
            "graph_layout_spacing_contract_schema"
        )
        == DEFAULT_GRAPH_LAYOUT_SPACING_CONTRACT_SCHEMA
        and int(
            function_diagnostics_graph_layout_result.get(
                "node_layout_contracts_checked", 0
            )
            or 0
        )
        >= 3
        and int(
            function_diagnostics_graph_layout_result.get(
                "layout_spacing_contracts_checked", 0
            )
            or 0
        )
        >= 3
        and function_diagnostics_graph_layout_result.get(
            "overlap_or_spacing_diagnostic_ready"
        )
        and "graph_layout_spacing_violation" in categories
    )
    repair_suggestions_generated = bool(
        repair_kinds == DEFAULT_REPAIR_SUGGESTION_KINDS
        and int(
            function_diagnostics_graph_layout_result.get(
                "repair_suggestion_count", 0
            )
            or 0
        )
        == len(DEFAULT_REPAIR_SUGGESTION_KINDS)
        and function_diagnostics_graph_layout_result.get(
            "repair_suggestions_are_manual_only"
        )
    )
    auto_graph_repair_execution_blocked = bool(
        not function_diagnostics_graph_layout_result.get(
            "auto_graph_repair_execution_allowed"
        )
        and not function_diagnostics_graph_layout_result.get(
            "graph_repair_command_dispatched"
        )
        and not function_diagnostics_graph_layout_result.get(
            "graph_repair_command_executed"
        )
        and not function_diagnostics_graph_layout_result.get(
            "graph_layout_mutation_performed"
        )
        and not function_diagnostics_graph_layout_result.get(
            "node_position_write_performed"
        )
        and not function_diagnostics_graph_layout_result.get(
            "pin_connection_write_performed"
        )
    )
    diagnostics_no_write_boundary_verified = bool(
        auto_graph_repair_execution_blocked
        and not function_diagnostics_graph_layout_result.get(
            "compile_dispatched"
        )
        and not function_diagnostics_graph_layout_result.get("compile_executed")
        and not function_diagnostics_graph_layout_result.get("save_dispatched")
        and not function_diagnostics_graph_layout_result.get("save_executed")
        and not function_diagnostics_graph_layout_result.get(
            "asset_write_performed"
        )
        and not function_diagnostics_graph_layout_result.get(
            "package_dirty_marked"
        )
        and not function_diagnostics_graph_layout_result.get("cleanup_allowed")
        and not function_diagnostics_graph_layout_result.get("cleanup_executed")
        and not function_diagnostics_graph_layout_result.get(
            "delete_asset_allowed"
        )
        and not function_diagnostics_graph_layout_result.get(
            "rename_asset_allowed"
        )
        and not function_diagnostics_graph_layout_result.get(
            "rename_command_dispatched"
        )
        and not function_diagnostics_graph_layout_result.get(
            "rename_command_executed"
        )
        and not function_diagnostics_graph_layout_result.get(
            "overwrite_allowed"
        )
        and not function_diagnostics_graph_layout_result.get(
            "overwrite_executed"
        )
        and not function_diagnostics_graph_layout_result.get(
            "production_path_write_allowed"
        )
        and not function_diagnostics_graph_layout_result.get(
            "production_path_write_executed"
        )
    )
    result_has_no_error = bool(
        function_diagnostics_graph_layout_result.get("error") in (None, "")
        and function_diagnostics_graph_layout_result.get(
            "failure_diagnostic_schema"
        )
        == DEFAULT_FAILURE_DIAGNOSTIC_SCHEMA
    )
    diagnostics_batch_passed = bool(
        actor_bp_readback_summary_ready
        and result_schema_matches
        and function_call_diagnostics_ready
        and pin_contract_diagnostics_ready
        and graph_layout_diagnostics_ready
        and repair_suggestions_generated
        and auto_graph_repair_execution_blocked
        and diagnostics_no_write_boundary_verified
        and result_has_no_error
    )

    return {
        "id": "durable_executor_authoring_function_diagnostics_graph_layout_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_273_280_summary_schema_matches": (
            section_273_280_summary_schema_matches
        ),
        "section_273_280_summary_passed": section_273_280_summary_passed,
        "section_273_280_component_default_readback_ready": (
            upstream_readback_ready
        ),
        "section_273_280_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "actor_bp_readback_summary_ready": actor_bp_readback_summary_ready,
        "target_scope_reconfirmed": target_scope_reconfirmed,
        "function_call_diagnostics_ready": function_call_diagnostics_ready,
        "pin_contract_diagnostics_ready": pin_contract_diagnostics_ready,
        "graph_layout_diagnostics_ready": graph_layout_diagnostics_ready,
        "repair_suggestions_generated": repair_suggestions_generated,
        "auto_graph_repair_execution_blocked": (
            auto_graph_repair_execution_blocked
        ),
        "diagnostics_no_write_boundary_verified": (
            diagnostics_no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_281_actor_bp_readback_summary_ready": diagnostics_batch_passed,
        "section_282_function_call_diagnostics_ready": diagnostics_batch_passed,
        "section_283_pin_contract_diagnostics_ready": diagnostics_batch_passed,
        "section_284_graph_layout_diagnostics_ready": diagnostics_batch_passed,
        "section_285_repair_suggestions_generated": diagnostics_batch_passed,
        "section_286_auto_graph_repair_execution_blocked": (
            diagnostics_batch_passed
        ),
        "section_287_diagnostics_no_write_boundary_verified": (
            diagnostics_batch_passed
        ),
        "section_288_function_diagnostics_graph_layout_release_ready": (
            diagnostics_batch_passed
        ),
        "graph_layout_repair_suggestions_ready": diagnostics_batch_passed,
        "function_diagnostics_graph_layout_no_write_verified": (
            diagnostics_batch_passed
        ),
        "final_durable_release_ready": diagnostics_batch_passed,
        "graph_repair_command_dispatched": False,
        "graph_repair_command_executed": False,
        "graph_layout_mutation_performed": False,
        "node_position_write_performed": False,
        "pin_connection_write_performed": False,
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
        "rename_command_dispatched": False,
        "rename_command_executed": False,
        "overwrite_allowed": False,
        "overwrite_executed": False,
        "production_path_write_allowed": False,
        "production_path_write_executed": False,
        **{
            key: 1 if diagnostics_batch_passed else 0
            for key in FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_function_diagnostics_graph_layout_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "function_call_diagnostics_ready")
            == len(requested)
            and _truthy_count(
                requested, "graph_layout_repair_suggestions_ready"
            )
            == len(requested)
            and _truthy_count(
                requested,
                "function_diagnostics_graph_layout_no_write_verified",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_function_diagnostics_graph_layout_batch_count": (
            len(requested)
        ),
        "section_273_280_summary_schema_matches_count": _truthy_count(
            requested, "section_273_280_summary_schema_matches"
        ),
        "section_273_280_summary_passed_count": _truthy_count(
            requested, "section_273_280_summary_passed"
        ),
        "section_273_280_component_default_readback_ready_count": (
            _truthy_count(
                requested, "section_273_280_component_default_readback_ready"
            )
        ),
        "section_273_280_outputs_closed_count": _truthy_count(
            requested, "section_273_280_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "actor_bp_readback_summary_ready_count": _truthy_count(
            requested, "actor_bp_readback_summary_ready"
        ),
        "target_scope_reconfirmed_count": _truthy_count(
            requested, "target_scope_reconfirmed"
        ),
        "function_call_diagnostics_ready_count": _truthy_count(
            requested, "function_call_diagnostics_ready"
        ),
        "pin_contract_diagnostics_ready_count": _truthy_count(
            requested, "pin_contract_diagnostics_ready"
        ),
        "graph_layout_diagnostics_ready_count": _truthy_count(
            requested, "graph_layout_diagnostics_ready"
        ),
        "repair_suggestions_generated_count": _truthy_count(
            requested, "repair_suggestions_generated"
        ),
        "auto_graph_repair_execution_blocked_count": _truthy_count(
            requested, "auto_graph_repair_execution_blocked"
        ),
        "diagnostics_no_write_boundary_verified_count": _truthy_count(
            requested, "diagnostics_no_write_boundary_verified"
        ),
        "result_has_no_error_count": _truthy_count(
            requested, "result_has_no_error"
        ),
        "graph_layout_repair_suggestions_ready_count": _truthy_count(
            requested, "graph_layout_repair_suggestions_ready"
        ),
        "function_diagnostics_graph_layout_no_write_verified_count": (
            _truthy_count(
                requested,
                "function_diagnostics_graph_layout_no_write_verified",
            )
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "graph_repair_command_dispatched_count": _truthy_count(
            requested, "graph_repair_command_dispatched"
        ),
        "graph_repair_command_executed_count": _truthy_count(
            requested, "graph_repair_command_executed"
        ),
        "graph_layout_mutation_performed_count": _truthy_count(
            requested, "graph_layout_mutation_performed"
        ),
        "node_position_write_performed_count": _truthy_count(
            requested, "node_position_write_performed"
        ),
        "pin_connection_write_performed_count": _truthy_count(
            requested, "pin_connection_write_performed"
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
        "rename_command_dispatched_count": _truthy_count(
            requested, "rename_command_dispatched"
        ),
        "rename_command_executed_count": _truthy_count(
            requested, "rename_command_executed"
        ),
        "overwrite_allowed_count": _truthy_count(
            requested, "overwrite_allowed"
        ),
        "overwrite_executed_count": _truthy_count(
            requested, "overwrite_executed"
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
            for key in FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_FUNCTION_DIAGNOSTICS_GRAPH_LAYOUT_OUTPUT_COUNT_KEYS
        }
    )
    return summary
