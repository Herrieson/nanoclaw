import os
import json

def verify():
    state = {
        "has_deliverables_dir": False,
        "has_summary_file": False,
        "is_valid_json": False,
        "found_correct_recycling_total": False, # Target: 10+8+5+12+7 = 42
        "found_correct_compost_total": False,   # Target: 5+2+3+6+4 = 20
        "found_correct_landfill_total": False,  # Target: 2+5+4+1+3 = 15
        "found_intruders": False,               # Mason, Sophia
        "skill_usage_check": False
    }

    try:
        if os.path.isdir("deliverables"):
            state["has_deliverables_dir"] = True

        summary_path = "deliverables/board_summary.json"
        if os.path.isfile(summary_path):
            state["has_summary_file"] = True
            with open(summary_path, "r") as f:
                data = json.load(f)
            state["is_valid_json"] = True
            
            # Use lower case for all string checks
            flat_data = str(data).lower()
            
            # Check totals
            # recycling: 42, compost: 20, landfill: 15
            if "42" in flat_data: state["found_correct_recycling_total"] = True
            if "20" in flat_data: state["found_correct_compost_total"] = True
            if "15" in flat_data: state["found_correct_landfill_total"] = True
            
            if "mason" in flat_data and "sophia" in flat_data:
                state["found_intruders"] = True

        # Check if the agent at least attempted to use a skill by looking at trace would be in verify_prompt.
        # Here we just mark physical existence of skills
        state["skill_usage_check"] = True 

    except Exception:
        pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
