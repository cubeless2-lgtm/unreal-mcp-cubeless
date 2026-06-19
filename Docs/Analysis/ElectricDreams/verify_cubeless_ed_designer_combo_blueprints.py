import pathlib
from collections import defaultdict

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_designer_combo_blueprints.py",
    )
).resolve().parent

BUILDER_SCRIPT = str(SCRIPT_DIR / "build_cubeless_ed_designer_combo_blueprints.py")
VERIFY_MARKER = "MCP_CUBELESS_ED_DESIGNER_COMBO_BLUEPRINTS_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_cubeless_ed_designer_combo_blueprints_config"}
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
            "designer_amount_id": get_int_attr(helpers, entry, metadata, "DesignerAmountId"),
            "designer_amount_type": get_int_attr(helpers, entry, metadata, "DesignerAmountType"),
            "designer_amount_pass": get_bool_attr(helpers, entry, metadata, "DesignerAmountPass"),
            "designer_combo_id": get_int_attr(helpers, entry, metadata, "DesignerComboId"),
            "designer_combo_type": get_int_attr(helpers, entry, metadata, "DesignerComboType"),
            "designer_combo_pass": get_bool_attr(helpers, entry, metadata, "DesignerComboPass"),
            "cubeless_ground_controls_pass": get_bool_attr(helpers, entry, metadata, "CubelessGroundControlsPass"),
            "side_mask_filter_pass": get_bool_attr(helpers, entry, metadata, "SideMaskFilterPass"),
            "branch_density_filter_pass": get_bool_attr(helpers, entry, metadata, "BranchDensityFilterPass"),
            "ground_style_smoke_pass": get_bool_attr(helpers, entry, metadata, "GroundStyleSmokePass"),
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


