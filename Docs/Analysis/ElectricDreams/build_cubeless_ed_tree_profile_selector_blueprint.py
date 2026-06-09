import json
import socket
import time


HOST = "127.0.0.1"
PORT = 55557

PACKAGE_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring"
BLUEPRINT_NAME = "BP_Cubeless_ED_PCGTreeProfileSelector"
BLUEPRINT_PATH = f"{PACKAGE_PATH}/{BLUEPRINT_NAME}.{BLUEPRINT_NAME}"
BLUEPRINT_CLASS_PATH = f"{PACKAGE_PATH}/{BLUEPRINT_NAME}.{BLUEPRINT_NAME}_C"
DEFAULT_GRAPH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/TreeProfilePresets/"
    "PCG_Cubeless_ED_TreeProfile_CompactConifer_Sparse."
    "PCG_Cubeless_ED_TreeProfile_CompactConifer_Sparse"
)


def send_command(command, params):
    command_obj = {"type": command, "params": params}
    command_json = json.dumps(command_obj)
    with socket.create_connection((HOST, PORT), timeout=20.0) as sock:
        sock.sendall(command_json.encode("utf-8"))
        chunks = []
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                break
            chunks.append(chunk)
            try:
                return json.loads(b"".join(chunks).decode("utf-8"))
            except json.JSONDecodeError:
                continue
    if not chunks:
        raise RuntimeError(f"No response for {command}")
    return json.loads(b"".join(chunks).decode("utf-8"))


def require_success(command, params):
    response = send_command(command, params)
    if not response or response.get("status") != "success":
        raise RuntimeError(f"{command} failed: {response}")
    return response.get("result", response)


def execute_unreal(code):
    return require_success(
        "execute_python",
        {
            "code": f"exec({code!r})",
            "mode": "execute",
            "defer_to_ticker": False,
        },
    )


def create_clean_blueprint():
    code = f"""
import unreal

PACKAGE_PATH = {PACKAGE_PATH!r}
BLUEPRINT_NAME = {BLUEPRINT_NAME!r}
BLUEPRINT_PATH = {BLUEPRINT_PATH!r}

print("MCP_CUBELESS_ED_TREE_PROFILE_SELECTOR_ASSET_SETUP_BEGIN")
unreal.EditorAssetLibrary.make_directory(PACKAGE_PATH)
existing = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
if existing:
    if not BLUEPRINT_PATH.startswith("/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"):
        raise RuntimeError(f"Refusing to delete unexpected asset path: {{BLUEPRINT_PATH}}")
    unreal.EditorAssetLibrary.delete_asset(BLUEPRINT_PATH.rsplit(".", 1)[0])

factory = unreal.BlueprintFactory()
factory.set_editor_property("parent_class", unreal.Actor)
blueprint = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
    BLUEPRINT_NAME,
    PACKAGE_PATH,
    unreal.Blueprint.static_class(),
    factory,
)
if not blueprint:
    raise RuntimeError(f"Failed to create {{BLUEPRINT_PATH}}")
unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
print(f"blueprint={{blueprint.get_path_name()}}")
print("MCP_CUBELESS_ED_TREE_PROFILE_SELECTOR_ASSET_SETUP_END")
"""
    execute_unreal(code)


def add_components():
    for component_type, component_name in [
        ("SplineComponent", "Spline"),
        ("PCGComponent", "PCG_TreeProfile"),
    ]:
        require_success(
            "add_component_to_blueprint",
            {
                "blueprint_name": BLUEPRINT_PATH,
                "component_type": component_type,
                "component_name": component_name,
                "location": [0.0, 0.0, 0.0],
                "rotation": [0.0, 0.0, 0.0],
                "scale": [1.0, 1.0, 1.0],
            },
        )


