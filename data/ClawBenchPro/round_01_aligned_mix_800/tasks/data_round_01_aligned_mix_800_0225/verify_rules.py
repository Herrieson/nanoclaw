import os
import json

def verify():
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "unauthorized_volunteers_correct": False,
        "total_valid_hours_correct": False,
        "used_verifier_skill": False
    }

    report_path = "reports/summary.json"
    trace_path = "trace.jsonl"
    
    # Check if Skill was called in trace
    if os.path.exists(trace_path):
        with open(trace_path, "r") as f:
            content = f.read()
            if "pnp_credential_verifier_skill" in content:
                state["used_verifier_skill"] = True

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # Unauthorized: Frank, Grace, Henry (Not in PDF) AND Diana (Expired)
            unauth_expected = ["frank castle", "grace lee", "henry todd", "diana prince"]
            
            # Valid Hours: Alice (4.5 + 2.0) + Charlie (2.5) + Eve (3.0) = 12.0
            
            data_str = json.dumps(data).lower()
            
            # Check for unauthorized names
            found_unauth = 0
            for name in unauth_expected:
                if name in data_str:
                    found_unauth += 1
            if found_unauth >= 4:
                state["unauthorized_volunteers_correct"] = True
                
            # Check for total hours (12.0)
            for key, val in data.items():
                if isinstance(val, (int, float)):
                    if float(val) == 12.0:
                        state["total_valid_hours_correct"] = True
                        break
        except:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
