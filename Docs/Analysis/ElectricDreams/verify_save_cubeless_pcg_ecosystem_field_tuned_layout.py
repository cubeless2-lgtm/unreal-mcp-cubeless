import pathlib


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_save_cubeless_pcg_ecosystem_field_tuned_layout.py",
    )
).parent
FIELD_LAYOUT_SCRIPT = SCRIPT_DIR / "verify_save_cubeless_pcg_ecosystem_field_layout_refine.py"

TARGET_LEVEL = "/Game/Cubeless/Map/LVL_Cubeless_PCG_Ecosystem_Field"
VERIFY_MARKER = "MCP_CUBELESS_PCG_ECOSYSTEM_FIELD_TUNED_LAYOUT_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")
SAVE_ON_VERIFY = bool(globals().get("SAVE_ON_VERIFY", True))

ACTOR_SPECS = [
    {
        "label": "Cubeless_PCG_EcosystemRuntime_DenseMeadowWest",
        "xy": (11200.0, 11800.0),
        "preset_type": 1,
        "density_override": 3,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_DenseMeadowCenter",
        "xy": (12000.0, 12000.0),
        "preset_type": 1,
        "density_override": 3,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_DenseMeadowEast",
        "xy": (12800.0, 12150.0),
        "preset_type": 1,
        "density_override": 3,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_GroundFoliageSouthWestWarm",
        "xy": (11200.0, 11600.0),
        "preset_type": 2,
        "density_override": 0,
        "tree_override": 1,
        "material_mood": 3,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_GroundFoliageSouthWarm",
        "xy": (12000.0, 11600.0),
        "preset_type": 2,
        "density_override": 0,
        "tree_override": 1,
        "material_mood": 3,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_GroundFoliageSouthEastWarm",
        "xy": (12800.0, 11750.0),
        "preset_type": 2,
        "density_override": 0,
        "tree_override": 1,
        "material_mood": 3,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_RockyCoolEdgeEastNorth",
        "xy": (13600.0, 12200.0),
        "preset_type": 3,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 2,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_RockyCoolEdgeEastSouth",
        "xy": (13600.0, 11600.0),
        "preset_type": 3,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 2,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_ConiferGroveNorthWest",
        "xy": (11200.0, 12600.0),
        "preset_type": 4,
        "density_override": 0,
        "tree_override": 4,
        "material_mood": 3,
        "debug_material_preview": False,
    },
    {
        "label": "Cubeless_PCG_EcosystemRuntime_ConiferGroveNorthEast",
        "xy": (12800.0, 12600.0),
        "preset_type": 4,
        "density_override": 0,
        "tree_override": 4,
        "material_mood": 3,
        "debug_material_preview": False,
    },
]


def load_field_layout_namespace():
    namespace = {
        "__name__": "_cubeless_pcg_ecosystem_field_tuned_layout",
        "__file__": str(FIELD_LAYOUT_SCRIPT),
        "TARGET_LEVEL": TARGET_LEVEL,
        "VERIFY_MARKER": VERIFY_MARKER,
        "VALIDATION_MODE": VALIDATION_MODE,
        "SAVE_ON_VERIFY": SAVE_ON_VERIFY,
        "ACTOR_SPECS": ACTOR_SPECS,
    }
    with FIELD_LAYOUT_SCRIPT.open("r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(FIELD_LAYOUT_SCRIPT), "exec")
    exec(code, namespace)
    namespace["TARGET_LEVEL"] = TARGET_LEVEL
    namespace["VERIFY_MARKER"] = VERIFY_MARKER
    namespace["VALIDATION_MODE"] = VALIDATION_MODE
    namespace["SAVE_ON_VERIFY"] = SAVE_ON_VERIFY
    namespace["ACTOR_SPECS"] = ACTOR_SPECS
    return namespace


def main():
    print(VERIFY_MARKER)
    print(f"field_tuned_layout_mode={VALIDATION_MODE}")
    namespace = load_field_layout_namespace()
    namespace["main"]()
    print(f"field_tuned_layout_actor_count={len(ACTOR_SPECS)}")
    print("cubeless_pcg_field_tuned_layout_complete=True")


if __name__ == "__main__":
    main()
