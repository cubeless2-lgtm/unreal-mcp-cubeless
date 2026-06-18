#!/usr/bin/env python
"""
Sections 481-488 durable executor non-Actor actual temp checkpoint bridge blocker.

This contract follows the DataAsset and Blueprint Function Library dry-run
admission gates plus the UserWidget bridge port ownership preflight. It records
that non-Actor actual temp asset checkpoints must remain blocked while
127.0.0.1:55557 is owned by the wrong workspace editor. Actual DataAsset/BFL
creation, readback, compile, save, delete, rename, overwrite, cleanup, and
production writes remain closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batch_contract as bfl_dry_run
import bp_authoring_durable_executor_authoring_data_asset_default_authoring_dry_run_admission_batch_contract as data_asset_dry_run
import bp_authoring_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_contract as bridge_port
import project_paths


DURABLE_EXECUTOR_AUTHORING_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_BATCH_SCHEMA = (
    "section_481_488_durable_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_BATCH_SUMMARY_SCHEMA = (
    "section_481_488_durable_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batch_summary_v1"
)
NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_RESULT_SCHEMA = (
    "section_481_488_non_actor_actual_temp_checkpoint_bridge_blocker_result_v1"
)
SECTION_441_448_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_SUMMARY_SCHEMA = (
    bridge_port
    .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_BATCH_SUMMARY_SCHEMA
)
SECTION_457_464_DATA_ASSET_DRY_RUN_SUMMARY_SCHEMA = (
    data_asset_dry_run
    .DURABLE_EXECUTOR_AUTHORING_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_ADMISSION_BATCH_SUMMARY_SCHEMA
)
SECTION_473_480_BFL_DRY_RUN_SUMMARY_SCHEMA = (
    bfl_dry_run
    .DURABLE_EXECUTOR_AUTHORING_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_ADMISSION_BATCH_SUMMARY_SCHEMA
)

DEFAULT_PROJECT_FILE_PATH = project_paths.default_cubeless_uproject()
DEFAULT_BRIDGE_HOST = "127.0.0.1"
DEFAULT_BRIDGE_PORT = 55557
DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH = project_paths.default_wrong_workspace_uproject()
DEFAULT_DATA_ASSET_TARGET_ASSET_PATH = (
    data_asset_dry_run.DEFAULT_TARGET_ASSET_PATH.replace(
        "DataAssetDryRun", "DataAssetActual"
    ).replace("DA_DurableDataAssetDryRun", "DA_DurableDataAssetActual")
)
DEFAULT_BFL_TARGET_ASSET_PATH = (
    bfl_dry_run.DEFAULT_TARGET_ASSET_PATH.replace(
        "FunctionLibraryDryRun", "FunctionLibraryActual"
    ).replace(
        "BFL_DurableFunctionLibraryDryRun",
        "BFL_DurableFunctionLibraryActual",
    )
)

BRIDGE_UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_count",
    "section_441_user_widget_bridge_port_ownership_checkpoint_satisfied_count",
    "section_442_primary_bridge_port_probe_recorded_count",
    "section_443_wrong_workspace_port_owner_detected_count",
    "section_444_correct_workspace_bridge_port_unavailable_count",
    "section_445_correct_workspace_bridge_start_blocked_count",
    "section_446_live_user_widget_mutation_bridge_blocked_count",
    "section_447_user_widget_bridge_port_no_dispatch_verified_count",
    "section_448_user_widget_bridge_port_ownership_preflight_release_ready_count",
    "user_widget_bridge_port_ownership_preflight_ready_count",
    "correct_workspace_bridge_port_release_still_required_count",
    "final_durable_release_ready_count",
)
BRIDGE_UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    bridge_port
    .BLOCKED_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_OUTPUT_COUNT_KEYS
)
DATA_ASSET_UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_data_asset_default_authoring_dry_run_admission_batch_count",
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
    "final_durable_release_ready_count",
)
DATA_ASSET_UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    data_asset_dry_run
    .BLOCKED_DATA_ASSET_DEFAULT_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
)
BFL_UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_blueprint_function_library_authoring_dry_run_admission_batch_count",
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
    "final_durable_release_ready_count",
)
BFL_UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS = (
    bfl_dry_run
    .BLOCKED_BLUEPRINT_FUNCTION_LIBRARY_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS
)

NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_PATH_COUNT_KEYS = (
    "section_481_non_actor_actual_temp_checkpoint_bridge_blocker_checkpoint_satisfied_count",
    "section_482_data_asset_actual_temp_checkpoint_preconditions_recorded_count",
    "section_483_bfl_actual_temp_checkpoint_preconditions_recorded_count",
    "section_484_wrong_workspace_bridge_blocker_reconfirmed_count",
    "section_485_live_non_actor_temp_creation_dispatch_blocked_count",
    "section_486_non_actor_temp_compile_save_write_outputs_blocked_count",
    "section_487_non_actor_actual_temp_checkpoint_no_write_boundary_verified_count",
    "section_488_non_actor_actual_temp_checkpoint_bridge_blocker_release_ready_count",
    "non_actor_actual_temp_checkpoint_bridge_blocker_ready_count",
    "non_actor_actual_temp_checkpoint_still_blocked_count",
)
BLOCKED_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_OUTPUT_COUNT_KEYS = (
    "correct_workspace_bridge_started_count",
    "correct_workspace_bridge_verified_count",
    "non_actor_actual_temp_checkpoint_command_dispatched_count",
    "non_actor_actual_temp_checkpoint_command_executed_count",
    "data_asset_actual_temp_create_command_dispatched_count",
    "data_asset_actual_temp_create_command_executed_count",
    "bfl_actual_temp_create_command_dispatched_count",
    "bfl_actual_temp_create_command_executed_count",
    "data_asset_default_mutation_command_dispatched_count",
    "data_asset_default_mutation_command_executed_count",
    "bfl_graph_mutation_command_dispatched_count",
    "bfl_graph_mutation_command_executed_count",
    "non_actor_readback_command_dispatched_count",
    "non_actor_readback_command_executed_count",
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
BLOCKED_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_RESULT_KEYS = tuple(
    key.removesuffix("_count")
    for key in BLOCKED_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_OUTPUT_COUNT_KEYS
)


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _count_is_one(summary: Dict[str, Any], key: str) -> bool:
    return bool(summary.get(key) == 1)


def _count_is_zero(summary: Dict[str, Any], key: str) -> bool:
    return bool(int(summary.get(key, 0) or 0) == 0)


def build_non_actor_actual_temp_checkpoint_bridge_blocker_result(
    *,
    project_file_path: str = DEFAULT_PROJECT_FILE_PATH,
    bridge_host: str = DEFAULT_BRIDGE_HOST,
    bridge_port_number: int = DEFAULT_BRIDGE_PORT,
    wrong_workspace_project_file_path: str = DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH,
    data_asset_target_asset_path: str = DEFAULT_DATA_ASSET_TARGET_ASSET_PATH,
    bfl_target_asset_path: str = DEFAULT_BFL_TARGET_ASSET_PATH,
    correct_workspace_bridge_required: bool = True,
    correct_workspace_bridge_verified: bool = False,
    wrong_workspace_bridge_owner_detected: bool = True,
    actual_temp_checkpoint_allowed: bool = False,
    dirty_content_before: Sequence[str] = (),
    dirty_content_after: Sequence[str] = (),
    dirty_maps_before: Sequence[str] = (),
    dirty_maps_after: Sequence[str] = (),
    external_dirty_preserved: bool = True,
    correct_workspace_bridge_started: bool = False,
    non_actor_actual_temp_checkpoint_command_dispatched: bool = False,
    non_actor_actual_temp_checkpoint_command_executed: bool = False,
    data_asset_actual_temp_create_command_dispatched: bool = False,
    data_asset_actual_temp_create_command_executed: bool = False,
    bfl_actual_temp_create_command_dispatched: bool = False,
    bfl_actual_temp_create_command_executed: bool = False,
    data_asset_default_mutation_command_dispatched: bool = False,
    data_asset_default_mutation_command_executed: bool = False,
    bfl_graph_mutation_command_dispatched: bool = False,
    bfl_graph_mutation_command_executed: bool = False,
    non_actor_readback_command_dispatched: bool = False,
    non_actor_readback_command_executed: bool = False,
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
        "schema": NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_RESULT_SCHEMA,
        "project_file_path": project_file_path,
        "bridge_host": bridge_host,
        "bridge_port": bridge_port_number,
        "wrong_workspace_project_file_path": wrong_workspace_project_file_path,
        "data_asset_target_asset_path": data_asset_target_asset_path,
        "bfl_target_asset_path": bfl_target_asset_path,
        "correct_workspace_bridge_required": correct_workspace_bridge_required,
        "correct_workspace_bridge_verified": correct_workspace_bridge_verified,
        "wrong_workspace_bridge_owner_detected": wrong_workspace_bridge_owner_detected,
        "actual_temp_checkpoint_allowed": actual_temp_checkpoint_allowed,
        "dirty_content_before": list(dirty_content_before),
        "dirty_content_after": list(dirty_content_after),
        "dirty_maps_before": list(dirty_maps_before),
        "dirty_maps_after": list(dirty_maps_after),
        "external_dirty_preserved": external_dirty_preserved,
        "correct_workspace_bridge_started": correct_workspace_bridge_started,
        "non_actor_actual_temp_checkpoint_command_dispatched": (
            non_actor_actual_temp_checkpoint_command_dispatched
        ),
        "non_actor_actual_temp_checkpoint_command_executed": (
            non_actor_actual_temp_checkpoint_command_executed
        ),
        "data_asset_actual_temp_create_command_dispatched": (
            data_asset_actual_temp_create_command_dispatched
        ),
        "data_asset_actual_temp_create_command_executed": (
            data_asset_actual_temp_create_command_executed
        ),
        "bfl_actual_temp_create_command_dispatched": (
            bfl_actual_temp_create_command_dispatched
        ),
        "bfl_actual_temp_create_command_executed": (
            bfl_actual_temp_create_command_executed
        ),
        "data_asset_default_mutation_command_dispatched": (
            data_asset_default_mutation_command_dispatched
        ),
        "data_asset_default_mutation_command_executed": (
            data_asset_default_mutation_command_executed
        ),
        "bfl_graph_mutation_command_dispatched": (
            bfl_graph_mutation_command_dispatched
        ),
        "bfl_graph_mutation_command_executed": (
            bfl_graph_mutation_command_executed
        ),
        "non_actor_readback_command_dispatched": non_actor_readback_command_dispatched,
        "non_actor_readback_command_executed": non_actor_readback_command_executed,
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
            BLOCKED_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_OUTPUT_COUNT_KEYS,
            BLOCKED_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_RESULT_KEYS,
        )
    }


def build_durable_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batch_contract(
    requested: bool,
    section_441_448_bridge_port_ownership_preflight_summary: Dict[str, Any],
    section_457_464_data_asset_dry_run_admission_summary: Dict[str, Any],
    section_473_480_bfl_dry_run_admission_summary: Dict[str, Any],
    non_actor_actual_temp_checkpoint_bridge_blocker_result: Dict[str, Any],
) -> Dict[str, Any]:
    bridge_schema_matches = bool(
        section_441_448_bridge_port_ownership_preflight_summary.get("schema")
        == SECTION_441_448_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_SUMMARY_SCHEMA
    )
    bridge_summary_passed = bool(
        section_441_448_bridge_port_ownership_preflight_summary.get("status")
        == "passed"
    )
    bridge_blocker_ready = all(
        _count_is_one(section_441_448_bridge_port_ownership_preflight_summary, key)
        for key in BRIDGE_UPSTREAM_READY_COUNT_KEYS
    )
    bridge_outputs_closed = all(
        _count_is_zero(section_441_448_bridge_port_ownership_preflight_summary, key)
        for key in BRIDGE_UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    data_asset_schema_matches = bool(
        section_457_464_data_asset_dry_run_admission_summary.get("schema")
        == SECTION_457_464_DATA_ASSET_DRY_RUN_SUMMARY_SCHEMA
    )
    data_asset_summary_passed = bool(
        section_457_464_data_asset_dry_run_admission_summary.get("status")
        == "passed"
    )
    data_asset_dry_run_ready = all(
        _count_is_one(section_457_464_data_asset_dry_run_admission_summary, key)
        for key in DATA_ASSET_UPSTREAM_READY_COUNT_KEYS
    )
    data_asset_outputs_closed = all(
        _count_is_zero(section_457_464_data_asset_dry_run_admission_summary, key)
        for key in DATA_ASSET_UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    bfl_schema_matches = bool(
        section_473_480_bfl_dry_run_admission_summary.get("schema")
        == SECTION_473_480_BFL_DRY_RUN_SUMMARY_SCHEMA
    )
    bfl_summary_passed = bool(
        section_473_480_bfl_dry_run_admission_summary.get("status") == "passed"
    )
    bfl_dry_run_ready = all(
        _count_is_one(section_473_480_bfl_dry_run_admission_summary, key)
        for key in BFL_UPSTREAM_READY_COUNT_KEYS
    )
    bfl_outputs_closed = all(
        _count_is_zero(section_473_480_bfl_dry_run_admission_summary, key)
        for key in BFL_UPSTREAM_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        non_actor_actual_temp_checkpoint_bridge_blocker_result.get("schema")
        == NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_RESULT_SCHEMA
    )
    checkpoint_satisfied = bool(
        requested
        and bridge_schema_matches
        and bridge_summary_passed
        and bridge_blocker_ready
        and bridge_outputs_closed
        and data_asset_schema_matches
        and data_asset_summary_passed
        and data_asset_dry_run_ready
        and data_asset_outputs_closed
        and bfl_schema_matches
        and bfl_summary_passed
        and bfl_dry_run_ready
        and bfl_outputs_closed
    )
    data_asset_preconditions_recorded = bool(
        non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "data_asset_target_asset_path"
        )
        == DEFAULT_DATA_ASSET_TARGET_ASSET_PATH
        and str(
            non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
                "data_asset_target_asset_path", ""
            )
        ).startswith("/Game/_MCP_Temp/")
    )
    bfl_preconditions_recorded = bool(
        non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "bfl_target_asset_path"
        )
        == DEFAULT_BFL_TARGET_ASSET_PATH
        and str(
            non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
                "bfl_target_asset_path", ""
            )
        ).startswith("/Game/_MCP_Temp/")
    )
    wrong_workspace_bridge_blocker_reconfirmed = bool(
        non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "project_file_path"
        )
        == DEFAULT_PROJECT_FILE_PATH
        and non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "bridge_host"
        )
        == DEFAULT_BRIDGE_HOST
        and non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "bridge_port"
        )
        == DEFAULT_BRIDGE_PORT
        and non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "wrong_workspace_project_file_path"
        )
        == DEFAULT_WRONG_WORKSPACE_PROJECT_FILE_PATH
        and non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "correct_workspace_bridge_required"
        )
        and not non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "correct_workspace_bridge_verified"
        )
        and non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "wrong_workspace_bridge_owner_detected"
        )
    )
    live_dispatch_blocked = bool(
        not non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "actual_temp_checkpoint_allowed"
        )
        and all(
            not non_actor_actual_temp_checkpoint_bridge_blocker_result.get(key)
            for key in (
                "correct_workspace_bridge_started",
                "correct_workspace_bridge_verified",
                "non_actor_actual_temp_checkpoint_command_dispatched",
                "non_actor_actual_temp_checkpoint_command_executed",
                "data_asset_actual_temp_create_command_dispatched",
                "data_asset_actual_temp_create_command_executed",
                "bfl_actual_temp_create_command_dispatched",
                "bfl_actual_temp_create_command_executed",
                "data_asset_default_mutation_command_dispatched",
                "data_asset_default_mutation_command_executed",
                "bfl_graph_mutation_command_dispatched",
                "bfl_graph_mutation_command_executed",
                "non_actor_readback_command_dispatched",
                "non_actor_readback_command_executed",
            )
        )
    )
    compile_save_write_outputs_blocked = all(
        not non_actor_actual_temp_checkpoint_bridge_blocker_result.get(key)
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
        not non_actor_actual_temp_checkpoint_bridge_blocker_result.get(key)
        for key in BLOCKED_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_RESULT_KEYS
    )
    no_write_boundary_verified = bool(
        all_outputs_blocked
        and non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "dirty_content_before"
        )
        == non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "dirty_content_after"
        )
        and non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "dirty_maps_before"
        )
        == non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "dirty_maps_after"
        )
        and not non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "dirty_content_after"
        )
        and not non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "dirty_maps_after"
        )
        and non_actor_actual_temp_checkpoint_bridge_blocker_result.get(
            "external_dirty_preserved"
        )
    )
    result_has_no_error = bool(
        non_actor_actual_temp_checkpoint_bridge_blocker_result.get("error")
        in (None, "")
    )
    blocker_ready = bool(
        checkpoint_satisfied
        and result_schema_matches
        and data_asset_preconditions_recorded
        and bfl_preconditions_recorded
        and wrong_workspace_bridge_blocker_reconfirmed
        and live_dispatch_blocked
        and compile_save_write_outputs_blocked
        and no_write_boundary_verified
        and result_has_no_error
    )
    return {
        "id": "durable_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batch",
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_441_448_summary_schema_matches": bridge_schema_matches,
        "section_441_448_summary_passed": bridge_summary_passed,
        "section_441_448_bridge_blocker_ready": bridge_blocker_ready,
        "section_441_448_outputs_closed": bridge_outputs_closed,
        "section_457_464_summary_schema_matches": data_asset_schema_matches,
        "section_457_464_summary_passed": data_asset_summary_passed,
        "section_457_464_data_asset_dry_run_ready": data_asset_dry_run_ready,
        "section_457_464_outputs_closed": data_asset_outputs_closed,
        "section_473_480_summary_schema_matches": bfl_schema_matches,
        "section_473_480_summary_passed": bfl_summary_passed,
        "section_473_480_bfl_dry_run_ready": bfl_dry_run_ready,
        "section_473_480_outputs_closed": bfl_outputs_closed,
        "result_schema_matches": result_schema_matches,
        "non_actor_actual_temp_checkpoint_bridge_blocker_checkpoint_satisfied": (
            checkpoint_satisfied
        ),
        "data_asset_actual_temp_checkpoint_preconditions_recorded": (
            data_asset_preconditions_recorded
        ),
        "bfl_actual_temp_checkpoint_preconditions_recorded": (
            bfl_preconditions_recorded
        ),
        "wrong_workspace_bridge_blocker_reconfirmed": (
            wrong_workspace_bridge_blocker_reconfirmed
        ),
        "live_non_actor_temp_creation_dispatch_blocked": live_dispatch_blocked,
        "non_actor_temp_compile_save_write_outputs_blocked": (
            compile_save_write_outputs_blocked
        ),
        "non_actor_actual_temp_checkpoint_no_write_boundary_verified": (
            no_write_boundary_verified
        ),
        "result_has_no_error": result_has_no_error,
        "section_481_non_actor_actual_temp_checkpoint_bridge_blocker_checkpoint_satisfied": (
            blocker_ready
        ),
        "section_482_data_asset_actual_temp_checkpoint_preconditions_recorded": (
            blocker_ready
        ),
        "section_483_bfl_actual_temp_checkpoint_preconditions_recorded": (
            blocker_ready
        ),
        "section_484_wrong_workspace_bridge_blocker_reconfirmed": blocker_ready,
        "section_485_live_non_actor_temp_creation_dispatch_blocked": blocker_ready,
        "section_486_non_actor_temp_compile_save_write_outputs_blocked": (
            blocker_ready
        ),
        "section_487_non_actor_actual_temp_checkpoint_no_write_boundary_verified": (
            blocker_ready
        ),
        "section_488_non_actor_actual_temp_checkpoint_bridge_blocker_release_ready": (
            blocker_ready
        ),
        "non_actor_actual_temp_checkpoint_bridge_blocker_ready": blocker_ready,
        "non_actor_actual_temp_checkpoint_still_blocked": blocker_ready,
        "final_durable_release_ready": blocker_ready,
        **{
            key: 1 if blocker_ready else 0
            for key in (
                NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_PATH_COUNT_KEYS
            )
        },
        **_blocked_output_counts(
            non_actor_actual_temp_checkpoint_bridge_blocker_result
        ),
    }


def summarize_durable_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "non_actor_actual_temp_checkpoint_bridge_blocker_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "non_actor_actual_temp_checkpoint_still_blocked",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_non_actor_actual_temp_checkpoint_bridge_blocker_batch_count": (
            len(requested)
        ),
        "section_441_448_summary_schema_matches_count": _truthy_count(
            requested, "section_441_448_summary_schema_matches"
        ),
        "section_441_448_summary_passed_count": _truthy_count(
            requested, "section_441_448_summary_passed"
        ),
        "section_441_448_bridge_blocker_ready_count": _truthy_count(
            requested, "section_441_448_bridge_blocker_ready"
        ),
        "section_441_448_outputs_closed_count": _truthy_count(
            requested, "section_441_448_outputs_closed"
        ),
        "section_457_464_summary_schema_matches_count": _truthy_count(
            requested, "section_457_464_summary_schema_matches"
        ),
        "section_457_464_summary_passed_count": _truthy_count(
            requested, "section_457_464_summary_passed"
        ),
        "section_457_464_data_asset_dry_run_ready_count": _truthy_count(
            requested, "section_457_464_data_asset_dry_run_ready"
        ),
        "section_457_464_outputs_closed_count": _truthy_count(
            requested, "section_457_464_outputs_closed"
        ),
        "section_473_480_summary_schema_matches_count": _truthy_count(
            requested, "section_473_480_summary_schema_matches"
        ),
        "section_473_480_summary_passed_count": _truthy_count(
            requested, "section_473_480_summary_passed"
        ),
        "section_473_480_bfl_dry_run_ready_count": _truthy_count(
            requested, "section_473_480_bfl_dry_run_ready"
        ),
        "section_473_480_outputs_closed_count": _truthy_count(
            requested, "section_473_480_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "non_actor_actual_temp_checkpoint_bridge_blocker_checkpoint_satisfied_count": (
            _truthy_count(
                requested,
                "non_actor_actual_temp_checkpoint_bridge_blocker_checkpoint_satisfied",
            )
        ),
        "data_asset_actual_temp_checkpoint_preconditions_recorded_count": (
            _truthy_count(
                requested,
                "data_asset_actual_temp_checkpoint_preconditions_recorded",
            )
        ),
        "bfl_actual_temp_checkpoint_preconditions_recorded_count": (
            _truthy_count(
                requested, "bfl_actual_temp_checkpoint_preconditions_recorded"
            )
        ),
        "wrong_workspace_bridge_blocker_reconfirmed_count": _truthy_count(
            requested, "wrong_workspace_bridge_blocker_reconfirmed"
        ),
        "live_non_actor_temp_creation_dispatch_blocked_count": _truthy_count(
            requested, "live_non_actor_temp_creation_dispatch_blocked"
        ),
        "non_actor_temp_compile_save_write_outputs_blocked_count": _truthy_count(
            requested, "non_actor_temp_compile_save_write_outputs_blocked"
        ),
        "non_actor_actual_temp_checkpoint_no_write_boundary_verified_count": (
            _truthy_count(
                requested,
                "non_actor_actual_temp_checkpoint_no_write_boundary_verified",
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
            for key in NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_BRIDGE_BLOCKER_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_NON_ACTOR_ACTUAL_TEMP_CHECKPOINT_OUTPUT_COUNT_KEYS
        }
    )
    return summary
