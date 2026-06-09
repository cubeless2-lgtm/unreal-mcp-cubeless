import gc
import importlib
import pathlib
import sys

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\verify_cubeless_pcg_production_candidate_blueprint.py",
    )
).parent
STYLE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_style_profile_matrix_presets.py"
TREE_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_tree_profile_presets.py"
MATERIAL_BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_material_override_presets.py"

PROJECT_PLUGIN_PYTHON = r"D:\Git\CubelessStylized\Plugins\CustomTools\Content\Python"
BLUEPRINT_PATH = (
    "/Game/Cubeless/PCG/ProductionCandidates/Blueprints/"
    "BP_Cubeless_PCG_EcosystemCandidate.BP_Cubeless_PCG_EcosystemCandidate"
)
BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ProductionCandidates/Blueprints/"
    "BP_Cubeless_PCG_EcosystemCandidate.BP_Cubeless_PCG_EcosystemCandidate_C"
)
LEVEL = "/Game/_MCP_Temp/PCG/LVL_Cubeless_PCG_ProductionCandidate_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_PCG_ProductionCandidate"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0
VERIFY_MARKER = "MCP_CUBELESS_PCG_PRODUCTION_CANDIDATE_VERIFY_BEGIN"
VALIDATION_MODE = globals().get("VALIDATION_MODE", "verify")

VALIDATION_SPECS = [
    {
        "name": "Preset_MixedMeadowDefault",
        "preset_type": 1,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "name": "Preset_DenseGroundFoliage",
        "preset_type": 2,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "name": "Preset_RockySparse",
        "preset_type": 3,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "name": "Preset_LightConiferEdge",
        "preset_type": 4,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "name": "Preset_ClassicGrassFill",
        "preset_type": 5,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "name": "Override_DensitySparse",
        "preset_type": 2,
        "density_override": 1,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "name": "Override_DensityDense",
        "preset_type": 1,
        "density_override": 3,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "name": "Override_TreeOff",
        "preset_type": 2,
        "density_override": 0,
        "tree_override": 1,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "name": "Override_TreeLightGrove",
        "preset_type": 5,
        "density_override": 0,
        "tree_override": 4,
        "material_mood": 0,
        "debug_material_preview": False,
    },
    {
        "name": "Override_MaterialCoolDark",
        "preset_type": 5,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 2,
        "debug_material_preview": False,
    },
    {
        "name": "Override_MaterialWarmSoft",
        "preset_type": 1,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 3,
        "debug_material_preview": False,
    },
    {
        "name": "Debug_MaterialPreviewOn",
        "preset_type": 1,
        "density_override": 0,
        "tree_override": 0,
        "material_mood": 0,
        "debug_material_preview": True,
    },
]


def release_python_uobject_refs():
    for attr_name in ("last_type", "last_value", "last_traceback"):
        try:
            if hasattr(sys, attr_name):
                setattr(sys, attr_name, None)
        except Exception:
            pass
    gc.collect()
    collect_garbage = getattr(getattr(unreal, "SystemLibrary", None), "collect_garbage", None)
    if collect_garbage:
        try:
            collect_garbage()
        except Exception:
            pass


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
    level_subsystem = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if get_current_level_path() == LEVEL:
        return
    release_python_uobject_refs()
    if unreal.EditorAssetLibrary.does_asset_exist(LEVEL):
        level_subsystem.load_level(LEVEL)
        release_python_uobject_refs()
        return
    unreal.EditorAssetLibrary.make_directory("/Game/_MCP_Temp/PCG")
    created = level_subsystem.new_level(LEVEL)
    if not created:
        raise RuntimeError(f"Failed to create validation level: {LEVEL}")
    release_python_uobject_refs()
    # _MCP_Temp levels are disposable validation worlds. Do not save them here:
    # UE 5.7 can crash on editor shutdown after saving PCG temp maps that carry
    # transient PCGControlFlowSettings references.


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
        raise RuntimeError("Production candidate actor has no SplineComponent")
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


def get_bool_property(actor, prop_names, default_value=False):
    for prop_name in prop_names:
        try:
            return bool(actor.get_editor_property(prop_name))
        except Exception:
            pass
    return bool(default_value)


