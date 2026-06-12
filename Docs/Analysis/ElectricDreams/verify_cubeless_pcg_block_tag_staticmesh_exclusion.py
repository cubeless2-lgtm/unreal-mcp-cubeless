import json
import pathlib

import unreal


REPORT_PATH = pathlib.Path(unreal.Paths.project_saved_dir()) / "MCP_PCG" / "CubelessBlockTagStaticMeshExclusion_Report.json"


def main():
    if not REPORT_PATH.exists():
        raise RuntimeError(f"Missing block-tag StaticMesh exclusion report: {REPORT_PATH}")
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    raw = report.get("raw_validation_before_python_prune") or {}
    fixed = report.get("validation_after_python_prune") or {}
    prune = report.get("python_prune") or {}
    cleanup = report.get("blocker_cleanup") or {}
    mesh_update = (report.get("block_aware_graph") or {}).get("mesh_override_update") or {}
    raw_mesh_override = raw.get("mesh_override") or {}
    if report.get("pass") is not True:
        raise RuntimeError(f"Block-tag StaticMesh exclusion did not pass: {report}")
    if report.get("native_graph_exclusion_pass") is not True:
        raise RuntimeError(f"Native graph block-tag exclusion did not pass: {report}")
    if int(raw.get("block_tagged_component_count", 0)) < 1:
        raise RuntimeError(f"Block-tagged component was not detected: {raw}")
    if int(raw.get("generated_instance_total", 0)) <= 0:
        raise RuntimeError(f"Block-aware graph generated no instances: {raw}")
    if raw_mesh_override.get("requested") is not True:
        raise RuntimeError(f"Block-aware graph should validate actor-property mesh override: {raw_mesh_override}")
    if raw_mesh_override.get("actor_property_mesh_override_pass") is not True:
        raise RuntimeError(f"Block-aware graph mesh override failed: {raw_mesh_override}")
    if mesh_update.get("mode") != "attribute_before_difference":
        raise RuntimeError(f"Block-aware graph used the wrong mesh override mode: {mesh_update}")
    if int(fixed.get("block_overlap_violation_count", -1)) != 0:
        raise RuntimeError(f"Block overlaps remain after prune: {fixed}")
    if int(prune.get("total_removed", -1)) != 0:
        raise RuntimeError(f"Native graph should not require Python prune after fix: {prune}")
    if cleanup.get("destroyed") is not True:
        raise RuntimeError(f"Blocker cleanup did not complete: {cleanup}")
    if int(cleanup.get("deleted_leftover_blockers", -1)) != 0:
        raise RuntimeError(f"Leftover block fixtures remain: {cleanup}")
    print("pcg_block_tag_staticmesh_exclusion_verify_complete=True")
    print(f"pcg_block_tag_staticmesh_exclusion_pass={report.get('pass')}")
    print(f"pcg_block_tag_staticmesh_exclusion_native_graph_pass={report.get('native_graph_exclusion_pass')}")
    print(f"pcg_block_tag_staticmesh_exclusion_generated_total={raw.get('generated_instance_total')}")
    print(f"pcg_block_tag_staticmesh_exclusion_mesh_override_mode={mesh_update.get('mode')}")
    print(f"pcg_block_tag_staticmesh_exclusion_raw_overlap={raw.get('block_overlap_violation_count')}")
    print(f"pcg_block_tag_staticmesh_exclusion_python_removed={prune.get('total_removed')}")
    print(f"pcg_block_tag_staticmesh_exclusion_final_overlap={fixed.get('block_overlap_violation_count')}")


if __name__ == "__main__":
    main()
