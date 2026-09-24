import os

def transcribe_memo(file_path: str) -> str:
    """
    Transcribes the proprietary .vmemo audio files into text.
    """
    if not os.path.exists(file_path):
        return f"Error: File not found at {file_path}"
    
    if not file_path.endswith('.vmemo'):
        return "Error: Invalid format. This tool only supports .vmemo files."
    
    # Mocking the transcription of the doctor's scribbles
    transcript = """
    [Auto-generated Transcript]
    *Heavy breathing* Okay, notes for Tuesday... Let's see. 
    Patient ID P-004... Name is Mary Jenkins. Her billing code is CODE-CHARITY. Duration was 2.0 hours.
    Then we had Patient ID P-005. Bob S. He's on code INS-PRI. I spent 1.5 hours with him. 
    *Sigh* I really need a break. End of memo.
    """
    return transcript