def get_int_property(actor, prop_names, default_value=0):
    for prop_name in prop_names:
        try:
            return int(actor.get_editor_property(prop_name))
        except Exception:
            pass
    return int(default_value)


def expected_axes_for_spec(spec, menu_module):
    return menu_module._resolve_production_candidate_axes(
        spec["preset_type"],
        spec["density_override"],
        spec["tree_override"],
        spec["material_mood"],
        spec["debug_material_preview"],
    )


def normalized_style_axes(axes):
    return int(axes["profile_mode"]), int(axes["ground_amount_type"]), int(axes["ditch_amount_type"])


def find_style_spec(style_config, axes):
    profile_mode, ground_type, ditch_type = normalized_style_axes(axes)
    for candidate in style_config["STYLE_PROFILE_MATRIX_SPECS"]:
        if (
            candidate["style_type"] == int(axes["visual_style_type"])
            and candidate["profile_mode"] == profile_mode
            and candidate["ground_amount_type"] == ground_type
            and candidate["ditch_amount_type"] == ditch_type
        ):
            return candidate
    raise RuntimeError(f"No style matrix spec for {axes}")


def find_tree_spec(tree_config, axes):
    for candidate in tree_config["TREE_PROFILE_SPECS"]:
        if (
            candidate["style_type"] == int(axes["tree_style_type"])
            and candidate["amount_type"] == int(axes["tree_amount_type"])
        ):
            return candidate
    raise RuntimeError(f"No tree profile spec for {axes}")


def find_material_spec(material_config, axes):
    for candidate in material_config["MATERIAL_OVERRIDE_SPECS"]:
        if (
            candidate["domain_type"] == int(axes["material_domain_type"])
            and candidate["variant_type"] == int(axes["material_variant_type"])
        ):
            return candidate
    raise RuntimeError(f"No material override spec for {axes}")


