import os
import csv
import json

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "final_pitch_list.csv")
    
    result = {
        "csv_exists": False,
        "correct_columns": False,
        "matched_tracks_count": 0,
        "correct_isrcs": False,
        "expected_matches_found": []
    }
    
    expected_matches = {
        "Neon Monks": ("Silent Choirs", "AU-NM1-23-0001"),
        "The Burnt Toast": ("Morning Routine", "AU-BT3-23-0003"),
        "Crimson Rebels": ("System Shock", "AU-CR5-23-0005")
    }

    if not os.path.exists(csv_path):
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    result["csv_exists"] = True
    
    found_matches = {}
    
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, [])
            if len(header) == 3 and [h.strip().lower() for h in header] == ["artist", "track", "isrc"]:
                result["correct_columns"] = True
            
            for row in reader:
                if len(row) >= 3:
                    artist = row[0].strip()
                    track = row[1].strip()
                    isrc = row[2].strip()
                    found_matches[artist] = (track, isrc)
                    
        result["matched_tracks_count"] = len(found_matches)
        
        correct_count = 0
        for artist, (track, isrc) in expected_matches.items():
            if artist in found_matches:
                f_track, f_isrc = found_matches[artist]
                if f_track == track and f_isrc == isrc:
                    correct_count += 1
                    result["expected_matches_found"].append(artist)
                    
        if correct_count == len(expected_matches) and len(found_matches) == len(expected_matches):
            result["correct_isrcs"] = True

    except Exception as e:
        result["error"] = str(e)

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
