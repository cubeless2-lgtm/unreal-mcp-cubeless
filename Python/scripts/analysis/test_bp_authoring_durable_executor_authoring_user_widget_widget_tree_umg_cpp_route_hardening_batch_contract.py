#!/usr/bin/env python
"""Offline smoke tests for Sections 425-432 UserWidget UMG C++ route hardening."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract as route_preflight  # noqa: E402
import bp_authoring_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract as hardening  # noqa: E402
from test_bp_authoring_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract import build_current_section_409_416_summary  # noqa: E402


def build_current_section_417_424_summary() -> dict:
    section_409_416_summary = build_current_section_409_416_summary()
    result = route_preflight.build_user_widget_widget_tree_mutation_route_preflight_result()
    contract = route_preflight.build_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batch_contract(
        True,
        section_409_416_summary,
        result,
    )
    return route_preflight.summarize_durable_executor_authoring_user_widget_widget_tree_mutation_route_preflight_batches(
        [contract]
    )


def build_current_hardening_result(**overrides: object) -> dict:
    result = hardening.build_user_widget_widget_tree_umg_cpp_route_hardening_result()
    result.update(overrides)
    return result


def main() -> int:
    section_417_424_summary = build_current_section_417_424_summary()
    result = build_current_hardening_result()
    contract = hardening.build_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract(
        True,
        section_417_424_summary,
        result,
    )
    assert (
        contract["schema"]
        == hardening
        .DURABLE_EXECUTOR_AUTHORING_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_417_424_summary_schema_matches"] is True
    assert contract["section_417_424_summary_passed"] is True
    assert contract["section_417_424_user_widget_route_preflight_ready"] is True
    assert contract["section_417_424_outputs_closed"] is True
    assert contract["section_417_424_cpp_route_hardening_required"] is True
    assert contract["result_schema_matches"] is True
    assert (
        contract["user_widget_umg_cpp_route_hardening_checkpoint_satisfied"]
        is True
    )
    assert contract["user_widget_umg_cpp_temp_scope_gate_verified"] is True
    assert contract["user_widget_umg_cpp_no_save_default_verified"] is True
    assert (
        contract[
            "user_widget_umg_cpp_production_path_opt_in_guard_verified"
        ]
        is True
    )
    assert contract["user_widget_umg_cpp_widget_tree_mutation_route_hardened"] is True
    assert contract["user_widget_umg_cpp_build_verified"] is True
    assert contract["user_widget_umg_cpp_live_command_no_dispatch_verified"] is True
    assert contract["result_has_no_error"] is True
    assert (
        contract[
            "section_425_user_widget_umg_cpp_route_hardening_checkpoint_satisfied"
        ]
        is True
    )
    assert contract["section_426_user_widget_umg_cpp_temp_scope_gate_verified"] is True
    assert contract["section_427_user_widget_umg_cpp_no_save_default_verified"] is True
    assert (
        contract[
            "section_428_user_widget_umg_cpp_production_path_opt_in_guard_verified"
        ]
        is True
    )
    assert (
        contract[
            "section_429_user_widget_umg_cpp_widget_tree_mutation_route_hardened"
        ]
        is True
    )
    assert contract["section_430_user_widget_umg_cpp_build_verified"] is True
    assert (
        contract[
            "section_431_user_widget_umg_cpp_live_command_no_dispatch_verified"
        ]
        is True
    )
    assert (
        contract[
            "section_432_user_widget_widget_tree_umg_cpp_route_hardening_release_ready"
        ]
        is True
    )
    assert (
        contract["user_widget_widget_tree_umg_cpp_route_hardening_ready"]
        is True
    )
    assert contract["final_durable_release_ready"] is True

    summary = hardening.summarize_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    expected_one_counts = (
        "durable_requested_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_count",
        "section_417_424_summary_schema_matches_count",
        "section_417_424_summary_passed_count",
        "section_417_424_user_widget_route_preflight_ready_count",
        "section_417_424_outputs_closed_count",
        "section_417_424_cpp_route_hardening_required_count",
        "result_schema_matches_count",
        "user_widget_umg_cpp_route_hardening_checkpoint_satisfied_count",
        "user_widget_umg_cpp_temp_scope_gate_verified_count",
        "user_widget_umg_cpp_no_save_default_verified_count",
        "user_widget_umg_cpp_production_path_opt_in_guard_verified_count",
        "user_widget_umg_cpp_widget_tree_mutation_route_hardened_count",
        "user_widget_umg_cpp_build_verified_count",
        "user_widget_umg_cpp_live_command_no_dispatch_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_425_user_widget_umg_cpp_route_hardening_checkpoint_satisfied_count",
        "section_426_user_widget_umg_cpp_temp_scope_gate_verified_count",
        "section_427_user_widget_umg_cpp_no_save_default_verified_count",
        "section_428_user_widget_umg_cpp_production_path_opt_in_guard_verified_count",
        "section_429_user_widget_umg_cpp_widget_tree_mutation_route_hardened_count",
        "section_430_user_widget_umg_cpp_build_verified_count",
        "section_431_user_widget_umg_cpp_live_command_no_dispatch_verified_count",
        "section_432_user_widget_widget_tree_umg_cpp_route_hardening_release_ready_count",
        "user_widget_widget_tree_umg_cpp_route_hardening_ready_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in (
        hardening
        .BLOCKED_USER_WIDGET_WIDGET_TREE_UMG_CPP_ROUTE_HARDENING_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key

    missing_upstream = dict(section_417_424_summary)
    missing_upstream["cpp_route_hardening_required_count"] = 0
    missing_upstream_contract = hardening.build_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = hardening.summarize_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_417_424_cpp_route_hardening_required"
        ]
        is False
    )
    assert (
        missing_upstream_contract[
            "user_widget_widget_tree_umg_cpp_route_hardening_ready"
        ]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    missing_temp_gate_contract = hardening.build_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract(
        True,
        section_417_424_summary,
        build_current_hardening_result(
            cpp_default_safe_widget_root_present=False,
            cpp_validate_safe_package_name_present=False,
        ),
    )
    missing_temp_gate_summary = hardening.summarize_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batches(
        [missing_temp_gate_contract]
    )
    assert (
        missing_temp_gate_contract["user_widget_umg_cpp_temp_scope_gate_verified"]
        is False
    )
    assert missing_temp_gate_summary["status"] == "failed"

    save_default_open_contract = hardening.build_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract(
        True,
        section_417_424_summary,
        build_current_hardening_result(
            cpp_save_default_false_present=False,
            cpp_save_asset_guarded_by_save_flag=False,
            cpp_immediate_save_asset_removed=False,
        ),
    )
    save_default_open_summary = hardening.summarize_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batches(
        [save_default_open_contract]
    )
    assert (
        save_default_open_contract["user_widget_umg_cpp_no_save_default_verified"]
        is False
    )
    assert save_default_open_summary["status"] == "failed"

    missing_production_guard_contract = hardening.build_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract(
        True,
        section_417_424_summary,
        build_current_hardening_result(
            cpp_blocks_production_without_opt_in=False,
            production_path_write_allowed=True,
        ),
    )
    missing_production_guard_summary = hardening.summarize_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batches(
        [missing_production_guard_contract]
    )
    assert (
        missing_production_guard_contract[
            "user_widget_umg_cpp_production_path_opt_in_guard_verified"
        ]
        is False
    )
    assert missing_production_guard_summary["status"] == "failed"

    missing_build_contract = hardening.build_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract(
        True,
        section_417_424_summary,
        build_current_hardening_result(
            ubt_build_succeeded=False,
            ubt_no_hot_reload_from_ide_used=False,
        ),
    )
    missing_build_summary = hardening.summarize_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batches(
        [missing_build_contract]
    )
    assert missing_build_contract["user_widget_umg_cpp_build_verified"] is False
    assert missing_build_summary["status"] == "failed"

    live_dispatch_contract = hardening.build_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batch_contract(
        True,
        section_417_424_summary,
        build_current_hardening_result(
            live_command_dispatched=True,
            widget_tree_mutation_command_dispatched=True,
            widget_tree_mutation_performed=True,
        ),
    )
    live_dispatch_summary = hardening.summarize_durable_executor_authoring_user_widget_widget_tree_umg_cpp_route_hardening_batches(
        [live_dispatch_contract]
    )
    assert (
        live_dispatch_contract[
            "user_widget_umg_cpp_live_command_no_dispatch_verified"
        ]
        is False
    )
    assert live_dispatch_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring UserWidget UMG C++ route hardening batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
