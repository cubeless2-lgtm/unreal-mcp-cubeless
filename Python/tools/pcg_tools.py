"""
PCG automation tools for Unreal MCP.

The tools execute Unreal Python through the generic execute_python bridge command.
This keeps the upstream C++ surface small while letting TA scripts evolve quickly.
"""

import json
import logging
import os
import tempfile
import textwrap
from typing import Any, Dict, List

from mcp.server.fastmcp import Context, FastMCP

logger = logging.getLogger("UnrealMCP")


def _run_unreal_python_json(code_body: str) -> Dict[str, Any]:
    """Run Unreal Python code that writes RESULT to a temp JSON file."""
    from unreal_mcp_server import get_unreal_connection

    result_path = os.path.join(tempfile.gettempdir(), "unreal_mcp_pcg_result.json")
    if os.path.exists(result_path):
        os.remove(result_path)

    wrapped_code = f"""
import json
import traceback
RESULT_PATH = {result_path!r}
try:
{textwrap.indent(code_body, "    ")}
    if "RESULT" not in globals():
        RESULT = {{"success": True}}
except Exception as exc:
    RESULT = {{"success": False, "error": str(exc), "traceback": traceback.format_exc()}}
with open(RESULT_PATH, "w", encoding="utf-8") as result_file:
    json.dump(RESULT, result_file, ensure_ascii=False, indent=2, default=str)
"""

    unreal = get_unreal_connection()
    if not unreal:
        return {"success": False, "message": "Failed to connect to Unreal Engine"}

    response = unreal.send_command(
        "execute_python",
        {"code": wrapped_code, "mode": "ExecuteFile"},
    )
    if not response or response.get("status") == "error":
        return response or {"success": False, "message": "No response from Unreal Engine"}

    if not os.path.exists(result_path):
        return {
            "success": False,
            "message": "Unreal Python did not write a result file",
            "unreal_response": response,
        }

    with open(result_path, "r", encoding="utf-8") as result_file:
        result = json.load(result_file)
    result["unreal_response"] = response
    return result


