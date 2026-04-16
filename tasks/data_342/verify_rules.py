import os
import json
import glob

def verify():
    base_dir = "."
    result = {
        "summary_exists": False,
        "correct_worst_building": False,
        "correct_avg": False,
        "notices_dir_exists": False,
        "correct_notice_files_created": False,
        "notices_content_valid": False,
        "score": 0,
        "details": []
    }

    summary_path = os.path.join(base_dir, "summary.json")
    if os.path.exists(summary_path):
        result["summary_exists"] = True
        try:
            with open(summary_path, "r") as f:
                data = json.load(f)
                
            if data.get("worst_building_id") == "B200":
                result["correct_worst_building"] = True
                result["score"] += 30
            else:
                result["details"].append("Wrong worst building ID.")

            if data.get("avg_kwh_per_sqft") == 2.20:
                result["correct_avg"] = True
                result["score"] += 20
            else:
                result["details"].append(f"Wrong average calculated: {data.get('avg_kwh_per_sqft')}")
        except Exception as e:
            result["details"].append(f"Error reading summary.json: {e}")
    else:
        result["details"].append("summary.json not found.")

    notices_dir = os.path.join(base_dir, "notices")
    if os.path.isdir(notices_dir):
        result["notices_dir_exists"] = True
        
        expected_files = ["notice_101_Johnson.txt", "notice_102_Williams.txt", "notice_201_Brown.txt"]
        found_files = [os.path.basename(p) for p in glob.glob(os.path.join(notices_dir, "*.txt"))]
        
        if sorted(expected_files) == sorted(found_files):
            result["correct_notice_files_created"] = True
            result["score"] += 20
            
            content_valid = True
            for f in expected_files:
                with open(os.path.join(notices_dir, f), "r") as nf:
                    content = nf.read().lower()
                    if "sustainable living" not in content or "15%" not in content:
                        content_valid = False
                        result["details"].append(f"Notice {f} missing keywords.")
            
            if content_valid:
                result["notices_content_valid"] = True
                result["score"] += 30
        else:
            result["details"].append(f"Expected notices {expected_files}, found {found_files}")
    else:
        result["details"].append("notices directory not found.")

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
