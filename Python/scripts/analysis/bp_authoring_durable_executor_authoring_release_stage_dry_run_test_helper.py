#!/usr/bin/env python
"""Test helpers for durable executor authoring release-stage dry-run contracts."""

from __future__ import annotations

from typing import Any, Callable, Dict


def build_previous_summary(module: Any, **overrides: object) -> Dict[str, object]:
    spec = module.STAGE_SPEC
    summary: Dict[str, object] = {
        "schema": "previous_stage_summary",
        "status": "passed",
        spec["previous_defined_count_key"]: 1,
        spec["previous_rejected_count_key"]: 0,
        spec["previous_unsafe_count_key"]: 0,
        "requested_command_forbidden_count": 0,
        "requested_command_unknown_count": 0,
    }
    for key in spec["previous_zero_count_keys"]:
        summary[key] = 0
    for _output_key, summary_key, _missing_key in module.CHAIN_INPUTS:
        summary.setdefault(summary_key, 0)
    summary.update(overrides)
    return summary


def build_future_previous_summary(module: Any) -> Dict[str, object]:
    return build_previous_summary(
        module,
        **{
            summary_key: 1
            for _output_key, summary_key, _missing_key in module.CHAIN_INPUTS
        },
    )


def build_stage_record(module: Any, **overrides: object) -> Dict[str, object]:
    spec = module.STAGE_SPEC
    record: Dict[str, object] = {
        "schema": spec["record_schema"],
        spec["scope_record_field"]: spec["expected_scope"],
        "status": "passed",
        "dry_run_only": True,
        "requested_command": "create_blueprint_asset",
        spec["operation_record_field"]: spec["allowed_operations"][-1],
        "target_asset": "/Game/MCPTestFixtures/BP_PlannerDurable",
        "operator_reconfirmed_no_live_dispatch": True,
        "operator_reconfirmed_no_live_execution": True,
        "operator_reconfirmed_no_write_execution": True,
        "operator_reconfirmed_no_save_delete_rename": True,
        spec["admission_proof_group"]: {
            output_key: True
            for output_key, _summary_key, _missing_key in module.CHAIN_INPUTS
        },
        "release_boundary_proof": {
            "durable_authoring_enabled": False,
            "final_durable_release_ready": False,
            "save_delete_rename_allowed": False,
            "live_durable_authoring_allowed": False,
        },
    }
    for key in module.OUTPUT_ACTION_KEYS:
        record[key] = False
    record.update(overrides)
    return record


def run_stage_smoke(
    module: Any,
    build_contract: Callable[[bool, Dict[str, object], Dict[str, object] | None], Dict[str, Any]],
    summarize: Callable[[list[Dict[str, Any]]], Dict[str, Any]],
    unsafe_key: str,
) -> None:
    spec = module.STAGE_SPEC
    current_summary = build_previous_summary(module)
    contract = build_contract(True, current_summary, None)
    assert contract["schema"] == spec["schema"]
    assert contract["requested"] is True
    assert contract[spec["contract_defined_key"]] is True
    assert contract[spec["previous_ready_key"]] is True
    assert contract[spec["chain_satisfied_key"]] is False
    assert contract[spec["record_present_key"]] is False
    assert contract[spec["record_valid_key"]] is False
    assert contract[spec["record_rejected_key"]] is False
    assert contract[spec["admissible_key"]] is False
    assert contract[spec["missing_count_key"]] == module.CURRENT_MISSING_PREREQUISITE_COUNT
    assert module.CHAIN_INPUTS[-1][2] in contract[spec["missing_prerequisites_key"]]
    assert spec["record_present_missing_key"] in contract[spec["missing_prerequisites_key"]]
    assert contract["durable_executor_command_path_opened"] is False
    assert contract["durable_authoring_command_allowed"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["final_durable_release_ready"] is False
    assert contract["save_delete_rename_allowed"] is False

    summary = summarize([contract])
    assert summary["status"] == "passed"
    assert summary[spec["request_count_key"]] == 1
    assert summary[spec["contract_defined_count_key"]] == 1
    assert summary[spec["previous_ready_count_key"]] == 1
    assert summary[spec["chain_satisfied_count_key"]] == 0
    assert summary[spec["record_present_count_key"]] == 0
    assert summary[spec["record_valid_count_key"]] == 0
    assert summary[spec["record_rejected_count_key"]] == 0
    assert summary[spec["admissible_count_key"]] == 0
    assert summary["durable_executor_command_path_opened_count"] == 0
    assert summary["durable_authoring_command_allowed_count"] == 0
    assert summary["durable_authoring_enabled_count"] == 0
    assert summary["final_durable_release_ready_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0

    blocked_with_record = build_contract(
        True,
        current_summary,
        build_stage_record(module),
    )
    assert blocked_with_record[spec["chain_satisfied_key"]] is False
    assert blocked_with_record[spec["record_valid_key"]] is False
    assert blocked_with_record[spec["record_rejected_key"]] is True
    assert blocked_with_record[spec["admissible_key"]] is False
    assert (
        blocked_with_record[spec["missing_count_key"]]
        == module.BLOCKED_WITH_RECORD_MISSING_PREREQUISITE_COUNT
    )
    assert blocked_with_record["durable_executor_command_path_opened"] is False
    assert blocked_with_record["durable_authoring_command_allowed"] is False
    assert blocked_with_record["save_delete_rename_allowed"] is False

    future_summary = build_future_previous_summary(module)
    future_contract = build_contract(
        True,
        future_summary,
        build_stage_record(module),
    )
    assert future_contract[spec["chain_satisfied_key"]] is True
    assert future_contract[spec["record_valid_key"]] is True
    assert future_contract[spec["record_rejected_key"]] is False
    assert future_contract[spec["admissible_key"]] is True
    assert future_contract[spec["missing_count_key"]] == 0
    for key in module.OUTPUT_ACTION_KEYS:
        if key != spec["admissible_key"]:
            assert future_contract[key] is False
    future_summary_result = summarize([future_contract])
    assert future_summary_result["status"] == "passed"
    assert future_summary_result[spec["admissible_count_key"]] == 1
    assert future_summary_result["durable_executor_command_path_opened_count"] == 0
    assert future_summary_result["durable_authoring_command_allowed_count"] == 0
    assert future_summary_result["save_delete_rename_allowed_count"] == 0

    forbidden_contract = build_contract(
        True,
        future_summary,
        build_stage_record(module, requested_command="save_asset"),
    )
    assert forbidden_contract["requested_command_forbidden"] is True
    assert forbidden_contract[spec["record_rejected_key"]] is True
    assert forbidden_contract[spec["admissible_key"]] is False
    forbidden_summary = summarize([forbidden_contract])
    assert forbidden_summary["status"] == "failed"
    assert forbidden_summary["requested_command_forbidden_count"] == 1
    assert forbidden_summary["durable_executor_command_path_opened_count"] == 0
    assert forbidden_summary["save_delete_rename_allowed_count"] == 0

    unsafe_contract = build_contract(
        True,
        future_summary,
        build_stage_record(module, **{unsafe_key: True}),
    )
    assert unsafe_contract[spec["unsafe_count_key"]] == 1
    assert unsafe_contract[spec["record_rejected_key"]] is True
    assert unsafe_contract[spec["admissible_key"]] is False
    assert unsafe_contract[unsafe_key] is False
    assert unsafe_contract["durable_executor_command_path_opened"] is False
    assert unsafe_contract["durable_authoring_command_allowed"] is False
    assert unsafe_contract["save_delete_rename_allowed"] is False
