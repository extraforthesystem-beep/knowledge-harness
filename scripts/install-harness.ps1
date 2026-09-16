# Deploy Knowledge Harness slash commands (Windows)
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$Cli = Join-Path $Root "packages\knowledge-harness\bin\knowledge-harness.js"

if (Test-Path $Cli) {
    node (Join-Path $Root "packages\knowledge-harness\scripts\bundle-assets.mjs") 2>$null
    node $Cli install -g -y @args
    exit $LASTEXITCODE
}

# Fallback legacy installer
$CmdSrc = Join-Path $Root "templates\commands"
$HomeDir = [System.Environment]::GetFolderPath('UserProfile')
$ResetOpenCode = $args -contains "--reset-opencode"

$ActiveCmds = @(
    "memory-sync.md",
    "feature-add.md",
    "memory-migrate.md",
    "memory-init.md",
    "memory-compact.md",
    "failure-log.md"
)

$RemovedCmds = @(
    "handoff.md",
    "extract-memory.md",
    "compact.md",
    "harness-sync.md"
)

function Get-OpenCodeJsonState($Path) {
    $legacy = @{
        '$schema' = 'https://opencode.ai/config.json'
        instructions = @('AGENTS.md', 'CROSS-IDE.md', '.memory/index.md')
    }
    $canonical = @{
        '$schema' = 'https://opencode.ai/config.json'
        instructions = @('AGENTS.md', 'CROSS-IDE.md', '.memory/index.md')
        permission = @{ '*' = 'allow' }
    }

    if (-not (Test-Path $Path)) { return "absent" }

    try {
        $raw = Get-Content $Path -Raw -Encoding utf8 | ConvertFrom-Json -AsHashtable
    } catch {
        return "custom"
    }

    $normalize = {
        param($Value)
        if ($null -eq $Value) { return $null }
        if ($Value -is [System.Collections.IDictionary]) {
            $out = [ordered]@{}
            foreach ($Key in ($Value.Keys | Sort-Object)) {
                $out[$Key] = & $normalize $Value[$Key]
            }
            return $out
        }
        if ($Value -is [System.Collections.IEnumerable] -and -not ($Value -is [string])) {
            $items = @()
            foreach ($Item in $Value) { $items += ,(& $normalize $Item) }
            return $items
        }
        return $Value
    }

    $parsedJson = (& $normalize $raw) | ConvertTo-Json -Depth 10 -Compress
    $legacyJson = (& $normalize $legacy) | ConvertTo-Json -Depth 10 -Compress
    $canonicalJson = (& $normalize $canonical) | ConvertTo-Json -Depth 10 -Compress

    if ($parsedJson -eq $canonicalJson) { return "canonical" }
    if ($parsedJson -eq $legacyJson) { return "managed-legacy" }
    return "custom"
}

function Write-OpenCodeJson($Path) {
@'
{
  "$schema": "https://opencode.ai/config.json",
  "instructions": [
    "AGENTS.md",
    "CROSS-IDE.md",
    ".memory/index.md"
  ],
  "permission": {
    "*": "allow"
  }
}
'@ | Set-Content $Path -Encoding utf8
}

function Reset-OpenCodeInstall() {
    $commandsDir = Join-Path $HomeDir ".config\opencode\commands"
    $globalAgents = Join-Path $HomeDir ".config\opencode\AGENTS.md"
    $projectJson = Join-Path $Root "opencode.json"

    foreach ($Name in ($ActiveCmds + $RemovedCmds)) {
        $target = Join-Path $commandsDir $Name
        if (Test-Path $target) {
            Remove-Item $target -Force
            Write-Host "  [-] $target" -ForegroundColor Yellow
        }
    }

    if ((Test-Path $globalAgents) -and ((Get-Content $globalAgents -Raw -Encoding utf8) -match "Global Knowledge Harness defaults")) {
        Remove-Item $globalAgents -Force
        Write-Host "  [-] $globalAgents" -ForegroundColor Yellow
    }

    if (Test-Path $projectJson) {
        $state = Get-OpenCodeJsonState $projectJson
        if ($state -in @("canonical", "managed-legacy")) {
            Remove-Item $projectJson -Force
            Write-Host "  [-] $projectJson" -ForegroundColor Yellow
        } elseif ($state -eq "custom") {
            Write-Host "  [~] $projectJson (preserved custom config)" -ForegroundColor Yellow
        }
    }
}

