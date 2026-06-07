#!/usr/bin/env python
"""
Section 69 durable live canary rehearsal readiness contract.

This contract reviews whether a live canary rehearsal may run. Current policy
keeps the rehearsal closed because fresh bridge/live evidence, marker proof,
cleanup proof, and save readiness are not satisfied.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_REHEARSAL_READINESS_SCHEMA = "section_69_durable_canary_rehearsal_readiness_contract_v1"
CANARY_REHEARSAL_READINESS_SUMMARY_SCHEMA = "section_69_durable_canary_rehearsal_readiness_summary_v1"


def build_canary_rehearsal_readiness_contract(
    requested: bool,
    bridge_refresh_summary: Dict[str, Any],
    live_evidence_summary: Dict[str, Any],
    marker_proof_summary: Dict[str, Any],
    cleanup_proof_summary: Dict[str, Any],
    save_review_summary: Dict[str, Any],
) -> Dict[str, Any]:
    missing = []
    if requested:
        if bridge_refresh_summary.get("bridge_refresh_satisfied_count") != 1:
            missing.append("bridge_refresh_satisfied")
        if live_evidence_summary.get("live_evidence_refresh_satisfied_count") != 1:
            missing.append("live_evidence_refresh_satisfied")
        if marker_proof_summary.get("write_readback_proof_satisfied_count") != 1:
            missing.append("ownership_marker_write_readback")
        if cleanup_proof_summary.get("cleanup_proof_satisfied_count") != 1:
            missing.append("rollback_cleanup_proof")
        if save_review_summary.get("durable_save_enable_ready_count") != 1:
            missing.append("durable_save_enable_ready")
    readiness_review_complete = bool(
        requested
        and bridge_refresh_summary.get("status") == "passed"
        and live_evidence_summary.get("status") == "passed"
        and marker_proof_summary.get("status") == "passed"
        and cleanup_proof_summary.get("status") == "passed"
        and save_review_summary.get("status") == "passed"
    )
    return {
        "id": "durable_live_canary_rehearsal_readiness",
        "schema": CANARY_REHEARSAL_READINESS_SCHEMA,
        "requested": requested,
        "rehearsal_readiness_review_complete": readiness_review_complete,
        "missing_rehearsal_prerequisites": missing,
        "missing_rehearsal_prerequisite_count": len(missing),
        "live_canary_rehearsal_ready": False,
        "live_canary_rehearsal_attempted": False,
        "canary_creation_attempted": False,
        "canary_save_attempted": False,
        "canary_cleanup_attempted": False,
        "durable_executor_may_open_for_rehearsal": False,
        "live_creation_command_count": 0,
        "live_save_command_count": 0,
        "live_cleanup_command_count": 0,
        "blocked_by": []
        if not requested
        else [
            "section_69_rehearsal_readiness_not_satisfied",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "refresh bridge and read-only canary live evidence before rehearsal",
            "prove marker write/readback and cleanup boundaries before rehearsal",
            "keep save/delete/rename disabled unless Section 68 durable save review becomes ready",
        ],
    }


def summarize_canary_rehearsal_readiness_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("rehearsal_readiness_review_complete")) == len(requested)
            and sum(1 for contract in requested if contract.get("live_canary_rehearsal_ready")) == 0
            and sum(1 for contract in requested if contract.get("live_canary_rehearsal_attempted")) == 0
            and sum(1 for contract in requested if contract.get("canary_creation_attempted")) == 0
            and sum(1 for contract in requested if contract.get("canary_save_attempted")) == 0
            and sum(1 for contract in requested if contract.get("canary_cleanup_attempted")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_for_rehearsal")) == 0
            and sum(contract.get("live_creation_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_save_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_cleanup_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": CANARY_REHEARSAL_READINESS_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_rehearsal_readiness_count": len(requested),
        "rehearsal_readiness_review_complete_count": sum(
            1 for contract in requested if contract.get("rehearsal_readiness_review_complete")
        ),
        "missing_rehearsal_prerequisite_count": sum(
            contract.get("missing_rehearsal_prerequisite_count", 0) for contract in requested
        ),
        "live_canary_rehearsal_ready_count": sum(
            1 for contract in requested if contract.get("live_canary_rehearsal_ready")
        ),
        "live_canary_rehearsal_attempted_count": sum(
            1 for contract in requested if contract.get("live_canary_rehearsal_attempted")
        ),
        "canary_creation_attempted_count": sum(1 for contract in requested if contract.get("canary_creation_attempted")),
        "canary_save_attempted_count": sum(1 for contract in requested if contract.get("canary_save_attempted")),
        "canary_cleanup_attempted_count": sum(1 for contract in requested if contract.get("canary_cleanup_attempted")),
        "durable_executor_may_open_for_rehearsal_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_for_rehearsal")
        ),
        "live_creation_command_count": sum(contract.get("live_creation_command_count", 0) for contract in requested),
        "live_save_command_count": sum(contract.get("live_save_command_count", 0) for contract in requested),
        "live_cleanup_command_count": sum(contract.get("live_cleanup_command_count", 0) for contract in requested),
    }
