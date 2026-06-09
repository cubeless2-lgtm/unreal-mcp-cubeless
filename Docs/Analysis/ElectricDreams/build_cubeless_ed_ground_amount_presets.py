import unreal


GROUND_BUILDER_SCRIPT = r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\build_cubeless_ground_controls_prototype.py"
PACKAGE_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning/AmountPresets"
CORE_ASSET_NAME = "PCG_Cubeless_ED_GroundControlsCore"
CORE_GRAPH_PATH = f"{PACKAGE_PATH}/{CORE_ASSET_NAME}.{CORE_ASSET_NAME}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_GroundAmount"

PROFILE_ID = 10
PROFILE_TYPE = 1

AMOUNT_SPECS = [
    {
        "name": "Sparse",
        "asset_name": "PCG_Cubeless_ED_GroundAmount_Sparse",
        "amount_id": 201,
        "amount_type": 1,
        "density_filter": (0.8, 1.0),
        "duplicate_iterations": 0,
        "expected_points": 3,
        "expected_ism": 3,
    },
    {
        "name": "Normal",
        "asset_name": "PCG_Cubeless_ED_GroundAmount_Normal",
        "amount_id": 202,
        "amount_type": 2,
        "density_filter": None,
        "duplicate_iterations": 0,
        "expected_points": 8,
        "expected_ism": 8,
    },
    {
        "name": "Dense",
        "asset_name": "PCG_Cubeless_ED_GroundAmount_Dense",
        "amount_id": 203,
        "amount_type": 3,
        "density_filter": None,
        "duplicate_iterations": 1,
        "expected_points": 16,
        "expected_ism": 16,
    },
]

AMOUNT_GRAPH_PATHS = {
    spec["name"]: f"{PACKAGE_PATH}/{spec['asset_name']}.{spec['asset_name']}"
    for spec in AMOUNT_SPECS
}


def load_ground_builder():
    namespace = {"__name__": "_cubeless_ground_controls_builder"}
    with open(GROUND_BUILDER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), GROUND_BUILDER_SCRIPT, "exec")
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
    transform.set_editor_property("translation", unreal.Vector(42.0, 42.0, 0.0))
    settings.set_editor_property("point_transform", transform)


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def build_core_graph(builder):
    unreal.EditorAssetLibrary.make_directory(PACKAGE_PATH)
    graph = unreal.EditorAssetLibrary.load_asset(CORE_GRAPH_PATH)
    if not graph:
        graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            CORE_ASSET_NAME,
            PACKAGE_PATH,
            unreal.PCGGraph.static_class(),
            unreal.PCGGraphFactory(),
        )
    if not graph:
        raise RuntimeError(f"Failed to create/load {CORE_GRAPH_PATH}")

    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)

    small_output = builder["build_profile_branch"](graph, "ed_small_set", -3200, -220)
    medium_output = builder["build_profile_branch"](graph, "ed_medium_set", -3200, 240)
    merge = builder["add_node"](graph, unreal.PCGMergeSettings, "13 Merge Ground Control Core Profiles", 160, 20)
    graph.add_edge(small_output, "Out", merge, "In")
    graph.add_edge(medium_output, "Out", merge, "In")
    graph.add_edge(merge, "Out", graph.get_output_node(), "Out")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def add_profile_and_amount_markers(graph, upstream, spec, x, y):
    profile_id = add_node(graph, unreal.PCGAddAttributeSettings, "DesignerProfileId GroundControls", x, y)
    profile_type = add_node(graph, unreal.PCGAddAttributeSettings, "DesignerProfileType GroundControls", x + 320, y)
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
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            spec["asset_name"],
            PACKAGE_PATH,
            unreal.PCGGraph.static_class(),
            unreal.PCGGraphFactory(),
        )
    if not graph:
        raise RuntimeError(f"Failed to create/load amount graph: {spec['name']}")

    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)

    source = add_node(graph, unreal.PCGSubgraphSettings, f"{spec['name']} GroundControlsCore", -1200, 0)
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
    builder["configure_grass_spawner"](spawner)
    graph.add_edge(markers, "Out", spawner, "In")
    graph.add_edge(spawner, "Out", graph.get_output_node(), "Out")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def spawn_validation_actor(spec, graph, index):
    label = f"{ACTOR_LABEL_PREFIX}_{spec['name']}_Validation"
    for actor in get_all_level_actors():
        if actor.get_actor_label() == label:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PCGVolume,
        unreal.Vector(9000 + index * 420, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(label)
    pcg = actor.pcg_component
    pcg.set_graph(graph)
    pcg.cleanup(True)
    pcg.generate(True)
    return actor


def main():
    print("MCP_CUBELESS_ED_GROUND_AMOUNT_PRESETS_BUILD_BEGIN")
    builder = load_ground_builder()
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
    print("MCP_CUBELESS_ED_GROUND_AMOUNT_PRESETS_BUILD_END")


if __name__ == "__main__":
    main()
