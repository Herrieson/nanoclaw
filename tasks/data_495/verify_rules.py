import os
import json

def verify():
    result = {
        "file_exists": False,
        "is_valid_json": False,
        "correct_data": False,
        "details": {}
    }
    
    target_file = "guitar_final_grades.json"
    
    if not os.path.exists(target_file):
        result["details"]["error"] = f"{target_file} not found in the workspace."
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    result["file_exists"] = True

    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        result["is_valid_json"] = True
    except json.JSONDecodeError:
        result["details"]["error"] = f"{target_file} is not a valid JSON file."
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    # Expected calculation
    # 101: 85 - 5 (3 Absent) = 80
    # 103: 78 - 3 (4 Late) = 75
    # 104: 92 - 0 = 92
    # 106: 65 - 8 (3 Absent, 4 Late) = 57
    # 107: 70 - 0 = 70
    expected = [
        {"StudentID": "101", "Name": "Alice Smith", "FinalScore": 80},
        {"StudentID": "103", "Name": "Charlie Brown", "FinalScore": 75},
        {"StudentID": "104", "Name": "Diana Prince", "FinalScore": 92},
        {"StudentID": "106", "Name": "Fiona Gallagher", "FinalScore": 57},
        {"StudentID": "107", "Name": "George Miller", "FinalScore": 70}
    ]

    result["details"]["expected"] = expected
    result["details"]["actual"] = data

    if data == expected:
        result["correct_data"] = True
    else:
        result["details"]["error"] = "The data in the JSON file does not match the expected output or is not sorted correctly."

    with open("verify_result.json", "w") as f:
        json.dump(result, f)

if __name__ == "__main__":
    verify()
