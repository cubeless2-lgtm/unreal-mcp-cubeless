# Local PCG Extension Notes

This document records the local changes made for the user's Unreal TA workflow.

## Goal

Keep `chongdashu/unreal-mcp` updateable from upstream while adding project-useful PCG and Unreal Python automation.

The extension deliberately avoids adding a separate C++ command for every TA operation. Instead:

- C++ adds one generic `execute_python` command.
- Python MCP tools call that command.
- PCG-specific behavior lives in Python and can evolve quickly.

## Current Branch

- Branch: `local/pcg-tools`
- Base upstream at time of extension: `4e5f00d`
- Initial extension commit: `ecab023`

## Files Added

- `AGENTS.md`
  - Instructions for Codex/AI agents. Read first.
- `Python/tools/python_tools.py`
  - Registers `execute_unreal_python`.
- `Python/tools/pcg_tools.py`
  - Registers PCG-focused automation tools.
- `Docs/Tools/pcg_tools.md`
  - User-facing tool summary.
- `scripts/update_with_pcg_extension.ps1`
  - Helper script for updating from upstream and keeping the local branch.

## Files Modified

- `Python/unreal_mcp_server.py`
  - Imports and registers `python_tools` and `pcg_tools`.
- `MCPGameProject/Plugins/UnrealMCP/UnrealMCP.uplugin`
  - Enables `PythonScriptPlugin`.
- `MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/UnrealMCP.Build.cs`
  - Adds `PythonScriptPlugin` dependency.
- `MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/Public/Commands/UnrealMCPProjectCommands.h`
  - Declares `HandleExecutePython`.
- `MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/Private/Commands/UnrealMCPProjectCommands.cpp`
  - Implements `execute_python` using `IPythonScriptPlugin::ExecPythonCommandEx`.
- `MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/Private/UnrealMCPBridge.cpp`
  - Routes `execute_python` to project commands.
- `MCPGameProject/Source/MCPGameProject.Target.cs`
  - Set to UE 5.7 build settings/include order.
- `MCPGameProject/Source/MCPGameProjectEditor.Target.cs`
  - Set to UE 5.7 build settings/include order.
- `mcp.json`
  - Points to `D:/Git/unreal-mcp/Python`.

## Added MCP Tools

- `execute_unreal_python(code, mode="ExecuteStatement")`
- `list_pcg_assets(root_path="/Game")`
- `list_pcg_components()`
- `refresh_pcg_components(actor_name="", selected_only=false)`
- `set_pcg_debug_enabled(enabled=false, actor_name="", selected_only=false)`
- `resave_pcg_assets(root_path="/Game")`

## Design Notes

`pcg_tools.py` writes Unreal Python results to a JSON file in the temp directory because Unreal's Python command result capture is limited for multi-line scripts. The MCP tool reads that JSON file and returns structured data.

The PCG component operations are best-effort. Unreal PCG Python API details vary by engine version and project plugins, so the tools check class/property/method names dynamically instead of depending on a narrow API surface.

## Update Guidance

When the user asks for "최신 업데이트", "업데이트 풀", "원본 pull", "upstream 최신", or similar wording, the expected behavior is:

- Keep the PCG/Python extension.
- Pull/fetch from `upstream`.
- Fast-forward local `main` to `upstream/main`.
- Rebase `local/pcg-tools` onto `main`.
- Resolve conflicts in favor of preserving:
  - generic `execute_python` C++ bridge
  - `Python/tools/python_tools.py`
  - `Python/tools/pcg_tools.py`
  - tool registration in `Python/unreal_mcp_server.py`
  - docs and update script
- Run Python verification.
- Push `local/pcg-tools` to `origin`; use `--force-with-lease` after a successful rebase.

Use this shape when updating:

```powershell
cd D:\Git\unreal-mcp
git fetch upstream
git checkout main
git merge --ff-only upstream/main
git checkout local/pcg-tools
git rebase main
uv --directory D:\Git\unreal-mcp\Python run python -m py_compile unreal_mcp_server.py tools\python_tools.py tools\pcg_tools.py
uv --directory D:\Git\unreal-mcp\Python run python -c "import unreal_mcp_server; print('server import ok')"
git push origin local/pcg-tools --force-with-lease
```

If the remote names are not set yet, the recommended layout is:

- `upstream`: `https://github.com/chongdashu/unreal-mcp`
- `origin`: user's own GitHub repository

## Verification Already Done

- Confirmed `D:\Git\UnrealEngine` is UE 5.7.4.
- Confirmed UE 5.7 has `IPythonScriptPlugin`, `FPythonCommandEx`, and `ExecPythonCommandEx`.
- Ran Python dependency sync:

```powershell
uv --directory D:\Git\unreal-mcp\Python sync
```

- Ran Python syntax/import checks:

```powershell
uv --directory D:\Git\unreal-mcp\Python run python -m py_compile unreal_mcp_server.py tools\python_tools.py tools\pcg_tools.py
uv --directory D:\Git\unreal-mcp\Python run python -c "import unreal_mcp_server; print('server import ok')"
```

## Build Caveat

A full C++ build against `D:\Git\UnrealEngine` started rebuilding thousands of source-engine actions and was stopped because it was too expensive for a quick verification pass. Avoid triggering a full source-engine rebuild unless the user explicitly wants that.
