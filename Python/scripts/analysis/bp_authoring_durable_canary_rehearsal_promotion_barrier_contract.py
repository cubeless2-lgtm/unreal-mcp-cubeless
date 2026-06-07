#!/usr/bin/env python
"""
Section 74 durable canary rehearsal promotion barrier contract.

This contract prevents an admitted read-only retry result from becoming live
canary rehearsal or durable authoring execution by itself.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_REHEARSAL_PROMOTION_BARRIER_SCHEMA = (
    "section_74_durable_canary_rehearsal_promotion_barrier_contract_v1"
)
CANARY_REHEARSAL_PROMOTION_BARRIER_SUMMARY_SCHEMA = (
    "section_74_durable_canary_rehearsal_promotion_barrier_summary_v1"
)


def build_canary_rehearsal_promotion_barrier_contract(
    requested: bool,
    retry_result_admission_summary: Dict[str, Any],
    rehearsal_readiness_summary: Dict[str, Any],
    marker_proof_summary: Dict[str, Any],
    cleanup_proof_summary: Dict[str, Any],
    save_review_summary: Dict[str, Any],
    explicit_live_canary_rehearsal_authorization: bool = False,
) -> Dict[str, Any]:
    result_admission_safe = bool(
        retry_result_admission_summary.get("status") == "passed"
        and retry_result_admission_summary.get("unsafe_retry_result_count") == 0
        and retry_result_admission_summary.get("durable_executor_may_open_after_retry_result_count") == 0
    )
    read_only_result_admitted = bool(
        retry_result_admission_summary.get("read_only_result_admitted_count") == 1
    )
    rehearsal_readiness_review_complete = bool(
        rehearsal_readiness_summary.get("status") == "passed"
        and rehearsal_readiness_summary.get("rehearsal_readiness_review_complete_count") == 1
    )
    live_canary_rehearsal_ready = bool(
        rehearsal_readiness_summary.get("live_canary_rehearsal_ready_count") == 1
    )
    marker_write_readback_satisfied = bool(
        marker_proof_summary.get("write_readback_proof_satisfied_count") == 1
    )
    cleanup_proof_satisfied = bool(cleanup_proof_summary.get("cleanup_proof_satisfied_count") == 1)
    durable_save_enable_ready = bool(save_review_summary.get("durable_save_enable_ready_count") == 1)
    promotion_barrier_defined = bool(
        requested
        and result_admission_safe
        and rehearsal_readiness_review_complete
        and marker_proof_summary.get("status") == "passed"
        and cleanup_proof_summary.get("status") == "passed"
        and save_review_summary.get("status") == "passed"
    )
    missing = []
    if requested:
        if not read_only_result_admitted:
            missing.append("read_only_retry_result_admitted")
        if not live_canary_rehearsal_ready:
            missing.append("live_canary_rehearsal_ready")
        if not marker_write_readback_satisfied:
            missing.append("ownership_marker_write_readback")
        if not cleanup_proof_satisfied:
            missing.append("rollback_cleanup_proof")
        if not durable_save_enable_ready:
            missing.append("durable_save_enable_ready")
        if not explicit_live_canary_rehearsal_authorization:
            missing.append("explicit_live_canary_rehearsal_authorization")
        missing.append("separate_durable_rehearsal_execution_release")
    promotion_inputs_satisfied = bool(
        requested
        and promotion_barrier_defined
        and read_only_result_admitted
        and live_canary_rehearsal_ready
        and marker_write_readback_satisfied
        and cleanup_proof_satisfied
        and durable_save_enable_ready
        and explicit_live_canary_rehearsal_authorization
    )
    return {
        "id": "durable_canary_rehearsal_promotion_barrier",
        "schema": CANARY_REHEARSAL_PROMOTION_BARRIER_SCHEMA,
        "requested": requested,
        "promotion_barrier_defined": promotion_barrier_defined,
        "read_only_result_admitted": read_only_result_admitted,
        "rehearsal_readiness_review_complete": rehearsal_readiness_review_complete,
        "promotion_inputs_satisfied": promotion_inputs_satisfied,
        "promotion_execution_release_present": False,
        "missing_promotion_prerequisites": missing,
        "missing_promotion_prerequisite_count": len(missing),
        "canary_rehearsal_promotion_allowed": False,
        "live_canary_rehearsal_allowed": False,
        "live_canary_rehearsal_performed": False,
        "canary_creation_allowed": False,
        "canary_save_allowed": False,
        "canary_cleanup_allowed": False,
        "durable_executor_may_open_after_promotion": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_creation_command_count": 0,
        "live_save_command_count": 0,
        "live_delete_rename_command_count": 0,
        "live_cleanup_command_count": 0,
        "blocked_by": []
        if not requested
        else [
            "section_74_read_only_result_cannot_promote_itself",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "require a separate durable rehearsal execution release before live canary rehearsal",
            "keep read-only retry evidence separate from authoring, save, delete, rename, and cleanup commands",
            "re-check marker, cleanup, save, and rehearsal readiness before any future promotion",
        ],
    }


def summarize_canary_rehearsal_promotion_barriers(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("promotion_barrier_defined")) == len(requested)
            and sum(1 for contract in requested if contract.get("promotion_execution_release_present")) == 0
            and sum(1 for contract in requested if contract.get("canary_rehearsal_promotion_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_canary_rehearsal_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_canary_rehearsal_performed")) == 0
            and sum(1 for contract in requested if contract.get("canary_creation_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_save_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_cleanup_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_after_promotion")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_delete_rename_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            and sum(contract.get("live_creation_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_save_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_delete_rename_command_count", 0) for contract in requested) == 0
            and sum(contract.get("live_cleanup_command_count", 0) for contract in requested) == 0
            else "failed"
        )
    return {
        "schema": CANARY_REHEARSAL_PROMOTION_BARRIER_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_rehearsal_promotion_barrier_count": len(requested),
        "promotion_barrier_defined_count": sum(
            1 for contract in requested if contract.get("promotion_barrier_defined")
        ),
        "read_only_result_admitted_count": sum(
            1 for contract in requested if contract.get("read_only_result_admitted")
        ),
        "rehearsal_readiness_review_complete_count": sum(
            1 for contract in requested if contract.get("rehearsal_readiness_review_complete")
        ),
        "promotion_inputs_satisfied_count": sum(
            1 for contract in requested if contract.get("promotion_inputs_satisfied")
        ),
        "promotion_execution_release_present_count": sum(
            1 for contract in requested if contract.get("promotion_execution_release_present")
        ),
        "missing_promotion_prerequisite_count": sum(
            contract.get("missing_promotion_prerequisite_count", 0) for contract in requested
        ),
        "canary_rehearsal_promotion_allowed_count": sum(
            1 for contract in requested if contract.get("canary_rehearsal_promotion_allowed")
        ),
        "live_canary_rehearsal_allowed_count": sum(
            1 for contract in requested if contract.get("live_canary_rehearsal_allowed")
        ),
        "live_canary_rehearsal_performed_count": sum(
            1 for contract in requested if contract.get("live_canary_rehearsal_performed")
        ),
        "canary_creation_allowed_count": sum(
            1 for contract in requested if contract.get("canary_creation_allowed")
        ),
        "canary_save_allowed_count": sum(1 for contract in requested if contract.get("canary_save_allowed")),
        "canary_cleanup_allowed_count": sum(
            1 for contract in requested if contract.get("canary_cleanup_allowed")
        ),
        "durable_executor_may_open_after_promotion_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_after_promotion")
        ),
        "durable_authoring_allowed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_allowed")
        ),
        "save_delete_rename_allowed_count": sum(
            1 for contract in requested if contract.get("save_delete_rename_allowed")
        ),
        "cleanup_allowed_count": sum(1 for contract in requested if contract.get("cleanup_allowed")),
        "live_creation_command_count": sum(
            contract.get("live_creation_command_count", 0) for contract in requested
        ),
        "live_save_command_count": sum(contract.get("live_save_command_count", 0) for contract in requested),
        "live_delete_rename_command_count": sum(
            contract.get("live_delete_rename_command_count", 0) for contract in requested
        ),
        "live_cleanup_command_count": sum(
            contract.get("live_cleanup_command_count", 0) for contract in requested
        ),
    }
