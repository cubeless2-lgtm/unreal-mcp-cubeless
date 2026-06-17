#!/usr/bin/env python
"""
Sections 273-280 durable executor live Actor Blueprint component/default readback.

This contract extends the Section 265-272 actual Actor Blueprint authoring
evidence with a readback-only component/default/type gate. It proves the saved
temporary Actor Blueprint can be re-read with class, variable default, component
template, and CDO tag evidence, while unsupported broader Blueprint classes stay
blocked until a separate authoring contract exists.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract as actual_authoring


DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_BATCH_SCHEMA = (
    "section_273_280_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_BATCH_SUMMARY_SCHEMA = (
    "section_273_280_durable_executor_authoring_live_actor_bp_component_default_readback_batch_summary_v1"
)
LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_RESULT_SCHEMA = (
    "section_273_280_live_actor_bp_component_default_readback_result_v1"
)
SECTION_265_272_LIVE_ACTOR_BP_ACTUAL_AUTHORING_SUMMARY_SCHEMA = (
    actual_authoring
    .DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_ACTUAL_AUTHORING_BATCH_SUMMARY_SCHEMA
)
DEFAULT_TARGET_ASSET_PATH = actual_authoring.DEFAULT_TARGET_ASSET_PATH
DEFAULT_GENERATED_CLASS_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/"
    "BP_DurableSaveGatePrep.BP_DurableSaveGatePrep_C"
)
DEFAULT_BLUEPRINT_PARENT_CLASS = "Actor"
DEFAULT_VARIABLE_NAME = actual_authoring.DEFAULT_VARIABLE_NAME
DEFAULT_VARIABLE_TYPE = "float"
DEFAULT_VARIABLE_VALUE = actual_authoring.DEFAULT_VARIABLE_VALUE
DEFAULT_COMPONENT_NAME = actual_authoring.DEFAULT_COMPONENT_NAME
DEFAULT_COMPONENT_CLASS = actual_authoring.DEFAULT_COMPONENT_CLASS
DEFAULT_TAG_NAME = actual_authoring.DEFAULT_TAG_NAME
DEFAULT_UNSUPPORTED_BLUEPRINT_CLASSES = (
    "UserWidget",
    "DataAsset",
    "AnimBlueprint",
)
UPSTREAM_READY_COUNT_KEYS = (
    "durable_requested_executor_authoring_live_actor_bp_actual_authoring_batch_count",
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
    "actual_live_actor_bp_authoring_final_checkpoint_satisfied_count",
    "actor_bp_authoring_external_dirty_preserved_count",
    "final_durable_release_ready_count",
)
UPSTREAM_DESTRUCTIVE_OUTPUTS_CLOSED_COUNT_KEYS = (
    "actual_live_actor_bp_authoring_requires_final_user_checkpoint_count",
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
LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_PATH_COUNT_KEYS = (
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
)
BLOCKED_LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_OUTPUT_COUNT_KEYS = (
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


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _count_is_one(summary: Dict[str, Any], key: str) -> bool:
    return bool(summary.get(key) == 1)


def _count_is_zero(summary: Dict[str, Any], key: str) -> bool:
    return bool(int(summary.get(key, 0) or 0) == 0)


def build_live_actor_bp_component_default_readback_result(
    *,
    target_asset_path: str = DEFAULT_TARGET_ASSET_PATH,
    generated_class_path: str = DEFAULT_GENERATED_CLASS_PATH,
    blueprint_parent_class: str = DEFAULT_BLUEPRINT_PARENT_CLASS,
    cdo_is_actor: bool = True,
    variable_name: str = DEFAULT_VARIABLE_NAME,
    variable_type: str = DEFAULT_VARIABLE_TYPE,
    scalar_default_value: float = DEFAULT_VARIABLE_VALUE,
    variable_default_readback_matches: bool = True,
    component_name: str = DEFAULT_COMPONENT_NAME,
    component_class: str = DEFAULT_COMPONENT_CLASS,
    component_template_owner_is_actor_cdo: bool = True,
    component_template_readback_matches: bool = True,
    tag_name: str = DEFAULT_TAG_NAME,
    cdo_tag_present: bool = True,
    default_tag_readback_matches: bool = True,
    unsupported_blueprint_classes: Sequence[str] = (
        DEFAULT_UNSUPPORTED_BLUEPRINT_CLASSES
    ),
    unsupported_class_authoring_blocked: bool = True,
    broader_blueprint_class_requires_separate_contract: bool = True,
    readback_only: bool = True,
    target_dirty_after_readback: bool = False,
    save_dispatched: bool = False,
    asset_write_performed: bool = False,
    compile_dispatched: bool = False,
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
        "schema": LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_RESULT_SCHEMA,
        "target_asset_path": target_asset_path,
        "generated_class_path": generated_class_path,
        "blueprint_parent_class": blueprint_parent_class,
        "cdo_is_actor": cdo_is_actor,
        "variable_name": variable_name,
        "variable_type": variable_type,
        "scalar_default_value": scalar_default_value,
        "variable_default_readback_matches": variable_default_readback_matches,
        "component_name": component_name,
        "component_class": component_class,
        "component_template_owner_is_actor_cdo": (
            component_template_owner_is_actor_cdo
        ),
        "component_template_readback_matches": (
            component_template_readback_matches
        ),
        "tag_name": tag_name,
        "cdo_tag_present": cdo_tag_present,
        "default_tag_readback_matches": default_tag_readback_matches,
        "unsupported_blueprint_classes": list(unsupported_blueprint_classes),
        "unsupported_class_authoring_blocked": (
            unsupported_class_authoring_blocked
        ),
        "broader_blueprint_class_requires_separate_contract": (
            broader_blueprint_class_requires_separate_contract
        ),
        "readback_only": readback_only,
        "target_dirty_after_readback": target_dirty_after_readback,
        "save_dispatched": save_dispatched,
        "asset_write_performed": asset_write_performed,
        "compile_dispatched": compile_dispatched,
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


def build_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract(
    requested: bool,
    section_265_272_live_actor_bp_actual_authoring_summary: Dict[str, Any],
    live_actor_bp_component_default_readback_result: Dict[str, Any],
) -> Dict[str, Any]:
    section_265_272_summary_schema_matches = bool(
        section_265_272_live_actor_bp_actual_authoring_summary.get("schema")
        == SECTION_265_272_LIVE_ACTOR_BP_ACTUAL_AUTHORING_SUMMARY_SCHEMA
    )
    section_265_272_summary_passed = bool(
        section_265_272_live_actor_bp_actual_authoring_summary.get("status")
        == "passed"
    )
    upstream_actual_authoring_ready = all(
        _count_is_one(
            section_265_272_live_actor_bp_actual_authoring_summary,
            key,
        )
        for key in UPSTREAM_READY_COUNT_KEYS
    )
    upstream_destructive_outputs_closed = all(
        _count_is_zero(
            section_265_272_live_actor_bp_actual_authoring_summary,
            key,
        )
        for key in UPSTREAM_DESTRUCTIVE_OUTPUTS_CLOSED_COUNT_KEYS
    )
    result_schema_matches = bool(
        live_actor_bp_component_default_readback_result.get("schema")
        == LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_RESULT_SCHEMA
    )
    actual_authoring_summary_ready = bool(
        requested
        and section_265_272_summary_schema_matches
        and section_265_272_summary_passed
        and upstream_actual_authoring_ready
        and upstream_destructive_outputs_closed
    )
    class_type_readback_verified = bool(
        live_actor_bp_component_default_readback_result.get("target_asset_path")
        == DEFAULT_TARGET_ASSET_PATH
        and str(
            live_actor_bp_component_default_readback_result.get(
                "target_asset_path", ""
            )
        ).startswith("/Game/_MCP_Temp/")
        and live_actor_bp_component_default_readback_result.get(
            "generated_class_path"
        )
        == DEFAULT_GENERATED_CLASS_PATH
        and live_actor_bp_component_default_readback_result.get(
            "blueprint_parent_class"
        )
        == DEFAULT_BLUEPRINT_PARENT_CLASS
        and live_actor_bp_component_default_readback_result.get("cdo_is_actor")
    )
    variable_default_type_readback_verified = bool(
        live_actor_bp_component_default_readback_result.get("variable_name")
        == DEFAULT_VARIABLE_NAME
        and live_actor_bp_component_default_readback_result.get("variable_type")
        == DEFAULT_VARIABLE_TYPE
        and float(
            live_actor_bp_component_default_readback_result.get(
                "scalar_default_value", -1
            )
        )
        == DEFAULT_VARIABLE_VALUE
        and live_actor_bp_component_default_readback_result.get(
            "variable_default_readback_matches"
        )
    )
    component_template_type_readback_verified = bool(
        live_actor_bp_component_default_readback_result.get("component_name")
        == DEFAULT_COMPONENT_NAME
        and live_actor_bp_component_default_readback_result.get(
            "component_class"
        )
        == DEFAULT_COMPONENT_CLASS
        and live_actor_bp_component_default_readback_result.get(
            "component_template_owner_is_actor_cdo"
        )
        and live_actor_bp_component_default_readback_result.get(
            "component_template_readback_matches"
        )
    )
    cdo_default_tag_readback_verified = bool(
        live_actor_bp_component_default_readback_result.get("tag_name")
        == DEFAULT_TAG_NAME
        and live_actor_bp_component_default_readback_result.get(
            "cdo_tag_present"
        )
        and live_actor_bp_component_default_readback_result.get(
            "default_tag_readback_matches"
        )
    )
    unsupported_classes = tuple(
        live_actor_bp_component_default_readback_result.get(
            "unsupported_blueprint_classes", ()
        )
        or ()
    )
    broader_blueprint_class_authoring_guard_verified = bool(
        unsupported_classes == DEFAULT_UNSUPPORTED_BLUEPRINT_CLASSES
        and live_actor_bp_component_default_readback_result.get(
            "unsupported_class_authoring_blocked"
        )
        and live_actor_bp_component_default_readback_result.get(
            "broader_blueprint_class_requires_separate_contract"
        )
    )
    readback_no_write_verified = bool(
        live_actor_bp_component_default_readback_result.get("readback_only")
        and not live_actor_bp_component_default_readback_result.get(
            "target_dirty_after_readback"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "save_dispatched"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "asset_write_performed"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "compile_dispatched"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "cleanup_allowed"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "cleanup_executed"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "delete_asset_allowed"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "rename_asset_allowed"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "rename_command_dispatched"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "rename_command_executed"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "overwrite_allowed"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "overwrite_executed"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "production_path_write_allowed"
        )
        and not live_actor_bp_component_default_readback_result.get(
            "production_path_write_executed"
        )
    )
    result_has_no_error = bool(
        live_actor_bp_component_default_readback_result.get("error")
        in (None, "")
    )
    component_default_readback_passed = bool(
        actual_authoring_summary_ready
        and result_schema_matches
        and class_type_readback_verified
        and variable_default_type_readback_verified
        and component_template_type_readback_verified
        and cdo_default_tag_readback_verified
        and broader_blueprint_class_authoring_guard_verified
        and readback_no_write_verified
        and result_has_no_error
    )

    return {
        "id": (
            "durable_executor_authoring_live_actor_bp_component_default_readback_batch"
        ),
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_BATCH_SCHEMA
        ),
        "requested": requested,
        "section_265_272_summary_schema_matches": (
            section_265_272_summary_schema_matches
        ),
        "section_265_272_summary_passed": section_265_272_summary_passed,
        "section_265_272_live_actor_bp_actual_authoring_ready": (
            upstream_actual_authoring_ready
        ),
        "section_265_272_destructive_outputs_closed": (
            upstream_destructive_outputs_closed
        ),
        "result_schema_matches": result_schema_matches,
        "actual_authoring_summary_ready": actual_authoring_summary_ready,
        "class_type_readback_verified": class_type_readback_verified,
        "variable_default_type_readback_verified": (
            variable_default_type_readback_verified
        ),
        "component_template_type_readback_verified": (
            component_template_type_readback_verified
        ),
        "cdo_default_tag_readback_verified": cdo_default_tag_readback_verified,
        "broader_blueprint_class_authoring_guard_verified": (
            broader_blueprint_class_authoring_guard_verified
        ),
        "readback_no_write_verified": readback_no_write_verified,
        "result_has_no_error": result_has_no_error,
        "section_273_live_actor_bp_actual_authoring_summary_ready": (
            component_default_readback_passed
        ),
        "section_274_live_actor_bp_class_type_readback_verified": (
            component_default_readback_passed
        ),
        "section_275_live_actor_bp_variable_default_type_readback_verified": (
            component_default_readback_passed
        ),
        "section_276_live_actor_bp_component_template_type_readback_verified": (
            component_default_readback_passed
        ),
        "section_277_live_actor_bp_cdo_default_tag_readback_verified": (
            component_default_readback_passed
        ),
        "section_278_broader_blueprint_class_authoring_guard_verified": (
            component_default_readback_passed
        ),
        "section_279_live_actor_bp_readback_no_write_verified": (
            component_default_readback_passed
        ),
        "section_280_live_actor_bp_component_default_readback_release_ready": (
            component_default_readback_passed
        ),
        "live_actor_bp_component_default_type_readback_ready": (
            component_default_readback_passed
        ),
        "broader_blueprint_class_authoring_guard_ready": (
            component_default_readback_passed
        ),
        "live_actor_bp_component_default_readback_no_write_verified": (
            component_default_readback_passed
        ),
        "final_durable_release_ready": component_default_readback_passed,
        "variable_add_command_dispatched": False,
        "variable_add_command_executed": False,
        "component_add_command_dispatched": False,
        "component_add_command_executed": False,
        "default_write_command_dispatched": False,
        "default_write_command_executed": False,
        "actor_bp_authoring_command_dispatched": False,
        "actor_bp_authoring_command_executed": False,
        "actor_bp_authoring_compile_dispatched": False,
        "actor_bp_authoring_compile_executed": False,
        "actor_bp_authoring_save_dispatched": False,
        "actor_bp_authoring_save_executed": False,
        "actor_bp_authoring_asset_write_performed": False,
        "actor_bp_authoring_package_dirty_marked": False,
        "actor_bp_authoring_target_dirty_after": False,
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
            key: 1 if component_default_readback_passed else 0
            for key in LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_PATH_COUNT_KEYS
        },
        **{
            key: 0
            for key in BLOCKED_LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_OUTPUT_COUNT_KEYS
        },
    }


def summarize_durable_executor_authoring_live_actor_bp_component_default_readback_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(
                requested,
                "live_actor_bp_component_default_type_readback_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "broader_blueprint_class_authoring_guard_ready",
            )
            == len(requested)
            and _truthy_count(
                requested,
                "live_actor_bp_component_default_readback_no_write_verified",
            )
            == len(requested)
            and all(
                _sum_count(requested, key) == 0
                for key in BLOCKED_LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_live_actor_bp_component_default_readback_batch_count": (
            len(requested)
        ),
        "section_265_272_summary_schema_matches_count": _truthy_count(
            requested, "section_265_272_summary_schema_matches"
        ),
        "section_265_272_summary_passed_count": _truthy_count(
            requested, "section_265_272_summary_passed"
        ),
        "section_265_272_live_actor_bp_actual_authoring_ready_count": (
            _truthy_count(
                requested,
                "section_265_272_live_actor_bp_actual_authoring_ready",
            )
        ),
        "section_265_272_destructive_outputs_closed_count": _truthy_count(
            requested, "section_265_272_destructive_outputs_closed"
        ),
        "result_schema_matches_count": _truthy_count(
            requested, "result_schema_matches"
        ),
        "actual_authoring_summary_ready_count": _truthy_count(
            requested, "actual_authoring_summary_ready"
        ),
        "class_type_readback_verified_count": _truthy_count(
            requested, "class_type_readback_verified"
        ),
        "variable_default_type_readback_verified_count": _truthy_count(
            requested, "variable_default_type_readback_verified"
        ),
        "component_template_type_readback_verified_count": _truthy_count(
            requested, "component_template_type_readback_verified"
        ),
        "cdo_default_tag_readback_verified_count": _truthy_count(
            requested, "cdo_default_tag_readback_verified"
        ),
        "broader_blueprint_class_authoring_guard_verified_count": (
            _truthy_count(
                requested,
                "broader_blueprint_class_authoring_guard_verified",
            )
        ),
        "readback_no_write_verified_count": _truthy_count(
            requested, "readback_no_write_verified"
        ),
        "result_has_no_error_count": _truthy_count(
            requested, "result_has_no_error"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
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
            for key in LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in BLOCKED_LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_OUTPUT_COUNT_KEYS
        }
    )
    return summary
