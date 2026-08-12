@echo off
setlocal EnableExtensions EnableDelayedExpansion
title DMC Installer

set "REPO_ZIP=https://github.com/D4RW1N013/DMC/archive/refs/heads/master.zip"
set "INSTALL_DIR=%LOCALAPPDATA%\DMC"
set "PYTHON_URL=https://www.python.org/downloads/release/python-31314/"

echo.
echo ==========================================
echo        DMC - Digital Machine Companion
echo ==========================================
echo.

echo [1/6] Checking Python 3.13...
set "PYTHON_CMD="

where py >nul 2>&1
if not errorlevel 1 (
    py -3.13 --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=py -3.13"
)

if not defined PYTHON_CMD (
    echo Python 3.13 not found. Installing...
    where winget >nul 2>&1
    if errorlevel 1 (
        echo ERROR: winget is unavailable.
        echo Download Python manually:
        echo %PYTHON_URL%
        start "" "%PYTHON_URL%"
        pause
        exit /b 1
    )
    winget install --id Python.Python.3.13 -e --source winget --accept-package-agreements --accept-source-agreements
    if errorlevel 1 (
        echo ERROR: Python installation failed.
        pause
        exit /b 1
    )
    echo Python was installed. Run this installer again.
    pause
    exit /b 0
)
echo Python OK.
echo.

echo [2/6] Checking Ollama...
where ollama >nul 2>&1
if errorlevel 1 (
    echo Ollama not found. Installing...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "irm https://ollama.com/install.ps1 | iex"
    if errorlevel 1 (
        echo ERROR: Ollama installation failed.
        start "" "https://ollama.com/download/windows"
        pause
        exit /b 1
    )
)
echo Ollama OK.
echo.

echo [3/6] Downloading DMC...
if exist "%INSTALL_DIR%" rmdir /s /q "%INSTALL_DIR%"

set "TMP=%TEMP%\DMC_%RANDOM%"
mkdir "%TMP%"

powershell -NoProfile -ExecutionPolicy Bypass -Command "$ProgressPreference='SilentlyContinue'; Invoke-WebRequest -Uri '%REPO_ZIP%' -OutFile '%TMP%\DMC.zip'"
if errorlevel 1 (
    echo ERROR: Could not download DMC.
    pause
    exit /b 1
)

powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%TMP%\DMC.zip' -DestinationPath '%TMP%\expanded' -Force"
if errorlevel 1 (
    echo ERROR: Could not extract DMC.
    pause
    exit /b 1
)

for /d %%D in ("%TMP%\expanded\DMC-*") do set "SOURCE_DIR=%%D"
move "!SOURCE_DIR!" "%INSTALL_DIR%" >nul
rmdir /s /q "%TMP%"

cd /d "%INSTALL_DIR%"
echo DMC downloaded.
echo.

echo [4/6] Installing Python dependencies...
%PYTHON_CMD% -m pip install --upgrade pip
if errorlevel 1 (
    echo ERROR: pip update failed.
    pause
    exit /b 1
)
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Python dependencies failed.
    pause
    exit /b 1
)
echo.

echo [5/6] Installing Playwright browser...
%PYTHON_CMD% -m playwright install
if errorlevel 1 echo WARNING: Playwright browser installation failed.
echo.

echo Downloading Qwen3 8B...
ollama pull qwen3:8b
if errorlevel 1 (
    echo ERROR: Qwen3 8B download failed.
    pause
    exit /b 1
)

echo.
echo [6/6] Starting DMC...
%PYTHON_CMD% -m dmc
pause
