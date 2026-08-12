#!/bin/bash

DMC_DIR="$HOME/DMC"

echo "=========================================="
echo "          DMC START - APPLE SILICON"
echo "=========================================="
echo ""

if [ "$(uname -m)" != "arm64" ]; then
    echo "Dieser Starter ist für Apple Silicon Macs."
    echo "Erkannt: $(uname -m)"
    read -p "Press Enter to exit..."
    exit 1
fi

if [ ! -f "$DMC_DIR/dmc/__main__.py" ]; then
    echo "DMC wurde nicht gefunden."
    echo "Bitte zuerst den DMC Installer ausführen."
    read -p "Press Enter to exit..."
    exit 1
fi

if ! command -v ollama >/dev/null 2>&1; then
    echo "Ollama wurde nicht gefunden."
    echo "Bitte zuerst den DMC Installer ausführen."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "Starte Ollama..."
ollama serve >/tmp/dmc_ollama.log 2>&1 &

sleep 2

cd "$DMC_DIR"

echo "Starte DMC..."

if command -v python3.13 >/dev/null 2>&1; then
    python3.13 -m dmc
else
    echo "Python 3.13 wurde nicht gefunden."
    read -p "Press Enter to exit..."
    exit 1
fi

read -p "Press Enter to exit..."
