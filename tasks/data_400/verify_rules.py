import os
import json

def verify():
    target_file = "hike_project/urgent_patrols.json"
    result = {
        "success": False,
        "file_exists": False,
        "valid_json": False,
        "correct_trails": False,
        "error": None
    }

    if not os.path.exists(target_file):
        result["error"] = "urgent_patrols.json not found."
        print(json.dumps(result))
        return

    result["file_exists"] = True

    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        result["valid_json"] = True
    except Exception as e:
        result["error"] = f"Invalid JSON format: {str(e)}"
        print(json.dumps(result))
        return

    # Expected logic: 
    # Multiplier = 1.8
    # Pine Ridge: 15 * 1.8 = 27 (<=50)
    # Bear Creek: 22 * 1.8 = 39.6 (<=50)
    # Devil's Backbone: 35 * 1.8 = 63 (>50)
    # Sunny Meadow: 5 * 1.8 = 9 (<=50)
    # Deadman's Pass: 40 * 1.8 = 72 (>50)
    expected_trails = {"Devil's Backbone", "Deadman's Pass"}

    if isinstance(data, list):
        actual_trails = set(data)
        if actual_trails == expected_trails:
            result["correct_trails"] = True
            result["success"] = True
        else:
            result["error"] = f"Expected trails {expected_trails}, but got {actual_trails}"
    else:
        result["error"] = "JSON content must be a flat array of strings."

    print(json.dumps(result))

if __name__ == "__main__":
    verify()
