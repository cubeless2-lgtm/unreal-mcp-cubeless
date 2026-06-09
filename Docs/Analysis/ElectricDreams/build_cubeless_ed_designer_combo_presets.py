import unreal


PACKAGE_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning/DesignerCombos"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
VALIDATION_BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/"
    "BP_Cubeless_ED_PCGDesignerControlActor.BP_Cubeless_ED_PCGDesignerControlActor_C"
)
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_DesignerCombo"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0

AMOUNT_PRESET_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning/AmountPresets"

COMBO_SPECS = [
    {
        "name": "Sparse",
        "asset_name": "PCG_Cubeless_ED_DesignerCombo_Sparse",
        "combo_id": 401,
        "combo_type": 1,
        "branches": [
            {
                "name": "GroundSparse",
                "graph_path": (
                    f"{AMOUNT_PRESET_PATH}/"
                    "PCG_Cubeless_ED_GroundAmount_Sparse.PCG_Cubeless_ED_GroundAmount_Sparse"
                ),
                "profile_id": 10,
                "profile_type": 1,
                "amount_id": 201,
                "amount_type": 1,
                "expected_points": 3,
            },
            {
                "name": "DitchSparse",
                "graph_path": (
                    f"{AMOUNT_PRESET_PATH}/"
                    "PCG_Cubeless_ED_DitchAmount_Sparse.PCG_Cubeless_ED_DitchAmount_Sparse"
                ),
                "profile_id": 20,
                "profile_type": 2,
                "amount_id": 301,
                "amount_type": 1,
                "expected_points": 18,
            },
        ],
        "expected_points": 21,
        "expected_ism": 21,
        "expected_profile_counts": {10: 3, 20: 18},
        "expected_amount_counts": {201: 3, 301: 18},
    },
    {
        "name": "Normal",
        "asset_name": "PCG_Cubeless_ED_DesignerCombo_Normal",
        "combo_id": 402,
        "combo_type": 2,
        "branches": [
            {
                "name": "GroundNormal",
                "graph_path": (
                    f"{AMOUNT_PRESET_PATH}/"
                    "PCG_Cubeless_ED_GroundAmount_Normal.PCG_Cubeless_ED_GroundAmount_Normal"
                ),
                "profile_id": 10,
                "profile_type": 1,
                "amount_id": 202,
                "amount_type": 2,
                "expected_points": 8,
            },
            {
                "name": "DitchNormal",
                "graph_path": (
                    f"{AMOUNT_PRESET_PATH}/"
                    "PCG_Cubeless_ED_DitchAmount_Normal.PCG_Cubeless_ED_DitchAmount_Normal"
                ),
                "profile_id": 20,
                "profile_type": 2,
                "amount_id": 302,
                "amount_type": 2,
                "expected_points": 42,
            },
        ],
        "expected_points": 50,
        "expected_ism": 50,
        "expected_profile_counts": {10: 8, 20: 42},
        "expected_amount_counts": {202: 8, 302: 42},
    },
    {
        "name": "Dense",
        "asset_name": "PCG_Cubeless_ED_DesignerCombo_Dense",
        "combo_id": 403,
        "combo_type": 3,
        "branches": [
            {
                "name": "GroundDense",
                "graph_path": (
                    f"{AMOUNT_PRESET_PATH}/"
                    "PCG_Cubeless_ED_GroundAmount_Dense.PCG_Cubeless_ED_GroundAmount_Dense"
                ),
                "profile_id": 10,
                "profile_type": 1,
                "amount_id": 203,
                "amount_type": 3,
                "expected_points": 16,
            },
            {
                "name": "DitchDense",
                "graph_path": (
                    f"{AMOUNT_PRESET_PATH}/"
                    "PCG_Cubeless_ED_DitchAmount_Dense.PCG_Cubeless_ED_DitchAmount_Dense"
                ),
                "profile_id": 20,
                "profile_type": 2,
                "amount_id": 303,
                "amount_type": 3,
                "expected_points": 84,
            },
        ],
        "expected_points": 100,
        "expected_ism": 100,
        "expected_profile_counts": {10: 16, 20: 84},
        "expected_amount_counts": {203: 16, 303: 84},
    },
]

COMBO_GRAPH_PATHS = {
    spec["name"]: f"{PACKAGE_PATH}/{spec['asset_name']}.{spec['asset_name']}"
    for spec in COMBO_SPECS
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


def add_combo_markers(graph, upstream, spec, x, y):
    combo_id = add_node(graph, unreal.PCGAddAttributeSettings, f"Combo {spec['combo_id']} DesignerComboId", x, y)
    combo_type = add_node(graph, unreal.PCGAddAttributeSettings, f"Combo {spec['combo_id']} DesignerComboType", x + 340, y)
    combo_pass = add_node(graph, unreal.PCGAddAttributeSettings, f"Combo {spec['combo_id']} DesignerComboPass", x + 680, y)

    configure_add(combo_id, "DesignerComboId", "@Last", unreal.PCGMetadataTypes.INTEGER32, spec["combo_id"])
    configure_add(combo_type, "DesignerComboType", "@Last", unreal.PCGMetadataTypes.INTEGER32, spec["combo_type"])
    configure_add(combo_pass, "DesignerComboPass", "@Last", unreal.PCGMetadataTypes.BOOLEAN, True)

    graph.add_edge(upstream, "Out", combo_id, "In")
    graph.add_edge(combo_id, "Out", combo_type, "In")
    graph.add_edge(combo_type, "Out", combo_pass, "In")
    return combo_pass


def build_combo_graph(spec):
    unreal.EditorAssetLibrary.make_directory(PACKAGE_PATH)
    graph_path = COMBO_GRAPH_PATHS[spec["name"]]
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            spec["asset_name"],
            PACKAGE_PATH,
            unreal.PCGGraph.static_class(),
            unreal.PCGGraphFactory(),
        )
    if not graph:
        raise RuntimeError(f"Failed to create/load combo graph: {spec['name']}")

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

    merge = add_node(graph, unreal.PCGMergeSettings, f"Combo {spec['combo_id']} Merge Amount Branches", -500, 0)
    for output in outputs:
        graph.add_edge(output, "Out", merge, "In")

    final = add_combo_markers(graph, merge, spec, -120, 0)
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

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(13200 + index * 520, 0, 0),
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
    print("MCP_CUBELESS_ED_DESIGNER_COMBO_PRESETS_BUILD_BEGIN")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for index, spec in enumerate(COMBO_SPECS):
        graph = build_combo_graph(spec)
        actor = spawn_validation_actor(spec, graph, index)
        print(f"combo={spec['name']}")
        print(f"combo_graph={graph.get_path_name()}")
        print(f"validation_actor={actor.get_actor_label()}")
        print(f"combo_id={spec['combo_id']}")
        print(f"combo_type={spec['combo_type']}")
        print(f"expected_points={spec['expected_points']}")
        print(f"expected_ism={spec['expected_ism']}")
        print(f"expected_profile_counts={spec['expected_profile_counts']}")
        print(f"expected_amount_counts={spec['expected_amount_counts']}")
    print("MCP_CUBELESS_ED_DESIGNER_COMBO_PRESETS_BUILD_END")


if __name__ == "__main__":
    main()
