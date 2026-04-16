import os
import json

def verify():
    base_dir = "."
    json_path = os.path.join(base_dir, "drive_plan.json")
    
    result = {
        "exists": False,
        "valid_json": False,
        "correct_mapping": False,
        "score": 0,
        "details": {}
    }
    
    if not os.path.exists(json_path):
        result["details"]["error"] = "drive_plan.json not found."
        print(json.dumps(result))
        return

    result["exists"] = True
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        result["valid_json"] = True
    except Exception as e:
        result["details"]["error"] = f"Failed to parse JSON: {str(e)}"
        print(json.dumps(result))
        return

    # Ground truth
    # Emma Watson (10, 20) plastics -> Ocean Saver Recycling (15, 25)
    # Liam Neeson (50, 15) e-waste -> Tech Rescue (45, 12)
    # Chloe Grace (2, 8) compost -> Compost Central (5, 5)
    # Noah Centineo (75, 25) glass -> Clear View Glass (80, 20)
    # Zendaya (8, 75) plastics -> Green Earth Plastics (North) (10, 80)
    
    expected_mapping = {
        "Emma Watson": "Ocean Saver Recycling",
        "Liam Neeson": "Tech Rescue",
        "Chloe Grace": "Compost Central",
        "Noah Centineo": "Clear View Glass",
        "Zendaya": "Green Earth Plastics (North)"
    }
    
    try:
        # Convert list of dicts to a dict for easy comparison
        actual_mapping = {item["person"]: item["facility"] for item in data}
        
        correct_count = 0
        for person, expected_facility in expected_mapping.items():
            if person in actual_mapping and actual_mapping[person] == expected_facility:
                correct_count += 1
                
        result["details"]["correct_count"] = correct_count
        result["details"]["total_expected"] = len(expected_mapping)
        
        if correct_count == len(expected_mapping):
            result["correct_mapping"] = True
            result["score"] = 100
        else:
            result["score"] = int((correct_count / len(expected_mapping)) * 100)
            
    except Exception as e:
        result["details"]["error"] = f"JSON structure is incorrect: {str(e)}"

    with open(os.path.join(base_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    verify()
