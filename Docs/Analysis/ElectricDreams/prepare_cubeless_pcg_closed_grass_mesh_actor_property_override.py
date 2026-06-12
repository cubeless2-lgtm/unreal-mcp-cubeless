import pathlib

import unreal


SCRIPT_PATH = (
    pathlib.Path(unreal.Paths.project_dir())
    / "Tools"
    / "Unreal"
    / "validate_pcg_closed_spline_grass_mesh_actor_property_override.py"
)


def main():
    if not SCRIPT_PATH.exists():
        raise RuntimeError(
            f"Missing Cubeless closed grass mesh override script: {SCRIPT_PATH}"
        )
    namespace = {"__name__": "__main__", "__file__": str(SCRIPT_PATH)}
    with SCRIPT_PATH.open("r", encoding="utf-8") as handle:
        exec(compile(handle.read(), str(SCRIPT_PATH), "exec"), namespace)
    print("pcg_closed_grass_mesh_actor_property_override_scheduled=True")
    print(
        "pcg_closed_grass_mesh_actor_property_override_note="
        "run deferred_verify after Unreal has ticked long enough for PCG generation"
    )


if __name__ == "__main__":
    main()
