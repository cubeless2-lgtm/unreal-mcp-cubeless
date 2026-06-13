"""Unreal-side helpers for AI texture generation tools."""

import json
import os
import struct
import tempfile
import textwrap
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


Color = Tuple[int, int, int, int]


def run_unreal_python_json(
    code_body: str,
    result_name: str = "texture_tools",
    defer_to_ticker: bool = False,
) -> Dict[str, Any]:
    """Run Unreal Python code that writes a RESULT object to a temp JSON file."""
    from unreal_mcp_server import get_unreal_connection

    safe_name = "".join(ch if ch.isalnum() or ch in ("_", "-") else "_" for ch in result_name)
    result_path = os.path.join(tempfile.gettempdir(), f"unreal_mcp_{safe_name}_result.json")
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
    RESULT = {{"success": False, "message": str(exc), "traceback": traceback.format_exc()}}
with open(RESULT_PATH, "w", encoding="utf-8") as result_file:
    json.dump(RESULT, result_file, ensure_ascii=False, indent=2, default=str)
"""

    unreal = get_unreal_connection()
    if not unreal:
        return {"success": False, "message": "Failed to connect to Unreal Engine"}

    response = unreal.send_command(
        "execute_python",
        {"code": wrapped_code, "mode": "ExecuteFile", "defer_to_ticker": defer_to_ticker},
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


def _png_chunk(tag: bytes, data: bytes) -> bytes:
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)


def _write_png_rgba(path: str, width: int, height: int, pixels: bytearray) -> None:
    raw = bytearray()
    stride = width * 4
    for y in range(height):
        raw.append(0)
        row_start = y * stride
        raw.extend(pixels[row_start : row_start + stride])

    png = bytearray()
    png.extend(b"\x89PNG\r\n\x1a\n")
    png.extend(_png_chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)))
    png.extend(_png_chunk(b"IDAT", zlib.compress(bytes(raw), 9)))
    png.extend(_png_chunk(b"IEND", b""))

    with open(path, "wb") as png_file:
        png_file.write(png)


def _set_pixel(pixels: bytearray, width: int, height: int, x: int, y: int, color: Color) -> None:
    if x < 0 or y < 0 or x >= width or y >= height:
        return
    idx = (y * width + x) * 4
    pixels[idx : idx + 4] = bytes(color)


def _draw_line(
    pixels: bytearray,
    width: int,
    height: int,
    start: Tuple[int, int],
    end: Tuple[int, int],
    color: Color,
    thickness: int = 2,
) -> None:
    x0, y0 = start
    x1, y1 = end
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    radius = max(0, thickness // 2)

    while True:
        for ox in range(-radius, radius + 1):
            for oy in range(-radius, radius + 1):
                _set_pixel(pixels, width, height, x0 + ox, y0 + oy, color)
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy


def _uv_to_pixel(uv: Sequence[float], size: int, padding: int) -> Tuple[int, int]:
    drawable = max(1, size - padding * 2 - 1)
    u = max(0.0, min(1.0, float(uv[0])))
    v = max(0.0, min(1.0, float(uv[1])))
    x = int(round(padding + u * drawable))
    y = int(round(padding + (1.0 - v) * drawable))
    return x, y


def render_uv_layout_png(
    polygons: List[List[List[float]]],
    output_path: str,
    image_size: int = 1024,
    transparent: bool = True,
) -> Dict[str, Any]:
    """Render UV polygon edges into a PNG using only the standard library."""
    output = Path(output_path).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    size = max(128, min(4096, int(image_size)))
    background: Color = (0, 0, 0, 0) if transparent else (0, 0, 0, 255)
    line_color: Color = (255, 255, 255, 255)
    pixels = bytearray(background * (size * size))
    padding = max(4, size // 128)
    segment_count = 0

    for polygon in polygons:
        if len(polygon) < 2:
            continue
        points = [_uv_to_pixel(uv, size, padding) for uv in polygon]
        for index, point in enumerate(points):
            next_point = points[(index + 1) % len(points)]
            _draw_line(pixels, size, size, point, next_point, line_color, thickness=max(1, size // 512))
            segment_count += 1

    _write_png_rgba(str(output), size, size, pixels)
    return {
        "success": True,
        "output_path": str(output),
        "image_size": size,
        "polygon_count": len(polygons),
        "line_segment_count": segment_count,
        "transparent": transparent,
    }


def get_static_mesh_uv_data(mesh_path: str, uv_channel: int = 0) -> Dict[str, Any]:
    """Read UV polygon data for a Static Mesh through Unreal Python."""
    code = f"""
import unreal

