# backend/transcribe_audio.py

import whisper
import os
from pathlib import Path

# Configuration
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "recordings"
TRANSCRIPT_DIR = Path(__file__).resolve().parent.parent / "transcripts"

def transcribe_audio(file_path):
    model = whisper.load_model("base")  # You can choose other models like "small", "medium", "large"
    print(f"Transcribing {file_path}...")
    result = model.transcribe(str(file_path))
    transcript = result["text"]
    return transcript

def save_transcript(transcript, output_path):
    with open(output_path, "w") as f:
        f.write(transcript)
    print(f"Transcript saved to {output_path}")

def process_latest_audio():
    if not TRANSCRIPT_DIR.exists():
        TRANSCRIPT_DIR.mkdir(parents=True)
    
    # Find the latest audio file
    audio_files = sorted([f for f in OUTPUT_DIR.iterdir() if f.suffix == '.wav'], key=lambda x: x.stat().st_mtime, reverse=True)
    if not audio_files:
        print("No audio files found in recordings directory.")
        return None, None
    
    latest_audio = audio_files[0]
    transcript = transcribe_audio(latest_audio)
    transcript_file = TRANSCRIPT_DIR / f"{latest_audio.stem}_transcript.txt"
    save_transcript(transcript, transcript_file)
    return latest_audio.name, transcript_file.name
