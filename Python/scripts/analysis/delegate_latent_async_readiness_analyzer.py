#!/usr/bin/env python
"""
Read-only delegate, latent, and async Blueprint authoring readiness analysis.

This analyzer focuses on callback topology: delegate declarations, Blueprint
assignable events, native bind/unbind calls, async action proxy classes, latent
functions, AbilityTasks, and custom K2 nodes. It compares those patterns with
the current UnrealMCP Blueprint authoring surface and reports concrete gaps.
"""

from __future__ import annotations

import argparse
import json
import os
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import external_project_readiness_analyzer as base


SOURCE_SUFFIXES = {".h", ".hpp", ".hh", ".cpp", ".cxx", ".cc", ".inl"}
CONTEXT_RADIUS = 2


@dataclass(frozen=True)
class PatternRule:
    key: str
    label: str
    pattern: str
    readiness: str
    risk: str
    gap: str


PATTERN_RULES: Tuple[PatternRule, ...] = (
    PatternRule(
        key="dynamic_delegate_declaration",
        label="Dynamic delegate declarations",
        pattern=r"\bDECLARE_DYNAMIC(?:_MULTICAST)?_DELEGATE(?:_RetVal)?(?:_[A-Za-z0-9]+)?\b",
        readiness="inventory_only",
        risk="medium",
        gap="Can inventory signatures and author Blueprint Event Dispatcher lifecycle nodes, but cannot generically author native or arbitrary delegate topologies yet.",
    ),
    PatternRule(
        key="native_delegate_declaration",
        label="Native delegate declarations",
        pattern=r"\bDECLARE_(?:MULTICAST_)?DELEGATE(?:_RetVal)?(?:_[A-Za-z0-9]+)?\b",
        readiness="blocked_native",
        risk="high",
        gap="Native-only delegate topology usually needs C++ lifecycle handling or wrapper APIs.",
    ),
    PatternRule(
        key="blueprint_assignable_delegate",
        label="BlueprintAssignable delegate properties",
        pattern=r"\bBlueprintAssignable\b",
        readiness="partial_blocked",
        risk="high",
        gap="Existing MCP can declare/call/bind/assign/unbind/clear Blueprint Event Dispatchers, but generic or arbitrary delegate target authoring remains blocked.",
    ),
    PatternRule(
        key="dynamic_binding",
        label="Dynamic delegate binding",
        pattern=r"\.\s*AddDynamic\s*\(",
        readiness="partial_blocked",
        risk="high",
        gap="Blueprint Event Dispatcher lifecycle nodes are supported; arbitrary AddDynamic conversion still needs target classification and lifecycle policy.",
    ),
    PatternRule(
        key="native_binding",
        label="Native delegate binding",
        pattern=r"\.\s*Add(?:UObject|Lambda|Raw|SP|Static)\s*\(",
        readiness="blocked_native",
        risk="critical",
        gap="Native delegate binding depends on object lifetime and shutdown-safe unbinding.",
    ),
    PatternRule(
        key="delegate_unbinding",
        label="Explicit delegate unbinding",
        pattern=r"\.\s*(?:RemoveAll|RemoveDynamic)\s*\(",
        readiness="partial_blocked",
        risk="high",
        gap="Conversion must preserve cleanup paths and object lifetime.",
    ),
    PatternRule(
        key="possible_delegate_unbinding",
        label="Possible delegate handle removal or clear",
        pattern=r"\.\s*(?:Remove|Clear)\s*\(",
        readiness="inventory_only",
        risk="medium",
        gap="Needs context to distinguish delegate handle cleanup from ordinary container mutation.",
    ),
    PatternRule(
        key="delegate_broadcast",
        label="Delegate broadcasts",
        pattern=r"\.\s*Broadcast\s*\(",
        readiness="partial_blocked",
        risk="high",
        gap="Broadcast points define callback semantics and ordering that need explicit graph topology.",
    ),
    PatternRule(
        key="async_action_class",
        label="Blueprint async action classes",
        pattern=r"\bclass\s+\w*Async\w*\s*:\s*public\s+(?:UBlueprintAsyncActionBase|UCancellableAsyncAction)\b",
        readiness="partial_blocked",
        risk="high",
        gap="Async proxy nodes expose callback exec pins that generic function calls do not model.",
    ),
    PatternRule(
        key="blueprint_internal_async_factory",
        label="Blueprint internal async factories",
        pattern=r"BlueprintInternalUseOnly\s*=\s*\"?true\"?",
        readiness="partial_blocked",
        risk="high",
        gap="Internal async factories normally spawn specialized K2 async nodes with delegate outputs.",
    ),
    PatternRule(
        key="latent_function",
        label="Latent Blueprint functions",
        pattern=r"\bLatent\b|LatentInfo|FLatentActionInfo",
        readiness="partial_blocked",
        risk="high",
        gap="MCP can optionally allow latent function calls, but latent continuation semantics still need validation.",
    ),
    PatternRule(
        key="ability_task",
        label="Gameplay AbilityTasks",
        pattern=r"\bUAbilityTask\b|\bAbilityTask_|\bWait(?:Gameplay|Target|Delay|Input|Attribute|Ability)",
        readiness="blocked_native",
        risk="critical",
        gap="AbilityTasks are GAS-specific async nodes with prediction and ability lifecycle constraints.",
    ),
    PatternRule(
        key="custom_k2_async_node",
        label="Custom K2 async nodes",
        pattern=r"\bUK2Node_AsyncAction\b|\bK2Node_Async\w*|\bUK2Node_\w*Async\w*",
        readiness="blocked_native",
        risk="critical",
        gap="Custom K2 expansion behavior is native editor code, outside generic BP graph authoring.",
    ),
    PatternRule(
        key="engine_lifecycle_delegate",
        label="Engine lifecycle delegates",
        pattern=r"\bF(?:World|Core|Slate|Editor)Delegates\b|FSlateApplication::Get\(\)|OnStartGameInstance|OnPreClientTravel",
        readiness="blocked_native",
        risk="critical",
        gap="Engine lifecycle delegates need shutdown-safe C++/subsystem handling.",
    ),
)


