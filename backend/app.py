# backend/app.py

from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
from record_audio import Recorder
from pathlib import Path

app = FastAPI()

# Configuration
RECORDINGS_DIR = Path(__file__).resolve().parent.parent / "recordings"

# Initialize Recorder as None initially
recorder = None

# Define Pydantic Models
class RecordingStatus(BaseModel):
    status: str

class AudioDevice(BaseModel):
    id: int
    name: str
    channels: int
    sample_rate: float

class DeviceSelection(BaseModel):
    device_id: int

# API Endpoints

@app.post("/api/start-recording", response_model=RecordingStatus)
def start_recording(device: Optional[DeviceSelection] = Body(None)):
    global recorder
    try:
        if device:
            print(f"Setting recorder device_index to: {device.device_id}")
            # Initialize Recorder with the selected device_id
            recorder = Recorder(device_index=device.device_id)
        else:
            raise HTTPException(status_code=400, detail="No device_id provided.")
        recorder.start()
        return RecordingStatus(status="Recording started")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stop-recording", response_model=RecordingStatus)
def stop_recording():
    global recorder
    try:
        if recorder and recorder.recording:
            output_file = recorder.stop()
            if output_file:
                return RecordingStatus(status=f"Recording stopped and saved to {output_file}")
            else:
                return RecordingStatus(status="Failed to save recording.")
        else:
            return RecordingStatus(status="No recording was in progress")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status", response_model=RecordingStatus)
def get_status():
    try:
        status = "Recording" if recorder and recorder.recording else "Idle"
        return RecordingStatus(status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recordings", response_model=List[str])
def list_recordings():
    try:
        if not RECORDINGS_DIR.exists():
            RECORDINGS_DIR.mkdir(parents=True)
        recordings = os.listdir(RECORDINGS_DIR)
        # Optionally, filter only .wav files
        recordings = [file for file in recordings if file.endswith(".wav")]
        return recordings
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio-devices", response_model=List[AudioDevice])
def get_audio_devices():
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        input_devices = []
        for idx, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                input_devices.append(AudioDevice(
                    id=idx,
                    name=device['name'],
                    channels=device['max_input_channels'],
                    sample_rate=device['default_samplerate']
                ))
        return input_devices
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount the recordings directory to serve static audio files
app.mount("/recordings", StaticFiles(directory=RECORDINGS_DIR), name="recordings")

# Mount the frontend directory to serve static files
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
