import unreal


PACKAGE_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning/DesignerMatrixCombos"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
VALIDATION_BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/"
    "BP_Cubeless_ED_PCGDesignerControlActor.BP_Cubeless_ED_PCGDesignerControlActor_C"
)
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_DesignerMatrix"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0

AMOUNT_PRESET_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning/AmountPresets"

GROUND_AMOUNT_SPECS = [
    {
        "name": "GroundSparse",
        "short_name": "GroundSparse",
        "graph_asset": "PCG_Cubeless_ED_GroundAmount_Sparse",
        "profile_id": 10,
        "profile_type": 1,
        "amount_id": 201,
        "amount_type": 1,
        "expected_points": 3,
    },
    {
        "name": "GroundNormal",
        "short_name": "GroundNormal",
        "graph_asset": "PCG_Cubeless_ED_GroundAmount_Normal",
        "profile_id": 10,
        "profile_type": 1,
        "amount_id": 202,
        "amount_type": 2,
        "expected_points": 8,
    },
    {
        "name": "GroundDense",
        "short_name": "GroundDense",
        "graph_asset": "PCG_Cubeless_ED_GroundAmount_Dense",
        "profile_id": 10,
        "profile_type": 1,
        "amount_id": 203,
        "amount_type": 3,
        "expected_points": 16,
    },
]

DITCH_AMOUNT_SPECS = [
    {
        "name": "DitchSparse",
        "short_name": "DitchSparse",
        "graph_asset": "PCG_Cubeless_ED_DitchAmount_Sparse",
        "profile_id": 20,
        "profile_type": 2,
        "amount_id": 301,
        "amount_type": 1,
        "expected_points": 18,
    },
    {
        "name": "DitchNormal",
        "short_name": "DitchNormal",
        "graph_asset": "PCG_Cubeless_ED_DitchAmount_Normal",
        "profile_id": 20,
        "profile_type": 2,
        "amount_id": 302,
        "amount_type": 2,
        "expected_points": 42,
    },
    {
        "name": "DitchDense",
        "short_name": "DitchDense",
        "graph_asset": "PCG_Cubeless_ED_DitchAmount_Dense",
        "profile_id": 20,
        "profile_type": 2,
        "amount_id": 303,
        "amount_type": 3,
        "expected_points": 84,
    },
]


def graph_path_for_amount(asset_name):
    return f"{AMOUNT_PRESET_PATH}/{asset_name}.{asset_name}"


def make_matrix_spec(ground, ditch):
    combo_type = ground["amount_type"] * 10 + ditch["amount_type"]
    combo_id = 500 + combo_type
    asset_name = f"PCG_Cubeless_ED_Matrix_{ground['short_name']}_{ditch['short_name']}"
    expected_points = ground["expected_points"] + ditch["expected_points"]
    return {
        "name": f"{ground['short_name']}_{ditch['short_name']}",
        "asset_name": asset_name,
        "combo_id": combo_id,
        "combo_type": combo_type,
        "ground_amount_type": ground["amount_type"],
        "ditch_amount_type": ditch["amount_type"],
        "branches": [
            {
                **ground,
                "graph_path": graph_path_for_amount(ground["graph_asset"]),
            },
            {
                **ditch,
                "graph_path": graph_path_for_amount(ditch["graph_asset"]),
            },
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


MATRIX_SPECS = [
    make_matrix_spec(ground, ditch)
    for ground in GROUND_AMOUNT_SPECS
    for ditch in DITCH_AMOUNT_SPECS
]

MATRIX_GRAPH_PATHS = {
    spec["name"]: f"{PACKAGE_PATH}/{spec['asset_name']}.{spec['asset_name']}"
    for spec in MATRIX_SPECS
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


def add_marker(graph, upstream, title, attr_name, value_type, value, x, y):
    node = add_node(graph, unreal.PCGAddAttributeSettings, title, x, y)
    configure_add(node, attr_name, "@Last", value_type, value)
    graph.add_edge(upstream, "Out", node, "In")
    return node


def add_matrix_markers(graph, upstream, spec):
    markers = [
        ("DesignerComboId", unreal.PCGMetadataTypes.INTEGER32, spec["combo_id"]),
        ("DesignerComboType", unreal.PCGMetadataTypes.INTEGER32, spec["combo_type"]),
        ("DesignerGroundAmountType", unreal.PCGMetadataTypes.INTEGER32, spec["ground_amount_type"]),
        ("DesignerDitchAmountType", unreal.PCGMetadataTypes.INTEGER32, spec["ditch_amount_type"]),
        ("DesignerComboPass", unreal.PCGMetadataTypes.BOOLEAN, True),
        ("DesignerMatrixPass", unreal.PCGMetadataTypes.BOOLEAN, True),
    ]
    current = upstream
    for index, (attr_name, value_type, value) in enumerate(markers):
        current = add_marker(
            graph,
            current,
            f"Matrix {spec['combo_id']} {attr_name}",
            attr_name,
            value_type,
            value,
            -120 + index * 340,
            0,
        )
    return current


def build_matrix_graph(spec):
    unreal.EditorAssetLibrary.make_directory(PACKAGE_PATH)
    graph_path = MATRIX_GRAPH_PATHS[spec["name"]]
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            spec["asset_name"],
            PACKAGE_PATH,
            unreal.PCGGraph.static_class(),
            unreal.PCGGraphFactory(),
        )
    if not graph:
        raise RuntimeError(f"Failed to create/load matrix graph: {spec['name']}")

    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)

    outputs = []
    for index, branch in enumerate(spec["branches"]):
        y = -180 + index * 360
        subgraph = add_node(
            graph,
            unreal.PCGSubgraphSettings,
            f"{spec['name']} {branch['name']} Amount Subgraph",
            -1180,
            y,
        )
        configure_subgraph(subgraph, branch["graph_path"])
        graph.add_edge(graph.get_input_node(), "In", subgraph, "In")
        outputs.append(subgraph)

    merge = add_node(graph, unreal.PCGMergeSettings, f"Matrix {spec['combo_id']} Merge Amount Branches", -500, 0)
    for output in outputs:
        graph.add_edge(output, "Out", merge, "In")

    final = add_matrix_markers(graph, merge, spec)
    graph.add_edge(final, "Out", graph.get_output_node(), "Out")
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

    row = index // len(DITCH_AMOUNT_SPECS)
    column = index % len(DITCH_AMOUNT_SPECS)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(17600 + column * 560, row * 520, 0),
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
    print("MCP_CUBELESS_ED_DESIGNER_MATRIX_PRESETS_BUILD_BEGIN")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for index, spec in enumerate(MATRIX_SPECS):
        graph = build_matrix_graph(spec)
        actor = spawn_validation_actor(spec, graph, index)
        print(f"matrix={spec['name']}")
        print(f"matrix_graph={graph.get_path_name()}")
        print(f"validation_actor={actor.get_actor_label()}")
        print(f"combo_id={spec['combo_id']}")
        print(f"combo_type={spec['combo_type']}")
        print(f"ground_amount_type={spec['ground_amount_type']}")
        print(f"ditch_amount_type={spec['ditch_amount_type']}")
        print(f"expected_points={spec['expected_points']}")
        print(f"expected_profile_counts={spec['expected_profile_counts']}")
        print(f"expected_amount_counts={spec['expected_amount_counts']}")
    print("MCP_CUBELESS_ED_DESIGNER_MATRIX_PRESETS_BUILD_END")


if __name__ == "__main__":
    main()
