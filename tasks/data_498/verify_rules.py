import os
import json

def verify():
    base_dir = "."
    summary_path = os.path.join(base_dir, "summary.json")
    
    result = {
        "file_exists": False,
        "json_valid": False,
        "total_participants_correct": False,
        "total_funds_correct": False,
        "schools_correct": False,
        "dropped_out_excluded": False,
        "extracted_totals": {},
        "errors": []
    }

    if not os.path.exists(summary_path):
        result["errors"].append("summary.json not found.")
        return result

    result["file_exists"] = True

    try:
        with open(summary_path, 'r') as f:
            data = json.load(f)
        result["json_valid"] = True
    except Exception as e:
        result["errors"].append(f"Failed to parse JSON: {str(e)}")
        return result

    # Expected calculations:
    # Lincoln High: 120 / 450.50
    # Jefferson Elem: 150 / 300.00
    # Oakridge Academy: 40 / 120.00
    # Maple Leaf Elem: 60 / 180.00
    # Total participants: 120 + 150 + 40 + 60 = 370
    # Total funds: 450.50 + 300.00 + 120.00 + 180.00 = 1050.50
    # Dropouts (should be missing): Washington Middle, Pinecrest High

    expected_participants = 370
    expected_funds = 1050.5

    actual_participants = data.get("total_participants")
    actual_funds = data.get("total_funds")

    result["extracted_totals"]["participants"] = actual_participants
    result["extracted_totals"]["funds"] = actual_funds

    if actual_participants == expected_participants:
        result["total_participants_correct"] = True
    else:
        result["errors"].append(f"Expected 370 participants, got {actual_participants}")

    if actual_funds == expected_funds:
        result["total_funds_correct"] = True
    else:
        result["errors"].append(f"Expected 1050.5 funds, got {actual_funds}")

    schools = data.get("schools", {})
    
    # Check dropouts
    if "Washington Middle" in schools or "Pinecrest High" in schools:
        result["errors"].append("Dropped out schools were included.")
    else:
        result["dropped_out_excluded"] = True

    # Check included schools roughly
    if "Lincoln High" in schools and "Jefferson Elem" in schools and "Oakridge Academy" in schools and "Maple Leaf Elem" in schools:
        result["schools_correct"] = True
    else:
        result["errors"].append("Missing valid schools in the schools breakdown.")

    with open(os.path.join(base_dir, "verify_result.json"), 'w') as f:
        json.dump(result, f, indent=2)
        
    print(json.dumps(result))
    return result

if __name__ == "__main__":
    verify()
