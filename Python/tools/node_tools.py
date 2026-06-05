"""
Blueprint Node Tools for Unreal MCP.

This module provides tools for manipulating Blueprint graph nodes and connections.
"""

import logging
from typing import Dict, List, Any, Optional
from mcp.server.fastmcp import FastMCP, Context

# Get logger
logger = logging.getLogger("UnrealMCP")

def register_blueprint_node_tools(mcp: FastMCP):
    """Register Blueprint node manipulation tools with the MCP server."""

    def send_node_command(command_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
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

    def add_graph_selector(
        params: Dict[str, Any],
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False,
    ) -> Dict[str, Any]:
        if graph_name:
            params["graph_name"] = graph_name
        if graph_id:
            params["graph_id"] = graph_id
        if graph_type:
            params["graph_type"] = graph_type
        if create_graph_if_missing:
            params["create_graph_if_missing"] = create_graph_if_missing
        return params
    
    @mcp.tool()
    def add_blueprint_event_node(
        ctx: Context,
        blueprint_name: str,
        event_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add an event node to a Blueprint's event graph.
        
        Args:
            blueprint_name: Name of the target Blueprint
            event_name: Name of the event. Use 'Receive' prefix for standard events:
                       - 'ReceiveBeginPlay' for Begin Play
                       - 'ReceiveTick' for Tick
                       - etc.
            node_position: Optional [X, Y] position in the graph
            
        Returns:
            Response containing the node ID and success status
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            # Handle default value within the method body
            if node_position is None:
                node_position = [0, 0]
            
            params = {
                "blueprint_name": blueprint_name,
                "event_name": event_name,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            
            logger.info(f"Adding event node '{event_name}' to blueprint '{blueprint_name}'")
            response = unreal.send_command("add_blueprint_event_node", params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Event node creation response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error adding event node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    @mcp.tool()
    def add_blueprint_input_action_node(
        ctx: Context,
        blueprint_name: str,
        action_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add an input action event node to a Blueprint's event graph.
        
        Args:
            blueprint_name: Name of the target Blueprint
            action_name: Name of the input action to respond to
            node_position: Optional [X, Y] position in the graph
            
        Returns:
            Response containing the node ID and success status
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            # Handle default value within the method body
            if node_position is None:
                node_position = [0, 0]
            
            params = {
                "blueprint_name": blueprint_name,
                "action_name": action_name,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            
            logger.info(f"Adding input action node for '{action_name}' to blueprint '{blueprint_name}'")
            response = unreal.send_command("add_blueprint_input_action_node", params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Input action node creation response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error adding input action node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    @mcp.tool()
    def add_blueprint_function_node(
        ctx: Context,
        blueprint_name: str,
        target: str,
        function_name: str,
        params = None,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a function call node to a Blueprint's event graph.
        
        Args:
            blueprint_name: Name of the target Blueprint
            target: Target object for the function (component name or self)
            function_name: Name of the function to call
            params: Optional parameters to set on the function node
            node_position: Optional [X, Y] position in the graph
            
        Returns:
            Response containing the node ID and success status
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            # Handle default values within the method body
            if params is None:
                params = {}
            if node_position is None:
                node_position = [0, 0]
            
            command_params = {
                "blueprint_name": blueprint_name,
                "target": target,
                "function_name": function_name,
                "params": params,
                "node_position": node_position
            }
            add_graph_selector(command_params, graph_name, graph_id, graph_type, create_graph_if_missing)
            
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            
            logger.info(f"Adding function node '{function_name}' to blueprint '{blueprint_name}'")
            response = unreal.send_command("add_blueprint_function_node", command_params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Function node creation response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error adding function node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_call_function_node(
        ctx: Context,
        blueprint_name: str,
        function_class: str,
        function_name: str,
        param_defaults: Optional[Dict[str, Any]] = None,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False,
        allow_latent: bool = False,
        allow_editor_only: bool = False,
        allow_wildcard: bool = False,
        allow_deprecated: bool = False,
        allow_internal: bool = False,
    ) -> Dict[str, Any]:
        """
        Add a validated Blueprint function call node.

        Args:
            blueprint_name: Blueprint name or path
            function_class: Owner class path/name, preferably /Script/Module.ClassName
            function_name: UFunction name to call
            param_defaults: Optional input pin defaults validated through the K2 schema
            node_position: Optional [X, Y] position in the graph
            allow_latent: Allow latent functions
            allow_editor_only: Allow editor-only functions
            allow_wildcard: Allow wildcard/custom thunk functions
            allow_deprecated: Allow deprecated functions
            allow_internal: Allow Blueprint-internal functions

        Returns:
            Response containing the created node metadata and pins
        """
        try:
            if param_defaults is None:
                param_defaults = {}
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "function_class": function_class,
                "function_name": function_name,
                "param_defaults": param_defaults,
                "node_position": node_position,
                "allow_latent": allow_latent,
                "allow_editor_only": allow_editor_only,
                "allow_wildcard": allow_wildcard,
                "allow_deprecated": allow_deprecated,
                "allow_internal": allow_internal,
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_call_function_node", params)
        except Exception as e:
            error_msg = f"Error adding validated function call node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
            
    @mcp.tool()
    def connect_blueprint_nodes(
        ctx: Context,
        blueprint_name: str,
        source_node_id: str,
        source_pin: str,
        target_node_id: str,
        target_pin: str,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        allow_pin_link_replacement: bool = False
    ) -> Dict[str, Any]:
        """
        Connect two nodes in a Blueprint's event graph.
        
        Args:
            blueprint_name: Name of the target Blueprint
            source_node_id: ID of the source node
            source_pin: Name of the output pin on the source node
            target_node_id: ID of the target node
            target_pin: Name of the input pin on the target node
            
        Returns:
            Response indicating success or failure
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            params = {
                "blueprint_name": blueprint_name,
                "source_node_id": source_node_id,
                "source_pin": source_pin,
                "target_node_id": target_node_id,
                "target_pin": target_pin,
                "allow_pin_link_replacement": allow_pin_link_replacement
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            
            logger.info(f"Connecting nodes in blueprint '{blueprint_name}'")
            response = unreal.send_command("connect_blueprint_nodes", params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Node connection response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error connecting nodes: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    @mcp.tool()
    def add_blueprint_variable(
        ctx: Context,
        blueprint_name: str,
        variable_name: str,
        variable_type: str,
        is_exposed: bool = False,
        default_value: Any = None,
        category: str = "",
        tooltip: str = "",
        friendly_name: str = "",
        type_object: str = "",
        is_array: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Add a variable to a Blueprint.
        
        Args:
            blueprint_name: Name of the target Blueprint
            variable_name: Name of the variable
            variable_type: Type of the variable (Boolean, Integer, Float, Vector, etc.)
            is_exposed: Whether to expose the variable to the editor
            default_value: Optional default value
            category: Optional Blueprint variable category
            tooltip: Optional Blueprint variable tooltip
            friendly_name: Optional display name
            type_object: Optional class path/name for object or class variables
            is_array: Whether to create an array variable
            metadata: Optional Blueprint variable metadata
            
        Returns:
            Response indicating success or failure
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            params = {
                "blueprint_name": blueprint_name,
                "variable_name": variable_name,
                "variable_type": variable_type,
                "is_exposed": is_exposed,
                "is_array": is_array,
            }
            if default_value is not None:
                params["default_value"] = default_value
            if category:
                params["category"] = category
            if tooltip:
                params["tooltip"] = tooltip
            if friendly_name:
                params["friendly_name"] = friendly_name
            if type_object:
                params["type_object"] = type_object
            if metadata:
                params["metadata"] = metadata
            
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            
            logger.info(f"Adding variable '{variable_name}' to blueprint '{blueprint_name}'")
            response = unreal.send_command("add_blueprint_variable", params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Variable creation response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error adding variable: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_function_parameter(
        ctx: Context,
        blueprint_name: str,
        parameter_name: str,
        parameter_type: str,
        direction: str = "input",
        default_value: Any = None,
        type_object: str = "",
        is_array: bool = False,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "function",
        create_graph_if_missing: bool = False,
    ) -> Dict[str, Any]:
        """
        Add an input or output parameter pin to a Blueprint function graph.

        Args:
            blueprint_name: Blueprint name or path
            parameter_name: Function parameter name
            parameter_type: Type descriptor such as bool, int, float, string, vector, object, or class
            direction: input or output
            default_value: Optional default value for the created pin
            type_object: Optional class path/name for object or class parameters
            is_array: Whether to create an array parameter
        """
        try:
            params = {
                "blueprint_name": blueprint_name,
                "parameter_name": parameter_name,
                "parameter_type": parameter_type,
                "direction": direction,
                "is_array": is_array,
            }
            if default_value is not None:
                params["default_value"] = default_value
            if type_object:
                params["type_object"] = type_object
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_function_parameter", params)
        except Exception as e:
            error_msg = f"Error adding function parameter: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_local_variable(
        ctx: Context,
        blueprint_name: str,
        variable_name: str,
        variable_type: str,
        default_value: Any = None,
        category: str = "",
        tooltip: str = "",
        type_object: str = "",
        is_array: bool = False,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "function",
        create_graph_if_missing: bool = False,
    ) -> Dict[str, Any]:
        """
        Add a local variable declaration to a Blueprint function graph.

        Args:
            blueprint_name: Blueprint name or path
            variable_name: Local variable name
            variable_type: Type descriptor such as bool, int, float, string, vector, object, or class
            default_value: Optional default value
            category: Optional local variable category
            tooltip: Optional local variable tooltip
            type_object: Optional class path/name for object or class variables
            is_array: Whether to create an array local variable
        """
        try:
            params = {
                "blueprint_name": blueprint_name,
                "variable_name": variable_name,
                "variable_type": variable_type,
                "is_array": is_array,
            }
            if default_value is not None:
                params["default_value"] = default_value
            if category:
                params["category"] = category
            if tooltip:
                params["tooltip"] = tooltip
            if type_object:
                params["type_object"] = type_object
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_local_variable", params)
        except Exception as e:
            error_msg = f"Error adding local variable: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    @mcp.tool()
    def add_blueprint_get_self_component_reference(
        ctx: Context,
        blueprint_name: str,
        component_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a node that gets a reference to a component owned by the current Blueprint.
        This creates a node similar to what you get when dragging a component from the Components panel.
        
        Args:
            blueprint_name: Name of the target Blueprint
            component_name: Name of the component to get a reference to
            node_position: Optional [X, Y] position in the graph
            
        Returns:
            Response containing the node ID and success status
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            # Handle None case explicitly in the function
            if node_position is None:
                node_position = [0, 0]
            
            params = {
                "blueprint_name": blueprint_name,
                "component_name": component_name,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            
            logger.info(f"Adding self component reference node for '{component_name}' to blueprint '{blueprint_name}'")
            response = unreal.send_command("add_blueprint_get_self_component_reference", params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Self component reference node creation response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error adding self component reference node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    @mcp.tool()
    def add_blueprint_self_reference(
        ctx: Context,
        blueprint_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a 'Get Self' node to a Blueprint's event graph that returns a reference to this actor.
        
        Args:
            blueprint_name: Name of the target Blueprint
            node_position: Optional [X, Y] position in the graph
            
        Returns:
            Response containing the node ID and success status
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            if node_position is None:
                node_position = [0, 0]
                
            params = {
                "blueprint_name": blueprint_name,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            
            logger.info(f"Adding self reference node to blueprint '{blueprint_name}'")
            response = unreal.send_command("add_blueprint_self_reference", params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Self reference node creation response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error adding self reference node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    @mcp.tool()
    def find_blueprint_nodes(
        ctx: Context,
        blueprint_name: str,
        node_type = None,
        event_type = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = ""
    ) -> Dict[str, Any]:
        """
        Find nodes in a Blueprint's event graph.
        
        Args:
            blueprint_name: Name of the target Blueprint
            node_type: Optional type of node to find (Event, Function, Variable, etc.)
            event_type: Optional specific event type to find (BeginPlay, Tick, etc.)
            
        Returns:
            Response containing array of found node IDs and success status
        """
        from unreal_mcp_server import get_unreal_connection
        
        try:
            params = {
                "blueprint_name": blueprint_name,
                "node_type": node_type,
                "event_type": event_type,
                "event_name": event_type
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            
            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}
            
            logger.info(f"Finding nodes in blueprint '{blueprint_name}'")
            response = unreal.send_command("find_blueprint_nodes", params)
            
            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}
            
            logger.info(f"Node find response: {response}")
            return response
            
        except Exception as e:
            error_msg = f"Error finding nodes: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def resolve_blueprint(
        ctx: Context,
        blueprint_name: str
    ) -> Dict[str, Any]:
        """
        Resolve a Blueprint by short name, object path, asset reference, or generated class path.

        Args:
            blueprint_name: Blueprint name or path to resolve

        Returns:
            Response containing the resolved asset path and candidate paths
        """
        try:
            return send_node_command("resolve_blueprint", {"blueprint_name": blueprint_name})
        except Exception as e:
            error_msg = f"Error resolving blueprint: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def list_blueprint_graphs(
        ctx: Context,
        blueprint_name: str,
        graph_type: str = ""
    ) -> Dict[str, Any]:
        """
        List graphs in a Blueprint.

        Args:
            blueprint_name: Blueprint name or path
            graph_type: Optional filter: event, function, macro, delegate, or any

        Returns:
            Response containing graph metadata including graph_id and graph_type
        """
        try:
            params = {
                "blueprint_name": blueprint_name,
                "graph_type": graph_type
            }
            return send_node_command("list_blueprint_graphs", params)
        except Exception as e:
            error_msg = f"Error listing blueprint graphs: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def resolve_blueprint_graph(
        ctx: Context,
        blueprint_name: str,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Resolve or create a Blueprint graph.

        Args:
            blueprint_name: Blueprint name or path
            graph_name: Optional graph name
            graph_id: Optional graph GUID
            graph_type: event, function, macro, delegate, or any
            create_if_missing: Create a missing function graph when graph_type is function

        Returns:
            Response containing graph metadata
        """
        try:
            params = {
                "blueprint_name": blueprint_name,
                "create_if_missing": create_if_missing
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("resolve_blueprint_graph", params)
        except Exception as e:
            error_msg = f"Error resolving blueprint graph: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def list_blueprint_nodes(
        ctx: Context,
        blueprint_name: str,
        node_type: str = "",
        title_contains: str = "",
        include_pins: bool = True,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = ""
    ) -> Dict[str, Any]:
        """
        List nodes in a Blueprint event graph, optionally including pins and links.

        Args:
            blueprint_name: Blueprint name or path
            node_type: Optional class or title substring filter
            title_contains: Optional title substring filter
            include_pins: Include pin metadata and links in the result

        Returns:
            Response containing graph node metadata
        """
        try:
            params = {
                "blueprint_name": blueprint_name,
                "node_type": node_type,
                "title_contains": title_contains,
                "include_pins": include_pins
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("list_blueprint_nodes", params)
        except Exception as e:
            error_msg = f"Error listing blueprint nodes: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_branch_node(
        ctx: Context,
        blueprint_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """Add a Branch node to a Blueprint graph."""
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_branch_node", params)
        except Exception as e:
            error_msg = f"Error adding branch node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_sequence_node(
        ctx: Context,
        blueprint_name: str,
        node_position = None,
        output_count: int = 2,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """Add a Sequence node to a Blueprint graph."""
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "node_position": node_position,
                "output_count": output_count
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_sequence_node", params)
        except Exception as e:
            error_msg = f"Error adding sequence node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_return_node(
        ctx: Context,
        blueprint_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "function",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """Add or resolve a Return node in a Blueprint function graph."""
        try:
            if node_position is None:
                node_position = [320, 0]
            params = {
                "blueprint_name": blueprint_name,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_return_node", params)
        except Exception as e:
            error_msg = f"Error adding return node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_dynamic_cast_node(
        ctx: Context,
        blueprint_name: str,
        target_class: str,
        node_position = None,
        pure: bool = False,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """Add a Dynamic Cast node to a Blueprint graph."""
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "target_class": target_class,
                "node_position": node_position,
                "pure": pure
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_dynamic_cast_node", params)
        except Exception as e:
            error_msg = f"Error adding dynamic cast node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_loop_node(
        ctx: Context,
        blueprint_name: str,
        loop_type: str = "for_loop",
        first_index: Optional[int] = None,
        last_index: Optional[int] = None,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a supported Blueprint loop macro node.

        Section 7 stable scope supports only loop_type="for_loop".
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "loop_type": loop_type,
                "node_position": node_position,
            }
            if first_index is not None:
                params["first_index"] = first_index
            if last_index is not None:
                params["last_index"] = last_index
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_loop_node", params)
        except Exception as e:
            error_msg = f"Error adding loop node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_array_function_node(
        ctx: Context,
        blueprint_name: str,
        operation: str,
        element_type: str,
        param_defaults: Optional[Dict[str, Any]] = None,
        type_object: str = "",
        enum_type: str = "",
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a typed Blueprint array function node.

        Supported operations: length, get, set, add.
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            if param_defaults is None:
                param_defaults = {}
            params = {
                "blueprint_name": blueprint_name,
                "operation": operation,
                "element_type": element_type,
                "param_defaults": param_defaults,
                "node_position": node_position,
            }
            if type_object:
                params["type_object"] = type_object
            if enum_type:
                params["enum_type"] = enum_type
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_array_function_node", params)
        except Exception as e:
            error_msg = f"Error adding array function node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_make_array_node(
        ctx: Context,
        blueprint_name: str,
        element_type: str,
        input_count: Optional[int] = None,
        values: Optional[List[Any]] = None,
        type_object: str = "",
        enum_type: str = "",
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a typed Blueprint Make Array node.

        Creates a 1D array literal with explicit element pin typing.
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "element_type": element_type,
                "node_position": node_position,
            }
            if input_count is not None:
                params["input_count"] = input_count
            if values is not None:
                params["values"] = values
            if type_object:
                params["type_object"] = type_object
            if enum_type:
                params["enum_type"] = enum_type
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_make_array_node", params)
        except Exception as e:
            error_msg = f"Error adding make array node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_input_axis_event_node(
        ctx: Context,
        blueprint_name: str,
        axis_name: str,
        node_position = None,
        consume_input: bool = True,
        execute_when_paused: bool = False,
        override_parent_binding: bool = False,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a legacy input axis event node to a Blueprint event graph.

        Args:
            blueprint_name: Blueprint name or path
            axis_name: Project input axis mapping name
            node_position: Optional [X, Y] position in the graph
            consume_input: Whether this event consumes input
            execute_when_paused: Whether this event runs while paused
            override_parent_binding: Whether parent bindings are overridden

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "axis_name": axis_name,
                "node_position": node_position,
                "consume_input": consume_input,
                "execute_when_paused": execute_when_paused,
                "override_parent_binding": override_parent_binding
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_input_axis_event_node", params)
        except Exception as e:
            error_msg = f"Error adding input axis event node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_enhanced_input_action_node(
        ctx: Context,
        blueprint_name: str,
        input_action: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add an Enhanced Input action event node to a Blueprint event graph.

        Args:
            blueprint_name: Blueprint name or path
            input_action: UInputAction asset path
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "input_action": input_action,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_enhanced_input_action_node", params)
        except Exception as e:
            error_msg = f"Error adding enhanced input action node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_variable_get_node(
        ctx: Context,
        blueprint_name: str,
        variable_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a variable getter node to a Blueprint event graph.

        Args:
            blueprint_name: Blueprint name or path
            variable_name: Variable or component member name
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "variable_name": variable_name,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_variable_get_node", params)
        except Exception as e:
            error_msg = f"Error adding variable get node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_variable_set_node(
        ctx: Context,
        blueprint_name: str,
        variable_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a variable setter node to a Blueprint event graph.

        Args:
            blueprint_name: Blueprint name or path
            variable_name: Variable member name
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "variable_name": variable_name,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_variable_set_node", params)
        except Exception as e:
            error_msg = f"Error adding variable set node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_math_node(
        ctx: Context,
        blueprint_name: str,
        operation: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a Kismet Math Library function node to a Blueprint event graph.

        Args:
            blueprint_name: Blueprint name or path
            operation: add, subtract, multiply, divide, clamp, or in_range
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "operation": operation,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_math_node", params)
        except Exception as e:
            error_msg = f"Error adding math node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_compare_node(
        ctx: Context,
        blueprint_name: str,
        operation: str,
        value_type: str = "double",
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a comparison expression node to a Blueprint graph.

        Args:
            blueprint_name: Blueprint name or path
            operation: less, greater, less_equal, greater_equal, equal, not_equal, or symbolic aliases
            value_type: int, int64, double, bool, object, class, or name
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "operation": operation,
                "value_type": value_type,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_compare_node", params)
        except Exception as e:
            error_msg = f"Error adding compare node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_boolean_node(
        ctx: Context,
        blueprint_name: str,
        operation: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a boolean expression node to a Blueprint graph.

        Args:
            blueprint_name: Blueprint name or path
            operation: not, and, nand, or, xor, nor, equal, not_equal, or symbolic aliases
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "operation": operation,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_boolean_node", params)
        except Exception as e:
            error_msg = f"Error adding boolean node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_select_node(
        ctx: Context,
        blueprint_name: str,
        value_type: str = "int",
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a typed Select expression node to a Blueprint graph.

        Args:
            blueprint_name: Blueprint name or path
            value_type: string, text, name, int, double, vector, rotator, color, transform, object, or class
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "value_type": value_type,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_select_node", params)
        except Exception as e:
            error_msg = f"Error adding select node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_literal_node(
        ctx: Context,
        blueprint_name: str,
        literal_type: str,
        value: Any = None,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a typed literal expression node to a Blueprint graph.

        Args:
            blueprint_name: Blueprint name or path
            literal_type: int, int64, float, double, bool, name, byte, string, or text
            value: Optional literal default value
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "literal_type": literal_type,
                "node_position": node_position
            }
            if value is not None:
                params["value"] = value
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_literal_node", params)
        except Exception as e:
            error_msg = f"Error adding literal node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_enum_literal_node(
        ctx: Context,
        blueprint_name: str,
        enum_type: str,
        value: Any = None,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a typed enum literal expression node to a Blueprint graph.

        Args:
            blueprint_name: Blueprint name or path
            enum_type: Native or asset enum path, preferably /Script/Module.EnumName
            value: Optional enum entry name or integer enum value
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "enum_type": enum_type,
                "node_position": node_position
            }
            if value is not None:
                params["value"] = value
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_enum_literal_node", params)
        except Exception as e:
            error_msg = f"Error adding enum literal node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_is_valid_node(
        ctx: Context,
        blueprint_name: str,
        value_type: str = "object",
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add an Is Valid expression node to a Blueprint graph.

        Args:
            blueprint_name: Blueprint name or path
            value_type: object or class
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "value_type": value_type,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_is_valid_node", params)
        except Exception as e:
            error_msg = f"Error adding is_valid node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_make_struct_node(
        ctx: Context,
        blueprint_name: str,
        struct_type: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a native Make Struct helper node to a Blueprint graph.

        Args:
            blueprint_name: Blueprint name or path
            struct_type: vector, rotator, or transform
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "struct_type": struct_type,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_make_struct_node", params)
        except Exception as e:
            error_msg = f"Error adding make struct node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_break_struct_node(
        ctx: Context,
        blueprint_name: str,
        struct_type: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a native Break Struct helper node to a Blueprint graph.

        Args:
            blueprint_name: Blueprint name or path
            struct_type: vector, rotator, or transform
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "struct_type": struct_type,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_break_struct_node", params)
        except Exception as e:
            error_msg = f"Error adding break struct node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_switch_int_node(
        ctx: Context,
        blueprint_name: str,
        start_index: int = 0,
        case_count: int = 2,
        case_values: Optional[List[int]] = None,
        has_default_pin: bool = True,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a contiguous Switch on Int node to a Blueprint graph.

        Args:
            blueprint_name: Blueprint name or path
            start_index: First case value when case_values is omitted
            case_count: Number of contiguous case pins when case_values is omitted
            case_values: Optional ascending contiguous integer cases
            has_default_pin: Whether to include the Default exec output
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "start_index": start_index,
                "case_count": case_count,
                "has_default_pin": has_default_pin,
                "node_position": node_position
            }
            if case_values is not None:
                params["case_values"] = case_values
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_switch_int_node", params)
        except Exception as e:
            error_msg = f"Error adding switch int node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_switch_enum_node(
        ctx: Context,
        blueprint_name: str,
        enum_type: str,
        has_default_pin: bool = False,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False
    ) -> Dict[str, Any]:
        """
        Add a Switch on Enum node to a Blueprint graph.

        Args:
            blueprint_name: Blueprint name or path
            enum_type: Native or asset enum path, preferably /Script/Module.EnumName
            has_default_pin: Whether to include the Default exec output
            node_position: Optional [X, Y] position in the graph

        Returns:
            Response containing the created node metadata
        """
        try:
            if node_position is None:
                node_position = [0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "enum_type": enum_type,
                "has_default_pin": has_default_pin,
                "node_position": node_position
            }
            add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)
            return send_node_command("add_blueprint_switch_enum_node", params)
        except Exception as e:
            error_msg = f"Error adding switch enum node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_blueprint_pin_default(
        ctx: Context,
        blueprint_name: str,
        node_id: str,
        pin_name: str,
        value: Any,
        direction: str = "",
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = ""
    ) -> Dict[str, Any]:
        """
        Set the default value or default object on a Blueprint node pin.

        Args:
            blueprint_name: Blueprint name or path
            node_id: Node GUID
            pin_name: Pin name
            value: Default value, object path, or class path
            direction: Optional input/output pin filter

        Returns:
            Response containing the updated pin metadata
        """
        try:
            params = {
                "blueprint_name": blueprint_name,
                "node_id": node_id,
                "pin_name": pin_name,
                "value": value,
                "direction": direction
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("set_blueprint_pin_default", params)
        except Exception as e:
            error_msg = f"Error setting pin default: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    logger.info("Blueprint node tools registered successfully")
