import json
import socket
import textwrap
import time


HOST = "127.0.0.1"
PORT = 55557

PACKAGE_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring"
BLUEPRINT_NAME = "BP_Cubeless_ED_PCGAuthoringSelector"
BLUEPRINT_PATH = f"{PACKAGE_PATH}/{BLUEPRINT_NAME}.{BLUEPRINT_NAME}"
BLUEPRINT_CLASS_PATH = f"{PACKAGE_PATH}/{BLUEPRINT_NAME}.{BLUEPRINT_NAME}_C"

COMBO_GRAPHS = {
    "PCG_Sparse": (
        "/Game/Cubeless/PCG/ElectricDreamsLearning/DesignerCombos/"
        "PCG_Cubeless_ED_DesignerCombo_Sparse.PCG_Cubeless_ED_DesignerCombo_Sparse"
    ),
    "PCG_Normal": (
        "/Game/Cubeless/PCG/ElectricDreamsLearning/DesignerCombos/"
        "PCG_Cubeless_ED_DesignerCombo_Normal.PCG_Cubeless_ED_DesignerCombo_Normal"
    ),
    "PCG_Dense": (
        "/Game/Cubeless/PCG/ElectricDreamsLearning/DesignerCombos/"
        "PCG_Cubeless_ED_DesignerCombo_Dense.PCG_Cubeless_ED_DesignerCombo_Dense"
    ),
}


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

print("MCP_CUBELESS_ED_AUTHORING_SELECTOR_ASSET_SETUP_BEGIN")
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
print("MCP_CUBELESS_ED_AUTHORING_SELECTOR_ASSET_SETUP_END")
"""
    execute_unreal(code)


def add_components():
    for component_type, component_name in [
        ("SplineComponent", "Spline"),
        ("PCGComponent", "PCG_Sparse"),
        ("PCGComponent", "PCG_Normal"),
        ("PCGComponent", "PCG_Dense"),
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
COMBO_GRAPHS = {COMBO_GRAPHS!r}

print("MCP_CUBELESS_ED_AUTHORING_SELECTOR_TEMPLATE_SETUP_BEGIN")
blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
if not blueprint:
    raise RuntimeError(f"Missing selector Blueprint: {{BLUEPRINT_PATH}}")

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
    object_name = obj.get_name()
    if isinstance(obj, unreal.SplineComponent):
        obj.modify()
        obj.set_editor_property("component_tags", ["CubelessEDAuthoringSpline"])
    if isinstance(obj, unreal.PCGComponent):
        graph_key = next((key for key in COMBO_GRAPHS if object_name.startswith(key)), None)
        if not graph_key:
            continue
        graph = unreal.EditorAssetLibrary.load_asset(COMBO_GRAPHS[graph_key])
        if not graph:
            raise RuntimeError(f"Missing combo graph for {{graph_key}}: {{COMBO_GRAPHS[graph_key]}}")
        obj.modify()
        try:
            obj.set_graph(graph)
        except Exception as exc:
            print(f"pcg_template_set_graph_warning={{graph_key}}|{{type(exc).__name__}}:{{exc}}")
        graph_instance = obj.get_editor_property("graph_instance")
        if not graph_instance:
            raise RuntimeError(f"PCG template has no graph_instance: {{object_name}}")
        graph_instance.modify()
        graph_instance.set_editor_property("graph", graph)
        obj.set_editor_property(
            "generation_trigger",
            unreal.PCGComponentGenerationTrigger.GENERATE_ON_DEMAND,
        )
        obj.set_editor_property("component_tags", [graph_key, "CubelessEDAuthoringSelector"])
        configured.append((object_name, graph.get_path_name()))

unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
print(f"configured_pcg_templates={{configured}}")
print("MCP_CUBELESS_ED_AUTHORING_SELECTOR_TEMPLATE_SETUP_END")
"""
    execute_unreal(code)


