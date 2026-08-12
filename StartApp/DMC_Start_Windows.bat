@echo off
setlocal

set "DMC_DIR=%LOCALAPPDATA%\DMC"

title DMC

if not exist "%DMC_DIR%\dmc\__main__.py" (
    echo DMC wurde nicht gefunden.
    echo Bitte zuerst den DMC Installer ausfuehren.
    pause
    exit /b 1
)

where ollama >nul 2>&1
if errorlevel 1 (
    echo Ollama wurde nicht gefunden.
    echo Bitte zuerst den DMC Installer ausfuehren.
    pause
    exit /b 1
)

echo Starte Ollama...
start "" ollama serve

timeout /t 2 /nobreak >nul

cd /d "%DMC_DIR%"

echo Starte DMC...
py -3.13 -m dmc

pause
