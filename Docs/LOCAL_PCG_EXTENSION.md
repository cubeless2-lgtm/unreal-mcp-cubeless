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
  - Registers PCG-focused automation tools. Fast PCG refresh and spline point sync use native UnrealMCP bridge commands first, with Unreal Python fallback for older running editor sessions.
- `Python/tools/editor_tools.py`
  - Adds native viewport bookmark listing, bookmark/active viewport screenshot wrappers for visual QA, and protected editor level transition preflight/opening.
- `Python/tools/texture_generation.py`
  - Registers BaseColor-focused AI texture generation tools.
- `Python/services/openai_image_service.py`
  - Calls OpenAI Images API without coupling to Unreal/MCP.
- `Python/services/unreal_texture_importer.py`
  - Wraps Unreal Python UV export, texture import, material creation, and material application helpers.
- `Docs/Tools/pcg_tools.md`
  - User-facing tool summary.
- `Docs/Tools/ai_texture_tools.md`
  - User-facing AI texture tool summary.
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

- `execute_unreal_python(code, mode="ExecuteFile", defer_to_ticker=false, allow_unsafe_editor_scripting_during_pie=false)`
  - Unsafe editor actor cleanup calls such as `EditorLevelLibrary.destroy_actor` are blocked during PIE/SIE by default.
- `list_pcg_assets(root_path="/Game")`
- `list_pcg_components()`
- `refresh_pcg_components(actor_name="", selected_only=false, cleanup=true, generate=true, wait_until_complete=false, timeout_seconds=10.0, poll_interval_seconds=0.05, max_components=1000)`
- `set_spline_component_points(points, actor_label="", actor_tag="", actor_label_prefix="", component_name="Road_SourceSpline", closed_loop=false)`
- `list_viewport_bookmarks()`
- `capture_viewport_bookmark_screenshot(filepath, bookmark_index=-1, redraw_count=2)`
- `open_editor_level(level_path, dry_run=true, allow_dirty_packages=false, load_as_template=false, show_progress=true)`
- `safe_new_preview_map(map_path, dry_run=true, allow_dirty_packages=false, overwrite_existing=false, allow_non_temp_path=false, required_root="/Game/_MCP_Temp", is_partitioned_world=false)`
- `set_pcg_debug_enabled(enabled=false, actor_name="", selected_only=false)`
- `resave_pcg_assets(root_path="/Game")`
- `get_static_mesh_uv_layout(mesh_path, uv_channel=0, output_path="")`
- `generate_texture_from_prompt(prompt, output_name, output_dir, size="1024x1024")`
- `generate_texture_for_mesh_uv(mesh_path, prompt, uv_channel=0, output_name="T_AI_Texture", output_dir="", size="1024x1024")`
- `import_texture_to_unreal(image_path, unreal_folder, asset_name)`
- `create_material_instance_with_texture(texture_asset_path, material_name, unreal_folder, base_material_path="")`
- `apply_material_to_mesh(target, material_asset_path, material_slot=0)`
- `generate_and_apply_ai_texture(target, prompt, output_name, unreal_folder="/Game/AI_Generated", uv_channel=0, size="1024x1024")`

## Design Notes

`pcg_tools.py` writes Unreal Python results to a JSON file in the temp directory because Unreal's Python command result capture is limited for multi-line scripts. The MCP tool reads that JSON file and returns structured data.

UE 5.7 multi-line scripts that include `import` statements should run through `ExecuteFile`. `ExecuteStatement` works for simple one-line commands but fails for the PCG helper's generated scripts.

The PCG component operations are native-first where a focused C++ bridge exists. `refresh_pcg_components` sends cleanup/refresh/generate requests through the C++ bridge and returns component state/readback without sleeping on the editor game thread. When `wait_until_complete=true`, the MCP Python tool polls the native command externally with `generate=false` until PCG busy state clears or the timeout expires. The Unreal Python fallback remains best-effort and does not block for completion because blocking Python can stall editor ticking. `set_spline_component_points` uses the native helper to avoid transient `TRASH_` spline components when available.

Editor level transitions should use `open_editor_level` instead of Python
`load_level`/`load_map` calls. The command defaults to `dry_run=true` and
returns target existence, current world, dirty package blockers, and whether a
real load would be attempted. Real loads are blocked by default when dirty
packages exist, avoiding the previous Python-frame world-reference crash path
and avoiding silent loss of unsaved editor state.

New temporary preview maps should use `safe_new_preview_map` instead of Python
`new_blank_map` or `new_map_from_template` calls. The command defaults to
`dry_run=true`, requires targets under `/Game/_MCP_Temp` unless explicitly
overridden, blocks dirty-package creation by default, and creates/saves the map
through the native C++ bridge.

The AI texture tools are BaseColor-first. They do not claim to create full PBR material sets. Normal, Roughness, AO, and Metallic generation should stay as separate TODO/stub work until deliberately implemented.

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
  - AI texture services/tools/docs
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

- Ran AI texture Python syntax/import checks:

```powershell
uv --directory D:\Git\unreal-mcp\Python run python -m py_compile unreal_mcp_server.py tools\texture_generation.py services\openai_image_service.py services\unreal_texture_importer.py
```

- Verified AI texture fallback behavior:
  - Missing `OPENAI_API_KEY` returns `missing_openai_api_key` without making an external call.
  - Local UV PNG renderer writes a valid PNG without Pillow.
  - `get_static_mesh_uv_layout` exported `/Game/LevelPrototyping/Meshes/SM_Cube` UV0 to PNG through UE 5.7.
  - Invalid mesh path returns a clear error.
  - Texture2D import and BaseColor Material creation succeeded after routing `execute_python` through the next game-thread tick for Interchange-safe execution.

- Verified against `D:\Git\CubelessStylized` running on `D:\Git\UnrealEngine` UE 5.7.4:
  - UnrealMCP socket responds on `127.0.0.1:55557`.
  - PCG Python API exposes `PCGComponent` and `PCGGraph`.
  - `list_pcg_assets` found 3 PCG-related `/Game` assets.
  - Current editor level had 0 PCG components, so component refresh/debug tools had no live targets.

## Build Caveat

A full C++ build against `D:\Git\UnrealEngine` started rebuilding thousands of source-engine actions and was stopped because it was too expensive for a quick verification pass. Avoid triggering a full source-engine rebuild unless the user explicitly wants that.
