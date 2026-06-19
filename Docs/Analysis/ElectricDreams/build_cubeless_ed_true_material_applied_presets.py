import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "build_cubeless_ed_true_material_applied_presets.py",
    )
).parent
STYLE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_style_profile_matrix_presets.py"
TREE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_tree_profile_presets.py"
MATERIAL_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_material_override_presets.py"

TRUE_MATERIAL_ROOT = "/Game/Cubeless/PCG/ElectricDreamsLearning/TrueMaterialApplied"
TRUE_STYLE_AMOUNT_PACKAGE = f"{TRUE_MATERIAL_ROOT}/StyleAmountPresets"
TRUE_STYLE_MATRIX_PACKAGE = f"{TRUE_MATERIAL_ROOT}/DesignerStyleProfileMatrixCombos"
TRUE_TREE_PROFILE_PACKAGE = f"{TRUE_MATERIAL_ROOT}/TreeProfilePresets"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_TrueMaterialApplied"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0
DYNAMIC_MESH_ATTR = "DynamicMeshPath"
OVERRIDE_TRUE_ATTR = "MeshOverrideTrue"

STYLE_DOMAIN_BY_STYLE_TYPE = {
    4: 1,
    5: 2,
}
TREE_DOMAIN_BY_STYLE_TYPE = {
    1: 3,
    2: 3,
    3: 3,
}


def load_config(script_path, namespace_name):
    namespace = {"__name__": namespace_name, "__file__": str(script_path)}
    with open(script_path, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(script_path), "exec")
    exec(code, namespace)
    return namespace


STYLE_CONFIG = load_config(STYLE_BUILDER_SCRIPT, "_cubeless_ed_style_profile_matrix_presets_config")
TREE_CONFIG = load_config(TREE_BUILDER_SCRIPT, "_cubeless_ed_tree_profile_presets_config")
MATERIAL_CONFIG = load_config(MATERIAL_BUILDER_SCRIPT, "_cubeless_ed_material_override_presets_config")


def true_material_variant_name(domain_type, variant_type):
    return MATERIAL_CONFIG["VARIANT_NAMES"].get((int(domain_type), int(variant_type)))


def base_without_prefix(asset_name):
    return asset_name.replace("PCG_Cubeless_ED_", "", 1)


def true_style_amount_asset_name(profile_key, amount, style, variant_type):
    domain_type = STYLE_DOMAIN_BY_STYLE_TYPE[style["style_type"]]
    variant_name = true_material_variant_name(domain_type, variant_type)
    return f"PCG_Cubeless_ED_TrueMaterial_{variant_name}_{profile_key}Amount_{amount['short_name']}_{style['name']}"


def true_style_amount_graph_path(profile_key, amount, style, variant_type):
    asset_name = true_style_amount_asset_name(profile_key, amount, style, variant_type)
    return f"{TRUE_STYLE_AMOUNT_PACKAGE}/{asset_name}.{asset_name}"


def true_style_matrix_asset_name(style_matrix_spec, variant_type):
    domain_type = STYLE_DOMAIN_BY_STYLE_TYPE[style_matrix_spec["style_type"]]
    variant_name = true_material_variant_name(domain_type, variant_type)
    return f"PCG_Cubeless_ED_TrueMaterial_{variant_name}_{base_without_prefix(style_matrix_spec['asset_name'])}"


def true_style_matrix_graph_path(style_matrix_spec, variant_type):
    asset_name = true_style_matrix_asset_name(style_matrix_spec, variant_type)
    return f"{TRUE_STYLE_MATRIX_PACKAGE}/{asset_name}.{asset_name}"


def true_tree_asset_name(tree_spec, variant_type):
    domain_type = TREE_DOMAIN_BY_STYLE_TYPE[tree_spec["style_type"]]
    variant_name = true_material_variant_name(domain_type, variant_type)
    return f"PCG_Cubeless_ED_TrueMaterial_{variant_name}_{base_without_prefix(tree_spec['asset_name'])}"


