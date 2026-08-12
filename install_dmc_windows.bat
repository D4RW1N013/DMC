@echo off
setlocal
title DMC Installer

echo ==========================================
echo DMC - Digital Machine Companion
echo Windows Installer
echo ==========================================
echo.

where python >nul 2>&1
if errorlevel 1 (
    echo Python was not found.
    echo Please install Python 3.11 or newer.
    start https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found:
python --version
echo.

where ollama >nul 2>&1
if errorlevel 1 (
    echo Ollama was not found.
    echo Opening Ollama download page...
    start https://ollama.com/download
    echo Install Ollama and run this installer again.
    pause
    exit /b 1
)

echo Ollama found.
echo Installing Python dependencies...

python -m pip install --upgrade pip

if exist requirements.txt (
    python -m pip install -r requirements.txt
)

echo.
echo Checking DMC model...

ollama list | findstr /i "qwen3:8b" >nul 2>&1
if errorlevel 1 (
    echo Downloading qwen3:8b...
    ollama pull qwen3:8b
)

echo.
echo DMC installation finished.
echo.

python -m dmc

pause
