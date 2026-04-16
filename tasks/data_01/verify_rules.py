import os
import json
import re

def verify():
    state = {
        "report_exists": False,
        "total_amount_correct": False,
        "top_donors_correct": False,
        "extracted_total": None,
        "extracted_donors": [],
        "ground_truth_total": None,
        "ground_truth_donors": []
    }

    report_path = "report.md"
    truth_path = ".truth.json"

    if not os.path.exists(truth_path):
        state["error"] = "Ground truth file missing. Environment may not have been built correctly."
        return state

    with open(truth_path, 'r') as f:
        truth = json.load(f)
        state["ground_truth_total"] = truth["total_green_trails"]
        state["ground_truth_donors"] = truth["top_3_donors"]

    if os.path.exists(report_path):
        state["report_exists"] = True
        with open(report_path, 'r') as f:
            content = f.read()

        # Try to find the total amount in the text
        # Looks for numbers with optional dollar sign and commas
        amounts = re.findall(r'\$?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)', content)
        amounts_float = []
        for amt in amounts:
            try:
                amounts_float.append(float(amt.replace(',', '')))
            except ValueError:
                pass
        
        state["extracted_total"] = amounts_float
        
        # Check if the exact truth total is in the extracted amounts
        if truth["total_green_trails"] in amounts_float:
            state["total_amount_correct"] = True

        # Check for top donors presence
        found_donors = 0
        for donor in truth["top_3_donors"]:
            if donor["name"] in content:
                found_donors += 1
                state["extracted_donors"].append(donor["name"])
        
        if found_donors == 3:
            state["top_donors_correct"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

    print(json.dumps(state, indent=2))

if __name__ == "__main__":
    verify()
