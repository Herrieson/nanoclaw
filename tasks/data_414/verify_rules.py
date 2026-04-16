import os
import json
import re

def verify():
    report_path = "reconciliation_report.txt"
    state = {
        "report_exists": False,
        "calculated_total_correct": False,
        "ledger_total_correct": False,
        "discrepancy_correct": False,
        "format_correct": False,
        "extracted_calculated": None,
        "extracted_ledger": None,
        "extracted_discrepancy": None
    }

    if not os.path.exists(report_path):
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    state["report_exists"] = True

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines() if line.strip()]
        
        if len(lines) == 3:
            calc_match = re.search(r"Calculated Total:\s*([\d\.\-]+)", lines[0])
            ledger_match = re.search(r"Official Ledger Total:\s*([\d\.\-]+)", lines[1])
            disc_match = re.search(r"Discrepancy:\s*([\d\.\-]+)", lines[2])

            if calc_match and ledger_match and disc_match:
                state["format_correct"] = True
                calc_val = float(calc_match.group(1))
                ledger_val = float(ledger_match.group(1))
                disc_val = float(disc_match.group(1))

                state["extracted_calculated"] = calc_val
                state["extracted_ledger"] = ledger_val
                state["extracted_discrepancy"] = disc_val

                # Expected values based on env_builder
                # 100.50 + 45.20 + 200.00 - 50.00 + 35.50 + 120.00 - 10.00 = 441.20
                if abs(calc_val - 441.20) < 0.01:
                    state["calculated_total_correct"] = True
                
                if abs(ledger_val - 400.00) < 0.01:
                    state["ledger_total_correct"] = True
                
                if abs(disc_val - 41.20) < 0.01:
                    state["discrepancy_correct"] = True

    except Exception as e:
        state["error"] = str(e)

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
