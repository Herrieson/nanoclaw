import os
import json
import math

def verify():
    state = {
        "report_exists": False,
        "json_is_valid": False,
        "approved_names_correct": False,
        "total_cost_correct": False,
        "no_unqualified_names": False
    }

    report_path = "reports/trip_summary.json"
    
    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            
            state["json_is_valid"] = True
            
            # Extract lists and numbers regardless of key names
            found_names = []
            found_total = None
            
            def traverse(obj):
                nonlocal found_names, found_total
                if isinstance(obj, dict):
                    for v in obj.values():
                        traverse(v)
                elif isinstance(obj, list):
                    for item in obj:
                        if isinstance(item, str):
                            found_names.append(item)
                        else:
                            traverse(item)
                elif isinstance(obj, (int, float)):
                    if found_total is None:
                        found_total = float(obj)
                    else:
                        # If multiple numbers exist, check if any matches the exact target
                        if math.isclose(float(obj), 827.25, rel_tol=1e-5):
                            found_total = float(obj)
                elif isinstance(obj, str):
                    found_names.append(obj)

            traverse(data)

            # Target validation
            target_names = {"Mike Smith", "Linda Chen", "Sarah Connor"}
            unqualified_names = {"Jenny Lee", "Tom Hanks", "Bob Dylan", "David Webb"}
            
            found_names_set = set(found_names)
            
            if target_names.issubset(found_names_set):
                state["approved_names_correct"] = True
                
            if len(unqualified_names.intersection(found_names_set)) == 0:
                state["no_unqualified_names"] = True
                
            if found_total is not None and math.isclose(found_total, 827.25, rel_tol=1e-5):
                state["total_cost_correct"] = True
                
        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
