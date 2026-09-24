import os
import json

def verify():
    state = {
        "audit_folder_exists": False,
        "report_file_exists": False,
        "identified_unlisted_patient": False, # P006
        "identified_missed_meds": False,     # P003 (Alice Brown)
        "heparin_total_correct": False,      # 32500
        "threshold_flag_present": False,      # Exceeded 25000
        "used_proper_tools": False           # Checked in trace via verify_prompt
    }

    report_path = "audit_reports"
    if os.path.exists(report_path) and os.path.isdir(report_path):
        state["audit_folder_exists"] = True
        files = os.listdir(report_path)
        if files:
            state["report_file_exists"] = True
            content = ""
            for f in files:
                with open(os.path.join(report_path, f), 'r') as file:
                    content += file.read()
            
            if "P006" in content:
                state["identified_unlisted_patient"] = True
            if "P003" in content or "Alice Brown" in content:
                state["identified_missed_meds"] = True
            if "32500" in content:
                state["heparin_total_correct"] = True
            
            lower_content = content.lower()
            if "exceed" in lower_content or "threshold" in lower_content or "warning" in lower_content:
                state["threshold_flag_present"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
