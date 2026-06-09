import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\verify_cubeless_ed_style_profile_matrix_selector_blueprint.py",
    )
).parent
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_style_profile_matrix_presets.py"
APPLY_SCRIPT = SCRIPT_DIR / "apply_cubeless_ed_style_profile_matrix_selector.py"
STYLE_VERIFY_SCRIPT = SCRIPT_DIR / "verify_cubeless_ed_style_profile_matrix_presets.py"

BLUEPRINT_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGStyleProfileMatrixSelector.BP_Cubeless_ED_PCGStyleProfileMatrixSelector"
)
BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGStyleProfileMatrixSelector.BP_Cubeless_ED_PCGStyleProfileMatrixSelector_C"
)
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_StyleProfileMatrixSelector"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0
VERIFY_MARKER = "MCP_CUBELESS_ED_STYLE_PROFILE_MATRIX_SELECTOR_VERIFY_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")


def load_builder_config():
    namespace = {"__name__": "_cubeless_ed_style_profile_matrix_presets_config"}
    with open(BUILDER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(BUILDER_SCRIPT), "exec")
    exec(code, namespace)
    namespace["ACTOR_LABEL_PREFIX"] = ACTOR_LABEL_PREFIX
    return namespace


def load_apply_module():
    namespace = {"__name__": "_cubeless_ed_style_profile_matrix_selector_apply", "__file__": str(APPLY_SCRIPT)}
    with open(APPLY_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(APPLY_SCRIPT), "exec")
    exec(code, namespace)
    return namespace


def load_style_verify_module():
    namespace = {"__name__": "_cubeless_ed_style_profile_matrix_verify", "__file__": str(STYLE_VERIFY_SCRIPT)}
    with open(STYLE_VERIFY_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(STYLE_VERIFY_SCRIPT), "exec")
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
        raise RuntimeError("Style profile matrix selector actor has no SplineComponent")
    half_length = (float(TARGET_SAMPLE_COUNT) - 1.0) * float(TARGET_POINT_SPACING) * 0.5
    for spline in splines:
        spline.clear_spline_points(False)
        spline.add_spline_point(unreal.Vector(0, -half_length, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, 0, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, half_length, 0), unreal.SplineCoordinateSpace.LOCAL, True)
        spline.update_spline()


def set_int_property(actor, prop_name, value):
    actor.set_editor_property(prop_name, int(value))


def ui_axis_value(value):
    value = int(value)
    if value in (1, 2, 3):
        return value
    return 2


def spawn_selector_actor(spec, index, apply_module):
    label = selector_label(spec)
    existing_actor = find_actor_by_label(label)
    if existing_actor:
        unreal.EditorLevelLibrary.destroy_actor(existing_actor)

    actor_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not actor_class:
        raise RuntimeError(f"Missing style profile matrix selector Blueprint class: {BLUEPRINT_CLASS_PATH}")

    row = index // 10
    column = index % 10
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(30200 + column * 520, row * 520, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(label)
    set_int_property(actor, "VisualStyleType", spec["style_type"])
    set_int_property(actor, "ProfileMode", spec["profile_mode"])
    set_int_property(actor, "GroundAmountType", ui_axis_value(spec["ground_amount_type"]))
    set_int_property(actor, "DitchAmountType", ui_axis_value(spec["ditch_amount_type"]))
    configure_validation_spline(actor)
    apply_result = apply_module["apply_style_profile_matrix_selector"](actor, force=True)
    return actor, apply_result


def get_actor_graph_path(actor):
    components = actor.get_components_by_class(unreal.PCGComponent)
    if not components:
        return None
    graph_instance = components[0].get_editor_property("graph_instance")
    graph = graph_instance.get_editor_property("graph") if graph_instance else None
    return graph.get_path_name() if graph else None


def validate_selector(spec, config, style_verify):
    label = selector_label(spec)
    actor = find_actor_by_label(label)
    if not actor:
        raise RuntimeError(
            f"Missing prepared style profile matrix selector validation actor: {label}. "
            "Run prepare_cubeless_ed_style_profile_matrix_selector_validation.py first."
        )
    expected_graph_path = config["STYLE_PROFILE_MATRIX_GRAPH_PATHS"][spec["name"]]
    actual_graph_path = get_actor_graph_path(actor)
    result = style_verify["validate_style_profile_matrix"](spec, config)
    result["actual_graph"] = actual_graph_path
    result["expected_graph"] = expected_graph_path
    result["graph_match"] = actual_graph_path == expected_graph_path
    result["validation_pass"] = bool(result["validation_pass"] and result["graph_match"])
    return result


def main():
    print(VERIFY_MARKER)
    blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
    if not blueprint:
        raise RuntimeError(f"Missing style profile matrix selector Blueprint: {BLUEPRINT_PATH}")

    ensure_validation_level_loaded()
    config = load_builder_config()
    apply_module = load_apply_module()
    style_verify = load_style_verify_module()
    specs = config["STYLE_PROFILE_MATRIX_SPECS"]

    if VALIDATION_MODE == "prepare":
        results = [spawn_selector_actor(spec, index, apply_module) for index, spec in enumerate(specs)]
        print(f"style_profile_matrix_selector_blueprint={BLUEPRINT_PATH}")
        print(f"style_profile_matrix_selector_class={BLUEPRINT_CLASS_PATH}")
        for actor, apply_result in results:
            print(f"prepared_actor={actor.get_actor_label()}")
            print(f"  apply_result={apply_result}")
        print("style_profile_matrix_selector_validation_prepared=True")
        print("MCP_CUBELESS_ED_STYLE_PROFILE_MATRIX_SELECTOR_VERIFY_END")
        return

    results = [validate_selector(spec, config, style_verify) for spec in specs]
    log_path, marker_found, log_errors = style_verify["scan_latest_log"](VERIFY_MARKER)
    validation_pass = all(result["validation_pass"] for result in results) and not log_errors

    print(f"style_profile_matrix_selector_blueprint={BLUEPRINT_PATH}")
    print(f"style_profile_matrix_selector_class={BLUEPRINT_CLASS_PATH}")
    for result in results:
        print(f"style_profile_matrix={result['style_profile_matrix']}")
        print(f"  actor={result['actor']}")
        print(f"  actual_graph={result['actual_graph']}")
        print(f"  expected_graph={result['expected_graph']}")
        print(f"  graph_match={result['graph_match']}")
        print(f"  style={result['style_id']}/{result['style_type']}")
        print(
            "  axes=profile:{profile_mode} ground:{ground_amount_type} ditch:{ditch_amount_type}".format(**result)
        )
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  total_ism_instances={result['total_ism_instances']}")
        print(f"  expected_ism={result['expected_ism']}")
        print(f"  profile_counts={result['profile_counts']}")
        print(f"  amount_counts={result['amount_counts']}")
        print(f"  style_counts={result['style_counts']}")
        print(f"  mesh_paths={result['mesh_paths']}")
        print(f"  expected_mesh_paths={result['expected_mesh_paths']}")
        print(f"  validation_pass={result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"style_profile_matrix_selector_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_STYLE_PROFILE_MATRIX_SELECTOR_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED style profile matrix selector verification failed")


if __name__ == "__main__":
    main()
