import sys
import json

def get_metadata(file_path):
    # Simulated metadata logic
    filename = file_path.split("/")[-1]
    registry = {
        "Vocals_Echo_Final.wav": {"duration_seconds": 185.2, "sample_rate": 44100},
        "Drums_Echo_Raw.wav": {"duration_seconds": 185.2, "sample_rate": 44100},
        "Guitar_Midnight_Test.wav": {"duration_seconds": 15.0, "sample_rate": 44100},
        "Bass_Neon_Main.wav": {"duration_seconds": 210.5, "sample_rate": 44100},
        "Synth_Neon_Arp.wav": {"duration_seconds": 210.5, "sample_rate": 44100},
        "Piano_Lost_Buzz.wav": {"duration_seconds": 45.0, "sample_rate": 44100},
        "Silence_Gap.wav": {"duration_seconds": 0.0, "sample_rate": 0} # Corrupted/Empty
    }
    return registry.get(filename, {"error": "Unknown file format or corrupted metadata."})

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(get_metadata(sys.argv[1])))
