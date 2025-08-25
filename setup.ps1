<#
Installer for Reflex project (Windows)
- Assumes Python 3.12+ is installed and available in PATH
- Creates a venv folder in the project root (.\venv)
- Installs poetry inside the venv and runs `poetry install`
- Attempts to install bun using the official installer script
- Creates run.bat in project root
Notes:
- pip installs use --proxy "" (empty proxy) as requested
#>

# stop on errors
$ErrorActionPreference = 'Stop'

# paths
$ProjectDir = (Get-Location).ProviderPath
$VenvDir    = Join-Path $ProjectDir "venv"
$ScriptsDir  = Join-Path $VenvDir "Scripts"

# output helpers
function Write-Ok   { param($m) Write-Host $m -ForegroundColor Green }
function Write-Warn { param($m) Write-Host $m -ForegroundColor Yellow }
function Write-Err  { param($m) Write-Host $m -ForegroundColor Red }

Write-Host "Project directory: $ProjectDir"

# --- 1) Check python ---
$pythonCmdInfo = Get-Command python -ErrorAction SilentlyContinue
$pythonCmd = if ($pythonCmdInfo) { $pythonCmdInfo.Source } else { $null }

if (-not $pythonCmd) {
    Write-Err "Python 3.12+ not found in PATH. Please install Python and try again."
    exit 1
}

try {
    $ver = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
} catch {
    Write-Err "Failed to determine Python version: $($_.Exception.Message)"
    exit 2
}

$vParts = $ver -split '\.'
if ([int]$vParts[0] -lt 3 -or ([int]$vParts[0] -eq 3 -and [int]$vParts[1] -lt 12)) {
    Write-Err "Python 3.12 or newer is required. Current version: $ver"
    exit 3
}

Write-Ok "Found Python $ver"

# --- 2) Create venv ---
if (-not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment at $VenvDir ..."
    try {
        & $pythonCmd -m venv $VenvDir
        Write-Ok "Virtual environment created."
    } catch {
        Write-Err "Failed to create virtual environment: $($_.Exception.Message)"
        exit 4
    }
} else {
    Write-Ok "Virtual environment already exists at $VenvDir"
}

$VenvPython = Join-Path $ScriptsDir "python.exe"
if (-not (Test-Path $VenvPython)) {
    Write-Warn "python.exe not found in venv scripts folder ($VenvPython). Attempting to recreate venv."
    try {
        & $pythonCmd -m venv $VenvDir
    } catch {
        Write-Err "Failed to recreate venv: $($_.Exception.Message)"
        exit 5
    }
}

# --- 3) Upgrade pip and install poetry inside venv ---
Write-Host "Upgrading pip and installing poetry in venv"
try {
    & $VenvPython -m pip install --proxy="" --upgrade pip setuptools wheel | Out-Null
    & $VenvPython -m pip install --proxy="" poetry | Out-Null
    Write-Ok "Poetry installed inside venv."
} catch {
    Write-Err "Failed to install poetry in venv: $($_.Exception.Message)"
    exit 6
}

# --- 4) Install dependencies with poetry ---
Write-Host "Installing dependencies (poetry install) ..."
$poetryExe = Join-Path $ScriptsDir "poetry.exe"
# tell poetry to NOT create its own virtualenv, use current interpreter instead
$env:POETRY_VIRTUALENVS_CREATE = "false"
try {
    if (Test-Path $poetryExe) {
        & $poetryExe install --no-interaction
    } else {
        & $VenvPython -m poetry install --no-interaction
    }
    Write-Ok "Dependencies installed."
} catch {
    Write-Err "poetry install failed: $($_.Exception.Message)"
    exit 7
}

# --- 5) Install bun via official installer script ---
Write-Host "Attempting to install bun via official installer..."
$bunInstalled = $false
try {
    $installer = Invoke-RestMethod -Uri 'https://bun.sh/install.ps1' -UseBasicParsing
    if (-not $installer) { throw "Could not download bun installer" }
    Invoke-Expression $installer
    Write-Ok "bun installer executed. bun should be installed."
    $bunInstalled = $true
} catch {
    Write-Warn "Automatic bun installation failed: $($_.Exception.Message)"
    Write-Host "Please download bun from https://bun.sh and add bun.exe to PATH or copy it into $ScriptsDir"
}

# Try to copy bun.exe into venv\Scripts if bun was installed into known default location
if ($bunInstalled) {
    $possiblePaths = @(
        (Join-Path $env:LOCALAPPDATA "bun\bun.exe"),
        (Join-Path $env:USERPROFILE ".bun\bin\bun.exe"),
        (Join-Path $env:LOCALAPPDATA "Programs\bun\bun.exe")
    )
    foreach ($p in $possiblePaths) {
        if (Test-Path $p) {
            try {
                if (-not (Test-Path $ScriptsDir)) { New-Item -ItemType Directory -Path $ScriptsDir | Out-Null }
                Copy-Item -Path $p -Destination (Join-Path $ScriptsDir "bun.exe") -Force
                Write-Ok "Copied bun.exe from $p to $ScriptsDir"
                break
            } catch {
                Write-Warn "Failed to copy bun.exe from $p : $($_.Exception.Message)"
            }
        }
    }
}

# --- 6) Create run.bat in project root ---
$runBat = Join-Path $ProjectDir "run.bat"
$runContent = @'
@echo off
chcp 65001 >nul
title Reflex App
call "%~dp0venv\Scripts\activate"
poetry run reflex run --env prod
pause
'@

try {
    Set-Content -Path $runBat -Value $runContent -Encoding UTF8
    Write-Ok "run.bat created at $runBat"
} catch {
    Write-Warn "Failed to create run.bat: $($_.Exception.Message)"
}

# --- Done ---
Write-Ok "Setup completed."
Write-Host "To run the app:"
Write-Host '  .\venv\Scripts\activate'
Write-Host '  poetry run reflex run --env prod'
