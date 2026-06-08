#!/usr/bin/env python
"""Offline smoke tests for Section 176 activation readiness dry-run contract."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_activation_readiness_dry_run_contract as readiness  # noqa: E402
from bp_authoring_durable_executor_authoring_release_stage_dry_run_test_helper import run_stage_smoke  # noqa: E402


def main() -> int:
    run_stage_smoke(
        readiness,
        readiness.build_durable_executor_authoring_activation_readiness_dry_run_contract,
        readiness.summarize_durable_executor_authoring_activation_readiness_dry_runs,
        "durable_executor_open_contract_started",
    )
    print("BP authoring durable executor authoring activation readiness dry-run contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
