import gc
import math
import pathlib
import sys

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\verify_cubeless_pcg_testmap_runtime_staging.py",
    )
).parent
PRODUCTION_VERIFIER_SCRIPT = SCRIPT_DIR / "verify_cubeless_pcg_production_candidate_blueprint.py"
STYLE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_style_profile_matrix_presets.py"
TREE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_tree_profile_presets.py"
MATERIAL_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_material_override_presets.py"

LEVEL = "/Game/Cubeless/TestMap"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_PCG_TestMapRuntime"
VERIFY_MARKER = "MCP_CUBELESS_PCG_TESTMAP_RUNTIME_STAGING_VERIFY_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")

RUNTIME_BLUEPRINT_NAME = "BP_Cubeless_PCG_EcosystemRuntime"
RUNTIME_BLUEPRINT_OBJECT = (
    "/Game/Cubeless/PCG/Runtime/Blueprints/"
    f"{RUNTIME_BLUEPRINT_NAME}.{RUNTIME_BLUEPRINT_NAME}"
)
RUNTIME_BLUEPRINT_CLASS = f"{RUNTIME_BLUEPRINT_OBJECT}_C"

HEIGHT_TOLERANCE_CM = 180.0
XY_RADIUS_TOLERANCE_CM = 2200.0
TRACE_Z = 200000.0
STAGING_CENTER_XY = (12000.0, 12000.0)

STAGING_SPEC = {
    "name": "TestMap_MixedMeadowDefault_Staging",
    "preset_type": 1,
    "density_override": 0,
    "tree_override": 0,
    "material_mood": 0,
    "debug_material_preview": False,
}
ACTOR_LABEL = f"{ACTOR_LABEL_PREFIX}_{STAGING_SPEC['name']}_Validation"


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


def load_runtime_verifier():
    namespace = load_namespace(PRODUCTION_VERIFIER_SCRIPT, "_cubeless_pcg_production_candidate_verifier")
    namespace["BLUEPRINT_PATH"] = RUNTIME_BLUEPRINT_OBJECT
    namespace["BLUEPRINT_CLASS_PATH"] = RUNTIME_BLUEPRINT_CLASS
    namespace["LEVEL"] = LEVEL
    namespace["ACTOR_LABEL_PREFIX"] = ACTOR_LABEL_PREFIX
    namespace["VALIDATION_SPECS"] = [STAGING_SPEC]
    namespace["VERIFY_MARKER"] = VERIFY_MARKER
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


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return list(actor_subsystem.get_all_level_actors())
    return list(unreal.EditorLevelLibrary.get_all_level_actors())


def get_current_level_path():
    world = get_editor_world()
    if world:
        return world.get_path_name().split(".", 1)[0]
    return None


def ensure_testmap_loaded():
    if get_current_level_path() == LEVEL:
        return
    if not unreal.EditorAssetLibrary.does_asset_exist(LEVEL):
        raise RuntimeError(f"Missing TestMap level: {LEVEL}")
    release_python_uobject_refs()
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    release_python_uobject_refs()


def is_landscape_actor(actor):
    if not actor:
        return False
    class_name = actor.get_class().get_name()
    return class_name == "Landscape" or "LandscapeStreamingProxy" in class_name


def find_landscape_actors():
    return [actor for actor in get_all_level_actors() if is_landscape_actor(actor)]


def trace_landscape(x, y):
    hit = unreal.SystemLibrary.line_trace_single(
        get_editor_world(),
        unreal.Vector(float(x), float(y), TRACE_Z),
        unreal.Vector(float(x), float(y), -TRACE_Z),
        unreal.TraceTypeQuery.TRACE_TYPE_QUERY1,
        False,
        [],
        unreal.DrawDebugTrace.NONE,
        True,
    )
    if hit is None:
        return {"hit": False, "actor": "None", "location": None, "slope_degrees": None}
    data = hit.to_tuple()
    blocking = bool(data[0]) if len(data) > 0 else False
    actor = data[9] if blocking and len(data) > 9 else None
    if not blocking or not is_landscape_actor(actor):
        return {
            "hit": False,
            "actor": actor.get_actor_label() if actor else "None",
            "location": None,
            "slope_degrees": None,
        }
    location = data[4]
    normal = data[6]
    slope_degrees = math.degrees(math.acos(max(-1.0, min(1.0, float(normal.z)))))
    return {
        "hit": True,
        "actor": actor.get_actor_label(),
        "location": location,
        "slope_degrees": slope_degrees,
    }