RISK_RANK = {"low": 0, "medium": 1, "high": 2, "critical": 3}
READINESS_RANK = {"inventory_only": 0, "partial": 1, "partial_blocked": 2, "blocked_native": 3}

DELEGATE_SITE_PATTERNS: Tuple[Tuple[str, re.Pattern[str]], ...] = (
    ("add_dynamic", re.compile(r"\.\s*AddDynamic\s*\(")),
    ("add_uobject", re.compile(r"\.\s*AddUObject\s*\(")),
    ("add_lambda", re.compile(r"\.\s*AddLambda\s*\(")),
    ("add_raw", re.compile(r"\.\s*AddRaw\s*\(")),
    ("add_sp", re.compile(r"\.\s*AddSP\s*\(")),
    ("add_static", re.compile(r"\.\s*AddStatic\s*\(")),
    ("remove_dynamic", re.compile(r"\.\s*RemoveDynamic\s*\(")),
    ("remove_all", re.compile(r"\.\s*RemoveAll\s*\(")),
    ("remove_handle", re.compile(r"\.\s*Remove\s*\(")),
    ("clear", re.compile(r"\.\s*Clear\s*\(")),
    (
        "engine_lifecycle",
        re.compile(
            r"\bF(?:World|Core|CoreUObject|Slate|Editor)Delegates\b|"
            r"FSlateApplication::Get\(\)|OnStartGameInstance|OnPreClientTravel|BeginPIE|EndPIE"
        ),
    ),
)

NATIVE_BINDING_METHODS = {"add_uobject", "add_lambda", "add_raw", "add_sp", "add_static"}
CLEANUP_METHODS = {"remove_dynamic", "remove_all", "remove_handle", "clear"}
ASYNC_HINTS = (
    "AsyncAction",
    "BlueprintAsyncActionBase",
    "UCancellableAsyncAction",
    "K2Node_Async",
    "UK2Node_Async",
)
ABILITY_HINTS = (
    "AbilityTask",
    "GameplayAbility",
    "AbilityTargetDataSetDelegate",
    "PredictionKey",
)

ASYNC_CLASS_DECL_RE = re.compile(
    r"\bclass\s+(?:[A-Za-z_][A-Za-z0-9_]*_API\s+)?(?P<class>[A-Za-z_][A-Za-z0-9_]*)"
    r"\s*:\s*public\s+(?P<base>[A-Za-z_:][A-Za-z0-9_:<>]*)"
)
CPP_METHOD_DEF_RE = re.compile(
    r"^\s*(?:[A-Za-z_][A-Za-z0-9_:<>,~*&\s]+\s+)?"
    r"(?P<class>[A-Za-z_][A-Za-z0-9_]*)::(?P<method>[A-Za-z_][A-Za-z0-9_]*)\s*\("
)
CALLBACK_FIELD_RE = re.compile(r"\b(?P<type>F[A-Za-z_][A-Za-z0-9_]*)\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*;")
FUNCTION_NAME_RE = re.compile(r"\b(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*\(")
ASYNC_FACTORY_RETURN_RE = re.compile(
    r"^\s*(?P<class>[A-Za-z_][A-Za-z0-9_]*)\s*\*\s+(?P=class)::(?P<method>[A-Za-z_][A-Za-z0-9_]*)\s*\("
)
ASYNC_CLEANUP_RE = re.compile(
    r"\b(?:Cancel|SetReadyToDestroy|EndTask|EndAction|OnDestroy|BeginDestroy)\s*\(|"
    r"\.\s*(?:RemoveAll|RemoveDynamic|Remove|Clear|Unbind)\s*\("
)


def iter_source_files(project_root: Path) -> Iterable[Path]:
    for current, dirs, files in os.walk(project_root):
        dirs[:] = [name for name in dirs if name not in base.IGNORED_DIRS]
        current_path = Path(current)
        for file_name in files:
            path = current_path / file_name
            if path.suffix.lower() in SOURCE_SUFFIXES:
                yield path


def relative(path: Path, root: Path) -> str:
    return base.relative(path, root)


def compile_rules() -> Dict[str, re.Pattern[str]]:
    return {rule.key: re.compile(rule.pattern) for rule in PATTERN_RULES}


def context_for_match(lines: Sequence[str], line_index: int) -> str:
    start = max(0, line_index - CONTEXT_RADIUS)
    end = min(len(lines), line_index + CONTEXT_RADIUS + 1)
    return "\n".join(line.rstrip() for line in lines[start:end])


def module_for_path(path: Path, project_root: Path) -> str:
    parts = path.relative_to(project_root).parts
    if parts and parts[0] == "Source" and len(parts) > 1:
        return parts[1]
    if parts and parts[0] == "Plugins" and len(parts) > 1:
        plugin_name = parts[1]
        if len(parts) > 3 and parts[2] == "Source":
            module_name = parts[3]
            if module_name in {"Public", "Private"}:
                module_name = plugin_name
            return f"{plugin_name}/{module_name}"
        return plugin_name
    return "(project)"


def classify_file(pattern_counts: Dict[str, int]) -> Tuple[str, str]:
    readiness = "inventory_only"
    risk = "low"
    for rule in PATTERN_RULES:
        if not pattern_counts.get(rule.key):
            continue
        if READINESS_RANK[rule.readiness] > READINESS_RANK[readiness]:
            readiness = rule.readiness
        if RISK_RANK[rule.risk] > RISK_RANK[risk]:
            risk = rule.risk
    return readiness, risk


def lifecycle_hints_for_path(path: Path) -> Tuple[bool, bool]:
    path_text = path.as_posix()
    return (
        any(hint in path_text for hint in ASYNC_HINTS),
        any(hint in path_text for hint in ABILITY_HINTS),
    )


def find_delegate_site_methods(line: str) -> List[str]:
    return [key for key, pattern in DELEGATE_SITE_PATTERNS if pattern.search(line)]


