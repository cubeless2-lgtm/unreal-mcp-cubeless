import json
import pathlib

import unreal


PROJECT_AUDIT_SCRIPT = (
    pathlib.Path(unreal.Paths.project_dir()).resolve()
    / "Tools"
    / "Unreal"
    / "audit_pcg_static_mesh_spawner_actor_property_overrides.py"
)
REPORT_PATH = (
    pathlib.Path(unreal.Paths.project_saved_dir()).resolve()
    / "MCP_PCG"
    / "CubelessPCGStaticMeshSpawnerActorPropertyAudit_Report.json"
)


def _require_int(report, key, expected=None):
    if key not in report:
        raise RuntimeError(f"Missing audit report key: {key}")
    try:
        value = int(report.get(key))
    except Exception as exc:
        raise RuntimeError(f"Audit report key is not an int: {key}={report.get(key)!r}") from exc
    if expected is not None and value != expected:
        raise RuntimeError(f"Unexpected audit report value: {key}={value}, expected={expected}")
    return value


def _run_project_audit():
    if not PROJECT_AUDIT_SCRIPT.exists():
        raise RuntimeError(f"Missing project audit script: {PROJECT_AUDIT_SCRIPT}")
    namespace = {
        "__name__": "__main__",
        "__file__": str(PROJECT_AUDIT_SCRIPT),
        "AUDIT_PRINT_FULL_REPORT": False,
    }
    with PROJECT_AUDIT_SCRIPT.open("r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(PROJECT_AUDIT_SCRIPT), "exec")
    exec(code, namespace)


def _read_report():
    if not REPORT_PATH.exists():
        raise RuntimeError(f"Missing StaticMeshSpawner actor-property audit report: {REPORT_PATH}")
    return json.loads(REPORT_PATH.read_text(encoding="utf-8"))


def _verify_policy(report):
    policy = report.get("policy") or {}
    if policy.get("loaded") is not True:
        raise RuntimeError(f"StaticMeshSpawner audit policy was not loaded: {policy}")
    if policy.get("load_error"):
        raise RuntimeError(f"StaticMeshSpawner audit policy load error: {policy.get('load_error')}")
    if int(policy.get("version", 0)) < 1:
        raise RuntimeError(f"Unexpected StaticMeshSpawner audit policy version: {policy}")
    if int(policy.get("legacy_learning_allowlist_count", 0)) <= 0:
        raise RuntimeError(f"StaticMeshSpawner audit policy has no legacy allowlist: {policy}")
    if "cleanup_candidate_count" not in policy:
        raise RuntimeError(f"StaticMeshSpawner audit policy has no cleanup candidate count: {policy}")
    return policy


def main():
    _run_project_audit()
    report = _read_report()
    policy = _verify_policy(report)

    actionable_graphs = _require_int(
        report,
        "actionable_graphs_needing_actor_property_review",
        expected=0,
    )
    actionable_spawners = _require_int(
        report,
        "actionable_review_spawner_count",
        expected=0,
    )
    production_graphs = _require_int(
        report,
        "production_graphs_needing_actor_property_review",
        expected=0,
    )
    production_spawners = _require_int(
        report,
        "production_review_spawner_count",
        expected=0,
    )
    cleanup_graphs = _require_int(report, "cleanup_candidate_graph_count")
    cleanup_spawners = _require_int(report, "cleanup_candidate_spawner_count")

    print("static_mesh_spawner_actor_property_audit_verify_complete=True")
    print(f"static_mesh_spawner_actor_property_audit_policy_version={policy.get('version')}")
    print(
        "static_mesh_spawner_actor_property_audit_policy_counts="
        f"allowlist={policy.get('legacy_learning_allowlist_count')}"
        f"|cleanup_candidates={policy.get('cleanup_candidate_count')}"
    )
    print(f"static_mesh_spawner_actor_property_audit_actionable_graphs={actionable_graphs}")
    print(f"static_mesh_spawner_actor_property_audit_actionable_spawners={actionable_spawners}")
    print(f"static_mesh_spawner_actor_property_audit_production_graphs={production_graphs}")
    print(f"static_mesh_spawner_actor_property_audit_production_spawners={production_spawners}")
    print(f"static_mesh_spawner_actor_property_audit_cleanup_graphs={cleanup_graphs}")
    print(f"static_mesh_spawner_actor_property_audit_cleanup_spawners={cleanup_spawners}")


if __name__ == "__main__":
    main()
