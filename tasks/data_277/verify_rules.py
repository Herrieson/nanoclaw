import os
import json

def verify():
    base_dir = "."
    target_file = os.path.join(base_dir, "grant_submission.json")
    
    result = {
        "file_exists": False,
        "valid_json": False,
        "schema_correct": False,
        "total_funding_correct": False,
        "families_correct": False,
        "sorting_correct": False,
        "details": []
    }

    if not os.path.exists(target_file):
        result["details"].append("grant_submission.json not found.")
        return result
    
    result["file_exists"] = True

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        result["valid_json"] = True
    except Exception as e:
        result["details"].append(f"Failed to parse JSON: {str(e)}")
        return result

    if "total_funding_requested" not in data or "eligible_families" not in data:
        result["details"].append("Missing required root keys.")
        return result
    
    result["schema_correct"] = True

    # Expected:
    # F001: 2 kids -> 1500 + 1000 = 2500
    # F002: 1 kid -> 1500 + 500 = 2000
    # F003: 3 kids -> 1500 + 1500 = 3000
    # F007: 1 kid -> 1500 + 500 = 2000
    # Total = 9500
    expected_total = 9500
    if float(data.get("total_funding_requested", 0)) == expected_total:
        result["total_funding_correct"] = True
    else:
        result["details"].append(f"Expected total_funding_requested={expected_total}, got {data.get('total_funding_requested')}")

    expected_families = {
        "F001": {"eligible_children_count": 2, "funding_amount": 2500},
        "F002": {"eligible_children_count": 1, "funding_amount": 2000},
        "F003": {"eligible_children_count": 3, "funding_amount": 3000},
        "F007": {"eligible_children_count": 1, "funding_amount": 2000}
    }

    families = data.get("eligible_families", [])
    if len(families) == 4:
        family_ids = [f.get("family_id") for f in families]
        if family_ids == sorted(family_ids):
            result["sorting_correct"] = True
        else:
            result["details"].append("Families are not sorted by family_id.")
        
        match_count = 0
        for f in families:
            fid = f.get("family_id")
            if fid in expected_families:
                exp = expected_families[fid]
                if f.get("eligible_children_count") == exp["eligible_children_count"] and \
                   float(f.get("funding_amount", 0)) == exp["funding_amount"]:
                    match_count += 1
                else:
                    result["details"].append(f"Incorrect calculations for family {fid}.")
            else:
                result["details"].append(f"Unexpected family included: {fid}")
        
        if match_count == 4:
            result["families_correct"] = True
    else:
        result["details"].append(f"Expected 4 families, got {len(families)}")

    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    
    print(json.dumps(result, indent=2))
    return result

if __name__ == "__main__":
    verify()
