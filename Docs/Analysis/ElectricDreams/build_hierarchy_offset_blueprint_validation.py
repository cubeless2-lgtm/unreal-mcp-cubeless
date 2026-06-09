import unreal


PACKAGE_PATH = "/Game/_MCP_Temp/PCG"
ASSET_NAME = "ElectricDreams_HierarchyOffsetBlueprintValidation_MCP"
GRAPH_PATH = f"{PACKAGE_PATH}/{ASSET_NAME}.{ASSET_NAME}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_HierarchyOffsetBlueprintValidation"
BLUEPRINT_CLASS_PATH = (
    "/Game/_MCP_Temp/PCGCustomNodes/"
    "PostCopyPoints-OffsetIndices.PostCopyPoints-OffsetIndices_C"
)


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
        value_struct.set_editor_property("transform_value", value)
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


def configure_points(node, coords):
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
        point.set_editor_property("density", 1.0)
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


def configure_cast(node, input_attr, output_attr, output_type):
    settings = node.get_settings()
    selector_import(settings, "input_source", input_attr)
    selector_import(settings, "output_target", output_attr)
    settings.set_editor_property("output_type", output_type)


def configure_filter_equal_zero(node, attr):
    settings = node.get_settings()
    settings.set_editor_property("operator", unreal.PCGAttributeFilterOperator.EQUAL)
    settings.set_editor_property("use_constant_threshold", True)
    selector_import(settings, "target_attribute", attr)
    selector_import(settings, "threshold_attribute", attr)
    value_struct = settings.get_editor_property("attribute_types")
    set_const_value_struct(value_struct, unreal.PCGMetadataTypes.INTEGER32, 0)
    settings.set_editor_property("attribute_types", value_struct)
    settings.set_editor_property("warn_on_data_missing_attribute", True)


def configure_copy_points(node):
    settings = node.get_settings()
    settings.set_editor_property("rotation_inheritance", unreal.PCGCopyPointsInheritanceMode.RELATIVE)
    settings.set_editor_property("scale_inheritance", unreal.PCGCopyPointsInheritanceMode.RELATIVE)
    settings.set_editor_property("color_inheritance", unreal.PCGCopyPointsInheritanceMode.RELATIVE)
    settings.set_editor_property("seed_inheritance", unreal.PCGCopyPointsInheritanceMode.RELATIVE)
    settings.set_editor_property("attribute_inheritance", unreal.PCGCopyPointsMetadataInheritanceMode.SOURCE_ONLY)
    settings.set_editor_property("tag_inheritance", unreal.PCGCopyPointsTagInheritanceMode.BOTH)
    settings.set_editor_property("copy_each_source_on_every_target", True)


