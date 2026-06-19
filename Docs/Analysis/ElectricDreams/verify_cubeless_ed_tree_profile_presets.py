import pathlib
from collections import defaultdict

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_tree_profile_presets.py",
    )
).parent
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_tree_profile_presets.py"
VERIFY_MARKER = "MCP_CUBELESS_ED_TREE_PROFILE_PRESETS_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_cubeless_ed_tree_profile_presets_config", "__file__": str(BUILDER_SCRIPT)}
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


def get_actor(label):
    for actor in get_all_level_actors():
        if actor.get_actor_label() == label:
            return actor
    raise RuntimeError(f"Missing actor: {label}")


def get_generated_point_data(component):
    for attempt in range(4):
        collection = component.get_generated_graph_output()
        for item in collection.get_editor_property("tagged_data"):
            data = item.get_editor_property("data").get_editor_property("data")
            if data and hasattr(data, "get_num_points"):
                return data
        if attempt < 3:
            component.generate(True)
    raise RuntimeError("No generated point data found")


def get_int_attr(helpers, entry, metadata, name):
    try:
        return int(helpers.get_integer32_attribute_by_metadata_key(entry, metadata, name))
    except Exception:
        return None


def get_bool_attr(helpers, entry, metadata, name):
    try:
        return bool(helpers.get_bool_attribute_by_metadata_key(entry, metadata, name))
    except Exception:
        return False


def get_double_attr(helpers, entry, metadata, name):
    try:
        return float(helpers.get_double_attribute_by_metadata_key(entry, metadata, name))
    except Exception:
        return None


def get_point_rows(point_data):
    metadata = point_data.const_metadata()
    point_count = point_data.get_num_points()
    input_range = unreal.PCGPointInputRange()
    input_range.set_editor_property("point_data", point_data)
    input_range.set_editor_property("range_start_index", 0)
    input_range.set_editor_property("range_size", point_count)

    entries = list(point_data.get_metadata_entry_values_from_range(input_range))
    helpers = unreal.PCGMetadataAccessorHelpers
    rows = []
    for entry in entries:
        entry = int(entry)
        rows.append({
            "designer_profile_id": get_int_attr(helpers, entry, metadata, "DesignerProfileId"),
            "designer_profile_type": get_int_attr(helpers, entry, metadata, "DesignerProfileType"),
            "designer_amount_id": get_int_attr(helpers, entry, metadata, "DesignerAmountId"),
            "designer_amount_type": get_int_attr(helpers, entry, metadata, "DesignerAmountType"),
            "designer_tree_style_id": get_int_attr(helpers, entry, metadata, "DesignerTreeStyleId"),
            "designer_tree_style_type": get_int_attr(helpers, entry, metadata, "DesignerTreeStyleType"),
            "designer_tree_profile_id": get_int_attr(helpers, entry, metadata, "DesignerTreeProfileId"),
            "designer_tree_profile_type": get_int_attr(helpers, entry, metadata, "DesignerTreeProfileType"),
            "designer_amount_pass": get_bool_attr(helpers, entry, metadata, "DesignerAmountPass"),
            "designer_tree_style_pass": get_bool_attr(helpers, entry, metadata, "DesignerTreeStylePass"),
            "designer_tree_profile_pass": get_bool_attr(helpers, entry, metadata, "DesignerTreeProfilePass"),
            "designer_tree_min_spacing": get_double_attr(helpers, entry, metadata, "DesignerTreeMinSpacing"),
        })
    return rows


def get_ism_rows(actor):
    rows = []
    for component in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
        mesh = component.get_editor_property("static_mesh")
        mesh_path = mesh.get_path_name() if mesh else "None"
        try:
            count = int(component.get_instance_count())
        except Exception:
            count = -1
        rows.append((component.get_name(), mesh_path, count))
    return rows


def get_spawner_mesh_paths(graph_path):
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        raise RuntimeError(f"Missing graph for spawner check: {graph_path}")
    mesh_paths = set()
    for node in graph.get_editor_property("nodes"):
        settings = node.get_settings()
        if not settings or settings.get_class().get_name() != "PCGStaticMeshSpawnerSettings":
            continue
        params = settings.get_editor_property("mesh_selector_parameters")
        for entry in params.get_editor_property("mesh_entries"):
            descriptor = entry.get_editor_property("descriptor")
            mesh = descriptor.get_editor_property("static_mesh") if descriptor else None
            if mesh:
                mesh_paths.add(mesh.get_path_name())
    return mesh_paths


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


