import unreal


STYLE_AMOUNT_PACKAGE = "/Game/Cubeless/PCG/ElectricDreamsLearning/StyleAmountPresets"
STYLE_MATRIX_PACKAGE = "/Game/Cubeless/PCG/ElectricDreamsLearning/DesignerStyleProfileMatrixCombos"
AMOUNT_PRESET_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning/AmountPresets"
GROUND_CORE_GRAPH_PATH = (
    f"{AMOUNT_PRESET_PATH}/PCG_Cubeless_ED_GroundControlsCore.PCG_Cubeless_ED_GroundControlsCore"
)
DITCH_CORE_GRAPH_PATH = (
    f"{AMOUNT_PRESET_PATH}/PCG_Cubeless_ED_DitchHierarchyCore.PCG_Cubeless_ED_DitchHierarchyCore"
)
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
VALIDATION_BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/"
    "BP_Cubeless_ED_PCGDesignerControlActor.BP_Cubeless_ED_PCGDesignerControlActor_C"
)
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_StyleProfileMatrix"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0

PROFILE_MODE_GROUND_ONLY = 1
PROFILE_MODE_DITCH_ONLY = 2
PROFILE_MODE_BOTH = 3

STYLE_SPECS = [
    {
        "name": "ClassicGrass",
        "style_id": 401,
        "style_type": 1,
        "mesh_paths": [(
            "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Grass/"
            "SM_Grass_Medium01.SM_Grass_Medium01"
        )],
    },
    {
        "name": "TallGrass",
        "style_id": 402,
        "style_type": 2,
        "mesh_paths": [(
            "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Grass/"
            "SM_Grass_Medium03.SM_Grass_Medium03"
        )],
    },
    {
        "name": "MixedGrass",
        "style_id": 403,
        "style_type": 3,
        "mesh_paths": [
            (
                "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Grass/"
                "SM_Grass_Medium01.SM_Grass_Medium01"
            ),
            (
                "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Grass/"
                "SM_Grass_Medium03.SM_Grass_Medium03"
            ),
        ],
    },
    {
        "name": "GroundFoliage",
        "style_id": 404,
        "style_type": 4,
        "mesh_paths": [
            (
                "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Plants/"
                "SM_Fern_01.SM_Fern_01"
            ),
            (
                "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Plants/"
                "SM_GroundLeaf_01.SM_GroundLeaf_01"
            ),
            (
                "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Flowers/"
                "SM_FlowerGroup_01_White.SM_FlowerGroup_01_White"
            ),
            (
                "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Flowers/"
                "SM_FlowerGroup_01_Yellow.SM_FlowerGroup_01_Yellow"
            ),
        ],
    },
    {
        "name": "SmallRocks",
        "style_id": 405,
        "style_type": 5,
        "mesh_paths": [
            (
                "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Stones/Rocks/"
                "SM_SmallRock_01.SM_SmallRock_01"
            ),
            (
                "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Stones/Rocks/"
                "SM_SmallRock_02.SM_SmallRock_02"
            ),
        ],
    },
]

GROUND_AMOUNT_SPECS = [
    {
        "name": "GroundSparse",
        "short_name": "Sparse",
        "profile_id": 10,
        "profile_type": 1,
        "amount_id": 201,
        "amount_type": 1,
        "density_filter": (0.8, 1.0),
        "duplicate_iterations": 0,
        "duplicate_offset": unreal.Vector(42.0, 42.0, 0.0),
        "core_graph_path": GROUND_CORE_GRAPH_PATH,
        "expected_points": 3,
    },
    {
        "name": "GroundNormal",
        "short_name": "Normal",
        "profile_id": 10,
        "profile_type": 1,
        "amount_id": 202,
        "amount_type": 2,
        "density_filter": None,
        "duplicate_iterations": 0,
        "duplicate_offset": unreal.Vector(42.0, 42.0, 0.0),
        "core_graph_path": GROUND_CORE_GRAPH_PATH,
        "expected_points": 8,
    },
    {
        "name": "GroundDense",
        "short_name": "Dense",
        "profile_id": 10,
        "profile_type": 1,
        "amount_id": 203,
        "amount_type": 3,
        "density_filter": None,
        "duplicate_iterations": 1,
        "duplicate_offset": unreal.Vector(42.0, 42.0, 0.0),
        "core_graph_path": GROUND_CORE_GRAPH_PATH,
        "expected_points": 16,
    },
]

