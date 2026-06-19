import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get("__file__", pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "build_cubeless_ed_ditch_amount_presets.py")
).parent
DITCH_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ditch_hierarchy_prototype.py"

PACKAGE_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning/AmountPresets"
CORE_ASSET_NAME = "PCG_Cubeless_ED_DitchHierarchyCore"
CORE_GRAPH_PATH = f"{PACKAGE_PATH}/{CORE_ASSET_NAME}.{CORE_ASSET_NAME}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
VALIDATION_BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/"
    "BP_Cubeless_ED_PCGDesignerControlActor.BP_Cubeless_ED_PCGDesignerControlActor_C"
)
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_DitchAmount"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0

PROFILE_ID = 20
PROFILE_TYPE = 2

AMOUNT_SPECS = [
    {
        "name": "Sparse",
        "asset_name": "PCG_Cubeless_ED_DitchAmount_Sparse",
        "amount_id": 301,
        "amount_type": 1,
        "density_filter": (0.9, 1.0),
        "duplicate_iterations": 0,
        "expected_points": 18,
        "expected_ism": 18,
    },
    {
        "name": "Normal",
        "asset_name": "PCG_Cubeless_ED_DitchAmount_Normal",
        "amount_id": 302,
        "amount_type": 2,
        "density_filter": None,
        "duplicate_iterations": 0,
        "expected_points": 42,
        "expected_ism": 42,
    },
    {
        "name": "Dense",
        "asset_name": "PCG_Cubeless_ED_DitchAmount_Dense",
        "amount_id": 303,
        "amount_type": 3,
        "density_filter": None,
        "duplicate_iterations": 1,
        "expected_points": 84,
        "expected_ism": 84,
    },
]

AMOUNT_GRAPH_PATHS = {
    spec["name"]: f"{PACKAGE_PATH}/{spec['asset_name']}.{spec['asset_name']}"
    for spec in AMOUNT_SPECS
}


def load_ditch_builder():
    namespace = {"__name__": "_cubeless_ditch_hierarchy_builder"}
    with open(DITCH_BUILDER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(DITCH_BUILDER_SCRIPT), "exec")
    exec(code, namespace)
    return namespace


def add_node(graph, settings_cls, title, x, y):
    created = graph.add_node_of_type(settings_cls.static_class())
    node = created[0] if isinstance(created, tuple) else created
    node.set_editor_property("node_title", title)
    try:
        node.set_node_position(unreal.Vector2D(x, y))
    except Exception:
        pass
    return node


def selector_import(settings, prop, text):
    selector = settings.get_editor_property(prop)
    selector.import_text(f"PCGBegin({text})PCGEnd")
    settings.set_editor_property(prop, selector)


def set_const_value_struct(value_struct, value_type, value):
    value_struct.set_editor_property("type", value_type)
    if value_type == unreal.PCGMetadataTypes.BOOLEAN:
        value_struct.set_editor_property("bool_value", bool(value))
    elif value_type == unreal.PCGMetadataTypes.INTEGER32:
        value_struct.set_editor_property("int32_value", int(value))
        value_struct.set_editor_property("int_value", int(value))
    elif value_type == unreal.PCGMetadataTypes.INTEGER64:
        value_struct.set_editor_property("int_value", int(value))
        value_struct.set_editor_property("int32_value", int(value))
    else:
        value_struct.set_editor_property("double_value", float(value))
        value_struct.set_editor_property("float_value", float(value))
    return value_struct


def configure_add(node, output_attr, input_attr="@Last", value_type=None, value=None):
    settings = node.get_settings()
    settings.set_editor_property("copy_all_attributes", False)
    settings.set_editor_property("copy_all_domains", False)
    selector_import(settings, "input_source", input_attr)
    selector_import(settings, "output_target", output_attr)
    if value_type is not None:
        value_struct = settings.get_editor_property("attribute_types")
        set_const_value_struct(value_struct, value_type, value)
        settings.set_editor_property("attribute_types", value_struct)


def configure_subgraph(node, subgraph_path):
    subgraph = unreal.EditorAssetLibrary.load_asset(subgraph_path)
    if not subgraph:
        raise RuntimeError(f"Missing subgraph asset: {subgraph_path}")
    settings = node.get_settings()
    instance = settings.get_editor_property("subgraph_instance")
    instance.set_editor_property("graph", subgraph)


