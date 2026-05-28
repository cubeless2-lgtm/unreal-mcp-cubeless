# PCG Tools

These tools are local TA extensions on top of `chongdashu/unreal-mcp`.

They use the generic `execute_python` bridge command, so most PCG logic can live in Python and stay easy to update when upstream changes.

## Tools

- `execute_unreal_python(code, mode="ExecuteStatement")`
  - Executes arbitrary Python in the running Unreal Editor.
- `list_pcg_assets(root_path="/Game")`
  - Lists PCG-related assets by class/name.
- `list_pcg_components()`
  - Lists PCG-like components in the current level.
- `refresh_pcg_components(actor_name="", selected_only=false)`
  - Best-effort calls common PCG component refresh/generate methods.
- `set_pcg_debug_enabled(enabled=false, actor_name="", selected_only=false)`
  - Best-effort toggles common PCG component debug properties.
- `resave_pcg_assets(root_path="/Game")`
  - Loads and saves PCG-related assets under a content path.

## Maintenance

Keep upstream updates clean by maintaining this extension as a small patch:

```powershell
cd D:\Git\unreal-mcp
git fetch origin
git checkout main
git pull --ff-only
git checkout -b local/pcg-tools
git cherry-pick <your-pcg-extension-commit>
```

If upstream changes `Python/unreal_mcp_server.py` or `UnrealMCPBridge.cpp`, reapply only the import/register lines and the `execute_python` route.
