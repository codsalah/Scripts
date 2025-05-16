#!/bin/bash

# Get the directory of this script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Function to kill existing process
kill_existing() {
    if [ -f "/tmp/speech_to_text.pid" ]; then
        pid=$(cat /tmp/speech_to_text.pid)
        if ps -p $pid > /dev/null; then
            kill $pid
            rm /tmp/speech_to_text.pid
            notify-send "Speech to Text" "Stopped listening" -i audio-input-microphone
            exit 0
        fi
    fi
}

# Check if already running
if [ -f "/tmp/speech_to_text.pid" ]; then
    kill_existing
else
    # Start new instance
    cd "$SCRIPT_DIR"
    source venv/bin/activate
    notify-send "Speech to Text" "Started listening..." -i audio-input-microphone
    ./Listener.py & echo $! > /tmp/speech_to_text.pid
fi 