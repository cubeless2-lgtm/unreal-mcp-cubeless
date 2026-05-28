# Repository Instructions for Codex

Read this file before making changes in this repository.

## Branch Context

This checkout is intended to keep a local TA-focused extension of `chongdashu/unreal-mcp`.

- Upstream repository: `https://github.com/chongdashu/unreal-mcp`
- Local extension branch: `local/pcg-tools`
- Primary target engine for the user: `D:\Git\UnrealEngine`, Unreal Engine 5.7.4
- User workflow: Unreal TA work with heavy PCG, Blueprint, and Python automation.

## Important Local Changes

The local extension adds a small generic Unreal Python bridge plus PCG-oriented MCP tools.

Always read these files before editing the extension:

- `Docs/LOCAL_PCG_EXTENSION.md`
- `Docs/Tools/pcg_tools.md`
- `Python/tools/python_tools.py`
- `Python/tools/pcg_tools.py`
- `MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/Private/Commands/UnrealMCPProjectCommands.cpp`
- `MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/Private/UnrealMCPBridge.cpp`

## Maintenance Rule

Do not rewrite upstream files broadly. Keep the local patch small and easy to rebase.

Preferred update flow:

```powershell
cd D:\Git\unreal-mcp
.\scripts\update_with_pcg_extension.ps1
```

If conflicts happen after an upstream update, preserve the generic `execute_python` bridge and the Python-only PCG tool layer.

## Verification

For Python changes, run:

```powershell
uv --directory D:\Git\unreal-mcp\Python run python -m py_compile unreal_mcp_server.py tools\python_tools.py tools\pcg_tools.py
uv --directory D:\Git\unreal-mcp\Python run python -c "import unreal_mcp_server; print('server import ok')"
```

C++ plugin verification should use the user's source engine at `D:\Git\UnrealEngine`. Avoid kicking off a full source-engine rebuild unless necessary; it can be very slow.
