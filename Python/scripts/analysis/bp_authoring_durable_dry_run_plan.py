#!/usr/bin/env python
"""
Section 53 durable executor dry-run plan.

The plan records how a future durable executor would reason about target,
conflict policy, validation, save, and rollback. It intentionally contains no
live authoring, save, delete, rename, or overwrite command plan.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


DRY_RUN_PLAN_SCHEMA = "section_53_durable_executor_dry_run_plan_v1"
DRY_RUN_PLAN_SUMMARY_SCHEMA = "section_53_durable_executor_dry_run_plan_summary_v1"

FORBIDDEN_COMMANDS = (
    "create_blueprint",
    "compile_and_validate_blueprint(save=true)",
    "save_asset",
    "delete_asset",
    "rename_asset",
    "duplicate_asset",
    "replace_existing_asset",
)


def _step(step_id: str, label: str, evidence: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": step_id,
        "label": label,
        "mode": "offline_report_only",
        "live_command_allowed": False,
        "command": "",
        "evidence": evidence,
    }


def build_durable_dry_run_plan(
    requested: bool,
    preflight_contract: Dict[str, Any],
    enable_contract: Dict[str, Any],
    ownership_marker_contract: Dict[str, Any],
    save_gate_contract: Dict[str, Any],
    rollback_policy_contract: Dict[str, Any],
    readiness_contract: Dict[str, Any],
    executor_skeleton_contract: Dict[str, Any],
) -> Dict[str, Any]:
    target_asset_path = preflight_contract.get("target_asset_path", "")
    plan_steps = []
    if requested:
        plan_steps = [
            _step(
                "target_preflight",
                "Read-only target asset existence preflight",
                {
                    "target_asset_path": target_asset_path,
                    "live_read_only_check_allowed": bool(preflight_contract.get("live_read_only_check_allowed")),
                    "asset_exists_check_command": preflight_contract.get("asset_exists_check_command", ""),
                },
            ),
            _step(
                "conflict_policy",
                "Overwrite-or-rename decision review",
                preflight_contract.get("overwrite_rename_decision_contract", {}),
            ),
            _step(
                "ownership_marker",
                "Executor-created ownership marker preparation",
                {
                    "ownership_marker_policy_ready": bool(
                        ownership_marker_contract.get("ownership_marker_policy_ready")
                    ),
                    "marker_schema": ownership_marker_contract.get("schema", ""),
                    "marker_key": ownership_marker_contract.get("marker_key", ""),
                },
            ),
            _step(
                "compile_validation_draft",
                "Durable compile validation draft",
                {
                    "compile_save_allowed": bool(save_gate_contract.get("compile_save_allowed")),
                    "durable_compile_save_validation_enabled": bool(
                        save_gate_contract.get("prerequisites", {}).get("durable_compile_save_validation_enabled")
                    ),
                },
            ),
            _step(
                "save_gate_review",
                "Durable save gate review",
                {
                    "save_allowed": bool(save_gate_contract.get("save_allowed")),
                    "blocked_by": list(save_gate_contract.get("blocked_by", [])),
                },
            ),
            _step(
                "rollback_authorization_draft",
                "Rollback authorization draft",
                {
                    "rollback_policy_ready": bool(rollback_policy_contract.get("rollback_policy_ready")),
                    "rollback_allowed": bool(rollback_policy_contract.get("rollback_allowed")),
                    "allowed_delete_scope": rollback_policy_contract.get("allowed_delete_scope", ""),
                },
            ),
        ]

    blocked_by: list[str] = []
    if requested:
        if not target_asset_path:
            blocked_by.append("target_asset_path_missing")
        blocked_by.extend(enable_contract.get("failed_required_gate_ids", []))
        blocked_by.extend(save_gate_contract.get("blocked_by", []))
        blocked_by.extend(readiness_contract.get("failing_checks", []))
        if not ownership_marker_contract.get("ownership_marker_policy_ready"):
            blocked_by.append("ownership_marker_policy_not_ready")
        if not rollback_policy_contract.get("rollback_policy_ready"):
            blocked_by.append("rollback_policy_not_ready")
        if executor_skeleton_contract.get("executor_enabled") or executor_skeleton_contract.get("can_execute"):
            blocked_by.append("durable_executor_unexpectedly_enabled")
        blocked_by.append("section_53_dry_run_only")

    dry_run_plan_created = bool(requested and target_asset_path)
    dry_run_plan_valid = bool(
        dry_run_plan_created
        and plan_steps
        and all(not step["live_command_allowed"] and not step["command"] for step in plan_steps)
    )
    return {
        "id": "durable_executor_dry_run_plan",
        "schema": DRY_RUN_PLAN_SCHEMA,
        "requested": requested,
        "target_asset_path": target_asset_path,
        "dry_run_plan_created": dry_run_plan_created,
        "dry_run_plan_valid": dry_run_plan_valid,
        "plan_status": "blocked_dry_run_ready" if dry_run_plan_valid else ("not_requested" if not requested else "invalid"),
        "plan_steps": plan_steps,
        "plan_step_count": len(plan_steps),
        "execution_command_plan": [],
        "live_command_count": 0,
        "durable_executor_may_execute": False,
        "durable_authoring_allowed": False,
        "save_allowed": False,
        "delete_allowed": False,
        "rename_allowed": False,
        "forbidden_commands": list(FORBIDDEN_COMMANDS),
        "blocked_by": sorted(set(blocked_by)),
        "required_reinforcement": []
        if not requested
        else [
            "keep Section 53 as a no-command dry-run plan",
            "satisfy enable, save simulation, canary approval, and rollback recovery sections before live durable execution",
        ],
    }


def summarize_dry_run_plans(plans: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested_plans = [plan for plan in plans if plan.get("requested")]
    live_command_count = sum(plan.get("live_command_count", 0) for plan in requested_plans)
    executor_may_execute_count = sum(1 for plan in requested_plans if plan.get("durable_executor_may_execute"))
    forbidden_allowed_count = sum(
        1
        for plan in requested_plans
        if plan.get("save_allowed") or plan.get("delete_allowed") or plan.get("rename_allowed")
    )
    status = "not_requested"
    if requested_plans:
        status = (
            "passed"
            if live_command_count == 0 and executor_may_execute_count == 0 and forbidden_allowed_count == 0
            else "failed"
        )
    return {
        "schema": DRY_RUN_PLAN_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_plan_count": len(requested_plans),
        "dry_run_plan_created_count": sum(1 for plan in requested_plans if plan.get("dry_run_plan_created")),
        "dry_run_plan_valid_count": sum(1 for plan in requested_plans if plan.get("dry_run_plan_valid")),
        "durable_executor_may_execute_count": executor_may_execute_count,
        "live_command_count": live_command_count,
        "forbidden_command_allowed_count": forbidden_allowed_count,
    }
