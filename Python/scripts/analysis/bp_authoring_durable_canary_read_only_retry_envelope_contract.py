#!/usr/bin/env python
"""
Section 72 durable canary read-only retry envelope contract.

This contract defines the envelope for a future read-only canary retry after
bridge recovery readiness. It does not perform the retry and does not open
durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_READ_ONLY_RETRY_ENVELOPE_SCHEMA = "section_72_durable_canary_read_only_retry_envelope_contract_v1"
CANARY_READ_ONLY_RETRY_ENVELOPE_SUMMARY_SCHEMA = "section_72_durable_canary_read_only_retry_envelope_summary_v1"
READ_ONLY_ASSET_EXISTS_COMMAND = "unreal.EditorAssetLibrary.does_asset_exist"


def build_canary_read_only_retry_envelope_contract(
    requested: bool,
    bridge_recovery_summary: Dict[str, Any],
    canary_live_preflight_summary: Dict[str, Any],
    command_allowlist_summary: Dict[str, Any],
) -> Dict[str, Any]:
    envelope_defined = bool(
        requested
        and bridge_recovery_summary.get("status") == "passed"
        and bridge_recovery_summary.get("local_recovery_inputs_ready_count") == 1
        and canary_live_preflight_summary.get("status") == "passed"
        and canary_live_preflight_summary.get("read_only_live_preflight_allowed_count") == 1
        and command_allowlist_summary.get("status") == "passed"
        and command_allowlist_summary.get("allowed_read_only_command_count") == 1
    )
    missing = []
    if requested:
        if bridge_recovery_summary.get("bridge_reachable_count") != 1:
            missing.append("bridge_socket_reachable")
        if bridge_recovery_summary.get("read_only_canary_retry_allowed_after_recovery_count") != 1:
            missing.append("explicit_live_read_only_retry_authorization")
    return {
        "id": "durable_canary_read_only_retry_envelope",
        "schema": CANARY_READ_ONLY_RETRY_ENVELOPE_SCHEMA,
        "requested": requested,
        "read_only_retry_envelope_defined": envelope_defined,
        "read_only_command": READ_ONLY_ASSET_EXISTS_COMMAND if requested else "",
        "read_only_command_count": 1 if requested else 0,
        "missing_retry_prerequisites": missing,
        "missing_retry_prerequisite_count": len(missing),
        "read_only_retry_prerequisites_satisfied": False,
        "live_read_only_retry_allowed": False,
        "live_read_only_retry_performed": False,
        "live_read_only_result_recorded": False,
        "canary_execution_allowed_after_retry": False,
        "durable_executor_may_open_after_retry": False,
        "authoring_command_allowed": False,
        "save_or_delete_allowed": False,
        "cleanup_allowed": False,
        "live_authoring_command_count": 0,
        "live_save_or_delete_command_count": 0,
        "live_cleanup_command_count": 0,
        "blocked_by": []
        if not requested
        else [
            "section_72_retry_envelope_does_not_perform_live_retry",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "perform a separate explicit live read-only retry only after bridge reachability is confirmed",
            "record the read-only asset-exists result before any later canary rehearsal",
            "keep durable create/save/delete/rename/cleanup disabled after read-only retry",
        ],
    }


def summarize_canary_read_only_retry_envelopes(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("read_only_retry_envelope_defined")) == len(requested)
            and sum(1 for contract in requested if contract.get("read_only_retry_prerequisites_satisfied")) == 0
            and sum(1 for contract in requested if contract.get("live_read_only_retry_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_read_only_retry_performed")) == 0
            and sum(1 for contract in requested if contract.get("live_read_only_result_recorded")) == 0
            and sum(1 for contract in requested if contract.get("canary_execution_allowed_after_retry")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_after_retry")) == 0
            and sum(1 for contract in requested if contract.get("authoring_command_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_or_delete_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            and sum(contract.get("live_authoring_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_save_or_delete_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_cleanup_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": CANARY_READ_ONLY_RETRY_ENVELOPE_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_read_only_retry_envelope_count": len(requested),
        "read_only_retry_envelope_defined_count": sum(
            1 for contract in requested if contract.get("read_only_retry_envelope_defined")
        ),
        "read_only_command_count": sum(contract.get("read_only_command_count", 0) for contract in requested),
        "missing_retry_prerequisite_count": sum(
            contract.get("missing_retry_prerequisite_count", 0) for contract in requested
        ),
        "read_only_retry_prerequisites_satisfied_count": sum(
            1 for contract in requested if contract.get("read_only_retry_prerequisites_satisfied")
        ),
        "live_read_only_retry_allowed_count": sum(
            1 for contract in requested if contract.get("live_read_only_retry_allowed")
        ),
        "live_read_only_retry_performed_count": sum(
            1 for contract in requested if contract.get("live_read_only_retry_performed")
        ),
        "live_read_only_result_recorded_count": sum(
            1 for contract in requested if contract.get("live_read_only_result_recorded")
        ),
        "canary_execution_allowed_after_retry_count": sum(
            1 for contract in requested if contract.get("canary_execution_allowed_after_retry")
        ),
        "durable_executor_may_open_after_retry_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_after_retry")
        ),
        "authoring_command_allowed_count": sum(1 for contract in requested if contract.get("authoring_command_allowed")),
        "save_or_delete_allowed_count": sum(1 for contract in requested if contract.get("save_or_delete_allowed")),
        "cleanup_allowed_count": sum(1 for contract in requested if contract.get("cleanup_allowed")),
        "live_authoring_command_count": sum(contract.get("live_authoring_command_count", 0) for contract in requested),
        "live_save_or_delete_command_count": sum(
            contract.get("live_save_or_delete_command_count", 0) for contract in requested
        ),
        "live_cleanup_command_count": sum(contract.get("live_cleanup_command_count", 0) for contract in requested),
    }
