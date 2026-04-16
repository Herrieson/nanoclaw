import os
import json

def verify():
    base_dir = "."
    report_path = os.path.join(base_dir, "consolidated_report.json")
    
    state = {
        "report_exists": False,
        "is_valid_json": False,
        "total_revenue_correct": False,
        "sorted_correctly": False,
        "filtered_invalid": False,
        "keys_correct": False
    }

    if os.path.exists(report_path):
        state["report_exists"] = True
        try:
            with open(report_path, "r") as f:
                data = json.load(f)
            state["is_valid_json"] = True

            # Check total revenue (25.0 + 15.0 + 9.0 + 22.4 = 71.4)
            expected_rev = 71.4
            if "total_revenue" in data and abs(float(data["total_revenue"]) - expected_rev) < 0.01:
                state["total_revenue_correct"] = True

            # Check deliveries list
            deliveries = data.get("deliveries", [])
            trks = [d.get("tracking_number", "") for d in deliveries]
            
            # Should only contain 4 valid tracking numbers
            if len(trks) == 4 and "TRK9999" not in trks:
                state["filtered_invalid"] = True
            
            # Should be sorted alphabetically
            if trks == sorted(trks) and len(trks) > 0:
                state["sorted_correctly"] = True
                
            # Check if required keys exist in the first delivery
            if len(deliveries) > 0:
                keys = set(deliveries[0].keys())
                if {"tracking_number", "zip_code", "weight", "revenue"}.issubset(keys):
                    state["keys_correct"] = True

        except Exception:
            pass

    with open(os.path.join(base_dir, "verify_result.json"), "w") as f:
        json.dump(state, f, indent=2)

if __name__ == "__main__":
    verify()
