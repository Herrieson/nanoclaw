import os
import sys
import json

def verify():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    
    state = {
        "report_exists": False,
        "valid_json": False,
        "correct_hours_found": False,
        "correct_fluid_found": False
    }

    report_path = os.path.join(workspace, "office_reports", "transmission_summary.json")

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            state["valid_json"] = True

            # Helper function to recursively extract all values from the JSON
            def extract_values(obj):
                values = []
                if isinstance(obj, dict):
                    for v in obj.values():
                        values.extend(extract_values(v))
                elif isinstance(obj, list):
                    for item in obj:
                        values.extend(extract_values(item))
                else:
                    values.append(obj)
                return values

            all_values = extract_values(data)
            str_values = [str(v).strip() for v in all_values]
            
            # The correct transmission hours is 12 + 2 + 4 = 18
            # The correct transmission fluid is 8 + 14 + 3 = 25
            
            if "18" in str_values or "18.0" in str_values:
                state["correct_hours_found"] = True
                
            if "25" in str_values or "25.0" in str_values:
                state["correct_fluid_found"] = True

        except Exception:
            pass

    # Save the objective state to state.json
    state_file = os.path.join(workspace, "state.json")
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
