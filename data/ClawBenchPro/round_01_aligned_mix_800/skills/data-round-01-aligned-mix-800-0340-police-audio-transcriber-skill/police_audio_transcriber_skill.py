import sys
import json
import os

def transcribe(file_path):
    if not os.path.exists(file_path):
        return "Error: File not found."
    
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Simulated extraction from metadata
        transcript = data.get("metadata", "No audio signal detected.")
        case_id = file_path.split("_")[-1].split(".")[0]
        return f"TRANSCRIPT CASE {case_id}: {transcript}"
    except Exception as e:
        return f"Error processing audio stream: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python police_audio_transcriber_skill.py <file_path>")
    else:
        print(transcribe(sys.argv[1]))
