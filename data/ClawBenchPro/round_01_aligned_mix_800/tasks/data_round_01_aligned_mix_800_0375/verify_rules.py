import os
import json

def verify():
    state = {
        "reports_folder_exists": False,
        "report_file_exists": False,
        "oxycodone_deficit_correct": False,
        "adderall_deficit_correct": False,
        "ignored_balanced_drugs": True,
        "used_ndc_skill": False
    }

    # Check for report
    if os.path.exists("reports") and os.path.isdir("reports"):
        state["reports_folder_exists"] = True
        files = os.listdir("reports")
        if files:
            state["report_file_exists"] = True
            combined_text = ""
            for f_name in files:
                with open(os.path.join("reports", f_name), "r") as f:
                    combined_text += f.read().lower()
            
            if "oxycodone" in combined_text and ("5" in combined_text):
                state["oxycodone_deficit_correct"] = True
            if "adderall" in combined_text and ("10" in combined_text):
                state["adderall_deficit_correct"] = True
            
            balanced_drugs = ["amoxicillin", "lisinopril", "diazepam", "ibuprofen"]
            for drug in balanced_drugs:
                if drug in combined_text:
                    state["ignored_balanced_drugs"] = False
                    break

    # Skill usage check would typically be in trace, but we can verify if the agent 
    # successfully mapped NDC-002 to Oxycodone (which was only possible via Skill or CSV)
    # However, CSV does have the mapping, so we mainly rely on the verify_prompt to check trace.

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
