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
    def create_pcg_graph_from_spec(
        ctx: Context,
        graph_spec: Dict[str, Any],
        overwrite_existing: bool = False,
        allow_overwrite_non_temp: bool = False,
        save: bool = True,
        dry_run: bool = False,
    ) -> Dict[str, Any]:
        """
        Create a PCG graph from a compact JSON-style spec.

        The spec supports:
        - asset_path: /Game package path for the graph
        - nodes: [{id, settings_class, title, position, settings, mesh_entries}]
        - edges: [{from, from_pin, to, to_pin}]
        - forbidden_dependency_prefixes: optional dependency guard after save

        Use /Game/_MCP_Temp for disposable validation graphs. Overwriting a
        non-temp graph requires allow_overwrite_non_temp=True.
        """
        if not isinstance(graph_spec, dict):
            return {"success": False, "message": "graph_spec must be an object"}

        spec_json = json.dumps(graph_spec, ensure_ascii=False)
        code = """
import json
import math
import unreal

spec = json.loads(__SPEC_JSON__)
overwrite_existing = __OVERWRITE_EXISTING__
allow_overwrite_non_temp = __ALLOW_OVERWRITE_NON_TEMP__
save_graph = __SAVE_GRAPH__
dry_run = __DRY_RUN__

def normalize_package_path(path):
    if not path:
        return ""
    text = str(path).strip()
    if "." in text and text.startswith("/Game/"):
        text = text.split(".", 1)[0]
    return text.rstrip("/")

def split_asset_path(path):
    package_path = normalize_package_path(path)
    if not package_path.startswith("/Game/"):
        raise RuntimeError("asset_path must be a /Game package path")
    parent, _, asset_name = package_path.rpartition("/")
    if not parent or not asset_name:
        raise RuntimeError("asset_path must include a parent folder and asset name")
    return parent, asset_name, package_path

def resolve_unreal_class(class_name):
    if not class_name:
        raise RuntimeError("settings_class is required")
    name = str(class_name)
    if hasattr(unreal, name):
        return getattr(unreal, name)
    loaded = unreal.load_class(None, name)
    if loaded:
        return loaded
    if not name.startswith("PCG") and hasattr(unreal, "PCG" + name):
        return getattr(unreal, "PCG" + name)
    raise RuntimeError("Could not resolve Unreal class: " + name)

def pin_label(pin):
    props = pin.get_editor_property("properties")
    return str(props.get_editor_property("label"))

def edge_count_for_pin(node, pin_name, pin_key):
    for pin in node.get_editor_property(pin_key):
        if pin_label(pin) == pin_name:
            return len(pin.get_editor_property("edges"))
    return -1

def enum_value_from_string(current, value):
    enum_class = getattr(unreal, type(current).__name__, None)
    if not enum_class:
        return value
    token = str(value).split(".")[-1]
    candidates = [token, token.upper()]
    for candidate in candidates:
        if hasattr(enum_class, candidate):
            return getattr(enum_class, candidate)
    return value

def coerce_value(current, value):
    type_name = type(current).__name__
    if value is None:
        return None
    if isinstance(value, str) and type_name.startswith("PCG"):
        return enum_value_from_string(current, value)
    if type_name == "Vector" and isinstance(value, (list, tuple)) and len(value) >= 3:
        return unreal.Vector(float(value[0]), float(value[1]), float(value[2]))
    if type_name == "Rotator" and isinstance(value, (list, tuple)) and len(value) >= 3:
        return unreal.Rotator(float(value[0]), float(value[1]), float(value[2]))
    if type_name == "Name":
        return unreal.Name(str(value))
    return value

def set_property_recursive(obj, property_name, value):
    if isinstance(value, dict):
        try:
            nested = obj.get_editor_property(property_name)
        except Exception:
            nested = None
        if nested is None:
            obj.set_editor_property(property_name, value)
            return
        for key, nested_value in value.items():
            set_property_recursive(nested, key, nested_value)
        try:
            obj.set_editor_property(property_name, nested)
        except Exception:
            pass
        return

    try:
        current = obj.get_editor_property(property_name)
        value = coerce_value(current, value)
    except Exception:
        pass
    obj.set_editor_property(property_name, value)

def apply_settings(settings_obj, settings_spec):
    applied = []
    errors = []
    for property_name, value in (settings_spec or {}).items():
        try:
            set_property_recursive(settings_obj, property_name, value)
            applied.append(property_name)
        except Exception as exc:
            errors.append({"property": property_name, "error": str(exc)})
    return applied, errors

def static_mesh_from_path(path):
    mesh = unreal.load_asset(str(path))
    if not mesh:
        raise RuntimeError("Could not load static mesh: " + str(path))
    if mesh.get_class().get_name() != "StaticMesh":
        raise RuntimeError("Asset is not a StaticMesh: " + str(path))
    return mesh

def configure_static_mesh_spawner(settings_obj, node_spec):
    configured = {}
    errors = []
    selector_spec = node_spec.get("mesh_selector") or {}
    selector_type = str(selector_spec.get("type") or "").lower()

    if selector_type in ("by_attribute", "attribute"):
        try:
            settings_obj.set_mesh_selector_type(unreal.PCGMeshSelectorByAttribute)
        except Exception as exc:
            errors.append({"mesh_selector_type": "by_attribute", "error": str(exc)})
        selector = settings_obj.get_editor_property("mesh_selector_parameters")
        try:
            selector.set_editor_property("attribute_name", unreal.Name(str(selector_spec.get("attribute_name", "Meshes"))))
            material_attrs = [
                unreal.Name(str(item))
                for item in selector_spec.get("material_override_attributes", [])
            ]
            if material_attrs:
                selector.set_editor_property("material_override_attributes", material_attrs)
                selector.set_editor_property("use_attribute_material_overrides", True)
            configured["mesh_selector"] = "by_attribute"
        except Exception as exc:
            errors.append({"mesh_selector": "by_attribute", "error": str(exc)})

    entries_spec = (
        node_spec.get("mesh_entries")
        or node_spec.get("static_mesh_entries")
        or node_spec.get("spawner_mesh_entries")
        or selector_spec.get("entries")
        or []
    )
    if entries_spec:
        try:
            try:
                settings_obj.set_mesh_selector_type(unreal.PCGMeshSelectorWeighted)
            except Exception:
                pass
            selector = settings_obj.get_editor_property("mesh_selector_parameters")
            entries = []
            for entry_spec in entries_spec:
                mesh_path = entry_spec.get("mesh") or entry_spec.get("static_mesh") or entry_spec.get("path")
                mesh = static_mesh_from_path(mesh_path)
                descriptor = unreal.PCGSoftISMComponentDescriptor()
                descriptor.set_editor_property("static_mesh", mesh)
                if "cast_shadow" in entry_spec:
                    descriptor.set_editor_property("cast_shadow", bool(entry_spec["cast_shadow"]))
                if "receives_decals" in entry_spec:
                    descriptor.set_editor_property("receives_decals", bool(entry_spec["receives_decals"]))
                if "override_materials" in entry_spec:
                    materials = []
                    for material_path in entry_spec.get("override_materials") or []:
                        material = unreal.load_asset(str(material_path))
                        if material:
                            materials.append(material)
                    descriptor.set_editor_property("override_materials", materials)
                entry = unreal.PCGMeshSelectorWeightedEntry()
                entry.set_editor_property("descriptor", descriptor)
                entry.set_editor_property("weight", int(entry_spec.get("weight", 1)))
                entries.append(entry)
            selector.set_editor_property("mesh_entries", entries)
            configured["weighted_mesh_entries"] = len(entries)
        except Exception as exc:
            errors.append({"mesh_entries": "weighted", "error": str(exc)})
    return configured, errors

def graph_dependencies(package_path):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    try:
        options = unreal.AssetRegistryDependencyOptions(
            include_soft_package_references=True,
            include_hard_package_references=True,
            include_searchable_names=False,
            include_soft_management_references=False,
            include_hard_management_references=False,
        )
        return [str(item) for item in registry.get_dependencies(package_path, options)]
    except TypeError:
        return [str(item) for item in registry.get_dependencies(package_path)]

asset_path = spec.get("asset_path") or spec.get("graph_path")
parent_path, asset_name, package_path = split_asset_path(asset_path)
nodes_spec = spec.get("nodes") or []
edges_spec = spec.get("edges") or []
forbidden_prefixes = list(spec.get("forbidden_dependency_prefixes") or [])

if dry_run:
    RESULT = {
        "success": True,
        "dry_run": True,
        "asset_path": package_path,
        "node_count": len(nodes_spec),
        "edge_count": len(edges_spec),
        "would_overwrite": bool(unreal.EditorAssetLibrary.does_asset_exist(package_path)),
    }
else:
    unreal.EditorAssetLibrary.make_directory(parent_path)
    graph = None
    if unreal.EditorAssetLibrary.does_asset_exist(package_path):
        if not overwrite_existing:
            raise RuntimeError("Asset already exists: " + package_path)
        if not allow_overwrite_non_temp and not package_path.startswith("/Game/_MCP_Temp/"):
            raise RuntimeError("Refusing to overwrite non-temp PCG graph without allow_overwrite_non_temp=True: " + package_path)
        existing_asset = unreal.EditorAssetLibrary.load_asset(package_path)
        if existing_asset and "PCGGraph" in existing_asset.get_class().get_name():
            graph = existing_asset
            for existing_node in list(graph.get_editor_property("nodes")):
                graph.remove_node(existing_node)
        elif not unreal.EditorAssetLibrary.delete_asset(package_path):
            raise RuntimeError("Failed to delete existing non-PCG asset before overwrite: " + package_path)

    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    if graph is None:
        graph = asset_tools.create_asset(asset_name, parent_path, unreal.PCGGraph, unreal.PCGGraphFactory())
    if not graph:
        raise RuntimeError("Failed to create PCG graph: " + package_path)

    node_lookup = {
        "__input__": graph.get_input_node(),
        "__output__": graph.get_output_node(),
        "input": graph.get_input_node(),
        "output": graph.get_output_node(),
    }
    created_nodes = []
    setting_errors = []
    spawner_errors = []
    for index, node_spec in enumerate(nodes_spec):
        node_id = str(node_spec.get("id") or node_spec.get("title") or "Node_" + str(index))
        settings_class = resolve_unreal_class(node_spec.get("settings_class") or node_spec.get("class"))
        result = graph.add_node_of_type(settings_class)
        if isinstance(result, tuple):
            node, settings_obj = result[0], result[1]
        else:
            node, settings_obj = result, result.get_settings()
        title = str(node_spec.get("title") or node_id)
        if title:
            node.set_editor_property("node_title", unreal.Name(title))
        position = node_spec.get("position") or node_spec.get("node_position") or [index * 320, 0]
        if isinstance(position, (list, tuple)) and len(position) >= 2:
            node.set_node_position(int(position[0]), int(position[1]))

        applied, errors = apply_settings(settings_obj, node_spec.get("settings") or {})
        for error in errors:
            error["node_id"] = node_id
        setting_errors.extend(errors)

        spawner_config = {}
        if settings_obj.get_class().get_name() == "PCGStaticMeshSpawnerSettings":
            spawner_config, errors = configure_static_mesh_spawner(settings_obj, node_spec)
            for error in errors:
                error["node_id"] = node_id
            spawner_errors.extend(errors)

        node_lookup[node_id] = node
        node_lookup[title] = node
        node_lookup[node.get_name()] = node
        created_nodes.append({
            "id": node_id,
            "title": title,
            "node_name": node.get_name(),
            "settings_class": settings_obj.get_class().get_name(),
            "position": list(node.get_node_position()),
            "settings_applied": applied,
            "spawner_config": spawner_config,
        })

    connected_edges = []
    edge_errors = []
    for edge_spec in edges_spec:
        from_id = str(edge_spec.get("from") or edge_spec.get("from_node") or "")
        to_id = str(edge_spec.get("to") or edge_spec.get("to_node") or "")
        from_node = node_lookup.get(from_id)
        to_node = node_lookup.get(to_id)
        if not from_node or not to_node:
            edge_errors.append({"edge": edge_spec, "error": "Unknown from/to node id"})
            continue
        from_pin = str(edge_spec.get("from_pin") or "Out")
        to_pin = str(edge_spec.get("to_pin") or ("Out" if to_id in ("__output__", "output") else "In"))
        before = edge_count_for_pin(from_node, from_pin, "output_pins")
        try:
            graph.add_edge(from_node, from_pin, to_node, to_pin)
            after = edge_count_for_pin(from_node, from_pin, "output_pins")
            if after <= before:
                edge_errors.append({
                    "edge": edge_spec,
                    "error": "Graph add_edge did not create a new source-pin edge",
                    "from_pin_edge_count_before": before,
                    "from_pin_edge_count_after": after,
                })
            else:
                connected_edges.append({"from": from_id, "from_pin": from_pin, "to": to_id, "to_pin": to_pin})
        except Exception as exc:
            edge_errors.append({"edge": edge_spec, "error": str(exc)})

    if save_graph:
        unreal.EditorAssetLibrary.save_loaded_asset(graph)

    dependencies = graph_dependencies(package_path)
    forbidden_hits = [
        dependency
        for dependency in dependencies
        for prefix in forbidden_prefixes
        if str(dependency).startswith(str(prefix))
    ]
    RESULT = {
        "success": not setting_errors and not spawner_errors and not edge_errors and not forbidden_hits,
        "asset_path": package_path,
        "object_path": graph.get_path_name(),
        "saved": bool(save_graph),
        "created_nodes": created_nodes,
        "connected_edges": connected_edges,
        "setting_errors": setting_errors,
        "spawner_errors": spawner_errors,
        "edge_errors": edge_errors,
        "dependencies": dependencies,
        "forbidden_dependency_prefixes": forbidden_prefixes,
        "forbidden_dependency_hits": forbidden_hits,
    }
""".replace("__SPEC_JSON__", repr(spec_json))
        code = code.replace("__OVERWRITE_EXISTING__", repr(bool(overwrite_existing)))
        code = code.replace("__ALLOW_OVERWRITE_NON_TEMP__", repr(bool(allow_overwrite_non_temp)))
        code = code.replace("__SAVE_GRAPH__", repr(bool(save)))
        code = code.replace("__DRY_RUN__", repr(bool(dry_run)))
        return _run_unreal_python_json(code)

    @mcp.tool()
    def audit_pcg_graph_contract(
        ctx: Context,
        graph_path: str,
        include_dependencies: bool = True,
        forbidden_dependency_prefixes: List[str] | None = None,
        fail_on_forbidden_dependencies: bool = True,
    ) -> Dict[str, Any]:
        """
        Read-only PCG graph contract audit.

        Reports node titles/classes, pins, edge endpoints, static mesh spawner
        selectors, actor tag selectors, dependencies, and forbidden dependency
        prefix hits.
        """
        if forbidden_dependency_prefixes is None:
            forbidden_dependency_prefixes = []
        code = """
import json
import unreal

graph_path = __GRAPH_PATH__
include_dependencies = __INCLUDE_DEPENDENCIES__
forbidden_prefixes = json.loads(__FORBIDDEN_PREFIXES__)
fail_on_forbidden = __FAIL_ON_FORBIDDEN__

def normalize_package_path(path):
    text = str(path).strip()
    if "." in text and text.startswith("/Game/"):
        text = text.split(".", 1)[0]
    return text.rstrip("/")

def load_graph(path):
    package_path = normalize_package_path(path)
    graph = unreal.load_asset(path)
    if not graph and package_path:
        graph = unreal.load_asset(package_path)
    if not graph:
        raise RuntimeError("Could not load PCG graph: " + str(path))
    if "PCGGraph" not in graph.get_class().get_name():
        raise RuntimeError("Asset is not a PCG graph: " + graph.get_path_name())
    return graph, package_path or normalize_package_path(graph.get_path_name())

def pin_label(pin):
    props = pin.get_editor_property("properties")
    return str(props.get_editor_property("label"))

def pin_key(pin):
    return pin.get_path_name()

def collect_pin_rows(node, pin_key_name):
    rows = []
    for pin in node.get_editor_property(pin_key_name):
        rows.append({
            "label": pin_label(pin),
            "pin_name": pin.get_name(),
            "pin_path": pin.get_path_name(),
            "edge_count": len(pin.get_editor_property("edges")),
        })
    return rows

def node_title(node):
    value = node.get_editor_property("node_title")
    return str(value) if value else ""

def node_identity(node):
    title = node_title(node)
    return title or node.get_name()

def graph_dependencies(package_path):
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    try:
        options = unreal.AssetRegistryDependencyOptions(
            include_soft_package_references=True,
            include_hard_package_references=True,
            include_searchable_names=False,
            include_soft_management_references=False,
            include_hard_management_references=False,
        )
        return [str(item) for item in registry.get_dependencies(package_path, options)]
    except TypeError:
        return [str(item) for item in registry.get_dependencies(package_path)]

def read_spawner(settings_obj):
    info = {}
    if settings_obj.get_class().get_name() != "PCGStaticMeshSpawnerSettings":
        return info
    selector = settings_obj.get_editor_property("mesh_selector_parameters")
    info["selector_class"] = selector.get_class().get_name()
    try:
        info["attribute_name"] = str(selector.get_editor_property("attribute_name"))
    except Exception:
        pass
    try:
        info["material_override_attributes"] = [
            str(item) for item in selector.get_editor_property("material_override_attributes")
        ]
    except Exception:
        pass
    entries = []
    try:
        for entry in selector.get_editor_property("mesh_entries"):
            descriptor = entry.get_editor_property("descriptor")
            mesh = descriptor.get_editor_property("static_mesh")
            entries.append({
                "mesh": mesh.get_path_name() if mesh else None,
                "weight": entry.get_editor_property("weight"),
            })
    except Exception:
        pass
    info["mesh_entries"] = entries
    return info

def read_actor_selector(settings_obj):
    info = {}
    try:
        selector = settings_obj.get_editor_property("actor_selector")
    except Exception:
        return info
    for property_name in [
        "actor_filter",
        "actor_selection",
        "actor_selection_tag",
        "must_overlap_self",
        "include_children",
        "component_selection",
        "component_selection_tag",
    ]:
        try:
            info[property_name] = str(selector.get_editor_property(property_name))
        except Exception:
            pass
    return info

graph, package_path = load_graph(graph_path)
node_by_pin_path = {}
pin_label_by_path = {}
pin_direction_by_path = {}
for node in list(graph.get_editor_property("nodes")) + [graph.get_input_node(), graph.get_output_node()]:
    for pin in node.get_editor_property("input_pins"):
        key = pin_key(pin)
        node_by_pin_path[key] = node_identity(node)
        pin_label_by_path[key] = pin_label(pin)
        pin_direction_by_path[key] = "input"
    for pin in node.get_editor_property("output_pins"):
        key = pin_key(pin)
        node_by_pin_path[key] = node_identity(node)
        pin_label_by_path[key] = pin_label(pin)
        pin_direction_by_path[key] = "output"

edges = {}
for node in list(graph.get_editor_property("nodes")) + [graph.get_input_node(), graph.get_output_node()]:
    for direction, pin_key_name in [("output", "output_pins"), ("input", "input_pins")]:
        for pin in node.get_editor_property(pin_key_name):
            for edge in pin.get_editor_property("edges"):
                edge_path = edge.get_path_name()
                row = edges.setdefault(edge_path, {"edge_path": edge_path})
                row[direction + "_node"] = node_identity(node)
                row[direction + "_pin"] = pin_label(pin)

nodes = []
for node in graph.get_editor_property("nodes"):
    settings_obj = node.get_settings()
    nodes.append({
        "node_name": node.get_name(),
        "title": node_title(node),
        "settings_class": settings_obj.get_class().get_name() if settings_obj else None,
        "position": list(node.get_node_position()),
        "input_pins": collect_pin_rows(node, "input_pins"),
        "output_pins": collect_pin_rows(node, "output_pins"),
        "spawner": read_spawner(settings_obj) if settings_obj else {},
        "actor_selector": read_actor_selector(settings_obj) if settings_obj else {},
    })

dependencies = graph_dependencies(package_path) if include_dependencies else []
forbidden_hits = [
    dependency
    for dependency in dependencies
    for prefix in forbidden_prefixes
    if str(dependency).startswith(str(prefix))
]
RESULT = {
    "success": not (fail_on_forbidden and forbidden_hits),
    "graph_path": package_path,
    "object_path": graph.get_path_name(),
    "node_count": len(nodes),
    "edge_count": len(edges),
    "nodes": nodes,
    "edges": list(edges.values()),
    "dependencies": dependencies,
    "forbidden_dependency_prefixes": forbidden_prefixes,
    "forbidden_dependency_hits": forbidden_hits,
}
"""
        code = code.replace("__GRAPH_PATH__", repr(graph_path))
        code = code.replace("__INCLUDE_DEPENDENCIES__", repr(bool(include_dependencies)))
        code = code.replace("__FORBIDDEN_PREFIXES__", repr(json.dumps(forbidden_dependency_prefixes, ensure_ascii=False)))
        code = code.replace("__FAIL_ON_FORBIDDEN__", repr(bool(fail_on_forbidden_dependencies)))
        return _run_unreal_python_json(code)

    @mcp.tool()
    def validate_pcg_source_independence(
        ctx: Context,
        graph_path: str,
        forbidden_dependency_prefixes: List[str] | None = None,
        allowed_dependency_prefixes: List[str] | None = None,
    ) -> Dict[str, Any]:
        """
        Validate that a PCG graph avoids forbidden source dependencies.

        This is a focused wrapper around audit_pcg_graph_contract for promoted
        source-independent rebuilds. By default it forbids PCGStudy references.
        """
        if forbidden_dependency_prefixes is None:
            forbidden_dependency_prefixes = ["/Game/Cubeless/PCG/PCGStudy"]
        if allowed_dependency_prefixes is None:
            allowed_dependency_prefixes = ["/Script/PCG", "/Game/DreamscapeSeries"]

        audit = audit_pcg_graph_contract(
            ctx,
            graph_path=graph_path,
            include_dependencies=True,
            forbidden_dependency_prefixes=forbidden_dependency_prefixes,
            fail_on_forbidden_dependencies=True,
        )
        if not audit.get("success") and "forbidden_dependency_hits" not in audit:
            return audit

        dependencies = audit.get("dependencies", [])
        allowed_misses = [
            dependency
            for dependency in dependencies
            if not any(str(dependency).startswith(prefix) for prefix in allowed_dependency_prefixes)
        ]
        forbidden_hits = audit.get("forbidden_dependency_hits", [])
        return {
            "success": not forbidden_hits,
            "graph_path": audit.get("graph_path", graph_path),
            "node_count": audit.get("node_count", 0),
            "edge_count": audit.get("edge_count", 0),
            "dependency_count": len(dependencies),
            "dependencies": dependencies,
            "forbidden_dependency_prefixes": forbidden_dependency_prefixes,
            "forbidden_dependency_hits": forbidden_hits,
            "allowed_dependency_prefixes": allowed_dependency_prefixes,
            "dependencies_outside_allowed_prefixes": allowed_misses,
            "audit": audit,
        }

    @mcp.tool()
    def set_pcg_static_mesh_spawner_entries(
        ctx: Context,
        graph_path: str,
        node_id: str,
        mesh_entries: List[Dict[str, Any]] | None = None,
        selector_type: str = "weighted",
        attribute_name: str = "Meshes",
        material_override_attributes: List[str] | None = None,
        save: bool = True,
    ) -> Dict[str, Any]:
        """
        Configure a Static Mesh Spawner selector on one PCG graph node.

        This is a focused helper for the most common PCGStudy rebuild step:
        swapping source meshes for replacement meshes such as Dreamscape assets.
        Use selector_type="by_attribute" for the PCGStudy-compatible Meshes /
        Override Materials attribute contract.
        """
        mesh_entries = mesh_entries or []
        if selector_type not in {"weighted", "by_attribute", "attribute"}:
            return {"success": False, "message": "selector_type must be weighted or by_attribute"}
        if selector_type == "weighted" and not mesh_entries:
            return {"success": False, "message": "mesh_entries must not be empty for weighted selector"}
        if material_override_attributes is None:
            material_override_attributes = []

        code = """
import json
import unreal

graph_path = __GRAPH_PATH__
node_id = __NODE_ID__
mesh_entries = json.loads(__MESH_ENTRIES__)
selector_type = __SELECTOR_TYPE__
attribute_name = __ATTRIBUTE_NAME__
material_override_attributes = json.loads(__MATERIAL_OVERRIDE_ATTRIBUTES__)
save_graph = __SAVE_GRAPH__

def normalize_package_path(path):
    text = str(path).strip()
    if "." in text and text.startswith("/Game/"):
        text = text.split(".", 1)[0]
    return text.rstrip("/")

def load_graph(path):
    package_path = normalize_package_path(path)
    graph = unreal.load_asset(path) or unreal.load_asset(package_path)
    if not graph:
        raise RuntimeError("Could not load PCG graph: " + str(path))
    if "PCGGraph" not in graph.get_class().get_name():
        raise RuntimeError("Asset is not a PCG graph: " + graph.get_path_name())
    return graph

def node_title(node):
    value = node.get_editor_property("node_title")
    return str(value) if value else ""

def find_node(graph, identifier):
    matches = []
    for node in graph.get_editor_property("nodes"):
        settings = node.get_settings()
        keys = {
            node.get_name(),
            node.get_path_name(),
            node_title(node),
        }
        if settings:
            keys.add(settings.get_name())
            keys.add(settings.get_path_name())
        if str(identifier) in keys:
            matches.append(node)
    if not matches:
        raise RuntimeError("No PCG node matched node_id: " + str(identifier))
    if len(matches) > 1:
        raise RuntimeError("Multiple PCG nodes matched node_id: " + str(identifier))
    return matches[0]

def load_static_mesh(path):
    mesh = unreal.load_asset(str(path))
    if not mesh:
        raise RuntimeError("Could not load static mesh: " + str(path))
    if mesh.get_class().get_name() != "StaticMesh":
        raise RuntimeError("Asset is not a StaticMesh: " + str(path))
    return mesh

def build_entry(entry_spec):
    mesh_path = entry_spec.get("mesh") or entry_spec.get("static_mesh") or entry_spec.get("path")
    mesh = load_static_mesh(mesh_path)
    descriptor = unreal.PCGSoftISMComponentDescriptor()
    descriptor.set_editor_property("static_mesh", mesh)
    if "cast_shadow" in entry_spec:
        descriptor.set_editor_property("cast_shadow", bool(entry_spec["cast_shadow"]))
    if "receives_decals" in entry_spec:
        descriptor.set_editor_property("receives_decals", bool(entry_spec["receives_decals"]))
    if "override_materials" in entry_spec:
        materials = []
        for material_path in entry_spec.get("override_materials") or []:
            material = unreal.load_asset(str(material_path))
            if not material:
                raise RuntimeError("Could not load override material: " + str(material_path))
            materials.append(material)
        descriptor.set_editor_property("override_materials", materials)
    entry = unreal.PCGMeshSelectorWeightedEntry()
    entry.set_editor_property("descriptor", descriptor)
    entry.set_editor_property("weight", int(entry_spec.get("weight", 1)))
    return entry

graph = load_graph(graph_path)
node = find_node(graph, node_id)
settings = node.get_settings()
if not settings or settings.get_class().get_name() != "PCGStaticMeshSpawnerSettings":
    raise RuntimeError("Matched node is not PCGStaticMeshSpawnerSettings: " + node.get_name())

selector_mode = "weighted"
if selector_type in ("by_attribute", "attribute"):
    selector_mode = "by_attribute"
    try:
        settings.set_mesh_selector_type(unreal.PCGMeshSelectorByAttribute)
    except Exception:
        pass
    selector = settings.get_editor_property("mesh_selector_parameters")
    selector.set_editor_property("attribute_name", unreal.Name(str(attribute_name or "Meshes")))
    override_names = [unreal.Name(str(item)) for item in material_override_attributes]
    selector.set_editor_property("material_override_attributes", override_names)
    selector.set_editor_property("use_attribute_material_overrides", bool(override_names))
else:
    try:
        settings.set_mesh_selector_type(unreal.PCGMeshSelectorWeighted)
    except Exception:
        pass
    selector = settings.get_editor_property("mesh_selector_parameters")
    entries = [build_entry(entry_spec) for entry_spec in mesh_entries]
    selector.set_editor_property("mesh_entries", entries)
if save_graph:
    unreal.EditorAssetLibrary.save_loaded_asset(graph)

readback = []
attribute_readback = {}
if selector_mode == "weighted":
    for entry in selector.get_editor_property("mesh_entries"):
        descriptor = entry.get_editor_property("descriptor")
        mesh = descriptor.get_editor_property("static_mesh")
        readback.append({
            "mesh": mesh.get_path_name() if mesh else None,
            "weight": entry.get_editor_property("weight"),
        })
else:
    attribute_readback = {
        "attribute_name": str(selector.get_editor_property("attribute_name")),
        "material_override_attributes": [
            str(item) for item in selector.get_editor_property("material_override_attributes")
        ],
        "use_attribute_material_overrides": bool(selector.get_editor_property("use_attribute_material_overrides")),
    }

RESULT = {
    "success": True,
    "graph_path": normalize_package_path(graph_path),
    "node": node.get_name(),
    "title": node_title(node),
    "selector_mode": selector_mode,
    "saved": bool(save_graph),
    "mesh_entry_count": len(readback),
    "mesh_entries": readback,
    "attribute_selector": attribute_readback,
}
"""
        code = code.replace("__GRAPH_PATH__", repr(graph_path))
        code = code.replace("__NODE_ID__", repr(node_id))
        code = code.replace("__MESH_ENTRIES__", repr(json.dumps(mesh_entries, ensure_ascii=False)))
        code = code.replace("__SELECTOR_TYPE__", repr(selector_type))
        code = code.replace("__ATTRIBUTE_NAME__", repr(attribute_name))
        code = code.replace("__MATERIAL_OVERRIDE_ATTRIBUTES__", repr(json.dumps(material_override_attributes, ensure_ascii=False)))
        code = code.replace("__SAVE_GRAPH__", repr(bool(save)))
        return _run_unreal_python_json(code)

    @mcp.tool()
    def read_pcg_node_contract(
        ctx: Context,
        graph_path: str,
        node_id: str = "",
        include_dependencies: bool = False,
    ) -> Dict[str, Any]:
        """
        Read selected PCG node contract data from a graph.

        This is a stable readback helper for node title, settings class,
        position, pins, spawner selector state, and actor selector state. If
        node_id is empty, all authored nodes are returned.
        """
        audit = audit_pcg_graph_contract(
            ctx,
            graph_path=graph_path,
            include_dependencies=include_dependencies,
            forbidden_dependency_prefixes=[],
            fail_on_forbidden_dependencies=False,
        )
        if not audit.get("success"):
            return audit

        nodes = audit.get("nodes", [])
        if node_id:
            needle = str(node_id).lower()
            nodes = [
                node
                for node in nodes
                if needle
                in {
                    str(node.get("node_name", "")).lower(),
                    str(node.get("title", "")).lower(),
                    str(node.get("settings_class", "")).lower(),
                }
            ]
            if not nodes:
                return {
                    "success": False,
                    "message": f"No PCG node matched node_id: {node_id}",
                    "graph_path": audit.get("graph_path", graph_path),
                    "available_nodes": [
                        {
                            "node_name": node.get("node_name"),
                            "title": node.get("title"),
                            "settings_class": node.get("settings_class"),
                        }
                        for node in audit.get("nodes", [])
                    ],
                }

        return {
            "success": True,
            "graph_path": audit.get("graph_path", graph_path),
            "node_id": node_id,
            "node_count": len(nodes),
            "nodes": nodes,
            "dependencies": audit.get("dependencies", []) if include_dependencies else [],
        }

    @mcp.tool()
    def promote_pcg_temp_graph(
        ctx: Context,
        source_graph_path: str,
        target_graph_path: str,
        forbidden_dependency_prefixes: List[str] | None = None,
        allowed_dependency_prefixes: List[str] | None = None,
        overwrite_existing: bool = False,
        allow_non_temp_source: bool = False,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Promote a validated temp PCG graph into a permanent content path.

        Defaults to dry-run and refuses non-temp sources unless explicitly
        allowed. No map switching or level mutation is performed.
        """
        if forbidden_dependency_prefixes is None:
            forbidden_dependency_prefixes = ["/Game/Cubeless/PCG/PCGStudy"]
        if allowed_dependency_prefixes is None:
            allowed_dependency_prefixes = ["/Script/PCG", "/Game/DreamscapeSeries"]

        validation = validate_pcg_source_independence(
            ctx,
            graph_path=source_graph_path,
            forbidden_dependency_prefixes=forbidden_dependency_prefixes,
            allowed_dependency_prefixes=allowed_dependency_prefixes,
        )
        if not validation.get("success"):
            return {
                "success": False,
                "message": "Source graph failed source-independence validation",
                "validation": validation,
            }

        code = """
import json
import unreal

source_graph_path = __SOURCE_GRAPH_PATH__
target_graph_path = __TARGET_GRAPH_PATH__
overwrite_existing = __OVERWRITE_EXISTING__
allow_non_temp_source = __ALLOW_NON_TEMP_SOURCE__
dry_run = __DRY_RUN__
validation = json.loads(__VALIDATION_JSON__)

def normalize_package_path(path):
    text = str(path).strip()
    if "." in text and text.startswith("/Game/"):
        text = text.split(".", 1)[0]
    return text.rstrip("/")

def split_asset_path(path):
    package_path = normalize_package_path(path)
    if not package_path.startswith("/Game/"):
        raise RuntimeError("target/source path must be a /Game package path")
    parent, _, asset_name = package_path.rpartition("/")
    if not parent or not asset_name:
        raise RuntimeError("Path must include a parent folder and asset name: " + package_path)
    return parent, asset_name, package_path

source_package = normalize_package_path(source_graph_path)
target_parent, target_name, target_package = split_asset_path(target_graph_path)
if not allow_non_temp_source and not source_package.startswith("/Game/_MCP_Temp/"):
    raise RuntimeError("Refusing to promote non-temp source without allow_non_temp_source=True: " + source_package)
if target_package.startswith("/Game/_MCP_Temp/"):
    raise RuntimeError("Promotion target must not be under /Game/_MCP_Temp: " + target_package)

source_graph = unreal.load_asset(source_graph_path) or unreal.load_asset(source_package)
if not source_graph:
    raise RuntimeError("Could not load source graph: " + source_graph_path)
if "PCGGraph" not in source_graph.get_class().get_name():
    raise RuntimeError("Source asset is not a PCG graph: " + source_graph.get_path_name())

exists = unreal.EditorAssetLibrary.does_asset_exist(target_package)
if dry_run:
    RESULT = {
        "success": True,
        "dry_run": True,
        "source_graph_path": source_package,
        "target_graph_path": target_package,
        "target_exists": bool(exists),
        "would_overwrite": bool(exists and overwrite_existing),
        "validation": validation,
    }
else:
    unreal.EditorAssetLibrary.make_directory(target_parent)
    if exists:
        if not overwrite_existing:
            raise RuntimeError("Target graph already exists: " + target_package)
        if not unreal.EditorAssetLibrary.delete_asset(target_package):
            raise RuntimeError("Failed to delete existing target graph: " + target_package)
    duplicated = unreal.EditorAssetLibrary.duplicate_asset(source_package, target_package)
    if not duplicated:
        raise RuntimeError("Duplicate failed from " + source_package + " to " + target_package)
    unreal.EditorAssetLibrary.save_loaded_asset(duplicated)
    RESULT = {
        "success": True,
        "dry_run": False,
        "source_graph_path": source_package,
        "target_graph_path": target_package,
        "object_path": duplicated.get_path_name(),
        "overwrote_existing": bool(exists),
        "validation": validation,
    }
"""
        code = code.replace("__SOURCE_GRAPH_PATH__", repr(source_graph_path))
        code = code.replace("__TARGET_GRAPH_PATH__", repr(target_graph_path))
        code = code.replace("__OVERWRITE_EXISTING__", repr(bool(overwrite_existing)))
        code = code.replace("__ALLOW_NON_TEMP_SOURCE__", repr(bool(allow_non_temp_source)))
        code = code.replace("__DRY_RUN__", repr(bool(dry_run)))
        code = code.replace("__VALIDATION_JSON__", repr(json.dumps(validation, ensure_ascii=False)))
        return _run_unreal_python_json(code)

    @mcp.tool()
    def pcg_actor_smoke_test(
        ctx: Context,
        graph_path: str,
        actor_label: str = "",
        selected_only: bool = False,
        cleanup: bool = True,
        generate: bool = True,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Smoke-test a PCG graph against existing PCG components in the current level.

        The default dry-run only audits the graph and reports matching existing
        actors/components. With dry_run=False it runs cleanup/generate on matching
        PCG components. This tool does not switch maps and does not create actors.
        """
        audit = audit_pcg_graph_contract(
            ctx,
            graph_path=graph_path,
            include_dependencies=True,
            forbidden_dependency_prefixes=[],
            fail_on_forbidden_dependencies=False,
        )
        if not audit.get("success"):
            return audit

        code = """
import json
import unreal

graph_path = __GRAPH_PATH__
actor_label = __ACTOR_LABEL__
selected_only = __SELECTED_ONLY__
cleanup = __CLEANUP__
generate = __GENERATE__
dry_run = __DRY_RUN__
audit = json.loads(__AUDIT_JSON__)

def normalize_package_path(path):
    text = str(path).strip()
    if "." in text and text.startswith("/Game/"):
        text = text.split(".", 1)[0]
    return text.rstrip("/")

graph_package = normalize_package_path(graph_path)
graph = unreal.load_asset(graph_path) or unreal.load_asset(graph_package)
if not graph:
    raise RuntimeError("Could not load PCG graph: " + str(graph_path))

editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = editor_actor_subsystem.get_selected_level_actors() if selected_only else editor_actor_subsystem.get_all_level_actors()
matches = []
for actor in actors:
    label = actor.get_actor_label()
    path = actor.get_path_name()
    if actor_label and actor_label not in label and actor_label not in path:
        continue
    components = []
    for component in actor.get_components_by_class(unreal.ActorComponent):
        class_name = component.get_class().get_name()
        if "PCG" not in class_name:
            continue
        component_graph = None
        for prop_name in ["graph", "Graph"]:
            try:
                component_graph = component.get_editor_property(prop_name)
                break
            except Exception:
                pass
        graph_matches = False
        if component_graph:
            graph_matches = normalize_package_path(component_graph.get_path_name()) == graph_package
        if not graph_matches:
            continue
        components.append({
            "component": component.get_name(),
            "component_class": class_name,
            "component_path": component.get_path_name(),
            "graph_matches": graph_matches,
        })
    if components:
        matches.append({
            "actor": label,
            "actor_path": path,
            "components": components,
        })

if dry_run:
    RESULT = {
        "success": True,
        "dry_run": True,
        "graph_path": graph_package,
        "matching_actor_count": len(matches),
        "matching_component_count": sum(len(item["components"]) for item in matches),
        "matches": matches,
        "audit": audit,
        "note": "dry_run=True; no PCG component cleanup/generate was executed",
    }
else:
    if not matches:
        raise RuntimeError("No existing PCG component in the current level references graph: " + graph_package)
    processed = []
    errors = []
    for match in matches:
        actor = unreal.load_object(None, match["actor_path"])
        if not actor:
            errors.append({"actor_path": match["actor_path"], "error": "Actor could not be reloaded"})
            continue
        for component_row in match["components"]:
            component = unreal.load_object(None, component_row["component_path"])
            if not component:
                errors.append({"component_path": component_row["component_path"], "error": "Component could not be reloaded"})
                continue
            called = []
            for method_name in (["cleanup"] if cleanup else []) + (["generate"] if generate else []):
                method = getattr(component, method_name, None)
                if not method:
                    continue
                try:
                    method()
                    called.append(method_name)
                except Exception as exc:
                    errors.append({
                        "actor": match["actor"],
                        "component": component_row["component"],
                        "method": method_name,
                        "error": str(exc),
                    })
            processed.append({
                "actor": match["actor"],
                "component": component_row["component"],
                "called_methods": called,
            })
    RESULT = {
        "success": len(errors) == 0,
        "dry_run": False,
        "graph_path": graph_package,
        "processed_count": len(processed),
        "processed": processed,
        "errors": errors,
        "audit": audit,
    }
"""
        code = code.replace("__GRAPH_PATH__", repr(graph_path))
        code = code.replace("__ACTOR_LABEL__", repr(actor_label))
        code = code.replace("__SELECTED_ONLY__", repr(bool(selected_only)))
        code = code.replace("__CLEANUP__", repr(bool(cleanup)))
        code = code.replace("__GENERATE__", repr(bool(generate)))
        code = code.replace("__DRY_RUN__", repr(bool(dry_run)))
        code = code.replace("__AUDIT_JSON__", repr(json.dumps(audit, ensure_ascii=False)))
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
