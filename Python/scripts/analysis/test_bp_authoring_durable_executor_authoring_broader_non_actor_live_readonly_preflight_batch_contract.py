#!/usr/bin/env python
"""Offline smoke tests for Sections 377-384 non-Actor read-only preflight."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract as broader_live  # noqa: E402
import bp_authoring_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract as live_route  # noqa: E402
from test_bp_authoring_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract import build_current_section_361_368_summary  # noqa: E402


def build_current_section_369_376_summary() -> dict:
    section_361_368_summary = build_current_section_361_368_summary()
    result = live_route.build_correct_project_live_mcp_route_preflight_result()
    contract = live_route.build_durable_executor_authoring_correct_project_live_mcp_route_preflight_batch_contract(
        True,
        section_361_368_summary,
        result,
    )
    return live_route.summarize_durable_executor_authoring_correct_project_live_mcp_route_preflight_batches(
        [contract]
    )


def build_current_broader_live_readonly_result(**overrides: object) -> dict:
    result = (
        broader_live.build_broader_non_actor_live_readonly_preflight_result()
    )
    result.update(overrides)
    return result


def main() -> int:
    section_369_376_summary = build_current_section_369_376_summary()
    result = build_current_broader_live_readonly_result()
    contract = broader_live.build_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract(
        True,
        section_369_376_summary,
        result,
    )
    assert (
        contract["schema"]
        == broader_live
        .DURABLE_EXECUTOR_AUTHORING_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_369_376_summary_schema_matches"] is True
    assert contract["section_369_376_summary_passed"] is True
    assert (
        contract["section_369_376_correct_project_live_route_preflight_ready"]
        is True
    )
    assert contract["section_369_376_outputs_closed"] is True
    assert contract["result_schema_matches"] is True
    assert (
        contract["broader_non_actor_live_readonly_checkpoint_satisfied"]
        is True
    )
    assert (
        contract[
            "correct_project_headless_non_actor_readonly_probe_recorded"
        ]
        is True
    )
    assert contract["non_actor_factory_prerequisites_verified"] is True
    assert contract["user_widget_readonly_prerequisites_verified"] is True
    assert contract["data_asset_readonly_prerequisites_verified"] is True
    assert contract["anim_blueprint_readonly_prerequisites_verified"] is True
    assert contract["non_actor_creation_mutation_outputs_blocked"] is True
    assert (
        contract[
            "broader_non_actor_live_readonly_no_write_boundary_verified"
        ]
        is True
    )
    assert contract["result_has_no_error"] is True
    assert (
        contract[
            "section_377_broader_non_actor_live_readonly_checkpoint_satisfied"
        ]
        is True
    )
    assert (
        contract[
            "section_378_correct_project_headless_non_actor_readonly_probe_recorded"
        ]
        is True
    )
    assert (
        contract["section_379_user_widget_readonly_prerequisites_verified"]
        is True
    )
    assert (
        contract["section_380_data_asset_readonly_prerequisites_verified"]
        is True
    )
    assert (
        contract["section_381_anim_blueprint_readonly_prerequisites_verified"]
        is True
    )
    assert (
        contract["section_382_non_actor_creation_mutation_outputs_blocked"]
        is True
    )
    assert (
        contract[
            "section_383_broader_non_actor_live_readonly_no_write_boundary_verified"
        ]
        is True
    )
    assert (
        contract[
            "section_384_broader_non_actor_live_readonly_preflight_release_ready"
        ]
        is True
    )
    assert contract["broader_non_actor_live_readonly_preflight_ready"] is True
    assert contract["broader_non_actor_actual_authoring_still_blocked"] is True
    assert contract["final_durable_release_ready"] is True

    summary = broader_live.summarize_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batches(
        [contract]
    )
    assert summary["status"] == "passed"
    expected_one_counts = (
        "durable_requested_executor_authoring_broader_non_actor_live_readonly_preflight_batch_count",
        "section_369_376_summary_schema_matches_count",
        "section_369_376_summary_passed_count",
        "section_369_376_correct_project_live_route_preflight_ready_count",
        "section_369_376_outputs_closed_count",
        "result_schema_matches_count",
        "broader_non_actor_live_readonly_checkpoint_satisfied_count",
        "correct_project_headless_non_actor_readonly_probe_recorded_count",
        "non_actor_factory_prerequisites_verified_count",
        "user_widget_readonly_prerequisites_verified_count",
        "data_asset_readonly_prerequisites_verified_count",
        "anim_blueprint_readonly_prerequisites_verified_count",
        "non_actor_creation_mutation_outputs_blocked_count",
        "broader_non_actor_live_readonly_no_write_boundary_verified_count",
        "result_has_no_error_count",
        "final_durable_release_ready_count",
        "section_377_broader_non_actor_live_readonly_checkpoint_satisfied_count",
        "section_378_correct_project_headless_non_actor_readonly_probe_recorded_count",
        "section_379_user_widget_readonly_prerequisites_verified_count",
        "section_380_data_asset_readonly_prerequisites_verified_count",
        "section_381_anim_blueprint_readonly_prerequisites_verified_count",
        "section_382_non_actor_creation_mutation_outputs_blocked_count",
        "section_383_broader_non_actor_live_readonly_no_write_boundary_verified_count",
        "section_384_broader_non_actor_live_readonly_preflight_release_ready_count",
        "broader_non_actor_live_readonly_preflight_ready_count",
        "broader_non_actor_actual_authoring_still_blocked_count",
    )
    for key in expected_one_counts:
        assert summary[key] == 1, key
    for key in (
        broader_live
        .BLOCKED_BROADER_NON_ACTOR_LIVE_READONLY_PREFLIGHT_OUTPUT_COUNT_KEYS
    ):
        assert summary[key] == 0, key

    missing_upstream = dict(section_369_376_summary)
    missing_upstream["correct_project_live_mcp_route_preflight_ready_count"] = 0
    missing_upstream_contract = broader_live.build_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract(
        True,
        missing_upstream,
        result,
    )
    missing_upstream_summary = broader_live.summarize_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batches(
        [missing_upstream_contract]
    )
    assert (
        missing_upstream_contract[
            "section_369_376_correct_project_live_route_preflight_ready"
        ]
        is False
    )
    assert (
        missing_upstream_contract[
            "broader_non_actor_live_readonly_preflight_ready"
        ]
        is False
    )
    assert missing_upstream_summary["status"] == "failed"

    wrong_project_contract = broader_live.build_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract(
        True,
        section_369_376_summary,
        build_current_broader_live_readonly_result(
            project_file_path="D:/Other/OtherProject.uproject",
            correct_project_loaded=False,
        ),
    )
    wrong_project_summary = broader_live.summarize_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batches(
        [wrong_project_contract]
    )
    assert (
        wrong_project_contract[
            "correct_project_headless_non_actor_readonly_probe_recorded"
        ]
        is False
    )
    assert wrong_project_summary["status"] == "failed"

    missing_factory_contract = broader_live.build_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract(
        True,
        section_369_376_summary,
        build_current_broader_live_readonly_result(
            factory_classes={"WidgetBlueprintFactory": False},
        ),
    )
    missing_factory_summary = broader_live.summarize_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batches(
        [missing_factory_contract]
    )
    assert (
        missing_factory_contract[
            "non_actor_factory_prerequisites_verified"
        ]
        is False
    )
    assert (
        missing_factory_contract[
            "user_widget_readonly_prerequisites_verified"
        ]
        is False
    )
    assert missing_factory_summary["status"] == "failed"

    missing_parent_contract = broader_live.build_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract(
        True,
        section_369_376_summary,
        build_current_broader_live_readonly_result(
            parent_class_probes={
                "AnimInstance": {
                    "path": "/Script/Engine.Actor",
                    "class_name": "Actor",
                    "loaded": True,
                }
            },
        ),
    )
    missing_parent_summary = broader_live.summarize_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batches(
        [missing_parent_contract]
    )
    assert (
        missing_parent_contract[
            "anim_blueprint_readonly_prerequisites_verified"
        ]
        is False
    )
    assert missing_parent_summary["status"] == "failed"

    creation_contract = broader_live.build_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract(
        True,
        section_369_376_summary,
        build_current_broader_live_readonly_result(
            non_actor_blueprint_creation_command_dispatched=True,
            user_widget_blueprint_create_command_dispatched=True,
        ),
    )
    creation_summary = broader_live.summarize_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batches(
        [creation_contract]
    )
    assert (
        creation_contract["non_actor_creation_mutation_outputs_blocked"]
        is False
    )
    assert creation_summary["status"] == "failed"

    dirty_contract = broader_live.build_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batch_contract(
        True,
        section_369_376_summary,
        build_current_broader_live_readonly_result(
            dirty_content_after=[
                "/Game/_MCP_Temp/DurableSaveGate/WBP_Unexpected"
            ],
            asset_write_performed=True,
        ),
    )
    dirty_summary = broader_live.summarize_durable_executor_authoring_broader_non_actor_live_readonly_preflight_batches(
        [dirty_contract]
    )
    assert (
        dirty_contract[
            "broader_non_actor_live_readonly_no_write_boundary_verified"
        ]
        is False
    )
    assert dirty_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring broader non-Actor live read-only preflight batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
