import os
import json
import sys

def verify():
    target_file = "final_schedule.json"
    result = {
        "file_exists": False,
        "json_valid": False,
        "correct_data": False,
        "errors": []
    }

    if not os.path.exists(target_file):
        result["errors"].append(f"File {target_file} not found.")
        print(json.dumps(result))
        return

    result["file_exists"] = True

    try:
        with open(target_file, "r") as f:
            data = json.load(f)
        result["json_valid"] = True
    except json.JSONDecodeError:
        result["errors"].append("Generated file is not valid JSON.")
        print(json.dumps(result))
        return

    # Expected calculations:
    # 2023-10-24:
    # John Doe: 08:00-16:00 (8h) - absent 12:00-16:00 (4h) = 4.0h
    # Jane Smith: 09:00-17:00 (8h) = 8.0h
    # Alice Johnson: 08:00-12:00 (4h) = 4.0h
    # 2023-10-25:
    # Mike Lee: 10:00-16:00 (6h) = 6.0h
    # John Doe: 08:00-16:00 (8h) = 8.0h
    # Jane Smith: 10:00-18:00 (8h) - absent 10:00-11:30 (1.5h) = 6.5h
    # Alice Johnson: 13:00-17:00 (4h) = 4.0h

    expected = {
        "2023-10-24": {
            "John Doe": 4.0,
            "Jane Smith": 8.0,
            "Alice Johnson": 4.0
        },
        "2023-10-25": {
            "Mike Lee": 6.0,
            "John Doe": 8.0,
            "Jane Smith": 6.5,
            "Alice Johnson": 4.0
        }
    }

    # Normalize float vs int comparison
    def normalize(d):
        norm_d = {}
        for date, staff in d.items():
            norm_d[date] = {}
            for name, hours in staff.items():
                norm_d[date][name] = float(hours)
        return norm_d

    try:
        norm_actual = normalize(data)
        norm_expected = normalize(expected)
        
        if norm_actual == norm_expected:
            result["correct_data"] = True
        else:
            result["errors"].append(f"Data mismatch. Expected: {norm_expected}, Got: {norm_actual}")
    except Exception as e:
        result["errors"].append(f"Error validating data structure: {str(e)}")

    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    verify()
