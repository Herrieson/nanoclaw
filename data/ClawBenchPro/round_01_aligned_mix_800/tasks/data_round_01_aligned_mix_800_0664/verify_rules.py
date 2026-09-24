import os
import json
import sys

def verify():
    # Set workspace
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    target_file = os.path.join(workspace, "deliverables", "regional_totals.json")
    
    state = {
        "deliverables_folder_exists": os.path.exists(os.path.join(workspace, "deliverables")),
        "target_file_exists": False,
        "is_valid_json": False,
        "has_all_regions": False,
        "west_correct": False,
        "east_correct": False,
        "north_correct": False,
        "south_correct": False,
        "central_correct": False,
        "no_extra_regions": False
    }
    
    if os.path.exists(target_file):
        state["target_file_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            
            state["is_valid_json"] = True
            
            # Normalize keys to lowercase for robust checking
            normalized_data = {str(k).lower(): v for k, v in data.items()}
            
            # Check presence of expected regions
            expected_keys = {"west", "east", "north", "south", "central"}
            state["has_all_regions"] = expected_keys.issubset(set(normalized_data.keys()))
            state["no_extra_regions"] = set(normalized_data.keys()).issubset(expected_keys)
            
            # Check values
            state["west_correct"] = (normalized_data.get("west") == 4500)
            state["east_correct"] = (normalized_data.get("east") == 1200)
            state["north_correct"] = (normalized_data.get("north") == 18000)
            state["south_correct"] = (normalized_data.get("south") == 2500)
            state["central_correct"] = (normalized_data.get("central") == 5000)
            
        except Exception:
            pass

    # Dump state to physical file
    state_path = os.path.join(workspace, "state.json")
    with open(state_path, "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
