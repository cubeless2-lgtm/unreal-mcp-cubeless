import time

import unreal


BLUEPRINT_CLASS_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Authoring/"
    "BP_Cubeless_ED_PCGAuthoringSelector.BP_Cubeless_ED_PCGAuthoringSelector_C"
)

COMBO_BY_TYPE = {
    1: "PCG_Sparse",
    2: "PCG_Normal",
    3: "PCG_Dense",
}


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


def get_designer_combo_type(actor):
    for prop_name in ("DesignerComboType", "designercombotype"):
        try:
            value = int(actor.get_editor_property(prop_name))
            return value
        except Exception:
            pass
    raise RuntimeError(f"Actor has no DesignerComboType property: {actor.get_actor_label()}")


def component_key(component):
    name = component.get_name()
    for key in COMBO_BY_TYPE.values():
        if name.startswith(key):
            return key
    return name


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


def wait_for_component_output(component, min_points=1, timeout_seconds=2.0):
    deadline = time.perf_counter() + float(timeout_seconds)
    attempts = 0
    while True:
        point_count = point_count_for_component(component)
        if point_count >= int(min_points) or time.perf_counter() >= deadline:
            return point_count
        attempts += 1
        if attempts % 3 == 0:
            component.generate(True)
        time.sleep(0.1)


def apply_selector(actor, force=True):
    combo_type = get_designer_combo_type(actor)
    selected_key = COMBO_BY_TYPE.get(combo_type, COMBO_BY_TYPE[2])
    components = actor.get_components_by_class(unreal.PCGComponent)
    if len(components) < 3:
        raise RuntimeError(f"Selector actor expected 3 PCG components: {actor.get_actor_label()}")

    result = {
        "actor": actor.get_actor_label(),
        "designer_combo_type": combo_type,
        "selected_component": selected_key,
        "component_point_counts": {},
    }
    for component in components:
        component.cleanup(True)
        component.deactivate()

    for component in components:
        key = component_key(component)
        if key == selected_key:
            component.activate(True)
            component.generate(bool(force))
            # Freshly activated PCG components can report no graph output on the
            # first editor call even when the graph is valid. A second forced
            # generate matches the existing validation pattern for these assets.
            component.generate(bool(force))
            result["component_point_counts"][key] = wait_for_component_output(component)
        else:
            result["component_point_counts"][key] = point_count_for_component(component)
    return result


def is_selector_actor(actor):
    selector_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not selector_class:
        return False
    try:
        return bool(actor.get_class().is_child_of(selector_class))
    except Exception:
        return actor.get_class() == selector_class


def main():
    print("MCP_CUBELESS_ED_AUTHORING_SELECTOR_APPLY_BEGIN")
    selected = [actor for actor in get_selected_level_actors() if is_selector_actor(actor)]
    actors = selected or [actor for actor in get_all_level_actors() if is_selector_actor(actor)]
    if not actors:
        raise RuntimeError("No Cubeless ED authoring selector actors found")
    print(f"selector_actor_count={len(actors)}")
    for actor in actors:
        result = apply_selector(actor, force=True)
        print(f"actor={result['actor']}")
        print(f"  designer_combo_type={result['designer_combo_type']}")
        print(f"  selected_component={result['selected_component']}")
        print(f"  component_point_counts={result['component_point_counts']}")
    print("MCP_CUBELESS_ED_AUTHORING_SELECTOR_APPLY_END")


if __name__ == "__main__":
    main()
