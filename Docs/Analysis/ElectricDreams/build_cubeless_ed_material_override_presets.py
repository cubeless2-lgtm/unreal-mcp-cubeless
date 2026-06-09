import unreal


MATERIAL_PACKAGE = "/Game/Cubeless/PCG/ElectricDreamsLearning/Materials/MaterialOverrides"
MATERIAL_OVERRIDE_PACKAGE = "/Game/Cubeless/PCG/ElectricDreamsLearning/MaterialOverridePresets"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_MaterialOverride"

MESH_PATHS = {
    "fern": (
        "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Plants/"
        "SM_Fern_01.SM_Fern_01"
    ),
    "ground_leaf": (
        "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Plants/"
        "SM_GroundLeaf_01.SM_GroundLeaf_01"
    ),
    "small_rock_01": (
        "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Stones/Rocks/"
        "SM_SmallRock_01.SM_SmallRock_01"
    ),
    "small_rock_02": (
        "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Stones/Rocks/"
        "SM_SmallRock_02.SM_SmallRock_02"
    ),
    "conifer_05": (
        "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Trees/"
        "SM_Conifer_05.SM_Conifer_05"
    ),
}

BASE_MATERIAL_PATHS = {
    "fern": (
        "/Game/DreamscapeSeries/DreamscapeMountains/Materials/Foliage/Plants/"
        "MI_Fern.MI_Fern"
    ),
    "ground_leaf": (
        "/Game/DreamscapeSeries/DreamscapeMountains/Materials/Foliage/Plants/"
        "MI_GroundLeaves_01.MI_GroundLeaves_01"
    ),
    "rock": (
        "/Game/DreamscapeSeries/DreamscapeMountains/Materials/Stones/"
        "MI_Tiling_Rock_02.MI_Tiling_Rock_02"
    ),
    "pine_leaves": (
        "/Game/DreamscapeSeries/DreamscapeMountains/Materials/Foliage/Trees/"
        "M_PineLeaves_01.M_PineLeaves_01"
    ),
    "pine_bark": (
        "/Game/DreamscapeSeries/DreamscapeMountains/Materials/Foliage/Trees/"
        "M_PineBark_01.M_PineBark_01"
    ),
}

