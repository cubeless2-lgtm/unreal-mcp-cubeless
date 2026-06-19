import pathlib
from collections import defaultdict

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_matrix_selector_blueprint.py",
    )
).parent
MATRIX_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_designer_matrix_presets.py"
APPLY_SCRIPT = SCRIPT_DIR / "apply_cubeless_ed_matrix_selector.py"

BLUEPRINT_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGMatrixSelector.BP_Cubeless_ED_PCGMatrixSelector"
)
BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGMatrixSelector.BP_Cubeless_ED_PCGMatrixSelector_C"
)
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_MatrixSelector"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0
VERIFY_MARKER = "MCP_CUBELESS_ED_MATRIX_SELECTOR_VERIFY_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")


def load_matrix_config():
    namespace = {"__name__": "_cubeless_ed_designer_matrix_presets_config"}
    with open(MATRIX_BUILDER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(MATRIX_BUILDER_SCRIPT), "exec")
    exec(code, namespace)
    return namespace


def load_apply_module():
    namespace = {"__name__": "_cubeless_ed_matrix_selector_apply", "__file__": str(APPLY_SCRIPT)}
    with open(APPLY_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(APPLY_SCRIPT), "exec")
    exec(code, namespace)
    return namespace


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


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


def selector_label(spec):
    return f"{ACTOR_LABEL_PREFIX}_{spec['name']}_Validation"


def find_actor_by_label(label):
    return next((actor for actor in get_all_level_actors() if actor.get_actor_label() == label), None)


def configure_validation_spline(actor):
    splines = actor.get_components_by_class(unreal.SplineComponent)
    if not splines:
        raise RuntimeError("Matrix selector actor has no SplineComponent")
    half_length = (float(TARGET_SAMPLE_COUNT) - 1.0) * float(TARGET_POINT_SPACING) * 0.5
    for spline in splines:
        spline.clear_spline_points(False)
        spline.add_spline_point(unreal.Vector(0, -half_length, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, 0, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, half_length, 0), unreal.SplineCoordinateSpace.LOCAL, True)
        spline.update_spline()


