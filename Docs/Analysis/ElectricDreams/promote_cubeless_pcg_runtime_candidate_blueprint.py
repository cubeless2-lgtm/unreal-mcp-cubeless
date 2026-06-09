import gc
import sys

import unreal


SOURCE_BLUEPRINT_NAME = "BP_Cubeless_PCG_EcosystemCandidate"
SOURCE_BLUEPRINT_PACKAGE = (
    "/Game/Cubeless/PCG/ProductionCandidates/Blueprints/"
    f"{SOURCE_BLUEPRINT_NAME}"
)
SOURCE_BLUEPRINT_OBJECT = f"{SOURCE_BLUEPRINT_PACKAGE}.{SOURCE_BLUEPRINT_NAME}"

RUNTIME_PACKAGE_PATH = "/Game/Cubeless/PCG/Runtime/Blueprints"
RUNTIME_BLUEPRINT_NAME = "BP_Cubeless_PCG_EcosystemRuntime"
RUNTIME_BLUEPRINT_PACKAGE = f"{RUNTIME_PACKAGE_PATH}/{RUNTIME_BLUEPRINT_NAME}"
RUNTIME_BLUEPRINT_OBJECT = f"{RUNTIME_BLUEPRINT_PACKAGE}.{RUNTIME_BLUEPRINT_NAME}"
RUNTIME_BLUEPRINT_CLASS = f"{RUNTIME_BLUEPRINT_OBJECT}_C"


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


def validate_paths():
    if not SOURCE_BLUEPRINT_PACKAGE.startswith("/Game/Cubeless/PCG/ProductionCandidates/Blueprints/"):
        raise RuntimeError(f"Unexpected source Blueprint path: {SOURCE_BLUEPRINT_PACKAGE}")
    if not RUNTIME_BLUEPRINT_PACKAGE.startswith("/Game/Cubeless/PCG/Runtime/Blueprints/"):
        raise RuntimeError(f"Unexpected runtime Blueprint path: {RUNTIME_BLUEPRINT_PACKAGE}")


def compile_and_save_blueprint(blueprint):
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    if not unreal.EditorAssetLibrary.save_loaded_asset(blueprint):
        raise RuntimeError(f"Failed to save runtime Blueprint: {RUNTIME_BLUEPRINT_OBJECT}")


def main():
    print("MCP_CUBELESS_PCG_RUNTIME_CANDIDATE_PROMOTE_BEGIN")
    validate_paths()

    if not unreal.EditorAssetLibrary.does_asset_exist(SOURCE_BLUEPRINT_PACKAGE):
        raise RuntimeError(f"Missing source production candidate Blueprint: {SOURCE_BLUEPRINT_OBJECT}")

    unreal.EditorAssetLibrary.make_directory(RUNTIME_PACKAGE_PATH)

    created = False
    if unreal.EditorAssetLibrary.does_asset_exist(RUNTIME_BLUEPRINT_PACKAGE):
        runtime_blueprint = unreal.EditorAssetLibrary.load_asset(RUNTIME_BLUEPRINT_OBJECT)
        if not runtime_blueprint:
            raise RuntimeError(f"Runtime Blueprint exists but could not be loaded: {RUNTIME_BLUEPRINT_OBJECT}")
    else:
        runtime_blueprint = unreal.EditorAssetLibrary.duplicate_asset(
            SOURCE_BLUEPRINT_PACKAGE,
            RUNTIME_BLUEPRINT_PACKAGE,
        )
        created = True
        if not runtime_blueprint:
            raise RuntimeError(
                f"Failed to duplicate {SOURCE_BLUEPRINT_OBJECT} to {RUNTIME_BLUEPRINT_OBJECT}"
            )

    compile_and_save_blueprint(runtime_blueprint)
    runtime_class = unreal.load_class(None, RUNTIME_BLUEPRINT_CLASS)
    if not runtime_class:
        raise RuntimeError(f"Runtime Blueprint class did not load after compile: {RUNTIME_BLUEPRINT_CLASS}")

    print(f"runtime_candidate_created={created}")
    print(f"runtime_candidate_blueprint={RUNTIME_BLUEPRINT_OBJECT}")
    print(f"runtime_candidate_class={RUNTIME_BLUEPRINT_CLASS}")
    print("runtime_candidate_compile_saved=True")
    print("MCP_CUBELESS_PCG_RUNTIME_CANDIDATE_PROMOTE_END")
    release_python_uobject_refs()


if __name__ == "__main__":
    main()
