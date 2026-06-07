#!/usr/bin/env python
"""Smoke tests for external_project_readiness_analyzer.py."""

from __future__ import annotations

import argparse
import json
import sys
import tempfile
from pathlib import Path
from typing import Optional, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import external_project_readiness_analyzer as analyzer  # noqa: E402


def write_fixture_project(root: Path) -> None:
    (root / "Source" / "FixtureGame").mkdir(parents=True)
    (root / "Config").mkdir()
    (root / "Content" / "Blueprints").mkdir(parents=True)
    (root / "Fixture.uproject").write_text(
        json.dumps(
            {
                "FileVersion": 3,
                "EngineAssociation": "5.7",
                "Modules": [{"Name": "FixtureGame", "Type": "Runtime"}],
                "Plugins": [
                    {"Name": "GameplayAbilities", "Enabled": True},
                    {"Name": "EnhancedInput", "Enabled": True},
                    {"Name": "CommonUI", "Enabled": True},
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    (root / "Config" / "DefaultGame.ini").write_text(
        "[/Script/GameplayTags.GameplayTagsSettings]\n+GameplayTagList=(Tag=\"Fixture.Readiness\")\n",
        encoding="utf-8",
    )
    (root / "Source" / "FixtureGame" / "FixtureActor.h").write_text(
        """
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GameplayTagContainer.h"
#include "AbilitySystemComponent.h"
#include "FixtureActor.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FFixtureChanged, int32, Value);

UCLASS(Blueprintable)
class AFixtureActor : public AActor
{
    GENERATED_BODY()

public:
    UPROPERTY(BlueprintReadWrite, ReplicatedUsing=OnRep_Count)
    int32 Count = 0;

    UPROPERTY(BlueprintAssignable)
    FFixtureChanged OnChanged;

    UFUNCTION(BlueprintCallable, Server, Reliable)
    void ServerDoThing();

    UFUNCTION()
    void OnRep_Count();

    virtual void GetLifetimeReplicatedProps(TArray<FLifetimeProperty>& OutLifetimeProps) const override;
};

class UFixtureWidget : public UUserWidget
{
    GENERATED_BODY()
};
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (root / "Source" / "FixtureGame" / "FixtureActor.cpp").write_text(
        """
#include "FixtureActor.h"

void AFixtureActor::ServerDoThing()
{
    if (Count > 3)
    {
        OnChanged.Broadcast(Count);
    }
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (root / "Content" / "Blueprints" / "BP_Fixture.uasset").write_bytes(b"fixture")


def run_fixture_smoke() -> None:
    with tempfile.TemporaryDirectory(prefix="mcp_readiness_fixture_") as temp_dir:
        temp_root = Path(temp_dir)
        project_root = temp_root / "FixtureProject"
        output_dir = temp_root / "out"
        project_root.mkdir()
        write_fixture_project(project_root)

        report = analyzer.build_report(
            project_root=project_root,
            requested_project_root=str(project_root),
            output_dir=output_dir,
            mcp_root=analyzer.repo_root_from_script(),
            plugin_root=None,
        )
        json_path, md_path = analyzer.write_report(report, output_dir)

        assert json_path.exists(), "JSON report was not written"
        assert md_path.exists(), "Markdown report was not written"
        assert report["read_only_policy"]["project_mutation_allowed"] is False
        assert report["source_scan"]["file_count"] == 2
        assert report["content_scan"]["asset_counts"][".uasset"] == 1
        assert "networking_replication" in report["source_scan"]["pattern_hits"]
        assert report["readiness"]["blocked_categories"], "Expected blocked native categories"
        findings = {item["key"]: item for item in report["readiness"]["all_findings"]}
        assert "common_ui_umg" in findings
        assert "umg_tools" not in findings["common_ui_umg"]["mapped_capabilities"]
        assert "umg_tools" in findings["common_ui_umg"]["capability_groups"]
        assert not (project_root / "lyra_readiness_report.json").exists(), "Report leaked into project root"


def run_external_project_smoke(project_root: Path, output_dir: Path) -> None:
    before_snapshot = analyzer.snapshot_project_tree(project_root)
    report = analyzer.build_report(
        project_root=project_root,
        requested_project_root=str(project_root),
        output_dir=output_dir,
        mcp_root=analyzer.repo_root_from_script(),
        plugin_root=analyzer.repo_root_from_script().parent / "CubelessStylized" / "Plugins" / "UnrealMCP",
    )
    analyzer.write_report(report, output_dir)
    after_snapshot = analyzer.snapshot_project_tree(project_root)

    assert before_snapshot == after_snapshot, "External project tree was modified"
    assert report["source_scan"]["file_count"] > 0, "External project source scan was empty"
    assert report["readiness"]["blocked_categories"], "Expected native blockers in external project"
    assert not analyzer.path_is_relative_to(output_dir, project_root), "Output dir must stay outside external project"


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-root", default="", help="Optional external project root for an additional smoke pass.")
    parser.add_argument(
        "--output-dir",
        default=str(analyzer.repo_root_from_script() / "Docs" / "Analysis" / "Lyra"),
        help="Output directory for the optional external project smoke.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_arg_parser().parse_args(argv)
    run_fixture_smoke()

    if args.project_root:
        run_external_project_smoke(Path(args.project_root).resolve(), Path(args.output_dir).resolve())

    print("external project readiness analyzer smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
