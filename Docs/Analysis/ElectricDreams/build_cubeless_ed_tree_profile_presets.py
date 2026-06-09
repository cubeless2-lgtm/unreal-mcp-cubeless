import math

import unreal


TREE_PROFILE_PACKAGE = "/Game/Cubeless/PCG/ElectricDreamsLearning/TreeProfilePresets"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_TreeProfile"

PROFILE_ID = 30
PROFILE_TYPE = 3

TREE_STYLE_SPECS = [
    {
        "name": "CompactConifer",
        "style_id": 501,
        "style_type": 1,
        "mesh_paths": [(
            "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Trees/"
            "SM_Conifer_05.SM_Conifer_05"
        )],
        "bounds_radius": 699.33,
    },
    {
        "name": "ColumnConifer",
        "style_id": 502,
        "style_type": 2,
        "mesh_paths": [(
            "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Trees/"
            "SM_Conifer_08.SM_Conifer_08"
        )],
        "bounds_radius": 962.93,
    },
    {
        "name": "MixedConifer",
        "style_id": 503,
        "style_type": 3,
        "mesh_paths": [
            (
                "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Trees/"
                "SM_Conifer_05.SM_Conifer_05"
            ),
            (
                "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Trees/"
                "SM_Conifer_08.SM_Conifer_08"
            ),
            (
                "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Trees/"
                "SM_Conifer_09.SM_Conifer_09"
            ),
        ],
        "bounds_radius": 1009.29,
    },
]

TREE_AMOUNT_SPECS = [
    {
        "name": "Solo",
        "amount_id": 601,
        "amount_type": 1,
        "point_offsets": [(0.0, 0.0, 0.0)],
    },
    {
        "name": "Sparse",
        "amount_id": 602,
        "amount_type": 2,
        "point_offsets": [(-900.0, 0.0, 0.0), (900.0, 0.0, 0.0)],
    },
    {
        "name": "LightGrove",
        "amount_id": 603,
        "amount_type": 3,
        "point_offsets": [(-1300.0, -700.0, 0.0), (1300.0, -700.0, 0.0), (0.0, 1300.0, 0.0)],
    },
]

for amount in TREE_AMOUNT_SPECS:
    amount["expected_points"] = len(amount["point_offsets"])
    amount["expected_ism"] = len(amount["point_offsets"])


def min_spacing(points):
    if len(points) < 2:
        return 0.0
    spacing = None
    for index, first in enumerate(points):
        for second in points[index + 1:]:
            distance = math.dist(first[:2], second[:2])
            spacing = distance if spacing is None else min(spacing, distance)
    return float(spacing or 0.0)


def tree_profile_type(style_type, amount_type):
    return int(style_type) * 10 + int(amount_type)


def tree_profile_id(style_type, amount_type):
    return 30000 + tree_profile_type(style_type, amount_type)


def tree_profile_asset_name(style, amount):
    return f"PCG_Cubeless_ED_TreeProfile_{style['name']}_{amount['name']}"


def tree_profile_graph_path(style, amount):
    asset_name = tree_profile_asset_name(style, amount)
    return f"{TREE_PROFILE_PACKAGE}/{asset_name}.{asset_name}"


TREE_PROFILE_SPECS = []
for style_spec in TREE_STYLE_SPECS:
    for amount_spec in TREE_AMOUNT_SPECS:
        TREE_PROFILE_SPECS.append({
            "name": f"{style_spec['name']}_{amount_spec['name']}",
            "asset_name": tree_profile_asset_name(style_spec, amount_spec),
            "style_id": style_spec["style_id"],
            "style_type": style_spec["style_type"],
            "mesh_paths": style_spec["mesh_paths"],
            "bounds_radius": style_spec["bounds_radius"],
            "profile_id": PROFILE_ID,
            "profile_type": PROFILE_TYPE,
            "amount_id": amount_spec["amount_id"],
            "amount_type": amount_spec["amount_type"],
            "point_offsets": amount_spec["point_offsets"],
            "min_spacing": min_spacing(amount_spec["point_offsets"]) if len(amount_spec["point_offsets"]) > 1 else 0.0,
            "tree_profile_id": tree_profile_id(style_spec["style_type"], amount_spec["amount_type"]),
            "tree_profile_type": tree_profile_type(style_spec["style_type"], amount_spec["amount_type"]),
            "expected_points": amount_spec["expected_points"],
            "expected_ism": amount_spec["expected_ism"],
        })

