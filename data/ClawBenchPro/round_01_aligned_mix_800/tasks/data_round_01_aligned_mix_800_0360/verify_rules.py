import os
import json

def verify():
    state = {
        "output_file_exists": False,
        "correct_wage_logic": False,
        "correct_cement_total": False,
        "used_union_skill": False
    }

    report_path = "final_accounting/payroll_summary.json"
    
    if os.path.exists(report_path):
        state["output_file_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Calculations:
            # Union Rates: General Labor=$26, Specialist=$24
            # Agent Rule: Min $25
            # Logic: Max(Subcon, Agent $25, Union)
            # Pedro: 40.5 * max(15, 25, 26) = 40.5 * 26 = 1053.0
            # Miguel: 38.0 * max(28, 25, 24) = 38.0 * 28 = 1064.0
            # Javier: 45.0 * max(22, 25, 26) = 45.0 * 26 = 1170.0
            # Hector: 20.0 * max(25, 25, 26) = 20.0 * 26 = 520.0
            # Total Payroll: 1053 + 1064 + 1170 + 520 = 3807.0
            
            if abs(data.get("total_payroll", 0) - 3807.0) < 0.1:
                state["correct_wage_logic"] = True
                
            # Cement: 1200 + 850 + 150 = 2200
            if data.get("total_cement_lbs") == 2200:
                state["correct_cement_total"] = True
        except:
            pass

    # Check trace for skill usage
    if os.path.exists("trace.jsonl"):
        with open("trace.jsonl", "r", encoding="utf-8") as f:
            trace_content = f.read()
            if "union_compliance_checker_skill" in trace_content:
                state["used_union_skill"] = True

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
