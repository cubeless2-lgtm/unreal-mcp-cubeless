"""Project-relative path helpers for Cubeless analysis scripts."""

from __future__ import annotations

import os
from pathlib import Path


def _as_posix(path: Path) -> str:
    return path.resolve().as_posix()


def _quote_cmd_arg(value: str) -> str:
    unquoted = value.strip()
    if len(unquoted) >= 2 and unquoted[0] == unquoted[-1] == '"':
        unquoted = unquoted[1:-1]
    escaped = unquoted.replace('"', r'\"')
    return f'"{escaped}"'


def _path_or_command(value: str) -> str:
    unquoted = value.strip()
    if len(unquoted) >= 2 and unquoted[0] == unquoted[-1] == '"':
        unquoted = unquoted[1:-1]
    if "/" not in unquoted and "\\" not in unquoted and not Path(unquoted).is_absolute():
        return unquoted
    return _as_posix(Path(unquoted).expanduser())


def mcp_repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def workspace_parent() -> Path:
    return mcp_repo_root().parent


def cubeless_project_root() -> Path:
    for name in ("CUBELESS_PROJECT_ROOT", "CUBELESS_STYLIZED_ROOT", "UNREAL_PROJECT_ROOT"):
        value = os.environ.get(name)
        if value:
            return Path(value).expanduser().resolve()

    project = os.environ.get("CUBELESS_UPROJECT")
    if project:
        return Path(project).expanduser().resolve().parent

    return (workspace_parent() / "CubelessStylized").resolve()


def wrong_workspace_project_root() -> Path:
    value = os.environ.get("CUBELESS_WRONG_WORKSPACE_ROOT")
    if value:
        return Path(value).expanduser().resolve()
    return (workspace_parent() / "CubelessStylized-delete-sky-main").resolve()


def default_cubeless_uproject() -> str:
    return _as_posix(cubeless_project_root() / "StylizedCubeless.uproject")


def default_wrong_workspace_uproject() -> str:
    return _as_posix(wrong_workspace_project_root() / "StylizedCubeless.uproject")


def cubeless_content_path(*parts: str) -> str:
    return _as_posix(cubeless_project_root() / "Content" / Path(*parts))


def cubeless_plugin_path(*parts: str) -> str:
    return _as_posix(cubeless_project_root() / "Plugins" / Path(*parts))


def cubeless_unreal_mcp_dll_path() -> str:
    return cubeless_plugin_path("UnrealMCP", "Binaries", "Win64", "UnrealEditor-UnrealMCP.dll")


def wrong_workspace_unreal_mcp_dll_path() -> str:
    return _as_posix(
        wrong_workspace_project_root()
        / "Plugins"
        / "UnrealMCP"
        / "Binaries"
        / "Win64"
        / "UnrealEditor-UnrealMCP.dll"
    )


def cubeless_unreal_mcp_source_path(*parts: str) -> str:
    return cubeless_plugin_path("UnrealMCP", "Source", "UnrealMCP", *parts)


def _coerce_unreal_root(path: Path) -> Path:
    expanded = path.expanduser()
    if expanded.name.lower() == "engine":
        return expanded.parent
    return expanded


def default_unreal_engine_root() -> Path | None:
    for name in ("UE_ENGINE_ROOT", "UE_SOURCE_ROOT", "UNREAL_ENGINE_ROOT", "UE_ROOT"):
        value = os.environ.get(name)
        if value:
            return _coerce_unreal_root(Path(value)).resolve()

    sibling_source_root = workspace_parent() / "UnrealEngine"
    if (sibling_source_root / "Engine").exists():
        return sibling_source_root.resolve()
    return None


def default_unreal_editor_exe() -> str:
    editor_exe = os.environ.get("UE_EDITOR_EXE")
    if editor_exe:
        return _path_or_command(editor_exe)

    engine_root = default_unreal_engine_root()
    if engine_root:
        return _as_posix(engine_root / "Engine" / "Binaries" / "Win64" / "UnrealEditor.exe")
    return "UnrealEditor.exe"


def default_ubt_build_command() -> str:
    build_bat = os.environ.get("UE_BUILD_BAT")
    if build_bat:
        build_bat = _path_or_command(build_bat)
    else:
        engine_root = default_unreal_engine_root()
        build_bat = (
            _as_posix(engine_root / "Engine" / "Build" / "BatchFiles" / "Build.bat")
            if engine_root
            else "Build.bat"
        )
    return (
        f"{_quote_cmd_arg(build_bat)} "
        "StylizedCubelessEditor Win64 Development "
        f"-Project={_quote_cmd_arg(default_cubeless_uproject())} "
        "-WaitMutex -NoHotReloadFromIDE"
    )


def default_port_owner_command_line() -> str:
    return (
        f"{_quote_cmd_arg(default_unreal_editor_exe())} "
        f"{_quote_cmd_arg(default_wrong_workspace_uproject())} -log"
    )


def default_lyra_project_candidates() -> list[Path]:
    candidates: list[Path] = []
    env_path = os.environ.get("LYRA_PROJECT_ROOT")
    if env_path:
        candidates.append(Path(env_path).expanduser())
    candidates.append(workspace_parent() / "LyraStarterGame")
    return candidates
