import os
import json

def verify():
    state = {
        "report_file_exists": False,
        "is_valid_json": False,
        "has_correct_total_cost": False,
        "has_mary_johnson": False,
        "has_alice_vance": False,
        "used_valuation_skill": False,
        "no_false_positives": True
    }

    report_path = "overdue_antiques_report.json"
    
    # Check if report exists
    if os.path.exists(report_path):
        state["report_file_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            raw_content = json.dumps(data).lower()
            
            # Target Data:
            # B-101: Mary Johnson, Due 2023-09-12 (Overdue), Value: 850
            # B-103: Alice Vance, Due 2023-08-30 (Overdue), Value: 1200
            # Total: 2050
            # B-102: Bobby Tables, Due 2023-10-15 (NOT Overdue)
            
            if "2050" in raw_content:
                state["has_correct_total_cost"] = True
            if "mary johnson" in raw_content:
                state["has_mary_johnson"] = True
            if "alice vance" in raw_content:
                state["has_alice_vance"] = True
            
            if "bobby tables" in raw_content or "timmy smith" in raw_content:
                state["no_false_positives"] = False
        except:
            pass

    # Check trace for skill usage (Self-check via looking at command history if possible, 
    # but here we rely on the verify_prompt to judge the trace)
    
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
