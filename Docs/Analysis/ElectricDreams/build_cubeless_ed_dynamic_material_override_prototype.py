import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\build_cubeless_ed_dynamic_material_override_prototype.py",
    )
).parent
TREE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_tree_profile_presets.py"
MATERIAL_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_material_override_presets.py"

DYNAMIC_PACKAGE = "/Game/Cubeless/PCG/ElectricDreamsLearning/DynamicMaterialPrototype"
DYNAMIC_GRAPH_ASSET = "PCG_Cubeless_ED_DynamicMaterial_CompactConifer_Sparse"
DYNAMIC_GRAPH_PATH = f"{DYNAMIC_PACKAGE}/{DYNAMIC_GRAPH_ASSET}.{DYNAMIC_GRAPH_ASSET}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_DynamicMaterialPrototype"

DYNAMIC_MESH_ATTR = "DynamicMeshPath"
DYNAMIC_MATERIAL_SLOT0_ATTR = "DynamicMaterialSlot0"
DYNAMIC_MATERIAL_SLOT1_ATTR = "DynamicMaterialSlot1"
DYNAMIC_ATTR_NODE_TITLES = {
    DYNAMIC_MESH_ATTR: "DynamicMeshPath Attribute",
    DYNAMIC_MATERIAL_SLOT0_ATTR: "DynamicMaterialSlot0 Attribute",
    DYNAMIC_MATERIAL_SLOT1_ATTR: "DynamicMaterialSlot1 Attribute",
}
COMPACT_CONIFER_MESH = (
    "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Trees/"
    "SM_Conifer_05.SM_Conifer_05"
)


def load_config(script_path, namespace_name):
    namespace = {"__name__": namespace_name, "__file__": str(script_path)}
    with open(script_path, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(script_path), "exec")
    exec(code, namespace)
    return namespace


TREE_CONFIG = load_config(TREE_BUILDER_SCRIPT, "_cubeless_ed_tree_profile_presets_config")
MATERIAL_CONFIG = load_config(MATERIAL_BUILDER_SCRIPT, "_cubeless_ed_material_override_presets_config")


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
    elif value_type == unreal.PCGMetadataTypes.SOFT_OBJECT_PATH:
        value_struct.set_editor_property("soft_object_path_value", unreal.SoftObjectPath(str(value)))
    elif value_type == unreal.PCGMetadataTypes.STRING:
        value_struct.set_editor_property("string_value", str(value))
    elif value_type == unreal.PCGMetadataTypes.NAME:
        value_struct.set_editor_property("name_value", str(value))
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


def ensure_graph():
    unreal.EditorAssetLibrary.make_directory(DYNAMIC_PACKAGE)
    graph = unreal.EditorAssetLibrary.load_asset(DYNAMIC_GRAPH_PATH)
    if not graph:
        graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            DYNAMIC_GRAPH_ASSET,
            DYNAMIC_PACKAGE,
            unreal.PCGGraph.static_class(),
            unreal.PCGGraphFactory(),
        )
    if not graph:
        raise RuntimeError(f"Failed to create/load dynamic graph: {DYNAMIC_GRAPH_PATH}")
    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)
    return graph


def get_compact_sparse_tree_spec():
    for spec in TREE_CONFIG["TREE_PROFILE_SPECS"]:
        if spec["style_type"] == 1 and spec["amount_type"] == 2:
            return spec
    raise RuntimeError("Missing CompactConifer Sparse tree profile spec")


def material_variant_paths(variant_type):
    material_path = MATERIAL_CONFIG["material_variant_path"]
    if int(variant_type) == 2:
        return {
            "variant_name": "DarkPine",
            "slot0": material_path("pine_leaves_dark"),
            "slot1": material_path("pine_bark_dark"),
        }
    if int(variant_type) == 3:
        return {
            "variant_name": "SoftPine",
            "slot0": material_path("pine_leaves_soft"),
            "slot1": material_path("pine_bark_soft"),
        }
    raise RuntimeError(f"Unsupported dynamic material variant: {variant_type}")


def get_graph_nodes_by_title(graph, title):
    return [
        node for node in graph.get_editor_property("nodes")
        if str(node.get_editor_property("node_title")) == title
    ]


def set_dynamic_attr_node(graph, attr_name, soft_object_path):
    nodes = get_graph_nodes_by_title(graph, DYNAMIC_ATTR_NODE_TITLES[attr_name])
    if len(nodes) != 1:
        raise RuntimeError(f"Expected one dynamic attr node for {attr_name}, found {len(nodes)}")
    configure_add(nodes[0], attr_name, "@Last", unreal.PCGMetadataTypes.SOFT_OBJECT_PATH, soft_object_path)


def set_dynamic_graph_material_variant(graph, variant_type, save_graph=False):
    variant = material_variant_paths(variant_type)
    set_dynamic_attr_node(graph, DYNAMIC_MATERIAL_SLOT0_ATTR, variant["slot0"])
    set_dynamic_attr_node(graph, DYNAMIC_MATERIAL_SLOT1_ATTR, variant["slot1"])
    if save_graph:
        unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return variant


