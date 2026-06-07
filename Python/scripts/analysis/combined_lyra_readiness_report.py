#!/usr/bin/env python
"""Combine Lyra C++ readiness and Blueprint asset ancestry reports."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

import external_project_readiness_analyzer as base


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def build_combined(
    cpp_report: Dict[str, Any],
    asset_report: Dict[str, Any],
    output_dir: Path,
    delegate_report: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    source_scan = cpp_report["source_scan"]
    cpp_readiness = cpp_report["readiness"]
    asset_summary = asset_report["summary"]

    supported_asset_categories = {
        key: value
        for key, value in asset_summary["category_counts"].items()
        if key in {"actor_blueprint", "component_blueprint", "blueprint_function_library", "enhanced_input_asset"}
    }
    dedicated_asset_categories = {
        key: value
        for key, value in asset_summary["category_counts"].items()
        if key
        in {
            "common_ui_umg",
            "gameplay_ability",
            "gameplay_effect",
            "gameplay_cue",
            "animation_blueprint",
            "data_asset",
            "blueprint_interface",
            "framework_blueprint",
            "unknown_blueprint",
        }
    }
    blocked_asset_categories = {
        key: value
        for key, value in asset_summary["category_counts"].items()
        if key in {"game_feature_or_experience", "editor_utility_blueprint"}
    }

    cpp_blockers = {
        item["key"]: {
            "label": item["label"],
            "hit_count": item["hit_count"],
            "file_count": item["file_count"],
            "risk": item["risk"],
            "note": item["note"],
        }
        for item in cpp_readiness["blocked_categories"]
    }
    cpp_partial = {
        item["key"]: {
            "label": item["label"],
            "hit_count": item["hit_count"],
            "file_count": item["file_count"],
            "risk": item["risk"],
            "note": item["note"],
        }
        for item in cpp_readiness["partial_categories"]
    }
    cpp_supported = {
        item["key"]: {
            "label": item["label"],
            "hit_count": item["hit_count"],
            "file_count": item["file_count"],
            "risk": item["risk"],
            "note": item["note"],
        }
        for item in cpp_readiness["supported_categories"]
    }

    verdict = {
        "minimum_stable_scope": "readiness_classification_and_candidate_selection",
        "current_authoring_ceiling": "temporary_smoke_only_bp_shells_allowlisted_actor_parent_component_hierarchy_property_graph_glue_validation_durable_read_only_asset_exists_preflight_overwrite_rename_decision_save_gate_rollback_draft_executor_readiness_checklist_and_disabled_executor_skeleton",
        "not_ready_for": [
            "whole-project C++ to Blueprint conversion",
            "replication/RPC/ReplicationGraph lowering",
            "Gameplay Ability System internals and ability-task flow",
            "CommonUI widget tree and activation-policy authoring",
            "Animation Blueprint graph/state-machine conversion",
            "GameFeature activation and experience architecture recreation",
            "custom K2/editor-only/Slate behavior recreation",
        ],
        "editor_open_required_now": False,
        "editor_open_reason": "Static class ancestry extraction found high-confidence ParentClass/NativeParentClass tags for Blueprint-like assets.",
    }

    delegate_summary: Dict[str, Any] = {}
    if delegate_report:
        delegate_scan = delegate_report["source_scan"]
        delegate_summary = {
            "status": delegate_report["verdict"]["current_status"],
            "matched_files": delegate_scan["matched_file_count"],
            "pattern_totals": delegate_scan["pattern_totals"],
            "readiness_by_file": delegate_scan["readiness_by_file"],
            "risk_by_file": delegate_scan["risk_by_file"],
            "lifecycle_classifier": delegate_scan.get("lifecycle_classifier", {}),
            "async_proxy_inventory": delegate_scan.get("async_proxy_inventory", {}),
            "mcp_gaps": delegate_report["mcp_capability_scan"]["identified_gaps"],
        }

    delegate_trigger_count = 0
    lifecycle_native_or_wrapper_count = 0
    async_callback_class_count = 0
    if delegate_summary:
        totals = delegate_summary["pattern_totals"]
        delegate_trigger_count = (
            totals.get("dynamic_binding", 0)
            + totals.get("blueprint_assignable_delegate", 0)
            + totals.get("delegate_unbinding", 0)
        )
        lifecycle_buckets = delegate_summary.get("lifecycle_classifier", {}).get("conversion_bucket_counts", {})
        lifecycle_native_or_wrapper_count = (
            lifecycle_buckets.get("native_required", 0)
            + lifecycle_buckets.get("requires_wrapper_api", 0)
            + lifecycle_buckets.get("requires_explicit_unbind_policy", 0)
        )
        async_summary = delegate_summary.get("async_proxy_inventory", {}).get("summary", {})
        async_callback_class_count = async_summary.get("classes_requiring_callback_exec_model", 0)

    next_candidates = [
        {
            "priority": 1,
            "name": "Native/arbitrary delegate lifecycle and async callback primitives",
            "why": (
                f"Lyra source shows {delegate_trigger_count} delegate bind/assign/unbind triggers, {lifecycle_native_or_wrapper_count} lifecycle sites that still require native retention, wrapper APIs, or explicit unbind policy, and {async_callback_class_count} async proxy classes requiring callback exec or native policy; Blueprint Event Dispatcher lifecycle is now covered, but native delegates, arbitrary delegate targets, and async callback topology still need reinforcement."
                if delegate_summary
                else "Lyra source and asset ancestry both show async/delegate-heavy workflows; Blueprint Event Dispatcher lifecycle is now covered, but native delegates, arbitrary delegate targets, and async callback topology still need reinforcement."
            ),
        },
        {
            "priority": 2,
            "name": "CommonUI/UMG structure inventory",
            "why": f"Asset ancestry found {asset_summary['category_counts'].get('common_ui_umg', 0)} CommonUI/UMG Blueprint-like assets.",
        },
        {
            "priority": 3,
            "name": "GameplayAbility-specific classifier",
            "why": f"Asset ancestry found {asset_summary['category_counts'].get('gameplay_ability', 0)} ability Blueprints plus GAS-heavy C++ patterns.",
        },
        {
            "priority": 4,
            "name": "Animation Blueprint read-only graph inventory",
            "why": f"Asset ancestry found {asset_summary['category_counts'].get('animation_blueprint', 0)} animation-related Blueprint assets; current MCP generic graph tools are not AnimGraph tools.",
        },
        {
            "priority": 5,
            "name": "Optional Editor Asset Registry verification",
            "why": "Use only if exact Unreal AssetRegistry class names or Blueprint graph counts are needed beyond static package tag extraction.",
        },
    ]

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_kind": "combined_lyra_bp_authoring_readiness",
        "output_dir": str(output_dir),
        "inputs": {
            "cpp_readiness_report": cpp_report.get("output_dir", ""),
            "asset_ancestry_report": asset_report.get("output_dir", ""),
            "delegate_async_report": delegate_report.get("output_dir", "") if delegate_report else "",
            "project_root": cpp_report.get("read_only_project_root") or asset_report.get("read_only_project_root", ""),
        },
        "verdict": verdict,
        "cpp_summary": {
            "source_files": source_scan["file_count"],
            "config_files": source_scan["config_file_count"],
            "readiness_by_file": source_scan["readiness_by_file"],
            "risk_by_file": source_scan["risk_by_file"],
            "supported_categories": cpp_supported,
            "partial_categories": cpp_partial,
            "blocked_categories": cpp_blockers,
        },
        "asset_summary": {
            "asset_count": asset_summary["asset_count"],
            "blueprint_like_asset_count": asset_summary["blueprint_like_asset_count"],
            "supported_candidate_count": asset_summary["supported_candidate_count"],
            "blocked_or_partial_blocked_count": asset_summary["blocked_or_partial_blocked_count"],
            "supported_asset_categories": supported_asset_categories,
            "dedicated_support_asset_categories": dedicated_asset_categories,
            "blocked_asset_categories": blocked_asset_categories,
            "top_parent_classes": asset_summary["top_native_or_parent_classes"],
        },
        "delegate_async_summary": delegate_summary,
        "next_reinforcement_candidates": next_candidates,
        "read_only_policy": {
            "lyra_project_mutation_allowed": False,
            "editor_opened_for_this_combined_report": False,
            "inputs_are_existing_reports": True,
        },
    }


def format_count_map(data: Dict[str, Any], limit: int = 20) -> str:
    if not data:
        return "- none\n"
    lines = []
    for index, (key, value) in enumerate(data.items()):
        if index >= limit:
            lines.append(f"- ... {len(data) - limit} more")
            break
        lines.append(f"- `{key}`: {value}")
    return "\n".join(lines) + "\n"


def render_markdown(report: Dict[str, Any]) -> str:
    verdict = report["verdict"]
    cpp = report["cpp_summary"]
    assets = report["asset_summary"]
    delegate = report.get("delegate_async_summary", {})
    lines = [
        "# Lyra Combined BP Authoring Readiness",
        "",
        f"- Generated UTC: `{report['generated_at']}`",
        f"- Project root: `{report['inputs']['project_root']}`",
        f"- Minimum stable scope: `{verdict['minimum_stable_scope']}`",
        f"- Current authoring ceiling: `{verdict['current_authoring_ceiling']}`",
        f"- Editor open required now: `{verdict['editor_open_required_now']}`",
        f"- Editor decision: {verdict['editor_open_reason']}",
        "",
        "## Combined Verdict",
        "",
        "The current UnrealMCP BP authoring surface is ready for candidate selection and narrow BP shell/graph-glue experiments, not for full Lyra C++ to BP conversion.",
        "",
        "## C++ Intake Summary",
        "",
        f"- Source files: `{cpp['source_files']}`",
        f"- Config files: `{cpp['config_files']}`",
        "",
        "### Supported C++ Pattern Categories",
        "",
        format_count_map({key: value["hit_count"] for key, value in cpp["supported_categories"].items()}),
        "### Partial C++ Pattern Categories",
        "",
        format_count_map({key: value["hit_count"] for key, value in cpp["partial_categories"].items()}),
        "### Native-Blocked C++ Pattern Categories",
        "",
        format_count_map({key: value["hit_count"] for key, value in cpp["blocked_categories"].items()}),
        "## Asset Ancestry Summary",
        "",
        f"- Assets scanned: `{assets['asset_count']}`",
        f"- Blueprint-like assets: `{assets['blueprint_like_asset_count']}`",
        f"- Supported partial candidates: `{assets['supported_candidate_count']}`",
        f"- Blocked or partial-blocked Blueprint-like assets: `{assets['blocked_or_partial_blocked_count']}`",
        "",
        "### Supported Asset Categories",
        "",
        format_count_map(assets["supported_asset_categories"]),
        "### Dedicated-Support Asset Categories",
        "",
        format_count_map(assets["dedicated_support_asset_categories"]),
        "### Blocked Asset Categories",
        "",
        format_count_map(assets["blocked_asset_categories"]),
    ]
    lines.extend(["## Delegate / Latent / Async Summary", ""])
    if delegate:
        async_inventory = delegate.get("async_proxy_inventory", {})
        async_summary = async_inventory.get("summary", {})
        lines.extend(
            [
                f"- Status: `{delegate['status']}`",
                f"- Matched source files: `{delegate['matched_files']}`",
                "",
                "### Delegate Pattern Totals",
                "",
                format_count_map(delegate["pattern_totals"]),
                "### Delegate Lifecycle Buckets",
                "",
                format_count_map(delegate.get("lifecycle_classifier", {}).get("conversion_bucket_counts", {})),
                "### Async Proxy Inventory",
                "",
                f"- Async proxy classes: `{async_summary.get('class_count', 0)}`",
                f"- Classes requiring callback exec/native policy: `{async_summary.get('classes_requiring_callback_exec_model', 0)}`",
                f"- Callback delegates: `{async_summary.get('callback_delegate_count', 0)}`",
                f"- Factory functions: `{async_summary.get('factory_function_count', 0)}`",
                f"- Broadcast sites: `{async_summary.get('broadcast_count', 0)}`",
                f"- Authoring status: `{async_inventory.get('authoring_status', 'inventory_only')}`",
                "",
                "#### Async Class Kinds",
                "",
                format_count_map(async_summary.get("kind_counts", {})),
                "### Delegate MCP Gaps",
                "",
            ]
        )
        lines.extend(f"- {gap}" for gap in delegate["mcp_gaps"])
    else:
        lines.append("- No delegate/latent/async report was provided.")

    lines.extend(["", "## Not Ready For", ""])
    lines.extend(f"- {item}" for item in verdict["not_ready_for"])
    lines.extend(["", "## Next Reinforcement Candidates", ""])
    for item in report["next_reinforcement_candidates"]:
        lines.append(f"- `{item['priority']}` {item['name']}: {item['why']}")
    lines.extend(
        [
            "",
            "## Decision",
            "",
            "Do not open Lyra in Editor for this combined pass. Static package tag extraction already produced high-confidence class ancestry for the Blueprint-like set. Use an Editor Asset Registry pass only as the next optional verification step when exact graph counts or property payload details become necessary.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report(report: Dict[str, Any], output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "lyra_combined_readiness_report.json"
    md_path = output_dir / "lyra_combined_readiness_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_arg_parser() -> argparse.ArgumentParser:
    repo_root = base.repo_root_from_script()
    output_dir = repo_root / "Docs" / "Analysis" / "Lyra"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cpp-report", default=str(output_dir / "lyra_readiness_report.json"))
    parser.add_argument("--asset-report", default=str(output_dir / "lyra_blueprint_asset_ancestry_report.json"))
    parser.add_argument("--delegate-report", default=str(output_dir / "lyra_delegate_latent_async_readiness_report.json"))
    parser.add_argument("--output-dir", default=str(output_dir))
    parser.add_argument("--no-write", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    output_dir = Path(args.output_dir).resolve()
    cpp_report = load_json(Path(args.cpp_report))
    asset_report = load_json(Path(args.asset_report))
    delegate_report_path = Path(args.delegate_report)
    delegate_report = load_json(delegate_report_path) if delegate_report_path.exists() else None
    project_root = Path(cpp_report.get("read_only_project_root") or asset_report.get("read_only_project_root", "")).resolve()
    if base.path_is_relative_to(output_dir, project_root):
        raise ValueError(f"Refusing to write output inside external project: {output_dir}")

    report = build_combined(cpp_report, asset_report, output_dir, delegate_report)
    if not args.no_write:
        json_path, md_path = write_report(report, output_dir)
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    print(f"Minimum stable scope: {report['verdict']['minimum_stable_scope']}")
    print(f"Current authoring ceiling: {report['verdict']['current_authoring_ceiling']}")
    print(f"Editor open required now: {report['verdict']['editor_open_required_now']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
