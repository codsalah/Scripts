# Linux Speech-to-Text at Cursor

A simple, offline speech recognition tool that types recognized text at your cursor position, similar to Windows' Win+H functionality.

## Prerequisites

1. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv portaudio19-dev xdotool wget unzip
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Make the script executable:
```bash
chmod +x Listener.py
```

2. Run the script:
```bash
./Listener.py
```

3. Set up a keyboard shortcut (recommended):
   - Open Settings → Keyboard → Keyboard Shortcuts
   - Click '+' to add a new shortcut
   - Name: "Speech to Text"
   - Command: `/full/path/to/Listener.py`
   - Choose your preferred keyboard shortcut (e.g., Ctrl+Alt+H)

## Features

- Offline speech recognition using Vosk
- Automatically downloads a small English language model (~50MB) on first run
- Types recognized text at current cursor position
- Works system-wide in any application
- Low latency and resource usage

## Notes

- The first run will download the speech recognition model (~50MB)
- Press Ctrl+C to stop the recognition
- The script uses the default microphone. To change it, modify the `device` parameter in the script
- Each recognition result is followed by a space automatically 