def true_tree_graph_path(tree_spec, variant_type):
    asset_name = true_tree_asset_name(tree_spec, variant_type)
    return f"{TRUE_TREE_PROFILE_PACKAGE}/{asset_name}.{asset_name}"


def material_override_map_for_style(style, variant_type):
    mesh_paths = MATERIAL_CONFIG["MESH_PATHS"]
    material_path = MATERIAL_CONFIG["material_variant_path"]
    style_type = int(style["style_type"])
    if style_type == 4:
        if int(variant_type) == 2:
            return {
                mesh_paths["fern"]: [material_path("fern_cool")],
                mesh_paths["ground_leaf"]: [material_path("ground_leaf_cool")],
            }
        return {
            mesh_paths["fern"]: [material_path("fern_warm")],
            mesh_paths["ground_leaf"]: [material_path("ground_leaf_warm")],
        }
    if style_type == 5:
        key = "rock_cool" if int(variant_type) == 2 else "rock_dark"
        return {
            mesh_paths["small_rock_01"]: [material_path(key)],
            mesh_paths["small_rock_02"]: [material_path(key)],
        }
    raise RuntimeError(f"Unsupported true material style type: {style_type}")


def material_override_map_for_tree(tree_spec, variant_type):
    material_path = MATERIAL_CONFIG["material_variant_path"]
    if int(variant_type) == 2:
        leaf_material = material_path("pine_leaves_dark")
        bark_material = material_path("pine_bark_dark")
    else:
        leaf_material = material_path("pine_leaves_soft")
        bark_material = material_path("pine_bark_soft")

    override_map = {}
    for mesh_path in tree_spec["mesh_paths"]:
        if "SM_Conifer_05." in mesh_path:
            override_map[mesh_path] = [leaf_material, bark_material]
        elif "SM_Conifer_08." in mesh_path or "SM_Conifer_09." in mesh_path:
            override_map[mesh_path] = [bark_material]
        else:
            raise RuntimeError(f"Unsupported true material tree mesh: {mesh_path}")
    return override_map


def true_material_marker_values(domain_type, variant_type):
    return {
        "domain_id": MATERIAL_CONFIG["DOMAIN_SPECS"][domain_type]["domain_id"],
        "domain_type": int(domain_type),
        "variant_id": 710 + int(variant_type),
        "variant_type": int(variant_type),
        "override_id": MATERIAL_CONFIG["material_override_id"](domain_type, variant_type),
        "override_type": MATERIAL_CONFIG["material_override_type"](domain_type, variant_type),
        "override_mode": 1,
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


def ensure_graph(package_path, asset_name):
    unreal.EditorAssetLibrary.make_directory(package_path)
    graph_path = f"{package_path}/{asset_name}.{asset_name}"
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            asset_name,
            package_path,
            unreal.PCGGraph.static_class(),
            unreal.PCGGraphFactory(),
        )
    if not graph:
        raise RuntimeError(f"Failed to create/load graph: {graph_path}")
    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)
    return graph


def add_true_material_markers(graph, upstream, domain_type, variant_type, x, y):
    values = true_material_marker_values(domain_type, variant_type)
    marker_specs = [
        ("DesignerMaterialDomainId", unreal.PCGMetadataTypes.INTEGER32, values["domain_id"]),
        ("DesignerMaterialDomainType", unreal.PCGMetadataTypes.INTEGER32, values["domain_type"]),
        ("DesignerMaterialVariantId", unreal.PCGMetadataTypes.INTEGER32, values["variant_id"]),
        ("DesignerMaterialVariantType", unreal.PCGMetadataTypes.INTEGER32, values["variant_type"]),
        ("DesignerMaterialOverrideId", unreal.PCGMetadataTypes.INTEGER32, values["override_id"]),
        ("DesignerMaterialOverrideType", unreal.PCGMetadataTypes.INTEGER32, values["override_type"]),
        ("DesignerMaterialOverrideMode", unreal.PCGMetadataTypes.INTEGER32, values["override_mode"]),
        ("DesignerMaterialOverridePass", unreal.PCGMetadataTypes.BOOLEAN, True),
        ("DesignerTrueMaterialAppliedPass", unreal.PCGMetadataTypes.BOOLEAN, True),
    ]
    current = upstream
    for index, (attr_name, attr_type, value) in enumerate(marker_specs):
        node = add_node(graph, unreal.PCGAddAttributeSettings, f"{attr_name} {value}", x + index * 280, y)
        STYLE_CONFIG["configure_add"](node, attr_name, "@Last", attr_type, value)
        graph.add_edge(current, "Out", node, "In")
        current = node
    return current


