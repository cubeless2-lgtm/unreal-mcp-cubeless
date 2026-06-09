import unreal


GRAPH_PATH = "/Game/_MCP_Temp/PCG/ElectricDreams_SplineAssembly_MCP.ElectricDreams_SplineAssembly_MCP"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_ElectricDreams_SplineAssembly_Test"
BLUEPRINT_CLASS_PATH = (
    "/Game/_MCP_Temp/PCGCustomNodes/"
    "PostCopyPoints-OffsetIndices.PostCopyPoints-OffsetIndices_C"
)
GRASS_MESH_PATH = (
    "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Grass/"
    "SM_Grass_Medium01.SM_Grass_Medium01"
)

SOURCE_ASSEMBLY_PRESET = "ditch_riverbank"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0

SIDE_MODE = "both"
BRANCH_JITTER = 18.0
WIDTH_VARIANT = 1.08
HEIGHT_VARIANT = 1.15

SIDE_MASK_FILTER_PROFILE = "center_right_after_copy"
SIDE_MASK_FILTER_PROFILE_OVERRIDE = None

BRANCH_DENSITY_PRUNING_PROFILE = "leaf_mud_only"
BRANCH_DENSITY_PRUNING_PROFILE_OVERRIDE = None
BRANCH_DENSITY_NOISE_MIN = 0.98
BRANCH_DENSITY_NOISE_MAX = 1.02
BRANCH_DENSITY_FILTER_THRESHOLD = 0.70

GROUND_STYLE_DENSITY_FILTER_ENABLED = True
GROUND_STYLE_DENSITY_FILTER_LOWER = 0.0
GROUND_STYLE_DENSITY_FILTER_UPPER = 1.0
GROUND_STYLE_SELF_PRUNING_ENABLED = True
GROUND_STYLE_SELF_PRUNING_RANDOMIZED = False
GROUND_STYLE_SELF_PRUNING_RADIUS_SIMILARITY = 0.0

RIVERBANK_HALF_WIDTH = 260.0
RIVERBANK_FORWARD_STEP = 120.0
RIVERBANK_HEIGHT_STEP = 35.0
RIVERBANK_ROCK_OFFSET = 70.0

DENSITY_BY_ROLE = {
    "root": 1.0,
    "bank": 0.92,
    "silt": 0.78,
    "lower_edge": 0.86,
    "upper_edge": 0.74,
    "mud": 0.68,
    "grass": 0.96,
    "rock": 0.82,
}

SIDE_MASK_BY_SIDE = {
    "left": -1.0,
    "center": 0.0,
    "right": 1.0,
}

SIDE_MASK_FILTER_PROFILES = {
    "all_after_copy": {
        "operator": "GREATER_OR_EQUAL",
        "threshold": -1.0,
        "allowed_sides": ("left", "center", "right"),
    },
    "left_only_after_copy": {
        "operator": "LESSER_OR_EQUAL",
        "threshold": 0.0,
        "allowed_sides": ("left", "center"),
    },
    "center_only_after_copy": {
        "operator": "EQUAL",
        "threshold": 0.0,
        "allowed_sides": ("center",),
    },
    "right_only_after_copy": {
        "operator": "GREATER_OR_EQUAL",
        "threshold": 0.0,
        "allowed_sides": ("center", "right"),
    },
    "center_right_after_copy": {
        "operator": "GREATER_OR_EQUAL",
        "threshold": 0.0,
        "allowed_sides": ("center", "right"),
    },
}

BRANCH_DENSITY_PRUNING_PROFILES = {
    "leaf_mud_only": {
        "noise_min": BRANCH_DENSITY_NOISE_MIN,
        "noise_max": BRANCH_DENSITY_NOISE_MAX,
        "threshold": BRANCH_DENSITY_FILTER_THRESHOLD,
        "density_overrides": {},
    },
    "right_upper_subtree": {
        "noise_min": BRANCH_DENSITY_NOISE_MIN,
        "noise_max": BRANCH_DENSITY_NOISE_MAX,
        "threshold": BRANCH_DENSITY_FILTER_THRESHOLD,
        "density_overrides": {
            "CenterMudPatch": 0.78,
            "RightUpperEdge": 0.68,
            "RightRockCap": 0.68,
        },
    },
}


