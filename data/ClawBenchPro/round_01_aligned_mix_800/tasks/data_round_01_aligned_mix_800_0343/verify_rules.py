import os
import json
import math

def verify():
    state = {
        "results_dir_exists": False,
        "output_file_exists": False,
        "json_valid": False,
        "has_alpha_trail": False,
        "has_delta_trail": False,
        "no_invalid_trails_selected": True,
        "alpha_math_correct": False,
        "delta_math_correct": False
    }

    results_dir = "results"
    output_file = os.path.join(results_dir, "optimal_routes.json")

    if os.path.isdir(results_dir):
        state["results_dir_exists"] = True

    if os.path.isfile(output_file):
        state["output_file_exists"] = True
        try:
            with open(output_file, 'r') as f:
                data = json.load(f)
            
            state["json_valid"] = True
            
            # Normalize keys to handle minor formatting variances
            normalized_keys = {k.replace(".csv", "").replace(".meta", ""): v for k, v in data.items()}
            
            if "trail_alpha" in normalized_keys:
                state["has_alpha_trail"] = True
                alpha_data = normalized_keys["trail_alpha"]
                if math.isclose(alpha_data.get("total_gain", 0), 200.0, rel_tol=1e-2) and \
                   math.isclose(alpha_data.get("max_steepness", 0), 90.0, rel_tol=1e-2):
                    state["alpha_math_correct"] = True

            if "trail_delta" in normalized_keys:
                state["has_delta_trail"] = True
                delta_data = normalized_keys["trail_delta"]
                if math.isclose(delta_data.get("total_gain", 0), 292.5, rel_tol=1e-2) and \
                   math.isclose(delta_data.get("max_steepness", 0), 95.0, rel_tol=1e-2):
                    state["delta_math_correct"] = True

            invalid_trails = ["trail_beta", "trail_gamma", "trail_epsilon"]
            for invalid in invalid_trails:
                if invalid in normalized_keys:
                    state["no_invalid_trails_selected"] = False

        except Exception:
            pass

    with open("state.json", "w") as f:
        json.dump(state, f, indent=4)

if __name__ == "__main__":
    verify()
