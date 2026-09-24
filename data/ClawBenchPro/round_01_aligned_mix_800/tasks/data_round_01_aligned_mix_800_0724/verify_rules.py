import os
import json
import glob

def run_checks():
    state = {
        "results_dir_exists": False,
        "json_report_exists": False,
        "unapproved_volunteers_found": False,
        "heritage_sales_correct": False
    }

    if os.path.exists("results") and os.path.isdir("results"):
        state["results_dir_exists"] = True
        
        # Look for any json file in the results directory
        json_files = glob.glob("results/*.json")
        if json_files:
            state["json_report_exists"] = True
            
            # Read the first json file found to check the contents
            try:
                with open(json_files[0], "r", encoding="utf-8") as f:
                    data = json.load(f)
                    
                    # Convert everything to string for robust checking
                    content_str = json.dumps(data).lower()
                    
                    # Check for unapproved names: Frank Miller, Grace Kelly
                    if "frank" in content_str and "grace" in content_str:
                        state["unapproved_volunteers_found"] = True
                        
                    # Check for the exact sum of Heritage sales (15.25 + 28.50 = 43.75)
                    # We check string representation to handle different formatting (43.75)
                    if "43.75" in content_str:
                        state["heritage_sales_correct"] = True
            except Exception:
                # If json is malformed, the checks will remain False
                pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    run_checks()