MATERIAL_VARIANT_SPECS = {
    "fern_cool": {
        "asset_name": "MI_Cubeless_ED_Fern_Cool",
        "parent": BASE_MATERIAL_PATHS["fern"],
        "vectors": {
            "Color Tint": (0.055, 0.165, 0.105, 1.0),
            "Color Gradient 01": (0.035, 0.105, 0.045, 1.0),
            "Color Gradient 02": (0.19, 0.36, 0.17, 1.0),
        },
    },
    "fern_warm": {
        "asset_name": "MI_Cubeless_ED_Fern_Warm",
        "parent": BASE_MATERIAL_PATHS["fern"],
        "vectors": {
            "Color Tint": (0.16, 0.125, 0.045, 1.0),
            "Color Gradient 01": (0.105, 0.075, 0.025, 1.0),
            "Color Gradient 02": (0.36, 0.30, 0.11, 1.0),
        },
    },
    "ground_leaf_cool": {
        "asset_name": "MI_Cubeless_ED_GroundLeaves_Cool",
        "parent": BASE_MATERIAL_PATHS["ground_leaf"],
        "vectors": {
            "Color Tint": (0.055, 0.155, 0.095, 1.0),
            "Color Gradient 01": (0.035, 0.10, 0.045, 1.0),
            "Color Gradient 02": (0.20, 0.34, 0.15, 1.0),
        },
    },
    "ground_leaf_warm": {
        "asset_name": "MI_Cubeless_ED_GroundLeaves_Warm",
        "parent": BASE_MATERIAL_PATHS["ground_leaf"],
        "vectors": {
            "Color Tint": (0.17, 0.125, 0.045, 1.0),
            "Color Gradient 01": (0.105, 0.07, 0.025, 1.0),
            "Color Gradient 02": (0.36, 0.28, 0.11, 1.0),
        },
    },
    "rock_cool": {
        "asset_name": "MI_Cubeless_ED_Rock_Cool",
        "parent": BASE_MATERIAL_PATHS["rock"],
        "vectors": {
            "Color Tint": (0.37, 0.41, 0.43, 1.0),
        },
    },
    "rock_dark": {
        "asset_name": "MI_Cubeless_ED_Rock_Dark",
        "parent": BASE_MATERIAL_PATHS["rock"],
        "vectors": {
            "Color Tint": (0.18, 0.16, 0.14, 1.0),
        },
    },
    "pine_leaves_dark": {
        "asset_name": "MI_Cubeless_ED_PineLeaves_Dark",
        "parent": BASE_MATERIAL_PATHS["pine_leaves"],
        "vectors": {
            "Color Tint": (0.035, 0.075, 0.04, 1.0),
            "Gradient Color Top": (0.055, 0.115, 0.055, 1.0),
            "Gradient Color Bottom": (0.018, 0.045, 0.024, 1.0),
        },
    },
    "pine_bark_dark": {
        "asset_name": "MI_Cubeless_ED_PineBark_Dark",
        "parent": BASE_MATERIAL_PATHS["pine_bark"],
        "vectors": {
            "Color Tint": (0.16, 0.105, 0.065, 1.0),
            "Gradient Color Top": (0.25, 0.18, 0.10, 1.0),
            "Gradient Color Bottom": (0.10, 0.07, 0.045, 1.0),
        },
    },
    "pine_leaves_soft": {
        "asset_name": "MI_Cubeless_ED_PineLeaves_Soft",
        "parent": BASE_MATERIAL_PATHS["pine_leaves"],
        "vectors": {
            "Color Tint": (0.095, 0.14, 0.07, 1.0),
            "Gradient Color Top": (0.14, 0.19, 0.09, 1.0),
            "Gradient Color Bottom": (0.055, 0.095, 0.045, 1.0),
        },
    },
    "pine_bark_soft": {
        "asset_name": "MI_Cubeless_ED_PineBark_Soft",
        "parent": BASE_MATERIAL_PATHS["pine_bark"],
        "vectors": {
            "Color Tint": (0.22, 0.16, 0.09, 1.0),
            "Gradient Color Top": (0.32, 0.23, 0.12, 1.0),
            "Gradient Color Bottom": (0.14, 0.095, 0.055, 1.0),
        },
    },
}


def material_variant_path(key):
    asset_name = MATERIAL_VARIANT_SPECS[key]["asset_name"]
    return f"{MATERIAL_PACKAGE}/{asset_name}.{asset_name}"


