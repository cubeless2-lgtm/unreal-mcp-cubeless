import pathlib
from collections import defaultdict

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_ground_combo_fixture.py",
    )
).resolve().parent

BUILDER_SCRIPT = str(SCRIPT_DIR / "build_ground_combo_fixture.py")
VERIFY_MARKER = "MCP_PCG_GROUND_COMBO_FIXTURE_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_pcg_ground_combo_fixture_config"}
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


def vector_tuple(vector):
    return (
        round(float(vector.get_editor_property("x")), 3),
        round(float(vector.get_editor_property("y")), 3),
        round(float(vector.get_editor_property("z")), 3),
    )


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
    bounds_min = list(point_data.get_bounds_min_values_from_range(input_range))
    bounds_max = list(point_data.get_bounds_max_values_from_range(input_range))
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
            "bounds_min": vector_tuple(bounds_min[idx]),
            "bounds_max": vector_tuple(bounds_max[idx]),
            "bounds_profile_id": int(
                helpers.get_integer32_attribute_by_metadata_key(
                    entry,
                    metadata,
                    "BoundsProfileId",
                )
            ),
            "ground_combo_fixture_pass": bool(
                helpers.get_bool_attribute_by_metadata_key(
                    entry,
                    metadata,
                    "GroundComboFixturePass",
                )
            ),
        })
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


def main():
    config = load_builder_config()
    source_points = config["SOURCE_POINTS"]
    source_count = len(source_points)
    expected_density_by_seed = {
        int(spec["seed"]): round(float(config["expected_density"](spec["density"])), 3)
        for spec in source_points
    }
    profile_by_id = {
        int(spec["id"]): name
        for name, spec in config["BOUNDS_PROFILES"].items()
    }
    expected_bounds_by_profile_id = {
        int(spec["id"]): (
            tuple(round(float(value), 3) for value in spec["bounds_min"]),
            tuple(round(float(value), 3) for value in spec["bounds_max"]),
        )
        for spec in config["BOUNDS_PROFILES"].values()
    }

    try:
        actor = get_actor(config["ACTOR_LABEL"])
    except RuntimeError:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(config["LEVEL"])
        actor = get_actor(config["ACTOR_LABEL"])

    component = actor.get_components_by_class(unreal.PCGComponent)[0]
    point_data = get_generated_point_data(component)
    rows = get_point_rows(point_data)

    rows_by_profile = defaultdict(list)
    for row in rows:
        rows_by_profile[row["bounds_profile_id"]].append(row)

    profile_counts = {
        profile_by_id.get(profile_id, f"unknown_{profile_id}"): len(profile_rows)
        for profile_id, profile_rows in sorted(rows_by_profile.items())
    }
    profile_seeds = {
        profile_by_id.get(profile_id, f"unknown_{profile_id}"): sorted(row["seed"] for row in profile_rows)
        for profile_id, profile_rows in sorted(rows_by_profile.items())
    }
    pass_count = sum(1 for row in rows if row["ground_combo_fixture_pass"])
    unknown_profile_count = sum(1 for row in rows if row["bounds_profile_id"] not in profile_by_id)
    unknown_seed_count = sum(1 for row in rows if row["seed"] not in expected_density_by_seed)
    density_mismatches = [
        row for row in rows
        if row["seed"] not in expected_density_by_seed
        or abs(row["density"] - expected_density_by_seed[row["seed"]]) > 0.005
    ]
    bounds_mismatches = []
    for row in rows:
        expected = expected_bounds_by_profile_id.get(row["bounds_profile_id"])
        if not expected:
            bounds_mismatches.append(row)
            continue
        expected_min, expected_max = expected
        if row["bounds_min"] != expected_min or row["bounds_max"] != expected_max:
            bounds_mismatches.append(row)

    tight_id = config["BOUNDS_PROFILES"]["tight"]["id"]
    expanded_id = config["BOUNDS_PROFILES"]["expanded"]["id"]
    tight_count = len(rows_by_profile.get(tight_id, []))
    expanded_count = len(rows_by_profile.get(expanded_id, []))
    log_path, marker_found, log_errors = scan_latest_log("MCP_PCG_GROUND_COMBO_FIXTURE_BUILD_BEGIN")

    validation_pass = all([
        tight_count == source_count,
        2 <= expanded_count < tight_count,
        pass_count == len(rows),
        unknown_profile_count == 0,
        unknown_seed_count == 0,
        not density_mismatches,
        not bounds_mismatches,
        not log_errors,
    ])

    print(VERIFY_MARKER)
    print(f"fixture_graph={config['GRAPH_PATH']}")
    print(f"fixture_actor={config['ACTOR_LABEL']}")
    print(f"source_point_count={source_count}")
    print(f"point_count={len(rows)}")
    print(f"profile_counts={profile_counts}")
    print(f"profile_seeds={profile_seeds}")
    print(f"tight_count={tight_count}")
    print(f"expanded_count={expanded_count}")
    print(f"density_remap_range_min={config['DENSITY_REMAP_RANGE_MIN']}")
    print(f"density_remap_range_max={config['DENSITY_REMAP_RANGE_MAX']}")
    print(f"density_remap_out_min={config['DENSITY_REMAP_OUT_MIN']}")
    print(f"density_remap_out_max={config['DENSITY_REMAP_OUT_MAX']}")
    print(f"self_pruning_randomized={config['SELF_PRUNING_RANDOMIZED']}")
    print(f"self_pruning_radius_similarity={config['SELF_PRUNING_RADIUS_SIMILARITY']}")
    print(f"expected_density_by_seed={expected_density_by_seed}")
    print(f"expected_bounds_by_profile_id={expected_bounds_by_profile_id}")
    print(f"ground_combo_fixture_pass_count={pass_count}")
    print(f"unknown_profile_count={unknown_profile_count}")
    print(f"unknown_seed_count={unknown_seed_count}")
    print(f"density_mismatch_count={len(density_mismatches)}")
    print(f"bounds_mismatch_count={len(bounds_mismatches)}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print("rows=")
    for row in sorted(rows, key=lambda item: (item["bounds_profile_id"], item["seed"])):
        print(
            "  Profile={bounds_profile_id} Seed={seed} Density={density} "
            "Translation={translation} BoundsMin={bounds_min} BoundsMax={bounds_max} "
            "GroundComboFixturePass={ground_combo_fixture_pass}".format(**row)
        )
    print(f"ground_combo_fixture_validation_pass={validation_pass}")
    print("MCP_PCG_GROUND_COMBO_FIXTURE_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Ground combo fixture verification failed")


if __name__ == "__main__":
    main()
