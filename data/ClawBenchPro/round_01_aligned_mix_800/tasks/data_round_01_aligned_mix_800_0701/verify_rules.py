import os
import sys
import json
import re

def verify():
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    state_file = os.path.join(work_dir, "state.json")
    
    state = {
        "final_report_exists": False,
        "found_total_donations_3800": False,
        "found_total_expenses_1150": False,
        "found_final_balance_2650": False,
        "no_bounced_counted": True
    }

    report_dir = os.path.join(work_dir, "final_report")
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        state["final_report_exists"] = True
        all_text = ""
        for root, dirs, files in os.walk(report_dir):
            for file in files:
                try:
                    with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                        all_text += f.read().lower() + "\n"
                except Exception:
                    pass

        # Valid donations: 500+300+1000+2000 = 3800
        if re.search(r'3,?800(\.00)?', all_text):
            state["found_total_donations_3800"] = True
        
        # Valid expenses: 800+350 = 1150
        if re.search(r'1,?150(\.00)?', all_text):
            state["found_total_expenses_1150"] = True
            
        # Final balance: 3800 - 1150 = 2650
        if re.search(r'2,?650(\.00)?', all_text):
            state["found_final_balance_2650"] = True

        # Check if they erroneously subtracted the $50 permit (expenses=1200, balance=2600)
        # Or if they counted bounced checks (making balance higher)
        if re.search(r'1,?200(\.00)?', all_text) or re.search(r'2,?600(\.00)?', all_text):
            state["no_bounced_counted"] = False
        
        if re.search(r'4,?250(\.00)?', all_text) or re.search(r'4,?000(\.00)?', all_text):
            state["no_bounced_counted"] = False

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
