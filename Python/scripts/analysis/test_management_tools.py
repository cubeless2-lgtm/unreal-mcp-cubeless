#!/usr/bin/env python
"""Smoke tests for management_tools.py."""

from __future__ import annotations

import sys
import unittest
import os
from pathlib import Path
from typing import Any, Callable, Dict, Optional


SCRIPT_DIR = Path(__file__).resolve().parent
PYTHON_ROOT = SCRIPT_DIR.parents[1]
sys.path.insert(0, str(PYTHON_ROOT))

from tools.management_tools import MCPToolRegistry, register_management_tools, request_telemetry, runtime_guard, set_health_provider  # noqa: E402


class FakeMCP:
    def __init__(self) -> None:
        self.registered: Dict[str, Callable[..., Any]] = {}

    def tool(self, name: Optional[str] = None, description: Optional[str] = None):
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.registered[name or func.__name__] = func
            return func

        return decorator


class ManagementToolsTests(unittest.TestCase):
    def tearDown(self) -> None:
        request_telemetry.reset_for_tests()
        runtime_guard.reset_for_tests()
        set_health_provider(lambda ping_unreal=False: {"success": True})
        for name in ("UNREAL_MCP_GUARD_MODE", "UNREAL_MCP_RATE_LIMIT_PER_MINUTE"):
            os.environ.pop(name, None)

    def test_default_enabled_tool_runs_unchanged(self) -> None:
        registry = MCPToolRegistry()
        mcp = FakeMCP()

        with registry.capture_tools(mcp, "alpha"):

            @mcp.tool()
            def sample(ctx: Any, value: int = 1) -> Dict[str, Any]:
                return {"success": True, "value": value}

        self.assertEqual(mcp.registered["sample"](None, 7), {"success": True, "value": 7})
        self.assertTrue(registry.is_tool_enabled("sample"))
        self.assertEqual(registry.report(include_tools=False)["enabled_tools"], 1)

    def test_disable_tool_blocks_only_that_tool(self) -> None:
        registry = MCPToolRegistry()
        mcp = FakeMCP()

        with registry.capture_tools(mcp, "alpha"):

            @mcp.tool()
            def first(ctx: Any) -> Dict[str, Any]:
                return {"success": True}

            @mcp.tool()
            def second(ctx: Any) -> Dict[str, Any]:
                return {"success": True}

        self.assertTrue(registry.set_tool_enabled("first", False)["success"])
        blocked = mcp.registered["first"](None)
        self.assertEqual(blocked["status"], "disabled")
        self.assertEqual(blocked["tool"], "first")
        self.assertEqual(mcp.registered["second"](None), {"success": True})

    def test_disable_category_blocks_category(self) -> None:
        registry = MCPToolRegistry()
        mcp = FakeMCP()

        with registry.capture_tools(mcp, "alpha"):

            @mcp.tool()
            def first(ctx: Any) -> Dict[str, Any]:
                return {"success": True}

        with registry.capture_tools(mcp, "beta"):

            @mcp.tool()
            def second(ctx: Any) -> Dict[str, Any]:
                return {"success": True}

        self.assertTrue(registry.set_category_enabled("alpha", False)["success"])
        self.assertEqual(mcp.registered["first"](None)["status"], "disabled")
        self.assertEqual(mcp.registered["second"](None), {"success": True})

    def test_manage_tools_is_protected(self) -> None:
        registry = MCPToolRegistry()
        mcp = FakeMCP()

        register_management_tools(mcp, registry)

        result = mcp.registered["manage_tools"](
            None,
            action="disable_tool",
            tool_name="manage_tools",
            include_tools=False,
        )
        self.assertFalse(result["success"])
        self.assertIn("Protected tool", result["error"])
        self.assertEqual(mcp.registered["manage_tools"](None, include_tools=False)["success"], True)

    def test_manage_tools_wrapper_accepts_category_argument(self) -> None:
        registry = MCPToolRegistry()
        mcp = FakeMCP()

        register_management_tools(mcp, registry)

        result = mcp.registered["manage_tools"](
            None,
            action="set_category",
            category="management",
            enabled=True,
            include_tools=False,
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["category"], "management")

    def test_set_actions_require_enabled_value(self) -> None:
        registry = MCPToolRegistry()
        mcp = FakeMCP()

        with registry.capture_tools(mcp, "alpha"):

            @mcp.tool()
            def sample(ctx: Any) -> Dict[str, Any]:
                return {"success": True}

        tool_result = registry.manage(action="set_tool", tool_name="sample", include_tools=False)
        category_result = registry.manage(action="set_category", category="alpha", include_tools=False)

        self.assertFalse(tool_result["success"])
        self.assertEqual(tool_result["error"], "enabled is required for set_tool")
        self.assertFalse(category_result["success"])
        self.assertEqual(category_result["error"], "enabled is required for set_category")
        self.assertTrue(registry.is_tool_enabled("sample"))

    def test_rate_limit_blocks_only_when_configured(self) -> None:
        os.environ["UNREAL_MCP_GUARD_MODE"] = "hard"
        os.environ["UNREAL_MCP_RATE_LIMIT_PER_MINUTE"] = "1"
        runtime_guard.reset_for_tests()
        request_telemetry.reset_for_tests()

        registry = MCPToolRegistry()
        mcp = FakeMCP()

        with registry.capture_tools(mcp, "alpha"):

            @mcp.tool()
            def sample(ctx: Any) -> Dict[str, Any]:
                return {"success": True}

        self.assertEqual(mcp.registered["sample"](None), {"success": True})
        blocked = mcp.registered["sample"](None)

        self.assertFalse(blocked["success"])
        self.assertEqual(blocked["status"], "rate_limited")
        self.assertEqual(blocked["tool"], "sample")
        telemetry = request_telemetry.report(include_recent=False)
        self.assertEqual(telemetry["status_counts"].get("rate_limited"), 1)

    def test_health_provider_failure_is_reported(self) -> None:
        registry = MCPToolRegistry()

        def failing_provider(ping_unreal: bool = False) -> Dict[str, Any]:
            raise RuntimeError("boom")

        set_health_provider(failing_provider)
        result = registry.health_report(include_tools=False, include_recent=False)

        self.assertFalse(result["success"])
        self.assertEqual(result["unreal_bridge"]["status"], "error")
        self.assertEqual(result["unreal_bridge"]["message"], "boom")

    def test_heartbeat_forces_ping_and_reports_failure(self) -> None:
        registry = MCPToolRegistry()
        calls = []

        def disconnected_provider(ping_unreal: bool = False) -> Dict[str, Any]:
            calls.append(ping_unreal)
            return {
                "success": not ping_unreal,
                "unreal_bridge": {
                    "status": "not connected" if ping_unreal else "not_checked",
                    "connected": False,
                },
            }

        set_health_provider(disconnected_provider)
        result = registry.manage(action="heartbeat", include_tools=False, include_recent=False)

        self.assertEqual(calls, [True])
        self.assertFalse(result["success"])
        self.assertEqual(result["unreal_bridge"]["status"], "not connected")


if __name__ == "__main__":
    unittest.main()
