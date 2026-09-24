import os
import json
import glob

def verify():
    state = {
        "deliverables_dir_exists": False,
        "report_file_exists": False,
        "correct_orders_identified": False,
        "incorrect_orders_included": True,
        "correct_customers_identified": False
    }

    deliverables_path = "deliverables"
    if os.path.isdir(deliverables_path):
        state["deliverables_dir_exists"] = True
        
        # Check if any file exists in deliverables
        files = glob.glob(os.path.join(deliverables_path, "*"))
        if len(files) > 0:
            state["report_file_exists"] = True
            
            # Read contents of all files in deliverables to check for targets
            all_content = ""
            for file_path in files:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        all_content += f.read()
                except:
                    pass
            
            all_content_upper = all_content.upper()
            
            # Expected correct targets
            # ORD-110 (Isabella Cortez), ORD-113 (David Kim)
            if "ORD-110" in all_content_upper and "ORD-113" in all_content_upper:
                state["correct_orders_identified"] = True
            
            if "ISABELLA" in all_content_upper and "DAVID" in all_content_upper:
                state["correct_customers_identified"] = True
                
            # Expected incorrect targets
            # ORD-111, ORD-112, ORD-114
            if "ORD-111" not in all_content_upper and "ORD-112" not in all_content_upper and "ORD-114" not in all_content_upper:
                state["incorrect_orders_included"] = False # This means it did NOT include incorrect orders, which is good.

    # Write state to physical file
    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
