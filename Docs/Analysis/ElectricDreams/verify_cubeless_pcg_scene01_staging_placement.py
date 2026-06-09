import gc
import pathlib
import sys

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\verify_cubeless_pcg_scene01_staging_placement.py",
    )
).parent
PRODUCTION_VERIFIER_SCRIPT = SCRIPT_DIR / "verify_cubeless_pcg_production_candidate_blueprint.py"
STYLE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_style_profile_matrix_presets.py"
TREE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_tree_profile_presets.py"
MATERIAL_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_material_override_presets.py"

LEVEL = "/Game/Cubeless/Map/Scene01"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_PCG_Scene01Candidate"
LEGACY_ACTOR_LABEL = "MCP_Cubeless_PCG_Scene01Candidate_MixedMeadowDefault_Staging"
VERIFY_MARKER = "MCP_CUBELESS_PCG_SCENE01_STAGING_VERIFY_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")

STAGING_SPEC = {
    "name": "Scene01_MixedMeadowDefault_Staging",
    "preset_type": 1,
    "density_override": 0,
    "tree_override": 0,
    "material_mood": 0,
    "debug_material_preview": False,
}
ACTOR_LABEL = f"{ACTOR_LABEL_PREFIX}_{STAGING_SPEC['name']}_Validation"
STAGING_LOCATION = unreal.Vector(0.0, 0.0, 4.0)


def release_python_uobject_refs():
    for attr_name in ("last_type", "last_value", "last_traceback"):
        try:
            if hasattr(sys, attr_name):
                setattr(sys, attr_name, None)
        except Exception:
            pass
    gc.collect()
    collect_garbage = getattr(getattr(unreal, "SystemLibrary", None), "collect_garbage", None)
    if collect_garbage:
        try:
            collect_garbage()
        except Exception:
            pass


def load_namespace(script_path, namespace_name):
    namespace = {"__name__": namespace_name, "__file__": str(script_path)}
    with open(script_path, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(script_path), "exec")
    exec(code, namespace)
    return namespace


def load_production_verifier():
    namespace = load_namespace(PRODUCTION_VERIFIER_SCRIPT, "_cubeless_pcg_production_candidate_verifier")
    namespace["LEVEL"] = LEVEL
    namespace["ACTOR_LABEL_PREFIX"] = ACTOR_LABEL_PREFIX
    namespace["VALIDATION_SPECS"] = [STAGING_SPEC]
    return namespace


def get_editor_world():
    subsystem_cls = getattr(unreal, "UnrealEditorSubsystem", None)
    if subsystem_cls:
        subsystem = unreal.get_editor_subsystem(subsystem_cls)
        if subsystem:
            world = subsystem.get_editor_world()
            if world:
                return world
    return unreal.EditorLevelLibrary.get_editor_world()


def get_current_level_path():
    world = get_editor_world()
    if world:
        return world.get_path_name().split(".", 1)[0]
    return None


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def ensure_scene01_loaded():
    if get_current_level_path() == LEVEL:
        return
    if not unreal.EditorAssetLibrary.does_asset_exist(LEVEL):
        raise RuntimeError(f"Missing Scene01 level: {LEVEL}")
    release_python_uobject_refs()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    release_python_uobject_refs()


def find_actor_by_label(label):
    return next((actor for actor in get_all_level_actors() if actor.get_actor_label() == label), None)


def destroy_existing_staging_actor():
    for label in (ACTOR_LABEL, LEGACY_ACTOR_LABEL):
        actor = find_actor_by_label(label)
        if actor:
            unreal.EditorLevelLibrary.destroy_actor(actor)


def cleanup_legacy_staging_actors():
    for actor in list(get_all_level_actors()):
        label = actor.get_actor_label()
        if label.startswith(f"{ACTOR_LABEL_PREFIX}_") and label != ACTOR_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)


