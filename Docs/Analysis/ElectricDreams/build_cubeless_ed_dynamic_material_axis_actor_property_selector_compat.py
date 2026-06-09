import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\build_cubeless_ed_dynamic_material_axis_actor_property_selector_compat.py",
    )
).parent
AXIS_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_dynamic_material_axis_by_point.py"

PACKAGE = "/Game/Cubeless/PCG/ElectricDreamsLearning/DynamicMaterialPrototype"
GRAPH_ASSET = "PCG_Cubeless_ED_DynamicMaterialAxis_ActorPropertySelector_Compat"
GRAPH_PATH = f"{PACKAGE}/{GRAPH_ASSET}.{GRAPH_ASSET}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_Cubeless_ED_DynamicMaterialAxis_ActorPropertySelector_Compat_GroundFoliage_CoolLeaf_Validation"

BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGMaterialOverrideSelector.BP_Cubeless_ED_PCGMaterialOverrideSelector_C"
)

DOMAIN_ATTR = "DesignerMaterialDomainType"
VARIANT_ATTR = "DesignerMaterialVariantType"
DOMAIN_PROPERTY = "MaterialDomainType"
VARIANT_PROPERTY = "MaterialVariantType"
SELECTED_DOMAIN_ATTR = "SelectedMaterialDomainType"
SELECTED_VARIANT_ATTR = "SelectedMaterialVariantType"
SELECTED_DOMAIN_TYPE = 1
SELECTED_VARIANT_TYPE = 2
INCLUDED_VARIANTS = (2, 3)


def load_axis_config():
    namespace = {"__name__": "_cubeless_ed_dynamic_material_axis_config", "__file__": str(AXIS_BUILDER_SCRIPT)}
    with open(AXIS_BUILDER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(AXIS_BUILDER_SCRIPT), "exec")
    exec(code, namespace)
    return namespace


AXIS_CONFIG = load_axis_config()


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
        raise RuntimeError(f"Failed to create/load compat actor property selector graph: {GRAPH_PATH}")
    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)
    return graph


def configure_get_actor_property(node, property_name, output_attr):
    settings = node.get_settings()
    settings.set_editor_property("property_name", property_name)
    settings.set_editor_property("always_requery_actors", True)
    settings.set_editor_property("sanitize_output_attribute_name", True)
    AXIS_CONFIG["DYNAMIC_CONFIG"]["selector_import"](settings, "output_attribute_name", output_attr)


def configure_attribute_filter_from_param(node, target_attr, threshold_attr):
    settings = node.get_settings()
    settings.set_editor_property("operator", unreal.PCGAttributeFilterOperator.EQUAL)
    settings.set_editor_property("use_constant_threshold", False)
    settings.set_editor_property("use_spatial_query", False)
    AXIS_CONFIG["DYNAMIC_CONFIG"]["selector_import"](settings, "target_attribute", target_attr)
    AXIS_CONFIG["DYNAMIC_CONFIG"]["selector_import"](settings, "threshold_attribute", threshold_attr)
    settings.set_editor_property("warn_on_data_missing_attribute", True)
    settings.set_editor_property("generate_output_data_even_if_empty", True)


def compat_specs():
    return [
        spec for spec in AXIS_CONFIG["MATERIAL_CONFIG"]["MATERIAL_OVERRIDE_SPECS"]
        if int(spec["variant_type"]) in INCLUDED_VARIANTS
    ]


def point_spec_for_single_point(spec, point_index):
    domain_type = int(spec["domain_type"])
    variant_type = int(spec["variant_type"])
    x_offset = AXIS_CONFIG["DOMAIN_X_OFFSETS"][domain_type]
    y_offset = AXIS_CONFIG["VARIANT_Y_OFFSETS"][variant_type] + point_index * AXIS_CONFIG["ENTRY_Y_SPACING"]
    source_offset = spec["point_offsets"][point_index]
    return dict(
        spec,
        point_offsets=AXIS_CONFIG["shift_offsets"]([source_offset], x_offset, y_offset),
    )


def add_soft_path_attr(graph, upstream, title, attr_name, soft_path, x, y):
    node = AXIS_CONFIG["DYNAMIC_CONFIG"]["add_node"](graph, unreal.PCGAddAttributeSettings, title, x, y)
    AXIS_CONFIG["DYNAMIC_CONFIG"]["configure_add"](
        node,
        attr_name,
        "@Last",
        unreal.PCGMetadataTypes.SOFT_OBJECT_PATH,
        soft_path,
    )
    graph.add_edge(upstream, "Out", node, "In")
    return node