def source_point(name, coord, actor, parent, depth, side="center", role="bank", density=None):
    return {
        "name": name,
        "coord": coord,
        "actor": actor,
        "parent": parent,
        "depth": depth,
        "side": side,
        "role": role,
        "density": DENSITY_BY_ROLE[role] if density is None else float(density),
    }


def side_mode_allows(side):
    if SIDE_MODE == "both":
        return True
    if SIDE_MODE not in {"left", "right"}:
        raise RuntimeError("SIDE_MODE must be 'both', 'left', or 'right'")
    return side in {"center", SIDE_MODE}


def side_mask_value(side):
    try:
        return SIDE_MASK_BY_SIDE[side]
    except KeyError:
        raise RuntimeError(f"Unknown side={side!r}; known sides: {sorted(SIDE_MASK_BY_SIDE)}")


def active_side_mask_filter_profile():
    return SIDE_MASK_FILTER_PROFILE_OVERRIDE or SIDE_MASK_FILTER_PROFILE


def side_filter_profile_spec():
    profile = active_side_mask_filter_profile()
    try:
        return SIDE_MASK_FILTER_PROFILES[profile]
    except KeyError:
        known = ", ".join(sorted(SIDE_MASK_FILTER_PROFILES))
        raise RuntimeError(f"Unknown SIDE_MASK_FILTER_PROFILE={profile!r}; known profiles: {known}")


def graph_side_filter_allows(spec):
    return spec["side"] in side_filter_profile_spec()["allowed_sides"]


def active_branch_density_pruning_profile():
    return BRANCH_DENSITY_PRUNING_PROFILE_OVERRIDE or BRANCH_DENSITY_PRUNING_PROFILE


def branch_density_pruning_profile_spec():
    profile = active_branch_density_pruning_profile()
    try:
        return BRANCH_DENSITY_PRUNING_PROFILES[profile]
    except KeyError:
        known = ", ".join(sorted(BRANCH_DENSITY_PRUNING_PROFILES))
        raise RuntimeError(f"Unknown BRANCH_DENSITY_PRUNING_PROFILE={profile!r}; known profiles: {known}")


def branch_density_noise_min():
    return float(branch_density_pruning_profile_spec()["noise_min"])


def branch_density_noise_max():
    return float(branch_density_pruning_profile_spec()["noise_max"])


def branch_density_filter_threshold():
    return float(branch_density_pruning_profile_spec()["threshold"])


def branch_density_value(spec):
    overrides = branch_density_pruning_profile_spec()["density_overrides"]
    return float(overrides.get(spec["name"], spec.get("density", 1.0)))


def apply_branch_jitter(coord, actor, side):
    if actor == 0 or BRANCH_JITTER == 0:
        return coord
    x, y, z = coord
    lateral_sign = -1.0 if side == "left" else 1.0 if side == "right" else 0.0
    lateral_noise = (((actor * 37) % 13) - 6) / 6.0
    forward_noise = (((actor * 19) % 9) - 4) / 4.0
    x += lateral_sign * abs(lateral_noise) * BRANCH_JITTER
    y += forward_noise * BRANCH_JITTER * 0.5
    return (x, y, z)


def finalize_source_assembly(raw_points, apply_side_filter=False):
    filtered = []
    for spec in raw_points:
        if not apply_side_filter or side_mode_allows(spec["side"]):
            filtered.append(dict(spec))

    old_to_new = {spec["actor"]: idx for idx, spec in enumerate(filtered)}
    finalized = []
    for idx, spec in enumerate(filtered):
        parent = spec["parent"]
        if parent >= 0 and parent not in old_to_new:
            raise RuntimeError(f"Parent {parent} for {spec['name']} was filtered out")
        coord = apply_branch_jitter(spec["coord"], spec["actor"], spec["side"])
        finalized.append({
            **spec,
            "coord": coord,
            "actor": idx,
            "parent": -1 if parent < 0 else old_to_new[parent],
        })
    return finalized


def build_learning_tree_source_assembly():
    return finalize_source_assembly([
        source_point("Root", (0, 0, 0), 0, -1, 0, role="root"),
        source_point("LeftChild", (-120, 0, 0), 1, 0, 1, side="left"),
        source_point("CenterChild", (0, 90, 0), 2, 0, 1, side="center"),
        source_point("RightChild", (120, 0, 0), 3, 0, 1, side="right"),
        source_point("LeftGrandchild", (-190, 70, 0), 4, 1, 2, side="left"),
        source_point("CenterGrandchild", (0, 180, 0), 5, 2, 2, side="center"),
        source_point("RightGrandchild", (190, 70, 0), 6, 3, 2, side="right"),
    ])


