#!/usr/bin/env python
"""
Section 62 durable live evidence refresh contract.

This contract classifies the stored live smoke report as durable-canary evidence
or as a stale/missing refresh. It is intentionally report-only and never opens
durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


LIVE_EVIDENCE_REFRESH_SCHEMA = "section_62_durable_live_evidence_refresh_contract_v1"
LIVE_EVIDENCE_REFRESH_SUMMARY_SCHEMA = "section_62_durable_live_evidence_refresh_summary_v1"


def build_live_evidence_refresh_contract(
    requested: bool,
    planner_report: Dict[str, Any] | None,
) -> Dict[str, Any]:
    planner_report = planner_report or {}
    live_gate = planner_report.get("live_gate", {})
    canary_gate = live_gate.get("durable_canary_live_preflight_gate", {})
    canary_gate_status = canary_gate.get("status", "")
    authoring_attempted = int(canary_gate.get("authoring_attempted_count") or 0)
    save_or_delete_attempted = int(canary_gate.get("save_or_delete_attempted_count") or 0)
    cleanup_attempted = int(canary_gate.get("cleanup_attempted_count") or 0)
    canary_execution_attempted = int(canary_gate.get("canary_execution_attempted_count") or 0)
    read_only_result_refreshed = bool(
        canary_gate_status == "passed"
        and canary_gate.get("live_requested") is True
        and canary_gate.get("live_result_count") == canary_gate.get("read_only_live_preflight_allowed_count") == 1
        and canary_gate.get("passed_read_only_result_count") == 1
        and authoring_attempted == 0
        and save_or_delete_attempted == 0
        and cleanup_attempted == 0
        and canary_execution_attempted == 0
        and canary_gate.get("read_only_only") is True
    )
    unsafe_attempt_count = authoring_attempted + save_or_delete_attempted + cleanup_attempted + canary_execution_attempted
    blocked_by: list[str] = []
    if requested:
        if not planner_report:
            blocked_by.append("planner_live_report_missing")
        if not canary_gate:
            blocked_by.append("durable_canary_live_evidence_missing")
        if canary_gate and not read_only_result_refreshed:
            blocked_by.append("durable_canary_live_evidence_not_read_only_refreshed")
        blocked_by.append("section_62_live_evidence_refresh_blocks_durable_execution")

    return {
        "id": "durable_live_evidence_refresh",
        "schema": LIVE_EVIDENCE_REFRESH_SCHEMA,
        "requested": requested,
        "planner_live_report_present": bool(planner_report),
        "planner_live_report_status": planner_report.get("verdict", {}).get("status", ""),
        "canary_live_evidence_present": bool(canary_gate),
        "canary_live_evidence_status": canary_gate_status,
        "live_evidence_refresh_required": requested,
        "read_only_result_refreshed": read_only_result_refreshed,
        "live_evidence_refresh_satisfied": bool(requested and read_only_result_refreshed),
        "authoring_attempted_count": authoring_attempted,
        "save_or_delete_attempted_count": save_or_delete_attempted,
        "cleanup_attempted_count": cleanup_attempted,
        "canary_execution_attempted_count": canary_execution_attempted,
        "unsafe_live_attempt_count": unsafe_attempt_count,
        "durable_executor_may_open_after_report_refresh": False,
        "durable_authoring_allowed": False,
        "save_or_delete_allowed": False,
        "cleanup_allowed": False,
        "blocked_by": sorted(set(blocked_by)),
        "required_reinforcement": []
        if not requested
        else [
            "regenerate PlannerDrivenSmoke with Section 57 canary read-only preflight evidence",
            "treat missing or stale canary evidence as executor-closed",
            "keep durable save/delete/cleanup disabled after report refresh",
        ],
    }


def summarize_live_evidence_refresh_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    unsafe_count = sum(contract.get("unsafe_live_attempt_count", 0) for contract in requested)
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if unsafe_count == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_after_report_refresh")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_or_delete_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            else "failed"
        )
    return {
        "schema": LIVE_EVIDENCE_REFRESH_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_live_evidence_refresh_count": len(requested),
        "planner_live_report_present_count": sum(
            1 for contract in requested if contract.get("planner_live_report_present")
        ),
        "canary_live_evidence_present_count": sum(
            1 for contract in requested if contract.get("canary_live_evidence_present")
        ),
        "live_evidence_refresh_required_count": sum(
            1 for contract in requested if contract.get("live_evidence_refresh_required")
        ),
        "read_only_result_refreshed_count": sum(
            1 for contract in requested if contract.get("read_only_result_refreshed")
        ),
        "live_evidence_refresh_satisfied_count": sum(
            1 for contract in requested if contract.get("live_evidence_refresh_satisfied")
        ),
        "unsafe_live_attempt_count": unsafe_count,
        "durable_executor_may_open_after_report_refresh_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_after_report_refresh")
        ),
        "durable_authoring_allowed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_allowed")
        ),
        "save_or_delete_allowed_count": sum(1 for contract in requested if contract.get("save_or_delete_allowed")),
        "cleanup_allowed_count": sum(1 for contract in requested if contract.get("cleanup_allowed")),
    }
