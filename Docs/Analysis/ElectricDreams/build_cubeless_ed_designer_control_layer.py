import unreal


PACKAGE_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning"
ASSET_NAME = "PCG_Cubeless_ED_DesignerControlLayer"
GRAPH_PATH = f"{PACKAGE_PATH}/{ASSET_NAME}.{ASSET_NAME}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_Cubeless_ED_DesignerControlLayer_Validation"
VALIDATION_BLUEPRINT_CLASS_PATH = (
    "/Game/_MCP_Temp/PCG/"
    "BP_ElectricDreamsSplineAssemblyTest.BP_ElectricDreamsSplineAssemblyTest_C"
)

PROFILE_SPECS = [
    {
        "name": "GroundControls",
        "id": 10,
        "type": 1,
        "expected_points": 8,
        "graph_path": (
            "/Game/Cubeless/PCG/ElectricDreamsLearning/"
            "PCG_Cubeless_GroundControlsPrototype.PCG_Cubeless_GroundControlsPrototype"
        ),
    },
    {
        "name": "DitchHierarchy",
        "id": 20,
        "type": 2,
        "expected_points": 42,
        "graph_path": (
            "/Game/Cubeless/PCG/ElectricDreamsLearning/"
            "PCG_Cubeless_DitchHierarchyPrototype.PCG_Cubeless_DitchHierarchyPrototype"
        ),
    },
]

TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0


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
    for spline in actor.get_components_by_class(unreal.SplineComponent):
        half_length = (float(TARGET_SAMPLE_COUNT) - 1.0) * float(TARGET_POINT_SPACING) * 0.5
        spline.clear_spline_points(False)
        spline.add_spline_point(unreal.Vector(0, -half_length, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, 0, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, half_length, 0), unreal.SplineCoordinateSpace.LOCAL, True)
        spline.update_spline()


def build_profile_branch(graph, spec, x, y):
    subgraph = add_node(graph, unreal.PCGSubgraphSettings, f"Profile {spec['id']} {spec['name']} Subgraph", x, y)
    profile_id = add_node(graph, unreal.PCGAddAttributeSettings, f"Profile {spec['id']} DesignerProfileId", x + 340, y)
    profile_type = add_node(graph, unreal.PCGAddAttributeSettings, f"Profile {spec['id']} DesignerProfileType", x + 680, y)
    pass_marker = add_node(graph, unreal.PCGAddAttributeSettings, f"Profile {spec['id']} DesignerControlLayerPass", x + 1020, y)

    configure_subgraph(subgraph, spec["graph_path"])
    configure_add(profile_id, "DesignerProfileId", "@Last", unreal.PCGMetadataTypes.INTEGER32, spec["id"])
    configure_add(profile_type, "DesignerProfileType", "@Last", unreal.PCGMetadataTypes.INTEGER32, spec["type"])
    configure_add(pass_marker, "DesignerControlLayerPass", "@Last", unreal.PCGMetadataTypes.BOOLEAN, True)

    graph.add_edge(graph.get_input_node(), "In", subgraph, "In")
    graph.add_edge(subgraph, "Out", profile_id, "In")
    graph.add_edge(profile_id, "Out", profile_type, "In")
    graph.add_edge(profile_type, "Out", pass_marker, "In")
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

    outputs = []
    for idx, spec in enumerate(PROFILE_SPECS):
        outputs.append(build_profile_branch(graph, spec, -1200, -180 + idx * 360))

    merge = add_node(graph, unreal.PCGMergeSettings, "Merge Designer Profile Outputs", 240, 0)
    for output in outputs:
        graph.add_edge(output, "Out", merge, "In")
    graph.add_edge(merge, "Out", graph.get_output_node(), "Out")

    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def spawn_validation_actor(graph):
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for actor in get_all_level_actors():
        if actor.get_actor_label() == ACTOR_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    actor_class = unreal.load_class(None, VALIDATION_BLUEPRINT_CLASS_PATH)
    if not actor_class:
        raise RuntimeError(f"Missing validation actor class: {VALIDATION_BLUEPRINT_CLASS_PATH}")

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(5100, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(ACTOR_LABEL)
    configure_validation_spline(actor)

    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {ACTOR_LABEL}")
    for component in pcg_components:
        component.set_graph(graph)
        component.cleanup(True)
        component.generate(True)
    return actor


def main():
    print("MCP_CUBELESS_ED_DESIGNER_CONTROL_LAYER_BUILD_BEGIN")
    graph = build_graph()
    actor = spawn_validation_actor(graph)
    print(f"production_graph={graph.get_path_name()}")
    print(f"validation_actor={actor.get_actor_label()}")
    print(f"validation_actor_class={VALIDATION_BLUEPRINT_CLASS_PATH}")
    print(f"profile_specs={PROFILE_SPECS}")
    print(f"expected_total_points={sum(spec['expected_points'] for spec in PROFILE_SPECS)}")
    print("MCP_CUBELESS_ED_DESIGNER_CONTROL_LAYER_BUILD_END")


if __name__ == "__main__":
    main()
