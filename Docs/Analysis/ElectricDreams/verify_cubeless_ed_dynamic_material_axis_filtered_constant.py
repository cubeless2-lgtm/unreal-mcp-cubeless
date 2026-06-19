import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_dynamic_material_axis_filtered_constant.py",
    )
).parent
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_dynamic_material_axis_filtered_constant.py"
AXIS_VERIFY_SCRIPT = SCRIPT_DIR / "verify_cubeless_ed_dynamic_material_axis_by_point.py"
VERIFY_MARKER = "MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_FILTERED_CONSTANT_VERIFY_BEGIN"


def load_script(script_path, namespace_name):
    namespace = {"__name__": namespace_name, "__file__": str(script_path)}
    with open(script_path, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(script_path), "exec")
    exec(code, namespace)
    return namespace


def load_config():
    return load_script(BUILDER_SCRIPT, "_cubeless_ed_dynamic_material_axis_filtered_constant_config")


BASE_VERIFY = load_script(AXIS_VERIFY_SCRIPT, "_cubeless_ed_dynamic_material_axis_verify_helpers")


def selector_text(selector):
    for attr in ("get_name", "get_display_text"):
        func = getattr(selector, attr, None)
        if callable(func):
            try:
                return str(func())
            except Exception:
                pass
    return str(selector)


def constant_int_value(value_struct):
    for prop in ("int32_value", "int_value"):
        try:
            return int(value_struct.get_editor_property(prop))
        except Exception:
            pass
    return None


def get_graph_nodes_by_settings(graph, settings_name):
    return [
        node for node in graph.get_editor_property("nodes")
        if node.get_settings() and node.get_settings().get_class().get_name() == settings_name
    ]


def validate_graph(config):
    graph = unreal.EditorAssetLibrary.load_asset(config["GRAPH_PATH"])
    if not graph:
        raise RuntimeError(f"Missing filtered constant graph: {config['GRAPH_PATH']}")

    filters = get_graph_nodes_by_settings(graph, "PCGAttributeFilteringSettings")
    spawners = get_graph_nodes_by_settings(graph, "PCGStaticMeshSpawnerSettings")
    filter_checks = []
    for node in filters:
        settings = node.get_settings()
        value_struct = settings.get_editor_property("attribute_types")
        filter_checks.append({
            "node": str(node.get_editor_property("node_title")),
            "target_attribute": selector_text(settings.get_editor_property("target_attribute")),
            "threshold_attribute": selector_text(settings.get_editor_property("threshold_attribute")),
            "operator": str(settings.get_editor_property("operator")),
            "use_constant_threshold": bool(settings.get_editor_property("use_constant_threshold")),
            "constant_int": constant_int_value(value_struct),
        })

    spawner_checks = []
    for node in spawners:
        settings = node.get_settings()
        params = settings.get_editor_property("mesh_selector_parameters")
        spawner_checks.append({
            "node": str(node.get_editor_property("node_title")),
            "selector_class": params.get_class().get_name() if params else None,
            "attribute_name": str(params.get_editor_property("attribute_name")) if params else None,
            "use_attribute_material_overrides": bool(params.get_editor_property("use_attribute_material_overrides")) if params else False,
            "material_override_attributes": [str(item) for item in params.get_editor_property("material_override_attributes")] if params else [],
        })

    domain_ok = any(
        config["DOMAIN_ATTR"] in item["target_attribute"]
        and item["constant_int"] == config["SELECTED_DOMAIN_TYPE"]
        and item["use_constant_threshold"]
        for item in filter_checks
    )
    variant_ok = any(
        config["VARIANT_ATTR"] in item["target_attribute"]
        and item["constant_int"] == config["SELECTED_VARIANT_TYPE"]
        and item["use_constant_threshold"]
        for item in filter_checks
    )
    spawner_ok = (
        len(spawner_checks) == 1
        and spawner_checks[0]["selector_class"] == "PCGMeshSelectorByAttribute"
        and spawner_checks[0]["attribute_name"] == config["AXIS_CONFIG"]["DYNAMIC_CONFIG"]["DYNAMIC_MESH_ATTR"]
        and spawner_checks[0]["use_attribute_material_overrides"]
        and spawner_checks[0]["material_override_attributes"] == [
            config["AXIS_CONFIG"]["DYNAMIC_CONFIG"]["DYNAMIC_MATERIAL_SLOT0_ATTR"],
            config["AXIS_CONFIG"]["DYNAMIC_CONFIG"]["DYNAMIC_MATERIAL_SLOT1_ATTR"],
        ]
    )
    validation_pass = len(filters) == 2 and domain_ok and variant_ok and spawner_ok
    return {
        "graph": config["GRAPH_PATH"],
        "filter_checks": filter_checks,
        "spawner_checks": spawner_checks,
        "domain_filter_ok": domain_ok,
        "variant_filter_ok": variant_ok,
        "spawner_ok": spawner_ok,
        "validation_pass": validation_pass,
    }


