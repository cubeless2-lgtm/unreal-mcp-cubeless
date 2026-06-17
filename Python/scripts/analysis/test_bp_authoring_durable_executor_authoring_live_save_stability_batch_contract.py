#!/usr/bin/env python
"""Offline smoke tests for Sections 225-232 live save stability batch."""

from __future__ import annotations

import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_durable_executor_authoring_live_actual_save_execution_batch_contract as live_actual_save_execution  # noqa: E402
import bp_authoring_durable_executor_authoring_live_save_stability_batch_contract as live_save_stability  # noqa: E402
from test_bp_authoring_durable_executor_authoring_live_actual_save_execution_batch_contract import build_current_section_209_216_summary  # noqa: E402


def build_current_section_217_224_summary() -> dict:
    section_209_216_summary = build_current_section_209_216_summary()
    execution_result = live_actual_save_execution.build_live_actual_save_execution_result()
    readback_result = live_actual_save_execution.build_live_actual_save_readback_result()
    contract = (
        live_actual_save_execution
        .build_durable_executor_authoring_live_actual_save_execution_batch_contract(
            True,
            section_209_216_summary,
            execution_result,
            readback_result,
        )
    )
    return (
        live_actual_save_execution
        .summarize_durable_executor_authoring_live_actual_save_execution_batches(
            [contract]
        )
    )


def build_current_stability_result(**overrides: object) -> dict:
    result = live_save_stability.build_live_save_stability_result(
        package_file_size_bytes=24133,
    )
    result.update(overrides)
    return result


