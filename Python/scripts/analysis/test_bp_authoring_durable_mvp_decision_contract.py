#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_mvp_decision_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_mvp_decision_contract as mvp_decision  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def main() -> int:
    manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    contract_summary = job_contract.summarize_manifests(manifests)
    executor_summary = manifest_executor.summarize_executor_policies(manifests, job_contract.DEFAULT_TEMP_PACKAGE_PATH)
    decision = mvp_decision.build_mvp_decision_contract(
        contract_summary,
        executor_summary,
        {
            "status": "passed",
            "release_boundary_version": "section_59_v2",
            "durable_authoring_enabled": False,
        },
    )
    assert decision["schema"] == mvp_decision.MVP_DECISION_SCHEMA
    assert decision["decision_status"] == "temporary_mvp_ready_durable_not_enabled"
    assert decision["temporary_blueprint_authoring_mvp_ready"] is True
    assert decision["durable_blueprint_authoring_mvp_ready"] is False
    assert decision["durable_authoring_enabled"] is False
    assert decision["durable_save_allowed"] is False
    assert decision["durable_delete_allowed"] is False
    assert decision["durable_rename_allowed"] is False
    assert decision["durable_cleanup_allowed"] is False
    assert decision["durable_canary_live_execution_allowed"] is False
    assert "refresh reachable live canary preflight report" in decision["required_before_durable_mvp"]

    blocked = mvp_decision.build_mvp_decision_contract(
        contract_summary,
        executor_summary,
        {
            "status": "failed",
            "release_boundary_version": "section_59_v2",
            "durable_authoring_enabled": False,
        },
    )
    assert blocked["decision_status"] == "mvp_decision_blocked"
    assert blocked["temporary_blueprint_authoring_mvp_ready"] is False

    print("BP authoring durable MVP decision contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
