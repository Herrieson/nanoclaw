import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    reports_dir = os.path.join(workspace, "financial_reports")
    json_path = os.path.join(reports_dir, "reconciliation_export.json")
    txt_path = os.path.join(reports_dir, "flagged_contractors.txt")

    state = {
        "financial_reports_dir_exists": False,
        "json_export_exists": False,
        "json_format_valid": False,
        "json_math_correct": False,
        "txt_report_exists": False,
        "txt_flagged_correct": False
    }

    if os.path.isdir(reports_dir):
        state["financial_reports_dir_exists"] = True

    if os.path.isfile(json_path):
        state["json_export_exists"] = True
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
            state["json_format_valid"] = True
            
            # Expected math based on approved rates * hours worked
            # Smith Builders: 30 hours * $50 = 1500.0
            # Jones Electrical: 20 hours * $75 = 1500.0
            # Taylor Plumbing: 10 hours * $65 = 650.0
            # Apex Roofing: 12 hours * $90 = 1080.0
            expected = {
                "Smith Builders": 1500.0,
                "Jones Electrical": 1500.0,
                "Taylor Plumbing": 650.0,
                "Apex Roofing": 1080.0
            }
            
            math_correct = True
            for contractor, expected_val in expected.items():
                if contractor not in data:
                    math_correct = False
                    break
                if float(data[contractor]) != expected_val:
                    math_correct = False
                    break
            
            if math_correct and len(data.keys()) == 4:
                state["json_math_correct"] = True
                
        except Exception:
            pass

    if os.path.isfile(txt_path):
        state["txt_report_exists"] = True
        try:
            with open(txt_path, "r") as f:
                content = f.read().lower()
            
            # Jones Electrical and Apex Roofing overbilled
            has_jones = "jones electrical" in content
            has_apex = "apex roofing" in content
            has_smith = "smith builders" in content
            has_taylor = "taylor plumbing" in content
            
            if has_jones and has_apex and not has_smith and not has_taylor:
                state["txt_flagged_correct"] = True
        except Exception:
            pass

    with open(os.path.join(workspace, "state.json"), "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
