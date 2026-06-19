import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_dynamic_material_axis_by_point.py",
    )
).parent
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_dynamic_material_axis_by_point.py"
VERIFY_MARKER = "MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_BY_POINT_VERIFY_BEGIN"


def load_config():
    namespace = {"__name__": "_cubeless_ed_dynamic_material_axis_config", "__file__": str(BUILDER_SCRIPT)}
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
    total_points = 0
    try:
        collection = component.get_generated_graph_output()
        for item in collection.get_editor_property("tagged_data"):
            data = item.get_editor_property("data").get_editor_property("data")
            if data and hasattr(data, "get_num_points"):
                total_points += int(data.get_num_points())
    except Exception:
        return 0
    return total_points


def get_component_graph_path(component):
    graph_instance = component.get_editor_property("graph_instance")
    graph = graph_instance.get_editor_property("graph") if graph_instance else None
    return graph.get_path_name() if graph else None


def get_graph_nodes_by_settings(graph, settings_name):
    return [
        node for node in graph.get_editor_property("nodes")
        if node.get_settings() and node.get_settings().get_class().get_name() == settings_name
    ]


def validate_graph(config):
    graph = unreal.EditorAssetLibrary.load_asset(config["GRAPH_PATH"])
    if not graph:
        raise RuntimeError(f"Missing dynamic material axis graph: {config['GRAPH_PATH']}")
    spawner_nodes = get_graph_nodes_by_settings(graph, "PCGStaticMeshSpawnerSettings")
    add_nodes = get_graph_nodes_by_settings(graph, "PCGAddAttributeSettings")
    rows = config["expected_rows"]()
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
    mesh_attr_count = sum(
        1 for node in add_nodes
        if config["DYNAMIC_CONFIG"]["DYNAMIC_MESH_ATTR"] in str(node.get_editor_property("node_title"))
    )
    slot0_attr_count = sum(
        1 for node in add_nodes
        if config["DYNAMIC_CONFIG"]["DYNAMIC_MATERIAL_SLOT0_ATTR"] in str(node.get_editor_property("node_title"))
    )
    slot1_attr_count = sum(
        1 for node in add_nodes
        if config["DYNAMIC_CONFIG"]["DYNAMIC_MATERIAL_SLOT1_ATTR"] in str(node.get_editor_property("node_title"))
    )
    pass_attr_count = sum(
        1 for node in add_nodes
        if config["DYNAMIC_AXIS_PASS_ATTR"] in str(node.get_editor_property("node_title"))
    )
    validation_pass = (
        len(spawner_checks) == 1
        and spawner_checks[0]["selector_class"] == "PCGMeshSelectorByAttribute"
        and spawner_checks[0]["attribute_name"] == config["DYNAMIC_CONFIG"]["DYNAMIC_MESH_ATTR"]
        and spawner_checks[0]["use_attribute_material_overrides"]
        and spawner_checks[0]["material_override_attributes"] == [
            config["DYNAMIC_CONFIG"]["DYNAMIC_MATERIAL_SLOT0_ATTR"],
            config["DYNAMIC_CONFIG"]["DYNAMIC_MATERIAL_SLOT1_ATTR"],
        ]
        and mesh_attr_count == len(rows)
        and slot0_attr_count == len(rows)
        and slot1_attr_count == len(rows)
        and pass_attr_count == len(rows)
    )
    return {
        "graph": config["GRAPH_PATH"],
        "row_count": len(rows),
        "spawner_checks": spawner_checks,
        "mesh_attr_count": mesh_attr_count,
        "slot0_attr_count": slot0_attr_count,
        "slot1_attr_count": slot1_attr_count,
        "pass_attr_count": pass_attr_count,
        "validation_pass": validation_pass,
    }


def matching_ism_rows(ism_rows, expected_row):
    materials = expected_row["materials"]
    return [
        row for row in ism_rows
        if row["mesh"] == expected_row["mesh_path"]
        and row["materials"][:len(materials)] == materials
    ]


