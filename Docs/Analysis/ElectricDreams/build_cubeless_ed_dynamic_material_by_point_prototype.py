import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\build_cubeless_ed_dynamic_material_by_point_prototype.py",
    )
).parent
BASE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_dynamic_material_override_prototype.py"

PACKAGE = "/Game/Cubeless/PCG/ElectricDreamsLearning/DynamicMaterialPrototype"
GRAPH_ASSET = "PCG_Cubeless_ED_DynamicMaterial_ByPoint_CompactConifer_Sparse"
GRAPH_PATH = f"{PACKAGE}/{GRAPH_ASSET}.{GRAPH_ASSET}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_Cubeless_ED_DynamicMaterialByPoint_CompactConifer_Sparse_Validation"

DYNAMIC_VARIANT_ATTR = "DynamicMaterialVariantType"
BRANCH_Y_OFFSETS = {
    2: -1200.0,
    3: 1200.0,
}


def load_base_config():
    namespace = {"__name__": "_cubeless_ed_dynamic_material_base_config", "__file__": str(BASE_BUILDER_SCRIPT)}
    with open(BASE_BUILDER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(BASE_BUILDER_SCRIPT), "exec")
    exec(code, namespace)
    return namespace


BASE = load_base_config()
TREE_CONFIG = BASE["TREE_CONFIG"]
MATERIAL_CONFIG = BASE["MATERIAL_CONFIG"]


def shifted_spec(spec, y_offset):
    copy = dict(spec)
    copy["point_offsets"] = [
        (float(x), float(y) + float(y_offset), float(z))
        for x, y, z in spec["point_offsets"]
    ]
    return copy


def ensure_graph():
    unreal.EditorAssetLibrary.make_directory(PACKAGE)
    graph = unreal.EditorAssetLibrary.load_asset(GRAPH_PATH)
    if not graph:
        graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            GRAPH_ASSET,
            PACKAGE,
            unreal.PCGGraph.static_class(),
            unreal.PCGGraphFactory(),
        )
    if not graph:
        raise RuntimeError(f"Failed to create/load by-point graph: {GRAPH_PATH}")
    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)
    return graph


