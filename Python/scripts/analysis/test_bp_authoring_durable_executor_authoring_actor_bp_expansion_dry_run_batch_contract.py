#!/usr/bin/env python
"""Offline smoke tests for Sections 249-256 Actor BP expansion dry-run batch."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract as actor_bp_expansion  # noqa: E402
import bp_authoring_durable_executor_authoring_rename_overwrite_dry_run_batch_contract as rename_overwrite_dry_run  # noqa: E402
from test_bp_authoring_durable_executor_authoring_rename_overwrite_dry_run_batch_contract import build_current_section_233_240_summary  # noqa: E402


def build_current_section_241_248_summary() -> dict:
    section_233_240_summary = build_current_section_233_240_summary()
    rename_result = rename_overwrite_dry_run.build_rename_overwrite_dry_run_result()
    contract = (
        rename_overwrite_dry_run
        .build_durable_executor_authoring_rename_overwrite_dry_run_batch_contract(
            True,
            section_233_240_summary,
            rename_result,
        )
    )
    return (
        rename_overwrite_dry_run
        .summarize_durable_executor_authoring_rename_overwrite_dry_run_batches(
            [contract]
        )
    )


def build_current_actor_result(**overrides: object) -> dict:
    result = actor_bp_expansion.build_actor_bp_expansion_dry_run_result()
    result.update(overrides)
    return result


def main() -> int:
    section_241_248_summary = build_current_section_241_248_summary()
    actor_result = build_current_actor_result()
    contract = (
        actor_bp_expansion
        .build_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract(
            True,
            section_241_248_summary,
            actor_result,
        )
    )
    assert (
        contract["schema"]
        == actor_bp_expansion
        .DURABLE_EXECUTOR_AUTHORING_ACTOR_BP_EXPANSION_DRY_RUN_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_241_248_summary_schema_matches"] is True
    assert contract["section_241_248_summary_passed"] is True
    assert contract["section_241_248_rename_overwrite_dry_run_ready"] is True
    assert contract["section_241_248_destructive_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["actor_blueprint_scope_confirmed"] is True
    assert contract["variable_authoring_plan_accepted"] is True
    assert contract["component_authoring_plan_accepted"] is True
    assert contract["default_authoring_plan_accepted"] is True
    assert contract["compile_save_dependency_declared"] is True
    assert contract["temp_package_mutation_boundary_clean"] is True
    assert contract["actor_authoring_readback_dry_run_ready"] is True
    assert contract["dry_run_blocks_actual_actor_authoring_outputs"] is True
    assert contract["result_has_no_error"] is True
    assert contract["actor_bp_expansion_dry_run_ready"] is True
    assert (
        contract["actual_actor_bp_authoring_requires_final_user_checkpoint"]
        is True
    )
    assert contract["section_249_actor_blueprint_scope_confirmed"] is True
    assert contract["section_250_variable_authoring_plan_accepted"] is True
    assert contract["section_251_component_authoring_plan_accepted"] is True
    assert contract["section_252_default_authoring_plan_accepted"] is True
    assert contract["section_253_compile_save_dependency_declared"] is True
    assert contract["section_254_temp_package_mutation_boundary_clean"] is True
    assert contract["section_255_actor_authoring_readback_dry_run_ready"] is True
    assert (
        contract["section_256_actual_actor_authoring_requires_final_user_checkpoint"]
        is True
    )
    assert contract["actor_bp_expansion_dry_run_allowed"] is True
    assert contract["variable_add_command_dispatched"] is False
    assert contract["component_add_command_dispatched"] is False
    assert contract["default_write_command_dispatched"] is False
    assert contract["actor_bp_authoring_command_dispatched"] is False
    assert contract["actor_bp_authoring_command_executed"] is False
    assert contract["actor_bp_authoring_compile_dispatched"] is False
    assert contract["actor_bp_authoring_save_dispatched"] is False
    assert contract["actor_bp_authoring_asset_write_performed"] is False
    assert contract["actor_bp_authoring_package_dirty_marked"] is False
    assert contract["production_path_write_allowed"] is False

    summary = (
        actor_bp_expansion
        .summarize_durable_executor_authoring_actor_bp_expansion_dry_run_batches(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_actor_bp_expansion_dry_run_batch_count"
        ]
        == 1
    )
    assert summary["section_241_248_summary_schema_matches_count"] == 1
    assert summary["section_241_248_summary_passed_count"] == 1
    assert summary["section_241_248_rename_overwrite_dry_run_ready_count"] == 1
    assert summary["section_241_248_destructive_outputs_closed_count"] == 1
    assert summary["actor_blueprint_scope_confirmed_count"] == 1
    assert summary["variable_authoring_plan_accepted_count"] == 1
    assert summary["component_authoring_plan_accepted_count"] == 1
    assert summary["default_authoring_plan_accepted_count"] == 1
    assert summary["compile_save_dependency_declared_count"] == 1
    assert summary["temp_package_mutation_boundary_clean_count"] == 1
    assert summary["actor_authoring_readback_dry_run_ready_count"] == 1
    assert summary["actor_bp_expansion_dry_run_ready_count"] == 1
    assert (
        summary[
            "actual_actor_bp_authoring_requires_final_user_checkpoint_count"
        ]
        == 1
    )
    assert summary["section_249_actor_blueprint_scope_confirmed_count"] == 1
    assert summary["section_250_variable_authoring_plan_accepted_count"] == 1
    assert summary["section_251_component_authoring_plan_accepted_count"] == 1
    assert summary["section_252_default_authoring_plan_accepted_count"] == 1
    assert summary["section_253_compile_save_dependency_declared_count"] == 1
    assert summary["section_254_temp_package_mutation_boundary_clean_count"] == 1
    assert summary["section_255_actor_authoring_readback_dry_run_ready_count"] == 1
    assert (
        summary[
            "section_256_actual_actor_authoring_requires_final_user_checkpoint_count"
        ]
        == 1
    )
    assert summary["variable_add_command_dispatched_count"] == 0
    assert summary["component_add_command_dispatched_count"] == 0
    assert summary["default_write_command_dispatched_count"] == 0
    assert summary["actor_bp_authoring_command_dispatched_count"] == 0
    assert summary["actor_bp_authoring_command_executed_count"] == 0
    assert summary["actor_bp_authoring_asset_write_performed_count"] == 0
    assert summary["actor_bp_authoring_package_dirty_marked_count"] == 0
    assert summary["production_path_write_allowed_count"] == 0

    missing_rename = dict(section_241_248_summary)
    missing_rename["rename_overwrite_dry_run_ready_count"] = 0
    missing_rename_contract = (
        actor_bp_expansion
        .build_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract(
            True,
            missing_rename,
            actor_result,
        )
    )
    missing_rename_summary = (
        actor_bp_expansion
        .summarize_durable_executor_authoring_actor_bp_expansion_dry_run_batches(
            [missing_rename_contract]
        )
    )
    assert (
        missing_rename_contract[
            "section_241_248_rename_overwrite_dry_run_ready"
        ]
        is False
    )
    assert missing_rename_contract["actor_bp_expansion_dry_run_ready"] is False
    assert missing_rename_summary["status"] == "failed"

    production_target_contract = (
        actor_bp_expansion
        .build_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract(
            True,
            section_241_248_summary,
            build_current_actor_result(
                target_asset_path="/Game/Cubeless/Unsafe/BP_ActorExpansion",
                target_under_temp_root=False,
            ),
        )
    )
    production_target_summary = (
        actor_bp_expansion
        .summarize_durable_executor_authoring_actor_bp_expansion_dry_run_batches(
            [production_target_contract]
        )
    )
    assert production_target_contract["actor_blueprint_scope_confirmed"] is False
    assert production_target_contract["actor_bp_expansion_dry_run_ready"] is False
    assert production_target_contract["production_path_write_allowed"] is False
    assert production_target_summary["status"] == "failed"

    non_actor_contract = (
        actor_bp_expansion
        .build_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract(
            True,
            section_241_248_summary,
            build_current_actor_result(
                parent_class="/Script/Engine.Object",
                blueprint_class_is_actor=False,
            ),
        )
    )
    non_actor_summary = (
        actor_bp_expansion
        .summarize_durable_executor_authoring_actor_bp_expansion_dry_run_batches(
            [non_actor_contract]
        )
    )
    assert non_actor_contract["actor_blueprint_scope_confirmed"] is False
    assert non_actor_contract["actor_bp_expansion_dry_run_ready"] is False
    assert non_actor_summary["status"] == "failed"

    mutation_attempt_contract = (
        actor_bp_expansion
        .build_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract(
            True,
            section_241_248_summary,
            build_current_actor_result(variable_add_command_dispatched=True),
        )
    )
    mutation_attempt_summary = (
        actor_bp_expansion
        .summarize_durable_executor_authoring_actor_bp_expansion_dry_run_batches(
            [mutation_attempt_contract]
        )
    )
    assert (
        mutation_attempt_contract[
            "dry_run_blocks_actual_actor_authoring_outputs"
        ]
        is False
    )
    assert mutation_attempt_contract["actor_bp_expansion_dry_run_ready"] is False
    assert mutation_attempt_contract["variable_add_command_dispatched"] is False
    assert mutation_attempt_summary["status"] == "failed"

    missing_default_plan_contract = (
        actor_bp_expansion
        .build_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract(
            True,
            section_241_248_summary,
            build_current_actor_result(default_value_plan_built=False),
        )
    )
    missing_default_plan_summary = (
        actor_bp_expansion
        .summarize_durable_executor_authoring_actor_bp_expansion_dry_run_batches(
            [missing_default_plan_contract]
        )
    )
    assert (
        missing_default_plan_contract["default_authoring_plan_accepted"]
        is False
    )
    assert missing_default_plan_contract["actor_bp_expansion_dry_run_ready"] is False
    assert missing_default_plan_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring Actor BP expansion dry-run batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
