import os
import json

def verify():
    state = {
        "has_finished_plan_dir": False,
        "has_report_file": False,
        "correct_total_cost_found": False,
        "mentions_budget_status": False
    }
    
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
            
            # The exact bought items:
            # steering wheel: 35.50
            # bolts: 4.20
            # Steel Axle: 45.00
            # used rubber wheels: 20.00
            # Total = 104.70
            
            if "104.70" in content or "104.7" in content:
                state["correct_total_cost_found"] = True
                
            # Budget is 200, so it is under budget
            budget_keywords = ["under budget", "under 200", "under $200", "did not go over", "didn't go over", "remaining"]
            if any(keyword in content for keyword in budget_keywords):
                state["mentions_budget_status"] = True

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == '__main__':
    verify()
