#!/usr/bin/env python
"""Smoke tests for blueprint_asset_ancestry_analyzer.py."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Optional, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import blueprint_asset_ancestry_analyzer as analyzer  # noqa: E402


def fake_uasset(*strings: str) -> bytes:
    payload = bytearray(b"\xc1\x83\x2a\x9e")
    for value in strings:
        payload.extend(b"\x00")
        payload.extend(value.encode("utf-8"))
        payload.extend(b"\x00")
    return bytes(payload)


def write_fixture(root: Path) -> None:
    content = root / "Content"
    (content / "Characters" / "Abilities").mkdir(parents=True)
    (content / "UI").mkdir(parents=True)
    (content / "World").mkdir(parents=True)
    (root / "Plugins" / "GameFeatures" / "ShooterCore" / "Content" / "Experiences").mkdir(parents=True)

    (content / "Characters" / "Abilities" / "GA_Test.uasset").write_bytes(
        fake_uasset(
            "BlueprintGeneratedClass",
            "GeneratedClass",
            "BlueprintGeneratedClass'/Game/Characters/Abilities/GA_Test.GA_Test_C'",
            "ParentClass",
            "Class'/Script/LyraGame.LyraGameplayAbility'",
            "NativeParentClass",
            "Class'/Script/LyraGame.LyraGameplayAbility'",
        )
    )
    (content / "UI" / "W_Test.uasset").write_bytes(
        fake_uasset(
            "WidgetBlueprintGeneratedClass",
            "GeneratedClass",
            "WidgetBlueprintGeneratedClass'/Game/UI/W_Test.W_Test_C'",
            "ParentClass",
            "Class'/Script/CommonUI.CommonActivatableWidget'",
            "NativeParentClass",
            "Class'/Script/CommonUI.CommonActivatableWidget'",
        )
    )
    (content / "World" / "B_TestActor.uasset").write_bytes(
        fake_uasset(
            "BlueprintGeneratedClass",
            "GeneratedClass",
            "BlueprintGeneratedClass'/Game/World/B_TestActor.B_TestActor_C'",
            "ParentClass",
            "Class'/Script/Engine.Actor'",
            "NativeParentClass",
            "Class'/Script/Engine.Actor'",
        )
    )
    (
        root
        / "Plugins"
        / "GameFeatures"
        / "ShooterCore"
        / "Content"
        / "Experiences"
        / "B_GameFeatureExperience.uasset"
    ).write_bytes(
        fake_uasset(
            "BlueprintGeneratedClass",
            "LyraExperienceDefinition",
            "GeneratedClass",
            "BlueprintGeneratedClass'/ShooterCore/Experiences/B_GameFeatureExperience.B_GameFeatureExperience_C'",
            "ParentClass",
            "Class'/Script/LyraGame.LyraExperienceDefinition'",
            "NativeParentClass",
            "Class'/Script/LyraGame.LyraExperienceDefinition'",
        )
    )


def run_fixture_smoke() -> None:
    with tempfile.TemporaryDirectory(prefix="mcp_asset_ancestry_fixture_") as temp_dir:
        project_root = Path(temp_dir) / "FixtureProject"
        output_dir = Path(temp_dir) / "out"
        project_root.mkdir()
        write_fixture(project_root)

        report = analyzer.build_report(project_root, str(project_root), output_dir)
        analyzer.write_report(report, output_dir)

        summary = report["summary"]
        assert summary["asset_count"] == 4
        assert summary["blueprint_like_asset_count"] == 4
        assert summary["category_counts"]["gameplay_ability"] == 1
        assert summary["category_counts"]["common_ui_umg"] == 1
        assert summary["category_counts"]["actor_blueprint"] == 1
        assert summary["category_counts"]["game_feature_or_experience"] == 1
        assert summary["supported_candidate_count"] == 1
        assert (output_dir / "lyra_blueprint_asset_ancestry_report.json").exists()
        assert not (project_root / "lyra_blueprint_asset_ancestry_report.json").exists()


def run_external_smoke(project_root: Path, output_dir: Path) -> None:
    before_snapshot = analyzer.base.snapshot_project_tree(project_root)
    report = analyzer.build_report(project_root, str(project_root), output_dir)
    analyzer.write_report(report, output_dir)
    after_snapshot = analyzer.base.snapshot_project_tree(project_root)

    assert before_snapshot == after_snapshot, "External project tree was modified"
    assert report["summary"]["asset_count"] > 0
    assert report["summary"]["blueprint_like_asset_count"] > 0
    assert "gameplay_ability" in report["summary"]["category_counts"]
    assert "common_ui_umg" in report["summary"]["category_counts"]


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default="", help="Optional external project root for an additional smoke pass.")
    parser.add_argument(
        "--output-dir",
        default=str(analyzer.base.repo_root_from_script() / "Docs" / "Analysis" / "Lyra"),
        help="Output directory for the optional external project smoke.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    run_fixture_smoke()
    if args.project_root:
        run_external_smoke(Path(args.project_root).resolve(), Path(args.output_dir).resolve())
    print("blueprint asset ancestry analyzer smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
