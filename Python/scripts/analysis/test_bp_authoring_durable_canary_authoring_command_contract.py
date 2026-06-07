#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_durable_canary_authoring_command_contract.py."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_canary_authoring_command_contract as authoring_command  # noqa: E402
import bp_authoring_durable_canary_authoring_enable_contract as authoring_enable  # noqa: E402


def build_current_authoring_enable_summary() -> dict:
    return {
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


def build_command_record(**overrides: object) -> dict:
    record = {
        "schema": authoring_command.CANARY_DURABLE_AUTHORING_COMMAND_RECORD_SCHEMA,
        "command_scope": authoring_command.EXPECTED_COMMAND_SCOPE,
        "explicit_durable_authoring_command_authorized": True,
        "operator_reconfirmed_no_save_delete_rename": True,
        "commands": [
            "create_blueprint_asset",
            "compile_and_validate_blueprint",
            "write_executor_ownership_marker",
            "readback_executor_ownership_marker",
        ],
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "durable_authoring_command_allowed": False,
        "durable_authoring_command_dispatched": False,
        "durable_authoring_command_executed": False,
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
    current_summary = build_current_authoring_enable_summary()
    contract = authoring_command.build_canary_durable_authoring_command_contract(
        True,
        current_summary,
    )
    assert contract["schema"] == authoring_command.CANARY_DURABLE_AUTHORING_COMMAND_SCHEMA
    assert contract["requested"] is True
    assert contract["authoring_command_contract_defined"] is True
    assert contract["authoring_enable_contract_ready"] is True
    assert contract["authoring_enable_inputs_satisfied"] is False
    assert contract["authoring_enable_record_valid"] is False
    assert contract["target_package_allowlist_reconfirmed"] is False
    assert contract["overwrite_rename_decision_reconfirmed"] is False
    assert contract["rollback_readiness_reconfirmed"] is False
    assert contract["ownership_marker_reconfirmed"] is False
    assert contract["authoring_command_inputs_satisfied"] is False
    assert contract["authoring_command_record_present"] is False
    assert contract["record_schema_matches"] is False
    assert contract["command_scope_matches"] is False
    assert contract["explicit_authoring_command_authorized"] is False
    assert contract["no_save_delete_rename_acknowledged"] is False
    assert contract["planned_authoring_command_count"] == 0
    assert contract["allowed_authoring_command_count"] == 0
    assert contract["forbidden_authoring_command_count"] == 0
    assert contract["unknown_authoring_command_count"] == 0
    assert contract["authoring_command_record_valid"] is False
    assert contract["authoring_command_record_rejected"] is False
    assert contract["unsafe_authoring_command_record_count"] == 0
    assert contract["missing_authoring_command_prerequisite_count"] == 13
    assert "section_84_authoring_enable_inputs_satisfied" in contract["missing_authoring_command_prerequisites"]
    assert "section_84_authoring_enable_record_valid" in contract["missing_authoring_command_prerequisites"]
    assert "section_84_target_package_allowlist_reconfirmed" in contract["missing_authoring_command_prerequisites"]
    assert "section_84_overwrite_rename_decision_reconfirmed" in contract["missing_authoring_command_prerequisites"]
    assert "section_84_rollback_readiness_reconfirmed" in contract["missing_authoring_command_prerequisites"]
    assert "section_84_ownership_marker_reconfirmed" in contract["missing_authoring_command_prerequisites"]
    assert "durable_authoring_command_record_present" in contract["missing_authoring_command_prerequisites"]
    assert "durable_authoring_command_record_schema" in contract["missing_authoring_command_prerequisites"]
    assert "durable_canary_authoring_command_only_scope" in contract["missing_authoring_command_prerequisites"]
    assert "explicit_durable_authoring_command_authorization" in contract["missing_authoring_command_prerequisites"]
    assert "operator_reconfirmed_no_save_delete_rename" in contract["missing_authoring_command_prerequisites"]
    assert "durable_authoring_commands_present" in contract["missing_authoring_command_prerequisites"]
    assert "separate_durable_authoring_command_dispatch_contract" in contract["missing_authoring_command_prerequisites"]
    assert contract["durable_authoring_command_allowed"] is False
    assert contract["durable_authoring_command_dispatched"] is False
    assert contract["durable_authoring_command_executed"] is False
    assert contract["durable_authoring_enabled"] is False
    assert contract["durable_authoring_allowed"] is False

    summary = authoring_command.summarize_canary_durable_authoring_commands([contract])
    assert summary == {
        "schema": authoring_command.CANARY_DURABLE_AUTHORING_COMMAND_SUMMARY_SCHEMA,
        "status": "passed",
        "durable_requested_canary_authoring_command_count": 1,
        "authoring_command_contract_defined_count": 1,
        "authoring_enable_contract_ready_count": 1,
        "authoring_enable_inputs_satisfied_count": 0,
        "authoring_enable_record_valid_count": 0,
        "target_package_allowlist_reconfirmed_count": 0,
        "overwrite_rename_decision_reconfirmed_count": 0,
        "rollback_readiness_reconfirmed_count": 0,
        "ownership_marker_reconfirmed_count": 0,
        "authoring_command_inputs_satisfied_count": 0,
        "authoring_command_record_present_count": 0,
        "record_schema_matches_count": 0,
        "command_scope_matches_count": 0,
        "explicit_authoring_command_authorized_count": 0,
        "no_save_delete_rename_acknowledged_count": 0,
        "planned_authoring_command_count": 0,
        "allowed_authoring_command_count": 0,
        "forbidden_authoring_command_count": 0,
        "unknown_authoring_command_count": 0,
        "authoring_command_record_valid_count": 0,
        "authoring_command_record_rejected_count": 0,
        "unsafe_authoring_command_record_count": 0,
        "missing_authoring_command_prerequisite_count": 13,
        "durable_authoring_command_allowed_count": 0,
        "durable_authoring_command_dispatched_count": 0,
        "durable_authoring_command_executed_count": 0,
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
        "authoring_enable_inputs_satisfied_count": 1,
        "authoring_enable_record_present_count": 1,
        "record_schema_matches_count": 1,
        "enable_scope_matches_count": 1,
        "explicit_authoring_enable_authorized_count": 1,
        "no_save_delete_rename_acknowledged_count": 1,
        "target_package_allowlist_reconfirmed_count": 1,
        "overwrite_rename_decision_reconfirmed_count": 1,
        "rollback_readiness_reconfirmed_count": 1,
        "ownership_marker_reconfirmed_count": 1,
        "authoring_enable_record_valid_count": 1,
        "reported_allowed_evidence_command_count": 4,
    }
    future_contract = authoring_command.build_canary_durable_authoring_command_contract(
        True,
        future_summary,
        build_command_record(),
    )
    assert future_contract["authoring_command_record_valid"] is True
    assert future_contract["planned_authoring_command_count"] == 4
    assert future_contract["allowed_authoring_command_count"] == 4
    assert future_contract["missing_authoring_command_prerequisite_count"] == 1
    assert future_contract["missing_authoring_command_prerequisites"] == [
        "separate_durable_authoring_command_dispatch_contract"
    ]
    assert future_contract["durable_authoring_command_allowed"] is False
    assert future_contract["durable_authoring_command_dispatched"] is False
    assert future_contract["durable_authoring_command_executed"] is False
    assert future_contract["durable_authoring_enabled"] is False
    assert future_contract["durable_authoring_allowed"] is False
    assert future_contract["reported_allowed_evidence_command_count"] == 4

    forbidden_contract = authoring_command.build_canary_durable_authoring_command_contract(
        True,
        future_summary,
        build_command_record(commands=["create_blueprint_asset", "save_asset"]),
    )
    assert forbidden_contract["authoring_command_record_valid"] is False
    assert forbidden_contract["authoring_command_record_rejected"] is True
    assert forbidden_contract["forbidden_authoring_command_count"] == 1
    forbidden_summary = authoring_command.summarize_canary_durable_authoring_commands(
        [forbidden_contract]
    )
    assert forbidden_summary["status"] == "failed"
    assert forbidden_summary["authoring_command_record_rejected_count"] == 1
    assert forbidden_summary["forbidden_authoring_command_count"] == 1
    assert forbidden_summary["durable_authoring_command_executed_count"] == 0
    assert forbidden_summary["durable_authoring_allowed_count"] == 0

    print("BP authoring durable canary authoring command contract smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
