import json
import pathlib


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "audit_cubeless_pcg_level_targets.py",
    )
).parent
PROJECT_ROOT = pathlib.Path(
    globals().get(
        "PROJECT_ROOT",
        __import__("os").environ.get(
            "CUBELESS_PROJECT_ROOT",
            SCRIPT_DIR.parents[2].parent / "CubelessStylized",
        ),
    )
)
CONTENT_ROOT = PROJECT_ROOT / "Content"

EXCLUDED_PARTS = {
    "_MCP_Temp",
    "_MCP_Sample",
    "__ExternalActors__",
    "__ExternalObjects__",
    "Saved",
    "Intermediate",
}


def to_package_path(umap_path):
    relative = umap_path.relative_to(CONTENT_ROOT).with_suffix("")
    return "/Game/" + "/".join(relative.parts)


def classify_map(package_path):
    if package_path.startswith("/Game/_MCP_Temp/"):
        return "temp_validation"
    if package_path.startswith("/Game/_MCP_Sample/"):
        return "sample_reference"
    if package_path.startswith("/Game/Cubeless/"):
        return "cubeless_project"
    if package_path.startswith("/Game/DreamscapeSeries/"):
        return "third_party_demo_or_reference"
    if package_path.startswith("/Game/EL/"):
        return "electric_or_environment_library"
    return "project_or_plugin"


def main():
    print("MCP_CUBELESS_PCG_LEVEL_TARGET_AUDIT_BEGIN")
    maps = []
    for umap_path in sorted(CONTENT_ROOT.rglob("*.umap")):
        if any(part in EXCLUDED_PARTS for part in umap_path.parts):
            continue
        package_path = to_package_path(umap_path)
        maps.append(
            {
                "package_path": package_path,
                "class": classify_map(package_path),
                "file": str(umap_path),
            }
        )

    recommended = [
        item
        for item in maps
        if item["class"] == "cubeless_project"
        and "/Generated/" not in item["package_path"]
        and "/Sky/" not in item["package_path"]
    ]

    print(f"content_root={CONTENT_ROOT}")
    print(f"map_count={len(maps)}")
    print(f"recommended_cubeless_target_count={len(recommended)}")
    print("recommended_cubeless_targets=")
    for item in recommended:
        print(f"  {item['package_path']}")
    print("level_target_audit_json=" + json.dumps({"maps": maps, "recommended": recommended}, ensure_ascii=False, sort_keys=True))
    print("MCP_CUBELESS_PCG_LEVEL_TARGET_AUDIT_END")


if __name__ == "__main__":
    main()
