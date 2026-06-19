import pathlib
import json
import os
import traceback

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "export_sg_copy_points_with_hierarchy_details.py",
    )
).resolve().parent

GRAPH_PATH = "/Game/PCG/Assets/PCGCustomNodes/SG_CopyPointsWithHierarchy.SG_CopyPointsWithHierarchy"
OUT_PATH = str(SCRIPT_DIR / "sg_copy_points_with_hierarchy_details.json")


def safe_str(value, limit=500):
    try:
        text = str(value)
    except Exception as exc:
        text = f"<str error: {exc}>"
    return text if len(text) <= limit else text[:limit] + "..."


def object_summary(obj):
    if obj is None:
        return None
    item = {
        "repr": safe_str(repr(obj), 300),
        "type": type(obj).__name__,
    }
    try:
        item["class"] = obj.get_class().get_name()
    except Exception:
        pass
    try:
        item["name"] = obj.get_name()
    except Exception:
        pass
    try:
        item["path"] = obj.get_path_name()
    except Exception:
        pass
    return item


def value_summary(value, depth=0):
    if depth > 2:
        return safe_str(repr(value), 250)
    if value is None:
        return None
    if isinstance(value, (bool, int, float, str)):
        return value
    if hasattr(value, "export_text"):
        try:
            return {"type": type(value).__name__, "export_text": value.export_text()}
        except Exception:
            pass
    if isinstance(value, (list, tuple)):
        return [value_summary(v, depth + 1) for v in list(value)[:50]]
    # Unreal Array is iterable but not always an isinstance(list).
    if type(value).__name__ == "Array":
        try:
            return [value_summary(v, depth + 1) for v in list(value)[:50]]
        except Exception:
            return safe_str(repr(value), 250)
    if hasattr(value, "get_path_name"):
        return object_summary(value)
    return safe_str(repr(value), 300)


def editor_props(obj):
    props = {}
    if obj is None:
        return props
    for name in dir(obj):
        if name.startswith("_"):
            continue
        try:
            value = obj.get_editor_property(name)
        except Exception:
            continue
        props[name] = value_summary(value)
    return props


def pin_label(pin):
    try:
        return str(pin.get_editor_property("properties").get_editor_property("label"))
    except Exception:
        return pin.get_name()


def graph_edges(nodes):
    edge_refs = {}
    for node in nodes:
        for direction, pin_prop in (("input", "input_pins"), ("output", "output_pins")):
            try:
                pins = list(node.get_editor_property(pin_prop))
            except Exception:
                continue
            for pin in pins:
                label = pin_label(pin)
                try:
                    edges = list(pin.get_editor_property("edges"))
                except Exception:
                    edges = []
                for edge in edges:
                    key = edge.get_path_name()
                    entry = edge_refs.setdefault(key, {"edge": key})
                    entry[direction] = {
                        "node": node.get_name(),
                        "node_title": safe_str(node.get_editor_property("node_title")),
                        "pin": pin.get_name(),
                        "label": label,
                    }
    return list(edge_refs.values())


def node_summary(node):
    settings = None
    try:
        settings = node.get_settings()
    except Exception:
        pass
    item = {
        "name": node.get_name(),
        "title": safe_str(node.get_editor_property("node_title")),
        "class": node.get_class().get_name(),
        "settings_class": settings.get_class().get_name() if settings else None,
        "settings_path": settings.get_path_name() if settings else None,
        "position": None,
        "pins": {"inputs": [], "outputs": []},
        "settings_properties": {},
    }
    try:
        item["position"] = safe_str(node.get_node_position())
    except Exception:
        pass
    for key, pin_prop in (("inputs", "input_pins"), ("outputs", "output_pins")):
        try:
            pins = list(node.get_editor_property(pin_prop))
        except Exception:
            pins = []
        for pin in pins:
            item["pins"][key].append(
                {
                    "name": pin.get_name(),
                    "label": pin_label(pin),
                    "edge_count": len(list(pin.get_editor_property("edges"))),
                }
            )
    if settings:
        interesting = [
            "blueprint_element_type",
            "blueprint_element_instance",
            "input_source",
            "output_target",
            "attribute_types",
            "copy_all_attributes",
            "copy_all_domains",
            "rotation_inheritance",
            "scale_inheritance",
            "color_inheritance",
            "seed_inheritance",
            "attribute_inheritance",
            "tag_inheritance",
            "copy_each_source_on_every_target",
        ]
        for prop in interesting:
            try:
                item["settings_properties"][prop] = value_summary(settings.get_editor_property(prop))
            except Exception:
                pass
    return item


def generated_class_asset_path(cls):
    if cls is None:
        return None
    try:
        path = cls.get_path_name()
    except Exception:
        return None
    # /Game/Foo/BP.BP_C -> /Game/Foo/BP.BP
    if path.endswith("_C") and "." in path:
        package, obj = path.rsplit(".", 1)
        if obj.endswith("_C"):
            return f"{package}.{obj[:-2]}"
    return None