def find_actor_by_label(label):
    return next((actor for actor in get_all_level_actors() if actor.get_actor_label() == label), None)


def cleanup_existing_staging_actors():
    for actor in list(get_all_level_actors()):
        if actor.get_actor_label().startswith(f"{ACTOR_LABEL_PREFIX}_"):
            unreal.EditorLevelLibrary.destroy_actor(actor)


def spawn_staging_actor(menu_module, verifier):
    cleanup_existing_staging_actors()
    trace = trace_landscape(*STAGING_CENTER_XY)
    if not trace["hit"]:
        raise RuntimeError(f"TestMap staging Landscape trace failed at {STAGING_CENTER_XY}: {trace}")

    actor_class = unreal.load_class(None, RUNTIME_BLUEPRINT_CLASS)
    if not actor_class:
        raise RuntimeError(f"Missing runtime Blueprint class: {RUNTIME_BLUEPRINT_CLASS}")

    location = trace["location"]
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(location.x, location.y, location.z),
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
    return actor, apply_result, trace


def get_instance_transform(component, index):
    transform = component.get_instance_transform(index, True)
    if isinstance(transform, tuple):
        return transform[0] if transform else None
    return transform


def get_world_instance_location(actor, local_or_world_location):
    actor_location = actor.get_actor_location()
    world_xy_delta = max(
        abs(local_or_world_location.x - actor_location.x),
        abs(local_or_world_location.y - actor_location.y),
    )
    local_xy_delta = max(abs(local_or_world_location.x), abs(local_or_world_location.y))
    if world_xy_delta <= XY_RADIUS_TOLERANCE_CM:
        return local_or_world_location
    if local_xy_delta > XY_RADIUS_TOLERANCE_CM:
        return local_or_world_location
    return unreal.Vector(
        actor_location.x + local_or_world_location.x,
        actor_location.y + local_or_world_location.y,
        actor_location.z + local_or_world_location.z,
    )


def validate_landscape_contact(actor):
    total_instances = 0
    trace_miss_count = 0
    height_fail_count = 0
    xy_fail_count = 0
    max_abs_height_delta = 0.0
    max_slope_degrees = 0.0
    min_instance_z = None
    max_instance_z = None
    samples = []

    actor_location = actor.get_actor_location()
    for component in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
        count = int(component.get_instance_count())
        total_instances += max(0, count)
        for index in range(count):
            transform = get_instance_transform(component, index)
            if not transform:
                trace_miss_count += 1
                samples.append((component.get_name(), index, "missing_transform"))
                continue
            location = get_world_instance_location(actor, transform.translation)
            min_instance_z = location.z if min_instance_z is None else min(min_instance_z, location.z)
            max_instance_z = location.z if max_instance_z is None else max(max_instance_z, location.z)
            trace = trace_landscape(location.x, location.y)
            if not trace["hit"]:
                trace_miss_count += 1
                if len(samples) < 8:
                    samples.append((component.get_name(), index, "trace_miss", location))
                continue
            delta = float(location.z - trace["location"].z)
            abs_delta = abs(delta)
            max_abs_height_delta = max(max_abs_height_delta, abs_delta)
            max_slope_degrees = max(max_slope_degrees, float(trace["slope_degrees"]))
            if abs_delta > HEIGHT_TOLERANCE_CM:
                height_fail_count += 1
                if len(samples) < 8:
                    samples.append((component.get_name(), index, "height_delta", delta, location, trace["location"]))
            if (
                abs(location.x - actor_location.x) > XY_RADIUS_TOLERANCE_CM
                or abs(location.y - actor_location.y) > XY_RADIUS_TOLERANCE_CM
            ):
                xy_fail_count += 1
                if len(samples) < 8:
                    samples.append((component.get_name(), index, "xy_delta", location, actor_location))

    return {
        "total_instances": total_instances,
        "trace_miss_count": trace_miss_count,
        "height_fail_count": height_fail_count,
        "xy_fail_count": xy_fail_count,
        "max_abs_height_delta": max_abs_height_delta,
        "max_slope_degrees": max_slope_degrees,
        "min_instance_z": min_instance_z,
        "max_instance_z": max_instance_z,
        "samples": samples,
        "validation_pass": total_instances > 0 and trace_miss_count == 0 and height_fail_count == 0 and xy_fail_count == 0,
    }


