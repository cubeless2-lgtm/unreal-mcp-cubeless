import pathlib
from collections import defaultdict

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\verify_cubeless_ed_authoring_selector_blueprint.py",
    )
).parent
APPLY_SCRIPT = SCRIPT_DIR / "apply_cubeless_ed_authoring_selector.py"

BLUEPRINT_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGAuthoringSelector.BP_Cubeless_ED_PCGAuthoringSelector"
)
BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGAuthoringSelector.BP_Cubeless_ED_PCGAuthoringSelector_C"
)
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_AuthoringSelector"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0
VERIFY_MARKER = "MCP_CUBELESS_ED_AUTHORING_SELECTOR_VERIFY_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")

SELECTOR_SPECS = [
    {
        "name": "Sparse",
        "designer_combo_type": 1,
        "combo_id": 401,
        "combo_type": 1,
        "selected_component": "PCG_Sparse",
        "expected_points": 21,
        "expected_ism": 21,
        "expected_profile_counts": {10: 3, 20: 18},
        "expected_amount_counts": {201: 3, 301: 18},
    },
    {
        "name": "Normal",
        "designer_combo_type": 2,
        "combo_id": 402,
        "combo_type": 2,
        "selected_component": "PCG_Normal",
        "expected_points": 50,
        "expected_ism": 50,
        "expected_profile_counts": {10: 8, 20: 42},
        "expected_amount_counts": {202: 8, 302: 42},
    },
    {
        "name": "Dense",
        "designer_combo_type": 3,
        "combo_id": 403,
        "combo_type": 3,
        "selected_component": "PCG_Dense",
        "expected_points": 100,
        "expected_ism": 100,
        "expected_profile_counts": {10: 16, 20: 84},
        "expected_amount_counts": {203: 16, 303: 84},
    },
]


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def selector_label(spec):
    return f"{ACTOR_LABEL_PREFIX}_{spec['name']}_Validation"


def find_actor_by_label(label):
    return next((actor for actor in get_all_level_actors() if actor.get_actor_label() == label), None)


def get_current_level_path():
    subsystem_cls = getattr(unreal, "UnrealEditorSubsystem", None)
    if subsystem_cls:
        try:
            subsystem = unreal.get_editor_subsystem(subsystem_cls)
            world = subsystem.get_editor_world() if subsystem else None
            if world:
                return world.get_path_name().split(".", 1)[0]
        except Exception:
            pass
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
        if world:
            return world.get_path_name().split(".", 1)[0]
    except Exception:
        return None
    return None


def ensure_validation_level_loaded():
    if get_current_level_path() != LEVEL:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)


def configure_validation_spline(actor):
    splines = actor.get_components_by_class(unreal.SplineComponent)
    if not splines:
        raise RuntimeError("Selector actor has no SplineComponent")
    half_length = (float(TARGET_SAMPLE_COUNT) - 1.0) * float(TARGET_POINT_SPACING) * 0.5
    for spline in splines:
        spline.clear_spline_points(False)
        spline.add_spline_point(unreal.Vector(0, -half_length, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, 0, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, half_length, 0), unreal.SplineCoordinateSpace.LOCAL, True)
        spline.update_spline()


def set_designer_combo_type(actor, value):
    for prop_name in ("DesignerComboType", "designer_combo_type"):
        try:
            actor.set_editor_property(prop_name, int(value))
            return prop_name
        except Exception:
            pass
    raise RuntimeError("Failed to set DesignerComboType on selector actor")


def load_apply_module():
    namespace = {"__name__": "_cubeless_ed_authoring_selector_apply", "__file__": str(APPLY_SCRIPT)}
    with open(APPLY_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(APPLY_SCRIPT), "exec")
    exec(code, namespace)
    return namespace


def get_generated_point_data(component):
    for attempt in range(4):
        collection = component.get_generated_graph_output()
        for item in collection.get_editor_property("tagged_data"):
            data = item.get_editor_property("data").get_editor_property("data")
            if data and hasattr(data, "get_num_points"):
                return data
        if attempt < 3 and component.is_active():
            component.generate(True)
    return None


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
    if not point_data:
        return []
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


def component_key(component):
    name = component.get_name()
    for key in ("PCG_Sparse", "PCG_Normal", "PCG_Dense"):
        if name.startswith(key):
            return key
    return name


