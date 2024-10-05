from fastapi import FastAPI, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import os
from record_audio import Recorder
from pathlib import Path
import whisper
from openai import OpenAI

from dotenv import load_dotenv

app = FastAPI()

# Load environment variables
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Configuration
RECORDINGS_DIR = Path(__file__).resolve().parent.parent / "recordings"
TRANSCRIPT_DIR = Path(__file__).resolve().parent.parent / "transcripts"
NOTES_DIR = Path(__file__).resolve().parent.parent / "notes"

# Ensure directories exist
for directory in [RECORDINGS_DIR, TRANSCRIPT_DIR, NOTES_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

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

class RecordingEntry(BaseModel):
    audio_file: str
    transcript_file: Optional[str] = None
    notes_file: Optional[str] = None

class QuestionRequest(BaseModel):
    notes_file: str
    question: str

class QuestionResponse(BaseModel):
    answer: str

# Initialize OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the .env file.")

# Function to transcribe audio using Whisper
def transcribe_audio(file_path: Path) -> str:
    model = whisper.load_model("base")  # Puedes elegir otros modelos como "small", "medium", "large"
    print(f"Transcribing {file_path}...")
    result = model.transcribe(str(file_path))
    transcript = result["text"]
    return transcript

# Function to generate notes using OpenAI
def generate_notes(transcript: str) -> str:
    prompt = (
        "You are a meeting assistant. Please summarize the following meeting transcript, highlight key points discussed, "
        "list any decisions made, and clearly outline the actions to be taken. Also specify who is responsible for each action "
        "and any deadlines. If any follow-up meetings are required, include that as well.\n\n"
        f"{transcript}"
    )
    try:
        # Chat completion request
        response = client.chat.completions.create(model="gpt-4o-mini",  
        messages=[
            {"role": "system", "content": "You are a helpful meeting assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=500,
        temperature=0.5)
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating notes: {e}")
        return ""

# Function to answer questions based on transcript
def answer_question(transcript: str, question: str) -> str:
    prompt = (
        "You are an assistant that provides detailed answers based on the following meeting transcript.\n\n"
        f"Transcript:\n{transcript}\n\n"
        f"Question: {question}\n"
        "Answer:"
    )
    try:
        response = client.chat.completions.create(model="gpt-4o-mini",  
            messages=[
                {"role": "system", "content": "You are a knowledgeable assistant that answers questions based on meeting transcripts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error answering question: {e}")
        return "Lo siento, no pude procesar tu pregunta en este momento."

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
                # After saving the audio file, transcribe and generate notes
                audio_path = Path(output_file)
                transcript = transcribe_audio(audio_path)
                transcript_filename = f"{audio_path.stem}_transcript.txt"
                transcript_path = TRANSCRIPT_DIR / transcript_filename
                with open(transcript_path, "w") as f:
                    f.write(transcript)
                print(f"Transcript saved to {transcript_path}")

                # Generate notes/summaries
                notes = generate_notes(transcript)
                if notes:
                    notes_filename = f"{audio_path.stem}_notes.txt"
                    notes_path = NOTES_DIR / notes_filename
                    with open(notes_path, "w") as f:
                        f.write(notes)
                    print(f"Notes saved to {notes_path}")
                else:
                    notes_path = None

                return RecordingStatus(status="Recording stopped and processed")
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

@app.get("/api/recordings", response_model=List[RecordingEntry])
def list_recordings():
    try:
        recordings = sorted(RECORDINGS_DIR.glob("meeting_audio_*.wav"), reverse=True)
        recording_entries = []
        for audio_file in recordings:
            stem = audio_file.stem  # meeting_audio_YYYYMMDD_HHMMSS
            transcript_file = TRANSCRIPT_DIR / f"{stem}_transcript.txt"
            notes_file = NOTES_DIR / f"{stem}_notes.txt"

            entry = RecordingEntry(
                audio_file=audio_file.name,
                transcript_file=transcript_file.name if transcript_file.exists() else None,
                notes_file=notes_file.name if notes_file.exists() else None
            )
            recording_entries.append(entry)
        return recording_entries
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

@app.post("/api/ask-question", response_model=QuestionResponse)
def ask_question(request: QuestionRequest):
    try:
        notes_path = NOTES_DIR / request.notes_file
        if not notes_path.exists():
            raise HTTPException(status_code=404, detail="Notes file not found.")
        
        with open(notes_path, "r") as f:
            notes_content = f.read()
        
        answer = answer_question(notes_content, request.question)
        
        return QuestionResponse(answer=answer)
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount the recordings directory to serve static audio files
app.mount("/recordings", StaticFiles(directory=RECORDINGS_DIR), name="recordings")

# Mount the transcripts directory to serve transcript files
app.mount("/transcripts", StaticFiles(directory=TRANSCRIPT_DIR), name="transcripts")

# Mount the notes directory to serve summary files
app.mount("/notes", StaticFiles(directory=NOTES_DIR), name="notes")

# Mount the frontend directory to serve static files
frontend_path = Path(__file__).resolve().parent.parent / "frontend"
app.mount("/", StaticFiles(directory=frontend_path, html=True), name="frontend")
