#!/usr/bin/env python
"""
Section 181 durable executor authoring release boundary consolidation contract.

This contract consolidates the Section 177-180 dry-run boundary after command
admission. It does not unlock durable authoring, open command paths, allow
authoring commands, dispatch live commands, execute live commands, modify
assets, dirty packages, save, delete/rename, cleanup, change code, or probe
live bridges.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DURABLE_EXECUTOR_AUTHORING_RELEASE_BOUNDARY_CONSOLIDATION_SCHEMA = (
    "section_181_durable_executor_authoring_release_boundary_consolidation_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_RELEASE_BOUNDARY_CONSOLIDATION_SUMMARY_SCHEMA = (
    "section_181_durable_executor_authoring_release_boundary_consolidation_summary_v1"
)
EXPECTED_COMMAND_ADMISSION_MISSING_PREREQUISITE_COUNT = 55
COMMAND_ADMISSION_SUMMARY_SCHEMA = (
    "section_180_durable_executor_authoring_command_admission_dry_run_summary_v1"
)

BLOCKED_OUTPUT_COUNT_KEYS = (
    "command_admission_dry_run_admissible_count",
    "durable_authoring_command_admission_promoted_count",
    "durable_authoring_command_contract_started_count",
    "durable_authoring_command_contract_accepted_count",
    "durable_authoring_command_allowed_count",
    "durable_authoring_command_dispatched_count",
    "durable_authoring_command_executed_count",
    "durable_authoring_command_completed_count",
    "durable_executor_command_path_opened_count",
    "durable_executor_command_path_allowed_count",
    "durable_executor_open_promotion_barrier_promoted_count",
    "durable_executor_open_promotion_barrier_started_count",
    "durable_executor_open_promotion_barrier_accepted_count",
    "durable_executor_open_contract_started_count",
    "durable_executor_open_contract_accepted_count",
    "durable_executor_open_performed_count",
    "durable_executor_activated_count",
    "durable_executor_opened_count",
    "durable_authoring_enable_started_count",
    "durable_authoring_enabled_count",
    "durable_authoring_allowed_count",
    "final_durable_release_ready_count",
    "asset_write_performed_count",
    "package_dirty_marked_count",
    "code_change_performed_count",
    "executor_code_modified_count",
    "unreal_asset_modified_count",
    "live_bridge_probe_started_count",
    "save_delete_rename_allowed_count",
    "save_asset_allowed_count",
    "delete_asset_allowed_count",
    "rename_asset_allowed_count",
    "cleanup_allowed_count",
    "live_command_dispatched_count",
    "live_command_executed_count",
)


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _blocked_output_counts(summary: Dict[str, Any]) -> Dict[str, int]:
    return {
        key: int(summary.get(key, 0) or 0)
        for key in BLOCKED_OUTPUT_COUNT_KEYS
    }


def build_durable_executor_authoring_release_boundary_consolidation_contract(
    requested: bool,
    section_180_command_admission_dry_run_summary: Dict[str, Any],
) -> Dict[str, Any]:
    blocked_counts = _blocked_output_counts(
        section_180_command_admission_dry_run_summary
    )
    section_180_summary_schema_matches = bool(
        section_180_command_admission_dry_run_summary.get("schema")
        == COMMAND_ADMISSION_SUMMARY_SCHEMA
    )
    section_180_summary_passed = bool(
        section_180_command_admission_dry_run_summary.get("status") == "passed"
    )
    section_180_contract_defined = bool(
        section_180_command_admission_dry_run_summary.get(
            "command_admission_contract_defined_count"
        )
        == 1
    )
    section_180_command_path_ready = bool(
        section_180_command_admission_dry_run_summary.get(
            "section_179_command_path_contract_ready_count"
        )
        == 1
    )
    section_180_chain_unsatisfied = bool(
        section_180_command_admission_dry_run_summary.get(
            "command_path_chain_satisfied_count"
        )
        == 0
    )
    command_admission_record_absent = bool(
        section_180_command_admission_dry_run_summary.get(
            "command_admission_dry_run_record_present_count"
        )
        == 0
    )
    command_admission_record_not_valid = bool(
        section_180_command_admission_dry_run_summary.get(
            "command_admission_dry_run_record_valid_count"
        )
        == 0
    )
    command_admission_not_admissible = bool(
        section_180_command_admission_dry_run_summary.get(
            "command_admission_dry_run_admissible_count"
        )
        == 0
    )
    command_admission_missing_prerequisites_match = bool(
        section_180_command_admission_dry_run_summary.get(
            "missing_command_admission_dry_run_prerequisite_count"
        )
        == EXPECTED_COMMAND_ADMISSION_MISSING_PREREQUISITE_COUNT
    )
    no_forbidden_or_unknown_requested_commands = bool(
        section_180_command_admission_dry_run_summary.get(
            "requested_command_forbidden_count", 0
        )
        == 0
        and section_180_command_admission_dry_run_summary.get(
            "requested_command_unknown_count", 0
        )
        == 0
    )
    no_rejected_or_unsafe_records = bool(
        section_180_command_admission_dry_run_summary.get(
            "command_admission_dry_run_record_rejected_count", 0
        )
        == 0
        and section_180_command_admission_dry_run_summary.get(
            "unsafe_command_admission_record_count", 0
        )
        == 0
    )
    blocked_outputs_zero = all(count == 0 for count in blocked_counts.values())
    release_boundary_consolidated = bool(
        requested
        and section_180_summary_schema_matches
        and section_180_summary_passed
        and section_180_contract_defined
        and section_180_command_path_ready
        and section_180_chain_unsatisfied
        and command_admission_record_absent
        and command_admission_record_not_valid
        and command_admission_not_admissible
        and command_admission_missing_prerequisites_match
        and no_forbidden_or_unknown_requested_commands
        and no_rejected_or_unsafe_records
        and blocked_outputs_zero
    )
    return {
        "id": "durable_executor_authoring_release_boundary_consolidation",
        "schema": DURABLE_EXECUTOR_AUTHORING_RELEASE_BOUNDARY_CONSOLIDATION_SCHEMA,
        "requested": requested,
        "section_180_summary_schema_matches": section_180_summary_schema_matches,
        "section_180_summary_passed": section_180_summary_passed,
        "section_180_command_admission_contract_defined": (
            section_180_contract_defined
        ),
        "section_179_command_path_contract_ready": section_180_command_path_ready,
        "section_180_command_path_chain_unsatisfied": section_180_chain_unsatisfied,
        "command_admission_record_absent": command_admission_record_absent,
        "command_admission_record_not_valid": command_admission_record_not_valid,
        "command_admission_not_admissible": command_admission_not_admissible,
        "command_admission_missing_prerequisites_match": (
            command_admission_missing_prerequisites_match
        ),
        "no_forbidden_or_unknown_requested_commands": (
            no_forbidden_or_unknown_requested_commands
        ),
        "no_rejected_or_unsafe_records": no_rejected_or_unsafe_records,
        "blocked_outputs_zero": blocked_outputs_zero,
        "durable_authoring_enabled": False,
        "final_durable_release_ready": False,
        "durable_safety_boundary_unlock_ready": False,
        "release_boundary_consolidated": release_boundary_consolidated,
        **blocked_counts,
    }


def summarize_durable_executor_authoring_release_boundary_consolidations(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "release_boundary_consolidated")
            == len(requested)
            and _truthy_count(requested, "durable_authoring_enabled") == 0
            and _truthy_count(requested, "final_durable_release_ready") == 0
            and _truthy_count(requested, "durable_safety_boundary_unlock_ready") == 0
            and all(_sum_count(requested, key) == 0 for key in BLOCKED_OUTPUT_COUNT_KEYS)
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": DURABLE_EXECUTOR_AUTHORING_RELEASE_BOUNDARY_CONSOLIDATION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_authoring_release_boundary_consolidation_count": (
            len(requested)
        ),
        "release_boundary_consolidated_count": _truthy_count(
            requested, "release_boundary_consolidated"
        ),
        "section_180_summary_schema_matches_count": _truthy_count(
            requested, "section_180_summary_schema_matches"
        ),
        "section_180_summary_passed_count": _truthy_count(
            requested, "section_180_summary_passed"
        ),
        "section_180_command_admission_contract_defined_count": _truthy_count(
            requested, "section_180_command_admission_contract_defined"
        ),
        "section_179_command_path_contract_ready_count": _truthy_count(
            requested, "section_179_command_path_contract_ready"
        ),
        "section_180_command_path_chain_unsatisfied_count": _truthy_count(
            requested, "section_180_command_path_chain_unsatisfied"
        ),
        "command_admission_record_absent_count": _truthy_count(
            requested, "command_admission_record_absent"
        ),
        "command_admission_record_not_valid_count": _truthy_count(
            requested, "command_admission_record_not_valid"
        ),
        "command_admission_not_admissible_count": _truthy_count(
            requested, "command_admission_not_admissible"
        ),
        "command_admission_missing_prerequisites_match_count": _truthy_count(
            requested, "command_admission_missing_prerequisites_match"
        ),
        "no_forbidden_or_unknown_requested_commands_count": _truthy_count(
            requested, "no_forbidden_or_unknown_requested_commands"
        ),
        "no_rejected_or_unsafe_records_count": _truthy_count(
            requested, "no_rejected_or_unsafe_records"
        ),
        "blocked_outputs_zero_count": _truthy_count(
            requested, "blocked_outputs_zero"
        ),
        "durable_authoring_enabled_count": _truthy_count(
            requested, "durable_authoring_enabled"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "durable_safety_boundary_unlock_ready_count": _truthy_count(
            requested, "durable_safety_boundary_unlock_ready"
        ),
    }
    summary.update({key: _sum_count(requested, key) for key in BLOCKED_OUTPUT_COUNT_KEYS})
    return summary