DITCH_AMOUNT_SPECS = [
    {
        "name": "DitchSparse",
        "short_name": "Sparse",
        "profile_id": 20,
        "profile_type": 2,
        "amount_id": 301,
        "amount_type": 1,
        "density_filter": (0.9, 1.0),
        "duplicate_iterations": 0,
        "duplicate_offset": unreal.Vector(55.0, 55.0, 0.0),
        "core_graph_path": DITCH_CORE_GRAPH_PATH,
        "expected_points": 18,
    },
    {
        "name": "DitchNormal",
        "short_name": "Normal",
        "profile_id": 20,
        "profile_type": 2,
        "amount_id": 302,
        "amount_type": 2,
        "density_filter": None,
        "duplicate_iterations": 0,
        "duplicate_offset": unreal.Vector(55.0, 55.0, 0.0),
        "core_graph_path": DITCH_CORE_GRAPH_PATH,
        "expected_points": 42,
    },
    {
        "name": "DitchDense",
        "short_name": "Dense",
        "profile_id": 20,
        "profile_type": 2,
        "amount_id": 303,
        "amount_type": 3,
        "density_filter": None,
        "duplicate_iterations": 1,
        "duplicate_offset": unreal.Vector(55.0, 55.0, 0.0),
        "core_graph_path": DITCH_CORE_GRAPH_PATH,
        "expected_points": 84,
    },
]


def style_amount_asset_name(profile_key, amount, style):
    return f"PCG_Cubeless_ED_{profile_key}Amount_{amount['short_name']}_{style['name']}"


def style_amount_graph_path(profile_key, amount, style):
    asset_name = style_amount_asset_name(profile_key, amount, style)
    return f"{STYLE_AMOUNT_PACKAGE}/{asset_name}.{asset_name}"


STYLE_AMOUNT_GRAPH_PATHS = {}
for style in STYLE_SPECS:
    for amount in GROUND_AMOUNT_SPECS:
        STYLE_AMOUNT_GRAPH_PATHS[("Ground", style["style_type"], amount["amount_type"])] = (
            style_amount_graph_path("Ground", amount, style)
        )
    for amount in DITCH_AMOUNT_SPECS:
        STYLE_AMOUNT_GRAPH_PATHS[("Ditch", style["style_type"], amount["amount_type"])] = (
            style_amount_graph_path("Ditch", amount, style)
        )


def profile_matrix_type(profile_mode, ground_type, ditch_type):
    return int(profile_mode) * 100 + int(ground_type) * 10 + int(ditch_type)


def profile_matrix_id(profile_mode, ground_type, ditch_type):
    return 1000 + profile_matrix_type(profile_mode, ground_type, ditch_type)


def style_profile_matrix_type(style_type, profile_mode, ground_type, ditch_type):
    return int(style_type) * 1000 + profile_matrix_type(profile_mode, ground_type, ditch_type)


def style_profile_matrix_id(style_type, profile_mode, ground_type, ditch_type):
    return 20000 + style_profile_matrix_type(style_type, profile_mode, ground_type, ditch_type)


def make_ground_only_spec(style, ground):
    profile_mode = PROFILE_MODE_GROUND_ONLY
    ground_type = ground["amount_type"]
    ditch_type = 0
    matrix_type = profile_matrix_type(profile_mode, ground_type, ditch_type)
    style_matrix_type = style_profile_matrix_type(style["style_type"], profile_mode, ground_type, ditch_type)
    return {
        "name": f"{style['name']}_GroundOnly_{ground['name']}",
        "asset_name": f"PCG_Cubeless_ED_StyleProfileMatrix_{style['name']}_GroundOnly_{ground['name']}",
        "style_id": style["style_id"],
        "style_type": style["style_type"],
        "mesh_paths": style["mesh_paths"],
        "profile_mode": profile_mode,
        "ground_amount_type": ground_type,
        "ditch_amount_type": ditch_type,
        "profile_matrix_type": matrix_type,
        "profile_matrix_id": profile_matrix_id(profile_mode, ground_type, ditch_type),
        "style_profile_matrix_type": style_matrix_type,
        "style_profile_matrix_id": style_profile_matrix_id(
            style["style_type"], profile_mode, ground_type, ditch_type
        ),
        "subgraph_paths": [STYLE_AMOUNT_GRAPH_PATHS[("Ground", style["style_type"], ground_type)]],
        "expected_points": ground["expected_points"],
        "expected_ism": ground["expected_points"],
        "expected_profile_counts": {ground["profile_id"]: ground["expected_points"]},
        "expected_amount_counts": {ground["amount_id"]: ground["expected_points"]},
    }


