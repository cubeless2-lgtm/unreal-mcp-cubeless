#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_authoring_enable_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_authoring_enable_contract as authoring_enable  # noqa: E402
import bp_authoring_durable_canary_executor_open_contract as executor_open  # noqa: E402


def build_current_open_summary() -> dict:
    return {
        "schema": executor_open.CANARY_DURABLE_EXECUTOR_OPEN_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_executor_open_count": 1,
        "open_contract_defined_count": 1,
        "activation_contract_ready_count": 1,
        "activation_inputs_satisfied_count": 0,
        "activation_record_valid_count": 0,
        "open_inputs_satisfied_count": 0,
        "open_record_present_count": 0,
        "record_schema_matches_count": 0,
        "open_scope_matches_count": 0,
        "explicit_open_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "open_record_valid_count": 0,
        "open_record_rejected_count": 0,
        "unsafe_open_record_count": 0,
        "missing_open_prerequisite_count": 8,
        "durable_executor_open_allowed_count": 0,
        "durable_executor_opened_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
    }


def build_enable_record(**overrides: object) -> dict:
    record = {
        "schema": authoring_enable.CANARY_DURABLE_AUTHORING_ENABLE_RECORD_SCHEMA,
        "enable_scope": authoring_enable.EXPECTED_ENABLE_SCOPE,
        "explicit_durable_authoring_enable_authorized": True,
        "operator_reconfirmed_no_save_delete_rename": True,
        "target_package_allowlist_reconfirmed": True,
        "overwrite_rename_decision_reconfirmed": True,
        "rollback_readiness_reconfirmed": True,
        "executor_created_ownership_marker_reconfirmed": True,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "durable_executor_activation_authorized": False,
        "durable_executor_open_authorized": False,
        "durable_executor_open_performed": False,
        "durable_executor_opened": False,
        "durable_authoring_command_authorized": False,
        "save_asset_authorized": False,
        "delete_asset_authorized": False,
        "rename_asset_authorized": False,
        "cleanup_authorized": False,
        "live_command_dispatch_authorized": False,
        "live_command_execution_authorized": False,
    }
    record.update(overrides)
    return record


