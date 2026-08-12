@echo off
setlocal EnableExtensions EnableDelayedExpansion

title DMC Installer

REM ============================================================
REM DMC Windows Installer v2
REM Uses GitHub's codeload endpoint for the repository archive.
REM ============================================================

set "REPO_ZIP=https://codeload.github.com/D4RW1N013/DMC/zip/refs/heads/master"
set "INSTALL_DIR=%LOCALAPPDATA%\DMC"
set "PYTHON_URL=https://www.python.org/downloads/release/python-31314/"
set "OLLAMA_URL=https://ollama.com/download/OllamaSetup.exe"

echo.
echo ==========================================
echo       DMC - Digital Machine Companion
echo ==========================================
echo.

REM ------------------------------------------------------------
REM 1. Python
REM ------------------------------------------------------------
echo [1/6] Checking Python 3.13...

set "PYTHON_CMD="

where py >nul 2>&1
if not errorlevel 1 (
    py -3.13 --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=py -3.13"
)

if not defined PYTHON_CMD (
    echo Python 3.13 was not found.
    echo Installing with winget...

    where winget >nul 2>&1
    if errorlevel 1 (
        echo ERROR: winget is unavailable.
        echo Please install Python 3.13 manually:
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

    echo.
    echo Python was installed.
    echo Please run this installer again.
    pause
    exit /b 0
)

echo Python OK.
echo.

REM ------------------------------------------------------------
REM 2. Ollama
REM ------------------------------------------------------------
echo [2/6] Checking Ollama...

where ollama >nul 2>&1
if errorlevel 1 (
    echo Ollama was not found.
    echo Downloading official Ollama installer...

    set "OLLAMA_SETUP=%TEMP%\OllamaSetup.exe"

    curl.exe -L --fail --retry 3 --retry-delay 2 "%OLLAMA_URL%" -o "!OLLAMA_SETUP!"

    if errorlevel 1 (
        echo ERROR: Could not download Ollama.
        echo Opening official download page...
        start "" "https://ollama.com/download/windows"
        pause
        exit /b 1
    )

    start /wait "" "!OLLAMA_SETUP!"

    where ollama >nul 2>&1
    if errorlevel 1 (
        echo ERROR: Ollama was not detected after installation.
        echo Please restart Windows and run the installer again.
        pause
        exit /b 1
    )
)

echo Ollama OK.
echo.

REM ------------------------------------------------------------
REM 3. Download DMC
REM ------------------------------------------------------------
echo [3/6] Downloading DMC...
echo Using GitHub codeload...

if exist "%INSTALL_DIR%" (
    echo Existing DMC installation found.
    echo Replacing it with the current GitHub version...
    rmdir /s /q "%INSTALL_DIR%"
)

set "TMP=%TEMP%\DMC_%RANDOM%_%RANDOM%"
mkdir "%TMP%"
mkdir "%TMP%\expanded"

echo Downloading repository ZIP...

curl.exe -L --fail --retry 5 --retry-delay 3 "%REPO_ZIP%" -o "%TMP%\DMC.zip"

if errorlevel 1 (
    echo.
    echo ERROR: Could not download DMC from GitHub.
    echo.
    echo The GitHub codeload endpoint also failed.
    echo If normal GitHub pages work but downloads do not,
    echo your network, firewall, proxy or security software
    echo may be blocking GitHub download traffic.
    echo.
    echo Repository:
    echo https://github.com/D4RW1N013/DMC
    rmdir /s /q "%TMP%" 2>nul
    pause
    exit /b 1
)

if not exist "%TMP%\DMC.zip" (
    echo ERROR: DMC ZIP was not created.
    rmdir /s /q "%TMP%" 2>nul
    pause
    exit /b 1
)

echo Extracting DMC...

powershell -NoProfile -ExecutionPolicy Bypass -Command "Expand-Archive -LiteralPath '%TMP%\DMC.zip' -DestinationPath '%TMP%\expanded' -Force"

if errorlevel 1 (
    echo ERROR: Could not extract DMC.
    rmdir /s /q "%TMP%" 2>nul
    pause
    exit /b 1
)

set "SOURCE_DIR="

for /d %%D in ("%TMP%\expanded\DMC-*") do set "SOURCE_DIR=%%D"

if not defined SOURCE_DIR (
    echo ERROR: DMC source directory was not found.
    rmdir /s /q "%TMP%" 2>nul
    pause
    exit /b 1
)

mkdir "%INSTALL_DIR%"
xcopy "%SOURCE_DIR%\*" "%INSTALL_DIR%\" /E /I /H /Y >nul

rmdir /s /q "%TMP%"

if not exist "%INSTALL_DIR%\dmc\__main__.py" (
    echo ERROR: DMC installation appears incomplete.
    pause
    exit /b 1
)

cd /d "%INSTALL_DIR%"

echo DMC downloaded successfully.
echo.

REM ------------------------------------------------------------
REM 4. Python dependencies
REM ------------------------------------------------------------
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

echo Dependencies installed.
echo.

REM ------------------------------------------------------------
REM 5. Playwright + Ollama model
REM ------------------------------------------------------------
echo [5/6] Installing Playwright browser...

%PYTHON_CMD% -m playwright install
if errorlevel 1 (
    echo WARNING: Playwright browser installation failed.
)

echo.
echo Checking Ollama service...

curl.exe -s http://127.0.0.1:11434/api/tags >nul 2>&1

if errorlevel 1 (
    echo Starting Ollama...
    start "" ollama serve
    timeout /t 4 /nobreak >nul
)

echo.
echo Downloading Qwen3 8B...
ollama pull qwen3:8b

if errorlevel 1 (
    echo ERROR: Could not download qwen3:8b.
    pause
    exit /b 1
)

echo.
echo Qwen3 8B is ready.
echo.

REM ------------------------------------------------------------
REM 6. Start DMC
REM ------------------------------------------------------------
echo [6/6] Starting DMC...
echo.
echo ==========================================
echo DMC installation completed successfully.
echo ==========================================
echo.

%PYTHON_CMD% -m dmc

pause
