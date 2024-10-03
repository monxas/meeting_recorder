# backend/record_audio.py

import sounddevice as sd
import numpy as np
import wave
import os
from datetime import datetime

# Configuration
RATE = 48000   # Sample rate
OUTPUT_DIR = "../recordings"  # Adjusted path for backend integration

class Recorder:
    def __init__(self, device_index):
        self.recording = False
        self.frames = []
        self.stream = None
        self.device_index = device_index
        self.channels = None
        self.samplerate = None
        self._initialize_device()

    def _initialize_device(self):
        try:
            device_info = sd.query_devices(self.device_index, 'input')
            self.channels = device_info['max_input_channels']
            self.samplerate = int(device_info['default_samplerate'])
            print(f"Initialized Recorder with device_id: {self.device_index}, channels: {self.channels}, samplerate: {self.samplerate}")
        except Exception as e:
            print(f"Error initializing device {self.device_index}: {e}")
            raise ValueError(f"Invalid device index: {self.device_index}")

    def start(self):
        if self.recording:
            print("Recording is already in progress.")
            return
        self.recording = True
        if not os.path.exists(OUTPUT_DIR):
            os.makedirs(OUTPUT_DIR)
        
        print(f"Attempting to start recording with device_id: {self.device_index}, channels: {self.channels}")
        
        try:
            self.stream = sd.InputStream(
                samplerate=self.samplerate,
                device=self.device_index,
                channels=self.channels,
                dtype='int16',
                callback=self.callback
            )
            self.stream.start()
            print("Recording started...")
        except Exception as e:
            print(f"Failed to start recording: {e}")
            self.recording = False
            raise e

    def callback(self, indata, frames_count, time_info, status):
        if status:
            print(f"Recording Warning: {status}")
        self.frames.append(indata.copy())

    def stop(self):
        if not self.recording:
            print("No recording is in progress.")
            return None
        self.recording = False
        self.stream.stop()
        self.stream.close()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(OUTPUT_DIR, f"meeting_audio_{timestamp}.wav")
        try:
            recording_data = np.concatenate(self.frames, axis=0)
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 2 bytes per sample for int16
                wf.setframerate(self.samplerate)
                wf.writeframes(recording_data.tobytes())
            print(f"Recording saved to {output_file}")
            self.frames = []
            return output_file
        except Exception as e:
            print(f"Failed to save recording: {e}")
            return None
