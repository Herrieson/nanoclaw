import os
import json

def verify():
    target_file = "festival_schedule.json"
    result = {
        "file_exists": False,
        "is_valid_json": False,
        "correct_artists_selected": False,
        "emails_fixed": False,
        "venues_matched": False,
        "score": 0
    }

    if not os.path.exists(target_file):
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    result["file_exists"] = True

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        result["is_valid_json"] = True
    except Exception:
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    if not isinstance(data, list):
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    expected_artists = {"Carlos", "Elena", "Mateo"}
    found_artists = {item.get("name") for item in data if isinstance(item, dict)}
    
    if expected_artists.issubset(found_artists) and len(found_artists) == 3:
        result["correct_artists_selected"] = True
        result["score"] += 40

    correct_emails = 0
    correct_venues = 0

    for item in data:
        name = item.get("name")
        email = item.get("email", "")
        venue = item.get("venue", "")

        if name == "Carlos":
            if "carlos_rock@gmail.com" in email: correct_emails += 1
            if venue == "The Basement": correct_venues += 1
        elif name == "Elena":
            if "elena_reggaeton@outlook.com" in email: correct_emails += 1
            if venue == "Rooftop Lounge": correct_venues += 1
        elif name == "Mateo":
            if "mateo_indie@protonmail.com" in email: correct_emails += 1
            if venue == "Warehouse 9": correct_venues += 1

    if correct_emails == 3:
        result["emails_fixed"] = True
        result["score"] += 30

    if correct_venues == 3:
        result["venues_matched"] = True
        result["score"] += 30

    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
