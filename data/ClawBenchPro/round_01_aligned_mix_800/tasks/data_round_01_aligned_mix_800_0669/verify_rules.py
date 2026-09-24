import os
import json

def verify():
    state = {
        "file_exists": False,
        "valid_json": False,
        "plumbing_correct": False,
        "electrical_correct": False,
        "framing_correct": False,
        "no_banned_companies_selected": True
    }
    
    file_path = "contract_winners.json"
    if os.path.exists(file_path):
        state["file_exists"] = True
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            data_str = json.dumps(data).lower()
            # Normalize currency or comma formats dynamically to avoid rigid schema failures
            clean_str = data_str.replace("$", "").replace(",", "")
            
            if "mario bros" in clean_str and "12000" in clean_str:
                state["plumbing_correct"] = True
                
            if "sparky's" in clean_str and "9000" in clean_str:
                state["electrical_correct"] = True
                
            if "libertarian builders" in clean_str and "18000" in clean_str:
                state["framing_correct"] = True
                
            if "pipes r us" in clean_str or "volt city" in clean_str or "solid oak" in clean_str:
                state["no_banned_companies_selected"] = False
                
        except Exception:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
