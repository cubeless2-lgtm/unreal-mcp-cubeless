import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\verify_cubeless_ed_dynamic_material_override_prototype.py",
    )
).parent
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_dynamic_material_override_prototype.py"
VERIFY_MARKER = "MCP_CUBELESS_ED_DYNAMIC_MATERIAL_PROTOTYPE_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_cubeless_ed_dynamic_material_prototype_config", "__file__": str(BUILDER_SCRIPT)}
    with open(BUILDER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(BUILDER_SCRIPT), "exec")
    exec(code, namespace)
    return namespace


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def find_actor(label):
    return next((actor for actor in get_all_level_actors() if actor.get_actor_label() == label), None)


def material_path(material):
    return material.get_path_name() if material else "None"


def get_component_material_paths(component):
    try:
        slot_count = int(component.get_num_materials())
    except Exception:
        slot_count = 4
    paths = []
    for slot_index in range(max(0, slot_count)):
        try:
            paths.append(material_path(component.get_material(slot_index)))
        except Exception:
            break
    return paths


def get_ism_rows(actor):
    rows = []
    for component in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
        mesh = component.get_editor_property("static_mesh")
        mesh_path = mesh.get_path_name() if mesh else "None"
        try:
            count = int(component.get_instance_count())
        except Exception:
            count = -1
        rows.append({
            "component": component.get_name(),
            "mesh": mesh_path,
            "count": count,
            "materials": get_component_material_paths(component),
        })
    return rows


def get_generated_point_count(component):
    try:
        collection = component.get_generated_graph_output()
        for item in collection.get_editor_property("tagged_data"):
            data = item.get_editor_property("data").get_editor_property("data")
            if data and hasattr(data, "get_num_points"):
                return int(data.get_num_points())
    except Exception:
        return 0
    return 0


def get_component_graph_path(component):
    graph_instance = component.get_editor_property("graph_instance")
    graph = graph_instance.get_editor_property("graph") if graph_instance else None
    return graph.get_path_name() if graph else None


def get_graph_nodes_by_settings(graph, settings_name):
    return [
        node for node in graph.get_editor_property("nodes")
        if node.get_settings() and node.get_settings().get_class().get_name() == settings_name
    ]


def get_graph_nodes_by_title(graph, title):
    return [
        node for node in graph.get_editor_property("nodes")
        if str(node.get_editor_property("node_title")) == title
    ]


def soft_object_value_path(value_struct):
    value = value_struct.get_editor_property("soft_object_path_value")
    try:
        return value.to_tuple()[0]
    except Exception:
        return str(value)


def get_add_attribute_constant(graph, attr_title):
    nodes = get_graph_nodes_by_title(graph, attr_title)
    if len(nodes) != 1:
        return {
            "title": attr_title,
            "node_count": len(nodes),
            "value": None,
            "valid": False,
        }
    settings = nodes[0].get_settings()
    value_struct = settings.get_editor_property("attribute_types")
    return {
        "title": attr_title,
        "node_count": len(nodes),
        "type": value_struct.get_editor_property("type"),
        "value": soft_object_value_path(value_struct),
        "valid": True,
    }


def validate_dynamic_graph(config):
    graph = unreal.EditorAssetLibrary.load_asset(config["DYNAMIC_GRAPH_PATH"])
    if not graph:
        raise RuntimeError(f"Missing dynamic material graph: {config['DYNAMIC_GRAPH_PATH']}")
    spawner_nodes = get_graph_nodes_by_settings(graph, "PCGStaticMeshSpawnerSettings")
    spawner_checks = []
    for node in spawner_nodes:
        settings = node.get_settings()
        params = settings.get_editor_property("mesh_selector_parameters")
        spawner_checks.append({
            "node": str(node.get_editor_property("node_title")),
            "selector_class": params.get_class().get_name() if params else None,
            "attribute_name": str(params.get_editor_property("attribute_name")) if params else None,
            "use_attribute_material_overrides": bool(params.get_editor_property("use_attribute_material_overrides")) if params else False,
            "material_override_attributes": [str(item) for item in params.get_editor_property("material_override_attributes")] if params else [],
        })
    attr_checks = [
        get_add_attribute_constant(graph, title)
        for title in config["DYNAMIC_ATTR_NODE_TITLES"].values()
    ]
    validation_pass = (
        len(spawner_checks) == 1
        and spawner_checks[0]["selector_class"] == "PCGMeshSelectorByAttribute"
        and spawner_checks[0]["attribute_name"] == config["DYNAMIC_MESH_ATTR"]
        and spawner_checks[0]["use_attribute_material_overrides"]
        and spawner_checks[0]["material_override_attributes"] == [
            config["DYNAMIC_MATERIAL_SLOT0_ATTR"],
            config["DYNAMIC_MATERIAL_SLOT1_ATTR"],
        ]
        and all(check["valid"] for check in attr_checks)
    )
    return {
        "graph": config["DYNAMIC_GRAPH_PATH"],
        "spawner_checks": spawner_checks,
        "attr_checks": attr_checks,
        "validation_pass": validation_pass,
    }


