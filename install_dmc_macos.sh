#!/bin/bash
set -e

echo "=========================================="
echo "DMC - Digital Machine Companion"
echo "macOS Installer"
echo "=========================================="
echo

if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 was not found."

    if command -v brew >/dev/null 2>&1; then
        brew install python
    else
        echo "Please install Python 3 first:"
        echo "https://www.python.org/downloads/macos/"
        exit 1
    fi
fi

if ! command -v ollama >/dev/null 2>&1; then
    echo "Ollama was not found."

    if command -v brew >/dev/null 2>&1; then
        brew install --cask ollama
    else
        echo "Please install Ollama:"
        echo "https://ollama.com/download"
        exit 1
    fi
fi

echo "Installing Python dependencies..."
python3 -m pip install --upgrade pip

if [ -f requirements.txt ]; then
    python3 -m pip install -r requirements.txt
fi

echo "Checking DMC model..."

if ! ollama list | grep -q "qwen3:8b"; then
    ollama pull qwen3:8b
fi

echo
echo "DMC installation complete."
echo

python3 -m dmc
