#!/usr/bin/env python
"""Offline smoke tests for Sections 441-448 bridge port ownership preflight."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_contract as port_preflight  # noqa: E402
import bp_authoring_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_contract as reload_preflight  # noqa: E402
from test_bp_authoring_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_contract import build_current_section_425_432_summary  # noqa: E402


def build_current_section_433_440_summary() -> dict:
    section_425_432_summary = build_current_section_425_432_summary()
    result = reload_preflight.build_user_widget_correct_workspace_reload_preflight_result()
    contract = reload_preflight.build_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_contract(
        True,
        section_425_432_summary,
        result,
    )
    return reload_preflight.summarize_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batches(
        [contract]
    )


def build_current_port_preflight_result(**overrides: object) -> dict:
    result = port_preflight.build_user_widget_bridge_port_ownership_preflight_result()
    result.update(overrides)
    return result


def main() -> int:
    section_433_440_summary = build_current_section_433_440_summary()
    result = build_current_port_preflight_result()
    contract = port_preflight.build_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_contract(
        True,
        section_433_440_summary,
        result,
    )
    assert (
        contract["schema"]
        == port_preflight
        .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_433_440_summary_schema_matches"] is True
    assert contract["section_433_440_summary_passed"] is True
    assert contract["section_433_440_user_widget_reload_preflight_ready"] is True
    assert contract["section_433_440_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert contract["user_widget_bridge_port_ownership_checkpoint_satisfied"] is True
    assert contract["primary_bridge_port_probe_recorded"] is True
    assert contract["wrong_workspace_port_owner_detected"] is True
    assert contract["correct_workspace_bridge_port_unavailable"] is True
    assert contract["correct_workspace_bridge_start_blocked"] is True
    assert contract["live_user_widget_mutation_bridge_blocked"] is True
    assert contract["user_widget_bridge_port_no_dispatch_verified"] is True
    assert contract["result_has_no_error"] is True
    assert (
        contract["section_441_user_widget_bridge_port_ownership_checkpoint_satisfied"]
        is True
    )
    assert contract["section_442_primary_bridge_port_probe_recorded"] is True
    assert contract["section_443_wrong_workspace_port_owner_detected"] is True
    assert contract["section_444_correct_workspace_bridge_port_unavailable"] is True
    assert contract["section_445_correct_workspace_bridge_start_blocked"] is True
    assert contract["section_446_live_user_widget_mutation_bridge_blocked"] is True
    assert contract["section_447_user_widget_bridge_port_no_dispatch_verified"] is True
    assert (
        contract["section_448_user_widget_bridge_port_ownership_preflight_release_ready"]
        is True
    )
    assert contract["user_widget_bridge_port_ownership_preflight_ready"] is True
    assert contract["correct_workspace_bridge_port_release_still_required"] is True
    assert contract["final_durable_release_ready"] is True

    summary = port_preflight.summarize_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    expected_one_counts = (
        "durable_requested_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_count",
        "section_433_440_summary_schema_matches_count",
        "section_433_440_summary_passed_count",
        "section_433_440_user_widget_reload_preflight_ready_count",
        "section_433_440_outputs_closed_count",
        "result_schema_matches_count",
        "user_widget_bridge_port_ownership_checkpoint_satisfied_count",
        "primary_bridge_port_probe_recorded_count",
        "wrong_workspace_port_owner_detected_count",
        "correct_workspace_bridge_port_unavailable_count",
        "correct_workspace_bridge_start_blocked_count",
        "live_user_widget_mutation_bridge_blocked_count",
        "user_widget_bridge_port_no_dispatch_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
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
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in (
        port_preflight
        .BLOCKED_USER_WIDGET_BRIDGE_PORT_OWNERSHIP_PREFLIGHT_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key

    missing_upstream = dict(section_433_440_summary)
    missing_upstream["user_widget_correct_workspace_reload_preflight_ready_count"] = 0
    missing_upstream_contract = port_preflight.build_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = port_preflight.summarize_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_433_440_user_widget_reload_preflight_ready"
        ]
        is False
    )
    assert (
        missing_upstream_contract[
            "user_widget_bridge_port_ownership_preflight_ready"
        ]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    no_port_owner_contract = port_preflight.build_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_contract(
        True,
        section_433_440_summary,
        build_current_port_preflight_result(
            port_listen_detected=False,
            port_established_detected=False,
            correct_workspace_bridge_port_available=True,
            correct_workspace_bridge_start_blocked=False,
        ),
    )
    no_port_owner_summary = port_preflight.summarize_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batches(
        [no_port_owner_contract]
    )
    assert no_port_owner_contract["primary_bridge_port_probe_recorded"] is False
    assert no_port_owner_summary["status"] == "failed"

    correct_owner_contract = port_preflight.build_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_contract(
        True,
        section_433_440_summary,
        build_current_port_preflight_result(
            port_owner_project_file_path=port_preflight.DEFAULT_PROJECT_FILE_PATH,
            port_owner_matches_expected_project=True,
            correct_workspace_bridge_port_available=True,
            correct_workspace_bridge_start_blocked=False,
            correct_workspace_bridge_started=True,
            correct_workspace_bridge_verified=True,
            live_user_widget_mutation_bridge_blocked=False,
        ),
    )
    correct_owner_summary = port_preflight.summarize_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batches(
        [correct_owner_contract]
    )
    assert correct_owner_contract["wrong_workspace_port_owner_detected"] is False
    assert correct_owner_summary["status"] == "failed"

    live_dispatch_contract = port_preflight.build_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batch_contract(
        True,
        section_433_440_summary,
        build_current_port_preflight_result(
            live_command_dispatched=True,
            widget_tree_mutation_command_dispatched=True,
            widget_tree_mutation_performed=True,
        ),
    )
    live_dispatch_summary = port_preflight.summarize_durable_executor_authoring_user_widget_bridge_port_ownership_preflight_batches(
        [live_dispatch_contract]
    )
    assert live_dispatch_contract["user_widget_bridge_port_no_dispatch_verified"] is False
    assert live_dispatch_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring UserWidget bridge port ownership preflight batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
