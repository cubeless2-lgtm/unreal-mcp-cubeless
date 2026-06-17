#!/usr/bin/env python
"""Offline smoke tests for Sections 265-272 live Actor BP actual authoring."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract as actual_authoring  # noqa: E402
import bp_authoring_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract as preflight  # noqa: E402
from test_bp_authoring_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract import build_current_section_249_256_summary  # noqa: E402


def build_current_section_257_264_summary() -> dict:
    section_249_256_summary = build_current_section_249_256_summary()
    preflight_result = preflight.build_live_actor_bp_authoring_preflight_result()
    contract = (
        preflight
        .build_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract(
            True,
            section_249_256_summary,
            preflight_result,
        )
    )
    return (
        preflight
        .summarize_durable_executor_authoring_live_actor_bp_authoring_preflight_batches(
            [contract]
        )
    )


def build_current_actual_result(**overrides: object) -> dict:
    result = actual_authoring.build_live_actor_bp_actual_authoring_result()
    result.update(overrides)
    return result


def main() -> int:
    section_257_264_summary = build_current_section_257_264_summary()
    result = build_current_actual_result()
    contract = (
        actual_authoring
        .build_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract(
            True,
            section_257_264_summary,
            result,
        )
    )
    assert (
        contract["schema"]
        == actual_authoring
        .DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_ACTUAL_AUTHORING_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_257_264_summary_schema_matches"] is True
    assert contract["section_257_264_summary_passed"] is True
    assert contract["section_257_264_live_actor_bp_preflight_ready"] is True
    assert contract["section_257_264_mutation_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["actual_execution_checkpoint_satisfied"] is True
    assert contract["target_scope_reconfirmed"] is True
    assert contract["variable_authoring_executed"] is True
    assert contract["component_authoring_executed"] is True
    assert contract["default_authoring_executed"] is True
    assert contract["compile_save_executed"] is True
    assert contract["readback_verified"] is True
    assert contract["dirty_baseline_preserved"] is True
    assert contract["destructive_outputs_closed"] is True
    assert contract["result_has_no_error"] is True
    assert contract["live_actor_bp_actual_authoring_executed"] is True
    assert contract["live_actor_bp_actual_authoring_saved"] is True
    assert contract["live_actor_bp_actual_authoring_readback_verified"] is True
    assert (
        contract[
            "actual_live_actor_bp_authoring_requires_final_user_checkpoint"
        ]
        is False
    )
    assert (
        contract[
            "actual_live_actor_bp_authoring_final_checkpoint_satisfied"
        ]
        is True
    )
    assert (
        contract[
            "section_265_live_actor_bp_actual_execution_checkpoint_satisfied"
        ]
        is True
    )
    assert contract["section_266_live_actor_bp_target_scope_reconfirmed"] is True
    assert contract["section_267_live_actor_bp_variable_authoring_executed"] is True
    assert contract["section_268_live_actor_bp_component_authoring_executed"] is True
    assert contract["section_269_live_actor_bp_default_authoring_executed"] is True
    assert contract["section_270_live_actor_bp_compile_save_executed"] is True
    assert contract["section_271_live_actor_bp_readback_verified"] is True
    assert contract["section_272_live_actor_bp_dirty_baseline_preserved"] is True
    assert contract["variable_add_command_dispatched"] is True
    assert contract["variable_add_command_executed"] is True
    assert contract["component_add_command_dispatched"] is True
    assert contract["component_add_command_executed"] is True
    assert contract["default_write_command_dispatched"] is True
    assert contract["default_write_command_executed"] is True
    assert contract["actor_bp_authoring_command_dispatched"] is True
    assert contract["actor_bp_authoring_command_executed"] is True
    assert contract["actor_bp_authoring_compile_executed"] is True
    assert contract["actor_bp_authoring_save_executed"] is True
    assert contract["actor_bp_authoring_asset_write_performed"] is True
    assert contract["actor_bp_authoring_package_dirty_marked"] is True
    assert contract["actor_bp_authoring_target_dirty_after"] is False
    assert contract["actor_bp_authoring_external_dirty_preserved"] is True
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["production_path_write_allowed"] is False

    summary = (
        actual_authoring
        .summarize_durable_executor_authoring_live_actor_bp_actual_authoring_batches(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_live_actor_bp_actual_authoring_batch_count"
        ]
        == 1
    )
    assert summary["section_257_264_live_actor_bp_preflight_ready_count"] == 1
    assert summary["section_257_264_mutation_outputs_closed_count"] == 1
    assert summary["live_actor_bp_actual_authoring_executed_count"] == 1
    assert summary["live_actor_bp_actual_authoring_saved_count"] == 1
    assert summary["live_actor_bp_actual_authoring_readback_verified_count"] == 1
    assert (
        summary[
            "actual_live_actor_bp_authoring_requires_final_user_checkpoint_count"
        ]
        == 0
    )
    assert (
        summary[
            "actual_live_actor_bp_authoring_final_checkpoint_satisfied_count"
        ]
        == 1
    )
    assert summary["section_265_live_actor_bp_actual_execution_checkpoint_satisfied_count"] == 1
    assert summary["section_266_live_actor_bp_target_scope_reconfirmed_count"] == 1
    assert summary["section_267_live_actor_bp_variable_authoring_executed_count"] == 1
    assert summary["section_268_live_actor_bp_component_authoring_executed_count"] == 1
    assert summary["section_269_live_actor_bp_default_authoring_executed_count"] == 1
    assert summary["section_270_live_actor_bp_compile_save_executed_count"] == 1
    assert summary["section_271_live_actor_bp_readback_verified_count"] == 1
    assert summary["section_272_live_actor_bp_dirty_baseline_preserved_count"] == 1
    assert summary["variable_add_command_executed_count"] == 1
    assert summary["component_add_command_executed_count"] == 1
    assert summary["default_write_command_executed_count"] == 1
    assert summary["actor_bp_authoring_command_executed_count"] == 1
    assert summary["actor_bp_authoring_compile_executed_count"] == 1
    assert summary["actor_bp_authoring_save_executed_count"] == 1
    assert summary["actor_bp_authoring_target_dirty_after_count"] == 0
    assert summary["actor_bp_authoring_external_dirty_preserved_count"] == 1
    assert summary["delete_asset_allowed_count"] == 0
    assert summary["rename_asset_allowed_count"] == 0
    assert summary["production_path_write_executed_count"] == 0

    missing_preflight = dict(section_257_264_summary)
    missing_preflight["live_actor_bp_authoring_checkpoint_ready_count"] = 0
    missing_preflight_contract = (
        actual_authoring
        .build_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract(
            True,
            missing_preflight,
            result,
        )
    )
    missing_preflight_summary = (
        actual_authoring
        .summarize_durable_executor_authoring_live_actor_bp_actual_authoring_batches(
            [missing_preflight_contract]
        )
    )
    assert (
        missing_preflight_contract[
            "section_257_264_live_actor_bp_preflight_ready"
        ]
        is False
    )
    assert (
        missing_preflight_contract["live_actor_bp_actual_authoring_executed"]
        is False
    )
    assert missing_preflight_summary["status"] == "failed"

    production_target_contract = (
        actual_authoring
        .build_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract(
            True,
            section_257_264_summary,
            build_current_actual_result(
                target_asset_path="/Game/Cubeless/Unsafe/BP_ActorExpansion"
            ),
        )
    )
    production_target_summary = (
        actual_authoring
        .summarize_durable_executor_authoring_live_actor_bp_actual_authoring_batches(
            [production_target_contract]
        )
    )
    assert production_target_contract["target_scope_reconfirmed"] is False
    assert production_target_contract["live_actor_bp_actual_authoring_executed"] is False
    assert production_target_contract["production_path_write_allowed"] is False
    assert production_target_summary["status"] == "failed"

    dirty_changed_contract = (
        actual_authoring
        .build_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract(
            True,
            section_257_264_summary,
            build_current_actual_result(
                external_dirty_after=(
                    actual_authoring.DEFAULT_EXTERNAL_DIRTY_PACKAGE,
                    "/Game/Cubeless/Unexpected",
                ),
                external_dirty_preserved=False,
            ),
        )
    )
    dirty_changed_summary = (
        actual_authoring
        .summarize_durable_executor_authoring_live_actor_bp_actual_authoring_batches(
            [dirty_changed_contract]
        )
    )
    assert dirty_changed_contract["dirty_baseline_preserved"] is False
    assert dirty_changed_contract["live_actor_bp_actual_authoring_executed"] is False
    assert dirty_changed_summary["status"] == "failed"

    missing_readback_contract = (
        actual_authoring
        .build_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract(
            True,
            section_257_264_summary,
            build_current_actual_result(component_exists_after=False),
        )
    )
    missing_readback_summary = (
        actual_authoring
        .summarize_durable_executor_authoring_live_actor_bp_actual_authoring_batches(
            [missing_readback_contract]
        )
    )
    assert missing_readback_contract["component_authoring_executed"] is False
    assert missing_readback_contract["readback_verified"] is False
    assert missing_readback_contract["live_actor_bp_actual_authoring_executed"] is False
    assert missing_readback_summary["status"] == "failed"

    destructive_contract = (
        actual_authoring
        .build_durable_executor_authoring_live_actor_bp_actual_authoring_batch_contract(
            True,
            section_257_264_summary,
            build_current_actual_result(production_path_write_executed=True),
        )
    )
    destructive_summary = (
        actual_authoring
        .summarize_durable_executor_authoring_live_actor_bp_actual_authoring_batches(
            [destructive_contract]
        )
    )
    assert destructive_contract["destructive_outputs_closed"] is False
    assert destructive_contract["live_actor_bp_actual_authoring_executed"] is False
    assert destructive_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring live Actor BP actual authoring batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
