"""
Editor Tools for Unreal MCP.

This module provides tools for controlling the Unreal Editor viewport and other editor functionality.
"""

import logging
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP, Context

# Get logger
logger = logging.getLogger("UnrealMCP")

def register_editor_tools(mcp: FastMCP):
    """Register editor tools with the MCP server."""
    
    @mcp.tool()
    def get_actors_in_level(ctx: Context) -> Dict[str, Any]:
        """Get all actors in the current level as structured JSON with actor_count and actors."""
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine", "actor_count": 0, "actors": []}
                
            response = unreal.send_command("get_actors_in_level", {})
            
            if not response:
                logger.warning("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine", "actor_count": 0, "actors": []}
                
            # Log the complete response for debugging
            logger.info(f"Complete response from Unreal: {response}")
            
            # Check response format
            if "result" in response and "actors" in response["result"]:
                actors = response["result"]["actors"]
                logger.info(f"Found {len(actors)} actors in level")
                return {"success": True, "actor_count": len(actors), "actors": actors, "unreal_response": response}
            elif "actors" in response:
                actors = response["actors"]
                logger.info(f"Found {len(actors)} actors in level")
                return {"success": True, "actor_count": len(actors), "actors": actors, "unreal_response": response}
                
            logger.warning(f"Unexpected response format: {response}")
            return {
                "success": False,
                "message": "Unexpected response format from Unreal Engine",
                "actor_count": 0,
                "actors": [],
                "unreal_response": response,
            }
            
        except Exception as e:
            logger.error(f"Error getting actors: {e}")
            return {"success": False, "message": str(e), "actor_count": 0, "actors": []}

    @mcp.tool()
    def find_actors_by_name(ctx: Context, pattern: str) -> Dict[str, Any]:
        """
        Find actors by name pattern and return structured actor data.

        Args:
            pattern: Substring to match against actor object names.
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.warning("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine", "actor_count": 0, "actors": []}
                
            response = unreal.send_command("find_actors_by_name", {
                "pattern": pattern
            })
            
            if not response:
                return {"success": False, "message": "No response from Unreal Engine", "actor_count": 0, "actors": []}

            if "result" in response and "actors" in response["result"]:
                actors = response["result"]["actors"]
            else:
                actors = response.get("actors", [])

            return {"success": True, "actor_count": len(actors), "actors": actors, "unreal_response": response}
            
        except Exception as e:
            logger.error(f"Error finding actors: {e}")
            return {"success": False, "message": str(e), "actor_count": 0, "actors": []}
    
    @mcp.tool()
    def spawn_actor(
        ctx: Context,
        name: str,
        type: str,
        location: List[float] = [0.0, 0.0, 0.0],
        rotation: List[float] = [0.0, 0.0, 0.0]
    ) -> Dict[str, Any]:
        """Create a new actor in the current level.
        
        Args:
            ctx: The MCP context
            name: The name to give the new actor (must be unique)
            type: The type of actor to create (e.g. StaticMeshActor, PointLight)
            location: The [x, y, z] world location to spawn at
            rotation: The [pitch, yaw, roll] rotation in degrees
            
        Returns:
            Dict containing the created actor's properties
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            
            # Ensure all parameters are properly formatted
            params = {
                "name": name,
                "type": type.upper(),  # Make sure type is uppercase
                "location": location,
                "rotation": rotation
            }
            
            # Validate location and rotation formats
            for param_name in ["location", "rotation"]:
                param_value = params[param_name]
                if not isinstance(param_value, list) or len(param_value) != 3:
                    logger.error(f"Invalid {param_name} format: {param_value}. Must be a list of 3 float values.")
                    return {"success": False, "message": f"Invalid {param_name} format. Must be a list of 3 float values."}
                # Ensure all values are float
                params[param_name] = [float(val) for val in param_value]
            
            logger.info(f"Creating actor '{name}' of type '{type}' with params: {params}")
            response = unreal.send_command("spawn_actor", params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            # Log the complete response for debugging
            logger.info(f"Actor creation response: {response}")
            
            # Handle error responses correctly
            if response.get("status") == "error":
                error_message = response.get("error", "Unknown error")
                logger.error(f"Error creating actor: {error_message}")
                return {"success": False, "message": error_message}
            
            return response
            
        except Exception as e:
            error_msg = f"Error creating actor: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    @mcp.tool()
    def delete_actor(ctx: Context, name: str) -> Dict[str, Any]:
        """Delete an actor by name."""
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("delete_actor", {
                "name": name
            })
            return response or {}
            
        except Exception as e:
            logger.error(f"Error deleting actor: {e}")
            return {}
    
    @mcp.tool()
    def set_actor_transform(
        ctx: Context,
        name: str,
        location: List[float]  = None,
        rotation: List[float]  = None,
        scale: List[float] = None
    ) -> Dict[str, Any]:
        """Set the transform of an actor."""
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
                
            params = {"name": name}
            if location is not None:
                params["location"] = location
            if rotation is not None:
                params["rotation"] = rotation
            if scale is not None:
                params["scale"] = scale
                
            response = unreal.send_command("set_actor_transform", params)
            return response or {}
            
        except Exception as e:
            logger.error(f"Error setting transform: {e}")
            return {}
    
    @mcp.tool()
    def get_actor_properties(ctx: Context, name: str) -> Dict[str, Any]:
        """Get all properties of an actor."""
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("get_actor_properties", {
                "name": name
            })
            return response or {}
            
        except Exception as e:
            logger.error(f"Error getting properties: {e}")
            return {}

    @mcp.tool()
    def set_actor_property(
        ctx: Context,
        name: str,
        property_name: str,
        property_value,
    ) -> Dict[str, Any]:
        """
        Set a property on an actor.
        
        Args:
            name: Name of the actor
            property_name: Name of the property to set
            property_value: Value to set the property to
            
        Returns:
            Dict containing response from Unreal with operation status
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
                
            response = unreal.send_command("set_actor_property", {
                "name": name,
                "property_name": property_name,
                "property_value": property_value
            })
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Set actor property response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error setting actor property: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def take_screenshot(
        ctx: Context,
        filepath: str,
    ) -> Dict[str, Any]:
        """
        Capture the active editor viewport to a PNG file through the legacy bridge command.

        Args:
            filepath: Absolute or project-relative PNG output path. .png is appended if omitted.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("take_screenshot", {"filepath": filepath})
            return response or {"success": False, "message": "No response from Unreal Engine"}

        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def focus_viewport(
        ctx: Context,
        target: Optional[str] = None,
        location: Optional[List[float]] = None,
        distance: float = 1000.0,
        orientation: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        Focus the viewport on a specific actor or location.
        
        Args:
            target: Name of the actor to focus on (if provided, location is ignored)
            location: [X, Y, Z] coordinates to focus on (used if target is None)
            distance: Distance from the target/location
            orientation: Optional [Pitch, Yaw, Roll] for the viewport camera
            
        Returns:
            Response from Unreal Engine
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
                
            params = {}
            if target:
                params["target"] = target
            elif location:
                params["location"] = location
            
            if distance:
                params["distance"] = distance
                
            if orientation:
                params["orientation"] = orientation
                
            response = unreal.send_command("focus_viewport", params)
            return response or {}
            
        except Exception as e:
            logger.error(f"Error focusing viewport: {e}")
            return {"status": "error", "message": str(e)}

    @mcp.tool()
    def take_screenshot(ctx: Context, filepath: str) -> Dict[str, Any]:
        """
        Capture the active editor viewport to a PNG file.

        Args:
            filepath: Output PNG path. The native bridge appends .png when omitted.

        Returns:
            Response from Unreal Engine with the saved filepath or an error.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("take_screenshot", {"filepath": filepath})
            return response or {"success": False, "message": "No response from Unreal Engine"}

        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def list_viewport_bookmarks(ctx: Context) -> Dict[str, Any]:
        """
        List bookmark slots available to the active editor viewport.

        Returns:
            Dict with max_bookmark_count, per-slot existence, existing_indices,
            and the current viewport transform.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("list_viewport_bookmarks", {})
            return response or {}

        except Exception as e:
            logger.error(f"Error listing viewport bookmarks: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def capture_viewport_bookmark_screenshot(
        ctx: Context,
        filepath: str,
        bookmark_index: int = -1,
        redraw_count: int = 2,
    ) -> Dict[str, Any]:
        """
        Capture the active editor viewport, optionally after jumping to a bookmark.

        Args:
            filepath: PNG output path.
            bookmark_index: Bookmark slot to jump to before capture. Use -1 for active viewport.
            redraw_count: Number of forced viewport draws before pixel readback, clamped by the bridge.

        Returns:
            Dict containing screenshot path, size, file size, capture mode, and viewport transform.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params: Dict[str, Any] = {
                "filepath": filepath,
                "redraw_count": redraw_count,
            }
            if bookmark_index >= 0:
                params["bookmark_index"] = bookmark_index

            response = unreal.send_command("capture_viewport_bookmark_screenshot", params)
            return response or {}

        except Exception as e:
            logger.error(f"Error capturing viewport screenshot: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def open_editor_level(
        ctx: Context,
        level_path: str,
        dry_run: bool = True,
        allow_dirty_packages: bool = False,
        load_as_template: bool = False,
        show_progress: bool = True,
    ) -> Dict[str, Any]:
        """
        Safely preflight or open an editor level through the native bridge.

        Args:
            level_path: Long package path, object path, or .umap filename.
            dry_run: If true, only validate the transition and report blockers.
            allow_dirty_packages: If false, block real transitions when dirty packages exist.
            load_as_template: Forwarded to FEditorFileUtils::LoadMap for real loads.
            show_progress: Forwarded to FEditorFileUtils::LoadMap for real loads.

        Returns:
            Dict with target path, current world, dirty package summary,
            can_load, blocked_reasons, load_attempted, and loaded.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command(
                "open_editor_level",
                {
                    "level_path": level_path,
                    "dry_run": dry_run,
                    "allow_dirty_packages": allow_dirty_packages,
                    "load_as_template": load_as_template,
                    "show_progress": show_progress,
                },
            )
            return response or {}

        except Exception as e:
            logger.error(f"Error opening editor level: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def safe_new_preview_map(
        ctx: Context,
        map_path: str,
        dry_run: bool = True,
        allow_dirty_packages: bool = False,
        overwrite_existing: bool = False,
        allow_non_temp_path: bool = False,
        required_root: str = "/Game/_MCP_Temp",
        is_partitioned_world: bool = False,
    ) -> Dict[str, Any]:
        """
        Safely preflight or create a new blank preview map through the native bridge.

        Args:
            map_path: Long package path, object path, or .umap filename for the new map.
            dry_run: If true, only validate the creation request and report blockers.
            allow_dirty_packages: If false, block real creation when dirty packages exist.
            overwrite_existing: If false, block when the target map already exists.
            allow_non_temp_path: If false, require the target to be under required_root.
            required_root: Required package root for temporary preview maps.
            is_partitioned_world: Forwarded to GEditor->NewMap for real creation.

        Returns:
            Dict with target path, current world, dirty package summary,
            can_create, blocked_reasons, create_attempted, created, and saved.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command(
                "safe_new_preview_map",
                {
                    "map_path": map_path,
                    "dry_run": dry_run,
                    "allow_dirty_packages": allow_dirty_packages,
                    "overwrite_existing": overwrite_existing,
                    "allow_non_temp_path": allow_non_temp_path,
                    "required_root": required_root,
                    "is_partitioned_world": is_partitioned_world,
                },
            )
            return response or {}

        except Exception as e:
            logger.error(f"Error creating preview map: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def spawn_blueprint_actor(
        ctx: Context,
        blueprint_name: str,
        actor_name: str,
        location: List[float] = [0.0, 0.0, 0.0],
        rotation: List[float] = [0.0, 0.0, 0.0]
    ) -> Dict[str, Any]:
        """Spawn an actor from a Blueprint.
        
        Args:
            ctx: The MCP context
            blueprint_name: Name of the Blueprint to spawn from
            actor_name: Name to give the spawned actor
            location: The [x, y, z] world location to spawn at
            rotation: The [pitch, yaw, roll] rotation in degrees
            
        Returns:
            Dict containing the spawned actor's properties
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            
            # Ensure all parameters are properly formatted
            params = {
                "blueprint_name": blueprint_name,
                "actor_name": actor_name,
                "location": location or [0.0, 0.0, 0.0],
                "rotation": rotation or [0.0, 0.0, 0.0]
            }
            
            # Validate location and rotation formats
            for param_name in ["location", "rotation"]:
                param_value = params[param_name]
                if not isinstance(param_value, list) or len(param_value) != 3:
                    logger.error(f"Invalid {param_name} format: {param_value}. Must be a list of 3 float values.")
                    return {"success": False, "message": f"Invalid {param_name} format. Must be a list of 3 float values."}
                # Ensure all values are float
                params[param_name] = [float(val) for val in param_value]
            
            logger.info(f"Spawning blueprint actor with params: {params}")
            response = unreal.send_command("spawn_blueprint_actor", params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Spawn blueprint actor response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error spawning blueprint actor: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def open_niagara_preview_player(ctx: Context, system_path: str = "") -> Dict[str, Any]:
        """Open the level-independent Niagara Preview Player window.

        The current MVP is a Slate drop surface. It accepts Content Browser
        assets and World Outliner actors, then exposes the latest drop through
        get_niagara_preview_player_state().

        Args:
            system_path: Optional Niagara System path to load into the player after opening.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {}
            if system_path:
                params["system_path"] = system_path
            response = unreal.send_command("open_niagara_preview_player", params)
            return response or {}

        except Exception as e:
            logger.error(f"Error opening Niagara Preview Player: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def get_niagara_preview_player_state(ctx: Context) -> Dict[str, Any]:
        """Get Niagara Preview Player window/drop state."""
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("get_niagara_preview_player_state", {})
            return response or {}

        except Exception as e:
            logger.error(f"Error getting Niagara Preview Player state: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def get_niagara_preview_lab_state(ctx: Context) -> Dict[str, Any]:
        """Get the current Niagara Preview Lab map, dirty, safety, and preview actor state."""
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("get_niagara_preview_lab_state", {})
            return response or {}

        except Exception as e:
            logger.error(f"Error getting Niagara Preview Lab state: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def cleanup_niagara_preview_lab(ctx: Context) -> Dict[str, Any]:
        """Delete Niagara Preview Lab preview actors without saving or reloading the map."""
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("cleanup_niagara_preview_lab", {})
            return response or {}

        except Exception as e:
            logger.error(f"Error cleaning Niagara Preview Lab: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def capture_niagara_preview_lab_view(
        ctx: Context,
        filepath: str,
        view: int = 1,
    ) -> Dict[str, Any]:
        """Capture a clean Niagara Preview Lab screenshot.

        When Preview Lab actors exist, Unreal auto-frames those temporary actors.
        The view number is a near/mid/far distance hint and a fallback when no
        preview actor exists.

        Args:
            filepath: PNG output path. Relative paths are resolved under Saved/MCP/NiagaraReviews.
            view: Preview Lab view number. Use 1 first; use 2 or 3 only when the auto-framed effect is too large, clipped, or not reviewable.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            response = unreal.send_command("capture_niagara_preview_lab_view", {
                "filepath": filepath,
                "view": int(view),
            })
            return response or {}

        except Exception as e:
            logger.error(f"Error capturing Niagara Preview Lab view: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def preview_niagara_system_in_preview_lab(
        ctx: Context,
        system_path: str,
        filepath: str,
        view: int = 1,
        label: str = "",
        warmup_time: float = 0.35,
        warmup_tick_delta: float = 1.0 / 30.0,
        cleanup_before: bool = True,
        cleanup_after: bool = True,
        location: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Run a one-call Niagara Preview Lab still preview.

        This optimized route loads a read-only Niagara system, deletes prior
        Preview Lab actors if requested, spawns one transient preview actor,
        advances simulation for warmup, captures with auto framing, and
        optionally removes the actor afterward.

        Args:
            system_path: Niagara system object path or package path.
            filepath: PNG output path. Relative paths are resolved under Saved/MCP/NiagaraReviews.
            view: Near/mid/far distance hint, 1 to 3.
            label: Optional preview actor label suffix.
            warmup_time: Seconds to advance simulation before capture.
            warmup_tick_delta: Simulation tick size for warmup.
            cleanup_before: Delete existing Preview Lab actors before spawning.
            cleanup_after: Delete Preview Lab actors after capture.
            location: Optional [x, y, z] spawn location. Defaults to [0, 0, 120].
            scale: Optional [x, y, z] actor scale. Defaults to [1, 1, 1].
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params: Dict[str, Any] = {
                "system_path": system_path,
                "filepath": filepath,
                "view": int(view),
                "warmup_time": float(warmup_time),
                "warmup_tick_delta": float(warmup_tick_delta),
                "cleanup_before": bool(cleanup_before),
                "cleanup_after": bool(cleanup_after),
            }
            if label:
                params["label"] = label
            if location is not None:
                params["location"] = location
            if scale is not None:
                params["scale"] = scale

            response = unreal.send_command("preview_niagara_system_in_preview_lab", params)
            return response or {}

        except Exception as e:
            logger.error(f"Error previewing Niagara system in Preview Lab: {e}")
            return {"success": False, "message": str(e)}

    @mcp.tool()
    def sample_niagara_system_in_preview_lab(
        ctx: Context,
        system_path: str,
        output_dir: str = "",
        label: str = "",
        warmup_times: Optional[List[float]] = None,
        views: Optional[List[int]] = None,
        warmup_tick_delta: float = 1.0 / 30.0,
        cleanup_before: bool = True,
        cleanup_after_each: bool = True,
        cleanup_after_all: bool = True,
        location: Optional[List[float]] = None,
        scale: Optional[List[float]] = None,
    ) -> Dict[str, Any]:
        """Capture multiple Niagara Preview Lab candidates in one MCP round trip.

        Use this when a Niagara effect is timing-sensitive or not visible in the
        first still. The Unreal-side command loops over warmup times and views,
        captures each candidate with auto framing, and returns sample metadata.

        Args:
            system_path: Niagara system object path or package path.
            output_dir: Relative output folder under Saved/MCP/NiagaraReviews.
            label: File and actor label stem.
            warmup_times: Seconds to advance simulation before each capture.
            views: Near/mid/far distance hints, values 1 to 3.
            warmup_tick_delta: Simulation tick size for warmup.
            cleanup_before: Delete existing Preview Lab actors before sampling.
            cleanup_after_each: Delete the sample actor after each capture.
            cleanup_after_all: Final cleanup pass after all samples.
            location: Optional [x, y, z] spawn location.
            scale: Optional [x, y, z] actor scale.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params: Dict[str, Any] = {
                "system_path": system_path,
                "warmup_tick_delta": float(warmup_tick_delta),
                "cleanup_before": bool(cleanup_before),
                "cleanup_after_each": bool(cleanup_after_each),
                "cleanup_after_all": bool(cleanup_after_all),
            }
            if output_dir:
                params["output_dir"] = output_dir
            if label:
                params["label"] = label
            if warmup_times is not None:
                params["warmup_times"] = warmup_times
            if views is not None:
                params["views"] = views
            if location is not None:
                params["location"] = location
            if scale is not None:
                params["scale"] = scale

            response = unreal.send_command("sample_niagara_system_in_preview_lab", params)
            return response or {}

        except Exception as e:
            logger.error(f"Error sampling Niagara system in Preview Lab: {e}")
            return {"success": False, "message": str(e)}

    logger.info("Editor tools registered successfully")