def configure_spawner_with_overrides(node, mesh_paths, override_map):
    settings = node.get_settings()
    try:
        settings.set_editor_property("allow_descriptor_changes", True)
    except Exception:
        pass
    entries = []
    for mesh_path in mesh_paths:
        mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        if not mesh:
            raise RuntimeError(f"Missing mesh for true material spawner: {mesh_path}")
        descriptor = unreal.PCGSoftISMComponentDescriptor()
        descriptor.set_editor_property("static_mesh", mesh)
        override_materials = []
        for material_path in override_map.get(mesh_path, []):
            material = unreal.EditorAssetLibrary.load_asset(material_path)
            if not material:
                raise RuntimeError(f"Missing true material override: {material_path}")
            override_materials.append(material)
        descriptor.set_editor_property("override_materials", override_materials)
        entry = unreal.PCGMeshSelectorWeightedEntry()
        entry.set_editor_property("descriptor", descriptor)
        entry.set_editor_property("weight", 1)
        entries.append(entry)
    params = settings.get_editor_property("mesh_selector_parameters")
    params.set_editor_property("mesh_entries", entries)


def selector_import(settings, prop, text):
    selector = settings.get_editor_property(prop)
    selector.import_text(f"PCGBegin({text})PCGEnd")
    settings.set_editor_property(prop, selector)


def configure_get_actor_property(node, property_name, output_attr):
    settings = node.get_settings()
    settings.set_editor_property("property_name", property_name)
    settings.set_editor_property("always_requery_actors", True)
    settings.set_editor_property("sanitize_output_attribute_name", True)
    selector_import(settings, "output_attribute_name", output_attr)


def configure_actor_bool_filter(node, use_property_name):
    settings = node.get_settings()
    settings.set_editor_property("operator", unreal.PCGAttributeFilterOperator.EQUAL)
    settings.set_editor_property("use_constant_threshold", False)
    settings.set_editor_property("use_spatial_query", False)
    selector_import(settings, "target_attribute", OVERRIDE_TRUE_ATTR)
    selector_import(settings, "threshold_attribute", use_property_name)
    settings.set_editor_property("warn_on_data_missing_attribute", False)
    settings.set_editor_property("generate_output_data_even_if_empty", True)


def configure_copy_actor_mesh(node, source_attr, target_attr=DYNAMIC_MESH_ATTR):
    settings = node.get_settings()
    settings.set_editor_property("copy_all_attributes", False)
    settings.set_editor_property("copy_all_domains", False)
    selector_import(settings, "input_source", source_attr)
    selector_import(settings, "output_target", target_attr)


def configure_by_attribute_spawner(node):
    settings = node.get_settings()
    settings.set_editor_property("allow_descriptor_changes", True)
    settings.set_mesh_selector_type(unreal.PCGMeshSelectorByAttribute.static_class())
    params = settings.get_editor_property("mesh_selector_parameters")
    params.set_editor_property("attribute_name", DYNAMIC_MESH_ATTR)
    params.set_editor_property("use_attribute_material_overrides", False)
    params.set_editor_property("material_override_attributes", [])


