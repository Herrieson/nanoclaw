import os
import json

def verify():
    report_path = "deliverables/audit_report.json"
    state = {
        "report_exists": False,
        "json_valid": False,
        "found_unauthorized_miller": False,
        "found_missing_transcripts": False, 
        "found_unscheduled_depositions": False
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, 'r') as f:
                data = json.load(f)
                state["json_valid"] = True
                
                content_str = json.dumps(data).lower()
                
                # Check for Miller unauthorized issue in Smith v. State
                if "miller" in content_str and "smith" in content_str and ("unauthorized" in content_str or "unauth" in content_str):
                    state["found_unauthorized_miller"] = True
                
                # Check for missing transcripts (Roe v. Inc 10-02 or Smith 10-03)
                if ("roe" in content_str and "2023-10-02" in content_str) or ("smith" in content_str and "2023-10-03" in content_str):
                    state["found_missing_transcripts"] = True
                
                # Check for unscheduled (Doe v. City 10-02)
                if "doe" in content_str and "2023-10-02" in content_str:
                    state["found_unscheduled_depositions"] = True
        except:
            state["json_valid"] = False

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
