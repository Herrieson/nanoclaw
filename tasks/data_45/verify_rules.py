import os
import json

def verify():
    base_dir = "."
    sitrep_path = os.path.join(base_dir, "SITREP.json")
    
    result = {
        "file_exists": False,
        "is_valid_json": False,
        "records_count": 0,
        "matches_expected": False,
        "errors": []
    }

    if not os.path.exists(sitrep_path):
        result["errors"].append("SITREP.json does not exist.")
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    result["file_exists"] = True

    try:
        with open(sitrep_path, "r") as f:
            data = json.load(f)
            result["is_valid_json"] = True
    except json.JSONDecodeError:
        result["errors"].append("SITREP.json is not valid JSON.")
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    if not isinstance(data, list):
        result["errors"].append("JSON root should be an array.")
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(result, f, indent=2)
        return

    result["records_count"] = len(data)

    expected_records = [
        {"Operation": "Autumn Wind", "Unit": "36th Infantry", "Commander": "Col. Redbird"},
        {"Operation": "Iron Wolf", "Unit": "1st Cav", "Commander": "Maj. Eagle"}
    ]

    # Check if exact match ignoring order
    def norm_record(r):
        return {k.lower(): str(v).lower() for k, v in r.items()}

    norm_expected = [norm_record(r) for r in expected_records]
    norm_actual = []
    
    for r in data:
        if isinstance(r, dict):
            norm_actual.append(norm_record(r))

    matched_all = True
    for expected in norm_expected:
        if expected not in norm_actual:
            matched_all = False
            result["errors"].append(f"Missing expected record: {expected}")
    
    # Also check if there are extra invalid records
    if len(norm_actual) > len(norm_expected):
        matched_all = False
        result["errors"].append("Contains invalid extra records.")

    result["matches_expected"] = matched_all

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
