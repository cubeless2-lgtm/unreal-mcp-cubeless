# MCP Runtime Tool Management

`manage_tools` is a conservative runtime policy tool for the Python FastMCP
server. It does not change the Unreal TCP bridge, `.mcp.json`, native command
handlers, or the default stdio transport.

## Safety Model

- All existing tools are enabled by default.
- Runtime enable/disable changes are memory-only.
- Restarting the MCP server clears all disabled tools and categories.
- `manage_tools` is protected and cannot disable itself.
- Disabled tools remain registered with FastMCP, but their wrapper returns a
  structured disabled response before calling the original tool body.
- No C++ command handler is removed or changed by this layer.

## Categories

The server records tools under these categories during registration:

- `editor`
- `blueprint`
- `blueprint_node`
- `project`
- `umg`
- `python`
- `pcg`
- `material`
- `niagara`
- `texture_generation`
- `ieta`
- `management`

## Usage

Read-only status:

```json
{
  "action": "status",
  "include_tools": false
}
```

Disable one tool until server restart or reset:

```json
{
  "action": "disable_tool",
  "tool_name": "resolve_pcg_graph"
}
```

Disable one category until server restart or reset:

```json
{
  "action": "disable_category",
  "category": "pcg"
}
```

Reset all runtime policy overrides:

```json
{
  "action": "reset"
}
```

Supported actions are `status`, `list`, `enable_tool`, `disable_tool`,
`set_tool`, `enable_category`, `disable_category`, `set_category`, and `reset`.
`set_tool` and `set_category` require an explicit boolean `enabled` value.
Use `health` or `heartbeat` for registry, telemetry, guard, and optional Unreal
bridge ping status.

This is the second MCP upgrade gate after the parity audit. It gives future
transport hardening and HTTP/SSE experiments a stable registry surface without
changing handler behavior by default.