DOMAIN_SPECS = {
    1: {
        "name": "GroundFoliage",
        "domain_id": 701,
        "domain_type": 1,
        "point_offsets": [(-180.0, 0.0, 0.0), (180.0, 0.0, 0.0)],
        "entries": [
            {
                "mesh_key": "fern",
                "mesh_path": MESH_PATHS["fern"],
                "variant_overrides": {
                    1: [],
                    2: [material_variant_path("fern_cool")],
                    3: [material_variant_path("fern_warm")],
                },
            },
            {
                "mesh_key": "ground_leaf",
                "mesh_path": MESH_PATHS["ground_leaf"],
                "variant_overrides": {
                    1: [],
                    2: [material_variant_path("ground_leaf_cool")],
                    3: [material_variant_path("ground_leaf_warm")],
                },
            },
        ],
    },
    2: {
        "name": "SmallRocks",
        "domain_id": 702,
        "domain_type": 2,
        "point_offsets": [(-220.0, 0.0, 0.0), (220.0, 0.0, 0.0)],
        "entries": [
            {
                "mesh_key": "small_rock_01",
                "mesh_path": MESH_PATHS["small_rock_01"],
                "variant_overrides": {
                    1: [],
                    2: [material_variant_path("rock_cool")],
                    3: [material_variant_path("rock_dark")],
                },
            },
            {
                "mesh_key": "small_rock_02",
                "mesh_path": MESH_PATHS["small_rock_02"],
                "variant_overrides": {
                    1: [],
                    2: [material_variant_path("rock_cool")],
                    3: [material_variant_path("rock_dark")],
                },
            },
        ],
    },
    3: {
        "name": "CompactConifer",
        "domain_id": 703,
        "domain_type": 3,
        "point_offsets": [(0.0, 0.0, 0.0)],
        "entries": [
            {
                "mesh_key": "conifer_05",
                "mesh_path": MESH_PATHS["conifer_05"],
                "variant_overrides": {
                    1: [],
                    2: [
                        material_variant_path("pine_leaves_dark"),
                        material_variant_path("pine_bark_dark"),
                    ],
                    3: [
                        material_variant_path("pine_leaves_soft"),
                        material_variant_path("pine_bark_soft"),
                    ],
                },
            },
        ],
    },
}

VARIANT_NAMES = {
    (1, 1): "Default",
    (1, 2): "CoolLeaf",
    (1, 3): "WarmLeaf",
    (2, 1): "Default",
    (2, 2): "CoolRock",
    (2, 3): "DarkRock",
    (3, 1): "Default",
    (3, 2): "DarkPine",
    (3, 3): "SoftPine",
}


def material_override_type(domain_type, variant_type):
    return int(domain_type) * 10 + int(variant_type)


def material_override_id(domain_type, variant_type):
    return 70000 + material_override_type(domain_type, variant_type)


def material_override_asset_name(domain, variant_type):
    variant_name = VARIANT_NAMES[(domain["domain_type"], variant_type)]
    return f"PCG_Cubeless_ED_MaterialOverride_{domain['name']}_{variant_name}"


MATERIAL_OVERRIDE_SPECS = []
for domain_type, domain_spec in DOMAIN_SPECS.items():
    for variant_type in (1, 2, 3):
        variant_name = VARIANT_NAMES[(domain_type, variant_type)]
        entries = []
        for entry in domain_spec["entries"]:
            entries.append({
                "mesh_key": entry["mesh_key"],
                "mesh_path": entry["mesh_path"],
                "override_material_paths": list(entry["variant_overrides"][variant_type]),
            })
        MATERIAL_OVERRIDE_SPECS.append({
            "name": f"{domain_spec['name']}_{variant_name}",
            "asset_name": material_override_asset_name(domain_spec, variant_type),
            "domain_name": domain_spec["name"],
            "domain_id": domain_spec["domain_id"],
            "domain_type": domain_spec["domain_type"],
            "variant_name": variant_name,
            "variant_id": 710 + variant_type,
            "variant_type": variant_type,
            "override_id": material_override_id(domain_type, variant_type),
            "override_type": material_override_type(domain_type, variant_type),
            "override_mode": 0 if variant_type == 1 else 1,
            "point_offsets": list(domain_spec["point_offsets"]),
            "entries": entries,
            "expected_points": len(domain_spec["point_offsets"]),
            "expected_ism": len(domain_spec["point_offsets"]),
        })

