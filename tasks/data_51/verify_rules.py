import os
import json
import re

def verify():
    result = {
        "output_file_exists": False,
        "contains_iceworm_dispatches": False,
        "excludes_irrelevant_dispatches": False,
        "is_chronological": False,
        "score": 0
    }

    target_file = "workspace/lecture_notes.txt"

    if not os.path.exists(target_file):
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    result["output_file_exists"] = True

    with open(target_file, "r") as f:
        content = f.read()

    # Dates that should be in the file (Iceworm related)
    required_dates = ["1960-05-22", "1961-02-09", "1962-10-18"]
    # Dates that should NOT be in the file
    excluded_dates = ["1960-03-12", "1959-11-14", "1958-08-30"]

    # Check for inclusions
    if all(date in content for date in required_dates):
        result["contains_iceworm_dispatches"] = True

    # Check for exclusions
    if all(date not in content for date in excluded_dates):
        result["excludes_irrelevant_dispatches"] = True

    # Check chronological order
    found_dates = []
    # Extract dates formatted like YYYY-MM-DD
    matches = re.finditer(r"\d{4}-\d{2}-\d{2}", content)
    for match in matches:
        found_dates.append(match.group())
    
    # Filter only the required dates found to ensure relative ordering is correct
    filtered_found_dates = [d for d in found_dates if d in required_dates]
    
    if filtered_found_dates == sorted(required_dates) and len(filtered_found_dates) == len(required_dates):
        result["is_chronological"] = True

    # Calculate Score
    score = 10
    if result["contains_iceworm_dispatches"]:
        score += 40
    if result["excludes_irrelevant_dispatches"]:
        score += 20
    if result["is_chronological"]:
        score += 30

    result["score"] = score

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