def classify_delegate_site(
    path: Path,
    line: str,
    context: str,
    file_cleanup_methods: Sequence[str],
) -> Dict[str, str]:
    methods = find_delegate_site_methods(line)
    method_set = set(methods)
    context_blob = f"{path.as_posix()}\n{context}\n{line}"
    b_async_path, b_ability_path = lifecycle_hints_for_path(path)
    b_async_context = b_async_path or any(hint in context_blob for hint in ASYNC_HINTS)
    b_ability_context = b_ability_path or any(hint in line for hint in ABILITY_HINTS)
    b_engine_lifecycle = "engine_lifecycle" in method_set
    b_has_cleanup_in_file = any(method in set(file_cleanup_methods) for method in CLEANUP_METHODS)

    if b_engine_lifecycle:
        return {
            "classification": "engine_lifecycle_native_blocker",
            "conversion_bucket": "native_required",
            "risk": "critical",
            "reason": "Engine/editor/Slate lifecycle delegates depend on subsystem or module shutdown order.",
            "required_before_bp": "Keep native or wrap with explicit subsystem lifecycle policy.",
        }
    if b_ability_context:
        return {
            "classification": "async_or_ability_task_candidate",
            "conversion_bucket": "async_or_ability_task",
            "risk": "critical",
            "reason": "Gameplay Ability or prediction-related delegate context requires GAS-aware async policy.",
            "required_before_bp": "Classify with AbilityTask/GAS policy before any BP graph conversion.",
        }
    if b_async_context:
        return {
            "classification": "async_or_ability_task_candidate",
            "conversion_bucket": "async_or_ability_task",
            "risk": "critical",
            "reason": "Async action or custom K2 async node context usually exposes callback exec topology.",
            "required_before_bp": "Model async proxy callback exec pins before authoring.",
        }
    if method_set & {"add_lambda", "add_raw", "add_sp", "add_static"}:
        return {
            "classification": "native_delegate_lifecycle_blocker",
            "conversion_bucket": "native_required",
            "risk": "critical",
            "reason": "Raw, shared-pointer, lambda, and static delegate bindings do not map safely to ordinary BP events.",
            "required_before_bp": "Keep native or create a reviewed wrapper API.",
        }
    if "add_uobject" in method_set:
        return {
            "classification": "native_delegate_lifecycle_blocker",
            "conversion_bucket": "requires_wrapper_api",
            "risk": "critical",
            "reason": "AddUObject binding depends on UObject lifetime and explicit unbinding or owner teardown.",
            "required_before_bp": "Require wrapper API or verified BP-equivalent dispatcher owner lifecycle.",
        }
    if "add_dynamic" in method_set:
        if b_has_cleanup_in_file:
            return {
                "classification": "bp_event_dispatcher_candidate_with_cleanup",
                "conversion_bucket": "bp_event_dispatcher_candidate",
                "risk": "medium",
                "reason": "Dynamic binding may map to Event Dispatcher lifecycle nodes when target ownership and cleanup are equivalent.",
                "required_before_bp": "Verify target delegate is BlueprintAssignable and preserve paired cleanup topology.",
            }
        return {
            "classification": "dynamic_delegate_requires_unbind_policy",
            "conversion_bucket": "requires_explicit_unbind_policy",
            "risk": "high",
            "reason": "Dynamic binding has no obvious cleanup in the same source file.",
            "required_before_bp": "Add or identify explicit unbind/clear policy before conversion.",
        }
    if method_set & CLEANUP_METHODS:
        return {
            "classification": "explicit_cleanup_observed",
            "conversion_bucket": "inventory_cleanup",
            "risk": "medium",
            "reason": "Cleanup call found; conversion must preserve ordering and target object semantics.",
            "required_before_bp": "Pair cleanup with the corresponding bind site before authoring.",
        }
    return {
        "classification": "delegate_lifecycle_context",
        "conversion_bucket": "inventory_only",
        "risk": "medium",
        "reason": "Delegate lifecycle context found but not enough signal for authoring.",
        "required_before_bp": "Inspect manually before conversion.",
    }


def scan_delegate_lifecycle_sites(project_root: Path, source_files: Sequence[Path]) -> Dict[str, Any]:
    sites: List[Dict[str, Any]] = []
    classification_counts: Counter = Counter()
    bucket_counts: Counter = Counter()
    risk_counts: Counter = Counter()
    module_counts: Counter = Counter()

    for path in sorted(source_files):
        text = base.read_text(path)
        lines = text.splitlines()
        file_method_counts: Counter = Counter()
        for line in lines:
            file_method_counts.update(find_delegate_site_methods(line))
        if not file_method_counts:
            continue

        file_cleanup_methods = [method for method in file_method_counts if method in CLEANUP_METHODS]
        rel = relative(path, project_root)
        module = module_for_path(path, project_root)
        for line_index, line in enumerate(lines):
            methods = find_delegate_site_methods(line)
            if not methods:
                continue
            context = context_for_match(lines, line_index)
            classification = classify_delegate_site(path, line, context, file_cleanup_methods)
            site = {
                "path": rel,
                "line": line_index + 1,
                "module": module,
                "methods": methods,
                "text": line.strip(),
                "context": context,
                "has_cleanup_in_file": bool(file_cleanup_methods),
                **classification,
            }
            sites.append(site)
            classification_counts[site["classification"]] += 1
            bucket_counts[site["conversion_bucket"]] += 1
            risk_counts[site["risk"]] += 1
            module_counts[module] += 1

    priority = {"critical": 3, "high": 2, "medium": 1, "low": 0}
    top_sites = sorted(
        sites,
        key=lambda item: (priority.get(item["risk"], 0), item["conversion_bucket"] != "inventory_cleanup", item["path"], item["line"]),
        reverse=True,
    )[:60]

    return {
        "site_count": len(sites),
        "classification_counts": dict(classification_counts),
        "conversion_bucket_counts": dict(bucket_counts),
        "risk_counts": dict(risk_counts),
        "module_counts": dict(module_counts.most_common(30)),
        "top_sites": top_sites,
    }


