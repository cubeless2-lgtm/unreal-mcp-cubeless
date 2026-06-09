import pathlib

import unreal


SCRIPT_DIR = pathlib.Path(
    globals().get(
        "__file__",
        r"D:\Git\unreal-mcp-cubeless\Docs\Analysis\ElectricDreams\apply_cubeless_ed_style_profile_matrix_selector.py",
    )
).parent
BUILDER_SCRIPT = SCRIPT_DIR / "build_cubeless_ed_style_profile_matrix_presets.py"

BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGStyleProfileMatrixSelector.BP_Cubeless_ED_PCGStyleProfileMatrixSelector_C"
)


def load_style_profile_matrix_config():
    namespace = {"__name__": "_cubeless_ed_style_profile_matrix_presets_config"}
    with open(BUILDER_SCRIPT, "r", encoding="utf-8") as handle:
        code = compile(handle.read(), str(BUILDER_SCRIPT), "exec")
    exec(code, namespace)
    graph_paths = {}
    for spec in namespace["STYLE_PROFILE_MATRIX_SPECS"]:
        key = (
            spec["style_type"],
            spec["profile_mode"],
            spec["ground_amount_type"],
            spec["ditch_amount_type"],
        )
        graph_paths[key] = namespace["STYLE_PROFILE_MATRIX_GRAPH_PATHS"][spec["name"]]
    return graph_paths


STYLE_PROFILE_MATRIX_GRAPH_BY_AXES = load_style_profile_matrix_config()


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def get_selected_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_selected_level_actors()
    return unreal.EditorLevelLibrary.get_selected_level_actors()


def get_int_property(actor, prop_names, default_value=2):
    for prop_name in prop_names:
        try:
            value = int(actor.get_editor_property(prop_name))
            return value
        except Exception:
            pass
    return int(default_value)


def normalize_amount_axis(value, default_value=2):
    value = int(value)
    if value in (1, 2, 3):
        return value
    return int(default_value)


def normalize_style_type(value, default_value=1):
    value = int(value)
    if value in (1, 2, 3, 4, 5):
        return value
    return int(default_value)


def get_style_profile_matrix_axes(actor):
    style_type = normalize_style_type(
        get_int_property(actor, ("VisualStyleType", "visualstyletype"), 1)
    )
    profile_mode = get_int_property(actor, ("ProfileMode", "profilemode"), 3)
    if profile_mode not in (1, 2, 3):
        profile_mode = 3
    ground_type = normalize_amount_axis(
        get_int_property(actor, ("GroundAmountType", "groundamounttype"), 2)
    )
    ditch_type = normalize_amount_axis(
        get_int_property(actor, ("DitchAmountType", "ditchamounttype"), 2)
    )
    if profile_mode == 1:
        ditch_type = 0
    elif profile_mode == 2:
        ground_type = 0
    key = (style_type, profile_mode, ground_type, ditch_type)
    if key not in STYLE_PROFILE_MATRIX_GRAPH_BY_AXES:
        key = (1, 3, 2, 2)
    return key


def point_count_for_component(component):
    try:
        collection = component.get_generated_graph_output()
        for item in collection.get_editor_property("tagged_data"):
            data = item.get_editor_property("data").get_editor_property("data")
            if data and hasattr(data, "get_num_points"):
                return int(data.get_num_points())
    except Exception:
        return 0
    return 0


def apply_style_profile_matrix_selector(actor, force=True):
    style_type, profile_mode, ground_type, ditch_type = get_style_profile_matrix_axes(actor)
    graph_path = STYLE_PROFILE_MATRIX_GRAPH_BY_AXES[(style_type, profile_mode, ground_type, ditch_type)]
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        raise RuntimeError(f"Missing style profile matrix graph: {graph_path}")

    components = actor.get_components_by_class(unreal.PCGComponent)
    if not components:
        raise RuntimeError(
            f"Style profile matrix selector actor has no PCG component: {actor.get_actor_label()}"
        )

    component = components[0]
    component.cleanup(True)
    component.set_graph(graph)
    component.activate(True)
    component.generate(bool(force))
    component.generate(bool(force))
    return {
        "actor": actor.get_actor_label(),
        "visual_style_type": style_type,
        "profile_mode": profile_mode,
        "ground_amount_type": ground_type,
        "ditch_amount_type": ditch_type,
        "graph": graph_path,
        "point_count": point_count_for_component(component),
    }


def is_style_profile_matrix_selector_actor(actor):
    selector_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not selector_class:
        return False
    try:
        return bool(actor.get_class().is_child_of(selector_class))
    except Exception:
        return actor.get_class() == selector_class


def main():
    print("MCP_CUBELESS_ED_STYLE_PROFILE_MATRIX_SELECTOR_APPLY_BEGIN")
    selected = [
        actor for actor in get_selected_level_actors()
        if is_style_profile_matrix_selector_actor(actor)
    ]
    actors = selected or [
        actor for actor in get_all_level_actors()
        if is_style_profile_matrix_selector_actor(actor)
    ]
    if not actors:
        raise RuntimeError("No Cubeless ED style profile matrix selector actors found")
    print(f"style_profile_matrix_selector_actor_count={len(actors)}")
    for actor in actors:
        result = apply_style_profile_matrix_selector(actor, force=True)
        print(f"actor={result['actor']}")
        print(f"  visual_style_type={result['visual_style_type']}")
        print(f"  profile_mode={result['profile_mode']}")
        print(f"  ground_amount_type={result['ground_amount_type']}")
        print(f"  ditch_amount_type={result['ditch_amount_type']}")
        print(f"  graph={result['graph']}")
        print(f"  point_count={result['point_count']}")
    print("MCP_CUBELESS_ED_STYLE_PROFILE_MATRIX_SELECTOR_APPLY_END")


if __name__ == "__main__":
    main()
