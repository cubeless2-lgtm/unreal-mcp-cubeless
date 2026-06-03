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

    def send_pcg_command(command_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        from unreal_mcp_server import get_unreal_connection

        unreal = get_unreal_connection()
        if not unreal:
            logger.error("Failed to connect to Unreal Engine")
            return {"success": False, "message": "Failed to connect to Unreal Engine"}

        response = unreal.send_command(command_name, params)
        if not response:
            logger.error("No response from Unreal Engine")
            return {"success": False, "message": "No response from Unreal Engine"}

        return response

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

    @mcp.tool()
    def resolve_pcg_graph(ctx: Context, graph_path: str) -> Dict[str, Any]:
        """
        Resolve a PCG graph by short name, package path, or object path.

        Args:
            graph_path: PCG graph name or path
        """
        try:
            return send_pcg_command("resolve_pcg_graph", {"graph_path": graph_path})
        except Exception as e:
            error_msg = f"Error resolving PCG graph: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def list_pcg_graph_nodes(
        ctx: Context,
        graph_path: str,
        node_type: str = "",
        title_contains: str = "",
        include_pins: bool = True,
    ) -> Dict[str, Any]:
        """
        List nodes, pins, and edges in a PCG graph.

        Args:
            graph_path: PCG graph name or path
            node_type: Optional settings class/name substring filter
            title_contains: Optional title substring filter
            include_pins: Include pin and edge metadata
        """
        try:
            params = {
                "graph_path": graph_path,
                "node_type": node_type,
                "title_contains": title_contains,
                "include_pins": include_pins,
            }
            return send_pcg_command("list_pcg_graph_nodes", params)
        except Exception as e:
            error_msg = f"Error listing PCG graph nodes: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_pcg_node(
        ctx: Context,
        graph_path: str,
        settings_class: str,
        node_position=None,
        node_title: str = "",
        settings: Dict[str, Any] | None = None,
    ) -> Dict[str, Any]:
        """
        Add a node to a PCG graph using a UPCGSettings class.

        Args:
            graph_path: PCG graph name or path
            settings_class: UPCGSettings class name or class path
            node_position: Optional [X, Y] editor position
            node_title: Optional authored node title
            settings: Optional settings property map
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            if settings is None:
                settings = {}
            params = {
                "graph_path": graph_path,
                "settings_class": settings_class,
                "node_position": node_position,
                "node_title": node_title,
                "settings": settings,
            }
            return send_pcg_command("add_pcg_node", params)
        except Exception as e:
            error_msg = f"Error adding PCG node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def connect_pcg_nodes(
        ctx: Context,
        graph_path: str,
        from_node_id: str,
        from_pin: str,
        to_node_id: str,
        to_pin: str,
    ) -> Dict[str, Any]:
        """
        Connect two PCG graph nodes by pin label.

        Args:
            graph_path: PCG graph name or path
            from_node_id: Source node id/name/path
            from_pin: Source output pin label
            to_node_id: Target node id/name/path
            to_pin: Target input pin label
        """
        try:
            params = {
                "graph_path": graph_path,
                "from_node_id": from_node_id,
                "from_pin": from_pin,
                "to_node_id": to_node_id,
                "to_pin": to_pin,
            }
            return send_pcg_command("connect_pcg_nodes", params)
        except Exception as e:
            error_msg = f"Error connecting PCG nodes: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_pcg_node_setting(
        ctx: Context,
        graph_path: str,
        node_id: str,
        property_name: str,
        value: Any,
    ) -> Dict[str, Any]:
        """
        Set a property on a PCG node settings object.

        Args:
            graph_path: PCG graph name or path
            node_id: Node id/name/path
            property_name: Settings property name
            value: New property value
        """
        try:
            params = {
                "graph_path": graph_path,
                "node_id": node_id,
                "property_name": property_name,
                "value": value,
            }
            return send_pcg_command("set_pcg_node_setting", params)
        except Exception as e:
            error_msg = f"Error setting PCG node setting: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def compile_or_notify_pcg_graph(ctx: Context, graph_path: str) -> Dict[str, Any]:
        """
        Notify a PCG graph of structural changes and request recompilation.

        Args:
            graph_path: PCG graph name or path
        """
        try:
            return send_pcg_command("compile_or_notify_pcg_graph", {"graph_path": graph_path})
        except Exception as e:
            error_msg = f"Error notifying PCG graph: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def save_pcg_graph(ctx: Context, graph_path: str) -> Dict[str, Any]:
        """
        Save a loaded PCG graph asset.

        Args:
            graph_path: PCG graph name or path
        """
        try:
            return send_pcg_command("save_pcg_graph", {"graph_path": graph_path})
        except Exception as e:
            error_msg = f"Error saving PCG graph: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    logger.info("PCG tools registered successfully")