def matching_ism_rows(ism_rows, expected_row):
    materials = expected_row["materials"]
    return [
        row for row in ism_rows
        if row["mesh"] == expected_row["mesh_path"]
        and row["materials"][:len(materials)] == materials
    ]


def validate_actor(config):
    actor = BASE_VERIFY["find_actor"](config["ACTOR_LABEL"])
    if not actor:
        raise RuntimeError(f"Missing filtered constant validation actor: {config['ACTOR_LABEL']}")
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {config['ACTOR_LABEL']}")
    component = pcg_components[0]
    expected_rows = config["selected_expected_rows"]()
    expected_total = sum(row["expected_instance_count"] for row in expected_rows)
    point_count = BASE_VERIFY["get_generated_point_count"](component)
    ism_rows = BASE_VERIFY["get_ism_rows"](actor)
    total_ism = sum(max(0, row["count"]) for row in ism_rows)
    row_results = []
    for expected_row in expected_rows:
        rows = matching_ism_rows(ism_rows, expected_row)
        row_results.append({
            "domain_name": expected_row["domain_name"],
            "domain_type": expected_row["domain_type"],
            "variant_name": expected_row["variant_name"],
            "variant_type": expected_row["variant_type"],
            "mesh_key": expected_row["mesh_key"],
            "mesh_path": expected_row["mesh_path"],
            "expected_materials": expected_row["materials"],
            "matching_row_count": len(rows),
            "matching_instance_count": sum(max(0, row["count"]) for row in rows),
            "expected_instance_count": expected_row["expected_instance_count"],
        })
    validation_pass = all([
        BASE_VERIFY["get_component_graph_path"](component) == config["GRAPH_PATH"],
        len(expected_rows) == 2,
        point_count == expected_total,
        total_ism == expected_total,
        all(result["matching_row_count"] == 1 for result in row_results),
        all(result["matching_instance_count"] == result["expected_instance_count"] for result in row_results),
    ])
    return {
        "actor": config["ACTOR_LABEL"],
        "graph": BASE_VERIFY["get_component_graph_path"](component),
        "expected_graph": config["GRAPH_PATH"],
        "point_count": point_count,
        "expected_points": expected_total,
        "total_ism": total_ism,
        "expected_ism": expected_total,
        "row_results": row_results,
        "ism_rows": ism_rows,
        "validation_pass": validation_pass,
    }


def main():
    print(VERIFY_MARKER)
    config = load_config()
    graph_result = validate_graph(config)
    actor_result = validate_actor(config)
    log_path, marker_found, log_errors = BASE_VERIFY["scan_latest_log"](
        "MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_FILTERED_CONSTANT_BUILD_BEGIN"
    )
    validation_pass = all([
        graph_result["validation_pass"],
        actor_result["validation_pass"],
        not log_errors,
    ])
    print(f"dynamic_material_axis_filtered_constant_graph={graph_result['graph']}")
    print("dynamic_material_axis_filtered_constant_graph_count=1")
    print(f"dynamic_material_axis_filtered_constant_filter_checks={graph_result['filter_checks']}")
    print(f"dynamic_material_axis_filtered_constant_spawner_checks={graph_result['spawner_checks']}")
    print(f"dynamic_material_axis_filtered_constant_domain_filter_ok={graph_result['domain_filter_ok']}")
    print(f"dynamic_material_axis_filtered_constant_variant_filter_ok={graph_result['variant_filter_ok']}")
    print(f"dynamic_material_axis_filtered_constant_spawner_ok={graph_result['spawner_ok']}")
    print(f"dynamic_material_axis_filtered_constant_graph_validation_pass={graph_result['validation_pass']}")
    print(f"dynamic_material_axis_filtered_constant_actor={actor_result['actor']}")
    print(f"  graph={actor_result['graph']}")
    print(f"  expected_graph={actor_result['expected_graph']}")
    print(f"  point_count={actor_result['point_count']}")
    print(f"  expected_points={actor_result['expected_points']}")
    print(f"  total_ism={actor_result['total_ism']}")
    print(f"  expected_ism={actor_result['expected_ism']}")
    for result in actor_result["row_results"]:
        print(f"  row_result={result}")
    print(f"  ism_rows={actor_result['ism_rows']}")
    print(f"  validation_pass={actor_result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"dynamic_material_axis_filtered_constant_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_FILTERED_CONSTANT_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED dynamic material axis filtered constant verification failed")


if __name__ == "__main__":
    main()
