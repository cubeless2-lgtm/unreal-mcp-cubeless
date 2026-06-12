import json
import pathlib

import unreal


REPORT_PATH = (
    pathlib.Path(unreal.Paths.project_saved_dir())
    / "MCP_PCG"
    / "CubelessClosedSplineGrassArea_Report.json"
)
EXPECTED_DEFAULT_MESH = (
    "/Game/DreamscapeSeries/DreamscapeMountains/Meshes/Foliage/Grass/"
    "SM_Grass_Medium01.SM_Grass_Medium01"
)


def main():
    if not REPORT_PATH.exists():
        raise RuntimeError(f"Missing closed spline grass report: {REPORT_PATH}")
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    validation = report.get("validation") or {}
    mesh_override = validation.get("mesh_override") or {}
    graph_update = report.get("graph_update") or {}
    if report.get("pass") is not True:
        raise RuntimeError(f"Closed spline grass report did not pass: {report}")
    if validation.get("spline_closed_loop") is not True:
        raise RuntimeError(f"Closed spline flag mismatch: {validation}")
    if int(validation.get("spline_point_count", -1)) < 3:
        raise RuntimeError(f"Closed spline point count is invalid: {validation}")
    if int(validation.get("generated_instance_total", 0)) <= 0:
        raise RuntimeError(f"Closed spline grass generated no instances: {validation}")
    if int(validation.get("outside_violation_count", -1)) != 0:
        raise RuntimeError(f"Closed spline grass has outside violations: {validation}")
    if int(validation.get("pitch_roll_violation_count_after", -1)) != 0:
        raise RuntimeError(f"Closed spline grass has pitch/roll violations: {validation}")
    if mesh_override.get("requested") is not False:
        raise RuntimeError(f"Default validation should keep mesh override disabled: {mesh_override}")
    if mesh_override.get("actor_property_mesh_override_pass") is not True:
        raise RuntimeError(f"Default mesh branch failed actor-property compatibility: {mesh_override}")
    if mesh_override.get("output_meshes") != [EXPECTED_DEFAULT_MESH]:
        raise RuntimeError(f"Default output mesh mismatch: {mesh_override}")
    if graph_update.get("edge_errors"):
        raise RuntimeError(f"Closed grass graph edge errors: {graph_update}")
    print("pcg_closed_spline_grass_area_verify_complete=True")
    print(f"pcg_closed_spline_grass_area_pass={report.get('pass')}")
    print(f"pcg_closed_spline_grass_area_generated_total={validation.get('generated_instance_total')}")
    print(f"pcg_closed_spline_grass_area_output_meshes={mesh_override.get('output_meshes')}")
    print(f"pcg_closed_spline_grass_area_outside={validation.get('outside_violation_count')}")


if __name__ == "__main__":
    main()
