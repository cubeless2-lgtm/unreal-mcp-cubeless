# Unreal MCP Editor Tools

This document provides detailed information about the editor tools available in the Unreal MCP integration.

## Overview

Editor tools allow you to control the Unreal Editor viewport and other editor functionality through MCP commands. These tools are particularly useful for automating tasks like focusing the camera on specific actors or locations.

## Editor Tools

### focus_viewport

Focus the viewport on a specific actor or location.

**Parameters:**
- `target` (string, optional) - Name of the actor to focus on (if provided, location is ignored)
- `location` (array, optional) - [X, Y, Z] coordinates to focus on (used if target is None)
- `distance` (float, optional) - Distance from the target/location (default: 1000.0)
- `orientation` (array, optional) - [Pitch, Yaw, Roll] for the viewport camera

**Returns:**
- Response from Unreal Engine containing the result of the focus operation

**Example:**
```json
{
  "command": "focus_viewport",
  "params": {
    "target": "PlayerStart",
    "distance": 500,
    "orientation": [0, 180, 0]
  }
}
```

### take_screenshot

Capture a screenshot of the viewport.

**Parameters:**
- `filename` (string, optional) - Name of the file to save the screenshot as (default: "screenshot.png")
- `show_ui` (boolean, optional) - Whether to include UI elements in the screenshot (default: false)
- `resolution` (array, optional) - [Width, Height] for the screenshot

**Returns:**
- Result of the screenshot operation

**Example:**
```json
{
  "command": "take_screenshot",
  "params": {
    "filename": "my_scene.png",
    "show_ui": false,
    "resolution": [1920, 1080]
  }
}
```

### list_viewport_bookmarks

List bookmark slots for the active editor viewport.

**Parameters:**
- None

**Returns:**
- `max_bookmark_count`
- `bookmarks` with per-slot `index` and `exists`
- `existing_indices`
- current `view_location` and `view_rotation`

### capture_viewport_bookmark_screenshot

Capture the active editor viewport to PNG, optionally after jumping to an existing bookmark slot. This uses the native UnrealMCP bridge path, not OS window capture, and does not overwrite bookmark data.

**Parameters:**
- `filepath` (string, required) - PNG output path
- `bookmark_index` (integer, optional) - Bookmark slot to jump to before capture. Omit or use `-1` for the active viewport.
- `redraw_count` (integer, optional) - Forced viewport draws before pixel readback, default `2`

**Returns:**
- `filepath`, `width`, `height`, `file_size_bytes`
- `capture_mode`
- `bookmark_requested`, `bookmark_exists`, `bookmark_index`
- `view_location`, `view_rotation`
- `dirty_package_count`, `dirty_packages`
- `dirty_package_count_before`, `dirty_package_count_after`
- `dirty_package_added_count`, `dirty_packages_added_by_command`
- `dirty_package_removed_count`, `dirty_packages_removed_by_command`

**Example:**
```json
{
  "command": "capture_viewport_bookmark_screenshot",
  "params": {
    "bookmark_index": 1,
    "filepath": "D:/Git/CubelessStylized/Saved/MCP_Screenshots/bookmark_1.png",
    "redraw_count": 2
  }
}
```

### open_editor_level

Safely preflight or open an editor level through the native UnrealMCP bridge. The default is `dry_run=true`, so the command reports target validity and blockers without changing the current map.

**Parameters:**
- `level_path` (string, required) - Long package path, object path, or `.umap` filename
- `dry_run` (boolean, optional) - Validate only, default `true`
- `allow_dirty_packages` (boolean, optional) - Allow a real transition while dirty packages exist, default `false`
- `load_as_template` (boolean, optional) - Forwarded to `FEditorFileUtils::LoadMap`
- `show_progress` (boolean, optional) - Forwarded to `FEditorFileUtils::LoadMap`

**Returns:**
- `target_long_package_name`, `target_filename`, `target_exists`
- `current_world_package_name`, `already_open`
- `can_load`, `blocked_reasons`
- `dirty_package_count_before`, `dirty_packages_before`
- `load_attempted`, `loaded`

**Example:**
```json
{
  "command": "open_editor_level",
  "params": {
    "level_path": "/Game/_MCP_Temp/PCG/LVL_PCG_LandscapeValidation_MCP",
    "dry_run": true
  }
}
```

### open_niagara_preview_player

Open the level-independent Niagara Preview Player window. The current MVP is a
Slate drop surface that accepts Content Browser assets and World Outliner actors
without saving or modifying the current level. Pass `system_path` to load a
Niagara System immediately after opening.

```json
{
  "command": "open_niagara_preview_player",
  "params": {
    "system_path": "/Game/FX/NS_Example.NS_Example"
  }
}
```

### get_niagara_preview_player_state

Return whether the Niagara Preview Player window is open and the latest dropped
asset/actor metadata.

```json
{
  "command": "get_niagara_preview_player_state",
  "params": {}
}
```

### get_niagara_preview_lab_state

Return Niagara Preview Lab safety state for the currently loaded editor world.

**Returns:**
- Current map package
- Whether the loaded map is the Niagara Preview Lab map
- Whether the map is dirty
- Preview actor labels using `MCP_NiagaraPreviewLab_` or legacy `MCP_NiagaraReview_`
- Whether an editor restart is recommended instead of reloading the map

### cleanup_niagara_preview_lab

Delete Niagara Preview Lab preview actors by prefix without saving or reloading the map.

