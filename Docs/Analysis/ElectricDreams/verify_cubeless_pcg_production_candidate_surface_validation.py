import gc
import pathlib
import sys

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\verify_cubeless_pcg_production_candidate_surface_validation.py",
    )
).parent
PRODUCTION_VERIFIER_SCRIPT = SCRIPT_DIR / "verify_cubeless_pcg_production_candidate_blueprint.py"
STYLE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_style_profile_matrix_presets.py"
TREE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_tree_profile_presets.py"
MATERIAL_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_material_override_presets.py"

LEVEL = "/Game/_MCP_Temp/PCG/LVL_Cubeless_PCG_ProductionCandidate_Surface_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_PCG_ProductionCandidateSurface"
SURFACE_LABEL = "MCP_Cubeless_PCG_SurfacePlane_Validation"
SURFACE_MESH = "/Engine/BasicShapes/Plane.Plane"
SURFACE_CENTER = unreal.Vector(73600.0, 1800.0, -2.0)
SURFACE_SCALE = unreal.Vector(240.0, 180.0, 1.0)
SURFACE_HALF_X = 12000.0
SURFACE_HALF_Y = 9000.0
SURFACE_Z_MIN = -100.0
SURFACE_Z_MAX = 1000.0
VERIFY_MARKER = "MCP_CUBELESS_PCG_PRODUCTION_CANDIDATE_SURFACE_VERIFY_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")

VALIDATION_SPECS = [
    {
        "name": "Surface_MixedMeadowDefault",
        "preset_type": 1,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "name": "Surface_DenseGroundFoliage",
        "preset_type": 2,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "name": "Surface_RockySparse",
        "preset_type": 3,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "name": "Surface_TreeOff",
        "preset_type": 2,
        "density_override": 0,
        "tree_override": 1,
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
    namespace["VALIDATION_SPECS"] = VALIDATION_SPECS
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


def ensure_surface_level_loaded():
    if get_current_level_path() == LEVEL:
        return
    release_python_uobject_refs()
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if unreal.EditorAssetLibrary.does_asset_exist(LEVEL):
        level_subsystem.load_level(LEVEL)
        release_python_uobject_refs()
        return
    unreal.EditorAssetLibrary.make_directory("/Game/_MCP_Temp/PCG")
    created = level_subsystem.new_level(LEVEL)
    if not created:
        raise RuntimeError(f"Failed to create surface validation level: {LEVEL}")
    release_python_uobject_refs()
    # Keep this unsaved. It is a disposable surface smoke world, and saving PCG
    # temp maps can trigger UE 5.7 shutdown crashes in Python/PCG teardown.


def find_actor_by_label(label):
    return next((actor for actor in get_all_level_actors() if actor.get_actor_label() == label), None)


def destroy_prefixed_actors():
    for actor in list(get_all_level_actors()):
        label = actor.get_actor_label()
        if label.startswith(f"{ACTOR_LABEL_PREFIX}_") or label == SURFACE_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)


def create_surface_plane():
    mesh = unreal.EditorAssetLibrary.load_asset(SURFACE_MESH)
    if not mesh:
        raise RuntimeError(f"Missing surface mesh: {SURFACE_MESH}")
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        unreal.StaticMeshActor,
        SURFACE_CENTER,
        unreal.Rotator(0.0, 0.0, 0.0),
    )
    actor.set_actor_label(SURFACE_LABEL)
    actor.set_actor_scale3d(SURFACE_SCALE)
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    if not component:
        raise RuntimeError("Surface plane has no StaticMeshComponent")
    component.set_static_mesh(mesh)
    return actor


def get_instance_transform(component, index):
    transform = component.get_instance_transform(index, True)
    if isinstance(transform, tuple):
        return transform[0] if transform else None
    return transform


def get_world_instance_location(actor, local_or_world_location):
    actor_location = actor.get_actor_location()
    looks_local = (
        abs(local_or_world_location.x - SURFACE_CENTER.x) > SURFACE_HALF_X
        and abs(local_or_world_location.x) <= SURFACE_HALF_X
    )
    if not looks_local:
        return local_or_world_location
    return unreal.Vector(
        actor_location.x + local_or_world_location.x,
        actor_location.y + local_or_world_location.y,
        actor_location.z + local_or_world_location.z,
    )


