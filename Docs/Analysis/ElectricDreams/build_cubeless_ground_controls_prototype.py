import unreal


PACKAGE_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning"
ASSET_NAME = "PCG_Cubeless_GroundControlsPrototype"
GRAPH_PATH = f"{PACKAGE_PATH}/{ASSET_NAME}.{ASSET_NAME}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_Cubeless_GroundControlsPrototype_Validation"
GRASS_MESH_PATH = (
    "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Grass/"
    "SM_Grass_Medium01.SM_Grass_Medium01"
)

DITCH_BRANCH_DENSITY_THRESHOLD = 0.3
GROUND_DENSITY_FILTER_LOWER = 0.5
GROUND_DENSITY_FILTER_UPPER = 1.0
DENSITY_REMAP_RANGE_MIN = 0.0
DENSITY_REMAP_RANGE_MAX = 1.0
DENSITY_REMAP_OUT_MIN = 0.5
DENSITY_REMAP_OUT_MAX = 1.0
DENSITY_REMAP_EXCLUDE_OUTSIDE = False
SELF_PRUNING_RANDOMIZED = False
SELF_PRUNING_RADIUS_SIMILARITY = 0.25

SOURCE_POINTS = [
    {"seed": 30, "coord": (0, 0, 0), "density": 0.20},
    {"seed": 31, "coord": (90, 0, 0), "density": 0.32},
    {"seed": 32, "coord": (180, 0, 0), "density": 0.44},
    {"seed": 33, "coord": (360, 0, 0), "density": 0.56},
    {"seed": 34, "coord": (450, 0, 0), "density": 0.68},
    {"seed": 35, "coord": (720, 0, 0), "density": 0.80},
]

