"""
PCG automation tools for Unreal MCP.

Fast editor operations prefer native UnrealMCP bridge commands when available.
Unreal Python remains as a compatibility fallback for older running editor
sessions or commands that still need TA script flexibility.
"""

import json
import logging
import os
import tempfile
import textwrap
import time
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


def _bridge_response_succeeded(response: Dict[str, Any] | None) -> bool:
    if not response:
        return False
    return response.get("status") == "success" or response.get("success") is True


def _bridge_response_unknown_command(response: Dict[str, Any] | None, command_name: str) -> bool:
    if not response:
        return False
    error_text = str(response.get("error") or response.get("message") or "")
    return response.get("status") == "error" and "Unknown command" in error_text and command_name in error_text


def _native_result_with_marker(response: Dict[str, Any], command_name: str) -> Dict[str, Any]:
    result = response.get("result", response)
    if isinstance(result, dict):
        result = dict(result)
    else:
        result = {"result": result}
    result.setdefault("success", True)
    result["native_command_used"] = True
    result["native_command"] = command_name
    result["native_response"] = response
    return result


def _int_or_default(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _native_refresh_result_ready(result: Dict[str, Any]) -> bool:
    components = result.get("components", [])
    if not isinstance(components, list):
        return bool(result.get("wait_completed", False))
    if not components:
        return _int_or_default(result.get("component_count"), 0) == 0

    min_generated_output_data_count = _int_or_default(
        result.get("min_generated_output_data_count"),
        -1,
    )
    min_managed_resource_count = _int_or_default(
        result.get("min_managed_resource_count"),
        -1,
    )

    for component in components:
        if not isinstance(component, dict):
            return False
        if (
            component.get("generating")
            or component.get("cleaning_up")
            or component.get("refresh_in_progress")
        ):
            return False
        if (
            min_generated_output_data_count >= 0
            and _int_or_default(component.get("generated_output_data_count"), 0)
            < min_generated_output_data_count
        ):
            return False
        if (
            min_managed_resource_count >= 0
            and _int_or_default(component.get("managed_resource_count"), 0)
            < min_managed_resource_count
        ):
            return False

    return True


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

    def poll_native_refresh_completion(
        command_name: str,
        initial_params: Dict[str, Any],
        initial_result: Dict[str, Any],
        timeout_seconds: float,
        poll_interval_seconds: float,
    ) -> Dict[str, Any]:
        timeout_seconds = max(0.0, min(float(timeout_seconds), 300.0))
        poll_interval_seconds = max(0.005, min(float(poll_interval_seconds), 1.0))

        poll_params = dict(initial_params)
        poll_params.update(
            {
                "cleanup": False,
                "generate": False,
                "refresh": False,
                "force": False,
                "wait_until_complete": True,
            }
        )

        result = dict(initial_result)
        start_time = time.monotonic()
        iterations = 0
        ready = _native_refresh_result_ready(result)

        while not ready:
            elapsed = time.monotonic() - start_time
            if elapsed >= timeout_seconds:
                break

            time.sleep(min(poll_interval_seconds, timeout_seconds - elapsed))
            iterations += 1

            poll_response = send_pcg_command(command_name, poll_params)
            if not _bridge_response_succeeded(poll_response):
                return {
                    "success": False,
                    "native_command_used": True,
                    "native_command": command_name,
                    "native_response": poll_response,
                    "initial_native_response": initial_result.get("native_response"),
                    "message": "Native PCG completion poll failed",
                }

            result = _native_result_with_marker(poll_response, command_name)
            ready = _native_refresh_result_ready(result)

        elapsed = time.monotonic() - start_time
        result["external_wait_used"] = True
        result["wait_requested"] = True
        result["wait_supported"] = True
        result["wait_mode"] = "external_mcp_poll"
        result["wait_completed"] = ready
        result["wait_timed_out"] = not ready
        result["wait_elapsed_seconds"] = elapsed
        result["wait_iterations"] = iterations
        result["timeout_seconds"] = timeout_seconds
        result["poll_interval_seconds"] = poll_interval_seconds
        result["initial_native_response"] = initial_result.get("native_response")
        result["initial_component_count"] = initial_result.get("component_count")
        result["initial_cleanup_count"] = initial_result.get("cleanup_count")
        result["initial_refresh_count"] = initial_result.get("refresh_count")
        result["initial_generate_count"] = initial_result.get("generate_count")
        return result

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
            "object_path": f"{{package_name}}.{{asset_name}}",
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
        cleanup: bool = True,
        generate: bool = True,
        refresh: bool = False,
        force: bool = True,
        wait_until_complete: bool = False,
        timeout_seconds: float = 10.0,
        poll_interval_seconds: float = 0.05,
        min_generated_output_data_count: int = -1,
        min_managed_resource_count: int = -1,
        max_components: int = 1000,
        native_first: bool = True,
    ) -> Dict[str, Any]:
        """
        Try to refresh/generate PCG components in the current editor level.

        Args:
            actor_name: Optional actor label/path substring filter.
            selected_only: If true, process only selected actors.
            cleanup: Clean existing generated output before generation.
            generate: Request PCG generation.
            refresh: Dirty and refresh components before generation.
            force: Force PCG generation when the native command is available.
            wait_until_complete: Poll native component state externally until PCG busy state clears.
            timeout_seconds: External native polling timeout.
            poll_interval_seconds: External native polling interval.
            min_generated_output_data_count: Optional native wait minimum generated output data count.
            min_managed_resource_count: Optional native wait minimum managed resource count.
            max_components: Maximum native PCG components to process.
            native_first: Prefer the native C++ bridge command when available.
        """
        native_command = "refresh_pcg_components"
        native_response = None
        if native_first:
            native_params: Dict[str, Any] = {
                "selected_only": selected_only,
                "cleanup": cleanup,
                "generate": generate,
                "refresh": refresh,
                "force": force,
                "wait_until_complete": False,
                "timeout_seconds": timeout_seconds,
                "poll_interval_seconds": poll_interval_seconds,
                "min_generated_output_data_count": min_generated_output_data_count,
                "min_managed_resource_count": min_managed_resource_count,
                "max_components": max_components,
            }
            if actor_name:
                native_params["actor_label_prefix"] = actor_name
            native_response = send_pcg_command(native_command, native_params)
            if _bridge_response_succeeded(native_response):
                native_result = _native_result_with_marker(native_response, native_command)
                if not actor_name or int(native_result.get("component_count", 0)) > 0:
                    if wait_until_complete:
                        return poll_native_refresh_completion(
                            native_command,
                            native_params,
                            native_result,
                            timeout_seconds,
                            poll_interval_seconds,
                        )
                    return native_result
            elif native_response and not _bridge_response_unknown_command(native_response, native_command):
                return {
                    "success": False,
                    "native_command_used": False,
                    "native_command": native_command,
                    "native_response": native_response,
                    "message": "Native PCG refresh command failed before Python fallback",
                }

        method_candidates = []
        if cleanup:
            method_candidates.append("cleanup")
        if refresh:
            method_candidates.extend(["refresh", "dirty_generated"])
        if generate:
            method_candidates.append("generate")
        if not method_candidates:
            method_candidates = ["refresh"]

        code = f"""
import unreal
actor_filter = {actor_name!r}
selected_only = {bool(selected_only)!r}
method_candidates = {method_candidates!r}
max_components = {int(max_components)!r}
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = editor_actor_subsystem.get_selected_level_actors() if selected_only else editor_actor_subsystem.get_all_level_actors()
processed = []
errors = []
limit_hit = False
for actor in actors:
    if len(processed) >= max_components:
        limit_hit = True
        break
    label = actor.get_actor_label()
    path = actor.get_path_name()
    if actor_filter and actor_filter not in label and actor_filter not in path:
        continue
    for component in actor.get_components_by_class(unreal.ActorComponent):
        class_name = component.get_class().get_name()
        if "PCG" not in class_name:
            continue
        if len(processed) >= max_components:
            limit_hit = True
            break
        called = []
        for method_name in method_candidates:
            method = getattr(component, method_name, None)
            if not method:
                continue
            try:
                method()
                called.append(method_name)
            except Exception as exc:
                errors.append({{
                    "actor": label,
                    "component": component.get_name(),
                    "method": method_name,
                    "error": str(exc),
                }})
        processed.append({{
            "actor": label,
            "component": component.get_name(),
            "component_class": class_name,
            "called_methods": called,
        }})
RESULT = {{
    "success": True,
    "native_command_used": False,
    "native_command": {native_command!r},
    "native_response": {native_response!r},
    "fallback_reason": "native unavailable or no matching native components",
    "wait_requested": {bool(wait_until_complete)!r},
    "wait_supported": False,
    "wait_note": "Python fallback does not block for PCG completion because that can stall editor ticking; use native refresh_pcg_components for wait_until_complete.",
    "count": len(processed),
    "component_limit_hit": limit_hit,
    "processed": processed,
    "errors": errors,
}}
"""
        return _run_unreal_python_json(code)

    @mcp.tool()
    def set_spline_component_points(
        ctx: Context,
        points: List[List[float]],
        actor_label: str = "",
        actor_name: str = "",
        actor_tag: str = "",
        actor_label_prefix: str = "",
        component_name: str = "Road_SourceSpline",
        component_tag: str = "",
        selected_only: bool = False,
        closed_loop: bool = False,
        native_first: bool = True,
    ) -> Dict[str, Any]:
        """
        Set points on a SplineComponent, preferring the native C++ bridge helper.

        Args:
            points: World-space points as [[x, y, z], ...].
            actor_label: Exact actor label filter.
            actor_name: Exact actor object name filter.
            actor_tag: Actor tag filter.
            actor_label_prefix: Actor label prefix filter.
            component_name: Spline component name, default Road_SourceSpline.
            component_tag: Spline component tag filter.
            selected_only: If true, process the selected actor.
            closed_loop: Set the spline closed-loop state.
            native_first: Prefer the native C++ bridge command when available.
        """
        native_command = "set_spline_component_points"
        if not points or len(points) < 2:
            return {"success": False, "message": "points must contain at least two [x, y, z] values"}

        native_response = None
        if native_first:
            native_params = {
                "points": points,
                "actor_label": actor_label,
                "actor_name": actor_name,
                "actor_tag": actor_tag,
                "actor_label_prefix": actor_label_prefix,
                "component_name": component_name,
                "component_tag": component_tag,
                "selected_only": selected_only,
                "closed_loop": closed_loop,
            }
            native_response = send_pcg_command(native_command, native_params)
            if _bridge_response_succeeded(native_response):
                return _native_result_with_marker(native_response, native_command)
            if native_response and not _bridge_response_unknown_command(native_response, native_command):
                return {
                    "success": False,
                    "native_command_used": False,
                    "native_command": native_command,
                    "native_response": native_response,
                    "message": "Native spline point command failed before Python fallback",
                }

        code = f"""
import math
import unreal

points = {points!r}
actor_label = {actor_label!r}
actor_name = {actor_name!r}
actor_tag = {actor_tag!r}
actor_label_prefix = {actor_label_prefix!r}
component_name = {component_name!r}
component_tag = {component_tag!r}
selected_only = {bool(selected_only)!r}
closed_loop = {bool(closed_loop)!r}

def actor_tags(actor):
    try:
        return [str(item) for item in actor.get_editor_property("tags")]
    except Exception:
        return []

def component_tags(component):
    try:
        return [str(item) for item in component.get_editor_property("component_tags")]
    except Exception:
        return []

def actor_matches(actor):
    label = actor.get_actor_label()
    name = actor.get_name()
    if actor_label and label.lower() != actor_label.lower():
        return False
    if actor_name and name.lower() != actor_name.lower():
        return False
    if actor_tag and actor_tag not in actor_tags(actor):
        return False
    if actor_label_prefix and not label.lower().startswith(actor_label_prefix.lower()):
        return False
    return True

editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = editor_actor_subsystem.get_selected_level_actors() if selected_only else editor_actor_subsystem.get_all_level_actors()
matches = [actor for actor in actors if actor_matches(actor)]
if not matches:
    raise RuntimeError("No matching actor found for spline point update")
if len(matches) > 1:
    raise RuntimeError("Multiple matching actors found: " + str([actor.get_actor_label() for actor in matches]))

actor = matches[0]
splines = [
    component
    for component in actor.get_components_by_class(unreal.SplineComponent)
    if not component.get_name().startswith("TRASH_")
]
if component_name:
    splines = [component for component in splines if component.get_name().lower() == component_name.lower()]
if component_tag:
    splines = [component for component in splines if component_tag in component_tags(component)]
if not splines:
    raise RuntimeError("No matching SplineComponent found on actor: " + actor.get_actor_label())

spline = splines[0]
actor.modify()
spline.modify()
try:
    spline.set_editor_property("input_spline_points_to_construction_script", True)
except Exception:
    pass
spline.clear_spline_points(False)
for point in points:
    spline.add_spline_point(unreal.Vector(float(point[0]), float(point[1]), float(point[2])), unreal.SplineCoordinateSpace.WORLD, False)
for index in range(len(points)):
    spline.set_spline_point_type(index, unreal.SplinePointType.LINEAR, False)
try:
    spline.set_closed_loop(closed_loop, False)
except Exception:
    pass
spline.update_spline()

final_points = []
deltas = []
for index in range(int(spline.get_number_of_spline_points())):
    location = spline.get_location_at_spline_point(index, unreal.SplineCoordinateSpace.WORLD)
    final = [float(location.x), float(location.y), float(location.z)]
    final_points.append(final)
    if index < len(points):
        expected = points[index]
        deltas.append(math.sqrt(
            (float(final[0]) - float(expected[0])) ** 2
            + (float(final[1]) - float(expected[1])) ** 2
            + (float(final[2]) - float(expected[2])) ** 2
        ))

RESULT = {{
    "success": True,
    "native_command_used": False,
    "native_command": {native_command!r},
    "native_response": {native_response!r},
    "fallback_reason": "native unavailable",
    "actor": actor.get_actor_label(),
    "actor_path": actor.get_path_name(),
    "component_name": spline.get_name(),
    "component_path": spline.get_path_name(),
    "requested_point_count": len(points),
    "final_point_count": int(spline.get_number_of_spline_points()),
    "spline_length": float(spline.get_spline_length()),
    "max_point_delta_cm": max(deltas) if deltas else 0.0,
    "points": final_points,
}}
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
            changed.append({{
                "actor": label,
                "component": component.get_name(),
                "component_class": class_name,
                "properties": component_changes,
            }})
RESULT = {{"success": True, "count": len(changed), "changed": changed, "errors": errors}}
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
        errors.append({{"asset": package_name, "error": str(exc)}})
RESULT = {{"success": True, "count": len(saved), "saved": saved, "errors": errors}}
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
