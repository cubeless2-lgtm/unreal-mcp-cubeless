"""
Project Tools for Unreal MCP.

This module provides tools for managing project-wide settings and configuration.
"""

import logging
from typing import Dict, Any
from mcp.server.fastmcp import FastMCP, Context

# Get logger
logger = logging.getLogger("UnrealMCP")

def register_project_tools(mcp: FastMCP):
    """Register project tools with the MCP server."""
    
    @mcp.tool()
    def create_input_mapping(
        ctx: Context,
        action_name: str,
        key: str,
        input_type: str = "Action"
    ) -> Dict[str, Any]:
        """
        Create an input mapping for the project.
        
        Args:
            action_name: Name of the input action
            key: Key to bind (SpaceBar, LeftMouseButton, etc.)
            input_type: Type of input mapping (Action or Axis)
            
        Returns:
            Response indicating success or failure
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            
            params = {
                "action_name": action_name,
                "key": key,
                "input_type": input_type
            }
            
            logger.info(f"Creating input mapping '{action_name}' with key '{key}'")
            response = unreal.send_command("create_input_mapping", params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Input mapping creation response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error creating input mapping: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def recreate_content_folder_mcp(
        ctx: Context,
        source_root: str = "/Game/UltraDynamicSky",
        target_root: str = "/Game/_MCP_Temp/UltraDynamicSky_MCP",
        suffix: str = "_MCP",
        allow_fallback_duplicate: bool = True,
        dry_run: bool = False,
        overwrite_existing: bool = False,
        delete_target_root_first: bool = False,
        remap_references: bool = True,
        compile_blueprints: bool = True,
        log_archive_remap_objects: bool = False,
        refresh_blueprint_nodes: bool = False,
        refresh_failed_blueprint_nodes: bool = True,
        save_assets: bool = True,
        repair_level_actors: bool = True,
        force_repair_level_actors: bool = True,
        compile_passes: int = 2,
        check_editor_log_health: bool = True,
        fail_on_editor_log_issues: bool = True,
        suppress_editor_prompts: bool = True,
    ) -> Dict[str, Any]:
        """
        Recreate a content folder under an MCP target path using a suffix rule.

        The Unreal-side command attempts exact-behavior recreation. When exact
        behavior cannot be safely produced from a fresh factory asset, it uses a
        duplicate fallback and records the reason in the report.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {
                "source_root": source_root,
                "target_root": target_root,
                "suffix": suffix,
                "allow_fallback_duplicate": allow_fallback_duplicate,
                "dry_run": dry_run,
                "overwrite_existing": overwrite_existing,
                "delete_target_root_first": delete_target_root_first,
                "remap_references": remap_references,
                "compile_blueprints": compile_blueprints,
                "log_archive_remap_objects": log_archive_remap_objects,
                "refresh_blueprint_nodes": refresh_blueprint_nodes,
                "refresh_failed_blueprint_nodes": refresh_failed_blueprint_nodes,
                "save_assets": save_assets,
                "repair_level_actors": repair_level_actors,
                "force_repair_level_actors": force_repair_level_actors,
                "compile_passes": compile_passes,
                "check_editor_log_health": check_editor_log_health,
                "fail_on_editor_log_issues": fail_on_editor_log_issues,
                "suppress_editor_prompts": suppress_editor_prompts,
            }
            response = unreal.send_command("recreate_content_folder_mcp", params)
            return response or {"success": False, "message": "No response from Unreal Engine"}
        except Exception as e:
            error_msg = f"Error recreating content folder: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def postprocess_content_folder_mcp(
        ctx: Context,
        source_root: str = "/Game/UltraDynamicSky",
        target_root: str = "/Game/_MCP_Temp/UltraDynamicSky_MCP",
        suffix: str = "_MCP",
        dry_run: bool = False,
        remap_references: bool = True,
        compile_blueprints: bool = True,
        refresh_blueprint_nodes: bool = False,
        refresh_failed_blueprint_nodes: bool = True,
        save_assets: bool = True,
        repair_level_actors: bool = False,
        force_repair_level_actors: bool = False,
        compile_passes: int = 2,
        check_editor_log_health: bool = True,
        fail_on_editor_log_issues: bool = True,
        suppress_editor_prompts: bool = True,
    ) -> Dict[str, Any]:
        """
        Run the reusable MCP postprocess and verification pass for an existing target content folder.

        This does not create, duplicate, delete, or overwrite assets. It pairs
        source assets to existing target assets using the suffix rule, then fixes
        references, Blueprint internals, level instances, and verification data.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {
                "source_root": source_root,
                "target_root": target_root,
                "suffix": suffix,
                "dry_run": dry_run,
                "remap_references": remap_references,
                "compile_blueprints": compile_blueprints,
                "refresh_blueprint_nodes": refresh_blueprint_nodes,
                "refresh_failed_blueprint_nodes": refresh_failed_blueprint_nodes,
                "save_assets": save_assets,
                "repair_level_actors": repair_level_actors,
                "force_repair_level_actors": force_repair_level_actors,
                "compile_passes": compile_passes,
                "check_editor_log_health": check_editor_log_health,
                "fail_on_editor_log_issues": fail_on_editor_log_issues,
                "suppress_editor_prompts": suppress_editor_prompts,
            }
            response = unreal.send_command("postprocess_content_folder_mcp", params)
            return response or {"success": False, "message": "No response from Unreal Engine"}
        except Exception as e:
            error_msg = f"Error postprocessing content folder: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def repair_world_actor_instances_mcp(
        ctx: Context,
        map_path: str,
        source_root: str = "/Game/UltraDynamicSky",
        target_root: str = "/Game/_MCP_Temp/UltraDynamicSky_MCP",
        suffix: str = "_MCP",
        dry_run: bool = False,
        save_map: bool = True,
        remap_level_blueprint: bool = False,
        repair_actor_classes: bool = True,
        repair_component_classes: bool = True,
        remap_actor_references: bool = True,
        remove_source_object_map_keys: bool = True,
        check_editor_log_health: bool = True,
        fail_on_editor_log_issues: bool = True,
        suppress_editor_prompts: bool = True,
    ) -> Dict[str, Any]:
        """
        Repair actor/component instances and object-key maps in one explicit target map.

        Use this after postprocess_content_folder_mcp when map-placed actors,
        components, or world instance references may still point at source assets.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            unreal = get_unreal_connection()
            if not unreal:
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            params = {
                "map_path": map_path,
                "source_root": source_root,
                "target_root": target_root,
                "suffix": suffix,
                "dry_run": dry_run,
                "save_map": save_map,
                "remap_level_blueprint": remap_level_blueprint,
                "repair_actor_classes": repair_actor_classes,
                "repair_component_classes": repair_component_classes,
                "remap_actor_references": remap_actor_references,
                "remove_source_object_map_keys": remove_source_object_map_keys,
                "check_editor_log_health": check_editor_log_health,
                "fail_on_editor_log_issues": fail_on_editor_log_issues,
                "suppress_editor_prompts": suppress_editor_prompts,
            }
            response = unreal.send_command("repair_world_actor_instances_mcp", params)
            return response or {"success": False, "message": "No response from Unreal Engine"}
        except Exception as e:
            error_msg = f"Error repairing world actor instances: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    logger.info("Project tools registered successfully")
