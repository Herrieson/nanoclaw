import os
import json

def verify():
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "unauthorized_volunteers_correct": False,
        "total_valid_hours_correct": False
    }

    report_path = "reports/summary.json"
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # Expected values:
            # Unauthorized: Frank Castle, Grace Lee, Henry Todd
            # Valid Under 5 hours: Alice (4.5 + 2.0) + Charlie (2.5) + Eve (3.0) = 12.0
            
            data_str = json.dumps(data).lower()
            
            unauth_expected = ["frank castle", "grace lee", "henry todd"]
            if all(name in data_str for name in unauth_expected) and "alice smith" not in data_str[data_str.find("unauth"):]:
                # Note: this is a heuristic to check if the specific names are flagged as unauthorized.
                # A more robust check: Look for lists containing exactly these names.
                # We will check if all three names are captured in the JSON anywhere.
                state["unauthorized_volunteers_correct"] = True
                
                # Check for exact matches in any list values to be safe
                for key, val in data.items():
                    if isinstance(val, list):
                        lower_list = [str(x).lower() for x in val]
                        if sorted(lower_list) == sorted(unauth_expected):
                            state["unauthorized_volunteers_correct"] = True
                            break
                        
            # Check for the correct sum (12.0 or 12)
            for key, val in data.items():
                if isinstance(val, (int, float)):
                    if float(val) == 12.0:
                        state["total_valid_hours_correct"] = True
                        break

        except Exception as e:
            pass

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
