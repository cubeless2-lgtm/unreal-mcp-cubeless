#!/usr/bin/env python
"""Shared helpers for durable executor authoring release-stage dry-run contracts."""

from __future__ import annotations

from typing import Any, Dict, Sequence


ALLOWED_REQUESTED_COMMANDS = (
    "create_blueprint_asset",
    "compile_and_validate_blueprint",
    "write_executor_ownership_marker",
    "readback_executor_ownership_marker",
    "read_only_asset_exists_check",
)
FORBIDDEN_REQUESTED_COMMANDS = (
    "compile_and_validate_blueprint(save=true)",
    "compile_and_save_blueprint",
    "save=true",
    "save_true",
    "save_asset",
    "delete_asset",
    "rename_asset",
    "duplicate_asset",
    "replace_existing_asset",
    "cleanup_asset",
    "general_durable_authoring",
    "live_command_dispatch",
    "live_command_execution",
)


def _attempted(value: Any) -> bool:
    return value is True or value == 1


def _sum_truthy(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(1 for contract in contracts if contract.get(key))


def _sum_count(contracts: Sequence[Dict[str, Any]], key: str) -> int:
    return sum(contract.get(key, 0) for contract in contracts)


def _proof_flag(record: Dict[str, Any], group: str, key: str) -> bool:
    value = record.get(group, {})
    return isinstance(value, dict) and value.get(key) is True


def _chain_flags(spec: Dict[str, Any], previous_summary: Dict[str, Any]) -> Dict[str, bool]:
    return {
        output_key: previous_summary.get(summary_key) == 1
        for output_key, summary_key, _missing_key in spec["chain_inputs"]
    }


def build_release_stage_dry_run_contract(
    spec: Dict[str, Any],
    requested: bool,
    previous_summary: Dict[str, Any],
    record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    record = record or {}
    record_present = bool(record)
    previous_contract_ready = bool(
        requested
        and previous_summary.get("status") == "passed"
        and previous_summary.get(spec["previous_defined_count_key"]) == 1
        and previous_summary.get(spec["previous_rejected_count_key"]) == 0
        and previous_summary.get(spec["previous_unsafe_count_key"]) == 0
        and previous_summary.get("requested_command_forbidden_count", 0) == 0
        and previous_summary.get("requested_command_unknown_count", 0) == 0
        and all(
            previous_summary.get(key) == 0
            for key in spec["previous_zero_count_keys"]
        )
    )
    chain_flags = _chain_flags(spec, previous_summary)
    chain_satisfied = all(chain_flags.values())
    contract_defined = bool(requested and previous_contract_ready)

    record_schema_matches = bool(
        record_present and record.get("schema") == spec["record_schema"]
    )
    scope_matches = bool(
        record_present
        and record.get(spec["scope_record_field"]) == spec["expected_scope"]
    )
    dry_run_only = bool(record_present and record.get("dry_run_only") is True)
    status_passed = bool(record_present and record.get("status") == "passed")
    operator_reconfirmed_no_live_dispatch = bool(
        record_present and record.get("operator_reconfirmed_no_live_dispatch") is True
    )
    operator_reconfirmed_no_live_execution = bool(
        record_present and record.get("operator_reconfirmed_no_live_execution") is True
    )
    operator_reconfirmed_no_write_execution = bool(
        record_present and record.get("operator_reconfirmed_no_write_execution") is True
    )
    operator_reconfirmed_no_save_delete_rename = bool(
        record_present
        and record.get("operator_reconfirmed_no_save_delete_rename") is True
    )
    requested_command = record.get("requested_command", "")
    operation = record.get(spec["operation_record_field"], "")
    target_asset = record.get("target_asset", "")
    requested_command_allowed = bool(requested_command in ALLOWED_REQUESTED_COMMANDS)
    requested_command_forbidden = bool(requested_command in FORBIDDEN_REQUESTED_COMMANDS)
    requested_command_unknown = bool(
        record_present
        and requested_command not in ALLOWED_REQUESTED_COMMANDS
        and requested_command not in FORBIDDEN_REQUESTED_COMMANDS
    )
    operation_allowed = bool(operation in spec["allowed_operations"])
    target_declared = bool(
        isinstance(target_asset, str) and target_asset.startswith("/Game/")
    )
    admission_proof_matches = all(
        _proof_flag(record, spec["admission_proof_group"], key)
        for key, _summary_key, _missing_key in spec["chain_inputs"]
    )
    release_boundary_proof_safe = bool(
        record_present
        and record.get("release_boundary_proof", {}).get("durable_authoring_enabled")
        is False
        and record.get("release_boundary_proof", {}).get("final_durable_release_ready")
        is False
        and record.get("release_boundary_proof", {}).get("save_delete_rename_allowed")
        is False
        and record.get("release_boundary_proof", {}).get("live_durable_authoring_allowed")
        is False
    )
    unsafe_count = sum(
        int(_attempted(record.get(key)))
        for key in spec["unsafe_action_keys"]
    )
    record_valid = bool(
        contract_defined
        and chain_satisfied
        and record_schema_matches
        and scope_matches
        and dry_run_only
        and status_passed
        and operator_reconfirmed_no_live_dispatch
        and operator_reconfirmed_no_live_execution
        and operator_reconfirmed_no_write_execution
        and operator_reconfirmed_no_save_delete_rename
        and requested_command_allowed
        and not requested_command_forbidden
        and not requested_command_unknown
        and operation_allowed
        and target_declared
        and admission_proof_matches
        and release_boundary_proof_safe
        and unsafe_count == 0
    )
    record_rejected = bool(record_present and not record_valid)
    admissible = bool(record_valid)

    missing: list[str] = []
    if requested:
        if not previous_contract_ready:
            missing.append(spec["previous_ready_missing_key"])
        for output_key, _summary_key, missing_key in spec["chain_inputs"]:
            if not chain_flags[output_key]:
                missing.append(missing_key)
        if not record_present:
            missing.append(spec["record_present_missing_key"])
        if not record_schema_matches:
            missing.append(spec["record_schema_missing_key"])
        if not scope_matches:
            missing.append(spec["scope_missing_key"])
        if not dry_run_only:
            missing.append(spec["dry_run_only_missing_key"])
        if not status_passed:
            missing.append(spec["status_missing_key"])
        if not operator_reconfirmed_no_live_dispatch:
            missing.append("operator_reconfirmed_no_live_dispatch")
        if not operator_reconfirmed_no_live_execution:
            missing.append("operator_reconfirmed_no_live_execution")
        if not operator_reconfirmed_no_write_execution:
            missing.append("operator_reconfirmed_no_write_execution")
        if not operator_reconfirmed_no_save_delete_rename:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        if not requested_command_allowed:
            missing.append("allowed_requested_command")
        if not operation_allowed:
            missing.append(spec["operation_missing_key"])
        if not target_declared:
            missing.append(spec["target_missing_key"])
        if not admission_proof_matches:
            missing.append(spec["admission_proof_missing_key"])
        if not release_boundary_proof_safe:
            missing.append("release_boundary_proof_safe")

    contract: Dict[str, Any] = {
        "id": spec["id"],
        "schema": spec["schema"],
        "requested": requested,
        spec["contract_defined_key"]: contract_defined,
        spec["required_record_schema_field"]: spec["record_schema"] if requested else "",
        spec["expected_scope_field"]: spec["expected_scope"] if requested else "",
        spec["allowed_operations_field"]: (
            list(spec["allowed_operations"]) if requested else []
        ),
        "allowed_requested_commands": (
            list(ALLOWED_REQUESTED_COMMANDS) if requested else []
        ),
        "forbidden_requested_commands": (
            list(FORBIDDEN_REQUESTED_COMMANDS) if requested else []
        ),
        spec["previous_ready_key"]: previous_contract_ready,
        spec["chain_satisfied_key"]: chain_satisfied,
        spec["record_present_key"]: record_present,
        "record_schema_matches": record_schema_matches,
        spec["scope_matches_key"]: scope_matches,
        "dry_run_only": dry_run_only,
        spec["status_passed_key"]: status_passed,
        "operator_reconfirmed_no_live_dispatch": operator_reconfirmed_no_live_dispatch,
        "operator_reconfirmed_no_live_execution": operator_reconfirmed_no_live_execution,
        "operator_reconfirmed_no_write_execution": operator_reconfirmed_no_write_execution,
        "operator_reconfirmed_no_save_delete_rename": (
            operator_reconfirmed_no_save_delete_rename
        ),
        "requested_command_allowed": requested_command_allowed,
        "requested_command_forbidden": requested_command_forbidden,
        "requested_command_unknown": requested_command_unknown,
        spec["operation_allowed_key"]: operation_allowed,
        spec["target_declared_key"]: target_declared,
        spec["admission_proof_matches_key"]: admission_proof_matches,
        "release_boundary_proof_safe": release_boundary_proof_safe,
        spec["record_valid_key"]: record_valid,
        spec["record_rejected_key"]: record_rejected,
        spec["admissible_key"]: admissible,
        spec["unsafe_count_key"]: unsafe_count,
        spec["missing_prerequisites_key"]: missing,
        spec["missing_count_key"]: len(missing),
    }
    contract.update(chain_flags)
    contract.update({key: False for key in spec["output_action_keys"]})
    contract[spec["admissible_key"]] = admissible
    return contract


def summarize_release_stage_dry_runs(
    spec: Dict[str, Any],
    contracts: Sequence[Dict[str, Any]],
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = _sum_truthy(requested, spec["record_rejected_key"])
    unsafe_count = _sum_count(requested, spec["unsafe_count_key"])
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if _sum_truthy(requested, spec["contract_defined_key"]) == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and _sum_truthy(requested, "requested_command_forbidden") == 0
            and _sum_truthy(requested, "requested_command_unknown") == 0
            and all(
                _sum_truthy(requested, key) == 0
                for key in spec["output_action_keys"]
                if key != spec["admissible_key"]
            )
            else "failed"
        )
    summary: Dict[str, Any] = {
        "schema": spec["summary_schema"],
        "status": status,
        spec["request_count_key"]: len(requested),
        spec["contract_defined_count_key"]: _sum_truthy(
            requested, spec["contract_defined_key"]
        ),
        spec["previous_ready_count_key"]: _sum_truthy(
            requested, spec["previous_ready_key"]
        ),
    }
    summary.update(
        {
            f"{output_key}_count": _sum_truthy(requested, output_key)
            for output_key, _summary_key, _missing_key in spec["chain_inputs"]
        }
    )
    summary.update(
        {
            spec["chain_satisfied_count_key"]: _sum_truthy(
                requested, spec["chain_satisfied_key"]
            ),
            spec["record_present_count_key"]: _sum_truthy(
                requested, spec["record_present_key"]
            ),
            "record_schema_matches_count": _sum_truthy(
                requested, "record_schema_matches"
            ),
            spec["scope_matches_count_key"]: _sum_truthy(
                requested, spec["scope_matches_key"]
            ),
            "dry_run_only_count": _sum_truthy(requested, "dry_run_only"),
            spec["status_passed_count_key"]: _sum_truthy(
                requested, spec["status_passed_key"]
            ),
            "operator_reconfirmed_no_live_dispatch_count": _sum_truthy(
                requested, "operator_reconfirmed_no_live_dispatch"
            ),
            "operator_reconfirmed_no_live_execution_count": _sum_truthy(
                requested, "operator_reconfirmed_no_live_execution"
            ),
            "operator_reconfirmed_no_write_execution_count": _sum_truthy(
                requested, "operator_reconfirmed_no_write_execution"
            ),
            "operator_reconfirmed_no_save_delete_rename_count": _sum_truthy(
                requested, "operator_reconfirmed_no_save_delete_rename"
            ),
            "requested_command_allowed_count": _sum_truthy(
                requested, "requested_command_allowed"
            ),
            "requested_command_forbidden_count": _sum_truthy(
                requested, "requested_command_forbidden"
            ),
            "requested_command_unknown_count": _sum_truthy(
                requested, "requested_command_unknown"
            ),
            spec["operation_allowed_count_key"]: _sum_truthy(
                requested, spec["operation_allowed_key"]
            ),
            spec["target_declared_count_key"]: _sum_truthy(
                requested, spec["target_declared_key"]
            ),
            spec["admission_proof_matches_count_key"]: _sum_truthy(
                requested, spec["admission_proof_matches_key"]
            ),
            "release_boundary_proof_safe_count": _sum_truthy(
                requested, "release_boundary_proof_safe"
            ),
            spec["record_valid_count_key"]: _sum_truthy(
                requested, spec["record_valid_key"]
            ),
            spec["record_rejected_count_key"]: rejected_count,
            spec["admissible_count_key"]: _sum_truthy(
                requested, spec["admissible_key"]
            ),
            spec["unsafe_count_key"]: unsafe_count,
            spec["missing_count_key"]: _sum_count(
                requested, spec["missing_count_key"]
            ),
        }
    )
    summary.update(
        {
            f"{key}_count": _sum_truthy(requested, key)
            for key in spec["output_action_keys"]
        }
    )
    return summary