def classify_async_class(class_name: str, base_class: str) -> Optional[str]:
    if "UK2Node_Async" in base_class or "K2Node_Async" in class_name or (
        class_name.startswith("UK2Node_") and "Async" in class_name
    ):
        return "custom_k2_async_node"
    if base_class.endswith("UCancellableAsyncAction"):
        return "cancellable_async_action"
    if base_class.endswith("UBlueprintAsyncActionBase"):
        return "blueprint_async_action"
    if base_class.endswith("UAbilityTask") or class_name.startswith("UAbilityTask_") or "AbilityTask_" in class_name:
        return "ability_task"
    return None


def add_unique_line(items: List[Dict[str, Any]], item: Dict[str, Any]) -> None:
    key = (item.get("path"), item.get("line"), item.get("text"), item.get("name"))
    for existing in items:
        if (existing.get("path"), existing.get("line"), existing.get("text"), existing.get("name")) == key:
            return
    items.append(item)


def find_callback_field(lines: Sequence[str], start_index: int) -> Dict[str, str]:
    for offset in range(0, 6):
        if start_index + offset >= len(lines):
            break
        candidate = lines[start_index + offset].strip()
        match = CALLBACK_FIELD_RE.search(candidate)
        if match:
            return {"type": match.group("type"), "name": match.group("name")}
    return {"type": "", "name": ""}


def find_function_name_after_macro(lines: Sequence[str], start_index: int) -> str:
    for offset in range(0, 8):
        if start_index + offset >= len(lines):
            break
        candidate = lines[start_index + offset].strip()
        if not candidate or candidate.startswith(("UFUNCTION", "UPROPERTY", "UCLASS", "GENERATED_")):
            continue
        if "(" not in candidate:
            continue
        matches = list(FUNCTION_NAME_RE.finditer(candidate))
        if matches:
            return matches[-1].group("name")
    return ""


def macro_context(lines: Sequence[str], start_index: int, max_lines: int = 6) -> str:
    collected = []
    for offset in range(0, max_lines):
        if start_index + offset >= len(lines):
            break
        collected.append(lines[start_index + offset].strip())
        if ")" in lines[start_index + offset]:
            break
    return " ".join(collected)


def make_async_entry(path: Path, project_root: Path, line_index: int, line: str, class_name: str, base_class: str, kind: str) -> Dict[str, Any]:
    rel = relative(path, project_root)
    return {
        "class_name": class_name,
        "base_class": base_class,
        "kind": kind,
        "module": module_for_path(path, project_root),
        "declaration": {"path": rel, "line": line_index + 1, "text": line.strip()},
        "source_files": {rel},
        "blueprint_assignable_callbacks": [],
        "factory_functions": [],
        "activate_methods": [],
        "broadcasts": [],
        "cleanup_signals": [],
        "authoring_policy": "inventory_only",
        "required_before_bp": "Model async proxy callback exec pins, delegate output pins, activation, cancellation, and cleanup before authoring.",
    }


def update_async_authoring_policy(entry: Dict[str, Any]) -> None:
    if entry["kind"] in {"ability_task", "custom_k2_async_node"}:
        entry["authoring_policy"] = "native_policy_required"
        entry["required_before_bp"] = "Keep native or implement a reviewed GAS/custom-K2 policy before any BP graph conversion."
        return
    if entry["blueprint_assignable_callbacks"] or entry["broadcasts"]:
        entry["authoring_policy"] = "callback_exec_model_required"
        entry["required_before_bp"] = "Implement async proxy callback exec pin modeling before authoring this as Blueprint graph topology."


