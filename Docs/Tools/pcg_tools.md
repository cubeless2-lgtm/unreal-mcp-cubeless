# PCG Tools

These tools are local TA extensions on top of `chongdashu/unreal-mcp`.

They prefer native UnrealMCP bridge commands for fast editor operations, then fall back to the generic `execute_python` bridge command when a running editor has not loaded the newer native command yet.

Exception: `set_pcg_attribute_selector` is native-only. It deliberately does not fall back to Unreal Python because mutating `FPCGAttributePropertySelector` structs through Python can trigger PythonScriptPlugin wrapper ensures and later editor shutdown crashes.

## Tools

- `execute_unreal_python(code, mode="ExecuteStatement")`
  - Executes arbitrary Python in the running Unreal Editor.
- `list_pcg_assets(root_path="/Game")`
  - Lists PCG-related assets by class/name.
- `list_pcg_components()`
  - Lists PCG-like components in the current level.
- `refresh_pcg_components(actor_name="", selected_only=false, cleanup=true, generate=true, wait_until_complete=false, timeout_seconds=10.0, poll_interval_seconds=0.05, max_components=1000)`
  - Native-first PCG cleanup/refresh/generate. The C++ bridge returns quickly with component state/readback; when `wait_until_complete=true`, the MCP Python tool polls that native state externally until PCG busy state clears or the timeout expires.
- `set_spline_component_points(points, actor_label="", actor_tag="", actor_label_prefix="", component_name="Road_SourceSpline", closed_loop=false)`
  - Native-first SplineComponent point sync that avoids transient `TRASH_` components and reports final point count, length, and max point delta.
- `set_pcg_debug_enabled(enabled=false, actor_name="", selected_only=false)`
  - Best-effort toggles common PCG component debug properties.
- `set_pcg_attribute_selector(graph_path, node_id, selector_property_name, selector_type="attribute", attribute_name="", selected_property_name="", domain_name="", point_property="", extra_property="", extra_names=None, reset_extra_names=true, save=true, dry_run=false)`
  - Native-only setter for PCG selector struct properties such as `WeightAttribute` / `weight_attribute`, `MatchAttribute`, `InputAttribute`, and `SetTarget`.
  - Use this instead of `execute_python` plus `PCGAttributePropertySelectorBlueprintHelpers.set_*`.
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
