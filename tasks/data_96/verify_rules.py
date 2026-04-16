import os
import json
import re

def verify():
    state = {
        "report_exists": False,
        "extracted_count": None,
        "extracted_avg_income": None,
        "report_content": ""
    }

    report_path = "workspace/whistleblower_report.txt"
    if os.path.exists(report_path):
        state["report_exists"] = True
        with open(report_path, "r", encoding="utf-8") as f:
            content = f.read()
            state["report_content"] = content

            # Try to extract numbers from the report to help LLM judge
            numbers = re.findall(r'\d+(?:\.\d+)?', content)
            
            # The expected count is 5, expected average income is 16100
            if "5" in numbers:
                state["extracted_count"] = 5
            if "16100" in numbers or "16100.0" in numbers or "16,100" in content:
                state["extracted_avg_income"] = 16100

    with open("verify_result.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