def main() -> int:
    section_217_224_summary = build_current_section_217_224_summary()
    stability_result = build_current_stability_result()
    contract = (
        live_save_stability
        .build_durable_executor_authoring_live_save_stability_batch_contract(
            True,
            section_217_224_summary,
            stability_result,
        )
    )
    assert (
        contract["schema"]
        == live_save_stability
        .DURABLE_EXECUTOR_AUTHORING_LIVE_SAVE_STABILITY_BATCH_SCHEMA
    )
    assert contract["requested"] is True
    assert contract["section_217_224_summary_schema_matches"] is True
    assert contract["section_217_224_summary_passed"] is True
    assert contract["section_217_224_actual_save_ready"] is True
    assert contract["section_217_224_delete_rename_closed"] is True
    assert contract["stability_result_schema_matches"] is True
    assert contract["target_path_matches"] is True
    assert contract["target_directory_matches"] is True
    assert contract["compile_api_fixed"] is True
    assert contract["legacy_compile_helper_mismatch_documented"] is True
    assert contract["partial_save_recovery_verified"] is True
    assert contract["idempotent_resave_verified"] is True
    assert contract["save_readback_schema_strengthened"] is True
    assert contract["dirty_package_stability_verified"] is True
    assert contract["production_path_untouched"] is True
    assert contract["delete_rename_cleanup_still_gated"] is True
    assert contract["stability_has_no_error"] is True
    assert contract["live_save_stability_ready"] is True
    assert contract["section_225_live_compile_api_fixed"] is True
    assert (
        contract["section_226_live_legacy_compile_helper_mismatch_documented"]
        is True
    )
    assert contract["section_227_live_partial_save_recovery_verified"] is True
    assert contract["section_228_live_idempotent_resave_verified"] is True
    assert contract["section_229_live_save_readback_schema_strengthened"] is True
    assert contract["section_230_live_dirty_package_stability_verified"] is True
    assert contract["section_231_live_production_path_untouched"] is True
    assert contract["section_232_live_delete_rename_cleanup_still_gated"] is True
    assert contract["final_durable_release_ready"] is True
    assert contract["save_asset_allowed"] is True
    assert contract["compile_save_allowed"] is True
    assert contract["cleanup_allowed"] is False
    assert contract["cleanup_executed"] is False
    assert contract["delete_asset_allowed"] is False
    assert contract["rename_asset_allowed"] is False
    assert contract["production_path_write_allowed"] is False
    assert contract["production_path_write_executed"] is False

    summary = (
        live_save_stability
        .summarize_durable_executor_authoring_live_save_stability_batches(
            [contract]
        )
    )
    assert summary["status"] == "passed"
    assert (
        summary[
            "durable_requested_executor_authoring_live_save_stability_batch_count"
        ]
        == 1
    )
    assert summary["section_217_224_actual_save_ready_count"] == 1
    assert summary["compile_api_fixed_count"] == 1
    assert summary["legacy_compile_helper_mismatch_documented_count"] == 1
    assert summary["partial_save_recovery_verified_count"] == 1
    assert summary["idempotent_resave_verified_count"] == 1
    assert summary["save_readback_schema_strengthened_count"] == 1
    assert summary["dirty_package_stability_verified_count"] == 1
    assert summary["production_path_untouched_count"] == 1
    assert summary["delete_rename_cleanup_still_gated_count"] == 1
    assert summary["live_save_stability_ready_count"] == 1
    assert summary["section_225_live_compile_api_fixed_count"] == 1
    assert (
        summary[
            "section_226_live_legacy_compile_helper_mismatch_documented_count"
        ]
        == 1
    )
    assert summary["section_227_live_partial_save_recovery_verified_count"] == 1
    assert summary["section_228_live_idempotent_resave_verified_count"] == 1
    assert summary["section_229_live_save_readback_schema_strengthened_count"] == 1
    assert summary["section_230_live_dirty_package_stability_verified_count"] == 1
    assert summary["section_231_live_production_path_untouched_count"] == 1
    assert summary["section_232_live_delete_rename_cleanup_still_gated_count"] == 1
    assert summary["final_durable_release_ready_count"] == 1
    assert summary["save_asset_allowed_count"] == 1
    assert summary["compile_save_allowed_count"] == 1
    assert summary["cleanup_allowed_count"] == 0
    assert summary["cleanup_executed_count"] == 0
    assert summary["delete_asset_allowed_count"] == 0
    assert summary["rename_asset_allowed_count"] == 0
    assert summary["production_path_write_allowed_count"] == 0
    assert summary["production_path_write_executed_count"] == 0

    missing_actual_save = dict(section_217_224_summary)
    missing_actual_save["section_224_final_durable_release_ready_count"] = 0
    missing_actual_save_contract = (
        live_save_stability
        .build_durable_executor_authoring_live_save_stability_batch_contract(
            True,
            missing_actual_save,
            stability_result,
        )
    )
    missing_actual_save_summary = (
        live_save_stability
        .summarize_durable_executor_authoring_live_save_stability_batches(
            [missing_actual_save_contract]
        )
    )
    assert missing_actual_save_contract["section_217_224_actual_save_ready"] is False
    assert missing_actual_save_contract["live_save_stability_ready"] is False
    assert missing_actual_save_contract["final_durable_release_ready"] is False
    assert missing_actual_save_summary["status"] == "failed"

    wrong_compile_api_contract = (
        live_save_stability
        .build_durable_executor_authoring_live_save_stability_batch_contract(
            True,
            section_217_224_summary,
            build_current_stability_result(
                compile_api_name="KismetEditorUtilities.compile_blueprint",
            ),
        )
    )
    wrong_compile_api_summary = (
        live_save_stability
        .summarize_durable_executor_authoring_live_save_stability_batches(
            [wrong_compile_api_contract]
        )
    )
    assert wrong_compile_api_contract["compile_api_fixed"] is False
    assert wrong_compile_api_contract["live_save_stability_ready"] is False
    assert wrong_compile_api_summary["status"] == "failed"

    dirty_stability_contract = (
        live_save_stability
        .build_durable_executor_authoring_live_save_stability_batch_contract(
            True,
            section_217_224_summary,
            build_current_stability_result(final_dirty_content_package_count=1),
        )
    )
    dirty_stability_summary = (
        live_save_stability
        .summarize_durable_executor_authoring_live_save_stability_batches(
            [dirty_stability_contract]
        )
    )
    assert dirty_stability_contract["dirty_package_stability_verified"] is False
    assert dirty_stability_contract["live_save_stability_ready"] is False
    assert dirty_stability_contract["delete_asset_allowed"] is False
    assert dirty_stability_summary["status"] == "failed"

    delete_attempt_contract = (
        live_save_stability
        .build_durable_executor_authoring_live_save_stability_batch_contract(
            True,
            section_217_224_summary,
            build_current_stability_result(delete_asset_called=True),
        )
    )
    delete_attempt_summary = (
        live_save_stability
        .summarize_durable_executor_authoring_live_save_stability_batches(
            [delete_attempt_contract]
        )
    )
    assert delete_attempt_contract["delete_rename_cleanup_still_gated"] is False
    assert delete_attempt_contract["live_save_stability_ready"] is False
    assert delete_attempt_contract["delete_asset_allowed"] is False
    assert delete_attempt_summary["status"] == "failed"

    production_touch_contract = (
        live_save_stability
        .build_durable_executor_authoring_live_save_stability_batch_contract(
            True,
            section_217_224_summary,
            build_current_stability_result(production_path_touched=True),
        )
    )
    production_touch_summary = (
        live_save_stability
        .summarize_durable_executor_authoring_live_save_stability_batches(
            [production_touch_contract]
        )
    )
    assert production_touch_contract["production_path_untouched"] is False
    assert production_touch_contract["live_save_stability_ready"] is False
    assert production_touch_contract["production_path_write_allowed"] is False
    assert production_touch_summary["status"] == "failed"

    print(
        "BP authoring durable executor authoring live save stability batch contract smoke passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
