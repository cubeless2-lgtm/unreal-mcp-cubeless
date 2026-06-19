import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_dynamic_material_axis_actor_property_selector.py",
    )
).parent
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_dynamic_material_axis_actor_property_selector.py"
AXIS_VERIFY_SCRIPT = SCRIPT_DIR / "verify_cubeless_ed_dynamic_material_axis_by_point.py"
VERIFY_MARKER = "MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_ACTOR_PROPERTY_VERIFY_BEGIN"


def load_script(script_path, namespace_name):
    namespace = {"__name__": namespace_name, "__file__": str(script_path)}
    with open(script_path, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(script_path), "exec")
    exec(code, namespace)
    return namespace


def load_config():
    return load_script(BUILDER_SCRIPT, "_cubeless_ed_dynamic_material_axis_actor_property_config")


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


def get_graph_nodes_by_settings(graph, settings_name):
    return [
        node for node in graph.get_editor_property("nodes")
        if node.get_settings() and node.get_settings().get_class().get_name() == settings_name
    ]


def validate_graph(config):
    graph = unreal.EditorAssetLibrary.load_asset(config["GRAPH_PATH"])
    if not graph:
        raise RuntimeError(f"Missing actor property selector graph: {config['GRAPH_PATH']}")

    property_nodes = get_graph_nodes_by_settings(graph, "PCGGetActorPropertySettings")
    filters = get_graph_nodes_by_settings(graph, "PCGAttributeFilteringSettings")
    spawners = get_graph_nodes_by_settings(graph, "PCGStaticMeshSpawnerSettings")

    property_checks = []
    for node in property_nodes:
        settings = node.get_settings()
        property_checks.append({
            "node": str(node.get_editor_property("node_title")),
            "property_name": str(settings.get_editor_property("property_name")),
            "output_attribute_name": selector_text(settings.get_editor_property("output_attribute_name")),
            "always_requery_actors": bool(settings.get_editor_property("always_requery_actors")),
        })

    filter_checks = []
    for node in filters:
        settings = node.get_settings()
        filter_checks.append({
            "node": str(node.get_editor_property("node_title")),
            "target_attribute": selector_text(settings.get_editor_property("target_attribute")),
            "threshold_attribute": selector_text(settings.get_editor_property("threshold_attribute")),
            "operator": str(settings.get_editor_property("operator")),
            "use_constant_threshold": bool(settings.get_editor_property("use_constant_threshold")),
            "use_spatial_query": bool(settings.get_editor_property("use_spatial_query")),
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

    domain_property_ok = any(
        item["property_name"] == config["DOMAIN_PROPERTY"]
        and config["SELECTED_DOMAIN_ATTR"] in item["output_attribute_name"]
        for item in property_checks
    )
    variant_property_ok = any(
        item["property_name"] == config["VARIANT_PROPERTY"]
        and config["SELECTED_VARIANT_ATTR"] in item["output_attribute_name"]
        for item in property_checks
    )
    domain_filter_ok = any(
        config["DOMAIN_ATTR"] in item["target_attribute"]
        and config["SELECTED_DOMAIN_ATTR"] in item["threshold_attribute"]
        and not item["use_constant_threshold"]
        for item in filter_checks
    )
    variant_filter_ok = any(
        config["VARIANT_ATTR"] in item["target_attribute"]
        and config["SELECTED_VARIANT_ATTR"] in item["threshold_attribute"]
        and not item["use_constant_threshold"]
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
    validation_pass = all([
        len(property_nodes) == 2,
        len(filters) == 2,
        domain_property_ok,
        variant_property_ok,
        domain_filter_ok,
        variant_filter_ok,
        spawner_ok,
    ])
    return {
        "graph": config["GRAPH_PATH"],
        "property_checks": property_checks,
        "filter_checks": filter_checks,
        "spawner_checks": spawner_checks,
        "domain_property_ok": domain_property_ok,
        "variant_property_ok": variant_property_ok,
        "domain_filter_ok": domain_filter_ok,
        "variant_filter_ok": variant_filter_ok,
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
        raise RuntimeError(f"Missing actor property selector validation actor: {config['ACTOR_LABEL']}")
    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {config['ACTOR_LABEL']}")
    component = pcg_components[0]
    expected_rows = config["selected_expected_rows"]()
    expected_total = sum(row["expected_instance_count"] for row in expected_rows)
    point_count = BASE_VERIFY["get_generated_point_count"](component)
    ism_rows = BASE_VERIFY["get_ism_rows"](actor)
    total_ism = sum(max(0, row["count"]) for row in ism_rows)
    actor_domain = int(actor.get_editor_property(config["DOMAIN_PROPERTY"]))
    actor_variant = int(actor.get_editor_property(config["VARIANT_PROPERTY"]))
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
        actor_domain == config["SELECTED_DOMAIN_TYPE"],
        actor_variant == config["SELECTED_VARIANT_TYPE"],
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
        "actor_domain": actor_domain,
        "expected_domain": config["SELECTED_DOMAIN_TYPE"],
        "actor_variant": actor_variant,
        "expected_variant": config["SELECTED_VARIANT_TYPE"],
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
        "MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_ACTOR_PROPERTY_BUILD_BEGIN"
    )
    validation_pass = all([
        graph_result["validation_pass"],
        actor_result["validation_pass"],
        not log_errors,
    ])
    print(f"dynamic_material_axis_actor_property_graph={graph_result['graph']}")
    print("dynamic_material_axis_actor_property_graph_count=1")
    print(f"dynamic_material_axis_actor_property_property_checks={graph_result['property_checks']}")
    print(f"dynamic_material_axis_actor_property_filter_checks={graph_result['filter_checks']}")
    print(f"dynamic_material_axis_actor_property_spawner_checks={graph_result['spawner_checks']}")
    print(f"dynamic_material_axis_actor_property_domain_property_ok={graph_result['domain_property_ok']}")
    print(f"dynamic_material_axis_actor_property_variant_property_ok={graph_result['variant_property_ok']}")
    print(f"dynamic_material_axis_actor_property_domain_filter_ok={graph_result['domain_filter_ok']}")
    print(f"dynamic_material_axis_actor_property_variant_filter_ok={graph_result['variant_filter_ok']}")
    print(f"dynamic_material_axis_actor_property_spawner_ok={graph_result['spawner_ok']}")
    print(f"dynamic_material_axis_actor_property_graph_validation_pass={graph_result['validation_pass']}")
    print(f"dynamic_material_axis_actor_property_actor={actor_result['actor']}")
    print(f"  graph={actor_result['graph']}")
    print(f"  expected_graph={actor_result['expected_graph']}")
    print(f"  actor_domain={actor_result['actor_domain']}")
    print(f"  expected_domain={actor_result['expected_domain']}")
    print(f"  actor_variant={actor_result['actor_variant']}")
    print(f"  expected_variant={actor_result['expected_variant']}")
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
    print(f"dynamic_material_axis_actor_property_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_ACTOR_PROPERTY_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED dynamic material axis actor property verification failed")


if __name__ == "__main__":
    main()
