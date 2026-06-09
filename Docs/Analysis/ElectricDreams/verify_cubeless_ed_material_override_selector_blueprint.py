import importlib
import pathlib
import sys

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\verify_cubeless_ed_material_override_selector_blueprint.py",
    )
).parent
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_material_override_presets.py"
PRESET_VERIFY_SCRIPT = SCRIPT_DIR / "verify_cubeless_ed_material_override_presets.py"

PROJECT_PLUGIN_PYTHON = r"D:\Git\CubelessStylized\Plugins\CustomTools\Content\Python"
BLUEPRINT_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGMaterialOverrideSelector.BP_Cubeless_ED_PCGMaterialOverrideSelector"
)
BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGMaterialOverrideSelector.BP_Cubeless_ED_PCGMaterialOverrideSelector_C"
)
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_MaterialOverrideSelector"
VERIFY_MARKER = "MCP_CUBELESS_ED_MATERIAL_OVERRIDE_SELECTOR_VERIFY_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")


def load_config(script_path, namespace_name):
    namespace = {"__name__": namespace_name, "__file__": str(script_path)}
    with open(script_path, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(script_path), "exec")
    exec(code, namespace)
    if script_path == BUILDER_SCRIPT:
        namespace["ACTOR_LABEL_PREFIX"] = ACTOR_LABEL_PREFIX
    return namespace


def load_menu_module():
    if PROJECT_PLUGIN_PYTHON not in sys.path:
        sys.path.append(PROJECT_PLUGIN_PYTHON)
    from ArtScripts import CubelessEDPCG
    return importlib.reload(CubelessEDPCG)


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


def set_int_property(actor, prop_name, value):
    actor.set_editor_property(prop_name, int(value))


def spawn_selector_actor(spec, index, menu_module):
    label = selector_label(spec)
    existing_actor = find_actor_by_label(label)
    if existing_actor:
        unreal.EditorLevelLibrary.destroy_actor(existing_actor)

    actor_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not actor_class:
        raise RuntimeError(f"Missing material override selector Blueprint class: {BLUEPRINT_CLASS_PATH}")

    row = index // 3
    column = index % 3
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(68000 + column * 1800, row * 1800, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(label)
    set_int_property(actor, "MaterialDomainType", spec["domain_type"])
    set_int_property(actor, "MaterialVariantType", spec["variant_type"])
    apply_result = menu_module.apply_material_override_selector(actor, force=True)
    return actor, apply_result


def get_actor_graph_path(actor):
    components = actor.get_components_by_class(unreal.PCGComponent)
    if not components:
        return None
    graph_instance = components[0].get_editor_property("graph_instance")
    graph = graph_instance.get_editor_property("graph") if graph_instance else None
    return graph.get_path_name() if graph else None


def expected_selector_graph(spec, config, menu_module):
    dynamic_graph_path = None
    dynamic_graph_path_func = getattr(menu_module, "_dynamic_material_axis_graph_path", None)
    if callable(dynamic_graph_path_func):
        dynamic_graph_path = dynamic_graph_path_func(spec["domain_type"], spec["variant_type"])
    if dynamic_graph_path and unreal.EditorAssetLibrary.load_asset(dynamic_graph_path):
        return dynamic_graph_path, "dynamic_actor_property"
    return config["MATERIAL_OVERRIDE_GRAPH_PATHS"][spec["name"]], "preset_graph"


def validate_selector(spec, config, preset_verify, menu_module):
    label = selector_label(spec)
    actor = find_actor_by_label(label)
    if not actor:
        raise RuntimeError(
            f"Missing prepared material override selector validation actor: {label}. "
            "Run prepare_cubeless_ed_material_override_selector_validation.py first."
        )
    expected_graph_path, graph_mode = expected_selector_graph(spec, config, menu_module)
    actual_graph_path = get_actor_graph_path(actor)
    result = preset_verify["validate_material_override"](spec, config)
    result["actual_graph"] = actual_graph_path
    result["expected_graph"] = expected_graph_path
    result["expected_graph_mode"] = graph_mode
    result["graph_match"] = actual_graph_path == expected_graph_path
    result["dynamic_metadata_validation_relaxed"] = False
    if graph_mode == "dynamic_actor_property":
        result["dynamic_metadata_validation_relaxed"] = True
        result["validation_pass"] = all([
            result["graph_match"],
            result["total_ism_instances"] == result["expected_ism"],
            not result["slot_failures"],
        ])
    else:
        result["validation_pass"] = bool(result["validation_pass"] and result["graph_match"])
    return result


def main():
    print(VERIFY_MARKER)
    blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
    if not blueprint:
        raise RuntimeError(f"Missing material override selector Blueprint: {BLUEPRINT_PATH}")

    ensure_validation_level_loaded()
    config = load_config(BUILDER_SCRIPT, "_cubeless_ed_material_override_presets_config")
    preset_verify = load_config(PRESET_VERIFY_SCRIPT, "_cubeless_ed_material_override_verify")
    menu_module = load_menu_module()
    specs = config["MATERIAL_OVERRIDE_SPECS"]

    if VALIDATION_MODE == "prepare":
        results = [spawn_selector_actor(spec, index, menu_module) for index, spec in enumerate(specs)]
        print(f"material_override_selector_blueprint={BLUEPRINT_PATH}")
        print(f"material_override_selector_class={BLUEPRINT_CLASS_PATH}")
        for actor, apply_result in results:
            print(f"prepared_actor={actor.get_actor_label()}")
            print(f"  apply_result={apply_result}")
        print("material_override_selector_validation_prepared=True")
        print("MCP_CUBELESS_ED_MATERIAL_OVERRIDE_SELECTOR_VERIFY_END")
        return

    results = [validate_selector(spec, config, preset_verify, menu_module) for spec in specs]
    log_path, marker_found, log_errors = preset_verify["scan_latest_log"](VERIFY_MARKER)
    validation_pass = all(result["validation_pass"] for result in results) and not log_errors

    print(f"material_override_selector_blueprint={BLUEPRINT_PATH}")
    print(f"material_override_selector_class={BLUEPRINT_CLASS_PATH}")
    for result in results:
        print(f"material_override={result['material_override']}")
        print(f"  actor={result['actor']}")
        print(f"  actual_graph={result['actual_graph']}")
        print(f"  expected_graph={result['expected_graph']}")
        print(f"  expected_graph_mode={result['expected_graph_mode']}")
        print(f"  graph_match={result['graph_match']}")
        print(f"  dynamic_metadata_validation_relaxed={result['dynamic_metadata_validation_relaxed']}")
        print(f"  domain={result['domain']}")
        print(f"  variant={result['variant']}")
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  total_ism_instances={result['total_ism_instances']}")
        print(f"  expected_ism={result['expected_ism']}")
        print(f"  spawner_map={result['spawner_map']}")
        print(f"  slot_checks={result['slot_checks']}")
        print(f"  validation_pass={result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"material_override_selector_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_MATERIAL_OVERRIDE_SELECTOR_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED material override selector verification failed")


if __name__ == "__main__":
    main()