def build_ditch_riverbank_source_assembly():
    half_width = RIVERBANK_HALF_WIDTH * WIDTH_VARIANT
    forward = RIVERBANK_FORWARD_STEP
    height = RIVERBANK_HEIGHT_STEP * HEIGHT_VARIANT
    rock = RIVERBANK_ROCK_OFFSET
    return finalize_source_assembly([
        source_point("RiverBankRoot", (0, 0, 0), 0, -1, 0, role="root"),
        source_point("LeftBank", (-half_width * 0.45, 0, height * 0.15), 1, 0, 1, side="left", role="bank"),
        source_point("CenterSilt", (0, forward * 0.45, height * 0.05), 2, 0, 1, side="center", role="silt"),
        source_point("RightBank", (half_width * 0.45, 0, height * 0.15), 3, 0, 1, side="right", role="bank"),
        source_point("LeftLowerEdge", (-half_width * 0.75, forward * 0.65, height * 0.3), 4, 1, 2, side="left", role="lower_edge"),
        source_point("LeftUpperEdge", (-half_width, forward * 1.45, height * 1.2), 5, 1, 2, side="left", role="upper_edge"),
        source_point("CenterMudPatch", (0, forward * 1.25, height * 0.4), 6, 2, 2, side="center", role="mud"),
        source_point("CenterGrassPatch", (0, forward * 2.1, height * 0.9), 7, 2, 2, side="center", role="grass"),
        source_point("RightLowerEdge", (half_width * 0.75, forward * 0.65, height * 0.3), 8, 3, 2, side="right", role="lower_edge"),
        source_point("RightUpperEdge", (half_width, forward * 1.45, height * 1.2), 9, 3, 2, side="right", role="upper_edge"),
        source_point("LeftRockCap", (-half_width - rock, forward * 2.2, height * 1.5), 10, 5, 3, side="left", role="rock"),
        source_point("RightRockCap", (half_width + rock, forward * 2.2, height * 1.5), 11, 9, 3, side="right", role="rock"),
    ], apply_side_filter=True)


SOURCE_ASSEMBLY_PRESETS = {
    "learning_tree": build_learning_tree_source_assembly,
    "ditch_riverbank": build_ditch_riverbank_source_assembly,
}


def get_source_assembly():
    try:
        return SOURCE_ASSEMBLY_PRESETS[SOURCE_ASSEMBLY_PRESET]()
    except KeyError:
        known = ", ".join(sorted(SOURCE_ASSEMBLY_PRESETS))
        raise RuntimeError(f"Unknown SOURCE_ASSEMBLY_PRESET={SOURCE_ASSEMBLY_PRESET!r}; known presets: {known}")


def selector_import(settings, prop, text):
    selector = settings.get_editor_property(prop)
    selector.import_text(f"PCGBegin({text})PCGEnd")
    settings.set_editor_property(prop, selector)


def set_const_value_struct(value_struct, value_type, value):
    value_struct.set_editor_property("type", value_type)
    if value_type == unreal.PCGMetadataTypes.INTEGER32:
        value_struct.set_editor_property("int32_value", int(value))
        value_struct.set_editor_property("int_value", int(value))
    elif value_type == unreal.PCGMetadataTypes.INTEGER64:
        value_struct.set_editor_property("int_value", int(value))
        value_struct.set_editor_property("int32_value", int(value))
    elif value_type == unreal.PCGMetadataTypes.BOOLEAN:
        value_struct.set_editor_property("bool_value", bool(value))
    elif value_type == unreal.PCGMetadataTypes.TRANSFORM:
        value_struct.set_editor_property("transform_value", value or unreal.Transform())
    else:
        value_struct.set_editor_property("double_value", float(value))
        value_struct.set_editor_property("float_value", float(value))
    return value_struct


def add_node(graph, settings_cls, title, x, y):
    created = graph.add_node_of_type(settings_cls.static_class())
    node = created[0] if isinstance(created, tuple) else created
    node.set_editor_property("node_title", title)
    try:
        node.set_node_position(unreal.Vector2D(x, y))
    except Exception:
        pass
    return node


