import pathlib


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\verify_cubeless_ed_dynamic_material_axis_actor_property_selector_compat.py",
    )
).parent
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_dynamic_material_axis_actor_property_selector_compat.py"
BASE_VERIFY_SCRIPT = SCRIPT_DIR / "verify_cubeless_ed_dynamic_material_axis_actor_property_selector.py"
VERIFY_MARKER = "MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_ACTOR_PROPERTY_COMPAT_VERIFY_BEGIN"


def load_script(script_path, namespace_name):
    namespace = {"__name__": namespace_name, "__file__": str(script_path)}
    with open(script_path, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(script_path), "exec")
    exec(code, namespace)
    return namespace


def main():
    print(VERIFY_MARKER)
    config = load_script(BUILDER_SCRIPT, "_cubeless_ed_dynamic_material_axis_actor_property_compat_config")
    base_verify = load_script(BASE_VERIFY_SCRIPT, "_cubeless_ed_dynamic_material_axis_actor_property_verify")
    graph_result = base_verify["validate_graph"](config)
    actor_result = base_verify["validate_actor"](config)
    log_path, marker_found, log_errors = base_verify["BASE_VERIFY"]["scan_latest_log"](
        "MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_ACTOR_PROPERTY_COMPAT_BUILD_BEGIN"
    )
    validation_pass = all([
        graph_result["validation_pass"],
        actor_result["validation_pass"],
        not log_errors,
    ])
    print(f"dynamic_material_axis_actor_property_compat_graph={graph_result['graph']}")
    print("dynamic_material_axis_actor_property_compat_graph_count=1")
    print(f"dynamic_material_axis_actor_property_compat_property_checks={graph_result['property_checks']}")
    print(f"dynamic_material_axis_actor_property_compat_filter_checks={graph_result['filter_checks']}")
    print(f"dynamic_material_axis_actor_property_compat_spawner_checks={graph_result['spawner_checks']}")
    print(f"dynamic_material_axis_actor_property_compat_graph_validation_pass={graph_result['validation_pass']}")
    print(f"dynamic_material_axis_actor_property_compat_actor={actor_result['actor']}")
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
    print(f"dynamic_material_axis_actor_property_compat_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_DYNAMIC_MATERIAL_AXIS_ACTOR_PROPERTY_COMPAT_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED dynamic material axis actor property compat verification failed")


if __name__ == "__main__":
    main()
