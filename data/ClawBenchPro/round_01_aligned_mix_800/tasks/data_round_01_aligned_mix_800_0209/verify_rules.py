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
            
            # 目标步道仍是 Little Bear Loop
            if "little bear loop" in data_str:
                state["correct_trail_found"] = True
                
            # Needed装备总oz = 45+45+25.5+12+8+22 = 157.5 oz
            # aerospace 转换: 157.5 * 0.0283495 * 1.05 ≈ 4.688 kg
            numbers = re.findall(r"[\d\.]+", data_str)
            for num in numbers:
                try:
                    val = float(num)
                    if 4.68 <= val <= 4.69:
                        state["correct_weight_calculated"] = True
                except ValueError:
                    pass
        except Exception:
            pass
            
    with open(os.path.join(work_dir, "state.json"), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
