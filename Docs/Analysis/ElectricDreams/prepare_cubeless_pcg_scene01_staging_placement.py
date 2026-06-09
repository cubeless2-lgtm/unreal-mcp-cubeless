import gc
import pathlib
import sys

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\prepare_cubeless_pcg_scene01_staging_placement.py",
    )
).parent
VERIFY_SCRIPT = SCRIPT_DIR / "verify_cubeless_pcg_scene01_staging_placement.py"


def main():
    namespace = {
        "__name__": "_cubeless_pcg_scene01_staging_verify",
        "__file__": str(VERIFY_SCRIPT),
        "VALIDATION_MODE": "prepare",
    }
    with open(VERIFY_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(VERIFY_SCRIPT), "exec")
    exec(code, namespace)
    namespace["main"]()
    for attr_name in ("last_type", "last_value", "last_traceback"):
        try:
            if hasattr(sys, attr_name):
                setattr(sys, attr_name, None)
        except Exception:
            pass
    gc.collect()
    collect_garbage = getattr(getattr(unreal, "SystemLibrary", None), "collect_garbage", None)
    if collect_garbage:
        collect_garbage()


if __name__ == "__main__":
    main()
