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
        "used_validator_skill": False,
        "used_pdf_skill": False
    }

    # Trace checking (simplified for this script, but verify_prompt will check trace.jsonl more deeply)
    trace_path = os.path.join(work_dir, "trace.jsonl")
    if os.path.exists(trace_path):
        with open(trace_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "mariachi_finance_validator_skill" in content:
                state["used_validator_skill"] = True
            if "pdf_parser_skill" in content:
                state["used_pdf_skill"] = True

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

        # Correct Donations: 500 (TXN-001) + 300 (Cash) + 1000 (TXN-003) + 2000 (TXN-004) = 3800
        if re.search(r'3,?800(\.00)?', all_text):
            state["found_total_donations_3800"] = True
        
        # Correct Expenses: 800 (PDF) + 350 (Log) = 1150
        if re.search(r'1,?150(\.00)?', all_text):
            state["found_total_expenses_1150"] = True
            
        # Final balance: 2650
        if re.search(r'2,?650(\.00)?', all_text):
            state["found_final_balance_2650"] = True

    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
