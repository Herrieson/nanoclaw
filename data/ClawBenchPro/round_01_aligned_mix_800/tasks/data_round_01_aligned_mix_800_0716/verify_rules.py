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
        "correct_volunteers_list": False
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            # Ground truth calculations:
            # Alice: 1 Usable, 2 Scrap (from batch1: Usable, scrap; batch3: SCRAP)
            # Bob: 1 Usable, 1 Scrap (batch1: SCRAP; batch2: usable)
            # Charlie: 1 Usable, 1 Scrap (batch2: Usable, scrap)
            # Elena: 2 Usable, 0 Scrap (batch1: USABLE; batch3: Usable)
            # Total Official Usable = 1(A) + 1(B) + 1(C) + 2(E) = 5
            # Total Official Scrap = 2(A) + 1(B) + 1(C) + 0(E) = 4
            # Verified volunteers = Alice Smith, Bob Johnson, Charlie Davis, Elena Rodriguez

            # Check counts
            # Allow some flexibility in keys (Agent might use usable_count, total_usable, etc.)
            usable_vals = [v for k, v in data.items() if "usable" in k.lower() and isinstance(v, int)]
            scrap_vals = [v for k, v in data.items() if "scrap" in k.lower() and isinstance(v, int)]
            
            if 5 in usable_vals:
                state["correct_usable_count"] = True
            if 4 in scrap_vals:
                state["correct_scrap_count"] = True
                
            # Check volunteer list
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
