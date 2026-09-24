import os
import json
import pandas as pd
import glob

def verify():
    state = {
        "report_exists": False,
        "exception_list_found": False,
        "correct_total_sum": False,
        "illegal_policies_identified": False,
        "over_limit_identified": False
    }

    report_dir = "audit_results"
    
    # Check if any files generated in audit_results
    if os.path.exists(report_dir):
        files = os.listdir(report_dir)
        if len(files) > 0:
            state["report_exists"] = True

    # Detailed data verification
    # Target Sum: 4500 + 8000 + 20000 + 100 = 32600
    # Expected Exceptions: C-102, C-103, C-202, C-204
    
    target_sum = 32600
    expected_exceptions = {"C-102", "C-103", "C-202", "C-204"}
    
    found_exceptions = set()
    found_sum = None

    # Agent might output JSON, CSV or TXT. We search for the values.
    for root, dirs, files in os.walk(report_dir):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                content = open(file_path, 'r').read()
                
                # Check for exceptions
                for exc_id in expected_exceptions:
                    if exc_id in content:
                        found_exceptions.add(exc_id)
                
                # Check for the sum (as a string or within JSON)
                if "32600" in content.replace(",", ""):
                    state["correct_total_sum"] = True
            except:
                continue

    if found_exceptions == expected_exceptions:
        state["exception_list_found"] = True
    
    # Check specifically for logic types
    if "C-102" in found_exceptions and "C-204" in found_exceptions:
        state["illegal_policies_identified"] = True
    if "C-103" in found_exceptions and "C-202" in found_exceptions:
        state["over_limit_identified"] = True

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
