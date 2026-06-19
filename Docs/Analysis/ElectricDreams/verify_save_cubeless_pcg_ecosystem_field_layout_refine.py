import gc
import importlib
import math
import pathlib
import sys

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_save_cubeless_pcg_ecosystem_field_layout_refine.py",
    )
).resolve().parent

PROJECT_ROOT = pathlib.Path(
    globals().get(
        "PROJECT_ROOT",
        __import__("os").environ.get(
            "CUBELESS_PROJECT_ROOT",
            SCRIPT_DIR.parents[2].parent / "CubelessStylized",
        ),
    )
).resolve()

TARGET_LEVEL = "/Game/Cubeless/Map/LVL_Cubeless_PCG_Ecosystem_Field"
PROJECT_PLUGIN_PYTHON = (PROJECT_ROOT / "Plugins" / "CustomTools" / "Content" / "Python").as_posix()
RUNTIME_BLUEPRINT_NAME = "BP_Cubeless_PCG_EcosystemRuntime"
RUNTIME_BLUEPRINT_CLASS = (
    "/Game/Cubeless/PCG/Runtime/Blueprints/"
    f"{RUNTIME_BLUEPRINT_NAME}.{RUNTIME_BLUEPRINT_NAME}_C"
)
VERIFY_MARKER = "MCP_CUBELESS_PCG_ECOSYSTEM_FIELD_LAYOUT_REFINE_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")
SAVE_ON_VERIFY = bool(globals().get("SAVE_ON_VERIFY", True))

HEIGHT_TOLERANCE_CM = 180.0
XY_RADIUS_TOLERANCE_CM = 2200.0
TRACE_Z = 200000.0

ACTOR_SPECS = [
    {
        "label": "Cubeless_PCG_EcosystemRuntime_MeadowCenter",
        "xy": (12000.0, 12000.0),
        "preset_type": 1,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_GroundFoliageSouth",
        "xy": (12000.0, 11600.0),
        "preset_type": 2,
        "density_override": 0,
        "tree_override": 1,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_RockyEdgeEast",
        "xy": (12800.0, 12200.0),
        "preset_type": 3,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
]


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


def load_menu_module():
    if PROJECT_PLUGIN_PYTHON not in sys.path:
        sys.path.append(PROJECT_PLUGIN_PYTHON)
    from ArtScripts import CubelessEDPCG

    return importlib.reload(CubelessEDPCG)


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


def ensure_target_level_loaded():
    if get_current_level_path() == TARGET_LEVEL:
        return
    if not unreal.EditorAssetLibrary.does_asset_exist(TARGET_LEVEL):
        raise RuntimeError(f"Missing field level: {TARGET_LEVEL}")
    release_python_uobject_refs()
    loaded = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(TARGET_LEVEL)
    release_python_uobject_refs()
    if not loaded:
        raise RuntimeError(f"Failed to load field level: {TARGET_LEVEL}")


def is_landscape_actor(actor):
    if not actor:
        return False
    class_name = actor.get_class().get_name()
    return class_name == "Landscape" or "LandscapeStreamingProxy" in class_name


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


def set_int_property(actor, prop_name, value):
    actor.set_editor_property(prop_name, int(value))


def set_bool_property(actor, prop_name, value):
    actor.set_editor_property(prop_name, bool(value))


def configure_field_spline(actor):
    splines = actor.get_components_by_class(unreal.SplineComponent)
    if not splines:
        raise RuntimeError(f"Runtime actor has no SplineComponent: {actor.get_actor_label()}")
    # Keep the same proven short line shape from validation; the field becomes
    # a patch by offsetting several runtime actors across the Landscape.
    for spline in splines:
        spline.clear_spline_points(False)
        spline.add_spline_point(unreal.Vector(0, -800.0, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, 0.0, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, 800.0, 0), unreal.SplineCoordinateSpace.LOCAL, True)
        spline.update_spline()


def cleanup_existing_field_actors():
    for actor in list(get_all_level_actors()):
        label = actor.get_actor_label()
        if label.startswith("Cubeless_PCG_EcosystemRuntime_"):
            unreal.EditorLevelLibrary.destroy_actor(actor)
        elif label.startswith("MCP_Cubeless_PCG_TestMapRuntime_"):
            unreal.EditorLevelLibrary.destroy_actor(actor)
        elif label == "PCG_ModularBuilding_Assembler_V2":
            unreal.EditorLevelLibrary.destroy_actor(actor)


def spawn_actor_for_spec(spec, menu_module):
    trace = trace_landscape(*spec["xy"])
    if not trace["hit"]:
        raise RuntimeError(f"Landscape trace failed for {spec['label']}: {spec['xy']} {trace}")
    actor_class = unreal.load_class(None, RUNTIME_BLUEPRINT_CLASS)
    if not actor_class:
        raise RuntimeError(f"Missing runtime Blueprint class: {RUNTIME_BLUEPRINT_CLASS}")
    location = trace["location"]
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(location.x, location.y, location.z),
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    actor.set_actor_label(spec["label"])
    set_int_property(actor, "PresetType", spec["preset_type"])
    set_int_property(actor, "DensityOverride", spec["density_override"])
    set_int_property(actor, "TreeOverride", spec["tree_override"])
    set_int_property(actor, "MaterialMood", spec["material_mood"])
    set_bool_property(actor, "DebugMaterialPreview", spec["debug_material_preview"])
    configure_field_spline(actor)
    apply_result = menu_module.apply_production_candidate_selector(actor, force=True)
    return actor, trace, apply_result


def find_actor(label):
    return next((actor for actor in get_all_level_actors() if actor.get_actor_label() == label), None)


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


def validate_actor_contact(actor):
    total_instances = 0
    trace_miss_count = 0
    height_fail_count = 0
    xy_fail_count = 0
    max_abs_height_delta = 0.0
    max_slope_degrees = 0.0
    mesh_counts = {}
    min_x = min_y = min_z = None
    max_x = max_y = max_z = None
    samples = []
    actor_location = actor.get_actor_location()
    for component in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
        count = int(component.get_instance_count())
        total_instances += max(0, count)
        mesh = component.get_editor_property("static_mesh")
        mesh_path = mesh.get_path_name() if mesh else "None"
        mesh_counts[mesh_path] = mesh_counts.get(mesh_path, 0) + count
        for index in range(count):
            transform = get_instance_transform(component, index)
            if not transform:
                trace_miss_count += 1
                samples.append((component.get_name(), index, "missing_transform"))
                continue
            location = get_world_instance_location(actor, transform.translation)
            min_x = location.x if min_x is None else min(min_x, location.x)
            min_y = location.y if min_y is None else min(min_y, location.y)
            min_z = location.z if min_z is None else min(min_z, location.z)
            max_x = location.x if max_x is None else max(max_x, location.x)
            max_y = location.y if max_y is None else max(max_y, location.y)
            max_z = location.z if max_z is None else max(max_z, location.z)
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
        "actor": actor.get_actor_label(),
        "total_instances": total_instances,
        "trace_miss_count": trace_miss_count,
        "height_fail_count": height_fail_count,
        "xy_fail_count": xy_fail_count,
        "max_abs_height_delta": max_abs_height_delta,
        "max_slope_degrees": max_slope_degrees,
        "mesh_counts": mesh_counts,
        "bounds_min": (min_x, min_y, min_z),
        "bounds_max": (max_x, max_y, max_z),
        "samples": samples,
        "validation_pass": total_instances > 0 and trace_miss_count == 0 and height_fail_count == 0 and xy_fail_count == 0,
    }


