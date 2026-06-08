#!/usr/bin/env python
"""Offline smoke tests for Section 174 release decision dry-run contract."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_release_decision_dry_run_contract as decision  # noqa: E402
from bp_authoring_durable_executor_authoring_release_stage_dry_run_test_helper import run_stage_smoke  # noqa: E402


def main() -> int:
    run_stage_smoke(
        decision,
        decision.build_durable_executor_authoring_release_decision_dry_run_contract,
        decision.summarize_durable_executor_authoring_release_decision_dry_runs,
        "durable_release_promotion_barrier_started",
    )
    print("BP authoring durable executor authoring release decision dry-run contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
