import unreal


BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGTreeProfileSelector.BP_Cubeless_ED_PCGTreeProfileSelector_C"
)
TREE_PROFILE_GRAPH_FOLDER = "/Game/Cubeless/PCG/ElectricDreamsLearning/TreeProfilePresets"

TREE_STYLE_NAMES = {
    1: "CompactConifer",
    2: "ColumnConifer",
    3: "MixedConifer",
}
TREE_AMOUNT_NAMES = {
    1: "Solo",
    2: "Sparse",
    3: "LightGrove",
}


def _get_int_property(actor, prop_names, default_value=1):
    for prop_name in prop_names:
        try:
            return int(actor.get_editor_property(prop_name))
        except Exception:
            pass
    return int(default_value)


def _normalize_axis(value, valid_values, default_value):
    value = int(value)
    if value in valid_values:
        return value
    return int(default_value)


def _tree_profile_asset_name(style_type, amount_type):
    style_name = TREE_STYLE_NAMES.get(style_type)
    amount_name = TREE_AMOUNT_NAMES.get(amount_type)
    if not style_name or not amount_name:
        return None
    return f"PCG_Cubeless_ED_TreeProfile_{style_name}_{amount_name}"


def tree_profile_graph_path(style_type, amount_type):
    asset_name = _tree_profile_asset_name(style_type, amount_type)
    if not asset_name:
        raise RuntimeError(f"Invalid tree profile axes: style={style_type} amount={amount_type}")
    return f"{TREE_PROFILE_GRAPH_FOLDER}/{asset_name}.{asset_name}"


def get_tree_profile_axes(actor):
    style_type = _normalize_axis(
        _get_int_property(actor, ("TreeStyleType", "treestyletype"), 1),
        TREE_STYLE_NAMES,
        1,
    )
    amount_type = _normalize_axis(
        _get_int_property(actor, ("TreeAmountType", "treeamounttype"), 2),
        TREE_AMOUNT_NAMES,
        2,
    )
    return style_type, amount_type


def apply_tree_profile_selector(actor, force=True):
    style_type, amount_type = get_tree_profile_axes(actor)
    graph_path = tree_profile_graph_path(style_type, amount_type)
    graph = unreal.EditorAssetLibrary.load_asset(graph_path)
    if not graph:
        raise RuntimeError(f"Missing tree profile graph: {graph_path}")

    components = actor.get_components_by_class(unreal.PCGComponent)
    if not components:
        raise RuntimeError(f"Tree profile selector actor has no PCG component: {actor.get_actor_label()}")

    component = components[0]
    component.cleanup(True)
    component.set_graph(graph)
    component.activate(True)
    component.generate(bool(force))
    component.generate(bool(force))
    return {
        "selector_type": "tree_profile",
        "actor": actor.get_actor_label(),
        "tree_style_type": style_type,
        "tree_amount_type": amount_type,
        "graph": graph_path,
        "component_point_counts": summarize_counts(actor),
    }


def component_key(component):
    return component.get_name()


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


def summarize_counts(actor):
    counts = {}
    for component in actor.get_components_by_class(unreal.PCGComponent):
        counts[component_key(component)] = point_count_for_component(component)
    return counts
