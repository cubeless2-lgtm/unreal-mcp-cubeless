"""AI texture generation tools for Unreal MCP."""

import logging
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict

from mcp.server.fastmcp import Context, FastMCP

from services.unreal_texture_importer import (
    apply_material_to_mesh as unreal_apply_material_to_mesh,
    create_material_instance_with_texture as unreal_create_material_instance_with_texture,
    export_static_mesh_uv_layout,
    import_texture_to_unreal as unreal_import_texture_to_unreal,
    resolve_target_static_mesh,
)


logger = logging.getLogger("UnrealMCP")


UV_GUIDED_PROMPT_SUFFIX = (
    "Follow the provided UV layout guide. Keep meaningful details inside UV islands. "
    "Avoid visible seams across UV island borders. Generate a BaseColor/albedo game texture only; "
    "do not claim to create a complete PBR material set."
)


def _default_output_dir() -> str:
    return os.path.join(tempfile.gettempdir(), "unreal_mcp_ai_textures")


def sanitize_output_name(output_name: str) -> str:
    """Return a filesystem-friendly PNG basename without an extension."""
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", output_name.strip())
    name = name.strip("._")
    return name or "AI_Texture"


def ensure_png_path(output_dir: str, output_name: str) -> str:
    """Build an absolute PNG path and create its parent directory."""
    safe_name = sanitize_output_name(output_name)
    output_path = Path(output_dir).expanduser().resolve() / f"{safe_name}.png"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return str(output_path)


def _material_name_from_output(output_name: str) -> str:
    safe_name = sanitize_output_name(output_name)
    if safe_name.startswith("T_"):
        return "M_" + safe_name[2:]
    if safe_name.startswith("MI_") or safe_name.startswith("M_"):
        return safe_name
    return "M_" + safe_name


def _builtin_image_generation_required(
    prompt: str,
    output_path: str,
    size: str,
    reference_image_path: str = "",
) -> Dict[str, Any]:
    return {
        "success": False,
        "stage": "builtin_image_generation_required",
        "api_route_disabled": True,
        "billing_route": "none",
        "image_generation_route": "codex_builtin_image_generation",
        "message": (
            "OpenAI API-key based image generation is disabled for this project. "
            "Use Codex built-in image generation to create the PNG, then call "
            "import_texture_to_unreal/create_material_instance_with_texture/apply_material_to_mesh."
        ),
        "prompt": prompt,
        "requested_size": size,
        "expected_output_path": output_path,
        "reference_image_path": reference_image_path,
    }