BOUNDS_PROFILES = {
    "ed_small_set": {
        "id": 10,
        "side_mask": 0.0,
        "branch_density": 0.65,
        "bounds_min": (-25.0, -25.0, -25.0),
        "bounds_max": (25.0, 25.0, 25.0),
    },
    "ed_medium_set": {
        "id": 20,
        "side_mask": 1.0,
        "branch_density": 0.85,
        "bounds_min": (-50.0, -50.0, -50.0),
        "bounds_max": (50.0, 50.0, 50.0),
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


def filter_operator_enum(operator_name):
    try:
        return getattr(unreal.PCGAttributeFilterOperator, operator_name)
    except AttributeError as exc:
        raise RuntimeError(f"Unknown PCGAttributeFilterOperator={operator_name!r}") from exc


def configure_attribute_filter_constant(node, attr, threshold, operator_name="GREATER_OR_EQUAL"):
    settings = node.get_settings()
    settings.set_editor_property("operator", filter_operator_enum(operator_name))
    settings.set_editor_property("use_constant_threshold", True)
    selector_import(settings, "target_attribute", attr)
    selector_import(settings, "threshold_attribute", attr)
    value_struct = settings.get_editor_property("attribute_types")
    set_const_value_struct(value_struct, unreal.PCGMetadataTypes.DOUBLE, threshold)
    settings.set_editor_property("attribute_types", value_struct)
    settings.set_editor_property("warn_on_data_missing_attribute", True)


def configure_density_remap(node):
    settings = node.get_settings()
    settings.set_editor_property("range_min", float(DENSITY_REMAP_RANGE_MIN))
    settings.set_editor_property("range_max", float(DENSITY_REMAP_RANGE_MAX))
    settings.set_editor_property("out_range_min", float(DENSITY_REMAP_OUT_MIN))
    settings.set_editor_property("out_range_max", float(DENSITY_REMAP_OUT_MAX))
    settings.set_editor_property("exclude_values_outside_input_range", bool(DENSITY_REMAP_EXCLUDE_OUTSIDE))


def configure_density_filter(node):
    settings = node.get_settings()
    settings.set_editor_property("lower_bound", float(GROUND_DENSITY_FILTER_LOWER))
    settings.set_editor_property("upper_bound", float(GROUND_DENSITY_FILTER_UPPER))
    settings.set_editor_property("invert_filter", False)
    settings.set_editor_property("keep_zero_density_points", False)


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
        params.set_editor_property("pruning_type", unreal.PCGSelfPruningType.ALL_EQUAL)
    except Exception:
        pass
    settings.set_editor_property("parameters", params)


def configure_grass_spawner(node):
    mesh = unreal.EditorAssetLibrary.load_asset(GRASS_MESH_PATH)
    if not mesh:
        raise RuntimeError(f"Failed to load grass mesh: {GRASS_MESH_PATH}")
    settings = node.get_settings()
    descriptor = unreal.PCGSoftISMComponentDescriptor()
    descriptor.set_editor_property("static_mesh", mesh)
    entry = unreal.PCGMeshSelectorWeightedEntry()
    entry.set_editor_property("descriptor", descriptor)
    entry.set_editor_property("weight", 1)
    params = settings.get_editor_property("mesh_selector_parameters")
    params.set_editor_property("mesh_entries", [entry])


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
    branch_density = add_node(graph, unreal.PCGAddAttributeSettings, f"02 {profile_name} BranchDensity Candidate", x + 280, y)
    side_mask = add_node(graph, unreal.PCGAddAttributeSettings, f"03 {profile_name} SideMask", x + 560, y)
    threshold = add_node(graph, unreal.PCGAddAttributeSettings, f"04 {profile_name} DitchThreshold", x + 840, y)
    ditch_filter = add_node(graph, unreal.PCGAttributeFilteringSettings, f"05 {profile_name} Ditch Density >= 0.3", x + 1120, y)
    ditch_pass = add_node(graph, unreal.PCGAddAttributeSettings, f"06 {profile_name} DitchCandidatePass", x + 1400, y)
    density_remap = add_node(graph, unreal.PCGDensityRemapSettings, f"07 {profile_name} Ground Remap 0-1 to 0.5-1", x + 1680, y)
    density_filter = add_node(graph, unreal.PCGDensityFilterSettings, f"08 {profile_name} Ground High Density 0.5-1", x + 1960, y)
    bounds = add_node(graph, unreal.PCGBoundsModifierSettings, f"09 {profile_name} Bounds Set", x + 2240, y)
    pruning = add_node(graph, unreal.PCGSelfPruningSettings, f"10 {profile_name} SelfPruning Equal", x + 2520, y)
    profile_id = add_node(graph, unreal.PCGAddAttributeSettings, f"11 {profile_name} BoundsProfileId", x + 2800, y)
    pass_marker = add_node(graph, unreal.PCGAddAttributeSettings, f"12 {profile_name} GroundControlsPass", x + 3080, y)

    configure_points(source)
    configure_add(branch_density, "BranchDensity", "@Last", unreal.PCGMetadataTypes.DOUBLE, profile["branch_density"])
    configure_add(side_mask, "SideMask", "@Last", unreal.PCGMetadataTypes.DOUBLE, profile["side_mask"])
    configure_add(threshold, "DitchDensityThreshold", "@Last", unreal.PCGMetadataTypes.DOUBLE, DITCH_BRANCH_DENSITY_THRESHOLD)
    configure_attribute_filter_constant(ditch_filter, "$Density", DITCH_BRANCH_DENSITY_THRESHOLD)
    configure_add(ditch_pass, "DitchStyleCandidatePass", "@Last", unreal.PCGMetadataTypes.BOOLEAN, True)
    configure_density_remap(density_remap)
    configure_density_filter(density_filter)
    configure_bounds_modifier(bounds, profile)
    configure_self_pruning(pruning)
    configure_add(profile_id, "BoundsProfileId", "@Last", unreal.PCGMetadataTypes.INTEGER32, profile["id"])
    configure_add(pass_marker, "CubelessGroundControlsPass", "@Last", unreal.PCGMetadataTypes.BOOLEAN, True)

    graph.add_edge(source, "Out", branch_density, "In")
    graph.add_edge(branch_density, "Out", side_mask, "In")
    graph.add_edge(side_mask, "Out", threshold, "In")
    graph.add_edge(threshold, "Out", ditch_filter, "In")
    graph.add_edge(ditch_filter, "InsideFilter", ditch_pass, "In")
    graph.add_edge(ditch_pass, "Out", density_remap, "In")
    graph.add_edge(density_remap, "Out", density_filter, "In")
    graph.add_edge(density_filter, "Out", bounds, "In")
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

    small_output = build_profile_branch(graph, "ed_small_set", -3200, -220)
    medium_output = build_profile_branch(graph, "ed_medium_set", -3200, 240)
    merge = add_node(graph, unreal.PCGMergeSettings, "13 Merge ED Candidate Profiles", 160, 20)
    spawner = add_node(graph, unreal.PCGStaticMeshSpawnerSettings, "14 Spawn Cubeless Grass Mesh", 460, 20)

    configure_grass_spawner(spawner)

    graph.add_edge(small_output, "Out", merge, "In")
    graph.add_edge(medium_output, "Out", merge, "In")
    graph.add_edge(merge, "Out", spawner, "In")
    graph.add_edge(spawner, "Out", graph.get_output_node(), "Out")

    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def spawn_validation_actor(graph):
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for actor in get_all_level_actors():
        if actor.get_actor_label() == ACTOR_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PCGVolume,
        unreal.Vector(3500, 0, 0),
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


def expected_ditch_survivor_seeds():
    return [
        int(spec["seed"])
        for spec in SOURCE_POINTS
        if float(spec["density"]) >= float(DITCH_BRANCH_DENSITY_THRESHOLD)
    ]


def main():
    print("MCP_CUBELESS_GROUND_CONTROLS_PROTOTYPE_BUILD_BEGIN")
    graph = build_graph()
    actor = spawn_validation_actor(graph)
    print(f"production_graph={graph.get_path_name()}")
    print(f"validation_actor={actor.get_actor_label()}")
    print(f"grass_mesh={GRASS_MESH_PATH}")
    print(f"source_point_count={len(SOURCE_POINTS)}")
    print(f"ditch_branch_density_threshold={DITCH_BRANCH_DENSITY_THRESHOLD}")
    print(f"expected_ditch_survivor_seeds={expected_ditch_survivor_seeds()}")
    print(f"ground_density_filter_lower={GROUND_DENSITY_FILTER_LOWER}")
    print(f"ground_density_filter_upper={GROUND_DENSITY_FILTER_UPPER}")
    print(f"density_remap_range_min={DENSITY_REMAP_RANGE_MIN}")
    print(f"density_remap_range_max={DENSITY_REMAP_RANGE_MAX}")
    print(f"density_remap_out_min={DENSITY_REMAP_OUT_MIN}")
    print(f"density_remap_out_max={DENSITY_REMAP_OUT_MAX}")
    print(f"self_pruning_randomized={SELF_PRUNING_RANDOMIZED}")
    print(f"self_pruning_radius_similarity={SELF_PRUNING_RADIUS_SIMILARITY}")
    print(f"bounds_profiles={BOUNDS_PROFILES}")
    print(f"expected_densities={[round(expected_density(spec['density']), 3) for spec in SOURCE_POINTS]}")
    print("MCP_CUBELESS_GROUND_CONTROLS_PROTOTYPE_BUILD_END")


if __name__ == "__main__":
    main()
