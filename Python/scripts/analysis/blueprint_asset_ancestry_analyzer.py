#!/usr/bin/env python
"""
Read-only Blueprint asset ancestry intake for external Unreal projects.

This is a static analyzer. It scans `.uasset` package bytes for asset-registry
tag strings such as ParentClass, NativeParentClass, and GeneratedClass. It does
not open Unreal Editor and does not write to the inspected project.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import external_project_readiness_analyzer as base


ASSET_SUFFIXES = {".uasset", ".umap"}
MAX_STRING_SCAN_BYTES = 96 * 1024 * 1024
ASCII_RE = re.compile(rb"[\x20-\x7e]{4,}")
UTF16_RE = re.compile(rb"(?:[\x20-\x7e]\x00){4,}")
CLASS_REF_RE = re.compile(r"(?:Class|BlueprintGeneratedClass|WidgetBlueprintGeneratedClass|AnimBlueprintGeneratedClass)'([^']+)'")
SCRIPT_CLASS_RE = re.compile(r"^/Script/[A-Za-z0-9_]+\.[A-Za-z0-9_]+$")
CONTENT_CLASS_RE = re.compile(r"^/(?:Game|[A-Za-z0-9_]+)/.+_C$")


def iter_asset_roots(project_root: Path) -> Iterable[Path]:
    content_root = project_root / "Content"
    if content_root.exists():
        yield content_root

    plugins_root = project_root / "Plugins"
    if plugins_root.exists():
        for current, dirs, _files in os.walk(plugins_root):
            dirs[:] = [name for name in dirs if name not in base.IGNORED_DIRS]
            current_path = Path(current)
            if current_path.name == "Content":
                yield current_path
                dirs[:] = []


def iter_asset_files(project_root: Path) -> Iterable[Path]:
    seen: set[Path] = set()
    for root in iter_asset_roots(project_root):
        for current, dirs, files in os.walk(root):
            dirs[:] = [name for name in dirs if name not in base.IGNORED_DIRS]
            for file_name in files:
                path = Path(current) / file_name
                if path.suffix.lower() in ASSET_SUFFIXES and path not in seen:
                    seen.add(path)
                    yield path


def package_path_for_asset(path: Path, project_root: Path) -> str:
    resolved = path.resolve()
    content_root = (project_root / "Content").resolve()
    if base.path_is_relative_to(resolved, content_root):
        rel = resolved.relative_to(content_root).with_suffix("")
        return "/Game/" + rel.as_posix()

    plugins_root = project_root / "Plugins"
    if plugins_root.exists():
        for content in iter_asset_roots(project_root):
            content_resolved = content.resolve()
            if content_resolved == content_root:
                continue
            if base.path_is_relative_to(resolved, content_resolved):
                plugin_name = content_resolved.parent.name
                rel = resolved.relative_to(content_resolved).with_suffix("")
                return f"/{plugin_name}/" + rel.as_posix()

    return "/" + path.with_suffix("").as_posix().replace(":", "")


def relative_asset_path(path: Path, project_root: Path) -> str:
    return base.relative(path, project_root)


def extract_package_strings(path: Path) -> Tuple[List[str], Optional[str]]:
    size = path.stat().st_size
    if size > MAX_STRING_SCAN_BYTES:
        return [], f"skipped_large_asset:{size}"

    data = path.read_bytes()
    strings: List[str] = []
    for raw in ASCII_RE.findall(data):
        try:
            strings.append(raw.decode("ascii"))
        except UnicodeDecodeError:
            continue
    for raw in UTF16_RE.findall(data):
        try:
            strings.append(raw.decode("utf-16le"))
        except UnicodeDecodeError:
            continue

    compact: List[str] = []
    last = None
    for value in strings:
        if value != last:
            compact.append(value)
        last = value
    return compact, None


def normalize_class_ref(value: str) -> str:
    match = CLASS_REF_RE.search(value)
    if match:
        return match.group(1)
    return value


def looks_like_class_ref(value: str) -> bool:
    normalized = normalize_class_ref(value)
    return bool(SCRIPT_CLASS_RE.match(normalized) or CONTENT_CLASS_RE.match(normalized))


def find_tag_values(strings: Sequence[str], tag_name: str) -> List[str]:
    values: List[str] = []
    for index, value in enumerate(strings):
        if value != tag_name:
            continue
        for candidate in strings[index + 1 : index + 8]:
            normalized = normalize_class_ref(candidate)
            if looks_like_class_ref(candidate):
                values.append(normalized)
                break
    return values


def first_or_empty(values: Sequence[str]) -> str:
    return values[0] if values else ""


def contains_any(haystack: str, needles: Iterable[str]) -> bool:
    lower = haystack.lower()
    return any(needle.lower() in lower for needle in needles)


def classify_asset(asset: Dict[str, Any], strings: Sequence[str]) -> Dict[str, Any]:
    name = asset["name"]
    path = asset["package_path"]
    parent = asset.get("parent_class", "")
    native_parent = asset.get("native_parent_class", "")
    generated = asset.get("generated_class", "")
    joined = "\n".join(strings[:1200])
    context = "\n".join([name, path, parent, native_parent, generated, joined])
    parent_context = "\n".join([parent, native_parent, generated])
    owns_blueprint_class = asset.get("owns_blueprint_generated_class", False)

    category = "unknown_asset"
    readiness = "inventory_only"
    risk = "low"
    reason = "No Blueprint class ancestry tags detected."

    if owns_blueprint_class or parent or native_parent:
        category = "unknown_blueprint"
        readiness = "partial"
        risk = "medium"
        reason = "Blueprint class ancestry is present but parent type was not classified."

    if contains_any(parent_context, ["AnimInstance", "AnimNotify", "AnimNotifyState", "AnimLayerInterface"]) or name.startswith(
        ("ABP_", "ALI_", "AN_", "ANS_")
    ):
        category = "animation_blueprint"
        readiness = "partial_blocked"
        risk = "high"
        reason = "Animation Blueprint graph/state-machine authoring is outside the current generic BP graph surface."

    if contains_any(
        parent_context,
        [
            "CommonUI",
            "CommonInput",
            "CommonActivatableWidget",
            "CommonUserWidget",
            "UserWidget",
            "LyraActivatableWidget",
            "LyraButton",
            "LyraConfirmationScreen",
            "LyraHUDLayout",
            "LyraTaggedWidget",
            "LyraReticleWidgetBase",
            "LyraPerfStatWidgetBase",
        ],
    ) or (name.startswith(("W_", "WBP_")) and owns_blueprint_class):
        category = "common_ui_umg"
        readiness = "partial_blocked"
        risk = "high"
        reason = "Widget ancestry is visible, but CommonUI/UMG tree and activation-policy authoring need dedicated tooling."

    if contains_any(parent_context, ["GameplayAbility", "LyraGameplayAbility"]) or (name.startswith("GA_") and owns_blueprint_class):
        category = "gameplay_ability"
        readiness = "partial_blocked"
        risk = "high"
        reason = "Ability Blueprint children are detectable, but GAS tasks, prediction, costs, and commit flow need dedicated support."

    if contains_any(parent_context, ["GameplayEffect"]) or (name.startswith("GE_") and owns_blueprint_class):
        category = "gameplay_effect"
        readiness = "partial"
        risk = "medium"
        reason = "GameplayEffect assets are data-heavy and need GAS-specific data inspection before authoring."

    if contains_any(parent_context, ["GameplayCueNotify"]) or (name.startswith("GCN_") and owns_blueprint_class):
        category = "gameplay_cue"
        readiness = "partial"
        risk = "medium"
        reason = "GameplayCue classes can be inventoried, but cue event semantics need GAS-specific checks."

    if contains_any(parent_context + "\n" + path, ["GameFeature", "LyraExperienceDefinition", "LyraPawnData", "ExperienceActionSet"]):
        category = "game_feature_or_experience"
        readiness = "blocked_native"
        risk = "critical"
        reason = "GameFeature and experience assets participate in plugin activation and project architecture."

    if contains_any(parent_context, ["DataAsset", "PrimaryDataAsset", "InventoryItemDefinition"]) and category in {
        "unknown_asset",
        "unknown_blueprint",
    }:
        category = "data_asset"
        readiness = "partial"
        risk = "medium"
        reason = "Data asset ancestry is visible, but property payload authoring needs asset-specific tooling."

    if contains_any(parent_context, ["InputAction", "InputMappingContext"]) or name.startswith(("IA_", "IMC_")):
        category = "enhanced_input_asset"
        readiness = "supported_inventory"
        risk = "low"
        reason = "Enhanced Input assets can be inventoried and connected to existing MCP input event authoring."

    if contains_any(parent_context, ["BlueprintFunctionLibrary"]) and category == "unknown_blueprint":
        category = "blueprint_function_library"
        readiness = "supported_partial"
        risk = "medium"
        reason = "Blueprint function libraries can be inventoried; function graph authoring is supported only for simple functions."

    if (parent == "/Script/CoreUObject.Interface" or native_parent == "/Script/CoreUObject.Interface") and category == "unknown_blueprint":
        category = "blueprint_interface"
        readiness = "partial_blocked"
        risk = "high"
        reason = "Blueprint Interface assets need dedicated interface/function signature authoring support."

    if contains_any(parent_context, ["AssetActionUtility", "EditorUtility", "Blutility"]) and category == "unknown_blueprint":
        category = "editor_utility_blueprint"
        readiness = "blocked_native"
        risk = "critical"
        reason = "Editor utility Blueprints are editor-only workflow tools and outside runtime C++ to BP conversion scope."

    if contains_any(parent_context, ["GameInstance", "GameMode", "GameState", "PlayerController", "CameraMode"]) and category in {
        "unknown_blueprint",
        "actor_blueprint",
    }:
        category = "framework_blueprint"
        readiness = "partial"
        risk = "medium"
        reason = "Framework Blueprints can be inventoried, but lifecycle/default wiring needs project-specific validation."

    if (
        contains_any(parent + "\n" + native_parent, ["ActorComponent", "SceneComponent"])
        and category in {"unknown_asset", "unknown_blueprint"}
    ):
        category = "component_blueprint"
        readiness = "supported_partial"
        risk = "medium"
        reason = "Component Blueprint ancestry maps to existing component and graph-glue authoring."

    if (
        contains_any(parent + "\n" + native_parent, ["Actor", "Pawn", "Character", "GameMode", "GameState", "PlayerController"])
        and category in {"unknown_asset", "unknown_blueprint"}
    ):
        category = "actor_blueprint"
        readiness = "supported_partial"
        risk = "medium"
        reason = "Actor-family Blueprint ancestry maps to existing shell, component, event, and compile validation tooling."

    if "/Plugins/GameFeatures/" in asset["relative_path"].replace("\\", "/"):
        if category in {"actor_blueprint", "component_blueprint", "data_asset", "unknown_blueprint"}:
            category = f"game_feature_scoped_{category}"
            readiness = "partial_blocked"
            risk = "high"
            reason = "Asset lives under a GameFeature plugin, so activation and dependency context must be preserved."

    confidence = "low"
    if parent or native_parent:
        confidence = "high"
    elif generated or owns_blueprint_class:
        confidence = "medium"

    return {
        "category": category,
        "readiness": readiness,
        "risk": risk,
        "confidence": confidence,
        "reason": reason,
    }


def analyze_asset(path: Path, project_root: Path) -> Dict[str, Any]:
    strings, skip_reason = extract_package_strings(path)
    rel = relative_asset_path(path, project_root)
    package_path = package_path_for_asset(path, project_root)
    name = path.stem

    parent_values = find_tag_values(strings, "ParentClass")
    native_parent_values = find_tag_values(strings, "NativeParentClass")
    generated_values = find_tag_values(strings, "GeneratedClass")
    expected_generated_class = f"{package_path}.{name}_C"
    owns_blueprint_generated_class = any(normalize_class_ref(value) == expected_generated_class for value in generated_values)

    references_blueprint_generated_class = any(
        "BlueprintGeneratedClass" in value or "WidgetBlueprintGeneratedClass" in value or "AnimBlueprintGeneratedClass" in value
        for value in strings
    )

    asset = {
        "name": name,
        "relative_path": rel,
        "package_path": package_path,
        "size": path.stat().st_size,
        "extension": path.suffix.lower(),
        "parent_class": first_or_empty(parent_values),
        "native_parent_class": first_or_empty(native_parent_values),
        "generated_class": first_or_empty(generated_values),
        "all_parent_classes": sorted(set(parent_values)),
        "all_native_parent_classes": sorted(set(native_parent_values)),
        "all_generated_classes": sorted(set(generated_values)),
        "owns_blueprint_generated_class": owns_blueprint_generated_class,
        "references_blueprint_generated_class": references_blueprint_generated_class,
        "skip_reason": skip_reason or "",
    }
    asset.update(classify_asset(asset, strings))
    return asset


def summarize_assets(assets: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    category_counts = Counter(asset["category"] for asset in assets)
    readiness_counts = Counter(asset["readiness"] for asset in assets)
    risk_counts = Counter(asset["risk"] for asset in assets)
    confidence_counts = Counter(asset["confidence"] for asset in assets)
    parent_counts = Counter(asset["native_parent_class"] or asset["parent_class"] or "(none)" for asset in assets)
    blueprint_assets = [
        asset
        for asset in assets
        if asset["owns_blueprint_generated_class"] or asset["parent_class"] or asset["native_parent_class"]
    ]

    candidates = [
        asset
        for asset in blueprint_assets
        if asset["readiness"] == "supported_partial" and asset["confidence"] in {"high", "medium"}
    ]
    blockers = [asset for asset in blueprint_assets if asset["readiness"] in {"blocked_native", "partial_blocked"}]

    return {
        "asset_count": len(assets),
        "blueprint_like_asset_count": len(blueprint_assets),
        "supported_candidate_count": len(candidates),
        "blocked_or_partial_blocked_count": len(blockers),
        "category_counts": dict(category_counts.most_common()),
        "readiness_counts": dict(readiness_counts.most_common()),
        "risk_counts": dict(risk_counts.most_common()),
        "confidence_counts": dict(confidence_counts.most_common()),
        "top_native_or_parent_classes": dict(parent_counts.most_common(30)),
        "supported_candidates": candidates[:80],
        "blocked_examples": blockers[:80],
    }


def build_report(project_root: Path, requested_project_root: str, output_dir: Path) -> Dict[str, Any]:
    if base.path_is_relative_to(output_dir, project_root):
        raise ValueError(f"Refusing to write output inside external project: {output_dir}")

    assets = [analyze_asset(path, project_root) for path in sorted(iter_asset_files(project_root))]
    summary = summarize_assets(assets)
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_kind": "external_unreal_project_blueprint_asset_ancestry",
        "read_only_project_root": str(project_root),
        "requested_project_root": requested_project_root,
        "output_dir": str(output_dir),
        "asset_roots": [str(root) for root in iter_asset_roots(project_root)],
        "summary": summary,
        "assets": assets,
        "read_only_policy": {
            "project_mutation_allowed": False,
            "asset_loading_performed": False,
            "editor_required": False,
            "string_scan_only": True,
            "writes_allowed_only_under_output_dir": True,
        },
    }


def format_count_map(data: Dict[str, Any], limit: int = 24) -> str:
    if not data:
        return "- none\n"
    lines = []
    for index, (key, value) in enumerate(data.items()):
        if index >= limit:
            lines.append(f"- ... {len(data) - limit} more")
            break
        lines.append(f"- `{key}`: {value}")
    return "\n".join(lines) + "\n"


def format_asset_table(assets: Sequence[Dict[str, Any]], limit: int = 25) -> str:
    if not assets:
        return "No assets.\n"
    lines = ["| Asset | Category | Parent | Readiness | Risk | Confidence |", "| --- | --- | --- | --- | --- | --- |"]
    for asset in assets[:limit]:
        parent = asset["native_parent_class"] or asset["parent_class"] or "(none)"
        lines.append(
            f"| `{asset['package_path']}` | `{asset['category']}` | `{parent}` | `{asset['readiness']}` | `{asset['risk']}` | `{asset['confidence']}` |"
        )
    return "\n".join(lines) + "\n"


def render_markdown(report: Dict[str, Any]) -> str:
    summary = report["summary"]
    lines = [
        "# Lyra Blueprint Asset Ancestry Intake",
        "",
        f"- Generated UTC: `{report['generated_at']}`",
        f"- Read-only project root: `{report['read_only_project_root']}`",
        f"- Output dir: `{report['output_dir']}`",
        "- Method: static `.uasset` string scan of asset-registry tags; no Editor load, save, or asset mutation.",
        "",
        "## Executive Result",
        "",
        f"- Assets scanned: `{summary['asset_count']}`",
        f"- Blueprint-like assets: `{summary['blueprint_like_asset_count']}`",
        f"- Supported partial candidates: `{summary['supported_candidate_count']}`",
        f"- Blocked or partial-blocked Blueprint-like assets: `{summary['blocked_or_partial_blocked_count']}`",
        "- Parent/native parent extraction is high confidence when `ParentClass` or `NativeParentClass` tags were present.",
        "",
        "## Category Counts",
        "",
        format_count_map(summary["category_counts"]),
        "## Readiness Counts",
        "",
        format_count_map(summary["readiness_counts"]),
        "## Risk Counts",
        "",
        format_count_map(summary["risk_counts"]),
        "## Top Parent Classes",
        "",
        format_count_map(summary["top_native_or_parent_classes"]),
        "## Supported Partial Candidates",
        "",
        format_asset_table(summary["supported_candidates"], limit=30),
        "## Blocked / Dedicated-Support Examples",
        "",
        format_asset_table(summary["blocked_examples"], limit=30),
        "## Intake Limits",
        "",
        "- This report does not parse Blueprint graphs or property payloads.",
        "- It should be treated as class-ancestry readiness, not final conversion proof.",
        "- Editor-side Asset Registry verification is a later optional pass and must still avoid saving Lyra assets.",
    ]
    return "\n".join(lines) + "\n"


def write_report(report: Dict[str, Any], output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "lyra_blueprint_asset_ancestry_report.json"
    md_path = output_dir / "lyra_blueprint_asset_ancestry_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_arg_parser() -> argparse.ArgumentParser:
    repo_root = base.repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default="", help="External Unreal project root. Defaults to known Lyra candidates.")
    parser.add_argument(
        "--output-dir",
        default=str(repo_root / "Docs" / "Analysis" / "Lyra"),
        help="Directory for JSON and Markdown reports. Must not be under the external project.",
    )
    parser.add_argument("--no-write", action="store_true", help="Analyze and print summary without writing reports.")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    project_root, _notes = base.resolve_project_root(args.project_root or None)
    output_dir = Path(args.output_dir).resolve()
    report = build_report(project_root, args.project_root, output_dir)
    if not args.no_write:
        json_path, md_path = write_report(report, output_dir)
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    summary = report["summary"]
    print(f"Project: {project_root}")
    print(f"Assets scanned: {summary['asset_count']}")
    print(f"Blueprint-like assets: {summary['blueprint_like_asset_count']}")
    print(f"Supported partial candidates: {summary['supported_candidate_count']}")
    print(f"Blocked or partial-blocked: {summary['blocked_or_partial_blocked_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
