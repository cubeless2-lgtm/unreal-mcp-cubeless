import unreal


SOURCE_BLUEPRINT_PACKAGE = "/Game/_MCP_Temp/PCG/BP_ElectricDreamsSplineAssemblyTest"
SOURCE_BLUEPRINT_PATH = (
    "/Game/_MCP_Temp/PCG/"
    "BP_ElectricDreamsSplineAssemblyTest.BP_ElectricDreamsSplineAssemblyTest"
)
PACKAGE_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints"
ASSET_NAME = "BP_Cubeless_ED_PCGDesignerControlActor"
BLUEPRINT_PACKAGE = f"{PACKAGE_PATH}/{ASSET_NAME}"
BLUEPRINT_PATH = f"{BLUEPRINT_PACKAGE}.{ASSET_NAME}"
BLUEPRINT_CLASS_PATH = f"{BLUEPRINT_PACKAGE}.{ASSET_NAME}_C"
DESIGNER_GRAPH_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/"
    "Presets/PCG_Cubeless_ED_Preset_Balanced.PCG_Cubeless_ED_Preset_Balanced"
)
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL = "MCP_Cubeless_ED_PCGDesignerControlActor_Validation"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0


def get_all_level_actors():
    actor_subsystem_cls = getattr(unreal, "EditorActorSubsystem", None)
    if actor_subsystem_cls:
        actor_subsystem = unreal.get_editor_subsystem(actor_subsystem_cls)
        if actor_subsystem:
            return actor_subsystem.get_all_level_actors()
    return unreal.EditorLevelLibrary.get_all_level_actors()


def get_subobject_templates(blueprint):
    subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
    library = unreal.SubobjectDataBlueprintFunctionLibrary
    if not subsystem:
        raise RuntimeError("SubobjectDataSubsystem is unavailable")

    rows = []
    for handle in subsystem.k2_gather_subobject_data_for_blueprint(blueprint):
        data = subsystem.k2_find_subobject_data_from_handle(handle)
        obj = library.get_object_for_blueprint(data, blueprint)
        if obj:
            rows.append({
                "object": obj,
                "name": obj.get_name(),
                "class": obj.get_class().get_name(),
                "is_component": bool(library.is_component(data)),
                "is_root": bool(library.is_root_component(data)),
                "is_scene": bool(library.is_scene_component(data)),
            })
    return rows


def configure_validation_spline(actor):
    splines = actor.get_components_by_class(unreal.SplineComponent)
    if not splines:
        raise RuntimeError("Validation actor has no SplineComponent")

    half_length = (float(TARGET_SAMPLE_COUNT) - 1.0) * float(TARGET_POINT_SPACING) * 0.5
    for spline in splines:
        spline.clear_spline_points(False)
        spline.add_spline_point(unreal.Vector(0, -half_length, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, 0, 0), unreal.SplineCoordinateSpace.LOCAL, False)
        spline.add_spline_point(unreal.Vector(0, half_length, 0), unreal.SplineCoordinateSpace.LOCAL, True)
        spline.update_spline()


def load_or_duplicate_blueprint():
    unreal.EditorAssetLibrary.make_directory(PACKAGE_PATH)
    blueprint = unreal.EditorAssetLibrary.load_asset(BLUEPRINT_PATH)
    created = False
    if blueprint:
        return blueprint, created

    source = unreal.EditorAssetLibrary.load_asset(SOURCE_BLUEPRINT_PATH)
    if not source:
        raise RuntimeError(f"Missing source blueprint: {SOURCE_BLUEPRINT_PATH}")

    duplicated = unreal.EditorAssetLibrary.duplicate_asset(SOURCE_BLUEPRINT_PACKAGE, BLUEPRINT_PACKAGE)
    if not duplicated:
        raise RuntimeError(f"Failed to duplicate blueprint to {BLUEPRINT_PACKAGE}")
    return duplicated, True


def set_blueprint_pcg_graph(blueprint, graph):
    templates = get_subobject_templates(blueprint)
    spline_templates = [
        row for row in templates
        if row["is_component"] and row["class"] == "SplineComponent"
    ]
    pcg_templates = [
        row for row in templates
        if row["is_component"] and isinstance(row["object"], unreal.PCGComponent)
    ]
    if not spline_templates:
        raise RuntimeError("Blueprint has no SplineComponent template")
    if not pcg_templates:
        raise RuntimeError("Blueprint has no PCGComponent template")

    for row in pcg_templates:
        pcg = row["object"]
        pcg.modify()
        try:
            pcg.set_graph(graph)
        except Exception as exc:
            print(f"pcg_template_set_graph_warning={type(exc).__name__}:{exc}")
        graph_instance = pcg.get_editor_property("graph_instance")
        if not graph_instance:
            raise RuntimeError(f"PCG template has no graph_instance: {pcg.get_name()}")
        graph_instance.modify()
        graph_instance.set_editor_property("graph", graph)
        pcg.set_editor_property(
            "generation_trigger",
            unreal.PCGComponentGenerationTrigger.GENERATE_ON_LOAD,
        )

    blueprint.modify()
    return templates


def compile_and_save(blueprint):
    unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
    unreal.EditorAssetLibrary.save_loaded_asset(blueprint)


def spawn_validation_actor(graph):
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for actor in get_all_level_actors():
        if actor.get_actor_label() == ACTOR_LABEL:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    actor_class = unreal.load_class(None, BLUEPRINT_CLASS_PATH)
    if not actor_class:
        raise RuntimeError(f"Missing production actor class: {BLUEPRINT_CLASS_PATH}")

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(5600, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(ACTOR_LABEL)
    configure_validation_spline(actor)

    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError("Validation actor has no PCGComponent")
    for component in pcg_components:
        # Keep the instance explicit for validation even though the template is set above.
        component.set_graph(graph)
        component.cleanup(True)
        component.generate(True)
    return actor


def main():
    print("MCP_CUBELESS_ED_DESIGNER_CONTROL_ACTOR_BUILD_BEGIN")
    graph = unreal.EditorAssetLibrary.load_asset(DESIGNER_GRAPH_PATH)
    if not graph:
        raise RuntimeError(f"Missing designer graph: {DESIGNER_GRAPH_PATH}")

    blueprint, created = load_or_duplicate_blueprint()
    templates = set_blueprint_pcg_graph(blueprint, graph)
    compile_and_save(blueprint)
    actor = spawn_validation_actor(graph)

    template_rows = [
        (row["name"], row["class"], row["is_component"], row["is_root"], row["is_scene"])
        for row in templates
    ]
    print(f"production_blueprint={blueprint.get_path_name()}")
    print(f"production_class={BLUEPRINT_CLASS_PATH}")
    print(f"created={created}")
    print(f"default_designer_graph={DESIGNER_GRAPH_PATH}")
    print(f"component_templates={template_rows}")
    print(f"validation_actor={actor.get_actor_label()}")
    print("MCP_CUBELESS_ED_DESIGNER_CONTROL_ACTOR_BUILD_END")


if __name__ == "__main__":
    main()
