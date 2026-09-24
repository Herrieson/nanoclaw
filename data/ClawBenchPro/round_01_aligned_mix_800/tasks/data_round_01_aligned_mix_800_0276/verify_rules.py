import os
import json
import re

def verify():
    state = {
        "output_dir_exists": False,
        "output_file_exists": False,
        "deductible_correct": False,
        "nondeductible_correct": False,
        "flagged_employee_correct": False
    }

    target_dir = "ready_for_review"
    
    if os.path.isdir(target_dir):
        state["output_dir_exists"] = True
        
        files = os.listdir(target_dir)
        if len(files) > 0:
            state["output_file_exists"] = True
            
            # Read all content from generated files in the directory
            content = ""
            for f_name in files:
                f_path = os.path.join(target_dir, f_name)
                if os.path.isfile(f_path):
                    with open(f_path, "r", encoding="utf-8", errors="ignore") as f:
                        content += f.read() + "\n"
            
            # Check for the objective values
            # Deductible total: 1551.00
            # Non-deductible total: 939.99
            # Flagged: EMP-042
            
            content_lower = content.lower()
            
            # Check deductible (1551 or 1551.00)
            if re.search(r'1551(\.00?)?', content):
                state["deductible_correct"] = True
                
            # Check non-deductible (939.99)
            if "939.99" in content:
                state["nondeductible_correct"] = True
                
            # Check if EMP-042 is flagged
            if "emp-042" in content_lower:
                state["flagged_employee_correct"] = True

    # Write objective findings to physical state file
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
