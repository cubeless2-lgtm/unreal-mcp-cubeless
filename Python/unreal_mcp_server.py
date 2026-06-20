"""
Unreal Engine MCP Server

A simple MCP server for interacting with Unreal Engine.
"""

import logging
import os
import socket
import sys
import json
import time
from contextlib import asynccontextmanager
from logging.handlers import RotatingFileHandler
from typing import AsyncIterator, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP


def _get_int_env(name: str, default: int) -> int:
    try:
        return int(os.environ.get(name, str(default)))
    except (TypeError, ValueError):
        return default


class LockedSafeRotatingFileHandler(RotatingFileHandler):
    """RotatingFileHandler that tolerates Windows log-file locks."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._rollover_retry_after = 0.0

    def shouldRollover(self, record):
        if self._rollover_retry_after and time.monotonic() < self._rollover_retry_after:
            return False
        return super().shouldRollover(record)

    def doRollover(self):
        try:
            super().doRollover()
            self._rollover_retry_after = 0.0
        except OSError:
            self._rollover_retry_after = time.monotonic() + 60.0


# Configure logging with more detailed format
_log_max_bytes = max(1024, _get_int_env("UNREAL_MCP_LOG_MAX_BYTES", 5 * 1024 * 1024))
_log_backup_count = max(1, _get_int_env("UNREAL_MCP_LOG_BACKUP_COUNT", 3))
logging.basicConfig(
    level=os.environ.get("UNREAL_MCP_LOG_LEVEL", "WARNING").upper(),
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        LockedSafeRotatingFileHandler(
            'unreal_mcp.log',
            maxBytes=_log_max_bytes,
            backupCount=_log_backup_count,
            encoding='utf-8',
        ),
        # logging.StreamHandler(sys.stdout) # Remove this handler to unexpected non-whitespace characters in JSON
    ]
)
logger = logging.getLogger("UnrealMCP")


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    if value is None or value.strip() == "":
        return default
    try:
        return int(value)
    except ValueError:
        logger.warning("Invalid integer for %s: %s", name, value)
        return default


# Configuration
UNREAL_HOST = os.environ.get("UNREAL_MCP_HOST", "127.0.0.1")
UNREAL_PORT = _env_int("UNREAL_MCP_PORT", 55557)
UNREAL_RESPONSE_TIMEOUT_SECONDS = _env_int("UNREAL_MCP_RESPONSE_TIMEOUT_SECONDS", 120)
UNREAL_MCP_HEARTBEAT_TIMEOUT_SECONDS = max(1, _env_int("UNREAL_MCP_HEARTBEAT_TIMEOUT_SECONDS", 5))
UNREAL_MCP_LOG_PAYLOAD_CHARS = _env_int("UNREAL_MCP_LOG_PAYLOAD_CHARS", 1200)

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
    
    def connect(self, timeout_seconds: Optional[int] = None) -> bool:
        """Connect to the Unreal Engine instance."""
        try:
            socket_timeout = timeout_seconds or UNREAL_RESPONSE_TIMEOUT_SECONDS
            guard_decision = runtime_guard.check_bridge_target(UNREAL_HOST, UNREAL_PORT)
            if guard_decision.get("would_block"):
                request_telemetry.record_guard_event("bridge_target", f"{UNREAL_HOST}:{UNREAL_PORT}", guard_decision)
            if not guard_decision.get("allowed", True):
                logger.error("Unreal bridge connection blocked by runtime guard: %s", guard_decision.get("reason"))
                self.connected = False
                return False

            # Close any existing socket
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
            self.socket = None
            
            logger.info(f"Connecting to Unreal at {UNREAL_HOST}:{UNREAL_PORT}...")
            self.socket = socket.create_connection(
                (UNREAL_HOST, UNREAL_PORT),
                timeout=socket_timeout,
            )
            self.socket.settimeout(socket_timeout)
            
            # Set socket options for better stability
            self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            
            # Set larger buffer sizes
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
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

    def receive_full_response(self, sock, buffer_size=4096, timeout_seconds: Optional[int] = None) -> bytes:
        """Receive a complete response from Unreal, handling chunked data."""
        chunks = []
        sock.settimeout(timeout_seconds or UNREAL_RESPONSE_TIMEOUT_SECONDS)
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
    
    def send_command(
        self,
        command: str,
        params: Dict[str, Any] = None,
        timeout_seconds: Optional[int] = None,
    ) -> Optional[Dict[str, Any]]:
        """Send a command to Unreal Engine and get the response."""
        telemetry_token = request_telemetry.begin("unreal_command", command)
        # Always reconnect for each command, since Unreal closes the connection after each command
        # This is different from Unity which keeps connections alive
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
            self.socket = None
            self.connected = False
        
        if not self.connect(timeout_seconds=timeout_seconds):
            logger.error("Failed to connect to Unreal Engine for command")
            request_telemetry.end(telemetry_token, False, status="connect_failed", error="Failed to connect to Unreal Engine")
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
            response_data = self.receive_full_response(self.socket, timeout_seconds=timeout_seconds)
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
            
            success = response.get("status") != "error" and response.get("success") is not False
            request_telemetry.end(
                telemetry_token,
                success,
                status=str(response.get("status") or ("ok" if success else "error")),
                error=str(response.get("error") or response.get("message") or ""),
            )
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
            request_telemetry.end(telemetry_token, False, status="exception", error=str(e))
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


def build_unreal_health(ping_unreal: bool = False) -> Dict[str, Any]:
    """Return structured bridge health without mutating Unreal assets."""
    guard_decision = runtime_guard.check_bridge_target(UNREAL_HOST, UNREAL_PORT)
    bridge = {
        "host": UNREAL_HOST,
        "port": UNREAL_PORT,
        "guard": guard_decision,
        "status": "not_checked",
        "connected": False,
    }
    if ping_unreal:
        started = time.perf_counter()
        attempts = []
        response = None
        for attempt_index in range(2):
            connection = UnrealConnection()
            response = connection.send_command(
                "ping",
                {},
                timeout_seconds=UNREAL_MCP_HEARTBEAT_TIMEOUT_SECONDS,
            )
            connection.disconnect()
            attempts.append(
                {
                    "attempt": attempt_index + 1,
                    "success": bool(response and response.get("status") != "error" and response.get("success") is not False),
                    "status": response.get("status") if response else "no_response",
                    "error": response.get("error") if response else "No response from Unreal Engine",
                }
            )
            if attempts[-1]["success"]:
                break
        elapsed_ms = round((time.perf_counter() - started) * 1000.0, 3)
        bridge["ping_elapsed_ms"] = elapsed_ms
        bridge["response"] = response
        bridge["attempts"] = attempts
        if response and response.get("status") != "error" and response.get("success") is not False:
            bridge["status"] = "connected"
            bridge["connected"] = True
        else:
            bridge["status"] = "not connected"
            bridge["connected"] = False
        bridge["success"] = bridge["connected"]
        return {"success": bridge["connected"], "unreal_bridge": bridge}
    bridge["success"] = True
    return {"success": True, "unreal_bridge": bridge}

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
from tools.management_tools import (
    register_management_tools,
    request_telemetry,
    runtime_guard,
    set_health_provider,
    tool_registry,
)

set_health_provider(build_unreal_health)

def register_tool_group(category, register_func):
    """Register one tool group while recording runtime policy metadata."""
    with tool_registry.capture_tools(mcp, category=category):
        register_func(mcp)

# Register tools. Runtime policy defaults to all tools enabled.
register_tool_group("editor", register_editor_tools)
register_tool_group("blueprint", register_blueprint_tools)
register_tool_group("blueprint_node", register_blueprint_node_tools)
register_tool_group("project", register_project_tools)
register_tool_group("umg", register_umg_tools)
register_tool_group("python", register_python_tools)
register_tool_group("pcg", register_pcg_tools)
register_tool_group("material", register_material_tools)
register_tool_group("niagara", register_niagara_tools)
register_tool_group("texture_generation", register_texture_generation_tools)
register_tool_group("ieta", register_ieta_tools)
register_management_tools(mcp, tool_registry)

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
    - `take_screenshot(filepath)` - Capture the active editor viewport to a PNG through the legacy bridge command
    - `capture_viewport_bookmark_screenshot(filepath, bookmark_index=-1)` - Capture the active editor viewport with bookmark-aware framing
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
    - `set_niagara_scratch_pad_function_input_default(system_path, function_name="", input_pin_name="", value=None, default_value="", function_node_guid="", function_node_index=None, function_call_index=None, scratch_pad_script_path="", scratch_pad_owner_kind="system", scratch_pad_script_index=None, scratch_pad_name="", scratch_pad_emitter_index=None, scratch_pad_emitter_name="", break_links=True, allow_multi_link_break=False, allow_source_edit=False, save=True, request_compile=True)` - Set a Scratch Pad internal function input default and optionally break existing links
    - `link_niagara_scratch_pad_pin_to_user_parameter(system_path, target_pin_name, user_parameter_name, scratch_pad_name="", overwrite_existing=False, allow_source_edit=False, save=True, request_compile=True)` - Link a Scratch Pad ParameterMapSet input pin to a Vector2D User parameter
    - `wrap_niagara_scratch_pad_output_with_stack_context(system_path, target_pin_name="StackContext.RGBA", scratch_pad_name="RenderCircleToGrid", previous_stack_value_pin_name="PreviousStackValue", local_value_pin_name="LocalStampValue", expression="max(PreviousStackValue, LocalStampValue)", skip_if_already_wrapped=True, replace_existing_custom=True, allow_source_edit=False, save=True, request_compile=True)` - Wrap a Scratch Pad output pin with a Custom HLSL accumulator that combines incoming StackContext with the existing local value
    - `insert_niagara_scratch_pad_custom_hlsl_for_pin(system_path, target_pin_name, expression, scratch_pad_name="RenderGrid", inputs=None, user_parameter_inputs=None, replace_existing_custom=False, rebuild_existing_custom=False, delete_unlinked_custom_input_source_nodes=False, allow_source_edit=False, save=True, request_compile=True)` - Wrap a Scratch Pad input pin with Custom HLSL, including optional User.* ParameterMapGet inputs
    - `inspect_niagara_compile_status(system_path, request_compile=False, force=False, allow_source_compile=False, wait_for_completion=False)` - Inspect Niagara script compile status and outstanding requests
    - `inspect_niagara_simulation_stages(system_path, include_compile_data=True, include_script_compile_status=True, max_stages=128)` - Inspect protected Niagara SimulationStage settings and compilation data
    - `set_niagara_simulation_stage_settings(system_path, emitter_index=None, emitter_name="", stage_index=None, stage_name="", enabled=None, iteration_source="", direct_dispatch_type="", direct_dispatch_element_type="", execute_behavior="", element_count=None, element_count_x=None, element_count_y=None, element_count_z=None, num_iterations=None, gpu_dispatch_force_linear=None, override_gpu_dispatch_num_threads=None, allow_source_edit=False, save=True, request_compile=True)` - Edit one generic SimulationStage, temp/generated assets only by default
    - `inspect_niagara_module_inputs(system_path, include_linked_sources=True, include_resolved_stack_inputs=False)` - Inspect module input candidates for generation planning
    - `inspect_niagara_data_interface_overrides(system_path, input_name="", emitter_index=None, emitter_name="", module_index=None, module_name="", module_node_guid="", max_modules=200, max_inputs_per_module=64, include_data_interface_properties=False, max_data_interface_properties=120, max_data_interface_property_value_length=512)` - Read Niagara Data Interface module input override graph nodes and User object bindings
    - `create_niagara_module_input_override(system_path, input_name, value, emitter_index=None, emitter_name="", module_index=None, module_name="", module_node_guid="", overwrite_existing=False, allow_source_edit=False, save=True, request_compile=True)` - Create a missing RapidIteration module input override, temp/generated assets only by default
    - `set_niagara_render_target2d_module_input(system_path, input_name, user_parameter_name="User.RT_IF_Deform", render_target_asset_path="", emitter_index=None, emitter_name="", module_index=None, module_name="", module_node_guid="", inherit_user_parameter_settings=True, overwrite_existing=False, allow_source_edit=False, save=True, request_compile=True)` - Bind a RenderTarget2D data-interface module input to a User render target parameter
    - `set_niagara_module_input_user_parameter(system_path, input_name, user_parameter_name, default_value=None, emitter_index=None, emitter_name="", module_index=None, module_name="", module_node_guid="", overwrite_existing=False, allow_source_edit=False, save=True, request_compile=True)` - Bind a scalar/vector/color/bool module input to a User parameter
    - `set_niagara_module_input_linked_parameter(system_path, input_name, linked_parameter_name, emitter_index=None, emitter_name="", module_index=None, module_name="", module_node_guid="", overwrite_existing=False, allow_source_edit=False, save=True, request_compile=True)` - Link a module input to an existing namespaced Niagara parameter such as `Emitter.Grid2D Collection`
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
    - `inspect_blueprint_graph_call_topology(blueprint_name, graph_type="", reference_contains="")` - Read static Blueprint graph call/reference/link topology
    - `inspect_anim_graph_protected_topology(blueprint_name, node_type="", graph_name="AnimGraph")` - Read protected AnimGraph nodes, pins, and pose links without modifying assets
    - `inspect_anim_graph_node_settings(blueprint_name, node_type="", graph_name="AnimGraph")` - Read reflected FAnimNode settings for AnimGraph nodes
    - `inspect_anim_state_machine_transitions(blueprint_name, state_machine_name="")` - Read AnimBP state-machine transition source/target/rule graph topology
    - `controlrig_direct_gate_probe(control_rig_path="", control_rig_class="", cases?)` - Run transient ControlRig property/curve gate probes and return hierarchy transform deltas without saving assets
    - `sample_controlrig_pre_post_runtime_pose(control_rig_path="", control_rig_class="", input_defaults?, curve_values?)` - Sample transient ControlRig hierarchy pre/post execute transforms and deltas
    - `sample_anim_node_pre_post_runtime_pose(blueprint_name="", node_id="", node_type="", dry_run=True)` - Resolve an AnimGraph node target or run compiled mapping, PoseWatch, active-component, or isolated-temp pose probes on main or Post Process AnimInstances
    - `sample_skeletal_bones_in_sie(actor_label="", actor_name="", component_name="", bones?, sockets?, require_pie_world=False)` - Sample live PIE/SIE/play SkeletalMeshComponent bone/socket transforms without modifying assets
    - `sample_blendspace_runtime_pose_grid(skeletal_mesh, blendspace_path="", blendspaces?, samples?, require_pie_world=True)` - Evaluate BlendSpace inputs on a transient runtime SkeletalMeshActor and return sampled bone/socket pose deltas
    - `ensure_blendspace_sample_variant(source_blendspace, axis_edits?, sample_edits?, add_samples?)` - Duplicate/reuse a sample BlendSpace variant, edit axes/sample coordinates safely, and save only the target asset
    - `inspect_anim_instance_runtime_state(actor_label="", actor_name="", component_name="", state_machine_name="", require_pie_world=False)` - Read live PIE/SIE/play AnimInstance state-machine, montage, and curve state
    - `set_anim_instance_runtime_property_for_probe(actor_label="", properties?, require_pie_world=False)` - Set live AnimInstance runtime properties for probing without saving assets
    - `sample_anim_state_machine_runtime_response(actor_label="", cases?, require_pie_world=False)` - Apply runtime property cases, tick narrowly, and sample state-machine response
    - `set_anim_graph_rigidbody_settings(blueprint_name, alpha?, external_force?, simulation_space?)` - Modify a sample RigidBody AnimGraph node
    - `ensure_anim_graph_input_pose_passthrough(blueprint_name, graph_name="AnimGraph", replace_existing=False)` - Create/reuse a Linked Input Pose node and connect it to the AnimGraph root Result pin
    - `ensure_postprocess_anim_demo_variant(source_blueprint_name, source_skeletal_mesh, variant_name, bone_name="head", rotation=[0,0,6])` - Duplicate/reuse a sample Post Process AnimBP and SkeletalMesh variant for safe late ModifyBone proof
    - `ensure_anim_graph_modify_bone_demo(blueprint_name, bone_name="head", rotation=[0,0,6], replace_existing=False)` - Create/reuse a safe Post Process AnimBP Modify Bone demo chain
    - `ensure_anim_graph_modify_curve_demo(blueprint_name, curve_values?)` - Create/reuse a sample Modify Curve demo chain, defaulting to StackOBot ControlRig gate curves
    - `set_anim_graph_controlrig_input_defaults(blueprint_name, input_defaults?)` - Expose sample ControlRig AnimGraph input pins and set defaults
    - `ensure_controlrig_forced_driver_animbp(blueprint_name, curve_values?, input_defaults?)` - Insert sample Modify Curve before ControlRig and force input defaults
    - `ensure_anim_graph_trail_demo(blueprint_name, trail_bone="VB VBHead", base_joint="head", replace_existing=False)` - Create/reuse a sample Trail Controller demo chain
    - `add_blueprint_event_node(blueprint_name, event_type)` - Add event nodes
    - `add_blueprint_input_action_node(blueprint_name, action_name)` - Add input nodes
    - `add_blueprint_function_node(blueprint_name, target, function_name)` - Add function nodes
    - `add_blueprint_branch_node(blueprint_name)` - Add Branch control-flow node
    - `add_blueprint_sequence_node(blueprint_name, output_count=2)` - Add Sequence control-flow node
    - `add_blueprint_return_node(blueprint_name, graph_type="function")` - Add or resolve function Return node
    - `add_blueprint_dynamic_cast_node(blueprint_name, target_class)` - Add Dynamic Cast node
    - `connect_blueprint_nodes(blueprint_name, source_node_id, source_pin, target_node_id, target_pin)` - Connect nodes
    - `delete_blueprint_node(blueprint_name, node_id, graph_name="", expected_node_class="", allow_non_exec_linked_delete=False)` - Delete one guarded Blueprint graph node
    - `add_blueprint_variable(blueprint_name, variable_name, variable_type, default_value=None)` - Add member variables with defaults/metadata
    - `set_blueprint_variable_metadata(blueprint_name, variable_name, metadata)` - Update metadata on existing member variables
    - `set_blueprint_category_sorting(blueprint_name, category_order?, category_to_front?)` - Set Blueprint Details/My Blueprint category order
    - `bind_pcg_generation_settings_to_blueprint(blueprint_name, component_variable="ForestPCG", function_class="/Script/YourRuntimeModule.YourPCGBlueprintLibrary")` - Wire Blueprint PCG generation variables to a PCG component in Construction Script
    - `add_blueprint_function_parameter(blueprint_name, parameter_name, parameter_type, direction="input")` - Add function input/output pins
    - `add_blueprint_local_variable(blueprint_name, variable_name, variable_type)` - Add function-scoped local variables
    - `add_blueprint_get_self_component_reference(blueprint_name, component_name)` - Add component refs
    - `add_blueprint_self_reference(blueprint_name)` - Add self references
    - `find_blueprint_nodes(blueprint_name, node_type, event_type)` - Find nodes
    
    ## Project Tools
    - `create_input_mapping(action_name, key, input_type)` - Create input mappings
    - `audit_content_root_mcp(root_path)` - Read-only audit for asset counts, dependencies, redirectors, dirty packages, and expected content checks
    - `analyze_blueprint_widget_fallbacks_mcp(source_root, target_root)` - Diagnose Blueprint/Widget duplicate fallback safety for MCP-generated content
    - `run_content_validation_pipeline_mcp(source_root, target_root, map_path="")` - Run the MCP recreate/postprocess/world-repair validation pipeline

    ## PCG Graph Tools
    - `list_pcg_assets(root_path="/Game")` - List PCG-related assets under a content path
    - `refresh_pcg_components(actor_name="", selected_only=False, cleanup=True, generate=True)` - Refresh or generate PCG components in the current editor level
    - `create_pcg_graph_from_spec(graph_spec, overwrite_existing=False)` - Create a PCG graph from a deterministic JSON-style spec
    - `audit_pcg_graph_contract(graph_path)` - Read-only PCG graph audit with nodes, pins, spawners, actor selectors, edges, and dependencies
    - `validate_pcg_source_independence(graph_path)` - Check that a recreated graph avoids forbidden source dependencies such as `/Game/Cubeless/PCG/PCGStudy`
    - `set_pcg_static_mesh_spawner_entries(graph_path, node_id, mesh_entries)` - Replace weighted Static Mesh Spawner entries on a PCG graph node
    - `read_pcg_node_contract(graph_path, node_id="")` - Read stable node contract data: title, class, position, pins, spawner selector, and actor selector
    - `promote_pcg_temp_graph(source_graph_path, target_graph_path, dry_run=True)` - Guarded temp-to-library PCG graph promotion after source-independence validation
    - `pcg_actor_smoke_test(graph_path, dry_run=True)` - Dry-run or run a guarded current-level PCG component smoke test without map switching
    - `resolve_pcg_graph(graph_path)` - Resolve a PCG graph by short name, package path, or object path
    - `list_pcg_graph_nodes(graph_path)` - List native PCG graph nodes and pins
    - `add_pcg_node(graph_path, settings_class)` / `connect_pcg_nodes(...)` / `set_pcg_node_setting(...)` / `save_pcg_graph(graph_path)` - Low-level PCG graph editing helpers

    ## Runtime Tool Management
    - `manage_tools(action="status", tool_name="", category="", enabled=None, include_tools=True, include_recent=True, ping_unreal=False)` - Inspect or adjust runtime-only MCP tool/category enablement. Use `action="health"` for registry, telemetry, guard, and optional Unreal bridge ping. Use `action="heartbeat"` for a required Unreal bridge ping. Defaults to all tools enabled, resets on server restart, cannot disable itself, and requires `enabled` for `set_tool`/`set_category`.

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
    - `list_material_collection_parameter_nodes(material_path)` - Inspect MPC collection parameter nodes and stale ParameterId mismatches
    - `mirror_material_parameter_collection(source_collection_path, target_collection_path)` - Copy same-name MPC parameters/defaults/ids into another MPC
    - `replace_material_collection_references(material_path, target_collection_path)` - Retarget MPC collection parameter nodes to another collection
    - `replace_material_collection_parameters(material_path)` - Bake MPC collection parameter nodes into normal scalar/vector parameter nodes
    - `replace_material_texture_references(material_path, replacements)` - Replace texture references in material texture sample nodes
    - `refresh_material_cached_expression_data(material_path)` - Refresh cached material dependencies after graph surgery
    - `expand_material_function_calls(material_path)` - Expand Material Function Call nodes into the owning Material graph; partial saves require allow_partial_save=True
    - `get_material_parameter_collection_values(collection_path)` - Read MPC asset defaults and current editor-world runtime values
    - `set_material_parameter_collection_values(collection_path, scalars, vectors)` - Set MPC asset defaults and/or runtime values
    - `set_material_parameter_collection_sync(action, source_collection_path, target_collection_path)` - Start/stop/status runtime MPC value sync

    ## AI Texture Generation
    - `get_static_mesh_uv_layout(mesh_path, uv_channel, output_path)` - Export a Static Mesh UV wireframe PNG
    - `generate_texture_from_prompt(prompt, output_name, output_dir, size)` - Prepare a BaseColor PNG request for Codex built-in image generation; does not call API-key image services
    - `generate_texture_for_mesh_uv(mesh_path, prompt, uv_channel, output_name, output_dir, size)` - Export a UV guide and prepare a built-in image generation handoff; does not call API-key image services
    - `import_texture_to_unreal(image_path, unreal_folder, asset_name)` - Import a PNG as Texture2D
    - `create_material_instance_with_texture(texture_asset_path, material_name, unreal_folder, base_material_path)` - Create a BaseColor material/material instance
    - `apply_material_to_mesh(target, material_asset_path, material_slot)` - Apply a material to selected/named mesh targets
    - `generate_and_apply_ai_texture(target, prompt, output_name, unreal_folder, uv_channel, size)` - Prepare the full texture pipeline handoff; import/apply steps run after the built-in image PNG exists

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
