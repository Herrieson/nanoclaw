import os
import json

def verify():
    state = {
        "audit_folder_exists": False,
        "interlopers_found_correctly": False,
        "emergency_fund_correct": False,
        "summary_report_exists": False,
        "used_ocr_skill": False,
        "used_insurance_skill": False
    }
    
    # Trace check for skill usage
    if os.path.exists("trace.jsonl"):
        with open("trace.jsonl", "r") as f:
            trace = f.read()
            if "handwritten_form_ocr_skill" in trace:
                state["used_ocr_skill"] = True
            if "insurance_premium_validator_skill" in trace:
                state["used_insurance_skill"] = True

    audit_dir = "final_audit"
    if os.path.exists(audit_dir):
        state["audit_folder_exists"] = True
        
        # Check Interlopers: Zoe Saldana (Batch 1), Jack Sparrow (OCR Batch 2)
        interlopers_file = next((f for f in os.listdir(audit_dir) if "interloper" in f.lower()), None)
        if interlopers_file:
            with open(os.path.join(audit_dir, interlopers_file), 'r') as f:
                content = f.read()
                if "Zoe Saldana" in content and "Jack Sparrow" in content:
                    state["interlopers_found_correctly"] = True
        
        # Check Summary
        summary_file = next((f for f in os.listdir(audit_dir) if "summary" in f.lower() or "report" in f.lower()), None)
        if summary_file:
            state["summary_report_exists"] = True
            with open(os.path.join(audit_dir, summary_file), 'r') as f:
                content = f.read()
                # 190 is the expected sum based on the insurance skill logic
                if "190" in content:
                    state["emergency_fund_correct"] = True

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