def main() -> int:
    current_summary = build_current_open_summary()
    contract = authoring_enable.build_canary_durable_authoring_enable_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == authoring_enable.CANARY_DURABLE_AUTHORING_ENABLE_SCHEMA
    assert contract["requested"] is True
    assert contract["authoring_enable_contract_defined"] is True
    assert contract["executor_open_contract_ready"] is True
    assert contract["open_inputs_satisfied"] is False
    assert contract["open_record_valid"] is False
    assert contract["authoring_enable_inputs_satisfied"] is False
    assert contract["authoring_enable_record_present"] is False
    assert contract["record_schema_matches"] is False
    assert contract["enable_scope_matches"] is False
    assert contract["explicit_authoring_enable_authorized"] is False
    assert contract["no_save_delete_rename_acknowledged"] is False
    assert contract["target_package_allowlist_reconfirmed"] is False
    assert contract["overwrite_rename_decision_reconfirmed"] is False
    assert contract["rollback_readiness_reconfirmed"] is False
    assert contract["ownership_marker_reconfirmed"] is False
    assert contract["authoring_enable_record_valid"] is False
    assert contract["authoring_enable_record_rejected"] is False
    assert contract["unsafe_authoring_enable_record_count"] == 0
    assert contract["missing_authoring_enable_prerequisite_count"] == 12
    assert "section_83_open_inputs_satisfied" in contract["missing_authoring_enable_prerequisites"]
    assert "section_83_open_record_valid" in contract["missing_authoring_enable_prerequisites"]
    assert "durable_authoring_enable_record_present" in contract["missing_authoring_enable_prerequisites"]
    assert "durable_authoring_enable_record_schema" in contract["missing_authoring_enable_prerequisites"]
    assert "durable_canary_authoring_enable_only_scope" in contract["missing_authoring_enable_prerequisites"]
    assert "explicit_durable_authoring_enable_authorization" in contract["missing_authoring_enable_prerequisites"]
    assert "operator_reconfirmed_no_save_delete_rename" in contract["missing_authoring_enable_prerequisites"]
    assert "section_51_target_package_allowlist_reconfirmed" in contract["missing_authoring_enable_prerequisites"]
    assert "section_51_overwrite_rename_decision_reconfirmed" in contract["missing_authoring_enable_prerequisites"]
    assert "section_51_rollback_readiness_reconfirmed" in contract["missing_authoring_enable_prerequisites"]
    assert "section_51_executor_created_ownership_marker_reconfirmed" in contract["missing_authoring_enable_prerequisites"]
    assert "separate_durable_authoring_command_contract" in contract["missing_authoring_enable_prerequisites"]
    assert contract["durable_authoring_enable_allowed"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["durable_authoring_allowed"] is False

    summary = authoring_enable.summarize_canary_durable_authoring_enables([contract])
    assert summary == {
        "schema": authoring_enable.CANARY_DURABLE_AUTHORING_ENABLE_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_authoring_enable_count": 1,
        "authoring_enable_contract_defined_count": 1,
        "executor_open_contract_ready_count": 1,
        "open_inputs_satisfied_count": 0,
        "open_record_valid_count": 0,
        "authoring_enable_inputs_satisfied_count": 0,
        "authoring_enable_record_present_count": 0,
        "record_schema_matches_count": 0,
        "enable_scope_matches_count": 0,
        "explicit_authoring_enable_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "target_package_allowlist_reconfirmed_count": 0,
        "overwrite_rename_decision_reconfirmed_count": 0,
        "rollback_readiness_reconfirmed_count": 0,
        "ownership_marker_reconfirmed_count": 0,
        "authoring_enable_record_valid_count": 0,
        "authoring_enable_record_rejected_count": 0,
        "unsafe_authoring_enable_record_count": 0,
        "missing_authoring_enable_prerequisite_count": 12,
        "durable_authoring_enable_allowed_count": 0,
        "durable_authoring_enabled_count": 0,
        "durable_authoring_allowed_count": 0,
        "save_delete_rename_allowed_count": 0,
        "cleanup_allowed_count": 0,
        "live_command_dispatch_allowed_count": 0,
        "live_command_plan_emitted_count": 0,
        "live_command_execution_allowed_count": 0,
        "live_command_executed_count": 0,
        "reported_allowed_evidence_command_count": 0,
        "reported_forbidden_evidence_command_count": 0,
    }

    future_summary = {
        **current_summary,
        "open_inputs_satisfied_count": 1,
        "open_record_present_count": 1,
        "record_schema_matches_count": 1,
        "open_scope_matches_count": 1,
        "explicit_open_authorized_count": 1,
        "no_save_delete_rename_acknowledged_count": 1,
        "open_record_valid_count": 1,
        "reported_allowed_evidence_command_count": 4,
    }
    future_contract = authoring_enable.build_canary_durable_authoring_enable_contract(
        True,
        future_summary,
        build_enable_record(),
    )
    assert future_contract["authoring_enable_record_valid"] is True
    assert future_contract["missing_authoring_enable_prerequisite_count"] == 1
    assert future_contract["missing_authoring_enable_prerequisites"] == [
        "separate_durable_authoring_command_contract"
    ]
    assert future_contract["durable_authoring_enable_allowed"] is False
    assert future_contract["durable_authoring_enabled"] is False
    assert future_contract["durable_authoring_allowed"] is False
    assert future_contract["reported_allowed_evidence_command_count"] == 4

    unsafe_contract = authoring_enable.build_canary_durable_authoring_enable_contract(
        True,
        future_summary,
        build_enable_record(durable_authoring_enabled=True),
    )
    assert unsafe_contract["authoring_enable_record_valid"] is False
    assert unsafe_contract["authoring_enable_record_rejected"] is True
    assert unsafe_contract["unsafe_authoring_enable_record_count"] == 1
    unsafe_summary = authoring_enable.summarize_canary_durable_authoring_enables([unsafe_contract])
    assert unsafe_summary["status"] == "failed"
    assert unsafe_summary["authoring_enable_record_rejected_count"] == 1
    assert unsafe_summary["unsafe_authoring_enable_record_count"] == 1
    assert unsafe_summary["durable_authoring_enabled_count"] == 0
    assert unsafe_summary["durable_authoring_allowed_count"] == 0

    print("BP authoring durable canary authoring enable contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
