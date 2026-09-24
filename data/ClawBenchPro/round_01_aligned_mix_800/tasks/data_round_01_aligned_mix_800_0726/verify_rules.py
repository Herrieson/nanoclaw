import os
import json

def verify():
    report_path = "deliverables/audit_report.json"
    state = {
        "report_exists": False,
        "json_valid": False,
        "unauthorized_list_correct": False,
        "total_duration_correct": False,
        "anomalous_ids_correct": False
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
                state["json_valid"] = True
                
                # Verify unauthorized personnel (John Doe, Unknown)
                unauthorized = [name.lower() for name in data.get("unauthorized_volunteers", [])]
                if "john doe" in unauthorized and "unknown" in unauthorized and len(unauthorized) == 2:
                    state["unauthorized_list_correct"] = True
                
                # Verify total duration of authorized only (Sarah 45+50, Michael 30+20, Elena 40, David 25) = 210
                if data.get("total_authorized_minutes") == 210:
                    state["total_duration_correct"] = True
                
                # Verify anomalous BP ID (104)
                anomalies = data.get("anomalous_log_ids", [])
                if "104" in [str(i) for i in anomalies] and len(anomalies) == 1:
                    state["anomalous_ids_correct"] = True
                    
        except Exception:
            state["json_valid"] = False

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
