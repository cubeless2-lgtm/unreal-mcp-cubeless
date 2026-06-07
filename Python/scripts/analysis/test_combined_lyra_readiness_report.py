#!/usr/bin/env python
"""Smoke tests for combined_lyra_readiness_report.py."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import combined_lyra_readiness_report as combined  # noqa: E402


def fixture_cpp_report() -> dict:
    return {
        "read_only_project_root": r"D:\Fixture\Lyra",
        "output_dir": r"D:\Fixture\Reports",
        "source_scan": {
            "file_count": 10,
            "config_file_count": 2,
            "readiness_by_file": {"supported_partial": 2, "blocked_native": 1},
            "risk_by_file": {"medium": 2, "critical": 1},
        },
        "readiness": {
            "supported_categories": [
                {
                    "key": "basic_actor_component_authoring",
                    "label": "Actor and component composition",
                    "hit_count": 5,
                    "file_count": 2,
                    "risk": "medium",
                    "note": "fixture",
                }
            ],
            "partial_categories": [
                {
                    "key": "common_ui_umg",
                    "label": "CommonUI and UMG",
                    "hit_count": 7,
                    "file_count": 3,
                    "risk": "high",
                    "note": "fixture",
                }
            ],
            "blocked_categories": [
                {
                    "key": "networking_replication",
                    "label": "Networking and replication",
                    "hit_count": 4,
                    "file_count": 1,
                    "risk": "critical",
                    "note": "fixture",
                }
            ],
        },
    }


def fixture_asset_report() -> dict:
    return {
        "read_only_project_root": r"D:\Fixture\Lyra",
        "output_dir": r"D:\Fixture\Reports",
        "summary": {
            "asset_count": 20,
            "blueprint_like_asset_count": 6,
            "supported_candidate_count": 2,
            "blocked_or_partial_blocked_count": 3,
            "category_counts": {
                "actor_blueprint": 2,
                "common_ui_umg": 2,
                "game_feature_or_experience": 1,
                "editor_utility_blueprint": 1,
            },
            "top_native_or_parent_classes": {"/Script/Engine.Actor": 2},
        },
    }


def fixture_delegate_report() -> dict:
    return {
        "output_dir": r"D:\Fixture\Reports",
        "source_scan": {
            "matched_file_count": 4,
            "pattern_totals": {
                "dynamic_binding": 2,
                "blueprint_assignable_delegate": 3,
                "delegate_unbinding": 1,
            },
            "readiness_by_file": {"partial_blocked": 3, "blocked_native": 1},
            "risk_by_file": {"high": 3, "critical": 1},
            "lifecycle_classifier": {
                "conversion_bucket_counts": {
                    "native_required": 2,
                    "requires_wrapper_api": 1,
                }
            },
            "async_proxy_inventory": {
                "summary": {
                    "class_count": 3,
                    "classes_requiring_callback_exec_model": 2,
                    "callback_delegate_count": 2,
                    "factory_function_count": 1,
                    "broadcast_count": 2,
                    "kind_counts": {
                        "blueprint_async_action": 1,
                        "ability_task": 1,
                        "custom_k2_async_node": 1,
                    },
                },
                "authoring_status": "inventory_only_until_async_proxy_callback_exec_model_exists",
            },
        },
        "mcp_capability_scan": {
            "identified_gaps": [
                "generic delegate bind/assign/event-dispatcher node authoring",
                "async proxy node authoring with callback exec pins",
            ]
        },
        "verdict": {
            "current_status": "not_ready_for_generic_delegate_or_async_proxy_authoring",
        },
    }


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="mcp_combined_readiness_fixture_") as temp_dir:
        output_dir = Path(temp_dir) / "out"
        report = combined.build_combined(
            fixture_cpp_report(),
            fixture_asset_report(),
            output_dir,
            fixture_delegate_report(),
        )
        json_path, md_path = combined.write_report(report, output_dir)

        assert json_path.exists()
        assert md_path.exists()
        assert report["verdict"]["editor_open_required_now"] is False
        assert report["asset_summary"]["supported_asset_categories"]["actor_blueprint"] == 2
        assert report["asset_summary"]["blocked_asset_categories"]["game_feature_or_experience"] == 1
        assert report["delegate_async_summary"]["matched_files"] == 4
        assert report["delegate_async_summary"]["pattern_totals"]["dynamic_binding"] == 2
        assert report["delegate_async_summary"]["async_proxy_inventory"]["summary"]["class_count"] == 3
        assert "6 delegate bind/assign/unbind triggers" in report["next_reinforcement_candidates"][0]["why"]
        assert "2 async proxy classes" in report["next_reinforcement_candidates"][0]["why"]
        assert "networking_replication" in report["cpp_summary"]["blocked_categories"]
    print("combined Lyra readiness report smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