TREE_PROFILE_GRAPH_PATHS = {
    spec["name"]: f"{TREE_PROFILE_PACKAGE}/{spec['asset_name']}.{spec['asset_name']}"
    for spec in TREE_PROFILE_SPECS
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
        point.set_editor_property("seed", int(spec["tree_profile_id"] + index))
        points.append(point)
    settings.set_editor_property("points_to_create", points)
    settings.set_editor_property("cull_points_outside_volume", False)


def configure_tree_spawner(node, spec):
    settings = node.get_settings()
    entries = []
    for mesh_path in spec["mesh_paths"]:
        mesh = unreal.EditorAssetLibrary.load_asset(mesh_path)
        if not mesh:
            raise RuntimeError(f"Missing tree mesh: {mesh_path}")
        descriptor = unreal.PCGSoftISMComponentDescriptor()
        descriptor.set_editor_property("static_mesh", mesh)
        entry = unreal.PCGMeshSelectorWeightedEntry()
        entry.set_editor_property("descriptor", descriptor)
        entry.set_editor_property("weight", 1)
        entries.append(entry)
    params = settings.get_editor_property("mesh_selector_parameters")
    params.set_editor_property("mesh_entries", entries)


def ensure_graph(asset_name):
    unreal.EditorAssetLibrary.make_directory(TREE_PROFILE_PACKAGE)
    graph_path = f"{TREE_PROFILE_PACKAGE}/{asset_name}.{asset_name}"
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
            asset_name,
            TREE_PROFILE_PACKAGE,
            unreal.PCGGraph.static_class(),
            unreal.PCGGraphFactory(),
        )
    if not graph:
        raise RuntimeError(f"Failed to create/load tree profile graph: {graph_path}")
    for node in list(graph.get_editor_property("nodes")):
        graph.remove_node(node)
    return graph


def add_tree_markers(graph, upstream, spec, x, y):
    marker_specs = [
        ("DesignerProfileId", unreal.PCGMetadataTypes.INTEGER32, spec["profile_id"]),
        ("DesignerProfileType", unreal.PCGMetadataTypes.INTEGER32, spec["profile_type"]),
        ("DesignerAmountId", unreal.PCGMetadataTypes.INTEGER32, spec["amount_id"]),
        ("DesignerAmountType", unreal.PCGMetadataTypes.INTEGER32, spec["amount_type"]),
        ("DesignerAmountPass", unreal.PCGMetadataTypes.BOOLEAN, True),
        ("DesignerTreeStyleId", unreal.PCGMetadataTypes.INTEGER32, spec["style_id"]),
        ("DesignerTreeStyleType", unreal.PCGMetadataTypes.INTEGER32, spec["style_type"]),
        ("DesignerTreeStylePass", unreal.PCGMetadataTypes.BOOLEAN, True),
        ("DesignerTreeProfileId", unreal.PCGMetadataTypes.INTEGER32, spec["tree_profile_id"]),
        ("DesignerTreeProfileType", unreal.PCGMetadataTypes.INTEGER32, spec["tree_profile_type"]),
        ("DesignerTreeProfilePass", unreal.PCGMetadataTypes.BOOLEAN, True),
        ("DesignerTreeMinSpacing", unreal.PCGMetadataTypes.DOUBLE, spec["min_spacing"]),
    ]
    current = upstream
    for index, (attr_name, attr_type, value) in enumerate(marker_specs):
        node = add_node(graph, unreal.PCGAddAttributeSettings, f"{attr_name} {value}", x + index * 280, y)
        configure_add(node, attr_name, "@Last", attr_type, value)
        graph.add_edge(current, "Out", node, "In")
        current = node
    return current


def build_tree_profile_graph(spec):
    graph = ensure_graph(spec["asset_name"])
    source = add_node(graph, unreal.PCGCreatePointsSettings, f"{spec['name']} Tree Points", -1200, 0)
    configure_points(source, spec)
    markers = add_tree_markers(graph, source, spec, -820, 0)
    spawner = add_node(graph, unreal.PCGStaticMeshSpawnerSettings, f"Spawn {spec['name']}", 2600, 0)
    configure_tree_spawner(spawner, spec)
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
        unreal.Vector(37000 + column * 2600, row * 2600, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(label)
    actor.pcg_component.set_graph(graph)
    actor.pcg_component.cleanup(True)
    actor.pcg_component.generate(True)
    return actor


def main():
    print("MCP_CUBELESS_ED_TREE_PROFILE_PRESETS_BUILD_BEGIN")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for index, spec in enumerate(TREE_PROFILE_SPECS):
        graph = build_tree_profile_graph(spec)
        actor = spawn_validation_actor(spec, graph, index)
        print(f"tree_profile={spec['name']}")
        print(f"tree_profile_graph={graph.get_path_name()}")
        print(f"validation_actor={actor.get_actor_label()}")
        print(f"style_type={spec['style_type']}")
        print(f"amount_type={spec['amount_type']}")
        print(f"expected_points={spec['expected_points']}")
        print(f"expected_ism={spec['expected_ism']}")
        print(f"min_spacing={spec['min_spacing']}")
        print(f"mesh_paths={spec['mesh_paths']}")
    print(f"tree_profile_graph_count={len(TREE_PROFILE_SPECS)}")
    print("MCP_CUBELESS_ED_TREE_PROFILE_PRESETS_BUILD_END")


if __name__ == "__main__":
    main()
