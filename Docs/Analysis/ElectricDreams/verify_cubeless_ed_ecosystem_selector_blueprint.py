import importlib
import pathlib
import sys

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        pathlib.Path.cwd() / "Docs" / "Analysis" / "ElectricDreams" / "verify_cubeless_ed_ecosystem_selector_blueprint.py",
    )
).parent
STYLE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_style_profile_matrix_presets.py"
TREE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_tree_profile_presets.py"
MATERIAL_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_material_override_presets.py"

PROJECT_ROOT = pathlib.Path(
    globals().get(
        "PROJECT_ROOT",
        __import__("os").environ.get(
            "CUBELESS_PROJECT_ROOT",
            SCRIPT_DIR.parents[2].parent / "CubelessStylized",
        ),
    )
).resolve()

PROJECT_PLUGIN_PYTHON = (PROJECT_ROOT / "Plugins" / "CustomTools" / "Content" / "Python").as_posix()
BLUEPRINT_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGEcosystemSelector.BP_Cubeless_ED_PCGEcosystemSelector"
)
BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGEcosystemSelector.BP_Cubeless_ED_PCGEcosystemSelector_C"
)
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_EcosystemSelector"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0
VERIFY_MARKER = "MCP_CUBELESS_ED_ECOSYSTEM_SELECTOR_VERIFY_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")

VALIDATION_SPECS = [
    {
        "name": "Combined_GroundFoliage_Both_GroundNormal_DitchSparse_ColumnSparse_MaterialRockCool",
        "ecosystem_mode": 3,
        "visual_style_type": 4,
        "profile_mode": 3,
        "ground_amount_type": 2,
        "ditch_amount_type": 1,
        "tree_style_type": 2,
        "tree_amount_type": 2,
        "material_domain_type": 2,
        "material_variant_type": 2,
    },
    {
        "name": "Combined_ClassicGrass_GroundOnly_GroundDense_CompactSolo_MaterialLeafWarm",
        "ecosystem_mode": 3,
        "visual_style_type": 1,
        "profile_mode": 1,
        "ground_amount_type": 3,
        "ditch_amount_type": 2,
        "tree_style_type": 1,
        "tree_amount_type": 1,
        "material_domain_type": 1,
        "material_variant_type": 3,
    },
    {
        "name": "NoPreview_Combined_ClassicGrass_GroundOnly_GroundDense_CompactSolo_MaterialLeafWarm",
        "ecosystem_mode": 3,
        "visual_style_type": 1,
        "profile_mode": 1,
        "ground_amount_type": 3,
        "ditch_amount_type": 2,
        "tree_style_type": 1,
        "tree_amount_type": 1,
        "material_domain_type": 1,
        "material_variant_type": 3,
        "generate_material_preview": False,
    },
    {
        "name": "StyleOnly_SmallRocks_DitchOnly_DitchNormal_MaterialLeafWarm",
        "ecosystem_mode": 1,
        "visual_style_type": 5,
        "profile_mode": 2,
        "ground_amount_type": 2,
        "ditch_amount_type": 2,
        "tree_style_type": 3,
        "tree_amount_type": 3,
        "material_domain_type": 1,
        "material_variant_type": 3,
    },
    {
        "name": "TreeOnly_MixedConifer_LightGrove_MaterialLeafCool",
        "ecosystem_mode": 2,
        "visual_style_type": 1,
        "profile_mode": 3,
        "ground_amount_type": 2,
        "ditch_amount_type": 2,
        "tree_style_type": 3,
        "tree_amount_type": 3,
        "material_domain_type": 1,
        "material_variant_type": 2,
    },
    {
        "name": "TrueStyle_GroundFoliage_Both_GroundNormal_DitchSparse_MaterialLeafCool",
        "ecosystem_mode": 1,
        "visual_style_type": 4,
        "profile_mode": 3,
        "ground_amount_type": 2,
        "ditch_amount_type": 1,
        "tree_style_type": 2,
        "tree_amount_type": 2,
        "material_domain_type": 1,
        "material_variant_type": 2,
    },
    {
        "name": "TrueStyle_SmallRocks_GroundOnly_GroundSparse_MaterialRockDark",
        "ecosystem_mode": 1,
        "visual_style_type": 5,
        "profile_mode": 1,
        "ground_amount_type": 1,
        "ditch_amount_type": 2,
        "tree_style_type": 3,
        "tree_amount_type": 3,
        "material_domain_type": 2,
        "material_variant_type": 3,
    },
    {
        "name": "TrueTree_CompactConifer_Sparse_MaterialPineDark",
        "ecosystem_mode": 2,
        "visual_style_type": 1,
        "profile_mode": 3,
        "ground_amount_type": 2,
        "ditch_amount_type": 2,
        "tree_style_type": 1,
        "tree_amount_type": 2,
        "material_domain_type": 3,
        "material_variant_type": 2,
    },
    {
        "name": "TrueTree_ColumnConifer_Sparse_MaterialPineSoft",
        "ecosystem_mode": 2,
        "visual_style_type": 1,
        "profile_mode": 3,
        "ground_amount_type": 2,
        "ditch_amount_type": 2,
        "tree_style_type": 2,
        "tree_amount_type": 2,
        "material_domain_type": 3,
        "material_variant_type": 3,
    },
    {
        "name": "TrueTree_MixedConifer_LightGrove_MaterialPineDark",
        "ecosystem_mode": 2,
        "visual_style_type": 1,
        "profile_mode": 3,
        "ground_amount_type": 2,
        "ditch_amount_type": 2,
        "tree_style_type": 3,
        "tree_amount_type": 3,
        "material_domain_type": 3,
        "material_variant_type": 2,
    },
]


