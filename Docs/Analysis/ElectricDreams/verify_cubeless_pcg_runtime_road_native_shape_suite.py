import importlib
import pathlib
import sys

import unreal


EXPECTED_SHAPE_COUNT = 4
TEMP_SHAPE_ACTOR_LABEL_PREFIX = "MCP_TMP_NativeRoadPCGShapeSuite_"


def load_road_module():
    script_dir = (
        pathlib.Path(unreal.Paths.project_dir())
        / "Plugins"
        / "CustomTools"
        / "Content"
        / "Python"
        / "ArtScripts"
    )
    if not script_dir.exists():
        raise RuntimeError(f"Missing Cubeless road script directory: {script_dir}")
    script_dir_text = str(script_dir)
    if script_dir_text not in sys.path:
        sys.path.append(script_dir_text)
    import CubelessRoadPCG

    return importlib.reload(CubelessRoadPCG)


def get_all_level_actors():
    subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if subsystem_cls:
        subsystem = unreal.get_editor_subsystem(subsystem_cls)
        if subsystem:
            return list(subsystem.get_all_level_actors())
    return list(unreal.EditorLevelLibrary.get_all_level_actors())


def actor_label(actor):
    try:
        return actor.get_actor_label()
    except Exception:
        return actor.get_name()


def verify_result_item(item):
    key = item.get("shape_key")
    quality = item.get("shape_suite_quality") or {}
    checks = quality.get("checks") or {}
    failed_checks = [name for name, passed in checks.items() if passed is not True]
    if quality.get("pass") is not True:
        raise RuntimeError(f"Shape suite quality failed for {key}: {quality}")
    if failed_checks:
        raise RuntimeError(f"Shape suite checks failed for {key}: {failed_checks}")
    if item.get("status") != "ready":
        raise RuntimeError(f"Shape suite item not ready for {key}: {item.get('status')}")
    if item.get("graph_edge_errors"):
        raise RuntimeError(f"Shape suite graph edge errors for {key}: {item.get('graph_edge_errors')}")
    if int(item.get("roadside_clearance_violation_count", -1)) != 0:
        raise RuntimeError(
            f"Shape suite clearance violations for {key}: {item.get('roadside_clearance_violations')}"
        )
    if item.get("runtime_material_value_mismatches"):
        raise RuntimeError(
            f"Shape suite material mismatches for {key}: {item.get('runtime_material_value_mismatches')}"
        )
    if int(item.get("spline_mesh_component_count", 0)) <= 0:
        raise RuntimeError(f"Shape suite produced no spline mesh components for {key}")
    if int(item.get("instanced_instance_total", 0)) <= 0:
        raise RuntimeError(f"Shape suite produced no roadside instances for {key}")


def verify_no_temp_shape_actor():
    leftovers = [
        actor_label(actor)
        for actor in get_all_level_actors()
        if actor_label(actor).startswith(TEMP_SHAPE_ACTOR_LABEL_PREFIX)
    ]
    if leftovers:
        raise RuntimeError(f"Native road shape suite preview actors remain: {leftovers}")
    return leftovers


def verify_report(report):
    if not report.get("exists"):
        raise RuntimeError(f"Missing native road shape suite report: {report.get('report_path')}")
    if report.get("status") != "ready":
        raise RuntimeError(
            "Native road shape suite report is not ready: "
            f"status={report.get('status')} report={report.get('report_path')}"
        )
    if report.get("pass") is not True:
        raise RuntimeError(f"Native road shape suite did not pass: {report}")
    if int(report.get("shape_count", -1)) != EXPECTED_SHAPE_COUNT:
        raise RuntimeError(
            f"Unexpected shape count: expected={EXPECTED_SHAPE_COUNT} actual={report.get('shape_count')}"
        )
    if int(report.get("completed_shape_count", -1)) != EXPECTED_SHAPE_COUNT:
        raise RuntimeError(
            "Native road shape suite did not complete every shape: "
            f"completed={report.get('completed_shape_count')} expected={EXPECTED_SHAPE_COUNT}"
        )
    if report.get("restore_pass") is not True:
        raise RuntimeError(f"Native road shape suite did not restore source spline: {report}")
    results = list(report.get("results") or [])
    if len(results) != EXPECTED_SHAPE_COUNT:
        raise RuntimeError(f"Unexpected shape result count: {len(results)}")
    for item in results:
        verify_result_item(item)


def main():
    road_module = load_road_module()
    report = road_module.read_runtime_road_native_graph_shape_suite_report()
    verify_report(report)
    leftovers = verify_no_temp_shape_actor()

    print("runtime_road_native_shape_suite_verify_complete=True")
    print(f"runtime_road_native_shape_suite_pass={report.get('pass')}")
    print(f"runtime_road_native_shape_suite_status={report.get('status')}")
    print(f"runtime_road_native_shape_suite_completed={report.get('completed_shape_count')}")
    for item in report.get("results") or []:
        print(
            "runtime_road_native_shape_suite_result="
            f"{item.get('shape_key')}|spline_mesh={item.get('spline_mesh_component_count')}"
            f"|instances={item.get('instanced_instance_total')}"
            f"|clearance={item.get('roadside_clearance_violation_count')}"
        )
    print(f"runtime_road_native_shape_suite_temp_actor_leftovers={leftovers}")


if __name__ == "__main__":
    main()
