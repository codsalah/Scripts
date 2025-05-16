#!/usr/bin/env python3
import json
import queue
import sys
import sounddevice as sd
import vosk
import os
import subprocess
from threading import Thread
import signal
import psutil

# Initialize audio parameters
SAMPLE_RATE = 16000
CHANNELS = 1
q = queue.Queue()

def cleanup_processes():
    """Clean up any existing speech recognition processes"""
    current_pid = os.getpid()
    # Find and kill other Listener.py processes
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.pid != current_pid and 'Listener.py' in ' '.join(proc.info['cmdline'] or []):
                proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Remove PID file if it exists
    pid_file = "/tmp/speech_to_text.pid"
    if os.path.exists(pid_file):
        os.remove(pid_file)

def signal_handler(sig, frame):
    print("\nExiting...")
    cleanup_processes()
    sys.exit(0)

def audio_callback(indata, frames, time, status):
    if status:
        print(status)
    q.put(bytes(indata))

def insert_text(text):
    """Insert text at current cursor position using xdotool"""
    try:
        subprocess.run(['xdotool', 'type', '--clearmodifiers', text], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error inserting text: {e}")

def main():
    # Clean up any existing processes first
    cleanup_processes()

    # Download the model if it doesn't exist
    model_path = os.path.expanduser("~/.cache/vosk/model")
    if not os.path.exists(model_path):
        print("Downloading the model...")
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        subprocess.run([
            "wget", "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip",
            "-O", "/tmp/model.zip"
        ], check=True)
        subprocess.run(["unzip", "/tmp/model.zip", "-d", os.path.dirname(model_path)], check=True)
        subprocess.run(["mv", os.path.dirname(model_path) + "/vosk-model-small-en-us-0.15", model_path], check=True)
        subprocess.run(["rm", "/tmp/model.zip"], check=True)

    # Load the model
    model = vosk.Model(model_path)
    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)

    print("Listening... (Press Win+Shift+L to toggle)")
    
    # Register signal handlers for proper cleanup
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    # Save our PID
    with open("/tmp/speech_to_text.pid", "w") as f:
        f.write(str(os.getpid()))

    try:
        with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, device=None,
                             dtype="int16", channels=CHANNELS, callback=audio_callback):
            while True:
                data = q.get()
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    if result["text"]:
                        print(f"Recognized: {result['text']}")
                        insert_text(result["text"] + " ")
    finally:
        # Clean up on exit
        cleanup_processes()

if __name__ == "__main__":
    main() 