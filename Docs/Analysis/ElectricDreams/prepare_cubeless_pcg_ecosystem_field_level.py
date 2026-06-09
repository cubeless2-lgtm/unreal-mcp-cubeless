import pathlib


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\prepare_cubeless_pcg_ecosystem_field_level.py",
    )
).parent
VERIFY_SCRIPT = SCRIPT_DIR / "verify_save_cubeless_pcg_ecosystem_field_level.py"


def main():
    namespace = {
        "__name__": "_cubeless_pcg_ecosystem_field_verify_save",
        "__file__": str(VERIFY_SCRIPT),
        "VALIDATION_MODE": "prepare",
    }
    with open(VERIFY_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(VERIFY_SCRIPT), "exec")
    exec(code, namespace)
    namespace["main"]()


if __name__ == "__main__":
    main()