def configure_component_templates():
    code = f"""
import unreal

BLUEPRINT_PATH = {BLUEPRINT_PATH!r}
DEFAULT_GRAPH = {DEFAULT_GRAPH!r}

print("MCP_CUBELESS_ED_TREE_PROFILE_SELECTOR_TEMPLATE_SETUP_BEGIN")
blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
if not blueprint:
    raise RuntimeError(f"Missing tree profile selector Blueprint: {{BLUEPRINT_PATH}}")

default_graph = unreal.EditorAssetLibrary.load_asset(DEFAULT_GRAPH)
if not default_graph:
    raise RuntimeError(f"Missing default tree profile graph: {{DEFAULT_GRAPH}}")

subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
library = unreal.SubobjectDataBlueprintFunctionLibrary
if not subsystem:
    raise RuntimeError("SubobjectDataSubsystem is unavailable")

configured = []
for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
    data = subsystem.k2_find_subobject_data_from_handle(handle)
    obj = library.get_object_for_blueprint(data, blueprint)
    if not obj:
        continue
    if isinstance(obj, unreal.SplineComponent):
        obj.modify()
        obj.set_editor_property("component_tags", ["CubelessEDTreeProfileSpline"])
    if isinstance(obj, unreal.PCGComponent):
        obj.modify()
        obj.set_graph(default_graph)
        graph_instance = obj.get_editor_property("graph_instance")
        if not graph_instance:
            raise RuntimeError(f"PCG template has no graph_instance: {{obj.get_name()}}")
        graph_instance.modify()
        graph_instance.set_editor_property("graph", default_graph)
        obj.set_editor_property(
            "generation_trigger",
            unreal.PCGComponentGenerationTrigger.GENERATE_ON_DEMAND,
        )
        obj.set_editor_property("component_tags", ["CubelessEDTreeProfileSelector"])
        configured.append((obj.get_name(), default_graph.get_path_name()))

unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
print(f"configured_pcg_templates={{configured}}")
print("MCP_CUBELESS_ED_TREE_PROFILE_SELECTOR_TEMPLATE_SETUP_END")
"""
    execute_unreal(code)


def add_selector_variable(name, default_value, friendly_name, tooltip):
    require_success(
        "add_blueprint_variable",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "variable_name": name,
            "variable_type": "Integer",
            "default_value": int(default_value),
            "is_exposed": True,
            "category": "Cubeless PCG Tree Profile",
            "friendly_name": friendly_name,
            "tooltip": tooltip,
            "metadata": {
                "ClampMin": "1",
                "ClampMax": "3",
                "UIMin": "1",
                "UIMax": "3",
            },
        },
    )


def add_selector_variables():
    add_selector_variable(
        "TreeStyleType",
        1,
        "Tree Style Type",
        "1 = CompactConifer, 2 = ColumnConifer, 3 = MixedConifer. Apply from the Cubeless ED PCG menu after changing.",
    )
    add_selector_variable(
        "TreeAmountType",
        2,
        "Tree Amount Type",
        "1 = Solo, 2 = Sparse, 3 = LightGrove. Tree profiles stay intentionally sparse.",
    )
    code = f"""
import unreal

BLUEPRINT_PATH = {BLUEPRINT_PATH!r}
blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
if not blueprint:
    raise RuntimeError(f"Missing tree profile selector Blueprint: {{BLUEPRINT_PATH}}")
for variable_name in ("TreeStyleType", "TreeAmountType"):
    blueprint.set_blueprint_variable_instance_editable(variable_name, True)
    blueprint.set_blueprint_variable_expose_on_spawn(variable_name, True)
blueprint.modify()
unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
"""
    execute_unreal(code)
    require_success(
        "compile_and_validate_blueprint",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "save": True,
            "refresh_nodes": True,
        },
    )


def main():
    print("MCP_CUBELESS_ED_TREE_PROFILE_SELECTOR_BUILD_BEGIN")
    create_clean_blueprint()
    add_components()
    configure_component_templates()
    add_selector_variables()
    result = require_success(
        "compile_and_validate_blueprint",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "save": True,
            "refresh_nodes": True,
        },
    )
    if not result.get("validation_pass"):
        raise RuntimeError(f"Tree profile selector Blueprint compile validation failed: {result}")
    print(f"tree_profile_selector_blueprint={BLUEPRINT_PATH}")
    print(f"tree_profile_selector_class={BLUEPRINT_CLASS_PATH}")
    print(f"default_graph={DEFAULT_GRAPH}")
    print(f"compile_result={result}")
    print("MCP_CUBELESS_ED_TREE_PROFILE_SELECTOR_BUILD_END")


if __name__ == "__main__":
    time.sleep(0.1)
    main()
