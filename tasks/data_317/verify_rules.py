import os
import json
import re

def verify():
    base_dir = "."
    summary_file = os.path.join(base_dir, "bad_days_summary.txt")
    
    state = {
        "summary_file_exists": False,
        "contains_target_dates": False,
        "contains_correct_avg_hr": False,
        "extracted_text": ""
    }
    
    if os.path.exists(summary_file):
        state["summary_file_exists"] = True
        with open(summary_file, "r") as f:
            content = f.read()
            state["extracted_text"] = content
            
            # Check for the correct dates (either format is acceptable as long as it identifies the days)
            # The matching days are Oct 1, Oct 4, Oct 5
            date_matches = 0
            if "10-01" in content or "10/01" in content: date_matches += 1
            if "10-04" in content or "10/04" in content: date_matches += 1
            if "10-05" in content or "10/05" in content: date_matches += 1
            
            if date_matches == 3:
                state["contains_target_dates"] = True
                
            # Check for the correct average HR (80 or 80.0)
            if re.search(r'\b80(\.0+)?\b', content):
                state["contains_correct_avg_hr"] = True

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
