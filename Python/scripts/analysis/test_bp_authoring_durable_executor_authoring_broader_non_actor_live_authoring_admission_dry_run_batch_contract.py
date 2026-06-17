#!/usr/bin/env python
"""Offline smoke tests for Sections 385-392 non-Actor admission dry-run."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract as admission  # noqa: E402
import bp_authoring_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract as readonly  # noqa: E402
from test_bp_authoring_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract import build_current_section_369_376_summary  # noqa: E402


def build_current_section_377_384_summary() -> dict:
    section_369_376_summary = build_current_section_369_376_summary()
    result = readonly.build_broader_non_actor_live_readonly_preflight_result()
    contract = readonly.build_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract(
        True,
        section_369_376_summary,
        result,
    )
    return readonly.summarize_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batches(
        [contract]
    )


def build_current_admission_result(**overrides: object) -> dict:
    result = (
        admission
        .build_broader_non_actor_live_authoring_admission_dry_run_result()
    )
    result.update(overrides)
    return result


def main() -> int:
    section_377_384_summary = build_current_section_377_384_summary()
    result = build_current_admission_result()
    contract = admission.build_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract(
        True,
        section_377_384_summary,
        result,
    )
    assert (
        contract["schema"]
        == admission
        .DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_DRY_RUN_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_377_384_summary_schema_matches"] is True
    assert contract["section_377_384_summary_passed"] is True
    assert (
        contract[
            "section_377_384_broader_non_actor_live_readonly_preflight_ready"
        ]
        is True
    )
    assert contract["section_377_384_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert (
        contract["live_authoring_admission_dry_run_checkpoint_satisfied"]
        is True
    )
    assert contract["admission_request_scope_classified"] is True
    assert (
        contract["user_widget_admission_blocked_pending_widget_tree_contract"]
        is True
    )
    assert (
        contract["data_asset_admission_blocked_pending_default_contract"]
        is True
    )
    assert (
        contract["anim_blueprint_admission_blocked_pending_skeleton_contract"]
        is True
    )
    assert (
        contract[
            "function_library_interface_admission_blocked_pending_graph_contract"
        ]
        is True
    )
    assert contract["live_non_actor_creation_outputs_blocked"] is True
    assert (
        contract[
            "live_non_actor_authoring_admission_no_write_boundary_verified"
        ]
        is True
    )
    assert contract["result_has_no_error"] is True
    assert (
        contract[
            "section_385_broader_non_actor_live_authoring_admission_checkpoint_satisfied"
        ]
        is True
    )
    assert (
        contract[
            "section_386_non_actor_live_authoring_admission_request_scope_classified"
        ]
        is True
    )
    assert (
        contract[
            "section_387_user_widget_admission_blocked_pending_widget_tree_contract"
        ]
        is True
    )
    assert (
        contract[
            "section_388_data_asset_admission_blocked_pending_default_contract"
        ]
        is True
    )
    assert (
        contract[
            "section_389_anim_blueprint_admission_blocked_pending_skeleton_contract"
        ]
        is True
    )
    assert (
        contract[
            "section_390_function_library_interface_admission_blocked_pending_graph_contract"
        ]
        is True
    )
    assert (
        contract[
            "section_391_live_non_actor_creation_outputs_blocked_no_write_verified"
        ]
        is True
    )
    assert (
        contract[
            "section_392_broader_non_actor_live_authoring_admission_dry_run_release_ready"
        ]
        is True
    )
    assert (
        contract["broader_non_actor_live_authoring_admission_dry_run_ready"]
        is True
    )
    assert contract["broader_non_actor_live_authoring_still_blocked"] is True
    assert contract["final_durable_release_ready"] is True

    summary = admission.summarize_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    expected_one_counts = (
        "durable_requested_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_count",
        "section_377_384_summary_schema_matches_count",
        "section_377_384_summary_passed_count",
        "section_377_384_broader_non_actor_live_readonly_preflight_ready_count",
        "section_377_384_outputs_closed_count",
        "result_schema_matches_count",
        "live_authoring_admission_dry_run_checkpoint_satisfied_count",
        "admission_request_scope_classified_count",
        "user_widget_admission_blocked_pending_widget_tree_contract_count",
        "data_asset_admission_blocked_pending_default_contract_count",
        "anim_blueprint_admission_blocked_pending_skeleton_contract_count",
        "function_library_interface_admission_blocked_pending_graph_contract_count",
        "live_non_actor_creation_outputs_blocked_count",
        "live_non_actor_authoring_admission_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_385_broader_non_actor_live_authoring_admission_checkpoint_satisfied_count",
        "section_386_non_actor_live_authoring_admission_request_scope_classified_count",
        "section_387_user_widget_admission_blocked_pending_widget_tree_contract_count",
        "section_388_data_asset_admission_blocked_pending_default_contract_count",
        "section_389_anim_blueprint_admission_blocked_pending_skeleton_contract_count",
        "section_390_function_library_interface_admission_blocked_pending_graph_contract_count",
        "section_391_live_non_actor_creation_outputs_blocked_no_write_verified_count",
        "section_392_broader_non_actor_live_authoring_admission_dry_run_release_ready_count",
        "broader_non_actor_live_authoring_admission_dry_run_ready_count",
        "broader_non_actor_live_authoring_still_blocked_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in (
        admission
        .BLOCKED_BROADER_NON_ACTOR_LIVE_AUTHORING_ADMISSION_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key

    missing_upstream = dict(section_377_384_summary)
    missing_upstream["broader_non_actor_live_readonly_preflight_ready_count"] = 0
    missing_upstream_contract = admission.build_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = admission.summarize_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_377_384_broader_non_actor_live_readonly_preflight_ready"
        ]
        is False
    )
    assert (
        missing_upstream_contract[
            "broader_non_actor_live_authoring_admission_dry_run_ready"
        ]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    bad_scope_contract = admission.build_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract(
        True,
        section_377_384_summary,
        build_current_admission_result(
            dry_run_root="/Game/Production",
            planned_output_asset_paths=(
                "/Game/Production/WBP_DurableNonActorAdmission",
                *admission.DEFAULT_PLANNED_OUTPUT_ASSET_PATHS[1:],
            ),
        ),
    )
    bad_scope_summary = admission.summarize_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batches(
        [bad_scope_contract]
    )
    assert bad_scope_contract["admission_request_scope_classified"] is False
    assert bad_scope_summary["status"] == "failed"

    widget_unblocked_contract = admission.build_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract(
        True,
        section_377_384_summary,
        build_current_admission_result(
            user_widget_admission_blocked_pending_widget_tree_contract=False,
        ),
    )
    widget_unblocked_summary = admission.summarize_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batches(
        [widget_unblocked_contract]
    )
    assert (
        widget_unblocked_contract[
            "user_widget_admission_blocked_pending_widget_tree_contract"
        ]
        is False
    )
    assert widget_unblocked_summary["status"] == "failed"

    anim_unblocked_contract = admission.build_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract(
        True,
        section_377_384_summary,
        build_current_admission_result(
            anim_blueprint_missing_skeleton_blocks_admission=False,
        ),
    )
    anim_unblocked_summary = admission.summarize_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batches(
        [anim_unblocked_contract]
    )
    assert (
        anim_unblocked_contract[
            "anim_blueprint_admission_blocked_pending_skeleton_contract"
        ]
        is False
    )
    assert anim_unblocked_summary["status"] == "failed"

    dispatched_contract = admission.build_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract(
        True,
        section_377_384_summary,
        build_current_admission_result(
            live_non_actor_authoring_admission_command_dispatched=True,
            user_widget_blueprint_create_command_dispatched=True,
        ),
    )
    dispatched_summary = admission.summarize_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batches(
        [dispatched_contract]
    )
    assert (
        dispatched_contract["live_non_actor_creation_outputs_blocked"]
        is False
    )
    assert dispatched_summary["status"] == "failed"

    dirty_contract = admission.build_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract(
        True,
        section_377_384_summary,
        build_current_admission_result(
            dirty_content_after_dry_run=[
                "/Game/_MCP_Temp/DurableSaveGate/NonActorAdmissionDryRun/WBP_Unexpected"
            ],
            non_actor_blueprint_asset_write_performed=True,
        ),
    )
    dirty_summary = admission.summarize_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batches(
        [dirty_contract]
    )
    assert (
        dirty_contract[
            "live_non_actor_authoring_admission_no_write_boundary_verified"
        ]
        is False
    )
    assert dirty_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring broader non-Actor live authoring admission dry-run batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