function Install-Commands($Dest) {
    if (-not (Test-Path $Dest)) { New-Item -ItemType Directory -Path $Dest -Force | Out-Null }
    foreach ($Name in $ActiveCmds) {
        $Src = Join-Path $CmdSrc $Name
        $Dst = Join-Path $Dest $Name
        Copy-Item $Src $Dst -Force
        Write-Host "  [+] $Dst" -ForegroundColor Green
    }
    foreach ($Name in $RemovedCmds) {
        $Dst = Join-Path $Dest $Name
        if (Test-Path $Dst) {
            Remove-Item $Dst -Force
            Write-Host "  [-] $Dst (alias removed)" -ForegroundColor Yellow
        }
    }
}

Write-Host "=== Knowledge Harness installer ===" -ForegroundColor Cyan
Write-Host "Source: $CmdSrc ($($ActiveCmds.Count) active commands)"

Write-Host "Claude Code"
Install-Commands (Join-Path $HomeDir ".claude\commands")

Write-Host "Antigravity Gemini CLI"
Install-Commands (Join-Path $HomeDir ".gemini\config\global_workflows")

Write-Host "Antigravity IDE"
Install-Commands (Join-Path $HomeDir ".gemini\antigravity\global_workflows")

Write-Host "Cursor global"
Install-Commands (Join-Path $HomeDir ".cursor\commands")

Write-Host "Cursor project"
Install-Commands (Join-Path $Root ".cursor\commands")

Write-Host "OpenCode"
if ($ResetOpenCode) {
    Write-Host "  [~] Resetting harness-managed OpenCode files before reinstall" -ForegroundColor Yellow
    Reset-OpenCodeInstall
}
Install-Commands (Join-Path $HomeDir ".config\opencode\commands")

Write-Host "OpenCode global router"
$OcDir = Join-Path $HomeDir ".config\opencode"
if (-not (Test-Path $OcDir)) { New-Item -ItemType Directory -Path $OcDir -Force | Out-Null }
@'
# Global Knowledge Harness defaults

**Daily:** `/feature-add` · `/memory-sync`
**One-time:** `/memory-migrate` · `/memory-init`
**Rare:** `/memory-compact` · `/failure-log`

Before any task in a harness project:
1. Read `.memory/index.md` if present
2. Read `.memory/progress/status.md` (or run `/memory-migrate` if flat `PROGRESS.md` exists)
3. Use `/graphify query` for codebase exploration
4. Run `/memory-sync` after updating memory

Legacy upgrade: `/memory-migrate` — flat `.memory/` to OKF layout. Copy scripts from `$env:HARNESS_HOME\scripts\` if missing.
'@ | Set-Content (Join-Path $OcDir "AGENTS.md") -Encoding utf8
Write-Host "  [+] $(Join-Path $OcDir 'AGENTS.md')" -ForegroundColor Green

$ProjectOpenCodeJson = Join-Path $Root "opencode.json"
$OpenCodeJsonState = Get-OpenCodeJsonState $ProjectOpenCodeJson
if ($OpenCodeJsonState -eq "absent") {
    Write-OpenCodeJson $ProjectOpenCodeJson
    Write-Host "  [+] $ProjectOpenCodeJson" -ForegroundColor Green
} elseif ($OpenCodeJsonState -eq "managed-legacy") {
    Write-OpenCodeJson $ProjectOpenCodeJson
    Write-Host "  [~] $ProjectOpenCodeJson (upgraded to canonical scaffold)" -ForegroundColor Yellow
} elseif ($OpenCodeJsonState -eq "canonical") {
    Write-Host "  [ok] $ProjectOpenCodeJson" -ForegroundColor Green
} else {
    Write-Host "  [~] $ProjectOpenCodeJson (preserved custom config)" -ForegroundColor Yellow
}

Write-Host "`n=== Done ===" -ForegroundColor Green
Write-Host "Active slash commands: $($ActiveCmds -replace '\.md$','' -join ', ')"
Write-Host "OpenCode reinstall:"
Write-Host "  npx knowledge-harness install -g -a opencode --reset-opencode -y"
Write-Host "  npx knowledge-harness install -p -a opencode --reset-opencode -y"
