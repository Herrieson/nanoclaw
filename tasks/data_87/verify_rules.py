import os
import json
import re

def verify():
    workspace = os.environ.get("WORKSPACE_DIR", ".")
    target_file = os.path.join(workspace, "display_plan.md")
    
    result = {
        "file_exists": False,
        "contains_correct_items": False,
        "excludes_wrong_items": False,
        "correct_total_value": False,
        "total_score": 0
    }

    if not os.path.exists(target_file):
        with open("verify_result.json", "w") as f:
            json.dump(result, f)
        return

    result["file_exists"] = True
    
    with open(target_file, "r") as f:
        content = f.read().lower()

    # Expected items: Noguchi Coffee Table (2500), Eames Lounge Chair and Ottoman (6000), Kofod-Larsen Rosewood Sideboard (8500)
    # Total: 17000
    
    expected_items = ["noguchi", "eames", "kofod-larsen"]
    wrong_items = ["nakashima", "mashiko", "kutani", "wegner"]
    
    if all(item in content for item in expected_items):
        result["contains_correct_items"] = True
        
    if all(item not in content for item in wrong_items):
        result["excludes_wrong_items"] = True
        
    if "17000" in content or "17,000" in content:
        result["correct_total_value"] = True

    score = 0
    if result["file_exists"]: score += 10
    if result["contains_correct_items"]: score += 30
    if result["excludes_wrong_items"]: score += 20
    if result["correct_total_value"]: score += 40
    
    result["total_score"] = score

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
