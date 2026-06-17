#!/usr/bin/env python
"""Offline smoke tests for Sections 257-264 live Actor BP preflight batch."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract as actor_bp_expansion  # noqa: E402
import bp_authoring_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract as live_actor_bp_preflight  # noqa: E402
from test_bp_authoring_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract import build_current_section_241_248_summary  # noqa: E402


def build_current_section_249_256_summary() -> dict:
    section_241_248_summary = build_current_section_241_248_summary()
    actor_result = actor_bp_expansion.build_actor_bp_expansion_dry_run_result()
    contract = (
        actor_bp_expansion
        .build_durable_executor_authoring_actor_bp_expansion_dry_run_batch_contract(
            True,
            section_241_248_summary,
            actor_result,
        )
    )
    return (
        actor_bp_expansion
        .summarize_durable_executor_authoring_actor_bp_expansion_dry_run_batches(
            [contract]
        )
    )


def build_current_live_preflight_result(**overrides: object) -> dict:
    result = live_actor_bp_preflight.build_live_actor_bp_authoring_preflight_result()
    result.update(overrides)
    return result


def main() -> int:
    section_249_256_summary = build_current_section_249_256_summary()
    preflight_result = build_current_live_preflight_result()
    contract = (
        live_actor_bp_preflight
        .build_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract(
            True,
            section_249_256_summary,
            preflight_result,
        )
    )
    assert (
        contract["schema"]
        == live_actor_bp_preflight
        .DURABLE_EXECUTOR_AUTHORING_LIVE_ACTOR_BP_AUTHORING_PREFLIGHT_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_249_256_summary_schema_matches"] is True
    assert contract["section_249_256_summary_passed"] is True
    assert contract["section_249_256_actor_bp_expansion_dry_run_ready"] is True
    assert contract["section_249_256_actor_bp_mutation_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["live_actor_bp_command_envelope_scoped"] is True
    assert contract["live_actor_bp_read_only_target_preflight_ready"] is True
    assert contract["live_actor_bp_mutation_sequence_planned"] is True
    assert contract["live_actor_bp_compile_save_ordering_verified"] is True
    assert contract["live_actor_bp_rollback_boundary_revalidated"] is True
    assert contract["live_actor_bp_readback_evidence_plan_ready"] is True
    assert contract["live_actor_bp_final_checkpoint_required"] is True
    assert contract["dry_run_blocks_actual_live_actor_authoring_outputs"] is True
    assert contract["result_has_no_error"] is True
    assert contract["live_actor_bp_authoring_checkpoint_ready"] is True
    assert (
        contract[
            "actual_live_actor_bp_authoring_requires_final_user_checkpoint"
        ]
        is True
    )
    assert contract["section_257_live_actor_bp_command_envelope_scoped"] is True
    assert (
        contract["section_258_live_actor_bp_read_only_target_preflight_ready"]
        is True
    )
    assert contract["section_259_live_actor_bp_mutation_sequence_planned"] is True
    assert (
        contract["section_260_live_actor_bp_compile_save_ordering_verified"]
        is True
    )
    assert (
        contract["section_261_live_actor_bp_rollback_boundary_revalidated"]
        is True
    )
    assert contract["section_262_live_actor_bp_readback_evidence_plan_ready"] is True
    assert contract["section_263_live_actor_bp_final_checkpoint_required"] is True
    assert contract["section_264_live_actor_bp_actual_authoring_closed"] is True
    assert contract["live_actor_bp_authoring_preflight_allowed"] is True
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
        live_actor_bp_preflight
        .summarize_durable_executor_authoring_live_actor_bp_authoring_preflight_batches(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_live_actor_bp_authoring_preflight_batch_count"
        ]
        == 1
    )
    assert summary["section_249_256_summary_schema_matches_count"] == 1
    assert summary["section_249_256_summary_passed_count"] == 1
    assert summary["section_249_256_actor_bp_expansion_dry_run_ready_count"] == 1
    assert summary["section_249_256_actor_bp_mutation_outputs_closed_count"] == 1
    assert summary["live_actor_bp_command_envelope_scoped_count"] == 1
    assert summary["live_actor_bp_read_only_target_preflight_ready_count"] == 1
    assert summary["live_actor_bp_mutation_sequence_planned_count"] == 1
    assert summary["live_actor_bp_compile_save_ordering_verified_count"] == 1
    assert summary["live_actor_bp_rollback_boundary_revalidated_count"] == 1
    assert summary["live_actor_bp_readback_evidence_plan_ready_count"] == 1
    assert summary["live_actor_bp_final_checkpoint_required_count"] == 1
    assert summary["live_actor_bp_authoring_checkpoint_ready_count"] == 1
    assert (
        summary[
            "actual_live_actor_bp_authoring_requires_final_user_checkpoint_count"
        ]
        == 1
    )
    assert summary["section_257_live_actor_bp_command_envelope_scoped_count"] == 1
    assert (
        summary[
            "section_258_live_actor_bp_read_only_target_preflight_ready_count"
        ]
        == 1
    )
    assert summary["section_259_live_actor_bp_mutation_sequence_planned_count"] == 1
    assert (
        summary[
            "section_260_live_actor_bp_compile_save_ordering_verified_count"
        ]
        == 1
    )
    assert (
        summary[
            "section_261_live_actor_bp_rollback_boundary_revalidated_count"
        ]
        == 1
    )
    assert summary["section_262_live_actor_bp_readback_evidence_plan_ready_count"] == 1
    assert summary["section_263_live_actor_bp_final_checkpoint_required_count"] == 1
    assert summary["section_264_live_actor_bp_actual_authoring_closed_count"] == 1
    assert summary["variable_add_command_dispatched_count"] == 0
    assert summary["component_add_command_dispatched_count"] == 0
    assert summary["default_write_command_dispatched_count"] == 0
    assert summary["actor_bp_authoring_command_dispatched_count"] == 0
    assert summary["actor_bp_authoring_command_executed_count"] == 0
    assert summary["actor_bp_authoring_asset_write_performed_count"] == 0
    assert summary["actor_bp_authoring_package_dirty_marked_count"] == 0
    assert summary["production_path_write_allowed_count"] == 0

    missing_actor_dry_run = dict(section_249_256_summary)
    missing_actor_dry_run["actor_bp_expansion_dry_run_ready_count"] = 0
    missing_actor_contract = (
        live_actor_bp_preflight
        .build_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract(
            True,
            missing_actor_dry_run,
            preflight_result,
        )
    )
    missing_actor_summary = (
        live_actor_bp_preflight
        .summarize_durable_executor_authoring_live_actor_bp_authoring_preflight_batches(
            [missing_actor_contract]
        )
    )
    assert (
        missing_actor_contract[
            "section_249_256_actor_bp_expansion_dry_run_ready"
        ]
        is False
    )
    assert missing_actor_contract["live_actor_bp_authoring_checkpoint_ready"] is False
    assert missing_actor_summary["status"] == "failed"

    production_target_contract = (
        live_actor_bp_preflight
        .build_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract(
            True,
            section_249_256_summary,
            build_current_live_preflight_result(
                target_asset_path="/Game/Cubeless/Unsafe/BP_ActorExpansion",
                target_under_temp_root=False,
            ),
        )
    )
    production_target_summary = (
        live_actor_bp_preflight
        .summarize_durable_executor_authoring_live_actor_bp_authoring_preflight_batches(
            [production_target_contract]
        )
    )
    assert production_target_contract["live_actor_bp_command_envelope_scoped"] is False
    assert production_target_contract["live_actor_bp_authoring_checkpoint_ready"] is False
    assert production_target_contract["production_path_write_allowed"] is False
    assert production_target_summary["status"] == "failed"

    missing_checkpoint_contract = (
        live_actor_bp_preflight
        .build_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract(
            True,
            section_249_256_summary,
            build_current_live_preflight_result(
                final_user_checkpoint_required=False
            ),
        )
    )
    missing_checkpoint_summary = (
        live_actor_bp_preflight
        .summarize_durable_executor_authoring_live_actor_bp_authoring_preflight_batches(
            [missing_checkpoint_contract]
        )
    )
    assert missing_checkpoint_contract["live_actor_bp_final_checkpoint_required"] is False
    assert missing_checkpoint_contract["live_actor_bp_authoring_checkpoint_ready"] is False
    assert missing_checkpoint_summary["status"] == "failed"

    dispatch_attempt_contract = (
        live_actor_bp_preflight
        .build_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract(
            True,
            section_249_256_summary,
            build_current_live_preflight_result(
                actor_bp_authoring_command_dispatched=True
            ),
        )
    )
    dispatch_attempt_summary = (
        live_actor_bp_preflight
        .summarize_durable_executor_authoring_live_actor_bp_authoring_preflight_batches(
            [dispatch_attempt_contract]
        )
    )
    assert (
        dispatch_attempt_contract[
            "dry_run_blocks_actual_live_actor_authoring_outputs"
        ]
        is False
    )
    assert dispatch_attempt_contract["live_actor_bp_authoring_checkpoint_ready"] is False
    assert dispatch_attempt_contract["actor_bp_authoring_command_dispatched"] is False
    assert dispatch_attempt_summary["status"] == "failed"

    missing_readback_contract = (
        live_actor_bp_preflight
        .build_durable_executor_authoring_live_actor_bp_authoring_preflight_batch_contract(
            True,
            section_249_256_summary,
            build_current_live_preflight_result(readback_evidence_plan_ready=False),
        )
    )
    missing_readback_summary = (
        live_actor_bp_preflight
        .summarize_durable_executor_authoring_live_actor_bp_authoring_preflight_batches(
            [missing_readback_contract]
        )
    )
    assert missing_readback_contract["live_actor_bp_readback_evidence_plan_ready"] is False
    assert missing_readback_contract["live_actor_bp_authoring_checkpoint_ready"] is False
    assert missing_readback_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring live Actor BP preflight batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
