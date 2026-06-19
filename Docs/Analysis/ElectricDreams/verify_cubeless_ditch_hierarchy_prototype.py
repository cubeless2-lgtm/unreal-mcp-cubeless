import pathlib


SCRIPT_DIR = pathlib.Path(
    globals().get("__file__", pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ditch_hierarchy_prototype.py")
).parent
BASE_VERIFIER_SCRIPT = SCRIPT_DIR / "verify_spline_assembly_output.py"
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ditch_hierarchy_prototype.py"
BUILD_MARKER = "MCP_CUBELESS_DITCH_HIERARCHY_PROTOTYPE_BUILD_BEGIN"
VERIFY_MARKER = "MCP_CUBELESS_DITCH_HIERARCHY_PROTOTYPE_VERIFY_BEGIN"


def load_script(path, name):
    namespace = {"__name__": name}
    with open(path, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(path), "exec")
    exec(code, namespace)
    return namespace


def main():
    builder_config = load_script(BUILDER_SCRIPT, "_cubeless_ditch_hierarchy_builder_config")
    verifier = load_script(BASE_VERIFIER_SCRIPT, "_cubeless_ditch_hierarchy_base_verifier")
    original_scan_latest_log = verifier["scan_latest_log"]

    def scan_latest_log_from_production_marker(_marker):
        return original_scan_latest_log(BUILD_MARKER)

    verifier["BUILDER_CONFIG_OVERRIDE"] = builder_config
    verifier["VERIFY_MARKER"] = VERIFY_MARKER
    verifier["scan_latest_log"] = scan_latest_log_from_production_marker
    verifier["main"]()


if __name__ == "__main__":
    main()