def load_config(script_path, namespace_name):
    namespace = {"__name__": namespace_name, "__file__": str(script_path)}
    with open(script_path, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(script_path), "exec")
    exec(code, namespace)
    return namespace


def load_menu_module():
    if PROJECT_PLUGIN_PYTHON not in sys.path:
        sys.path.append(PROJECT_PLUGIN_PYTHON)
    from ArtScripts import CubelessEDPCG
    return importlib.reload(CubelessEDPCG)


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def get_current_level_path():
    subsystem_cls = getattr(unreal, "UnrealEditorSubsystem", None)
    if subsystem_cls:
        try:
            subsystem = unreal.get_editor_subsystem(subsystem_cls)
            world = subsystem.get_editor_world() if subsystem else None
            if world:
                return world.get_path_name().split(".", 1)[0]
        except Exception:
            pass
    try:
        world = unreal.EditorLevelLibrary.get_editor_world()
        if world:
            return world.get_path_name().split(".", 1)[0]
    except Exception:
        return None
    return None


def ensure_validation_level_loaded():
    if get_current_level_path() != LEVEL:
        unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)


def selector_label(spec):
    return f"{ACTOR_LABEL_PREFIX}_{spec['name']}_Validation"


def find_actor_by_label(label):
    return next((actor for actor in get_all_level_actors() if actor.get_actor_label() == label), None)


def cleanup_existing_validation_actors():
    for actor in list(get_all_level_actors()):
        if actor.get_actor_label().startswith(f"{ACTOR_LABEL_PREFIX}_"):
            unreal.EditorLevelLibrary.destroy_actor(actor)


def configure_validation_spline(actor):
    splines = actor.get_components_by_class(unreal.SplineComponent)
    if not splines:
        raise RuntimeError("Ecosystem selector actor has no SplineComponent")
    half_length = (float(TARGET_SAMPLE_COUNT) - 1.0) * float(TARGET_POINT_SPACING) * 0.5
    for spline in splines:
        spline.clear_spline_points(False)
        spline.add_spline_point(unreal.Vector(0, -half_length, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, 0, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, half_length, 0), unreal.SplineCoordinateSpace.LOCAL, True)
        spline.update_spline()


def set_int_property(actor, prop_name, value):
    actor.set_editor_property(prop_name, int(value))


def set_bool_property(actor, prop_name, value):
    actor.set_editor_property(prop_name, bool(value))


def get_bool_property(actor, prop_names, default_value=True):
    for prop_name in prop_names:
        try:
            return bool(actor.get_editor_property(prop_name))
        except Exception:
            pass
    return bool(default_value)


