import openai
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TRANSCRIPT_DIR = "transcripts"
NOTES_DIR = "notes"

# Ensure the OpenAI API key is loaded
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set in the .env file.")

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

def main():
    if not os.path.exists(NOTES_DIR):
        os.makedirs(NOTES_DIR)

    # Find the latest transcript file
    transcript_files = sorted(
        [f for f in os.listdir(TRANSCRIPT_DIR) if f.endswith('.txt')],
        key=lambda x: os.path.getmtime(os.path.join(TRANSCRIPT_DIR, x)),
        reverse=True
    )
    if not transcript_files:
        print("No transcript files found in transcripts directory.")
        return

    latest_transcript = os.path.join(TRANSCRIPT_DIR, transcript_files[0])
    with open(latest_transcript, "r") as f:
        transcript = f.read()

    notes = generate_notes(transcript)
    if notes:
        notes_file = os.path.join(
            NOTES_DIR,
            f"{os.path.splitext(transcript_files[0])[0]}_notes.txt"
        )
        save_notes(notes, notes_file)
    else:
        print("No notes were generated.")

if __name__ == "__main__":
    main()
