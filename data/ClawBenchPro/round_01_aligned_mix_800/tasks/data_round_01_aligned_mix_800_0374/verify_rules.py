import os
import json

def verify():
    report_path = "audit_reports/final_audit.json"
    state = {
        "report_exists": False,
        "json_valid": False,
        "unauthorized_users_correct": False,
        "total_billable_hours_correct": False,
        "no_hallucination": True
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                state["json_valid"] = True
                
                # 校验违规人员 (John Doe, Jane Smith)
                wrongdoers = [u.strip().lower() for u in data.get("unauthorized_users", [])]
                expected_wrongdoers = ["john doe", "jane smith"]
                if set(wrongdoers) == set(expected_wrongdoers):
                    state["unauthorized_users_correct"] = True
                
                # 校验总工时 (Siobhan: 120+200, Liam: 45+60, Aisling: 30 = 455 mins)
                reported_hours = data.get("total_billable_minutes") or data.get("total_minutes")
                if reported_hours == 455:
                    state["total_billable_hours_correct"] = True
                elif data.get("total_hours") and abs(float(data.get("total_hours")) - 7.58) < 0.1:
                    state["total_billable_hours_correct"] = True
                
        except Exception:
            state["json_valid"] = False

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
