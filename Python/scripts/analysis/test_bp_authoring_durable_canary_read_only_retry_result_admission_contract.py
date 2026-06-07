#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_read_only_retry_result_admission_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_bridge_recovery_readiness_contract as bridge_recovery  # noqa: E402
import bp_authoring_durable_canary_command_allowlist_contract as command_allowlist  # noqa: E402
import bp_authoring_durable_canary_read_only_retry_envelope_contract as retry_envelope  # noqa: E402
import bp_authoring_durable_canary_read_only_retry_result_admission_contract as result_admission  # noqa: E402
import bp_authoring_job_contract as job_contract  # noqa: E402
import bp_authoring_manifest_executor as manifest_executor  # noqa: E402


def build_retry_envelope_summary() -> dict:
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
    allowlist = command_allowlist.build_canary_command_allowlist_contract(True, executor_summary)
    envelope = retry_envelope.build_canary_read_only_retry_envelope_contract(
        True,
        bridge_recovery.summarize_bridge_recovery_readiness_contracts([recovery]),
        contract_summary["durable_canary_live_preflight_summary"],
        command_allowlist.summarize_canary_command_allowlist_contracts([allowlist]),
    )
    return retry_envelope.summarize_canary_read_only_retry_envelopes([envelope])


def build_read_only_result(**overrides: object) -> dict:
    result = {
        "schema": result_admission.CANARY_READ_ONLY_RETRY_RESULT_SCHEMA,
        "command": result_admission.READ_ONLY_RESULT_COMMAND,
        "status": "passed",
        "read_only": True,
        "asset_exists_check_performed": True,
        "explicit_live_read_only_retry_authorized": True,
        "authoring_attempted": False,
        "save_or_delete_attempted": False,
        "save_asset_attempted": False,
        "delete_asset_attempted": False,
        "rename_asset_attempted": False,
        "cleanup_attempted": False,
        "canary_execution_attempted": False,
        "durable_authoring_attempted": False,
    }
    result.update(overrides)
    return result


def main() -> int:
    envelope_summary = build_retry_envelope_summary()
    missing_result_contract = result_admission.build_canary_read_only_retry_result_admission_contract(
        True,
        envelope_summary,
    )
    assert missing_result_contract["schema"] == result_admission.CANARY_READ_ONLY_RETRY_RESULT_ADMISSION_SCHEMA
    assert missing_result_contract["requested"] is True
    assert missing_result_contract["retry_result_admission_contract_defined"] is True
    assert missing_result_contract["live_read_only_retry_result_present"] is False
    assert missing_result_contract["explicit_live_read_only_retry_authorized"] is False
    assert missing_result_contract["read_only_result_admitted"] is False
    assert missing_result_contract["missing_admission_prerequisite_count"] == 2
    assert "live_read_only_retry_result_missing" in missing_result_contract["missing_admission_prerequisites"]
    assert (
        "explicit_live_read_only_retry_authorization_missing"
        in missing_result_contract["missing_admission_prerequisites"]
    )
    assert missing_result_contract["retry_result_rejected"] is False
    assert missing_result_contract["unsafe_retry_result_count"] == 0
    assert missing_result_contract["canary_execution_allowed_after_retry_result"] is False
    assert missing_result_contract["durable_executor_may_open_after_retry_result"] is False
    assert missing_result_contract["authoring_command_allowed"] is False
    assert missing_result_contract["save_delete_rename_allowed"] is False
    assert missing_result_contract["cleanup_allowed"] is False

    missing_summary = result_admission.summarize_canary_read_only_retry_result_admissions(
        [missing_result_contract]
    )
    assert missing_summary == {
        "schema": result_admission.CANARY_READ_ONLY_RETRY_RESULT_ADMISSION_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_read_only_retry_result_admission_count": 1,
        "retry_result_admission_contract_defined_count": 1,
        "live_read_only_retry_result_present_count": 0,
        "result_schema_matches_count": 0,
        "explicit_live_read_only_retry_authorized_count": 0,
        "read_only_command_matches_count": 0,
        "result_status_passed_count": 0,
        "read_only_result_count": 0,
        "asset_exists_check_performed_count": 0,
        "read_only_result_admitted_count": 0,
        "missing_admission_prerequisite_count": 2,
        "rejected_retry_result_count": 0,
        "unsafe_retry_result_count": 0,
        "canary_execution_allowed_after_retry_result_count": 0,
        "durable_executor_may_open_after_retry_result_count": 0,
        "authoring_command_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_authoring_command_count": 0,
        "live_save_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
        "live_canary_execution_command_count": 0,
    }

    admitted_contract = result_admission.build_canary_read_only_retry_result_admission_contract(
        True,
        envelope_summary,
        build_read_only_result(),
    )
    assert admitted_contract["read_only_result_admitted"] is True
    assert admitted_contract["retry_result_rejected"] is False
    assert admitted_contract["durable_executor_may_open_after_retry_result"] is False
    assert admitted_contract["canary_execution_allowed_after_retry_result"] is False

    unsafe_contract = result_admission.build_canary_read_only_retry_result_admission_contract(
        True,
        envelope_summary,
        build_read_only_result(authoring_attempted=True),
    )
    assert unsafe_contract["read_only_result_admitted"] is False
    assert unsafe_contract["retry_result_rejected"] is True
    assert unsafe_contract["unsafe_retry_result_count"] == 1
    unsafe_summary = result_admission.summarize_canary_read_only_retry_result_admissions([unsafe_contract])
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["rejected_retry_result_count"] == 1
    assert unsafe_summary["unsafe_retry_result_count"] == 1
    assert unsafe_summary["durable_executor_may_open_after_retry_result_count"] == 0

    print("BP authoring durable canary read-only retry result admission contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
