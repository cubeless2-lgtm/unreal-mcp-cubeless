#!/usr/bin/env python
"""
Blueprint authoring request planner for the current UnrealMCP capability ceiling.

The planner is intentionally conservative: when a request mixes safe Blueprint
graph glue with blocked native systems, the whole request is blocked until the
blocked part is separated or reinforced. Ambiguous requests require review
rather than being treated as safe to author.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

import external_project_readiness_analyzer as base


STATUS_SAFE = "safe_to_author"
STATUS_REVIEW = "requires_review"
STATUS_BLOCKED = "blocked_until_reinforced"


@dataclass(frozen=True)
class PlannerRule:
    key: str
    label: str
    status: str
    patterns: Tuple[str, ...]
    needed_tools: Tuple[str, ...]
    guidance: str
    validation: Tuple[str, ...]


SAFE_RULES: Tuple[PlannerRule, ...] = (
    PlannerRule(
        key="blueprint_shell",
        label="Blueprint shell / class setup",
        status=STATUS_SAFE,
        patterns=(
            r"\b(actor|pawn|character|component)\s+blueprint\b",
            r"\bblueprint\s+(class|shell|actor|component)\b",
            r"\bbp\s+(class|actor|component|shell)\b",
        ),
        needed_tools=("create_blueprint", "compile_and_validate_blueprint"),
        guidance="Create a narrow Blueprint shell using an existing parent class; keep native behavior in native classes.",
        validation=("resolve_blueprint", "compile_and_validate_blueprint"),
    ),
    PlannerRule(
        key="component_setup",
        label="Component composition",
        status=STATUS_SAFE,
        patterns=(r"\badd\s+component\b", r"\bcomponent\s+setup\b", r"\bstatic mesh component\b", r"\bscene component\b"),
        needed_tools=("add_component_to_blueprint", "list_blueprint_components", "get_component_property", "set_component_property"),
        guidance="Add existing component classes and set exposed defaults; do not recreate native component internals.",
        validation=("resolve_blueprint", "compile_and_validate_blueprint"),
    ),
    PlannerRule(
        key="variables_defaults",
        label="Variables and defaults",
        status=STATUS_SAFE,
        patterns=(r"\bvariable\b", r"\bmember\b", r"\bdefault value\b", r"\bproperty\b", r"\bexposed\b"),
        needed_tools=("add_blueprint_variable", "set_blueprint_pin_default"),
        guidance="Add Blueprint variables with explicit type/default metadata and expose only requested controls.",
        validation=("resolve_blueprint", "compile_and_validate_blueprint"),
    ),
    PlannerRule(
        key="function_graph_glue",
        label="Function calls and graph glue",
        status=STATUS_SAFE,
        patterns=(
            r"\bfunction call\b",
            r"\bcall function\b",
            r"\bfunction graph\b",
            r"\bfunction parameter\b",
            r"\breturn node\b",
            r"\bgenerated function\b",
            r"\blocal variable\b",
            r"\bmath node\b",
            r"\bcompare\b",
            r"\bgreater than\b",
            r"\bdataflow\b",
            r"\bbranch\b",
            r"\bsequence\b",
            r"\bloop\b",
            r"\barray\b",
        ),
        needed_tools=(
            "resolve_blueprint_graph",
            "add_blueprint_function_parameter",
            "add_blueprint_local_variable",
            "add_blueprint_variable_get_node",
            "add_blueprint_variable_set_node",
            "add_blueprint_self_reference",
            "add_blueprint_math_node",
            "add_blueprint_compare_node",
            "add_blueprint_return_node",
            "add_blueprint_call_function_node",
            "add_blueprint_branch_node",
            "add_blueprint_sequence_node",
            "connect_blueprint_nodes",
        ),
        guidance="Author ordinary reflected function calls and simple control-flow glue only.",
        validation=("list_blueprint_nodes", "compile_and_validate_blueprint"),
    ),
    PlannerRule(
        key="event_dispatcher_lifecycle",
        label="Blueprint Event Dispatcher lifecycle",
        status=STATUS_SAFE,
        patterns=(
            r"\bevent dispatcher\b",
            r"\bblueprintassignable\b",
            r"\bdispatcher\s+(bind|assign|unbind|clear|call|broadcast)\b",
        ),
        needed_tools=(
            "add_blueprint_event_dispatcher",
            "add_blueprint_event_dispatcher_call_node",
            "add_blueprint_custom_event_node",
            "add_blueprint_event_dispatcher_bind_node",
            "add_blueprint_event_dispatcher_assign_node",
            "add_blueprint_event_dispatcher_unbind_node",
            "add_blueprint_event_dispatcher_clear_node",
            "connect_blueprint_nodes",
        ),
        guidance="Use Blueprint Event Dispatcher primitives only when the delegate owner and cleanup semantics are Blueprint-equivalent.",
        validation=("list_blueprint_graphs", "list_blueprint_nodes", "compile_and_validate_blueprint"),
    ),
    PlannerRule(
        key="enhanced_input_glue",
        label="Enhanced Input event glue",
        status=STATUS_SAFE,
        patterns=(r"\benhanced input\b", r"\binput action\b", r"\binput mapping\b"),
        needed_tools=("create_input_mapping", "add_blueprint_enhanced_input_action_node", "connect_blueprint_nodes"),
        guidance="Author input event glue against existing InputAction/InputMapping assets; do not infer trigger/modifier asset semantics.",
        validation=("list_blueprint_nodes", "compile_and_validate_blueprint"),
    ),
)


REVIEW_RULES: Tuple[PlannerRule, ...] = (
    PlannerRule(
        key="latent_function",
        label="Latent function call",
        status=STATUS_REVIEW,
        patterns=(r"\blatent\b", r"\bdelay\b", r"\btimeline\b", r"\basync load\b"),
        needed_tools=("add_blueprint_call_function_node",),
        guidance="Latent calls are opt-in only; continuation ordering and world-context pins must be reviewed before authoring.",
        validation=("list_blueprint_nodes", "compile_and_validate_blueprint", "manual continuation review"),
    ),
    PlannerRule(
        key="umg_widget_event",
        label="UMG widget event binding",
        status=STATUS_REVIEW,
        patterns=(r"\bumg\b", r"\buserwidget\b", r"\bwidget blueprint\b", r"\bbutton click\b", r"\bwidget event\b"),
        needed_tools=("bind_widget_event", "add_blueprint_event_node", "connect_blueprint_nodes"),
        guidance="Widget-specific event binding can be reviewed, but widget tree construction and layout policy are not generic BP graph work.",
        validation=("list_blueprint_nodes", "compile_and_validate_blueprint", "editor widget smoke when available"),
    ),
    PlannerRule(
        key="graph_glue_from_unclear_logic",
        label="Unclear C++ logic lowering",
        status=STATUS_REVIEW,
        patterns=(r"\bconvert\s+c\+\+\b", r"\bcode\s+level\b", r"\bsame as c\+\+\b", r"\bport\s+this\b"),
        needed_tools=("list_blueprint_nodes", "compile_and_validate_blueprint"),
        guidance="Split the request into reflected calls, simple flow, and blocked native behavior before authoring.",
        validation=("planner review", "compile_and_validate_blueprint"),
    ),
)


BLOCKED_RULES: Tuple[PlannerRule, ...] = (
    PlannerRule(
        key="native_delegate_lifecycle",
        label="Native or arbitrary delegate lifecycle",
        status=STATUS_BLOCKED,
        patterns=(
            r"\badddynamic\b",
            r"\badduobject\b",
            r"\baddlambda\b",
            r"\bremoveall\b",
            r"\bremove dynamic\b",
            r"\bnative delegate\b",
            r"\barbitrary delegate\b",
            r"\bdelegate lifecycle\b",
        ),
        needed_tools=(),
        guidance="Native/arbitrary delegate binding needs owner-lifetime and explicit cleanup policy before BP authoring.",
        validation=("delegate lifecycle classifier", "manual owner/cleanup review"),
    ),
    PlannerRule(
        key="generic_delegate_without_dispatcher",
        label="Generic delegate request without Event Dispatcher scope",
        status=STATUS_BLOCKED,
        patterns=(r"\bdelegate\b",),
        needed_tools=(),
        guidance="Generic delegate requests are blocked unless narrowed to Blueprint Event Dispatcher lifecycle primitives.",
        validation=("delegate lifecycle classifier",),
    ),
    PlannerRule(
        key="async_proxy_callback_exec",
        label="Async proxy callback exec topology",
        status=STATUS_BLOCKED,
        patterns=(
            r"\basync action\b",
            r"\basync proxy\b",
            r"\bblueprintasyncactionbase\b",
            r"\bcancellableasyncaction\b",
            r"\bcallback exec\b",
            r"\bactivate\(\)",
        ),
        needed_tools=(),
        guidance="Async proxy nodes need callback exec pin, payload pin, activation, cancellation, and cleanup modeling first.",
        validation=("async proxy callback inventory",),
    ),
    PlannerRule(
        key="gas_ability_task",
        label="Gameplay Ability System / AbilityTask",
        status=STATUS_BLOCKED,
        patterns=(r"\bgas\b", r"\bgameplay ability\b", r"\babilitytask\b", r"\bability task\b", r"\bprediction\b"),
        needed_tools=(),
        guidance="GAS internals and AbilityTasks require domain-specific native policy and prediction-safe authoring.",
        validation=("GAS classifier", "native review"),
    ),
    PlannerRule(
        key="replication_rpc",
        label="Replication, RPC, or ReplicationGraph",
        status=STATUS_BLOCKED,
        patterns=(r"\breplication\b", r"\breplicated\b", r"\brpc\b", r"\bserver\b", r"\bclient\b", r"\bnetmulticast\b", r"\breplicationgraph\b"),
        needed_tools=(),
        guidance="Replication and RPC authority policy are native-blocked for generic C++ to BP lowering.",
        validation=("native networking review",),
    ),
    PlannerRule(
        key="commonui_structure",
        label="CommonUI structure or activation policy",
        status=STATUS_BLOCKED,
        patterns=(r"\bcommonui\b", r"\bcommon activatable\b", r"\bactivatable widget\b", r"\bui layer\b", r"\bactivation policy\b"),
        needed_tools=(),
        guidance="CommonUI widget tree, layer, and activation policy authoring need dedicated tooling before BP generation.",
        validation=("CommonUI/UMG structure inventory",),
    ),
    PlannerRule(
        key="animation_blueprint",
        label="Animation Blueprint graph or state machine",
        status=STATUS_BLOCKED,
        patterns=(r"\banimation blueprint\b", r"\banim blueprint\b", r"\banimbp\b", r"\banimgraph\b", r"\bstate machine\b"),
        needed_tools=(),
        guidance="AnimGraph and state-machine authoring are outside current generic Blueprint graph tooling.",
        validation=("AnimBP graph inventory",),
    ),
    PlannerRule(
        key="custom_k2_node",
        label="Custom K2 / editor graph extension",
        status=STATUS_BLOCKED,
        patterns=(r"\buk2node\b", r"\bk2node\b", r"\bcustom k2\b", r"\bexpandnode\b"),
        needed_tools=(),
        guidance="Custom K2 expansion behavior is native editor code and cannot be recreated with generic BP graph nodes.",
        validation=("native editor/K2 review",),
    ),
    PlannerRule(
        key="gamefeature_architecture",
        label="GameFeature or Experience architecture",
        status=STATUS_BLOCKED,
        patterns=(r"\bgamefeature\b", r"\bgame feature\b", r"\bexperience\b", r"\bmodular gameplay\b"),
        needed_tools=(),
        guidance="GameFeature activation and experience architecture are project-level systems, not generic BP graph glue.",
        validation=("GameFeature architecture review",),
    ),
    PlannerRule(
        key="slate_editor_cpp",
        label="Slate or editor-only C++ behavior",
        status=STATUS_BLOCKED,
        patterns=(r"\bslate\b", r"\bscompoundwidget\b", r"\beditor module\b", r"\basset action\b", r"\bcommandlet\b"),
        needed_tools=(),
        guidance="Slate/editor module behavior should stay native unless a dedicated editor tooling path is implemented.",
        validation=("Unreal C++ editor lifecycle review",),
    ),
)


DEFAULT_SAMPLE_REQUESTS: Tuple[Tuple[str, str], ...] = (
    (
        "simple_actor_bp",
        "Create an Actor Blueprint shell with a Static Mesh Component, exposed health variable, BeginPlay event, branch, and function call.",
    ),
    (
        "component_function_glue",
        "Make a Blueprint component setup that calls an existing reflected function and connects simple branch flow.",
    ),
    (
        "component_hierarchy",
        "Create an Actor Blueprint shell with a Scene Component root and a child Static Mesh Component attached to that root.",
    ),
    (
        "component_property_defaults",
        "Create an Actor Blueprint shell with a Static Mesh Component visibility false.",
    ),
    (
        "function_graph_body_math",
        "Create a function graph with a local variable, math node, dataflow, and return node.",
    ),
    (
        "function_graph_local_set",
        "Create a function graph with an input parameter, math node, local variable set node, and return node.",
    ),
    (
        "function_graph_compare_branch",
        "Create a function graph with an input parameter, compare node, branch, then and else local variable set nodes, and return node.",
    ),
    (
        "typed_variables_defaults",
        "Create an Actor Blueprint shell with a Scene Component, bool variable default, string variable default, and vector variable default.",
    ),
    (
        "event_sequence_flow",
        "Create an Actor Blueprint shell with BeginPlay, a Sequence node, and two PrintString calls.",
    ),
    (
        "generated_function_invocation",
        "Create a function graph and call the generated function from BeginPlay with an input default, then store the output in a variable.",
    ),
    (
        "event_dispatcher_lifecycle",
        "Create a Blueprint Event Dispatcher, call it, bind it to a compatible custom event, assign it, unbind it, and clear it.",
    ),
    (
        "async_proxy_request",
        "Convert a UBlueprintAsyncActionBase async action with callback exec pins, Activate(), Broadcast(), and cancellation cleanup.",
    ),
    (
        "gas_replication_request",
        "Build a Gameplay Ability with AbilityTask prediction and replicated Server RPC state changes.",
    ),
    (
        "commonui_request",
        "Create a CommonUI activatable widget tree with layer activation policy and back handling.",
    ),
)


def compile_patterns(patterns: Iterable[str]) -> Tuple[re.Pattern[str], ...]:
    return tuple(re.compile(pattern, re.IGNORECASE) for pattern in patterns)


COMPILED_RULES: Tuple[Tuple[PlannerRule, Tuple[re.Pattern[str], ...]], ...] = tuple(
    (rule, compile_patterns(rule.patterns)) for rule in (*BLOCKED_RULES, *REVIEW_RULES, *SAFE_RULES)
)


def repo_root_from_script() -> Path:
    return base.repo_root_from_script()


def load_json_if_exists(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def normalize_request(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def rule_matches(rule_patterns: Sequence[re.Pattern[str]], text: str) -> bool:
    return any(pattern.search(text) for pattern in rule_patterns)


def is_event_dispatcher_scoped(text: str) -> bool:
    return bool(re.search(r"\bevent dispatcher\b|\bblueprintassignable\b|\bdispatcher\s+(bind|assign|unbind|clear|call|broadcast)\b", text, re.IGNORECASE))


def filter_false_blockers(matches: List[PlannerRule], text: str) -> List[PlannerRule]:
    filtered: List[PlannerRule] = []
    for rule in matches:
        if rule.key == "generic_delegate_without_dispatcher" and is_event_dispatcher_scoped(text):
            continue
        filtered.append(rule)
    return filtered


def choose_status(matched_rules: Sequence[PlannerRule]) -> str:
    if any(rule.status == STATUS_BLOCKED for rule in matched_rules):
        return STATUS_BLOCKED
    if any(rule.status == STATUS_REVIEW for rule in matched_rules):
        return STATUS_REVIEW
    if any(rule.status == STATUS_SAFE for rule in matched_rules):
        return STATUS_SAFE
    return STATUS_REVIEW


def status_reason(status: str, matched_rules: Sequence[PlannerRule]) -> str:
    if not matched_rules:
        return "No known-safe authoring pattern was detected; request needs review before tool execution."
    if status == STATUS_BLOCKED:
        labels = ", ".join(rule.label for rule in matched_rules if rule.status == STATUS_BLOCKED)
        return f"Blocked patterns detected: {labels}."
    if status == STATUS_REVIEW:
        labels = ", ".join(rule.label for rule in matched_rules if rule.status == STATUS_REVIEW)
        return f"Review-required patterns detected: {labels}."
    labels = ", ".join(rule.label for rule in matched_rules if rule.status == STATUS_SAFE)
    return f"Only currently safe authoring patterns detected: {labels}."


def unique(items: Iterable[str]) -> List[str]:
    seen = set()
    result = []
    for item in items:
        if not item or item in seen:
            continue
        seen.add(item)
        result.append(item)
    return result


def plan_request(request_id: str, request_text: str, target_class: str = "") -> Dict[str, Any]:
    normalized = normalize_request(request_text)
    matched_rules = [
        rule
        for rule, patterns in COMPILED_RULES
        if rule_matches(patterns, normalized)
    ]
    matched_rules = filter_false_blockers(matched_rules, normalized)
    status = choose_status(matched_rules)

    safe_rules = [rule for rule in matched_rules if rule.status == STATUS_SAFE]
    review_rules = [rule for rule in matched_rules if rule.status == STATUS_REVIEW]
    blocked_rules = [rule for rule in matched_rules if rule.status == STATUS_BLOCKED]

    safe_steps = [
        {
            "key": rule.key,
            "label": rule.label,
            "guidance": rule.guidance,
            "tools": list(rule.needed_tools),
        }
        for rule in safe_rules
    ]
    requires_review = [
        {
            "key": rule.key,
            "label": rule.label,
            "reason": rule.guidance,
            "validation": list(rule.validation),
        }
        for rule in review_rules
    ]
    blocked_items = [
        {
            "key": rule.key,
            "label": rule.label,
            "reason": rule.guidance,
            "required_before_authoring": list(rule.validation),
        }
        for rule in blocked_rules
    ]
    if not matched_rules:
        requires_review.append(
            {
                "key": "insufficient_specificity",
                "label": "Insufficiently specific BP request",
                "reason": "Planner could not map the request to a known-safe UnrealMCP BP authoring path.",
                "validation": ["clarify target parent class", "identify graph events/functions", "rerun planner"],
            }
        )

    needed_tools = unique(tool for rule in safe_rules + review_rules for tool in rule.needed_tools)
    validation_plan = unique(
        [
            "resolve_blueprint or create under /Game/_MCP_Temp for smoke when possible",
            *[step for rule in safe_rules + review_rules for step in rule.validation],
            "compile_and_validate_blueprint before save",
            "list_blueprint_nodes after authoring",
        ]
    )
    if status == STATUS_BLOCKED:
        validation_plan = unique(
            [
                *[step for rule in blocked_rules for step in rule.validation],
                "do not author Blueprint graph until blocked items are removed or reinforced",
            ]
        )

    return {
        "id": request_id,
        "request": normalized,
        "target_class": target_class,
        "status": status,
        "reason": status_reason(status, matched_rules),
        "matched_rules": [
            {
                "key": rule.key,
                "label": rule.label,
                "status": rule.status,
            }
            for rule in matched_rules
        ],
        "safe_steps": safe_steps,
        "requires_review": requires_review,
        "blocked_items": blocked_items,
        "needed_mcp_tools": needed_tools,
        "validation_plan": validation_plan,
        "false_safe_guard": "Any blocked match overrides safe steps. Requests with no known-safe match require review.",
    }


def build_policy_basis(
    quality_gate_report: Dict[str, Any],
    combined_report: Dict[str, Any],
    delegate_report: Dict[str, Any],
) -> Dict[str, Any]:
    quality_verdict = quality_gate_report.get("verdict", {})
    combined_verdict = combined_report.get("verdict", {})
    delegate_verdict = delegate_report.get("verdict", {})
    async_summary = delegate_report.get("source_scan", {}).get("async_proxy_inventory", {}).get("summary", {})
    lifecycle_summary = delegate_report.get("source_scan", {}).get("lifecycle_classifier", {})
    return {
        "quality_gate_status": quality_verdict.get("status", "unknown"),
        "current_authoring_ceiling": combined_verdict.get(
            "current_authoring_ceiling",
            "temporary_smoke_only_bp_shells_allowlisted_actor_parent_component_hierarchy_property_graph_glue_validation_durable_read_only_asset_exists_preflight_overwrite_rename_decision_save_gate_rollback_draft_executor_readiness_checklist_and_disabled_executor_skeleton",
        ),
        "safe_now": delegate_verdict.get("safe_now", []),
        "not_ready_for": combined_verdict.get("not_ready_for", []),
        "unsafe_without_reinforcement": delegate_verdict.get("unsafe_without_reinforcement", []),
        "delegate_lifecycle_sites": lifecycle_summary.get("site_count", 0),
        "async_proxy_classes": async_summary.get("class_count", 0),
        "async_proxy_classes_requiring_policy": async_summary.get("classes_requiring_callback_exec_model", 0),
    }


def summarize_plans(plans: Sequence[Dict[str, Any]]) -> Dict[str, Any]:
    status_counts = Counter(plan["status"] for plan in plans)
    blocked_rule_counts: Counter = Counter()
    review_rule_counts: Counter = Counter()
    safe_rule_counts: Counter = Counter()
    for plan in plans:
        for rule in plan["matched_rules"]:
            if rule["status"] == STATUS_BLOCKED:
                blocked_rule_counts[rule["key"]] += 1
            elif rule["status"] == STATUS_REVIEW:
                review_rule_counts[rule["key"]] += 1
            elif rule["status"] == STATUS_SAFE:
                safe_rule_counts[rule["key"]] += 1
    return {
        "request_count": len(plans),
        "status_counts": dict(status_counts),
        "safe_rule_counts": dict(safe_rule_counts),
        "review_rule_counts": dict(review_rule_counts),
        "blocked_rule_counts": dict(blocked_rule_counts),
    }


def build_report(
    requests: Sequence[Tuple[str, str]],
    output_dir: Path,
    quality_gate_report: Dict[str, Any],
    combined_report: Dict[str, Any],
    delegate_report: Dict[str, Any],
    target_class: str = "",
) -> Dict[str, Any]:
    plans = [plan_request(request_id, request_text, target_class) for request_id, request_text in requests]
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "analysis_kind": "bp_authoring_quality_planner",
        "planner_version": "section_10_initial",
        "output_dir": str(output_dir),
        "policy_basis": build_policy_basis(quality_gate_report, combined_report, delegate_report),
        "summary": summarize_plans(plans),
        "plans": plans,
        "policy": {
            "status_priority": [STATUS_BLOCKED, STATUS_REVIEW, STATUS_SAFE],
            "default_for_unknown_requests": STATUS_REVIEW,
            "lyra_specific_content_dependency": False,
            "cxx_changes_required": False,
        },
    }


def format_count_map(data: Dict[str, Any]) -> str:
    if not data:
        return "- none\n"
    return "\n".join(f"- `{key}`: {value}" for key, value in data.items()) + "\n"


def render_markdown(report: Dict[str, Any]) -> str:
    basis = report["policy_basis"]
    summary = report["summary"]
    lines = [
        "# BP Authoring Quality Planner",
        "",
        f"- Generated UTC: `{report['generated_at']}`",
        f"- Planner version: `{report['planner_version']}`",
        f"- Current authoring ceiling: `{basis['current_authoring_ceiling']}`",
        f"- Quality gate status: `{basis['quality_gate_status']}`",
        f"- Delegate lifecycle sites from Lyra intake: `{basis['delegate_lifecycle_sites']}`",
        f"- Async proxy classes from Lyra intake: `{basis['async_proxy_classes']}`",
        "",
        "## Summary",
        "",
        f"- Requests planned: `{summary['request_count']}`",
        "",
        "### Status Counts",
        "",
        format_count_map(summary["status_counts"]),
        "### Safe Rule Counts",
        "",
        format_count_map(summary["safe_rule_counts"]),
        "### Review Rule Counts",
        "",
        format_count_map(summary["review_rule_counts"]),
        "### Blocked Rule Counts",
        "",
        format_count_map(summary["blocked_rule_counts"]),
        "## Plans",
        "",
    ]
    for plan in report["plans"]:
        lines.extend(
            [
                f"### {plan['id']}",
                "",
                f"- Status: `{plan['status']}`",
                f"- Request: {plan['request']}",
                f"- Reason: {plan['reason']}",
                "",
                "Safe steps:",
            ]
        )
        if plan["safe_steps"]:
            lines.extend(f"- `{item['key']}`: {item['guidance']}" for item in plan["safe_steps"])
        else:
            lines.append("- none")
        lines.append("")
        lines.append("Requires review:")
        if plan["requires_review"]:
            lines.extend(f"- `{item['key']}`: {item['reason']}" for item in plan["requires_review"])
        else:
            lines.append("- none")
        lines.append("")
        lines.append("Blocked items:")
        if plan["blocked_items"]:
            lines.extend(f"- `{item['key']}`: {item['reason']}" for item in plan["blocked_items"])
        else:
            lines.append("- none")
        lines.append("")
        lines.append("Needed MCP tools:")
        if plan["needed_mcp_tools"]:
            lines.extend(f"- `{tool}`" for tool in plan["needed_mcp_tools"])
        else:
            lines.append("- none")
        lines.append("")
        lines.append("Validation plan:")
        lines.extend(f"- {step}" for step in plan["validation_plan"])
        lines.append("")
    lines.extend(
        [
            "## Policy",
            "",
            "- Blocked matches override safe matches.",
            "- Requests with no known-safe match require review.",
            "- Lyra intake informs the policy, but rule matching does not depend on Lyra content names.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_report(report: Dict[str, Any], output_dir: Path) -> Tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "bp_authoring_quality_planner_report.json"
    md_path = output_dir / "bp_authoring_quality_planner_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    md_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, md_path


def request_pairs_from_args(requests: Sequence[str]) -> List[Tuple[str, str]]:
    if not requests:
        return list(DEFAULT_SAMPLE_REQUESTS)
    return [(f"request_{index + 1}", request) for index, request in enumerate(requests)]


def build_arg_parser() -> argparse.ArgumentParser:
    repo_root = repo_root_from_script()
    analysis_root = repo_root / "Docs" / "Analysis"
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--request", action="append", default=[], help="Blueprint authoring request to classify. Repeatable.")
    parser.add_argument("--target-class", default="", help="Optional target parent class or Blueprint class hint.")
    parser.add_argument("--output-dir", default=str(analysis_root / "BPAuthoringPlanner"))
    parser.add_argument("--quality-gate-report", default=str(analysis_root / "BPAuthoringQualityGate" / "bp_authoring_quality_gate_report.json"))
    parser.add_argument("--combined-report", default=str(analysis_root / "Lyra" / "lyra_combined_readiness_report.json"))
    parser.add_argument("--delegate-report", default=str(analysis_root / "Lyra" / "lyra_delegate_latent_async_readiness_report.json"))
    parser.add_argument("--no-write", action="store_true")
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    output_dir = Path(args.output_dir).resolve()
    report = build_report(
        request_pairs_from_args(args.request),
        output_dir,
        load_json_if_exists(Path(args.quality_gate_report)),
        load_json_if_exists(Path(args.combined_report)),
        load_json_if_exists(Path(args.delegate_report)),
        target_class=args.target_class,
    )
    if not args.no_write:
        json_path, md_path = write_report(report, output_dir)
        print(f"Wrote {json_path}")
        print(f"Wrote {md_path}")
    print(f"Requests planned: {report['summary']['request_count']}")
    print(f"Status counts: {report['summary']['status_counts']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
