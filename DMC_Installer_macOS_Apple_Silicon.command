#!/bin/bash
set -e
REPO_ZIP="https://github.com/D4RW1N013/DMC/archive/refs/heads/master.zip"
INSTALL_DIR="$HOME/DMC"

echo "=========================================="
echo "   DMC - macOS Apple Silicon Installer"
echo "=========================================="

if [ "$(uname -m)" != "arm64" ]; then
    echo "This installer is for Apple Silicon Macs."
    read -p "Press Enter to exit..."
    exit 1
fi

echo "[1/6] Checking Python 3.13..."
if command -v python3.13 >/dev/null 2>&1; then
    PYTHON="$(command -v python3.13)"
elif command -v brew >/dev/null 2>&1; then
    brew install python@3.13
    PYTHON="$(brew --prefix python@3.13)/bin/python3.13"
else
    echo "Homebrew is required for automatic Python installation."
    echo "Install it from https://brew.sh/"
    read -p "Press Enter to exit..."
    exit 1
fi
"$PYTHON" --version

echo "[2/6] Checking Ollama..."
if ! command -v ollama >/dev/null 2>&1; then
    curl -fsSL https://ollama.com/install.sh | sh
fi

echo "[3/6] Downloading DMC..."
TMP="$(mktemp -d)"
curl -L "$REPO_ZIP" -o "$TMP/DMC.zip"
rm -rf "$INSTALL_DIR"
mkdir -p "$INSTALL_DIR"
unzip -q "$TMP/DMC.zip" -d "$TMP"
SOURCE_DIR="$(find "$TMP" -maxdepth 1 -type d -name 'DMC-*' | head -n 1)"
cp -R "$SOURCE_DIR"/. "$INSTALL_DIR"/
rm -rf "$TMP"
cd "$INSTALL_DIR"

echo "[4/6] Installing Python dependencies..."
"$PYTHON" -m pip install --upgrade pip
"$PYTHON" -m pip install -r requirements.txt

echo "[5/6] Installing Playwright browser..."
"$PYTHON" -m playwright install || true

echo "Downloading Qwen3 8B..."
ollama pull qwen3:8b

echo "[6/6] Starting DMC..."
"$PYTHON" -m dmc
read -p "Press Enter to close..."
