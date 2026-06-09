import json
import socket
import time


HOST = "127.0.0.1"
PORT = 55557

PACKAGE_PATH = "/Game/Cubeless/PCG/ProductionCandidates/Blueprints"
BLUEPRINT_NAME = "BP_Cubeless_PCG_EcosystemCandidate"
BLUEPRINT_PATH = f"{PACKAGE_PATH}/{BLUEPRINT_NAME}.{BLUEPRINT_NAME}"
BLUEPRINT_CLASS_PATH = f"{PACKAGE_PATH}/{BLUEPRINT_NAME}.{BLUEPRINT_NAME}_C"
DEFAULT_STYLE_GRAPH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/DesignerStyleProfileMatrixCombos/"
    "PCG_Cubeless_ED_StyleProfileMatrix_MixedGrass_Both_GroundNormal_DitchSparse."
    "PCG_Cubeless_ED_StyleProfileMatrix_MixedGrass_Both_GroundNormal_DitchSparse"
)
DEFAULT_TREE_GRAPH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/TreeProfilePresets/"
    "PCG_Cubeless_ED_TreeProfile_CompactConifer_Solo."
    "PCG_Cubeless_ED_TreeProfile_CompactConifer_Solo"
)
DEFAULT_MATERIAL_GRAPH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/DynamicMaterialPrototype/"
    "PCG_Cubeless_ED_DynamicMaterialAxis_ActorPropertySelector_Compat."
    "PCG_Cubeless_ED_DynamicMaterialAxis_ActorPropertySelector_Compat"
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

print("MCP_CUBELESS_PCG_PRODUCTION_CANDIDATE_ASSET_SETUP_BEGIN")
unreal.EditorAssetLibrary.make_directory(PACKAGE_PATH)
existing = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
if existing:
    if not BLUEPRINT_PATH.startswith("/Game/Cubeless/PCG/ProductionCandidates/Blueprints/"):
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
print("MCP_CUBELESS_PCG_PRODUCTION_CANDIDATE_ASSET_SETUP_END")
"""
    execute_unreal(code)


def add_components():
    for component_type, component_name in [
        ("SplineComponent", "Spline"),
        ("PCGComponent", "PCG_Style"),
        ("PCGComponent", "PCG_Tree"),
        ("PCGComponent", "PCG_MaterialPreview"),
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
DEFAULT_STYLE_GRAPH = {DEFAULT_STYLE_GRAPH!r}
DEFAULT_TREE_GRAPH = {DEFAULT_TREE_GRAPH!r}
DEFAULT_MATERIAL_GRAPH = {DEFAULT_MATERIAL_GRAPH!r}

print("MCP_CUBELESS_PCG_PRODUCTION_CANDIDATE_TEMPLATE_SETUP_BEGIN")
blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
if not blueprint:
    raise RuntimeError(f"Missing production candidate Blueprint: {{BLUEPRINT_PATH}}")

default_style_graph = unreal.EditorAssetLibrary.load_asset(DEFAULT_STYLE_GRAPH)
default_tree_graph = unreal.EditorAssetLibrary.load_asset(DEFAULT_TREE_GRAPH)
default_material_graph = unreal.EditorAssetLibrary.load_asset(DEFAULT_MATERIAL_GRAPH)
if not default_style_graph:
    raise RuntimeError(f"Missing default style graph: {{DEFAULT_STYLE_GRAPH}}")
if not default_tree_graph:
    raise RuntimeError(f"Missing default tree graph: {{DEFAULT_TREE_GRAPH}}")
if not default_material_graph:
    raise RuntimeError(f"Missing default material graph: {{DEFAULT_MATERIAL_GRAPH}}")

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
        obj.set_editor_property("component_tags", ["CubelessPCGProductionCandidateSpline"])
    if isinstance(obj, unreal.PCGComponent):
        obj.modify()
        if obj.get_name().startswith("PCG_Tree"):
            graph = default_tree_graph
        elif obj.get_name().startswith("PCG_MaterialPreview"):
            graph = default_material_graph
        else:
            graph = default_style_graph
        obj.set_graph(graph)
        graph_instance = obj.get_editor_property("graph_instance")
        if not graph_instance:
            raise RuntimeError(f"PCG template has no graph_instance: {{obj.get_name()}}")
        graph_instance.modify()
        graph_instance.set_editor_property("graph", graph)
        obj.set_editor_property(
            "generation_trigger",
            unreal.PCGComponentGenerationTrigger.GENERATE_ON_DEMAND,
        )
        obj.set_editor_property("component_tags", ["CubelessPCGProductionCandidate"])
        configured.append((obj.get_name(), graph.get_path_name()))

unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
unreal.EditorAssetLibrary.save_loaded_asset(blueprint)
print(f"configured_pcg_templates={{configured}}")
print("MCP_CUBELESS_PCG_PRODUCTION_CANDIDATE_TEMPLATE_SETUP_END")
"""
    execute_unreal(code)


