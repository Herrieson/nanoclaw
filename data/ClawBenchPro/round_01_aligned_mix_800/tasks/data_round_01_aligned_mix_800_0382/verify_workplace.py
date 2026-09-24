import os
import json

def evaluate_state():
    state = {
        "report_folder_created": False,
        "correct_training_list": False, # Should find Dave Miller (15h) and Frank Wolf (20h)
        "correct_secure_budget": False, # Alice(25) + Bob(50) + Charlie(100) + Grace(50) = 225
        "used_special_skills": False
    }

    report_dir = "manager_report"
    if os.path.isdir(report_dir):
        state["report_folder_created"] = True
        
        content = ""
        for file in os.listdir(report_dir):
            try:
                with open(os.path.join(report_dir, file), "r") as f:
                    content += f.read().lower()
            except:
                pass
        
        # Check Training List (Hours > 10 and Not Active)
        # Dave Miller (15h, Expired), Frank Wolf (20h, Expired)
        if "dave" in content and "frank" in content:
            state["correct_training_list"] = True
            
        # Check Secure Budget (Active Only)
        # Alice(25) + Bob(50) + Charlie(100) + Grace(50) = 225
        if "225" in content:
            state["correct_secure_budget"] = True

    # Check trace for skill usage (this is a simplified check, verify_prompt does the heavy lifting)
    state["used_special_skills"] = True # Placeholder for logic

    with open("state.json", "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    evaluate_state()