def expected_material_selector_graph(axes, material_spec, material_config, menu_module):
    dynamic_graph_path = None
    dynamic_graph_path_func = getattr(menu_module, "_dynamic_material_axis_graph_path", None)
    if callable(dynamic_graph_path_func):
        dynamic_graph_path = dynamic_graph_path_func(
            int(axes["material_domain_type"]),
            int(axes["material_variant_type"]),
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


def spawn_candidate_actor(spec, index, menu_module):
    label = selector_label(spec)
    existing_actor = find_actor_by_label(label)
    if existing_actor:
        unreal.EditorLevelLibrary.destroy_actor(existing_actor)

    actor_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not actor_class:
        raise RuntimeError(f"Missing production candidate Blueprint class: {BLUEPRINT_CLASS_PATH}")

    row = index // 3
    column = index % 3
    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(70000 + column * 3600, row * 3600, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(label)
    set_int_property(actor, "PresetType", spec["preset_type"])
    set_int_property(actor, "DensityOverride", spec["density_override"])
    set_int_property(actor, "TreeOverride", spec["tree_override"])
    set_int_property(actor, "MaterialMood", spec["material_mood"])
    set_bool_property(actor, "DebugMaterialPreview", spec["debug_material_preview"])
    configure_validation_spline(actor)
    apply_result = menu_module.apply_production_candidate_selector(actor, force=True)
    return actor, apply_result


def validate_candidate(spec, style_config, tree_config, material_config, menu_module):
    label = selector_label(spec)
    actor = find_actor_by_label(label)
    if not actor:
        raise RuntimeError(
            f"Missing prepared production candidate validation actor: {label}. "
            "Run prepare_cubeless_pcg_production_candidate_validation.py first."
        )
    axes = expected_axes_for_spec(spec, menu_module)
    style_spec = find_style_spec(style_config, axes)
    tree_spec = find_tree_spec(tree_config, axes)
    material_spec = find_material_spec(material_config, axes)
    style_component = get_named_pcg_component(actor, "PCG_Style")
    tree_component = get_named_pcg_component(actor, "PCG_Tree")
    material_component = get_named_pcg_component(actor, "PCG_MaterialPreview")
    style_graph_path = get_component_graph_path(style_component)
    tree_graph_path = get_component_graph_path(tree_component)
    material_graph_path = get_component_graph_path(material_component)
    default_style_graph = style_config["STYLE_PROFILE_MATRIX_GRAPH_PATHS"][style_spec["name"]]
    default_tree_graph = tree_config["TREE_PROFILE_GRAPH_PATHS"][tree_spec["name"]]
    expected_style_graph = menu_module._true_material_style_profile_matrix_graph_path(
        int(axes["visual_style_type"]),
        style_spec["profile_mode"],
        style_spec["ground_amount_type"],
        style_spec["ditch_amount_type"],
        int(axes["material_domain_type"]),
        int(axes["material_variant_type"]),
    )
    expected_tree_graph = menu_module._true_material_tree_profile_graph_path(
        int(axes["tree_style_type"]),
        int(axes["tree_amount_type"]),
        int(axes["material_domain_type"]),
        int(axes["material_variant_type"]),
    )
    expected_material_graph, expected_material_graph_mode = expected_material_selector_graph(
        axes,
        material_spec,
        material_config,
        menu_module,
    )
    expected_debug_material_preview = bool(axes["debug_material_preview"])
    actual_debug_material_preview = get_bool_property(
        actor,
        ("DebugMaterialPreview", "debugmaterialpreview"),
        False,
    )
    actual_internal_material_domain = get_int_property(actor, ("MaterialDomainType", "materialdomaintype"), 0)
    actual_internal_material_variant = get_int_property(actor, ("MaterialVariantType", "materialvarianttype"), 0)
    style_active = int(axes["ecosystem_mode"]) in (1, 3)
    tree_active = int(axes["ecosystem_mode"]) in (2, 3)
    style_true_material_route = expected_style_graph != default_style_graph
    tree_true_material_route = expected_tree_graph != default_tree_graph
    expected_style_points = style_spec["expected_points"] if style_active else 0
    expected_tree_points = tree_spec["expected_points"] if tree_active else 0
    expected_material_points = material_spec["expected_points"] if expected_debug_material_preview else 0
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
    expected_material_ism = material_spec["expected_ism"] if expected_debug_material_preview else 0
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
        expected_debug_material_preview
        and expected_material_graph_mode == "dynamic_actor_property"
    )
    if material_dynamic_metadata_relaxed:
        material_point_check_pass = True
    debug_material_preview_check = actual_debug_material_preview == expected_debug_material_preview
    internal_material_check = (
        actual_internal_material_domain == int(axes["material_domain_type"])
        and actual_internal_material_variant == int(axes["material_variant_type"])
    )
    validation_pass = all([
        style_graph_path == expected_style_graph,
        tree_graph_path == expected_tree_graph,
        material_graph_path == expected_material_graph,
        debug_material_preview_check,
        internal_material_check,
        style_points == expected_style_points,
        tree_points == expected_tree_points,
        material_point_check_pass,
        style_ism_check_pass,
        tree_ism_check_pass,
        material_ism_check_pass,
    ])
    return {
        "candidate": spec["name"],
        "actor": label,
        "preset_type": spec["preset_type"],
        "preset_label": axes["label"],
        "density_override": spec["density_override"],
        "tree_override": spec["tree_override"],
        "material_mood": spec["material_mood"],
        "debug_material_preview": actual_debug_material_preview,
        "expected_debug_material_preview": expected_debug_material_preview,
        "ecosystem_mode": axes["ecosystem_mode"],
        "visual_style_type": axes["visual_style_type"],
        "profile_mode": axes["profile_mode"],
        "ground_amount_type": axes["ground_amount_type"],
        "ditch_amount_type": axes["ditch_amount_type"],
        "tree_style_type": axes["tree_style_type"],
        "tree_amount_type": axes["tree_amount_type"],
        "material_domain_type": axes["material_domain_type"],
        "material_variant_type": axes["material_variant_type"],
        "internal_material_domain": actual_internal_material_domain,
        "internal_material_variant": actual_internal_material_variant,
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
        "debug_material_preview_check": debug_material_preview_check,
        "internal_material_check": internal_material_check,
        "material_dynamic_metadata_relaxed": material_dynamic_metadata_relaxed,
        "ism_rows": ism_rows,
        "validation_pass": validation_pass,
    }


def main():
    print(VERIFY_MARKER)
    blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
    if not blueprint:
        raise RuntimeError(f"Missing production candidate Blueprint: {BLUEPRINT_PATH}")

    ensure_validation_level_loaded()
    style_config = load_config(STYLE_BUILDER_SCRIPT, "_cubeless_ed_style_profile_matrix_presets_config")
    tree_config = load_config(TREE_BUILDER_SCRIPT, "_cubeless_ed_tree_profile_presets_config")
    material_config = load_config(MATERIAL_BUILDER_SCRIPT, "_cubeless_ed_material_override_presets_config")
    menu_module = load_menu_module()

    if VALIDATION_MODE == "prepare":
        cleanup_existing_validation_actors()
        results = [spawn_candidate_actor(spec, index, menu_module) for index, spec in enumerate(VALIDATION_SPECS)]
        print(f"production_candidate_blueprint={BLUEPRINT_PATH}")
        print(f"production_candidate_class={BLUEPRINT_CLASS_PATH}")
        print(f"production_candidate_validation_level={LEVEL}")
        for actor, apply_result in results:
            print(f"prepared_actor={actor.get_actor_label()}")
            print(f"  apply_result={apply_result}")
        print("production_candidate_validation_prepared=True")
        print("MCP_CUBELESS_PCG_PRODUCTION_CANDIDATE_VERIFY_END")
        return

    results = [
        validate_candidate(spec, style_config, tree_config, material_config, menu_module)
        for spec in VALIDATION_SPECS
    ]
    log_path, marker_found, log_errors = scan_latest_log(VERIFY_MARKER)
    validation_pass = all(result["validation_pass"] for result in results) and not log_errors

    print(f"production_candidate_blueprint={BLUEPRINT_PATH}")
    print(f"production_candidate_class={BLUEPRINT_CLASS_PATH}")
    print(f"production_candidate_validation_level={LEVEL}")
    for result in results:
        print(f"candidate={result['candidate']}")
        print(f"  actor={result['actor']}")
        print(f"  preset_type={result['preset_type']}")
        print(f"  preset_label={result['preset_label']}")
        print(f"  density_override={result['density_override']}")
        print(f"  tree_override={result['tree_override']}")
        print(f"  material_mood={result['material_mood']}")
        print(f"  debug_material_preview={result['debug_material_preview']}")
        print(f"  expected_debug_material_preview={result['expected_debug_material_preview']}")
        print(f"  ecosystem_mode={result['ecosystem_mode']}")
        print(f"  visual_style_type={result['visual_style_type']}")
        print(f"  profile_mode={result['profile_mode']}")
        print(f"  ground_amount_type={result['ground_amount_type']}")
        print(f"  ditch_amount_type={result['ditch_amount_type']}")
        print(f"  tree_style_type={result['tree_style_type']}")
        print(f"  tree_amount_type={result['tree_amount_type']}")
        print(f"  material_domain_type={result['material_domain_type']}")
        print(f"  material_variant_type={result['material_variant_type']}")
        print(f"  internal_material_domain={result['internal_material_domain']}")
        print(f"  internal_material_variant={result['internal_material_variant']}")
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
        print(f"  debug_material_preview_check={result['debug_material_preview_check']}")
        print(f"  internal_material_check={result['internal_material_check']}")
        print(f"  material_dynamic_metadata_relaxed={result['material_dynamic_metadata_relaxed']}")
        print(f"  ism_rows={result['ism_rows']}")
        print(f"  validation_pass={result['validation_pass']}")
    print(f"log={log_path}")
    print(f"log_marker_found={marker_found}")
    print(f"log_error_count={len(log_errors)}")
    for line in log_errors[:20]:
        print(f"log_error={line}")
    print(f"production_candidate_validation_pass={validation_pass}")
    print("MCP_CUBELESS_PCG_PRODUCTION_CANDIDATE_VERIFY_END")
    if not validation_pass:
        raise RuntimeError("Cubeless PCG production candidate verification failed")


if __name__ == "__main__":
    main()