def register_pcg_tools(mcp: FastMCP):
    """Register PCG-focused automation tools."""

    @mcp.tool()
    def list_pcg_assets(ctx: Context, root_path: str = "/Game") -> Dict[str, Any]:
        """
        List PCG-related assets under a content path.

        Args:
            root_path: Unreal content path to scan, for example /Game.
        """
        code = f"""
import unreal
root_path = {root_path!r}
registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = registry.get_assets_by_path(root_path, recursive=True)
items = []
for asset in assets:
    class_name = str(asset.asset_class_path.asset_name)
    package_name = str(asset.package_name)
    asset_name = str(asset.asset_name)
    if "PCG" in class_name or "PCG" in asset_name:
        items.append({{
            "asset_name": asset_name,
            "package_name": package_name,
            "class_name": class_name,
            "object_path": f"{package_name}.{asset_name}",
        }})
RESULT = {{"success": True, "count": len(items), "assets": items}}
"""
        return _run_unreal_python_json(code)

    @mcp.tool()
    def list_pcg_components(ctx: Context) -> Dict[str, Any]:
        """List PCG-like components in the current editor level."""
        code = """
import unreal
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = editor_actor_subsystem.get_all_level_actors()
items = []
for actor in actors:
    for component in actor.get_components_by_class(unreal.ActorComponent):
        class_name = component.get_class().get_name()
        if "PCG" in class_name:
            items.append({
                "actor": actor.get_actor_label(),
                "actor_path": actor.get_path_name(),
                "component": component.get_name(),
                "component_class": class_name,
            })
RESULT = {"success": True, "count": len(items), "components": items}
"""
        return _run_unreal_python_json(code)

    @mcp.tool()
    def refresh_pcg_components(
        ctx: Context,
        actor_name: str = "",
        selected_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Try to refresh/generate PCG components in the current editor level.

        Args:
            actor_name: Optional actor label/path substring filter.
            selected_only: If true, process only selected actors.
        """
        code = f"""
import unreal
actor_filter = {actor_name!r}
selected_only = {bool(selected_only)!r}
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = editor_actor_subsystem.get_selected_level_actors() if selected_only else editor_actor_subsystem.get_all_level_actors()
processed = []
errors = []
method_candidates = ["cleanup", "generate", "refresh", "dirty_generated"]
for actor in actors:
    label = actor.get_actor_label()
    path = actor.get_path_name()
    if actor_filter and actor_filter not in label and actor_filter not in path:
        continue
    for component in actor.get_components_by_class(unreal.ActorComponent):
        class_name = component.get_class().get_name()
        if "PCG" not in class_name:
            continue
        called = []
        for method_name in method_candidates:
            method = getattr(component, method_name, None)
            if not method:
                continue
            try:
                method()
                called.append(method_name)
            except Exception as exc:
                errors.append({
                    "actor": label,
                    "component": component.get_name(),
                    "method": method_name,
                    "error": str(exc),
                })
        processed.append({
            "actor": label,
            "component": component.get_name(),
            "component_class": class_name,
            "called_methods": called,
        })
RESULT = {"success": True, "count": len(processed), "processed": processed, "errors": errors}
"""
        return _run_unreal_python_json(code)

    @mcp.tool()
    def set_pcg_debug_enabled(
        ctx: Context,
        enabled: bool = False,
        actor_name: str = "",
        selected_only: bool = False,
    ) -> Dict[str, Any]:
        """
        Best-effort toggle for common PCG component debug/editor flags.

        Args:
            enabled: Desired debug state.
            actor_name: Optional actor label/path substring filter.
            selected_only: If true, process only selected actors.
        """
        code = f"""
import unreal
enabled = {bool(enabled)!r}
actor_filter = {actor_name!r}
selected_only = {bool(selected_only)!r}
property_names = [
    "debug",
    "bDebug",
    "b_debug",
    "show_debug",
    "bShowDebug",
    "b_show_debug",
    "debug_enabled",
    "bDebugEnabled",
    "b_debug_enabled",
]
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = editor_actor_subsystem.get_selected_level_actors() if selected_only else editor_actor_subsystem.get_all_level_actors()
changed = []
errors = []
for actor in actors:
    label = actor.get_actor_label()
    path = actor.get_path_name()
    if actor_filter and actor_filter not in label and actor_filter not in path:
        continue
    for component in actor.get_components_by_class(unreal.ActorComponent):
        class_name = component.get_class().get_name()
        if "PCG" not in class_name:
            continue
        component_changes = []
        for property_name in property_names:
            try:
                component.set_editor_property(property_name, enabled)
                component_changes.append(property_name)
            except Exception:
                pass
        if component_changes:
            changed.append({
                "actor": label,
                "component": component.get_name(),
                "component_class": class_name,
                "properties": component_changes,
            })
RESULT = {"success": True, "count": len(changed), "changed": changed, "errors": errors}
"""
        return _run_unreal_python_json(code)

    @mcp.tool()
    def resave_pcg_assets(ctx: Context, root_path: str = "/Game") -> Dict[str, Any]:
        """
        Resave PCG-related assets under a content path.

        Args:
            root_path: Unreal content path to scan, for example /Game.
        """
        code = f"""
import unreal
root_path = {root_path!r}
registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = registry.get_assets_by_path(root_path, recursive=True)
saved = []
errors = []
for asset_data in assets:
    class_name = str(asset_data.asset_class_path.asset_name)
    asset_name = str(asset_data.asset_name)
    package_name = str(asset_data.package_name)
    if "PCG" not in class_name and "PCG" not in asset_name:
        continue
    try:
        asset = unreal.EditorAssetLibrary.load_asset(package_name)
        if asset and unreal.EditorAssetLibrary.save_loaded_asset(asset):
            saved.append(package_name)
    except Exception as exc:
        errors.append({"asset": package_name, "error": str(exc)})
RESULT = {"success": True, "count": len(saved), "saved": saved, "errors": errors}
"""
        return _run_unreal_python_json(code)

    logger.info("PCG tools registered successfully")