def normalized_style_axes(spec):
    profile_mode = int(spec["profile_mode"])
    ground_type = int(spec["ground_amount_type"])
    ditch_type = int(spec["ditch_amount_type"])
    if profile_mode == 1:
        ditch_type = 0
    elif profile_mode == 2:
        ground_type = 0
    return profile_mode, ground_type, ditch_type


def find_style_spec(style_config, spec):
    profile_mode, ground_type, ditch_type = normalized_style_axes(spec)
    for candidate in style_config["STYLE_PROFILE_MATRIX_SPECS"]:
        if (
            candidate["style_type"] == int(spec["visual_style_type"])
            and candidate["profile_mode"] == profile_mode
            and candidate["ground_amount_type"] == ground_type
            and candidate["ditch_amount_type"] == ditch_type
        ):
            return candidate
    raise RuntimeError(f"No style matrix spec for {spec}")


def find_tree_spec(tree_config, spec):
    for candidate in tree_config["TREE_PROFILE_SPECS"]:
        if (
            candidate["style_type"] == int(spec["tree_style_type"])
            and candidate["amount_type"] == int(spec["tree_amount_type"])
        ):
            return candidate
    raise RuntimeError(f"No tree profile spec for {spec}")


def find_material_spec(material_config, spec):
    for candidate in material_config["MATERIAL_OVERRIDE_SPECS"]:
        if (
            candidate["domain_type"] == int(spec["material_domain_type"])
            and candidate["variant_type"] == int(spec["material_variant_type"])
        ):
            return candidate
    raise RuntimeError(f"No material override spec for {spec}")


def expected_material_selector_graph(spec, material_spec, material_config, menu_module):
    dynamic_graph_path = None
    dynamic_graph_path_func = getattr(menu_module, "_dynamic_material_axis_graph_path", None)
    if callable(dynamic_graph_path_func):
        dynamic_graph_path = dynamic_graph_path_func(
            int(spec["material_domain_type"]),
            int(spec["material_variant_type"]),
        )
    if dynamic_graph_path and unreal.EditorAssetLibrary.load_asset(dynamic_graph_path):
        return dynamic_graph_path, "dynamic_actor_property"
    return material_config["MATERIAL_OVERRIDE_GRAPH_PATHS"][material_spec["name"]], "preset_graph"


def get_named_pcg_component(actor, name_prefix):
    for component in actor.get_components_by_class(unreal.PCGComponent):
        if component.get_name().startswith(name_prefix):
            return component
    raise RuntimeError(f"Missing PCG component {name_prefix}: {actor.get_actor_label()}")


def get_component_graph_path(component):
    graph_instance = component.get_editor_property("graph_instance")
    graph = graph_instance.get_editor_property("graph") if graph_instance else None
    return graph.get_path_name() if graph else None


def get_generated_point_count(component):
    try:
        collection = component.get_generated_graph_output()
        for item in collection.get_editor_property("tagged_data"):
            data = item.get_editor_property("data").get_editor_property("data")
            if data and hasattr(data, "get_num_points"):
                return int(data.get_num_points())
    except Exception:
        return 0
    return 0


def get_ism_rows(actor):
    rows = []
    for component in actor.get_components_by_class(unreal.InstancedStaticMeshComponent):
        mesh = component.get_editor_property("static_mesh")
        mesh_path = mesh.get_path_name() if mesh else "None"
        try:
            count = int(component.get_instance_count())
        except Exception:
            count = -1
        rows.append((component.get_name(), mesh_path, count))
    return rows


def count_instances_for_meshes(ism_rows, mesh_paths):
    expected = set(mesh_paths)
    return sum(max(0, count) for _, mesh_path, count in ism_rows if mesh_path in expected)


def meshes_are_disjoint(left, right):
    return set(left).isdisjoint(set(right))


def scan_latest_log(marker):
    log_dir = pathlib.Path(unreal.Paths.project_log_dir())
    logs = sorted(log_dir.glob("*.log"), key=lambda path: path.stat().st_mtime, reverse=True)
    if not logs:
        return None, False, []
    latest = logs[0]
    text = latest.read_text(encoding="utf-8", errors="ignore")
    idx = text.rfind(marker)
    scan_text = text[idx:] if idx >= 0 else text
    errors = [line for line in scan_text.splitlines() if "Error:" in line]
    return latest, idx >= 0, errors


