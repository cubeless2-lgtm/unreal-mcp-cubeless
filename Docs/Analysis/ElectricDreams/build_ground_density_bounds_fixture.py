import unreal


PACKAGE_PATH = "/Game/_MCP_Temp/PCG"
ASSET_NAME = "ElectricDreams_DensityBoundsFixture_MCP"
GRAPH_PATH = f"{PACKAGE_PATH}/{ASSET_NAME}.{ASSET_NAME}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_ElectricDreams_DensityBoundsFixture"

DENSITY_REMAP_RANGE_MIN = 0.0
DENSITY_REMAP_RANGE_MAX = 1.0
DENSITY_REMAP_OUT_MIN = 0.1
DENSITY_REMAP_OUT_MAX = 0.9
DENSITY_REMAP_EXCLUDE_OUTSIDE = False

BOUNDS_SET_MIN = (-64.0, -32.0, -16.0)
BOUNDS_SET_MAX = (64.0, 32.0, 16.0)

SOURCE_POINTS = [
    {"seed": 10, "coord": (0, 0, 0), "extent": (10, 10, 10), "density": 0.2},
    {"seed": 11, "coord": (220, 0, 0), "extent": (12, 12, 12), "density": 0.5},
    {"seed": 12, "coord": (440, 0, 0), "extent": (14, 14, 14), "density": 0.8},
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


def configure_density_remap(node):
    settings = node.get_settings()
    settings.set_editor_property("range_min", float(DENSITY_REMAP_RANGE_MIN))
    settings.set_editor_property("range_max", float(DENSITY_REMAP_RANGE_MAX))
    settings.set_editor_property("out_range_min", float(DENSITY_REMAP_OUT_MIN))
    settings.set_editor_property("out_range_max", float(DENSITY_REMAP_OUT_MAX))
    settings.set_editor_property("exclude_values_outside_input_range", bool(DENSITY_REMAP_EXCLUDE_OUTSIDE))


def configure_bounds_modifier(node):
    settings = node.get_settings()
    settings.set_editor_property("mode", unreal.PCGBoundsModifierMode.SET)
    settings.set_editor_property("bounds_min", unreal.Vector(*BOUNDS_SET_MIN))
    settings.set_editor_property("bounds_max", unreal.Vector(*BOUNDS_SET_MAX))


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

    source = add_node(graph, unreal.PCGCreatePointsSettings, "01 Density Source Points x3", -900, 0)
    remap = add_node(graph, unreal.PCGDensityRemapSettings, "02 Ground DensityRemap 0.1-0.9", -600, 0)
    bounds = add_node(graph, unreal.PCGBoundsModifierSettings, "03 Ground BoundsModifier Set", -300, 0)
    pass_marker = add_node(graph, unreal.PCGAddAttributeSettings, "04 DensityBoundsFixturePass True", 0, 0)

    configure_points(source)
    configure_density_remap(remap)
    configure_bounds_modifier(bounds)
    configure_add(pass_marker, "DensityBoundsFixturePass", "@Last", unreal.PCGMetadataTypes.BOOLEAN, True)

    graph.add_edge(source, "Out", remap, "In")
    graph.add_edge(remap, "Out", bounds, "In")
    graph.add_edge(bounds, "Out", pass_marker, "In")
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
        unreal.Vector(2700, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(ACTOR_LABEL)
    pcg = actor.pcg_component
    pcg.set_graph(graph)
    pcg.cleanup(True)
    pcg.generate(True)
    return actor


def expected_density(input_density):
    alpha = (
        (float(input_density) - float(DENSITY_REMAP_RANGE_MIN))
        / (float(DENSITY_REMAP_RANGE_MAX) - float(DENSITY_REMAP_RANGE_MIN))
    )
    return float(DENSITY_REMAP_OUT_MIN) + alpha * (
        float(DENSITY_REMAP_OUT_MAX) - float(DENSITY_REMAP_OUT_MIN)
    )


def main():
    print("MCP_PCG_DENSITY_BOUNDS_FIXTURE_BUILD_BEGIN")
    graph = build_graph()
    actor = spawn_fixture_actor(graph)
    print(f"fixture_graph={graph.get_path_name()}")
    print(f"fixture_actor={actor.get_actor_label()}")
    print(f"source_point_count={len(SOURCE_POINTS)}")
    print(f"density_remap_range_min={DENSITY_REMAP_RANGE_MIN}")
    print(f"density_remap_range_max={DENSITY_REMAP_RANGE_MAX}")
    print(f"density_remap_out_min={DENSITY_REMAP_OUT_MIN}")
    print(f"density_remap_out_max={DENSITY_REMAP_OUT_MAX}")
    print(f"density_remap_exclude_outside={DENSITY_REMAP_EXCLUDE_OUTSIDE}")
    print(f"bounds_set_min={BOUNDS_SET_MIN}")
    print(f"bounds_set_max={BOUNDS_SET_MAX}")
    print(f"source_seeds={[spec['seed'] for spec in SOURCE_POINTS]}")
    print(f"expected_densities={[round(expected_density(spec['density']), 3) for spec in SOURCE_POINTS]}")
    print("MCP_PCG_DENSITY_BOUNDS_FIXTURE_BUILD_END")


if __name__ == "__main__":
    main()
