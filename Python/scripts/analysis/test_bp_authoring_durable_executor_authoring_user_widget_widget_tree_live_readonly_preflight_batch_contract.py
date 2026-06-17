#!/usr/bin/env python
"""Offline smoke tests for Sections 393-400 UserWidget read-only preflight."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract as admission  # noqa: E402
import bp_authoring_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract as widget_preflight  # noqa: E402
from test_bp_authoring_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract import build_current_section_377_384_summary  # noqa: E402


def build_current_section_385_392_summary() -> dict:
    section_377_384_summary = build_current_section_377_384_summary()
    result = admission.build_broader_non_actor_live_authoring_admission_dry_run_result()
    contract = admission.build_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batch_contract(
        True,
        section_377_384_summary,
        result,
    )
    return admission.summarize_durable_executor_authoring_broader_non_actor_live_authoring_admission_dry_run_batches(
        [contract]
    )


def build_current_widget_preflight_result(**overrides: object) -> dict:
    result = (
        widget_preflight
        .build_user_widget_widget_tree_live_readonly_preflight_result()
    )
    result.update(overrides)
    return result


def main() -> int:
    section_385_392_summary = build_current_section_385_392_summary()
    result = build_current_widget_preflight_result()
    contract = widget_preflight.build_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract(
        True,
        section_385_392_summary,
        result,
    )
    assert (
        contract["schema"]
        == widget_preflight
        .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_LIVE_READONLY_PREFLIGHT_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_385_392_summary_schema_matches"] is True
    assert contract["section_385_392_summary_passed"] is True
    assert contract["section_385_392_non_actor_admission_dry_run_ready"] is True
    assert contract["section_385_392_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["user_widget_widget_tree_checkpoint_satisfied"] is True
    assert (
        contract["correct_project_user_widget_readonly_probe_recorded"]
        is True
    )
    assert contract["widget_blueprint_prerequisites_verified"] is True
    assert contract["root_widget_control_prerequisites_verified"] is True
    assert contract["widget_tree_creation_mutation_outputs_blocked"] is True
    assert contract["widget_compile_save_write_outputs_blocked"] is True
    assert (
        contract["user_widget_widget_tree_no_write_boundary_verified"]
        is True
    )
    assert contract["result_has_no_error"] is True
    assert contract["section_393_user_widget_widget_tree_checkpoint_satisfied"] is True
    assert (
        contract["section_394_correct_project_user_widget_readonly_probe_recorded"]
        is True
    )
    assert contract["section_395_widget_blueprint_prerequisites_verified"] is True
    assert contract["section_396_root_widget_control_prerequisites_verified"] is True
    assert contract["section_397_widget_tree_creation_mutation_outputs_blocked"] is True
    assert contract["section_398_widget_compile_save_write_outputs_blocked"] is True
    assert (
        contract["section_399_user_widget_widget_tree_no_write_boundary_verified"]
        is True
    )
    assert (
        contract[
            "section_400_user_widget_widget_tree_live_readonly_preflight_release_ready"
        ]
        is True
    )
    assert contract["user_widget_widget_tree_live_readonly_preflight_ready"] is True
    assert contract["user_widget_widget_tree_actual_authoring_still_blocked"] is True
    assert contract["final_durable_release_ready"] is True

    summary = widget_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    expected_one_counts = (
        "durable_requested_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_count",
        "section_385_392_summary_schema_matches_count",
        "section_385_392_summary_passed_count",
        "section_385_392_non_actor_admission_dry_run_ready_count",
        "section_385_392_outputs_closed_count",
        "result_schema_matches_count",
        "user_widget_widget_tree_checkpoint_satisfied_count",
        "correct_project_user_widget_readonly_probe_recorded_count",
        "widget_blueprint_prerequisites_verified_count",
        "root_widget_control_prerequisites_verified_count",
        "widget_tree_creation_mutation_outputs_blocked_count",
        "widget_compile_save_write_outputs_blocked_count",
        "user_widget_widget_tree_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_393_user_widget_widget_tree_checkpoint_satisfied_count",
        "section_394_correct_project_user_widget_readonly_probe_recorded_count",
        "section_395_widget_blueprint_prerequisites_verified_count",
        "section_396_root_widget_control_prerequisites_verified_count",
        "section_397_widget_tree_creation_mutation_outputs_blocked_count",
        "section_398_widget_compile_save_write_outputs_blocked_count",
        "section_399_user_widget_widget_tree_no_write_boundary_verified_count",
        "section_400_user_widget_widget_tree_live_readonly_preflight_release_ready_count",
        "user_widget_widget_tree_live_readonly_preflight_ready_count",
        "user_widget_widget_tree_actual_authoring_still_blocked_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in (
        widget_preflight
        .BLOCKED_USER_WIDGET_WIDGET_TREE_PREFLIGHT_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key

    missing_upstream = dict(section_385_392_summary)
    missing_upstream[
        "broader_non_actor_live_authoring_admission_dry_run_ready_count"
    ] = 0
    missing_upstream_contract = widget_preflight.build_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = widget_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_385_392_non_actor_admission_dry_run_ready"
        ]
        is False
    )
    assert (
        missing_upstream_contract[
            "user_widget_widget_tree_live_readonly_preflight_ready"
        ]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    wrong_project_contract = widget_preflight.build_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract(
        True,
        section_385_392_summary,
        build_current_widget_preflight_result(
            project_file_path="D:/Other/OtherProject.uproject",
        ),
    )
    wrong_project_summary = widget_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batches(
        [wrong_project_contract]
    )
    assert (
        wrong_project_contract[
            "correct_project_user_widget_readonly_probe_recorded"
        ]
        is False
    )
    assert wrong_project_summary["status"] == "failed"

    missing_widget_class_contract = widget_preflight.build_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract(
        True,
        section_385_392_summary,
        build_current_widget_preflight_result(
            class_probes={
                "WidgetTree": {
                    "path": "/Script/UMG.WidgetTree",
                    "class_name": "WidgetTree",
                    "loaded": False,
                }
            },
        ),
    )
    missing_widget_class_summary = widget_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batches(
        [missing_widget_class_contract]
    )
    assert (
        missing_widget_class_contract[
            "widget_blueprint_prerequisites_verified"
        ]
        is False
    )
    assert missing_widget_class_summary["status"] == "failed"

    missing_root_control_contract = widget_preflight.build_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract(
        True,
        section_385_392_summary,
        build_current_widget_preflight_result(
            class_probes={
                "CanvasPanel": {
                    "path": "/Script/UMG.CanvasPanel",
                    "class_name": "CanvasPanel",
                    "loaded": False,
                }
            },
        ),
    )
    missing_root_control_summary = widget_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batches(
        [missing_root_control_contract]
    )
    assert (
        missing_root_control_contract[
            "root_widget_control_prerequisites_verified"
        ]
        is False
    )
    assert missing_root_control_summary["status"] == "failed"

    mutation_contract = widget_preflight.build_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract(
        True,
        section_385_392_summary,
        build_current_widget_preflight_result(
            widget_blueprint_create_command_dispatched=True,
            widget_tree_mutation_performed=True,
        ),
    )
    mutation_summary = widget_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batches(
        [mutation_contract]
    )
    assert (
        mutation_contract["widget_tree_creation_mutation_outputs_blocked"]
        is False
    )
    assert mutation_summary["status"] == "failed"

    compile_save_contract = widget_preflight.build_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract(
        True,
        section_385_392_summary,
        build_current_widget_preflight_result(
            compile_executed=True,
            save_executed=True,
        ),
    )
    compile_save_summary = widget_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batches(
        [compile_save_contract]
    )
    assert (
        compile_save_contract["widget_compile_save_write_outputs_blocked"]
        is False
    )
    assert compile_save_summary["status"] == "failed"

    dirty_contract = widget_preflight.build_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract(
        True,
        section_385_392_summary,
        build_current_widget_preflight_result(
            dirty_content_after=[
                "/Game/_MCP_Temp/DurableSaveGate/WBP_Unexpected"
            ],
            asset_write_performed=True,
        ),
    )
    dirty_summary = widget_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batches(
        [dirty_contract]
    )
    assert (
        dirty_contract["user_widget_widget_tree_no_write_boundary_verified"]
        is False
    )
    assert dirty_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring UserWidget widget-tree live read-only preflight batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
