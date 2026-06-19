import gc
import json
import pathlib
import sys

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "audit_cubeless_pcg_production_promotion_targets.py",
    )
).parent

TARGET_ROOTS = [
    "/Game/PCG",
    "/Game/PCG/RuntimeGrass",
    "/Game/PCG/NewPCGGraph",
    "/Game/Cubeless/PCG/ProductionCandidates",
    "/Game/Cubeless/PCG/ElectricDreamsLearning",
]

CANDIDATE_BLUEPRINT = (
    "/Game/Cubeless/PCG/ProductionCandidates/Blueprints/"
    "BP_Cubeless_PCG_EcosystemCandidate.BP_Cubeless_PCG_EcosystemCandidate"
)


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


def get_asset_class_name(asset_path):
    try:
        asset_data = unreal.EditorAssetLibrary.find_asset_data(asset_path)
        asset_class_path = getattr(asset_data, "asset_class_path", None)
        if asset_class_path:
            asset_name = getattr(asset_class_path, "asset_name", None)
            if asset_name:
                return str(asset_name)
        asset_class = getattr(asset_data, "asset_class", None)
        if asset_class:
            return str(asset_class)
    except Exception:
        return "Unknown"
    return "Unknown"


def summarize_root(root):
    entry = {
        "directory_exists": False,
        "asset_count": 0,
        "class_counts": {},
        "sample_assets": [],
    }
    try:
        entry["directory_exists"] = bool(unreal.EditorAssetLibrary.does_directory_exist(root))
    except Exception as exc:
        entry["directory_error"] = str(exc)
    if not entry["directory_exists"]:
        return entry

    assets = []
    try:
        assets = list(unreal.EditorAssetLibrary.list_assets(root, recursive=True, include_folder=False))
        entry["asset_count"] = len(assets)
        for asset_path in assets:
            class_name = get_asset_class_name(asset_path)
            entry["class_counts"][class_name] = entry["class_counts"].get(class_name, 0) + 1
            if len(entry["sample_assets"]) < 12:
                entry["sample_assets"].append({"path": str(asset_path), "class": class_name})
    except Exception as exc:
        entry["list_error"] = str(exc)
    finally:
        try:
            del assets
        except Exception:
            pass
    return entry


def main():
    print("MCP_CUBELESS_PCG_PRODUCTION_PROMOTION_AUDIT_BEGIN")
    results = {root: summarize_root(root) for root in TARGET_ROOTS}
    candidate_exists = bool(unreal.EditorAssetLibrary.does_asset_exist(CANDIDATE_BLUEPRINT))
    runtime_roots_exist = any(
        results[root]["directory_exists"]
        for root in ("/Game/PCG/RuntimeGrass", "/Game/PCG/NewPCGGraph")
    )
    learning_root_ready = results["/Game/Cubeless/PCG/ElectricDreamsLearning"]["asset_count"] > 0
    promotion_ready_for_approval = bool(candidate_exists and learning_root_ready)

    print(f"candidate_blueprint={CANDIDATE_BLUEPRINT}")
    print(f"candidate_exists={candidate_exists}")
    print(f"runtime_roots_exist={runtime_roots_exist}")
    print(f"learning_root_ready={learning_root_ready}")
    print(f"promotion_ready_for_approval={promotion_ready_for_approval}")
    print(f"approval_required_before_asset_changes={promotion_ready_for_approval}")
    print("promotion_target_audit_json=" + json.dumps(results, ensure_ascii=False, sort_keys=True))
    print("MCP_CUBELESS_PCG_PRODUCTION_PROMOTION_AUDIT_END")
    release_python_uobject_refs()


if __name__ == "__main__":
    main()
