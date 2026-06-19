import pathlib
from collections import defaultdict

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ground_controls_prototype.py",
    )
).resolve().parent

BUILDER_SCRIPT = str(SCRIPT_DIR / "build_cubeless_ground_controls_prototype.py")
VERIFY_MARKER = "MCP_CUBELESS_GROUND_CONTROLS_PROTOTYPE_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_cubeless_ground_controls_prototype_config"}
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
            "branch_density": round(float(
                helpers.get_double_attribute_by_metadata_key(entry, metadata, "BranchDensity")
            ), 3),
            "side_mask": round(float(
                helpers.get_double_attribute_by_metadata_key(entry, metadata, "SideMask")
            ), 3),
            "ditch_density_threshold": round(float(
                helpers.get_double_attribute_by_metadata_key(entry, metadata, "DitchDensityThreshold")
            ), 3),
            "bounds_profile_id": int(
                helpers.get_integer32_attribute_by_metadata_key(
                    entry,
                    metadata,
                    "BoundsProfileId",
                )
            ),
            "ditch_style_candidate_pass": bool(
                helpers.get_bool_attribute_by_metadata_key(
                    entry,
                    metadata,
                    "DitchStyleCandidatePass",
                )
            ),
            "cubeless_ground_controls_pass": bool(
                helpers.get_bool_attribute_by_metadata_key(
                    entry,
                    metadata,
                    "CubelessGroundControlsPass",
                )
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


def get_bounds_modifier_settings(graph, profiles):
    rows = {}
    for node in graph.get_editor_property("nodes"):
        settings = node.get_settings()
        if not settings or settings.get_class().get_name() != "PCGBoundsModifierSettings":
            continue
        title = str(node.get_editor_property("node_title")).lower()
        for profile_name in profiles:
            if profile_name.lower() in title:
                rows[profile_name] = {
                    "bounds_min": vector_tuple(settings.get_editor_property("bounds_min")),
                    "bounds_max": vector_tuple(settings.get_editor_property("bounds_max")),
                    "mode": str(settings.get_editor_property("mode")),
                }
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
    graph = unreal.EditorAssetLibrary.load_asset(config["GRAPH_PATH"])
    if not graph:
        raise RuntimeError(f"Missing graph: {config['GRAPH_PATH']}")
    try:
        actor = get_actor(config["ACTOR_LABEL"])
    except RuntimeError:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(config["LEVEL"])
        actor = get_actor(config["ACTOR_LABEL"])

    component = actor.get_components_by_class(unreal.PCGComponent)[0]
    point_data = get_generated_point_data(component)
    rows = get_point_rows(point_data)
    ism_rows = get_ism_rows(actor)

    source_by_seed = {int(spec["seed"]): spec for spec in config["SOURCE_POINTS"]}
    expected_seed_set = set(config["expected_ditch_survivor_seeds"]())
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
    expected_bounds_by_profile_name = {
        name: (
            tuple(round(float(value), 3) for value in spec["bounds_min"]),
            tuple(round(float(value), 3) for value in spec["bounds_max"]),
        )
        for name, spec in config["BOUNDS_PROFILES"].items()
    }
    expected_side_mask_by_profile_id = {
        int(spec["id"]): round(float(spec["side_mask"]), 3)
        for spec in config["BOUNDS_PROFILES"].values()
    }
    expected_branch_density_by_profile_id = {
        int(spec["id"]): round(float(spec["branch_density"]), 3)
        for spec in config["BOUNDS_PROFILES"].values()
    }

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

    expected_density_by_seed = {
        int(spec["seed"]): round(float(config["expected_density"](spec["density"])), 3)
        for spec in config["SOURCE_POINTS"]
    }
    pass_count = sum(1 for row in rows if row["cubeless_ground_controls_pass"])
    ditch_pass_count = sum(1 for row in rows if row["ditch_style_candidate_pass"])
    unknown_profile_count = sum(1 for row in rows if row["bounds_profile_id"] not in profile_by_id)
    unexpected_seed_count = sum(1 for row in rows if row["seed"] not in expected_seed_set)
    below_threshold_count = sum(
        1
        for row in rows
        if row["branch_density"] < float(config["DITCH_BRANCH_DENSITY_THRESHOLD"]) - 0.005
    )
    density_mismatches = [
        row for row in rows
        if row["seed"] not in expected_density_by_seed
        or abs(row["density"] - expected_density_by_seed[row["seed"]]) > 0.005
    ]
    branch_density_mismatches = [
        row for row in rows
        if abs(row["branch_density"] - expected_branch_density_by_profile_id.get(row["bounds_profile_id"], -999.0)) > 0.005
    ]
    threshold_mismatches = [
        row for row in rows
        if abs(row["ditch_density_threshold"] - float(config["DITCH_BRANCH_DENSITY_THRESHOLD"])) > 0.005
    ]
    side_mask_mismatches = [
        row for row in rows
        if abs(row["side_mask"] - expected_side_mask_by_profile_id.get(row["bounds_profile_id"], -999.0)) > 0.005
    ]
    bounds_settings = get_bounds_modifier_settings(graph, config["BOUNDS_PROFILES"])
    bounds_settings_mismatches = []
    for profile_name, expected in expected_bounds_by_profile_name.items():
        actual = bounds_settings.get(profile_name)
        if not actual:
            bounds_settings_mismatches.append({"profile": profile_name, "reason": "missing"})
            continue
        expected_min, expected_max = expected
        if actual["bounds_min"] != expected_min or actual["bounds_max"] != expected_max:
            bounds_settings_mismatches.append({
                "profile": profile_name,
                "expected": expected,
                "actual": actual,
            })

    small_id = config["BOUNDS_PROFILES"]["ed_small_set"]["id"]
    medium_id = config["BOUNDS_PROFILES"]["ed_medium_set"]["id"]
    small_count = len(rows_by_profile.get(small_id, []))
    medium_count = len(rows_by_profile.get(medium_id, []))
    expected_survivor_count = len(expected_seed_set)
    total_ism_instances = sum(max(0, count) for _, _, count in ism_rows)
    log_path, marker_found, log_errors = scan_latest_log("MCP_CUBELESS_GROUND_CONTROLS_PROTOTYPE_BUILD_BEGIN")

    validation_pass = all([
        small_count == expected_survivor_count,
        1 <= medium_count < small_count,
        pass_count == len(rows),
        ditch_pass_count == len(rows),
        total_ism_instances == len(rows),
        unknown_profile_count == 0,
        unexpected_seed_count == 0,
        below_threshold_count == 0,
        not density_mismatches,
        not branch_density_mismatches,
        not threshold_mismatches,
        not side_mask_mismatches,
        not bounds_settings_mismatches,
        not log_errors,
    ])

    print(VERIFY_MARKER)
    print(f"production_graph={config['GRAPH_PATH']}")
    print(f"validation_actor={config['ACTOR_LABEL']}")
    print(f"grass_mesh={config['GRASS_MESH_PATH']}")
    print(f"source_point_count={len(config['SOURCE_POINTS'])}")
    print(f"expected_ditch_survivor_seeds={sorted(expected_seed_set)}")
    print(f"point_count={len(rows)}")
    print(f"profile_counts={profile_counts}")
    print(f"profile_seeds={profile_seeds}")
    print(f"small_count={small_count}")
    print(f"medium_count={medium_count}")
    print(f"ditch_branch_density_threshold={config['DITCH_BRANCH_DENSITY_THRESHOLD']}")
    print(f"density_remap_range_min={config['DENSITY_REMAP_RANGE_MIN']}")
    print(f"density_remap_range_max={config['DENSITY_REMAP_RANGE_MAX']}")
    print(f"density_remap_out_min={config['DENSITY_REMAP_OUT_MIN']}")
    print(f"density_remap_out_max={config['DENSITY_REMAP_OUT_MAX']}")
    print(f"ground_density_filter_lower={config['GROUND_DENSITY_FILTER_LOWER']}")
    print(f"ground_density_filter_upper={config['GROUND_DENSITY_FILTER_UPPER']}")
    print(f"self_pruning_randomized={config['SELF_PRUNING_RANDOMIZED']}")
    print(f"self_pruning_radius_similarity={config['SELF_PRUNING_RADIUS_SIMILARITY']}")
    print(f"expected_density_by_seed={expected_density_by_seed}")
    print(f"expected_branch_density_by_profile_id={expected_branch_density_by_profile_id}")
    print(f"expected_bounds_by_profile_id={expected_bounds_by_profile_id}")
    print(f"bounds_modifier_settings={bounds_settings}")
    print(f"cubeless_ground_controls_pass_count={pass_count}")
    print(f"ditch_style_candidate_pass_count={ditch_pass_count}")
    print(f"total_ism_instances={total_ism_instances}")
    print(f"ism_rows={ism_rows}")
    print(f"unknown_profile_count={unknown_profile_count}")
    print(f"unexpected_seed_count={unexpected_seed_count}")
    print(f"below_threshold_count={below_threshold_count}")
    print(f"density_mismatch_count={len(density_mismatches)}")
    print(f"branch_density_mismatch_count={len(branch_density_mismatches)}")
    print(f"threshold_mismatch_count={len(threshold_mismatches)}")
    print(f"side_mask_mismatch_count={len(side_mask_mismatches)}")
    print("output_bounds_stage=post_static_mesh_spawner_mesh_bounds")
    print(f"bounds_settings_mismatch_count={len(bounds_settings_mismatches)}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print("rows=")
    for row in sorted(rows, key=lambda item: (item["bounds_profile_id"], item["seed"])):
        print(
            "  Profile={bounds_profile_id} Seed={seed} Density={density} BranchDensity={branch_density} "
            "SideMask={side_mask} Threshold={ditch_density_threshold} Translation={translation} "
            "BoundsMin={bounds_min} BoundsMax={bounds_max} DitchPass={ditch_style_candidate_pass} "
            "GroundPass={cubeless_ground_controls_pass}".format(**row)
        )
    print(f"cubeless_ground_controls_prototype_validation_pass={validation_pass}")
    print("MCP_CUBELESS_GROUND_CONTROLS_PROTOTYPE_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ground controls prototype verification failed")


if __name__ == "__main__":
    main()
