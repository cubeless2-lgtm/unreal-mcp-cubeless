"""
Python execution tools for Unreal MCP.

These tools intentionally keep the Unreal bridge generic. TA-specific workflows
can be implemented as Python scripts without adding a new C++ command each time.
"""

import logging
from typing import Any, Dict

from mcp.server.fastmcp import Context, FastMCP

logger = logging.getLogger("UnrealMCP")


def register_python_tools(mcp: FastMCP):
    """Register generic Unreal Python execution tools."""

    @mcp.tool()
    def execute_unreal_python(
        ctx: Context,
        code: str,
        mode: str = "ExecuteStatement",
    ) -> Dict[str, Any]:
        """
        Execute Python inside the running Unreal Editor.

        Args:
            code: Python code to execute in Unreal.
            mode: Python execution mode. Usually ExecuteStatement.

        Returns:
            Response from Unreal, including Python logs and command_result.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("execute_python", {"code": code, "mode": mode})
            return response or {"success": False, "message": "No response from Unreal Engine"}
        except Exception as exc:
            logger.exception("Error executing Unreal Python")
            return {"success": False, "message": str(exc)}

    logger.info("Python tools registered successfully")
