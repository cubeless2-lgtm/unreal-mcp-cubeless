import pathlib


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\verify_cubeless_pcg_ecosystem_field_level.py",
    )
).parent
FIELD_VERIFY_SCRIPT = SCRIPT_DIR / "verify_save_cubeless_pcg_ecosystem_field_tuned_layout.py"


def main():
    namespace = {
        "__name__": "_cubeless_pcg_ecosystem_field_readonly_verify",
        "__file__": str(FIELD_VERIFY_SCRIPT),
        "VALIDATION_MODE": "verify",
        "SAVE_ON_VERIFY": False,
    }
    with open(FIELD_VERIFY_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(FIELD_VERIFY_SCRIPT), "exec")
    exec(code, namespace)
    namespace["main"]()
    print("ecosystem_field_readonly_verify_complete=True")


if __name__ == "__main__":
    main()
