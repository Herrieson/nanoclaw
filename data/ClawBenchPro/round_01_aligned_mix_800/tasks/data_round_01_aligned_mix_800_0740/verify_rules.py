import os
import json

def verify():
    state = {
        "summary_exists": False,
        "valid_json": False,
        "total_value_correct": False,
        "cases_correct": False
    }

    target_file = os.path.join("precinct_desk", "bolo_summary.json")
    
    if os.path.exists(target_file):
        state["summary_exists"] = True
        try:
            with open(target_file, "r") as f:
                data = json.load(f)
            state["valid_json"] = True

            # Expected total stolen: 500 + 25000 + 1200 + 300 = 27000
            # Expected cases: 102, 104
            
            found_total = False
            found_cases = False

            # We don't know the exact keys the agent will use, so we inspect all values
            for key, value in data.items():
                if str(value) == "27000" or value == 27000:
                    found_total = True
                
                if isinstance(value, list):
                    # Convert all elements to string and sort for reliable comparison
                    str_cases = sorted([str(c) for c in value])
                    if str_cases == ["102", "104"]:
                        found_cases = True

            state["total_value_correct"] = found_total
            state["cases_correct"] = found_cases
            
        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