def spawn_staging_actor(menu_module, verifier):
    destroy_existing_staging_actor()
    cleanup_legacy_staging_actors()
    actor_class = unreal.load_class(None, verifier["BLUEPRINT_CLASS_PATH"])
    if not actor_class:
        raise RuntimeError(f"Missing production candidate Blueprint class: {verifier['BLUEPRINT_CLASS_PATH']}")
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        STAGING_LOCATION,
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    actor.set_actor_label(ACTOR_LABEL)
    verifier["set_int_property"](actor, "PresetType", STAGING_SPEC["preset_type"])
    verifier["set_int_property"](actor, "DensityOverride", STAGING_SPEC["density_override"])
    verifier["set_int_property"](actor, "TreeOverride", STAGING_SPEC["tree_override"])
    verifier["set_int_property"](actor, "MaterialMood", STAGING_SPEC["material_mood"])
    verifier["set_bool_property"](actor, "DebugMaterialPreview", STAGING_SPEC["debug_material_preview"])
    verifier["configure_validation_spline"](actor)
    apply_result = menu_module.apply_production_candidate_selector(actor, force=True)
    return actor, apply_result


def get_dirty_package_names():
    result = []
    utils = getattr(unreal, "EditorLoadingAndSavingUtils", None)
    if not utils or not hasattr(utils, "get_dirty_map_packages"):
        return result
    packages = []
    try:
        packages = list(utils.get_dirty_map_packages())
        for package in packages:
            try:
                result.append(package.get_name())
            except Exception:
                result.append(str(package))
    finally:
        try:
            del packages
        except Exception:
            pass
    return sorted(result)


def count_generated_instances(actor):
    counts = {}
    total = 0
    for component in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
        count = int(component.get_instance_count())
        counts[component.get_name()] = count
        total += count
    return total, counts


def main():
    print(VERIFY_MARKER)
    ensure_scene01_loaded()
    verifier = load_production_verifier()
    style_config = verifier["load_config"](STYLE_BUILDER_SCRIPT, "_scene01_style_config")
    tree_config = verifier["load_config"](TREE_BUILDER_SCRIPT, "_scene01_tree_config")
    material_config = verifier["load_config"](MATERIAL_BUILDER_SCRIPT, "_scene01_material_config")
    menu_module = verifier["load_menu_module"]()

    if VALIDATION_MODE == "prepare":
        actor, apply_result = spawn_staging_actor(menu_module, verifier)
        print(f"scene01_staging_level={LEVEL}")
        print(f"scene01_staging_actor={actor.get_actor_label()}")
        print(f"scene01_staging_location={actor.get_actor_location()}")
        print(f"scene01_apply_result={apply_result}")
        print("scene01_staging_prepared=True")
        print("MCP_CUBELESS_PCG_SCENE01_STAGING_VERIFY_END")
        release_python_uobject_refs()
        return

    actor = find_actor_by_label(ACTOR_LABEL)
    if not actor:
        raise RuntimeError(f"Missing Scene01 staging actor: {ACTOR_LABEL}")

    route_result = verifier["validate_candidate"](STAGING_SPEC, style_config, tree_config, material_config, menu_module)
    total_instances, instance_counts = count_generated_instances(actor)
    log_path, marker_found, log_errors = verifier["scan_latest_log"](VERIFY_MARKER)
    dirty_maps = get_dirty_package_names()
    validation_pass = (
        bool(route_result["validation_pass"])
        and total_instances > 0
        and marker_found
        and not log_errors
    )

    print(f"scene01_staging_level={LEVEL}")
    print(f"scene01_staging_actor={actor.get_actor_label()}")
    print(f"scene01_route_validation_pass={route_result['validation_pass']}")
    print(f"scene01_style_points={route_result['style_points']}")
    print(f"scene01_tree_points={route_result['tree_points']}")
    print(f"scene01_material_points={route_result['material_points']}")
    print(f"scene01_total_instances={total_instances}")
    print(f"scene01_instance_counts={instance_counts}")
    print(f"scene01_dirty_map_packages={dirty_maps}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"scene01_staging_validation_pass={validation_pass}")
    print("MCP_CUBELESS_PCG_SCENE01_STAGING_VERIFY_END")
    release_python_uobject_refs()
    if not validation_pass:
        raise RuntimeError("Scene01 production candidate staging validation failed")


if __name__ == "__main__":
    main()
