import pathlib
from collections import defaultdict

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_style_profile_matrix_presets.py",
    )
).resolve().parent

BUILDER_SCRIPT = str(SCRIPT_DIR / "build_cubeless_ed_style_profile_matrix_presets.py")
VERIFY_MARKER = "MCP_CUBELESS_ED_STYLE_PROFILE_MATRIX_PRESETS_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_cubeless_ed_style_profile_matrix_presets_config"}
    with open(BUILDER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), BUILDER_SCRIPT, "exec")
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
            "designer_amount_id": get_int_attr(helpers, entry, metadata, "DesignerAmountId"),
            "designer_visual_style_id": get_int_attr(helpers, entry, metadata, "DesignerVisualStyleId"),
            "designer_visual_style_type": get_int_attr(helpers, entry, metadata, "DesignerVisualStyleType"),
            "designer_profile_mode": get_int_attr(helpers, entry, metadata, "DesignerProfileMode"),
            "designer_ground_amount_type": get_int_attr(helpers, entry, metadata, "DesignerGroundAmountType"),
            "designer_ditch_amount_type": get_int_attr(helpers, entry, metadata, "DesignerDitchAmountType"),
            "designer_profile_matrix_id": get_int_attr(helpers, entry, metadata, "DesignerProfileMatrixId"),
            "designer_profile_matrix_type": get_int_attr(helpers, entry, metadata, "DesignerProfileMatrixType"),
            "designer_style_profile_matrix_id": get_int_attr(
                helpers, entry, metadata, "DesignerStyleProfileMatrixId"
            ),
            "designer_style_profile_matrix_type": get_int_attr(
                helpers, entry, metadata, "DesignerStyleProfileMatrixType"
            ),
            "designer_amount_pass": get_bool_attr(helpers, entry, metadata, "DesignerAmountPass"),
            "designer_visual_style_pass": get_bool_attr(helpers, entry, metadata, "DesignerVisualStylePass"),
            "designer_profile_matrix_pass": get_bool_attr(helpers, entry, metadata, "DesignerProfileMatrixPass"),
            "designer_style_profile_matrix_pass": get_bool_attr(
                helpers, entry, metadata, "DesignerStyleProfileMatrixPass"
            ),
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
        if not settings:
            continue
        settings_class = settings.get_class().get_name()
        if settings_class != "PCGStaticMeshSpawnerSettings":
            continue
        params = settings.get_editor_property("mesh_selector_parameters")
        for entry in params.get_editor_property("mesh_entries"):
            descriptor = entry.get_editor_property("descriptor")
            mesh = descriptor.get_editor_property("static_mesh") if descriptor else None
            if mesh:
                mesh_paths.add(mesh.get_path_name())
    return mesh_paths


def validate_style_amount_spawners(config):
    results = []
    amount_groups = [
        ("Ground", config["GROUND_AMOUNT_SPECS"]),
        ("Ditch", config["DITCH_AMOUNT_SPECS"]),
    ]
    for style in config["STYLE_SPECS"]:
        expected_mesh_paths = set(style["mesh_paths"])
        for profile_key, amount_specs in amount_groups:
            for amount in amount_specs:
                graph_path = config["STYLE_AMOUNT_GRAPH_PATHS"][
                    (profile_key, style["style_type"], amount["amount_type"])
                ]
                actual_mesh_paths = get_spawner_mesh_paths(graph_path)
                results.append({
                    "style": style["name"],
                    "profile": profile_key,
                    "amount": amount["short_name"],
                    "graph": graph_path,
                    "mesh_paths": sorted(actual_mesh_paths),
                    "expected_mesh_paths": sorted(expected_mesh_paths),
                    "validation_pass": actual_mesh_paths == expected_mesh_paths,
                })
    return results


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


