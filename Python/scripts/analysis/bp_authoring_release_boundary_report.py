#!/usr/bin/env python
"""
Section 49-50 Blueprint authoring regression matrix and release boundary report.

The report does not run live Unreal authoring. It reads the current analysis
reports and rebuilds the offline manifest/executor matrix so the release
boundary is explicit before publishing BP authoring changes.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import bp_authoring_job_contract as job_contract
import bp_authoring_manifest_executor as manifest_executor


REPORT_SCHEMA = "section_49_50_bp_authoring_release_boundary_v1"
ANALYSIS_KIND = "bp_authoring_release_boundary"


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def read_json(path: Path) -> Optional[Dict[str, Any]]:
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def row(
    row_id: str,
    label: str,
    passed: bool,
    expected: Dict[str, Any],
    actual: Dict[str, Any],
    blocking: bool = True,
    notes: Iterable[str] = (),
) -> Dict[str, Any]:
    return {
        "id": row_id,
        "label": label,
        "status": "passed" if passed else "failed",
        "blocking": blocking,
        "expected": expected,
        "actual": actual,
        "notes": list(notes),
    }


def missing_row(row_id: str, label: str, path: Path) -> Dict[str, Any]:
    return row(
        row_id,
        label,
        passed=False,
        expected={"report_exists": True},
        actual={"report_exists": False, "path": str(path)},
        notes=("regenerate the required analysis report before release review",),
    )


def default_manifests() -> List[Dict[str, Any]]:
    return [
        job_contract.build_job_manifest(request_id, request, temp_package_path=job_contract.DEFAULT_TEMP_PACKAGE_PATH)
        for request_id, request in job_contract.DEFAULT_SAMPLE_REQUESTS
    ]


def build_contract_matrix_row(contract_summary: Dict[str, Any]) -> Dict[str, Any]:
    expected = {
        "manifest_count": 19,
        "executable_manifest_count": 12,
        "non_executable_manifest_count": 7,
        "non_safe_authoring_command_count": 0,
        "durable_authoring_request_count": 1,
        "durable_authoring_eligible_count": 0,
    }
    actual = {key: contract_summary.get(key) for key in expected}
    return row(
        "job_contract_default_request_set",
        "Section 12-39 job contract default request set",
        passed=actual == expected,
        expected=expected,
        actual=actual,
    )


def build_executor_matrix_row(executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    expected = {
        "executable_by_executor_count": 12,
        "blocked_by_executor_count": 7,
        "save_step_count": 0,
        "unknown_command_count": 0,
        "forbidden_command_count": 0,
        "durable_authoring_allowed": False,
        "save_allowed": False,
    }
    actual = {key: executor_summary.get(key) for key in expected}
    return row(
        "manifest_executor_policy",
        "Section 40-41 temporary manifest executor policy",
        passed=actual == expected,
        expected=expected,
        actual=actual,
    )


def build_capability_matrix_row(executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    expected_ready = {
        "typed_defaults": 5,
        "graph_layout_dataflow": 11,
        "function_graph_executor": 5,
        "dispatcher_lifecycle_executor": 1,
    }
    capability_summary = executor_summary.get("capability_summary", {})
    actual = {
        key: {
            "requested": capability_summary.get(key, {}).get("requested_manifest_count"),
            "ready": capability_summary.get(key, {}).get("ready_manifest_count"),
            "missing": capability_summary.get(key, {}).get("missing_evidence_manifest_count"),
        }
        for key in expected_ready
    }
    passed = all(
        actual[key]["requested"] == expected_ready[key]
        and actual[key]["ready"] == expected_ready[key]
        and actual[key]["missing"] == 0
        for key in expected_ready
    )
    return row(
        "executor_capability_matrix",
        "Section 42-45 executor capability matrix",
        passed=passed,
        expected={key: {"requested": value, "ready": value, "missing": 0} for key, value in expected_ready.items()},
        actual=actual,
    )


def build_durable_gate_matrix_row(executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    expected = {
        "status": "passed",
        "durable_requested_manifest_count": 1,
        "read_only_live_preflight_allowed_count": 1,
        "durable_executor_enabled_count": 0,
        "durable_executor_executable_count": 0,
        "allowed_live_authoring_command_count": 0,
        "contract_save_allowed_count": 0,
        "save_or_delete_commands_allowed_count": 0,
        "preflight_pass_count": 0,
    }
    durable_summary = executor_summary.get("durable_gate_summary", {})
    actual = {key: durable_summary.get(key) for key in expected}
    return row(
        "durable_executor_gate_matrix",
        "Section 46-48 durable executor gate matrix",
        passed=actual == expected,
        expected=expected,
        actual=actual,
    )


def build_durable_enable_contract_row(contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    enable_summary = contract_summary.get("durable_enable_contract_summary", {})
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "summary_status": "passed",
        "durable_requested_manifest_count": 1,
        "enable_contract_satisfied_count": 0,
        "durable_executor_may_open_count": 0,
        "durable_authoring_allowed_count": 0,
        "forbidden_command_allowed_count": 0,
        "target_package_allowlist_passed_count": 1,
        "overwrite_rename_decision_passed_count": 0,
        "rollback_readiness_passed_count": 0,
        "ownership_marker_passed_count": 1,
        "executor_gate_may_open_count": 0,
    }
    actual = {
        "summary_status": enable_summary.get("status"),
        "durable_requested_manifest_count": enable_summary.get("durable_requested_manifest_count"),
        "enable_contract_satisfied_count": enable_summary.get("enable_contract_satisfied_count"),
        "durable_executor_may_open_count": enable_summary.get("durable_executor_may_open_count"),
        "durable_authoring_allowed_count": enable_summary.get("durable_authoring_allowed_count"),
        "forbidden_command_allowed_count": enable_summary.get("forbidden_command_allowed_count"),
        "target_package_allowlist_passed_count": enable_summary.get("target_package_allowlist_passed_count"),
        "overwrite_rename_decision_passed_count": enable_summary.get("overwrite_rename_decision_passed_count"),
        "rollback_readiness_passed_count": enable_summary.get("rollback_readiness_passed_count"),
        "ownership_marker_passed_count": enable_summary.get("ownership_marker_passed_count"),
        "executor_gate_may_open_count": durable_gate_summary.get("durable_enable_executor_may_open_count"),
    }
    return row(
        "durable_authoring_enable_contract",
        "Section 51 durable authoring enable contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Section 51 separates target allowlist, overwrite/rename, rollback readiness, and ownership marker gates.",
            "It does not enable durable save/delete/rename/live authoring.",
        ),
    )


def build_durable_ownership_marker_row(contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "durable_ownership_marker_request_count": 1,
        "durable_ownership_marker_policy_ready_count": 1,
        "durable_ownership_delete_without_marker_allowed_count": 0,
        "durable_ownership_delete_preexisting_asset_allowed_count": 0,
        "executor_gate_ownership_marker_policy_ready_count": 1,
        "executor_gate_delete_without_marker_allowed_count": 0,
        "executor_gate_delete_preexisting_asset_allowed_count": 0,
    }
    actual = {
        "durable_ownership_marker_request_count": contract_summary.get("durable_ownership_marker_request_count"),
        "durable_ownership_marker_policy_ready_count": contract_summary.get(
            "durable_ownership_marker_policy_ready_count"
        ),
        "durable_ownership_delete_without_marker_allowed_count": contract_summary.get(
            "durable_ownership_delete_without_marker_allowed_count"
        ),
        "durable_ownership_delete_preexisting_asset_allowed_count": contract_summary.get(
            "durable_ownership_delete_preexisting_asset_allowed_count"
        ),
        "executor_gate_ownership_marker_policy_ready_count": durable_gate_summary.get("ownership_marker_policy_ready_count"),
        "executor_gate_delete_without_marker_allowed_count": durable_gate_summary.get(
            "delete_without_ownership_marker_allowed_count"
        ),
        "executor_gate_delete_preexisting_asset_allowed_count": durable_gate_summary.get(
            "delete_preexisting_asset_allowed_count"
        ),
    }
    return row(
        "durable_ownership_marker_contract",
        "Section 52 durable rollback ownership marker contract",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Rollback/delete is authorized only for executor-created assets with a matching ownership marker.",
            "Section 52 still does not execute delete or durable save commands.",
        ),
    )


def build_durable_dry_run_plan_row(contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    dry_run_summary = contract_summary.get("durable_dry_run_plan_summary", {})
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "summary_status": "passed",
        "durable_requested_plan_count": 1,
        "dry_run_plan_created_count": 1,
        "dry_run_plan_valid_count": 1,
        "durable_executor_may_execute_count": 0,
        "live_command_count": 0,
        "forbidden_command_allowed_count": 0,
        "executor_gate_dry_run_plan_created_count": 1,
        "executor_gate_dry_run_plan_valid_count": 1,
        "executor_gate_dry_run_may_execute_count": 0,
        "executor_gate_dry_run_live_command_count": 0,
    }
    actual = {
        "summary_status": dry_run_summary.get("status"),
        "durable_requested_plan_count": dry_run_summary.get("durable_requested_plan_count"),
        "dry_run_plan_created_count": dry_run_summary.get("dry_run_plan_created_count"),
        "dry_run_plan_valid_count": dry_run_summary.get("dry_run_plan_valid_count"),
        "durable_executor_may_execute_count": dry_run_summary.get("durable_executor_may_execute_count"),
        "live_command_count": dry_run_summary.get("live_command_count"),
        "forbidden_command_allowed_count": dry_run_summary.get("forbidden_command_allowed_count"),
        "executor_gate_dry_run_plan_created_count": durable_gate_summary.get("dry_run_plan_created_count"),
        "executor_gate_dry_run_plan_valid_count": durable_gate_summary.get("dry_run_plan_valid_count"),
        "executor_gate_dry_run_may_execute_count": durable_gate_summary.get("dry_run_plan_executor_may_execute_count"),
        "executor_gate_dry_run_live_command_count": durable_gate_summary.get("dry_run_plan_live_command_count"),
    }
    return row(
        "durable_executor_dry_run_plan",
        "Section 53 durable executor dry-run plan",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Dry-run plan records durable execution intent without live commands.",
            "Execution command plan must remain empty until a later durable release.",
        ),
    )


def build_durable_save_simulator_row(contract_summary: Dict[str, Any], executor_summary: Dict[str, Any]) -> Dict[str, Any]:
    save_summary = contract_summary.get("durable_save_simulation_summary", {})
    durable_gate_summary = executor_summary.get("durable_gate_summary", {})
    expected = {
        "summary_status": "passed",
        "durable_requested_simulation_count": 1,
        "simulation_evaluated_count": 1,
        "future_save_conditions_satisfied_count": 0,
        "save_true_allowed_count": 0,
        "save_asset_allowed_count": 0,
        "compile_save_command_allowed_count": 0,
        "live_command_count": 0,
        "executor_gate_simulation_evaluated_count": 1,
        "executor_gate_conditions_satisfied_count": 0,
        "executor_gate_save_true_allowed_count": 0,
        "executor_gate_save_asset_allowed_count": 0,
        "executor_gate_live_command_count": 0,
    }
    actual = {
        "summary_status": save_summary.get("status"),
        "durable_requested_simulation_count": save_summary.get("durable_requested_simulation_count"),
        "simulation_evaluated_count": save_summary.get("simulation_evaluated_count"),
        "future_save_conditions_satisfied_count": save_summary.get("future_save_conditions_satisfied_count"),
        "save_true_allowed_count": save_summary.get("save_true_allowed_count"),
        "save_asset_allowed_count": save_summary.get("save_asset_allowed_count"),
        "compile_save_command_allowed_count": save_summary.get("compile_save_command_allowed_count"),
        "live_command_count": save_summary.get("live_command_count"),
        "executor_gate_simulation_evaluated_count": durable_gate_summary.get("save_simulation_evaluated_count"),
        "executor_gate_conditions_satisfied_count": durable_gate_summary.get(
            "save_simulation_conditions_satisfied_count"
        ),
        "executor_gate_save_true_allowed_count": durable_gate_summary.get("save_simulation_save_true_allowed_count"),
        "executor_gate_save_asset_allowed_count": durable_gate_summary.get("save_simulation_save_asset_allowed_count"),
        "executor_gate_live_command_count": durable_gate_summary.get("save_simulation_live_command_count"),
    }
    return row(
        "durable_save_validation_simulator",
        "Section 54 durable save validation simulator",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=(
            "Simulator evaluates save prerequisites without save=true or save_asset.",
            "Failed conditions must keep durable save closed.",
        ),
    )


def build_planner_live_rows(planner_report_path: Path, planner_report: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    if planner_report is None:
        return [missing_row("planner_driven_live_smoke_report", "Planner-driven live smoke report", planner_report_path)]
    verdict = planner_report.get("verdict", {})
    live_gate = planner_report.get("live_gate", {})
    preflight_gate = live_gate.get("durable_live_preflight_gate", {})
    smoke_expected = {
        "verdict_status": "passed",
        "safe_requests_queued": 12,
        "non_safe_requests_prevented": 7,
        "executor_executable_manifests": 12,
    }
    smoke_actual = {
        "verdict_status": verdict.get("status"),
        "safe_requests_queued": verdict.get("safe_requests_queued"),
        "non_safe_requests_prevented": verdict.get("non_safe_requests_prevented"),
        "executor_executable_manifests": verdict.get("executor_executable_manifests"),
    }
    cleanup_expected = {
        "generated_leftovers": 0,
        "new_log_errors": 0,
        "durable_authoring_attempted": False,
        "durable_live_save_or_delete_attempted": False,
    }
    cleanup_actual = {
        "generated_leftovers": len(live_gate.get("generated_leftovers", [])),
        "new_log_errors": len(live_gate.get("new_log_errors", [])),
        "durable_authoring_attempted": live_gate.get("durable_authoring_attempted"),
        "durable_live_save_or_delete_attempted": live_gate.get("durable_live_save_or_delete_attempted"),
    }
    preflight_expected = {
        "status": "passed",
        "live_result_count": 1,
        "passed_read_only_result_count": 1,
        "authoring_attempted_count": 0,
        "save_or_delete_attempted_count": 0,
        "preflight_pass_count": 0,
    }
    preflight_actual = {key: preflight_gate.get(key) for key in preflight_expected}
    return [
        row(
            "planner_driven_live_smoke_report",
            "Planner-driven live smoke report",
            passed=smoke_actual == smoke_expected,
            expected=smoke_expected,
            actual=smoke_actual,
        ),
        row(
            "planner_live_cleanup_and_log_boundary",
            "Planner live cleanup and log boundary",
            passed=cleanup_actual == cleanup_expected,
            expected=cleanup_expected,
            actual=cleanup_actual,
        ),
        row(
            "durable_read_only_live_preflight",
            "Durable read-only live preflight boundary",
            passed=preflight_actual == preflight_expected,
            expected=preflight_expected,
            actual=preflight_actual,
        ),
    ]


def build_quality_gate_row(quality_report_path: Path, quality_report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if quality_report is None:
        return missing_row("bp_authoring_quality_gate_live_report", "BP authoring quality gate live report", quality_report_path)
    expected = {
        "verdict_status": "existing_bp_authoring_quality_gate_passed",
        "live_status": "passed",
        "cxx_changes_required_for_this_gate": False,
    }
    actual = {
        "verdict_status": quality_report.get("verdict", {}).get("status"),
        "live_status": quality_report.get("live_gate", {}).get("status"),
        "cxx_changes_required_for_this_gate": quality_report.get("verdict", {}).get(
            "cxx_changes_required_for_this_gate"
        ),
    }
    return row(
        "bp_authoring_quality_gate_live_report",
        "BP authoring quality gate live report",
        passed=actual == expected,
        expected=expected,
        actual=actual,
    )


def build_lyra_boundary_row(lyra_report_path: Path, lyra_report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if lyra_report is None:
        return missing_row("lyra_readiness_boundary", "Lyra readiness boundary report", lyra_report_path)
    verdict = lyra_report.get("verdict", {})
    ceiling = verdict.get("current_authoring_ceiling", "")
    not_ready_for = verdict.get("not_ready_for", [])
    actual = {
        "minimum_stable_scope": verdict.get("minimum_stable_scope"),
        "ceiling_mentions_temporary_smoke": "temporary_smoke_only" in ceiling,
        "editor_open_required_now": verdict.get("editor_open_required_now"),
        "not_ready_for_count": len(not_ready_for),
    }
    expected = {
        "minimum_stable_scope": "readiness_classification_and_candidate_selection",
        "ceiling_mentions_temporary_smoke": True,
        "editor_open_required_now": False,
        "not_ready_for_count_at_least": 1,
    }
    passed = (
        actual["minimum_stable_scope"] == expected["minimum_stable_scope"]
        and actual["ceiling_mentions_temporary_smoke"] is True
        and actual["editor_open_required_now"] is False
        and actual["not_ready_for_count"] >= expected["not_ready_for_count_at_least"]
    )
    return row(
        "lyra_readiness_boundary",
        "Lyra readiness and authoring ceiling boundary",
        passed=passed,
        expected=expected,
        actual=actual,
    )


def collect_project_filesystem_boundary(project_root: Path) -> Dict[str, Any]:
    temp_root = project_root / "Content" / "_MCP_Temp" / "PlannerDrivenSmoke"
    generated_leftovers = []
    if temp_root.exists():
        generated_leftovers = [str(path) for path in temp_root.rglob("*") if "MCP_PlannerSmoke_" in path.name]
    durable_asset = project_root / "Content" / "MCPTestFixtures" / "BP_PlannerDurable.uasset"
    actual = {
        "project_root_exists": project_root.exists(),
        "generated_planner_smoke_leftovers": len(generated_leftovers),
        "durable_test_asset_exists": durable_asset.exists(),
    }
    expected = {
        "project_root_exists": True,
        "generated_planner_smoke_leftovers": 0,
        "durable_test_asset_exists": False,
    }
    return row(
        "project_filesystem_side_effect_boundary",
        "Project filesystem side-effect boundary",
        passed=actual == expected,
        expected=expected,
        actual=actual,
        notes=generated_leftovers[:5],
    )


def build_report(repo_root: Optional[Path] = None, project_root: Optional[Path] = None) -> Dict[str, Any]:
    repo_root = repo_root or repo_root_from_script()
    project_root = project_root or repo_root.parent / "CubelessStylized"
    reports_root = repo_root / "Docs" / "Analysis"
    planner_report_path = reports_root / "PlannerDrivenSmoke" / "planner_driven_bp_authoring_smoke_report.json"
    quality_report_path = reports_root / "BPAuthoringQualityGate" / "bp_authoring_quality_gate_report.json"
    lyra_report_path = reports_root / "Lyra" / "lyra_combined_readiness_report.json"

    manifests = default_manifests()
    contract_summary = job_contract.summarize_manifests(manifests)
    executor_summary = manifest_executor.summarize_executor_policies(manifests, job_contract.DEFAULT_TEMP_PACKAGE_PATH)
    planner_report = read_json(planner_report_path)
    quality_report = read_json(quality_report_path)
    lyra_report = read_json(lyra_report_path)

    matrix = [
        build_contract_matrix_row(contract_summary),
        build_executor_matrix_row(executor_summary),
        build_capability_matrix_row(executor_summary),
        build_durable_gate_matrix_row(executor_summary),
        build_durable_enable_contract_row(contract_summary, executor_summary),
        build_durable_ownership_marker_row(contract_summary, executor_summary),
        build_durable_dry_run_plan_row(contract_summary, executor_summary),
        build_durable_save_simulator_row(contract_summary, executor_summary),
        *build_planner_live_rows(planner_report_path, planner_report),
        build_quality_gate_row(quality_report_path, quality_report),
        build_lyra_boundary_row(lyra_report_path, lyra_report),
        collect_project_filesystem_boundary(project_root),
    ]
    failed_blocking = [item for item in matrix if item["blocking"] and item["status"] != "passed"]
    return {
        "schema": REPORT_SCHEMA,
        "analysis_kind": ANALYSIS_KIND,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "repo_root": str(repo_root),
        "project_root": str(project_root),
        "report_inputs": {
            "planner_driven_smoke": str(planner_report_path),
            "bp_authoring_quality_gate": str(quality_report_path),
            "lyra_combined_readiness": str(lyra_report_path),
        },
        "regression_matrix": matrix,
        "verdict": {
            "status": "passed" if not failed_blocking else "failed",
            "failed_blocking_count": len(failed_blocking),
            "failed_blocking_ids": [item["id"] for item in failed_blocking],
            "ready_for_main_push": not failed_blocking,
            "durable_authoring_enabled": False,
            "durable_authoring_release_status": "not_enabled_read_only_preflight_only",
            "current_authoring_ceiling": (
                "planner_safe_temporary_manifest_execution_with_structural_validation_durable_read_only_preflight_section_51_enable_contract_section_52_ownership_marker_section_53_dry_run_plan_and_section_54_save_simulator"
            ),
            "cxx_changes_required": False,
        },
        "next_reinforcement_candidates": [
            "limited durable canary prep after Section 54 simulator remains no-command",
            "component default/type readback expansion for broader Blueprint classes",
            "function call diagnostics and graph layout repair suggestions",
            "UMG/CommonUI authoring classifier and non-executable manifest coverage",
        ],
    }


def render_markdown(report: Dict[str, Any]) -> str:
    verdict = report["verdict"]
    lines = [
        "# BP Authoring Release Boundary",
        "",
        f"- Generated UTC: `{report['generated_at']}`",
        f"- Schema: `{report['schema']}`",
        f"- Status: `{verdict['status']}`",
        f"- Ready for main push: `{verdict['ready_for_main_push']}`",
        f"- Durable authoring enabled: `{verdict['durable_authoring_enabled']}`",
        f"- Durable release status: `{verdict['durable_authoring_release_status']}`",
        f"- Current authoring ceiling: `{verdict['current_authoring_ceiling']}`",
        "",
        "## Regression Matrix",
        "",
    ]
    for item in report["regression_matrix"]:
        lines.append(
            f"- `{item['status']}` `{item['id']}` blocking=`{item['blocking']}` - {item['label']}"
        )
        if item["status"] != "passed":
            lines.append(f"  - expected: `{json.dumps(item['expected'], sort_keys=True)}`")
            lines.append(f"  - actual: `{json.dumps(item['actual'], sort_keys=True)}`")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "This boundary permits temporary planner-safe manifest execution only. Section 51 records the durable authoring enable contract, but durable Blueprint creation, saving, delete, and rename remain disabled until a later explicit durable release.",
            "",
            "## Next Reinforcement Candidates",
            "",
        ]
    )
    lines.extend(f"- {item}" for item in report["next_reinforcement_candidates"])
    return "\n".join(lines) + "\n"


def write_report(report: Dict[str, Any], output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "bp_authoring_release_boundary_report.json"
    md_path = output_dir / "bp_authoring_release_boundary_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_arg_parser() -> argparse.ArgumentParser:
    repo_root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", default=str(repo_root / "Docs" / "Analysis" / "BPAuthoringReleaseBoundary"))
    parser.add_argument("--project-root", default=str(repo_root.parent / "CubelessStylized"))
    parser.add_argument("--no-write", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    report = build_report(project_root=Path(args.project_root).resolve())
    if not args.no_write:
        json_path, md_path = write_report(report, Path(args.output_dir).resolve())
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    print(f"Release boundary status: {report['verdict']['status']}")
    print(f"Failed blocking rows: {report['verdict']['failed_blocking_count']}")
    return 0 if report["verdict"]["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
