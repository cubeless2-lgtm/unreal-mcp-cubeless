import importlib
import pathlib
import sys

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\verify_cubeless_ed_dynamic_material_axis_menu_apply.py",
    )
).parent
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_dynamic_material_axis_actor_property_selector_compat.py"
AXIS_VERIFY_SCRIPT = SCRIPT_DIR / "verify_cubeless_ed_dynamic_material_axis_by_point.py"

PROJECT_PLUGIN_PYTHON = r"D:\Git\CubelessStylized\Plugins\CustomTools\Content\Python"
VERIFY_MARKER = "MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_MENU_APPLY_VERIFY_BEGIN"
ACTOR_LABEL = "MCP_Cubeless_ED_DynamicMaterialAxis_MenuApply_GroundFoliage_CoolLeaf_Validation"


def load_script(script_path, namespace_name):
    namespace = {"__name__": namespace_name, "__file__": str(script_path)}
    with open(script_path, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(script_path), "exec")
    exec(code, namespace)
    return namespace


CONFIG = load_script(BUILDER_SCRIPT, "_cubeless_ed_dynamic_material_axis_actor_property_config")
BASE_VERIFY = load_script(AXIS_VERIFY_SCRIPT, "_cubeless_ed_dynamic_material_axis_verify_helpers")


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
    if get_current_level_path() != CONFIG["LEVEL"]:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(CONFIG["LEVEL"])


def find_actor(label):
    return next((actor for actor in get_all_level_actors() if actor.get_actor_label() == label), None)


def get_or_spawn_selector_actor():
    existing = find_actor(ACTOR_LABEL) or find_actor(CONFIG["ACTOR_LABEL"])
    if existing:
        existing.set_editor_property(CONFIG["DOMAIN_PROPERTY"], CONFIG["SELECTED_DOMAIN_TYPE"])
        existing.set_editor_property(CONFIG["VARIANT_PROPERTY"], CONFIG["SELECTED_VARIANT_TYPE"])
        return existing, False

    for actor in list(get_all_level_actors()):
        if actor.get_actor_label() == ACTOR_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    actor_class = unreal.load_class(None, CONFIG["BLUEPRINT_CLASS_PATH"])
    if not actor_class:
        raise RuntimeError(f"Missing material override selector Blueprint class: {CONFIG['BLUEPRINT_CLASS_PATH']}")

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(108000, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(ACTOR_LABEL)
    actor.set_editor_property(CONFIG["DOMAIN_PROPERTY"], CONFIG["SELECTED_DOMAIN_TYPE"])
    actor.set_editor_property(CONFIG["VARIANT_PROPERTY"], CONFIG["SELECTED_VARIANT_TYPE"])
    return actor, True


def matching_ism_rows(ism_rows, expected_row):
    materials = expected_row["materials"]
    return [
        row for row in ism_rows
        if row["mesh"] == expected_row["mesh_path"]
        and row["materials"][:len(materials)] == materials
    ]


def validate_actor(actor, apply_result):
    components = actor.get_components_by_class(unreal.PCGComponent)
    if not components:
        raise RuntimeError(f"Menu apply validation actor has no PCGComponent: {ACTOR_LABEL}")
    component = components[0]
    expected_rows = CONFIG["selected_expected_rows"]()
    expected_total = sum(row["expected_instance_count"] for row in expected_rows)
    point_count = BASE_VERIFY["get_generated_point_count"](component)
    ism_rows = BASE_VERIFY["get_ism_rows"](actor)
    total_ism = sum(max(0, row["count"]) for row in ism_rows)
    row_results = []
    for expected_row in expected_rows:
        rows = matching_ism_rows(ism_rows, expected_row)
        row_results.append({
            "domain_name": expected_row["domain_name"],
            "domain_type": expected_row["domain_type"],
            "variant_name": expected_row["variant_name"],
            "variant_type": expected_row["variant_type"],
            "mesh_key": expected_row["mesh_key"],
            "mesh_path": expected_row["mesh_path"],
            "expected_materials": expected_row["materials"],
            "matching_row_count": len(rows),
            "matching_instance_count": sum(max(0, row["count"]) for row in rows),
            "expected_instance_count": expected_row["expected_instance_count"],
        })

    graph_path = BASE_VERIFY["get_component_graph_path"](component)
    validation_pass = all([
        apply_result.get("graph_mode") == "dynamic_actor_property",
        apply_result.get("graph") == CONFIG["GRAPH_PATH"],
        graph_path == CONFIG["GRAPH_PATH"],
        point_count == expected_total,
        total_ism == expected_total,
        all(result["matching_row_count"] == 1 for result in row_results),
        all(result["matching_instance_count"] == result["expected_instance_count"] for result in row_results),
    ])
    return {
        "actor": actor.get_actor_label(),
        "apply_result": apply_result,
        "graph": graph_path,
        "expected_graph": CONFIG["GRAPH_PATH"],
        "point_count": point_count,
        "expected_points": expected_total,
        "total_ism": total_ism,
        "expected_ism": expected_total,
        "row_results": row_results,
        "ism_rows": ism_rows,
        "validation_pass": validation_pass,
    }


def main():
    print(VERIFY_MARKER)
    ensure_validation_level_loaded()
    menu_module = load_menu_module()
    actor, spawned_fresh = get_or_spawn_selector_actor()
    apply_result = menu_module.apply_material_override_selector(actor, force=True)
    actor_result = validate_actor(actor, apply_result)
    log_path, marker_found, log_errors = BASE_VERIFY["scan_latest_log"](VERIFY_MARKER)
    validation_pass = actor_result["validation_pass"] and not log_errors

    print(f"dynamic_material_axis_menu_apply_actor={actor_result['actor']}")
    print(f"  spawned_fresh={spawned_fresh}")
    print(f"  apply_result={actor_result['apply_result']}")
    print(f"  graph={actor_result['graph']}")
    print(f"  expected_graph={actor_result['expected_graph']}")
    print(f"  point_count={actor_result['point_count']}")
    print(f"  expected_points={actor_result['expected_points']}")
    print(f"  total_ism={actor_result['total_ism']}")
    print(f"  expected_ism={actor_result['expected_ism']}")
    for result in actor_result["row_results"]:
        print(f"  row_result={result}")
    print(f"  ism_rows={actor_result['ism_rows']}")
    print(f"  validation_pass={actor_result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"dynamic_material_axis_menu_apply_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_MENU_APPLY_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED dynamic material axis menu apply verification failed")


if __name__ == "__main__":
    main()
