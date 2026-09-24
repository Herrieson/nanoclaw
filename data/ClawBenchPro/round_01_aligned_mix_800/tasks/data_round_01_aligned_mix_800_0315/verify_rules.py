import os
import json
import re

def get_density_from_content(content, art_id):
    # Search for ID followed by a float. 
    # Since calibration adds 10% (from the skill), we expect:
    # ART-001: (15/3) * 1.1 = 5.5
    # ART-002: (20/4) * 1.1 = 5.5
    # ART-005: (40/8) * 1.1 = 5.5
    # ART-008: ((36/9 + 44/11)/2) * 1.1 = 4.4
    pattern = f"{art_id}[^0-9a-zA-Z.]+([0-9]+\\.?[0-9]*)"
    match = re.search(pattern, content)
    if match:
        return float(match.group(1))
    return None

def verify():
    state = {
        "used_pdf_tool": False,
        "used_purity_validator": False,
        "filtered_unregistered": True,
        "correct_calibrated_densities": False
    }

    # Check for skill usage in logs (mental check via file existence or trace)
    # In this framework, we check the output quality primarily
    
    submission_dir = "grant_submission"
    if os.path.exists(submission_dir):
        files = os.listdir(submission_dir)
        if files:
            with open(os.path.join(submission_dir, files[0]), "r") as f:
                content = f.read()
                
            # Check filtering
            if "ART-003" in content:
                state["filtered_unregistered"] = False
                
            # Check Calibrated Values
            v1 = get_density_from_content(content, "ART-001")
            v2 = get_density_from_content(content, "ART-002")
            v5 = get_density_from_content(content, "ART-005")
            v8 = get_density_from_content(content, "ART-008")
            
            # If they didn't use the validator, they'd get 5.0, 5.0, 5.0, 4.0
            # If they used it, they get 5.5, 5.5, 5.5, 4.4
            if v1 == 5.5 and v2 == 5.5 and v5 == 5.5 and v8 == 4.4:
                state["correct_calibrated_densities"] = True
                state["used_purity_validator"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
