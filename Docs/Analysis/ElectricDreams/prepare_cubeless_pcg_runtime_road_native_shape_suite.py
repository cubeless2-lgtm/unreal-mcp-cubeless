import importlib
import pathlib
import sys

import unreal


def load_road_module():
    script_dir = (
        pathlib.Path(unreal.Paths.project_dir())
        / "Plugins"
        / "CustomTools"
        / "Content"
        / "Python"
        / "ArtScripts"
    )
    if not script_dir.exists():
        raise RuntimeError(f"Missing Cubeless road script directory: {script_dir}")
    script_dir_text = str(script_dir)
    if script_dir_text not in sys.path:
        sys.path.append(script_dir_text)
    import CubelessRoadPCG

    return importlib.reload(CubelessRoadPCG)


def main():
    road_module = load_road_module()
    result = road_module.start_runtime_road_native_graph_shape_suite_smoke_test(
        timeout_seconds=8.0,
        keep_last_preview=False,
    )
    print("runtime_road_native_shape_suite_scheduled=True")
    print(f"runtime_road_native_shape_suite_status={result.get('status')}")
    print(f"runtime_road_native_shape_suite_shape_count={result.get('shape_count')}")
    print(f"runtime_road_native_shape_suite_report={result.get('report_path')}")
    print(
        "runtime_road_native_shape_suite_note=run deferred_verify after Unreal has ticked "
        "long enough for every route shape to finish"
    )


if __name__ == "__main__":
    main()
