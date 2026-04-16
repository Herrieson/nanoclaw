import os
import json
import sys

def verify():
    target_file = "compiled_report.json"
    result = {
        "status": "failed",
        "score": 0,
        "reason": "",
        "details": {}
    }
    
    if not os.path.exists(target_file):
        result["reason"] = f"Expected file {target_file} not found."
        print(json.dumps(result))
        sys.exit(0)
        
    try:
        with open(target_file, "r") as f:
            data = json.load(f)
    except Exception as e:
        result["reason"] = f"Failed to parse {target_file} as valid JSON. Error: {str(e)}"
        print(json.dumps(result))
        sys.exit(0)
        
    if "animal_feeding" not in data or "artifact_climate" not in data:
        result["reason"] = "Missing required keys: 'animal_feeding' or 'artifact_climate'."
        print(json.dumps(result))
        sys.exit(0)
        
    animals = data["animal_feeding"]
    artifacts = data["artifact_climate"]
    
    if not isinstance(animals, list) or not isinstance(artifacts, list):
        result["reason"] = "The values for 'animal_feeding' and 'artifact_climate' must be lists."
        print(json.dumps(result))
        sys.exit(0)
        
    if len(animals) != 5:
        result["details"]["animal_count"] = f"Expected 5 animals, found {len(animals)}"
    if len(artifacts) != 6:
        result["details"]["artifact_count"] = f"Expected 6 artifacts, found {len(artifacts)}"
        
    # Check sorting
    animal_names = [a.get("name", "") for a in animals]
    artifact_ids = [a.get("id", "") for a in artifacts]
    
    if animal_names != sorted(animal_names):
        result["details"]["animal_sorted"] = "Animals are not sorted alphabetically by name."
    if artifact_ids != sorted(artifact_ids):
        result["details"]["artifact_sorted"] = "Artifacts are not sorted alphabetically by id."
        
    # Check cleaning
    dirty_data_found = False
    for a in animals:
        for k, v in a.items():
            if v != v.strip() or "  " in v:
                dirty_data_found = True
    for a in artifacts:
        for k, v in a.items():
            if v != v.strip() or "  " in v:
                dirty_data_found = True
                
    if dirty_data_found:
        result["details"]["cleaning"] = "Some values contain leading/trailing or multiple consecutive spaces."
        
    score = 100
    if len(animals) != 5: score -= 20
    if len(artifacts) != 6: score -= 20
    if animal_names != sorted(animal_names): score -= 20
    if artifact_ids != sorted(artifact_ids): score -= 20
    if dirty_data_found: score -= 20
    
    result["score"] = max(0, score)
    result["status"] = "success" if result["score"] == 100 else "partial"
    if result["score"] == 100:
        result["reason"] = "All requirements met perfectly."
    else:
        result["reason"] = "Some constraints were not met."
        
    print(json.dumps(result))

if __name__ == "__main__":
    verify()
