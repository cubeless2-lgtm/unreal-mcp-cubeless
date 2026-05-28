param(
    [string]$BranchName = "local/pcg-tools"
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $PSScriptRoot

Push-Location $RepoRoot
try {
    git fetch origin
    git checkout main
    git pull --ff-only

    if (git show-ref --verify --quiet "refs/heads/$BranchName") {
        git checkout $BranchName
        git rebase main
    } else {
        git checkout -b $BranchName
    }

    Write-Host "Repository updated. Keep PCG extension changes on branch '$BranchName'."
} finally {
    Pop-Location
}