def configure_points(node, coords, density=1.0):
    settings = node.get_settings()
    points = settings.get_editor_property("points_to_create")
    points.clear()
    for idx, coord in enumerate(coords):
        point = unreal.PCGPoint()
        transform = point.get_editor_property("transform")
        transform.set_editor_property(
            "translation",
            unreal.Vector(float(coord[0]), float(coord[1]), float(coord[2])),
        )
        point.set_editor_property("transform", transform)
        point.set_editor_property("density", float(density))
        point.set_editor_property("steepness", 1.0)
        point.set_editor_property("seed", idx)
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


def configure_copy_points(node):
    settings = node.get_settings()
    settings.set_editor_property("rotation_inheritance", unreal.PCGCopyPointsInheritanceMode.RELATIVE)
    settings.set_editor_property("scale_inheritance", unreal.PCGCopyPointsInheritanceMode.RELATIVE)
    settings.set_editor_property("color_inheritance", unreal.PCGCopyPointsInheritanceMode.RELATIVE)
    settings.set_editor_property("seed_inheritance", unreal.PCGCopyPointsInheritanceMode.RELATIVE)
    settings.set_editor_property("attribute_inheritance", unreal.PCGCopyPointsMetadataInheritanceMode.SOURCE_ONLY)
    settings.set_editor_property("tag_inheritance", unreal.PCGCopyPointsTagInheritanceMode.BOTH)
    settings.set_editor_property("copy_each_source_on_every_target", True)


def configure_attribute_noise(node, input_attr, output_attr, noise_min, noise_max):
    settings = node.get_settings()
    settings.set_editor_property("mode", unreal.PCGAttributeNoiseMode.MULTIPLY)
    settings.set_editor_property("noise_min", float(noise_min))
    settings.set_editor_property("noise_max", float(noise_max))
    selector_import(settings, "input_source", input_attr)
    selector_import(settings, "output_target", output_attr)


def filter_operator_enum(operator_name):
    try:
        return getattr(unreal.PCGAttributeFilterOperator, operator_name)
    except AttributeError:
        raise RuntimeError(f"Unknown PCGAttributeFilterOperator={operator_name!r}")


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


def configure_density_filter_smoke(node):
    settings = node.get_settings()
    settings.set_editor_property("lower_bound", float(GROUND_STYLE_DENSITY_FILTER_LOWER))
    settings.set_editor_property("upper_bound", float(GROUND_STYLE_DENSITY_FILTER_UPPER))
    settings.set_editor_property("invert_filter", False)
    settings.set_editor_property("keep_zero_density_points", False)


def configure_self_pruning_smoke(node):
    settings = node.get_settings()
    params = settings.get_editor_property("parameters")
    params.set_editor_property("randomized_pruning", bool(GROUND_STYLE_SELF_PRUNING_RANDOMIZED))
    params.set_editor_property("radius_similarity_factor", float(GROUND_STYLE_SELF_PRUNING_RADIUS_SIMILARITY))
    try:
        params.set_editor_property("pruning_type", unreal.PCGSelfPruningType.LARGE_TO_SMALL)
    except Exception:
        pass
    settings.set_editor_property("parameters", params)


def configure_side_mask_filter(node):
    spec = side_filter_profile_spec()
    configure_attribute_filter_constant(
        node,
        "SideMask",
        float(spec["threshold"]),
        str(spec["operator"]),
    )


def configure_spline_sampler(node):
    settings = node.get_settings()
    params = settings.get_editor_property("sampler_params")
    params.set_editor_property("dimension", unreal.PCGSplineSamplingDimension.ON_SPLINE)
    params.set_editor_property("mode", unreal.PCGSplineSamplingMode.NUMBER_OF_SAMPLES)
    params.set_editor_property("fill", unreal.PCGSplineSamplingFill.FILL)
    params.set_editor_property("num_samples", int(TARGET_SAMPLE_COUNT))
    params.set_editor_property("distance_increment", float(TARGET_POINT_SPACING))
    params.set_editor_property("interior_sample_spacing", float(TARGET_POINT_SPACING))
    params.set_editor_property("interior_border_sample_spacing", float(TARGET_POINT_SPACING))
    params.set_editor_property("subdivisions_per_segment", max(1, int(TARGET_SAMPLE_COUNT) - 1))
    params.set_editor_property("treat_spline_as_polyline", False)
    settings.set_editor_property("sampler_params", params)


