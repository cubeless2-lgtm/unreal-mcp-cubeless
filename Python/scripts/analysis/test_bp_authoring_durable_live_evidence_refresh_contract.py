#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_live_evidence_refresh_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_live_evidence_refresh_contract as live_evidence  # noqa: E402


def main() -> int:
    stale_report = {
        "verdict": {"status": "passed"},
        "live_gate": {
            "status": "passed",
            "durable_live_preflight_gate": {"status": "passed"},
        },
    }
    contract = live_evidence.build_live_evidence_refresh_contract(True, stale_report)
    assert contract["schema"] == live_evidence.LIVE_EVIDENCE_REFRESH_SCHEMA
    assert contract["requested"] is True
    assert contract["planner_live_report_present"] is True
    assert contract["planner_live_report_status"] == "passed"
    assert contract["canary_live_evidence_present"] is False
    assert contract["live_evidence_refresh_required"] is True
    assert contract["read_only_result_refreshed"] is False
    assert contract["live_evidence_refresh_satisfied"] is False
    assert contract["unsafe_live_attempt_count"] == 0
    assert contract["durable_executor_may_open_after_report_refresh"] is False
    assert contract["durable_authoring_allowed"] is False
    assert contract["save_or_delete_allowed"] is False
    assert contract["cleanup_allowed"] is False
    assert "durable_canary_live_evidence_missing" in contract["blocked_by"]

    refreshed_report = {
        "verdict": {"status": "passed"},
        "live_gate": {
            "durable_canary_live_preflight_gate": {
                "status": "passed",
                "live_requested": True,
                "live_result_count": 1,
                "read_only_live_preflight_allowed_count": 1,
                "passed_read_only_result_count": 1,
                "authoring_attempted_count": 0,
                "save_or_delete_attempted_count": 0,
                "cleanup_attempted_count": 0,
                "canary_execution_attempted_count": 0,
                "read_only_only": True,
            }
        },
    }
    refreshed = live_evidence.build_live_evidence_refresh_contract(True, refreshed_report)
    assert refreshed["canary_live_evidence_present"] is True
    assert refreshed["read_only_result_refreshed"] is True
    assert refreshed["live_evidence_refresh_satisfied"] is True
    assert refreshed["durable_executor_may_open_after_report_refresh"] is False
    assert refreshed["durable_authoring_allowed"] is False

    summary = live_evidence.summarize_live_evidence_refresh_contracts([contract])
    assert summary == {
        "schema": live_evidence.LIVE_EVIDENCE_REFRESH_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_live_evidence_refresh_count": 1,
        "planner_live_report_present_count": 1,
        "canary_live_evidence_present_count": 0,
        "live_evidence_refresh_required_count": 1,
        "read_only_result_refreshed_count": 0,
        "live_evidence_refresh_satisfied_count": 0,
        "unsafe_live_attempt_count": 0,
        "durable_executor_may_open_after_report_refresh_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_or_delete_allowed_count": 0,
        "cleanup_allowed_count": 0,
    }

    print("BP authoring durable live evidence refresh contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
