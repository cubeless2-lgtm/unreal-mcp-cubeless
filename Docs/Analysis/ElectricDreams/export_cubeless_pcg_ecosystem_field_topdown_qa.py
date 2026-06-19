import json
import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "export_cubeless_pcg_ecosystem_field_topdown_qa.py",
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
OUTPUT_DIR = PROJECT_ROOT / "Saved" / "MCP_Screenshots"
OUTPUT_JSON = OUTPUT_DIR / "pcg_field_broad_patch_topdown.json"
OUTPUT_SVG = OUTPUT_DIR / "pcg_field_broad_patch_topdown.svg"

ACTOR_LABELS = [
    "Cubeless_PCG_EcosystemRuntime_DenseMeadowWest",
    "Cubeless_PCG_EcosystemRuntime_DenseMeadowCenter",
    "Cubeless_PCG_EcosystemRuntime_DenseMeadowEast",
    "Cubeless_PCG_EcosystemRuntime_GroundFoliageSouthWestWarm",
    "Cubeless_PCG_EcosystemRuntime_GroundFoliageSouthWarm",
    "Cubeless_PCG_EcosystemRuntime_GroundFoliageSouthEastWarm",
    "Cubeless_PCG_EcosystemRuntime_RockyCoolEdgeEastNorth",
    "Cubeless_PCG_EcosystemRuntime_RockyCoolEdgeEastSouth",
    "Cubeless_PCG_EcosystemRuntime_ConiferGroveNorthWest",
    "Cubeless_PCG_EcosystemRuntime_ConiferGroveNorthEast",
]

COLORS = {
    "meadow": "#4f9b35",
    "foliage": "#f2c84b",
    "rock": "#8b98a8",
    "conifer": "#1e6f38",
    "unknown": "#d9d9d9",
}


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
        raise RuntimeError(f"Missing target level: {TARGET_LEVEL}")
    loaded = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(TARGET_LEVEL)
    if not loaded:
        raise RuntimeError(f"Failed to load level: {TARGET_LEVEL}")


def get_instance_transform(component, index):
    transform = component.get_instance_transform(index, True)
    if isinstance(transform, tuple):
        return transform[0] if transform else None
    return transform


def category_for(actor_label, mesh_path):
    lowered = f"{actor_label} {mesh_path}".lower()
    if "rock" in lowered or "stone" in lowered:
        return "rock"
    if "conifer" in lowered or "tree" in lowered:
        return "conifer"
    if "grass" in lowered or "meadow" in lowered:
        return "meadow"
    if "foliage" in lowered or "fern" in lowered or "flower" in lowered or "leaf" in lowered:
        return "foliage"
    return "unknown"


def collect_instances():
    actors_by_label = {actor.get_actor_label(): actor for actor in get_all_level_actors()}
    missing = [label for label in ACTOR_LABELS if label not in actors_by_label]
    if missing:
        raise RuntimeError(f"Missing tuned field actors: {missing}")

    instances = []
    actor_summaries = []
    for label in ACTOR_LABELS:
        actor = actors_by_label[label]
        actor_count = 0
        mesh_counts = {}
        for component in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
            mesh = component.get_editor_property("static_mesh")
            mesh_path = mesh.get_path_name() if mesh else "None"
            count = int(component.get_instance_count())
            mesh_counts[mesh_path] = mesh_counts.get(mesh_path, 0) + count
            for index in range(count):
                transform = get_instance_transform(component, index)
                if not transform:
                    continue
                location = transform.translation
                category = category_for(label, mesh_path)
                instances.append(
                    {
                        "actor": label,
                        "mesh": mesh_path,
                        "category": category,
                        "x": float(location.x),
                        "y": float(location.y),
                        "z": float(location.z),
                    }
                )
                actor_count += 1
        actor_summaries.append(
            {
                "actor": label,
                "instance_count": actor_count,
                "mesh_counts": mesh_counts,
            }
        )
    return actor_summaries, instances


def bounds_for(instances):
    xs = [item["x"] for item in instances]
    ys = [item["y"] for item in instances]
    return {
        "min_x": min(xs),
        "max_x": max(xs),
        "min_y": min(ys),
        "max_y": max(ys),
        "width_cm": max(xs) - min(xs),
        "height_cm": max(ys) - min(ys),
    }


