import os
import json
import re

def verify():
    base_dir = "."
    result = {
        "recovered_exam_exists": False,
        "recovered_exam_correct": False,
        "signed_waiver_exists": False,
        "signed_waiver_name_correct": False,
        "signed_waiver_birth_correct": False,
        "signed_waiver_citizen_correct": False,
        "signed_waiver_disability_correct": False
    }

    # 1. Check exam
    recovered_path = os.path.join(base_dir, "recovered_exam.txt")
    if os.path.exists(recovered_path):
        result["recovered_exam_exists"] = True
        with open(recovered_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "CATHOLIC HISTORY EXAM" in content and "Great Schism" in content:
                result["recovered_exam_correct"] = True

    # 2. Check waiver
    waiver_path = os.path.join(base_dir, "signed_waiver.txt")
    if os.path.exists(waiver_path):
        result["signed_waiver_exists"] = True
        with open(waiver_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
            if "maria" in content:
                result["signed_waiver_name_correct"] = True
            if "chile" in content:
                result["signed_waiver_birth_correct"] = True
            if "not a" in content or "non-citizen" in content or "no" in content.split("citizen")[1][:15]:
                result["signed_waiver_citizen_correct"] = True
            if "yes" in content.split("disability")[1][:15]:
                result["signed_waiver_disability_correct"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
