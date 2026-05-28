# AI Texture Tools

These MCP tools add a BaseColor-focused AI texture pipeline for Unreal Editor.

The first implementation does not claim to generate a complete PBR set. Normal,
Roughness, AO, and Metallic generation are TODO/stub territory and should be
added as separate heuristics or model calls later.

## Requirements

- Unreal Editor must be running with the UnrealMCP plugin connected on port `55557`.
- `OPENAI_API_KEY` must be set in the MCP server environment for image generation.
- Optional: `OPENAI_IMAGE_MODEL` can override the default `gpt-image-1` model.

## Tools

- `get_static_mesh_uv_layout(mesh_path, uv_channel=0, output_path="")`
  - Exports a Static Mesh UV wireframe PNG.
- `generate_texture_from_prompt(prompt, output_name, output_dir, size="1024x1024")`
  - Generates a PNG texture from text only.
- `generate_texture_for_mesh_uv(mesh_path, prompt, uv_channel=0, output_name="T_AI_Texture", output_dir="", size="1024x1024")`
  - Exports UVs, then uses the UV PNG as a guide image for GPT Image.
- `import_texture_to_unreal(image_path, unreal_folder, asset_name)`
  - Imports a PNG as a Texture2D.
- `create_material_instance_with_texture(texture_asset_path, material_name, unreal_folder, base_material_path="")`
  - Creates a BaseColor material, or a material instance if `base_material_path` is provided.
- `apply_material_to_mesh(target, material_asset_path, material_slot=0)`
  - Applies a material to selected actors, a named actor, or a Static Mesh asset.
- `generate_and_apply_ai_texture(target, prompt, output_name, unreal_folder="/Game/AI_Generated", uv_channel=0, size="1024x1024")`
  - Full pipeline: resolve mesh, export UV, generate PNG, import Texture2D, create material, apply.

## Examples

Generate and apply to the selected Static Mesh actor:

```text
Use generate_and_apply_ai_texture on the selected mesh.
Prompt: mossy ancient stone floor, realistic game texture, high detail, non-photographic, seamless feel.
Output name: T_AI_MossyStone_01.
```

Generate a texture for a specific mesh path:

```text
Use generate_texture_for_mesh_uv with mesh_path /Game/Props/SM_Panel.
Prompt: sci-fi metal panel texture, worn edges, high detail, game albedo texture.
Output name: T_AI_SciFiPanel_01.
```

Generate a texture only, without importing:

```text
Use generate_texture_from_prompt.
Prompt: hand painted mossy stone floor tile, seamless feel, BaseColor only.
Output name: T_AI_MossyStone_Only.
Output dir: D:/Temp/AI_Textures.
```

Create a material from an imported Texture2D:

```text
Use create_material_instance_with_texture.
Texture asset path: /Game/AI_Generated/Textures/T_AI_MossyStone_01.
Material name: M_AI_MossyStone_01.
Unreal folder: /Game/AI_Generated/Materials.
```

## Failure Behavior

- Missing `OPENAI_API_KEY` returns a friendly error before any external call.
- Invalid `mesh_path` returns an Unreal-side validation error.
- UV export failure stops the image pipeline and returns the UV stage result.
- If GPT Image guided editing is unavailable, the UV PNG path is returned with a clear guide to use text-only generation or enable a supported image-edit model/API path.