def configure_blueprint_node(node):
    settings = node.get_settings()
    bp_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not bp_class:
        raise RuntimeError(f"Failed to load {BLUEPRINT_CLASS_PATH}")
    settings.set_editor_property("blueprint_element_type", bp_class)


def try_selector_property(settings, prop, selector_text):
    try:
        selector_import(settings, prop, selector_text)
    except Exception:
        pass


def configure_apply_hierarchy(node):
    settings = node.get_settings()
    settings.set_editor_property("apply_hierarchy", unreal.PCGApplyHierarchyOption.ALWAYS)
    settings.set_editor_property("apply_parent_rotation", unreal.PCGApplyHierarchyOption.OPT_OUT_BY_ATTRIBUTE)
    settings.set_editor_property("apply_parent_scale", unreal.PCGApplyHierarchyOption.OPT_OUT_BY_ATTRIBUTE)
    try_selector_property(settings, "point_attribute", "ActorIndex")
    try_selector_property(settings, "parent_attribute", "ParentIndex")
    try_selector_property(settings, "hierarchy_depth_attribute", "HierarchyDepth")
    try_selector_property(settings, "relative_transform_attribute", "RelativeTransform")
    try_selector_property(settings, "apply_parent_rotation_attribute", "IgnoreParentRotation")
    try_selector_property(settings, "apply_parent_scale_attribute", "IgnoreParentScale")


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


def build_source_branch(graph, spec, label, y):
    point_node = add_node(graph, unreal.PCGCreatePointsSettings, f"02{label} Source {spec['name']}", -2020, y)
    actor_node = add_node(graph, unreal.PCGAddAttributeSettings, f"03{label} {spec['name']} ActorIndex", -1740, y)
    parent_node = add_node(graph, unreal.PCGAddAttributeSettings, f"04{label} {spec['name']} ParentIndex", -1480, y)
    depth_node = add_node(graph, unreal.PCGAddAttributeSettings, f"05{label} {spec['name']} HierarchyDepth", -1220, y)
    relative_node = add_node(graph, unreal.PCGAddAttributeSettings, f"06{label} {spec['name']} RelativeTransform", -960, y)
    density_node = add_node(graph, unreal.PCGAddAttributeSettings, f"07{label} {spec['name']} BranchDensity", -700, y)
    side_node = add_node(graph, unreal.PCGAddAttributeSettings, f"08{label} {spec['name']} SideMask", -440, y)

    configure_points(point_node, [spec["coord"]], branch_density_value(spec))
    configure_add(actor_node, "ActorIndex", "@Last", unreal.PCGMetadataTypes.INTEGER64, spec["actor"])
    configure_add(parent_node, "ParentIndex", "@Last", unreal.PCGMetadataTypes.INTEGER64, spec["parent"])
    configure_add(depth_node, "HierarchyDepth", "@Last", unreal.PCGMetadataTypes.INTEGER32, spec["depth"])
    configure_add(relative_node, "RelativeTransform", "$Transform", unreal.PCGMetadataTypes.TRANSFORM, unreal.Transform())
    configure_add(density_node, "BranchDensity", "@Last", unreal.PCGMetadataTypes.DOUBLE, branch_density_value(spec))
    configure_add(side_node, "SideMask", "@Last", unreal.PCGMetadataTypes.DOUBLE, side_mask_value(spec["side"]))

    graph.add_edge(point_node, "Out", actor_node, "In")
    graph.add_edge(actor_node, "Out", parent_node, "In")
    graph.add_edge(parent_node, "Out", depth_node, "In")
    graph.add_edge(depth_node, "Out", relative_node, "In")
    graph.add_edge(relative_node, "Out", density_node, "In")
    graph.add_edge(density_node, "Out", side_node, "In")
    return side_node