def scan_async_proxy_inventory(project_root: Path, source_files: Sequence[Path]) -> Dict[str, Any]:
    classes: Dict[str, Dict[str, Any]] = {}

    for path in sorted(source_files):
        text = base.read_text(path)
        lines = text.splitlines()
        active_class: Optional[str] = None
        class_brace_depth = 0
        class_body_started = False

        for line_index, line in enumerate(lines):
            class_match = ASYNC_CLASS_DECL_RE.search(line)
            if class_match:
                class_name = class_match.group("class")
                base_class = class_match.group("base")
                kind = classify_async_class(class_name, base_class)
                if kind:
                    classes.setdefault(
                        class_name,
                        make_async_entry(path, project_root, line_index, line, class_name, base_class, kind),
                    )
                    active_class = class_name
                    class_body_started = "{" in line
                    class_brace_depth = line.count("{") - line.count("}")
                    if not class_body_started:
                        class_brace_depth = 0
                continue

            if active_class:
                entry = classes[active_class]
                entry["source_files"].add(relative(path, project_root))
                stripped = line.strip()
                if "{" in line:
                    class_body_started = True
                if class_body_started:
                    class_brace_depth += line.count("{") - line.count("}")

                if "BlueprintAssignable" in line:
                    field = find_callback_field(lines, line_index)
                    add_unique_line(
                        entry["blueprint_assignable_callbacks"],
                        {
                            "path": relative(path, project_root),
                            "line": line_index + 1,
                            "text": stripped,
                            **field,
                        },
                    )
                if "UFUNCTION" in line:
                    function_macro = macro_context(lines, line_index)
                else:
                    function_macro = ""
                if (
                    function_macro
                    and "BlueprintCallable" in function_macro
                    and "BlueprintInternalUseOnly" in function_macro
                ):
                    add_unique_line(
                        entry["factory_functions"],
                        {
                            "path": relative(path, project_root),
                            "line": line_index + 1,
                            "text": stripped,
                            "name": find_function_name_after_macro(lines, line_index),
                            "source": "declaration",
                        },
                    )
                if re.search(r"\bActivate\s*\(", line):
                    add_unique_line(
                        entry["activate_methods"],
                        {
                            "path": relative(path, project_root),
                            "line": line_index + 1,
                            "text": stripped,
                            "name": "Activate",
                            "source": "declaration",
                        },
                    )
                if ASYNC_CLEANUP_RE.search(line):
                    add_unique_line(
                        entry["cleanup_signals"],
                        {
                            "path": relative(path, project_root),
                            "line": line_index + 1,
                            "text": stripped,
                            "source": "declaration",
                        },
                    )

                if class_body_started and class_brace_depth <= 0 and "};" in line:
                    active_class = None
                    class_body_started = False

    for path in sorted(source_files):
        text = base.read_text(path)
        lines = text.splitlines()
        active_cpp_class: Optional[str] = None
        function_brace_depth = 0
        function_body_started = False

        for line_index, line in enumerate(lines):
            stripped = line.strip()
            rel = relative(path, project_root)
            factory_match = ASYNC_FACTORY_RETURN_RE.search(line)
            if factory_match and factory_match.group("class") in classes:
                class_name = factory_match.group("class")
                entry = classes[class_name]
                entry["source_files"].add(rel)
                add_unique_line(
                    entry["factory_functions"],
                    {
                        "path": rel,
                        "line": line_index + 1,
                        "text": stripped,
                        "name": factory_match.group("method"),
                        "source": "definition",
                    },
                )

            method_match = CPP_METHOD_DEF_RE.search(line)
            if method_match and method_match.group("class") in classes and not (stripped.endswith(";") and "{" not in line):
                active_cpp_class = method_match.group("class")
                entry = classes[active_cpp_class]
                method_name = method_match.group("method")
                entry["source_files"].add(rel)
                if method_name == "Activate":
                    add_unique_line(
                        entry["activate_methods"],
                        {
                            "path": rel,
                            "line": line_index + 1,
                            "text": stripped,
                            "name": "Activate",
                            "source": "definition",
                        },
                    )
                if method_name in {"Cancel", "SetReadyToDestroy", "EndTask", "EndAction", "OnDestroy", "BeginDestroy"}:
                    add_unique_line(
                        entry["cleanup_signals"],
                        {
                            "path": rel,
                            "line": line_index + 1,
                            "text": stripped,
                            "name": method_name,
                            "source": "definition",
                        },
                    )
                function_body_started = "{" in line
                function_brace_depth = 0

            if active_cpp_class:
                entry = classes[active_cpp_class]
                entry["source_files"].add(rel)
                if ".Broadcast(" in line or ". Broadcast(" in line:
                    add_unique_line(
                        entry["broadcasts"],
                        {
                            "path": rel,
                            "line": line_index + 1,
                            "text": stripped,
                        },
                    )
                if ASYNC_CLEANUP_RE.search(line):
                    add_unique_line(
                        entry["cleanup_signals"],
                        {
                            "path": rel,
                            "line": line_index + 1,
                            "text": stripped,
                        },
                    )

                if "{" in line:
                    function_body_started = True
                if function_body_started:
                    function_brace_depth += line.count("{") - line.count("}")
                if function_body_started and function_brace_depth <= 0:
                    active_cpp_class = None
                    function_body_started = False

    kind_counts: Counter = Counter()
    policy_counts: Counter = Counter()
    module_counts: Counter = Counter()
    class_items: List[Dict[str, Any]] = []
    for entry in classes.values():
        update_async_authoring_policy(entry)
        entry["source_files"] = sorted(entry["source_files"])
        kind_counts[entry["kind"]] += 1
        policy_counts[entry["authoring_policy"]] += 1
        module_counts[entry["module"]] += 1
        class_items.append(entry)

    class_items.sort(
        key=lambda item: (
            item["authoring_policy"] != "inventory_only",
            len(item["blueprint_assignable_callbacks"]),
            len(item["broadcasts"]),
            len(item["factory_functions"]),
            item["class_name"],
        ),
        reverse=True,
    )
    total_callbacks = sum(len(item["blueprint_assignable_callbacks"]) for item in class_items)
    total_factories = sum(len(item["factory_functions"]) for item in class_items)
    total_broadcasts = sum(len(item["broadcasts"]) for item in class_items)

    return {
        "summary": {
            "class_count": len(class_items),
            "kind_counts": dict(kind_counts),
            "authoring_policy_counts": dict(policy_counts),
            "module_counts": dict(module_counts.most_common(20)),
            "classes_with_callback_delegates": sum(1 for item in class_items if item["blueprint_assignable_callbacks"]),
            "classes_with_factory_functions": sum(1 for item in class_items if item["factory_functions"]),
            "classes_with_activate": sum(1 for item in class_items if item["activate_methods"]),
            "classes_with_broadcasts": sum(1 for item in class_items if item["broadcasts"]),
            "classes_with_cleanup_signals": sum(1 for item in class_items if item["cleanup_signals"]),
            "classes_requiring_callback_exec_model": sum(
                1 for item in class_items if item["authoring_policy"] != "inventory_only"
            ),
            "callback_delegate_count": total_callbacks,
            "factory_function_count": total_factories,
            "broadcast_count": total_broadcasts,
        },
        "classes": class_items,
        "top_classes": class_items[:40],
        "authoring_status": "inventory_only_until_async_proxy_callback_exec_model_exists",
    }