def validate_style_profile_matrix(spec, config):
    graph_path = config["STYLE_PROFILE_MATRIX_GRAPH_PATHS"][spec["name"]]
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        raise RuntimeError(f"Missing style profile matrix graph: {graph_path}")

    label = f"{config['ACTOR_LABEL_PREFIX']}_{spec['name']}_Validation"
    actor = get_actor(label)
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {label}")

    rows = get_point_rows(get_generated_point_data(pcg_components[0]))
    ism_rows = get_ism_rows(actor)

    profile_counts = defaultdict(int)
    amount_counts = defaultdict(int)
    style_counts = defaultdict(int)
    for row in rows:
        profile_counts[row["designer_profile_id"]] += 1
        amount_counts[row["designer_amount_id"]] += 1
        style_counts[row["designer_visual_style_id"]] += 1

    total_ism_instances = sum(max(0, count) for _, _, count in ism_rows)
    positive_mesh_paths = {
        mesh_path
        for _, mesh_path, count in ism_rows
        if count > 0
    }
    expected_mesh_paths = set(spec["mesh_paths"])
    mesh_paths_allowed = bool(positive_mesh_paths) and positive_mesh_paths.issubset(expected_mesh_paths)
    profile_mode_mismatch_count = sum(1 for row in rows if row["designer_profile_mode"] != spec["profile_mode"])
    ground_axis_mismatch_count = sum(
        1 for row in rows
        if row["designer_ground_amount_type"] != spec["ground_amount_type"]
    )
    ditch_axis_mismatch_count = sum(
        1 for row in rows
        if row["designer_ditch_amount_type"] != spec["ditch_amount_type"]
    )
    visual_style_id_mismatch_count = sum(
        1 for row in rows
        if row["designer_visual_style_id"] != spec["style_id"]
    )
    visual_style_type_mismatch_count = sum(
        1 for row in rows
        if row["designer_visual_style_type"] != spec["style_type"]
    )
    profile_matrix_id_mismatch_count = sum(
        1 for row in rows
        if row["designer_profile_matrix_id"] != spec["profile_matrix_id"]
    )
    profile_matrix_type_mismatch_count = sum(
        1 for row in rows
        if row["designer_profile_matrix_type"] != spec["profile_matrix_type"]
    )
    style_profile_matrix_id_mismatch_count = sum(
        1 for row in rows
        if row["designer_style_profile_matrix_id"] != spec["style_profile_matrix_id"]
    )
    style_profile_matrix_type_mismatch_count = sum(
        1 for row in rows
        if row["designer_style_profile_matrix_type"] != spec["style_profile_matrix_type"]
    )
    amount_pass_count = sum(1 for row in rows if row["designer_amount_pass"])
    visual_style_pass_count = sum(1 for row in rows if row["designer_visual_style_pass"])
    profile_matrix_pass_count = sum(1 for row in rows if row["designer_profile_matrix_pass"])
    style_profile_matrix_pass_count = sum(1 for row in rows if row["designer_style_profile_matrix_pass"])

    validation_pass = all([
        len(rows) == spec["expected_points"],
        total_ism_instances == spec["expected_ism"],
        dict(profile_counts) == spec["expected_profile_counts"],
        dict(amount_counts) == spec["expected_amount_counts"],
        dict(style_counts) == {spec["style_id"]: spec["expected_points"]},
        mesh_paths_allowed,
        profile_mode_mismatch_count == 0,
        ground_axis_mismatch_count == 0,
        ditch_axis_mismatch_count == 0,
        visual_style_id_mismatch_count == 0,
        visual_style_type_mismatch_count == 0,
        profile_matrix_id_mismatch_count == 0,
        profile_matrix_type_mismatch_count == 0,
        style_profile_matrix_id_mismatch_count == 0,
        style_profile_matrix_type_mismatch_count == 0,
        amount_pass_count == spec["expected_points"],
        visual_style_pass_count == spec["expected_points"],
        profile_matrix_pass_count == spec["expected_points"],
        style_profile_matrix_pass_count == spec["expected_points"],
    ])

    return {
        "style_profile_matrix": spec["name"],
        "actor": label,
        "graph": graph_path,
        "style_type": spec["style_type"],
        "style_id": spec["style_id"],
        "profile_mode": spec["profile_mode"],
        "ground_amount_type": spec["ground_amount_type"],
        "ditch_amount_type": spec["ditch_amount_type"],
        "point_count": len(rows),
        "expected_points": spec["expected_points"],
        "total_ism_instances": total_ism_instances,
        "expected_ism": spec["expected_ism"],
        "profile_counts": dict(profile_counts),
        "amount_counts": dict(amount_counts),
        "style_counts": dict(style_counts),
        "mesh_paths": sorted(positive_mesh_paths),
        "expected_mesh_paths": sorted(expected_mesh_paths),
        "mesh_paths_allowed": mesh_paths_allowed,
        "profile_mode_mismatch_count": profile_mode_mismatch_count,
        "ground_axis_mismatch_count": ground_axis_mismatch_count,
        "ditch_axis_mismatch_count": ditch_axis_mismatch_count,
        "visual_style_id_mismatch_count": visual_style_id_mismatch_count,
        "visual_style_type_mismatch_count": visual_style_type_mismatch_count,
        "profile_matrix_id_mismatch_count": profile_matrix_id_mismatch_count,
        "profile_matrix_type_mismatch_count": profile_matrix_type_mismatch_count,
        "style_profile_matrix_id_mismatch_count": style_profile_matrix_id_mismatch_count,
        "style_profile_matrix_type_mismatch_count": style_profile_matrix_type_mismatch_count,
        "amount_pass_count": amount_pass_count,
        "visual_style_pass_count": visual_style_pass_count,
        "profile_matrix_pass_count": profile_matrix_pass_count,
        "style_profile_matrix_pass_count": style_profile_matrix_pass_count,
        "ism_rows": ism_rows,
        "validation_pass": validation_pass,
    }


