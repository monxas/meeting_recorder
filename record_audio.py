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
CHANNELS = 2  # Stereo recording
RATE = 48000   # Sample rate matching the Aggregate Device
OUTPUT_DIR = "recordings"
COMBINED_INPUT_INDEX = 4  # Device ID for "Dispositivo agregado"

def record_audio():
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    OUTPUT_FILE = os.path.join(OUTPUT_DIR, f"meeting_audio_{timestamp}.wav")

    print("Recording... Press Ctrl+C to stop.")

    # Initialize an empty list to store audio frames
    frames = []

    try:
        # Define a callback function to capture audio data
        def callback(indata, frames_count, time_info, status):
            if status:
                print(f"Warning: {status}")
            # Append a copy of the incoming data to the frames list
            frames.append(indata.copy())

        # Open an InputStream
        with sd.InputStream(samplerate=RATE,
                            device=COMBINED_INPUT_INDEX,
                            channels=CHANNELS,
                            dtype='int16',
                            callback=callback):
            while True:
                # Keep the stream active until interrupted
                sd.sleep(1000)
    except KeyboardInterrupt:
        print("\nRecording stopped by user.")
    except Exception as e:
        print(f"An error occurred during recording: {e}")
        return

    if not frames:
        print("No audio data recorded.")
        return

    # Concatenate all recorded frames
    recording = np.concatenate(frames, axis=0)

    # Save the recording to a WAV file
    try:
        with wave.open(OUTPUT_FILE, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 2 bytes per sample for int16
            wf.setframerate(RATE)
            wf.writeframes(recording.tobytes())
        print(f"Audio recorded and saved to {OUTPUT_FILE}")
    except Exception as e:
        print(f"Failed to save audio file: {e}")

if __name__ == "__main__":
    record_audio()
