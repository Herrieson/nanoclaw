import os
import json
import re

def verify():
    state = {
        "summary_file_exists": False,
        "correct_total_calculated": False,
        "included_gas_items_by_mistake": False,
        "included_donations_by_mistake": False
    }

    summary_path = "church_funds/summary.txt"
    if os.path.exists(summary_path):
        state["summary_file_exists"] = True
        with open(summary_path, "r", encoding="utf-8") as f:
            content = f.read()
            
            # Correct Bake Sale Items: 
            # Pecan Pie (15.50) + Sweet Tea Jug (5.00) + Brownies (20.00) + Cookies (12.00) + Lemon Pound Cake (18.00) = 70.50
            if "70.5" in content or "70.50" in content:
                state["correct_total_calculated"] = True
                
            # Check for common mistakes
            # If they added pump (42) + marlboro (8.50) = 50.50 -> 121.00
            if "121.0" in content or "121" in content:
                state["included_gas_items_by_mistake"] = True
                
            # If they added the $5 donation -> 75.50
            if "75.5" in content or "75.50" in content:
                state["included_donations_by_mistake"] = True

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
