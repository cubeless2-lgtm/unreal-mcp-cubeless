import pathlib
from collections import defaultdict

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_material_override_presets.py",
    )
).parent
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_material_override_presets.py"
VERIFY_MARKER = "MCP_CUBELESS_ED_MATERIAL_OVERRIDE_PRESETS_VERIFY_BEGIN"


def load_builder_config():
    namespace = {"__name__": "_cubeless_ed_material_override_presets_config", "__file__": str(BUILDER_SCRIPT)}
    with open(BUILDER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(BUILDER_SCRIPT), "exec")
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


def get_int_attr(helpers, entry, metadata, name):
    try:
        return int(helpers.get_integer32_attribute_by_metadata_key(entry, metadata, name))
    except Exception:
        return None


def get_bool_attr(helpers, entry, metadata, name):
    try:
        return bool(helpers.get_bool_attribute_by_metadata_key(entry, metadata, name))
    except Exception:
        return False


def get_point_rows(point_data):
    metadata = point_data.const_metadata()
    point_count = point_data.get_num_points()
    input_range = unreal.PCGPointInputRange()
    input_range.set_editor_property("point_data", point_data)
    input_range.set_editor_property("range_start_index", 0)
    input_range.set_editor_property("range_size", point_count)

    entries = list(point_data.get_metadata_entry_values_from_range(input_range))
    helpers = unreal.PCGMetadataAccessorHelpers
    rows = []
    for entry in entries:
        entry = int(entry)
        rows.append({
            "designer_material_domain_id": get_int_attr(helpers, entry, metadata, "DesignerMaterialDomainId"),
            "designer_material_domain_type": get_int_attr(helpers, entry, metadata, "DesignerMaterialDomainType"),
            "designer_material_variant_id": get_int_attr(helpers, entry, metadata, "DesignerMaterialVariantId"),
            "designer_material_variant_type": get_int_attr(helpers, entry, metadata, "DesignerMaterialVariantType"),
            "designer_material_override_id": get_int_attr(helpers, entry, metadata, "DesignerMaterialOverrideId"),
            "designer_material_override_type": get_int_attr(helpers, entry, metadata, "DesignerMaterialOverrideType"),
            "designer_material_override_mode": get_int_attr(helpers, entry, metadata, "DesignerMaterialOverrideMode"),
            "designer_material_override_pass": get_bool_attr(helpers, entry, metadata, "DesignerMaterialOverridePass"),
        })
    return rows


def get_material_path(material):
    return material.get_path_name() if material else "None"


def get_component_material_paths(component):
    try:
        slot_count = int(component.get_num_materials())
    except Exception:
        slot_count = 4
    paths = []
    for slot_index in range(max(0, slot_count)):
        try:
            paths.append(get_material_path(component.get_material(slot_index)))
        except Exception:
            break
    return paths


def get_ism_rows(actor):
    rows = []
    for component in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
        mesh = component.get_editor_property("static_mesh")
        mesh_path = mesh.get_path_name() if mesh else "None"
        try:
            count = int(component.get_instance_count())
        except Exception:
            count = -1
        rows.append({
            "component": component.get_name(),
            "mesh": mesh_path,
            "count": count,
            "materials": get_component_material_paths(component),
        })
    return rows


def get_spawner_entry_rows(graph_path):
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        raise RuntimeError(f"Missing graph for spawner check: {graph_path}")
    rows = []
    for node in graph.get_editor_property("nodes"):
        settings = node.get_settings()
        if not settings or settings.get_class().get_name() != "PCGStaticMeshSpawnerSettings":
            continue
        params = settings.get_editor_property("mesh_selector_parameters")
        for entry in params.get_editor_property("mesh_entries"):
            descriptor = entry.get_editor_property("descriptor")
            mesh = descriptor.get_editor_property("static_mesh") if descriptor else None
            overrides = descriptor.get_editor_property("override_materials") if descriptor else []
            rows.append({
                "mesh": mesh.get_path_name() if mesh else "None",
                "override_materials": [get_material_path(material) for material in overrides],
            })
    return rows


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


def expected_entry_map(spec):
    return {
        entry["mesh_path"]: list(entry["override_material_paths"])
        for entry in spec["entries"]
    }


def actual_entry_map(rows):
    return {
        row["mesh"]: list(row["override_materials"])
        for row in rows
    }


def validate_material_assets(config):
    rows = []
    for key, spec in config["MATERIAL_VARIANT_SPECS"].items():
        path = config["material_variant_path"](key)
        material = unreal.EditorAssetLibrary.load_asset(path)
        parent = material.get_editor_property("parent") if material else None
        parent_path = parent.get_path_name() if parent else None
        rows.append({
            "key": key,
            "path": path,
            "exists": bool(material),
            "parent": parent_path,
            "expected_parent": spec["parent"],
            "parent_match": parent_path == spec["parent"],
        })
    return rows


def validate_generated_material_slots(ism_rows, expected_map):
    checked = []
    failures = []
    for row in ism_rows:
        mesh = row["mesh"]
        expected_overrides = expected_map.get(mesh, [])
        if row["count"] <= 0 or not expected_overrides:
            continue
        actual_prefix = row["materials"][:len(expected_overrides)]
        match = actual_prefix == expected_overrides
        checked.append({
            "mesh": mesh,
            "component": row["component"],
            "expected": expected_overrides,
            "actual": actual_prefix,
            "match": match,
        })
        if not match:
            failures.append(checked[-1])
    return checked, failures


