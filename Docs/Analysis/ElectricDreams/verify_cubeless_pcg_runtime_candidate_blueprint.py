import pathlib


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\verify_cubeless_pcg_runtime_candidate_blueprint.py",
    )
).parent
PRODUCTION_VERIFIER_SCRIPT = SCRIPT_DIR / "verify_cubeless_pcg_production_candidate_blueprint.py"

RUNTIME_BLUEPRINT_NAME = "BP_Cubeless_PCG_EcosystemRuntime"
RUNTIME_BLUEPRINT_OBJECT = (
    "/Game/Cubeless/PCG/Runtime/Blueprints/"
    f"{RUNTIME_BLUEPRINT_NAME}.{RUNTIME_BLUEPRINT_NAME}"
)
RUNTIME_BLUEPRINT_CLASS = f"{RUNTIME_BLUEPRINT_OBJECT}_C"
RUNTIME_VALIDATION_LEVEL = "/Game/_MCP_Temp/PCG/LVL_Cubeless_PCG_RuntimeCandidate_MCP"
RUNTIME_ACTOR_LABEL_PREFIX = "MCP_Cubeless_PCG_RuntimeCandidate"
RUNTIME_VERIFY_MARKER = "MCP_CUBELESS_PCG_RUNTIME_CANDIDATE_VERIFY_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")


def main():
    namespace = {
        "__name__": "_cubeless_pcg_production_candidate_verifier",
        "__file__": str(PRODUCTION_VERIFIER_SCRIPT),
        "VALIDATION_MODE": VALIDATION_MODE,
    }
    with open(PRODUCTION_VERIFIER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(PRODUCTION_VERIFIER_SCRIPT), "exec")
    exec(code, namespace)

    namespace["BLUEPRINT_PATH"] = RUNTIME_BLUEPRINT_OBJECT
    namespace["BLUEPRINT_CLASS_PATH"] = RUNTIME_BLUEPRINT_CLASS
    namespace["LEVEL"] = RUNTIME_VALIDATION_LEVEL
    namespace["ACTOR_LABEL_PREFIX"] = RUNTIME_ACTOR_LABEL_PREFIX
    namespace["VERIFY_MARKER"] = RUNTIME_VERIFY_MARKER
    namespace["main"]()
    print(f"runtime_candidate_validation_mode={VALIDATION_MODE}")
    print("runtime_candidate_validation_wrapper_complete=True")


if __name__ == "__main__":
    main()
