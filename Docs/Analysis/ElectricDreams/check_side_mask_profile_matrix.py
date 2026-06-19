import pathlib
from collections import Counter


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "check_side_mask_profile_matrix.py",
    )
).resolve().parent

BUILDER_SCRIPT = str(SCRIPT_DIR / "build_spline_assembly_with_post_copy_offset.py")
VERIFY_SCRIPT = str(SCRIPT_DIR / "verify_spline_assembly_output.py")

SIDE_MASK_PROFILES_TO_CHECK = [
    "all_after_copy",
    "left_only_after_copy",
    "center_only_after_copy",
    "right_only_after_copy",
    "center_right_after_copy",
]


def load_script(path, name):
    namespace = {"__name__": name}
    with open(path, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), path, "exec")
    exec(code, namespace)
    return namespace


def scaled_counts(counter, target_count):
    return {key: value * target_count for key, value in sorted(counter.items())}


def main():
    builder = load_script(BUILDER_SCRIPT, "_pcg_side_mask_matrix_builder")
    verifier = load_script(VERIFY_SCRIPT, "_pcg_side_mask_matrix_verifier")
    source_assembly = builder["get_source_assembly"]()
    target_count = int(builder["TARGET_SAMPLE_COUNT"])
    noise_min = float(builder["branch_density_noise_min"]())
    noise_max = float(builder["branch_density_noise_max"]())
    density_threshold = float(builder["branch_density_filter_threshold"]())
    density_value = builder["branch_density_value"]
    results = []

    print("MCP_PCG_SIDE_MASK_PROFILE_MATRIX_BEGIN")
    for profile in SIDE_MASK_PROFILES_TO_CHECK:
        builder["SIDE_MASK_FILTER_PROFILE_OVERRIDE"] = profile
        side_spec = builder["side_filter_profile_spec"]()
        side_survivors, side_pruned, side_parent_gaps = verifier["classify_side_filter"](
            source_assembly,
            builder["graph_side_filter_allows"],
        )
        survivors, density_pruned, ambiguous, survivor_parent_gaps = verifier["classify_pruning"](
            side_survivors,
            noise_min,
            noise_max,
            density_threshold,
            density_value,
        )
        density_counts = scaled_counts(
            Counter(round(float(density_value(spec)), 3) for spec in survivors),
            target_count,
        )
        side_mask_counts = scaled_counts(
            Counter(round(float(builder["side_mask_value"](spec["side"])), 3) for spec in survivors),
            target_count,
        )
        row = {
            "profile": profile,
            "operator": side_spec["operator"],
            "threshold": side_spec["threshold"],
            "allowed_sides": list(side_spec["allowed_sides"]),
            "source_survivors": len(survivors),
            "side_pruned_sources": len(side_pruned),
            "density_pruned_sources": len(density_pruned),
            "expected_points": len(survivors) * target_count,
            "side_parent_gaps": len(side_parent_gaps),
            "survivor_parent_gaps": len(survivor_parent_gaps),
            "ambiguous_density_sources": len(ambiguous),
            "density_counts": density_counts,
            "side_mask_counts": side_mask_counts,
        }
        row["preflight_pass"] = all([
            row["expected_points"] > 0,
            row["density_pruned_sources"] > 0,
            row["side_parent_gaps"] == 0,
            row["survivor_parent_gaps"] == 0,
            row["ambiguous_density_sources"] == 0,
        ])
        results.append(row)
        print(f"profile={profile}")
        print(f"  operator={row['operator']} threshold={row['threshold']} allowed_sides={row['allowed_sides']}")
        print(
            "  source_survivors={source_survivors} side_pruned_sources={side_pruned_sources} "
            "density_pruned_sources={density_pruned_sources} expected_points={expected_points}".format(**row)
        )
        print(
            "  side_parent_gaps={side_parent_gaps} survivor_parent_gaps={survivor_parent_gaps} "
            "ambiguous_density_sources={ambiguous_density_sources} preflight_pass={preflight_pass}".format(**row)
        )
        print(f"  side_mask_counts={side_mask_counts}")
        print(f"  density_counts={density_counts}")

    failed = [row["profile"] for row in results if not row["preflight_pass"]]
    print(f"MCP_PCG_SIDE_MASK_PROFILE_MATRIX_FAILED={failed}")
    print("MCP_PCG_SIDE_MASK_PROFILE_MATRIX_END")
    if failed:
        raise RuntimeError(f"SideMask profile matrix preflight failed: {failed}")


if __name__ == "__main__":
    main()