def configure_by_attribute_spawner(node):
    settings = node.get_settings()
    settings.set_editor_property("allow_descriptor_changes", True)
    settings.set_mesh_selector_type(unreal.PCGMeshSelectorByAttribute.static_class())
    params = settings.get_editor_property("mesh_selector_parameters")
    params.set_editor_property("attribute_name", DYNAMIC_MESH_ATTR)
    params.set_editor_property("use_attribute_material_overrides", True)
    params.set_editor_property(
        "material_override_attributes",
        [DYNAMIC_MATERIAL_SLOT0_ATTR, DYNAMIC_MATERIAL_SLOT1_ATTR],
    )


def build_dynamic_graph():
    spec = get_compact_sparse_tree_spec()
    graph = ensure_graph()
    source = add_node(graph, unreal.PCGCreatePointsSettings, "CompactConifer Sparse Points", -1800, 0)
    TREE_CONFIG["configure_points"](source, spec)
    tree_markers = TREE_CONFIG["add_tree_markers"](graph, source, spec, -1420, 0)

    mesh_attr = add_node(graph, unreal.PCGAddAttributeSettings, DYNAMIC_ATTR_NODE_TITLES[DYNAMIC_MESH_ATTR], 2060, 0)
    configure_add(mesh_attr, DYNAMIC_MESH_ATTR, "@Last", unreal.PCGMetadataTypes.SOFT_OBJECT_PATH, COMPACT_CONIFER_MESH)
    graph.add_edge(tree_markers, "Out", mesh_attr, "In")

    slot0_attr = add_node(graph, unreal.PCGAddAttributeSettings, DYNAMIC_ATTR_NODE_TITLES[DYNAMIC_MATERIAL_SLOT0_ATTR], 2360, 0)
    configure_add(
        slot0_attr,
        DYNAMIC_MATERIAL_SLOT0_ATTR,
        "@Last",
        unreal.PCGMetadataTypes.SOFT_OBJECT_PATH,
        material_variant_paths(2)["slot0"],
    )
    graph.add_edge(mesh_attr, "Out", slot0_attr, "In")

    slot1_attr = add_node(graph, unreal.PCGAddAttributeSettings, DYNAMIC_ATTR_NODE_TITLES[DYNAMIC_MATERIAL_SLOT1_ATTR], 2660, 0)
    configure_add(
        slot1_attr,
        DYNAMIC_MATERIAL_SLOT1_ATTR,
        "@Last",
        unreal.PCGMetadataTypes.SOFT_OBJECT_PATH,
        material_variant_paths(2)["slot1"],
    )
    graph.add_edge(slot0_attr, "Out", slot1_attr, "In")

    prototype_marker = add_node(graph, unreal.PCGAddAttributeSettings, "DesignerDynamicMaterialPrototypePass True", 2960, 0)
    configure_add(
        prototype_marker,
        "DesignerDynamicMaterialPrototypePass",
        "@Last",
        unreal.PCGMetadataTypes.BOOLEAN,
        True,
    )
    graph.add_edge(slot1_attr, "Out", prototype_marker, "In")

    spawner = add_node(graph, unreal.PCGStaticMeshSpawnerSettings, "Spawn ByAttribute Dynamic CompactConifer", 3300, 0)
    configure_by_attribute_spawner(spawner)
    graph.add_edge(prototype_marker, "Out", spawner, "In")
    graph.add_edge(spawner, "Out", graph.get_output_node(), "Out")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph, spec


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def spawn_validation_actor(graph, spec, variant_type, index):
    variant = set_dynamic_graph_material_variant(graph, variant_type, save_graph=True)
    label = f"{ACTOR_LABEL_PREFIX}_CompactConifer_Sparse_{variant['variant_name']}_Validation"
    for actor in list(get_all_level_actors()):
        if actor.get_actor_label() == label:
            unreal.EditorLevelLibrary.destroy_actor(actor)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PCGVolume,
        unreal.Vector(90000 + index * 1800, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(label)
    component = actor.pcg_component
    component.set_graph(graph)
    component.cleanup(True)
    component.generate(True)
    component.generate(True)
    return actor, variant


VALIDATION_VARIANTS = (2, 3)


def main():
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_PROTOTYPE_BUILD_BEGIN")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    MATERIAL_CONFIG["ensure_material_variants"]()
    graph, spec = build_dynamic_graph()
    for index, variant_type in enumerate(VALIDATION_VARIANTS):
        actor, variant = spawn_validation_actor(graph, spec, variant_type, index)
        print(f"dynamic_validation_actor={actor.get_actor_label()}")
        print(f"  graph={graph.get_path_name()}")
        print(f"  tree_style_type={spec['style_type']}")
        print(f"  tree_amount_type={spec['amount_type']}")
        print(f"  variant_type={variant_type}")
        print(f"  variant_name={variant['variant_name']}")
        print(f"  expected_points={spec['expected_points']}")
        print(f"  expected_ism={spec['expected_ism']}")
        print(f"  mesh_attr={DYNAMIC_MESH_ATTR}:{COMPACT_CONIFER_MESH}")
        print(f"  material_attrs={[DYNAMIC_MATERIAL_SLOT0_ATTR, DYNAMIC_MATERIAL_SLOT1_ATTR]}")
        print(f"  expected_materials={[variant['slot0'], variant['slot1']]}")
    print(f"dynamic_graph_count=1")
    print(f"dynamic_validation_actor_count={len(VALIDATION_VARIANTS)}")
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_PROTOTYPE_BUILD_END")


if __name__ == "__main__":
    main()
