#!/usr/bin/env python
"""
Read-only Unreal external project intake and Blueprint authoring readiness analysis.

The analyzer is intentionally filesystem-only. It does not open Unreal Editor,
does not load assets, and refuses to write output inside the inspected project.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


IGNORED_DIRS = {
    ".git",
    ".vs",
    "Binaries",
    "DerivedDataCache",
    "Intermediate",
    "Saved",
    "__pycache__",
}

SOURCE_SUFFIXES = {".h", ".hpp", ".hh", ".cpp", ".cxx", ".cc", ".inl", ".cs"}
CONFIG_SUFFIXES = {".ini", ".uproject", ".uplugin"}
CONTENT_SUFFIXES = {".uasset", ".umap"}
SNAPSHOT_ROOT_DIRS = ("Config", "Source", "Content", "Plugins")
PSEUDO_CAPABILITY_GROUPS = {"umg_tools", "project_tools", "editor_tools"}


@dataclass(frozen=True)
class PatternRule:
    key: str
    label: str
    readiness: str
    risk: str
    patterns: Tuple[str, ...]
    mcp_mapping: Tuple[str, ...]
    note: str


@dataclass
class PatternHit:
    count: int = 0
    files: Counter = field(default_factory=Counter)
    examples: List[str] = field(default_factory=list)


PATTERN_RULES: Tuple[PatternRule, ...] = (
    PatternRule(
        key="reflected_api",
        label="Reflected Unreal API surface",
        readiness="supported_inventory",
        risk="low",
        patterns=(r"\bUCLASS\s*\(", r"\bUSTRUCT\s*\(", r"\bUENUM\s*\(", r"\bUPROPERTY\s*\(", r"\bUFUNCTION\s*\("),
        mcp_mapping=("create_blueprint", "add_blueprint_variable", "add_blueprint_function_parameter", "compile_and_validate_blueprint"),
        note="Reflection macros can be inventoried and partially mapped to Blueprint shells, variables, and callable nodes.",
    ),
    PatternRule(
        key="blueprint_exposed_api",
        label="Blueprint-exposed native API",
        readiness="supported_partial",
        risk="low",
        patterns=(
            r"BlueprintCallable",
            r"BlueprintPure",
            r"BlueprintReadOnly",
            r"BlueprintReadWrite",
            r"BlueprintAssignable",
            r"BlueprintType",
            r"Blueprintable",
            r"BlueprintNativeEvent",
            r"BlueprintImplementableEvent",
        ),
        mcp_mapping=("add_blueprint_call_function_node", "set_blueprint_pin_default", "connect_blueprint_nodes"),
        note="Existing MCP tools can call exposed functions and author graph glue, but native implementations remain native.",
    ),
    PatternRule(
        key="basic_actor_component_authoring",
        label="Actor and component composition",
        readiness="supported_partial",
        risk="medium",
        patterns=(
            r"\bAActor\b",
            r"\bAPawn\b",
            r"\bACharacter\b",
            r"\bUActorComponent\b",
            r"\bUSceneComponent\b",
            r"\bCreateDefaultSubobject\s*<",
            r"\bBeginPlay\s*\(",
            r"\bTick\s*\(",
        ),
        mcp_mapping=("create_blueprint", "add_component_to_blueprint", "set_component_property", "add_blueprint_event_node"),
        note="Blueprint shells and component setup are feasible when behavior is simple and component classes already exist.",
    ),
    PatternRule(
        key="control_flow_expression_authoring",
        label="Blueprint graph control flow and expressions",
        readiness="supported_partial",
        risk="medium",
        patterns=(
            r"\bif\s*\(",
            r"\belse\b",
            r"\bswitch\s*\(",
            r"\bfor\s*\(",
            r"\bwhile\s*\(",
            r"\bTArray\s*<",
            r"\bTMap\s*<",
            r"\bTSet\s*<",
        ),
        mcp_mapping=(
            "add_blueprint_branch_node",
            "add_blueprint_switch_int_node",
            "add_blueprint_switch_enum_node",
            "add_blueprint_loop_node",
            "add_blueprint_array_function_node",
            "add_blueprint_make_array_node",
        ),
        note="MCP can author common graph constructs, but arbitrary C++ expression lowering remains heuristic.",
    ),
    PatternRule(
        key="enhanced_input",
        label="Enhanced Input",
        readiness="supported_partial",
        risk="medium",
        patterns=(r"\bEnhancedInput\b", r"\bUInputAction\b", r"\bUInputMappingContext\b", r"\bInputAction\b", r"\bBindAction\s*\("),
        mcp_mapping=("create_input_mapping", "add_blueprint_enhanced_input_action_node", "add_blueprint_input_action_node"),
        note="Event node authoring exists; full asset/data migration and trigger/modifier semantics need separate handling.",
    ),
    PatternRule(
        key="data_assets_and_registry",
        label="Data assets and data registries",
        readiness="partial",
        risk="medium",
        patterns=(r"\bUDataAsset\b", r"\bUPrimaryDataAsset\b", r"\bPrimaryDataAsset\b", r"\bDataRegistry\b", r"\bAssetManager\b"),
        mcp_mapping=("create_blueprint", "set_blueprint_property", "compile_and_validate_blueprint"),
        note="Asset classes can be discovered; data asset creation/editing needs editor-side asset tooling beyond graph authoring.",
    ),
    PatternRule(
        key="gameplay_tags",
        label="Gameplay Tags",
        readiness="partial",
        risk="medium",
        patterns=(r"\bFGameplayTag\b", r"\bFGameplayTagContainer\b", r"\bGameplayTag", r"\bGameplayTags\b"),
        mcp_mapping=("add_blueprint_variable", "add_blueprint_call_function_node", "add_blueprint_enum_literal_node"),
        note="Tags can be referenced through exposed APIs; tag table authoring and semantic migration are separate concerns.",
    ),
    PatternRule(
        key="gameplay_ability_system",
        label="Gameplay Ability System",
        readiness="partial_blocked",
        risk="high",
        patterns=(
            r"\bUGameplayAbility\b",
            r"\bUAbilitySystemComponent\b",
            r"\bUAttributeSet\b",
            r"\bGameplayEffect\b",
            r"\bGameplayCue\b",
            r"\bFGameplayAbility",
            r"\bAbilityTask\b",
        ),
        mcp_mapping=("add_blueprint_call_function_node", "add_blueprint_event_node", "compile_and_validate_blueprint"),
        note="Blueprint children and glue may be feasible, but core ASC, attributes, prediction, and ability tasks remain native-heavy.",
    ),
    PatternRule(
        key="common_ui_umg",
        label="CommonUI and UMG",
        readiness="partial_blocked",
        risk="high",
        patterns=(
            r"\bCommonUI\b",
            r"\bUCommon",
            r"\bUUserWidget\b",
            r"\bBindWidget",
            r"\bActivatableWidget\b",
            r"\bWidgetTree\b",
        ),
        mcp_mapping=("umg_tools", "add_blueprint_event_node", "add_blueprint_call_function_node"),
        note="UMG wrappers help, but CommonUI activation/layer policy and widget trees need dedicated analyzer support.",
    ),
    PatternRule(
        key="subsystems_lifecycle",
        label="Subsystem and lifecycle orchestration",
        readiness="partial_blocked",
        risk="high",
        patterns=(
            r"\bUWorldSubsystem\b",
            r"\bUGameInstanceSubsystem\b",
            r"\bULocalPlayerSubsystem\b",
            r"\bUEngineSubsystem\b",
            r"\bInitialize\s*\(",
            r"\bDeinitialize\s*\(",
            r"\bShouldCreateSubsystem\s*\(",
        ),
        mcp_mapping=("add_blueprint_call_function_node", "add_blueprint_event_node"),
        note="Lifecycle hooks can be called around, but authoritative subsystem behavior should remain native or get explicit support.",
    ),
    PatternRule(
        key="delegates_async_latent",
        label="Delegates, async actions, and latent flow",
        readiness="partial_blocked",
        risk="high",
        patterns=(
            r"\bDECLARE_DYNAMIC",
            r"\bDECLARE_MULTICAST",
            r"\bBlueprintAssignable",
            r"\bDelegate\b",
            r"\bAddDynamic\s*\(",
            r"\bAddUObject\s*\(",
            r"\bAsyncAction",
            r"\bLatent",
            r"\bAsyncTask\b",
        ),
        mcp_mapping=("add_blueprint_call_function_node", "connect_blueprint_nodes"),
        note="Binding and callback topology are detectable, but robust delegate/event authoring needs more MCP graph primitives.",
    ),
    PatternRule(
        key="networking_replication",
        label="Networking and replication",
        readiness="blocked_native",
        risk="critical",
        patterns=(
            r"\bReplicated\b",
            r"\bReplicatedUsing\b",
            r"\bOnRep_",
            r"\bGetLifetimeReplicatedProps\b",
            r"\bDOREPLIFETIME",
            r"\bServer\s*,",
            r"\bClient\s*,",
            r"\bNetMulticast\b",
            r"\bReplicationGraph\b",
            r"\bFastArraySerializer\b",
        ),
        mcp_mapping=("compile_and_validate_blueprint",),
        note="Replication policy, prediction, RPC authority, and replication graph behavior are not safe to auto-lower to BP.",
    ),
    PatternRule(
        key="game_features_modular_gameplay",
        label="Game Features and Modular Gameplay",
        readiness="blocked_native",
        risk="critical",
        patterns=(r"\bGameFeature", r"\bGameFeatures\b", r"\bModularGameplay\b", r"\bGameFeatureAction\b", r"\bExperience\b"),
        mcp_mapping=("project_tools", "compile_and_validate_blueprint"),
        note="Plugin activation, experience loading, and component injection are project architecture concerns, not just BP graph authoring.",
    ),
    PatternRule(
        key="slate_editor_cpp",
        label="Slate and editor-only C++",
        readiness="blocked_native",
        risk="critical",
        patterns=(
            r"\bSCompoundWidget\b",
            r"\bSWidget\b",
            r"\bSlate\b",
            r"\bFSlate",
            r"\bUEditor",
            r"\bCommandlet\b",
            r"\bEditorValidator",
            r"\bFAssetTypeActions",
        ),
        mcp_mapping=("editor_tools",),
        note="Editor modules and Slate widgets should be classified out of runtime BP conversion scope.",
    ),
    PatternRule(
        key="custom_k2_native_extensions",
        label="Custom K2 and native graph extensions",
        readiness="blocked_native",
        risk="critical",
        patterns=(r"\bUK2Node\b", r"\bK2Node_", r"\bFBlueprintActionDatabase", r"\bFGraphPanel", r"\bUEdGraphNode\b"),
        mcp_mapping=("list_blueprint_nodes", "compile_and_validate_blueprint"),
        note="Custom K2 node behavior is native editor extension code and cannot be recreated by generic BP authoring alone.",
    ),
)


RISK_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
READINESS_RANK = {
    "supported_inventory": 0,
    "supported_partial": 1,
    "partial": 2,
    "partial_blocked": 3,
    "blocked_native": 4,
}


def path_is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def default_project_candidates() -> List[Path]:
    env_path = os.environ.get("LYRA_PROJECT_ROOT")
    candidates: List[Path] = []
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(
        [
            Path(r"D:\Git\LyraStarterGame"),
        ]
    )
    return candidates


def resolve_project_root(explicit: Optional[str]) -> Tuple[Path, List[str]]:
    notes: List[str] = []
    candidates = [Path(explicit)] if explicit else default_project_candidates()
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            if explicit and Path(explicit) != candidate:
                notes.append(f"Resolved explicit project root to {candidate}")
            return candidate.resolve(), notes

    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError(f"External project root not found. Searched: {searched}")


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="ignore")


def iter_files(root: Path, suffixes: Iterable[str]) -> Iterable[Path]:
    suffix_set = {suffix.lower() for suffix in suffixes}
    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in IGNORED_DIRS]
        current_path = Path(current)
        for file_name in files:
            path = current_path / file_name
            if path.suffix.lower() in suffix_set or file_name.endswith(".Build.cs") or file_name.endswith(".Target.cs"):
                yield path


def iter_project_snapshot_files(project_root: Path) -> Iterable[Path]:
    for descriptor in sorted(project_root.glob("*.uproject")):
        if descriptor.is_file():
            yield descriptor

    for root_name in SNAPSHOT_ROOT_DIRS:
        root = project_root / root_name
        if not root.exists():
            continue
        for current, dirs, files in os.walk(root):
            dirs[:] = [name for name in dirs if name not in IGNORED_DIRS]
            current_path = Path(current)
            for file_name in files:
                yield current_path / file_name


def snapshot_project_tree(project_root: Path) -> Dict[str, Tuple[int, int]]:
    snapshot: Dict[str, Tuple[int, int]] = {}
    for path in iter_project_snapshot_files(project_root):
        stat = path.stat()
        snapshot[relative(path, project_root)] = (stat.st_size, stat.st_mtime_ns)
    return snapshot


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def load_project_descriptor(project_root: Path) -> Dict[str, Any]:
    descriptors = sorted(project_root.glob("*.uproject"))
    if not descriptors:
        return {"path": None, "modules": [], "plugins": [], "error": "No .uproject file found"}

    descriptor_path = descriptors[0]
    try:
        data = json.loads(read_text(descriptor_path))
    except json.JSONDecodeError as exc:
        return {"path": descriptor_path.name, "modules": [], "plugins": [], "error": str(exc)}

    return {
        "path": descriptor_path.name,
        "engine_association": data.get("EngineAssociation", ""),
        "modules": data.get("Modules", []),
        "plugins": data.get("Plugins", []),
        "enabled_plugin_names": sorted(plugin.get("Name", "") for plugin in data.get("Plugins", []) if plugin.get("Enabled")),
    }


def classify_file(path: Path, text: str, project_root: Path) -> Dict[str, Any]:
    rel = relative(path, project_root)
    hits: Dict[str, int] = {}
    max_readiness = "supported_inventory"
    max_risk = "low"

    for rule in PATTERN_RULES:
        count = 0
        for pattern in rule.patterns:
            count += len(re.findall(pattern, text))
        if count:
            hits[rule.key] = count
            if READINESS_RANK[rule.readiness] > READINESS_RANK[max_readiness]:
                max_readiness = rule.readiness
            if RISK_RANK[rule.risk] > RISK_RANK[max_risk]:
                max_risk = rule.risk

    return {
        "path": rel,
        "line_count": text.count("\n") + 1 if text else 0,
        "hits": hits,
        "readiness": max_readiness if hits else "unknown",
        "risk": max_risk if hits else "unknown",
    }


def scan_source(project_root: Path) -> Dict[str, Any]:
    files = list(iter_files(project_root, SOURCE_SUFFIXES | CONFIG_SUFFIXES))
    source_files = [path for path in files if path.suffix.lower() in SOURCE_SUFFIXES or path.name.endswith((".Build.cs", ".Target.cs"))]
    config_files = [path for path in files if path.suffix.lower() in CONFIG_SUFFIXES]

    pattern_hits: Dict[str, PatternHit] = {rule.key: PatternHit() for rule in PATTERN_RULES}
    file_summaries: List[Dict[str, Any]] = []
    module_counts: Counter = Counter()
    suffix_counts: Counter = Counter()

    for path in sorted(source_files + config_files):
        text = read_text(path)
        summary = classify_file(path, text, project_root)
        file_summaries.append(summary)
        suffix_counts[path.suffix.lower() or path.name] += 1
        parts = path.relative_to(project_root).parts
        if parts and parts[0] in {"Source", "Plugins"}:
            if parts[0] == "Source" and len(parts) > 1:
                module_counts[parts[1]] += 1
            elif parts[0] == "Plugins" and len(parts) > 3 and parts[2] == "Source":
                module_name = parts[3]
                if module_name in {"Public", "Private"} or module_name.endswith(".Build.cs"):
                    module_name = parts[1]
                module_counts[f"{parts[1]}/{module_name}"] += 1

        for key, count in summary["hits"].items():
            hit = pattern_hits[key]
            hit.count += count
            hit.files[summary["path"]] += count
            if len(hit.examples) < 8:
                hit.examples.append(summary["path"])

    readiness_by_file = Counter(item["readiness"] for item in file_summaries if item["readiness"] != "unknown")
    risk_by_file = Counter(item["risk"] for item in file_summaries if item["risk"] != "unknown")

    return {
        "file_count": len(source_files),
        "config_file_count": len(config_files),
        "suffix_counts": dict(sorted(suffix_counts.items())),
        "module_file_counts": dict(module_counts.most_common()),
        "readiness_by_file": dict(readiness_by_file),
        "risk_by_file": dict(risk_by_file),
        "pattern_hits": {
            key: {
                "count": hit.count,
                "file_count": len(hit.files),
                "top_files": [{"path": path, "count": count} for path, count in hit.files.most_common(8)],
                "examples": hit.examples,
            }
            for key, hit in pattern_hits.items()
            if hit.count
        },
        "top_risk_files": sorted(
            [item for item in file_summaries if item["risk"] in {"high", "critical"}],
            key=lambda item: (RISK_RANK[item["risk"]], sum(item["hits"].values())),
            reverse=True,
        )[:25],
    }


def scan_content_assets(project_root: Path) -> Dict[str, Any]:
    content_root = project_root / "Content"
    if not content_root.exists():
        return {"content_root_exists": False, "asset_counts": {}, "top_directories": {}}

    asset_counts: Counter = Counter()
    top_dirs: Counter = Counter()
    for path in iter_files(content_root, CONTENT_SUFFIXES):
        asset_counts[path.suffix.lower()] += 1
        try:
            rel_parts = path.relative_to(content_root).parts
        except ValueError:
            rel_parts = path.parts
        if rel_parts:
            top_dirs[rel_parts[0]] += 1

    return {
        "content_root_exists": True,
        "asset_counts": dict(asset_counts),
        "top_directories": dict(top_dirs.most_common(20)),
        "note": "Binary assets are counted by path only; asset internals require Unreal Asset Registry or editor-side analysis.",
    }


def scan_mcp_capabilities(mcp_root: Path, plugin_root: Optional[Path]) -> Dict[str, Any]:
    python_tools = {}
    tools_root = mcp_root / "Python" / "tools"
    if tools_root.exists():
        for path in sorted(tools_root.glob("*.py")):
            text = read_text(path)
            funcs = sorted(set(re.findall(r"^\s{4}def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(", text, flags=re.MULTILINE)))
            if funcs:
                python_tools[path.name] = funcs

    cxx_commands: List[str] = []
    if plugin_root and plugin_root.exists():
        source_root = plugin_root / "Source" / "UnrealMCP"
        if source_root.exists():
            command_patterns = (
                re.compile(r'CommandType\s*==\s*TEXT\("([a-z][a-z0-9_]+)"\)'),
                re.compile(r'CommandType\.Equals\s*\(\s*TEXT\("([a-z][a-z0-9_]+)"\)'),
            )
            for path in iter_files(source_root, {".h", ".cpp"}):
                if "Blueprint" not in path.name and "Project" not in path.name and "Editor" not in path.name:
                    continue
                text = read_text(path)
                for command_pattern in command_patterns:
                    cxx_commands.extend(command_pattern.findall(text))

    flat_tool_names = sorted({name for funcs in python_tools.values() for name in funcs})
    return {
        "mcp_root": str(mcp_root),
        "plugin_root": str(plugin_root) if plugin_root else "",
        "python_tool_count": len(flat_tool_names),
        "python_tools": python_tools,
        "plugin_command_count": len(set(cxx_commands)),
        "plugin_commands": sorted(set(cxx_commands)),
    }


def build_readiness_findings(source_scan: Dict[str, Any], capabilities: Dict[str, Any]) -> Dict[str, Any]:
    tool_names = set(capabilities.get("python_tools", {}).get("blueprint_tools.py", []))
    for funcs in capabilities.get("python_tools", {}).values():
        tool_names.update(funcs)
    tool_names.update(capabilities.get("plugin_commands", []))

    findings: List[Dict[str, Any]] = []
    for rule in PATTERN_RULES:
        hit = source_scan["pattern_hits"].get(rule.key)
        if not hit:
            continue
        mapped = [name for name in rule.mcp_mapping if name in tool_names]
        capability_groups = [name for name in rule.mcp_mapping if name in PSEUDO_CAPABILITY_GROUPS]
        missing = [
            name
            for name in rule.mcp_mapping
            if name not in tool_names and name not in PSEUDO_CAPABILITY_GROUPS
        ]
        findings.append(
            {
                "key": rule.key,
                "label": rule.label,
                "readiness": rule.readiness,
                "risk": rule.risk,
                "hit_count": hit["count"],
                "file_count": hit["file_count"],
                "mapped_capabilities": mapped,
                "capability_groups": capability_groups,
                "unconfirmed_capabilities": missing,
                "note": rule.note,
                "top_files": hit["top_files"],
            }
        )

    findings.sort(key=lambda item: (READINESS_RANK[item["readiness"]], RISK_RANK[item["risk"]], item["hit_count"]), reverse=True)
    blocked = [item for item in findings if item["readiness"] == "blocked_native"]
    partial = [item for item in findings if item["readiness"] in {"partial", "partial_blocked"}]
    supported = [item for item in findings if item["readiness"].startswith("supported")]

    return {
        "overall": {
            "minimum_stable_scope": "readiness_classification_only",
            "bp_conversion_readiness": "partial_with_native_blockers",
            "recommended_first_pass": [
                "Inventory reflected C++ API and Blueprint-exposed surface.",
                "Classify native-heavy systems before attempting any BP graph authoring.",
                "Generate BP shells or graph glue only for low/medium risk classes with existing native parent types.",
                "Keep GAS, replication, GameFeatures, Slate/editor modules, and custom K2 as native-blocked until dedicated support exists.",
            ],
        },
        "supported_categories": supported,
        "partial_categories": partial,
        "blocked_categories": blocked,
        "all_findings": findings,
    }


def build_report(
    project_root: Path,
    requested_project_root: Optional[str],
    output_dir: Path,
    mcp_root: Path,
    plugin_root: Optional[Path],
) -> Dict[str, Any]:
    if path_is_relative_to(output_dir, project_root):
        raise ValueError(f"Refusing to write output inside external project: {output_dir}")

    descriptor = load_project_descriptor(project_root)
    source_scan = scan_source(project_root)
    content_scan = scan_content_assets(project_root)
    capabilities = scan_mcp_capabilities(mcp_root, plugin_root)
    readiness = build_readiness_findings(source_scan, capabilities)

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_kind": "external_unreal_project_bp_authoring_readiness",
        "read_only_project_root": str(project_root),
        "requested_project_root": requested_project_root or "",
        "output_dir": str(output_dir),
        "project_descriptor": descriptor,
        "source_scan": source_scan,
        "content_scan": content_scan,
        "mcp_capabilities": capabilities,
        "readiness": readiness,
        "read_only_policy": {
            "project_mutation_allowed": False,
            "asset_loading_performed": False,
            "editor_required": False,
            "writes_allowed_only_under_output_dir": True,
        },
    }


def format_count_map(data: Dict[str, Any], limit: int = 12) -> str:
    if not data:
        return "- none\n"
    lines = []
    items = list(data.items())
    for key, value in items[:limit]:
        lines.append(f"- `{key}`: {value}")
    if len(items) > limit:
        lines.append(f"- ... {len(items) - limit} more")
    return "\n".join(lines) + "\n"


def format_category_table(categories: Sequence[Dict[str, Any]]) -> str:
    if not categories:
        return "No matching categories.\n"
    lines = [
        "| Category | Readiness | Risk | Hits | Files | Confirmed MCP Mapping | Related Tool Groups |",
        "| --- | --- | --- | ---: | ---: | --- | --- |",
    ]
    for item in categories:
        mapping = ", ".join(f"`{name}`" for name in item["mapped_capabilities"]) or "none confirmed"
        groups = ", ".join(f"`{name}`" for name in item.get("capability_groups", [])) or "none"
        lines.append(
            f"| {item['label']} | `{item['readiness']}` | `{item['risk']}` | {item['hit_count']} | {item['file_count']} | {mapping} | {groups} |"
        )
    return "\n".join(lines) + "\n"


def format_top_files(files: Sequence[Dict[str, Any]], limit: int = 12) -> str:
    if not files:
        return "- none\n"
    lines = []
    for item in files[:limit]:
        hit_keys = ", ".join(sorted(item.get("hits", {}).keys())[:5])
        lines.append(f"- `{item['path']}`: risk `{item['risk']}`, readiness `{item['readiness']}`, patterns {hit_keys}")
    return "\n".join(lines) + "\n"


def render_markdown(report: Dict[str, Any]) -> str:
    descriptor = report["project_descriptor"]
    source_scan = report["source_scan"]
    readiness = report["readiness"]
    content_scan = report["content_scan"]
    caps = report["mcp_capabilities"]

    enabled_plugins = descriptor.get("enabled_plugin_names", [])
    lines = [
        "# Lyra External Project Intake & Readiness Analysis",
        "",
        f"- Generated UTC: `{report['generated_at']}`",
        f"- Read-only project root: `{report['read_only_project_root']}`",
        f"- Requested project root: `{report['requested_project_root'] or 'auto-detected'}`",
        f"- Output dir: `{report['output_dir']}`",
        f"- Unreal descriptor: `{descriptor.get('path')}`",
        f"- Engine association: `{descriptor.get('engine_association', '')}`",
        "",
        "## Executive Result",
        "",
        f"- Minimum stable scope: `{readiness['overall']['minimum_stable_scope']}`",
        f"- BP conversion readiness: `{readiness['overall']['bp_conversion_readiness']}`",
        "- Lyra should remain a read-only corpus for this phase.",
        "- The current UnrealMCP BP surface is useful for inventory, BP shell creation, variables, function calls, control-flow graph glue, Enhanced Input events, and compile validation.",
        "- Full C++ to BP conversion is blocked for native-heavy Lyra systems such as replication, GAS internals, GameFeatures activation, CommonUI policy, Slate/editor modules, and custom K2 nodes.",
        "",
        "## Project Shape",
        "",
        f"- Source/config files scanned: `{source_scan['file_count']}` source, `{source_scan['config_file_count']}` config",
        f"- Content root present: `{content_scan.get('content_root_exists')}`",
        "",
        "### Enabled Plugins",
        "",
        format_count_map({name: "enabled" for name in enabled_plugins}, limit=40),
        "### Module File Counts",
        "",
        format_count_map(source_scan["module_file_counts"], limit=25),
        "### Content Asset Counts",
        "",
        format_count_map(content_scan.get("asset_counts", {})),
        "## Readiness Categories",
        "",
        "### Supported Or Partially Supported",
        "",
        format_category_table(readiness["supported_categories"]),
        "### Partial / Needs Dedicated Support",
        "",
        format_category_table(readiness["partial_categories"]),
        "### Native Blockers",
        "",
        format_category_table(readiness["blocked_categories"]),
        "## Top Risk Files",
        "",
        format_top_files(source_scan["top_risk_files"]),
        "## Current MCP Capability Snapshot",
        "",
        f"- Python MCP tool functions: `{caps['python_tool_count']}`",
        f"- UnrealMCP plugin command names observed: `{caps['plugin_command_count']}`",
        "",
        "## Minimum Stable Range",
        "",
    ]
    for item in readiness["overall"]["recommended_first_pass"]:
        lines.append(f"- {item}")

    lines.extend(
        [
            "",
            "## Next Reinforcement Candidates",
            "",
            "- Add a dedicated asset-registry intake mode to inspect Blueprint class ancestry without saving assets.",
            "- Add delegate/event binding graph primitives before attempting async or callback-heavy conversion.",
            "- Add CommonUI/UMG structure inventory before converting UI classes.",
            "- Add GameplayAbility-specific classification for ability tasks, costs, cooldowns, target data, and prediction boundaries.",
            "- Keep replication graph, RPC authority policy, custom movement, Slate/editor modules, and custom K2 nodes native-blocked unless explicit C++ support is added.",
            "",
            "## Read-only Verification",
            "",
            "- Analyzer uses filesystem reads only for the external project.",
            "- Binary assets are counted by path only.",
            "- Output is guarded so it cannot be written inside the inspected project root.",
        ]
    )

    return "\n".join(lines) + "\n"


def write_report(report: Dict[str, Any], output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "lyra_readiness_report.json"
    md_path = output_dir / "lyra_readiness_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_arg_parser() -> argparse.ArgumentParser:
    repo_root = repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default="", help="External Unreal project root. Defaults to known Lyra candidates.")
    parser.add_argument("--mcp-root", default=str(repo_root), help="unreal-mcp-cubeless repository root.")
    parser.add_argument(
        "--plugin-root",
        default=str(repo_root.parent / "CubelessStylized" / "Plugins" / "UnrealMCP"),
        help="Optional UnrealMCP plugin root used for command inventory.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(repo_root / "Docs" / "Analysis" / "Lyra"),
        help="Directory for JSON and Markdown reports. Must not be under the external project.",
    )
    parser.add_argument("--no-write", action="store_true", help="Analyze and print summary without writing reports.")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    project_root, resolution_notes = resolve_project_root(args.project_root or None)
    output_dir = Path(args.output_dir).resolve()
    mcp_root = Path(args.mcp_root).resolve()
    plugin_root = Path(args.plugin_root).resolve() if args.plugin_root else None

    report = build_report(
        project_root=project_root,
        requested_project_root=args.project_root,
        output_dir=output_dir,
        mcp_root=mcp_root,
        plugin_root=plugin_root,
    )
    if resolution_notes:
        report["resolution_notes"] = resolution_notes

    if not args.no_write:
        json_path, md_path = write_report(report, output_dir)
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")

    overall = report["readiness"]["overall"]
    print(f"Project: {project_root}")
    print(f"Minimum stable scope: {overall['minimum_stable_scope']}")
    print(f"BP conversion readiness: {overall['bp_conversion_readiness']}")
    print(f"Native blocker categories: {len(report['readiness']['blocked_categories'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