def validate_actor(config):
    actor = find_actor(config["ACTOR_LABEL"])
    if not actor:
        raise RuntimeError(f"Missing dynamic material axis validation actor: {config['ACTOR_LABEL']}")
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {config['ACTOR_LABEL']}")
    component = pcg_components[0]
    expected_rows = config["expected_rows"]()
    expected_total = sum(row["expected_instance_count"] for row in expected_rows)
    point_count = get_generated_point_count(component)
    ism_rows = get_ism_rows(actor)
    total_ism = sum(max(0, row["count"]) for row in ism_rows)
    row_results = []
    for expected_row in expected_rows:
        rows = matching_ism_rows(ism_rows, expected_row)
        row_results.append({
            "domain_name": expected_row["domain_name"],
            "domain_type": expected_row["domain_type"],
            "variant_name": expected_row["variant_name"],
            "variant_type": expected_row["variant_type"],
            "mesh_key": expected_row["mesh_key"],
            "mesh_path": expected_row["mesh_path"],
            "expected_materials": expected_row["materials"],
            "matching_row_count": len(rows),
            "matching_instance_count": sum(max(0, row["count"]) for row in rows),
            "expected_instance_count": expected_row["expected_instance_count"],
        })
    validation_pass = all([
        get_component_graph_path(component) == config["GRAPH_PATH"],
        point_count == expected_total,
        total_ism == expected_total,
        all(result["matching_row_count"] == 1 for result in row_results),
        all(result["matching_instance_count"] == result["expected_instance_count"] for result in row_results),
    ])
    return {
        "actor": config["ACTOR_LABEL"],
        "graph": get_component_graph_path(component),
        "expected_graph": config["GRAPH_PATH"],
        "point_count": point_count,
        "expected_points": expected_total,
        "total_ism": total_ism,
        "expected_ism": expected_total,
        "row_results": row_results,
        "ism_rows": ism_rows,
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
    config = load_config()
    graph_result = validate_graph(config)
    actor_result = validate_actor(config)
    log_path, marker_found, log_errors = scan_latest_log("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_BY_POINT_BUILD_BEGIN")
    validation_pass = all([
        graph_result["validation_pass"],
        actor_result["validation_pass"],
        not log_errors,
    ])
    print(f"dynamic_material_axis_graph={graph_result['graph']}")
    print("dynamic_material_axis_graph_count=1")
    print(f"dynamic_material_axis_expected_row_count={graph_result['row_count']}")
    print(f"dynamic_material_axis_spawner_checks={graph_result['spawner_checks']}")
    print(f"dynamic_material_axis_mesh_attr_count={graph_result['mesh_attr_count']}")
    print(f"dynamic_material_axis_slot0_attr_count={graph_result['slot0_attr_count']}")
    print(f"dynamic_material_axis_slot1_attr_count={graph_result['slot1_attr_count']}")
    print(f"dynamic_material_axis_pass_attr_count={graph_result['pass_attr_count']}")
    print(f"dynamic_material_axis_graph_validation_pass={graph_result['validation_pass']}")
    print(f"dynamic_material_axis_actor={actor_result['actor']}")
    print(f"  graph={actor_result['graph']}")
    print(f"  expected_graph={actor_result['expected_graph']}")
    print(f"  point_count={actor_result['point_count']}")
    print(f"  expected_points={actor_result['expected_points']}")
    print(f"  total_ism={actor_result['total_ism']}")
    print(f"  expected_ism={actor_result['expected_ism']}")
    for result in actor_result["row_results"]:
        print(f"  row_result={result}")
    print(f"  ism_rows={actor_result['ism_rows']}")
    print(f"  validation_pass={actor_result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"dynamic_material_axis_by_point_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_BY_POINT_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED dynamic material axis by-point verification failed")


if __name__ == "__main__":
    main()
