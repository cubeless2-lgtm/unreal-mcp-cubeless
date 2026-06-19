import pathlib


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "prepare_cubeless_pcg_ecosystem_tuning_gallery.py",
    )
).parent
VERIFY_SCRIPT = SCRIPT_DIR / "verify_cubeless_pcg_ecosystem_tuning_gallery.py"


def main():
    namespace = {
        "__name__": "_cubeless_pcg_ecosystem_tuning_gallery_prepare",
        "__file__": str(VERIFY_SCRIPT),
        "VALIDATION_MODE": "prepare",
        "SAVE_ON_VERIFY": True,
    }
    with VERIFY_SCRIPT.open("r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(VERIFY_SCRIPT), "exec")
    exec(code, namespace)
    namespace["main"]()


if __name__ == "__main__":
    main()
