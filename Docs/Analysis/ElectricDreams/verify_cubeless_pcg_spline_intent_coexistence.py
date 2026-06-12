import json
import pathlib

import unreal


REPORT_PATH = pathlib.Path(unreal.Paths.project_saved_dir()) / "MCP_PCG" / "CubelessSplineIntentCoexistence_Report.json"


def main():
    if not REPORT_PATH.exists():
        raise RuntimeError(f"Missing spline intent coexistence report: {REPORT_PATH}")
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    closed = report.get("closed_area_validation") or {}
    opened = report.get("open_linear_validation") or {}
    isolation = report.get("intent_isolation") or {}
    if report.get("pass") is not True:
        raise RuntimeError(f"Spline intent coexistence did not pass: {report}")
    if int(closed.get("spline_point_count", -1)) != 6:
        raise RuntimeError(f"Closed spline point count mismatch: {closed}")
    if int(closed.get("outside_violation_count", -1)) != 0:
        raise RuntimeError(f"Closed spline outside violations exist: {closed}")
    if int(opened.get("spline_point_count", -1)) != 2:
        raise RuntimeError(f"Open spline point count mismatch: {opened}")
    if opened.get("actor_property_mesh_override_pass") is not True:
        raise RuntimeError(f"Open spline mesh override failed: {opened}")
    if isolation.get("pass") is not True:
        raise RuntimeError(f"Spline intent isolation failed: {isolation}")
    print("pcg_spline_intent_coexistence_verify_complete=True")
    print(f"pcg_spline_intent_coexistence_pass={report.get('pass')}")
    print(f"pcg_spline_intent_coexistence_closed_points={closed.get('spline_point_count')}")
    print(f"pcg_spline_intent_coexistence_open_points={opened.get('spline_point_count')}")
    print(f"pcg_spline_intent_coexistence_open_components={opened.get('spline_mesh_component_count')}")


if __name__ == "__main__":
    main()
