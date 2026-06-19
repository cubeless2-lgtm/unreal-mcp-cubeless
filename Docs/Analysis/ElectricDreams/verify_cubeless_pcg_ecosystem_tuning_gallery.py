import gc
import pathlib
import sys

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_pcg_ecosystem_tuning_gallery.py",
    )
).parent
FIELD_LAYOUT_SCRIPT = SCRIPT_DIR / "verify_save_cubeless_pcg_ecosystem_field_layout_refine.py"

SOURCE_LEVEL = "/Game/Cubeless/Map/LVL_Cubeless_PCG_Ecosystem_Field"
DISCARD_LEVEL = "/Game/Untitled"
TARGET_LEVEL = "/Game/_MCP_Temp/PCG/LVL_Cubeless_PCG_TuningGallery_MCP"
TARGET_LEVEL_OBJECT = f"{TARGET_LEVEL}.LVL_Cubeless_PCG_TuningGallery_MCP"
VERIFY_MARKER = "MCP_CUBELESS_PCG_ECOSYSTEM_TUNING_GALLERY_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")
SAVE_ON_VERIFY = bool(globals().get("SAVE_ON_VERIFY", True))

ACTOR_SPECS = [
    {
        "label": "Cubeless_PCG_EcosystemRuntime_Tuning_MixedMeadowDefault",
        "xy": (9600.0, 13600.0),
        "preset_type": 1,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_Tuning_DenseGroundFoliage_TreeOff",
        "xy": (12000.0, 13600.0),
        "preset_type": 2,
        "density_override": 0,
        "tree_override": 1,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_Tuning_RockySparse",
        "xy": (14400.0, 13600.0),
        "preset_type": 3,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_Tuning_LightConiferEdge",
        "xy": (9600.0, 11200.0),
        "preset_type": 4,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_Tuning_ClassicGrassFill",
        "xy": (12000.0, 11200.0),
        "preset_type": 5,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_Tuning_MeadowDenseOverride",
        "xy": (14400.0, 11200.0),
        "preset_type": 1,
        "density_override": 3,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_Tuning_GroundFoliageWarm",
        "xy": (9600.0, 8800.0),
        "preset_type": 2,
        "density_override": 0,
        "tree_override": 1,
        "material_mood": 3,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_Tuning_RockyCoolDark",
        "xy": (12000.0, 8800.0),
        "preset_type": 3,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 2,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_Tuning_ConiferLightGrove",
        "xy": (14400.0, 8800.0),
        "preset_type": 4,
        "density_override": 0,
        "tree_override": 4,
        "material_mood": 3,
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


def load_level(level_path):
    release_python_uobject_refs()
    loaded = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(level_path)
    release_python_uobject_refs()
    if not loaded:
        raise RuntimeError(f"Failed to load level: {level_path}")


def recreate_temp_gallery_level():
    if not unreal.EditorAssetLibrary.does_asset_exist(SOURCE_LEVEL):
        raise RuntimeError(f"Missing source field level: {SOURCE_LEVEL}")
    if get_current_level_path() == TARGET_LEVEL:
        # The loaded temp map can be reused and cleaned in-place. Loading away
        # from a map while Python still owns references to it can trip Unreal's
        # editor-world leak guard.
        return
    unreal.EditorAssetLibrary.make_directory("/Game/_MCP_Temp/PCG")
    if unreal.EditorAssetLibrary.does_asset_exist(TARGET_LEVEL):
        load_level(TARGET_LEVEL)
        return
    duplicated = unreal.EditorAssetLibrary.duplicate_asset(SOURCE_LEVEL, TARGET_LEVEL)
    if not duplicated:
        raise RuntimeError(f"Failed to duplicate {SOURCE_LEVEL} to {TARGET_LEVEL}")
    if not unreal.EditorAssetLibrary.save_loaded_asset(duplicated):
        raise RuntimeError(f"Failed to save duplicated temp gallery level: {TARGET_LEVEL_OBJECT}")
    duplicated = None
    release_python_uobject_refs()
    load_level(TARGET_LEVEL)


def ensure_temp_gallery_level_loaded():
    if get_current_level_path() == TARGET_LEVEL:
        return
    if not unreal.EditorAssetLibrary.does_asset_exist(TARGET_LEVEL):
        recreate_temp_gallery_level()
        return
    load_level(TARGET_LEVEL)


def load_field_layout_namespace():
    namespace = {
        "__name__": "_cubeless_pcg_ecosystem_tuning_gallery",
        "__file__": str(FIELD_LAYOUT_SCRIPT),
        "TARGET_LEVEL": TARGET_LEVEL,
        "VERIFY_MARKER": VERIFY_MARKER,
        "VALIDATION_MODE": VALIDATION_MODE,
        "SAVE_ON_VERIFY": SAVE_ON_VERIFY,
        "ACTOR_SPECS": ACTOR_SPECS,
    }
    with FIELD_LAYOUT_SCRIPT.open("r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(FIELD_LAYOUT_SCRIPT), "exec")
    exec(code, namespace)
    namespace["TARGET_LEVEL"] = TARGET_LEVEL
    namespace["VERIFY_MARKER"] = VERIFY_MARKER
    namespace["VALIDATION_MODE"] = VALIDATION_MODE
    namespace["SAVE_ON_VERIFY"] = SAVE_ON_VERIFY
    namespace["ACTOR_SPECS"] = ACTOR_SPECS
    return namespace


def main():
    print(VERIFY_MARKER)
    print(f"tuning_gallery_mode={VALIDATION_MODE}")
    if VALIDATION_MODE == "prepare":
        recreate_temp_gallery_level()
    else:
        ensure_temp_gallery_level_loaded()

    namespace = load_field_layout_namespace()
    namespace["main"]()
    print(f"tuning_gallery_level={TARGET_LEVEL}")
    print(f"tuning_gallery_actor_count={len(ACTOR_SPECS)}")
    print("cubeless_pcg_tuning_gallery_complete=True")


if __name__ == "__main__":
    main()
