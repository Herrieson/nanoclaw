import os
import json
import sys

def verify():
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "deliverables_folder_exists": False,
        "valid_json_report_exists": False,
        "identified_exceeds_limit_clm_8811": False,
        "identified_predates_policy_clm_8812": False,
        "identified_strict_exceeds_limit_clm_8813": False,
        "correctly_excluded_valid_clm_8810": False,
        "correctly_excluded_valid_clm_8814": False
    }
    
    deliverables_path = os.path.join(work_dir, "deliverables")
    
    if os.path.exists(deliverables_path) and os.path.isdir(deliverables_path):
        state["deliverables_folder_exists"] = True
        
        # Look for any JSON file in the deliverables folder
        for filename in os.listdir(deliverables_path):
            file_path = os.path.join(deliverables_path, filename)
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    
                    state["valid_json_report_exists"] = True
                    data_str = json.dumps(data)
                    
                    # Check for presence of invalid claims
                    if "CLM-8811" in data_str:
                        state["identified_exceeds_limit_clm_8811"] = True
                    if "CLM-8812" in data_str:
                        state["identified_predates_policy_clm_8812"] = True
                    if "CLM-8813" in data_str:
                        state["identified_strict_exceeds_limit_clm_8813"] = True
                        
                    # Check for absence of valid claims
                    if "CLM-8810" not in data_str:
                        state["correctly_excluded_valid_clm_8810"] = True
                    if "CLM-8814" not in data_str:
                        state["correctly_excluded_valid_clm_8814"] = True
                        
                    break # Stop after finding the first valid JSON file
                except (json.JSONDecodeError, UnicodeDecodeError):
                    continue
                    
    state_file = os.path.join(work_dir, "state.json")
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