def graph_node_details(ed_graph):
    result = {
        "name": ed_graph.get_name(),
        "class": ed_graph.get_class().get_name(),
        "path": ed_graph.get_path_name(),
        "nodes": [],
    }
    try:
        nodes = list(ed_graph.get_editor_property("nodes"))
    except Exception:
        nodes = []
    for node in nodes:
        node_item = {
            "name": node.get_name(),
            "class": node.get_class().get_name(),
            "path": node.get_path_name(),
            "props": {},
            "pins": [],
        }
        for prop in ["node_comment", "function_name", "custom_function_name", "member_name"]:
            try:
                node_item["props"][prop] = value_summary(node.get_editor_property(prop))
            except Exception:
                pass
        try:
            pins = list(node.get_editor_property("pins"))
        except Exception:
            pins = []
        for pin in pins:
            pin_item = {
                "name": safe_str(pin.get_editor_property("pin_name")),
                "direction": safe_str(pin.get_editor_property("direction")),
                "category": None,
                "default_value": None,
                "linked_to": [],
            }
            try:
                pin_item["category"] = safe_str(pin.get_editor_property("pin_type").get_editor_property("pin_category"))
            except Exception:
                pass
            try:
                pin_item["default_value"] = safe_str(pin.get_editor_property("default_value"))
            except Exception:
                pass
            try:
                pin_item["linked_to"] = [linked.get_path_name() for linked in list(pin.get_editor_property("linked_to"))]
            except Exception:
                pass
            node_item["pins"].append(pin_item)
        result["nodes"].append(node_item)
    return result


def inspect_blueprint_asset(asset):
    if asset is None:
        return None
    result = object_summary(asset)
    result["properties"] = {}
    for prop in ["parent_class", "generated_class", "skeleton_generated_class", "ubergraph_pages", "function_graphs", "new_variables"]:
        try:
            result["properties"][prop] = value_summary(asset.get_editor_property(prop))
        except Exception:
            pass
    graphs = []
    for prop in ["ubergraph_pages", "function_graphs"]:
        try:
            graph_list = list(asset.get_editor_property(prop))
        except Exception:
            graph_list = []
        for ed_graph in graph_list:
            graphs.append(graph_node_details(ed_graph))
    # Some Blueprint assets do not expose graph arrays through editor properties in
    # commandlet mode. Query common graph names directly through the editor helper.
    direct_graph_names = [
        "EventGraph",
        "ExecuteWithContext",
        "IterationLoopBody",
        "ReceiveExecute",
        "Execute",
    ]
    try:
        event_graph = unreal.BlueprintEditorLibrary.find_event_graph(asset)
    except Exception:
        event_graph = None
    if event_graph:
        existing = {g.get("path") for g in graphs}
        detail = graph_node_details(event_graph)
        if detail.get("path") not in existing:
            graphs.append(detail)
    for graph_name in direct_graph_names:
        try:
            ed_graph = unreal.BlueprintEditorLibrary.find_graph(asset, graph_name)
        except Exception:
            ed_graph = None
        if not ed_graph:
            continue
        existing = {g.get("path") for g in graphs}
        detail = graph_node_details(ed_graph)
        if detail.get("path") not in existing:
            graphs.append(detail)
    result["graphs"] = graphs
    return result


def main():
    report = {
        "graph_path": GRAPH_PATH,
        "errors": [],
        "graph": None,
        "nodes": [],
        "edges": [],
        "blueprint_settings": [],
    }
    try:
        graph = unreal.EditorAssetLibrary.load_asset(GRAPH_PATH)
        if not graph:
            raise RuntimeError(f"Failed to load {GRAPH_PATH}")
        report["graph"] = object_summary(graph)
        nodes = list(graph.get_editor_property("nodes"))
        for extra in [graph.get_input_node(), graph.get_output_node()]:
            if extra and extra not in nodes:
                nodes.append(extra)
        report["nodes"] = [node_summary(n) for n in nodes]
        report["edges"] = graph_edges(nodes)
        for n in nodes:
            settings = n.get_settings()
            if not settings or settings.get_class().get_name() != "PCGBlueprintSettings":
                continue
            item = {
                "node": n.get_name(),
                "title": safe_str(n.get_editor_property("node_title")),
                "settings": object_summary(settings),
                "settings_properties": editor_props(settings),
                "blueprint_element_type": None,
                "blueprint_element_default_object": None,
                "blueprint_asset": None,
                "blueprint_element_instance": None,
            }
            try:
                element_type = settings.get_editor_property("blueprint_element_type")
            except Exception:
                element_type = None
            item["blueprint_element_type"] = object_summary(element_type)
            if element_type:
                try:
                    cdo = element_type.get_default_object()
                except Exception:
                    cdo = None
                item["blueprint_element_default_object"] = {
                    "summary": object_summary(cdo),
                    "properties": editor_props(cdo),
                    "dir": [x for x in dir(cdo) if not x.startswith("_")][:300] if cdo else [],
                }
                asset_path = generated_class_asset_path(element_type)
                if asset_path:
                    asset = unreal.EditorAssetLibrary.load_asset(asset_path)
                    item["blueprint_asset"] = inspect_blueprint_asset(asset)
            try:
                instance = settings.get_editor_property("blueprint_element_instance")
            except Exception:
                instance = None
            item["blueprint_element_instance"] = {
                "summary": object_summary(instance),
                "properties": editor_props(instance),
                "dir": [x for x in dir(instance) if not x.startswith("_")][:300] if instance else [],
            }
            report["blueprint_settings"].append(item)
    except Exception:
        report["errors"].append(traceback.format_exc())
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    unreal.log(f"Wrote {OUT_PATH}")
    if report["errors"]:
        unreal.log_error("\\n".join(report["errors"]))


main()