def register_texture_generation_tools(mcp: FastMCP):
    """Register texture helper tools that avoid API-key image generation."""

    @mcp.tool()
    def get_static_mesh_uv_layout(
        ctx: Context,
        mesh_path: str,
        uv_channel: int = 0,
        output_path: str = "",
    ) -> Dict[str, Any]:
        """
        Export a Static Mesh UV layout as a PNG.

        Args:
            mesh_path: Static Mesh asset path, for example /Game/Meshes/SM_Rock.
            uv_channel: UV channel index to export.
            output_path: Optional PNG output path. Defaults to the temp directory.
        """
        try:
            return export_static_mesh_uv_layout(mesh_path, uv_channel, output_path or None)
        except Exception as exc:
            logger.exception("Failed to export Static Mesh UV layout")
            return {"success": False, "message": str(exc)}

    @mcp.tool()
    def generate_texture_from_prompt(
        ctx: Context,
        prompt: str,
        output_name: str,
        output_dir: str,
        size: str = "1024x1024",
    ) -> Dict[str, Any]:
        """
        Prepare a BaseColor texture request for Codex built-in image generation.

        This tool does not call API-key based or external image services.

        Args:
            prompt: Text prompt for the image model.
            output_name: Output PNG basename.
            output_dir: Local directory where the generated PNG will be saved.
            size: Image size, for example 1024x1024.
        """
        output_path = ensure_png_path(output_dir, output_name)
        return _builtin_image_generation_required(prompt, output_path, size)

    @mcp.tool()
    def generate_texture_for_mesh_uv(
        ctx: Context,
        mesh_path: str,
        prompt: str,
        uv_channel: int = 0,
        output_name: str = "T_AI_Texture",
        output_dir: str = "",
        size: str = "1024x1024",
    ) -> Dict[str, Any]:
        """
        Export a mesh UV layout and prepare a Codex built-in image generation request.

        This tool does not call API-key based or external image services.

        Args:
            mesh_path: Static Mesh asset path.
            prompt: Texture prompt.
            uv_channel: UV channel index.
            output_name: Output PNG basename.
            output_dir: Local output directory.
            size: Image size, for example 1024x1024.
        """
        local_output_dir = output_dir or _default_output_dir()
        uv_path = ensure_png_path(local_output_dir, f"{sanitize_output_name(output_name)}_UV{uv_channel}")
        uv_result = export_static_mesh_uv_layout(mesh_path, uv_channel, uv_path)
        if not uv_result.get("success"):
            return {"success": False, "stage": "uv_export", "uv_result": uv_result}

        output_path = ensure_png_path(local_output_dir, output_name)
        guided_prompt = f"{prompt.strip()}\n\n{UV_GUIDED_PROMPT_SUFFIX}"
        result = _builtin_image_generation_required(
            guided_prompt,
            output_path,
            size,
            reference_image_path=uv_result.get("output_path", uv_path),
        )
        result.update(
            {
                "uv_layout_path": uv_result.get("output_path"),
                "mesh_path": mesh_path,
                "uv_channel": uv_channel,
                "uv_result": uv_result,
            }
        )
        return result

    @mcp.tool()
    def import_texture_to_unreal(
        ctx: Context,
        image_path: str,
        unreal_folder: str,
        asset_name: str,
    ) -> Dict[str, Any]:
        """
        Import a PNG file as a Texture2D asset into Unreal.

        Args:
            image_path: Local PNG path.
            unreal_folder: Destination Content Browser folder, for example /Game/AI_Generated/Textures.
            asset_name: Texture asset name.
        """
        return unreal_import_texture_to_unreal(image_path, unreal_folder, asset_name)

    @mcp.tool()
    def create_material_instance_with_texture(
        ctx: Context,
        texture_asset_path: str,
        material_name: str,
        unreal_folder: str,
        base_material_path: str = "",
    ) -> Dict[str, Any]:
        """
        Create a BaseColor material or a material instance using an imported texture.

        Args:
            texture_asset_path: Texture2D asset path.
            material_name: Material or material instance asset name.
            unreal_folder: Destination Content Browser folder.
            base_material_path: Optional base material for a Material Instance.
        """
        return unreal_create_material_instance_with_texture(
            texture_asset_path,
            material_name,
            unreal_folder,
            base_material_path,
        )

    @mcp.tool()
    def apply_material_to_mesh(
        ctx: Context,
        target: str,
        material_asset_path: str,
        material_slot: int = 0,
    ) -> Dict[str, Any]:
        """
        Apply a material to selected actors, a named actor, or a Static Mesh asset.

        Args:
            target: "selected", an actor label/path/name, or a Static Mesh asset path.
            material_asset_path: Material or Material Instance asset path.
            material_slot: Material slot index.
        """
        return unreal_apply_material_to_mesh(target, material_asset_path, material_slot)

    @mcp.tool()
    def generate_and_apply_ai_texture(
        ctx: Context,
        target: str,
        prompt: str,
        output_name: str,
        unreal_folder: str = "/Game/AI_Generated",
        uv_channel: int = 0,
        size: str = "1024x1024",
    ) -> Dict[str, Any]:
        """
        Prepare the UV-guided texture workflow without calling API-key image generation.

        This returns a built-in image-generation handoff. After the PNG exists,
        call import_texture_to_unreal, create_material_instance_with_texture, and
        apply_material_to_mesh.

        Args:
            target: "selected", an actor label/path/name, or a Static Mesh asset path.
            prompt: Texture prompt.
            output_name: Texture asset/output basename.
            unreal_folder: Root destination folder in Unreal.
            uv_channel: UV channel index.
            size: Image size, for example 1024x1024.
        """
        logs = []

        resolved = resolve_target_static_mesh(target)
        logs.append({"stage": "resolve_target", "result": resolved})
        if not resolved.get("success"):
            return {"success": False, "stage": "resolve_target", "logs": logs}

        mesh_path = resolved["mesh_path"]
        local_output_dir = os.path.join(_default_output_dir(), sanitize_output_name(output_name))
        texture_generation = generate_texture_for_mesh_uv(
            ctx,
            mesh_path=mesh_path,
            prompt=prompt,
            uv_channel=uv_channel,
            output_name=output_name,
            output_dir=local_output_dir,
            size=size,
        )
        logs.append({"stage": "generate_texture", "result": texture_generation})
        if not texture_generation.get("success"):
            return {
                "success": False,
                "stage": "builtin_image_generation_required",
                "logs": logs,
                "next_steps": [
                    "Generate the PNG with Codex built-in image generation using the returned prompt and UV layout.",
                    "Save it to expected_output_path.",
                    "Then call import_texture_to_unreal, create_material_instance_with_texture, and apply_material_to_mesh.",
                ],
            }

        texture_folder = f"{unreal_folder.rstrip('/')}/Textures"
        material_folder = f"{unreal_folder.rstrip('/')}/Materials"
        texture_asset_name = sanitize_output_name(output_name)
        material_name = _material_name_from_output(output_name)

        imported_texture = unreal_import_texture_to_unreal(
            texture_generation["image_path"],
            texture_folder,
            texture_asset_name,
        )
        logs.append({"stage": "import_texture", "result": imported_texture})
        if not imported_texture.get("success"):
            return {"success": False, "stage": "import_texture", "logs": logs}

        material = unreal_create_material_instance_with_texture(
            imported_texture["asset_path"],
            material_name,
            material_folder,
        )
        logs.append({"stage": "create_material", "result": material})
        if not material.get("success"):
            return {"success": False, "stage": "create_material", "logs": logs}

        applied = unreal_apply_material_to_mesh(target, material["asset_path"], 0)
        logs.append({"stage": "apply_material", "result": applied})
        if not applied.get("success"):
            return {"success": False, "stage": "apply_material", "logs": logs}

        return {
            "success": True,
            "target": target,
            "mesh_path": mesh_path,
            "uv_layout_path": texture_generation.get("uv_layout_path"),
            "generated_image_path": texture_generation.get("image_path"),
            "texture_asset_path": imported_texture.get("asset_path"),
            "material_asset_path": material.get("asset_path"),
            "logs": logs,
            "note": "This first implementation creates a BaseColor texture/material only. Normal/Roughness/AO/Metallic generation is intentionally left as TODO.",
        }

    logger.info("AI texture generation tools registered successfully")
