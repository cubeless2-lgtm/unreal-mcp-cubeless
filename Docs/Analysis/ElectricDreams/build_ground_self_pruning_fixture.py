import unreal


PACKAGE_PATH = "/Game/_MCP_Temp/PCG"
ASSET_NAME = "ElectricDreams_SelfPruningFixture_MCP"
GRAPH_PATH = f"{PACKAGE_PATH}/{ASSET_NAME}.{ASSET_NAME}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_ElectricDreams_SelfPruningFixture"

DENSITY_FILTER_LOWER = 0.0
DENSITY_FILTER_UPPER = 1.0
SELF_PRUNING_RANDOMIZED = False
SELF_PRUNING_RADIUS_SIMILARITY = 1.0

SOURCE_POINTS = [
    {"name": "ClusterA_Large", "seed": 100, "coord": (0, 0, 0), "extent": (120, 120, 80), "density": 1.0},
    {"name": "ClusterA_SmallCenter", "seed": 101, "coord": (0, 0, 0), "extent": (35, 35, 35), "density": 0.95},
    {"name": "ClusterA_SmallRight", "seed": 102, "coord": (24, 0, 0), "extent": (30, 30, 30), "density": 0.90},
    {"name": "ClusterA_TinyLeft", "seed": 103, "coord": (-18, 8, 0), "extent": (20, 20, 20), "density": 0.85},
    {"name": "ClusterB_Large", "seed": 200, "coord": (460, 0, 0), "extent": (110, 110, 70), "density": 1.0},
    {"name": "ClusterB_SmallCenter", "seed": 201, "coord": (460, 0, 0), "extent": (32, 32, 32), "density": 0.90},
    {"name": "FarSingletonA", "seed": 300, "coord": (900, 0, 0), "extent": (35, 35, 35), "density": 0.78},
    {"name": "FarSingletonB", "seed": 301, "coord": (1120, 0, 0), "extent": (35, 35, 35), "density": 0.74},
]


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


def configure_points(node):
    settings = node.get_settings()
    points = settings.get_editor_property("points_to_create")
    points.clear()
    for spec in SOURCE_POINTS:
        point = unreal.PCGPoint()
        transform = point.get_editor_property("transform")
        x, y, z = spec["coord"]
        transform.set_editor_property("translation", unreal.Vector(float(x), float(y), float(z)))
        point.set_editor_property("transform", transform)

        ex, ey, ez = spec["extent"]
        point.set_editor_property("bounds_min", unreal.Vector(-float(ex), -float(ey), -float(ez)))
        point.set_editor_property("bounds_max", unreal.Vector(float(ex), float(ey), float(ez)))
        point.set_editor_property("density", float(spec["density"]))
        point.set_editor_property("steepness", 1.0)
        point.set_editor_property("seed", int(spec["seed"]))
        points.append(point)
    settings.set_editor_property("points_to_create", points)
    settings.set_editor_property("cull_points_outside_volume", False)


def configure_density_filter(node):
    settings = node.get_settings()
    settings.set_editor_property("lower_bound", float(DENSITY_FILTER_LOWER))
    settings.set_editor_property("upper_bound", float(DENSITY_FILTER_UPPER))
    settings.set_editor_property("invert_filter", False)
    settings.set_editor_property("keep_zero_density_points", False)


def configure_self_pruning(node):
    settings = node.get_settings()
    params = settings.get_editor_property("parameters")
    params.set_editor_property("randomized_pruning", bool(SELF_PRUNING_RANDOMIZED))
    params.set_editor_property("radius_similarity_factor", float(SELF_PRUNING_RADIUS_SIMILARITY))
    try:
        params.set_editor_property("pruning_type", unreal.PCGSelfPruningType.LARGE_TO_SMALL)
    except Exception:
        pass
    settings.set_editor_property("parameters", params)


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


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def build_graph():
    unreal.EditorAssetLibrary.make_directory(PACKAGE_PATH)
    graph = unreal.EditorAssetLibrary.load_asset(GRAPH_PATH)
    if not graph:
        graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            ASSET_NAME,
            PACKAGE_PATH,
            unreal.PCGGraph.static_class(),
            unreal.PCGGraphFactory(),
        )
    if not graph:
        raise RuntimeError(f"Failed to create/load {GRAPH_PATH}")

    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)

    source = add_node(graph, unreal.PCGCreatePointsSettings, "01 Overlap Source Points x8", -900, 0)
    density_filter = add_node(graph, unreal.PCGDensityFilterSettings, "02 Ground DensityFilter Broad Pass", -600, 0)
    self_pruning = add_node(graph, unreal.PCGSelfPruningSettings, "03 Destructive SelfPruning LargeToSmall", -300, 0)
    pass_marker = add_node(graph, unreal.PCGAddAttributeSettings, "04 SelfPruningFixturePass True", 0, 0)

    configure_points(source)
    configure_density_filter(density_filter)
    configure_self_pruning(self_pruning)
    configure_add(pass_marker, "SelfPruningFixturePass", "@Last", unreal.PCGMetadataTypes.BOOLEAN, True)

    graph.add_edge(source, "Out", density_filter, "In")
    graph.add_edge(density_filter, "Out", self_pruning, "In")
    graph.add_edge(self_pruning, "Out", pass_marker, "In")
    graph.add_edge(pass_marker, "Out", graph.get_output_node(), "Out")

    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def spawn_fixture_actor(graph):
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for actor in get_all_level_actors():
        if actor.get_actor_label() == ACTOR_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PCGVolume,
        unreal.Vector(2300, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(ACTOR_LABEL)
    pcg = actor.pcg_component
    pcg.set_graph(graph)
    pcg.cleanup(True)
    pcg.generate(True)
    return actor


def main():
    print("MCP_PCG_SELF_PRUNING_FIXTURE_BUILD_BEGIN")
    graph = build_graph()
    actor = spawn_fixture_actor(graph)
    print(f"fixture_graph={graph.get_path_name()}")
    print(f"fixture_actor={actor.get_actor_label()}")
    print(f"source_point_count={len(SOURCE_POINTS)}")
    print(f"density_filter_lower={DENSITY_FILTER_LOWER}")
    print(f"density_filter_upper={DENSITY_FILTER_UPPER}")
    print(f"self_pruning_randomized={SELF_PRUNING_RANDOMIZED}")
    print(f"self_pruning_radius_similarity={SELF_PRUNING_RADIUS_SIMILARITY}")
    print(f"source_seeds={[spec['seed'] for spec in SOURCE_POINTS]}")
    print("MCP_PCG_SELF_PRUNING_FIXTURE_BUILD_END")


if __name__ == "__main__":
    main()
