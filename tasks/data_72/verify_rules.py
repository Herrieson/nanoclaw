import os
import json
import re

def verify():
    base_dir = "."
    restored_dir = os.path.join(base_dir, "restored_audio")
    playlist_path = os.path.join(base_dir, "playlist.html")
    
    expected_files = [
        "Arctic Monkeys - Do I Wanna Know.mp3",
        "My Chemical Romance - Welcome to the Black Parade.mp3",
        "Paramore - Misery Business.mp3",
        "Tame Impala - Let It Happen.mp3",
        "The Strokes - Reptilia.mp3",
        "The Velvet Underground - Sunday Morning.mp3"
    ]
    
    state = {
        "restored_dir_exists": False,
        "playlist_exists": False,
        "correct_files_count": 0,
        "total_expected_files": len(expected_files),
        "playlist_contains_all_tracks": False,
        "playlist_is_sorted": False,
        "unexpected_files_found": 0
    }
    
    if os.path.exists(restored_dir) and os.path.isdir(restored_dir):
        state["restored_dir_exists"] = True
        actual_files = os.listdir(restored_dir)
        
        correct_count = 0
        for ef in expected_files:
            if ef in actual_files:
                correct_count += 1
                
        state["correct_files_count"] = correct_count
        state["unexpected_files_found"] = len(actual_files) - correct_count

    if os.path.exists(playlist_path):
        state["playlist_exists"] = True
        with open(playlist_path, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Check if all expected formats are in the file
            all_present = True
            found_tracks = []
            
            for ef in expected_files:
                track_name = ef.replace(".mp3", "")
                if track_name not in content:
                    all_present = False
                else:
                    # Capture the position to check sorting
                    found_tracks.append((track_name, content.find(track_name)))
                    
            state["playlist_contains_all_tracks"] = all_present
            
            if all_present and len(found_tracks) == len(expected_files):
                # Check if sorted by position in HTML
                found_tracks.sort(key=lambda x: x[1]) # Sort by position in text
                extracted_names = [x[0] for x in found_tracks]
                
                # Check if the extracted names are in alphabetical order
                if extracted_names == sorted(expected_files, key=lambda x: x.replace(".mp3", "")):
                    state["playlist_is_sorted"] = True

    # Output the result
    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)
        
    print(json.dumps(state, indent=4))

if __name__ == "__main__":
    verify()
