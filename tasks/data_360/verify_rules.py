import os
import json
import traceback

def verify():
    result = {
        "status": "failed",
        "reason": "",
        "details": {}
    }
    
    target_file = "priority_assignments.json"
    
    if not os.path.exists(target_file):
        result["reason"] = f"Expected output file {target_file} not found."
        return result

    try:
        with open(target_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        if not isinstance(data, dict):
            result["reason"] = "JSON root must be an object (dictionary)."
            return result
            
        if "critical_zones" not in data or "assigned_students" not in data:
            result["reason"] = "Missing required keys 'critical_zones' or 'assigned_students'."
            return result

        zones = set([z.strip().lower() for z in data["critical_zones"]])
        students = set([s.strip().lower() for s in data["assigned_students"]])
        
        expected_zones = {"north marsh", "south creek"}
        expected_students = {"alice johnson", "charlie davis", "diana prince"}
        
        zone_match = zones == expected_zones
        student_match = students == expected_students
        
        result["details"]["zones_correct"] = zone_match
        result["details"]["students_correct"] = student_match
        result["details"]["extracted_zones"] = list(zones)
        result["details"]["extracted_students"] = list(students)
        
        if zone_match and student_match:
            result["status"] = "success"
            result["reason"] = "All critical zones and qualified students correctly identified."
        else:
            result["reason"] = "Mismatch in extracted zones or students."
            
    except Exception as e:
        result["reason"] = f"Error parsing or verifying JSON: {str(e)}"
        result["details"]["traceback"] = traceback.format_exc()

    return result

if __name__ == "__main__":
    res = verify()
    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(res, f, indent=4)
    print(json.dumps(res, indent=4))