def add_variant_branch(graph, spec, variant_type, x, y):
    variant = BASE["material_variant_paths"](variant_type)
    branch_spec = shifted_spec(spec, BRANCH_Y_OFFSETS[variant_type])
    source = BASE["add_node"](
        graph,
        unreal.PCGCreatePointsSettings,
        f"CompactConifer Sparse Points {variant['variant_name']}",
        x,
        y,
    )
    TREE_CONFIG["configure_points"](source, branch_spec)
    current = TREE_CONFIG["add_tree_markers"](graph, source, spec, x + 360, y)

    variant_attr = BASE["add_node"](
        graph,
        unreal.PCGAddAttributeSettings,
        f"{DYNAMIC_VARIANT_ATTR} {variant_type}",
        x + 3740,
        y,
    )
    BASE["configure_add"](
        variant_attr,
        DYNAMIC_VARIANT_ATTR,
        "@Last",
        unreal.PCGMetadataTypes.INTEGER32,
        variant_type,
    )
    graph.add_edge(current, "Out", variant_attr, "In")
    current = variant_attr

    mesh_attr = BASE["add_node"](
        graph,
        unreal.PCGAddAttributeSettings,
        f"{BASE['DYNAMIC_MESH_ATTR']} {variant['variant_name']}",
        x + 4040,
        y,
    )
    BASE["configure_add"](
        mesh_attr,
        BASE["DYNAMIC_MESH_ATTR"],
        "@Last",
        unreal.PCGMetadataTypes.SOFT_OBJECT_PATH,
        BASE["COMPACT_CONIFER_MESH"],
    )
    graph.add_edge(current, "Out", mesh_attr, "In")
    current = mesh_attr

    slot0_attr = BASE["add_node"](
        graph,
        unreal.PCGAddAttributeSettings,
        f"{BASE['DYNAMIC_MATERIAL_SLOT0_ATTR']} {variant['variant_name']}",
        x + 4340,
        y,
    )
    BASE["configure_add"](
        slot0_attr,
        BASE["DYNAMIC_MATERIAL_SLOT0_ATTR"],
        "@Last",
        unreal.PCGMetadataTypes.SOFT_OBJECT_PATH,
        variant["slot0"],
    )
    graph.add_edge(current, "Out", slot0_attr, "In")
    current = slot0_attr

    slot1_attr = BASE["add_node"](
        graph,
        unreal.PCGAddAttributeSettings,
        f"{BASE['DYNAMIC_MATERIAL_SLOT1_ATTR']} {variant['variant_name']}",
        x + 4640,
        y,
    )
    BASE["configure_add"](
        slot1_attr,
        BASE["DYNAMIC_MATERIAL_SLOT1_ATTR"],
        "@Last",
        unreal.PCGMetadataTypes.SOFT_OBJECT_PATH,
        variant["slot1"],
    )
    graph.add_edge(current, "Out", slot1_attr, "In")
    current = slot1_attr

    pass_attr = BASE["add_node"](
        graph,
        unreal.PCGAddAttributeSettings,
        f"DesignerDynamicMaterialByPointPass {variant['variant_name']}",
        x + 4940,
        y,
    )
    BASE["configure_add"](
        pass_attr,
        "DesignerDynamicMaterialByPointPass",
        "@Last",
        unreal.PCGMetadataTypes.BOOLEAN,
        True,
    )
    graph.add_edge(current, "Out", pass_attr, "In")
    return pass_attr, variant


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def spawn_validation_actor(graph):
    for actor in list(get_all_level_actors()):
        if actor.get_actor_label() == ACTOR_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PCGVolume,
        unreal.Vector(95000, 3000, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(ACTOR_LABEL)
    component = actor.pcg_component
    component.set_graph(graph)
    component.cleanup(True)
    component.generate(True)
    component.generate(True)
    return actor


def build_graph():
    spec = BASE["get_compact_sparse_tree_spec"]()
    graph = ensure_graph()
    branch_results = []
    for row, variant_type in enumerate((2, 3)):
        branch_results.append(add_variant_branch(graph, spec, variant_type, -2200, row * 900))

    spawner = BASE["add_node"](
        graph,
        unreal.PCGStaticMeshSpawnerSettings,
        "Spawn ByAttribute Dynamic CompactConifer ByPoint",
        3300,
        420,
    )
    BASE["configure_by_attribute_spawner"](spawner)
    for branch_node, _variant in branch_results:
        graph.add_edge(branch_node, "Out", spawner, "In")
    graph.add_edge(spawner, "Out", graph.get_output_node(), "Out")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph, spec, [variant for _node, variant in branch_results]


def main():
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_BY_POINT_BUILD_BEGIN")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    MATERIAL_CONFIG["ensure_material_variants"]()
    graph, spec, variants = build_graph()
    actor = spawn_validation_actor(graph)
    print(f"dynamic_by_point_graph={graph.get_path_name()}")
    print(f"dynamic_by_point_graph_count=1")
    print(f"dynamic_by_point_actor={actor.get_actor_label()}")
    print(f"dynamic_by_point_actor_count=1")
    print(f"expected_points_per_variant={spec['expected_points']}")
    print(f"expected_total_points={spec['expected_points'] * len(variants)}")
    print(f"expected_ism_per_variant={spec['expected_ism']}")
    print(f"expected_total_ism={spec['expected_ism'] * len(variants)}")
    for variant in variants:
        print(f"variant_name={variant['variant_name']}")
        print(f"  expected_materials={[variant['slot0'], variant['slot1']]}")
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_BY_POINT_BUILD_END")


if __name__ == "__main__":
    main()
