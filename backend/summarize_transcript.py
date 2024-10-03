# backend/summarize_transcript.py

import openai
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Configuration
TRANSCRIPT_DIR = Path(__file__).resolve().parent.parent / "transcripts"
NOTES_DIR = Path(__file__).resolve().parent.parent / "notes"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure the OpenAI API key is loaded
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

# Set OpenAI API key
openai.api_key = OPENAI_API_KEY

def generate_notes(transcript):
    prompt = (
        "You are a meeting assistant. Please summarize the following meeting transcript, highlight key points discussed, "
        "list any decisions made, and clearly outline the actions to be taken. Also specify who is responsible for each action "
        "and any deadlines. If any follow-up meetings are required, include that as well.\n\n"
        f"{transcript}"
    )
    try:
        # Chat completion request
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # Ensure you have access to GPT-4
            messages=[
                {"role": "system", "content": "You are a helpful meeting assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.5,
        )
        return response.choices[0].message.content.strip()  # Corrected way to access content
    except Exception as e:
        print(f"Error generating notes: {e}")
        return ""

def save_notes(notes, output_path):
    with open(output_path, "w") as f:
        f.write(notes)
    print(f"Notes saved to {output_path}")

def process_latest_transcript():
    if not NOTES_DIR.exists():
        NOTES_DIR.mkdir(parents=True)

    # Find the latest transcript file
    transcript_files = sorted(
        [f for f in TRANSCRIPT_DIR.iterdir() if f.suffix == '.txt'],
        key=lambda x: x.stat().st_mtime,
        reverse=True
    )
    if not transcript_files:
        print("No transcript files found in transcripts directory.")
        return None, None

    latest_transcript = transcript_files[0]
    with latest_transcript.open("r") as f:
        transcript = f.read()

    notes = generate_notes(transcript)
    if notes:
        notes_file = NOTES_DIR / f"{latest_transcript.stem}_notes.txt"
        save_notes(notes, notes_file)
        return latest_transcript.name, notes_file.name
    else:
        print("No notes were generated.")
        return None, None
