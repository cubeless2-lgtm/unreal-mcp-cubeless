import json
import pathlib
from collections import Counter, defaultdict

import unreal


OUTPUT_JSON = pathlib.Path(
    r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams"
    r"\electric_dreams_pcg_extracted_settings.json"
)

GRAPH_PATHS = [
    "/Game/PCG/Graphs/Ditch/PCGDemo_Ditch.PCGDemo_Ditch",
    "/Game/PCG/Graphs/Ground/PCGDemo_Ground.PCGDemo_Ground",
    "/Game/PCG/Graphs/Forest/DiscardPointsInBumpyAreas.DiscardPointsInBumpyAreas",
]

PROPERTY_MAP = {
    "PCGDensityFilterSettings": [
        "lower_bound",
        "upper_bound",
        "invert_filter",
        "keep_zero_density_points",
        "seed",
    ],
    "PCGDensityRemapSettings": [
        "range_min",
        "range_max",
        "out_range_min",
        "out_range_max",
        "exclude_values_outside_input_range",
        "seed",
    ],
    "PCGBoundsModifierSettings": [
        "mode",
        "bounds_min",
        "bounds_max",
        "seed",
    ],
    "PCGSelfPruningSettings": [
        "parameters",
        "seed",
    ],
    "PCGAttributeNoiseSettings": [
        "mode",
        "noise_min",
        "noise_max",
        "input_source",
        "output_target",
        "seed",
    ],
    "PCGAttributeFilteringSettings": [
        "operator",
        "use_constant_threshold",
        "target_attribute",
        "threshold_attribute",
        "attribute_types",
        "warn_on_data_missing_attribute",
        "seed",
    ],
}

SELF_PRUNING_PARAMETER_PROPS = [
    "pruning_type",
    "comparison_source",
    "radius_similarity_factor",
    "randomized_pruning",
    "use_collision_attribute",
    "collision_attribute",
    "collision_query_flag",
]


def vector_to_dict(value):
    return {
        "x": round(float(value.get_editor_property("x")), 6),
        "y": round(float(value.get_editor_property("y")), 6),
        "z": round(float(value.get_editor_property("z")), 6),
    }


def safe_export_text(value):
    for method_name in ("export_text", "to_string"):
        method = getattr(value, method_name, None)
        if method:
            try:
                return str(method())
            except Exception:
                pass
    return str(value)


def simplify_value(value):
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if value.__class__.__name__ == "Vector":
        return vector_to_dict(value)
    text = safe_export_text(value)
    if text.startswith("<") and "{" in text:
        return text
    if "." in text and text.startswith("<") is False:
        return text
    return text


def read_property(settings, prop_name):
    try:
        value = settings.get_editor_property(prop_name)
    except Exception as exc:
        return {"error": str(exc)}

    if prop_name == "parameters" and settings.__class__.__name__ == "PCGSelfPruningSettings":
        params = {}
        for sub_prop in SELF_PRUNING_PARAMETER_PROPS:
            try:
                params[sub_prop] = simplify_value(value.get_editor_property(sub_prop))
            except Exception as exc:
                params[sub_prop] = {"error": str(exc)}
        return params

    return simplify_value(value)


def extract_graph(graph_path):
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        return {
            "path": graph_path,
            "loaded": False,
            "nodes": [],
            "class_counts": {},
            "value_fingerprints": {},
        }

    nodes = []
    class_counts = Counter()
    fingerprints = defaultdict(Counter)
    for node in graph.get_editor_property("nodes"):
        settings = node.get_settings()
        settings_class = settings.__class__.__name__
        class_counts[settings_class] += 1
        if settings_class not in PROPERTY_MAP:
            continue

        try:
            title = str(node.get_editor_property("node_title"))
        except Exception:
            title = ""
        try:
            node_name = str(node.get_name())
        except Exception:
            node_name = ""

        properties = {}
        for prop_name in PROPERTY_MAP[settings_class]:
            properties[prop_name] = read_property(settings, prop_name)

        fingerprint = json.dumps(properties, sort_keys=True, ensure_ascii=False)
        fingerprints[settings_class][fingerprint] += 1
        nodes.append({
            "node_name": node_name,
            "title": title,
            "settings_class": settings_class,
            "settings_path": settings.get_path_name(),
            "properties": properties,
        })

    return {
        "path": graph_path,
        "loaded": True,
        "node_count": len(graph.get_editor_property("nodes")),
        "extracted_node_count": len(nodes),
        "class_counts": dict(sorted(class_counts.items())),
        "nodes": nodes,
        "value_fingerprints": {
            cls: [
                {"count": count, "properties": json.loads(fingerprint)}
                for fingerprint, count in counter.most_common()
            ]
            for cls, counter in sorted(fingerprints.items())
        },
    }


def main():
    print("MCP_PCG_ELECTRIC_DREAMS_SETTINGS_EXTRACT_BEGIN")
    report = {
        "graphs": [extract_graph(path) for path in GRAPH_PATHS],
    }
    OUTPUT_JSON.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"output_json={OUTPUT_JSON}")
    for graph in report["graphs"]:
        print(
            "graph={path}|loaded={loaded}|nodes={node_count}|extracted={extracted_node_count}".format(
                path=graph["path"],
                loaded=graph["loaded"],
                node_count=graph.get("node_count", 0),
                extracted_node_count=graph.get("extracted_node_count", 0),
            )
        )
        for cls in sorted(PROPERTY_MAP):
            count = graph.get("class_counts", {}).get(cls, 0)
            unique = len(graph.get("value_fingerprints", {}).get(cls, []))
            if count or unique:
                print(f"  {cls}|count={count}|unique_property_sets={unique}")
    print("MCP_PCG_ELECTRIC_DREAMS_SETTINGS_EXTRACT_END")


if __name__ == "__main__":
    main()