def add_bool_attr(graph, upstream, title, attr_name, value, x, y):
    node = AXIS_CONFIG["DYNAMIC_CONFIG"]["add_node"](graph, unreal.PCGAddAttributeSettings, title, x, y)
    AXIS_CONFIG["DYNAMIC_CONFIG"]["configure_add"](
        node,
        attr_name,
        "@Last",
        unreal.PCGMetadataTypes.BOOLEAN,
        value,
    )
    graph.add_edge(upstream, "Out", node, "In")
    return node


def non_empty_materials(entry_spec):
    return [path for path in entry_spec["override_material_paths"] if path]


def compat_branch_label(spec, entry_spec, point_index):
    return f"{spec['domain_name']}_{spec['variant_name']}_{point_index}_{entry_spec['mesh_key']}"


def add_compat_point_branch(graph, spec, point_index, branch_index):
    entry_spec = spec["entries"][point_index % len(spec["entries"])]
    y = branch_index * 260.0
    label = compat_branch_label(spec, entry_spec, point_index)
    source = AXIS_CONFIG["DYNAMIC_CONFIG"]["add_node"](
        graph,
        unreal.PCGCreatePointsSettings,
        f"{label} Point",
        -2600,
        y,
    )
    AXIS_CONFIG["MATERIAL_CONFIG"]["configure_points"](source, point_spec_for_single_point(spec, point_index))
    current = AXIS_CONFIG["MATERIAL_CONFIG"]["add_material_markers"](graph, source, spec, -2220, y)
    current = add_soft_path_attr(
        graph,
        current,
        f"{AXIS_CONFIG['DYNAMIC_CONFIG']['DYNAMIC_MESH_ATTR']} {label}",
        AXIS_CONFIG["DYNAMIC_CONFIG"]["DYNAMIC_MESH_ATTR"],
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
        f"{AXIS_CONFIG['DYNAMIC_CONFIG']['DYNAMIC_MATERIAL_SLOT0_ATTR']} {label}",
        AXIS_CONFIG["DYNAMIC_CONFIG"]["DYNAMIC_MATERIAL_SLOT0_ATTR"],
        slot0,
        620,
        y,
    )
    current = add_soft_path_attr(
        graph,
        current,
        f"{AXIS_CONFIG['DYNAMIC_CONFIG']['DYNAMIC_MATERIAL_SLOT1_ATTR']} {label}",
        AXIS_CONFIG["DYNAMIC_CONFIG"]["DYNAMIC_MATERIAL_SLOT1_ATTR"],
        slot1,
        940,
        y,
    )
    current = add_bool_attr(
        graph,
        current,
        f"{AXIS_CONFIG['DYNAMIC_AXIS_PASS_ATTR']} {label}",
        AXIS_CONFIG["DYNAMIC_AXIS_PASS_ATTR"],
        True,
        1260,
        y,
    )
    return current


def expected_rows():
    rows = []
    for spec in compat_specs():
        for point_index, _ in enumerate(spec["point_offsets"]):
            entry_spec = spec["entries"][point_index % len(spec["entries"])]
            rows.append({
                "domain_name": spec["domain_name"],
                "domain_type": spec["domain_type"],
                "variant_name": spec["variant_name"],
                "variant_type": spec["variant_type"],
                "mesh_key": entry_spec["mesh_key"],
                "mesh_path": entry_spec["mesh_path"],
                "materials": non_empty_materials(entry_spec),
                "expected_instance_count": 1,
                "point_index": point_index,
            })
    return rows


def selected_expected_rows():
    return [
        row for row in expected_rows()
        if int(row["domain_type"]) == SELECTED_DOMAIN_TYPE
        and int(row["variant_type"]) == SELECTED_VARIANT_TYPE
    ]


