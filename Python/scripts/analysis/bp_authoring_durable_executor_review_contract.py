#!/usr/bin/env python
"""
Section 63 durable executor implementation review contract.

The contract reviews the current durable executor boundary as a disabled
implementation surface. Passing this review does not approve live durable
authoring; it proves the executor is still closed.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


EXECUTOR_REVIEW_SCHEMA = "section_63_durable_executor_review_contract_v1"
EXECUTOR_REVIEW_SUMMARY_SCHEMA = "section_63_durable_executor_review_summary_v1"


REVIEW_CHECK_IDS = (
    "durable_executor_disabled",
    "durable_command_plan_empty",
    "save_delete_rename_forbidden",
    "read_only_preflight_only",
    "canary_execution_closed",
    "release_boundary_blocks_live_approval",
)


def _check(check_id: str, passed: bool, evidence: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": check_id,
        "passed": passed,
        "evidence": evidence,
    }


def build_executor_review_contract(
    requested: bool,
    executor_summary: Dict[str, Any],
) -> Dict[str, Any]:
    durable_gate = executor_summary.get("durable_gate_summary", {})
    checks = []
    if requested:
        checks = [
            _check(
                "durable_executor_disabled",
                durable_gate.get("durable_executor_enabled_count") == 0
                and durable_gate.get("durable_executor_executable_count") == 0,
                {
                    "enabled_count": durable_gate.get("durable_executor_enabled_count"),
                    "executable_count": durable_gate.get("durable_executor_executable_count"),
                },
            ),
            _check(
                "durable_command_plan_empty",
                durable_gate.get("durable_executor_command_count") == 0
                and durable_gate.get("allowed_live_authoring_command_count") == 0,
                {
                    "command_count": durable_gate.get("durable_executor_command_count"),
                    "allowed_live_authoring_command_count": durable_gate.get(
                        "allowed_live_authoring_command_count"
                    ),
                },
            ),
            _check(
                "save_delete_rename_forbidden",
                durable_gate.get("contract_save_allowed_count") == 0
                and durable_gate.get("save_or_delete_commands_allowed_count") == 0,
                {
                    "contract_save_allowed_count": durable_gate.get("contract_save_allowed_count"),
                    "save_or_delete_commands_allowed_count": durable_gate.get(
                        "save_or_delete_commands_allowed_count"
                    ),
                },
            ),
            _check(
                "read_only_preflight_only",
                durable_gate.get("read_only_live_preflight_allowed_count") == durable_gate.get(
                    "durable_requested_manifest_count"
                )
                and durable_gate.get("preflight_pass_count") == 0,
                {
                    "read_only_allowed_count": durable_gate.get("read_only_live_preflight_allowed_count"),
                    "durable_requested_manifest_count": durable_gate.get("durable_requested_manifest_count"),
                    "preflight_pass_count": durable_gate.get("preflight_pass_count"),
                },
            ),
            _check(
                "canary_execution_closed",
                durable_gate.get("canary_live_execution_allowed_count") == 0
                and durable_gate.get("canary_bridge_refresh_execution_allowed_count") == 0
                and durable_gate.get("canary_bridge_refresh_executor_may_open_count") == 0,
                {
                    "canary_live_execution_allowed_count": durable_gate.get(
                        "canary_live_execution_allowed_count"
                    ),
                    "bridge_refresh_execution_allowed_count": durable_gate.get(
                        "canary_bridge_refresh_execution_allowed_count"
                    ),
                    "bridge_refresh_executor_may_open_count": durable_gate.get(
                        "canary_bridge_refresh_executor_may_open_count"
                    ),
                },
            ),
            _check(
                "release_boundary_blocks_live_approval",
                executor_summary.get("temporary_scope_only") is True
                and executor_summary.get("durable_authoring_allowed") is False
                and executor_summary.get("save_allowed") is False,
                {
                    "temporary_scope_only": executor_summary.get("temporary_scope_only"),
                    "durable_authoring_allowed": executor_summary.get("durable_authoring_allowed"),
                    "save_allowed": executor_summary.get("save_allowed"),
                },
            ),
        ]
    failing = [check["id"] for check in checks if not check["passed"]]
    disabled_boundary_review_passed = bool(requested and checks and not failing)
    return {
        "id": "durable_executor_implementation_review",
        "schema": EXECUTOR_REVIEW_SCHEMA,
        "requested": requested,
        "review_check_count": len(checks),
        "review_checks": checks,
        "failing_check_ids": failing,
        "disabled_executor_boundary_review_passed": disabled_boundary_review_passed,
        "durable_live_implementation_approved": False,
        "durable_executor_may_open_after_review": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "canary_execution_allowed": False,
        "blocked_by": []
        if not requested
        else [
            "section_63_review_does_not_approve_live_durable_executor",
            "durable_live_implementation_not_approved",
        ],
        "required_reinforcement": []
        if not requested
        else [
            "review durable executor implementation before enabling any live command plan",
            "keep save/delete/rename forbidden until the save gate and rollback proof pass",
            "require a later explicit durable release decision before executor may open",
        ],
    }


def summarize_executor_review_contracts(contracts: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(1 for contract in requested if contract.get("disabled_executor_boundary_review_passed")) == len(requested)
            and sum(1 for contract in requested if contract.get("durable_live_implementation_approved")) == 0
            and sum(1 for contract in requested if contract.get("durable_executor_may_open_after_review")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_delete_rename_allowed")) == 0
            and sum(1 for contract in requested if contract.get("canary_execution_allowed")) == 0
            else "failed"
        )
    return {
        "schema": EXECUTOR_REVIEW_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_executor_review_count": len(requested),
        "review_check_count": sum(contract.get("review_check_count", 0) for contract in requested),
        "disabled_executor_boundary_review_passed_count": sum(
            1 for contract in requested if contract.get("disabled_executor_boundary_review_passed")
        ),
        "durable_live_implementation_approved_count": sum(
            1 for contract in requested if contract.get("durable_live_implementation_approved")
        ),
        "durable_executor_may_open_after_review_count": sum(
            1 for contract in requested if contract.get("durable_executor_may_open_after_review")
        ),
        "durable_authoring_allowed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_allowed")
        ),
        "save_delete_rename_allowed_count": sum(
            1 for contract in requested if contract.get("save_delete_rename_allowed")
        ),
        "canary_execution_allowed_count": sum(
            1 for contract in requested if contract.get("canary_execution_allowed")
        ),
        "failing_check_count": sum(len(contract.get("failing_check_ids", [])) for contract in requested),
    }
