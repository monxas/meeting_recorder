# record_audio.py

import sounddevice as sd
import numpy as np
import wave
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables (if needed)
load_dotenv()

# Configuration
CHANNELS = 2  # Changed from 3 to 2 for stereo recording
RATE = 48000   # Set to match the Aggregate Device's sample rate
OUTPUT_DIR = "recordings"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"meeting_audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav")

# Device Index
COMBINED_INPUT_INDEX = 4  # Using device ID 4 as identified earlier

def record_audio():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    print("Recording... Press Ctrl+C to stop.")
    try:
        # Start recording from the Aggregate Device with 2 channels
        recording = sd.rec(int(RATE * 3600),  # Record for up to 1 hour
                          samplerate=RATE,
                          channels=CHANNELS,
                          dtype='int16',
                          device=COMBINED_INPUT_INDEX)
        sd.wait()  # Wait until recording is finished or interrupted
    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
    except Exception as e:
        print(f"An error occurred during recording: {e}")
        return
    
    # Save as WAV file
    with wave.open(OUTPUT_FILE, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(2)  # 2 bytes per sample for int16
        wf.setframerate(RATE)
        wf.writeframes(recording.tobytes())
    
    print(f"Audio recorded and saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    record_audio()
