import os
import json

def verify():
    base_dir = "."
    faulty_file = os.path.join(base_dir, "faulty_device.txt")
    result_file = os.path.join(base_dir, "attenuation_result.txt")
    
    state = {
        "faulty_file_exists": False,
        "result_file_exists": False,
        "mac_correct": False,
        "calc_correct": False,
        "extracted_mac": None,
        "extracted_calc": None
    }
    
    if os.path.exists(faulty_file):
        state["faulty_file_exists"] = True
        with open(faulty_file, "r") as f:
            content = f.read().strip()
            state["extracted_mac"] = content
            if "00:14:22:01:23:45" in content.upper():
                state["mac_correct"] = True
                
    if os.path.exists(result_file):
        state["result_file_exists"] = True
        with open(result_file, "r") as f:
            content = f.read().strip()
            state["extracted_calc"] = content
            # Calculation: Max signal = 95, Min noise = 12
            # Diff = 83. 83 * 1.618 = 134.294
            if "134.294" in content:
                state["calc_correct"] = True
                
    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
