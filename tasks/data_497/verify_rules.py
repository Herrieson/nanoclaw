import os
import json

def verify():
    base_dir = "."
    truth_file = os.path.join(base_dir, ".ground_truth.json")
    summary_file = os.path.join(base_dir, "summary.json")
    
    result = {
        "summary_exists": False,
        "format_valid": False,
        "top_speed_match": False,
        "miles_match": False,
        "expected_top_speed": None,
        "got_top_speed": None,
        "expected_miles": None,
        "got_miles": None,
        "score": 0
    }

    try:
        with open(truth_file, "r") as f:
            truth = json.load(f)
            result["expected_top_speed"] = truth["top_speed"]
            result["expected_miles"] = truth["total_miles"]
    except Exception as e:
        pass

    if os.path.exists(summary_file):
        result["summary_exists"] = True
        try:
            with open(summary_file, "r") as f:
                summary = json.load(f)
            
            if "top_speed" in summary and "total_miles" in summary:
                result["format_valid"] = True
                
                got_speed = float(summary["top_speed"])
                got_miles = float(summary["total_miles"])
                
                result["got_top_speed"] = got_speed
                result["got_miles"] = got_miles
                
                if got_speed == result["expected_top_speed"]:
                    result["top_speed_match"] = True
                    result["score"] += 40
                
                # Check miles with a tolerance of 0.2 miles due to float rounding
                if abs(got_miles - result["expected_miles"]) <= 0.2:
                    result["miles_match"] = True
                    result["score"] += 60

        except Exception as e:
            pass

    with open("verify_result.json", "w") as f:
        json.dump(result, f, indent=2)

if __name__ == "__main__":
    verify()
