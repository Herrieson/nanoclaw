import sys
import os

def transcribe(file_path):
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' does not exist."
    
    filename = os.path.basename(file_path)
    
    # Internal mock mapping
    transcripts = {
        "log_monday.mp3": "[Audio Start] Morning check. Weather is crisp. Sheep-092 seems fine and is eating well. Cow-104: fever, isolated in pen 3. Need to fix the fence near the creek. [Audio End]",
        "log_tuesday.mp3": "[Audio Start] Pig-33 is growing fast. Checked the north pasture, grass is getting low. Horse-07 limping after the morning trail ride, calling the vet. [Audio End]",
        "log_wednesday.mp3": "[Audio Start] Normal day. Cow-105 healthy. Found a stray dog near the barn, scared the chickens. Goat-12 is stubborn as usual. [Audio End]",
        "log_thursday.mp3": "[Audio Start] Heavy rain today. Barn roof is leaking slightly. Sheep-099 looking a bit tired but no fever. All animals accounted for. [Audio End]",
    }

    if filename in transcripts:
        return f"--- Transcription for {filename} ---\n" + transcripts[filename]
    else:
        return f"Error: Unable to process audio format or file empty for '{filename}'."

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python farm_voice_transcriber.py <path_to_audio_file>")
    else:
        print(transcribe(sys.argv[1]))
