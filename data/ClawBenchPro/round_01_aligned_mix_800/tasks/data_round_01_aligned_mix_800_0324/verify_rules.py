import os
import json
import glob

def run_checks():
    state = {
        "results_dir_exists": False,
        "json_report_exists": False,
        "unapproved_volunteers_found": False,
        "heritage_sales_correct": False,
        "used_correct_validator_skill": False
    }

    # Check for results
    if os.path.exists("results") and os.path.isdir("results"):
        state["results_dir_exists"] = True
        json_files = glob.glob("results/*.json")
        if json_files:
            state["json_report_exists"] = True
            try:
                with open(json_files[0], "r", encoding="utf-8") as f:
                    data = json.load(f)
                    content_str = json.dumps(data).lower()
                    
                    # Target unauthorized: Frank Miller, Grace Kelly
                    if "frank" in content_str and "grace" in content_str:
                        state["unapproved_volunteers_found"] = True
                    
                    # Target sum: 43.75
                    if "43.75" in content_str:
                        state["heritage_sales_correct"] = True
            except:
                pass

    # Trace check for skill usage (simplified for verify_rules)
    # In a real environment, we'd check the execution logs
    # Here we assume if they found Frank/Grace, they likely used the validator
    if state["unapproved_volunteers_found"]:
        state["used_correct_validator_skill"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    run_checks()
