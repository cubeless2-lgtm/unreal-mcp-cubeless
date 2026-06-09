import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\build_cubeless_ed_dynamic_material_axis_by_point.py",
    )
).parent
DYNAMIC_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_dynamic_material_override_prototype.py"
MATERIAL_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_material_override_presets.py"

PACKAGE = "/Game/Cubeless/PCG/ElectricDreamsLearning/DynamicMaterialPrototype"
GRAPH_ASSET = "PCG_Cubeless_ED_DynamicMaterialAxis_ByPoint_AllDomains"
GRAPH_PATH = f"{PACKAGE}/{GRAPH_ASSET}.{GRAPH_ASSET}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_Cubeless_ED_DynamicMaterialAxis_ByPoint_AllDomains_Validation"

DYNAMIC_AXIS_PASS_ATTR = "DynamicMaterialAxisPass"
INCLUDED_VARIANTS = (2, 3)
DOMAIN_X_OFFSETS = {
    1: 0.0,
    2: 3600.0,
    3: 7200.0,
}
VARIANT_Y_OFFSETS = {
    2: -1400.0,
    3: 1400.0,
}
ENTRY_Y_SPACING = 420.0


def load_config(script_path, namespace_name):
    namespace = {"__name__": namespace_name, "__file__": str(script_path)}
    with open(script_path, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(script_path), "exec")
    exec(code, namespace)
    return namespace


DYNAMIC_CONFIG = load_config(DYNAMIC_BUILDER_SCRIPT, "_cubeless_ed_dynamic_material_config")
MATERIAL_CONFIG = load_config(MATERIAL_BUILDER_SCRIPT, "_cubeless_ed_material_override_config")


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
        raise RuntimeError(f"Failed to create/load dynamic material axis graph: {GRAPH_PATH}")
    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)
    return graph


def shift_offsets(offsets, x_offset, y_offset):
    return [
        (float(x) + float(x_offset), float(y) + float(y_offset), float(z))
        for x, y, z in offsets
    ]


def point_spec_for_entry(spec, entry_index):
    domain_type = int(spec["domain_type"])
    variant_type = int(spec["variant_type"])
    return dict(
        spec,
        point_offsets=shift_offsets(
            spec["point_offsets"],
            DOMAIN_X_OFFSETS[domain_type],
            VARIANT_Y_OFFSETS[variant_type] + entry_index * ENTRY_Y_SPACING,
        ),
    )


def configure_points(node, spec, entry_index):
    point_spec = point_spec_for_entry(spec, entry_index)
    MATERIAL_CONFIG["configure_points"](node, point_spec)


def non_empty_materials(entry_spec):
    return [
        path for path in entry_spec["override_material_paths"]
        if path
    ]


def add_soft_path_attr(graph, upstream, title, attr_name, soft_path, x, y):
    node = DYNAMIC_CONFIG["add_node"](graph, unreal.PCGAddAttributeSettings, title, x, y)
    DYNAMIC_CONFIG["configure_add"](
        node,
        attr_name,
        "@Last",
        unreal.PCGMetadataTypes.SOFT_OBJECT_PATH,
        soft_path,
    )
    graph.add_edge(upstream, "Out", node, "In")
    return node


def add_bool_attr(graph, upstream, title, attr_name, value, x, y):
    node = DYNAMIC_CONFIG["add_node"](graph, unreal.PCGAddAttributeSettings, title, x, y)
    DYNAMIC_CONFIG["configure_add"](
        node,
        attr_name,
        "@Last",
        unreal.PCGMetadataTypes.BOOLEAN,
        value,
    )
    graph.add_edge(upstream, "Out", node, "In")
    return node


def branch_label(spec, entry_spec):
    return f"{spec['domain_name']}_{spec['variant_name']}_{entry_spec['mesh_key']}"


