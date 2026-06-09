import pathlib
from collections import defaultdict

import unreal


BUILDER_SCRIPT = r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\build_cubeless_ed_profile_matrix_presets.py"
VERIFY_MARKER = "MCP_CUBELESS_ED_PROFILE_MATRIX_PRESETS_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_cubeless_ed_profile_matrix_presets_config"}
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
            "designer_profile_mode": get_int_attr(helpers, entry, metadata, "DesignerProfileMode"),
            "designer_ground_amount_type": get_int_attr(helpers, entry, metadata, "DesignerGroundAmountType"),
            "designer_ditch_amount_type": get_int_attr(helpers, entry, metadata, "DesignerDitchAmountType"),
            "designer_profile_matrix_id": get_int_attr(helpers, entry, metadata, "DesignerProfileMatrixId"),
            "designer_profile_matrix_type": get_int_attr(helpers, entry, metadata, "DesignerProfileMatrixType"),
            "designer_profile_matrix_pass": get_bool_attr(helpers, entry, metadata, "DesignerProfileMatrixPass"),
            "designer_amount_pass": get_bool_attr(helpers, entry, metadata, "DesignerAmountPass"),
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


def validate_profile_matrix(spec, config):
    graph = unreal.EditorAssetLibrary.load_asset(config["PROFILE_MATRIX_GRAPH_PATHS"][spec["name"]])
    if not graph:
        raise RuntimeError(f"Missing profile matrix graph: {spec['name']}")

    label = f"{config['ACTOR_LABEL_PREFIX']}_{spec['name']}_Validation"
    actor = get_actor(label)
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {label}")

    rows = get_point_rows(get_generated_point_data(pcg_components[0]))
    ism_rows = get_ism_rows(actor)

    profile_counts = defaultdict(int)
    amount_counts = defaultdict(int)
    for row in rows:
        profile_counts[row["designer_profile_id"]] += 1
        amount_counts[row["designer_amount_id"]] += 1

    total_ism_instances = sum(max(0, count) for _, _, count in ism_rows)
    profile_mode_mismatch_count = sum(1 for row in rows if row["designer_profile_mode"] != spec["profile_mode"])
    ground_axis_mismatch_count = sum(
        1 for row in rows
        if row["designer_ground_amount_type"] != spec["ground_amount_type"]
    )
    ditch_axis_mismatch_count = sum(
        1 for row in rows
        if row["designer_ditch_amount_type"] != spec["ditch_amount_type"]
    )
    profile_matrix_id_mismatch_count = sum(
        1 for row in rows
        if row["designer_profile_matrix_id"] != spec["profile_matrix_id"]
    )
    profile_matrix_type_mismatch_count = sum(
        1 for row in rows
        if row["designer_profile_matrix_type"] != spec["profile_matrix_type"]
    )
    profile_matrix_pass_count = sum(1 for row in rows if row["designer_profile_matrix_pass"])
    amount_pass_count = sum(1 for row in rows if row["designer_amount_pass"])

    validation_pass = all([
        len(rows) == spec["expected_points"],
        total_ism_instances == spec["expected_ism"],
        dict(profile_counts) == spec["expected_profile_counts"],
        dict(amount_counts) == spec["expected_amount_counts"],
        profile_mode_mismatch_count == 0,
        ground_axis_mismatch_count == 0,
        ditch_axis_mismatch_count == 0,
        profile_matrix_id_mismatch_count == 0,
        profile_matrix_type_mismatch_count == 0,
        profile_matrix_pass_count == spec["expected_points"],
        amount_pass_count == spec["expected_points"],
    ])

    return {
        "profile_matrix": spec["name"],
        "actor": label,
        "graph": config["PROFILE_MATRIX_GRAPH_PATHS"][spec["name"]],
        "profile_mode": spec["profile_mode"],
        "ground_amount_type": spec["ground_amount_type"],
        "ditch_amount_type": spec["ditch_amount_type"],
        "profile_matrix_id": spec["profile_matrix_id"],
        "profile_matrix_type": spec["profile_matrix_type"],
        "point_count": len(rows),
        "expected_points": spec["expected_points"],
        "total_ism_instances": total_ism_instances,
        "expected_ism": spec["expected_ism"],
        "profile_counts": dict(profile_counts),
        "amount_counts": dict(amount_counts),
        "profile_mode_mismatch_count": profile_mode_mismatch_count,
        "ground_axis_mismatch_count": ground_axis_mismatch_count,
        "ditch_axis_mismatch_count": ditch_axis_mismatch_count,
        "profile_matrix_id_mismatch_count": profile_matrix_id_mismatch_count,
        "profile_matrix_type_mismatch_count": profile_matrix_type_mismatch_count,
        "profile_matrix_pass_count": profile_matrix_pass_count,
        "amount_pass_count": amount_pass_count,
        "ism_rows": ism_rows,
        "validation_pass": validation_pass,
    }


def main():
    config = load_builder_config()
    for graph_path in config["PROFILE_MATRIX_GRAPH_PATHS"].values():
        graph = unreal.EditorAssetLibrary.load_asset(graph_path)
        if not graph:
            raise RuntimeError(f"Missing profile matrix graph: {graph_path}")

    results = [validate_profile_matrix(spec, config) for spec in config["PROFILE_MATRIX_SPECS"]]
    log_path, marker_found, log_errors = scan_latest_log("MCP_CUBELESS_ED_PROFILE_MATRIX_PRESETS_BUILD_BEGIN")
    validation_pass = all(result["validation_pass"] for result in results) and not log_errors

    print(VERIFY_MARKER)
    print(f"profile_matrix_graph_paths={config['PROFILE_MATRIX_GRAPH_PATHS']}")
    for result in results:
        print(f"profile_matrix={result['profile_matrix']}")
        print(f"  graph={result['graph']}")
        print(f"  actor={result['actor']}")
        print(
            "  axes=profile:{profile_mode} ground:{ground_amount_type} ditch:{ditch_amount_type}".format(**result)
        )
        print(f"  profile_matrix={result['profile_matrix_id']}/{result['profile_matrix_type']}")
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  total_ism_instances={result['total_ism_instances']}")
        print(f"  expected_ism={result['expected_ism']}")
        print(f"  profile_counts={result['profile_counts']}")
        print(f"  amount_counts={result['amount_counts']}")
        print(f"  profile_mode_mismatch_count={result['profile_mode_mismatch_count']}")
        print(f"  ground_axis_mismatch_count={result['ground_axis_mismatch_count']}")
        print(f"  ditch_axis_mismatch_count={result['ditch_axis_mismatch_count']}")
        print(f"  profile_matrix_id_mismatch_count={result['profile_matrix_id_mismatch_count']}")
        print(f"  profile_matrix_type_mismatch_count={result['profile_matrix_type_mismatch_count']}")
        print(f"  profile_matrix_pass_count={result['profile_matrix_pass_count']}")
        print(f"  amount_pass_count={result['amount_pass_count']}")
        print(f"  ism_rows={result['ism_rows']}")
        print(f"  validation_pass={result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"profile_matrix_presets_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_PROFILE_MATRIX_PRESETS_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED profile matrix presets verification failed")


if __name__ == "__main__":
    main()