def main():
    config = load_builder_config()
    print(VERIFY_MARKER)
    print(f"style_profile_matrix_graph_count={len(config['STYLE_PROFILE_MATRIX_GRAPH_PATHS'])}")

    for graph_path in config["STYLE_PROFILE_MATRIX_GRAPH_PATHS"].values():
        if not unreal.EditorAssetLibrary.load_asset(graph_path):
            raise RuntimeError(f"Missing style profile matrix graph: {graph_path}")

    spawner_results = validate_style_amount_spawners(config)
    results = [
        validate_style_profile_matrix(spec, config)
        for spec in config["STYLE_PROFILE_MATRIX_SPECS"]
    ]
    log_path, marker_found, log_errors = scan_latest_log(
        "MCP_CUBELESS_ED_STYLE_PROFILE_MATRIX_PRESETS_BUILD_BEGIN"
    )
    validation_pass = (
        all(result["validation_pass"] for result in spawner_results)
        and all(result["validation_pass"] for result in results)
        and not log_errors
    )

    for result in spawner_results:
        print(f"style_amount_spawner={result['style']}_{result['profile']}_{result['amount']}")
        print(f"  graph={result['graph']}")
        print(f"  mesh_paths={result['mesh_paths']}")
        print(f"  expected_mesh_paths={result['expected_mesh_paths']}")
        print(f"  validation_pass={result['validation_pass']}")
    for result in results:
        print(f"style_profile_matrix={result['style_profile_matrix']}")
        print(f"  actor={result['actor']}")
        print(f"  graph={result['graph']}")
        print(f"  style={result['style_id']}/{result['style_type']}")
        print(
            "  axes=profile:{profile_mode} ground:{ground_amount_type} ditch:{ditch_amount_type}".format(**result)
        )
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  total_ism_instances={result['total_ism_instances']}")
        print(f"  expected_ism={result['expected_ism']}")
        print(f"  profile_counts={result['profile_counts']}")
        print(f"  amount_counts={result['amount_counts']}")
        print(f"  style_counts={result['style_counts']}")
        print(f"  mesh_paths={result['mesh_paths']}")
        print(f"  expected_mesh_paths={result['expected_mesh_paths']}")
        print(f"  mesh_paths_allowed={result['mesh_paths_allowed']}")
        print(f"  profile_mode_mismatch_count={result['profile_mode_mismatch_count']}")
        print(f"  ground_axis_mismatch_count={result['ground_axis_mismatch_count']}")
        print(f"  ditch_axis_mismatch_count={result['ditch_axis_mismatch_count']}")
        print(f"  visual_style_id_mismatch_count={result['visual_style_id_mismatch_count']}")
        print(f"  visual_style_type_mismatch_count={result['visual_style_type_mismatch_count']}")
        print(f"  profile_matrix_id_mismatch_count={result['profile_matrix_id_mismatch_count']}")
        print(f"  profile_matrix_type_mismatch_count={result['profile_matrix_type_mismatch_count']}")
        print(
            "  style_profile_matrix_id_mismatch_count="
            f"{result['style_profile_matrix_id_mismatch_count']}"
        )
        print(
            "  style_profile_matrix_type_mismatch_count="
            f"{result['style_profile_matrix_type_mismatch_count']}"
        )
        print(f"  amount_pass_count={result['amount_pass_count']}")
        print(f"  visual_style_pass_count={result['visual_style_pass_count']}")
        print(f"  profile_matrix_pass_count={result['profile_matrix_pass_count']}")
        print(f"  style_profile_matrix_pass_count={result['style_profile_matrix_pass_count']}")
        print(f"  ism_rows={result['ism_rows']}")
        print(f"  validation_pass={result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"style_profile_matrix_presets_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_STYLE_PROFILE_MATRIX_PRESETS_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED style profile matrix presets verification failed")


if __name__ == "__main__":
    main()
