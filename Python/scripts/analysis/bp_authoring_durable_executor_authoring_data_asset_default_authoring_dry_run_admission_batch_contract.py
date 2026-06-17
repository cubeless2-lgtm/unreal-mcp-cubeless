#!/usr/bin/env python
"""
Sections 457-464 durable executor DataAsset default authoring dry-run admission.

This contract follows the DataAsset default read-only preflight. It admits only
an offline dry-run plan for a disposable PrimaryDataAsset Blueprint under
_MCP_Temp. Actual DataAsset Blueprint creation, default-value mutation, compile,
save, delete, rename, overwrite, cleanup, and production writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_data_asset_default_readonly_preflight_batch_contract as readonly_preflight


DURABLE_EXECUTOR_AUTHORING_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_ADMISSION_BATCH_SCHEMA = (
    "section_457_464_durable_executor_authoring_data_asset_default_authoring_dry_run_admission_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_ADMISSION_BATCH_SUMMARY_SCHEMA = (
    "section_457_464_durable_executor_authoring_data_asset_default_authoring_dry_run_admission_batch_summary_v1"
)
DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_ADMISSION_RESULT_SCHEMA = (
    "section_457_464_data_asset_default_authoring_dry_run_admission_result_v1"
)
SECTION_449_456_DATA_ASSET_DEFAULT_READONLY_PREFLIGHT_SUMMARY_SCHEMA = (
    readonly_preflight
    .DURABLE_EXECUTOR_AUTHORING_DATA_ASSET_DEFAULT_READONLY_PREFLIGHT_BATCH_SUMMARY_SCHEMA
)
DEFAULT_DRY_RUN_ROOT = "/Game/_MCP_Temp/DurableSaveGate/DataAssetDryRun"
DEFAULT_TARGET_ASSET_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/DataAssetDryRun/"
    "DA_DurableDataAssetDryRun"
)
DEFAULT_PARENT_CLASS = "PrimaryDataAsset"
DEFAULT_DEFAULT_VALUE_PLAN = (
    "PrimaryAssetType=CodexDryRun",
    "PrimaryAssetName=DA_DurableDataAssetDryRun",
    "DisplayName=Durable DataAsset DryRun",
    "Revision=1",
)

UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_data_asset_default_readonly_preflight_batch_count",
    "section_449_data_asset_default_readonly_checkpoint_satisfied_count",
    "section_450_correct_project_data_asset_readonly_probe_recorded_count",
    "section_451_data_asset_blueprint_factory_prerequisites_verified_count",
    "section_452_primary_data_asset_default_readback_prerequisites_verified_count",
    "section_453_data_asset_default_mutation_outputs_blocked_count",
    "section_454_data_asset_compile_save_write_outputs_blocked_count",
    "section_455_data_asset_default_readonly_no_write_boundary_verified_count",
    "section_456_data_asset_default_readonly_preflight_release_ready_count",
    "data_asset_default_readonly_preflight_ready_count",
    "data_asset_default_actual_authoring_still_blocked_count",
    "final_durable_release_ready_count",
)
UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    readonly_preflight
    .BLOCKED_DATA_ASSET_DEFAULT_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS
)

DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_ADMISSION_PATH_COUNT_KEYS = (
    "section_457_data_asset_authoring_dry_run_checkpoint_satisfied_count",
    "section_458_data_asset_dry_run_scope_verified_count",
    "section_459_data_asset_default_value_plan_classified_count",
    "section_460_data_asset_default_readback_plan_recorded_count",
    "section_461_data_asset_default_mutation_command_blocked_count",
    "section_462_data_asset_compile_save_write_outputs_blocked_count",
    "section_463_data_asset_authoring_dry_run_no_write_boundary_verified_count",
    "section_464_data_asset_authoring_dry_run_admission_release_ready_count",
    "data_asset_default_authoring_dry_run_admission_ready_count",
    "data_asset_default_actual_authoring_still_blocked_count",
)
BLOCKED_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS = (
    "data_asset_authoring_admission_command_dispatched_count",
    "data_asset_authoring_admission_command_executed_count",
    "data_asset_blueprint_create_command_dispatched_count",
    "data_asset_blueprint_create_command_executed_count",
    "data_asset_default_mutation_command_dispatched_count",
    "data_asset_default_mutation_command_executed_count",
    "data_asset_default_value_changed_count",
    "data_asset_cdo_mutation_performed_count",
    "data_asset_property_added_count",
    "data_asset_property_removed_count",
    "data_asset_readback_command_dispatched_count",
    "data_asset_readback_command_executed_count",
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
BLOCKED_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_RESULT_KEYS = tuple(
    key.removesuffix("_count")
    for key in BLOCKED_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
)


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _count_is_one(summary: Dict[str, Any], key: str) -> bool:
    return bool(summary.get(key) == 1)


def _count_is_zero(summary: Dict[str, Any], key: str) -> bool:
    return bool(int(summary.get(key, 0) or 0) == 0)


def build_data_asset_default_authoring_dry_run_admission_result(
    *,
    dry_run_only: bool = True,
    dry_run_root: str = DEFAULT_DRY_RUN_ROOT,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    parent_class: str = DEFAULT_PARENT_CLASS,
    default_value_plan: Sequence[str] = DEFAULT_DEFAULT_VALUE_PLAN,
    default_readback_plan_recorded: bool = True,
    default_mutation_requires_live_contract: bool = True,
    data_asset_default_mutation_command_blocked: bool = True,
    actual_data_asset_authoring_allowed: bool = False,
    dirty_content_after_dry_run: Sequence[str] = (),
    dirty_maps_after_dry_run: Sequence[str] = (),
    data_asset_authoring_admission_command_dispatched: bool = False,
    data_asset_authoring_admission_command_executed: bool = False,
    data_asset_blueprint_create_command_dispatched: bool = False,
    data_asset_blueprint_create_command_executed: bool = False,
    data_asset_default_mutation_command_dispatched: bool = False,
    data_asset_default_mutation_command_executed: bool = False,
    data_asset_default_value_changed: bool = False,
    data_asset_cdo_mutation_performed: bool = False,
    data_asset_property_added: bool = False,
    data_asset_property_removed: bool = False,
    data_asset_readback_command_dispatched: bool = False,
    data_asset_readback_command_executed: bool = False,
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
        "schema": DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_ADMISSION_RESULT_SCHEMA,
        "dry_run_only": dry_run_only,
        "dry_run_root": dry_run_root,
        "target_asset_path": target_asset_path,
        "parent_class": parent_class,
        "default_value_plan": list(default_value_plan),
        "default_readback_plan_recorded": default_readback_plan_recorded,
        "default_mutation_requires_live_contract": (
            default_mutation_requires_live_contract
        ),
        "data_asset_default_mutation_command_blocked": (
            data_asset_default_mutation_command_blocked
        ),
        "actual_data_asset_authoring_allowed": actual_data_asset_authoring_allowed,
        "dirty_content_after_dry_run": list(dirty_content_after_dry_run),
        "dirty_maps_after_dry_run": list(dirty_maps_after_dry_run),
        "data_asset_authoring_admission_command_dispatched": (
            data_asset_authoring_admission_command_dispatched
        ),
        "data_asset_authoring_admission_command_executed": (
            data_asset_authoring_admission_command_executed
        ),
        "data_asset_blueprint_create_command_dispatched": (
            data_asset_blueprint_create_command_dispatched
        ),
        "data_asset_blueprint_create_command_executed": (
            data_asset_blueprint_create_command_executed
        ),
        "data_asset_default_mutation_command_dispatched": (
            data_asset_default_mutation_command_dispatched
        ),
        "data_asset_default_mutation_command_executed": (
            data_asset_default_mutation_command_executed
        ),
        "data_asset_default_value_changed": data_asset_default_value_changed,
        "data_asset_cdo_mutation_performed": data_asset_cdo_mutation_performed,
        "data_asset_property_added": data_asset_property_added,
        "data_asset_property_removed": data_asset_property_removed,
        "data_asset_readback_command_dispatched": (
            data_asset_readback_command_dispatched
        ),
        "data_asset_readback_command_executed": (
            data_asset_readback_command_executed
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
            BLOCKED_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS,
            BLOCKED_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_RESULT_KEYS,
        )
    }


def build_durable_executor_authoring_data_asset_default_authoring_dry_run_admission_batch_contract(
    requested: bool,
    section_449_456_data_asset_default_readonly_preflight_summary: Dict[str, Any],
    data_asset_default_authoring_dry_run_admission_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_449_456_summary_schema_matches = bool(
        section_449_456_data_asset_default_readonly_preflight_summary.get(
            "schema"
        )
        == SECTION_449_456_DATA_ASSET_DEFAULT_READONLY_PREFLIGHT_SUMMARY_SCHEMA
    )
    section_449_456_summary_passed = bool(
        section_449_456_data_asset_default_readonly_preflight_summary.get(
            "status"
        )
        == "passed"
    )
    upstream_readonly_preflight_ready = all(
        _count_is_one(
            section_449_456_data_asset_default_readonly_preflight_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_outputs_closed = all(
        _count_is_zero(
            section_449_456_data_asset_default_readonly_preflight_summary,
            key,
        )
        for key in UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        data_asset_default_authoring_dry_run_admission_result.get("schema")
        == DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_ADMISSION_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and section_449_456_summary_schema_matches
        and section_449_456_summary_passed
        and upstream_readonly_preflight_ready
        and upstream_outputs_closed
    )
    dry_run_scope_verified = bool(
        data_asset_default_authoring_dry_run_admission_result.get(
            "dry_run_only"
        )
        and data_asset_default_authoring_dry_run_admission_result.get(
            "dry_run_root"
        )
        == DEFAULT_DRY_RUN_ROOT
        and data_asset_default_authoring_dry_run_admission_result.get(
            "target_asset_path"
        )
        == DEFAULT_TARGET_ASSET_PATH
        and str(
            data_asset_default_authoring_dry_run_admission_result.get(
                "target_asset_path", ""
            )
        ).startswith("/Game/_MCP_Temp/")
        and data_asset_default_authoring_dry_run_admission_result.get(
            "parent_class"
        )
        == DEFAULT_PARENT_CLASS
        and not data_asset_default_authoring_dry_run_admission_result.get(
            "actual_data_asset_authoring_allowed"
        )
    )
    default_value_plan_classified = bool(
        tuple(
            data_asset_default_authoring_dry_run_admission_result.get(
                "default_value_plan", ()
            )
            or ()
        )
        == DEFAULT_DEFAULT_VALUE_PLAN
    )
    default_readback_plan_recorded = bool(
        data_asset_default_authoring_dry_run_admission_result.get(
            "default_readback_plan_recorded"
        )
    )
    default_mutation_command_blocked = bool(
        data_asset_default_authoring_dry_run_admission_result.get(
            "default_mutation_requires_live_contract"
        )
        and data_asset_default_authoring_dry_run_admission_result.get(
            "data_asset_default_mutation_command_blocked"
        )
        and not data_asset_default_authoring_dry_run_admission_result.get(
            "actual_data_asset_authoring_allowed"
        )
        and all(
            not data_asset_default_authoring_dry_run_admission_result.get(key)
            for key in (
                "data_asset_authoring_admission_command_dispatched",
                "data_asset_authoring_admission_command_executed",
                "data_asset_blueprint_create_command_dispatched",
                "data_asset_blueprint_create_command_executed",
                "data_asset_default_mutation_command_dispatched",
                "data_asset_default_mutation_command_executed",
                "data_asset_default_value_changed",
                "data_asset_cdo_mutation_performed",
                "data_asset_property_added",
                "data_asset_property_removed",
                "data_asset_readback_command_dispatched",
                "data_asset_readback_command_executed",
            )
        )
    )
    compile_save_write_outputs_blocked = all(
        not data_asset_default_authoring_dry_run_admission_result.get(key)
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
        not data_asset_default_authoring_dry_run_admission_result.get(key)
        for key in BLOCKED_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        all_outputs_blocked
        and not data_asset_default_authoring_dry_run_admission_result.get(
            "dirty_content_after_dry_run"
        )
        and not data_asset_default_authoring_dry_run_admission_result.get(
            "dirty_maps_after_dry_run"
        )
    )
    result_has_no_error = bool(
        data_asset_default_authoring_dry_run_admission_result.get("error")
        in (None, "")
    )
    dry_run_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and dry_run_scope_verified
        and default_value_plan_classified
        and default_readback_plan_recorded
        and default_mutation_command_blocked
        and compile_save_write_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_data_asset_default_authoring_dry_run_admission_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_ADMISSION_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_449_456_summary_schema_matches": (
            section_449_456_summary_schema_matches
        ),
        "section_449_456_summary_passed": section_449_456_summary_passed,
        "section_449_456_data_asset_default_readonly_preflight_ready": (
            upstream_readonly_preflight_ready
        ),
        "section_449_456_outputs_closed": upstream_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "data_asset_authoring_dry_run_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "data_asset_dry_run_scope_verified": dry_run_scope_verified,
        "data_asset_default_value_plan_classified": (
            default_value_plan_classified
        ),
        "data_asset_default_readback_plan_recorded": (
            default_readback_plan_recorded
        ),
        "data_asset_default_mutation_command_blocked": (
            default_mutation_command_blocked
        ),
        "data_asset_compile_save_write_outputs_blocked": (
            compile_save_write_outputs_blocked
        ),
        "data_asset_authoring_dry_run_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_457_data_asset_authoring_dry_run_checkpoint_satisfied": (
            dry_run_ready
        ),
        "section_458_data_asset_dry_run_scope_verified": dry_run_ready,
        "section_459_data_asset_default_value_plan_classified": dry_run_ready,
        "section_460_data_asset_default_readback_plan_recorded": dry_run_ready,
        "section_461_data_asset_default_mutation_command_blocked": (
            dry_run_ready
        ),
        "section_462_data_asset_compile_save_write_outputs_blocked": (
            dry_run_ready
        ),
        "section_463_data_asset_authoring_dry_run_no_write_boundary_verified": (
            dry_run_ready
        ),
        "section_464_data_asset_authoring_dry_run_admission_release_ready": (
            dry_run_ready
        ),
        "data_asset_default_authoring_dry_run_admission_ready": dry_run_ready,
        "data_asset_default_actual_authoring_still_blocked": dry_run_ready,
        "final_durable_release_ready": dry_run_ready,
        **{
            key: 1 if dry_run_ready else 0
            for key in (
                DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_ADMISSION_PATH_COUNT_KEYS
            )
        },
        **_blocked_output_counts(data_asset_default_authoring_dry_run_admission_result),
    }


def summarize_durable_executor_authoring_data_asset_default_authoring_dry_run_admission_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "data_asset_default_authoring_dry_run_admission_ready",
            )
            == len(requested)
            and _truthy_count(
                requested, "data_asset_default_actual_authoring_still_blocked"
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in (
                    BLOCKED_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
                )
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_ADMISSION_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_data_asset_default_authoring_dry_run_admission_batch_count": (
            len(requested)
        ),
        "section_449_456_summary_schema_matches_count": _truthy_count(
            requested, "section_449_456_summary_schema_matches"
        ),
        "section_449_456_summary_passed_count": _truthy_count(
            requested, "section_449_456_summary_passed"
        ),
        "section_449_456_data_asset_default_readonly_preflight_ready_count": (
            _truthy_count(
                requested,
                "section_449_456_data_asset_default_readonly_preflight_ready",
            )
        ),
        "section_449_456_outputs_closed_count": _truthy_count(
            requested, "section_449_456_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "data_asset_authoring_dry_run_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "data_asset_authoring_dry_run_checkpoint_satisfied",
            )
        ),
        "data_asset_dry_run_scope_verified_count": _truthy_count(
            requested, "data_asset_dry_run_scope_verified"
        ),
        "data_asset_default_value_plan_classified_count": _truthy_count(
            requested, "data_asset_default_value_plan_classified"
        ),
        "data_asset_default_readback_plan_recorded_count": _truthy_count(
            requested, "data_asset_default_readback_plan_recorded"
        ),
        "data_asset_default_mutation_command_blocked_count": _truthy_count(
            requested, "data_asset_default_mutation_command_blocked"
        ),
        "data_asset_compile_save_write_outputs_blocked_count": _truthy_count(
            requested, "data_asset_compile_save_write_outputs_blocked"
        ),
        "data_asset_authoring_dry_run_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "data_asset_authoring_dry_run_no_write_boundary_verified",
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
            for key in DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_ADMISSION_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in (
                BLOCKED_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
            )
        }
    )
    return summary