def add_selector_variable():
    require_success(
        "add_blueprint_variable",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "variable_name": "DesignerComboType",
            "variable_type": "Integer",
            "default_value": 2,
            "is_exposed": True,
            "category": "Cubeless PCG",
            "friendly_name": "Designer Combo Type",
            "tooltip": "1 = Sparse, 2 = Normal, 3 = Dense. Changing this reruns the authoring selector.",
            "metadata": {
                "ClampMin": "1",
                "ClampMax": "3",
                "UIMin": "1",
                "UIMax": "3",
            },
        },
    )
    code = f"""
import unreal

BLUEPRINT_PATH = {BLUEPRINT_PATH!r}
blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
if not blueprint:
    raise RuntimeError(f"Missing selector Blueprint: {{BLUEPRINT_PATH}}")
blueprint.set_blueprint_variable_instance_editable("DesignerComboType", True)
blueprint.set_blueprint_variable_expose_on_spawn("DesignerComboType", True)
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


def resolve_construction_graph():
    result = require_success(
        "resolve_blueprint_graph",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "graph_name": "UserConstructionScript",
            "graph_type": "function",
        },
    )
    graph = result.get("graph")
    if not graph:
        raise RuntimeError(f"UserConstructionScript not resolved: {result}")
    return graph["graph_id"]


def find_construction_entry(graph_id):
    result = require_success(
        "list_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "graph_id": graph_id,
            "include_pins": True,
        },
    )
    for node in result.get("nodes", []):
        if node.get("class") == "K2Node_FunctionEntry":
            return node["node_id"]
    raise RuntimeError("Construction Script entry node not found")


def add_component_ref(graph_id, component_name, x, y):
    result = require_success(
        "add_blueprint_get_self_component_reference",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "graph_id": graph_id,
            "component_name": component_name,
            "node_position": [x, y],
        },
    )
    return result["node_id"]


def add_call(graph_id, function_name, x, y, defaults=None):
    result = require_success(
        "add_blueprint_call_function_node",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "graph_id": graph_id,
            "function_class": "/Script/PCG.PCGComponent",
            "function_name": function_name,
            "node_position": [x, y],
            "param_defaults": defaults or {},
        },
    )
    return result["node_id"]


def add_actor_component_call(graph_id, function_name, x, y, defaults=None):
    result = require_success(
        "add_blueprint_call_function_node",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "graph_id": graph_id,
            "function_class": "/Script/Engine.ActorComponent",
            "function_name": function_name,
            "node_position": [x, y],
            "param_defaults": defaults or {},
        },
    )
    return result["node_id"]


def connect(graph_id, source_node, source_pin, target_node, target_pin, replace=False):
    return require_success(
        "connect_blueprint_nodes",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "graph_id": graph_id,
            "source_node_id": source_node,
            "source_pin": source_pin,
            "target_node_id": target_node,
            "target_pin": target_pin,
            "allow_pin_link_replacement": replace,
        },
    )


def build_construction_script():
    graph_id = resolve_construction_graph()
    entry = find_construction_entry(graph_id)

    self_ref = require_success(
        "add_blueprint_self_reference",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "graph_id": graph_id,
            "node_position": [-760, 220],
        },
    )["node_id"]
    selector_get = require_success(
        "add_blueprint_variable_get_node",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "graph_id": graph_id,
            "variable_name": "DesignerComboType",
            "node_position": [-520, 120],
        },
    )["node_id"]
    switch = require_success(
        "add_blueprint_switch_int_node",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "graph_id": graph_id,
            "start_index": 1,
            "case_count": 3,
            "has_default_pin": True,
            "node_position": [520, 20],
        },
    )["node_id"]

    refs = {
        "Sparse": add_component_ref(graph_id, "PCG_Sparse", -520, -320),
        "Normal": add_component_ref(graph_id, "PCG_Normal", -520, -120),
        "Dense": add_component_ref(graph_id, "PCG_Dense", -520, -520),
    }
    cleanup = {
        "Sparse": add_call(graph_id, "Cleanup", -160, -320, {"bRemoveComponents": True}),
        "Normal": add_call(graph_id, "Cleanup", 60, -120, {"bRemoveComponents": True}),
        "Dense": add_call(graph_id, "Cleanup", 280, -520, {"bRemoveComponents": True}),
    }
    deactivate = {
        "Sparse": add_actor_component_call(graph_id, "SetActive", 500, -320, {"bNewActive": False, "bReset": False}),
        "Normal": add_actor_component_call(graph_id, "SetActive", 720, -120, {"bNewActive": False, "bReset": False}),
        "Dense": add_actor_component_call(graph_id, "SetActive", 940, -520, {"bNewActive": False, "bReset": False}),
    }
    activate = {
        "Sparse": add_actor_component_call(graph_id, "SetActive", 1160, -260, {"bNewActive": True, "bReset": False}),
        "Normal": add_actor_component_call(graph_id, "SetActive", 1160, 20, {"bNewActive": True, "bReset": False}),
        "Dense": add_actor_component_call(graph_id, "SetActive", 1160, 300, {"bNewActive": True, "bReset": False}),
    }
    generate = {
        "Sparse": add_call(graph_id, "Generate", 1440, -260, {"bForce": True}),
        "Normal": add_call(graph_id, "Generate", 1440, 20, {"bForce": True}),
        "Dense": add_call(graph_id, "Generate", 1440, 300, {"bForce": True}),
    }

    for name in refs:
        connect(graph_id, refs[name], f"PCG_{name}", cleanup[name], "self")
        connect(graph_id, refs[name], f"PCG_{name}", deactivate[name], "self")
        connect(graph_id, refs[name], f"PCG_{name}", activate[name], "self")
        connect(graph_id, refs[name], f"PCG_{name}", generate[name], "self")

    connect(graph_id, entry, "then", cleanup["Sparse"], "execute")
    connect(graph_id, cleanup["Sparse"], "then", cleanup["Normal"], "execute")
    connect(graph_id, cleanup["Normal"], "then", cleanup["Dense"], "execute")
    connect(graph_id, cleanup["Dense"], "then", deactivate["Sparse"], "execute")
    connect(graph_id, deactivate["Sparse"], "then", deactivate["Normal"], "execute")
    connect(graph_id, deactivate["Normal"], "then", deactivate["Dense"], "execute")
    connect(graph_id, deactivate["Dense"], "then", switch, "execute")
    connect(graph_id, self_ref, "self", selector_get, "self")
    connect(graph_id, selector_get, "DesignerComboType", switch, "Selection")
    connect(graph_id, switch, "1", activate["Sparse"], "execute")
    connect(graph_id, switch, "2", activate["Normal"], "execute")
    connect(graph_id, switch, "3", activate["Dense"], "execute")
    connect(graph_id, switch, "Default", activate["Normal"], "execute")
    connect(graph_id, activate["Sparse"], "then", generate["Sparse"], "execute")
    connect(graph_id, activate["Normal"], "then", generate["Normal"], "execute")
    connect(graph_id, activate["Dense"], "then", generate["Dense"], "execute")


def main():
    print("MCP_CUBELESS_ED_AUTHORING_SELECTOR_BUILD_BEGIN")
    create_clean_blueprint()
    add_components()
    configure_component_templates()
    add_selector_variable()
    # PCGComponent Generate/SetActive nodes compile in Construction Script with
    # unsafe-call warnings and do not reliably generate editor output there.
    # The selector is therefore applied through editor scripting.
    result = require_success(
        "compile_and_validate_blueprint",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "save": True,
            "refresh_nodes": True,
        },
    )
    if not result.get("validation_pass"):
        raise RuntimeError(f"Selector Blueprint compile validation failed: {result}")
    print(f"selector_blueprint={BLUEPRINT_PATH}")
    print(f"selector_class={BLUEPRINT_CLASS_PATH}")
    print(f"compile_result={result}")
    print("MCP_CUBELESS_ED_AUTHORING_SELECTOR_BUILD_END")


if __name__ == "__main__":
    # Give the editor bridge a moment if the previous command just finished a save.
    time.sleep(0.1)
    main()
