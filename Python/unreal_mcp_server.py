"""
Unreal Engine MCP Server

A simple MCP server for interacting with Unreal Engine.
"""

import logging
import os
import socket
import sys
import json
from contextlib import asynccontextmanager
from typing import AsyncIterator, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP

# Configure logging with more detailed format
logging.basicConfig(
    level=os.environ.get("UNREAL_MCP_LOG_LEVEL", "INFO").upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.FileHandler('unreal_mcp.log'),
        # logging.StreamHandler(sys.stdout) # Remove this handler to unexpected non-whitespace characters in JSON
    ]
)
logger = logging.getLogger("UnrealMCP")

# Configuration
UNREAL_HOST = "127.0.0.1"
UNREAL_PORT = 55557
UNREAL_RESPONSE_TIMEOUT_SECONDS = int(os.environ.get("UNREAL_MCP_RESPONSE_TIMEOUT_SECONDS", "120"))
UNREAL_MCP_LOG_PAYLOAD_CHARS = int(os.environ.get("UNREAL_MCP_LOG_PAYLOAD_CHARS", "1200"))

def _summarize_for_log(value: Any, max_chars: int = UNREAL_MCP_LOG_PAYLOAD_CHARS) -> str:
    """Return a bounded JSON-ish representation for operational logs."""
    try:
        text = json.dumps(value, ensure_ascii=False, default=str)
    except Exception:
        text = str(value)
    if len(text) <= max_chars:
        return text
    return f"{text[:max_chars]}... <truncated {len(text) - max_chars} chars>"

