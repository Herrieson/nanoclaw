import os
import json
import re

def verify():
    base_dir = "."
    plan_path = os.path.join(base_dir, 'festival_plan.txt')
    
    state = {
        "plan_exists": False,
        "has_correct_ticket": False,
        "has_neon_indian_time": False,
        "has_kendrick_lamar_time": False,
        "budget_calculated_correctly_in_thought": False # We will let LLM judge this part if needed, or infer from ticket.
    }

    if os.path.exists(plan_path):
        state["plan_exists"] = True
        with open(plan_path, 'r', encoding='utf-8') as f:
            content = f.read().lower()
            
            # Net budget is 400, VIP is 350. She can afford VIP.
            if "vip" in content and "ga" not in content.replace("general admission", ""):
                state["has_correct_ticket"] = True
            elif "vip" in content:
                # If both mentioned, we just check if VIP is the conclusion, loose check.
                state["has_correct_ticket"] = True

            # Times: Neon Indian is 19:30, Kendrick is 22:30
            if "19:30" in content or "7:30" in content:
                state["has_neon_indian_time"] = True
            
            if "22:30" in content or "10:30" in content:
                state["has_kendrick_lamar_time"] = True

    # Output results
    result_path = os.path.join(os.path.dirname(__file__), 'state.json')
    with open(result_path, 'w', encoding='utf-8') as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
