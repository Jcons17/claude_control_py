#!/bin/bash
# =============================================================
#  launch.sh — Haz doble clic en este archivo para iniciar
#  Voice Computer Use en tu Mac Mini M4
# =============================================================

# Directorio donde está este script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

echo "🚀 Iniciando Voice Computer Use..."
echo ""

# --- Verifica que Python 3 esté instalado ---
if ! command -v python3 &> /dev/null; then
    osascript -e 'display alert "Python 3 no encontrado" message "Instala Python desde https://python.org antes de continuar."'
    exit 1
fi

# --- Crea entorno virtual si no existe ---
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual..."
    python3 -m venv .venv
fi

# --- Activa el entorno virtual ---
source .venv/bin/activate

# --- Instala dependencias si hace falta ---
if [ ! -f ".venv/.deps_installed" ]; then
    echo "📥 Instalando dependencias (solo la primera vez, puede tardar)..."
    pip3 install --upgrade pip --quiet

    # Whisper nativo para Apple Silicon
    pip3 install mlx-whisper --quiet

    # Audio
    pip3 install sounddevice soundfile numpy --quiet

    # Anthropic SDK
    pip3 install anthropic --quiet

    # cliclick para control del mouse (instalar via Homebrew si no está)
    if ! command -v cliclick &> /dev/null; then
        echo "🖱️  Instalando cliclick para control del mouse..."
        brew install cliclick 2>/dev/null || echo "⚠️  Instala Homebrew primero: https://brew.sh"
    fi

    touch .venv/.deps_installed
    echo "✅ Dependencias instaladas."
fi

echo ""
echo "============================================"
echo "  Voice Computer Use — iniciando ahora..."
echo "============================================"
echo ""

# --- Corre el programa en una ventana de Terminal visible ---
osascript <<EOF
tell application "Terminal"
    activate
    do script "cd '$DIR' && source .venv/bin/activate && python3 main.py"
end tell
EOF