def configure_blueprint_node(node):
    settings = node.get_settings()
    bp_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not bp_class:
        raise RuntimeError(f"Failed to load {BLUEPRINT_CLASS_PATH}")
    settings.set_editor_property("blueprint_element_type", bp_class)


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

    source0 = add_node(graph, unreal.PCGCreatePointsSettings, "01A Source Root Point", -1540, -360)
    source1 = add_node(graph, unreal.PCGCreatePointsSettings, "01B Source Child Point 1", -1540, -120)
    source2 = add_node(graph, unreal.PCGCreatePointsSettings, "01C Source Child Point 2", -1540, 120)
    target = add_node(graph, unreal.PCGCreatePointsSettings, "02 Target Copy Points x2", -1540, 420)
    source0_actor = add_node(graph, unreal.PCGAddAttributeSettings, "03A Root ActorIndex 0", -1260, -360)
    source0_parent = add_node(graph, unreal.PCGAddAttributeSettings, "04A Root ParentIndex -1", -1020, -360)
    source0_depth = add_node(graph, unreal.PCGAddAttributeSettings, "05A Root HierarchyDepth 0", -780, -360)
    source0_relative = add_node(graph, unreal.PCGAddAttributeSettings, "06A Root RelativeTransform", -540, -360)
    source1_actor = add_node(graph, unreal.PCGAddAttributeSettings, "03B Child1 ActorIndex 1", -1260, -120)
    source1_parent = add_node(graph, unreal.PCGAddAttributeSettings, "04B Child1 ParentIndex 0", -1020, -120)
    source1_depth = add_node(graph, unreal.PCGAddAttributeSettings, "05B Child1 HierarchyDepth 1", -780, -120)
    source1_relative = add_node(graph, unreal.PCGAddAttributeSettings, "06B Child1 RelativeTransform", -540, -120)
    source2_actor = add_node(graph, unreal.PCGAddAttributeSettings, "03C Child2 ActorIndex 2", -1260, 120)
    source2_parent = add_node(graph, unreal.PCGAddAttributeSettings, "04C Child2 ParentIndex 0", -1020, 120)
    source2_depth = add_node(graph, unreal.PCGAddAttributeSettings, "05C Child2 HierarchyDepth 1", -780, 120)
    source2_relative = add_node(graph, unreal.PCGAddAttributeSettings, "06C Child2 RelativeTransform", -540, 120)
    source_merge = add_node(graph, unreal.PCGMergeSettings, "09 Merge Source Hierarchy", -240, -120)
    copy = add_node(graph, unreal.PCGCopyPointsSettings, "10 Copy Source Onto Targets", 740, -20)
    post_copy = add_node(graph, unreal.PCGBlueprintSettings, "11 Original PostCopyPoints Offset Blueprint", 1040, -20)
    ignore_rot = add_node(graph, unreal.PCGAddAttributeSettings, "12 IgnoreParentRotation False", 1340, -20)
    ignore_scale = add_node(graph, unreal.PCGAddAttributeSettings, "13 IgnoreParentScale False", 1620, -20)

    configure_points(source0, [(0, 0, 0)])
    configure_points(source1, [(100, 0, 0)])
    configure_points(source2, [(200, 0, 0)])
    configure_points(target, [(0, 0, 0), (0, 400, 0)])
    configure_add(source0_actor, "ActorIndex", "@Last", unreal.PCGMetadataTypes.INTEGER64, 0)
    configure_add(source0_parent, "ParentIndex", "@Last", unreal.PCGMetadataTypes.INTEGER64, -1)
    configure_add(source0_depth, "HierarchyDepth", "@Last", unreal.PCGMetadataTypes.INTEGER32, 0)
    configure_add(source0_relative, "RelativeTransform", "$Transform")
    configure_add(source1_actor, "ActorIndex", "@Last", unreal.PCGMetadataTypes.INTEGER64, 1)
    configure_add(source1_parent, "ParentIndex", "@Last", unreal.PCGMetadataTypes.INTEGER64, 0)
    configure_add(source1_depth, "HierarchyDepth", "@Last", unreal.PCGMetadataTypes.INTEGER32, 1)
    configure_add(source1_relative, "RelativeTransform", "$Transform")
    configure_add(source2_actor, "ActorIndex", "@Last", unreal.PCGMetadataTypes.INTEGER64, 2)
    configure_add(source2_parent, "ParentIndex", "@Last", unreal.PCGMetadataTypes.INTEGER64, 0)
    configure_add(source2_depth, "HierarchyDepth", "@Last", unreal.PCGMetadataTypes.INTEGER32, 1)
    configure_add(source2_relative, "RelativeTransform", "$Transform")
    configure_copy_points(copy)
    configure_blueprint_node(post_copy)
    configure_add(ignore_rot, "IgnoreParentRotation", "@Last", unreal.PCGMetadataTypes.BOOLEAN, False)
    configure_add(ignore_scale, "IgnoreParentScale", "@Last", unreal.PCGMetadataTypes.BOOLEAN, False)

    graph.add_edge(source0, "Out", source0_actor, "In")
    graph.add_edge(source0_actor, "Out", source0_parent, "In")
    graph.add_edge(source0_parent, "Out", source0_depth, "In")
    graph.add_edge(source0_depth, "Out", source0_relative, "In")
    graph.add_edge(source1, "Out", source1_actor, "In")
    graph.add_edge(source1_actor, "Out", source1_parent, "In")
    graph.add_edge(source1_parent, "Out", source1_depth, "In")
    graph.add_edge(source1_depth, "Out", source1_relative, "In")
    graph.add_edge(source2, "Out", source2_actor, "In")
    graph.add_edge(source2_actor, "Out", source2_parent, "In")
    graph.add_edge(source2_parent, "Out", source2_depth, "In")
    graph.add_edge(source2_depth, "Out", source2_relative, "In")
    graph.add_edge(source0_relative, "Out", source_merge, "In")
    graph.add_edge(source1_relative, "Out", source_merge, "In")
    graph.add_edge(source2_relative, "Out", source_merge, "In")
    graph.add_edge(source_merge, "Out", copy, "Source")
    graph.add_edge(target, "Out", copy, "Target")
    graph.add_edge(copy, "Out", post_copy, "CopyPointsOut")
    graph.add_edge(target, "Out", post_copy, "CopyPointsTarget")
    graph.add_edge(post_copy, "Out", ignore_rot, "In")
    graph.add_edge(ignore_rot, "Out", ignore_scale, "In")
    graph.add_edge(ignore_scale, "Out", graph.get_output_node(), "Out")

    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def spawn_validation_actor(graph):
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == ACTOR_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PCGVolume,
        unreal.Vector(1600, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(ACTOR_LABEL)
    pcg = actor.pcg_component
    pcg.set_graph(graph)
    pcg.cleanup(True)
    pcg.generate(True)
    return actor


print("MCP_PCG_OFFSET_BP_VALIDATION_BUILD_BEGIN")
validation_graph = build_graph()
validation_actor = spawn_validation_actor(validation_graph)
print(f"validation_graph={validation_graph.get_path_name()}")
print(f"validation_actor={validation_actor.get_actor_label()}")
print("MCP_PCG_OFFSET_BP_VALIDATION_BUILD_END")
