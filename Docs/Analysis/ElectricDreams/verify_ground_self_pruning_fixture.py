import pathlib

import unreal


BUILDER_SCRIPT = r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\build_ground_self_pruning_fixture.py"
VERIFY_MARKER = "MCP_PCG_SELF_PRUNING_FIXTURE_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_pcg_self_pruning_fixture_config"}
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
        transform = transforms[idx]
        rows.append({
            "metadata_entry": int(entry),
            "seed": int(seeds[idx]),
            "density": round(float(densities[idx]), 3),
            "translation": vector_tuple(transform.get_editor_property("translation")),
            "bounds_min": vector_tuple(bounds_min[idx]),
            "bounds_max": vector_tuple(bounds_max[idx]),
            "self_pruning_fixture_pass": bool(
                helpers.get_bool_attribute_by_metadata_key(
                    int(entry),
                    metadata,
                    "SelfPruningFixturePass",
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
    source_seeds = {int(spec["seed"]) for spec in source_points}

    try:
        actor = get_actor(config["ACTOR_LABEL"])
    except RuntimeError:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(config["LEVEL"])
        actor = get_actor(config["ACTOR_LABEL"])

    component = actor.get_components_by_class(unreal.PCGComponent)[0]
    point_data = get_generated_point_data(component)
    rows = get_point_rows(point_data)

    point_count = len(rows)
    pruned_count = source_count - point_count
    survived_seeds = sorted(row["seed"] for row in rows)
    unknown_seed_count = sum(1 for seed in survived_seeds if seed not in source_seeds)
    marker_count = sum(1 for row in rows if row["self_pruning_fixture_pass"])
    unique_positions = sorted({row["translation"] for row in rows})
    log_path, marker_found, log_errors = scan_latest_log("MCP_PCG_SELF_PRUNING_FIXTURE_BUILD_BEGIN")

    validation_pass = all([
        point_count >= 2,
        point_count < source_count,
        pruned_count > 0,
        marker_count == point_count,
        unknown_seed_count == 0,
        len(unique_positions) >= 2,
        not log_errors,
    ])

    print(VERIFY_MARKER)
    print(f"fixture_graph={config['GRAPH_PATH']}")
    print(f"fixture_actor={config['ACTOR_LABEL']}")
    print(f"source_point_count={source_count}")
    print(f"point_count={point_count}")
    print(f"pruned_count={pruned_count}")
    print(f"density_filter_lower={config['DENSITY_FILTER_LOWER']}")
    print(f"density_filter_upper={config['DENSITY_FILTER_UPPER']}")
    print(f"self_pruning_randomized={config['SELF_PRUNING_RANDOMIZED']}")
    print(f"self_pruning_radius_similarity={config['SELF_PRUNING_RADIUS_SIMILARITY']}")
    print(f"source_seeds={sorted(source_seeds)}")
    print(f"survived_seeds={survived_seeds}")
    print(f"unknown_seed_count={unknown_seed_count}")
    print(f"self_pruning_fixture_pass_count={marker_count}")
    print(f"unique_position_count={len(unique_positions)}")
    print(f"unique_positions={unique_positions}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print("rows=")
    for row in sorted(rows, key=lambda item: item["seed"]):
        print(
            "  Seed={seed} Density={density} Translation={translation} "
            "BoundsMin={bounds_min} BoundsMax={bounds_max} "
            "SelfPruningFixturePass={self_pruning_fixture_pass}".format(**row)
        )
    print(f"self_pruning_fixture_validation_pass={validation_pass}")
    print("MCP_PCG_SELF_PRUNING_FIXTURE_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Self-pruning fixture verification failed")


if __name__ == "__main__":
    main()
