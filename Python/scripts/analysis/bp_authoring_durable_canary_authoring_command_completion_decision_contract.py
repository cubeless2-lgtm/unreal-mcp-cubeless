#!/usr/bin/env python
"""
Section 89 durable canary authoring command completion decision contract.

This contract defines the scoped decision record required after future durable
authoring command execution evidence is admitted. It does not complete commands,
save assets, or open durable authoring.
"""

from __future__ import annotations

from typing import Any, Dict, Sequence


CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_DECISION_SCHEMA = (
    "section_89_durable_canary_authoring_command_completion_decision_contract_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_DECISION_RECORD_SCHEMA = (
    "section_89_durable_canary_authoring_command_completion_decision_record_v1"
)
CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_DECISION_SUMMARY_SCHEMA = (
    "section_89_durable_canary_authoring_command_completion_decision_summary_v1"
)
EXPECTED_COMPLETION_SCOPE = "durable_canary_authoring_command_completion_decision_only"


def _authorized(value: Any) -> bool:
    return value is True or value == 1


def build_canary_durable_authoring_command_completion_decision_contract(
    requested: bool,
    evidence_summary: Dict[str, Any],
    completion_decision_record: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    completion_decision_record = completion_decision_record or {}
    decision_record_present = bool(completion_decision_record)
    evidence_contract_ready = bool(
        requested
        and evidence_summary.get("status") == "passed"
        and evidence_summary.get("evidence_contract_defined_count") == 1
        and evidence_summary.get("evidence_record_rejected_count") == 0
        and evidence_summary.get("unsafe_evidence_record_count") == 0
        and evidence_summary.get("reported_forbidden_evidence_command_count") == 0
        and evidence_summary.get("durable_authoring_command_dispatch_allowed_count") == 0
        and evidence_summary.get("durable_authoring_command_dispatched_count") == 0
        and evidence_summary.get("durable_authoring_command_execution_allowed_count") == 0
        and evidence_summary.get("durable_authoring_command_executed_count") == 0
        and evidence_summary.get("durable_promotion_allowed_count") == 0
        and evidence_summary.get("durable_authoring_enabled_count") == 0
        and evidence_summary.get("durable_authoring_allowed_count") == 0
        and evidence_summary.get("save_delete_rename_allowed_count") == 0
        and evidence_summary.get("cleanup_allowed_count") == 0
        and evidence_summary.get("live_command_dispatch_allowed_count") == 0
        and evidence_summary.get("live_command_execution_allowed_count") == 0
        and evidence_summary.get("live_command_executed_count") == 0
    )
    authoring_command_execution_evidence_admitted = bool(
        evidence_summary.get("authoring_command_execution_evidence_admitted_count") == 1
    )
    allowed_evidence_command_observed = bool(
        evidence_summary.get("allowed_evidence_command_observed_count") == 1
    )
    no_forbidden_evidence_commands = bool(
        evidence_summary.get("no_forbidden_evidence_commands_count") == 1
    )
    evidence_ready_for_completion = bool(
        authoring_command_execution_evidence_admitted
        and allowed_evidence_command_observed
        and no_forbidden_evidence_commands
    )
    record_schema_matches = bool(
        decision_record_present
        and completion_decision_record.get("schema")
        == CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_DECISION_RECORD_SCHEMA
    )
    completion_scope_matches = bool(
        decision_record_present
        and completion_decision_record.get("completion_scope") == EXPECTED_COMPLETION_SCOPE
    )
    explicit_completion_authorized = bool(
        decision_record_present
        and completion_decision_record.get(
            "explicit_durable_authoring_command_completion_authorized"
        )
        is True
    )
    no_save_delete_rename_acknowledged = bool(
        decision_record_present
        and completion_decision_record.get("operator_reconfirmed_no_save_delete_rename")
        is True
    )
    unsafe_completion_decision_record_count = sum(
        int(_authorized(completion_decision_record.get(key)))
        for key in (
            "durable_authoring_command_completion_allowed",
            "durable_authoring_command_completed",
            "durable_authoring_command_dispatch_allowed",
            "durable_authoring_command_dispatched",
            "durable_authoring_command_execution_allowed",
            "durable_authoring_command_executed",
            "durable_release_promotion_allowed",
            "durable_release_promoted",
            "durable_authoring_enabled",
            "durable_authoring_allowed",
            "save_asset_authorized",
            "save_asset_executed",
            "delete_asset_authorized",
            "rename_asset_authorized",
            "cleanup_authorized",
            "live_command_dispatch_authorized",
            "live_command_dispatch_performed",
            "live_command_execution_authorized",
            "live_command_execution_performed",
            "live_command_executed",
        )
    )
    completion_decision_contract_defined = bool(requested and evidence_contract_ready)
    completion_decision_record_valid = bool(
        completion_decision_contract_defined
        and evidence_ready_for_completion
        and record_schema_matches
        and completion_scope_matches
        and explicit_completion_authorized
        and no_save_delete_rename_acknowledged
        and unsafe_completion_decision_record_count == 0
    )
    missing = []
    if requested:
        if not authoring_command_execution_evidence_admitted:
            missing.append("section_88_authoring_command_execution_evidence_admitted")
        if not allowed_evidence_command_observed:
            missing.append("section_88_allowed_evidence_command_observed")
        if not no_forbidden_evidence_commands:
            missing.append("section_88_no_forbidden_evidence_commands")
        if not decision_record_present:
            missing.append("durable_authoring_command_completion_decision_record_present")
        if not record_schema_matches:
            missing.append("durable_authoring_command_completion_decision_record_schema")
        if not completion_scope_matches:
            missing.append("durable_canary_authoring_command_completion_decision_only_scope")
        if not explicit_completion_authorized:
            missing.append("explicit_durable_authoring_command_completion_authorization")
        if not no_save_delete_rename_acknowledged:
            missing.append("operator_reconfirmed_no_save_delete_rename")
        missing.append("separate_durable_authoring_command_completion_application_contract")
    completion_decision_record_rejected = bool(
        decision_record_present and not completion_decision_record_valid
    )
    return {
        "id": "durable_canary_authoring_command_completion_decision",
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_DECISION_SCHEMA,
        "requested": requested,
        "completion_decision_contract_defined": completion_decision_contract_defined,
        "required_completion_decision_record_schema": (
            CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_DECISION_RECORD_SCHEMA
            if requested
            else ""
        ),
        "expected_completion_scope": EXPECTED_COMPLETION_SCOPE if requested else "",
        "evidence_contract_ready": evidence_contract_ready,
        "authoring_command_execution_evidence_admitted": (
            authoring_command_execution_evidence_admitted
        ),
        "allowed_evidence_command_observed": allowed_evidence_command_observed,
        "no_forbidden_evidence_commands": no_forbidden_evidence_commands,
        "evidence_ready_for_completion": evidence_ready_for_completion,
        "decision_record_present": decision_record_present,
        "record_schema_matches": record_schema_matches,
        "completion_scope_matches": completion_scope_matches,
        "explicit_completion_authorized": explicit_completion_authorized,
        "no_save_delete_rename_acknowledged": no_save_delete_rename_acknowledged,
        "completion_decision_record_valid": completion_decision_record_valid,
        "completion_decision_record_rejected": completion_decision_record_rejected,
        "unsafe_completion_decision_record_count": unsafe_completion_decision_record_count,
        "missing_completion_prerequisites": missing,
        "missing_completion_prerequisite_count": len(missing),
        "durable_authoring_command_completion_allowed": False,
        "durable_authoring_command_completed": False,
        "durable_authoring_command_dispatch_allowed": False,
        "durable_authoring_command_dispatched": False,
        "durable_authoring_command_execution_allowed": False,
        "durable_authoring_command_executed": False,
        "durable_promotion_allowed": False,
        "durable_authoring_enabled": False,
        "durable_authoring_allowed": False,
        "save_delete_rename_allowed": False,
        "cleanup_allowed": False,
        "live_command_dispatch_allowed": False,
        "live_command_plan_emitted": False,
        "live_command_execution_allowed": False,
        "live_command_executed": False,
        "reported_allowed_evidence_command_count": evidence_summary.get(
            "reported_allowed_evidence_command_count",
            0,
        ),
        "reported_forbidden_evidence_command_count": evidence_summary.get(
            "reported_forbidden_evidence_command_count",
            0,
        ),
        "blocked_by": []
        if not requested
        else [
            "section_89_completion_decision_does_not_complete_or_save",
            *missing,
        ],
        "required_reinforcement": []
        if not requested
        else [
            "record a scoped durable authoring command completion decision only after Section 88 admits evidence",
            "reject completion decisions that authorize completion, save, delete, rename, cleanup, durable authoring, or live command actions",
            "keep durable authoring command completion application behind a separate contract after decision validation",
        ],
    }


def summarize_canary_durable_authoring_command_completion_decisions(
    contracts: Sequence[Dict[str, Any]]
) -> Dict[str, Any]:
    requested = [contract for contract in contracts if contract.get("requested")]
    rejected_count = sum(
        1 for contract in requested if contract.get("completion_decision_record_rejected")
    )
    unsafe_count = sum(
        contract.get("unsafe_completion_decision_record_count", 0)
        for contract in requested
    )
    forbidden_evidence_count = sum(
        contract.get("reported_forbidden_evidence_command_count", 0)
        for contract in requested
    )
    status = "not_requested"
    if requested:
        status = (
            "passed"
            if sum(
                1
                for contract in requested
                if contract.get("completion_decision_contract_defined")
            )
            == len(requested)
            and rejected_count == 0
            and unsafe_count == 0
            and forbidden_evidence_count == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_completion_allowed")
            )
            == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_completed")
            )
            == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_dispatch_allowed")
            )
            == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_dispatched")
            )
            == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_execution_allowed")
            )
            == 0
            and sum(
                1
                for contract in requested
                if contract.get("durable_authoring_command_executed")
            )
            == 0
            and sum(1 for contract in requested if contract.get("durable_promotion_allowed")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_enabled")) == 0
            and sum(1 for contract in requested if contract.get("durable_authoring_allowed")) == 0
            and sum(1 for contract in requested if contract.get("save_delete_rename_allowed")) == 0
            and sum(1 for contract in requested if contract.get("cleanup_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_dispatch_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_plan_emitted")) == 0
            and sum(1 for contract in requested if contract.get("live_command_execution_allowed")) == 0
            and sum(1 for contract in requested if contract.get("live_command_executed")) == 0
            else "failed"
        )
    return {
        "schema": CANARY_DURABLE_AUTHORING_COMMAND_COMPLETION_DECISION_SUMMARY_SCHEMA,
        "status": status,
        "durable_requested_canary_authoring_command_completion_decision_count": len(requested),
        "completion_decision_contract_defined_count": sum(
            1
            for contract in requested
            if contract.get("completion_decision_contract_defined")
        ),
        "evidence_contract_ready_count": sum(
            1 for contract in requested if contract.get("evidence_contract_ready")
        ),
        "authoring_command_execution_evidence_admitted_count": sum(
            1
            for contract in requested
            if contract.get("authoring_command_execution_evidence_admitted")
        ),
        "allowed_evidence_command_observed_count": sum(
            1 for contract in requested if contract.get("allowed_evidence_command_observed")
        ),
        "no_forbidden_evidence_commands_count": sum(
            1 for contract in requested if contract.get("no_forbidden_evidence_commands")
        ),
        "evidence_ready_for_completion_count": sum(
            1 for contract in requested if contract.get("evidence_ready_for_completion")
        ),
        "decision_record_present_count": sum(
            1 for contract in requested if contract.get("decision_record_present")
        ),
        "record_schema_matches_count": sum(
            1 for contract in requested if contract.get("record_schema_matches")
        ),
        "completion_scope_matches_count": sum(
            1 for contract in requested if contract.get("completion_scope_matches")
        ),
        "explicit_completion_authorized_count": sum(
            1 for contract in requested if contract.get("explicit_completion_authorized")
        ),
        "no_save_delete_rename_acknowledged_count": sum(
            1 for contract in requested if contract.get("no_save_delete_rename_acknowledged")
        ),
        "completion_decision_record_valid_count": sum(
            1 for contract in requested if contract.get("completion_decision_record_valid")
        ),
        "completion_decision_record_rejected_count": rejected_count,
        "unsafe_completion_decision_record_count": unsafe_count,
        "missing_completion_prerequisite_count": sum(
            contract.get("missing_completion_prerequisite_count", 0)
            for contract in requested
        ),
        "reported_allowed_evidence_command_count": sum(
            contract.get("reported_allowed_evidence_command_count", 0)
            for contract in requested
        ),
        "reported_forbidden_evidence_command_count": forbidden_evidence_count,
        "durable_authoring_command_completion_allowed_count": sum(
            1
            for contract in requested
            if contract.get("durable_authoring_command_completion_allowed")
        ),
        "durable_authoring_command_completed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_command_completed")
        ),
        "durable_authoring_command_dispatch_allowed_count": sum(
            1
            for contract in requested
            if contract.get("durable_authoring_command_dispatch_allowed")
        ),
        "durable_authoring_command_dispatched_count": sum(
            1 for contract in requested if contract.get("durable_authoring_command_dispatched")
        ),
        "durable_authoring_command_execution_allowed_count": sum(
            1
            for contract in requested
            if contract.get("durable_authoring_command_execution_allowed")
        ),
        "durable_authoring_command_executed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_command_executed")
        ),
        "durable_promotion_allowed_count": sum(
            1 for contract in requested if contract.get("durable_promotion_allowed")
        ),
        "durable_authoring_enabled_count": sum(
            1 for contract in requested if contract.get("durable_authoring_enabled")
        ),
        "durable_authoring_allowed_count": sum(
            1 for contract in requested if contract.get("durable_authoring_allowed")
        ),
        "save_delete_rename_allowed_count": sum(
            1 for contract in requested if contract.get("save_delete_rename_allowed")
        ),
        "cleanup_allowed_count": sum(
            1 for contract in requested if contract.get("cleanup_allowed")
        ),
        "live_command_dispatch_allowed_count": sum(
            1 for contract in requested if contract.get("live_command_dispatch_allowed")
        ),
        "live_command_plan_emitted_count": sum(
            1 for contract in requested if contract.get("live_command_plan_emitted")
        ),
        "live_command_execution_allowed_count": sum(
            1 for contract in requested if contract.get("live_command_execution_allowed")
        ),
        "live_command_executed_count": sum(
            1 for contract in requested if contract.get("live_command_executed")
        ),
    }
