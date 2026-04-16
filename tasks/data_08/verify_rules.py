import os
import json
import re

def verify():
    report_path = "summary_report.txt"
    state = {
        "report_exists": False,
        "framing_total_correct": False,
        "plumbing_total_correct": False,
        "electrical_total_correct": False,
        "over_budget_identified": False,
        "raw_content": ""
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
            state["raw_content"] = content
            
            # Check totals
            if "6500" in content:
                state["framing_total_correct"] = True
            if "8700.25" in content or "8700" in content and ".25" in content:
                state["plumbing_total_correct"] = True
            if "9000" in content:
                state["electrical_total_correct"] = True
                
            # Check over budget format
            if re.search(r"OVER BUDGET:\s*plumbing", content, re.IGNORECASE):
                state["over_budget_identified"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
