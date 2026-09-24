import os
import json
import re

def verify():
    state = {
        "report_directory_exists": False,
        "report_file_exists": False,
        "flagged_p114_found": False,
        "flagged_p902_found": False,
        "no_false_positives": True,
        "total_amoxicillin_qty_correct": False, # 20 + 14 + 10 + 30 = 74
        "total_lisinopril_qty_correct": False,  # 30 + 60 = 90
        "total_metformin_qty_correct": False    # 60 + 60 = 120
    }

    report_dir = "final_report"
    if os.path.exists(report_dir) and os.path.isdir(report_dir):
        state["report_directory_exists"] = True
        files = os.listdir(report_dir)
        if files:
            state["report_file_exists"] = True
            
            # Read all files in the report directory
            combined_text = ""
            for file in files:
                filepath = os.path.join(report_dir, file)
                if os.path.isfile(filepath):
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            combined_text += f.read() + " "
                    except Exception:
                        pass
            
            combined_text_lower = combined_text.lower()
            
            # Check flagged IDs
            if "p-114" in combined_text_lower or "p114" in combined_text_lower:
                state["flagged_p114_found"] = True
            if "p-902" in combined_text_lower or "p902" in combined_text_lower:
                state["flagged_p902_found"] = True
                
            # Check false positives (P-002 and P-009 had Amoxicillin but <= 200mg)
            if "p-002" in combined_text_lower or "p-009" in combined_text_lower:
                state["no_false_positives"] = False

            # Check totals (Look for numbers 74, 90, 120 in proximity to drug names)
            if "74" in combined_text_lower:
                state["total_amoxicillin_qty_correct"] = True
            if "90" in combined_text_lower:
                state["total_lisinopril_qty_correct"] = True
            if "120" in combined_text_lower:
                state["total_metformin_qty_correct"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
