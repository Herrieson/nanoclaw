import os
import json

def verify():
    base_dir = "."
    target_file = "cobra_report_final.json"
    result = {
        "file_exists": False,
        "valid_json": False,
        "correct_count": 0,
        "uppercase_correct": False,
        "required_fields_present": False,
        "hidden_log_entry_found": False
    }

    if os.path.exists(target_file):
        result["file_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
                result["valid_json"] = True
                
                # 预期名单: 
                # 1. MICHEAL O'DONNELL (from XML)
                # 2. BRIDGET MURPHY (from Log)
                # 3. EILEEN WALSH (from JSON cache)
                
                names = [item.get("Full_Name", "") for item in data]
                result["correct_count"] = len(names)
                
                if all(n == n.upper() for n in names) and len(names) > 0:
                    result["uppercase_correct"] = True
                
                if any("BRIDGET MURPHY" in n for n in names):
                    result["hidden_log_entry_found"] = True
                
                if all("Social_Security_Number" in item and "Eligibility_Status" in item for item in data):
                    result["required_fields_present"] = True
        except:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
