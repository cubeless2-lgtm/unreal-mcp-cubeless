#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_release_decision_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_mvp_decision_contract as mvp_decision  # noqa: E402
import bp_authoring_durable_release_decision_contract as release_decision  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def main() -> int:
    manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    contract_summary = job_contract.summarize_manifests(manifests)
    executor_summary = manifest_executor.summarize_executor_policies(
        manifests,
        job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    mvp = mvp_decision.build_mvp_decision_contract(
        contract_summary,
        executor_summary,
        {
            "status": "passed",
            "release_boundary_version": "section_70_v12",
            "durable_authoring_enabled": False,
        },
    )
    contract = release_decision.build_durable_release_decision_contract(
        True,
        mvp,
        executor_summary,
        ["passed"] * 9,
    )
    assert contract["schema"] == release_decision.DURABLE_RELEASE_DECISION_SCHEMA
    assert contract["requested"] is True
    assert contract["decision_status"] == "section_70_temporary_mvp_ready_durable_not_enabled"
    assert contract["temporary_blueprint_authoring_mvp_ready"] is True
    assert contract["durable_blueprint_authoring_mvp_ready"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["section_61_69_safety_contracts_passed"] is True
    assert contract["section_61_69_safety_contract_count"] == 9
    assert contract["durable_executor_enabled_count"] == 0
    assert contract["durable_executor_executable_count"] == 0
    assert contract["save_or_delete_commands_allowed_count"] == 0
    assert contract["allowed_live_authoring_command_count"] == 0
    assert contract["preflight_pass_count"] == 0
    assert contract["final_durable_release_ready"] is False
    assert contract["main_push_requested"] is False

    summary = release_decision.summarize_durable_release_decisions([contract])
    assert summary == {
        "schema": release_decision.DURABLE_RELEASE_DECISION_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_release_decision_count": 1,
        "temporary_blueprint_authoring_mvp_ready_count": 1,
        "durable_blueprint_authoring_mvp_ready_count": 0,
        "durable_authoring_enabled_count": 0,
        "section_61_69_safety_contracts_passed_count": 1,
        "durable_executor_enabled_count": 0,
        "durable_executor_executable_count": 0,
        "save_or_delete_commands_allowed_count": 0,
        "allowed_live_authoring_command_count": 0,
        "preflight_pass_count": 0,
        "final_durable_release_ready_count": 0,
    }

    print("BP authoring durable release decision contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
