import os
import csv
import json

def verify():
    result = {
        "success": False,
        "score": 0,
        "feedback": []
    }
    
    csv_path = "assignments.csv"
    if not os.path.exists(csv_path):
        result["feedback"].append("File assignments.csv not found.")
        return json.dumps(result)

    # Reference data
    tree_to_soil = {
        "Red Maple": "Loam",
        "White Pine": "Sandy",
        "River Birch": "Clay"
    }
    
    zone_caps = {
        "Z-North": {"soil": "Loam", "cap": 3},
        "Z-South": {"soil": "Sandy", "cap": 2},
        "Z-East": {"soil": "Clay", "cap": 2},
        "Z-West": {"soil": "Loam", "cap": 2},
        "Z-Central": {"soil": "Sandy", "cap": 1}
    }
    
    # Track usage
    assigned_students = set()
    zone_counts = {k: 0 for k in zone_caps.keys()}
    
    score = 0
    valid_rows = 0
    errors = 0

    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            
            # Check headers
            expected_headers = {"Student_Name", "Tree_Choice", "Assigned_Zone"}
            if not expected_headers.issubset(set(reader.fieldnames or [])):
                result["feedback"].append(f"Missing headers. Found: {reader.fieldnames}")
                errors += 1
                
            for row in reader:
                student = row.get("Student_Name", "").strip()
                tree = row.get("Tree_Choice", "").strip()
                zone = row.get("Assigned_Zone", "").strip()
                
                if not student or not tree or not zone:
                    continue
                    
                if student in assigned_students:
                    result["feedback"].append(f"Duplicate assignment for student: {student}")
                    errors += 1
                    continue
                    
                assigned_students.add(student)
                
                if zone not in zone_caps:
                    result["feedback"].append(f"Invalid zone assigned: {zone}")
                    errors += 1
                    continue
                    
                expected_soil = tree_to_soil.get(tree)
                actual_soil = zone_caps[zone]["soil"]
                
                if expected_soil != actual_soil:
                    result["feedback"].append(f"Soil mismatch for {student}. Tree {tree} needs {expected_soil}, but {zone} is {actual_soil}")
                    errors += 1
                    continue
                    
                zone_counts[zone] += 1
                valid_rows += 1
                
        # Check constraints
        for z, count in zone_counts.items():
            if count > zone_caps[z]["cap"]:
                result["feedback"].append(f"Zone {z} overcrowded. Capacity: {zone_caps[z]['cap']}, Assigned: {count}")
                errors += 1
                
        # Expecting exactly 10 valid assignments:
        # Loam (5 cap): Alice, Frank, Grace, Hank, Ivy (Jack skipped)
        # Sandy (3 cap): Bob, David, Eve (Liam skipped)
        # Clay (2 cap): Charlie, Mia
        expected_total = 10
        
        if errors == 0 and valid_rows == expected_total:
            score = 100
            result["success"] = True
            result["feedback"].append("All constraints successfully met!")
        else:
            score = max(0, int((valid_rows / expected_total) * 100) - (errors * 15))
            result["feedback"].append(f"Valid rows: {valid_rows}/{expected_total}. Errors: {errors}")
            
    except Exception as e:
        result["feedback"].append(f"Error parsing CSV: {str(e)}")
        
    result["score"] = score
    print(json.dumps(result))

if __name__ == "__main__":
    verify()
