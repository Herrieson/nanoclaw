import os
import csv
import json

def verify():
    base_dir = "."
    playlist_path = os.path.join(base_dir, "hype_playlist.csv")
    time_path = os.path.join(base_dir, "total_time.txt")
    
    state = {
        "playlist_exists": False,
        "playlist_header_correct": False,
        "playlist_order_correct": False,
        "playlist_tracks_correct": False,
        "time_file_exists": False,
        "time_correct": False,
        "extracted_playlist": [],
        "extracted_time_value": None
    }
    
    # Expected details
    expected_order = [
        {"Title": "Savage", "Artist": "Megan Thee Stallion", "Duration": "2:35", "BPM": 169},
        {"Title": "Just Wanna Rock", "Artist": "Lil Uzi Vert", "Duration": "2:03", "BPM": 150},
        {"Title": "HISS", "Artist": "Megan Thee Stallion", "Duration": "3:12", "BPM": 140},
        {"Title": "DNA.", "Artist": "Kendrick Lamar", "Duration": "3:05", "BPM": 135},
        {"Title": "Love Sosa", "Artist": "Chief Keef", "Duration": "4:06", "BPM": 132},
        {"Title": "Not Like Us", "Artist": "Kendrick Lamar", "Duration": "4:34", "BPM": 130},
        {"Title": "TGIF", "Artist": "GloRilla", "Duration": "2:50", "BPM": 125}
    ]
    
    expected_titles = [x["Title"] for x in expected_order]
    
    # Total seconds = 155 + 123 + 192 + 185 + 246 + 274 + 170 = 1345
    # Total minutes = 1345 / 60 = 22.41666...
    expected_time_min = 1345 / 60.0
    
    if os.path.exists(playlist_path):
        state["playlist_exists"] = True
        try:
            with open(playlist_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                header = next(reader)
                if [h.strip().lower() for h in header] == ["title", "artist", "duration"]:
                    state["playlist_header_correct"] = True
                
                rows = list(reader)
                state["extracted_playlist"] = rows
                
                if len(rows) == len(expected_order):
                    actual_titles = [r[0].strip() for r in rows]
                    if sorted(actual_titles) == sorted(expected_titles):
                        state["playlist_tracks_correct"] = True
                    if actual_titles == expected_titles:
                        state["playlist_order_correct"] = True
        except Exception:
            pass

    if os.path.exists(time_path):
        state["time_file_exists"] = True
        try:
            with open(time_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
                val = float(content)
                state["extracted_time_value"] = val
                if abs(val - expected_time_min) < 0.05:  # Tolerance for rounding (e.g. 22.41, 22.42)
                    state["time_correct"] = True
        except Exception:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
