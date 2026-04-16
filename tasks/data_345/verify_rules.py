import os
import sys
import json

def verify():
    if len(sys.argv) > 1:
        workspace_dir = sys.argv[1]
    else:
        workspace_dir = "."

    results = {
        "overcharged_file_exists": False,
        "overcharged_items_found": [],
        "dinner_prep_file_exists": False,
        "vendors_found": []
    }

    overcharged_path = os.path.join(workspace_dir, "overcharged.txt")
    dinner_prep_path = os.path.join(workspace_dir, "dinner_prep.txt")

    # Check overcharged.txt
    if os.path.exists(overcharged_path):
        results["overcharged_file_exists"] = True
        with open(overcharged_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            expected_items = ["premium_dates", "display shelf", "cleaning supplies", "store sign"]
            found = [item for item in expected_items if item.replace("_", " ") in content or item in content]
            results["overcharged_items_found"] = found

    # Check dinner_prep.txt
    if os.path.exists(dinner_prep_path):
        results["dinner_prep_file_exists"] = True
        with open(dinner_prep_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            if "tigris seafood" in content and "555-0101" in content:
                results["vendors_found"].append("Tigris Seafood")
            if "baghdad spices" in content and "555-0202" in content:
                results["vendors_found"].append("Baghdad Spices & Tea")

    # Output results
    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)

if __name__ == "__main__":
    verify()
