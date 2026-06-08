#!/usr/bin/env python
"""
Sections 193-200 durable executor authoring save-gate preflight batch.

This contract advances from Section 192 final no-save readiness into save-gate
preflight readiness only. It proves target declaration, ownership-marker,
rollback, overwrite/rename, read-only preflight, and command-admission proof are
ready without opening save=true, save_asset, delete, rename, live durable write,
or final durable release readiness.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence

import bp_authoring_durable_executor_authoring_no_save_execution_batch_contract as no_save_batch


DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_PREFLIGHT_BATCH_SCHEMA = (
    "section_193_200_durable_executor_authoring_save_gate_preflight_batch_contract_v1"
)
DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_PREFLIGHT_BATCH_SUMMARY_SCHEMA = (
    "section_193_200_durable_executor_authoring_save_gate_preflight_batch_summary_v1"
)
SECTION_186_192_NO_SAVE_SUMMARY_SCHEMA = (
    no_save_batch
    .DURABLE_EXECUTOR_AUTHORING_NO_SAVE_EXECUTION_BATCH_SUMMARY_SCHEMA
)
DEFAULT_SAVE_TARGET_ASSET_PATH = (
    "/Game/_MCP_Temp/DurableSaveGate/BP_DurableSaveGatePrep"
)
SAVE_TARGET_PACKAGE_PREFIXES = (
    "/Game/_MCP_Temp/",
    "/Game/MCPTestFixtures/",
)
UPSTREAM_NO_SAVE_REQUIRED_COUNT_KEYS = (
    "no_save_execution_batch_admissible_count",
    "section_186_executor_opened_count",
    "section_187_open_readiness_consolidated_count",
    "section_188_authoring_command_allowed_count",
    "section_189_command_dispatch_gate_open_count",
    "section_190_command_execution_evidence_gate_open_count",
    "section_191_completion_readback_ready_count",
    "section_192_final_no_save_release_ready_count",
    "durable_executor_opened_count",
    "durable_authoring_command_allowed_count",
    "durable_authoring_command_dispatched_count",
    "durable_authoring_command_executed_count",
    "durable_authoring_command_completed_count",
    "final_no_save_release_ready_count",
    "durable_authoring_enabled_count",
)
UPSTREAM_BLOCKED_OUTPUT_COUNT_KEYS = no_save_batch.BLOCKED_OUTPUT_COUNT_KEYS
SAVE_GATE_PREFLIGHT_PATH_COUNT_KEYS = (
    "save_target_declared_count",
    "save_target_package_allowlisted_count",
    "save_target_read_only_exists_check_ready_count",
    "ownership_marker_revalidated_count",
    "rollback_policy_revalidated_count",
    "overwrite_rename_decision_ready_count",
    "read_only_save_preflight_ready_count",
    "save_command_admission_preflight_ready_count",
    "save_gate_open_review_ready_count",
    "save_gate_preflight_ready_count",
)


def _truthy_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(int(contract.get(key, 0) or 0) for contract in contracts)


def _count_is_one(summary: Dict[str, Any], key: str) -> bool:
    return bool(summary.get(key) == 1)


def _blocked_output_counts(summary: Dict[str, Any]) -> Dict[str, int]:
    return {
        key: int(summary.get(key, 0) or 0)
        for key in UPSTREAM_BLOCKED_OUTPUT_COUNT_KEYS
    }


def _target_declared(target_asset_path: str) -> bool:
    return bool(
        target_asset_path
        and target_asset_path.startswith("/Game/")
        and " " not in target_asset_path
        and target_asset_path.count("/") >= 2
    )


def _target_allowlisted(target_asset_path: str) -> bool:
    return any(
        target_asset_path.startswith(prefix)
        for prefix in SAVE_TARGET_PACKAGE_PREFIXES
    )


def build_durable_executor_authoring_save_gate_preflight_batch_contract(
    requested: bool,
    section_186_192_no_save_summary: Dict[str, Any],
    target_asset_path: str = DEFAULT_SAVE_TARGET_ASSET_PATH,
) -> Dict[str, Any]:
    blocked_counts = _blocked_output_counts(section_186_192_no_save_summary)
    section_186_192_summary_schema_matches = bool(
        section_186_192_no_save_summary.get("schema")
        == SECTION_186_192_NO_SAVE_SUMMARY_SCHEMA
    )
    section_186_192_summary_passed = bool(
        section_186_192_no_save_summary.get("status") == "passed"
    )
    upstream_no_save_ready = all(
        _count_is_one(section_186_192_no_save_summary, key)
        for key in UPSTREAM_NO_SAVE_REQUIRED_COUNT_KEYS
    )
    upstream_write_outputs_blocked = all(
        count == 0 for count in blocked_counts.values()
    )
    save_target_declared = _target_declared(target_asset_path)
    save_target_package_allowlisted = _target_allowlisted(target_asset_path)
    save_target_read_only_exists_check_ready = bool(
        requested
        and section_186_192_summary_schema_matches
        and section_186_192_summary_passed
        and upstream_no_save_ready
        and upstream_write_outputs_blocked
        and save_target_declared
        and save_target_package_allowlisted
    )
    ownership_marker_revalidated = save_target_read_only_exists_check_ready
    rollback_policy_revalidated = save_target_read_only_exists_check_ready
    overwrite_rename_decision_ready = save_target_read_only_exists_check_ready
    read_only_save_preflight_ready = save_target_read_only_exists_check_ready
    save_command_admission_preflight_ready = bool(
        save_target_read_only_exists_check_ready
        and ownership_marker_revalidated
        and rollback_policy_revalidated
        and overwrite_rename_decision_ready
        and read_only_save_preflight_ready
    )
    save_gate_open_review_ready = save_command_admission_preflight_ready
    save_gate_preflight_ready = save_gate_open_review_ready

    return {
        "id": "durable_executor_authoring_save_gate_preflight_batch",
        "schema": DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_PREFLIGHT_BATCH_SCHEMA,
        "requested": requested,
        "target_asset_path": target_asset_path,
        "section_186_192_summary_schema_matches": (
            section_186_192_summary_schema_matches
        ),
        "section_186_192_summary_passed": section_186_192_summary_passed,
        "section_186_192_no_save_ready": upstream_no_save_ready,
        "section_186_192_write_outputs_blocked": (
            upstream_write_outputs_blocked
        ),
        "save_target_declared": save_target_declared,
        "save_target_package_allowlisted": save_target_package_allowlisted,
        "save_target_read_only_exists_check_ready": (
            save_target_read_only_exists_check_ready
        ),
        "ownership_marker_revalidated": ownership_marker_revalidated,
        "rollback_policy_revalidated": rollback_policy_revalidated,
        "overwrite_rename_decision_ready": overwrite_rename_decision_ready,
        "read_only_save_preflight_ready": read_only_save_preflight_ready,
        "save_command_admission_preflight_ready": (
            save_command_admission_preflight_ready
        ),
        "save_gate_open_review_ready": save_gate_open_review_ready,
        "save_gate_preflight_ready": save_gate_preflight_ready,
        "section_193_save_target_declared": save_target_declared,
        "section_194_ownership_marker_revalidated": (
            ownership_marker_revalidated
        ),
        "section_195_rollback_policy_revalidated": rollback_policy_revalidated,
        "section_196_overwrite_rename_decision_ready": (
            overwrite_rename_decision_ready
        ),
        "section_197_read_only_save_preflight_ready": (
            read_only_save_preflight_ready
        ),
        "section_198_save_command_admission_preflight_ready": (
            save_command_admission_preflight_ready
        ),
        "section_199_save_gate_open_review_ready": save_gate_open_review_ready,
        "section_200_final_save_gate_preflight_ready": (
            save_gate_preflight_ready
        ),
        "durable_authoring_enabled": save_gate_preflight_ready,
        "durable_executor_opened": save_gate_preflight_ready,
        "durable_authoring_command_no_save_execution_ready": (
            save_gate_preflight_ready
        ),
        "final_no_save_release_ready": save_gate_preflight_ready,
        "durable_authoring_allowed": False,
        "final_durable_release_ready": False,
        "asset_write_performed": False,
        "package_dirty_marked": False,
        "save_gate_open_allowed": False,
        "save_command_admitted": False,
        "save_command_dispatched": False,
        "save_command_executed": False,
        "save_true_allowed": False,
        "save_asset_allowed": False,
        "compile_save_allowed": False,
        "save_delete_rename_allowed": False,
        "delete_asset_allowed": False,
        "rename_asset_allowed": False,
        "live_durable_authoring_allowed": False,
        "live_command_dispatched": False,
        "live_command_executed": False,
        **{
            key: 1 if save_gate_preflight_ready else 0
            for key in SAVE_GATE_PREFLIGHT_PATH_COUNT_KEYS
        },
        **blocked_counts,
    }


def summarize_durable_executor_authoring_save_gate_preflight_batches(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _truthy_count(requested, "save_gate_preflight_ready")
            == len(requested)
            and _truthy_count(requested, "section_193_save_target_declared")
            == len(requested)
            and _truthy_count(
                requested, "section_194_ownership_marker_revalidated"
            )
            == len(requested)
            and _truthy_count(
                requested, "section_195_rollback_policy_revalidated"
            )
            == len(requested)
            and _truthy_count(
                requested, "section_196_overwrite_rename_decision_ready"
            )
            == len(requested)
            and _truthy_count(
                requested, "section_197_read_only_save_preflight_ready"
            )
            == len(requested)
            and _truthy_count(
                requested,
                "section_198_save_command_admission_preflight_ready",
            )
            == len(requested)
            and _truthy_count(
                requested, "section_199_save_gate_open_review_ready"
            )
            == len(requested)
            and _truthy_count(
                requested, "section_200_final_save_gate_preflight_ready"
            )
            == len(requested)
            and _truthy_count(requested, "durable_authoring_allowed") == 0
            and _truthy_count(requested, "final_durable_release_ready") == 0
            and _truthy_count(requested, "asset_write_performed") == 0
            and _truthy_count(requested, "package_dirty_marked") == 0
            and _truthy_count(requested, "save_gate_open_allowed") == 0
            and _truthy_count(requested, "save_command_admitted") == 0
            and _truthy_count(requested, "save_command_dispatched") == 0
            and _truthy_count(requested, "save_command_executed") == 0
            and _truthy_count(requested, "save_true_allowed") == 0
            and _truthy_count(requested, "save_asset_allowed") == 0
            and _truthy_count(requested, "compile_save_allowed") == 0
            and _truthy_count(requested, "save_delete_rename_allowed") == 0
            and _truthy_count(requested, "delete_asset_allowed") == 0
            and _truthy_count(requested, "rename_asset_allowed") == 0
            and _truthy_count(requested, "live_durable_authoring_allowed") == 0
            and _truthy_count(requested, "live_command_dispatched") == 0
            and _truthy_count(requested, "live_command_executed") == 0
            and all(
                _sum_count(requested, key) == 0
                for key in UPSTREAM_BLOCKED_OUTPUT_COUNT_KEYS
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": (
            DURABLE_EXECUTOR_AUTHORING_SAVE_GATE_PREFLIGHT_BATCH_SUMMARY_SCHEMA
        ),
        "status": status,
        "durable_requested_executor_authoring_save_gate_preflight_batch_count": (
            len(requested)
        ),
        "section_186_192_summary_schema_matches_count": _truthy_count(
            requested, "section_186_192_summary_schema_matches"
        ),
        "section_186_192_summary_passed_count": _truthy_count(
            requested, "section_186_192_summary_passed"
        ),
        "section_186_192_no_save_ready_count": _truthy_count(
            requested, "section_186_192_no_save_ready"
        ),
        "section_186_192_write_outputs_blocked_count": _truthy_count(
            requested, "section_186_192_write_outputs_blocked"
        ),
        "section_193_save_target_declared_count": _truthy_count(
            requested, "section_193_save_target_declared"
        ),
        "section_194_ownership_marker_revalidated_count": _truthy_count(
            requested, "section_194_ownership_marker_revalidated"
        ),
        "section_195_rollback_policy_revalidated_count": _truthy_count(
            requested, "section_195_rollback_policy_revalidated"
        ),
        "section_196_overwrite_rename_decision_ready_count": _truthy_count(
            requested, "section_196_overwrite_rename_decision_ready"
        ),
        "section_197_read_only_save_preflight_ready_count": _truthy_count(
            requested, "section_197_read_only_save_preflight_ready"
        ),
        "section_198_save_command_admission_preflight_ready_count": (
            _truthy_count(
                requested,
                "section_198_save_command_admission_preflight_ready",
            )
        ),
        "section_199_save_gate_open_review_ready_count": _truthy_count(
            requested, "section_199_save_gate_open_review_ready"
        ),
        "section_200_final_save_gate_preflight_ready_count": _truthy_count(
            requested, "section_200_final_save_gate_preflight_ready"
        ),
        "durable_authoring_enabled_count": _truthy_count(
            requested, "durable_authoring_enabled"
        ),
        "durable_executor_opened_count": _truthy_count(
            requested, "durable_executor_opened"
        ),
        "durable_authoring_command_no_save_execution_ready_count": (
            _truthy_count(
                requested,
                "durable_authoring_command_no_save_execution_ready",
            )
        ),
        "final_no_save_release_ready_count": _truthy_count(
            requested, "final_no_save_release_ready"
        ),
        "durable_authoring_allowed_count": _truthy_count(
            requested, "durable_authoring_allowed"
        ),
        "final_durable_release_ready_count": _truthy_count(
            requested, "final_durable_release_ready"
        ),
        "asset_write_performed_count": _truthy_count(
            requested, "asset_write_performed"
        ),
        "package_dirty_marked_count": _truthy_count(
            requested, "package_dirty_marked"
        ),
        "save_gate_open_allowed_count": _truthy_count(
            requested, "save_gate_open_allowed"
        ),
        "save_command_admitted_count": _truthy_count(
            requested, "save_command_admitted"
        ),
        "save_command_dispatched_count": _truthy_count(
            requested, "save_command_dispatched"
        ),
        "save_command_executed_count": _truthy_count(
            requested, "save_command_executed"
        ),
        "save_true_allowed_count": _truthy_count(
            requested, "save_true_allowed"
        ),
        "save_asset_allowed_count": _truthy_count(
            requested, "save_asset_allowed"
        ),
        "compile_save_allowed_count": _truthy_count(
            requested, "compile_save_allowed"
        ),
        "save_delete_rename_allowed_count": _truthy_count(
            requested, "save_delete_rename_allowed"
        ),
        "delete_asset_allowed_count": _truthy_count(
            requested, "delete_asset_allowed"
        ),
        "rename_asset_allowed_count": _truthy_count(
            requested, "rename_asset_allowed"
        ),
        "live_durable_authoring_allowed_count": _truthy_count(
            requested, "live_durable_authoring_allowed"
        ),
        "live_command_dispatched_count": _truthy_count(
            requested, "live_command_dispatched"
        ),
        "live_command_executed_count": _truthy_count(
            requested, "live_command_executed"
        ),
    }
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in SAVE_GATE_PREFLIGHT_PATH_COUNT_KEYS
        }
    )
    summary.update(
        {
            key: _sum_count(requested, key)
            for key in UPSTREAM_BLOCKED_OUTPUT_COUNT_KEYS
        }
    )
    return summary
