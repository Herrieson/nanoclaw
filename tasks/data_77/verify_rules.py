import os
import json
import re

def verify():
    base_dir = "."
    output_file = os.path.join(base_dir, "endangered_birds.json")
    state = {
        "output_file_exists": False,
        "is_valid_json": False,
        "correct_schema": False,
        "has_correct_species": False,
        "filtered_correctly": False,
        "sorted_correctly": False,
        "score": 0,
        "error": ""
    }

    if not os.path.exists(output_file):
        state["error"] = "Output file endangered_birds.json does not exist."
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    state["output_file_exists"] = True

    try:
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        state["is_valid_json"] = True
    except Exception as e:
        state["error"] = f"Invalid JSON format: {str(e)}"
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    if not isinstance(data, list):
        state["error"] = "JSON root is not a list."
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    if len(data) == 0:
        state["error"] = "JSON list is empty."
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    # Check schema
    required_keys = {"date", "species", "latitude", "longitude"}
    if all(required_keys.issubset(item.keys()) for item in data):
        state["correct_schema"] = True

    # Validate content
    target_species = {"piping plover", "least tern"}
    invalid_locations = {"lakefront park", "downtown marina"}
    
    # We will read the original log to cross-reference if needed, 
    # but we can do a logical check on the JSON first.
    has_wrong_species = False
    
    dates = []
    
    for item in data:
        sp = str(item.get("species", "")).lower()
        if sp not in target_species:
            has_wrong_species = True
            
        dates.append(item.get("date", ""))

    if not has_wrong_species:
        state["has_correct_species"] = True

    # Check if filtered correctly by searching original log to see if any forbidden records snuck in
    # Actually, we can check if the dates/coordinates match known forbidden ones, or simply parse the log ourselves
    log_file = os.path.join(base_dir, "raw_observations.log")
    
    with open(log_file, "r", encoding="utf-8") as f:
        log_content = f.read()

    # Extract all valid expected dates to compare
    pattern = re.compile(r'\[(.*?)\].*?msg:.*?(Piping Plover|Least Tern).*?\{"lat": (.*?), "lng": (.*?), "loc": "(.*?)"\}', re.IGNORECASE)
    expected_dates = []
    
    for match in pattern.finditer(log_content):
        dt, sp, lat, lng, loc = match.groups()
        if "lakefront park" not in loc.lower() and "downtown marina" not in loc.lower():
            expected_dates.append(dt)
            
    expected_dates.sort()
    
    # Check if the generated dates match the sorted expected dates
    extracted_dates = [item.get("date") for item in data]
    
    if len(extracted_dates) > 0 and len(extracted_dates) <= len(expected_dates):
        # We check if any extracted date belongs to the forbidden locations.
        # Since we extracted expected_dates excluding forbidden, extracted must be a subset
        if all(d in expected_dates for d in extracted_dates):
            # To be fully correct, they should extract ALL valid ones
            if len(extracted_dates) == len(expected_dates):
                state["filtered_correctly"] = True

    # Check sorting
    if extracted_dates == sorted(extracted_dates):
        state["sorted_correctly"] = True

    # Calculate score
    score = 0
    if state["output_file_exists"]: score += 10
    if state["is_valid_json"]: score += 20
    if state["correct_schema"]: score += 20
    if state["has_correct_species"]: score += 20
    if state["filtered_correctly"]: score += 20
    if state["sorted_correctly"]: score += 10
    
    state["score"] = score

    with open("verify_result.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
