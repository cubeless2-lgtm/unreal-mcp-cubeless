#!/usr/bin/env python
"""
Section 67 durable rollback cleanup proof contract.

Recovery scenarios are defined, but cleanup/delete proof is not satisfied until
an executor-created ownership marker has been written and read back.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


ROLLBACK_CLEANUP_PROOF_SCHEMA = "section_67_durable_rollback_cleanup_proof_contract_v1"
ROLLBACK_CLEANUP_PROOF_SUMMARY_SCHEMA = "section_67_durable_rollback_cleanup_proof_summary_v1"


def build_rollback_cleanup_proof_contract(
    requested: bool,
    contract_summary: Dict[str, Any],
    marker_proof_contract: Dict[str, Any],
) -> Dict[str, Any]:
    recovery_ready = bool(contract_summary.get("durable_canary_recovery_matrix_ready_count") == 1)
    marker_proof_satisfied = bool(marker_proof_contract.get("write_readback_proof_satisfied"))
    cleanup_proof_required = bool(requested and recovery_ready)
    return {
        "id": "durable_rollback_cleanup_proof",
        "schema": ROLLBACK_CLEANUP_PROOF_SCHEMA,
        "requested": requested,
        "recovery_matrix_ready": recovery_ready,
        "cleanup_proof_required": cleanup_proof_required,
        "ownership_marker_write_readback_satisfied": marker_proof_satisfied,
        "cleanup_proof_satisfied": False,
        "cleanup_allowed": False,
        "delete_allowed": False,
        "delete_preexisting_asset_allowed": False,
        "delete_without_marker_allowed": False,
        "durable_executor_may_open_after_cleanup_proof": False,
        "live_cleanup_command_count": 0,
        "live_delete_command_count": 0,
        "blocked_by": []
        if not requested
        else [
            "section_67_cleanup_proof_not_satisfied",
            "ownership_marker_write_readback_proof_missing",
        ],
        "required_reinforcement": []
        if not requested
        else [
            "require Section 66 marker write/readback proof before cleanup",
            "delete only executor-created canary assets with matching marker fields",
            "keep preexisting asset delete forbidden",
        ],
    }


def summarize_rollback_cleanup_proof_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("recovery_matrix_ready")) == len(requested)
            and sum(1 for contract in requested if contract.get("cleanup_proof_satisfied")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            and sum(1 for contract in requested if contract.get("delete_allowed")) == 0
            and sum(1 for contract in requested if contract.get("delete_preexisting_asset_allowed")) == 0
            and sum(1 for contract in requested if contract.get("delete_without_marker_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_after_cleanup_proof")) == 0
            and sum(contract.get("live_cleanup_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_delete_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": ROLLBACK_CLEANUP_PROOF_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_rollback_cleanup_proof_count": len(requested),
        "recovery_matrix_ready_count": sum(1 for contract in requested if contract.get("recovery_matrix_ready")),
        "cleanup_proof_required_count": sum(1 for contract in requested if contract.get("cleanup_proof_required")),
        "ownership_marker_write_readback_satisfied_count": sum(
            1 for contract in requested if contract.get("ownership_marker_write_readback_satisfied")
        ),
        "cleanup_proof_satisfied_count": sum(1 for contract in requested if contract.get("cleanup_proof_satisfied")),
        "cleanup_allowed_count": sum(1 for contract in requested if contract.get("cleanup_allowed")),
        "delete_allowed_count": sum(1 for contract in requested if contract.get("delete_allowed")),
        "delete_preexisting_asset_allowed_count": sum(
            1 for contract in requested if contract.get("delete_preexisting_asset_allowed")
        ),
        "delete_without_marker_allowed_count": sum(
            1 for contract in requested if contract.get("delete_without_marker_allowed")
        ),
        "durable_executor_may_open_after_cleanup_proof_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_after_cleanup_proof")
        ),
        "live_cleanup_command_count": sum(contract.get("live_cleanup_command_count", 0) for contract in requested),
        "live_delete_command_count": sum(contract.get("live_delete_command_count", 0) for contract in requested),
    }
