#!/usr/bin/env python
"""
Section 66 durable ownership marker write/readback proof contract.

The ownership marker policy is present, but no marker write/readback has been
performed. Cleanup and delete remain closed until that proof exists.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


OWNERSHIP_MARKER_PROOF_SCHEMA = "section_66_durable_ownership_marker_proof_contract_v1"
OWNERSHIP_MARKER_PROOF_SUMMARY_SCHEMA = "section_66_durable_ownership_marker_proof_summary_v1"


def build_ownership_marker_proof_contract(
    requested: bool,
    contract_summary: Dict[str, Any],
) -> Dict[str, Any]:
    policy_ready = bool(contract_summary.get("durable_ownership_marker_policy_ready_count") == 1)
    proof_required = bool(requested and policy_ready)
    return {
        "id": "durable_ownership_marker_write_readback_proof",
        "schema": OWNERSHIP_MARKER_PROOF_SCHEMA,
        "requested": requested,
        "ownership_marker_policy_ready": policy_ready,
        "write_readback_proof_required": proof_required,
        "marker_write_performed": False,
        "marker_readback_verified": False,
        "marker_asset_path_matches_canary": False,
        "marker_run_id_verified": False,
        "write_readback_proof_satisfied": False,
        "cleanup_allowed_after_marker_proof": False,
        "delete_allowed_after_marker_proof": False,
        "durable_executor_may_open_after_marker_proof": False,
        "live_write_command_count": 0,
        "live_readback_command_count": 0,
        "live_delete_command_count": 0,
        "blocked_by": []
        if not requested
        else [
            "section_66_marker_write_readback_proof_not_performed",
            "cleanup_delete_wait_for_verified_executor_created_marker",
        ],
        "required_reinforcement": []
        if not requested
        else [
            "write an executor-created ownership marker only during a future approved canary rehearsal",
            "read back marker fields before cleanup or delete",
            "require marker asset path and run id to match the canary attempt",
        ],
    }


def summarize_ownership_marker_proof_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("ownership_marker_policy_ready")) == len(requested)
            and sum(1 for contract in requested if contract.get("write_readback_proof_satisfied")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed_after_marker_proof")) == 0
            and sum(1 for contract in requested if contract.get("delete_allowed_after_marker_proof")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_after_marker_proof")) == 0
            and sum(contract.get("live_write_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_readback_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_delete_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": OWNERSHIP_MARKER_PROOF_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_ownership_marker_proof_count": len(requested),
        "ownership_marker_policy_ready_count": sum(
            1 for contract in requested if contract.get("ownership_marker_policy_ready")
        ),
        "write_readback_proof_required_count": sum(
            1 for contract in requested if contract.get("write_readback_proof_required")
        ),
        "marker_write_performed_count": sum(1 for contract in requested if contract.get("marker_write_performed")),
        "marker_readback_verified_count": sum(
            1 for contract in requested if contract.get("marker_readback_verified")
        ),
        "write_readback_proof_satisfied_count": sum(
            1 for contract in requested if contract.get("write_readback_proof_satisfied")
        ),
        "cleanup_allowed_after_marker_proof_count": sum(
            1 for contract in requested if contract.get("cleanup_allowed_after_marker_proof")
        ),
        "delete_allowed_after_marker_proof_count": sum(
            1 for contract in requested if contract.get("delete_allowed_after_marker_proof")
        ),
        "durable_executor_may_open_after_marker_proof_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_after_marker_proof")
        ),
        "live_write_command_count": sum(contract.get("live_write_command_count", 0) for contract in requested),
        "live_readback_command_count": sum(contract.get("live_readback_command_count", 0) for contract in requested),
        "live_delete_command_count": sum(contract.get("live_delete_command_count", 0) for contract in requested),
    }
