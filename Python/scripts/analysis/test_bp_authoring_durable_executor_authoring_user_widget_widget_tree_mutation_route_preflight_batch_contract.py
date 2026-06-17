#!/usr/bin/env python
"""Offline smoke tests for Sections 417-424 WidgetTree mutation route preflight."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract as route_preflight  # noqa: E402
from test_bp_authoring_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract import build_current_section_401_408_summary  # noqa: E402
import bp_authoring_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract as actual_checkpoint  # noqa: E402


def build_current_section_409_416_summary() -> dict:
    section_401_408_summary = build_current_section_401_408_summary()
    result = actual_checkpoint.build_user_widget_actual_asset_creation_checkpoint_result()
    contract = actual_checkpoint.build_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batch_contract(
        True,
        section_401_408_summary,
        result,
    )
    return actual_checkpoint.summarize_durable_executor_authoring_user_widget_actual_asset_creation_checkpoint_batches(
        [contract]
    )


def build_current_preflight_result(**overrides: object) -> dict:
    result = route_preflight.build_user_widget_widget_tree_mutation_route_preflight_result()
    result.update(overrides)
    return result


def main() -> int:
    section_409_416_summary = build_current_section_409_416_summary()
    result = build_current_preflight_result()
    contract = route_preflight.build_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract(
        True,
        section_409_416_summary,
        result,
    )
    assert (
        contract["schema"]
        == route_preflight
        .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_MUTATION_ROUTE_PREFLIGHT_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_409_416_summary_schema_matches"] is True
    assert contract["section_409_416_summary_passed"] is True
    assert contract["section_409_416_user_widget_actual_checkpoint_ready"] is True
    assert contract["section_409_416_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert (
        contract["user_widget_widget_tree_route_preflight_checkpoint_satisfied"]
        is True
    )
    assert contract["user_widget_actual_temp_asset_readonly_confirmed"] is True
    assert contract["python_widget_tree_mutation_route_blocked"] is True
    assert contract["unreal_mcp_umg_cpp_route_detected"] is True
    assert contract["umg_cpp_route_safe_gate_hardening_required"] is True
    assert contract["widget_tree_mutation_execution_outputs_blocked"] is True
    assert (
        contract[
            "user_widget_widget_tree_route_preflight_no_write_boundary_verified"
        ]
        is True
    )
    assert contract["result_has_no_error"] is True
    assert (
        contract[
            "section_417_user_widget_widget_tree_route_preflight_checkpoint_satisfied"
        ]
        is True
    )
    assert (
        contract["section_418_user_widget_actual_temp_asset_readonly_confirmed"]
        is True
    )
    assert (
        contract["section_419_python_widget_tree_mutation_route_blocked"]
        is True
    )
    assert contract["section_420_unreal_mcp_umg_cpp_route_detected"] is True
    assert (
        contract["section_421_umg_cpp_route_safe_gate_hardening_required"]
        is True
    )
    assert (
        contract["section_422_widget_tree_mutation_execution_outputs_blocked"]
        is True
    )
    assert (
        contract[
            "section_423_user_widget_widget_tree_route_preflight_no_write_boundary_verified"
        ]
        is True
    )
    assert (
        contract[
            "section_424_user_widget_widget_tree_mutation_route_preflight_release_ready"
        ]
        is True
    )
    assert (
        contract["user_widget_widget_tree_mutation_route_preflight_ready"]
        is True
    )
    assert contract["user_widget_widget_tree_actual_mutation_still_blocked"] is True
    assert contract["cpp_route_hardening_required"] is True
    assert contract["final_durable_release_ready"] is True

    summary = route_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    expected_one_counts = (
        "durable_requested_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_count",
        "section_409_416_summary_schema_matches_count",
        "section_409_416_summary_passed_count",
        "section_409_416_user_widget_actual_checkpoint_ready_count",
        "section_409_416_outputs_closed_count",
        "result_schema_matches_count",
        "user_widget_widget_tree_route_preflight_checkpoint_satisfied_count",
        "user_widget_actual_temp_asset_readonly_confirmed_count",
        "python_widget_tree_mutation_route_blocked_count",
        "unreal_mcp_umg_cpp_route_detected_count",
        "umg_cpp_route_safe_gate_hardening_required_count",
        "widget_tree_mutation_execution_outputs_blocked_count",
        "user_widget_widget_tree_route_preflight_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_417_user_widget_widget_tree_route_preflight_checkpoint_satisfied_count",
        "section_418_user_widget_actual_temp_asset_readonly_confirmed_count",
        "section_419_python_widget_tree_mutation_route_blocked_count",
        "section_420_unreal_mcp_umg_cpp_route_detected_count",
        "section_421_umg_cpp_route_safe_gate_hardening_required_count",
        "section_422_widget_tree_mutation_execution_outputs_blocked_count",
        "section_423_user_widget_widget_tree_route_preflight_no_write_boundary_verified_count",
        "section_424_user_widget_widget_tree_mutation_route_preflight_release_ready_count",
        "user_widget_widget_tree_mutation_route_preflight_ready_count",
        "user_widget_widget_tree_actual_mutation_still_blocked_count",
        "cpp_route_hardening_required_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in (
        route_preflight
        .BLOCKED_USER_WIDGET_WIDGET_TREE_ROUTE_PREFLIGHT_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key

    missing_upstream = dict(section_409_416_summary)
    missing_upstream["user_widget_actual_asset_creation_checkpoint_ready_count"] = 0
    missing_upstream_contract = route_preflight.build_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = route_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_409_416_user_widget_actual_checkpoint_ready"
        ]
        is False
    )
    assert (
        missing_upstream_contract[
            "user_widget_widget_tree_mutation_route_preflight_ready"
        ]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    missing_asset_contract = route_preflight.build_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract(
        True,
        section_409_416_summary,
        build_current_preflight_result(
            target_asset_exists=False,
            target_package_file_exists=False,
            asset_loaded=False,
        ),
    )
    missing_asset_summary = route_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batches(
        [missing_asset_contract]
    )
    assert (
        missing_asset_contract["user_widget_actual_temp_asset_readonly_confirmed"]
        is False
    )
    assert missing_asset_summary["status"] == "failed"

    python_route_open_contract = route_preflight.build_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract(
        True,
        section_409_416_summary,
        build_current_preflight_result(
            python_widget_tree_class_available=True,
            python_widget_tree_property_accessible=True,
            python_construct_widget_route_ready=True,
            widget_tree_protected_access_error_count=0,
        ),
    )
    python_route_open_summary = route_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batches(
        [python_route_open_contract]
    )
    assert (
        python_route_open_contract["python_widget_tree_mutation_route_blocked"]
        is False
    )
    assert python_route_open_summary["status"] == "failed"

    missing_cpp_route_contract = route_preflight.build_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract(
        True,
        section_409_416_summary,
        build_current_preflight_result(
            unreal_mcp_umg_cpp_route_detected=False,
            cpp_uses_widget_tree_construct_widget=False,
        ),
    )
    missing_cpp_route_summary = route_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batches(
        [missing_cpp_route_contract]
    )
    assert missing_cpp_route_contract["unreal_mcp_umg_cpp_route_detected"] is False
    assert missing_cpp_route_summary["status"] == "failed"

    hardened_cpp_route_contract = route_preflight.build_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract(
        True,
        section_409_416_summary,
        build_current_preflight_result(
            cpp_fixed_game_widgets_path_present=False,
            cpp_immediate_save_asset_present=False,
            cpp_safe_target_path_parameter_present=True,
            cpp_no_save_mode_present=True,
            cpp_temp_scope_gate_present=True,
        ),
    )
    hardened_cpp_route_summary = route_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batches(
        [hardened_cpp_route_contract]
    )
    assert (
        hardened_cpp_route_contract["umg_cpp_route_safe_gate_hardening_required"]
        is False
    )
    assert hardened_cpp_route_summary["status"] == "failed"

    mutation_contract = route_preflight.build_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract(
        True,
        section_409_416_summary,
        build_current_preflight_result(
            widget_tree_mutation_command_dispatched=True,
            widget_tree_mutation_performed=True,
        ),
    )
    mutation_summary = route_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batches(
        [mutation_contract]
    )
    assert (
        mutation_contract["widget_tree_mutation_execution_outputs_blocked"]
        is False
    )
    assert mutation_summary["status"] == "failed"

    dirty_contract = route_preflight.build_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract(
        True,
        section_409_416_summary,
        build_current_preflight_result(
            dirty_content_after=[
                "/Game/_MCP_Temp/DurableSaveGate/UserWidgetActual/WBP_DurableWidgetTreeActual"
            ],
            target_dirty_after=True,
        ),
    )
    dirty_summary = route_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batches(
        [dirty_contract]
    )
    assert (
        dirty_contract[
            "user_widget_widget_tree_route_preflight_no_write_boundary_verified"
        ]
        is False
    )
    assert dirty_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring UserWidget WidgetTree mutation route preflight batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
