import pathlib
from collections import Counter, defaultdict

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_spline_assembly_output.py",
    )
).resolve().parent

BUILDER_SCRIPT = str(SCRIPT_DIR / "build_spline_assembly_with_post_copy_offset.py")
VERIFY_MARKER = "MCP_PCG_SPLINE_ASSEMBLY_VERIFY_BEGIN"
BUILDER_CONFIG_OVERRIDE = None


def load_builder_config():
    if BUILDER_CONFIG_OVERRIDE is not None:
        return BUILDER_CONFIG_OVERRIDE
    namespace = {"__name__": "_pcg_builder_config"}
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


def get_point_rows(point_data):
    metadata = point_data.const_metadata()
    point_count = point_data.get_num_points()
    input_range = unreal.PCGPointInputRange()
    input_range.set_editor_property("point_data", point_data)
    input_range.set_editor_property("range_start_index", 0)
    input_range.set_editor_property("range_size", point_count)

    entries = list(point_data.get_metadata_entry_values_from_range(input_range))
    point_densities = list(point_data.get_density_values_from_range(input_range))
    helpers = unreal.PCGMetadataAccessorHelpers
    rows = []
    for idx, entry in enumerate(entries):
        entry = int(entry)
        rows.append({
            "actor": int(helpers.get_integer64_attribute_by_metadata_key(entry, metadata, "ActorIndex")),
            "parent": int(helpers.get_integer64_attribute_by_metadata_key(entry, metadata, "ParentIndex")),
            "depth": int(helpers.get_integer32_attribute_by_metadata_key(entry, metadata, "HierarchyDepth")),
            "branch_density": round(float(helpers.get_double_attribute_by_metadata_key(entry, metadata, "BranchDensity")), 3),
            "side_mask": round(float(helpers.get_double_attribute_by_metadata_key(entry, metadata, "SideMask")), 3),
            "side_mask_filter_pass": bool(helpers.get_bool_attribute_by_metadata_key(entry, metadata, "SideMaskFilterPass")),
            "branch_density_noised": round(float(helpers.get_double_attribute_by_metadata_key(entry, metadata, "BranchDensityNoised")), 3),
            "branch_density_filter_pass": bool(helpers.get_bool_attribute_by_metadata_key(entry, metadata, "BranchDensityFilterPass")),
            "ground_style_smoke_pass": bool(helpers.get_bool_attribute_by_metadata_key(entry, metadata, "GroundStyleSmokePass")),
            "point_density": round(float(point_densities[idx]), 3),
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


def find_root_key(row, by_actor):
    seen = set()
    current = row
    while current["parent"] >= 0:
        if current["actor"] in seen:
            return None
        seen.add(current["actor"])
        current = by_actor.get(current["parent"])
        if current is None:
            return None
    return current["actor"]


def scaled_counts(source_counter, target_count):
    return {key: value * target_count for key, value in sorted(source_counter.items())}


def find_parent_gaps(source_specs):
    survivor_actors = {spec["actor"] for spec in source_specs}
    return [
        spec for spec in source_specs
        if spec["parent"] >= 0 and spec["parent"] not in survivor_actors
    ]


def classify_side_filter(source_assembly, side_filter_allows):
    survivors = []
    pruned = []
    for spec in source_assembly:
        if side_filter_allows(spec):
            survivors.append(spec)
        else:
            pruned.append(spec)
    return survivors, pruned, find_parent_gaps(survivors)


def side_mask_passes_profile(side_mask, profile_spec):
    operator_name = str(profile_spec["operator"])
    threshold = float(profile_spec["threshold"])
    if operator_name == "GREATER_OR_EQUAL":
        return side_mask >= threshold
    if operator_name == "LESSER_OR_EQUAL":
        return side_mask <= threshold
    if operator_name == "EQUAL":
        return abs(side_mask - threshold) <= 0.001
    raise RuntimeError(f"Unsupported SideMask verifier operator: {operator_name!r}")


def classify_pruning(source_assembly, noise_min, noise_max, filter_threshold, density_value=None):
    survivors = []
    pruned = []
    ambiguous = []
    density_value = density_value or (lambda spec: float(spec.get("density", 1.0)))
    for spec in source_assembly:
        density = float(density_value(spec))
        min_noised = density * noise_min
        max_noised = density * noise_max
        if min_noised >= filter_threshold:
            survivors.append(spec)
        elif max_noised < filter_threshold:
            pruned.append(spec)
        else:
            ambiguous.append(spec)

    return survivors, pruned, ambiguous, find_parent_gaps(survivors)


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
    source_assembly = config["get_source_assembly"]()
    target_count = int(config["TARGET_SAMPLE_COUNT"])
    expected_source_count = len(source_assembly)
    side_filter_spec = config["side_filter_profile_spec"]()
    active_side_profile = config.get(
        "active_side_mask_filter_profile",
        lambda: config.get("SIDE_MASK_FILTER_PROFILE", "none"),
    )()
    active_density_profile = config.get(
        "active_branch_density_pruning_profile",
        lambda: config.get("BRANCH_DENSITY_PRUNING_PROFILE", "none"),
    )()
    side_filter_operator = str(side_filter_spec["operator"])
    side_filter_threshold = float(side_filter_spec["threshold"])
    side_filter_allowed_sides = list(side_filter_spec["allowed_sides"])
    noise_min = float(config.get("branch_density_noise_min", lambda: config["BRANCH_DENSITY_NOISE_MIN"])())
    noise_max = float(config.get("branch_density_noise_max", lambda: config["BRANCH_DENSITY_NOISE_MAX"])())
    filter_threshold = float(config.get("branch_density_filter_threshold", lambda: config["BRANCH_DENSITY_FILTER_THRESHOLD"])())
    density_value = config.get("branch_density_value", lambda spec: float(spec.get("density", 1.0)))
    side_survivors, side_pruned, side_parent_gaps = classify_side_filter(
        source_assembly,
        config["graph_side_filter_allows"],
    )
    survivors, density_pruned, ambiguous, survivor_parent_gaps = classify_pruning(
        side_survivors,
        noise_min,
        noise_max,
        filter_threshold,
        density_value,
    )
    expected_survivor_count = len(survivors)
    expected_side_survivor_count = len(side_survivors)
    expected_side_pruned_source_count = len(side_pruned)
    expected_side_pruned_point_count = expected_side_pruned_source_count * target_count
    expected_density_pruned_source_count = len(density_pruned)
    expected_density_pruned_point_count = expected_density_pruned_source_count * target_count
    expected_pruned_source_count = expected_side_pruned_source_count + expected_density_pruned_source_count
    expected_pruned_point_count = expected_pruned_source_count * target_count
    expected_point_count = expected_survivor_count * target_count
    expected_root_count = sum(1 for spec in survivors if spec["parent"] < 0) * target_count
    expected_non_root_count = expected_point_count - expected_root_count
    expected_depth_counts = scaled_counts(Counter(spec["depth"] for spec in survivors), target_count)
    expected_density_counts = scaled_counts(
        Counter(round(float(density_value(spec)), 3) for spec in survivors),
        target_count,
    )
    expected_side_mask_counts = scaled_counts(
        Counter(round(float(config["side_mask_value"](spec["side"])), 3) for spec in survivors),
        target_count,
    )

    try:
        actor = get_actor(config["ACTOR_LABEL"])
    except RuntimeError:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(config["LEVEL"])
        actor = get_actor(config["ACTOR_LABEL"])
    component = actor.get_components_by_class(unreal.PCGComponent)[0]
    point_data = get_generated_point_data(component)
    rows = get_point_rows(point_data)

    by_actor = {row["actor"]: row for row in rows}
    roots = [row for row in rows if row["parent"] < 0]
    non_roots = [row for row in rows if row["parent"] >= 0]
    depth_counts = dict(sorted(Counter(row["depth"] for row in rows).items()))
    branch_density_counts = dict(sorted(Counter(row["branch_density"] for row in rows).items()))
    side_mask_counts = dict(sorted(Counter(row["side_mask"] for row in rows).items()))
    point_density_counts = dict(sorted(Counter(row["point_density"] for row in rows).items()))
    side_filter_pass_count = sum(1 for row in rows if row["side_mask_filter_pass"])
    filter_pass_count = sum(1 for row in rows if row["branch_density_filter_pass"])
    ground_style_smoke_pass_count = sum(1 for row in rows if row["ground_style_smoke_pass"])
    side_profile_failures = [
        row for row in rows
        if not side_mask_passes_profile(row["side_mask"], side_filter_spec)
    ]
    noised_threshold_failures = [
        row for row in rows
        if row["branch_density_noised"] < round(filter_threshold, 3)
    ]
    noised_ratio_failures = []
    for row in rows:
        if row["branch_density"] == 0:
            continue
        ratio = row["branch_density_noised"] / row["branch_density"]
        if ratio < noise_min - 0.01 or ratio > noise_max + 0.01:
            noised_ratio_failures.append(row)
    missing_parents = [row for row in non_roots if row["parent"] not in by_actor]
    parent_depth_mismatches = [
        row for row in non_roots
        if row["parent"] in by_actor and by_actor[row["parent"]]["depth"] != row["depth"] - 1
    ]

    groups = defaultdict(list)
    for row in rows:
        groups[find_root_key(row, by_actor)].append(row)
    group_sizes = sorted(len(value) for key, value in groups.items() if key is not None)
    null_group_count = len(groups.get(None, []))

    ism_rows = get_ism_rows(actor)
    ism_total = sum(count for _, _, count in ism_rows if count > 0)
    log_path, marker_found, log_errors = scan_latest_log("MCP_PCG_MAIN_LEARNING_SOURCE_BUILD_BEGIN")

    validation_pass = all([
        len(rows) == expected_point_count,
        expected_density_pruned_point_count > 0,
        expected_pruned_point_count > 0,
        not side_parent_gaps,
        not ambiguous,
        not survivor_parent_gaps,
        len(roots) == expected_root_count,
        len(non_roots) == expected_non_root_count,
        len(set(row["actor"] for row in rows)) == len(rows),
        not missing_parents,
        not parent_depth_mismatches,
        depth_counts == expected_depth_counts,
        group_sizes == [expected_survivor_count] * expected_root_count,
        null_group_count == 0,
        branch_density_counts == expected_density_counts,
        side_mask_counts == expected_side_mask_counts,
        point_density_counts == expected_density_counts,
        side_filter_pass_count == len(rows),
        filter_pass_count == len(rows),
        ground_style_smoke_pass_count == len(rows),
        not side_profile_failures,
        not noised_threshold_failures,
        not noised_ratio_failures,
        ism_total == expected_point_count,
        not log_errors,
    ])

    print(VERIFY_MARKER)
    print(f"source_assembly_preset={config['SOURCE_ASSEMBLY_PRESET']}")
    print(f"side_mode={config['SIDE_MODE']}")
    print(f"source_point_count={expected_source_count}")
    print(f"side_mask_filter_profile={active_side_profile}")
    print(f"side_mask_filter_operator={side_filter_operator}")
    print(f"side_mask_filter_threshold={side_filter_threshold}")
    print(f"side_mask_filter_allowed_sides={side_filter_allowed_sides}")
    print(f"branch_density_pruning_profile={active_density_profile}")
    print(f"target_sample_count={target_count}")
    print(f"expected_side_survivor_source_count={expected_side_survivor_count}")
    print(f"expected_side_pruned_source_count={expected_side_pruned_source_count}")
    print(f"expected_side_pruned_point_count={expected_side_pruned_point_count}")
    print(f"expected_density_pruned_source_count={expected_density_pruned_source_count}")
    print(f"expected_density_pruned_point_count={expected_density_pruned_point_count}")
    print(f"expected_survivor_source_count={expected_survivor_count}")
    print(f"expected_pruned_source_count={expected_pruned_source_count}")
    print(f"expected_pruned_point_count={expected_pruned_point_count}")
    print(f"expected_point_count={expected_point_count}")
    print(f"point_count={len(rows)}")
    print(f"root_count={len(roots)}")
    print(f"non_root_count={len(non_roots)}")
    print(f"depth_counts={depth_counts}")
    print(f"expected_depth_counts={expected_depth_counts}")
    print(f"unique_actor_index={len(set(row['actor'] for row in rows)) == len(rows)}")
    print(f"missing_parent_count={len(missing_parents)}")
    print(f"parent_depth_mismatch_count={len(parent_depth_mismatches)}")
    print(f"group_sizes={group_sizes}")
    print(f"null_group_count={null_group_count}")
    print(f"branch_density_counts={branch_density_counts}")
    print(f"side_mask_counts={side_mask_counts}")
    print(f"expected_side_mask_counts={expected_side_mask_counts}")
    print(f"point_density_counts={point_density_counts}")
    print(f"expected_density_counts={expected_density_counts}")
    print(f"branch_density_noise_min={noise_min}")
    print(f"branch_density_noise_max={noise_max}")
    print(f"branch_density_filter_threshold={filter_threshold}")
    print(f"ground_style_density_filter_enabled={config.get('GROUND_STYLE_DENSITY_FILTER_ENABLED', False)}")
    print(f"ground_style_density_filter_lower={config.get('GROUND_STYLE_DENSITY_FILTER_LOWER', None)}")
    print(f"ground_style_density_filter_upper={config.get('GROUND_STYLE_DENSITY_FILTER_UPPER', None)}")
    print(f"ground_style_self_pruning_enabled={config.get('GROUND_STYLE_SELF_PRUNING_ENABLED', False)}")
    print(f"ground_style_self_pruning_randomized={config.get('GROUND_STYLE_SELF_PRUNING_RANDOMIZED', None)}")
    print(f"ground_style_self_pruning_radius_similarity={config.get('GROUND_STYLE_SELF_PRUNING_RADIUS_SIMILARITY', None)}")
    print(f"survivor_source_names={[spec['name'] for spec in survivors]}")
    print(f"side_pruned_source_names={[spec['name'] for spec in side_pruned]}")
    print(f"density_pruned_source_names={[spec['name'] for spec in density_pruned]}")
    print(f"pruned_source_names={[spec['name'] for spec in side_pruned + density_pruned]}")
    print(f"side_parent_gap_count={len(side_parent_gaps)}")
    print(f"ambiguous_pruning_source_names={[spec['name'] for spec in ambiguous]}")
    print(f"survivor_parent_gap_count={len(survivor_parent_gaps)}")
    print(f"side_mask_filter_pass_count={side_filter_pass_count}")
    print(f"side_profile_failure_count={len(side_profile_failures)}")
    print(f"branch_density_filter_pass_count={filter_pass_count}")
    print(f"ground_style_smoke_pass_count={ground_style_smoke_pass_count}")
    print(f"noised_threshold_failure_count={len(noised_threshold_failures)}")
    print(f"noised_ratio_failure_count={len(noised_ratio_failures)}")
    print(f"ism_total={ism_total}")
    for name, mesh, count in ism_rows:
        print(f"ism={name}|{count}|{mesh}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print("rows_sample=")
    for row in sorted(rows, key=lambda item: (item["actor"], item["depth"]))[:24]:
        print(
            "  ActorIndex={actor} ParentIndex={parent} HierarchyDepth={depth} "
            "SideMask={side_mask} SideMaskFilterPass={side_mask_filter_pass} "
            "BranchDensity={branch_density} BranchDensityNoised={branch_density_noised} "
            "BranchDensityFilterPass={branch_density_filter_pass} "
            "GroundStyleSmokePass={ground_style_smoke_pass} PointDensity={point_density}".format(**row)
        )
    print(f"spline_assembly_validation_pass={validation_pass}")
    print("MCP_PCG_SPLINE_ASSEMBLY_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Spline assembly verification failed")


if __name__ == "__main__":
    main()