def validate_surface_instances(actors):
    total_instances = 0
    out_of_bounds = []
    z_out_of_range = []
    min_z = None
    max_z = None
    min_x = None
    max_x = None
    min_y = None
    max_y = None
    for actor in actors:
        for component in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
            count = int(component.get_instance_count())
            total_instances += max(0, count)
            for index in range(count):
                transform = get_instance_transform(component, index)
                if not transform:
                    out_of_bounds.append((actor.get_actor_label(), component.get_name(), index, "missing_transform"))
                    continue
                location = get_world_instance_location(actor, transform.translation)
                min_x = location.x if min_x is None else min(min_x, location.x)
                max_x = location.x if max_x is None else max(max_x, location.x)
                min_y = location.y if min_y is None else min(min_y, location.y)
                max_y = location.y if max_y is None else max(max_y, location.y)
                min_z = location.z if min_z is None else min(min_z, location.z)
                max_z = location.z if max_z is None else max(max_z, location.z)
                in_x = abs(location.x - SURFACE_CENTER.x) <= SURFACE_HALF_X
                in_y = abs(location.y - SURFACE_CENTER.y) <= SURFACE_HALF_Y
                in_z = SURFACE_Z_MIN <= location.z <= SURFACE_Z_MAX
                if not (in_x and in_y):
                    out_of_bounds.append((actor.get_actor_label(), component.get_name(), index, location))
                if not in_z:
                    z_out_of_range.append((actor.get_actor_label(), component.get_name(), index, location.z))
    return {
        "surface_mode": "StaticMeshPlane",
        "landscape_direct_validation": False,
        "total_instances": total_instances,
        "bounds_min_x": min_x,
        "bounds_max_x": max_x,
        "bounds_min_y": min_y,
        "bounds_max_y": max_y,
        "bounds_min_z": min_z,
        "bounds_max_z": max_z,
        "out_of_bounds_count": len(out_of_bounds),
        "z_out_of_range_count": len(z_out_of_range),
        "out_of_bounds_samples": out_of_bounds[:8],
        "z_out_of_range_samples": z_out_of_range[:8],
        "validation_pass": total_instances > 0 and not out_of_bounds and not z_out_of_range,
    }


def print_dict(prefix, data):
    for key, value in data.items():
        print(f"{prefix}{key}={value}")


def main():
    print(VERIFY_MARKER)
    ensure_surface_level_loaded()
    verifier = load_production_verifier()
    style_config = verifier["load_config"](STYLE_BUILDER_SCRIPT, "_surface_style_config")
    tree_config = verifier["load_config"](TREE_BUILDER_SCRIPT, "_surface_tree_config")
    material_config = verifier["load_config"](MATERIAL_BUILDER_SCRIPT, "_surface_material_config")
    menu_module = verifier["load_menu_module"]()

    if VALIDATION_MODE == "prepare":
        destroy_prefixed_actors()
        surface_actor = create_surface_plane()
        actors = []
        for index, spec in enumerate(VALIDATION_SPECS):
            actor, apply_result = verifier["spawn_candidate_actor"](spec, index, menu_module)
            actors.append(actor)
            print(f"prepared_actor={actor.get_actor_label()}")
            print(f"  apply_result={apply_result}")
        print(f"surface_actor={surface_actor.get_actor_label()}")
        print(f"surface_mesh={SURFACE_MESH}")
        print(f"surface_validation_level={LEVEL}")
        print("production_candidate_surface_validation_prepared=True")
        print("MCP_CUBELESS_PCG_PRODUCTION_CANDIDATE_SURFACE_VERIFY_END")
        return

    surface_actor = find_actor_by_label(SURFACE_LABEL)
    if not surface_actor:
        raise RuntimeError(
            "Missing surface validation plane. "
            "Run prepare_cubeless_pcg_production_candidate_surface_validation.py first."
        )
    results = [
        verifier["validate_candidate"](spec, style_config, tree_config, material_config, menu_module)
        for spec in VALIDATION_SPECS
    ]
    actors = [find_actor_by_label(verifier["selector_label"](spec)) for spec in VALIDATION_SPECS]
    missing_actors = [spec["name"] for spec, actor in zip(VALIDATION_SPECS, actors) if not actor]
    actors = [actor for actor in actors if actor]
    surface_result = validate_surface_instances(actors)
    log_path, marker_found, log_errors = verifier["scan_latest_log"](VERIFY_MARKER)
    validation_pass = (
        all(result["validation_pass"] for result in results)
        and not missing_actors
        and surface_result["validation_pass"]
        and not log_errors
    )

    print(f"surface_validation_level={LEVEL}")
    print(f"surface_actor={surface_actor.get_actor_label()}")
    print(f"surface_mesh={SURFACE_MESH}")
    print(f"missing_actor_count={len(missing_actors)}")
    for name in missing_actors:
        print(f"missing_actor={name}")
    for result in results:
        print(f"candidate={result['candidate']}")
        print(f"  validation_pass={result['validation_pass']}")
        print(f"  style_points={result['style_points']}")
        print(f"  tree_points={result['tree_points']}")
        print(f"  material_points={result['material_points']}")
        print(f"  style_ism={result['style_ism']}")
        print(f"  tree_ism={result['tree_ism']}")
        print(f"  material_ism={result['material_ism']}")
    print_dict("surface_", surface_result)
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"production_candidate_surface_validation_pass={validation_pass}")
    print("MCP_CUBELESS_PCG_PRODUCTION_CANDIDATE_SURFACE_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless PCG production candidate surface validation failed")


if __name__ == "__main__":
    main()
