import os
import json
import sys

def verify():
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "alice_correct": False,
        "bob_correct": False,
        "charlie_correct": False,
        "david_correct": False,
        "eve_correct": False,
        "frank_correct": False,
        "intervention_list_correct": False
    }
    
    report_path = "reports/intervention_summary.json"
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                content = json.load(f)
            state["is_valid_json"] = True
            
            content_str = json.dumps(content).lower()
            
            # Check for correct mapping and calculation
            if "110" in content_str and "alice" in content_str:
                state["alice_correct"] = True
            if "50" in content_str and "bob" in content_str:
                state["bob_correct"] = True
            if "120" in content_str and "charlie" in content_str:
                state["charlie_correct"] = True
            if "75" in content_str and "david" in content_str:
                state["david_correct"] = True
            if "105" in content_str and "eve" in content_str:
                state["eve_correct"] = True
            if "90" in content_str and "frank" in content_str:
                state["frank_correct"] = True
                
            # Below 100: Bob (50), David (75), Frank (90)
            for key, val in content.items():
                if isinstance(val, list):
                    lower_list = [str(x).lower() for x in val]
                    if "bob" in lower_list and "david" in lower_list and "frank" in lower_list:
                        if "alice" not in lower_list and "charlie" not in lower_list and "eve" not in lower_list:
                            state["intervention_list_correct"] = True
                            break
                            
        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
