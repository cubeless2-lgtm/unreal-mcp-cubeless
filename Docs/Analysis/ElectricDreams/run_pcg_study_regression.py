import pathlib
import time
import traceback


SCRIPT_DIR = pathlib.Path(__file__).resolve().parent
SUPPRESS_FINAL_RAISE = bool(globals().get("PCG_STUDY_REGRESSION_SUPPRESS_FINAL_RAISE", False))
REGRESSION_PHASE = str(globals().get("PCG_STUDY_REGRESSION_PHASE", "all"))
REGRESSION_STEP_FILTER = str(globals().get("PCG_STUDY_REGRESSION_STEP", ""))
AUTO_REGRESSION_PHASES = {"build", "verify"}

REGRESSION_STEPS = [
    (
        "build",
        "main_spline_assembly_build",
        "build_spline_assembly_with_post_copy_offset.py",
    ),
    (
        "verify",
        "main_spline_assembly_verify",
        "verify_spline_assembly_output.py",
    ),
    (
        "build",
        "self_pruning_fixture_build",
        "build_ground_self_pruning_fixture.py",
    ),
    (
        "verify",
        "self_pruning_fixture_verify",
        "verify_ground_self_pruning_fixture.py",
    ),
    (
        "build",
        "density_bounds_fixture_build",
        "build_ground_density_bounds_fixture.py",
    ),
    (
        "verify",
        "density_bounds_fixture_verify",
        "verify_ground_density_bounds_fixture.py",
    ),
    (
        "build",
        "ground_combo_fixture_build",
        "build_ground_combo_fixture.py",
    ),
    (
        "verify",
        "ground_combo_fixture_verify",
        "verify_ground_combo_fixture.py",
    ),
    (
        "verify",
        "dynamic_material_axis_actor_property_compat_verify",
        "verify_cubeless_ed_dynamic_material_axis_actor_property_selector_compat.py",
    ),
    (
        "verify",
        "dynamic_material_axis_menu_apply_verify",
        "verify_cubeless_ed_dynamic_material_axis_menu_apply.py",
    ),
    (
        "verify",
        "true_material_applied_presets_verify",
        "verify_cubeless_ed_true_material_applied_presets.py",
    ),
    (
        "build",
        "material_override_selector_prepare",
        "prepare_cubeless_ed_material_override_selector_validation.py",
    ),
    (
        "verify",
        "material_override_selector_verify",
        "verify_cubeless_ed_material_override_selector_blueprint.py",
    ),
    (
        "build",
        "ecosystem_selector_prepare",
        "prepare_cubeless_ed_ecosystem_selector_validation.py",
    ),
    (
        "verify",
        "ecosystem_selector_verify",
        "verify_cubeless_ed_ecosystem_selector_blueprint.py",
    ),
    (
        "build",
        "production_candidate_prepare",
        "prepare_cubeless_pcg_production_candidate_validation.py",
    ),
    (
        "verify",
        "production_candidate_verify",
        "verify_cubeless_pcg_production_candidate_blueprint.py",
    ),
    (
        "build",
        "runtime_candidate_promote",
        "promote_cubeless_pcg_runtime_candidate_blueprint.py",
    ),
    (
        "build",
        "runtime_candidate_prepare",
        "prepare_cubeless_pcg_runtime_candidate_validation.py",
    ),
    (
        "verify",
        "runtime_candidate_verify",
        "verify_cubeless_pcg_runtime_candidate_blueprint.py",
    ),
    (
        "verify",
        "ecosystem_field_level_verify",
        "verify_cubeless_pcg_ecosystem_field_level.py",
    ),
    (
        "verify",
        "ecosystem_field_topdown_qa",
        "export_cubeless_pcg_ecosystem_field_topdown_qa.py",
    ),
    (
        "build",
        "ecosystem_tuning_gallery_prepare",
        "prepare_cubeless_pcg_ecosystem_tuning_gallery.py",
    ),
    (
        "verify",
        "ecosystem_tuning_gallery_verify",
        "verify_cubeless_pcg_ecosystem_tuning_gallery.py",
    ),
    (
        "build",
        "intent_gallery_prepare",
        "prepare_cubeless_pcg_intent_gallery.py",
    ),
    (
        "verify",
        "intent_gallery_verify",
        "verify_cubeless_pcg_intent_gallery.py",
    ),
    (
        "deferred_prepare",
        "runtime_road_native_smoke_prepare",
        "prepare_cubeless_pcg_runtime_road_native_smoke.py",
    ),
    (
        "deferred_verify",
        "runtime_road_native_smoke_verify",
        "verify_cubeless_pcg_runtime_road_native_smoke.py",
    ),
    (
        "deferred_prepare",
        "runtime_actor_property_override_prepare",
        "prepare_cubeless_pcg_runtime_actor_property_override_validation.py",
    ),
    (
        "deferred_verify",
        "runtime_actor_property_override_verify",
        "verify_cubeless_pcg_runtime_actor_property_override_validation.py",
    ),
    (
        "verify",
        "production_promotion_target_audit",
        "audit_cubeless_pcg_production_promotion_targets.py",
    ),
]


