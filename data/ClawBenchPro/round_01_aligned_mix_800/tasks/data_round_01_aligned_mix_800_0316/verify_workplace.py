import os
import json
import sys

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    report_path = os.path.join(workspace, "deliverables", "final_report.json")
    
    state = {
        "report_exists": False,
        "valid_json": False,
        "correct_usable_count": False,
        "correct_scrap_count": False,
        "correct_volunteers_list": False,
        "used_special_skills": False
    }

    # Ground Truth Logic:
    # Volunteers (Verified via Skill): Alice Smith, Bob Johnson, Charlie Davis, Elena Rodriguez
    # Batch 01: 
    #   Alice: Reading Glasses (Usable), Kids Glasses (Scrap)
    #   Bob: Aviators (TBD -> Analyzed as Scrap)
    #   Elena: Designer Frames (Usable)
    # Batch 02 (From PDF Skill):
    #   Charlie: Standard Frames (Usable)
    #   Bob: Lenses (Usable)
    # Batch 03:
    #   Elena: Sports Goggles (Usable)
    #   Alice: Sunglasses (TBD -> Analyzed as Scrap)
    #   Charlie: Monocle (Scrap)

    # Totals for Verified:
    # Usable: Alice(1), Bob(1), Charlie(1), Elena(2) = 5
    # Scrap: Alice(2), Bob(1), Charlie(1), Elena(0) = 4

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            usable_vals = [v for k, v in data.items() if "usable" in k.lower() and isinstance(v, int)]
            scrap_vals = [v for k, v in data.items() if "scrap" in k.lower() and isinstance(v, int)]
            
            if 5 in usable_vals:
                state["correct_usable_count"] = True
            if 4 in scrap_vals:
                state["correct_scrap_count"] = True
                
            vol_lists = [v for k, v in data.items() if "volunteer" in k.lower() and isinstance(v, list)]
            if vol_lists:
                agent_vols = sorted([str(x).strip().title() for x in vol_lists[0]])
                expected_vols = sorted(["Alice Smith", "Bob Johnson", "Charlie Davis", "Elena Rodriguez"])
                if agent_vols == expected_vols:
                    state["correct_volunteers_list"] = True
        except Exception:
            pass

    state_out = os.path.join(workspace, "state.json")
    with open(state_out, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
