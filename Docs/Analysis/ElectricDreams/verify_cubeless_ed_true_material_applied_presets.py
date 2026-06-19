import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_true_material_applied_presets.py",
    )
).parent
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_true_material_applied_presets.py"
VERIFY_MARKER = "MCP_CUBELESS_ED_TRUE_MATERIAL_APPLIED_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_cubeless_ed_true_material_applied_config", "__file__": str(BUILDER_SCRIPT)}
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


def get_generated_point_data(component):
    for attempt in range(4):
        collection = component.get_generated_graph_output()
        for item in collection.get_editor_property("tagged_data"):
            data = item.get_editor_property("data").get_editor_property("data")
            if data and hasattr(data, "get_num_points"):
                return data
        if attempt < 3:
            component.generate(True)
    return None


def get_generated_point_count(component):
    data = get_generated_point_data(component)
    return int(data.get_num_points()) if data else 0


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


def get_graph_nodes_by_settings(graph_path, settings_name):
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        raise RuntimeError(f"Missing graph: {graph_path}")
    nodes = []
    for node in graph.get_editor_property("nodes"):
        settings = node.get_settings()
        if settings and settings.get_class().get_name() == settings_name:
            nodes.append(node)
    return nodes


def get_spawner_entry_rows(graph_path):
    rows = []
    for node in get_graph_nodes_by_settings(graph_path, "PCGStaticMeshSpawnerSettings"):
        params = node.get_settings().get_editor_property("mesh_selector_parameters")
        for entry in params.get_editor_property("mesh_entries"):
            descriptor = entry.get_editor_property("descriptor")
            mesh = descriptor.get_editor_property("static_mesh") if descriptor else None
            overrides = descriptor.get_editor_property("override_materials") if descriptor else []
            rows.append({
                "mesh": mesh.get_path_name() if mesh else "None",
                "override_materials": [material_path(material) for material in overrides],
            })
    return rows


def get_subgraph_paths(graph_path):
    rows = []
    for node in get_graph_nodes_by_settings(graph_path, "PCGSubgraphSettings"):
        settings = node.get_settings()
        instance = settings.get_editor_property("subgraph_instance")
        graph = instance.get_editor_property("graph") if instance else None
        rows.append(graph.get_path_name() if graph else "None")
    return rows


def expected_override_map_from_spawner_specs(spec):
    return {
        mesh_path: list(materials)
        for mesh_path, materials in spec["expected_override_map"].items()
    }


def actual_override_map_from_rows(rows):
    return {
        row["mesh"]: list(row["override_materials"])
        for row in rows
        if row["override_materials"]
    }


def validate_style_amount_graphs(config):
    failures = []
    for style in config["STYLE_CONFIG"]["STYLE_SPECS"]:
        if style["style_type"] not in config["STYLE_DOMAIN_BY_STYLE_TYPE"]:
            continue
        for variant_type in (2, 3):
            expected_map = config["material_override_map_for_style"](style, variant_type)
            for profile_key, amount_list in (
                ("Ground", config["STYLE_CONFIG"]["GROUND_AMOUNT_SPECS"]),
                ("Ditch", config["STYLE_CONFIG"]["DITCH_AMOUNT_SPECS"]),
            ):
                for amount in amount_list:
                    graph_path = config["true_style_amount_graph_path"](profile_key, amount, style, variant_type)
                    rows = get_spawner_entry_rows(graph_path)
                    actual_map = actual_override_map_from_rows(rows)
                    if actual_map != expected_map:
                        failures.append({
                            "graph": graph_path,
                            "actual": actual_map,
                            "expected": expected_map,
                        })
    return failures


def validate_style_matrix_graphs(config):
    failures = []
    for spec in config["TRUE_STYLE_MATRIX_SPECS"]:
        graph_path = spec["graph_path"]
        actual_subgraphs = sorted(get_subgraph_paths(graph_path))
        expected_subgraphs = sorted(spec["subgraph_paths"])
        if actual_subgraphs != expected_subgraphs:
            failures.append({
                "graph": graph_path,
                "actual_subgraphs": actual_subgraphs,
                "expected_subgraphs": expected_subgraphs,
            })
    return failures