def scan_source(project_root: Path) -> Dict[str, Any]:
    compiled = compile_rules()
    rule_by_key = {rule.key: rule for rule in PATTERN_RULES}
    pattern_totals: Counter = Counter()
    files_by_pattern: Dict[str, Counter] = defaultdict(Counter)
    module_counts: Counter = Counter()
    readiness_by_file: Counter = Counter()
    risk_by_file: Counter = Counter()
    examples: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    file_summaries: List[Dict[str, Any]] = []

    files = sorted(iter_source_files(project_root))
    for path in files:
        rel = relative(path, project_root)
        text = base.read_text(path)
        lines = text.splitlines()
        file_counts: Counter = Counter()

        for line_index, line in enumerate(lines):
            for key, pattern in compiled.items():
                matches = pattern.findall(line)
                if not matches:
                    continue
                count = len(matches)
                file_counts[key] += count
                pattern_totals[key] += count
                files_by_pattern[key][rel] += count
                if len(examples[key]) < 12:
                    examples[key].append(
                        {
                            "path": rel,
                            "line": line_index + 1,
                            "text": line.strip(),
                            "context": context_for_match(lines, line_index),
                        }
                    )

        if not file_counts:
            continue

        readiness, risk = classify_file(dict(file_counts))
        module_counts[module_for_path(path, project_root)] += sum(file_counts.values())
        readiness_by_file[readiness] += 1
        risk_by_file[risk] += 1
        file_summaries.append(
            {
                "path": rel,
                "module": module_for_path(path, project_root),
                "counts": dict(file_counts),
                "readiness": readiness,
                "risk": risk,
                "total_hits": sum(file_counts.values()),
            }
        )

    findings = []
    for rule in PATTERN_RULES:
        count = pattern_totals[rule.key]
        if not count:
            continue
        findings.append(
            {
                "key": rule.key,
                "label": rule.label,
                "count": count,
                "file_count": len(files_by_pattern[rule.key]),
                "readiness": rule.readiness,
                "risk": rule.risk,
                "gap": rule.gap,
                "top_files": [
                    {"path": path, "count": file_count}
                    for path, file_count in files_by_pattern[rule.key].most_common(10)
                ],
                "examples": examples[rule.key],
            }
        )

    findings.sort(key=lambda item: (READINESS_RANK[item["readiness"]], RISK_RANK[item["risk"]], item["count"]), reverse=True)
    top_risk_files = sorted(
        file_summaries,
        key=lambda item: (RISK_RANK[item["risk"]], READINESS_RANK[item["readiness"]], item["total_hits"]),
        reverse=True,
    )[:40]

    lifecycle_classifier = scan_delegate_lifecycle_sites(project_root, files)
    async_proxy_inventory = scan_async_proxy_inventory(project_root, files)

    return {
        "source_file_count": len(files),
        "matched_file_count": len(file_summaries),
        "pattern_totals": dict(pattern_totals),
        "readiness_by_file": dict(readiness_by_file),
        "risk_by_file": dict(risk_by_file),
        "module_hit_counts": dict(module_counts.most_common(30)),
        "findings": findings,
        "top_risk_files": top_risk_files,
        "lifecycle_classifier": lifecycle_classifier,
        "async_proxy_inventory": async_proxy_inventory,
    }


def scan_mcp_capabilities(mcp_root: Path, plugin_root: Optional[Path]) -> Dict[str, Any]:
    capabilities = base.scan_mcp_capabilities(mcp_root, plugin_root)
    tool_names = set(capabilities.get("plugin_commands", []))
    for funcs in capabilities.get("python_tools", {}).values():
        tool_names.update(funcs)

    relevant = {
        "can_call_functions": "add_blueprint_call_function_node" in tool_names,
        "can_optionally_allow_latent_function_calls": "add_blueprint_call_function_node" in tool_names,
        "can_list_delegate_graphs": "list_blueprint_graphs" in tool_names,
        "can_create_event_nodes": "add_blueprint_event_node" in tool_names,
        "can_connect_nodes": "connect_blueprint_nodes" in tool_names,
        "can_bind_umg_widget_events": "bind_widget_event" in tool_names,
        "has_event_dispatcher_declaration": "add_blueprint_event_dispatcher" in tool_names,
        "has_event_dispatcher_call_node": "add_blueprint_event_dispatcher_call_node" in tool_names,
        "has_custom_event_node": "add_blueprint_custom_event_node" in tool_names,
        "has_event_dispatcher_bind_node": "add_blueprint_event_dispatcher_bind_node" in tool_names,
        "has_event_dispatcher_unbind_node": "add_blueprint_event_dispatcher_unbind_node" in tool_names,
        "has_event_dispatcher_clear_node": "add_blueprint_event_dispatcher_clear_node" in tool_names,
        "has_event_dispatcher_assign_node": "add_blueprint_event_dispatcher_assign_node" in tool_names,
        "has_generic_delegate_bind_node": any(
            name
            in tool_names
            for name in {
                "add_blueprint_delegate_bind_node",
                "add_blueprint_assign_delegate_node",
                "add_blueprint_delegate_assign_node",
                "add_blueprint_delegate_unbind_node",
                "add_blueprint_delegate_clear_node",
            }
        ),
        "has_async_proxy_node_authoring": any(
            name
            in tool_names
            for name in {"add_blueprint_async_action_node", "add_blueprint_latent_action_node", "add_blueprint_k2_async_node"}
        ),
    }

    gaps = []
    if not relevant["has_event_dispatcher_declaration"]:
        gaps.append("Blueprint Event Dispatcher declaration")
    if not relevant["has_event_dispatcher_call_node"]:
        gaps.append("Blueprint Event Dispatcher call node authoring")
    if not relevant["has_custom_event_node"]:
        gaps.append("custom event node authoring")
    if not relevant["has_event_dispatcher_bind_node"]:
        gaps.append("Blueprint Event Dispatcher bind node authoring")
    if not relevant["has_event_dispatcher_unbind_node"]:
        gaps.append("Blueprint Event Dispatcher unbind node authoring")
    if not relevant["has_event_dispatcher_clear_node"]:
        gaps.append("Blueprint Event Dispatcher clear node authoring")
    if not relevant["has_event_dispatcher_assign_node"]:
        gaps.append("Blueprint Event Dispatcher assign node authoring")
    if not relevant["has_generic_delegate_bind_node"]:
        gaps.append("generic delegate lifecycle authoring for non-Event-Dispatcher targets")
    if not relevant["has_async_proxy_node_authoring"]:
        gaps.append("async proxy node authoring with callback exec pins")
    if relevant["can_optionally_allow_latent_function_calls"]:
        gaps.append("latent call validation exists only as opt-in function-call creation, not full continuation topology")
    if relevant["can_bind_umg_widget_events"]:
        gaps.append("UMG event binding exists, but it is widget-specific and not a generic delegate solution")

    return {
        "raw_capabilities": capabilities,
        "relevant_capabilities": relevant,
        "identified_gaps": gaps,
    }


