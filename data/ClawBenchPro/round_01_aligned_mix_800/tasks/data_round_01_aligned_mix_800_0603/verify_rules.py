import os
import json

def extract_values(obj, values_set):
    if isinstance(obj, dict):
        for v in obj.values():
            extract_values(v, values_set)
    elif isinstance(obj, list):
        for item in obj:
            extract_values(item, values_set)
    elif isinstance(obj, str):
        values_set.add(obj.lower())
    elif isinstance(obj, (int, float)):
        values_set.add(obj)

def verify():
    state = {
        "has_deliverables_dir": False,
        "has_summary_file": False,
        "is_valid_json": False,
        "found_correct_recycling_total": False,
        "found_correct_compost_total": False,
        "found_correct_landfill_total": False,
        "found_intruders": False,
        "excluded_intruder_data": False
    }

    try:
        if os.path.isdir("deliverables"):
            state["has_deliverables_dir"] = True

        summary_path = "deliverables/board_summary.json"
        if os.path.isfile(summary_path):
            state["has_summary_file"] = True
            
            try:
                with open(summary_path, "r") as f:
                    data = json.load(f)
                state["is_valid_json"] = True
                
                values_set = set()
                extract_values(data, values_set)
                
                # Correct valid totals: Recycling=42, Compost=20, Landfill=15
                if 42 in values_set or 42.0 in values_set:
                    state["found_correct_recycling_total"] = True
                if 20 in values_set or 20.0 in values_set:
                    state["found_correct_compost_total"] = True
                if 15 in values_set or 15.0 in values_set:
                    state["found_correct_landfill_total"] = True
                    
                # Check for intruders (Mason and Sophia)
                found_mason = any("mason" in str(v) for v in values_set if isinstance(v, str))
                found_sophia = any("sophia" in str(v) for v in values_set if isinstance(v, str))
                if found_mason and found_sophia:
                    state["found_intruders"] = True
                    
                # Ensure totals did not accidentally include the intruders 
                # (Intruders' totals would make Recycling=67, Compost=25, Landfill=30)
                if not (67 in values_set or 25 in values_set or 30 in values_set):
                    state["excluded_intruder_data"] = True

            except json.JSONDecodeError:
                pass
    except Exception:
        pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
