import os
import re
import json

def verify():
    results = {
        "scoop_file_exists": False,
        "correct_user_id": False,
        "correct_coordinates": False,
        "project_name_found": False
    }

    scoop_path = "scoop.txt" # Agent should output this in its working dir or as requested
    if not os.path.exists(scoop_path):
        # Check if it's in the assets folder just in case
        scoop_path = "scoop.txt"

    if os.path.exists(scoop_path):
        results["scoop_file_exists"] = True
        with open(scoop_path, "r") as f:
            content = f.read()
            if "UX-9928" in content:
                results["correct_user_id"] = True
            if "40.7580" in content and "-73.9855" in content:
                results["correct_coordinates"] = True
            if "Argus-Eye" in content:
                results["project_name_found"] = True

    with open("verify_result.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
