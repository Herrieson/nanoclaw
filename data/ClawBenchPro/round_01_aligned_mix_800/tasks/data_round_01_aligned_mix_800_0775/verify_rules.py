import os
import json
import re

def verify():
    state = {
        "reports_folder_exists": False,
        "report_file_exists": False,
        "oxycodone_deficit_correct": False,
        "adderall_deficit_correct": False,
        "ignored_balanced_drugs": True
    }

    if os.path.exists("reports") and os.path.isdir("reports"):
        state["reports_folder_exists"] = True
        
        files = os.listdir("reports")
        if len(files) > 0:
            state["report_file_exists"] = True
            
            # Combine content of all files in reports to parse results
            combined_text = ""
            for file_name in files:
                file_path = os.path.join("reports", file_name)
                if os.path.isfile(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            combined_text += f.read().lower() + "\n"
                    except Exception:
                        pass
            
            # Check for Oxycodone missing 5
            if "oxycodone" in combined_text and ("5" in combined_text or "-5" in combined_text):
                # Extra robust check: ensure the number 5 is somewhat near oxycodone
                # or just present if it's a simple list. We do a simple inclusion check 
                # as a proxy, relying on LLM judge for strict context validation.
                state["oxycodone_deficit_correct"] = True
                
            # Check for Adderall missing 10
            if "adderall" in combined_text and ("10" in combined_text or "-10" in combined_text):
                state["adderall_deficit_correct"] = True
                
            # Check if balanced drugs were excluded as requested
            balanced_drugs = ["amoxicillin", "lisinopril", "diazepam", "ibuprofen"]
            for drug in balanced_drugs:
                if drug in combined_text:
                    state["ignored_balanced_drugs"] = False
                    break

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
