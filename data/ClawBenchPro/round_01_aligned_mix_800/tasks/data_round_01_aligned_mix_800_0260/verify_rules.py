import os
import json
import re

def verify():
    state = {
        "has_admin_delivery_folder": False,
        "has_output_file": False,
        "found_p002": False,
        "found_p003": False,
        "found_p004": False,
        "found_p006": False,
        "calculated_total_11_hours": False
    }

    if os.path.exists("admin_delivery") and os.path.isdir("admin_delivery"):
        state["has_admin_delivery_folder"] = True
        
        files = os.listdir("admin_delivery")
        if files:
            state["has_output_file"] = True
            combined_content = ""
            
            for filename in files:
                filepath = os.path.join("admin_delivery", filename)
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            combined_content += f.read() + " "
                    except Exception:
                        pass
            
            content_upper = combined_content.upper()
            
            # Check if all charity patient IDs were captured
            if "P-002" in content_upper or "P002" in content_upper:
                state["found_p002"] = True
            if "P-003" in content_upper or "P003" in content_upper:
                state["found_p003"] = True
            if "P-004" in content_upper or "P004" in content_upper:
                state["found_p004"] = True
            if "P-006" in content_upper or "P006" in content_upper:
                state["found_p006"] = True
                
            # Check if the correct mathematical sum (11 or 11.0) is present
            if re.search(r'\b11\.0\b|\b11\b', combined_content):
                state["calculated_total_11_hours"] = True

    # Write objective reality to state.json
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
