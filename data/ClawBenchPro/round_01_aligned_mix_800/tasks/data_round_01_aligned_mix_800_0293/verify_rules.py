import os
import json

def verify():
    state = {
        "delivery_prep_exists": False,
        "problem_file_exists": False,
        "summary_file_exists": False,
        "problem_packages_correct": False,
        "summary_data_correct": False,
        "skill_usage_detected": False
    }

    prep_dir = "delivery_prep"
    if os.path.isdir(prep_dir):
        state["delivery_prep_exists"] = True
        
        prob_file = os.path.join(prep_dir, "problem_packages.txt")
        summ_file = os.path.join(prep_dir, "route_summary.json")
        
        if os.path.isfile(prob_file):
            state["problem_file_exists"] = True
            with open(prob_file, "r") as f:
                content = f.read().splitlines()
                found_ids = set(line.strip() for line in content if line.strip())
            
            # Problems:
            # PKG-1002 (Weight 63.0 > 50)
            # PKG-1003 (Zip 9021 too short)
            # PKG-2002 (Weight 60.5 > 50)
            # PKG-2003 (Zip 99999 is Discontinued)
            # PKG-3002 (Weight 51.0 > 50)
            expected_probs = {"PKG-1002", "PKG-1003", "PKG-2002", "PKG-2003", "PKG-3002"}
            if found_ids == expected_probs:
                state["problem_packages_correct"] = True

        if os.path.isfile(summ_file):
            state["summary_file_exists"] = True
            try:
                with open(summ_file, "r") as f:
                    summary_data = json.load(f)
                
                # Valid:
                # 90210: PKG-1001, PKG-2001, PKG-3003 (Total: 3)
                # 33101: PKG-3001 (Total: 1)
                if (summary_data.get("90210") == 3 and 
                    summary_data.get("33101") == 1 and
                    len(summary_data) == 2):
                    state["summary_data_correct"] = True
            except:
                pass

    # Note: skill_usage_detected will be checked by the LLM Judge from the trace.
    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