def add_true_material_mesh_override_switch(
    graph,
    upstream,
    domain_name,
    use_property,
    mesh_property,
    mesh_paths,
    override_map,
    x,
    y,
):
    flag = add_node(graph, unreal.PCGAddAttributeSettings, f"{domain_name} Override Flag True", x, y)
    STYLE_CONFIG["configure_add"](
        flag,
        OVERRIDE_TRUE_ATTR,
        "@Last",
        unreal.PCGMetadataTypes.BOOLEAN,
        True,
    )

    get_use = add_node(graph, unreal.PCGGetActorPropertySettings, f"Get Actor {use_property}", x, y - 280)
    configure_get_actor_property(get_use, use_property, use_property)

    split = add_node(graph, unreal.PCGAttributeFilteringSettings, f"Split {domain_name} Mesh Override", x + 340, y)
    configure_actor_bool_filter(split, use_property)

    original_spawner = add_node(
        graph,
        unreal.PCGStaticMeshSpawnerSettings,
        f"Spawn {domain_name} TrueMaterial Default",
        x + 700,
        y + 120,
    )
    configure_spawner_with_overrides(original_spawner, mesh_paths, override_map)

    get_mesh = add_node(graph, unreal.PCGGetActorPropertySettings, f"Get Actor {mesh_property}", x + 700, y - 280)
    configure_get_actor_property(get_mesh, mesh_property, mesh_property)

    copy_mesh = add_node(
        graph,
        unreal.PCGCopyAttributesSettings,
        f"Copy {mesh_property} To {DYNAMIC_MESH_ATTR}",
        x + 1040,
        y - 120,
    )
    configure_copy_actor_mesh(copy_mesh, mesh_property, DYNAMIC_MESH_ATTR)

    override_spawner = add_node(
        graph,
        unreal.PCGStaticMeshSpawnerSettings,
        f"Spawn {domain_name} ByActorMeshOverride",
        x + 1380,
        y - 120,
    )
    configure_by_attribute_spawner(override_spawner)

    merge = add_node(graph, unreal.PCGMergeSettings, f"Merge {domain_name} Mesh Override Result", x + 1760, y)

    graph.add_edge(upstream, "Out", flag, "In")
    graph.add_edge(flag, "Out", split, "In")
    graph.add_edge(get_use, "Out", split, "Filter")
    graph.add_edge(split, "OutsideFilter", original_spawner, "In")
    graph.add_edge(split, "InsideFilter", copy_mesh, "Target")
    graph.add_edge(get_mesh, "Out", copy_mesh, "Source")
    graph.add_edge(copy_mesh, "Out", override_spawner, "In")
    graph.add_edge(original_spawner, "Out", merge, "In")
    graph.add_edge(override_spawner, "Out", merge, "In")
    return merge


def build_true_style_amount_graph(profile_key, amount, style, variant_type):
    asset_name = true_style_amount_asset_name(profile_key, amount, style, variant_type)
    graph = ensure_graph(TRUE_STYLE_AMOUNT_PACKAGE, asset_name)

    source = add_node(graph, unreal.PCGSubgraphSettings, f"{amount['name']} Core", -1700, 0)
    STYLE_CONFIG["configure_subgraph"](source, amount["core_graph_path"])
    graph.add_edge(graph.get_input_node(), "In", source, "In")
    upstream = source
    x = -1320

    if amount["density_filter"]:
        lower, upper = amount["density_filter"]
        density_filter = add_node(graph, unreal.PCGDensityFilterSettings, f"Density {lower}-{upper}", x, 0)
        STYLE_CONFIG["configure_density_filter"](density_filter, lower, upper)
        graph.add_edge(upstream, "Out", density_filter, "In")
        upstream = density_filter
        x += 320

    if amount["duplicate_iterations"] > 0:
        duplicate = add_node(graph, unreal.PCGDuplicatePointSettings, f"Duplicate x{amount['duplicate_iterations']}", x, 0)
        STYLE_CONFIG["configure_duplicate"](duplicate, amount["duplicate_iterations"], amount["duplicate_offset"])
        graph.add_edge(upstream, "Out", duplicate, "In")
        upstream = duplicate
        x += 320

    markers = STYLE_CONFIG["add_profile_amount_style_markers"](graph, upstream, amount, style, x, 0)
    domain_type = STYLE_DOMAIN_BY_STYLE_TYPE[style["style_type"]]
    material_markers = add_true_material_markers(graph, markers, domain_type, variant_type, x + 2240, 0)
    style_type = int(style["style_type"])
    domain_name = "Rock" if style_type == 5 else "Grass"
    use_property = "UseRockMeshOverride" if style_type == 5 else "UseGrassMeshOverride"
    mesh_property = "RockMeshOverride" if style_type == 5 else "GrassMeshOverride"
    merged = add_true_material_mesh_override_switch(
        graph,
        material_markers,
        domain_name,
        use_property,
        mesh_property,
        style["mesh_paths"],
        material_override_map_for_style(style, variant_type),
        x + 5000,
        0,
    )
    graph.add_edge(merged, "Out", graph.get_output_node(), "Out")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def true_style_subgraph_paths(style_matrix_spec, variant_type):
    style = next(
        item for item in STYLE_CONFIG["STYLE_SPECS"]
        if item["style_type"] == style_matrix_spec["style_type"]
    )
    subgraphs = []
    if style_matrix_spec["profile_mode"] in (1, 3):
        amount = next(
            item for item in STYLE_CONFIG["GROUND_AMOUNT_SPECS"]
            if item["amount_type"] == style_matrix_spec["ground_amount_type"]
        )
        subgraphs.append(true_style_amount_graph_path("Ground", amount, style, variant_type))
    if style_matrix_spec["profile_mode"] in (2, 3):
        amount = next(
            item for item in STYLE_CONFIG["DITCH_AMOUNT_SPECS"]
            if item["amount_type"] == style_matrix_spec["ditch_amount_type"]
        )
        subgraphs.append(true_style_amount_graph_path("Ditch", amount, style, variant_type))
    return subgraphs


