import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get("__file__", r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\build_cubeless_ditch_hierarchy_prototype.py")
).parent
BASE_BUILDER_SCRIPT = SCRIPT_DIR / "build_spline_assembly_with_post_copy_offset.py"

PACKAGE_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning"
ASSET_NAME = "PCG_Cubeless_DitchHierarchyPrototype"
GRAPH_PATH = f"{PACKAGE_PATH}/{ASSET_NAME}.{ASSET_NAME}"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_Cubeless_DitchHierarchyPrototype_Validation"
VALIDATION_BLUEPRINT_CLASS_PATH = (
    "/Game/_MCP_Temp/PCG/"
    "BP_ElectricDreamsSplineAssemblyTest.BP_ElectricDreamsSplineAssemblyTest_C"
)
BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/"
    "BP_Cubeless_PostCopyPointsOffsetIndices.BP_Cubeless_PostCopyPointsOffsetIndices_C"
)


def load_base_namespace():
    namespace = {"__name__": "_cubeless_ditch_hierarchy_base"}
    with open(BASE_BUILDER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(BASE_BUILDER_SCRIPT), "exec")
    exec(code, namespace)
    return namespace


BASE = load_base_namespace()
BASE.update({
    "GRAPH_PATH": GRAPH_PATH,
    "LEVEL": LEVEL,
    "ACTOR_LABEL": ACTOR_LABEL,
    "BLUEPRINT_CLASS_PATH": BLUEPRINT_CLASS_PATH,
    "SOURCE_ASSEMBLY_PRESET": "ditch_riverbank",
    "TARGET_SAMPLE_COUNT": 6,
    "TARGET_POINT_SPACING": 320.0,
    "SIDE_MASK_FILTER_PROFILE": "center_right_after_copy",
    "BRANCH_DENSITY_PRUNING_PROFILE": "leaf_mud_only",
    "GROUND_STYLE_DENSITY_FILTER_LOWER": 0.0,
    "GROUND_STYLE_DENSITY_FILTER_UPPER": 1.0,
    "GROUND_STYLE_SELF_PRUNING_RANDOMIZED": False,
    "GROUND_STYLE_SELF_PRUNING_RADIUS_SIMILARITY": 0.0,
})

for exported_name in [
    "SOURCE_ASSEMBLY_PRESET",
    "TARGET_SAMPLE_COUNT",
    "TARGET_POINT_SPACING",
    "SIDE_MODE",
    "BRANCH_JITTER",
    "WIDTH_VARIANT",
    "HEIGHT_VARIANT",
    "SIDE_MASK_FILTER_PROFILE",
    "BRANCH_DENSITY_PRUNING_PROFILE",
    "BRANCH_DENSITY_NOISE_MIN",
    "BRANCH_DENSITY_NOISE_MAX",
    "BRANCH_DENSITY_FILTER_THRESHOLD",
    "GROUND_STYLE_DENSITY_FILTER_ENABLED",
    "GROUND_STYLE_DENSITY_FILTER_LOWER",
    "GROUND_STYLE_DENSITY_FILTER_UPPER",
    "GROUND_STYLE_SELF_PRUNING_ENABLED",
    "GROUND_STYLE_SELF_PRUNING_RANDOMIZED",
    "GROUND_STYLE_SELF_PRUNING_RADIUS_SIMILARITY",
    "RIVERBANK_HALF_WIDTH",
    "RIVERBANK_FORWARD_STEP",
    "RIVERBANK_HEIGHT_STEP",
    "RIVERBANK_ROCK_OFFSET",
    "get_source_assembly",
    "side_filter_profile_spec",
    "active_side_mask_filter_profile",
    "graph_side_filter_allows",
    "active_branch_density_pruning_profile",
    "branch_density_pruning_profile_spec",
    "branch_density_noise_min",
    "branch_density_noise_max",
    "branch_density_filter_threshold",
    "branch_density_value",
    "side_mask_value",
]:
    globals()[exported_name] = BASE[exported_name]


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def ensure_graph_asset():
    unreal.EditorAssetLibrary.make_directory(PACKAGE_PATH)
    graph = unreal.EditorAssetLibrary.load_asset(GRAPH_PATH)
    if graph:
        return graph
    graph = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        ASSET_NAME,
        PACKAGE_PATH,
        unreal.PCGGraph.static_class(),
        unreal.PCGGraphFactory(),
    )
    if not graph:
        raise RuntimeError(f"Failed to create {GRAPH_PATH}")
    unreal.EditorAssetLibrary.save_loaded_asset(graph)
    return graph


