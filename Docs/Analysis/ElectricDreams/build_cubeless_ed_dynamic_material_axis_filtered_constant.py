import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\build_cubeless_ed_dynamic_material_axis_filtered_constant.py",
    )
).parent
AXIS_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_dynamic_material_axis_by_point.py"

PACKAGE = "/Game/Cubeless/PCG/ElectricDreamsLearning/DynamicMaterialPrototype"
GRAPH_ASSET = "PCG_Cubeless_ED_DynamicMaterialAxis_FilteredConstant_GroundFoliage_CoolLeaf"
GRAPH_PATH = f"{PACKAGE}/{GRAPH_ASSET}.{GRAPH_ASSET}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_Cubeless_ED_DynamicMaterialAxis_FilteredConstant_GroundFoliage_CoolLeaf_Validation"

DOMAIN_ATTR = "DesignerMaterialDomainType"
VARIANT_ATTR = "DesignerMaterialVariantType"
SELECTED_DOMAIN_TYPE = 1
SELECTED_VARIANT_TYPE = 2


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
        raise RuntimeError(f"Failed to create/load filtered constant graph: {GRAPH_PATH}")
    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)
    return graph


def configure_attribute_filter_constant(node, attr, threshold):
    settings = node.get_settings()
    settings.set_editor_property("operator", unreal.PCGAttributeFilterOperator.EQUAL)
    settings.set_editor_property("use_constant_threshold", True)
    AXIS_CONFIG["DYNAMIC_CONFIG"]["selector_import"](settings, "target_attribute", attr)
    AXIS_CONFIG["DYNAMIC_CONFIG"]["selector_import"](settings, "threshold_attribute", attr)
    value_struct = settings.get_editor_property("attribute_types")
    AXIS_CONFIG["DYNAMIC_CONFIG"]["set_const_value_struct"](
        value_struct,
        unreal.PCGMetadataTypes.INTEGER32,
        int(threshold),
    )
    settings.set_editor_property("attribute_types", value_struct)
    settings.set_editor_property("warn_on_data_missing_attribute", True)
    settings.set_editor_property("generate_output_data_even_if_empty", True)


def selected_expected_rows():
    return [
        row for row in AXIS_CONFIG["expected_rows"]()
        if int(row["domain_type"]) == SELECTED_DOMAIN_TYPE
        and int(row["variant_type"]) == SELECTED_VARIANT_TYPE
    ]


def build_graph():
    graph = ensure_graph()
    branch_nodes = []
    branch_index = 0
    for spec in AXIS_CONFIG["dynamic_specs"]():
        for entry_index, entry_spec in enumerate(spec["entries"]):
            branch_nodes.append(
                AXIS_CONFIG["add_dynamic_entry_branch"](graph, spec, entry_spec, entry_index, branch_index)
            )
            branch_index += 1

    domain_filter = AXIS_CONFIG["DYNAMIC_CONFIG"]["add_node"](
        graph,
        unreal.PCGAttributeFilteringSettings,
        f"Filter {DOMAIN_ATTR} == {SELECTED_DOMAIN_TYPE}",
        1660,
        420,
    )
    variant_filter = AXIS_CONFIG["DYNAMIC_CONFIG"]["add_node"](
        graph,
        unreal.PCGAttributeFilteringSettings,
        f"Filter {VARIANT_ATTR} == {SELECTED_VARIANT_TYPE}",
        1980,
        420,
    )
    spawner = AXIS_CONFIG["DYNAMIC_CONFIG"]["add_node"](
        graph,
        unreal.PCGStaticMeshSpawnerSettings,
        "Spawn Filtered ByAttribute Dynamic Material Axis",
        2320,
        420,
    )

    configure_attribute_filter_constant(domain_filter, DOMAIN_ATTR, SELECTED_DOMAIN_TYPE)
    configure_attribute_filter_constant(variant_filter, VARIANT_ATTR, SELECTED_VARIANT_TYPE)
    AXIS_CONFIG["DYNAMIC_CONFIG"]["configure_by_attribute_spawner"](spawner)

    for branch_node in branch_nodes:
        graph.add_edge(branch_node, "Out", domain_filter, "In")
    graph.add_edge(domain_filter, "InsideFilter", variant_filter, "In")
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
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PCGVolume,
        unreal.Vector(104000, 0, 0),
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
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_FILTERED_CONSTANT_BUILD_BEGIN")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    AXIS_CONFIG["MATERIAL_CONFIG"]["ensure_material_variants"]()
    graph = build_graph()
    actor = spawn_validation_actor(graph)
    rows = selected_expected_rows()
    expected_total = sum(row["expected_instance_count"] for row in rows)
    print(f"dynamic_material_axis_filtered_constant_graph={graph.get_path_name()}")
    print("dynamic_material_axis_filtered_constant_graph_count=1")
    print(f"dynamic_material_axis_filtered_constant_actor={actor.get_actor_label()}")
    print("dynamic_material_axis_filtered_constant_actor_count=1")
    print(f"dynamic_material_axis_filtered_constant_selected_domain={SELECTED_DOMAIN_TYPE}")
    print(f"dynamic_material_axis_filtered_constant_selected_variant={SELECTED_VARIANT_TYPE}")
    print(f"dynamic_material_axis_filtered_constant_expected_row_count={len(rows)}")
    print(f"dynamic_material_axis_filtered_constant_expected_points={expected_total}")
    print(f"dynamic_material_axis_filtered_constant_expected_ism={expected_total}")
    for row in rows:
        print(f"expected_row={row}")
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_FILTERED_CONSTANT_BUILD_END")


if __name__ == "__main__":
    main()
