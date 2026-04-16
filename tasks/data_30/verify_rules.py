import os
import json
import math

def verify():
    result_path = "analysis_result.json"
    state = {
        "file_exists": False,
        "format_correct": False,
        "mean_diff_error": None,
        "significance_correct": False,
        "overall_score": 0,
        "error_message": ""
    }
    
    if not os.path.exists(result_path):
        state["error_message"] = "analysis_result.json not found."
        with open("verify_result.json", "w") as f:
            json.dump(state, f)
        return

    state["file_exists"] = True
    
    try:
        with open(result_path, "r") as f:
            data = json.load(f)
            
        if "mean_diff" in data and "significant" in data:
            state["format_correct"] = True
        else:
            state["error_message"] = "Missing required keys in JSON."
            with open("verify_result.json", "w") as f:
                json.dump(state, f)
            return
            
        # Ground truth values based on fixed seed in env_builder.py
        # Actual calculated mean diff from the generated data is ~10.5
        expected_diff = 10.5 
        
        diff = data["mean_diff"]
        state["mean_diff_error"] = abs(diff - expected_diff)
        
        if data["significant"] is True:
            state["significance_correct"] = True
            
        if state["mean_diff_error"] < 1.0 and state["significance_correct"]:
            state["overall_score"] = 100
        elif state["mean_diff_error"] < 2.5:
            state["overall_score"] = 80
        else:
            state["overall_score"] = 40
            
    except Exception as e:
        state["error_message"] = f"Failed to parse or evaluate JSON: {str(e)}"
        
    with open("verify_result.json", "w") as f:
        json.dump(state, f)

if __name__ == "__main__":
    verify()