def configure_validation_spline(actor):
    for spline in actor.get_components_by_class(unreal.SplineComponent):
        half_length = (float(TARGET_SAMPLE_COUNT) - 1.0) * float(TARGET_POINT_SPACING) * 0.5
        spline.clear_spline_points(False)
        spline.add_spline_point(unreal.Vector(0, -half_length, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, 0, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, half_length, 0), unreal.SplineCoordinateSpace.LOCAL, True)
        spline.update_spline()


def spawn_validation_actor(graph):
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for actor in get_all_level_actors():
        if actor.get_actor_label() == ACTOR_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    actor_class = unreal.load_class(None, VALIDATION_BLUEPRINT_CLASS_PATH)
    if not actor_class:
        raise RuntimeError(f"Missing validation actor class: {VALIDATION_BLUEPRINT_CLASS_PATH}")

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(4300, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(ACTOR_LABEL)
    configure_validation_spline(actor)

    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {ACTOR_LABEL}")
    for component in pcg_components:
        component.set_graph(graph)
        component.cleanup(True)
        component.generate(True)
    return actor


def build_graph():
    ensure_graph_asset()
    return BASE["build_graph"]()


def main():
    helper_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not helper_class:
        raise RuntimeError(f"Missing production post-copy helper class: {BLUEPRINT_CLASS_PATH}")

    source_assembly = get_source_assembly()
    print("MCP_CUBELESS_DITCH_HIERARCHY_PROTOTYPE_BUILD_BEGIN")
    graph = build_graph()
    actor = spawn_validation_actor(graph)
    print(f"production_graph={graph.get_path_name()}")
    print(f"validation_actor={actor.get_actor_label()}")
    print(f"post_copy_helper_class={BLUEPRINT_CLASS_PATH}")
    print(f"validation_actor_class={VALIDATION_BLUEPRINT_CLASS_PATH}")
    print(f"source_assembly_preset={SOURCE_ASSEMBLY_PRESET}")
    print(f"source_point_count={len(source_assembly)}")
    print(f"target_sample_count={TARGET_SAMPLE_COUNT}")
    print(f"target_point_spacing={TARGET_POINT_SPACING}")
    print(f"side_mask_filter_profile={active_side_mask_filter_profile()}")
    density_spec = branch_density_pruning_profile_spec()
    print(f"branch_density_pruning_profile={active_branch_density_pruning_profile()}")
    print(f"branch_density_noise_min={density_spec['noise_min']}")
    print(f"branch_density_noise_max={density_spec['noise_max']}")
    print(f"branch_density_filter_threshold={density_spec['threshold']}")
    print(f"ground_style_density_filter_lower={GROUND_STYLE_DENSITY_FILTER_LOWER}")
    print(f"ground_style_density_filter_upper={GROUND_STYLE_DENSITY_FILTER_UPPER}")
    print(f"ground_style_self_pruning_randomized={GROUND_STYLE_SELF_PRUNING_RANDOMIZED}")
    print(f"ground_style_self_pruning_radius_similarity={GROUND_STYLE_SELF_PRUNING_RADIUS_SIMILARITY}")
    print("MCP_CUBELESS_DITCH_HIERARCHY_PROTOTYPE_BUILD_END")


if __name__ == "__main__":
    main()