def get_dirty_map_package_names():
    utils = getattr(unreal, "EditorLoadingAndSavingUtils", None)
    if not utils or not hasattr(utils, "get_dirty_map_packages"):
        return []
    result = []
    for package in utils.get_dirty_map_packages():
        try:
            result.append(package.get_name())
        except Exception:
            result.append(str(package))
    return sorted(result)


def main():
    print(VERIFY_MARKER)
    ensure_testmap_loaded()
    landscapes = find_landscape_actors()
    if not landscapes:
        raise RuntimeError(f"No Landscape actors found in {LEVEL}")

    verifier = load_runtime_verifier()
    style_config = verifier["load_config"](STYLE_BUILDER_SCRIPT, "_testmap_style_config")
    tree_config = verifier["load_config"](TREE_BUILDER_SCRIPT, "_testmap_tree_config")
    material_config = verifier["load_config"](MATERIAL_BUILDER_SCRIPT, "_testmap_material_config")
    menu_module = verifier["load_menu_module"]()

    if VALIDATION_MODE == "prepare":
        actor, apply_result, trace = spawn_staging_actor(menu_module, verifier)
        print(f"testmap_staging_level={LEVEL}")
        print(f"testmap_landscape_actor_count={len(landscapes)}")
        print(f"testmap_staging_actor={actor.get_actor_label()}")
        print(f"testmap_staging_location={actor.get_actor_location()}")
        print(f"testmap_staging_trace_actor={trace['actor']}")
        print(f"testmap_staging_trace_slope={trace['slope_degrees']}")
        print(f"testmap_apply_result={apply_result}")
        print("testmap_runtime_staging_prepared=True")
        print("MCP_CUBELESS_PCG_TESTMAP_RUNTIME_STAGING_VERIFY_END")
        release_python_uobject_refs()
        return

    actor = find_actor_by_label(ACTOR_LABEL)
    if not actor:
        raise RuntimeError(f"Missing TestMap runtime staging actor: {ACTOR_LABEL}")

    route_result = verifier["validate_candidate"](STAGING_SPEC, style_config, tree_config, material_config, menu_module)
    contact_result = validate_landscape_contact(actor)
    log_path, marker_found, log_errors = verifier["scan_latest_log"](VERIFY_MARKER)
    dirty_maps = get_dirty_map_package_names()
    validation_pass = (
        bool(route_result["validation_pass"])
        and bool(contact_result["validation_pass"])
        and marker_found
        and not log_errors
    )

    print(f"testmap_staging_level={LEVEL}")
    print(f"testmap_staging_actor={actor.get_actor_label()}")
    print(f"testmap_route_validation_pass={route_result['validation_pass']}")
    print(f"testmap_style_points={route_result['style_points']}")
    print(f"testmap_tree_points={route_result['tree_points']}")
    print(f"testmap_material_points={route_result['material_points']}")
    for key, value in contact_result.items():
        print(f"testmap_landscape_{key}={value}")
    print(f"testmap_dirty_map_packages={dirty_maps}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"testmap_runtime_staging_validation_pass={validation_pass}")
    print("MCP_CUBELESS_PCG_TESTMAP_RUNTIME_STAGING_VERIFY_END")
    release_python_uobject_refs()
    if not validation_pass:
        raise RuntimeError("TestMap runtime staging validation failed")


if __name__ == "__main__":
    main()
