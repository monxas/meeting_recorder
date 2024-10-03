# transcribe_audio.py

import whisper
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
OUTPUT_DIR = "recordings"
TRANSCRIPT_DIR = "transcripts"

def transcribe_audio(file_path):
    model = whisper.load_model("base")  # You can choose other models like "small", "medium", "large"
    print(f"Transcribing {file_path}...")
    result = model.transcribe(file_path)
    transcript = result["text"]
    return transcript

def save_transcript(transcript, output_path):
    with open(output_path, "w") as f:
        f.write(transcript)
    print(f"Transcript saved to {output_path}")

def main():
    if not os.path.exists(TRANSCRIPT_DIR):
        os.makedirs(TRANSCRIPT_DIR)
    
    # Find the latest audio file
    audio_files = sorted([f for f in os.listdir(OUTPUT_DIR) if f.endswith('.wav')], reverse=True)
    if not audio_files:
        print("No audio files found in recordings directory.")
        return
    
    latest_audio = os.path.join(OUTPUT_DIR, audio_files[0])
    transcript = transcribe_audio(latest_audio)
    transcript_file = os.path.join(TRANSCRIPT_DIR, f"{os.path.splitext(audio_files[0])[0]}_transcript.txt")
    save_transcript(transcript, transcript_file)

if __name__ == "__main__":
    main()
