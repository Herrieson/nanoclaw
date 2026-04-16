import os
import json
import sys

def verify():
    # Expecting the agent to create summary.json in the workspace
    # In the evaluation environment, this script runs against the workspace directory
    workspace_dir = os.environ.get("WORKSPACE_DIR", ".")
    summary_file = os.path.join(workspace_dir, "summary.json")
    
    state = {
        "summary_file_exists": False,
        "valid_json": False,
        "keys_present": False,
        "correct_bottles": False,
        "correct_earnings": False,
        "extracted_bottles": None,
        "extracted_earnings": None,
        "overall_success": False
    }

    if os.path.exists(summary_file):
        state["summary_file_exists"] = True
        try:
            with open(summary_file, "r") as f:
                data = json.load(f)
            state["valid_json"] = True
            
            if "total_bottles" in data and "total_earnings" in data:
                state["keys_present"] = True
                
                # Extracted values
                b = data.get("total_bottles", 0)
                e = data.get("total_earnings", 0.0)
                
                state["extracted_bottles"] = b
                state["extracted_earnings"] = e
                
                # Calculate correct values:
                # Bottles: 42 + 18 + 105 + 33 = 198
                # Earnings: (3.5 + 2 + 4) * 15 = 9.5 * 15 = 142.5
                if int(b) == 198:
                    state["correct_bottles"] = True
                if float(e) == 142.5:
                    state["correct_earnings"] = True
                    
            if state["correct_bottles"] and state["correct_earnings"]:
                state["overall_success"] = True
                
        except Exception as e:
            state["error"] = str(e)

    # Output structural result
    print(json.dumps(state))
    return state

if __name__ == "__main__":
    verify()
