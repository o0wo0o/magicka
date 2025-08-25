<#
Installer for Reflex project (Windows)
- Assumes Python 3.12+ is installed globally
- Creates venv in project root
- Installs poetry and dependencies via poetry install
- Installs bun via official installer
- Creates run.bat to launch Reflex
#>

set -e

$ProjectDir = (Get-Location).ProviderPath
$VenvDir = Join-Path $ProjectDir "venv"
$ScriptsDir = Join-Path $VenvDir "Scripts"

function Write-Ok { param($m) Write-Host $m -ForegroundColor Green }
function Write-Warn { param($m) Write-Host $m -ForegroundColor Yellow }
function Write-Err { param($m) Write-Host $m -ForegroundColor Red }

Write-Host "Project directory: $ProjectDir"

# --- 1) Check python ---
$pythonCmd = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $pythonCmd) { throw "Python 3.12+ не найден в PATH. Установи Python." }

$ver = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
$vParts = $ver -split '\.'
if ([int]$vParts[0] -lt 3 -or ([int]$vParts[0] -eq 3 -and [int]$vParts[1] -lt 12)) {
    throw "Нужен Python 3.12+, текущий: $ver"
}
Write-Ok "Python $ver найден"

# --- 2) Create venv ---
if (-not (Test-Path $VenvDir)) {
    Write-Host "Создаём venv в $VenvDir ..."
    & $pythonCmd -m venv $VenvDir
    Write-Ok "venv создан"
} else { Write-Ok "venv уже существует" }

$VenvPython = Join-Path $ScriptsDir "python.exe"

# --- 3) Upgrade pip and install poetry ---
Write-Host "Обновляем pip и устанавливаем poetry..."
& $VenvPython -m pip install --upgrade pip setuptools wheel | Out-Null
& $VenvPython -m pip install poetry | Out-Null
Write-Ok "poetry установлен в venv"

# --- 4) Install dependencies ---
Write-Host "Устанавливаем зависимости (poetry install)..."
$poetryExe = Join-Path $ScriptsDir "poetry.exe"
if (Test-Path $poetryExe) {
    & $poetryExe install --no-interaction
} else {
    & $VenvPython -m poetry install --no-interaction
}
Write-Ok "Зависимости установлены"

# --- 5) Install bun via official installer ---
Write-Host "Устанавливаем bun через официальный скрипт..."
try {
    iex "& { $(irm https://bun.sh/install.ps1) }"
    Write-Ok "bun установлен"
} catch {
    Write-Warn "Не удалось автоматически установить bun: $_"
    Write-Host "Скачай вручную с https://bun.sh и добавь bun.exe в PATH"
}

# --- 6) Create run.bat ---
$runBat = Join-Path $ProjectDir "run.bat"
$runContent = @"
@echo off
chcp 65001 >nul
title Reflex App
call `"%~dp0venv\Scripts\activate`"
poetry run reflex run --env prod
pause
"@

Set-Content -Path $runBat -Value $runContent -Encoding UTF8
Write-Ok "run.bat создан в $runBat"

Write-Ok "Установка завершена! Запускай run.bat для старта приложения."
