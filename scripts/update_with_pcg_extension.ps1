[CmdletBinding()]
param(
    [string]$IntegrationBranch = "main",
    [string]$OriginRemote = "origin",
    [string]$UpstreamRemote = "upstream",
    [string]$UpstreamUrl = "https://github.com/chongdashu/unreal-mcp.git",
    [string]$UpstreamBranch = "main",
    [switch]$SkipVerification,
    [switch]$Push
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

function Invoke-Git {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
    }
}

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Command,

        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Command $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
    }
}

function Get-GitOutput {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments
    )

    $output = & git @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed with exit code $LASTEXITCODE."
    }
    return $output
}

function Test-GitMergeInProgress {
    $mergeHeadPath = @(& git rev-parse --git-path MERGE_HEAD 2>$null)
    if ($LASTEXITCODE -ne 0 -or $mergeHeadPath.Count -eq 0) {
        return $false
    }

    return Test-Path -LiteralPath $mergeHeadPath[0]
}

Push-Location $RepoRoot
try {
    $dirty = Get-GitOutput @("status", "--porcelain")
    if ($dirty) {
        throw "Working tree is not clean. Commit, stash, or discard changes before updating from upstream."
    }

    $remoteNames = Get-GitOutput @("remote")
    if ($remoteNames -notcontains $UpstreamRemote) {
        Invoke-Git @("remote", "add", $UpstreamRemote, $UpstreamUrl)
    }

    $upstreamPushUrl = Get-GitOutput @("remote", "get-url", "--push", $UpstreamRemote)
    if ($upstreamPushUrl -ne "DISABLED") {
        Invoke-Git @("remote", "set-url", "--push", $UpstreamRemote, "DISABLED")
    }

    Invoke-Git @("fetch", $OriginRemote, "--prune")
    Invoke-Git @("fetch", $UpstreamRemote, "--prune")
    Invoke-Git @("checkout", $IntegrationBranch)
    Invoke-Git @("pull", "--ff-only", $OriginRemote, $IntegrationBranch)

    $integrationHeadBeforeMerge = (Get-GitOutput @("rev-parse", "HEAD"))[0]
    $upstreamRef = "$UpstreamRemote/$UpstreamBranch"
    $upstreamHead = (Get-GitOutput @("rev-parse", $upstreamRef))[0]

    & git merge-base --is-ancestor $upstreamRef HEAD
    if ($LASTEXITCODE -eq 0) {
        Write-Host "'$IntegrationBranch' already contains '$upstreamRef'."
    }
    elseif ($LASTEXITCODE -eq 1) {
        Invoke-Git @("merge", "--no-commit", "--no-ff", $upstreamRef)
    }
    else {
        throw "git merge-base --is-ancestor $upstreamRef HEAD failed with exit code $LASTEXITCODE."
    }

    if (-not $SkipVerification) {
        Invoke-CheckedCommand "uv" @("--directory", ".\Python", "run", "python", "-m", "py_compile", "unreal_mcp_server.py", "tools\python_tools.py", "tools\pcg_tools.py")
        Invoke-CheckedCommand "uv" @("--directory", ".\Python", "run", "python", "-c", "import unreal_mcp_server; print('server import ok')")
        Invoke-CheckedCommand "uv" @("--directory", ".\Python", "run", "python", "-m", "py_compile", "unreal_mcp_server.py", "tools\texture_generation.py", "services\openai_image_service.py", "services\unreal_texture_importer.py")
    }

    $mergeInProgress = Test-GitMergeInProgress
    $currentHead = (Get-GitOutput @("rev-parse", "HEAD"))[0]
    if ($mergeInProgress) {
        if ($currentHead -ne $integrationHeadBeforeMerge) {
            throw "Merge state is active, but HEAD moved unexpectedly. Inspect the repository before continuing."
        }

        Invoke-Git @("commit", "-m", "Merge upstream MCP updates")
    }

    if ($Push) {
        Invoke-Git @("push", $OriginRemote, $IntegrationBranch)
    }

    Write-Host "Updated '$IntegrationBranch' with '$upstreamRef' at $upstreamHead."
    if (-not $Push) {
        Write-Host "Push was not requested; local changes remain unpushed if a merge commit was created."
    }
}
catch {
    if (Test-GitMergeInProgress) {
        Write-Warning "Update stopped with a merge in progress. Resolve and commit it, or run 'git merge --abort' from $RepoRoot to return to the pre-merge state."
    }

    Write-Warning "Update failed: $($_.Exception.Message)"
    throw
}
finally {
    Pop-Location
}