def make_ditch_only_spec(style, ditch):
    profile_mode = PROFILE_MODE_DITCH_ONLY
    ground_type = 0
    ditch_type = ditch["amount_type"]
    matrix_type = profile_matrix_type(profile_mode, ground_type, ditch_type)
    style_matrix_type = style_profile_matrix_type(style["style_type"], profile_mode, ground_type, ditch_type)
    return {
        "name": f"{style['name']}_DitchOnly_{ditch['name']}",
        "asset_name": f"PCG_Cubeless_ED_StyleProfileMatrix_{style['name']}_DitchOnly_{ditch['name']}",
        "style_id": style["style_id"],
        "style_type": style["style_type"],
        "mesh_paths": style["mesh_paths"],
        "profile_mode": profile_mode,
        "ground_amount_type": ground_type,
        "ditch_amount_type": ditch_type,
        "profile_matrix_type": matrix_type,
        "profile_matrix_id": profile_matrix_id(profile_mode, ground_type, ditch_type),
        "style_profile_matrix_type": style_matrix_type,
        "style_profile_matrix_id": style_profile_matrix_id(
            style["style_type"], profile_mode, ground_type, ditch_type
        ),
        "subgraph_paths": [STYLE_AMOUNT_GRAPH_PATHS[("Ditch", style["style_type"], ditch_type)]],
        "expected_points": ditch["expected_points"],
        "expected_ism": ditch["expected_points"],
        "expected_profile_counts": {ditch["profile_id"]: ditch["expected_points"]},
        "expected_amount_counts": {ditch["amount_id"]: ditch["expected_points"]},
    }


def make_both_spec(style, ground, ditch):
    profile_mode = PROFILE_MODE_BOTH
    ground_type = ground["amount_type"]
    ditch_type = ditch["amount_type"]
    matrix_type = profile_matrix_type(profile_mode, ground_type, ditch_type)
    style_matrix_type = style_profile_matrix_type(style["style_type"], profile_mode, ground_type, ditch_type)
    expected_points = ground["expected_points"] + ditch["expected_points"]
    return {
        "name": f"{style['name']}_Both_{ground['name']}_{ditch['name']}",
        "asset_name": (
            f"PCG_Cubeless_ED_StyleProfileMatrix_{style['name']}_Both_{ground['name']}_{ditch['name']}"
        ),
        "style_id": style["style_id"],
        "style_type": style["style_type"],
        "mesh_paths": style["mesh_paths"],
        "profile_mode": profile_mode,
        "ground_amount_type": ground_type,
        "ditch_amount_type": ditch_type,
        "profile_matrix_type": matrix_type,
        "profile_matrix_id": profile_matrix_id(profile_mode, ground_type, ditch_type),
        "style_profile_matrix_type": style_matrix_type,
        "style_profile_matrix_id": style_profile_matrix_id(
            style["style_type"], profile_mode, ground_type, ditch_type
        ),
        "subgraph_paths": [
            STYLE_AMOUNT_GRAPH_PATHS[("Ground", style["style_type"], ground_type)],
            STYLE_AMOUNT_GRAPH_PATHS[("Ditch", style["style_type"], ditch_type)],
        ],
        "expected_points": expected_points,
        "expected_ism": expected_points,
        "expected_profile_counts": {
            ground["profile_id"]: ground["expected_points"],
            ditch["profile_id"]: ditch["expected_points"],
        },
        "expected_amount_counts": {
            ground["amount_id"]: ground["expected_points"],
            ditch["amount_id"]: ditch["expected_points"],
        },
    }


STYLE_PROFILE_MATRIX_SPECS = []
for style_spec in STYLE_SPECS:
    STYLE_PROFILE_MATRIX_SPECS.extend(
        make_ground_only_spec(style_spec, ground) for ground in GROUND_AMOUNT_SPECS
    )
    STYLE_PROFILE_MATRIX_SPECS.extend(
        make_ditch_only_spec(style_spec, ditch) for ditch in DITCH_AMOUNT_SPECS
    )
    STYLE_PROFILE_MATRIX_SPECS.extend(
        make_both_spec(style_spec, ground, ditch)
        for ground in GROUND_AMOUNT_SPECS
        for ditch in DITCH_AMOUNT_SPECS
    )