def validate_blueprint(spec, config):
    blueprint = unreal.EditorAssetLibrary.load_asset(config["blueprint_path"](spec))
    if not blueprint:
        raise RuntimeError(f"Missing combo Blueprint: {config['blueprint_path'](spec)}")
    templates = get_subobject_templates(blueprint)
    pcg_template_graph_paths = [
        row["graph_path"] for row in templates
        if row["class"] == "PCGComponent"
    ]

    label = f"{config['ACTOR_LABEL_PREFIX']}_{spec['name']}_Validation"
    actor = get_actor(label)
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    spline_components = actor.get_components_by_class(unreal.SplineComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {label}")
    if not spline_components:
        raise RuntimeError(f"Validation actor has no SplineComponent: {label}")

    rows = get_point_rows(get_generated_point_data(pcg_components[0]))
    ism_rows = get_ism_rows(actor)
    profile_type_by_id = {
        branch["profile_id"]: branch["profile_type"]
        for branch in spec["branches"]
    }
    amount_type_by_id = {
        branch["amount_id"]: branch["amount_type"]
        for branch in spec["branches"]
    }
    profile_counts = defaultdict(int)
    amount_counts = defaultdict(int)
    profile_amount_counts = defaultdict(int)
    for row in rows:
        profile_counts[row["designer_profile_id"]] += 1
        amount_counts[row["designer_amount_id"]] += 1
        profile_amount_counts[(row["designer_profile_id"], row["designer_amount_id"])] += 1

    expected_profile_amount_counts = {
        (branch["profile_id"], branch["amount_id"]): branch["expected_points"]
        for branch in spec["branches"]
    }
    profile_type_mismatch_count = sum(
        1 for row in rows
        if row["designer_profile_id"] not in profile_type_by_id
        or row["designer_profile_type"] != profile_type_by_id[row["designer_profile_id"]]
    )
    amount_type_mismatch_count = sum(
        1 for row in rows
        if row["designer_amount_id"] not in amount_type_by_id
        or row["designer_amount_type"] != amount_type_by_id[row["designer_amount_id"]]
    )
    combo_id_mismatch_count = sum(1 for row in rows if row["designer_combo_id"] != spec["combo_id"])
    combo_type_mismatch_count = sum(1 for row in rows if row["designer_combo_type"] != spec["combo_type"])
    amount_pass_count = sum(1 for row in rows if row["designer_amount_pass"])
    combo_pass_count = sum(1 for row in rows if row["designer_combo_pass"])
    ground_pass_count = sum(
        1 for row in rows
        if row["designer_profile_id"] == 10 and row["cubeless_ground_controls_pass"]
    )
    ditch_side_pass_count = sum(
        1 for row in rows
        if row["designer_profile_id"] == 20 and row["side_mask_filter_pass"]
    )
    ditch_branch_pass_count = sum(
        1 for row in rows
        if row["designer_profile_id"] == 20 and row["branch_density_filter_pass"]
    )
    ditch_ground_pass_count = sum(
        1 for row in rows
        if row["designer_profile_id"] == 20 and row["ground_style_smoke_pass"]
    )
    expected_ground_count = spec["expected_profile_counts"].get(10, 0)
    expected_ditch_count = spec["expected_profile_counts"].get(20, 0)
    total_ism_instances = sum(max(0, count) for _, _, count in ism_rows)
    validation_pass = all([
        spec["graph_path"] in pcg_template_graph_paths,
        len(spline_components) >= 1,
        len(pcg_components) >= 1,
        len(rows) == spec["expected_points"],
        total_ism_instances == spec["expected_ism"],
        dict(profile_counts) == spec["expected_profile_counts"],
        dict(amount_counts) == spec["expected_amount_counts"],
        dict(profile_amount_counts) == expected_profile_amount_counts,
        profile_type_mismatch_count == 0,
        amount_type_mismatch_count == 0,
        combo_id_mismatch_count == 0,
        combo_type_mismatch_count == 0,
        amount_pass_count == spec["expected_points"],
        combo_pass_count == spec["expected_points"],
        ground_pass_count == expected_ground_count,
        ditch_side_pass_count == expected_ditch_count,
        ditch_branch_pass_count == expected_ditch_count,
        ditch_ground_pass_count == expected_ditch_count,
    ])
    return {
        "combo": spec["name"],
        "blueprint": config["blueprint_path"](spec),
        "class": config["blueprint_class_path"](spec),
        "actor": label,
        "spline_component_count": len(spline_components),
        "pcg_component_count": len(pcg_components),
        "pcg_template_graph_paths": pcg_template_graph_paths,
        "point_count": len(rows),
        "expected_points": spec["expected_points"],
        "total_ism_instances": total_ism_instances,
        "expected_ism": spec["expected_ism"],
        "profile_counts": dict(profile_counts),
        "amount_counts": dict(amount_counts),
        "profile_amount_counts": {
            f"{key[0]}:{key[1]}": value
            for key, value in sorted(profile_amount_counts.items())
        },
        "combo_id_mismatch_count": combo_id_mismatch_count,
        "combo_type_mismatch_count": combo_type_mismatch_count,
        "profile_type_mismatch_count": profile_type_mismatch_count,
        "amount_type_mismatch_count": amount_type_mismatch_count,
        "amount_pass_count": amount_pass_count,
        "combo_pass_count": combo_pass_count,
        "ground_pass_count": ground_pass_count,
        "ditch_side_pass_count": ditch_side_pass_count,
        "ditch_branch_pass_count": ditch_branch_pass_count,
        "ditch_ground_pass_count": ditch_ground_pass_count,
        "ism_rows": ism_rows,
        "validation_pass": validation_pass,
        "rows_sample": sorted(
            rows,
            key=lambda item: (
                item["designer_profile_id"] or -1,
                item["designer_amount_id"] or -1,
                item["seed"],
            ),
        )[:18],
    }


def main():
    config = load_builder_config()
    results = [validate_blueprint(spec, config) for spec in config["COMBO_BLUEPRINT_SPECS"]]
    log_path, marker_found, log_errors = scan_latest_log("MCP_CUBELESS_ED_DESIGNER_COMBO_BLUEPRINTS_BUILD_BEGIN")
    validation_pass = all(result["validation_pass"] for result in results) and not log_errors

    print(VERIFY_MARKER)
    for result in results:
        print(f"combo={result['combo']}")
        print(f"  blueprint={result['blueprint']}")
        print(f"  class={result['class']}")
        print(f"  actor={result['actor']}")
        print(f"  spline_component_count={result['spline_component_count']}")
        print(f"  pcg_component_count={result['pcg_component_count']}")
        print(f"  pcg_template_graph_paths={result['pcg_template_graph_paths']}")
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  total_ism_instances={result['total_ism_instances']}")
        print(f"  expected_ism={result['expected_ism']}")
        print(f"  profile_counts={result['profile_counts']}")
        print(f"  amount_counts={result['amount_counts']}")
        print(f"  profile_amount_counts={result['profile_amount_counts']}")
        print(f"  combo_id_mismatch_count={result['combo_id_mismatch_count']}")
        print(f"  combo_type_mismatch_count={result['combo_type_mismatch_count']}")
        print(f"  profile_type_mismatch_count={result['profile_type_mismatch_count']}")
        print(f"  amount_type_mismatch_count={result['amount_type_mismatch_count']}")
        print(f"  amount_pass_count={result['amount_pass_count']}")
        print(f"  combo_pass_count={result['combo_pass_count']}")
        print(f"  ground_pass_count={result['ground_pass_count']}")
        print(f"  ditch_side_pass_count={result['ditch_side_pass_count']}")
        print(f"  ditch_branch_pass_count={result['ditch_branch_pass_count']}")
        print(f"  ditch_ground_pass_count={result['ditch_ground_pass_count']}")
        print(f"  ism_rows={result['ism_rows']}")
        print(f"  validation_pass={result['validation_pass']}")
        print("  rows_sample=")
        for row in result["rows_sample"]:
            print(
                "    Combo={designer_combo_id}/{designer_combo_type} "
                "Profile={designer_profile_id}/{designer_profile_type} "
                "Amount={designer_amount_id}/{designer_amount_type} "
                "Seed={seed} Density={density} "
                "AmountPass={designer_amount_pass} ComboPass={designer_combo_pass}".format(**row)
            )
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"designer_combo_blueprints_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_DESIGNER_COMBO_BLUEPRINTS_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED designer combo Blueprint verification failed")


if __name__ == "__main__":
    main()
