#!/usr/bin/env python
"""
Sections 265-272 durable executor live Actor Blueprint actual authoring batch.

This contract admits the single target-scoped live Actor Blueprint authoring
execution under /Game/_MCP_Temp after the Section 257-264 checkpoint. It proves
the actual variable, component, CDO default/tag, compile, save, readback, and
dirty-baseline isolation evidence while keeping delete, rename, overwrite, and
production writes closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract as live_actor_bp_preflight


DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_ACTUAL_AUTHORING_BATCH_SCHEMA = (
    "section_265_272_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_ACTUAL_AUTHORING_BATCH_SUMMARY_SCHEMA = (
    "section_265_272_durable_executor_authoring_live_actor_bp_actual_authoring_batch_summary_v1"
)
LIVE_ACTOR_BP_ACTUAL_AUTHORING_RESULT_SCHEMA = (
    "section_265_272_live_actor_bp_actual_authoring_result_v1"
)
SECTION_257_264_LIVE_ACTOR_BP_PREFLIGHT_SUMMARY_SCHEMA = (
    live_actor_bp_preflight
    .DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = live_actor_bp_preflight.DEFAULT_TARGET_ASSET_PATH
DEFAULT_VARIABLE_NAME = "MCPAuthoringScalar"
DEFAULT_VARIABLE_VALUE = 1.0
DEFAULT_COMPONENT_NAME = "MCPAuthoringProbeComponent"
DEFAULT_COMPONENT_CLASS = "SceneComponent"
DEFAULT_TAG_NAME = "MCP_DurableAuthoring_LiveProbe"
DEFAULT_EXTERNAL_DIRTY_PACKAGE = "/Game/Cubeless/VFX/Fire/NS_Codex_Fire_01"
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_live_actor_bp_authoring_preflight_batch_count",
    "section_257_live_actor_bp_command_envelope_scoped_count",
    "section_258_live_actor_bp_read_only_target_preflight_ready_count",
    "section_259_live_actor_bp_mutation_sequence_planned_count",
    "section_260_live_actor_bp_compile_save_ordering_verified_count",
    "section_261_live_actor_bp_rollback_boundary_revalidated_count",
    "section_262_live_actor_bp_readback_evidence_plan_ready_count",
    "section_263_live_actor_bp_final_checkpoint_required_count",
    "section_264_live_actor_bp_actual_authoring_closed_count",
    "live_actor_bp_authoring_preflight_allowed_count",
    "live_actor_bp_authoring_checkpoint_ready_count",
    "actual_live_actor_bp_authoring_requires_final_user_checkpoint_count",
    "final_durable_release_ready_count",
)
UPSTREAM_MUTATION_MUST_BE_CLOSED_COUNT_KEYS = (
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
    "cleanup_allowed_count",
    "cleanup_executed_count",
    "delete_asset_allowed_count",
    "rename_asset_allowed_count",
    "production_path_write_allowed_count",
    "production_path_write_executed_count",
)
LIVE_ACTOR_BP_ACTUAL_AUTHORING_PATH_COUNT_KEYS = (
    "section_265_live_actor_bp_actual_execution_checkpoint_satisfied_count",
    "section_266_live_actor_bp_target_scope_reconfirmed_count",
    "section_267_live_actor_bp_variable_authoring_executed_count",
    "section_268_live_actor_bp_component_authoring_executed_count",
    "section_269_live_actor_bp_default_authoring_executed_count",
    "section_270_live_actor_bp_compile_save_executed_count",
    "section_271_live_actor_bp_readback_verified_count",
    "section_272_live_actor_bp_dirty_baseline_preserved_count",
    "live_actor_bp_actual_authoring_executed_count",
    "live_actor_bp_actual_authoring_saved_count",
    "live_actor_bp_actual_authoring_readback_verified_count",
)
BLOCKED_LIVE_ACTOR_BP_DESTRUCTIVE_OUTPUT_COUNT_KEYS = (
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


def build_live_actor_bp_actual_authoring_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    variable_name: str = DEFAULT_VARIABLE_NAME,
    variable_value: float = DEFAULT_VARIABLE_VALUE,
    component_name: str = DEFAULT_COMPONENT_NAME,
    component_class: str = DEFAULT_COMPONENT_CLASS,
    tag_name: str = DEFAULT_TAG_NAME,
    cdo_is_actor: bool = True,
    variable_exists_before: bool = False,
    component_exists_before: bool = False,
    tag_exists_before: bool = False,
    variable_added: bool = True,
    component_added: bool = True,
    default_written: bool = True,
    compile_executed: bool = True,
    saved: bool = True,
    variable_exists_after: bool = True,
    scalar_default_after: float = DEFAULT_VARIABLE_VALUE,
    component_exists_after: bool = True,
    tag_exists_after: bool = True,
    readback_passed: bool = True,
    target_dirty_after: bool = False,
    external_dirty_before: Sequence[str] = (DEFAULT_EXTERNAL_DIRTY_PACKAGE,),
    external_dirty_after: Sequence[str] = (DEFAULT_EXTERNAL_DIRTY_PACKAGE,),
    external_dirty_preserved: bool = True,
    safety_passed: bool = True,
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
        "schema": LIVE_ACTOR_BP_ACTUAL_AUTHORING_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "variable_name": variable_name,
        "variable_value": variable_value,
        "component_name": component_name,
        "component_class": component_class,
        "tag_name": tag_name,
        "cdo_is_actor": cdo_is_actor,
        "variable_exists_before": variable_exists_before,
        "component_exists_before": component_exists_before,
        "tag_exists_before": tag_exists_before,
        "variable_added": variable_added,
        "component_added": component_added,
        "default_written": default_written,
        "compile_executed": compile_executed,
        "saved": saved,
        "variable_exists_after": variable_exists_after,
        "scalar_default_after": scalar_default_after,
        "component_exists_after": component_exists_after,
        "tag_exists_after": tag_exists_after,
        "readback_passed": readback_passed,
        "target_dirty_after": target_dirty_after,
        "external_dirty_before": list(external_dirty_before),
        "external_dirty_after": list(external_dirty_after),
        "external_dirty_preserved": external_dirty_preserved,
        "safety_passed": safety_passed,
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


def build_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract(
    requested: bool,
    section_257_264_live_actor_bp_preflight_summary: Dict[str, Any],
    live_actor_bp_actual_authoring_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_257_264_summary_schema_matches = bool(
        section_257_264_live_actor_bp_preflight_summary.get("schema")
        == SECTION_257_264_LIVE_ACTOR_BP_PREFLIGHT_SUMMARY_SCHEMA
    )
    section_257_264_summary_passed = bool(
        section_257_264_live_actor_bp_preflight_summary.get("status")
        == "passed"
    )
    upstream_preflight_ready = all(
        _count_is_one(section_257_264_live_actor_bp_preflight_summary, key)
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_mutation_outputs_closed = all(
        _count_is_zero(section_257_264_live_actor_bp_preflight_summary, key)
        for key in UPSTREAM_MUTATION_MUST_BE_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        live_actor_bp_actual_authoring_result.get("schema")
        == LIVE_ACTOR_BP_ACTUAL_AUTHORING_RESULT_SCHEMA
    )
    target_scope_reconfirmed = bool(
        live_actor_bp_actual_authoring_result.get("target_asset_path")
        == DEFAULT_TARGET_ASSET_PATH
        and str(
            live_actor_bp_actual_authoring_result.get("target_asset_path", "")
        ).startswith("/Game/_MCP_Temp/")
        and live_actor_bp_actual_authoring_result.get("cdo_is_actor")
    )
    actual_execution_checkpoint_satisfied = bool(
        requested
        and section_257_264_summary_schema_matches
        and section_257_264_summary_passed
        and upstream_preflight_ready
        and upstream_mutation_outputs_closed
    )
    variable_authoring_executed = bool(
        live_actor_bp_actual_authoring_result.get("variable_name")
        == DEFAULT_VARIABLE_NAME
        and not live_actor_bp_actual_authoring_result.get("variable_exists_before")
        and live_actor_bp_actual_authoring_result.get("variable_added")
        and live_actor_bp_actual_authoring_result.get("variable_exists_after")
        and float(
            live_actor_bp_actual_authoring_result.get("scalar_default_after", -1)
        )
        == DEFAULT_VARIABLE_VALUE
    )
    component_authoring_executed = bool(
        live_actor_bp_actual_authoring_result.get("component_name")
        == DEFAULT_COMPONENT_NAME
        and live_actor_bp_actual_authoring_result.get("component_class")
        == DEFAULT_COMPONENT_CLASS
        and not live_actor_bp_actual_authoring_result.get("component_exists_before")
        and live_actor_bp_actual_authoring_result.get("component_added")
        and live_actor_bp_actual_authoring_result.get("component_exists_after")
    )
    default_authoring_executed = bool(
        live_actor_bp_actual_authoring_result.get("tag_name") == DEFAULT_TAG_NAME
        and not live_actor_bp_actual_authoring_result.get("tag_exists_before")
        and live_actor_bp_actual_authoring_result.get("default_written")
        and live_actor_bp_actual_authoring_result.get("tag_exists_after")
    )
    compile_save_executed = bool(
        live_actor_bp_actual_authoring_result.get("compile_executed")
        and live_actor_bp_actual_authoring_result.get("saved")
        and not live_actor_bp_actual_authoring_result.get("target_dirty_after")
    )
    readback_verified = bool(
        live_actor_bp_actual_authoring_result.get("readback_passed")
        and variable_authoring_executed
        and component_authoring_executed
        and default_authoring_executed
    )
    dirty_baseline_preserved = bool(
        live_actor_bp_actual_authoring_result.get("external_dirty_preserved")
        and live_actor_bp_actual_authoring_result.get("external_dirty_before")
        == live_actor_bp_actual_authoring_result.get("external_dirty_after")
    )
    destructive_outputs_closed = bool(
        not live_actor_bp_actual_authoring_result.get("cleanup_allowed")
        and not live_actor_bp_actual_authoring_result.get("cleanup_executed")
        and not live_actor_bp_actual_authoring_result.get("delete_asset_allowed")
        and not live_actor_bp_actual_authoring_result.get("rename_asset_allowed")
        and not live_actor_bp_actual_authoring_result.get("rename_command_dispatched")
        and not live_actor_bp_actual_authoring_result.get("rename_command_executed")
        and not live_actor_bp_actual_authoring_result.get("overwrite_allowed")
        and not live_actor_bp_actual_authoring_result.get("overwrite_executed")
        and not live_actor_bp_actual_authoring_result.get(
            "production_path_write_allowed"
        )
        and not live_actor_bp_actual_authoring_result.get(
            "production_path_write_executed"
        )
    )
    result_has_no_error = bool(
        live_actor_bp_actual_authoring_result.get("error") in (None, "")
    )
    actual_authoring_passed = bool(
        actual_execution_checkpoint_satisfied
        and result_schema_matches
        and target_scope_reconfirmed
        and variable_authoring_executed
        and component_authoring_executed
        and default_authoring_executed
        and compile_save_executed
        and readback_verified
        and dirty_baseline_preserved
        and destructive_outputs_closed
        and live_actor_bp_actual_authoring_result.get("safety_passed")
        and result_has_no_error
    )

    return {
        "id": "durable_executor_authoring_live_actor_bp_actual_authoring_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_ACTUAL_AUTHORING_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_257_264_summary_schema_matches": (
            section_257_264_summary_schema_matches
        ),
        "section_257_264_summary_passed": section_257_264_summary_passed,
        "section_257_264_live_actor_bp_preflight_ready": (
            upstream_preflight_ready
        ),
        "section_257_264_mutation_outputs_closed": (
            upstream_mutation_outputs_closed
        ),
        "result_schema_matches": result_schema_matches,
        "actual_execution_checkpoint_satisfied": (
            actual_execution_checkpoint_satisfied
        ),
        "target_scope_reconfirmed": target_scope_reconfirmed,
        "variable_authoring_executed": variable_authoring_executed,
        "component_authoring_executed": component_authoring_executed,
        "default_authoring_executed": default_authoring_executed,
        "compile_save_executed": compile_save_executed,
        "readback_verified": readback_verified,
        "dirty_baseline_preserved": dirty_baseline_preserved,
        "destructive_outputs_closed": destructive_outputs_closed,
        "result_has_no_error": result_has_no_error,
        "live_actor_bp_actual_authoring_executed": actual_authoring_passed,
        "live_actor_bp_actual_authoring_saved": actual_authoring_passed,
        "live_actor_bp_actual_authoring_readback_verified": actual_authoring_passed,
        "actual_live_actor_bp_authoring_requires_final_user_checkpoint": False,
        "actual_live_actor_bp_authoring_final_checkpoint_satisfied": (
            actual_authoring_passed
        ),
        "section_265_live_actor_bp_actual_execution_checkpoint_satisfied": (
            actual_authoring_passed
        ),
        "section_266_live_actor_bp_target_scope_reconfirmed": (
            actual_authoring_passed
        ),
        "section_267_live_actor_bp_variable_authoring_executed": (
            actual_authoring_passed
        ),
        "section_268_live_actor_bp_component_authoring_executed": (
            actual_authoring_passed
        ),
        "section_269_live_actor_bp_default_authoring_executed": (
            actual_authoring_passed
        ),
        "section_270_live_actor_bp_compile_save_executed": actual_authoring_passed,
        "section_271_live_actor_bp_readback_verified": actual_authoring_passed,
        "section_272_live_actor_bp_dirty_baseline_preserved": (
            actual_authoring_passed
        ),
        "final_durable_release_ready": actual_authoring_passed,
        "variable_add_command_dispatched": actual_authoring_passed,
        "variable_add_command_executed": actual_authoring_passed,
        "component_add_command_dispatched": actual_authoring_passed,
        "component_add_command_executed": actual_authoring_passed,
        "default_write_command_dispatched": actual_authoring_passed,
        "default_write_command_executed": actual_authoring_passed,
        "actor_bp_authoring_command_dispatched": actual_authoring_passed,
        "actor_bp_authoring_command_executed": actual_authoring_passed,
        "actor_bp_authoring_compile_dispatched": actual_authoring_passed,
        "actor_bp_authoring_compile_executed": actual_authoring_passed,
        "actor_bp_authoring_save_dispatched": actual_authoring_passed,
        "actor_bp_authoring_save_executed": actual_authoring_passed,
        "actor_bp_authoring_asset_write_performed": actual_authoring_passed,
        "actor_bp_authoring_package_dirty_marked": actual_authoring_passed,
        "actor_bp_authoring_target_dirty_after": False,
        "actor_bp_authoring_external_dirty_preserved": actual_authoring_passed,
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
            key: 1 if actual_authoring_passed else 0
            for key in LIVE_ACTOR_BP_ACTUAL_AUTHORING_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_LIVE_ACTOR_BP_DESTRUCTIVE_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_live_actor_bp_actual_authoring_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "live_actor_bp_actual_authoring_executed")
            == len(requested)
            and _truthy_count(
                requested,
                "actual_live_actor_bp_authoring_final_checkpoint_satisfied",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "actual_live_actor_bp_authoring_requires_final_user_checkpoint",
            )
            == 0
            and _truthy_count(requested, "production_path_write_allowed") == 0
            and _truthy_count(requested, "production_path_write_executed") == 0
            and _truthy_count(requested, "delete_asset_allowed") == 0
            and _truthy_count(requested, "rename_asset_allowed") == 0
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_LIVE_ACTOR_BP_DESTRUCTIVE_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_ACTUAL_AUTHORING_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_live_actor_bp_actual_authoring_batch_count": (
            len(requested)
        ),
        "section_257_264_summary_schema_matches_count": _truthy_count(
            requested, "section_257_264_summary_schema_matches"
        ),
        "section_257_264_summary_passed_count": _truthy_count(
            requested, "section_257_264_summary_passed"
        ),
        "section_257_264_live_actor_bp_preflight_ready_count": _truthy_count(
            requested, "section_257_264_live_actor_bp_preflight_ready"
        ),
        "section_257_264_mutation_outputs_closed_count": _truthy_count(
            requested, "section_257_264_mutation_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "actual_execution_checkpoint_satisfied_count": _truthy_count(
            requested, "actual_execution_checkpoint_satisfied"
        ),
        "target_scope_reconfirmed_count": _truthy_count(
            requested, "target_scope_reconfirmed"
        ),
        "variable_authoring_executed_count": _truthy_count(
            requested, "variable_authoring_executed"
        ),
        "component_authoring_executed_count": _truthy_count(
            requested, "component_authoring_executed"
        ),
        "default_authoring_executed_count": _truthy_count(
            requested, "default_authoring_executed"
        ),
        "compile_save_executed_count": _truthy_count(
            requested, "compile_save_executed"
        ),
        "readback_verified_count": _truthy_count(
            requested, "readback_verified"
        ),
        "dirty_baseline_preserved_count": _truthy_count(
            requested, "dirty_baseline_preserved"
        ),
        "destructive_outputs_closed_count": _truthy_count(
            requested, "destructive_outputs_closed"
        ),
        "result_has_no_error_count": _truthy_count(
            requested, "result_has_no_error"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "actual_live_actor_bp_authoring_requires_final_user_checkpoint_count": (
            _truthy_count(
                requested,
                "actual_live_actor_bp_authoring_requires_final_user_checkpoint",
            )
        ),
        "actual_live_actor_bp_authoring_final_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "actual_live_actor_bp_authoring_final_checkpoint_satisfied",
            )
        ),
        "variable_add_command_dispatched_count": _truthy_count(
            requested, "variable_add_command_dispatched"
        ),
        "variable_add_command_executed_count": _truthy_count(
            requested, "variable_add_command_executed"
        ),
        "component_add_command_dispatched_count": _truthy_count(
            requested, "component_add_command_dispatched"
        ),
        "component_add_command_executed_count": _truthy_count(
            requested, "component_add_command_executed"
        ),
        "default_write_command_dispatched_count": _truthy_count(
            requested, "default_write_command_dispatched"
        ),
        "default_write_command_executed_count": _truthy_count(
            requested, "default_write_command_executed"
        ),
        "actor_bp_authoring_command_dispatched_count": _truthy_count(
            requested, "actor_bp_authoring_command_dispatched"
        ),
        "actor_bp_authoring_command_executed_count": _truthy_count(
            requested, "actor_bp_authoring_command_executed"
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
        "actor_bp_authoring_target_dirty_after_count": _truthy_count(
            requested, "actor_bp_authoring_target_dirty_after"
        ),
        "actor_bp_authoring_external_dirty_preserved_count": _truthy_count(
            requested, "actor_bp_authoring_external_dirty_preserved"
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
            for key in LIVE_ACTOR_BP_ACTUAL_AUTHORING_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_LIVE_ACTOR_BP_DESTRUCTIVE_OUTPUT_COUNT_KEYS
        }
    )
    return summary
