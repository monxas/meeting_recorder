# backend/app.py

from fastapi import FastAPI, HTTPException, Body, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
from record_audio import Recorder
from transcribe_audio import process_latest_audio
from summarize_transcript import process_latest_transcript
from pathlib import Path

app = FastAPI()

# Configuration
RECORDINGS_DIR = Path(__file__).resolve().parent.parent / "recordings"
TRANSCRIPT_DIR = Path(__file__).resolve().parent.parent / "transcripts"
NOTES_DIR = Path(__file__).resolve().parent.parent / "notes"

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

class RecordingInfo(BaseModel):
    audio_file: str
    transcript_file: Optional[str] = None
    notes_file: Optional[str] = None

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

@app.post("/api/stop-recording", response_model=RecordingInfo)
def stop_recording(background_tasks: BackgroundTasks):
    global recorder
    try:
        if recorder and recorder.recording:
            output_file = recorder.stop()
            if output_file:
                # Process transcription and summarization in the background
                background_tasks.add_task(process_recording, output_file)
                return RecordingInfo(audio_file=output_file)
            else:
                raise HTTPException(status_code=500, detail="Failed to save recording.")
        else:
            raise HTTPException(status_code=400, detail="No recording was in progress.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status", response_model=RecordingStatus)
def get_status():
    try:
        status = "Recording" if recorder and recorder.recording else "Idle"
        return RecordingStatus(status=status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/recordings", response_model=List[RecordingInfo])
def list_recordings():
    try:
        if not RECORDINGS_DIR.exists():
            RECORDINGS_DIR.mkdir(parents=True)
        recordings = sorted([f for f in RECORDINGS_DIR.iterdir() if f.suffix == '.wav'], key=lambda x: x.stat().st_mtime, reverse=True)
        recording_infos = []
        for recording in recordings:
            transcript_file = TRANSCRIPT_DIR / f"{recording.stem}_transcript.txt"
            notes_file = NOTES_DIR / f"{recording.stem}_notes.txt"
            recording_infos.append(RecordingInfo(
                audio_file=recording.name,
                transcript_file=transcript_file.name if transcript_file.exists() else None,
                notes_file=notes_file.name if notes_file.exists() else None
            ))
        return recording_infos
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

# Mount the transcripts directory to serve static transcript files
app.mount("/transcripts", StaticFiles(directory=TRANSCRIPT_DIR), name="transcripts")

# Mount the notes directory to serve static notes/summaries files
app.mount("/notes", StaticFiles(directory=NOTES_DIR), name="notes")

# Mount the frontend directory to serve static files
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")

# Background task to process transcription and summarization
def process_recording(audio_filename: str):
    print(f"Processing transcription and summarization for {audio_filename}...")
    audio_file_path = RECORDINGS_DIR / audio_filename
    # Transcription
    audio_name, transcript_name = process_latest_audio()
    if transcript_name:
        # Summarization
        transcript_file_path = TRANSCRIPT_DIR / transcript_name
        transcript = ""
        with transcript_file_path.open("r") as f:
            transcript = f.read()
        notes = process_latest_transcript()
        if notes:
            print(f"Processing completed for {audio_filename}.")
        else:
            print(f"Summarization failed for {audio_filename}.")
    else:
        print(f"Transcription failed for {audio_filename}.")