def build_recommendations(source_scan: Dict[str, Any], mcp_scan: Dict[str, Any]) -> List[Dict[str, Any]]:
    totals = Counter(source_scan["pattern_totals"])
    lifecycle = source_scan.get("lifecycle_classifier", {})
    buckets = Counter(lifecycle.get("conversion_bucket_counts", {}))
    async_inventory = source_scan.get("async_proxy_inventory", {}).get("summary", {})
    return [
        {
            "priority": 1,
            "name": "Native and arbitrary delegate lifecycle classification",
            "trigger_count": buckets.get("native_required", 0)
            + buckets.get("requires_wrapper_api", 0)
            + buckets.get("requires_explicit_unbind_policy", 0),
            "reason": "Lyra includes delegate sites that require native retention, wrapper APIs, or explicit unbind policy even though Blueprint Event Dispatcher lifecycle nodes are now covered.",
            "implementation_hint": "Add lifecycle-aware classification for non-BP-safe native delegates first, then consider generic delegate target authoring only where Blueprint graph semantics are equivalent.",
        },
        {
            "priority": 2,
            "name": "Async proxy node inventory and authoring",
            "trigger_count": async_inventory.get("classes_requiring_callback_exec_model", 0)
            + async_inventory.get("factory_function_count", 0)
            + async_inventory.get("broadcast_count", 0),
            "reason": "Lyra uses async action, cancellable async action, custom K2 async, and AbilityTask classes whose callback delegates and broadcasts need explicit exec-pin topology.",
            "implementation_hint": "Start with read-only async proxy inventory. Authoring should model callback exec pins before any conversion attempt.",
        },
        {
            "priority": 3,
            "name": "Lifecycle delegate safety classifier",
            "trigger_count": totals.get("native_binding", 0) + totals.get("engine_lifecycle_delegate", 0),
            "reason": "Native AddUObject/RemoveAll and engine lifecycle delegates are shutdown-sensitive and should remain native unless explicitly wrapped.",
            "implementation_hint": "Classify World/Core/Slate/Editor delegate sites as native blockers in conversion planning.",
        },
        {
            "priority": 4,
            "name": "GAS AbilityTask-specific async policy",
            "trigger_count": totals.get("ability_task", 0),
            "reason": "AbilityTasks are async Blueprint nodes tied to prediction, ability ownership, and activation lifecycle.",
            "implementation_hint": "Handle as part of the GameplayAbility-specific classifier rather than generic async graph authoring.",
        },
    ]


