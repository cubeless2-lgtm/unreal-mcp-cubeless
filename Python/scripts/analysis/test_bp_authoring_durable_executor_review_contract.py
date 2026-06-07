#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_executor_review_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_review_contract as executor_review  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def main() -> int:
    manifests = [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]
    executor_summary = manifest_executor.summarize_executor_policies(
        manifests,
        job_contract.DEFAULT_TEMP_PACKAGE_PATH,
    )
    contract = executor_review.build_executor_review_contract(True, executor_summary)
    assert contract["schema"] == executor_review.EXECUTOR_REVIEW_SCHEMA
    assert contract["requested"] is True
    assert contract["review_check_count"] == len(executor_review.REVIEW_CHECK_IDS)
    assert {check["id"] for check in contract["review_checks"]} == set(executor_review.REVIEW_CHECK_IDS)
    assert contract["failing_check_ids"] == []
    assert contract["disabled_executor_boundary_review_passed"] is True
    assert contract["durable_live_implementation_approved"] is False
    assert contract["durable_executor_may_open_after_review"] is False
    assert contract["durable_authoring_allowed"] is False
    assert contract["save_delete_rename_allowed"] is False
    assert contract["canary_execution_allowed"] is False
    assert "section_63_review_does_not_approve_live_durable_executor" in contract["blocked_by"]

    summary = executor_review.summarize_executor_review_contracts([contract])
    assert summary == {
        "schema": executor_review.EXECUTOR_REVIEW_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_executor_review_count": 1,
        "review_check_count": len(executor_review.REVIEW_CHECK_IDS),
        "disabled_executor_boundary_review_passed_count": 1,
        "durable_live_implementation_approved_count": 0,
        "durable_executor_may_open_after_review_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "canary_execution_allowed_count": 0,
        "failing_check_count": 0,
    }

    print("BP authoring durable executor review contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