def build_true_style_matrix_graph(style_matrix_spec, variant_type):
    asset_name = true_style_matrix_asset_name(style_matrix_spec, variant_type)
    graph = ensure_graph(TRUE_STYLE_MATRIX_PACKAGE, asset_name)
    source_nodes = []
    for index, subgraph_path in enumerate(true_style_subgraph_paths(style_matrix_spec, variant_type)):
        source = add_node(
            graph,
            unreal.PCGSubgraphSettings,
            f"{style_matrix_spec['name']} TrueMaterial Source {index + 1}",
            -1200,
            index * 260,
        )
        STYLE_CONFIG["configure_subgraph"](source, subgraph_path)
        graph.add_edge(graph.get_input_node(), "In", source, "In")
        source_nodes.append(source)

    if len(source_nodes) == 1:
        upstream = source_nodes[0]
    else:
        merge = add_node(graph, unreal.PCGMergeSettings, f"{style_matrix_spec['name']} Merge", -820, 120)
        for source in source_nodes:
            graph.add_edge(source, "Out", merge, "In")
        upstream = merge

    style_markers = STYLE_CONFIG["add_style_profile_matrix_markers"](graph, upstream, style_matrix_spec, -460, 0)
    domain_type = STYLE_DOMAIN_BY_STYLE_TYPE[style_matrix_spec["style_type"]]
    material_markers = add_true_material_markers(graph, style_markers, domain_type, variant_type, 2060, 0)
    graph.add_edge(material_markers, "Out", graph.get_output_node(), "Out")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def build_true_tree_graph(tree_spec, variant_type):
    asset_name = true_tree_asset_name(tree_spec, variant_type)
    graph = ensure_graph(TRUE_TREE_PROFILE_PACKAGE, asset_name)
    source = add_node(graph, unreal.PCGCreatePointsSettings, f"{tree_spec['name']} Tree Points", -1200, 0)
    TREE_CONFIG["configure_points"](source, tree_spec)
    tree_markers = TREE_CONFIG["add_tree_markers"](graph, source, tree_spec, -820, 0)
    domain_type = TREE_DOMAIN_BY_STYLE_TYPE[tree_spec["style_type"]]
    material_markers = add_true_material_markers(graph, tree_markers, domain_type, variant_type, 2600, 0)
    merged = add_true_material_mesh_override_switch(
        graph,
        material_markers,
        "Tree",
        "UseTreeMeshOverride",
        "TreeMeshOverride",
        tree_spec["mesh_paths"],
        material_override_map_for_tree(tree_spec, variant_type),
        5300,
        0,
    )
    graph.add_edge(merged, "Out", graph.get_output_node(), "Out")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


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


