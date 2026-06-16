"""
Niagara authoring and inspection tools for Unreal MCP.

These tools route to UnrealMCP C++ commands for Niagara APIs that are not
safe or practical through Unreal Python alone, such as renderer material edits
and stack/module input inspection.
"""

import logging
from typing import Any, Dict

from mcp.server.fastmcp import Context, FastMCP

logger = logging.getLogger("UnrealMCP")


def register_niagara_tools(mcp: FastMCP):
    """Register Niagara inspection and limited authoring tools."""

    def send_niagara_command(command_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
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
    def analyze_niagara_system(
        ctx: Context,
        system_path: str,
        include_renderers: bool = True,
        include_user_parameters: bool = True,
        include_stack: bool = True,
        include_graph: bool = True,
        include_module_inputs: bool = True,
        include_compile_status: bool = True,
        include_pins: bool = False,
        include_links: bool = False,
        include_scratch_pads: bool = True,
        include_resolved_stack_inputs: bool = False,
        max_function_calls: int = 200,
        max_nodes_per_graph: int = 300,
        max_links_per_graph: int = 0,
        max_modules: int = 200,
        max_candidates_per_module: int = 24,
        max_resolved_inputs_per_module: int = 8,
        max_top_candidates: int = 80,
    ) -> Dict[str, Any]:
        """
        Aggregate read-only Niagara renderer, user parameter, stack, graph,
        module-input, and compile-health inspection into one response.

        Args:
            system_path: Niagara System package path or object path
            include_renderers: Include renderer/material inspection
            include_user_parameters: Include exposed User.* parameter inspection
            include_stack: Include stack function-call inspection
            include_graph: Include graph topology inspection
            include_module_inputs: Include module input candidate inspection
            include_compile_status: Include read-only compile status inspection
            include_pins: Include pin metadata where supported
            include_links: Include explicit graph links where supported
            include_scratch_pads: Include Scratch Pad graph/script data
            include_resolved_stack_inputs: Include resolved stack input values in module inspection
            max_function_calls: Maximum function calls per stack graph
            max_nodes_per_graph: Maximum graph nodes per graph
            max_links_per_graph: Maximum graph links per graph
            max_modules: Maximum modules to inspect
            max_candidates_per_module: Maximum candidates per module
            max_resolved_inputs_per_module: Maximum resolved inputs per module
            max_top_candidates: Maximum prioritized module input candidates
        """
        try:
            return send_niagara_command(
                "analyze_niagara_system",
                {
                    "system_path": system_path,
                    "include_renderers": include_renderers,
                    "include_user_parameters": include_user_parameters,
                    "include_stack": include_stack,
                    "include_graph": include_graph,
                    "include_module_inputs": include_module_inputs,
                    "include_compile_status": include_compile_status,
                    "include_pins": include_pins,
                    "include_links": include_links,
                    "include_scratch_pads": include_scratch_pads,
                    "include_resolved_stack_inputs": include_resolved_stack_inputs,
                    "max_function_calls": max_function_calls,
                    "max_nodes_per_graph": max_nodes_per_graph,
                    "max_links_per_graph": max_links_per_graph,
                    "max_modules": max_modules,
                    "max_candidates_per_module": max_candidates_per_module,
                    "max_resolved_inputs_per_module": max_resolved_inputs_per_module,
                    "max_top_candidates": max_top_candidates,
                },
            )
        except Exception as e:
            error_msg = f"Error analyzing Niagara system: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_niagara_renderers(ctx: Context, system_path: str) -> Dict[str, Any]:
        """
        Inspect enabled renderer properties and materials on a Niagara System.

        Args:
            system_path: Niagara System package path or object path
        """
        try:
            return send_niagara_command("inspect_niagara_renderers", {"system_path": system_path})
        except Exception as e:
            error_msg = f"Error inspecting Niagara renderers: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_niagara_renderer_material(
        ctx: Context,
        system_path: str,
        material_path: str,
        emitter_index: int | None = None,
        emitter_name: str = "",
        renderer_index: int | None = None,
        material_slot_index: int = 0,
        allow_source_edit: bool = False,
        save: bool = True,
    ) -> Dict[str, Any]:
        """
        Set a Niagara renderer material on a temp/generated system by default.

        Args:
            system_path: Niagara System package path or object path
            material_path: Material or Material Instance package path or object path
            emitter_index: Optional target emitter index
            emitter_name: Optional target emitter name
            renderer_index: Optional target renderer index
            material_slot_index: Mesh renderer override slot index
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System after editing
        """
        try:
            params: Dict[str, Any] = {
                "system_path": system_path,
                "material_path": material_path,
                "emitter_name": emitter_name,
                "material_slot_index": material_slot_index,
                "allow_source_edit": allow_source_edit,
                "save": save,
            }
            if emitter_index is not None:
                params["emitter_index"] = emitter_index
            if renderer_index is not None:
                params["renderer_index"] = renderer_index
            return send_niagara_command("set_niagara_renderer_material", params)
        except Exception as e:
            error_msg = f"Error setting Niagara renderer material: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_niagara_user_parameters(ctx: Context, system_path: str) -> Dict[str, Any]:
        """
        Inspect exposed User parameters on a Niagara System.

        Args:
            system_path: Niagara System package path or object path
        """
        try:
            return send_niagara_command("inspect_niagara_user_parameters", {"system_path": system_path})
        except Exception as e:
            error_msg = f"Error inspecting Niagara user parameters: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_niagara_user_parameter(
        ctx: Context,
        system_path: str,
        parameter_name: str,
        value: Any,
        allow_source_edit: bool = False,
        save: bool = True,
    ) -> Dict[str, Any]:
        """
        Set a supported exposed Niagara User parameter value.

        Args:
            system_path: Niagara System package path or object path
            parameter_name: Parameter name, with or without the User. prefix
            value: New JSON value. Vector/color values use arrays or objects.
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System after editing
        """
        try:
            return send_niagara_command(
                "set_niagara_user_parameter",
                {
                    "system_path": system_path,
                    "parameter_name": parameter_name,
                    "value": value,
                    "allow_source_edit": allow_source_edit,
                    "save": save,
                },
            )
        except Exception as e:
            error_msg = f"Error setting Niagara user parameter: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_niagara_stack(
        ctx: Context,
        system_path: str,
        include_pins: bool = False,
        max_function_calls: int = 200,
    ) -> Dict[str, Any]:
        """
        Inspect Niagara System, emitter, and scratch-pad stack function calls.

        Args:
            system_path: Niagara System package path or object path
            include_pins: Include function call pin metadata
            max_function_calls: Maximum function calls per script/graph
        """
        try:
            return send_niagara_command(
                "inspect_niagara_stack",
                {
                    "system_path": system_path,
                    "include_pins": include_pins,
                    "max_function_calls": max_function_calls,
                },
            )
        except Exception as e:
            error_msg = f"Error inspecting Niagara stack: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_niagara_graph(
        ctx: Context,
        system_path: str,
        include_pins: bool = True,
        include_links: bool = True,
        include_scratch_pads: bool = True,
        max_nodes_per_graph: int = 600,
        max_links_per_graph: int = 2000,
    ) -> Dict[str, Any]:
        """
        Inspect full Niagara graph nodes, pins, links, and scratch-pad graphs.

        Args:
            system_path: Niagara System package path or object path
            include_pins: Include pin metadata on each graph node
            include_links: Include explicit graph links and linked pin refs
            include_scratch_pads: Include system, emitter, and parent scratch pads
            max_nodes_per_graph: Maximum nodes returned per graph
            max_links_per_graph: Maximum links returned per graph
        """
        try:
            return send_niagara_command(
                "inspect_niagara_graph",
                {
                    "system_path": system_path,
                    "include_pins": include_pins,
                    "include_links": include_links,
                    "include_scratch_pads": include_scratch_pads,
                    "max_nodes_per_graph": max_nodes_per_graph,
                    "max_links_per_graph": max_links_per_graph,
                },
            )
        except Exception as e:
            error_msg = f"Error inspecting Niagara graph: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_niagara_scratch_pad_interface(
        ctx: Context,
        system_path: str,
        include_graph_summary: bool = True,
        include_parent_scratch_pads: bool = True,
        max_scripts: int = 200,
        max_function_calls: int = 80,
    ) -> Dict[str, Any]:
        """
        Inspect Scratch Pad scripts as read-only authoring interfaces.

        Args:
            system_path: Niagara System package path or object path
            include_graph_summary: Include compact function-call/input/output graph summary per Scratch Pad
            include_parent_scratch_pads: Include inherited parent-emitter Scratch Pads
            max_scripts: Maximum Scratch Pad scripts to return
            max_function_calls: Maximum function calls per Scratch Pad graph summary
        """
        try:
            return send_niagara_command(
                "inspect_niagara_scratch_pad_interface",
                {
                    "system_path": system_path,
                    "include_graph_summary": include_graph_summary,
                    "include_parent_scratch_pads": include_parent_scratch_pads,
                    "max_scripts": max_scripts,
                    "max_function_calls": max_function_calls,
                },
            )
        except Exception as e:
            error_msg = f"Error inspecting Niagara scratch pad interface: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def duplicate_or_attach_emitter_from_source(
        ctx: Context,
        target_system_path: str,
        source_emitter_path: str = "",
        source_system_path: str = "",
        source_emitter_index: int | None = None,
        source_emitter_name: str = "",
        new_emitter_name: str = "",
        enabled: bool | None = None,
        allow_source_edit: bool = False,
        save: bool = True,
        request_compile: bool = True,
    ) -> Dict[str, Any]:
        """
        Duplicate or attach a source Niagara emitter into a target temp Niagara System.

        Args:
            target_system_path: Target Niagara System package path or object path
            source_emitter_path: Optional source Niagara Emitter asset path
            source_system_path: Optional source Niagara System path when copying one of its emitter handles
            source_emitter_index: Optional source emitter index for source_system_path
            source_emitter_name: Optional source emitter display name for source_system_path
            new_emitter_name: Optional desired display name for the new target emitter
            enabled: Optional enabled-state override for the new target emitter
            allow_source_edit: Allow editing target systems outside /Game/_MCP_Temp/NiagaraGenerated/
            save: Save the target system after attaching the emitter
            request_compile: Request Niagara compile after attaching the emitter
        """
        try:
            params: Dict[str, Any] = {
                "target_system_path": target_system_path,
                "source_emitter_path": source_emitter_path,
                "source_system_path": source_system_path,
                "source_emitter_name": source_emitter_name,
                "new_emitter_name": new_emitter_name,
                "allow_source_edit": allow_source_edit,
                "save": save,
                "request_compile": request_compile,
            }
            if source_emitter_index is not None:
                params["source_emitter_index"] = source_emitter_index
            if enabled is not None:
                params["enabled"] = enabled
            return send_niagara_command("duplicate_or_attach_emitter_from_source", params)
        except Exception as e:
            error_msg = f"Error duplicating or attaching Niagara emitter: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def create_or_duplicate_scratch_pad_module(
        ctx: Context,
        target_system_path: str,
        source_script_path: str = "",
        source_system_path: str = "",
        source_owner_kind: str = "system",
        source_script_index: int | None = None,
        source_scratch_pad_name: str = "",
        source_emitter_index: int | None = None,
        source_emitter_name: str = "",
        target_owner_kind: str = "system",
        target_emitter_index: int | None = None,
        target_emitter_name: str = "",
        new_script_name: str = "",
        allow_source_edit: bool = False,
        save: bool = True,
        request_compile: bool = True,
    ) -> Dict[str, Any]:
        """
        Duplicate an existing Scratch Pad script into a target temp Niagara System or emitter.

        Args:
            target_system_path: Target Niagara System package path or object path
            source_script_path: Optional direct Scratch Pad script object path
            source_system_path: Optional source Niagara System path when selecting by owner/index/name
            source_owner_kind: Source owner kind: system, emitter, parent_emitter
            source_script_index: Optional source Scratch Pad script index
            source_scratch_pad_name: Optional source Scratch Pad script name
            source_emitter_index: Optional source emitter index for emitter-owned Scratch Pads
            source_emitter_name: Optional source emitter name for emitter-owned Scratch Pads
            target_owner_kind: Target owner kind: system or emitter
            target_emitter_index: Optional target emitter index when target_owner_kind is emitter
            target_emitter_name: Optional target emitter name when target_owner_kind is emitter
            new_script_name: Optional desired name for the duplicated Scratch Pad script
            allow_source_edit: Allow editing target systems outside /Game/_MCP_Temp/NiagaraGenerated/
            save: Save the target system after duplicating the Scratch Pad
            request_compile: Request Niagara compile after duplicating the Scratch Pad
        """
        try:
            params: Dict[str, Any] = {
                "target_system_path": target_system_path,
                "source_script_path": source_script_path,
                "source_system_path": source_system_path,
                "source_owner_kind": source_owner_kind,
                "source_scratch_pad_name": source_scratch_pad_name,
                "source_emitter_name": source_emitter_name,
                "target_owner_kind": target_owner_kind,
                "target_emitter_name": target_emitter_name,
                "new_script_name": new_script_name,
                "allow_source_edit": allow_source_edit,
                "save": save,
                "request_compile": request_compile,
            }
            if source_script_index is not None:
                params["source_script_index"] = source_script_index
            if source_emitter_index is not None:
                params["source_emitter_index"] = source_emitter_index
            if target_emitter_index is not None:
                params["target_emitter_index"] = target_emitter_index
            return send_niagara_command("create_or_duplicate_scratch_pad_module", params)
        except Exception as e:
            error_msg = f"Error duplicating Niagara Scratch Pad module: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_scratch_pad_module_to_stack(
        ctx: Context,
        target_system_path: str,
        scratch_pad_script_path: str = "",
        scratch_pad_owner_kind: str = "system",
        scratch_pad_script_index: int | None = None,
        scratch_pad_name: str = "",
        scratch_pad_emitter_index: int | None = None,
        scratch_pad_emitter_name: str = "",
        target_usage: str = "ParticleUpdateScript",
        target_usage_id: str = "",
        target_emitter_index: int | None = None,
        target_emitter_name: str = "",
        target_index: int | None = None,
        suggested_name: str = "",
        skip_if_duplicate: bool = True,
        allow_source_edit: bool = False,
        save: bool = True,
        request_compile: bool = True,
    ) -> Dict[str, Any]:
        """
        Insert a target-local Scratch Pad module into a Niagara stack.

        Args:
            target_system_path: Target Niagara System package path or object path
            scratch_pad_script_path: Optional direct Scratch Pad script object path already inside the target system
            scratch_pad_owner_kind: Scratch Pad owner kind: system or emitter
            scratch_pad_script_index: Optional Scratch Pad script index
            scratch_pad_name: Optional Scratch Pad script name
            scratch_pad_emitter_index: Optional emitter index for emitter-owned Scratch Pads
            scratch_pad_emitter_name: Optional emitter name for emitter-owned Scratch Pads
            target_usage: Target stack usage, such as ParticleUpdateScript or EmitterSpawnScript
            target_usage_id: Optional target output usage GUID
            target_emitter_index: Optional target emitter index for emitter/particle stacks
            target_emitter_name: Optional target emitter name for emitter/particle stacks
            target_index: Optional stack insertion index; omit or -1 to append
            suggested_name: Optional suggested module node name
            skip_if_duplicate: Skip without mutation if the same Scratch Pad already exists in the requested output stack
            allow_source_edit: Allow editing target systems outside /Game/_MCP_Temp/NiagaraGenerated/
            save: Save the target system after stack insertion
            request_compile: Request Niagara compile after stack insertion
        """
        try:
            params: Dict[str, Any] = {
                "target_system_path": target_system_path,
                "scratch_pad_script_path": scratch_pad_script_path,
                "scratch_pad_owner_kind": scratch_pad_owner_kind,
                "scratch_pad_name": scratch_pad_name,
                "scratch_pad_emitter_name": scratch_pad_emitter_name,
                "target_usage": target_usage,
                "target_usage_id": target_usage_id,
                "target_emitter_name": target_emitter_name,
                "suggested_name": suggested_name,
                "skip_if_duplicate": skip_if_duplicate,
                "allow_source_edit": allow_source_edit,
                "save": save,
                "request_compile": request_compile,
            }
            if scratch_pad_script_index is not None:
                params["scratch_pad_script_index"] = scratch_pad_script_index
            if scratch_pad_emitter_index is not None:
                params["scratch_pad_emitter_index"] = scratch_pad_emitter_index
            if target_emitter_index is not None:
                params["target_emitter_index"] = target_emitter_index
            if target_index is not None:
                params["target_index"] = target_index
            return send_niagara_command("add_scratch_pad_module_to_stack", params)
        except Exception as e:
            error_msg = f"Error adding Niagara Scratch Pad module to stack: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_niagara_scratch_pad_function_input_default(
        ctx: Context,
        system_path: str,
        function_name: str = "",
        input_pin_name: str = "",
        value: Any | None = None,
        default_value: str = "",
        function_node_guid: str = "",
        function_node_index: int | None = None,
        function_call_index: int | None = None,
        scratch_pad_script_path: str = "",
        scratch_pad_owner_kind: str = "system",
        scratch_pad_script_index: int | None = None,
        scratch_pad_name: str = "",
        scratch_pad_emitter_index: int | None = None,
        scratch_pad_emitter_name: str = "",
        break_links: bool = True,
        allow_multi_link_break: bool = False,
        allow_source_edit: bool = False,
        save: bool = True,
        request_compile: bool = True,
    ) -> Dict[str, Any]:
        """
        Set a Scratch Pad internal function-call input pin default value.

        Args:
            system_path: Niagara System package path or object path
            function_name: Target internal function name, for example SetRenderTargetValue
            input_pin_name: Target function input pin name, for example Value
            value: JSON value converted to a Niagara pin default string
            default_value: Raw Unreal pin default string; takes precedence over value
            function_node_guid: Optional target function node GUID
            function_node_index: Optional graph node index from inspect_niagara_graph
            function_call_index: Optional function-call-only index inside the Scratch Pad graph
            scratch_pad_script_path: Direct target Scratch Pad script path; required unless name or index is provided
            scratch_pad_owner_kind: system or emitter
            scratch_pad_script_index: Scratch Pad script index; required unless path or name is provided
            scratch_pad_name: Scratch Pad script name; required unless path or index is provided
            scratch_pad_emitter_index: Optional emitter index for emitter-owned Scratch Pads
            scratch_pad_emitter_name: Optional emitter name for emitter-owned Scratch Pads
            break_links: Break existing links from the target input pin after setting its default
            allow_multi_link_break: Allow breaking more than one existing link
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System after editing
            request_compile: Request Niagara compile after editing
        """
        try:
            params: Dict[str, Any] = {
                "system_path": system_path,
                "function_name": function_name,
                "function_node_guid": function_node_guid,
                "input_pin_name": input_pin_name,
                "scratch_pad_script_path": scratch_pad_script_path,
                "scratch_pad_owner_kind": scratch_pad_owner_kind,
                "scratch_pad_name": scratch_pad_name,
                "scratch_pad_emitter_name": scratch_pad_emitter_name,
                "break_links": break_links,
                "allow_multi_link_break": allow_multi_link_break,
                "allow_source_edit": allow_source_edit,
                "save": save,
                "request_compile": request_compile,
            }
            if default_value:
                params["default_value"] = default_value
            else:
                params["value"] = value
            if function_node_index is not None:
                params["function_node_index"] = function_node_index
            if function_call_index is not None:
                params["function_call_index"] = function_call_index
            if scratch_pad_script_index is not None:
                params["scratch_pad_script_index"] = scratch_pad_script_index
            if scratch_pad_emitter_index is not None:
                params["scratch_pad_emitter_index"] = scratch_pad_emitter_index
            return send_niagara_command("set_niagara_scratch_pad_function_input_default", params)
        except Exception as e:
            error_msg = f"Error setting Niagara Scratch Pad function input default: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def link_niagara_scratch_pad_pin_to_user_parameter(
        ctx: Context,
        system_path: str,
        target_pin_name: str,
        user_parameter_name: str,
        scratch_pad_script_path: str = "",
        scratch_pad_owner_kind: str = "system",
        scratch_pad_script_index: int | None = None,
        scratch_pad_name: str = "",
        scratch_pad_emitter_index: int | None = None,
        scratch_pad_emitter_name: str = "",
        target_node_guid: str = "",
        target_node_index: int | None = None,
        parameter_map_set_index: int | None = None,
        default_value: Any = None,
        overwrite_existing: bool = False,
        allow_multi_link_break: bool = False,
        allow_source_edit: bool = False,
        save: bool = True,
        request_compile: bool = True,
    ) -> Dict[str, Any]:
        """
        Link a Scratch Pad ParameterMapSet input pin to a Vector2D User parameter.

        Args:
            system_path: Niagara System package path or object path
            target_pin_name: Target ParameterMapSet input pin, e.g. Local.Module.AdvectionAmount
            user_parameter_name: User parameter name, with or without User. prefix
            scratch_pad_script_path: Direct target Scratch Pad script path; required unless name or index is provided
            scratch_pad_owner_kind: system or emitter
            scratch_pad_script_index: Scratch Pad script index; required unless path or name is provided
            scratch_pad_name: Scratch Pad script name; required unless path or index is provided
            scratch_pad_emitter_index: Optional emitter index for emitter-owned Scratch Pads
            scratch_pad_emitter_name: Optional emitter name for emitter-owned Scratch Pads
            target_node_guid: Optional target ParameterMapSet node GUID
            target_node_index: Optional graph node index from inspect_niagara_graph
            parameter_map_set_index: Optional ParameterMapSet-only index in the Scratch Pad graph
            default_value: Optional Vector2D default value such as [0, 0]
            overwrite_existing: Replace existing links on the target pin
            allow_multi_link_break: Allow breaking more than one existing link
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System after editing
            request_compile: Request Niagara compile after editing
        """
        try:
            params: Dict[str, Any] = {
                "system_path": system_path,
                "target_pin_name": target_pin_name,
                "user_parameter_name": user_parameter_name,
                "scratch_pad_script_path": scratch_pad_script_path,
                "scratch_pad_owner_kind": scratch_pad_owner_kind,
                "scratch_pad_name": scratch_pad_name,
                "scratch_pad_emitter_name": scratch_pad_emitter_name,
                "target_node_guid": target_node_guid,
                "overwrite_existing": overwrite_existing,
                "allow_multi_link_break": allow_multi_link_break,
                "allow_source_edit": allow_source_edit,
                "save": save,
                "request_compile": request_compile,
            }
            if scratch_pad_script_index is not None:
                params["scratch_pad_script_index"] = scratch_pad_script_index
            if scratch_pad_emitter_index is not None:
                params["scratch_pad_emitter_index"] = scratch_pad_emitter_index
            if target_node_index is not None:
                params["target_node_index"] = target_node_index
            if parameter_map_set_index is not None:
                params["parameter_map_set_index"] = parameter_map_set_index
            if default_value is not None:
                params["default_value"] = default_value
            return send_niagara_command("link_niagara_scratch_pad_pin_to_user_parameter", params)
        except Exception as e:
            error_msg = f"Error linking Niagara Scratch Pad pin to User parameter: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def wrap_niagara_scratch_pad_output_with_stack_context(
        ctx: Context,
        system_path: str,
        target_pin_name: str = "StackContext.RGBA",
        scratch_pad_script_path: str = "",
        scratch_pad_owner_kind: str = "system",
        scratch_pad_script_index: int | None = None,
        scratch_pad_name: str = "RenderCircleToGrid",
        scratch_pad_emitter_index: int | None = None,
        scratch_pad_emitter_name: str = "",
        target_node_guid: str = "",
        target_node_index: int | None = None,
        parameter_map_set_index: int | None = None,
        previous_stack_value_pin_name: str = "PreviousStackValue",
        local_value_pin_name: str = "LocalStampValue",
        expression: str = "max(PreviousStackValue, LocalStampValue)",
        skip_if_already_wrapped: bool = True,
        replace_existing_custom: bool = True,
        allow_source_edit: bool = False,
        save: bool = True,
        request_compile: bool = True,
    ) -> Dict[str, Any]:
        """
        Wrap a Scratch Pad ParameterMapSet value input with a Custom HLSL accumulator.

        The existing linked value becomes local_value_pin_name, while the expression can
        read the incoming StackContext through the dynamic input's ParameterMap.

        Args:
            system_path: Niagara System package path or object path
            target_pin_name: ParameterMapSet input pin to wrap, defaults to StackContext.RGBA
            scratch_pad_script_path: Direct target Scratch Pad script path
            scratch_pad_owner_kind: system or emitter
            scratch_pad_script_index: Scratch Pad script index
            scratch_pad_name: Scratch Pad script name, defaults to RenderCircleToGrid
            scratch_pad_emitter_index: Optional emitter index for emitter-owned Scratch Pads
            scratch_pad_emitter_name: Optional emitter name for emitter-owned Scratch Pads
            target_node_guid: Optional target ParameterMapSet node GUID
            target_node_index: Optional graph node index from inspect_niagara_graph
            parameter_map_set_index: Optional ParameterMapSet-only index in the Scratch Pad graph
            previous_stack_value_pin_name: Custom HLSL input name for the incoming StackContext value
            local_value_pin_name: Custom HLSL input name for the previous linked value
            expression: Dynamic Custom HLSL expression, defaults to max(PreviousStackValue, LocalStampValue)
            skip_if_already_wrapped: Return success when the same Custom HLSL wrapper already exists
            replace_existing_custom: Replace an existing Custom HLSL wrapper while preserving local_value_pin_name
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System after editing
            request_compile: Request Niagara compile after editing
        """
        try:
            params: Dict[str, Any] = {
                "system_path": system_path,
                "target_pin_name": target_pin_name,
                "scratch_pad_script_path": scratch_pad_script_path,
                "scratch_pad_owner_kind": scratch_pad_owner_kind,
                "scratch_pad_name": scratch_pad_name,
                "scratch_pad_emitter_name": scratch_pad_emitter_name,
                "target_node_guid": target_node_guid,
                "previous_stack_value_pin_name": previous_stack_value_pin_name,
                "local_value_pin_name": local_value_pin_name,
                "expression": expression,
                "skip_if_already_wrapped": skip_if_already_wrapped,
                "replace_existing_custom": replace_existing_custom,
                "allow_source_edit": allow_source_edit,
                "save": save,
                "request_compile": request_compile,
            }
            if scratch_pad_script_index is not None:
                params["scratch_pad_script_index"] = scratch_pad_script_index
            if scratch_pad_emitter_index is not None:
                params["scratch_pad_emitter_index"] = scratch_pad_emitter_index
            if target_node_index is not None:
                params["target_node_index"] = target_node_index
            if parameter_map_set_index is not None:
                params["parameter_map_set_index"] = parameter_map_set_index
            return send_niagara_command("wrap_niagara_scratch_pad_output_with_stack_context", params)
        except Exception as e:
            error_msg = f"Error wrapping Niagara Scratch Pad output with StackContext accumulator: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def insert_niagara_scratch_pad_custom_hlsl_for_pin(
        ctx: Context,
        system_path: str,
        target_pin_name: str,
        expression: str,
        scratch_pad_script_path: str = "",
        scratch_pad_owner_kind: str = "system",
        scratch_pad_script_index: int | None = None,
        scratch_pad_name: str = "RenderGrid",
        scratch_pad_emitter_index: int | None = None,
        scratch_pad_emitter_name: str = "",
        target_node_guid: str = "",
        target_node_name: str = "",
        target_node_index: int | None = None,
        preserve_existing_link_as: str = "BaseValue",
        output_pin_name: str = "CustomHLSLOutput",
        signature_name: str = "IF_CustomPinValue",
        inputs: list[dict[str, Any]] | None = None,
        user_parameter_inputs: list[dict[str, Any]] | None = None,
        skip_if_already_inserted: bool = True,
        replace_existing_custom: bool = False,
        rebuild_existing_custom: bool = False,
        requires_context: bool = False,
        delete_unlinked_custom_nodes: bool = False,
        delete_unlinked_custom_input_source_nodes: bool = False,
        allow_source_edit: bool = False,
        save: bool = True,
        request_compile: bool = True,
    ) -> Dict[str, Any]:
        """
        Insert or replace a Custom HLSL dynamic input for a Scratch Pad input pin.

        Args:
            system_path: Niagara System package path or object path
            target_pin_name: Target input pin to wrap with Custom HLSL
            expression: Custom HLSL expression body
            scratch_pad_script_path: Direct target Scratch Pad script path
            scratch_pad_owner_kind: system or emitter
            scratch_pad_script_index: Scratch Pad script index
            scratch_pad_name: Scratch Pad script name, defaults to RenderGrid
            scratch_pad_emitter_index: Optional emitter index for emitter-owned Scratch Pads
            scratch_pad_emitter_name: Optional emitter name for emitter-owned Scratch Pads
            target_node_guid: Optional target node GUID
            target_node_name: Optional target node name
            target_node_index: Optional target graph node index
            preserve_existing_link_as: Custom input name for the existing target-pin value link
            output_pin_name: Custom HLSL output pin name
            signature_name: Custom HLSL function signature name
            inputs: Extra inputs linked from existing Scratch Pad graph pins
            user_parameter_inputs: Extra inputs created from User.* ParameterMapGet nodes
            skip_if_already_inserted: Return success when the same expression is already present
            replace_existing_custom: Replace an existing Custom HLSL wrapper
            rebuild_existing_custom: Preserve the existing base-value input when replacing a Custom node
            requires_context: Mark the Custom HLSL signature as context-requiring
            delete_unlinked_custom_nodes: Delete unlinked Custom HLSL nodes after insertion
            delete_unlinked_custom_input_source_nodes: Delete now-unlinked input source nodes that belonged to the replaced Custom node
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System after editing
            request_compile: Request Niagara compile after editing
        """
        try:
            params: Dict[str, Any] = {
                "system_path": system_path,
                "target_pin_name": target_pin_name,
                "expression": expression,
                "scratch_pad_script_path": scratch_pad_script_path,
                "scratch_pad_owner_kind": scratch_pad_owner_kind,
                "scratch_pad_name": scratch_pad_name,
                "scratch_pad_emitter_name": scratch_pad_emitter_name,
                "target_node_guid": target_node_guid,
                "target_node_name": target_node_name,
                "preserve_existing_link_as": preserve_existing_link_as,
                "output_pin_name": output_pin_name,
                "signature_name": signature_name,
                "skip_if_already_inserted": skip_if_already_inserted,
                "replace_existing_custom": replace_existing_custom,
                "rebuild_existing_custom": rebuild_existing_custom,
                "requires_context": requires_context,
                "delete_unlinked_custom_nodes": delete_unlinked_custom_nodes,
                "delete_unlinked_custom_input_source_nodes": delete_unlinked_custom_input_source_nodes,
                "allow_source_edit": allow_source_edit,
                "save": save,
                "request_compile": request_compile,
            }
            if scratch_pad_script_index is not None:
                params["scratch_pad_script_index"] = scratch_pad_script_index
            if scratch_pad_emitter_index is not None:
                params["scratch_pad_emitter_index"] = scratch_pad_emitter_index
            if target_node_index is not None:
                params["target_node_index"] = target_node_index
            if inputs is not None:
                params["inputs"] = inputs
            if user_parameter_inputs is not None:
                params["user_parameter_inputs"] = user_parameter_inputs
            return send_niagara_command("insert_niagara_scratch_pad_custom_hlsl_for_pin", params)
        except Exception as e:
            error_msg = f"Error inserting Niagara Scratch Pad Custom HLSL for pin: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_niagara_compile_status(
        ctx: Context,
        system_path: str,
        request_compile: bool = False,
        force: bool = False,
        allow_source_compile: bool = False,
        wait_for_completion: bool = False,
        timeout_seconds: float = 10.0,
        poll_interval_seconds: float = 0.1,
    ) -> Dict[str, Any]:
        """
        Inspect Niagara script compile status and outstanding compile requests.

        Args:
            system_path: Niagara System package path or object path
            request_compile: Request a compile before returning status
            force: Force compile when request_compile is true
            allow_source_compile: Allow compile requests outside /Game/_MCP_Temp/NiagaraGenerated/
            wait_for_completion: Poll outstanding compile requests before returning
            timeout_seconds: Maximum wait time when wait_for_completion is true
            poll_interval_seconds: Poll interval when wait_for_completion is true
        """
        try:
            return send_niagara_command(
                "inspect_niagara_compile_status",
                {
                    "system_path": system_path,
                    "request_compile": request_compile,
                    "force": force,
                    "allow_source_compile": allow_source_compile,
                    "wait_for_completion": wait_for_completion,
                    "timeout_seconds": timeout_seconds,
                    "poll_interval_seconds": poll_interval_seconds,
                },
            )
        except Exception as e:
            error_msg = f"Error inspecting Niagara compile status: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_niagara_simulation_stages(
        ctx: Context,
        system_path: str,
        include_compile_data: bool = True,
        include_script_compile_status: bool = True,
        max_stages: int = 128,
    ) -> Dict[str, Any]:
        """
        Inspect Niagara SimulationStage settings and compiled stage data.

        Args:
            system_path: Niagara System package path or object path
            include_compile_data: Include FillCompilationData output for generic stages
            include_script_compile_status: Include per-stage script compile status
            max_stages: Maximum SimulationStages to include across all emitters
        """
        try:
            return send_niagara_command(
                "inspect_niagara_simulation_stages",
                {
                    "system_path": system_path,
                    "include_compile_data": include_compile_data,
                    "include_script_compile_status": include_script_compile_status,
                    "max_stages": max_stages,
                },
            )
        except Exception as e:
            error_msg = f"Error inspecting Niagara simulation stages: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_niagara_simulation_stage_settings(
        ctx: Context,
        system_path: str,
        emitter_index: int | None = None,
        emitter_name: str = "",
        stage_index: int | None = None,
        stage_name: str = "",
        enabled: bool | None = None,
        iteration_source: str = "",
        direct_dispatch_type: str = "",
        direct_dispatch_element_type: str = "",
        execute_behavior: str = "",
        element_count: list[int] | None = None,
        element_count_x: int | None = None,
        element_count_y: int | None = None,
        element_count_z: int | None = None,
        num_iterations: int | None = None,
        gpu_dispatch_force_linear: bool | None = None,
        override_gpu_dispatch_num_threads: bool | None = None,
        allow_source_edit: bool = False,
        save: bool = True,
        request_compile: bool = True,
    ) -> Dict[str, Any]:
        """
        Edit a target-local Niagara generic SimulationStage setting.

        Args:
            system_path: Niagara System package path or object path
            emitter_index: Optional target emitter index
            emitter_name: Optional target emitter name
            stage_index: Optional SimulationStage index
            stage_name: Optional SimulationStage name
            enabled: Optional stage enabled state
            iteration_source: Optional Particles, DataInterface, or DirectSet
            direct_dispatch_type: Optional OneD, TwoD, or ThreeD
            direct_dispatch_element_type: Optional NumThreads, NumThreadsNoClipping, or NumGroups
            execute_behavior: Optional Always, OnSimulationReset, or NotOnSimulationReset
            element_count: Optional 1-3 integer array for direct dispatch
            element_count_x: Optional direct dispatch element count X
            element_count_y: Optional direct dispatch element count Y
            element_count_z: Optional direct dispatch element count Z
            num_iterations: Optional number of stage iterations
            gpu_dispatch_force_linear: Optional force-linear GPU dispatch flag
            override_gpu_dispatch_num_threads: Optional custom thread-group override flag
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System after editing
            request_compile: Request Niagara compile after editing
        """
        try:
            params: Dict[str, Any] = {
                "system_path": system_path,
                "emitter_name": emitter_name,
                "stage_name": stage_name,
                "allow_source_edit": allow_source_edit,
                "save": save,
                "request_compile": request_compile,
            }
            if emitter_index is not None:
                params["emitter_index"] = emitter_index
            if stage_index is not None:
                params["stage_index"] = stage_index
            if enabled is not None:
                params["enabled"] = enabled
            if iteration_source:
                params["iteration_source"] = iteration_source
            if direct_dispatch_type:
                params["direct_dispatch_type"] = direct_dispatch_type
            if direct_dispatch_element_type:
                params["direct_dispatch_element_type"] = direct_dispatch_element_type
            if execute_behavior:
                params["execute_behavior"] = execute_behavior
            if element_count is not None:
                params["element_count"] = element_count
            if element_count_x is not None:
                params["element_count_x"] = element_count_x
            if element_count_y is not None:
                params["element_count_y"] = element_count_y
            if element_count_z is not None:
                params["element_count_z"] = element_count_z
            if num_iterations is not None:
                params["num_iterations"] = num_iterations
            if gpu_dispatch_force_linear is not None:
                params["gpu_dispatch_force_linear"] = gpu_dispatch_force_linear
            if override_gpu_dispatch_num_threads is not None:
                params["override_gpu_dispatch_num_threads"] = override_gpu_dispatch_num_threads
            return send_niagara_command("set_niagara_simulation_stage_settings", params)
        except Exception as e:
            error_msg = f"Error setting Niagara simulation stage settings: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_niagara_module_inputs(
        ctx: Context,
        system_path: str,
        include_linked_sources: bool = True,
        include_resolved_stack_inputs: bool = False,
        max_modules: int = 200,
        max_candidates_per_module: int = 24,
        max_resolved_inputs_per_module: int = 8,
        max_top_candidates: int = 80,
    ) -> Dict[str, Any]:
        """
        Inspect Niagara module input candidates for generation planning.

        Args:
            system_path: Niagara System package path or object path
            include_linked_sources: Include linked script/source metadata
            include_resolved_stack_inputs: Include resolved stack input values
            max_modules: Maximum modules to inspect per emitter
            max_candidates_per_module: Maximum editable-looking candidates per module
            max_resolved_inputs_per_module: Maximum resolved inputs per module
            max_top_candidates: Maximum prioritized candidates in the top list
        """
        try:
            return send_niagara_command(
                "inspect_niagara_module_inputs",
                {
                    "system_path": system_path,
                    "include_linked_sources": include_linked_sources,
                    "include_resolved_stack_inputs": include_resolved_stack_inputs,
                    "max_modules": max_modules,
                    "max_candidates_per_module": max_candidates_per_module,
                    "max_resolved_inputs_per_module": max_resolved_inputs_per_module,
                    "max_top_candidates": max_top_candidates,
                },
            )
        except Exception as e:
            error_msg = f"Error inspecting Niagara module inputs: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_niagara_data_interface_overrides(
        ctx: Context,
        system_path: str,
        input_name: str = "",
        emitter_index: int | None = None,
        emitter_name: str = "",
        module_index: int | None = None,
        module_name: str = "",
        module_node_guid: str = "",
        max_modules: int = 200,
        max_inputs_per_module: int = 64,
        include_data_interface_properties: bool = False,
        max_data_interface_properties: int = 120,
        max_data_interface_property_value_length: int = 512,
    ) -> Dict[str, Any]:
        """
        Inspect Niagara Data Interface module input overrides and User object bindings.

        Args:
            system_path: Niagara System package path or object path
            input_name: Optional module input name filter, with or without the Module. prefix
            emitter_index: Optional target emitter index
            emitter_name: Optional target emitter name
            module_index: Optional target module index from inspect_niagara_module_inputs
            module_name: Optional target module name
            module_node_guid: Optional target module node GUID
            max_modules: Maximum matching modules to include per emitter
            max_inputs_per_module: Maximum Data Interface inputs to include per module
            include_data_interface_properties: Include reflected editable Data Interface properties
            max_data_interface_properties: Maximum reflected Data Interface properties to include
            max_data_interface_property_value_length: Maximum reflected property value string length
        """
        try:
            params: Dict[str, Any] = {
                "system_path": system_path,
                "input_name": input_name,
                "emitter_name": emitter_name,
                "module_name": module_name,
                "module_node_guid": module_node_guid,
                "max_modules": max_modules,
                "max_inputs_per_module": max_inputs_per_module,
                "include_data_interface_properties": include_data_interface_properties,
                "max_data_interface_properties": max_data_interface_properties,
                "max_data_interface_property_value_length": max_data_interface_property_value_length,
            }
            if emitter_index is not None:
                params["emitter_index"] = emitter_index
            if module_index is not None:
                params["module_index"] = module_index
            return send_niagara_command("inspect_niagara_data_interface_overrides", params)
        except Exception as e:
            error_msg = f"Error inspecting Niagara data interface overrides: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_niagara_module_input_value(
        ctx: Context,
        system_path: str,
        input_name: str,
        value: Any,
        emitter_index: int | None = None,
        emitter_name: str = "",
        module_index: int | None = None,
        module_name: str = "",
        module_node_guid: str = "",
        allow_source_edit: bool = False,
        save: bool = True,
    ) -> Dict[str, Any]:
        """
        Set an existing Niagara RapidIteration module input override.

        Args:
            system_path: Niagara System package path or object path
            input_name: Module input name, with or without the Module. prefix
            value: New JSON value. Only existing RapidIteration values are edited.
            emitter_index: Optional target emitter index
            emitter_name: Optional target emitter name
            module_index: Optional target module index from inspect_niagara_module_inputs
            module_name: Optional target module name
            module_node_guid: Optional target module node GUID
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System after editing
        """
        try:
            params: Dict[str, Any] = {
                "system_path": system_path,
                "input_name": input_name,
                "value": value,
                "emitter_name": emitter_name,
                "module_name": module_name,
                "module_node_guid": module_node_guid,
                "allow_source_edit": allow_source_edit,
                "save": save,
            }
            if emitter_index is not None:
                params["emitter_index"] = emitter_index
            if module_index is not None:
                params["module_index"] = module_index
            return send_niagara_command("set_niagara_module_input_value", params)
        except Exception as e:
            error_msg = f"Error setting Niagara module input value: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def create_niagara_module_input_override(
        ctx: Context,
        system_path: str,
        input_name: str,
        value: Any,
        emitter_index: int | None = None,
        emitter_name: str = "",
        module_index: int | None = None,
        module_name: str = "",
        module_node_guid: str = "",
        overwrite_existing: bool = False,
        allow_source_edit: bool = False,
        save: bool = True,
    ) -> Dict[str, Any]:
        """
        Create a missing Niagara RapidIteration module input override.

        Args:
            system_path: Niagara System package path or object path
            input_name: Module input name, with or without the Module. prefix
            value: Initial JSON value for the new override
            emitter_index: Optional target emitter index
            emitter_name: Optional target emitter name
            module_index: Optional target module index from inspect_niagara_module_inputs
            module_name: Optional target module name
            module_node_guid: Optional target module node GUID
            overwrite_existing: Allow replacing an existing override
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System after editing
        """
        try:
            params: Dict[str, Any] = {
                "system_path": system_path,
                "input_name": input_name,
                "value": value,
                "emitter_name": emitter_name,
                "module_name": module_name,
                "module_node_guid": module_node_guid,
                "overwrite_existing": overwrite_existing,
                "allow_source_edit": allow_source_edit,
                "save": save,
            }
            if emitter_index is not None:
                params["emitter_index"] = emitter_index
            if module_index is not None:
                params["module_index"] = module_index
            return send_niagara_command("create_niagara_module_input_override", params)
        except Exception as e:
            error_msg = f"Error creating Niagara module input override: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_niagara_render_target2d_module_input(
        ctx: Context,
        system_path: str,
        input_name: str,
        user_parameter_name: str = "User.RT_IF_Deform",
        render_target_asset_path: str = "",
        emitter_index: int | None = None,
        emitter_name: str = "",
        module_index: int | None = None,
        module_name: str = "",
        module_node_guid: str = "",
        inherit_user_parameter_settings: bool = True,
        overwrite_existing: bool = False,
        allow_source_edit: bool = False,
        save: bool = True,
        request_compile: bool = True,
    ) -> Dict[str, Any]:
        """
        Bind a Niagara RenderTarget2D data-interface module input to a User render target parameter.

        Args:
            system_path: Niagara System package path or object path
            input_name: RenderTarget2D module input name, with or without the Module. prefix
            user_parameter_name: User render target parameter, default User.RT_IF_Deform
            render_target_asset_path: Optional TextureRenderTarget asset to store as the User parameter default
            emitter_index: Optional target emitter index
            emitter_name: Optional target emitter name
            module_index: Optional target module index from inspect_niagara_module_inputs
            module_name: Optional target module name
            module_node_guid: Optional target module node GUID
            inherit_user_parameter_settings: Use size/format/settings from the User render target asset
            overwrite_existing: Replace an existing linked override for the module input
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System after editing
            request_compile: Request Niagara compile after editing
        """
        try:
            params: Dict[str, Any] = {
                "system_path": system_path,
                "input_name": input_name,
                "user_parameter_name": user_parameter_name,
                "render_target_asset_path": render_target_asset_path,
                "emitter_name": emitter_name,
                "module_name": module_name,
                "module_node_guid": module_node_guid,
                "inherit_user_parameter_settings": inherit_user_parameter_settings,
                "overwrite_existing": overwrite_existing,
                "allow_source_edit": allow_source_edit,
                "save": save,
                "request_compile": request_compile,
            }
            if emitter_index is not None:
                params["emitter_index"] = emitter_index
            if module_index is not None:
                params["module_index"] = module_index
            return send_niagara_command("set_niagara_render_target2d_module_input", params)
        except Exception as e:
            error_msg = f"Error binding Niagara RenderTarget2D module input: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_niagara_module_input_user_parameter(
        ctx: Context,
        system_path: str,
        input_name: str,
        user_parameter_name: str,
        default_value: Any | None = None,
        emitter_index: int | None = None,
        emitter_name: str = "",
        module_index: int | None = None,
        module_name: str = "",
        module_node_guid: str = "",
        overwrite_existing: bool = False,
        allow_source_edit: bool = False,
        save: bool = True,
        request_compile: bool = True,
    ) -> Dict[str, Any]:
        """
        Bind a Niagara scalar/vector/color/bool module input to a User parameter.

        Args:
            system_path: Niagara System package path or object path
            input_name: Module input name, with or without the Module. prefix
            user_parameter_name: User parameter name, with or without the User. prefix
            default_value: Optional default value for the User parameter
            emitter_index: Optional target emitter index
            emitter_name: Optional target emitter name
            module_index: Optional target module index from inspect_niagara_module_inputs
            module_name: Optional target module name
            module_node_guid: Optional target module node GUID
            overwrite_existing: Replace an existing linked override for the module input
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System after editing
            request_compile: Request Niagara compile after editing
        """
        try:
            params: Dict[str, Any] = {
                "system_path": system_path,
                "input_name": input_name,
                "user_parameter_name": user_parameter_name,
                "emitter_name": emitter_name,
                "module_name": module_name,
                "module_node_guid": module_node_guid,
                "overwrite_existing": overwrite_existing,
                "allow_source_edit": allow_source_edit,
                "save": save,
                "request_compile": request_compile,
            }
            if default_value is not None:
                params["default_value"] = default_value
            if emitter_index is not None:
                params["emitter_index"] = emitter_index
            if module_index is not None:
                params["module_index"] = module_index
            return send_niagara_command("set_niagara_module_input_user_parameter", params)
        except Exception as e:
            error_msg = f"Error binding Niagara module input to User parameter: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_niagara_module_input_linked_parameter(
        ctx: Context,
        system_path: str,
        input_name: str,
        linked_parameter_name: str,
        emitter_index: int | None = None,
        emitter_name: str = "",
        module_index: int | None = None,
        module_name: str = "",
        module_node_guid: str = "",
        overwrite_existing: bool = False,
        allow_source_edit: bool = False,
        save: bool = True,
        request_compile: bool = True,
    ) -> Dict[str, Any]:
        """
        Link a Niagara module input to an existing namespaced Niagara parameter.

        Args:
            system_path: Niagara System package path or object path
            input_name: Module input name, with or without the Module. prefix
            linked_parameter_name: Existing parameter name, e.g. Emitter.Grid2D Collection
            emitter_index: Optional target emitter index
            emitter_name: Optional target emitter name
            module_index: Optional target module index from inspect_niagara_module_inputs
            module_name: Optional target module name
            module_node_guid: Optional target module node GUID
            overwrite_existing: Replace an existing linked override for the module input
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System after editing
            request_compile: Request Niagara compile after editing
        """
        try:
            params: Dict[str, Any] = {
                "system_path": system_path,
                "input_name": input_name,
                "linked_parameter_name": linked_parameter_name,
                "emitter_name": emitter_name,
                "module_name": module_name,
                "module_node_guid": module_node_guid,
                "overwrite_existing": overwrite_existing,
                "allow_source_edit": allow_source_edit,
                "save": save,
                "request_compile": request_compile,
            }
            if emitter_index is not None:
                params["emitter_index"] = emitter_index
            if module_index is not None:
                params["module_index"] = module_index
            return send_niagara_command("set_niagara_module_input_linked_parameter", params)
        except Exception as e:
            error_msg = f"Error linking Niagara module input to parameter: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_niagara_module_inputs_batch(
        ctx: Context,
        system_path: str,
        edits: list[Dict[str, Any]],
        operation: str = "set_existing",
        overwrite_existing: bool = False,
        continue_on_error: bool = False,
        allow_source_edit: bool = False,
        save: bool = True,
    ) -> Dict[str, Any]:
        """
        Apply multiple Niagara RapidIteration module input edits in one command.

        Args:
            system_path: Niagara System package path or object path
            edits: Edit objects with selectors, input_name, value, and optional operation
            operation: Default operation: set_existing, create_override, or upsert
            overwrite_existing: Default overwrite flag for create/upsert operations
            continue_on_error: Continue processing after an edit failure
            allow_source_edit: Allow edits outside /Game/_MCP_Temp
            save: Save the Niagara System once after successful edits
        """
        try:
            return send_niagara_command(
                "set_niagara_module_inputs_batch",
                {
                    "system_path": system_path,
                    "edits": edits,
                    "operation": operation,
                    "overwrite_existing": overwrite_existing,
                    "continue_on_error": continue_on_error,
                    "allow_source_edit": allow_source_edit,
                    "save": save,
                },
            )
        except Exception as e:
            error_msg = f"Error batch setting Niagara module input values: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    logger.info("Niagara tools registered successfully")
