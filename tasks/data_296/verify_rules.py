import os
import json

def verify():
    base_dir = "."
    payload_path = os.path.join(base_dir, "upload_payload.json")
    
    result = {
        "payload_exists": False,
        "is_valid_json": False,
        "is_list": False,
        "correct_calculations": False,
        "details": ""
    }
    
    if not os.path.exists(payload_path):
        result["details"] = "upload_payload.json not found."
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(result, f)
        return

    result["payload_exists"] = True
    
    try:
        with open(payload_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        result["is_valid_json"] = True
    except Exception as e:
        result["details"] = f"Invalid JSON: {str(e)}"
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(result, f)
        return

    if not isinstance(data, list):
        result["details"] = "JSON root is not a list."
        with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
            json.dump(result, f)
        return
        
    result["is_list"] = True
    
    # Expected totals:
    # Alice Johnson (1001): 45 + 55 = 100
    # Bob Smith (1002): 50 + 40 = 90
    # Charlie Brown (1003): 20 + 15 = 35
    # David Lee (1004): 30
    # Emma Davis (1005): 100
    
    expected = {
        1001: 100,
        1002: 90,
        1003: 35,
        1004: 30,
        1005: 100
    }
    
    actual = {}
    for item in data:
        if isinstance(item, dict) and "student_id" in item and "total_pages" in item:
            actual[item["student_id"]] = item["total_pages"]
            
    is_correct = True
    for student_id, total in expected.items():
        if actual.get(student_id) != total:
            is_correct = False
            result["details"] += f" ID {student_id} expected {total}, got {actual.get(student_id)}."
            
    if is_correct and len(actual) == len(expected):
        result["correct_calculations"] = True
        result["details"] = "All calculations are correct."
        
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
