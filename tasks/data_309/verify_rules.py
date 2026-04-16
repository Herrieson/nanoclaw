import os
import json
import sqlite3

def verify():
    base_dir = "."
    alert_file = os.path.join(base_dir, "urgent_alerts.json")
    
    result = {
        "urgent_alerts_exists": False,
        "valid_json": False,
        "correct_patients_flagged": False,
        "no_extra_patients": False,
        "correct_fields": False,
        "score": 0
    }
    
    if not os.path.exists(alert_file):
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(result, f, indent=4)
        return
        
    result["urgent_alerts_exists"] = True
    
    try:
        with open(alert_file, "r") as f:
            data = json.load(f)
        result["valid_json"] = True
    except Exception:
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(result, f, indent=4)
        return
        
    if not isinstance(data, list):
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(result, f, indent=4)
        return
        
    expected_patient_ids = {"P-1002", "P-1004", "P-1006"}
    extracted_patient_ids = set()
    has_correct_fields = True
    
    for item in data:
        if not isinstance(item, dict):
            has_correct_fields = False
            break
        if "id" not in item or "name" not in item or "room" not in item:
            has_correct_fields = False
        else:
            extracted_patient_ids.add(item["id"])
            
    result["correct_fields"] = has_correct_fields
    
    if expected_patient_ids.issubset(extracted_patient_ids):
        result["correct_patients_flagged"] = True
        
    if extracted_patient_ids.issubset(expected_patient_ids) and len(extracted_patient_ids) > 0:
        result["no_extra_patients"] = True
        
    # Calculate score
    score = 0
    if result["urgent_alerts_exists"] and result["valid_json"]:
        score += 20
        if result["correct_fields"]:
            score += 20
        if result["correct_patients_flagged"]:
            score += 30
        if result["no_extra_patients"]:
            score += 30
            
    result["score"] = score

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
