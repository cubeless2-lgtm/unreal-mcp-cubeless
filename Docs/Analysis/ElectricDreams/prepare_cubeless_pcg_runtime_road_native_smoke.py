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
    result = road_module.start_runtime_road_native_graph_live_smoke_test(
        keep_preview=False,
        timeout_seconds=6.0,
    )
    print("runtime_road_native_smoke_scheduled=True")
    print(f"runtime_road_native_smoke_status={result.get('status')}")
    print(f"runtime_road_native_smoke_graph={result.get('graph_path')}")
    print(f"runtime_road_native_smoke_report={result.get('report_path')}")
    print(
        "runtime_road_native_smoke_note=run deferred_verify after Unreal has ticked "
        "long enough for PCG generation to finish"
    )


if __name__ == "__main__":
    main()
