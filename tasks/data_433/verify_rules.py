import os
import json
import re

def verify():
    workspace_dir = "."
    target_file = os.path.join(workspace_dir, "urgent_delivery.txt")
    
    result = {
        "success": False,
        "reason": "",
        "details": {}
    }
    
    if not os.path.exists(target_file):
        result["reason"] = "urgent_delivery.txt not found in workspace."
        return result
        
    try:
        with open(target_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            
        result["details"]["file_content"] = content
        
        # Expected: Address: 740 Park Avenue, Penthouse B | Code: ELEVATOR_OVERRIDE_99
        expected_pattern = r"^Address:\s*740 Park Avenue, Penthouse B\s*\|\s*Code:\s*ELEVATOR_OVERRIDE_99$"
        
        if re.match(expected_pattern, content, re.IGNORECASE):
            result["success"] = True
            result["reason"] = "Address and decoded access code correctly identified and formatted."
        else:
            result["reason"] = "File found, but content does not match the expected format, address, or decoded code."
            
    except Exception as e:
        result["reason"] = f"Error reading target file: {str(e)}"
        
    # Write output state
    with open(os.path.join(workspace_dir, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4)
        
    print(json.dumps(result))

if __name__ == "__main__":
    verify()
