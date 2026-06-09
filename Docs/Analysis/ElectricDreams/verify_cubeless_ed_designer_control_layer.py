import pathlib
from collections import defaultdict

import unreal


BUILDER_SCRIPT = r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\build_cubeless_ed_designer_control_layer.py"
VERIFY_MARKER = "MCP_CUBELESS_ED_DESIGNER_CONTROL_LAYER_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_cubeless_ed_designer_control_layer_config"}
    with open(BUILDER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), BUILDER_SCRIPT, "exec")
    exec(code, namespace)
    return namespace


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def get_actor(label):
    for actor in get_all_level_actors():
        if actor.get_actor_label() == label:
            return actor
    raise RuntimeError(f"Missing actor: {label}")


def get_generated_point_data(component):
    for attempt in range(4):
        collection = component.get_generated_graph_output()
        for item in collection.get_editor_property("tagged_data"):
            data = item.get_editor_property("data").get_editor_property("data")
            if data and hasattr(data, "get_num_points"):
                return data
        if attempt < 3:
            component.generate(True)
    raise RuntimeError("No generated point data found")


def get_point_rows(point_data):
    metadata = point_data.const_metadata()
    point_count = point_data.get_num_points()
    input_range = unreal.PCGPointInputRange()
    input_range.set_editor_property("point_data", point_data)
    input_range.set_editor_property("range_start_index", 0)
    input_range.set_editor_property("range_size", point_count)

    entries = list(point_data.get_metadata_entry_values_from_range(input_range))
    seeds = list(point_data.get_seed_values_from_range(input_range))
    densities = list(point_data.get_density_values_from_range(input_range))
    helpers = unreal.PCGMetadataAccessorHelpers
    rows = []
    for idx, entry in enumerate(entries):
        entry = int(entry)
        rows.append({
            "metadata_entry": entry,
            "seed": int(seeds[idx]),
            "density": round(float(densities[idx]), 3),
            "designer_profile_id": int(
                helpers.get_integer32_attribute_by_metadata_key(
                    entry,
                    metadata,
                    "DesignerProfileId",
                )
            ),
            "designer_profile_type": int(
                helpers.get_integer32_attribute_by_metadata_key(
                    entry,
                    metadata,
                    "DesignerProfileType",
                )
            ),
            "designer_control_layer_pass": bool(
                helpers.get_bool_attribute_by_metadata_key(
                    entry,
                    metadata,
                    "DesignerControlLayerPass",
                )
            ),
        })
    return rows


def get_ism_rows(actor):
    rows = []
    for component in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
        mesh = component.get_editor_property("static_mesh")
        mesh_path = mesh.get_path_name() if mesh else "None"
        try:
            count = int(component.get_instance_count())
        except Exception:
            count = -1
        rows.append((component.get_name(), mesh_path, count))
    return rows


def get_subgraph_references(graph):
    refs = {}
    for node in graph.get_editor_property("nodes"):
        settings = node.get_settings()
        if not settings or settings.get_class().get_name() != "PCGSubgraphSettings":
            continue
        title = str(node.get_editor_property("node_title"))
        instance = settings.get_editor_property("subgraph_instance")
        subgraph = instance.get_editor_property("graph") if instance else None
        refs[title] = subgraph.get_path_name() if subgraph else None
    return refs