def configure_density_filter(node, lower, upper):
    settings = node.get_settings()
    settings.set_editor_property("lower_bound", float(lower))
    settings.set_editor_property("upper_bound", float(upper))
    settings.set_editor_property("invert_filter", False)
    settings.set_editor_property("keep_zero_density_points", False)


def configure_duplicate(node, iterations):
    settings = node.get_settings()
    settings.set_editor_property("iterations", int(iterations))
    settings.set_editor_property("output_source_point", True)
    transform = settings.get_editor_property("point_transform")
    transform.set_editor_property("translation", unreal.Vector(55.0, 55.0, 0.0))
    settings.set_editor_property("point_transform", transform)


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def configure_validation_spline(actor):
    splines = actor.get_components_by_class(unreal.SplineComponent)
    if not splines:
        raise RuntimeError("Validation actor has no SplineComponent")
    half_length = (float(TARGET_SAMPLE_COUNT) - 1.0) * float(TARGET_POINT_SPACING) * 0.5
    for spline in splines:
        spline.clear_spline_points(False)
        spline.add_spline_point(unreal.Vector(0, -half_length, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, 0, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, half_length, 0), unreal.SplineCoordinateSpace.LOCAL, True)
        spline.update_spline()


def ensure_graph(path, asset_name):
    unreal.EditorAssetLibrary.make_directory(PACKAGE_PATH)
    graph = unreal.EditorAssetLibrary.load_asset(path)
    if graph:
        return graph
    graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        asset_name,
        PACKAGE_PATH,
        unreal.PCGGraph.static_class(),
        unreal.PCGGraphFactory(),
    )
    if not graph:
        raise RuntimeError(f"Failed to create/load {path}")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def node_title(node):
    try:
        return str(node.get_editor_property("node_title"))
    except Exception:
        return ""


def build_core_graph(builder):
    graph = ensure_graph(CORE_GRAPH_PATH, CORE_ASSET_NAME)
    base = builder["BASE"]
    old_graph_path = base["GRAPH_PATH"]
    try:
        base["GRAPH_PATH"] = CORE_GRAPH_PATH
        graph = base["build_graph"]()
    finally:
        base["GRAPH_PATH"] = old_graph_path

    apply_node = None
    spawner_node = None
    for node in list(graph.get_editor_property("nodes")):
        settings = node.get_settings()
        settings_class = settings.get_class().get_name() if settings else ""
        title = node_title(node)
        if settings_class == "PCGApplyHierarchySettings" or "Apply Offset Hierarchy" in title:
            apply_node = node
        if settings_class == "PCGStaticMeshSpawnerSettings" or "Spawn Cubeless Grass Mesh" in title:
            spawner_node = node

    if not apply_node:
        raise RuntimeError("Failed to find ApplyHierarchy node in Ditch core graph")
    if spawner_node:
        graph.remove_node(spawner_node)
    graph.add_edge(apply_node, "Out", graph.get_output_node(), "Out")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def add_profile_and_amount_markers(graph, upstream, spec, x, y):
    profile_id = add_node(graph, unreal.PCGAddAttributeSettings, "DesignerProfileId DitchHierarchy", x, y)
    profile_type = add_node(graph, unreal.PCGAddAttributeSettings, "DesignerProfileType DitchHierarchy", x + 320, y)
    amount_id = add_node(graph, unreal.PCGAddAttributeSettings, f"Amount {spec['amount_id']} DesignerAmountId", x + 640, y)
    amount_type = add_node(graph, unreal.PCGAddAttributeSettings, f"Amount {spec['amount_id']} DesignerAmountType", x + 960, y)
    amount_pass = add_node(graph, unreal.PCGAddAttributeSettings, f"Amount {spec['amount_id']} DesignerAmountPass", x + 1280, y)

    configure_add(profile_id, "DesignerProfileId", "@Last", unreal.PCGMetadataTypes.INTEGER32, PROFILE_ID)
    configure_add(profile_type, "DesignerProfileType", "@Last", unreal.PCGMetadataTypes.INTEGER32, PROFILE_TYPE)
    configure_add(amount_id, "DesignerAmountId", "@Last", unreal.PCGMetadataTypes.INTEGER32, spec["amount_id"])
    configure_add(amount_type, "DesignerAmountType", "@Last", unreal.PCGMetadataTypes.INTEGER32, spec["amount_type"])
    configure_add(amount_pass, "DesignerAmountPass", "@Last", unreal.PCGMetadataTypes.BOOLEAN, True)

    graph.add_edge(upstream, "Out", profile_id, "In")
    graph.add_edge(profile_id, "Out", profile_type, "In")
    graph.add_edge(profile_type, "Out", amount_id, "In")
    graph.add_edge(amount_id, "Out", amount_type, "In")
    graph.add_edge(amount_type, "Out", amount_pass, "In")
    return amount_pass


