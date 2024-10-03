# app.py

import sounddevice as sd
import numpy as np
import wave
import os
from datetime import datetime
from dotenv import load_dotenv
import tkinter as tk
from tkinter import messagebox
import threading

# Load environment variables
load_dotenv()

# Configuration
CHANNELS = 2  # Stereo recording
RATE = 48000   # Sample rate matching the Aggregate Device
OUTPUT_DIR = "recordings"
COMBINED_INPUT_INDEX = 4  # Device ID for "Dispositivo agregado"

# Initialize global variables
recording = False
frames = []

def get_device_info(device_name):
    devices = sd.query_devices()
    for idx, device in enumerate(devices):
        if device['name'] == device_name:
            return idx, device
    raise ValueError(f"Device '{device_name}' not found.")

def start_recording():
    global recording, frames
    try:
        device_index, device_info = get_device_info("Dispositivo agregado")
    except ValueError as e:
        messagebox.showerror("Device Error", str(e))
        return

    # Reset frames
    frames = []
    recording = True

    def callback(indata, frames_count, time_info, status):
        if status:
            print(f"Warning: {status}")
        frames.append(indata.copy())

    try:
        stream = sd.InputStream(samplerate=RATE,
                                device=COMBINED_INPUT_INDEX,
                                channels=CHANNELS,
                                dtype='int16',
                                callback=callback)
        stream.start()
        print("Recording started...")
        status_label.config(text="Status: Recording...")
        
        # Keep the stream open until recording is stopped
        while recording:
            sd.sleep(100)
    except Exception as e:
        messagebox.showerror("Recording Error", f"An error occurred: {e}")
        recording = False
        status_label.config(text="Status: Error")
        return

def stop_recording():
    global recording
    if not recording:
        return
    recording = False
    print("Recording stopped by user.")
    status_label.config(text="Status: Stopped Recording...")
    
    # Save the recording
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = os.path.join(OUTPUT_DIR, f"meeting_audio_{timestamp}.wav")
    
    if frames:
        recording_data = np.concatenate(frames, axis=0)
        try:
            with wave.open(output_file, 'wb') as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)  # 2 bytes per sample for int16
                wf.setframerate(RATE)
                wf.writeframes(recording_data.tobytes())
            messagebox.showinfo("Recording Saved", f"Audio recorded and saved to:\n{output_file}")
            status_label.config(text="Status: Recording Saved")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save recording: {e}")
            status_label.config(text="Status: Save Failed")
    else:
        messagebox.showwarning("No Data", "No audio data was recorded.")
        status_label.config(text="Status: No Data Recorded")

def threaded_start_recording():
    threading.Thread(target=start_recording, daemon=True).start()

# Set up the GUI
root = tk.Tk()
root.title("Meeting Recorder Tool")
root.geometry("300x150")

start_button = tk.Button(root, text="Start Recording", command=threaded_start_recording, width=20, height=2)
start_button.pack(pady=10)

stop_button = tk.Button(root, text="Stop Recording", command=stop_recording, width=20, height=2)
stop_button.pack(pady=10)

status_label = tk.Label(root, text="Status: Idle")
status_label.pack(pady=10)

root.mainloop()
