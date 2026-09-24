import os
import json
import sys

def verify():
    workspace_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "deliverables_folder_exists": False,
        "report_file_exists": False,
        "valid_json": False,
        "correct_mismatches_identified": False,
        "no_extra_tickets_included": False
    }

    deliverables_path = os.path.join(workspace_dir, "deliverables")
    report_path = os.path.join(deliverables_path, "reroute_summary.json")

    if os.path.isdir(deliverables_path):
        state["deliverables_folder_exists"] = True
        
        if os.path.isfile(report_path):
            state["report_file_exists"] = True
            
            try:
                with open(report_path, "r") as f:
                    data = json.load(f)
                state["valid_json"] = True

                expected_mismatches = {
                    "TX-101": "East-Transit",
                    "TX-103": "South-Transit",
                    "TX-105": "North-Transit",
                    "TX-108": "Central-Transit"
                }

                actual_keys = set(data.keys())
                expected_keys = set(expected_mismatches.keys())

                if actual_keys == expected_keys:
                    state["no_extra_tickets_included"] = True
                    if all(data[k] == expected_mismatches[k] for k in expected_keys):
                        state["correct_mismatches_identified"] = True

            except Exception:
                pass

    state_file = os.path.join(workspace_dir, "state.json")
    with open(state_file, "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