def build_graph():
    graph = unreal.EditorAssetLibrary.load_asset(GRAPH_PATH)
    if not graph:
        raise RuntimeError(f"Failed to load graph: {GRAPH_PATH}")

    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)

    get_spline = add_node(graph, unreal.PCGGetSplineSettings, "00 Get Owning Actor Spline", -1820, 360)
    spline_sampler = add_node(graph, unreal.PCGSplineSamplerSettings, "01 Spline Target Sampler", -1540, 360)
    source_assembly = get_source_assembly()
    source_outputs = []
    for idx, spec in enumerate(source_assembly):
        label = chr(ord("A") + idx)
        source_outputs.append(build_source_branch(graph, spec, label, -820 + idx * 210))

    source_merge = add_node(graph, unreal.PCGMergeSettings, "09 Merge Source Local Hierarchy", -640, -190)
    copy = add_node(graph, unreal.PCGCopyPointsSettings, "10 Copy Source Onto Spline Targets", -340, 40)
    post_copy = add_node(graph, unreal.PCGBlueprintSettings, "11 Original PostCopyPoints Offset Blueprint", -40, 40)
    side_filter = add_node(
        graph,
        unreal.PCGAttributeFilteringSettings,
        f"12 Filter SideMask {active_side_mask_filter_profile()}",
        260,
        40,
    )
    side_pass = add_node(graph, unreal.PCGAddAttributeSettings, "13 SideMaskFilterPass True", 560, 40)
    density_noise = add_node(graph, unreal.PCGAttributeNoiseSettings, "14 Consume BranchDensity With Noise", 860, 40)
    density_filter = add_node(graph, unreal.PCGAttributeFilteringSettings, "15 Filter BranchDensityNoised >= Threshold", 1160, 40)
    filter_pass = add_node(graph, unreal.PCGAddAttributeSettings, "16 BranchDensityFilterPass True", 1460, 40)
    ground_density_filter = add_node(graph, unreal.PCGDensityFilterSettings, "17 GroundStyle DensityFilter Smoke", 1760, 40)
    ground_self_pruning = add_node(graph, unreal.PCGSelfPruningSettings, "18 GroundStyle SelfPruning Smoke", 2040, 40)
    ground_pass = add_node(graph, unreal.PCGAddAttributeSettings, "19 GroundStyleSmokePass True", 2320, 40)
    ignore_rot = add_node(graph, unreal.PCGAddAttributeSettings, "20 IgnoreParentRotation False", 2620, 40)
    ignore_scale = add_node(graph, unreal.PCGAddAttributeSettings, "21 IgnoreParentScale False", 2900, 40)
    apply = add_node(graph, unreal.PCGApplyHierarchySettings, "22 Apply Offset Hierarchy", 3180, 40)
    spawner = add_node(graph, unreal.PCGStaticMeshSpawnerSettings, "23 Spawn Cubeless Grass Mesh", 3460, 40)

    configure_spline_sampler(spline_sampler)
    configure_copy_points(copy)
    configure_blueprint_node(post_copy)
    configure_side_mask_filter(side_filter)
    configure_add(side_pass, "SideMaskFilterPass", "@Last", unreal.PCGMetadataTypes.BOOLEAN, True)
    configure_attribute_noise(
        density_noise,
        "BranchDensity",
        "BranchDensityNoised",
        branch_density_noise_min(),
        branch_density_noise_max(),
    )
    configure_attribute_filter_constant(density_filter, "BranchDensityNoised", branch_density_filter_threshold())
    configure_add(filter_pass, "BranchDensityFilterPass", "@Last", unreal.PCGMetadataTypes.BOOLEAN, True)
    configure_density_filter_smoke(ground_density_filter)
    configure_self_pruning_smoke(ground_self_pruning)
    configure_add(ground_pass, "GroundStyleSmokePass", "@Last", unreal.PCGMetadataTypes.BOOLEAN, True)
    configure_add(ignore_rot, "IgnoreParentRotation", "@Last", unreal.PCGMetadataTypes.BOOLEAN, False)
    configure_add(ignore_scale, "IgnoreParentScale", "@Last", unreal.PCGMetadataTypes.BOOLEAN, False)
    configure_apply_hierarchy(apply)
    configure_grass_spawner(spawner)

    graph.add_edge(get_spline, "Out", spline_sampler, "Spline")
    for source_output in source_outputs:
        graph.add_edge(source_output, "Out", source_merge, "In")
    graph.add_edge(source_merge, "Out", copy, "Source")
    graph.add_edge(spline_sampler, "Out", copy, "Target")
    graph.add_edge(copy, "Out", post_copy, "CopyPointsOut")
    graph.add_edge(spline_sampler, "Out", post_copy, "CopyPointsTarget")
    graph.add_edge(post_copy, "Out", side_filter, "In")
    graph.add_edge(side_filter, "InsideFilter", side_pass, "In")
    graph.add_edge(side_pass, "Out", density_noise, "In")
    graph.add_edge(density_noise, "Out", density_filter, "In")
    graph.add_edge(density_filter, "InsideFilter", filter_pass, "In")
    graph.add_edge(filter_pass, "Out", ground_density_filter, "In")
    graph.add_edge(ground_density_filter, "Out", ground_self_pruning, "In")
    graph.add_edge(ground_self_pruning, "Out", ground_pass, "In")
    graph.add_edge(ground_pass, "Out", ignore_rot, "In")
    graph.add_edge(ignore_rot, "Out", ignore_scale, "In")
    graph.add_edge(ignore_scale, "Out", apply, "In")
    graph.add_edge(apply, "Out", spawner, "In")
    graph.add_edge(spawner, "Out", graph.get_output_node(), "Out")

    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def regenerate_test_actor(graph):
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    actor = None
    for candidate in get_all_level_actors():
        if candidate.get_actor_label() == ACTOR_LABEL:
            actor = candidate
            break
    if not actor:
        raise RuntimeError(f"Missing test actor: {ACTOR_LABEL}")

    for spline in actor.get_components_by_class(unreal.SplineComponent):
        half_length = (float(TARGET_SAMPLE_COUNT) - 1.0) * float(TARGET_POINT_SPACING) * 0.5
        spline.clear_spline_points(False)
        spline.add_spline_point(unreal.Vector(0, -half_length, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, 0, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, half_length, 0), unreal.SplineCoordinateSpace.LOCAL, True)
        spline.update_spline()

    for component in actor.get_components_by_class(unreal.PCGComponent):
        component.set_graph(graph)
        component.cleanup(True)
        component.generate(True)
    return actor


