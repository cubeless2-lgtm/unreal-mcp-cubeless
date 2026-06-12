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
