import importlib
import pathlib
import sys

import unreal


EXPECTED_ROADSIDE_COUNTS = {
    "gravel": 235,
    "stone": 46,
    "embankment": 7,
}
EXPECTED_SPLINE_MESH_COUNT = 288
EXPECTED_INSTANCE_TOTAL = 288
TEMP_VALIDATION_ACTOR_LABEL = "MCP_TMP_NativeRoadPCGValidation_LiveCollect"


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


def verify_report(report):
    if not report.get("exists"):
        raise RuntimeError(f"Missing native road smoke report: {report.get('report_path')}")
    if report.get("status") != "ready":
        raise RuntimeError(
            "Native road smoke report is not ready: "
            f"status={report.get('status')} report={report.get('report_path')}"
        )
    if report.get("pass") is not True:
        raise RuntimeError(f"Native road smoke did not pass: {report}")

    actual_counts = report.get("roadside_point_counts") or {}
    if actual_counts != EXPECTED_ROADSIDE_COUNTS:
        raise RuntimeError(
            "Native road roadside counts mismatch: "
            f"expected={EXPECTED_ROADSIDE_COUNTS} actual={actual_counts}"
        )

    if report.get("roadside_count_mismatches"):
        raise RuntimeError(f"Unexpected roadside count mismatches: {report.get('roadside_count_mismatches')}")
    if int(report.get("roadside_clearance_violation_count", -1)) != 0:
        raise RuntimeError(
            "Native road clearance violations exist: "
            f"{report.get('roadside_clearance_violations')}"
        )
    if int(report.get("spline_mesh_component_count", -1)) != EXPECTED_SPLINE_MESH_COUNT:
        raise RuntimeError(
            "Native road spline mesh count mismatch: "
            f"expected={EXPECTED_SPLINE_MESH_COUNT} actual={report.get('spline_mesh_component_count')}"
        )
    if int(report.get("instanced_instance_total", -1)) != EXPECTED_INSTANCE_TOTAL:
        raise RuntimeError(
            "Native road instance total mismatch: "
            f"expected={EXPECTED_INSTANCE_TOTAL} actual={report.get('instanced_instance_total')}"
        )


def verify_no_temp_actor():
    leftovers = [
        actor_label(actor)
        for actor in get_all_level_actors()
        if actor_label(actor) == TEMP_VALIDATION_ACTOR_LABEL
    ]
    if leftovers:
        raise RuntimeError(f"Native road smoke preview actors remain: {leftovers}")
    return leftovers


def main():
    road_module = load_road_module()
    report = road_module.read_runtime_road_native_graph_live_smoke_report()
    verify_report(report)
    leftovers = verify_no_temp_actor()

    print("runtime_road_native_smoke_verify_complete=True")
    print(f"runtime_road_native_smoke_pass={report.get('pass')}")
    print(f"runtime_road_native_smoke_status={report.get('status')}")
    print(f"runtime_road_native_smoke_roadside_counts={report.get('roadside_point_counts')}")
    print(f"runtime_road_native_smoke_clearance_violations={report.get('roadside_clearance_violation_count')}")
    print(f"runtime_road_native_smoke_spline_mesh_count={report.get('spline_mesh_component_count')}")
    print(f"runtime_road_native_smoke_instance_total={report.get('instanced_instance_total')}")
    print(f"runtime_road_native_smoke_temp_actor_leftovers={leftovers}")


if __name__ == "__main__":
    main()
