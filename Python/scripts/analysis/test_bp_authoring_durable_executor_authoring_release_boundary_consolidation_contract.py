#!/usr/bin/env python
"""Offline smoke tests for Section 181 release boundary consolidation contract."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_command_admission_dry_run_contract as command_admission  # noqa: E402
import bp_authoring_durable_executor_authoring_release_boundary_consolidation_contract as consolidation  # noqa: E402
from bp_authoring_durable_executor_authoring_release_stage_dry_run_test_helper import build_previous_summary  # noqa: E402


def build_current_section_180_summary() -> dict:
    section_179_summary = build_previous_summary(command_admission)
    contract = (
        command_admission.build_durable_executor_authoring_command_admission_dry_run_contract(
            True,
            section_179_summary,
            None,
        )
    )
    return command_admission.summarize_durable_executor_authoring_command_admission_dry_runs(
        [contract]
    )


def main() -> int:
    section_180_summary = build_current_section_180_summary()
    contract = consolidation.build_durable_executor_authoring_release_boundary_consolidation_contract(
        True,
        section_180_summary,
    )
    assert (
        contract["schema"]
        == consolidation.DURABLE_EXECUTOR_AUTHORING_RELEASE_BOUNDARY_CONSOLIDATION_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_180_summary_schema_matches"] is True
    assert contract["section_180_summary_passed"] is True
    assert contract["section_180_command_admission_contract_defined"] is True
    assert contract["section_179_command_path_contract_ready"] is True
    assert contract["section_180_command_path_chain_unsatisfied"] is True
    assert contract["command_admission_record_absent"] is True
    assert contract["command_admission_record_not_valid"] is True
    assert contract["command_admission_not_admissible"] is True
    assert contract["command_admission_missing_prerequisites_match"] is True
    assert contract["no_forbidden_or_unknown_requested_commands"] is True
    assert contract["no_rejected_or_unsafe_records"] is True
    assert contract["blocked_outputs_zero"] is True
    assert contract["durable_authoring_enabled"] is False
    assert contract["final_durable_release_ready"] is False
    assert contract["durable_safety_boundary_unlock_ready"] is False
    assert contract["release_boundary_consolidated"] is True
    assert contract["durable_authoring_command_allowed_count"] == 0
    assert contract["save_delete_rename_allowed_count"] == 0
    assert contract["live_command_dispatched_count"] == 0

    summary = (
        consolidation.summarize_durable_executor_authoring_release_boundary_consolidations(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_release_boundary_consolidation_count"
        ]
        == 1
    )
    assert summary["release_boundary_consolidated_count"] == 1
    assert summary["durable_authoring_enabled_count"] == 0
    assert summary["final_durable_release_ready_count"] == 0
    assert summary["durable_safety_boundary_unlock_ready_count"] == 0
    assert summary["durable_authoring_command_allowed_count"] == 0
    assert summary["save_delete_rename_allowed_count"] == 0
    assert summary["live_command_executed_count"] == 0

    unsafe_summary = dict(section_180_summary)
    unsafe_summary["durable_authoring_command_allowed_count"] = 1
    unsafe_contract = consolidation.build_durable_executor_authoring_release_boundary_consolidation_contract(
        True,
        unsafe_summary,
    )
    assert unsafe_contract["blocked_outputs_zero"] is False
    assert unsafe_contract["release_boundary_consolidated"] is False
    unsafe_result = (
        consolidation.summarize_durable_executor_authoring_release_boundary_consolidations(
            [unsafe_contract]
        )
    )
    assert unsafe_result["status"] == "failed"
    assert unsafe_result["durable_authoring_command_allowed_count"] == 1

    print(
        "BP authoring durable executor authoring release boundary consolidation contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
