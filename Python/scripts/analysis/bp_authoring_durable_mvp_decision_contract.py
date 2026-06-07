#!/usr/bin/env python
"""
Section 60 Blueprint authoring MVP decision contract.

The decision separates the temporary planner-safe authoring MVP from durable
Blueprint authoring. Durable authoring remains disabled.
"""

from __future__ import annotations

from typing import Any, Dict


MVP_DECISION_SCHEMA = "section_60_bp_authoring_mvp_decision_contract_v1"


def build_mvp_decision_contract(
    contract_summary: Dict[str, Any],
    executor_summary: Dict[str, Any],
    release_verdict: Dict[str, Any],
) -> Dict[str, Any]:
    temporary_ready = bool(
        release_verdict.get("status") == "passed"
        and executor_summary.get("executable_by_executor_count") == 12
        and executor_summary.get("blocked_by_executor_count") == 7
        and executor_summary.get("temporary_scope_only") is True
        and executor_summary.get("save_allowed") is False
        and contract_summary.get("non_safe_authoring_command_count") == 0
    )
    durable_disabled = bool(
        release_verdict.get("durable_authoring_enabled") is False
        and contract_summary.get("durable_authoring_eligible_count") == 0
        and contract_summary.get("durable_enable_executor_may_open_count") == 0
        and contract_summary.get("durable_save_allowed_count") == 0
        and contract_summary.get("durable_canary_executor_may_open_count") == 0
        and contract_summary.get("durable_canary_recovery_cleanup_command_allowed_count") == 0
    )
    return {
        "schema": MVP_DECISION_SCHEMA,
        "decision_status": "temporary_mvp_ready_durable_not_enabled"
        if temporary_ready and durable_disabled
        else "mvp_decision_blocked",
        "temporary_blueprint_authoring_mvp_ready": temporary_ready,
        "temporary_mvp_scope": "planner_safe_actor_blueprint_temporary_smoke",
        "durable_blueprint_authoring_mvp_ready": False,
        "durable_authoring_enabled": False,
        "durable_mvp_scope": "not_enabled_contracts_only",
        "durable_save_allowed": False,
        "durable_delete_allowed": False,
        "durable_rename_allowed": False,
        "durable_cleanup_allowed": False,
        "durable_canary_live_execution_allowed": False,
        "release_boundary_version": release_verdict.get("release_boundary_version", ""),
        "required_before_durable_mvp": [
            "refresh reachable live canary preflight report",
            "add explicit durable executor implementation review",
            "prove durable save gate with save=true still isolated from temporary smoke",
            "prove cleanup/delete only for ownership-marked executor-created canary assets",
            "rerun full offline suite and live smoke before any durable enable flag",
        ],
    }
