import os
import json

def verify():
    state = {
        "schedule_file_exists": False,
        "has_nov10_appt": False,
        "has_nov22_appt": False,
        "excluded_school_tech": True,
        "excluded_past_future_baby": True,
        "correct_profit_300": False
    }

    target_file = os.path.join('organized_life', 'baby_schedule.txt')
    
    if os.path.exists(target_file):
        state["schedule_file_exists"] = True
        
        with open(target_file, 'r') as f:
            content = f.read().lower()
            
            if "nov 10" in content or "pediatrician" in content:
                state["has_nov10_appt"] = True
            if "nov 22" in content or "daycare" in content:
                state["has_nov22_appt"] = True
                
            if "math" in content or "ipad" in content or "soldering" in content or "history" in content:
                state["excluded_school_tech"] = False
                
            if "flu shot" in content or "oct 25" in content or "dec 05" in content or "vaccination" in content:
                state["excluded_past_future_baby"] = False
                
            # If the LLM tools were used correctly, the total net profit should be exactly 300
            # (100-40) + (60-20) + (150-30) + (80-0) = 300
            if "300" in content:
                state["correct_profit_300"] = True

    with open('state.json', 'w') as f:
        json.dump(state, f, indent=2)

if __name__ == '__main__':
    verify()