This command is intentionally conservative. If the map remains dirty after cleanup, do not call `load_map` from the same session. Restart Unreal Editor for a full reset.

### capture_niagara_preview_lab_view

Capture a clean Niagara Preview Lab viewport PNG. When Preview Lab actors exist, the Unreal-side command frames those temporary actors with an auto camera instead of relying on fixed bookmarks. The `view` value remains a near/mid/far distance hint and fallback when no preview actor exists.

**Parameters:**
- `filepath` (string, required) - PNG output path. Relative paths are resolved under `Saved/MCP/NiagaraReviews`.
- `view` (integer, optional) - Preview view number. Use 1 first; use 2 or 3 only when the auto-framed effect is too large, clipped, or not reviewable.

**Safety:**
- Requires `/Game/SampleTestMap/Niagara_TestMap` to already be loaded.
- Does not load, reload, or save maps.
- Temporarily enters clean game view for the capture and restores viewport flags afterward.
- Returns camera mode, camera location/rotation, and frame target metadata when auto framing is used.

### preview_niagara_system_in_preview_lab

Run the optimized one-call Niagara Preview Lab route.

This command loads a read-only Niagara system, optionally deletes existing Preview Lab actors, spawns one transient preview actor, advances Niagara simulation for a short warmup, captures with auto framing, and optionally removes the actor afterward. Use this as the default route for repeated generated Niagara still reviews because it avoids separate Python spawn, state, capture, and cleanup round trips.

**Parameters:**
- `system_path` (string, required) - Niagara system object path or package path.
- `filepath` (string, required) - PNG output path. Relative paths are resolved under `Saved/MCP/NiagaraReviews`.
- `view` (integer, optional) - Near/mid/far distance hint, 1 to 3.
- `label` (string, optional) - Preview actor label suffix.
- `warmup_time` (float, optional) - Seconds to advance simulation before capture. Default `0.35`.
- `warmup_tick_delta` (float, optional) - Simulation tick size for warmup. Default `1/30`.
- `cleanup_before` (bool, optional) - Delete existing Preview Lab actors before spawning. Default `true`.
- `cleanup_after` (bool, optional) - Delete Preview Lab actors after capture. Default `true`.
- `location` (array, optional) - Spawn location `[x, y, z]`. Default `[0, 0, 120]`.
- `scale` (array, optional) - Actor scale `[x, y, z]`. Default `[1, 1, 1]`.

**Safety:**
- Requires `/Game/SampleTestMap/Niagara_TestMap` to already be loaded.
- Does not load, reload, or save maps.
- Does not modify or save the source Niagara system.
- Spawns the preview actor as transient and removes it by default.

### sample_niagara_system_in_preview_lab

Capture multiple Niagara Preview Lab candidates in one MCP round trip.

Use this when a Niagara effect is timing-sensitive, invisible in the first still, or needs a quick search over warmup moments and near/mid/far distances. The command loops over `warmup_times` and `views`, uses the optimized one-call preview route for each candidate, and returns structured metadata for every generated PNG.

**Parameters:**
- `system_path` (string, required) - Niagara system object path or package path.
- `output_dir` (string, optional) - Relative output folder under `Saved/MCP/NiagaraReviews`.
- `label` (string, optional) - File and actor label stem.
- `warmup_times` (array, optional) - Seconds to advance simulation before each capture. Default `[0.1, 0.35, 0.7]`.
- `views` (array, optional) - Near/mid/far distance hints. Default `[1]`.
- `warmup_tick_delta` (float, optional) - Simulation tick size for warmup. Default `1/30`.
- `cleanup_before` (bool, optional) - Delete existing Preview Lab actors before sampling. Default `true`.
- `cleanup_after_each` (bool, optional) - Delete the sample actor after each capture. Default `true`.
- `cleanup_after_all` (bool, optional) - Final cleanup pass after all samples. Default `true`.
- `location` (array, optional) - Spawn location `[x, y, z]`.
- `scale` (array, optional) - Actor scale `[x, y, z]`.

**Safety:**
- Requires `/Game/SampleTestMap/Niagara_TestMap` to already be loaded.
- Does not load, reload, or save maps.
- Does not modify or save the source Niagara system.
- Leaves no preview actors when cleanup options remain enabled.

## Error Handling

All command responses include a "status" field indicating whether the operation succeeded, and an optional "message" field with details in case of failure.

```json
{
  "status": "error",
  "message": "Failed to get active viewport"
}
```

## Usage Examples

### Python Example

```python
from unreal_mcp_server import get_unreal_connection

# Get connection to Unreal Engine
unreal = get_unreal_connection()

# Focus on a specific actor
focus_response = unreal.send_command("focus_viewport", {
    "target": "PlayerStart",
    "distance": 500,
    "orientation": [0, 180, 0]
})
print(focus_response)

# Take a screenshot
screenshot_response = unreal.send_command("take_screenshot", {"filename": "my_scene.png"})
print(screenshot_response)
```

## Troubleshooting

- **Command fails with "Failed to get active viewport"**: Make sure Unreal Editor is running and has an active viewport.
- **Actor not found**: Verify that the actor name is correct and the actor exists in the current level.
- **Invalid parameters**: Ensure that location and orientation arrays contain exactly 3 values (X, Y, Z for location; Pitch, Yaw, Roll for orientation).

## Future Enhancements

- Support for setting viewport display mode (wireframe, lit, etc.)
- Camera animation paths for cinematic viewport control
- Support for multiple viewports
