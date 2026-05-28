param(
    [string]$ProjectRoot
)

$ErrorActionPreference = "Stop"

$scriptPath = $MyInvocation.MyCommand.Path
$scriptsRoot = Split-Path -Parent $scriptPath
$repoRoot = Split-Path -Parent $scriptsRoot

if ([string]::IsNullOrWhiteSpace($ProjectRoot)) {
    $repoParent = Split-Path -Parent $repoRoot
    $ProjectRoot = Join-Path $repoParent "CubelessStylized"
}

$projectRootPath = Resolve-Path -LiteralPath $ProjectRoot
$projectParent = Split-Path -Parent $projectRootPath.Path
$repoRoot = Join-Path $projectParent "unreal-mcp"
$pythonRoot = Join-Path $repoRoot "Python"
$serverScript = Join-Path $pythonRoot "unreal_mcp_server.py"

if (-not (Test-Path -LiteralPath $repoRoot -PathType Container)) {
    throw "Expected unreal-mcp at '$repoRoot'. Clone it under the CubelessStylized parent folder first."
}

if (-not (Test-Path -LiteralPath $serverScript -PathType Leaf)) {
    throw "Expected MCP server script at '$serverScript'. Check the unreal-mcp checkout."
}

& uv --directory $pythonRoot run unreal_mcp_server.py
