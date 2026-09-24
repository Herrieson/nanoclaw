import os
import json
import math

def extract_all_numbers(d):
    nums = []
    if isinstance(d, dict):
        for v in d.values():
            nums.extend(extract_all_numbers(v))
    elif isinstance(d, list):
        for v in d:
            nums.extend(extract_all_numbers(v))
    elif isinstance(d, (int, float)):
        nums.append(float(d))
    elif isinstance(d, str):
        try:
            nums.append(float(d))
        except ValueError:
            pass
    return nums

def verify():
    state = {
        "deliverables_dir_exists": False,
        "clean_results_exists": False,
        "is_valid_json": False,
        "found_correct_count": False,
        "found_correct_average": False,
        "used_special_skills": False
    }

    if os.path.exists("deliverables") and os.path.isdir("deliverables"):
        state["deliverables_dir_exists"] = True

    result_path = "deliverables/clean_results.json"
    if os.path.exists(result_path):
        state["clean_results_exists"] = True
        try:
            with open(result_path, 'r') as f:
                data = json.load(f)
            state["is_valid_json"] = True
            numbers = extract_all_numbers(data)
            
            # Target: Count 4, Average 300.25
            for num in numbers:
                if math.isclose(num, 4.0, rel_tol=1e-5):
                    state["found_correct_count"] = True
                if math.isclose(num, 300.25, rel_tol=1e-5):
                    state["found_correct_average"] = True
        except:
            pass

    # Check for skill usage markers in a hypothetical trace or log if possible
    # Here we rely on the verify_prompt to double check the trace.jsonl
    
    with open("state.json", "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
