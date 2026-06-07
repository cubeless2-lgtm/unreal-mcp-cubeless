#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_command_allowlist_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_command_allowlist_contract as command_allowlist  # noqa: E402
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
    contract = command_allowlist.build_canary_command_allowlist_contract(True, executor_summary)
    assert contract["schema"] == command_allowlist.CANARY_COMMAND_ALLOWLIST_SCHEMA
    assert contract["requested"] is True
    assert contract["allowed_read_only_commands"] == [command_allowlist.READ_ONLY_ASSET_EXISTS_COMMAND]
    assert contract["allowed_read_only_command_count"] == 1
    assert "save_asset" in contract["forbidden_commands"]
    assert "delete_asset" in contract["forbidden_commands"]
    assert "rename_asset" in contract["forbidden_commands"]
    assert contract["forbidden_command_count"] == len(command_allowlist.FORBIDDEN_COMMANDS)
    assert contract["executor_gate_matches_allowlist"] is True
    assert contract["authoring_commands_allowed"] is False
    assert contract["save_commands_allowed"] is False
    assert contract["delete_commands_allowed"] is False
    assert contract["rename_commands_allowed"] is False
    assert contract["cleanup_commands_allowed"] is False
    assert contract["canary_execution_allowed"] is False
    assert contract["durable_executor_may_open_from_allowlist"] is False
    assert "section_64_allowlist_is_read_only_preflight_only" in contract["blocked_by"]

    summary = command_allowlist.summarize_canary_command_allowlist_contracts([contract])
    assert summary == {
        "schema": command_allowlist.CANARY_COMMAND_ALLOWLIST_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_command_allowlist_count": 1,
        "allowed_read_only_command_count": 1,
        "forbidden_command_count": len(command_allowlist.FORBIDDEN_COMMANDS),
        "executor_gate_matches_allowlist_count": 1,
        "authoring_commands_allowed_count": 0,
        "save_commands_allowed_count": 0,
        "delete_commands_allowed_count": 0,
        "rename_commands_allowed_count": 0,
        "cleanup_commands_allowed_count": 0,
        "canary_execution_allowed_count": 0,
        "durable_executor_may_open_from_allowlist_count": 0,
    }

    print("BP authoring durable canary command allowlist contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