def validate_tree_graphs(config):
    failures = []
    for spec in config["TRUE_TREE_SPECS"]:
        rows = get_spawner_entry_rows(spec["graph_path"])
        actual_map = actual_override_map_from_rows(rows)
        expected_map = expected_override_map_from_spawner_specs(spec)
        if actual_map != expected_map:
            failures.append({
                "graph": spec["graph_path"],
                "actual": actual_map,
                "expected": expected_map,
            })
    return failures


def validate_generated_slots(actor, expected_map):
    checks = []
    failures = []
    for row in get_ism_rows(actor):
        expected = expected_map.get(row["mesh"], [])
        if row["count"] <= 0 or not expected:
            continue
        actual = row["materials"][:len(expected)]
        match = actual == expected
        check = {
            "mesh": row["mesh"],
            "component": row["component"],
            "expected": expected,
            "actual": actual,
            "match": match,
        }
        checks.append(check)
        if not match:
            failures.append(check)
    return checks, failures


def validate_validation_actor(config, spec):
    label = f"{config['ACTOR_LABEL_PREFIX']}_{spec['name']}_Validation"
    actor = find_actor(label)
    if not actor:
        raise RuntimeError(f"Missing true material validation actor: {label}")
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {label}")
    point_count = get_generated_point_count(pcg_components[0])
    ism_rows = get_ism_rows(actor)
    total_ism = sum(max(0, row["count"]) for row in ism_rows)
    slot_checks, slot_failures = validate_generated_slots(actor, spec["expected_override_map"])
    validation_pass = all([
        point_count == spec["expected_points"],
        total_ism == spec["expected_ism"],
        not slot_failures,
    ])
    return {
        "name": spec["name"],
        "kind": spec["kind"],
        "actor": label,
        "graph": spec["graph_path"],
        "point_count": point_count,
        "expected_points": spec["expected_points"],
        "total_ism": total_ism,
        "expected_ism": spec["expected_ism"],
        "slot_checks": slot_checks,
        "slot_failures": slot_failures,
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
    config = load_builder_config()
    style_amount_failures = validate_style_amount_graphs(config)
    style_matrix_failures = validate_style_matrix_graphs(config)
    tree_failures = validate_tree_graphs(config)
    validation_results = [
        validate_validation_actor(config, spec)
        for spec in config["VALIDATION_SPECS"]
    ]
    log_path, marker_found, log_errors = scan_latest_log("MCP_CUBELESS_ED_TRUE_MATERIAL_APPLIED_BUILD_BEGIN")
    validation_pass = all([
        not style_amount_failures,
        not style_matrix_failures,
        not tree_failures,
        all(result["validation_pass"] for result in validation_results),
        not log_errors,
    ])

    print(f"true_material_style_amount_graph_count={24}")
    print(f"true_material_style_matrix_graph_count={len(config['TRUE_STYLE_MATRIX_SPECS'])}")
    print(f"true_material_tree_graph_count={len(config['TRUE_TREE_SPECS'])}")
    print(f"style_amount_failure_count={len(style_amount_failures)}")
    for failure in style_amount_failures[:20]:
        print(f"style_amount_failure={failure}")
    print(f"style_matrix_failure_count={len(style_matrix_failures)}")
    for failure in style_matrix_failures[:20]:
        print(f"style_matrix_failure={failure}")
    print(f"tree_failure_count={len(tree_failures)}")
    for failure in tree_failures[:20]:
        print(f"tree_failure={failure}")

    for result in validation_results:
        print(f"true_material_validation={result['name']}")
        print(f"  kind={result['kind']}")
        print(f"  actor={result['actor']}")
        print(f"  graph={result['graph']}")
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  total_ism={result['total_ism']}")
        print(f"  expected_ism={result['expected_ism']}")
        print(f"  slot_checks={result['slot_checks']}")
        print(f"  slot_failures={result['slot_failures']}")
        print(f"  validation_pass={result['validation_pass']}")

    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"true_material_applied_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_TRUE_MATERIAL_APPLIED_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED true material applied presets verification failed")


if __name__ == "__main__":
    main()
