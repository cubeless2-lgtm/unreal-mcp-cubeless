#!/usr/bin/env python
"""
Read-only parity audit for FastMCP tool exposure and UnrealMCP C++ routes.

This script is intentionally filesystem-only. It does not start the MCP server,
does not connect to Unreal Editor, and does not mutate project files.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


PYTHON_TOOLS_DIR = Path("Python") / "tools"
CPP_BRIDGE_PATH = (
    Path("MCPGameProject")
    / "Plugins"
    / "UnrealMCP"
    / "Source"
    / "UnrealMCP"
    / "Private"
    / "UnrealMCPBridge.cpp"
)


PYTHON_ROUTE_ALIASES: Mapping[str, Tuple[str, ...]] = {
    "execute_unreal_python": ("execute_python",),
    "show_ieta_connection_status": ("ieta_status",),
}


PYTHON_ONLY_TOOLS: Mapping[str, str] = {
    "manage_tools": "Host-side runtime FastMCP tool policy manager.",
    "get_static_mesh_uv_layout": "Host-side UV extraction helper, not a direct C++ bridge route.",
    "generate_texture_from_prompt": "Host-side texture generation workflow.",
    "generate_texture_for_mesh_uv": "Host-side texture generation workflow.",
    "import_texture_to_unreal": "Host-side import workflow that dispatches lower-level Unreal Python.",
    "create_material_instance_with_texture": "Host-side material workflow that dispatches lower-level Unreal Python.",
    "apply_material_to_mesh": "Host-side material workflow that dispatches lower-level Unreal Python.",
    "generate_and_apply_ai_texture": "Composite host-side texture workflow.",
    "list_pcg_assets": "Unreal Python inventory helper.",
    "list_pcg_components": "Unreal Python inventory helper.",
    "set_pcg_debug_enabled": "Unreal Python debug flag helper.",
    "resave_pcg_assets": "Unreal Python maintenance helper.",
}


CPP_ONLY_ROUTES: Mapping[str, str] = {
    "ping": "Native bridge liveness probe.",
    "create_actor": "Legacy native alias for spawn_actor.",
    "focus_viewport": "Native route retained while the FastMCP tool is disabled.",
    "run_content_validation_pipeline_mcp": "Internal project command not currently exposed as a FastMCP tool.",
    "analyze_blueprint_widget_fallbacks_mcp": "Internal project command not currently exposed as a FastMCP tool.",
}


CPP_ROUTE_RE = re.compile(r'CommandType\s*==\s*TEXT\("([^"]+)"\)')


@dataclass(frozen=True)
class LocatedName:
    name: str
    file: str
    line: int


def repo_root_from_script() -> Path:
    return Path(__file__).resolve().parents[3]


def _relative_path(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _decorator_tool_name(function_name: str, decorator: ast.expr) -> Optional[str]:
    if isinstance(decorator, ast.Call):
        func = decorator.func
        args = decorator.args
        keywords = decorator.keywords
    else:
        func = decorator
        args = []
        keywords = []

    if not isinstance(func, ast.Attribute) or func.attr != "tool":
        return None
    if not isinstance(func.value, ast.Name) or func.value.id != "mcp":
        return None

    for keyword in keywords:
        if keyword.arg == "name" and isinstance(keyword.value, ast.Constant) and isinstance(keyword.value.value, str):
            return keyword.value.value

    if args and isinstance(args[0], ast.Constant) and isinstance(args[0].value, str):
        return args[0].value

    return function_name


def discover_python_tools(tools_dir: Path, repo_root: Path) -> Tuple[List[LocatedName], List[str]]:
    tools: List[LocatedName] = []
    errors: List[str] = []

    if not tools_dir.exists():
        return tools, [f"Python tools directory not found: {_relative_path(tools_dir, repo_root)}"]

    for path in sorted(tools_dir.glob("*.py")):
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(path))
        except (OSError, SyntaxError) as exc:
            errors.append(f"{_relative_path(path, repo_root)}: {exc}")
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            for decorator in node.decorator_list:
                tool_name = _decorator_tool_name(node.name, decorator)
                if tool_name:
                    tools.append(
                        LocatedName(
                            name=tool_name,
                            file=_relative_path(path, repo_root),
                            line=node.lineno,
                        )
                    )
                    break

    return tools, errors


def _dispatch_region(source: str) -> Tuple[str, int]:
    start = source.find('if (CommandType == TEXT("ping"))')
    if start < 0:
        return source, 0

    unknown = source.find("Unknown command:", start)
    if unknown < 0:
        return source[start:], source[:start].count("\n")

    return source[start:unknown], source[:start].count("\n")


def discover_cpp_routes(bridge_path: Path, repo_root: Path) -> Tuple[List[LocatedName], List[str]]:
    if not bridge_path.exists():
        return [], [f"C++ bridge file not found: {_relative_path(bridge_path, repo_root)}"]

    try:
        source = bridge_path.read_text(encoding="utf-8")
    except OSError as exc:
        return [], [f"{_relative_path(bridge_path, repo_root)}: {exc}"]

    region, line_offset = _dispatch_region(source)
    routes: List[LocatedName] = []
    for match in CPP_ROUTE_RE.finditer(region):
        line = line_offset + region[: match.start()].count("\n") + 1
        routes.append(
            LocatedName(
                name=match.group(1),
                file=_relative_path(bridge_path, repo_root),
                line=line,
            )
        )

    return routes, []


def _duplicates(items: Sequence[LocatedName]) -> List[Dict[str, Any]]:
    by_name: Dict[str, List[LocatedName]] = {}
    for item in items:
        by_name.setdefault(item.name, []).append(item)

    duplicates: List[Dict[str, Any]] = []
    for name in sorted(by_name):
        entries = by_name[name]
        if len(entries) > 1:
            duplicates.append(
                {
                    "name": name,
                    "entries": [asdict(entry) for entry in entries],
                }
            )
    return duplicates


def _known_items(items: Sequence[LocatedName], reasons: Mapping[str, str]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for item in sorted(items, key=lambda value: (value.name, value.file, value.line)):
        reason = reasons.get(item.name)
        if reason:
            entry = asdict(item)
            entry["reason"] = reason
            result.append(entry)
    return result


def _route_to_python_aliases() -> Dict[str, List[str]]:
    route_to_aliases: Dict[str, List[str]] = {}
    for python_tool, routes in PYTHON_ROUTE_ALIASES.items():
        for route in routes:
            route_to_aliases.setdefault(route, []).append(python_tool)
    return route_to_aliases


def build_report(repo_root: Path) -> Dict[str, Any]:
    repo_root = repo_root.resolve()
    python_tools, python_errors = discover_python_tools(repo_root / PYTHON_TOOLS_DIR, repo_root)
    cpp_routes, cpp_errors = discover_cpp_routes(repo_root / CPP_BRIDGE_PATH, repo_root)

    python_names = {tool.name for tool in python_tools}
    cpp_names = {route.name for route in cpp_routes}
    route_to_aliases = _route_to_python_aliases()

    missing_in_cpp: List[Dict[str, Any]] = []
    for tool in sorted(python_tools, key=lambda value: (value.name, value.file, value.line)):
        if tool.name in PYTHON_ONLY_TOOLS:
            continue
        expected_routes = PYTHON_ROUTE_ALIASES.get(tool.name, (tool.name,))
        if not any(route in cpp_names for route in expected_routes):
            entry = asdict(tool)
            entry["expected_cpp_routes"] = list(expected_routes)
            missing_in_cpp.append(entry)

    missing_in_python: List[Dict[str, Any]] = []
    for route in sorted(cpp_routes, key=lambda value: (value.name, value.file, value.line)):
        if route.name in CPP_ONLY_ROUTES:
            continue
        if route.name in python_names:
            continue
        if any(alias in python_names for alias in route_to_aliases.get(route.name, [])):
            continue
        missing_in_python.append(asdict(route))

    duplicate_python_tools = _duplicates(python_tools)
    duplicate_cpp_routes = _duplicates(cpp_routes)
    errors = python_errors + cpp_errors
    fail_reasons = {
        "missing_in_cpp": len(missing_in_cpp),
        "missing_in_python": len(missing_in_python),
        "duplicate_python_tools": len(duplicate_python_tools),
        "duplicate_cpp_routes": len(duplicate_cpp_routes),
        "errors": len(errors),
    }
    status = "fail" if any(fail_reasons.values()) else "pass"

    return {
        "status": status,
        "repo_root": repo_root.as_posix(),
        "python_tools_dir": PYTHON_TOOLS_DIR.as_posix(),
        "cpp_bridge_path": CPP_BRIDGE_PATH.as_posix(),
        "counts": {
            "python_tools": len(python_tools),
            "cpp_routes": len(cpp_routes),
            "unique_python_tools": len(python_names),
            "unique_cpp_routes": len(cpp_names),
        },
        "fail_reasons": fail_reasons,
        "missing_in_cpp": missing_in_cpp,
        "missing_in_python": missing_in_python,
        "duplicate_python_tools": duplicate_python_tools,
        "duplicate_cpp_routes": duplicate_cpp_routes,
        "python_only_tools": _known_items(python_tools, PYTHON_ONLY_TOOLS),
        "cpp_only_routes": _known_items(cpp_routes, CPP_ONLY_ROUTES),
        "route_aliases": {name: list(routes) for name, routes in sorted(PYTHON_ROUTE_ALIASES.items())},
        "errors": errors,
    }


def print_text_report(report: Mapping[str, Any]) -> None:
    counts = report["counts"]
    print(f"MCP tool parity audit: {report['status']}")
    print(
        "Counts: "
        f"python_tools={counts['python_tools']} "
        f"cpp_routes={counts['cpp_routes']} "
        f"unique_python_tools={counts['unique_python_tools']} "
        f"unique_cpp_routes={counts['unique_cpp_routes']}"
    )

    for key in ("missing_in_cpp", "missing_in_python", "duplicate_python_tools", "duplicate_cpp_routes"):
        items = report[key]
        print(f"{key}: {len(items)}")
        for item in items[:20]:
            if "entries" in item:
                locations = ", ".join(f"{entry['file']}:{entry['line']}" for entry in item["entries"])
                print(f"  - {item['name']} ({locations})")
            else:
                name = item.get("name", item.get("route", "<unknown>"))
                expected = item.get("expected_cpp_routes")
                suffix = f" expected={expected}" if expected else ""
                print(f"  - {name} ({item['file']}:{item['line']}){suffix}")
        if len(items) > 20:
            print(f"  ... {len(items) - 20} more")

    if report["errors"]:
        print("errors:")
        for error in report["errors"]:
            print(f"  - {error}")


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=repo_root_from_script(),
        help="Path to the unreal-mcp-cubeless repository root.",
    )
    parser.add_argument("--json", action="store_true", help="Print the full JSON report.")
    parser.add_argument("--output", type=Path, help="Optional JSON output path.")
    parser.add_argument(
        "--fail-on",
        choices=("issues", "never"),
        default="issues",
        help="Exit with status 1 when parity issues are found unless set to never.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    report = build_report(args.repo_root)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print_text_report(report)

    if args.fail_on == "never":
        return 0
    return 1 if report["status"] == "fail" else 0


if __name__ == "__main__":
    raise SystemExit(main())
