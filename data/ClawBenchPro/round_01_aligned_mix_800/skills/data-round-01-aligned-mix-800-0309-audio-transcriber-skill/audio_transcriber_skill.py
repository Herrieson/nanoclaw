import sys

def transcribe(file_path):
    # Mocking transcription based on file content for the specific task
    if "manager_note.mp4" in file_path:
        return "Hey Danny, it's the manager. Bad news: I dropped the last bottle of Grenadine, it's everywhere. Also, don't use the Simple Syrup, it's got mold in it. We need to toss it. Everything else is fine."
    return "Error: File not found or unsupported format."

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(transcribe(sys.argv[1]))
