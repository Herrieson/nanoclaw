import os
import json
import re

def verify():
    state = {
        "delivery_prep_exists": False,
        "problem_file_exists": False,
        "summary_file_exists": False,
        "problem_packages_correct": False,
        "summary_json_valid": False,
        "summary_data_correct": False
    }

    prep_dir = "delivery_prep"
    if os.path.isdir(prep_dir):
        state["delivery_prep_exists"] = True
        
        prob_file = os.path.join(prep_dir, "problem_packages.txt")
        summ_file = os.path.join(prep_dir, "route_summary.json")
        
        if os.path.isfile(prob_file):
            state["problem_file_exists"] = True
            with open(prob_file, "r") as f:
                content = f.read()
                
            # Expected problems: 
            # PKG-1002 (>50), PKG-1003 (bad zip), PKG-2002 (>50), PKG-2004 (bad zip), PKG-3002 (>50)
            expected_probs = {"PKG-1002", "PKG-1003", "PKG-2002", "PKG-2004", "PKG-3002"}
            # Valid ones that should NOT be here: PKG-1001, PKG-1004, PKG-2001, PKG-2003, PKG-3001, PKG-3003
            unexpected_probs = {"PKG-1001", "PKG-1004", "PKG-2001", "PKG-2003", "PKG-3001", "PKG-3003"}
            
            found_all = all(p in content for p in expected_probs)
            found_none = all(p not in content for p in unexpected_probs)
            
            if found_all and found_none:
                state["problem_packages_correct"] = True

        if os.path.isfile(summ_file):
            state["summary_file_exists"] = True
            try:
                with open(summ_file, "r") as f:
                    summary_data = json.load(f)
                state["summary_json_valid"] = True
                
                # Expected valid tally:
                # 90210: PKG-1001, PKG-2001, PKG-3003 -> 3
                # 90001: PKG-1004, PKG-2003 -> 2
                # 33101: PKG-3001 -> 1
                if (summary_data.get("90210") == 3 and 
                    summary_data.get("90001") == 2 and 
                    summary_data.get("33101") == 1):
                    state["summary_data_correct"] = True
            except:
                pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
