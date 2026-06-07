#!/usr/bin/env python
"""Offline smoke tests for bp_authoring_release_boundary_report.py."""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import bp_authoring_release_boundary_report as release_boundary  # noqa: E402


def find_row(report: dict, row_id: str) -> dict:
    for item in report["regression_matrix"]:
        if item["id"] == row_id:
            return item
    raise AssertionError(f"missing row {row_id}")


def main() -> int:
    repo_root = SCRIPT_DIR.parents[2]
    with tempfile.TemporaryDirectory(prefix="mcp_release_boundary_fixture_") as temp_dir:
        project_root = Path(temp_dir)
        (project_root / "Content" / "_MCP_Temp" / "PlannerDrivenSmoke").mkdir(parents=True)
        report = release_boundary.build_report(repo_root=repo_root, project_root=project_root)
        assert report["schema"] == release_boundary.REPORT_SCHEMA
        assert report["verdict"]["status"] == "passed"
        assert report["verdict"]["ready_for_main_push"] is True
        assert report["verdict"]["durable_authoring_enabled"] is False
        assert find_row(report, "job_contract_default_request_set")["status"] == "passed"
        assert find_row(report, "manifest_executor_policy")["status"] == "passed"
        assert find_row(report, "executor_capability_matrix")["status"] == "passed"
        assert find_row(report, "durable_executor_gate_matrix")["status"] == "passed"
        enable_row = find_row(report, "durable_authoring_enable_contract")
        assert enable_row["status"] == "passed"
        assert enable_row["actual"]["enable_contract_satisfied_count"] == 0
        assert enable_row["actual"]["durable_executor_may_open_count"] == 0
        assert enable_row["actual"]["executor_gate_may_open_count"] == 0
        assert enable_row["actual"]["ownership_marker_passed_count"] == 1
        ownership_row = find_row(report, "durable_ownership_marker_contract")
        assert ownership_row["status"] == "passed"
        assert ownership_row["actual"]["durable_ownership_marker_policy_ready_count"] == 1
        assert ownership_row["actual"]["durable_ownership_delete_without_marker_allowed_count"] == 0
        assert ownership_row["actual"]["durable_ownership_delete_preexisting_asset_allowed_count"] == 0
        assert find_row(report, "planner_driven_live_smoke_report")["status"] == "passed"
        assert find_row(report, "durable_read_only_live_preflight")["status"] == "passed"
        assert find_row(report, "project_filesystem_side_effect_boundary")["status"] == "passed"
        output_dir = Path(temp_dir) / "out"
        json_path, md_path = release_boundary.write_report(report, output_dir)
        assert json_path.exists()
        assert md_path.exists()
    print("BP authoring release boundary smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