def validate_validation_actor(config, variant_type):
    variant = config["material_variant_paths"](variant_type)
    label = f"{config['ACTOR_LABEL_PREFIX']}_CompactConifer_Sparse_{variant['variant_name']}_Validation"
    actor = find_actor(label)
    if not actor:
        raise RuntimeError(f"Missing dynamic material validation actor: {label}")
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {label}")
    component = pcg_components[0]
    point_count = get_generated_point_count(component)
    ism_rows = get_ism_rows(actor)
    total_ism = sum(max(0, row["count"]) for row in ism_rows)
    expected_materials = [variant["slot0"], variant["slot1"]]
    matching_rows = [
        row for row in ism_rows
        if row["mesh"] == config["COMPACT_CONIFER_MESH"] and row["materials"][:2] == expected_materials
    ]
    spec = config["get_compact_sparse_tree_spec"]()
    validation_pass = all([
        get_component_graph_path(component) == config["DYNAMIC_GRAPH_PATH"],
        point_count == spec["expected_points"],
        total_ism == spec["expected_ism"],
        len(matching_rows) == 1,
    ])
    return {
        "actor": label,
        "variant_type": variant_type,
        "variant_name": variant["variant_name"],
        "graph": get_component_graph_path(component),
        "expected_graph": config["DYNAMIC_GRAPH_PATH"],
        "point_count": point_count,
        "expected_points": spec["expected_points"],
        "total_ism": total_ism,
        "expected_ism": spec["expected_ism"],
        "expected_materials": expected_materials,
        "ism_rows": ism_rows,
        "matching_row_count": len(matching_rows),
        "validation_pass": validation_pass,
    }


def scan_latest_log(marker):
    log_dir = pathlib.Path(unreal.Paths.project_log_dir())
    logs = sorted(log_dir.glob("*.log"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not logs:
        return None, False, []
    latest = logs[0]
    text = latest.read_text(encoding="utf-8", errors="ignore")
    idx = text.rfind(marker)
    scan_text = text[idx:] if idx >= 0 else text
    errors = [line for line in scan_text.splitlines() if "Error:" in line]
    return latest, idx >= 0, errors


def main():
    print(VERIFY_MARKER)
    config = load_builder_config()
    graph_result = validate_dynamic_graph(config)
    actor_results = [
        validate_validation_actor(config, variant_type)
        for variant_type in config["VALIDATION_VARIANTS"]
    ]
    log_path, marker_found, log_errors = scan_latest_log("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_PROTOTYPE_BUILD_BEGIN")
    validation_pass = all([
        graph_result["validation_pass"],
        all(result["validation_pass"] for result in actor_results),
        not log_errors,
    ])

    print(f"dynamic_graph={graph_result['graph']}")
    print(f"dynamic_graph_count=1")
    print(f"dynamic_spawner_checks={graph_result['spawner_checks']}")
    print(f"dynamic_attr_checks={graph_result['attr_checks']}")
    print(f"dynamic_graph_validation_pass={graph_result['validation_pass']}")
    for result in actor_results:
        print(f"dynamic_validation_actor={result['actor']}")
        print(f"  variant_type={result['variant_type']}")
        print(f"  variant_name={result['variant_name']}")
        print(f"  graph={result['graph']}")
        print(f"  expected_graph={result['expected_graph']}")
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  total_ism={result['total_ism']}")
        print(f"  expected_ism={result['expected_ism']}")
        print(f"  expected_materials={result['expected_materials']}")
        print(f"  matching_row_count={result['matching_row_count']}")
        print(f"  ism_rows={result['ism_rows']}")
        print(f"  validation_pass={result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"dynamic_material_override_prototype_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_PROTOTYPE_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED dynamic material override prototype verification failed")


if __name__ == "__main__":
    main()