def spawn_validation_actor(label, graph, index, needs_spline):
    for actor in list(get_all_level_actors()):
        if actor.get_actor_label() == label:
            unreal.EditorLevelLibrary.destroy_actor(actor)
    if needs_spline:
        actor_class = unreal.load_class(None, STYLE_CONFIG["VALIDATION_BLUEPRINT_CLASS_PATH"])
        if not actor_class:
            raise RuntimeError(f"Missing validation actor class: {STYLE_CONFIG['VALIDATION_BLUEPRINT_CLASS_PATH']}")
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            actor_class,
            unreal.Vector(76000 + (index % 4) * 900, (index // 4) * 900, 0),
            unreal.Rotator(0, 0, 0),
        )
        configure_validation_spline(actor)
        pcg_components = actor.get_components_by_class(unreal.PCGComponent)
        if not pcg_components:
            raise RuntimeError(f"Validation actor has no PCGComponent: {label}")
        component = pcg_components[0]
    else:
        actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
            unreal.PCGVolume,
            unreal.Vector(76000 + (index % 4) * 900, (index // 4) * 900, 0),
            unreal.Rotator(0, 0, 0),
        )
        component = actor.pcg_component
    actor.set_actor_label(label)
    component.set_graph(graph)
    component.cleanup(True)
    component.generate(True)
    component.generate(True)
    return actor


def make_style_matrix_specs():
    specs = []
    for style_matrix_spec in STYLE_CONFIG["STYLE_PROFILE_MATRIX_SPECS"]:
        if style_matrix_spec["style_type"] not in STYLE_DOMAIN_BY_STYLE_TYPE:
            continue
        for variant_type in (2, 3):
            domain_type = STYLE_DOMAIN_BY_STYLE_TYPE[style_matrix_spec["style_type"]]
            specs.append({
                "kind": "style",
                "name": f"{style_matrix_spec['name']}_{true_material_variant_name(domain_type, variant_type)}",
                "asset_name": true_style_matrix_asset_name(style_matrix_spec, variant_type),
                "graph_path": true_style_matrix_graph_path(style_matrix_spec, variant_type),
                "style_matrix_spec": style_matrix_spec,
                "domain_type": domain_type,
                "variant_type": variant_type,
                "expected_points": style_matrix_spec["expected_points"],
                "expected_ism": style_matrix_spec["expected_ism"],
                "expected_override_map": material_override_map_for_style(
                    next(
                        item for item in STYLE_CONFIG["STYLE_SPECS"]
                        if item["style_type"] == style_matrix_spec["style_type"]
                    ),
                    variant_type,
                ),
                "subgraph_paths": true_style_subgraph_paths(style_matrix_spec, variant_type),
            })
    return specs


def make_tree_specs():
    specs = []
    for tree_spec in TREE_CONFIG["TREE_PROFILE_SPECS"]:
        if tree_spec["style_type"] not in TREE_DOMAIN_BY_STYLE_TYPE:
            continue
        for variant_type in (2, 3):
            domain_type = TREE_DOMAIN_BY_STYLE_TYPE[tree_spec["style_type"]]
            specs.append({
                "kind": "tree",
                "name": f"{tree_spec['name']}_{true_material_variant_name(domain_type, variant_type)}",
                "asset_name": true_tree_asset_name(tree_spec, variant_type),
                "graph_path": true_tree_graph_path(tree_spec, variant_type),
                "tree_spec": tree_spec,
                "domain_type": domain_type,
                "variant_type": variant_type,
                "expected_points": tree_spec["expected_points"],
                "expected_ism": tree_spec["expected_ism"],
                "expected_override_map": material_override_map_for_tree(tree_spec, variant_type),
            })
    return specs


TRUE_STYLE_MATRIX_SPECS = make_style_matrix_specs()
TRUE_TREE_SPECS = make_tree_specs()

VALIDATION_SPECS = [
    next(spec for spec in TRUE_STYLE_MATRIX_SPECS if spec["name"] == "GroundFoliage_Both_GroundNormal_DitchSparse_CoolLeaf"),
    next(spec for spec in TRUE_STYLE_MATRIX_SPECS if spec["name"] == "GroundFoliage_GroundOnly_GroundDense_WarmLeaf"),
    next(spec for spec in TRUE_STYLE_MATRIX_SPECS if spec["name"] == "SmallRocks_DitchOnly_DitchNormal_DarkRock"),
    next(spec for spec in TRUE_STYLE_MATRIX_SPECS if spec["name"] == "SmallRocks_GroundOnly_GroundSparse_CoolRock"),
    next(spec for spec in TRUE_TREE_SPECS if spec["name"] == "CompactConifer_Solo_DarkPine"),
    next(spec for spec in TRUE_TREE_SPECS if spec["name"] == "CompactConifer_Sparse_SoftPine"),
    next(spec for spec in TRUE_TREE_SPECS if spec["name"] == "ColumnConifer_Sparse_DarkPine"),
    next(spec for spec in TRUE_TREE_SPECS if spec["name"] == "MixedConifer_LightGrove_SoftPine"),
]


def main():
    print("MCP_CUBELESS_ED_TRUE_MATERIAL_APPLIED_BUILD_BEGIN")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    MATERIAL_CONFIG["ensure_material_variants"]()

    built_style_amount_paths = []
    for style in STYLE_CONFIG["STYLE_SPECS"]:
        if style["style_type"] not in STYLE_DOMAIN_BY_STYLE_TYPE:
            continue
        for variant_type in (2, 3):
            for amount in STYLE_CONFIG["GROUND_AMOUNT_SPECS"]:
                built_style_amount_paths.append(build_true_style_amount_graph("Ground", amount, style, variant_type).get_path_name())
            for amount in STYLE_CONFIG["DITCH_AMOUNT_SPECS"]:
                built_style_amount_paths.append(build_true_style_amount_graph("Ditch", amount, style, variant_type).get_path_name())

    built_style_matrix_paths = []
    for spec in TRUE_STYLE_MATRIX_SPECS:
        built_style_matrix_paths.append(
            build_true_style_matrix_graph(spec["style_matrix_spec"], spec["variant_type"]).get_path_name()
        )

    built_tree_paths = []
    for spec in TRUE_TREE_SPECS:
        built_tree_paths.append(build_true_tree_graph(spec["tree_spec"], spec["variant_type"]).get_path_name())

    for index, spec in enumerate(VALIDATION_SPECS):
        graph = unreal.EditorAssetLibrary.load_asset(spec["graph_path"])
        if not graph:
            raise RuntimeError(f"Missing true material validation graph: {spec['graph_path']}")
        label = f"{ACTOR_LABEL_PREFIX}_{spec['name']}_Validation"
        actor = spawn_validation_actor(label, graph, index, spec["kind"] == "style")
        print(f"validation_actor={actor.get_actor_label()}")
        print(f"  kind={spec['kind']}")
        print(f"  graph={spec['graph_path']}")
        print(f"  domain_type={spec['domain_type']}")
        print(f"  variant_type={spec['variant_type']}")
        print(f"  expected_points={spec['expected_points']}")
        print(f"  expected_ism={spec['expected_ism']}")
        print(f"  expected_override_map={spec['expected_override_map']}")

    print(f"true_material_style_amount_graph_count={len(built_style_amount_paths)}")
    print(f"true_material_style_matrix_graph_count={len(built_style_matrix_paths)}")
    print(f"true_material_tree_graph_count={len(built_tree_paths)}")
    print(f"true_material_validation_actor_count={len(VALIDATION_SPECS)}")
    print("MCP_CUBELESS_ED_TRUE_MATERIAL_APPLIED_BUILD_END")


if __name__ == "__main__":
    main()
