#!/usr/bin/env python
"""Offline safety checks for Niagara MCP temp-only mutation boundaries."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    source = (repo_root / "tools" / "niagara_tools.py").read_text(encoding="utf-8")

    assert "allow_source_edit: bool = False" in source
    assert '"allow_source_edit": allow_source_edit' in source
    assert "Allow edits outside /Game/_MCP_Temp" in source
    assert (
        "Allow editing target systems outside /Game/_MCP_Temp/NiagaraGenerated/"
        in source
    )
    assert "allow_source_compile: bool = False" in source
    assert '"allow_source_compile": allow_source_compile' in source
    assert "temp_folder must be under /Game/\"" not in source

    print("Niagara tool safety smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