def build_graph():
    graph = ensure_graph()
    branch_nodes = []
    branch_index = 0
    for spec in compat_specs():
        for point_index, _ in enumerate(spec["point_offsets"]):
            branch_nodes.append(add_compat_point_branch(graph, spec, point_index, branch_index))
            branch_index += 1

    domain_property = AXIS_CONFIG["DYNAMIC_CONFIG"]["add_node"](
        graph,
        unreal.PCGGetActorPropertySettings,
        f"Get Actor {DOMAIN_PROPERTY}",
        1600,
        -260,
    )
    variant_property = AXIS_CONFIG["DYNAMIC_CONFIG"]["add_node"](
        graph,
        unreal.PCGGetActorPropertySettings,
        f"Get Actor {VARIANT_PROPERTY}",
        1920,
        -260,
    )
    domain_filter = AXIS_CONFIG["DYNAMIC_CONFIG"]["add_node"](
        graph,
        unreal.PCGAttributeFilteringSettings,
        f"Filter {DOMAIN_ATTR} == ${SELECTED_DOMAIN_ATTR}",
        1660,
        420,
    )
    variant_filter = AXIS_CONFIG["DYNAMIC_CONFIG"]["add_node"](
        graph,
        unreal.PCGAttributeFilteringSettings,
        f"Filter {VARIANT_ATTR} == ${SELECTED_VARIANT_ATTR}",
        1980,
        420,
    )
    spawner = AXIS_CONFIG["DYNAMIC_CONFIG"]["add_node"](
        graph,
        unreal.PCGStaticMeshSpawnerSettings,
        "Spawn Compat Actor Property Dynamic Material Axis",
        2320,
        420,
    )

    configure_get_actor_property(domain_property, DOMAIN_PROPERTY, SELECTED_DOMAIN_ATTR)
    configure_get_actor_property(variant_property, VARIANT_PROPERTY, SELECTED_VARIANT_ATTR)
    configure_attribute_filter_from_param(domain_filter, DOMAIN_ATTR, SELECTED_DOMAIN_ATTR)
    configure_attribute_filter_from_param(variant_filter, VARIANT_ATTR, SELECTED_VARIANT_ATTR)
    AXIS_CONFIG["DYNAMIC_CONFIG"]["configure_by_attribute_spawner"](spawner)

    for branch_node in branch_nodes:
        graph.add_edge(branch_node, "Out", domain_filter, "In")
    graph.add_edge(domain_property, "Out", domain_filter, "Filter")
    graph.add_edge(domain_filter, "InsideFilter", variant_filter, "In")
    graph.add_edge(variant_property, "Out", variant_filter, "Filter")
    graph.add_edge(variant_filter, "InsideFilter", spawner, "In")
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

    actor_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not actor_class:
        raise RuntimeError(f"Missing material override selector Blueprint class: {BLUEPRINT_CLASS_PATH}")

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(107000, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(ACTOR_LABEL)
    actor.set_editor_property(DOMAIN_PROPERTY, SELECTED_DOMAIN_TYPE)
    actor.set_editor_property(VARIANT_PROPERTY, SELECTED_VARIANT_TYPE)

    components = actor.get_components_by_class(unreal.PCGComponent)
    if not components:
        raise RuntimeError(f"Selector validation actor has no PCGComponent: {ACTOR_LABEL}")
    component = components[0]
    component.set_graph(graph)
    component.cleanup(True)
    component.generate(True)
    component.generate(True)
    return actor


def main():
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_ACTOR_PROPERTY_COMPAT_BUILD_BEGIN")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    AXIS_CONFIG["MATERIAL_CONFIG"]["ensure_material_variants"]()
    graph = build_graph()
    actor = spawn_validation_actor(graph)
    rows = selected_expected_rows()
    expected_total = sum(row["expected_instance_count"] for row in rows)
    all_rows = expected_rows()
    all_total = sum(row["expected_instance_count"] for row in all_rows)
    print(f"dynamic_material_axis_actor_property_compat_graph={graph.get_path_name()}")
    print("dynamic_material_axis_actor_property_compat_graph_count=1")
    print(f"dynamic_material_axis_actor_property_compat_actor={actor.get_actor_label()}")
    print("dynamic_material_axis_actor_property_compat_actor_count=1")
    print(f"dynamic_material_axis_actor_property_compat_all_row_count={len(all_rows)}")
    print(f"dynamic_material_axis_actor_property_compat_all_expected_points={all_total}")
    print(f"dynamic_material_axis_actor_property_compat_selected_domain={actor.get_editor_property(DOMAIN_PROPERTY)}")
    print(f"dynamic_material_axis_actor_property_compat_selected_variant={actor.get_editor_property(VARIANT_PROPERTY)}")
    print(f"dynamic_material_axis_actor_property_compat_expected_row_count={len(rows)}")
    print(f"dynamic_material_axis_actor_property_compat_expected_points={expected_total}")
    print(f"dynamic_material_axis_actor_property_compat_expected_ism={expected_total}")
    for row in rows:
        print(f"expected_row={row}")
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_ACTOR_PROPERTY_COMPAT_BUILD_END")


if __name__ == "__main__":
    main()
