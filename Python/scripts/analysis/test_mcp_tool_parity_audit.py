#!/usr/bin/env python
"""Smoke tests for mcp_tool_parity_audit.py."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import mcp_tool_parity_audit as audit  # noqa: E402


def write_fixture(root: Path, python_files: dict[str, str], cpp_source: str) -> None:
    tools_dir = root / "Python" / "tools"
    bridge_dir = root / "MCPGameProject" / "Plugins" / "UnrealMCP" / "Source" / "UnrealMCP" / "Private"
    tools_dir.mkdir(parents=True)
    bridge_dir.mkdir(parents=True)

    for name, source in python_files.items():
        (tools_dir / name).write_text(source.strip() + "\n", encoding="utf-8")

    (bridge_dir / "UnrealMCPBridge.cpp").write_text(cpp_source.strip() + "\n", encoding="utf-8")


def cpp_dispatch(*routes: str) -> str:
    checks = []
    for index, route in enumerate(routes):
        prefix = "if" if index == 0 else "else if"
        checks.append(f'{prefix} (CommandType == TEXT("{route}")) {{}}')
    return (
        "void Handle()\n"
        "{\n"
        '    if (CommandType == TEXT("ping")) {}\n'
        f"    {' '.join(checks)}\n"
        "    else\n"
        "    {\n"
        '        ResponseJson->SetStringField(TEXT("error"), FString::Printf(TEXT("Unknown command: %s"), *CommandType));\n'
        "    }\n"
        "}\n"
    )


class McpToolParityAuditTests(unittest.TestCase):
    def test_matching_python_tool_and_cpp_route_pass(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mcp_parity_") as temp_dir:
            root = Path(temp_dir)
            write_fixture(
                root,
                {
                    "alpha_tools.py": """
def register_alpha_tools(mcp):
    @mcp.tool()
    def alpha(ctx):
        return {}
""",
                },
                cpp_dispatch("alpha"),
            )

            report = audit.build_report(root)

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["missing_in_cpp"], [])
            self.assertEqual(report["missing_in_python"], [])

    def test_python_route_alias_matches_cpp_route(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mcp_parity_") as temp_dir:
            root = Path(temp_dir)
            write_fixture(
                root,
                {
                    "python_tools.py": """
def register_python_tools(mcp):
    @mcp.tool()
    def execute_unreal_python(ctx, code):
        return {}
""",
                },
                cpp_dispatch("execute_python"),
            )

            report = audit.build_report(root)

            self.assertEqual(report["status"], "pass")
            self.assertEqual(report["missing_in_cpp"], [])
            self.assertEqual(report["missing_in_python"], [])

    def test_reports_missing_python_and_cpp_sides(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mcp_parity_") as temp_dir:
            root = Path(temp_dir)
            write_fixture(
                root,
                {
                    "one_tools.py": """
def register_one_tools(mcp):
    @mcp.tool()
    def python_only_candidate(ctx):
        return {}
""",
                },
                cpp_dispatch("cpp_only_candidate"),
            )

            report = audit.build_report(root)

            self.assertEqual(report["status"], "fail")
            self.assertEqual([item["name"] for item in report["missing_in_cpp"]], ["python_only_candidate"])
            self.assertEqual([item["name"] for item in report["missing_in_python"]], ["cpp_only_candidate"])

    def test_reports_duplicate_python_tools_and_cpp_routes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="mcp_parity_") as temp_dir:
            root = Path(temp_dir)
            write_fixture(
                root,
                {
                    "first_tools.py": """
def register_first_tools(mcp):
    @mcp.tool()
    def duplicate_py(ctx):
        return {}
""",
                    "second_tools.py": """
def register_second_tools(mcp):
    @mcp.tool()
    def duplicate_py(ctx):
        return {}
""",
                },
                cpp_dispatch("duplicate_py", "duplicate_cpp", "duplicate_cpp"),
            )

            report = audit.build_report(root)

            self.assertEqual(report["status"], "fail")
            self.assertEqual(report["duplicate_python_tools"][0]["name"], "duplicate_py")
            self.assertEqual(report["duplicate_cpp_routes"][0]["name"], "duplicate_cpp")


if __name__ == "__main__":
    unittest.main()
