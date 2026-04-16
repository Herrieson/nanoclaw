import os
import json
import re

def verify():
    base_dir = "."
    exhibit_path = os.path.join(base_dir, "Exhibit_A.md")
    state = {
        "exhibit_exists": False,
        "found_mismatches": [],
        "table_formatted": False
    }

    if os.path.exists(exhibit_path):
        state["exhibit_exists"] = True
        with open(exhibit_path, "r") as f:
            content = f.read()
        
        # Check for expected mismatched invoices
        expected_mismatches = ["INV-002", "INV-004", "INV-007", "INV-009"]
        found = []
        for inv in expected_mismatches:
            if inv in content:
                found.append(inv)
        state["found_mismatches"] = found

        # Minimal check to see if it looks like a markdown table
        if "|" in content and "-|-" in content.replace(" ", ""):
            state["table_formatted"] = True

    with open("verify_result.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
