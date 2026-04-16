import os
import json

def verify():
    workspace = "."
    result_file = os.path.join(workspace, "result.json")
    
    state = {
        "file_exists": False,
        "json_valid": False,
        "old_devices_correct": False,
        "broken_mri_correct": False,
        "extracted_old_devices": [],
        "extracted_broken_mri": None
    }
    
    expected_old_devices = {"XR-45-A2", "SS-20-C9", "IL-38-E5", "BL-90-G7", "GS-50-H8"}
    expected_broken_mri = "MRI-99X-BROKEN"

    if os.path.exists(result_file):
        state["file_exists"] = True
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["json_valid"] = True
            
            old_devices = data.get("old_devices", [])
            broken_mri = data.get("broken_mri", "")
            
            state["extracted_old_devices"] = old_devices
            state["extracted_broken_mri"] = broken_mri

            # Check old devices (<= 1950)
            if isinstance(old_devices, list) and set(old_devices) == expected_old_devices:
                state["old_devices_correct"] = True
                
            # Check broken MRI
            if broken_mri == expected_broken_mri:
                state["broken_mri_correct"] = True
                
        except Exception as e:
            pass
            
    with open(os.path.join(workspace, "verify_result.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
