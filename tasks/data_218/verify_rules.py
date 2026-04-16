import os
import csv
import json

def verify():
    result = {
        "file_exists": False,
        "correct_columns": False,
        "correct_sorting": False,
        "correct_residents": False,
        "staff_assigned_correctly": False,
        "score": 0,
        "details": []
    }
    
    file_path = "approved_roster.csv"
    if not os.path.exists(file_path):
        result["details"].append("File approved_roster.csv does not exist.")
        return result

    result["file_exists"] = True
    
    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration:
            result["details"].append("File is empty.")
            return result
        
        header = [h.strip() for h in header]
        expected_header = ["Resident Name", "Status", "Assigned Staff"]
        if header == expected_header:
            result["correct_columns"] = True
        else:
            result["details"].append(f"Header mismatch. Expected {expected_header}, got {header}.")
        
        rows = []
        for row in reader:
            if len(row) >= 3:
                rows.append([col.strip() for col in row[:3]])
                
    if not rows:
        result["details"].append("No data rows found in CSV.")
        return result

    # Check sorting
    resident_names = [r[0] for r in rows]
    if resident_names == sorted(resident_names):
        result["correct_sorting"] = True
    else:
        result["details"].append("Rows are not sorted alphabetically by Resident Name.")

    # Validate logical correctness
    expected_residents = {"Alice", "Charlie", "Diana", "Edward", "Fiona"}
    actual_residents = set(resident_names)
    
    if expected_residents == actual_residents:
        result["correct_residents"] = True
    else:
        result["details"].append(f"Expected residents {expected_residents}, but got {actual_residents}.")
        
    available_staff_pool = {"Nurse_Sarah", "Orderly_Mike", "Orderly_Anna"}
    used_staff = set()
    staff_valid = True
    
    for row in rows:
        name, status, staff = row
        if name in ["Alice", "Edward"]:
            if status != "OK" or staff != "":
                staff_valid = False
                result["details"].append(f"{name} should have status OK and no assigned staff.")
        elif name in ["Charlie", "Diana", "Fiona"]:
            if status != "Needs Escort":
                staff_valid = False
                result["details"].append(f"{name} should have status Needs Escort.")
            if staff not in available_staff_pool:
                staff_valid = False
                result["details"].append(f"{name} is assigned to invalid or unavailable staff: '{staff}'.")
            if staff in used_staff:
                staff_valid = False
                result["details"].append(f"Staff '{staff}' was assigned multiple times.")
            used_staff.add(staff)
            
    if staff_valid:
        result["staff_assigned_correctly"] = True

    # Calculate Score
    score = 0
    if result["file_exists"]: score += 10
    if result["correct_columns"]: score += 20
    if result["correct_sorting"]: score += 20
    if result["correct_residents"]: score += 25
    if result["staff_assigned_correctly"]: score += 25
    
    result["score"] = score

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)
        
    return result

if __name__ == "__main__":
    verify()
