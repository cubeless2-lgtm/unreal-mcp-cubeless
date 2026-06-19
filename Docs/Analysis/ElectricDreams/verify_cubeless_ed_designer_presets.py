import pathlib
from collections import defaultdict

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_designer_presets.py",
    )
).resolve().parent

BUILDER_SCRIPT = str(SCRIPT_DIR / "build_cubeless_ed_designer_presets.py")
VERIFY_MARKER = "MCP_CUBELESS_ED_DESIGNER_PRESETS_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_cubeless_ed_designer_presets_config"}
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
    return int(helpers.get_integer32_attribute_by_metadata_key(entry, metadata, name))


def get_bool_attr(helpers, entry, metadata, name):
    return bool(helpers.get_bool_attribute_by_metadata_key(entry, metadata, name))


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
    helpers = unreal.PCGMetadataAccessorHelpers
    rows = []
    for idx, entry in enumerate(entries):
        entry = int(entry)
        rows.append({
            "metadata_entry": entry,
            "seed": int(seeds[idx]),
            "density": round(float(densities[idx]), 3),
            "designer_profile_id": get_int_attr(helpers, entry, metadata, "DesignerProfileId"),
            "designer_profile_type": get_int_attr(helpers, entry, metadata, "DesignerProfileType"),
            "designer_control_layer_pass": get_bool_attr(helpers, entry, metadata, "DesignerControlLayerPass"),
            "designer_preset_id": get_int_attr(helpers, entry, metadata, "DesignerPresetId"),
            "designer_preset_type": get_int_attr(helpers, entry, metadata, "DesignerPresetType"),
            "designer_preset_pass": get_bool_attr(helpers, entry, metadata, "DesignerPresetPass"),
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


def validate_preset(spec, config):
    label = f"{config['ACTOR_LABEL_PREFIX']}_{spec['name']}_Validation"
    actor = get_actor(label)
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    spline_components = actor.get_components_by_class(unreal.SplineComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {label}")
    if not spline_components:
        raise RuntimeError(f"Validation actor has no SplineComponent: {label}")

    point_data = get_generated_point_data(pcg_components[0])
    rows = get_point_rows(point_data)
    ism_rows = get_ism_rows(actor)

    profile_name_by_id = {
        int(profile_spec["id"]): profile_spec["name"]
        for profile_spec in config["PROFILE_SPECS"].values()
    }
    profile_type_by_id = {
        int(profile_spec["id"]): int(profile_spec["type"])
        for profile_spec in config["PROFILE_SPECS"].values()
    }
    rows_by_profile = defaultdict(list)
    for row in rows:
        rows_by_profile[row["designer_profile_id"]].append(row)

    profile_counts = {
        profile_name_by_id.get(profile_id, f"unknown_{profile_id}"): len(profile_rows)
        for profile_id, profile_rows in sorted(rows_by_profile.items())
    }
    profile_types = {
        profile_name_by_id.get(profile_id, f"unknown_{profile_id}"): sorted(
            set(row["designer_profile_type"] for row in profile_rows)
        )
        for profile_id, profile_rows in sorted(rows_by_profile.items())
    }
    type_mismatch_count = sum(
        1 for row in rows
        if row["designer_profile_id"] not in profile_type_by_id
        or row["designer_profile_type"] != profile_type_by_id[row["designer_profile_id"]]
    )
    preset_id_mismatch_count = sum(1 for row in rows if row["designer_preset_id"] != spec["id"])
    preset_type_mismatch_count = sum(1 for row in rows if row["designer_preset_type"] != spec["type"])
    preset_pass_count = sum(1 for row in rows if row["designer_preset_pass"])
    control_pass_count = sum(1 for row in rows if row["designer_control_layer_pass"])
    total_ism_instances = sum(max(0, count) for _, _, count in ism_rows)
    validation_pass = all([
        len(rows) == spec["expected_points"],
        profile_counts == spec["expected_profile_counts"],
        type_mismatch_count == 0,
        preset_id_mismatch_count == 0,
        preset_type_mismatch_count == 0,
        preset_pass_count == len(rows),
        control_pass_count == len(rows),
        total_ism_instances == spec["expected_points"],
    ])
    return {
        "preset": spec["name"],
        "actor": label,
        "point_count": len(rows),
        "expected_points": spec["expected_points"],
        "profile_counts": profile_counts,
        "profile_types": profile_types,
        "preset_id": spec["id"],
        "preset_type": spec["type"],
        "preset_id_mismatch_count": preset_id_mismatch_count,
        "preset_type_mismatch_count": preset_type_mismatch_count,
        "preset_pass_count": preset_pass_count,
        "control_pass_count": control_pass_count,
        "total_ism_instances": total_ism_instances,
        "ism_rows": ism_rows,
        "validation_pass": validation_pass,
        "rows_sample": sorted(rows, key=lambda item: (item["designer_profile_id"], item["seed"]))[:12],
    }


def main():
    config = load_builder_config()
    for graph_path in config["PRESET_GRAPH_PATHS"].values():
        graph = unreal.EditorAssetLibrary.load_asset(graph_path)
        if not graph:
            raise RuntimeError(f"Missing preset graph: {graph_path}")

    results = [validate_preset(spec, config) for spec in config["PRESET_SPECS"]]
    log_path, marker_found, log_errors = scan_latest_log("MCP_CUBELESS_ED_DESIGNER_PRESETS_BUILD_BEGIN")
    validation_pass = all(result["validation_pass"] for result in results) and not log_errors

    print(VERIFY_MARKER)
    print(f"preset_graph_paths={config['PRESET_GRAPH_PATHS']}")
    print(f"balanced_preset_graph={config['BALANCED_PRESET_GRAPH_PATH']}")
    for result in results:
        print(f"preset={result['preset']}")
        print(f"  actor={result['actor']}")
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  profile_counts={result['profile_counts']}")
        print(f"  profile_types={result['profile_types']}")
        print(f"  preset_id={result['preset_id']}")
        print(f"  preset_type={result['preset_type']}")
        print(f"  preset_id_mismatch_count={result['preset_id_mismatch_count']}")
        print(f"  preset_type_mismatch_count={result['preset_type_mismatch_count']}")
        print(f"  preset_pass_count={result['preset_pass_count']}")
        print(f"  control_pass_count={result['control_pass_count']}")
        print(f"  total_ism_instances={result['total_ism_instances']}")
        print(f"  ism_rows={result['ism_rows']}")
        print(f"  validation_pass={result['validation_pass']}")
        print("  rows_sample=")
        for row in result["rows_sample"]:
            print(
                "    Preset={designer_preset_id}/{designer_preset_type} "
                "Profile={designer_profile_id}/{designer_profile_type} "
                "Seed={seed} Density={density} "
                "PresetPass={designer_preset_pass} ControlPass={designer_control_layer_pass}".format(**row)
            )
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"designer_presets_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_DESIGNER_PRESETS_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED designer presets verification failed")


if __name__ == "__main__":
    main()
