#!/usr/bin/env python
"""
Sections 345-352 durable executor graph repair execution dry-run batch.

This contract follows the broader non-Actor Blueprint dry-run gate. It admits a
dry-run graph repair command/evidence path for the current temp Actor Blueprint,
but the observed graph state is empty, so execution is a no-op. Actual graph
repair dispatch, node movement, pin rewiring, compile, save, delete, rename,
overwrite, cleanup, and production writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_broader_non_actor_blueprint_dry_run_batch_contract as broader
import bp_authoring_durable_executor_authoring_post_recreation_function_diagnostics_refresh_batch_contract as diagnostics_refresh


DURABLE_EXECUTOR_AUTHORING_GRAPH_REPAIR_EXECUTION_DRY_RUN_BATCH_SCHEMA = (
    "section_345_352_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_GRAPH_REPAIR_EXECUTION_DRY_RUN_BATCH_SUMMARY_SCHEMA = (
    "section_345_352_durable_executor_authoring_graph_repair_execution_dry_run_batch_summary_v1"
)
GRAPH_REPAIR_EXECUTION_DRY_RUN_RESULT_SCHEMA = (
    "section_345_352_graph_repair_execution_dry_run_result_v1"
)
SECTION_337_344_BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_SUMMARY_SCHEMA = (
    broader
    .DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = diagnostics_refresh.DEFAULT_TARGET_ASSET_PATH
DEFAULT_TARGET_ROOT = diagnostics_refresh.DEFAULT_TARGET_ROOT
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_broader_non_actor_blueprint_dry_run_batch_count",
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
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = broader.BLOCKED_BROADER_NON_ACTOR_BLUEPRINT_OUTPUT_COUNT_KEYS
GRAPH_REPAIR_EXECUTION_DRY_RUN_PATH_COUNT_KEYS = (
    "section_345_graph_repair_dry_run_checkpoint_satisfied_count",
    "section_346_graph_repair_dry_run_command_admitted_count",
    "section_347_graph_repair_dry_run_command_executed_count",
    "section_348_empty_graph_noop_repair_verified_count",
    "section_349_node_pin_mutation_outputs_blocked_count",
    "section_350_compile_save_outputs_blocked_count",
    "section_351_graph_repair_dry_run_no_write_boundary_verified_count",
    "section_352_graph_repair_execution_dry_run_release_ready_count",
    "graph_repair_execution_dry_run_ready_count",
    "graph_repair_actual_execution_still_blocked_count",
)
BLOCKED_GRAPH_REPAIR_EXECUTION_DRY_RUN_OUTPUT_COUNT_KEYS = (
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
BLOCKED_GRAPH_REPAIR_EXECUTION_DRY_RUN_RESULT_KEYS = (
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


def build_graph_repair_execution_dry_run_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    target_root: str = DEFAULT_TARGET_ROOT,
    target_under_expected_root: bool = True,
    dry_run_only: bool = True,
    upstream_empty_graph_state_verified: bool = True,
    graph_repair_dry_run_command_admitted: bool = True,
    graph_repair_dry_run_command_executed: bool = True,
    dry_run_noop_due_empty_graph: bool = True,
    node_position_repair_plan_count: int = 0,
    pin_connection_repair_plan_count: int = 0,
    compile_required: bool = False,
    save_required: bool = False,
    repair_evidence_captured: bool = True,
    target_dirty_after_dry_run: bool = False,
    dirty_maps_after_dry_run: Sequence[str] = (),
    dirty_content_after_dry_run: Sequence[str] = (),
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
        "schema": GRAPH_REPAIR_EXECUTION_DRY_RUN_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "target_root": target_root,
        "target_under_expected_root": target_under_expected_root,
        "dry_run_only": dry_run_only,
        "upstream_empty_graph_state_verified": upstream_empty_graph_state_verified,
        "graph_repair_dry_run_command_admitted": (
            graph_repair_dry_run_command_admitted
        ),
        "graph_repair_dry_run_command_executed": (
            graph_repair_dry_run_command_executed
        ),
        "dry_run_noop_due_empty_graph": dry_run_noop_due_empty_graph,
        "node_position_repair_plan_count": node_position_repair_plan_count,
        "pin_connection_repair_plan_count": pin_connection_repair_plan_count,
        "compile_required": compile_required,
        "save_required": save_required,
        "repair_evidence_captured": repair_evidence_captured,
        "target_dirty_after_dry_run": target_dirty_after_dry_run,
        "dirty_maps_after_dry_run": list(dirty_maps_after_dry_run),
        "dirty_content_after_dry_run": list(dirty_content_after_dry_run),
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


def build_durable_executor_authoring_graph_repair_execution_dry_run_batch_contract(
    requested: bool,
    section_337_344_broader_non_actor_blueprint_dry_run_summary: Dict[str, Any],
    graph_repair_execution_dry_run_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_337_344_summary_schema_matches = bool(
        section_337_344_broader_non_actor_blueprint_dry_run_summary.get(
            "schema"
        )
        == SECTION_337_344_BROADER_NON_ACTOR_BLUEPRINT_DRY_RUN_SUMMARY_SCHEMA
    )
    section_337_344_summary_passed = bool(
        section_337_344_broader_non_actor_blueprint_dry_run_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_broader_dry_run_ready = all(
        _count_is_one(
            section_337_344_broader_non_actor_blueprint_dry_run_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_337_344_broader_non_actor_blueprint_dry_run_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        graph_repair_execution_dry_run_result.get("schema")
        == GRAPH_REPAIR_EXECUTION_DRY_RUN_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_337_344_summary_schema_matches
        and section_337_344_summary_passed
        and upstream_broader_dry_run_ready
        and upstream_outputs_closed
    )
    target_scope_verified = bool(
        graph_repair_execution_dry_run_result.get("target_asset_path")
        == DEFAULT_TARGET_ASSET_PATH
        and graph_repair_execution_dry_run_result.get("target_root")
        == DEFAULT_TARGET_ROOT
        and graph_repair_execution_dry_run_result.get(
            "target_under_expected_root"
        )
        and str(
            graph_repair_execution_dry_run_result.get("target_asset_path", "")
        ).startswith("/Game/_MCP_Temp/")
    )
    dry_run_command_admitted = bool(
        target_scope_verified
        and graph_repair_execution_dry_run_result.get("dry_run_only")
        and graph_repair_execution_dry_run_result.get(
            "upstream_empty_graph_state_verified"
        )
        and graph_repair_execution_dry_run_result.get(
            "graph_repair_dry_run_command_admitted"
        )
    )
    dry_run_command_executed = bool(
        dry_run_command_admitted
        and graph_repair_execution_dry_run_result.get(
            "graph_repair_dry_run_command_executed"
        )
        and graph_repair_execution_dry_run_result.get(
            "repair_evidence_captured"
        )
    )
    empty_graph_noop_repair_verified = bool(
        graph_repair_execution_dry_run_result.get("dry_run_noop_due_empty_graph")
        and int(
            graph_repair_execution_dry_run_result.get(
                "node_position_repair_plan_count", -1
            )
            or 0
        )
        == 0
        and int(
            graph_repair_execution_dry_run_result.get(
                "pin_connection_repair_plan_count", -1
            )
            or 0
        )
        == 0
    )
    node_pin_mutation_outputs_blocked = bool(
        not graph_repair_execution_dry_run_result.get(
            "graph_repair_command_dispatched"
        )
        and not graph_repair_execution_dry_run_result.get(
            "graph_repair_command_executed"
        )
        and not graph_repair_execution_dry_run_result.get(
            "graph_layout_mutation_performed"
        )
        and not graph_repair_execution_dry_run_result.get(
            "node_position_write_performed"
        )
        and not graph_repair_execution_dry_run_result.get(
            "pin_connection_write_performed"
        )
    )
    compile_save_outputs_blocked = bool(
        not graph_repair_execution_dry_run_result.get("compile_required")
        and not graph_repair_execution_dry_run_result.get("save_required")
        and not graph_repair_execution_dry_run_result.get(
            "actor_bp_authoring_compile_dispatched"
        )
        and not graph_repair_execution_dry_run_result.get(
            "actor_bp_authoring_compile_executed"
        )
        and not graph_repair_execution_dry_run_result.get(
            "actor_bp_authoring_save_dispatched"
        )
        and not graph_repair_execution_dry_run_result.get(
            "actor_bp_authoring_save_executed"
        )
        and not graph_repair_execution_dry_run_result.get(
            "actor_bp_authoring_asset_write_performed"
        )
        and not graph_repair_execution_dry_run_result.get(
            "actor_bp_authoring_package_dirty_marked"
        )
    )
    no_write_boundary_verified = bool(
        node_pin_mutation_outputs_blocked
        and compile_save_outputs_blocked
        and not graph_repair_execution_dry_run_result.get(
            "target_dirty_after_dry_run"
        )
        and not graph_repair_execution_dry_run_result.get(
            "dirty_maps_after_dry_run"
        )
        and not graph_repair_execution_dry_run_result.get(
            "dirty_content_after_dry_run"
        )
        and all(
            not graph_repair_execution_dry_run_result.get(key)
            for key in BLOCKED_GRAPH_REPAIR_EXECUTION_DRY_RUN_RESULT_KEYS
        )
    )
    result_has_no_error = bool(
        graph_repair_execution_dry_run_result.get("error") in (None, "")
    )
    dry_run_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and dry_run_command_admitted
        and dry_run_command_executed
        and empty_graph_noop_repair_verified
        and node_pin_mutation_outputs_blocked
        and compile_save_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_graph_repair_execution_dry_run_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_GRAPH_REPAIR_EXECUTION_DRY_RUN_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_337_344_summary_schema_matches": (
            section_337_344_summary_schema_matches
        ),
        "section_337_344_summary_passed": section_337_344_summary_passed,
        "section_337_344_broader_non_actor_blueprint_dry_run_ready": (
            upstream_broader_dry_run_ready
        ),
        "section_337_344_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "graph_repair_dry_run_checkpoint_satisfied": checkpoint_satisfied,
        "graph_repair_dry_run_command_admitted": dry_run_command_admitted,
        "graph_repair_dry_run_command_executed": dry_run_command_executed,
        "empty_graph_noop_repair_verified": empty_graph_noop_repair_verified,
        "node_pin_mutation_outputs_blocked": node_pin_mutation_outputs_blocked,
        "compile_save_outputs_blocked": compile_save_outputs_blocked,
        "graph_repair_dry_run_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_345_graph_repair_dry_run_checkpoint_satisfied": (
            dry_run_ready
        ),
        "section_346_graph_repair_dry_run_command_admitted": dry_run_ready,
        "section_347_graph_repair_dry_run_command_executed": dry_run_ready,
        "section_348_empty_graph_noop_repair_verified": dry_run_ready,
        "section_349_node_pin_mutation_outputs_blocked": dry_run_ready,
        "section_350_compile_save_outputs_blocked": dry_run_ready,
        "section_351_graph_repair_dry_run_no_write_boundary_verified": (
            dry_run_ready
        ),
        "section_352_graph_repair_execution_dry_run_release_ready": (
            dry_run_ready
        ),
        "graph_repair_execution_dry_run_ready": dry_run_ready,
        "graph_repair_actual_execution_still_blocked": dry_run_ready,
        "final_durable_release_ready": dry_run_ready,
        **{
            key: 1 if dry_run_ready else 0
            for key in GRAPH_REPAIR_EXECUTION_DRY_RUN_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_GRAPH_REPAIR_EXECUTION_DRY_RUN_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_graph_repair_execution_dry_run_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "graph_repair_execution_dry_run_ready")
            == len(requested)
            and _truthy_count(
                requested, "graph_repair_actual_execution_still_blocked"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_GRAPH_REPAIR_EXECUTION_DRY_RUN_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_GRAPH_REPAIR_EXECUTION_DRY_RUN_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_graph_repair_execution_dry_run_batch_count": (
            len(requested)
        ),
        "section_337_344_summary_schema_matches_count": _truthy_count(
            requested, "section_337_344_summary_schema_matches"
        ),
        "section_337_344_summary_passed_count": _truthy_count(
            requested, "section_337_344_summary_passed"
        ),
        "section_337_344_broader_non_actor_blueprint_dry_run_ready_count": (
            _truthy_count(
                requested,
                "section_337_344_broader_non_actor_blueprint_dry_run_ready",
            )
        ),
        "section_337_344_outputs_closed_count": _truthy_count(
            requested, "section_337_344_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "graph_repair_dry_run_checkpoint_satisfied_count": _truthy_count(
            requested, "graph_repair_dry_run_checkpoint_satisfied"
        ),
        "graph_repair_dry_run_command_admitted_count": _truthy_count(
            requested, "graph_repair_dry_run_command_admitted"
        ),
        "graph_repair_dry_run_command_executed_count": _truthy_count(
            requested, "graph_repair_dry_run_command_executed"
        ),
        "empty_graph_noop_repair_verified_count": _truthy_count(
            requested, "empty_graph_noop_repair_verified"
        ),
        "node_pin_mutation_outputs_blocked_count": _truthy_count(
            requested, "node_pin_mutation_outputs_blocked"
        ),
        "compile_save_outputs_blocked_count": _truthy_count(
            requested, "compile_save_outputs_blocked"
        ),
        "graph_repair_dry_run_no_write_boundary_verified_count": _truthy_count(
            requested, "graph_repair_dry_run_no_write_boundary_verified"
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
            for key in GRAPH_REPAIR_EXECUTION_DRY_RUN_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_GRAPH_REPAIR_EXECUTION_DRY_RUN_OUTPUT_COUNT_KEYS
        }
    )
    return summary
