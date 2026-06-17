#!/usr/bin/env python
"""Offline smoke tests for Sections 433-440 correct-workspace reload preflight."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_contract as reload_preflight  # noqa: E402
import bp_authoring_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract as hardening  # noqa: E402
from test_bp_authoring_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract import build_current_section_417_424_summary  # noqa: E402


def build_current_section_425_432_summary() -> dict:
    section_417_424_summary = build_current_section_417_424_summary()
    result = hardening.build_user_widget_widget_tree_umg_cpp_route_hardening_result()
    contract = hardening.build_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract(
        True,
        section_417_424_summary,
        result,
    )
    return hardening.summarize_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batches(
        [contract]
    )


def build_current_reload_preflight_result(**overrides: object) -> dict:
    result = reload_preflight.build_user_widget_correct_workspace_reload_preflight_result()
    result.update(overrides)
    return result


def main() -> int:
    section_425_432_summary = build_current_section_425_432_summary()
    result = build_current_reload_preflight_result()
    contract = reload_preflight.build_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_contract(
        True,
        section_425_432_summary,
        result,
    )
    assert (
        contract["schema"]
        == reload_preflight
        .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_425_432_summary_schema_matches"] is True
    assert contract["section_425_432_summary_passed"] is True
    assert contract["section_425_432_user_widget_umg_cpp_route_hardening_ready"] is True
    assert contract["section_425_432_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert (
        contract["user_widget_correct_workspace_reload_checkpoint_satisfied"]
        is True
    )
    assert contract["hardened_unreal_mcp_dll_on_disk_verified"] is True
    assert contract["running_editor_workspace_mismatch_detected"] is True
    assert (
        contract["running_editor_unreal_mcp_module_mismatch_detected"]
        is True
    )
    assert contract["correct_workspace_live_bridge_blocked"] is True
    assert (
        contract["correct_workspace_editor_restart_required_recorded"]
        is True
    )
    assert contract["user_widget_live_mutation_command_no_dispatch_verified"] is True
    assert contract["result_has_no_error"] is True
    assert (
        contract[
            "section_433_user_widget_correct_workspace_reload_checkpoint_satisfied"
        ]
        is True
    )
    assert contract["section_434_hardened_unreal_mcp_dll_on_disk_verified"] is True
    assert contract["section_435_running_editor_workspace_mismatch_detected"] is True
    assert (
        contract[
            "section_436_running_editor_unreal_mcp_module_mismatch_detected"
        ]
        is True
    )
    assert contract["section_437_correct_workspace_live_bridge_blocked"] is True
    assert (
        contract[
            "section_438_correct_workspace_editor_restart_required_recorded"
        ]
        is True
    )
    assert (
        contract[
            "section_439_user_widget_live_mutation_command_no_dispatch_verified"
        ]
        is True
    )
    assert (
        contract[
            "section_440_user_widget_correct_workspace_reload_preflight_release_ready"
        ]
        is True
    )
    assert contract["user_widget_correct_workspace_reload_preflight_ready"] is True
    assert contract["correct_workspace_editor_reload_still_required"] is True
    assert contract["final_durable_release_ready"] is True

    summary = reload_preflight.summarize_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    expected_one_counts = (
        "durable_requested_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_count",
        "section_425_432_summary_schema_matches_count",
        "section_425_432_summary_passed_count",
        "section_425_432_user_widget_umg_cpp_route_hardening_ready_count",
        "section_425_432_outputs_closed_count",
        "result_schema_matches_count",
        "user_widget_correct_workspace_reload_checkpoint_satisfied_count",
        "hardened_unreal_mcp_dll_on_disk_verified_count",
        "running_editor_workspace_mismatch_detected_count",
        "running_editor_unreal_mcp_module_mismatch_detected_count",
        "correct_workspace_live_bridge_blocked_count",
        "correct_workspace_editor_restart_required_recorded_count",
        "user_widget_live_mutation_command_no_dispatch_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_433_user_widget_correct_workspace_reload_checkpoint_satisfied_count",
        "section_434_hardened_unreal_mcp_dll_on_disk_verified_count",
        "section_435_running_editor_workspace_mismatch_detected_count",
        "section_436_running_editor_unreal_mcp_module_mismatch_detected_count",
        "section_437_correct_workspace_live_bridge_blocked_count",
        "section_438_correct_workspace_editor_restart_required_recorded_count",
        "section_439_user_widget_live_mutation_command_no_dispatch_verified_count",
        "section_440_user_widget_correct_workspace_reload_preflight_release_ready_count",
        "user_widget_correct_workspace_reload_preflight_ready_count",
        "correct_workspace_editor_reload_still_required_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in (
        reload_preflight
        .BLOCKED_USER_WIDGET_CORRECT_WORKSPACE_RELOAD_PREFLIGHT_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key

    missing_upstream = dict(section_425_432_summary)
    missing_upstream["user_widget_widget_tree_umg_cpp_route_hardening_ready_count"] = 0
    missing_upstream_contract = reload_preflight.build_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = reload_preflight.summarize_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_425_432_user_widget_umg_cpp_route_hardening_ready"
        ]
        is False
    )
    assert (
        missing_upstream_contract[
            "user_widget_correct_workspace_reload_preflight_ready"
        ]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    missing_dll_contract = reload_preflight.build_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_contract(
        True,
        section_425_432_summary,
        build_current_reload_preflight_result(
            hardened_unreal_mcp_dll_exists=False,
            hardened_unreal_mcp_dll_size_bytes=0,
        ),
    )
    missing_dll_summary = reload_preflight.summarize_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batches(
        [missing_dll_contract]
    )
    assert missing_dll_contract["hardened_unreal_mcp_dll_on_disk_verified"] is False
    assert missing_dll_summary["status"] == "failed"

    correct_editor_loaded_contract = reload_preflight.build_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_contract(
        True,
        section_425_432_summary,
        build_current_reload_preflight_result(
            running_editor_project_file_path=reload_preflight.DEFAULT_PROJECT_FILE_PATH,
            running_editor_unreal_mcp_dll_path=reload_preflight.DEFAULT_EXPECTED_UNREAL_MCP_DLL_PATH,
            running_editor_matches_expected_project=True,
            running_editor_loaded_expected_unreal_mcp_dll=True,
            correct_workspace_editor_session_loaded=True,
            correct_workspace_live_bridge_verified=True,
            correct_workspace_editor_restart_required=False,
        ),
    )
    correct_editor_loaded_summary = reload_preflight.summarize_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batches(
        [correct_editor_loaded_contract]
    )
    assert (
        correct_editor_loaded_contract[
            "running_editor_workspace_mismatch_detected"
        ]
        is False
    )
    assert (
        correct_editor_loaded_contract["correct_workspace_live_bridge_blocked"]
        is False
    )
    assert correct_editor_loaded_summary["status"] == "failed"

    live_dispatch_contract = reload_preflight.build_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batch_contract(
        True,
        section_425_432_summary,
        build_current_reload_preflight_result(
            live_command_dispatched=True,
            widget_tree_mutation_command_dispatched=True,
            widget_tree_mutation_performed=True,
        ),
    )
    live_dispatch_summary = reload_preflight.summarize_durable_executor_authoring_user_widget_correct_workspace_reload_preflight_batches(
        [live_dispatch_contract]
    )
    assert (
        live_dispatch_contract[
            "user_widget_live_mutation_command_no_dispatch_verified"
        ]
        is False
    )
    assert live_dispatch_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring UserWidget correct-workspace reload preflight batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
