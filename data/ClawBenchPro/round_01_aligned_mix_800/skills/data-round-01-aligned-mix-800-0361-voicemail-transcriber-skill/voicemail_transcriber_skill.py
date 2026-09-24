import argparse
import os

def transcribe(file_path):
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found."
    
    if not file_path.endswith('.mp3'):
        return "Error: Unsupported audio format. Only .mp3 is supported."

    # Return the exact pre-recorded mock transcription for this task
    transcription = """Hey! Here are the RSVPs from the voicemails:
1. Rosa (she said she completely avoids all animal products)
2. Juan (I'll eat anything!)
3. Miguel - he will swell up and die if he is near peanuts!!
4. Elena -> no animal products and same peanut issue as Miguel.
5. Luis (no restrictions)
6. Blanca ... milk makes her sick.
7. Chloe: no milk, no meat, no eggs.
8. Mateo (none)

Good luck organizing everything!"""

    return f"--- Transcription of {file_path} ---\n{transcription}\n--- End of Transcription ---"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcribe voicemail MP3 files.")
    parser.add_argument("--file", required=True, help="Path to the .mp3 file")
    args = parser.parse_args()
    
    print(transcribe(args.file))