mesh_path = {mesh_path!r}
uv_channel = int({uv_channel!r})
mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
if not mesh:
    RESULT = {{"success": False, "message": f"Static Mesh not found: {{mesh_path}}"}}
else:
    class_name = mesh.get_class().get_name()
    if class_name != "StaticMesh":
        RESULT = {{"success": False, "message": f"Asset is not a StaticMesh: {{mesh_path}}", "class_name": class_name}}
    else:
        subsystem = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        try:
            num_uv_channels = subsystem.get_num_uv_channels(mesh, 0)
        except Exception:
            num_uv_channels = unreal.EditorStaticMeshLibrary.get_num_uv_channels(mesh, 0)
        if uv_channel < 0 or uv_channel >= num_uv_channels:
            RESULT = {{
                "success": False,
                "message": f"UV channel {{uv_channel}} is out of range. Mesh has {{num_uv_channels}} UV channel(s).",
                "num_uv_channels": num_uv_channels,
            }}
        else:
            desc = mesh.get_static_mesh_description(0)
            polygons = []
            min_u = 999999.0
            min_v = 999999.0
            max_u = -999999.0
            max_v = -999999.0
            polygon_count = desc.get_polygon_count()
            for polygon_index in range(polygon_count):
                polygon_id = unreal.PolygonID(polygon_index)
                try:
                    if not desc.is_polygon_valid(polygon_id):
                        continue
                    vertex_instances = desc.get_polygon_vertex_instances(polygon_id)
                    points = []
                    for vertex_instance in vertex_instances:
                        uv = desc.get_vertex_instance_uv(vertex_instance, uv_channel)
                        u = float(uv.x)
                        v = float(uv.y)
                        min_u = min(min_u, u)
                        min_v = min(min_v, v)
                        max_u = max(max_u, u)
                        max_v = max(max_v, v)
                        points.append([u, v])
                    if len(points) >= 2:
                        polygons.append(points)
                except Exception:
                    continue
            RESULT = {{
                "success": True,
                "mesh_path": mesh_path,
                "mesh_name": mesh.get_name(),
                "uv_channel": uv_channel,
                "num_uv_channels": num_uv_channels,
                "polygon_count": len(polygons),
                "source_polygon_count": polygon_count,
                "uv_bounds": {{"min_u": min_u, "min_v": min_v, "max_u": max_u, "max_v": max_v}},
                "polygons": polygons,
            }}
"""
    return run_unreal_python_json(code, "static_mesh_uv")


def export_static_mesh_uv_layout(
    mesh_path: str,
    uv_channel: int = 0,
    output_path: Optional[str] = None,
    image_size: int = 1024,
) -> Dict[str, Any]:
    """Read a Static Mesh's UVs and render them to a PNG layout image."""
    uv_data = get_static_mesh_uv_data(mesh_path, uv_channel)
    if not uv_data.get("success"):
        return uv_data

    if not output_path:
        safe_mesh = Path(mesh_path.replace("/", "_").replace("\\", "_")).name.strip("_") or "StaticMesh"
        output_path = os.path.join(tempfile.gettempdir(), f"{safe_mesh}_UV{uv_channel}.png")

    render_result = render_uv_layout_png(uv_data.get("polygons", []), output_path, image_size=image_size)
    if not render_result.get("success"):
        return render_result

    return {
        "success": True,
        "mesh_path": uv_data.get("mesh_path"),
        "mesh_name": uv_data.get("mesh_name"),
        "uv_channel": uv_data.get("uv_channel"),
        "num_uv_channels": uv_data.get("num_uv_channels"),
        "polygon_count": uv_data.get("polygon_count"),
        "uv_bounds": uv_data.get("uv_bounds"),
        "output_path": render_result.get("output_path"),
        "image_size": render_result.get("image_size"),
        "line_segment_count": render_result.get("line_segment_count"),
    }


