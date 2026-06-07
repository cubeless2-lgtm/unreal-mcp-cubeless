#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_read_only_retry_envelope_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_bridge_recovery_readiness_contract as bridge_recovery  # noqa: E402
import bp_authoring_durable_canary_command_allowlist_contract as command_allowlist  # noqa: E402
import bp_authoring_durable_canary_read_only_retry_envelope_contract as retry_envelope  # noqa: E402
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
    recovery = bridge_recovery.build_bridge_recovery_readiness_contract(
        True,
        {
            "mcp_config_present": True,
            "server_defined": True,
            "command": bridge_recovery.EXPECTED_COMMAND,
            "args": [
                "--directory",
                bridge_recovery.EXPECTED_DIRECTORY_ARG,
                "run",
                "--python",
                bridge_recovery.EXPECTED_PYTHON_VERSION,
                bridge_recovery.EXPECTED_SERVER_SCRIPT,
            ],
            "directory_arg": bridge_recovery.EXPECTED_DIRECTORY_ARG,
            "python_version": bridge_recovery.EXPECTED_PYTHON_VERSION,
            "python_dir_exists": True,
            "server_script_exists": True,
            "uv_available": True,
        },
    )
    recovery_summary = bridge_recovery.summarize_bridge_recovery_readiness_contracts([recovery])
    allowlist = command_allowlist.build_canary_command_allowlist_contract(True, executor_summary)
    allowlist_summary = command_allowlist.summarize_canary_command_allowlist_contracts([allowlist])
    contract = retry_envelope.build_canary_read_only_retry_envelope_contract(
        True,
        recovery_summary,
        contract_summary["durable_canary_live_preflight_summary"],
        allowlist_summary,
    )
    assert contract["schema"] == retry_envelope.CANARY_READ_ONLY_RETRY_ENVELOPE_SCHEMA
    assert contract["requested"] is True
    assert contract["read_only_retry_envelope_defined"] is True
    assert contract["read_only_command"] == retry_envelope.READ_ONLY_ASSET_EXISTS_COMMAND
    assert contract["read_only_command_count"] == 1
    assert contract["missing_retry_prerequisite_count"] == 2
    assert "bridge_socket_reachable" in contract["missing_retry_prerequisites"]
    assert "explicit_live_read_only_retry_authorization" in contract["missing_retry_prerequisites"]
    assert contract["read_only_retry_prerequisites_satisfied"] is False
    assert contract["live_read_only_retry_allowed"] is False
    assert contract["live_read_only_retry_performed"] is False
    assert contract["live_read_only_result_recorded"] is False
    assert contract["canary_execution_allowed_after_retry"] is False
    assert contract["durable_executor_may_open_after_retry"] is False
    assert contract["authoring_command_allowed"] is False
    assert contract["save_or_delete_allowed"] is False
    assert contract["cleanup_allowed"] is False
    assert contract["live_authoring_command_count"] == 0
    assert contract["live_save_or_delete_command_count"] == 0
    assert contract["live_cleanup_command_count"] == 0

    summary = retry_envelope.summarize_canary_read_only_retry_envelopes([contract])
    assert summary == {
        "schema": retry_envelope.CANARY_READ_ONLY_RETRY_ENVELOPE_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_read_only_retry_envelope_count": 1,
        "read_only_retry_envelope_defined_count": 1,
        "read_only_command_count": 1,
        "missing_retry_prerequisite_count": 2,
        "read_only_retry_prerequisites_satisfied_count": 0,
        "live_read_only_retry_allowed_count": 0,
        "live_read_only_retry_performed_count": 0,
        "live_read_only_result_recorded_count": 0,
        "canary_execution_allowed_after_retry_count": 0,
        "durable_executor_may_open_after_retry_count": 0,
        "authoring_command_allowed_count": 0,
        "save_or_delete_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_authoring_command_count": 0,
        "live_save_or_delete_command_count": 0,
        "live_cleanup_command_count": 0,
    }

    print("BP authoring durable canary read-only retry envelope contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
