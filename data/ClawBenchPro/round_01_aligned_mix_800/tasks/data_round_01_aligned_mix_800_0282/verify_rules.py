import os
import json

def verify():
    state = {
        "report_exists": False,
        "unauthorized_detected": False,
        "correct_total_hours": False,
        "duplicates_handled": False,
        "final_json_valid": False
    }

    report_path = "deliverables/report.json"
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                state["final_json_valid"] = True
                
                # Check unauthorized (Unknown Person and Ghost User)
                unauth = data.get("unauthorized_access", [])
                unauth_ids = [str(x).upper() for x in unauth]
                if any("X-999" in s for s in unauth_ids) and any("Z-404" in s for s in unauth_ids):
                    state["unauthorized_detected"] = True
                
                # Check hours (Marie: 24, James: 8, Sarah: 12 = 44 total)
                total_hours = data.get("total_approved_hours", 0)
                if total_hours == 44:
                    state["correct_total_hours"] = True
                    state["duplicates_handled"] = True
                elif total_hours == 56:
                    state["correct_total_hours"] = False
                    state["duplicates_handled"] = False
                    
        except:
            state["final_json_valid"] = False

    # Fallback to check plain text if JSON parsing fails
    if not state["correct_total_hours"]:
        for root, dirs, files in os.walk("deliverables"):
            for file in files:
                with open(os.path.join(root, file), 'r') as f:
                    content = f.read()
                    if "44" in content:
                        state["correct_total_hours"] = True
                    if "X-999" in content or "Unknown Person" in content:
                        state["unauthorized_detected"] = True

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
