import pathlib
from collections import defaultdict

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_ground_amount_presets.py",
    )
).resolve().parent

BUILDER_SCRIPT = str(SCRIPT_DIR / "build_cubeless_ed_ground_amount_presets.py")
VERIFY_MARKER = "MCP_CUBELESS_ED_GROUND_AMOUNT_PRESETS_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_cubeless_ed_ground_amount_presets_config"}
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


def vector_tuple(vector):
    return (
        round(float(vector.get_editor_property("x")), 3),
        round(float(vector.get_editor_property("y")), 3),
        round(float(vector.get_editor_property("z")), 3),
    )


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


def get_point_rows(point_data):
    metadata = point_data.const_metadata()
    point_count = point_data.get_num_points()
    input_range = unreal.PCGPointInputRange()
    input_range.set_editor_property("point_data", point_data)
    input_range.set_editor_property("range_start_index", 0)
    input_range.set_editor_property("range_size", point_count)

    entries = list(point_data.get_metadata_entry_values_from_range(input_range))
    seeds = list(point_data.get_seed_values_from_range(input_range))
    densities = list(point_data.get_density_values_from_range(input_range))
    transforms = list(point_data.get_transform_values_from_range(input_range))
    helpers = unreal.PCGMetadataAccessorHelpers
    rows = []
    for idx, entry in enumerate(entries):
        entry = int(entry)
        transform = transforms[idx]
        rows.append({
            "metadata_entry": entry,
            "seed": int(seeds[idx]),
            "density": round(float(densities[idx]), 3),
            "translation": vector_tuple(transform.get_editor_property("translation")),
            "bounds_profile_id": int(
                helpers.get_integer32_attribute_by_metadata_key(entry, metadata, "BoundsProfileId")
            ),
            "designer_profile_id": int(
                helpers.get_integer32_attribute_by_metadata_key(entry, metadata, "DesignerProfileId")
            ),
            "designer_profile_type": int(
                helpers.get_integer32_attribute_by_metadata_key(entry, metadata, "DesignerProfileType")
            ),
            "designer_amount_id": int(
                helpers.get_integer32_attribute_by_metadata_key(entry, metadata, "DesignerAmountId")
            ),
            "designer_amount_type": int(
                helpers.get_integer32_attribute_by_metadata_key(entry, metadata, "DesignerAmountType")
            ),
            "designer_amount_pass": bool(
                helpers.get_bool_attribute_by_metadata_key(entry, metadata, "DesignerAmountPass")
            ),
            "cubeless_ground_controls_pass": bool(
                helpers.get_bool_attribute_by_metadata_key(entry, metadata, "CubelessGroundControlsPass")
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


def validate_amount(spec, config):
    graph = unreal.EditorAssetLibrary.load_asset(config["AMOUNT_GRAPH_PATHS"][spec["name"]])
    if not graph:
        raise RuntimeError(f"Missing amount graph: {spec['name']}")
    label = f"{config['ACTOR_LABEL_PREFIX']}_{spec['name']}_Validation"
    actor = get_actor(label)
    component = actor.get_components_by_class(unreal.PCGComponent)[0]
    rows = get_point_rows(get_generated_point_data(component))
    ism_rows = get_ism_rows(actor)

    profile_counts = defaultdict(int)
    amount_counts = defaultdict(int)
    for row in rows:
        profile_counts[row["designer_profile_id"]] += 1
        amount_counts[row["designer_amount_id"]] += 1

    amount_pass_count = sum(1 for row in rows if row["designer_amount_pass"])
    ground_pass_count = sum(1 for row in rows if row["cubeless_ground_controls_pass"])
    profile_type_mismatch_count = sum(
        1 for row in rows
        if row["designer_profile_id"] != config["PROFILE_ID"]
        or row["designer_profile_type"] != config["PROFILE_TYPE"]
    )
    amount_mismatch_count = sum(
        1 for row in rows
        if row["designer_amount_id"] != spec["amount_id"]
        or row["designer_amount_type"] != spec["amount_type"]
    )
    sparse_density_mismatch_count = 0
    if spec["density_filter"]:
        lower, upper = spec["density_filter"]
        sparse_density_mismatch_count = sum(
            1 for row in rows
            if row["density"] < float(lower) - 0.005 or row["density"] > float(upper) + 0.005
        )
    total_ism_instances = sum(max(0, count) for _, _, count in ism_rows)
    validation_pass = all([
        len(rows) == spec["expected_points"],
        total_ism_instances == spec["expected_ism"],
        dict(profile_counts) == {config["PROFILE_ID"]: spec["expected_points"]},
        dict(amount_counts) == {spec["amount_id"]: spec["expected_points"]},
        amount_pass_count == spec["expected_points"],
        ground_pass_count == spec["expected_points"],
        profile_type_mismatch_count == 0,
        amount_mismatch_count == 0,
        sparse_density_mismatch_count == 0,
    ])
    return {
        "amount": spec["name"],
        "actor": label,
        "graph": config["AMOUNT_GRAPH_PATHS"][spec["name"]],
        "point_count": len(rows),
        "expected_points": spec["expected_points"],
        "total_ism_instances": total_ism_instances,
        "expected_ism": spec["expected_ism"],
        "profile_counts": dict(profile_counts),
        "amount_counts": dict(amount_counts),
        "amount_pass_count": amount_pass_count,
        "ground_pass_count": ground_pass_count,
        "profile_type_mismatch_count": profile_type_mismatch_count,
        "amount_mismatch_count": amount_mismatch_count,
        "sparse_density_mismatch_count": sparse_density_mismatch_count,
        "ism_rows": ism_rows,
        "validation_pass": validation_pass,
        "rows_sample": sorted(rows, key=lambda item: (item["designer_amount_id"], item["seed"], item["translation"]))[:16],
    }


def main():
    config = load_builder_config()
    core = unreal.EditorAssetLibrary.load_asset(config["CORE_GRAPH_PATH"])
    if not core:
        raise RuntimeError(f"Missing core graph: {config['CORE_GRAPH_PATH']}")

    results = [validate_amount(spec, config) for spec in config["AMOUNT_SPECS"]]
    log_path, marker_found, log_errors = scan_latest_log("MCP_CUBELESS_ED_GROUND_AMOUNT_PRESETS_BUILD_BEGIN")
    validation_pass = all(result["validation_pass"] for result in results) and not log_errors

    print(VERIFY_MARKER)
    print(f"core_graph={config['CORE_GRAPH_PATH']}")
    print(f"amount_graph_paths={config['AMOUNT_GRAPH_PATHS']}")
    for result in results:
        print(f"amount={result['amount']}")
        print(f"  graph={result['graph']}")
        print(f"  actor={result['actor']}")
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  total_ism_instances={result['total_ism_instances']}")
        print(f"  expected_ism={result['expected_ism']}")
        print(f"  profile_counts={result['profile_counts']}")
        print(f"  amount_counts={result['amount_counts']}")
        print(f"  amount_pass_count={result['amount_pass_count']}")
        print(f"  ground_pass_count={result['ground_pass_count']}")
        print(f"  profile_type_mismatch_count={result['profile_type_mismatch_count']}")
        print(f"  amount_mismatch_count={result['amount_mismatch_count']}")
        print(f"  sparse_density_mismatch_count={result['sparse_density_mismatch_count']}")
        print(f"  ism_rows={result['ism_rows']}")
        print(f"  validation_pass={result['validation_pass']}")
        print("  rows_sample=")
        for row in result["rows_sample"]:
            print(
                "    Amount={designer_amount_id}/{designer_amount_type} "
                "Profile={designer_profile_id}/{designer_profile_type} "
                "Seed={seed} Density={density} Translation={translation} "
                "AmountPass={designer_amount_pass} GroundPass={cubeless_ground_controls_pass}".format(**row)
            )
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"ground_amount_presets_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_GROUND_AMOUNT_PRESETS_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED ground amount preset verification failed")


if __name__ == "__main__":
    main()