def main():
    source_assembly = get_source_assembly()
    print("MCP_PCG_MAIN_LEARNING_SOURCE_BUILD_BEGIN")
    main_graph = build_graph()
    test_actor = regenerate_test_actor(main_graph)
    print(f"graph={main_graph.get_path_name()}")
    print(f"actor={test_actor.get_actor_label()}")
    print(f"source_assembly_preset={SOURCE_ASSEMBLY_PRESET}")
    print(f"source_point_count={len(source_assembly)}")
    print(f"target_sample_count={TARGET_SAMPLE_COUNT}")
    print(f"target_point_spacing={TARGET_POINT_SPACING}")
    print(f"side_mode={SIDE_MODE}")
    print(f"branch_jitter={BRANCH_JITTER}")
    print(f"width_variant={WIDTH_VARIANT}")
    print(f"height_variant={HEIGHT_VARIANT}")
    print(f"side_mask_filter_profile={active_side_mask_filter_profile()}")
    side_spec = side_filter_profile_spec()
    print(f"side_mask_filter_operator={side_spec['operator']}")
    print(f"side_mask_filter_threshold={side_spec['threshold']}")
    print(f"side_mask_filter_allowed_sides={list(side_spec['allowed_sides'])}")
    density_spec = branch_density_pruning_profile_spec()
    print(f"branch_density_pruning_profile={active_branch_density_pruning_profile()}")
    print(f"branch_density_noise_min={density_spec['noise_min']}")
    print(f"branch_density_noise_max={density_spec['noise_max']}")
    print(f"branch_density_filter_threshold={density_spec['threshold']}")
    print(f"branch_density_overrides={density_spec['density_overrides']}")
    print(f"ground_style_density_filter_enabled={GROUND_STYLE_DENSITY_FILTER_ENABLED}")
    print(f"ground_style_density_filter_lower={GROUND_STYLE_DENSITY_FILTER_LOWER}")
    print(f"ground_style_density_filter_upper={GROUND_STYLE_DENSITY_FILTER_UPPER}")
    print(f"ground_style_self_pruning_enabled={GROUND_STYLE_SELF_PRUNING_ENABLED}")
    print(f"ground_style_self_pruning_randomized={GROUND_STYLE_SELF_PRUNING_RANDOMIZED}")
    print(f"ground_style_self_pruning_radius_similarity={GROUND_STYLE_SELF_PRUNING_RADIUS_SIMILARITY}")
    print("MCP_PCG_MAIN_LEARNING_SOURCE_BUILD_END")


if __name__ == "__main__":
    main()