def import_texture_to_unreal(image_path: str, unreal_folder: str, asset_name: str) -> Dict[str, Any]:
    """Import a PNG as Texture2D into the Unreal Content Browser."""
    code = f"""
import os
import unreal

image_path = os.path.abspath({image_path!r})
unreal_folder = {unreal_folder!r}
asset_name = {asset_name!r}

if not os.path.exists(image_path):
    RESULT = {{"success": False, "message": f"Image file does not exist: {{image_path}}"}}
elif not unreal_folder.startswith("/Game"):
    RESULT = {{"success": False, "message": "unreal_folder must start with /Game"}}
else:
    unreal.EditorAssetLibrary.make_directory(unreal_folder)
    task = unreal.AssetImportTask()
    task.filename = image_path
    task.destination_path = unreal_folder
    task.destination_name = asset_name
    task.automated = True
    task.save = True
    task.replace_existing = True
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
    imported_paths = list(task.imported_object_paths)
    asset_path = imported_paths[0] if imported_paths else f"{{unreal_folder}}/{{asset_name}}"
    texture = unreal.EditorAssetLibrary.load_asset(asset_path)
    if not texture:
        RESULT = {{"success": False, "message": "Texture import did not produce a loadable asset", "asset_path": asset_path, "imported_paths": imported_paths}}
    else:
        unreal.EditorAssetLibrary.save_loaded_asset(texture)
        RESULT = {{
            "success": True,
            "asset_path": texture.get_path_name().split(".")[0],
            "object_path": texture.get_path_name(),
            "class_name": texture.get_class().get_name(),
            "imported_paths": imported_paths,
        }}
"""
    return run_unreal_python_json(code, "import_texture", defer_to_ticker=True)


def create_material_instance_with_texture(
    texture_asset_path: str,
    material_name: str,
    unreal_folder: str,
    base_material_path: str = "",
) -> Dict[str, Any]:
    """Create a Material or Material Instance that uses a texture as BaseColor."""
    code = f"""
import unreal

texture_asset_path = {texture_asset_path!r}
material_name = {material_name!r}
unreal_folder = {unreal_folder!r}
base_material_path = {base_material_path!r}

texture = unreal.EditorAssetLibrary.load_asset(texture_asset_path)
if not texture:
    RESULT = {{"success": False, "message": f"Texture asset not found: {{texture_asset_path}}"}}
elif not unreal_folder.startswith("/Game"):
    RESULT = {{"success": False, "message": "unreal_folder must start with /Game"}}
else:
    unreal.EditorAssetLibrary.make_directory(unreal_folder)
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    warnings = []
    if base_material_path:
        base_material = unreal.EditorAssetLibrary.load_asset(base_material_path)
        if not base_material:
            RESULT = {{"success": False, "message": f"Base material not found: {{base_material_path}}"}}
        else:
            factory = unreal.MaterialInstanceConstantFactoryNew()
            material_asset = asset_tools.create_asset(material_name, unreal_folder, unreal.MaterialInstanceConstant, factory)
            unreal.MaterialEditingLibrary.set_material_instance_parent(material_asset, base_material)
            applied_parameters = []
            for parameter_name in ["BaseColor", "Base Color", "BaseColorTexture", "Base_Color", "Albedo", "Diffuse", "Texture"]:
                try:
                    unreal.MaterialEditingLibrary.set_material_instance_texture_parameter_value(material_asset, parameter_name, texture)
                    applied_parameters.append(parameter_name)
                except Exception:
                    pass
            if not applied_parameters:
                warnings.append("Created the material instance but did not find a matching texture parameter on the base material.")
            unreal.MaterialEditingLibrary.update_material_instance(material_asset)
            unreal.EditorAssetLibrary.save_loaded_asset(material_asset)
            RESULT = {{
                "success": True,
                "asset_path": material_asset.get_path_name().split(".")[0],
                "object_path": material_asset.get_path_name(),
                "class_name": material_asset.get_class().get_name(),
                "base_material_path": base_material_path,
                "applied_parameters": applied_parameters,
                "warnings": warnings,
            }}
    else:
        factory = unreal.MaterialFactoryNew()
        material_asset = asset_tools.create_asset(material_name, unreal_folder, unreal.Material, factory)
        try:
            texture_sample = unreal.MaterialEditingLibrary.create_material_expression(
                material_asset,
                unreal.MaterialExpressionTextureSample,
                -384,
                0,
            )
            texture_sample.set_editor_property("texture", texture)
            unreal.MaterialEditingLibrary.connect_material_property(
                texture_sample,
                "",
                unreal.MaterialProperty.MP_BASE_COLOR,
            )
            unreal.MaterialEditingLibrary.recompile_material(material_asset)
            unreal.EditorAssetLibrary.save_loaded_asset(material_asset)
            RESULT = {{
                "success": True,
                "asset_path": material_asset.get_path_name().split(".")[0],
                "object_path": material_asset.get_path_name(),
                "class_name": material_asset.get_class().get_name(),
                "base_material_path": "",
                "warnings": warnings,
            }}
        except Exception as exc:
            unreal.EditorAssetLibrary.save_loaded_asset(material_asset)
            RESULT = {{
                "success": False,
                "message": f"Material asset was created but BaseColor hookup failed: {{exc}}",
                "asset_path": material_asset.get_path_name().split(".")[0],
            }}
"""
    return run_unreal_python_json(code, "create_material")


