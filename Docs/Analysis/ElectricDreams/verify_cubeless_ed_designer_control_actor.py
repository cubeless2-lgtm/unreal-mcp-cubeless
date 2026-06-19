import pathlib
from collections import defaultdict

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_designer_control_actor.py",
    )
).resolve().parent

BUILDER_SCRIPT = str(SCRIPT_DIR / "build_cubeless_ed_designer_control_actor.py")
VERIFY_MARKER = "MCP_CUBELESS_ED_DESIGNER_CONTROL_ACTOR_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_cubeless_ed_designer_control_actor_config"}
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


def get_subobject_templates(blueprint):
    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    library = unreal.SubobjectDataBlueprintFunctionLibrary
    if not subsystem:
        raise RuntimeError("SubobjectDataSubsystem is unavailable")

    rows = []
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        data = subsystem.k2_find_subobject_data_from_handle(handle)
        obj = library.get_object_for_blueprint(data, blueprint)
        if not obj:
            continue
        graph_path = None
        if isinstance(obj, unreal.PCGComponent):
            graph_instance = obj.get_editor_property("graph_instance")
            graph = graph_instance.get_editor_property("graph") if graph_instance else None
            graph_path = graph.get_path_name() if graph else None
        rows.append({
            "name": obj.get_name(),
            "class": obj.get_class().get_name(),
            "is_component": bool(library.is_component(data)),
            "is_root": bool(library.is_root_component(data)),
            "is_scene": bool(library.is_scene_component(data)),
            "graph_path": graph_path,
        })
    return rows


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
    helpers = unreal.PCGMetadataAccessorHelpers
    rows = []
    for idx, entry in enumerate(entries):
        entry = int(entry)
        rows.append({
            "metadata_entry": entry,
            "seed": int(seeds[idx]),
            "density": round(float(densities[idx]), 3),
            "designer_profile_id": int(
                helpers.get_integer32_attribute_by_metadata_key(
                    entry,
                    metadata,
                    "DesignerProfileId",
                )
            ),
            "designer_profile_type": int(
                helpers.get_integer32_attribute_by_metadata_key(
                    entry,
                    metadata,
                    "DesignerProfileType",
                )
            ),
            "designer_control_layer_pass": bool(
                helpers.get_bool_attribute_by_metadata_key(
                    entry,
                    metadata,
                    "DesignerControlLayerPass",
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
    blueprint = unreal.EditorAssetLibrary.load_asset(config["BLUEPRINT_PATH"])
    if not blueprint:
        raise RuntimeError(f"Missing production blueprint: {config['BLUEPRINT_PATH']}")

    try:
        actor = get_actor(config["ACTOR_LABEL"])
    except RuntimeError:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(config["LEVEL"])
        actor = get_actor(config["ACTOR_LABEL"])
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    spline_components = actor.get_components_by_class(unreal.SplineComponent)
    if not pcg_components:
        raise RuntimeError("Validation actor has no PCGComponent")
    if not spline_components:
        raise RuntimeError("Validation actor has no SplineComponent")

    component = pcg_components[0]
    point_data = get_generated_point_data(component)
    rows = get_point_rows(point_data)
    ism_rows = get_ism_rows(actor)
    templates = get_subobject_templates(blueprint)

    expected_counts = {
        "GroundControls": 8,
        "DitchHierarchy": 42,
    }
    expected_by_id = {
        10: {"name": "GroundControls", "type": 1, "expected_points": 8},
        20: {"name": "DitchHierarchy", "type": 2, "expected_points": 42},
    }
    rows_by_profile = defaultdict(list)
    for row in rows:
        rows_by_profile[row["designer_profile_id"]].append(row)

    profile_counts = {
        expected_by_id.get(profile_id, {"name": f"unknown_{profile_id}"})["name"]: len(profile_rows)
        for profile_id, profile_rows in sorted(rows_by_profile.items())
    }
    profile_types = {
        expected_by_id.get(profile_id, {"name": f"unknown_{profile_id}"})["name"]: sorted(
            set(row["designer_profile_type"] for row in profile_rows)
        )
        for profile_id, profile_rows in sorted(rows_by_profile.items())
    }
    pass_count = sum(1 for row in rows if row["designer_control_layer_pass"])
    unknown_profile_count = sum(1 for row in rows if row["designer_profile_id"] not in expected_by_id)
    type_mismatch_count = sum(
        1 for row in rows
        if row["designer_profile_id"] not in expected_by_id
        or row["designer_profile_type"] != expected_by_id[row["designer_profile_id"]]["type"]
    )
    pcg_template_graph_paths = [
        row["graph_path"] for row in templates
        if row["class"] == "PCGComponent"
    ]
    total_ism_instances = sum(max(0, count) for _, _, count in ism_rows)
    log_path, marker_found, log_errors = scan_latest_log("MCP_CUBELESS_ED_DESIGNER_CONTROL_ACTOR_BUILD_BEGIN")

    expected_total_points = sum(expected_counts.values())
    validation_pass = all([
        len(rows) == expected_total_points,
        profile_counts == expected_counts,
        profile_types == {"GroundControls": [1], "DitchHierarchy": [2]},
        pass_count == expected_total_points,
        unknown_profile_count == 0,
        type_mismatch_count == 0,
        len(spline_components) >= 1,
        len(pcg_components) >= 1,
        config["DESIGNER_GRAPH_PATH"] in pcg_template_graph_paths,
        total_ism_instances == expected_total_points,
        not log_errors,
    ])

    print(VERIFY_MARKER)
    print(f"production_blueprint={config['BLUEPRINT_PATH']}")
    print(f"production_class={config['BLUEPRINT_CLASS_PATH']}")
    print(f"validation_actor={actor.get_actor_label()}")
    print(f"spline_component_count={len(spline_components)}")
    print(f"pcg_component_count={len(pcg_components)}")
    print(f"pcg_template_graph_paths={pcg_template_graph_paths}")
    print(f"expected_total_points={expected_total_points}")
    print(f"point_count={len(rows)}")
    print(f"profile_counts={profile_counts}")
    print(f"profile_types={profile_types}")
    print(f"designer_control_layer_pass_count={pass_count}")
    print(f"unknown_profile_count={unknown_profile_count}")
    print(f"type_mismatch_count={type_mismatch_count}")
    print(f"total_ism_instances={total_ism_instances}")
    print(f"ism_rows={ism_rows}")
    print(f"component_templates={templates}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print("rows_sample=")
    for row in sorted(rows, key=lambda item: (item["designer_profile_id"], item["seed"]))[:24]:
        print(
            "  Profile={designer_profile_id} Type={designer_profile_type} "
            "Seed={seed} Density={density} ControlPass={designer_control_layer_pass}".format(**row)
        )
    print(f"designer_control_actor_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_DESIGNER_CONTROL_ACTOR_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED designer control actor verification failed")


if __name__ == "__main__":
    main()
