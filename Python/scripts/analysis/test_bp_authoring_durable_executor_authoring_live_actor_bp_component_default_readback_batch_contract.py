#!/usr/bin/env python
"""Offline smoke tests for Sections 273-280 Actor BP readback expansion."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract as actual_authoring  # noqa: E402
import bp_authoring_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract as readback  # noqa: E402
from test_bp_authoring_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract import build_current_section_257_264_summary  # noqa: E402


def build_current_section_265_272_summary() -> dict:
    section_257_264_summary = build_current_section_257_264_summary()
    actual_result = actual_authoring.build_live_actor_bp_actual_authoring_result()
    contract = (
        actual_authoring
        .build_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract(
            True,
            section_257_264_summary,
            actual_result,
        )
    )
    return (
        actual_authoring
        .summarize_durable_executor_authoring_live_actor_bp_actual_authoring_batches(
            [contract]
        )
    )


def build_current_readback_result(**overrides: object) -> dict:
    result = readback.build_live_actor_bp_component_default_readback_result()
    result.update(overrides)
    return result


def main() -> int:
    section_265_272_summary = build_current_section_265_272_summary()
    result = build_current_readback_result()
    contract = readback.build_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract(
        True,
        section_265_272_summary,
        result,
    )
    assert (
        contract["schema"]
        == readback
        .DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_COMPONENT_DEFAULT_READBACK_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_265_272_summary_schema_matches"] is True
    assert contract["section_265_272_summary_passed"] is True
    assert contract["section_265_272_live_actor_bp_actual_authoring_ready"] is True
    assert contract["section_265_272_destructive_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["actual_authoring_summary_ready"] is True
    assert contract["class_type_readback_verified"] is True
    assert contract["variable_default_type_readback_verified"] is True
    assert contract["component_template_type_readback_verified"] is True
    assert contract["cdo_default_tag_readback_verified"] is True
    assert contract["broader_blueprint_class_authoring_guard_verified"] is True
    assert contract["readback_no_write_verified"] is True
    assert contract["result_has_no_error"] is True
    assert contract["section_273_live_actor_bp_actual_authoring_summary_ready"] is True
    assert contract["section_274_live_actor_bp_class_type_readback_verified"] is True
    assert (
        contract[
            "section_275_live_actor_bp_variable_default_type_readback_verified"
        ]
        is True
    )
    assert (
        contract[
            "section_276_live_actor_bp_component_template_type_readback_verified"
        ]
        is True
    )
    assert (
        contract["section_277_live_actor_bp_cdo_default_tag_readback_verified"]
        is True
    )
    assert (
        contract["section_278_broader_blueprint_class_authoring_guard_verified"]
        is True
    )
    assert contract["section_279_live_actor_bp_readback_no_write_verified"] is True
    assert (
        contract[
            "section_280_live_actor_bp_component_default_readback_release_ready"
        ]
        is True
    )
    assert contract["live_actor_bp_component_default_type_readback_ready"] is True
    assert contract["broader_blueprint_class_authoring_guard_ready"] is True
    assert (
        contract["live_actor_bp_component_default_readback_no_write_verified"]
        is True
    )
    assert contract["final_durable_release_ready"] is True
    assert contract["variable_add_command_dispatched"] is False
    assert contract["component_add_command_dispatched"] is False
    assert contract["default_write_command_dispatched"] is False
    assert contract["actor_bp_authoring_save_dispatched"] is False
    assert contract["actor_bp_authoring_asset_write_performed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["production_path_write_allowed"] is False

    summary = readback.summarize_durable_executor_authoring_live_actor_bp_component_default_readback_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_live_actor_bp_component_default_readback_batch_count"
        ]
        == 1
    )
    expected_one_counts = (
        "section_265_272_summary_schema_matches_count",
        "section_265_272_summary_passed_count",
        "section_265_272_live_actor_bp_actual_authoring_ready_count",
        "section_265_272_destructive_outputs_closed_count",
        "result_schema_matches_count",
        "actual_authoring_summary_ready_count",
        "class_type_readback_verified_count",
        "variable_default_type_readback_verified_count",
        "component_template_type_readback_verified_count",
        "cdo_default_tag_readback_verified_count",
        "broader_blueprint_class_authoring_guard_verified_count",
        "readback_no_write_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
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
    for key in expected_one_counts:
        assert summary[key] == 1, key
    expected_zero_counts = (
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
    for key in expected_zero_counts:
        assert summary[key] == 0, key

    missing_actual_summary = dict(section_265_272_summary)
    missing_actual_summary["live_actor_bp_actual_authoring_readback_verified_count"] = 0
    missing_actual_contract = readback.build_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract(
        True,
        missing_actual_summary,
        result,
    )
    missing_actual_summary_result = readback.summarize_durable_executor_authoring_live_actor_bp_component_default_readback_batches(
        [missing_actual_contract]
    )
    assert (
        missing_actual_contract[
            "section_265_272_live_actor_bp_actual_authoring_ready"
        ]
        is False
    )
    assert (
        missing_actual_contract[
            "live_actor_bp_component_default_type_readback_ready"
        ]
        is False
    )
    assert missing_actual_summary_result["status"] == "failed"

    component_mismatch_contract = readback.build_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract(
        True,
        section_265_272_summary,
        build_current_readback_result(component_class="StaticMeshComponent"),
    )
    component_mismatch_summary = readback.summarize_durable_executor_authoring_live_actor_bp_component_default_readback_batches(
        [component_mismatch_contract]
    )
    assert (
        component_mismatch_contract[
            "component_template_type_readback_verified"
        ]
        is False
    )
    assert (
        component_mismatch_contract[
            "live_actor_bp_component_default_type_readback_ready"
        ]
        is False
    )
    assert component_mismatch_summary["status"] == "failed"

    variable_default_mismatch_contract = readback.build_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract(
        True,
        section_265_272_summary,
        build_current_readback_result(scalar_default_value=2.0),
    )
    variable_default_mismatch_summary = readback.summarize_durable_executor_authoring_live_actor_bp_component_default_readback_batches(
        [variable_default_mismatch_contract]
    )
    assert (
        variable_default_mismatch_contract[
            "variable_default_type_readback_verified"
        ]
        is False
    )
    assert variable_default_mismatch_summary["status"] == "failed"

    unsupported_unblocked_contract = readback.build_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract(
        True,
        section_265_272_summary,
        build_current_readback_result(unsupported_class_authoring_blocked=False),
    )
    unsupported_unblocked_summary = readback.summarize_durable_executor_authoring_live_actor_bp_component_default_readback_batches(
        [unsupported_unblocked_contract]
    )
    assert (
        unsupported_unblocked_contract[
            "broader_blueprint_class_authoring_guard_verified"
        ]
        is False
    )
    assert unsupported_unblocked_summary["status"] == "failed"

    write_during_readback_contract = readback.build_durable_executor_authoring_live_actor_bp_component_default_readback_batch_contract(
        True,
        section_265_272_summary,
        build_current_readback_result(
            save_dispatched=True,
            asset_write_performed=True,
            target_dirty_after_readback=True,
        ),
    )
    write_during_readback_summary = readback.summarize_durable_executor_authoring_live_actor_bp_component_default_readback_batches(
        [write_during_readback_contract]
    )
    assert write_during_readback_contract["readback_no_write_verified"] is False
    assert (
        write_during_readback_contract[
            "live_actor_bp_component_default_readback_no_write_verified"
        ]
        is False
    )
    assert write_during_readback_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring live Actor BP component/default readback batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
