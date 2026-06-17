#!/usr/bin/env python
"""Offline smoke tests for Sections 401-408 UserWidget dry-run admission."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract as dry_run  # noqa: E402
import bp_authoring_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract as preflight  # noqa: E402
from test_bp_authoring_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract import build_current_section_385_392_summary  # noqa: E402


def build_current_section_393_400_summary() -> dict:
    section_385_392_summary = build_current_section_385_392_summary()
    result = preflight.build_user_widget_widget_tree_live_readonly_preflight_result()
    contract = preflight.build_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batch_contract(
        True,
        section_385_392_summary,
        result,
    )
    return preflight.summarize_durable_executor_authoring_user_widget_widget_tree_live_readonly_preflight_batches(
        [contract]
    )


def build_current_dry_run_result(**overrides: object) -> dict:
    result = dry_run.build_user_widget_widget_tree_authoring_dry_run_admission_result()
    result.update(overrides)
    return result


def main() -> int:
    section_393_400_summary = build_current_section_393_400_summary()
    result = build_current_dry_run_result()
    contract = dry_run.build_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract(
        True,
        section_393_400_summary,
        result,
    )
    assert (
        contract["schema"]
        == dry_run
        .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_AUTHORING_DRY_RUN_ADMISSION_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_393_400_summary_schema_matches"] is True
    assert contract["section_393_400_summary_passed"] is True
    assert contract["section_393_400_user_widget_preflight_ready"] is True
    assert contract["section_393_400_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["user_widget_authoring_dry_run_checkpoint_satisfied"] is True
    assert contract["widget_blueprint_dry_run_scope_verified"] is True
    assert contract["root_widget_plan_classified"] is True
    assert contract["child_widget_slot_plan_classified"] is True
    assert contract["widget_binding_event_graph_plan_blocked"] is True
    assert contract["widget_authoring_creation_mutation_outputs_blocked"] is True
    assert (
        contract["user_widget_authoring_dry_run_no_write_boundary_verified"]
        is True
    )
    assert contract["result_has_no_error"] is True
    assert (
        contract["section_401_user_widget_authoring_dry_run_checkpoint_satisfied"]
        is True
    )
    assert contract["section_402_widget_blueprint_dry_run_scope_verified"] is True
    assert contract["section_403_root_widget_plan_classified"] is True
    assert contract["section_404_child_widget_slot_plan_classified"] is True
    assert contract["section_405_widget_binding_event_graph_plan_blocked"] is True
    assert (
        contract["section_406_widget_authoring_creation_mutation_outputs_blocked"]
        is True
    )
    assert (
        contract[
            "section_407_user_widget_authoring_dry_run_no_write_boundary_verified"
        ]
        is True
    )
    assert (
        contract[
            "section_408_user_widget_authoring_dry_run_admission_release_ready"
        ]
        is True
    )
    assert (
        contract["user_widget_widget_tree_authoring_dry_run_admission_ready"]
        is True
    )
    assert contract["user_widget_widget_tree_actual_authoring_still_blocked"] is True
    assert contract["final_durable_release_ready"] is True

    summary = dry_run.summarize_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    expected_one_counts = (
        "durable_requested_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_count",
        "section_393_400_summary_schema_matches_count",
        "section_393_400_summary_passed_count",
        "section_393_400_user_widget_preflight_ready_count",
        "section_393_400_outputs_closed_count",
        "result_schema_matches_count",
        "user_widget_authoring_dry_run_checkpoint_satisfied_count",
        "widget_blueprint_dry_run_scope_verified_count",
        "root_widget_plan_classified_count",
        "child_widget_slot_plan_classified_count",
        "widget_binding_event_graph_plan_blocked_count",
        "widget_authoring_creation_mutation_outputs_blocked_count",
        "user_widget_authoring_dry_run_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_401_user_widget_authoring_dry_run_checkpoint_satisfied_count",
        "section_402_widget_blueprint_dry_run_scope_verified_count",
        "section_403_root_widget_plan_classified_count",
        "section_404_child_widget_slot_plan_classified_count",
        "section_405_widget_binding_event_graph_plan_blocked_count",
        "section_406_widget_authoring_creation_mutation_outputs_blocked_count",
        "section_407_user_widget_authoring_dry_run_no_write_boundary_verified_count",
        "section_408_user_widget_authoring_dry_run_admission_release_ready_count",
        "user_widget_widget_tree_authoring_dry_run_admission_ready_count",
        "user_widget_widget_tree_actual_authoring_still_blocked_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in dry_run.BLOCKED_USER_WIDGET_AUTHORING_DRY_RUN_OUTPUT_COUNT_KEYS:
        assert summary[key] == 0, key

    missing_upstream = dict(section_393_400_summary)
    missing_upstream["user_widget_widget_tree_live_readonly_preflight_ready_count"] = 0
    missing_upstream_contract = dry_run.build_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = dry_run.summarize_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batches(
        [missing_upstream_contract]
    )
    assert missing_upstream_contract["section_393_400_user_widget_preflight_ready"] is False
    assert (
        missing_upstream_contract[
            "user_widget_widget_tree_authoring_dry_run_admission_ready"
        ]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    bad_scope_contract = dry_run.build_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract(
        True,
        section_393_400_summary,
        build_current_dry_run_result(
            target_asset_path="/Game/Production/WBP_DurableWidgetTreeDryRun",
        ),
    )
    bad_scope_summary = dry_run.summarize_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batches(
        [bad_scope_contract]
    )
    assert bad_scope_contract["widget_blueprint_dry_run_scope_verified"] is False
    assert bad_scope_summary["status"] == "failed"

    wrong_root_contract = dry_run.build_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract(
        True,
        section_393_400_summary,
        build_current_dry_run_result(root_widget_class="Overlay"),
    )
    wrong_root_summary = dry_run.summarize_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batches(
        [wrong_root_contract]
    )
    assert wrong_root_contract["root_widget_plan_classified"] is False
    assert wrong_root_summary["status"] == "failed"

    missing_child_contract = dry_run.build_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract(
        True,
        section_393_400_summary,
        build_current_dry_run_result(child_widget_classes=("Button",)),
    )
    missing_child_summary = dry_run.summarize_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batches(
        [missing_child_contract]
    )
    assert missing_child_contract["child_widget_slot_plan_classified"] is False
    assert missing_child_summary["status"] == "failed"

    binding_unblocked_contract = dry_run.build_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract(
        True,
        section_393_400_summary,
        build_current_dry_run_result(
            widget_binding_event_graph_plan_blocked=False,
        ),
    )
    binding_unblocked_summary = dry_run.summarize_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batches(
        [binding_unblocked_contract]
    )
    assert binding_unblocked_contract["widget_binding_event_graph_plan_blocked"] is False
    assert binding_unblocked_summary["status"] == "failed"

    mutation_contract = dry_run.build_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract(
        True,
        section_393_400_summary,
        build_current_dry_run_result(
            widget_blueprint_create_command_dispatched=True,
            widget_tree_mutation_command_dispatched=True,
        ),
    )
    mutation_summary = dry_run.summarize_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batches(
        [mutation_contract]
    )
    assert (
        mutation_contract[
            "widget_authoring_creation_mutation_outputs_blocked"
        ]
        is False
    )
    assert mutation_summary["status"] == "failed"

    dirty_contract = dry_run.build_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batch_contract(
        True,
        section_393_400_summary,
        build_current_dry_run_result(
            dirty_content_after_dry_run=[
                "/Game/_MCP_Temp/DurableSaveGate/UserWidgetDryRun/WBP_Unexpected"
            ],
            asset_write_performed=True,
        ),
    )
    dirty_summary = dry_run.summarize_durable_executor_authoring_user_widget_widget_tree_authoring_dry_run_admission_batches(
        [dirty_contract]
    )
    assert (
        dirty_contract[
            "user_widget_authoring_dry_run_no_write_boundary_verified"
        ]
        is False
    )
    assert dirty_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring UserWidget widget-tree authoring dry-run admission batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