def add_dynamic_entry_branch(graph, spec, entry_spec, entry_index, branch_index):
    y = branch_index * 260.0
    label = branch_label(spec, entry_spec)
    source = DYNAMIC_CONFIG["add_node"](
        graph,
        unreal.PCGCreatePointsSettings,
        f"{label} Points",
        -2600,
        y,
    )
    configure_points(source, spec, entry_index)
    current = MATERIAL_CONFIG["add_material_markers"](graph, source, spec, -2220, y)
    current = add_soft_path_attr(
        graph,
        current,
        f"{DYNAMIC_CONFIG['DYNAMIC_MESH_ATTR']} {label}",
        DYNAMIC_CONFIG["DYNAMIC_MESH_ATTR"],
        entry_spec["mesh_path"],
        300,
        y,
    )

    materials = non_empty_materials(entry_spec)
    slot0 = materials[0] if len(materials) > 0 else ""
    slot1 = materials[1] if len(materials) > 1 else ""
    current = add_soft_path_attr(
        graph,
        current,
        f"{DYNAMIC_CONFIG['DYNAMIC_MATERIAL_SLOT0_ATTR']} {label}",
        DYNAMIC_CONFIG["DYNAMIC_MATERIAL_SLOT0_ATTR"],
        slot0,
        620,
        y,
    )
    current = add_soft_path_attr(
        graph,
        current,
        f"{DYNAMIC_CONFIG['DYNAMIC_MATERIAL_SLOT1_ATTR']} {label}",
        DYNAMIC_CONFIG["DYNAMIC_MATERIAL_SLOT1_ATTR"],
        slot1,
        940,
        y,
    )
    current = add_bool_attr(
        graph,
        current,
        f"{DYNAMIC_AXIS_PASS_ATTR} {label}",
        DYNAMIC_AXIS_PASS_ATTR,
        True,
        1260,
        y,
    )
    return current


def dynamic_specs():
    return [
        spec for spec in MATERIAL_CONFIG["MATERIAL_OVERRIDE_SPECS"]
        if int(spec["variant_type"]) in INCLUDED_VARIANTS
    ]


def expected_rows():
    rows = []
    for spec in dynamic_specs():
        for entry_index, entry_spec in enumerate(spec["entries"]):
            rows.append({
                "domain_name": spec["domain_name"],
                "domain_type": spec["domain_type"],
                "variant_name": spec["variant_name"],
                "variant_type": spec["variant_type"],
                "mesh_key": entry_spec["mesh_key"],
                "mesh_path": entry_spec["mesh_path"],
                "materials": non_empty_materials(entry_spec),
                "expected_instance_count": len(spec["point_offsets"]),
                "entry_index": entry_index,
            })
    return rows


def build_graph():
    graph = ensure_graph()
    branch_nodes = []
    branch_index = 0
    for spec in dynamic_specs():
        for entry_index, entry_spec in enumerate(spec["entries"]):
            branch_nodes.append(add_dynamic_entry_branch(graph, spec, entry_spec, entry_index, branch_index))
            branch_index += 1

    spawner = DYNAMIC_CONFIG["add_node"](
        graph,
        unreal.PCGStaticMeshSpawnerSettings,
        "Spawn ByAttribute Dynamic Material Axis",
        1680,
        720,
    )
    DYNAMIC_CONFIG["configure_by_attribute_spawner"](spawner)
    for branch_node in branch_nodes:
        graph.add_edge(branch_node, "Out", spawner, "In")
    graph.add_edge(spawner, "Out", graph.get_output_node(), "Out")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


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
        unreal.Vector(101000, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(ACTOR_LABEL)
    component = actor.pcg_component
    component.set_graph(graph)
    component.cleanup(True)
    component.generate(True)
    component.generate(True)
    return actor


def main():
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_BY_POINT_BUILD_BEGIN")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    MATERIAL_CONFIG["ensure_material_variants"]()
    graph = build_graph()
    actor = spawn_validation_actor(graph)
    rows = expected_rows()
    expected_total = sum(row["expected_instance_count"] for row in rows)
    print(f"dynamic_material_axis_graph={graph.get_path_name()}")
    print("dynamic_material_axis_graph_count=1")
    print(f"dynamic_material_axis_actor={actor.get_actor_label()}")
    print("dynamic_material_axis_actor_count=1")
    print(f"dynamic_material_axis_expected_row_count={len(rows)}")
    print(f"dynamic_material_axis_expected_points={expected_total}")
    print(f"dynamic_material_axis_expected_ism={expected_total}")
    for row in rows:
        print(f"expected_row={row}")
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_BY_POINT_BUILD_END")


if __name__ == "__main__":
    main()
