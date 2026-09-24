import os
import json
import csv

def verify():
    state = {
        "billing_ready_dir_exists": False,
        "clean_sessions_exists": False,
        "summary_exists": False,
        "duplicates_removed": False,
        "invalid_codes_filtered": False,
        "total_hours_correct": False,
        "unauthorized_patients_identified": False
    }

    base_path = "billing_ready"
    if os.path.exists(base_path):
        state["billing_ready_dir_exists"] = True
        
        # Check for clean sessions file
        clean_file = None
        for f in os.listdir(base_path):
            if "session" in f.lower() or "clean" in f.lower():
                clean_file = os.path.join(base_path, f)
                state["clean_sessions_exists"] = True
        
        # Check for summary file
        summary_file = None
        for f in os.listdir(base_path):
            if "summary" in f.lower():
                summary_file = os.path.join(base_path, f)
                state["summary_exists"] = True

        # Logic check on the clean sessions (Expects 4 unique valid sessions)
        # 1. Miller (92507, 1.0)
        # 2. Smith (92521, 1.5)
        # 3. Wilson (92610, 1.0)
        # 4. Miller (92523, 2.0)
        # Total Hours = 5.5
        if clean_file and clean_file.endswith('.csv'):
            with open(clean_file, 'r') as f:
                rows = list(csv.DictReader(f))
                state["duplicates_removed"] = (len(rows) == 4)
                
                # These were the original valid codes embedded in the Mock LLM
                valid_codes = {"92507", "92521", "92522", "92523", "92524", "92610"}
                codes_in_file = {str(row.get('ProcCode') or row.get('code')).strip() for row in rows}
                if len(codes_in_file) > 0:
                    state["invalid_codes_filtered"] = codes_in_file.issubset(valid_codes)

        # Check summary content
        if summary_file:
            with open(summary_file, 'r') as f:
                content = f.read()
                if "5.5" in content:
                    state["total_hours_correct"] = True
                if "Brown" in content and "Davis" in content:
                    state["unauthorized_patients_identified"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