class UnrealConnection:
    """Connection to an Unreal Engine instance."""
    
    def __init__(self):
        """Initialize the connection."""
        self.socket = None
        self.connected = False
    
    def connect(self) -> bool:
        """Connect to the Unreal Engine instance."""
        try:
            # Close any existing socket
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            
            logger.info(f"Connecting to Unreal at {UNREAL_HOST}:{UNREAL_PORT}...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.settimeout(UNREAL_RESPONSE_TIMEOUT_SECONDS)
            
            # Set socket options for better stability
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Set larger buffer sizes
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
            
            self.socket.connect((UNREAL_HOST, UNREAL_PORT))
            self.connected = True
            logger.info("Connected to Unreal Engine")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Unreal: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """Disconnect from the Unreal Engine instance."""
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.socket = None
        self.connected = False

    def receive_full_response(self, sock, buffer_size=4096) -> bytes:
        """Receive a complete response from Unreal, handling chunked data."""
        chunks = []
        sock.settimeout(UNREAL_RESPONSE_TIMEOUT_SECONDS)
        try:
            while True:
                chunk = sock.recv(buffer_size)
                if not chunk:
                    if not chunks:
                        raise Exception("Connection closed before receiving data")
                    break
                chunks.append(chunk)
                
                # Process the data received so far
                data = b''.join(chunks)
                try:
                    decoded_data = data.decode('utf-8')
                    json.loads(decoded_data)
                    logger.info(f"Received complete response ({len(data)} bytes)")
                    return data
                except UnicodeDecodeError:
                    logger.debug("Received partial UTF-8 sequence, waiting for more data...")
                    continue
                except json.JSONDecodeError:
                    # Not complete JSON yet, continue reading
                    logger.debug(f"Received partial response, waiting for more data...")
                    continue
                except Exception as e:
                    logger.warning(f"Error processing response chunk: {str(e)}")
                    continue
        except socket.timeout:
            logger.warning("Socket timeout during receive")
            if chunks:
                # If we have some data already, try to use it
                data = b''.join(chunks)
                try:
                    json.loads(data.decode('utf-8'))
                    logger.info(f"Using partial response after timeout ({len(data)} bytes)")
                    return data
                except:
                    pass
            raise Exception("Timeout receiving Unreal response")
        except Exception as e:
            logger.error(f"Error during receive: {str(e)}")
            raise
    
    def send_command(self, command: str, params: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """Send a command to Unreal Engine and get the response."""
        # Always reconnect for each command, since Unreal closes the connection after each command
        # This is different from Unity which keeps connections alive
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self.connected = False
        
        if not self.connect():
            logger.error("Failed to connect to Unreal Engine for command")
            return None
        
        try:
            # Match Unity's command format exactly
            command_obj = {
                "type": command,  # Use "type" instead of "command"
                "params": params or {}  # Use Unity's params or {} pattern
            }
            
            # Send without newline, exactly like Unity
            command_json = json.dumps(command_obj)
            logger.info(
                "Sending command '%s' (%d bytes): %s",
                command,
                len(command_json.encode("utf-8")),
                _summarize_for_log(command_obj),
            )
            self.socket.sendall(command_json.encode('utf-8'))
            
            # Read response using improved handler
            response_data = self.receive_full_response(self.socket)
            response = json.loads(response_data.decode('utf-8'))
            
            logger.info(
                "Complete response from Unreal for '%s': %s",
                command,
                _summarize_for_log(response),
            )
            
            # Check for both error formats: {"status": "error", ...} and {"success": false, ...}
            if response.get("status") == "error":
                error_message = response.get("error") or response.get("message", "Unknown Unreal error")
                logger.error(f"Unreal error (status=error): {error_message}")
                # We want to preserve the original error structure but ensure error is accessible
                if "error" not in response:
                    response["error"] = error_message
            elif response.get("success") is False:
                # This format uses {"success": false, "error": "message"} or {"success": false, "message": "message"}
                error_message = response.get("error") or response.get("message", "Unknown Unreal error")
                logger.error(f"Unreal error (success=false): {error_message}")
                response.setdefault("status", "error")
                response.setdefault("error", error_message)
            
            # Always close the connection after command is complete
            # since Unreal will close it on its side anyway
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self.connected = False
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending command: {e}")
            # Always reset connection state on any error
            self.connected = False
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            return {
                "status": "error",
                "error": str(e)
            }

# Global connection state
_unreal_connection: UnrealConnection = None

def get_unreal_connection() -> Optional[UnrealConnection]:
    """Get the connection to Unreal Engine."""
    global _unreal_connection
    try:
        if _unreal_connection is None:
            _unreal_connection = UnrealConnection()
            if not _unreal_connection.connect():
                logger.warning("Could not connect to Unreal Engine")
                _unreal_connection = None
        elif not _unreal_connection.connected or _unreal_connection.socket is None:
            _unreal_connection = UnrealConnection()
            if not _unreal_connection.connect():
                logger.warning("Could not reconnect to Unreal Engine")
                _unreal_connection = None
        
        return _unreal_connection
    except Exception as e:
        logger.error(f"Error getting Unreal connection: {e}")
        return None

@asynccontextmanager
async def server_lifespan(server: FastMCP) -> AsyncIterator[Dict[str, Any]]:
    """Handle server startup and shutdown."""
    global _unreal_connection
    logger.info("UnrealMCP server starting up")
    try:
        _unreal_connection = get_unreal_connection()
        if _unreal_connection:
            logger.info("Connected to Unreal Engine on startup")
        else:
            logger.warning("Could not connect to Unreal Engine on startup")
    except Exception as e:
        logger.error(f"Error connecting to Unreal Engine on startup: {e}")
        _unreal_connection = None
    
    try:
        yield {}
    finally:
        if _unreal_connection:
            _unreal_connection.disconnect()
            _unreal_connection = None
        logger.info("Unreal MCP server shut down")

# Initialize server
mcp = FastMCP(
    "UnrealMCP",
    description="Unreal Engine integration via Model Context Protocol",
    lifespan=server_lifespan
)

# Import and register tools
from tools.editor_tools import register_editor_tools
from tools.blueprint_tools import register_blueprint_tools
from tools.node_tools import register_blueprint_node_tools
from tools.project_tools import register_project_tools
from tools.umg_tools import register_umg_tools
from tools.python_tools import register_python_tools
from tools.pcg_tools import register_pcg_tools
from tools.material_tools import register_material_tools
from tools.niagara_tools import register_niagara_tools
from tools.texture_generation import register_texture_generation_tools
from tools.ieta_tools import register_ieta_tools
from tools.niagara_tools import register_niagara_tools

# Register tools
register_editor_tools(mcp)
register_blueprint_tools(mcp)
register_blueprint_node_tools(mcp)
register_project_tools(mcp)
register_umg_tools(mcp)  
register_python_tools(mcp)
register_pcg_tools(mcp)
register_material_tools(mcp)
register_niagara_tools(mcp)
register_texture_generation_tools(mcp)
register_ieta_tools(mcp)
register_niagara_tools(mcp)

@mcp.prompt()
def info():
    """Information about available Unreal MCP tools and best practices."""
    return """
    # Unreal MCP Server Tools and Best Practices
    
    ## UMG (Widget Blueprint) Tools
    - `create_umg_widget_blueprint(widget_name, parent_class="UserWidget", path="/Game/UI")` 
      Create a new UMG Widget Blueprint
    - `add_text_block_to_widget(widget_name, text_block_name, text="", position=[0,0], size=[200,50], font_size=12, color=[1,1,1,1])`
      Add a Text Block widget with customizable properties
    - `add_button_to_widget(widget_name, button_name, text="", position=[0,0], size=[200,50], font_size=12, color=[1,1,1,1], background_color=[0.1,0.1,0.1,1])`
      Add a Button widget with text and styling
    - `bind_widget_event(widget_name, widget_component_name, event_name, function_name="")`
      Bind events like OnClicked to functions
    - `add_widget_to_viewport(widget_name, z_order=0)`
      Add widget instance to game viewport
    - `set_text_block_binding(widget_name, text_block_name, binding_property, binding_type="Text")`
      Set up dynamic property binding for text blocks

    ## Editor Tools
    ### Viewport and Screenshots
    - `focus_viewport(target, location, distance, orientation)` - Focus viewport
    - `take_screenshot(filename, show_ui, resolution)` - Capture screenshots
    - `open_niagara_preview_player(system_path="")` - Open the level-independent Niagara Preview Player Slate drop surface and optionally load a Niagara System
    - `get_niagara_preview_player_state()` - Inspect Niagara Preview Player window and latest dropped asset/actor state
    - `get_niagara_preview_lab_state()` - Inspect Niagara Preview Lab map, dirty, and preview actor safety state
    - `cleanup_niagara_preview_lab()` - Delete Niagara Preview Lab preview actors without saving or reloading the map
    - `capture_niagara_preview_lab_view(filepath, view=1)` - Capture a clean Niagara Preview Lab PNG; auto-frames preview actors when present
    - `preview_niagara_system_in_preview_lab(system_path, filepath, view=1, label="", warmup_time=0.35, cleanup_after=True)` - One-call optimized Niagara preview: spawn, warm up, auto-frame capture, and optional cleanup
    - `sample_niagara_system_in_preview_lab(system_path, output_dir="", label="", warmup_times=[...], views=[...])` - Multi-candidate optimized Niagara preview sampling in one MCP round trip

    ## Niagara Authoring
    - `analyze_niagara_system(system_path)` - Aggregate read-only Niagara renderer, user parameter, stack, graph, module-input, and compile inspection
    - `inspect_niagara_renderers(system_path)` - Inspect enabled Niagara renderers and material slots
    - `set_niagara_renderer_material(system_path, material_path, emitter_index=None, emitter_name="", renderer_index=None, material_slot_index=0, allow_source_edit=False, save=True)` - Set renderer material, temp/generated assets only by default
    - `inspect_niagara_user_parameters(system_path)` - Inspect exposed User parameters and current values
    - `set_niagara_user_parameter(system_path, parameter_name, value, allow_source_edit=False, save=True)` - Set supported User parameter values
    - `inspect_niagara_stack(system_path, include_pins=False, max_function_calls=200)` - Inspect system/emitter/scratch-pad function calls
    - `inspect_niagara_graph(system_path, include_pins=True, include_links=True)` - Inspect full Niagara graph nodes, pins, links, and scratch-pad graphs
    - `inspect_niagara_scratch_pad_interface(system_path, include_graph_summary=True, include_parent_scratch_pads=True)` - Inspect Scratch Pad inputs/outputs/usages as a read-only authoring interface
    - `duplicate_or_attach_emitter_from_source(target_system_path, source_emitter_path="", source_system_path="", source_emitter_index=None, source_emitter_name="", new_emitter_name="", enabled=None, allow_source_edit=False, save=True, request_compile=True)` - Add a source emitter into a generated temp Niagara System
    - `create_or_duplicate_scratch_pad_module(target_system_path, source_script_path="", source_system_path="", source_owner_kind="system", source_script_index=None, source_scratch_pad_name="", source_emitter_index=None, source_emitter_name="", target_owner_kind="system", target_emitter_index=None, target_emitter_name="", new_script_name="", allow_source_edit=False, save=True, request_compile=True)` - Duplicate an existing Scratch Pad script into a generated temp Niagara System or emitter
    - `add_scratch_pad_module_to_stack(target_system_path, scratch_pad_script_path="", scratch_pad_owner_kind="system", scratch_pad_script_index=None, scratch_pad_name="", scratch_pad_emitter_index=None, scratch_pad_emitter_name="", target_usage="ParticleUpdateScript", target_usage_id="", target_emitter_index=None, target_emitter_name="", target_index=None, suggested_name="", allow_source_edit=False, save=True, request_compile=True, skip_if_duplicate=True)` - Insert a target-local Scratch Pad module into a Niagara stack
    - `inspect_niagara_compile_status(system_path, request_compile=False, force=False, allow_source_compile=False, wait_for_completion=False)` - Inspect Niagara script compile status and outstanding requests
    - `inspect_niagara_module_inputs(system_path, include_linked_sources=True, include_resolved_stack_inputs=False)` - Inspect module input candidates for generation planning
    - `create_niagara_module_input_override(system_path, input_name, value, emitter_index=None, emitter_name="", module_index=None, module_name="", module_node_guid="", overwrite_existing=False, allow_source_edit=False, save=True, request_compile=True)` - Create a missing RapidIteration module input override, temp/generated assets only by default
    - `set_niagara_module_inputs_batch(system_path, edits, operation="set_existing", overwrite_existing=False, continue_on_error=False, allow_source_edit=False, save=True, request_compile=True)` - Apply multiple RapidIteration module input edits, compile once, and save once
    - `set_niagara_module_input_value(system_path, input_name, value, emitter_index=None, emitter_name="", module_index=None, module_name="", module_node_guid="", allow_source_edit=False, save=True, request_compile=True)` - Set an existing RapidIteration module input override

    ### Actor Management
    - `get_actors_in_level()` - List all actors in current level
    - `find_actors_by_name(pattern)` - Find actors by name pattern
    - `spawn_actor(name, type, location=[0,0,0], rotation=[0,0,0], scale=[1,1,1])` - Create actors
    - `delete_actor(name)` - Remove actors
    - `set_actor_transform(name, location, rotation, scale)` - Modify actor transform
    - `get_actor_properties(name)` - Get actor properties
    
    ## Blueprint Management
    - `create_blueprint(name, parent_class)` - Create new Blueprint classes
    - `add_component_to_blueprint(blueprint_name, component_type, component_name, parent_component_name?)` - Add components
    - `list_blueprint_components(blueprint_name, component_name="")` - List Blueprint SCS components and defaults
    - `get_component_property(blueprint_name, component_name, property_name)` - Read component template properties
    - `set_static_mesh_properties(blueprint_name, component_name, static_mesh)` - Configure meshes
    - `set_physics_properties(blueprint_name, component_name)` - Configure physics
    - `compile_blueprint(blueprint_name)` - Compile Blueprint changes
    - `compile_and_validate_blueprint(blueprint_name, save=False, refresh_nodes=True)` - Compile and return validation status
    - `set_blueprint_property(blueprint_name, property_name, property_value)` - Set properties
    - `set_pawn_properties(blueprint_name)` - Configure Pawn settings
    - `spawn_blueprint_actor(blueprint_name, actor_name)` - Spawn Blueprint actors
    
    ## Blueprint Node Management
    - `list_blueprint_graphs(blueprint_name, graph_type="")` - List Blueprint graphs with graph_id metadata
    - `resolve_blueprint_graph(blueprint_name, graph_name="", graph_id="", graph_type="", create_if_missing=False)` - Resolve or create a Blueprint graph
    - `add_blueprint_event_node(blueprint_name, event_type)` - Add event nodes
    - `add_blueprint_input_action_node(blueprint_name, action_name)` - Add input nodes
    - `add_blueprint_function_node(blueprint_name, target, function_name)` - Add function nodes
    - `add_blueprint_branch_node(blueprint_name)` - Add Branch control-flow node
    - `add_blueprint_sequence_node(blueprint_name, output_count=2)` - Add Sequence control-flow node
    - `add_blueprint_return_node(blueprint_name, graph_type="function")` - Add or resolve function Return node
    - `add_blueprint_dynamic_cast_node(blueprint_name, target_class)` - Add Dynamic Cast node
    - `connect_blueprint_nodes(blueprint_name, source_node_id, source_pin, target_node_id, target_pin)` - Connect nodes
    - `add_blueprint_variable(blueprint_name, variable_name, variable_type, default_value=None)` - Add member variables with defaults/metadata
    - `add_blueprint_function_parameter(blueprint_name, parameter_name, parameter_type, direction="input")` - Add function input/output pins
    - `add_blueprint_local_variable(blueprint_name, variable_name, variable_type)` - Add function-scoped local variables
    - `add_blueprint_get_self_component_reference(blueprint_name, component_name)` - Add component refs
    - `add_blueprint_self_reference(blueprint_name)` - Add self references
    - `find_blueprint_nodes(blueprint_name, node_type, event_type)` - Find nodes
    
    ## Project Tools
    - `create_input_mapping(action_name, key, input_type)` - Create input mappings

    ## Material Graph Management
    - `resolve_material_graph(material_path, graph_type="auto")` - Resolve a Material or Material Function
    - `list_material_nodes(material_path, graph_type="auto")` - List material expression nodes, pins, links, and root material property connections
    - `analyze_material_graph(material_path, graph_type="auto")` - Read-only Material/Function/Instance analysis with semantics, function/reroute metadata, cost hints, and usage hints
    - `add_material_node(material_path, expression_class)` - Add a MaterialExpression node
    - `add_custom_material_node(material_path, code, output_type="CMOT_Float3", inputs=[])` - Add a validated MaterialExpressionCustom node for Custom HLSL islands
    - `set_material_node_property(material_path, node_id, property_name, value)` - Set an expression property using node_key/node_id from list/analyze output
    - `connect_material_nodes(material_path, from_node_id, to_node_id, to_input, from_output="")` - Connect expression nodes using node_key/node_id values
    - `connect_material_property(material_path, from_node_id, property, from_output="")` - Connect an expression to BaseColor/Roughness/Normal/etc.
    - `delete_material_node(material_path, node_id)` - Delete an expression node using node_key/node_id
    - `layout_material_nodes(material_path)` - Layout expression nodes
    - `compile_and_save_material(material_path)` - Recompile/update and save a Material or Material Function
    - `expand_material_function_calls(material_path)` - Expand Material Function Call nodes into the owning Material graph; partial saves require allow_partial_save=True
    - `get_material_parameter_collection_values(collection_path)` - Read MPC asset defaults and current editor-world runtime values

    ## AI Texture Generation
    - `get_static_mesh_uv_layout(mesh_path, uv_channel, output_path)` - Export a Static Mesh UV wireframe PNG
    - `generate_texture_from_prompt(prompt, output_name, output_dir, size)` - Generate a BaseColor PNG with GPT Image
    - `generate_texture_for_mesh_uv(mesh_path, prompt, uv_channel, output_name, output_dir, size)` - Generate a UV-guided texture PNG
    - `import_texture_to_unreal(image_path, unreal_folder, asset_name)` - Import a PNG as Texture2D
    - `create_material_instance_with_texture(texture_asset_path, material_name, unreal_folder, base_material_path)` - Create a BaseColor material/material instance
    - `apply_material_to_mesh(target, material_asset_path, material_slot)` - Apply a material to selected/named mesh targets
    - `generate_and_apply_ai_texture(target, prompt, output_name, unreal_folder, uv_channel, size)` - Run the full BaseColor texture pipeline

    ## Niagara Inspection and Validation
    - `list_niagara_assets(root_path="/Game", include_scripts=False, include_parameter_collections=False)` - List Niagara Systems/Emitters and optional related assets
    - `inspect_niagara_system(system_path)` - Read-only Niagara System summary with emitters, user parameters, scripts, and compile hints where Python reflection exposes them
    - `list_niagara_components(selected_only=False)` - List Niagara components in the current editor level
    - `duplicate_niagara_system_to_temp(system_path, temp_folder="/Game/_MCP_Temp")` - Duplicate a System into disposable MCP temp content for safe experiments
    - `compile_and_save_niagara_system(system_path, save=False)` - Best-effort Niagara compile/wait/poll validation; save is limited to /Game/_MCP_Temp assets
    
    ## Best Practices
    
    ### UMG Widget Development
    - Create widgets with descriptive names that reflect their purpose
    - Use consistent naming conventions for widget components
    - Organize widget hierarchy logically
    - Set appropriate anchors and alignment for responsive layouts
    - Use property bindings for dynamic updates instead of direct setting
    - Handle widget events appropriately with meaningful function names
    - Clean up widgets when no longer needed
    - Test widget layouts at different resolutions
    
    ### Editor and Actor Management
    - Use unique names for actors to avoid conflicts
    - Clean up temporary actors
    - Validate transforms before applying
    - Check actor existence before modifications
    - Take regular viewport screenshots during development
    - Keep the viewport focused on relevant actors during operations
    
    ### Blueprint Development
    - Compile Blueprints after changes
    - Use meaningful names for variables and functions
    - Organize nodes logically
    - Test functionality in isolation
    - Consider performance implications
    - Document complex setups
    
    ### Error Handling
    - Check command responses for success
    - Handle errors gracefully
    - Log important operations
    - Validate parameters
    - Clean up resources on errors
    """

# Run the server
if __name__ == "__main__":
    logger.info("Starting MCP server with stdio transport")
    mcp.run(transport='stdio') 
