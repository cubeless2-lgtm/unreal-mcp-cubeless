import json
import pathlib

import unreal


REPORT_PATH = (
    pathlib.Path(unreal.Paths.project_saved_dir())
    / "MCP_PCG"
    / "CubelessClosedSplineGrassMeshActorPropertyOverride_Report.json"
)


def main():
    if not REPORT_PATH.exists():
        raise RuntimeError(f"Missing closed grass mesh override report: {REPORT_PATH}")
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    validation = report.get("validation") or {}
    mesh_override = validation.get("mesh_override") or {}
    graph_update = report.get("graph_update") or {}
    if report.get("pass") is not True:
        raise RuntimeError(f"Closed grass mesh override report did not pass: {report}")
    if validation.get("spline_closed_loop") is not True:
        raise RuntimeError(f"Closed spline flag mismatch: {validation}")
    if int(validation.get("spline_point_count", -1)) < 3:
        raise RuntimeError(f"Closed spline point count is invalid: {validation}")
    if int(validation.get("generated_instance_total", 0)) <= 0:
        raise RuntimeError(f"Closed grass override generated no instances: {validation}")
    if int(validation.get("outside_violation_count", -1)) != 0:
        raise RuntimeError(f"Closed grass override has outside violations: {validation}")
    if mesh_override.get("requested") is not True:
        raise RuntimeError(f"Mesh override was not requested by the source actor: {mesh_override}")
    if mesh_override.get("actor_property_mesh_override_pass") is not True:
        raise RuntimeError(f"Actor-property mesh override failed: {mesh_override}")
    if graph_update.get("edge_errors"):
        raise RuntimeError(f"Closed grass mesh override graph edge errors: {graph_update}")
    print("pcg_closed_grass_mesh_actor_property_override_verify_complete=True")
    print(f"pcg_closed_grass_mesh_actor_property_override_pass={report.get('pass')}")
    print(
        "pcg_closed_grass_mesh_actor_property_override_actor_mesh="
        f"{mesh_override.get('actor_property_mesh')}"
    )
    print(
        "pcg_closed_grass_mesh_actor_property_override_output_meshes="
        f"{mesh_override.get('output_meshes')}"
    )
    print(
        "pcg_closed_grass_mesh_actor_property_override_generated_total="
        f"{validation.get('generated_instance_total')}"
    )


if __name__ == "__main__":
    main()
