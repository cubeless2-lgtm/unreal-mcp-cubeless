#!/usr/bin/env python
"""Offline smoke tests for Section 179 command path dry-run contract."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_command_path_dry_run_contract as command_path  # noqa: E402
from bp_authoring_durable_executor_authoring_release_stage_dry_run_test_helper import run_stage_smoke  # noqa: E402


def main() -> int:
    run_stage_smoke(
        command_path,
        command_path.build_durable_executor_authoring_command_path_dry_run_contract,
        command_path.summarize_durable_executor_authoring_command_path_dry_runs,
        "durable_executor_command_path_opened",
    )
    print("BP authoring durable executor authoring command path dry-run contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
