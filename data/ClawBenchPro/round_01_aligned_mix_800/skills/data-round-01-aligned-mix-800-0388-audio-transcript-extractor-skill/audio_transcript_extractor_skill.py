import sys
import json

def extract_audio(file_path):
    # Mock behavior for the specific task file
    if "session_voice_backup.m4a" in file_path:
        return json.dumps({
            "session_id": 106,
            "counselor": "Robert Brown",
            "duration_min": 40,
            "date": "2023-10-06",
            "note": "Final session for the week."
        })
    return json.dumps({"error": "File not found or format not supported."})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(extract_audio(sys.argv[1]))