def scan_latest_log(marker):
    log_dir = pathlib.Path(unreal.Paths.project_log_dir())
    logs = sorted(log_dir.glob("*.log"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not logs:
        return None, False, []
    latest = logs[0]
    text = latest.read_text(encoding="utf-8", errors="ignore")
    idx = text.rfind(marker)
    scan_text = text[idx:] if idx >= 0 else text
    errors = [line for line in scan_text.splitlines() if "Error:" in line]
    return latest, idx >= 0, errors


def main():
    config = load_builder_config()
    graph = unreal.EditorAssetLibrary.load_asset(config["GRAPH_PATH"])
    if not graph:
        raise RuntimeError(f"Missing graph: {config['GRAPH_PATH']}")

    try:
        actor = get_actor(config["ACTOR_LABEL"])
    except RuntimeError:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(config["LEVEL"])
        actor = get_actor(config["ACTOR_LABEL"])

    component = actor.get_components_by_class(unreal.PCGComponent)[0]
    point_data = get_generated_point_data(component)
    rows = get_point_rows(point_data)
    ism_rows = get_ism_rows(actor)
    subgraph_refs = get_subgraph_references(graph)

    expected_by_id = {
        int(spec["id"]): {
            "name": spec["name"],
            "type": int(spec["type"]),
            "expected_points": int(spec["expected_points"]),
            "graph_path": spec["graph_path"],
        }
        for spec in config["PROFILE_SPECS"]
    }
    rows_by_profile = defaultdict(list)
    for row in rows:
        rows_by_profile[row["designer_profile_id"]].append(row)

    profile_counts = {
        expected_by_id.get(profile_id, {"name": f"unknown_{profile_id}"})["name"]: len(profile_rows)
        for profile_id, profile_rows in sorted(rows_by_profile.items())
    }
    profile_types = {
        expected_by_id.get(profile_id, {"name": f"unknown_{profile_id}"})["name"]: sorted(
            set(row["designer_profile_type"] for row in profile_rows)
        )
        for profile_id, profile_rows in sorted(rows_by_profile.items())
    }
    expected_counts = {
        spec["name"]: int(spec["expected_points"])
        for spec in config["PROFILE_SPECS"]
    }

    pass_count = sum(1 for row in rows if row["designer_control_layer_pass"])
    unknown_profile_count = sum(1 for row in rows if row["designer_profile_id"] not in expected_by_id)
    type_mismatches = [
        row for row in rows
        if row["designer_profile_id"] not in expected_by_id
        or row["designer_profile_type"] != expected_by_id[row["designer_profile_id"]]["type"]
    ]
    count_mismatches = [
        {
            "profile": expected["name"],
            "expected": expected["expected_points"],
            "actual": len(rows_by_profile.get(profile_id, [])),
        }
        for profile_id, expected in expected_by_id.items()
        if len(rows_by_profile.get(profile_id, [])) != expected["expected_points"]
    ]
    subgraph_ref_mismatches = []
    for expected in expected_by_id.values():
        matching_refs = [
            path for title, path in subgraph_refs.items()
            if expected["name"] in title
        ]
        if expected["graph_path"] not in matching_refs:
            subgraph_ref_mismatches.append({
                "profile": expected["name"],
                "expected_graph": expected["graph_path"],
                "actual_refs": matching_refs,
            })

    total_expected_points = sum(spec["expected_points"] for spec in expected_by_id.values())
    total_ism_instances = sum(max(0, count) for _, _, count in ism_rows)
    log_path, marker_found, log_errors = scan_latest_log("MCP_CUBELESS_ED_DESIGNER_CONTROL_LAYER_BUILD_BEGIN")

    validation_pass = all([
        len(rows) == total_expected_points,
        profile_counts == expected_counts,
        pass_count == len(rows),
        unknown_profile_count == 0,
        not type_mismatches,
        not count_mismatches,
        not subgraph_ref_mismatches,
        total_ism_instances == total_expected_points,
        not log_errors,
    ])

    print(VERIFY_MARKER)
    print(f"production_graph={config['GRAPH_PATH']}")
    print(f"validation_actor={config['ACTOR_LABEL']}")
    print(f"profile_specs={config['PROFILE_SPECS']}")
    print(f"expected_total_points={total_expected_points}")
    print(f"point_count={len(rows)}")
    print(f"expected_profile_counts={expected_counts}")
    print(f"profile_counts={profile_counts}")
    print(f"profile_types={profile_types}")
    print(f"designer_control_layer_pass_count={pass_count}")
    print(f"unknown_profile_count={unknown_profile_count}")
    print(f"type_mismatch_count={len(type_mismatches)}")
    print(f"count_mismatch_count={len(count_mismatches)}")
    print(f"subgraph_references={subgraph_refs}")
    print(f"subgraph_ref_mismatch_count={len(subgraph_ref_mismatches)}")
    print(f"total_ism_instances={total_ism_instances}")
    print(f"ism_rows={ism_rows}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print("rows_sample=")
    for row in sorted(rows, key=lambda item: (item["designer_profile_id"], item["seed"]))[:24]:
        print(
            "  Profile={designer_profile_id} Type={designer_profile_type} "
            "Seed={seed} Density={density} ControlPass={designer_control_layer_pass}".format(**row)
        )
    print(f"designer_control_layer_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_DESIGNER_CONTROL_LAYER_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED designer control layer verification failed")


if __name__ == "__main__":
    main()
