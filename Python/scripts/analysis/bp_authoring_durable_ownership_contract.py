#!/usr/bin/env python
"""
Section 52 durable rollback ownership marker contract.

The contract defines how a future durable executor proves that an asset was
created by that executor before rollback/delete can even be considered. It does
not execute delete, save, rename, or overwrite operations.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable


OWNERSHIP_MARKER_SCHEMA = "section_52_durable_ownership_marker_contract_v1"
ROLLBACK_DELETE_AUTHORIZATION_SCHEMA = "section_52_rollback_delete_authorization_v1"

MARKER_NAMESPACE = "unreal_mcp_durable_authoring"
MARKER_KEY = "mcp_executor_created_asset_marker"

REQUIRED_MARKER_FIELDS = (
    "schema",
    "namespace",
    "marker_key",
    "executor_id",
    "durable_plan_id",
    "run_id",
    "target_asset_path",
    "created_asset_path",
    "preflight_asset_existed_before_authoring",
)


def build_ownership_marker_contract(requested: bool, target_asset_path: str) -> Dict[str, Any]:
    policy_ready = bool(requested and target_asset_path)
    return {
        "id": "durable_ownership_marker",
        "schema": OWNERSHIP_MARKER_SCHEMA,
        "requested": requested,
        "target_asset_path": target_asset_path,
        "ownership_marker_policy_ready": policy_ready,
        "marker_namespace": MARKER_NAMESPACE,
        "marker_key": MARKER_KEY,
        "required_marker_fields": list(REQUIRED_MARKER_FIELDS),
        "marker_record_required_before_save": requested,
        "marker_verification_required_before_rollback_delete": requested,
        "delete_without_marker_allowed": False,
        "delete_preexisting_asset_allowed": False,
        "overwrite_preexisting_asset_allowed": False,
        "rename_preexisting_asset_allowed": False,
        "allowed_rollback_delete_scope": (
            "only executor-created assets whose marker matches the target asset path and whose preflight asset-exists result was false"
            if requested
            else "not_requested"
        ),
        "required_reinforcement": []
        if policy_ready
        else (
            [
                "define an executor-created asset ownership marker before rollback/delete policy can pass",
                "bind marker verification to target asset path and preflight asset-exists result",
            ]
            if requested
            else []
        ),
    }


def _missing_fields(marker_record: Dict[str, Any], required_fields: Iterable[str]) -> list[str]:
    return [field for field in required_fields if field not in marker_record]


def evaluate_rollback_delete_authorization(
    ownership_contract: Dict[str, Any],
    candidate_asset_path: str,
    marker_record: Dict[str, Any] | None,
    preflight_asset_existed_before_authoring: bool,
) -> Dict[str, Any]:
    marker_record = marker_record or {}
    blocked_by: list[str] = []
    if not ownership_contract.get("requested"):
        blocked_by.append("durable_rollback_not_requested")
    if not ownership_contract.get("ownership_marker_policy_ready"):
        blocked_by.append("ownership_marker_policy_not_ready")
    if preflight_asset_existed_before_authoring:
        blocked_by.append("preexisting_asset_delete_forbidden")
    missing = _missing_fields(marker_record, ownership_contract.get("required_marker_fields", []))
    if missing:
        blocked_by.append("ownership_marker_missing_required_fields")
    if marker_record.get("schema") != OWNERSHIP_MARKER_SCHEMA:
        blocked_by.append("ownership_marker_schema_mismatch")
    if marker_record.get("namespace") != ownership_contract.get("marker_namespace"):
        blocked_by.append("ownership_marker_namespace_mismatch")
    if marker_record.get("marker_key") != ownership_contract.get("marker_key"):
        blocked_by.append("ownership_marker_key_mismatch")
    target_asset_path = ownership_contract.get("target_asset_path", "")
    if candidate_asset_path != target_asset_path:
        blocked_by.append("candidate_asset_path_mismatch")
    if marker_record.get("target_asset_path") != target_asset_path:
        blocked_by.append("marker_target_asset_path_mismatch")
    if marker_record.get("created_asset_path") != candidate_asset_path:
        blocked_by.append("marker_created_asset_path_mismatch")
    if marker_record.get("preflight_asset_existed_before_authoring") is not False:
        blocked_by.append("marker_preflight_asset_existed_before_authoring_not_false")

    return {
        "schema": ROLLBACK_DELETE_AUTHORIZATION_SCHEMA,
        "candidate_asset_path": candidate_asset_path,
        "target_asset_path": target_asset_path,
        "authorized": not blocked_by,
        "delete_allowed_now": False,
        "blocked_by": sorted(set(blocked_by)),
        "durable_side_effects_allowed": False,
    }


def build_valid_marker_record(
    target_asset_path: str,
    executor_id: str = "durable_executor",
    durable_plan_id: str = "offline_plan",
    run_id: str = "offline_run",
) -> Dict[str, Any]:
    return {
        "schema": OWNERSHIP_MARKER_SCHEMA,
        "namespace": MARKER_NAMESPACE,
        "marker_key": MARKER_KEY,
        "executor_id": executor_id,
        "durable_plan_id": durable_plan_id,
        "run_id": run_id,
        "target_asset_path": target_asset_path,
        "created_asset_path": target_asset_path,
        "preflight_asset_existed_before_authoring": False,
    }
