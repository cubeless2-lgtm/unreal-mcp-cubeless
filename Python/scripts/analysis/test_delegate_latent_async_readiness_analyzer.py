#!/usr/bin/env python
"""Smoke tests for delegate_latent_async_readiness_analyzer.py."""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path
from typing import Optional, Sequence


SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import delegate_latent_async_readiness_analyzer as analyzer  # noqa: E402


def write_fixture(root: Path) -> None:
    source = root / "Source" / "FixtureGame"
    source.mkdir(parents=True)
    (source / "FixtureAsync.h").write_text(
        """
#pragma once
#include "Kismet/BlueprintAsyncActionBase.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FFixtureDone, int32, Value);
DECLARE_MULTICAST_DELEGATE_OneParam(FFixtureNative, bool);

UCLASS()
class UFixtureAsyncAction : public UBlueprintAsyncActionBase
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, meta=(BlueprintInternalUseOnly="true", WorldContext="WorldContextObject"))
    static UFixtureAsyncAction* WaitForFixture(UObject* WorldContextObject);

    virtual void Activate() override;

    UPROPERTY(BlueprintAssignable)
    FFixtureDone Completed;
};

class UFixtureCancellableAction : public UCancellableAsyncAction
{
    GENERATED_BODY()
public:
    UFUNCTION(BlueprintCallable, meta=(BlueprintInternalUseOnly="true"))
    static UFixtureCancellableAction* WatchFixture();

    virtual void Activate() override;

    UPROPERTY(BlueprintAssignable)
    FFixtureDone Canceled;
};

class UFixtureAbilityTask : public UAbilityTask
{
    GENERATED_BODY()
public:
    virtual void Activate() override;

    UPROPERTY(BlueprintAssignable)
    FFixtureDone Ready;
};
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (source / "FixtureAsync.cpp").write_text(
        """
#include "FixtureAsync.h"

UFixtureAsyncAction* UFixtureAsyncAction::WaitForFixture(UObject* WorldContextObject)
{
    return NewObject<UFixtureAsyncAction>();
}

void UFixtureAsyncAction::Activate()
{
    Completed.Broadcast(3);
    SetReadyToDestroy();
}

UFixtureCancellableAction* UFixtureCancellableAction::WatchFixture()
{
    return NewObject<UFixtureCancellableAction>();
}

void UFixtureCancellableAction::Activate()
{
    Canceled.Broadcast(4);
    Cancel();
}

void UFixtureAbilityTask::Activate()
{
    Ready.Broadcast(5);
    EndTask();
}

void UFixtureSubsystem::Start()
{
    Target->OnDone.AddDynamic(this, &ThisClass::HandleDone);
    FWorldDelegates::OnStartGameInstance.AddUObject(this, &ThisClass::HandleStart);
    Target->OnNativeDone.AddLambda([this]() { HandleDone(1); });
    AbilityComponent->AbilityTargetDataSetDelegate(CurrentSpecHandle, PredictionKey).AddUObject(this, &ThisClass::HandleAbilityData);
    Target->OnDone.Broadcast(7);
    Target->OnDone.RemoveAll(this);
    ActiveRequests.Remove(Request);
}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    (source / "FixtureK2Node.h").write_text(
        """
#pragma once
#include "K2Node_AsyncAction.h"

class UK2Node_AsyncFixture : public UK2Node_AsyncAction
{
};
""".strip()
        + "\n",
        encoding="utf-8",
    )


def run_fixture_smoke() -> None:
    with tempfile.TemporaryDirectory(prefix="mcp_delegate_async_fixture_") as temp_dir:
        project_root = Path(temp_dir) / "FixtureProject"
        output_dir = Path(temp_dir) / "out"
        project_root.mkdir()
        write_fixture(project_root)

        report = analyzer.build_report(project_root, str(project_root), output_dir, analyzer.base.repo_root_from_script(), None)
        json_path, md_path = analyzer.write_report(report, output_dir)

        totals = report["source_scan"]["pattern_totals"]
        assert totals["dynamic_delegate_declaration"] >= 1
        assert totals["native_delegate_declaration"] >= 1
        assert totals["blueprint_assignable_delegate"] >= 1
        assert totals["dynamic_binding"] >= 1
        assert totals["native_binding"] >= 1
        assert totals["delegate_broadcast"] >= 1
        assert totals["delegate_unbinding"] == 1
        assert totals["possible_delegate_unbinding"] == 1
        assert totals["async_action_class"] >= 1
        assert totals["blueprint_internal_async_factory"] >= 1
        assert totals["custom_k2_async_node"] >= 1
        lifecycle = report["source_scan"]["lifecycle_classifier"]
        assert lifecycle["site_count"] >= 5
        assert lifecycle["classification_counts"]["bp_event_dispatcher_candidate_with_cleanup"] >= 1
        assert lifecycle["classification_counts"]["engine_lifecycle_native_blocker"] >= 1
        assert lifecycle["classification_counts"]["native_delegate_lifecycle_blocker"] >= 1
        assert lifecycle["classification_counts"]["async_or_ability_task_candidate"] >= 1
        assert lifecycle["conversion_bucket_counts"]["native_required"] >= 1
        assert lifecycle["conversion_bucket_counts"]["async_or_ability_task"] >= 1
        async_inventory = report["source_scan"]["async_proxy_inventory"]
        async_summary = async_inventory["summary"]
        assert async_summary["kind_counts"]["blueprint_async_action"] >= 1
        assert async_summary["kind_counts"]["cancellable_async_action"] >= 1
        assert async_summary["kind_counts"]["ability_task"] >= 1
        assert async_summary["kind_counts"]["custom_k2_async_node"] >= 1
        assert async_summary["callback_delegate_count"] >= 3
        assert async_summary["factory_function_count"] >= 2
        assert async_summary["broadcast_count"] >= 3
        assert async_summary["classes_with_activate"] >= 3
        assert async_summary["classes_requiring_callback_exec_model"] >= 3
        assert async_inventory["authoring_status"] == "inventory_only_until_async_proxy_callback_exec_model_exists"
        assert report["verdict"]["current_status"] == "not_ready_for_generic_delegate_or_async_proxy_authoring"
        assert json_path.exists()
        assert md_path.exists()
        assert not (project_root / "lyra_delegate_latent_async_readiness_report.json").exists()


def run_external_smoke(project_root: Path, output_dir: Path) -> None:
    before_snapshot = analyzer.base.snapshot_project_tree(project_root)
    report = analyzer.build_report(
        project_root,
        str(project_root),
        output_dir,
        analyzer.base.repo_root_from_script(),
        None,
    )
    analyzer.write_report(report, output_dir)
    after_snapshot = analyzer.base.snapshot_project_tree(project_root)

    assert before_snapshot == after_snapshot, "External project tree was modified"
    assert report["source_scan"]["matched_file_count"] > 0
    assert report["verdict"]["current_status"] == "not_ready_for_generic_delegate_or_async_proxy_authoring"
    assert "dynamic_binding" in report["source_scan"]["pattern_totals"]
    assert "async_proxy_inventory" in report["source_scan"]


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

    print("delegate latent async readiness analyzer smoke passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
