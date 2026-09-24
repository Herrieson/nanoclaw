import os
import json
import sys
import glob

def verify():
    # Expected answers:
    # TechNova: (40 + 10) * 150 = 50 * 150 = 7500
    # ByteSynergy: 15 * 200 = 3000
    # CloudArchitects: 20 * 180 = 3600
    # Total Authorized = 7500 + 3000 + 3600 = 14100
    # Unauthorized: RogueIT Contractors, ShadowCoders
    
    state = {
        "deliverables_dir_created": False,
        "summary_file_exists": False,
        "valid_json_format": False,
        "correct_total_cost_found": False,
        "unauthorized_vendors_identified": False
    }

    if os.path.isdir("deliverables"):
        state["deliverables_dir_created"] = True
        
        # Find any JSON file in deliverables
        json_files = glob.glob("deliverables/*.json")
        if json_files:
            state["summary_file_exists"] = True
            try:
                with open(json_files[0], 'r', encoding='utf-8') as f:
                    data = json.load(f)
                state["valid_json_format"] = True
                
                # Convert entire JSON to string to lazily search for values
                # regardless of the schema the Agent decided to use.
                data_str = json.dumps(data).lower()
                
                if "14100" in data_str:
                    state["correct_total_cost_found"] = True
                    
                if "rogueit contractors" in data_str and "shadowcoders" in data_str:
                    state["unauthorized_vendors_identified"] = True
                    
            except Exception:
                pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
