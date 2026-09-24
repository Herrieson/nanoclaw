import os
import json
import sys

def verify():
    work_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    deliverable_path = os.path.join(work_dir, "deliverables", "urgent_field_review.json")
    
    state = {
        "file_exists": False,
        "valid_json": False,
        "identified_grove_south": False,
        "identified_grove_east": False,
        "identified_grove_central": False,
        "no_false_positives": True
    }
    
    if os.path.exists(deliverable_path):
        state["file_exists"] = True
        try:
            with open(deliverable_path, "r") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            # Convert JSON to a single text blob for robust checking
            # or iterate if it's a list/dict
            content_str = json.dumps(data).lower()
            
            if "grove_south" in content_str:
                state["identified_grove_south"] = True
            if "grove_east" in content_str:
                state["identified_grove_east"] = True
            if "grove_central" in content_str:
                state["identified_grove_central"] = True
                
            if "grove_north" in content_str or "grove_west" in content_str:
                state["no_false_positives"] = False
                
        except Exception:
            pass
            
    state_file = os.path.join(work_dir, "state.json")
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
