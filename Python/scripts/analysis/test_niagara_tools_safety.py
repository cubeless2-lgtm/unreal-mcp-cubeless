#!/usr/bin/env python
"""Offline safety checks for Niagara MCP temp-only mutation boundaries."""

from __future__ import annotations

from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[2]
    source = (repo_root / "tools" / "niagara_tools.py").read_text(encoding="utf-8")

    assert 'normalized_temp_folder != "/Game/_MCP_Temp"' in source
    assert 'not normalized_temp_folder.startswith("/Game/_MCP_Temp/")' in source
    assert "temp_folder must be under /Game/_MCP_Temp" in source
    assert 'startswith("/Game/_MCP_Temp/")' in source
    assert "save=true is allowed only for Niagara Systems under /Game/_MCP_Temp" in source
    assert "temp_folder must be under /Game/\"" not in source

    print("Niagara tool safety smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