STYLE_PROFILE_MATRIX_GRAPH_PATHS = {
    spec["name"]: f"{STYLE_MATRIX_PACKAGE}/{spec['asset_name']}.{spec['asset_name']}"
    for spec in STYLE_PROFILE_MATRIX_SPECS
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


def configure_duplicate(node, iterations, offset):
    settings = node.get_settings()
    settings.set_editor_property("iterations", int(iterations))
    settings.set_editor_property("output_source_point", True)
    transform = settings.get_editor_property("point_transform")
    transform.set_editor_property("translation", offset)
    settings.set_editor_property("point_transform", transform)


def configure_style_spawner(node, style):
    settings = node.get_settings()
    entries = []
    for mesh_path in style["mesh_paths"]:
        mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        if not mesh:
            raise RuntimeError(f"Missing visual style mesh: {mesh_path}")
        descriptor = unreal.PCGSoftISMComponentDescriptor()
        descriptor.set_editor_property("static_mesh", mesh)
        entry = unreal.PCGMeshSelectorWeightedEntry()
        entry.set_editor_property("descriptor", descriptor)
        entry.set_editor_property("weight", 1)
        entries.append(entry)
    params = settings.get_editor_property("mesh_selector_parameters")
    params.set_editor_property("mesh_entries", entries)


def ensure_graph(package_path, asset_name):
    graph_path = f"{package_path}/{asset_name}.{asset_name}"
    unreal.EditorAssetLibrary.make_directory(package_path)
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            asset_name,
            package_path,
            unreal.PCGGraph.static_class(),
            unreal.PCGGraphFactory(),
        )
    if not graph:
        raise RuntimeError(f"Failed to create/load graph: {graph_path}")
    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)
    return graph


def add_profile_amount_style_markers(graph, upstream, amount, style, x, y):
    marker_specs = [
        ("DesignerProfileId", unreal.PCGMetadataTypes.INTEGER32, amount["profile_id"]),
        ("DesignerProfileType", unreal.PCGMetadataTypes.INTEGER32, amount["profile_type"]),
        ("DesignerAmountId", unreal.PCGMetadataTypes.INTEGER32, amount["amount_id"]),
        ("DesignerAmountType", unreal.PCGMetadataTypes.INTEGER32, amount["amount_type"]),
        ("DesignerAmountPass", unreal.PCGMetadataTypes.BOOLEAN, True),
        ("DesignerVisualStyleId", unreal.PCGMetadataTypes.INTEGER32, style["style_id"]),
        ("DesignerVisualStyleType", unreal.PCGMetadataTypes.INTEGER32, style["style_type"]),
        ("DesignerVisualStylePass", unreal.PCGMetadataTypes.BOOLEAN, True),
    ]
    current = upstream
    for index, (attr_name, attr_type, value) in enumerate(marker_specs):
        node = add_node(graph, unreal.PCGAddAttributeSettings, f"{attr_name} {value}", x + index * 280, y)
        configure_add(node, attr_name, "@Last", attr_type, value)
        graph.add_edge(current, "Out", node, "In")
        current = node
    return current


def build_style_amount_graph(profile_key, amount, style):
    asset_name = style_amount_asset_name(profile_key, amount, style)
    graph = ensure_graph(STYLE_AMOUNT_PACKAGE, asset_name)

    source = add_node(graph, unreal.PCGSubgraphSettings, f"{amount['name']} Core", -1700, 0)
    configure_subgraph(source, amount["core_graph_path"])
    graph.add_edge(graph.get_input_node(), "In", source, "In")
    upstream = source
    x = -1320

    if amount["density_filter"]:
        lower, upper = amount["density_filter"]
        density_filter = add_node(graph, unreal.PCGDensityFilterSettings, f"Density {lower}-{upper}", x, 0)
        configure_density_filter(density_filter, lower, upper)
        graph.add_edge(upstream, "Out", density_filter, "In")
        upstream = density_filter
        x += 320

    if amount["duplicate_iterations"] > 0:
        duplicate = add_node(graph, unreal.PCGDuplicatePointSettings, f"Duplicate x{amount['duplicate_iterations']}", x, 0)
        configure_duplicate(duplicate, amount["duplicate_iterations"], amount["duplicate_offset"])
        graph.add_edge(upstream, "Out", duplicate, "In")
        upstream = duplicate
        x += 320

    markers = add_profile_amount_style_markers(graph, upstream, amount, style, x, 0)
    spawner = add_node(graph, unreal.PCGStaticMeshSpawnerSettings, f"Spawn {style['name']}", x + 2520, 0)
    configure_style_spawner(spawner, style)
    graph.add_edge(markers, "Out", spawner, "In")
    graph.add_edge(spawner, "Out", graph.get_output_node(), "Out")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def add_style_profile_matrix_markers(graph, upstream, spec, x, y):
    marker_specs = [
        ("DesignerProfileMode", unreal.PCGMetadataTypes.INTEGER32, spec["profile_mode"]),
        ("DesignerGroundAmountType", unreal.PCGMetadataTypes.INTEGER32, spec["ground_amount_type"]),
        ("DesignerDitchAmountType", unreal.PCGMetadataTypes.INTEGER32, spec["ditch_amount_type"]),
        ("DesignerProfileMatrixId", unreal.PCGMetadataTypes.INTEGER32, spec["profile_matrix_id"]),
        ("DesignerProfileMatrixType", unreal.PCGMetadataTypes.INTEGER32, spec["profile_matrix_type"]),
        ("DesignerProfileMatrixPass", unreal.PCGMetadataTypes.BOOLEAN, True),
        ("DesignerStyleProfileMatrixId", unreal.PCGMetadataTypes.INTEGER32, spec["style_profile_matrix_id"]),
        ("DesignerStyleProfileMatrixType", unreal.PCGMetadataTypes.INTEGER32, spec["style_profile_matrix_type"]),
        ("DesignerStyleProfileMatrixPass", unreal.PCGMetadataTypes.BOOLEAN, True),
    ]
    current = upstream
    for index, (attr_name, attr_type, value) in enumerate(marker_specs):
        node = add_node(graph, unreal.PCGAddAttributeSettings, f"{attr_name} {value}", x + index * 280, y)
        configure_add(node, attr_name, "@Last", attr_type, value)
        graph.add_edge(current, "Out", node, "In")
        current = node
    return current