def validate_material_override(spec, config):
    graph_path = config["MATERIAL_OVERRIDE_GRAPH_PATHS"][spec["name"]]
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        raise RuntimeError(f"Missing material override graph: {graph_path}")

    label = f"{config['ACTOR_LABEL_PREFIX']}_{spec['name']}_Validation"
    actor = get_actor(label)
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {label}")

    rows = get_point_rows(get_generated_point_data(pcg_components[0]))
    ism_rows = get_ism_rows(actor)
    total_ism_instances = sum(max(0, row["count"]) for row in ism_rows)
    expected_map = expected_entry_map(spec)
    spawner_rows = get_spawner_entry_rows(graph_path)
    spawner_map = actual_entry_map(spawner_rows)
    slot_checks, slot_failures = validate_generated_material_slots(ism_rows, expected_map)

    domain_counts = defaultdict(int)
    variant_counts = defaultdict(int)
    override_counts = defaultdict(int)
    for row in rows:
        domain_counts[row["designer_material_domain_id"]] += 1
        variant_counts[row["designer_material_variant_id"]] += 1
        override_counts[row["designer_material_override_id"]] += 1

    mismatch_counts = {
        "domain_type": sum(1 for row in rows if row["designer_material_domain_type"] != spec["domain_type"]),
        "variant_type": sum(1 for row in rows if row["designer_material_variant_type"] != spec["variant_type"]),
        "override_type": sum(1 for row in rows if row["designer_material_override_type"] != spec["override_type"]),
        "override_mode": sum(1 for row in rows if row["designer_material_override_mode"] != spec["override_mode"]),
    }
    override_pass_count = sum(1 for row in rows if row["designer_material_override_pass"])

    validation_pass = all([
        len(rows) == spec["expected_points"],
        total_ism_instances == spec["expected_ism"],
        dict(domain_counts) == {spec["domain_id"]: spec["expected_points"]},
        dict(variant_counts) == {spec["variant_id"]: spec["expected_points"]},
        dict(override_counts) == {spec["override_id"]: spec["expected_points"]},
        all(count == 0 for count in mismatch_counts.values()),
        override_pass_count == spec["expected_points"],
        spawner_map == expected_map,
        not slot_failures,
    ])
    return {
        "material_override": spec["name"],
        "actor": label,
        "graph": graph_path,
        "domain": f"{spec['domain_id']}/{spec['domain_type']}",
        "variant": f"{spec['variant_id']}/{spec['variant_type']}",
        "point_count": len(rows),
        "expected_points": spec["expected_points"],
        "total_ism_instances": total_ism_instances,
        "expected_ism": spec["expected_ism"],
        "domain_counts": dict(domain_counts),
        "variant_counts": dict(variant_counts),
        "override_counts": dict(override_counts),
        "mismatch_counts": mismatch_counts,
        "override_pass_count": override_pass_count,
        "spawner_map": spawner_map,
        "expected_spawner_map": expected_map,
        "slot_checks": slot_checks,
        "slot_failures": slot_failures,
        "ism_rows": ism_rows,
        "validation_pass": validation_pass,
    }


def main():
    print(VERIFY_MARKER)
    config = load_builder_config()
    material_rows = validate_material_assets(config)
    material_assets_pass = all(row["exists"] and row["parent_match"] for row in material_rows)
    print(f"material_variant_count={len(material_rows)}")
    for row in material_rows:
        print(f"material_variant={row['key']}")
        print(f"  path={row['path']}")
        print(f"  exists={row['exists']}")
        print(f"  parent={row['parent']}")
        print(f"  expected_parent={row['expected_parent']}")
        print(f"  parent_match={row['parent_match']}")

    print(f"material_override_graph_count={len(config['MATERIAL_OVERRIDE_GRAPH_PATHS'])}")
    results = [
        validate_material_override(spec, config)
        for spec in config["MATERIAL_OVERRIDE_SPECS"]
    ]
    log_path, marker_found, log_errors = scan_latest_log("MCP_CUBELESS_ED_MATERIAL_OVERRIDE_PRESETS_BUILD_BEGIN")
    validation_pass = material_assets_pass and all(result["validation_pass"] for result in results) and not log_errors

    for result in results:
        print(f"material_override={result['material_override']}")
        print(f"  actor={result['actor']}")
        print(f"  graph={result['graph']}")
        print(f"  domain={result['domain']}")
        print(f"  variant={result['variant']}")
        print(f"  point_count={result['point_count']}")
        print(f"  expected_points={result['expected_points']}")
        print(f"  total_ism_instances={result['total_ism_instances']}")
        print(f"  expected_ism={result['expected_ism']}")
        print(f"  domain_counts={result['domain_counts']}")
        print(f"  variant_counts={result['variant_counts']}")
        print(f"  override_counts={result['override_counts']}")
        print(f"  mismatch_counts={result['mismatch_counts']}")
        print(f"  override_pass_count={result['override_pass_count']}")
        print(f"  spawner_map={result['spawner_map']}")
        print(f"  expected_spawner_map={result['expected_spawner_map']}")
        print(f"  slot_checks={result['slot_checks']}")
        print(f"  slot_failures={result['slot_failures']}")
        print(f"  ism_rows={result['ism_rows']}")
        print(f"  validation_pass={result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"material_override_presets_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_MATERIAL_OVERRIDE_PRESETS_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED material override presets verification failed")


if __name__ == "__main__":
    main()
