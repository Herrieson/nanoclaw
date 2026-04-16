import os
import json

def verify():
    output_path = "output/pattern_output.json"
    result = {
        "success": False,
        "output_exists": False,
        "valid_json": False,
        "correct_pattern": False,
        "points": 0,
        "error": None
    }
    
    if not os.path.exists(output_path):
        result["error"] = "Output file pattern_output.json not found."
        return result
        
    result["output_exists"] = True
    result["points"] += 20
    
    try:
        with open(output_path, 'r') as f:
            data = json.load(f)
        result["valid_json"] = True
        result["points"] += 30
    except Exception as e:
        result["error"] = f"Output file is not valid JSON: {e}"
        return result
        
    # Expected pattern coordinates for the black pixels in the 10x10 image
    expected_coords = [
        {"x": 2, "y": 1}, {"x": 3, "y": 1}, {"x": 4, "y": 1},
        {"x": 1, "y": 2}, {"x": 2, "y": 2}, {"x": 3, "y": 2}, {"x": 4, "y": 2}, {"x": 5, "y": 2},
        {"x": 1, "y": 3}, {"x": 2, "y": 3}, {"x": 3, "y": 3}, {"x": 4, "y": 3}, {"x": 5, "y": 3}, {"x": 6, "y": 3},
        {"x": 2, "y": 4}, {"x": 3, "y": 4}, {"x": 4, "y": 4}, {"x": 5, "y": 4},
        {"x": 3, "y": 5}, {"x": 4, "y": 5}, {"x": 5, "y": 5},
        {"x": 3, "y": 6}, {"x": 4, "y": 6}, {"x": 5, "y": 6},
        {"x": 3, "y": 7}, {"x": 4, "y": 7}, {"x": 5, "y": 7}
    ]
    
    if isinstance(data, list) and len(data) == len(expected_coords):
        # Sort both lists by x and y to compare safely
        sorted_actual = sorted(data, key=lambda d: (d.get("x", -1), d.get("y", -1)))
        sorted_expected = sorted(expected_coords, key=lambda d: (d["x"], d["y"]))
        
        if sorted_actual == sorted_expected:
            result["correct_pattern"] = True
            result["success"] = True
            result["points"] += 50
        else:
            result["error"] = "Pattern coordinates do not match the target image."
    else:
        result["error"] = "Pattern list length does not match expected black pixels."
        
    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=4)
        
    return result

if __name__ == "__main__":
    verify()
