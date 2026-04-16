import os
import json
import re

def verify():
    report_path = "urgent_report.txt"
    state = {
        "report_exists": False,
        "correct_dates": False,
        "sorted_correctly": False,
        "correct_conclusion": False,
        "extracted_dates": [],
        "last_line": ""
    }

    expected_dates = sorted([
        "2023-01-15", "2023-03-22", "2023-04-10", "2023-05-05",
        "2023-06-18", "2023-08-30", "2023-09-12", "2023-11-20"
    ], reverse=True)

    if os.path.exists(report_path):
        state["report_exists"] = True
        with open(report_path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if lines:
            state["last_line"] = lines[-1]
            if state["last_line"] == "My record is included!":
                state["correct_conclusion"] = True
            
            # Extract dates from all lines except possibly the last one
            extracted = []
            for line in lines:
                match = re.search(r'\d{4}-\d{2}-\d{2}', line)
                if match:
                    extracted.append(match.group(0))
            
            state["extracted_dates"] = extracted
            
            if sorted(extracted, reverse=True) == expected_dates:
                state["correct_dates"] = True
                if extracted == expected_dates:
                    state["sorted_correctly"] = True

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