def run_script(step_name, relative_script):
    script_path = SCRIPT_DIR / relative_script
    if not script_path.exists():
        raise RuntimeError(f"Missing regression script for {step_name}: {script_path}")

    started = time.perf_counter()
    namespace = {
        "__name__": "__main__",
        "__file__": str(script_path),
    }
    with script_path.open("r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(script_path), "exec")
    exec(code, namespace)
    elapsed = time.perf_counter() - started
    return elapsed


def main():
    print("MCP_PCG_STUDY_REGRESSION_BEGIN")
    print(f"regression_phase={REGRESSION_PHASE}")
    print(f"regression_step_filter={REGRESSION_STEP_FILTER}")
    if REGRESSION_PHASE == "all":
        print(
            "regression_phase_note=all runs build and verify in one Unreal Python call; "
            "use separate build then verify phases when generated graph output is delayed"
        )
        print(
            "regression_deferred_note=deferred_prepare/deferred_verify steps are skipped "
            "by all unless explicitly requested by phase or step filter"
        )
    results = []
    failures = []
    started = time.perf_counter()

    selected_steps = [
        (phase, step_name, relative_script)
        for phase, step_name, relative_script in REGRESSION_STEPS
        if (
            (REGRESSION_PHASE == "all" and phase in AUTO_REGRESSION_PHASES)
            or phase == REGRESSION_PHASE
            or (
                REGRESSION_PHASE == "all"
                and REGRESSION_STEP_FILTER
                and (step_name == REGRESSION_STEP_FILTER or relative_script == REGRESSION_STEP_FILTER)
            )
        )
    ]
    if REGRESSION_STEP_FILTER:
        selected_steps = [
            (phase, step_name, relative_script)
            for phase, step_name, relative_script in selected_steps
            if step_name == REGRESSION_STEP_FILTER or relative_script == REGRESSION_STEP_FILTER
        ]
    if not selected_steps:
        raise RuntimeError(
            f"No regression steps selected for phase={REGRESSION_PHASE!r} "
            f"step={REGRESSION_STEP_FILTER!r}"
        )

    for phase, step_name, relative_script in selected_steps:
        print(f"regression_step_begin={step_name}|{relative_script}")
        try:
            elapsed = run_script(step_name, relative_script)
            results.append((phase, step_name, relative_script, "PASS", elapsed, ""))
            print(f"regression_step_result={step_name}|PASS|{elapsed:.3f}s")
        except Exception as exc:
            elapsed = 0.0
            message = "".join(traceback.format_exception_only(type(exc), exc)).strip()
            failures.append((step_name, relative_script, message))
            results.append((phase, step_name, relative_script, "FAIL", elapsed, message))
            print(f"regression_step_result={step_name}|FAIL|{message}")
            print(traceback.format_exc())

    total_elapsed = time.perf_counter() - started
    pass_count = sum(1 for _, _, _, status, _, _ in results if status == "PASS")
    fail_count = len(failures)

    print("regression_summary=")
    for phase, step_name, relative_script, status, elapsed, message in results:
        if status == "PASS":
            print(f"  {phase}|{step_name}|{relative_script}|{status}|{elapsed:.3f}s")
        else:
            print(f"  {phase}|{step_name}|{relative_script}|{status}|{message}")

    print(f"regression_pass_count={pass_count}")
    print(f"regression_fail_count={fail_count}")
    print(f"regression_total_elapsed={total_elapsed:.3f}s")
    print(f"pcg_study_regression_pass={fail_count == 0}")
    print("MCP_PCG_STUDY_REGRESSION_END")

    if failures and not SUPPRESS_FINAL_RAISE:
        failed_names = ", ".join(step_name for step_name, _, _ in failures)
        raise RuntimeError(f"PCG study regression failed: {failed_names}")


if __name__ == "__main__":
    main()
