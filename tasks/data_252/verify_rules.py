import os
import json

def verify():
    base_dir = "."
    manifest_path = os.path.join(base_dir, "eco_vision_manifest.json")
    reschedule_path = os.path.join(base_dir, "reschedule_notices.txt")
    
    state = {
        "manifest_exists": False,
        "manifest_valid": False,
        "volunteers_found": 0,
        "reschedule_exists": False,
        "reschedule_correct": False,
        "patients_found": 0
    }
    
    # 1. Verify Manifest
    if os.path.exists(manifest_path):
        state["manifest_exists"] = True
        try:
            with open(manifest_path, "r") as f:
                data = json.load(f)
            
            # Flexible checking for structure
            volunteers = []
            if isinstance(data, list):
                volunteers = data
            elif isinstance(data, dict):
                for v in data.values():
                    if isinstance(v, list):
                        volunteers.extend(v)
            
            found_sarah = False
            found_marcus = False
            found_chloe = False
            
            for v in volunteers:
                name = str(v.get("name", "")).lower()
                fabric = str(v.get("fabric", "")).lower()
                
                if "sarah" in name and "bamboo" in fabric:
                    found_sarah = True
                if "marcus" in name and "cotton" in fabric:
                    found_marcus = True
                if "chloe" in name and "polyester" in fabric:
                    found_chloe = True
            
            score = sum([found_sarah, found_marcus, found_chloe])
            state["volunteers_found"] = score
            if score == 3:
                state["manifest_valid"] = True
                
        except Exception as e:
            pass

    # 2. Verify Reschedule Notices
    if os.path.exists(reschedule_path):
        state["reschedule_exists"] = True
        try:
            with open(reschedule_path, "r") as f:
                content = f.read().lower()
            
            found_robert = "robert ford" in content
            found_william = "william abernathy" in content
            found_emily = "emily clark" in content
            
            state["patients_found"] = sum([found_robert, found_william])
            
            # Should find Robert and William, but NOT Emily (she is Oct 14)
            if found_robert and found_william and not found_emily:
                state["reschedule_correct"] = True
                
        except Exception as e:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