def scan_latest_log(marker):
    project_log = PROJECT_ROOT / "Saved" / "Logs" / "StylizedCubeless.log"
    if not project_log.exists():
        return str(project_log), False, ["missing_log"]
    lines = project_log.read_text(encoding="utf-8", errors="ignore").splitlines()
    marker_index = None
    for index in range(len(lines) - 1, -1, -1):
        if marker in lines[index]:
            marker_index = index
            break
    if marker_index is None:
        return str(project_log), False, ["missing_marker"]
    errors = [
        line
        for line in lines[marker_index:]
        if "Error:" in line or "Fatal" in line or "Assertion failed" in line
    ]
    return str(project_log), True, errors


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


def save_target_level():
    dirty_maps = get_dirty_map_package_names()
    unexpected = [name for name in dirty_maps if not name.startswith(TARGET_LEVEL)]
    if unexpected:
        raise RuntimeError(f"Refusing to save with unexpected dirty maps: {dirty_maps}")
    saved = unreal.EditorAssetLibrary.save_asset(TARGET_LEVEL, only_if_is_dirty=True)
    release_python_uobject_refs()
    return saved, dirty_maps, get_dirty_map_package_names()


def main():
    print(VERIFY_MARKER)
    ensure_target_level_loaded()
    menu_module = load_menu_module()
    if VALIDATION_MODE == "prepare":
        cleanup_existing_field_actors()
        results = []
        for spec in ACTOR_SPECS:
            actor, trace, apply_result = spawn_actor_for_spec(spec, menu_module)
            results.append((actor, trace, apply_result))
        print(f"field_level={TARGET_LEVEL}")
        for actor, trace, apply_result in results:
            print(f"prepared_actor={actor.get_actor_label()}")
            print(f"  location={actor.get_actor_location()}")
            print(f"  trace_actor={trace['actor']}")
            print(f"  trace_slope={trace['slope_degrees']}")
            print(f"  apply_result={apply_result}")
        print(f"dirty_map_packages={get_dirty_map_package_names()}")
        print("field_layout_refine_prepared=True")
        print("MCP_CUBELESS_PCG_ECOSYSTEM_FIELD_LAYOUT_REFINE_END")
        release_python_uobject_refs()
        return

    contact_results = []
    missing = []
    for spec in ACTOR_SPECS:
        actor = find_actor(spec["label"])
        if not actor:
            missing.append(spec["label"])
            continue
        contact_results.append(validate_actor_contact(actor))
    log_path, marker_found, log_errors = scan_latest_log(VERIFY_MARKER)
    total_instances = sum(result["total_instances"] for result in contact_results)
    validation_pass = (
        not missing
        and total_instances > 0
        and all(result["validation_pass"] for result in contact_results)
        and marker_found
        and not log_errors
    )
    saved = False
    dirty_before_save = get_dirty_map_package_names()
    dirty_after_save = dirty_before_save
    if validation_pass and SAVE_ON_VERIFY:
        saved, dirty_before_save, dirty_after_save = save_target_level()
    print(f"field_level={TARGET_LEVEL}")
    print(f"missing_actors={missing}")
    print(f"field_total_instances={total_instances}")
    for result in contact_results:
        print(f"actor_result={result}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"dirty_before_save={dirty_before_save}")
    print(f"save_on_verify={SAVE_ON_VERIFY}")
    print(f"field_layout_refine_saved={saved}")
    print(f"dirty_after_save={dirty_after_save}")
    print(f"field_layout_refine_validation_pass={validation_pass}")
    print("MCP_CUBELESS_PCG_ECOSYSTEM_FIELD_LAYOUT_REFINE_END")
    release_python_uobject_refs()
    if not validation_pass:
        raise RuntimeError("Cubeless field layout refinement validation failed")


if __name__ == "__main__":
    main()
