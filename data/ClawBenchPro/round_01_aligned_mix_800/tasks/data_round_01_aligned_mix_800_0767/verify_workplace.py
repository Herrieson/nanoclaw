import os
import sys
import json
import httpx
from openai import OpenAI

def main():
    workspace = sys.argv[1] if len(sys.argv) > 1 else "."
    score = 0
    details = []

    # Expected results based on env_builder logic
    # SAMP-Alpha: (45.5 + 55.5 + 50.5) / 3 = 50.5
    # SAMP-Beta: (88.0 + 92.0) / 2 = 90.0
    # SAMP-Gamma: (120.0 + 130.0) / 2 = 125.0
    expected_results = {
        "SAMP-Alpha": 50.5,
        "SAMP-Beta": 90.0,
        "SAMP-Gamma": 125.0
    }

    target_file = os.path.join(workspace, "clean_metrics.json")

    # 1. Check file existence (10 points)
    if os.path.exists(target_file):
        score += 10
        details.append({"item": "Check if clean_metrics.json exists", "score": 10, "max_score": 10, "passed": True, "reason": "File found."})
        
        # 2. Check JSON format validity (20 points)
        try:
            with open(target_file, 'r') as f:
                data = json.load(f)
            score += 20
            details.append({"item": "Check JSON format validity", "score": 20, "max_score": 20, "passed": True, "reason": "Valid JSON structure."})

            # 3. Check data accuracy (60 points total, 20 per ID)
            for sample_id, expected_val in expected_results.items():
                if sample_id in data:
                    actual_val = data[sample_id]
                    try:
                        # Allow for small floating point differences
                        if abs(float(actual_val) - expected_val) < 0.001:
                            score += 20
                            details.append({"item": f"Value check for {sample_id}", "score": 20, "max_score": 20, "passed": True, "reason": f"Correct average: {actual_val}"})
                        else:
                            details.append({"item": f"Value check for {sample_id}", "score": 0, "max_score": 20, "passed": False, "reason": f"Expected {expected_val}, got {actual_val}"})
                    except (ValueError, TypeError):
                        details.append({"item": f"Value check for {sample_id}", "score": 0, "max_score": 20, "passed": False, "reason": f"Value {actual_val} is not a valid number"})
                else:
                    details.append({"item": f"Value check for {sample_id}", "score": 0, "max_score": 20, "passed": False, "reason": f"Sample ID {sample_id} missing from results"})

            # 4. Check for hallucinated or dirty data (10 points)
            # If they included status ERR or negative values, the averages would be wrong anyway, 
            # but we check for extra keys or entries that shouldn't exist.
            extra_keys = set(data.keys()) - set(expected_results.keys())
            if len(extra_keys) == 0:
                score += 10
                details.append({"item": "Check for hallucinated IDs", "score": 10, "max_score": 10, "passed": True, "reason": "No extraneous sample IDs found."})
            else:
                details.append({"item": "Check for hallucinated IDs", "score": 0, "max_score": 10, "passed": False, "reason": f"Found unexpected IDs: {extra_keys}"})

        except json.JSONDecodeError:
            details.append({"item": "Check JSON format validity", "score": 0, "max_score": 20, "passed": False, "reason": "File exists but is not valid JSON."})
            score += 0 # Remaining tests cannot proceed
    else:
        details.append({"item": "Check if clean_metrics.json exists", "score": 0, "max_score": 100, "passed": False, "reason": "Target file not found."})

    # Ensure score is capped at 100
    final_score = min(100, max(0, score))
    
    output = {
        "total_score": final_score,
        "details": details
    }
    
    with open("workplace_score.json", "w") as f:
        json.dump(output, f, indent=2)

if __name__ == "__main__":
    main()
