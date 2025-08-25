<#
Reflex Project Installer (Windows)
- Requires Python 3.12+
- Creates Poetry venv inside project (.venv)
- Installs Poetry in venv
- Installs all dependencies via Poetry
- Installs bun in .venv\Scripts
- Creates run.bat to launch Reflex
#>

$ErrorActionPreference = 'Stop'

$ProjectDir = (Get-Location).ProviderPath
$PoetryVenvDir = Join-Path $ProjectDir ".venv"
$ScriptsDir = Join-Path $PoetryVenvDir "Scripts"

function Write-Ok   { param($m) Write-Host $m -ForegroundColor Green }
function Write-Warn { param($m) Write-Host $m -ForegroundColor Yellow }
function Write-Err  { param($m) Write-Host $m -ForegroundColor Red }

Write-Host "Project directory: $ProjectDir"

# --- 1) Check Python ---
$pythonCmdInfo = Get-Command python -ErrorAction SilentlyContinue
$pythonCmd = if ($pythonCmdInfo) { $pythonCmdInfo.Source } else { $null }
if (-not $pythonCmd) { Write-Err "Python 3.12+ not found in PATH"; exit 1 }

$ver = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
$vParts = $ver -split '\.'
if ([int]$vParts[0] -lt 3 -or ([int]$vParts[0] -eq 3 -and [int]$vParts[1] -lt 12)) {
    Write-Err "Python 3.12+ required. Current: $ver"; exit 1
}
Write-Ok "Found Python $ver"

# --- 2) Create temporary venv to install Poetry ---
$tempVenvDir = Join-Path $ProjectDir "__poetry_temp_venv"
if (-not (Test-Path $tempVenvDir)) {
    Write-Host "Creating temporary venv to install Poetry..."
    & $pythonCmd -m venv $tempVenvDir
}
$tempPython = Join-Path $tempVenvDir "Scripts\python.exe"

# Upgrade pip and install Poetry in temp venv
Write-Host "Installing Poetry..."
& $tempPython -m pip install --proxy="" --upgrade pip setuptools wheel | Out-Null
& $tempPython -m pip install --proxy="" poetry | Out-Null
$tempPoetry = Join-Path $tempVenvDir "Scripts\poetry.exe"

# --- 3) Configure Poetry to create venv inside project ---
& $tempPoetry config virtualenvs.in-project true
Write-Ok "Poetry configured to create venv inside project"

# --- 4) Install dependencies (Poetry will create .venv) ---
Write-Host "Installing dependencies via Poetry..."
& $tempPoetry install --no-interaction
Write-Ok "Dependencies installed inside .venv"

# --- 5) Remove temporary Poetry venv ---
Remove-Item $tempVenvDir -Recurse -Force
Write-Ok "Temporary Poetry installer venv removed"

# --- 6) Install bun into .venv\Scripts ---
Write-Host "Installing bun..."
try {
    $installer = Invoke-RestMethod -Uri 'https://bun.sh/install.ps1' -UseBasicParsing
    Invoke-Expression $installer
    Write-Ok "bun installer executed"

    # Copy bun.exe into .venv\Scripts
    $possiblePaths = @(
        (Join-Path $env:LOCALAPPDATA "bun\bun.exe"),
        (Join-Path $env:USERPROFILE ".bun\bin\bun.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\bun\bun.exe")
    )
    foreach ($p in $possiblePaths) {
        if (Test-Path $p) {
            Copy-Item -Path $p -Destination (Join-Path $ScriptsDir "bun.exe") -Force
            Write-Ok "Copied bun.exe to $ScriptsDir"
            break
        }
    }
} catch {
    Write-Warn "Automatic bun installation failed: $($_.Exception.Message)"
    Write-Host "Please download bun manually and copy bun.exe into $ScriptsDir"
}

# --- 7) Create run.bat ---
$runBat = Join-Path $ProjectDir "run.bat"
$runContent = @'
@echo off
chcp 65001 >nul
title Reflex App
call "%~dp0.venv\Scripts\activate"
poetry run reflex run --env prod
pause
'@
Set-Content -Path $runBat -Value $runContent -Encoding UTF8
Write-Ok "run.bat created at $runBat"

Write-Ok "Setup completed. Run run.bat to start the application."