def validate_tree_profile(spec, config):
    graph_path = config["TREE_PROFILE_GRAPH_PATHS"][spec["name"]]
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        raise RuntimeError(f"Missing tree profile graph: {graph_path}")

    label = f"{config['ACTOR_LABEL_PREFIX']}_{spec['name']}_Validation"
    actor = get_actor(label)
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {label}")

    rows = get_point_rows(get_generated_point_data(pcg_components[0]))
    ism_rows = get_ism_rows(actor)
    total_ism_instances = sum(max(0, count) for _, _, count in ism_rows)

    profile_counts = defaultdict(int)
    amount_counts = defaultdict(int)
    style_counts = defaultdict(int)
    for row in rows:
        profile_counts[row["designer_profile_id"]] += 1
        amount_counts[row["designer_amount_id"]] += 1
        style_counts[row["designer_tree_style_id"]] += 1

    positive_mesh_paths = {
        mesh_path
        for _, mesh_path, count in ism_rows
        if count > 0
    }
    expected_mesh_paths = set(spec["mesh_paths"])
    spawner_mesh_paths = get_spawner_mesh_paths(graph_path)
    min_spacing_mismatch_count = sum(
        1 for row in rows
        if row["designer_tree_min_spacing"] is None
        or abs(row["designer_tree_min_spacing"] - spec["min_spacing"]) > 0.01
    )

    mismatch_counts = {
        "profile_type": sum(1 for row in rows if row["designer_profile_type"] != spec["profile_type"]),
        "amount_type": sum(1 for row in rows if row["designer_amount_type"] != spec["amount_type"]),
        "tree_style_id": sum(1 for row in rows if row["designer_tree_style_id"] != spec["style_id"]),
        "tree_style_type": sum(1 for row in rows if row["designer_tree_style_type"] != spec["style_type"]),
        "tree_profile_id": sum(1 for row in rows if row["designer_tree_profile_id"] != spec["tree_profile_id"]),
        "tree_profile_type": sum(
            1 for row in rows if row["designer_tree_profile_type"] != spec["tree_profile_type"]
        ),
        "tree_min_spacing": min_spacing_mismatch_count,
    }
    pass_counts = {
        "amount": sum(1 for row in rows if row["designer_amount_pass"]),
        "tree_style": sum(1 for row in rows if row["designer_tree_style_pass"]),
        "tree_profile": sum(1 for row in rows if row["designer_tree_profile_pass"]),
    }

    mesh_paths_allowed = bool(positive_mesh_paths) and positive_mesh_paths.issubset(expected_mesh_paths)
    validation_pass = all([
        len(rows) == spec["expected_points"],
        total_ism_instances == spec["expected_ism"],
        dict(profile_counts) == {spec["profile_id"]: spec["expected_points"]},
        dict(amount_counts) == {spec["amount_id"]: spec["expected_points"]},
        dict(style_counts) == {spec["style_id"]: spec["expected_points"]},
        spawner_mesh_paths == expected_mesh_paths,
        mesh_paths_allowed,
        all(count == 0 for count in mismatch_counts.values()),
        all(count == spec["expected_points"] for count in pass_counts.values()),
        spec["min_spacing"] == 0.0 or spec["min_spacing"] >= 1500.0,
    ])
    return {
        "tree_profile": spec["name"],
        "actor": label,
        "graph": graph_path,
        "style": f"{spec['style_id']}/{spec['style_type']}",
        "amount": f"{spec['amount_id']}/{spec['amount_type']}",
        "point_count": len(rows),
        "expected_points": spec["expected_points"],
        "total_ism_instances": total_ism_instances,
        "expected_ism": spec["expected_ism"],
        "profile_counts": dict(profile_counts),
        "amount_counts": dict(amount_counts),
        "style_counts": dict(style_counts),
        "mesh_paths": sorted(positive_mesh_paths),
        "expected_mesh_paths": sorted(expected_mesh_paths),
        "spawner_mesh_paths": sorted(spawner_mesh_paths),
        "mesh_paths_allowed": mesh_paths_allowed,
        "min_spacing": spec["min_spacing"],
        "mismatch_counts": mismatch_counts,
        "pass_counts": pass_counts,
        "ism_rows": ism_rows,
        "validation_pass": validation_pass,
    }


def main():
    print(VERIFY_MARKER)
    config = load_builder_config()
    print(f"tree_profile_graph_count={len(config['TREE_PROFILE_GRAPH_PATHS'])}")
    results = [validate_tree_profile(spec, config) for spec in config["TREE_PROFILE_SPECS"]]
    log_path, marker_found, log_errors = scan_latest_log("MCP_CUBELESS_ED_TREE_PROFILE_PRESETS_BUILD_BEGIN")
    validation_pass = all(result["validation_pass"] for result in results) and not log_errors

    for result in results:
        print(f"tree_profile={result['tree_profile']}")
        print(f"  actor={result['actor']}")
        print(f"  graph={result['graph']}")
        print(f"  style={result['style']}")
        print(f"  amount={result['amount']}")
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  total_ism_instances={result['total_ism_instances']}")
        print(f"  expected_ism={result['expected_ism']}")
        print(f"  profile_counts={result['profile_counts']}")
        print(f"  amount_counts={result['amount_counts']}")
        print(f"  style_counts={result['style_counts']}")
        print(f"  mesh_paths={result['mesh_paths']}")
        print(f"  expected_mesh_paths={result['expected_mesh_paths']}")
        print(f"  spawner_mesh_paths={result['spawner_mesh_paths']}")
        print(f"  mesh_paths_allowed={result['mesh_paths_allowed']}")
        print(f"  min_spacing={result['min_spacing']}")
        print(f"  mismatch_counts={result['mismatch_counts']}")
        print(f"  pass_counts={result['pass_counts']}")
        print(f"  ism_rows={result['ism_rows']}")
        print(f"  validation_pass={result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"tree_profile_presets_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_TREE_PROFILE_PRESETS_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED tree profile presets verification failed")


if __name__ == "__main__":
    main()
