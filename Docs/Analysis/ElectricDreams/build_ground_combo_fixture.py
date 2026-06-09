import unreal


PACKAGE_PATH = "/Game/_MCP_Temp/PCG"
ASSET_NAME = "ElectricDreams_GroundComboFixture_MCP"
GRAPH_PATH = f"{PACKAGE_PATH}/{ASSET_NAME}.{ASSET_NAME}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_ElectricDreams_GroundComboFixture"

DENSITY_REMAP_RANGE_MIN = 0.0
DENSITY_REMAP_RANGE_MAX = 1.0
DENSITY_REMAP_OUT_MIN = 0.1
DENSITY_REMAP_OUT_MAX = 0.9
DENSITY_REMAP_EXCLUDE_OUTSIDE = False
SELF_PRUNING_RANDOMIZED = False
SELF_PRUNING_RADIUS_SIMILARITY = 1.0

SOURCE_POINTS = [
    {"seed": 20, "coord": (0, 0, 0), "density": 0.20},
    {"seed": 21, "coord": (40, 0, 0), "density": 0.32},
    {"seed": 22, "coord": (80, 0, 0), "density": 0.44},
    {"seed": 23, "coord": (300, 0, 0), "density": 0.56},
    {"seed": 24, "coord": (340, 0, 0), "density": 0.68},
    {"seed": 25, "coord": (620, 0, 0), "density": 0.80},
]

BOUNDS_PROFILES = {
    "tight": {
        "id": 0,
        "bounds_min": (-8.0, -8.0, -8.0),
        "bounds_max": (8.0, 8.0, 8.0),
    },
    "expanded": {
        "id": 1,
        "bounds_min": (-64.0, -32.0, -16.0),
        "bounds_max": (64.0, 32.0, 16.0),
    },
}


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
        point.set_editor_property("bounds_min", unreal.Vector(-4.0, -4.0, -4.0))
        point.set_editor_property("bounds_max", unreal.Vector(4.0, 4.0, 4.0))
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


def configure_bounds_modifier(node, profile):
    settings = node.get_settings()
    settings.set_editor_property("mode", unreal.PCGBoundsModifierMode.SET)
    settings.set_editor_property("bounds_min", unreal.Vector(*profile["bounds_min"]))
    settings.set_editor_property("bounds_max", unreal.Vector(*profile["bounds_max"]))


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


def build_profile_branch(graph, profile_name, x, y):
    profile = BOUNDS_PROFILES[profile_name]
    source = add_node(graph, unreal.PCGCreatePointsSettings, f"01 {profile_name} Source x6", x, y)
    remap = add_node(graph, unreal.PCGDensityRemapSettings, f"02 {profile_name} DensityRemap", x + 280, y)
    bounds = add_node(graph, unreal.PCGBoundsModifierSettings, f"03 {profile_name} Bounds Set", x + 560, y)
    pruning = add_node(graph, unreal.PCGSelfPruningSettings, f"04 {profile_name} SelfPruning", x + 840, y)
    profile_id = add_node(graph, unreal.PCGAddAttributeSettings, f"05 {profile_name} BoundsProfileId", x + 1120, y)
    pass_marker = add_node(graph, unreal.PCGAddAttributeSettings, f"06 {profile_name} GroundComboFixturePass", x + 1400, y)

    configure_points(source)
    configure_density_remap(remap)
    configure_bounds_modifier(bounds, profile)
    configure_self_pruning(pruning)
    configure_add(profile_id, "BoundsProfileId", "@Last", unreal.PCGMetadataTypes.INTEGER32, profile["id"])
    configure_add(pass_marker, "GroundComboFixturePass", "@Last", unreal.PCGMetadataTypes.BOOLEAN, True)

    graph.add_edge(source, "Out", remap, "In")
    graph.add_edge(remap, "Out", bounds, "In")
    graph.add_edge(bounds, "Out", pruning, "In")
    graph.add_edge(pruning, "Out", profile_id, "In")
    graph.add_edge(profile_id, "Out", pass_marker, "In")
    return pass_marker


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

    tight_output = build_profile_branch(graph, "tight", -1200, -180)
    expanded_output = build_profile_branch(graph, "expanded", -1200, 220)
    merge = add_node(graph, unreal.PCGMergeSettings, "07 Merge Profile Outputs", 520, 20)

    graph.add_edge(tight_output, "Out", merge, "In")
    graph.add_edge(expanded_output, "Out", merge, "In")
    graph.add_edge(merge, "Out", graph.get_output_node(), "Out")

    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def spawn_fixture_actor(graph):
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for actor in get_all_level_actors():
        if actor.get_actor_label() == ACTOR_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PCGVolume,
        unreal.Vector(3100, 0, 0),
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
    print("MCP_PCG_GROUND_COMBO_FIXTURE_BUILD_BEGIN")
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
    print(f"self_pruning_randomized={SELF_PRUNING_RANDOMIZED}")
    print(f"self_pruning_radius_similarity={SELF_PRUNING_RADIUS_SIMILARITY}")
    print(f"bounds_profiles={BOUNDS_PROFILES}")
    print(f"source_seeds={[spec['seed'] for spec in SOURCE_POINTS]}")
    print(f"expected_densities={[round(expected_density(spec['density']), 3) for spec in SOURCE_POINTS]}")
    print("MCP_PCG_GROUND_COMBO_FIXTURE_BUILD_END")


if __name__ == "__main__":
    main()
