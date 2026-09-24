import os
import json
import sys

def verify():
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverable_path = os.path.join(work_dir, "deliverables", "urgent_field_review.json")
    
    state = {
        "file_exists": False,
        "valid_json": False,
        "identified_grove_south": False, # pH low
        "identified_grove_east": False,  # Nitro-Max unapproved
        "identified_grove_central": False, # Both
        "skill_usage_correct": False
    }
    
    if os.path.exists(deliverable_path):
        state["file_exists"] = True
        try:
            with open(deliverable_path, "r") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            content_str = json.dumps(data).lower()
            
            if "grove_south" in content_str and "ph" in content_str:
                state["identified_grove_south"] = True
            if "grove_east" in content_str and ("nitro-max" in content_str or "chemical" in content_str or "fertilizer" in content_str):
                state["identified_grove_east"] = True
            if "grove_central" in content_str:
                state["identified_grove_central"] = True
                
        except Exception:
            pass
            
    # Check trace for skill usage (this is a placeholder for the verify_prompt logic)
    # The actual trace checking happens in the LLM Judge
    
    state_file = os.path.join(work_dir, "state.json")
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
