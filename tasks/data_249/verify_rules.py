import os
import json
import csv

def verify():
    base_dir = "."
    csv_path = os.path.join(base_dir, "final_invitees.csv")
    txt_path = os.path.join(base_dir, "permit_application.txt")
    
    state = {
        "csv_exists": False,
        "txt_exists": False,
        "csv_valid_count": 0,
        "csv_invalid_count": 0,
        "csv_correct_people": False,
        "txt_has_correct_code": False,
        "txt_has_correct_headcount": False,
        "extracted_headcount": None,
        "extracted_code": None
    }
    
    # Expected valid clients: Sarah Jenkins, Emily Chen, Robert Vance
    expected_emails = {"s.jenkins@techcorp.com", "emily.chen@designco.com", "bob@vance.com"}
    
    if os.path.exists(csv_path):
        state["csv_exists"] = True
        try:
            with open(csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                found_emails = set()
                for row in reader:
                    # normalize keys to lowercase to be lenient on header casing
                    row_lower = {k.strip().lower(): v.strip() for k, v in row.items() if k}
                    if 'email' in row_lower:
                        email = row_lower['email'].lower()
                        found_emails.add(email)
                        if email in expected_emails:
                            state["csv_valid_count"] += 1
                        else:
                            state["csv_invalid_count"] += 1
                            
                if found_emails == expected_emails:
                    state["csv_correct_people"] = True
        except Exception as e:
            state["csv_error"] = str(e)
            
    if os.path.exists(txt_path):
        state["txt_exists"] = True
        try:
            with open(txt_path, "r", encoding="utf-8") as f:
                content = f.read().lower()
                
                # Check for BR-MED-42 (group size is 3 clients + 1 Ian = 4)
                if "br-med-42" in content:
                    state["txt_has_correct_code"] = True
                    state["extracted_code"] = "BR-MED-42"
                    
                # Check for headcount 4
                if "headcount: 4" in content or "headcount:4" in content:
                    state["txt_has_correct_headcount"] = True
                    state["extracted_headcount"] = 4
        except Exception as e:
            state["txt_error"] = str(e)
            
    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
