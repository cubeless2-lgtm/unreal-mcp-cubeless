# unreal-mcp-cubeless Codex Adapter

## Shared Ops Bootstrap

- Every new Codex session in this repository must first resolve and apply the shared Cubeless agent rules.
- Resolve `../CubelessOps/AGENTS.md` relative to this repository parent first.
- If that sibling is missing, try `CUBELESS_OPS_ROOT\AGENTS.md`.
- If neither path resolves, report that `CubelessOps` is missing, continue only with the critical local rules in this file, and do not pretend the shared rules were loaded.
- After loading shared Ops, read `../CubelessOps/projects/unreal-mcp-cubeless.md` for this repository's binding.
- For MCP implementation, upstream sync, and release checks, use the MCP role files referenced by that binding.
- For local Cubeless work on any PC, prefer the maximum local-work Codex permission profile documented in `../CubelessOps/docs/policies/local-permission-profile.md`.
- Keep Git status, diffs, staging, commits, pushes, and summaries separate for `unreal-mcp-cubeless`, `../CubelessOps`, consuming projects, and Unreal plugin submodules.

## Branch Context

This checkout is intended to keep a local TA-focused extension of `chongdashu/unreal-mcp`.

- Upstream repository: `https://github.com/chongdashu/unreal-mcp`
- Cubeless integration/default branch: `main`
- Legacy local extension branch: `local/pcg-tools`
- Primary target engine for the user: Unreal Engine 5.7.4. Resolve the engine checkout from `UE_ENGINE_ROOT` or `UE_SOURCE_ROOT` when set, otherwise from a local workspace sibling such as `../UnrealEngine`.
- User workflow: Unreal TA work with heavy PCG, Blueprint, and Python automation.

## Important Local Changes

The local extension adds a small generic Unreal Python bridge plus PCG-oriented MCP tools.

Always read these files before editing the extension:

- `Docs/LOCAL_PCG_EXTENSION.md`
- `Docs/Tools/pcg_tools.md`
- `Docs/Tools/ai_texture_tools.md`
- `Python/tools/python_tools.py`
- `Python/tools/pcg_tools.py`
- `Python/tools/texture_generation.py`
- `Python/services/openai_image_service.py`
- `Python/services/unreal_texture_importer.py`
- `MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/Private/Commands/UnrealMCPProjectCommands.cpp`
- `MCPGameProject/Plugins/UnrealMCP/Source/UnrealMCP/Private/UnrealMCPBridge.cpp`

## Maintenance Rule

Do not rewrite upstream files broadly. Keep the local patch small and easy to rebase.

If the user says any of the following, treat it as a request to update from upstream while preserving the local PCG/Python extension:

- "최신 업데이트 받아줘"
- "업데이트 풀 받아줘"
- "원본에서 pull 받아줘"
- "upstream 최신 받아줘"
- "chongdashu 최신으로 업데이트해줘"
- Similar Korean/English wording about getting the latest original/upstream changes.

For those requests, use the shared workflow in `../CubelessOps/docs/workflows/mcp-upstream-update.md`. By default, update `main` by merging `upstream/main`, preserve the local Cubeless extension, run verification, and push only when the user explicitly asks for push intent.

Preferred update flow:

```powershell
cd <this unreal-mcp-cubeless repository root>
.\scripts\update_with_pcg_extension.ps1
```

If conflicts happen after an upstream update, preserve the generic `execute_python` bridge, the Python-only PCG tool layer, and the AI texture tool layer.

## Verification

For Python changes, run:

```powershell
uv --directory .\Python run python -m py_compile unreal_mcp_server.py tools\python_tools.py tools\pcg_tools.py
uv --directory .\Python run python -c "import unreal_mcp_server; print('server import ok')"
```

For AI texture tool changes, include:

```powershell
uv --directory .\Python run python -m py_compile unreal_mcp_server.py tools\texture_generation.py services\openai_image_service.py services\unreal_texture_importer.py
```

C++ plugin verification should use the user's source engine resolved from `UE_ENGINE_ROOT`, `UE_SOURCE_ROOT`, or the local workspace sibling `../UnrealEngine`. Avoid kicking off a full source-engine rebuild unless necessary; it can be very slow.
