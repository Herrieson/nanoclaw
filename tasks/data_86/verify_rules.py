import os
import json

def verify():
    base_dir = "ad_campaign_music"
    target_file = os.path.join(base_dir, "affordable_tracks.txt")
    
    state = {
        "file_exists": False,
        "correct_tracks_found": [],
        "incorrect_tracks_found": [],
        "missing_correct_tracks": ["Fuzzy Echoes", "Cloud Surfing"]
    }

    if os.path.exists(target_file):
        state["file_exists"] = True
        with open(target_file, "r") as f:
            content = f.read().lower()
            
        expected_tracks = ["fuzzy echoes", "cloud surfing"]
        all_tracks = ["neon city", "corporate synergy", "fuzzy echoes", "angry screams", "cloud surfing", "static noise", "random song"]
        
        for track in all_tracks:
            if track in content:
                if track in expected_tracks:
                    state["correct_tracks_found"].append(track)
                    if track in [t.lower() for t in state["missing_correct_tracks"]]:
                        # Remove case-insensitively
                        state["missing_correct_tracks"] = [t for t in state["missing_correct_tracks"] if t.lower() != track]
                else:
                    state["incorrect_tracks_found"].append(track)

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