def build_amount_graph(builder, spec):
    graph_path = AMOUNT_GRAPH_PATHS[spec["name"]]
    graph = ensure_graph(graph_path, spec["asset_name"])
    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)

    source = add_node(graph, unreal.PCGSubgraphSettings, f"{spec['name']} DitchHierarchyCore", -1200, 0)
    configure_subgraph(source, CORE_GRAPH_PATH)
    graph.add_edge(graph.get_input_node(), "In", source, "In")
    upstream = source
    x = -820

    if spec["density_filter"]:
        lower, upper = spec["density_filter"]
        density_filter = add_node(graph, unreal.PCGDensityFilterSettings, f"{spec['name']} Density {lower}-{upper}", x, 0)
        configure_density_filter(density_filter, lower, upper)
        graph.add_edge(upstream, "Out", density_filter, "In")
        upstream = density_filter
        x += 320

    if spec["duplicate_iterations"] > 0:
        duplicate = add_node(graph, unreal.PCGDuplicatePointSettings, f"{spec['name']} Duplicate x{spec['duplicate_iterations']}", x, 0)
        configure_duplicate(duplicate, spec["duplicate_iterations"])
        graph.add_edge(upstream, "Out", duplicate, "In")
        upstream = duplicate
        x += 320

    markers = add_profile_and_amount_markers(graph, upstream, spec, x, 0)
    spawner = add_node(graph, unreal.PCGStaticMeshSpawnerSettings, f"{spec['name']} Spawn Grass Mesh", x + 1660, 0)
    builder["BASE"]["configure_grass_spawner"](spawner)
    graph.add_edge(markers, "Out", spawner, "In")
    graph.add_edge(spawner, "Out", graph.get_output_node(), "Out")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def spawn_validation_actor(spec, graph, index):
    label = f"{ACTOR_LABEL_PREFIX}_{spec['name']}_Validation"
    for actor in get_all_level_actors():
        if actor.get_actor_label() == label:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    actor_class = unreal.load_class(None, VALIDATION_BLUEPRINT_CLASS_PATH)
    if not actor_class:
        raise RuntimeError(f"Missing validation actor class: {VALIDATION_BLUEPRINT_CLASS_PATH}")
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(11800 + index * 460, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(label)
    configure_validation_spline(actor)
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {label}")
    for component in pcg_components:
        component.set_graph(graph)
        component.cleanup(True)
        component.generate(True)
    return actor


def main():
    print("MCP_CUBELESS_ED_DITCH_AMOUNT_PRESETS_BUILD_BEGIN")
    builder = load_ditch_builder()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    core_graph = build_core_graph(builder)
    print(f"core_graph={core_graph.get_path_name()}")
    for index, spec in enumerate(AMOUNT_SPECS):
        graph = build_amount_graph(builder, spec)
        actor = spawn_validation_actor(spec, graph, index)
        print(f"amount={spec['name']}")
        print(f"amount_graph={graph.get_path_name()}")
        print(f"validation_actor={actor.get_actor_label()}")
        print(f"expected_points={spec['expected_points']}")
        print(f"expected_ism={spec['expected_ism']}")
        print(f"density_filter={spec['density_filter']}")
        print(f"duplicate_iterations={spec['duplicate_iterations']}")
    print("MCP_CUBELESS_ED_DITCH_AMOUNT_PRESETS_BUILD_END")


if __name__ == "__main__":
    main()
