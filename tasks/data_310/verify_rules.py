import os
import json

def verify():
    workspace_dir = "workspace"
    target_file = os.path.join(workspace_dir, "faulty_workers.txt")
    
    result = {
        "file_exists": False,
        "correct_names_found": False,
        "extra_incorrect_names": False,
        "details": ""
    }
    
    expected_names = {"David Nguyen", "Emily Chen", "Aaron Levi"}
    
    if os.path.exists(target_file):
        result["file_exists"] = True
        with open(target_file, "r") as f:
            content = f.read().strip().splitlines()
        
        found_names = set(name.strip() for name in content if name.strip())
        
        if expected_names.issubset(found_names):
            result["correct_names_found"] = True
        
        if not found_names.issubset(expected_names):
            result["extra_incorrect_names"] = True
            
        result["details"] = f"Found names: {list(found_names)}"
    else:
        result["details"] = "faulty_workers.txt not found."

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)

if __name__ == "__main__":
    verify()