def build_style_profile_matrix_graph(spec):
    graph = ensure_graph(STYLE_MATRIX_PACKAGE, spec["asset_name"])
    source_nodes = []
    for index, subgraph_path in enumerate(spec["subgraph_paths"]):
        source = add_node(
            graph,
            unreal.PCGSubgraphSettings,
            f"{spec['name']} Source {index + 1}",
            -1200,
            index * 260,
        )
        configure_subgraph(source, subgraph_path)
        graph.add_edge(graph.get_input_node(), "In", source, "In")
        source_nodes.append(source)

    if len(source_nodes) == 1:
        upstream = source_nodes[0]
    else:
        merge = add_node(graph, unreal.PCGMergeSettings, f"{spec['name']} Merge", -820, 120)
        for source in source_nodes:
            graph.add_edge(source, "Out", merge, "In")
        upstream = merge

    markers = add_style_profile_matrix_markers(graph, upstream, spec, -460, 0)
    graph.add_edge(markers, "Out", graph.get_output_node(), "Out")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


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


def spawn_validation_actor(spec, graph, index):
    label = f"{ACTOR_LABEL_PREFIX}_{spec['name']}_Validation"
    for actor in get_all_level_actors():
        if actor.get_actor_label() == label:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    actor_class = unreal.load_class(None, VALIDATION_BLUEPRINT_CLASS_PATH)
    if not actor_class:
        raise RuntimeError(f"Missing validation actor class: {VALIDATION_BLUEPRINT_CLASS_PATH}")

    row = index // 10
    column = index % 10
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(24600 + column * 520, row * 520, 0),
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
    print("MCP_CUBELESS_ED_STYLE_PROFILE_MATRIX_PRESETS_BUILD_BEGIN")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for core_path in (GROUND_CORE_GRAPH_PATH, DITCH_CORE_GRAPH_PATH):
        if not unreal.EditorAssetLibrary.load_asset(core_path):
            raise RuntimeError(f"Missing required core graph: {core_path}")

    built_amount_paths = []
    for style in STYLE_SPECS:
        for amount in GROUND_AMOUNT_SPECS:
            built_amount_paths.append(build_style_amount_graph("Ground", amount, style).get_path_name())
        for amount in DITCH_AMOUNT_SPECS:
            built_amount_paths.append(build_style_amount_graph("Ditch", amount, style).get_path_name())

    print(f"style_amount_graph_count={len(built_amount_paths)}")
    for path in built_amount_paths:
        print(f"style_amount_graph={path}")

    for index, spec in enumerate(STYLE_PROFILE_MATRIX_SPECS):
        graph = build_style_profile_matrix_graph(spec)
        actor = spawn_validation_actor(spec, graph, index)
        print(f"style_profile_matrix={spec['name']}")
        print(f"style_profile_matrix_graph={graph.get_path_name()}")
        print(f"validation_actor={actor.get_actor_label()}")
        print(f"style_type={spec['style_type']}")
        print(f"profile_mode={spec['profile_mode']}")
        print(f"ground_amount_type={spec['ground_amount_type']}")
        print(f"ditch_amount_type={spec['ditch_amount_type']}")
        print(f"expected_points={spec['expected_points']}")
        print(f"expected_ism={spec['expected_ism']}")
        print(f"mesh_paths={spec['mesh_paths']}")
    print("MCP_CUBELESS_ED_STYLE_PROFILE_MATRIX_PRESETS_BUILD_END")


if __name__ == "__main__":
    main()