def apply_material_to_mesh(target: str, material_asset_path: str, material_slot: int = 0) -> Dict[str, Any]:
    """Apply a material to selected StaticMesh actors, a named actor, or a StaticMesh asset."""
    code = f"""
import unreal

target = {target!r}
material_asset_path = {material_asset_path!r}
material_slot = int({material_slot!r})
material = unreal.EditorAssetLibrary.load_asset(material_asset_path)

if not material:
    RESULT = {{"success": False, "message": f"Material asset not found: {{material_asset_path}}"}}
else:
    editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    actors = []
    target_asset = None
    if target == "selected":
        actors = list(editor_actor_subsystem.get_selected_level_actors())
        if not actors:
            RESULT = {{"success": False, "message": "No selected actors. Select a Static Mesh actor or pass an actor name/path."}}
        else:
            RESULT = None
    else:
        target_asset = unreal.EditorAssetLibrary.load_asset(target)
        if target_asset and target_asset.get_class().get_name() == "StaticMesh":
            RESULT = None
        else:
            all_actors = editor_actor_subsystem.get_all_level_actors()
            for actor in all_actors:
                if target in actor.get_actor_label() or target in actor.get_path_name() or target == actor.get_name():
                    actors.append(actor)
            if not actors:
                RESULT = {{"success": False, "message": f"No actor or StaticMesh asset matched target: {{target}}"}}

    if RESULT is None:
        applied = []
        if target_asset and target_asset.get_class().get_name() == "StaticMesh":
            target_asset.set_material(material_slot, material)
            unreal.EditorAssetLibrary.save_loaded_asset(target_asset)
            applied.append({{
                "target": target_asset.get_path_name(),
                "type": "StaticMesh",
                "slot": material_slot,
            }})
        for actor in actors:
            components = actor.get_components_by_class(unreal.StaticMeshComponent)
            for component in components:
                component.set_material(material_slot, material)
                applied.append({{
                    "target": actor.get_actor_label(),
                    "actor_path": actor.get_path_name(),
                    "component": component.get_name(),
                    "slot": material_slot,
                }})
        if not applied:
            RESULT = {{"success": False, "message": "Target did not contain a StaticMeshComponent and was not a StaticMesh asset."}}
        else:
            RESULT = {{"success": True, "applied": applied, "count": len(applied), "material_asset_path": material_asset_path}}
"""
    return run_unreal_python_json(code, "apply_material")


def resolve_target_static_mesh(target: str) -> Dict[str, Any]:
    """Resolve selected/named actor or StaticMesh asset into a mesh path for UV export."""
    code = f"""
import unreal

target = {target!r}
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
result = None
if target == "selected":
    actors = list(editor_actor_subsystem.get_selected_level_actors())
    if not actors:
        RESULT = {{"success": False, "message": "No selected actors. Select a Static Mesh actor or pass an actor name/path."}}
    else:
        target_actor = actors[0]
        components = target_actor.get_components_by_class(unreal.StaticMeshComponent)
        mesh = components[0].static_mesh if components else None
        if not mesh:
            RESULT = {{"success": False, "message": "Selected actor does not have a StaticMeshComponent with a mesh."}}
        else:
            RESULT = {{
                "success": True,
                "target": target,
                "actor": target_actor.get_actor_label(),
                "actor_path": target_actor.get_path_name(),
                "mesh_path": mesh.get_path_name().split(".")[0],
            }}
else:
    target_asset = unreal.EditorAssetLibrary.load_asset(target)
    if target_asset and target_asset.get_class().get_name() == "StaticMesh":
        RESULT = {{"success": True, "target": target, "mesh_path": target_asset.get_path_name().split(".")[0]}}
    else:
        actors = []
        for actor in editor_actor_subsystem.get_all_level_actors():
            if target in actor.get_actor_label() or target in actor.get_path_name() or target == actor.get_name():
                actors.append(actor)
        if not actors:
            RESULT = {{"success": False, "message": f"No actor or StaticMesh asset matched target: {{target}}"}}
        else:
            target_actor = actors[0]
            components = target_actor.get_components_by_class(unreal.StaticMeshComponent)
            mesh = components[0].static_mesh if components else None
            if not mesh:
                RESULT = {{"success": False, "message": f"Actor has no StaticMeshComponent with a mesh: {{target}}"}}
            else:
                RESULT = {{
                    "success": True,
                    "target": target,
                    "actor": target_actor.get_actor_label(),
                    "actor_path": target_actor.get_path_name(),
                    "mesh_path": mesh.get_path_name().split(".")[0],
                }}
"""
    return run_unreal_python_json(code, "resolve_mesh")
