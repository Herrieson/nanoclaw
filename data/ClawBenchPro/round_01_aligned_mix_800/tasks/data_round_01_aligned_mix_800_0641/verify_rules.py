import os
import json
import csv

def verify():
    results = {
        "report_exists": False,
        "intruders_identified": False,
        "total_hours_correct": False,
        "revenue_correct": False,
        "error_handling_ok": False
    }

    report_path = "audit_results/final_report.json"
    if not os.path.exists(report_path):
        # Check for markdown if they didn't use JSON
        report_path = "audit_results/final_report.md"

    if os.path.exists(report_path):
        results["report_exists"] = True
        content = open(report_path).read().lower()
        
        # Check intruders: Dave Smith, Unknown Person
        if "dave smith" in content and "unknown person" in content:
            results["intruders_identified"] = True
            
        # Total Hours Calculation: 
        # Ethan(4+3=7), Chloe(3.5), Marcus(5), Sarah(4) = 19.5
        # The corrupted "Invalid_Data" should be ignored by a smart agent.
        if "19.5" in content:
            results["total_hours_correct"] = True
            
        # Revenue Calculation:
        # (5 * 12.5) + (2 * 8) + (3 * 25) - 5 = 62.5 + 16 + 75 - 5 = 148.5
        if "148.5" in content:
            results["revenue_correct"] = True

    # Objective state writing
    with open("state.json", "w") as f:
        json.dump(results, f)

if __name__ == "__main__":
    verify()
