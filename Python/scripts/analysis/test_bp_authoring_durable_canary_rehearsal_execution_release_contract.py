#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_rehearsal_execution_release_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_rehearsal_execution_release_contract as execution_release  # noqa: E402
import bp_authoring_durable_canary_rehearsal_promotion_barrier_contract as promotion_barrier  # noqa: E402


def build_current_promotion_summary() -> dict:
    return {
        "schema": promotion_barrier.CANARY_REHEARSAL_PROMOTION_BARRIER_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_rehearsal_promotion_barrier_count": 1,
        "promotion_barrier_defined_count": 1,
        "read_only_result_admitted_count": 0,
        "rehearsal_readiness_review_complete_count": 1,
        "promotion_inputs_satisfied_count": 0,
        "promotion_execution_release_present_count": 0,
        "missing_promotion_prerequisite_count": 7,
        "canary_rehearsal_promotion_allowed_count": 0,
        "live_canary_rehearsal_allowed_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_promotion_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_creation_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
    }


def build_release_record(**overrides: object) -> dict:
    record = {
        "schema": execution_release.CANARY_REHEARSAL_EXECUTION_RELEASE_RECORD_SCHEMA,
        "release_scope": execution_release.EXPECTED_RELEASE_SCOPE,
        "explicit_durable_canary_rehearsal_execution_authorized": True,
        "operator_reconfirmed_no_save_delete_rename": True,
        "durable_authoring_authorized": False,
        "save_asset_authorized": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_promotion_summary()
    contract = execution_release.build_canary_rehearsal_execution_release_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == execution_release.CANARY_REHEARSAL_EXECUTION_RELEASE_SCHEMA
    assert contract["requested"] is True
    assert contract["execution_release_contract_defined"] is True
    assert contract["promotion_barrier_defined"] is True
    assert contract["promotion_inputs_satisfied"] is False
    assert contract["release_record_present"] is False
    assert contract["release_record_valid"] is False
    assert contract["release_record_rejected"] is False
    assert contract["unsafe_release_record_count"] == 0
    assert contract["missing_release_prerequisite_count"] == 7
    assert "section_74_promotion_inputs_satisfied" in contract["missing_release_prerequisites"]
    assert "durable_rehearsal_execution_release_record_present" in contract["missing_release_prerequisites"]
    assert "durable_rehearsal_execution_release_record_schema" in contract["missing_release_prerequisites"]
    assert "durable_canary_rehearsal_only_release_scope" in contract["missing_release_prerequisites"]
    assert (
        "explicit_durable_canary_rehearsal_execution_authorization"
        in contract["missing_release_prerequisites"]
    )
    assert "operator_reconfirmed_no_save_delete_rename" in contract["missing_release_prerequisites"]
    assert "separate_live_rehearsal_runner_release" in contract["missing_release_prerequisites"]
    assert contract["live_canary_rehearsal_release_allowed"] is False
    assert contract["live_canary_rehearsal_execution_allowed"] is False
    assert contract["live_canary_rehearsal_performed"] is False
    assert contract["canary_creation_allowed"] is False
    assert contract["canary_save_allowed"] is False
    assert contract["canary_cleanup_allowed"] is False
    assert contract["durable_executor_may_open_after_execution_release"] is False

    summary = execution_release.summarize_canary_rehearsal_execution_releases([contract])
    assert summary == {
        "schema": execution_release.CANARY_REHEARSAL_EXECUTION_RELEASE_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_rehearsal_execution_release_count": 1,
        "execution_release_contract_defined_count": 1,
        "promotion_barrier_defined_count": 1,
        "promotion_inputs_satisfied_count": 0,
        "release_record_present_count": 0,
        "record_schema_matches_count": 0,
        "release_scope_matches_count": 0,
        "explicit_execution_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "release_record_valid_count": 0,
        "release_record_rejected_count": 0,
        "unsafe_release_record_count": 0,
        "missing_release_prerequisite_count": 7,
        "live_canary_rehearsal_release_allowed_count": 0,
        "live_canary_rehearsal_execution_allowed_count": 0,
        "live_canary_rehearsal_performed_count": 0,
        "canary_creation_allowed_count": 0,
        "canary_save_allowed_count": 0,
        "canary_cleanup_allowed_count": 0,
        "durable_executor_may_open_after_execution_release_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_creation_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
    }

    future_summary = {
        **current_summary,
        "promotion_inputs_satisfied_count": 1,
    }
    future_contract = execution_release.build_canary_rehearsal_execution_release_contract(
        True,
        future_summary,
        build_release_record(),
    )
    assert future_contract["release_record_valid"] is True
    assert future_contract["missing_release_prerequisite_count"] == 1
    assert future_contract["missing_release_prerequisites"] == ["separate_live_rehearsal_runner_release"]
    assert future_contract["live_canary_rehearsal_release_allowed"] is False
    assert future_contract["live_canary_rehearsal_execution_allowed"] is False
    assert future_contract["durable_executor_may_open_after_execution_release"] is False

    unsafe_contract = execution_release.build_canary_rehearsal_execution_release_contract(
        True,
        future_summary,
        build_release_record(save_asset_authorized=True),
    )
    assert unsafe_contract["release_record_valid"] is False
    assert unsafe_contract["release_record_rejected"] is True
    assert unsafe_contract["unsafe_release_record_count"] == 1
    unsafe_summary = execution_release.summarize_canary_rehearsal_execution_releases([unsafe_contract])
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["release_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_release_record_count"] == 1
    assert unsafe_summary["durable_executor_may_open_after_execution_release_count"] == 0

    print("BP authoring durable canary rehearsal execution release contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
