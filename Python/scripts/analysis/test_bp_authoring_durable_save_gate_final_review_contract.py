#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_save_gate_final_review_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_save_gate_final_review_contract as save_review  # noqa: E402
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
    contract = save_review.build_save_gate_final_review_contract(
        True,
        contract_summary,
        executor_summary,
    )
    assert contract["schema"] == save_review.SAVE_GATE_FINAL_REVIEW_SCHEMA
    assert contract["requested"] is True
    assert contract["save_gate_final_review_complete"] is True
    assert contract["missing_enable_prerequisite_count"] == 4
    assert "overwrite_or_rename_decision" in contract["missing_enable_prerequisites"]
    assert "rollback_readiness" in contract["missing_enable_prerequisites"]
    assert "save_validation_conditions" in contract["missing_enable_prerequisites"]
    assert "durable_live_preflight_pass" in contract["missing_enable_prerequisites"]
    assert contract["durable_save_enable_ready"] is False
    assert contract["save_true_allowed"] is False
    assert contract["save_asset_allowed"] is False
    assert contract["compile_save_allowed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["durable_executor_may_open_after_save_review"] is False
    assert contract["live_save_command_count"] == 0
    assert contract["live_delete_or_rename_command_count"] == 0

    summary = save_review.summarize_save_gate_final_review_contracts([contract])
    assert summary == {
        "schema": save_review.SAVE_GATE_FINAL_REVIEW_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_save_gate_final_review_count": 1,
        "save_gate_final_review_complete_count": 1,
        "missing_enable_prerequisite_count": 4,
        "durable_save_enable_ready_count": 0,
        "save_true_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "compile_save_allowed_count": 0,
        "delete_asset_allowed_count": 0,
        "rename_asset_allowed_count": 0,
        "durable_executor_may_open_after_save_review_count": 0,
        "live_save_command_count": 0,
        "live_delete_or_rename_command_count": 0,
    }

    print("BP authoring durable save gate final review contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