def spawn_selector_actor(spec, index, apply_module):
    label = selector_label(spec)
    existing_actor = find_actor_by_label(label)
    if existing_actor:
        unreal.EditorLevelLibrary.destroy_actor(existing_actor)

    actor_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not actor_class:
        raise RuntimeError(f"Missing selector Blueprint class: {BLUEPRINT_CLASS_PATH}")

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(16400 + index * 560, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(label)
    set_prop = set_designer_combo_type(actor, spec["designer_combo_type"])
    configure_validation_spline(actor)
    apply_result = apply_module["apply_selector"](actor, force=True)
    return actor, set_prop, apply_result


def validate_selector(spec, index, apply_module):
    label = selector_label(spec)
    actor = find_actor_by_label(label)
    if not actor:
        raise RuntimeError(
            f"Missing prepared selector validation actor: {label}. "
            "Run prepare_cubeless_ed_authoring_selector_validation.py first."
        )
    try:
        current_combo_type = int(actor.get_editor_property("DesignerComboType"))
    except Exception:
        current_combo_type = None
    set_prop = "prepared_actor"
    apply_result = {
        "actor": actor.get_actor_label(),
        "mode": "verify_existing_after_editor_tick",
        "designer_combo_type": current_combo_type,
    }
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if len(pcg_components) < 3:
        raise RuntimeError(f"Selector actor expected 3 PCG components, found {len(pcg_components)}")

    component_rows = {}
    for component in pcg_components:
        key = component_key(component)
        data = get_generated_point_data(component)
        rows = get_point_rows(data)
        graph_instance = component.get_editor_property("graph_instance")
        graph = graph_instance.get_editor_property("graph") if graph_instance else None
        component_rows[key] = {
            "point_count": len(rows),
            "rows": rows,
            "active": bool(component.is_active()),
            "graph": graph.get_path_name() if graph else None,
        }

    selected_rows = component_rows.get(spec["selected_component"], {}).get("rows", [])
    profile_counts = defaultdict(int)
    amount_counts = defaultdict(int)
    for row in selected_rows:
        profile_counts[row["designer_profile_id"]] += 1
        amount_counts[row["designer_amount_id"]] += 1

    total_ism_instances = sum(max(0, count) for _, _, count in get_ism_rows(actor))
    combo_id_mismatch_count = sum(1 for row in selected_rows if row["designer_combo_id"] != spec["combo_id"])
    combo_type_mismatch_count = sum(1 for row in selected_rows if row["designer_combo_type"] != spec["combo_type"])
    combo_pass_count = sum(1 for row in selected_rows if row["designer_combo_pass"])
    amount_pass_count = sum(1 for row in selected_rows if row["designer_amount_pass"])
    ground_pass_count = sum(
        1 for row in selected_rows
        if row["designer_profile_id"] == 10 and row["cubeless_ground_controls_pass"]
    )
    ditch_side_pass_count = sum(
        1 for row in selected_rows
        if row["designer_profile_id"] == 20 and row["side_mask_filter_pass"]
    )
    ditch_branch_pass_count = sum(
        1 for row in selected_rows
        if row["designer_profile_id"] == 20 and row["branch_density_filter_pass"]
    )
    ditch_ground_pass_count = sum(
        1 for row in selected_rows
        if row["designer_profile_id"] == 20 and row["ground_style_smoke_pass"]
    )
    expected_ground_count = spec["expected_profile_counts"].get(10, 0)
    expected_ditch_count = spec["expected_profile_counts"].get(20, 0)
    unselected_counts = {
        key: row["point_count"]
        for key, row in component_rows.items()
        if key != spec["selected_component"]
    }
    validation_pass = all([
        len(selected_rows) == spec["expected_points"],
        total_ism_instances == spec["expected_ism"],
        dict(profile_counts) == spec["expected_profile_counts"],
        dict(amount_counts) == spec["expected_amount_counts"],
        combo_id_mismatch_count == 0,
        combo_type_mismatch_count == 0,
        combo_pass_count == spec["expected_points"],
        amount_pass_count == spec["expected_points"],
        ground_pass_count == expected_ground_count,
        ditch_side_pass_count == expected_ditch_count,
        ditch_branch_pass_count == expected_ditch_count,
        ditch_ground_pass_count == expected_ditch_count,
        all(count == 0 for count in unselected_counts.values()),
    ])
    return {
        "selector": spec["name"],
        "actor": actor.get_actor_label(),
        "set_property": set_prop,
        "apply_result": apply_result,
        "designer_combo_type": spec["designer_combo_type"],
        "selected_component": spec["selected_component"],
        "component_point_counts": {
            key: value["point_count"]
            for key, value in sorted(component_rows.items())
        },
        "component_graphs": {
            key: value["graph"]
            for key, value in sorted(component_rows.items())
        },
        "point_count": len(selected_rows),
        "expected_points": spec["expected_points"],
        "total_ism_instances": total_ism_instances,
        "expected_ism": spec["expected_ism"],
        "profile_counts": dict(profile_counts),
        "amount_counts": dict(amount_counts),
        "combo_id_mismatch_count": combo_id_mismatch_count,
        "combo_type_mismatch_count": combo_type_mismatch_count,
        "combo_pass_count": combo_pass_count,
        "amount_pass_count": amount_pass_count,
        "ground_pass_count": ground_pass_count,
        "ditch_side_pass_count": ditch_side_pass_count,
        "ditch_branch_pass_count": ditch_branch_pass_count,
        "ditch_ground_pass_count": ditch_ground_pass_count,
        "unselected_counts": unselected_counts,
        "ism_rows": get_ism_rows(actor),
        "validation_pass": validation_pass,
        "rows_sample": sorted(
            selected_rows,
            key=lambda item: (
                item["designer_profile_id"] or -1,
                item["designer_amount_id"] or -1,
                item["seed"],
            ),
        )[:18],
    }


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
    print(VERIFY_MARKER)
    blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
    if not blueprint:
        raise RuntimeError(f"Missing selector Blueprint: {BLUEPRINT_PATH}")

    ensure_validation_level_loaded()
    apply_module = load_apply_module()
    if VALIDATION_MODE == "prepare":
        results = [spawn_selector_actor(spec, index, apply_module) for index, spec in enumerate(SELECTOR_SPECS)]
        print(f"selector_blueprint={BLUEPRINT_PATH}")
        print(f"selector_class={BLUEPRINT_CLASS_PATH}")
        for actor, set_prop, apply_result in results:
            print(f"prepared_actor={actor.get_actor_label()}")
            print(f"  set_property={set_prop}")
            print(f"  apply_result={apply_result}")
        print("authoring_selector_validation_prepared=True")
        print("MCP_CUBELESS_ED_AUTHORING_SELECTOR_VERIFY_END")
        return

    results = [validate_selector(spec, index, apply_module) for index, spec in enumerate(SELECTOR_SPECS)]
    log_path, marker_found, log_errors = scan_latest_log(VERIFY_MARKER)
    validation_pass = all(result["validation_pass"] for result in results) and not log_errors

    print(f"selector_blueprint={BLUEPRINT_PATH}")
    print(f"selector_class={BLUEPRINT_CLASS_PATH}")
    for result in results:
        print(f"selector={result['selector']}")
        print(f"  actor={result['actor']}")
        print(f"  set_property={result['set_property']}")
        print(f"  apply_result={result['apply_result']}")
        print(f"  designer_combo_type={result['designer_combo_type']}")
        print(f"  selected_component={result['selected_component']}")
        print(f"  component_point_counts={result['component_point_counts']}")
        print(f"  component_graphs={result['component_graphs']}")
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  total_ism_instances={result['total_ism_instances']}")
        print(f"  expected_ism={result['expected_ism']}")
        print(f"  profile_counts={result['profile_counts']}")
        print(f"  amount_counts={result['amount_counts']}")
        print(f"  combo_id_mismatch_count={result['combo_id_mismatch_count']}")
        print(f"  combo_type_mismatch_count={result['combo_type_mismatch_count']}")
        print(f"  combo_pass_count={result['combo_pass_count']}")
        print(f"  amount_pass_count={result['amount_pass_count']}")
        print(f"  ground_pass_count={result['ground_pass_count']}")
        print(f"  ditch_side_pass_count={result['ditch_side_pass_count']}")
        print(f"  ditch_branch_pass_count={result['ditch_branch_pass_count']}")
        print(f"  ditch_ground_pass_count={result['ditch_ground_pass_count']}")
        print(f"  unselected_counts={result['unselected_counts']}")
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
    print(f"authoring_selector_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_AUTHORING_SELECTOR_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED authoring selector verification failed")


if __name__ == "__main__":
    main()