MATERIAL_OVERRIDE_GRAPH_PATHS = {
    spec["name"]: f"{MATERIAL_OVERRIDE_PACKAGE}/{spec['asset_name']}.{spec['asset_name']}"
    for spec in MATERIAL_OVERRIDE_SPECS
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


def make_color(values):
    return unreal.LinearColor(float(values[0]), float(values[1]), float(values[2]), float(values[3]))


def ensure_material_variant(key, spec):
    unreal.EditorAssetLibrary.make_directory(MATERIAL_PACKAGE)
    asset_name = spec["asset_name"]
    material_path = f"{MATERIAL_PACKAGE}/{asset_name}.{asset_name}"
    material = unreal.EditorAssetLibrary.load_asset(material_path)
    if not material:
        material = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            asset_name,
            MATERIAL_PACKAGE,
            unreal.MaterialInstanceConstant.static_class(),
            unreal.MaterialInstanceConstantFactoryNew(),
        )
    if not material:
        raise RuntimeError(f"Failed to create material variant: {material_path}")

    parent = unreal.EditorAssetLibrary.load_asset(spec["parent"])
    if not parent:
        raise RuntimeError(f"Missing material parent for {key}: {spec['parent']}")

    material.modify()
    if hasattr(unreal.MaterialEditingLibrary, "set_material_instance_parent"):
        unreal.MaterialEditingLibrary.set_material_instance_parent(material, parent)
    else:
        material.set_editor_property("parent", parent)
    for param_name, rgba in spec["vectors"].items():
        unreal.MaterialEditingLibrary.set_material_instance_vector_parameter_value(
            material,
            param_name,
            make_color(rgba),
        )
    unreal.MaterialEditingLibrary.update_material_instance(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    return material


def ensure_material_variants():
    created = {}
    for key, spec in MATERIAL_VARIANT_SPECS.items():
        material = ensure_material_variant(key, spec)
        created[key] = material.get_path_name()
    return created


def configure_points(node, spec):
    settings = node.get_settings()
    points = settings.get_editor_property("points_to_create")
    points.clear()
    for index, coord in enumerate(spec["point_offsets"]):
        point = unreal.PCGPoint()
        transform = point.get_editor_property("transform")
        transform.set_editor_property("translation", unreal.Vector(*coord))
        point.set_editor_property("transform", transform)
        point.set_editor_property("bounds_min", unreal.Vector(-80.0, -80.0, 0.0))
        point.set_editor_property("bounds_max", unreal.Vector(80.0, 80.0, 80.0))
        point.set_editor_property("density", 1.0)
        point.set_editor_property("steepness", 1.0)
        point.set_editor_property("seed", int(spec["override_id"] + index))
        points.append(point)
    settings.set_editor_property("points_to_create", points)
    settings.set_editor_property("cull_points_outside_volume", False)


def add_material_markers(graph, upstream, spec, x, y):
    marker_specs = [
        ("DesignerMaterialDomainId", unreal.PCGMetadataTypes.INTEGER32, spec["domain_id"]),
        ("DesignerMaterialDomainType", unreal.PCGMetadataTypes.INTEGER32, spec["domain_type"]),
        ("DesignerMaterialVariantId", unreal.PCGMetadataTypes.INTEGER32, spec["variant_id"]),
        ("DesignerMaterialVariantType", unreal.PCGMetadataTypes.INTEGER32, spec["variant_type"]),
        ("DesignerMaterialOverrideId", unreal.PCGMetadataTypes.INTEGER32, spec["override_id"]),
        ("DesignerMaterialOverrideType", unreal.PCGMetadataTypes.INTEGER32, spec["override_type"]),
        ("DesignerMaterialOverrideMode", unreal.PCGMetadataTypes.INTEGER32, spec["override_mode"]),
        ("DesignerMaterialOverridePass", unreal.PCGMetadataTypes.BOOLEAN, True),
    ]
    current = upstream
    for index, (attr_name, attr_type, value) in enumerate(marker_specs):
        node = add_node(graph, unreal.PCGAddAttributeSettings, f"{attr_name} {value}", x + index * 280, y)
        configure_add(node, attr_name, "@Last", attr_type, value)
        graph.add_edge(current, "Out", node, "In")
        current = node
    return current


def configure_material_spawner(node, spec):
    settings = node.get_settings()
    if hasattr(settings, "set_editor_property"):
        try:
            settings.set_editor_property("allow_descriptor_changes", True)
        except Exception:
            pass
    entries = []
    for entry_spec in spec["entries"]:
        mesh = unreal.EditorAssetLibrary.load_asset(entry_spec["mesh_path"])
        if not mesh:
            raise RuntimeError(f"Missing material override mesh: {entry_spec['mesh_path']}")
        descriptor = unreal.PCGSoftISMComponentDescriptor()
        descriptor.set_editor_property("static_mesh", mesh)
        overrides = []
        for material_path in entry_spec["override_material_paths"]:
            material = unreal.EditorAssetLibrary.load_asset(material_path)
            if not material:
                raise RuntimeError(f"Missing override material: {material_path}")
            overrides.append(material)
        descriptor.set_editor_property("override_materials", overrides)
        weighted_entry = unreal.PCGMeshSelectorWeightedEntry()
        weighted_entry.set_editor_property("descriptor", descriptor)
        weighted_entry.set_editor_property("weight", 1)
        entries.append(weighted_entry)
    params = settings.get_editor_property("mesh_selector_parameters")
    params.set_editor_property("mesh_entries", entries)


def ensure_graph(asset_name):
    unreal.EditorAssetLibrary.make_directory(MATERIAL_OVERRIDE_PACKAGE)
    graph_path = f"{MATERIAL_OVERRIDE_PACKAGE}/{asset_name}.{asset_name}"
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            asset_name,
            MATERIAL_OVERRIDE_PACKAGE,
            unreal.PCGGraph.static_class(),
            unreal.PCGGraphFactory(),
        )
    if not graph:
        raise RuntimeError(f"Failed to create/load material override graph: {graph_path}")
    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)
    return graph


