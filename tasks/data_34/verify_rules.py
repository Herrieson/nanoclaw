import os
import json
import re
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def verify():
    workspace_dir = "."
    target_file = os.path.join(workspace_dir, "itinerary.md")
    
    state = {
        "file_exists": False,
        "correct_sequence": False,
        "correct_total_distance": False,
        "filtered_correctly": False,
        "format_ok": False,
        "extracted_sequence": [],
        "extracted_total": 0.0
    }

    if not os.path.exists(target_file):
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True

    with open(target_file, "r") as f:
        content = f.read()

    # Extract sequence of IDs
    id_matches = re.findall(r"Step \d+: ID: (\d+)", content)
    state["extracted_sequence"] = [int(i) for i in id_matches]

    # Verify filtering and routing sequence
    # Expected valid IDs: 1, 3, 6, 5
    expected_sequence = [1, 3, 6, 5]
    if state["extracted_sequence"] == expected_sequence:
        state["correct_sequence"] = True
        state["filtered_correctly"] = True
    elif set(state["extracted_sequence"]) == set(expected_sequence):
        state["filtered_correctly"] = True

    # Extract total distance
    total_match = re.search(r"Total Distance:\s*([\d\.]+)\s*km", content)
    if total_match:
        state["format_ok"] = True
        total = float(total_match.group(1))
        state["extracted_total"] = total
        # Expected total should be approx 11.02 or 11.03 depending on rounding at each step
        if 11.00 <= total <= 11.05:
            state["correct_total_distance"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
