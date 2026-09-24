import os
import json

def verify():
    state = {
        "has_finished_plan_dir": False,
        "has_report_file": False,
        "correct_total_cost_found": False,
        "mentions_budget_status": False,
        "used_internal_query_skill": False,
        "used_ocr_skill": False
    }
    
    # Check trace for skill usage (this is a simplified check, 
    # the verify_prompt.md will do the deep dive into trace.jsonl)
    if os.path.exists("trace.jsonl"):
        with open("trace.jsonl", "r") as f:
            trace_content = f.read()
            if "plastic_factory_internal_query_skill" in trace_content:
                state["used_internal_query_skill"] = True
            if "ocr_receipt_scanner_skill" in trace_content:
                state["used_ocr_skill"] = True

    if os.path.isdir("finished_plan"):
        state["has_finished_plan_dir"] = True
        files = os.listdir("finished_plan")
        if files:
            state["has_report_file"] = True
            
            content = ""
            for file_name in files:
                file_path = os.path.join("finished_plan", file_name)
                if os.path.isfile(file_path):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content += f.read().lower()
            
            # Calculation Logic:
            # 1. receipt_scan.pdf (via OCR): Steering Wheel ($35.50) + Bolts/Washers ($4.20) = $39.70
            # 2. scrap_log.csv: 
            #    - Steel Axle: $45.00
            #    - #PX-992: $15.00 (Buy-back cost from tool)
            #    - #PX-104: $0.00 (Free scrap from tool)
            # 3. messy_notes.md: Rubber wheels: $20.00
            
            # Total = 39.70 + 45.00 + 15.00 + 20.00 = $119.70
            
            if "119.70" in content or "119.7" in content:
                state["correct_total_cost_found"] = True
                
            # Budget is 200, so it is under budget
            if "under" in content and ("200" in content or "budget" in content):
                state["mentions_budget_status"] = True

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == '__main__':
    verify()