def build_report(project_root: Path, requested_project_root: str, output_dir: Path, mcp_root: Path, plugin_root: Optional[Path]) -> Dict[str, Any]:
    if base.path_is_relative_to(output_dir, project_root):
        raise ValueError(f"Refusing to write output inside external project: {output_dir}")

    source_scan = scan_source(project_root)
    mcp_scan = scan_mcp_capabilities(mcp_root, plugin_root)
    recommendations = build_recommendations(source_scan, mcp_scan)
    verdict = {
        "minimum_stable_scope": "delegate_async_gap_classification",
        "current_status": "not_ready_for_generic_delegate_or_async_proxy_authoring",
        "safe_now": [
            "inventory delegate/async/latent sites",
            "create ordinary event/function/call nodes",
            "declare and call Blueprint Event Dispatchers with signature graphs",
            "bind Blueprint Event Dispatchers to signature-compatible custom events",
            "assign, unbind, and clear Blueprint Event Dispatcher lifecycle nodes",
            "optionally create latent function call nodes when explicitly allowed",
            "bind some UMG widget events through existing UMG-specific command",
        ],
        "unsafe_without_reinforcement": [
            "generic delegate lifecycle authoring for non-Event-Dispatcher targets",
            "native or arbitrary delegate target binding without lifecycle classification",
            "async action proxy nodes with callback exec outputs",
            "native AddUObject/AddLambda lifecycle conversion",
            "AbilityTask conversion",
            "custom K2 async node recreation",
        ],
    }
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_kind": "lyra_delegate_latent_async_readiness",
        "read_only_project_root": str(project_root),
        "requested_project_root": requested_project_root,
        "output_dir": str(output_dir),
        "source_scan": source_scan,
        "mcp_capability_scan": mcp_scan,
        "recommendations": recommendations,
        "verdict": verdict,
        "read_only_policy": {
            "project_mutation_allowed": False,
            "asset_loading_performed": False,
            "editor_required": False,
            "writes_allowed_only_under_output_dir": True,
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


def format_findings(findings: Sequence[Dict[str, Any]], limit: int = 20) -> str:
    if not findings:
        return "No findings.\n"
    lines = ["| Pattern | Readiness | Risk | Hits | Files | Gap |", "| --- | --- | --- | ---: | ---: | --- |"]
    for item in findings[:limit]:
        lines.append(
            f"| {item['label']} | `{item['readiness']}` | `{item['risk']}` | {item['count']} | {item['file_count']} | {item['gap']} |"
        )
    return "\n".join(lines) + "\n"


def format_top_files(files: Sequence[Dict[str, Any]], limit: int = 20) -> str:
    if not files:
        return "- none\n"
    lines = []
    for item in files[:limit]:
        keys = ", ".join(sorted(item["counts"].keys())[:6])
        lines.append(f"- `{item['path']}`: `{item['risk']}` / `{item['readiness']}`, hits `{item['total_hits']}` ({keys})")
    return "\n".join(lines) + "\n"


def format_lifecycle_sites(sites: Sequence[Dict[str, Any]], limit: int = 30) -> str:
    if not sites:
        return "- none\n"
    lines = []
    for item in sites[:limit]:
        methods = ", ".join(item.get("methods", []))
        lines.append(
            f"- `{item['path']}:{item['line']}` `{item['classification']}` / `{item['conversion_bucket']}` "
            f"({methods}): {item['reason']}"
        )
    return "\n".join(lines) + "\n"


def format_async_proxy_classes(classes: Sequence[Dict[str, Any]], limit: int = 30) -> str:
    if not classes:
        return "- none\n"
    lines = []
    for item in classes[:limit]:
        declaration = item.get("declaration", {})
        lines.append(
            f"- `{item['class_name']}` `{item['kind']}` / `{item['authoring_policy']}` "
            f"at `{declaration.get('path', '')}:{declaration.get('line', '')}` "
            f"(callbacks `{len(item.get('blueprint_assignable_callbacks', []))}`, "
            f"factories `{len(item.get('factory_functions', []))}`, "
            f"activate `{len(item.get('activate_methods', []))}`, "
            f"broadcasts `{len(item.get('broadcasts', []))}`, "
            f"cleanup `{len(item.get('cleanup_signals', []))}`)"
        )
    return "\n".join(lines) + "\n"


def render_markdown(report: Dict[str, Any]) -> str:
    scan = report["source_scan"]
    caps = report["mcp_capability_scan"]
    verdict = report["verdict"]
    lifecycle = scan.get("lifecycle_classifier", {})
    async_inventory = scan.get("async_proxy_inventory", {})
    async_summary = async_inventory.get("summary", {})
    lines = [
        "# Lyra Delegate / Latent / Async Readiness",
        "",
        f"- Generated UTC: `{report['generated_at']}`",
        f"- Read-only project root: `{report['read_only_project_root']}`",
        f"- Output dir: `{report['output_dir']}`",
        f"- Minimum stable scope: `{verdict['minimum_stable_scope']}`",
        f"- Current status: `{verdict['current_status']}`",
        "",
        "## Executive Result",
        "",
        "Lyra has enough native delegate, arbitrary delegate target, latent, and async callback topology that generic C++ to BP conversion should stay blocked here. Blueprint Event Dispatcher lifecycle authoring is covered, but native lifecycle classification and async proxy node authoring are still required.",
        "",
        "## Source Scan",
        "",
        f"- Source files scanned: `{scan['source_file_count']}`",
        f"- Files with delegate/async/latent matches: `{scan['matched_file_count']}`",
        "",
        "### Pattern Findings",
        "",
        format_findings(scan["findings"]),
        "### Readiness By File",
        "",
        format_count_map(scan["readiness_by_file"]),
        "### Risk By File",
        "",
        format_count_map(scan["risk_by_file"]),
        "### Module Hit Counts",
        "",
        format_count_map(scan["module_hit_counts"]),
        "## Delegate Lifecycle Classifier",
        "",
        f"- Classified delegate lifecycle sites: `{lifecycle.get('site_count', 0)}`",
        "",
        "### Conversion Buckets",
        "",
        format_count_map(lifecycle.get("conversion_bucket_counts", {})),
        "### Lifecycle Classifications",
        "",
        format_count_map(lifecycle.get("classification_counts", {})),
        "### Top Lifecycle Blockers",
        "",
        format_lifecycle_sites(lifecycle.get("top_sites", [])),
        "## Async Proxy Callback Inventory",
        "",
        f"- Async proxy classes: `{async_summary.get('class_count', 0)}`",
        f"- Classes requiring callback exec/native policy: `{async_summary.get('classes_requiring_callback_exec_model', 0)}`",
        f"- BlueprintAssignable callback fields: `{async_summary.get('callback_delegate_count', 0)}`",
        f"- Factory functions: `{async_summary.get('factory_function_count', 0)}`",
        f"- Broadcast sites: `{async_summary.get('broadcast_count', 0)}`",
        f"- Authoring status: `{async_inventory.get('authoring_status', 'inventory_only')}`",
        "",
        "### Async Class Kinds",
        "",
        format_count_map(async_summary.get("kind_counts", {})),
        "### Async Authoring Policy Counts",
        "",
        format_count_map(async_summary.get("authoring_policy_counts", {})),
        "### Top Async Proxy Classes",
        "",
        format_async_proxy_classes(async_inventory.get("top_classes", [])),
        "## MCP Capability Match",
        "",
        format_count_map(caps["relevant_capabilities"]),
        "### Identified Gaps",
        "",
    ]
    lines.extend(f"- {gap}" for gap in caps["identified_gaps"])
    lines.extend(["", "## Top Risk Files", "", format_top_files(scan["top_risk_files"])])
    lines.extend(["## Recommendations", ""])
    for item in report["recommendations"]:
        lines.append(f"- `{item['priority']}` {item['name']}: {item['reason']} Trigger count: `{item['trigger_count']}`.")
    lines.extend(["", "## Safe Now", ""])
    lines.extend(f"- {item}" for item in verdict["safe_now"])
    lines.extend(["", "## Unsafe Without Reinforcement", ""])
    lines.extend(f"- {item}" for item in verdict["unsafe_without_reinforcement"])
    return "\n".join(lines) + "\n"


def write_report(report: Dict[str, Any], output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "lyra_delegate_latent_async_readiness_report.json"
    md_path = output_dir / "lyra_delegate_latent_async_readiness_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def build_arg_parser() -> argparse.ArgumentParser:
    repo_root = base.repo_root_from_script()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default="", help="External Unreal project root. Defaults to known Lyra candidates.")
    parser.add_argument(
        "--mcp-root",
        default=str(repo_root),
        help="unreal-mcp-cubeless repository root.",
    )
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
    project_root, _notes = base.resolve_project_root(args.project_root or None)
    output_dir = Path(args.output_dir).resolve()
    mcp_root = Path(args.mcp_root).resolve()
    plugin_root = Path(args.plugin_root).resolve() if args.plugin_root else None

    report = build_report(project_root, args.project_root, output_dir, mcp_root, plugin_root)
    if not args.no_write:
        json_path, md_path = write_report(report, output_dir)
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")

    print(f"Project: {project_root}")
    print(f"Matched files: {report['source_scan']['matched_file_count']}")
    print(f"Status: {report['verdict']['current_status']}")
    print(f"Top recommendation: {report['recommendations'][0]['name']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