def spawn_selector_actor(spec, index, menu_module):
    label = selector_label(spec)
    existing_actor = find_actor_by_label(label)
    if existing_actor:
        unreal.EditorLevelLibrary.destroy_actor(existing_actor)

    actor_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not actor_class:
        raise RuntimeError(f"Missing ecosystem selector Blueprint class: {BLUEPRINT_CLASS_PATH}")

    row = index // 2
    column = index % 2
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(54000 + column * 3600, row * 3600, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(label)
    for prop_name in (
        "EcosystemMode",
        "VisualStyleType",
        "ProfileMode",
        "GroundAmountType",
        "DitchAmountType",
        "TreeStyleType",
        "TreeAmountType",
        "MaterialDomainType",
        "MaterialVariantType",
    ):
        key = prop_name[0].lower() + prop_name[1:]
        snake_key = {
            "EcosystemMode": "ecosystem_mode",
            "VisualStyleType": "visual_style_type",
            "ProfileMode": "profile_mode",
            "GroundAmountType": "ground_amount_type",
            "DitchAmountType": "ditch_amount_type",
            "TreeStyleType": "tree_style_type",
            "TreeAmountType": "tree_amount_type",
            "MaterialDomainType": "material_domain_type",
            "MaterialVariantType": "material_variant_type",
        }[prop_name]
        set_int_property(actor, prop_name, spec.get(snake_key, spec.get(key)))
    set_bool_property(actor, "GenerateMaterialPreview", spec.get("generate_material_preview", True))
    configure_validation_spline(actor)
    apply_result = menu_module.apply_ecosystem_selector(actor, force=True)
    return actor, apply_result


def validate_selector(spec, style_config, tree_config, material_config, menu_module):
    label = selector_label(spec)
    actor = find_actor_by_label(label)
    if not actor:
        raise RuntimeError(
            f"Missing prepared ecosystem selector validation actor: {label}. "
            "Run prepare_cubeless_ed_ecosystem_selector_validation.py first."
        )
    style_spec = find_style_spec(style_config, spec)
    tree_spec = find_tree_spec(tree_config, spec)
    material_spec = find_material_spec(material_config, spec)
    style_component = get_named_pcg_component(actor, "PCG_StyleProfileMatrix")
    tree_component = get_named_pcg_component(actor, "PCG_TreeProfile")
    material_component = get_named_pcg_component(actor, "PCG_MaterialOverride")
    style_graph_path = get_component_graph_path(style_component)
    tree_graph_path = get_component_graph_path(tree_component)
    material_graph_path = get_component_graph_path(material_component)
    default_style_graph = style_config["STYLE_PROFILE_MATRIX_GRAPH_PATHS"][style_spec["name"]]
    default_tree_graph = tree_config["TREE_PROFILE_GRAPH_PATHS"][tree_spec["name"]]
    expected_style_graph = menu_module._true_material_style_profile_matrix_graph_path(
        int(spec["visual_style_type"]),
        style_spec["profile_mode"],
        style_spec["ground_amount_type"],
        style_spec["ditch_amount_type"],
        int(spec["material_domain_type"]),
        int(spec["material_variant_type"]),
    )
    expected_tree_graph = menu_module._true_material_tree_profile_graph_path(
        int(spec["tree_style_type"]),
        int(spec["tree_amount_type"]),
        int(spec["material_domain_type"]),
        int(spec["material_variant_type"]),
    )
    expected_material_graph, expected_material_graph_mode = expected_material_selector_graph(
        spec,
        material_spec,
        material_config,
        menu_module,
    )
    expected_generate_material_preview = bool(spec.get("generate_material_preview", True))
    actual_generate_material_preview = get_bool_property(
        actor,
        ("GenerateMaterialPreview", "generatematerialpreview"),
        True,
    )
    style_active = int(spec["ecosystem_mode"]) in (1, 3)
    tree_active = int(spec["ecosystem_mode"]) in (2, 3)
    style_true_material_route = expected_style_graph != default_style_graph
    tree_true_material_route = expected_tree_graph != default_tree_graph
    expected_style_points = style_spec["expected_points"] if style_active else 0
    expected_tree_points = tree_spec["expected_points"] if tree_active else 0
    expected_material_points = material_spec["expected_points"] if expected_generate_material_preview else 0
    style_points = get_generated_point_count(style_component)
    tree_points = get_generated_point_count(tree_component)
    material_points = get_generated_point_count(material_component)
    ism_rows = get_ism_rows(actor)
    style_ism = count_instances_for_meshes(ism_rows, style_spec["mesh_paths"])
    tree_ism = count_instances_for_meshes(ism_rows, tree_spec["mesh_paths"])
    material_mesh_paths = [entry["mesh_path"] for entry in material_spec["entries"]]
    material_ism = count_instances_for_meshes(ism_rows, material_mesh_paths)
    expected_style_ism = style_spec["expected_ism"] if style_active else 0
    expected_tree_ism = tree_spec["expected_ism"] if tree_active else 0
    expected_material_ism = material_spec["expected_ism"] if expected_generate_material_preview else 0
    style_mesh_disjoint_from_material = meshes_are_disjoint(style_spec["mesh_paths"], material_mesh_paths)
    tree_mesh_disjoint_from_material = meshes_are_disjoint(tree_spec["mesh_paths"], material_mesh_paths)
    style_ism_check_required = style_mesh_disjoint_from_material
    tree_ism_check_required = tree_mesh_disjoint_from_material
    material_ism_check_required = (
        (not style_active or style_mesh_disjoint_from_material)
        and (not tree_active or tree_mesh_disjoint_from_material)
    )
    style_ism_check_pass = (not style_ism_check_required) or style_ism == expected_style_ism
    tree_ism_check_pass = (not tree_ism_check_required) or tree_ism == expected_tree_ism
    material_ism_check_pass = (not material_ism_check_required) or material_ism == expected_material_ism
    material_point_check_pass = material_points == expected_material_points
    material_dynamic_metadata_relaxed = (
        expected_generate_material_preview
        and expected_material_graph_mode == "dynamic_actor_property"
    )
    if material_dynamic_metadata_relaxed:
        material_point_check_pass = True
    material_preview_enabled_check = actual_generate_material_preview == expected_generate_material_preview
    validation_pass = all([
        style_graph_path == expected_style_graph,
        tree_graph_path == expected_tree_graph,
        material_graph_path == expected_material_graph,
        material_preview_enabled_check,
        style_points == expected_style_points,
        tree_points == expected_tree_points,
        material_point_check_pass,
        style_ism_check_pass,
        tree_ism_check_pass,
        material_ism_check_pass,
    ])
    return {
        "ecosystem": spec["name"],
        "actor": label,
        "ecosystem_mode": spec["ecosystem_mode"],
        "generate_material_preview": actual_generate_material_preview,
        "expected_generate_material_preview": expected_generate_material_preview,
        "style_graph": style_graph_path,
        "expected_style_graph": expected_style_graph,
        "tree_graph": tree_graph_path,
        "expected_tree_graph": expected_tree_graph,
        "material_graph": material_graph_path,
        "expected_material_graph": expected_material_graph,
        "expected_material_graph_mode": expected_material_graph_mode,
        "style_true_material_route": style_true_material_route,
        "tree_true_material_route": tree_true_material_route,
        "style_points": style_points,
        "expected_style_points": expected_style_points,
        "tree_points": tree_points,
        "expected_tree_points": expected_tree_points,
        "material_points": material_points,
        "expected_material_points": expected_material_points,
        "style_ism": style_ism,
        "expected_style_ism": expected_style_ism,
        "tree_ism": tree_ism,
        "expected_tree_ism": expected_tree_ism,
        "material_ism": material_ism,
        "expected_material_ism": expected_material_ism,
        "style_ism_check_required": style_ism_check_required,
        "tree_ism_check_required": tree_ism_check_required,
        "material_ism_check_required": material_ism_check_required,
        "material_preview_enabled_check": material_preview_enabled_check,
        "material_dynamic_metadata_relaxed": material_dynamic_metadata_relaxed,
        "ism_rows": ism_rows,
        "validation_pass": validation_pass,
    }


def main():
    print(VERIFY_MARKER)
    blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
    if not blueprint:
        raise RuntimeError(f"Missing ecosystem selector Blueprint: {BLUEPRINT_PATH}")

    ensure_validation_level_loaded()
    style_config = load_config(STYLE_BUILDER_SCRIPT, "_cubeless_ed_style_profile_matrix_presets_config")
    tree_config = load_config(TREE_BUILDER_SCRIPT, "_cubeless_ed_tree_profile_presets_config")
    material_config = load_config(MATERIAL_BUILDER_SCRIPT, "_cubeless_ed_material_override_presets_config")
    menu_module = load_menu_module()

    if VALIDATION_MODE == "prepare":
        cleanup_existing_validation_actors()
        results = [spawn_selector_actor(spec, index, menu_module) for index, spec in enumerate(VALIDATION_SPECS)]
        print(f"ecosystem_selector_blueprint={BLUEPRINT_PATH}")
        print(f"ecosystem_selector_class={BLUEPRINT_CLASS_PATH}")
        for actor, apply_result in results:
            print(f"prepared_actor={actor.get_actor_label()}")
            print(f"  apply_result={apply_result}")
        print("ecosystem_selector_validation_prepared=True")
        print("MCP_CUBELESS_ED_ECOSYSTEM_SELECTOR_VERIFY_END")
        return

    results = [
        validate_selector(spec, style_config, tree_config, material_config, menu_module)
        for spec in VALIDATION_SPECS
    ]
    log_path, marker_found, log_errors = scan_latest_log(VERIFY_MARKER)
    validation_pass = all(result["validation_pass"] for result in results) and not log_errors

    print(f"ecosystem_selector_blueprint={BLUEPRINT_PATH}")
    print(f"ecosystem_selector_class={BLUEPRINT_CLASS_PATH}")
    for result in results:
        print(f"ecosystem={result['ecosystem']}")
        print(f"  actor={result['actor']}")
        print(f"  ecosystem_mode={result['ecosystem_mode']}")
        print(f"  generate_material_preview={result['generate_material_preview']}")
        print(f"  expected_generate_material_preview={result['expected_generate_material_preview']}")
        print(f"  style_graph={result['style_graph']}")
        print(f"  expected_style_graph={result['expected_style_graph']}")
        print(f"  tree_graph={result['tree_graph']}")
        print(f"  expected_tree_graph={result['expected_tree_graph']}")
        print(f"  material_graph={result['material_graph']}")
        print(f"  expected_material_graph={result['expected_material_graph']}")
        print(f"  expected_material_graph_mode={result['expected_material_graph_mode']}")
        print(f"  style_true_material_route={result['style_true_material_route']}")
        print(f"  tree_true_material_route={result['tree_true_material_route']}")
        print(f"  style_points={result['style_points']}")
        print(f"  expected_style_points={result['expected_style_points']}")
        print(f"  tree_points={result['tree_points']}")
        print(f"  expected_tree_points={result['expected_tree_points']}")
        print(f"  material_points={result['material_points']}")
        print(f"  expected_material_points={result['expected_material_points']}")
        print(f"  style_ism={result['style_ism']}")
        print(f"  expected_style_ism={result['expected_style_ism']}")
        print(f"  tree_ism={result['tree_ism']}")
        print(f"  expected_tree_ism={result['expected_tree_ism']}")
        print(f"  material_ism={result['material_ism']}")
        print(f"  expected_material_ism={result['expected_material_ism']}")
        print(f"  style_ism_check_required={result['style_ism_check_required']}")
        print(f"  tree_ism_check_required={result['tree_ism_check_required']}")
        print(f"  material_ism_check_required={result['material_ism_check_required']}")
        print(f"  material_preview_enabled_check={result['material_preview_enabled_check']}")
        print(f"  material_dynamic_metadata_relaxed={result['material_dynamic_metadata_relaxed']}")
        print(f"  ism_rows={result['ism_rows']}")
        print(f"  validation_pass={result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"ecosystem_selector_validation_pass={validation_pass}")
    print("MCP_CUBELESS_ED_ECOSYSTEM_SELECTOR_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless ED ecosystem selector verification failed")


if __name__ == "__main__":
    main()