def build_material_override_graph(spec):
    graph = ensure_graph(spec["asset_name"])
    source = add_node(graph, unreal.PCGCreatePointsSettings, f"{spec['name']} Points", -1200, 0)
    configure_points(source, spec)
    markers = add_material_markers(graph, source, spec, -820, 0)
    spawner = add_node(graph, unreal.PCGStaticMeshSpawnerSettings, f"Spawn {spec['name']}", 1700, 0)
    configure_material_spawner(spawner, spec)
    graph.add_edge(markers, "Out", spawner, "In")
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


def spawn_validation_actor(spec, graph, index):
    label = f"{ACTOR_LABEL_PREFIX}_{spec['name']}_Validation"
    for actor in get_all_level_actors():
        if actor.get_actor_label() == label:
            unreal.EditorLevelLibrary.destroy_actor(actor)
    row = index // 3
    column = index % 3
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.PCGVolume,
        unreal.Vector(62000 + column * 1800, row * 1800, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(label)
    actor.pcg_component.set_graph(graph)
    actor.pcg_component.cleanup(True)
    actor.pcg_component.generate(True)
    actor.pcg_component.generate(True)
    return actor


def main():
    print("MCP_CUBELESS_ED_MATERIAL_OVERRIDE_PRESETS_BUILD_BEGIN")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    created_materials = ensure_material_variants()
    for key, path in sorted(created_materials.items()):
        print(f"material_variant={key}:{path}")

    for index, spec in enumerate(MATERIAL_OVERRIDE_SPECS):
        graph = build_material_override_graph(spec)
        actor = spawn_validation_actor(spec, graph, index)
        print(f"material_override={spec['name']}")
        print(f"material_override_graph={graph.get_path_name()}")
        print(f"validation_actor={actor.get_actor_label()}")
        print(f"domain_type={spec['domain_type']}")
        print(f"variant_type={spec['variant_type']}")
        print(f"expected_points={spec['expected_points']}")
        print(f"expected_ism={spec['expected_ism']}")
        print(f"entries={spec['entries']}")
    print(f"material_override_graph_count={len(MATERIAL_OVERRIDE_SPECS)}")
    print("MCP_CUBELESS_ED_MATERIAL_OVERRIDE_PRESETS_BUILD_END")


if __name__ == "__main__":
    main()
