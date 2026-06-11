import pathlib

import unreal


PROJECT_SCRIPT = (
    pathlib.Path(unreal.Paths.project_dir()).resolve()
    / "Tools"
    / "Unreal"
    / "validate_pcg_runtime_actor_property_overrides.py"
)


def main():
    namespace = {
        "__name__": "__main__",
        "__file__": str(PROJECT_SCRIPT),
        "VALIDATION_MODE": "verify_cleanup",
    }
    with PROJECT_SCRIPT.open("r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(PROJECT_SCRIPT), "exec")
    exec(code, namespace)
    print("runtime_actor_property_override_verify_complete=True")


if __name__ == "__main__":
    main()
