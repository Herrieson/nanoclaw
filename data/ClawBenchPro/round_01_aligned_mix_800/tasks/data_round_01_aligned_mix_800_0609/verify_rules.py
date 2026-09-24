import os
import json
import sys
import re

def verify():
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "manifest_exists": False,
        "valid_json": False,
        "correct_trail_found": False,
        "correct_weight_calculated": False
    }
    
    manifest_path = os.path.join(work_dir, "hike_manifest.json")
    if os.path.exists(manifest_path):
        state["manifest_exists"] = True
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            data_str = json.dumps(data).lower()
            
            # The target trail that meets all criteria is "Little Bear Loop"
            if "little bear loop" in data_str:
                state["correct_trail_found"] = True
                
            # The needed gear total is 157.5 oz, which equals ~4.465 kg
            numbers = re.findall(r"[\d\.]+", data_str)
            for num in numbers:
                try:
                    val = float(num)
                    if 4.45 <= val <= 4.48:
                        state["correct_weight_calculated"] = True
                except ValueError:
                    pass
        except Exception:
            pass
            
    with open(os.path.join(work_dir, "state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
