# MCP Tool Parity Audit

`Python/scripts/analysis/mcp_tool_parity_audit.py` is the first conservative
gate for the MCP upgrade work. It compares FastMCP tools exposed from
`Python/tools/*.py` with native C++ routes dispatched by
`MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/Private/UnrealMCPBridge.cpp`.

The audit is read-only. It does not launch the MCP server, connect to Unreal
Editor, or change `.mcp.json`, the FastMCP stdio entry point, the existing TCP
bridge, or port `55557`.

## Why This Comes First

The planned upgrade path keeps the current server stable while adding checks
around it:

1. Audit TypeScript/Python-facing tool exposure against C++ handler routes.
2. Add a tool registry facade that can later support category-level
   enable/disable without moving handlers.
3. Add transport hardening around the current path: capability token,
   loopback-only default, rate limit, heartbeat, and request queue telemetry.
4. Add an opt-in native Streamable HTTP/SSE endpoint only after the registry
   and telemetry gates can compare old and new behavior.

This script owns step 1. A mismatch should be treated as a planning signal
before changing transport or dynamic tool-management behavior.

## Usage

Run from the repository root with the project Python environment:

```powershell
uv --directory Python run python scripts\analysis\mcp_tool_parity_audit.py
```

For automation or CI-style collection:

```powershell
uv --directory Python run python scripts\analysis\mcp_tool_parity_audit.py --json
uv --directory Python run python scripts\analysis\mcp_tool_parity_audit.py --output Saved\MCP\mcp_tool_parity_audit.json
```

By default, the command exits with status `1` when it finds parity issues,
duplicate Python tools, duplicate C++ routes, or discovery errors. Use
`--fail-on never` for exploratory reporting.

## Report Fields

- `missing_in_cpp`: FastMCP tools that are not mapped to a native C++ route.
- `missing_in_python`: native C++ routes that are not exposed as FastMCP tools.
- `duplicate_python_tools`: duplicate FastMCP tool names.
- `duplicate_cpp_routes`: duplicate native dispatch route names.
- `python_only_tools`: documented host-side tools that intentionally do not
  have a one-to-one C++ route, such as `manage_tools` and texture helpers.
- `cpp_only_routes`: documented native routes that intentionally are not
  exposed as FastMCP tools.
- `route_aliases`: documented Python tool names that intentionally dispatch to
  differently named native routes.

New intentional exceptions should be added to the script with a reason. That
keeps `manage_tools`, transport hardening, and future HTTP/SSE promotion from
inheriting undocumented routing drift.
