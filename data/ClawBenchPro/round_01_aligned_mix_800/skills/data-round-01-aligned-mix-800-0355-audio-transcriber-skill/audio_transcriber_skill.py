import sys
import os

def transcribe(filepath):
    if not os.path.exists(filepath):
        return f"Error: The file {filepath} does not exist."
    
    if not filepath.endswith(".mp3"):
        return "Error: Unsupported format. Only .mp3 is supported by this basic transcriber."
    
    if "audio_log_shift_end.mp3" in filepath:
        # Mocking the transcription of the messy notes
        transcript = """
        [System: Audio transcription initiated. Confidence: 92%]
        
        "Uh, okay, let's see what we got in the lost and found today. Man, this place is a mess...
        >>> LOST & FOUND LOG - Neon Galaxy MD <<<
        1. Found: Blue Jacket | Name: Marcus Johnson | Location: Arcade
        2. Item: dirty sock - Name: NONE, Location: Bathroom
        3. Apple Watch (Owner: Sarah Connor) found at Laser Tag
        4. keys... Owner: N/A ... Lobby
        5. Found: Gold Ring | Owner: David Smith | Location: VR Room
        6. Item: water bottle | Name:  | Location: Entrance
        7. VR Headset piece [Name: Chloe Bennett] (Loc: VR Room)
        8. Unknown item: loose change. Name: null.
        
        Alright, that's everything. Back to the zero-G simulator..."
        
        [System: Audio transcription completed.]
        """
        return transcript.strip()
    
    return "Error: Could not decode audio stream for the given file."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python audio_transcriber_skill.py <path_to_audio_file>")
        sys.exit(1)
        
    print(transcribe(sys.argv[1]))
