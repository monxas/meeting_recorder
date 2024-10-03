# workflow.py

import subprocess
import time
import os
from datetime import datetime

# Paths to scripts
RECORD_SCRIPT = "record_audio.py"
TRANSCRIBE_SCRIPT = "transcribe_audio.py"  # or "transcribe_audio_api.py" if using API
GENERATE_NOTES_SCRIPT = "generate_notes.py"

def run_script(script_name):
    subprocess.run(["python", script_name])

def main():
    print("Starting the meeting recording workflow...")
    
    # Start recording in a separate process
    print("Starting audio recording. Press Ctrl+C to stop.")
    try:
        subprocess.Popen(["python", RECORD_SCRIPT])
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping recording...")
        # Assuming the recording script handles KeyboardInterrupt to stop recording
        # Wait a moment to ensure the recording script has saved the file
        time.sleep(2)
    
    # Transcribe audio
    print("Transcribing audio...")
    run_script(TRANSCRIBE_SCRIPT)
    
    # Generate notes
    print("Generating notes...")
    run_script(GENERATE_NOTES_SCRIPT)
    
    print("Workflow completed successfully.")

if __name__ == "__main__":
    main()