def set_int_property(actor, prop_name, value):
    actor.set_editor_property(prop_name, int(value))


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
    helpers = unreal.PCGMetadataAccessorHelpers
    rows = []
    for entry in entries:
        entry = int(entry)
        rows.append({
            "metadata_entry": entry,
            "designer_profile_id": get_int_attr(helpers, entry, metadata, "DesignerProfileId"),
            "designer_amount_id": get_int_attr(helpers, entry, metadata, "DesignerAmountId"),
            "designer_combo_id": get_int_attr(helpers, entry, metadata, "DesignerComboId"),
            "designer_combo_type": get_int_attr(helpers, entry, metadata, "DesignerComboType"),
            "designer_ground_amount_type": get_int_attr(helpers, entry, metadata, "DesignerGroundAmountType"),
            "designer_ditch_amount_type": get_int_attr(helpers, entry, metadata, "DesignerDitchAmountType"),
            "designer_amount_pass": get_bool_attr(helpers, entry, metadata, "DesignerAmountPass"),
            "designer_combo_pass": get_bool_attr(helpers, entry, metadata, "DesignerComboPass"),
            "designer_matrix_pass": get_bool_attr(helpers, entry, metadata, "DesignerMatrixPass"),
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


def spawn_selector_actor(spec, index, apply_module):
    label = selector_label(spec)
    existing_actor = find_actor_by_label(label)
    if existing_actor:
        unreal.EditorLevelLibrary.destroy_actor(existing_actor)

    actor_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not actor_class:
        raise RuntimeError(f"Missing matrix selector Blueprint class: {BLUEPRINT_CLASS_PATH}")

    row = index // 3
    column = index % 3
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(19800 + column * 560, row * 520, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(label)
    set_int_property(actor, "GroundAmountType", spec["ground_amount_type"])
    set_int_property(actor, "DitchAmountType", spec["ditch_amount_type"])
    configure_validation_spline(actor)
    apply_result = apply_module["apply_matrix_selector"](actor, force=True)
    return actor, apply_result


def validate_selector(spec, config):
    label = selector_label(spec)
    actor = find_actor_by_label(label)
    if not actor:
        raise RuntimeError(
            f"Missing prepared matrix selector validation actor: {label}. "
            "Run prepare_cubeless_ed_matrix_selector_validation.py first."
        )

    components = actor.get_components_by_class(unreal.PCGComponent)
    if not components:
        raise RuntimeError(f"Matrix selector actor has no PCGComponent: {label}")
    component = components[0]
    graph_instance = component.get_editor_property("graph_instance")
    graph = graph_instance.get_editor_property("graph") if graph_instance else None
    graph_path = graph.get_path_name() if graph else None
    expected_graph_path = config["MATRIX_GRAPH_PATHS"][spec["name"]]
    rows = get_point_rows(get_generated_point_data(component))
    ism_rows = get_ism_rows(actor)

    profile_counts = defaultdict(int)
    amount_counts = defaultdict(int)
    for row in rows:
        profile_counts[row["designer_profile_id"]] += 1
        amount_counts[row["designer_amount_id"]] += 1

    total_ism_instances = sum(max(0, count) for _, _, count in ism_rows)
    combo_id_mismatch_count = sum(1 for row in rows if row["designer_combo_id"] != spec["combo_id"])
    combo_type_mismatch_count = sum(1 for row in rows if row["designer_combo_type"] != spec["combo_type"])
    ground_axis_mismatch_count = sum(
        1 for row in rows
        if row["designer_ground_amount_type"] != spec["ground_amount_type"]
    )
    ditch_axis_mismatch_count = sum(
        1 for row in rows
        if row["designer_ditch_amount_type"] != spec["ditch_amount_type"]
    )
    amount_pass_count = sum(1 for row in rows if row["designer_amount_pass"])
    combo_pass_count = sum(1 for row in rows if row["designer_combo_pass"])
    matrix_pass_count = sum(1 for row in rows if row["designer_matrix_pass"])
    validation_pass = all([
        graph_path == expected_graph_path,
        len(rows) == spec["expected_points"],
        total_ism_instances == spec["expected_ism"],
        dict(profile_counts) == spec["expected_profile_counts"],
        dict(amount_counts) == spec["expected_amount_counts"],
        combo_id_mismatch_count == 0,
        combo_type_mismatch_count == 0,
        ground_axis_mismatch_count == 0,
        ditch_axis_mismatch_count == 0,
        amount_pass_count == spec["expected_points"],
        combo_pass_count == spec["expected_points"],
        matrix_pass_count == spec["expected_points"],
    ])
    return {
        "matrix": spec["name"],
        "actor": actor.get_actor_label(),
        "graph": graph_path,
        "expected_graph": expected_graph_path,
        "ground_amount_type": spec["ground_amount_type"],
        "ditch_amount_type": spec["ditch_amount_type"],
        "point_count": len(rows),
        "expected_points": spec["expected_points"],
        "total_ism_instances": total_ism_instances,
        "expected_ism": spec["expected_ism"],
        "profile_counts": dict(profile_counts),
        "amount_counts": dict(amount_counts),
        "combo_id_mismatch_count": combo_id_mismatch_count,
        "combo_type_mismatch_count": combo_type_mismatch_count,
        "ground_axis_mismatch_count": ground_axis_mismatch_count,
        "ditch_axis_mismatch_count": ditch_axis_mismatch_count,
        "amount_pass_count": amount_pass_count,
        "combo_pass_count": combo_pass_count,
        "matrix_pass_count": matrix_pass_count,
        "ism_rows": ism_rows,
        "validation_pass": validation_pass,
    }


def main():
    print(VERIFY_MARKER)
    blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
    if not blueprint:
        raise RuntimeError(f"Missing matrix selector Blueprint: {BLUEPRINT_PATH}")

    ensure_validation_level_loaded()
    config = load_matrix_config()
    apply_module = load_apply_module()
    specs = config["MATRIX_SPECS"]

    if VALIDATION_MODE == "prepare":
        results = [spawn_selector_actor(spec, index, apply_module) for index, spec in enumerate(specs)]
        print(f"matrix_selector_blueprint={BLUEPRINT_PATH}")
        print(f"matrix_selector_class={BLUEPRINT_CLASS_PATH}")
        for actor, apply_result in results:
            print(f"prepared_actor={actor.get_actor_label()}")
            print(f"  apply_result={apply_result}")
        print("matrix_selector_validation_prepared=True")
        print("MCP_CUBELESS_ED_MATRIX_SELECTOR_VERIFY_END")
        return

    results = [validate_selector(spec, config) for spec in specs]
    log_path, marker_found, log_errors = scan_latest_log(VERIFY_MARKER)
    validation_pass = all(result["validation_pass"] for result in results) and not log_errors

    print(f"matrix_selector_blueprint={BLUEPRINT_PATH}")
    print(f"matrix_selector_class={BLUEPRINT_CLASS_PATH}")
    for result in results:
        print(f"matrix={result['matrix']}")
        print(f"  actor={result['actor']}")
        print(f"  graph={result['graph']}")
        print(f"  expected_graph={result['expected_graph']}")
        print(f"  axes=ground:{result['ground_amount_type']} ditch:{result['ditch_amount_type']}")
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  total_ism_instances={result['total_ism_instances']}")
        print(f"  expected_ism={result['expected_ism']}")
        print(f"  profile_counts={result['profile_counts']}")
        print(f"  amount_counts={result['amount_counts']}")
        print(f"  combo_id_mismatch_count={result['combo_id_mismatch_count']}")
        print(f"  combo_type_mismatch_count={result['combo_type_mismatch_count']}")
        print(f"  ground_axis_mismatch_count={result['ground_axis_mismatch_count']}")
        print(f"  ditch_axis_mismatch_count={result['ditch_axis_mismatch_count']}")
        print(f"  amount_pass_count={result['amount_pass_count']}")
        print(f"  combo_pass_count={result['combo_pass_count']}")
        print(f"  matrix_pass_count={result['matrix_pass_count']}")
        print(f"  ism_rows={result['ism_rows']}")
        print(f"  validation_pass={result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"matrix_selector_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_MATRIX_SELECTOR_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED matrix selector verification failed")


if __name__ == "__main__":
    main()
