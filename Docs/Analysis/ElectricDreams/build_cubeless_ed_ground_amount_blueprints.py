import unreal


SOURCE_BLUEPRINT_PACKAGE = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/"
    "BP_Cubeless_ED_PCGDesignerControlActor"
)
SOURCE_BLUEPRINT_PATH = (
    "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/"
    "BP_Cubeless_ED_PCGDesignerControlActor.BP_Cubeless_ED_PCGDesignerControlActor"
)
PACKAGE_PATH = "/Game/Cubeless/PCG/ElectricDreamsLearning/Blueprints/Amount"
LEVEL = "/Game/_MCP_Temp/PCG/LVL_ElectricDreams_SplineAssembly_MCP"
ACTOR_LABEL_PREFIX = "MCP_Cubeless_ED_GroundAmountBlueprint"
TARGET_SAMPLE_COUNT = 6
TARGET_POINT_SPACING = 320.0

AMOUNT_BLUEPRINT_SPECS = [
    {
        "name": "Sparse",
        "asset_name": "BP_Cubeless_ED_GroundAmount_Sparse",
        "graph_path": (
            "/Game/Cubeless/PCG/ElectricDreamsLearning/AmountPresets/"
            "PCG_Cubeless_ED_GroundAmount_Sparse.PCG_Cubeless_ED_GroundAmount_Sparse"
        ),
        "expected_points": 3,
        "expected_ism": 3,
        "amount_id": 201,
        "amount_type": 1,
    },
    {
        "name": "Normal",
        "asset_name": "BP_Cubeless_ED_GroundAmount_Normal",
        "graph_path": (
            "/Game/Cubeless/PCG/ElectricDreamsLearning/AmountPresets/"
            "PCG_Cubeless_ED_GroundAmount_Normal.PCG_Cubeless_ED_GroundAmount_Normal"
        ),
        "expected_points": 8,
        "expected_ism": 8,
        "amount_id": 202,
        "amount_type": 2,
    },
    {
        "name": "Dense",
        "asset_name": "BP_Cubeless_ED_GroundAmount_Dense",
        "graph_path": (
            "/Game/Cubeless/PCG/ElectricDreamsLearning/AmountPresets/"
            "PCG_Cubeless_ED_GroundAmount_Dense.PCG_Cubeless_ED_GroundAmount_Dense"
        ),
        "expected_points": 16,
        "expected_ism": 16,
        "amount_id": 203,
        "amount_type": 3,
    },
]


def blueprint_package(spec):
    return f"{PACKAGE_PATH}/{spec['asset_name']}"


def blueprint_path(spec):
    return f"{blueprint_package(spec)}.{spec['asset_name']}"


def blueprint_class_path(spec):
    return f"{blueprint_package(spec)}.{spec['asset_name']}_C"


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


def load_or_duplicate_blueprint(spec):
    unreal.EditorAssetLibrary.make_directory(PACKAGE_PATH)
    blueprint = unreal.EditorAssetLibrary.load_asset(blueprint_path(spec))
    created = False
    if blueprint:
        return blueprint, created

    source = unreal.EditorAssetLibrary.load_asset(SOURCE_BLUEPRINT_PATH)
    if not source:
        raise RuntimeError(f"Missing source blueprint: {SOURCE_BLUEPRINT_PATH}")

    duplicated = unreal.EditorAssetLibrary.duplicate_asset(SOURCE_BLUEPRINT_PACKAGE, blueprint_package(spec))
    if not duplicated:
        raise RuntimeError(f"Failed to duplicate blueprint to {blueprint_package(spec)}")
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
        raise RuntimeError(f"Blueprint has no SplineComponent template: {blueprint.get_path_name()}")
    if not pcg_templates:
        raise RuntimeError(f"Blueprint has no PCGComponent template: {blueprint.get_path_name()}")

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


def spawn_validation_actor(spec, graph, index):
    label = f"{ACTOR_LABEL_PREFIX}_{spec['name']}_Validation"
    for actor in get_all_level_actors():
        if actor.get_actor_label() == label:
            unreal.EditorLevelLibrary.destroy_actor(actor)

    actor_class = unreal.load_class(None, blueprint_class_path(spec))
    if not actor_class:
        raise RuntimeError(f"Missing amount Blueprint class: {blueprint_class_path(spec)}")

    actor = unreal.EditorLevelLibrary.spawn_actor_from_class(
        actor_class,
        unreal.Vector(10400 + index * 420, 0, 0),
        unreal.Rotator(0, 0, 0),
    )
    actor.set_actor_label(label)
    configure_validation_spline(actor)

    pcg_components = actor.get_components_by_class(unreal.PCGComponent)
    if not pcg_components:
        raise RuntimeError(f"Validation actor has no PCGComponent: {label}")
    for component in pcg_components:
        component.set_graph(graph)
        component.cleanup(True)
        component.generate(True)
    return actor


def main():
    print("MCP_CUBELESS_ED_GROUND_AMOUNT_BLUEPRINTS_BUILD_BEGIN")
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).load_level(LEVEL)
    for index, spec in enumerate(AMOUNT_BLUEPRINT_SPECS):
        graph = unreal.EditorAssetLibrary.load_asset(spec["graph_path"])
        if not graph:
            raise RuntimeError(f"Missing amount graph for {spec['name']}: {spec['graph_path']}")
        blueprint, created = load_or_duplicate_blueprint(spec)
        templates = set_blueprint_pcg_graph(blueprint, graph)
        compile_and_save(blueprint)
        actor = spawn_validation_actor(spec, graph, index)
        template_rows = [
            (row["name"], row["class"], row["is_component"], row["is_root"], row["is_scene"])
            for row in templates
        ]
        print(f"amount={spec['name']}")
        print(f"production_blueprint={blueprint.get_path_name()}")
        print(f"production_class={blueprint_class_path(spec)}")
        print(f"created={created}")
        print(f"default_graph={spec['graph_path']}")
        print(f"component_templates={template_rows}")
        print(f"validation_actor={actor.get_actor_label()}")
        print(f"expected_points={spec['expected_points']}")
        print(f"expected_ism={spec['expected_ism']}")
    print("MCP_CUBELESS_ED_GROUND_AMOUNT_BLUEPRINTS_BUILD_END")


if __name__ == "__main__":
    main()
