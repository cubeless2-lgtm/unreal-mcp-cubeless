"""
Niagara tools for Unreal MCP.

These tools intentionally use the generic execute_python bridge. Niagara's
editor API exposes many useful details through reflected properties, while the
deeper stack/graph editing APIs are C++-heavy and should stay out of the first
MVP.
"""

import logging
from typing import Any, Dict

from mcp.server.fastmcp import Context, FastMCP

from services.unreal_texture_importer import run_unreal_python_json


logger = logging.getLogger("UnrealMCP")


def _run_niagara_python(code_body: str) -> Dict[str, Any]:
    """Run Unreal Python for Niagara tooling and return a JSON RESULT."""
    return run_unreal_python_json(code_body, result_name="niagara_tools")


def register_niagara_tools(mcp: FastMCP):
    """Register Niagara-focused inspection and validation tools."""

    @mcp.tool()
    def list_niagara_assets(
        ctx: Context,
        root_path: str = "/Game",
        include_scripts: bool = False,
        include_parameter_collections: bool = False,
    ) -> Dict[str, Any]:
        """
        List Niagara assets under a content path.

        Args:
            root_path: Unreal content path to scan, for example /Game.
            include_scripts: Include NiagaraScript/module assets in addition to systems and emitters.
            include_parameter_collections: Include Niagara parameter collections.
        """
        code = f"""
import unreal

root_path = {root_path!r}
include_scripts = {bool(include_scripts)!r}
include_parameter_collections = {bool(include_parameter_collections)!r}

registry = unreal.AssetRegistryHelpers.get_asset_registry()
assets = registry.get_assets_by_path(root_path, recursive=True)
items = []

def tags_to_dict(asset_data):
    tags = {{}}
    raw_tags = getattr(asset_data, "tags_and_values", None)
    if raw_tags:
        try:
            for key in raw_tags:
                tags[str(key)] = str(raw_tags[key])
        except Exception:
            try:
                tags = {{str(k): str(v) for k, v in dict(raw_tags).items()}}
            except Exception:
                tags = {{}}
    return tags

for asset_data in assets:
    class_name = str(asset_data.asset_class_path.asset_name)
    package_name = str(asset_data.package_name)
    asset_name = str(asset_data.asset_name)
    is_system = class_name == "NiagaraSystem"
    is_emitter = class_name in ("NiagaraEmitter", "NiagaraStatelessEmitter")
    is_script = class_name == "NiagaraScript"
    is_collection = class_name == "NiagaraParameterCollection"
    if not is_system and not is_emitter:
        if is_script and not include_scripts:
            continue
        if is_collection and not include_parameter_collections:
            continue
        if not is_script and not is_collection:
            continue
    items.append({{
        "asset_name": asset_name,
        "package_name": package_name,
        "object_path": f"{{package_name}}.{{asset_name}}",
        "class_name": class_name,
        "tags": tags_to_dict(asset_data),
    }})

RESULT = {{"success": True, "count": len(items), "assets": items}}
"""
        return _run_niagara_python(code)

    @mcp.tool()
    def inspect_niagara_system(
        ctx: Context,
        system_path: str,
        include_emitters: bool = True,
        include_scripts: bool = True,
        include_parameters: bool = True,
    ) -> Dict[str, Any]:
        """
        Inspect a Niagara System asset without modifying it.

        Args:
            system_path: Niagara System package/object path or short asset name.
            include_emitters: Include emitter handle summaries where reflected data is available.
            include_scripts: Include system/emitter script summaries where reflected data is available.
            include_parameters: Include exposed user parameter summaries where reflected data is available.
        """
        code = f"""
import unreal

system_path = {system_path!r}
include_emitters = {bool(include_emitters)!r}
include_scripts = {bool(include_scripts)!r}
include_parameters = {bool(include_parameters)!r}

def safe_string(value):
    try:
        if value is None:
            return ""
        if hasattr(value, "to_string"):
            return value.to_string()
        return str(value)
    except Exception:
        return repr(value)

def asset_ref(obj):
    if not obj:
        return None
    return {{
        "name": safe_string(obj.get_name()) if hasattr(obj, "get_name") else "",
        "path": safe_string(obj.get_path_name()) if hasattr(obj, "get_path_name") else "",
        "class_name": safe_string(obj.get_class().get_name()) if hasattr(obj, "get_class") else type(obj).__name__,
    }}

def get_prop(obj, names, default=None):
    if obj is None:
        return default
    for name in names:
        try:
            return obj.get_editor_property(name)
        except Exception:
            pass
    for name in names:
        if hasattr(obj, name):
            try:
                return getattr(obj, name)
            except Exception:
                pass
    return default

def call_no_arg(obj, names, default=None):
    if obj is None:
        return default
    for name in names:
        fn = getattr(obj, name, None)
        if callable(fn):
            try:
                return fn()
            except Exception:
                pass
    return default

def enum_name(value):
    text = safe_string(value)
    if "." in text:
        return text.split(".")[-1]
    return text

def variable_summary(variable):
    if variable is None:
        return {{"name": "", "type": "", "raw": ""}}
    name = call_no_arg(variable, ["get_name"], None)
    if name is None:
        name = get_prop(variable, ["name", "Name"], "")
    type_def = call_no_arg(variable, ["get_type"], None)
    if type_def is None:
        type_def = get_prop(variable, ["type_def", "TypeDef", "type", "Type"], "")
    return {{"name": safe_string(name), "type": safe_string(type_def), "raw": safe_string(variable)}}

def parameter_store_summary(store):
    if store is None:
        return {{"available": False, "reason": "parameter store was not readable"}}
    variables = []
    raw_variables = None
    for method_name in ("get_user_parameters", "get_parameters"):
        method = getattr(store, method_name, None)
        if callable(method):
            try:
                raw_variables = method()
                break
            except Exception:
                pass
    if raw_variables is None:
        raw_variables = get_prop(
            store,
            [
                "sorted_parameter_offsets",
                "SortedParameterOffsets",
                "user_parameter_redirects",
                "UserParameterRedirects",
            ],
            None,
        )
    if raw_variables is not None:
        try:
            for variable in raw_variables:
                variables.append(variable_summary(variable))
        except Exception as exc:
            return {{
                "available": False,
                "reason": "parameter variables exist but could not be iterated",
                "error": str(exc),
                "raw": safe_string(raw_variables),
            }}
    return {{
        "available": bool(variables),
        "count": len(variables),
        "parameters": variables,
        "raw": safe_string(store) if not variables else "",
    }}

def script_summary(script):
    if not script:
        return None
    vm_data = get_prop(script, ["cached_script_vm", "CachedScriptVM"], None)
    compile_status = None
    compile_events = []
    error_message = ""
    if vm_data is not None:
        compile_status = get_prop(vm_data, ["last_compile_status", "LastCompileStatus"], None)
        error_message = safe_string(get_prop(vm_data, ["error_msg", "ErrorMsg"], ""))
        events = get_prop(vm_data, ["last_compile_events", "LastCompileEvents"], [])
        try:
            for event in events:
                compile_events.append(safe_string(event))
        except Exception:
            compile_events = [safe_string(events)]
    if compile_status is None:
        compile_status = get_prop(script, ["last_compile_status", "LastCompileStatus"], None)
    return {{
        "asset": asset_ref(script),
        "usage": enum_name(get_prop(script, ["usage", "Usage"], "")),
        "last_compile_status": enum_name(compile_status),
        "error_message": error_message,
        "compile_event_count": len(compile_events),
        "compile_events": compile_events[:25],
    }}

def emitter_data_summary(emitter_data):
    if emitter_data is None:
        return {{}}
    renderers = []
    for renderer in get_prop(emitter_data, ["renderer_properties", "RendererProperties"], []) or []:
        renderers.append(asset_ref(renderer))
    return {{
        "sim_target": enum_name(get_prop(emitter_data, ["sim_target", "SimTarget"], "")),
        "local_space": bool(get_prop(emitter_data, ["local_space", "bLocalSpace", "b_local_space"], False)),
        "determinism": bool(get_prop(emitter_data, ["determinism", "bDeterminism", "b_determinism"], False)),
        "random_seed": get_prop(emitter_data, ["random_seed", "RandomSeed"], None),
        "renderer_count": len(renderers),
        "renderers": renderers,
        "spawn_script": script_summary(get_prop(get_prop(emitter_data, ["emitter_spawn_script_props", "EmitterSpawnScriptProps"], None), ["script", "Script"], None)) if include_scripts else None,
        "update_script": script_summary(get_prop(get_prop(emitter_data, ["emitter_update_script_props", "EmitterUpdateScriptProps"], None), ["script", "Script"], None)) if include_scripts else None,
    }}

def emitter_handle_summary(handle, index):
    name = call_no_arg(handle, ["get_name"], None)
    if name is None:
        name = get_prop(handle, ["name", "Name"], "")
    enabled = call_no_arg(handle, ["get_is_enabled"], None)
    if enabled is None:
        enabled = get_prop(handle, ["is_enabled", "bIsEnabled", "b_is_enabled"], None)
    mode = call_no_arg(handle, ["get_emitter_mode"], None)
    if mode is None:
        mode = get_prop(handle, ["emitter_mode", "EmitterMode"], "")
    instance = call_no_arg(handle, ["get_instance"], None)
    if instance is None:
        instance = get_prop(handle, ["versioned_instance", "VersionedInstance"], None)
    emitter = get_prop(instance, ["emitter", "Emitter"], None)
    version = get_prop(instance, ["version", "Version"], None)
    emitter_data = call_no_arg(instance, ["get_emitter_data"], None)
    if emitter_data is None:
        emitter_data = get_prop(emitter, ["latest_emitter_data", "LatestEmitterData"], None)
    return {{
        "index": index,
        "name": safe_string(name),
        "enabled": enabled if enabled is not None else "unknown",
        "mode": enum_name(mode),
        "emitter_asset": asset_ref(emitter),
        "version": safe_string(version),
        "data": emitter_data_summary(emitter_data),
    }}

def resolve_system(path):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if asset and asset.get_class().get_name() == "NiagaraSystem":
        return asset
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    candidates = registry.get_assets_by_path("/Game", recursive=True)
    for asset_data in candidates:
        if str(asset_data.asset_class_path.asset_name) != "NiagaraSystem":
            continue
        package_name = str(asset_data.package_name)
        asset_name = str(asset_data.asset_name)
        object_path = f"{{package_name}}.{{asset_name}}"
        if path in (asset_name, package_name, object_path) or package_name.endswith("/" + path):
            return unreal.EditorAssetLibrary.load_asset(package_name)
    return None

system = resolve_system(system_path)
if not system:
    RESULT = {{"success": False, "message": f"Niagara System not found: {{system_path}}"}}
elif system.get_class().get_name() != "NiagaraSystem":
    RESULT = {{
        "success": False,
        "message": f"Asset is not a NiagaraSystem: {{system_path}}",
        "class_name": system.get_class().get_name(),
    }}
else:
    system_scripts = []
    if include_scripts:
        for prop_names in (
            ["system_spawn_script", "SystemSpawnScript"],
            ["system_update_script", "SystemUpdateScript"],
        ):
            summary = script_summary(get_prop(system, prop_names, None))
            if summary:
                system_scripts.append(summary)

    emitters = []
    if include_emitters:
        handles = get_prop(system, ["emitter_handles", "EmitterHandles"], [])
        try:
            for index, handle in enumerate(handles):
                emitters.append(emitter_handle_summary(handle, index))
        except Exception as exc:
            emitters.append({{"error": f"EmitterHandles could not be iterated: {{exc}}", "raw": safe_string(handles)}})

    exposed_parameters = None
    if include_parameters:
        exposed_parameters = parameter_store_summary(get_prop(system, ["exposed_parameters", "ExposedParameters"], None))

    RESULT = {{
        "success": True,
        "asset": asset_ref(system),
        "is_valid": call_no_arg(system, ["is_valid"], "unknown"),
        "is_ready_to_run": call_no_arg(system, ["is_ready_to_run"], "unknown"),
        "needs_warmup": call_no_arg(system, ["needs_warmup"], "unknown"),
        "warmup_time": call_no_arg(system, ["get_warmup_time"], get_prop(system, ["warmup_time", "WarmupTime"], None)),
        "warmup_tick_count": call_no_arg(system, ["get_warmup_tick_count"], get_prop(system, ["warmup_tick_count", "WarmupTickCount"], None)),
        "warmup_tick_delta": call_no_arg(system, ["get_warmup_tick_delta"], get_prop(system, ["warmup_tick_delta", "WarmupTickDelta"], None)),
        "system_scripts": system_scripts,
        "exposed_parameters": exposed_parameters,
        "emitter_count": len(emitters),
        "emitters": emitters,
        "notes": [
            "This MVP uses reflected Python-visible fields. Deep Niagara stack module graph editing is intentionally not included.",
            "If emitter details are sparse, the engine did not expose the relevant internal fields through Python reflection.",
        ],
    }}
"""
        return _run_niagara_python(code)

    @mcp.tool()
    def list_niagara_components(
        ctx: Context,
        selected_only: bool = False,
    ) -> Dict[str, Any]:
        """
        List Niagara components in the current editor level.

        Args:
            selected_only: If true, inspect only selected actors.
        """
        code = f"""
import unreal

selected_only = {bool(selected_only)!r}
editor_actor_subsystem = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actors = editor_actor_subsystem.get_selected_level_actors() if selected_only else editor_actor_subsystem.get_all_level_actors()
components = []

for actor in actors:
    actor_label = actor.get_actor_label()
    actor_path = actor.get_path_name()
    for component in actor.get_components_by_class(unreal.ActorComponent):
        class_name = component.get_class().get_name()
        if "NiagaraComponent" not in class_name:
            continue
        asset = None
        getter = getattr(component, "get_asset", None)
        if callable(getter):
            try:
                asset = getter()
            except Exception:
                asset = None
        if asset is None:
            try:
                asset = component.get_editor_property("asset")
            except Exception:
                pass
        components.append({{
            "actor": actor_label,
            "actor_path": actor_path,
            "component": component.get_name(),
            "component_path": component.get_path_name(),
            "component_class": class_name,
            "system_asset": asset.get_path_name() if asset else "",
        }})

RESULT = {{"success": True, "count": len(components), "components": components}}
"""
        return _run_niagara_python(code)

    @mcp.tool()
    def duplicate_niagara_system_to_temp(
        ctx: Context,
        system_path: str,
        temp_folder: str = "/Game/_MCP_Temp",
        new_name: str = "",
    ) -> Dict[str, Any]:
        """
        Duplicate a Niagara System into a temporary package for safe experiments.

        Args:
            system_path: Source Niagara System package/object path or short asset name.
            temp_folder: Destination content folder, normally /Game/_MCP_Temp.
            new_name: Optional duplicate asset name. Defaults to <SourceName>_MCP.
        """
        code = f"""
import re
import unreal

system_path = {system_path!r}
temp_folder = {temp_folder!r}
new_name = {new_name!r}

def resolve_system(path):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if asset and asset.get_class().get_name() == "NiagaraSystem":
        return asset
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    for asset_data in registry.get_assets_by_path("/Game", recursive=True):
        if str(asset_data.asset_class_path.asset_name) != "NiagaraSystem":
            continue
        package_name = str(asset_data.package_name)
        asset_name = str(asset_data.asset_name)
        object_path = f"{{package_name}}.{{asset_name}}"
        if path in (asset_name, package_name, object_path) or package_name.endswith("/" + path):
            return unreal.EditorAssetLibrary.load_asset(package_name)
    return None

source = resolve_system(system_path)
if not source:
    RESULT = {{"success": False, "message": f"Niagara System not found: {{system_path}}"}}
else:
    normalized_temp_folder = temp_folder.rstrip("/")
    if normalized_temp_folder != "/Game/_MCP_Temp" and not normalized_temp_folder.startswith("/Game/_MCP_Temp/"):
        RESULT = {{"success": False, "message": "temp_folder must be under /Game/_MCP_Temp"}}
    else:
        source_name = source.get_name()
        safe_name = new_name or f"{{source_name}}_MCP"
        safe_name = re.sub(r"[^A-Za-z0-9_]", "_", safe_name)
        destination_path = f"{{normalized_temp_folder}}/{{safe_name}}"
        if unreal.EditorAssetLibrary.does_asset_exist(destination_path):
            unreal.EditorAssetLibrary.delete_asset(destination_path)
        duplicated = unreal.EditorAssetLibrary.duplicate_asset(source.get_path_name().split(".")[0], destination_path)
        if duplicated:
            unreal.EditorAssetLibrary.save_loaded_asset(duplicated)
            RESULT = {{
                "success": True,
                "source": source.get_path_name(),
                "duplicate": duplicated.get_path_name(),
                "package_path": destination_path,
                "note": "Temporary duplicate created for MCP validation. Do not stage _MCP_Temp outputs unless explicitly requested.",
            }}
        else:
            RESULT = {{"success": False, "message": f"Failed to duplicate {{source.get_path_name()}} to {{destination_path}}"}}
"""
        return _run_niagara_python(code)

    @mcp.tool()
    def compile_and_save_niagara_system(
        ctx: Context,
        system_path: str,
        save: bool = False,
    ) -> Dict[str, Any]:
        """
        Best-effort compile validation for a Niagara System, optionally saving after success.

        Args:
            system_path: Niagara System package/object path or short asset name.
            save: Save the asset after the compile/wait path reports no immediate failure.
        """
        code = f"""
import unreal

system_path = {system_path!r}
save = {bool(save)!r}

def resolve_system(path):
    asset = unreal.EditorAssetLibrary.load_asset(path)
    if asset and asset.get_class().get_name() == "NiagaraSystem":
        return asset
    registry = unreal.AssetRegistryHelpers.get_asset_registry()
    for asset_data in registry.get_assets_by_path("/Game", recursive=True):
        if str(asset_data.asset_class_path.asset_name) != "NiagaraSystem":
            continue
        package_name = str(asset_data.package_name)
        asset_name = str(asset_data.asset_name)
        object_path = f"{{package_name}}.{{asset_name}}"
        if path in (asset_name, package_name, object_path) or package_name.endswith("/" + path):
            return unreal.EditorAssetLibrary.load_asset(package_name)
    return None

def try_call(obj, name, *args):
    fn = getattr(obj, name, None)
    if not callable(fn):
        return {{"called": False, "message": f"{{name}} is not exposed to Python"}}
    try:
        value = fn(*args)
        return {{"called": True, "success": True, "value": str(value)}}
    except Exception as exc:
        return {{"called": True, "success": False, "message": str(exc)}}

def script_compile_summary(script):
    if not script:
        return None
    def get_prop(obj, names, default=None):
        for prop_name in names:
            try:
                return obj.get_editor_property(prop_name)
            except Exception:
                pass
        return default
    vm_data = get_prop(script, ["cached_script_vm", "CachedScriptVM"], None)
    status = ""
    events = []
    error_msg = ""
    if vm_data is not None:
        status = str(get_prop(vm_data, ["last_compile_status", "LastCompileStatus"], ""))
        error_msg = str(get_prop(vm_data, ["error_msg", "ErrorMsg"], ""))
        raw_events = get_prop(vm_data, ["last_compile_events", "LastCompileEvents"], [])
        try:
            events = [str(event) for event in raw_events]
        except Exception:
            events = [str(raw_events)] if raw_events else []
    if not status:
        status = str(get_prop(script, ["last_compile_status", "LastCompileStatus"], ""))
    return {{
        "script": script.get_path_name(),
        "usage": str(get_prop(script, ["usage", "Usage"], "")),
        "last_compile_status": status,
        "error_message": error_msg,
        "compile_event_count": len(events),
        "compile_events": events[:25],
    }}

system = resolve_system(system_path)
if not system:
    RESULT = {{"success": False, "message": f"Niagara System not found: {{system_path}}"}}
elif save and not system.get_path_name().split(".")[0].startswith("/Game/_MCP_Temp/"):
    RESULT = {{
        "success": False,
        "message": "save=true is allowed only for Niagara Systems under /Game/_MCP_Temp",
        "asset": system.get_path_name(),
        "save_requested": save,
    }}
else:
    request_result = try_call(system, "request_compile", True)
    wait_result = try_call(system, "wait_for_compilation_complete", False, False)
    poll_result = try_call(system, "poll_for_compilation_complete", True)
    save_result = None

    scripts = []
    for prop_name in ("system_spawn_script", "SystemSpawnScript", "system_update_script", "SystemUpdateScript"):
        try:
            script = system.get_editor_property(prop_name)
            if script:
                summary = script_compile_summary(script)
                if summary and summary not in scripts:
                    scripts.append(summary)
        except Exception:
            pass

    compile_error_count = 0
    for summary in scripts:
        status = summary.get("last_compile_status", "")
        if "Error" in status or summary.get("error_message"):
            compile_error_count += 1
        for event in summary.get("compile_events", []):
            if "Error" in event or "error" in event:
                compile_error_count += 1

    validation_pass = compile_error_count == 0
    if save and validation_pass:
        try:
            save_result = unreal.EditorAssetLibrary.save_loaded_asset(system)
        except Exception as exc:
            validation_pass = False
            save_result = {{"success": False, "message": str(exc)}}

    RESULT = {{
        "success": True,
        "asset": system.get_path_name(),
        "request_compile": request_result,
        "wait_for_compilation_complete": wait_result,
        "poll_for_compilation_complete": poll_result,
        "compile_error_count": compile_error_count,
        "validation_pass": validation_pass,
        "save_requested": save,
        "save_result": save_result,
        "scripts": scripts,
        "note": "Niagara compile C++ methods may not be exposed in Python on every engine build. Inspect request/wait/poll called flags before trusting this as a full compile gate.",
    }}
"""
        return _run_niagara_python(code)

    logger.info("Niagara tools registered successfully")
