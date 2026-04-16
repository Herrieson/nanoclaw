import os
import json

def verify():
    result = {
        "target_patients_found": False,
        "target_patients_correct": False,
        "conflict_report_found": False,
        "conflict_report_correct": False
    }
    
    expected_patients = {"PT-1002", "PT-1004", "PT-1006", "PT-1008"}
    expected_conflicts = {
        "Sarah Jenkins, 2023-11-10",
        "Mark O'Connor, 2023-11-12"
    }
    
    if os.path.exists("target_patients.txt"):
        result["target_patients_found"] = True
        with open("target_patients.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            extracted_patients = set(lines)
            if extracted_patients == expected_patients:
                result["target_patients_correct"] = True
                
    if os.path.exists("conflict_report.txt"):
        result["conflict_report_found"] = True
        with open("conflict_report.txt", "r") as f:
            lines = [line.strip() for line in f if line.strip()]
            extracted_conflicts = set(lines)
            if extracted_conflicts == expected_conflicts:
                result["conflict_report_correct"] = True

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
