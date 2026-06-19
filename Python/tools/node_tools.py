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
    def delete_blueprint_node(
        ctx: Context,
        blueprint_name: str,
        node_id: str,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        expected_node_name: str = "",
        expected_node_class: str = "",
        expected_title_contains: str = "",
        allow_non_exec_linked_delete: bool = False,
        allow_exec_linked_delete: bool = False,
        allow_any_linked_delete: bool = False,
    ) -> Dict[str, Any]:
        """
        Delete one Blueprint graph node by GUID with safety guards.

        Args:
            blueprint_name: Name or asset path of the target Blueprint
            node_id: Node GUID to delete
            graph_name: Optional target graph name
            graph_id: Optional target graph GUID
            graph_type: Optional target graph type
            expected_node_name: Optional exact node object name guard
            expected_node_class: Optional node class guard, such as K2Node_VariableSet
            expected_title_contains: Optional title substring guard
            allow_non_exec_linked_delete: Allow deleting a node with data links
            allow_exec_linked_delete: Allow deleting a node with execution links
            allow_any_linked_delete: Allow deleting any linked node
        """
        try:
            params: Dict[str, Any] = {
                "blueprint_name": blueprint_name,
                "node_id": node_id,
                "expected_node_name": expected_node_name,
                "expected_node_class": expected_node_class,
                "expected_title_contains": expected_title_contains,
                "allow_non_exec_linked_delete": allow_non_exec_linked_delete,
                "allow_exec_linked_delete": allow_exec_linked_delete,
                "allow_any_linked_delete": allow_any_linked_delete,
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("delete_blueprint_node", params)
        except Exception as e:
            error_msg = f"Error deleting Blueprint node: {e}"
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
    def set_blueprint_variable_metadata(
        ctx: Context,
        blueprint_name: str,
        variable_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        is_editable: Optional[bool] = None,
        instance_editable: Optional[bool] = None,
        expose_on_spawn: Optional[bool] = None,
    ) -> Dict[str, Any]:
        """
        Set metadata or editor exposure flags on an existing Blueprint member variable.

        Args:
            blueprint_name: Name or asset path of the target Blueprint.
            variable_name: Existing Blueprint member variable name.
            metadata: Metadata key/value pairs, such as ClampMin, ClampMax, UIMin, UIMax, or ToolTip.
            is_editable: Optional alias for making the variable editable on instances.
            instance_editable: Optional explicit Instance Editable flag.
            expose_on_spawn: Optional Expose on Spawn flag.

        Returns:
            Response containing applied metadata, verified metadata, and flag edits.
        """
        from unreal_mcp_server import get_unreal_connection

        try:
            params = {
                "blueprint_name": blueprint_name,
                "variable_name": variable_name,
            }
            if metadata:
                params["metadata"] = metadata
            if is_editable is not None:
                params["is_editable"] = is_editable
            if instance_editable is not None:
                params["instance_editable"] = instance_editable
            if expose_on_spawn is not None:
                params["expose_on_spawn"] = expose_on_spawn

            unreal = get_unreal_connection()
            if not unreal:
                logger.error("Failed to connect to Unreal Engine")
                return {"success": False, "message": "Failed to connect to Unreal Engine"}

            logger.info(
                "Setting metadata on variable '%s' in blueprint '%s'",
                variable_name,
                blueprint_name,
            )
            response = unreal.send_command("set_blueprint_variable_metadata", params)

            if not response:
                logger.error("No response from Unreal Engine")
                return {"success": False, "message": "No response from Unreal Engine"}

            logger.info(f"Variable metadata response: {response}")
            return response

        except Exception as e:
            error_msg = f"Error setting variable metadata: {e}"
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
    def add_blueprint_event_dispatcher(
        ctx: Context,
        blueprint_name: str,
        dispatcher_name: str,
        inputs: Optional[List[Dict[str, Any]]] = None,
        category: str = "",
        tooltip: str = "",
        friendly_name: str = "",
    ) -> Dict[str, Any]:
        """
        Add an Event Dispatcher declaration to a Blueprint.

        Args:
            blueprint_name: Name of the target Blueprint
            dispatcher_name: Name of the Event Dispatcher
            inputs: Optional signature inputs. Each item accepts name/parameter_name and type/parameter_type.
            category: Optional Blueprint category
            tooltip: Optional Blueprint tooltip
            friendly_name: Optional display name

        Returns:
            Response containing the dispatcher name, multicast delegate pin type, and signature graph
        """
        params: Dict[str, Any] = {
            "blueprint_name": blueprint_name,
            "dispatcher_name": dispatcher_name,
        }
        if inputs:
            params["inputs"] = inputs
        if category:
            params["category"] = category
        if tooltip:
            params["tooltip"] = tooltip
        if friendly_name:
            params["friendly_name"] = friendly_name

        try:
            logger.info(f"Adding Event Dispatcher '{dispatcher_name}' to blueprint '{blueprint_name}'")
            return send_node_command("add_blueprint_event_dispatcher", params)
        except Exception as e:
            error_msg = f"Error adding Event Dispatcher: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_event_dispatcher_call_node(
        ctx: Context,
        blueprint_name: str,
        dispatcher_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False,
    ) -> Dict[str, Any]:
        """
        Add a call node for an existing Blueprint Event Dispatcher.

        Args:
            blueprint_name: Name of the target Blueprint
            dispatcher_name: Name of the Event Dispatcher to call
            node_position: Optional [X, Y] position in the graph
            graph_name: Optional target graph name
            graph_id: Optional target graph id
            graph_type: Optional target graph type
            create_graph_if_missing: Whether to create the target graph when allowed

        Returns:
            Response containing the node id, pins, dispatcher name, signature function, and graph metadata
        """
        if node_position is None:
            node_position = [0, 0]

        params: Dict[str, Any] = {
            "blueprint_name": blueprint_name,
            "dispatcher_name": dispatcher_name,
            "node_position": node_position,
        }
        add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)

        try:
            logger.info(f"Adding Event Dispatcher call node '{dispatcher_name}' to blueprint '{blueprint_name}'")
            return send_node_command("add_blueprint_event_dispatcher_call_node", params)
        except Exception as e:
            error_msg = f"Error adding Event Dispatcher call node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_custom_event_node(
        ctx: Context,
        blueprint_name: str,
        custom_event_name: str,
        node_position = None,
        signature_source_dispatcher_name: str = "",
        call_in_editor: Optional[bool] = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False,
    ) -> Dict[str, Any]:
        """
        Add a custom event node to a Blueprint event graph.

        Args:
            blueprint_name: Name of the target Blueprint
            custom_event_name: Name of the custom event
            node_position: Optional [X, Y] position in the graph
            signature_source_dispatcher_name: Optional Event Dispatcher whose signature should be copied
            call_in_editor: Optional value for the custom event's Call In Editor flag
            graph_name: Optional target graph name
            graph_id: Optional target graph id
            graph_type: Optional target graph type; custom events require an event graph
            create_graph_if_missing: Whether to create the target graph when supported

        Returns:
            Response containing the node id, pins, custom event name, signature function, and graph metadata
        """
        if node_position is None:
            node_position = [0, 0]

        params: Dict[str, Any] = {
            "blueprint_name": blueprint_name,
            "custom_event_name": custom_event_name,
            "node_position": node_position,
        }
        if signature_source_dispatcher_name:
            params["signature_source_dispatcher_name"] = signature_source_dispatcher_name
        if call_in_editor is not None:
            params["call_in_editor"] = call_in_editor
        add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)

        try:
            logger.info(f"Adding custom event node '{custom_event_name}' to blueprint '{blueprint_name}'")
            return send_node_command("add_blueprint_custom_event_node", params)
        except Exception as e:
            error_msg = f"Error adding custom event node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_event_dispatcher_bind_node(
        ctx: Context,
        blueprint_name: str,
        dispatcher_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False,
    ) -> Dict[str, Any]:
        """
        Add a bind node for an existing Blueprint Event Dispatcher.

        Args:
            blueprint_name: Name of the target Blueprint
            dispatcher_name: Name of the Event Dispatcher to bind
            node_position: Optional [X, Y] position in the graph
            graph_name: Optional target graph name
            graph_id: Optional target graph id
            graph_type: Optional target graph type such as event or function
            create_graph_if_missing: Whether to create the target graph when supported

        Returns:
            Response containing the node id, pins, dispatcher name, signature function, and graph metadata
        """
        if node_position is None:
            node_position = [0, 0]

        params: Dict[str, Any] = {
            "blueprint_name": blueprint_name,
            "dispatcher_name": dispatcher_name,
            "node_position": node_position,
        }
        add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)

        try:
            logger.info(f"Adding Event Dispatcher bind node '{dispatcher_name}' to blueprint '{blueprint_name}'")
            return send_node_command("add_blueprint_event_dispatcher_bind_node", params)
        except Exception as e:
            error_msg = f"Error adding Event Dispatcher bind node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_event_dispatcher_unbind_node(
        ctx: Context,
        blueprint_name: str,
        dispatcher_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False,
    ) -> Dict[str, Any]:
        """
        Add an unbind node for an existing Blueprint Event Dispatcher.

        Args:
            blueprint_name: Name of the target Blueprint
            dispatcher_name: Name of the Event Dispatcher to unbind
            node_position: Optional [X, Y] position in the graph
            graph_name: Optional target graph name
            graph_id: Optional target graph id
            graph_type: Optional target graph type such as event or function
            create_graph_if_missing: Whether to create the target graph when supported

        Returns:
            Response containing the node id, pins, dispatcher name, signature function, and graph metadata
        """
        if node_position is None:
            node_position = [0, 0]

        params: Dict[str, Any] = {
            "blueprint_name": blueprint_name,
            "dispatcher_name": dispatcher_name,
            "node_position": node_position,
        }
        add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)

        try:
            logger.info(f"Adding Event Dispatcher unbind node '{dispatcher_name}' to blueprint '{blueprint_name}'")
            return send_node_command("add_blueprint_event_dispatcher_unbind_node", params)
        except Exception as e:
            error_msg = f"Error adding Event Dispatcher unbind node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_event_dispatcher_clear_node(
        ctx: Context,
        blueprint_name: str,
        dispatcher_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False,
    ) -> Dict[str, Any]:
        """
        Add a clear node for an existing Blueprint Event Dispatcher.

        Args:
            blueprint_name: Name of the target Blueprint
            dispatcher_name: Name of the Event Dispatcher to clear
            node_position: Optional [X, Y] position in the graph
            graph_name: Optional target graph name
            graph_id: Optional target graph id
            graph_type: Optional target graph type such as event or function
            create_graph_if_missing: Whether to create the target graph when supported

        Returns:
            Response containing the node id, pins, dispatcher name, signature function, and graph metadata
        """
        if node_position is None:
            node_position = [0, 0]

        params: Dict[str, Any] = {
            "blueprint_name": blueprint_name,
            "dispatcher_name": dispatcher_name,
            "node_position": node_position,
        }
        add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)

        try:
            logger.info(f"Adding Event Dispatcher clear node '{dispatcher_name}' to blueprint '{blueprint_name}'")
            return send_node_command("add_blueprint_event_dispatcher_clear_node", params)
        except Exception as e:
            error_msg = f"Error adding Event Dispatcher clear node: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def add_blueprint_event_dispatcher_assign_node(
        ctx: Context,
        blueprint_name: str,
        dispatcher_name: str,
        node_position = None,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        create_graph_if_missing: bool = False,
    ) -> Dict[str, Any]:
        """
        Add an assign node for an existing Blueprint Event Dispatcher.

        Args:
            blueprint_name: Name of the target Blueprint
            dispatcher_name: Name of the Event Dispatcher to assign
            node_position: Optional [X, Y] position in the graph
            graph_name: Optional target graph name
            graph_id: Optional target graph id
            graph_type: Optional target graph type; assign nodes require an event graph
            create_graph_if_missing: Whether to create the target graph when supported

        Returns:
            Response containing the node id, pins, dispatcher name, signature function, and graph metadata
        """
        if node_position is None:
            node_position = [0, 0]

        params: Dict[str, Any] = {
            "blueprint_name": blueprint_name,
            "dispatcher_name": dispatcher_name,
            "node_position": node_position,
        }
        add_graph_selector(params, graph_name, graph_id, graph_type, create_graph_if_missing)

        try:
            logger.info(f"Adding Event Dispatcher assign node '{dispatcher_name}' to blueprint '{blueprint_name}'")
            return send_node_command("add_blueprint_event_dispatcher_assign_node", params)
        except Exception as e:
            error_msg = f"Error adding Event Dispatcher assign node: {e}"
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
    def inspect_blueprint_graph_call_topology(
        ctx: Context,
        blueprint_name: str,
        graph_name: str = "",
        graph_id: str = "",
        graph_type: str = "",
        graph_name_contains: str = "",
        node_type: str = "",
        title_contains: str = "",
        reference_contains: str = "",
        include_pins: bool = False,
        include_links: bool = True,
        include_references: bool = True,
        max_graphs: int = 64,
        max_nodes_per_graph: int = 512,
        max_links_per_graph: int = 1024,
        max_references_per_node: int = 64
    ) -> Dict[str, Any]:
        """
        Read static Blueprint graph call/link topology.

        This command is read-only. It reports graph nodes, classified K2 node kinds,
        function/variable/event member references, asset/reference paths, and pin links.
        It does not prove runtime execution.

        Args:
            blueprint_name: Blueprint name or path
            graph_name: Optional exact graph name selector
            graph_id: Optional graph GUID selector
            graph_type: Optional graph type selector: event, function, macro, delegate, or any
            graph_name_contains: Optional graph name substring filter
            node_type: Optional node class/title substring filter
            title_contains: Optional node title substring filter
            reference_contains: Optional substring filter across function, variable, event, pin, and reference text
            include_pins: Include full per-node pin metadata
            include_links: Include normalized pin links
            include_references: Include per-node reference_paths
            max_graphs: Maximum graphs to include, -1 for unlimited
            max_nodes_per_graph: Maximum matching nodes per graph, -1 for unlimited
            max_links_per_graph: Maximum links per graph, -1 for unlimited
            max_references_per_node: Maximum reference paths per node, -1 for unlimited

        Returns:
            Response containing static Blueprint graph topology.
        """
        try:
            params = {
                "blueprint_name": blueprint_name,
                "graph_name_contains": graph_name_contains,
                "node_type": node_type,
                "title_contains": title_contains,
                "reference_contains": reference_contains,
                "include_pins": include_pins,
                "include_links": include_links,
                "include_references": include_references,
                "max_graphs": max_graphs,
                "max_nodes_per_graph": max_nodes_per_graph,
                "max_links_per_graph": max_links_per_graph,
                "max_references_per_node": max_references_per_node,
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("inspect_blueprint_graph_call_topology", params)
        except Exception as e:
            error_msg = f"Error inspecting Blueprint graph call topology: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_anim_graph_protected_topology(
        ctx: Context,
        blueprint_name: str,
        node_id: str = "",
        node_type: str = "",
        title_contains: str = "",
        include_pins: bool = True,
        include_pose_pins: bool = True,
        include_links: bool = True,
        include_non_pose_links: bool = False,
        include_settings: bool = False,
        max_depth: int = 3,
        max_nodes: int = 512,
        max_links: int = 2048,
        graph_name: str = "AnimGraph",
        graph_id: str = "",
        graph_type: str = "function"
    ) -> Dict[str, Any]:
        """
        Read protected AnimGraph editor topology in a stable read-only format.

        This command reports AnimGraph nodes, pins, pose pins, and normalized links.
        It does not compile, save, modify assets, or prove runtime execution.

        Args:
            blueprint_name: Animation Blueprint name or path
            node_id: Optional node GUID filter
            node_type: Optional class or title substring filter
            title_contains: Optional title substring filter
            include_pins: Include full per-node pin metadata
            include_pose_pins: Include pose-pin summaries and preferred input/output pose pins
            include_links: Include normalized graph links
            include_non_pose_links: Include non-pose data links in addition to pose/component-pose links
            include_settings: Include reflected FAnimNode settings through the existing settings dumper
            max_depth: Maximum nested property depth when include_settings is true
            max_nodes: Maximum nodes to include, -1 for unlimited
            max_links: Maximum links to include, -1 for unlimited
            graph_name: Target animation graph name, defaults to AnimGraph
            graph_id: Optional target graph GUID
            graph_type: Graph selector type, defaults to function because AnimGraph is reported there

        Returns:
            Response containing static AnimGraph topology.
        """
        try:
            params = {
                "blueprint_name": blueprint_name,
                "node_id": node_id,
                "node_type": node_type,
                "title_contains": title_contains,
                "include_pins": include_pins,
                "include_pose_pins": include_pose_pins,
                "include_links": include_links,
                "include_non_pose_links": include_non_pose_links,
                "include_settings": include_settings,
                "max_depth": max_depth,
                "max_nodes": max_nodes,
                "max_links": max_links,
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("inspect_anim_graph_protected_topology", params)
        except Exception as e:
            error_msg = f"Error inspecting AnimGraph protected topology: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_anim_graph_node_settings(
        ctx: Context,
        blueprint_name: str,
        node_id: str = "",
        node_type: str = "",
        title_contains: str = "",
        include_pins: bool = True,
        max_depth: int = 4,
        graph_name: str = "AnimGraph",
        graph_id: str = "",
        graph_type: str = "function"
    ) -> Dict[str, Any]:
        """
        Read AnimGraph node runtime settings from the internal FAnimNode struct.

        Args:
            blueprint_name: Animation Blueprint name or path
            node_id: Optional node GUID filter
            node_type: Optional class or title substring filter
            title_contains: Optional title substring filter
            include_pins: Include pin metadata and links in the result
            max_depth: Maximum nested property depth for struct/array dumping
            graph_name: Target animation graph name, defaults to AnimGraph
            graph_id: Optional target graph GUID
            graph_type: Graph selector type, defaults to function because AnimGraph is reported there

        Returns:
            Response containing node metadata and reflected anim-node settings.
        """
        try:
            params = {
                "blueprint_name": blueprint_name,
                "node_id": node_id,
                "node_type": node_type,
                "title_contains": title_contains,
                "include_pins": include_pins,
                "max_depth": max_depth,
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("inspect_anim_graph_node_settings", params)
        except Exception as e:
            error_msg = f"Error inspecting AnimGraph node settings: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_anim_state_machine_transitions(
        ctx: Context,
        blueprint_name: str,
        state_machine_name: str = "",
        include_pins: bool = True,
        include_rule_graph_nodes: bool = True,
        include_state_nodes: bool = True,
        max_rule_graph_nodes: int = 256
    ) -> Dict[str, Any]:
        """
        Read Animation Blueprint state-machine transition topology.

        This command is read-only. It reports state-machine nodes, source/target states,
        transition rule graphs, rule graph nodes, and transition blend/priority settings.

        Args:
            blueprint_name: Animation Blueprint name or path
            state_machine_name: Optional state machine name/title substring filter
            include_pins: Include pin metadata and links on returned graph nodes
            include_rule_graph_nodes: Include nodes inside each transition rule graph
            include_state_nodes: Include state node summaries for each state machine
            max_rule_graph_nodes: Maximum rule graph nodes per transition, -1 for unlimited

        Returns:
            Response containing state machines and transition topology.
        """
        try:
            params = {
                "blueprint_name": blueprint_name,
                "state_machine_name": state_machine_name,
                "include_pins": include_pins,
                "include_rule_graph_nodes": include_rule_graph_nodes,
                "include_state_nodes": include_state_nodes,
                "max_rule_graph_nodes": max_rule_graph_nodes,
            }
            return send_node_command("inspect_anim_state_machine_transitions", params)
        except Exception as e:
            error_msg = f"Error inspecting AnimBP state-machine transitions: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def controlrig_direct_gate_probe(
        ctx: Context,
        control_rig_path: str = "",
        control_rig_class: str = "",
        cases: Optional[List[Dict[str, Any]]] = None,
        sample_elements: Optional[List[Any]] = None,
        execute_events: Optional[List[str]] = None,
        should_trace_property: str = "ShouldDoIKTrace",
        interaction_location_property: str = "InteractionWorldLocation"
    ) -> Dict[str, Any]:
        """
        Run a transient direct ControlRig gate probe without modifying or saving assets.

        The default case set matches the StackOBot ControlRig learning pass: it toggles
        ShouldDoIKTrace, InteractionWorldLocation, IKBlend_l, and IK_blend_interact,
        executes Construction/Forwards Solve/Post Forwards Solve, samples hierarchy
        transforms, and reports deltas from the first case.

        Args:
            control_rig_path: ControlRig Blueprint asset path
            control_rig_class: Optional generated ControlRig class path
            cases: Optional case list. Each case may include name, properties, should_trace,
                loc or interaction_world_location, and curves.
            sample_elements: Optional hierarchy element names or {type, name} objects
            execute_events: Optional ControlRig event names to execute
            should_trace_property: Property name used by shorthand should_trace
            interaction_location_property: Property name used by shorthand loc

        Returns:
            Response containing case outputs, transform samples, deltas, and errors.
        """
        try:
            params: Dict[str, Any] = {
                "should_trace_property": should_trace_property,
                "interaction_location_property": interaction_location_property,
            }
            if control_rig_path:
                params["control_rig_path"] = control_rig_path
            if control_rig_class:
                params["control_rig_class"] = control_rig_class
            if cases is not None:
                params["cases"] = cases
            if sample_elements is not None:
                params["sample_elements"] = sample_elements
            if execute_events is not None:
                params["execute_events"] = execute_events
            return send_node_command("controlrig_direct_gate_probe", params)
        except Exception as e:
            error_msg = f"Error running ControlRig direct gate probe: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def sample_controlrig_pre_post_runtime_pose(
        ctx: Context,
        control_rig_path: str = "",
        control_rig_class: str = "",
        input_defaults: Optional[Dict[str, Any]] = None,
        curve_values: Optional[Dict[str, float]] = None,
        cases: Optional[List[Dict[str, Any]]] = None,
        sample_elements: Optional[List[Any]] = None,
        execute_events: Optional[List[str]] = None,
        should_trace_property: str = "ShouldDoIKTrace",
        interaction_location_property: str = "InteractionWorldLocation"
    ) -> Dict[str, Any]:
        """
        Sample ControlRig hierarchy transforms before and after execute events.

        This is a read-only transient ControlRig pre/post probe. It does not
        instrument the compiled AnimGraph node stack; the response labels this as
        runtime_source=direct_transient_controlrig and runtime_graph_prepost=false.

        Args:
            control_rig_path: ControlRig Blueprint asset path
            control_rig_class: Optional generated ControlRig class path
            input_defaults: Optional ControlRig property defaults
            curve_values: Optional hierarchy curve values
            cases: Optional case list. Each case may include name, properties, should_trace,
                loc or interaction_world_location, and curves.
            sample_elements: Optional hierarchy element names or {type, name} objects
            execute_events: Optional ControlRig event names to execute, default Forwards Solve
            should_trace_property: Property name used by shorthand should_trace
            interaction_location_property: Property name used by shorthand loc

        Returns:
            Response containing pre_pose, post_pose, deltas, echoes, and execution status.
        """
        try:
            if input_defaults is None:
                input_defaults = {
                    "ShouldDoIKTrace": True,
                    "InteractionWorldLocation": [80, -40, 80],
                }
            if curve_values is None:
                curve_values = {
                    "IK_blend_interact": 1.0,
                    "IKBlend_l": 1.0,
                }
            params: Dict[str, Any] = {
                "input_defaults": input_defaults,
                "curve_values": curve_values,
                "should_trace_property": should_trace_property,
                "interaction_location_property": interaction_location_property,
            }
            if control_rig_path:
                params["control_rig_path"] = control_rig_path
            if control_rig_class:
                params["control_rig_class"] = control_rig_class
            if cases is not None:
                params["cases"] = cases
            if sample_elements is not None:
                params["sample_elements"] = sample_elements
            if execute_events is not None:
                params["execute_events"] = execute_events
            return send_node_command("sample_controlrig_pre_post_runtime_pose", params)
        except Exception as e:
            error_msg = f"Error sampling ControlRig pre/post runtime pose: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def sample_anim_node_pre_post_runtime_pose(
        ctx: Context,
        blueprint_name: str = "",
        anim_blueprint: str = "",
        graph_name: str = "AnimGraph",
        graph_id: str = "",
        graph_type: str = "function",
        node_id: str = "",
        node_type: str = "",
        title_contains: str = "",
        sample_bones: Optional[List[str]] = None,
        sample_sockets: Optional[List[str]] = None,
        mode: str = "active_component_tick_delta",
        skeletal_mesh: str = "",
        temp_root: str = "/Game/_MCP_Temp/AnimNodePrePost",
        cleanup: bool = True,
        overwrite_existing_temp_assets: bool = True,
        run_id: str = "",
        actor_label: str = "",
        actor_name: str = "",
        actor_path: str = "",
        component_name: str = "",
        anim_instance_source: str = "main",
        prefer_pie_world: bool = True,
        require_pie_world: bool = False,
        tick_count: int = 1,
        tick_delta_time: float = 1.0 / 30.0,
        settle_tick_count: int = 0,
        refresh_bone_transforms: bool = True,
        allow_missing_bones: bool = False,
        pose_link_max_depth: int = 4,
        input_pose_mode: str = "first",
        input_pose_field_path: str = "",
        input_pose_index: int = -1,
        include_pins: bool = True,
        max_depth: int = 3,
        dry_run: bool = True
    ) -> Dict[str, Any]:
        """
        Resolve a target AnimGraph node or run a limited runtime probe.

        With dry_run=True this is a read-only target resolver. With dry_run=False,
        mode="compiled_graph_mapping" maps the selected editor AnimGraph node to
        the compiled/live FAnimNode instance on a matched AnimInstance and reports
        runtime FPoseLink/FComponentSpacePoseLink link IDs. With
        mode="pose_watch_capture", it temporarily sets the AnimBP debug object,
        registers transient PoseWatch debug entries for the selected compiled
        node output and selected runtime input pose link(s), and samples them
        during the same forced tick without adding PoseWatches to the AnimBP asset.
        With
        mode="active_component_tick_delta" samples final SkeletalMeshComponent pose
        before and after forced ticks on a matched live component. With
        mode="isolated_temp_components", it duplicates the AnimBP under _MCP_Temp,
        bypasses the selected node in a source copy, and compares that against a
        selected-node copy on separate transient components.

        Args:
            blueprint_name: Anim Blueprint name or path
            anim_blueprint: Alternative Anim Blueprint name or path
            graph_name: AnimGraph graph name, defaults to AnimGraph
            graph_id: Optional graph GUID
            graph_type: Graph type, defaults to function for AnimGraph
            node_id: Exact target node GUID. Required when filters are ambiguous.
            node_type: Node class/title filter such as AnimGraphNode_RigidBody
            title_contains: Node title substring filter
            sample_bones: Optional future sample bone list echoed in the response
            sample_sockets: Optional future sample socket list echoed in the response
            mode: Runtime mode for dry_run=False. compiled_graph_mapping, pose_watch_capture, active_component_tick_delta, or isolated_temp_components.
            skeletal_mesh: SkeletalMesh path required by isolated_temp_components
            temp_root: Temp asset root for isolated_temp_components
            cleanup: Delete transient actors/temp assets after isolated sampling
            overwrite_existing_temp_assets: Replace colliding temp assets
            run_id: Optional stable suffix for generated temp asset/actor names
            actor_label: Live actor label to sample for active_component_tick_delta
            actor_name: Live actor object name to sample
            actor_path: Live actor object path to sample
            component_name: SkeletalMeshComponent name to sample
            anim_instance_source: AnimInstance source on the sampled component: main or post_process
            prefer_pie_world: Prefer PIE/SIE/play worlds over editor world
            require_pie_world: Refuse editor-world fallback
            tick_count: Forced tick count between pre/post samples
            tick_delta_time: Delta time for forced ticks
            settle_tick_count: Forced ticks before taking the pre sample
            refresh_bone_transforms: Refresh bone transforms after forced ticks
            allow_missing_bones: Return partial samples instead of failing on missing bones/sockets
            pose_link_max_depth: Max struct recursion depth for compiled_graph_mapping and pose_watch_capture runtime pose-link inventory
            input_pose_mode: PoseWatch input selection mode: first or all
            input_pose_field_path: Exact runtime pose-link field path to capture
            input_pose_index: Zero-based valid runtime pose-link index to capture
            include_pins: Include full pin data for the selected node
            max_depth: Reflected settings depth
            dry_run: Resolve only when true; run the selected mode when false

        Returns:
            Resolver response or selected runtime probe response.
        """
        try:
            params: Dict[str, Any] = {
                "graph_name": graph_name,
                "graph_type": graph_type,
                "mode": mode,
                "temp_root": temp_root,
                "cleanup": cleanup,
                "overwrite_existing_temp_assets": overwrite_existing_temp_assets,
                "prefer_pie_world": prefer_pie_world,
                "require_pie_world": require_pie_world,
                "tick_count": tick_count,
                "tick_delta_time": tick_delta_time,
                "settle_tick_count": settle_tick_count,
                "refresh_bone_transforms": refresh_bone_transforms,
                "allow_missing_bones": allow_missing_bones,
                "anim_instance_source": anim_instance_source,
                "pose_link_max_depth": pose_link_max_depth,
                "input_pose_mode": input_pose_mode,
                "include_pins": include_pins,
                "max_depth": max_depth,
                "dry_run": dry_run,
            }
            if blueprint_name:
                params["blueprint_name"] = blueprint_name
            if anim_blueprint:
                params["anim_blueprint"] = anim_blueprint
            if graph_id:
                params["graph_id"] = graph_id
            if skeletal_mesh:
                params["skeletal_mesh"] = skeletal_mesh
            if run_id:
                params["run_id"] = run_id
            if node_id:
                params["node_id"] = node_id
            if node_type:
                params["node_type"] = node_type
            if title_contains:
                params["title_contains"] = title_contains
            if actor_label:
                params["actor_label"] = actor_label
            if actor_name:
                params["actor_name"] = actor_name
            if actor_path:
                params["actor_path"] = actor_path
            if component_name:
                params["component_name"] = component_name
            if sample_bones is not None:
                params["sample_bones"] = sample_bones
            if sample_sockets is not None:
                params["sample_sockets"] = sample_sockets
            if input_pose_field_path:
                params["input_pose_field_path"] = input_pose_field_path
            if input_pose_index >= 0:
                params["input_pose_index"] = input_pose_index
            return send_node_command("sample_anim_node_pre_post_runtime_pose", params)
        except Exception as e:
            error_msg = f"Error resolving AnimGraph node pre/post runtime pose target: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def sample_skeletal_bones_in_sie(
        ctx: Context,
        actor_label: str = "",
        actor_name: str = "",
        actor_path: str = "",
        component_name: str = "",
        bones: Optional[List[str]] = None,
        sockets: Optional[List[str]] = None,
        prefer_pie_world: bool = True,
        require_pie_world: bool = False
    ) -> Dict[str, Any]:
        """
        Sample SkeletalMeshComponent bone/socket transforms from the active PIE/SIE/play world.

        This is a read-only immediate sampler. It prefers a live PIE/SIE/play world when
        available, falls back to the editor world, and reports the sampled world type.
        It does not start or tick SIE by itself.

        Args:
            actor_label: Optional actor label filter, case-insensitive exact match
            actor_name: Optional actor object name filter, case-insensitive exact match
            actor_path: Optional actor path filter, exact or path suffix match
            component_name: Optional SkeletalMeshComponent object name
            bones: Optional bone names to sample. Defaults to key StackOBot-style bones.
            sockets: Optional socket names to sample
            prefer_pie_world: Prefer active PIE/SIE/play world before editor world
            require_pie_world: Fail instead of falling back to the editor world when no PIE/SIE/play world matches

        Returns:
            Response containing actor/component metadata, sampled world type, and transforms.
        """
        try:
            params: Dict[str, Any] = {
                "actor_label": actor_label,
                "actor_name": actor_name,
                "actor_path": actor_path,
                "component_name": component_name,
                "prefer_pie_world": prefer_pie_world,
                "require_pie_world": require_pie_world,
            }
            if bones is not None:
                params["bones"] = bones
            if sockets is not None:
                params["sockets"] = sockets
            return send_node_command("sample_skeletal_bones_in_sie", params)
        except Exception as e:
            error_msg = f"Error sampling skeletal bones in SIE: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def sample_blendspace_runtime_pose_grid(
        ctx: Context,
        skeletal_mesh: str,
        blendspace_path: str = "",
        blendspaces: Optional[List[Any]] = None,
        samples: Optional[List[Dict[str, Any]]] = None,
        sample_bones: Optional[List[str]] = None,
        sample_sockets: Optional[List[str]] = None,
        actor_label: str = "MCP_BlendSpace_RuntimePoseGrid",
        sample_time: float = 0.25,
        settle_tick_count: int = 2,
        tick_count: int = 1,
        tick_delta_time: float = 1.0 / 30.0,
        include_axis_extremes: bool = False,
        allow_missing_bones: bool = False,
        refresh_bone_transforms: bool = True,
        cleanup: bool = True,
        prefer_pie_world: bool = True,
        require_pie_world: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate BlendSpace inputs on a transient runtime SkeletalMeshActor and sample bone/socket poses.

        This command does not start SIE by itself. By default it requires an active
        PIE/SIE/play world, spawns a transient SkeletalMeshActor, configures
        AnimationSingleNode BlendSpace playback, applies each requested input,
        forces narrow component ticks, samples requested bones/sockets, and cleans
        up the transient actor without saving assets.

        Args:
            skeletal_mesh: SkeletalMesh asset path for the transient probe actor
            blendspace_path: Single BlendSpace asset path
            blendspaces: Optional list of BlendSpace paths or objects with path/name/samples
            samples: Optional sample inputs for single blendspace_path. Each object may include label and input or x/y/z.
            sample_bones: Bone names to sample. Defaults to key humanoid bones in C++.
            sample_sockets: Socket names to sample
            actor_label: Transient actor label
            sample_time: Single-node playback time applied before sampling
            settle_tick_count: Forced ticks after setting each input before final tick
            tick_count: Forced ticks immediately before sampling
            tick_delta_time: Delta time for forced component ticks
            include_axis_extremes: Include min/center/max axis probes when samples are not supplied
            allow_missing_bones: Return partial sample data instead of failing on missing bones/sockets
            refresh_bone_transforms: Refresh bones after each forced tick
            cleanup: Destroy transient actor before returning
            prefer_pie_world: Prefer active PIE/SIE/play worlds over editor world
            require_pie_world: Fail without active PIE/SIE/play world

        Returns:
            Response with per-BlendSpace sample poses, weighted source samples, and deltas from each BlendSpace's first valid sample.
        """
        try:
            params: Dict[str, Any] = {
                "skeletal_mesh": skeletal_mesh,
                "actor_label": actor_label,
                "sample_time": sample_time,
                "settle_tick_count": settle_tick_count,
                "tick_count": tick_count,
                "tick_delta_time": tick_delta_time,
                "include_axis_extremes": include_axis_extremes,
                "allow_missing_bones": allow_missing_bones,
                "refresh_bone_transforms": refresh_bone_transforms,
                "cleanup": cleanup,
                "prefer_pie_world": prefer_pie_world,
                "require_pie_world": require_pie_world,
            }
            if blendspace_path:
                params["blendspace_path"] = blendspace_path
            if blendspaces is not None:
                params["blendspaces"] = blendspaces
            if samples is not None:
                params["samples"] = samples
            if sample_bones is not None:
                params["sample_bones"] = sample_bones
            if sample_sockets is not None:
                params["sample_sockets"] = sample_sockets
            return send_node_command("sample_blendspace_runtime_pose_grid", params)
        except Exception as e:
            error_msg = f"Error sampling BlendSpace runtime pose grid: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def ensure_blendspace_sample_variant(
        ctx: Context,
        source_blendspace: str,
        variant_name: str = "Variant",
        target_root: str = "/Game/_MCP_Sample/AnimStudy",
        target_blendspace: str = "",
        axis_edits: Optional[List[Dict[str, Any]]] = None,
        sample_edits: Optional[List[Dict[str, Any]]] = None,
        add_samples: Optional[List[Dict[str, Any]]] = None,
        overwrite_existing: bool = False,
        save: bool = True,
        dry_run: bool = False,
        validate_only: bool = False,
        allow_non_sample: bool = False,
    ) -> Dict[str, Any]:
        """
        Create or reuse a sample-only BlendSpace variant and apply explicit axis/sample edits.

        By default this command refuses targets outside /Game/_MCP_Sample. It duplicates
        the source BlendSpace to a sample path, applies axis range/grid changes,
        edits existing sample coordinates or sample animations, optionally adds samples
        with compatible AnimSequence assets, validates/resamples the BlendSpace, and saves
        only the target asset. Use sample_blendspace_runtime_pose_grid after this command
        for runtime pose evidence.

        Args:
            source_blendspace: Source BlendSpace path
            variant_name: Name segment used for default target path
            target_root: Sample output folder, defaults to /Game/_MCP_Sample/AnimStudy
            target_blendspace: Optional explicit target BlendSpace package path
            axis_edits: Optional axis edits. Each entry accepts index/axis plus min, max, grid_num, display_name, snap_to_grid, wrap_input.
            sample_edits: Optional existing sample edits. Select by index/sample_index, animation, or animation_name; set input/position/sample_value, x/y/z, offset/delta, or replacement_animation.
            add_samples: Optional samples to add. Each entry requires animation and input/position/sample_value or x/y/z.
            overwrite_existing: Delete and recreate existing target asset before applying edits
            save: Save the target BlendSpace after edits
            dry_run: Validate paths/request and return without editing assets
            validate_only: Same as dry_run for command-routing compatibility
            allow_non_sample: Allow target paths outside /Game/_MCP_Sample

        Returns:
            Response with target path, before/after axes and samples, edit results, save result, and safety flags.
        """
        try:
            params: Dict[str, Any] = {
                "source_blendspace": source_blendspace,
                "variant_name": variant_name,
                "target_root": target_root,
                "overwrite_existing": overwrite_existing,
                "save": save,
                "dry_run": dry_run,
                "validate_only": validate_only,
                "allow_non_sample": allow_non_sample,
            }
            if target_blendspace:
                params["target_blendspace"] = target_blendspace
            if axis_edits is not None:
                params["axis_edits"] = axis_edits
            if sample_edits is not None:
                params["sample_edits"] = sample_edits
            if add_samples is not None:
                params["add_samples"] = add_samples
            return send_node_command("ensure_blendspace_sample_variant", params)
        except Exception as e:
            error_msg = f"Error ensuring BlendSpace sample variant: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def inspect_anim_instance_runtime_state(
        ctx: Context,
        actor_label: str = "",
        actor_name: str = "",
        actor_path: str = "",
        component_name: str = "",
        state_machine_name: str = "",
        include_states: bool = True,
        include_state_weights: bool = True,
        include_relevant_anim_times: bool = False,
        include_transition_progress: bool = True,
        include_inactive_transition_progress: bool = False,
        include_montages: bool = True,
        include_curves: bool = False,
        curve_names: Optional[List[str]] = None,
        max_state_machines: int = 32,
        max_state_machine_instances_to_probe: int = 256,
        max_states_per_machine: int = 64,
        max_transitions_per_machine: int = 128,
        max_curves: int = 128,
        prefer_pie_world: bool = True,
        require_pie_world: bool = False
    ) -> Dict[str, Any]:
        """
        Inspect runtime AnimInstance state from an active PIE/SIE/play SkeletalMeshComponent.

        This is read-only. It prefers a live PIE/SIE/play world when available,
        falls back to the editor world, and does not start or tick SIE by itself.

        Args:
            actor_label: Optional actor label filter, case-insensitive exact match
            actor_name: Optional actor object name filter, case-insensitive exact match
            actor_path: Optional actor path filter, exact or path suffix match
            component_name: Optional SkeletalMeshComponent object name
            state_machine_name: Optional state-machine name substring filter
            include_states: Include per-state metadata for each state machine
            include_state_weights: Include runtime state/machine weights
            include_relevant_anim_times: Include relevant asset-player time/remaining values per state
            include_transition_progress: Include active transition elapsed/crossfade progress
            include_inactive_transition_progress: Include inactive transitions with zero progress
            include_montages: Include current active montage data
            include_curves: Include curve values
            curve_names: Optional curve names. If omitted and include_curves is true, active/all names are used.
            max_state_machines: Maximum state machines to include
            max_state_machine_instances_to_probe: Maximum runtime AnimNode indexes to probe for state-machine instances
            max_states_per_machine: Maximum states per included machine
            max_transitions_per_machine: Maximum transitions per included machine for transition progress
            max_curves: Maximum curves to include
            prefer_pie_world: Prefer active PIE/SIE/play world before editor world
            require_pie_world: Fail instead of falling back to the editor world when no PIE/SIE/play world matches

        Returns:
            Response containing AnimInstance metadata, state-machine state, montage, and curves.
        """
        try:
            params: Dict[str, Any] = {
                "actor_label": actor_label,
                "actor_name": actor_name,
                "actor_path": actor_path,
                "component_name": component_name,
                "state_machine_name": state_machine_name,
                "include_states": include_states,
                "include_state_weights": include_state_weights,
                "include_relevant_anim_times": include_relevant_anim_times,
                "include_transition_progress": include_transition_progress,
                "include_inactive_transition_progress": include_inactive_transition_progress,
                "include_montages": include_montages,
                "include_curves": include_curves,
                "max_state_machines": max_state_machines,
                "max_state_machine_instances_to_probe": max_state_machine_instances_to_probe,
                "max_states_per_machine": max_states_per_machine,
                "max_transitions_per_machine": max_transitions_per_machine,
                "max_curves": max_curves,
                "prefer_pie_world": prefer_pie_world,
                "require_pie_world": require_pie_world,
            }
            if curve_names is not None:
                params["curve_names"] = curve_names
            return send_node_command("inspect_anim_instance_runtime_state", params)
        except Exception as e:
            error_msg = f"Error inspecting AnimInstance runtime state: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_anim_instance_runtime_property_for_probe(
        ctx: Context,
        actor_label: str = "",
        actor_name: str = "",
        actor_path: str = "",
        component_name: str = "",
        properties: Optional[Dict[str, Any]] = None,
        property_name: str = "",
        value: Any = None,
        tick_after_set: bool = False,
        tick_count: int = 1,
        tick_delta_time: float = 1.0 / 30.0,
        refresh_bone_transforms: bool = True,
        include_snapshot_after: bool = True,
        include_previous_values: bool = True,
        state_machine_name: str = "",
        include_states: bool = True,
        include_state_weights: bool = True,
        include_relevant_anim_times: bool = False,
        include_transition_progress: bool = True,
        include_inactive_transition_progress: bool = False,
        include_montages: bool = True,
        include_curves: bool = False,
        curve_names: Optional[List[str]] = None,
        max_transitions_per_machine: int = 128,
        prefer_pie_world: bool = True,
        require_pie_world: bool = False
    ) -> Dict[str, Any]:
        """
        Set properties on the matched live AnimInstance for runtime probing only.

        This modifies the current runtime object, not the Animation Blueprint asset.

        Args:
            actor_label: Optional actor label filter
            actor_name: Optional actor object name filter
            actor_path: Optional actor path filter
            component_name: Optional SkeletalMeshComponent object name
            properties: Property map such as {"GroundSpeed": 250.0}
            property_name: Single property name alternative
            value: Single property value alternative
            tick_after_set: Force a narrow component animation tick after setting
            tick_count: Number of forced component animation ticks
            tick_delta_time: Delta time per forced tick
            refresh_bone_transforms: Refresh component bone transforms during/after forced ticks when tick_count > 0
            include_snapshot_after: Include state-machine/montage/curve snapshot after the set
            include_previous_values: Include previous property values in the response
            state_machine_name: Optional state-machine name substring filter for snapshots
            include_states: Include per-state metadata in snapshots
            include_state_weights: Include runtime state/machine weights in snapshots
            include_relevant_anim_times: Include relevant asset-player time/remaining values per state in snapshots
            include_transition_progress: Include active transition elapsed/crossfade progress in snapshots
            include_inactive_transition_progress: Include inactive transition progress entries in snapshots
            include_montages: Include active montage data in snapshots
            include_curves: Include curve values in snapshots
            curve_names: Optional curve names for snapshots
            max_transitions_per_machine: Maximum transitions per included machine for transition progress
            prefer_pie_world: Prefer active PIE/SIE/play world before editor world
            require_pie_world: Fail instead of falling back to the editor world when no PIE/SIE/play world matches

        Returns:
            Response containing applied runtime properties and optional post-set snapshot.
        """
        try:
            params: Dict[str, Any] = {
                "actor_label": actor_label,
                "actor_name": actor_name,
                "actor_path": actor_path,
                "component_name": component_name,
                "tick_after_set": tick_after_set,
                "tick_count": tick_count,
                "tick_delta_time": tick_delta_time,
                "refresh_bone_transforms": refresh_bone_transforms,
                "include_snapshot_after": include_snapshot_after,
                "include_previous_values": include_previous_values,
                "state_machine_name": state_machine_name,
                "include_states": include_states,
                "include_state_weights": include_state_weights,
                "include_relevant_anim_times": include_relevant_anim_times,
                "include_transition_progress": include_transition_progress,
                "include_inactive_transition_progress": include_inactive_transition_progress,
                "include_montages": include_montages,
                "include_curves": include_curves,
                "max_transitions_per_machine": max_transitions_per_machine,
                "prefer_pie_world": prefer_pie_world,
                "require_pie_world": require_pie_world,
            }
            if properties is not None:
                params["properties"] = properties
            if property_name:
                params["property_name"] = property_name
                params["value"] = value
            if curve_names is not None:
                params["curve_names"] = curve_names
            return send_node_command("set_anim_instance_runtime_property_for_probe", params)
        except Exception as e:
            error_msg = f"Error setting AnimInstance runtime property for probe: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def sample_anim_state_machine_runtime_response(
        ctx: Context,
        actor_label: str = "",
        actor_name: str = "",
        actor_path: str = "",
        component_name: str = "",
        cases: Optional[List[Dict[str, Any]]] = None,
        properties: Optional[Dict[str, Any]] = None,
        name: str = "case_0",
        tick_count: int = 1,
        tick_delta_time: float = 1.0 / 30.0,
        refresh_bone_transforms: bool = True,
        restore_after_case: bool = True,
        include_baseline: bool = True,
        state_machine_name: str = "",
        include_states: bool = True,
        include_state_weights: bool = True,
        include_relevant_anim_times: bool = False,
        include_transition_progress: bool = True,
        include_inactive_transition_progress: bool = False,
        include_montages: bool = True,
        include_curves: bool = False,
        curve_names: Optional[List[str]] = None,
        max_state_machines: int = 32,
        max_state_machine_instances_to_probe: int = 256,
        max_states_per_machine: int = 64,
        max_transitions_per_machine: int = 128,
        max_curves: int = 128,
        prefer_pie_world: bool = True,
        require_pie_world: bool = False
    ) -> Dict[str, Any]:
        """
        Apply runtime AnimInstance property cases, tick narrowly, and sample state-machine response.

        This is a runtime probe only. By default it restores each successfully
        changed property after the case and never saves Animation Blueprint assets.

        Args:
            actor_label: Optional actor label filter
            actor_name: Optional actor object name filter
            actor_path: Optional actor path filter
            component_name: Optional SkeletalMeshComponent object name
            cases: Case list. Each case can include name, properties, tick_count, tick_delta_time, restore_after_case.
            properties: Single-case property map used when cases is omitted
            name: Single-case name used when cases is omitted
            tick_count: Default forced component animation tick count per case
            tick_delta_time: Default delta time per forced tick
            refresh_bone_transforms: Refresh component bone transforms during/after forced ticks when tick_count > 0
            restore_after_case: Restore successful property changes after each case
            include_baseline: Capture state before cases
            state_machine_name: Optional state-machine name substring filter
            include_states: Include per-state metadata
            include_state_weights: Include runtime state/machine weights
            include_relevant_anim_times: Include relevant asset-player time/remaining values per state
            include_transition_progress: Include active transition elapsed/crossfade progress
            include_inactive_transition_progress: Include inactive transition progress entries
            include_montages: Include active montage data
            include_curves: Include curve values
            curve_names: Optional curve names
            max_state_machines: Maximum state machines to include
            max_state_machine_instances_to_probe: Maximum runtime AnimNode indexes to probe
            max_states_per_machine: Maximum states per included machine
            max_transitions_per_machine: Maximum transitions per included machine for transition progress
            max_curves: Maximum curves to include
            prefer_pie_world: Prefer active PIE/SIE/play world before editor world
            require_pie_world: Fail instead of falling back to the editor world when no PIE/SIE/play world matches

        Returns:
            Response containing baseline and per-case state-machine snapshots.
        """
        try:
            params: Dict[str, Any] = {
                "actor_label": actor_label,
                "actor_name": actor_name,
                "actor_path": actor_path,
                "component_name": component_name,
                "name": name,
                "tick_count": tick_count,
                "tick_delta_time": tick_delta_time,
                "refresh_bone_transforms": refresh_bone_transforms,
                "restore_after_case": restore_after_case,
                "include_baseline": include_baseline,
                "state_machine_name": state_machine_name,
                "include_states": include_states,
                "include_state_weights": include_state_weights,
                "include_relevant_anim_times": include_relevant_anim_times,
                "include_transition_progress": include_transition_progress,
                "include_inactive_transition_progress": include_inactive_transition_progress,
                "include_montages": include_montages,
                "include_curves": include_curves,
                "max_state_machines": max_state_machines,
                "max_state_machine_instances_to_probe": max_state_machine_instances_to_probe,
                "max_states_per_machine": max_states_per_machine,
                "max_transitions_per_machine": max_transitions_per_machine,
                "max_curves": max_curves,
                "prefer_pie_world": prefer_pie_world,
                "require_pie_world": require_pie_world,
            }
            if cases is not None:
                params["cases"] = cases
            if properties is not None:
                params["properties"] = properties
            if curve_names is not None:
                params["curve_names"] = curve_names
            return send_node_command("sample_anim_state_machine_runtime_response", params)
        except Exception as e:
            error_msg = f"Error sampling AnimInstance state-machine runtime response: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_anim_graph_rigidbody_settings(
        ctx: Context,
        blueprint_name: str,
        node_id: str = "",
        alpha = None,
        external_force = None,
        simulation_space: str = "",
        enable_world_geometry = None,
        allow_non_sample: bool = False,
        graph_name: str = "AnimGraph",
        graph_id: str = "",
        graph_type: str = "function"
    ) -> Dict[str, Any]:
        """
        Set a narrow set of RigidBody AnimGraph node settings.

        By default this refuses to modify Animation Blueprints outside `/Game/_MCP_Sample/`.

        Args:
            blueprint_name: Animation Blueprint name or path
            node_id: Optional RigidBody node GUID filter
            alpha: Optional RigidBody alpha value
            external_force: Optional [X, Y, Z] external force vector
            simulation_space: Optional ComponentSpace, WorldSpace, or BaseBoneSpace
            enable_world_geometry: Optional world geometry collision toggle
            allow_non_sample: Allow editing non-`/Game/_MCP_Sample/` assets
            graph_name: Target animation graph name, defaults to AnimGraph
            graph_id: Optional target graph GUID
            graph_type: Graph selector type, defaults to function

        Returns:
            Response containing updated RigidBody node metadata and reflected settings.
        """
        try:
            params = {
                "blueprint_name": blueprint_name,
                "node_id": node_id,
                "allow_non_sample": allow_non_sample,
            }
            if alpha is not None:
                params["alpha"] = alpha
            if external_force is not None:
                params["external_force"] = external_force
            if simulation_space:
                params["simulation_space"] = simulation_space
            if enable_world_geometry is not None:
                params["enable_world_geometry"] = enable_world_geometry
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("set_anim_graph_rigidbody_settings", params)
        except Exception as e:
            error_msg = f"Error setting AnimGraph RigidBody settings: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def ensure_anim_graph_input_pose_passthrough(
        ctx: Context,
        blueprint_name: str,
        graph_name: str = "AnimGraph",
        graph_id: str = "",
        graph_type: str = "function",
        replace_existing: bool = False,
        input_node_position = None,
        allow_non_sample: bool = False
    ) -> Dict[str, Any]:
        """
        Ensure an Animation Blueprint AnimGraph passes the incoming input pose to the root output.

        This is intended for Post Process AnimBP learning/setup: it creates or reuses a
        Linked Input Pose node and connects its pose output to the AnimGraph root Result pin.

        Args:
            blueprint_name: Anim Blueprint name or path
            graph_name: Target animation graph name, defaults to AnimGraph
            graph_id: Optional target graph GUID
            graph_type: Graph selector type, defaults to function because AnimGraph is reported there
            replace_existing: Replace an existing root Result pose link when it is not the input pose
            input_node_position: Optional [X, Y] position for a newly created input pose node
            allow_non_sample: Allow editing non-`/Game/_MCP_Sample/` AnimBPs

        Returns:
            Response containing created/reused node metadata and connection status.
        """
        try:
            if input_node_position is None:
                input_node_position = [-320, 0]
            params = {
                "blueprint_name": blueprint_name,
                "replace_existing": replace_existing,
                "input_node_position": input_node_position,
                "allow_non_sample": allow_non_sample,
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("ensure_anim_graph_input_pose_passthrough", params)
        except Exception as e:
            error_msg = f"Error ensuring AnimGraph input pose pass-through: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def ensure_anim_graph_modify_bone_demo(
        ctx: Context,
        blueprint_name: str,
        bone_name: str = "head",
        rotation = None,
        graph_name: str = "AnimGraph",
        graph_id: str = "",
        graph_type: str = "function",
        replace_existing: bool = False,
        allow_non_sample: bool = False
    ) -> Dict[str, Any]:
        """
        Ensure an AnimGraph contains a safe Modify Bone demonstration chain.

        The resulting chain is:
        Linked Input Pose -> Local To Component Space -> Transform (Modify) Bone ->
        Component To Local Space -> Root Result.

        Args:
            blueprint_name: Anim Blueprint name or path
            bone_name: Bone to modify, defaults to head
            rotation: Optional [Pitch, Yaw, Roll] additive rotation in bone space
            graph_name: Target animation graph name, defaults to AnimGraph
            graph_id: Optional target graph GUID
            graph_type: Graph selector type, defaults to function because AnimGraph is reported there
            replace_existing: Replace existing pose links on the target chain pins
            allow_non_sample: Allow editing non-`/Game/_MCP_Sample/` AnimBPs

        Returns:
            Response containing chain node metadata and connection status.
        """
        try:
            if rotation is None:
                rotation = [0, 0, 6]
            params = {
                "blueprint_name": blueprint_name,
                "bone_name": bone_name,
                "rotation": rotation,
                "replace_existing": replace_existing,
                "allow_non_sample": allow_non_sample,
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("ensure_anim_graph_modify_bone_demo", params)
        except Exception as e:
            error_msg = f"Error ensuring AnimGraph Modify Bone demo chain: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def ensure_postprocess_anim_demo_variant(
        ctx: Context,
        source_blueprint_name: str,
        source_skeletal_mesh: str,
        variant_name: str = "Variant",
        target_root: str = "/Game/_MCP_Sample/AnimStudy",
        target_blueprint_name: str = "",
        target_skeletal_mesh: str = "",
        bone_name: str = "head",
        rotation = None,
        graph_name: str = "AnimGraph",
        graph_id: str = "",
        graph_type: str = "function",
        replace_existing: bool = True,
        overwrite_existing: bool = False,
        compile: bool = True,
        save: bool = True,
        dry_run: bool = False,
        allow_non_sample: bool = False
    ) -> Dict[str, Any]:
        """
        Create or reuse a sample Post Process AnimBP demo variant and assign it to a duplicated SkeletalMesh.

        The command duplicates the source AnimBP/SkeletalMesh to target sample paths, ensures the
        target AnimGraph contains the Modify Bone demo chain, compiles the AnimBP, and sets the
        target SkeletalMesh Post Process AnimBlueprint to the generated class.

        Args:
            source_blueprint_name: Source Anim Blueprint name or path to duplicate
            source_skeletal_mesh: Source SkeletalMesh path to duplicate
            variant_name: Name segment used for default target paths
            target_root: Target content folder, defaults to /Game/_MCP_Sample/AnimStudy
            target_blueprint_name: Optional explicit target AnimBP package path
            target_skeletal_mesh: Optional explicit target SkeletalMesh package path
            bone_name: Bone to modify in the Post Process AnimGraph
            rotation: Optional [Pitch, Yaw, Roll] additive rotation in bone space
            graph_name: Target animation graph name, defaults to AnimGraph
            graph_id: Optional target graph GUID
            graph_type: Graph selector type, defaults to function
            replace_existing: Replace existing pose links needed for the demo chain
            overwrite_existing: Delete and recreate existing target assets instead of reusing them
            compile: Compile the target AnimBP before assigning it
            save: Save target AnimBP and SkeletalMesh assets
            dry_run: Validate and report paths without editing assets
            allow_non_sample: Allow target paths outside /Game/_MCP_Sample

        Returns:
            Response with target asset paths, graph result, compile result, and save result.
        """
        try:
            if rotation is None:
                rotation = [0, 0, 6]
            params = {
                "source_blueprint_name": source_blueprint_name,
                "source_skeletal_mesh": source_skeletal_mesh,
                "variant_name": variant_name,
                "target_root": target_root,
                "bone_name": bone_name,
                "rotation": rotation,
                "replace_existing": replace_existing,
                "overwrite_existing": overwrite_existing,
                "compile": compile,
                "save": save,
                "dry_run": dry_run,
                "allow_non_sample": allow_non_sample,
            }
            if target_blueprint_name:
                params["target_blueprint_name"] = target_blueprint_name
            if target_skeletal_mesh:
                params["target_skeletal_mesh"] = target_skeletal_mesh
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("ensure_postprocess_anim_demo_variant", params)
        except Exception as e:
            error_msg = f"Error ensuring Post Process AnimBP demo variant: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def ensure_anim_graph_modify_curve_demo(
        ctx: Context,
        blueprint_name: str,
        curve_values: Optional[Dict[str, float]] = None,
        alpha: float = 1.0,
        apply_mode: str = "Add",
        graph_name: str = "AnimGraph",
        graph_id: str = "",
        graph_type: str = "function",
        replace_existing: bool = False,
        allow_non_sample: bool = False
    ) -> Dict[str, Any]:
        """
        Ensure an AnimGraph contains a safe Modify Curve demonstration chain.

        The resulting chain is:
        Linked Input Pose -> Modify Curve -> Root Result.

        By default this command only modifies `/Game/_MCP_Sample/` AnimBPs.
        The default curve values are tuned for the StackOBot ControlRig gate study:
        IK_blend_interact=1.0 and IKBlend_l=1.0.

        Args:
            blueprint_name: Anim Blueprint name or path
            curve_values: Optional curve name to value map
            alpha: Modify Curve alpha, clamped by Unreal to 0..1
            apply_mode: Add, Scale, Blend, WeightedMovingAverage, or RemapCurve
            graph_name: Target animation graph name, defaults to AnimGraph
            graph_id: Optional target graph GUID
            graph_type: Graph selector type, defaults to function because AnimGraph is reported there
            replace_existing: Replace existing pose links on the target chain pins
            allow_non_sample: Allow editing non-`/Game/_MCP_Sample/` AnimBPs

        Returns:
            Response containing chain node metadata and reflected Modify Curve settings.
        """
        try:
            if curve_values is None:
                curve_values = {
                    "IK_blend_interact": 1.0,
                    "IKBlend_l": 1.0,
                }
            params = {
                "blueprint_name": blueprint_name,
                "curve_values": curve_values,
                "alpha": alpha,
                "apply_mode": apply_mode,
                "replace_existing": replace_existing,
                "allow_non_sample": allow_non_sample,
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("ensure_anim_graph_modify_curve_demo", params)
        except Exception as e:
            error_msg = f"Error ensuring AnimGraph Modify Curve demo chain: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def set_anim_graph_controlrig_input_defaults(
        ctx: Context,
        blueprint_name: str,
        input_defaults: Optional[Dict[str, Any]] = None,
        graph_name: str = "AnimGraph",
        graph_id: str = "",
        graph_type: str = "function",
        node_id: str = "",
        node_name: str = "",
        title_contains: str = "",
        control_rig_class: str = "",
        disconnect_existing_links: bool = False,
        allow_non_sample: bool = False
    ) -> Dict[str, Any]:
        """
        Expose ControlRig AnimGraph input pins and set their default values.

        By default this command only modifies `/Game/_MCP_Sample/` AnimBPs.
        The default inputs are tuned for the StackOBot ControlRig forced-driver study:
        ShouldDoIKTrace=true and InteractionWorldLocation=[80, -40, 80].

        Args:
            blueprint_name: Anim Blueprint name or path
            input_defaults: Optional input/control name to value map
            graph_name: Target animation graph name, defaults to AnimGraph
            graph_id: Optional target graph GUID
            graph_type: Graph selector type, defaults to function because AnimGraph is reported there
            node_id: Optional ControlRig node GUID or object name filter
            node_name: Optional ControlRig node object name filter
            title_contains: Optional ControlRig node title substring filter
            control_rig_class: Optional ControlRig generated class path or substring filter
            disconnect_existing_links: Disconnect existing links on target pins so defaults drive the sample
            allow_non_sample: Allow editing non-`/Game/_MCP_Sample/` AnimBPs

        Returns:
            Response containing node metadata, available input names, and applied defaults.
        """
        try:
            if input_defaults is None:
                input_defaults = {
                    "ShouldDoIKTrace": True,
                    "InteractionWorldLocation": [80, -40, 80],
                }
            params = {
                "blueprint_name": blueprint_name,
                "input_defaults": input_defaults,
                "disconnect_existing_links": disconnect_existing_links,
                "allow_non_sample": allow_non_sample,
            }
            if node_id:
                params["node_id"] = node_id
            if node_name:
                params["node_name"] = node_name
            if title_contains:
                params["title_contains"] = title_contains
            if control_rig_class:
                params["control_rig_class"] = control_rig_class
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("set_anim_graph_controlrig_input_defaults", params)
        except Exception as e:
            error_msg = f"Error setting ControlRig AnimGraph input defaults: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def ensure_controlrig_forced_driver_animbp(
        ctx: Context,
        blueprint_name: str,
        curve_values: Optional[Dict[str, float]] = None,
        input_defaults: Optional[Dict[str, Any]] = None,
        alpha: float = 1.0,
        apply_mode: str = "Add",
        graph_name: str = "AnimGraph",
        graph_id: str = "",
        graph_type: str = "function",
        node_id: str = "",
        node_name: str = "",
        title_contains: str = "",
        control_rig_class: str = "",
        replace_existing: bool = True,
        disconnect_existing_links: bool = True,
        allow_non_sample: bool = False
    ) -> Dict[str, Any]:
        """
        Ensure a sample AnimBP has a forced ControlRig driver path.

        The command inserts a Modify Curve node directly before the selected
        ControlRig node, sets forced curve values, exposes/sets ControlRig input
        defaults, and can disconnect existing input links so defaults drive the sample.

        By default this command only modifies `/Game/_MCP_Sample/` AnimBPs.

        Args:
            blueprint_name: Anim Blueprint name or path
            curve_values: Optional curve name to value map
            input_defaults: Optional ControlRig input/control name to value map
            alpha: Modify Curve alpha, clamped by Unreal to 0..1
            apply_mode: Add, Scale, Blend, WeightedMovingAverage, or RemapCurve
            graph_name: Target animation graph name, defaults to AnimGraph
            graph_id: Optional target graph GUID
            graph_type: Graph selector type, defaults to function because AnimGraph is reported there
            node_id: Optional ControlRig node GUID or object name filter
            node_name: Optional ControlRig node object name filter
            title_contains: Optional ControlRig node title substring filter
            control_rig_class: Optional ControlRig generated class path or substring filter
            replace_existing: Replace pose links needed to insert Modify Curve before ControlRig
            disconnect_existing_links: Disconnect target ControlRig input links so defaults drive the sample
            allow_non_sample: Allow editing non-`/Game/_MCP_Sample/` AnimBPs

        Returns:
            Response containing ControlRig/ModifyCurve node metadata, applied curves, and input defaults.
        """
        try:
            if curve_values is None:
                curve_values = {
                    "IK_blend_interact": 1.0,
                    "IKBlend_l": 1.0,
                }
            if input_defaults is None:
                input_defaults = {
                    "ShouldDoIKTrace": True,
                    "InteractionWorldLocation": [80, -40, 80],
                }
            params = {
                "blueprint_name": blueprint_name,
                "curve_values": curve_values,
                "input_defaults": input_defaults,
                "alpha": alpha,
                "apply_mode": apply_mode,
                "replace_existing": replace_existing,
                "disconnect_existing_links": disconnect_existing_links,
                "allow_non_sample": allow_non_sample,
            }
            if node_id:
                params["node_id"] = node_id
            if node_name:
                params["node_name"] = node_name
            if title_contains:
                params["title_contains"] = title_contains
            if control_rig_class:
                params["control_rig_class"] = control_rig_class
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("ensure_controlrig_forced_driver_animbp", params)
        except Exception as e:
            error_msg = f"Error ensuring ControlRig forced-driver AnimBP: {e}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}

    @mcp.tool()
    def ensure_anim_graph_trail_demo(
        ctx: Context,
        blueprint_name: str,
        trail_bone: str = "VB VBHead",
        base_joint: str = "head",
        chain_length: int = 2,
        chain_bone_axis: str = "X",
        alpha: float = 1.0,
        fake_velocity = None,
        graph_name: str = "AnimGraph",
        graph_id: str = "",
        graph_type: str = "function",
        replace_existing: bool = False,
        allow_non_sample: bool = False,
        invert_chain_bone_axis: bool = False,
        reorient_parent_to_child: bool = True,
        actor_space_fake_velocity: bool = False,
        relaxation_speed_scale: float = 1.0,
        limit_stretch: bool = False,
        stretch_limit: float = 0.0,
        max_delta_time: float = 0.0
    ) -> Dict[str, Any]:
        """
        Ensure an AnimGraph contains a Trail Controller demonstration chain.

        The resulting chain is:
        Linked Input Pose -> Local To Component Space -> Trail ->
        Component To Local Space -> Root Result.

        By default this command only modifies `/Game/_MCP_Sample/` AnimBPs.

        Args:
            blueprint_name: Anim Blueprint name or path
            trail_bone: Active trail bone, defaults to StackOBot's VB VBHead
            base_joint: Base joint for velocity, defaults to head
            chain_length: Number of bones in the trail chain, minimum 2
            chain_bone_axis: X, Y, or Z
            alpha: Trail node alpha
            fake_velocity: Optional [X, Y, Z] fake velocity for static preview tests
            graph_name: Target animation graph name, defaults to AnimGraph
            graph_id: Optional target graph GUID
            graph_type: Graph selector type, defaults to function because AnimGraph is reported there
            replace_existing: Replace existing pose links on the target chain pins
            allow_non_sample: Allow editing non-`/Game/_MCP_Sample/` AnimBPs
            invert_chain_bone_axis: Invert the selected chain bone axis
            reorient_parent_to_child: Reorient parent bones toward children
            actor_space_fake_velocity: Apply fake velocity in actor space instead of world space
            relaxation_speed_scale: Trail relaxation scale
            limit_stretch: Enable stretch limiting
            stretch_limit: Stretch limit when enabled
            max_delta_time: Optional timestep clamp

        Returns:
            Response containing chain node metadata and reflected Trail settings.
        """
        try:
            if fake_velocity is None:
                fake_velocity = [0, 0, 0]
            params = {
                "blueprint_name": blueprint_name,
                "trail_bone": trail_bone,
                "base_joint": base_joint,
                "chain_length": chain_length,
                "chain_bone_axis": chain_bone_axis,
                "alpha": alpha,
                "fake_velocity": fake_velocity,
                "replace_existing": replace_existing,
                "allow_non_sample": allow_non_sample,
                "invert_chain_bone_axis": invert_chain_bone_axis,
                "reorient_parent_to_child": reorient_parent_to_child,
                "actor_space_fake_velocity": actor_space_fake_velocity,
                "relaxation_speed_scale": relaxation_speed_scale,
                "limit_stretch": limit_stretch,
                "stretch_limit": stretch_limit,
                "max_delta_time": max_delta_time,
            }
            add_graph_selector(params, graph_name, graph_id, graph_type)
            return send_node_command("ensure_anim_graph_trail_demo", params)
        except Exception as e:
            error_msg = f"Error ensuring AnimGraph Trail demo chain: {e}"
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
        target_class: str = "",
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
            target_class: Optional class path/name for external object member variables

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
            if target_class:
                params["target_class"] = target_class
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
