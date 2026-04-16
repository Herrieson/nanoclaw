import os
import json

def verify():
    base_dir = "community_fund"
    target_file = os.path.join(base_dir, "final_list.txt")
    
    result = {
        "target_file_exists": False,
        "extracted_names": [],
        "correct_order": False,
        "error": None
    }

    if not os.path.exists(target_file):
        result["error"] = "final_list.txt not found."
        with open("verify_result.json", "w") as f:
            json.dump(result, f, indent=4)
        return

    result["target_file_exists"] = True
    
    try:
        with open(target_file, "r") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
            
        result["extracted_names"] = lines
        
        # Ground truth calculation:
        # Tariq: 300 - 100 = 200
        # Fatima: 200 - 20 = 180
        # Ali: 150 - 50 = 100
        # Bilal: 80 - 0 = 80
        # Omar: 50 - 50 = 0
        expected = ["Tariq", "Fatima", "Ali"]
        
        # Check if the extracted names match the expected order exactly (case-insensitive)
        extracted_lower = [name.lower() for name in lines[:3]]
        expected_lower = [name.lower() for name in expected]
        
        if extracted_lower == expected_lower:
            result["correct_order"] = True
            
    except Exception as e:
        result["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
