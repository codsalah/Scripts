
#!/bin/bash
# kittenreader — shell launcher for kittenreader.py
# Activates the kittentts venv and runs the Python CLI

VENV="$HOME/kittentts-env"
SCRIPT="$(dirname "$(readlink -f "$0")")/kitten_tts.py"

if [ ! -f "$VENV/bin/activate" ]; then
    echo "Error: venv not found at $VENV"
    echo "Create it with: python3 -m venv $VENV"
    exit 1
fi

if [ ! -f "$SCRIPT" ]; then
    echo "Error: kitten_tts.py not found at $SCRIPT"
    exit 1
fi

source "$VENV/bin/activate"
python3 "$SCRIPT" "$@"