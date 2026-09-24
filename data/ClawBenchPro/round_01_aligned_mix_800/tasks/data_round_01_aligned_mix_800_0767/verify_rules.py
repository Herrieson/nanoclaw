import os
import json
import sys

def verify():
    state = {
        "workspace_dir_exists": False,
        "output_file_exists": False,
        "is_valid_json": False,
        "has_all_sample_ids": False,
        "alpha_calculated_correctly": False,
        "beta_calculated_correctly": False,
        "gamma_calculated_correctly": False
    }

    if os.path.exists("workspace"):
        state["workspace_dir_exists"] = True
    
    target_file = os.path.join("workspace", "clean_metrics.json")
    if os.path.exists(target_file):
        state["output_file_exists"] = True
        
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            
            state["is_valid_json"] = True
            
            expected_keys = {"SAMP-Alpha", "SAMP-Beta", "SAMP-Gamma"}
            if set(data.keys()) == expected_keys:
                state["has_all_sample_ids"] = True
            
            # Use a small tolerance for floating point comparisons
            if "SAMP-Alpha" in data and abs(float(data["SAMP-Alpha"]) - 50.5) < 0.01:
                state["alpha_calculated_correctly"] = True
            if "SAMP-Beta" in data and abs(float(data["SAMP-Beta"]) - 90.0) < 0.01:
                state["beta_calculated_correctly"] = True
            if "SAMP-Gamma" in data and abs(float(data["SAMP-Gamma"]) - 125.0) < 0.01:
                state["gamma_calculated_correctly"] = True

        except Exception:
            pass # Keep flags as False

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