def write_json(actor_summaries, instances, bounds):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    category_counts = {}
    for item in instances:
        category_counts[item["category"]] = category_counts.get(item["category"], 0) + 1
    payload = {
        "level": TARGET_LEVEL,
        "actor_count": len(actor_summaries),
        "instance_count": len(instances),
        "bounds": bounds,
        "category_counts": category_counts,
        "actors": actor_summaries,
        "instances": instances,
    }
    OUTPUT_JSON.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return payload


def svg_circle(x, y, radius, fill, title):
    return (
        f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:.2f}" fill="{fill}" '
        f'fill-opacity="0.82"><title>{title}</title></circle>'
    )


def write_svg(payload):
    bounds = payload["bounds"]
    margin = 64.0
    width = 1200.0
    height = 820.0
    data_w = max(1.0, bounds["width_cm"])
    data_h = max(1.0, bounds["height_cm"])
    scale = min((width - margin * 2.0) / data_w, (height - margin * 2.0) / data_h)

    def map_x(value):
        return margin + (value - bounds["min_x"]) * scale

    def map_y(value):
        return height - margin - (value - bounds["min_y"]) * scale

    circles = []
    for item in payload["instances"]:
        radius = 6.0
        if item["category"] == "conifer":
            radius = 12.0
        elif item["category"] == "rock":
            radius = 10.0
        elif item["category"] == "foliage":
            radius = 5.0
        fill = COLORS.get(item["category"], COLORS["unknown"])
        title = f'{item["actor"]} | {item["category"]} | {item["mesh"]}'
        circles.append(svg_circle(map_x(item["x"]), map_y(item["y"]), radius, fill, title))

    labels = []
    for actor in payload["actors"]:
        actor_instances = [item for item in payload["instances"] if item["actor"] == actor["actor"]]
        if not actor_instances:
            continue
        cx = sum(item["x"] for item in actor_instances) / len(actor_instances)
        cy = sum(item["y"] for item in actor_instances) / len(actor_instances)
        labels.append(
            f'<text x="{map_x(cx):.2f}" y="{map_y(cy) - 18.0:.2f}" '
            f'font-size="18" font-family="Arial" text-anchor="middle" fill="#1b1b1b">'
            f'{actor["instance_count"]}</text>'
        )

    legend_items = [
        ("meadow", "Meadow grass"),
        ("foliage", "Warm foliage/flowers"),
        ("rock", "Rock edge"),
        ("conifer", "Conifer edge"),
    ]
    legend = []
    lx = margin
    ly = 42.0
    for index, (category, label) in enumerate(legend_items):
        x = lx + index * 240.0
        legend.append(svg_circle(x, ly - 5.0, 8.0, COLORS[category], label))
        legend.append(
            f'<text x="{x + 16.0:.2f}" y="{ly:.2f}" font-size="16" '
            f'font-family="Arial" fill="#1b1b1b">{label}</text>'
        )

    title = (
        f'Cubeless PCG Field Top-Down QA - {payload["actor_count"]} actors, '
        f'{payload["instance_count"]} instances, '
        f'{bounds["width_cm"] / 100.0:.1f}m x {bounds["height_cm"] / 100.0:.1f}m'
    )
    svg = "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">',
            '<rect width="100%" height="100%" fill="#f5f1e8"/>',
            f'<text x="{margin:.2f}" y="24" font-size="20" font-family="Arial" fill="#1b1b1b">{title}</text>',
            *legend,
            '<rect x="64" y="64" width="1072" height="692" fill="#ffffff" fill-opacity="0.4" stroke="#9d9688"/>',
            *circles,
            *labels,
            "</svg>",
        ]
    )
    OUTPUT_SVG.write_text(svg, encoding="utf-8")


def main():
    print("MCP_CUBELESS_PCG_FIELD_TOPDOWN_QA_BEGIN")
    ensure_target_level_loaded()
    actor_summaries, instances = collect_instances()
    bounds = bounds_for(instances)
    payload = write_json(actor_summaries, instances, bounds)
    write_svg(payload)
    print(f"qa_level={TARGET_LEVEL}")
    print(f"qa_actor_count={payload['actor_count']}")
    print(f"qa_instance_count={payload['instance_count']}")
    print(f"qa_bounds={payload['bounds']}")
    print(f"qa_category_counts={payload['category_counts']}")
    print(f"qa_json={OUTPUT_JSON}")
    print(f"qa_svg={OUTPUT_SVG}")
    print("pcg_field_topdown_qa_pass=True")
    print("MCP_CUBELESS_PCG_FIELD_TOPDOWN_QA_END")


if __name__ == "__main__":
    main()
