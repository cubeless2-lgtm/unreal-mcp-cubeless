import unreal


PACKAGE_PATH = "/Game/_MCP_Temp/PCG"
ASSET_NAME = "ElectricDreams_HierarchyOffsetValidation_MCP"
GRAPH_PATH = f"{PACKAGE_PATH}/{ASSET_NAME}.{ASSET_NAME}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_HierarchyOffsetValidation"
SOURCE_COUNT = 3
COPIES_COUNT = 2


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


def configure_math(node, operation, input1, input2, output_attr):
    settings = node.get_settings()
    settings.set_editor_property("operation", operation)
    selector_import(settings, "input_source1", input1)
    selector_import(settings, "input_source2", input2)
    selector_import(settings, "output_target", output_attr)


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

    source = add_node(graph, unreal.PCGCreatePointsSettings, "01 Source Local Assembly Points x3", -1200, -150)
    target = add_node(graph, unreal.PCGCreatePointsSettings, "02 Target Copy Points x2", -1200, 180)
    copy = add_node(graph, unreal.PCGCopyPointsSettings, "03 Copy Source Onto Two Targets", -900, 0)
    global_index = add_node(graph, unreal.PCGAddAttributeSettings, "04 GlobalIndex From $MetadataEntry", -620, 0)
    source_count = add_node(graph, unreal.PCGAddAttributeSettings, "05 SourcePointCount Constant 3", -380, 0)
    copies_count = add_node(graph, unreal.PCGAddAttributeSettings, "06 CopiesCount Constant 2", -140, 0)
    local_raw = add_node(graph, unreal.PCGMetadataMathsSettings, "07 ActorIndexLocalRaw = GlobalIndex / CopiesCount", 120, 0)
    local_index = add_node(graph, unreal.PCGMetadataMathsSettings, "08 ActorIndexLocal = Floor(LocalRaw)", 390, 0)
    copy_index = add_node(graph, unreal.PCGMetadataMathsSettings, "09 CopyIndex = GlobalIndex % CopiesCount", 660, 0)
    copy_offset = add_node(graph, unreal.PCGMetadataMathsSettings, "10 CopyOffset = CopyIndex * SourcePointCount", 930, 0)
    actor_index = add_node(graph, unreal.PCGMetadataMathsSettings, "11 ActorIndex = ActorIndexLocal + CopyOffset", 1200, 0)
    root_filter = add_node(graph, unreal.PCGAttributeFilteringSettings, "12 Split Root Where ActorIndexLocal == 0", 1480, 0)
    root_parent = add_node(graph, unreal.PCGAddAttributeSettings, "13R Root ParentIndex -1", 1760, -160)
    root_depth = add_node(graph, unreal.PCGAddAttributeSettings, "14R Root HierarchyDepth 0", 2000, -160)
    child_parent = add_node(graph, unreal.PCGAddAttributeSettings, "13C Child ParentIndex = CopyOffset", 1760, 160)
    child_depth = add_node(graph, unreal.PCGAddAttributeSettings, "14C Child HierarchyDepth 1", 2000, 160)
    merge = add_node(graph, unreal.PCGMergeSettings, "15 Merge Offset Hierarchy Branches", 2280, 0)

    configure_points(source, [(0, 0, 0), (100, 0, 0), (200, 0, 0)])
    configure_points(target, [(0, 0, 0), (0, 400, 0)])

    copy_settings = copy.get_settings()
    copy_settings.set_editor_property("rotation_inheritance", unreal.PCGCopyPointsInheritanceMode.RELATIVE)
    copy_settings.set_editor_property("scale_inheritance", unreal.PCGCopyPointsInheritanceMode.RELATIVE)
    copy_settings.set_editor_property("color_inheritance", unreal.PCGCopyPointsInheritanceMode.RELATIVE)
    copy_settings.set_editor_property("seed_inheritance", unreal.PCGCopyPointsInheritanceMode.RELATIVE)
    copy_settings.set_editor_property("attribute_inheritance", unreal.PCGCopyPointsMetadataInheritanceMode.SOURCE_ONLY)
    copy_settings.set_editor_property("tag_inheritance", unreal.PCGCopyPointsTagInheritanceMode.BOTH)
    copy_settings.set_editor_property("copy_each_source_on_every_target", True)

    configure_add(global_index, "GlobalIndex", "$MetadataEntry")
    configure_add(source_count, "SourcePointCount", "@Last", unreal.PCGMetadataTypes.INTEGER32, SOURCE_COUNT)
    configure_add(copies_count, "CopiesCount", "@Last", unreal.PCGMetadataTypes.INTEGER32, COPIES_COUNT)
    configure_math(local_raw, unreal.PCGMetadataMathsOperation.DIVIDE, "GlobalIndex", "CopiesCount", "ActorIndexLocalRaw")
    configure_math(local_index, unreal.PCGMetadataMathsOperation.FLOOR, "ActorIndexLocalRaw", "ActorIndexLocalRaw", "ActorIndexLocal")
    configure_math(copy_index, unreal.PCGMetadataMathsOperation.MODULO, "GlobalIndex", "CopiesCount", "CopyIndex")
    configure_math(copy_offset, unreal.PCGMetadataMathsOperation.MULTIPLY, "CopyIndex", "SourcePointCount", "CopyOffset")
    configure_math(actor_index, unreal.PCGMetadataMathsOperation.ADD, "ActorIndexLocal", "CopyOffset", "ActorIndex")
    configure_filter_equal_zero(root_filter, "ActorIndexLocal")
    configure_add(root_parent, "ParentIndex", "@Last", unreal.PCGMetadataTypes.INTEGER32, -1)
    configure_add(root_depth, "HierarchyDepth", "@Last", unreal.PCGMetadataTypes.INTEGER32, 0)
    configure_add(child_parent, "ParentIndex", "CopyOffset")
    configure_add(child_depth, "HierarchyDepth", "@Last", unreal.PCGMetadataTypes.INTEGER32, 1)

    graph.add_edge(source, "Out", copy, "Source")
    graph.add_edge(target, "Out", copy, "Target")
    graph.add_edge(copy, "Out", global_index, "In")
    graph.add_edge(global_index, "Out", source_count, "In")
    graph.add_edge(source_count, "Out", copies_count, "In")
    graph.add_edge(copies_count, "Out", local_raw, "InA")
    graph.add_edge(copies_count, "Out", local_raw, "InB")
    graph.add_edge(local_raw, "Out", local_index, "In")
    graph.add_edge(local_index, "Out", copy_index, "InA")
    graph.add_edge(local_index, "Out", copy_index, "InB")
    graph.add_edge(copy_index, "Out", copy_offset, "InA")
    graph.add_edge(copy_index, "Out", copy_offset, "InB")
    graph.add_edge(copy_offset, "Out", actor_index, "InA")
    graph.add_edge(copy_offset, "Out", actor_index, "InB")
    graph.add_edge(actor_index, "Out", root_filter, "In")
    graph.add_edge(root_filter, "InsideFilter", root_parent, "In")
    graph.add_edge(root_parent, "Out", root_depth, "In")
    graph.add_edge(root_filter, "OutsideFilter", child_parent, "In")
    graph.add_edge(child_parent, "Out", child_depth, "In")
    graph.add_edge(root_depth, "Out", merge, "In")
    graph.add_edge(child_depth, "Out", merge, "In")
    graph.add_edge(merge, "Out", graph.get_output_node(), "Out")

    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def spawn_validation_actor(graph):
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for actor in unreal.EditorLevelLibrary.get_all_level_actors():
        if actor.get_actor_label() == ACTOR_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PCGVolume,
        unreal.Vector(1200, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(ACTOR_LABEL)
    pcg = actor.pcg_component
    pcg.set_graph(graph)
    pcg.cleanup(True)
    pcg.generate(True)
    return actor


print("MCP_PCG_OFFSET_VALIDATION_BUILD_BEGIN")
validation_graph = build_graph()
validation_actor = spawn_validation_actor(validation_graph)
print(f"validation_graph={validation_graph.get_path_name()}")
print(f"validation_actor={validation_actor.get_actor_label()}")
print("MCP_PCG_OFFSET_VALIDATION_BUILD_END")
