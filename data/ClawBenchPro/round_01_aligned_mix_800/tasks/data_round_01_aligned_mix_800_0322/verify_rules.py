import os
import json
import re

def verify():
    state = {
        "audit_folder_exists": False,
        "clean_attendance_exists": False,
        "unauthorized_exists": False,
        "valid_attendees_found": [],
        "unauthorized_found": [],
        "clean_format_is_csv": False
    }

    if os.path.isdir("audit_report"):
        state["audit_folder_exists"] = True
        
        # Check clean attendance
        clean_path = "audit_report/clean_attendance.csv"
        if os.path.isfile(clean_path):
            state["clean_attendance_exists"] = True
            try:
                with open(clean_path, "r") as f:
                    content = f.read()
                    # Check if it looks like a CSV (has commas and multiple lines)
                    if "," in content and len(content.splitlines()) >= 2:
                        state["clean_format_is_csv"] = True
                    
                    # Extract PA IDs to see who was included
                    found_ids = re.findall(r"PA-\d{3}", content)
                    state["valid_attendees_found"] = list(set(found_ids))
            except Exception:
                pass

        # Check unauthorized
        unauth_path = "audit_report/unauthorized.txt"
        if os.path.isfile(unauth_path):
            state["unauthorized_exists"] = True
            try:
                with open(unauth_path, "r") as f:
                    content = f.read()
                    found_ids = re.findall(r"PA-\d{3}", content)
                    state["unauthorized_found"] = list(set(found_ids))
            except Exception:
                pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
