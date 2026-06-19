import pathlib


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_pcg_runtime_candidate_landscape_validation.py",
    )
).parent
LANDSCAPE_VERIFIER_SCRIPT = SCRIPT_DIR / "verify_cubeless_pcg_production_candidate_landscape_validation.py"

RUNTIME_BLUEPRINT_NAME = "BP_Cubeless_PCG_EcosystemRuntime"
RUNTIME_BLUEPRINT_OBJECT = (
    "/Game/Cubeless/PCG/Runtime/Blueprints/"
    f"{RUNTIME_BLUEPRINT_NAME}.{RUNTIME_BLUEPRINT_NAME}"
)
RUNTIME_BLUEPRINT_CLASS = f"{RUNTIME_BLUEPRINT_OBJECT}_C"
RUNTIME_ACTOR_LABEL_PREFIX = "MCP_Cubeless_PCG_RuntimeLandscapeCandidate"
RUNTIME_VERIFY_MARKER = "MCP_CUBELESS_PCG_RUNTIME_CANDIDATE_LANDSCAPE_VERIFY_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")


def main():
    namespace = {
        "__name__": "_cubeless_pcg_production_candidate_landscape_verifier",
        "__file__": str(LANDSCAPE_VERIFIER_SCRIPT),
        "VALIDATION_MODE": VALIDATION_MODE,
    }
    with open(LANDSCAPE_VERIFIER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(LANDSCAPE_VERIFIER_SCRIPT), "exec")
    exec(code, namespace)

    namespace["ACTOR_LABEL_PREFIX"] = RUNTIME_ACTOR_LABEL_PREFIX
    namespace["VERIFY_MARKER"] = RUNTIME_VERIFY_MARKER

    original_load_production_verifier = namespace["load_production_verifier"]

    def load_runtime_verifier():
        verifier = original_load_production_verifier()
        verifier["BLUEPRINT_PATH"] = RUNTIME_BLUEPRINT_OBJECT
        verifier["BLUEPRINT_CLASS_PATH"] = RUNTIME_BLUEPRINT_CLASS
        return verifier

    namespace["load_production_verifier"] = load_runtime_verifier
    namespace["main"]()
    print(f"runtime_landscape_validation_mode={VALIDATION_MODE}")
    print("runtime_landscape_validation_wrapper_complete=True")


if __name__ == "__main__":
    main()