def add_integer_variable(
    name,
    default_value,
    friendly_name,
    tooltip,
    clamp_min,
    clamp_max,
    is_exposed=True,
    category=None,
):
    resolved_category = category or (
        "Cubeless PCG Production Candidate" if is_exposed else "Cubeless PCG Production Internal"
    )
    require_success(
        "add_blueprint_variable",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "variable_name": name,
            "variable_type": "Integer",
            "default_value": int(default_value),
            "is_exposed": bool(is_exposed),
            "category": resolved_category,
            "friendly_name": friendly_name,
            "tooltip": tooltip,
            "metadata": {
                "ClampMin": str(int(clamp_min)),
                "ClampMax": str(int(clamp_max)),
                "UIMin": str(int(clamp_min)),
                "UIMax": str(int(clamp_max)),
            },
        },
    )


def add_bool_variable(name, default_value, friendly_name, tooltip, is_exposed=True):
    require_success(
        "add_blueprint_variable",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "variable_name": name,
            "variable_type": "Boolean",
            "default_value": bool(default_value),
            "is_exposed": bool(is_exposed),
            "category": "Cubeless PCG Production Candidate" if is_exposed else "Cubeless PCG Production Internal",
            "friendly_name": friendly_name,
            "tooltip": tooltip,
        },
    )


def add_candidate_variables():
    add_integer_variable(
        "PresetType",
        1,
        "Preset Type",
        "1 = MixedMeadowDefault, 2 = DenseGroundFoliage, 3 = RockySparse, 4 = LightConiferEdge, 5 = ClassicGrassFill.",
        1,
        5,
    )
    add_integer_variable(
        "DensityOverride",
        0,
        "Density Override",
        "0 = UsePreset, 1 = Sparse, 2 = Normal, 3 = Dense.",
        0,
        3,
    )
    add_integer_variable(
        "TreeOverride",
        0,
        "Tree Override",
        "0 = UsePreset, 1 = Off, 2 = Solo, 3 = Sparse, 4 = LightGrove.",
        0,
        4,
    )
    add_integer_variable(
        "MaterialMood",
        0,
        "Material Mood",
        "0 = UsePreset, 1 = Default, 2 = Cool/Dark, 3 = Warm/Soft.",
        0,
        3,
    )
    add_bool_variable(
        "DebugMaterialPreview",
        False,
        "Debug Material Preview",
        "Generate the separate material preview component for debug inspection.",
    )
    add_integer_variable(
        "MaterialDomainType",
        1,
        "Material Domain Type",
        "Internal value used by the dynamic material preview graph.",
        1,
        3,
        True,
        "Cubeless PCG Production Internal",
    )
    add_integer_variable(
        "MaterialVariantType",
        1,
        "Material Variant Type",
        "Internal value used by the dynamic material preview graph.",
        1,
        3,
        True,
        "Cubeless PCG Production Internal",
    )

    code = f"""
import unreal

BLUEPRINT_PATH = {BLUEPRINT_PATH!r}
blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
if not blueprint:
    raise RuntimeError(f"Missing production candidate Blueprint: {{BLUEPRINT_PATH}}")
for variable_name in (
    "PresetType",
    "DensityOverride",
    "TreeOverride",
    "MaterialMood",
    "DebugMaterialPreview",
):
    blueprint.set_blueprint_variable_instance_editable(variable_name, True)
    blueprint.set_blueprint_variable_expose_on_spawn(variable_name, True)
for variable_name in (
    "MaterialDomainType",
    "MaterialVariantType",
):
    blueprint.set_blueprint_variable_instance_editable(variable_name, True)
    blueprint.set_blueprint_variable_expose_on_spawn(variable_name, False)
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
    print("MCP_CUBELESS_PCG_PRODUCTION_CANDIDATE_BUILD_BEGIN")
    create_clean_blueprint()
    add_components()
    configure_component_templates()
    add_candidate_variables()
    result = require_success(
        "compile_and_validate_blueprint",
        {
            "blueprint_name": BLUEPRINT_PATH,
            "save": True,
            "refresh_nodes": True,
        },
    )
    if not result.get("validation_pass"):
        raise RuntimeError(f"Production candidate Blueprint compile validation failed: {result}")
    print(f"production_candidate_blueprint={BLUEPRINT_PATH}")
    print(f"production_candidate_class={BLUEPRINT_CLASS_PATH}")
    print(f"default_style_graph={DEFAULT_STYLE_GRAPH}")
    print(f"default_tree_graph={DEFAULT_TREE_GRAPH}")
    print(f"default_material_graph={DEFAULT_MATERIAL_GRAPH}")
    print(f"compile_result={result}")
    print("MCP_CUBELESS_PCG_PRODUCTION_CANDIDATE_BUILD_END")


if __name__ == "__main__":
    time.sleep(0.1)
    main()
