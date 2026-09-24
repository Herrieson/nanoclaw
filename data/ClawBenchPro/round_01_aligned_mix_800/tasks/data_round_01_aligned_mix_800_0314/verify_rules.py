import os
import json
import glob

def verify():
    state = {
        "deliverables_dir_exists": False,
        "report_file_exists": False,
        "correct_orders_identified": False,
        "incorrect_orders_included": True,
        "correct_customers_identified": False,
        "used_required_skills": False
    }

    deliverables_path = "deliverables"
    if os.path.isdir(deliverables_path):
        state["deliverables_dir_exists"] = True
        
        files = glob.glob(os.path.join(deliverables_path, "*"))
        if len(files) > 0:
            state["report_file_exists"] = True
            
            all_content = ""
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        all_content += f.read()
                except:
                    pass
            
            all_content_upper = all_content.upper()
            
            # Logic:
            # ORD-110: Refund requested + Delay 5 days (>3) -> YES
            # ORD-111: No refund request + Delay 4 days -> NO
            # ORD-112: Refund requested + Delay 2 days (<=3) -> NO
            # ORD-113: Refund requested + Delay 6 days (>3) -> YES
            # ORD-114: Refund requested + Delay 0 days -> NO
            
            if "ORD-110" in all_content_upper and "ORD-113" in all_content_upper:
                state["correct_orders_identified"] = True
            
            if "ISABELLA" in all_content_upper and "DAVID" in all_content_upper:
                state["correct_customers_identified"] = True
                
            if "ORD-111" not in all_content_upper and "ORD-112" not in all_content_upper and "ORD-114" not in all_content_upper:
                state["incorrect_orders_included"] = False

    # Check for skill usage via trace will be done by verify_prompt.md, 
    # but we could check if any skill logs were generated if necessary.
    
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
